#!/usr/bin/env python3
"""sample_passages.py — Phase D1 passage sampling for the style judge.

See stylejudge/phase-d1-plan.md. Turns corpus_roster.csv into two on-disk
.jsonl artifacts under ~/workdata/chronologic-dating-corpus/passages/:

    positive_passages.jsonl  — dated positive passages (date predictor
                                 union authenticity-detector positives)
    elicitation_prep.jsonl   — negative-sample templates for Phase D2
                                 (infill bookends, few-shot sentence sets)

D1 is offline-only: no LLM calls anywhere. No source file is ever opened in
write mode. Library-first, per Phase C's contract: `normalize_corpus_text`,
`rejection_reason`, and `sample_length` are imported, never re-implemented.

Run from stylejudge/:

    python sample_passages.py all --decades 1830-1839 --target-per-decade 50 \\
        --infill-target 20 --fewshot-target 20 --out-dir /tmp/dryrun
    python sample_passages.py report --positives-in /tmp/dryrun/positive_passages.jsonl
"""

import argparse
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from normalize import normalize_corpus_text, load_lexicon, load_roster, read_volume  # noqa: E402
from passage_filters import rejection_reason                                          # noqa: E402
from measure_length_distribution import sample_length, count_words, count_sentences   # noqa: E402

import nltk  # noqa: E402  (punkt availability already ensured by measure_length_distribution)

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

DEFAULT_SEED = 20260809          # reuse fetch_idi_fill.py's project-wide seed
DEFAULT_MAX_PER_VOLUME = 12      # per-decade / per-supplement round-robin cap
CAP_INCREMENT = 5                # overflow relaxation step when a decade can't hit target at the cap
DEFAULT_TARGET_PER_DECADE = 2000
DEFAULT_MARGIN = 0.05
DEFAULT_MAX_DRAW_TRIES = 25      # per-passage redraw budget before giving up on one slot
DEFAULT_POSITIVE_TARGET = 32000
DEFAULT_FRAGMENT_MIN_WORDS = 6
DEFAULT_GAP_SIZES = (1, 2, 3)
DEFAULT_BOOKEND_SENTENCES = 2
DEFAULT_INFILL_TARGET = 12800     # 40% of 32,000, matches D2's modality weight
DEFAULT_INFILL_MAX_PER_VOLUME = 4
DEFAULT_FEWSHOT_MIN_WORDS = 11
DEFAULT_FEWSHOT_TARGET = 3200     # 10% of 32,000
DEFAULT_FEWSHOT_MAX_PER_VOLUME = 3
DEFAULT_MAX_WORD_ATTEMPTS = 15    # few-shot: word-retry budget per volume

AUTHENTICITY_DATE_LO = 1831
AUTHENTICITY_DATE_HI = 1930

DEFAULT_LENGTH_TABLE = SCRIPT_DIR / "length_distribution.json"
DEFAULT_OUT_ROOT = Path.home() / "workdata" / "chronologic-dating-corpus" / "passages"
DEFAULT_POSITIVES_PATH = DEFAULT_OUT_ROOT / "positive_passages.jsonl"
DEFAULT_ELICITATION_PATH = DEFAULT_OUT_ROOT / "elicitation_prep.jsonl"

# Fry/Oxford "first 100" instructional word list. No ranked-frequency source
# exists elsewhere in this repo: normalize.py's lexicon is a 174k-word
# dictionary for OOV/dehyphenation checks, unranked; nltk.corpus.stopwords is
# a different, non-ranked ~127-word set. Hardcoded here, offline, no new
# dependency.
TOP100_ENGLISH_WORDS = frozenset({
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
    "he", "was", "for", "on", "are", "as", "with", "his", "they", "i",
    "at", "be", "this", "have", "from", "or", "one", "had", "by", "word",
    "but", "not", "what", "all", "were", "we", "when", "your", "can", "said",
    "there", "use", "an", "each", "which", "she", "do", "how", "their", "if",
    "will", "up", "other", "about", "out", "many", "then", "them", "these", "so",
    "some", "her", "would", "make", "like", "him", "into", "time", "has", "look",
    "two", "more", "write", "go", "see", "number", "no", "way", "could", "people",
    "my", "than", "first", "water", "been", "call", "who", "oil", "its", "now",
    "find", "long", "down", "day", "did", "get", "come", "made", "may", "part",
})

_WORD_RE = re.compile(r"[A-Za-z']+")


# ---------------------------------------------------------------------------
# volume-level primitives
# ---------------------------------------------------------------------------

@dataclass
class Sentence:
    text: str
    start: int
    end: int


@dataclass
class VolumeIndex:
    text: str
    sentences: list
    eligible_index_range: tuple   # (lo, hi), half-open, into `sentences`
    collection: str
    volume_id: str
    date: int
    decade: int


def load_and_split_volume(row, lexicon, margin=DEFAULT_MARGIN):
    """Normalize a whole volume once, sentence-split it, and margin-trim it.

    Sentence offsets are recovered by incremental `text.find(sentence, pos)`:
    safe because `sent_tokenize` only splits, never rewrites, so each sentence
    is a literal substring of `text` in order.
    """
    raw = read_volume(row["path"])
    text = normalize_corpus_text(raw, row["collection"], lexicon)
    sent_texts = nltk.sent_tokenize(text) if text else []

    sentences = []
    pos = 0
    for s in sent_texts:
        start = text.find(s, pos)
        if start == -1:
            start = pos  # pathological: fall back rather than crash
        end = start + len(s)
        sentences.append(Sentence(s, start, end))
        pos = end

    n = len(text)
    low, high = margin * n, (1 - margin) * n
    lo_idx = len(sentences)
    for i, sent in enumerate(sentences):
        if sent.start >= low:
            lo_idx = i
            break
    hi_idx = 0
    for i, sent in enumerate(sentences):
        if sent.end <= high:
            hi_idx = i + 1
    eligible_index_range = (lo_idx, max(hi_idx, lo_idx))

    return VolumeIndex(
        text=text, sentences=sentences, eligible_index_range=eligible_index_range,
        collection=row["collection"], volume_id=row["volume_id"],
        date=int(row["date"]), decade=int(row["decade"]),
    )


