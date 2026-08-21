#!/usr/bin/env python3
"""authenticity_detector.py — Phase E2: DeBERTa authenticity detector.

Thin wrapper around `bertclassify/train_deberta.py` (reused unmodified — a
working, Delta-verified DeBERTa fine-tuning loop) plus everything that script
doesn't do: JSONL -> TSV split preparation, a length-matched cross-generator
holdout-eval set, scoring a trained run, and a provenance-joined failure-mode
report. Per `new-style-judge-spec.md` §E2.

Trains on `$P/matched/{positives,negatives}_matched.jsonl` (`$P` =
`~/workdata/chronologic-dating-corpus/passages/`) — 29,003 rows/class, already
length-matched (Phase D2/D3) so a length-only classifier cannot separate the
classes. The cross-generator holdout (`negatives.jsonl`, `split_role ==
"eval_holdout"`, 5 models never seen in training) is scored separately, against
its own length-matched positive set (`holdout-eval-set`) — the raw holdout was
never length-matched, so scoring it against arbitrary positives would silently
reintroduce the length shortcut D2/D3 spent effort removing.

CLI
    python authenticity_detector.py prepare          [--matched-dir DIR] [--seed N]
                                                       [--roster PATH] [--out-dir DIR]
    python authenticity_detector.py holdout-eval-set [--negatives PATH] [--out-dir DIR]
                                                       [--seed N]
    python authenticity_detector.py score  --run-dir DIR --in PATH --out PATH
                                            [--max-length N] [--batch-size N] [--device D]
    python authenticity_detector.py analyze --scored PATH --records PATH
                                             [--scored-holdout PATH] [--records-holdout PATH]
                                             [--report PATH]

Training itself is not a subcommand here — run `bertclassify/train_deberta.py`
directly against the TSVs `prepare` writes (see `phase-e2-runbook.md`).
"""

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import model_stable as ms                                          # noqa: E402
import passage_filters                                             # noqa: E402
import verify_d2                                                   # noqa: E402
from normalize import load_lexicon                                 # noqa: E402

DEFAULT_PASSAGES = Path.home() / "workdata/chronologic-dating-corpus/passages"
DEFAULT_MATCHED_DIR = DEFAULT_PASSAGES / "matched"
DEFAULT_NEGATIVES = DEFAULT_PASSAGES / "negatives.jsonl"
DEFAULT_ROSTER = SCRIPT_DIR / "corpus_roster.csv"
DEFAULT_OUT_DIR = DEFAULT_PASSAGES / "e2"
DEFAULT_SPLITS = DEFAULT_OUT_DIR / "splits.json"

DEFAULT_SEED = 20260812
DEFAULT_SPLIT_FRACTIONS = (0.8, 0.1, 0.1)

LABEL_AUTHENTIC = 0
LABEL_SYNTHETIC = 1


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_matched(matched_dir=DEFAULT_MATCHED_DIR):
    matched_dir = Path(matched_dir)
    positives = list(read_jsonl(matched_dir / "positives_matched.jsonl"))
    negatives = list(read_jsonl(matched_dir / "negatives_matched.jsonl"))
    return positives, negatives


