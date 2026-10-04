#!/usr/bin/env python3
"""sample_pairs.py — sample candidate-answer pairs for human validation of p_fit.

Maps the actual distribution of logit(p_fit) and |Delta logit(p_fit)| across
every candidate-pair x question combination in the 346 partial-credit
questions of a ChronoLogic benchmark (default: chronologic_en_0.8.jsonl),
then selects 90 pairs stratified on that distribution (per
humeval_bt/human-validation-for-pfit-spec.md) and assigns them to 6 human
raters via a balanced dyad design: C(6,2) = 15 rater dyads, one item from
each of 6 |Delta logit(p_fit)| strata assigned to each dyad, so every rater
judges 30 pairs and every pair is judged by exactly 2 raters.

Only candidate model outputs are ever a side of a comparison pair. Ground
truth and distractor strings from the benchmark are a separate pool, used
only for on-screen context in rate_pairs.py, and never enter this script's
pairing logic.

Usage
-----
  python sample_pairs.py [options]

  --benchmark PATH        Default: <repo>/booksample/chronologic_en_0.8.jsonl
  --scored-glob PATTERN   Default: judge_*__*__0.8__c-*__j-medium_btcontext.json
                          (resolved under modelasjudge/scored_answers/)
  --generated-dir PATH    Default: modelasjudge/generated_answers/
  --candidates LABELS     Comma list to restrict to specific candidate_labels.
                          Default: auto-discover all matching --scored-glob.
  --raters CODES          Comma list of rater identifiers.
                          Default: R1,R2,R3,R4,R5,R6
  --seed INT              Default: 1914
  --out-dir PATH          Default: modelasjudge/humeval_bt/round1/
  --dry-run               Compute distribution + strata + coverage report and
                          save the two population plots, but do not select
                          pairs or write master/rater files.

Examples
--------
  cd modelasjudge/humeval_bt
  ~/Dropbox/python/py310hf/bin/python3 sample_pairs.py --dry-run
  ~/Dropbox/python/py310hf/bin/python3 sample_pairs.py
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np
from scipy.special import logit

SCRIPT_DIR = Path(__file__).resolve().parent
MODELASJUDGE_DIR = SCRIPT_DIR.parent
REPO_ROOT = MODELASJUDGE_DIR.parent
sys.path.insert(0, str(MODELASJUDGE_DIR))

from bt.design import derive_seed  # noqa: E402
from naming import sanitize  # noqa: E402
from substantive.routing import route_questions  # noqa: E402

DEFAULT_BENCHMARK = REPO_ROOT / "booksample" / "chronologic_en_0.8.jsonl"
DEFAULT_SCORED_DIR = MODELASJUDGE_DIR / "scored_answers"
DEFAULT_GENERATED_DIR = MODELASJUDGE_DIR / "generated_answers"
DEFAULT_SCORED_GLOB = "judge_*__*__0.8__c-*__j-medium_btcontext.json"
DEFAULT_OUT_DIR = SCRIPT_DIR / "round1"
DEFAULT_SEED = 1914
DEFAULT_RATERS = ["R1", "R2", "R3", "R4", "R5", "R6"]
N_BELOW_MEDIAN_STRATA = 4
N_ABOVE_MEDIAN_STRATA = 2
EPS = 1e-6
TIE_EPS = 1e-9  # p_fit values closer than this are treated as an exact BT tie


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_answer_text(generated_dir: Path, label: str) -> tuple[dict, str]:
    """Candidate model outputs only, keyed by question_number string.

    Tries the 0.8 free_gen file first, falls back to 0.7 (several 0.8-scored
    candidates reused their 0.7 free-gen text unchanged), then a bare glob.
    Tries both the full sanitized label and just its basename, since at
    least one candidate (a local path like
    "/projects/bdfx/models/Qwen2.5-72B-Instruct") has a free_gen file named
    after only the last path segment. Returns (text_by_qnum, version_used_label).
    """
    tags = [sanitize(label)]
    basename = label.rsplit("/", 1)[-1]
    if basename != label:
        tags.append(sanitize(basename))

    for tag in tags:
        for version in ("0.8", "0.7"):
            p = generated_dir / f"free_gen_{tag}__{version}.json"
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                text = {qnum: entry.get("answer", "")
                        for qnum, entry in data.get("answers", {}).items()}
                return text, version
    for tag in tags:
        matches = sorted(generated_dir.glob(f"free_gen_{tag}*.json"))
        if matches:
            data = json.loads(matches[0].read_text(encoding="utf-8"))
            text = {qnum: entry.get("answer", "")
                    for qnum, entry in data.get("answers", {}).items()}
            return text, f"fallback:{matches[0].name}"
    return {}, "none"


def load_candidates(scored_dir: Path, scored_glob: str,
                     candidates_filter: set | None,
                     generated_dir: Path) -> tuple[dict, list[str]]:
    """Return {label: {"p_fit": {qnum: float}, "text": {qnum: str}}}, coverage lines."""
    files = sorted(scored_dir.glob(scored_glob))
    if not files:
        raise SystemExit(f"No scored_answers files matched {scored_glob!r} in {scored_dir}")

    result: dict[str, dict] = {}
    coverage_lines = ["candidate_label | p_fit_questions | text_resolved | missing_text | text_source"]
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        label = data.get("candidate_label") or f.stem
        if candidates_filter and label not in candidates_filter:
            continue
        p_fit = {}
        for qnum, entry in data.get("context_fit", {}).items():
            bt = entry.get("bt") or {}
            p = bt.get("p_fit")
            if p is not None and 0.0 < p < 1.0:
                p_fit[qnum] = float(p)

        text, version_used = load_answer_text(generated_dir, label)
        missing = [q for q in p_fit if q not in text or not text[q].strip()]
        coverage_lines.append(
            f"{label} | {len(p_fit)} | {len(p_fit) - len(missing)} | "
            f"{len(missing)} | {version_used}"
        )
        result[label] = {"p_fit": p_fit, "text": text}

    return result, coverage_lines


# ---------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------

def build_population(candidates: dict, partial_qnums: list[str]) -> list[dict]:
    """Every (question, candidate-pair) with resolvable p_fit + distinct answer text.

    Only draws from candidates[*]["text"] (model outputs). Ground truth and
    distractor strings are never touched here.
    """
    labels = sorted(candidates)
    pop = []
    for qnum in partial_qnums:
        for la, lb in itertools.combinations(labels, 2):
            pa = candidates[la]["p_fit"].get(qnum)
            pb = candidates[lb]["p_fit"].get(qnum)
            if pa is None or pb is None:
                continue
            ta = candidates[la]["text"].get(qnum, "")
            tb = candidates[lb]["text"].get(qnum, "")
            if not ta.strip() or not tb.strip():
                continue
            if ta.strip() == tb.strip():
                continue  # a human can't force-choose between identical text
            if abs(pa - pb) < TIE_EPS:
                continue  # exact p_fit tie -- the model predicts 0.5 here by
                          # construction (f(0,m)=0), so there is no signal to
                          # gain by spending a human judgment on it
            pa_c = min(max(pa, EPS), 1 - EPS)
            pb_c = min(max(pb, EPS), 1 - EPS)
            x = abs(float(logit(pa_c) - logit(pb_c)))
            m = (pa + pb) / 2.0
            if pa >= pb:
                hi_label, lo_label, p_hi, p_lo = la, lb, pa, pb
            else:
                hi_label, lo_label, p_hi, p_lo = lb, la, pb, pa
            pop.append({
                "question_number": qnum,
                "candidate_label_hi": hi_label,
                "candidate_label_lo": lo_label,
                "p_fit_hi": p_hi,
                "p_fit_lo": p_lo,
                "delta_p": p_hi - p_lo,
                "x": x,
                "m": m,
            })
    return pop


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_distributions(candidates: dict, pop: list[dict], out_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available -- skipping plots", file=sys.stderr)
        return

    all_p = np.array([p for c in candidates.values() for p in c["p_fit"].values()])
    all_p = np.clip(all_p, EPS, 1 - EPS)
    all_logit = logit(all_p)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.hist(all_logit, bins=40, color="#4C78A8")
    ax.set_xlabel("logit(p_fit)")
    ax.set_ylabel("count")
    ax.set_title("Distribution of logit(p_fit), all candidates x all partial-credit questions")
    fig.tight_layout()
    fig.savefig(out_dir / "distribution_pfit_logit.png", dpi=150)
    plt.close(fig)

    xs = np.array([r["x"] for r in pop])
    med, mean = float(np.median(xs)), float(np.mean(xs))
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.hist(xs, bins=40, color="#4C78A8")
    ax.axvline(med, color="black", ls="--", label=f"median={med:.3f}")
    ax.axvline(mean, color="gray", ls=":", label=f"mean={mean:.3f}")
    ax.set_xlabel("|Delta logit(p_fit)| between two candidates on the same question")
    ax.set_ylabel("count")
    ax.set_title("Distribution of |Delta logit(p_fit)| across candidate pairs")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "distribution_delta_logit.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Stratification
# ---------------------------------------------------------------------------

def assign_strata(pop: list[dict]) -> tuple[float, np.ndarray, np.ndarray]:
    """6 strata on x: 4 quantile bins below the population median, 2 above.

    Returns (median_x, below_edges, above_edges); mutates each record with
    r["stratum"] in 0..5 (0-3 below median, 4-5 above).
    """
    xs = np.array(sorted(r["x"] for r in pop))
    median_x = float(np.median(xs))
    below = xs[xs <= median_x]
    above = xs[xs > median_x]
    if len(above) == 0:
        # degenerate (all ties at the median); still produce 2 empty-ish bins
        above = below[-1:]
    below_edges = np.quantile(below, [0, .25, .5, .75, 1.0])
    above_edges = np.quantile(above, [0, .5, 1.0])
    below_inner = below_edges[1:-1]
    above_inner = above_edges[1:-1]

    for r in pop:
        x = r["x"]
        if x <= median_x:
            r["stratum"] = int(np.searchsorted(below_inner, x, side="right"))
        else:
            r["stratum"] = 4 + int(np.searchsorted(above_inner, x, side="right"))
    return median_x, below_edges, above_edges


def assign_midpoint_tertiles(pop: list[dict]) -> np.ndarray:
    ms = np.array(sorted(r["m"] for r in pop))
    edges = np.quantile(ms, [1 / 3, 2 / 3])
    for r in pop:
        r["midpoint_tertile"] = int(np.searchsorted(edges, r["m"], side="right"))
    return edges


# ---------------------------------------------------------------------------
# Selection: 15 items per stratum, best-effort 5/5/5 midpoint balance,
# one distinct question_number across all 90 selected items.
# ---------------------------------------------------------------------------

def select_items(pop: list[dict], seed: int, pairs_per_stratum: int,
                  n_strata: int) -> tuple[list[list[dict]], list[str]]:
    by_stratum_tertile: dict[int, dict[int, list[dict]]] = {
        s: {0: [], 1: [], 2: []} for s in range(n_strata)
    }
    for r in pop:
        by_stratum_tertile[r["stratum"]][r["midpoint_tertile"]].append(r)

    used_questions: set[str] = set()
    selected_by_stratum: list[list[dict]] = []
    balance_log: list[str] = []

    for s in range(n_strata):
        cells = by_stratum_tertile[s]
        target = pairs_per_stratum / 3.0
        remaining_target = {t: round(target) for t in range(3)}
        # fix rounding so the three targets sum to pairs_per_stratum
        diff = pairs_per_stratum - sum(remaining_target.values())
        remaining_target[0] += diff

        tertile_order = sorted(range(3), key=lambda t: len(cells[t]))
        selected: list[dict] = []
        selected_qnums: set[str] = set()
        achieved = {0: 0, 1: 0, 2: 0}

        for t in tertile_order:
            rng = random.Random(derive_seed(seed, "sample", s, t))
            pool = [r for r in cells[t]
                    if r["question_number"] not in used_questions
                    and r["question_number"] not in selected_qnums]
            rng.shuffle(pool)
            need = remaining_target[t]
            for r in pool:
                if achieved[t] >= need:
                    break
                if r["question_number"] in selected_qnums:
                    continue  # another item in this same pool already claimed this question
                selected.append(r)
                selected_qnums.add(r["question_number"])
                achieved[t] += 1

        # backfill any shortfall from anywhere in this stratum
        if len(selected) < pairs_per_stratum:
            rng = random.Random(derive_seed(seed, "sample-backfill", s))
            all_pool = [r for t in range(3) for r in cells[t]
                        if r["question_number"] not in used_questions
                        and r["question_number"] not in selected_qnums]
            rng.shuffle(all_pool)
            for r in all_pool:
                if len(selected) >= pairs_per_stratum:
                    break
                if r["question_number"] in selected_qnums:
                    continue
                selected.append(r)
                selected_qnums.add(r["question_number"])
                achieved[r["midpoint_tertile"]] += 1

        used_questions |= selected_qnums
        selected_by_stratum.append(selected)
        balance_log.append(
            f"stratum {s}: target={pairs_per_stratum} achieved={len(selected)} "
            f"(midpoint low/mid/high = {achieved[0]}/{achieved[1]}/{achieved[2]}, "
            f"target each ~{pairs_per_stratum/3:.1f})"
        )
        if len(selected) < pairs_per_stratum:
            balance_log.append(
                f"  WARNING: stratum {s} short by {pairs_per_stratum - len(selected)} "
                "item(s) -- pool exhausted under the distinct-question constraint."
            )

    return selected_by_stratum, balance_log


# ---------------------------------------------------------------------------
# Dyad assignment + side randomization
# ---------------------------------------------------------------------------

def assign_dyads_and_sides(selected_by_stratum: list[list[dict]], raters: list[str],
                            seed: int) -> list[dict]:
    dyads = list(itertools.combinations(raters, 2))
    master: list[dict] = []
    pair_counter = 0

    for s, items in enumerate(selected_by_stratum):
        rng = random.Random(derive_seed(seed, "dyad-assign", s))
        items_shuffled = list(items)
        rng.shuffle(items_shuffled)
        n = min(len(items_shuffled), len(dyads))
        if len(items_shuffled) != len(dyads):
            print(f"WARNING: stratum {s} has {len(items_shuffled)} items but "
                  f"{len(dyads)} dyads -- some dyads will not get an item "
                  "from this stratum.", file=sys.stderr)

        for i in range(n):
            item = items_shuffled[i]
            dyad = dyads[i]
            pair_counter += 1
            pair_id = f"P{pair_counter:03d}"
            raters_info = []
            for rater_id in dyad:
                coin = random.Random(derive_seed(seed, "side", pair_id, rater_id)).random()
                side_of_hi = "A" if coin < 0.5 else "B"
                raters_info.append({"rater_id": rater_id, "side_of_hi": side_of_hi})
            master.append({
                "pair_id": pair_id,
                "question_number": item["question_number"],
                "stratum": s,
                "midpoint_tertile": item["midpoint_tertile"],
                "x": item["x"],
                "m": item["m"],
                "delta_p": item["delta_p"],
                "candidate_label_hi": item["candidate_label_hi"],
                "candidate_label_lo": item["candidate_label_lo"],
                "p_fit_hi": item["p_fit_hi"],
                "p_fit_lo": item["p_fit_lo"],
                "dyad": list(dyad),
                "raters": raters_info,
            })
    return master


def write_rater_files(master: list[dict], candidates: dict, raters: list[str],
                       seed: int, out_dir: Path) -> None:
    per_rater: dict[str, list[dict]] = {r: [] for r in raters}
    for row in master:
        text_hi = candidates[row["candidate_label_hi"]]["text"][row["question_number"]]
        text_lo = candidates[row["candidate_label_lo"]]["text"][row["question_number"]]
        for r in row["raters"]:
            rater_id = r["rater_id"]
            if r["side_of_hi"] == "A":
                answer_a, answer_b = text_hi, text_lo
            else:
                answer_a, answer_b = text_lo, text_hi
            per_rater[rater_id].append({
                "rater_id": rater_id,
                "pair_id": row["pair_id"],
                "question_number": row["question_number"],
                "answer_A": answer_a,
                "answer_B": answer_b,
            })

    for rater_id, items in per_rater.items():
        rng = random.Random(derive_seed(seed, "order", rater_id))
        rng.shuffle(items)
        for i, item in enumerate(items, start=1):
            item["item_index"] = i
        items.sort(key=lambda d: d["item_index"])
        path = out_dir / f"humeval_pfit_{rater_id}.jsonl"
        with open(path, "w", encoding="utf-8") as fh:
            for item in items:
                # explicit key order: no candidate label, no p_fit -- blinding boundary
                row = {
                    "rater_id": item["rater_id"],
                    "item_index": item["item_index"],
                    "pair_id": item["pair_id"],
                    "question_number": item["question_number"],
                    "answer_A": item["answer_A"],
                    "answer_B": item["answer_B"],
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"  wrote {path} ({len(items)} items)")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_sampling_summary(out_dir: Path, coverage_lines: list[str], pop: list[dict],
                            median_x: float, below_edges: np.ndarray, above_edges: np.ndarray,
                            balance_log: list[str] | None, master: list[dict] | None) -> None:
    lines = ["# Sampling summary\n"]
    lines.append("## Candidate coverage\n")
    lines.extend(f"    {c}" for c in coverage_lines)
    lines.append("")

    xs = np.array([r["x"] for r in pop])
    lines.append("## Population\n")
    lines.append(f"- candidate-pair x question combinations usable: {len(pop)}")
    lines.append(f"- |Delta logit(p_fit)| median={median_x:.4f} mean={float(xs.mean()):.4f} "
                 f"IQR=[{float(np.quantile(xs,.25)):.4f}, {float(np.quantile(xs,.75)):.4f}]")
    lines.append("")

    lines.append("## Stratum edges (logit-x space, then empirical raw |Delta p_fit| range)\n")
    edge_pairs = []
    for i in range(4):
        edge_pairs.append((below_edges[i], below_edges[i + 1]))
    for i in range(2):
        edge_pairs.append((above_edges[i], above_edges[i + 1]))
    for s, (lo, hi) in enumerate(edge_pairs):
        raw = [r["delta_p"] for r in pop if r.get("stratum") == s]
        if raw:
            raw_lo, raw_hi = min(raw), max(raw)
        else:
            raw_lo = raw_hi = float("nan")
        lines.append(f"- stratum {s}: x in [{lo:.4f}, {hi:.4f}]  ->  "
                     f"raw |Delta p_fit| observed in [{raw_lo:.4f}, {raw_hi:.4f}]")
    lines.append("")

    if balance_log is not None:
        lines.append("## Selection balance (target 5/5/5 midpoint tertile per stratum)\n")
        lines.extend(f"- {b}" for b in balance_log)
        lines.append("")

    if master is not None:
        qnums = sorted({r["question_number"] for r in master}, key=int)
        lines.append(f"## Selected pairs: {len(master)} total, {len(qnums)} distinct questions\n")
        lines.append("question_numbers: " + ", ".join(qnums))
        lines.append("")
        from collections import Counter
        pair_freq = Counter(
            tuple(sorted((r["candidate_label_hi"], r["candidate_label_lo"])))
            for r in master
        )
        lines.append("## Candidate-label pair frequency among selected items\n")
        for pair, n in pair_freq.most_common():
            lines.append(f"- {pair[0]} vs {pair[1]}: {n}")

    (out_dir / "sampling_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Sample and assign candidate-answer pairs for p_fit human validation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    p.add_argument("--scored-glob", default=DEFAULT_SCORED_GLOB)
    p.add_argument("--generated-dir", default=str(DEFAULT_GENERATED_DIR))
    p.add_argument("--candidates", default=None,
                    help="Comma list to restrict to specific candidate_labels")
    p.add_argument("--raters", default=",".join(DEFAULT_RATERS))
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates_filter = (set(x.strip() for x in args.candidates.split(","))
                         if args.candidates else None)
    raters = [r.strip() for r in args.raters.split(",") if r.strip()]

    print("Loading candidates...")
    candidates, coverage_lines = load_candidates(
        DEFAULT_SCORED_DIR, args.scored_glob, candidates_filter, Path(args.generated_dir)
    )
    print(f"  {len(candidates)} candidate(s) loaded")
    for line in coverage_lines:
        print(f"  {line}")
    (out_dir / "coverage_report.txt").write_text("\n".join(coverage_lines) + "\n", encoding="utf-8")

    routing = route_questions(args.benchmark)
    partial_qnums = sorted(routing.partial.keys(), key=int)
    print(f"Benchmark partial-credit questions: {len(partial_qnums)}")

    print("Building candidate-pair population...")
    pop = build_population(candidates, partial_qnums)
    print(f"  {len(pop)} usable (question, candidate-pair) combinations")
    if not pop:
        raise SystemExit("No usable candidate pairs -- check coverage_report.txt")

    plot_distributions(candidates, pop, out_dir)
    median_x, below_edges, above_edges = assign_strata(pop)
    assign_midpoint_tertiles(pop)

    if args.dry_run:
        write_sampling_summary(out_dir, coverage_lines, pop, median_x, below_edges,
                               above_edges, balance_log=None, master=None)
        print(f"Dry run complete. See {out_dir}/distribution_delta_logit.png, "
              f"{out_dir}/sampling_summary.md, {out_dir}/coverage_report.txt")
        return

    pairs_per_stratum = len(list(itertools.combinations(raters, 2)))
    n_strata = N_BELOW_MEDIAN_STRATA + N_ABOVE_MEDIAN_STRATA
    print(f"Selecting {pairs_per_stratum} items per stratum x {n_strata} strata "
          f"= {pairs_per_stratum * n_strata} pairs...")
    selected_by_stratum, balance_log = select_items(pop, args.seed, pairs_per_stratum, n_strata)
    for line in balance_log:
        print(f"  {line}")

    master = assign_dyads_and_sides(selected_by_stratum, raters, args.seed)
    print(f"Assigned {len(master)} pairs across {len(raters)} raters "
          f"({len(list(itertools.combinations(raters, 2)))} dyads).")

    master_path = out_dir / "master_pairs.jsonl"
    with open(master_path, "w", encoding="utf-8") as fh:
        for row in master:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"  wrote {master_path} ({len(master)} lines) -- privileged, do not distribute")

    write_rater_files(master, candidates, raters, args.seed, out_dir)
    write_sampling_summary(out_dir, coverage_lines, pop, median_x, below_edges,
                           above_edges, balance_log, master)
    print(f"Done. See {out_dir}/sampling_summary.md for the full report.")


if __name__ == "__main__":
    main()
