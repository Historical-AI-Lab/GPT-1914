model-as-judge workflow overview
==============================

This is a complete overview of the plan for model-as-judge scoring of the ChronoLogic benchmark. Other plans will be written to cover specific parts of the code.

### The big picture: scoring a single model

We allow a model to produce free-generated responses to the ChronoLogic benchmark questions.

Then each response passes through this filter:

1. Is the model response to question Q (Q_m) precisely equal to the ground truth answer (Q_gt)? If so, score it correct. If not, it passes through two judging processes.
2. A panel of LLMs judge a) the response's substantive fitness for the question, and b) appropriateness for the context (the metadata frame).
3. A discriminative model judges its stylistic fit to the period.
4. Each of those processes produces a score for each question, which can be understood as a continuous variable or as a binary T/F.
5. The continuous scores are weighted by the per-question reliability of the judges, to produce three weighted scores for the model being tested: question accuracy, fit to context, and stylistic authenticity.
6. The binary scores are combined using the rule that a question fails if it fails on any of the tests: question, context, or period. This gives us an overall accuracy figure for the model.

### The free generation part of the code

This largely already exists, in free_generation.py, which is a copy of evalcode/benchmark_free_generation.py. However, it may need to be adapted. The model-querying scripts in bertclassify/ are able to query models through Open Router, and we should make sure that free_generation.py has a comparable ability.

Note also that knowledge and abstention questions, iirc, get a slightly different prompt than other questions, stressing that questions unanswerable in the specified context should be answered "insufficient information."

We should confirm this and document the two different prompts, perhaps in a free-standing markdown document in this folder that describes the free generation process.

### The scoring process for the LLM panel, before weighting (UPDATED)

LLM judging will eventually be done by a three-judge panel, but for ease of development we can start with a single model and then write code to aggregate those scores. We'll start with Claude Opus 5.6.

Here's the prompting structure:

SHARED PROMPT = 
"""You will be asked to choose between two answers to a question.

Question: {question}

Answer A: {Q_a}

Answer B: {Q_b}

1. Question fit.
Which answer better fits the question itself? {added_specification} 
- Choose A or B. 
- Choose C only if the two answers are equally accurate and relevant to the question.

2. Context fit.
Now consider this historical context for the question:

Context: {context}

 Ignore your previous decision. Now decide which answer is something the specified source would be likely to say. An incorrect answer to the question could still be typical of the source.
 - Choose A or B.
 - Choose C only if the two answers are equally typical of the source.

{added_instruction_for_knowledge_and_abstention_questions = "If the question could not be answered in the specified historical context or makes no sense there, treat 'insufficient information' as the best possible answer."}

Respond in JSON: {"question fit": "A"|"B"|"C", "context fit": "A"|"B"|"C"}

Your response:"""

We randomly assign Q_gt and Q_m to Q_a and Q_b, to avoid any order bias.

The added_specifications for different reasoning types are:

character_modeling = "Which fits the character and situation described?"
topic_sentence = "Which provides a more appropriate introduction to the paragraph and better conveys its meaning?"
knowledge = "Which is more accurate?"
abstention = "Which is more accurate?"
inference = "Which reasons more accurately and better fulfills any specified conditions?"
sentence_cloze = "Which better completes the passage?"
phrase_cloze = "Which better completes the passage?"
constrained_generation = "Which makes more sense, and better fulfills any specified constraints?"

The code for scoring should check that the reply is in the correct JSON format. We should record whether Q_m won, lost, or tied for both categories in the final report. But the numeric scoring rule for the question is that Q_m will pass (get a value of 1) whenever it is scored *either* better than or equal to (a tie) Q_gt. Otherwise, if it's rated worse, it gets 0.

#### NEW: The --cautious command-line option for scoring

The scoring process just described is the fast, default option. It assumes there is only a single ground truth answer for each question. In reality there are often two or more ground truth options, but if we're doing a fast scoring pass it's okay to select one at random.

Also, the process just described randomizes the order of ground truth and model answer, but doesn't try both possible sequences.

A more cautious approach would consider all available ground truth answers, comparing each to the model answer -- and trying *both* possible orderings in each case. So if there were for instance two ground truth answers, this approach would ask the question four times.

This cautious approach can be selected by adding --cautious to the command when judge_scoring.py is run.

Note that to implement this option we may have to change the way output files are structured. We now need to save multiple answers for both question fit and context fit, indicating whether the judge selected GT, model answer, or tie in each case. We should consider the impacts of this change on tests, and on downstream scripts. The overall numeric scores for question fit and context fit can each be reduced to a single float by averaging the 0/1 responses produced by multiple versions of the question.

### The scoring process for the discriminative model, before weighting