def load_roster_authors(roster_path=DEFAULT_ROSTER):
    authors = {}
    with open(roster_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            authors[row["volume_id"]] = (row.get("author") or "").strip()
    return authors


def load_eval_holdout(negatives_path=DEFAULT_NEGATIVES):
    return [r for r in read_jsonl(negatives_path)
            if r.get("split_role") == ms.EVAL_HOLDOUT]


def row_id_of(row):
    return row.get("passage_id") or row.get("negative_id")


# ---------------------------------------------------------------------------
# Grouped, decade-stratified split spanning both classes
# ---------------------------------------------------------------------------
#
# A paraphrase or infill negative shares near-identical content with its
# positive source passage, so the grouping key must tie the two classes
# together: positives group by `volume_id`, negatives by `source_volume_id` —
# always present, including for `talkie_local` rows, whose "source" is a
# positive passage rather than a fixed volume span. Author-grouping (via the
# roster) then keeps one author's several volumes in the same split, exactly
# as `date_predictor.py`'s E1 split does. The 102 `bertclassify_reuse`
# dup-source infill pairs (NOTES.md §16) inherit the same split automatically,
# since two generators answering the same source volume share a group key —
# no special case needed, just tested.

def content_volume_id(row, is_positive):
    return row["volume_id"] if is_positive else row.get("source_volume_id")


def row_decade(row, is_positive):
    return row["decade"] if is_positive else row.get("source_decade")


def build_group_key(row, is_positive, authors):
    vid = content_volume_id(row, is_positive)
    return authors.get(vid) or vid or row_id_of(row)


def grouped_split(positives, negatives, authors, seed=DEFAULT_SEED,
                  fractions=DEFAULT_SPLIT_FRACTIONS):
    by_decade = defaultdict(set)
    for r in positives:
        by_decade[row_decade(r, True)].add(build_group_key(r, True, authors))
    for r in negatives:
        by_decade[row_decade(r, False)].add(build_group_key(r, False, authors))

    assignment = {}
    rng = random.Random(seed)
    for decade in sorted(k for k in by_decade if k is not None):
        keys = sorted(by_decade[decade])
        rng.shuffle(keys)
        n = len(keys)
        n_train = round(n * fractions[0])
        n_val = round(n * fractions[1])
        if n >= 3:
            n_train = min(n_train, n - 2)
            n_val = min(n_val, n - n_train - 1)
        n_test = n - n_train - n_val
        labels = ["train"] * n_train + ["val"] * n_val + ["test"] * n_test
        for key, label in zip(keys, labels):
            assignment[key] = label
    return assignment


def assign_split(row, is_positive, assignment, authors):
    key = build_group_key(row, is_positive, authors)
    return assignment.get(key, "unassigned")


def split_summary(positives, negatives, assignment, authors):
    counts = defaultdict(lambda: defaultdict(int))
    for r in positives:
        counts["positive"][assign_split(r, True, assignment, authors)] += 1
    for r in negatives:
        counts["negative"][assign_split(r, False, assignment, authors)] += 1
    return {k: dict(v) for k, v in counts.items()}


# ---------------------------------------------------------------------------
# CLI: prepare
# ---------------------------------------------------------------------------

def _tsv_safe(text):
    return text.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def cmd_prepare(args):
    positives, negatives = load_matched(Path(args.matched_dir))
    authors = load_roster_authors(Path(args.roster))
    assignment = grouped_split(positives, negatives, authors, seed=args.seed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "splits.json", "w", encoding="utf-8") as f:
        json.dump(assignment, f)

    labeled = ([(r, LABEL_AUTHENTIC, True) for r in positives]
              + [(r, LABEL_SYNTHETIC, False) for r in negatives])
    by_split = defaultdict(list)
    for row, label, is_pos in labeled:
        by_split[assign_split(row, is_pos, assignment, authors)].append(
            (row, label, is_pos))

    for split in ("train", "val", "test"):
        items = by_split.get(split, [])
        with open(out_dir / f"{split}.tsv", "w", encoding="utf-8") as f:
            f.write("text\tlabel\trow_id\n")
            for row, label, _ in items:
                f.write(f"{_tsv_safe(row['text'])}\t{label}\t{row_id_of(row)}\n")
        if split == "test":
            with open(out_dir / "test.jsonl", "w", encoding="utf-8") as f:
                for row, label, is_pos in items:
                    out = dict(row)
                    out["label"] = label
                    out["row_id"] = row_id_of(row)
                    out["is_positive"] = is_pos
                    f.write(json.dumps(out, ensure_ascii=False) + "\n")

    summary = split_summary(positives, negatives, assignment, authors)
    print(f"wrote splits + TSVs to {out_dir}")
    print(json.dumps(summary, indent=2))
    return 0


# ---------------------------------------------------------------------------
# CLI: holdout-eval-set
# ---------------------------------------------------------------------------

def cmd_holdout_eval_set(args):
    test_path = Path(args.out_dir) / "test.jsonl"
    if not test_path.exists():
        print(f"no {test_path} — run `prepare` first", file=sys.stderr)
        return 1
    test_positives = [r for r in read_jsonl(test_path) if r.get("is_positive")]
    eval_holdout_negs = load_eval_holdout(Path(args.negatives))
    if not test_positives or not eval_holdout_negs:
        print("empty test-positive or eval_holdout set", file=sys.stderr)
        return 1

    kp, kn = verify_d2.match_lengths(test_positives, eval_holdout_negs, seed=args.seed)

    out_path = Path(args.out_dir) / "holdout.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for row in kp:
            out = dict(row)
            out.update(label=LABEL_AUTHENTIC, row_id=row_id_of(row), is_positive=True)
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
        for row in kn:
            out = dict(row)
            out.update(label=LABEL_SYNTHETIC, row_id=row_id_of(row), is_positive=False)
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(f"wrote {len(kp)} positive + {len(kn)} negative length-matched holdout "
          f"rows to {out_path} (from {len(test_positives)} test positives, "
          f"{len(eval_holdout_negs)} eval_holdout negatives)")
    return 0


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def load_run(run_dir):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(run_dir)
    model = AutoModelForSequenceClassification.from_pretrained(run_dir)
    model.eval()
    return model, tokenizer


def resolve_device(device_arg):
    """cuda > mps > cpu, mirroring train_deberta.py's select_device().

    Inference-only (no optimizer step), so the Adam-eps NaN bug that forced
    training onto explicit --device cpu/cuda does not apply here — there is no
    backward pass or parameter update, so MPS is safe to use for scoring.
    """
    if device_arg != "auto":
        return device_arg
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def score_texts(model, tokenizer, texts, max_length=256, batch_size=32, device="cpu"):
    """Return p(label=1) = p(synthetic) per text, sigmoid of the single logit."""
    import torch

    model.to(device)
    probs = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, truncation=True,
                            max_length=max_length, return_tensors="pt").to(device)
            logits = model(**enc).logits.squeeze(-1)
            probs.extend(torch.sigmoid(logits).cpu().tolist())
    return probs


