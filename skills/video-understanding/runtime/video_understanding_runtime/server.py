from __future__ import annotations

import base64
import concurrent.futures
import hashlib
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ImageContent, TextContent, ToolAnnotations

from .pipeline import (
    VideoRuntimeError,
    chapter_index,
    frame_paths_for_window,
    prepare_uploaded_video,
    prepare_video,
    public_manifest,
    search_video_memory,
    transcript_window,
)

mcp = MCPServer(
    "video-understanding",
    instructions=(
        "Read-only evidence preparation for uploaded/local videos, Bilibili, and YouTube. "
        "For long videos, use chapters and search_video_memory before loading large transcript "
        "or frame windows. Start jobs and wait internally; never ask the end user to operate job IDs."
    ),
)

READ_FETCH = ToolAnnotations(
    read_only_hint=True,
    open_world_hint=True,
)

_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="video-analysis",
)
_jobs_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}


def _finish_job(
    job_id: str,
    result: dict[str, Any] | None = None,
    error: Exception | None = None,
) -> None:
    with _jobs_lock:
        job = _jobs[job_id]
        if error is None:
            job["status"] = "complete"
            if result is not None:
                result = dict(result)
                result["task_id"] = job_id
                result["request_fingerprint"] = job.get(
                    "request_fingerprint"
                )
            job["result"] = result
        else:
            if isinstance(error, VideoRuntimeError):
                code = error.code
                message = str(error)
            else:
                code = "INTERNAL_ERROR"
                message = str(error)
            job["status"] = "failed"
            job["error"] = {
                "code": code,
                "message": message,
            }
        job["completed_at"] = time.time()


def _run_url_job(
    job_id: str,
    url: str,
    mode: str,
    include_audience: bool,
    force: bool,
) -> None:
    try:
        result = prepare_video(
            url,
            mode=mode,  # type: ignore[arg-type]
            include_audience=include_audience,
            force=force,
        )
        _finish_job(job_id, result=result)
    except Exception as exc:
        _finish_job(job_id, error=exc)


def _run_upload_job(
    job_id: str,
    file_path: str,
    mode: str,
    force: bool,
) -> None:
    try:
        result = prepare_uploaded_video(
            file_path,
            mode=mode,  # type: ignore[arg-type]
            force=force,
        )
        _finish_job(job_id, result=result)
    except Exception as exc:
        _finish_job(job_id, error=exc)


def _new_job(
    *,
    source: str,
    source_kind: str,
    mode: str,
) -> str:
    job_id = uuid.uuid4().hex
    request_fingerprint = hashlib.sha256(
        f"{source_kind}:{source}".encode(
            "utf-8"
        )
    ).hexdigest()[:24]
    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "task_id": job_id,
            "request_fingerprint": request_fingerprint,
            "status": "running",
            "source": source,
            "source_kind": source_kind,
            "mode": mode,
            "started_at": time.time(),
        }
    return job_id


