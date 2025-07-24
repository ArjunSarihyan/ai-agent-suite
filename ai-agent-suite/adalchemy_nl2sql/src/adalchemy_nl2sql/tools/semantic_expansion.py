import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
INDEX_PATH = os.path.join(BASE_DIR, "knowledge", "taxonomy_faiss.index")
META_PATH = os.path.join(BASE_DIR, "knowledge", "taxonomy_metadata.pkl")
DEBUG_FILE = os.path.join(BASE_DIR, "knowledge", "debug.md")

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

index = faiss.read_index(INDEX_PATH)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_top_k_similar_phrases(keywords: list[str], top_k: int = 3) -> dict[str, list[dict]]:
    results = {}
    for keyword in keywords:
        embedding = model.encode([keyword], convert_to_numpy=True)
        D, I = index.search(embedding, top_k)
        matches = []
        for idx in I[0]:
            entry = metadata[idx]
            matches.append({
                "text": entry["text"],
                "source_table": entry["source_table"],
                "unique_id": entry["unique_id"]
            })
        results[keyword] = matches
    return results

def log_debug(content: str):
    with open(DEBUG_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")
