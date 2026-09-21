# Video Understanding Runtime v0.1.0

This is the executable reference Runtime for `skills/video-understanding/SKILL.md`.

## What it does

- Bilibili native metadata/subtitle extraction, including b23 short-link resolution and multi-part selection metadata.
- YouTube metadata plus manual/automatic caption retrieval.
- Local faster-whisper fallback when no usable subtitle exists.
- Local video-only download for visual work.
- Scene-aware overview frame indexing plus 12-second baseline coverage.
- Dense on-demand frame extraction for agentic rewatch.
- Streamable HTTP MCP server that returns real JPEG `ImageContent` blocks so the host ChatGPT model can inspect the frames directly.
- Internal long-job flow: start → wait → evidence retrieval. The end user should only need to paste a video URL.

## Tools

- `start_video_analysis`
- `wait_video_analysis`
- `get_video_manifest`
- `get_video_transcript`
- `inspect_video_window`

All tools are semantically read/fetch operations. Local cache writes are implementation details; the tools do not modify the source platform or user content.

## Local defaults

- MCP: Streamable HTTP on `127.0.0.1:8765/mcp`.
- Cache: `~/.video-understanding`.
- Whisper model: `small`.
- Whisper device: `auto` (try CUDA, then CPU).
- Visual source: video-only stream capped around 720p when available.
- Overview scene probe: every 3 seconds.
- Baseline coverage: every 12 seconds.
- Returned image width: up to 960 px.

Environment overrides:
- `VIDEO_UNDERSTANDING_CACHE`
- `VIDEO_WHISPER_MODEL`
- `VIDEO_WHISPER_DEVICE`

## Important boundary

The Runtime prepares evidence; the host ChatGPT model performs the final multimodal reasoning.

Recommended host sequence:

1. start the job;
2. keep calling wait internally until complete;
3. retrieve transcript windows;
4. inspect overview frames;
5. identify important/uncertain intervals;
6. call `inspect_video_window(..., density="dense")` for those intervals;
7. synthesize the final answer with evidence labels.

The user should never need to see or operate the internal job id.

## ChatGPT connection

ChatGPT does not directly connect to localhost. Run this MCP locally and connect it through OpenAI Secure MCP Tunnel, or deploy the MCP endpoint remotely. Keep the Runtime private unless you intentionally expose it.

## Current limitations

- v0.1 is anonymous/public-content first.
- Browser-cookie workflows are deliberately not automatic.
- OCR is currently performed by the host vision model from returned frame images; a dedicated local OCR stage is planned.
- Long-video throughput has not yet been benchmarked on the user's machine.
- YouTube/Bilibili extraction can break when upstream sites change.
- No real end-to-end smoke test is claimed until the Runtime is actually installed and run.

## Third-party

The Bilibili-native extractor is vendored from AntaresGG/BiliBiliVideoParser under the MIT License. See `THIRD_PARTY_NOTICES.md` and the vendored LICENSE.
