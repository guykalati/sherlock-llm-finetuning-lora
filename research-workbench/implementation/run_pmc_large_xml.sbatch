#!/bin/bash
#SBATCH --job-name=pmc_xml_expand
#SBATCH --partition=cpu
#SBATCH --account=yshahar
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=01:00:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
timeout 3550s /home/guykalat/.conda/envs/hw1_llm/bin/python pmc_large_xml.py
