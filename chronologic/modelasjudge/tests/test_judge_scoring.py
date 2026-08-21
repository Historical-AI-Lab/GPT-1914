"""test_judge_scoring.py — Tests for judge_scoring_nocontext.py and
judge_alpha_reliability_nocontext.py.

Uses stub judge functions; no network calls, no LLM needed.

Run with:
    pytest modelasjudge/tests/test_judge_scoring.py -v
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from judge_scoring_nocontext import (
    run_panel,
    _auto_output_path,
    _write_output,
    _normalize_for_identity,
    _rebuild_needs_human,
    _load_context_scored_qnums,
    _load_pass_fail_qnums,
)
from judge_alpha_reliability_nocontext import (
    compute_reliability, _load_distractor_penalties, _parse_questions_arg,
)

# Load once for all reliability tests.
_PENALTIES = _load_distractor_penalties()


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

def _make_stub_judge_factory(always_q):
    """Return a judge_call_factory that always returns the given question-fit choice."""
    def factory(model_id):
        response = f'{{"question fit": "{always_q}"}}'
        def judge_call(prompt):
            return response
        return judge_call
    return factory


def _make_bad_judge_factory():
    """Return a factory whose judge always returns invalid JSON."""
    def factory(model_id):
        def judge_call(prompt):
            return "not json"
        return judge_call
    return factory


# ---------------------------------------------------------------------------
# Fake data
# ---------------------------------------------------------------------------

FAKE_ANSWERS = {
    "1": {
        "metadata_frame": "This is context one.",
        "main_question": "Who wrote it?",
        "ground_truth": "Author One",
        "reasoning_type": "knowledge",
        "length_spec": "a few words",
        "answer": "Author One",
    },
    "2": {
        "metadata_frame": "This is context two.",
        "main_question": "What happened?",
        "ground_truth": "Something happened.",
        "reasoning_type": "inference",
        "length_spec": "one sentence of about 10-20 words",
        "answer": "Nothing happened.",
    },
    "3": {
        "metadata_frame": "Context three.",
        "main_question": "What is the theme?",
        "ground_truth": "Loss and memory.",
        "reasoning_type": "constrained_generation",
        "length_spec": "a short phrase",
        "answer": "Hope and renewal.",
    },
}

FAKE_BENCHMARK = [
    {
        "question_number": 1,
        "metadata_frame": "Context 1.",
        "main_question": "Who wrote it?",
        "reasoning_type": "knowledge",
        "answer_strings": ["Author One", "Robot Answer", "Anachronism"],
        "answer_types": ["ground_truth", "manual", "anachronistic_gpt-oss:20b"],
    },
    {
        "question_number": 2,
        "metadata_frame": "Context 2.",
        "main_question": "What happened?",
        "reasoning_type": "inference",
        "answer_strings": ["Something.", "Nothing.", "Robots did it."],
        "answer_types": ["ground_truth", "manual", "manual"],
    },
]


# ---------------------------------------------------------------------------
# run_panel tests
# ---------------------------------------------------------------------------

class TestRunPanel:
    def test_returns_single_dict(self):
        factory = _make_stub_judge_factory("C")
        result = run_panel(
            judge_model="test-judge",
            answers=FAKE_ANSWERS,
            judge_call_factory=factory,
            reliability={},
            seed=17,
        )
        # run_panel now returns a single dict (question_fit only)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"1", "2", "3"}

    def test_tie_always_passes(self):
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel(
            "test-judge", FAKE_ANSWERS, factory, reliability={}, seed=42
        )
        for qnum in qf_scores:
            assert all(s == 1 for s in qf_scores[qnum]["scores"])

    def test_no_context_keys_in_result(self):
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel(
            "test-judge", FAKE_ANSWERS, factory, reliability={}, seed=17
        )
        for entry in qf_scores.values():
            assert "context_outcome" not in entry
            assert "context_pass" not in entry

    def test_invalid_json_gives_invalid_outcome(self):
        factory = _make_bad_judge_factory()
        qf_scores = run_panel(
            "test-judge", FAKE_ANSWERS, factory, reliability={}, seed=17
        )
        for qnum in qf_scores:
            if qf_scores[qnum]["judge"] == "identity":
                assert all(j == "tie" for j in qf_scores[qnum]["judgments"])
                assert all(s == 1 for s in qf_scores[qnum]["scores"])
            else:
                assert all(j == "invalid" for j in qf_scores[qnum]["judgments"])
                assert all(s == 0 for s in qf_scores[qnum]["scores"])

    def test_limit_respected(self):
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel(
            "test-judge", FAKE_ANSWERS, factory, reliability={}, seed=17, limit=2
        )
        assert len(qf_scores) == 2

    def test_start_qnum_skips_earlier(self):
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel(
            "test-judge", FAKE_ANSWERS, factory, reliability={}, seed=17, start_qnum="2"
        )
        assert "1" not in qf_scores
        assert "2" in qf_scores

    def test_reproducible_with_same_seed(self):
        factory = _make_stub_judge_factory("A")
        qf1 = run_panel("test-judge", FAKE_ANSWERS, factory, reliability={}, seed=99)
        qf2 = run_panel("test-judge", FAKE_ANSWERS, factory, reliability={}, seed=99)
        for qnum in qf1:
            assert qf1[qnum]["gt_positions"] == qf2[qnum]["gt_positions"]

    def test_on_progress_called(self):
        factory = _make_stub_judge_factory("C")
        seen = []
        def on_progress(qnum, qf_entry):
            seen.append(qnum)
        run_panel("test-judge", FAKE_ANSWERS, factory, reliability={},
                  seed=17, on_progress=on_progress)
        assert sorted(seen) == ["1", "2", "3"]


# ---------------------------------------------------------------------------
# _rebuild_needs_human tests
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# _load_context_scored_qnums
# ---------------------------------------------------------------------------

class TestLoadContextScoredQnums:
    """_load_context_scored_qnums should return only book_context+constrained_generation."""

    def _write_benchmark(self, tmp_path, rows):
        p = tmp_path / "bench.jsonl"
        lines = [json.dumps(r) for r in rows]
        p.write_text("\n".join(lines))
        return p

    def test_only_constrained_generation_book_context_included(self, tmp_path):
        rows = [
            {"question_number": 1, "frame_type": "book_context",    "reasoning_type": "constrained_generation"},
            {"question_number": 2, "frame_type": "book_context",    "reasoning_type": "character_modeling"},
            {"question_number": 3, "frame_type": "book_context",    "reasoning_type": "topic_sentence"},
            {"question_number": 4, "frame_type": "world_context",   "reasoning_type": "constrained_generation"},
            {"question_number": 5, "frame_type": "passage_context", "reasoning_type": "phrase_cloze"},
        ]
        p = self._write_benchmark(tmp_path, rows)
        result = _load_context_scored_qnums(p)
        assert result == {"1"}, f"Expected only qnum '1', got {result}"

    def test_empty_benchmark_returns_empty_set(self, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("")
        assert _load_context_scored_qnums(p) == set()

    def test_missing_fields_do_not_raise(self, tmp_path):
        rows = [
            {"question_number": 10},                                  # no frame_type
            {"question_number": 11, "frame_type": "book_context"},   # no reasoning_type
        ]
        p = self._write_benchmark(tmp_path, rows)
        result = _load_context_scored_qnums(p)
        assert result == set()

    def test_multiple_constrained_generation(self, tmp_path):
        rows = [
            {"question_number": i, "frame_type": "book_context", "reasoning_type": "constrained_generation"}
            for i in range(5)
        ]
        p = self._write_benchmark(tmp_path, rows)
        result = _load_context_scored_qnums(p)
        assert result == {"0", "1", "2", "3", "4"}

    def test_partial_credit_field_takes_precedence(self, tmp_path):
        """When partial_credit is present it wins over the legacy rule --
        the fix for the 157-question drop on chronologic_en_0.7."""
        rows = [
            {"question_number": 1, "partial_credit": 1, "frame_type": "book_context",
             "reasoning_type": "character_modeling"},   # legacy rule would exclude this
            {"question_number": 2, "partial_credit": 0, "frame_type": "book_context",
             "reasoning_type": "constrained_generation"},  # legacy rule would include this
        ]
        p = self._write_benchmark(tmp_path, rows)
        assert _load_context_scored_qnums(p) == {"1"}

    def test_pass_fail_is_the_complement(self, tmp_path):
        rows = [
            {"question_number": 1, "partial_credit": 1},
            {"question_number": 2, "partial_credit": 0},
            {"question_number": 3, "partial_credit": 0},
        ]
        p = self._write_benchmark(tmp_path, rows)
        assert _load_context_scored_qnums(p) == {"1"}
        assert _load_pass_fail_qnums(p) == {"2", "3"}


class TestParseQuestionsArg:
    def test_none_means_no_restriction(self):
        assert _parse_questions_arg(None) is None
        assert _parse_questions_arg("") is None

    def test_comma_list(self):
        assert _parse_questions_arg("1,2,3") == {"1", "2", "3"}

    def test_comma_list_strips_whitespace(self):
        assert _parse_questions_arg(" 1 , 2 ,3") == {"1", "2", "3"}

    def test_at_file(self, tmp_path):
        f = tmp_path / "qnums.txt"
        f.write_text("1\n2\n\n3\n")
        assert _parse_questions_arg(f"@{f}") == {"1", "2", "3"}


class TestRebuildNeedsHuman:
    def _make_output_data(self, qf_entries, ctx_entries=None, book_ctx=None):
        return {
            "thresholds": {"question_fit": 0.65},
            "question_fit": qf_entries,
            "context_fit": ctx_entries or {},
            "book_context_qnums": list(book_ctx or []),
        }

    def test_low_qr_adds_question_fit(self):
        data = self._make_output_data(
            {"1": {"judge": "model", "r_q": 0.5}},
        )
        _rebuild_needs_human(data)
        assert any("question_fit" in item["aspects"] for item in data["needs_human"]
                   if item["qnum"] == "1")

    def test_high_qr_no_question_fit(self):
        data = self._make_output_data(
            {"1": {"judge": "model", "r_q": 0.9}},
        )
        _rebuild_needs_human(data)
        for item in data["needs_human"]:
            assert "question_fit" not in item["aspects"]

    def test_book_context_always_gets_context_fit(self):
        data = self._make_output_data(
            {"7": {"judge": "model", "r_q": 0.9}},
            book_ctx=["7"],
        )
        _rebuild_needs_human(data)
        items = [i for i in data["needs_human"] if i["qnum"] == "7"]
        assert len(items) == 1
        assert "context_fit" in items[0]["aspects"]

    def test_non_book_context_no_context_fit(self):
        data = self._make_output_data(
            {"7": {"judge": "model", "r_q": 0.9}},
            book_ctx=[],   # qnum 7 is world_context/passage_context
        )
        _rebuild_needs_human(data)
        for item in data["needs_human"]:
            assert "context_fit" not in item["aspects"]

    def test_already_human_judged_context_skipped(self):
        data = self._make_output_data(
            {"7": {"judge": "model", "r_q": 0.9}},
            ctx_entries={"7": {"judge": "human", "r_q": 0.85, "scores": [1]}},
            book_ctx=["7"],
        )
        _rebuild_needs_human(data)
        for item in data["needs_human"]:
            assert "context_fit" not in item["aspects"]

    def test_book_context_qnum_not_yet_scored_still_routed(self):
        # book_context qnum not in question_fit yet (being processed for first time)
        data = self._make_output_data(
            {},   # question_fit empty
            book_ctx=["42"],
        )
        _rebuild_needs_human(data)
        items = [i for i in data["needs_human"] if i["qnum"] == "42"]
        assert len(items) == 1
        assert "context_fit" in items[0]["aspects"]


# ---------------------------------------------------------------------------
# File I/O smoke test
# ---------------------------------------------------------------------------

class TestScoringFileIO:
    def test_write_and_reload(self):
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel(
            "test-judge", FAKE_ANSWERS, factory, reliability={}, seed=17
        )
        output_data = {
            "judge_model": "test-judge",
            "candidate_model": "test-candidate",
            "benchmark_version": "0.2",
            "question_fit": qf_scores,
            "context_fit": {},
            "book_context_qnums": [],
            "needs_human": [],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "scores.json"
            _write_output(out, output_data)
            assert out.exists()
            with open(out, encoding="utf-8") as fh:
                loaded = json.load(fh)
        assert loaded["judge_model"] == "test-judge"
        assert set(loaded["question_fit"].keys()) == {"1", "2", "3"}
        assert loaded["context_fit"] == {}
        for entry in loaded["question_fit"].values():
            assert "judgments" in entry
            assert "scores" in entry
            assert "gt_positions" in entry
            assert "r_q" in entry


# ---------------------------------------------------------------------------
# compute_reliability tests (question-only output)
# ---------------------------------------------------------------------------

class TestComputeReliability:
    def _tie_always(self):
        def judge_call(prompt):
            return '{"question fit": "C"}'
        return judge_call

    def _distractor_always_wins(self):
        def judge_call(prompt):
            return '{"question fit": "B"}'
        return judge_call

    def test_basic_structure_question_only(self):
        per_q = compute_reliability(FAKE_BENCHMARK, self._tie_always(),
                                    distractor_penalties=_PENALTIES)
        assert set(per_q.keys()) == {"1", "2"}
        for qnum, v in per_q.items():
            assert "question_correct" in v
            assert "question_total" in v
            assert "question_r" in v
            assert "question_invalid" in v
            assert "question_weight" in v
            assert "context_correct" not in v
            assert "context_total" not in v

    def test_totals_correct(self):
        per_q = compute_reliability(FAKE_BENCHMARK, self._tie_always(),
                                    distractor_penalties=_PENALTIES)
        # Q1: 2 distractors × 2 positions = 4; Q2: 2 distractors × 2 positions = 4
        assert per_q["1"]["question_total"] == 4
        assert per_q["2"]["question_total"] == 4

    def test_tie_tolerance_depends_on_penalty(self):
        # Q1 distractors: manual (penalty=both, tie wrong) + anachronistic (penalty=context, tie OK on question)
        # Always-tie judge → q_correct = 2 (anachronistic × 2 positions)
        per_q = compute_reliability(FAKE_BENCHMARK[:1], self._tie_always(),
                                    distractor_penalties=_PENALTIES)
        assert per_q["1"]["question_correct"] == 2
        assert abs(per_q["1"]["question_r"] - 0.5) < 0.01
        # Q2 has two manual distractors — ties wrong on question → all zero
        per_q2 = compute_reliability(FAKE_BENCHMARK[1:2], self._tie_always(),
                                     distractor_penalties=_PENALTIES)
        assert per_q2["2"]["question_correct"] == 0

    def test_static_a_judge_gives_r_half(self):
        def static_a(prompt):
            return '{"question fit": "A"}'
        per_q = compute_reliability(FAKE_BENCHMARK[:1], static_a,
                                    distractor_penalties=_PENALTIES)
        assert per_q["1"]["question_total"] == 4
        assert per_q["1"]["question_correct"] == 2
        assert abs(per_q["1"]["question_r"] - 0.5) < 0.01

    def test_limit_respected(self):
        per_q = compute_reliability(FAKE_BENCHMARK, self._tie_always(),
                                    distractor_penalties=_PENALTIES, limit=1)
        assert len(per_q) == 1

    def test_invalid_counted(self):
        def bad_judge(prompt):
            return "not json"
        per_q = compute_reliability(FAKE_BENCHMARK[:1], bad_judge,
                                    distractor_penalties=_PENALTIES)
        assert per_q["1"]["question_invalid"] > 0

    def test_multiple_ground_truths(self):
        bench = [{
            "question_number": 88,
            "metadata_frame": "Context.",
            "main_question": "Who?",
            "reasoning_type": "knowledge",
            "answer_strings": ["GT-A", "GT-B", "Robot"],
            "answer_types": ["ground_truth", "ground_truth", "manual"],
        }]
        per_q = compute_reliability(bench, self._tie_always(),
                                    distractor_penalties=_PENALTIES)
        # 2 GTs × 1 distractor × 2 positions = 4
        assert per_q["88"]["question_total"] == 4

    def test_unknown_distractor_type_skipped(self):
        bench = [{
            "question_number": 77,
            "metadata_frame": "Context.",
            "main_question": "Who?",
            "reasoning_type": "knowledge",
            "answer_strings": ["GT", "Distractor"],
            "answer_types": ["ground_truth", "unknown_type_xyz"],
        }]
        per_q = compute_reliability(bench, self._tie_always(),
                                    distractor_penalties=_PENALTIES)
        assert per_q["77"]["question_total"] == 0


# ---------------------------------------------------------------------------
# Identity short-circuit tests
# ---------------------------------------------------------------------------

def _make_exploding_judge_factory():
    def factory(model_id):
        def judge_call(prompt):
            raise AssertionError("LLM judge should not be called for identity match")
        return judge_call
    return factory


class TestIdentityShortCircuit:
    def test_verbatim_match_uses_identity_judge(self):
        factory = _make_exploding_judge_factory()
        qf_scores = run_panel(
            "test-judge", {"1": FAKE_ANSWERS["1"]}, factory, reliability={}, seed=17
        )
        assert qf_scores["1"]["judge"] == "identity"
        assert qf_scores["1"]["r_q"] == 0.999
        assert all(j == "tie" for j in qf_scores["1"]["judgments"])
        assert all(s == 1 for s in qf_scores["1"]["scores"])
        assert all(p in ("A", "B") for p in qf_scores["1"]["gt_positions"])

    def test_case_insensitive_match(self):
        answers = {"x": {**FAKE_ANSWERS["1"], "answer": "author one"}}
        factory = _make_exploding_judge_factory()
        qf_scores = run_panel("test-judge", answers, factory, reliability={}, seed=17)
        assert qf_scores["x"]["judge"] == "identity"

    def test_punctuation_insensitive_match(self):
        answers = {"x": {**FAKE_ANSWERS["1"], "answer": "Author One."}}
        factory = _make_exploding_judge_factory()
        qf_scores = run_panel("test-judge", answers, factory, reliability={}, seed=17)
        assert qf_scores["x"]["judge"] == "identity"

    def test_non_match_uses_llm_judge(self):
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel(
            "test-judge", {"3": FAKE_ANSWERS["3"]}, factory, reliability={}, seed=17
        )
        assert qf_scores["3"]["judge"] == "test-judge"

    def test_empty_answer_does_not_short_circuit(self):
        answers = {"x": {**FAKE_ANSWERS["1"], "answer": "", "ground_truth": ""}}
        factory = _make_stub_judge_factory("C")
        qf_scores = run_panel("test-judge", answers, factory, reliability={}, seed=17)
        assert qf_scores["x"]["judge"] == "test-judge"

    def test_multi_gt_partial_match_short_circuits(self):
        answers = {"x": {
            "metadata_frame": "Context.",
            "main_question": "Who?",
            "ground_truths": ["Author One", "A. One"],
            "reasoning_type": "knowledge",
            "length_spec": "a few words",
            "answer": "Author One",
        }}
        factory = _make_exploding_judge_factory()
        qf_scores = run_panel(
            "test-judge", answers, factory, reliability={}, seed=17
        )
        assert qf_scores["x"]["judge"] == "identity"
        assert all(s == 1 for s in qf_scores["x"]["scores"])

    def test_normalize_for_identity(self):
        assert _normalize_for_identity("Author One") == "author one"
        assert _normalize_for_identity("Author One.") == "author one"
        assert _normalize_for_identity("AUTHOR ONE!") == "author one"
        assert _normalize_for_identity("") == ""
        assert _normalize_for_identity(None) == ""


# ---------------------------------------------------------------------------
# Distractor auto-fail (the inverse short-circuit)
# ---------------------------------------------------------------------------

class TestDistractorAutoFail:
    """A verbatim match to a probability-0 distractor of penalty class
    "question" or "both" is an automatic zero, with no judge call. Matches to
    "context"-class distractors (anachronistic_*) must still be judged --
    the pass/fail path does not measure period fidelity."""

    BASE = {
        "metadata_frame": "This is context one.",
        "main_question": "Who wrote it?",
        "ground_truths": ["Author One"],
        "reasoning_type": "knowledge",
    }

    def test_distractor_match_skips_the_judge(self):
        factory = _make_exploding_judge_factory()
        qf = run_panel("test-judge", {"1": {**self.BASE, "answer": "Author Two"}},
                       factory, reliability={}, seed=17,
                       autofail_strings={"1": ["Author Two"]})
        assert qf["1"]["judge"] == "identity"
        assert qf["1"]["auto_verdict"] == "distractor_identity"
        assert all(s == 0 for s in qf["1"]["scores"])
        assert all(j == "loss" for j in qf["1"]["judgments"])
        assert qf["1"]["r_q"] == 0.999

    def test_distractor_match_is_normalization_insensitive(self):
        factory = _make_exploding_judge_factory()
        qf = run_panel("test-judge", {"1": {**self.BASE, "answer": "  author two!  "}},
                       factory, reliability={}, seed=17,
                       autofail_strings={"1": ["Author Two"]})
        assert qf["1"]["auto_verdict"] == "distractor_identity"

    def test_unlisted_distractor_reaches_the_judge(self):
        """The negative control: a context-class distractor is not in
        autofail_strings, so it must be judged normally."""
        factory = _make_stub_judge_factory("C")
        qf = run_panel("test-judge",
                       {"1": {**self.BASE, "answer": "An anachronistic answer"}},
                       factory, reliability={}, seed=17,
                       autofail_strings={"1": ["Author Two"]})
        assert qf["1"]["judge"] == "test-judge"
        assert "auto_verdict" not in qf["1"]
        assert all(s == 1 for s in qf["1"]["scores"])

    def test_ground_truth_wins_over_a_distractor_match(self):
        factory = _make_exploding_judge_factory()
        qf = run_panel("test-judge", {"1": {**self.BASE, "answer": "Author One"}},
                       factory, reliability={}, seed=17,
                       autofail_strings={"1": ["Author One"]})
        assert qf["1"]["auto_verdict"] == "gt_identity"
        assert all(s == 1 for s in qf["1"]["scores"])

    def test_empty_answer_does_not_auto_fail(self):
        factory = _make_stub_judge_factory("A")
        qf = run_panel("test-judge", {"1": {**self.BASE, "answer": ""}},
                       factory, reliability={}, seed=17,
                       autofail_strings={"1": [""]})
        assert qf["1"]["judge"] == "test-judge"
        assert "auto_verdict" not in qf["1"]

    def test_omitting_autofail_strings_preserves_old_behavior(self):
        factory = _make_stub_judge_factory("C")
        qf = run_panel("test-judge", {"1": {**self.BASE, "answer": "Author Two"}},
                       factory, reliability={}, seed=17)
        assert qf["1"]["judge"] == "test-judge"
        assert "auto_verdict" not in qf["1"]

    def test_autofail_entry_shape_matches_a_judged_one(self):
        """v_hat downstream is mean(scores) and n_v is len(scores), so the
        fabricated plan must have the same length as a real one."""
        judged = run_panel("test-judge", {"1": {**self.BASE, "answer": "Other"}},
                           _make_stub_judge_factory("A"), reliability={}, seed=17)
        auto = run_panel("test-judge", {"1": {**self.BASE, "answer": "Author Two"}},
                         _make_exploding_judge_factory(), reliability={}, seed=17,
                         autofail_strings={"1": ["Author Two"]})
        assert len(auto["1"]["scores"]) == len(judged["1"]["scores"])
        assert set(auto["1"]) >= set(judged["1"])

    def test_multi_ground_truth_question_still_fabricates_a_full_plan(self):
        entry = {**self.BASE, "ground_truths": ["A", "B", "C", "D"],
                 "answer": "Author Two"}
        qf = run_panel("test-judge", {"1": entry}, _make_exploding_judge_factory(),
                       reliability={}, seed=17, autofail_strings={"1": ["Author Two"]})
        # Even #GTs -> one doubled -> odd total, same rule as the judged path.
        assert len(qf["1"]["scores"]) == 5
        assert all(s == 0 for s in qf["1"]["scores"])
