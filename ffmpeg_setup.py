import os
import platform
import stat
import sys


def setup_ffmpeg():
    """
    Add bundled ffmpeg binaries from assets/ffmpeg/{platform}/ to PATH.
    """
    if sys.platform == "win32":
        subdir = "win32"
    elif sys.platform == "darwin":
        subdir = "darwin_arm64" if platform.machine() == "arm64" else "darwin"
    else:
        subdir = "linux"

    # assets/ffmpeg/{platform} is relative to this file
    ffmpeg_dir = os.path.join(os.path.dirname(__file__), "assets", "ffmpeg", subdir)
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

    # Ensure executable permissions on macOS/Linux (packaging may strip them)
    if sys.platform != "win32":
        for binary in ["ffmpeg", "ffprobe"]:
            binary_path = os.path.join(ffmpeg_dir, binary)
            if os.path.exists(binary_path):
                os.chmod(binary_path, os.stat(binary_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
