#!/usr/bin/env python3
"""
Unified Pipeline v2: Prompt Optimization → Inference

Supports multiple LLM models with model-specific output directories.

This script runs the full modular error classification pipeline:
1. Optimize classifiers for all 59 error codes (if not already done)
2. Run inference on input data using the optimized classifiers

Each model gets its own output directory structure:
    output_<model>/
    ├── checkpoints/       # Optimized classifier checkpoints
    ├── logs/              # Prompt logs, optimization logs
    └── results/           # Inference results (.jsonl)

Usage:
    python src/run_pipeline_v2.py --model gpt-5 --input data.csv --output results.jsonl
    python src/run_pipeline_v2.py --model claude-3.7-sonnet --input data.csv --output results.jsonl
    python src/run_pipeline_v2.py --list-models
    python src/run_pipeline_v2.py --test-model gpt-5
"""
import argparse
import asyncio
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Load .env before other imports
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------- Configuration ----------
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"

# Add src to path for imports
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from llm.model_registry import MODEL_CONFIGS, get_model_config, list_available_models


# ---------- Directory Helpers ----------

def get_model_output_dir(model_alias: str) -> Path:
    """Get the output directory for a model (contains checkpoints, logs, results)."""
    safe_name = model_alias.replace("/", "_").replace(" ", "_").replace(".", "_")
    return ROOT / f"output_{safe_name}"


def get_checkpoint_dir(model_alias: str) -> Path:
    """Get the checkpoint directory for a model."""
    return get_model_output_dir(model_alias) / "checkpoints"


def get_logs_dir(model_alias: str) -> Path:
    """Get the logs directory for a model."""
    return get_model_output_dir(model_alias) / "logs"


def get_results_dir(model_alias: str) -> Path:
    """Get the results directory for a model."""
    return get_model_output_dir(model_alias) / "results"


def setup_model_dirs(model_alias: str) -> None:
    """Create all directories for a model."""
    get_checkpoint_dir(model_alias).mkdir(parents=True, exist_ok=True)
    get_logs_dir(model_alias).mkdir(parents=True, exist_ok=True)
    get_results_dir(model_alias).mkdir(parents=True, exist_ok=True)


# ---------- Model Testing ----------

def test_model(model_alias: str) -> bool:
    """Test a model's configuration by running the test script."""
    logging.info("Testing model: %s", model_alias)
    
    result = subprocess.run(
        [sys.executable, str(SRC_DIR / "llm" / "test_models.py"), model_alias, "--raw"],
        cwd=str(ROOT),
        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
    )
    return result.returncode == 0


# ---------- Optimization ----------

def run_optimization(model_alias: str, shard_size: int = 4, max_parallel: int = 4, use_mipro: bool = False):
    """
    Run prompt optimization for all 59 error codes.
    Uses the shard runner for parallel optimization.
    """
    config = get_model_config(model_alias)
    checkpoint_dir = get_checkpoint_dir(model_alias)
    logs_dir = get_logs_dir(model_alias)
    
    setup_model_dirs(model_alias)
    
    logging.info("="*60)
    logging.info("STEP 1: Prompt Optimization")
    logging.info("="*60)
    logging.info("Model: %s (%s)", model_alias, config.display_name)
    logging.info("Optimizer: %s", "MIPROv2" if use_mipro else "BootstrapFewShot")
    logging.info("Checkpoint dir: %s", checkpoint_dir)
    logging.info("Logs dir: %s", logs_dir)
    
    # Check how many checkpoints already exist
    existing = list(checkpoint_dir.glob("optimized_classifier_*.json"))
    logging.info("Existing checkpoints: %d", len(existing))
    
    if len(existing) >= 30:  # Assuming ~30 codes have positive training data
        logging.info("Sufficient checkpoints exist. Skipping optimization.")
        logging.info("(Use --force-optimize to re-run anyway)")
        return checkpoint_dir
    
    # Run the shard optimizer
    logging.info("Running optimization with %d shards, %d parallel...", shard_size, max_parallel)
    
    env = os.environ.copy()
    env["MODEL_NAME"] = model_alias
    env["SHARD_SIZE"] = str(shard_size)
    env["MAX_PAR"] = str(max_parallel)
    env["PYTHONPATH"] = str(SRC_DIR)
    env["OUTPUT_DIR"] = str(checkpoint_dir)
    env["LOGS_DIR"] = str(logs_dir)
    
    # Select optimizer script
    optimizer_script = "src/optimize_dspy_mipro.py" if use_mipro else "src/optimize_dspy.py"
    env["OPTIMIZER_SCRIPT"] = optimizer_script
    
    shard_script = ROOT / "run_optimize_all_shards.sh"
    
    if shard_script.exists():
        result = subprocess.run(
            ["bash", str(shard_script)],
            cwd=str(ROOT),
            env=env,
        )
        if result.returncode != 0:
            logging.warning("Shard optimization returned non-zero exit code: %d", result.returncode)
        
        # Checkpoints are now saved directly to checkpoint_dir (no merge needed)
        saved_checkpoints = list(checkpoint_dir.glob("optimized_classifier_*.json"))
        logging.info("Optimization complete. %d checkpoints saved to %s", len(saved_checkpoints), checkpoint_dir)
    else:
        logging.warning("Shard script not found: %s", shard_script)
        logging.info("Falling back to single-process optimization...")
        
        result = subprocess.run(
            [sys.executable, str(ROOT / optimizer_script)],
            cwd=str(ROOT),
            env=env,
        )
    
    return checkpoint_dir


