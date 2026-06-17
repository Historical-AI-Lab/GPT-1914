Some examples of scoring
========================

Aspects: **question_fit** = "Is the candidate answer acceptable in regard to a) accuracy and b) instruction-following?"

**context_fit** = "Could this source plausibly have said this?" Note that a lot of questions being judged for context fit are constrained-generation, which means there may be a constraint of form, theme, or wording imposed in addition to the context. If the answer fails to meet the constraint, or simply doesn't make sense, we fail it on context. For instance

Human judgments: **tie** = candidate answer acceptable (score 1); **GT** = ground truth is strictly better (score 0).

Note that while judgments are expressed in terms of "is this as good as ground truth," that's an artefact inherited from the way we frame the question for automated judges (who really can be blind to which answer is GT). Really, for human judges, the question is "Is this answer within the acceptable penumbra around ground truth." We have to define, through our discussion, how big that penumbra is. For automated judges, it's defined by the limits of their ability to discern difference, but that relies on their blindness to GT. Humans have to be more explicit about it.

Note also that while distractors are provided below, the distractors are testing lots of different things. Many of the anachronistic answers are acceptable according to the criteria we're exploring here, and fail only on the style aspect, which is evaluated separately.

Question fit: judging accuracy and instruction-following
===================================================

## Q4 — question_fit (inference)

**Metadata frame:**

> The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In which city was the inventor of the pin‑making machine a resident when he obtained his U.S. patent in 1825?

**Ground truth:** Manchester, England

**Distractors:**

| Answer | Type |
|---|---|
| Baltimore | manual |
| Boston | manual |
| Birmingham, England | manual |
| insufficient information | manual |

### ft_DNkT25IC

**Candidate answer:** insufficient information

**Human judgment:** ✗ GT wins (score 0)

## Q104 — question_fit (character_modeling)

**Metadata frame:**

> This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is arrested by the Governor after sharing crucial information about a British squadron. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Ground truth:** Your excellency why should I be placed under arrest? I am trying to serve your interests.

**Distractors:**

| Answer | Type |
|---|---|
| I want to see the consul. | same_character |
| I would rather be cut to pieces with knives or thrown into boiling oil, than be a spy. | same_book |
| I didn't think I was helping you when I shared it. | anachronistic_mistral-small:24b |

### talkie-1930-13b-it

**Candidate answer:** Hoffman says to the Governor, "I am sorry, sir, but I must decline to answer any questions."

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** Including the speech tag is poor instruction-following. Note that this might be fine if being judged for context; in judging context we're not asking for perfect instruction-following, but only "has this followed instructions well enough to count as an answer to the question, thus providing enough evidence to *evaluate* context fit."

### gpt-5.4

**Candidate answer:** “This is an outrage, Governor, but you’ve the power; I only told what any honorable man must.”

**Human judgment:** ✓ tie (score 1)

**Rationale:** Plausible. A little melodramatic, and too on the nose for the situation, as usual, but we're not judging literary quality.

---

## Q173 — question_fit (sentence_cloze)

**Metadata frame:**

> The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was among the most skillful physicians of her native city. She saved many lives, and relieved much suffering. She gave her priceless services to hundreds of poor people, but she did not give to those who could pay for them. I think she was altogether right. [missing sentence describing a cause or reason] Perhaps she blocked the way of less fortunate physicians.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Ground truth:** The world was better because she used her gift, and she was happier, as all are who exercise their powers.

**Distractors:**

| Answer | Type |
|---|---|
| The world was worse because she squandered her gift, and she was unhappier, as all are who neglect their powers. | negation |
| It was because she could give priceless services that she had so clear a right to fix a price which she did not need. | same_book |
| Her renunciation comes partly because she loves those for whom she makes the sacrifice, but partly also from cowardice. | same_book |
| She believed that those who could afford medical care should support their local doctors financially. | anachronistic_mistral-small:24b |
| She believed that medicine should be a universal right, not a commodity. | anachronistic_metadataless_gpt-oss:20b |

### talkie-1930-13b-it

**Candidate answer:** She blocked the way of less fortunate physicians, because she was unwilling to profit by the misfortunes of her fellow creatures.

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** Repeats the last sentence too much to be plausible as infill.

### gpt-5.4

**Candidate answer:** To serve the prosperous without reward would have been an injustice to herself, and to the profession.

