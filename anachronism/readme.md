anachronism
===========

Experiments to measure the anachronistic deviation of LLM responses when they are asked to reproduce the style and content of earlier eras. We also inquire how far this can be addressed by RAG or fine-tuning, and how far fixing it requires pretraining on a period corpus.

### training of GPT-1914

The list of HTids held out from GPT-1914 is in HeldOutListNoDupes.txt. The tsv files HeldOutRecords1905-14_nodupes.tsv and HeldOutRecords1905-14.tsv contain fuller metadata for this list; the second file contains multiple volumes in cases where a title occurred in multiple copies.

The code used to train GPT-1914 was drawn from [Andrej Karpathy's llm.c](https://github.com/karpathy/llm.c).

### date prediction

To assess the stylistic distribution of model generation, RoBERTa was fine-tuned on a subset of COHA. FineTuneRoBERTaForYear.py was used to tune the model, and RobertaRegressionPredictor.py was used for inference. The regression model itself is 1.5GB, a little large for this repo, [but available at this link.](https://www.dropbox.com/scl/fi/e25oyo5gsai93bumh45lp/best_model.pt?rlkey=k9ygvu5w3hglxnrtc9zq7nc5x&dl=0)

### data visualization

Visualization of kernel density distributions over the timeline are produced by ```VisualizePublicationYears.ipynb.```

### human evaluation

Measurements of inter-annotator agreement are contained in the /qualitative subdirectory.

