"""bt/prompts.py — pairwise comparison prompts and the strict parse layer.

Two rubric modes.  "rationales" is the default and the preferred mode;
"exemplars" is retained only for reproducing artifacts fitted before the
mode existed, and is otherwise deprecated.

  exemplars (deprecated)
      Shows the *text* of every answer option except the two being
      compared, ground truths labelled acceptable and distractors
      unacceptable with their rationale.  Its defect is structural: by
      dropping the compared items it also drops their rationales, so the
      rubric loses its warning about the very answer under judgement.  On
      q39 of the pilot, `d0` is authentic 1830 travel prose rejected as
      "significantly archaic for 1872" -- and when `d0` is compared, the
      only archaism warning in the rubric is the one just withheld.  The
      judge is asked to detect archaism with every mention of archaism
      removed.  Measured over the pilot's 40 questions, 11 had a
      distractor outrank a ground truth under this mode.

  rationales (preferred)
      Suppresses every distractor text and lists *all* the rationales,
      including those of the two items under comparison, as a criteria
      list.  Ground-truth texts are still shown as positive exemplars,
      minus any GT compared or withdrawn.  Rubric coverage no longer
      collapses on the item being judged.  On the 16 questions tested
      head-to-head, 10 of the 11 inverted questions improved (median
      theta gap +0.66, sign test p = 0.012) with the five clean controls
      essentially unmoved.

WHERE MASKING HAPPENS.  Rationales in the benchmark frequently quote the
answer they describe, so showing all of them would let the judge match a
rejection to an answer in front of it -- a label leak that cannot
transfer to a real candidate, who has no rationale.  Masking is applied
**at prompt-build time, per comparison**, inside `_build_rationales_block`
via `mask_self_overlap`: for each of the ~660 comparisons in a 40-question
benchmark, the two answers then in play are masked out of *every*
rationale in that one prompt.

The benchmark file is never modified and `reject_reasons` are never
rewritten on disk; a rationale that is masked in one comparison appears
in full in the next, where its answer is not being judged.  Masking is
therefore not a preprocessing stage you can inspect once -- to see it,
render the block for a specific pair (see the runbook, "Inspect by
hand").  Over the pilot it touches ~11% of rendered rationale lines.

Prompt layout puts the invariant block (context frame, question, rubric,
instructions) before the variable block (the two answers).  Note this
does not currently buy provider-side prompt caching: the invariant prefix
runs ~300-500 tokens, under the 1024-token minimum for claude-sonnet-5,
and no cache_control breakpoint is set anywhere in the pipeline.  Rubric
order is fixed per question (benchmark array order); AB/BA balancing
handles the comparison itself.
"""

from __future__ import annotations

import json
import re

from .design import Item

PROMPT_VERSION = "bt-v3"

# Which rubric a caller gets when it does not say. This is a policy choice and
# is deliberately NOT the same thing as which mode owns the bare artifact tag:
# "exemplars" ran first and its artifacts have no __pm- suffix, and renaming
# them would orphan a real anchor fit. See artifacts.UNSUFFIXED_PROMPT_MODE.
DEFAULT_PROMPT_MODE = "rationales"
PROMPT_MODES = ("exemplars", "rationales")

_SHARED_HEAD = """You are an expert judge of historical discourse. You will compare two candidate answers to a question and decide which one better fits the specific discursive and socio-historical context described. Fit to context means: the answer sounds like something this particular source — its genre, period, and author — might actually say, and reasons within the conceptual horizon of that context.
"""

_SHARED_TAIL = """
Judge only fit to the specified context. Do not reward or penalize an answer for grammar, length, eloquence, or whether you personally agree with it.

You must choose exactly one answer. Ties are not allowed. Respond with JSON only, in exactly this form:
{"context fit": "A"}
or
{"context fit": "B"}"""

SYSTEM_PROMPT = _SHARED_HEAD + """
You will be shown examples of acceptable, partly acceptable, and unacceptable answers as a rubric. The examples are guidance about the failure modes that matter for this question; the two answers you compare are never among them.
""" + _SHARED_TAIL

# The rationales-mode rubric describes every answer written for the question,
# including the two under comparison, so the "never among them" guarantee of
# SYSTEM_PROMPT would be false here and is dropped.  Nothing replaces it: the
# rubric neither asserts nor denies that a described answer is one of the two,
# because a disclosure either way invites the judge to hunt for the match
# rather than apply the criteria.
SYSTEM_PROMPT_RATIONALES = _SHARED_HEAD + """
You will be shown one acceptable example, then short descriptions of how the other answers written for this question were judged. The descriptions are guidance about the failure modes that matter for this question. A phrase replaced by [masked phrase] has been withheld; treat the surrounding description as still informative.
""" + _SHARED_TAIL


def system_prompt_for(mode: str) -> str:
    return SYSTEM_PROMPT_RATIONALES if mode == "rationales" else SYSTEM_PROMPT

