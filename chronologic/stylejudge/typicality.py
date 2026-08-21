#!/usr/bin/env python3
"""typicality.py — Phase F: model-level conformal calibration on the RPS.

See phase-f-plan.md (and the frolicking-treehouse plans it supersedes).
Builds the Reference Prediction Set (RPS) by scoring `calibration_corpus.py`'s
output through frozen E1 (`date_predictor.py`) and E2 (`authenticity_detector.py`),
then (in later subcommands, not yet implemented) turns per-answer scores into
per-passage conformal q's and model-level typicality statistics.

CLI
    python typicality.py fit-length-bins --reference reference_scored.jsonl
                                          [--n-bins 6] [--out length_bin_edges.json]
    python typicality.py score-reference --calibration PATH
                                          --e1-model-dir DIR --e2-run-dir DIR
                                          [--temperature-fit e1_temperature_fit.json]
                                          [--batch-size N] [--max-length N] [--device D]
                                          [--out reference_scored.jsonl]
    python typicality.py qscore          --reference reference_scored.jsonl --answers ANSWERS.jsonl
                                          --e1-model-dir DIR --e2-run-dir DIR
                                          [--temperature-fit e1_temperature_fit.json]
                                          [--length-bin-edges length_bin_edges.json]
                                          [--h 10] [--batch-size N] [--max-length N] [--device D]
                                          [--out answers_q.jsonl]
    python typicality.py verify          --reference reference_scored.jsonl
                                          [--length-bin-edges length_bin_edges.json]
                                          [--h 10] [--step 5] [--lovo-out PATH] [--report OUT.md]
    python typicality.py model-report    --answers-q answers_q.jsonl --reference reference_scored.jsonl
                                          [--length-bin-edges length_bin_edges.json]
                                          [--h 10] [--n-null 2000] [--n-boot 1000] [--seed N]
                                          [--fusion-method hmp|max|cct]
                                          [--report OUT.md] [--stats-out PATH] [--boot-out PATH]

`fit-length-bins` fits frozen quantile cut points on `log(n_words)` over the full RPS (positives
only — same spirit as T*, never refit on answers) and is the length analogue of
`e1_temperature_fit.json`. Every other subcommand that touches a q — `qscore`, `verify`,
`model-report` — conditions its reference window on the candidate's own length bin (from these
frozen edges) *in addition to* the existing date window, not just date alone. This replaces an
earlier length-blind design: `verify` found E1's q's length-dependent (frac≤0.5 by tercile:
0.351 low / 0.664 high — short passages read spuriously modern, long ones spuriously archaic),
and a follow-up review confirmed the effect is real (though a specific proposed causal story about
it didn't hold up under a length-vs-T_drift check) and large enough to condition on directly
rather than leave to the pseudo-model null to quietly correct for.

`score-reference` imports E1's and E2's library functions directly (no
shelling out) — `date_predictor.load_model_dir`/`transform_features`/
`predict_probs`/`histogram_features` and `authenticity_detector.load_run`/
`score_texts` — producing one RPS row per calibration passage: `passage_id`,
`volume_id`, `date`, `decade`, `source_tier`, `n_words`, `n_sentences`,
`e1_mean` (at T* from `--temperature-fit`, frozen — never refit here),
`e1_entropy`, `e1_multimodality` (diagnostic columns only, per rev.2 §2-3),
`e1_signed_residual` (`e1_mean - date`, the reference quantity the E1 q-score
windows against), and `e2_p_synthetic`.

`qscore` scores real benchmark answers the same way and turns them into
per-passage conformal q's against the RPS. `--answers` is a JSONL of the
`diagnose_e1_stats.py sample-benchmark-answers` output (`row_id`, `model`,
`source_file`, `question_number`, `text`, `true_date`) — reused rather than
reimplementing the generated-answers-to-source_date join. `question_number`
is carried through to the output unchanged: it is the *shared* item id
(the same question asked of every model), distinct from `row_id` (which is
model-scoped) — the two-way bootstrap's item-clustering (rev.2 §6, corrected
per phase-f-plan.md) must group by the former, never the latter.

`verify` computes each RPS row's own-date, leave-one-volume-out q's (no model
inference — pure percentile computation over already-scored fields, now
length-conditioned like everything else) and sweeps target dates across the
corpus in `--step`-year increments, reporting per-window uniformity
(KS + frac≤0.1/0.5, both channels) and a pooled per-length-bin breakdown —
the direct check for whether length-conditioning actually flattened the
frac≤0.5 skew the old pooled-tercile check found. Per rev.2 §5's coherence
point, these are the same LOVO q's pseudo-model null simulation reuses
unchanged.

`model-report` groups `qscore`'s answers by `model`, computes T_drift/T_disp/
T_E2/T_KS (rev.2 §4), builds each statistic's empirical null from B
volume-blocked, date/length-matched pseudo-models drawn from the RPS's own
precomputed own-date LOVO q's (rev.2 §5 — own-date targeting is why those q's
transfer unchanged into the null rather than needing rescoring), and reports
a two-way bootstrap CI (rev.2 §6: item-clustered by `question_number` *and*
volume-clustered reference resampling, simultaneously per draw, shared across
all models in one pass for tractability). Length-conditioning now lives in
the q computation itself, so T_drift/T_disp are directly comparable across
models without needing to mentally subtract out a length confound.

`model-report` is the older multi-model/legacy cohort-wide path (`fused_score`'s
T_KS/T_E2 combination and its own report table). The current per-candidate scoring
path is `score_style.py`, which reuses this module's `W1`
(`wasserstein1_uniform`), `e1_period_fidelity`, `e2_authenticity_fidelity`, and
`empirical_quantile_grid` to report two 0-100 headline scores — **Period
Fidelity** (W1-based) and **Authenticity Fidelity** — with W1 now the E1
headline distance and T_KS demoted to a compatibility diagnostic (an omnibus
statistic that subsumes T_drift/T_disp into one number but can't decompose
which one is driving it). See `modelasjudge/plan-wire-in-style-judge.md` and
`StyleJudgeGuide.md`'s "Scoring one candidate end-to-end".
"""

import argparse
import json
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from sample_passages import read_jsonl, write_jsonl               # noqa: E402
from measure_length_distribution import count_words                # noqa: E402
import date_predictor as dp                                        # noqa: E402
import authenticity_detector as ad                                 # noqa: E402

DEFAULT_CALIBRATION = (Path.home() / "workdata" / "chronologic-dating-corpus"
                        / "calibration_passages.jsonl")
DEFAULT_E1_MODEL_DIR = (Path.home() / "workdata" / "chronologic-dating-corpus"
                         / "passages" / "e1" / "model")
DEFAULT_E2_RUN_DIR = REPO_ROOT / "bertclassify" / "model_output" / "e2_v1"
DEFAULT_TEMPERATURE_FIT = SCRIPT_DIR / "e1_temperature_fit.json"
DEFAULT_REFERENCE_OUT = (Path.home() / "workdata" / "chronologic-dating-corpus"
                          / "calibration_reference_scored.jsonl")
DEFAULT_LENGTH_BIN_EDGES = SCRIPT_DIR / "length_bin_edges.json"
DEFAULT_N_LENGTH_BINS = 6


def load_temperature(path):
    """T*_nll from e1_temperature_fit.json — frozen, never refit against the
    calibration corpus (per rev.2 §"no parameter of the scoring instrument,
    including T*, is ever fit on negatives or on benchmark answers")."""
    with open(path, encoding="utf-8") as f:
        fit = json.load(f)
    return float(fit["t_nll"])


def fit_length_bin_edges(reference_rows, n_bins=DEFAULT_N_LENGTH_BINS):
    """`n_bins - 1` interior quantile cut points on log(n_words), fit once over
    the full RPS (positives only — same spirit as T*, frozen and never refit
    against answers). Returns a plain ascending list of floats.
    """
    logs = sorted(math.log(max(r.get("n_words") or 1, 1)) for r in reference_rows)
    n = len(logs)
    return [logs[min(round(n * i / n_bins), n - 1)] for i in range(1, n_bins)]