def cmd_score(args):
    model, tokenizer = load_run(args.run_dir)
    device = resolve_device(args.device)
    print(f"scoring on device={device}", file=sys.stderr)

    rows = list(read_jsonl(args.in_path))
    texts = [r["text"] for r in rows]
    probs_synthetic = score_texts(model, tokenizer, texts, max_length=args.max_length,
                                  batch_size=args.batch_size, device=device)

    Path(args.out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_path, "w", encoding="utf-8") as f:
        for row, p in zip(rows, probs_synthetic):
            out = {"row_id": row.get("row_id") or row_id_of(row),
                  "label": row.get("label"), "p_synthetic": p, "p_authentic": 1.0 - p}
            f.write(json.dumps(out) + "\n")
    print(f"scored {len(rows)} rows -> {args.out_path}")
    return 0


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(labels, probs):
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

    labels = np.asarray(labels)
    probs = np.asarray(probs, dtype=float)
    preds = (probs >= 0.5).astype(int)
    acc = float(accuracy_score(labels, preds))
    f1 = float(f1_score(labels, preds, zero_division=0))
    if len(set(labels.tolist())) > 1:
        try:
            auroc = float(roc_auc_score(labels, probs))
        except ValueError:
            auroc = float("nan")
    else:
        auroc = float("nan")
    return {"n": int(len(labels)), "accuracy": round(acc, 4), "f1": round(f1, 4),
            "auroc": round(auroc, 4) if auroc == auroc else None}


def slice_metrics(rows, key_fn, min_n=5):
    groups = defaultdict(list)
    for r in rows:
        groups[key_fn(r)].append(r)
    out = []
    for key in sorted(groups, key=lambda k: (-len(groups[k]), str(k))):
        grp = groups[key]
        if len(grp) < min_n:
            continue
        m = compute_metrics([r["label"] for r in grp], [r["p_synthetic"] for r in grp])
        out.append({"slice": key, **m})
    return out


def model_family(model_id):
    if not model_id:
        return "unknown"
    spec = ms.by_id(model_id)
    if spec:
        return spec.family
    if "talkie" in model_id:
        return "talkie"
    return "unknown"


