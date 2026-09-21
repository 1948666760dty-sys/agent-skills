# Video Understanding Runtime Contract v0.2.3

## 1. Scope

Inputs:
- current-chat video attachment when host-accessible
- Bilibili
- YouTube
- host-materialized upload inside allowed roots

Runtime prepares evidence; host performs final multimodal reasoning.

## 2. Audio State Contract

Never collapse audio state into one boolean.

Required fields:
- `audio_present`
- `audio_decodable`
- `speech_transcribed`
- `transcript_source`

`audio_present=true + audio_decodable=true + speech_transcribed=false` means the audio is healthy but ASR/caption transcription was not completed.

Missing faster-whisper must return/record `ASR_UNAVAILABLE` or a warning and preserve visual/audio evidence; it must not fail the whole upload task by default.

## 3. Visual Health Contract

For uploaded/prepared media, FFprobe/FFmpeg health records:
- duration_seconds
- video/audio codec
- decoded_until_seconds
- visual_coverage_ratio
- decode_errors

Deep visual completion threshold: >=98%.

## 4. Completion Guard

Overall state:
- COMPLETE
- PARTIAL
- FAILED

Deep COMPLETE requires adequate visual coverage when video is present and adequate transcript/caption coverage when audio is present.

Useful but incomplete evidence => PARTIAL.

Do not say “看完了” for PARTIAL.

## 5. Corrupt Video Fallback

If a video becomes undecodable mid-stream:
- keep frames decoded before the failure;
- keep healthy audio;
- continue ASR if possible;
- keep transcript evidence;
- report exact coverage and error;
- attempt repair only as a fallback.

Repair may try:
1. tolerant remux;
2. bounded-duration H.264 transcode.

Repair acceptance must compare decoded coverage to the **original video duration**. A clean truncated prefix must not be accepted as a full repair.

## 6. Task / Session Identity

start/wait job:
- task_id
- request_fingerprint

prepared result:
- session_id
- source_fingerprint

Host must deliver only a result tied to the current task. Stale Skill-update text, previous-video output, or another session must be rejected.

## 7. Upload Security

Default root:
`~/.video-understanding/inbox`

Additional roots:
`VIDEO_UPLOAD_ROOTS`

Outside roots => `UPLOAD_PATH_NOT_ALLOWED`.

## 8. Current MCP Tools

1. start_video_analysis
2. start_uploaded_video_analysis
3. wait_video_analysis
4. get_video_manifest
5. get_video_transcript
6. get_video_chapters
7. search_prepared_video
8. inspect_video_window

## 9. Long Video

Use chapters + Evidence Memory + bounded transcript/frame windows. Do not inject entire 1–3h evidence sets into one model call.

## 10. Scene / Visual

- PySceneDetect AdaptiveDetector
- baseline fallback
- host-vision OCR
- dense agentic rewatch

## 11. External Runtime Requirements

Python dependencies are in `pyproject.toml`.

System executables required:
- ffmpeg
- ffprobe

`scripts/preflight.py` must verify both.

## 12. Errors

- UNSUPPORTED_URL
- VIDEO_NOT_FOUND
- UPLOAD_PATH_NOT_ALLOWED
- MEDIA_DOWNLOAD_FAILED
- ASR_UNAVAILABLE
- ASR_FAILED
- FRAME_EXTRACTION_FAILED
- VISUAL_ANALYSIS_FAILED
- INTERNAL_ERROR

## 13. Regression Samples

`scripts/media_health_regression.py` accepts:
1. a healthy video with healthy audio;
2. a video with partially corrupt visual stream but healthy audio.

It validates audio tri-state semantics, partial visual coverage, Completion Guard and repair scoring against original timeline.

## 14. Stable Gate

Do not mark stable before:
- Python/TOML/static syntax checks pass;
- MCP tool names are consistent;
- real healthy/corrupt sample regression passes;
- real ASR path passes on target Windows runtime;
- 30–90m and 90–180m smoke tests pass.
