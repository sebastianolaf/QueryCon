import sys
import os
import shutil
import time

from scripts.utils import make_conference_dirs
from scripts.download_audio import download_audio_from_playlist
from scripts.transcribe_audio import transcribe_all_audio
from scripts.summarize_talks import summarize_all_transcripts
from scripts.embed_talks import embed_all_summaries


def run_pipeline(
    conference_url,
    do_summarize=False,
    do_embed=False,
    max_download_attempts=3,
    top_n=30,
):
    print(f"\n🎯 Starting pipeline for: {conference_url}")

    audio_root = "data/conferences"
    temp_audio_dir = f"{audio_root}/temp_audio"
    os.makedirs(temp_audio_dir, exist_ok=True)

    playlist_title = None
    conference_id = None

    for attempt in range(1, max_download_attempts + 1):
        print(
            f"\n📥 Step 1: Downloading top {top_n} videos (attempt {attempt}/{max_download_attempts})..."
        )

        try:
            playlist_title, conference_id = download_audio_from_playlist(
                playlist_url=conference_url,
                output_dir=temp_audio_dir,
                max_workers=10,
                limit=top_n,
            )
            break
        except Exception as e:
            print(f"❌ Download failed: {e}")
            if attempt < max_download_attempts:
                print("🔁 Retrying in 5 seconds...\n")
                time.sleep(5)
            else:
                print("❌ Max retries reached. Exiting.")
                sys.exit(1)

    print(f"\n🧾 Playlist title: {playlist_title}")
    print(f"📁 Conference folder: {conference_id}")

    # Step 2: Prepare final folders
    print("\n📁 Step 2: Preparing folders...")
    paths = make_conference_dirs(conference_id)
    print(f"✅ Folder structure ready under: data/conferences/{conference_id}")

    # Step 3: Move new audio files
    print("\n📂 Step 3: Moving new audio files to conference folder...")
    moved = 0
    for file in os.listdir(temp_audio_dir):
        dst_path = os.path.join(paths["audio"], file)
        if not os.path.exists(dst_path):
            shutil.move(os.path.join(temp_audio_dir, file), dst_path)
            print(f"📦 Moved: {file}")
            moved += 1
        else:
            print(f"⏭️ Skipped (already exists): {file}")

    shutil.rmtree(temp_audio_dir)
    print(f"✅ Moved {moved} new files.\n")

    # Step 4: Transcribe
    print("🗣️ Step 4: Transcribing audio files...")
    transcribe_all_audio(paths["audio"], paths["transcripts"])
    print("✅ Transcription complete.\n")

    # Step 5: Summarize
    if do_summarize:
        print("🧠 Step 5: Summarizing transcripts...")
        summarize_all_transcripts(paths["transcripts"], paths["summaries"])
        print("✅ Summarization complete.\n")
    else:
        print("⚠️ Skipping summarization (use --summarize to enable)\n")

    # Step 6: Embed
    if do_embed:
        print("🧬 Step 6: Embedding summaries...")
        embed_all_summaries(paths["summaries"], paths["embeddings"])
        print("✅ Embedding complete.\n")
    else:
        print("⚠️ Skipping embedding (use --embed to enable)\n")

    print(
        f"\n✅ Pipeline finished successfully for: {playlist_title} ({conference_id})\n"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: poetry run python scripts/main.py <playlist_url> [--summarize] [--embed] [--top N]"
        )
        sys.exit(1)

    playlist_url = sys.argv[1]
    do_summarize = "--summarize" in sys.argv
    do_embed = "--embed" in sys.argv

    # Optional: --top N
    try:
        top_n = (
            int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 30
        )
    except (IndexError, ValueError):
        print("⚠️ Invalid value for --top. Using default: 30")
        top_n = 30

    run_pipeline(
        conference_url=playlist_url,
        do_summarize=do_summarize,
        do_embed=do_embed,
        top_n=top_n,
    )