We have already trained a DeBERTa model to distinguish real period text from LLM-generated infill or continuation of period text, with ~0.89 accuracy. We may later expand the training set slightly to include some contemporary text, but this is good enough for now.

We're going to use this model to create log-odds values for the model answer (Q_m) and ground truth answer (Q_gt), and then compare those two log-odds to produce both a) a continuous score in [0, 1] and b) a binary {0, 1} pass/fail score.

In order to score, we will first need to calculate log-odds for ground_truth / anachronistic distractor pairs in our benchmark, and subtract them to get a range of Δ_anachronic. (Note that same_book and same_character distractors, and other non-anachronistic distractor types should not be used here. Only distractor types that contain 'anachronistic' or that are simply 'manual,' full stop.)

We'll also select same-source pairs from our period source texts, matching the length distribution and length ratio of our benchmark pairs. We'll calculate log-odds and get a range of Δ_gt between authentic texts.

We train a logistic model with a quadratic term

logit[P(anachronic∣Δ)] = β0 ​+ β1|Δ| + β2​Δ²

Then at deployment time we measure the difference between logodds of Q_gt and Q_m to get Δ_m, and apply |max(0, Δ_m)| so candidates that beat GT count as zero gap, before using our logistic model to predict P(anachronic∣Δ_m), which is our continuous score.

For binary {0, 1} scoring we binarize the probability using a 0.5 threshold.

### Assessing the per-question reliability of judges

None of our judges are perfect, and just as importantly, some question categories don't provide much evidence for a particular kind of score. E.g., for knowledge questions answered with a proper name or brief phrase, style has little relevance. So the continuous scores for question fit, context appropriateness, and stylistic appropriateness will be *weighted* to reflect judge reliability.

Before a judge can score any candidate model, we need to first calculate the judge's reliability score for each question.

#### LLM-as-judge reliability (DEPRECATED - OLDEST)

In the case of an LLM judge, we calculate reliability per-question, because it's hard to generalize. We calculate it by using the prompt outlines above to get scores for all the ground_truth - distractor pairs in the benchmark. Since position can matter, we test with both positions. So, e.g., a question with one ground truth and four distractors would have eight comparisons.

Reliability is the fraction of times that this comparison produced a clear win for Q_gt. Ties and wins for Q_d do not count in the numerator.

We calculate this separately for both question and context scores, and call it r_q, judge reliability on the question.

Questions are then weighted by max(2r_q − 1, 0)², the inverse-variance weight under a noisy-channel model. We are effectively giving items with r_q < 0.5 zero weight.

#### LLM-judge reliability (DEPRECATED)

In the case of an LLM judge, we calculate reliability per-question, because it's hard to generalize. We calculate it by using the prompt outlines above to get scores for all the ground_truth - distractor pairs in the benchmark. Since position can matter, we test with both positions. So, e.g., a question with one ground truth and four distractors would have eight comparisons.

We produce *separate* per-question reliability estimates for question fit and context fit. The question scores produce rq_q, the context scores produce rc_q.

Scoring depends on the distractor type being compared the ground truth in this instance. A same_book distractor, for instance, is actually a good fit for the social context. It's just inappropriate for the specific question posed. So we don't penalize any reply on the context question: A, B, or C could all be correct. When the judge is assessing question fit, however, it needs to rate the ground truth better than this distractor. A tie, or a win for the distractor, both count as invalid.

Conversely, a distractor that is anachronistic or drawn from a different author may well be a good fit for the question. So we don't penalize any answers to "question fit." But it's a bad context fit, by definition. So on the context question ground truth must clearly win, or the judge is penalized.

We infer the penalties appropriate for each distractor by consulting distractor_penalties.txt, where the possible values are '

As the evaluation script runs, it reports the number of invalid answers separately for question fit and context fit, and calculates both rq_q and rc_q for each question.

Questions will ultimately be weighted by max(2r_q − 1, 0)², the inverse-variance weight under a noisy-channel model, and we might as well also calculate that and report it for both question and context in each case.

#### LLM-judge reliability (CURRENT)

In the case of an LLM judge, we calculate reliability per-question, because it's hard to generalize. We calculate it by using the prompt outlines above to get scores for all the ground_truth - distractor pairs in the benchmark. Since position can matter, we test with both positions. So, e.g., a question with one ground truth and four distractors would have eight comparisons. Note that a question with two ground truths and three distractors would have twelve comparisons! We test each ground truth against all of the distractors.

We produce *separate* per-question reliability estimates for question fit and context fit. The question scores produce q_r, the context scores produce ctx_r.

