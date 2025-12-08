import os
import json
import time
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils.config import Config
import numpy as np

# === Initialize configuration ===
cfg = Config()

# === Load from cache instead of processing templates ===
print("📚 Loading from cache...")

# Load specialty-condition mapping from cache
with open(cfg.results_dir / "specialty_condition_mapping.json", "r") as f:
    specialty_conditions = json.load(f)

# Load cache content (pre-formatted templates text)
with open(cfg.results_dir / "cache_content.txt", "r") as f:
    cache_content = f.read()
    
# Extract templates text from cache content
# The cache file has sections separated by "=== TEMPLATES ===" and "=== SPECIALTY MAPPINGS ==="
templates_section = cache_content.split("=== SPECIALTY MAPPINGS ===")[0]
templates_text = templates_section.replace("=== TEMPLATES ===\n", "").strip()


TEMPLATES_TEXT = templates_text

# Create specialty-condition mapping text (already formatted in cache)
specialty_mapping_text = ""
for specialty, conditions in specialty_conditions.items():
    specialty_mapping_text += f"\n{specialty}: {', '.join(conditions[:10])}..."

# Load cache metadata for reference
with open(cfg.results_dir / "cache_metadata.json", "r") as f:
    cache_metadata = json.load(f)
    print(f"✅ Loaded cache (hash: {cache_metadata['content_hash']}, templates: {cache_metadata['template_count']})")


# === Few-shot examples ===
FEW_SHOT_EXAMPLES = """
Example 1:
Clinical Question: "68 yo male with history of asthma and pulmonary embolism reporting persistent SOB with exertion and dry cough. Current asthma medication: Huntersville HFA 230-21 and albuterol/nebulizer. Symptoms started at the end of 01/08/2024. Was seen in ED and given 5 day prednisone course. Most recent office treatment included 15 day 40mg steroid taper and Zpak which he completed at the end of January. D Dimer was WNL on 02/12/2024 as well. Pt also increased Adviar to TID temporarily. Initially saw some improvement (no longer productive cough), but SOB and dry cough have persisted. He is pending an echocardiogram given history of PE and then will be able to schedule in person pulm consult. I am not sure if I should try him on a different inhaler at this point or consider further chest imaging given his history. Are there any recommendations on what I can try while he awaits pulm consult?"

Response:
{
    "specialties": ["Pulmonology", "Internal Medicine", "Cardiology"],
    "conditions": ["pulmonology_asthma", "pulmonology_chronic_cough", "pulmonology_abnormal_imaging", "pulmonology_copd", "pulmonology_other"]
}

Example 2:
Clinical Question: "32 yo female, noted to have endometrial cells on recent PAP, otherwise PAP was normal (NIL, neg HPV). LMP 07/20/2023, last 4-5 days - menarche: 14 yo - G:0 - negative STD testing 08/02/2023 - last PAP est 12 year ago, recalls was normal - no hx of HPV vaccine - message from patient after appt: 'Just one caveat that might be worth mentioning my LMP did start 7/1 but it was an abnormal one, due to effects of a one time contraceptive pill, my regular periods start around the 20's of each month ( and I'm really regular) , the Pap test was on the 18 and my regular period came the 21st, so maybe that's why endometrial cells were present.'"

Response:
{
    "specialties": ["Gynecology", "Family Medicine", "Internal Medicine"],
    "conditions": ["gynecology_abnormal_pap_smear", "gynecology_contraceptive_issues", "gynecology_other", "gynecology_vaginitis", "gynecology_abnormal_pap_smear"]
}
"""


########updated prompt for vertigo and tinnitus handling########

SYSTEM_PROMPT = f"""You are a clinical reasoning assistant.
Given a patient's eConsult question, determine:
(1) The top 3 most appropriate specialties (ranked by relevance).
(2) The top 5 most relevant template conditions (ranked by relevance).

CRITICAL CONSTRAINT: All 5 conditions MUST be from the TOP specialty you choose (the first specialty in your list). Do NOT mix conditions from different specialties.

Note: For the following conditions, please consider the associated specialties:
- **Vertigo**: Both ENT-Otolaryngology and Neurology are valid specialties.
- **Tinnitus**: Both ENT-Otolaryngology and Neurology are valid specialties.
- **Sinusitis**: ENT-Otolaryngology is the primary specialty, but Internal Medicine may also be relevant.

Available specialty-condition mappings:
{specialty_mapping_text}

Here are examples of correct responses:
{FEW_SHOT_EXAMPLES}

Return your answer strictly in JSON format:
{{
    "specialties": ["specialty1", "specialty2", "specialty3"],
    "conditions": ["condition1", "condition2", "condition3", "condition4", "condition5"]
}}

Remember: All 5 conditions must belong to your top-ranked specialty (specialty1).
Make sure to provide exactly 3 specialties and 5 conditions from the top specialty only.
"""


