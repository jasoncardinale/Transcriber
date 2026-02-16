import os
import sys


def setup_ffmpeg():
    """
    Set up ffmpeg path by finding the bundled binaries and adding to PATH.
    This avoids static_ffmpeg.add_paths() which tries to write lock files
    to its package directory - which fails in protected locations like Program Files.
    """
    if sys.platform == "win32":
        ffmpeg_subdir = "win32"
    elif sys.platform == "darwin":
        import platform

        if platform.machine() == "arm64":
            ffmpeg_subdir = "darwin_arm64"
        else:
            ffmpeg_subdir = "darwin"
    else:
        ffmpeg_subdir = "linux"

    # Find static_ffmpeg package location and add binaries to PATH
    try:
        import static_ffmpeg

        ffmpeg_bin_dir = os.path.join(os.path.dirname(static_ffmpeg.__file__), "bin", ffmpeg_subdir)
        if os.path.exists(ffmpeg_bin_dir):
            os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")
            return
    except ImportError:
        pass

    # Fallback: use static_ffmpeg.add_paths() if we can't find the binaries
    import static_ffmpeg

    static_ffmpeg.add_paths()
