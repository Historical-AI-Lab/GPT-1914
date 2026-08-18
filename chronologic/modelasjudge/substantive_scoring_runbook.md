# Substantive scoring — testing and production runbook

The automated pipeline built from `substantive-uncertainty-spec.md` (design)
and the `it-s-time-to-fuse-synchronous-squirrel` plan (implementation).
Orchestrator: `run_pipeline.py`. Scoring CLI: `score_substantive.py`. This
runbook is the sequence to go from "code merged, nothing run for real yet"
to "ledger has trustworthy rows for every candidate."

**Run every command from `modelasjudge/`.** Paste once per shell session:

```bash
cd /Users/tunder/Library/CloudStorage/Dropbox/python/GPT-1914/chronologic/modelasjudge
export PY=/Users/tunder/Library/CloudStorage/Dropbox/python/py310hf/bin/python
export BM=../booksample/chronologic_en_0.7.jsonl
export JUDGE=anthropic/claude-sonnet-4-6
export BTJUDGE=anthropic/claude-sonnet-5
```

## Observed costs (empirical — append a row each time you have a real number)

Nothing in this codebase logs token usage or cost from past API calls (checked
2026-08-17: `openrouter_client.py` sends `max_tokens` as a request parameter
but never reads back `usage`; the judgment logs record comparison metadata,
not tokens or cost). So there is no way to derive a cost estimate from local
data alone — these rows are the only ground truth we have, and are worth
recording every time a stage actually runs for real.

| date | stage | model | effort | calls | total cost | $/call |
|---|---|---|---|---:|---:|---:|
| 2026-08-18 | anchor_fit | anthropic/claude-sonnet-5 | medium | ~9,000 | ~$25 | ~$0.0028 |

Sonnet 5 pricing at time of that run: $2/$10 per 1M input/output tokens.
That $/call is *lower* than even the most optimistic bracket in this
session's pre-run estimate (which assumed a floor of ~300 reasoning tokens/
call and came out around $0.0046/call) — medium-effort reasoning on this
pairwise-comparison task is apparently using less of its thinking budget
than assumed. Treat the bracket-estimate method (input tokens measured from
a real prompt sample, output tokens guessed across a range) as a fallback
for a stage with no observed row yet, not as more reliable than an actual
observed row.

No command below carries a trailing `#` comment — interactive zsh has
`INTERACTIVE_COMMENTS` off by default, and a pasted `#` gets read as an
argument. `setopt interactivecomments` first if you want inline comments to
work.

---

## Step 0 — fix the benchmark before anything else touches it

Two questions were just added to `chronologic_en_0.7.jsonl` (qnums 888,
889). They carry `context_judged: 1` and `frame_type: book_context` —
clearly meant for the Bradley-Terry channel — but are **missing the
`partial_credit` field**. `routing.py` picks `partial_credit` as the
deciding field for the whole file the moment any record has it, and an
absent key reads as `None == 1` → `False`, so both currently fall through
to the pass/fail binary channel instead of BT. Confirm, then fix:

```bash
$PY -c "
from substantive.routing import route_questions
r = route_questions('$BM')
print(r.basis, len(r.pass_fail), len(r.partial))"
```

If this prints anything other than `partial_credit 554 312` (or whatever
your true intended split is), the two new questions are still misrouted —
add `\"partial_credit\": 1` to both records and re-run the check before
proceeding. **Every artifact downstream — reliability data, anchor fits,
LOO, calibration, delta draws — is keyed by which channel a question lands
in, so getting this right first is cheaper than re-fitting later.**

Once routing is correct, update the regression pin that guards against this
exact class of bug recurring:

```
tests/test_substantive_routing.py:91-92
    assert len(routing.pass_fail) == 554     # -> new correct count
    assert len(routing.partial) == 310       # -> new correct count
```

---

## Step 1 — pre-flight checks (free, no judge calls)

```bash
$PY -m pytest tests/ -q -m "not llm" \
    --ignore=tests/test_bayes_correction.py --ignore=tests/test_bootstrap_confidence.py
```

Expect all green except the two pre-existing, unrelated
`test_openrouter_client.py::TestBuildExtraBody` failures (tracked
separately, not part of this pipeline).

```bash
$PY score_substantive.py identity
```

Expect `residual < 1e-9` and `OK` — this is the spec §2 algebraic identity
(display posteriors average back to the aggregate), needs no real data, and
is the fastest sanity check that nothing in the estimator math regressed.

```bash
$PY run_pipeline.py --candidate placeholder --benchmark $BM --dry-run
```

