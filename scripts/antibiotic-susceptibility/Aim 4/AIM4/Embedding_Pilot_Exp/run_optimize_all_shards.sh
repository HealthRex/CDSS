#!/usr/bin/env bash
set -euo pipefail

# Auto-shard all code_keys from the codebook and run one process per shard.
# Env overrides:
#   MODEL_NAME   - target model (default: gpt-5)
#   SHARD_SIZE   - number of codes per shard (default: 4)
#   MAX_PAR      - max concurrent shards (default: 4)
#   TRAIN_PATH   - optional override of training CSV (handled in optimize_dspy)

MODEL_NAME="${MODEL_NAME:-gpt-5}"
SHARD_SIZE="${SHARD_SIZE:-4}"
MAX_PAR="${MAX_PAR:-4}"  # max shards to run concurrently
OPTIMIZER_SCRIPT="${OPTIMIZER_SCRIPT:-src/optimize_dspy.py}" # script to run (default: standard few-shot)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH:-}"

# Base output directory - use OUTPUT_DIR env var if set, otherwise default
BASE_OUTPUT_DIR="${OUTPUT_DIR:-${SCRIPT_DIR}/optimized_classifiers_${MODEL_NAME}}"

# Logs directory - use LOGS_DIR env var if set, otherwise default to BASE_OUTPUT_DIR
LOGS_DIR="${LOGS_DIR:-${BASE_OUTPUT_DIR}}"

# Create logs directory if it doesn't exist
mkdir -p "${LOGS_DIR}"

# Build shard list (comma-separated code_keys per shard) via Python
SHARDS_TEXT="$(python - <<'PY'
import os
from data.loader_dspy import load_codebook
from util.modular_error_pipeline import build_error_code_map

model_name = os.getenv("MODEL_NAME", "gpt-5")
shard_size = int(os.getenv("SHARD_SIZE", "4"))

codebook = load_codebook()
code_map = build_error_code_map(codebook)
codes = sorted(code_map.keys())

if not codes:
    raise SystemExit("No codes found in codebook.")

shards = [codes[i:i+shard_size] for i in range(0, len(codes), shard_size)]
for shard in shards:
    print(",".join(shard))
PY
)"

SHARDS=()
while IFS= read -r line; do
  [ -n "$line" ] && SHARDS+=("$line")
done <<< "${SHARDS_TEXT}"

if [ ${#SHARDS[@]} -eq 0 ]; then
  echo "No shards generated. Check codebook and PYTHONPATH."
  exit 1
fi

echo "Starting ${#SHARDS[@]} shards with MODEL_NAME=${MODEL_NAME}, SHARD_SIZE=${SHARD_SIZE}, MAX_PAR=${MAX_PAR}"
echo "Base output directory: ${BASE_OUTPUT_DIR}"

# Create logs directory
mkdir -p "${BASE_OUTPUT_DIR}"

idx=1
running=0
for shard_codes in "${SHARDS[@]}"; do
  # Save directly to BASE_OUTPUT_DIR (no shard subdirs needed - each code gets its own file)
  echo "Shard ${idx}: codes=$(echo "${shard_codes}" | tr ',' ' ')"
  CODE_FILTER="${shard_codes}" OUTPUT_DIR="${BASE_OUTPUT_DIR}" MODEL_NAME="${MODEL_NAME}" \
  DSPY_VERBOSE="${DSPY_VERBOSE:-}" DSPY_PROMPT_LOG="${DSPY_PROMPT_LOG:-}" \
    python "${SCRIPT_DIR}/${OPTIMIZER_SCRIPT}" > "${LOGS_DIR}/shard${idx}.log" 2>&1 &
  running=$((running+1))
  idx=$((idx+1))

  # throttle concurrency (portable: wait for all when at limit)
  if [ "$running" -ge "$MAX_PAR" ]; then
    wait
    running=0
  fi
done

echo "Waiting for remaining shards to complete..."
wait

echo "All shards finished."
echo "Logs: ${LOGS_DIR}/shard*.log"
echo "Checkpoints: ${BASE_OUTPUT_DIR}/optimized_classifier_*.json"

# Usage: MODEL_NAME=gpt-5 SHARD_SIZE=4 MAX_PAR=4 ./run_optimize_all_shards.sh
# Or with custom output: OUTPUT_DIR=/path/to/checkpoints MODEL_NAME=claude-3.7-sonnet ./run_optimize_all_shards.sh