class VolumeCache:
    """Lazy per-volume-id VolumeIndex cache, shared across draws in a run.

    Deviation from the plan's literal "cache for the duration of that volume's
    draws, then discard": the spread-round-robin scheduler revisits volumes
    across passes, so the cache is kept for the life of the stage (or, when a
    single cache is threaded through `all`, for the whole run) rather than
    discarded after one volume's slots are filled. This is the tradeoff
    documented in NOTES.md — correctness and one-normalize-per-volume are
    preserved; the strict per-volume memory bound is not.
    """

    def __init__(self, lexicon, margin=DEFAULT_MARGIN):
        self.lexicon = lexicon
        self.margin = margin
        self._cache = {}

    def get(self, row):
        vid = row["volume_id"]
        if vid not in self._cache:
            self._cache[vid] = load_and_split_volume(row, self.lexicon, self.margin)
        return self._cache[vid]


# ---------------------------------------------------------------------------
# passage drawing
# ---------------------------------------------------------------------------

@dataclass
class Passage:
    text: str
    target_sentences: int
    target_words: int
    fragment: bool
    n_sentences: int
    n_words: int
    char_start: int
    char_end: int
    volume_id: str
    collection: str
    date: int
    decade: int
    draw_tries: int
    fallback: bool = False
    purposes: list = field(default_factory=list)

    @property
    def span(self):
        return (self.char_start, self.char_end)

    @property
    def passage_id(self):
        return f"{self.volume_id}_{self.char_start}_{self.char_end}"


def _bump(stats, key):
    if stats is not None:
        stats[key] = stats.get(key, 0) + 1


def draw_fragment(vindex, rng, lexicon, min_words=DEFAULT_FRAGMENT_MIN_WORDS,
                   max_tries=DEFAULT_MAX_DRAW_TRIES, exclude_spans=None, stats=None):
    """Sub-sentential continuation: cut after the last comma, keep comma->end."""
    lo, hi = vindex.eligible_index_range
    if hi <= lo:
        return None
    exclude_spans = exclude_spans if exclude_spans is not None else set()

    for tries in range(1, max_tries + 1):
        i = rng.randrange(lo, hi)
        sent = vindex.sentences[i]
        comma = sent.text.rfind(",")
        if comma == -1:
            _bump(stats, "fragment_no_comma")
            continue
        raw_candidate = sent.text[comma + 1:]
        candidate = raw_candidate.strip()
        if count_words(candidate) <= min_words:
            _bump(stats, "fragment_too_short")
            continue
        lstripped = len(raw_candidate) - len(raw_candidate.lstrip())
        start = sent.start + comma + 1 + lstripped
        end = sent.end
        if (start, end) in exclude_spans:
            _bump(stats, "duplicate_span")
            continue
        reason = rejection_reason(candidate, lexicon)
        if reason is not None:
            _bump(stats, reason)
            continue
        return Passage(
            text=candidate, target_sentences=1, target_words=count_words(candidate),
            fragment=True, n_sentences=count_sentences(candidate), n_words=count_words(candidate),
            char_start=start, char_end=end, volume_id=vindex.volume_id,
            collection=vindex.collection, date=vindex.date, decade=vindex.decade,
            draw_tries=tries,
        )
    return None


def _window_span(vindex, i, n):
    first, last = vindex.sentences[i], vindex.sentences[i + n - 1]
    return vindex.text[first.start:last.end], first.start, last.end


def draw_window(vindex, sentences, words, fragment, rng, lexicon, exclude_spans=None,
                 max_tries=DEFAULT_MAX_DRAW_TRIES, fragment_min_words=DEFAULT_FRAGMENT_MIN_WORDS,
                 stats=None):
    """One passage-draw attempt for a (sentences, words, fragment) length target.

    Dispatches to the fragment recipe when `fragment` is True; if the
    fragment-draw budget is exhausted, falls back to an ordinary window draw
    for the same target rather than dropping the slot (fragments are a
    minority per the joint table, so an occasional substitution doesn't
    distort it).
    """
    exclude_spans = exclude_spans if exclude_spans is not None else set()
    fallback = False
    if fragment:
        p = draw_fragment(vindex, rng, lexicon, min_words=fragment_min_words,
                           max_tries=max_tries, exclude_spans=exclude_spans, stats=stats)
        if p is not None:
            return p
        fallback = True
        _bump(stats, "fragment_fallback")

    lo, hi = vindex.eligible_index_range
    span_len = hi - lo
    if span_len < 1:
        return None
    n_target = max(1, min(sentences, span_len))

    for tries in range(1, max_tries + 1):
        max_start = hi - n_target
        if max_start < lo:
            n_target -= 1
            if n_target < 1:
                return None
            continue
        i = rng.randrange(lo, max_start + 1)
        best = None
        for cand_n in (n_target - 1, n_target, n_target + 1):
            if cand_n < 1 or i + cand_n > hi:
                continue
            wtext, start, end = _window_span(vindex, i, cand_n)
            wwords = count_words(wtext)
            diff = abs(wwords - words)
            if best is None or diff < best[0]:
                best = (diff, cand_n, wtext, start, end, wwords)
        if best is None:
            continue
        _, cand_n, wtext, start, end, wwords = best
        if (start, end) in exclude_spans:
            _bump(stats, "duplicate_span")
            continue
        reason = rejection_reason(wtext, lexicon)
        if reason is not None:
            _bump(stats, reason)
            continue
        return Passage(
            text=wtext, target_sentences=sentences, target_words=words, fragment=False,
            n_sentences=count_sentences(wtext), n_words=wwords, char_start=start, char_end=end,
            volume_id=vindex.volume_id, collection=vindex.collection,
            date=vindex.date, decade=vindex.decade, draw_tries=tries, fallback=fallback,
        )
    return None