def length_bin(n_words, edges):
    """Bin index (0..len(edges)) for `n_words`, via frozen interior cut points
    on log(n_words). `edges=[]` degenerates to a single bin (index 0 always)
    — i.e. no length-conditioning, the pre-length-conditioning behavior."""
    x = math.log(max(n_words or 1, 1))
    idx = 0
    for cut in edges:
        if x >= cut:
            idx += 1
        else:
            break
    return idx


def load_length_bin_edges(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["edges"]


def annotate_length_bins(rows, edges):
    """Mutates `rows` in place, adding a `length_bin` field to each — computed
    once globally so every window lookup downstream is a cheap field
    comparison instead of a repeated log/compare per row per window.
    """
    for r in rows:
        r["length_bin"] = length_bin(r.get("n_words") or 1, edges)
    return rows


def cmd_fit_length_bins(args):
    reference_rows = read_jsonl(args.reference)
    edges = fit_length_bin_edges(reference_rows, args.n_bins)
    Path(args.out).write_text(
        json.dumps({"n_bins": args.n_bins, "edges": edges}, indent=2), encoding="utf-8")
    print(f"wrote {args.n_bins}-bin length edges (log n_words) to {args.out}: "
          f"{[round(e, 3) for e in edges]}", file=sys.stderr)


def score_e1(texts, e1_model_dir, temperature):
    config, vectorizer, _ridge, model, _edges, midpoints = dp.load_model_dir(e1_model_dir)
    X = dp.transform_features(vectorizer, texts, config["feature_type"])
    probs = dp.predict_probs(model, X, temperature=temperature)
    return [dp.histogram_features(p, midpoints) for p in probs]


def score_e2(texts, e2_run_dir, max_length, batch_size, device, chunk_size=1000):
    """Chunked wrapper around `authenticity_detector.score_texts`.

    Two reasons to chunk rather than call it once over all 43K texts: (1) MPS
    inference was observed to leak memory across batches with no per-batch
    release (18GB+ and climbing, eventually a "stuck" process, on a single
    uninterrupted `score_texts` call) — `torch.mps.empty_cache()` after every
    chunk keeps that bounded; (2) `score_texts` has no internal progress
    output, so a silent multi-minute call is indistinguishable from a hang.
    """
    model, tokenizer = ad.load_run(e2_run_dir)
    device = ad.resolve_device(device)
    print(f"  E2 scoring on device={device}, {len(texts)} texts, "
          f"chunk_size={chunk_size}", file=sys.stderr)

    probs = []
    for start in range(0, len(texts), chunk_size):
        chunk = texts[start:start + chunk_size]
        probs.extend(ad.score_texts(model, tokenizer, chunk, max_length=max_length,
                                     batch_size=batch_size, device=device))
        print(f"    {min(start + chunk_size, len(texts))}/{len(texts)} scored",
              file=sys.stderr)
        if device == "mps":
            import torch
            torch.mps.empty_cache()
    return probs


def cmd_score_reference(args):
    rows = read_jsonl(args.calibration)
    print(f"  loaded {len(rows)} calibration passages", file=sys.stderr)
    texts = [r["text"] for r in rows]

    temperature = load_temperature(args.temperature_fit)
    print(f"  E1 scoring at T*={temperature:.4f} ({args.e1_model_dir})", file=sys.stderr)
    e1_features = score_e1(texts, args.e1_model_dir, temperature)

    print(f"  E2 scoring ({args.e2_run_dir})", file=sys.stderr)
    p_synthetic = score_e2(texts, args.e2_run_dir, args.max_length, args.batch_size, args.device)

    out_rows = []
    for r, (mean, entropy, multimodality), p_syn in zip(rows, e1_features, p_synthetic):
        out_rows.append({
            "passage_id": r["passage_id"],
            "volume_id": r["volume_id"],
            "date": r["date"],
            "decade": r["decade"],
            "source_tier": r.get("source_tier"),
            "n_words": r.get("n_words"),
            "n_sentences": r.get("n_sentences"),
            "e1_mean": mean,
            "e1_entropy": entropy,
            "e1_multimodality": multimodality,
            "e1_signed_residual": mean - r["date"],
            "e2_p_synthetic": p_syn,
        })

    write_jsonl(out_rows, args.out)
    print(f"wrote {len(out_rows)} scored reference rows to {args.out}", file=sys.stderr)
    if len(out_rows) != len(rows):
        print(f"  WARNING: row count mismatch ({len(out_rows)} scored vs "
              f"{len(rows)} input) — no row should be silently dropped", file=sys.stderr)


DEFAULT_WINDOW_H = 10
TARGET_DATE_LO_DEFAULT = 1831
TARGET_DATE_HI_DEFAULT = 1930
DEFAULT_ANSWERS_Q_OUT = (Path.home() / "workdata" / "chronologic-dating-corpus"
                          / "answers_q.jsonl")


def q_score(value, reference_values):
    """Empirical percentile of `value` among `reference_values`.

    q = fraction of `reference_values` STRICTLY LESS THAN `value`. A tie
    (reference == value) is therefore NOT counted as "beaten" by the
    candidate — the conservative tie-handling rev.2 §2 calls for, pinned
    here so a future refactor can't silently flip it: with small discrete
    reference windows, counting ties in the candidate's favor would
    systematically inflate its apparent typicality.

    q -> 0 means `value` sits at or below the bottom of the reference
    distribution (e.g. E1: archaic-reading relative to the window's authentic
    prose); q -> 1 means it sits at or above the top (e.g. E2: more
    detector-legible than the window's authentic prose).
    """
    if not reference_values:
        return float("nan")
    return sum(1 for r in reference_values if r < value) / len(reference_values)


def index_reference_by_year(reference_rows):
    by_year = {}
    for r in reference_rows:
        by_year.setdefault(r["date"], []).append(r)
    return by_year


def window_rows(reference_by_year, target_date, h, exclude_volume_id=None):
    """RPS rows with `date` in the closed interval [target_date-h, target_date+h].

    `exclude_volume_id`, when given, drops every reference row from that
    volume (leave-one-VOLUME-out, not leave-one-passage-out) — needed when
    the thing being scored is itself an RPS row (self-test/pseudo-model use,
    not real benchmark answers, which have no volume-mates in the RPS).
    """
    rows = []
    for year in range(target_date - h, target_date + h + 1):
        rows.extend(reference_by_year.get(year, ()))
    if exclude_volume_id is not None:
        rows = [r for r in rows if r["volume_id"] != exclude_volume_id]
    return rows


def length_conditioned_window(reference_by_year, target_date, h, target_length_bin,
                               exclude_volume_id=None):
    """The date window, then filtered to rows sharing `target_length_bin`.

    Requires every row already carry a `length_bin` field (`annotate_length_bins`,
    called once globally by the caller — not per lookup, since the same
    reference row is reused across many different candidates' windows).
    Returns (length_conditioned_rows, date_window_n_volumes) — the latter so a
    thin length-cell can be told apart from a thin date window.
    """
    window = window_rows(reference_by_year, target_date, h, exclude_volume_id)
    date_window_n_volumes = len({r["volume_id"] for r in window})
    cell = [r for r in window if r["length_bin"] == target_length_bin]
    return cell, date_window_n_volumes


def qscore_answer(e1_mean, p_synthetic, target_date, n_words, edges, reference_by_year, h,
                   exclude_volume_id=None):
    """One answer's (q_e1, q_e2, cell_n_passages, cell_n_volumes,
    date_window_n_volumes, e1_null_window_mean).

    `e1_null_window_mean` is the date-and-length-matched window's own mean
    `e1_signed_residual` -- the instrument's local bias, needed downstream to
    baseline-correct this answer's raw residual into "drift years" (see the
    wiring plan's year-baseline-correction section). NaN when the window is
    empty, matching q_e1/q_e2.
    """
    target_bin = length_bin(n_words, edges)
    window, date_window_n_volumes = length_conditioned_window(
        reference_by_year, target_date, h, target_bin, exclude_volume_id)
    signed_residual = e1_mean - target_date
    window_residuals = [r["e1_signed_residual"] for r in window]
    q_e1 = q_score(signed_residual, window_residuals)
    q_e2 = q_score(p_synthetic, [r["e2_p_synthetic"] for r in window])
    n_volumes = len({r["volume_id"] for r in window})
    e1_null_window_mean = (sum(window_residuals) / len(window_residuals)
                            if window_residuals else float("nan"))
    return q_e1, q_e2, len(window), n_volumes, date_window_n_volumes, e1_null_window_mean


def cmd_qscore(args):
    reference_rows = read_jsonl(args.reference)
    print(f"  loaded {len(reference_rows)} reference passages", file=sys.stderr)
    edges = load_length_bin_edges(args.length_bin_edges)
    annotate_length_bins(reference_rows, edges)
    reference_by_year = index_reference_by_year(reference_rows)

    answers = read_jsonl(args.answers)
    print(f"  loaded {len(answers)} answers", file=sys.stderr)
    texts = [a["text"] for a in answers]
    n_words_list = [count_words(t) for t in texts]

    temperature = load_temperature(args.temperature_fit)
    print(f"  E1 scoring at T*={temperature:.4f} ({args.e1_model_dir})", file=sys.stderr)
    e1_features = score_e1(texts, args.e1_model_dir, temperature)

    print(f"  E2 scoring ({args.e2_run_dir})", file=sys.stderr)
    p_synthetic = score_e2(texts, args.e2_run_dir, args.max_length, args.batch_size, args.device)

    out_rows = []
    for a, (mean, entropy, multimodality), p_syn, n_words in zip(
            answers, e1_features, p_synthetic, n_words_list):
        target_date = a["true_date"]
        q_e1, q_e2, window_n, window_vols, date_window_vols, e1_null_window_mean = qscore_answer(
            mean, p_syn, target_date, n_words, edges, reference_by_year, args.h)
        out_rows.append({
            "row_id": a["row_id"],
            "model": a["model"],
            "source_file": a.get("source_file"),
            "question_number": a["question_number"],
            "true_date": target_date,
            "e1_mean": mean,
            "e1_entropy": entropy,
            "e1_multimodality": multimodality,
            "e1_signed_residual": mean - target_date,
            "e1_null_window_mean": e1_null_window_mean,
            "e2_p_synthetic": p_syn,
            "q_e1": q_e1,
            "q_e2": q_e2,
            "window_n_passages": window_n,
            "window_n_volumes": window_vols,
            "date_window_n_volumes": date_window_vols,
            "window_empty": window_n == 0,
            "n_words": n_words,
            "length_bin": length_bin(n_words, edges),
        })

    write_jsonl(out_rows, args.out)
    print(f"wrote {len(out_rows)} scored answer rows to {args.out}", file=sys.stderr)
    if len(out_rows) != len(answers):
        print(f"  WARNING: row count mismatch ({len(out_rows)} scored vs "
              f"{len(answers)} input) — no row should be silently dropped", file=sys.stderr)

    # Empty window (no reference at all -> q_e1/q_e2 are NaN, unscoreable) is a
    # different condition from merely-thin (nonzero, real, just below the
    # ~60-volume target near the 1831/1836 edge, per calibration_corpus.py
    # report) -- conflating them here previously mislabeled genuinely
    # out-of-range answer dates as an expected edge effect.
    empty = [r for r in out_rows if r["window_empty"]]
    if empty:
        bad_dates = sorted({r["true_date"] for r in empty})
        print(f"  WARNING: {len(empty)}/{len(out_rows)} answers have true_date outside "
              f"the calibration corpus's covered span -> EMPTY window -> q_e1/q_e2 are NaN. "
              f"Kept in output (never silently dropped), but must be excluded before any "
              f"model-level aggregate. true_dates: {bad_dates}", file=sys.stderr)
    thin = [r for r in out_rows if not r["window_empty"] and r["window_n_volumes"] < 60]
    if thin:
        thin_dates = sorted({r["true_date"] for r in thin})
        print(f"  {len(thin)}/{len(out_rows)} answers scored against a real but thin "
              f"length-conditioned cell (<60 distinct reference volumes, nonzero); "
              f"true_dates span {thin_dates[0]}-{thin_dates[-1]}", file=sys.stderr)


def compute_lovo_qs(reference_rows, h, edges):
    """Own-date, own-length-bin, leave-one-VOLUME-out q_e1/q_e2 for every RPS row.

    "Own-date" per rev.2 §5: each row's target is its own known date, not a
    slot/step center, so the LOVO q's are the exchangeable-authentic baseline
    and — the coherence point rev.2 makes explicit — can be precomputed once
    here and reused unchanged by both `verify`'s uniformity sweep and
    pseudo-model null simulation, rather than recomputed per sweep step. Now
    also length-conditioned (own length bin, from the frozen `edges`) — the
    fix for the length-dependence `verify` found in the pre-length-conditioning
    design; `edges=[]` reduces to the old date-only behavior.
    """
    annotate_length_bins(reference_rows, edges)
    by_year = index_reference_by_year(reference_rows)
    out = []
    for r in reference_rows:
        window, date_window_n_volumes = length_conditioned_window(
            by_year, r["date"], h, r["length_bin"], exclude_volume_id=r["volume_id"])
        q_e1 = q_score(r["e1_signed_residual"], [w["e1_signed_residual"] for w in window])
        q_e2 = q_score(r["e2_p_synthetic"], [w["e2_p_synthetic"] for w in window])
        row = dict(r)
        row["lovo_q_e1"] = q_e1
        row["lovo_q_e2"] = q_e2
        row["lovo_window_n_volumes"] = len({w["volume_id"] for w in window})
        row["lovo_date_window_n_volumes"] = date_window_n_volumes
        out.append(row)
    return out


def _ks_uniform(values):
    """KS statistic + p-value against Uniform(0,1); NaN-safe (drops NaNs)."""
    from scipy.stats import kstest
    import math
    clean = [v for v in values if not math.isnan(v)]
    if len(clean) < 2:
        return float("nan"), float("nan"), len(clean)
    result = kstest(clean, "uniform")
    return float(result.statistic), float(result.pvalue), len(clean)


def _frac_le(values, threshold):
    import math
    clean = [v for v in values if not math.isnan(v)]
    if not clean:
        return float("nan")
    return sum(1 for v in clean if v <= threshold) / len(clean)


def _uniformity_block(q_e1_values, q_e2_values):
    ks_e1, p_e1, n_e1 = _ks_uniform(q_e1_values)
    ks_e2, p_e2, n_e2 = _ks_uniform(q_e2_values)
    return {
        "n_e1": n_e1, "ks_e1": ks_e1, "ks_p_e1": p_e1,
        "frac_le_0.1_e1": _frac_le(q_e1_values, 0.1), "frac_le_0.5_e1": _frac_le(q_e1_values, 0.5),
        "n_e2": n_e2, "ks_e2": ks_e2, "ks_p_e2": p_e2,
        "frac_le_0.1_e2": _frac_le(q_e2_values, 0.1), "frac_le_0.5_e2": _frac_le(q_e2_values, 0.5),
    }


def group_by_length_bin(rows, n_bins):
    buckets = {i: [] for i in range(n_bins)}
    for r in rows:
        buckets.setdefault(r["length_bin"], []).append(r)
    return buckets


def cmd_verify(args):
    reference_rows = read_jsonl(args.reference)
    print(f"  loaded {len(reference_rows)} reference passages", file=sys.stderr)
    edges = load_length_bin_edges(args.length_bin_edges)
    print(f"  computing own-date, own-length-bin LOVO q's for every row "
          f"(h={args.h}, {len(edges) + 1} length bins)...", file=sys.stderr)
    lovo_rows = compute_lovo_qs(reference_rows, args.h, edges)

    if args.lovo_out:
        write_jsonl(lovo_rows, args.lovo_out)
        print(f"  wrote {len(lovo_rows)} LOVO-scored rows to {args.lovo_out}", file=sys.stderr)

    lines = ["# typicality.py verify report", "",
             f"n = {len(lovo_rows)} reference passages; h = {args.h}; step = {args.step}; "
             f"{len(edges) + 1} length bins", ""]

    lines += ["## What this checks, and why it matters", "",
              "Every reference passage's own-date, leave-one-volume-out q asks: among its "
              "genuinely-dated peers, where does this real passage fall? If the instrument is "
              "well-calibrated, that's a plain percentile of an honestly-labeled item among "
              "exchangeable peers — uniform on [0,1] by construction. So exactly half of all "
              "rows should land below the median (`frac_le_0.5` ≈ 0.5), a tenth below the 10th "
              "percentile (`frac_le_0.1` ≈ 0.1), and `ks_p` (the KS test's p-value against "
              "Uniform(0,1)) shouldn't reject except by chance. A skew away from those targets "
              "means the reference isn't actually neutral for that slice of passages — this is "
              "exactly the check that caught E1's length-dependence in the first place "
              "(pre-length-conditioning: frac≤0.5 = 0.351 in the shortest tercile, 0.664 in the "
              "longest — badly non-uniform). It's a validity check on the *instrument*, not a "
              "claim about any individual passage.", "",
              "**Why frac≤0.5 near 0.5 matters for E2 too, not just E1**: E2 (the authenticity "
              "detector) was never as visibly broken as E1 in the pre-length-conditioning check "
              "(0.517 / 0.511 / 0.468 by tercile — much closer to 0.5 than E1's 0.351/0.664), "
              "even though its KS test also rejected uniformity in every tercile. That pattern — "
              "small frac≤0.5 deviation, but KS still significant — is the signature of a large "
              "sample (n>10,000) having enough statistical power to detect a real but minor "
              "shape difference, rather than a length bias worth fixing on its own. After "
              "length-conditioning, E2's frac≤0.5 sits at 0.498–0.500 in every bin below — "
              "essentially exact, which is the confirmation that reading was right.", "",
              "**Why 6 length bins**: splitting the reference by length costs *passages*, not "
              "*volumes* — and passages are the abundant resource here, volumes the scarce one. "
              "A density check across the corpus's thinnest windows (t=1831, 57 volumes; "
              "t=1836, 59 volumes) found every one of 6 length bins still held 950–1060 "
              "passages *and* the full volume count (56–59 of 57–59) in both windows. That "
              "works because every volume's passages are already spread across the whole length "
              "distribution (`MAX_PASSAGES_PER_VOLUME=100` in `calibration_corpus.py`), so "
              "splitting by length thins the passage-abundant dimension without touching volume "
              "coverage. If a future corpus or answer set ever needed finer bins, this same "
              "check — bin count × thinnest window — is how to decide how far that can go "
              "before a cell starts running short of volumes.", ""]

    lines += ["## Per-window uniformity of own-date, own-length-bin LOVO q's", "",
              "Uniform(0,1) under exchangeability if the RPS is well-calibrated. "
              "`frac_le_0.5` near 0.5 and `frac_le_0.1` near 0.1 are the cheap "
              "sanity checks; `ks_p` small (<0.05) flags a window worth a closer look. "
              "`n_volumes` here is the length-conditioned cell's count, pooled over all "
              "length bins in the window for this table (see the per-length-bin table below "
              "for whether length-conditioning is actually working).", "",
              "| t | n_passages | n_volumes | ks_e1 | ks_p_e1 | frac≤0.5 e1 | "
              "ks_e2 | ks_p_e2 | frac≤0.5 e2 |",
              "|---|---|---|---|---|---|---|---|---|"]
    t = TARGET_DATE_LO_DEFAULT
    while t <= TARGET_DATE_HI_DEFAULT:
        window = [r for r in lovo_rows if t - args.h <= r["date"] <= t + args.h]
        n_volumes = len({r["volume_id"] for r in window})
        block = _uniformity_block([r["lovo_q_e1"] for r in window],
                                   [r["lovo_q_e2"] for r in window])
        flag = " **short**" if n_volumes < 60 else ""
        lines.append(
            f"| {t} | {len(window)} | {n_volumes}{flag} | {block['ks_e1']:.3f} | "
            f"{block['ks_p_e1']:.3f} | {block['frac_le_0.5_e1']:.3f} | {block['ks_e2']:.3f} | "
            f"{block['ks_p_e2']:.3f} | {block['frac_le_0.5_e2']:.3f} |")
        t += args.step

    lines += ["", "## Per-length-bin breakdown (pooled across all windows)", "",
              "The direct check for whether length-conditioning fixed the length-dependence "
              "the pre-length-conditioning design had (frac≤0.5 ranged 0.351 low / 0.664 high "
              "by tercile). Every bin should now sit near 0.5 — that's the confirmation, not "
              "just an assumption, that conditioning the window on length actually worked.", "",
              "| length bin | n | ks_e1 | ks_p_e1 | frac≤0.5 e1 | ks_e2 | ks_p_e2 | frac≤0.5 e2 |",
              "|---|---|---|---|---|---|---|---|"]
    for name, bucket in sorted(group_by_length_bin(lovo_rows, len(edges) + 1).items()):
        block = _uniformity_block([r["lovo_q_e1"] for r in bucket],
                                   [r["lovo_q_e2"] for r in bucket])
        lines.append(
            f"| {name} | {len(bucket)} | {block['ks_e1']:.3f} | {block['ks_p_e1']:.3f} | "
            f"{block['frac_le_0.5_e1']:.3f} | {block['ks_e2']:.3f} | {block['ks_p_e2']:.3f} | "
            f"{block['frac_le_0.5_e2']:.3f} |")

    report = "\n".join(lines) + "\n"
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"wrote {args.report}", file=sys.stderr)
    else:
        print(report)


