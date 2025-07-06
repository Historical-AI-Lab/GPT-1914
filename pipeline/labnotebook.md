lab notebook
============

Thurs, Jul 3, 2025
-----------
Downloading 1890-94 from hathi_pd
Started planning ByT5

optimized header remover
Best trial: 17
Best F1 score: 0.8598

Best hyperparameters:
  batch_size: 6
  learning_rate: 2.3912164944578284e-05
  warmup_steps: 120
  metadata_std: 0.06
  
Second best were:
Trial 31 finished with value: 0.8409264849720771 and parameters:
{'batch_size': 6, 'learning_rate': 2.5501603876806743e-05, 
'warmup_steps': 100, 'metadata_std': 0.04}.

I recommend batch 6, learning rate 2.45e-05, warmup 110, metadata .06

Fri July 4, 2025
----------------
test with the new hyperparameters in order to assess whether we're in hailing distance

We're getting there

KEEP as the positive class:

TP = 129 545

FP = 336+1867 = 2203

FN = 1743

Precision = 129 545 / (129 545 + 2203) ≈ 0.9837

Recall = 129 545 / (129 545 + 1743) ≈ 0.9867

F₁ ≈ 0.9852

DROP as the positive class:

TP = 10 716

FP = 1743

FN = 2203

Precision = 10 716 / (10 716 + 1743) ≈ 0.8601

Recall = 10 716 / (10 716 + 2203) ≈ 0.8292

F₁ ≈ 0.8442

Macro-averaged F₁ = (0.9852 + 0.8442) / 2 ≈ 0.9147

If you still want recall broken out by the two “DROP” sub-classes (just to see how well you’re catching each):

header_footer recall = 1294 / (1294 + 336) ≈ 0.7939

internal_drop recall = 9422 / (9422 + 1867) ≈ 0.8346

But as you noted, there’s no sensible way to define precision for those two separately under a shared “DROP” prediction.

However, talking to Claude it's clear that adding class weights for the loss will improve our F1 on the smaller DROP class, so I'm now engaged in doing that.

As long as I'm doing that, I might as well run doccano to build up the data a little more.

Sun, Jul 6
-----------

I annotated 36 more books and added them to the data, shuffled the data, and used class weights. Not much change on overall maximum F1:

But what the class weights have done is raise F1 for DROP relative to F1 for KEEP.

Best trial: 22
Best F1 score: 0.8590

Best hyperparameters:
  batch_size: 4
  learning_rate: 3.478802872532888e-05
  warmup_steps: 110
  metadata_std: 0.04

Second best: Trial 25 finished with value: 0.8561429673886692 and parameters: {'batch_size': 4, 'learning_rate': 1.8916970677228235e-05, 'warmup_steps': 100, 'metadata_std': 0.08}.

