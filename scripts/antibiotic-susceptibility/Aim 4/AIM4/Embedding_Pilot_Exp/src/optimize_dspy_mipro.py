"""
Optimization script for the modular 59-classifier pipeline using MIPROv2.

MIPROv2 is more powerful than BootstrapFewShot because it:
1) Generates and optimizes the instruction text (system prompt)
2) Selects the best few-shot demos
3) Uses iterative meta-prompting to improve instructions

For each deduplicated error code we:
1) Build a code-specific binary trainset.
2) Optimize the ModularErrorClassifier with MIPROv2.
3) Save the optimized program to disk (optimized_classifier_<code_key>.json).

NOTE: MIPROv2 is more expensive (more LLM calls) but can produce better results.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List

import dspy
import pandas as pd

# Try importing MIPROv2 - may need dspy>=2.4.0
try:
    from dspy.teleprompt import MIPROv2
    MIPRO_AVAILABLE = True
except ImportError:
    MIPRO_AVAILABLE = False
    logging.warning("MIPROv2 not available. Please upgrade dspy: pip install dspy-ai>=2.4.0")

from data.loader_dspy import load_codebook
from llm.dspy_adapter import HealthRexDSPyLM
from util.modular_error_pipeline import (
    ModularErrorClassifier,
    build_error_code_map,
)
from util.pydantic_modules import ErrorCheckOutput

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5")
ROOT = Path(__file__).resolve().parent.parent
TRAIN_PATH = ROOT / "src/data/input_data/labeled_modular_training_20pos_20neg.csv"


def _safe_dir(name: str) -> str:
    """Sanitize model name to a filesystem-friendly suffix."""
    return re.sub(r"[^\w.-]+", "_", name)


# Separate output per model and optimizer type
OUTPUT_DIR = Path(
    os.getenv("OUTPUT_DIR", str(ROOT / f"optimized_classifiers_mipro_{_safe_dir(MODEL_NAME)}"))
)


def _extract_assessment(obj):
    """Handle both wrapped (obj.assessment) and direct ErrorCheckOutput."""
    return getattr(obj, "assessment", obj)


def validate_binary_classification(example, pred, trace=None):
    """Metric: strict match on error_present."""
    gt = _extract_assessment(example)
    pr = _extract_assessment(pred)
    return getattr(gt, "error_present", None) == getattr(pr, "error_present", None)


def _stringify(val) -> str:
    if val is None:
        return ""
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def _first_present(row, keys):
    for k in keys:
        if k in row and pd.notna(row[k]):
            return row[k]
    return ""


def build_trainset_for_code(code_key: str, df: pd.DataFrame) -> List[dspy.Example]:
    """
    Build a DSPy trainset for a specific code.
    Expects a boolean column `label_<code_key>` in df.
    """
    label_col = f"label_{code_key}"
    rationale_col = f"rationale_{code_key}"
    excerpt_col = f"excerpt_{code_key}"

    if label_col not in df.columns:
        logging.warning("Skipping %s: missing label column %s", code_key, label_col)
        return []

    trainset: List[dspy.Example] = []
    for _, row in df.iterrows():
        label_val = bool(row[label_col])
        rationale = row.get(rationale_col, "Human label provided; rationale not captured.")
        if label_val:
            excerpt = row.get(
                excerpt_col,
                "Human label provided as positive; excerpt not captured in dataset.",
            )
        else:
            excerpt = "Not Applicable"

        expected = ErrorCheckOutput(
            error_present=label_val,
            rationale=_stringify(rationale),
            verbatim_excerpt=_stringify(excerpt),
        )

        ex = (
            dspy.Example(
                patient_message=_stringify(_first_present(row, ["patient_message", "Patient Message"])),
                llm_response=_stringify(_first_present(row, ["llm_response", "Suggested Response from LLM"])),
                patient_info=_stringify(_first_present(row, ["patient_info", "Data"])),
                clinical_notes=_stringify(_first_present(row, ["clinical_notes", "Last Note"])),
                previous_messages=_stringify(_first_present(row, ["previous_messages", "Previous Messages"])),
                retrieved_pairs=_stringify(_first_present(row, ["retrieved_pairs"])),
                assessment=expected,
            ).with_inputs(
                "patient_message",
                "llm_response",
                "patient_info",
                "clinical_notes",
                "previous_messages",
                "retrieved_pairs",
            )
        )
        trainset.append(ex)
    return trainset


def optimize_all_mipro(error_code_map: Dict[str, str], train_df: pd.DataFrame):
    """Compile an optimized classifier per error code using MIPROv2."""
    if not MIPRO_AVAILABLE:
        raise ImportError("MIPROv2 is not available. Please upgrade dspy: pip install dspy-ai>=2.4.0")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lm = HealthRexDSPyLM(model_name=MODEL_NAME)
    dspy.settings.configure(lm=lm)

    # Optional: filter codes via env CODE_FILTER (comma-separated)
    code_filter_env = os.getenv("CODE_FILTER", "").strip()
    code_filter = {c.strip() for c in code_filter_env.split(",") if c.strip()} if code_filter_env else set()
    
    for code_key, definition in error_code_map.items():
        if code_filter and code_key not in code_filter:
            continue
            
        ckpt_path = OUTPUT_DIR / f"optimized_classifier_{code_key}.json"
        if ckpt_path.exists():
            logging.info("Checkpoint exists for %s, skipping: %s", code_key, ckpt_path)
            continue

        logging.info("Optimizing classifier for %s with MIPROv2", code_key)
        trainset = build_trainset_for_code(code_key, train_df)
        
        if not trainset:
            logging.warning("No training data for %s. Skipping optimization.", code_key)
            continue
        
        # Check for positive examples
        positive_count = sum(1 for ex in trainset if ex.assessment.error_present)
        if positive_count == 0:
            logging.warning("No positive examples for %s. Skipping.", code_key)
            continue

        student = ModularErrorClassifier(error_code_str=definition)
        
        # MIPROv2 Configuration
        # - auto: Set to None to allow manual configuration of trials/candidates
        optimizer = MIPROv2(
            metric=validate_binary_classification,
            auto=None,                  # Disable auto-configuration to use manual settings
            num_candidates=3,           # Generate 3 instruction candidates per iteration
            init_temperature=1.0,       # Temperature for initial instruction generation
            num_threads=1,              # LM adapter is synchronous
            max_bootstrapped_demos=2,   # Max demos to bootstrap
            max_labeled_demos=2,        # Max labeled demos to include
        )

        try:
            # MIPROv2 needs both trainset and a validation set
            # If we have limited data, we can use trainset for both (not ideal but works)
            # For better results, split trainset into train/val
            
            # Simple split: use 80% for training, 20% for validation
            split_idx = max(1, int(len(trainset) * 0.8))
            train_split = trainset[:split_idx]
            val_split = trainset[split_idx:] if split_idx < len(trainset) else trainset[:2]
            
            logging.info("Training with %d examples, validating with %d examples", 
                        len(train_split), len(val_split))
            
            optimized_program = optimizer.compile(
                student,
                trainset=train_split,
                valset=val_split,
                num_trials=5,           # Number of optimization iterations
                minibatch_size=min(5, len(val_split)),  # Minibatch for faster eval
                minibatch_full_eval_steps=2,  # Full eval every N steps
                requires_permission_to_run=False,  # Don't ask for permission
            )
            
            optimized_program.save(str(ckpt_path))
            logging.info("Saved MIPROv2 optimized classifier to %s", ckpt_path)
            
        except Exception as e:
            logging.exception("Failed to optimize/save for %s: %s", code_key, e)
            # Continue to next code instead of crashing
            continue


def main():
    logging.basicConfig(level=logging.INFO)
    
    if not MIPRO_AVAILABLE:
        logging.error("MIPROv2 is not available. Please run: pip install dspy-ai>=2.4.0")
        return
    
    logging.info("Loading codebook and training data...")
    codebook = load_codebook()
    error_code_map = build_error_code_map(codebook, include_examples=False)

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(f"Training CSV not found at {TRAIN_PATH}")
    
    train_df = pd.read_csv(TRAIN_PATH)
    logging.info("Loaded training data with shape %s from %s", train_df.shape, TRAIN_PATH)

    logging.info("="*60)
    logging.info("Starting MIPROv2 Optimization")
    logging.info("="*60)
    logging.info("Model: %s", MODEL_NAME)
    logging.info("Output: %s", OUTPUT_DIR)
    logging.info("Codes to optimize: %d", len(error_code_map))
    logging.info("="*60)
    
    optimize_all_mipro(error_code_map, train_df)
    
    logging.info("MIPROv2 optimization complete!")


if __name__ == "__main__":
    main()

