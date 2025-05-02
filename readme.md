GPT-1914
========

Training small language models on historically specific corpora. The repo will include scripts needed to clean the data, which is a big part of the task.

Data and big metadata files are located in a GPT-1914 Box folder that you need to be invited to. This is mostly code.

Organization at the moment

anachronism
-----------
Contains code to support Ted Underwood, Laura K. Nelson, and Matthew Wilkens, ["Can language models represent the past without anachronism?"](https://arxiv.org/abs/2505.00030)

metadata
--------
Metadata files for the corpus; right now it only has the subset we're using to train macrophage.
For the full corpus metadata, see Box.

datacleaning
------------
**paratext** is code for training models that filter at the volume and page level -- which is mostly getting rid of reference books and pages that are paratext, i.e. tables of contents or indexes or library stamps on the last page.

**macrophage** is code for training a sentence-level model; it looks at sentences, plus two sentences on either side, and decides to cut sentences that are gibberish or bibliographies/catalogs/numeric tables.

**production** is code that applies the two previous categories of models. We're running this on the campus cluster.