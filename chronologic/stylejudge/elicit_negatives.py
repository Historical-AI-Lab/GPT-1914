#!/usr/bin/env python3
"""elicit_negatives.py — Phase D2 §5: elicit LLM imitations of 1831-1930 prose.

The negative half of the authenticity detector's training set. Five modalities in
fixed proportions (infill 40 / continuation 20 / paraphrase 10 / constrained 20 /
few-shot 10), spread across the generator stable in `model_stable.py` with a
family-level holdout that never enters a training round.

Follows the `CLAUDE.md` pipeline conventions: progressive JSONL append, resume,
never load the full output into memory, and a thin local wrapper over
`make_openrouter_client` / `call_openrouter_chat`.

Three design points worth stating up front, because each fixes a way the pool
could quietly go wrong:

**The router reads actuals, never defaults.** At startup it scans
`negatives.jsonl` for what each (modality, model) pair has already achieved and
subtracts that from quota. Reuse delivered 5,301 infill / 1,099 continuation,
not the 5,760/640 `model_stable` assumes, and only the file knows the truth.
Resume falls out of the same scan — for a shared append-only file, line offsets
mean nothing and quota-aware resume is the only correct semantics.

**Length targets come from the complement, not the raw table.** Reuse is 85%
single-sentence against positives' median of 2, so drawing elicited lengths from
the Phase A distribution directly would leave the pooled negatives measurably
shorter than the positives — a shortcut the detector would find before it found
anything about style. `complement_length_table()` subtracts what is already in
the file from the pool-wide target histogram and draws from what remains.

**`date_in_prompt` is recorded, never re-inferred.** §5.1 requires the coin flip
be logged; a resumed run must not reflip it and an analysis must not guess it
from the text.

CLI
    python elicit_negatives.py smoke     [--stable R] [--model ID] [--json]
    python elicit_negatives.py summaries [--n N] [--out PATH] ...
    python elicit_negatives.py run       [--limit N] [--dry-run] ...
    python elicit_negatives.py report    [--by model|modality|decade|...]
"""

import argparse
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT / "modelasjudge"))

import model_stable as ms                                              # noqa: E402
from measure_length_distribution import count_words                    # noqa: E402
from negative_qc import fit_length, qc_negative                        # noqa: E402
from normalize import load_lexicon                                     # noqa: E402
from sample_passages import load_length_table                          # noqa: E402

DEFAULT_PASSAGES = Path.home() / "workdata" / "chronologic-dating-corpus" / "passages"
DEFAULT_POSITIVES = DEFAULT_PASSAGES / "positive_passages.jsonl"
DEFAULT_PREP = DEFAULT_PASSAGES / "elicitation_prep.jsonl"
DEFAULT_SUMMARIES = DEFAULT_PASSAGES / "constrained_gen_db.jsonl"
DEFAULT_NEGATIVES = DEFAULT_PASSAGES / "negatives.jsonl"
DEFAULT_ROSTER = SCRIPT_DIR / "corpus_roster.csv"
DEFAULT_LENGTH_TABLE = SCRIPT_DIR / "length_distribution.json"

DEFAULT_SEED = 20260809
DEFAULT_BUDGET_CAP = 75.0
DEFAULT_CONCURRENCY = 4
SUMMARY_MODEL = "openai/gpt-5.6-terra"

INFILL = ms.INFILL
CONTINUATION = ms.CONTINUATION
PARAPHRASE = ms.PARAPHRASE
CONSTRAINED = ms.CONSTRAINED
FEW_SHOT = ms.FEW_SHOT


# ---------------------------------------------------------------------------
# Prompt assembly — pure functions, no I/O, no network
# ---------------------------------------------------------------------------

def _date_clause(date, date_in_prompt):
    return f" The passage was published in {date}." if date_in_prompt else ""


def assemble_infill_prompt(prep_row, variant, date_in_prompt):
    """§5.1 infill. Two variants; the date clause is an independent coin flip.

    variant "explicit_length": states sentence count and an approximate word
    count. variant "style_only": states the sentence count and asks for a
    matching style, with no word target — the pair isolates how much of a
    model's period pastiche depends on being told the shape of the answer.
    """
    n_sent = prep_row.get("gap_n_sentences", 1)
    plural = "sentence" if n_sent == 1 else "sentences"
    if variant == "explicit_length":
        words = prep_row.get("gap_n_words", 25)
        ask = (f"Write the missing {plural}: {n_sent} {plural}, "
               f"roughly {words} words.")
    else:
        ask = (f"Fill the gap in a style matching the surrounding text. "
               f"Write {n_sent} {plural}.")
    return (f"{ask}{_date_clause(prep_row.get('date'), date_in_prompt)}\n"
            f"Respond with the missing text only.\n\n"
            f"{prep_row.get('bookend_before', '')}\n"
            f"[missing text]\n"
            f"{prep_row.get('bookend_after', '')}")


def assemble_continuation_prompt(passage_row):
    """§5.1 continuation. Raw prefix for /v1/completions.

    No instruction, no date, no length guidance — that is the entire point of the
    completion endpoint: the model sees period text and continues it without a
    chat template or an assistant persona in the way.
    """
    return passage_row["text"].rstrip()


