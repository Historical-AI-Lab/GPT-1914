"""
Stage A: Build a benchmark diff between chronologic_en_0.2 and chronologic_en_0.4.

Joins the two benchmarks on `question_number`, identifies deletions and in-place
edits, and writes three outputs to --out-dir:

1. chronologic_diff_0.2_to_0.4.jsonl  -- mini-benchmark containing only questions
   whose model-visible fields changed (full 0.4 records, in 0.4 order).  Feed
   this directly to benchmark_evaluation.py for stage-B re-runs.

2. diff_manifest.json -- machine-readable contract consumed by
   integrate_diff_results.py (stage C):
   {
     "old_file": "...0.2.jsonl",
     "new_file": "...0.4.jsonl",
     "prompt_fields": [...],
     "old_qnum_order": [1, 2, ...],    # 0.2 line position -> question_number
     "new_qnum_order": [1, 2, ...],    # 0.4 line position -> question_number
     "deleted_qnums": [20, 321],
     "rerun_qnums": [2, 63, 97, ...],  # questions in mini-benchmark, in 0.4 order
     "changed_fields": {"2": ["answer_strings", ...], ...},
     "subset_only_changes": {"243": ["question_category"], ...}
   }

3. DIFF_REPORT.md -- human-readable summary with before/after snippets.

Usage
-----
python evalcode/make_benchmark_diff.py \\
    booksample/chronologic_en_0.2.jsonl \\
    booksample/chronologic_en_0.4.jsonl \\
    --out-dir evalcode/diff_0.2_to_0.4

Options
-------
--out-dir DIR      Output directory (default: evalcode/diff_0.2_to_0.4)
--prompt-fields F  Comma-separated field names whose changes trigger a re-run
                   (default: metadata_frame,main_question,answer_strings,
                             answer_types,answer_probabilities)
--mini-name NAME   Filename stem for the mini-benchmark JSONL
                   (default: chronologic_diff_0.2_to_0.4)
"""

import argparse
import json
import textwrap
from pathlib import Path


# Fields that directly affect the model's prompt or scoring; any change here
# requires re-running the model.
DEFAULT_PROMPT_FIELDS = [
    "metadata_frame",
    "main_question",
    "answer_strings",
    "answer_types",
    "answer_probabilities",
]

# Fields that only affect subset slicing in confidence-interval reporting; a
# change here is handled at integration time without re-running the model.
SUBSET_FIELDS = [
    "question_category",
    "frame_type",
    "reasoning_type",
    "answer_length",
]


def load_jsonl(path):
    """Return list of dicts from a JSONL file, preserving order."""
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def field_changed(old_val, new_val):
    """Return True if two field values differ."""
    return old_val != new_val


def format_snippet(val, max_len=120):
    """Return a short printable representation of a field value."""
    s = json.dumps(val, ensure_ascii=False)
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    return s


