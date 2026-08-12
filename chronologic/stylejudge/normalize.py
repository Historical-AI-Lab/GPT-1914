#!/usr/bin/env python3
"""normalize.py — Phase C text normalization for the style judge.

See stylejudge/phase-c-plan.md. Three layers, with a hard wall between
*normalizers* (change text; run on everything) and *filters* (reject text;
corpus side only — those live in stylejudge/passage_filters.py).

    Layer 1  clean_source(text, collection)   ingest only, per-collection
    Layer 2  normalize_typography(text)       symmetric: train *and* production
    Layer 3  clean_model_answer(text)         answer side only

The two public entry points compose the layers in the only correct order:

    normalize_corpus_text(text, collection)   = Layer 1 then Layer 2
    clean_model_answer(text)                  = Layer 3 then Layer 2

Layers 1 and 3 are line-structure aware (running heads, page numbers,
line-break hyphenation, code fences, trailing commentary paragraphs); Layer 2
collapses everything to a single line. So Layer 2 always runs last, and the
ordering is encoded here rather than in the CLI so it cannot be invoked
backwards.

**Layer 3 is never called on historical text.** Period catechisms, school
readers, and statutes literally contain `Answer:` lines and numbered
enumerations as genuine content.

Nothing outside ~/workdata/ is ever written. `materialize` refuses any output
root elsewhere; see _guard_output_root().

Run from stylejudge/ (or anywhere — paths are resolved relative to this file):

    python normalize.py census --out normalization_census_before.md
    python normalize.py census --normalized --out normalization_census_after.md
    python normalize.py sample --collection coha_mag -n 8
    python normalize.py clean --collection coha_mag -i volume.txt
    python normalize.py clean --layer answer -i answer.txt
    python normalize.py materialize --collections oapen_web
"""

import argparse
import functools
import glob
import json
import os
import random
import re
import string
import sys
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

DEFAULT_LEXICON = Path.home() / "Dropbox" / "DataMunging" / "rulesets" / "MainDictionary.txt"
DEFAULT_ROSTER = SCRIPT_DIR / "corpus_roster.csv"
DEFAULT_ANSWERS_GLOB = str(REPO_ROOT / "modelasjudge" / "generated_answers" / "*0.4*.json")
DEFAULT_OUT_ROOT = Path.home() / "workdata" / "chronologic-dating-corpus" / "normalized"
WORKDATA_ROOT = Path.home() / "workdata"

DEFAULT_OOV_THRESHOLD = 0.22


# ---------------------------------------------------------------------------
# lexicon
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=4)
def load_lexicon(path=None):
    """Return a frozenset of lowercase dictionary words.

    MainDictionary.txt is tab-separated: word, in-dictionary flag, corpus
    frequency. Only rows flagged `1` count as words (174,437 of 333,864 rows);
    the flag-0 rows are observed-but-rejected forms and admitting them would
    defeat the OOV guard on long-s repair.
    """
    path = Path(path) if path else DEFAULT_LEXICON
    words = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > 1 and parts[1] == "1" and parts[0]:
                words.add(parts[0].lower())
    return frozenset(words)


_STRIP_CHARS = string.punctuation + "‘’“”—–"


def _bare(token):
    """Token reduced to its lexicon-lookup form: lowercased, punctuation stripped."""
    return token.strip(_STRIP_CHARS).lower()


def in_lexicon(token, lexicon):
    bare = _bare(token)
    return bool(bare) and bare in lexicon


# ---------------------------------------------------------------------------
# Layer 2 — normalize_typography: symmetric, train *and* production
# ---------------------------------------------------------------------------

# Superset of bertclassify/filter_balance_clean.py:56 normalize_text(). That
# function stays untouched — it serves the currently trained DeBERTa, and
# changing normalization under a trained model invalidates it.

_SINGLE_QUOTES = "‘’‚‛′´`"
_DOUBLE_QUOTES = "“”„‟″«»"
_DASHES = "—–―‒‐‑−⁃"
_SPACES = "              　﻿"
_INVISIBLE = "­​‌‍⁠"

_LIGATURES = (("ﬀ", "ff"), ("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬃ", "ffi"),
              ("ﬄ", "ffl"), ("ﬅ", "st"), ("ﬆ", "st"), ("Œ", "Oe"),
              ("œ", "oe"), ("Æ", "Ae"), ("æ", "ae"))

_SPACE_BEFORE_PUNCT = re.compile(r"[ \t]+([,;:.!?%])")
# A whole run of dashes *and* the whitespace between them, so `, - - even`
# (which is what `,---even` becomes once COHA's `--` is respaced) collapses in
# one pass instead of leaving a second hyphen behind.
_DASH_RUN = re.compile(r"(?:\s*-\s*)+")


