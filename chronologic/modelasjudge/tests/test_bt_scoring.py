"""test_bt_scoring.py — end-to-end test of the `score` CLI subcommand
against tmp_path fixtures, with the real judge replaced by a stub
(monkeypatched module factory). No network calls.

Run with:
    pytest modelasjudge/tests/test_bt_scoring.py -v
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

import bt_context_scoring as cli
from bt import artifacts
from bt.fit import AnchorFit, save_anchor_fits


QUESTION = {
    "question_number": 1,
    "frame_type": "book_context",
    "reasoning_type": "constrained_generation",
    "metadata_frame": "A medical periodical, 1840s Britain.",
    "main_question": "Describe the limits of phrenology.",
    "answer_strings": ["gt text zero", "gt text one", "distractor text zero"],
    "answer_types": ["ground_truth", "ground_truth", "anachronistic_x"],
    "answer_probabilities": [1.0, 1.0, 0.0],
    "reject_reasons": ["", "", "too modern"],
}

QUESTION_OTHER_ASPECT = {
    "question_number": 2,
    "frame_type": "world_context",  # not context-scored
    "reasoning_type": "knowledge",
    "metadata_frame": "x", "main_question": "y",
    "answer_strings": ["a", "b"], "answer_types": ["ground_truth", "manual"],
    "answer_probabilities": [1.0, 0.0],
}


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    benchmark_path = tmp_path / "bench.jsonl"
    with benchmark_path.open("w") as f:
        f.write(json.dumps(QUESTION) + "\n")
        f.write(json.dumps(QUESTION_OTHER_ASPECT) + "\n")

    scored_path = tmp_path / "judge_test__cand__0.1__c-none__j-none.json"
    scored_path.write_text(json.dumps({
        "judge_model": "test", "candidate_model": "cand", "benchmark_version": "0.1",
        "question_fit": {}, "context_fit": {}, "book_context_qnums": ["1"],
    }))

    free_gen_path = tmp_path / "free_gen.json"
    free_gen_path.write_text(json.dumps({
        "model": "cand", "answers": {
            "1": {"answer": "candidate answer text"},
            "2": {"answer": "unrelated answer"},
        },
    }))

    # Pre-built tiny anchor fit for question "1" (3 items: gt0, gt1, d0).
    monkeypatch.setattr(artifacts, "ARTIFACT_DIR", tmp_path / "bt_artifacts")
    rng = np.random.default_rng(0)
    draws = rng.normal(0, 1, size=(200, 3))
    draws -= draws.mean(axis=1, keepdims=True)
    fit = AnchorFit(item_ids=["gt0", "gt1", "d0"], theta_draws=draws, prior_scale=1.0)
    tag = artifacts.bt_tag("anthropic/claude-sonnet-5", benchmark_path, "medium")
    save_anchor_fits(artifacts.anchors_path(tag), {"1": fit}, meta={"judge": "test"})

    calib_path = artifacts.calibration_path(tag)
    calib_path.parent.mkdir(parents=True, exist_ok=True)
    calib_path.write_text(json.dumps({"intercept": 0.0, "slope": 1.0}))

    call_counter = {"n": 0}

    def stub_factory(args):
        def judge_call(comp, system, user):
            call_counter["n"] += 1
            # Candidate always loses to everything -> low tau/p_fit, but
            # deterministic and always parseable.
            return '{"context fit": "B"}'
        return judge_call

    monkeypatch.setattr(cli, "make_judge_call_from_args", stub_factory)

    return {
        "benchmark": benchmark_path, "scored": scored_path, "free_gen": free_gen_path,
        "tag": tag, "call_counter": call_counter, "tmp_path": tmp_path,
    }


def make_args(ws, **overrides):
    class Args:
        pass
    a = Args()
    a.judge = "anthropic/claude-sonnet-5"
    a.judge_effort = "medium"
    a.seed = 20260728
    a.benchmark = str(ws["benchmark"])
    a.repeats = 1
    a.prior_scale = 1.0
    a.prompt_mode = artifacts.DEFAULT_PROMPT_MODE
    a.prior_dist = "normal"
    a.prior_df = 3.0
    a.questions = None
    a.no_cache = False
    a.dry_run = False
    a.debug = False
    a.scored_file = str(ws["scored"])
    a.free_gen = str(ws["free_gen"])
    a.output = None
    a.emit_calibration_row = None
    for k, v in overrides.items():
        setattr(a, k, v)
    return a


class TestScoreEndToEnd:
    def test_output_format_and_input_untouched(self, workspace):
        args = make_args(workspace)
        cli.cmd_score(args)

        out_path = workspace["scored"].parent / f"{workspace['scored'].stem}_btcontext.json"
        assert out_path.exists()
        out = json.loads(out_path.read_text())

        assert "1" in out["context_fit"]
        entry = out["context_fit"]["1"]
        assert isinstance(entry["scores"], list) and len(entry["scores"]) == 1
        assert 0.0 <= entry["scores"][0] <= 1.0
        assert entry["judge"] == "bt:anthropic/claude-sonnet-5"
        assert "bt" in entry
        assert set(entry["bt"]) >= {
            "p_fit", "p_fit_ci", "tau_mean", "tau_ci", "delta_cg_mean", "delta_cg_ci",
            "reference_gt", "withdrawn_gts", "n_comparisons", "dropped_pairs", "artifacts_tag",
        }
        assert "2" not in out["context_fit"]  # non-context question untouched

        # Original input file was not modified.
        original = json.loads(workspace["scored"].read_text())
        assert original["context_fit"] == {}

    def test_cache_makes_second_run_zero_calls(self, workspace):
        args = make_args(workspace)
        cli.cmd_score(args)
        n_after_first = workspace["call_counter"]["n"]
        assert n_after_first > 0

        cli.cmd_score(args)
        n_after_second = workspace["call_counter"]["n"]
        assert n_after_second == n_after_first  # all served from cache

    def test_artifacts_tag_matches_bt_tag(self, workspace):
        args = make_args(workspace)
        cli.cmd_score(args)
        out_path = workspace["scored"].parent / f"{workspace['scored'].stem}_btcontext.json"
        out = json.loads(out_path.read_text())
        assert out["context_fit"]["1"]["bt"]["artifacts_tag"] == workspace["tag"]
        assert out["bt_context"]["artifacts_tag"] == workspace["tag"]


class TestPriorScaleGuard:
    """theta scales ~linearly with prior_scale under near-complete separation,
    and calibration silently undoes it (pilot: Delta inflated 2.81x from
    ps=1->3, b compensated 2.78x, p_fit moved a median 0.009). The
    cancellation only holds when b is applied on the scale it was fitted on,
    so mixing artifacts is a large silent error -- and prior_scale is not in
    the artifact tag, so nothing else catches it."""

    def test_matching_scales_pass(self):
        cli.check_prior_scale_consistency(
            {"prior_scale": 1.0}, {"intercept": 0.5, "slope": 1.8, "prior_scale": 1.0}, 1.0)

    def test_calibration_from_a_different_scale_raises(self):
        with pytest.raises(cli.PriorScaleMismatch, match="prior_scale differs"):
            cli.check_prior_scale_consistency(
                {"prior_scale": 1.0}, {"intercept": 0.6, "slope": 0.65, "prior_scale": 3.0}, 1.0)

    def test_candidate_grid_disagreeing_with_anchors_raises(self):
        with pytest.raises(cli.PriorScaleMismatch):
            cli.check_prior_scale_consistency(
                {"prior_scale": 1.0}, {"intercept": 0.5, "slope": 1.8, "prior_scale": 1.0}, 3.0)

    def test_no_calibration_still_checks_the_anchors(self):
        cli.check_prior_scale_consistency({"prior_scale": 2.0}, None, 2.0)
        with pytest.raises(cli.PriorScaleMismatch):
            cli.check_prior_scale_consistency({"prior_scale": 2.0}, None, 1.0)

    def test_unstamped_artifacts_warn_but_proceed(self, capsys):
        """Artifacts written before the stamp existed must not hard-fail."""
        cli.check_prior_scale_consistency({}, {"intercept": 0.5, "slope": 1.8}, 1.0)
        out = capsys.readouterr().out
        assert "no prior_scale recorded" in out
        assert "anchors" in out and "calibration" in out

    def test_the_error_names_the_offending_values(self):
        with pytest.raises(cli.PriorScaleMismatch) as e:
            cli.check_prior_scale_consistency(
                {"prior_scale": 1.0}, {"prior_scale": 3.0}, 1.0)
        msg = str(e.value)
        assert "anchors=1.0" in msg and "calibration=3.0" in msg

    def test_score_refuses_a_mismatched_calibration(self, workspace):
        """End to end: the guard fires inside cmd_score, before any judging."""
        tag = workspace["tag"]
        calib_path = artifacts.calibration_path(tag)
        calib_path.write_text(json.dumps({"intercept": 0.6, "slope": 0.647, "prior_scale": 3.0}))
        args = make_args(workspace)          # candidate grid + anchors at 1.0
        with pytest.raises(cli.PriorScaleMismatch):
            cli.cmd_score(args)
        assert workspace["call_counter"]["n"] == 0   # refused before spending


class TestMissingCalibrationRaises:
    """spec §8.9: uncalibrated tau is not on the p_q scale and must never
    enter a pooled score, so a missing calibration file is a hard error --
    not a silent fall back to score.tau_mean."""

    def test_score_raises_when_no_calibration_file_exists(self, workspace):
        tag = workspace["tag"]
        calib_path = artifacts.calibration_path(tag)
        calib_path.unlink()   # the `workspace` fixture writes one by default
        args = make_args(workspace)
        with pytest.raises(FileNotFoundError, match="calibration"):
            cli.cmd_score(args)
        assert workspace["call_counter"]["n"] == 0   # refused before spending


class TestSubstantiveFrameReachesThePromptBuilder:
    def test_prefers_substantive_metadata_frame_when_present(self, workspace, monkeypatch):
        bench = json.loads(workspace["benchmark"].read_text().splitlines()[0])
        bench["substantive_metadata_frame"] = "ADJUSTED FRAME TEXT"
        rewritten = "\n".join([json.dumps(bench)]
                              + workspace["benchmark"].read_text().splitlines()[1:])
        workspace["benchmark"].write_text(rewritten)

        seen_frames = []
        real_build = cli.build_bt_prompt

        def spy(frame, *a, **kw):
            seen_frames.append(frame)
            return real_build(frame, *a, **kw)
        monkeypatch.setattr(cli, "build_bt_prompt", spy)

        args = make_args(workspace)
        cli.cmd_score(args)
        assert seen_frames and all(f == "ADJUSTED FRAME TEXT" for f in seen_frames)

    def test_falls_back_to_metadata_frame_when_absent(self, workspace, monkeypatch):
        seen_frames = []
        real_build = cli.build_bt_prompt

        def spy(frame, *a, **kw):
            seen_frames.append(frame)
            return real_build(frame, *a, **kw)
        monkeypatch.setattr(cli, "build_bt_prompt", spy)

        args = make_args(workspace)
        cli.cmd_score(args)
        assert seen_frames and all(f == QUESTION["metadata_frame"] for f in seen_frames)


class TestContextJudgedSelection:
    """context_judged alone defines the pool. It exists so suitability is a
    direct editorial decision, not a side effect of reasoning_type -- the old
    rule silently dropped 3 questions their author had flagged on purpose."""

    def _write(self, tmp_path, recs):
        p = tmp_path / "b.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in recs))
        return p

    def test_flag_wins_over_reasoning_type(self, tmp_path):
        """A flagged question of any reasoning_type is in; an unflagged
        constrained_generation question is out."""
        recs = [
            {"question_number": 1, "context_judged": 1,
             "frame_type": "book_context", "reasoning_type": "character_modeling"},
            {"question_number": 2, "context_judged": 1,
             "frame_type": "book_context", "reasoning_type": "topic_sentence"},
            {"question_number": 3, "context_judged": 0,
             "frame_type": "book_context", "reasoning_type": "constrained_generation"},
        ]
        got = cli.load_benchmark(self._write(tmp_path, recs))
        assert set(got) == {"1", "2"}

    def test_falls_back_when_no_record_carries_the_flag(self, tmp_path, capsys):
        """Released chronologic_en_*.jsonl have no context_judged; filtering on
        it alone would select nothing, so the old rule still applies there."""
        recs = [
            {"question_number": 1, "frame_type": "book_context",
             "reasoning_type": "constrained_generation"},
            {"question_number": 2, "frame_type": "world_context",
             "reasoning_type": "knowledge"},
        ]
        got = cli.load_benchmark(self._write(tmp_path, recs))
        assert set(got) == {"1"}
        assert "no partial_credit or context_judged field" in capsys.readouterr().out

    def test_a_flagged_file_is_taken_at_its_word(self, tmp_path):
        """Presence of the field anywhere switches off the fallback, so a 0 is
        honoured even on a question the old rule would have selected."""
        recs = [
            {"question_number": 1, "context_judged": 1,
             "frame_type": "book_context", "reasoning_type": "constrained_generation"},
            {"question_number": 2,
             "frame_type": "book_context", "reasoning_type": "constrained_generation"},
        ]
        got = cli.load_benchmark(self._write(tmp_path, recs))
        assert set(got) == {"1"}

    def test_the_pilot_benchmark_still_selects_all_forty(self):
        bm = MODELASJUDGE.parent / "booksample" / "chronologic_btpilot_0.1.jsonl"
        if bm.exists():
            assert len(cli.load_benchmark(bm)) == 40


class TestAnchorFitMerges:
    """save_anchor_fits rewrites the whole archive, so a --questions run must
    merge into what is already there or it silently discards every question it
    did not refit."""

    def test_subset_run_preserves_the_other_questions(self, tmp_path, monkeypatch):
        from bt.fit import AnchorFit, save_anchor_fits, load_anchor_fits
        monkeypatch.setattr(artifacts, "ARTIFACT_DIR", tmp_path / "bt_artifacts")
        rng = np.random.default_rng(0)
        mk = lambda: AnchorFit(item_ids=["gt0", "d0"],
                               theta_draws=rng.normal(0, 1, size=(50, 2)), prior_scale=1.0)
        path = artifacts.anchors_path("t")
        save_anchor_fits(path, {"1": mk(), "2": mk(), "3": mk()}, meta={"seed": 1})

        existing, prior_meta = load_anchor_fits(path)
        refit = {"2": mk()}
        merged = dict(existing); merged.update(refit)
        save_anchor_fits(path, merged, meta={**prior_meta, "seed": 2})

        back, meta = load_anchor_fits(path)
        assert set(back) == {"1", "2", "3"}, "a subset refit dropped other questions"
        assert meta["seed"] == 2
        assert np.allclose(back["1"].theta_draws, existing["1"].theta_draws)
        assert not np.allclose(back["2"].theta_draws, existing["2"].theta_draws)
