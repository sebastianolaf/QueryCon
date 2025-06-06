import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def summarize_all_transcripts(transcript_dir, summary_dir):
    os.makedirs(summary_dir, exist_ok=True)

    for filename in os.listdir(transcript_dir):
        if filename.endswith(".json"):
            video_id = filename.split(".")[0]
            summary_path = os.path.join(summary_dir, f"{video_id}.json")
            if os.path.exists(summary_path):
                print(f"✅ Already summarized: {video_id}")
                continue

            with open(os.path.join(transcript_dir, filename)) as f:
                transcript_data = json.load(f)
                transcript_text = transcript_data.get("text", "")

            print(f"🧠 Summarizing: {video_id}")
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant summarizing conference talks into structured JSON format.",
                },
                {"role": "user", "content": transcript_text},
            ]
            response = client.chat.completions.create(model="gpt-4o", messages=messages)
            summary = response.choices[0].message.content

            with open(summary_path, "w") as f:
                f.write(summary)
