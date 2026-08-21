"""test_bt_design.py — Tests for bt/design.py.

Run with:
    pytest modelasjudge/tests/test_bt_design.py -v
"""

import subprocess
import sys
from itertools import combinations
from pathlib import Path

import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from bt.design import (
    DesignError,
    DisconnectedGraphError,
    Item,
    assert_connected,
    build_anchor_design,
    build_candidate_design,
    derive_seed,
    items_from_question,
    select_reference_gt,
)


def make_items(n_gt=2, n_d=3):
    items = []
    for i in range(n_gt):
        items.append(Item(f"gt{i}", f"gt text {i}", "ground_truth", ""))
    for i in range(n_d):
        items.append(Item(f"d{i}", f"distractor text {i}", "distractor", f"reason {i}"))
    return items


class TestItemsFromQuestion:
    def test_basic_two_gt(self):
        rec = {
            "answer_strings": ["a", "b", "c"],
            "answer_types": ["ground_truth", "ground_truth", "anachronistic_x"],
            "answer_probabilities": [1.0, 1.0, 0.0],
            "reject_reasons": ["", "", "too modern"],
        }
        items = items_from_question(rec)
        assert [it.item_id for it in items] == ["gt0", "gt1", "d0"]
        assert items[2].reject_reason == "too modern"

    def test_robust_to_three_gt(self):
        rec = {
            "answer_strings": ["a", "b", "c", "d"],
            "answer_types": ["ground_truth"] * 3 + ["manual"],
            "answer_probabilities": [1.0, 1.0, 1.0, 0.0],
        }
        items = items_from_question(rec)
        assert [it.item_id for it in items] == ["gt0", "gt1", "gt2", "d0"]

    def test_mismatched_lengths_raise(self):
        rec = {"answer_strings": ["a", "b"], "answer_types": ["ground_truth"],
               "answer_probabilities": [1.0, 0.0]}
        with pytest.raises(DesignError):
            items_from_question(rec)

    def test_no_ground_truth_raises(self):
        rec = {"answer_strings": ["a", "b"], "answer_types": ["manual", "manual"],
               "answer_probabilities": [0.0, 0.0]}
        with pytest.raises(DesignError):
            items_from_question(rec)

    def test_gt_prob_mismatch_raises(self):
        rec = {"answer_strings": ["a"], "answer_types": ["ground_truth"],
               "answer_probabilities": [0.5]}
        with pytest.raises(DesignError):
            items_from_question(rec)

    def test_probability_carried_onto_items(self):
        rec = {
            "answer_strings": ["a", "b", "c"],
            "answer_types": ["ground_truth", "anachronistic_x", "anachronistic_y"],
            "answer_probabilities": [1.0, 0.0, 0.25],
            "reject_reasons": ["", "too modern", "is largely in keeping"],
        }
        items = items_from_question(rec)
        assert [it.prob for it in items] == [1.0, 0.0, 0.25]

    def test_partial_credit_answer_is_still_a_distractor(self):
        """0 < p < 1 answers change only how they are labelled and
        calibrated; they remain ordinary anchor items and opponents."""
        rec = {
            "answer_strings": ["a", "b", "c"],
            "answer_types": ["ground_truth", "ground_truth", "anachronistic_y"],
            "answer_probabilities": [1.0, 1.0, 0.75],
            "reject_reasons": ["", "", "is basically a good fit"],
        }
        items = items_from_question(rec)
        partial = items[2]
        assert partial.item_id == "d0"
        assert partial.kind == "distractor"
        assert partial.is_partial
        assert not items[0].is_partial
        comps, withdrawn = build_candidate_design(
            "q1", items, Item("cand", "candidate", "candidate"),
            reference_gt="gt0", repeats=1, master_seed=1,
        )
        assert "d0" in {c.first for c in comps} | {c.second for c in comps}
        assert withdrawn == ["gt1"]     # a non-reference GT, withdrawn as usual

    def test_negative_probability_raises(self):
        rec = {"answer_strings": ["a", "b"], "answer_types": ["ground_truth", "x"],
               "answer_probabilities": [1.0, -0.5]}
        with pytest.raises(DesignError):
            items_from_question(rec)


class TestAnchorDesign:
    def test_every_unordered_pair_both_orders(self):
        items = make_items(2, 3)
        comps = build_anchor_design("q1", items, repeats=2, master_seed=42)
        ids = sorted(it.item_id for it in items)
        expected_pairs = set(combinations(ids, 2))
        seen = {}
        for c in comps:
            key = tuple(sorted((c.first, c.second)))
            seen.setdefault(key, {"fwd": 0, "bwd": 0})
            if (c.first, c.second) == tuple(sorted((c.first, c.second))):
                seen[key]["fwd"] += 1
            else:
                seen[key]["bwd"] += 1
        assert set(seen) == expected_pairs
        for key, counts in seen.items():
            assert counts["fwd"] == 2
            assert counts["bwd"] == 2

    def test_repeats_default_and_seeds_deterministic(self):
        items = make_items(2, 2)
        c1 = build_anchor_design("q1", items, repeats=1, master_seed=7)
        c2 = build_anchor_design("q1", items, repeats=1, master_seed=7)
        assert [c.seed for c in c1] == [c.seed for c in c2]


