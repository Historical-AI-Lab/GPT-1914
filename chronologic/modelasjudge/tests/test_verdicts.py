"""test_verdicts.py — Tests for substantive/verdicts.py.

The asymmetry between the two paths is the point of most of these: a
"context"-class distractor match is an automatic fail on the partial-credit
path and NOT on the pass/fail path, because pass/fail does not measure
period fidelity.

Run with:
    pytest modelasjudge/tests/test_verdicts.py -v
"""

import sys
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.verdicts import (
    AUTOFAIL_CLASSES_PASSFAIL,
    auto_verdict,
    autofail_strings_partial,
    autofail_strings_passfail,
    ground_truth_strings,
    load_distractor_penalties,
    normalize_for_identity,
)

# answer_types chosen to span all three penalty classes.
PENALTIES = {
    "negation": "question",
    "same_book": "question",
    "manual": "both",
    "anachronistic_manual": "context",
    "other_book_1911": "context",
}

RECORD = {
    "answer_strings": [
        "The ground truth.",          # gt
        "A negated answer.",          # question   -> autofail both paths
        "A manual distractor.",       # both       -> autofail both paths
        "An anachronistic answer.",   # context    -> autofail partial only
        "A partly good answer.",      # question class but prob > 0
        "An unclassified answer.",    # type absent from the penalties table
    ],
    "answer_types": [
        "ground_truth", "negation", "manual",
        "anachronistic_manual", "same_book", "brand_new_type_2027",
    ],
    "answer_probabilities": [1.0, 0.0, 0.0, 0.0, 0.5, 0.0],
}


class TestNormalizeForIdentity:
    def test_lowercases(self):
        assert normalize_for_identity("Author One") == "author one"

    def test_strips_punctuation(self):
        assert normalize_for_identity("Author One.") == "author one"
        assert normalize_for_identity("AUTHOR ONE!") == "author one"

    def test_strips_surrounding_whitespace(self):
        assert normalize_for_identity("  Author One  ") == "author one"

    def test_none_and_empty(self):
        assert normalize_for_identity(None) == ""
        assert normalize_for_identity("") == ""

    def test_does_not_collapse_interior_whitespace(self):
        # Deliberately narrow: every widening turns a judged comparison into
        # an unjudged certainty.
        assert normalize_for_identity("a  b") != normalize_for_identity("a b")


class TestPenaltiesTable:
    def test_real_table_loads_and_classes_are_valid(self):
        penalties = load_distractor_penalties()
        assert penalties, "distractor_penalties.txt should not be empty"
        assert set(penalties.values()) <= {"question", "both", "context"}

    def test_known_types_have_the_expected_classes(self):
        penalties = load_distractor_penalties()
        assert penalties["negation"] == "question"
        assert penalties["same_book"] == "question"
        assert penalties["anachronistic_manual"] == "context"

    def test_context_is_not_an_autofail_class(self):
        assert "context" not in AUTOFAIL_CLASSES_PASSFAIL
        assert AUTOFAIL_CLASSES_PASSFAIL == {"question", "both"}


class TestAutofailStrings:
    def test_partial_takes_every_probability_zero_distractor(self):
        got = autofail_strings_partial(RECORD)
        assert got == ["A negated answer.", "A manual distractor.",
                       "An anachronistic answer.", "An unclassified answer."]

    def test_passfail_takes_only_question_and_both_classes(self):
        got = autofail_strings_passfail(RECORD, PENALTIES)
        assert got == ["A negated answer.", "A manual distractor."]

    def test_passfail_excludes_context_class(self):
        assert "An anachronistic answer." not in autofail_strings_passfail(RECORD, PENALTIES)

    def test_neither_path_takes_a_partial_credit_answer(self):
        assert "A partly good answer." not in autofail_strings_partial(RECORD)
        assert "A partly good answer." not in autofail_strings_passfail(RECORD, PENALTIES)

    def test_unknown_answer_type_is_not_an_autofail_on_passfail(self, capsys):
        got = autofail_strings_passfail(RECORD, PENALTIES)
        assert "An unclassified answer." not in got

    def test_ground_truth_is_never_an_autofail_string(self):
        assert "The ground truth." not in autofail_strings_partial(RECORD)
        assert "The ground truth." not in autofail_strings_passfail(RECORD, PENALTIES)

    def test_ground_truth_strings(self):
        assert ground_truth_strings(RECORD) == ["The ground truth."]

    def test_malformed_record_yields_nothing_rather_than_raising(self):
        bad = {"answer_strings": ["a", "b"], "answer_types": ["ground_truth"],
               "answer_probabilities": [1.0, 0.0]}
        assert autofail_strings_partial(bad) == []
        assert ground_truth_strings(bad) == []


class TestAutoVerdict:
    def setup_method(self):
        self.gts = ground_truth_strings(RECORD)
        self.pf = autofail_strings_passfail(RECORD, PENALTIES)
        self.pc = autofail_strings_partial(RECORD)

    def test_ground_truth_match_passes(self):
        assert auto_verdict("The ground truth.", self.gts, self.pf) == "pass"

    def test_ground_truth_match_is_normalization_insensitive(self):
        assert auto_verdict("the ground truth", self.gts, self.pf) == "pass"
        assert auto_verdict("  THE GROUND TRUTH!  ", self.gts, self.pf) == "pass"

    def test_question_class_distractor_fails_on_both_paths(self):
        assert auto_verdict("A negated answer.", self.gts, self.pf) == "fail"
        assert auto_verdict("A negated answer.", self.gts, self.pc) == "fail"

    def test_both_class_distractor_fails_on_both_paths(self):
        assert auto_verdict("A manual distractor.", self.gts, self.pf) == "fail"
        assert auto_verdict("A manual distractor.", self.gts, self.pc) == "fail"

    def test_context_class_distractor_fails_on_partial_only(self):
        # The asymmetry this module exists to encode.
        assert auto_verdict("An anachronistic answer.", self.gts, self.pf) is None
        assert auto_verdict("An anachronistic answer.", self.gts, self.pc) == "fail"

    def test_partial_credit_answer_is_never_automatic(self):
        assert auto_verdict("A partly good answer.", self.gts, self.pf) is None
        assert auto_verdict("A partly good answer.", self.gts, self.pc) is None

    def test_unmatched_answer_returns_none(self):
        assert auto_verdict("Something nobody wrote.", self.gts, self.pc) is None

    def test_empty_candidate_never_matches(self):
        assert auto_verdict("", self.gts, self.pc) is None
        assert auto_verdict("   ", self.gts, self.pc) is None
        assert auto_verdict(None, self.gts, self.pc) is None

    def test_empty_candidate_does_not_match_an_empty_option(self):
        assert auto_verdict("", [""], [""]) is None

    def test_ground_truth_wins_over_a_distractor_match(self, capsys):
        verdict = auto_verdict("Same text.", ["Same text."], ["Same text."], qnum="7")
        assert verdict == "pass"
        assert "question 7" in capsys.readouterr().out

    def test_missing_autofail_list_still_allows_a_pass(self):
        assert auto_verdict("The ground truth.", self.gts, None) == "pass"
        assert auto_verdict("A negated answer.", self.gts, None) is None
