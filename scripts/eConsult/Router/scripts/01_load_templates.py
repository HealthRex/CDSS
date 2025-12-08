import os, json
from pathlib import Path
from utils.config import Config

cfg = Config()

templates = {}
for file in os.listdir(cfg.templates_dir):
    if file.endswith(".json"):
        file_path = Path(cfg.templates_dir) / file
        with open(file_path, "r") as f:
            data = json.load(f)

        # Handle files that contain a list instead of a dict
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        if not isinstance(data, dict):
            print(f"⚠️ Skipping {file} (unexpected format)")
            continue

        specialty = data.get("specialty", "")
        condition = data.get("template_name", file.replace(".json", ""))
        text = f"""
Specialty: {specialty}
Condition: {condition}
Required Info: {data.get('required', '')}
Diagnostics: {data.get('diagnostics', '')}
Clinical Pearls: {data.get('clinical_pearls', '')}
"""
        templates[file] = text

print(f"✅ Loaded {len(templates)} templates.")
