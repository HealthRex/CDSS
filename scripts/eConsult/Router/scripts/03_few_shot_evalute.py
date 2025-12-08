import pandas as pd
from utils.config import Config
from difflib import SequenceMatcher
import re
import os
from pathlib import Path

cfg = Config()


# ==============================
# 🔹 File Merging Functions
# ==============================
def merge_prediction_files(
    results_dir,
    pattern="chunk_*_predictions.csv",
    output_filename="gpt_predictions_merged.csv",
):
    results_path = Path(results_dir)
    csv_files = list(results_path.glob(pattern))

    if not csv_files:
        print(f"❌ No files found matching pattern '{pattern}' in {results_dir}")
        return None

    print(f"📁 Found {len(csv_files)} files to merge:")
    for f in csv_files:
        print(f"   - {f.name}")

    merged_data = []
    for file_path in csv_files:
        try:
            df_temp = pd.read_csv(file_path)
            print(f"   ✅ Loaded {len(df_temp)} rows from {file_path.name}")
            merged_data.append(df_temp)
        except Exception as e:
            print(f"   ❌ Error loading {file_path.name}: {e}")

    if not merged_data:
        print("❌ No valid data found to merge")
        return None

    merged_df = pd.concat(merged_data, ignore_index=True)

    if "question" in merged_df.columns:
        initial_count = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=["question"], keep="first")
        final_count = len(merged_df)
        if initial_count != final_count:
            print(f"🧹 Removed {initial_count - final_count} duplicate questions")

    output_path = results_path / output_filename
    merged_df.to_csv(output_path, index=False)
    print(f"💾 Merged file saved: {output_path} ({len(merged_df)} total rows)")
    return output_path


# ==============================
# 🔹 Helper Functions
# ==============================
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s_,;]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def remove_specialty_prefix(text):
    if not text:
        return text
    prefixes = [
        "cardiology_",
        "gastroenterology_",
        "urology_",
        "endocrinology_",
        "pulmonology_",
        "oncology_",
        "neurology_",
        "psychiatry_",
        "orthopedics_",
        "dermatology_",
        "ophthalmology_",
        "ent_",
        "gynecology_",
        "hematology_",
        "nephrology_",
        "radiology_",
        "pathology_",
        "anesthesiology_",
        "surgery_",
        "internal_medicine_",
    ]
    text_clean = text.lower().strip()
    for prefix in prefixes:
        if text_clean.startswith(prefix):
            text_clean = text_clean[len(prefix) :]
            break
    return text_clean


def split_multiple_items(text):
    if not text:
        return []
    items = re.split(r"[,;]|\band\b", text)
    items = [item.strip() for item in items if item.strip()]
    return items


def flexible_match(gt_text, pred_text, threshold=0.80):
    if not gt_text or not pred_text:
        return False

    gt_clean = clean_text(gt_text)
    pred_clean = clean_text(pred_text)
    gt_normalized = gt_clean.replace("_", " ").strip()
    pred_normalized = pred_clean.replace("_", " ").strip()

    if gt_normalized == pred_normalized:
        return True
    if gt_normalized in pred_normalized or pred_normalized in gt_normalized:
        return True

    pred_no_prefix = remove_specialty_prefix(pred_clean)
    pred_no_prefix_normalized = pred_no_prefix.replace("_", " ").strip()

    if gt_normalized == pred_no_prefix_normalized:
        return True
    if (
        gt_normalized in pred_no_prefix_normalized
        or pred_no_prefix_normalized in gt_normalized
    ):
        return True

    if (
        SequenceMatcher(None, gt_normalized, pred_no_prefix_normalized).ratio()
        >= threshold
    ):
        return True

    pred_parts = split_multiple_items(pred_normalized)
    for part in pred_parts:
        part_no_prefix = remove_specialty_prefix(part).replace("_", " ").strip()
        if gt_normalized in part_no_prefix or part_no_prefix in gt_normalized:
            return True
        if gt_normalized == part_no_prefix:
            return True
        if SequenceMatcher(None, gt_normalized, part_no_prefix).ratio() >= threshold:
            return True

    gt_words = set(gt_normalized.split())
    pred_words = set(pred_no_prefix_normalized.split())
    if len(gt_words) > 0:
        common_words = gt_words.intersection(pred_words)
        if len(common_words) / len(gt_words) >= 0.8:
            return True

    medical_synonyms = {
        "ekg": ["ecg", "electrocardiogram"],
        "lfts": ["liver function tests", "liver enzymes"],
        "uti": ["urinary tract infection"],
        "pft": ["pulmonary function test", "pulmonary function tests"],
        "pfts": ["pulmonary function test", "pulmonary function tests"],
        "abnormal": ["elevated", "decreased", "irregular", "unusual"],
        "chest pain": ["chest discomfort", "thoracic pain"],
        "shortness of breath": ["dyspnea", "sob", "breathing difficulty"],
    }
    for key, synonyms in medical_synonyms.items():
        all_terms = [key] + synonyms
        if any(term in gt_normalized for term in all_terms) and any(
            term in pred_no_prefix_normalized for term in all_terms
        ):
            return True

    return False


