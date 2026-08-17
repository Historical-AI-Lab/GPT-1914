"""bt/validate.py — leave-one-out validation, ROC/AUC, and bias stats.

For each question with 2+ ground truths, every answer option can be
scored by LOO tau: remove it from the anchor set, refit anchors without
it, then score it exactly as a production candidate would be scored.
Across questions this yields (mostly) GT and distractor tau values from
which alpha(t) (distractor pass rate) and beta(t) (GT fail rate) are
swept to build an ROC curve and AUC.

The reduced anchor fit reuses the ALREADY-COLLECTED anchor counts
restricted to pairs that do not involve the held-out item -- no new
anchor judge calls are needed.  Only held-out-vs-pool comparisons are
new calls, and their prompts differ from the anchor-phase prompts
because the exemplar set excludes the held-out item.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .design import Item, build_candidate_design, select_reference_gt
from .fit import AnchorFit, fit_anchor_model
from .tau import CandidateScore, score_candidate


@dataclass
class LooRecord:
    qid: str
    item_id: str
    kind: str                 # "ground_truth" | "distractor"
    reference_gt: str
    score: CandidateScore
    prob: float = 0.0         # benchmark answer_probability of the held-out item


def is_partial(record) -> bool:
    """True for a held-out distractor with 0 < answer_probability < 1.

    alpha and beta are defined over unambiguous positives and negatives.
    An answer human judges scored 0.25 is neither, so it is excluded from
    the ROC sweep and the AUC — it still contributes a Delta to
    calibration, where its fractional label is the whole point.
    """
    return getattr(record, "kind", None) == "distractor" and 0.0 < getattr(record, "prob", 0.0) < 1.0


def dedupe_judgments(log_records: list[dict]) -> list[dict]:
    """Collapse a judgment log to one row per planned comparison, last wins.

    `artifacts.append_jsonl` appends, so re-running a phase (very likely
    while shaking the pipeline down) leaves duplicate rows in
    bt_judgments_{tag}.jsonl.  Reconstructing binomial counts from that
    log would then double-count every repeated comparison, and bias_stats
    would over-weight it.  Deduping at read time keeps the append-only
    log honest without rewriting it.
    """
    by_key: dict[tuple, dict] = {}
    for rec in log_records:
        key = (rec.get("qid"), rec.get("phase"), rec.get("first"),
               rec.get("second"), rec.get("repeat"))
        by_key[key] = rec
    return list(by_key.values())


def restrict_counts(counts: dict, exclude_id: str) -> dict:
    """Drop every ordered-pair count that involves `exclude_id`."""
    return {pair: v for pair, v in counts.items() if exclude_id not in pair}


def build_loo_designs(qid: str, items: list[Item], master_seed: int, repeats: int):
    """For every answer option, the (held_out_item, reduced_item_ids,
    candidate_design, withdrawn_gts) needed to run its LOO comparisons.

    A held-out ground truth needs another GT as reference; if the
    question has only one GT, that item is skipped (no LOO tau possible
    for it, per spec).
    """
    gt_ids = [it.item_id for it in items if it.kind == "ground_truth"]
    plans = []
    for held_out in items:
        reduced_items = [it for it in items if it.item_id != held_out.item_id]
        if held_out.kind == "ground_truth":
            if len(gt_ids) < 2:
                continue
            reference_gt = select_reference_gt(
                qid, [g for g in gt_ids if g != held_out.item_id], master_seed,
            )
        else:
            reference_gt = select_reference_gt(qid, gt_ids, master_seed)
        comparisons, withdrawn = build_candidate_design(
            qid, reduced_items, held_out, reference_gt, repeats, master_seed,
            phase=f"loo:{held_out.item_id}",
        )
        plans.append({
            "held_out": held_out, "reduced_items": reduced_items,
            "reference_gt": reference_gt, "comparisons": comparisons,
            "withdrawn": withdrawn,
        })
    return plans


def run_loo_for_question(qid: str, items: list[Item], anchor_counts: dict,
                         held_out_counts_by_item: dict[str, dict],
                         master_seed: int, *, prior_scale: float,
                         seed_offset: int = 0) -> list[LooRecord]:
    """Fit reduced anchors + score each held-out item as a candidate.

    held_out_counts_by_item[item_id] must hold the ordered-pair counts
    from that item's LOO comparisons (collected by the caller via
    bt.collect against build_loo_designs's comparison lists).
    """
    gt_ids = [it.item_id for it in items if it.kind == "ground_truth"]
    records: list[LooRecord] = []
    for held_out in items:
        if held_out.kind == "ground_truth" and len(gt_ids) < 2:
            continue
        reduced_items = [it for it in items if it.item_id != held_out.item_id]
        reduced_ids = [it.item_id for it in reduced_items]
        reduced_counts = restrict_counts(anchor_counts, held_out.item_id)

        anchor_seed = seed_offset  # deterministic; caller derives per-qid seeds upstream
        fit = fit_anchor_model(reduced_ids, reduced_counts,
                               prior_scale=prior_scale, seed=anchor_seed)

        # `pool_ref` = who the held-out item was compared against (must match
        # what build_loo_designs planned, or the counts will not line up).
        # `delta_refs` = what Delta is measured from: the mean of every GT
        # except the held-out one.  Their thetas come from the reduced anchor
        # fit and are already on its shared scale, so measuring against GTs
        # the item never faced is well defined and needs no extra calls.
        if held_out.kind == "ground_truth":
            eligible = [g for g in gt_ids if g != held_out.item_id]
            pool_ref = select_reference_gt(qid, eligible, master_seed)
            delta_refs = eligible
        else:
            pool_ref = select_reference_gt(qid, gt_ids, master_seed)
            delta_refs = gt_ids

        cand_counts = held_out_counts_by_item.get(held_out.item_id, {})
        if not cand_counts:
            continue
        score = score_candidate(fit, cand_counts, held_out.item_id, delta_refs,
                                prior_scale=prior_scale, seed=anchor_seed + 1)
        records.append(LooRecord(qid=qid, item_id=held_out.item_id,
                                 kind=held_out.kind, reference_gt=pool_ref,
                                 score=score, prob=held_out.prob))
    return records


def roc_from_loo(records: list[LooRecord]) -> dict:
    """Sweep tau thresholds; alpha = distractor pass rate, beta = GT fail rate.

    Partial-credit distractors are excluded from both classes (see
    `is_partial`); their count is reported as n_excluded_partial.
    """
    n_partial = sum(1 for r in records if is_partial(r))
    records = [r for r in records if not is_partial(r)]
    distractor_taus = [r.score.tau_mean for r in records if r.kind == "distractor"]
    gt_taus = [r.score.tau_mean for r in records if r.kind == "ground_truth"]
    if not distractor_taus or not gt_taus:
        raise ValueError("need at least one distractor and one held-out GT tau")

    d = np.array(distractor_taus)
    g = np.array(gt_taus)

    # Threshold grid from the observed tau values, not a uniform [0,1] grid.
    # tau = sigmoid(Delta), and under the near-complete separation this judge
    # produces, Delta is large and tau piles up against 0 and 1 -- so a uniform
    # grid spends most of its 201 points in empty space and resolves the
    # optimum coarsely.  Using the observed values (plus midpoints, plus the
    # endpoints) enumerates every achievable (alpha, beta) pair exactly, which
    # is the standard ROC construction and removes a grid artifact that made
    # r_q appear to fall when prior_scale rose even though AUC was unchanged.
    obs = np.unique(np.concatenate([d, g]))
    mids = (obs[:-1] + obs[1:]) / 2 if obs.size > 1 else np.array([])
    thresholds = np.unique(np.concatenate([[0.0], obs, mids, [1.0 + 1e-12]]))
    roc = []
    best_sum = np.inf
    best_ts = []
    for t in thresholds:
        alpha = float(np.mean(d >= t))     # distractor incorrectly passes
        beta = float(np.mean(g < t))       # GT incorrectly fails
        roc.append({"t": float(t), "alpha": alpha, "beta": beta})
        s = alpha + beta
        if s < best_sum - 1e-12:
            best_sum = s
            best_ts = [float(t)]
        elif s <= best_sum + 1e-12:
            best_ts.append(float(t))
    t_star = float(np.median(best_ts))
    alpha_star = float(np.mean(d >= t_star))
    beta_star = float(np.mean(g < t_star))

    # Mann-Whitney AUC: P(random GT tau > random distractor tau), ties count 0.5
    auc = _mann_whitney_auc(g, d)

    return {"roc": roc, "t_star": t_star, "alpha_at_t_star": alpha_star,
            "beta_at_t_star": beta_star, "auc": auc,
            "n_ground_truth": len(gt_taus), "n_distractor": len(distractor_taus),
            "n_excluded_partial": n_partial,
            "r_q": 1.0 - (alpha_star + beta_star) / 2.0}


def _mann_whitney_auc(positives: np.ndarray, negatives: np.ndarray) -> float:
    wins = 0.0
    for p in positives:
        wins += np.sum(p > negatives) + 0.5 * np.sum(p == negatives)
    return float(wins / (len(positives) * len(negatives)))


def bootstrap_auc(records_by_question: dict[str, list[LooRecord]], *,
                  n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Bootstrap AUC by resampling QUESTIONS (not answer options), per spec."""
    rng = np.random.default_rng(seed)
    qids = list(records_by_question)
    if not qids:
        raise ValueError("no questions to bootstrap")
    aucs = []
    for _ in range(n_boot):
        sample_qids = rng.choice(qids, size=len(qids), replace=True)
        pooled: list[LooRecord] = []
        for q in sample_qids:
            pooled.extend(r for r in records_by_question[q] if not is_partial(r))
        d = np.array([r.score.tau_mean for r in pooled if r.kind == "distractor"])
        g = np.array([r.score.tau_mean for r in pooled if r.kind == "ground_truth"])
        if len(d) == 0 or len(g) == 0:
            continue
        aucs.append(_mann_whitney_auc(g, d))
    if not aucs:
        raise ValueError("no bootstrap replicate had both classes represented")
    return (float(np.quantile(aucs, 0.025)), float(np.quantile(aucs, 0.975)))