# ---------------------------------------------------------------------------
# scheduling + drawing: capped, spread-first round-robin
# ---------------------------------------------------------------------------

def _row_key(row):
    return row["volume_id"]


def spread_round_robin(rows, target_n, draw_fn, rng, max_per_volume,
                        cap_increment=CAP_INCREMENT, used_spans=None):
    """Max-min-fair round-robin: every volume gets one draw attempt before any
    volume gets a second, up to `max_per_volume`; relaxes the cap by
    `cap_increment` when a full pass makes no progress and quota is unmet.
    """
    shuffled = list(rows)
    rng.shuffle(shuffled)
    counts = {_row_key(r): 0 for r in shuffled}
    exhausted = set()
    used_spans = used_spans if used_spans is not None else defaultdict(set)
    results = []
    effective_cap = max_per_volume
    max_draws_one_volume = 0

    while len(results) < target_n:
        made_progress = False
        for row in shuffled:
            if len(results) >= target_n:
                break
            vid = _row_key(row)
            if vid in exhausted or counts[vid] >= effective_cap:
                continue
            item = draw_fn(row, exclude_spans=used_spans[vid])
            if item is None:
                exhausted.add(vid)
                continue
            results.append(item)
            counts[vid] += 1
            used_spans[vid].add(item.span)
            max_draws_one_volume = max(max_draws_one_volume, counts[vid])
            made_progress = True
        if not made_progress:
            if len(results) < target_n and any(vid not in exhausted for vid in counts):
                effective_cap += cap_increment
            else:
                break

    report = {
        "target": target_n,
        "achieved": len(results),
        "volumes_used": sum(1 for c in counts.values() if c > 0),
        "volumes_exhausted": len(exhausted),
        "max_draws_from_one_volume": max_draws_one_volume,
        "effective_cap": effective_cap,
        "shortfall": max(target_n - len(results), 0),
    }
    return results, report


def plan_decade_jobs(roster_rows, target_n, max_per_volume):
    """Metadata-only, diagnostic upper-bound allocation (no text I/O).

    True per-volume yield depends on rejection/redraw behavior that only
    text-level draws can see, so this is not a hard slot list — it is a
    cheap a-priori cap for reporting/dry-run sizing. `run_volume_jobs` does
    the real spread-round-robin, with its own overflow handling, against
    live draws.
    """
    return {row["volume_id"]: max_per_volume for row in roster_rows}


def run_volume_jobs(roster_rows, target_n, length_table, lexicon, rng, max_per_volume,
                     margin=DEFAULT_MARGIN, max_draw_tries=DEFAULT_MAX_DRAW_TRIES,
                     cap_increment=CAP_INCREMENT, cache=None, used_spans=None,
                     fragment_min_words=DEFAULT_FRAGMENT_MIN_WORDS, stats=None):
    """Draw `target_n` passages from `roster_rows` via spread_round_robin.

    Returns (passages, report, cache) — the cache is returned so callers can
    thread it into subsequent stages and avoid re-normalizing shared volumes.
    """
    cache = cache if cache is not None else VolumeCache(lexicon, margin)
    stats = stats if stats is not None else {}

    def draw_fn(row, exclude_spans):
        vindex = cache.get(row)
        sentences, words, fragment = sample_length(length_table, rng)
        return draw_window(vindex, sentences, words, fragment, rng, lexicon,
                            exclude_spans=exclude_spans, max_tries=max_draw_tries,
                            fragment_min_words=fragment_min_words, stats=stats)

    passages, report = spread_round_robin(
        roster_rows, target_n, draw_fn, rng, max_per_volume,
        cap_increment=cap_increment, used_spans=used_spans)
    report["rejection_reasons"] = dict(stats)
    return passages, report, cache


def _existing_rows(roster_subset):
    return [r for _, r in roster_subset.iterrows()
            if isinstance(r["path"], str) and os.path.exists(r["path"])]


# ---------------------------------------------------------------------------
# output records + eligibility flags
# ---------------------------------------------------------------------------

def passage_record(p):
    return {
        "passage_id": p.passage_id,
        "volume_id": p.volume_id,
        "collection": p.collection,
        "date": p.date,
        "decade": p.decade,
        "text": p.text,
        "n_sentences": p.n_sentences,
        "n_words": p.n_words,
        "fragment": p.fragment,
        "target_sentences": p.target_sentences,
        "target_words": p.target_words,
        "char_start": p.char_start,
        "char_end": p.char_end,
        "purposes": list(p.purposes),
        "draw_tries": p.draw_tries,
        "fallback": p.fallback,
    }


def tag_elicitation_eligibility(rows):
    """Add derived eligible_* flags onto positive-passage dict rows, in place."""
    for r in rows:
        n = r.get("n_sentences", 0)
        r["eligible_continuation"] = n >= 3
        r["eligible_paraphrase"] = True
        r["eligible_constrained_generation"] = 2 <= n <= 5
    return rows


# ---------------------------------------------------------------------------
# stage driver: date predictor
# ---------------------------------------------------------------------------

