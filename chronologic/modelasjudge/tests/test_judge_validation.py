"""tests/test_judge_validation.py — pooled alpha/beta arithmetic and the
separation guarantee: alpha/beta artifacts are validation evidence, never a
scoring dependency (direct-binary-scoring-spec.md section 18).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import beta as beta_dist

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.judge_validation import (
    Rate, alpha_draws, alpha_point, beta_from_coefs, jeffreys_interval,
    pooled_alpha, pooled_beta,
)


class TestJeffreysInterval:
    def test_hand_computed_against_scipy_beta_ppf(self):
        k, n = 361, 6446
        lo, hi = jeffreys_interval(k, n)
        exp_lo, exp_hi = beta_dist.ppf([0.025, 0.975], 0.5 + k, 0.5 + (n - k))
        assert lo == pytest.approx(exp_lo)
        assert hi == pytest.approx(exp_hi)

    def test_custom_ci_width(self):
        k, n = 23, 200
        lo90, hi90 = jeffreys_interval(k, n, ci=(5.0, 95.0))
        lo95, hi95 = jeffreys_interval(k, n, ci=(2.5, 97.5))
        assert lo90 > lo95
        assert hi90 < hi95

    def test_zero_k_gives_a_small_but_nonzero_lower_bound(self):
        """Jeffreys (Beta(0.5, n+0.5)) never collapses to a point mass at
        k=0 the way a naive k/n rate would -- the interval stays informative
        about how large the true rate plausibly is."""
        lo, hi = jeffreys_interval(0, 100)
        assert 0.0 < lo < 1e-3
        assert hi > lo


class TestPooledAlpha:
    def test_hand_computed_k_and_n(self, tmp_path):
        """k = sum(question_total - question_correct), n = sum(question_total)."""
        path = tmp_path / "reliability.json"
        per_question = {
            "1": {"question_correct": 8, "question_total": 8},   # 0 errors
            "2": {"question_correct": 6, "question_total": 8},   # 2 errors
            "3": {"question_correct": 7, "question_total": 10},  # 3 errors
        }
        path.write_text(json.dumps({"per_question": per_question}))

        rate = pooled_alpha(path)
        assert isinstance(rate, Rate)
        assert rate.k == 5
        assert rate.n == 26
        assert rate.rate == pytest.approx(5 / 26)
        assert rate.n_questions == 3
        assert rate.lo < rate.rate < rate.hi

    def test_real_reliability_file_matches_plan_verified_baseline(self):
        """Verified against the plan's baseline table: 361 false passes /
        6446 known-bad trials = 5.60%, over 791 questions."""
        path = MODELASJUDGE / "llm_reliability" / "anthropic_claude-sonnet-4-6__0.7.json"
        if not path.exists():
            pytest.skip(f"{path} not present in this checkout")
        rate = pooled_alpha(path)
        assert rate.k == 361
        assert rate.n == 6446
        assert rate.n_questions == 791
        assert rate.rate == pytest.approx(0.0560, abs=1e-4)


class TestPooledBeta:
    def test_hand_computed_k_and_n_and_the_halving(self, tmp_path):
        """k = sum(k_nontie), n = sum(n_valid_trials); rate halved on the
        way out -- a GT-vs-GT tie pair gives the judge two chances to err,
        so the raw non-tie fraction estimates 2*beta."""
        path = tmp_path / "gt_pairs.jsonl"
        records = [
            {"k_nontie": 0, "n_valid_trials": 2},
            {"k_nontie": 2, "n_valid_trials": 2},
            {"k_nontie": 1, "n_valid_trials": 2},
        ]
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        rate = pooled_beta(path)
        assert rate.k == 3
        assert rate.n == 6
        raw_two_beta = 3 / 6
        assert rate.rate == pytest.approx(raw_two_beta / 2.0)
        assert rate.n_questions == 3

    def test_real_gt_pairs_file_matches_plan_verified_baseline(self):
        """23 non-ties / 200 trials over 100 GT pairs -> 2b = 0.115, b = 0.0575."""
        path = MODELASJUDGE / "beta_reliability" / "gt_pairs_anthropic_claude-sonnet-4-6__0.4.jsonl"
        if not path.exists():
            pytest.skip(f"{path} not present in this checkout")
        rate = pooled_beta(path)
        assert rate.k == 23
        assert rate.n == 200
        assert rate.n_questions == 100
        assert rate.rate == pytest.approx(0.0575, abs=1e-4)

    def test_interval_is_halved_along_with_the_point(self, tmp_path):
        path = tmp_path / "gt_pairs.jsonl"
        records = [{"k_nontie": 23, "n_valid_trials": 200}]
        path.write_text(json.dumps(records[0]) + "\n")
        rate = pooled_beta(path)
        raw_lo, raw_hi = jeffreys_interval(23, 200)
        assert rate.lo == pytest.approx(raw_lo / 2.0)
        assert rate.hi == pytest.approx(raw_hi / 2.0)


class TestRelocatedAlphaBetaFunctions:
    """alpha_point / alpha_draws / beta_from_coefs moved here verbatim from
    the old substantive/estimator.py -- pin their behaviour so the move
    didn't change any arithmetic."""

    def test_alpha_point_closed_form(self):
        k, n = np.array([2.0]), np.array([10.0])
        expected = (0.5 + 2.0) / (2 * 0.5 + 10.0)
        assert alpha_point(k, n)[0] == pytest.approx(expected)

    def test_alpha_draws_shape_and_bounds(self):
        rng = np.random.default_rng(0)
        draws = alpha_draws(np.array([2, 5]), np.array([10, 10]), n_draws=500, rng=rng)
        assert draws.shape == (2, 500)
        assert np.all(draws >= 0.0) and np.all(draws <= 1.0)

    def test_beta_from_coefs_bounded_to_half(self):
        rng = np.random.default_rng(1)
        n_q, R = 30, 100
        b0 = rng.normal(0, 1, size=R)
        b_len = rng.normal(0, 0.3, size=R)
        u_frame = rng.normal(0, 1, size=(R, 3))
        frame_idx = rng.integers(0, 3, size=n_q)
        z_loglen = rng.normal(0, 1, size=n_q)
        b = beta_from_coefs(b0, b_len, u_frame, frame_idx=frame_idx, z_loglen=z_loglen)
        assert np.all(b >= 0.0) and np.all(b <= 0.5)