def assemble_continuation_chat_prompt(passage_row, n_sentences):
    """Continuation for chat models, which cannot take a bare prefix."""
    plural = "sentence" if n_sentences == 1 else "sentences"
    return (f"Continue the following passage for {n_sentences} more {plural}, "
            f"in the same style. Respond with the continuation only.\n\n"
            f"{passage_row['text'].rstrip()}")


def assemble_paraphrase_prompt(passage_row, date_in_prompt):
    """§5.1 paraphrase."""
    return ("Express this in different words, retaining the meaning, the period "
            "style, and roughly the same length."
            f"{_date_clause(passage_row.get('date'), date_in_prompt)}\n"
            "Respond with the rewritten passage only.\n\n"
            f"{passage_row['text']}")


def assemble_constrained_prompt(passage_row, summary_row, title, n_sentences,
                                n_words):
    """§5.1 constrained generation — closest of the five to the real benchmark.

    Uses the summary when one is available and falls back to the required word,
    so a gap in `constrained_gen_db.jsonl` degrades the prompt rather than
    dropping the job.
    """
    plural = "sentence" if n_sentences == 1 else "sentences"
    date = passage_row.get("date")
    lines = [f"Write a passage of {n_sentences} {plural}, roughly {n_words} words,"]
    if title:
        lines.append(f"as it might appear in \"{title}\" ({date}).")
    else:
        lines.append(f"in the prose style of {date}.")
    summary = (summary_row or {}).get("summary")
    words = (summary_row or {}).get("uncommon_words") or []
    if summary:
        lines.append(f"It should convey: {summary}")
    if words:
        lines.append(f"Use the word \"{words[0]}\".")
    lines.append("Respond with the passage only.")
    return "\n".join(lines)


def assemble_fewshot_prompt(prep_row):
    """§5.1 few-shot: three period sentences sharing a word, ask for a fourth."""
    word = prep_row.get("target_word", "")
    examples = "\n".join(f"- {s}" for s in prep_row.get("sentences", []))
    return (f"Here are three sentences from the same period source, all using "
            f"the word \"{word}\":\n\n{examples}\n\n"
            f"Write one new sentence in the same style, also using the word "
            f"\"{word}\". Respond with the sentence only.")


PROMPT_VARIANTS = {
    INFILL: ("explicit_length", "style_only"),
    CONTINUATION: ("raw_prefix",),
    PARAPHRASE: ("same_length",),
    CONSTRAINED: ("title_date_summary",),
    FEW_SHOT: ("shared_word",),
}

#: Modalities where the date can appear in the prompt (§5.1). Continuation is
#: excluded by construction — a raw prefix carries no instruction to put it in.
DATE_FLIP_MODALITIES = (INFILL, PARAPHRASE)


# ---------------------------------------------------------------------------
# Length complement
# ---------------------------------------------------------------------------

def length_cell_key(n_sentences, n_words, length_table):
    """Map an observed (sentences, words) pair onto a Phase A cell key."""
    for cell in length_table:
        lo, hi = cell["word_bin"]
        if cell["sentences"] == n_sentences and lo <= n_words < hi:
            return (cell["sentences"], lo, hi)
    # Out-of-table lengths fall in the nearest bin of the right sentence count.
    same = [c for c in length_table if c["sentences"] == n_sentences]
    if not same:
        return None
    nearest = min(same, key=lambda c: abs(sum(c["word_bin"]) / 2 - n_words))
    return (nearest["sentences"], nearest["word_bin"][0], nearest["word_bin"][1])


def complement_length_table(length_table, achieved_rows, pool_total):
    """The length distribution the *remaining* rows must follow.

    Target histogram is `length_table` scaled to `pool_total`. Subtract what the
    file already holds; whatever is left is what still needs generating. Cells
    already over-filled contribute zero rather than a negative weight.

    Returns a table in the same shape as `length_table` (so `sample_length` and
    `sample_fitted_length` accept it), reweighted to the deficit. Falls back to
    the original table when the deficit is empty — better a correct-shaped draw
    than no draw at all.
    """
    total_weight = sum(c["weight"] for c in length_table) or 1.0
    achieved = Counter()
    for row in achieved_rows:
        key = length_cell_key(row.get("n_sentences", 0), row.get("n_words", 0),
                              length_table)
        if key:
            achieved[key] += 1

    out = []
    for cell in length_table:
        key = (cell["sentences"], cell["word_bin"][0], cell["word_bin"][1])
        target = pool_total * cell["weight"] / total_weight
        deficit = max(0.0, target - achieved.get(key, 0))
        if deficit > 0:
            new = dict(cell)
            new["weight"] = deficit
            out.append(new)
    if not out:
        return list(length_table)
    total = sum(c["weight"] for c in out)
    for c in out:
        c["weight"] = c["weight"] / total
    return out


# ---------------------------------------------------------------------------
# Startup scan — what the output file already holds
# ---------------------------------------------------------------------------

