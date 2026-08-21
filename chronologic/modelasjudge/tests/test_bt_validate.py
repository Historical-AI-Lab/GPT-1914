"""test_bt_validate.py — direct unit tests for bt/validate.py helpers
(roc_from_loo, bootstrap_auc, bias_stats) using synthetic LooRecords, no
PyMC fitting required.

Run with:
    pytest modelasjudge/tests/test_bt_validate.py -v
"""

import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from bt.tau import CandidateScore
from bt.validate import (LooRecord, bias_stats, bootstrap_auc, dedupe_judgments,
                         roc_from_loo)


def make_score(tau_mean):
    return CandidateScore(tau_draws=None, delta_draws=None, tau_mean=tau_mean,
                          tau_ci=(tau_mean, tau_mean), delta_mean=0.0,
                          delta_ci=(0.0, 0.0), reference_gt="gt0", n_comparisons=10)


class TestRocFromLoo:
    def test_perfect_separation_gives_auc_one(self):
        records = (
            [LooRecord("q1", "gt1", "ground_truth", "gt0", make_score(0.9)) for _ in range(5)]
            + [LooRecord("q1", "d0", "distractor", "gt0", make_score(0.1)) for _ in range(5)]
        )
        result = roc_from_loo(records)
        assert result["auc"] == 1.0
        assert result["alpha_at_t_star"] == 0.0
        assert result["beta_at_t_star"] == 0.0

    def test_no_separation_gives_auc_half(self):
        records = (
            [LooRecord("q1", "gt1", "ground_truth", "gt0", make_score(0.5)) for _ in range(10)]
            + [LooRecord("q1", "d0", "distractor", "gt0", make_score(0.5)) for _ in range(10)]
        )
        result = roc_from_loo(records)
        assert abs(result["auc"] - 0.5) < 1e-9

    def test_requires_both_classes(self):
        records = [LooRecord("q1", "gt1", "ground_truth", "gt0", make_score(0.9))]
        with pytest.raises(ValueError):
            roc_from_loo(records)


class TestPartialCreditExclusion:
    """Answers human judges scored 0 < p < 1 are neither positives nor
    negatives, so they must not enter alpha, beta, or the AUC."""

    def _base(self):
        return (
            [LooRecord("q1", "gt1", "ground_truth", "gt0", make_score(0.9))] * 5
            + [LooRecord("q1", f"d{i}", "distractor", "gt0", make_score(0.1)) for i in range(5)]
        )

    def test_partial_records_do_not_change_the_roc(self):
        clean = roc_from_loo(self._base())
        # A partial-credit answer sitting right in the middle would wreck
        # perfect separation if it were counted as a distractor.
        with_partial = roc_from_loo(
            self._base()
            + [LooRecord("q1", "d9", "distractor", "gt0", make_score(0.55), prob=0.25)]
        )
        assert with_partial["auc"] == clean["auc"] == 1.0
        assert with_partial["alpha_at_t_star"] == 0.0
        assert with_partial["n_excluded_partial"] == 1
        assert clean["n_excluded_partial"] == 0
        assert with_partial["n_distractor"] == clean["n_distractor"] == 5

    def test_partial_records_excluded_from_bootstrap(self):
        by_q = {
            f"q{i}": [
                LooRecord(f"q{i}", "gt1", "ground_truth", "gt0", make_score(0.8)),
                LooRecord(f"q{i}", "d0", "distractor", "gt0", make_score(0.2)),
                LooRecord(f"q{i}", "d1", "distractor", "gt0", make_score(0.9), prob=0.75),
            ]
            for i in range(20)
        }
        lo, hi = bootstrap_auc(by_q, n_boot=200, seed=1)
        assert lo == hi == 1.0

    def test_probability_zero_distractor_still_counts(self):
        result = roc_from_loo(self._base())
        assert result["n_distractor"] == 5
        assert result["n_excluded_partial"] == 0


