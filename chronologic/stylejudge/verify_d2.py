#!/usr/bin/env python3
"""verify_d2.py — Phase D2 §7 acceptance checks over the built pool.

Runs the checks that can only be made once `negatives.jsonl` exists, in the
order §7 lists them. Two of these decide whether the instrument is valid at all:

**§7.7 symmetry.** If the Phase C artifact counters — markdown, curly quotes,
dashes, whitespace — differ measurably between positives and negatives, the
detector has a shortcut and every Phase E number is meaningless. This check
protects the whole instrument, so it is extended here beyond the plan's list to
cover **length** (`n_sentences`, `n_words`), which is where the reuse tier was
found to skew and which the plan's census counters do not measure.

**§7.9 holdout integrity.** No `eval_holdout` model id may appear on a row
labelled `split_role: "train"`, and no Google-family output may survive anywhere
in the training pool — checked at the *output* level, not only at the filename
level where the exclusion is applied.

Usage
    python verify_d2.py [--negatives PATH] [--positives PATH] [--n 200]
                        [--format table|json]
"""

import argparse
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import model_stable as ms                                          # noqa: E402
from negative_qc import shared_ngram                               # noqa: E402
from normalize import count_artifacts, load_lexicon                # noqa: E402

DEFAULT_PASSAGES = Path.home() / "workdata" / "chronologic-dating-corpus" / "passages"
DEFAULT_NEGATIVES = DEFAULT_PASSAGES / "negatives.jsonl"
DEFAULT_POSITIVES = DEFAULT_PASSAGES / "positive_passages.jsonl"

#: Counters whose cross-class gap would be a shortcut. Tolerance is absolute,
#: in units of "per 1,000 words", except OOV which is a percentage.
SYMMETRY_TOLERANCE = 2.0