def normalize_typography(text):
    """Canonicalize quotes, dashes, spaces, and line structure. Symmetric.

    This is the layer that kills the curly-quote tell (Chicago 56/kw, gpt-5.4
    22/kw, IDI 0.3/kw) and the newline-density tell (0-121/kw across
    collections). Output is always a single whitespace-normalized line.

    Dash policy, decided in phase-c-plan.md: every dash-like character and every
    ASCII `--` collapses to one plain `-` with surrounding whitespace removed.
    Historical dash/hyphen disambiguation is unsolvable in OCR; collapsing to a
    single form makes the question moot rather than answering it wrong.
    """
    if not text:
        return ""

    for ch in _INVISIBLE:
        text = text.replace(ch, "")
    for ch in _SPACES:
        text = text.replace(ch, " ")
    for ch in _SINGLE_QUOTES:
        text = text.replace(ch, "'")
    for ch in _DOUBLE_QUOTES:
        text = text.replace(ch, '"')
    for ch in _DASHES:
        text = text.replace(ch, "-")
    text = text.replace("…", "...")
    text = text.replace("\t", " ")

    # Early-print typography that survived transcription: the long s itself
    # (U+017F, distinct from the f/s OCR confusion Layer 1 repairs) and the
    # printer's ligatures. Both are perfect pre-1800 giveaways, and both are
    # transcription policy rather than anything an author chose, so they are
    # exactly the channel this layer exists to remove.
    text = text.replace("ſ", "s").replace("ẞ", "SS")
    for lig, expansion in _LIGATURES:
        text = text.replace(lig, expansion)

    # Remaining control characters (keep newlines for now; they collapse below).
    text = "".join(
        c for c in text
        if c == "\n" or not unicodedata.category(c).startswith("C")
    )

    # One canonical dash form, one canonical spacing. Runs first while newlines
    # still mark line breaks, so a dash straddling a break also collapses.
    text = _DASH_RUN.sub("-", text)

    text = re.sub(r"\s+", " ", text)
    text = _SPACE_BEFORE_PUNCT.sub(r"\1", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Layer 1 — clean_source: ingest only, dispatched on the roster's collection
# ---------------------------------------------------------------------------

# --- shared repairs -------------------------------------------------------

_SOFT_HYPHEN_AT_EOL = re.compile(r"­[ \t]*\n")
_SPACED_APOSTROPHE = re.compile(r"(\w) ' (s|t|d|m|re|ve|ll)\b", re.IGNORECASE)
# Elisions common enough in 18th-20th century prose to attach an apostrophe to.
_ELISION_RE = re.compile(
    r"(?:em|tis|twas|twere|til|till|cause|round|bout|gainst|neath|"
    r"gan|un|ere|way|nother|fore|pon|mongst|midst|prentice|squire)\b",
    re.IGNORECASE)
_HYPHEN_AT_EOL = re.compile(r"(\S*\w)-[ \t]*\n[ \t]*(\w\S*)")
_MAX_LONG_S = 8   # 2**8 candidate substitutions; longer f-runs are not long-s


def rejoin_clitics(text):
    """`do n't` -> `don't`, `state ' s` -> `state's`.

    COHA is distributed tokenized (15/kw spaced clitics in fiction); ECCO OCR
    produces the same shape at 2.6/kw. Corpus side only — Layer 1 never touches
    model answers.
    """
    text = _SPACED_APOSTROPHE.sub(r"\1'\2", text)
    text = re.sub(r"(\w) (n't|'s|'re|'ve|'ll|'d|'m)\b", r"\1\2", text)
    # A free-standing apostrophe between two words is a plural possessive
    # (`thirty days ' campaign`), an elision (`one of ' em`), or a single-quote
    # quotation mark (`the word ' liberty ' means`). Attach left after an `s`;
    # attach right only for a known elision; otherwise leave it alone, because
    # gluing a *closing* single quote rightward is worse than leaving a space.
    def attach(m):
        left, right = m.group(1), m.group(2)
        if left in "sS":
            return left + "' " + right
        if _ELISION_RE.match(right):
            return left + " '" + right
        return m.group(0)

    return re.sub(r"(\w) ' (\w+)", attach, text)


def dehyphenate_linebreaks(text, lexicon):
    """Repair words split by a hyphen at a line ending, dictionary-guarded.

    The rule (user-specified): for `x-` + `y`, rejoin as `xy` only if `xy` is in
    the lexicon *and* `x` and `y` are not both independently in it. Otherwise
    drop the hyphen and leave the two pieces separated by a space.

    A consequence worth stating: `under-\\nstand` becomes `under stand`, because
    "under", "stand", and "understand" are all lexicon words, so the second
    clause blocks the rejoin. That is the approved rule, not a bug; the
    alternative (rejoin whenever the merge is a word) fuses genuine compounds
    like `well-\\nknown` into `wellknown`.

    Adapted from novelty/cleanandchunk/clean_and_chunk.py:76 fix_broken_words(),
    which implements the merge-and-check half without the second clause.

    Rates measured in the census: OAPEN 6.4-6.6/kw, IDI 0.4/kw, 0 elsewhere.
    """
    def repair(m):
        left, right = m.group(1), m.group(2)
        merged = left + right
        if in_lexicon(merged, lexicon) and not (
            in_lexicon(left, lexicon) and in_lexicon(right, lexicon)
        ):
            return merged + "\n"
        return left + " " + right + "\n"

    return _HYPHEN_AT_EOL.sub(repair, text)


def repair_long_s(text, lexicon):
    """Undo OCR's long-s confusion (`confeffes` -> `confesses`), OOV-guarded.

    For an out-of-vocabulary token containing `f`, try every subset of its `f`
    positions substituted to `s`, and accept the first substitution that yields
    a lexicon word. Subsets, not all-or-one: `confeffes` needs its second and
    third `f` changed but not its first. The OOV guard makes this safe to run on
    every collection — it fires at 54.6/ktok in the 1700-1799 band and at or
    below 0.2/ktok everywhere else.
    """
    def repair_token(token):
        bare = _bare(token)
        if not bare or "f" not in bare or bare in lexicon:
            return token
        positions = [i for i, ch in enumerate(bare) if ch == "f"]
        if len(positions) > _MAX_LONG_S:
            return token
        # Prefer substitutions that change the most characters: a long s is a
        # systematic misread, so a word with three of them usually has three.
        candidates = []
        for mask in range(1, 1 << len(positions)):
            chars = list(bare)
            for bit, pos in enumerate(positions):
                if mask & (1 << bit):
                    chars[pos] = "s"
            candidates.append("".join(chars))
        candidates.sort(key=lambda c: -sum(a != b for a, b in zip(c, bare)))
        for cand in candidates:
            if cand in lexicon:
                # Splice the repair back into the original token, preserving
                # its punctuation and capitalization pattern.
                start = token.lower().find(bare)
                if start < 0:
                    return token
                fixed = "".join(
                    c.upper() if token[start + j].isupper() else c
                    for j, c in enumerate(cand)
                )
                return token[:start] + fixed + token[start + len(bare):]
        return token

    return re.sub(r"\S+", lambda m: repair_token(m.group(0)), text)


def reflow(text):
    """A lone newline is a line wrap, not a paragraph break."""
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text)


