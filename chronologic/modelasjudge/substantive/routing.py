"""substantive/routing.py — the one definition of which channel a question is in.

Precedence: `partial_credit` -> `context_judged` -> the legacy
frame_type/reasoning_type rule. `bt_context_scoring.load_benchmark` and
`judge_scoring_nocontext._load_context_scored_qnums` both delegate here.

Why this exists: ChronoLogic 0.7 carries no `context_judged` field, so both
loaders silently fell back to the legacy rule (frame_type == "book_context"
and reasoning_type == "constrained_generation"), which selects 153
questions -- a strict subset of the 310 that carry `partial_credit == 1`.
That dropped 157 questions from the partial-credit channel and, because
cmd_score intersects with the other loader's identically-broken set, from
the pass/fail channel too. `partial_credit` is the field the spec names
(substantive-uncertainty-spec.md §Context), so it takes precedence whenever
present; `context_judged` is honoured next because it is an explicit
editorial flag (see chronologic_btpilot_0.1.jsonl, which predates
`partial_credit` but carries `context_judged` on all 40 of its questions);
the legacy rule is the last resort, kept only for benchmarks written before
either field existed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


def is_legacy_context_scored(rec: dict) -> bool:
    return (rec.get("frame_type") == "book_context"
            and rec.get("reasoning_type") == "constrained_generation")


def routing_basis(records: list[dict]) -> str:
    """Which field decides routing for this set of records.

    A file is taken at its word once any record carries the higher-
    precedence field, including records that set it to 0 -- the fallback
    only fires when a field is entirely absent from the file.
    """
    if any("partial_credit" in rec for rec in records):
        return "partial_credit"
    if any("context_judged" in rec for rec in records):
        return "context_judged"
    return "legacy"


def _is_partial(rec: dict, basis: str) -> bool:
    if basis == "partial_credit":
        return rec.get("partial_credit") == 1
    if basis == "context_judged":
        return rec.get("context_judged") == 1
    return is_legacy_context_scored(rec)


@dataclass
class Routing:
    basis: str
    pass_fail: dict[str, dict]
    partial: dict[str, dict]


def _load_records(path) -> list[tuple[int, dict]]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                rows.append((i, json.loads(line)))
    return rows


def route_questions(benchmark_path) -> Routing:
    """Partition every question in `benchmark_path` into the two channels."""
    rows = _load_records(benchmark_path)
    basis = routing_basis([rec for _, rec in rows])
    if basis == "legacy":
        print(f"  note: {Path(benchmark_path).name} has no partial_credit or "
              f"context_judged field; falling back to frame_type/reasoning_type.")

    pass_fail: dict[str, dict] = {}
    partial: dict[str, dict] = {}
    for i, rec in rows:
        qnum = str(rec.get("question_number", i))
        bucket = partial if _is_partial(rec, basis) else pass_fail
        bucket[qnum] = rec
    return Routing(basis=basis, pass_fail=pass_fail, partial=partial)


def assert_partition(routing: Routing, answered) -> None:
    """Raise if any question in `answered` was not routed to either channel.

    Every benchmark record is placed in exactly one bucket by construction,
    so a miss here means `answered` names a qnum absent from the benchmark
    that produced `routing` -- e.g. the wrong benchmark version was loaded.
    """
    routed = set(routing.pass_fail) | set(routing.partial)
    missing = sorted(set(answered) - routed, key=lambda q: (len(q), q))
    if missing:
        shown = missing[:10]
        more = f" (+{len(missing) - 10} more)" if len(missing) > 10 else ""
        raise ValueError(
            f"{len(missing)} answered question(s) not routed to any channel "
            f"under basis={routing.basis!r}: {shown}{more}"
        )
