import datetime
import os

import streamlit as st

from transcribe import transcribe

st.title("Transcribe")

# Shared state for files and output directory
if "audio_files" not in st.session_state:
    st.session_state.audio_files = []
if "output_dir" not in st.session_state:
    st.session_state.output_dir = ""
if "last_destination" not in st.session_state:
    st.session_state.last_destination = ""

tabs = st.tabs(["Upload", "Generate", "View"])

with tabs[0]:
    st.header("Upload Audio Files")
    audio_files = st.file_uploader(
        "Select audio files",
        accept_multiple_files=True,
        type=["mp3", "wav", "m4a"],
    )
    if audio_files:
        st.session_state.audio_files = audio_files
        st.success(f"{len(audio_files)} file(s) uploaded.")

with tabs[1]:
    st.header("Generate Transcriptions")
    output_dir = st.text_input(
        "Output directory",
        placeholder="~/Documents",
        value=st.session_state.output_dir,
    )
    if output_dir:
        st.session_state.output_dir = output_dir

    audio_files = st.session_state.get("audio_files", [])
    run_disabled = not audio_files or not output_dir

    def run_transcribe():
        destination = (
            os.path.expanduser(output_dir)
            + f"/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        os.makedirs(destination, exist_ok=True)
        for uploaded_file in audio_files:
            file_path = os.path.join(destination, uploaded_file.name)
            uploaded_file.seek(0)
            with open(file_path, "wb") as out_file:
                out_file.write(uploaded_file.read())
            transcribe(file_path, destination)
            os.remove(file_path)
        st.session_state.last_destination = destination
        st.success("Transcription complete!")

    st.button("Run", disabled=run_disabled, on_click=run_transcribe)
    if not audio_files:
        st.info("Please upload audio files first.")
    if not output_dir:
        st.info("Please set an output directory.")

with tabs[2]:
    st.header("View Transcriptions")
    last_destination = st.session_state.get("last_destination", "")
    if last_destination and os.path.isdir(last_destination):
        vtt_files = [f for f in os.listdir(last_destination) if f.endswith(".vtt")]
        if vtt_files:
            st.write(f"Found {len(vtt_files)} VTT file(s):")
            for vtt_file in vtt_files:
                file_path = os.path.join(last_destination, vtt_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    st.subheader(vtt_file)
                    st.text(f.read())
        else:
            st.info("No VTT files found in the last output directory.")
    else:
        st.info("No transcriptions to view yet. Run a transcription first.")
