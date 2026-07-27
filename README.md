# Sherlock LLM Fine-Tuning, LoRA & Hyperparameter Alignment Framework

![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)
![PEFT](https://img.shields.io/badge/PEFT-LoRA-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An end-to-end framework for Supervised Fine-Tuning (SFT) and Parameter-Efficient Fine-Tuning (LoRA) of open-source Large Language Models (Qwen, Llama). Includes automated hyperparameter ablation grid execution across GPU clusters to systematically analyze rank selection ($r$), scaling ($\alpha$), learning rate schedules, and target modules.

---

## 📌 Features

- **Supervised Fine-Tuning (SFT)**: Formats unstructured conversational data into multi-turn chat templates (`jsonl`) and executes full-parameter / adapter tuning.
- **Parameter-Efficient Fine-Tuning (PEFT / LoRA)**: Injects low-rank trainable matrices into self-attention projection layers (`q_proj`, `v_proj`, `k_proj`, `o_proj`), dramatically reducing VRAM usage.
- **Automated Grid Search & Ablation**: Runs distributed hyperparameter grids to benchmark loss convergence, evaluation perplexity, and inference generation quality.
- **Sherlock Cluster Integration**: Configured for SLURM / GPU cluster execution with multi-GPU environment handling.

---

## 🛠 Tech Stack

| Category | Tools & Libraries |
|---|---|
| **Core Frameworks** | PyTorch, HuggingFace `transformers`, `peft`, `datasets`, `accelerate` |
| **Models** | Qwen-2.5 / Qwen-7B, Llama-3 / Llama-3-8B |
| **Optimization** | BitsAndBytes (4-bit/8-bit quantization), AdamW, Cosine Annealing |
| **Cluster & Scripting** | Python, SLURM, JSON Config Profiles, Jupyter |

---

## 📊 Pipeline Overview

```
Raw Conversation Data ➔ Chat Template Formatting ➔ Quantized Base LLM
                                                           │
                                             ┌─────────────┴─────────────┐
                                             ▼                           ▼
                                      Full SFT Tuning             LoRA Adapters (r=8..64)
                                             │                           │
                                             └─────────────┬─────────────┘
                                                           ▼
                                               Hyperparameter Grid Ablation
                                                           │
                                                           ▼
                                                Benchmark Evaluation & ROUGE
```

---

## 💻 Usage

### 1. Requirements Installation
```bash
pip install torch transformers peft datasets accelerate bitsandbytes
```

### 2. Run LoRA Fine-Tuning
```bash
# Run LoRA training notebook / script
python scripts/train_lora.py --config hw1_config.json
```

### 3. Run SFT Pipeline
```bash
# Execute SFT training on formatted dataset
python scripts/train_sft.py --config hw2_config.json
```

---

## 👤 Author

**Guy Kalati**  
M.Sc. Candidate, Ben-Gurion University of the Negev  
GitHub: [guykalati](https://github.com/guykalati) | Email: [guykalati@gmail.com](mailto:guykalati@gmail.com)