# --- per-collection de-formatting ----------------------------------------

_COHA_TAGS = re.compile(r"</?[pP]>|</?[bB][rR]\s*/?>|\s//\s")


def detokenize_quotes(text):
    """Remove the space COHA's tokenizer puts on the *inside* of quotation marks.

    `" Do n't wake Lilly . "` -> `"Do n't wake Lilly ."`. Which side is inside
    can't be read off a straight `"`, so parity decides it: within a line,
    even-numbered quotes open and odd-numbered ones close. Parity resets at each
    line, so an unbalanced quote spoils one line rather than the rest of the
    volume. The space *outside* the quote is left alone — that one is real.
    """
    out_lines = []
    for line in text.split("\n"):
        if '"' not in line:
            out_lines.append(line)
            continue
        parts = line.split('"')
        for k in range(len(parts) - 1):          # quote k sits after parts[k]
            if k % 2 == 0:                       # opening
                parts[k + 1] = parts[k + 1].lstrip(" \t")
            else:                                # closing
                parts[k] = parts[k].rstrip(" \t")
        out_lines.append('"'.join(parts))
    return "\n".join(out_lines)
_REDACTION = re.compile(r"(?:@\s*){3,}")


def _clean_coha(text, lexicon):
    """COHA arrives tokenized and SGML-lite: detokenize it.

    `@ @ @` copyright redactions are *not* repairable here — they are a hole,
    not noise. passage_filters.has_redaction() rejects passages containing one.
    """
    text = _COHA_TAGS.sub(" ", text)
    text = text.replace("--", " - ")
    text = rejoin_clitics(text)
    # COHA's tokenizer puts a space on the inside of every quotation mark
    # (`" Do n't wake Lilly . "`). Nothing else in the corpus does, so the
    # residue is a collection channel in its own right; the census after the
    # first pass showed it at 15-33/kw in COHA against 1.2 in ECCO.
    return detokenize_quotes(text)


_OAPEN_BOILERPLATE = re.compile(
    r"(doi\.org|dx\.doi\.org|https?://|creativecommons\.org|"
    r"©\s*The Author|\(C\)\s*The Author|ISBN|e-ISBN|"
    r"This chapter is distributed under|Open Access)",
    re.IGNORECASE,
)
_FOOTNOTE_AFTER_QUOTE = re.compile(r"([\"'”’])\d{1,3}(?=\W|$)")


def _clean_oapen(text, lexicon):
    """OAPEN is PDF-extracted: soft hyphens, running heads, footnote digits."""
    lines = text.split("\n")
    heads = _repeated_short_lines(lines)
    kept = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            if stripped in heads:
                continue
            if _is_bare_number(stripped):
                continue
            if _OAPEN_BOILERPLATE.search(stripped) and len(stripped.split()) < 30:
                continue
        kept.append(line)
    text = "\n".join(kept)
    text = _FOOTNOTE_AFTER_QUOTE.sub(r"\1", text)
    return text


