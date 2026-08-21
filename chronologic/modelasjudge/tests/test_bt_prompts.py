"""test_bt_prompts.py — Tests for bt/prompts.py and the collect drop-balance
invariant in bt/collect.py.

Run with:
    pytest modelasjudge/tests/test_bt_prompts.py -v
"""

import sys
from itertools import combinations
from pathlib import Path

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from bt.collect import run_comparisons
from bt.design import Item, build_anchor_design, build_candidate_design
from bt.prompts import build_bt_prompt, build_exemplar_block, parse_bt_response


def make_question_items(n_gt=2, n_d=5):
    items = []
    for i in range(n_gt):
        items.append(Item(f"gt{i}", f"ground truth text {i}", "ground_truth", ""))
    for i in range(n_d):
        items.append(Item(f"d{i}", f"distractor text {i}", "distractor", f"reason {i}"))
    return items


class TestExemplarBlock:
    def test_compared_items_never_appear(self):
        items = make_question_items(2, 5)
        ids = [it.item_id for it in items]
        for a, b in combinations(ids, 2):
            block = build_exemplar_block(items, {a, b}, set(), "exemplars")
            assert f'"{next(it.text for it in items if it.item_id == a)}"' not in block
            assert f'"{next(it.text for it in items if it.item_id == b)}"' not in block

    def test_withdrawn_gt_excluded_in_candidate_phase(self):
        items = make_question_items(2, 3)
        block = build_exemplar_block(items, {"cand", "gt0"}, {"gt1"}, "exemplars")
        assert items[1].text not in block  # gt1 withdrawn
        assert items[2].text in block      # d0 still present

    def test_exemplar_order_fixed_across_pairs(self):
        items = make_question_items(2, 3)
        block_a = build_exemplar_block(items, {"gt0", "d0"}, set(), "exemplars")
        block_b = build_exemplar_block(items, {"gt0", "d1"}, set(), "exemplars")
        # Common exemplars (all except the two compared each time) must appear
        # in the same relative order in both blocks.
        common_ids = ["gt1", "d2"]
        positions_a = [block_a.index(items[[i.item_id for i in items].index(cid)].text)
                       if False else block_a.find(next(it.text for it in items if it.item_id == cid))
                       for cid in common_ids]
        positions_b = [block_b.find(next(it.text for it in items if it.item_id == cid))
                       for cid in common_ids]
        assert positions_a == sorted(positions_a)
        assert positions_b == sorted(positions_b)

    def test_exemplar_count_formula(self):
        items = make_question_items(2, 5)  # 7 total
        # anchor phase: two compared removed, nothing withdrawn -> 5 exemplars
        anchor_block = build_exemplar_block(items, {"gt0", "d0"}, set(), "exemplars")
        # production phase g=2: candidate+reference compared, one GT withdrawn -> 5 exemplars
        cand_block = build_exemplar_block(items, {"cand", "gt0"}, {"gt1"}, "exemplars")
        n_anchor = anchor_block.count("example of context fit")
        n_cand = cand_block.count("example of context fit")
        assert n_anchor == n_cand == 5


class TestExemplarHeaders:
    """Header text and rationale framing.

    "ACCEPTABLE example" is a substring of both "UNACCEPTABLE example" and
    "PARTLY ACCEPTABLE example", so every assertion here anchors on a full
    header line rather than a bare `in` check.
    """

    def test_three_headers(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "plain distractor text", "distractor", "gives away its later origin", 0.0),
            Item("d1", "near-miss text", "distractor", "is largely in keeping with the period", 0.25),
            Item("d2", "compared, excluded", "distractor", "whatever", 0.0),
        ]
        block = build_exemplar_block(items, {"d2"}, set(), "exemplars")
        lines = block.splitlines()
        assert "ACCEPTABLE example of context fit:" in lines
        assert "UNACCEPTABLE example of context fit:" in lines
        assert "PARTLY ACCEPTABLE example of context fit:" in lines

    def test_partial_item_gets_partly_acceptable_header(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "near-miss text", "distractor", "is largely in keeping", 0.25),
        ]
        block = build_exemplar_block(items, {"gt0"}, set(), "exemplars")
        assert block.startswith("PARTLY ACCEPTABLE example of context fit:")

    def test_zero_probability_distractor_stays_unacceptable(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "bad text", "distractor", "gives away its later origin", 0.0),
        ]
        block = build_exemplar_block(items, {"gt0"}, set(), "exemplars")
        assert block.startswith("UNACCEPTABLE example of context fit:")

    def test_rationale_framed_as_this_answer(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "bad text", "distractor", "gives away its later origin", 0.0),
        ]
        block = build_exemplar_block(items, {"gt0"}, set(), "exemplars")
        assert "This answer gives away its later origin" in block
        assert "Why it fails" not in block

    def test_ground_truth_carries_no_rationale(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "bad text", "distractor", "gives away its later origin", 0.0),
        ]
        block = build_exemplar_block(items, {"d0"}, set(), "exemplars")
        assert "This answer" not in block

    def test_missing_rationale_omits_the_line(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "bad text", "distractor", "", 0.0),
        ]
        block = build_exemplar_block(items, {"gt0"}, set(), "exemplars")
        assert block == 'UNACCEPTABLE example of context fit:\n"bad text"'


