"""test_score_substantive.py — end-to-end test of score_substantive.py's
score/checks/identity subcommands against tmp_path fixtures. No LLM calls,
no PyMC: every draw bank is a synthetic on-disk npz built by hand. No
reliability JSON or beta draw bank either -- the binary channel reads
straight off the scored-answers file (direct-binary-scoring-spec.md).

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
           "prior_scale": 3.0}
    meta.update(extra)
    return meta


def _write_benchmark(path, pf_qnums, pc_qnums):
    with open(path, "w") as f:
        for q in pf_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 0, "frame_type": "world_context",
                "source_genre": "fiction", "question_category": "plot",
                "reasoning_type": "knowledge",
                "answer_strings": ["a ground truth answer of modest length"],
            }) + "\n")
        for q in pc_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 1, "frame_type": "book_context",
                "source_genre": "fiction", "question_category": "plot",
                "reasoning_type": "constrained_generation",
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

    calib_path = tmp_path / "calib_draws.npz"
    _write_calib_bank(calib_path)
    delta_path = tmp_path / "delta_draws.npz"
    _write_delta_bank(delta_path, pc_qnums)

    return dict(tmp_path=tmp_path, benchmark=benchmark, scored=scored, bt_scored=bt_scored,
               calib_path=calib_path, delta_path=delta_path,
               pf_qnums=pf_qnums, pc_qnums=pc_qnums)


def make_args(ws, command="score", **overrides):
    class Args:
        pass
    a = Args()
    a.scored_file = str(ws["scored"])
    a.bt_scored_file = None
    a.delta_draws = str(ws["delta_path"])
    a.benchmark = str(ws["benchmark"])
    a.calib_draws = str(ws["calib_path"])
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
    def test_produces_finite_scores_matching_the_raw_verdicts(self, workspace, tmp_path):
        report = tmp_path / "report.md"
        output = tmp_path / "scores.json"
        args = make_args(workspace, report=str(report), output=str(output))
        cli.cmd_score(args)

        assert report.exists()
        scores = json.loads(output.read_text())
        for key in ("passfail", "partial", "pooled_count", "pooled_equal"):
            assert np.isfinite(scores[key]), f"{key} is not finite: {scores[key]!r}"
            assert 0.0 <= scores[key] <= 1.0
        assert len(scores["passfail_draws"]) == args.n_boot
        assert scores["scoring_version"] == "direct_binary_v1"
        assert (scores["n_binary_pass"] + scores["n_binary_fail"] + scores["n_binary_split"]
               == scores["n_passfail"])

        question_fit = json.loads(workspace["scored"].read_text())["question_fit"]
        raw_mean = np.mean([np.mean(rec["scores"]) for rec in question_fit.values()])
        assert scores["passfail"] == pytest.approx(raw_mean)

    def test_no_rogan_gladen_columns_in_the_scores_file(self, workspace, tmp_path):
        args = make_args(workspace, report=str(tmp_path / "report.md"),
                         output=str(tmp_path / "scores.json"))
        cli.cmd_score(args)
        scores = json.loads((tmp_path / "scores.json").read_text())
        for retired in ("alpha_prior", "n_excluded_floor", "clip_rate",
                       "near_floor_frac", "sigma_u", "mean_alpha"):
            assert retired not in scores

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

    def test_no_reliability_or_beta_draws_flags_on_the_score_parser(self):
        parser = cli.build_parser()
        for flag in ("--reliability", "--beta-draws", "--alpha-prior", "--floor"):
            with pytest.raises(SystemExit):
                parser.parse_args(["score", "--scored-file", "x", flag, "y"])


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
    def test_all_checks_run_without_error(self, workspace, capsys):
        args = make_args(workspace, command="checks", report=None)
        cli.cmd_checks(args)
        out = capsys.readouterr().out
        for header in ("binary identity", "layer ablation",
                      "2- vs 3-parameter calibration", "per-slice calibration",
                      "reasoning-type breakdown"):
            assert header in out
        for retired in ("Jeffreys vs uniform", "alpha x1.5 sensitivity"):
            assert retired not in out

    def test_binary_identity_check_reads_zero_on_real_data(self, workspace, capsys):
        args = make_args(workspace, command="checks", report=None)
        cli.cmd_checks(args)
        out = capsys.readouterr().out
        line = [l for l in out.splitlines() if "passfail - mean(v_q)" in l][0]
        assert "0.00e+00" in line

    def test_checks_report_written_when_requested(self, workspace, tmp_path):
        report = tmp_path / "checks.md"
        args = make_args(workspace, command="checks", report=str(report))
        cli.cmd_checks(args)
        assert report.exists()
        assert "layer ablation" in report.read_text()


class TestGroupBreakdownEndToEnd:
    def test_group_table_present_and_counts_match_channel_totals(self, workspace, tmp_path):
        report = tmp_path / "report.md"
        args = make_args(workspace, report=str(report), output=str(tmp_path / "scores.json"))
        cli.cmd_score(args)
        text = report.read_text()
        assert "## Scores by reasoning type" in text

        scores = json.loads((tmp_path / "scores.json").read_text())
        n_pf_total = sum(scores[f"grp_{p}_n_pf"] for p in ("cloze", "congen", "knowinf"))
        n_pc_total = sum(scores[f"grp_{p}_n_pc"] for p in ("cloze", "congen", "knowinf"))
        assert n_pf_total == scores["n_passfail"]
        assert n_pc_total == scores["n_partial"]
        # every pf question in this fixture is reasoning_type=knowledge
        assert scores["grp_knowinf_n_pf"] == scores["n_passfail"]
        # every pc question in this fixture is reasoning_type=constrained_generation
        assert scores["grp_congen_n_pc"] == scores["n_partial"]


class TestIdentity:
    def test_residuals_within_tolerance(self, capsys):
        cli.cmd_identity(None)
        out = capsys.readouterr().out
        assert "OK" in out
        assert "residual (binary == mean(v_q))" in out
        assert "residual (partition identity)" in out


class TestLengthCovariateFlagRemoved:
    def test_score_parser_has_no_length_covariate_flag(self):
        parser = cli.build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["score", "--scored-file", "x", "--length-covariate"])
