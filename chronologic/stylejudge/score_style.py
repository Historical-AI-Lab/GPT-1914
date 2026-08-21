#!/usr/bin/env python3
"""score_style.py — per-candidate style-judge scoring (Spec A: "a script in
the stylejudge/ folder"; see modelasjudge/plan-wire-in-style-judge.md).

Scores ONE candidate's `free_gen_*.json` against the Reference Prediction
Set (RPS), producing the two Spec B headline 0-100 scores (Period Fidelity,
Authenticity Fidelity) with 95% bootstrap CIs, drift/dispersion in both
raw-year and conformal units, and a quantile curve + null band for plotting.

Every intermediate is candidate-scoped (row_id/path all key off
`candidate_label`) -- nothing is written into `stylejudge/` itself, and
successive candidates never clobber each other the way the retired
cohort-wide `stylejudge/answers_q.jsonl` batch did.

Imports `typicality`, `date_predictor` (via typicality), `authenticity_detector`
(via typicality), `measure_length_distribution`, `naming` -- never
`modelasjudge.substantive.*` (this script must run even when the substantive
pipeline hasn't; the ledger join happens downstream, in
`modelasjudge/merge_style_row.py`).

CLI
    python score_style.py --free-gen PATH [options]

    # full run
    python score_style.py --free-gen ../modelasjudge/generated_answers/free_gen_gpt-5.4__0.7.json

    # re-report after a statistics change, no GPU work at all
    python score_style.py --free-gen ../modelasjudge/generated_answers/free_gen_gpt-5.4__0.7.json \\
        --answers-q ~/workdata/chronologic-dating-corpus/style_intermediates/answers_q_gpt-5.4__0.7.jsonl

    # smoke
    python score_style.py --free-gen ... --n-null 50 --n-boot 50 --out-dir /tmp/style_smoke

    # one-time validation of the fixed-W0 approximation (~31s/replicate, never run by run_pipeline)
    python score_style.py --free-gen ... --answers-q ... --diagnose-null-stability 50
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT / "modelasjudge") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "modelasjudge"))

import numpy as np

import typicality as tp                                 # noqa: E402
from measure_length_distribution import count_words      # noqa: E402
import naming                                            # noqa: E402

BOOKSAMPLE_DIR = REPO_ROOT / "booksample"
DEFAULT_OUT_DIR = REPO_ROOT / "modelasjudge" / "results"
DEFAULT_INTERMEDIATE_DIR = (Path.home() / "workdata" / "chronologic-dating-corpus"
                            / "style_intermediates")

SCHEMA_VERSION = "stylejudge-2.0"
DEFAULT_H = 10
DEFAULT_MIN_WORDS = 6  # matches diagnose_e1_stats.DEFAULT_MIN_WORDS
DEFAULT_N_NULL = 2000
DEFAULT_N_BOOT = 1000
DEFAULT_SEED = 20260809  # matches typicality.py model-report
DEFAULT_QUANTILE_GRID_N = 101

METHOD_NOTE = """\
W0 (the null-mean W1) and mu0 (the E2 null center) are held fixed at their
point estimates inside every bootstrap replicate, rather than recomputed per
replicate from a resampled reference. Recomputing the null per replicate
would need a nested simulation (n_null pseudo-model draws inside every one
of n_boot bootstrap draws, each preceded by a full leave-one-volume-out
recomputation of the reference's own q's) -- not tractable, and largely
redundant: reference-resampling uncertainty already enters W_obs in every
replicate, because the replicate recomputes each answer's q_e1 against the
resampled reference, which is exactly what the null baseline corrects for.

Monte Carlo error in estimating W0 from n_null draws is negligible (~1e-4,
scaling with candidate n) against the bootstrap's own spread (~0.01-0.02) --
estimating W0 once and treating it as known is not a compromise on that
axis. The real approximation is that W0 is conditional on the actual RPS;
the correct matched baseline for replicate b is W0^(b), not W0. Both the
variance and location effects of holding W0 fixed point conservative (wider
CI, and the replicate numerator W_obs^(b) - W0 is systematically too large,
shifting the score distribution down) but the sign of the net effect isn't
determined analytically -- see `--diagnose-null-stability` for the one-time
empirical check.

