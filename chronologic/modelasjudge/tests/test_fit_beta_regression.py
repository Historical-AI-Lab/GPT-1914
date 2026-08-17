"""test_fit_beta_regression.py — Unit tests for fit_beta_regression_nocontext.py.

Pure-function tests; no network calls, no LLM, no PyMC sampling.
The synthetic-recovery test (marked slow) samples a tiny MCMC chain.

Run with:
    pytest modelasjudge/tests/test_fit_beta_regression.py -v
    pytest modelasjudge/tests/test_fit_beta_regression.py -v -m "not slow"
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from fit_beta_regression_nocontext import (
    FRAME_TYPES,
    _FRAME_IDX,
    _infer_frame_type,
    _moment_match_beta,
    _ci,
    _summarize_two_beta_draws,
    prepare_data,
    post_stratify,
    save_draw_bank,
)
from substantive.artifacts import load_npz


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pair_rec(qnum, orig_len, frame_type, n_valid=2, k_nontie=1, k_A=1, k_B=0,
              invalid=0, reasoning_type="knowledge",
              judge_model="test/judge", reasoning_effort="none",
              benchmark_version="0.3"):
    return {
        "pair_id":         f"alt:{qnum}",
        "question_number": str(qnum),
        "source":          "alt",
        "frame_type":      frame_type,
        "reasoning_type":  reasoning_type,
        "orig_len":        orig_len,
        "n_valid_trials":  n_valid,
        "k_nontie":        k_nontie,
        "k_A":             k_A,
        "k_B":             k_B,
        "invalid":         invalid,
        "judge_model":     judge_model,
        "reasoning_effort":reasoning_effort,
        "benchmark_version": benchmark_version,
    }


def _bm_rec(qnum, frame_type, gt_text, reasoning_type="knowledge"):
    return {
        "question_number": qnum,
        "frame_type":      frame_type,
        "reasoning_type":  reasoning_type,
        "answer_strings":  [gt_text, "distractor"],
        "answer_types":    ["ground_truth", "manual"],
    }


# ---------------------------------------------------------------------------
# _moment_match_beta
# ---------------------------------------------------------------------------

class TestMomentMatchBeta:
    def test_valid_moment_match(self):
        mu, var = 0.3, 0.02
        result = _moment_match_beta(mu, var)
        assert result is not None
        assert result["alpha"] > 0
        assert result["beta"] > 0
        # Check: mean = alpha / (alpha + beta) ≈ mu
        a, b = result["alpha"], result["beta"]
        assert abs(a / (a + b) - mu) < 0.01

    def test_zero_variance_returns_none(self):
        assert _moment_match_beta(0.3, 0.0) is None

    def test_negative_variance_returns_none(self):
        assert _moment_match_beta(0.3, -0.01) is None

    def test_mu_zero_returns_none(self):
        assert _moment_match_beta(0.0, 0.01) is None

    def test_mu_one_returns_none(self):
        assert _moment_match_beta(1.0, 0.01) is None

    def test_very_small_variance_gives_large_concentration(self):
        result = _moment_match_beta(0.3, 1e-5)
        assert result is not None
        c = result["alpha"] + result["beta"]
        assert c > 100   # high concentration = small variance


# ---------------------------------------------------------------------------
# _ci and _summarize_two_beta_draws
# ---------------------------------------------------------------------------

class TestCiAndSummarize:
    def test_ci_percentiles(self):
        draws = np.linspace(0, 1, 1000)
        lo, hi = _ci(draws)
        assert abs(lo - 0.03) < 0.005
        assert abs(hi - 0.97) < 0.005

    def test_summarize_fields(self):
        draws = np.full(100, 0.4)
        s = _summarize_two_beta_draws(draws)
        assert s["two_beta_mean"] == pytest.approx(0.4)
        assert s["beta_mean"] == pytest.approx(0.2)
        assert s["two_beta_ci"] == [pytest.approx(0.4), pytest.approx(0.4)]

    def test_summarize_beta_is_half(self):
        rng = np.random.default_rng(0)
        draws = rng.uniform(0.1, 0.5, 500)
        s = _summarize_two_beta_draws(draws)
        assert abs(s["beta_mean"] - s["two_beta_mean"] / 2) < 1e-4


# ---------------------------------------------------------------------------
# prepare_data
# ---------------------------------------------------------------------------

class TestPrepareData:
    def _make_minimal(self):
        pairs = [
            _pair_rec(1, orig_len=20, frame_type="world_context",   n_valid=2, k_nontie=1),
            _pair_rec(2, orig_len=80, frame_type="book_context",    n_valid=2, k_nontie=0),
            _pair_rec(3, orig_len=50, frame_type="passage_context", n_valid=1, k_nontie=1),
        ]
        bm = [
            _bm_rec(1,  "world_context",   "short answer"),
            _bm_rec(2,  "book_context",    "a moderately lengthy answer about books"),
            _bm_rec(3,  "passage_context", "passage answer with some length"),
            _bm_rec(99, "world_context",   "prediction only"),  # no matching pair
        ]
        return pairs, bm

    def test_fitting_arrays_shape(self):
        pairs, bm = self._make_minimal()
        data = prepare_data(pairs, bm)
        assert len(data["n"]) == 3
        assert len(data["k"]) == 3
        assert len(data["frame_idx"]) == 3
        assert len(data["z_loglen"]) == 3

    def test_population_covers_all_benchmark_questions(self):
        pairs, bm = self._make_minimal()
        data = prepare_data(pairs, bm)
        assert len(data["pop_qnums"]) == 4   # all 4 benchmark questions
        assert "99" in data["pop_qnums"]

    def test_raw_counts_correct(self):
        pairs, bm = self._make_minimal()
        data = prepare_data(pairs, bm)
        rc = data["raw_counts"]
        assert rc["n_pairs"] == 3
        assert rc["n_trials"] == 5   # 2+2+1
        assert rc["k_nontie"] == 2   # 1+0+1

    def test_standardization_constants(self):
        pairs, bm = self._make_minimal()
        data = prepare_data(pairs, bm)
        # mu_loglen and sd_loglen must be finite
        assert math.isfinite(data["mu_loglen"])
        assert math.isfinite(data["sd_loglen"])
        assert data["sd_loglen"] > 0

    def test_z_loglen_uses_population_standardization(self):
        """z_loglen must be (log(orig_len) - mu_pop) / sd_pop, not pair-local."""
        pairs = [_pair_rec(1, orig_len=20, frame_type="world_context")]
        bm    = [_bm_rec(1, "world_context", "short")]
        data  = prepare_data(pairs, bm)
        expected_z = (math.log(20) - data["mu_loglen"]) / data["sd_loglen"]
        assert abs(data["z_loglen"][0] - expected_z) < 1e-9

    def test_pairs_with_zero_valid_trials_excluded_from_arrays(self):
        pairs = [
            _pair_rec(1, 20, "world_context", n_valid=0, k_nontie=0),
            _pair_rec(2, 30, "world_context", n_valid=2, k_nontie=1),
        ]
        bm = [_bm_rec(1, "world_context", "a"), _bm_rec(2, "world_context", "b")]
        data = prepare_data(pairs, bm)
        assert len(data["n"]) == 1   # only pair 2
        assert data["raw_counts"]["n_pairs"] == 2   # both counted in raw

    def test_pairs_with_unknown_frame_type_excluded_from_arrays(self):
        pairs = [
            _pair_rec(1, 20, "mystery_type", n_valid=2, k_nontie=1),
            _pair_rec(2, 30, "world_context", n_valid=2, k_nontie=0),
        ]
        bm = [_bm_rec(2, "world_context", "b")]
        data = prepare_data(pairs, bm)
        assert len(data["n"]) == 1   # only world_context pair

    def test_pair_by_qnum_index(self):
        pairs, bm = self._make_minimal()
        data = prepare_data(pairs, bm)
        assert "1" in data["pair_by_qnum"]
        assert "99" not in data["pair_by_qnum"]

    def test_metadata_extracted_from_first_record(self):
        pairs, bm = self._make_minimal()
        data = prepare_data(pairs, bm)
        assert data["judge_model"] == "test/judge"
        assert data["benchmark_version"] == "0.3"
        assert data["reasoning_effort"] == "none"


# ---------------------------------------------------------------------------
# post_stratify (mock trace)
# ---------------------------------------------------------------------------

class MockTrace:
    """Minimal stand-in for an ArviZ InferenceData trace."""
    def __init__(self, b0, b_len, u_frame):
        """Args are scalar/array values; posterior contains single-draw 1-chain."""
        import xarray as xr

        n_frames = len(FRAME_TYPES)
        # Shape conventions: (chain=1, draw=1, ...) for PyMC output
        self.posterior = xr.Dataset({
            "b0":      xr.DataArray([[b0]], dims=["chain", "draw"]),
            "b_len":   xr.DataArray([[b_len]], dims=["chain", "draw"]),
            "u_frame": xr.DataArray(
                [[[u_frame[i] for i in range(n_frames)]]],
                dims=["chain", "draw", "frame"]
            ),
        })
        self.sample_stats = xr.Dataset({
            "diverging": xr.DataArray([[False]], dims=["chain", "draw"])
        })


class TestPostStratify:
    def _make_data_uniform(self, n_pairs=6):
        """All pairs are world_context, same length, half failures."""
        pairs = [
            _pair_rec(i, orig_len=30, frame_type="world_context",
                      n_valid=2, k_nontie=1, k_A=1, k_B=0)
            for i in range(1, n_pairs + 1)
        ]
        bm = [
            _bm_rec(i, "world_context", "answer " * 3)
            for i in range(1, 10)
        ]
        return prepare_data(pairs, bm)

    def test_population_two_beta_mean_is_fraction(self):
        data = self._make_data_uniform()
        # b0=-0.5, no length effect, no frame effect => sigmoid(-0.5) ≈ 0.378
        trace = MockTrace(b0=-0.5, b_len=0.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        pop = results["population"]
        assert 0 < pop["two_beta_mean"] < 1
        assert pop["beta_mean"] == pytest.approx(pop["two_beta_mean"] / 2, abs=1e-4)

    def test_per_question_covers_all_benchmark_qnums(self):
        pairs = [_pair_rec(1, 20, "world_context")]
        bm    = [_bm_rec(1, "world_context", "x"), _bm_rec(2, "world_context", "y")]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=0.0, b_len=0.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        assert "1" in results["per_question"]
        assert "2" in results["per_question"]

    def test_per_question_raw_counts_filled_for_observed_qnums(self):
        pairs = [_pair_rec(7, 20, "world_context", n_valid=2, k_nontie=1)]
        bm    = [_bm_rec(7, "world_context", "hello")]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=0.0, b_len=0.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        pq = results["per_question"]["7"]
        assert pq["n_trials"] == 2
        assert pq["k_nontie"] == 1

    def test_per_question_raw_counts_null_for_prediction_only(self):
        pairs = [_pair_rec(1, 20, "world_context")]
        bm    = [_bm_rec(1, "world_context", "x"),
                 _bm_rec(99, "world_context", "prediction only question")]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=0.0, b_len=0.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        pq = results["per_question"]["99"]
        assert pq["n_trials"] is None
        assert pq["k_nontie"] is None

    def test_beta_mean_is_half_two_beta_mean(self):
        pairs = [_pair_rec(i, 30, "world_context") for i in range(1, 4)]
        bm    = [_bm_rec(i, "world_context", "answer") for i in range(1, 5)]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=-0.3, b_len=0.1, u_frame=[0.05, -0.05, 0.0])
        results = post_stratify(trace, data)
        for pq in results["per_question"].values():
            assert abs(pq["beta_mean"] - pq["two_beta_mean"] / 2) < 1e-4

    def test_positive_b_len_increases_two_beta_with_longer_answer(self):
        """Longer answers should give higher 2β when b_len is positive."""
        pairs = [
            _pair_rec(1, orig_len=10,  frame_type="world_context"),
            _pair_rec(2, orig_len=200, frame_type="world_context"),
        ]
        bm = [
            _bm_rec(1, "world_context", "x"),    # short
            _bm_rec(2, "world_context", "x" * 200),  # long
        ]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=0.0, b_len=2.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        two_beta_1 = results["per_question"]["1"]["two_beta_mean"]
        two_beta_2 = results["per_question"]["2"]["two_beta_mean"]
        assert two_beta_2 > two_beta_1

    def test_position_symmetry_binomial_p_included(self):
        pairs = [_pair_rec(i, 20, "world_context", k_A=1, k_B=1) for i in range(1, 3)]
        bm    = [_bm_rec(i, "world_context", "x") for i in range(1, 4)]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=0.0, b_len=0.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        ps = results["position_symmetry"]
        assert "k_A" in ps and "k_B" in ps and "binomial_p" in ps

    def test_two_beta_beta_dist_is_none_for_single_draw(self):
        """With only 1 posterior draw, variance=0 and moment-match returns None."""
        pairs = [_pair_rec(1, 20, "world_context")]
        bm    = [_bm_rec(1, "world_context", "x")]
        data  = prepare_data(pairs, bm)
        trace = MockTrace(b0=0.0, b_len=0.0, u_frame=[0.0, 0.0, 0.0])
        results = post_stratify(trace, data)
        # variance is 0 with one draw => moment-match returns None
        assert results["per_question"]["1"]["two_beta_beta_dist"] is None


# ---------------------------------------------------------------------------
# save_draw_bank
# ---------------------------------------------------------------------------

class MockTraceMultiDraw:
    """Like MockTrace, but with many draws so thinning is meaningful."""
    def __init__(self, n_draws, seed=0):
        import xarray as xr

        rng = np.random.default_rng(seed)
        n_frames = len(FRAME_TYPES)
        b0 = rng.normal(-1.0, 0.2, size=(1, n_draws))
        b_len = rng.normal(0.3, 0.1, size=(1, n_draws))
        u_frame = rng.normal(0.0, 0.3, size=(1, n_draws, n_frames))
        self.posterior = xr.Dataset({
            "b0": xr.DataArray(b0, dims=["chain", "draw"]),
            "b_len": xr.DataArray(b_len, dims=["chain", "draw"]),
            "u_frame": xr.DataArray(u_frame, dims=["chain", "draw", "frame"]),
        })
        self.sample_stats = xr.Dataset({
            "diverging": xr.DataArray(np.zeros((1, n_draws), dtype=bool), dims=["chain", "draw"])
        })


class TestSaveDrawBank:
    def _data(self, n_pairs=20):
        pairs = [
            _pair_rec(i, orig_len=20 + i, frame_type=FRAME_TYPES[i % 3],
                      n_valid=2, k_nontie=int(i % 3 == 0))
            for i in range(1, n_pairs + 1)
        ]
        bm = [_bm_rec(i, FRAME_TYPES[i % 3], "answer " * 3) for i in range(1, n_pairs + 1)]
        return prepare_data(pairs, bm)

    def test_shapes_and_thinning(self, tmp_path):
        data = self._data()
        trace = MockTraceMultiDraw(n_draws=500)
        path = tmp_path / "beta_draws.npz"
        meta = save_draw_bank(trace, data, path=path, thin=100, judge_model="test/judge",
                              judge_effort="none", benchmark_path="bench.jsonl", seed=1)
        arrays, loaded_meta = load_npz(path)
        assert arrays["b0"].shape == (100,)
        assert arrays["b_len"].shape == (100,)
        assert arrays["u_frame"].shape == (100, len(FRAME_TYPES))
        assert loaded_meta["n_draws"] == 100
        assert loaded_meta["n_draws_source"] == 500
        assert meta == loaded_meta

    def test_thin_larger_than_source_keeps_everything(self, tmp_path):
        data = self._data()
        trace = MockTraceMultiDraw(n_draws=50)
        path = tmp_path / "beta_draws.npz"
        save_draw_bank(trace, data, path=path, thin=5000, judge_model="test/judge",
                       judge_effort="none", benchmark_path="bench.jsonl", seed=1)
        arrays, meta = load_npz(path)
        assert arrays["b0"].shape == (50,)
        assert meta["n_draws"] == 50

    def test_frame_types_order_matches_module_constant(self, tmp_path):
        data = self._data()
        trace = MockTraceMultiDraw(n_draws=200)
        path = tmp_path / "beta_draws.npz"
        save_draw_bank(trace, data, path=path, thin=200, judge_model="test/judge",
                       judge_effort="none", benchmark_path="bench.jsonl", seed=1)
        _, meta = load_npz(path)
        assert meta["frame_types"] == list(FRAME_TYPES)

    def test_standardization_is_full_precision_not_rounded(self, tmp_path):
        data = self._data()
        # force a standardization value that would lose information at 4dp
        data["mu_loglen"] = 4.31967928288946123
        data["sd_loglen"] = 1.25910657919594331
        trace = MockTraceMultiDraw(n_draws=200)
        path = tmp_path / "beta_draws.npz"
        save_draw_bank(trace, data, path=path, thin=200, judge_model="test/judge",
                       judge_effort="none", benchmark_path="bench.jsonl", seed=1)
        _, meta = load_npz(path)
        assert meta["standardization"]["mu_loglen"] == data["mu_loglen"]
        assert meta["standardization"]["sd_loglen"] == data["sd_loglen"]

    def test_meta_carries_sigma_u_and_diagnostics(self, tmp_path):
        data = self._data()
        trace = MockTraceMultiDraw(n_draws=200)
        path = tmp_path / "beta_draws.npz"
        save_draw_bank(trace, data, path=path, thin=200, judge_model="test/judge",
                       judge_effort="none", benchmark_path="bench.jsonl", seed=1)
        _, meta = load_npz(path)
        assert meta["sigma_u"] >= 0.0
        assert "overdispersion_ratio" in meta["sigma_u_diagnostics"]
        assert "underdispersed" in meta["sigma_u_diagnostics"]


# ---------------------------------------------------------------------------
# Synthetic recovery (slow; skipped by default)
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_synthetic_recovery():
    """Generate data with known parameters; fit a tiny chain; check recovery.

    This test does run PyMC MCMC (2 chains × 200 draws).  It is marked slow
    and excluded from the default test run.  Run with -m slow to include it.
    """
    from fit_beta_regression_nocontext import fit_model
    from scipy.special import expit

    rng = np.random.default_rng(42)

    # True parameters
    true_b0    = -1.0
    true_b_len = 0.5
    true_u     = np.array([0.3, -0.2, 0.0])   # world, book, passage

    # Generate synthetic pairs
    n_per_frame = 30
    pair_records = []
    bm_records = []
    qnum = 1
    for fi, fname in enumerate(FRAME_TYPES):
        for _ in range(n_per_frame):
            z = rng.normal(0, 1)
            orig_len = max(1, int(math.exp(z * 0.8 + 3.0)))
            logit_p = true_b0 + true_u[fi] + true_b_len * z
            p = expit(logit_p)
            k = int(rng.binomial(2, p))
            pair_records.append(_pair_rec(
                qnum, orig_len, fname,
                n_valid=2, k_nontie=k, k_A=k // 2, k_B=k - k // 2,
            ))
            bm_records.append(_bm_rec(qnum, fname, "x" * orig_len))
            qnum += 1

    data = prepare_data(pair_records, bm_records)

    trace = fit_model(data, draws=200, tune=200, chains=2, seed=42)

    b0_mean   = float(trace.posterior["b0"].values.mean())
    b_len_mean = float(trace.posterior["b_len"].values.mean())

    assert abs(b0_mean   - true_b0)    < 0.5, f"b0: {b0_mean:.2f} vs {true_b0}"
    assert abs(b_len_mean - true_b_len) < 0.4, f"b_len: {b_len_mean:.2f} vs {true_b_len}"
