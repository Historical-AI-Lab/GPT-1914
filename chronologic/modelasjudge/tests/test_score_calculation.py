"""test_score_calculation.py — Unit and end-to-end tests for score_calculation.py.

All tests are pure Python: no network, no DeBERTa, no LLM calls.

Run with:
    pytest modelasjudge/tests/test_score_calculation.py -v
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from score_calculation import (
    aspect_pass,
    compute_aspect_means,
    compute_overall_binary,
    compute_per_question,
    question_score,
    weight_lin,
    weight_sq,
    weighted_mean,
    _locate_judge_file,
    _locate_discrim_file,
)


# ---------------------------------------------------------------------------
# Fixtures: minimal synthetic judge / discrim dicts
# ---------------------------------------------------------------------------

def _make_judge(qf_entries: dict, ctx_entries: dict) -> dict:
    """Build a minimal judge data dict."""
    return {
        "judge_model": "test_judge",
        "candidate_model": "test_candidate",
        "candidate_reasoning_effort": "none",
        "benchmark_version": "0.2",
        "question_fit": qf_entries,
        "context_fit": ctx_entries,
        "needs_human": [],
    }


def _make_discrim(style_entries: dict, below_threshold: list = None) -> dict:
    return {
        "judge_kind": "discriminative",
        "judge_tag": "test_deberta",
        "candidate_model": "test_candidate",
        "candidate_reasoning_effort": "none",
        "benchmark_version": "0.2",
        "style": style_entries,
        "below_threshold": below_threshold or [],
    }


def _qf_entry(scores, r_q=1.0):
    return {"judge": "test", "r_q": r_q, "judgments": ["GT"] * len(scores),
            "scores": scores, "gt_positions": ["A"] * len(scores),
            "gt_indices": [0] * len(scores)}


def _style_entry(continuous, r_q=1.0):
    return {"judge": "test", "r_q": r_q, "w_q": weight_sq(r_q),
            "gt_indices": [0], "deltas": [0.0], "p_anachronic": [1 - continuous],
            "continuous_scores": [continuous], "continuous": continuous}


# ---------------------------------------------------------------------------
# 1. Weight formula
# ---------------------------------------------------------------------------

class TestWeightFormulas:
    def test_weight_sq_at_half(self):
        assert weight_sq(0.5) == pytest.approx(0.0)

    def test_weight_sq_at_0_65(self):
        assert weight_sq(0.65) == pytest.approx(0.09)

    def test_weight_sq_at_0_75(self):
        assert weight_sq(0.75) == pytest.approx(0.25)

    def test_weight_sq_at_1(self):
        assert weight_sq(1.0) == pytest.approx(1.0)

    def test_weight_sq_none(self):
        assert weight_sq(None) == 0.0

    def test_weight_lin_at_half(self):
        assert weight_lin(0.5) == pytest.approx(0.0)

    def test_weight_lin_at_0_75(self):
        assert weight_lin(0.75) == pytest.approx(0.5)

    def test_weight_lin_at_1(self):
        assert weight_lin(1.0) == pytest.approx(1.0)

    def test_weight_lin_none(self):
        assert weight_lin(None) == 0.0


# ---------------------------------------------------------------------------
# 2. Weight clamped below 0.5
# ---------------------------------------------------------------------------

class TestWeightBelowHalf:
    @pytest.mark.parametrize("r", [0.0, 0.1, 0.49, 0.5])
    def test_sq_clamped(self, r):
        assert weight_sq(r) == pytest.approx(0.0)

    @pytest.mark.parametrize("r", [0.0, 0.1, 0.49, 0.5])
    def test_lin_clamped(self, r):
        assert weight_lin(r) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 3. Per-question score (multi-GT averaging)
# ---------------------------------------------------------------------------

class TestQuestionScore:
    def test_single_pass(self):
        assert question_score([1]) == pytest.approx(1.0)

    def test_single_fail(self):
        assert question_score([0]) == pytest.approx(0.0)

    def test_three_scores(self):
        assert question_score([1, 0, 1]) == pytest.approx(2 / 3)

    def test_two_passes(self):
        assert question_score([1, 1]) == pytest.approx(1.0)

    def test_empty(self):
        assert question_score([]) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 4. aspect_pass threshold
# ---------------------------------------------------------------------------

class TestAspectPass:
    def test_exactly_half(self):
        assert aspect_pass(0.5) is True

    def test_just_below(self):
        assert aspect_pass(0.499) is False

    def test_one(self):
        assert aspect_pass(1.0) is True

    def test_zero(self):
        assert aspect_pass(0.0) is False


# ---------------------------------------------------------------------------
# 5. weighted_mean basic
# ---------------------------------------------------------------------------

class TestWeightedMean:
    def test_basic(self):
        # scores 1, 0 with weights 0.25, 0.75 → 0.25*1 / (0.25+0.75) = 0.25
        result = weighted_mean([(1.0, 0.25), (0.0, 0.75)])
        assert result == pytest.approx(0.25)

    def test_equal_weights(self):
        result = weighted_mean([(1.0, 1.0), (0.0, 1.0)])
        assert result == pytest.approx(0.5)

    def test_single(self):
        assert weighted_mean([(0.7, 0.5)]) == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# 6. weighted_mean all-zero weights returns None
# ---------------------------------------------------------------------------

class TestWeightedMeanZeroWeights:
    def test_all_zero(self):
        result = weighted_mean([(1.0, 0.0), (0.0, 0.0)])
        assert result is None

    def test_empty(self):
        assert weighted_mean([]) is None


# ---------------------------------------------------------------------------
# 7. weighted_mean skips NA scores
# ---------------------------------------------------------------------------

class TestWeightedMeanSkipsNAs:
    def test_one_na(self):
        # NA score is skipped; only (1.0, 1.0) contributes
        result = weighted_mean([(None, 1.0), (1.0, 1.0)])
        assert result == pytest.approx(1.0)

    def test_all_na(self):
        result = weighted_mean([(None, 0.5), (None, 0.8)])
        assert result is None


# ---------------------------------------------------------------------------
# 8. overall_binary: style NA counts as pass
# ---------------------------------------------------------------------------

class TestOverallBinaryStyleNA:
    def test_style_na_passes(self):
        judge = _make_judge(
            {"q1": _qf_entry([1], r_q=1.0)},
            {"q1": _qf_entry([1], r_q=1.0)},
        )
        discrim = _make_discrim({}, below_threshold=["q1"])
        per_q = compute_per_question(judge, discrim)
        assert per_q["q1"]["style"]["na"] is True
        assert per_q["q1"]["overall_pass"] is True

    def test_style_na_when_missing_from_discrim(self):
        judge = _make_judge(
            {"q1": _qf_entry([1], r_q=1.0)},
            {"q1": _qf_entry([1], r_q=1.0)},
        )
        discrim = _make_discrim({})
        per_q = compute_per_question(judge, discrim)
        assert per_q["q1"]["style"]["na"] is True
        assert per_q["q1"]["overall_pass"] is True


# ---------------------------------------------------------------------------
# 9. overall_binary: style fail blocks
# ---------------------------------------------------------------------------

class TestOverallBinaryStyleFail:
    def test_style_fail_blocks(self):
        judge = _make_judge(
            {"q1": _qf_entry([1], r_q=1.0)},
            {"q1": _qf_entry([1], r_q=1.0)},
        )
        discrim = _make_discrim({"q1": _style_entry(0.4, r_q=0.9)})
        per_q = compute_per_question(judge, discrim)
        assert per_q["q1"]["style"]["pass"] is False
        assert per_q["q1"]["overall_pass"] is False


# ---------------------------------------------------------------------------
# 10. overall_binary: question_fit fail blocks
# ---------------------------------------------------------------------------

class TestOverallBinaryQFBlocks:
    def test_qf_fail_blocks(self):
        judge = _make_judge(
            {"q1": _qf_entry([0], r_q=1.0)},
            {"q1": _qf_entry([1], r_q=1.0)},
        )
        discrim = _make_discrim({"q1": _style_entry(1.0, r_q=1.0)})
        per_q = compute_per_question(judge, discrim)
        assert per_q["q1"]["question_fit"]["pass"] is False
        assert per_q["q1"]["overall_pass"] is False


# ---------------------------------------------------------------------------
# 11. human judge collapsed list processed normally
# ---------------------------------------------------------------------------

class TestHumanJudgeEntry:
    def test_human_judge_processed(self):
        human_r = 0.93
        judge = _make_judge(
            {"q1": {"judge": "human", "r_q": human_r, "judgments": ["tie"],
                    "scores": [1], "gt_positions": [None], "gt_indices": [None]}},
            {"q1": {"judge": "human", "r_q": human_r, "judgments": ["GT"],
                    "scores": [0], "gt_positions": [None], "gt_indices": [None]}},
        )
        discrim = _make_discrim({"q1": _style_entry(0.8, r_q=0.9)})
        per_q = compute_per_question(judge, discrim)

        assert per_q["q1"]["question_fit"]["score"] == pytest.approx(1.0)
        assert per_q["q1"]["question_fit"]["r_q"] == pytest.approx(human_r)
        assert per_q["q1"]["context_fit"]["score"] == pytest.approx(0.0)

        means = compute_aspect_means(per_q)
        # question_fit: score=1, r_q=0.93 → weight_sq=(2*0.93-1)^2 = 0.86^2 = 0.7396
        assert means["question_fit"]["squared"] == pytest.approx(1.0)
        # context_fit: score=0, weight > 0 → mean = 0
        assert means["context_fit"]["squared"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 12. below_threshold marks style NA
# ---------------------------------------------------------------------------

class TestBelowThresholdStyleNA:
    def test_na_when_in_below_threshold(self):
        discrim = _make_discrim(
            {"q1": _style_entry(0.9, r_q=0.9)},
            below_threshold=["q1"],
        )
        judge = _make_judge({"q1": _qf_entry([1])}, {"q1": _qf_entry([1])})
        per_q = compute_per_question(judge, discrim)
        assert per_q["q1"]["style"]["na"] is True
        # score should be None even though the entry exists in style_section
        assert per_q["q1"]["style"]["score"] is None


# ---------------------------------------------------------------------------
# 13. E2E: all pass
# ---------------------------------------------------------------------------

class TestE2EAllPass:
    def _build(self):
        judge = _make_judge(
            {str(i): _qf_entry([1], r_q=1.0) for i in range(3)},
            {str(i): _qf_entry([1], r_q=1.0) for i in range(3)},
        )
        discrim = _make_discrim(
            {str(i): _style_entry(1.0, r_q=1.0) for i in range(3)}
        )
        return judge, discrim

    def test_means_all_one(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        for asp in ("question_fit", "context_fit", "style"):
            assert means[asp]["squared"] == pytest.approx(1.0), asp
            assert means[asp]["linear"] == pytest.approx(1.0), asp

    def test_overall_one(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        assert compute_overall_binary(per_q) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 14. E2E: all fail
# ---------------------------------------------------------------------------

class TestE2EAllFail:
    def _build(self):
        judge = _make_judge(
            {str(i): _qf_entry([0], r_q=1.0) for i in range(3)},
            {str(i): _qf_entry([0], r_q=1.0) for i in range(3)},
        )
        discrim = _make_discrim(
            {str(i): _style_entry(0.0, r_q=1.0) for i in range(3)}
        )
        return judge, discrim

    def test_means_all_zero(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        for asp in ("question_fit", "context_fit", "style"):
            assert means[asp]["squared"] == pytest.approx(0.0), asp

    def test_overall_zero(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        assert compute_overall_binary(per_q) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 15. E2E: mixed known means
# ---------------------------------------------------------------------------

class TestE2EMixedKnownMeans:
    """Three questions: two with r_q=1.0, one with r_q=0.75.

    question_fit scores: [1, 0, 1]
    context_fit scores:  [1, 1, 0]
    style scores:        [1, 1, 0.6]

    Squared weights: [1.0, 1.0, 0.25]

    question_fit mean (sq) = (1*1 + 0*1 + 1*0.25) / (1+1+0.25) = 1.25/2.25
    context_fit mean (sq)  = (1*1 + 1*1 + 0*0.25) / 2.25       = 2.0/2.25
    style mean (sq)        = (1*1 + 1*1 + 0.6*0.25) / 2.25     = 2.15/2.25

    Linear weights: [1.0, 1.0, 0.5]

    question_fit mean (lin) = (1 + 0 + 0.5) / 2.5 = 1.5/2.5 = 0.6
    """

    def _build(self):
        qf = {
            "q0": _qf_entry([1], r_q=1.0),
            "q1": _qf_entry([0], r_q=1.0),
            "q2": _qf_entry([1], r_q=0.75),
        }
        ctx = {
            "q0": _qf_entry([1], r_q=1.0),
            "q1": _qf_entry([1], r_q=1.0),
            "q2": _qf_entry([0], r_q=0.75),
        }
        st = {
            "q0": _style_entry(1.0, r_q=1.0),
            "q1": _style_entry(1.0, r_q=1.0),
            "q2": _style_entry(0.6, r_q=0.75),
        }
        return _make_judge(qf, ctx), _make_discrim(st)

    def test_qf_squared(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        assert means["question_fit"]["squared"] == pytest.approx(1.25 / 2.25, rel=1e-5)

    def test_qf_linear(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        assert means["question_fit"]["linear"] == pytest.approx(1.5 / 2.5, rel=1e-5)

    def test_ctx_squared(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        assert means["context_fit"]["squared"] == pytest.approx(2.0 / 2.25, rel=1e-5)

    def test_style_squared(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        assert means["style"]["squared"] == pytest.approx(2.15 / 2.25, rel=1e-5)

    def test_overall(self):
        judge, discrim = self._build()
        per_q = compute_per_question(judge, discrim)
        # q0: qf=1≥0.5✓, cf=1✓, st=1✓ → pass
        # q1: qf=0<0.5✗ → fail
        # q2: qf=1✓, cf=0✗ → fail
        assert compute_overall_binary(per_q) == pytest.approx(1 / 3, rel=1e-5)


# ---------------------------------------------------------------------------
# 16. E2E: writes expected schema
# ---------------------------------------------------------------------------

class TestE2EWritesSchema:
    def test_output_schema(self, tmp_path):
        from score_calculation import compute_per_question, compute_aspect_means, compute_overall_binary
        import score_calculation as sc

        judge = _make_judge(
            {"q1": _qf_entry([1], r_q=0.9)},
            {"q1": _qf_entry([1], r_q=0.9)},
        )
        discrim = _make_discrim({"q1": _style_entry(0.8, r_q=0.9)})

        per_q = compute_per_question(judge, discrim)
        means = compute_aspect_means(per_q)
        overall = compute_overall_binary(per_q)

        output_data = {
            "candidate_model": "test_candidate",
            "candidate_reasoning_effort": "none",
            "benchmark_version": "0.2",
            "sources": {
                "judge_file": "judge_test__test__0.2.json",
                "discrim_file": "discrim_test__test__0.2.json",
                "judge_used_human": False,
            },
            "weighted_means": means,
            "overall_binary_accuracy": overall,
            "per_question": per_q,
        }
        out = tmp_path / "final_test__0.2.json"
        sc._write_output(out, output_data)

        with open(out) as fh:
            loaded = json.load(fh)

        assert "candidate_model" in loaded
        assert "weighted_means" in loaded
        assert "overall_binary_accuracy" in loaded
        assert "per_question" in loaded
        assert "sources" in loaded
        wm = loaded["weighted_means"]
        for asp in ("question_fit", "context_fit", "style"):
            assert asp in wm, asp
            assert "squared" in wm[asp], asp
            assert "linear" in wm[asp], asp
        pq = loaded["per_question"]["q1"]
        for asp in ("question_fit", "context_fit", "style"):
            assert asp in pq, asp
            assert "score" in pq[asp]
            assert "r_q" in pq[asp]
            assert "pass" in pq[asp]
        assert "overall_pass" in pq


# ---------------------------------------------------------------------------
# 17. E2E: prefers human variant in auto-locate
# ---------------------------------------------------------------------------

class TestE2EPrefersHumanVariant:
    def test_prefers_human(self, tmp_path, monkeypatch):
        import score_calculation as sc
        monkeypatch.setattr(sc, "SCORED_DIR", tmp_path)

        # Create both files
        base = tmp_path / "judge_testjudge__mymodel__0.2.json"
        human = tmp_path / "judge_testjudge__mymodel__0.2_human.json"
        base.write_text("{}")
        human.write_text("{}")

        path, used_human = _locate_judge_file("mymodel", "0.2")
        assert path == human
        assert used_human is True

    def test_falls_back_to_base(self, tmp_path, monkeypatch):
        import score_calculation as sc
        monkeypatch.setattr(sc, "SCORED_DIR", tmp_path)

        base = tmp_path / "judge_testjudge__mymodel__0.2.json"
        base.write_text("{}")

        path, used_human = _locate_judge_file("mymodel", "0.2")
        assert path == base
        assert used_human is False

    def test_used_human_flag_in_sources(self, tmp_path, monkeypatch):
        import score_calculation as sc
        monkeypatch.setattr(sc, "SCORED_DIR", tmp_path)

        human = tmp_path / "judge_testjudge__mymodel__0.2_human.json"
        judge = _make_judge(
            {"q1": _qf_entry([1], r_q=0.9)},
            {"q1": _qf_entry([1], r_q=0.9)},
        )
        human.write_text(json.dumps(judge))

        discrim_f = tmp_path / "discrim_deb__mymodel__0.2.json"
        discrim = _make_discrim({"q1": _style_entry(0.8, r_q=0.9)})
        discrim_f.write_text(json.dumps(discrim))

        path, used_human = _locate_judge_file("mymodel", "0.2")
        assert used_human is True