def bias_stats(log_records: list[dict]) -> dict:
    """Pooled positional/length bias and abstention rate from a judgment log."""
    parsed = [r for r in log_records if r["parse_ok"]]
    n_first_total = len(parsed)
    n_first_chosen = sum(1 for r in parsed if r["choice"] == "A")

    length_eligible = [r for r in parsed if r["first_len"] != r["second_len"]]
    n_longer_total = len(length_eligible)
    n_longer_chosen = 0
    for r in length_eligible:
        longer_is_first = r["first_len"] > r["second_len"]
        chose_first = r["choice"] == "A"
        if longer_is_first == chose_first:
            n_longer_chosen += 1

    n_planned = len(log_records)
    n_dropped = sum(1 for r in log_records if r.get("dropped"))

    def wilson_ci(k, n):
        if n == 0:
            return (0.0, 1.0)
        p = k / n
        z = 1.959963985
        denom = 1 + z * z / n
        center = (p + z * z / (2 * n)) / denom
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
        return (max(0.0, center - half), min(1.0, center + half))

    return {
        "p_first": (n_first_chosen / n_first_total) if n_first_total else None,
        "n_first_total": n_first_total,
        "p_first_ci": wilson_ci(n_first_chosen, n_first_total),
        "p_longer": (n_longer_chosen / n_longer_total) if n_longer_total else None,
        "n_longer_total": n_longer_total,
        "p_longer_ci": wilson_ci(n_longer_chosen, n_longer_total),
        "abstention_rate": (n_dropped / n_planned) if n_planned else 0.0,
        "n_planned": n_planned, "n_dropped": n_dropped,
    }