_BRACKETED_PAGE = re.compile(r"\[\s*\d{1,4}\s*\]")
_BARE_NUMBER = re.compile(r"[\dIVXLCivxlc.,\-—\[\]() ]{1,12}")


def _is_bare_number(stripped):
    return bool(_BARE_NUMBER.fullmatch(stripped))


def _is_short_allcaps(stripped):
    return (
        len(stripped) < 45
        and stripped == stripped.upper()
        and bool(re.search(r"[A-Z]{3}", stripped))
    )


def _clean_idi_ecco(text, lexicon):
    """IDI and ECCO: the clean_ocr_text() logic, plus bracketed page markers.

    Reuses booksample/connectors/make_cloze_questions.py:540 clean_ocr_text() —
    bare page/section numbers and short ALL-CAPS running heads (the
    bookplate/accession-stamp case the Phase B spot check found: `HARVARD
    COLLEGE LIBRARY GIFT OF`). Line-break dehyphenation and long-s repair are
    applied by the shared tail rather than here, so every collection gets the
    same treatment and no counter can differ by collection.
    """
    text = _BRACKETED_PAGE.sub(" ", text)
    kept = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped:
            if _is_bare_number(stripped):
                continue
            if _is_short_allcaps(stripped):
                continue
        kept.append(line)
    return "\n".join(kept)


_MD_BULLET = re.compile(r"^[ \t]*[-*+•][ \t]+", re.MULTILINE)
_MD_HEADER = re.compile(r"^[ \t]*#{1,6}[ \t]*", re.MULTILINE)
_MD_RULE = re.compile(r"^[ \t]*(?:[-*_][ \t]*){3,}$", re.MULTILINE)
_NAV_LINE = re.compile(
    r"^[ \t]*(?:home|menu|search|share|tweet|print|next|previous|"
    r"skip to (?:main )?content|cookie|privacy policy|terms of use|"
    r"all rights reserved|subscribe|sign up|log ?in)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)


def _clean_crawl(text, lexicon):
    """Common Crawl is born-digital web text: markdown bullets and nav chrome."""
    text = _MD_RULE.sub("", text)
    text = _NAV_LINE.sub("", text)
    text = _MD_HEADER.sub("", text)
    text = _MD_BULLET.sub("", text)
    return text


def _clean_chicago(text, lexicon):
    """Chicago fiction is clean modern OCR; Layer 2 does nearly all the work."""
    kept = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and _is_bare_number(stripped):
            continue
        kept.append(line)
    return "\n".join(kept)


def _clean_generic(text, lexicon):
    return text


_DISPATCH = (
    ("coha", _clean_coha),
    ("oapen", _clean_oapen),
    ("idi", _clean_idi_ecco),
    ("ecco", _clean_idi_ecco),
    ("chicago", _clean_chicago),
    ("commoncrawl", _clean_crawl),
    ("crawl", _clean_crawl),
)


def collection_cleaner(collection):
    """Return the Layer-1 function for a roster `collection` value."""
    name = (collection or "generic").strip().lower()
    for prefix, fn in _DISPATCH:
        if name.startswith(prefix):
            return fn
    return _clean_generic


_REPEAT_MIN = 3
_REPEAT_MAX_WORDS = 8


def _repeated_short_lines(lines):
    """Short lines that recur across a document: PDF running heads."""
    counts = {}
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped.split()) <= _REPEAT_MAX_WORDS:
            counts[stripped] = counts.get(stripped, 0) + 1
    return {s for s, n in counts.items() if n >= _REPEAT_MIN}


def clean_source(text, collection="generic", lexicon=None):
    """Layer 1: per-collection de-formatting of a whole volume. Ingest only.

    Operates on a *whole volume* because the work needs document context —
    OAPEN running-head detection finds short lines that repeat across pages,
    and reflow needs the surrounding paragraph. Phase D's passage sampler
    should clean a volume once and cache it while drawing passages from it.

    Pure function; reads nothing and writes nothing.
    """
    if not text:
        return ""
    if lexicon is None:
        lexicon = load_lexicon()

    # A soft hyphen at a line ending is a line-break hyphen (OAPEN
    # `copy\xad\nright`); make it one before the rest of them are deleted.
    text = _SOFT_HYPHEN_AT_EOL.sub("-\n", text)
    text = text.replace("­", "")

    text = collection_cleaner(collection)(text, lexicon)

    # Shared tail, applied to every collection so no counter can carry the
    # collection's identity. Order matters: dehyphenation needs the line breaks
    # that reflow is about to remove.
    text = dehyphenate_linebreaks(text, lexicon)
    text = reflow(text)
    text = re.sub(r"[ \t]+([,;:.!?])", r"\1", text)
    text = rejoin_clitics(text)
    text = repair_long_s(text, lexicon)
    return re.sub(r"[ \t]{2,}", " ", text)


def normalize_corpus_text(text, collection="generic", lexicon=None):
    """Corpus path: Layer 1 then Layer 2. The order is not optional."""
    return normalize_typography(clean_source(text, collection, lexicon))


