"""bt/collect.py — run a comparison design through a judge and aggregate counts.

The judge is an injected callable `judge_call(comparison, system, user) -> str`
(raw model text).  Real judges wrap openrouter_client; tests and the
recovery machinery inject stubs.

Balance invariant: if a call is unparseable after all retries, the whole
(unordered pair, repeat) group — i.e. its AB/BA partner too — is dropped
from the counts, retracting an already-parsed partner if necessary.
Bias tallies (P(first chosen), P(longer chosen)) are computed over every
parsed call, including later-retracted ones, because they describe judge
behavior rather than the fitted data.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

from .cache import PromptCache
from .design import Comparison, Item
from .prompts import RETRY_SUFFIX, parse_bt_response


@dataclass
class CollectResult:
    counts: dict = field(default_factory=dict)   # (first, second) -> (wins_first, n)
    dropped_groups: list = field(default_factory=list)  # (qid, phase, id_a, id_b, repeat), a < b
    planned_calls: int = 0
    completed_calls: int = 0
    cache_hits: int = 0
    unparseable_calls: int = 0
    first_chosen: int = 0
    first_total: int = 0
    longer_chosen: int = 0
    longer_total: int = 0
    log_records: list = field(default_factory=list)

    @property
    def abstention_rate(self) -> float:
        return 0.0 if self.planned_calls == 0 else (
            (self.planned_calls - self.completed_calls) / self.planned_calls)


def run_comparisons(comparisons: list[Comparison],
                    items_by_id: dict[str, Item],
                    prompt_builder,
                    judge_call,
                    *,
                    cache: PromptCache | None = None,
                    judge_model: str = "",
                    judge_effort: str = "",
                    max_retries: int = 3) -> CollectResult:
    """Execute every comparison; return binomial counts and tallies.

    prompt_builder(comparison) -> (system_content, user_content)
    judge_call(comparison, system_content, user_content) -> raw text
    """
    result = CollectResult(planned_calls=len(comparisons))
    outcomes: dict[Comparison, str | None] = {}

    for comp in comparisons:
        system, user = prompt_builder(comp)
        choice = None
        attempt = 0
        cache_hit = False
        for attempt in range(1 + max_retries):
            user_attempt = user if attempt == 0 else user + RETRY_SUFFIX
            raw = None
            key = None
            if cache is not None:
                key = cache.key(judge_model, judge_effort, attempt, system,
                                user_attempt, comp.repeat)
                raw = cache.get(key)
                if raw is not None:
                    cache_hit = True
                    result.cache_hits += 1
            if raw is None:
                raw = judge_call(comp, system, user_attempt)
                if cache is not None and raw is not None:
                    cache.put(key, raw, judge_model=judge_model,
                              effort=judge_effort, attempt=attempt)
            choice = parse_bt_response(raw)
            if choice is not None:
                break
        outcomes[comp] = choice

        if choice is None:
            result.unparseable_calls += 1
        else:
            result.first_total += 1
            if choice == "A":
                result.first_chosen += 1
            len_first = len(items_by_id[comp.first].text)
            len_second = len(items_by_id[comp.second].text)
            if len_first != len_second:
                result.longer_total += 1
                chosen_len = len_first if choice == "A" else len_second
                if chosen_len == max(len_first, len_second):
                    result.longer_chosen += 1

        result.log_records.append({
            "qid": comp.qid, "phase": comp.phase,
            "first": comp.first, "second": comp.second, "repeat": comp.repeat,
            "parse_ok": choice is not None, "choice": choice,
            "retries": attempt,
            "cache_hit": cache_hit,
            "first_len": len(items_by_id[comp.first].text),
            "second_len": len(items_by_id[comp.second].text),
            "judge": judge_model, "effort": judge_effort,
            "dropped": False,  # finalized below
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })

    # Group by (qid, phase, unordered pair, repeat); drop incomplete groups.
    groups: dict[tuple, list[Comparison]] = {}
    for comp in comparisons:
        pair = tuple(sorted((comp.first, comp.second)))
        groups.setdefault((comp.qid, comp.phase, pair, comp.repeat), []).append(comp)

    dropped_comps = set()
    for (qid, phase, pair, repeat), members in groups.items():
        if any(outcomes[m] is None for m in members):
            result.dropped_groups.append((qid, phase, pair[0], pair[1], repeat))
            dropped_comps.update(members)

    for comp in comparisons:
        if comp in dropped_comps:
            continue
        choice = outcomes[comp]
        wins, n = result.counts.get((comp.first, comp.second), (0, 0))
        result.counts[(comp.first, comp.second)] = (wins + (choice == "A"), n + 1)
        result.completed_calls += 1

    dropped_keys = {(c.qid, c.phase, c.first, c.second, c.repeat) for c in dropped_comps}
    for rec in result.log_records:
        if (rec["qid"], rec["phase"], rec["first"], rec["second"], rec["repeat"]) in dropped_keys:
            rec["dropped"] = True

    return result


def merge_counts(*count_dicts) -> dict:
    """Sum binomial counts across CollectResults (ordered-pair keyed)."""
    merged: dict = {}
    for counts in count_dicts:
        for pair, (w, n) in counts.items():
            mw, mn = merged.get(pair, (0, 0))
            merged[pair] = (mw + w, mn + n)
    return merged
