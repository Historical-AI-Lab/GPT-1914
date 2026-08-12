#!/usr/bin/env python3
"""passage_filters.py — Phase C passage rejection predicates. Corpus side only.

The hard wall from phase-c-plan.md: *normalizers* change text and run on
everything; *filters* reject text and run only when assembling the training
corpus. **These are never applied in production.** A candidate answer gets
scored whatever it looks like — a filter on the answer path would silently drop
benchmark items.

Predicates specific to Phase C live here. The ones that already existed are
imported from bertclassify rather than copied, so there is one implementation:

    looks_like_index_line, looks_like_formula_or_table, latex_score
        -- bertclassify/filter_balance_clean.py
    count_words, digit_fraction
        -- bertclassify/bin_counter.py

latex_score matters for bertclassify/imitation/ if Phase D reuses those existing
negatives: data_cleaning.md documents LaTeX contamination there, and
spot-checking confirms numeric-table bleed-through.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT / "bertclassify"))

from bin_counter import count_words, digit_fraction              # noqa: E402
from filter_balance_clean import (                               # noqa: E402
    latex_score,
    looks_like_formula_or_table,
    looks_like_index_line,
    looks_like_markup_or_code,
)

from normalize import DEFAULT_OOV_THRESHOLD, _bare, load_lexicon  # noqa: E402

__all__ = [
    "has_redaction", "cut_at_redaction", "oov_fraction", "rejection_reason",
    "count_words", "digit_fraction", "latex_score",
    "looks_like_formula_or_table", "looks_like_index_line",
    "looks_like_markup_or_code", "DEFAULT_OOV_THRESHOLD",
]

# COHA blanks ten consecutive words for copyright with `@ @ @ ...`, at 15/kw in
# every COHA genre. That is a hole, not noise, and no normalizer can fill it.
_REDACTION = re.compile(r"(?:@\s*){3,}")


def has_redaction(text):
    """True if the passage contains a `@ @ @` copyright redaction."""
    return bool(_REDACTION.search(text or ""))


def cut_at_redaction(text):
    """Return the longest redaction-free span, for windowing rather than rejecting."""
    if not text:
        return ""
    pieces = _REDACTION.split(text)
    return max(pieces, key=len).strip() if pieces else ""


def oov_fraction(text, lexicon=None):
    """Fraction of alphabetic tokens absent from the dictionary.

    The user's dictionary filter. Volume-level rates from the census: 0.9-5.4%
    for ordinary prose, 9.8% for idi_fill and 10.5% for oapen_1925_1990. A
    passage-level threshold near 0.22 removes the tail — Latin/Greek/Pali
    interleaving, tabular garble, multilingual scholarly text — without touching
    ordinary prose.
    """
    if lexicon is None:
        lexicon = load_lexicon()
    alpha = [b for b in (_bare(t) for t in (text or "").split()) if b and b.isalpha()]
    if not alpha:
        return 0.0
    return sum(1 for b in alpha if b not in lexicon) / len(alpha)


def rejection_reason(text, lexicon=None, oov_threshold=DEFAULT_OOV_THRESHOLD,
                     min_words=5):
    """Return a reason string if the passage should be rejected, else None.

    Corpus side only. Order is cheapest-first.
    """
    t = text or ""
    if count_words(t) < min_words:
        return "too_short"
    if has_redaction(t):
        return "redaction"
    if looks_like_markup_or_code(t):
        return "markup"
    if looks_like_formula_or_table(t):
        return "formula_table"
    if looks_like_index_line(t):
        return "index"
    if oov_fraction(t, lexicon) > oov_threshold:
        return "oov"
    return None
