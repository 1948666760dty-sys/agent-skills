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
from scenedetect import AdaptiveDetector, SceneManager, open_video

from .long_video import (
    build_chapters,
    build_evidence_chunks,
    sampling_profile,
    search_evidence,
)
from .media_health import (
    attempt_repair,
    completion_guard,
    file_fingerprint,
    inspect_media,
)

SCHEMA_VERSION = "0.2.3"
DEFAULT_CACHE = Path(
    os.environ.get("VIDEO_UNDERSTANDING_CACHE", Path.home() / ".video-understanding")
)
DEFAULT_CACHE.mkdir(parents=True, exist_ok=True)
DEFAULT_UPLOAD_INBOX = DEFAULT_CACHE / "inbox"
DEFAULT_UPLOAD_INBOX.mkdir(parents=True, exist_ok=True)


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
    raise VideoRuntimeError(
        "UNSUPPORTED_URL",
        "Only Bilibili and YouTube URLs are supported by the URL adapter.",
    )


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


def _run_bilibili_native(
    value: str,
    session_dir: Path,
    include_audience: bool,
) -> dict[str, Any]:
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
        raise VideoRuntimeError(
            "VIDEO_NOT_FOUND",
            f"Bilibili extraction failed at {exc.stage}: {exc}",
        ) from exc


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
        text = " ".join(
            line.strip() for line in caption.text.splitlines() if line.strip()
        )
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
        raise VideoRuntimeError(
            "VIDEO_NOT_FOUND",
            f"YouTube extraction failed: {exc}",
        ) from exc

    vtt = _choose_vtt(list(session_dir.glob("source.*.vtt")))
    segments = _parse_vtt(vtt) if vtt else []
    requested = info.get("requested_subtitles") or {}
    source = "none"
    if segments:
        manual_tracks = info.get("subtitles") or {}
        automatic_tracks = info.get("automatic_captions") or {}
        selected_langs = set(requested)
        if any(lang in manual_tracks for lang in selected_langs):
            source = "human"
        elif any(lang in automatic_tracks for lang in selected_langs):
            source = "platform_auto"
        else:
            source = "platform_auto"

    return {
        "platform": "youtube",
        "input_kind": "url",
        "canonical_id": str(info.get("id") or ""),
        "canonical_url": info.get("webpage_url") or value,
        "title": info.get("title") or "",
        "author": info.get("uploader") or info.get("channel") or "",
        "duration_seconds": float(info.get("duration") or 0),
        "transcript_source": source,
        "transcript_segments": segments,
        "audience": None,
        "warnings": [] if segments else [
            "No accessible subtitle text; ASR fallback is required."
        ],
    }


