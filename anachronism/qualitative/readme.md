qualitative
===========

Data and code used to test contemporary models' susceptibility to anachronism when they are instructed to simulate 1914.

questions.json has questions and ground-truth answers

questions.txt may be more human-readable and easier to edit

If you want to add a new question file, you could either create it in the ad-hoc .txt format I was using or create a .json file; either is fine. I have a utility to convert. I found the .txt format easier to write in because it required fewer {} [] , characters I could get wrong.

If you're actually adding directly to existing files, best to add to the json because my old questions.txt is no longer up to date.

lab_notebook.md contains records of fine-tuning jobs, etc

## Human labels

* `anachronism-codebook.md` has notes on labeling model outputs as "plausibly 1914"
* Matt's labels are in `questions_with_answers.xlsm`. Ted's (for a slightly different set of conditions) are in `4oBigUntunedJudged.json`
* `interannotator.ipynb` has quick code to process the labels and calculate interannotator agreement.
