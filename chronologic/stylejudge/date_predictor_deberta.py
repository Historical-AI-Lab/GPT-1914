#!/usr/bin/env python3
"""date_predictor_deberta.py — Phase E3: DeBERTa date-predictor wrapper.

Mirrors `authenticity_detector.py`'s division of labour — this module does data
prep, evaluation and scoring; training itself runs on Delta via
`bertclassify/train_date_deberta_A100.slurm`. See `stylejudge/phase-e3-plan.md`
Steps 3 and 6.

  split     volume/author-grouped, decade-stratified train/val/test, seeded from
            an existing E1 splits.json so the E1-vs-E3 comparison stays honest:
            any volume already assigned in E1 keeps its split; author groups
            adopt an inherited member's split; only genuinely new volumes are
            drawn fresh.
  prepare   pool + splits -> e3/{train,val,test}.jsonl (text + date + passthrough).
  evaluate  the same CRPS/MAE/R2/coverage report as `date_predictor.py evaluate`,
            side-by-side-diffable, plus a per-decade mean signed residual column
            (E1's shrinkage slope runs +28 yr @1830s to -43 yr @1930s; whether
            DeBERTa flattens it is the E3 headline). `--against-benchmarkbooks`
            scores the independent e2/benchmarkbooks_sample.jsonl instead.
  score     emits the (probs, mean, entropy, multimodality) record shape
            `date_predictor.py score` emits, so it drops into
            `typicality.score_e1` once Phase E4 wires it in. Abstains on
            sub-sentential fragments (probs: null + skip_reason).
"""

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import date_predictor as dp                                        # noqa: E402
from measure_length_distribution import is_fragment                # noqa: E402

WORKDATA = Path.home() / "workdata/chronologic-dating-corpus"
DEFAULT_PASSAGES = WORKDATA / "passages" / "date_predictor_passages_v2.jsonl"
DEFAULT_ROSTER = SCRIPT_DIR / "corpus_roster_dated.csv"
DEFAULT_INHERIT = WORKDATA / "passages" / "e1" / "splits.json"
DEFAULT_E3_DIR = WORKDATA / "passages" / "e3"
DEFAULT_SPLITS = DEFAULT_E3_DIR / "splits.json"
DEFAULT_SEED = 20260812
DEFAULT_SPLIT_FRACTIONS = (0.8, 0.1, 0.1)


# ---------------------------------------------------------------------------
# shared loaders
# ---------------------------------------------------------------------------

def load_pool(passages_path):
    return dp.load_date_predictor_rows(Path(passages_path))


