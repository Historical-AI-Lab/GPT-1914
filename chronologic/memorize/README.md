# memorize - the contamination test

Ground truth in this benchmark comes from published books, so a fair question is whether
the models being tested have simply read them. This directory measures that.

The method follows [Chang et al. (2023)](https://arxiv.org/abs/2305.00118): pick proper
nouns that cannot be inferred from context — fictional names, or names obscure enough that
no amount of reasoning would recover them — blank them out of a surrounding passage, and
ask a model to fill them in. A model that has memorized the book can do this; a model that
has not, cannot.

We selected 16 books from the corpus (at a point when the corpus was 1875-1924), focusing on books that would contain fictional or highly obscure proper nouns (so a lot of fiction, along with some travelogues and autobiographical writing). In those volumes, we selected 60 proper nouns, and gave roughly 100 words of
context around each to four models: Qwen-2.5-72B, R1-distill-Llama-70B, GPT-4.1, and
GPT-5.4-medium.

None of them answered a single question correctly. Because a null result from a hard test is weak evidence, we ran a second, easier one. Reframed as multiple choice, the same items give a per-book memorization score, which can
be correlated against the same model's average skill score on real benchmark questions
drawn from that book. If memorizing a book helped, the two should move together. They do
not: *n* = 64, *r* = −0.014, *p* = 0.911.

That fits Chang et al.'s own finding that memorization risk concentrates in books
frequently quoted online — which is exactly what the corpus selection avoided.

## Running

```bash
python evaluate_memorization.py freegen    # string-match hit rate
python evaluate_memorization.py mcq        # per-book correlation against benchmark skill
```

Both modes read whatever model outputs are present in `freegen60questions/` and
`mcq60questions/` — there is no hardcoded model list, so adding a model means adding its
output file.

| File | Contents |
|---|---|
| `memobenchfull.jsonl` | The 60 proper-noun cloze items |
| `freegen60questions/`, `mcq60questions/` | Per-model answers |
| `transform_memotest.py` | Builds the MCQ form from the free-generation form |
