#!/usr/bin/env python3
"""generate_talkie_negatives.py — Phase D2 §4.3: negatives from Talkie on Delta.

`talkie-1930-13b-base` is the only genuinely untuned base model available and the
only generator anywhere in the stable actually *trained* on pre-1931 English —
which makes it the hardest negative source in the pool and the one most likely to
reproduce its training data verbatim. Every row therefore passes the same §5.4
leakage guard as everything else; a memorized passage is a positive wearing a
negative's label, and it would teach the detector the inverse of the target.

Quota: **1,600 continuation + 400 few-shot = 2,000 rows (6% of negatives)**, free
compute. Base models handle both natively from a raw prefix. Infill, paraphrase
and constrained generation need instruction-following and are not attempted.

Two stages, because the model needs a GPU and the staging does not:

    stage   builds `talkie_input.jsonl` locally — no GPU, no model download
    run     consumes it on Delta; `--dry-run` assembles prompts and emits schema
            rows *without* loading the checkpoint, which is the only sane local
            check (the real thing is a ~26 GB download and hour-scale CPU
            generation).

The deliverable here is the script pair plus the staged input. **The user submits
the Delta job**; `talkie_negatives.slurm` is written to be submitted as-is.
"""

import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from negative_qc import qc_negative                                    # noqa: E402
from normalize import load_lexicon                                     # noqa: E402
from sample_passages import load_length_table                          # noqa: E402

DEFAULT_PASSAGES = Path.home() / "workdata" / "chronologic-dating-corpus" / "passages"
DEFAULT_POSITIVES = DEFAULT_PASSAGES / "positive_passages.jsonl"
DEFAULT_PREP = DEFAULT_PASSAGES / "elicitation_prep.jsonl"
DEFAULT_INPUT = SCRIPT_DIR / "talkie_input.jsonl"
DEFAULT_OUT = SCRIPT_DIR / "talkie_negatives.jsonl"
DEFAULT_LENGTH_TABLE = SCRIPT_DIR / "length_distribution.json"

DEFAULT_MODEL = "talkie-1930-13b-base"
DEFAULT_N_CONTINUATION = 1600
DEFAULT_N_FEWSHOT = 400
DEFAULT_SEED = 20260809

CONTINUATION = "continuation"
FEW_SHOT = "few_shot"


# ---------------------------------------------------------------------------
# Prompt assembly — raw prefixes only; a base model has no chat template
# ---------------------------------------------------------------------------

def continuation_prompt(passage_row):
    """The passage itself. A base model continues text; it takes no instruction."""
    return passage_row["text"].rstrip()


def fewshot_prompt(prep_row):
    """Three period sentences, then a dangling fourth for the model to complete.

    No "write one sentence using X" instruction — that is a chat-model framing.
    The base model sees a list that stops mid-item and continues the pattern.
    """
    lines = [s.strip() for s in prep_row.get("sentences", [])]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# stage
# ---------------------------------------------------------------------------

def load_used_sources(negatives_path):
    """(modality, source_passage_id) pairs already consumed by another producer.

    Talkie is staged after elicitation has run, so without this the same passage
    would be handed to both an OpenRouter model and Talkie — two negatives off
    one source, which narrows the pool's real source diversity without narrowing
    its row count.
    """
    path = Path(negatives_path)
    used = set()
    if not path.exists():
        return used
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("source_passage_id"):
                used.add((row.get("elicitation_strategy"),
                          row["source_passage_id"]))
    return used


