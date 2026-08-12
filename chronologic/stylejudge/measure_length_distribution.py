"""
measure_length_distribution.py

Phase A of the style judge (see new-style-judge-spec.md and phase-a-plan.md).

Measures the length distribution of the texts the style judge will actually have to
score in production -- free-generation answers to benchmark questions that pass the
existing triage rule in bertclassify/free_gen_triage.py -- and mixes in a proportional
share of the longer, newer manual questions.

Emits stylejudge/length_distribution.json, a joint (sentences, words) sampling table
that Phase B (historical passage sampling) and Phase D (LLM elicitation) both consume
via sample_length().

Run from the repo root:

    python stylejudge/measure_length_distribution.py
"""

import argparse
import glob
import json
import os
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime

import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_ANSWERS_DIR = "modelasjudge/generated_answers"
DEFAULT_ANSWERS_GLOB = "*0.4*.json"
DEFAULT_BENCHMARK = "booksample/chronologic_en_0.4.jsonl"
DEFAULT_MANUAL_GLOB = "booksample/manual/process_files/*_manualquestions.jsonl"
DEFAULT_EXCLUDE = ["deepseek-r1-distill-llama-70b"]
DEFAULT_MANUAL_FRACTION = 0.12

MIN_WORDS = 5           # the triage floor, from free_gen_triage.py:119-126
PROJECTED_MANUAL = 50   # ~50 more manual questions expected beyond the 51 on disk

# Word bins for the joint sampling table: fine where the mass is, coarse in the tail.
WORD_BIN_EDGES = [5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 100, 130, 170]

# Sentence counts above this are pooled into a single top bucket.
MAX_SENTENCES = 5


# --------------------------------------------------------------------------
# measurement helpers (ported from bertclassify/length_distribution.py)
# --------------------------------------------------------------------------

def count_words(s):
    return len(s.split())


def count_sentences(s):
    """Number of sentence units, always >= 1 for non-empty text.

    bertclassify/length_distribution.py collapsed "starts lowercase OR doesn't end in
    terminal punctuation" to a sentence count of 0.  That conflates two different
    things, and eyeballing the surviving answers shows why it matters: a large share of
    the free-gen answers are simply truncated by max_tokens mid-sentence.  Those are
    still two- or three-sentence answers; only their last unit is cut off.  So sentence
    count is measured straight, and the two conditions are reported separately by
    is_fragment() and is_truncated().
    """
    s = s.strip()
    if not s:
        return 0
    return len(nltk.sent_tokenize(s))


def _first_alpha(s):
    """First alphabetic character, skipping quotes, digits, and dashes."""
    for ch in s:
        if ch.isalpha():
            return ch
    return ""


def is_fragment(s):
    """True for a sub-sentential continuation -- the shape of a cloze answer.

    Tested on the first *alphabetic* character so that answers opening with a quotation
    mark, a stray page number, or a dash are not misread as lowercase-initial.
    """
    s = s.strip()
    if not s:
        return False
    ch = _first_alpha(s)
    return bool(ch) and ch.islower() and count_sentences(s) <= 1


def is_truncated(s):
    """True when the text does not end in terminal punctuation.

    Diagnostic only.  It mixes token-limit truncation with cloze fills that
    legitimately stop mid-sentence, so it is reported, not filtered on.
    """
    s = s.strip().rstrip('"\'”’)]')
    return bool(s) and s[-1] not in '.!?'


# --------------------------------------------------------------------------
# pre-normalization -- Phase C (stylejudge/normalize.py)
# --------------------------------------------------------------------------

# This used to be a local prenormalize(); its docstring asked to be replaced by
# a call into the full normalization suite once that existed. It does now, so
# measurement and production scoring share one code path.

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import clean_model_answer   # noqa: E402


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_benchmark(path):
    """Return {qnum: record} from a benchmark JSONL."""
    bench = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            bench[str(rec.get("question_number", ""))] = rec
    return bench


def model_label(path):
    """Filename-derived label.

    The `model` field is not unique across files: gpt-5.4 appears twice with different
    reasoning_effort, and Qwen2.5-7B-Instruct appears twice (base vs. finetune).
    """
    stem = os.path.basename(path)
    stem = stem[:-len(".json")] if stem.endswith(".json") else stem
    if stem.startswith("free_gen_"):
        stem = stem[len("free_gen_"):]
    return stem


