from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from video_understanding_runtime.media_health import (
    attempt_repair,
    completion_guard,
    inspect_media,
)


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Regression test for the two real uploaded-video failure modes: "
            "healthy H.264 with missing ASR, and partially corrupt HEVC with healthy audio."
        )
    )
    parser.add_argument("healthy_video", type=Path)
    parser.add_argument("corrupt_video", type=Path)
    args = parser.parse_args()

    healthy = inspect_media(
        args.healthy_video,
        transcript_source="none",
        transcript=[],
        mode="deep",
    )
    corrupt = inspect_media(
        args.corrupt_video,
        transcript_source="none",
        transcript=[],
        mode="deep",
    )

    assert_true(
        healthy["audio"]["audio_present"] is True,
        "healthy sample should contain audio",
    )
    assert_true(
        healthy["audio"]["audio_decodable"] is True,
        "healthy sample audio should decode fully",
    )
    assert_true(
        healthy["video"]["visual_coverage_ratio"] >= 0.98,
        "healthy sample visual coverage should be complete",
    )
    assert_true(
        healthy["completion"]["status"] == "PARTIAL",
        "healthy sample must stay PARTIAL when speech is not transcribed",
    )
    assert_true(
        healthy["completion"]["speech_transcribed"] is False,
        "audio presence must not be confused with speech transcription",
    )

    assert_true(
        corrupt["audio"]["audio_present"] is True,
        "corrupt sample should contain audio",
    )
    assert_true(
        corrupt["audio"]["audio_decodable"] is True,
        "corrupt sample audio should still decode fully",
    )
    cov = float(
        corrupt["video"]["visual_coverage_ratio"]
    )
    assert_true(
        0.25 <= cov <= 0.35,
        f"corrupt sample visual coverage should be about 27.9%, got {cov:.3%}",
    )
    assert_true(
        corrupt["completion"]["status"] == "PARTIAL",
        "corrupt sample must be PARTIAL",
    )

    with tempfile.TemporaryDirectory() as temp:
        repair = attempt_repair(
            args.corrupt_video,
            Path(temp),
            original_health=corrupt,
        )


    assert_true(
        repair["adopted"] is False,
        "truncating/remuxing to the surviving prefix must not count as repair",
    )
    assert_true(
        abs(
            float(
                repair[
                    "best_visual_coverage_ratio"
                ]
            )
            - cov
        )
        < 0.02,
        "repair scoring must use original timeline duration",
    )

    kinds = {
        item.get("kind"): item
        for item in repair.get("attempts", [])
    }
    assert_true(
        "remux" in kinds,
        "corrupt sample should exercise tolerant remux",
    )
    assert_true(
        "h264_transcode" in kinds,
        "short corrupt sample should exercise H.264 transcode",
    )
    for kind in ("remux", "h264_transcode"):
        item = kinds[kind]
        if item.get("command_succeeded"):
            preserved = float(
                item.get(
                    "preserved_original_timeline_ratio",
                    0.0,
                )
            )
            assert_true(
                abs(preserved - cov) < 0.02,
                f"{kind} must be scored against original timeline",
            )

    synthetic = [
        {"start": 0.0, "end": 29.8, "text": "ok"}
    ]
    complete = completion_guard(
        mode="deep",
        duration_seconds=30.0,
        video_present=True,
        visual_coverage_ratio=1.0,
        audio_present=True,
        audio_decodable=True,
        transcript_source="asr",
        transcript=synthetic,
    )
    assert_true(
        complete["status"] == "COMPLETE",
        "complete visual + near-full ASR should pass Completion Guard",
    )

    print(
        json.dumps(
            {
                "ok": True,
                "healthy": {
                    "visual_coverage_ratio": healthy[
                        "video"
                    ][
                        "visual_coverage_ratio"
                    ],
                    "audio_decodable": healthy[
                        "audio"
                    ][
                        "audio_decodable"
                    ],
                    "speech_transcribed": healthy[
                        "completion"
                    ][
                        "speech_transcribed"
                    ],
                    "status": healthy[
                        "completion"
                    ][
                        "status"
                    ],
                },
                "corrupt": {
                    "decoded_until_seconds": corrupt[
                        "video"
                    ][
                        "decoded_until_seconds"
                    ],
                    "visual_coverage_ratio": cov,
                    "audio_decodable": corrupt[
                        "audio"
                    ][
                        "audio_decodable"
                    ],
                    "status": corrupt[
                        "completion"
                    ][
                        "status"
                    ],
                },
                "repair": {
                    "attempted": repair["attempted"],
                    "adopted": repair["adopted"],
                    "best_visual_coverage_ratio": repair[
                        "best_visual_coverage_ratio"
                    ],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