class TestPromptStructure:
    def test_invariant_block_precedes_answers(self):
        items = make_question_items(2, 3)
        block = build_exemplar_block(items, {"gt0", "d0"}, set(), "exemplars")
        system, user = build_bt_prompt("A 19th c. medical periodical", "Describe X.",
                                       block, "answer one text", "answer two text")
        assert user.index("RUBRIC") < user.index("ANSWER A")
        assert user.index("ANSWER A") < user.index("ANSWER B")
        assert "answer one text" in user
        assert "answer two text" in user


class TestParseBtResponse:
    def test_clean_json(self):
        assert parse_bt_response('{"context fit": "A"}') == "A"
        assert parse_bt_response('{"context fit": "B"}') == "B"

    def test_fenced_json(self):
        assert parse_bt_response('```json\n{"context fit": "A"}\n```') == "A"

    def test_prose_preamble(self):
        raw = 'Let me think about this. My answer is: {"context fit": "B"}'
        assert parse_bt_response(raw) == "B"

    def test_bare_letter(self):
        assert parse_bt_response("A") == "A"
        assert parse_bt_response(" b ") == "B"

    def test_refusal_returns_none(self):
        assert parse_bt_response("I cannot make this determination.") is None

    def test_tie_declaration_returns_none(self):
        assert parse_bt_response('{"context fit": "tie"}') is None
        assert parse_bt_response('{"context fit": "C"}') is None
        assert parse_bt_response("Both answers are equally good.") is None

    def test_truncated_json_returns_none(self):
        assert parse_bt_response('{"context fit": "A"') is None

    def test_empty_returns_none(self):
        assert parse_bt_response("") is None
        assert parse_bt_response(None) is None

    def test_lowercase_key_and_underscore_tolerant(self):
        assert parse_bt_response('{"context_fit": "A"}') == "A"


class TestCollectDropBalance:
    def test_unparseable_after_retries_drops_both_orderings(self):
        items = {it.item_id: it for it in make_question_items(1, 1)}
        comps = build_anchor_design("q1", list(items.values()), repeats=1, master_seed=1)
        assert len(comps) == 2  # one pair, both orders

        def prompt_builder(comp):
            return ("sys", f"{comp.first} vs {comp.second}")

        # The AB call always parses "A"; the BA call always fails.
        def judge_call(comp, system, user):
            if comp.first < comp.second:
                return '{"context fit": "A"}'
            return "I refuse to answer."

        result = run_comparisons(comps, items, prompt_builder, judge_call,
                                 cache=None, max_retries=1)
        assert result.counts == {}
        assert len(result.dropped_groups) == 1
        assert result.completed_calls == 0

    def test_retracts_already_parsed_partner(self):
        items = {it.item_id: it for it in make_question_items(1, 1)}
        comps = build_anchor_design("q1", list(items.values()), repeats=1, master_seed=1)
        order = []

        def prompt_builder(comp):
            return ("sys", f"{comp.first} vs {comp.second}")

        def judge_call(comp, system, user):
            order.append(comp)
            # First-encountered call succeeds, the partner fails.
            if len(order) == 1:
                return '{"context fit": "A"}'
            return "unparseable"

        result = run_comparisons(comps, items, prompt_builder, judge_call,
                                 cache=None, max_retries=0)
        assert result.counts == {}
        assert result.completed_calls == 0
        assert len(result.dropped_groups) == 1

    def test_balanced_pair_survives(self):
        items = {it.item_id: it for it in make_question_items(1, 1)}
        comps = build_anchor_design("q1", list(items.values()), repeats=1, master_seed=1)

        def prompt_builder(comp):
            return ("sys", f"{comp.first} vs {comp.second}")

        def judge_call(comp, system, user):
            return '{"context fit": "A"}'

        result = run_comparisons(comps, items, prompt_builder, judge_call,
                                 cache=None, max_retries=0)
        assert len(result.dropped_groups) == 0
        assert result.completed_calls == 2
        assert sum(n for _w, n in result.counts.values()) == 2

    def test_abstention_rate_reflects_drops(self):
        items = {it.item_id: it for it in make_question_items(2, 2)}
        cand = Item("cand", "candidate text", "candidate")
        comps, _ = build_candidate_design("q1", list(items.values()), cand,
                                          reference_gt="gt0", repeats=1, master_seed=1)
        items["cand"] = cand

        def prompt_builder(comp):
            return ("sys", f"{comp.first} vs {comp.second}")

        def judge_call(comp, system, user):
            return "garbage"

        result = run_comparisons(comps, items, prompt_builder, judge_call,
                                 cache=None, max_retries=0)
        assert result.abstention_rate == 1.0


