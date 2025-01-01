lab notebook
============

Experiments that measure the degree of anachronistic distortion in particular models.

Dec 27
------

Begin fine-tuning experiment.

job = client.fine_tuning.jobs.create(
    training_file='file-CctgNe1d3Z1EZkjdP1X2wD',
    validation_file='file-1RjppXQZmtxuZh2qKWhusf',
    model="gpt-4o-mini-2024-07-18"
)

training file: FileObject(id='file-CctgNe1d3Z1EZkjdP1X2wD', bytes=3393596, created_at=1735321402, filename='train_messages.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)

validation file: FileObject(id='file-1RjppXQZmtxuZh2qKWhusf', bytes=665282, created_at=1735323015, filename='test_messages.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)

Ran fine-tuning job 'ftjob-TJJbDAquB21Z7tyAClj3fAcu'

Completed with this result:

FineTuningJob(id='ftjob-TJJbDAquB21Z7tyAClj3fAcu', created_at=1735323648, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:tedunderwood::Aj9zpMdD', finished_at=1735326547, hyperparameters=Hyperparameters(batch_size=3, learning_rate_multiplier=1.8, n_epochs=3), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-aw09ch9csbZw51lKeR83xQAq', result_files=['file-5LcjWzc4ugQCny85es9HZ4'], seed=198387980, status='succeeded', trained_tokens=2303796, training_file='file-CctgNe1d3Z1EZkjdP1X2wD', validation_file='file-1RjppXQZmtxuZh2qKWhusf', estimated_finish=None, integrations=[], method=Method(dpo=None, supervised=MethodSupervised(hyperparameters=MethodSupervisedHyperparameters(batch_size=3, learning_rate_multiplier=1.8, n_epochs=3)), type='supervised'), user_provided_suffix=None)

Ran GenerateGPT4oCompletions.ipynb on this, producing finetuned_4omini_continuations.tsv, and a subset of columns for use in prediction: finetuned_4omini_dataforegression.tsv

ran python RobertaRegressionPredictor.py -m regressionmodels/best_model.pt -d finetuned_4omini_dataforegression.tsv -o finetuned_4omini_publicationyears.tsv

Wed Jan 1
---------

Fine tuning a first qualitative test on 4o-mini

train1.jsonl file = TpjYXYbsniNDm9dMGPiPvt
validate1.jsonl = JezVyLexZk5LLr2x9pphK4

fine-tuning job, fold1: 
job = client.fine_tuning.jobs.create(
    training_file='file-TpjYXYbsniNDm9dMGPiPvt',
    validation_file='file-JezVyLexZk5LLr2x9pphK4',
    suffix = 'fold1',
    model="gpt-4o-mini-2024-07-18"
)

FineTuningJob(id='ftjob-ImcHr48LtgWVvQB10tDkg7sC', created_at=1735767593, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(batch_size='auto', learning_rate_multiplier='auto', n_epochs='auto'), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-aw09ch9csbZw51lKeR83xQAq', result_files=[], seed=109134267, status='validating_files', trained_tokens=None, training_file='file-TpjYXYbsniNDm9dMGPiPvt', validation_file='file-JezVyLexZk5LLr2x9pphK4', estimated_finish=None, integrations=[], method=Method(dpo=None, supervised=MethodSupervised(hyperparameters=MethodSupervisedHyperparameters(batch_size='auto', learning_rate_multiplier='auto', n_epochs='auto')), type='supervised'), user_provided_suffix='fold1')