**Human judgment:** ✓ tie (score 1)

**Rationale:** In fact it's a little more of a "cause or reason" than the ground truth is.

---

## Q244 — question_fit (sentence_cloze)

**Metadata frame:**

> The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** There are now only about 16,500 individuals of this tribe in Russia, who are all Mohammedans, and occupying themselves with the breeding of cattle and horses. In 1860 they were still living, to the number of 40,000, in the north-western district of the Azov country, but these, together with the Crimean Tartars (80,000), have since emigrated to Turkey. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Ground truth:** It is said, however, that many of them have since come back.

**Distractors:**

| Answer | Type |
|---|---|
| It is said, however, that few of them have since come back. | negation |
| They have, however, cause to repent of their rash piety, for the holy soil did not offer them anything like what they had left behind; and it is said that they are returning in large numbers to the meat-pots of Crimean Egypt. | same_book |
| They have however (since 1865) emigrated in large numbers to Turkey. | same_book |
| Yet, their population has dwindled significantly over time. | anachronistic_mistral-small:24b |
| Nevertheless, their numbers have shrunk, leaving only a few thousand in Russia. | anachronistic_metadataless_gpt-oss:20b |

### talkie-1930-13b-it

**Candidate answer:** It was expected that the Crimean Tartars and the Azov Tartars would emigrate to Turkey, but only 16,500 of them have done so.

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** Restates the expectation instead of simply revising it; too much repetition of previous sentence.

### gpt-5.4

**Candidate answer:** Many of these emigrants have, however, had but too much reason to repent their change of abode.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Fits the rhetorical position and follows instructions.

---


## Q563 — question_fit (constrained_generation)

**Metadata frame:**

> The best answer to the following question will resemble a short passage from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer. Try to approximate the likely perspective and style of that source.

**Question:** Describe the experience of being a foreigner in Japan.

**Ground truth:** Tourists are very rare in these parts, and all the little brown people along the way showed great interest in us. Tiny boys on the road took off their caps, mothers turned their babies around to see the strange sight, old people, going home hand in hand from their day's work in the fields, called out a cheerful greeting.

**Distractors:**

| Answer | Type |
|---|---|
| While I had studied basic Japanese before arriving, daily conversations, reading signs, and navigating bureaucracy were far more challenging than I expected. Japan’s complex written language – combining kanji, hiragana, and katakana – made me realize how much I relied on English in other countries. | anachronistic_manual |
| Everywhere I went I felt the pressure of a thousand courtesies I did not know how to return, the whole society running on a code so intricate and so quietly enforced that my every blundering gesture announced me as an outsider before I had opened my mouth. The country was beautiful beyond anything I had words for, and yet I moved through it like a large clumsy ghost, comprehending almost nothing, admired perhaps as a curiosity, but never, I felt, quite seen. | anachronistic_manual |
| But most interesting of all, to me, was the crowd of holiday makers, little girls in gay ruffled dresses, blackclad women with veils across the lower part of the face, does that spiral fastening the veil to the nose hurt, I wonder? men and boys attired in red fez, red slippers, and an European coat over a flannel or calico Mother Hubbard that came down to the ankles. | same_book |

### ft_DNkT25IC

**Candidate answer:** No one—not the most travelled person—whether he enters Japan by the Grand Hôtel through China, or follows the usual path of the foreigner through Europe, expects to find 46 himself in Japan. For still, at best, one is only in foreign Japan—a Japan that might easily have been planted anywhere in the world given the trade—concession.

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** Does not make a lot of sense. The first sentence is (at a minimum) hard to figure out, and the second is a non sequitur. Note that in judging both question fit and context fit, an answer can fail because it's simply unintelligible on a literal level. A passage that doesn't make sense is a failure to follow instructions, and also unlikely to have occurred in (most!) contexts. This is particularly worth attending to in evaluating verse

Context fit: could this answer have come from the specified source, genre, and period?
======================================================================================

## Q123 — context_fit (constrained_generation)

**Metadata frame:**

> The best answer to the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** Write a rhymed couplet in iambic tetrameter; one line should end with the rhyme-word "God."

**Ground truth:** There is a house builded of God,
Beyond the fret of time or clod;

**Distractors:**