# ---------------------------------------------------------------------------
# Layer 3 — clean_model_answer: answer side only
# ---------------------------------------------------------------------------

# Ports and extends stylejudge/measure_length_distribution.py:127 prenormalize(),
# whose docstring asked to be replaced by a call into this module.
#
# TRAP, stated so nobody removes the guard later: label and enumerator
# stripping runs *only* here and *only* at leading position. Period catechisms,
# school readers, and statutes in the corpus literally contain `Answer:` lines
# and numbered enumerations as genuine content. Layer 3 is never called on
# historical text.

_PREAMBLES = (
    "answer:", "a:", "response:", "completion:", "passage:", "output:",
    "note:", "explanation:", "continuation:", "text:",
)

_END_MARKERS = ("END OF ANSWER", "END OF PASSAGE", "[END]", "<END>")

# openings of a trailing paragraph in which the model discusses its own answer
_COMMENTARY = (
    "note:", "explanation:", "(note", "this answer", "the answer provided",
    "this response", "the response", "this passage adheres", "i have ",
    "in this answer", "please note", "here, ", "the above", "as requested",
)

# inline framing that precedes the answer proper, flagged in NOTES.md:228
_INLINE_FRAMING = re.compile(
    r"^[^\n]{0,120}?\b(?:should read|would read|reads as follows|"
    r"is as follows|might be|could be|filled in|completed (?:passage|sentence)|"
    r"missing (?:clause|sentence|words?|text))\b[^\n]{0,40}?:\s*",
    re.IGNORECASE,
)

_LEADING_ENUMERATOR = re.compile(r"^[ \t]*\(?\d{1,2}[.)][ \t]+", re.MULTILINE)
_AT_START_ENUMERATOR = re.compile(r"\A[ \t]*\(?\d{1,2}[.)][ \t]+")
_AT_START_BULLET = re.compile(r"\A[ \t]*[-*+•][ \t]+")
_BLOCKQUOTE = re.compile(r"^[ \t]*>[ \t]?", re.MULTILINE)
_EMPHASIS = re.compile(r"(\*{1,3}|_{1,3}|`{1,3})(?=\S)(.+?)(?<=\S)\1", re.DOTALL)

