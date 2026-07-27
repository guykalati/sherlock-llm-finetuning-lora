# Running HW1 on the BGU Slurm Cluster from Mac

This guide is for the current project folder:

`/Users/gyklty/Desktop/Semester B/Advanced LLM/HW1-second_try`

You are already on VPN and have cluster access, so the missing pieces are: copy the project to cluster storage, create a Python/Jupyter environment, request the course GPU queue, and open the notebook through Jupyter/VS Code.

## 1. Upload the Project from Mac to the Cluster

From a Mac terminal, replace `<BGU_USER>` with your BGU username:

```bash
rsync -av --progress \
  --exclude ".DS_Store" \
  "/Users/gyklty/Desktop/Semester B/Advanced LLM/HW1-second_try/" \
  <BGU_USER>@slurm.bgu.ac.il:~/HW1-second_try/
```

This copies the notebooks, config, and `Data/` folder to your cluster home directory.

If you later change only code/config, rerun the same command. `rsync` sends only differences.

### If You Uploaded by Dragging Files in VS Code

This is also fine. In your screenshot you are connected to:

```text
guykalat@slurm-login-01
```

That is the cluster login node. You have already uploaded at least:

- `HW1_sherlock_lora_cluster.ipynb`
- `hw1_config.json`
- `Data/`

Before continuing, organize them into one project folder on the cluster. In the VS Code remote terminal, run:

```bash
mkdir -p ~/HW1-second_try
mv ~/HW1_sherlock_lora_cluster.ipynb ~/HW1-second_try/ 2>/dev/null || true
mv ~/hw1_config.json ~/HW1-second_try/ 2>/dev/null || true
mv ~/Data ~/HW1-second_try/ 2>/dev/null || true
cd ~/HW1-second_try
ls -lah
```

You should see:

```text
HW1_sherlock_lora_cluster.ipynb
hw1_config.json
Data/
```

If you prefer leaving the files in your home folder, that can work too, but keeping them in `~/HW1-second_try/` makes paths and outputs easier to manage.

## 2. SSH to the Login Node

```bash
ssh <BGU_USER>@slurm.bgu.ac.il
```

Important: the login/manager node is only for setup, copying files, and submitting jobs. Do not run training there.

## 3. Create the Conda/Jupyter Environment Once

On the cluster login node:

```bash
module load anaconda
conda create -n hw1_llm python=3.11 -y
conda activate hw1_llm
conda install -y jupyterlab ipykernel
python -m ipykernel install --user --name hw1_llm --display-name "hw1_llm"
conda deactivate
```

Do not reinstall Anaconda. The cluster already provides it.

The notebook itself installs the ML packages from `hw1_config.json`. If bitsandbytes complains about CUDA libraries on the cluster, load CUDA before launching Jupyter:

```bash
module avail cuda
module load cuda/13.0
```

If `cuda/13.0` is unavailable, use the closest CUDA 13 module shown by `module avail cuda`.

## 4. Launch Jupyter on the Course GPU Queue

Run this from the login node with conda deactivated:

```bash
conda deactivate
cd ~/HW1-second_try
sjupyter --time 0-5:00:00 --qos course --part rtx3090 --gpu rtx_3090:1 --account cours_ibm26
```

This is the Jupyter version of the course staff allocation, with the RTX 3090 partition/GPU type that worked in practice:

- `--qos course`
- `--part rtx3090`
- `--gpu rtx_3090:1`
- `--account cours_ibm26`

`sjupyter` submits a Slurm job, waits for it to start, and prints a JupyterLab URL. Keep this SSH terminal open. If it closes, the interactive Jupyter job can die.

Open the printed URL in your Mac browser and accept the self-signed certificate warning.

If the cluster's `sjupyter --help` does not show `--account`, omit only that flag and keep the rest:

```bash
sjupyter --time 0-5:00:00 --qos course --part rtx2080 --gpu 1
```

If `--part rtx2080` is rejected, try the older guide spelling:

```bash
sjupyter --time 0-5:00:00 --qos course --part course --gpu 1
```

The course staff line explicitly says `--part rtx2080`, so try that first.

## 5. Open the Notebook

In JupyterLab:

