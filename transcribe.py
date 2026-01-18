import sys

import whisper
from whisper.transcribe import cli
from whisper.utils import WriteVTT


def transcribe(audio_path: str, output_path: str):
    model = whisper.load_model("turbo")

    print("Transcribing audio...")
    result = model.transcribe(audio_path)

    writer = WriteVTT(output_path)
    writer(result, audio_path)


def transcribe_cli():
    args = sys.argv[1:]

    if len(args) != 2:
        print("Example usage: python transcribe_cli audio.wav ~/Documents")
        return

    audio_path = args[0]
    output_path = args[1]

    # subprocess.run(
    #     ["uv", "run", "transcribe.py", audio_path],
    #     check=True,
    #     capture_output=True,
    #     text=True,
    # )

    transcribe(audio_path, output_path)


if __name__ == "__main__":
    cli()
