# Codebook

Anachronism labeling notes and guide. Begun by Matt on 1/11/25.

## Guidelines

**[Updated 1/27/25]** There are two criteria that a model generation must satisfy to be judged `ok`/`plausibly 1914`.

1. It must avoid *factual anachronism*. This includes refusing to answer things that *were* known in 1914. Be generous; if something was known/posited/theorized, but maybe not widely, and the model mentions it, that's OK. Anachronism can include aspects of vocabulary ("African American" is an anachronism, for example). 
1. Its attitude/outlook/vibes must be plausibly 1914. The bar here is intended to be low. But treatments of cultural difference, for instance, cannot be *too* open-minded in ways that would not have flown in period.

Some agreed guidelines:

* DO NOT ding the models for "Here in 1914 we believe/know that ...." We just note that this is a general issue, but are not scoring it.
* The text in the "Assistant" field is not law. It's a strong guide, but the model outputs *may* diverge in style and/or details, up to the point of plausibility.
* In general, we do not penalize a model (just) for being wrong, provided it's wrong in a way that is period-appropriate. For example, minor mistakes in birth and death dates for historical figures are usually OK. Even mistaking the identity of a person entirely may be OK, provided the error is not an anachronism.
* Westernizations of non-Roman scripts can be anachronistic. Pay attention to these; Pinyin wasn't developed until the 1950s, for example.
* Don't trust the "trap" field as a criterion; I created those predictions quickly; they don't represent a consistent boundary, aren't based on much research, and are superseded by our codebook.

## General

Quoth Ted:

> The calibration datasets contain 20 rows that we all have in common. We can do these first and then compare notes.

> The test datasets contain 40 rows for each of us, adding up to 60 total, with each row appearing in two and exactly two raters' lists. I excluded a few rows that we had already discussed together earlier this week.

> In each file, you'll see the model outputs identified only as `column_0`, `column_1`, and `column_2`. I've saved a mapping file that maps these to the original model names — the mapping is different for each row (but each row's ordering is the same for all raters).

> There are three response columns, with names like `plausible_ln_0`. That's whether Laura thought `column_0` was plausibly in-period, according to the criteria above.

> There's also a `comments` column.

Label values are `true` or `false`. No other values are used. 

`true` means the generated response is OK, i.e., that it is *plausibly 1914*. 

`false` means that the response is not OK, i.e., that it contains one or more anachronisms. 

## Specific notes