RETRY_SUFFIX = """

Your previous reply could not be parsed. Respond with ONLY a JSON object, no other text: {"context fit": "A"} or {"context fit": "B"}. You must pick one; ties are not allowed."""


MASK = "[masked phrase]"

_WORD_RE = re.compile(r"[A-Za-z0-9]+")
_QUOTED_RE = re.compile(r"[\"“”']([^\"“”']{1,400})[\"“”']")

# Small deliberately: the point is to stop incidental function-word runs like
# "of the town and" from being masked, not to strip content words.
_STOP = frozenset("""a an the and or but of in on at to for from by with without
as is are was were be been being it its this that these those there here he she
they them his her their which who whom what when where how not no nor so than
then too very can could would should may might must do does did done have has
had""".split())


def _tokens(text: str) -> list[tuple[str, int, int]]:
    return [(m.group(0).lower(), m.start(), m.end()) for m in _WORD_RE.finditer(text)]


def _quoted_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(1), m.end(1)) for m in _QUOTED_RE.finditer(text)]


def mask_self_overlap(reason: str, *texts: str, min_tokens: int = 4,
                      min_quoted_tokens: int = 2, max_span: int = 40) -> str:
    """Replace runs of `reason` that appear verbatim in any of `texts` with MASK.

    Rationales in the benchmark frequently quote the answer they describe
    ("adopts a style significantly archaic for 1872, e.g. 'a climate
    eminently mild and salubrious'").  In rationales mode the rubric shows
    every rationale, including those of the two answers under comparison,
    so an unmasked quotation would let the judge match a rejection to an
    answer in front of it -- a leak that cannot transfer to a real
    candidate, who has no rationale, and would therefore inflate the
    anchor fit.

    `texts` is the set of answers to protect, i.e. the two under
    comparison.  Masking is deliberately not restricted to the rationale's
    *own* answer: rationales sometimes quote a phrase that occurs in a
    different answer -- q2's `d3` quotes "the old oak", which is in `gt0`'s
    text -- and that cross-quote makes a rejection rationale appear to
    describe a ground truth, the most damaging direction the leak can
    take.  Rationales belonging to items that are not in play still keep
    every phrase that does not occur in a compared answer, which is where
    their period-diction value lives.

    A run must be >= min_tokens long with at least two non-stopword tokens,
    or >= min_quoted_tokens long if it sits entirely inside quotation marks
    -- an explicit quotation is an explicit pointer and needs no length
    excuse.
    """
    if not reason or not texts:
        return reason

    r_toks = _tokens(reason)
    if not r_toks:
        return reason

    own_ngrams: dict[int, set[tuple[str, ...]]] = {}
    for text in texts:
        own = [t[0] for t in _tokens(text or "")]
        for n in range(1, min(max_span, len(own)) + 1):
            own_ngrams.setdefault(n, set()).update(
                tuple(own[i:i + n]) for i in range(len(own) - n + 1)
            )
    if not own_ngrams:
        return reason

    quoted = _quoted_spans(reason)

    def in_quotes(start: int, end: int) -> bool:
        return any(qs <= start and end <= qe for qs, qe in quoted)

    spans: list[tuple[int, int]] = []
    i = 0
    while i < len(r_toks):
        best = 0
        for n in range(min(max_span, len(r_toks) - i), 0, -1):
            if n in own_ngrams and tuple(t[0] for t in r_toks[i:i + n]) in own_ngrams[n]:
                best = n
                break
        if best:
            run = r_toks[i:i + best]
            start, end = run[0][1], run[-1][2]
            threshold = min_quoted_tokens if in_quotes(start, end) else min_tokens
            content = sum(1 for t in run if t[0] not in _STOP)
            if best >= threshold and content >= 2:
                spans.append((start, end))
                i += best
                continue
        i += 1

    if not spans:
        return reason

    merged: list[list[int]] = []
    for s, e in spans:
        # join runs separated only by punctuation/whitespace so the output
        # reads as one elision rather than a stutter of masks
        if merged and not _WORD_RE.search(reason[merged[-1][1]:s]):
            merged[-1][1] = e
        else:
            merged.append([s, e])

    out, prev = [], 0
    for s, e in merged:
        out.append(reason[prev:s])
        out.append(MASK)
        prev = e
    out.append(reason[prev:])
    masked = "".join(out)

    covered = sum(e - s for s, e in merged)
    if covered > 0.6 * len(reason):
        import warnings
        warnings.warn(
            f"mask_self_overlap: {covered / len(reason):.0%} of a rationale was "
            f"masked as self-quotation; consider rewriting it to describe the "
            f"failure without quoting: {reason[:80]!r}",
            stacklevel=2,
        )
    return masked


def _rationale_line(item: Item) -> str:
    header = ("PARTLY ACCEPTABLE" if item.is_partial else "UNACCEPTABLE")
    return f"- {header}. This answer {item.reject_reason}"


