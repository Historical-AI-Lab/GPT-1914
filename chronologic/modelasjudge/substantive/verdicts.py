"""substantive/verdicts.py — the one definition of an automatic verdict.

Some candidate answers do not need a judge. If a model's answer is, after
normalization, character-identical to one of the question's own answer
options, we already know the verdict and calling an LLM to rediscover it
wastes money and adds noise to a certainty.

Two conditions, and they are not symmetric between the two scoring paths:

  GT identity          the answer matches a ground truth -> automatic pass
                       on both paths.

  distractor identity  the answer matches a probability-0 distractor ->
                       automatic fail, but on the pass/fail path only for
                       distractors whose penalty class is "question" or
                       "both".

Why the asymmetry. `distractor_penalties.txt` records which criteria each
distractor type violates, and judge_alpha_reliability_nocontext.py already
relies on it: a tie against a "context"-class distractor counts as a
*correct* question-fit judgment there. Those types -- anachronistic_*,
other_book_*, britannica* -- are accurate, relevant answers whose only flaw
is period fidelity. The pass/fail path does not measure period fidelity
(anachronism is penalized on style instead), so matching one is not a
pass/fail failure. The partial-credit path *does* cover context fit, so
every probability-0 match fails there.

Probability > 0 is never an automatic fail on either path. A partial-credit
answer is one human judges scored as partly satisfactory; "partly
satisfactory" is exactly the judgment the partial-credit path exists to
make, so it goes to the judge.

Both scoring paths import this module rather than reaching into each
other: judge_scoring_nocontext.py already imports substantive.routing, and
bt_context_scoring.py already imports substantive.artifacts, so this adds
no new coupling. Importing a top-level CLI script for a few lines of logic
is the more fragile arrangement (see drawbank.py's note on the same point).
"""

from __future__ import annotations

import string
from pathlib import Path

_PUNCT_TABLE = str.maketrans("", "", string.punctuation)

# Distractor penalty classes that count as pass/fail failures. "context" is
# deliberately absent -- see the module docstring.
AUTOFAIL_CLASSES_PASSFAIL = frozenset({"question", "both"})

_PENALTIES_PATH = Path(__file__).resolve().parent.parent / "distractor_penalties.txt"

# One warning per unknown answer_type per process, matching the behavior of
# judge_alpha_reliability_nocontext.compute_reliability.
_warned_unknown_types: set[str] = set()


def normalize_for_identity(s) -> str:
    """Lowercase, drop ASCII punctuation, strip surrounding whitespace.

    Deliberately loose: a model that answers "Author One." when the ground
    truth is "Author One" has given the same answer. Deliberately not
    looser than that -- no stemming, no whitespace collapsing inside the
    string -- because every widening of this function turns some judged
    comparison into an unjudged certainty.
    """
    return (s or "").lower().translate(_PUNCT_TABLE).strip()


def load_distractor_penalties(path=None) -> dict[str, str]:
    """Return {answer_type: "both"|"question"|"context"} from the TSV file."""
    penalties: dict[str, str] = {}
    with open(path or _PENALTIES_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            atype, penalty = parts[0].strip(), parts[1].strip().lower()
            if penalty in ("both", "question", "context"):
                penalties[atype] = penalty
    return penalties


def _zip_answers(rec: dict):
    """Yield (text, answer_type, probability) for every answer option."""
    strings = rec.get("answer_strings") or []
    types = rec.get("answer_types") or []
    probs = rec.get("answer_probabilities") or []
    if not (len(strings) == len(types) == len(probs)):
        # items_from_question raises on this; here we simply decline to
        # manufacture verdicts from a malformed record.
        return
    for text, atype, prob in zip(strings, types, probs):
        yield text, atype, float(prob or 0.0)


def ground_truth_strings(rec: dict) -> list[str]:
    return [t for t, atype, _ in _zip_answers(rec) if atype == "ground_truth"]


def autofail_strings_partial(rec: dict) -> list[str]:
    """Probability-0 distractors, all of them -- the partial-credit rule."""
    return [t for t, atype, prob in _zip_answers(rec)
            if atype != "ground_truth" and prob == 0.0]


def autofail_strings_passfail(rec: dict, penalties: dict[str, str]) -> list[str]:
    """Probability-0 distractors whose penalty class is "question" or "both".

    An answer_type absent from distractor_penalties.txt does NOT auto-fail:
    it falls through to the judge with a one-time warning. An unclassified
    type is an unknown, not a known-bad, and inventing a failure from one
    would be the expensive kind of wrong.
    """
    out = []
    for text, atype, prob in _zip_answers(rec):
        if atype == "ground_truth" or prob != 0.0:
            continue
        penalty = penalties.get(atype)
        if penalty is None:
            if atype not in _warned_unknown_types:
                print(f"  [warning] answer_type {atype!r} is not in "
                      f"distractor_penalties.txt; not eligible for auto-fail")
                _warned_unknown_types.add(atype)
            continue
        if penalty in AUTOFAIL_CLASSES_PASSFAIL:
            out.append(text)
    return out


def auto_verdict(candidate, ground_truths, autofail_strings, *, qnum=None):
    """Return "pass", "fail", or None for a candidate answer.

    A ground-truth match wins over a distractor match. The two should never
    both fire -- a question whose distractor equals its own ground truth is
    a data bug -- so say so rather than resolve it silently.

    An empty candidate matches nothing: normalizing "" to "" would
    otherwise make it identical to any empty answer option.
    """
    norm = normalize_for_identity(candidate)
    if not norm:
        return None

    hit_gt = any(normalize_for_identity(gt) == norm for gt in (ground_truths or []))
    hit_fail = any(normalize_for_identity(d) == norm for d in (autofail_strings or []))

    if hit_gt and hit_fail:
        where = f" on question {qnum}" if qnum is not None else ""
        print(f"  [warning] answer{where} matches both a ground truth and a "
              f"probability-0 distractor; treating as a pass. The benchmark "
              f"record needs fixing.")
    if hit_gt:
        return "pass"
    if hit_fail:
        return "fail"
    return None
