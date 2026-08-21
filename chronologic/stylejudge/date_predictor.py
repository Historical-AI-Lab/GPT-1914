#!/usr/bin/env python3
"""date_predictor.py — Phase E1: lexical date predictor (binned ordinal softmax).

Builds a ridge-regularized multinomial logistic regression over tf-idf/log-count
lexical features, trained against *soft* Gaussian targets over a decade bin grid
(not one-hot labels — an 1883 passage gets a Gaussian bump over bins centered at
1883). Evaluated with CRPS (the natural generalization of MAE to a predicted
distribution) plus calibration coverage, per `new-style-judge-spec.md` §E1.

Reads `positive_passages.jsonl` (Phase D1 output; already Phase-C normalized) for
rows whose `purposes` includes `"date_predictor"` — 66,000 rows, 2,000/decade,
1700–2020. Splits are volume/author-grouped so no volume's lexical fingerprint
leaks across train/val/test.

Out of scope here (deferred, per the E1 plan): a contextual DeBERTa date
regressor, the lexical/DeBERTa disagreement feature, and cross-model conformal
fusion — this module only builds and evaluates the lexical head.

CLI
    python date_predictor.py split       [--seed N] [--out PATH]
    python date_predictor.py train       [--vocab-sizes 5000,20000,50000]
                                          [--weight-decays 1e-4,1e-3,1e-2]
                                          [--sigmas 10,15] [--feature-type tfidf|logcount]
                                          [--decades RANGE,...] [--sample-frac F]
                                          [--splits PATH] [--out-dir DIR]
                                          [--corrected-dates PATH]
    python date_predictor.py train-ridge [--vocab-sizes 5000,20000,50000]
                                          [--alphas 0.1,1,10,100,1000]
                                          [--feature-type tfidf,logcount]
                                          [--decades RANGE,...] [--sample-frac F]
                                          [--splits PATH] [--out-dir DIR]
                                          [--corrected-dates PATH]
    python date_predictor.py evaluate    --model-dir DIR [--split test|val]
                                          [--splits PATH] [--report PATH]
                                          [--corrected-dates PATH]
    python date_predictor.py score       --model-dir DIR --in PATH --out PATH

`train-ridge` fits an ordinary (untuned-softmax) Ridge regressor on the same
lexical features, grid-searched independently of the softmax model's grid, as
a plain-baseline comparison — see `stylejudge/NOTES.md` §15 follow-up and
`e1_ridge_evaluation.md`. `evaluate` accepts a model dir from either command
and reports CRPS/MAE/R2 (plus coverage for the softmax model).

`--corrected-dates PATH` (on `train`/`train-ridge`/`evaluate`) points at
situate's `full_record_list_calibrated.csv` and swaps in its `fpub_final`
metadata-matched date (not a model prediction) for `date`/`decade` wherever
`barcode`/`volume_id` match; unmatched rows keep the catalog date. On `train`/
`train-ridge` this changes what the model is fit against; on `evaluate` it
changes what predictions are scored against — the two are independent. See
`stylejudge/NOTES.md` §15 second follow-up for coverage/magnitude analysis.
"""

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_PASSAGES = (Path.home() / "workdata/chronologic-dating-corpus/passages"
                    / "positive_passages.jsonl")
DEFAULT_ROSTER = REPO_ROOT / "corpus_roster.csv"
DEFAULT_OUT_DIR = (Path.home() / "workdata/chronologic-dating-corpus/passages/e1")
DEFAULT_SPLITS = DEFAULT_OUT_DIR / "splits.json"
DEFAULT_CALIBRATED_DATES = (Path.home() / "Library/CloudStorage/Dropbox/python"
                             / "situate/wikimeta/full_record_list_calibrated.csv")

GRID_LO = 1680
GRID_HI = 2040
BIN_WIDTH = 10

DEFAULT_VOCAB_SIZES = (5000, 20000, 50000)
DEFAULT_WEIGHT_DECAYS = (1e-4, 1e-3, 1e-2)
DEFAULT_SIGMAS = (10, 15)
DEFAULT_SEED = 20260812
DEFAULT_SPLIT_FRACTIONS = (0.8, 0.1, 0.1)

CENTURY_THIRDS = ("pre1830", "core_1830_1930", "post1930")


