model-as-judge workflow overview
==============================

This is a complete overview of the plan for model-as-judge scoring of the ChronoLogic benchmark. Other plans will be written to cover specific parts of the code.

## The big picture: scoring a single model

We allow a model to produce free-generated responses to the ChronoLogic benchmark questions.

Then responses pass through this filter:

1. Is the model response to question Q (Q_m) precisely equal to the ground truth answer (Q_gt)? If so, score it correct. If not, it passes through two judging processes.
2. An LLM judges the response's substantive accuracy for the question and metadata frame. We will use Claude 4.6 for all models that aren't in the Claude family. For Claudes we'll use a GPT. Average reliability on these topics is high enough ( > .9) that a panel approach is probably not needed.
3. A discriminative model judges its stylistic fit to the period.
4. If the question has "frame_type" as "book_context," it also needs a specific judgment about fit to that context. This will be made by a human judge.
4. Each of those processes produces a score for each question. So each question gets a score for question accuracy and style authenticity; some also get a score for context fit. This score is usually 0 or 1, but special circumstances (multiple ground truths) can make it fractional.
5. We have also measured the per-question reliability of the judges, and we use the reliability scores in two ways. First, we replace some scores with NA, if the reliability is =< .7 for a particular aspect of judgement (question or style, for instance). Questions with "world_context" or "passage_context" also get an NA for context.
6. In the case of the question accuracy dimensions, if we have an NA, we get a human judge to score that dimension of the question. In the case of style, we just ignore the NAs, because those questions typically have brief noun-phrase answers where "style" is not a very meaningful measurement. Similarly we ignore NAs for context.
7. So now we have vectors for all three aspects of judgment, where each answer is associated with a judge and a reliability score — either the per-question reliability score of an LLM judge, or a human reliability score calculated by comparing human annotators. For style and context, we also have some NAs.
8. We produce weighted scores for accuracy, context fit, and stylistic authenticity, weighting each question by judge reliability. We ignore NAs.
9. We also produce an overall binary benchmark score, using the rule that a question must pass all three aspects (or get an NA) in order to pass.
10. Finally, we calculate confidence means for all four scores (specific aspect scores and overall benchmark score) using a hierarchical Bayesian model.

## The free generation part of the code

This largely already exists, in free_generation.py, which is a copy of evalcode/benchmark_free_generation.py. However, it may need to be adapted. The model-querying scripts in bertclassify/ are able to query models through Open Router, and we should make sure that free_generation.py has a comparable ability.

Note also that knowledge and abstention questions, iirc, get a slightly different prompt than other questions, stressing that questions unanswerable in the specified context should be answered "insufficient information."

We should confirm this and document the two different prompts, perhaps in a free-standing markdown document in this folder that describes the free generation process.

## The scoring process for the LLM panel, before weighting

LLM judging will be done by a single model, because frontier models are pretty good at discriminating the best answer for accuracy ~ 0.92.

Here's the prompting structure:

SHARED PROMPT = 
"""You will be asked to choose between two answers to a question.

Context: {context}
Question: {question}

Answer A: {Q_a}

Answer B: {Q_b}

Which answer better fits the question? {added_qualification}
- Choose A or B if one answer is more accurate.
- Choose C if the two answers are equally accurate and relevant to the question.

{abstention clause}

Respond in JSON: {"question fit": "A"|"B"|"C", "context fit": "A"|"B"|"C"}

Your response:"""

_ABSTENTION_CLAUSE = (
    "If the question could not be answered in the specified historical context "
    "or makes no sense there, 'insufficient information' is a valid response. "
    "It is also acceptable to explain why the question could not be answered.\n\n"
)

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

The code for scoring should check that the reply is in the correct JSON format. We should record whether Q_m won, lost, or tied. But the numeric scoring rule for the question is that Q_m will pass (get a value of 1) whenever it is scored *either* better than or equal to (a tie) Q_gt. Otherwise, if it's rated worse, it gets 0.

### Multiple ground truth

If there is only a single ground truth answer for each question, we can just pose the question once. But there are often two or more ground truth options.

In this case the model answer should be tested against both ground truth answers, and both responses should be preserved. It matters that we got two answers, because it increases the evidence for this question: [1, 1] should not just average out to 1. On the other hand, if there are just two ground truth options, they could produce a split verdict, averaging to 0.5 which would create ambiguity later. So if there are an even number of ground truth options, one of them should be chosen at random to be asked twice, with both possible order sequences, to ensure a tie breaker.

