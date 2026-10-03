#!/bin/bash
#SBATCH --job-name=pmc_metadata_5000
#SBATCH --partition=cpu
#SBATCH --account=yshahar
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=02:00:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
timeout 7100s /home/guykalat/.conda/envs/hw1_llm/bin/python pmc_large_metadata.py
