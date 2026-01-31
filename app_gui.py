import os
from pathlib import Path
import flet as ft
import flet_audio as fta
from parser import parse_vtt
from transcribe import transcribe

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


def timestamp_to_seconds(ts):
    m, s = ts.split(":")
    s, ms = s.split(".")
    return int(m) * 60 + int(s) + int(ms) // 1000


def main(page: ft.Page):
    page.title = "Audio Transcription Tool"
    page.width = 1100
    page.height = 800

    # State
    audio_files = []
    output_dir = ""
    last_destination = ""
    file_pairs = {}
    segments = []
    selected_folder = ""
    selected_audio = ""
    selected_vtt = ""
    upload_message = ft.Text(
        "No files uploaded yet. Please select your audio files above.", color="grey"
    )
    run_message = ft.Text("")
    view_message = ft.Text("")
    segment_controls = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    audio_player = fta.Audio(src="", autoplay=False)

    # --- Upload Tab ---
    async def select_files(_: ft.Event[ft.Button]):
        print("select_files handler called!")  # DEBUG
        nonlocal audio_files
        files = await ft.FilePicker().pick_files(
            allow_multiple=True,
            allowed_extensions=AUDIO_VIDEO_EXTS,
        )
        print(f"pick_files returned: {files}")  # DEBUG
        if files:
            audio_files.clear()
            for f in files:
                audio_files.append(f.path)
            upload_message.value = f"Uploaded {len(audio_files)} file(s). You can now proceed to the next step."
            upload_message.color = "green"
        else:
            upload_message.value = (
                "No files uploaded yet. Please select your audio files above."
            )
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
        label="Output folder (where your transcriptions will be saved):", width=600
    )

    def on_output_dir_change(e):
        nonlocal output_dir
        output_dir = output_dir_input.value

    output_dir_input.on_change = on_output_dir_change

    def run_transcribe(e):
        nonlocal last_destination
        if not audio_files or not output_dir:
            run_message.value = "Please select files and output folder."
            run_message.color = "red"
            page.update()
            return
        destination = os.path.expanduser(output_dir)
        os.makedirs(destination, exist_ok=True)
        errors = []
        for file_path in audio_files:
            filename = None
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination, filename)
                with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
                    dst.write(src.read())
                transcribe(dest_path, destination)
            except Exception as ex:
                errors.append(f"Unable to transcribe {filename}: {ex}")
        last_destination = destination
        if errors:
            run_message.value = "\n".join(errors)
            run_message.color = "red"
        else:
            run_message.value = "Transcription complete!"
            run_message.color = "green"
        view_folder_input.value = last_destination
        page.update()

    upload_tab = ft.Column(
        [
            ft.Text("Audio Transcription Tool", size=28, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Welcome! This app lets you easily transcribe your audio recordings into text.\n"
                "Just upload your audio files, choose where to save the results, and generate your transcriptions.\n"
                "You can also review and listen to your transcriptions right here.",
                size=16,
            ),
            ft.Divider(),
            ft.Text(
                "Step 1: Upload Your Audio/Video Files",
                size=22,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Select one or more files from your computer to transcribe.", size=14
            ),
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
            ft.Text(
                "Step 2: Generate Transcriptions", size=22, weight=ft.FontWeight.BOLD
            ),
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
            ft.Button(
                "Run",
                on_click=run_transcribe,
                bgcolor="#0078ff",
                color="white",
                width=200,
            ),
            run_message,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # --- View Tab ---
    # async def select_viewed_directory(_):
    #     directory = await ft.FilePicker().get_directory_path()
    #     if directory:
    #         view_folder_input.value = directory
    #         refresh_view_tab()
    #         page.update()

    # view_folder_input = ft.TextField(
    #     label="Folder containing your transcriptions", width=600
    # )

    # def on_view_folder_change(e):
    #     refresh_view_tab()

    # view_folder_input.on_change = on_view_folder_change

    # vtt_list = ft.ListView(expand=True, spacing=4, height=200)

    # def refresh_view_tab():
    #     nonlocal file_pairs, selected_folder
    #     folder = view_folder_input.value or last_destination
    #     selected_folder = folder
    #     vtt_list.controls.clear()
    #     file_pairs.clear()
    #     if folder and os.path.isdir(folder):
    #         dir_files = os.listdir(folder)
    #         vtt_files = [f for f in dir_files if f.endswith(".vtt")]
    #         for vtt_name in vtt_files:
    #             vtt_stem = Path(vtt_name).stem
    #             audio_file = None
    #             for f in dir_files:
    #                 p = Path(f)
    #                 if p.stem == vtt_stem and p.suffix != ".vtt":
    #                     audio_file = f
    #                     break
    #             file_pairs[vtt_name] = audio_file
    #             vtt_list.controls.append(
    #                 ft.ListTile(
    #                     title=ft.Text(vtt_name),
    #                     subtitle=ft.Text(
    #                         audio_file if audio_file else "No audio found"
    #                     ),
    #                     on_click=lambda e, vtt=vtt_name: show_transcription(vtt),
    #                 )
    #             )
    #         if file_pairs:
    #             view_message.value = f"Found {len(file_pairs)} transcription file(s). Select one to view."
    #             view_message.color = "green"
    #         else:
    #             view_message.value = (
    #                 "No transcription files found in the specified directory."
    #             )
    #             view_message.color = "red"
    #     else:
    #         view_message.value = (
    #             "No transcriptions to view yet. Run a transcription first."
    #         )
    #         view_message.color = "grey"
    #     segment_controls.controls.clear()
    #     # audio_player.visible = False
    #     page.update()

    # def show_transcription(vtt_name):
    #     nonlocal segments, selected_audio, selected_vtt
    #     folder = selected_folder
    #     audio_file = file_pairs.get(vtt_name)
    #     file_path = os.path.join(folder, vtt_name)
    #     audio_path = os.path.join(folder, audio_file) if audio_file else None
    #     selected_audio = audio_path
    #     selected_vtt = file_path
    #     segments = parse_vtt(file_path, audio_file)
    #     segment_controls.controls.clear()
    #     if audio_path and os.path.exists(audio_path):
    #         audio_player.src = audio_path
    #         # audio_player.visible = True
    #     # else:
    #     # audio_player.visible = False
    #     for idx, (text, start, end) in enumerate(segments):

    #         def make_on_click(seek_time):
    #             async def _on_click(e):
    #                 # if audio_player.visible:
    #                 await audio_player.seek(
    #                     ft.Duration(seconds=timestamp_to_seconds(seek_time))
    #                 )
    #                 await audio_player.play()

    #             return _on_click

    #         segment_controls.controls.append(
    #             ft.TextButton(
    #                 f"[{start}] {text}",
    #                 style=ft.ButtonStyle(
    #                     # color={"": "#0078ff"},
    #                     # bgcolor={"": "#e3f0ff"},
    #                     padding=10,
    #                     shape=ft.RoundedRectangleBorder(radius=6),
    #                 ),
    #                 on_click=make_on_click(start),
    #             )
    #         )
    #     page.update()

    view_tab = ft.Column(
        [
            # ft.Text(
            #     "View and Listen to Your Transcriptions",
            #     size=22,
            #     weight=ft.FontWeight.BOLD,
            # ),
            ft.Text(
                "Enter the folder where your transcriptions are saved to review your results.\n"
                "You can listen to the original audio and read the transcribed text.\n"
                "Click on any transcript segment to jump to that part of the audio!",
                size=14,
            ),
            # ft.Row(
            #     [
            #         view_folder_input,
            #         ft.Button(
            #             "Browse Folder",
            #             on_click=select_viewed_directory,
            #         ),
            #     ]
            # ),
            # view_message,
            # vtt_list,
            # ft.Text("Transcript Segments:", size=16, weight=ft.FontWeight.BOLD),
            # segment_controls,
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
                        ft.Tab(label="Upload Audio/Video"),
                        ft.Tab(label="View Transcriptions"),
                    ]
                ),
                ft.TabBarView(expand=True, controls=[upload_tab, view_tab]),
            ],
        ),
        expand=True,
    )

    page.add(tabs)


ft.run(main)
