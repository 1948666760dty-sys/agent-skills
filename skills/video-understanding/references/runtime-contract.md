# Video Understanding Runtime Contract v0.2.0

## 1. Scope

Reference Runtime:
`skills/video-understanding/runtime/`

Inputs:
- Bilibili URL
- YouTube URL
- host-materialized uploaded/local video inside an allowed inbox

The Runtime prepares evidence. The host model performs final multimodal reasoning.

## 2. Security Boundary for Uploads

`start_uploaded_video_analysis` must never become an arbitrary local-file reader.

Default allowed root:
`~/.video-understanding/inbox`

Optional additional roots:
`VIDEO_UPLOAD_ROOTS` using the platform path separator.

A path outside allowed roots returns:
`UPLOAD_PATH_NOT_ALLOWED`.

A ChatGPT attachment can use this tool only when the host has actually materialized the file into an allowed root. If not, the host must process the attachment through its own file runtime or explain the limitation.

## 3. Current MCP Tools

1. start_video_analysis
2. start_uploaded_video_analysis
3. wait_video_analysis
4. get_video_manifest
5. get_video_transcript
6. get_video_chapters
7. search_prepared_video
8. inspect_video_window

All are read/fetch semantics with local cache as an implementation detail.

## 4. Long-Video Strategy

Runtime profile by duration:

- <=5m: short
- <=30m: standard
- <=90m: long
- <=180m: very_long
- >180m: ultra_long

Each profile defines:
- baseline frame step
- overview frame budget
- chapter window
- evidence-memory window/overlap
- PySceneDetect frame skip

The Runtime must not load full long-video evidence into one model call.

Recommended host:
```text
manifest
→ chapters
→ search evidence / transcript windows
→ overview frames
→ identify important intervals
→ dense rewatch
→ final synthesis
```

## 5. PySceneDetect

Reference Runtime uses:
- scenedetect-headless >=0.7.1
- SceneManager
- AdaptiveDetector
- auto_downscale=true

If scene detection fails:
- preserve baseline coverage
- return warning
- do not claim scene-aware success.

## 6. ASR

Reference:
- faster-whisper >=1.2.1
- local model
- device=auto attempts CUDA then CPU int8
- VAD enabled

Platform subtitles remain preferred for URL inputs.

Uploaded-file v0.2 uses ASR unless the host separately supplies a trusted subtitle track.

## 7. Chapters

Runtime chapters are structural navigation windows, not generated semantic chapter summaries.

They contain:
- chapter_id
- start/end
- segment_count
- characters
- preview
- title=null
- summary=null
- status=structural_window

The host may assign semantic titles only after actual content understanding.

## 8. Evidence Memory

Runtime builds overlapping transcript chunks.

`search_prepared_video` uses local lexical/BM25-like scoring and returns candidate windows.

It is a retrieval step, not factual verification.

Important answers should still inspect:
- transcript window
- visual frames when relevant.

No embedding API is required.

## 9. Visual

Deep mode:
- URL: downloads a video-only stream capped near 720p when available
- upload: uses the allowed materialized file directly
- overview frame budget adapts to duration
- returned frame image width is capped to reduce context/transport cost
- dense rewatch max 20 images per tool call

OCR status in v0.2 remains:
`host_vision`

Do not claim local OCR ran unless a future local OCR stage is actually executed.

## 10. Upload Cache

Uploaded videos are not automatically duplicated into cache because multi-hour files can be very large.

Manifest stores the allowed absolute source path for later rewatch.

If the host deletes the source:
- transcript/memory may still exist
- future visual rewatch returns a clear re-upload/materialization error.

## 11. Context Protection

For long/very_long/ultra_long:
- do not request all transcript segments at once
- do not request all frames at once
- query chapters/search first
- fetch bounded windows.

`get_video_transcript` caps max_chars per call.

`inspect_video_window` caps images per call.

## 12. Errors

- UNSUPPORTED_URL
- VIDEO_NOT_FOUND
- UPLOAD_PATH_NOT_ALLOWED
- MEDIA_DOWNLOAD_FAILED
- ASR_FAILED
- FRAME_EXTRACTION_FAILED
- VISUAL_ANALYSIS_FAILED
- INTERNAL_ERROR

Partial success is allowed and must be labelled.

## 13. Performance

No fixed SLA.

60-minute captioned video 5–15 minutes is an optimization target, not a guarantee.

Longer/no-caption/visual-heavy videos can take materially longer.

## 14. Stable Gate

Do not mark stable before real smoke tests cover:
- short upload
- 30–90m upload
- 90–180m input
- Bilibili
- YouTube
- ASR fallback
- scene detector success and fallback
- Video Memory retrieval
- dense rewatch
- upload path security.