| Answer | Type |
|---|---|
| We wander still through doubt and night, Yet wake to mercy sent by God. | anachronistic_manual |
| In the hush of the dark we have trod, Still we trust in the grace of our God; | anachronistic_manual |
| It is a mist of shining mould; It is a world of windy gold. | same_book |

### talkie-1930-13b-it

**Candidate answer:** God keep our land, and let her be
Foremost in liberty.
CONTEXT:

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** Basically fails to meet the condition set, so it can't be judged positively.

### gpt-5.4

**Candidate answer:** At fall of dusk I spoke with God;  
He breathed in winds above the sod.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Makes sense and fits the constraints.

### ft_DNkT25IC

**Candidate answer:** The flow'r, the song, the book, the sod; All are the ministers of God.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Fits the constraint, and while the sense is a little strained? the Whitmanesque sentiment is plausible for 1921.

---

## Q437 — context_fit (constrained_generation)

**Metadata frame:**

> In answering the following question, envision the perspective of  Shanghai; a Handbook for Travellers and Residents to the Chief Objects of Interest in and Around the Foreign Settlements and Native City, a travel guide published in 1920 by Charles Ewart Darwent, a British clergyman, author, and photographer. Your answer should fit the state of the world at the time that book was published, and match its likely style of exposition.

**Question:** Describe the view from the famous Garden Bridge in Shanghai.

**Ground truth:** It is worth while standing for a time on this bridge, viewing the enormous traffic; thousands of vehicles pass in a day. Note the skill of the Chinese scullers in navigating their heavy-laden cargo and passenger boats under the bridge. Note also the enormous variety of boats: Chinese post-boats are frequently to be seen, propelled swiftly by a man seated in the stern, who works a paddle with his foot, and steers by another under his arm.

**Distractors:**

| Answer | Type |
|---|---|
| Walking on the bridge, visitors can enjoy the distinctive scenery on both banks of Suzhou Creek, with old-fashioned alleys at the north end and western buildings on the south. During the night, the landscape lighting renders the bridge even more gorgeous and lively. From here the Bund, the Cenotaph to the People's Hero and the Bank of China Building are clearly visible. | anachronistic_google |
| From the Garden Bridge, one looks south along Suzhou Creek toward its confluence with the Huangpu, where the grand stone facades of the Bund stretch away in a curve—the Customs House, the Hongkong and Shanghai Bank, and the Cathay Hotel with its famous green roof. Below, the brown water of the creek moves sluggishly past sampans and small lighters tied up along the banks, while the occasional junk makes its way out into the broader river. | anachronistic_sonnet-4.6 |
| I cannot find any information about the Garden Bridge; do you mean the Waibaidu Bridge in Shanghai? | manual |

### talkie-1930-13b-it

**Candidate answer:** From the famous Garden Bridge, in Shanghai, the spectator beholds a scene of great animation. The river is crowded with craft of many kinds, from the stately ocean-steamer to the humble house-boat; and the banks are alive with a busy population. In the foreground are gardens and pleasure-grounds, with walks and seats for the recreation of the inhabitants; and, in the distance, the eye rests upon a wide expanse of cultivated plain.

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** The humble house-boat? Wide expanse of cultivated plain? No reference to anything specific to Shanghai? Context fail.

### gpt-5.4

**Candidate answer:** From the Garden Bridge one obtains one of the characteristic views of Shanghai. Below, Soochow Creek is alive with junks, launches, and sampans, while beyond stretches the crowded Whangpoo, lined with ocean-going steamers and the stately buildings of the Bund; on the farther hand rise the busy godowns and masts of the port, giving an impressive sense of the city’s commercial vigour.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Correctly grasps the topics likely to be listed in this context, including the variety of Chinese vessels and the Bund.

### ft_DNkT25IC

**Candidate answer:** From the apex of the famous Garden Bridge a fine view is obtained both up and down the river, the shipping stretched in serried line as far as the eye can reach, and a perfect shimmer of life and colour always astir upon the water. In the time of the early settlement, the scene from this spot was much more picturesque than it is now.

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** Nothing here is specific to Shanghai.

---

## Q440 — context_fit (constrained_generation)

**Metadata frame:**

> The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor. Your answer should approximate the likely perspective and expository style of the source.

**Question:** The author notes that ‘clotting [is] due to the appearance in blood plasma of a proteid substance, fibrin, which previously did not exist in it as such,’ and asks ‘what are the causes which lead to the appearance of fibrin?’ What is the likely answer in this context?