class TestDedupeJudgments:
    """append_jsonl appends, so re-running a phase leaves duplicate rows in
    the judgment log; counts reconstructed from it must not double-count."""

    def _row(self, first, second, choice, repeat=0):
        return {"qid": "q1", "phase": "anchor", "first": first, "second": second,
                "repeat": repeat, "choice": choice, "parse_ok": True,
                "first_len": 10, "second_len": 20, "dropped": False}

    def test_duplicate_rows_collapse(self):
        clean = [self._row("gt0", "d0", "A"), self._row("d0", "gt0", "B")]
        assert len(dedupe_judgments(clean + clean)) == 2

    def test_last_occurrence_wins(self):
        rows = [self._row("gt0", "d0", "A"), self._row("gt0", "d0", "B")]
        assert dedupe_judgments(rows)[0]["choice"] == "B"

    def test_repeats_are_kept_distinct(self):
        rows = [self._row("gt0", "d0", "A", repeat=0),
                self._row("gt0", "d0", "B", repeat=1)]
        assert len(dedupe_judgments(rows)) == 2

    def test_deduped_log_matches_clean_bias_stats(self):
        clean = [self._row("gt0", "d0", "A"), self._row("d0", "gt0", "B")]
        assert bias_stats(dedupe_judgments(clean + clean)) == bias_stats(clean)


class TestBootstrapAuc:
    def test_ci_brackets_true_auc(self):
        records_by_q = {
            f"q{i}": (
                [LooRecord(f"q{i}", "gt1", "ground_truth", "gt0", make_score(0.8))]
                + [LooRecord(f"q{i}", "d0", "distractor", "gt0", make_score(0.2))]
            )
            for i in range(20)
        }
        lo, hi = bootstrap_auc(records_by_q, n_boot=200, seed=1)
        assert lo <= 1.0 <= hi + 1e-9


class TestBiasStats:
    def test_pooled_position_and_length_bias(self):
        log = [
            {"parse_ok": True, "choice": "A", "first_len": 10, "second_len": 20, "dropped": False},
            {"parse_ok": True, "choice": "B", "first_len": 10, "second_len": 20, "dropped": False},
            {"parse_ok": True, "choice": "A", "first_len": 30, "second_len": 20, "dropped": False},
            {"parse_ok": False, "choice": None, "first_len": 5, "second_len": 5, "dropped": True},
        ]
        stats = bias_stats(log)
        assert stats["n_first_total"] == 3
        assert abs(stats["p_first"] - (2 / 3)) < 1e-9
        assert stats["n_longer_total"] == 3
        # rec1: longer=second, chose first -> not counted
        # rec2: longer=second, chose second -> counted
        # rec3: longer=first, chose first -> counted
        assert abs(stats["p_longer"] - (2 / 3)) < 1e-9
        assert stats["abstention_rate"] == 0.25


class TestThresholdGridIsExact:
    """tau = sigmoid(Delta) piles up at 0 and 1 under separation, so a uniform
    [0,1] grid resolves the optimum coarsely and r_q moves with prior_scale
    even when AUC does not. The grid must come from the observed values."""

    def _recs(self, gts, dists):
        return ([LooRecord("q1", f"gt{i}", "ground_truth", "gt0", make_score(t))
                 for i, t in enumerate(gts)]
                + [LooRecord("q1", f"d{i}", "distractor", "gt0", make_score(t))
                   for i, t in enumerate(dists)])

    def test_finds_the_exact_optimum_a_uniform_grid_misses(self):
        """All tau within one 1/200 cell: a uniform grid cannot separate them."""
        recs = self._recs([0.9970, 0.9975], [0.9960, 0.9965])
        r = roc_from_loo(recs)
        assert r["alpha_at_t_star"] == 0.0 and r["beta_at_t_star"] == 0.0
        assert r["r_q"] == 1.0

    def test_perfect_separation_still_scores_one(self):
        r = roc_from_loo(self._recs([0.9, 0.95], [0.1, 0.2]))
        assert r["auc"] == 1.0 and r["r_q"] == 1.0

    def test_threshold_lies_between_the_classes(self):
        r = roc_from_loo(self._recs([0.80, 0.90], [0.10, 0.20]))
        assert 0.20 < r["t_star"] <= 0.80

    def test_no_separation_is_unaffected(self):
        r = roc_from_loo(self._recs([0.5] * 5, [0.5] * 5))
        assert abs(r["auc"] - 0.5) < 1e-9
