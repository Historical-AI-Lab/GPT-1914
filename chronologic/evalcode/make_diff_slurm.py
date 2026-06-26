"""
Stage B (HPC path): Generate a SLURM script to run a model on the diff mini-benchmark.

Clones the structure of the existing evalcode/*.slurm templates but points at the
mini-benchmark produced by make_benchmark_diff.py and writes output to
mcq_04_diff/ or prob_04_diff/.

Usage
-----
python evalcode/make_diff_slurm.py \\
    --old evalcode/mcq_02/eval_results_mcq__projects_bdfx_models_gemma-3-27b-pt_<ts>.json \\
    --mini-benchmark evalcode/diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl

Options
-------
--old FILE            Path to the 0.2 result file for this model.  Used to read
                      model_id and eval_mode from metadata; also verifies that
                      the intended model matches.
--mini-benchmark FILE Path to the mini-benchmark JSONL (default:
                      evalcode/diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl)
--out FILE            Write the .slurm script here.  Default: evalcode/<slug>_diff.slurm
--eval-mode {mcq,probabilistic}
                      Override eval_mode (defaults to old result's eval_mode).
--model-id STR        Override model_id (defaults to old result's model_id).
--lora-adapter PATH   LoRA adapter path (if any).
--gpus N              Number of GPUs (default: inferred from model size; 1 for ≤7B,
                      2 for ≤32B, 4 for 72B+).
--mem-gb N            Memory in GB (default: inferred).
--no-hf-offline       Omit HF_HUB_OFFLINE=1 (for models not pre-downloaded).
--output-dir-mcq DIR  Where to write MCQ diff results (default: mcq_04_diff).
--output-dir-prob DIR Where to write prob diff results (default: prob_04_diff).
--dry-run             Print the script to stdout instead of writing to a file.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Model-size heuristics for GPU / memory selection
_GPU_MEMORY_HINTS = [
    # (substring in model_id, gpus, mem_gb, venv)
    ("72B",  4, 160, "qlora-env"),
    ("32B",  2,  64, "qlora-env"),
    ("27b",  2,  64, "qlora-env"),  # gemma-3-27b
    ("13b",  1, 128, "talkie-eval-env"),
    ("7B",   1,  64, "qlora-env"),
    ("7b",   1,  64, "qlora-env"),
]

_DEFAULT_GPUS   = 1
_DEFAULT_MEM    = 64
_DEFAULT_VENV   = "qlora-env"


def infer_resources(model_id):
    for hint, gpus, mem, venv in _GPU_MEMORY_HINTS:
        if hint in model_id:
            return gpus, mem, venv
    return _DEFAULT_GPUS, _DEFAULT_MEM, _DEFAULT_VENV


def model_safe_slug(model_id, lora_adapter=None):
    slug = model_id.replace(":", "_").replace("/", "_")
    if lora_adapter:
        slug += "_" + Path(lora_adapter).name
    return slug


def venv_activate_line(venv_name, model_id):
    """Return the source-activate line appropriate for the model."""
    if "talkie" in model_id.lower():
        return 'source "$SLURM_SUBMIT_DIR/talkie-eval-env/bin/activate"'
    return f"source ../qwentuning/{venv_name}/bin/activate"


def build_script(
    model_id,
    eval_mode,
    mini_benchmark,
    lora_adapter=None,
    gpus=None,
    mem_gb=None,
    hf_offline=True,
    output_dir_mcq="mcq_04_diff",
    output_dir_prob="prob_04_diff",
    device_map_auto=False,
):
    inferred_gpus, inferred_mem, venv = infer_resources(model_id)
    gpus   = gpus   or inferred_gpus
    mem_gb = mem_gb or inferred_mem

    slug = model_safe_slug(model_id, lora_adapter)
    job_name = f"{slug[:30]}-diff"
    mode_flag = "--mcq" if eval_mode == "mcq" else "--full-eval"
    out_dir = output_dir_mcq if eval_mode == "mcq" else output_dir_prob

    lines = [
        "#!/bin/bash",
        f"#SBATCH --nodes=1",
        f"#SBATCH --ntasks-per-node=1",
        f"#SBATCH --cpus-per-task=8",
        f"#SBATCH --partition=gpuA100x4",
        f"#SBATCH --account=bdfx-delta-gpu",
        f"#SBATCH --time=02:00:00",
        f"#SBATCH --job-name={job_name}",
        f"#SBATCH --error={job_name}-%j.err",
        f"#SBATCH --output={job_name}-%j.out",
        f"#SBATCH --gpus-per-node={gpus}",
        f"#SBATCH --mem={mem_gb}g",
        f'#SBATCH --constraint="scratch"',
        "",
        'echo "Job starting on $(hostname)"',
        "date",
        "",
        "module reset",
        "module load cudatoolkit/25.3_12.8",
        "module list",
        "",
        venv_activate_line(venv, model_id),
    ]

    # peft needed for LoRA
    if lora_adapter:
        lines.append("pip install -q peft")

    lines += [
        "",
        "SCRIPT_DIR=\"$SLURM_SUBMIT_DIR\"",
        'cd "$SCRIPT_DIR"',
        "",
    ]

    if hf_offline:
        lines += [
            "export HF_HOME=/work/nvme/bdfx/.cache/huggingface",
            "export TRANSFORMERS_CACHE=/work/nvme/bdfx/.cache/huggingface/hub",
            "export HF_HUB_OFFLINE=1",
            "",
        ]

    # Build the python command
    cmd = ["python -u benchmark_evaluation.py \\"]
    cmd.append(f"    {model_id} \\")
    cmd.append(f"    {mini_benchmark} \\")
    if device_map_auto or gpus > 1:
        cmd.append("    --device-map auto \\")
    if lora_adapter:
        cmd.append(f"    --lora-adapter {lora_adapter} \\")
    cmd.append(f"    {mode_flag} \\")
    cmd.append(f"    --output-dir {out_dir}")

    lines += cmd
    lines += [
        "",
        'echo "Job completed"',
        "date",
    ]

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a SLURM script for stage-B diff re-runs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--old", required=True,
        help="Path to old (0.2) result JSON (to read model_id / eval_mode)"
    )
    parser.add_argument(
        "--mini-benchmark",
        default="diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl",
        help="Path to mini-benchmark JSONL"
    )
    parser.add_argument("--out",          help="Output .slurm filename")
    parser.add_argument("--eval-mode",    choices=["mcq", "probabilistic"])
    parser.add_argument("--model-id",     help="Override model_id")
    parser.add_argument("--lora-adapter", help="LoRA adapter path")
    parser.add_argument("--gpus",         type=int)
    parser.add_argument("--mem-gb",       type=int)
    parser.add_argument(
        "--no-hf-offline", action="store_true",
        help="Omit HF_HUB_OFFLINE=1"
    )
    parser.add_argument(
        "--output-dir-mcq",  default="mcq_04_diff",
        help="Output dir for MCQ diff results (default: mcq_04_diff)"
    )
    parser.add_argument(
        "--output-dir-prob", default="prob_04_diff",
        help="Output dir for prob diff results (default: prob_04_diff)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print script to stdout instead of writing"
    )
    args = parser.parse_args()

    # Load metadata from old result file
    with open(args.old, encoding="utf-8") as f:
        old_result = json.load(f)
    old_meta = old_result["metadata"]

    model_id  = args.model_id  or old_meta["model_id"]
    eval_mode = args.eval_mode or old_meta["eval_mode"]

    print(f"Model:     {model_id}")
    print(f"Eval mode: {eval_mode}")
    print(f"Mini-benchmark: {args.mini_benchmark}")

    # Infer device_map_auto from old result metadata (if it was used before)
    # If the old result used it, we reproduce it; otherwise infer from GPU count
    gpus_to_use = args.gpus or infer_resources(model_id)[0]
    device_map_auto = gpus_to_use > 1

    script = build_script(
        model_id=model_id,
        eval_mode=eval_mode,
        mini_benchmark=args.mini_benchmark,
        lora_adapter=args.lora_adapter,
        gpus=args.gpus,
        mem_gb=args.mem_gb,
        hf_offline=not args.no_hf_offline,
        output_dir_mcq=args.output_dir_mcq,
        output_dir_prob=args.output_dir_prob,
        device_map_auto=device_map_auto,
    )

    if args.dry_run:
        print()
        print(script)
        return

    slug = model_safe_slug(model_id, args.lora_adapter)
    out_path = Path(args.out) if args.out else Path(f"{slug[:40]}_diff.slurm")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"SLURM script written: {out_path}")
    print(f"Submit with: sbatch {out_path}")


if __name__ == "__main__":
    main()