def sample_date_predictor(roster, length_table, target_per_decade=DEFAULT_TARGET_PER_DECADE,
                           max_per_volume=DEFAULT_MAX_PER_VOLUME, margin=DEFAULT_MARGIN,
                           max_draw_tries=DEFAULT_MAX_DRAW_TRIES, seed=DEFAULT_SEED,
                           lexicon=None, decades=None, cache=None):
    lexicon = lexicon if lexicon is not None else load_lexicon()
    rng = random.Random(seed)
    decade_values = decades if decades is not None else sorted(
        int(d) for d in roster["decade"].dropna().unique())
    cache = cache if cache is not None else VolumeCache(lexicon, margin)

    records = []
    reports = {}
    for decade in decade_values:
        rows = _existing_rows(roster[roster["decade"] == decade])
        if not rows:
            reports[int(decade)] = {"target": target_per_decade, "achieved": 0,
                                     "shortfall": target_per_decade, "volumes_used": 0}
            continue
        passages, report, cache = run_volume_jobs(
            rows, target_per_decade, length_table, lexicon, rng, max_per_volume,
            margin=margin, max_draw_tries=max_draw_tries, cache=cache)
        for p in passages:
            p.purposes = ["date_predictor"]
        records.extend(passage_record(p) for p in passages)
        reports[int(decade)] = report

    tag_elicitation_eligibility(records)
    return records, reports


# ---------------------------------------------------------------------------
# stage driver: 1831-1930 authenticity positive supplement
# ---------------------------------------------------------------------------

def sample_authenticity_supplement(roster, length_table, existing_positives,
                                    positive_target=DEFAULT_POSITIVE_TARGET,
                                    max_per_volume=DEFAULT_MAX_PER_VOLUME,
                                    split="even", seed=DEFAULT_SEED, lexicon=None,
                                    margin=DEFAULT_MARGIN, max_draw_tries=DEFAULT_MAX_DRAW_TRIES,
                                    cache=None):
    """Tag in-range date-predictor rows, then top up to `positive_target`.

    Mutates `existing_positives` rows in place (tags purposes); returns only
    the *new* supplement rows plus a report. Callers combine
    `existing_positives + new_records` for the final positive_passages.jsonl.
    """
    lexicon = lexicon if lexicon is not None else load_lexicon()
    rng = random.Random(seed)
    cache = cache if cache is not None else VolumeCache(lexicon, margin)

    used_spans = defaultdict(set)
    in_range = []
    for row in existing_positives:
        used_spans[row["volume_id"]].add((row["char_start"], row["char_end"]))
        if AUTHENTICITY_DATE_LO <= row["date"] <= AUTHENTICITY_DATE_HI:
            purposes = row.setdefault("purposes", [])
            if "authenticity_positive" not in purposes:
                purposes.append("authenticity_positive")
            in_range.append(row)

    shortfall = max(positive_target - len(in_range), 0)
    report = {"in_range_from_date_predictor": len(in_range), "shortfall_target": shortfall}

    supplement_roster = roster[(roster["date"] >= AUTHENTICITY_DATE_LO) &
                                (roster["date"] <= AUTHENTICITY_DATE_HI)]
    if shortfall == 0 or supplement_roster.empty:
        report["decade_reports"] = {}
        report["achieved_new"] = 0
        report["total_authenticity_positive"] = len(in_range)
        return [], report

    new_records = []
    if split == "pooled":
        rows = _existing_rows(supplement_roster)
        passages, decade_report, cache = run_volume_jobs(
            rows, shortfall, length_table, lexicon, rng, max_per_volume,
            margin=margin, max_draw_tries=max_draw_tries, cache=cache, used_spans=used_spans)
        for p in passages:
            p.purposes = ["authenticity_positive"]
        new_records = [passage_record(p) for p in passages]
        report["decade_reports"] = {"pooled": decade_report}
    else:
        decades_present = sorted(int(d) for d in supplement_roster["decade"].dropna().unique())
        n_decades = len(decades_present) or 1
        base = shortfall // n_decades
        remainder = shortfall - base * n_decades
        supply = {d: len(supplement_roster[supplement_roster["decade"] == d]) for d in decades_present}
        ranked = sorted(decades_present, key=lambda d: -supply[d])
        targets = {d: base for d in decades_present}
        for d in ranked[:remainder]:
            targets[d] += 1

        decade_reports = {}
        for decade in decades_present:
            rows = _existing_rows(supplement_roster[supplement_roster["decade"] == decade])
            if not rows or targets[decade] == 0:
                decade_reports[decade] = {"target": targets[decade], "achieved": 0}
                continue
            passages, decade_report, cache = run_volume_jobs(
                rows, targets[decade], length_table, lexicon, rng, max_per_volume,
                margin=margin, max_draw_tries=max_draw_tries, cache=cache, used_spans=used_spans)
            for p in passages:
                p.purposes = ["authenticity_positive"]
            new_records.extend(passage_record(p) for p in passages)
            decade_reports[decade] = decade_report
        report["decade_reports"] = decade_reports

    tag_elicitation_eligibility(new_records)
    report["achieved_new"] = len(new_records)
    report["total_authenticity_positive"] = len(in_range) + len(new_records)
    return new_records, report


# ---------------------------------------------------------------------------
# elicitation prep: infill
# ---------------------------------------------------------------------------

@dataclass
class InfillRecord:
    volume_id: str
    collection: str
    date: int
    decade: int
    title: str
    author: str
    bookend_before: str
    gap_text: str
    bookend_after: str
    gap_n_sentences: int
    gap_n_words: int
    bookend_before_n_words: int
    bookend_after_n_words: int
    matched_positive_passage_id: object
    char_start: int
    char_end: int
    draw_tries: int = 0

    @property
    def span(self):
        return (self.char_start, self.char_end)

    @property
    def elicitation_id(self):
        return f"infill_{self.volume_id}_{self.char_start}_{self.char_end}"


