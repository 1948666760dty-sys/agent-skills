# Video Understanding Runtime v0.2.0

Executable reference Runtime for `skills/video-understanding/SKILL.md`.

## v0.2 headline

The Runtime is now **Upload-First + Long-Video aware**.

Inputs:
- Bilibili URL
- YouTube URL
- uploaded/local video materialized into a restricted inbox

Long videos are not pushed into one huge model context. The Runtime builds:
- adaptive scene overview
- structural chapter windows
- overlapping Evidence Memory
- local retrieval candidates
- bounded transcript windows
- dense visual rewatch windows

## Current MCP tools

1. `start_video_analysis`
2. `start_uploaded_video_analysis`
3. `wait_video_analysis`
4. `get_video_manifest`
5. `get_video_transcript`
6. `get_video_chapters`
7. `search_prepared_video`
8. `inspect_video_window`

The end user should never operate job IDs or polling.

## Long-video tiers

| Duration | Tier | Baseline | Chapter window | Evidence window |
|---|---|---:|---:|---:|
| <=5 min | short | ~6s | ~2m | ~90s |
| 5–30 min | standard | ~12s | ~4m | ~2m |
| 30–90 min | long | ~20s | ~6m | ~3m |
| 90–180 min | very_long | ~30s | ~10m | ~5m |
| >180 min | ultra_long | ~45s | ~15m | ~7m |

PySceneDetect scene representatives are additional to baseline coverage.

## Scene detection

v0.2 uses:
- PySceneDetect 0.7.x
- AdaptiveDetector
- SceneManager auto-downscale
- baseline fallback if scene detection fails

This replaces the v0.1 fixed histogram-difference detector.

## ASR

- faster-whisper >=1.2.1
- local
- VAD enabled
- `VIDEO_WHISPER_DEVICE=auto` tries CUDA, then CPU int8
- URL platform subtitles remain preferred when available

## Upload inbox security

The MCP uploaded-file tool is deliberately not an arbitrary file reader.

Default allowed directory:

`~/.video-understanding/inbox`

Windows example:

`C:\Users\<you>\.video-understanding\inbox`

Additional allowed roots may be explicitly configured with:

`VIDEO_UPLOAD_ROOTS`

The Runtime rejects a path outside allowed roots.

A ChatGPT attachment only uses this MCP path if the host actually materializes/copies the attachment into an allowed root. The Skill must not invent a local path.

## Windows quick start

1. Run `scripts\install_windows.ps1` once.
2. Run `scripts\run_windows.ps1`.
3. Run `.venv\Scripts\python.exe scripts\mcp_smoke.py`.
4. Confirm all 8 tools appear.
5. Follow `TUNNEL_SETUP.md` if connecting the local MCP to ChatGPT Web.

## Recommended long-video host loop

```text
start + wait
→ manifest
→ chapters
→ first bounded transcript windows
→ overview frames
→ first-pass understanding
→ search_prepared_video(question/topic)
→ exact transcript window
→ dense visual rewatch
→ final answer
```

For 1–3 hour videos, do not request the full transcript and all frames in one model turn.

## Cache

Default:
`~/.video-understanding`

URL video cache can keep downloaded video evidence.

Uploaded videos are not duplicated automatically because multi-hour files can be large; the manifest references the allowed materialized source path. If the source file is later deleted, transcript/memory may remain but visual rewatch requires re-materialization.

## Environment

- `VIDEO_UNDERSTANDING_CACHE`
- `VIDEO_WHISPER_MODEL`
- `VIDEO_WHISPER_DEVICE`
- `VIDEO_UPLOAD_ROOTS`

## Current limitations

- release-candidate: real Windows 30–90m and 90–180m end-to-end benchmarks have not yet passed.
- ChatGPT custom MCP does not automatically receive arbitrary chat attachments; host/materialization support is required for the MCP upload adapter.
- host vision performs OCR in v0.2; there is no dedicated local OCR stage yet.
- URL extraction can change when upstream Bilibili/YouTube behavior changes.
- multi-hour video speed depends strongly on subtitles, GPU, storage and scene complexity.

## Third-party

Bilibili-native extractor:
AntaresGG/BiliBiliVideoParser (MIT), vendored with license preserved.

PySceneDetect:
BSD-3-Clause upstream dependency.

faster-whisper:
MIT upstream dependency.
