"""
build_corpus_roster.py

Phase B.5 of the style judge (see phase-b5-plan.md, NOTES.md).

`corpus_manifest.csv` is an inventory -- everything usable on disk. This script is the
selection layer: it applies the corpus policy to that inventory and emits the roster
that actually trains the date predictor.

The two are deliberately separate. The manifest can stay a complete census (so the
policy is auditable against what was available and not chosen), and re-running selection
costs nothing.

Policy, per decade:

  target                 150 volumes in the 1831-1930 core, 100 elsewhere
  source priority        IDI first; then mixed-genre sources (ECCO pre-1800,
                         OAPEN post-1925); then, post-1930 only, Chicago fiction
  Chicago ceiling        30% of the target, post-1930 only
  IDI ceiling            40% of the target, post-1930 only -- post-1930 IDI is 40%
                         LAW / 19% SOCIAL SCIENCES / 9% AGRICULTURE, i.e. statutes and
                         government documents, and the genre labels are not trusted
                         enough to filter on directly
  COHA                   additive bonus everywhere: all of it, uncapped, and it does
                         not count against the quota

Genre balance floats freely outside the post-1930 span, where the sources are
mixed-genre and their natural composition varies by era.

Run from the repo root with the py310hf interpreter:

    ~/Dropbox/python/py310hf/bin/python3 stylejudge/build_corpus_roster.py
"""

import argparse
import csv
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime

csv.field_size_limit(10_000_000)

CORE = (1831, 1930)

# Manifest collections grouped into the tiers the policy talks about.
TIER_OF_COLLECTION = {
    "idi_sample1000": "idi",
    "idi_fill": "idi",
    "ecco": "ecco",
    "oapen_web": "oapen",
    "oapen_1925_1990": "oapen",
    "commoncrawl": "oapen",          # the other mixed modern source; only 23 volumes
    "chicago_fiction": "chicago",
    "coha_fic": "coha",
    "coha_mag": "coha",
    "coha_news": "coha",
    "coha_nf": "coha",
}

# Ordered tiers with each tier's cap as a fraction of the decade target.
# Declarative on purpose: rebalancing the corpus is an edit here, not a code change.
PRE_1931 = [("idi", 1.0), ("ecco", 1.0), ("oapen", 1.0)]
POST_1930 = [("idi", 0.40), ("oapen", 1.0), ("chicago", 0.30)]
ADDITIVE_TIERS = ["coha"]

ROSTER_FIELDS = [
    "volume_id", "collection", "tier", "path", "title", "author",
    "date", "decade", "selection_rank", "word_count",
]


