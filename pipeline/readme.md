Production pipeline for data cleaning
=====================================

This folder will contain all the code and pre-trained models for cleaning English-language books and serials, 1800-1930. The models can likely be used on post-1930 books as well, though it would be prudent to add some data from that period and retrain them.

The code isn't fully running yet, but when it is, usage will be

```python3 ProcessBooks.py --input_type paths --input pathlist.txt --batch_mb 250 --header_model ./headermodel --output_folder ./your_output_folder```

ProcessBooks can also, alternatively, accept a .jsonl file with texts in the format used by IDI. In that case ```input_type``` would be '.jsonl' and the ```input``` would be the name of the .jsonl file.

Files will be written to your_output_folder with front and back matter removed, headers and footnotes removed, OCR corrected, and lines rejoined so that each paragraph is a separate line.

![Flowchart of the process](DataCleaningPipelineJun25.jpg)