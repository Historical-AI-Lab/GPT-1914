"""
Stage A: Build a benchmark diff between two ChronoLogic benchmark versions.

Joins two benchmarks on `question_number`, identifies deletions, additions,
and in-place edits, and writes to --out-dir:

1. {mini-name-prefix}_mcq.jsonl -- mini-benchmark containing full new-version
   records for every question that needs a fresh MCQ/likelihood-scored run:
   additions plus any question whose --prompt-fields changed (by default this
   includes the answer fields, since MCQ/likelihood scoring is positional
   against the option list -- any change to answer_strings/answer_types/
   answer_probabilities invalidates old answers for that question).

2. {mini-name-prefix}_freegen.jsonl -- mini-benchmark containing full
   new-version records for every question that needs a fresh free-generation
   run: additions plus any question whose --freegen-fields changed (by
   default just metadata_frame/main_question, since free-generation never
   shows the candidate model the answer options). This is normally a subset
   of the mcq mini-benchmark.

3. diff_manifest.json -- machine-readable contract consumed by the fusion
   scripts (fuse_eval_results.py, fuse_free_generation.py):
   {
     "old_file": "...", "new_file": "...",
     "old_label": "0.4", "new_label": "0.7",
     "prompt_fields": [...], "freegen_fields": [...],
     "old_qnum_order": [1, 2, ...],    # old-file line position -> question_number
     "new_qnum_order": [1, 2, ...],    # new-file line position -> question_number
     "deleted_qnums": [...], "added_qnums": [...],
     "rerun_qnums": [...],             # = rerun_qnums_mcq, kept for compatibility
     "rerun_qnums_mcq": [...],
     "rerun_qnums_freegen": [...],
     "mini_benchmark_mcq": "...", "mini_benchmark_freegen": "...",
     "changed_fields": {"2": ["answer_strings", ...], ...},
     "subset_only_changes": {"243": ["question_category"], ...}
   }

4. DIFF_REPORT.md -- human-readable summary with before/after snippets.

Usage
-----
python evalcode/make_benchmark_diff.py \\
    booksample/chronologic_en_0.4.jsonl \\
    booksample/chronologic_en_0.7.jsonl \\
    --out-dir evalcode/diff_0.4_to_0.7 \\
    --old-label 0.4 --new-label 0.7

Options
-------
--out-dir DIR          Output directory (default: diff_<old>_to_<new>)
--old-label STR        Label for the old file in reports/manifest (default:
                        extracted from the filename, e.g. "0.4")
--new-label STR        Label for the new file (default: extracted similarly)
--prompt-fields F      Comma-separated field names that matter to MCQ/
                        likelihood-scored candidates (default:
                        metadata_frame,main_question,answer_strings,
                        answer_types,answer_probabilities)
--freegen-fields F     Comma-separated field names that matter to
                        free-generation candidates; must be a subset of
                        --prompt-fields (default: metadata_frame,main_question)
--ignore-fields F      Comma-separated field names excluded from diffing and
                        reporting entirely (default: substantive_metadata_frame)
--mini-name-prefix P   Filename stem prefix for the two mini-benchmark JSONL
                        files (default: chronologic_diff_<old>_to_<new>)
"""

import argparse
import json
import re
from pathlib import Path


# Fields that directly affect an MCQ/likelihood-scored candidate's prompt or
# scoring; any change here requires re-running that flavor.
DEFAULT_PROMPT_FIELDS = [
    "metadata_frame",
    "main_question",
    "answer_strings",
    "answer_types",
    "answer_probabilities",
]

# Fields that affect a free-generation candidate's prompt (it never sees
# answer options, so this is normally a subset of DEFAULT_PROMPT_FIELDS).
DEFAULT_FREEGEN_FIELDS = [
    "metadata_frame",
    "main_question",
]

# Fields that only affect subset slicing in confidence-interval reporting; a
# change here is handled at integration time without re-running the model.
SUBSET_FIELDS = [
    "question_category",
    "frame_type",
    "reasoning_type",
    "answer_length",
]

