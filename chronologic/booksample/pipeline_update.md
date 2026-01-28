# English-Language Pipeline Update

The main readme file in this directory provides an overview of pipeline strategy and corpus development. This file is aimed specifically at changes in Dec-Jan 25/26, for people who have some previous exposure to the pipeline.

## main strategy shift

The key general change is that I adjusted strategy so that it doesn't lean as heavily on an initial LLM pass (or multiple LLM passes!) over the entire corpus to extract appropriate passages. We were having trouble getting good accuracy with small models. In theory that wasn't a terrible problem, because we anticipated a manual approval step to filter the final questions. But in practice, as I started forming questions, I realized that it was often important to have *collections of parallel entities/sentences* from the text that could be used automatically as distractors. If initial accuracy was low, these, too, would be unreliable.

Also, more fundamentally, there was just no important reason *not* to use a simpler strategy for the initial filter. The risk of a simple strategy is, for instance, that we might miss some subtle edge cases exemplifying a specific rhetorical category. But the goal of categorization in this benchmark is usually not that we're interested in the category itself. It's rather that we need some categories -- any categories -- to provide a structure other than simple fill-in-the-blank.

For instance, the ```connectors/``` module identifies "sentences describing an effect or inference" using these rules:

**as first word:** so, hence
**in first five words:** thus, therefore, thence, accordingly, consequence, result, effect, consequently, it follows that

In using those rules we will get some false positives. Those can be filtered manually; in some cases there's also an initial LLM pass to filter ambiguous words like "so" or "since" or "while" (which have a temporal as well as a causal sense). False positives are important to exclude.

We will also get some false negatives: we will miss some cases where a cause-effect or premise-inference relation between two sentences is implicit and unstated. But the false negatives don't particularly matter. We're not writing a paper on causal rhetoric in 19th-century English prose, where it's vital to catch subtle edge cases. In framing a benchmark, we simply need a category of sentences where logical relations are clear so we can tell a model "the missing sentence describes an effect or inference" and give it a chance to go beyond simple cloze by taking advantage of multiple kinds of evidence. We want to challenge the model, not mainly by giving it especially subtle edge cases of causation, but by giving it some sentences where the right answer requires *an ability to produce 19c/20c prose in response to specifications that may be expressed in 21c terms.* That's the mission.

So this version of the English pipeline often relies on simple NLP strategies (SpaCy or the like) to identify entities, clauses, or sentences in a period text that could function as a ground truth answer. It may then use language models to do some filtering or summary, or to write the final question.

An exception to the rule here is the ```character/``` module which does use small language models to make two initial passes over a book (one extracting character descriptions, another character dialogue), before pairing descriptions with dialogue to form questions about characters.

The language models I have used most heavily are mistral-small:24b, and gpt-oss:20b. To be blunt, I used them because they run on my Macbook Pro with 64GB, and that made things easier. The Mistral is more reliable. GPT-OSS is a thinking model, and it often thinks too long, causing answer overflow. It's also quite flowery when asked to imitate the past, which is sort of fun and produces some colorful distractors. The ```connectors\``` module generates anachronistic distractors using both models for variety.

You might prefer other models! For the Chinese-language benchmark it will of course be important to use models that are good in Chinese, and ideally able to understand a range of scripts and linguistic registers.

## things not yet solved

It's important not to give our test-taking models simple clues that they can take advantage of to discern the right answer. Right now, this remains a bit of a challenge for our "anachronistic distractors" (wrong answers produced by contemporary language models).

Two specific challenges are

1. Ensuring that the average length of anachronistic distractors is comparable to ground truth.
2. In ```connectors/``` we need to ensure that anachronistic distractors are as likely as ground truth to contain the logical connectors that serve as trigger words.

There's also a general puzzling question about *how much information* to give the models when they produce distractors. For instance, do we provide the metadata_frame for the question, so the model can try to match date, genre, etc? Right now I have solved this in ```connectors/``` by producing one anachronistic distractor where the model did see the metadata, and one where it didn't. (They are labeled.) In the Chinese-language benchmark, it might be quite important whether we explicitly tell the model to produce a literary or vernacular response (matching the register of the source), or allow it to be wrong. I don't know which approach is preferable.

3. An edit I need to make to the pipeline code: I think it's a good idea to store, with each question, the *number of words* in the question text drawn from our period source, and the *number of words* created by a contemporary model or human. This may be useful analytically as we strive to understand the performance of models that have more or less exposure to different periods. Right now we know which distractors are period or anachronistic. But we don't have that information about question text.

## categories of questions, with examples

We have right now ~240 questions, mostly in ```character/```, ```connectors/```, and ```knowledge```. The knowledge questions at present all come from one encyclopedia in 1897. We'll broaden that out so we have another group from the 1870s and another group from 1918. But knowledge questions will always be a little clumpy across the date axis. We may eventually have 250 or so of these.

We have almost 100 character questions. That's probably about as many as we need for ten fiction volumes. 

I expect to produce two or three hundred more questions in ```manual/```, distributed across textbook, attribution, and a range of other handcrafted types. 

The number of questions in ```connectors/``` could grow much larger, because it's a flexible and widely applicable process. It would be relatively easy to get ~800 questions here. I also think there is a good rationale for having a lot of questions in this category. They are semi-cloze questions, and the way I understand model assessment right now is that cloze is the foundation on which we must build. We want to go beyond it! But capacity to do cloze has to be there: it implicitly captures a wide range of knowledges and skills that we could never aspire to enumerate explicitly.

Our treatment of categories will be flexible: we can macro-average them as units as well as micro-averaging across individual questions. So the number of questions in a category does not necessarily determine its weight in evaluation.

### knowledge questions

**Source HTID:** hvd.hn5bs8

**Source Title:** Columbian Cyclopedia, vol 23

**Question Category:** knowledge

**Context:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year did the New York Magazine begin publication?

**Answers:**

| Type | Answer | Prob |
|:-----|:-------|-----:|
| ground_truth | 1790 | 1.0 |
| manual_anachronistic_distractor | 1968 | 0.0 |
| manual_distractor | 1848 | 0.0 |
| manual_distractor | 1850 | 0.0 |

### character questions