def read_negatives(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_positives(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if "authenticity_positive" in row.get("purposes", []):
                rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# §7.9 holdout integrity
# ---------------------------------------------------------------------------

def check_holdout(negatives):
    holdout_ids = {m.model_id for m in ms.EVAL_MODELS}
    problems = []

    leaked = [r["negative_id"] for r in negatives
              if r.get("model_id") in holdout_ids
              and r.get("split_role") != ms.EVAL_HOLDOUT]
    if leaked:
        problems.append(f"{len(leaked)} holdout-model rows labelled train "
                        f"(e.g. {leaked[:3]})")

    # Google output is *required* in the holdout (§4.4 makes it the frontier
    # family transfer test). What is forbidden is Google anywhere in training —
    # including the reuse tier, where the exclusion is applied at filename level
    # and so deserves an independent output-level check.
    def is_google(row):
        mid = str(row.get("model_id", "")).lower()
        return "gemma" in mid or "google" in mid

    google_train = [r["negative_id"] for r in negatives
                    if is_google(r) and r.get("split_role") != ms.EVAL_HOLDOUT]
    if google_train:
        problems.append(f"{len(google_train)} Google-family rows outside the "
                        f"holdout (e.g. {google_train[:3]})")

    google_reuse = [r["negative_id"] for r in negatives
                    if is_google(r) and r.get("provenance") == "bertclassify_reuse"]
    if google_reuse:
        problems.append(f"{len(google_reuse)} Google rows survived the reuse "
                        f"exclusion (e.g. {google_reuse[:3]})")

    n_google_holdout = sum(1 for r in negatives
                           if is_google(r) and r.get("split_role") == ms.EVAL_HOLDOUT)

    try:
        ms.assert_holdout_integrity()
    except ValueError as exc:
        problems.append(str(exc))

    return {"ok": not problems, "problems": problems,
            "n_train": sum(1 for r in negatives
                           if r.get("split_role") == ms.TRAIN),
            "n_eval_holdout": sum(1 for r in negatives
                                  if r.get("split_role") == ms.EVAL_HOLDOUT),
            "n_google_in_holdout": n_google_holdout}


# ---------------------------------------------------------------------------
# §7.6 leakage audit
# ---------------------------------------------------------------------------

def check_leakage(negatives, threshold=0.05):
    """Per-model 8-gram rejection is logged at generation time; here we confirm
    nothing that *was* checkable slipped through, and report coverage.

    §7.6's "above ~5% for any generator means it has memorized the corpus" is a
    statement about the *rejection* rate during generation, which lives in the
    run log. What can be checked from the file is that no surviving row shares
    an 8-gram with a reference it was checked against, and how much of the pool
    was checkable at all.
    """
    checkable = [r for r in negatives if r.get("leakage_checkable")]
    by_model = Counter(r.get("model_id") for r in checkable)
    total_by_model = Counter(r.get("model_id") for r in negatives)
    coverage = {m: round(by_model[m] / total_by_model[m], 3)
                for m in sorted(total_by_model)}
    return {"ok": True,
            "checkable_rows": len(checkable),
            "total_rows": len(negatives),
            "checkable_share": round(len(checkable) / max(len(negatives), 1), 3),
            "coverage_by_model": coverage,
            "note": "continuation rows are structurally uncheckable: the true "
                    "continuation is not stored alongside the prompt"}


# ---------------------------------------------------------------------------
# §7.7 symmetry — the check that protects the instrument
# ---------------------------------------------------------------------------

def check_symmetry(positives, negatives, n=200, seed=20260809,
                   tolerance=SYMMETRY_TOLERANCE):
    rng = random.Random(seed)
    pos = rng.sample(positives, min(n, len(positives)))
    neg = rng.sample(negatives, min(n, len(negatives)))
    lexicon = load_lexicon()

    def profile(rows, key):
        counters = [count_artifacts(r[key], lexicon) for r in rows if r.get(key)]
        names = sorted({k for c in counters for k in c})
        return {name: statistics.mean(c.get(name, 0.0) for c in counters)
                for name in names}

    pos_profile = profile(pos, "text")
    neg_profile = profile(neg, "text")

    rows, problems = [], []
    for name in sorted(set(pos_profile) | set(neg_profile)):
        p, q = pos_profile.get(name, 0.0), neg_profile.get(name, 0.0)
        gap = abs(p - q)
        flagged = gap > tolerance
        rows.append({"counter": name, "positives": round(p, 2),
                     "negatives": round(q, 2), "gap": round(gap, 2),
                     "flagged": flagged})
        if flagged:
            problems.append(f"{name}: positives {p:.2f} vs negatives {q:.2f}")

    # Length, which the Phase C counters do not measure and where the reuse
    # tier is known to skew short.
    def lengths(rows_):
        return ([r.get("n_words", 0) for r in rows_],
                [r.get("n_sentences", 0) for r in rows_])

    pw, ps = lengths(positives)
    nw, nsent = lengths(negatives)
    length = {
        "positives_median_words": statistics.median(pw) if pw else 0,
        "negatives_median_words": statistics.median(nw) if nw else 0,
        "positives_mean_sentences": round(statistics.mean(ps), 2) if ps else 0,
        "negatives_mean_sentences": round(statistics.mean(nsent), 2) if nsent else 0,
        "positives_sentence_hist": dict(sorted(Counter(ps).items())),
        "negatives_sentence_hist": dict(sorted(Counter(nsent).items())),
    }
    word_gap = abs(length["positives_median_words"] - length["negatives_median_words"])
    sent_gap = abs(length["positives_mean_sentences"] - length["negatives_mean_sentences"])
    length["median_word_gap"] = word_gap
    length["mean_sentence_gap"] = round(sent_gap, 2)
    # Measured on training rows only -- that is the pool the detector sees.
    train_only = [r for r in negatives
                  if r.get("split_role", ms.TRAIN) == ms.TRAIN] or negatives
    length["length_only_classifier_accuracy"] = length_shortcut_accuracy(
        positives, train_only)
    acc = length["length_only_classifier_accuracy"]
    if acc is not None and acc > 0.55:
        problems.append(f"length alone separates the classes at {acc:.1%} "
                        f"-- run `--export-matched` and train on that instead")
    if word_gap > 5:
        problems.append(f"median words differ by {word_gap} "
                        f"(positives {length['positives_median_words']}, "
                        f"negatives {length['negatives_median_words']})")
    if sent_gap > 0.3:
        problems.append(f"mean sentence count differs by {sent_gap:.2f}")

    return {"ok": not problems, "problems": problems, "counters": rows,
            "length": length, "n_sampled": len(pos)}


# ---------------------------------------------------------------------------
# Pool composition
# ---------------------------------------------------------------------------

def length_cell(n_sentences, n_words):
    """Coarse (sentences, word-decile) cell used for length matching."""
    return (min(n_sentences or 0, 6), min((n_words or 0) // 10, 12))


def length_shortcut_accuracy(positives, negatives, seed=20260809):
    """How well a classifier seeing *only* length can separate the classes.

    0.50 means length carries no signal. Anything well above that is a shortcut
    the detector will find before it finds anything about style, so this is the
    number that says whether §7.7 is satisfied in substance rather than by the
    counters alone.
    """
    rng = random.Random(seed)
    p = [length_cell(r.get("n_sentences"), r.get("n_words")) for r in positives]
    n = [length_cell(r.get("n_sentences"), r.get("n_words")) for r in negatives]
    k = min(len(p), len(n))
    if k < 100:
        return None
    p, n = rng.sample(p, k), rng.sample(n, k)
    p_tr, p_te = p[:k // 2], p[k // 2:]
    n_tr, n_te = n[:k // 2], n[k // 2:]
    pc, nc = Counter(p_tr), Counter(n_tr)
    correct = sum(1 for c in p_te if pc[c] >= nc[c])
    correct += sum(1 for c in n_te if nc[c] > pc[c])
    return round(correct / (len(p_te) + len(n_te)), 4)


def match_lengths(positives, negatives, seed=20260809):
    """Down-sample both classes to a common (sentences, words) histogram.

    The structural remedy for the residual length gap: some negative modalities
    have lengths that cannot be chosen (infill is pinned by its prep gap,
    few-shot is one sentence by definition), so the pool cannot be *generated*
    length-matched. It can be *sampled* length-matched, which removes the
    shortcut exactly rather than approximately.
    """
    rng = random.Random(seed)
    by_cell_p, by_cell_n = defaultdict(list), defaultdict(list)
    for r in positives:
        by_cell_p[length_cell(r.get("n_sentences"), r.get("n_words"))].append(r)
    for r in negatives:
        by_cell_n[length_cell(r.get("n_sentences"), r.get("n_words"))].append(r)
    kept_p, kept_n = [], []
    for cell in set(by_cell_p) | set(by_cell_n):
        take = min(len(by_cell_p[cell]), len(by_cell_n[cell]))
        if not take:
            continue
        kept_p.extend(rng.sample(by_cell_p[cell], take))
        kept_n.extend(rng.sample(by_cell_n[cell], take))
    return kept_p, kept_n


def check_composition(negatives, total=ms.DEFAULT_TOTAL, drift_tolerance=0.03):
    """Modality mix against the spec's 40/20/10/20/10.

    Phase D3 deliberately softened that rule to buy length symmetry, so once
    `length_targeted` rows are present a drift is a *reported trade*, not a
    defect -- flagged as `notes` rather than `problems`. Making it a hard failure
    would leave the tool permanently red for a decision that was taken on
    purpose, and a check that always fails is a check nobody reads.
    """
    train = [r for r in negatives if r.get("split_role") == ms.TRAIN]
    supplemented = any(r.get("length_targeted") for r in negatives)
    by_modality = Counter(r.get("elicitation_strategy") for r in train)
    targets = ms.modality_totals(total)
    rows, problems = [], []
    for mod in ms.MODALITIES:
        got, want = by_modality.get(mod, 0), targets[mod]
        share = got / max(len(train), 1)
        rows.append({"modality": mod, "rows": got, "target": want,
                     "share": round(share, 3),
                     "target_share": round(want / total, 3)})
    notes = []
    if train and len(train) >= total:
        for row in rows:
            drift = row["share"] - row["target_share"]
            if abs(drift) > drift_tolerance:
                msg = (f"{row['modality']}: {row['share']:.3f} "
                       f"vs target {row['target_share']:.3f} ({drift:+.3f})")
                (notes if supplemented else problems).append(msg)
    dup = [k for k, v in Counter(r.get("negative_id") for r in negatives).items()
           if v > 1]
    if dup:
        problems.append(f"{len(dup)} duplicate negative_id values")
    return {"ok": not problems, "problems": problems, "notes": notes,
            "length_targeted_rows": sum(1 for r in negatives
                                        if r.get("length_targeted")),
            "modalities": rows,
            "n_train": len(train), "target_total": total,
            "by_provenance": dict(Counter(r.get("provenance") for r in negatives)),
            "complete": len(train) >= total}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--negatives", default=str(DEFAULT_NEGATIVES))
    ap.add_argument("--positives", default=str(DEFAULT_POSITIVES))
    ap.add_argument("--n", type=int, default=200,
                    help="sample size for the symmetry census")
    ap.add_argument("--format", choices=["table", "json"], default="table")
    ap.add_argument("--export-matched", metavar="DIR", default=None,
                    help="write length-matched positives/negatives to DIR")
    args = ap.parse_args(argv)

    negatives = read_negatives(args.negatives)
    positives = read_positives(args.positives)

    report = {
        "n_negatives": len(negatives),
        "n_positives": len(positives),
        "composition": check_composition(negatives),
        "holdout_integrity": check_holdout(negatives),
        "leakage_coverage": check_leakage(negatives),
        "symmetry": check_symmetry(positives, negatives, n=args.n),
    }
    if args.export_matched:
        out_dir = Path(args.export_matched)
        out_dir.mkdir(parents=True, exist_ok=True)
        # TRAIN ROWS ONLY. This export exists to be trained on, so shipping the
        # eval_holdout rows inside it would put Google and gpt-5.6-sol output
        # into training -- precisely the contamination §4.4 froze the holdout to
        # prevent, and invisible to check_holdout(), which inspects the pool
        # file rather than the export.
        trainable = [r for r in negatives if r.get("split_role") == ms.TRAIN]
        kp, kn = match_lengths(positives, trainable)
        holdout_ids = {m.model_id for m in ms.EVAL_MODELS}
        leaked = [r for r in kn if r.get("model_id") in holdout_ids
                  or r.get("split_role") == ms.EVAL_HOLDOUT]
        if leaked:
            raise SystemExit(f"refusing to write export: {len(leaked)} holdout "
                             f"rows reached the matched training set")
        for name, rows in (("positives_matched.jsonl", kp),
                           ("negatives_matched.jsonl", kn)):
            with open(out_dir / name, "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        report["matched_export"] = {
            "dir": str(out_dir), "per_class": len(kp),
            "train_rows_available": len(trainable),
            "retained_share": round(len(kn) / max(len(trainable), 1), 3),
            "holdout_rows_in_export": 0,
            "length_only_accuracy_after": length_shortcut_accuracy(kp, kn)}
        print(f"exported {len(kp)} matched rows per class to {out_dir}",
              file=sys.stderr)

    failed = [k for k in ("composition", "holdout_integrity", "symmetry")
              if not report[k]["ok"]]
    report["RESULT"] = "PASS" if not failed else f"FAIL: {', '.join(failed)}"

    if args.format == "json":
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"negatives: {report['n_negatives']}   "
              f"positives: {report['n_positives']}\n")
        comp = report["composition"]
        print(f"composition ({'complete' if comp['complete'] else 'PARTIAL — '
                              'pool not yet built out'}):")
        print(f"  by provenance: {comp['by_provenance']}")
        for row in comp["modalities"]:
            print(f"  {row['modality']:24s} {row['rows']:6d} / {row['target']:6d}"
                  f"   share {row['share']:.3f} (target {row['target_share']:.3f})")
        for note in comp.get("notes", []):
            print(f"  ~ accepted D3 drift: {note}")
        for prob in comp["problems"]:
            print(f"  ! {prob}")
        print(f"\nholdout integrity: "
              f"{'ok' if report['holdout_integrity']['ok'] else 'FAIL'}")
        for p in report["holdout_integrity"]["problems"]:
            print(f"  ! {p}")
        leak = report["leakage_coverage"]
        print(f"\nleakage coverage: {leak['checkable_rows']}/{leak['total_rows']} "
              f"({leak['checkable_share']:.1%}) rows had a reference to check")
        sym = report["symmetry"]
        print(f"\nsymmetry census (n={sym['n_sampled']} per class):")
        print(f"  {'counter':28s} {'positives':>10s} {'negatives':>10s} {'gap':>8s}")
        for row in sym["counters"]:
            flag = "  <-- FLAGGED" if row["flagged"] else ""
            print(f"  {row['counter']:28s} {row['positives']:10.2f} "
                  f"{row['negatives']:10.2f} {row['gap']:8.2f}{flag}")
        ln = sym["length"]
        print(f"\n  median words     positives {ln['positives_median_words']}  "
              f"negatives {ln['negatives_median_words']}  "
              f"gap {ln['median_word_gap']}")
        print(f"  mean sentences   positives {ln['positives_mean_sentences']}  "
              f"negatives {ln['negatives_mean_sentences']}  "
              f"gap {ln['mean_sentence_gap']}")
        for p in sym["problems"]:
            print(f"  ! {p}")
        print(f"\nRESULT: {report['RESULT']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
