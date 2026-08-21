"""test_viz_scripts.py — smoke tests for modelasjudge/viz_scripts/ (Spec B
Appendix A1-A4 + the shared style_report_io loader). Agg backend throughout;
no real model inference, no network."""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

VIZ_DIR = Path(__file__).parent.parent / "viz_scripts"
sys.path.insert(0, str(VIZ_DIR))

import style_report_io as srio  # noqa: E402
import plot_style_quantiles  # noqa: E402
import plot_style_scatter  # noqa: E402
import plot_style_diagnostics  # noqa: E402
import compare_w1_ks_rankings  # noqa: E402


def _synthetic_report(candidate_label, benchmark_version="0.7", *, seed_offset=0.0):
    import numpy as np
    grid = list(np.linspace(0.0, 1.0, 21))
    model_quantiles = [g + 0.05 * seed_offset for g in grid]
    deviation = [mq - g for mq, g in zip(model_quantiles, grid)]
    return {
        "schema_version": "stylejudge-2.0",
        "model": {"name": candidate_label, "candidate_label": candidate_label,
                  "candidate_model": candidate_label, "benchmark_version": benchmark_version,
                  "n_answers": 100},
        "e1": {
            "headline": {"name": "period_fidelity", "score": 80.0 + seed_offset,
                        "ci95": [75.0 + seed_offset, 85.0 + seed_offset]},
            "wasserstein": {"w1_observed": 0.05 + 0.01 * seed_offset, "w1_ci95": [0.03, 0.08],
                           "w1_null_mean": 0.01, "w1_null_sd": 0.003, "w1_null_ci95": [0.005, 0.02],
                           "normalized_excess_distance": 0.1},
            "years": {"drift_mean": -5.0 + seed_offset, "drift_ci95": [-8.0, -2.0],
                     "dispersion_mae": 18.0, "dispersion_ci95": [16.0, 20.0],
                     "drift_mean_raw": -15.0, "dispersion_mae_raw": 28.0,
                     "null_drift_mean": -14.0, "null_dispersion_mae": 26.0,
                     "baseline_correction": "per_answer_window_mean"},
            "conformal": {"drift": 0.45 + 0.01 * seed_offset, "drift_ci95": [0.40, 0.50],
                         "drift_null_center": 0.5, "dispersion": 0.24, "dispersion_ci95": [0.22, 0.26],
                         "dispersion_null_center": 0.25},
            "quantile_curve": {"grid": grid, "model_quantiles": model_quantiles, "deviation": deviation},
            "quantile_null_band": {"grid": grid, "median": grid, "lower_95": [g - 0.05 for g in grid],
                                  "upper_95": [g + 0.05 for g in grid]},
        },
        "e2": {
            "headline": {"name": "authenticity_fidelity", "score": 30.0 + seed_offset,
                        "ci95": [25.0 + seed_offset, 35.0 + seed_offset]},
            "conformal": {"mean_q": 0.85, "mean_q_ci95": [0.80, 0.90], "null_center": 0.5,
                         "null_center_source": "pseudo_model_mean"},
        },
        "diagnostics": {"ks": 0.1 + 0.01 * seed_offset, "ks_null_mean": 0.03,
                       "median_window_n_volumes": 70, "thin_cell_frac": 0.02},
        "bootstrap": {"n_boot": 100, "seed": 1},
        "provenance": {"style_run_id": f"run{seed_offset}"},
    }


def _write_reports(tmp_path, n=2, benchmark_version="0.7"):
    paths = []
    for i in range(n):
        rec = _synthetic_report(f"model{i}", benchmark_version=benchmark_version, seed_offset=float(i))
        path = tmp_path / f"style_report_model{i}__{benchmark_version}.json"
        path.write_text(json.dumps(rec), encoding="utf-8")
        paths.append(path)
    return paths


# ---------------------------------------------------------------------------
# style_report_io
# ---------------------------------------------------------------------------

def test_load_reports_rejects_wrong_schema_version(tmp_path, capsys):
    good = tmp_path / "style_report_a__0.7.json"
    good.write_text(json.dumps(_synthetic_report("a")), encoding="utf-8")
    bad = tmp_path / "style_report_b__0.7.json"
    bad_rec = _synthetic_report("b")
    bad_rec["schema_version"] = "typicality-1.0"
    bad.write_text(json.dumps(bad_rec), encoding="utf-8")

    records = srio.load_reports(tmp_path)
    assert len(records) == 1
    assert records[0]["model"]["candidate_label"] == "a"


