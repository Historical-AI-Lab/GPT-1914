"""Evaluate memorization of source books via free-generation and MCQ tests.

Two modes, both driven by whatever model files are actually present in
memorize/freegen60questions/ and memorize/mcq60questions/ (no hardcoded model
list):

  freegen: string-match hit rate between model answers and ground truths.
  mcq:     per-book average skill score on the memorization MCQ, correlated
           against per-book average skill score on the real chronologic_en_0.4
           benchmark, to see whether memorizing a book predicts doing better
           on substantive questions about it.
"""

import argparse
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evalcode"))
from benchmark_evaluation import calculate_mcq_skill_score  # noqa: E402

# Maps memorize/mcq60questions metadata.model_id -> filename in --mcq04-dir.
# Naming differs too much between the two sets of runs (dates, reasoning
# effort, vendor prefixes) for automatic matching to be reliable, so this is
# maintained by hand. Add an entry here once a new model's memorization MCQ
# file lands in mcq60questions/.
MCQ04_FILE_FOR_MODEL = {
    "gpt-4.1-2025-04-14":
        "eval_results_mcq_gpt-4.1_20260627_112454.json",
    "gpt-5.4":
        "eval_results_mcq_gpt-5.4_medium_20260627_042128.json",
    "qwen/qwen-2.5-72b-instruct":
        "eval_results_mcq__projects_bdfx_models_Qwen2.5-72B-Instruct_20260627_034810.json",
    "deepseek/deepseek-r1-distill-llama-70b":
        "eval_results_mcq_deepseek_deepseek-r1-distill-llama-70b_20260626_163659.json",
}


def normalize(s):
    return s.lower().replace(".", "")


def normalize_barcode(barcode):
    """Canonicalize an htid for cross-file matching.

    chronologic_en_0.4.jsonl and memobenchfull.jsonl disagree on case and on
    whether the institution prefix (e.g. "hvd.") is present, for the same
    underlying book. Lowercase and drop everything up to the first "." to
    get a stable join key; verified unique (no collisions) across the 16
    memorization-test barcodes.
    """
    return barcode.lower().split(".", 1)[-1]


def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def row_k(row, include_negation=False):
    types = row["answer_types"]
    if include_negation:
        return len(types)
    return sum(1 for t in types if t != "negation")


def run_freegen_eval(freegen_dir, memobench_path, inspect_out=None):
    memobench = {row["question_number"]: row for row in load_jsonl(memobench_path)}

    files = sorted(
        p for p in Path(freegen_dir).glob("*.json")
        if ".bak" not in p.name and "TRUNCATED" not in p.name
    )
    if not files:
        print(f"No free-gen files found in {freegen_dir}")
        return

    inspect_lines = []
    print("=== Free-generation string-match evaluation ===")
    total_hits = 0
    total_n = 0
    for path in files:
        data = json.loads(path.read_text())
        model = data.get("model", path.stem)
        hits = 0
        n = 0
        for qnum_str, entry in sorted(data["answers"].items(), key=lambda kv: int(kv[0])):
            raw_answer = entry.get("answer", "") or ""
            ground_truths = entry.get("ground_truths", [])
            model_answer_norm = normalize(raw_answer)
            hit = any(normalize(gt) and normalize(gt) in model_answer_norm
                      for gt in ground_truths)
            n += 1
            if hit:
                hits += 1

            row = memobench.get(int(qnum_str), {})
            inspect_lines.append(
                f"[{'HIT ' if hit else 'MISS'}] model={model} question={qnum_str} "
                f"barcode={row.get('barcode_src', '?')}\n"
                f"  QUESTION      : {row.get('main_question', '?')}\n"
                f"  GROUND_TRUTHS : {ground_truths}\n"
                f"  MODEL_ANSWER  : {raw_answer!r}\n"
            )
        rate = hits / n if n else float("nan")
        print(f"{model}: {hits}/{n} = {rate:.3f}")
        total_hits += hits
        total_n += n

    overall = total_hits / total_n if total_n else float("nan")
    print(f"\nOverall: {total_hits}/{total_n} = {overall:.3f}")

    if inspect_out:
        Path(inspect_out).write_text("\n".join(inspect_lines))
        print(f"\nWrote {len(inspect_lines)} answer/ground-truth pairs to {inspect_out}")


def skill_grid(per_question_results, benchmark_rows, barcode_field,
                barcode_filter=None):
    """Group per-question skill scores by barcode, return {barcode: avg_skill}."""
    by_barcode = defaultdict(list)
    for result, row in zip(per_question_results, benchmark_rows):
        barcode = normalize_barcode(row[barcode_field])
        if barcode_filter is not None and barcode not in barcode_filter:
            continue
        k = row_k(row)
        skill = calculate_mcq_skill_score(bool(result["correct"]), k)
        by_barcode[barcode].append(skill)
    return {b: float(np.mean(scores)) for b, scores in by_barcode.items()}