def _bilibili_source(
    value: str,
    session_dir: Path,
    include_audience: bool,
) -> dict[str, Any]:
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
        "input_kind": "url",
        "canonical_id": str(metadata.get("bvid") or metadata.get("aid") or ""),
        "canonical_url": result.get("source", {}).get("canonical_url") or value,
        "title": metadata.get("title") or "",
        "author": (
            (metadata.get("uploader") or {}).get("name", "")
            if isinstance(metadata.get("uploader"), dict)
            else str(metadata.get("uploader") or "")
        ),
        "duration_seconds": float(
            next(
                (
                    item.get("duration_seconds")
                    for item in metadata.get("pages", [])
                    if item.get("page")
                    == result.get("selection", {}).get("page")
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


def _download_media(
    url: str,
    session_dir: Path,
    kind: Literal["audio", "video"],
) -> Path:
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
        raise VideoRuntimeError(
            "MEDIA_DOWNLOAD_FAILED",
            f"{kind} download failed: {exc}",
        ) from exc

    candidates = [
        p
        for p in session_dir.glob(f"{kind}.*")
        if p.is_file() and not p.name.endswith(".part")
    ]
    if not candidates:
        raise VideoRuntimeError(
            "MEDIA_DOWNLOAD_FAILED",
            f"{kind} download completed without a usable file.",
        )
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _transcribe(
    media: Path,
) -> tuple[list[dict[str, Any]], str, list[str]]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise VideoRuntimeError(
            "ASR_UNAVAILABLE",
            "faster-whisper is not installed in this runtime.",
        ) from exc

    model_name = os.environ.get("VIDEO_WHISPER_MODEL", "small")
    requested_device = os.environ.get(
        "VIDEO_WHISPER_DEVICE",
        "auto",
    ).lower()
    attempts = (
        [("cuda", "float16"), ("cpu", "int8")]
        if requested_device == "auto"
        else [
            (
                requested_device,
                "float16" if requested_device == "cuda" else "int8",
            )
        ]
    )
    errors: list[str] = []
    for device, compute_type in attempts:
        try:
            model = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type,
            )
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
    raise VideoRuntimeError(
        "ASR_FAILED",
        "faster-whisper failed: " + " | ".join(errors),
    )


def _resize(frame: Any, max_width: int = 960) -> Any:
    height, width = frame.shape[:2]
    if width <= max_width:
        return frame
    ratio = max_width / float(width)
    return cv2.resize(
        frame,
        (max_width, max(1, int(height * ratio))),
    )


def _frame_at(
    cap: cv2.VideoCapture,
    seconds: float,
) -> Any | None:
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, seconds) * 1000.0)
    ok, frame = cap.read()
    return frame if ok else None


def _probe_video(path: Path) -> dict[str, Any]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise VideoRuntimeError(
            "VIDEO_NOT_FOUND",
            f"OpenCV could not open video: {path.name}",
        )
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    duration = frame_count / fps if fps > 0 else 0.0
    return {
        "duration_seconds": round(duration, 3),
        "fps": round(fps, 3),
        "width": width,
        "height": height,
        "frame_count": int(frame_count),
        "file_size_bytes": path.stat().st_size,
    }


def _upload_roots() -> list[Path]:
    configured = os.environ.get("VIDEO_UPLOAD_ROOTS", "").strip()
    if configured:
        roots = [
            Path(part).expanduser().resolve()
            for part in configured.split(os.pathsep)
            if part.strip()
        ]
    else:
        roots = [DEFAULT_UPLOAD_INBOX.resolve()]
    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
    return roots


def _validated_upload_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise VideoRuntimeError(
            "VIDEO_NOT_FOUND",
            f"Uploaded/local video file was not found: {path.name}",
        )
    roots = _upload_roots()
    if not any(path.is_relative_to(root) for root in roots):
        raise VideoRuntimeError(
            "UPLOAD_PATH_NOT_ALLOWED",
            "Local video path is outside VIDEO_UPLOAD_ROOTS. "
            "Use the dedicated video-understanding inbox or explicitly configure an allowed root.",
        )
    return path


def _fingerprint_local_file(path: Path) -> str:
    return file_fingerprint(path)


def _scene_candidates(
    video: Path,
    duration_seconds: float,
) -> tuple[list[dict[str, float]], list[str], dict[str, Any]]:
    profile = sampling_profile(duration_seconds)
    warnings: list[str] = []
    scenes: list[dict[str, float]] = []
    try:
        stream = open_video(str(video))
        manager = SceneManager()
        manager.auto_downscale = True
        manager.add_detector(
            AdaptiveDetector(
                adaptive_threshold=3.0,
                min_scene_len=0.8,
                window_width=2,
                min_content_val=15.0,
            )
        )
        manager.detect_scenes(
            video=stream,
            frame_skip=int(profile["scene_frame_skip"]),
            show_progress=False,
        )
        for start, end in manager.get_scene_list(start_in_scene=True):
            s = float(start.get_seconds())
            e = float(end.get_seconds())
            if e <= s:
                continue
            scenes.append(
                {
                    "start_seconds": round(s, 3),
                    "end_seconds": round(e, 3),
                    "representative_seconds": round((s + e) / 2.0, 3),
                    "duration_seconds": round(e - s, 3),
                }
            )
    except Exception as exc:
        warnings.append(
            "PySceneDetect adaptive detection failed; "
            f"falling back to baseline coverage only: {exc}"
        )
    return scenes, warnings, profile


