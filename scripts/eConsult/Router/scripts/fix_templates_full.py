import json
from pathlib import Path

folder = Path("data/templates")

for file in folder.glob("*.json"):
    try:
        with open(file, "r") as f:
            content = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read {file.name}: {e}")
        continue

    # If already structured, skip
    if isinstance(content, dict) and "specialty" in content:
        print(f"⏩ Already structured: {file.name}")
        continue

    # Extract specialty + condition from file name
    stem = file.stem  # e.g. cardiology_chest_pain
    parts = stem.split("_", 1)

    if len(parts) < 2:
        print(f"⚠️ Cannot parse: {file.name}")
        continue

    specialty_raw, condition_raw = parts
    specialty = specialty_raw.replace("-", " ").title()
    condition = condition_raw.replace("-", "_")

    # Wrap the original list into a structured template object
    structured = {
        "specialty": specialty,
        "condition": condition,
        "template_name": stem,
        "sections": content if isinstance(content, list) else [content]
    }

    # Save back to disk
    with open(file, "w") as f:
        json.dump(structured, f, indent=2)

    print(f"✔️ Fixed {file.name}: specialty={specialty}, condition={condition}")

print("\n🎉 DONE — all templates processed!")
