import os
import sys

# Set up ffmpeg path BEFORE any other imports
if getattr(sys, "frozen", False):
    # Running as bundled executable - ffmpeg is in _MEIPASS
    bundle_dir = sys._MEIPASS  # type: ignore[attr-defined]
else:
    # Running as script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Add bundle directory to PATH so subprocess can find ffmpeg
os.environ["PATH"] = bundle_dir + os.pathsep + os.environ.get("PATH", "")

# Also set it explicitly for whisper/ffmpeg-python which may use these
os.environ["FFMPEG_BINARY"] = os.path.join(bundle_dir, "ffmpeg")

from streamlit.web import cli as stcli

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port=8501",
        "--global.developmentMode=false",
        "--theme.base=light",
        "--theme.primaryColor=#10475a",
        "--theme.secondaryBackgroundColor=#f2f9f2",
    ]

    stcli.main()