def build_exemplar_block(items: list[Item], compared_ids: set[str],
                         withdrawn_ids: set[str], mode: str = DEFAULT_PROMPT_MODE) -> str:
    """Render the rubric exemplars: every item except the two being
    compared and any withdrawn ground truths, in the items' given order.

    Ground truths render as acceptable examples; distractors as
    unacceptable examples with their rationale; distractors human judges
    scored between 0 and 1 as PARTLY ACCEPTABLE, so the header does not
    contradict a rationale that says the answer is nearly right.

    The rationales in the benchmark are written to presume a subject and
    to carry the judgment internally ("gives away its later origin with
    terms like...", "is largely in keeping with the period; errs only
    through..."), so they are prefixed with a neutral "This answer "
    rather than a verdict of our own.

    mode="rationales" instead suppresses every distractor text and lists
    *all* the rationales, including those of the two items under comparison
    (masked against self-quotation).  The exemplars mode drops the compared
    items entirely, which means the rubric's coverage collapses exactly
    where the comparison is hardest: judging an archaic distractor with the
    only archaism warning withheld.  Ground-truth texts are still shown as
    positive exemplars, minus any GT under comparison or withdrawn.
    """
    if mode == "rationales":
        return _build_rationales_block(items, compared_ids, withdrawn_ids)
    if mode != "exemplars":
        raise ValueError(f"unknown exemplar block mode {mode!r}")

    blocks = []
    for it in items:
        if it.item_id in compared_ids or it.item_id in withdrawn_ids:
            continue
        if it.kind == "ground_truth":
            blocks.append(f'ACCEPTABLE example of context fit:\n"{it.text}"')
            continue
        header = "PARTLY ACCEPTABLE" if it.is_partial else "UNACCEPTABLE"
        entry = f'{header} example of context fit:\n"{it.text}"'
        if it.reject_reason:
            entry += f"\nThis answer {it.reject_reason}"
        blocks.append(entry)
    return "\n\n".join(blocks)


def _build_rationales_block(items: list[Item], compared_ids: set[str],
                            withdrawn_ids: set[str]) -> str:
    """Ground-truth exemplars, then one rationale line per distractor.

    Every distractor contributes exactly one line, in benchmark array order,
    whether or not it is under comparison -- so the list length is constant
    within a question and carries no information about which items are in
    play.  The three-tier acceptability label survives the loss of the
    texts, keeping the partial-credit calibration signal intact.
    """
    blocks = []
    for it in items:
        if it.kind != "ground_truth":
            continue
        if it.item_id in compared_ids or it.item_id in withdrawn_ids:
            continue
        blocks.append(f'ACCEPTABLE example of context fit:\n"{it.text}"')

    # Protect both compared answers in *every* rationale, not just their own:
    # a cross-quote is what lets a rejection rationale appear to describe a
    # ground truth that happens to share the phrase.
    protect = tuple(it.text for it in items if it.item_id in compared_ids)

    lines = []
    for it in items:
        if it.kind == "ground_truth" or not it.reject_reason:
            continue
        reason = mask_self_overlap(it.reject_reason, *protect)
        lines.append(_rationale_line(
            Item(it.item_id, it.text, it.kind, reason, it.prob)))

    if lines:
        blocks.append("Other answers written for this question were judged as "
                      "follows.\n" + "\n".join(lines))
    return "\n\n".join(blocks)


_RUBRIC_HEADER = {
    "exemplars": "RUBRIC — examples of acceptable, partly acceptable, and unacceptable answers for this question:",
    "rationales": "RUBRIC — how answers to this question have been judged:",
}


def build_bt_prompt(metadata_frame: str, main_question: str,
                    exemplar_block: str, answer_first: str,
                    answer_second: str, mode: str = DEFAULT_PROMPT_MODE) -> tuple[str, str]:
    """Return (system_content, user_content) for one ordered comparison."""
    user = f"""CONTEXT: {metadata_frame}

QUESTION: {main_question}

{_RUBRIC_HEADER[mode]}

{exemplar_block}

Now compare the two answers below solely on their fit to the context specified above. Choose the one that better fits.

ANSWER A:
"{answer_first}"

ANSWER B:
"{answer_second}"

Respond with JSON only: {{"context fit": "A"}} or {{"context fit": "B"}}."""
    return system_prompt_for(mode), user


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_JSON_RE = re.compile(r"\{[^{}]*\}")


def parse_bt_response(raw: str) -> str | None:
    """Parse a judge reply into "A" or "B"; anything else returns None.

    Tolerant about transport (code fences, prose preambles, whitespace)
    but strict about semantics: ties, "C", refusals, and ambiguity are
    all None.  A dropped call must also drop its AB/BA partner — that
    bookkeeping lives in bt.collect, not here.
    """
    if not raw:
        return None
    text = raw.strip()
    fenced = _FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    if text.upper() in ("A", "B"):
        return text.upper()
    for match in _JSON_RE.findall(text):
        try:
            obj = json.loads(match)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        for key, value in obj.items():
            if key.strip().lower().replace("_", " ") == "context fit":
                if isinstance(value, str) and value.strip().upper() in ("A", "B"):
                    return value.strip().upper()
                return None
    return None