def oov_shortcut_probe(rows, min_n=20):
    """Within-class Spearman correlation of OOV fraction vs. detector p(synthetic).

    Pooling both classes would just reproduce the (real, desired) label signal,
    since OOV differs systematically between authentic and synthetic text
    (OCR noise vs. none). Computing the correlation *within* each true class
    isolates OOV variation from the label and asks the sharper question: among
    texts that are all authentic (or all synthetic), does more OOV nudge the
    score toward "authentic"? A near-zero within-class rho is the evidence the
    detector is not using OOV as a shortcut.
    """
    from scipy.stats import spearmanr

    lexicon = load_lexicon()
    out = {}
    for name, label in (("authentic", LABEL_AUTHENTIC), ("synthetic", LABEL_SYNTHETIC)):
        grp = [r for r in rows if r.get("label") == label]
        if len(grp) < min_n:
            out[name] = None
            continue
        oov = [passage_filters.oov_fraction(r["text"], lexicon) for r in grp]
        p = [r["p_synthetic"] for r in grp]
        if len(set(oov)) < 2 or len(set(p)) < 2:
            out[name] = None
            continue
        rho, pval = spearmanr(oov, p)
        out[name] = {"rho": round(float(rho), 4), "p_value": round(float(pval), 4),
                    "n": len(grp)}
    return out


# ---------------------------------------------------------------------------
# CLI: analyze
# ---------------------------------------------------------------------------

def join_scored(records_path, scored_path):
    records = {r.get("row_id") or row_id_of(r): r for r in read_jsonl(records_path)}
    out = []
    for s in read_jsonl(scored_path):
        rec = records.get(s["row_id"])
        if rec is None:
            continue
        row = dict(rec)
        row["p_synthetic"] = s["p_synthetic"]
        row["p_authentic"] = s["p_authentic"]
        out.append(row)
    return out


def _md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def _slice_table_lines(title, rows, key_fn):
    slices = slice_metrics(rows, key_fn)
    if not slices:
        return [f"### {title}", "", "(no slice cleared the n>=5 floor)", ""]
    body = [[s["slice"], s["n"], s["accuracy"], s["f1"],
            s["auroc"] if s["auroc"] is not None else "n/a"] for s in slices]
    return [f"### {title}", "",
           _md_table(["slice", "n", "accuracy", "f1", "auroc"], body), ""]