@mcp.tool(
    title="Start URL video analysis",
    description=(
        "Start preparing a Bilibili or YouTube URL. "
        "Deep mode builds an adaptive scene overview, long-video chapter index, "
        "and searchable evidence memory. Keep job_id private and wait internally."
    ),
    annotations=READ_FETCH,
)
def start_video_analysis(
    url: str,
    mode: Literal["deep", "quick"] = "deep",
    include_audience: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    job_id = _new_job(
        source=url,
        source_kind="url",
        mode=mode,
    )
    _executor.submit(
        _run_url_job,
        job_id,
        url,
        mode,
        include_audience,
        force,
    )
    with _jobs_lock:
        job = dict(_jobs[job_id])
    return {
        "job_id": job_id,
        "task_id": job_id,
        "request_fingerprint": job.get(
            "request_fingerprint"
        ),
        "status": "running",
        "instruction": (
            "Call wait_video_analysis with this job_id. "
            "Do not ask the user to poll."
        ),
    }


@mcp.tool(
    title="Start uploaded video analysis",
    description=(
        "Start analyzing a host-materialized/uploaded local video file. "
        "The path must be inside VIDEO_UPLOAD_ROOTS (default: the dedicated "
        "~/.video-understanding/inbox). This prevents arbitrary local-file access. "
        "Use only when the host actually exposes/materializes the user attachment."
    ),
    annotations=READ_FETCH,
)
def start_uploaded_video_analysis(
    file_path: str,
    mode: Literal["deep", "quick"] = "deep",
    force: bool = False,
) -> dict[str, Any]:
    job_id = _new_job(
        source=file_path,
        source_kind="uploaded_file",
        mode=mode,
    )
    _executor.submit(
        _run_upload_job,
        job_id,
        file_path,
        mode,
        force,
    )
    with _jobs_lock:
        job = dict(_jobs[job_id])
    return {
        "job_id": job_id,
        "task_id": job_id,
        "request_fingerprint": job.get(
            "request_fingerprint"
        ),
        "status": "running",
        "instruction": (
            "Call wait_video_analysis with this job_id. "
            "Do not ask the user to poll."
        ),
    }


@mcp.tool(
    title="Wait for video analysis",
    description=(
        "Wait briefly for a previously started URL/upload analysis job. "
        "If still running, call again internally; never expose polling mechanics to the user."
    ),
    annotations=READ_FETCH,
)
def wait_video_analysis(
    job_id: str,
    wait_seconds: int = 25,
) -> dict[str, Any]:
    wait_seconds = max(0, min(int(wait_seconds), 30))
    deadline = time.monotonic() + wait_seconds
    while True:
        with _jobs_lock:
            job = dict(_jobs.get(job_id) or {})
        if not job:
            return {
                "job_id": job_id,
                "status": "failed",
                "error": {
                    "code": "VIDEO_NOT_FOUND",
                    "message": "Unknown job_id.",
                },
            }

        if (
            job.get("status") != "running"
            or time.monotonic() >= deadline
        ):
            if job.get("status") == "complete":
                return {
                    "job_id": job_id,
                    "task_id": job.get(
                        "task_id"
                    ),
                    "request_fingerprint": job.get(
                        "request_fingerprint"
                    ),
                    "status": "complete",
                    "result": job.get("result"),
                }
            if job.get("status") == "failed":
                return {
                    "job_id": job_id,
                    "task_id": job.get(
                        "task_id"
                    ),
                    "request_fingerprint": job.get(
                        "request_fingerprint"
                    ),
                    "status": "failed",
                    "error": job.get("error"),
                }
            return {
                "job_id": job_id,
                "task_id": job.get(
                    "task_id"
                ),
                "request_fingerprint": job.get(
                    "request_fingerprint"
                ),
                "status": "running",
                "elapsed_seconds": round(
                    time.time()
                    - float(
                        job.get("started_at")
                        or time.time()
                    ),
                    1,
                ),
                "instruction": (
                    "Call wait_video_analysis again. "
                    "Do not ask the user to poll."
                ),
            }
        time.sleep(0.5)


@mcp.tool(
    title="Get video manifest",
    description=(
        "Return normalized metadata, acquisition status, long-video tier, "
        "chapter/evidence counts, scene count, frame count, and warnings."
    ),
    annotations=READ_FETCH,
)
def get_video_manifest(
    session_id: str,
) -> dict[str, Any]:
    try:
        return public_manifest(session_id)
    except VideoRuntimeError as exc:
        return {
            "status": "failed",
            "error": {
                "code": exc.code,
                "message": str(exc),
            },
        }


@mcp.tool(
    title="Get transcript window",
    description=(
        "Return timestamped transcript segments for a bounded time window. "
        "For long videos, prefer chapters/search first, then fetch only relevant transcript windows."
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
            start_seconds=max(
                0.0,
                float(start_seconds),
            ),
            end_seconds=end_seconds,
            max_chars=max(
                2000,
                min(int(max_chars), 40000),
            ),
        )
    except VideoRuntimeError as exc:
        return {
            "status": "failed",
            "error": {
                "code": exc.code,
                "message": str(exc),
            },
        }


@mcp.tool(
    title="Get long-video chapters",
    description=(
        "Return structural chapter windows for a prepared video. "
        "These are evidence navigation windows, not fabricated semantic summaries."
    ),
    annotations=READ_FETCH,
)
def get_video_chapters(
    session_id: str,
) -> dict[str, Any]:
    try:
        return chapter_index(session_id)
    except VideoRuntimeError as exc:
        return {
            "status": "failed",
            "error": {
                "code": exc.code,
                "message": str(exc),
            },
        }


@mcp.tool(
    title="Search video memory",
    description=(
        "Search overlapping transcript evidence windows for a question or topic. "
        "Use this before loading large long-video transcripts. "
        "Important answers should still be verified with transcript/visual rewatch."
    ),
    annotations=READ_FETCH,
)
def search_prepared_video(
    session_id: str,
    query: str,
    limit: int = 8,
) -> dict[str, Any]:
    try:
        return search_video_memory(
            session_id,
            query=query,
            limit=limit,
        )
    except VideoRuntimeError as exc:
        return {
            "status": "failed",
            "error": {
                "code": exc.code,
                "message": str(exc),
            },
        }


@mcp.tool(
    title="Inspect video frames",
    description=(
        "Return timestamp labels and actual JPEG ImageContent from a prepared video. "
        "Use density='overview' for global coverage and density='dense' for agentic "
        "rewatch of a relevant interval. The host model may read on-screen text directly."
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
            start_seconds=max(
                0.0,
                float(start_seconds),
            ),
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
                f"Video frame batch: session={session_id}, "
                f"density={density}, "
                f"range={start_seconds}-"
                f"{end_seconds if end_seconds is not None else 'end'}, "
                f"frames={len(frames)}. "
                "Each timestamp label immediately precedes its image."
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
                    f"Frame {index}/{len(frames)} @ "
                    f"{float(item['timestamp_seconds']):.3f}s "
                    f"reason={item.get('reason')}"
                ),
            )
        )
        blocks.append(
            ImageContent(
                type="image",
                data=base64.b64encode(
                    path.read_bytes()
                ).decode("ascii"),
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
