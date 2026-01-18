import subprocess
import whisper
import sys

from whisper.transcribe import cli
from whisper.utils import SubtitlesWriter, WriteVTT, get_writer


def transcribe(audio_file: str):
    model = whisper.load_model("turbo")

    print("Transcribing audio...")
    result = model.transcribe(audio_file, word_timestamps=True)

    writer = WriteVTT(".")

    for i, (start, end, text) in enumerate(writer.iterate_result(result), start=1):
        print(f"{i}\n{start} --> {end}\n{text}\n")

    return result["text"]


def transcribe_cli():
    args = sys.argv[1:]

    if len(args) != 1:
        print("Example usage: python transcribe_cli audio.wav")
        return

    audio_path = args[0]

    # subprocess.run(["uv", "run", "transcribe.py", audio_path], check=True, capture_output=True, text=True)

    result = transcribe(audio_path)

    print(result)