def load_answer_files(answers_dir, pattern, exclude):
    paths = sorted(glob.glob(os.path.join(answers_dir, pattern)))
    kept = []
    for p in paths:
        label = model_label(p)
        if any(x in label or x in os.path.basename(p) for x in exclude):
            print(f"  excluding {label} (matched --exclude-model)")
            continue
        with open(p) as f:
            data = json.load(f)
        kept.append((label, p, data))
    return kept


# --------------------------------------------------------------------------
# triage (ported from bertclassify/free_gen_triage.py:119-126)
# --------------------------------------------------------------------------

def triage_reason(entry, bench_rec):
    """Return the reason this answer is NOT eligible for style judgment, or None."""
    gts = entry.get("ground_truths") or []
    if isinstance(gts, str):          # older adapter output
        gts = [gts]
    ground_truth = gts[0] if gts else entry.get("ground_truth", "")
    model_answer = entry.get("answer", "")
    reasoning_type = entry.get("reasoning_type", "")
    answer_length = (bench_rec or {}).get("answer_length", "")

    if count_words(ground_truth) < MIN_WORDS:
        return "short_ground_truth"
    if count_words(model_answer) < MIN_WORDS:
        return "short_answer"
    if reasoning_type == "abstention":
        return "abstention"
    if answer_length == "short_answer":
        return "short_answer_length"
    return None


# --------------------------------------------------------------------------
# stats
# --------------------------------------------------------------------------

def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    idx = q * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def summarize(words):
    s = sorted(words)
    return {
        "n": len(s),
        "mean_words": round(statistics.mean(s), 1) if s else None,
        "median_words": quantile(s, 0.5),
        "p10_words": quantile(s, 0.10),
        "p25_words": quantile(s, 0.25),
        "p75_words": quantile(s, 0.75),
        "p90_words": quantile(s, 0.90),
        "max_words": s[-1] if s else None,
    }


def weighted_quantiles(pairs, qs):
    """pairs: list of (value, weight), weights need not be normalized."""
    if not pairs:
        return {}
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    out = {}
    cum = 0.0
    i = 0
    for q in qs:
        target = q * total
        while i < len(pairs) - 1 and cum + pairs[i][1] < target:
            cum += pairs[i][1]
            i += 1
        out[str(q)] = pairs[i][0]
    return out


def word_bin(w):
    """Return (lo, hi) for a word count, clamped to the outermost bins."""
    edges = WORD_BIN_EDGES
    if w < edges[0]:
        return (edges[0], edges[1])
    for lo, hi in zip(edges, edges[1:]):
        if lo <= w < hi:
            return (lo, hi)
    return (edges[-2], edges[-1])


# --------------------------------------------------------------------------
# sampling helper -- the point of the whole exercise
# --------------------------------------------------------------------------

def sample_length(table, rng=None):
    """Draw a length target from a `joint` table.

    `table` is the list under the "joint" key of length_distribution.json.
    Returns (sentences, words, fragment), where `fragment` is True when the target
    should be a sub-sentential continuation rather than a complete sentence.
    Words are drawn uniformly within the selected bin.
    """
    rng = rng or random
    r = rng.random()
    cum = 0.0
    cell = table[-1]
    for entry in table:
        cum += entry["weight"]
        if r <= cum:
            cell = entry
            break
    lo, hi = cell["word_bin"]
    words = rng.randint(lo, max(lo, hi - 1))
    fragment = rng.random() < cell.get("fragment_share", 0.0)
    return cell["sentences"], words, fragment


# --------------------------------------------------------------------------
# plotting
# --------------------------------------------------------------------------

