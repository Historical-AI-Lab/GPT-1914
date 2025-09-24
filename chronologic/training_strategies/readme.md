training strategies
===================

The script ```make_training_data_causality.py``` accepts a text file and processes it

1. into a json list of chunks, each chunk ending at sentence boundaries, and each less than 768 tokens long
2. into a json list of chunks annotated by a language model, with fields for 'passage', 'causal_yn', 'cause', and 'effect'.

The first of these will be written to the folder where it's located as {sourcefile}-chunks.json. The second will be written as {sourcefile}-causal-analysis.json.

USAGE:

You need a python environment with these modules:

    pip install nltk tiktoken requests

You also need to download ollama and run these commands:


    ollama pull qwen2.5:7b-instruct
    ollama serve

Then operate the script with a command like

    python make_training_data_causality.py full /Users/tunder/workdata/hathifiles/selected_gutenberg/26306.txt 

The option "full" tells it to both chunk and invoke the model. The second command-line argument is the path to a Gutenberg text.

scoring system
--------------

To test a model, I would edit the make_training_data_motive.py script to use that model and then run it like this

    python make_training_data_motive.py analyze evaldata-chunks.json

This will produce a file called ```evaldata-motive-analysis.json```.

Then you can score that file by running, for instance

    python motive_behavior_scorer.py evaldata-motive-analysis.json evaldata.json

Which should produce output like this:

Loading prediction data...
Loading ground truth data...
Loaded 21 prediction chunks and 21 ground truth chunks

SCORING RESULTS

Y/N Classification:
  Accuracy:  0.762 (16/21 correct)
  Precision: 0.714 (5/7 predicted Y were correct)
  Recall:    0.625 (5/8 actual Y were predicted)

Passage Matching (for predicted Y chunks):
  Match Percentage: 0.643
  Match Score: 9/14 possible points
  (Based on 7 chunks predicted as Y)

Summary:
  Total chunks processed: 21
  Predicted Y: 7
  Actual Y: 8