In other words, if you just have G1, just ask about G1, and randomly place it before or after the model answer to be evaluated.

However, if you have G1 and G2, one of them should be used once (with random ordering), and the other should be used twice (with both possible orderings).

Note that this functionality was not included when the script was first written. And to implement it we may have to change the way output files are structured. We need to be able to save multiple answers for both question fit and context fit, indicating whether the judge selected GT, model answer, or tie in each case, and also recording a numeric score as 1 or 0 in each case. 

## The scoring process for the discriminative model, before weighting

We have already trained a DeBERTa model to distinguish real period text from LLM-generated infill or continuation of period text, with ~0.89 accuracy. We may later expand the training set slightly to include some contemporary text, but this is good enough for now.

We're going to use this model to create log-odds values for the model answer (Q_m) and ground truth answer (Q_gt), and then compare those two log-odds to produce both a) a continuous score in [0, 1] and b) a binary {0, 1} pass/fail score.

In order to score, we will first need to calculate log-odds for ground_truth / anachronistic distractor pairs in our benchmark, and subtract them to get a range of Δ_anachronic. (Note that same_book and same_character distractors, and other non-anachronistic distractor types should not be used here. Only distractor types that contain 'anachronistic' or that are simply 'manual,' full stop.)

We'll also select same-source pairs from our period source texts, matching the length distribution and length ratio of our benchmark pairs. We'll calculate log-odds and get a range of Δ_gt between authentic texts.

We train a logistic model with a quadratic term

logit[P(anachronic∣Δ)] = β0 ​+ β1|Δ| + β2​Δ²

Then at deployment time we measure the difference between logodds of Q_gt and Q_m to get Δ_m, and apply |max(0, Δ_m)| so candidates that beat GT count as zero gap, before using our logistic model to predict P(anachronic∣Δ_m), which is our continuous score.

For binary {0, 1} scoring we will eventually binarize the probability using a 0.5 threshold, but that's not necessary in discriminative_scoring.py -- the real-valued score(s) should be preserved. (Scores is plural because we test the answer candidate against each ground truth.)

## Assessing the per-question reliability of judges

None of our judges are perfect, and just as importantly, some question categories don't provide much evidence for a particular kind of score. E.g., for knowledge questions answered with a proper name or brief phrase, style has little relevance. So the continuous scores for question fit and stylistic appropriateness will be *weighted* to reflect judge reliability.

Before a judge can score any candidate model, we need to first calculate the judge's reliability score for each question.

### question-judge reliability

In the case of an LLM judge, we calculate reliability per-question, because it's hard to generalize. 

There are two types of error probability that concern us:

1. The probability that that a judge will accept a distractor in head-to-head comparisons with ground truth. We might call this the type I error rate, or alpha.

2. The probability that a judge will wrongly reject an answer that is as valid as the ground truth. Call this type II error, or beta.

#### alpha
We calculate alpha by using the prompt outlines above to get scores for all the ground_truth - distractor pairs in the benchmark. Since position can matter, we test with both positions. So, e.g., a question with one ground truth and four distractors would have eight comparisons. Note that a question with two ground truths and three distractors would have twelve comparisons! We test each ground truth against all of the distractors.

We produce per-question reliability estimates for question fit, q_r.

Scoring of ties depends on the distractor type being compared to ground truth in this instance. A distractor that is anachronistic or drawn from a different author may well be a good fit for the question. So when we use these distractors to assess "question fit," we only penalize the model if it says the distractor is actually better.

We infer the penalties appropriate for each distractor by consulting distractor_penalties.txt, where the possible situations for a tie to be penalized are 'both', 'context', or 'question.'

Questions will ultimately be weighted by max(2r_q − 1, 0)², the inverse-variance weight under a noise-channel model, and we might as well also calculate that and report it for both question and context in each case.

#### beta

Here, instead of pairing a ground truth from the benchmark file with a distractor, we pair two ground truth answers. As before, we will pose the question with answer sequences A-then-B as well as B-then-A to allow for the possibility of variation based on order effects. If the judge model prefers *either* of the answers, and fails to recognize a tie, we count that as a failure.

We need to record the raw number of tests and the number of failures overall. But we should also stratify questions into two bins based on the length of the *original* ground truth answer. Find a length (in characters) that creates two bins of close to equal sizes, and record the number of tests and number of failures for each bin.

The failure rate is 2 * beta, because it includes both failures that prefer A and failures that prefer B. In our eventual correction script we will be concerned with one-sided failure and will use primarily beta itself, the failure rate / 2. Record this for each length bin.