Scoring of ties depends on the distractor type being compared to ground truth in this instance. A same_book distractor, for instance, is actually a decent fit for the social context. It's just inappropriate for the specific question posed. So when assessing context, we *only penalize the model if it says the distractor is positively better than ground truth.* A tie counts as a correct answer for context. When the judge is assessing question fit, however, it needs to rate the ground truth positively better than this distractor, because a same_book distractor that has been chosen at random from the book should not really be a relevant answer for the question. A tie, or a win for the distractor, both count as invalid answers for question fit.

Conversely, a distractor that is anachronistic or drawn from a different author may well be a good fit for the question. So we don't penalize a tie for "question fit." We only penalize the model on question fit if it says the distractor is actually better. But an anachronistic answer is a a bad context fit, by definition. So on the context question ground truth must actually win; the judge is penalized for ties as well as wrong choices.

We infer the penalties appropriate for each distractor by consulting distractor_penalties.txt, where the possible values are 'both', 'context', or 'question.'

As the evaluation script runs, it reports the number of invalid answers separately for question fit and context fit, and calculates both q_r and ctx_r for each question. *Note that the denominator will be the same for the question and context calculations. All questions are counted as relevant to both fractions; it's just that the scoring rules for ties are different depending on the distractor.

Questions will ultimately be weighted by max(2r_q − 1, 0)², the inverse-variance weight under a noisy-channel model, and we might as well also calculate that and report it for both question and context in each case.

#### discriminative-judge reliability

Per-question reliability is going to be noisy. We can accept that for the LLM case because reliability is generally pretty high and we're going to ultimately have a panel of three judges, so the absolute value of noise is low and will be tempered.

For the discriminative judge, there are large categories of questions where the judge is pretty useless, since the question is factual and/or answers are short. So it makes sense to stratify reliability. We group questions in two ways: by reasoning_type and by the decile of the mean answer-length. Then we apply the logistic model described above to all the ground-truth/anachronistic distractor pairs for questions in that group, and count the judgment as correct only if P(anachronic) is > 0.5.

Calculate group-level reliability for each of the reasoning_type strata and length deciles, and set r_q for each question as min(reasoning_type, length). Then calculate its per-question weight as max(2r_q − 1, 0)². 

#### How LLM scores are calculated and aggregated if we eventually have a panel

For the continuous scores (for question fit and context fit), calculate a mean model score for each judge. Each question score will be either 0 or 1. But for the continuous scores, we weight questions as above, producing a weighted average. Then, if we have multiple judges, take the mean of the judges.

For producing an overall binary accuracy measure on the whole benchmark, see below.

### Calculating overall binary accuracy

In the overall binary scheme, a question is counted as correctly answered only if it gets > 0.5 for all three categories — question fit, context fit, and style fit.

Note that that's a greater-than sign, not a >= sign. If the --cautious option has been selected, but we don't yet have a three-judge panel, it is possible that we'll get exactly 0.5 scores, produced by averaging one run that has ground truth before model answer, and one that has model answer before ground truth. That will count as a failure.

If there are multiple LLM judges, aggregate their answers by considering each judge's score for the question and each judge's r_q (for question fit or context fit, depending on what's at issue). Construct a weighted average for the question by weighting the different scores using the standard weighting formula, max(2r_q − 1, 0)².

An exception: if no judge has an r_q greater than 0.65 on this aspect of the question, we really don't have much evidence to make a decision. In that case count the question as correctly answered (for "question fit" or "context fit," whichever aspect is being considered). But keep track of the question numbers where we have to punt like this. If a question passes all the automated judges but there was a "punt" on one or more aspect(s) of the question, we will need to pass it to a human judge.

In evaluating the discriminative (style) score, we similarly require the continuous score reported by the judge to be > 0.5 for a pass. But again, we will not fail the answer unless the judge's r_q for the question is > 0.65. Otherwise, we "punt" the answer and count it provisionally as a pass, no matter how low the score is.

To summarize: for each question, we evaluate the aspects of question fit, context fit, and style fit. In each case, the question must have a score > 0.5 to pass. But it passes automatically if no judge involved has a reliability > 0.65 on this aspect.

A question only passes if it gets a pass on all three aspects.

We will calculate overall binary accuracy simply by counting the number of questions that passed and dividing by the number of questions. Print that provisionally.

However, there may be an additional human step needed after automated scoring, so the calculation script should write all the details to a summary result file: including the model, the benchmark file used, the reasoning level if any, and then for each question the score on each aspect of of the question, the r_qs of the judges involved in that aspect, and the final verdict (pass or fail).

A final human_scoring script should go through this file looking for questions that have passed, but passed by "punting" — that is, without any judge of greater than .65 accuracy. For each of those questions, print the metadata frame, question, ground truth answer, and model answer, and request human evaluation.

Once these punts are resolved the human decisions and final accuracy score can be added to the summary result. 



