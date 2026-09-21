# Video Understanding v0.2.3 Audit Results

Date: 2026-09-22
Status: release-candidate
Repository: `1948666760dty-sys/agent-skills`

## Summary

v0.2.3 fixes the real failures observed with two uploaded MP4 samples:

- audio presence/decodability is now separate from speech transcription;
- Deep completion now uses an explicit Completion Guard;
- partial/corrupt video keeps healthy audio and surviving visual evidence;
- repair is evaluated against the original timeline, so truncation cannot masquerade as a successful repair;
- each job/result carries task/request/session/source identity to prevent stale-result cross-talk;
- `深度看` is a strong Deep-mode trigger.

## Real sample A — healthy H.264

File used in local regression: `1000037705.mp4`

Observed:
- duration: 24.45 s
- video: H.264, 1080×1920, 30 fps
- audio: AAC, 44.1 kHz, stereo
- audio_present: true
- audio_decodable: true
- speech_transcribed: false in the current Native test environment
- visual_coverage_ratio: 1.0
- visual decode errors: none
- Completion Guard: PARTIAL

Why PARTIAL:
visual coverage is complete, but the audio/speech content was not transcribed in the current environment.

This intentionally replaces the incorrect wording “audio cannot be heard” with the more precise state “audio is present and decodable, but speech transcription is unavailable/not completed.”

## Real sample B — partially corrupt HEVC

File used in local regression: `1000034255.mp4`

Observed:
- duration: 30.531995 s
- video: HEVC/H.265, 2160×3840, 60 fps
- audio: AAC, 44.1 kHz, stereo
- audio_present: true
- audio_decodable: true
- speech_transcribed: false in the current Native test environment
- last decoded visual timestamp: 8.533333 s
- visual_coverage_ratio: 0.279488 (~27.9%)
- Completion Guard: PARTIAL

Decoder errors included:
- `Invalid NAL unit size`
- `Error splitting the input into NAL units`
- `Decoding error: Invalid data found when processing input`

The healthy AAC audio is preserved even though the HEVC stream fails.

## Repair audit

Both repair paths were exercised against the corrupt HEVC sample:

1. tolerant remux
2. H.264 ultrafast transcode

Both produced a clean candidate of about 8.533333 s.

Important guard:
- candidate internal coverage: 100% of its shortened file
- preserved coverage of the original 30.531995 s timeline: still 0.279488
- adopted: false

Therefore, truncation is correctly rejected as a “successful repair.”

## Real regression harness

Script:
`skills/video-understanding/runtime/scripts/media_health_regression.py`

Local real-sample regression result:
- healthy audio decode: PASS
- healthy visual coverage: PASS
- healthy/no-ASR => PARTIAL: PASS
- corrupt audio preserved: PASS
- corrupt visual coverage ≈27.9%: PASS
- truncated-remux repair rejection: PASS
- synthetic complete visual + near-full ASR => COMPLETE: PASS

## ASR test status

A direct attempt to install `faster-whisper==1.2.1` in the current Native analysis container failed because that container cannot resolve external package hosts.

This is an environment-network limitation, not a passing ASR inference test.

However, the repository-level GitHub Actions audit successfully installed the full Runtime dependency set, and Runtime preflight passed, including importing faster-whisper.

A real speech transcription/model inference on the target Windows machine remains required before stable release.

## GitHub Actions audit

Permanent workflow:
`.github/workflows/video-understanding-audit.yml`

Audit run:
- run id: `35668142940`
- result: SUCCESS

All steps passed:
1. checkout
2. Python 3.12 setup
3. FFmpeg installation
4. Runtime dependency installation
5. Python compile
6. JSON/TOML validation
7. Runtime preflight
8. synthetic media-health smoke
9. MCP server startup + 8-tool smoke

The temporary PR used only to trigger the workflow was closed and not merged.

## Static repository checks

Verified on canonical main:
- Skill version: 0.2.3
- Runtime package version: 0.2.3
- schema: 0.2.3
- regression cases: 50
- 8 MCP tools present
- `深度看` strong trigger present
- audio tri-state present
- Completion Guard present
- source/task identity guard present
- literal `\\n` formatting bugs in pyproject/preflight fixed
- media-health regression script present

## Remaining release blockers

Before `stable`:
- real faster-whisper inference on target Windows runtime;
- real MCP upload/inbox end-to-end on target Windows;
- at least one 30–90 minute video;
- at least one 90–180 minute video;
- real ChatGPT/MCP task identity delivery validation.
