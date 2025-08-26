import os
import json

def save_jsonl_line(file_path, data):
    """Appends a single JSON object as a line to file_path."""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_processed_indices(identifier_path):
    """Loads indices already processed from identifier results."""
    indices = set()
    if os.path.exists(identifier_path):
        with open(identifier_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    indices.add(obj["index"])
                except Exception:
                    continue
    return indices

def load_processed_labeler_keys(labeler_path):
    """Loads processed (index, domain) pairs from labeler results."""
    keys = set()
    if os.path.exists(labeler_path):
        with open(labeler_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    keys.add((obj["index"], obj["domain"]))
                except Exception:
                    continue
    return keys