class TestReferenceGtSelection:
    def test_deterministic_same_process(self):
        gt_ids = ["gt0", "gt1", "gt2"]
        a = select_reference_gt("q1", gt_ids, master_seed=99)
        b = select_reference_gt("q1", gt_ids, master_seed=99)
        assert a == b
        assert a in gt_ids

    def test_deterministic_across_subprocess(self):
        code = (
            "import sys; sys.path.insert(0, %r); "
            "from bt.design import select_reference_gt; "
            "print(select_reference_gt('q1', ['gt0','gt1','gt2'], master_seed=99))"
        ) % str(MODELASJUDGE)
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
        in_process = select_reference_gt("q1", ["gt0", "gt1", "gt2"], master_seed=99)
        assert out.stdout.strip() == in_process

    def test_exclude_picks_another_gt(self):
        gt_ids = ["gt0", "gt1", "gt2"]
        base = select_reference_gt("q1", gt_ids, master_seed=5)
        excluded = select_reference_gt("q1", gt_ids, master_seed=5, exclude=base)
        assert excluded != base
        assert excluded in gt_ids

    def test_exclude_only_remaining_gt_raises(self):
        with pytest.raises(DesignError):
            select_reference_gt("q1", ["gt0"], master_seed=5, exclude="gt0")

    def test_no_eligible_gts_raises(self):
        with pytest.raises(DesignError):
            select_reference_gt("q1", [], master_seed=5)


class TestCandidateDesign:
    def test_pool_excludes_non_reference_gts(self):
        """The candidate faces one GT and every distractor, so a question
        with more GTs does not hand it more strong opponents."""
        items = make_items(2, 3)
        cand = Item("cand", "candidate text", "candidate")
        comps, withdrawn = build_candidate_design(
            "q1", items, cand, reference_gt="gt0", repeats=1, master_seed=1,
        )
        opponents = {c.first if c.first != "cand" else c.second for c in comps}
        assert opponents == {"gt0", "d0", "d1", "d2"}
        assert withdrawn == ["gt1"]

    def test_both_orders_and_repeats(self):
        items = make_items(1, 2)
        cand = Item("cand", "candidate text", "candidate")
        comps, _ = build_candidate_design(
            "q1", items, cand, reference_gt="gt0", repeats=2, master_seed=1,
        )
        # 3 opponents (gt0, d0, d1) x 2 orders x 2 repeats
        assert len(comps) == 3 * 2 * 2

    def test_three_gt_withdraws_two(self):
        items = make_items(3, 1)
        cand = Item("cand", "candidate text", "candidate")
        comps, withdrawn = build_candidate_design(
            "q1", items, cand, reference_gt="gt1", repeats=1, master_seed=1,
        )
        assert sorted(withdrawn) == ["gt0", "gt2"]
        opponents = {c.first if c.first != "cand" else c.second for c in comps}
        assert opponents == {"gt1", "d0"}

    def test_candidate_id_collision_raises(self):
        items = make_items(2, 2)
        cand = Item("gt0", "oops", "candidate")
        with pytest.raises(DesignError):
            build_candidate_design("q1", items, cand, reference_gt="gt0",
                                   repeats=1, master_seed=1)


class TestConnectivity:
    def test_connected_graph_passes(self):
        counts = {("gt0", "d0"): (1, 1), ("d0", "gt0"): (0, 1),
                  ("d0", "d1"): (1, 1), ("d1", "d0"): (0, 1)}
        assert_connected(["gt0", "d0", "d1"], counts)

    def test_disconnected_graph_raises(self):
        counts = {("gt0", "d0"): (1, 1), ("d0", "gt0"): (0, 1)}
        with pytest.raises(DisconnectedGraphError):
            assert_connected(["gt0", "d0", "d1", "d2"], counts)

    def test_dropped_pairs_zero_n_do_not_connect(self):
        counts = {("gt0", "d0"): (0, 0)}
        with pytest.raises(DisconnectedGraphError):
            assert_connected(["gt0", "d0"], counts)


class TestDeriveSeed:
    def test_deterministic_and_typed(self):
        s1 = derive_seed(42, "q1", "anchor", "gt0", "d0", "0")
        s2 = derive_seed(42, "q1", "anchor", "gt0", "d0", "0")
        assert s1 == s2
        assert isinstance(s1, int)

    def test_sensitive_to_each_part(self):
        base = derive_seed(42, "q1", "anchor", "gt0", "d0", "0")
        assert derive_seed(42, "q1", "anchor", "gt0", "d0", "1") != base
        assert derive_seed(42, "q2", "anchor", "gt0", "d0", "0") != base
        assert derive_seed(43, "q1", "anchor", "gt0", "d0", "0") != base