def date_bin(date, width=10):
    return (int(date) // width) * width


def build_cell_index(rows, bin_width=10):
    """dict[(date_bin, length_bin)] -> {volume_id: [rows...]}, for volume-blocked
    pseudo-model draws. Rows must already carry `length_bin` (`annotate_length_bins`,
    or via `compute_lovo_qs`, which annotates internally) — using the SAME frozen
    partition the q's themselves are conditioned on, not a separately-computed
    tercile, so null construction and the actual q computation stay consistent.
    """
    index = {}
    for r in rows:
        cell = (date_bin(r["date"], bin_width), r["length_bin"])
        index.setdefault(cell, {}).setdefault(r["volume_id"], []).append(r)
    return index


def volume_blocked_sample(cell_volumes, n, rng):
    """Draw `n` rows from {volume_id: [rows]}, round-robin across volumes so
    one long volume can't dominate the draw (rev.2 §5's volume-blocking ask).

    Cycles each volume's own shuffled rows via modulo once its own supply is
    exhausted (revisits rather than inventing data), guaranteeing one item of
    progress per volume per pass — never stalls as long as >=1 volume has
    >=1 row, so no separate exhaustion bookkeeping is needed.
    """
    shuffled = {vid: rng.sample(rows, len(rows)) for vid, rows in cell_volumes.items() if rows}
    if not shuffled or n <= 0:
        return []
    vids = list(shuffled.keys())
    rng.shuffle(vids)
    out = []
    idx = {vid: 0 for vid in vids}
    while len(out) < n:
        for vid in vids:
            if len(out) >= n:
                break
            rows = shuffled[vid]
            out.append(rows[idx[vid] % len(rows)])
            idx[vid] += 1
    return out


def _integral_abs_const_minus_x(c, a, b):
    """Exact integral_a^b |c - u| du for constant c -- the closed-form
    building block `wasserstein1_uniform` sums over each order statistic's
    own `((i-1)/n, i/n]` interval (spec B §6).
    """
    if c <= a:
        return ((b - c) ** 2 - (a - c) ** 2) / 2.0
    if c >= b:
        return ((c - a) ** 2 - (c - b) ** 2) / 2.0
    return ((c - a) ** 2 + (b - c) ** 2) / 2.0


def wasserstein1_uniform(values):
    """Exact W1 distance between the empirical distribution of `values` (in
    [0,1]) and Uniform(0,1), via the closed-form quantile integral -- the
    same right-continuous step function `method="inverted_cdf"` evaluates,
    so `quantile_curve`'s plotted area is literally this number (spec §A1).

    `wasserstein1_uniform([]) == 0.0` -- the BEST possible W1, not a "no
    data" sentinel. Callers must guard at the call site after NaN filtering:
    `w1 = wasserstein1_uniform(e1) if e1 else float("nan")`.
    """
    n = len(values)
    if n == 0:
        return 0.0
    sorted_vals = sorted(values)
    total = 0.0
    for i, x in enumerate(sorted_vals):
        total += _integral_abs_const_minus_x(x, i / n, (i + 1) / n)
    return total


def e1_period_fidelity(w_obs, w_null_mean):
    """0-100 headline score: 100 when W_obs is at or below the null mean
    (indistinguishable from period-and-length-matched authentic prose), 0 at
    W1's maximum of 0.5. Raises on a degenerate null (w_null_mean >= 0.5).
    """
    denom = 0.5 - w_null_mean
    if denom <= 0:
        raise ValueError(f"degenerate null: w_null_mean={w_null_mean!r} >= 0.5")
    d = max(0.0, w_obs - w_null_mean) / denom
    return max(0.0, min(100.0, 100.0 * (1.0 - d)))


def e2_authenticity_fidelity(t_e2, null_center=0.5):
    """0-100 headline score: 100 at or below the null center (no more
    detector-legible than authentic prose), 0 at T_E2=1. One-sided like
    T_E2 itself -- there is no "too archaic" direction for E2, so
    below-center also scores 100.
    """
    denom = 1.0 - null_center
    if denom <= 0:
        raise ValueError(f"degenerate null: null_center={null_center!r} >= 1.0")
    d = max(0.0, t_e2 - null_center) / denom
    return max(0.0, min(100.0, 100.0 * (1.0 - d)))


def empirical_quantile_grid(values, n_grid=101):
    """Model quantile curve on an `n_grid`-point grid over [0,1], via
    `method="inverted_cdf"` -- the same right-continuous step function
    `wasserstein1_uniform`'s exact integral evaluates, so
    `trapezoid(|deviation|, grid) ~ W1` (spec §A1's "literally the area").
    """
    import numpy as np
    grid = np.linspace(0.0, 1.0, n_grid)
    values = np.asarray(list(values), dtype=float)
    if values.size == 0:
        model_quantiles = np.full(n_grid, np.nan)
    else:
        model_quantiles = np.quantile(values, grid, method="inverted_cdf")
    deviation = model_quantiles - grid
    return {"grid": grid, "model_quantiles": model_quantiles, "deviation": deviation}


def model_stats_from_qs(q_e1_values, q_e2_values, signed_residuals=None, *, quantile_grid_n=None):
    """Per-model summary statistics from per-answer q_e1/q_e2 and, opt-in,
    baseline-corrected years residuals.

    `signed_residuals`, when given, must ALREADY be window-mean-corrected
    (see the wiring plan's year-baseline-correction section) -- passing raw
    `e1_signed_residual` here silently reproduces the ~-15.7-year instrument
    bias the correction exists to remove. NaN filtering is index-aligned to
    `q_e1_values`: `signed_residuals[i]` is kept exactly when
    `q_e1_values[i]` is kept, so drift_years/dispersion_mae stay paired with
    q_e1's own valid set. q_e2's NaN filtering is independent of q_e1's --
    `n_e1` and `n_e2` can differ when the two channels' valid answers don't
    coincide. `n` (== `n_e1`) is kept for the existing callers that key on it.
    """
    if signed_residuals is not None and len(signed_residuals) != len(q_e1_values):
        raise ValueError("signed_residuals must be the same length as q_e1_values")

    e1_idx = [i for i, q in enumerate(q_e1_values) if not math.isnan(q)]
    e1 = [q_e1_values[i] for i in e1_idx]
    e2 = [q for q in q_e2_values if not math.isnan(q)]
    resid = [signed_residuals[i] for i in e1_idx] if signed_residuals is not None else None

    t_drift = sum(e1) / len(e1) if e1 else float("nan")
    t_disp = sum(abs(q - 0.5) for q in e1) / len(e1) if e1 else float("nan")
    t_e2 = sum(e2) / len(e2) if e2 else float("nan")
    t_ks, _p, _n = _ks_uniform(e1)
    w1 = wasserstein1_uniform(e1) if e1 else float("nan")

    stats = {"n": len(e1), "n_e1": len(e1), "n_e2": len(e2),
             "T_drift": t_drift, "T_disp": t_disp, "T_E2": t_e2, "T_KS": t_ks, "W1": w1}

    if resid is not None:
        stats["drift_years"] = sum(resid) / len(resid) if resid else float("nan")
        stats["dispersion_mae"] = sum(abs(r) for r in resid) / len(resid) if resid else float("nan")

    if quantile_grid_n is not None:
        stats["q_grid"] = empirical_quantile_grid(e1, quantile_grid_n)

    return stats


def simulate_pseudo_model(cell_index, profile, rng, *, quantile_grid_n=None):
    """One pseudo-model: volume-blocked draws from each (date_bin, length_bin)
    cell in `profile` (a Counter of the real model's own cell counts), using
    each RPS row's own-date, own-length-bin LOVO q's directly — no rescoring,
    per rev.2 §5. Also carries each drawn row's own (raw, uncorrected)
    `e1_signed_residual` through to `model_stats_from_qs`'s years channel --
    for a pseudo-model the "correction" is not meaningful, since these ARE
    the reference corpus's own residuals; the resulting drift_years/
    dispersion_mae are the instrument's bias and noise floor, not a target
    (`.get(..., nan)` tolerates callers/fixtures that predate this field).
    """
    drawn = []
    unmet = 0
    for cell, n in profile.items():
        available = cell_index.get(cell)
        if not available:
            unmet += n
            continue
        rows = volume_blocked_sample(available, n, rng)
        unmet += max(0, n - len(rows))
        drawn.extend(rows)
    stats = model_stats_from_qs(
        [r["lovo_q_e1"] for r in drawn], [r["lovo_q_e2"] for r in drawn],
        [r.get("e1_signed_residual", float("nan")) for r in drawn],
        quantile_grid_n=quantile_grid_n)
    return stats, unmet


def null_p_value(real_value, null_values, center, sidedness):
    """Empirical p-value: fraction of null draws at least as extreme as the
    real value. Ties count toward the null (conservative — matches q_score's
    tie convention). `sidedness`: 'two-sided' folds |x-center|; 'high' tests
    x >= real directly.
    """
    import math
    clean = [v for v in null_values if not math.isnan(v)]
    if not clean or math.isnan(real_value):
        return float("nan")
    if sidedness == "two-sided":
        real_stat = abs(real_value - center)
        return sum(1 for v in clean if abs(v - center) >= real_stat) / len(clean)
    return sum(1 for v in clean if v >= real_value) / len(clean)


# ---------------------------------------------------------------------------
# Optional fused score: double-conformal wrapper over (p_KS, p_E2)
#
# Combines the two channels' pseudo-model p-values into one scalar via a
# fixed inner combiner, then re-validates that scalar empirically (its own
# percentile among the same combiner applied to every pseudo-model's own
# self-ranked p's) rather than trusting the combiner's textbook p-value. This
# is what makes the fused score valid regardless of which inner combiner is
# used — but validity is not power: an inner combiner that structurally
# buries a one-channel-extreme signal in a middling scalar stays weak against
# that pattern even after re-validation, which is why the choice between
# combiners is decided empirically (see the masking regression test) rather
# than by formula elegance alone.
# ---------------------------------------------------------------------------

def rank_based_ps(values, sidedness="high"):
    """Empirical p (self-inclusive, tie-conservative) for every value in
    `values` against the full set — gives every pseudo-model draw its own p,
    the input the double-conformal outer step needs. `sidedness='high'`:
    p_i = fraction of `values` >= values[i] (bigger raw stat = more extreme,
    matches T_KS/T_E2's own convention).
    """
    import bisect
    n = len(values)
    sorted_vals = sorted(values)
    out = []
    for v in values:
        if sidedness == "high":
            idx = bisect.bisect_left(sorted_vals, v)
            out.append((n - idx) / n)
        else:
            idx = bisect.bisect_right(sorted_vals, v)
            out.append(idx / n)
    return out


def _clamp_p(p, n_null):
    """A p of exactly 0 or 1 breaks HMP's division and CCT's tan() at the
    poles; floor/ceiling at the finite-sample resolution 1/(n_null+1)."""
    floor = 1.0 / (n_null + 1)
    return max(min(p, 1.0 - floor), floor)


def combine_max_extremeness(p_a, p_b):
    """min(p_a, p_b) — 'how extreme is this model's worst-offending channel.'
    Small = alarming. Immune to masking by construction: one boring channel
    can never dilute an extreme one, since the minimum just is the minimum.
    """
    return min(p_a, p_b), "low"


def combine_hmp(p_a, p_b):
    """Harmonic mean p-value (Wilson 2019), equal weights. Small = alarming.
    Only blows up as p->0 (never as p->1), so a boring channel contributes a
    small bounded amount and can never numerically cancel an alarming one —
    unlike CCT below. Valid under arbitrary/unknown dependence between the
    two p's, same as CCT, which matters here since p_KS and p_E2 share the
    same pseudo-model null and are therefore correlated, not independent.
    """
    denom = 0.5 / p_a + 0.5 / p_b
    return 1.0 / denom, "low"


def combine_cct(p_a, p_b):
    """Cauchy combination test, equal weights. Large = alarming. The
    tan((0.5-p)*pi) transform is unbounded at BOTH p->0 and p->1, with
    opposite sign — this is the exact mechanism that let a screamingly
    extreme channel and a boring channel numerically cancel in the earlier,
    now-superseded passage-level fusion design (a masking bug, not a corner
    case: date-accurate-but-detectably-synthetic is the modal profile of good
    pastiche). Kept as an option for comparison, not necessarily the default
    — see the masking regression test.
    """
    t = 0.5 * math.tan((0.5 - p_a) * math.pi) + 0.5 * math.tan((0.5 - p_b) * math.pi)
    return t, "high"


INNER_COMBINERS = {"max": combine_max_extremeness, "hmp": combine_hmp, "cct": combine_cct}
DEFAULT_FUSION_METHOD = "hmp"  # set by test_fused_score_masking_* -- see tests/test_typicality.py


def fused_score(p_a_real, p_b_real, null_a_values, null_b_values, method):
    """Double-conformal fused score for one model: combine (p_a, p_b) via
    `method`, then take the empirical outer percentile of that combined
    scalar among the same combiner applied to every pseudo-model's own
    self-ranked (p_a, p_b). Returns (fused_p, combined_scalar).

    `null_a_values`/`null_b_values` are the RAW per-draw statistic values
    (e.g. every pseudo-model's T_KS, T_E2) — not p-values themselves; this
    function does the self-ranking internally via `rank_based_ps`, so the
    same raw null arrays used to compute `p_a_real`/`p_b_real` (via
    `null_p_value`) are what's passed in here.
    """
    combiner = INNER_COMBINERS[method]
    n_null = len(null_a_values)
    p_a_real = _clamp_p(p_a_real, n_null)
    p_b_real = _clamp_p(p_b_real, n_null)
    real_scalar, sidedness = combiner(p_a_real, p_b_real)

    null_p_a = rank_based_ps(null_a_values, "high")
    null_p_b = rank_based_ps(null_b_values, "high")
    null_scalars = [combiner(_clamp_p(pa, n_null), _clamp_p(pb, n_null))[0]
                     for pa, pb in zip(null_p_a, null_p_b)]

    if sidedness == "low":
        fused_p = sum(1 for v in null_scalars if v <= real_scalar) / n_null
    else:
        fused_p = sum(1 for v in null_scalars if v >= real_scalar) / n_null
    return fused_p, real_scalar


def cmd_model_report(args):
    import random

    reference_rows = read_jsonl(args.reference)
    print(f"  loaded {len(reference_rows)} reference passages", file=sys.stderr)
    edges = load_length_bin_edges(args.length_bin_edges)
    print(f"  computing own-date, own-length-bin LOVO q's (h={args.h})...", file=sys.stderr)
    lovo_rows = compute_lovo_qs(reference_rows, args.h, edges)

    answers = read_jsonl(args.answers_q)
    print(f"  loaded {len(answers)} scored answers", file=sys.stderr)
    valid = [a for a in answers if not a.get("window_empty")
             and not math.isnan(a["q_e1"]) and not math.isnan(a["q_e2"])]
    n_dropped = len(answers) - len(valid)
    if n_dropped:
        print(f"  excluding {n_dropped} answers with empty/NaN windows from all "
              f"model-level statistics", file=sys.stderr)

    cell_index = build_cell_index(lovo_rows)

    models = sorted({a["model"] for a in valid})
    by_model = {m: [a for a in valid if a["model"] == m] for m in models}

    rng = random.Random(args.seed)

    print(f"  simulating {args.n_null} pseudo-model nulls per model...", file=sys.stderr)
    real_stats = {}
    null_stats = {}
    for m in models:
        rows = by_model[m]
        real_stats[m] = model_stats_from_qs([r["q_e1"] for r in rows],
                                             [r["q_e2"] for r in rows])
        profile = {}
        for r in rows:
            cell = (date_bin(r["true_date"]), r["length_bin"])
            profile[cell] = profile.get(cell, 0) + 1
        draws = []
        total_unmet = 0
        for _ in range(args.n_null):
            stats, unmet = simulate_pseudo_model(cell_index, profile, rng)
            draws.append(stats)
            total_unmet += unmet
        null_stats[m] = draws
        if total_unmet:
            print(f"    {m}: {total_unmet} pseudo-answer slots unmet across "
                  f"{args.n_null} draws (empty cells in the RPS)", file=sys.stderr)

    print(f"  two-way bootstrap ({args.n_boot} draws)...", file=sys.stderr)
    boot_stats = two_way_bootstrap(valid, reference_rows, models, by_model, args.h,
                                    args.n_boot, rng)

    lines = ["# typicality.py model-report", "",
             f"n_models = {len(models)}; n_answers = {len(valid)} "
             f"({n_dropped} excluded, empty/NaN window); "
             f"n_null = {args.n_null}; n_boot = {args.n_boot}; "
             f"{len(edges) + 1} length bins ({args.length_bin_edges})", "",
             "T_drift/T_disp/T_E2 are length-conditioned in the q computation itself (not "
             "just in the pseudo-model null) — see `verify`'s per-length-bin table for the "
             "direct confirmation that this keeps the reference neutral by length. Comparable "
             "across models without a length adjustment in your head.", ""]

    lines += ["## What these statistics mean", "",
              "- **T_drift** — mean of the model's `q_e1` values. Signed: >0.5 reads "
              "systematically *modern* relative to period-and-length-matched authentic prose; "
              "<0.5 reads systematically *archaic*. 0.5 is the null center (no drift).",
              "- **T_disp** — mean of `|q_e1 − 0.5|`: how far each answer's q typically sits "
              "from neutral, regardless of direction. Null center is 0.25 (the expected value "
              "under a uniform q). *Above* 0.25: erratic/inconsistent-in-period, with extremes "
              "in both directions that T_drift's plain average can hide. *Below* 0.25: "
              "suspiciously over-consistent — tighter clustering around \"typical\" than "
              "genuine period prose shows, a possible generated-text tell no other statistic "
              "here catches.",
              "- **T_E2** — mean of the model's `q_e2` values (the authenticity-detector "
              "channel). One-sided: >0.5 means more detector-legible as synthetic than "
              "authentic prose of the same period and length; there's no meaningful \"too "
              "archaic\" direction for a binary detector, so it's read high-only.",
              "- **T_KS** — the Kolmogorov–Smirnov statistic comparing the model's `q_e1` "
              "distribution to Uniform(0,1) directly; an omnibus check that subsumes drift and "
              "dispersion into one number but loses the decomposed story. Reported for "
              "completeness, not as the headline.",
              "- **p** (beside each statistic) — empirical p-value against `n_null` "
              "pseudo-model nulls: volume-blocked, date-and-length-matched draws from the "
              "reference corpus's own passages, simulating what an honestly-dated, "
              "honestly-styled \"model\" would look like. Small p means the real model's "
              "statistic is more extreme than that fraction of pseudo-models built from "
              "genuine period prose.",
              "- **CI** (bootstrap table below) — 95% interval from resampling both the "
              "model's answers (clustered by shared question) and the reference corpus "
              "(clustered by volume) together, so item-difficulty and reference-sampling "
              "uncertainty are both reflected, not just answer count.",
              f"- **Fused** — T_KS and T_E2 combined into one number via a "
              f"`{args.fusion_method}` inner combiner (double-conformal: the combiner's own "
              f"scalar is re-validated against the same combiner applied to every pseudo-model's "
              f"own self-ranked p's, not trusted directly). Small = alarming on the combination. "
              f"Chosen over the Cauchy combination test because CCT's transform is unbounded at "
              f"*both* p→0 and p→1 with opposite sign, so a screaming channel and a boring "
              f"channel can numerically cancel — confirmed empirically "
              f"(`test_fused_score_masking_hmp_and_max_catch_it`) rather than assumed.", "",
              "| model | n | T_drift | p | T_disp | p | T_E2 | p | T_KS | Fused | p |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    p_values = {}
    fused_values = {}
    for m in models:
        rs = real_stats[m]
        nulls = null_stats[m]
        p_drift = null_p_value(rs["T_drift"], [d["T_drift"] for d in nulls], 0.5, "two-sided")
        p_disp = null_p_value(rs["T_disp"], [d["T_disp"] for d in nulls], 0.25, "two-sided")
        p_e2 = null_p_value(rs["T_E2"], [d["T_E2"] for d in nulls], 0.5, "high")
        p_ks = null_p_value(rs["T_KS"], [d["T_KS"] for d in nulls], None, "high")
        p_values[m] = {"drift": p_drift, "disp": p_disp, "e2": p_e2, "ks": p_ks}
        fused_p, fused_scalar = fused_score(
            p_ks, p_e2, [d["T_KS"] for d in nulls], [d["T_E2"] for d in nulls],
            args.fusion_method)
        fused_values[m] = {"p": fused_p, "scalar": fused_scalar}
        lines.append(
            f"| {m} | {rs['n']} | {rs['T_drift']:.3f} | {p_drift:.3f} | "
            f"{rs['T_disp']:.3f} | {p_disp:.3f} | {rs['T_E2']:.3f} | {p_e2:.3f} | "
            f"{rs['T_KS']:.3f} | {fused_scalar:.3f} | {fused_p:.3f} |")

    lines += ["", "## Two-way bootstrap 95% CIs (item x reference-volume clustered)", "",
              "| model | T_drift CI | T_disp CI | T_E2 CI |", "|---|---|---|---|"]
    for m in models:
        b = boot_stats[m]
        def ci(key):
            vals = sorted(v[key] for v in b if not math.isnan(v[key]))
            if not vals:
                return "n/a"
            lo = vals[int(0.025 * len(vals))]
            hi = vals[min(int(0.975 * len(vals)), len(vals) - 1)]
            return f"[{lo:.3f}, {hi:.3f}]"
        lines.append(f"| {m} | {ci('T_drift')} | {ci('T_disp')} | {ci('T_E2')} |")

    lines += ["", "## Patterns in this run", ""]
    drift_ranked = sorted(models, key=lambda m: real_stats[m]["T_drift"])
    most_archaic, most_modern = drift_ranked[0], drift_ranked[-1]
    lines.append(
        f"- **T_drift range**: {most_archaic} reads most archaic "
        f"(T_drift={real_stats[most_archaic]['T_drift']:.3f}, p={p_values[most_archaic]['drift']:.3f}); "
        f"{most_modern} reads most modern "
        f"(T_drift={real_stats[most_modern]['T_drift']:.3f}, p={p_values[most_modern]['drift']:.3f}).")
    overdispersed = sorted(
        [m for m in models if real_stats[m]["T_disp"] > 0.25 and p_values[m]["disp"] < 0.05],
        key=lambda m: -real_stats[m]["T_disp"])
    underdispersed = sorted(
        [m for m in models if real_stats[m]["T_disp"] < 0.25 and p_values[m]["disp"] < 0.05],
        key=lambda m: real_stats[m]["T_disp"])
    if overdispersed:
        lines.append(
            "- **Erratic-in-period (T_disp significantly above 0.25)**: " +
            ", ".join(f"{m} ({real_stats[m]['T_disp']:.3f})" for m in overdispersed) +
            " — balanced extremes in both directions that T_drift's plain average would hide.")
    if underdispersed:
        lines.append(
            "- **Suspiciously over-consistent (T_disp significantly below 0.25)**: " +
            ", ".join(f"{m} ({real_stats[m]['T_disp']:.3f})" for m in underdispersed) +
            " — tighter than genuine period prose, a tell T_drift alone can't see.")
    e2_ranked = sorted(models, key=lambda m: real_stats[m]["T_E2"])
    e2_not_significant = [m for m in models if p_values[m]["e2"] >= 0.05]
    e2_caveat = (f" Indistinguishable from authentic prose by E2 this run: "
                 f"{', '.join(e2_not_significant)}."
                 if e2_not_significant else
                 " Every model is E2-significant this run — none is indistinguishable "
                 "from authentic prose by the detector.")
    lines.append(
        f"- **T_E2 range**: {e2_ranked[0]} least detector-legible "
        f"(T_E2={real_stats[e2_ranked[0]]['T_E2']:.3f}); {e2_ranked[-1]} most "
        f"(T_E2={real_stats[e2_ranked[-1]]['T_E2']:.3f}).{e2_caveat}")
    fused_significant = sorted(
        [m for m in models if fused_values[m]["p"] < 0.05],
        key=lambda m: fused_values[m]["p"])
    if fused_significant:
        lines.append(
            f"- **Fused-significant ({args.fusion_method}, p<0.05)**: " +
            ", ".join(f"{m} (p={fused_values[m]['p']:.3f})" for m in fused_significant) +
            " — alarming on at least one of T_KS/T_E2 in a way the null doesn't explain away.")
    else:
        lines.append(f"- **Fused-significant ({args.fusion_method}, p<0.05)**: none this run.")
    floor = 1.0 / (args.n_null + 1)
    at_floor = [m for m in models if p_values[m]["e2"] <= floor or p_values[m]["ks"] <= floor]
    if at_floor:
        lines.append(
            f"- **Resolution floor**: {len(at_floor)}/{len(models)} model(s) have T_E2 and/or "
            f"T_KS more extreme than *every one* of the {args.n_null} pseudo-model draws, so "
            f"their p (and the fused p that inherits it) is pinned at the empirical floor "
            f"`1/(n_null+1)={floor:.4f}` — \"at least this significant,\" not a precise value. "
            f"The fused *scalar* column still varies below that floor and is the more honest "
            f"thing to rank pinned models by; separating them further on p alone would need a "
            f"larger `--n-null`.")

    report = "\n".join(lines) + "\n"
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"wrote {args.report}", file=sys.stderr)
    else:
        print(report)

    if args.stats_out:
        stats_payload = {m: {"real": real_stats[m], "p": p_values[m], "fused": fused_values[m]}
                          for m in models}
        Path(args.stats_out).write_text(json.dumps(stats_payload, indent=2), encoding="utf-8")
        print(f"wrote {args.stats_out}", file=sys.stderr)

    if args.boot_out:
        # Raw per-draw bootstrap stats (T_drift/T_disp/T_E2/T_KS), one list per
        # model -- lets a plotting script derive any CI (or a different
        # interval, e.g. 90%) without re-running the bootstrap, which is the
        # dominant cost of this command.
        Path(args.boot_out).write_text(json.dumps(boot_stats, indent=2), encoding="utf-8")
        print(f"wrote {args.boot_out}", file=sys.stderr)


def two_way_bootstrap(valid_answers, reference_rows, models, by_model, h, n_boot, rng, *,
                      quantile_grid_n=None):
    """Per draw: resample RPS volumes (with replacement) and recompute every
    answer's q against the resampled reference, length-conditioned exactly
    like the real q's (each answer's own `length_bin`, already computed by
    `qscore`); SEPARATELY resample each model's own question_numbers (with
    replacement, item-clustered) and aggregate stats from the matching
    (possibly repeated) recomputed rows. One reference resample + one
    q-recompute pass per draw, shared across all models, rather than redone
    per model — the resample is otherwise the same dominant cost n_boot times
    over. `reference_rows` must already carry `length_bin` (true here: the
    caller runs `compute_lovo_qs`, which annotates in place, before this).

    Also recomputes each answer's window-mean-corrected years residual
    INSIDE the reference-resample pass (not merely threaded through from the
    real q's): the raw `e1_signed_residual` is invariant under the reference
    resample (it's `e1_mean - true_date`), but the corrected residual is
    not -- it subtracts the resampled window's own mean.
    """
    import numpy as np

    volumes = sorted({r["volume_id"] for r in reference_rows})
    rows_by_volume = {}
    for r in reference_rows:
        rows_by_volume.setdefault(r["volume_id"], []).append(r)

    boot_stats = {m: [] for m in models}
    for _ in range(n_boot):
        drawn_volumes = [rng.choice(volumes) for _ in volumes]
        resampled_by_cell = {}
        for vid in drawn_volumes:
            for r in rows_by_volume[vid]:
                resampled_by_cell.setdefault((r["date"], r["length_bin"]), []).append(r)
        # Per-cell arrays are NOT individually sorted here -- np.searchsorted needs
        # the merged window sorted as a whole, and concatenating several
        # separately-sorted per-cell arrays does not produce a globally sorted
        # array (e.g. [1,5,9]+[2,3,7] -> [1,5,9,2,3,7], not sorted). Sort once,
        # after concatenating each window, not before.
        e1_by_cell = {k: np.array([r["e1_signed_residual"] for r in rs])
                      for k, rs in resampled_by_cell.items()}
        e2_by_cell = {k: np.array([r["e2_p_synthetic"] for r in rs])
                      for k, rs in resampled_by_cell.items()}

        recomputed = {}
        for a in valid_answers:
            t = a["true_date"]
            b = a["length_bin"]
            e1_vals = [e1_by_cell[(y, b)] for y in range(t - h, t + h + 1) if (y, b) in e1_by_cell]
            e2_vals = [e2_by_cell[(y, b)] for y in range(t - h, t + h + 1) if (y, b) in e2_by_cell]
            if not e1_vals:
                recomputed[a["row_id"]] = (float("nan"), float("nan"), float("nan"))
                continue
            e1_arr = np.sort(np.concatenate(e1_vals))
            e2_arr = np.sort(np.concatenate(e2_vals))
            signed_residual = a["e1_mean"] - t
            q_e1 = float(np.searchsorted(e1_arr, signed_residual, side="left")) / len(e1_arr)
            q_e2 = float(np.searchsorted(e2_arr, a["e2_p_synthetic"], side="left")) / len(e2_arr)
            resid_corrected = signed_residual - e1_arr.mean()
            recomputed[a["row_id"]] = (q_e1, q_e2, resid_corrected)

        for m in models:
            rows = by_model[m]
            item_ids = sorted({r["question_number"] for r in rows})
            if not item_ids:
                continue
            drawn_items = [rng.choice(item_ids) for _ in item_ids]
            item_counts = {}
            for it in drawn_items:
                item_counts[it] = item_counts.get(it, 0) + 1
            q_e1_list, q_e2_list, resid_list = [], [], []
            for r in rows:
                mult = item_counts.get(r["question_number"], 0)
                if mult == 0:
                    continue
                q_e1, q_e2, resid = recomputed[r["row_id"]]
                q_e1_list.extend([q_e1] * mult)
                q_e2_list.extend([q_e2] * mult)
                resid_list.extend([resid] * mult)
            boot_stats[m].append(model_stats_from_qs(
                q_e1_list, q_e2_list, resid_list, quantile_grid_n=quantile_grid_n))

    return boot_stats


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)

    fl = sub.add_parser("fit-length-bins",
                         help="fit frozen quantile cut points on log(n_words) over the RPS")
    fl.add_argument("--reference", default=str(DEFAULT_REFERENCE_OUT))
    fl.add_argument("--n-bins", type=int, default=DEFAULT_N_LENGTH_BINS)
    fl.add_argument("--out", default=str(DEFAULT_LENGTH_BIN_EDGES))
    fl.set_defaults(func=cmd_fit_length_bins)

    sr = sub.add_parser("score-reference",
                         help="score every calibration passage through frozen E1+E2")
    sr.add_argument("--calibration", default=str(DEFAULT_CALIBRATION))
    sr.add_argument("--e1-model-dir", default=str(DEFAULT_E1_MODEL_DIR))
    sr.add_argument("--e2-run-dir", default=str(DEFAULT_E2_RUN_DIR))
    sr.add_argument("--temperature-fit", default=str(DEFAULT_TEMPERATURE_FIT))
    sr.add_argument("--max-length", type=int, default=256)
    sr.add_argument("--batch-size", type=int, default=32)
    sr.add_argument("--device", default="auto")
    sr.add_argument("--out", default=str(DEFAULT_REFERENCE_OUT))
    sr.set_defaults(func=cmd_score_reference)

    qs = sub.add_parser("qscore",
                         help="per-answer conformal q's against the RPS")
    qs.add_argument("--reference", default=str(DEFAULT_REFERENCE_OUT))
    qs.add_argument("--answers", required=True)
    qs.add_argument("--e1-model-dir", default=str(DEFAULT_E1_MODEL_DIR))
    qs.add_argument("--e2-run-dir", default=str(DEFAULT_E2_RUN_DIR))
    qs.add_argument("--temperature-fit", default=str(DEFAULT_TEMPERATURE_FIT))
    qs.add_argument("--length-bin-edges", default=str(DEFAULT_LENGTH_BIN_EDGES))
    qs.add_argument("--h", type=int, default=DEFAULT_WINDOW_H)
    qs.add_argument("--max-length", type=int, default=256)
    qs.add_argument("--batch-size", type=int, default=32)
    qs.add_argument("--device", default="auto")
    qs.add_argument("--out", default=str(DEFAULT_ANSWERS_Q_OUT))
    qs.set_defaults(func=cmd_qscore)

    vf = sub.add_parser("verify",
                         help="uniformity sweep of own-date, own-length-bin LOVO q's over the RPS")
    vf.add_argument("--reference", default=str(DEFAULT_REFERENCE_OUT))
    vf.add_argument("--length-bin-edges", default=str(DEFAULT_LENGTH_BIN_EDGES))
    vf.add_argument("--h", type=int, default=DEFAULT_WINDOW_H)
    vf.add_argument("--step", type=int, default=5)
    vf.add_argument("--lovo-out", default=None,
                     help="optionally also write the per-row LOVO q table "
                          "(reused unchanged by pseudo-model null simulation later)")
    vf.add_argument("--report", default=None)
    vf.set_defaults(func=cmd_verify)

    mr = sub.add_parser("model-report",
                         help="per-model T_drift/T_disp/T_E2/T_KS, pseudo-model nulls, "
                              "two-way bootstrap CIs")
    mr.add_argument("--answers-q", required=True)
    mr.add_argument("--reference", default=str(DEFAULT_REFERENCE_OUT))
    mr.add_argument("--length-bin-edges", default=str(DEFAULT_LENGTH_BIN_EDGES))
    mr.add_argument("--h", type=int, default=DEFAULT_WINDOW_H)
    mr.add_argument("--n-null", type=int, default=2000)
    mr.add_argument("--n-boot", type=int, default=1000)
    mr.add_argument("--seed", type=int, default=20260809)
    mr.add_argument("--fusion-method", choices=list(INNER_COMBINERS), default=DEFAULT_FUSION_METHOD,
                     help="inner combiner for the fused T_KS/T_E2 score (double-conformal "
                          "outer percentile always applied regardless of choice)")
    mr.add_argument("--report", default=None)
    mr.add_argument("--stats-out", default=None,
                     help="optionally write real_stats + p-values per model as JSON")
    mr.add_argument("--boot-out", default=None,
                     help="optionally write the raw per-draw bootstrap stats per model as "
                          "JSON (for plotting CIs without re-running the bootstrap)")
    mr.set_defaults(func=cmd_model_report)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