1. Open `~/HW1-second_try/HW1_sherlock_lora_cluster.ipynb`.
2. Select kernel `hw1_llm`.
3. Run the `!nvidia-smi` cell.
4. Continue only if it shows an NVIDIA GPU.
5. Run cells top to bottom.

Outputs will save under:

```bash
~/HW1-second_try/runs/<run_name>/
```

The default run name is controlled by `hw1_config.json`.

### If You Get `FileNotFoundError: Data/pg244.txt`

This means the notebook is not running from the folder that contains `Data/pg244.txt`, or the data files are nested inside another uploaded folder.

In a notebook cell, run:

```python
from pathlib import Path
import os

print("Notebook cwd:", os.getcwd())
print("Home:", Path.home())
print("Project folder exists:", Path("~/HW1-second_try").expanduser().exists())
print("Data in cwd:", Path("Data").exists())
print("Data in project:", Path("~/HW1-second_try/Data").expanduser().exists())
!find ~ -maxdepth 4 -name pg244.txt -print
```

If the final line prints something like `/home/<user>/Data/pg244.txt`, set `data_dir` in `hw1_config.json` to that absolute folder:

```json
"data_dir": "/home/<user>/Data"
```

If it prints `/home/<user>/HW1-second_try/Data/pg244.txt`, set:

```json
"data_dir": "/home/<user>/HW1-second_try/Data"
```

Then rerun the notebook cells starting from **Load Configuration**.

You can also fix the project layout from the remote terminal:

```bash
mkdir -p ~/HW1-second_try
mv ~/HW1_sherlock_lora_cluster.ipynb ~/HW1-second_try/ 2>/dev/null || true
mv ~/hw1_config.json ~/HW1-second_try/ 2>/dev/null || true
mv ~/Data ~/HW1-second_try/ 2>/dev/null || true
find ~/HW1-second_try/Data -maxdepth 3 -name 'pg244.txt' -print
```

## 6. Using VS Code Instead of Browser Jupyter

Recommended simple path:

1. Start `sjupyter` as above.
2. Copy the printed Jupyter URL.
3. In local Mac VS Code, install the `Python` and `Jupyter` extensions.
4. Command Palette: `Jupyter: Specify Jupyter Server for Connections`.
5. Choose existing server and paste the URL.
6. If VS Code rejects the certificate, enable:

```text
Settings -> Jupyter: Allow Unauthorized Remote Connection
```

Alternative Remote-SSH path:

```bash
sinteractive --time 0-5:00:00 --qos course --part rtx2080 --gpu 1 --account cours_ibm26
```

Copy the compute node hostname from the output. In Mac VS Code, use Remote SSH to connect to:

```text
<BGU_USER>@<COMPUTE_NODE_HOSTNAME>
```

Do not connect VS Code to `slurm.bgu.ac.il` for actual training. That is the login node, not the GPU compute node.

## 7. Monitor and Stop Jobs

From another SSH terminal:

```bash
ssh <BGU_USER>@slurm.bgu.ac.il
squeue --me
```

Cancel a job when done:

```bash
scancel <JOB_ID>
```

Check memory/time after a completed job:

```bash
sacct -j <JOB_ID> --format=JobName,MaxRSS,AllocTRES,State,Elapsed,Start,ExitCode
```

## 8. Practical Settings for RTX2080

The RTX2080 has about 11GB VRAM, so start conservatively:

```json
"model_id": "ibm-granite/granite-4.1-3b"
```

```json
"max_seq_length": 512
```

```json
"load_in_4bit": true
```

```json
"save_steps": 25
```

After a successful short run, you can try the requested 8B model again:

```json
"model_id": "ibm-granite/granite-4.1-8b"
```

For 8B on RTX2080, keep `max_seq_length` low, use 4-bit QLoRA, and expect that it may still be tight.

## 9. What Not To Do

- Do not train on the login node.
- Do not leave an idle GPU Jupyter job running.
- Do not request more than one GPU unless IT approved it.
- Do not reinstall Anaconda.
- Do not submit Slurm/Jupyter jobs while your conda env is active; use `conda deactivate` first.
- Do not use the Claude skills folder for this immediate run; it is useful later for queue/status automation, not for first connection.
