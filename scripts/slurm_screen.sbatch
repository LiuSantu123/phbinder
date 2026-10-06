#!/bin/bash
#SBATCH --partition=all
#SBATCH --nodelist=localhost
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=phbinder_%j.out
#SBATCH --error=phbinder_%j.err
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Optional site integration. The core screen is CPU-only.
if [[ -n "${PHBINDER_GPU_GUARD:-}" ]]; then source "$PHBINDER_GPU_GUARD"; fi
if command -v gpu-run >/dev/null 2>&1; then gpu-run python -m phbinder.cli run "$@"; else python -m phbinder.cli run "$@"; fi
