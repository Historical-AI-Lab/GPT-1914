# Benchmark diff: 0.2 → 0.4

- **Old file:** `booksample/chronologic_en_0.2.jsonl`  (714 questions)
- **New file:** `booksample/chronologic_en_0.4.jsonl`  (712 questions)
- **Prompt fields:** metadata_frame, main_question, answer_strings, answer_types, answer_probabilities

## Summary

| Stat | Count |
|------|-------|
| Questions in 0.2 | 714 |
| Questions in 0.4 | 712 |
| Deleted (in 0.2, not 0.4) | 2 |
| Added (in 0.4, not 0.2) | 0 |
| Prompt-visible changes → re-run | 14 |
| Subset-label-only changes (no re-run) | 1 |
| Other field changes (passage etc., no re-run) | 5 |

## Deleted questions (present in 0.2, absent from 0.4)

- **qnum 20**: "What is the name of the port that is located in Moquegua and through which much of Bolivian trade passes?"
- **qnum 321**: "Moreover, the propagation of the current is stopped by a ligature, or by crushing the nerve. We may speak of the con...

## Prompt-visible changes → re-run (14 questions)

### qnum 2
Changed fields: answer_probabilities, answer_strings, answer_types

**answer_probabilities**
- OLD: `[1.0, 0.0, 0.0, 0.0, 0.0]`
- NEW: `[1.0, 1.0, 0.0, 0.0, 0.0, 0.0]`

**answer_strings**
- OLD: `["Colonel John Endicott", "Lieutenant Lefebvre", "Natty Bumppo", "Benjamin Franklin", "insufficient information"]`
- NEW: `["Colonel John Endicott", "John Mason", "Lieutenant Lefebvre", "Natty Bumppo", "Benjamin Franklin", "insufficient inf...`

**answer_types**
- OLD: `["ground_truth", "manual", "manual", "manual", "manual"]`
- NEW: `["ground_truth", "ground_truth", "manual", "manual", "manual", "manual"]`

### qnum 63
Changed fields: main_question

**main_question**
- OLD: `"The character in question here is Coupe-tête, who is described this way in the book:\n\"This is a well-made active y...`
- NEW: `"The character in question here is Coupe-tête, who is described this way in the book:\n\"This is a well-made active y...`

### qnum 97
Changed fields: answer_strings

**answer_strings**
- OLD: `["But how would you explain this working of His power? We are too fond of explaining things nowadays. And until we kn...`
- NEW: `["We are too fond of explaining things nowadays. I think we should do well to follow the example of the Cherubim who ...`

### qnum 116
Changed fields: main_question

**main_question**
- OLD: `"The character in question here is Marquis de Rosnay, who is described this way in the book:\n\"He was a beautiful ol...`
- NEW: `"The character in question here is Marquis de Rosnay, who is described this way in the book:\n\"He was a beautiful ol...`

### qnum 149
Changed fields: main_question

**main_question**
- OLD: `"He may understand the end of the way of sensuality by looking at any old pleasure-seeker, Gray, and gap-toothed, and...`
- NEW: `"He may understand the end of the way of sensuality by looking at any old pleasure-seeker, Gray, and gap-toothed, and...`

### qnum 243
Changed fields: main_question

**main_question**
- OLD: `"In consequence of a second defeat on the 25th September, he retreated to the southern bank of the Araxes. Paskjevitc...`
- NEW: `"In consequence of a second defeat on the 25th September, he retreated to the southern bank of the Araxes. Paskjevitc...`

### qnum 329
Changed fields: main_question

**main_question**
- OLD: `"Therefore, when an electron, negatively charged, leaves an atom, there is then less negative electricity than positi...`
- NEW: `"Therefore, when an electron, negatively charged, leaves an atom, there is then less negative electricity than positi...`

### qnum 331
Changed fields: main_question

**main_question**
- OLD: `"The two types of detectors which act as rectifiers are, namely, the crystal detector and the vacuum tube detector. W...`
- NEW: `"The two types of detectors which act as rectifiers are, namely, the crystal detector and the vacuum tube detector. W...`

### qnum 379
Changed fields: main_question

**main_question**
- OLD: `"It was also about this time that the Iroquois began to establish, on a considerable scale, a regular traffic with th...`
- NEW: `"It was also about this time that the Iroquois began to establish, on a considerable scale, a regular traffic with th...`

### qnum 468
Changed fields: main_question

**main_question**
- OLD: `"How many cubic feet are there in a pile of wood 26 feet long, 6 feet high, and 3 feet wide. How many cordss?"`
- NEW: `"How many cubic feet are there in a pile of wood 26 feet long, 6 feet high, and 3 feet wide. How many cords?"`

### qnum 495
Changed fields: main_question

**main_question**
- OLD: `"Suppose that your name is Jennifer Lane, you're unmarried, and you've been invited to dinner. But you dcan't go or d...`
- NEW: `"Suppose that your name is Jennifer Lane, you're unmarried, and you've been invited to dinner. But you can't go or do...`

### qnum 521
Changed fields: main_question

**main_question**
- OLD: `"Which of the following men have served as Prime Ministers of the United Kingdom? Andrew Jackson. Charles Grey. Arthu...`
- NEW: `"How many of the following men have served as Prime Ministers of the United Kingdom? Andrew Jackson. Charles Grey. Ar...`

### qnum 584
Changed fields: main_question

**main_question**
- OLD: `"Which of the following political entities govern the city of Cracow?"`
- NEW: `"Which political entity governs the city of Cracow?"`

### qnum 656
Changed fields: main_question

**main_question**
- OLD: `"The character in question here is Mr. Henderson, who is described this way in the book:\n\"tall, broad-shouldered, i...`
- NEW: `"The character in question here is Mr. Henderson, who is described this way in the book:\n\"tall, broad-shouldered, i...`

## Subset-label-only changes (no re-run, 1 questions)

### qnum 507
- **frame_type**: `"book_context"` → `"world_context"`
- **reasoning_type**: `"constrained_generation"` → `"knowledge"`

## Other field changes — passage etc. (no re-run, 5 questions)

- **qnum 64**: passage
- **qnum 65**: passage
- **qnum 66**: passage
- **qnum 647**: passage
- **qnum 648**: passage

## Mini-benchmark

Written to: `evalcode/diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl`

Run with `benchmark_evaluation.py <model> evalcode/diff_0.2_to_0.4/chronologic_diff_0.2_to_0.4.jsonl [backend flags] --output-dir evalcode/mcq_04_diff` (or `prob_04_diff`).