# Fields excluded from diffing/reporting entirely (schema bookkeeping with no
# effect on any candidate's prompt).
DEFAULT_IGNORE_FIELDS = [
    "substantive_metadata_frame",
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


def guess_label(path):
    """Extract a version-like label (e.g. "0.4") from a filename, else stem."""
    m = re.search(r"(\d+\.\d+)", Path(path).stem)
    return m.group(1) if m else Path(path).stem


def main():
    parser = argparse.ArgumentParser(
        description="Build a benchmark diff between two ChronoLogic JSONL files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("old_jsonl", help="Path to the old benchmark (e.g. 0.4)")
    parser.add_argument("new_jsonl", help="Path to the new benchmark (e.g. 0.7)")
    parser.add_argument("--out-dir", default=None, help="Output directory")
    parser.add_argument("--old-label", default=None, help="Label for the old file")
    parser.add_argument("--new-label", default=None, help="Label for the new file")
    parser.add_argument(
        "--prompt-fields",
        default=",".join(DEFAULT_PROMPT_FIELDS),
        help="Comma-separated MCQ/likelihood-visible field names",
    )
    parser.add_argument(
        "--freegen-fields",
        default=",".join(DEFAULT_FREEGEN_FIELDS),
        help="Comma-separated free-generation-visible field names "
             "(must be a subset of --prompt-fields)",
    )
    parser.add_argument(
        "--ignore-fields",
        default=",".join(DEFAULT_IGNORE_FIELDS),
        help="Comma-separated field names excluded from diff/report entirely",
    )
    parser.add_argument(
        "--mini-name-prefix",
        default=None,
        help="Filename stem prefix for the mini-benchmark JSONL files",
    )
    args = parser.parse_args()

    old_label = args.old_label or guess_label(args.old_jsonl)
    new_label = args.new_label or guess_label(args.new_jsonl)

    prompt_fields = [f.strip() for f in args.prompt_fields.split(",") if f.strip()]
    freegen_fields = [f.strip() for f in args.freegen_fields.split(",") if f.strip()]
    ignore_fields = set(f.strip() for f in args.ignore_fields.split(",") if f.strip())

    if not set(freegen_fields) <= set(prompt_fields):
        raise ValueError(
            f"--freegen-fields {freegen_fields} must be a subset of "
            f"--prompt-fields {prompt_fields}"
        )

    out_dir = Path(args.out_dir or f"diff_{old_label}_to_{new_label}")
    out_dir.mkdir(parents=True, exist_ok=True)

    mini_name_prefix = args.mini_name_prefix or f"chronologic_diff_{old_label}_to_{new_label}"

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
    changed_fields = {}      # qnum -> list of changed mcq/likelihood-tier fields
    subset_only_changes = {} # qnum -> list of changed subset-only fields
    all_changed = {}         # qnum -> list of ALL changed fields (for report)

    for qn in new_qnum_order:
        if qn not in old_by_qnum:
            continue  # addition -- tracked separately
        old_rec = old_by_qnum[qn]
        new_rec = new_by_qnum[qn]
        all_fields = set(old_rec.keys()) | set(new_rec.keys())
        changed = []
        for field in sorted(all_fields):
            if field in ignore_fields:
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
            # field (e.g. passage, partial_credit).  No re-run needed.
            pass

    # Re-run sets: mcq/likelihood tier and free-generation tier
    rerun_set_mcq = set(changed_fields.keys()) | set(added_qnums)
    rerun_set_freegen = {
        qn for qn, fields in changed_fields.items()
        if any(f in freegen_fields for f in fields)
    } | set(added_qnums)

    rerun_qnums_mcq = [qn for qn in new_qnum_order if qn in rerun_set_mcq]
    rerun_qnums_freegen = [qn for qn in new_qnum_order if qn in rerun_set_freegen]

    # -----------------------------------------------------------------------
    # 1. Write mini-benchmark JSONLs
    # -----------------------------------------------------------------------
    mini_path_mcq = out_dir / f"{mini_name_prefix}_mcq.jsonl"
    with open(mini_path_mcq, "w", encoding="utf-8") as f:
        for qn in rerun_qnums_mcq:
            f.write(json.dumps(new_by_qnum[qn], ensure_ascii=False) + "\n")
    print(f"MCQ/likelihood mini-benchmark written: {mini_path_mcq}  ({len(rerun_qnums_mcq)} questions)")

    mini_path_freegen = out_dir / f"{mini_name_prefix}_freegen.jsonl"
    with open(mini_path_freegen, "w", encoding="utf-8") as f:
        for qn in rerun_qnums_freegen:
            f.write(json.dumps(new_by_qnum[qn], ensure_ascii=False) + "\n")
    print(f"Free-generation mini-benchmark written: {mini_path_freegen}  ({len(rerun_qnums_freegen)} questions)")

    # -----------------------------------------------------------------------
    # 2. Write diff_manifest.json
    # -----------------------------------------------------------------------
    manifest = {
        "old_file": str(Path(args.old_jsonl).resolve()),
        "new_file": str(Path(args.new_jsonl).resolve()),
        "old_label": old_label,
        "new_label": new_label,
        "prompt_fields": prompt_fields,
        "freegen_fields": freegen_fields,
        "old_qnum_order": old_qnum_order,
        "new_qnum_order": new_qnum_order,
        "deleted_qnums": deleted_qnums,
        "added_qnums": added_qnums,
        "rerun_qnums": rerun_qnums_mcq,          # kept for backward compatibility
        "rerun_qnums_mcq": rerun_qnums_mcq,
        "rerun_qnums_freegen": rerun_qnums_freegen,
        "mini_benchmark_mcq": str(mini_path_mcq),
        "mini_benchmark_freegen": str(mini_path_freegen),
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
    other_changed = {
        qn: fields
        for qn, fields in all_changed.items()
        if qn not in changed_fields and qn not in subset_only_changes
    }

    report_lines = [
        f"# Benchmark diff: {old_label} → {new_label}",
        "",
        f"- **Old file:** `{args.old_jsonl}`  ({len(old_records)} questions)",
        f"- **New file:** `{args.new_jsonl}`  ({len(new_records)} questions)",
        f"- **MCQ/likelihood-tier fields:** {', '.join(prompt_fields)}",
        f"- **Free-generation-tier fields:** {', '.join(freegen_fields)}",
        f"- **Ignored fields:** {', '.join(sorted(ignore_fields)) or '(none)'}",
        "",
        "## Summary",
        "",
        f"| Stat | Count |",
        f"|------|-------|",
        f"| Questions in {old_label} | {len(old_records)} |",
        f"| Questions in {new_label} | {len(new_records)} |",
        f"| Deleted (in {old_label}, not {new_label}) | {len(deleted_qnums)} |",
        f"| Added (in {new_label}, not {old_label}) | {len(added_qnums)} |",
        f"| Re-run — MCQ/likelihood tier | {len(rerun_qnums_mcq)} |",
        f"| Re-run — free-generation tier | {len(rerun_qnums_freegen)} |",
        f"| Subset-label-only changes (no re-run) | {len(subset_only_changes)} |",
        f"| Other field changes (passage etc., no re-run) | {len(other_changed)} |",
        "",
    ]

    if deleted_qnums:
        report_lines += [
            f"## Deleted questions (present in {old_label}, absent from {new_label})",
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
            f"## Added questions (present in {new_label}, absent from {old_label})",
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
            f"## Re-run — MCQ/likelihood tier ({len(rerun_qnums_mcq)} questions: "
            f"{len(added_qnums)} added + {len(changed_fields)} changed)",
            "",
        ]
        for qn in rerun_qnums_mcq:
            if qn not in changed_fields:
                continue  # already listed under "Added questions" above
            old_rec = old_by_qnum[qn]
            new_rec = new_by_qnum[qn]
            fields = changed_fields[qn]
            in_freegen_tier = qn in rerun_set_freegen
            report_lines.append(
                f"### qnum {qn}"
                + (" (also in free-generation tier)" if in_freegen_tier else "")
            )
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

    if other_changed:
        report_lines += [
            f"## Other field changes — passage etc. (no re-run, {len(other_changed)} questions)",
            "",
        ]
        for qn, fields in sorted(other_changed.items()):
            report_lines.append(f"- **qnum {qn}**: {', '.join(fields)}")
        report_lines.append("")

    report_lines += [
        "## Mini-benchmarks",
        "",
        f"MCQ/likelihood tier ({len(rerun_qnums_mcq)} questions): `{mini_path_mcq}`",
        "",
        f"    python evalcode/benchmark_evaluation.py <model> {mini_path_mcq} "
        f"--mcq --output-dir evalcode/mcq_{new_label.replace('.', '')}_diff",
        f"    python evalcode/benchmark_evaluation.py <model> {mini_path_mcq} "
        f"--full-eval --output-dir evalcode/prob_{new_label.replace('.', '')}_diff",
        "",
        f"Free-generation tier ({len(rerun_qnums_freegen)} questions): `{mini_path_freegen}`",
        "",
        f"    python evalcode/benchmark_free_generation.py <model> {mini_path_freegen} "
        f"--output evalcode/free_{new_label.replace('.', '')}_diff/free_gen_<model>_<ts>.json",
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
    print(f"  Old: {len(old_records)} questions ({old_label})")
    print(f"  New: {len(new_records)} questions ({new_label})")
    print(f"  Deleted:                 {deleted_qnums}")
    print(f"  Added:                   {added_qnums}")
    print(f"  Re-run (mcq/likelihood): {len(rerun_qnums_mcq)} qnums")
    print(f"  Re-run (free-gen):       {len(rerun_qnums_freegen)} qnums")
    print(f"  Subset-only qnums:       {sorted(subset_only_changes.keys())}")


if __name__ == "__main__":
    main()