def load_manifest(path):
    """Permitted, deduplicated, dated rows only -- the eligible pool."""
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["excluded"] != "0" or r["duplicate_of"] or not r["date"]:
                continue
            r["date"] = int(r["date"])
            r["decade"] = (r["date"] // 10) * 10
            r["tier"] = TIER_OF_COLLECTION.get(r["collection"], "other")
            r["word_count"] = int(r["word_count"]) if (r["word_count"] or "").isdigit() else 0
            rows.append(r)
    return rows


def author_key(row):
    """Grouping key for author spread.

    Blank authors become singleton groups rather than one giant bucket -- otherwise
    every anonymous volume in a decade would compete for a single round-robin slot.
    """
    a = (row.get("author") or "").strip().lower()
    if not a or a in ("nan", "none", "unknown") or "anonymous" in a:
        return f"__blank__{row['volume_id']}"
    return a


def pick_with_author_spread(candidates, n, rng):
    """Take n candidates, rotating across authors so no one author dominates.

    The IDI sampler already enforces <=2 books/author at draw time, but Chicago and
    OAPEN have no such control: taking the first 30 Chicago volumes of the 1980s could
    hand several slots to one prolific novelist. Deterministic given the seed.
    """
    if n <= 0 or not candidates:
        return []
    groups = defaultdict(list)
    for row in candidates:
        groups[author_key(row)].append(row)
    order = sorted(groups)
    rng.shuffle(order)
    for k in order:
        groups[k].sort(key=lambda r: (r["date"], r["volume_id"]))

    picked = []
    round_no = 0
    while len(picked) < n:
        added = False
        for k in order:
            if round_no < len(groups[k]):
                picked.append(groups[k][round_no])
                added = True
                if len(picked) >= n:
                    break
        if not added:
            break                       # pool exhausted before the quota
        round_no += 1
    return picked[:n]


def select(rows, args):
    """Apply the policy. Returns (roster_rows, per_decade_stats)."""
    rng = random.Random(args.seed)
    by_decade = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_decade[r["decade"]][r["tier"]].append(r)

    roster = []
    stats = {}
    for decade in sorted(by_decade):
        # Two decades straddle the core boundary -- 1831-1839 is 9/10 core, and only
        # 1930 of the 1930s is. Prorate the target by overlap rather than snapping the
        # whole decade to one side, which is what the census does too.
        core_years = sum(1 for y in range(decade, decade + 10)
                         if CORE[0] <= y <= CORE[1])
        target = round((core_years * args.core_target
                        + (10 - core_years) * args.outside_target) / 10)
        in_core = core_years >= 5

        # Post-1930 rules (IDI + Chicago ceilings) apply from the 1930s decade on:
        # 9 of its 10 years are post-1930.
        tiers = PRE_1931 if decade < 1930 else [
            ("idi", args.idi_cap_post1930), ("oapen", 1.0), ("chicago", args.chicago_cap)
        ]

        # Cap basis. "target" reads the ceilings as fractions of the 100/150 goal;
        # "realized" reads them as fractions of what actually gets selected. They
        # differ only where a decade falls short, and there the difference is severe:
        # with OAPEN (the sole uncapped post-1930 source) holding 6 volumes in the
        # 1930s, realized-share caps bound the whole decade to oapen/0.3 = 20 volumes.
        basis = target
        if args.cap_basis == "realized":
            uncapped = sum(len(by_decade[decade].get(t, [])) for t, c in tiers if c >= 1.0)
            capped_frac = sum(c for _t, c in tiers if c < 1.0)
            if capped_frac < 1.0:
                basis = min(target, int(uncapped / (1.0 - capped_frac)))

        need = target
        chosen = []
        composition = Counter()
        for tier_name, cap in tiers:
            if need <= 0:
                break
            pool = by_decade[decade].get(tier_name, [])
            allowed = min(need, round(cap * basis), len(pool))
            got = pick_with_author_spread(pool, allowed, rng)
            for row in got:
                chosen.append((row, tier_name))
            composition[tier_name] = len(got)
            need -= len(got)

        # COHA rides along: uncapped, additive, outside the quota
        bonus = []
        for tier_name in ADDITIVE_TIERS:
            for row in by_decade[decade].get(tier_name, []):
                bonus.append((row, "additive"))

        for rank, (row, tier_name) in enumerate(chosen + bonus, 1):
            out = {k: row.get(k, "") for k in ROSTER_FIELDS}
            out["tier"] = tier_name
            out["selection_rank"] = rank
            roster.append(out)

        stats[decade] = {
            "target": target,
            "selected": len(chosen),
            "shortfall": max(0, target - len(chosen)),
            "composition": dict(composition),
            "coha_bonus": len(bonus),
            "words": sum(r["word_count"] for r, _t in chosen + bonus),
            "in_core": in_core,
        }
    return roster, stats


def check_policy(stats, args):
    """Check the ceilings. Returns (hard_violations, realized_share_notes).

    Hard violations are breaches of the cap on its chosen basis -- those are bugs.
    The notes list decades where the *realized* share exceeds the nominal ceiling
    because the decade fell short of target; those are supply facts, not bugs, and
    are reported so the drift is never invisible.
    """
    bad, notes = [], []
    for decade, s in sorted(stats.items()):
        if s["selected"] > s["target"]:
            bad.append(f"{decade}s: {s['selected']} selected exceeds target {s['target']}")
        if decade < 1930 or not s["selected"]:
            continue
        basis = s["selected"] if args.cap_basis == "realized" else s["target"]
        for tier, cap, label in (("idi", args.idi_cap_post1930, "IDI"),
                                 ("chicago", args.chicago_cap, "Chicago")):
            n = s["composition"].get(tier, 0)
            if n > round(cap * basis):
                bad.append(f"{decade}s: {label} {n} exceeds {cap:.0%} of "
                           f"{args.cap_basis} ({basis})")
            share = n / s["selected"]
            if share > cap + 0.005:
                notes.append(f"{decade}s: {label} is {share:.0%} of the "
                             f"{s['selected']} selected (ceiling {cap:.0%}); the decade "
                             f"is {s['shortfall']} short of target")
    return bad, notes


def author_spread_report(roster):
    """Worst author concentration per decade, excluding the additive COHA tier."""
    out = {}
    per = defaultdict(Counter)
    for r in roster:
        if r["tier"] == "additive":
            continue
        a = (r.get("author") or "").strip().lower()
        if a and a not in ("nan", "none", "unknown") and "anonymous" not in a:
            per[r["decade"]][a] += 1
    for decade, c in per.items():
        if c:
            author, n = c.most_common(1)[0]
            out[decade] = (author[:40], n)
    return out


def write_report(path, stats, roster, spread, violations, notes, args):
    L = []
    a = L.append
    total = sum(s["selected"] for s in stats.values())
    bonus = sum(s["coha_bonus"] for s in stats.values())
    words = sum(s["words"] for s in stats.values())

    a("# Dating-corpus roster\n")
    a(f"Generated {datetime.now().isoformat(timespec='seconds')} by "
      "`stylejudge/build_corpus_roster.py`.\n")
    a(f"**{total:,} volumes selected** against the per-decade quota, plus **{bonus:,}** "
      f"additive COHA volumes. {words/1e6:.0f}M words total.\n")
    a("This is the corpus that trains the date predictor. "
      "`corpus_manifest.csv` remains the full inventory of what was available.\n")

    a("## Policy\n")
    a(f"- Target: **{args.core_target}** volumes/decade in {CORE[0]}-{CORE[1]}, "
      f"**{args.outside_target}** elsewhere.")
    a("- Priority: IDI → mixed-genre (ECCO pre-1800, OAPEN post-1925) → Chicago fiction.")
    a(f"- Post-1930 ceilings: IDI ≤ **{args.idi_cap_post1930:.0%}**, "
      f"Chicago ≤ **{args.chicago_cap:.0%}** of the target.")
    a("- COHA is additive everywhere: uncapped, and outside the quota.\n")

    a("## Per-decade composition\n")
    a("| Decade | target | selected | short | IDI | ECCO | OAPEN | Chicago | +COHA | words |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for d in sorted(stats):
        s = stats[d]
        c = s["composition"]
        def cell(k):
            n = c.get(k, 0)
            if not n:
                return ""
            return f"{n} ({100*n/s['selected']:.0f}%)" if s["selected"] else str(n)
        short = f"**{s['shortfall']}**" if s["shortfall"] else ""
        a(f"| {d}s | {s['target']} | {s['selected']} | {short} | {cell('idi')} | "
          f"{cell('ecco')} | {cell('oapen')} | {cell('chicago')} | "
          f"{s['coha_bonus'] or ''} | {s['words']/1e6:.1f}M |")
    a("")

    a("## Policy checks\n")
    a(f"Ceilings enforced against the **{args.cap_basis}** "
      f"({'the 100/150 goal' if args.cap_basis == 'target' else 'what was actually selected'}).\n")
    if notes:
        a("Realized shares above the nominal ceiling, because the decade is "
          "supply-limited and fell short of target:\n")
        for n in notes:
            a(f"- {n}")
        a("")
    if violations:
        a("**VIOLATIONS:**\n")
        for v in violations:
            a(f"- {v}")
    else:
        a("No decade exceeds its target; no post-1930 decade exceeds the IDI 40% or "
          "Chicago 30% ceiling.")
    a("")
    shortfalls = [(d, s["shortfall"]) for d, s in sorted(stats.items()) if s["shortfall"]]
    if shortfalls:
        a("Decades short of target (supply-limited, not policy failures):\n")
        a("| Decade | short by |")
        a("|---|---|")
        for d, n in shortfalls:
            a(f"| {d}s | {n} |")
        a("")

    a("## Author spread\n")
    a("Most-repeated author per decade in the quota tiers (COHA excluded). Selection "
      "rotates across authors, so a high number means the pool itself was thin.\n")
    a("| Decade | author | volumes |")
    a("|---|---|---|")
    for d in sorted(spread):
        author, n = spread[d]
        flag = " ⚠" if n > 3 else ""
        a(f"| {d}s | {author} | {n}{flag} |")
    a("")

    with open(path, "w") as fh:
        fh.write("\n".join(L))


def make_plot(stats, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    decades = sorted(stats)
    x = np.arange(len(decades))
    tiers = ["idi", "ecco", "oapen", "chicago"]
    colors = {"idi": "#3b6ea5", "ecco": "#8c6bb1", "oapen": "#41ab5d",
              "chicago": "#e6821e", "coha": "#999999"}

    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = np.zeros(len(decades))
    for t in tiers:
        vals = np.array([stats[d]["composition"].get(t, 0) for d in decades], dtype=float)
        if not vals.any():
            continue
        ax.bar(x, vals, bottom=bottom, label=t, color=colors[t], width=0.82)
        bottom += vals
    coha = np.array([stats[d]["coha_bonus"] for d in decades], dtype=float)
    ax.bar(x, coha, bottom=bottom, label="coha (additive)", color=colors["coha"],
           width=0.82, alpha=0.55)

    ax.plot(x, [stats[d]["target"] for d in decades], "k--", lw=1.4, label="target")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{d}s" for d in decades], rotation=90, fontsize=8)
    ax.set_ylabel("Volumes", fontsize=12)
    ax.set_title("Dating-corpus roster: selected volumes per decade by source",
                 fontsize=13)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Plot written to {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="stylejudge/corpus_manifest.csv")
    ap.add_argument("--out", default="stylejudge/corpus_roster.csv")
    ap.add_argument("--report", default="stylejudge/corpus_roster_report.md")
    ap.add_argument("--plot", default="stylejudge/corpus_roster.png")
    ap.add_argument("--core-target", type=int, default=150)
    ap.add_argument("--outside-target", type=int, default=100)
    ap.add_argument("--idi-cap-post1930", type=float, default=0.40)
    ap.add_argument("--chicago-cap", type=float, default=0.30)
    ap.add_argument("--cap-basis", choices=("target", "realized"), default="target",
                    help="enforce post-1930 ceilings as a fraction of the decade target "
                         "(default) or of the volumes actually selected. 'realized' is "
                         "stricter but bounds a short decade to uncapped_supply/0.3 -- "
                         "20 volumes for the 1930s, where OAPEN holds only 6.")
    ap.add_argument("--seed", type=int, default=20260810)
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    rows = load_manifest(args.manifest)
    print(f"Eligible pool: {len(rows):,} volumes "
          f"({len({r['collection'] for r in rows})} collections)")

    roster, stats = select(rows, args)
    violations, notes = check_policy(stats, args)
    spread = author_spread_report(roster)

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ROSTER_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in roster:
            w.writerow(r)
    print(f"Roster written to {args.out} ({len(roster):,} rows)")

    write_report(args.report, stats, roster, spread, violations, notes, args)
    print(f"Report written to {args.report}")
    if not args.no_plot:
        make_plot(stats, args.plot)

    quota = sum(s["selected"] for s in stats.values())
    bonus = sum(s["coha_bonus"] for s in stats.values())
    print(f"\n=== {quota:,} volumes on quota + {bonus:,} additive COHA "
          f"= {len(roster):,} rows ===")
    print(f"{'dec':7s}{'sel':>5s}{'tgt':>5s}   composition")
    for d in sorted(stats):
        s = stats[d]
        comp = "  ".join(f"{k}={v}" for k, v in s["composition"].items() if v)
        short = "  SHORT" if s["shortfall"] else ""
        print(f"{d}s {s['selected']:>4d} {s['target']:>4d}   {comp}"
              f"{'  +coha=' + str(s['coha_bonus']) if s['coha_bonus'] else ''}{short}")

    if notes:
        print("\nRealized share above the nominal ceiling (supply-limited decades):")
        for n in notes:
            print(f"  {n}")
    if violations:
        print("\nPOLICY VIOLATIONS:")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)
    print("\nPolicy checks passed.")


if __name__ == "__main__":
    main()
