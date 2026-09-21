from __future__ import annotations

import importlib
import platform
import shutil
import sys

REQUIRED = [
    ("mcp", "MCP SDK"),
    ("yt_dlp", "yt-dlp"),
    ("faster_whisper", "faster-whisper"),
    ("cv2", "OpenCV"),
    ("webvtt", "webvtt-py"),
    ("scenedetect", "PySceneDetect"),
]

EXTERNAL = [
    ("ffmpeg", "FFmpeg decoder"),
    ("ffprobe", "FFprobe metadata probe"),
]

print(f"Python: {sys.version.split()[0]}")
print(f"OS: {platform.platform()}")

failed = False
for module, label in REQUIRED:
    try:
        imported = importlib.import_module(module)
        version = getattr(
            imported,
            "__version__",
            "installed",
        )
        print(f"OK  {label}: {version}")
    except Exception as exc:
        failed = True
        print(f"FAIL {label}: {exc}")

for executable, label in EXTERNAL:
    path = shutil.which(executable)
    if path:
        print(f"OK  {label}: {path}")
    else:
        failed = True
        print(f"FAIL {label}: not found in PATH")

try:
    import ctranslate2

    count = ctranslate2.get_cuda_device_count()
    print(
        f"CUDA devices visible to CTranslate2: {count}"
    )
    if count == 0:
        print(
            "INFO faster-whisper will fall back to CPU "
            "unless CUDA runtime support is installed."
        )
except Exception as exc:
    print(f"INFO CUDA probe unavailable: {exc}")

if failed:
    raise SystemExit(1)

print("Preflight passed.")