### discriminative, stylistic-judge reliability

Per-question reliability is going to be noisy. We can accept that for the LLM case because reliability is generally pretty high and we're going to ultimately have a panel of three judges, so the absolute value of noise is low and will be tempered.

For the discriminative judge, there are large categories of questions where the judge is pretty useless, since the question is factual and/or answers are short. So it makes sense to stratify reliability. We group questions in two ways: by reasoning_type and by the decile of the mean answer-length. Then we apply the logistic model described above to all the ground-truth/anachronistic distractor pairs for questions in that group, and count the judgment as correct only if P(anachronic) is > 0.5.

Calculate group-level reliability for each of the reasoning_type strata and length deciles, and set r_q for each question as min(reasoning_type, length). 

### The output of the judge_scoring script

The judge_scoring script should end by writing results to a file: including 

1. Metadata like the model being tested, the reasoning level if any, and the benchmark file used.

2. Then a keys for question accuracy, pointing to a list of questions. For each question, the result file should report
a. The judge (model name or "human"),
b. the judge reliability r_q, 
c. a list of actual judgments (GT, model, or tie), 
d. a list of numeric scores (usually 1 or 0), and
e. the GT being tested in each case, e.g. 0 or 1 if there are two ground truth answers. This will be needed for bootstrap uncertainty estimation, because separate GTs provide more evidence than retesting the same one with a different ordering.

The next step will be to pass this to a human_scoring.py script.

## Thresholding scores and consulting the human judge

If the LLM judge accuracy is lower than .7 for question accuracy or context fit, the odds of error are too high, and we must consult a human judge.

Also, human judges must be consulted for all ~216 questions defined with "frame_type" as "book_context," in order to get a context score (1 or 0).

The judge_scoring.py script should keep track of questions where this is necessary, and put the list in the output file created by judge_scoring.py.

Before final scores can be calculated, this file will need to go to human_scoring.py, which will query a human for judgment on all the questions in the list. It first asks the human for a human_reliability value to be used as r_q for these scores. Then, for each question that needs human input, it prints metadata_frame, the question itself, the ground truth answer, before enumerating the aspects that need input. For each aspect the human is asked to judge, the script prints up to 5 recent precedents/reasons for this question & aspect, before asking the human judge for a score and reason.

Note that the judge_scoring output file records GT wins, model wins, and ties as well as numeric 0s and 1s. But the human judge only needs to provide a 0 or 1 (model answer fails or passes). If it passes, that can always be considered a tie. Unlike the other judges, the human judge knows which answer is ground truth, and it would be meaningless for model answer to beat ground truth.

One important feature of the human_scoring script is that, whenever a question is scored, it writes the question number, model being tested, model's answer, aspect being evaluated, human judgment on the answer, and reason for the judgment to a cumulative file (separate from the scoring files for this model) that keeps track of all human judgments across models. When previous answers are available for a question, human_scoring.py shares the 5 most recent answers, [judgments, and reasons] with the human judge so they can be guided by previous precedent. (Note that I'm not sure it's currently sharing answers, judgments, *and* reasons: this may need to be added.)

The human_scoring output file resembles the judge output file that was submitted to it. But this script adds "_human" to the filename and edits the lists of judges, scores, and judge_reliabilities for question_accuracy and context_fit by replacing the LLM judge's name, score, and reliability with "human," the human score (0 or 1), and the provided human_reliability value wherever a human score was necessary.

Note that none of this is necessary for the style scores. Any questions where the discriminative (style) judge is less reliable than 0.7 get NA or None as their score and are not counted toward the stylistic authenticity average score. They don't represent significant evidence about style.

Once there's an output file from a discriminative judge, and the output file from judge_scoring has passed through human_scoring, both of those files can be submitted to the final score_calculation script.

## Calculating the weighted scores for each of the three aspects

For each aspect, do a weighted average of all scores that aren't NA. The weight of each score is determined by the reliability r_q of its judge (which will be human reliability if a question had to be judged by a human), using the formula max(2r_q − 1, 0)².

## Calculating overall binary accuracy

In the overall binary scheme, a question is counted as correctly answered only if it gets >= 0.5 for all three categories — question fit, context fit, and style fit.

For the style and context scores, NA counts as a pass.

We will calculate overall binary accuracy simply by counting the number of questions that passed and dividing by the number of questions. Print that provisionally.

### Bayesian uncertainty model

The last step of analysis uses a hierarchival Bayesian model to correct both per-aspect and overall scores for judge reliability.



