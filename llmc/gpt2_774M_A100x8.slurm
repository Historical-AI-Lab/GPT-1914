#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8  # One task per GPU
#SBATCH --cpus-per-task=4    # 4 CPU cores per GPU task
#SBATCH --partition=gpuA100x8
#SBATCH --account=bdfx-delta-gpu
#SBATCH --time=48:00:00
#SBATCH --job-name=774M-b8v2
#SBATCH --error=774M-b8v2%j.err
#SBATCH --output=774M-b8v2%j.out
#SBATCH --gpus-per-node=8
#SBATCH --gpu-bind=closest
#SBATCH --mem=700g  # A100x4 nodes have 2TB RAM total

# Print node information
echo "Job is starting on $(hostname)"
date

# Load necessary modules
module load cuda/11.8.0
module load cudnn/8.9.0.131
source hellaswag_env/bin/activate
module load openmpi/4.1.6
module load nccl/2.19.3-1

# Assuming you've already created the virtual environment and installed packages
# source ~/llmc_env/bin/activate not needed because we're not using python

# Set some MPI environment variables for better performance
export LD_LIBRARY_PATH=/sw/spack/deltas11-2023-03/apps/linux-rhel8-zen3/gcc-11.4.0/openmpi-4.1.6-lranp74/lib:/sw/spack/deltas11-2023-03/apps/linux-rhel8-zen3/gcc-11.4.0/nccl-2.19.3-1-464jrf3/lib:/sw/external/libraries/cudnn-linux-x86_64-8.9.0.131_cuda11-archive/lib:$LD_LIBRARY_PATH

export OMPI_MCA_btl="^openib"
# export OMPI_MCA_pml="ucx"
# export UCX_TLS="rc,sm,cuda_copy,cuda_ipc,gdr_copy"
# export UCX_RNDV_SCHEME="put_zcopy"
# export UCX_MEMTYPE_CACHE=n
export NCCL_IB_TIMEOUT=100
export NCCL_DEBUG=INFO

# Navigate to llm.c directory (adjust path as needed)
# cd ~/llm.c not needed since we're there

# Run the training with mpirun
# The parameters here match Karpathy's example but with larger batch size and no -x

out_dir="log774M-b8"
done_file="$out_dir/DONE_00150000"

# in case the training stalls or crashes, loop to resume (-y 1)
while true; do

    # exit condition is that optimization has finished
    if [ -f "$done_file" ]; then
        echo "File $done_file exists. Exiting the loop."
        break
    fi

    mpirun -np 8 ./train_gpt2cu \
                -i "/work/hdd/bdfx/shards/firsttrain/documents_train*.bin" \
                -j "/work/hdd/bdfx/shards/firsttrain/documents_val_*.bin" \
                -o log774M-b8 \
                -v 250 -s 300000 -g 144 \
                -h 1 \
                -b 8 -t 1024 \
                -d 524288 -x 150000 \
                -r 0 \
                -z 1 \
                -c 0.1 \
                -l 0.00025 \
                -q 0.0 \
                -u 700 \
                -n 4000 \
                -y 1 \
                -e "d36"

    sleep 1
done

# print completion time
date
echo "Job completed"