class TestRepeatsAreNotServedFromCache:
    """--repeats N must produce N independent judge calls per ordered pair.

    The prompt for repeat 1 is byte-identical to repeat 0, so a cache keyed
    only on prompt text would serve one call back N times: the binomial n
    would grow without a new observation, understating the standard error
    and overstating separation.
    """

    def test_repeat_index_changes_the_cache_key(self):
        from bt.cache import PromptCache
        k0 = PromptCache.key("m", "medium", 0, "sys", "user", 0)
        k1 = PromptCache.key("m", "medium", 0, "sys", "user", 1)
        assert k0 != k1

    def test_each_repeat_reaches_the_judge(self, tmp_path):
        from bt.cache import PromptCache
        items = {it.item_id: it for it in make_question_items(1, 1)}
        comps = build_anchor_design("q1", list(items.values()), repeats=3, master_seed=1)
        assert len(comps) == 6  # one pair, two orderings, three repeats

        calls = []

        def prompt_builder(comp):
            return ("sys", f"{comp.first} vs {comp.second}")

        def judge_call(comp, system, user):
            calls.append((comp.first, comp.second, comp.repeat))
            return '{"context fit": "A"}'

        cache = PromptCache(tmp_path / "cache")
        result = run_comparisons(comps, items, prompt_builder, judge_call,
                                 cache=cache, max_retries=0)
        assert len(calls) == 6
        assert result.cache_hits == 0
        assert sum(n for _w, n in result.counts.values()) == 6

    def test_rerun_still_hits_cache(self, tmp_path):
        """The fix must not defeat resuming an interrupted run."""
        from bt.cache import PromptCache
        items = {it.item_id: it for it in make_question_items(1, 1)}
        comps = build_anchor_design("q1", list(items.values()), repeats=2, master_seed=1)
        calls = []

        def prompt_builder(comp):
            return ("sys", f"{comp.first} vs {comp.second}")

        def judge_call(comp, system, user):
            calls.append(comp)
            return '{"context fit": "A"}'

        cache = PromptCache(tmp_path / "cache")
        run_comparisons(comps, items, prompt_builder, judge_call, cache=cache, max_retries=0)
        n_first = len(calls)
        result = run_comparisons(comps, items, prompt_builder, judge_call,
                                 cache=cache, max_retries=0)
        assert len(calls) == n_first        # no new billed calls
        assert result.cache_hits == 4


class TestMaskSelfOverlap:
    """Rationales quote the answers they describe; in rationales mode that
    would let the judge match a rejection to an answer in front of it."""

    def test_quoted_span_present_in_the_answer_is_masked(self):
        from bt.prompts import mask_self_overlap
        out = mask_self_overlap(
            'adopts a style significantly archaic for 1872, e.g. "a climate '
            'eminently mild and salubrious" adjective inversion',
            "a climate eminently mild and salubrious, distant from London")
        assert "[masked phrase]" in out
        assert "eminently mild" not in out
        assert out.startswith("adopts a style significantly archaic for 1872")
        assert out.endswith("adjective inversion")

    def test_two_word_quote_is_enough_when_quoted(self):
        from bt.prompts import mask_self_overlap
        out = mask_self_overlap('quibbles only at "amber light" here',
                                "it goes in amber light")
        assert out == 'quibbles only at "[masked phrase]" here'

    def test_quoted_span_absent_from_the_answer_survives(self):
        from bt.prompts import mask_self_overlap
        r = 'invents a phrase, "the Jurassic Coast", unknown before the 21c'
        assert mask_self_overlap(r, "a wholly different answer text") == r

    def test_stopword_run_is_not_masked(self):
        from bt.prompts import mask_self_overlap
        r = "is odd in the way that of the and"
        assert mask_self_overlap(r, "of the and that way") == r

    def test_no_overlap_returns_input_unchanged(self):
        from bt.prompts import mask_self_overlap
        r = "is too modern in its framing"
        assert mask_self_overlap(r, "nothing whatsoever in common") == r

    def test_protects_every_supplied_text_not_just_the_first(self):
        """Cross-quoting: a rationale may quote an answer it does not describe."""
        from bt.prompts import mask_self_overlap
        r = "technically fits the theme of the old oak wood well enough"
        assert "[masked phrase]" in mask_self_overlap(r, "unrelated", "of the old oak wood")

    def test_empty_inputs_are_safe(self):
        from bt.prompts import mask_self_overlap
        assert mask_self_overlap("", "abc") == ""
        assert mask_self_overlap("abc", "") == "abc"
        assert mask_self_overlap("abc") == "abc"