# ---------------------------------------------------------------------------
# Bin grid, soft labels, CRPS
# ---------------------------------------------------------------------------

def build_bin_grid(lo=GRID_LO, hi=GRID_HI, width=BIN_WIDTH):
    """Return (edges, midpoints); `hi` bounds the grid, edges are inclusive of both ends."""
    edges = np.arange(lo, hi + width, width, dtype=float)
    midpoints = (edges[:-1] + edges[1:]) / 2.0
    return edges, midpoints


def date_to_bin(date, edges):
    """Bin index containing `date`; clamps out-of-range dates to the nearest edge bin."""
    idx = int(np.searchsorted(edges, date, side="right") - 1)
    return int(np.clip(idx, 0, len(edges) - 2))


def soft_label(date, sigma, midpoints):
    """Gaussian bump over bins centered at `date`, normalized to sum to 1.

    Falls back to a one-hot on the nearest bin if `date` is so far outside the grid
    that the Gaussian evaluates to all-zero in floating point — a safety net, not an
    expected code path given the grid's margin over the actual 1700-2020 data.
    """
    d = np.asarray(midpoints, dtype=float)
    probs = np.exp(-0.5 * ((d - date) / sigma) ** 2)
    total = probs.sum()
    if total <= 0.0:
        probs = np.zeros_like(d)
        probs[int(np.argmin(np.abs(d - date)))] = 1.0
        return probs
    return probs / total


def crps_binned(probs, true_bin, bin_width=BIN_WIDTH):
    """CRPS for a binned predictive distribution against the true bin.

    Reduces to `|point_bin - true_bin| * bin_width` for a degenerate (one-hot)
    `probs`, so a point-prediction baseline is directly comparable in the same units.
    """
    probs = np.asarray(probs, dtype=float)
    cdf = np.cumsum(probs)
    step = (np.arange(len(probs)) >= true_bin).astype(float)
    return float(np.sum((cdf - step) ** 2) * bin_width)


def central_interval_bins(probs, level):
    """Smallest [lo, hi] bin range whose predicted mass is symmetric around `level`."""
    probs = np.asarray(probs, dtype=float)
    cdf = np.cumsum(probs)
    alpha = (1.0 - level) / 2.0
    lo = int(np.searchsorted(cdf, alpha, side="left"))
    hi = int(np.searchsorted(cdf, 1.0 - alpha, side="left"))
    n = len(probs)
    lo = min(lo, n - 1)
    hi = min(hi, n - 1)
    return lo, hi


def coverage(probs_batch, true_bins, level):
    hits = 0
    for probs, tb in zip(probs_batch, true_bins):
        lo, hi = central_interval_bins(probs, level)
        if lo <= tb <= hi:
            hits += 1
    return hits / len(true_bins) if len(true_bins) else float("nan")


def histogram_features(probs, midpoints):
    """(mean, entropy, multimodality) per the spec's fusion-feature ask.

    `multimodality` is `1 - mass of the largest contiguous mode`: the mode is the
    monotonically non-increasing run of bins straddling the global peak; a
    concentrated, unimodal histogram scores near 0, a smeared or bimodal one scores
    higher — the "pastiche detector" property the spec asks for.
    """
    probs = np.asarray(probs, dtype=float)
    midpoints = np.asarray(midpoints, dtype=float)
    mean = float(np.sum(probs * midpoints))
    nz = probs[probs > 0]
    entropy = float(-np.sum(nz * np.log(nz))) if len(nz) else 0.0
    if probs.sum() <= 0:
        return mean, entropy, 0.0
    peak = int(np.argmax(probs))
    n = len(probs)
    left = peak
    while left > 0 and probs[left - 1] <= probs[left]:
        left -= 1
    right = peak
    while right < n - 1 and probs[right + 1] <= probs[right]:
        right += 1
    main_mass = float(probs[left:right + 1].sum())
    multimodality = 1.0 - main_mass
    return mean, entropy, multimodality


