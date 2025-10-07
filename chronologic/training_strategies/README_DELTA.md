# Deploying GPTOSS Model on Delta

## Problem

When deploying the GPTOSS model on Delta using vLLM, the `c_moe` kernel from vLLM is required, but it is not supported by glibc 2.28 (the latest version available on Delta).

## Solution: Using Apptainer

vLLM provides an official Docker image that we can use to build an Apptainer image to solve this issue. The Docker image supports deploying models through an OpenAI-compatible server.

### Step 1: Build Apptainer Image

Pull and build the Docker image from vLLM:

```bash
apptainer build vllm_openai.sif docker://vllm/vllm-openai:latest
```

This will create a .sif file in your current directory. 

### Step 2: Create Deployment Script

Create a SLURM script to deploy the model (e.g., `scripts/gptoss.sh`): 

```bash
#!/bin/bash
#SBATCH --job-name=vllm
#SBATCH --account=bdfx-delta-gpu
#SBATCH --partition=gpuA100x4
#SBATCH --nodes=1
#SBATCH --gpus=2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=28
#SBATCH --time=24:00:00
#SBATCH --output=logs/vllm_gptoss_%j.out
#SBATCH --error=logs/vllm_gptoss_%j.err

# Update these paths for your setup
MODEL_DIR="/work/hdd/bdfx/zqiu1/models/gpt-oss-20b"
IMAGE="/work/hdd/bdfx/zqiu1/models/vllm-openai_latest.sif"

# Clear host GCC environment variables to avoid conflicts
unset CC
unset CXX
unset FC
unset CFLAGS
unset CXXFLAGS
unset LDFLAGS

# vLLM API Server
apptainer exec --nv \
  --bind $MODEL_DIR:$MODEL_DIR \
  --bind /tmp:/tmp \
  $IMAGE \
  python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_DIR \
    --tensor-parallel-size 2 \
    --host 0.0.0.0 \
    --port 9011
```

### Step 3: Install Required Packages and Configure Client Code

#### 3.1 Install Python Dependencies

Install the required Python packages for the client code (you do NOT need to install vLLM - it's already included in the .sif container):

```bash
pip install openai nltk tiktoken --user
```

#### 3.2 update settings in the python script (make_training_data_motive_gptoss.py)

```bash
# configurations
BASE_URL = "http://localhost:9011/v1"  # API endpoint
API_KEY = "EMPTY"  # vLLM doesn't require a real API key
MODEL_NAME = "/work/hdd/bdfx/zqiu1/models/gpt-oss-20b"  # This should match your deployed model

# update the output path
output_file = "/work/hdd/bdfx/zqiu1/response/evaldata-motive-analysis-gptoss.json" 
```

### Step 4: Submit the Job

```bash
sbatch scripts/gptoss.sh
```

### Step 5: Call the Deployed Model

Check the job ID and enter an interactive session:

```bash
# Check your jobs
squeue -u $USER

# Enter an interactive bash session for the job
srun --jobid <jobid> --pty bash

# Call the model through the OpenAI-compatible interface
python make_training_data_motive_gptoss.py analyze ./data/evaldata-chunks.json
```

### Step 6: Cancel the Job After Completion

After inference is complete, cancel the job promptly to avoid resource waste:

```bash
scancel <jobid>
```
