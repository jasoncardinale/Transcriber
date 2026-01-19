import datetime
import os
from parser import parse_vtt
from pathlib import Path

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

tabs = st.tabs(["Upload", "Read"])

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

    # st.header("Generate Transcriptions")
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
        destination = os.path.expanduser(output_dir)
        os.makedirs(destination, exist_ok=True)
        for uploaded_file in audio_files:
            file_path = os.path.join(destination, uploaded_file.name)
            uploaded_file.seek(0)
            with open(file_path, "wb") as out_file:
                out_file.write(uploaded_file.read())
            transcribe(file_path, destination)

        st.session_state.last_destination = destination
        st.success("Transcription complete!")

    st.button("Run", disabled=run_disabled, on_click=run_transcribe)
    if not audio_files:
        st.info("Please upload audio files first.")
    if not output_dir:
        st.info("Please set an output directory.")

with tabs[1]:
    st.header("View Transcriptions")

    last_destination = st.session_state.get("last_destination", "")

    folder = st.text_input(
        "Folder containing transcriptions",
        placeholder="~/Documents",
        value=last_destination,
    )

    if folder and os.path.isdir(folder):
        dir = os.listdir(folder)
        vtt_files = [f for f in dir if f.endswith(".vtt")]
        file_pairs: dict[str, str | None] = {}
        for vtt_name in vtt_files:
            file_pairs[vtt_name] = None
            vtt_stem = Path(vtt_name).stem

            for f in dir:
                p = Path(f)
                if p.stem == vtt_stem and p.suffix != ".vtt":
                    file_pairs[vtt_name] = f
                    break

        if file_pairs:

            def timestamp_to_seconds(ts):
                m, s = ts.split(":")
                s, ms = s.split(".")
                return int(m) * 60 + int(s) + int(ms) / 1000

            st.write(f"Found {len(file_pairs)} transcription file(s):")
            for vtt_name, audio in file_pairs.items():
                file_path = os.path.join(folder, vtt_name)
                audio_path = os.path.join(folder, audio) if audio else None
                with st.expander(vtt_name):
                    # if audio_path:
                    # st.audio(audio_path)
                    segments = parse_vtt(file_path, audio)

                    seek_key = f"seek_{audio}"
                    if seek_key not in st.session_state:
                        st.session_state[seek_key] = 0.0

                    autoplay_key = f"autoplay_{audio}"
                    if autoplay_key not in st.session_state:
                        st.session_state[autoplay_key] = False

                    st.audio(
                        audio_path,
                        start_time=st.session_state[seek_key],
                        autoplay=st.session_state[autoplay_key],
                    )

                    for idx, (text, start, end) in enumerate(segments):
                        start_sec = timestamp_to_seconds(start)
                        if st.button(text, key=f"{audio}_{idx}"):
                            st.session_state[seek_key] = start_sec
                            st.session_state[autoplay_key] = True
                            st.rerun()
                        st.write(
                            f"<span style='color: #888; font-size: 0.9em;'>[{start}]</span>",
                            unsafe_allow_html=True,
                        )
        else:
            st.info("No transcription files found in the specified directory.")
    else:
        st.info("No transcriptions to view yet. Run a transcription first.")
