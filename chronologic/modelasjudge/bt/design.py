"""bt/design.py — comparison design tables for the Bradley-Terry context judge.

Items, ordered-pair comparison plans, reproducible reference-GT selection,
derived seeds, and the graph-connectivity assertion.

Judgments aggregate to binomial counts keyed by ORDERED pair
(first_id, second_id) -> (wins_first, n).  Repeats are never averaged.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass


class DesignError(ValueError):
    """Malformed question record or invalid design request."""


class DisconnectedGraphError(RuntimeError):
    """The comparison graph does not connect all items.

    With a proper prior a disconnected graph does not error at fit time —
    it silently returns components pinned by the prior rather than the
    data — so we refuse to fit instead.
    """


@dataclass(frozen=True)
class Item:
    item_id: str          # "gt0", "gt1", "d0", ... in benchmark array order; "cand" for candidates
    text: str
    kind: str             # "ground_truth" | "distractor" | "candidate"
    reject_reason: str = ""
    prob: float = 0.0     # the benchmark's answer_probability; 1.0 for GTs, 0.0 for
                          # plain distractors, fractional for partial-credit answers

    @property
    def is_partial(self) -> bool:
        """A distractor human judges scored as partly satisfactory.

        These stay `kind == "distractor"` — they are ordinary anchor items
        and ordinary opponents — but they render differently in the rubric
        and carry a soft label into calibration instead of a hard 0.
        """
        return self.kind == "distractor" and 0.0 < self.prob < 1.0


@dataclass(frozen=True)
class Comparison:
    """One ordered judge call: `first` is presented as Answer A."""
    qid: str
    phase: str            # "anchor" | "loo:<held_out_item_id>" | "candidate"
    first: str
    second: str
    repeat: int
    seed: int


def derive_seed(master_seed: int, *parts: str) -> int:
    """Stable 63-bit seed derived from a master seed and string parts.

    sha256-based so it is identical across processes, platforms, and runs.
    """
    payload = f"{master_seed}|" + "|".join(str(p) for p in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") >> 1


def items_from_question(rec: dict) -> list[Item]:
    """Build the answer-option Items for one benchmark question record.

    Validates parallel-array lengths and ground-truth/probability
    consistency.  Robust to 1-3+ ground truths.
    """
    strings = rec.get("answer_strings")
    types = rec.get("answer_types")
    probs = rec.get("answer_probabilities")
    if not strings or not types or not probs:
        raise DesignError("record missing answer_strings/answer_types/answer_probabilities")
    if not (len(strings) == len(types) == len(probs)):
        raise DesignError(
            f"parallel arrays differ in length: {len(strings)} strings, "
            f"{len(types)} types, {len(probs)} probabilities"
        )
    reasons = rec.get("reject_reasons") or [""] * len(strings)
    if len(reasons) != len(strings):
        raise DesignError(f"reject_reasons length {len(reasons)} != {len(strings)}")

    items: list[Item] = []
    n_gt = n_d = 0
    for text, atype, prob, reason in zip(strings, types, probs, reasons):
        if atype == "ground_truth":
            if prob != 1.0:
                raise DesignError(f"ground_truth answer with probability {prob}")
            items.append(Item(f"gt{n_gt}", text, "ground_truth", "", 1.0))
            n_gt += 1
        else:
            if prob == 1.0:
                raise DesignError(f"answer_type {atype!r} with probability 1.0")
            if not 0.0 <= prob < 1.0:
                raise DesignError(f"answer probability {prob} outside [0, 1)")
            items.append(Item(f"d{n_d}", text, "distractor", reason or "", float(prob)))
            n_d += 1
    if n_gt < 1:
        raise DesignError("question has no ground_truth answer")
    if len(items) < 2:
        raise DesignError("question has fewer than two answer options")
    return items


def build_anchor_design(qid: str, items: list[Item], repeats: int,
                        master_seed: int) -> list[Comparison]:
    """Every unordered pair of items, both orderings, `repeats` times each order."""
    comparisons = []
    for a_pos in range(len(items)):
        for b_pos in range(a_pos + 1, len(items)):
            a, b = items[a_pos].item_id, items[b_pos].item_id
            for first, second in ((a, b), (b, a)):
                for rep in range(repeats):
                    comparisons.append(Comparison(
                        qid=qid, phase="anchor", first=first, second=second,
                        repeat=rep,
                        seed=derive_seed(master_seed, qid, "anchor", first, second, str(rep)),
                    ))
    return comparisons


def select_reference_gt(qid: str, gt_ids: list[str], master_seed: int,
                        exclude: str | None = None) -> str:
    """Reproducibly select the single reference GT for tau comparisons.

    The base selection depends only on (master_seed, qid), so every
    process and phase agrees on it.  `exclude` is used when the scored
    item is itself a GT (LOO): if the base selection is the excluded
    item, a second derived seed picks among the remaining GTs.
    """
    eligible = sorted(set(gt_ids))
    if not eligible:
        raise DesignError(f"question {qid}: no ground truths to select from")
    rng = random.Random(derive_seed(master_seed, qid, "refgt"))
    choice = rng.choice(eligible)
    if exclude is not None and choice == exclude:
        remaining = [g for g in eligible if g != exclude]
        if not remaining:
            raise DesignError(
                f"question {qid}: no reference GT remains after excluding {exclude}"
            )
        rng2 = random.Random(derive_seed(master_seed, qid, "refgt", "excl", exclude))
        choice = rng2.choice(remaining)
    return choice


def build_candidate_design(qid: str, items: list[Item], candidate: Item,
                           reference_gt: str, repeats: int, master_seed: int,
                           phase: str = "candidate",
                           ) -> tuple[list[Comparison], list[str]]:
    """Design for scoring one candidate against the anchor pool.

    Pool = the reference GT plus all distractors; non-reference GTs are
    withdrawn from both the pool and (by the caller, via the returned
    list) the exemplar block.  Both orderings, `repeats` each.

    Note the division of labour with bt.tau.score_candidate: this decides
    which anchors the candidate is *compared against*; that decides which
    anchors Delta is *measured from*.  They are independent.  Delta is now
    taken against the mean of every ground truth -- their theta values come
    from the stored anchor draws and are already on the question's shared
    scale, so no comparison against a withdrawn GT is needed to use it.
    Keeping the withdrawal preserves the "no harder opponents" property and
    costs nothing.
    """
    pool = [it.item_id for it in items
            if it.kind == "distractor" or it.item_id == reference_gt]
    withdrawn = [it.item_id for it in items
                 if it.kind == "ground_truth" and it.item_id != reference_gt]
    if candidate.item_id in {it.item_id for it in items}:
        raise DesignError(
            f"candidate id {candidate.item_id!r} collides with an anchor item"
        )
    comparisons = []
    for opp in pool:
        for first, second in ((candidate.item_id, opp), (opp, candidate.item_id)):
            for rep in range(repeats):
                comparisons.append(Comparison(
                    qid=qid, phase=phase, first=first, second=second,
                    repeat=rep,
                    seed=derive_seed(master_seed, qid, phase, first, second, str(rep)),
                ))
    return comparisons, withdrawn


def assert_connected(item_ids: list[str],
                     counts: dict[tuple[str, str], tuple[int, int]]) -> None:
    """Raise DisconnectedGraphError unless observed comparisons (n > 0)
    connect every item in `item_ids`."""
    parent = {i: i for i in item_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), (_w, n) in counts.items():
        if n > 0 and a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    components: dict[str, list[str]] = {}
    for i in item_ids:
        components.setdefault(find(i), []).append(i)
    if len(components) > 1:
        raise DisconnectedGraphError(
            "comparison graph is disconnected; components: "
            + "; ".join(",".join(sorted(c)) for c in components.values())
        )
