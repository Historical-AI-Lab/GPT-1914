# Plan: Remove LLM context scoring; route context to human judges (book_context only)

> **Superseded.** This document predates the current two-path framing. ChronoLogic
> no longer claims a divide between a "question fit" construct and a "context fit"
> construct; it has a binary **pass/fail path** (`judge_scoring_nocontext.py`,
> instruction following + factual accuracy) and a continuous **partial-credit path**
> (`bt_context_scoring.py`) whose criteria are a superset of those. The final scoring
> stage is `score_substantive.py`. Kept as a record of the reasoning at the time.
> See `substantive-uncertainty-spec.md` and `estimator_and_calibration_explained.md`.

## Motivation

LLM judge type-II error on *context fit* is too high. Decision: the LLM judge
scores **question fit only**. Context fit is scored by a **human judge, but only
for `frame_type == "book_context"` questions** (~216). world_context/passage_context
questions get no context score (NA → pass downstream). Style remains unchanged.

## Files changed

| File | Change |
|---|---|
| `judge_prompts_nocontext.py` | NEW — question-only prompt/parse/score API |
| `judge_alpha_reliability_nocontext.py` | Replaces old `judge_reliability.py`; question-only |
| `judge_beta_reliability_nocontext.py` | Fixes broken import; question-only beta |
| `judge_scoring_nocontext.py` | LLM scores question only; adds book_context routing |
| `human_scoring.py` | Collect context_fit for all book_context qnums |
| `score_calculation.py` | Docstring update only (logic already handles None) |
| `judge_agreement_report.py` | Guard context_fit possibly absent |
| `tests/test_judge_prompts.py` | Target nocontext module |
| `tests/test_judge_scoring.py` | Target nocontext modules; question-only schema |
| `tests/test_judge_beta_reliability.py` | Target nocontext module; question_fit only |

## CLI reference

All CLIs are unchanged from the deprecated originals except where noted.

### judge_alpha_reliability_nocontext.py (replaces judge_reliability.py)
```
python judge_alpha_reliability_nocontext.py --judge MODEL_ID [options]

  --judge MODEL_ID              (required) e.g. anthropic/claude-opus-4-7
  --benchmark PATH              Default: ../booksample/chronologic_en_0.2.jsonl
  --openrouter-credentials PATH Default: ../bertclassify/OpenRouterCredentials.txt
  --openai-credentials PATH     Default: ../evalcode/credentials.txt
  --reasoning-effort LEVEL      none|low|medium|high (default: none)
  --output PATH                 Override output path
  --limit N                     Process only N questions
  --seed INT                    RNG seed (default: 17)
  --debug                       Print raw judge responses

Output: llm_reliability/{judge}__{version}.json
        Per-question: question_correct, question_total, question_r,
                      question_invalid, question_weight
        (No context_* fields)
```

### judge_beta_reliability_nocontext.py (replaces judge_beta_reliability.py)
```
python judge_beta_reliability_nocontext.py --judge MODEL_ID [options]

  --judge MODEL_ID              (required)
  --benchmark PATH              Default: ../booksample/chronologic_en_0.3.jsonl
  --alternate-gt PATH           Default: derived from --benchmark
  --openrouter-credentials PATH Default: ../bertclassify/OpenRouterCredentials.txt
  --openai-credentials PATH     Default: ../evalcode/credentials.txt
  --reasoning-effort LEVEL      none|low|medium|high (default: none)
  --output PATH                 Override output path
  --limit N                     Process only first N pairs
  --seed INT                    RNG seed (default: 17)
  --debug                       Print raw judge responses
  --dry-run                     Print pair counts and length split, then exit

Output: beta_reliability/{judge}__{version}.json
        overall/by_length_bin contain only question_fit tally
        (No context_fit tallies)
```

### judge_scoring_nocontext.py (replaces judge_scoring.py)
```
python judge_scoring_nocontext.py FREE_GEN_FILE --judge MODEL_ID [options]

  FREE_GEN_FILE                 Output from free_generation.py
  --judge MODEL_ID              (required)
  --benchmark PATH              Benchmark JSONL; now also used to load frame_type.
                                Default: ../booksample/chronologic_en_0.2.jsonl
  --reliability PATH            Pre-computed LLM reliability JSON
  --openrouter-credentials PATH Default: ../bertclassify/OpenRouterCredentials.txt
  --openai-credentials PATH     Default: ../evalcode/credentials.txt
  --reasoning-effort LEVEL      none|low|medium|high (default: none)
  --output PATH                 Override output path
  --start QNUM                  Resume from this question number
  --limit N                     Process only N questions
  --seed INT                    Random seed (default: 17)
  --debug                       Print full judge responses

Output: scored_answers/judge_{judge}__{candidate}__{version}.json
        question_fit: populated by LLM
        context_fit: {} (populated later by human_scoring.py)
        book_context_qnums: list of qnums needing human context judgment
        needs_human: question_fit (low reliability) + context_fit (book_context)
```

### human_scoring.py (unchanged CLI; changed behavior)
```
python human_scoring.py JUDGE_FILE [options]

  JUDGE_FILE                    scored_answers/judge_*_human.json
  --free-gen PATH               Free-gen JSON; auto-located if omitted
  --log PATH                    Cumulative judgment log (default: human_judgments.jsonl)
  --output PATH                 Override output path
  --reliability F               Human reliability (skips interactive prompt)
  --resume                      Skip already-judged (qnum, aspect) pairs

Now requests context_fit for ALL book_context questions (from book_context_qnums
in the judge file), in addition to question_fit for low-reliability LLM scores.
```

## Validation commands (run from modelasjudge/)

```bash
# 1. Unit tests (no network)
pytest tests/test_judge_prompts.py tests/test_judge_scoring.py \
       tests/test_judge_beta_reliability.py -v

# 2. Prompt sanity check
python -c "
import sys; sys.path.insert(0, '.')
from judge_prompts_nocontext import build_judge_prompt
p = build_judge_prompt('ctx', 'Who?', 'Alice', 'Bob', 'knowledge')
assert 'Context fit' not in p
assert 'Source:' not in p
assert 'question fit' in p.lower()
print('PASS: prompt is question-only')
"

# 3. Alpha reliability smoke (3 questions, ~6 real LLM calls)
python judge_alpha_reliability_nocontext.py --judge openai/gpt-4o-mini --limit 3 --debug

# 4. Beta reliability dry-run
python judge_beta_reliability_nocontext.py --judge openai/gpt-4o-mini --dry-run

# 5. Scoring smoke (5 questions, also tests book_context routing)
python judge_scoring_nocontext.py generated_answers/free_gen_gpt-4.1__0.2.json \
    --judge openai/gpt-4o-mini --limit 5

# 6. Human scoring (non-interactive, reliability=0.9)
python human_scoring.py scored_answers/judge_openai_gpt-4o-mini__gpt-4.1__0.2.json \
    --reliability 0.9

# 7. Final score calculation
python score_calculation.py gpt-4.1__0.2
python judge_agreement_report.py scored_answers/final_gpt-4.1__0.2.json
```

## Deferred (separate follow-up plan)

`bootstrap_confidence.py` and `bayes_correction.py` read `context_correct`/
`context_total` (LLM Beta k/n) and `context_fit` beta tallies — all of which
vanish after this change. Reworking them for human-based context uncertainty is
a separate effort. The non-Bayesian `score_calculation.py` path is fully functional.
