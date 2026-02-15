import asyncio
import os
from pathlib import Path
from typing import Literal

import flet as ft
import flet_audio as fta

from transcribe import parse_vtt, timestamp_to_seconds, transcribe

AUDIO_VIDEO_EXTS = [
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
]


def main(page: ft.Page):
    page.title = "Audio Transcription Tool"
    page.window.width = 800
    page.window.height = 800

    audio_files: list[str] = []
    output_dir: str = ""
    file_pairs: dict[str, str | None] = {}
    selected_folder: str = ""
    selected_vtt: str = ""

    upload_message = ft.Text("No files uploaded yet. Please select your audio files above.", color="grey")

    run_message = ft.Text("")
    run_progress = ft.ProgressRing(visible=False)
    run_button = ft.Button(
        "Run",
        bgcolor="blue",
        color="white",
        width=200,
    )

    view_message = ft.Text("")
    segment_controls = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=400)
    end_timestamps: list[int] = []
    playback_controls = ft.Row()

    audio_player = None

    # --- Upload Tab ---
    async def select_files(_: ft.Event[ft.Button]):
        files = await ft.FilePicker().pick_files(
            allow_multiple=True,
            allowed_extensions=AUDIO_VIDEO_EXTS,
        )
        if files:
            audio_files.clear()
            for f in files:
                if f.path:
                    audio_files.append(f.path)
            if audio_files:
                upload_message.value = f"Uploaded {len(audio_files)} file(s). You can now proceed to the next step."
                upload_message.color = "green"
        else:
            upload_message.value = "No files uploaded yet. Please select your audio files above."
            upload_message.color = "grey"
        page.update()

    async def select_output_directory(_: ft.Event[ft.Button]):
        nonlocal output_dir

        directory = await ft.FilePicker().get_directory_path()
        if directory:
            output_dir_input.value = directory
            output_dir = directory
            page.update()

    output_dir_input = ft.TextField(
        label="Output folder (where your transcriptions will be saved):",
        width=600,
    )

    async def run_transcribe():
        run_progress.visible = True
        run_button.disabled = True
        page.update()

        output_dir_value = output_dir_input.value

        if not audio_files or not output_dir_value:
            run_message.value = "Please select files and output folder."
            run_message.color = "red"
            page.update()
            return
        else:
            run_message.value = ""
            run_message.color = ""
            page.update()

        transcription_path = os.path.expanduser(output_dir_value)
        os.makedirs(transcription_path, exist_ok=True)
        errors: list[str] = []
        for file_path in audio_files:
            filename = None
            try:
                filename = os.path.basename(file_path)
                audio_path = os.path.join(transcription_path, filename)
                with open(file_path, "rb") as src, open(audio_path, "wb") as dst:
                    dst.write(src.read())
                await asyncio.to_thread(transcribe, audio_path, transcription_path)
            except Exception as e:
                errors.append(f"Unable to transcribe {filename}: {e}")

        last_destination = transcription_path
        if errors:
            run_message.value = "\n".join(errors)
            run_message.color = "red"
        else:
            run_message.value = "Transcription complete! Click 'View Transcriptions'"
            run_message.color = "green"

        view_dir_input.value = last_destination
        refresh_view_tab()

        run_progress.visible = False
        run_button.disabled = False

        page.update()

    run_button.on_click = run_transcribe

    upload_tab = ft.Column(
        [
            ft.Text(
                "Step 1: Upload Your Audio/Video Files",
                size=22,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text("Select one or more files from your computer to transcribe.", size=14),
            ft.Row(
                [
                    ft.Button(
                        "Browse Files",
                        on_click=select_files,
                    ),
                ]
            ),
            upload_message,
            ft.Divider(),
            ft.Text("Step 2: Generate Transcriptions", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Choose a folder where you want your transcription files to be saved.\nThen click Run to start the transcription process.",
                size=14,
            ),
            ft.Row(
                [
                    output_dir_input,
                    ft.Button(
                        "Browse Folder",
                        on_click=select_output_directory,
                    ),
                ]
            ),
            ft.Row(
                [
                    run_button,
                    run_progress,
                ]
            ),
            run_message,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # --- View Tab ---
    vtt_list = ft.ListView(expand_loose=True, height=200, spacing=4, visible=False)

    view_dir_input = ft.TextField(
        label="Folder containing your transcriptions",
        width=600,
    )

    def make_segment_click(seek_time: int):
        async def _on_click():
            if audio_player:
                await audio_player.play(ft.Duration(seconds=seek_time))

        return _on_click

    def control_playback(command: Literal["start", "pause", "resume"]):
        async def _on_click():
            if audio_player:
                match command:
                    case "start":
                        await audio_player.play(ft.Duration(seconds=0))
                    case "pause":
                        await audio_player.pause()
                    case "resume":
                        await audio_player.resume()

        return _on_click

    def handle_audio_state_change(event: fta.AudioStateChangeEvent):
        playback_controls.controls.clear()
        playback_controls.controls.append(ft.Button("Start", icon=ft.Icons.START, on_click=control_playback("start")))

        if event.state == fta.AudioState.PAUSED:
            playback_controls.controls.append(ft.Button("Resume", icon=ft.Icons.PLAY_CIRCLE, on_click=control_playback("resume")))
        elif event.state == fta.AudioState.PLAYING:
            playback_controls.controls.append(ft.Button("Pause", icon=ft.Icons.PAUSE_CIRCLE, on_click=control_playback("pause")))

    async def handle_audio_position_change(event: fta.AudioPositionChangeEvent):
        seconds = event.position // 1000
        updated = False

        for i, t in enumerate(end_timestamps):
            segment_controls.controls[i].opacity = 0.7
            if t >= seconds:
                if not updated:
                    segment_controls.controls[i].opacity = 1.0
                    await segment_controls.scroll_to(scroll_key=end_timestamps[i], duration=200)
                    updated = True

    transcript_text = ft.Text("Select a transcript", size=22, weight=ft.FontWeight.BOLD, color="grey")

    def show_transcription(vtt_name: str):
        nonlocal selected_vtt, audio_player

        vtt_list.visible = False
        select_transcript_button.visible = True

        transcript_text.value = vtt_name
        transcript_text.color = "black"

        folder = selected_folder
        audio_file = file_pairs.get(vtt_name)
        file_path = os.path.join(folder, vtt_name)
        audio_path = os.path.join(folder, audio_file) if audio_file else None
        selected_vtt = file_path

        segments = parse_vtt(file_path)
        segment_controls.controls.clear()
        end_timestamps.clear()
        playback_controls.controls.clear()

        if audio_path and os.path.exists(audio_path):
            audio_player = fta.Audio(
                src=audio_path,
                autoplay=False,
                release_mode=fta.ReleaseMode.STOP,
                on_state_change=handle_audio_state_change,
                on_position_change=handle_audio_position_change,
            )

        playback_controls.controls.clear()
        playback_controls.controls.append(ft.Button("Start", icon=ft.Icons.START, on_click=control_playback("start")))

        for text, start, end in segments:
            start_seconds = timestamp_to_seconds(start)
            end_seconds = timestamp_to_seconds(end)
            end_timestamps.append(end_seconds)
            segment_controls.controls.append(
                ft.TextButton(
                    f"[{start}] {text}",
                    style=ft.ButtonStyle(
                        padding=10,
                        shape=ft.RoundedRectangleBorder(radius=6),
                    ),
                    on_click=make_segment_click(start_seconds),
                    key=ft.ScrollKey(start_seconds),
                )
            )

        page.update()

    def refresh_view_tab():
        nonlocal selected_folder

        folder = view_dir_input.value
        selected_folder = folder
        vtt_list.controls.clear()
        file_pairs.clear()

        if folder and os.path.isdir(folder):
            dir_files = os.listdir(folder)
            vtt_files = [f for f in dir_files if f.endswith(".vtt")]

            for vtt_name in vtt_files:
                vtt_stem = Path(vtt_name).stem
                audio_file = None
                for f in dir_files:
                    p = Path(f)

                    if p.stem == vtt_stem and p.suffix != ".vtt":
                        audio_file = f
                        break

                file_pairs[vtt_name] = audio_file
                vtt_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(vtt_name),
                        subtitle=ft.Text(audio_file if audio_file else "No audio found"),
                        on_click=lambda _, vtt=vtt_name: show_transcription(vtt),
                    )
                )

            if file_pairs:
                view_message.value = f"Found {len(file_pairs)} transcription file{'' if len(file_pairs) == 1 else 's'}. Select one to view."
                view_message.color = "green"
            else:
                view_message.value = "No transcription files found in the specified directory."
                view_message.color = "red"
        else:
            view_message.value = "No transcriptions to view yet. Generate a transcription first."
            view_message.color = "grey"

        vtt_list.visible = bool(vtt_list.controls)
        select_transcript_button.visible = True

        playback_controls.controls.clear()
        segment_controls.controls.clear()
        end_timestamps.clear()
        page.update()

    view_dir_input.on_change = refresh_view_tab

    async def select_viewed_directory():
        directory = await ft.FilePicker().get_directory_path()
        if directory:
            view_dir_input.value = directory
            refresh_view_tab()
            page.update()

    def open_list():
        vtt_list.visible = True
        select_transcript_button.visible = False
        page.update()

    select_transcript_button = ft.Button("Select transcript", visible=not vtt_list.visible, on_click=open_list)

    view_tab = ft.Column(
        [
            ft.Text(
                "View and Listen to Your Transcriptions",
                size=22,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                [
                    view_dir_input,
                    ft.Button(
                        "Browse Folder",
                        on_click=select_viewed_directory,
                    ),
                ]
            ),
            view_message,
            vtt_list,
            ft.Divider(),
            ft.Row(
                [transcript_text, select_transcript_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            playback_controls,
            segment_controls,
            ft.Divider(),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    tabs = ft.Tabs(
        selected_index=0,
        length=2,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Upload Audio/Video", icon=ft.Icons.UPLOAD_FILE),
                        ft.Tab(label="View Transcriptions", icon=ft.Icons.TRANSCRIBE),
                    ]
                ),
                ft.TabBarView(expand=True, controls=[upload_tab, view_tab]),
            ],
        ),
        expand=True,
    )

    page.add(tabs)


ft.run(main)