def scan_negatives(path):
    """Read `negatives.jsonl` once and report what is already achieved.

    Streams the file; never holds more than the summary plus the length rows,
    per the progressive-JSONL convention.
    """
    path = Path(path)
    state = {
        "n_rows": 0,
        "by_modality": Counter(),
        "by_model": Counter(),
        "by_model_modality": Counter(),
        "by_provenance": Counter(),
        "by_provenance_modality": Counter(),
        "by_split_role": Counter(),
        "length_rows": [],
        "used_sources": set(),
        "used_negative_ids": set(),
    }
    if not path.exists():
        return state
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            state["n_rows"] += 1
            mod = row.get("elicitation_strategy")
            mid = row.get("model_id")
            state["by_modality"][mod] += 1
            state["by_model"][mid] += 1
            state["by_model_modality"][(mid, mod)] += 1
            state["by_provenance"][row.get("provenance")] += 1
            state["by_provenance_modality"][(row.get("provenance"), mod)] += 1
            state["by_split_role"][row.get("split_role")] += 1
            state["length_rows"].append({"n_sentences": row.get("n_sentences", 0),
                                         "n_words": row.get("n_words", 0)})
            if row.get("source_passage_id"):
                state["used_sources"].add((mod, row["source_passage_id"]))
            if row.get("negative_id"):
                state["used_negative_ids"].add(row["negative_id"])
    return state


def remaining_quota(plan, state, role=ms.TRAIN):
    """Per (model, modality) rows still owed, after what the file already holds."""
    if role == ms.EVAL_HOLDOUT:
        return _eval_holdout_quota(state)
    out = {}
    for mid, mods in plan["per_model"].items():
        for mod, n in mods.items():
            done = state["by_model_modality"].get((mid, mod), 0)
            if n - done > 0:
                out[(mid, mod)] = n - done
    return out


def _eval_holdout_quota(state):
    """§4.4: ~2,000 frozen negatives, spread evenly over the holdout models."""
    models = [m for m in ms.EVAL_MODELS if m.available]
    per_model = ms.largest_remainder(
        ms.DEFAULT_EVAL_HOLDOUT_TOTAL,
        {m.model_id: 1 for m in models})
    out = {}
    for m in models:
        share = ms.largest_remainder(per_model[m.model_id],
                                     {mod: 1 for mod in m.modalities})
        for mod, n in share.items():
            done = state["by_model_modality"].get((m.model_id, mod), 0)
            if n - done > 0:
                out[(m.model_id, mod)] = n - done
    return out


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------