def make_plot(pooled, manual, mixture_pairs, out_path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import gaussian_kde

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    series = [
        ([r[0] for r in pooled], [r[-1] for r in pooled],
         "Model answers (0.4, equal-weight)", "steelblue"),
        ([r[0] for r in manual], [r[-1] for r in manual],
         "New manual questions (GT)", "seagreen"),
        ([r[0] for r in mixture_pairs], [r[-1] for r in mixture_pairs],
         "Final target mixture", "darkorange"),
    ]

    for vals, wts, label, color in series:
        if len(set(vals)) < 3:
            continue
        arr = np.array(vals, dtype=float)
        kde = gaussian_kde(arr, bw_method='scott', weights=np.array(wts, dtype=float))
        x = np.linspace(0, 175, 500)
        style = '-' if label.startswith("Final") else '--'
        lw = 2.6 if label.startswith("Final") else 1.8
        ax1.plot(x, kde(x), label=label, color=color, linewidth=lw, linestyle=style)
        if label.startswith("Final"):
            ax1.fill_between(x, kde(x), alpha=0.15, color=color)

    ax1.set_xlabel("Words", fontsize=12)
    ax1.set_ylabel("Density", fontsize=12)
    ax1.set_title("Word-count distribution", fontsize=13)
    ax1.legend(fontsize=9)
    ax1.set_xlim(0, 175)

    # sentence-count panel
    buckets = list(range(1, MAX_SENTENCES + 1))
    width = 0.38
    for offset, data, label, color in (
            (-width / 2, pooled, "Model answers (0.4, equal-weight)", "steelblue"),
            (width / 2, mixture_pairs, "Final target mixture", "darkorange")):
        total = sum(r[-1] for r in data)
        heights = [sum(r[-1] for r in data if min(r[1], MAX_SENTENCES) == b) / total
                   if total else 0 for b in buckets]
        ax2.bar([b + offset for b in buckets], heights, width=width,
                label=label, color=color, alpha=0.85)

    ax2.set_xticks(buckets)
    ax2.set_xticklabels([str(b) if b < MAX_SENTENCES else f"{MAX_SENTENCES}+"
                         for b in buckets])
    ax2.set_xlabel("Sentences", fontsize=12)
    ax2.set_ylabel("Share", fontsize=12)
    ax2.set_title("Sentence-count distribution", fontsize=13)
    ax2.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"\nPlot written to {out_path}")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--answers-dir", default=DEFAULT_ANSWERS_DIR)
    ap.add_argument("--answers-glob", default=DEFAULT_ANSWERS_GLOB)
    ap.add_argument("--benchmark", default=DEFAULT_BENCHMARK)
    ap.add_argument("--manual-glob", default=DEFAULT_MANUAL_GLOB)
    ap.add_argument("--exclude-model", action="append", default=None,
                    help="substring of a filename to drop; repeatable "
                         f"(default: {DEFAULT_EXCLUDE})")
    ap.add_argument("--manual-fraction", type=float, default=DEFAULT_MANUAL_FRACTION,
                    help="share of the final mixture drawn from new manual questions")
    ap.add_argument("--out", default="stylejudge/length_distribution.json")
    ap.add_argument("--plot", default="stylejudge/length_distribution.png")
    ap.add_argument("--report", default="stylejudge/length_distribution_report.md")
    ap.add_argument("--show-samples", type=int, default=0,
                    help="print N random surviving answers for eyeballing")
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--seed", type=int, default=1914)
    args = ap.parse_args()

    exclude = args.exclude_model if args.exclude_model is not None else DEFAULT_EXCLUDE
    rng = random.Random(args.seed)

    print(f"Loading benchmark: {args.benchmark}")
    bench = load_benchmark(args.benchmark)
    print(f"  {len(bench)} questions")

    print(f"Loading answers: {args.answers_dir}/{args.answers_glob}")
    files = load_answer_files(args.answers_dir, args.answers_glob, exclude)
    if not files:
        sys.exit("No answer files matched.")
    print(f"  {len(files)} files kept")

    # ---- measure -------------------------------------------------------
    per_model = {}          # label -> list of (words, sentences, fragment)
    per_model_meta = {}
    excluded_by_reason = Counter()
    excluded_by_reason_model = defaultdict(Counter)
    kept_texts = []
    n_raw = 0
    n_unterminated = 0
    frag_by_category = defaultdict(lambda: [0, 0])   # category -> [fragments, total]

    for label, path, data in files:
        kept = []
        for qnum, entry in data["answers"].items():
            n_raw += 1
            bench_rec = bench.get(str(qnum))
            reason = triage_reason(entry, bench_rec)
            if reason:
                excluded_by_reason[reason] += 1
                excluded_by_reason_model[label][reason] += 1
                continue
            text = clean_model_answer(entry.get("answer", ""))
            if count_words(text) < MIN_WORDS:
                # prenormalization can drop a borderline answer below the floor
                excluded_by_reason["short_after_normalization"] += 1
                excluded_by_reason_model[label]["short_after_normalization"] += 1
                continue
            frag = is_fragment(text)
            kept.append((count_words(text), count_sentences(text), frag))
            n_unterminated += is_truncated(text)
            cat = (bench_rec or {}).get("question_category", "unknown")
            frag_by_category[cat][0] += frag
            frag_by_category[cat][1] += 1
            kept_texts.append((label, qnum, text))
        per_model[label] = kept
        per_model_meta[label] = {
            "model": data.get("model"),
            "reasoning_effort": data.get("reasoning_effort"),
            "file": path,
        }

    n_models = len(per_model)
    print(f"\nRaw answers: {n_raw}")
    print(f"Excluded:    {sum(excluded_by_reason.values())} "
          f"({100 * sum(excluded_by_reason.values()) / n_raw:.1f}%)")
    for reason, c in excluded_by_reason.most_common():
        print(f"  {reason:28s} {c:5d}")

    n_kept = sum(len(v) for v in per_model.values())
    print(f"Unterminated (no final .!?): {n_unterminated} "
          f"({100 * n_unterminated / max(n_kept, 1):.1f}%) -- kept, since production "
          f"scores these strings too")

    # ---- pooled, equal weight per model --------------------------------
    pooled = []   # (words, sentences, fragment, weight)
    for label, triples in per_model.items():
        if not triples:
            continue
        w = 1.0 / (n_models * len(triples))
        pooled.extend((wc, sc, fr, w) for wc, sc, fr in triples)

    # ---- manual questions ----------------------------------------------
    manual_paths = sorted(glob.glob(args.manual_glob))
    manual_seen = set()
    manual_lengths = []
    for p in manual_paths:
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                strings = rec.get("answer_strings") or []
                if not strings:
                    continue
                gt = clean_model_answer(strings[0])
                key = rec.get("main_question", "") + "||" + gt[:80]
                if key in manual_seen:
                    continue
                manual_seen.add(key)
                if count_words(gt) < MIN_WORDS:
                    continue
                manual_lengths.append(
                    (count_words(gt), count_sentences(gt), is_fragment(gt)))

    print(f"\nManual questions: {len(manual_paths)} files, "
          f"{len(manual_lengths)} usable ground truths "
          f"(+{PROJECTED_MANUAL} projected)")

    manual = []
    if manual_lengths:
        w = 1.0 / len(manual_lengths)
        manual = [(wc, sc, fr, w) for wc, sc, fr in manual_lengths]

    # ---- mixture --------------------------------------------------------
    f = args.manual_fraction if manual else 0.0
    mixture = ([(wc, sc, fr, wt * (1 - f)) for wc, sc, fr, wt in pooled] +
               [(wc, sc, fr, wt * f) for wc, sc, fr, wt in manual])
    total_w = sum(wt for *_r, wt in mixture)
    mixture = [(wc, sc, fr, wt / total_w) for wc, sc, fr, wt in mixture]

    # ---- joint table ----------------------------------------------------
    cells = defaultdict(float)
    cell_frag = defaultdict(float)
    for wc, sc, fr, wt in mixture:
        key = (min(sc, MAX_SENTENCES), word_bin(wc))
        cells[key] += wt
        if fr:
            cell_frag[key] += wt
    joint = [{"sentences": s, "word_bin": list(b), "weight": w,
              "fragment_share": round(cell_frag[(s, b)] / w, 4) if w else 0.0}
             for (s, b), w in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1]))]
    jt = sum(e["weight"] for e in joint)
    joint = [dict(e, weight=e["weight"] / jt) for e in joint]

    sent_hist = defaultdict(float)
    for wc, sc, fr, wt in mixture:
        sent_hist[min(sc, MAX_SENTENCES)] += wt
    fragment_rate = sum(wt for _wc, _sc, fr, wt in mixture if fr)

    qs = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    mixture_q = weighted_quantiles([(wc, wt) for wc, _sc, _fr, wt in mixture], qs)
    pooled_q = weighted_quantiles([(wc, wt) for wc, _sc, _fr, wt in pooled], qs)

    # ---- per-model summaries -------------------------------------------
    per_model_out = {}
    for label, triples in per_model.items():
        summ = summarize([wc for wc, _s, _f in triples])
        hist = Counter(min(sc, MAX_SENTENCES) for _w, sc, _f in triples)
        n = len(triples) or 1
        summ["sentence_hist"] = {str(k): round(v / n, 4) for k, v in sorted(hist.items())}
        summ["fragment_rate"] = round(sum(1 for *_x, fr in triples if fr) / n, 4)
        summ.update(per_model_meta[label])
        summ["excluded"] = dict(excluded_by_reason_model[label])
        per_model_out[label] = summ

    # ---- validation cross-tab: fragments should track cloze categories ---
    frag_cat = {
        cat: {"fragment_rate": round(fr / tot, 3), "n": tot}
        for cat, (fr, tot) in sorted(frag_by_category.items(),
                                     key=lambda kv: -kv[1][0] / max(kv[1][1], 1))
    }

    # ---- emit -----------------------------------------------------------
    out = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "generator": "stylejudge/measure_length_distribution.py",
        "sources": {
            "answers_dir": args.answers_dir,
            "answers_glob": args.answers_glob,
            "answer_files": [p for _l, p, _d in files],
            "excluded_models": exclude,
            "benchmark": args.benchmark,
            "manual_glob": args.manual_glob,
            "manual_files": len(manual_paths),
        },
        "eligibility_rule": (
            "ported from bertclassify/free_gen_triage.py:119-126 -- "
            "drop if GT < 5 words, answer < 5 words, reasoning_type == 'abstention', "
            "or benchmark answer_length == 'short_answer'"
        ),
        "manual_fraction": f,
        "projected_manual_questions": PROJECTED_MANUAL,
        "n_raw": n_raw,
        "n_pooled": len(pooled),
        "n_manual": len(manual),
        "n_models": n_models,
        "excluded_by_reason": dict(excluded_by_reason),
        "unterminated_rate": round(n_unterminated / max(n_kept, 1), 4),
        "fragment_rate": round(fragment_rate, 4),
        "fragment_rate_by_category": frag_cat,
        "per_model": per_model_out,
        "pooled_words_quantiles": {k: round(v, 1) for k, v in pooled_q.items()},
        "words_quantiles": {k: round(v, 1) for k, v in mixture_q.items()},
        "sentence_hist": {str(k): round(v, 4) for k, v in sorted(sent_hist.items())},
        "word_bin_edges": WORD_BIN_EDGES,
        "joint": [dict(e, weight=round(e["weight"], 6)) for e in joint],
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nDistribution written to {args.out}")

    # ---- report ---------------------------------------------------------
    write_report(args.report, out, per_model_out, mixture_q, pooled_q, sent_hist,
                 excluded_by_reason, n_raw)
    print(f"Report written to {args.report}")

    if not args.no_plot:
        make_plot(pooled, manual, mixture, args.plot)

    if args.show_samples:
        print(f"\n--- {args.show_samples} random surviving answers ---")
        for label, qnum, text in rng.sample(kept_texts,
                                            min(args.show_samples, len(kept_texts))):
            flags = []
            if is_fragment(text):
                flags.append("fragment")
            if is_truncated(text):
                flags.append("truncated")
            print(f"\n[{label} q{qnum}] ({count_words(text)}w, "
                  f"{count_sentences(text)}s{', ' + ', '.join(flags) if flags else ''})"
                  f"\n{text}")

    # ---- console summary ------------------------------------------------
    print("\n=== Fragment rate by question category (validation) ===")
    for cat, d in list(frag_cat.items())[:6]:
        print(f"  {cat:38s} {d['fragment_rate']:.2f}  (n={d['n']})")
    print("  ...")
    for cat, d in list(frag_cat.items())[-4:]:
        print(f"  {cat:38s} {d['fragment_rate']:.2f}  (n={d['n']})")

    print("\n=== Final target mixture ===")
    for q in qs:
        print(f"  p{int(q * 100):>2}  {mixture_q[str(q)]:6.1f} words")
    print("  sentences: " + "  ".join(
        f"{k if k < MAX_SENTENCES else str(k) + '+'}={v:.1%}"
        for k, v in sorted(sent_hist.items())))
    print(f"  fragments: {fragment_rate:.1%}")