def _build_positive_index(positive_passages):
    """volume_id -> sorted list of (start, end, passage_id) for authenticity positives."""
    idx = defaultdict(list)
    for r in positive_passages:
        if "authenticity_positive" in r.get("purposes", []):
            idx[r["volume_id"]].append((r["char_start"], r["char_end"], r["passage_id"]))
    for vid in idx:
        idx[vid].sort()
    return idx


def _best_overlap(gap_start, gap_end, spans, threshold=0.8):
    gap_len = gap_end - gap_start
    if gap_len <= 0 or not spans:
        return None
    best_id, best_frac = None, 0.0
    for s, e, pid in spans:
        if e <= gap_start:
            continue
        if s >= gap_end:
            break
        overlap = min(e, gap_end) - max(s, gap_start)
        frac = overlap / gap_len
        if frac > best_frac:
            best_frac, best_id = frac, pid
    return best_id if best_frac >= threshold else None


def _infill_candidates(vindex, bookend_sentences, gap_sizes, positive_spans):
    """All bookend-gap-bookend candidates, split into overlap-matched vs. not."""
    lo, hi = vindex.eligible_index_range
    matched, unmatched = [], []
    for g in gap_sizes:
        total = 2 * bookend_sentences + g
        if hi - lo < total:
            continue
        for i in range(lo + bookend_sentences, hi - bookend_sentences - g + 1):
            before_sents = vindex.sentences[i - bookend_sentences:i]
            gap_sents = vindex.sentences[i:i + g]
            after_sents = vindex.sentences[i + g:i + g + bookend_sentences]
            match_id = _best_overlap(gap_sents[0].start, gap_sents[-1].end, positive_spans)
            cand = {
                "before_sents": before_sents, "gap_sents": gap_sents,
                "after_sents": after_sents, "gap_size": g, "match_id": match_id,
            }
            (matched if match_id else unmatched).append(cand)
    return matched, unmatched


def make_infill_draw_fn(cache, positive_index, rng, lexicon, bookend_sentences, gap_sizes,
                         max_tries, stats=None):
    candidate_state = {}

    def draw_fn(row, exclude_spans):
        vid = row["volume_id"]
        if vid not in candidate_state:
            vindex = cache.get(row)
            positive_spans = positive_index.get(vid, [])
            matched, unmatched = _infill_candidates(vindex, bookend_sentences, gap_sizes,
                                                      positive_spans)
            rng.shuffle(matched)
            rng.shuffle(unmatched)
            candidate_state[vid] = {"vindex": vindex, "queue": matched + unmatched}
        state = candidate_state[vid]
        vindex, queue = state["vindex"], state["queue"]

        tries = 0
        while queue and tries < max_tries:
            tries += 1
            cand = queue.pop(0)
            before_sents, gap_sents, after_sents = (
                cand["before_sents"], cand["gap_sents"], cand["after_sents"])
            full_start = before_sents[0].start
            full_end = after_sents[-1].end
            span = (full_start, full_end)
            if span in exclude_spans:
                _bump(stats, "duplicate_span")
                continue
            full_text = vindex.text[full_start:full_end]
            reason = rejection_reason(full_text, lexicon)
            if reason is not None:
                _bump(stats, reason)
                continue
            bookend_before = vindex.text[before_sents[0].start:before_sents[-1].end]
            bookend_after = vindex.text[after_sents[0].start:after_sents[-1].end]
            gap_text = vindex.text[gap_sents[0].start:gap_sents[-1].end]
            return InfillRecord(
                volume_id=vid, collection=vindex.collection, date=vindex.date, decade=vindex.decade,
                title=row.get("title", ""), author=row.get("author", ""),
                bookend_before=bookend_before, gap_text=gap_text, bookend_after=bookend_after,
                gap_n_sentences=len(gap_sents), gap_n_words=count_words(gap_text),
                bookend_before_n_words=count_words(bookend_before),
                bookend_after_n_words=count_words(bookend_after),
                matched_positive_passage_id=cand["match_id"],
                char_start=full_start, char_end=full_end, draw_tries=tries,
            )
        return None

    return draw_fn


def infill_record_dict(r):
    return {
        "elicitation_id": r.elicitation_id, "elicitation_strategy": "infill",
        "volume_id": r.volume_id, "collection": r.collection, "date": r.date, "decade": r.decade,
        "title": r.title, "author": r.author,
        "bookend_before": r.bookend_before, "gap_text": r.gap_text, "bookend_after": r.bookend_after,
        "gap_n_sentences": r.gap_n_sentences, "gap_n_words": r.gap_n_words,
        "bookend_before_n_words": r.bookend_before_n_words,
        "bookend_after_n_words": r.bookend_after_n_words,
        "matched_positive_passage_id": r.matched_positive_passage_id,
        "char_start": r.char_start, "char_end": r.char_end,
    }


def sample_infill_prep(positive_passages, roster, gap_sizes=DEFAULT_GAP_SIZES,
                        bookend_sentences=DEFAULT_BOOKEND_SENTENCES,
                        infill_target=DEFAULT_INFILL_TARGET,
                        infill_max_per_volume=DEFAULT_INFILL_MAX_PER_VOLUME,
                        seed=DEFAULT_SEED, lexicon=None, margin=DEFAULT_MARGIN,
                        max_draw_tries=DEFAULT_MAX_DRAW_TRIES, cache=None):
    lexicon = lexicon if lexicon is not None else load_lexicon()
    rng = random.Random(seed)
    cache = cache if cache is not None else VolumeCache(lexicon, margin)
    positive_index = _build_positive_index(positive_passages)

    volume_ids = set(positive_index.keys())
    supplement_roster = roster[roster["volume_id"].isin(volume_ids)]
    rows = _existing_rows(supplement_roster)
    if not rows:
        return [], {"target": infill_target, "achieved": 0, "shortfall": infill_target}

    stats = {}
    draw_fn = make_infill_draw_fn(cache, positive_index, rng, lexicon,
                                   bookend_sentences, gap_sizes, max_draw_tries, stats=stats)
    records, report = spread_round_robin(rows, infill_target, draw_fn, rng, infill_max_per_volume)
    report["rejection_reasons"] = dict(stats)
    report["matched_share"] = (
        sum(1 for r in records if r.matched_positive_passage_id is not None) / len(records)
        if records else 0.0)
    return [infill_record_dict(r) for r in records], report