def load_positives(path, purposes="authenticity_positive"):
    """Stream the positives file, keeping only authenticity rows."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if purposes in row.get("purposes", []):
                rows.append(row)
    return rows


def load_prep(path):
    """Split `elicitation_prep.jsonl` into its two strategies."""
    infill, fewshot = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            (infill if row.get("elicitation_strategy") == "infill"
             else fewshot).append(row)
    return infill, fewshot


def load_summaries(path):
    """passage_id -> summary row, for constrained generation."""
    path = Path(path)
    if not path.exists():
        return {}
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            out[row["passage_id"]] = row
    return out


def load_titles(roster_path=DEFAULT_ROSTER):
    """volume_id -> title. The positives file carries no title of its own."""
    try:
        import pandas as pd
        df = pd.read_csv(roster_path)
        return {str(v): (t if isinstance(t, str) else "")
                for v, t in zip(df["volume_id"], df["title"])}
    except Exception:                                              # noqa: BLE001
        return {}


# ---------------------------------------------------------------------------
# Job construction
# ---------------------------------------------------------------------------

def prefer_multi_sentence(prep_rows, rng):
    """Order infill prep rows so larger gaps are consumed first.

    The pool is over-supplied with single-sentence negatives (reuse is 85% of
    them), so infill — whose length is pinned by its prep row's gap — is the one
    place selection can push back. Gap-3 before gap-2 before gap-1.
    """
    rows = list(prep_rows)
    rng.shuffle(rows)
    rows.sort(key=lambda r: -r.get("gap_n_sentences", 1))
    return rows


def build_job_pools(positives, infill_prep, fewshot_prep, rng, state=None):
    """Per-modality queues of source rows, longest-gap-first where it matters."""
    used = (state or {}).get("used_sources", set())
    pools = {}
    pools[INFILL] = [r for r in prefer_multi_sentence(infill_prep, rng)
                     if (INFILL, r.get("elicitation_id")) not in used]

    fewshot = [r for r in fewshot_prep
               if (FEW_SHOT, r.get("elicitation_id")) not in used]
    rng.shuffle(fewshot)
    pools[FEW_SHOT] = fewshot

    def positive_pool(flag, modality):
        rows = [r for r in positives if r.get(flag)
                and (modality, r["passage_id"]) not in used]
        rng.shuffle(rows)
        return rows

    pools[CONTINUATION] = positive_pool("eligible_continuation", CONTINUATION)
    pools[PARAPHRASE] = positive_pool("eligible_paraphrase", PARAPHRASE)
    pools[CONSTRAINED] = positive_pool("eligible_constrained_generation", CONSTRAINED)
    return pools


def plan_jobs(quota, pools, rng, length_table, titles=None, summaries=None,
              limit=None):
    """Build the flat job list for the outstanding quota.

    Jobs are drawn round-robin across (model, modality) pairs so each pair's
    sources come off the front of its pool, then the whole list is **shuffled**.
    The shuffle matters: round-robin alone makes any prefix reflect the *number*
    of pairs rather than the size of their quotas, so a `--limit 200` dry run
    would show 30% continuation against a true share of 2%. Shuffling makes every
    prefix — a dry run, a budget-capped stop, an interrupted run — an unbiased
    sample of the whole plan.
    """
    titles = titles or {}
    summaries = summaries or {}
    cursors = {mod: 0 for mod in pools}
    pairs = sorted(quota, key=lambda k: (-quota[k], k))
    outstanding = dict(quota)
    jobs = []

    while outstanding:
        progressed = False
        for pair in list(pairs):
            if pair not in outstanding:
                continue
            mid, mod = pair
            pool = pools.get(mod) or []
            if cursors[mod] >= len(pool):
                del outstanding[pair]
                continue
            source = pool[cursors[mod]]
            cursors[mod] += 1
            jobs.append(make_job(mid, mod, source, rng, length_table,
                                 titles, summaries))
            outstanding[pair] -= 1
            progressed = True
            if outstanding[pair] <= 0:
                del outstanding[pair]
        if not progressed:
            break
    rng.shuffle(jobs)
    return jobs[:limit] if limit else jobs


def make_job(model_id, modality, source, rng, length_table, titles, summaries):
    """One elicitation job: everything needed to issue the call and QC the result.

    The date coin-flip happens here, once, and is carried on the job into the
    output row — §5.1 requires it be logged rather than re-inferred.
    """
    spec = ms.by_id(model_id)
    variants = PROMPT_VARIANTS[modality]
    variant = variants[rng.randrange(len(variants))]
    date_in_prompt = (modality in DATE_FLIP_MODALITIES and rng.random() < 0.5)

    job = {"model_id": model_id, "modality": modality, "prompt_variant": variant,
           "date_in_prompt": date_in_prompt,
           "endpoint": spec.endpoint if spec else ms.CHAT,
           "reasoning_effort": spec.reasoning_effort if spec else None,
           "source": source}

    if modality == INFILL:
        job["prompt"] = assemble_infill_prompt(source, variant, date_in_prompt)
        job["target_sentences"] = source.get("gap_n_sentences", 1)
        job["target_words"] = source.get("gap_n_words", 25)
        job["references"] = [source.get("gap_text", "")]
        job["bookend_before"] = source.get("bookend_before", "")
        job["bookend_after"] = source.get("bookend_after", "")
        job["source_passage_id"] = source.get("elicitation_id")
    elif modality == FEW_SHOT:
        job["prompt"] = assemble_fewshot_prompt(source)
        job["target_sentences"] = 1
        job["target_words"] = None
        job["references"] = list(source.get("sentences", []))
        job["source_passage_id"] = source.get("elicitation_id")
    elif modality == PARAPHRASE:
        job["prompt"] = assemble_paraphrase_prompt(source, date_in_prompt)
        job["target_sentences"] = source.get("n_sentences", 2)
        job["target_words"] = source.get("n_words")
        # A paraphrase that reproduces its source is not a paraphrase.
        job["references"] = [source.get("text", "")]
        job["source_passage_id"] = source.get("passage_id")
    elif modality == CONSTRAINED:
        from measure_length_distribution import sample_length
        n_sent, n_words, _ = sample_length(length_table, rng)
        title = titles.get(str(source.get("volume_id")), "")
        job["prompt"] = assemble_constrained_prompt(
            source, summaries.get(source.get("passage_id")), title, n_sent, n_words)
        job["target_sentences"] = n_sent
        job["target_words"] = n_words
        job["references"] = [source.get("text", "")]
        job["source_passage_id"] = source.get("passage_id")
    else:  # continuation
        from measure_length_distribution import sample_length
        n_sent, n_words, _ = sample_length(length_table, rng)
        if job["endpoint"] == ms.COMPLETIONS:
            job["prompt"] = assemble_continuation_prompt(source)
        else:
            job["prompt"] = assemble_continuation_chat_prompt(source, n_sent)
        job["target_sentences"] = n_sent
        job["target_words"] = n_words
        # The true continuation lives in the volume and is not loaded here; the
        # source passage is the prefix, so this catches prompt echo only. Rows
        # are tagged `leakage_checkable: false` to keep that visible downstream.
        job["references"] = []
        job["bookend_before"] = source.get("text", "")
        job["source_passage_id"] = source.get("passage_id")

    job.setdefault("bookend_before", "")
    job.setdefault("bookend_after", "")
    job["leakage_checkable"] = bool(job["references"])
    return job


# ---------------------------------------------------------------------------
# Cost accounting
# ---------------------------------------------------------------------------

def estimate_tokens(text):
    """Token estimate for budgeting. tiktoken when available, else words x 1.3."""
    if not text:
        return 0
    try:
        import tiktoken
        return len(tiktoken.get_encoding("o200k_base").encode(text))
    except Exception:                                              # noqa: BLE001
        return int(count_words(text) * 1.3) + 1


class CostTally:
    """Running per-model spend, with the §5.5 hard cap.

    Token counts are *estimates* — `call_openrouter_chat` returns a string, not
    a usage object, so there is no exact accounting available through the
    import surface `CLAUDE.md` prescribes. The cap therefore trips on an
    estimate; it is a guard rail, not an invoice.
    """

    def __init__(self, cap=DEFAULT_BUDGET_CAP):
        self.cap = cap
        self.by_model = defaultdict(lambda: {"in": 0, "out": 0, "usd": 0.0,
                                             "calls": 0})
        self.total_usd = 0.0

    def record(self, model_id, prompt, response):
        spec = ms.by_id(model_id)
        t_in, t_out = estimate_tokens(prompt), estimate_tokens(response)
        price_in = spec.price_in if spec else 0.0
        price_out = spec.price_out if spec else 0.0
        usd = (t_in * price_in + t_out * price_out) / 1e6
        entry = self.by_model[model_id]
        entry["in"] += t_in
        entry["out"] += t_out
        # Accumulate at full precision. Rounding each call to 4 decimals drops
        # anything under $0.00005 -- which is most single calls on the cheap
        # models -- and 23,600 of those silently vanish from the total.
        entry["usd"] += usd
        entry["calls"] += 1
        self.total_usd += usd
        return usd

    @property
    def exceeded(self):
        return self.total_usd >= self.cap

    def summary(self):
        return {"total_usd": round(self.total_usd, 4), "cap": self.cap,
                "by_model": {k: {**v, "usd": round(v["usd"], 4)}
                             for k, v in sorted(self.by_model.items())}}


# ---------------------------------------------------------------------------
# Thin network wrapper
# ---------------------------------------------------------------------------

def make_client(cred_path=None):
    from openrouter_client import make_openrouter_client
    return make_openrouter_client(cred_path)


def call_chat(client, model_id, prompt, max_tokens=400, reasoning_effort=None):
    """Chat endpoint, via the shared wrapper `CLAUDE.md` prescribes."""
    from openrouter_client import call_openrouter_chat
    return call_openrouter_chat(
        client, model_id, prompt, max_tokens=max_tokens,
        reasoning_effort=reasoning_effort or "none")


def call_completion(client, model_id, prompt, max_tokens=400, temperature=1.0):
    """Completion endpoint — no chat template, no assistant persona.

    The shared wrapper covers chat only, so this is the one place a raw client
    call is made. §4.2 flags the whole pseudo-base premise as unverified: any
    model that 404s here loses its quota, which is what `smoke` is for.
    """
    resp = client.completions.create(
        model=model_id, prompt=prompt, max_tokens=max_tokens,
        temperature=temperature)
    return (resp.choices[0].text or "") if resp.choices else ""


def issue(client, job, max_tokens=400, temperature=1.0):
    if job["endpoint"] == ms.COMPLETIONS:
        return call_completion(client, job["model_id"], job["prompt"],
                               max_tokens=max_tokens, temperature=temperature)
    return call_chat(client, job["model_id"], job["prompt"],
                     max_tokens=max_tokens,
                     reasoning_effort=job.get("reasoning_effort"))


# ---------------------------------------------------------------------------
# Row assembly
# ---------------------------------------------------------------------------

def negative_row(job, raw_response, verdict, split_role, temperature):
    source = job["source"]
    date = source.get("date")
    return {
        "negative_id": f"elicit_{job['modality']}_{job['model_id']}"
                       f"_{job['source_passage_id']}".replace("/", "_"),
        "elicitation_strategy": job["modality"],
        "prompt_variant": job["prompt_variant"],
        "date_in_prompt": job["date_in_prompt"],
        "model_id": job["model_id"],
        "endpoint": job["endpoint"],
        "temperature": temperature,
        "reasoning_effort": job.get("reasoning_effort"),
        "source_passage_id": job["source_passage_id"],
        "source_volume_id": source.get("volume_id"),
        "source_collection": source.get("collection"),
        "source_date": date,
        "source_decade": source.get("decade"),
        "source_title": source.get("title", ""),
        "raw_response": raw_response,
        "text": verdict["text"],
        "n_sentences": verdict["n_sentences"],
        "n_words": verdict["n_words"],
        "leakage_checkable": job["leakage_checkable"],
        "provenance": "elicited",
        "split_role": split_role,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def append_row(row, path):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Subcommand: smoke
# ---------------------------------------------------------------------------

SMOKE_CHAT_PROMPT = ("Write one sentence of English prose as it might have been "
                     "written in 1880. Respond with the sentence only.")
SMOKE_COMPLETION_PREFIX = ("It was in the autumn of the year 1880 that I first "
                           "came to the village of")


def cmd_smoke(args):
    """One call per model. Gates which pseudo-base models keep their quota."""
    models = ms.select(role=args.stable)
    if args.model:
        models = [m for m in ms.ALL_MODELS if m.model_id in set(args.model)]
    models = [m for m in models if m.endpoint != ms.LOCAL]

    client = make_client(args.credentials)
    tally = CostTally(cap=args.budget_cap)
    results = []
    for spec in models:
        prompt = (SMOKE_COMPLETION_PREFIX if spec.endpoint == ms.COMPLETIONS
                  else SMOKE_CHAT_PROMPT)
        started = time.time()
        row = {"model_id": spec.model_id, "endpoint": spec.endpoint,
               "role": spec.role}
        try:
            job = {"endpoint": spec.endpoint, "model_id": spec.model_id,
                   "prompt": prompt, "reasoning_effort": spec.reasoning_effort}
            text = issue(client, job, max_tokens=120)
            row.update({"ok": bool(text and text.strip()),
                        "latency_s": round(time.time() - started, 2),
                        "response": (text or "").strip()[:200],
                        "response_tokens": estimate_tokens(text)})
            tally.record(spec.model_id, prompt, text)
        except Exception as exc:                                   # noqa: BLE001
            row.update({"ok": False, "latency_s": round(time.time() - started, 2),
                        "error": f"{type(exc).__name__}: {exc}"[:300]})
        results.append(row)
        if not args.json:
            status = "ok  " if row.get("ok") else "FAIL"
            print(f"{status} {spec.model_id:45s} {spec.endpoint:12s} "
                  f"{row.get('latency_s', 0):6.2f}s  "
                  f"{row.get('error', row.get('response', ''))[:70]}",
                  file=sys.stderr)

    passed = [r for r in results if r.get("ok")]
    failed_base = [r["model_id"] for r in results
                   if not r.get("ok") and r["endpoint"] == ms.COMPLETIONS]
    out = {"results": results, "n_ok": len(passed), "n_total": len(results),
           "pseudo_base_failures": failed_base,
           "surviving_pseudo_base": [r["model_id"] for r in results
                                     if r.get("ok") and r["endpoint"] == ms.COMPLETIONS],
           "cost": tally.summary()}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"\n{len(passed)}/{len(results)} ok; "
              f"pseudo-base survivors: {out['surviving_pseudo_base']}",
              file=sys.stderr)
        print(f"estimated cost ${tally.total_usd:.4f}", file=sys.stderr)
    return 0 if passed else 1


# ---------------------------------------------------------------------------
# Subcommand: summaries (constrained-generation pre-pass, §5.2)
# ---------------------------------------------------------------------------

SUMMARY_PROMPT = ("Summarize the following passage in one short sentence, in "
                  "plain modern English. Respond with the summary only.\n\n")


def pick_uncommon_words(text, lexicon=None, k=3):
    """Content words from the passage, skipping the top-100 stopword list.

    Same guard `sample_fewshot_prep` uses: `TOP100_ENGLISH_WORDS` plus lexicon
    membership, so the required word is a real period word and not an OCR artifact.
    """
    from sample_passages import TOP100_ENGLISH_WORDS
    seen, out = set(), []
    for token in re.findall(r"[A-Za-z][A-Za-z'-]+", text or ""):
        low = token.lower()
        if low in TOP100_ENGLISH_WORDS or len(low) < 5 or low in seen:
            continue
        if lexicon is not None and low not in lexicon:
            continue
        seen.add(low)
        out.append(low)
        if len(out) >= k:
            break
    return out


def cmd_summaries(args):
    lexicon = load_lexicon()
    positives = load_positives(args.positives_in)
    eligible = [r for r in positives if r.get("eligible_constrained_generation")]
    rng = random.Random(args.seed)
    rng.shuffle(eligible)

    done = set(load_summaries(args.out))
    todo = [r for r in eligible if r["passage_id"] not in done][:args.n]
    todo = todo[args.start_line:]
    print(f"{len(done)} cached; generating {len(todo)}", file=sys.stderr)

    client = None if args.dry_run else make_client(args.credentials)
    tally = CostTally(cap=args.budget_cap)
    written = 0
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        for row in todo[:5]:
            print((SUMMARY_PROMPT + row["text"])[:300], file=sys.stderr)
        print(f"dry run: would summarize {len(todo)} passages", file=sys.stderr)
        return 0

    from concurrent.futures import ThreadPoolExecutor

    def attempt(row):
        prompt = SUMMARY_PROMPT + row["text"]
        try:
            return row, prompt, call_chat(client, args.model, prompt,
                                          max_tokens=80), None
        except Exception as exc:                                   # noqa: BLE001
            return row, prompt, None, exc

    started = time.time()
    width = max(1, args.concurrency)
    with ThreadPoolExecutor(max_workers=width) as pool:
        for i in range(0, len(todo), width):
            if tally.exceeded:
                print(f"budget cap ${tally.cap} reached; stopping", file=sys.stderr)
                break
            for row, prompt, summary, exc in pool.map(attempt, todo[i:i + width]):
                if exc is not None:
                    print(f"error on {row['passage_id']}: {exc}", file=sys.stderr)
                    continue
                tally.record(args.model, prompt, summary)
                with open(args.out, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "passage_id": row["passage_id"],
                        "volume_id": row.get("volume_id"),
                        "summary": (summary or "").strip(),
                        "uncommon_words": pick_uncommon_words(row["text"], lexicon),
                        "generated_at": datetime.now(timezone.utc)
                                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }, ensure_ascii=False) + "\n")
                written += 1
            if (i + width) % 400 < width:
                rate = (i + width) / max(time.time() - started, 1e-6)
                print(f"  {written} summaries, ${tally.total_usd:.2f}, "
                      f"{rate:.1f}/s", file=sys.stderr)
    print(json.dumps({"written": written, "cost": tally.summary()}, indent=2),
          file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# Subcommand: run
# ---------------------------------------------------------------------------

def cmd_run(args):
    ms.assert_holdout_integrity()
    rng = random.Random(args.seed)
    lexicon = load_lexicon()
    length_table = load_length_table(args.length_table)

    state = scan_negatives(args.out)
    print(f"negatives.jsonl holds {state['n_rows']} rows "
          f"({dict(state['by_provenance'])})", file=sys.stderr)

    # The quota plan is rebuilt from what the file actually holds, not from
    # model_stable's defaults: reuse delivered 5,301/1,099 rather than 5,760/640,
    # and only the file knows that.
    pm = state["by_provenance_modality"]
    plan = ms.quota_plan(
        total=args.total,
        reuse_infill=pm.get(("bertclassify_reuse", INFILL), 0),
        reuse_continuation=pm.get(("bertclassify_reuse", CONTINUATION), 0),
        talkie_continuation=pm.get(("talkie_local", CONTINUATION),
                                   ms.DEFAULT_TALKIE_CONTINUATION),
        talkie_fewshot=pm.get(("talkie_local", FEW_SHOT),
                              ms.DEFAULT_TALKIE_FEWSHOT),
        available_pseudo_base=args.pseudo_base or None)

    quota = remaining_quota(plan, state, role=args.role)
    if args.modality:
        quota = {k: v for k, v in quota.items() if k[1] in set(args.modality)}
    if args.model:
        quota = {k: v for k, v in quota.items() if k[0] in set(args.model)}
    print(f"outstanding quota: {sum(quota.values())} rows across {len(quota)} "
          f"(model, modality) pairs", file=sys.stderr)

    # Length targets come from the complement of what is already in the file.
    comp_table = complement_length_table(length_table, state["length_rows"],
                                         args.total)

    positives = load_positives(args.positives_in)
    infill_prep, fewshot_prep = load_prep(args.prep_in)
    pools = build_job_pools(positives, infill_prep, fewshot_prep, rng, state)
    titles = load_titles(args.roster)
    summaries = load_summaries(args.summaries_in)

    jobs = plan_jobs(quota, pools, rng, comp_table, titles, summaries,
                     limit=args.limit)
    print(f"planned {len(jobs)} jobs", file=sys.stderr)

    if args.dry_run:
        for job in jobs[:args.show]:
            print("-" * 70, file=sys.stderr)
            print(f"{job['model_id']} | {job['modality']} | {job['prompt_variant']} "
                  f"| date_in_prompt={job['date_in_prompt']} | {job['endpoint']}",
                  file=sys.stderr)
            print(job["prompt"][:600], file=sys.stderr)
        print(json.dumps(summarize_jobs(jobs), indent=2), file=sys.stderr)
        return 0

    client = make_client(args.credentials)
    tally = CostTally(cap=args.budget_cap)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    per_model = defaultdict(Counter)
    attempts = Counter()
    written = 0

    # Concurrency: 23,600 serial calls is a ~16-hour job, so requests run in a
    # thread pool. **Not** in lock-step waves: per-call latency across this
    # stable ranges from 0.5s to 14s, and a wave that waits for its slowest
    # member throughs at `width / max_latency` instead of
    # `width / mean_latency` -- measured at 0.4/s with width 10, a 16-hour ETA.
    # Instead the pool is kept continuously full: each completion immediately
    # submits the next job. The budget cap is checked on every completion, so
    # it still stops the run promptly.
    from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

    def attempt(job):
        try:
            raw = issue(client, job, max_tokens=args.max_tokens,
                        temperature=args.temperature)
            return job, raw, None
        except Exception as exc:                                   # noqa: BLE001
            return job, None, exc

    started = time.time()
    width = max(1, args.concurrency)
    issued = 0
    stopping = False

    with ThreadPoolExecutor(max_workers=width) as pool:
        pending = set()
        for job in jobs[:width]:
            pending.add(pool.submit(attempt, job))
            issued += 1

        while pending:
            done_set, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done_set:
                job, raw, exc = future.result()
                # Tally per model as well as overall: §7.6 wants a per-generator
                # leakage rate, and "above ~5% for any generator means it has
                # memorized the corpus" is not answerable from a pooled count.
                # Rejected rows are never written, so the log is the only record.
                attempts[job["model_id"]] += 1
                if exc is not None:
                    stats[f"api_error:{type(exc).__name__}"] += 1
                    per_model[job["model_id"]][f"api_error:{type(exc).__name__}"] += 1
                else:
                    tally.record(job["model_id"], job["prompt"], raw)
                    verdict = qc_negative(
                        raw, lexicon=lexicon, references=job["references"],
                        bookend_before=job["bookend_before"],
                        bookend_after=job["bookend_after"],
                        target_sentences=job["target_sentences"],
                        target_words=job["target_words"])
                    if verdict["ok"]:
                        append_row(negative_row(job, raw, verdict, args.role,
                                                args.temperature), args.out)
                        written += 1
                        stats["accepted"] += 1
                        per_model[job["model_id"]]["accepted"] += 1
                    else:
                        stats[f"qc:{verdict['reason']}"] += 1
                        per_model[job["model_id"]][f"qc:{verdict['reason']}"] += 1

                if tally.exceeded and not stopping:
                    stopping = True
                    print(f"budget cap ${tally.cap} reached after {written} "
                          f"rows; draining", file=sys.stderr)

                # Refill: keep the pool saturated rather than waiting for peers.
                if not stopping and issued < len(jobs):
                    pending.add(pool.submit(attempt, jobs[issued]))
                    issued += 1

                if issued % 250 == 0:
                    rate = issued / max(time.time() - started, 1e-6)
                    eta = (len(jobs) - issued) / max(rate, 1e-6) / 60
                    print(f"  {issued}/{len(jobs)} issued, {written} kept, "
                          f"${tally.total_usd:.2f}, {rate:.1f}/s, ETA {eta:.0f}m",
                          file=sys.stderr)

    # §7.6: "above ~5% for any generator means it has memorized the source
    # corpus; move its infill quota to constrained generation."
    leakage = {m: round(per_model[m].get("qc:leakage_ngram", 0)
                        / max(attempts[m], 1), 4)
               for m in sorted(attempts)}
    flagged = [m for m, rate in leakage.items() if rate > 0.05]
    print(json.dumps({"written": written, "stats": dict(stats.most_common()),
                      "attempts_by_model": dict(attempts),
                      "leakage_rate_by_model": leakage,
                      "leakage_flagged_over_5pct": flagged,
                      "rejections_by_model": {m: dict(c.most_common())
                                              for m, c in sorted(per_model.items())},
                      "cost": tally.summary()}, indent=2), file=sys.stderr)
    return 0


def summarize_jobs(jobs):
    return {
        "n_jobs": len(jobs),
        "by_modality": dict(Counter(j["modality"] for j in jobs)),
        "by_model": dict(Counter(j["model_id"] for j in jobs).most_common()),
        "by_variant": dict(Counter(j["prompt_variant"] for j in jobs)),
        "by_endpoint": dict(Counter(j["endpoint"] for j in jobs)),
        "date_in_prompt": dict(Counter(j["date_in_prompt"] for j in jobs)),
        "leakage_checkable": dict(Counter(j["leakage_checkable"] for j in jobs)),
        "by_decade": dict(sorted(Counter(
            j["source"].get("decade") for j in jobs).items(),
            key=lambda kv: (kv[0] is None, kv[0]))),
    }


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args):
    state = scan_negatives(args.negatives_in)
    keys = args.by or ["provenance", "modality", "model"]
    out = {"n_rows": state["n_rows"]}
    mapping = {"model": "by_model", "modality": "by_modality",
               "provenance": "by_provenance", "split_role": "by_split_role"}
    for key in keys:
        if key == "decade":
            continue
        out[key] = dict(Counter(state[mapping[key]]).most_common())
    if "decade" in keys:
        decades = Counter()
        with open(args.negatives_in, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    decades[json.loads(line).get("source_decade")] += 1
        out["decade"] = dict(sorted(decades.items(),
                                    key=lambda kv: (kv[0] is None, kv[0])))
    if args.format == "json":
        print(json.dumps(out, indent=2))
    else:
        for key, counts in out.items():
            if key == "n_rows":
                print(f"n_rows: {counts}")
                continue
            print(f"\n{key}:")
            for k, v in counts.items():
                print(f"  {str(k):50s} {v}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("smoke", help="one call per model, both endpoints")
    sp.add_argument("--stable", choices=[ms.TRAIN, ms.EVAL_HOLDOUT, "all"],
                    default="all")
    sp.add_argument("--model", action="append", default=None)
    sp.add_argument("--json", action="store_true")
    sp.add_argument("--credentials", default=None)
    sp.add_argument("--budget-cap", type=float, default=DEFAULT_BUDGET_CAP)
    sp.set_defaults(func=cmd_smoke)

    up = sub.add_parser("summaries", help="constrained-generation pre-pass")
    up.add_argument("--positives-in", default=str(DEFAULT_POSITIVES))
    up.add_argument("--n", type=int, default=6400)
    up.add_argument("--model", default=SUMMARY_MODEL)
    up.add_argument("--out", default=str(DEFAULT_SUMMARIES))
    up.add_argument("--start-line", type=int, default=0)
    up.add_argument("--seed", type=int, default=DEFAULT_SEED)
    up.add_argument("--credentials", default=None)
    up.add_argument("--budget-cap", type=float, default=DEFAULT_BUDGET_CAP)
    up.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    up.add_argument("--dry-run", action="store_true")
    up.set_defaults(func=cmd_summaries)

    rp = sub.add_parser("run", help="main elicitation loop")
    rp.add_argument("--positives-in", default=str(DEFAULT_POSITIVES))
    rp.add_argument("--prep-in", default=str(DEFAULT_PREP))
    rp.add_argument("--summaries-in", default=str(DEFAULT_SUMMARIES))
    rp.add_argument("--roster", default=str(DEFAULT_ROSTER))
    rp.add_argument("--length-table", default=str(DEFAULT_LENGTH_TABLE))
    rp.add_argument("--out", default=str(DEFAULT_NEGATIVES))
    rp.add_argument("--total", type=int, default=ms.DEFAULT_TOTAL)
    rp.add_argument("--modality", action="append", default=None,
                    choices=list(ms.MODALITIES))
    rp.add_argument("--model", action="append", default=None)
    rp.add_argument("--pseudo-base", action="append", default=None,
                    help="model ids that passed `smoke`; others lose their quota")
    rp.add_argument("--role", choices=[ms.TRAIN, ms.EVAL_HOLDOUT], default=ms.TRAIN)
    rp.add_argument("--limit", type=int, default=None)
    rp.add_argument("--start-line", type=int, default=0,
                    help="kept for CLI compatibility; resume is quota-aware and "
                         "derived from the output file, not from line offsets")
    rp.add_argument("--budget-cap", type=float, default=DEFAULT_BUDGET_CAP)
    rp.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    rp.add_argument("--max-tokens", type=int, default=400)
    rp.add_argument("--temperature", type=float, default=1.0)
    rp.add_argument("--seed", type=int, default=DEFAULT_SEED)
    rp.add_argument("--credentials", default=None)
    rp.add_argument("--show", type=int, default=6,
                    help="prompts to print under --dry-run")
    rp.add_argument("--dry-run", action="store_true")
    rp.set_defaults(func=cmd_run)

    pp = sub.add_parser("report", help="counts over negatives.jsonl")
    pp.add_argument("--negatives-in", default=str(DEFAULT_NEGATIVES))
    pp.add_argument("--by", action="append", default=None,
                    choices=["model", "modality", "decade", "split_role",
                             "provenance"])
    pp.add_argument("--format", choices=["table", "json"], default="table")
    pp.set_defaults(func=cmd_report)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