def run_mcq_eval(mcq_dir, memobench_path, real_benchmark_path, mcq04_dir):
    memobench_rows = load_jsonl(memobench_path)
    real_rows = load_jsonl(real_benchmark_path)
    memo_barcodes = sorted({normalize_barcode(row["barcode_src"]) for row in memobench_rows})

    mcq_files = sorted(Path(mcq_dir).glob("eval_results_mcq_*.json"))
    if not mcq_files:
        print(f"No MCQ files found in {mcq_dir}")
        return

    print("=== MCQ skill-score evaluation ===\n")

    memo_grid = {}
    real_grid = {}
    for path in mcq_files:
        data = json.loads(path.read_text())
        model_id = data["metadata"]["model_id"]
        per_question_results = data["per_question_results"]

        overall = data.get("confidence_intervals", {}).get("overall_benchmark")
        if overall:
            accuracy = overall["accuracy"][1]
            skill_score = overall["skill_score"][1]
            print(f"{model_id}: accuracy={accuracy:.3f}, avg_skill_score={skill_score:.4f}")

        if len(per_question_results) != len(memobench_rows):
            warnings.warn(
                f"{path.name}: {len(per_question_results)} results but "
                f"{len(memobench_rows)} memobench rows; skipping"
            )
            continue

        memo_grid[model_id] = skill_grid(
            per_question_results, memobench_rows, "barcode_src"
        )

        mcq04_name = MCQ04_FILE_FOR_MODEL.get(model_id)
        if mcq04_name is None:
            print(f"WARNING: no mcq_04 mapping for model_id={model_id!r}; "
                  f"excluding from correlation")
            continue
        mcq04_path = Path(mcq04_dir) / mcq04_name
        if not mcq04_path.exists():
            print(f"WARNING: mapped mcq_04 file not found: {mcq04_path}; "
                  f"excluding {model_id} from correlation")
            continue
        real_data = json.loads(mcq04_path.read_text())
        real_results = real_data["per_question_results"]
        if len(real_results) != len(real_rows):
            warnings.warn(
                f"{mcq04_path.name}: {len(real_results)} results but "
                f"{len(real_rows)} real-benchmark rows; skipping {model_id}"
            )
            continue

        real_grid[model_id] = skill_grid(
            real_results, real_rows, "source_htid",
            barcode_filter=set(memo_barcodes),
        )

    print("Memorization-MCQ skill grid (model x barcode):")
    for model_id, row in memo_grid.items():
        print(f"  {model_id}: {row}")

    print("\nReal-benchmark skill grid, restricted to memo-test barcodes:")
    for model_id, row in real_grid.items():
        print(f"  {model_id}: {row}")

    memo_vals = []
    real_vals = []
    for model_id, real_row in real_grid.items():
        memo_row = memo_grid[model_id]
        for barcode in memo_barcodes:
            if barcode in memo_row and barcode in real_row:
                memo_vals.append(memo_row[barcode])
                real_vals.append(real_row[barcode])

    print(f"\nPaired (model, barcode) cells: n={len(memo_vals)}")
    if len(memo_vals) >= 2:
        r, p = pearsonr(memo_vals, real_vals)
        print(f"Pearson r={r:.3f}, p={p:.3f}")
    else:
        print("Not enough paired data to compute a correlation.")


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["freegen", "mcq", "both"],
                        default="both")
    parser.add_argument("--freegen-dir", default=str(here / "freegen60questions"))
    parser.add_argument("--mcq-dir", default=str(here / "mcq60questions"))
    parser.add_argument("--memobench", default=str(here / "memobenchfull.jsonl"))
    parser.add_argument("--real-benchmark",
                        default=str(here.parent / "booksample" / "chronologic_en_0.4.jsonl"))
    parser.add_argument("--mcq04-dir", default=str(here.parent / "evalcode" / "mcq_04"))
    parser.add_argument("--freegen-inspect-out",
                        default=str(here / "freegen_pairs.txt"),
                        help="Path to write question/ground-truth/model-answer "
                             "triples for manual inspection. Pass '' to skip.")
    args = parser.parse_args()

    if args.mode in ("freegen", "both"):
        run_freegen_eval(args.freegen_dir, args.memobench,
                          inspect_out=args.freegen_inspect_out or None)
        print()
    if args.mode in ("mcq", "both"):
        run_mcq_eval(args.mcq_dir, args.memobench, args.real_benchmark, args.mcq04_dir)


if __name__ == "__main__":
    main()