def main():
    parser = argparse.ArgumentParser(
        description="Build a benchmark diff between two ChronoLogic JSONL files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("old_jsonl", help="Path to the old benchmark (e.g. 0.2)")
    parser.add_argument("new_jsonl", help="Path to the new benchmark (e.g. 0.4)")
    parser.add_argument(
        "--out-dir",
        default="diff_0.2_to_0.4",
        help="Output directory (default: diff_0.2_to_0.4)",
    )
    parser.add_argument(
        "--prompt-fields",
        default=",".join(DEFAULT_PROMPT_FIELDS),
        help="Comma-separated model-visible field names (changes trigger re-runs)",
    )
    parser.add_argument(
        "--mini-name",
        default="chronologic_diff_0.2_to_0.4",
        help="Stem for the mini-benchmark JSONL filename",
    )
    args = parser.parse_args()

    prompt_fields = [f.strip() for f in args.prompt_fields.split(",") if f.strip()]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading old benchmark: {args.old_jsonl}")
    old_records = load_jsonl(args.old_jsonl)
    print(f"Loading new benchmark: {args.new_jsonl}")
    new_records = load_jsonl(args.new_jsonl)

    # Build qnum -> record maps and ordered qnum lists
    old_by_qnum = {}
    old_qnum_order = []
    for rec in old_records:
        qn = rec["question_number"]
        old_by_qnum[qn] = rec
        old_qnum_order.append(qn)

    new_by_qnum = {}
    new_qnum_order = []
    for rec in new_records:
        qn = rec["question_number"]
        new_by_qnum[qn] = rec
        new_qnum_order.append(qn)

    old_qnums = set(old_qnum_order)
    new_qnums = set(new_qnum_order)

    deleted_qnums = sorted(old_qnums - new_qnums)
    added_qnums = sorted(new_qnums - old_qnums)

    # For each question present in both, detect changed fields
    changed_fields = {}      # qnum -> list of changed prompt fields
    subset_only_changes = {} # qnum -> list of changed subset-only fields
    all_changed = {}         # qnum -> list of ALL changed fields (for report)

    for qn in new_qnum_order:
        if qn not in old_by_qnum:
            continue  # addition -- tracked separately
        old_rec = old_by_qnum[qn]
        new_rec = new_by_qnum[qn]
        all_fields = set(old_rec.keys()) | set(new_rec.keys())
        # Ignore the new-only field 'substantive_metadata_frame'
        changed = []
        for field in sorted(all_fields):
            if field == "substantive_metadata_frame":
                continue
            old_val = old_rec.get(field)
            new_val = new_rec.get(field)
            if field_changed(old_val, new_val):
                changed.append(field)
        if not changed:
            continue
        all_changed[qn] = changed
        prompt_changes = [f for f in changed if f in prompt_fields]
        subset_changes = [f for f in changed if f in SUBSET_FIELDS]
        if prompt_changes:
            changed_fields[qn] = prompt_changes
        elif subset_changes:
            subset_only_changes[qn] = subset_changes
        else:
            # Changed in a field that is neither prompt-visible nor a subset
            # field (e.g. passage).  No re-run needed; record for the report.
            pass

    # Re-run set: questions that need a new model run, in 0.4 order
    rerun_set = set(changed_fields.keys())
    rerun_qnums = [qn for qn in new_qnum_order if qn in rerun_set]

    # -----------------------------------------------------------------------
    # 1. Write mini-benchmark JSONL
    # -----------------------------------------------------------------------
    mini_path = out_dir / f"{args.mini_name}.jsonl"
    with open(mini_path, "w", encoding="utf-8") as f:
        for qn in rerun_qnums:
            f.write(json.dumps(new_by_qnum[qn], ensure_ascii=False) + "\n")
    print(f"Mini-benchmark written: {mini_path}  ({len(rerun_qnums)} questions)")

    # -----------------------------------------------------------------------
    # 2. Write diff_manifest.json
    # -----------------------------------------------------------------------
    manifest = {
        "old_file": str(Path(args.old_jsonl).resolve()),
        "new_file": str(Path(args.new_jsonl).resolve()),
        "prompt_fields": prompt_fields,
        "old_qnum_order": old_qnum_order,
        "new_qnum_order": new_qnum_order,
        "deleted_qnums": deleted_qnums,
        "added_qnums": added_qnums,
        "rerun_qnums": rerun_qnums,
        "changed_fields": {str(k): v for k, v in changed_fields.items()},
        "subset_only_changes": {str(k): v for k, v in subset_only_changes.items()},
    }
    manifest_path = out_dir / "diff_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written:       {manifest_path}")

    # -----------------------------------------------------------------------
    # 3. Write DIFF_REPORT.md
    # -----------------------------------------------------------------------
    report_lines = [
        "# Benchmark diff: 0.2 → 0.4",
        "",
        f"- **Old file:** `{args.old_jsonl}`  ({len(old_records)} questions)",
        f"- **New file:** `{args.new_jsonl}`  ({len(new_records)} questions)",
        f"- **Prompt fields:** {', '.join(prompt_fields)}",
        "",
        "## Summary",
        "",
        f"| Stat | Count |",
        f"|------|-------|",
        f"| Questions in 0.2 | {len(old_records)} |",
        f"| Questions in 0.4 | {len(new_records)} |",
        f"| Deleted (in 0.2, not 0.4) | {len(deleted_qnums)} |",
        f"| Added (in 0.4, not 0.2) | {len(added_qnums)} |",
        f"| Prompt-visible changes → re-run | {len(changed_fields)} |",
        f"| Subset-label-only changes (no re-run) | {len(subset_only_changes)} |",
        f"| Other field changes (passage etc., no re-run) | "
        f"{len(all_changed) - len(changed_fields) - len(subset_only_changes)} |",
        "",
    ]

    if deleted_qnums:
        report_lines += [
            "## Deleted questions (present in 0.2, absent from 0.4)",
            "",
        ]
        for qn in deleted_qnums:
            rec = old_by_qnum[qn]
            report_lines.append(
                f"- **qnum {qn}**: {format_snippet(rec.get('main_question', ''))}"
            )
        report_lines.append("")

    if added_qnums:
        report_lines += [
            "## Added questions (present in 0.4, absent from 0.2)",
            "",
        ]
        for qn in added_qnums:
            rec = new_by_qnum[qn]
            report_lines.append(
                f"- **qnum {qn}**: {format_snippet(rec.get('main_question', ''))}"
            )
        report_lines.append("")

    if changed_fields:
        report_lines += [
            f"## Prompt-visible changes → re-run ({len(changed_fields)} questions)",
            "",
        ]
        for qn in rerun_qnums:
            old_rec = old_by_qnum[qn]
            new_rec = new_by_qnum[qn]
            fields = changed_fields[qn]
            report_lines.append(f"### qnum {qn}")
            report_lines.append(f"Changed fields: {', '.join(fields)}")
            report_lines.append("")
            for field in fields:
                old_val = old_rec.get(field, "<absent>")
                new_val = new_rec.get(field, "<absent>")
                report_lines.append(f"**{field}**")
                report_lines.append(f"- OLD: `{format_snippet(old_val)}`")
                report_lines.append(f"- NEW: `{format_snippet(new_val)}`")
                report_lines.append("")

    if subset_only_changes:
        report_lines += [
            f"## Subset-label-only changes (no re-run, {len(subset_only_changes)} questions)",
            "",
        ]
        for qn, fields in sorted(subset_only_changes.items()):
            old_rec = old_by_qnum[qn]
            new_rec = new_by_qnum[qn]
            report_lines.append(f"### qnum {qn}")
            for field in fields:
                old_val = old_rec.get(field, "<absent>")
                new_val = new_rec.get(field, "<absent>")
                report_lines.append(
                    f"- **{field}**: `{format_snippet(old_val)}` → `{format_snippet(new_val)}`"
                )
            report_lines.append("")

    # Passage-only and other non-prompt, non-subset changes
    other_changed = {
        qn: fields
        for qn, fields in all_changed.items()
        if qn not in changed_fields and qn not in subset_only_changes
    }
    if other_changed:
        report_lines += [
            f"## Other field changes — passage etc. (no re-run, {len(other_changed)} questions)",
            "",
        ]
        for qn, fields in sorted(other_changed.items()):
            report_lines.append(f"- **qnum {qn}**: {', '.join(fields)}")
        report_lines.append("")

    report_lines += [
        "## Mini-benchmark",
        "",
        f"Written to: `{mini_path}`",
        "",
        f"Run with `benchmark_evaluation.py <model> {mini_path} [backend flags] "
        f"--output-dir evalcode/mcq_04_diff` (or `prob_04_diff`).",
        "",
    ]

    report_path = out_dir / "DIFF_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Diff report written:    {report_path}")

    # -----------------------------------------------------------------------
    # Console summary
    # -----------------------------------------------------------------------
    print()
    print("=== Summary ===")
    print(f"  Old: {len(old_records)} questions (0.2)")
    print(f"  New: {len(new_records)} questions (0.4)")
    print(f"  Deleted:           {deleted_qnums}")
    print(f"  Added:             {added_qnums}")
    print(f"  Re-run qnums:      {rerun_qnums}")
    print(f"  Subset-only qnums: {sorted(subset_only_changes.keys())}")


if __name__ == "__main__":
    main()
