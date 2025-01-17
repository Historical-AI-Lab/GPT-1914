# Codebook

Anachronism labeling notes and guide. Begun by Matt on 1/11/25.

## General

Labels are kept in the file `questions_with_answers.xlsm`.

There are three columns for labels, matching the three column headings for generations:

* `4omini-raw-ok`
* `4omini-ft-ok`
* `4obig-ok`

Label values are `true` or `false`. No other values are used, except that there are blanks where I have not yet provided a label. 

`true` means the generated response is OK, i.e., *does not* contain factual anachronism. 

`false` means that the response does contain one or more anachronisms. 

This labeling polarity matches Ted's use in `4oBigUntunedJudged.json`.

I (Matt) am checking only for *factual anachronism*. Noting style issues, where they seem significant, in the `notes` column. This makes sense to me, since we have other ways of judging stylistic proximity.

## Specific notes