import os
from parser import parse_vtt
from pathlib import Path

import streamlit as st

from transcribe import transcribe

st.title("Audio Transcription Tool")
st.markdown("""
Welcome! This app lets you easily transcribe your audio recordings into text.
Just upload your audio files, choose where to save the results, and generate your transcriptions.
You can also review and listen to your transcriptions right here.
""")

# Shared state for files and output directory
if "audio_files" not in st.session_state:
    st.session_state.audio_files = []
if "output_dir" not in st.session_state:
    st.session_state.output_dir = ""
if "last_destination" not in st.session_state:
    st.session_state.last_destination = ""

tabs = st.tabs(["Upload", "View Transcriptions"])

with tabs[0]:
    st.header("Step 1: Upload Your Audio/Video Files")
    st.markdown("""
    Select one or more files from your computer to transcribe.
    """)
    audio_files = st.file_uploader(
        "Click 'Browse files' and select your audio or video recordings.",
        accept_multiple_files=True,
        type=[
            "wav",
            "mp3",
            "m4a",
            "aac",
            "ogg",
            "flac",
            "opus",
            "wma",
            "alac",
            "amr",
            "aiff",
            "caf",
            "mp4",
            "mov",
            "avi",
            "mkv",
            "webm",
            "flv",
            "wmv",
            "mpeg",
            "m4v",
        ],
    )
    if audio_files:
        st.session_state.audio_files = audio_files
        st.success(
            f"Uploaded {len(audio_files)} file(s). You can now proceed to the next step."
        )
    else:
        st.info("No files uploaded yet. Please select your audio files above.")

    st.header("Step 2: Generate Transcriptions")
    st.markdown("""
    Choose a folder where you want your transcription files to be saved.
    Then click **Run** to start the transcription process.
    """)
    output_dir = st.text_input(
        "Output folder (where your transcriptions will be saved):",
        placeholder="~/Documents/Transcriptions",
        value=st.session_state.output_dir,
    )
    if output_dir:
        st.session_state.output_dir = output_dir
    else:
        st.info("Please enter a folder where your transcriptions will be saved.")

    audio_files = st.session_state.get("audio_files", [])
    run_disabled = not audio_files or not output_dir

    def run_transcribe():
        destination = os.path.expanduser(output_dir)
        os.makedirs(destination, exist_ok=True)
        for uploaded_file in audio_files:
            try:
                file_path = os.path.join(destination, uploaded_file.name)
                uploaded_file.seek(0)
                with open(file_path, "wb") as out_file:
                    out_file.write(uploaded_file.read())
                transcribe(file_path, destination)
            except Exception as e:
                st.error(f"Unable to transcribe {uploaded_file.name} at this time: {e}")

        st.session_state.last_destination = destination
        st.success("Transcription complete!")

    st.button(
        "Run",
        disabled=run_disabled,
        on_click=run_transcribe,
        help="Click to start transcribing your uploaded audio files.",
    )

with tabs[1]:
    st.header("View and Listen to Your Transcriptions")
    st.markdown("""
    Enter the folder where your transcriptions are saved to review your results.
    You can listen to the original audio and read the transcribed text.
    Click on any transcript segment to jump to that part of the audio!
    """)

    last_destination = st.session_state.get("last_destination", "")

    folder = st.text_input(
        "Folder containing your transcriptions",
        placeholder="~/Documents/Transcriptions",
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

                    with st.container(height=500):
                        for idx, (text, start, end) in enumerate(segments):
                            start_sec = timestamp_to_seconds(start)
                            st.write(
                                f"<span style='color: #888; font-size: 0.9em;'>[{start}]</span>",
                                unsafe_allow_html=True,
                            )
                            if st.button(text, key=f"{audio}_{idx}"):
                                st.session_state[seek_key] = start_sec
                                st.session_state[autoplay_key] = True
                                st.rerun()

        else:
            st.info("No transcription files found in the specified directory.")
    else:
        st.info("No transcriptions to view yet. Run a transcription first.")
