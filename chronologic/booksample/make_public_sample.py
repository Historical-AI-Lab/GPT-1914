#!/usr/bin/env python3
"""Draw the public sample of Chronologic-EN.

The full benchmark is distributed under controlled access, so the repository
ships a sample instead. This script draws it, and is committed so that the
selection is reproducible and inspectable rather than a file of unclear
provenance.

What it draws
-------------
100 questions. Two constraints shape the draw:

1. **Proportional by reasoning type.** Each of the eight reasoning types gets
   a share of the 100 matching its share of the full benchmark, allocated by
   the largest-remainder method so the parts sum to exactly 100. A reader of
   the sample therefore sees the same mix of task shapes the benchmark has.

2. **Balanced by frame type within each reasoning type.** The three frame
   types (world_context, book_context, passage_context) are filled round
   robin, so a type whose questions are mostly book-framed still contributes
   some world-framed examples where it has them.

Questions already printed in the paper are force-included, since publishing
them costs no additional exposure and it lets a reader match the sample
against the paper's examples. They count against their reasoning type's quota
rather than adding to it. See PAPER_QUESTIONS below.

The draw is seeded, so re-running reproduces the same file exactly.

Usage
-----
    python booksample/make_public_sample.py
    python booksample/make_public_sample.py --n 150 --seed 20260914
    python booksample/make_public_sample.py --describe     # report, write nothing

The default output name is matched by a negation in .gitignore; every other
chronologic_en_* file is deliberately excluded from git.
"""

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_BENCHMARK = SCRIPT_DIR / "chronologic_en_0.8.jsonl"
DEFAULT_OUT = SCRIPT_DIR / "chronologic_en_1.0_sample.jsonl"
DEFAULT_N = 100
DEFAULT_SEED = 20260914

# Questions reproduced in the paper, so already public. Keyed by question
# number, with the location that prints them.
PAPER_QUESTIONS = {
    42:  "Appendix, Knowledge example (Philip V / Duke of Anjou)",
    107: "Appendix, Character modeling example (Kin-da-shon's Wife, 1892)",
    210: "Appendix, Structured cloze example (Argentina, Hirst, 1910)",
    424: "Figure, metadata frame vs. main question (Macaulay / Hunter Commission)",
    453: "Appendix, Inference example (Jamieson, Applied Mechanics, 1895)",
    543: "Appendix, Abstention example (ferrite rod antenna, Nilson, 1924)",
    569: "Appendix, Constrained generation example (The Theosophical Forum, 1903)",
    727: "Section 'Admissible variation' (the 'necessaries of life' question)",
    733: "Appendix, reasoning-model diagnostics table (the 'sleeves' question)",
    765: "Section 'Substantive judgment' (Quaker periodical, US Indian policy)",
    888: "Appendix, Bradley-Terry worked example (Notes on Sea-coast Defence, 1861)",
}


def read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def largest_remainder(counts, total):
    """Apportion `total` across `counts` so the parts sum to exactly `total`.

    Plain rounding of proportional shares does not sum to the target -- for the
    866-question benchmark it lands on 99 -- so the fractional parts decide who
    gets the leftover seats, largest first.
    """
    grand = sum(counts.values())
    exact = {k: v * total / grand for k, v in counts.items()}
    floors = {k: int(v) for k, v in exact.items()}
    shortfall = total - sum(floors.values())
    order = sorted(exact, key=lambda k: (exact[k] - floors[k], counts[k]), reverse=True)
    for key in order[:shortfall]:
        floors[key] += 1
    return floors