def _extract_scene_index(
    video: Path,
    duration_seconds: float,
    out_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    list[str],
]:
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise VideoRuntimeError(
            "FRAME_EXTRACTION_FAILED",
            "OpenCV could not open the video.",
        )

    probe = _probe_video(video)
    duration = duration_seconds or float(probe["duration_seconds"])
    if duration <= 0:
        cap.release()
        raise VideoRuntimeError(
            "FRAME_EXTRACTION_FAILED",
            "Video duration could not be determined.",
        )

    scenes, warnings, profile = _scene_candidates(video, duration)
    baseline_step = float(profile["baseline_step_seconds"])
    max_frames = int(profile["max_overview_frames"])

    candidates: list[tuple[float, str, float]] = []
    baseline_count = max(1, int(duration // baseline_step) + 1)
    for index in range(baseline_count):
        candidates.append(
            (
                min(duration, index * baseline_step),
                "baseline",
                0.0,
            )
        )

    scene_reps = [
        (
            float(scene["representative_seconds"]),
            "scene",
            float(scene["duration_seconds"]),
        )
        for scene in scenes
    ]

    if len(scene_reps) > max_frames:
        step = len(scene_reps) / float(max_frames)
        scene_reps = [
            scene_reps[min(len(scene_reps) - 1, int(i * step))]
            for i in range(max_frames)
        ]

    candidates.extend(scene_reps)
    candidates.sort(key=lambda item: item[0])

    deduped: list[tuple[float, str, float]] = []
    for item in candidates:
        if deduped and item[0] - deduped[-1][0] < 1.0:
            if item[1] == "scene" and deduped[-1][1] != "scene":
                deduped[-1] = item
            continue
        deduped.append(item)

    if len(deduped) > max_frames:
        scene_items = [item for item in deduped if item[1] == "scene"]
        baseline_items = [item for item in deduped if item[1] == "baseline"]
        scene_budget = min(len(scene_items), max_frames // 2)
        baseline_budget = max_frames - scene_budget

        def evenly_pick(
            items: list[tuple[float, str, float]],
            limit: int,
        ) -> list[tuple[float, str, float]]:
            if limit <= 0:
                return []
            if len(items) <= limit:
                return items
            if limit == 1:
                return [items[len(items) // 2]]
            indices = [
                round(i * (len(items) - 1) / (limit - 1))
                for i in range(limit)
            ]
            return [items[i] for i in indices]

        deduped = sorted(
            evenly_pick(scene_items, scene_budget)
            + evenly_pick(baseline_items, baseline_budget),
            key=lambda item: item[0],
        )

    records: list[dict[str, Any]] = []
    for seconds, reason, score in deduped:
        frame = _frame_at(cap, seconds)
        if frame is None:
            continue
        frame = _resize(frame)
        name = f"{int(seconds * 1000):010d}.jpg"
        path = frames_dir / name
        cv2.imwrite(
            str(path),
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 78],
        )
        records.append(
            {
                "timestamp_seconds": round(seconds, 3),
                "reason": reason,
                "score": round(score, 4),
                "relative_path": str(path.relative_to(out_dir)).replace(
                    "\\",
                    "/",
                ),
            }
        )
    cap.release()
    return records, scenes, profile, warnings


def _build_manifest(
    *,
    sid: str,
    mode: Literal["deep", "quick"],
    source: dict[str, Any],
    transcript: list[dict[str, Any]],
    transcript_source: str,
    asr_language: str | None,
    video_path: Path | None,
    session_dir: Path,
    started: float,
    warnings: list[str],
    uploaded_absolute_path: Path | None = None,
    media_health: dict[str, Any] | None = None,
    source_fingerprint: str | None = None,
    repair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    duration = float(source.get("duration_seconds") or 0)
    frame_index: list[dict[str, Any]] = []
    scene_index: list[dict[str, Any]] = []
    profile = sampling_profile(duration)
    visual = False

    if media_health is None and video_path is not None:
        try:
            media_health = inspect_media(
                video_path,
                transcript_source=transcript_source,
                transcript=transcript,
                mode=mode,
            )
        except Exception as exc:
            warnings.append(
                f"Media health inspection failed: {exc}"
            )

    if mode == "deep" and video_path is not None:
        try:
            frame_index, scene_index, profile, scene_warnings = _extract_scene_index(
                video_path,
                duration,
                session_dir,
            )
            warnings.extend(scene_warnings)
            visual = bool(frame_index)
        except Exception as exc:
            warnings.append(
                f"Visual index extraction failed; preserving other evidence: {exc}"
            )

    chapters = build_chapters(transcript, duration)
    evidence_chunks = build_evidence_chunks(transcript, duration)

    if media_health is not None:
        probe = media_health.get("probe", {})
        audio_state = media_health.get("audio", {})
        video_state = media_health.get("video", {})
        completion = completion_guard(
            mode=mode,
            duration_seconds=float(
                probe.get("duration_seconds")
                or duration
                or 0.0
            ),
            video_present=bool(
                probe.get("video_present", video_path is not None)
            ),
            visual_coverage_ratio=float(
                video_state.get("visual_coverage_ratio")
                or 0.0
            ),
            audio_present=bool(
                probe.get("audio_present", False)
            ),
            audio_decodable=audio_state.get(
                "audio_decodable"
            ),
            transcript_source=transcript_source,
            transcript=transcript,
        )
        media_health["completion"] = completion
    else:
        completion = {
            "status": (
                "PARTIAL"
                if transcript or frame_index
                else "FAILED"
            ),
            "visual_coverage_ratio": None,
            "transcript_coverage_ratio": None,
            "audio_present": None,
            "audio_decodable": None,
            "speech_transcribed": (
                transcript_source == "asr"
                and bool(transcript)
            ),
            "transcript_source": transcript_source,
            "reasons": [
                "media health coverage was unavailable"
            ],
        }

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "session_id": sid,
        "identity": {
            "session_id": sid,
            "source_fingerprint": (
                source_fingerprint or sid
            ),
        },
        "mode": mode,
        "created_at_unix": int(time.time()),
        "source": source,
        "acquisition": {
            "transcript_source": transcript_source,
            "asr_language": asr_language,
            "visual": visual,
            "ocr": "host_vision",
            "second_pass": (
                "available_on_demand"
                if visual
                else False
            ),
            "audience": bool(source.get("audience")),
            "audio_present": completion.get(
                "audio_present"
            ),
            "audio_decodable": completion.get(
                "audio_decodable"
            ),
            "speech_transcribed": completion.get(
                "speech_transcribed"
            ),
        },
        "completion": completion,
        "media_health": media_health,
        "repair": repair,
        "long_video": {
            "profile": profile,
            "chapter_count": len(chapters),
            "evidence_chunk_count": len(
                evidence_chunks
            ),
            "strategy": (
                "chaptered_retrieval_and_agentic_rewatch"
                if profile["tier"]
                in {
                    "long",
                    "very_long",
                    "ultra_long",
                }
                else "global_overview_and_agentic_rewatch"
            ),
        },
        "transcript": transcript,
        "chapters": chapters,
        "evidence_chunks": evidence_chunks,
        "scene_index": scene_index,
        "frame_index": frame_index,
        "runtime": {
            "video_relative_path": (
                str(
                    video_path.relative_to(
                        session_dir
                    )
                ).replace("\\", "/")
                if video_path is not None
                and uploaded_absolute_path is None
                and video_path.is_relative_to(
                    session_dir
                )
                else None
            ),
            "video_absolute_path": (
                str(uploaded_absolute_path)
                if uploaded_absolute_path
                is not None
                else None
            ),
            "prepare_ms": round(
                (time.monotonic() - started)
                * 1000
            ),
        },
        "warnings": warnings,
    }
    _save_manifest(sid, manifest)
    return manifest


def prepare_video(
    value: str,
    mode: Literal["deep", "quick"] = "deep",
    include_audience: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Prepare a Bilibili/YouTube URL."""
    started = time.monotonic()
    platform = detect_platform(value)
    sid = _session_id("url:" + value)
    session_dir = _session_dir(sid)

    if not force and _manifest_path(sid).is_file():
        existing = load_manifest(sid)
        if existing.get("schema_version") == SCHEMA_VERSION:
            return _public_prepare_result(
                existing,
                cached=True,
            )

    warnings: list[str] = []
    source = (
        _bilibili_source(
            value,
            session_dir,
            include_audience,
        )
        if platform == "bilibili"
        else _youtube_source(
            value,
            session_dir,
        )
    )
    warnings.extend(
        source.pop("warnings", [])
    )

    transcript = source.pop(
        "transcript_segments",
        [],
    )
    transcript_source = source.pop(
        "transcript_source",
        "none",
    )
    asr_language = None

    if not transcript:
        try:
            audio = _download_media(
                source["canonical_url"],
                session_dir,
                "audio",
            )
            (
                transcript,
                asr_language,
                asr_warnings,
            ) = _transcribe(audio)
            warnings.extend(asr_warnings)
            transcript_source = "asr"
            warnings.append(
                "ASR may be wrong on names, numbers, jargon, "
                "accents, or overlapping speech."
            )
        except Exception as exc:
            transcript = []
            transcript_source = "none"
            warnings.append(
                f"ASR unavailable/failed; continuing with visual evidence: {exc}"
            )

    video_path = None
    if mode == "deep":
        try:
            video_path = _download_media(
                source["canonical_url"],
                session_dir,
                "video",
            )
        except Exception as exc:
            warnings.append(
                f"Video acquisition failed; preserving transcript evidence: {exc}"
            )

    manifest = _build_manifest(
        sid=sid,
        mode=mode,
        source=source,
        transcript=transcript,
        transcript_source=transcript_source,
        asr_language=asr_language,
        video_path=video_path,
        session_dir=session_dir,
        started=started,
        warnings=warnings,
        source_fingerprint=_session_id(
            "canonical:"
            + str(
                source.get("canonical_id")
                or source.get("canonical_url")
                or value
            )
        ),
    )
    return _public_prepare_result(
        manifest,
        cached=False,
    )


def prepare_uploaded_video(
    file_path: str,
    mode: Literal["deep", "quick"] = "deep",
    force: bool = False,
) -> dict[str, Any]:
    """Prepare a host-materialized/uploaded local video from a restricted inbox."""
    started = time.monotonic()
    path = _validated_upload_path(file_path)
    fingerprint = _fingerprint_local_file(
        path
    )
    sid = _session_id(
        "upload:" + fingerprint
    )
    session_dir = _session_dir(sid)

    if not force and _manifest_path(sid).is_file():
        existing = load_manifest(sid)
        if existing.get(
            "schema_version"
        ) == SCHEMA_VERSION:
            return _public_prepare_result(
                existing,
                cached=True,
            )

    warnings: list[str] = []
    original_health: dict[str, Any] | None = None
    repair: dict[str, Any] | None = None
    analysis_path = path

    try:
        original_health = inspect_media(
            path,
            transcript_source="none",
            transcript=[],
            mode=mode,
        )
        probe = original_health["probe"]
    except Exception as exc:
        probe = _probe_video(path)
        warnings.append(
            f"Full media health inspection failed: {exc}"
        )

    if (
        mode == "deep"
        and original_health is not None
        and float(
            original_health.get(
                "video",
                {},
            ).get(
                "visual_coverage_ratio",
                0.0,
            )
        ) < 0.98
    ):
        try:
            repair = attempt_repair(
                path,
                session_dir / "repair",
                original_health=original_health,
            )
            if repair.get("adopted"):
                analysis_path = Path(
                    str(
                        repair[
                            "repaired_path"
                        ]
                    )
                )
                improved = float(
                    repair.get(
                        "best_visual_coverage_ratio",
                        0.0,
                    )
                )
                video_state = dict(
                    original_health.get(
                        "video",
                        {},
                    )
                )
                video_state[
                    "visual_coverage_ratio"
                ] = improved
                video_state[
                    "decoded_until_seconds"
                ] = round(
                    improved
                    * float(
                        probe.get(
                            "duration_seconds"
                        )
                        or 0.0
                    ),
                    6,
                )
                video_state[
                    "video_decodable"
                ] = improved >= 0.98
                original_health[
                    "video"
                ] = video_state
            else:
                warnings.append(
                    "Repair attempts did not materially improve the original visual timeline."
                )
        except Exception as exc:
            warnings.append(
                f"Repair attempt failed; preserving partial original evidence: {exc}"
            )

    source = {
        "platform": "upload",
        "input_kind": "uploaded_file",
        "canonical_id": fingerprint,
        "canonical_url": None,
        "title": path.name,
        "author": None,
        "duration_seconds": float(
            probe.get(
                "duration_seconds",
                0.0,
            )
        ),
        "part": None,
        "file": probe,
    }

    transcript: list[dict[str, Any]] = []
    asr_language = None
    transcript_source = "none"
    try:
        (
            transcript,
            asr_language,
            asr_warnings,
        ) = _transcribe(path)
        warnings.extend(asr_warnings)
        transcript_source = "asr"
        warnings.append(
            "Uploaded-file ASR may contain errors in names, "
            "numbers, jargon, accents, or overlapping speech."
        )
    except Exception as exc:
        warnings.append(
            f"Audio is not the same as transcription: ASR unavailable/failed, "
            f"while media health is preserved separately. Detail: {exc}"
        )

    warnings.append(
        "The cached session references the allowed local upload path; "
        "if the host deletes that file, later visual rewatch may require "
        "re-upload/materialization."
    )

    use_absolute = (
        mode == "deep"
        and analysis_path == path
    )
    manifest = _build_manifest(
        sid=sid,
        mode=mode,
        source=source,
        transcript=transcript,
        transcript_source=transcript_source,
        asr_language=asr_language,
        video_path=(
            analysis_path
            if mode == "deep"
            else None
        ),
        session_dir=session_dir,
        started=started,
        warnings=warnings,
        uploaded_absolute_path=(
            path
            if use_absolute
            else None
        ),
        media_health=original_health,
        source_fingerprint=fingerprint,
        repair=repair,
    )
    return _public_prepare_result(
        manifest,
        cached=False,
    )


def _public_prepare_result(
    manifest: dict[str, Any],
    cached: bool,
) -> dict[str, Any]:
    source = manifest["source"]
    long_video = manifest.get(
        "long_video",
        {},
    )
    completion = manifest.get(
        "completion",
        {},
    )
    status = str(
        completion.get(
            "status",
            "PARTIAL",
        )
    ).lower()
    return {
        "status": status,
        "cached": cached,
        "session_id": manifest["session_id"],
        "source_fingerprint": (
            manifest.get(
                "identity",
                {},
            ).get(
                "source_fingerprint"
            )
        ),
        "completion": completion,
        "platform": source.get("platform"),
        "input_kind": source.get(
            "input_kind"
        ),
        "canonical_id": source.get(
            "canonical_id"
        ),
        "canonical_url": source.get(
            "canonical_url"
        ),
        "title": source.get("title"),
        "author": source.get("author"),
        "duration_seconds": source.get(
            "duration_seconds"
        ),
        "part": source.get("part"),
        "transcript_source": (
            manifest.get(
                "acquisition",
                {},
            ).get(
                "transcript_source"
            )
        ),
        "audio_present": completion.get(
            "audio_present"
        ),
        "audio_decodable": completion.get(
            "audio_decodable"
        ),
        "speech_transcribed": completion.get(
            "speech_transcribed"
        ),
        "transcript_segments": len(
            manifest.get(
                "transcript",
                [],
            )
        ),
        "visual_coverage_ratio": completion.get(
            "visual_coverage_ratio"
        ),
        "transcript_coverage_ratio": completion.get(
            "transcript_coverage_ratio"
        ),
        "visual_ready": bool(
            manifest.get(
                "acquisition",
                {},
            ).get(
                "visual"
            )
        ),
        "frame_count": len(
            manifest.get(
                "frame_index",
                [],
            )
        ),
        "chapter_count": long_video.get(
            "chapter_count",
            0,
        ),
        "evidence_chunk_count": (
            long_video.get(
                "evidence_chunk_count",
                0,
            )
        ),
        "long_video_tier": (
            long_video.get(
                "profile",
                {},
            ).get(
                "tier"
            )
        ),
        "second_pass": (
            manifest.get(
                "acquisition",
                {},
            ).get(
                "second_pass"
            )
        ),
        "repair": manifest.get("repair"),
        "warnings": manifest.get(
            "warnings",
            [],
        ),
        "prepare_ms": (
            manifest.get(
                "runtime",
                {},
            ).get(
                "prepare_ms"
            )
        ),
    }


def public_manifest(session_id: str) -> dict[str, Any]:
    manifest = load_manifest(session_id)
    source = manifest["source"]
    transcript = manifest.get(
        "transcript",
        [],
    )
    return {
        "schema_version": manifest.get(
            "schema_version"
        ),
        "session_id": session_id,
        "identity": manifest.get("identity"),
        "mode": manifest.get("mode"),
        "source": {
            "platform": source.get("platform"),
            "input_kind": source.get(
                "input_kind"
            ),
            "canonical_id": source.get(
                "canonical_id"
            ),
            "canonical_url": source.get(
                "canonical_url"
            ),
            "title": source.get("title"),
            "author": source.get("author"),
            "duration_seconds": source.get(
                "duration_seconds"
            ),
            "part": source.get("part"),
            "file": source.get("file"),
        },
        "acquisition": manifest.get(
            "acquisition"
        ),
        "completion": manifest.get(
            "completion"
        ),
        "media_health": manifest.get(
            "media_health"
        ),
        "repair": manifest.get("repair"),
        "long_video": manifest.get(
            "long_video"
        ),
        "transcript_segments": len(
            transcript
        ),
        "transcript_characters": sum(
            len(x.get("text", ""))
            for x in transcript
        ),
        "chapter_count": len(
            manifest.get("chapters", [])
        ),
        "evidence_chunk_count": len(
            manifest.get(
                "evidence_chunks",
                [],
            )
        ),
        "scene_count": len(
            manifest.get(
                "scene_index",
                [],
            )
        ),
        "frame_count": len(
            manifest.get(
                "frame_index",
                [],
            )
        ),
        "warnings": manifest.get(
            "warnings",
            [],
        ),
    }


def transcript_window(
    session_id: str,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    max_chars: int = 24000,
) -> dict[str, Any]:
    manifest = load_manifest(session_id)
    duration = float(
        manifest.get("source", {}).get("duration_seconds") or 0
    )
    end = duration if end_seconds is None else min(
        float(end_seconds),
        duration,
    )
    rows = [
        row
        for row in manifest.get("transcript", [])
        if float(row.get("end", 0)) >= start_seconds
        and float(row.get("start", 0)) <= end
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
        "source": manifest.get("acquisition", {}).get(
            "transcript_source"
        ),
        "segments": out,
        "truncated": truncated,
        "characters": count,
    }


def chapter_index(session_id: str) -> dict[str, Any]:
    manifest = load_manifest(session_id)
    return {
        "session_id": session_id,
        "tier": manifest.get("long_video", {})
        .get("profile", {})
        .get("tier"),
        "chapters": manifest.get("chapters", []),
    }


def search_video_memory(
    session_id: str,
    query: str,
    limit: int = 8,
) -> dict[str, Any]:
    manifest = load_manifest(session_id)
    results = search_evidence(
        manifest.get("evidence_chunks", []),
        query=query,
        limit=limit,
    )
    return {
        "session_id": session_id,
        "query": query,
        "results": results,
        "instruction": (
            "Use these windows as retrieval candidates. "
            "For important factual or visual questions, inspect the matching "
            "transcript and dense video frames before answering."
        ),
    }


def _video_path(
    manifest: dict[str, Any],
    session_id: str,
) -> Path:
    absolute = manifest.get("runtime", {}).get(
        "video_absolute_path"
    )
    if absolute:
        path = Path(absolute)
        if path.is_file():
            return path
        raise VideoRuntimeError(
            "VISUAL_ANALYSIS_FAILED",
            "The uploaded local video is no longer available. "
            "Re-upload/materialize it into the configured inbox.",
        )

    rel = manifest.get("runtime", {}).get("video_relative_path")
    if not rel:
        raise VideoRuntimeError(
            "VISUAL_ANALYSIS_FAILED",
            "This session has no prepared video stream.",
        )
    path = _session_dir(session_id) / rel
    if not path.is_file():
        raise VideoRuntimeError(
            "VISUAL_ANALYSIS_FAILED",
            "Prepared video file is missing.",
        )
    return path


def _evenly_pick(
    items: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    if len(items) <= limit:
        return items
    if limit <= 1:
        return [items[len(items) // 2]]
    indices = [
        round(i * (len(items) - 1) / (limit - 1))
        for i in range(limit)
    ]
    return [items[i] for i in indices]


def frame_paths_for_window(
    session_id: str,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    max_frames: int = 12,
    density: Literal["overview", "dense"] = "overview",
) -> list[dict[str, Any]]:
    manifest = load_manifest(session_id)
    duration = float(
        manifest.get("source", {}).get("duration_seconds") or 0
    )
    end = duration if end_seconds is None else min(
        end_seconds,
        duration,
    )
    if end <= start_seconds:
        raise VideoRuntimeError(
            "FRAME_EXTRACTION_FAILED",
            "end_seconds must be greater than start_seconds.",
        )
    max_frames = max(1, min(int(max_frames), 20))

    if density == "overview":
        candidates = [
            item
            for item in manifest.get("frame_index", [])
            if start_seconds
            <= float(item.get("timestamp_seconds", 0))
            <= end
        ]
        picked = _evenly_pick(candidates, max_frames)
        return [
            {
                **item,
                "absolute_path": str(
                    _session_dir(session_id)
                    / item["relative_path"]
                ),
            }
            for item in picked
        ]

    video = _video_path(manifest, session_id)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise VideoRuntimeError(
            "FRAME_EXTRACTION_FAILED",
            "OpenCV could not reopen the prepared video.",
        )
    window_dir = _session_dir(session_id) / "rewatch"
    window_dir.mkdir(parents=True, exist_ok=True)
    if max_frames == 1:
        times = [(start_seconds + end) / 2.0]
    else:
        times = [
            start_seconds
            + i * (end - start_seconds) / (max_frames - 1)
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
        cv2.imwrite(
            str(path),
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 82],
        )
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
