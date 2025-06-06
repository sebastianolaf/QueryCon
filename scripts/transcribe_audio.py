import os
import json
from transformers import pipeline


def transcribe_all_audio(audio_dir, transcript_dir):
    print("🧠 Loading fast Whisper model (large-v3-turbo, MPS-compatible)...")
    asr = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3-turbo",
        generate_kwargs={"task": "transcribe"},
        device="mps",  # Use "cuda" if on GPU, "cpu" if no GPU
    )

    os.makedirs(transcript_dir, exist_ok=True)

    for filename in os.listdir(audio_dir):
        if filename.endswith(".wav"):
            video_id = filename.rsplit(".", 1)[0]
            audio_path = os.path.join(audio_dir, filename)
            transcript_path = os.path.join(transcript_dir, f"{video_id}.json")

            if os.path.exists(transcript_path):
                print(f"✅ Already transcribed: {filename}")
                continue

            print(f"🗣️ Transcribing: {filename}")
            result = asr(audio_path, return_timestamps=True)
            with open(transcript_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ All audio files transcribed.")