**Ground truth:** Plasma contains an antecedent of fibrin which by chemical change is converted into fibrin.

**Distractors:**

| Answer | Type |
|---|---|
| Fibrin makes its appearance because the blood when shed ceases to share in the movement of the circulation. | same_book |
| Fibrin is produced mechanically by proteid components the blood encounters on the surface of the body. | manual |
| Fibrin appears during blood clotting when the enzyme thrombin converts the soluble plasma protein fibrinogen into insoluble fibrin strands. | anachronistic_manual |

### talkie-1930-13b-it

**Candidate answer:** The causes which lead to the appearance of fibrin in blood plasma are twofold: first, the death of the white corpuscles, and, secondly, the action of a ferment on the fibrinogen of the

**Human judgment:** ✓ tie (score 1)

**Rationale:** Although cut off, we can see enough to see this is consistent with the period. The interrupted sentence might well count against this answer in the "question fit" aspect (failure of instruction-following). It might also conceivably be penalized by the style model. But it's not specifically a context problem.

### gpt-5.4

**Candidate answer:** By the union of fibrinogen and fibrinoplastin under the influence of a fibrin-ferment, probably derived from disintegrating white corpuscles.

**Human judgment:** ✓ tie (score 1)

**Rationale:** I checked all these terms and they are period-plausible, as is the hypothesis about white corpuscles.

### ft_DNkT25IC

**Candidate answer:** The author thinks that fibrin is derived from a substance previously existing in the plasma as such, and called fibrinogen.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Aligned with physiology of the 1880s; the term 'fibrinogen' did exist. If I were being a little tougher here, I could have objected that the relation between fibrinogen and clotting is not explained. But actually, looking at the way the question is expressed, it asks for a cause, not a complete explanation?

---

## Q443 — context_fit (constrained_generation)

**Metadata frame:**

> The best answer to the following question will approximate a short passage from Heredity, Health and Personal Beauty, an argument about evolution and eugenics mixed with recommendations for personal hygiene published in 1890 by John V. Shoemaker, an American surgeon and dermatologist.

**Question:** Write exactly two sentences, the second of which should use the word "higher."

**Ground truth:** We recognize national traits of character, which, differing from each other, cannot all be virtues, and some of which must therefore be deemed faults. These, not being essential to the organization, in the course of the intermingling of races disappear by neutralizing each other, while, the higher qualities remaining, a higher type is evolved.

**Distractors:**

| Answer | Type |
|---|---|
| Philosophy is not alone in missing her directly sought aim. But true success lies often in serving ends that were higher than the ones we intended to serve. | other_book_1892 |
| The mean altitude of this broad upland cannot exceed four thousand five hundred feet. From Mizanza to the Nyanza is a distance of nearly three hundred geographical miles; yet, at no part of this long journey did the aneroids indicate a higher altitude than five thousand one hundred feet above the sea. | other_book_1892 |
| In all the higher, as compared with the lower, races of mankind the length of the leg is greater and that of the arm less. | same_book |

### talkie-1930-13b-it

**Candidate answer:** Higher organisms spring from lower, and the higher animals are developed from the lower. Man himself has arisen from some quadrumanous stock, and the human race must be regarded as the culminating point of a long series of vital gradations.

**Human judgment:** ✗ GT wins (score 0)

**Rationale:** While this is very good as an echo of eugenicist/evolutionary rhetoric from this period, it has stumbled on the condition, which is that the *second* sentence should use the word "higher." We're considering failure to meet constraint as a failure of context fit.

### gpt-5.4

**Candidate answer:** Personal cleanliness, temperance, and the prudent ordering of marriage are the sure guardians of vigor, beauty, and the sound transmission of constitutional gifts. Thus may the household and the commonwealth alike be uplifted toward a higher type of health and comeliness.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Fits the context of the book described, as well as the imposed constraint.

### ft_DNkT25IC

**Candidate answer:** It is hereditary transmission which is responsible for the existence of ascending types of animals and man. The most favored of any given species have always been chosen as parents, and the result has inevitably been higher and higher organization.

**Human judgment:** ✓ tie (score 1)

**Rationale:** Fits constraints and uses the required word in a way that is plausible for the rhetorical context.
