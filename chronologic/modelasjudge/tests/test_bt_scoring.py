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
from substantive import artifacts as substantive_artifacts


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
    monkeypatch.setattr(substantive_artifacts, "SUBSTANTIVE_ARTIFACTS_DIR",
                        tmp_path / "substantive_artifacts")
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
    a.save_delta_draws = None
    a.thin = 1000
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


class TestSaveDeltaDraws:
    def test_bare_flag_writes_one_key_per_scored_question(self, workspace):
        args = make_args(workspace, save_delta_draws="")
        cli.cmd_score(args)
        path = substantive_artifacts.delta_draws_path(workspace["tag"], "cand", "none")
        assert path.exists()
        arrays, meta = substantive_artifacts.load_npz(path)
        assert "delta__1" in arrays
        assert "c_len__1" in arrays
        assert meta["candidate_label"] == "cand"
        assert meta["bt_tag"] == workspace["tag"]

    def test_explicit_path_overrides_derived_path(self, workspace, tmp_path):
        out = tmp_path / "custom_delta.npz"
        args = make_args(workspace, save_delta_draws=str(out))
        cli.cmd_score(args)
        assert out.exists()
        arrays, _meta = substantive_artifacts.load_npz(out)
        assert "delta__1" in arrays

    def test_omitted_flag_writes_nothing(self, workspace):
        args = make_args(workspace)   # save_delta_draws=None by default
        cli.cmd_score(args)
        path = substantive_artifacts.delta_draws_path(workspace["tag"], "cand", "none")
        assert not path.exists()

    def test_thin_caps_draw_count(self, workspace):
        args = make_args(workspace, save_delta_draws="", thin=50)
        cli.cmd_score(args)
        path = substantive_artifacts.delta_draws_path(workspace["tag"], "cand", "none")
        arrays, meta = substantive_artifacts.load_npz(path)
        assert arrays["delta__1"].shape[0] == 50
        assert meta["thin"] == 50


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


class TestEmitPilotLabels:
    """qid namespacing: pilot qid '3' (benchmark 0.1) and production qid
    '3' (0.7) are different questions; the cluster bootstrap resamples by
    qid, so leaving both bare would silently merge them (plan §4)."""

    def test_qids_are_namespaced_and_version_stamped(self, tmp_path, monkeypatch):
        monkeypatch.setattr(artifacts, "ARTIFACT_DIR", tmp_path / "bt_artifacts")
        pilot_bm = tmp_path / "chronologic_btpilot_0.1.jsonl"
        pilot_bm.write_text("")   # only benchmark_version(path) is used, no parsing

        tag = artifacts.bt_tag("anthropic/claude-sonnet-5", pilot_bm, "medium")
        artifacts.write_json(artifacts.loo_path(tag), {
            "meta": {},
            "records": [
                {"qid": "3", "item_id": "gt0", "kind": "ground_truth", "prob": 1.0,
                 "delta_mean": 2.0},
                {"qid": "3", "item_id": "d0", "kind": "distractor", "prob": 0.0,
                 "delta_mean": -2.0},
            ],
        })

        out = tmp_path / "pilot_rows.jsonl"

        class Args:
            pass
        a = Args()
        a.judge = "anthropic/claude-sonnet-5"
        a.judge_effort = "medium"
        a.pilot_benchmark = str(pilot_bm)
        a.prior_scale = 1.0
        a.prior_dist = "normal"
        a.prompt_mode = artifacts.DEFAULT_PROMPT_MODE
        a.output = str(out)
        cli.cmd_emit_pilot_labels(a)

        rows = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        assert len(rows) == 2
        assert all(r["qid"] == "pilot:3" for r in rows)
        assert all(r["benchmark_version"] == "0.1" for r in rows)

    def test_collision_with_production_qid_is_caught_by_verify_compatible(self, tmp_path, monkeypatch):
        """The trap this namespacing prevents, demonstrated: an UNnamespaced
        merge of pilot qid '3' and production qid '3' collides two versions
        under one cluster id, and drawbank.verify_compatible must catch it."""
        from substantive.drawbank import ArtifactMismatch, verify_compatible
        unnamespaced_cluster_ids = [["3", "0.1"], ["3", "0.7"]]
        with pytest.raises(ArtifactMismatch, match="more than one benchmark version"):
            verify_compatible({"calib": {"cluster_ids": unnamespaced_cluster_ids}})


# ---------------------------------------------------------------------------
# Automatic verdicts on the partial-credit path
# ---------------------------------------------------------------------------

def _rewrite_free_gen(ws, answer):
    ws["free_gen"].write_text(json.dumps({
        "model": "cand",
        "answers": {"1": {"answer": answer}, "2": {"answer": "unrelated answer"}},
    }))