# ---------------------------------------------------------------------------
# elicitation prep: few-shot
# ---------------------------------------------------------------------------

@dataclass
class FewshotRecord:
    volume_id: str
    collection: str
    date: int
    decade: int
    title: str
    author: str
    target_word: str
    sentences: list
    sentence_n_words: list
    span_key: tuple
    draw_tries: int = 0

    @property
    def span(self):
        return self.span_key

    @property
    def elicitation_id(self):
        flat = "_".join(f"{a}-{b}" for a, b in self.span_key)
        return f"fewshot_{self.volume_id}_{flat}"


def _content_word_candidates(sentence_text, lexicon, used):
    words = set()
    for m in _WORD_RE.finditer(sentence_text):
        w = m.group(0).lower()
        if w in TOP100_ENGLISH_WORDS or w in used:
            continue
        if w in lexicon:
            words.add(w)
    return words


def _sentence_has_word(sentence_text, word):
    return re.search(rf"\b{re.escape(word)}\b", sentence_text, re.IGNORECASE) is not None


def make_fewshot_draw_fn(cache, rng, lexicon, min_words, max_word_attempts, stats=None):
    used_words = defaultdict(set)

    def draw_fn(row, exclude_spans):
        vid = row["volume_id"]
        vindex = cache.get(row)
        lo, hi = vindex.eligible_index_range
        eligible_sents = vindex.sentences[lo:hi]
        if not eligible_sents:
            return None

        for attempt in range(1, max_word_attempts + 1):
            sent = eligible_sents[rng.randrange(len(eligible_sents))]
            candidates = _content_word_candidates(sent.text, lexicon, used_words[vid])
            if not candidates:
                _bump(stats, "fewshot_no_candidate_word")
                continue
            word = rng.choice(sorted(candidates))
            qualifying = [s for s in eligible_sents
                          if count_words(s.text) >= min_words and _sentence_has_word(s.text, word)]
            if len(qualifying) < 3:
                _bump(stats, "fewshot_too_few_sentences")
                continue
            chosen = rng.sample(qualifying, 3)
            span_key = tuple(sorted((s.start, s.end) for s in chosen))
            if span_key in exclude_spans:
                _bump(stats, "duplicate_span")
                continue
            used_words[vid].add(word)
            return FewshotRecord(
                volume_id=vid, collection=vindex.collection, date=vindex.date, decade=vindex.decade,
                title=row.get("title", ""), author=row.get("author", ""),
                target_word=word, sentences=[s.text for s in chosen],
                sentence_n_words=[count_words(s.text) for s in chosen],
                span_key=span_key, draw_tries=attempt,
            )
        return None

    return draw_fn


def fewshot_record_dict(r):
    return {
        "elicitation_id": r.elicitation_id, "elicitation_strategy": "few_shot",
        "volume_id": r.volume_id, "collection": r.collection, "date": r.date, "decade": r.decade,
        "title": r.title, "author": r.author,
        "target_word": r.target_word, "sentences": r.sentences,
        "sentence_n_words": r.sentence_n_words,
    }


def sample_fewshot_prep(roster, fewshot_min_words=DEFAULT_FEWSHOT_MIN_WORDS,
                         fewshot_target=DEFAULT_FEWSHOT_TARGET,
                         fewshot_max_per_volume=DEFAULT_FEWSHOT_MAX_PER_VOLUME,
                         seed=DEFAULT_SEED, lexicon=None, margin=DEFAULT_MARGIN,
                         cache=None, max_word_attempts=DEFAULT_MAX_WORD_ATTEMPTS):
    lexicon = lexicon if lexicon is not None else load_lexicon()
    rng = random.Random(seed)
    cache = cache if cache is not None else VolumeCache(lexicon, margin)

    supplement_roster = roster[(roster["date"] >= AUTHENTICITY_DATE_LO) &
                                (roster["date"] <= AUTHENTICITY_DATE_HI)]
    rows = _existing_rows(supplement_roster)
    if not rows:
        return [], {"target": fewshot_target, "achieved": 0, "shortfall": fewshot_target}

    stats = {}
    draw_fn = make_fewshot_draw_fn(cache, rng, lexicon, fewshot_min_words, max_word_attempts,
                                    stats=stats)
    records, report = spread_round_robin(rows, fewshot_target, draw_fn, rng, fewshot_max_per_volume)
    report["rejection_reasons"] = dict(stats)
    return [fewshot_record_dict(r) for r in records], report


# ---------------------------------------------------------------------------
# CLI support
# ---------------------------------------------------------------------------

def load_length_table(path=None):
    path = Path(path) if path else DEFAULT_LENGTH_TABLE
    with open(path, encoding="utf-8") as f:
        return json.load(f)["joint"]


def read_jsonl(path):
    rows = []
    path = Path(path)
    if not path.exists():
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def parse_decades(spec, all_decades):
    if not spec:
        return list(all_decades)
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        lo, hi = spec.split("-")
        lo, hi = int(lo), int(hi)
        return [d for d in all_decades if lo <= d <= hi]
    return [int(x) for x in spec.split(",")]