Two artifacts of the score definition worth reading past a plot: because
d_E1 = max(0, W_obs - W0)/(0.5 - W0) clips at zero, a model near its null
mean gets a degenerate CI of [100, 100] -- every replicate clips. That is
not zero uncertainty; it means indistinguishable from the matched reference
at this sample size. Read w1_ci95 instead. And near the clip boundary the
fidelity CI is one-sided by construction: percentile intervals stay valid
but must not be read as +/-.
"""


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def _sha256_file(path, chunk_size=1 << 16) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _ci95(values):
    clean = sorted(v for v in values if not (v != v))  # v != v drops NaN, no math import needed
    if not clean:
        return float("nan"), float("nan")
    lo = clean[int(0.025 * len(clean))]
    hi = clean[min(int(0.975 * len(clean)), len(clean) - 1)]
    return float(lo), float(hi)


def _mean(values):
    clean = [v for v in values if not math.isnan(v)]
    return sum(clean) / len(clean) if clean else float("nan")


def _sd(values):
    clean = [v for v in values if not math.isnan(v)]
    return statistics.pstdev(clean) if len(clean) > 1 else float("nan")


def _pearson_corr(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if not (math.isnan(x) or math.isnan(y))]
    if len(pairs) < 2:
        return float("nan")
    xa = np.array([p[0] for p in pairs])
    ya = np.array([p[1] for p in pairs])
    if xa.std() == 0 or ya.std() == 0:
        return float("nan")
    return float(np.corrcoef(xa, ya)[0, 1])


def git_head() -> str:
    import subprocess
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                             capture_output=True, text=True, timeout=5, check=True)
        return out.stdout.strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# _resolve -- paths + identity, mirrors score_substantive._resolve
# ---------------------------------------------------------------------------

def _resolve(args) -> dict:
    free_gen_path = Path(args.free_gen)
    if not free_gen_path.exists():
        sys.exit(f"ERROR: --free-gen {free_gen_path} not found")
    free_gen = json.loads(free_gen_path.read_text(encoding="utf-8"))

    candidate_label = (args.candidate_label or free_gen.get("candidate_label")
                       or free_gen.get("model") or free_gen_path.stem)
    candidate_model = free_gen.get("model", candidate_label)
    candidate_effort = free_gen.get("reasoning_effort", "none")
    benchmark_version = free_gen.get("benchmark_version") or naming.benchmark_version(free_gen_path)

    if args.benchmark:
        benchmark_path = Path(args.benchmark)
    elif free_gen.get("benchmark_path") and Path(free_gen["benchmark_path"]).exists():
        benchmark_path = Path(free_gen["benchmark_path"])
    else:
        benchmark_path = BOOKSAMPLE_DIR / f"chronologic_en_{benchmark_version}.jsonl"
    if not benchmark_path.exists():
        sys.exit(f"ERROR: benchmark {benchmark_path} not found (candidate {candidate_label!r}, "
                 f"benchmark_version {benchmark_version!r}); pass --benchmark explicitly.")

    reference = Path(args.reference) if args.reference else tp.DEFAULT_REFERENCE_OUT
    e1_model_dir = Path(args.e1_model_dir) if args.e1_model_dir else tp.DEFAULT_E1_MODEL_DIR
    e2_run_dir = Path(args.e2_run_dir) if args.e2_run_dir else tp.DEFAULT_E2_RUN_DIR
    temperature_fit = Path(args.temperature_fit) if args.temperature_fit else tp.DEFAULT_TEMPERATURE_FIT
    length_bin_edges = (Path(args.length_bin_edges) if args.length_bin_edges
                        else tp.DEFAULT_LENGTH_BIN_EDGES)

    ctag = naming.candidate_tag(candidate_label)
    label_tag = naming.sanitize(candidate_label)
    out_dir = Path(args.out_dir)
    json_out = (Path(args.json_out) if args.json_out
               else out_dir / f"style_report_{label_tag}__{benchmark_version}.json")
    report_path = (Path(args.report) if args.report
                  else out_dir / f"style_report_{label_tag}__{benchmark_version}.md")
    intermediate_dir = Path(args.intermediate_dir)
    answers_q_out = (Path(args.answers_q_out) if args.answers_q_out
                     else intermediate_dir / f"answers_q_{ctag}__{benchmark_version}.jsonl")

    return dict(
        free_gen=free_gen, free_gen_path=free_gen_path,
        candidate_label=candidate_label, candidate_model=candidate_model,
        candidate_effort=candidate_effort, benchmark_version=benchmark_version,
        benchmark_path=benchmark_path, reference=reference, e1_model_dir=e1_model_dir,
        e2_run_dir=e2_run_dir, temperature_fit=temperature_fit, length_bin_edges=length_bin_edges,
        json_out=json_out, report_path=report_path, intermediate_dir=intermediate_dir,
        answers_q_out=answers_q_out,
    )


# ---------------------------------------------------------------------------
# _build_answer_rows -- the diagnose_e1_stats.cmd_sample_benchmark_answers
# join, scoped to ONE free-gen file / ONE candidate, with counters returned
# (not just printed) so they land in the JSON.
# ---------------------------------------------------------------------------

def _build_answer_rows(free_gen: dict, free_gen_path: Path, benchmark_path: Path,
                       candidate_label: str, min_words: int):
    by_qnum = {r["question_number"]: r for r in tp.read_jsonl(benchmark_path)}
    answers = free_gen.get("answers", {})
    ctag = naming.candidate_tag(candidate_label)

    rows = []
    n_excluded_short = n_excluded_missing_text = n_excluded_unmatched = 0
    for qnum_str, ans in answers.items():
        text = (ans or {}).get("answer")
        if not text:
            n_excluded_missing_text += 1
            continue
        if count_words(text) < min_words:
            n_excluded_short += 1
            continue
        brow = by_qnum.get(int(qnum_str))
        if brow is None or brow.get("source_date") is None:
            n_excluded_unmatched += 1
            continue
        rows.append({
            "row_id": f"{ctag}_{free_gen_path.stem}_{qnum_str}",
            "model": candidate_label,
            "source_file": free_gen_path.name,
            "question_number": int(qnum_str),
            "text": text,
            "true_date": brow["source_date"],
        })

    counts = dict(
        n_generated=len(answers), n_excluded_short=n_excluded_short,
        n_excluded_missing_text=n_excluded_missing_text, n_excluded_unmatched=n_excluded_unmatched,
    )
    return rows, counts


# ---------------------------------------------------------------------------
# scoring: answer rows -> the answers_q schema (mirrors typicality.cmd_qscore
# so the two paths stay in step, per the wiring plan)
# ---------------------------------------------------------------------------

def _score_answers(answer_rows, edges, reference_by_year, *, e1_model_dir, e2_run_dir,
                   temperature_fit, h, max_length, batch_size, device):
    texts = [a["text"] for a in answer_rows]
    n_words_list = [count_words(t) for t in texts]

    temperature = tp.load_temperature(temperature_fit)
    print(f"  E1 scoring at T*={temperature:.4f} ({e1_model_dir})", file=sys.stderr)
    e1_features = tp.score_e1(texts, e1_model_dir, temperature)

    print(f"  E2 scoring ({e2_run_dir})", file=sys.stderr)
    p_synthetic = tp.score_e2(texts, e2_run_dir, max_length, batch_size, device)

    out_rows = []
    for a, (mean, entropy, multimodality), p_syn, n_words in zip(
            answer_rows, e1_features, p_synthetic, n_words_list):
        target_date = a["true_date"]
        q_e1, q_e2, window_n, window_vols, date_window_vols, e1_null_window_mean = tp.qscore_answer(
            mean, p_syn, target_date, n_words, edges, reference_by_year, h)
        out_rows.append({
            "row_id": a["row_id"], "model": a["model"], "source_file": a.get("source_file"),
            "question_number": a["question_number"], "true_date": target_date,
            "e1_mean": mean, "e1_entropy": entropy, "e1_multimodality": multimodality,
            "e1_signed_residual": mean - target_date, "e1_null_window_mean": e1_null_window_mean,
            "e2_p_synthetic": p_syn, "q_e1": q_e1, "q_e2": q_e2,
            "window_n_passages": window_n, "window_n_volumes": window_vols,
            "date_window_n_volumes": date_window_vols, "window_empty": window_n == 0,
            "n_words": n_words, "length_bin": tp.length_bin(n_words, edges),
        })
    return out_rows


def _valid(answers_q):
    """Same predicate as typicality.cmd_model_report."""
    return [a for a in answers_q if not a.get("window_empty")
           and not math.isnan(a["q_e1"]) and not math.isnan(a["q_e2"])]


# ---------------------------------------------------------------------------
# LOVO cache
# ---------------------------------------------------------------------------

def _lovo_with_cache(reference_rows, h, edges, *, reference_path, length_bin_edges_path,
                     cache_dir, use_cache):
    if not use_cache:
        return tp.compute_lovo_qs(reference_rows, h, edges)

    ref_sha = _sha256_file(reference_path)[:12]
    edges_sha = _sha256_file(length_bin_edges_path)[:8]
    cache_path = Path(cache_dir) / f"lovo_h{h}_{ref_sha}_{edges_sha}.jsonl"
    if cache_path.exists():
        print(f"  LOVO cache hit: {cache_path}", file=sys.stderr)
        return tp.read_jsonl(cache_path)

    print(f"  LOVO cache miss; computing (h={h}, {len(edges) + 1} length bins)...", file=sys.stderr)
    lovo_rows = tp.compute_lovo_qs(reference_rows, h, edges)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tp.write_jsonl(lovo_rows, cache_path)
    print(f"  wrote LOVO cache {cache_path}", file=sys.stderr)
    return lovo_rows


# ---------------------------------------------------------------------------
# --diagnose-null-stability: one-time validation, never invoked by run_pipeline
# ---------------------------------------------------------------------------

def _diagnose_null_stability(*, n_replicates, reference_rows, edges, valid, profile, h, n_null,
                             seed, out_path):
    """Recompute W0^(b) for `n_replicates` bootstrap-style reference resamples
    (resample RPS volumes with replacement, rebuild LOVO q's + cell index
    from the resampled reference, simulate n_null pseudo-models against it)
    and W_obs^(b) (each valid answer's q_e1 recomputed against the same
    resampled reference), reporting sd(W0^(b)) and Corr(W_obs^(b), W0^(b)).
    Cost is dominated by re-running LOVO per replicate.
    """
    rng = random.Random(seed)
    volumes = sorted({r["volume_id"] for r in reference_rows})
    rows_by_volume = {}
    for r in reference_rows:
        rows_by_volume.setdefault(r["volume_id"], []).append(r)

    w0_draws, w_obs_draws = [], []
    for i in range(n_replicates):
        drawn_volumes = [rng.choice(volumes) for _ in volumes]
        resampled_rows = [dict(r) for vid in drawn_volumes for r in rows_by_volume[vid]]

        lovo_resampled = tp.compute_lovo_qs(resampled_rows, h, edges)
        cell_index_b = tp.build_cell_index(lovo_resampled)
        draws_b = []
        for _ in range(n_null):
            stats, _unmet = tp.simulate_pseudo_model(cell_index_b, profile, rng)
            draws_b.append(stats["W1"])
        w0_b = _mean(draws_b)
        w0_draws.append(w0_b)

        by_year_b = tp.index_reference_by_year(resampled_rows)
        q_e1_b = []
        for a in valid:
            q_e1, _q_e2, _n, _nv, _dnv, _wm = tp.qscore_answer(
                a["e1_mean"], a["e2_p_synthetic"], a["true_date"], a["n_words"], edges,
                by_year_b, h)
            q_e1_b.append(q_e1)
        clean_q_e1_b = [q for q in q_e1_b if not math.isnan(q)]
        w_obs_b = tp.wasserstein1_uniform(clean_q_e1_b) if clean_q_e1_b else float("nan")
        w_obs_draws.append(w_obs_b)
        print(f"  diagnose-null-stability {i + 1}/{n_replicates}: "
             f"W0^(b)={w0_b:.4f} W_obs^(b)={w_obs_b:.4f}", file=sys.stderr)

    sd_w0 = _sd(w0_draws)
    corr = _pearson_corr(w_obs_draws, w0_draws)
    lines = [
        "# score_style.py --diagnose-null-stability", "",
        f"n_replicates = {n_replicates}, n_null = {n_null}, h = {h}, seed = {seed}", "",
        f"sd(W0^(b)) = {sd_w0:.5f}",
        f"Corr(W_obs^(b), W0^(b)) = {corr:.4f}", "",
        "Compare sd(W0^(b)) against the reported score CI width (w1_ci95 in the main JSON): "
        "if sd(W0^(b)) is small relative to that width, holding W0 fixed at its point estimate "
        "inside every bootstrap replicate (rather than recomputing it per replicate) is validated "
        "empirically rather than by argument alone. See the Method note in the main markdown "
        "report for the full reasoning.", "",
    ]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return dict(sd_w0=sd_w0, corr=corr, n_replicates=n_replicates)


# ---------------------------------------------------------------------------
# main scoring flow
# ---------------------------------------------------------------------------

def run(args):
    resolved = _resolve(args)
    candidate_label = resolved["candidate_label"]
    benchmark_version = resolved["benchmark_version"]

    print(f"  loading reference {resolved['reference']}", file=sys.stderr)
    reference_rows = tp.read_jsonl(resolved["reference"])
    edges = tp.load_length_bin_edges(resolved["length_bin_edges"])
    tp.annotate_length_bins(reference_rows, edges)
    reference_by_year = tp.index_reference_by_year(reference_rows)

    # Always rebuild the answer-rows join for its counters (cheap: benchmark
    # read + word counts, no model inference) so n_generated/n_excluded_*
    # in the JSON reflect the real free-gen/benchmark join even when
    # --answers-q skips scoring -- otherwise a reuse-path report would
    # silently fabricate these as (n_answers_q, 0, 0, 0).
    answer_rows, answer_counts = _build_answer_rows(
        resolved["free_gen"], resolved["free_gen_path"], resolved["benchmark_path"],
        candidate_label, args.min_words)
    print(f"  {len(answer_rows)}/{answer_counts['n_generated']} answers usable "
         f"(excluded: {answer_counts['n_excluded_short']} short, "
         f"{answer_counts['n_excluded_missing_text']} missing text, "
         f"{answer_counts['n_excluded_unmatched']} unmatched)", file=sys.stderr)

    if args.answers_q:
        print(f"  reusing scored answers from {args.answers_q} (skipping E1/E2 inference)",
             file=sys.stderr)
        answers_q = tp.read_jsonl(args.answers_q)
    else:
        answers_q = _score_answers(
            answer_rows, edges, reference_by_year, e1_model_dir=resolved["e1_model_dir"],
            e2_run_dir=resolved["e2_run_dir"], temperature_fit=resolved["temperature_fit"],
            h=args.h, max_length=args.max_length, batch_size=args.batch_size, device=args.device)
        resolved["answers_q_out"].parent.mkdir(parents=True, exist_ok=True)
        tp.write_jsonl(answers_q, resolved["answers_q_out"])
        print(f"  wrote {resolved['answers_q_out']}", file=sys.stderr)

    valid = _valid(answers_q)
    n_excluded_empty_window = len(answers_q) - len(valid)
    if n_excluded_empty_window:
        print(f"  excluding {n_excluded_empty_window}/{len(answers_q)} answers with "
             f"empty/NaN windows from all model-level statistics", file=sys.stderr)
    if not valid:
        sys.exit("ERROR: no valid (non-empty-window) answers to score")

    lovo_rows = _lovo_with_cache(
        reference_rows, args.h, edges, reference_path=resolved["reference"],
        length_bin_edges_path=resolved["length_bin_edges"], cache_dir=args.lovo_cache_dir,
        use_cache=not args.no_lovo_cache)
    cell_index = tp.build_cell_index(lovo_rows)

    # Corrected years residuals: raw signed residual minus the SAME window
    # mean qscore_answer already computed (e1_null_window_mean), per the
    # wiring plan's year-baseline-correction section.
    corrected_residuals = [a["e1_signed_residual"] - a["e1_null_window_mean"] for a in valid]
    raw_residuals = [a["e1_signed_residual"] for a in valid]

    real_stats = tp.model_stats_from_qs(
        [a["q_e1"] for a in valid], [a["q_e2"] for a in valid], corrected_residuals,
        quantile_grid_n=args.quantile_grid_n)
    drift_mean_raw = _mean(raw_residuals)
    dispersion_mae_raw = _mean([abs(r) for r in raw_residuals])

    profile = {}
    for r in valid:
        cell = (tp.date_bin(r["true_date"]), r["length_bin"])
        profile[cell] = profile.get(cell, 0) + 1

    rng = random.Random(args.seed)
    print(f"  simulating {args.n_null} pseudo-model null draws...", file=sys.stderr)
    null_draws = []
    total_unmet = 0
    for _ in range(args.n_null):
        stats, unmet = tp.simulate_pseudo_model(cell_index, profile, rng,
                                                 quantile_grid_n=args.quantile_grid_n)
        null_draws.append(stats)
        total_unmet += unmet
    if total_unmet:
        print(f"    {total_unmet} pseudo-answer slots unmet across {args.n_null} draws "
             f"(empty cells in the RPS)", file=sys.stderr)

    w0_values = [d["W1"] for d in null_draws]
    w0 = _mean(w0_values)
    w0_sd = _sd(w0_values)
    w0_ci95 = _ci95(w0_values)
    mu0 = _mean([d["T_E2"] for d in null_draws])
    null_drift_mean = _mean([d.get("drift_years", float("nan")) for d in null_draws])
    null_dispersion_mae = _mean([d.get("dispersion_mae", float("nan")) for d in null_draws])

    e1_headline = tp.e1_period_fidelity(real_stats["W1"], w0)
    e2_headline = tp.e2_authenticity_fidelity(real_stats["T_E2"], mu0)
    d_e1 = max(0.0, real_stats["W1"] - w0) / (0.5 - w0) if w0 < 0.5 else float("nan")

    print(f"  two-way bootstrap ({args.n_boot} draws)...", file=sys.stderr)
    boot_stats = tp.two_way_bootstrap(
        valid, reference_rows, models=[candidate_label], by_model={candidate_label: valid},
        h=args.h, n_boot=args.n_boot, rng=rng, quantile_grid_n=args.quantile_grid_n)[candidate_label]

    boot_e1_headline = [tp.e1_period_fidelity(d["W1"], w0) for d in boot_stats
                        if not math.isnan(d["W1"])]
    boot_e2_headline = [tp.e2_authenticity_fidelity(d["T_E2"], mu0) for d in boot_stats
                        if not math.isnan(d["T_E2"])]

    def _boot_ci(key):
        return _ci95([d[key] for d in boot_stats])

    e1_headline_ci = _ci95(boot_e1_headline)
    e2_headline_ci = _ci95(boot_e2_headline)
    w1_ci = _boot_ci("W1")
    drift_years_ci = _boot_ci("drift_years")
    dispersion_mae_ci = _boot_ci("dispersion_mae")
    t_drift_ci = _boot_ci("T_drift")
    t_disp_ci = _boot_ci("T_disp")
    t_e2_ci = _boot_ci("T_E2")

    # Null band: per-grid-point 2.5/50/97.5 percentiles across the n_null
    # pseudo-models' own quantile grids (spec B §10's finite-sample envelope).
    null_grid = null_draws[0]["q_grid"]["grid"] if null_draws and "q_grid" in null_draws[0] else None
    if null_grid is not None:
        null_mq_stack = np.stack([d["q_grid"]["model_quantiles"] for d in null_draws], axis=0)
        null_band_median = np.percentile(null_mq_stack, 50, axis=0)
        null_band_lo = np.percentile(null_mq_stack, 2.5, axis=0)
        null_band_hi = np.percentile(null_mq_stack, 97.5, axis=0)
        q_curve = real_stats["q_grid"]
    else:
        q_curve = None

    ks, ks_null_mean = real_stats["T_KS"], _mean([d["T_KS"] for d in null_draws])
    median_window_n_volumes = statistics.median(
        [a["window_n_volumes"] for a in valid]) if valid else float("nan")
    thin_cell_frac = (sum(1 for a in valid if a["window_n_volumes"] < 60) / len(valid)
                      if valid else float("nan"))

    style_run_id = hashlib.sha256("|".join(str(x) for x in [
        naming.candidate_tag(candidate_label), benchmark_version,
        _sha256_file(resolved["reference"])[:12], str(resolved["e1_model_dir"]),
        str(resolved["e2_run_dir"]), args.h, args.seed, args.n_boot, args.n_null,
    ]).encode("utf-8")).hexdigest()[:16]

    result = {
        "schema_version": SCHEMA_VERSION,
        "model": {
            "name": candidate_label, "candidate_label": candidate_label,
            "candidate_model": resolved["candidate_model"],
            "candidate_effort": resolved["candidate_effort"],
            "benchmark_version": benchmark_version, "benchmark_path": str(resolved["benchmark_path"]),
            "free_gen_path": str(resolved["free_gen_path"]),
            "n_answers": len(valid), "n_answers_e1": real_stats["n_e1"],
            "n_answers_e2": real_stats["n_e2"], **answer_counts,
            "n_excluded_empty_window": n_excluded_empty_window,
        },
        "e1": {
            "headline": {"name": "period_fidelity", "score": e1_headline,
                        "ci95": list(e1_headline_ci)},
            "wasserstein": {"w1_observed": real_stats["W1"], "w1_ci95": list(w1_ci),
                           "w1_null_mean": w0, "w1_null_sd": w0_sd, "w1_null_ci95": list(w0_ci95),
                           "normalized_excess_distance": d_e1},
            "years": {"drift_mean": real_stats["drift_years"], "drift_ci95": list(drift_years_ci),
                     "dispersion_mae": real_stats["dispersion_mae"],
                     "dispersion_ci95": list(dispersion_mae_ci),
                     "drift_mean_raw": drift_mean_raw, "dispersion_mae_raw": dispersion_mae_raw,
                     "null_drift_mean": null_drift_mean, "null_dispersion_mae": null_dispersion_mae,
                     "baseline_correction": "per_answer_window_mean"},
            "conformal": {"drift": real_stats["T_drift"], "drift_ci95": list(t_drift_ci),
                         "drift_null_center": 0.5, "dispersion": real_stats["T_disp"],
                         "dispersion_ci95": list(t_disp_ci), "dispersion_null_center": 0.25},
            "quantile_curve": ({"grid": q_curve["grid"].tolist(),
                               "model_quantiles": q_curve["model_quantiles"].tolist(),
                               "deviation": q_curve["deviation"].tolist()}
                              if q_curve is not None else None),
            "quantile_null_band": ({"grid": null_grid.tolist(), "median": null_band_median.tolist(),
                                   "lower_95": null_band_lo.tolist(), "upper_95": null_band_hi.tolist()}
                                  if null_grid is not None else None),
        },
        "e2": {
            "headline": {"name": "authenticity_fidelity", "score": e2_headline,
                        "ci95": list(e2_headline_ci)},
            "conformal": {"mean_q": real_stats["T_E2"], "mean_q_ci95": list(t_e2_ci),
                         "null_center": mu0, "null_center_source": "pseudo_model_mean"},
        },
        "diagnostics": {"ks": ks, "ks_null_mean": ks_null_mean,
                        "median_window_n_volumes": median_window_n_volumes,
                        "thin_cell_frac": thin_cell_frac},
        "bootstrap": {"n_boot": args.n_boot, "seed": args.seed, "item_clustered": True,
                     "item_cluster_key": "question_number", "reference_volume_clustered": True,
                     "null_baselines_held_fixed": True,
                     "null_baselines_held_fixed_note": METHOD_NOTE},
        "null_simulation": {"n_pseudo_models": args.n_null,
                            "matched_on": ["date", "length", "candidate_suite_structure"],
                            "unmet_slots": total_unmet},
        "provenance": {"style_run_id": style_run_id, "produced_by": "stylejudge/score_style.py",
                      "produced_at": datetime.now(timezone.utc).isoformat(),
                      "git_head": git_head(), "reference_path": str(resolved["reference"]),
                      "reference_sha256": _sha256_file(resolved["reference"]),
                      "e1_model_dir": str(resolved["e1_model_dir"]),
                      "e2_run_dir": str(resolved["e2_run_dir"]), "temperature": tp.load_temperature(
                          resolved["temperature_fit"]),
                      "length_bin_edges": str(resolved["length_bin_edges"]), "h": args.h,
                      "quantile_method": "inverted_cdf"},
    }

    resolved["json_out"].parent.mkdir(parents=True, exist_ok=True)
    resolved["json_out"].write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"wrote {resolved['json_out']}", file=sys.stderr)

    if args.boot_out:
        # Raw per-draw bootstrap stats (candidate-scoped, unlike the retired
        # cohort-wide typicality.py model-report --boot-out) plus the full
        # n_null-length null W1 array (spec B §8 asks for the null
        # distribution itself, not just its mean/sd/ci95 -- those alone are
        # kept in the main JSON).
        boot_payload = {
            "boot_draws": [{k: v for k, v in d.items() if k != "q_grid"} for d in boot_stats],
            "null_w1_draws": w0_values,
        }
        Path(args.boot_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.boot_out).write_text(json.dumps(boot_payload, indent=1), encoding="utf-8")
        print(f"wrote {args.boot_out}", file=sys.stderr)

    report = _render_report(result)
    resolved["report_path"].parent.mkdir(parents=True, exist_ok=True)
    resolved["report_path"].write_text(report, encoding="utf-8")
    print(f"wrote {resolved['report_path']}", file=sys.stderr)

    if args.diagnose_null_stability:
        diag_out = resolved["json_out"].with_name(
            resolved["json_out"].stem + "_null_stability.md")
        _diagnose_null_stability(
            n_replicates=args.diagnose_null_stability, reference_rows=reference_rows, edges=edges,
            valid=valid, profile=profile, h=args.h, n_null=args.n_null, seed=args.seed,
            out_path=diag_out)

    print(f"\n{candidate_label}: Period Fidelity {e1_headline:.1f} {e1_headline_ci} "
         f"  Authenticity Fidelity {e2_headline:.1f} {e2_headline_ci}")
    return result


# ---------------------------------------------------------------------------
# markdown report (Spec B §15)
# ---------------------------------------------------------------------------

def _render_report(result: dict) -> str:
    m, e1, e2, diag = result["model"], result["e1"], result["e2"], result["diagnostics"]
    lines = [f"# Style score: {m['candidate_label']}", "",
             f"Benchmark `{m['benchmark_version']}` · n_answers={m['n_answers']} "
             f"(n_generated={m['n_generated']}, excluded: {m['n_excluded_short']} short, "
             f"{m['n_excluded_missing_text']} missing text, {m['n_excluded_unmatched']} unmatched, "
             f"{m['n_excluded_empty_window']} empty window)", ""]

    lines += ["## Headline scores", "",
             f"- **Period Fidelity**: {e1['headline']['score']:.1f} "
             f"(95% CI [{e1['headline']['ci95'][0]:.1f}, {e1['headline']['ci95'][1]:.1f}])",
             f"- **Authenticity Fidelity**: {e2['headline']['score']:.1f} "
             f"(95% CI [{e2['headline']['ci95'][0]:.1f}, {e2['headline']['ci95'][1]:.1f}])", ""]

    y = e1["years"]
    lines += ["## E1 (date) diagnostics -- years", "",
             f"- drift (corrected, headline): {y['drift_mean']:.2f} "
             f"[{y['drift_ci95'][0]:.2f}, {y['drift_ci95'][1]:.2f}] years "
             "(positive = reads too modern relative to genuine prose of the same period/length)",
             f"- dispersion (corrected, headline): {y['dispersion_mae']:.2f} "
             f"[{y['dispersion_ci95'][0]:.2f}, {y['dispersion_ci95'][1]:.2f}] years",
             f"- drift (raw, uncorrected): {y['drift_mean_raw']:.2f}; "
             f"dispersion (raw): {y['dispersion_mae_raw']:.2f}",
             f"- null drift/dispersion (instrument bias + noise floor for this candidate's "
             f"composition): {y['null_drift_mean']:.2f} / {y['null_dispersion_mae']:.2f}", ""]

    c = e1["conformal"]
    lines += ["## E1 (date) diagnostics -- conformal", "",
             f"- T_drift: {c['drift']:.4f} [{c['drift_ci95'][0]:.4f}, {c['drift_ci95'][1]:.4f}] "
             f"(null center {c['drift_null_center']})",
             f"- T_disp: {c['dispersion']:.4f} "
             f"[{c['dispersion_ci95'][0]:.4f}, {c['dispersion_ci95'][1]:.4f}] "
             f"(null center {c['dispersion_null_center']})", ""]

    w = e1["wasserstein"]
    lines += ["## W1 (period fidelity's underlying distance)", "",
             f"- W_obs: {w['w1_observed']:.4f} [{w['w1_ci95'][0]:.4f}, {w['w1_ci95'][1]:.4f}]",
             f"- W0 (null mean): {w['w1_null_mean']:.4f}, sd={w['w1_null_sd']:.4f}, "
             f"95% CI [{w['w1_null_ci95'][0]:.4f}, {w['w1_null_ci95'][1]:.4f}]",
             f"- normalized excess distance d_E1: {w['normalized_excess_distance']:.4f}", ""]

    ec = e2["conformal"]
    lines += ["## E2 (authenticity) diagnostics", "",
             f"- T_E2 (mean_q): {ec['mean_q']:.4f} "
             f"[{ec['mean_q_ci95'][0]:.4f}, {ec['mean_q_ci95'][1]:.4f}] "
             f"(null center {ec['null_center']:.4f}, source: {ec['null_center_source']})", ""]

    lines += ["## KS compatibility (diagnostic, not a headline)", "",
             f"- T_KS: {diag['ks']:.4f} (null mean {diag['ks_null_mean']:.4f})",
             f"- median window n_volumes: {diag['median_window_n_volumes']:.0f}; "
             f"thin-cell fraction (<60 volumes): {diag['thin_cell_frac']:.3f}", ""]

    lines += ["## Glossary", "",
             "- **Period Fidelity** (0-100): 100 when the model's date-residual distribution is "
             "indistinguishable from period-and-length-matched authentic prose (W_obs <= W0); "
             "0 at W1's maximum of 0.5.",
             "- **Authenticity Fidelity** (0-100): 100 when the E2 detector finds the model no "
             "more legible-as-synthetic than authentic prose (T_E2 <= null center); 0 at T_E2=1.",
             "- **W1**: exact Wasserstein-1 distance of the model's q_e1 distribution from "
             "Uniform(0,1) -- the period-fidelity headline's underlying distance.",
             "- **T_KS**: Kolmogorov-Smirnov statistic against Uniform(0,1); an omnibus check "
             "kept for compatibility with the legacy `typicality.py model-report`, not a headline.",
             "", "## Method note", "", METHOD_NOTE, ""]

    prov = result["provenance"]
    lines += ["## Provenance", "",
             f"- style_run_id: `{prov['style_run_id']}`",
             f"- produced_by: `{prov['produced_by']}` at {prov['produced_at']}",
             f"- git_head: `{prov['git_head']}`",
             f"- reference: `{prov['reference_path']}` (sha256 {prov['reference_sha256'][:16]}...)",
             f"- e1_model_dir: `{prov['e1_model_dir']}`; e2_run_dir: `{prov['e2_run_dir']}`",
             f"- temperature: {prov['temperature']:.4f}; h: {prov['h']}; "
             f"quantile_method: {prov['quantile_method']}",
             f"- bootstrap: n_boot={result['bootstrap']['n_boot']} seed={result['bootstrap']['seed']}; "
             f"null_simulation: n_pseudo_models={result['null_simulation']['n_pseudo_models']}", ""]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--free-gen", required=True,
                  help="modelasjudge/generated_answers/free_gen_{tag}__{ver}.json")
    p.add_argument("--benchmark", default=None,
                  help="default: free_gen's own benchmark_path, else booksample/chronologic_en_{ver}.jsonl")
    p.add_argument("--candidate-label", default=None,
                  help="default: free_gen's candidate_label or model -- the identity key")
    p.add_argument("--reference", default=None, help="default: typicality.DEFAULT_REFERENCE_OUT")
    p.add_argument("--e1-model-dir", default=None)
    p.add_argument("--e2-run-dir", default=None)
    p.add_argument("--temperature-fit", default=None)
    p.add_argument("--length-bin-edges", default=None)
    p.add_argument("--h", type=int, default=DEFAULT_H)
    p.add_argument("--min-words", type=int, default=DEFAULT_MIN_WORDS)
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--device", default="auto")
    p.add_argument("--n-null", type=int, default=DEFAULT_N_NULL)
    p.add_argument("--n-boot", type=int, default=DEFAULT_N_BOOT)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--quantile-grid-n", type=int, default=DEFAULT_QUANTILE_GRID_N)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--json-out", default=None)
    p.add_argument("--report", default=None)
    p.add_argument("--boot-out", default=None,
                  help="optional raw per-draw bootstrap stats + the full n_null-length null W1 array")
    p.add_argument("--answers-q", default=None,
                  help="reuse an existing scored-answer JSONL; skips all E1/E2 inference")
    p.add_argument("--answers-q-out", default=None)
    p.add_argument("--intermediate-dir", default=str(DEFAULT_INTERMEDIATE_DIR))
    p.add_argument("--lovo-cache", dest="lovo_cache_dir", default=str(DEFAULT_INTERMEDIATE_DIR),
                  metavar="DIR", help="directory for the shared, content-hashed LOVO cache file")
    p.add_argument("--no-lovo-cache", action="store_true")
    p.add_argument("--diagnose-null-stability", type=int, default=0, metavar="N",
                  help="one-time validation: recompute W0^(b) for N bootstrap replicates "
                       "(~31s/replicate); never invoked by run_pipeline")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    main()
