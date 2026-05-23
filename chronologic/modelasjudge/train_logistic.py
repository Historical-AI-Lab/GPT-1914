#!/usr/bin/env python3
"""train_logistic.py

Train a logistic model to distinguish anachronic pairs from ground-truth pairs
using the signed log-odds gap Δ from DeBERTa:

    logit[P(anachronic | Δ)] = β0 + β1 Δ + β2 Δ²

Features: [Δ, Δ²]   (signed Δ; intercept handled by LogisticRegression).

Note: an earlier version used |Δ| as the linear feature.  With anachronic
distractors that are LLM-generated period imitations, |Δ_anachronic| and
|Δ_gt| overlap heavily, and the |Δ| fit yielded β1 < 0 (a non-monotonic
U-shape).  The signed Δ form forces a one-sided test and produces a
monotonically increasing P(anachronic | Δ).

Reports 5-fold CV accuracy.  Final model is refit on all data and pickled.

Outputs:
  calibration/logistic_calibrator.pkl   — sklearn model + metadata
  calibration/logistic_calibrator.json  — coefficients for human inspection
  calibration/logistic_curve.png        — scatter + fitted curve

Usage:
    python modelasjudge/train_logistic.py \\
        [--anachronic PATH] [--ground-truth PATH] [--out-dir PATH]
"""

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
DEFAULT_ANACH = SCRIPT_DIR / "calibration" / "anachronic_pairs_scored.jsonl"
DEFAULT_ANACH_NOMANUAL = SCRIPT_DIR / "calibration" / "anachronic_pairs_scored_nomanual.jsonl"
DEFAULT_GT = SCRIPT_DIR / "calibration" / "ground_truth_pairs_scored.jsonl"
DEFAULT_GT_NOMANUAL = SCRIPT_DIR / "calibration" / "ground_truth_pairs_scored_nomanual.jsonl"
DEFAULT_OUT_DIR = SCRIPT_DIR / "calibration"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Train logistic calibrator for discriminative judge")
    p.add_argument("--anachronic", default=None, metavar="PATH",
                   help="Scored anachronic pairs JSONL (default depends on --nomanual)")
    p.add_argument("--ground-truth", default=None, dest="ground_truth", metavar="PATH",
                   help="Scored ground-truth pairs JSONL (default depends on --nomanual)")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), dest="out_dir", metavar="PATH")
    p.add_argument("--nomanual", action="store_true",
                   help="Use nomanual variants for inputs; write outputs with _nomanual suffix.")
    p.add_argument("--tag", default=None, metavar="TAG",
                   help="Short identifier for this calibrator (e.g. 'deberta-baseline-2026-04'). "
                        "Written into the calibrator JSON and pickle so discriminative_scoring.py "
                        "can include it in output filenames.")
    args = p.parse_args(argv)
    if args.anachronic is None:
        args.anachronic = str(DEFAULT_ANACH_NOMANUAL if args.nomanual else DEFAULT_ANACH)
    if args.ground_truth is None:
        args.ground_truth = str(DEFAULT_GT_NOMANUAL if args.nomanual else DEFAULT_GT)
    return args


def load_deltas(path: Path) -> list[float]:
    deltas = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                deltas.append(json.loads(line)["delta"])
    return deltas


def make_features(deltas: np.ndarray) -> np.ndarray:
    """Return [Δ, Δ²] feature matrix (signed Δ)."""
    return np.column_stack([deltas, deltas ** 2])