def is_too_short(text, min_words=80):
    if pd.isna(text):
        return True
    text = str(text).strip()
    return len(re.findall(r"\b\w+\b", text)) < min_words


def looks_like_lab_or_bp(text):
    if pd.isna(text):
        return False
    text = text.lower()
    num_tokens = len(
        re.findall(r"\d+|\bmg\b|\bbp\b|\bcreatinine\b|\bvalue\b|\bref range\b", text)
    )
    total_tokens = len(re.findall(r"\b\w+\b", text))
    if total_tokens == 0:
        return False
    numeric_ratio = num_tokens / total_tokens
    return numeric_ratio > 0.4 or bool(
        re.search(r"\bcreatinine\b|\bbp\b|\bvalue\b|\bref range\b", text)
    )


def get_top_k_predictions(row, field_prefix, k=5):
    predictions = []
    if field_prefix == "pred_specialty" and "pred_specialties_top5" in row:
        pred_text = str(row["pred_specialties_top5"])
        if not pd.isna(row["pred_specialties_top5"]):
            predictions = [p.strip() for p in pred_text.split(",") if p.strip()]
    elif field_prefix == "pred_condition" and "pred_conditions_top5" in row:
        pred_text = str(row["pred_conditions_top5"])
        if not pd.isna(row["pred_conditions_top5"]):
            predictions = [p.strip() for p in pred_text.split(",") if p.strip()]
    else:
        for i in range(1, k + 1):
            col_name = f"{field_prefix}_{i}"
            if col_name in row and not pd.isna(row[col_name]):
                predictions.append(str(row[col_name]))
        if not predictions and field_prefix in row and not pd.isna(row[field_prefix]):
            pred_text = str(row[field_prefix])
            predictions = [
                p.strip() for p in re.split(r"[,;]|\band\b", pred_text) if p.strip()
            ]
    return predictions[:k]


def evaluate_top_k(gt_value, predictions, k):
    if not gt_value or not predictions:
        return False
    for pred in predictions[:k]:
        if flexible_match(gt_value, pred):
            return True
    return False


# ==============================
# 🔹 Shared-Condition Cross-Specialty Map
# ==============================
shared_condition_specialties = {
    "vertigo": ["neurology", "ent", "otolaryngology"],
    "tinnitus": ["ent", "otolaryngology", "neurology"],
    "sinusitis": ["ent", "otolaryngology", "internal_medicine"],
    "hearing_loss": ["ent", "neurology"],
    "dizziness": ["neurology", "ent", "otolaryngology"],
}


def matches_shared_condition(gt_cond, gt_spec, pred_specs):
    """Return True if condition belongs to shared map and predicted specialty overlaps."""
    condition_text = clean_text(gt_cond)
    gt_spec_clean = clean_text(gt_spec)
    for cond_key, allowed_specs in shared_condition_specialties.items():
        if cond_key in condition_text:
            if any(
                any(spec.lower().startswith(allowed) for allowed in allowed_specs)
                for spec in pred_specs
            ):
                return True
    return False


# ==============================
# 🔹 Load and Merge Data
# ==============================
merge_files = True
single_file = "gpt_predictions_constrained_topk.csv"

if merge_files:
    print("🔄 Attempting to merge prediction files...")
    merged_file_path = merge_prediction_files(
        results_dir=cfg.results_dir,
        pattern="chunk_*_predictions.csv",
        output_filename="gpt_predictions_merged.csv",
    )
    if merged_file_path and merged_file_path.exists():
        df = pd.read_csv(merged_file_path)
        print(f"📊 Loaded merged dataset: {len(df)} rows")
    else:
        print(f"⚠️  Merging failed, falling back to single file: {single_file}")
        df = pd.read_csv(cfg.results_dir / single_file)
else:
    df = pd.read_csv(cfg.results_dir / single_file)
    print(f"📊 Loaded single file dataset: {len(df)} rows")

initial_count = len(df)
df["is_short"] = df["question"].apply(is_too_short)
df["is_lab_like"] = df["question"].apply(looks_like_lab_or_bp)
df_filtered = df[~(df["is_short"] | df["is_lab_like"])].reset_index(drop=True)
filtered_count = len(df_filtered)
print(
    f"✅ Filtered dataset from {initial_count} → {filtered_count} (removed {initial_count - filtered_count}) questions"
)
print(f"\n📋 Available columns: {list(df_filtered.columns)}")