def cmd_date_predictor(args):
    lexicon = load_lexicon(args.lexicon)
    roster = load_roster(args.roster)
    length_table = load_length_table(args.length_table)
    all_decades = sorted(int(d) for d in roster["decade"].dropna().unique())
    decades = parse_decades(args.decades, all_decades)

    records, reports = sample_date_predictor(
        roster, length_table, target_per_decade=args.target_per_decade,
        max_per_volume=args.max_per_volume, margin=args.margin,
        max_draw_tries=args.max_draw_tries, seed=args.seed, lexicon=lexicon, decades=decades)
    write_jsonl(records, args.out)
    print(json.dumps(reports, indent=2, default=str), file=sys.stderr)
    print(f"wrote {len(records)} rows to {args.out}", file=sys.stderr)


def cmd_authenticity_positive(args):
    lexicon = load_lexicon(args.lexicon)
    roster = load_roster(args.roster)
    length_table = load_length_table(args.length_table)
    existing = read_jsonl(args.positives_in)

    new_records, report = sample_authenticity_supplement(
        roster, length_table, existing, positive_target=args.positive_target,
        max_per_volume=args.max_per_volume, split=args.split, seed=args.seed, lexicon=lexicon)
    combined = existing + new_records
    write_jsonl(combined, args.out)
    print(json.dumps(report, indent=2, default=str), file=sys.stderr)
    print(f"wrote {len(combined)} rows to {args.out}", file=sys.stderr)


def cmd_elicitation_prep(args):
    lexicon = load_lexicon(args.lexicon)
    roster = load_roster(args.roster)
    positives = read_jsonl(args.positives_in)
    gap_sizes = tuple(int(x) for x in args.gap_sizes.split(","))

    infill_records, infill_report = sample_infill_prep(
        positives, roster, gap_sizes=gap_sizes, bookend_sentences=args.bookend_sentences,
        infill_target=args.infill_target, infill_max_per_volume=args.infill_max_per_volume,
        seed=args.seed, lexicon=lexicon)
    fewshot_records, fewshot_report = sample_fewshot_prep(
        roster, fewshot_min_words=args.fewshot_min_words, fewshot_target=args.fewshot_target,
        fewshot_max_per_volume=args.fewshot_max_per_volume, seed=args.seed, lexicon=lexicon)

    write_jsonl(infill_records + fewshot_records, args.out)
    print(json.dumps({"infill": infill_report, "few_shot": fewshot_report}, indent=2, default=str),
          file=sys.stderr)
    print(f"wrote {len(infill_records) + len(fewshot_records)} rows to {args.out}", file=sys.stderr)


def cmd_all(args):
    lexicon = load_lexicon(args.lexicon)
    roster = load_roster(args.roster)
    length_table = load_length_table(args.length_table)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_decades = sorted(int(d) for d in roster["decade"].dropna().unique())
    decades = parse_decades(args.decades, all_decades)
    cache = VolumeCache(lexicon, args.margin)

    records, dp_report = sample_date_predictor(
        roster, length_table, target_per_decade=args.target_per_decade,
        max_per_volume=args.max_per_volume, margin=args.margin,
        max_draw_tries=args.max_draw_tries, seed=args.seed, lexicon=lexicon, decades=decades,
        cache=cache)

    new_auth, auth_report = sample_authenticity_supplement(
        roster, length_table, records, positive_target=args.positive_target,
        max_per_volume=args.max_per_volume, split=args.split, seed=args.seed, lexicon=lexicon,
        margin=args.margin, max_draw_tries=args.max_draw_tries, cache=cache)
    combined = records + new_auth
    positives_out = out_dir / "positive_passages.jsonl"
    write_jsonl(combined, positives_out)

    gap_sizes = tuple(int(x) for x in args.gap_sizes.split(","))
    infill_records, infill_report = sample_infill_prep(
        combined, roster, gap_sizes=gap_sizes, bookend_sentences=args.bookend_sentences,
        infill_target=args.infill_target, infill_max_per_volume=args.infill_max_per_volume,
        seed=args.seed, lexicon=lexicon, margin=args.margin, max_draw_tries=args.max_draw_tries,
        cache=cache)
    fewshot_records, fewshot_report = sample_fewshot_prep(
        roster, fewshot_min_words=args.fewshot_min_words, fewshot_target=args.fewshot_target,
        fewshot_max_per_volume=args.fewshot_max_per_volume, seed=args.seed, lexicon=lexicon,
        margin=args.margin, cache=cache)
    elicitation_out = out_dir / "elicitation_prep.jsonl"
    write_jsonl(infill_records + fewshot_records, elicitation_out)

    report = {"date_predictor": dp_report, "authenticity_positive": auth_report,
              "infill": infill_report, "few_shot": fewshot_report}
    print(json.dumps(report, indent=2, default=str), file=sys.stderr)
    print(f"wrote {len(combined)} rows to {positives_out}", file=sys.stderr)
    print(f"wrote {len(infill_records) + len(fewshot_records)} rows to {elicitation_out}",
          file=sys.stderr)


def cmd_report(args):
    rows = read_jsonl(args.positives_in)
    decade_counts = Counter(r["decade"] for r in rows)
    purpose_counts = Counter(p for r in rows for p in r.get("purposes", []))
    volumes = Counter(r["volume_id"] for r in rows)
    n_fragment = sum(1 for r in rows if r.get("fragment"))
    n_fallback = sum(1 for r in rows if r.get("fallback"))
    total_draw_tries = sum(r.get("draw_tries", 1) for r in rows)
    report = {
        "n_rows": len(rows),
        "decade_counts": dict(sorted(decade_counts.items())),
        "purpose_counts": dict(purpose_counts),
        "n_volumes": len(volumes),
        "max_draws_from_one_volume": max(volumes.values()) if volumes else 0,
        "fragment_rows": n_fragment,
        "fragment_fallback_rows": n_fallback,
        "approx_redraw_events": total_draw_tries - len(rows),
    }
    print(json.dumps(report, indent=2))


