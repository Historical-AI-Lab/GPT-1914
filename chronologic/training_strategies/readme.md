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