# ==============================
# 🔹 Evaluate Recall with Top-K Metrics
# ==============================
top_k_values = [1, 3, 5]
specialty_hits = {k: 0 for k in top_k_values}
condition_hits = {k: 0 for k in top_k_values}
mismatch_data = []

for idx, r in df_filtered.iterrows():
    gt_spec = str(r["gt_specialty"]) if not pd.isna(r["gt_specialty"]) else ""
    gt_cond = str(r["gt_condition"]) if not pd.isna(r["gt_condition"]) else ""
    pred_specs = get_top_k_predictions(r, "pred_specialty", k=5)
    pred_conds = get_top_k_predictions(r, "pred_condition", k=5)

    spec_matches = {}
    cond_matches = {}

    for k in top_k_values:
        spec_match = evaluate_top_k(gt_spec, pred_specs, k)
        cond_match = evaluate_top_k(gt_cond, pred_conds, k)

        # ✅ Add shared-condition overlap handling
        if not spec_match and matches_shared_condition(gt_cond, gt_spec, pred_specs):
            spec_match = True

        spec_matches[k] = spec_match
        cond_matches[k] = cond_match

        if spec_match:
            specialty_hits[k] += 1
        if cond_match:
            condition_hits[k] += 1

    if not (spec_matches[5] and cond_matches[5]):
        mismatch_data.append(
            {
                "index": idx,
                "question": (
                    r["question"][:100] + "..."
                    if len(str(r["question"])) > 100
                    else r["question"]
                ),
                "gt_specialty": gt_spec,
                "pred_specialties_top5": ", ".join(pred_specs[:5]),
                "specialty_match_top5": spec_matches[5],
                "gt_condition": gt_cond,
                "pred_conditions_top5": ", ".join(pred_conds[:5]),
                "condition_match_top5": cond_matches[5],
            }
        )

total = len(df_filtered)

# ==============================
# 🔹 Metrics Summary
# ==============================
print("\n📊 Top-K Recall Metrics:")
print("=" * 60)
print(f"{'Metric':<20} {'Top-1':<15} {'Top-3':<15} {'Top-5':<15}")
print("-" * 60)

spec_recall_str = ""
for k in top_k_values:
    recall = (specialty_hits[k] / total) * 100
    spec_recall_str += f"{recall:.1f}% ({specialty_hits[k]}/{total})\t"
print(f"{'Specialty Recall':<20} {spec_recall_str}")

cond_recall_str = ""
for k in top_k_values:
    recall = (condition_hits[k] / total) * 100
    cond_recall_str += f"{recall:.1f}% ({condition_hits[k]}/{total})\t"
print(f"{'Condition Recall':<20} {cond_recall_str}")

print("\n📊 Joint Accuracy (Both Correct):")
print("-" * 60)
joint_str = ""
for k in top_k_values:
    both_correct = sum(
        1
        for idx, r in df_filtered.iterrows()
        if (
            evaluate_top_k(
                str(r["gt_specialty"]) if not pd.isna(r["gt_specialty"]) else "",
                get_top_k_predictions(r, "pred_specialty", k=k),
                k,
            )
            or matches_shared_condition(
                str(r["gt_condition"]),
                str(r["gt_specialty"]),
                get_top_k_predictions(r, "pred_specialty", k=k),
            )
        )
        and evaluate_top_k(
            str(r["gt_condition"]) if not pd.isna(r["gt_condition"]) else "",
            get_top_k_predictions(r, "pred_condition", k=k),
            k,
        )
    )
    joint_acc = (both_correct / total) * 100
    joint_str += f"{joint_acc:.1f}% ({both_correct}/{total})\t"
print(f"{'Joint Accuracy':<20} {joint_str}")

# ==============================
# 🔹 Save Mismatches
# ==============================
if mismatch_data:
    mismatch_df = pd.DataFrame(mismatch_data)
    mismatch_file = cfg.results_dir / "evaluation_mismatches_merged_topk.csv"
    mismatch_df.to_csv(mismatch_file, index=False)
    print(f"\n💾 Saved {len(mismatch_data)} mismatches to: {mismatch_file}")
    print(f"\n📋 Sample mismatches (first 3 shown):")
    for i, row in enumerate(mismatch_data[:3]):
        print(f"\n--- Mismatch {i+1} ---")
        print(f"Question: {row['question']}")
        print(
            f"GT Specialty: {row['gt_specialty']} | Predicted: {row['pred_specialties_top5']}"
        )
        print(
            f"GT Condition: {row['gt_condition']} | Predicted: {row['pred_conditions_top5']}"
        )

print("\n✅ Evaluation complete!")
