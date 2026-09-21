from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

_ERROR_MARKERS = (
    "invalid nal unit",
    "decoding error",
    "invalid data found",
    "error splitting",
    "corrupt",
    "error while decoding",
)
_OUT_US_RE = re.compile(r"out_time_us=([0-9]+)")


def _tool(name: str) -> str:
    value = shutil.which(name)
    if not value:
        raise RuntimeError(f"Required media tool is missing: {name}")
    return value


def _run(args: list[str], timeout: int = 3600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def file_fingerprint(path: Path) -> str:
    stat = path.stat()
    digest = hashlib.sha256()
    digest.update(str(stat.st_size).encode("ascii"))
    digest.update(path.name.encode("utf-8", errors="ignore"))
    with path.open("rb") as handle:
        digest.update(handle.read(1024 * 1024))
        if stat.st_size > 1024 * 1024:
            handle.seek(max(0, stat.st_size - 1024 * 1024))
            digest.update(handle.read(1024 * 1024))
    return digest.hexdigest()[:24]


def probe_media(path: Path) -> dict[str, Any]:
    result = _run([
        _tool("ffprobe"),
        "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        str(path),
    ], timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout or "{}")
    streams = payload.get("streams") or []
    fmt = payload.get("format") or {}
    duration = float(fmt.get("duration") or 0.0)
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    return {
        "duration_seconds": round(duration, 6),
        "file_size_bytes": int(fmt.get("size") or path.stat().st_size),
        "video_present": video is not None,
        "audio_present": audio is not None,
        "video_codec": video.get("codec_name") if video else None,
        "audio_codec": audio.get("codec_name") if audio else None,
        "width": int(video.get("width") or 0) if video else None,
        "height": int(video.get("height") or 0) if video else None,
        "sample_rate": int(audio.get("sample_rate") or 0) if audio else None,
        "channels": int(audio.get("channels") or 0) if audio else None,
    }


def decode_audio_health(path: Path, audio_present: bool) -> dict[str, Any]:
    if not audio_present:
        return {
            "audio_present": False,
            "audio_decodable": None,
            "decode_errors": [],
        }
    result = _run([
        _tool("ffmpeg"), "-hide_banner", "-v", "error",
        "-i", str(path), "-map", "0:a:0", "-f", "null", "-",
    ])
    errors = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    bad = any(marker in result.stderr.lower() for marker in _ERROR_MARKERS)
    return {
        "audio_present": True,
        "audio_decodable": result.returncode == 0 and not bad and not errors,
        "decode_errors": errors[-20:],
    }


def decode_video_health(
    path: Path,
    duration_seconds: float,
    video_present: bool,
) -> dict[str, Any]:
    if not video_present:
        return {
            "video_present": False,
            "video_decodable": None,
            "decoded_until_seconds": 0.0,
            "visual_coverage_ratio": 0.0,
            "decode_errors": [],
        }
    result = _run([
        _tool("ffmpeg"), "-hide_banner", "-v", "error",
        "-progress", "pipe:1", "-nostats",
        "-i", str(path), "-map", "0:v:0", "-f", "null", "-",
    ])
    out_us = [int(m.group(1)) for m in _OUT_US_RE.finditer(result.stdout)]
    last = (max(out_us) / 1_000_000.0) if out_us else 0.0
    lower = result.stderr.lower()
    errors = [
        line.strip() for line in result.stderr.splitlines()
        if any(marker in line.lower() for marker in _ERROR_MARKERS)
    ]
    has_decode_error = any(marker in lower for marker in _ERROR_MARKERS)
    if duration_seconds > 0:
        coverage = min(1.0, max(0.0, last / duration_seconds))
        if not has_decode_error and coverage >= 0.97:
            coverage = 1.0
            last = duration_seconds
    else:
        coverage = 1.0 if out_us and not has_decode_error else 0.0
    return {
        "video_present": True,
        "video_decodable": bool(out_us) and not has_decode_error and coverage >= 0.98,
        "decoded_until_seconds": round(last, 6),
        "visual_coverage_ratio": round(coverage, 6),
        "decode_errors": errors[-20:],
    }


def transcript_coverage(
    transcript: list[dict[str, Any]],
    duration_seconds: float,
) -> float:
    if not transcript or duration_seconds <= 0:
        return 0.0
    start = min(float(x.get("start", 0.0)) for x in transcript)
    end = max(float(x.get("end", 0.0)) for x in transcript)
    return round(
        min(1.0, max(0.0, (end - start) / duration_seconds)),
        6,
    )


def completion_guard(
    *,
    mode: str,
    duration_seconds: float,
    video_present: bool,
    visual_coverage_ratio: float,
    audio_present: bool,
    audio_decodable: bool | None,
    transcript_source: str,
    transcript: list[dict[str, Any]],
) -> dict[str, Any]:
    t_cov = transcript_coverage(transcript, duration_seconds)
    speech_transcribed = transcript_source == "asr" and bool(transcript)
    transcript_available = (
        transcript_source not in {"none", "unavailable", ""}
        and bool(transcript)
    )
    transcript_complete = (
        not audio_present
        or (transcript_available and t_cov >= 0.90)
    )
    visual_required = mode == "deep" and video_present
    visual_complete = (
        not visual_required
        or visual_coverage_ratio >= 0.98
    )

    reasons: list[str] = []
    if visual_required and not visual_complete:
        reasons.append(
            f"visual coverage {visual_coverage_ratio:.1%} < 98%"
        )
    if audio_present and not audio_decodable:
        reasons.append(
            "audio is present but not fully decodable"
        )
    if audio_present and not transcript_complete:
        reasons.append(
            "audio/speech content is not sufficiently transcribed or captioned"
        )

    has_evidence = (
        visual_coverage_ratio > 0.0
        or transcript_available
    )
    if (
        visual_complete
        and transcript_complete
        and (not audio_present or audio_decodable is not False)
    ):
        status = "COMPLETE"
    elif has_evidence:
        status = "PARTIAL"
    else:
        status = "FAILED"

    return {
        "status": status,
        "visual_coverage_ratio": round(
            visual_coverage_ratio,
            6,
        ),
        "transcript_coverage_ratio": t_cov,
        "audio_present": audio_present,
        "audio_decodable": audio_decodable,
        "speech_transcribed": speech_transcribed,
        "transcript_source": transcript_source,
        "reasons": reasons,
    }


def inspect_media(
    path: Path,
    *,
    transcript_source: str = "none",
    transcript: list[dict[str, Any]] | None = None,
    mode: str = "deep",
) -> dict[str, Any]:
    probe = probe_media(path)
    audio = decode_audio_health(
        path,
        bool(probe["audio_present"]),
    )
    video = decode_video_health(
        path,
        float(probe["duration_seconds"]),
        bool(probe["video_present"]),
    )
    transcript = transcript or []
    completion = completion_guard(
        mode=mode,
        duration_seconds=float(probe["duration_seconds"]),
        video_present=bool(probe["video_present"]),
        visual_coverage_ratio=float(
            video["visual_coverage_ratio"]
        ),
        audio_present=bool(probe["audio_present"]),
        audio_decodable=audio["audio_decodable"],
        transcript_source=transcript_source,
        transcript=transcript,
    )
    return {
        "fingerprint": file_fingerprint(path),
        "probe": probe,
        "audio": audio,
        "video": video,
        "completion": completion,
    }


def attempt_repair(
    path: Path,
    out_dir: Path,
    *,
    original_health: dict[str, Any],
) -> dict[str, Any]:
    duration = float(
        original_health.get("probe", {})
        .get("duration_seconds")
        or 0.0
    )
    original_cov = float(
        original_health.get("video", {})
        .get("visual_coverage_ratio")
        or 0.0
    )
    if original_cov >= 0.98:
        return {
            "attempted": False,
            "adopted": False,
            "reason": "visual coverage already complete",
            "attempts": [],
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    attempts: list[dict[str, Any]] = []
    candidates: list[tuple[str, Path, list[str]]] = []

    remux = out_dir / "repair_remux.mp4"
    candidates.append((
        "remux",
        remux,
        [
            _tool("ffmpeg"), "-y", "-hide_banner",
            "-v", "error", "-fflags", "+discardcorrupt",
            "-err_detect", "ignore_err", "-i", str(path),
            "-map", "0:v:0", "-map", "0:a?",
            "-c", "copy", str(remux),
        ],
    ))

    max_transcode = float(
        os.environ.get(
            "VIDEO_REPAIR_TRANSCODE_MAX_SECONDS",
            "900",
        )
    )
    if duration <= max_transcode:
        transcode = out_dir / "repair_h264.mp4"
        candidates.append((
            "h264_transcode",
            transcode,
            [
                _tool("ffmpeg"), "-y", "-hide_banner",
                "-v", "error", "-fflags", "+discardcorrupt",
                "-err_detect", "ignore_err", "-i", str(path),
                "-map", "0:v:0", "-map", "0:a?",
                "-c:v", "libx264", "-preset", "ultrafast",
                "-crf", "23", "-vf", "scale=-2:1280",
                "-c:a", "aac", "-b:a", "160k",
                str(transcode),
            ],
        ))

    best_path: Path | None = None
    best_health: dict[str, Any] | None = None
    best_cov = original_cov

    for kind, candidate, cmd in candidates:
        result = _run(cmd)
        record: dict[str, Any] = {
            "kind": kind,
            "command_succeeded": (
                result.returncode == 0
                and candidate.is_file()
            ),
            "stderr_tail": [
                x
                for x in result.stderr.splitlines()
                if x.strip()
            ][-20:],
        }
        if candidate.is_file():
            try:
                health = inspect_media(
                    candidate,
                    transcript_source="none",
                    transcript=[],
                    mode="deep",
                )
                decoded_until = float(
                    health["video"]
                    ["decoded_until_seconds"]
                    or 0.0
                )
                preserved_cov = (
                    min(1.0, decoded_until / duration)
                    if duration > 0
                    else float(
                        health["video"]
                        ["visual_coverage_ratio"]
                    )
                )
                record["candidate_duration_seconds"] = (
                    health["probe"]["duration_seconds"]
                )
                record["decoded_until_seconds"] = (
                    decoded_until
                )
                record[
                    "preserved_original_timeline_ratio"
                ] = round(preserved_cov, 6)

                if preserved_cov > best_cov + 0.01:
                    best_cov = preserved_cov
                    best_path = candidate
                    best_health = health
            except Exception as exc:
                record["inspection_error"] = str(exc)
        attempts.append(record)

    return {
        "attempted": True,
        "adopted": best_path is not None,
        "original_visual_coverage_ratio": original_cov,
        "best_visual_coverage_ratio": best_cov,
        "repaired_path": (
            str(best_path)
            if best_path
            else None
        ),
        "repaired_health": best_health,
        "attempts": attempts,
        "reason": (
            "adopted only when decoded visual coverage improved "
            "by >1 percentage point"
            if best_path
            else "repair attempts did not materially improve "
            "visual coverage"
        ),
    }