def stage_rows(positives, infill_unused, fewshot_prep, n_continuation, n_fewshot,
               rng, length_table, used_sources=(), achieved_rows=None,
               pool_total=32000):
    """Build the upload bundle: one row per generation the GPU job must perform.

    Continuation length targets are drawn from the *complement* of what the pool
    already holds, not from the raw Phase A table. Talkie is the last producer to
    run, so it is the last chance to correct the pool's length distribution --
    and continuation is one of only two modalities whose length is a free knob
    (infill is pinned by its gap, few-shot is one sentence by definition).
    """
    from measure_length_distribution import sample_length
    if achieved_rows:
        import sys as _sys
        _sys.path.insert(0, str(SCRIPT_DIR))
        from elicit_negatives import complement_length_table
        length_table = complement_length_table(length_table, achieved_rows,
                                               pool_total)

    used = set(used_sources)
    eligible = [r for r in positives if r.get("eligible_continuation")
                and (CONTINUATION, r["passage_id"]) not in used]
    rng.shuffle(eligible)
    fewshot = [r for r in fewshot_prep
               if (FEW_SHOT, r.get("elicitation_id")) not in used]
    rng.shuffle(fewshot)

    rows = []
    for row in eligible[:n_continuation]:
        n_sent, n_words, _ = sample_length(length_table, rng)
        rows.append({
            "talkie_id": f"talkie_continuation_{row['passage_id']}",
            "elicitation_strategy": CONTINUATION,
            "prompt": continuation_prompt(row),
            "target_sentences": n_sent,
            "target_words": n_words,
            "source_passage_id": row["passage_id"],
            "source_volume_id": row.get("volume_id"),
            "source_collection": row.get("collection"),
            "source_date": row.get("date"),
            "source_decade": row.get("decade"),
            # The prefix, for echo detection. The true continuation lives in the
            # volume and is not staged, so these rows are not leakage-checkable
            # in the strict sense -- flagged, not silently assumed checked.
            "prefix": row["text"],
            "references": [],
            "leakage_checkable": False,
        })

    for row in fewshot[:n_fewshot]:
        rows.append({
            "talkie_id": f"talkie_fewshot_{row['elicitation_id']}",
            "elicitation_strategy": FEW_SHOT,
            "prompt": fewshot_prompt(row),
            "target_sentences": 1,
            "target_words": None,
            "source_passage_id": row["elicitation_id"],
            "source_volume_id": row.get("volume_id"),
            "source_collection": row.get("collection"),
            "source_date": row.get("date"),
            "source_decade": row.get("decade"),
            "prefix": "",
            "references": list(row.get("sentences", [])),
            "leakage_checkable": True,
        })
    rng.shuffle(rows)
    return rows