def main(argv=None):
    args = parse_args(argv)

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score

    anach_path = Path(args.anachronic)
    gt_path = Path(args.ground_truth)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not anach_path.exists():
        raise FileNotFoundError(f"Not found: {anach_path} — run build_anachronic_pairs.py first")
    if not gt_path.exists():
        raise FileNotFoundError(f"Not found: {gt_path} — run build_ground_truth_pairs.py first")

    anach_deltas = load_deltas(anach_path)
    gt_deltas = load_deltas(gt_path)

    print(f"Anachronic pairs: {len(anach_deltas):,}  (label=1)")
    print(f"Ground-truth pairs: {len(gt_deltas):,}  (label=0)")

    all_deltas = np.array(anach_deltas + gt_deltas)
    labels = np.array([1] * len(anach_deltas) + [0] * len(gt_deltas))
    X = make_features(all_deltas)

    # 5-fold CV
    clf_cv = LogisticRegression(penalty=None, solver="lbfgs", max_iter=1000)
    cv_scores = cross_val_score(clf_cv, X, labels, cv=5, scoring="accuracy")
    print(f"\n5-fold CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"  fold scores: {[round(s, 4) for s in cv_scores]}")

    # Final fit on all data
    clf = LogisticRegression(penalty=None, solver="lbfgs", max_iter=1000)
    clf.fit(X, labels)

    beta0 = float(clf.intercept_[0])
    beta1 = float(clf.coef_[0][0])
    beta2 = float(clf.coef_[0][1])
    print(f"\nFitted coefficients:")
    print(f"  β0 (intercept) = {beta0:.6f}")
    print(f"  β1 (Δ)         = {beta1:.6f}")
    print(f"  β2 (Δ²)        = {beta2:.6f}")
    train_acc = (clf.predict(X) == labels).mean()
    print(f"  Training accuracy (all data): {train_acc:.4f}")

    suffix = "_nomanual" if args.nomanual else ""

    # Pickle
    artifact = {
        "model": clf,
        "tag": args.tag,
        "feature_names": ["delta", "delta_sq"],
        "label_names": {0: "ground_truth_pair", 1: "anachronic_pair"},
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "created": datetime.now(timezone.utc).isoformat(),
        "benchmark": "chronologic-0.2",
    }
    pkl_path = out_dir / f"logistic_calibrator{suffix}.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(artifact, f)
    print(f"\nPickled calibrator → {pkl_path}")

    # JSON coefficients
    coef_path = out_dir / f"logistic_calibrator{suffix}.json"
    with open(coef_path, "w", encoding="utf-8") as f:
        json.dump({
            "tag": args.tag,
            "beta0_intercept": beta0,
            "beta1_delta": beta1,
            "beta2_delta_sq": beta2,
            "cv_accuracy_mean": float(cv_scores.mean()),
            "cv_accuracy_std": float(cv_scores.std()),
            "n_anachronic": len(anach_deltas),
            "n_ground_truth": len(gt_deltas),
            "created": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)
    print(f"Coefficients → {coef_path}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        delta_range = np.linspace(all_deltas.min() - 0.5, all_deltas.max() + 0.5, 500)
        X_curve = make_features(delta_range)
        p_curve = clf.predict_proba(X_curve)[:, 1]

        fig, ax = plt.subplots(figsize=(8, 5))
        jitter = np.random.default_rng(0).uniform(-0.02, 0.02, size=len(labels))
        ax.scatter(all_deltas[labels == 0], labels[labels == 0] + jitter[labels == 0],
                   alpha=0.2, s=6, color="steelblue", label="GT pair (label=0)")
        ax.scatter(all_deltas[labels == 1], labels[labels == 1] + jitter[labels == 1],
                   alpha=0.2, s=6, color="tomato", label="Anachronic pair (label=1)")
        ax.plot(delta_range, p_curve, color="black", lw=2, label="P(anachronic | Δ)")
        ax.axhline(0.5, color="gray", linestyle="--", lw=1)
        ax.set_xlabel("Δ = logit_b − logit_a  (signed; training uses Δ, Δ²)")
        ax.set_ylabel("P(anachronic)")
        ax.set_title(f"Discriminative calibrator  (CV acc={cv_scores.mean():.3f})")
        ax.legend()
        plt.tight_layout()
        png_path = out_dir / f"logistic_curve{suffix}.png"
        fig.savefig(png_path, dpi=150)
        plt.close(fig)
        print(f"Curve plot → {png_path}")
    except ImportError:
        print("matplotlib not available — skipping plot")


if __name__ == "__main__":
    main()
