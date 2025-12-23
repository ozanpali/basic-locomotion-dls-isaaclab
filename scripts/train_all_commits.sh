#!/usr/bin/env bash
# Iterate through a list of commits (inclusive) and run training for each.
# It stashes local changes (if any), checks out each commit in detached HEAD,
# builds a commit-specific run_name, launches the training, and finally
# restores your original branch and stashed changes.

# Safety: don't abort the entire loop on a single training failure
set -u

# --- Config you asked for (defaults, can be overridden via CLI) ---
TASK="Commando-Aliengo-Flat"
NUM_ENVS="8192"
HEADLESS_FLAG="--headless"
LOG_PROJECT_NAME="Commando-Aliengo-Flat"
# default max iterations (can be overridden by --max-iterations)
MAX_ITER="1000"
TRAIN_SCRIPT="scripts/rsl_rl/train_symm.py"
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
  de2d929b5e508199d8b0982344bbc7f113d09cd4
)

# Optional per-commit iteration overrides.
# Set entries like: COMMIT_MAX_ITER[<commit_hash>]=<iterations>
# If not set for a commit, the global MAX_ITER is used.
declare -A COMMIT_MAX_ITER
# Example overrides (uncomment and edit as needed):
# COMMIT_MAX_ITER[7dc08f284420776595a2ba6dfed1f7a1ced39cd3]=1000
# COMMIT_MAX_ITER[169761ffc8c7579f4769b0c9d4206b51413ca1f6]=1000
# COMMIT_MAX_ITER[f0a37ce48a03f3a2bf5fad6e62cf6e4d3aee8755]=1000
# COMMIT_MAX_ITER[4705c65007f11d0b952cefa891b93cbba4148286]=1000
# COMMIT_MAX_ITER[8a46910adb2b3a34878ba6e4524e78f811b10ad6]=1000
# COMMIT_MAX_ITER[d04575f6ad4985cea65e09c1b37a08266d44de0f]=3000
# COMMIT_MAX_ITER[24a430a303d492be1382be9de6fbc4ff818bdabc]=4000
# COMMIT_MAX_ITER[6c0fb2d2a2498b5a6f424e6b2b67b258a821d269]=5000
# COMMIT_MAX_ITER[08c3b0746b426775aafb9bde65896231dfa82f57]=6000

# For this run: first 4 commits use default MAX_ITER (1000),
# last 3 commits use 3000 iterations.
# COMMIT_MAX_ITER[20838669580ca337800c63edddbf5a3d0d871c47]=3000
# COMMIT_MAX_ITER[5c14c83446692bdc2a520dc344b2ae0e10fd5b08]=3000
# COMMIT_MAX_ITER[93437b78f167641598967b86aa92a97d1e971e05]=3000


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
  # Resolve per-commit max iterations if provided, else use global default
  PER_COMMIT_MAX_ITER="${COMMIT_MAX_ITER[${COMMIT}]:-}" || true
  if [[ -z "${PER_COMMIT_MAX_ITER}" ]]; then
    PER_COMMIT_MAX_ITER="${MAX_ITER}"
  fi

  # Build run name: include iterations, envs, short commit id and sanitized commit subject
  RUN_NAME="RPC_${PER_COMMIT_MAX_ITER}Iter_${NUM_ENVS}Env_${SHORT_COMMIT}_${RUN_SUFFIX}"

  info "Commit subject: ${SUBJECT}"
  info "Run name     : ${RUN_NAME}"

  # Launch training; continue on failure
  python "${TRAIN_SCRIPT}" \
    --task="${TASK}" \
    --num_envs="${NUM_ENVS}" \
    ${HEADLESS_FLAG} \
    --log_project_name="${LOG_PROJECT_NAME}" \
    --run_name="${RUN_NAME}" \
    --max_iterations="${PER_COMMIT_MAX_ITER}"

  STATUS=$?
  if [[ ${STATUS} -ne 0 ]]; then
    err "Training failed for ${COMMIT} (exit ${STATUS}). Continuing to next commit."
  else
    info "Training completed for ${COMMIT}."
  fi

done

info "All requested commits processed."
