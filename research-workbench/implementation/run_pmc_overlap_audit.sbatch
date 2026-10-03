#!/bin/bash
#SBATCH --job-name=pmc_overlap_audit
#SBATCH --partition=cpu
#SBATCH --account=yshahar
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
timeout 550s /home/guykalat/.conda/envs/hw1_llm/bin/python pmc_overlap_audit.py
