# Qwen/Qwen2.5-7B-Instruct

## Question 1

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** The students' laboratories are in the wings at this end; one. toward the front, is for students of the second year, and is 29.6 metres long by 10 metres wide, with high arched windows, 1.7 metres wide,
on three sides of the room. On one of the long sides of this room is a projection which was intended for a fume room, [masked clause describing a tension or contrast].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but the fume closets were found sufficient | ground_truth | 1.000 | 0.023 |
| however, fourteen double desks; each student being allowed double the space that is permitted in the first-described laboratory | same_book | 0.000 | 0.043 |
| but for the practical examination of candidates for degree of federal assayer, prepared in other institutions and, if necessary, for the instruction in this branch | same_book | 0.000 | 0.030 |
| however, it remains unused due to budget constraints | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.645 |
| in stark contrast to the airy space | anachronistic_gpt-oss:20b | 0.000 | 0.258 |

**Brier Score:** 0.2881

## Question 2

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Judge Story, a strong advocate of the supremacy of the treaty-making power, in Section 1508 of his work, uses this language, speaking of the treaty-making power, - "But though the power is thus general and unrestricted, it is not to be so construed as to destroy the fundamental laws of the State. A power given by the Constitution cannot be construed to authorize a destruction of other powers given in the same instrument. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It must be construed, therefore, in subordination to it; and cannot supercede or interfere with any other of its fundamental provisions. | ground_truth | 1.000 | 0.132 |
| It must be construed, therefore, as independent from it; and can supplement or align with any other of its fundamental provisions. | negation | 0.000 | 0.022 |
| The question, therefore, is whether the people of the United States wish to change the manner in which they exercise their own powers, whether they wish to do less through local governments and more through the general government, and this change can lawfully be made only by the people through an amendment to the Constitution. | same_book | 0.000 | 0.142 |
| This implies that while the treaty-making power is expansive, it must coexist harmoniously with other constitutional provisions. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.428 |
| Therefore, the treaty power must be exercised in a manner that preserves the constitutional rights of the states. | anachronistic_gpt-oss:20b | 0.000 | 0.276 |

**Brier Score:** 0.2067

## Question 3

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But the necessity for a guilty mind or criminal intent does not mean that it is necessary that the person doing the prohibited act be conscious that it is wrong, for, as we have said before, ignorance of the law excuses no one. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Thus when the selling of adulterated milk is made a crime, ignorance that the milk sold is below the standard fixed by law is no defense. | ground_truth | 1.000 | 0.104 |
| Thus when the selling of pure milk is made a crime, knowledge that the milk sold is above the standard fixed by law is no defense. | negation | 0.000 | 0.036 |
| Hence it is said that every crime, at least at common law, consists of two elements-the criminal act or omission, and the mental element commonly called the criminal intent. | same_book | 0.000 | 0.162 |
| Therefore, to make an arrest lawful, it is necessary that the person arrested should have notice that he is arrested by lawful authority. | same_book | 0.000 | 0.036 |
| This implies that even if someone is unaware of the moral implications of their actions, they can still be held liable for their deeds. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.336 |
| Therefore, a person may be held liable for a prohibited act even if he did not consciously recognize it as unlawful. | anachronistic_gpt-oss:20b | 0.000 | 0.325 |

**Brier Score:** 0.1749

## Question 4

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Whether it be due to the intoxication caused by our incalculable natural resources or to the fact that our population, upon whom ultimately rests the responsibility of government, is made EDUCATIONAL up largely of the millions who have been EXPERIMENTS pushed out of older countries and have not yet had time in this country to develop respect for authority or to set up sane standards, it remains true that we have been indulging in educational experiments with a recklessness and on a scale that have never before been attempted by any civilized nation. [masked sentence describing a cause or reason] Our population is heterogeneous to the last extreme, our cities are the meeting-ground of the nations of the earth.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| However, if not in justification, at least in palliation of this procedure, it should be borne in mind that our situation in this country is characterized by many special difficulties. | ground_truth | 1.000 | 0.188 |
| However, if not in condemnation, at least in mitigation of this procedure, it should be overlooked that our situation in this country lacks many special advantages. | negation | 0.000 | 0.040 |
| There is no one cause for retardation nor can we say that any one cause is preponderant. | same_book | 0.000 | 0.121 |
| Does it not savor much like the boasting we hear every time we have a Catholic elected to public office, as if the Church sought such, or could be benefited
thereby. | same_book | 0.000 | 0.030 |
| This lack of homogeneity and stability has made it difficult to establish a consistent educational framework. | anachronistic_mistral-small:24b | 0.000 | 0.622 |

**Brier Score:** 0.2128

## Question 5

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was ready to pour out money in any case of distress, but she had no idea of its value, and none of her charities prospered, except so far as her rosy, good-natured face could be seen, for that, to be sure, did good like a medicine. And she was not a stupid girl, [masked clause acknowledging a countervailing fact]. If she had been taught that arithmetic is positively needed by every girl, rich or poor, she could have learned all she needed to know of figures to make her life a blessing to hundreds of people whom she only injured for lack of such knowledge.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though certainly not brilliant in mathematics | ground_truth | 1.000 | 0.059 |
| though hardly dull-witted in mathematics | negation | 0.000 | 0.004 |
| though it was always a sorrow to her that she had had too little instruction to produce anything of value to others | same_book | 0.000 | 0.197 |
| though she was often ashamed of her cowardice | manual_same_book | 0.000 | 0.124 |
| though she had been endowed with good common sense | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.265 |
| though she lacked mathematical training, she was otherwise earnest in her benevolence | anachronistic_gpt-oss:20b | 0.000 | 0.351 |

**Brier Score:** 0.1889
