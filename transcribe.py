import whisper
import sys

def transcribe_cli():
    args = sys.argv[1:]

    if len(args) != 1:
        print("Example usage: python transcribe_cli audio.wav")

    audio_file = args[1]

    model = whisper.load_model("turbo")
    result = model.transcribe(audio_file)