class TestRationalesMode:
    def _items(self):
        return [
            Item("gt0", "authentic period prose one", "ground_truth", "", 1.0),
            Item("gt1", "authentic period prose two", "ground_truth", "", 1.0),
            Item("d0", "a distractor about the old oak wood", "distractor",
                 'quotes "the old oak wood" and is too modern', 0.0),
            Item("d1", "another distractor entirely", "distractor",
                 "is in the wrong metre", 0.0),
            Item("d2", "a near miss", "distractor", "is largely in keeping", 0.5),
        ]

    def test_no_distractor_text_appears(self):
        block = build_exemplar_block(self._items(), {"gt0", "d0"}, set(), "rationales")
        for text in ("a distractor about the old oak wood",
                     "another distractor entirely", "a near miss"):
            assert text not in block

    def test_one_line_per_distractor_including_the_compared_one(self):
        items = self._items()
        for a, b in combinations([i.item_id for i in items], 2):
            block = build_exemplar_block(items, {a, b}, set(), "rationales")
            assert block.count("\n- ") == 3, f"pair {a},{b} changed the line count"

    def test_ground_truth_texts_kept_except_the_compared_one(self):
        block = build_exemplar_block(self._items(), {"gt0", "d0"}, set(), "rationales")
        assert "authentic period prose two" in block
        assert "authentic period prose one" not in block

    def test_withdrawn_ground_truth_is_dropped(self):
        block = build_exemplar_block(self._items(), {"cand", "gt0"}, {"gt1"}, "rationales")
        assert "authentic period prose two" not in block

    def test_acceptability_tiers_survive_the_loss_of_texts(self):
        block = build_exemplar_block(self._items(), {"gt0", "gt1"}, set(), "rationales")
        assert "- PARTLY ACCEPTABLE. This answer is largely in keeping" in block
        assert "- UNACCEPTABLE. This answer is in the wrong metre" in block

    def test_masks_only_where_a_compared_answer_is_quoted(self):
        items = self._items()
        # d0 compared: its own quote of "the old oak wood" must go
        masked = build_exemplar_block(items, {"d0", "d1"}, set(), "rationales")
        assert "the old oak wood" not in masked
        assert "[masked phrase]" in masked
        # d0 not compared: nothing quotes gt0 or gt1, so no mask at all
        clean = build_exemplar_block(items, {"gt0", "gt1"}, set(), "rationales")
        assert "[masked phrase]" not in clean
        assert 'quotes "the old oak wood" and is too modern' in clean

    def test_unknown_mode_raises(self):
        import pytest
        with pytest.raises(ValueError):
            build_exemplar_block(self._items(), {"gt0"}, set(), "nonsense")


class TestExemplarsModeUnchanged:
    """The default mode must be byte-identical to the pre-rationales rendering,
    so existing artifacts and the recovery suite stay comparable."""

    def test_exact_rendering(self):
        items = [
            Item("gt0", "ground truth text", "ground_truth", "", 1.0),
            Item("d0", "bad text", "distractor", "gives away its later origin", 0.0),
            Item("d1", "near text", "distractor", "is largely in keeping", 0.25),
        ]
        assert build_exemplar_block(items, {"gt0"}, set(), "exemplars") == (
            'UNACCEPTABLE example of context fit:\n"bad text"\n'
            'This answer gives away its later origin\n\n'
            'PARTLY ACCEPTABLE example of context fit:\n"near text"\n'
            'This answer is largely in keeping'
        )

    def test_the_default_mode_is_rationales(self):
        """The preferred mode is what a caller gets without asking. That is a
        separate question from which mode owns the unsuffixed artifact tag —
        "exemplars" keeps the bare tag so its existing fit is not orphaned."""
        from bt import artifacts
        from bt.prompts import DEFAULT_PROMPT_MODE
        assert DEFAULT_PROMPT_MODE == "rationales"
        assert artifacts.UNSUFFIXED_PROMPT_MODE == "exemplars"
        items = [
            Item("gt0", "gt", "ground_truth", "", 1.0),
            Item("d0", "d", "distractor", "fails", 0.0),
        ]
        assert (build_exemplar_block(items, {"gt0"}, set())
                == build_exemplar_block(items, {"gt0"}, set(), "rationales"))
        assert (build_exemplar_block(items, {"gt0"}, set())
                != build_exemplar_block(items, {"gt0"}, set(), "exemplars"))

    def test_system_prompt_differs_by_mode(self):
        from bt.prompts import system_prompt_for
        ex = system_prompt_for("exemplars")
        ra = system_prompt_for("rationales")
        # the exemplars guarantee is false in rationales mode and must not survive
        assert "never among them" in ex
        assert "never among them" not in ra
        # and nothing replaces it with a disclosure either way
        assert "may be among" not in ra
