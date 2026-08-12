#!/usr/bin/env python3
"""negative_qc.py — Phase D2 §5.4: quality control shared by every negative source.

Both `reuse_bertclassify.py` and `elicit_negatives.py` must apply the same
predicates, or the two halves of the negative pool differ systematically and the
detector learns the difference instead of the concept. Following the convention
already set by `passage_filters.py`, there is one implementation and both
callers import it.

The five checks, in the order §5.4 specifies:

1. `rejection_reason()` — the same corpus-side predicate the positives passed.
2. Refusal and meta-commentary; bookend echo.
3. **Leakage guard.** Reject on any shared 8-gram with the true gap text or the
   source continuation. This is the most important check in the phase: a model
   reproducing a memorized passage has emitted a *positive*, and labelling it 1
   teaches the detector the inverse of the target concept.
4. Length compliance against the Phase A distribution.
5. Normalization, Layer 3 then Layer 2.

On ordering: normalization runs *last* for the record that gets written, but the
leakage guard compares normalized text on both sides internally. Curly quotes and
dash style differ between a model's output and the corpus, and an un-normalized
comparison lets those cosmetic differences mask a real verbatim overlap.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from measure_length_distribution import count_sentences, count_words  # noqa: E402
from normalize import clean_model_answer, normalize_typography        # noqa: E402
from passage_filters import rejection_reason                          # noqa: E402

DEFAULT_NGRAM = 8

#: Openers and asides that betray the assistant persona. Deliberately narrow:
#: these match scaffolding, not period prose that happens to start with "Sure".
REFUSAL_PATTERNS = [
    r"^\s*(certainly|sure|of course|absolutely|got it)\b[!,.]",
    r"^\s*here(?:'s| is| are)\b",
    # Refusals need an object, not just a first-person negation: "I cannot say
    # what became of him" is ordinary period narration and must survive, while
    # "I cannot assist with that" must not.
    r"^\s*(i'm sorry|i am sorry|i apologize)\b[,.]?\s+(but\s+)?(i|as)\b",
    r"\b(i cannot|i can't|i am unable to|i'm unable to|i won't|i will not)\s+"
    r"(help|assist|comply|provide|generate|create|produce|fulfil|fulfill|"
    r"continue with|do that|write that)\b",
    r"\bas an ai\b",
    r"\bas a language model\b",
    r"^\s*(sure|okay|ok)\s*[,!.]",
    r"^\s*(note|disclaimer)\s*:",
    r"^\s*\[?(?:begin|end)\s+(?:of\s+)?(?:passage|text|excerpt)\]?",
    r"\bin the style of\b.*\b(19th|nineteenth|early twentieth)\b",
    r"^\s*(the following|this passage|this sentence)\b.*\b(is|was)\b.*\b"
    r"(written|composed|generated)\b",
]

_REFUSAL_RE = [re.compile(p, re.IGNORECASE) for p in REFUSAL_PATTERNS]

#: Markdown/scaffolding leftovers that `strip_answer_scaffolding` did not catch.
_RESIDUAL_MARKUP_RE = re.compile(r"(\*\*|^#{1,6}\s|^\s*[-*]\s+|```)", re.MULTILINE)


def looks_like_refusal_or_meta(text):
    """Return a reason string if the response is scaffolding, else None."""
    t = (text or "").strip()
    if not t:
        return "empty"
    for rx in _REFUSAL_RE:
        if rx.search(t):
            return "refusal_or_meta"
    if _RESIDUAL_MARKUP_RE.search(t):
        return "residual_markup"
    return None


# ---------------------------------------------------------------------------
# Leakage guard
# ---------------------------------------------------------------------------

def _tokens(text):
    """Lowercased word tokens off normalized text, punctuation dropped."""
    return re.findall(r"[a-z0-9']+", normalize_typography(text or "").lower())


def ngrams(text, n=DEFAULT_NGRAM):
    """The set of word n-grams in `text`, normalized. Empty if too short."""
    toks = _tokens(text)
    if len(toks) < n:
        return set()
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def shared_ngram(candidate, reference, n=DEFAULT_NGRAM):
    """Return one shared n-gram between the two texts, or None.

    Returning the actual overlap rather than a bool makes the rejection log
    auditable — §7.6 wants a per-model leakage rate, and a sample of what leaked
    is what tells you whether a model memorized the corpus or merely echoed a
    stock phrase.
    """
    if not candidate or not reference:
        return None
    a = ngrams(candidate, n)
    if not a:
        return None
    hit = a & ngrams(reference, n)
    return " ".join(sorted(hit)[0]) if hit else None


def leakage_reason(candidate, references, n=DEFAULT_NGRAM):
    """Reject if `candidate` shares an n-gram with any reference text.

    Args:
        candidate: the generated negative.
        references: iterable of texts the model must not have reproduced —
            the true gap text, the real continuation, the source passage.
        n: n-gram order; 8 per §5.4.

    Returns:
        (reason, evidence) or (None, None).
    """
    for ref in references:
        hit = shared_ngram(candidate, ref, n)
        if hit:
            return "leakage_ngram", hit
    return None, None


def bookend_echo_reason(candidate, bookend_before="", bookend_after="", n=6):
    """Reject a response that restates the prompt's bookends.

    A lower n than the leakage guard: echoing six words of the prompt back is
    already a formatting failure, whereas eight words of the *hidden* text is a
    memorization failure. Different problems, different thresholds.
    """
    for part, label in ((bookend_before, "before"), (bookend_after, "after")):
        if part and shared_ngram(candidate, part, n):
            return f"bookend_echo_{label}"
    return None


# ---------------------------------------------------------------------------
# Length compliance
# ---------------------------------------------------------------------------

def truncate_to_sentences(text, n_sentences):
    """Keep the first `n_sentences` sentences, cutting on a sentence boundary."""
    if n_sentences <= 0:
        return ""
    try:
        import nltk
        sents = nltk.sent_tokenize(text)
    except Exception:                                          # noqa: BLE001
        sents = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(s.strip() for s in sents[:n_sentences]).strip()


def sample_fitted_length(length_table, rng, avail_sentences, avail_words,
                         tolerance=0.4):
    """Draw a Phase A length cell that this candidate can actually satisfy.

    Re-cutting can only ever shorten text. Drawing a target from the *full*
    Phase A distribution and discarding whatever falls short therefore throws
    away material for a reason that has nothing to do with the material — and
    biases what survives. Restricting the draw to reachable cells keeps the
    Phase A shape wherever supply allows and spends the rejections on genuine
    quality problems instead.

    Returns (sentences, words) or None when no cell is reachable.
    """
    reachable = [c for c in length_table
                 if c["sentences"] <= avail_sentences
                 and c["word_bin"][0] * (1 - tolerance) <= avail_words]
    if not reachable:
        return None
    total = sum(c["weight"] for c in reachable)
    if total <= 0:
        return None
    r = rng.random() * total
    cum, cell = 0.0, reachable[-1]
    for entry in reachable:
        cum += entry["weight"]
        if r <= cum:
            cell = entry
            break
    lo, hi = cell["word_bin"]
    return cell["sentences"], rng.randint(lo, max(lo, hi - 1))


def fit_length(text, target_sentences, target_words, tolerance=0.4,
               min_words=5, max_overshoot=None):
    """Trim `text` toward the Phase A target; return (fitted_text, reason).

    Over-long responses are truncated at a sentence boundary, per §5.4.
    Under-length responses are discarded rather than padded — there is nothing
    honest to pad them with.

    `max_overshoot` closes an asymmetry: truncation fixes the *sentence* count
    exactly but nothing bounds words from above, so a model asked for "5
    sentences, 68 words" can return 5 very long sentences and still pass. Across
    D2 that left the negatives wordier than the positives at matched sentence
    counts (+28 words at 5 sentences). When set, a response is rejected if it
    exceeds `target_words * (1 + max_overshoot)`.

    **Default None — off.** The D2 pool was built without it and must stay
    reproducible; only the D3 length-targeted supplement passes a value.
    """
    t = (text or "").strip()
    if not t:
        return None, "empty"
    fitted = truncate_to_sentences(t, target_sentences) if target_sentences else t
    if not fitted:
        return None, "empty_after_truncation"
    n_words = count_words(fitted)
    if n_words < min_words:
        return None, "too_short"
    if target_words and n_words < target_words * (1 - tolerance):
        return None, "under_length"
    if target_words and max_overshoot is not None \
            and n_words > target_words * (1 + max_overshoot):
        return None, "over_length"
    return fitted, None


# ---------------------------------------------------------------------------
# The whole pass
# ---------------------------------------------------------------------------

def qc_negative(raw_text, lexicon=None, references=(), bookend_before="",
                bookend_after="", target_sentences=None, target_words=None,
                tolerance=0.4, ngram=DEFAULT_NGRAM, check_bookends=True,
                max_overshoot=None):
    """Run §5.4 end to end on one candidate negative.

    Returns:
        dict with `ok` (bool), `text` (normalized, fitted; None when rejected),
        `reason`, `evidence`, `n_sentences`, `n_words`.

    Normalization happens first so every later predicate sees the same text the
    positives side would see — the symmetry §7.7 checks for.
    """
    result = {"ok": False, "text": None, "reason": None, "evidence": None,
              "n_sentences": 0, "n_words": 0}

    # 5: normalize up front — clean_model_answer is already Layer 3 then Layer 2.
    text = clean_model_answer(raw_text or "")
    if not text.strip():
        result["reason"] = "empty"
        return result

    # 2: scaffolding
    reason = looks_like_refusal_or_meta(text)
    if reason:
        result["reason"] = reason
        return result

    if check_bookends:
        reason = bookend_echo_reason(text, bookend_before, bookend_after)
        if reason:
            result["reason"] = reason
            return result

    # 3: leakage — the check this whole module exists for
    reason, evidence = leakage_reason(text, references, n=ngram)
    if reason:
        result["reason"] = reason
        result["evidence"] = evidence
        return result

    # 4: length
    fitted, reason = fit_length(text, target_sentences, target_words, tolerance,
                                max_overshoot=max_overshoot)
    if reason:
        result["reason"] = reason
        return result

    # 1: the corpus-side predicate the positives passed
    reason = rejection_reason(fitted, lexicon)
    if reason:
        result["reason"] = reason
        return result

    result.update({"ok": True, "text": fitted,
                   "n_sentences": count_sentences(fitted),
                   "n_words": count_words(fitted)})
    return result