# === Alternative: Two-step approach ===
def ask_gpt_two_step(question, retries=3, delay=5):
    """Two-step approach: First get specialty, then get conditions from that specialty"""

    # Step 1: Get specialty
    specialty_prompt = f"""You are a clinical reasoning assistant.
Given this patient's eConsult question, determine the top 3 most appropriate specialties (ranked by relevance).

Clinical Question: {question}

Return your answer strictly in JSON format:
{{"specialties": ["specialty1", "specialty2", "specialty3"]}}
"""

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": cfg.securegpt_api_key,
    }

    # Get specialties first
    payload = {
        "model": cfg.llm_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a clinical reasoning assistant. Respond only in JSON format.",
            },
            {"role": "user", "content": specialty_prompt},
        ],
    }

    try:
        response = requests.post(cfg.securegpt_url, headers=headers, json=payload)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]["content"]
        specialty_result = json.loads(message)
        top_specialty = specialty_result.get("specialties", [""])[0]
    except Exception as e:
        print(f"⚠️ Error getting specialty: {e}")
        return {"specialties": ["", "", ""], "conditions": ["", "", "", "", ""]}

    # Step 2: Get conditions from the top specialty only
    if top_specialty and top_specialty in specialty_conditions:
        available_conditions = specialty_conditions[top_specialty]
        conditions_text = (
            f"Available conditions for {top_specialty}: {', '.join(available_conditions)}"
        )
    else:
        conditions_text = TEMPLATES_TEXT

    condition_prompt = f"""You are a clinical reasoning assistant.
Given this patient's eConsult question and the top specialty "{top_specialty}", 
choose the top 5 most relevant conditions from this specialty only.

Clinical Question: {question}

{conditions_text}

Return your answer strictly in JSON format:
{{"conditions": ["condition1", "condition2", "condition3", "condition4", "condition5"]}}

All conditions must be from the {top_specialty} specialty only.
"""

    payload = {
        "model": cfg.llm_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a clinical reasoning assistant. Respond only in JSON format.",
            },
            {"role": "user", "content": condition_prompt},
        ],
    }

    try:
        response = requests.post(cfg.securegpt_url, headers=headers, json=payload)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]["content"]
        condition_result = json.loads(message)

        specialties = specialty_result.get("specialties", [])[:3]
        conditions = condition_result.get("conditions", [])[:5]

        # Pad with empty strings if needed
        while len(specialties) < 3:
            specialties.append("")
        while len(conditions) < 5:
            conditions.append("")

        return {"specialties": specialties, "conditions": conditions}

    except Exception as e:
        print(f"⚠️ Error getting conditions: {e}")
        return {"specialties": ["", "", ""], "conditions": ["", "", "", "", ""]}