Read the stage plan and cost table. This is a pure planning step — it
reads the filesystem but writes nothing and spawns nothing except a
one-shot `python -c "import pymc"` check. Confirm:
- stage numbers/skip reasons make sense given what's already on disk
- the `--pool-pilot` note (if it fires) matches your expectation — see
  **Known gaps** below
- the cost table's total is a number you're prepared to spend

---

## Step 2 — instrument-column artifacts (shared across every candidate)

These six stages (0–3, then 4–7) are per-`(judge, benchmark, prompt_mode,
prior_scale)` combination, not per-candidate. Run them once; every
candidate scored afterward reuses them.

```bash
$PY run_pipeline.py --candidate placeholder --benchmark $BM \
    --judge $JUDGE --bt-judge $BTJUDGE --judge-effort medium \
    --stop-after calibrate
```

(`--candidate placeholder` is required by the CLI but unused by stages
0–7; any string works.) Each stage prints its own progress and checkpoints
to its own output file — if the process dies or you Ctrl-C, re-run the
identical command and it resumes from wherever it stopped (plan §3: every
long stage owns its SIGINT handler and its own resumable output).

**Cost reality check before stage 4 (anchor-fit) and stage 5 (LOO) run for
real** — these are the two long poles (§8: ~9,150 calls / ~310 fits for
anchor-fit, ~3,900 calls / ~410 fits for LOO at the default 80-question
subsample). If you want to see the exact call count before committing:

```bash
$PY run_pipeline.py --candidate placeholder --benchmark $BM \
    --judge $JUDGE --bt-judge $BTJUDGE --judge-effort medium \
    --only anchor_fit,loo --dry-run
```

**Pooling the pilot's 40 questions into calibration** (recommended — it's
free LOO data you already have): emit namespaced labels once, then pass
them explicitly.

```bash
$PY bt_context_scoring.py emit-pilot-labels \
    --judge $BTJUDGE --judge-effort medium \
    --pilot-benchmark ../booksample/chronologic_btpilot_0.1.jsonl \
    --output bt_artifacts/pilot_labels.jsonl

$PY run_pipeline.py --candidate placeholder --benchmark $BM \
    --judge $JUDGE --bt-judge $BTJUDGE --judge-effort medium \
    --pilot-labels bt_artifacts/pilot_labels.jsonl \
    --only calibrate --force calibrate
```

(`--force calibrate` because stage 7 will already show as skipped if you
ran it without pilot labels in the first pass above — force re-runs it
with pooling.)

### Decision gate (plan §8, after stage 7)

Before spending any per-candidate budget, score **one** candidate all the
way through (Step 3 below) and then run:

```bash
$PY score_substantive.py checks \
    --scored-file scored_answers/judge_*__<that-candidate>__0.7__*.json \
    --report results/checks_<that-candidate>.md
```

Read three numbers in the output:
1. **Layer ablation** — does instrument noise (layer 2) meaningfully widen
   the interval versus judgment + item-sampling alone? If yes, §8.7's
   advice to enlarge the calibration set is now urgent — grow
   `--loo-subsample` *before* running the rest of the candidate roster,
   because widening it later means re-fitting LOO for every prior
   candidate's ledger row to stay comparable.
2. **Jeffreys vs uniform** — how much does the α-prior choice move the
   pass/fail number? Confirms the prior choice isn't quietly load-bearing.
3. **Alpha ×1.5 sensitivity** — a stand-in for "how wrong would this be if
   the reliability estimate were noisier than measured."

Only after reading these should you commit the full candidate roster's
budget.

---

## Step 3 — per-candidate scoring

Repeat for each candidate model:

```bash
$PY run_pipeline.py --candidate <MODEL_ID> --candidate-label <LABEL> \
    --candidate-effort <none|minimal|low|medium|high> \
    --benchmark $BM --judge $JUDGE --bt-judge $BTJUDGE --judge-effort medium
```

Since stages 0–7 are already satisfied, this only runs 8–11: free
generation, pass/fail judging, BT scoring, and the final
`score_substantive.py score` that writes the report and upserts the
ledger row. Cost is roughly 864 + 554 + (310 × 11) calls per candidate
(§8) — the free-generation and pass/fail-judging counts scale with your
corrected total question count from Step 0.

**After each candidate**, spot-check before moving to the next:

```bash
tail -30 results/report_<label>__0.7.md
column -s, -t results/chronologic_scores.csv | less -S
```

Confirm the report's headline pooled-equal-weight number and its 95% CI
are what you'd expect given the candidate's reputation, and that
`n_excluded_floor` is 0 or small (a large excluded count means many
questions had an uninformative judge for this candidate — worth
investigating, not silently accepting).

---

## End-to-end sanity checks (run once, cheaply, before trusting the ledger)

**1. The mismatch guard actually fires** — confirm draw banks from
different instruments can't silently combine into a wrong number:

```bash
$PY score_substantive.py score --scored-file <a 0.7 scored file> \
    --calib-draws bt_artifacts/bt_calib_draws_<a 0.1 pilot tag>.npz
```

Expect `ArtifactMismatch` naming `benchmark_version`, not a number.

**2. Ledger and report agree.** Every number in a ledger row must also
appear, formatted, in that row's report — `tests/test_substantive_report.py`
pins this at the unit level; spot-check it once on a real row too:

```bash
diff <(grep -oE '[0-9]+\.[0-9]+%?' results/report_<label>__0.7.md | sort -u) \
     <(grep <label> results/chronologic_scores.csv)
```

(Informal — the point is eyeballing that the report and CSV tell the same
story, not an automated diff.)

**3. Regression against the old pipeline** (plan §9) — on a candidate you
also scored under the pre-substantive-pipeline code, confirm the new
`--alpha-prior uniform` number is close to the old raw/range-normalized
number, and that switching to Jeffreys moves it in the expected direction.

**4. Freeze anything that will be cited.** If a number is going in a paper
or a report someone else will read later:

```bash
$PY score_substantive.py score --scored-file <file> --freeze-bank \
    results/frozen/<label>__0.7.npz
```

`--frozen-bank results/frozen/<label>__0.7.npz` on a later run reproduces
that exact number bit-for-bit even after the producing artifacts (draw
banks, reliability files) move or get refit.

---

## Moving to production

"Production" here means: every candidate in your roster has a ledger row,
the decision-gate checks have been read once and acted on, and the
instrument-column artifacts are stable enough that re-running a candidate
doesn't silently change under it.

- **Don't refit stages 0–7 casually.** Anything that changes them (a new
  `--loo-subsample`, a different `--prior-scale`, adding pilot pooling
  after already scoring candidates without it) changes the instrument that
  every already-scored candidate was measured against. Either refit before
  scoring anyone, or accept that pre- and post-refit candidates aren't
  directly comparable and say so in `notes`.
- **`results/chronologic_scores.csv` is the source of truth**, upserted by
  key `(benchmark_version, candidate_label, candidate_effort, judge,
  judge_effort, bt_tag)`. Re-running a candidate after a bug fix replaces
  its row; it does not duplicate it.
- **`results/score_history.jsonl`** is the append-only audit trail with
  full provenance and every replicate array — keep it, don't prune it; it's
  what makes a published number re-derivable later.
- **Style is opt-in and cohort-scoped**, not per-row automatic. Run it
  once you have your full candidate set assembled:

  ```bash
  $PY run_pipeline.py --candidate placeholder --benchmark $BM \
      --only style_refresh --force style_refresh --refresh-style
  ```

  This writes `results/style_report_<cohort>.md` and
  `results/style_report_stats_<cohort>.json` but does **not** write style
  columns into the ledger (see Known gaps) — pull the numbers in by hand
  for now.

---

## Troubleshooting

- **A stage fails mid-run:** `run_pipeline.py` prints the exact resume
  command and stops (plan §5's failure policy: stop on first failure,
  never delete a partial output). Fix the underlying issue, then paste the
  printed command — every stage resumes by re-invocation.
- **Re-run just one stage:** `--only <name-or-number>`. Re-run a stage even
  though it looks satisfied: `--only <stage> --force <stage>`.
- **Stop after a specific stage** (e.g. to inspect artifacts before
  spending on the next): `--stop-after <name-or-number>`.
- **A skip reason looks wrong:** skip predicates are content-based (keys
  present in a JSON/npz) where cheap, mtime-based otherwise — if a stage
  is skipping when it shouldn't, check whether its output file is stale
  but *newer* than its input (mtime lies) versus genuinely incomplete
  (content check should catch this; if it doesn't, that's a bug in
  `run_pipeline.py`, not your data).

---

## Known gaps (deliberate, not oversights)

- **`--pool-pilot`** needs `--pilot-labels PATH` explicitly passed (see
  Step 2) — there's no auto-discovered convention for that file yet.
  Without it, `run_pipeline.py` prints a note and proceeds unpooled.
- **`--length-covariate`** on `bt_context_scoring.py calibrate` fits and
  banks the 3-parameter draws, but `score_substantive.py` still scores
  with the 2-parameter calibration — the estimator side isn't wired yet.
- **Style columns aren't auto-joined into the ledger.** The join between
  `typicality.py`'s per-model stats (keyed on free-gen's raw `model`
  field) and the ledger's `candidate_label`/`candidate_model` columns
  isn't verified, so `run_pipeline.py --refresh-style` computes and prints
  the numbers but leaves the ledger's style columns for you to fill in.