def merge_shard_outputs(model_alias: str):
    """Merge checkpoints from shard directories into main checkpoint dir."""
    checkpoint_dir = get_checkpoint_dir(model_alias)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Find shard directories (they use MODEL_NAME which is the alias)
    safe_name = model_alias.replace("/", "_").replace(" ", "_").replace(".", "_")
    patterns = [
        f"optimized_classifiers_{model_alias}_shard*",
        f"optimized_classifiers_{safe_name}_shard*",
    ]
    
    shard_dirs = []
    for pattern in patterns:
        shard_dirs.extend(ROOT.glob(pattern))
    
    if not shard_dirs:
        logging.info("No shard directories found to merge.")
        return
    
    copied = 0
    for shard_dir in shard_dirs:
        for ckpt_file in shard_dir.glob("optimized_classifier_*.json"):
            dest = checkpoint_dir / ckpt_file.name
            if not dest.exists():
                shutil.copy2(ckpt_file, dest)
                copied += 1
    
    logging.info("Merged %d checkpoints from %d shard directories", copied, len(shard_dirs))


# ---------- Inference ----------

async def run_inference(
    model_alias: str,
    input_path: str,
    output_path: str,
    batch_size: int = 2,
    delay: float = 2.0,
    max_classifiers: int = 5,
    with_reference: bool = True,
    verbose: bool = False,
):
    """Run inference using the optimized classifiers."""
    # IMPORTANT: Set model name BEFORE importing batch_runner_modular
    # because it reads MODEL_NAME at module load time
    os.environ["MODEL_NAME"] = model_alias
    
    from batch_runner_modular import (
        load_classifiers,
        batch_pipeline_runner,
        init_lm,
    )
    import pandas as pd
    
    config = get_model_config(model_alias)
    checkpoint_dir = get_checkpoint_dir(model_alias)
    results_dir = get_results_dir(model_alias)
    logs_dir = get_logs_dir(model_alias)
    
    setup_model_dirs(model_alias)
    
    # If output_path is just a filename, put it in results_dir
    output_file = Path(output_path)
    if not output_file.is_absolute() and output_file.parent == Path("."):
        output_path = str(results_dir / output_file.name)
    
    # Set up logging to file (always log INFO to file)
    log_file = logs_dir / "pipeline.log"
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logging.getLogger().addHandler(file_handler)
    
    # Set up prompt logging to model's logs dir
    if verbose:
        os.environ["DSPY_PROMPT_LOG"] = str(logs_dir / "prompts.log")
    
    logging.info("="*60)
    logging.info("STEP 2: Inference")
    logging.info("="*60)
    logging.info("Model: %s (%s)", model_alias, config.display_name)
    logging.info("Checkpoint dir: %s", checkpoint_dir)
    logging.info("Results dir: %s", results_dir)
    logging.info("Input: %s", input_path)
    logging.info("Output: %s", output_path)
    
    # Initialize LM with the correct model
    init_lm(model_alias)
    
    # Load classifiers
    classifiers, _ = load_classifiers(checkpoint_dir=checkpoint_dir)
    
    # Load input data
    if input_path.endswith(".csv"):
        sample_data = pd.read_csv(input_path)
    else:
        sample_data = pd.read_json(input_path, lines=True)
    logging.info("Loaded %d rows from input", len(sample_data))
    
    # Run inference
    results = await batch_pipeline_runner(
        sample_data=sample_data,
        classifiers=classifiers,
        output_path=output_path,
        with_reference=with_reference,
        batch_size=batch_size,
        delay_between_batches=delay,
        max_concurrent_classifiers=max_classifiers,
    )
    
    # Summary
    total_errors = sum(r["num_errors"] for r in results)
    logging.info("="*60)
    logging.info("COMPLETE")
    logging.info("="*60)
    logging.info("Processed: %d cases", len(results))
    logging.info("Total errors detected: %d", total_errors)
    logging.info("Results saved to: %s", output_path)
    
    return results


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Unified Pipeline v2: Prompt Optimization → Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with gpt-5
  python src/run_pipeline_v2.py --model gpt-5 --input data.csv --output results.jsonl

  # Skip optimization (use existing checkpoints)
  python src/run_pipeline_v2.py --model gpt-5 --input data.csv --output results.jsonl --skip-optimize

  # Run with Claude model
  python src/run_pipeline_v2.py --model claude-3.7-sonnet --input data.csv --output results.jsonl

  # Test a model's configuration
  python src/run_pipeline_v2.py --test-model gpt-5

  # List available models
  python src/run_pipeline_v2.py --list-models
        """
    )
    
    # Model selection
    parser.add_argument("--model", "-m", choices=list(MODEL_CONFIGS.keys()), default="gpt-5",
                        help="Model to use (default: gpt-5)")
    parser.add_argument("--list-models", action="store_true", help="List available models and exit")
    parser.add_argument("--test-model", metavar="MODEL", help="Test a model's configuration and exit")
    
    # Input/Output
    parser.add_argument("--input", "-i", help="Input CSV or JSONL path")
    parser.add_argument("--output", "-o", help="Output JSONL filename (saved to model's results dir)")
    
    # Optimization options
    parser.add_argument("--skip-optimize", action="store_true", help="Skip optimization step")
    parser.add_argument("--force-optimize", action="store_true", help="Force re-run optimization")
    parser.add_argument("--optimize-only", action="store_true", help="Only run optimization, skip inference")
    parser.add_argument("--shard-size", type=int, default=4, help="Codes per optimization shard")
    parser.add_argument("--max-parallel", type=int, default=4, help="Max parallel shards")
    parser.add_argument("--mipro", action="store_true", help="Use MIPROv2 optimizer instead of BootstrapFewShot")
    
    # Inference options
    parser.add_argument("--batch-size", type=int, default=2, help="Cases per inference batch")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between batches (seconds)")
    parser.add_argument("--max-classifiers", type=int, default=5, help="Max concurrent classifiers per case")
    parser.add_argument("--no-reference", action="store_true", help="Disable retrieved pairs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging (saves prompts to logs dir)")
    
    args = parser.parse_args()
    
    # List models
    if args.list_models:
        list_available_models()
        return
    
    # Test model
    if args.test_model:
        success = test_model(args.test_model)
        sys.exit(0 if success else 1)
    
    # Validate required args for pipeline
    if not args.optimize_only and (not args.input or not args.output):
        parser.error("--input and --output are required (unless --list-models, --test-model, or --optimize-only)")
    
    # Step 1: Optimization
    if not args.skip_optimize:
        if args.force_optimize:
            checkpoint_dir = get_checkpoint_dir(args.model)
            if checkpoint_dir.exists():
                logging.info("Clearing existing checkpoints for forced re-optimization...")
                shutil.rmtree(checkpoint_dir)
        
        run_optimization(
            model_alias=args.model,
            shard_size=args.shard_size,
            max_parallel=args.max_parallel,
            use_mipro=args.mipro,
        )
    else:
        logging.info("Skipping optimization (--skip-optimize)")
    
    # Step 2: Inference
    if not args.optimize_only:
        asyncio.run(run_inference(
            model_alias=args.model,
            input_path=args.input,
            output_path=args.output,
            batch_size=args.batch_size,
            delay=args.delay,
            max_classifiers=args.max_classifiers,
            with_reference=not args.no_reference,
            verbose=args.verbose,
        ))


if __name__ == "__main__":
    main()