def load_authors(roster_path):
    authors = {}
    with open(roster_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            authors[row["volume_id"]] = (row.get("author") or "").strip()
    return authors


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


# ---------------------------------------------------------------------------
# split (Step 3)
# ---------------------------------------------------------------------------

def inherited_grouped_split(rows, authors, inherit, seed=DEFAULT_SEED,
                            fractions=DEFAULT_SPLIT_FRACTIONS):
    """{volume_id: 'train'|'val'|'test'}, mirroring dp.volume_grouped_split but
    honouring `inherit` ({volume_id: split} from E1).

    Per decade, volumes are grouped by author (fallback volume_id). If any
    volume in a group carries an inherited assignment, the whole group adopts
    it (majority vote across the group's inherited members; ties and genuine
    disagreements are reported). Groups with no inherited member are drawn
    fresh with E1's exact fraction/min-per-split logic.
    """
    by_decade = defaultdict(lambda: defaultdict(list))
    seen = set()
    for r in rows:
        vid = r["volume_id"]
        if vid in seen:
            continue
        seen.add(vid)
        key = authors.get(vid) or vid
        by_decade[r["decade"]][key].append(vid)

    assignment = {}
    conflicts = []
    n_inherited_vols = 0
    n_fresh_vols = 0
    rng = random.Random(seed)
    for decade in sorted(by_decade):
        groups = by_decade[decade]
        fresh_keys = []
        for key in sorted(groups):
            inh = [inherit[v] for v in groups[key] if v in inherit]
            if not inh:
                fresh_keys.append(key)
                continue
            counts = Counter(inh)
            ranked = counts.most_common()
            if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
                chosen = sorted(inh)[0]
            else:
                chosen = ranked[0][0]
            if len(set(inh)) > 1:
                conflicts.append({"decade": decade, "group": key,
                                  "inherited": dict(counts), "chosen": chosen})
            for v in groups[key]:
                assignment[v] = chosen
            n_inherited_vols += len(groups[key])

        rng.shuffle(fresh_keys)
        n = len(fresh_keys)
        n_train = round(n * fractions[0])
        n_val = round(n * fractions[1])
        if n >= 3:
            n_train = min(n_train, n - 2)
            n_val = min(n_val, n - n_train - 1)
        n_test = n - n_train - n_val
        labels = ["train"] * n_train + ["val"] * n_val + ["test"] * n_test
        for key, label in zip(fresh_keys, labels):
            for v in groups[key]:
                assignment[v] = label
                n_fresh_vols += 1

    stats = {"n_volumes": len(assignment), "n_inherited": n_inherited_vols,
             "n_fresh": n_fresh_vols, "n_conflicts": len(conflicts),
             "conflicts": conflicts[:20]}
    return assignment, stats


def split_summary(rows, assignment):
    counts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        counts[r["decade"]][assignment.get(r["volume_id"], "unassigned")] += 1
    return {str(d): dict(v) for d, v in sorted(counts.items())}


def cmd_split(args):
    rows = load_pool(args.passages)
    authors = load_authors(args.roster)
    inherit = {}
    if not args.no_inherit:
        if not Path(args.inherit).exists():
            print(f"ERROR: --inherit {args.inherit} not found (pass --no-inherit "
                  f"to assign every volume fresh)", file=sys.stderr)
            return 1
        with open(args.inherit, encoding="utf-8") as f:
            inherit = json.load(f)

    assignment, stats = inherited_grouped_split(rows, authors, inherit, seed=args.seed)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assignment, f)

    totals = Counter(assignment.values())
    print(f"wrote {out_path} ({stats['n_volumes']} volumes, {len(rows)} rows)",
          file=sys.stderr)
    print(f"inherited from E1: {stats['n_inherited']}; drawn fresh: {stats['n_fresh']}; "
          f"split conflicts: {stats['n_conflicts']}", file=sys.stderr)
    for c in stats["conflicts"]:
        print(f"  conflict {c['decade']}s {c['group']!r}: {c['inherited']} -> {c['chosen']}",
              file=sys.stderr)
    print(f"totals: {dict(totals)}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# prepare (Step 6)
# ---------------------------------------------------------------------------

def cmd_prepare(args):
    rows = load_pool(args.passages)
    with open(args.splits, encoding="utf-8") as f:
        assignment = json.load(f)

    by_split = defaultdict(list)
    for r in rows:
        by_split[assignment.get(r["volume_id"], "unassigned")].append(r)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for split in ("train", "val", "test"):
        items = by_split.get(split, [])
        with open(out_dir / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for r in items:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  {split}.jsonl: {len(items)} rows", file=sys.stderr)
    if by_split.get("unassigned"):
        print(f"  WARNING: {len(by_split['unassigned'])} unassigned rows dropped",
              file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# model loading + prediction
# ---------------------------------------------------------------------------

def _resolve_device(device_arg):
    if device_arg != "auto":
        return device_arg
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def is_deberta_dir(path):
    """True if `path` is a DeBERTa (E3) run dir, False if a lexical (E1) model dir.

    A lexical dir always carries `vectorizer.joblib` (that check wins). A DeBERTa
    dir carries a HuggingFace `config.json` stamped with `date_grid_lo` (see
    `load_run_dir`), and a `model.safetensors` / `pytorch_model.bin` weight file.
    """
    path = Path(path)
    if (path / "vectorizer.joblib").exists():
        return False
    if (path / "model.safetensors").exists() or (path / "pytorch_model.bin").exists():
        return True
    cfg = path / "config.json"
    if cfg.exists():
        try:
            with open(cfg, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False
        if "date_grid_lo" in data:
            return True
    return False


def load_run_dir(run_dir):
    """Return (model, tokenizer, edges, midpoints). Bin grid + sigma live on
    model.config (train_date_deberta.py stamps them there before save)."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    run_dir = Path(run_dir)
    tokenizer = AutoTokenizer.from_pretrained(run_dir)
    model = AutoModelForSequenceClassification.from_pretrained(run_dir)
    model.eval()
    cfg = model.config
    lo = int(getattr(cfg, "date_grid_lo", dp.GRID_LO))
    hi = int(getattr(cfg, "date_grid_hi", dp.GRID_HI))
    width = int(getattr(cfg, "date_bin_width", dp.BIN_WIDTH))
    edges, midpoints = dp.build_bin_grid(lo, hi, width)
    if len(midpoints) != cfg.num_labels:
        print(f"WARNING: grid has {len(midpoints)} bins but head has "
              f"{cfg.num_labels} labels", file=sys.stderr)
    return model, tokenizer, edges, midpoints


def predict_probs(model, tokenizer, texts, edges, midpoints, temperature=1.0,
                  max_length=256, batch_size=32, device="cpu"):
    import torch
    model.to(device)
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, truncation=True,
                            max_length=max_length, return_tensors="pt").to(device)
            logits = model(**enc).logits
            if temperature != 1.0:
                logits = logits / temperature
            probs = torch.softmax(logits, dim=-1).cpu().float()
            probs = torch.nan_to_num(probs, nan=0.0)
            out.append(probs.numpy())
            # MPS leaks memory across batches with no per-batch release — an
            # uninterrupted multi-10K-row scoring call climbs past 18 GB and
            # hangs (the same failure `typicality.score_e2` chunks around).
            # Flush periodically; score() feeds this the full positive pool.
            if device == "mps" and (i // batch_size) % 50 == 49:
                torch.mps.empty_cache()
    if device == "mps":
        torch.mps.empty_cache()
    return np.concatenate(out, axis=0) if out else np.zeros((0, len(midpoints)))


def _predict_logits(model, tokenizer, texts, max_length=256, batch_size=32, device="cpu"):
    """Raw pre-softmax logits, ndarray (len(texts), n_bins). Mirrors
    `predict_probs`'s batching and the MPS per-batch cache flush (that flush is
    load-bearing — an uninterrupted multi-10K-row call climbs past 18 GB and
    hangs), but stops before the softmax so a temperature fitter can optimise
    `softmax(logits/T)` over a cached array without re-running the model."""
    import torch
    model.to(device)
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, padding=True, truncation=True,
                            max_length=max_length, return_tensors="pt").to(device)
            logits = model(**enc).logits.cpu().float().numpy()
            out.append(logits)
            if device == "mps" and (i // batch_size) % 50 == 49:
                torch.mps.empty_cache()
    if device == "mps":
        torch.mps.empty_cache()
    return np.concatenate(out, axis=0) if out else np.zeros((0, model.config.num_labels))


def _softmax(row):
    row = np.asarray(row, dtype=float)
    row = row - np.max(row)
    e = np.exp(row)
    return e / e.sum()


def _fragment_mask(texts):
    return [is_fragment(t or "") for t in texts]


def score_e1(texts, run_dir, temperature, *, device="auto", max_length=256, batch_size=32):
    """`typicality.score_e1`-shaped: list of (mean, entropy, multimodality) per
    text, with `None` at every index whose text is a sub-sentential fragment
    (E3 was trained only on complete sentences and abstains on fragments)."""
    model, tokenizer, edges, midpoints = load_run_dir(run_dir)
    dev = _resolve_device(device)
    frag = _fragment_mask(texts)
    keep_idx = [i for i, is_frag in enumerate(frag) if not is_frag]
    probs = predict_probs(model, tokenizer, [texts[i] for i in keep_idx], edges, midpoints,
                          temperature=temperature, max_length=max_length,
                          batch_size=batch_size, device=dev)
    out = [None] * len(texts)
    for k, i in enumerate(keep_idx):
        out[i] = dp.histogram_features(probs[k], midpoints)
    return out


def score_e1_with_probs(texts, run_dir, *, device="auto", max_length=256, batch_size=32):
    """(triples_or_None, logits, edges, midpoints).

    `logits` is a full-length ndarray (len(texts), n_bins) of raw pre-softmax
    logits, with an all-NaN row at each fragment index — so the invariant
    `triples[i] is None  <=>  logits[i] all-NaN` holds and both stay aligned to
    the input order. `triples` are `histogram_features(softmax(logits))` at
    T=1; a temperature fitter rescales the cached `logits` itself.
    """
    model, tokenizer, edges, midpoints = load_run_dir(run_dir)
    dev = _resolve_device(device)
    frag = _fragment_mask(texts)
    keep_idx = [i for i, is_frag in enumerate(frag) if not is_frag]
    n_bins = len(midpoints)
    kept_logits = _predict_logits(model, tokenizer, [texts[i] for i in keep_idx],
                                  max_length=max_length, batch_size=batch_size, device=dev)
    logits = np.full((len(texts), n_bins), np.nan, dtype=float)
    triples = [None] * len(texts)
    for k, i in enumerate(keep_idx):
        logits[i] = kept_logits[k]
        triples[i] = dp.histogram_features(_softmax(kept_logits[k]), midpoints)
    return triples, logits, edges, midpoints


# ---------------------------------------------------------------------------
# evaluate (Step 6)
# ---------------------------------------------------------------------------

def _eval_rows_for_split(passages, splits, split):
    rows = dp.load_date_predictor_rows(Path(passages))
    with open(splits, encoding="utf-8") as f:
        assignment = json.load(f)
    return [r for r in rows if assignment.get(r["volume_id"]) == split]


def _group_table(eval_rows, probs, edges, midpoints):
    dates = np.array([float(r["date"]) for r in eval_rows], dtype=float)
    true_bins = np.array([dp.date_to_bin(d, edges) for d in dates])
    feats = [dp.histogram_features(p, midpoints) for p in probs]
    means = np.array([f[0] for f in feats])
    crps = np.array([dp.crps_binned(p, tb) for p, tb in zip(probs, true_bins)])
    signed = means - dates
    ae = np.abs(signed)

    groups = defaultdict(list)
    for i, r in enumerate(eval_rows):
        groups["overall"].append(i)
        groups[dp.century_third(float(r["date"]))].append(i)
        groups[f"decade_{r['decade']}"].append(i)

    order = ["overall", "pre1830", "core_1830_1930", "post1930"]
    order += sorted(g for g in groups if g.startswith("decade_"))

    lines = ["| group | n | CRPS | MAE | R2 | coverage@50 | coverage@90 | "
             "mean_signed_residual |", "|---|---|---|---|---|---|---|---|"]
    for g in order:
        idx = np.array(groups.get(g, []), dtype=int)
        if idx.size == 0:
            continue
        r2 = dp.r2_score(dates[idx], means[idx])
        cov50 = dp.coverage([probs[i] for i in idx], true_bins[idx], 0.5)
        cov90 = dp.coverage([probs[i] for i in idx], true_bins[idx], 0.9)
        lines.append(f"| {g} | {idx.size} | {crps[idx].mean():.3f} | {ae[idx].mean():.2f} | "
                     f"{r2:.3f} | {cov50:.3f} | {cov90:.3f} | {signed[idx].mean():+.2f} |")
    return "\n".join(lines)


def _benchmarkbooks_block(rows, probs, edges, midpoints):
    dates = np.array([float(r["date"]) for r in rows], dtype=float)
    true_bins = [dp.date_to_bin(d, edges) for d in dates]
    means = np.array([dp.histogram_features(p, midpoints)[0] for p in probs])
    mae = float(np.mean(np.abs(means - dates)))
    crps = float(np.mean([dp.crps_binned(p, tb) for p, tb in zip(probs, true_bins)]))
    nll = float(np.mean([-np.log(max(p[tb], 1e-12)) for p, tb in zip(probs, true_bins)]))
    return mae, crps, nll


def cmd_evaluate(args):
    model, tokenizer, edges, midpoints = load_run_dir(args.run_dir)
    device = _resolve_device(args.device)
    print(f"evaluating on device={device}", file=sys.stderr)

    if args.against_benchmarkbooks:
        rows = [r for r in read_jsonl(args.against_benchmarkbooks)
                if r.get("text") and r.get("date") not in (None, "")]
        probs = predict_probs(model, tokenizer, [r["text"] for r in rows], edges,
                              midpoints, temperature=args.temperature,
                              max_length=args.max_length, batch_size=args.batch_size,
                              device=device)
        mae, crps, nll = _benchmarkbooks_block(rows, probs, edges, midpoints)
        report = "\n".join([
            "# E3 DeBERTa date predictor — benchmarkbooks",
            "",
            f"file = `{args.against_benchmarkbooks}`, n = {len(rows)}, "
            f"run-dir = `{args.run_dir}`, T = {args.temperature}",
            "",
            "| model | MAE | CRPS | NLL |",
            "|---|---|---|---|",
            f"| E3 DeBERTa | {mae:.2f} | {crps:.2f} | {nll:.3f} |",
            "| E1 lexical (catalog dates, published) | 28.43 | 30.16 | 3.448 |",
            "| E1 lexical (corrected dates, published) | 28.10 | 29.51 | 3.438 |",
            "",
            "Success criterion (b): E3 MAE beats E1's 28.10 on this same file.",
            "",
        ]) + "\n"
    else:
        eval_rows = _eval_rows_for_split(args.passages, args.splits, args.split)
        if not eval_rows:
            print(f"no rows in split={args.split}", file=sys.stderr)
            return 1
        probs = predict_probs(model, tokenizer, [r["text"] for r in eval_rows], edges,
                              midpoints, temperature=args.temperature,
                              max_length=args.max_length, batch_size=args.batch_size,
                              device=device)
        table = _group_table(eval_rows, probs, edges, midpoints)
        report = "\n".join([
            f"# E3 DeBERTa date predictor — evaluation ({args.split} split)",
            "",
            f"n = {len(eval_rows)}; run-dir = `{args.run_dir}`; T = {args.temperature}; "
            f"grid = {len(midpoints)} bins",
            "",
            "Columns and grouping match `date_predictor.py evaluate` so E1 and E3 "
            "reports diff line for line; `mean_signed_residual` (pred_mean - true_date) "
            "is the added column — E1's slope is +28 yr @1830s to -43 yr @1930s.",
            "",
            table,
            "",
        ]) + "\n"

    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"wrote {args.report}", file=sys.stderr)
    else:
        print(report)
    return 0


# ---------------------------------------------------------------------------
# score (Step 6)
# ---------------------------------------------------------------------------

def _is_fragment_row(row):
    if row.get("fragment") is True:
        return True
    text = row.get("text") or ""
    return is_fragment(text)


def cmd_score(args):
    model, tokenizer, edges, midpoints = load_run_dir(args.run_dir)
    device = _resolve_device(args.device)
    print(f"scoring on device={device}", file=sys.stderr)

    rows = list(read_jsonl(args.in_path))
    abstain = not args.no_abstain
    to_score_idx = []
    for i, r in enumerate(rows):
        if abstain and _is_fragment_row(r):
            continue
        to_score_idx.append(i)

    probs = predict_probs(model, tokenizer, [rows[i]["text"] for i in to_score_idx],
                          edges, midpoints, temperature=args.temperature,
                          max_length=args.max_length, batch_size=args.batch_size,
                          device=device)
    probs_by_idx = {idx: probs[k] for k, idx in enumerate(to_score_idx)}

    n_abstained = 0
    Path(args.out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(rows):
            pid = r.get("passage_id")
            if i not in probs_by_idx:
                n_abstained += 1
                f.write(json.dumps({"passage_id": pid, "probs": None, "mean": None,
                                    "entropy": None, "multimodality": None,
                                    "skip_reason": "fragment"}) + "\n")
                continue
            p = probs_by_idx[i]
            mean, entropy, multimodality = dp.histogram_features(p, midpoints)
            f.write(json.dumps({"passage_id": pid, "probs": p.tolist(), "mean": mean,
                                "entropy": entropy, "multimodality": multimodality}) + "\n")
    print(f"wrote {len(rows)} rows to {args.out_path} "
          f"({n_abstained} abstained on fragments)", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("split", help="volume/author-grouped split, inheriting E1's")
    sp.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    sp.add_argument("--roster", default=str(DEFAULT_ROSTER))
    sp.add_argument("--inherit", default=str(DEFAULT_INHERIT))
    sp.add_argument("--no-inherit", action="store_true",
                    help="ignore --inherit; assign every volume fresh")
    sp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    sp.add_argument("--out", default=str(DEFAULT_SPLITS))
    sp.set_defaults(func=cmd_split)

    pp = sub.add_parser("prepare", help="pool + splits -> e3/{train,val,test}.jsonl")
    pp.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    pp.add_argument("--splits", default=str(DEFAULT_SPLITS))
    pp.add_argument("--out-dir", default=str(DEFAULT_E3_DIR))
    pp.set_defaults(func=cmd_prepare)

    ep = sub.add_parser("evaluate", help="CRPS/MAE/R2/coverage + signed-residual report")
    ep.add_argument("--run-dir", required=True)
    ep.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    ep.add_argument("--splits", default=str(DEFAULT_SPLITS))
    ep.add_argument("--split", choices=["train", "val", "test"], default="test")
    ep.add_argument("--against-benchmarkbooks", default=None,
                    dest="against_benchmarkbooks",
                    help="score this jsonl (text, date) instead of a split")
    ep.add_argument("--temperature", type=float, default=1.0)
    ep.add_argument("--max-length", type=int, default=256)
    ep.add_argument("--batch-size", type=int, default=32)
    ep.add_argument("--device", default="auto")
    ep.add_argument("--report", default=None)
    ep.set_defaults(func=cmd_evaluate)

    scp = sub.add_parser("score", help="emit per-passage histogram + fusion features")
    scp.add_argument("--run-dir", required=True)
    scp.add_argument("--in", dest="in_path", required=True)
    scp.add_argument("--out", dest="out_path", required=True)
    scp.add_argument("--temperature", type=float, default=1.0)
    scp.add_argument("--max-length", type=int, default=256)
    scp.add_argument("--batch-size", type=int, default=32)
    scp.add_argument("--device", default="auto")
    scp.add_argument("--no-abstain", action="store_true",
                     help="score fragments too instead of emitting probs:null")
    scp.set_defaults(func=cmd_score)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
