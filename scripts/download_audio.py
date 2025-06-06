import os
import re
import time
import csv
from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor, as_completed


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())


def extract_playlist_metadata(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "force_generic_extractor": True,
        "ignoreerrors": True,
        "socket_timeout": 10,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        playlist_title = info.get("title", "unknown_playlist")
        video_entries = info.get("entries", [])

        video_urls = []
        overview = []

        for entry in video_entries:
            if not entry or "url" not in entry:
                continue

            full_url = entry["url"]
            if not full_url.startswith("http"):
                full_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"

            video_urls.append(full_url)
            overview.append(
                {
                    "title": entry.get("title", "Unknown Title"),
                    "url": full_url,
                    "view_count": entry.get("view_count", "N/A"),
                    "duration": entry.get("duration", "N/A"),
                    "upload_date": entry.get("upload_date", "N/A"),
                    "id": entry.get("id", ""),
                }
            )

        return playlist_title, video_urls, overview


def write_conference_overview(metadata_list, output_path):
    metadata_list.sort(key=lambda x: x.get("view_count", 0) or 0, reverse=True)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Title", "Views", "Duration (sec)", "Upload Date", "Video URL"]
        )
        for item in metadata_list:
            writer.writerow(
                [
                    item.get("title", "Unknown Title"),
                    item.get("view_count", "N/A"),
                    item.get("duration", "N/A"),
                    item.get("upload_date", "N/A"),
                    item.get("url", ""),
                ]
            )


def download_audio(video_url, output_dir, user_agent=None):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_dir}/%(title).80s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "user_agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "extractor_args": {
            "youtube": ["player_client=default,-tv,web_safari,web_embedded"]
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            output_filename = os.path.join(output_dir, f"{info['title'][:80]}.wav")
            if (
                os.path.exists(output_filename)
                and os.path.getsize(output_filename) == 0
            ):
                print(f"❌ File is empty: {output_filename}")
                return False
        print(f"✅ Downloaded: {video_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {video_url}: {e}")
        return False


def download_audio_from_playlist(playlist_url, output_dir, max_workers=10, limit=30):
    os.makedirs(output_dir, exist_ok=True)
    failed_downloads = []

    print("🔍 Extracting playlist metadata...")
    playlist_title, video_urls, metadata_list = extract_playlist_metadata(playlist_url)
    print(f"🎵 Playlist title: {playlist_title}")
    print(f"📁 Download folder: {output_dir}")

    # Sort by view count descending
    sorted_metadata = sorted(
        metadata_list,
        key=lambda x: x.get("view_count") or 0,
        reverse=True,
    )

    # Apply limit
    if limit:
        sorted_metadata = sorted_metadata[:limit]

    # Extract top N video URLs
    video_urls = [item["url"] for item in sorted_metadata]

    if not video_urls:
        print("⚠️ No videos found in playlist. Skipping download.")
        return playlist_title, slugify(playlist_title)

    print(
        f"🚀 Downloading top {len(video_urls)} videos with {max_workers} threads...\n"
    )

    # Write overview.csv before downloads
    overview_path = os.path.join(os.path.dirname(output_dir), "overview.csv")
    write_conference_overview(sorted_metadata, overview_path)
    print(f"📄 Saved overview.csv to {overview_path}")

    def wrapped_download(url):
        success = download_audio(url, output_dir)
        return url if not success else None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(wrapped_download, url) for url in video_urls]
        for future in as_completed(futures):
            failed = future.result()
            if failed:
                failed_downloads.append(failed)

    if failed_downloads:
        print(
            f"\n🔁 Retrying {len(failed_downloads)} failed downloads (safer mode)...\n"
        )
        time.sleep(2)
        retry_failed = []
        for url in failed_downloads:
            time.sleep(1)
            ok = download_audio(
                url,
                output_dir,
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/109.0.0.0 Safari/537.36",
            )
            if not ok:
                retry_failed.append(url)

        if retry_failed:
            with open(os.path.join(output_dir, "failed_downloads.txt"), "w") as f:
                for url in retry_failed:
                    f.write(url + "\n")
            print(
                f"\n⚠️ Could not download {len(retry_failed)} videos after retry. Logged to failed_downloads.txt."
            )

    print("\n✅ All downloads attempted.")
    return playlist_title, slugify(playlist_title)