class TestAutoVerdictShortCircuit:
    """A verbatim match to an answer option is a certainty, so it must produce
    its verdict without spending a single judge call."""

    def test_ground_truth_match_scores_one_with_no_judge_calls(self, workspace):
        _rewrite_free_gen(workspace, "gt text zero")
        cli.cmd_score(make_args(workspace))

        out = json.loads((workspace["scored"].parent /
                          f"{workspace['scored'].stem}_btcontext.json").read_text())
        entry = out["context_fit"]["1"]
        assert entry["scores"] == [1.0]
        assert entry["judge"] == "bt:identity"
        assert entry["bt"]["p_fit"] == 1.0
        assert entry["bt"]["auto_verdict"] == "gt_identity"
        assert entry["bt"]["n_comparisons"] == 0
        assert workspace["call_counter"]["n"] == 0     # spent nothing

    def test_distractor_match_scores_zero_with_no_judge_calls(self, workspace):
        _rewrite_free_gen(workspace, "distractor text zero")
        cli.cmd_score(make_args(workspace))

        entry = json.loads((workspace["scored"].parent /
                            f"{workspace['scored'].stem}_btcontext.json").read_text()
                           )["context_fit"]["1"]
        assert entry["scores"] == [0.0]
        assert entry["bt"]["auto_verdict"] == "distractor_identity"
        assert entry["bt"]["n_comparisons"] == 0
        assert workspace["call_counter"]["n"] == 0

    def test_context_class_distractor_still_auto_fails_here(self, workspace):
        """anachronistic_x is "context" class -- exempt on the pass/fail path,
        but the partial-credit path covers context fit, so it fails."""
        _rewrite_free_gen(workspace, "distractor text zero")
        cli.cmd_score(make_args(workspace))
        entry = json.loads((workspace["scored"].parent /
                            f"{workspace['scored'].stem}_btcontext.json").read_text()
                           )["context_fit"]["1"]
        assert entry["scores"] == [0.0]

    def test_normalization_insensitive(self, workspace):
        _rewrite_free_gen(workspace, "  GT Text Zero.  ")
        cli.cmd_score(make_args(workspace))
        entry = json.loads((workspace["scored"].parent /
                            f"{workspace['scored'].stem}_btcontext.json").read_text()
                           )["context_fit"]["1"]
        assert entry["bt"]["auto_verdict"] == "gt_identity"
        assert workspace["call_counter"]["n"] == 0

    def test_a_normal_candidate_still_spends(self, workspace):
        """Control: without a verbatim match, judging proceeds as before."""
        cli.cmd_score(make_args(workspace))
        entry = json.loads((workspace["scored"].parent /
                            f"{workspace['scored'].stem}_btcontext.json").read_text()
                           )["context_fit"]["1"]
        assert "auto_verdict" not in entry["bt"]
        assert entry["bt"]["n_comparisons"] > 0
        assert workspace["call_counter"]["n"] > 0

    def test_auto_entry_keeps_the_full_bt_key_set(self, workspace):
        """Downstream readers index these unconditionally."""
        cli.cmd_score(make_args(workspace))
        judged = json.loads((workspace["scored"].parent /
                             f"{workspace['scored'].stem}_btcontext.json").read_text()
                            )["context_fit"]["1"]["bt"]
        _rewrite_free_gen(workspace, "gt text zero")
        cli.cmd_score(make_args(workspace))
        auto = json.loads((workspace["scored"].parent /
                           f"{workspace['scored'].stem}_btcontext.json").read_text()
                          )["context_fit"]["1"]["bt"]
        assert set(judged) <= set(auto)

    def test_delta_cg_is_json_null_not_nan(self, workspace):
        """json.dumps writes a bare NaN literal that strict parsers reject."""
        _rewrite_free_gen(workspace, "gt text zero")
        cli.cmd_score(make_args(workspace))
        raw = (workspace["scored"].parent /
               f"{workspace['scored'].stem}_btcontext.json").read_text()
        assert "NaN" not in raw
        entry = json.loads(raw)["context_fit"]["1"]
        assert entry["bt"]["delta_cg_mean"] is None


class TestAutoVerdictDeltaDraws:
    def test_auto_key_written_and_delta_row_is_nan(self, workspace):
        _rewrite_free_gen(workspace, "gt text zero")
        draws_path = workspace["tmp_path"] / "delta.npz"
        cli.cmd_score(make_args(workspace, save_delta_draws=str(draws_path), thin=50))

        arrays, meta = substantive_artifacts.load_npz(draws_path)
        assert arrays["auto__1"] == 1.0
        assert np.all(np.isnan(arrays["delta__1"]))
        assert meta["pin_p"] is None            # this fixture's calibration is unpinned
        assert meta["class_balance"] is False

    def test_distractor_match_writes_zero(self, workspace):
        _rewrite_free_gen(workspace, "distractor text zero")
        draws_path = workspace["tmp_path"] / "delta.npz"
        cli.cmd_score(make_args(workspace, save_delta_draws=str(draws_path), thin=50))
        arrays, _ = substantive_artifacts.load_npz(draws_path)
        assert arrays["auto__1"] == 0.0

    def test_judged_question_writes_no_auto_key(self, workspace):
        draws_path = workspace["tmp_path"] / "delta.npz"
        cli.cmd_score(make_args(workspace, save_delta_draws=str(draws_path), thin=50))
        arrays, _ = substantive_artifacts.load_npz(draws_path)
        assert "auto__1" not in arrays
        assert not np.any(np.isnan(arrays["delta__1"]))
