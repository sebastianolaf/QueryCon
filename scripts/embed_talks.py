import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def embed_all_summaries(summary_dir, embedding_dir):
    os.makedirs(embedding_dir, exist_ok=True)

    for filename in os.listdir(summary_dir):
        if filename.endswith(".json"):
            video_id = filename.split(".")[0]
            embedding_path = os.path.join(embedding_dir, f"{video_id}.npy")
            if os.path.exists(embedding_path):
                print(f"✅ Already embedded: {video_id}")
                continue

            with open(os.path.join(summary_dir, filename)) as f:
                text = f.read().replace("\n", " ")
                embedding = client.embeddings.create(
                    input=[text], model="text-embedding-3-small"
                )
                np.save(embedding_path, embedding.data[0].embedding)