def pick_within_type(pool, quota, forced, rng):
    """Choose `quota` questions from one reasoning type, frame-balanced.

    `forced` are taken first. The rest are drawn by cycling through frame
    types, so the result spreads across frames instead of following whatever
    frame happens to dominate the type.
    """
    chosen = [r for r in pool if r["question_number"] in forced]
    remaining = [r for r in pool if r["question_number"] not in forced]

    by_frame = defaultdict(list)
    for record in remaining:
        by_frame[record["frame_type"]].append(record)
    for frame in by_frame:
        rng.shuffle(by_frame[frame])

    # Start from the least-represented frame so scarce frames are not starved
    # by a round robin that always begins at the same place.
    frames = sorted(by_frame, key=lambda f: len(by_frame[f]))
    while len(chosen) < quota and any(by_frame[f] for f in frames):
        for frame in frames:
            if len(chosen) >= quota:
                break
            if by_frame[frame]:
                chosen.append(by_frame[frame].pop())
    return chosen


def draw(records, n, seed):
    rng = random.Random(seed)
    forced = set(PAPER_QUESTIONS)

    present = {r["question_number"] for r in records}
    missing = forced - present
    if missing:
        raise SystemExit(
            f"paper questions absent from the benchmark: {sorted(missing)}. "
            "PAPER_QUESTIONS is keyed to the released question numbering; if the "
            "numbering changed, update it rather than dropping the entries."
        )

    by_type = defaultdict(list)
    for record in records:
        by_type[record["reasoning_type"]].append(record)
    for key in by_type:
        by_type[key].sort(key=lambda r: r["question_number"])

    quotas = largest_remainder(
        {k: len(v) for k, v in by_type.items()}, n)

    # A reasoning type could in principle carry more forced questions than its
    # proportional quota. Honour the forced set and let that type run over.
    forced_by_type = Counter(
        r["reasoning_type"] for r in records if r["question_number"] in forced)
    for rtype, count in forced_by_type.items():
        quotas[rtype] = max(quotas[rtype], count)

    chosen = []
    for rtype in sorted(by_type):
        chosen.extend(pick_within_type(by_type[rtype], quotas[rtype], forced, rng))
    chosen.sort(key=lambda r: r["question_number"])
    return chosen


def describe(records, chosen):
    all_types = Counter(r["reasoning_type"] for r in records)
    got_types = Counter(r["reasoning_type"] for r in chosen)
    print(f"  {len(chosen)} questions drawn from {len(records)}\n")
    print("  %-24s %8s %8s" % ("reasoning type", "sample", "full"))
    for rtype in sorted(all_types, key=lambda k: -all_types[k]):
        print("  %-24s %5d    %5d" % (rtype, got_types[rtype], all_types[rtype]))
    print()
    all_frames = Counter(r["frame_type"] for r in records)
    got_frames = Counter(r["frame_type"] for r in chosen)
    print("  %-24s %8s %8s" % ("frame type", "sample", "full"))
    for frame in sorted(all_frames, key=lambda k: -all_frames[k]):
        print("  %-24s %5d    %5d" % (frame, got_frames[frame], all_frames[frame]))
    included = sorted(r["question_number"] for r in chosen
                      if r["question_number"] in PAPER_QUESTIONS)
    print(f"\n  paper questions included: {len(included)}/{len(PAPER_QUESTIONS)} "
          f"-> {included}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK),
                        help=f"full benchmark JSONL (default: {DEFAULT_BENCHMARK.name})")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help=f"output JSONL (default: {DEFAULT_OUT.name})")
    parser.add_argument("--n", type=int, default=DEFAULT_N,
                        help=f"sample size (default: {DEFAULT_N})")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"RNG seed (default: {DEFAULT_SEED})")
    parser.add_argument("--describe", action="store_true",
                        help="print the composition report and write nothing")
    args = parser.parse_args()

    records = read_jsonl(args.benchmark)
    chosen = draw(records, args.n, args.seed)
    describe(records, chosen)

    if args.describe:
        print("\n  --describe: no file written")
        return

    out_path = Path(args.out)
    with open(out_path, "w", encoding="utf-8") as handle:
        for record in chosen:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"\n  wrote {len(chosen)} questions to {out_path}")


if __name__ == "__main__":
    main()
