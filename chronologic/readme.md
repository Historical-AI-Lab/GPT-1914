Chronologic-EN-1.0
=====================

Ted Underwood, Ziliang Qiu, Sarah Griebel, Laura K. Nelson, Teddy Roland, Wenyi Shang, Matthew Wilkens

Chronologic-EN-1.0 is a benchmark that measures language models' ability to respond like English-language writers located in specified social and historical contexts between 1831 and 1930.

For the paper, see URL.

The benchmark was based on 176 sources listed in booksample/primary_metadata.csv. A sample of questions is also available in booksample/chronologic_en_1.0_sample.jsonl.

To reduce the risk of benchmark contamination, we publicly release a representative sample rather than the complete answer set. The complete benchmark is available under controlled access through [repository], subject to an agreement not to redistribute the data or use it for model training.

Running the benchmark
---------------------

The benchmark was developed under Python 3.10, in an environment with [list of packages].

Once you have retrieved the whole benchmark file from HuggingFace, you can run a model against it in one of two ways.

### Likelihood scoring

Calculates Brier scores as well as skill scores and top-1 accuracy.

Artifacts you will need before running:

[list of artifacts foes here]

Sample command-line instruction:

[sample CLI goes here]

### Free generation

Administers questions, with loose length cues, to elicit free text responses. Then passes those responses through both substantive evaluation (using LLM judges) and stylistic evaluation (using fine-tuned DeBERTa models.)

Artifacts you will need before running:

[list of artifacts goes here]

Sample command-line instruction:

[sample CLI]

Documentation for the benchmark
-------------------------------

**Booksample** contains metadata for the sources used in constructing the benchmark, as well as scripts used to develop questions.

**Bertclassify** contains DeBERTa models used for judging style.

**Evalcode** contains

**Modelasjudge** contains scripts for judging free generation, as well as results from models evaluated through free generation.

**Stylejudge**