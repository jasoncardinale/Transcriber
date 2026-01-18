import datetime
import os
import tempfile

import streamlit as st

from transcribe import transcribe

st.title("Transcribe")

st.header("Upload Audio Files")

audio_files = st.file_uploader(
    "",
    accept_multiple_files=True,
    type=["mp3", "wav", "m4a"],
)

st.header("Generate Transcriptions")

st.subheader("Output directory")
output_dir = st.text_input(
    "Enter folder name where you want your transcriptions saved",
    placeholder="~/Documents",
)


def run_transcribe():
    destination = (
        os.path.expanduser(output_dir)
        + f"/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(destination, exist_ok=True)
    for uploaded_file in audio_files:
        # Use the original filename
        file_path = os.path.join(destination, uploaded_file.name)
        # Save the uploaded file to disk
        with open(file_path, "wb") as out_file:
            out_file.write(uploaded_file.read())
        # Pass the saved file path to transcribe
        transcribe(file_path, destination)


run_disabled = not audio_files or not output_dir

st.button("Run", disabled=run_disabled, on_click=run_transcribe)
