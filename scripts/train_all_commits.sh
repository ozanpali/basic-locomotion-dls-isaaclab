#!/usr/bin/env bash
# Iterate through a list of commits (inclusive) and run training for each.
# It stashes local changes (if any), checks out each commit in detached HEAD,
# builds a commit-specific run_name, launches the training, and finally
# restores your original branch and stashed changes.

# Safety: don't abort the entire loop on a single training failure
set -u

# --- Config you asked for (defaults, can be overridden via CLI) ---
TASK="Robust-Aliengo-Flat"
NUM_ENVS="8192"
HEADLESS_FLAG="--headless"
LOG_PROJECT_NAME="Robust-Aliengo-Flat"
# default max iterations (can be overridden by --max-iterations)
MAX_ITER="1000"
TRAIN_SCRIPT="scripts/rsl_rl/train.py"
DRY_RUN=false

# Simple CLI parsing to override defaults
print_usage() {
  cat <<EOF
Usage: $0 [--num-envs N] [--max-iterations N] [--no-headless]
  --num-envs N           Number of envs to simulate (overrides NUM_ENVS default)
  --max-iterations N     Max training iterations (overrides MAX_ITER default)
  --no-headless          Run without the headless flag
  --task TASK            Override the TASK to run (default: ${TASK})
  --dry-run              Print commands and run names without executing training
  --help                 Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --num-envs)
      NUM_ENVS="$2"
      shift 2
      ;;
    --task)
      TASK="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift 1
      ;;
    --max-iterations|--max-iter)
      MAX_ITER="$2"
      shift 2
      ;;
    --no-headless)
      HEADLESS_FLAG=""
      shift 1
      ;;
    --help)
      print_usage
      exit 0
      ;;
    *)
      # stop parsing on first non-option to allow for positional use later
      break
      ;;
  esac
done

# Ordered list from first to last commit (as you provided)
COMMITS=(
  #4ceb149c53088b507442d97d752f4f7908e86d4a
  #3ffb03803383b9a411916f7411f8dbcbe04a02da
  #9762cdd8b5ea4531dbb17c9c6b84a5f775866ecd
  befd709e4ff6d1e6aea5dae27da527a489ff546e
)

# --- Helpers ---
err() { echo "[ERROR] $*" >&2; }
info() { echo "[INFO]  $*"; }

# Convert a commit subject into a compact CamelCase suffix for run_name
# Steps:
# 1) Replace symbols with spaces
# 2) Keep only alphanumeric and spaces
# 3) TitleCase each word
# 4) Remove spaces, cap length to 80 chars
subject_to_camelcase() {
  # Convert commit subject into a conventional-commit style suffix:
  # - replace common separators with spaces
  # - remove any characters except alphanumerics, dots, and spaces
  # - convert spaces to underscores, collapse repeats, lowercase
  # - trim leading/trailing underscores and limit length to 80
  local subject="$1"
  local cleaned
  cleaned=$(echo "$subject" \
    | sed 's/[_&+\/: -]/ /g' \
    | sed -E 's/[^[:alnum:]. ]//g' \
    | tr ' ' '_' \
    | tr -s '_' \
    | sed -E 's/^_+|_+$//g' \
    | tr '[:upper:]' '[:lower:]')
  echo "${cleaned:0:80}"
}

# --- Main ---
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "${REPO_ROOT}" ]]; then
  err "Not inside a Git repository. Aborting."
  exit 1
fi
cd "${REPO_ROOT}" || { err "Failed to cd to repo root: ${REPO_ROOT}"; exit 1; }

START_REF=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD")
info "Starting from: ${START_REF} in repo: ${REPO_ROOT}"

STASHED=false
if [[ -n "$(git status --porcelain)" ]]; then
  info "Uncommitted changes detected. Stashing them temporarily."
  git stash push -u -m "auto-stash: train_all_commits $(date -Is)" >/dev/null || true
  STASHED=true
fi

# Ensure we come back to the original state even if interrupted
restore_state() {
  info "Restoring original ref: ${START_REF}"
  git switch "${START_REF}" >/dev/null 2>&1 || git checkout "${START_REF}" >/dev/null 2>&1 || true
  if [[ "${STASHED}" == true ]]; then
    info "Restoring stashed changes (if any)."
    git stash pop >/dev/null 2>&1 || true
  fi
}
trap restore_state EXIT

# Iterate commits
for COMMIT in "${COMMITS[@]}"; do
  info "\n=== Processing commit ${COMMIT} ==="
  # Checkout in detached mode (prefer switch, fallback to checkout)
  if ! git switch --detach "${COMMIT}" >/dev/null 2>&1; then
    if ! git checkout --detach "${COMMIT}" >/dev/null 2>&1; then
      err "Failed to checkout commit ${COMMIT}. Skipping."
      continue
    fi
  fi

  SUBJECT=$(git log -1 --pretty=%s 2>/dev/null || echo "${COMMIT}")
  # Commit subject (raw) and a sanitized suffix for filenames
  SUBJECT=$(git log -1 --pretty=%s 2>/dev/null || echo "${COMMIT}")
  # Short commit id for easier identification
  SHORT_COMMIT=$(git rev-parse --short=8 "${COMMIT}" 2>/dev/null || echo "${COMMIT:0:8}")
  # Fix typo: use SUBJECT when building the suffix
  RUN_SUFFIX=$(subject_to_camelcase "${SUBJECT}")
  # Build run name: include iterations, envs, short commit id and sanitized commit subject
  RUN_NAME="RPC_${MAX_ITER}Iter_${NUM_ENVS}Env_${SHORT_COMMIT}_${RUN_SUFFIX}"

  info "Commit subject: ${SUBJECT}"
  info "Run name     : ${RUN_NAME}"

  # Launch training; continue on failure
  python "${TRAIN_SCRIPT}" \
    --task="${TASK}" \
    --num_envs="${NUM_ENVS}" \
    ${HEADLESS_FLAG} \
    --log_project_name="${LOG_PROJECT_NAME}" \
    --run_name="${RUN_NAME}" \
    --max_iterations="${MAX_ITER}"

  STATUS=$?
  if [[ ${STATUS} -ne 0 ]]; then
    err "Training failed for ${COMMIT} (exit ${STATUS}). Continuing to next commit."
  else
    info "Training completed for ${COMMIT}."
  fi

done

info "All requested commits processed."
