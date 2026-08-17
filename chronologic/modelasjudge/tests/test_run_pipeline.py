"""test_run_pipeline.py — execute()/select_stages() against a fake runner,
plus build_stages() skip predicates against a synthetic on-disk workspace.
No subprocess is ever actually spawned; no network, no PyMC.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

import run_pipeline as rp
from bt import artifacts as bt_artifacts
from substantive import artifacts as substantive_artifacts


# ---------------------------------------------------------------------------
# execute() / select_stages() -- pure logic, hand-built Stage lists
# ---------------------------------------------------------------------------

class FakeResult:
    def __init__(self, returncode=0):
        self.returncode = returncode


class FakeRunner:
    def __init__(self, fail_on: set[str] | None = None):
        self.calls: list[list[str]] = []
        self.fail_on = fail_on or set()

    def __call__(self, argv, cwd=None):
        self.calls.append(argv)
        rc = 1 if any(f in argv[0] or (len(argv) > 1 and f in argv[1]) for f in self.fail_on) else 0
        return FakeResult(rc)


def _stage(number, name, *, skip=False, argv=None, action=None, est_calls=0, est_fits=0):
    return rp.Stage(number, name, "instrument",
                    skip=rp.SkipResult(skip, "test"), argv=argv, action=action,
                    est_calls=est_calls, est_fits=est_fits)


class TestExecuteSkipLogic:
    def test_skipped_stage_never_calls_runner(self):
        stages = [_stage(0, "a", skip=True, argv=["prog", "a"])]
        runner = FakeRunner()
        ok = rp.execute(stages, runner=runner)
        assert ok
        assert runner.calls == []

    def test_non_skipped_stage_calls_runner(self):
        stages = [_stage(0, "a", skip=False, argv=["prog", "a"])]
        runner = FakeRunner()
        ok = rp.execute(stages, runner=runner)
        assert ok
        assert runner.calls == [["prog", "a"]]

    def test_force_overrides_skip_by_number(self):
        stages = [_stage(0, "a", skip=True, argv=["prog", "a"])]
        runner = FakeRunner()
        ok = rp.execute(stages, runner=runner, force=("0",))
        assert ok
        assert runner.calls == [["prog", "a"]]

    def test_force_overrides_skip_by_name(self):
        stages = [_stage(0, "a", skip=True, argv=["prog", "a"])]
        runner = FakeRunner()
        ok = rp.execute(stages, runner=runner, force=("a",))
        assert ok
        assert runner.calls == [["prog", "a"]]

    def test_force_does_not_affect_other_stages(self):
        stages = [_stage(0, "a", skip=True, argv=["prog", "a"]),
                 _stage(1, "b", skip=True, argv=["prog", "b"])]
        runner = FakeRunner()
        rp.execute(stages, runner=runner, force=("a",))
        assert runner.calls == [["prog", "a"]]


class TestExecuteFailurePropagation:
    def test_failure_stops_iteration(self):
        stages = [_stage(0, "a", argv=["progA", "x"]),
                 _stage(1, "b", argv=["progB", "x"]),
                 _stage(2, "c", argv=["progC", "x"])]
        runner = FakeRunner(fail_on={"progB"})
        ok = rp.execute(stages, runner=runner)
        assert not ok
        assert runner.calls == [["progA", "x"], ["progB", "x"]]  # c never runs

    def test_failure_prints_resume_command(self, capsys):
        stages = [_stage(0, "a", argv=["progA", "--flag", "value"])]
        runner = FakeRunner(fail_on={"progA"})
        rp.execute(stages, runner=runner)
        out = capsys.readouterr().out
        assert "progA --flag value" in out
        assert "failed" in out


class TestExecuteDryRun:
    def test_dry_run_calls_nothing(self):
        stages = [_stage(0, "a", skip=False, argv=["prog", "a"]),
                 _stage(1, "b", skip=True, argv=["prog", "b"])]
        runner = FakeRunner()
        ok = rp.execute(stages, runner=runner, dry_run=True)
        assert ok
        assert runner.calls == []

    def test_dry_run_does_not_invoke_action(self):
        called = []
        stages = [_stage(0, "a", skip=False, action=lambda runner: called.append(True))]
        rp.execute(stages, runner=FakeRunner(), dry_run=True)
        assert called == []


class TestExecuteActionStages:
    def test_action_receives_the_runner(self):
        seen = []
        stages = [_stage(0, "a", skip=False, action=lambda runner: seen.append(runner))]
        runner = FakeRunner()
        rp.execute(stages, runner=runner)
        assert seen == [runner]

    def test_pre_action_runs_before_subprocess(self):
        order = []
        stage = _stage(0, "a", skip=False, argv=["prog", "a"])
        stage.pre_action = lambda: order.append("pre")

        class OrderRunner(FakeRunner):
            def __call__(self, argv, cwd=None):
                order.append("run")
                return super().__call__(argv, cwd=cwd)

        rp.execute([stage], runner=OrderRunner())
        assert order == ["pre", "run"]


class TestSelectStages:
    def _stages(self):
        return [_stage(0, "alpha"), _stage(1, "beta"), _stage(2, "gamma")]

    def test_only_matches_by_number(self):
        got = rp.select_stages(self._stages(), only="1")
        assert [s.name for s in got] == ["beta"]

    def test_only_matches_by_name_case_insensitive(self):
        got = rp.select_stages(self._stages(), only="GAMMA")
        assert [s.name for s in got] == ["gamma"]

    def test_only_accepts_a_comma_list(self):
        got = rp.select_stages(self._stages(), only="0,2")
        assert [s.name for s in got] == ["alpha", "gamma"]

    def test_stop_after_truncates_inclusive(self):
        got = rp.select_stages(self._stages(), stop_after="beta")
        assert [s.name for s in got] == ["alpha", "beta"]

    def test_stop_after_unmatched_raises(self):
        with pytest.raises(ValueError):
            rp.select_stages(self._stages(), stop_after="nonexistent")

    def test_neither_flag_returns_everything(self):
        got = rp.select_stages(self._stages())
        assert [s.name for s in got] == ["alpha", "beta", "gamma"]


class TestCostTable:
    def test_sums_only_running_stages(self):
        stages = [
            _stage(0, "a", skip=False, est_calls=100, est_fits=1),
            _stage(1, "b", skip=True, est_calls=9999, est_fits=9),  # skipped -- excluded
            _stage(2, "c", skip=False, est_calls=50, est_fits=0),
        ]
        calls, fits = rp.total_estimated_cost(stages)
        assert calls == 150
        assert fits == 1

    def test_all_skipped_sums_to_zero(self):
        stages = [_stage(0, "a", skip=True, est_calls=500, est_fits=5)]
        assert rp.total_estimated_cost(stages) == (0, 0)


# ---------------------------------------------------------------------------
# build_stages() -- skip predicates against a synthetic on-disk workspace
# ---------------------------------------------------------------------------

def _write_benchmark(path, pf_qnums, pc_qnums):
    with open(path, "w") as f:
        for q in pf_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 0, "frame_type": "world_context",
                "question_category": "knowledge",
                "answer_types": ["ground_truth", "same_book"],
                "answer_strings": ["a ground truth answer"],
            }) + "\n")
        for q in pc_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 1, "frame_type": "book_context",
                "question_category": "plot",
                "answer_types": ["ground_truth", "same_book"],
                "answer_strings": ["a ground truth answer"],
            }) + "\n")


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "RELIABILITY_DIR", tmp_path / "llm_reliability")
    monkeypatch.setattr(rp, "PENALTIES_PATH", tmp_path / "distractor_penalties.txt")
    monkeypatch.setattr(rp, "SCORED_DIR", tmp_path / "scored_answers")
    monkeypatch.setattr(rp, "GENERATED_ANSWERS_DIR", tmp_path / "generated_answers")
    monkeypatch.setattr(bt_artifacts, "ARTIFACT_DIR", tmp_path / "bt_artifacts")
    monkeypatch.setattr(substantive_artifacts, "BETA_RELIABILITY_DIR", tmp_path / "beta_reliability")
    monkeypatch.setattr(substantive_artifacts, "SUBSTANTIVE_ARTIFACTS_DIR", tmp_path / "substantive_artifacts")

    (tmp_path / "llm_reliability").mkdir()
    (tmp_path / "distractor_penalties.txt").write_text(
        "same_book\tquestion\nground_truth\tboth\n", encoding="utf-8")

    pf_qnums = ["1", "2"]
    pc_qnums = ["10", "11"]
    benchmark = tmp_path / "bench_0.7.jsonl"
    _write_benchmark(benchmark, pf_qnums, pc_qnums)

    return dict(tmp_path=tmp_path, benchmark=benchmark, pf_qnums=pf_qnums, pc_qnums=pc_qnums)


def make_args(ws, **overrides):
    class Args:
        pass
    a = Args()
    a.candidate = "cand-model"
    a.candidate_label = "cand"
    a.benchmark = str(ws["benchmark"])
    a.judge = "testjudge"
    a.bt_judge = "testbtjudge"
    a.judge_effort = "medium"
    a.candidate_effort = "none"
    a.prior_scale = 3.0
    a.prompt_mode = "rationales"
    a.loo_subsample = 4
    a.pool_pilot = False
    a.pilot_labels = None
    a.refresh_style = False
    a.python = sys.executable
    a.seed_reliability_from = "0.4"
    for k, v in overrides.items():
        setattr(a, k, v)
    return a


class TestBuildStagesStage0:
    def test_skips_when_all_answer_types_classified(self, workspace):
        args = make_args(workspace)
        stages = rp.build_stages(args)
        assert stages[0].skip.skip

    def test_runs_when_answer_types_unclassified(self, workspace):
        _write_benchmark(workspace["benchmark"], workspace["pf_qnums"] + ["3"], workspace["pc_qnums"])
        # question 3 reuses the default fixture answer_types (same_book, classified);
        # write a fresh benchmark with an unclassified type instead.
        with open(workspace["benchmark"], "a") as f:
            f.write(json.dumps({
                "question_number": 99, "partial_credit": 0, "frame_type": "world_context",
                "question_category": "knowledge",
                "answer_types": ["ground_truth", "anachronistic_9999"],
                "answer_strings": ["x"],
            }) + "\n")
        args = make_args(workspace)
        stages = rp.build_stages(args)
        assert not stages[0].skip.skip
        assert "anachronistic_9999" in stages[0].skip.reason


class TestBuildStagesStage1And2:
    def test_stage1_skips_when_target_reliability_exists(self, workspace):
        target = workspace["tmp_path"] / "llm_reliability" / "testjudge__0.7.json"
        target.write_text(json.dumps({"reasoning_effort": "medium", "per_question": {}}))
        stages = rp.build_stages(make_args(workspace))
        assert stages[1].skip.skip

    def test_stage2_skips_when_all_pf_qnums_scored(self, workspace):
        target = workspace["tmp_path"] / "llm_reliability" / "testjudge__0.7.json"
        target.write_text(json.dumps({
            "reasoning_effort": "medium",
            "per_question": {q: {"question_correct": 8, "question_total": 8}
                             for q in workspace["pf_qnums"]},
        }))
        stages = rp.build_stages(make_args(workspace))
        assert stages[2].skip.skip

    def test_stage2_runs_when_pf_qnums_missing(self, workspace):
        stages = rp.build_stages(make_args(workspace))
        assert not stages[2].skip.skip
        assert stages[2].est_calls == len(workspace["pf_qnums"]) * rp.AVG_TRIALS_PER_ALPHA_Q


class TestBuildStagesStage8And9:
    def test_stage8_skips_when_free_gen_complete(self, workspace):
        gen_dir = workspace["tmp_path"] / "generated_answers"
        gen_dir.mkdir()
        total = len(workspace["pf_qnums"]) + len(workspace["pc_qnums"])
        (gen_dir / "free_gen_cand__0.7.json").write_text(json.dumps({
            "answers": {str(i): {"answer": "x"} for i in range(total)}
        }))
        stages = rp.build_stages(make_args(workspace))
        assert stages[8].skip.skip

    def test_stage9_runs_when_scored_file_absent(self, workspace):
        stages = rp.build_stages(make_args(workspace))
        assert not stages[9].skip.skip
        assert stages[9].est_calls == len(workspace["pf_qnums"])


class TestBuildStagesStage11And12:
    def test_stage11_never_skipped(self, workspace):
        stages = rp.build_stages(make_args(workspace))
        assert not stages[11].skip.skip

    def test_stage12_skipped_unless_refresh_style(self, workspace):
        stages = rp.build_stages(make_args(workspace))
        assert stages[12].skip.skip
        stages = rp.build_stages(make_args(workspace, refresh_style=True))
        assert not stages[12].skip.skip


class TestStageNumbersAreSequential:
    def test_thirteen_stages_numbered_0_through_12(self, workspace):
        stages = rp.build_stages(make_args(workspace))
        assert [s.number for s in stages] == list(range(13))
