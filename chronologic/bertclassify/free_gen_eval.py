#!/usr/bin/env python3
"""free_gen_eval.py

Unified free-generation evaluation pipeline.

Integrates triage → DeBERTa inference → pair scoring → manual review into a
single workflow, adds rejected_questions.txt as a triage criterion, tracks
question_numbers through the DeBERTa path, and computes an overall accuracy
estimate.

Usage:
    python bertclassify/free_gen_eval.py INPUT_FILE [options]

Positional:
    INPUT_FILE              Free-gen JSON result file

Options:
    --benchmark PATH        Benchmark JSONL
                            (default: booksample/chronologic_en_0.1.jsonl)
    --model-dir PATH        DeBERTa model directory
                            (default: baseline/)
    --device STR            Device for DeBERTa: mps | cuda | cpu | auto
                            (default: auto)
    --start-line N          Resume manual scoring from line N; defaults to
                            counting existing lines in the scored file
    --auto-only             Skip manual scoring; write partial results with
                            DeBERTa scores only

Examples:
    python bertclassify/free_gen_eval.py booksample/free_gen_gpt-5.4_20260318_180622.json

    python bertclassify/free_gen_eval.py booksample/free_gen_gpt-5.4_20260318_180622.json \\
        --auto-only

    python bertclassify/free_gen_eval.py booksample/free_gen_gpt-5.4_20260318_180622.json \\
        --model-dir bertclassify/model_output/search_1/ --device cpu
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from free_gen_triage import (
    _derive_output_stem,
    count_words,
    load_benchmark,
    trim_quotes,
    write_deberta_tsv,
    write_manual_jsonl,
)

FORSCORING_DIR = SCRIPT_DIR / "forscoring"
FORMANUAL_DIR = SCRIPT_DIR / "formanual"
SCORES_DIR = SCRIPT_DIR / "scores"

REJECTED_QUESTIONS_PATH = SCRIPT_DIR / "rejected_questions.txt"
DEFAULT_BENCHMARK = REPO_ROOT / "booksample" / "chronologic_en_0.1.jsonl"
DEFAULT_MODEL_DIR = "baseline/"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Unified free-generation evaluation pipeline.",
    )
    parser.add_argument(
        "input_file",
        metavar="INPUT_FILE",
        help="Free-gen JSON result file",
    )
    parser.add_argument(
        "--benchmark",
        default=str(DEFAULT_BENCHMARK),
        metavar="PATH",
        help="Benchmark JSONL (default: booksample/chronologic_en_0.1.jsonl)",
    )
    parser.add_argument(
        "--model-dir",
        default=DEFAULT_MODEL_DIR,
        dest="model_dir",
        metavar="PATH",
        help="DeBERTa model directory (default: baseline/)",
    )
    parser.add_argument(
        "--device",
        default="auto",
        metavar="STR",
        help="Device for DeBERTa: mps | cuda | cpu | auto (default: auto)",
    )
    parser.add_argument(
        "--start-line",
        default=None,
        type=int,
        dest="start_line",
        metavar="N",
        help="Resume manual scoring from line N (default: auto-detect from scored file)",
    )
    parser.add_argument(
        "--auto-only",
        action="store_true",
        dest="auto_only",
        help="Skip manual scoring; write partial results with DeBERTa scores only",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Step 1: Load rejected questions
# ---------------------------------------------------------------------------

def load_rejected_questions(path=None):
    """Read rejected_questions.txt; return set of question number strings.

    Each non-empty line is treated as a question number. Returns empty set if
    the file does not exist.
    """
    if path is None:
        path = REJECTED_QUESTIONS_PATH
    path = Path(path)
    if not path.exists():
        return set()
    rejected = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            qnum = line.strip()
            if qnum:
                rejected.add(qnum)
    return rejected


# ---------------------------------------------------------------------------
# Step 1: Triage with rejected questions
# ---------------------------------------------------------------------------

def triage_with_rejected(answers, benchmark, rejected_qnums):
    """Apply triage criteria including rejected question list.

    Routing priority:
      1. rejected_qnums  → manual, triage_reason="rejected"
      2. short_ground_truth (< 5 words)
      3. short_answer (< 5 words)
      4. abstention reasoning_type
      5. short_answer_length answer_length field

    Returns:
        deberta_items   : list of dicts (parallel to deberta_qnums)
        manual_items    : list of enriched dicts
        deberta_qnums   : list of str question numbers, parallel to deberta_items
    """
    deberta_items = []
    manual_items = []
    deberta_qnums = []

    for qnum_raw, entry in answers.items():
        qnum = str(qnum_raw)
        ground_truth = entry.get("ground_truth", "")
        model_answer = entry.get("answer", "")
        reasoning_type = entry.get("reasoning_type", "")

        bench = benchmark.get(qnum, {})
        answer_length = bench.get("answer_length", "")

        # These reasoning types always go to DeBERTa
        if reasoning_type in ("sentence_cloze", "phrase_cloze", "character_modeling"):
            item = {
                "question_number": qnum,
                "metadata_frame": entry.get("metadata_frame", ""),
                "main_question": entry.get("main_question", ""),
                "ground_truth": ground_truth,
                "model_answer": model_answer,
                "reasoning_type": reasoning_type,
                "length_spec": entry.get("length_spec", ""),
            }
            deberta_items.append(item)
            deberta_qnums.append(qnum)
            continue

        # Determine triage reason — rejected check first
        triage_reason = None
        if qnum in rejected_qnums:
            triage_reason = "rejected"
        elif count_words(ground_truth) < 5:
            triage_reason = "short_ground_truth"
        elif count_words(model_answer) < 5:
            triage_reason = "short_answer"
        elif reasoning_type == "abstention":
            triage_reason = "abstention"
        elif answer_length == "short_answer":
            triage_reason = "short_answer_length"

        item = {
            "question_number": qnum,
            "metadata_frame": entry.get("metadata_frame", ""),
            "main_question": entry.get("main_question", ""),
            "ground_truth": ground_truth,
            "model_answer": model_answer,
            "reasoning_type": reasoning_type,
            "length_spec": entry.get("length_spec", ""),
        }

        if triage_reason is None:
            deberta_items.append(item)
            deberta_qnums.append(qnum)
        else:
            manual_item = dict(item)
            manual_item["answer_strings"] = bench.get("answer_strings", [])
            manual_item["answer_types"] = bench.get("answer_types", [])
            manual_item["answer_length"] = answer_length
            manual_item["triage_reason"] = triage_reason
            manual_items.append(manual_item)

    return deberta_items, manual_items, deberta_qnums


# ---------------------------------------------------------------------------
# Step 3: Pair scoring with question-number mapping
# ---------------------------------------------------------------------------

def score_deberta_pairs(predictions_path, deberta_qnums):
    """Read DeBERTa predictions; compute detection rate and per-question results.

    Rows in predictions_path are ordered gt/model alternating.  Pair i maps to
    deberta_qnums[i].

    Returns:
        scored_dict     : {qnum: "D" | "U"}  (D=detected, U=undetected)
        detection_rate  : float in [0, 1]
    """
    import csv

    predictions_path = Path(predictions_path)
    rows = []
    with open(predictions_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            rows.append(row)

    if len(rows) % 2 != 0:
        raise ValueError(
            f"Expected even number of prediction rows (gt/model pairs), got {len(rows)}."
        )

    n_pairs = len(rows) // 2
    if n_pairs != len(deberta_qnums):
        raise ValueError(
            f"Predictions has {n_pairs} pairs but deberta_qnums has {len(deberta_qnums)} entries."
        )

    scored_dict = {}
    detected_count = 0

    for i in range(n_pairs):
        gt_row = rows[2 * i]
        model_row = rows[2 * i + 1]
        gt_prob = float(gt_row["probability"])
        model_prob = float(model_row["probability"])
        detected = model_prob > gt_prob
        if detected:
            detected_count += 1
        qnum = deberta_qnums[i]
        scored_dict[qnum] = "D" if detected else "U"

    detection_rate = detected_count / n_pairs if n_pairs else 0.0
    return scored_dict, detection_rate


# ---------------------------------------------------------------------------
# Step 4: Manual scoring
# ---------------------------------------------------------------------------

def _load_scored_file(scored_path):
    """Read existing scored JSONL; return {qnum: {"correct": bool, "reason": str}}."""
    scored_path = Path(scored_path)
    existing = {}
    if scored_path.exists():
        with open(scored_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                qnum = str(record["question_number"])
                existing[qnum] = record
    return existing


def run_manual_scoring(manual_items, scored_path, start_line=None):
    """Interactively score manual items; append to scored_path.

    If start_line is None, it is derived by counting existing lines in scored_path.

    For each unscored question prints a formatted prompt and reads Y/n input.

    Returns:
        scored_dict     : {qnum: "T" | "F"}
        manual_accuracy : float in [0, 1]  (or 0.0 if nothing was scored)
    """
    scored_path = Path(scored_path)
    scored_path.parent.mkdir(parents=True, exist_ok=True)

    # Load already-scored records
    existing = _load_scored_file(scored_path)

    # Determine how many items to skip
    if start_line is None:
        start_line = len(existing)

    # Build scored_dict from existing records
    scored_dict = {}
    for qnum, record in existing.items():
        scored_dict[qnum] = "T" if record["correct"] else "F"

    # Open in append mode for new records
    with open(scored_path, "a", encoding="utf-8") as out_f:
        for idx, item in enumerate(manual_items):
            qnum = str(item["question_number"])

            # Skip already-scored
            if qnum in scored_dict:
                continue
            if idx < start_line:
                continue

            # Auto-accept exact matches
            answer_strings = item.get("answer_strings", [])
            answer_types = item.get("answer_types", [])
            model_answer = item.get("model_answer", "")

            if (answer_strings and answer_types
                    and answer_types[0] == "ground_truth"
                    and model_answer == answer_strings[0]):
                record = {"question_number": qnum, "correct": True, "reason": "exact_match"}
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_f.flush()
                scored_dict[qnum] = "T"
                continue

            reasoning_type = item.get("reasoning_type", "")
            if (reasoning_type == "abstention"
                    and model_answer.lower().strip(".") == "insufficient information"):
                record = {"question_number": qnum, "correct": True, "reason": "correct abstention"}
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_f.flush()
                scored_dict[qnum] = "T"
                continue

            # Display question
            print(f"\n--- Question {qnum} ---")
            print(f"Frame: {item.get('metadata_frame', '')}")
            print(f"Question: {item.get('main_question', '')}")

            if answer_strings:
                print("Answers:")
                for i, (ans, atype) in enumerate(zip(answer_strings, answer_types)):
                    print(f"  [{i}] ({atype}): \"{ans}\"")

            print(f"Model answer: \"{item.get('model_answer', '')}\"")

            try:
                correct_input = input("Correct? Y/n: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nScoring interrupted.")
                break

            correct = correct_input != "n"

            try:
                reason = input("Reason? ").strip() if not correct else ""
            except (EOFError, KeyboardInterrupt):
                reason = ""

            record = {
                "question_number": qnum,
                "correct": correct,
                "reason": reason,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()

            scored_dict[qnum] = "T" if correct else "F"

    # Compute accuracy
    total_scored = len(scored_dict)
    correct_count = sum(1 for v in scored_dict.values() if v == "T")
    manual_accuracy = correct_count / total_scored if total_scored else 0.0

    return scored_dict, manual_accuracy


# ---------------------------------------------------------------------------
# Step 5: Combined scoring and output
# ---------------------------------------------------------------------------

def compute_overall_accuracy(deberta_scored, manual_scored, total_questions):
    """Compute overall accuracy estimate.

    Uses indistinguishability assumption:
      d = detection rate among DeBERTa-scored questions
      g = fraction indistinguishable = (1 - d) / 0.5, clamped to [0, 1]
      estimated_indistinguishable = g * n_deberta
      manual_correct = count of "T" in manual_scored
      overall = (estimated_indistinguishable + manual_correct) / total_questions

    Returns:
        detection_rate, indistinguishable_rate, estimated_overall_accuracy
    """
    n_deberta = len(deberta_scored)
    if n_deberta == 0:
        detection_rate = 0.0
    else:
        detected = sum(1 for v in deberta_scored.values() if v == "D")
        detection_rate = detected / n_deberta

    g = (1.0 - detection_rate) / 0.5
    g = max(0.0, min(1.0, g))

    estimated_indistinguishable = g * n_deberta
    manual_correct = sum(1 for v in manual_scored.values() if v == "T")

    if total_questions == 0:
        overall = 0.0
    else:
        overall = (estimated_indistinguishable + manual_correct) / total_questions

    return detection_rate, g, overall


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    benchmark_path = Path(args.benchmark)
    if not benchmark_path.exists():
        print(f"Error: benchmark file not found: {benchmark_path}", file=sys.stderr)
        sys.exit(1)

    # Load inputs
    with open(input_path, encoding="utf-8") as f:
        free_gen = json.load(f)
    answers = free_gen.get("answers", {})
    model_name = free_gen.get("model", "unknown")

    benchmark = load_benchmark(benchmark_path)
    rejected_qnums = load_rejected_questions()

    # Triage
    deberta_items, manual_items, deberta_qnums = triage_with_rejected(
        answers, benchmark, rejected_qnums
    )

    total_questions = len(answers)
    n_deberta = len(deberta_items)
    n_manual = len(manual_items)

    # Derive output stem
    stem = _derive_output_stem(input_path)

    # Write intermediate files
    deberta_tsv_path = FORSCORING_DIR / f"{stem}_fordeberta.tsv"
    manual_jsonl_path = FORMANUAL_DIR / f"{stem}_formanual.jsonl"

    write_deberta_tsv(deberta_items, deberta_tsv_path)
    write_manual_jsonl(manual_items, manual_jsonl_path)

    print(f"Total questions:    {total_questions}")
    print(f"Sent to DeBERTa:    {n_deberta}  → {deberta_tsv_path}")
    print(f"Sent to manual:     {n_manual}  → {manual_jsonl_path}")

    reason_counts: dict = {}
    for item in manual_items:
        r = item["triage_reason"]
        reason_counts[r] = reason_counts.get(r, 0) + 1
    if reason_counts:
        print("Manual triage breakdown:")
        for reason, count in sorted(reason_counts.items()):
            print(f"  {reason}: {count}")

    # Step 2: DeBERTa inference
    predictions_path = FORSCORING_DIR / f"{stem}_fordeberta_predictions.tsv"

    model_dir = args.model_dir
    # Resolve relative model_dir against script dir
    model_dir_path = Path(model_dir)
    if not model_dir_path.is_absolute():
        model_dir_path = SCRIPT_DIR / model_dir_path

    if not model_dir_path.exists():
        print(
            f"Warning: model directory not found: {model_dir_path}\n"
            "Skipping DeBERTa inference. If predictions file already exists it will be used.",
            file=sys.stderr,
        )
        deberta_available = predictions_path.exists()
    else:
        print(f"\nRunning DeBERTa inference ...")
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "run_deberta.py"),
            str(deberta_tsv_path),
            "--model-dir", str(model_dir_path),
            "--output", str(predictions_path),
            "--device", args.device,
        ]
        result = subprocess.run(cmd, check=False)
        deberta_available = result.returncode == 0

    # Step 3: Pair scoring
    deberta_scored = {}
    detection_rate = 0.0

    if deberta_available and predictions_path.exists():
        print(f"\nScoring DeBERTa pairs ...")
        deberta_scored, detection_rate = score_deberta_pairs(
            predictions_path, deberta_qnums
        )
        g = max(0.0, min(1.0, (1.0 - detection_rate) / 0.5))
        print(f"Detection rate:         {detection_rate:.3f}")
        print(f"Indistinguishable rate: {g:.3f}")
    else:
        print("No DeBERTa predictions available; DeBERTa scores will be absent.", file=sys.stderr)

    # Step 4: Manual scoring
    manual_scored = {}
    manual_accuracy = 0.0
    scored_path = FORMANUAL_DIR / f"{stem}_scored.jsonl"

    if args.auto_only:
        print("\n--auto-only: skipping manual scoring.")
        # Still load existing scored file if present
        existing = _load_scored_file(scored_path)
        for qnum, record in existing.items():
            manual_scored[qnum] = "T" if record["correct"] else "F"
    else:
        if manual_items:
            print(f"\nStarting manual scoring ({n_manual} questions) ...")
            manual_scored, manual_accuracy = run_manual_scoring(
                manual_items, scored_path, start_line=args.start_line
            )
        else:
            print("\nNo manual items to score.")

    if manual_scored:
        correct_count = sum(1 for v in manual_scored.values() if v == "T")
        total_manual = len(manual_scored)
        manual_accuracy = correct_count / total_manual if total_manual else 0.0
        print(f"Manual accuracy:        {manual_accuracy:.3f}  ({correct_count}/{total_manual})")

    # Step 5: Combined scoring
    detection_rate, indistinguishable_rate, overall = compute_overall_accuracy(
        deberta_scored, manual_scored, total_questions
    )

    print(f"\nEstimated overall accuracy: {overall:.3f}")

    # Build output
    scored_answers = {}
    scored_answers.update(deberta_scored)
    scored_answers.update(manual_scored)

    output_data = {
        "model_evaluated": model_name,
        "benchmark_source_file": str(args.benchmark),
        "detection_rate": round(detection_rate, 6),
        "indistinguishable_rate": round(indistinguishable_rate, 6),
        "manual_accuracy": round(manual_accuracy, 6),
        "estimated_overall_accuracy": round(overall, 6),
        "scored_answers": scored_answers,
    }

    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    score_path = SCORES_DIR / f"{stem}_score.json"
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Score written → {score_path}")


if __name__ == "__main__":
    main()