def write_report(path, out, per_model_out, mixture_q, pooled_q, sent_hist,
                 excluded_by_reason, n_raw):
    L = []
    a = L.append
    a("# Target length distribution for the style judge\n")
    a(f"Generated {out['generated']} by `{out['generator']}`.\n")
    a("Measures the lengths of free-generation model answers that are actually eligible "
      "for style judgment, then mixes in a proportional share of the newer, longer "
      "manual questions. The result is the length distribution that Phase B historical "
      "passages and Phase D LLM imitations should match.\n")

    a("## Eligibility\n")
    a(f"{out['eligibility_rule']}\n")
    a(f"Raw answers: **{n_raw}** ({out['n_models']} models x 712 questions). "
      f"Excluded: **{sum(excluded_by_reason.values())}** "
      f"({100 * sum(excluded_by_reason.values()) / n_raw:.1f}%). "
      f"Surviving: **{out['n_pooled']}**.\n")
    a("| Exclusion reason | n |")
    a("|---|---|")
    for reason, c in excluded_by_reason.most_common():
        a(f"| `{reason}` | {c} |")
    a("")
    a("For comparison, the independent `discrim_*` reliability gate "
      "(`r_q > 0.70`) drops 262 of 712 questions, ~37%.\n")

    a("## Per-model answer lengths (post-filter)\n")
    a("| Model file | n | mean | p10 | median | p90 | max | 1s | 2s | 3s+ | frag |")
    a("|---|---|---|---|---|---|---|---|---|---|---|")
    for label, s in sorted(per_model_out.items(),
                           key=lambda kv: kv[1]["median_words"] or 0):
        h = s["sentence_hist"]
        three_plus = sum(v for k, v in h.items() if int(k) >= 3)
        a(f"| `{label}` | {s['n']} | {s['mean_words']} | {s['p10_words']:.0f} | "
          f"{s['median_words']:.0f} | {s['p90_words']:.0f} | {s['max_words']} | "
          f"{h.get('1', 0):.0%} | {h.get('2', 0):.0%} | "
          f"{three_plus:.0%} | {s['fragment_rate']:.0%} |")
    a("")
    a(f"Models are pooled with **equal weight each** "
      f"({', '.join(out['sources']['excluded_models'])} excluded).\n")

    a("## The mixture\n")
    a(f"Final = {1 - out['manual_fraction']:.2f} x pooled model answers + "
      f"{out['manual_fraction']:.2f} x new manual ground truths "
      f"({out['n_manual']} on disk + ~{out['projected_manual_questions']} projected, "
      f"against a 712-question base).\n")
    a("| quantile | pooled answers | final mixture |")
    a("|---|---|---|")
    for q in ["0.05", "0.1", "0.25", "0.5", "0.75", "0.9", "0.95", "0.99"]:
        if q in mixture_q:
            a(f"| p{int(float(q) * 100)} | {pooled_q[q]:.0f} | {mixture_q[q]:.0f} |")
    a("")
    a("| sentences | share of mixture |")
    a("|---|---|")
    for k, v in sorted(sent_hist.items()):
        lab = f"{k}+" if k >= MAX_SENTENCES else str(k)
        a(f"| {lab} | {v:.1%} |")
    a("")

    a("## Fragments and truncation\n")
    a("Two things the earlier `bertclassify/length_distribution.py` conflated into a "
      "sentence count of 0:\n")
    a(f"- **Fragments** ({out['fragment_rate']:.1%} of the mixture): genuinely "
      "sub-sentential continuations, the shape of a cloze answer. Detected as "
      "lowercase on the first *alphabetic* character (skipping quotes, digits, dashes) "
      "with a single sentence unit. These are a real feature of the target and Phase D "
      "must be able to elicit them.")
    a(f"- **Unterminated endings** ({out['unterminated_rate']:.1%} of surviving "
      "answers): the text does not end in `.`/`!`/`?`. Almost all of these end on a "
      "letter, and they are a mix of token-limit truncation and cloze fills that "
      "legitimately stop mid-sentence. They are kept -- the production style judge "
      "scores these same strings -- and their word counts remain valid; only a "
      "sentence count of 0 would have been wrong.\n")
    a("Validation cross-tab. If the fragment flag is measuring cloze-ness rather than "
      "truncation, cloze categories should dominate the top of this table and "
      "character/parallax categories the bottom:\n")
    a("| question_category | fragment rate | n |")
    a("|---|---|---|")
    for cat, d in out["fragment_rate_by_category"].items():
        a(f"| `{cat}` | {d['fragment_rate']:.2f} | {d['n']} |")
    a("")

    a("## What Phase B and D should sample\n")
    p50 = mixture_q.get("0.5")
    p90 = mixture_q.get("0.9")
    a(f"Historical passages and elicited imitations should center near **{p50:.0f} words** "
      f"with a real tail out past **{p90:.0f}** (p90). "
      f"About **{out['fragment_rate']:.0%}** of targets are sub-sentential fragments "
      "rather than complete sentences -- Phase D infill and paraphrase prompts need to "
      "be able to request those, not only whole sentences.\n")
    a("Do not sample the dimensions independently. Use the `joint` table in "
      "`length_distribution.json` via `sample_length()` in "
      "`measure_length_distribution.py`, which returns a coherent "
      "`(sentences, words, fragment)` triple.\n")

    with open(path, "w") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
