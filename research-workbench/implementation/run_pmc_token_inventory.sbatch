#!/bin/bash
#SBATCH --job-name=pmc_token_inventory
#SBATCH --partition=cpu
#SBATCH --account=yshahar
#SBATCH --qos=normal
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:08:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=2
/home/guykalat/.conda/envs/hw1_llm/bin/python - <<'PY'
import hashlib,json
from pathlib import Path
manifest=json.loads(Path('manifest.json').read_text())
for name,digest in manifest['files_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest
assert not Path('token_inventory.json').exists()
PY
timeout 450s /home/guykalat/.conda/envs/hw1_llm/bin/python pmc_token_inventory.py documents.jsonl review_queue.jsonl /home/guykalat/.cache/huggingface/hub/models--Qwen--Qwen2.5-3B-Instruct/snapshots/aa8e72537993ba99e69dfaafa59ed015b17504d1 token_inventory.json