def cmd_export(args):
    rows = read_jsonl(args.positives_in)
    filtered = [r for r in rows if args.purpose in r.get("purposes", [])]
    write_jsonl(filtered, args.out)
    print(f"wrote {len(filtered)} rows to {args.out}", file=sys.stderr)


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--roster", default=None)
        sp.add_argument("--lexicon", default=None)
        sp.add_argument("--length-table", default=str(DEFAULT_LENGTH_TABLE))
        sp.add_argument("--seed", type=int, default=DEFAULT_SEED)
        sp.add_argument("--max-per-volume", type=int, default=DEFAULT_MAX_PER_VOLUME)
        sp.add_argument("--margin", type=float, default=DEFAULT_MARGIN)
        sp.add_argument("--max-draw-tries", type=int, default=DEFAULT_MAX_DRAW_TRIES)

    dp = sub.add_parser("date-predictor", help="draw the date-predictor positive pool")
    common(dp)
    dp.add_argument("--target-per-decade", type=int, default=DEFAULT_TARGET_PER_DECADE)
    dp.add_argument("--decades", default=None, help="comma list or lo-hi range")
    dp.add_argument("--jobs", type=int, default=1)
    dp.add_argument("--out", default=str(DEFAULT_POSITIVES_PATH))
    dp.set_defaults(func=cmd_date_predictor)

    ap = sub.add_parser("authenticity-positive", help="top up the 1831-1930 authenticity pool")
    common(ap)
    ap.add_argument("--positives-in", default=str(DEFAULT_POSITIVES_PATH))
    ap.add_argument("--positive-target", type=int, default=DEFAULT_POSITIVE_TARGET)
    ap.add_argument("--split", choices=["even", "pooled"], default="even",
                     dest="split")
    ap.add_argument("--supplement-even-split", dest="split", action="store_const", const="even")
    ap.add_argument("--supplement-pooled", dest="split", action="store_const", const="pooled")
    ap.add_argument("--out", default=str(DEFAULT_POSITIVES_PATH))
    ap.set_defaults(func=cmd_authenticity_positive)

    ep = sub.add_parser("elicitation-prep", help="build infill + few-shot negative templates")
    common(ep)
    ep.add_argument("--positives-in", default=str(DEFAULT_POSITIVES_PATH))
    ep.add_argument("--gap-sizes", default=",".join(str(g) for g in DEFAULT_GAP_SIZES))
    ep.add_argument("--bookend-sentences", type=int, default=DEFAULT_BOOKEND_SENTENCES)
    ep.add_argument("--infill-target", type=int, default=DEFAULT_INFILL_TARGET)
    ep.add_argument("--infill-max-per-volume", type=int, default=DEFAULT_INFILL_MAX_PER_VOLUME)
    ep.add_argument("--fewshot-min-words", type=int, default=DEFAULT_FEWSHOT_MIN_WORDS)
    ep.add_argument("--fewshot-target", type=int, default=DEFAULT_FEWSHOT_TARGET)
    ep.add_argument("--fewshot-max-per-volume", type=int, default=DEFAULT_FEWSHOT_MAX_PER_VOLUME)
    ep.add_argument("--out", default=str(DEFAULT_ELICITATION_PATH))
    ep.set_defaults(func=cmd_elicitation_prep)

    al = sub.add_parser("all", help="run date-predictor, authenticity-positive, "
                                     "elicitation-prep in sequence")
    common(al)
    al.add_argument("--target-per-decade", type=int, default=DEFAULT_TARGET_PER_DECADE)
    al.add_argument("--decades", default=None)
    al.add_argument("--positive-target", type=int, default=DEFAULT_POSITIVE_TARGET)
    al.add_argument("--split", choices=["even", "pooled"], default="even", dest="split")
    al.add_argument("--supplement-even-split", dest="split", action="store_const", const="even")
    al.add_argument("--supplement-pooled", dest="split", action="store_const", const="pooled")
    al.add_argument("--gap-sizes", default=",".join(str(g) for g in DEFAULT_GAP_SIZES))
    al.add_argument("--bookend-sentences", type=int, default=DEFAULT_BOOKEND_SENTENCES)
    al.add_argument("--infill-target", type=int, default=DEFAULT_INFILL_TARGET)
    al.add_argument("--infill-max-per-volume", type=int, default=DEFAULT_INFILL_MAX_PER_VOLUME)
    al.add_argument("--fewshot-min-words", type=int, default=DEFAULT_FEWSHOT_MIN_WORDS)
    al.add_argument("--fewshot-target", type=int, default=DEFAULT_FEWSHOT_TARGET)
    al.add_argument("--fewshot-max-per-volume", type=int, default=DEFAULT_FEWSHOT_MAX_PER_VOLUME)
    al.add_argument("--out-dir", default=str(DEFAULT_OUT_ROOT))
    al.set_defaults(func=cmd_all)

    rp = sub.add_parser("report", help="recompute counts/spread/rejection stats from existing jsonl")
    rp.add_argument("--positives-in", default=str(DEFAULT_POSITIVES_PATH))
    rp.set_defaults(func=cmd_report)

    ex = sub.add_parser("export", help="filter positive_passages.jsonl to one purpose")
    ex.add_argument("--positives-in", default=str(DEFAULT_POSITIVES_PATH))
    ex.add_argument("--purpose", choices=["date_predictor", "authenticity_positive"], required=True)
    ex.add_argument("--out", required=True)
    ex.set_defaults(func=cmd_export)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