def century_third(date):
    if date < 1830:
        return "pre1830"
    if date <= 1930:
        return "core_1830_1930"
    return "post1930"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_date_predictor_rows(passages_path=DEFAULT_PASSAGES, decades=None, sample_frac=None,
                              seed=DEFAULT_SEED):
    """Rows with 'date_predictor' in purposes, optionally filtered/subsampled for a dry run."""
    decade_set = _parse_decades(decades) if decades else None
    rows = []
    with open(passages_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if "date_predictor" not in row.get("purposes", ()):
                continue
            if decade_set is not None and row["decade"] not in decade_set:
                continue
            rows.append(row)
    if sample_frac is not None and 0 < sample_frac < 1:
        rng = random.Random(seed)
        rng.shuffle(rows)
        rows = rows[:max(1, int(len(rows) * sample_frac))]
    return rows


def _parse_decades(spec):
    """'1830-1839,1900-1909' or '1830,1900' -> a set of decade values present in the data."""
    decades = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = (int(x) for x in part.split("-"))
        else:
            lo = hi = int(part)
        for d in range(lo, hi + 1):
            decades.add((d // 10) * 10)
    return decades


def load_roster_authors(roster_path=DEFAULT_ROSTER):
    authors = {}
    with open(roster_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            authors[row["volume_id"]] = (row.get("author") or "").strip()
    return authors


def load_corrected_dates(path=DEFAULT_CALIBRATED_DATES):
    """{volume_id: fpub_final} from situate's metadata-matched corrected dates.

    `fpub_final` is a metadata-triangulation estimate (Wikidata/OpenLibrary/IDI
    catalog cross-referencing), not a model prediction. `barcode` in this file
    is already uppercase with no `hvd.` prefix, matching `volume_id` directly.
    """
    corrected = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            value = row.get("fpub_final")
            if value:
                corrected[row["barcode"]] = float(value)
    return corrected


def apply_date_correction(rows, corrected):
    """Rows with a volume_id match get `date`/`decade` overwritten from `corrected`
    (the original date kept under `date_original`); unmatched rows pass through
    unchanged. Returns a new list; never mutates `rows` or its dicts in place.
    """
    out = []
    for r in rows:
        fixed_date = corrected.get(r["volume_id"])
        if fixed_date is None:
            out.append(r)
            continue
        r = dict(r)
        r["date_original"] = r["date"]
        r["date"] = fixed_date
        r["decade"] = (int(fixed_date) // 10) * 10
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------

def volume_grouped_split(rows, authors, seed=DEFAULT_SEED, fractions=DEFAULT_SPLIT_FRACTIONS):
    """{volume_id: 'train'|'val'|'test'}, grouped by author (fallback volume_id), per decade.

    Grouping and the train/val/test fractions are applied to the *group* count within
    each decade, not to passage counts — passages per volume are already capped fairly
    close together by the Phase D1 sampler, so this keeps every decade represented in
    every split without a passage-level draw that could leak a volume's vocabulary
    across the boundary.
    """
    by_decade = defaultdict(set)
    for r in rows:
        by_decade[r["decade"]].add(r["volume_id"])

    assignment = {}
    rng = random.Random(seed)
    for decade in sorted(by_decade):
        groups = defaultdict(list)
        for vid in by_decade[decade]:
            key = authors.get(vid) or vid
            groups[key].append(vid)
        keys = sorted(groups)
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
            for vid in groups[key]:
                assignment[vid] = label
    return assignment


def split_summary(rows, assignment):
    counts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        split = assignment.get(r["volume_id"], "unassigned")
        counts[r["decade"]][split] += 1
    return {str(dec): dict(v) for dec, v in sorted(counts.items())}


# ---------------------------------------------------------------------------
# Features and model
# ---------------------------------------------------------------------------

def build_vectorizer(feature_type, vocab_size):
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    kwargs = dict(max_features=vocab_size, ngram_range=(1, 2), lowercase=True,
                  token_pattern=r"(?u)\b\w+\b")
    if feature_type == "tfidf":
        return TfidfVectorizer(**kwargs)
    if feature_type == "logcount":
        return CountVectorizer(**kwargs)
    raise ValueError(f"unknown feature_type: {feature_type}")


def transform_features(vectorizer, texts, feature_type):
    X = vectorizer.transform(texts)
    if feature_type == "logcount":
        X = X.copy()
        X.data = np.log1p(X.data)
    return X


def r2_score(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")


def fit_lexical_model(X_train, Y_soft_train, n_bins, weight_decay, epochs=25, lr=0.05,
                       batch_size=256, seed=0):
    """nn.Linear(vocab_size, n_bins) + softmax, cross-entropy against soft targets, L2 = ridge."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)
    n_features = X_train.shape[1]
    model = nn.Linear(n_features, n_bins)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    y = torch.tensor(Y_soft_train, dtype=torch.float32)
    n = X_train.shape[0]
    idx = np.arange(n)
    for _ in range(epochs):
        np.random.shuffle(idx)
        for start in range(0, n, batch_size):
            batch = idx[start:start + batch_size]
            xb = torch.tensor(np.asarray(X_train[batch].todense()), dtype=torch.float32)
            yb = y[batch]
            logp = torch.log_softmax(model(xb), dim=1)
            loss = -(yb * logp).sum(dim=1).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    return model


def predict_probs(model, X, batch_size=1024, temperature=1.0):
    import torch
    n = X.shape[0]
    out = []
    with torch.no_grad():
        for start in range(0, n, batch_size):
            xb = torch.tensor(np.asarray(X[start:start + batch_size].todense()),
                               dtype=torch.float32)
            logits = model(xb)
            if temperature != 1.0:
                logits = logits / temperature
            out.append(torch.softmax(logits, dim=1).numpy())
    return np.concatenate(out, axis=0) if out else np.zeros((0, model.out_features))


# ---------------------------------------------------------------------------
# CLI: split
# ---------------------------------------------------------------------------

def cmd_split(args):
    rows = load_date_predictor_rows(Path(args.passages))
    authors = load_roster_authors(Path(args.roster))
    assignment = volume_grouped_split(rows, authors, seed=args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assignment, f)
    summary = split_summary(rows, assignment)
    print(f"wrote {out_path} ({len(assignment)} volumes, {len(rows)} rows)")
    totals = defaultdict(int)
    for dec_counts in summary.values():
        for split, n in dec_counts.items():
            totals[split] += n
    print("totals:", dict(totals))
    return 0


# ---------------------------------------------------------------------------
# CLI: train
# ---------------------------------------------------------------------------

def _parse_float_list(spec):
    return [float(x) for x in spec.split(",")]


def _parse_int_list(spec):
    return [int(float(x)) for x in spec.split(",")]


def _maybe_apply_correction(rows, corrected_dates_path):
    """Apply situate date correction if --corrected-dates was passed, else no-op."""
    if not corrected_dates_path:
        return rows
    corrected = load_corrected_dates(Path(corrected_dates_path))
    rows = apply_date_correction(rows, corrected)
    n_corrected = sum(1 for r in rows if "date_original" in r)
    print(f"corrected dates: {n_corrected}/{len(rows)} rows", file=sys.stderr)
    return rows


def cmd_train(args):
    import joblib
    from sklearn.linear_model import Ridge

    rows = load_date_predictor_rows(Path(args.passages), decades=args.decades,
                                     sample_frac=args.sample_frac, seed=args.seed)
    rows = _maybe_apply_correction(rows, args.corrected_dates)
    if not Path(args.splits).exists():
        print(f"no splits file at {args.splits} — run `split` first", file=sys.stderr)
        return 1
    with open(args.splits, encoding="utf-8") as f:
        assignment = json.load(f)

    rows_by_split = defaultdict(list)
    for r in rows:
        rows_by_split[assignment.get(r["volume_id"], "unassigned")].append(r)
    train_rows, val_rows = rows_by_split["train"], rows_by_split["val"]
    if not train_rows or not val_rows:
        print("empty train or val split for the requested --decades filter", file=sys.stderr)
        return 1

    edges, midpoints = build_bin_grid()
    n_bins = len(midpoints)
    vocab_sizes = _parse_int_list(args.vocab_sizes)
    weight_decays = _parse_float_list(args.weight_decays)
    sigmas = _parse_float_list(args.sigmas)

    train_texts = [r["text"] for r in train_rows]
    val_texts = [r["text"] for r in val_rows]
    train_dates = np.array([r["date"] for r in train_rows], dtype=float)
    val_dates = np.array([r["date"] for r in val_rows], dtype=float)
    val_bins = np.array([date_to_bin(d, edges) for d in val_dates])

    results = []
    best = None  # (mean_val_crps, vocab_size, weight_decay, sigma, vectorizer, model)
    for vocab_size in vocab_sizes:
        vectorizer = build_vectorizer(args.feature_type, vocab_size)
        vectorizer.fit(train_texts)
        X_train = transform_features(vectorizer, train_texts, args.feature_type)
        X_val = transform_features(vectorizer, val_texts, args.feature_type)
        for sigma in sigmas:
            Y_train = np.stack([soft_label(d, sigma, midpoints) for d in train_dates])
            for weight_decay in weight_decays:
                model = fit_lexical_model(X_train, Y_train, n_bins, weight_decay,
                                          epochs=args.epochs, lr=args.lr, seed=args.seed)
                val_probs = predict_probs(model, X_val)
                val_crps = float(np.mean([crps_binned(p, tb) for p, tb in
                                          zip(val_probs, val_bins)]))
                cell = dict(vocab_size=vocab_size, weight_decay=weight_decay, sigma=sigma,
                           val_crps=val_crps)
                results.append(cell)
                print(f"  vocab={vocab_size:6d} sigma={sigma:5.1f} wd={weight_decay:.0e} "
                      f"-> val_crps={val_crps:.3f}", file=sys.stderr)
                if best is None or val_crps < best[0]:
                    best = (val_crps, vocab_size, weight_decay, sigma, vectorizer, model)

    _, best_vocab, best_wd, best_sigma, _, _ = best
    print(f"best cell: vocab={best_vocab} weight_decay={best_wd} sigma={best_sigma} "
          f"val_crps={best[0]:.3f}")

    # Refit at the best cell on train+val for the final artifact.
    final_rows = train_rows + val_rows
    final_texts = [r["text"] for r in final_rows]
    final_dates = np.array([r["date"] for r in final_rows], dtype=float)
    vectorizer = build_vectorizer(args.feature_type, best_vocab)
    vectorizer.fit(final_texts)
    X_final = transform_features(vectorizer, final_texts, args.feature_type)
    Y_final = np.stack([soft_label(d, best_sigma, midpoints) for d in final_dates])
    final_model = fit_lexical_model(X_final, Y_final, n_bins, best_wd,
                                    epochs=args.epochs, lr=args.lr, seed=args.seed)

    ridge = Ridge(alpha=1.0)
    ridge.fit(X_final, final_dates)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, out_dir / "vectorizer.joblib")
    joblib.dump(ridge, out_dir / "ridge_baseline.joblib")
    import torch
    torch.save(final_model.state_dict(), out_dir / "model.pt")
    config = dict(vocab_size=best_vocab, weight_decay=best_wd, sigma=best_sigma,
                  feature_type=args.feature_type, n_bins=n_bins,
                  grid_lo=GRID_LO, grid_hi=GRID_HI, bin_width=BIN_WIDTH)
    with open(out_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    with open(out_dir / "bin_grid.json", "w", encoding="utf-8") as f:
        json.dump(dict(edges=edges.tolist(), midpoints=midpoints.tolist()), f, indent=2)
    with open(out_dir / "grid_search_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"wrote artifacts to {out_dir}")
    return 0


# ---------------------------------------------------------------------------
# CLI: train-ridge
# ---------------------------------------------------------------------------

def cmd_train_ridge(args):
    import joblib
    from sklearn.linear_model import Ridge

    rows = load_date_predictor_rows(Path(args.passages), decades=args.decades,
                                     sample_frac=args.sample_frac, seed=args.seed)
    rows = _maybe_apply_correction(rows, args.corrected_dates)
    if not Path(args.splits).exists():
        print(f"no splits file at {args.splits} — run `split` first", file=sys.stderr)
        return 1
    with open(args.splits, encoding="utf-8") as f:
        assignment = json.load(f)

    rows_by_split = defaultdict(list)
    for r in rows:
        rows_by_split[assignment.get(r["volume_id"], "unassigned")].append(r)
    train_rows, val_rows = rows_by_split["train"], rows_by_split["val"]
    if not train_rows or not val_rows:
        print("empty train or val split for the requested --decades filter", file=sys.stderr)
        return 1

    edges, midpoints = build_bin_grid()
    vocab_sizes = _parse_int_list(args.vocab_sizes)
    alphas = _parse_float_list(args.alphas)
    feature_types = [s.strip() for s in args.feature_type.split(",")]

    train_texts = [r["text"] for r in train_rows]
    val_texts = [r["text"] for r in val_rows]
    train_dates = np.array([r["date"] for r in train_rows], dtype=float)
    val_dates = np.array([r["date"] for r in val_rows], dtype=float)
    val_bins = np.array([date_to_bin(d, edges) for d in val_dates])

    results = []
    best = None  # (mean_val_crps, feature_type, vocab_size, alpha, vectorizer, ridge)
    for feature_type in feature_types:
        for vocab_size in vocab_sizes:
            vectorizer = build_vectorizer(feature_type, vocab_size)
            vectorizer.fit(train_texts)
            X_train = transform_features(vectorizer, train_texts, feature_type)
            X_val = transform_features(vectorizer, val_texts, feature_type)
            for alpha in alphas:
                ridge = Ridge(alpha=alpha)
                ridge.fit(X_train, train_dates)
                val_preds = ridge.predict(X_val)
                val_crps = float(np.mean([
                    crps_binned(_point_probs(pred, edges), tb, BIN_WIDTH)
                    for pred, tb in zip(val_preds, val_bins)
                ]))
                val_mae = float(np.mean(np.abs(val_preds - val_dates)))
                val_r2 = r2_score(val_dates, val_preds)
                cell = dict(feature_type=feature_type, vocab_size=vocab_size, alpha=alpha,
                           val_crps=val_crps, val_mae=val_mae, val_r2=val_r2)
                results.append(cell)
                print(f"  feature={feature_type:8s} vocab={vocab_size:6d} alpha={alpha:8g} "
                      f"-> val_crps={val_crps:.3f} val_mae={val_mae:.3f} val_r2={val_r2:.3f}",
                      file=sys.stderr)
                if best is None or val_crps < best[0]:
                    best = (val_crps, feature_type, vocab_size, alpha)

    _, best_feature_type, best_vocab, best_alpha = best
    print(f"best cell: feature_type={best_feature_type} vocab={best_vocab} "
          f"alpha={best_alpha} val_crps={best[0]:.3f}")

    # Refit at the best cell on train+val for the final artifact.
    final_rows = train_rows + val_rows
    final_texts = [r["text"] for r in final_rows]
    final_dates = np.array([r["date"] for r in final_rows], dtype=float)
    vectorizer = build_vectorizer(best_feature_type, best_vocab)
    vectorizer.fit(final_texts)
    X_final = transform_features(vectorizer, final_texts, best_feature_type)
    ridge = Ridge(alpha=best_alpha)
    ridge.fit(X_final, final_dates)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, out_dir / "vectorizer.joblib")
    joblib.dump(ridge, out_dir / "ridge.joblib")
    config = dict(model_type="ridge_only", vocab_size=best_vocab, alpha=best_alpha,
                  feature_type=best_feature_type,
                  grid_lo=GRID_LO, grid_hi=GRID_HI, bin_width=BIN_WIDTH)
    with open(out_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    with open(out_dir / "bin_grid.json", "w", encoding="utf-8") as f:
        json.dump(dict(edges=edges.tolist(), midpoints=midpoints.tolist()), f, indent=2)
    with open(out_dir / "grid_search_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"wrote artifacts to {out_dir}")
    return 0


# ---------------------------------------------------------------------------
# CLI: evaluate
# ---------------------------------------------------------------------------

def load_model_dir(model_dir):
    import joblib

    model_dir = Path(model_dir)
    with open(model_dir / "config.json", encoding="utf-8") as f:
        config = json.load(f)
    vectorizer = joblib.load(model_dir / "vectorizer.joblib")
    with open(model_dir / "bin_grid.json", encoding="utf-8") as f:
        grid = json.load(f)
    edges = np.array(grid["edges"])
    midpoints = np.array(grid["midpoints"])

    if config.get("model_type") == "ridge_only":
        ridge = joblib.load(model_dir / "ridge.joblib")
        return config, vectorizer, ridge, None, edges, midpoints

    import torch
    import torch.nn as nn

    ridge = joblib.load(model_dir / "ridge_baseline.joblib")
    n_features = len(vectorizer.vocabulary_)
    model = nn.Linear(n_features, config["n_bins"])
    state = torch.load(model_dir / "model.pt")
    model.load_state_dict(state)
    model.eval()
    return config, vectorizer, ridge, model, edges, midpoints


def cmd_evaluate(args):
    config, vectorizer, ridge, model, edges, midpoints = load_model_dir(args.model_dir)
    is_ridge_only = model is None

    rows = load_date_predictor_rows(Path(args.passages))
    rows = _maybe_apply_correction(rows, args.corrected_dates)
    with open(args.splits, encoding="utf-8") as f:
        assignment = json.load(f)
    eval_rows = [r for r in rows if assignment.get(r["volume_id"]) == args.split]
    if not eval_rows:
        print(f"no rows in split={args.split}", file=sys.stderr)
        return 1
    n_corrected = sum(1 for r in eval_rows if "date_original" in r)

    texts = [r["text"] for r in eval_rows]
    dates = np.array([r["date"] for r in eval_rows], dtype=float)
    true_bins = np.array([date_to_bin(d, edges) for d in dates])
    X = transform_features(vectorizer, texts, config["feature_type"])

    ridge_preds = ridge.predict(X)
    ridge_ae = np.abs(ridge_preds - dates)
    ridge_crps = np.array([
        crps_binned(_point_probs(pred, edges), tb, BIN_WIDTH)
        for pred, tb in zip(ridge_preds, true_bins)
    ])

    if not is_ridge_only:
        probs = predict_probs(model, X)
        crps_values = np.array([crps_binned(p, tb) for p, tb in zip(probs, true_bins)])

    groups = defaultdict(list)
    for i, r in enumerate(eval_rows):
        groups["overall"].append(i)
        groups[f"decade_{r['decade']}"].append(i)
        groups[century_third(r["date"])].append(i)
        groups["corrected_subset" if "date_original" in r else "catalog_only_subset"].append(i)

    title = ("E1 ridge-only date predictor" if is_ridge_only
             else "E1 lexical date predictor")
    header = (["| group | n | CRPS (ridge) | MAE (ridge) | R2 (ridge) |",
               "|---|---|---|---|---|"] if is_ridge_only else
              ["| group | n | CRPS (lexical) | CRPS (ridge) | MAE (ridge) | R2 (ridge) | "
               "coverage@50 | coverage@90 |",
               "|---|---|---|---|---|---|---|---|"])
    lines = [f"# {title} — evaluation ({args.split} split)", "",
             f"n = {len(eval_rows)}; n corrected = {n_corrected}; "
             f"model dir = `{args.model_dir}`; "
             f"config = `{json.dumps(config)}`", ""] + header
    group_order = ["overall"]
    if args.corrected_dates:
        group_order += ["corrected_subset", "catalog_only_subset"]
    group_order += ["pre1830", "core_1830_1930", "post1930"]
    for group in group_order + sorted(g for g in groups if g.startswith("decade_")):
        idx = groups.get(group, [])
        if not idx:
            continue
        idx = np.array(idx)
        r2 = r2_score(dates[idx], ridge_preds[idx])
        if is_ridge_only:
            lines.append(
                f"| {group} | {len(idx)} | {ridge_crps[idx].mean():.3f} | "
                f"{ridge_ae[idx].mean():.2f} | {r2:.3f} |")
        else:
            cov50 = coverage(probs[idx], true_bins[idx], 0.5)
            cov90 = coverage(probs[idx], true_bins[idx], 0.9)
            lines.append(
                f"| {group} | {len(idx)} | {crps_values[idx].mean():.3f} | "
                f"{ridge_crps[idx].mean():.3f} | {ridge_ae[idx].mean():.2f} | {r2:.3f} | "
                f"{cov50:.3f} | {cov90:.3f} |")

    report = "\n".join(lines) + "\n"
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")
    else:
        print(report)
    return 0


def _point_probs(point_date, edges):
    n_bins = len(edges) - 1
    probs = np.zeros(n_bins)
    probs[date_to_bin(point_date, edges)] = 1.0
    return probs


# ---------------------------------------------------------------------------
# CLI: score
# ---------------------------------------------------------------------------

def cmd_score(args):
    config, vectorizer, ridge, model, edges, midpoints = load_model_dir(args.model_dir)
    rows = []
    with open(args.in_path, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    texts = [r["text"] for r in rows]
    X = transform_features(vectorizer, texts, config["feature_type"])
    probs = predict_probs(model, X)
    with open(args.out_path, "w", encoding="utf-8") as f:
        for r, p in zip(rows, probs):
            mean, entropy, multimodality = histogram_features(p, midpoints)
            out = dict(passage_id=r.get("passage_id"), probs=p.tolist(),
                       mean=mean, entropy=entropy, multimodality=multimodality)
            f.write(json.dumps(out) + "\n")
    print(f"wrote {len(rows)} scored rows to {args.out_path}")
    return 0


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("split", help="volume/author-grouped, decade-stratified train/val/test")
    sp.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    sp.add_argument("--roster", default=str(DEFAULT_ROSTER))
    sp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    sp.add_argument("--out", default=str(DEFAULT_SPLITS))
    sp.set_defaults(func=cmd_split)

    tp = sub.add_parser("train", help="grid search + fit the lexical model and ridge baseline")
    tp.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    tp.add_argument("--splits", default=str(DEFAULT_SPLITS))
    tp.add_argument("--vocab-sizes", default=",".join(str(v) for v in DEFAULT_VOCAB_SIZES))
    tp.add_argument("--weight-decays", default=",".join(str(v) for v in DEFAULT_WEIGHT_DECAYS))
    tp.add_argument("--sigmas", default=",".join(str(v) for v in DEFAULT_SIGMAS))
    tp.add_argument("--feature-type", choices=["tfidf", "logcount"], default="tfidf")
    tp.add_argument("--decades", default=None, help="e.g. 1830-1839,1900-1909")
    tp.add_argument("--sample-frac", type=float, default=None)
    tp.add_argument("--epochs", type=int, default=25)
    tp.add_argument("--lr", type=float, default=0.05)
    tp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    tp.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR / "model"))
    tp.add_argument("--corrected-dates", default=None,
                     help="path to situate's full_record_list_calibrated.csv; "
                          "when set, train against fpub_final where available")
    tp.set_defaults(func=cmd_train)

    rp = sub.add_parser("train-ridge",
                         help="grid search + fit a plain Ridge regressor (no softmax head)")
    rp.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    rp.add_argument("--splits", default=str(DEFAULT_SPLITS))
    rp.add_argument("--vocab-sizes", default=",".join(str(v) for v in DEFAULT_VOCAB_SIZES))
    rp.add_argument("--alphas", default="0.1,1,10,100,1000")
    rp.add_argument("--feature-type", default="tfidf,logcount",
                     help="comma-separated subset of tfidf,logcount")
    rp.add_argument("--decades", default=None, help="e.g. 1830-1839,1900-1909")
    rp.add_argument("--sample-frac", type=float, default=None)
    rp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    rp.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR / "ridge_model"))
    rp.add_argument("--corrected-dates", default=None,
                     help="path to situate's full_record_list_calibrated.csv; "
                          "when set, train against fpub_final where available")
    rp.set_defaults(func=cmd_train_ridge)

    ep = sub.add_parser("evaluate", help="CRPS/MAE/R2/coverage report on a held-out split")
    ep.add_argument("--model-dir", required=True)
    ep.add_argument("--passages", default=str(DEFAULT_PASSAGES))
    ep.add_argument("--splits", default=str(DEFAULT_SPLITS))
    ep.add_argument("--split", choices=["train", "val", "test"], default="test")
    ep.add_argument("--report", default=None)
    ep.add_argument("--corrected-dates", default=None,
                     help="path to situate's full_record_list_calibrated.csv; "
                          "when set, score predictions against fpub_final where "
                          "available, and report a corrected_subset breakout")
    ep.set_defaults(func=cmd_evaluate)

    scp = sub.add_parser("score", help="emit per-passage histogram + fusion features")
    scp.add_argument("--model-dir", required=True)
    scp.add_argument("--in", dest="in_path", required=True)
    scp.add_argument("--out", dest="out_path", required=True)
    scp.set_defaults(func=cmd_score)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
