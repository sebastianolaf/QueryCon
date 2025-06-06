import os
import re
import csv


def sanitize_conference_id(url: str) -> str:
    if "list=" in url:
        return url.split("list=")[-1].split("&")[0]
    return re.sub(r"\W+", "_", url.strip())


def make_conference_dirs(conference_id: str):
    base_path = f"data/conferences/{conference_id}"
    for subfolder in ["audio", "transcripts", "summaries", "embeddings"]:
        os.makedirs(os.path.join(base_path, subfolder), exist_ok=True)
    return {
        "base": base_path,
        "audio": os.path.join(base_path, "audio"),
        "transcripts": os.path.join(base_path, "transcripts"),
        "summaries": os.path.join(base_path, "summaries"),
        "embeddings": os.path.join(base_path, "embeddings"),
    }


def write_conference_overview(metadata_list, output_path):
    """
    Writes a CSV with video title and view count for each video.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Title", "Views"])

        for item in metadata_list:
            title = item.get("title", "Unknown Title")
            views = item.get("view_count", "N/A")
            writer.writerow([title, views])