def cmd_stage(args):
    rng = random.Random(args.seed)
    length_table = load_length_table(args.length_table)

    positives = []
    with open(args.positives_in, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if "authenticity_positive" in row.get("purposes", []):
                positives.append(row)

    fewshot_prep = []
    with open(args.prep_in, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("elicitation_strategy") == "few_shot":
                fewshot_prep.append(row)

    used = load_used_sources(args.negatives_in) if args.exclude_used else set()
    achieved = []
    if args.exclude_used and Path(args.negatives_in).exists():
        with open(args.negatives_in, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    achieved.append({"n_sentences": r.get("n_sentences", 0),
                                     "n_words": r.get("n_words", 0)})
    rows = stage_rows(positives, None, fewshot_prep, args.n_continuation,
                      args.n_fewshot, rng, length_table, used_sources=used,
                      achieved_rows=achieved)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({
        "staged": len(rows),
        "excluded_used_sources": len(used),
        "by_strategy": dict(Counter(r["elicitation_strategy"] for r in rows)),
        "by_decade": dict(sorted(Counter(r["source_decade"] for r in rows).items())),
        "out": str(args.out),
    }, indent=2), file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def load_input(path, start_line=0):
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < start_line or not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def already_done(out_path):
    """talkie_ids already written, so a resumed job does not repeat work."""
    path = Path(out_path)
    if not path.exists():
        return set()
    done = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                done.add(json.loads(line)["negative_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def make_row(job, raw_text, verdict, model_name, temperature, top_p):
    return {
        "negative_id": job["talkie_id"],
        "elicitation_strategy": job["elicitation_strategy"],
        "prompt_variant": "raw_prefix",
        "date_in_prompt": False,
        "model_id": model_name,
        "endpoint": "local",
        "temperature": temperature,
        "top_p": top_p,
        "reasoning_effort": None,
        "source_passage_id": job["source_passage_id"],
        "source_volume_id": job["source_volume_id"],
        "source_collection": job["source_collection"],
        "source_date": job["source_date"],
        "source_decade": job["source_decade"],
        "source_title": "",
        "raw_response": raw_text,
        "text": verdict["text"],
        "n_sentences": verdict["n_sentences"],
        "n_words": verdict["n_words"],
        "leakage_checkable": job["leakage_checkable"],
        "provenance": "talkie_local",
        "split_role": "train",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def cmd_run(args):
    # `normalize.DEFAULT_LEXICON` points at ~/Dropbox/DataMunging/rulesets/,
    # which exists on the workstation and nowhere else. On Delta the path must
    # be supplied explicitly or the run dies on the first QC call.
    lexicon = load_lexicon(args.lexicon)
    jobs = load_input(args.input, args.start_line)
    done = already_done(args.out)
    jobs = [j for j in jobs if j["talkie_id"] not in done]
    if args.limit:
        jobs = jobs[:args.limit]
    print(f"{len(jobs)} jobs to run ({len(done)} already done)", file=sys.stderr)

    model = None
    if not args.dry_run:
        try:
            from talkie import Talkie
        except ImportError as exc:
            raise SystemExit(
                "the `talkie` package is not importable. On Delta:\n"
                "  source \"$SLURM_SUBMIT_DIR/talkie-eval-env/bin/activate\"\n"
                f"({exc})")
        model = Talkie(args.model, device=args.device)

    stats = Counter()
    written = 0
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    for job in jobs:
        if args.dry_run:
            # Echo the prompt back as the "response" so schema assembly and QC
            # wiring are exercised without a checkpoint. These rows are never
            # written; the point is to prove the pipeline runs end to end.
            raw = job["prefix"] or job["prompt"]
            stats["dry_run_prompts_assembled"] += 1
            if stats["dry_run_prompts_assembled"] <= args.show:
                print("-" * 70, file=sys.stderr)
                print(f"{job['elicitation_strategy']} | {job['talkie_id']}",
                      file=sys.stderr)
                print(job["prompt"][:400], file=sys.stderr)
            continue

        try:
            result = model.generate(job["prompt"], temperature=args.temperature,
                                    top_p=args.top_p,
                                    max_tokens=args.max_new_tokens)
            raw = result.text
        except Exception as exc:                                   # noqa: BLE001
            stats[f"generation_error:{type(exc).__name__}"] += 1
            continue

        verdict = qc_negative(
            raw, lexicon=lexicon, references=job.get("references", []),
            bookend_before=job.get("prefix", ""),
            target_sentences=job.get("target_sentences"),
            target_words=job.get("target_words"))
        if not verdict["ok"]:
            stats[f"qc:{verdict['reason']}"] += 1
            continue

        with open(args.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(make_row(job, raw, verdict, args.model,
                                        args.temperature, args.top_p),
                               ensure_ascii=False) + "\n")
        written += 1
        stats["accepted"] += 1
        if written % 50 == 0:
            print(f"  {written} rows", file=sys.stderr)

    print(json.dumps({"written": written, "stats": dict(stats.most_common())},
                     indent=2), file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("stage", help="build the upload bundle locally (no GPU)")
    sp.add_argument("--positives-in", default=str(DEFAULT_POSITIVES))
    sp.add_argument("--prep-in", default=str(DEFAULT_PREP))
    sp.add_argument("--n-continuation", type=int, default=DEFAULT_N_CONTINUATION)
    sp.add_argument("--n-fewshot", type=int, default=DEFAULT_N_FEWSHOT)
    sp.add_argument("--length-table", default=str(DEFAULT_LENGTH_TABLE))
    sp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    sp.add_argument("--negatives-in", default=str(DEFAULT_PASSAGES / "negatives.jsonl"),
                    help="pool file scanned for sources already used elsewhere")
    sp.add_argument("--exclude-used", action="store_true", default=True,
                    help="skip sources another producer already consumed (default)")
    sp.add_argument("--allow-used", dest="exclude_used", action="store_false")
    sp.add_argument("--out", default=str(DEFAULT_INPUT))
    sp.set_defaults(func=cmd_stage)

    rp = sub.add_parser("run", help="generate (runs on Delta)")
    rp.add_argument("--input", default=str(DEFAULT_INPUT))
    rp.add_argument("--model", default=DEFAULT_MODEL)
    rp.add_argument("--temperature", type=float, default=0.9)
    rp.add_argument("--top-p", type=float, default=0.95)
    rp.add_argument("--max-new-tokens", type=int, default=160)
    rp.add_argument("--batch-size", type=int, default=8,
                    help="accepted for interface compatibility; Talkie.generate() "
                         "is one prompt at a time, so this is not yet consumed")
    rp.add_argument("--limit", type=int, default=None)
    rp.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    rp.add_argument("--dry-run", action="store_true",
                    help="assemble prompts and exercise the pipeline without "
                         "loading the checkpoint")
    rp.add_argument("--show", type=int, default=5)
    rp.add_argument("--out", default=str(DEFAULT_OUT))
    rp.add_argument("--lexicon", default=None,
                    help="MainDictionary.txt; required off the workstation, "
                         "where the default ~/Dropbox path does not exist")
    rp.add_argument("--start-line", type=int, default=0)
    rp.set_defaults(func=cmd_run)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