# === Original single-step approach with improved prompt ===
def ask_gpt(question, retries=3, delay=5):
    user_prompt = (
        f"Clinical Question:\n{question}\n\nAvailable Templates:\n{TEMPLATES_TEXT}"
    )

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": cfg.securegpt_api_key,
    }

    payload = {
        "model": cfg.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(cfg.securegpt_url, headers=headers, json=payload)
            response.raise_for_status()
            message = response.json()["choices"][0]["message"]["content"]
            result = json.loads(message)

            specialties = result.get("specialties", [])[:3]
            conditions = result.get("conditions", [])[:5]

            # Validate that conditions are from the top specialty
            top_specialty = specialties[0] if specialties else ""
            if top_specialty and top_specialty in specialty_conditions:
                valid_conditions = []
                available_conditions = [
                    c.lower() for c in specialty_conditions[top_specialty]
                ]

                for condition in conditions:
                    # Check if condition belongs to the top specialty
                    condition_lower = condition.lower()
                    specialty_prefix = top_specialty.lower().replace(" ", "_")

                    if condition_lower.startswith(specialty_prefix) or any(
                        cond in condition_lower for cond in available_conditions
                    ):
                        valid_conditions.append(condition)

                # If we don't have enough valid conditions, fill with available ones
                if len(valid_conditions) < 5 and top_specialty in specialty_conditions:
                    remaining_needed = 5 - len(valid_conditions)
                    available = specialty_conditions[top_specialty]
                    for i in range(min(remaining_needed, len(available))):
                        if available[i] not in valid_conditions:
                            valid_conditions.append(available[i])

                conditions = valid_conditions

            # Pad with empty strings if needed
            while len(specialties) < 3:
                specialties.append("")
            while len(conditions) < 5:
                conditions.append("")

            return {"specialties": specialties, "conditions": conditions}

        except requests.exceptions.HTTPError as e:
            print(f"⚠️ HTTP {response.status_code} on attempt {attempt}: {e}")
            if response.status_code in [429, 500, 503]:
                time.sleep(delay)
                continue
            break
        except Exception as e:
            print(f"⚠️ Error on attempt {attempt}: {e}")
            time.sleep(delay)

    return {"specialties": ["", "", ""], "conditions": ["", "", "", "", ""]}


# === Load and split data into 5 chunks ===
df = pd.read_csv(cfg.data_dir / "all_questions.csv")
print(f"📊 Total questions to process: {len(df)}")

# Split dataframe into 5 roughly equal chunks
chunk_size = len(df) // 5
chunks = []

for i in range(5):
    start_idx = i * chunk_size
    if i == 4:  # Last chunk gets any remaining rows
        end_idx = len(df)
    else:
        end_idx = (i + 1) * chunk_size

    chunk = df.iloc[start_idx:end_idx].copy()
    chunks.append(chunk)
    print(f"Chunk {i+1}: {len(chunk)} questions (rows {start_idx} to {end_idx-1})")

# === Choose which chunks to process ===
print("\n📋 Choose which chunks to process:")
print("1. Process all chunks (1-5)")
print("2. Process specific chunk(s)")
chunk_choice = input("Enter choice (1 or 2): ").strip()

if chunk_choice == "2":
    print("\nOptions for specific chunks:")
    print("- Single chunk: Enter number (e.g., '3')")
    print("- Multiple chunks: Enter comma-separated (e.g., '1,3,5')")
    print("- Range: Enter range (e.g., '2-4')")

    chunk_input = input("Enter chunk selection: ").strip()

    # Parse chunk selection
    chunks_to_process = []

    if "-" in chunk_input:  # Range like "2-4"
        start_chunk, end_chunk = map(int, chunk_input.split("-"))
        chunks_to_process = list(
            range(start_chunk - 1, end_chunk)
        )  # Convert to 0-indexed
    elif "," in chunk_input:  # Multiple like "1,3,5"
        chunks_to_process = [
            int(x.strip()) - 1 for x in chunk_input.split(",")
        ]  # Convert to 0-indexed
    else:  # Single chunk like "3"
        chunks_to_process = [int(chunk_input) - 1]  # Convert to 0-indexed

    # Validate chunk numbers
    chunks_to_process = [i for i in chunks_to_process if 0 <= i < 5]

    if not chunks_to_process:
        print("❌ Invalid chunk selection. Processing all chunks.")
        chunks_to_process = list(range(5))

    print(f"📌 Selected chunks: {[i+1 for i in chunks_to_process]}")
else:
    chunks_to_process = list(range(5))  # Process all chunks

# === Process selected chunks ===
print("\nChoose approach:")
print("1. Single-step with improved prompt and validation")
print("2. Two-step approach (specialty first, then conditions)")
approach = input("Enter choice (1 or 2): ").strip()

all_predictions = []  # Store all results from selected chunks

for chunk_idx in chunks_to_process:
    chunk_df = chunks[chunk_idx]
    print(f"\n🚀 Processing Chunk {chunk_idx + 1}/5 ({len(chunk_df)} questions)...")
    chunk_preds = []

    # Process each question in the current chunk
    for i, row in tqdm(
        chunk_df.iterrows(), total=len(chunk_df), desc=f"Chunk {chunk_idx + 1}"
    ):
        q = row["clean_question"] if "clean_question" in row else row["question"]

        if approach == "2":
            result = ask_gpt_two_step(q)
        else:
            result = ask_gpt(q)

        pred_dict = {
            "original_index": i,  # Keep track of original row index
            "chunk_number": chunk_idx + 1,
            "question": q,
            "gt_specialty": row.get("dept_specialty", ""),
            "gt_condition": row.get("condition_label", ""),
        }

        # Add top 3 specialty predictions
        for j, spec in enumerate(result.get("specialties", [])):
            pred_dict[f"pred_specialty_{j+1}"] = spec

        # Add top 5 condition predictions
        for j, cond in enumerate(result.get("conditions", [])):
            pred_dict[f"pred_condition_{j+1}"] = cond

        chunk_preds.append(pred_dict)

    # Save intermediate results for this chunk
    chunk_df_results = pd.DataFrame(chunk_preds)
    chunk_filename = f"chunk_{chunk_idx + 1}_predictions.csv"
    chunk_df_results.to_csv(cfg.results_dir / chunk_filename, index=False)
    print(f"💾 Saved chunk {chunk_idx + 1} → {cfg.results_dir}/{chunk_filename}")

    # Add chunk results to overall results
    all_predictions.extend(chunk_preds)

    # Optional: Add a small delay between chunks (if processing multiple)
    if len(chunks_to_process) > 1 and chunk_idx != chunks_to_process[-1]:
        print("⏳ Waiting 2 seconds before next chunk...")
        time.sleep(2)

# === Handle results based on what was processed ===
if len(chunks_to_process) == 1:
    # Single chunk - save with specific name
    single_chunk_num = chunks_to_process[0] + 1
    results_df = pd.DataFrame(all_predictions)
    filename = f"chunk_{single_chunk_num}_only_predictions.csv"
    results_df.to_csv(cfg.results_dir / filename, index=False)
    print(f"✅ Saved chunk {single_chunk_num} results → {cfg.results_dir}/{filename}")

else:
    # Multiple chunks - concatenate and save
    print(f"\n📊 Concatenating results from selected chunks...")
    print(f"Total predictions collected: {len(all_predictions)}")

    final_df = pd.DataFrame(all_predictions)

    # Sort by original index to maintain original order
    final_df = final_df.sort_values("original_index").reset_index(drop=True)

    # Create filename based on processed chunks
    chunk_numbers = [str(i + 1) for i in chunks_to_process]
    if len(chunks_to_process) == 5:
        chunk_suffix = "all_chunks"
    else:
        chunk_suffix = f"chunks_{'_'.join(chunk_numbers)}"

    final_filename = f"gpt_predictions_{chunk_suffix}.csv"
    final_df.to_csv(cfg.results_dir / final_filename, index=False)
    print(f"✅ Saved concatenated results → {cfg.results_dir}/{final_filename}")

    results_df = final_df

# === Calculate performance ===
print(f"\n📊 Calculating Performance on processed data ({len(results_df)} questions)...")


def calculate_topk_accuracy(df, gt_col, pred_cols):
    """Calculate accuracy at different k values"""
    accuracies = {}

    for k in range(1, len(pred_cols) + 1):
        hits = 0
        total = 0

        for _, row in df.iterrows():
            gt = str(row[gt_col]).lower().strip()
            if not gt:
                continue

            match_found = False
            for j in range(k):
                pred = str(row[pred_cols[j]]).lower().strip()
                if gt in pred or pred in gt:
                    match_found = True
                    break

            if match_found:
                hits += 1
            total += 1

        accuracies[f"@{k}"] = hits / total if total > 0 else 0

    return accuracies


# Calculate performance
specialty_cols = [f"pred_specialty_{i}" for i in range(1, 4)]
specialty_acc = calculate_topk_accuracy(results_df, "gt_specialty", specialty_cols)

condition_cols = [f"pred_condition_{i}" for i in range(1, 6)]
condition_acc = calculate_topk_accuracy(results_df, "gt_condition", condition_cols)

# Print results
print(f"\n🎯 Specialty Performance (Chunks {[i+1 for i in chunks_to_process]}):")
print(f"  Top-1 Accuracy: {specialty_acc['@1']:.3f}")
print(f"  Top-3 Accuracy: {specialty_acc['@3']:.3f}")

print(f"\n🎯 Condition Performance (Chunks {[i+1 for i in chunks_to_process]}):")
print(f"  Top-1 Accuracy: {condition_acc['@1']:.3f}")
print(f"  Top-5 Accuracy: {condition_acc['@5']:.3f}")

# Save results summary
results_summary = {
    "chunks_processed": [i + 1 for i in chunks_to_process],
    "total_questions_processed": len(results_df),
    "specialty_top1": specialty_acc["@1"],
    "specialty_top3": specialty_acc["@3"],
    "condition_top1": condition_acc["@1"],
    "condition_top5": condition_acc["@5"],
}

if len(chunks_to_process) == 1:
    results_file = f"chunk_{chunks_to_process[0]+1}_results.json"
else:
    results_file = (
        f"chunks_{'_'.join([str(i+1) for i in chunks_to_process])}_results.json"
    )

with open(cfg.results_dir / results_file, "w") as f:
    json.dump(results_summary, f, indent=2)

print(f"\n✅ Saved performance results → {cfg.results_dir}/{results_file}")