class TestPoolAndReferenceAreSeparateConcerns:
    """Who the candidate is COMPARED AGAINST and what Delta is MEASURED FROM
    are independent choices.  The reference-GT lottery injected a median 0.71
    Delta swing decided by a seed, so Delta moved to the mean of every GT --
    but their thetas come from the anchor fit and are already on the shared
    scale, so that needed no change to the pool and no new judge calls."""

    def test_pool_still_faces_only_the_reference_gt(self):
        items = make_items(n_gt=2, n_d=3)
        comps, withdrawn = build_candidate_design(
            "q1", items, Item("cand", "c", "candidate"), "gt0", 1, 1)
        opponents = ({c.first for c in comps} | {c.second for c in comps}) - {"cand"}
        assert opponents == {"gt0", "d0", "d1", "d2"}
        assert withdrawn == ["gt1"]

    def test_delta_can_reference_a_gt_never_faced(self):
        """gt1 is withdrawn from the pool yet still enters Delta."""
        from bt.fit import AnchorFit
        from bt.tau import score_candidate
        import numpy as np
        ids = ["gt0", "gt1", "d0"]
        draws = np.tile(np.array([[2.0, 0.0, -3.0]]), (200, 1))
        fit = AnchorFit(item_ids=ids, theta_draws=draws, prior_scale=1.0)
        counts = {("cand", "gt0"): (1, 2), ("gt0", "cand"): (1, 2),
                  ("cand", "d0"): (2, 2), ("d0", "cand"): (0, 2)}
        s = score_candidate(fit, counts, "cand", ["gt0", "gt1"], prior_scale=3.0, seed=1)
        assert s.reference_gt == "gt0,gt1"

    def test_every_opponent_is_compared_in_both_orderings(self):
        items = make_items(n_gt=2, n_d=3)
        comps, _ = build_candidate_design(
            "q1", items, Item("cand", "c", "candidate"), "gt0", 1, 1)
        assert len(comps) == 2 * 4
        for opp in ("gt0", "d0", "d1", "d2"):
            assert any(c.first == "cand" and c.second == opp for c in comps)
            assert any(c.first == opp and c.second == "cand" for c in comps)


class TestDeltaAgainstMeanOfGroundTruths:
    def _fit(self, thetas):
        from bt.fit import AnchorFit
        import numpy as np
        ids = list(thetas)
        draws = np.tile(np.array([[thetas[i] for i in ids]], dtype=float), (200, 1))
        return AnchorFit(item_ids=ids, theta_draws=draws, prior_scale=1.0)

    def test_mean_of_two_gts_is_used(self):
        from bt.tau import score_candidate
        fit = self._fit({"gt0": 2.0, "gt1": 0.0, "d0": -3.0})
        counts = {("cand", "d0"): (2, 2), ("d0", "cand"): (0, 2)}
        s = score_candidate(fit, counts, "cand", ["gt0", "gt1"], prior_scale=3.0, seed=1)
        one = score_candidate(fit, counts, "cand", ["gt0"], prior_scale=3.0, seed=1)
        # reference mean is 1.0, i.e. exactly 1.0 above the gt0-only reference
        assert abs((s.delta_mean - one.delta_mean) - 1.0) < 1e-9
        assert s.reference_gt == "gt0,gt1"

    def test_a_single_gt_behaves_as_before(self):
        from bt.tau import score_candidate
        fit = self._fit({"gt0": 1.0, "d0": -2.0})
        counts = {("cand", "d0"): (2, 2), ("d0", "cand"): (0, 2)}
        a = score_candidate(fit, counts, "cand", "gt0", prior_scale=3.0, seed=1)
        b = score_candidate(fit, counts, "cand", ["gt0"], prior_scale=3.0, seed=1)
        assert abs(a.delta_mean - b.delta_mean) < 1e-12

    def test_order_of_references_does_not_matter(self):
        from bt.tau import score_candidate
        fit = self._fit({"gt0": 2.0, "gt1": 0.0, "d0": -3.0})
        counts = {("cand", "d0"): (2, 2), ("d0", "cand"): (0, 2)}
        a = score_candidate(fit, counts, "cand", ["gt0", "gt1"], prior_scale=3.0, seed=1)
        b = score_candidate(fit, counts, "cand", ["gt1", "gt0"], prior_scale=3.0, seed=1)
        assert abs(a.delta_mean - b.delta_mean) < 1e-12

    def test_empty_reference_list_raises(self):
        from bt.tau import score_candidate
        import pytest
        fit = self._fit({"gt0": 1.0, "d0": -2.0})
        with pytest.raises(ValueError):
            score_candidate(fit, {("cand", "d0"): (2, 2)}, "cand", [],
                            prior_scale=3.0, seed=1)