def build_report(test_rows, holdout_rows):
    lines = ["# E2 authenticity detector — evaluation", ""]

    overall = compute_metrics([r["label"] for r in test_rows],
                              [r["p_synthetic"] for r in test_rows])
    lines += [f"## Test split (n={overall['n']})", "",
             f"accuracy **{overall['accuracy']}**, f1 {overall['f1']}, "
             f"auroc {overall['auroc']}", ""]

    neg_rows = [r for r in test_rows if r["label"] == LABEL_SYNTHETIC]
    pos_rows = [r for r in test_rows if r["label"] == LABEL_AUTHENTIC]

    lines += _slice_table_lines("By elicitation strategy (negatives)", neg_rows,
                                lambda r: r.get("elicitation_strategy"))
    lines += _slice_table_lines("By generator family (negatives)", neg_rows,
                                lambda r: model_family(r.get("model_id")))
    lines += _slice_table_lines("By source decade (negatives)", neg_rows,
                                lambda r: r.get("source_decade"))
    lines += _slice_table_lines("By length cell (negatives)", neg_rows,
                                lambda r: verify_d2.length_cell(r.get("n_sentences"),
                                                                r.get("n_words")))
    lines += _slice_table_lines("By date_in_prompt (negatives)", neg_rows,
                                lambda r: r.get("date_in_prompt"))
    lines += _slice_table_lines("By prompt_variant (negatives)", neg_rows,
                                lambda r: r.get("prompt_variant"))
    lines += _slice_table_lines("By provenance (negatives)", neg_rows,
                                lambda r: r.get("provenance"))

    lines += ["### False positives — authentic text flagged as synthetic", ""]
    fp_slices = slice_metrics(pos_rows, lambda r: r.get("collection"))
    # slice_metrics reports accuracy (fraction correctly labelled authentic);
    # false-positive rate is 1 - accuracy on the positive class alone.
    body = [[s["slice"], s["n"], round(1 - s["accuracy"], 4)] for s in fp_slices]
    lines += [_md_table(["collection", "n", "false_positive_rate"], body), ""]

    talkie = [r for r in neg_rows if r.get("provenance") == "talkie_local"]
    if talkie:
        m = compute_metrics([r["label"] for r in talkie], [r["p_synthetic"] for r in talkie])
        lines += ["### Flagged: Talkie continuation rows (memorization unverified, "
                 "NOTES §16)", "",
                 f"n={m['n']}, detection accuracy {m['accuracy']} "
                 "(a low number here is ambiguous — could be genuine detector "
                 "weakness, or a Talkie row wearing a positive's label)", ""]

    probe = oov_shortcut_probe(test_rows)
    lines += ["### OOV shortcut probe (within-class Spearman rho, oov_fraction vs. "
             "p_synthetic)", "", json.dumps(probe, indent=2), "",
             "Near zero in both classes is the expected, non-shortcut result.", ""]

    if holdout_rows:
        hold = compute_metrics([r["label"] for r in holdout_rows],
                               [r["p_synthetic"] for r in holdout_rows])
        lines += ["## Cross-generator holdout (length-matched, 5 unseen model families)",
                 "", f"accuracy **{hold['accuracy']}**, f1 {hold['f1']}, "
                 f"auroc {hold['auroc']}  (n={hold['n']})", "",
                 f"Transfer gap vs. test: accuracy {overall['accuracy']} -> "
                 f"{hold['accuracy']} ({hold['accuracy'] - overall['accuracy']:+.4f})", ""]
        by_model = slice_metrics([r for r in holdout_rows if r["label"] == LABEL_SYNTHETIC],
                                 lambda r: r.get("model_id"))
        body = [[s["slice"], s["n"], s["accuracy"]] for s in by_model]
        lines += ["### Holdout detection accuracy by held-out model", "",
                 _md_table(["model_id", "n", "accuracy"], body), ""]

    return "\n".join(lines) + "\n"


def cmd_analyze(args):
    test_rows = join_scored(args.records, args.scored)
    holdout_rows = (join_scored(args.records_holdout, args.scored_holdout)
                    if args.scored_holdout and args.records_holdout else [])
    report = build_report(test_rows, holdout_rows)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")
    else:
        print(report)
    return 0


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    pp = sub.add_parser("prepare", help="matched jsonl -> grouped split -> TSVs")
    pp.add_argument("--matched-dir", default=str(DEFAULT_MATCHED_DIR))
    pp.add_argument("--roster", default=str(DEFAULT_ROSTER))
    pp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    pp.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    pp.set_defaults(func=cmd_prepare)

    hp = sub.add_parser("holdout-eval-set",
                        help="length-matched cross-generator holdout eval pair")
    hp.add_argument("--negatives", default=str(DEFAULT_NEGATIVES))
    hp.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    hp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    hp.set_defaults(func=cmd_holdout_eval_set)

    scp = sub.add_parser("score", help="run a trained checkpoint over a jsonl file")
    scp.add_argument("--run-dir", required=True)
    scp.add_argument("--in", dest="in_path", required=True)
    scp.add_argument("--out", dest="out_path", required=True)
    scp.add_argument("--max-length", type=int, default=256)
    scp.add_argument("--batch-size", type=int, default=32)
    scp.add_argument("--device", default="auto")
    scp.set_defaults(func=cmd_score)

    ap2 = sub.add_parser("analyze", help="provenance-joined failure-mode report")
    ap2.add_argument("--scored", required=True)
    ap2.add_argument("--records", default=str(DEFAULT_OUT_DIR / "test.jsonl"))
    ap2.add_argument("--scored-holdout", default=None)
    ap2.add_argument("--records-holdout", default=str(DEFAULT_OUT_DIR / "holdout.jsonl"))
    ap2.add_argument("--report", default=None)
    ap2.set_defaults(func=cmd_analyze)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