def test_load_reports_default_keeps_only_newest_version(tmp_path, capsys):
    _write_reports(tmp_path, n=1, benchmark_version="0.4")
    (tmp_path / "style_report_model0__0.4.json").rename(tmp_path / "style_report_old__0.4.json")
    _write_reports(tmp_path, n=1, benchmark_version="0.7")

    records = srio.load_reports(tmp_path)
    versions = {r["model"]["benchmark_version"] for r in records}
    assert versions == {"0.7"}


def test_load_reports_all_versions_flag(tmp_path):
    _write_reports(tmp_path, n=1, benchmark_version="0.4")
    (tmp_path / "style_report_model0__0.4.json").rename(tmp_path / "style_report_old__0.4.json")
    _write_reports(tmp_path, n=1, benchmark_version="0.7")

    records = srio.load_reports(tmp_path, all_versions=True)
    versions = {r["model"]["benchmark_version"] for r in records}
    assert versions == {"0.4", "0.7"}


def test_label_of_names_and_numbers():
    rec = _synthetic_report("gpt-5.4")
    assert srio.label_of(rec, "names") == "gpt-5.4"
    assert srio.label_of(rec, "numbers", index=0) == "1: gpt-5.4"


def test_err_bars_clamped_nonnegative():
    lo, hi = srio.err_bars(5.0, (4.0, 6.0))
    assert lo == 1.0 and hi == 1.0
    lo, hi = srio.err_bars(5.0, (5.5, 6.0))  # point below its own CI lower bound
    assert lo == 0.0


# ---------------------------------------------------------------------------
# A1: plot_style_quantiles
# ---------------------------------------------------------------------------

def test_plot_style_quantiles_writes_nonempty_png(tmp_path):
    paths = _write_reports(tmp_path, n=1)
    out_path = tmp_path / "q.png"
    plot_style_quantiles.main([str(paths[0]), "--out", str(out_path)])
    assert out_path.exists() and out_path.stat().st_size > 0


def test_plot_style_quantiles_quantile_mode(tmp_path):
    paths = _write_reports(tmp_path, n=1)
    out_path = tmp_path / "q2.png"
    plot_style_quantiles.main([str(paths[0]), "--out", str(out_path), "--mode", "quantile",
                              "--no-null-band", "--no-annotate"])
    assert out_path.exists() and out_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# A2: plot_style_scatter
# ---------------------------------------------------------------------------

def test_plot_style_scatter_writes_nonempty_png(tmp_path):
    _write_reports(tmp_path, n=3)
    out_path = tmp_path / "scatter.png"
    plot_style_scatter.main([str(tmp_path), "--out", str(out_path)])
    assert out_path.exists() and out_path.stat().st_size > 0


def test_plot_style_scatter_full_scale(tmp_path):
    _write_reports(tmp_path, n=2)
    out_path = tmp_path / "scatter_fs.png"
    plot_style_scatter.main([str(tmp_path), "--out", str(out_path), "--full-scale",
                            "--label-mode", "numbers"])
    assert out_path.exists() and out_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# A3: plot_style_diagnostics
# ---------------------------------------------------------------------------

def test_plot_style_diagnostics_both_writes_two_pngs(tmp_path):
    _write_reports(tmp_path, n=2)
    plot_style_diagnostics.main([str(tmp_path), "--mode", "both", "--out-dir", str(tmp_path)])
    conformal = tmp_path / "style_diagnostics_conformal.png"
    years = tmp_path / "style_diagnostics_years.png"
    assert conformal.exists() and conformal.stat().st_size > 0
    assert years.exists() and years.stat().st_size > 0


# ---------------------------------------------------------------------------
# A4: compare_w1_ks_rankings
# ---------------------------------------------------------------------------

def test_compare_w1_ks_rankings_spearman_one_for_identical_orderings(tmp_path):
    """Two candidates whose W1 and T_KS both order the same way -> Spearman
    rho == 1.0 (trivially true for n=2 with distinct values, but pins the
    computation path end-to-end)."""
    _write_reports(tmp_path, n=2)
    out_md = tmp_path / "rankings.md"
    out_plot = tmp_path / "rankings.png"
    compare_w1_ks_rankings.main([str(tmp_path), "--out-md", str(out_md), "--out-plot", str(out_plot)])
    assert out_md.exists()
    text = out_md.read_text()
    assert "rho=1.0000" in text
    assert out_plot.exists() and out_plot.stat().st_size > 0


def test_compare_w1_ks_rankings_include_cvm(tmp_path):
    _write_reports(tmp_path, n=2)
    out_md = tmp_path / "rankings_cvm.md"
    compare_w1_ks_rankings.main([str(tmp_path), "--out-md", str(out_md), "--include-cvm"])
    text = out_md.read_text()
    assert "CvM-proxy" in text