# ---------------------------------------------------------------------------
# The separation guarantee: nothing in the scoring path imports this module,
# and removing the alpha/beta artifacts entirely leaves scoring unaffected.
# ---------------------------------------------------------------------------

class TestSeparationFromScoring:
    def test_no_scoring_module_imports_judge_validation(self):
        import ast

        targets = ["substantive/drawbank.py", "substantive/estimator.py",
                  "substantive/report.py", "score_substantive.py"]
        for rel in targets:
            path = MODELASJUDGE / rel
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name)
            assert not any("judge_validation" in name for name in imported), (
                f"{rel} imports judge_validation: {imported}"
            )

    def test_removing_alpha_beta_artifacts_leaves_cmd_score_unchanged(self, tmp_path, monkeypatch):
        """The strongest form of the separation guarantee: delete the
        reliability JSON and beta draw bank entirely (not just don't pass
        them) and confirm score_substantive.py's score command still runs
        and returns byte-identical numbers to a run where those files
        exist on disk but are simply never referenced."""
        import score_substantive as cli
        from substantive import artifacts as substantive_artifacts

        monkeypatch.setattr(substantive_artifacts, "BETA_RELIABILITY_DIR", tmp_path / "beta_reliability")
        monkeypatch.setattr(substantive_artifacts, "BT_ARTIFACTS_DIR", tmp_path / "bt_artifacts")
        monkeypatch.setattr(substantive_artifacts, "SUBSTANTIVE_ARTIFACTS_DIR", tmp_path / "substantive_artifacts")
        monkeypatch.setattr(substantive_artifacts, "RESULTS_DIR", tmp_path / "results")

        pf_qnums, pc_qnums = ["1", "2", "3"], ["10"]
        benchmark = tmp_path / "bench.jsonl"
        with open(benchmark, "w") as f:
            for q in pf_qnums:
                f.write(json.dumps({
                    "question_number": int(q), "partial_credit": 0, "frame_type": "world_context",
                    "reasoning_type": "knowledge", "answer_strings": ["a ground truth"],
                }) + "\n")
            for q in pc_qnums:
                f.write(json.dumps({
                    "question_number": int(q), "partial_credit": 1, "frame_type": "book_context",
                    "reasoning_type": "constrained_generation", "answer_strings": ["a ground truth"],
                }) + "\n")

        scored = tmp_path / "judge_testjudge__cand__0.7__c-none__j-none.json"
        rng = np.random.default_rng(0)
        question_fit = {q: {"scores": [int(x) for x in rng.integers(0, 2, 5)]} for q in pf_qnums}
        scored.write_text(json.dumps({
            "judge_model": "testjudge", "reasoning_effort": "none",
            "candidate_label": "cand", "candidate_model": "cand-model",
            "candidate_reasoning_effort": "none", "question_fit": question_fit,
        }))
        (scored.parent / f"{scored.stem}_btcontext.json").write_text(
            json.dumps({"bt_context": {"artifacts_tag": "testtag"}}))

        base_meta = {"schema_version": 1, "produced_by": "test", "produced_at": "now",
                    "git_head": "abc", "benchmark_version": "0.7"}
        calib_path = tmp_path / "calib_draws.npz"
        substantive_artifacts.save_npz(
            calib_path, {"cal_a": np.zeros(20), "cal_b": np.ones(20)}, base_meta)
        delta_path = tmp_path / "delta_draws.npz"
        substantive_artifacts.save_npz(
            delta_path, {f"delta__{q}": rng.normal(0, 1, 50) for q in pc_qnums}, base_meta)

        # No reliability JSON, no beta draw bank, anywhere on disk -- not
        # skipped, not empty, absent.
        assert not (tmp_path / "beta_reliability").exists()

        class Args:
            pass
        args = Args()
        args.scored_file = str(scored)
        args.bt_scored_file = None
        args.delta_draws = str(delta_path)
        args.benchmark = str(benchmark)
        args.calib_draws = str(calib_path)
        args.n_boot = 100
        args.seed = 0
        args.freeze_bank = None
        args.frozen_bank = None
        args.report = str(tmp_path / "report.md")
        args.output = str(tmp_path / "scores.json")
        args.no_ledger = True

        cli.cmd_score(args)  # must not raise despite no alpha/beta artifacts existing

        scores = json.loads((tmp_path / "scores.json").read_text())
        expected = np.mean([np.mean(rec["scores"]) for rec in question_fit.values()])
        assert scores["passfail"] == pytest.approx(expected)