_WRAP_QUOTES = (('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’"))


def _unwrap_structured(t):
    """If the model wrapped its answer in JSON or a dict literal, take the value."""
    stripped = t.strip()
    if not stripped or stripped[0] not in "{[":
        return t
    try:
        obj = json.loads(stripped)
    except (ValueError, TypeError):
        return t
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
        return obj[0]
    if isinstance(obj, dict):
        for key in ("answer", "response", "text", "completion", "passage", "output"):
            val = obj.get(key)
            if isinstance(val, str):
                return val
        vals = [v for v in obj.values() if isinstance(v, str)]
        if len(vals) == 1:
            return vals[0]
    return t


def _strip_leaders(t):
    """Peel leading labels, enumerators, and bullets until none remain.

    Iterative because they nest: `**Answer:** 1. He went home` needs the label
    removed before the enumerator underneath it becomes leading.
    """
    for _ in range(4):
        before = t
        lowered = t.lower()
        for p in _PREAMBLES:
            if lowered.startswith(p):
                t = t[len(p):].lstrip()
                break
        t = _AT_START_ENUMERATOR.sub("", t)
        t = _AT_START_BULLET.sub("", t)
        t = t.lstrip()
        if t == before:
            break
    return t


def strip_answer_scaffolding(text):
    """Layer 3 proper: remove markdown, labels, wrappers, and self-commentary.

    Line-structure aware, so it must run before normalize_typography() collapses
    the text to one line. Callers should use clean_model_answer(), which
    composes the two in the right order.
    """
    t = (text or "").strip()
    if not t:
        return ""

    t = _unwrap_structured(t).strip()

    # fenced code blocks: drop the fence lines, keep the contents
    if "```" in t:
        t = "\n".join(ln for ln in t.split("\n") if not ln.strip().startswith("```")).strip()

    # models that announce where their answer stops, then editorialize about it
    for marker in _END_MARKERS:
        idx = t.find(marker)
        if idx != -1:
            t = t[:idx].strip()
            break
    lines = t.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() in ("END", "---", "###", "***") and i > 0:
            t = "\n".join(lines[:i]).strip()
            break

    # a trailing self-commentary paragraph
    paras = t.split("\n\n")
    while len(paras) > 1 and paras[-1].strip().lower().startswith(_COMMENTARY):
        paras.pop()
    t = "\n\n".join(paras).strip()

    t = _MD_RULE.sub("", t)
    t = _MD_HEADER.sub("", t)
    t = _BLOCKQUOTE.sub("", t)
    # Per-line, because talkie-base numbers nearly every line (34.5/kw). Two
    # digits maximum, so a sentence opening "1861. It was..." is left alone.
    t = _LEADING_ENUMERATOR.sub("", t)
    t = _MD_BULLET.sub("", t)
    t = _EMPHASIS.sub(r"\2", t)
    t = _strip_leaders(t.strip())

    framed = _INLINE_FRAMING.sub("", t, count=1)
    if framed.strip():
        t = framed.strip()

    # surrounding quotes, straight or curly
    for open_q, close_q in _WRAP_QUOTES:
        if len(t) > 2 and t.startswith(open_q) and t.endswith(close_q):
            t = t[len(open_q):-len(close_q)].strip()
            break

    return t.strip()


def clean_model_answer(text):
    """Answer path: Layer 3 then Layer 2. The order is not optional.

    Never call this on corpus text.
    """
    return normalize_typography(strip_answer_scaffolding(text))


# ---------------------------------------------------------------------------
# CLI support: roster, sampling, census counters
# ---------------------------------------------------------------------------

def load_roster(path=None):
    import pandas as pd
    return pd.read_csv(path or DEFAULT_ROSTER)


def read_volume(path, max_chars=None, offset_fraction=1 / 3):
    """Read a volume, optionally a window taken `offset_fraction` into it."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    if max_chars and len(text) > max_chars:
        start = int(len(text) * offset_fraction)
        start = min(start, len(text) - max_chars)
        text = text[start:start + max_chars]
    return text


def _sample_volumes(roster, collection, n, seed):
    rows = roster[roster["collection"] == collection]
    rows = rows[rows["path"].apply(lambda p: isinstance(p, str) and os.path.exists(p))]
    if len(rows) == 0:
        return []
    rng = random.Random(seed)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    return [rows.iloc[i] for i in idx[:n]]


_COUNTERS = {
    "@ @ @ redaction": lambda t: len(_REDACTION.findall(t)),
    "<p>/<br>": lambda t: len(re.findall(r"</?[pP]>|</?[bB][rR]\s*/?>", t)),
    " // ": lambda t: t.count(" // "),
    "space+clitic": lambda t: len(re.findall(r"\w (?:n't|'s|'re|'ve|'ll|'d|'m|' \w)", t)),
    "space before punct": lambda t: len(re.findall(r"\S[ \t]+[,;:.!?]", t)),
    "curly quotes": lambda t: sum(t.count(c) for c in "‘’“”"),
    # Not in the plan's pass criteria; added after the first pass, when the
    # tokenized-quote residue turned out to be a channel of its own. Counts
    # quotation marks with whitespace on *both* sides, which is direction-free:
    # a tokenizer pads both sides, ordinary typography pads exactly one. A
    # counter keyed on one side only measures how much dialogue a genre has.
    "isolated quotes": lambda t: len(re.findall(r'(?:^|\s)["\'](?:\s|$)', t)),
    "soft hyphen": lambda t: t.count("­"),
    "em/en dash": lambda t: sum(t.count(c) for c in "—–"),
    "--": lambda t: t.count("--"),
    "ellipsis char": lambda t: t.count("…"),
    "hyphen at line break": lambda t: len(re.findall(r"\w-[ \t]*\n", t)),
    "markdown bullet": lambda t: len(_MD_BULLET.findall(t)),
    "markdown **": lambda t: t.count("**"),
    "num-list prefix": lambda t: len(_LEADING_ENUMERATOR.findall(t)),
    "newlines": lambda t: t.count("\n"),
    "short-ALLCAPS lines": lambda t: sum(
        1 for ln in t.split("\n") if ln.strip() and _is_short_allcaps(ln.strip())
    ),
}

_COUNTER_ORDER = list(_COUNTERS)


def count_artifacts(text, lexicon):
    """Artifact counts per 1,000 words, plus OOV% and long-s per 1,000 tokens."""
    tokens = text.split()
    n_words = max(len(tokens), 1)
    per_kw = {name: 1000.0 * fn(text) / n_words for name, fn in _COUNTERS.items()}

    bare = [_bare(tok) for tok in tokens]
    alpha = [b for b in bare if b and b.isalpha()]
    oov = [b for b in alpha if b not in lexicon]
    per_kw["OOV %"] = 100.0 * len(oov) / max(len(alpha), 1)
    longs = sum(
        1 for b in oov
        if "f" in b and (
            b.replace("f", "s") in lexicon
            or any(b[:i] + "s" + b[i + 1:] in lexicon for i, c in enumerate(b) if c == "f")
        )
    )
    per_kw["long-s /ktok"] = 1000.0 * longs / max(len(alpha), 1)
    return per_kw


_CENSUS_ROWS = _COUNTER_ORDER + ["OOV %", "long-s /ktok"]


def _format_table(colnames, rows, fmt):
    """rows: dict[row_label][colname] -> float."""
    if fmt == "csv":
        out = ["metric," + ",".join(colnames)]
        for label in _CENSUS_ROWS:
            out.append(label + "," + ",".join(
                f"{rows.get(label, {}).get(c, 0.0):.2f}" for c in colnames))
        return "\n".join(out)
    out = ["| | " + " | ".join(colnames) + " |",
           "|---|" + "---|" * len(colnames)]
    for label in _CENSUS_ROWS:
        out.append("| `" + label + "` | " + " | ".join(
            f"{rows.get(label, {}).get(c, 0.0):.1f}" for c in colnames) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def cmd_census(args):
    lexicon = load_lexicon(args.lexicon)
    roster = load_roster(args.roster)
    collections = sorted(roster["collection"].dropna().unique())

    corpus_rows = {}
    for coll in collections:
        vols = _sample_volumes(roster, coll, args.volumes_per_collection, args.seed)
        if not vols:
            continue
        totals = {}
        for row in vols:
            text = read_volume(row["path"], args.chars_per_volume)
            if args.normalized:
                text = normalize_corpus_text(text, coll, lexicon)
            counts = count_artifacts(text, lexicon)
            for k, v in counts.items():
                totals[k] = totals.get(k, 0.0) + v
        for k, v in totals.items():
            corpus_rows.setdefault(k, {})[coll] = v / len(vols)
        print(f"  {coll}: {len(vols)} volumes", file=sys.stderr)

    answer_rows = {}
    answer_cols = []
    for path in sorted(glob.glob(args.answers_glob)):
        label = os.path.basename(path).replace(".json", "")
        texts = _extract_answer_texts(path)
        if not texts:
            continue
        answer_cols.append(label)
        totals = {}
        for t in texts:
            if args.normalized:
                t = clean_model_answer(t)
            for k, v in count_artifacts(t, lexicon).items():
                totals[k] = totals.get(k, 0.0) + v
        for k, v in totals.items():
            answer_rows.setdefault(k, {})[label] = v / len(texts)
        print(f"  {label}: {len(texts)} answers", file=sys.stderr)

    state = "after normalization" if args.normalized else "before normalization"
    parts = [f"# Normalization census — {state}", "",
             f"Sampled {args.volumes_per_collection} volumes per collection, "
             f"{args.chars_per_volume} chars each, seed {args.seed}. "
             f"Rates per 1,000 words.", "",
             "## Corpus", "",
             _format_table([c for c in collections if c in
                            next(iter(corpus_rows.values()), {})],
                           corpus_rows, args.format), ""]
    if answer_cols:
        parts += ["## Model answers", "",
                  _format_table(answer_cols, answer_rows, args.format), ""]
    report = "\n".join(parts)

    out = Path(args.out)
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}", file=sys.stderr)


def _extract_answer_texts(path):
    """Pull free-generation answer strings out of a generated_answers JSON."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return []
    texts = []

    def walk(obj):
        if isinstance(obj, dict):
            for key in ("free_generation", "generation", "answer", "response", "completion"):
                val = obj.get(key)
                if isinstance(val, str) and val.strip():
                    texts.append(val)
                    return
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    return texts


def cmd_clean(args):
    lexicon = load_lexicon(args.lexicon)
    text = Path(args.input).read_text(encoding="utf-8", errors="replace") if args.input \
        else sys.stdin.read()

    collection = args.collection or "generic"
    if args.layer == "source":
        out = clean_source(text, collection, lexicon)
    elif args.layer == "typography":
        out = normalize_typography(text)
    elif args.layer == "answer_only":
        out = strip_answer_scaffolding(text)
    elif args.layer == "answer":
        out = clean_model_answer(text)
    elif args.layer == "all":
        out = clean_model_answer(clean_source(text, collection, lexicon))
    else:  # corpus
        out = normalize_corpus_text(text, collection, lexicon)

    if args.filter:
        import passage_filters
        reason = passage_filters.rejection_reason(
            out, lexicon=lexicon, oov_threshold=args.oov_threshold)
        if reason:
            print(f"REJECTED ({reason}): {out[:120]}", file=sys.stderr)
            out = ""

    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
    else:
        sys.stdout.write(out + "\n")


def cmd_sample(args):
    lexicon = load_lexicon(args.lexicon)
    roster = load_roster(args.roster)
    collections = [args.collection] if args.collection else \
        sorted(roster["collection"].dropna().unique())

    rng = random.Random(args.seed)
    for coll in collections:
        vols = _sample_volumes(roster, coll, args.n, args.seed)
        print(f"\n{'=' * (args.width * 2 + 3)}\n{coll}\n{'=' * (args.width * 2 + 3)}")
        for row in vols:
            raw = read_volume(row["path"], 20000)
            start = rng.randrange(0, max(len(raw) - 1200, 1))
            before = raw[start:start + 1200]
            after = normalize_corpus_text(before, coll, lexicon)
            print(f"\n--- {row['volume_id']} ({row['date']}) ---")
            print("BEFORE:", " / ".join(before.split("\n"))[:args.width * 4])
            print("AFTER :", after[:args.width * 4])


def _guard_output_root(out_root):
    """Refuse any output root outside ~/workdata/.

    The read-only guarantee: nothing outside ~/workdata/ is ever written, and no
    source volume is cleaned in place. CHICAGO_CORPUS in particular is a shared
    resource. Both sides are resolved because ~/workdata may itself be a symlink.
    """
    resolved = Path(out_root).expanduser().resolve()
    allowed = WORKDATA_ROOT.expanduser().resolve()
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(
            f"refusing to write outside {allowed}: {resolved}. "
            "normalize.py never modifies a source corpus."
        )
    return resolved


def _write_output(out_root, relative, text):
    """The module's only write path for volume text; runs the guard every time."""
    root = _guard_output_root(out_root)
    dest = (root / relative).resolve()
    if root not in dest.parents:
        raise ValueError(f"refusing to write outside {root}: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return dest


def _materialize_one(job):
    """Worker for `materialize --jobs N`. Must be module-level to be picklable."""
    volume_id, collection, src, out_root, rel, lexicon_path = job
    lexicon = load_lexicon(lexicon_path)          # cached per worker process
    raw = read_volume(src)
    out = normalize_corpus_text(raw, collection, lexicon)
    dest = _write_output(out_root, rel, out)
    # Volume-level diagnostics, not a filtering decision: passage filters are
    # applied at draw time by the Phase D sampler, on the passage, not here.
    # Computed inline rather than through passage_filters, which imports this
    # module.
    alpha = [b for b in (_bare(t) for t in out.split()) if b and b.isalpha()]
    return {
        "volume_id": volume_id, "collection": collection,
        "source_path": src, "normalized_path": str(dest),
        "words_before": len(raw.split()), "words_after": len(out.split()),
        "redactions": len(_REDACTION.findall(out)),
        "oov_fraction": round(
            sum(1 for b in alpha if b not in lexicon) / max(len(alpha), 1), 4),
    }


def cmd_materialize(args):
    import csv
    from concurrent.futures import ProcessPoolExecutor

    load_lexicon(args.lexicon)                    # fail fast on a bad path
    roster = load_roster(args.roster)
    root = _guard_output_root(args.out_root)

    wanted = set(args.collections.split(",")) if args.collections else None
    manifest_path = root / "normalized_manifest.csv"
    skipped = 0
    jobs = []
    for _, row in roster.iterrows():
        coll = row["collection"]
        if wanted and coll not in wanted:
            continue
        src = row["path"]
        if not (isinstance(src, str) and os.path.exists(src)):
            continue
        rel = Path(str(coll)) / f"{row['volume_id']}.txt"
        if (root / rel).exists() and not args.force:
            skipped += 1
            continue
        jobs.append((row["volume_id"], coll, src, root, rel, args.lexicon))

    rows = []
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for i, rec in enumerate(pool.map(_materialize_one, jobs, chunksize=4), 1):
                rows.append(rec)
                if i % 100 == 0:
                    print(f"  {i}/{len(jobs)} written", file=sys.stderr)
    else:
        for i, job in enumerate(jobs, 1):
            rows.append(_materialize_one(job))
            if i % 100 == 0:
                print(f"  {i}/{len(jobs)} written", file=sys.stderr)
    written = len(rows)

    if rows:
        exists = manifest_path.exists()
        with open(manifest_path, "a" if exists else "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            if not exists:
                w.writeheader()
            w.writerows(rows)
    print(f"wrote {written}, skipped {skipped}; manifest {manifest_path}", file=sys.stderr)


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--lexicon", default=str(DEFAULT_LEXICON))
        sp.add_argument("--roster", default=str(DEFAULT_ROSTER))

    c = sub.add_parser("census", help="measure artifact rates, before or after normalization")
    common(c)
    c.add_argument("--answers-glob", default=DEFAULT_ANSWERS_GLOB)
    c.add_argument("--normalized", action="store_true")
    c.add_argument("--volumes-per-collection", type=int, default=25)
    c.add_argument("--chars-per-volume", type=int, default=200000)
    c.add_argument("--seed", type=int, default=11)
    c.add_argument("--out", default="normalization_census.md")
    c.add_argument("--format", choices=["md", "csv"], default="md")
    c.set_defaults(func=cmd_census)

    cl = sub.add_parser("clean", help="normalize a file or stream")
    common(cl)
    cl.add_argument("--collection", default=None)
    cl.add_argument("--layer", default="corpus",
                    choices=["source", "typography", "answer", "answer_only", "corpus", "all"])
    cl.add_argument("--oov-threshold", type=float, default=DEFAULT_OOV_THRESHOLD)
    cl.add_argument("--filter", action="store_true")
    cl.add_argument("-i", "--input", default=None)
    cl.add_argument("-o", "--output", default=None)
    cl.set_defaults(func=cmd_clean)

    s = sub.add_parser("sample", help="print passages before and after normalization")
    common(s)
    s.add_argument("--collection", default=None)
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--seed", type=int, default=11)
    s.add_argument("--width", type=int, default=100)
    s.set_defaults(func=cmd_sample)

    m = sub.add_parser("materialize", help="optional write-new cache under ~/workdata/")
    common(m)
    m.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    m.add_argument("--collections", default=None)
    m.add_argument("--jobs", type=int, default=1)
    m.add_argument("--force", action="store_true")
    m.set_defaults(func=cmd_materialize)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPT_DIR))
    main()
