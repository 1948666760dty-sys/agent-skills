from __future__ import annotations

import base64
import concurrent.futures
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ImageContent, TextContent, ToolAnnotations

from .pipeline import (
    VideoRuntimeError,
    frame_paths_for_window,
    prepare_video,
    public_manifest,
    transcript_window,
)

mcp = MCPServer(
    "video-understanding",
    instructions=(
        "Read-only video preparation and evidence retrieval for Bilibili and YouTube. "
        "A host should start analysis, wait internally until complete, read transcript, "
        "inspect overview frames, then inspect important windows more densely."
    ),
)

READ_FETCH = ToolAnnotations(read_only_hint=True, open_world_hint=True)

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="video-analysis")
_jobs_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}


def _run_job(job_id: str, url: str, mode: str, include_audience: bool, force: bool) -> None:
    try:
        result = prepare_video(
            url,
            mode=mode,  # type: ignore[arg-type]
            include_audience=include_audience,
            force=force,
        )
        with _jobs_lock:
            job = _jobs[job_id]
            job["status"] = "complete"
            job["result"] = result
            job["completed_at"] = time.time()
    except Exception as exc:
        if isinstance(exc, VideoRuntimeError):
            code = exc.code
            message = str(exc)
        else:
            code = "INTERNAL_ERROR"
            message = str(exc)
        with _jobs_lock:
            job = _jobs[job_id]
            job["status"] = "failed"
            job["error"] = {"code": code, "message": message}
            job["completed_at"] = time.time()


@mcp.tool(
    title="Start video analysis",
    description=(
        "Start preparing a Bilibili or YouTube video for deep understanding. "
        "This only reads public video data and creates an internal local cache. "
        "The host should keep the job_id private and call wait_video_analysis until complete."
    ),
    annotations=READ_FETCH,
)
def start_video_analysis(
    url: str,
    mode: Literal["deep", "quick"] = "deep",
    include_audience: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    job_id = uuid.uuid4().hex
    job = {
        "job_id": job_id,
        "status": "running",
        "url": url,
        "mode": mode,
        "started_at": time.time(),
    }
    with _jobs_lock:
        _jobs[job_id] = job
    _executor.submit(_run_job, job_id, url, mode, include_audience, force)
    return {
        "job_id": job_id,
        "status": "running",
        "instruction": "Call wait_video_analysis with this job_id. Do not ask the user to do this.",
    }


@mcp.tool(
    title="Wait for video analysis",
    description=(
        "Wait briefly for a previously started video analysis job. "
        "If still running, call this tool again; do not expose the job_id or polling to the user."
    ),
    annotations=READ_FETCH,
)
def wait_video_analysis(job_id: str, wait_seconds: int = 25) -> dict[str, Any]:
    wait_seconds = max(0, min(int(wait_seconds), 30))
    deadline = time.monotonic() + wait_seconds
    while True:
        with _jobs_lock:
            job = dict(_jobs.get(job_id) or {})
        if not job:
            return {
                "job_id": job_id,
                "status": "failed",
                "error": {"code": "VIDEO_NOT_FOUND", "message": "Unknown job_id."},
            }
        if job.get("status") != "running" or time.monotonic() >= deadline:
            if job.get("status") == "complete":
                return {
                    "job_id": job_id,
                    "status": "complete",
                    "result": job.get("result"),
                }
            if job.get("status") == "failed":
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "error": job.get("error"),
                }
            return {
                "job_id": job_id,
                "status": "running",
                "elapsed_seconds": round(time.time() - float(job.get("started_at") or time.time()), 1),
                "instruction": "Call wait_video_analysis again. Do not ask the user to poll.",
            }
        time.sleep(0.5)


@mcp.tool(
    title="Get video manifest",
    description=(
        "Return the normalized metadata and acquisition status for a prepared video session. "
        "Use this to learn duration, transcript source, visual readiness, frame count and warnings."
    ),
    annotations=READ_FETCH,
)
def get_video_manifest(session_id: str) -> dict[str, Any]:
    try:
        return public_manifest(session_id)
    except VideoRuntimeError as exc:
        return {"status": "failed", "error": {"code": exc.code, "message": str(exc)}}


@mcp.tool(
    title="Get transcript window",
    description=(
        "Return timestamped transcript segments for a prepared video. "
        "Use start_seconds/end_seconds to page through long videos instead of requesting everything at once."
    ),
    annotations=READ_FETCH,
)
def get_video_transcript(
    session_id: str,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    max_chars: int = 24000,
) -> dict[str, Any]:
    try:
        return transcript_window(
            session_id,
            start_seconds=max(0.0, float(start_seconds)),
            end_seconds=end_seconds,
            max_chars=max(2000, min(int(max_chars), 40000)),
        )
    except VideoRuntimeError as exc:
        return {"status": "failed", "error": {"code": exc.code, "message": str(exc)}}


@mcp.tool(
    title="Inspect video frames",
    description=(
        "Return timestamp labels and actual JPEG image content from a prepared video. "
        "Use density='overview' for first-pass coverage and density='dense' for agentic rewatch of an important interval. "
        "The images are intended for the host model to inspect visually, including on-screen text/OCR."
    ),
    annotations=READ_FETCH,
    structured_output=False,
)
def inspect_video_window(
    session_id: str,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    max_frames: int = 12,
    density: Literal["overview", "dense"] = "overview",
) -> list[TextContent | ImageContent]:
    try:
        frames = frame_paths_for_window(
            session_id=session_id,
            start_seconds=max(0.0, float(start_seconds)),
            end_seconds=end_seconds,
            max_frames=max_frames,
            density=density,
        )
    except VideoRuntimeError as exc:
        return [
            TextContent(
                type="text",
                text=f"ERROR {exc.code}: {exc}",
            )
        ]

    blocks: list[TextContent | ImageContent] = [
        TextContent(
            type="text",
            text=(
                f"Video frame batch: session={session_id}, density={density}, "
                f"range={start_seconds}-{end_seconds if end_seconds is not None else 'end'}, "
                f"frames={len(frames)}. Each timestamp label immediately precedes its image."
            ),
        )
    ]
    for index, item in enumerate(frames, start=1):
        path = Path(item["absolute_path"])
        if not path.is_file():
            continue
        blocks.append(
            TextContent(
                type="text",
                text=(
                    f"Frame {index}/{len(frames)} @ {float(item['timestamp_seconds']):.3f}s "
                    f"reason={item.get('reason')}"
                ),
            )
        )
        blocks.append(
            ImageContent(
                type="image",
                data=base64.b64encode(path.read_bytes()).decode("ascii"),
                mime_type="image/jpeg",
            )
        )
    return blocks


def main() -> None:
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8765,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=False,
    )


if __name__ == "__main__":
    main()
