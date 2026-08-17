"""test_score_substantive.py — end-to-end test of score_substantive.py's
score/checks/identity subcommands against tmp_path fixtures. No LLM calls,
no PyMC: every draw bank is a synthetic on-disk npz built by hand.

Run with:
    pytest modelasjudge/tests/test_score_substantive.py -v
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

import score_substantive as cli
from substantive import artifacts as substantive_artifacts

FRAME_TYPES = ["world_context"]


def _base_meta(**extra):
    meta = {"schema_version": 1, "produced_by": "test", "produced_at": "now", "git_head": "abc",
           "benchmark_version": "0.7", "routing_basis": "partial_credit", "judge_effort": "none",
           "prompt_mode": "rationales", "prior_dist": "normal", "prior_df": 3.0,
           "prior_scale": 3.0, "frame_types": FRAME_TYPES}
    meta.update(extra)
    return meta


def _write_benchmark(path, pf_qnums, pc_qnums):
    with open(path, "w") as f:
        for q in pf_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 0, "frame_type": "world_context",
                "source_genre": "fiction", "question_category": "plot",
                "answer_strings": ["a ground truth answer of modest length"],
            }) + "\n")
        for q in pc_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 1, "frame_type": "book_context",
                "source_genre": "fiction", "question_category": "plot",
                "answer_strings": ["a ground truth answer of modest length"],
            }) + "\n")


def _write_scored(path, pf_qnums, *, candidate_label="cand", seed=0):
    rng = np.random.default_rng(seed)
    question_fit = {q: {"scores": [int(x) for x in rng.integers(0, 2, 9)]} for q in pf_qnums}
    Path(path).write_text(json.dumps({
        "judge_model": "testjudge", "reasoning_effort": "none",
        "candidate_label": candidate_label, "candidate_model": f"{candidate_label}-model",
        "candidate_reasoning_effort": "none", "question_fit": question_fit,
    }))


def _write_bt_scored(scored_path, *, tag="testtag"):
    out_path = scored_path.parent / f"{scored_path.stem}_btcontext.json"
    out_path.write_text(json.dumps({"bt_context": {"artifacts_tag": tag}}))
    return out_path


def _write_reliability(path, pf_qnums):
    # 4 of 5 questions have a perfect judge (question_correct == question_total,
    # zero errors); the 5th has 2 errors -- mirrors the real corpus's "82.3%
    # perfect" pattern (see substantive-uncertainty-spec.md Sec8.5). This is
    # the exact realistic shape that the k_alpha inversion bug produced NaN
    # scores on: question_correct=8 must NOT be read as the Beta posterior's
    # k, or alpha comes out near 1 instead of near 0 and floor-excludes
    # everything.
    per_question = {}
    for i, q in enumerate(pf_qnums):
        if i == len(pf_qnums) - 1:
            per_question[q] = {"question_correct": 6, "question_total": 8}
        else:
            per_question[q] = {"question_correct": 8, "question_total": 8}
    Path(path).write_text(json.dumps({"per_question": per_question}))


def _write_beta_bank(path, *, D=300):
    rng = np.random.default_rng(10)
    arrays = {"b0": rng.normal(-2.0, 0.05, D), "b_len": np.zeros(D), "u_frame": np.zeros((D, 1))}
    meta = _base_meta(standardization={"mu_loglen": 3.0, "sd_loglen": 1.0}, sigma_u=0.3,
                      sigma_u_diagnostics={"overdispersion_ratio": 1.4})
    substantive_artifacts.save_npz(path, arrays, meta)


def _write_calib_bank(path, *, C=300):
    rng = np.random.default_rng(11)
    arrays = {"cal_a": rng.normal(0, 0.05, C), "cal_b": rng.normal(1, 0.05, C)}
    substantive_artifacts.save_npz(path, arrays, _base_meta())


def _write_delta_bank(path, pc_qnums, *, n_draws=300):
    rng = np.random.default_rng(12)
    arrays = {f"delta__{q}": rng.normal(0.5, 1.0, n_draws) for q in pc_qnums}
    substantive_artifacts.save_npz(path, arrays, _base_meta())


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(substantive_artifacts, "BETA_RELIABILITY_DIR", tmp_path / "beta_reliability")
    monkeypatch.setattr(substantive_artifacts, "BT_ARTIFACTS_DIR", tmp_path / "bt_artifacts")
    monkeypatch.setattr(substantive_artifacts, "SUBSTANTIVE_ARTIFACTS_DIR", tmp_path / "substantive_artifacts")
    monkeypatch.setattr(substantive_artifacts, "RESULTS_DIR", tmp_path / "results")

    pf_qnums = ["1", "2", "3", "4", "5"]
    pc_qnums = ["10", "11"]
    benchmark = tmp_path / "bench.jsonl"
    _write_benchmark(benchmark, pf_qnums, pc_qnums)

    scored = tmp_path / "judge_testjudge__cand__0.7__c-none__j-none.json"
    _write_scored(scored, pf_qnums)
    bt_scored = _write_bt_scored(scored)

    reliability = tmp_path / "reliability.json"
    _write_reliability(reliability, pf_qnums)

    beta_path = tmp_path / "beta_draws.npz"
    _write_beta_bank(beta_path)
    calib_path = tmp_path / "calib_draws.npz"
    _write_calib_bank(calib_path)
    delta_path = tmp_path / "delta_draws.npz"
    _write_delta_bank(delta_path, pc_qnums)

    return dict(tmp_path=tmp_path, benchmark=benchmark, scored=scored, bt_scored=bt_scored,
               reliability=reliability, beta_path=beta_path, calib_path=calib_path,
               delta_path=delta_path, pf_qnums=pf_qnums, pc_qnums=pc_qnums)


def make_args(ws, command="score", **overrides):
    class Args:
        pass
    a = Args()
    a.scored_file = str(ws["scored"])
    a.bt_scored_file = None
    a.delta_draws = str(ws["delta_path"])
    a.benchmark = str(ws["benchmark"])
    a.reliability = str(ws["reliability"])
    a.beta_draws = str(ws["beta_path"])
    a.calib_draws = str(ws["calib_path"])
    a.alpha_prior = "jeffreys"
    a.floor = 0.2
    a.n_boot = 300
    a.seed = 0
    a.slices = "source_genre,frame_type,question_category"
    if command == "score":
        a.freeze_bank = None
        a.frozen_bank = None
        a.report = None
        a.output = None
        a.no_ledger = True
    elif command == "checks":
        a.report = None
    for k, v in overrides.items():
        setattr(a, k, v)
    return a


class TestScoreEndToEnd:
    def test_produces_finite_scores_with_realistic_reliability(self, workspace, tmp_path):
        report = tmp_path / "report.md"
        output = tmp_path / "scores.json"
        args = make_args(workspace, report=str(report), output=str(output))
        cli.cmd_score(args)

        assert report.exists()
        scores = json.loads(output.read_text())
        for key in ("passfail", "partial", "pooled_count", "pooled_equal"):
            assert np.isfinite(scores[key]), f"{key} is not finite: {scores[key]!r}"
            assert 0.0 <= scores[key] <= 1.0
        assert scores["n_excluded_floor"] == 0
        assert len(scores["passfail_draws"]) == args.n_boot

    def test_mean_alpha_uses_the_prior_posterior_not_raw_mle(self, workspace, tmp_path):
        """Regression pin for the k_alpha inversion bug: with 4/5 questions
        perfect (0 errors) and 1/5 with 2 errors out of 8, the Jeffreys
        posterior mean must land near (0.5+0)/(1+8) and (0.5+2)/(1+8)
        averaged -- not near 1 (which is what raw question_correct/n gives
        when misread as the error count)."""
        report = tmp_path / "report.md"
        args = make_args(workspace, report=str(report), output=str(tmp_path / "scores.json"))
        cli.cmd_score(args)
        text = report.read_text()
        expected = (4 * (0.5 / 9) + 1 * (2.5 / 9)) / 5
        line = [l for l in text.splitlines() if "mean alpha" in l][0]
        reported = float(line.rsplit(":", 1)[1].strip().rstrip("%\n"))
        assert abs(reported - expected) < 1e-3
        assert reported < 0.2   # sanity: nowhere near the ~0.8 the inverted bug produced

    def test_ledger_and_history_written_when_not_suppressed(self, workspace, tmp_path):
        args = make_args(workspace, no_ledger=False,
                         report=str(tmp_path / "report.md"), output=str(tmp_path / "scores.json"))
        cli.cmd_score(args)

        ledger_path = substantive_artifacts.ledger_path()
        assert ledger_path.exists()
        rows = list(csv.DictReader(ledger_path.open()))
        assert len(rows) == 1
        assert rows[0]["candidate_label"] == "cand"

        history_path = substantive_artifacts.history_path()
        assert history_path.exists()
        history_rows = [json.loads(l) for l in history_path.read_text().splitlines() if l.strip()]
        assert len(history_rows) == 1

    def test_no_ledger_suppresses_ledger_write(self, workspace, tmp_path):
        args = make_args(workspace, no_ledger=True,
                         report=str(tmp_path / "report.md"), output=str(tmp_path / "scores.json"))
        cli.cmd_score(args)
        assert not substantive_artifacts.ledger_path().exists()

    def test_missing_bt_scored_file_raises_with_actionable_message(self, workspace, tmp_path):
        scored2 = tmp_path / "judge_testjudge__other__0.7__c-none__j-none.json"
        _write_scored(scored2, workspace["pf_qnums"], candidate_label="other")
        # No corresponding _btcontext.json written for scored2.
        args = make_args(workspace, scored_file=str(scored2),
                         calib_draws=None, delta_draws=None,
                         report=str(tmp_path / "report.md"), output=str(tmp_path / "scores.json"))
        with pytest.raises(FileNotFoundError, match="bt_context_scoring"):
            cli.cmd_score(args)


class TestFreezeAndFrozenBank:
    def test_frozen_bank_reproduces_the_same_score(self, workspace, tmp_path):
        frozen_path = tmp_path / "frozen.npz"
        args1 = make_args(workspace, freeze_bank=str(frozen_path),
                          report=str(tmp_path / "report1.md"), output=str(tmp_path / "scores1.json"))
        cli.cmd_score(args1)
        assert frozen_path.exists()

        args2 = make_args(workspace, frozen_bank=str(frozen_path),
                          report=str(tmp_path / "report2.md"), output=str(tmp_path / "scores2.json"))
        cli.cmd_score(args2)

        s1 = json.loads((tmp_path / "scores1.json").read_text())
        s2 = json.loads((tmp_path / "scores2.json").read_text())
        # Same bank + same seed => bit-for-bit identical bootstrap replicates.
        assert s1["passfail_draws"] == s2["passfail_draws"]
        assert s1["pooled_equal_draws"] == s2["pooled_equal_draws"]


class TestChecksEndToEnd:
    def test_all_five_checks_run_without_error(self, workspace, capsys):
        args = make_args(workspace, command="checks", report=None)
        cli.cmd_checks(args)
        out = capsys.readouterr().out
        for header in ("layer ablation", "Jeffreys vs uniform", "alpha x1.5 sensitivity",
                      "2- vs 3-parameter calibration", "per-slice calibration"):
            assert header in out

    def test_checks_report_written_when_requested(self, workspace, tmp_path):
        report = tmp_path / "checks.md"
        args = make_args(workspace, command="checks", report=str(report))
        cli.cmd_checks(args)
        assert report.exists()
        assert "layer ablation" in report.read_text()


class TestIdentity:
    def test_residual_within_tolerance(self, capsys):
        cli.cmd_identity(None)
        out = capsys.readouterr().out
        assert "OK" in out
        assert "residual" in out


class TestLengthCovariateFlagRemoved:
    def test_score_parser_has_no_length_covariate_flag(self):
        parser = cli.build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["score", "--scored-file", "x", "--length-covariate"])
