from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Literal

import cv2
import yt_dlp

SCHEMA_VERSION = "0.1"
DEFAULT_CACHE = Path(os.environ.get("VIDEO_UNDERSTANDING_CACHE", Path.home() / ".video-understanding"))
DEFAULT_CACHE.mkdir(parents=True, exist_ok=True)


class VideoRuntimeError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def detect_platform(value: str) -> Literal["bilibili", "youtube"]:
    text = value.strip()
    lower = text.lower()
    if (
        "bilibili.com/" in lower
        or "b23.tv/" in lower
        or lower.startswith("bv")
        or lower.startswith("av")
        or lower.startswith("ep")
        or lower.startswith("ss")
    ):
        return "bilibili"
    if "youtube.com/" in lower or "youtu.be/" in lower:
        return "youtube"
    raise VideoRuntimeError("UNSUPPORTED_URL", "Only Bilibili and YouTube are supported in v0.1.")


def _session_id(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()[:20]


def _session_dir(session_id: str) -> Path:
    path = DEFAULT_CACHE / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _manifest_path(session_id: str) -> Path:
    return _session_dir(session_id) / "manifest.json"


def load_manifest(session_id: str) -> dict[str, Any]:
    path = _manifest_path(session_id)
    if not path.is_file():
        raise VideoRuntimeError("VIDEO_NOT_FOUND", f"Unknown session_id: {session_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _save_manifest(session_id: str, manifest: dict[str, Any]) -> None:
    _manifest_path(session_id).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _run_bilibili_native(value: str, session_dir: Path, include_audience: bool) -> dict[str, Any]:
    from .vendor.bililens import bilibili_extract as native

    args = argparse.Namespace(
        video=value,
        page=None,
        subtitle_language=None,
        include_danmaku=include_audience,
        danmaku_limit=300,
        use_env_cookie=False,
        retries=3,
    )
    try:
        return asyncio.run(native.extract(args))
    except native.ParserError as exc:
        raise VideoRuntimeError("VIDEO_NOT_FOUND", f"Bilibili extraction failed at {exc.stage}: {exc}") from exc


def _choose_vtt(files: list[Path]) -> Path | None:
    if not files:
        return None

    def score(path: Path) -> tuple[int, str]:
        name = path.name.lower()
        if any(tag in name for tag in (".zh-hans.", ".zh-cn.", ".zh.")):
            return (0, name)
        if any(tag in name for tag in (".en-us.", ".en.")):
            return (1, name)
        return (2, name)

    return sorted(files, key=score)[0]


def _parse_vtt(path: Path) -> list[dict[str, Any]]:
    import webvtt

    segments: list[dict[str, Any]] = []
    previous = ""
    for caption in webvtt.read(str(path)):
        text = " ".join(line.strip() for line in caption.text.splitlines() if line.strip())
        if not text or text == previous:
            continue
        previous = text
        segments.append(
            {
                "start": round(caption.start_in_seconds, 3),
                "end": round(caption.end_in_seconds, 3),
                "text": text,
            }
        )
    return segments


def _youtube_source(value: str, session_dir: Path) -> dict[str, Any]:
    for old in session_dir.glob("source.*.vtt"):
        old.unlink(missing_ok=True)

    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["zh-Hans", "zh-CN", "zh", "en-US", "en"],
        "subtitlesformat": "vtt",
        "outtmpl": str(session_dir / "source.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(value, download=True)
    except Exception as exc:
        raise VideoRuntimeError("VIDEO_NOT_FOUND", f"YouTube extraction failed: {exc}") from exc

    vtt = _choose_vtt(list(session_dir.glob("source.*.vtt")))
    segments = _parse_vtt(vtt) if vtt else []
    requested = info.get("requested_subtitles") or {}
    source = "none"
    if segments:
        manual_tracks = info.get("subtitles") or {}
        automatic_tracks = info.get("automatic_captions") or {}
        selected_langs = set(requested)
        # The same language can exist in both manual and automatic catalogs.
        # Prefer the manual catalog when yt-dlp selected that language so we do
        # not downgrade a human subtitle merely because an auto track also exists.
        if any(lang in manual_tracks for lang in selected_langs):
            source = "human"
        elif any(lang in automatic_tracks for lang in selected_langs):
            source = "platform_auto"
        else:
            source = "platform_auto"

    return {
        "platform": "youtube",
        "canonical_id": str(info.get("id") or ""),
        "canonical_url": info.get("webpage_url") or value,
        "title": info.get("title") or "",
        "author": info.get("uploader") or info.get("channel") or "",
        "duration_seconds": float(info.get("duration") or 0),
        "transcript_source": source,
        "transcript_segments": segments,
        "audience": None,
        "warnings": [] if segments else ["No accessible subtitle text; ASR fallback is required."],
    }


def _bilibili_source(value: str, session_dir: Path, include_audience: bool) -> dict[str, Any]:
    result = _run_bilibili_native(value, session_dir, include_audience)
    metadata = result.get("metadata", {})
    content = result.get("content", {})
    source_type = content.get("source_type")
    normalized_source = {
        "official_subtitle": "human",
        "ai_subtitle": "platform_auto",
        "asr": "asr",
        "none": "none",
    }.get(source_type, "none")
    return {
        "platform": "bilibili",
        "canonical_id": str(metadata.get("bvid") or metadata.get("aid") or ""),
        "canonical_url": result.get("source", {}).get("canonical_url") or value,
        "title": metadata.get("title") or "",
        "author": (metadata.get("uploader") or {}).get("name", "") if isinstance(metadata.get("uploader"), dict) else str(metadata.get("uploader") or ""),
        "duration_seconds": float(
            next(
                (
                    item.get("duration_seconds")
                    for item in metadata.get("pages", [])
                    if item.get("page") == result.get("selection", {}).get("page")
                ),
                metadata.get("duration_seconds") or 0,
            )
            or 0
        ),
        "part": result.get("selection"),
        "transcript_source": normalized_source,
        "transcript_segments": content.get("segments") or [],
        "audience": result.get("audience_signals"),
        "warnings": result.get("diagnostics", {}).get("warnings") or [],
    }


def _download_media(url: str, session_dir: Path, kind: Literal["audio", "video"]) -> Path:
    stem = session_dir / kind
    for old in session_dir.glob(f"{kind}.*"):
        if old.name not in {"manifest.json"}:
            old.unlink(missing_ok=True)

    fmt = (
        "bestaudio/best"
        if kind == "audio"
        else "bestvideo[height<=720]/best[height<=720]/bestvideo/best"
    )
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": fmt,
        "outtmpl": str(stem) + ".%(ext)s",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            requested = info.get("requested_downloads") or []
            if requested and requested[0].get("filepath"):
                candidate = Path(requested[0]["filepath"])
                if candidate.is_file():
                    return candidate
    except Exception as exc:
        raise VideoRuntimeError("MEDIA_DOWNLOAD_FAILED", f"{kind} download failed: {exc}") from exc

    candidates = [
        p for p in session_dir.glob(f"{kind}.*")
        if p.is_file() and not p.name.endswith(".part")
    ]
    if not candidates:
        raise VideoRuntimeError("MEDIA_DOWNLOAD_FAILED", f"{kind} download completed without a usable file.")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _transcribe(media: Path) -> tuple[list[dict[str, Any]], str, list[str]]:
    from faster_whisper import WhisperModel

    model_name = os.environ.get("VIDEO_WHISPER_MODEL", "small")
    requested_device = os.environ.get("VIDEO_WHISPER_DEVICE", "auto").lower()
    attempts = (
        [("cuda", "float16"), ("cpu", "int8")]
        if requested_device == "auto"
        else [(requested_device, "float16" if requested_device == "cuda" else "int8")]
    )
    errors: list[str] = []
    for device, compute_type in attempts:
        try:
            model = WhisperModel(model_name, device=device, compute_type=compute_type)
            generated, info = model.transcribe(
                str(media),
                language=None,
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )
            segments: list[dict[str, Any]] = []
            for item in generated:
                text = item.text.strip()
                if text:
                    segments.append(
                        {
                            "start": round(float(item.start), 3),
                            "end": round(float(item.end), 3),
                            "text": text,
                        }
                    )
            return segments, str(info.language or "unknown"), errors
        except Exception as exc:
            errors.append(f"{device}/{compute_type}: {exc}")
    raise VideoRuntimeError("ASR_FAILED", "faster-whisper failed: " + " | ".join(errors))


def _resize(frame: Any, max_width: int = 960) -> Any:
    height, width = frame.shape[:2]
    if width <= max_width:
        return frame
    ratio = max_width / float(width)
    return cv2.resize(frame, (max_width, max(1, int(height * ratio))))


def _frame_at(cap: cv2.VideoCapture, seconds: float) -> Any | None:
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, seconds) * 1000.0)
    ok, frame = cap.read()
    return frame if ok else None


def _histogram(frame: Any) -> Any:
    small = cv2.resize(frame, (160, 90))
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
    cv2.normalize(hist, hist)
    return hist


def _extract_scene_index(video: Path, duration_seconds: float, out_dir: Path) -> list[dict[str, Any]]:
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise VideoRuntimeError("FRAME_EXTRACTION_FAILED", "OpenCV could not open the downloaded video.")

    duration = duration_seconds
    if duration <= 0:
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        duration = count / fps if fps > 0 else 0
    if duration <= 0:
        cap.release()
        raise VideoRuntimeError("FRAME_EXTRACTION_FAILED", "Video duration could not be determined.")

    sample_step = 3.0
    baseline_step = 12.0
    scene_threshold = 0.36
    scene_candidates: list[tuple[float, float]] = []
    previous_hist = None
    t = 0.0
    while t < duration:
        frame = _frame_at(cap, t)
        if frame is not None:
            hist = _histogram(frame)
            if previous_hist is not None:
                corr = cv2.compareHist(previous_hist, hist, cv2.HISTCMP_CORREL)
                diff = max(0.0, 1.0 - float(corr))
                if diff >= scene_threshold:
                    scene_candidates.append((t, diff))
            previous_hist = hist
        t += sample_step

    baseline = [(float(t), 0.0, "baseline") for t in range(0, int(duration) + 1, int(baseline_step))]
    scenes = [(t, score, "scene_cut") for t, score in scene_candidates]
    candidates = baseline + scenes
    candidates.sort(key=lambda x: x[0])

    deduped: list[tuple[float, float, str]] = []
    for item in candidates:
        if deduped and item[0] - deduped[-1][0] < 1.2:
            if item[1] > deduped[-1][1]:
                deduped[-1] = item
            continue
        deduped.append(item)

    if len(deduped) > 600:
        baselines = [x for x in deduped if x[2] == "baseline"]
        scenes_sorted = sorted((x for x in deduped if x[2] == "scene_cut"), key=lambda x: x[1], reverse=True)
        room = max(0, 600 - len(baselines))
        deduped = sorted(baselines + scenes_sorted[:room], key=lambda x: x[0])

    records: list[dict[str, Any]] = []
    for seconds, score, reason in deduped:
        frame = _frame_at(cap, seconds)
        if frame is None:
            continue
        frame = _resize(frame)
        name = f"{int(seconds * 1000):010d}.jpg"
        path = frames_dir / name
        cv2.imwrite(str(path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 78])
        records.append(
            {
                "timestamp_seconds": round(seconds, 3),
                "reason": reason,
                "score": round(score, 4),
                "relative_path": str(path.relative_to(out_dir)).replace("\\", "/"),
            }
        )
    cap.release()
    return records


def prepare_video(
    value: str,
    mode: Literal["deep", "quick"] = "deep",
    include_audience: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    started = time.monotonic()
    platform = detect_platform(value)
    sid = _session_id(value)
    session_dir = _session_dir(sid)

    if not force and _manifest_path(sid).is_file():
        existing = load_manifest(sid)
        if existing.get("schema_version") == SCHEMA_VERSION and (
            mode == "quick" or existing.get("acquisition", {}).get("visual")
        ):
            return _public_prepare_result(existing, cached=True)

    warnings: list[str] = []
    source = (
        _bilibili_source(value, session_dir, include_audience)
        if platform == "bilibili"
        else _youtube_source(value, session_dir)
    )
    warnings.extend(source.pop("warnings", []))

    transcript = source.pop("transcript_segments", [])
    transcript_source = source.pop("transcript_source", "none")
    asr_language = None

    if not transcript:
        audio = _download_media(source["canonical_url"], session_dir, "audio")
        transcript, asr_language, asr_warnings = _transcribe(audio)
        warnings.extend(asr_warnings)
        transcript_source = "asr"
        warnings.append("ASR may be wrong on names, numbers, jargon, accents, or overlapping speech.")

    visual = False
    video_path = None
    frame_index: list[dict[str, Any]] = []
    if mode == "deep":
        video_path = _download_media(source["canonical_url"], session_dir, "video")
        frame_index = _extract_scene_index(
            video_path,
            float(source.get("duration_seconds") or 0),
            session_dir,
        )
        visual = bool(frame_index)

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "session_id": sid,
        "mode": mode,
        "created_at_unix": int(time.time()),
        "source": source,
        "acquisition": {
            "transcript_source": transcript_source,
            "asr_language": asr_language,
            "visual": visual,
            "ocr": "host_vision",
            "second_pass": "available_on_demand" if visual else False,
            "audience": bool(source.get("audience")),
        },
        "transcript": transcript,
        "frame_index": frame_index,
        "runtime": {
            "video_relative_path": (
                str(video_path.relative_to(session_dir)).replace("\\", "/") if video_path else None
            ),
            "prepare_ms": round((time.monotonic() - started) * 1000),
        },
        "warnings": warnings,
    }
    _save_manifest(sid, manifest)
    return _public_prepare_result(manifest, cached=False)


def _public_prepare_result(manifest: dict[str, Any], cached: bool) -> dict[str, Any]:
    source = manifest["source"]
    return {
        "status": "complete",
        "cached": cached,
        "session_id": manifest["session_id"],
        "platform": source.get("platform"),
        "canonical_id": source.get("canonical_id"),
        "canonical_url": source.get("canonical_url"),
        "title": source.get("title"),
        "author": source.get("author"),
        "duration_seconds": source.get("duration_seconds"),
        "part": source.get("part"),
        "transcript_source": manifest.get("acquisition", {}).get("transcript_source"),
        "transcript_segments": len(manifest.get("transcript", [])),
        "visual_ready": bool(manifest.get("acquisition", {}).get("visual")),
        "frame_count": len(manifest.get("frame_index", [])),
        "second_pass": manifest.get("acquisition", {}).get("second_pass"),
        "warnings": manifest.get("warnings", []),
        "prepare_ms": manifest.get("runtime", {}).get("prepare_ms"),
    }


def public_manifest(session_id: str) -> dict[str, Any]:
    manifest = load_manifest(session_id)
    source = manifest["source"]
    transcript = manifest.get("transcript", [])
    return {
        "schema_version": manifest.get("schema_version"),
        "session_id": session_id,
        "mode": manifest.get("mode"),
        "source": {
            "platform": source.get("platform"),
            "canonical_id": source.get("canonical_id"),
            "canonical_url": source.get("canonical_url"),
            "title": source.get("title"),
            "author": source.get("author"),
            "duration_seconds": source.get("duration_seconds"),
            "part": source.get("part"),
        },
        "acquisition": manifest.get("acquisition"),
        "transcript_segments": len(transcript),
        "transcript_characters": sum(len(x.get("text", "")) for x in transcript),
        "frame_count": len(manifest.get("frame_index", [])),
        "warnings": manifest.get("warnings", []),
    }


def transcript_window(
    session_id: str,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    max_chars: int = 24000,
) -> dict[str, Any]:
    manifest = load_manifest(session_id)
    duration = float(manifest.get("source", {}).get("duration_seconds") or 0)
    end = duration if end_seconds is None else end_seconds
    rows = [
        row
        for row in manifest.get("transcript", [])
        if float(row.get("end", 0)) >= start_seconds and float(row.get("start", 0)) <= end
    ]
    out: list[dict[str, Any]] = []
    count = 0
    truncated = False
    for row in rows:
        text = str(row.get("text", ""))
        if count + len(text) > max_chars and out:
            truncated = True
            break
        out.append(row)
        count += len(text)
    return {
        "session_id": session_id,
        "start_seconds": start_seconds,
        "end_seconds": end,
        "source": manifest.get("acquisition", {}).get("transcript_source"),
        "segments": out,
        "truncated": truncated,
        "characters": count,
    }


def _video_path(manifest: dict[str, Any], session_id: str) -> Path:
    rel = manifest.get("runtime", {}).get("video_relative_path")
    if not rel:
        raise VideoRuntimeError("VISUAL_ANALYSIS_FAILED", "This session has no prepared video stream.")
    path = _session_dir(session_id) / rel
    if not path.is_file():
        raise VideoRuntimeError("VISUAL_ANALYSIS_FAILED", "Prepared video file is missing.")
    return path


def _evenly_pick(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(items) <= limit:
        return items
    if limit <= 1:
        return [items[len(items) // 2]]
    indices = [round(i * (len(items) - 1) / (limit - 1)) for i in range(limit)]
    return [items[i] for i in indices]


def frame_paths_for_window(
    session_id: str,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    max_frames: int = 12,
    density: Literal["overview", "dense"] = "overview",
) -> list[dict[str, Any]]:
    manifest = load_manifest(session_id)
    duration = float(manifest.get("source", {}).get("duration_seconds") or 0)
    end = duration if end_seconds is None else min(end_seconds, duration)
    if end <= start_seconds:
        raise VideoRuntimeError("FRAME_EXTRACTION_FAILED", "end_seconds must be greater than start_seconds.")
    max_frames = max(1, min(int(max_frames), 20))

    if density == "overview":
        candidates = [
            item for item in manifest.get("frame_index", [])
            if start_seconds <= float(item.get("timestamp_seconds", 0)) <= end
        ]
        picked = _evenly_pick(candidates, max_frames)
        return [
            {
                **item,
                "absolute_path": str(_session_dir(session_id) / item["relative_path"]),
            }
            for item in picked
        ]

    video = _video_path(manifest, session_id)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise VideoRuntimeError("FRAME_EXTRACTION_FAILED", "OpenCV could not reopen the prepared video.")
    window_dir = _session_dir(session_id) / "rewatch"
    window_dir.mkdir(parents=True, exist_ok=True)
    if max_frames == 1:
        times = [(start_seconds + end) / 2.0]
    else:
        times = [
            start_seconds + i * (end - start_seconds) / (max_frames - 1)
            for i in range(max_frames)
        ]
    records: list[dict[str, Any]] = []
    for seconds in times:
        frame = _frame_at(cap, seconds)
        if frame is None:
            continue
        frame = _resize(frame)
        name = f"{int(seconds * 1000):010d}.jpg"
        path = window_dir / name
        cv2.imwrite(str(path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
        records.append(
            {
                "timestamp_seconds": round(seconds, 3),
                "reason": "rewatch",
                "score": None,
                "absolute_path": str(path),
            }
        )
    cap.release()
    return records
