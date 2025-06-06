# QueryCon 🎙️→📜→🧠

This tool lets you:

1. **Download** the top N videos from a YouTube playlist (audio only)
2. **Transcribe** the audio using OpenAI Whisper (via HuggingFace)
3. **Summarize** the transcriptions (optional)
4. **Embed** summaries for search and analysis (optional)

All organized neatly into folders per conference or playlist.

---

## 🔧 Installation

### 1. Clone the repository

```
git clone https://github.com/your-org/querycon.git
cd querycon
```

### 2. Install Poetry

Make sure you have Poetry installed:

```
curl -sSL https://install.python-poetry.org | python3 -
```

Ensure it's in your PATH:

```
poetry --version
```

### 3. Create a virtual environment and install dependencies

```
poetry install
```

Poetry will automatically use Python 3.11 if installed. If you don’t have Python 3.11 available, install it with `pyenv` or your system package manager.

---

## ▶️ Usage

### Basic transcription pipeline

To download and transcribe the top 30 videos from a YouTube playlist:

```
poetry run python -m scripts.main "https://www.youtube.com/playlist?list=PL03Lrmd9CiGefrid6QpdDQW-NaxVfmk53" --top 30
```

This will:

- Download audio files into `data/conferences/{playlist_slug}/audio`
- Transcribe each file using `openai/whisper-large`
- Save transcripts as JSON into `data/conferences/{playlist_slug}/transcripts`

### Optional flags

- `--summarize`: Summarize each transcript (requires summarization logic)
- `--embed`: Generate vector embeddings for each summary (requires embedding logic)

Example:

```
poetry run python -m scripts.main "https://www.youtube.com/playlist?list=XYZ" --top 20 --summarize --embed
```

---

## 🗂 Folder Structure

Output is saved under:

```
data/
└── conferences/
    └── {slugified_playlist_name}/
        ├── audio/          # .wav files
        ├── transcripts/    # .json transcripts
        ├── summaries/      # .md or .txt summaries (optional)
        └── embeddings/     # .json or .npy embeddings (optional)
```

---

## 🧪 Development

### Run in dev mode:

```
poetry shell
python -m scripts.main "https://www.youtube.com/playlist?list=XYZ" --top 10
```

### Export a requirements.txt (optional)

```
poetry export -f requirements.txt --without-hashes > requirements.txt
```

---

## 📦 Dependencies

Your `pyproject.toml` includes:

- `yt-dlp`: Downloading YouTube content
- `openai-whisper`: Whisper model (via GitHub)
- `transformers`: HuggingFace pipeline (for Whisper inference)
- `openai`: For optional summarization / embedding
- `torchaudio`, `numpy`, `python-dotenv`

---

## ✅ Requirements

- Python 3.11 (enforced in `pyproject.toml`)
- macOS with MPS support (Whisper uses `device="mps"` for Apple Silicon)
- ffmpeg installed (`brew install ffmpeg` on macOS)

---

## 🧠 Credits

Developed by [Sebastian Olafsson](mailto:sebastian.olafsson@bekk.no) at Bekk.
