# Audio Transcription Tool

Welcome! This app lets you easily transcribe your audio recordings into text using OpenAI Whisper.  
You can upload audio files, generate transcriptions, and review/listen to your results—all in your browser.

---

## Features

- **Easy Upload:** Drag and drop or browse for audio files.
- **Fast Transcription:** Uses OpenAI Whisper for accurate speech-to-text.
- **Organized Output:** Save transcriptions to a folder of your choice.
- **Interactive Review:** Listen to your audio and click on transcript segments to jump to that part of the audio.

---

## Get Started

### Option 1: Download the Executable

1. **Download:**  
   Go to the [Releases](https://github.com/jasoncardinale/Transcriber/releases) page and download the latest executable for your operating system.

2. **Run:**  
   - On Windows: Double-click the downloaded `.exe` file.
   - On Mac: Double-click the `app` file.

3. **Follow the App Instructions:**  
   The app will open in a new window. Follow the on-screen steps to upload audio, generate transcriptions, and view results.

**Troubleshooting:**
- If you see a security warning, you may need to allow the app to run in your system settings.


### Option 2: Run from Source

If you prefer, you can run the app directly from Python source code. See the Development section below.

---

## Development

### 1. Install Requirements

Make sure you have Python 3.12+ installed.

Install dependencies:
```bash
uv sync
```

### 2. Run the App

```bash
uv run python main.py
```

The app GUI will open in a new window.

---

## How to Use

### Step 1: Upload Audio Files

- Go to the **Upload Audio** tab.
- Click "Browse files" and select one or more audio files.
- Wait for the upload to complete.

### Step 2: Generate Transcriptions

- Enter the folder where you want your transcriptions saved (e.g., `~/Documents`).
- Click **Run** to start transcribing.
- When finished, you’ll see a success message.

### Step 3: View and Listen to Transcriptions

- Go to the **View Transcriptions** tab.
- Enter the folder where your transcriptions are saved.
- Expand a file to listen to the audio and read the transcript.
- Click on any transcript segment to jump to that part of the audio.

---

## Output

- Transcriptions are saved as `.vtt` files in your chosen folder.
- The original audio files are also saved in the same folder for easy playback so you may want to delete the audio files from their original location to save space.

---

## Credits

- Built with [Flet](https://github.com/flet-dev/flet) and [OpenAI Whisper](https://github.com/openai/whisper).

---

## License

MIT License
