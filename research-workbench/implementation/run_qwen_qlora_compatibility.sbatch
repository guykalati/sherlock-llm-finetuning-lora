#!/bin/bash
#SBATCH --job-name=qwen_qlora_smoke
#SBATCH --partition=rtx3090
#SBATCH --account=yshahar
#SBATCH --qos=normal
#SBATCH --gres=gpu:rtx_3090:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:08:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
timeout 450s /home/guykalat/.conda/envs/hw1_llm/bin/python qwen_qlora_compatibility.py
