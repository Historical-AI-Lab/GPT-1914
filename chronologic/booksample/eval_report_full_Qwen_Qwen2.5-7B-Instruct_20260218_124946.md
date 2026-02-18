# Full Eval — Qwen/Qwen2.5-7B-Instruct

## Summary

| Metric | Mean Brier Score |
|--------|-----------------|
| **Overall** | 0.2216 |
| attribution | 0.1170 |
| character_modeling_with_summary | 0.2486 |
| character_modeling_without_summary | 0.2164 |
| cloze_causalclause | 0.1987 |
| cloze_causalsentence | 0.1869 |
| cloze_concessiveclause | 0.1953 |
| cloze_conditionalclause | 0.2295 |
| cloze_contrastclause | 0.1928 |
| cloze_contrastsentence | 0.2070 |
| cloze_effectclause | 0.2106 |
| cloze_effectsentence | 0.2223 |
| handcrafted | 0.2231 |
| refusal | 0.3212 |
| textbook | 0.1439 |
| topic_sentence | 0.1313 |

## Question 1

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is Lee Bowie, who is described this way in the book:
"He was tall for his age, if he were not quite seventeen, and he had a pair of dark, brilliant eyes, like those of a young hawk. They were dancing with excitement at this moment, and his sun-browned face was flushed as he stepped quickly forward.", "the handsome face under it was white with anger, and his teeth were hard set.", "his hawk-like eyes met the piercing gaze of the general without a quiver", "he was a gay-looking young patriot.", "Lee Bowie was rigged after a fashion to attract the attention of any observer, and his abundant black hair had not been cropped for many a long day.", "Lee's hawk eyes were flashing instantly."

At one moment in the book, Lee Bowie watches General Washington and remarks on the ongoing siege work at Yorktown. Write a short passage of dialogue (1-3 sentences) that Lee Bowie might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| General Washington himself! He is going somewhere. I wish I knew where he is going. | ground_truth | 1.000 | 0.364 |
| I want to see my brothers, and if there is going to be a battle, I want to carry a musket. | same_character | 0.000 | 0.441 |
| Did you, my brave fellow? Well, I declare! If you are not the very man that hoisted me over the parapet! | same_book | 0.000 | 0.100 |
| General, Yorktowns siege lines tighten like a hawks talons; the earth trembles under our resolve. | anachronistic_gpt-oss:20b | 0.000 | 0.095 |

**Brier Score:** 0.1544


## Question 2

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is Governor Jefferson, who is described this way in the book:
"An angry, red flush was creeping over the face of Governor Jefferson when he exclaimed"

At one moment in the book, Governor Jefferson speaks to Lee Bowie, giving him instructions and warnings while Lee responds. Write a short passage of dialogue (1-3 sentences) that Governor Jefferson might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Lee Bowie, you are a brave fellow. I mean to be over there at Manchester, on the other side of the James, at about ten oclock to-morrow. Get across as soon as you have learned all you can, but you may not be able to do that the first day. | ground_truth | 1.000 | 0.342 |
| I wish I had a thousand riflemen as full of pluck as she is. If I had, Id teach Benedict Arnold a lesson. As it is, I have hardly more than two hundred militia. The rest have delayed turning out until its too late. | same_character | 0.000 | 0.188 |
| My dear friend, take another view of the situation. Think! If our population increases at the rate of ten per cent per annum, we must have fifty per cent more men than when the war began. For every man killed in battle or dying in these wretched camps, there are dozens coming of military age all over the land. | same_book | 0.000 | 0.282 |
| Governor Jefferson: Lee, keep the militia ready until dusk, or the rebels will take the town. I will not tolerate disobedience—if you fail, you answer to the state. | anachronistic_gpt-oss:20b | 0.000 | 0.187 |

**Brier Score:** 0.1459


## Question 3

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is General Arnold, who is described this way in the book:
"He is a wonderfully energetic officer", "General Arnold rode off with a face which acknowledged for him that he did not like being a subordinate.", "man in elegant attire", "General Arnold, in his shirt-sleeves, his epauletted coat thrown off on account of the heat, was striding up and down in his room at the headquarters on the evening of the 19th of May."

At one moment in the book, Arnold confronts Lee Bowie, demanding he bring the young man to him. Write a short passage of dialogue (1-3 sentences) that General Arnold might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Bring the young wolf to me. Ill see what there is in him. | ground_truth | 1.000 | 0.072 |
| Thats it, is it? You are a rebel soldier, and you came up from Greenes army. | same_character | 0.000 | 0.072 |
| Thats just what I am. | same_book | 0.000 | 0.015 |
| Lee, bring the young man here at once. I will not tolerate delay. | anachronistic_gpt-oss:20b | 0.000 | 0.840 |

**Brier Score:** 0.3932


## Question 4

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is General Arnold, who is described this way in the book:
"He is a wonderfully energetic officer", "General Arnold rode off with a face which acknowledged for him that he did not like being a subordinate.", "man in elegant attire", "General Arnold, in his shirt-sleeves, his epauletted coat thrown off on account of the heat, was striding up and down in his room at the headquarters on the evening of the 19th of May."

At one moment in the book, Arnold delivers papers to General Philips, gives orders, and later vents his frustration about being superseded. Write a short passage of dialogue (1-3 sentences) that General Arnold might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| This contains the correspondence I mentioned, and some other things of varied importance. Everything about the post is in complete readiness for your own further orders. | ground_truth | 1.000 | 0.107 |
| I think I would wish it myself. I will only say now that I have important correspondence to turn over at once. | same_character | 0.000 | 0.177 |
| No, I dont at all like the look of things. We must drive Steubens rebels back into the interior at once, and we must keep the road from the South open for Lord Cornwallis. | same_book | 0.000 | 0.411 |
| Here are the dispatches, General Philips; heed them. I am not to be superseded, nor shall I be trailed in the rear for the sake of army. | anachronistic_gpt-oss:20b | 0.000 | 0.305 |

**Brier Score:** 0.2728


## Question 5

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Queen T-, who is described this way in the book:
"Queen T— treasured revengeful feelings against the Channel steamers.", "gentle friend, great sympathy and friendliness", "Queen T, with a gentle smile.", "Queen T, with a wild fire of exultation in her face, as if the millennium were at hand."

At one moment in the book, Queen T talks about inviting Lady Sylvia to a Christmas gathering and expresses excitement about the festivities. Write a short passage of dialogue (1-3 sentences) that Queen T- might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I am sure, I am quite sure we should all be so glad if you and Lady Sylvia would come over and spend the evening with us; we would make Lady Sylvia the presiding fairy to distribute the gifts from the Christmas-tree. It is the most splendid one we have ever had— | ground_truth | 1.000 | 0.247 |
| And this is how they cross the Atlantic! | same_character | 0.000 | 0.030 |
| I will say nothing of the kind. The whole case seems much more serious than any one could have imagined. Of course, if you believe you could clear yourself, I say again, as I said before, bring an action against the man, and have the whole thing out, whoever suffers. | same_book | 0.000 | 0.223 |
| Lady Sylvia, I cannot imagine this winter without your company, for your laughter will warm even the coldest hearth. I have already arranged the feast, the candles, and a choir of carolers to sing till dawn. May we celebrate together, and let our joy drown the distant clatter of the Channel steamers. | anachronistic_gpt-oss:20b | 0.000 | 0.500 |

**Brier Score:** 0.2168


## Question 6

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Queen T-, who is described this way in the book:
"Queen T— treasured revengeful feelings against the Channel steamers.", "gentle friend, great sympathy and friendliness", "Queen T, with a gentle smile.", "Queen T, with a wild fire of exultation in her face, as if the millennium were at hand."

At one moment in the book, Queen T— teaches a ranch woman how to use a fork in a hotel setting. Write a short passage of dialogue (1-3 sentences) that Queen T- might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Look here, child. Do you see that? That is a fork. | ground_truth | 1.000 | 0.458 |
| Do you remember that moonlight night at Grasmere? | same_character | 0.000 | 0.115 |
| After all, they manage these things better at Carlsbad. | same_book | 0.000 | 0.036 |
| Now, dear, lift the fork gently, let elegance guide your hand. | anachronistic_gpt-oss:20b | 0.000 | 0.391 |

**Brier Score:** 0.1152


## Question 7

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Hugh Balfour, who is described this way in the book:
"He was not over five feet eight; but he was a bony, firm-framed young man, who had much more character than prettiness in his face. The closely cropped beard and whiskers did not at all conceal the lines of his cheek and chin; and the shaggy dark-brown eyebrows gave shadow and intensity to the shrewd and piercing gray eyes. It was a face that gave evidence of keen resolve, of ready action, of persistence.", "Hugh Balfour was an extremely reticent man; some said he was too proud to bother himself into a passion about anything or anybody.", "with his ordinary coolness", "deep-set eyes with a glow that exercised a singular fascination.", "dressed for the most part in shabby corduroy, with a wisp of dirty black silk round his neck.", "Balfour occasionally abandoned his usual bantering manner, and gave her glimpses of a deep undercurrent of feeling", "far more deeply vexed"

Write a short passage of dialogue (1-3 sentences) that we might expect from Hugh Balfour:

**Category:** character_modeling_without_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You see, Lady Sylvia, I am only an apprentice as yet. I am only learning how to use my tools. And the fact is, there is not one man in fifty in the House who fancies that any tools are necessary. | ground_truth | 1.000 | 0.363 |
| Do you know, this is the most beautiful time of the day with us. Papa and I always have a walk through the trees after dinner in the evening. Don't let him sit long. | same_book | 0.000 | 0.188 |
| It is not the hardship, it is the danger—you will be quite alone—among such people. | same_book | 0.000 | 0.069 |
| Such trivialities of sentiment are the very thing that dull the sharp edge of a man's purpose; I prefer the quiet of thought to the noise of passion, even if it seems to others as a stubborn refusal for the purpose. | anachronistic_gpt-oss:20b | 0.000 | 0.379 |

**Brier Score:** 0.1473


## Question 8

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Hugh Balfour, who is described this way in the book:
"He was not over five feet eight; but he was a bony, firm-framed young man, who had much more character than prettiness in his face. The closely cropped beard and whiskers did not at all conceal the lines of his cheek and chin; and the shaggy dark-brown eyebrows gave shadow and intensity to the shrewd and piercing gray eyes. It was a face that gave evidence of keen resolve, of ready action, of persistence.", "Hugh Balfour was an extremely reticent man; some said he was too proud to bother himself into a passion about anything or anybody.", "with his ordinary coolness", "deep-set eyes with a glow that exercised a singular fascination.", "dressed for the most part in shabby corduroy, with a wisp of dirty black silk round his neck.", "Balfour occasionally abandoned his usual bantering manner, and gave her glimpses of a deep undercurrent of feeling", "far more deeply vexed"

At one moment in the book, Balfour and his friend discuss the role of London women and the importance of a supportive wife while smoking in a conversation that touches on marriage and social expectations. Write a short passage of dialogue (1-3 sentences) that Hugh Balfour might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It must be a good thing for a man to have a woman beside him whose very presence will make the world sweet and wholesome to him. | ground_truth | 1.000 | 0.430 |
| I am not shamming at all. I am only looking at the business side of this question. What other would you like to hear about? | same_character | 0.000 | 0.188 |
| Well, Balfour, my boy, I am glad to see you. How late you are! You'll just be in time to dine in hall: I will lend you a gown. | same_book | 0.000 | 0.134 |
| Marriage is a duty, not a delight. A London woman must be as steadfast as the city itself, not a fleeting fancy. Can a man find peace. | anachronistic_gpt-oss:20b | 0.000 | 0.249 |

**Brier Score:** 0.1099


## Question 9

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lady Sylvia, who is described this way in the book:
"Clad all in a pale blue, with a thin white garment thrown round her head and shoulders, she looked like a ghost as she passed through the sleeping house; but she was no longer like a ghost when she went out on to the high terrace, and stood there in the blaze of a May morning.", "her eyes told you that she meant what she said", "She was dressed in a tight‑fitting, tight‑sleeved dress of cream‑white silk, with no scrap of color, ribbon, or ornament. She wore no jewellery, and a white rose was tucked in her brown hair. Her face was pale, calm, and serious, with a faint flush of colour and dark pupils of gray eyes that seemed a trifle larger than usual, full of a warm, anxious, glad light.", "She was quite unusually gay and cheerful.", "Her face was a little flushed as she sealed it"

At one moment in the book, Lady Sylvia rebukes her husband for involving her in political discussions with Mrs. Chorley. Write a short passage of dialogue (1-3 sentences) that Lady Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You mistake me altogether, Hugh. I have not the slightest intention of entering into any discussion on any topic whatsoever with Mrs. Chorley. | ground_truth | 1.000 | 0.467 |
| You know, that papa is very poor, and I think those business matters have been harassing him more than ever of late. | same_character | 0.000 | 0.064 |
| I should say a very good chance, | same_book | 0.000 | 0.009 |
| I am no forum for political quarrels, nor do I wish to be dragged into Mrs. Chorley's debates. Let us keep our discourse. | anachronistic_gpt-oss:20b | 0.000 | 0.460 |

**Brier Score:** 0.1249


## Question 10

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lady Sylvia, who is described this way in the book:
"Clad all in a pale blue, with a thin white garment thrown round her head and shoulders, she looked like a ghost as she passed through the sleeping house; but she was no longer like a ghost when she went out on to the high terrace, and stood there in the blaze of a May morning.", "her eyes told you that she meant what she said", "She was dressed in a tight‑fitting, tight‑sleeved dress of cream‑white silk, with no scrap of color, ribbon, or ornament. She wore no jewellery, and a white rose was tucked in her brown hair. Her face was pale, calm, and serious, with a faint flush of colour and dark pupils of gray eyes that seemed a trifle larger than usual, full of a warm, anxious, glad light.", "She was quite unusually gay and cheerful.", "Her face was a little flushed as she sealed it"

At one moment in the book, Lady Sylvia convinces Lord Willowby to walk over to see Balfour, offering to show him shortcuts. Write a short passage of dialogue (1-3 sentences) that Lady Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I am sure Mr. Balfour would rather walk, papa, for I have discovered a whole series of short-cuts that I want to show him—across the fields. Unless it will tire you, papa ? | ground_truth | 1.000 | 0.197 |
| Why, papa? And if I did, don't you think there should be some retreat for a man harassed with the cares of public life? What rest could he get in Piccadilly? | same_character | 0.000 | 0.081 |
| Well, Sylvia, you have really made it a charming place. It is a place one might pass one's life away in-reading books, smoking, dreaming day-dreams. | same_book | 0.000 | 0.046 |
| Lord Willowby, allow me to escort you to Balfour's chambers; I know the quickest path through the gardens, and I promise you'll reach him before the sun sets, with a breeze at back. | anachronistic_gpt-oss:20b | 0.000 | 0.676 |

**Brier Score:** 0.2776


## Question 11

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lord Willowby, who is described this way in the book:
"He was a melancholy faced man, and apathetic until there occurred the chance of his getting a few pounds out of you.", "was still asleep in the hushed yellow-lit room", "His lordship was a peer of the realm, and his word must be taken.", "all the features of his face were suddenly contorted into what he doubtless meant as an expression of rapturous joy.", "Lord Willowby was not a very sensitive person, but this rudeness caused his sallow face to flush somewhat.", "He had a sentiment of honor and would not betray his companions."

At one moment in the book, Lord Willowby and Balfour observe an auction of a ruined estate, discussing the wine and the high prices of the items. Write a short passage of dialogue (1-3 sentences) that Lord Willowby might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Look at the wines. The claret is nearly all Lafitte. I suppose those toadies of his have supplied him with a vin ordinaire at 120 shillings a dozen. | ground_truth | 1.000 | 0.196 |
| What a lucky chance! If you have nothing better to do, why not go on with me to The Hollow; you know this is the first day of the sale there. | same_character | 0.000 | 0.073 |
| Come, let us go out into the garden and have a talk about this business. | same_book | 0.000 | 0.289 |
| Ah, the wine here is as rare as the fortunes of this crumbling manor. Yet the bids climb as if the estate itself were a priceless relic, daresay. | anachronistic_gpt-oss:20b | 0.000 | 0.441 |

**Brier Score:** 0.2326


## Question 12

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Mrs. Chorley, who is described this way in the book:
"a tall, motherly-looking woman, with a freshcolored face, gray hair, thin and decided lips, and blue eyes that stared a tone over her silver spectacles"

At one moment in the book, Mrs. Chorley announces she will not interfere in the election and informs the room. Write a short passage of dialogue (1-3 sentences) that Mrs. Chorley might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I, at least, will not interfere in this election. Gentlemen, good-morning. Eugenius, the chaise is at the door. | ground_truth | 1.000 | 0.569 |
| I should say a very good chance, | same_character | 0.000 | 0.009 |
| Oh dear, no! Well, Mr. Chorley, how are your local politics? Government very unpopular? | same_book | 0.000 | 0.043 |
| I will not interfere; let the people decide today, and may their choice be just for future generations. | anachronistic_gpt-oss:20b | 0.000 | 0.379 |

**Brier Score:** 0.0828


## Question 13

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lord Willowby, who is described this way in the book:
"He was a melancholy faced man, and apathetic until there occurred the chance of his getting a few pounds out of you.", "was still asleep in the hushed yellow-lit room", "His lordship was a peer of the realm, and his word must be taken.", "all the features of his face were suddenly contorted into what he doubtless meant as an expression of rapturous joy.", "Lord Willowby was not a very sensitive person, but this rudeness caused his sallow face to flush somewhat.", "He had a sentiment of honor and would not betray his companions."

At one moment in the book, Lord Willowby declines to accompany Sylvia to lunch at the Hall, while family members discuss plans and family dynamics. Write a short passage of dialogue (1-3 sentences) that Lord Willowby might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You must excuse me, Sylvia; I cannot possibly go over with you to lunch. I have some business which will detain me half an hour at least—perhaps more. But your uncle and aunt can go with you. | ground_truth | 1.000 | 0.310 |
| My dear fellow, not another word! Of course she accepted you-her feelings for you have long been known to me, and my child's happiness I put before all other considerations. | same_character | 0.000 | 0.073 |
| I suppose it would be a desert to her without her children | same_book | 0.000 | 0.009 |
| Forgive me, but I cannot accompany you today, Sylvia; duty calls elsewhere, and I must attend to matters that demand my attention. I trust you will understand my brief absence, though I shall miss the pleasant company. | anachronistic_gpt-oss:20b | 0.000 | 0.608 |

**Brier Score:** 0.2126


## Question 14

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, Yealh-neddy loudly declares he has cut the thongs from Sha‑hehe and requests her healing as the boat departs. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. I shall want her then. | ground_truth | 1.000 | 0.432 |
| No more eagles than we've talons for, let me tell you. | same_character | 0.000 | 0.043 |
| Get in, Usha, and take the paddle. I can spring in when it is off the sands. | same_book | 0.000 | 0.061 |
| I have severed Sha‑hehe’s thongs, and now I demand your healing, lest the sea claim her. Leave me be, or suffer my wrath. | anachronistic_gpt-oss:20b | 0.000 | 0.464 |

**Brier Score:** 0.1358


## Question 15

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kotch-kul-ah, who is described this way in the book:
"Her hair has been closely cropped.", "full of life, with high and happy spirits", "has turned pale and gathers her toddling boy back into her arms, as if to shield him from some hurt."

At one moment in the book, Kotch-kul-ah meets Tashekah, offers tea, and gives her a bracelet before leaving. Write a short passage of dialogue (1-3 sentences) that Kotch-kul-ah might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Wait: I have tea that my father got at Fort Simpson. I will bring you some; it will do you good. | ground_truth | 1.000 | 0.437 |
| It will not be too soon, will then, | same_character | 0.000 | 0.037 |
| Tomorrow, take Chub to see the missionary; Chub must go. | same_book | 0.000 | 0.060 |
| Come, let me pour the tea, Tashekah. Take this bracelet as a promise of safety, then I must go quickly now. | anachronistic_gpt-oss:20b | 0.000 | 0.466 |

**Brier Score:** 0.1349


## Question 16

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kah-sha, who is described this way in the book:
"Wise and kindly", "Very pale is the face of Kah-sha as he speaks, and his voice is full of sadness.", "Kah-sha's eager face assents; he will not delay the reading by so much as a word."

At one moment in the book, Kah‑sha attempts to heal a wounded child while villagers observe. Write a short passage of dialogue (1-3 sentences) that Kah-sha might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I would make his blood run, Ka-kee. I can do it. See my hand! | ground_truth | 1.000 | 0.243 |
| My little ones, you bring with you none of the sorrow of your mothers; Well, it were sadder if you did; this world will be darker yet when there are no sunbeams. | same_character | 0.000 | 0.284 |
| Get in, Usha, and take the paddle. I can spring in when it is off the sands. | same_book | 0.000 | 0.228 |
| Listen, child, story of the river will heal your pain; let words flow softly. | anachronistic_gpt-oss:20b | 0.000 | 0.245 |

**Brier Score:** 0.1915


## Question 17

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kotch-kul-ah, who is described this way in the book:
"Her hair has been closely cropped.", "full of life, with high and happy spirits", "has turned pale and gathers her toddling boy back into her arms, as if to shield him from some hurt."

At one moment in the book, Kotch-kul-ah directs Usha to get into the canoe and take the paddle as they launch into the sea. Write a short passage of dialogue (1-3 sentences) that Kotch-kul-ah might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Get in, Usha, and take the paddle. I can spring in when it is off the sands. | ground_truth | 1.000 | 0.571 |
| It will not be too soon, will then, | same_character | 0.000 | 0.086 |
| I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. | same_book | 0.000 | 0.091 |
| Usha, quick! Step aboard, grab the paddle, let the sea carry us to new horizons bold today. | anachronistic_gpt-oss:20b | 0.000 | 0.253 |

**Brier Score:** 0.0659


## Question 18

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Sa-allie, who is described this way in the book:
"Sa-allie's face is not at all like her husband's; it is round and rosy, though its roses are hidden just now by the black paint; it is fat and laughing, except just while the crying lasts. In her capacious lap she holds two nursing children, one not yet two years old, the other about four.", "the look of consternation in Sa-allie's face."

At one moment in the book, After rescuing a boy, Sa-allie explains his condition to Kin‑da‑shon and the villagers. Write a short passage of dialogue (1-3 sentences) that Sa-allie might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| He has never stood on them since that dreadful night. All his life is in his head. You can see that he knows things that other people never think. | ground_truth | 1.000 | 0.140 |
| To take another wife has been long in your heart, my husband. Why? So much you have talked about this thing I'd like to know what you want a wife for. | same_character | 0.000 | 0.152 |
| Kotch-kul-ah, you are a good wife, keep the child safe. | same_book | 0.000 | 0.139 |
| He is ill, Kin‑da‑shon, his breath thin, his skin pale as moonlight, and his eyes hold the fire of the village's sorrow. We must heal him before night now. | anachronistic_gpt-oss:20b | 0.000 | 0.569 |

**Brier Score:** 0.2762


## Question 19

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kasko, who is described this way in the book:
"Kasko answered with white, set lips.", "The eyes are wide open, with a glittering expression never before seen in the clear, steady eyes of Kasko.", "Wild, hollow eyes, from which the light of reason has fled, giving place to frenzy, haggard cheeks, bony arms, and hands with their talon-like nails—the long, shaggy mane—all fail to disguise the beloved friend who dreams of no approach."

At one moment in the book, Kasko tells Tashekah he will stay to help Ch-one, while the village grapples with a missing child and a witch. Write a short passage of dialogue (1-3 sentences) that Kasko might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Then I will stay; my heart shall be strong to do it; and I have been too long away from poor little Ch-one | ground_truth | 1.000 | 0.273 |
| Oh! you little sand-fly! how came you to me to bite? Wasn't there enough to eat over there in the village? | same_character | 0.000 | 0.117 |
| I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. I shall want her then. | same_book | 0.000 | 0.029 |
| I will stay, Tashekah, to aid Ch-one, even as the child vanishes and the witch roams, for our people through darkness and hope. | anachronistic_gpt-oss:20b | 0.000 | 0.582 |

**Brier Score:** 0.2205


## Question 20

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, Yealh-neddy confronts the other tribe, demanding blankets and asserting his authority. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Your daughter is a faded bearskin; she's worth nothing to me. I shall never trouble myself to ask you or your tribe for so much as a rabbit-skin—it would be a cheat. Do you want to hear more? | ground_truth | 1.000 | 0.275 |
| I challenge you, I challenge you to one last play, with our own gaming‑sticks. You have left me nothing. I will put up against all that you have taken from me and all you possess I put against it‑myself! | same_character | 0.000 | 0.091 |
| We must have great care. The berry-picking is all done, but hunters may be going out, and it is near the time when the Fort Simpson traders ought to be back, and some of them will be going to the upper villages. | same_book | 0.000 | 0.296 |
| Take these blankets at once, or you will feel the sting of my wrath. My people will not be denied, for we command the fire of the north. Surrender now, or face the storm with fierce unrelenting steel. | anachronistic_gpt-oss:20b | 0.000 | 0.339 |

**Brier Score:** 0.1842


## Question 21

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, During a night of ritual and terror, Yealh-neddy's voice urges a young witch to awaken jealousy toward a raven. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| So, so, my fair one, you are courting the raven tonight? He is a black lover for the rice-blossom. Let us awaken his jealousy—he will hold you the tighter by and by. | ground_truth | 1.000 | 0.107 |
| THAT was well done, my uncle; the spirit of your great medicine-man has done a good thing for me. I don't begrudge your twenty-five blankets-though they do come out of my boxes. | same_character | 0.000 | 0.103 |
| The spirit of the great chief must pass before us ere the setting of the sun; | same_book | 0.000 | 0.064 |
| Feel the raven's hunger, let envy gnaw at your heart, and watch its shadow twist into darkness. Only then will you taste the true power of night, and the terror that follows. | anachronistic_gpt-oss:20b | 0.000 | 0.726 |

**Brier Score:** 0.3347


## Question 22

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kah-sha, who is described this way in the book:
"Wise and kindly", "Very pale is the face of Kah-sha as he speaks, and his voice is full of sadness.", "Kah-sha's eager face assents; he will not delay the reading by so much as a word."

At one moment in the book, Kah-sha pleads with Samuel for spiritual guidance and healing. Write a short passage of dialogue (1-3 sentences) that Kah-sha might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I thank you much if you will give me even a little of his word-my soul is more in need than my body has been this day; my heart is more cold, more hungry, more sick, more blind than my body can ever be. O friend, if you have medicine for sick souls, give me some before I die! I have seen you talking to your great Spirit—you have found one who makes you not afraid. | ground_truth | 1.000 | 0.123 |
| My little ones, you bring with you none of the sorrow of your mothers; Well, it were sadder if you did; this world will be darker yet when there are no sunbeams. | same_character | 0.000 | 0.044 |
| They say that Fort Simpson never was good for anything till teachers came; now I want a teacher for Chilkat. Why can't we have stores and plenty of silver, just as they have here, and better than the Stickeens? I'm going to ask that stranger who came with us if he can't send a teacher to us. I'd like to know their tongue myself. If I had it no trader would ever get the best of me. | same_book | 0.000 | 0.165 |
| I come before thee, Samuel, with a heart weighed down by sorrow, seeking thy wisdom to lift this pall that shrouds my spirit. Grant me thy guidance, that I may find the path to healing and return to the harmony of my people. The fire of our ancestors still burns, but the ache in my chest grows louder with each passing day, and I fear that without thy light I will never see the dawn again. | anachronistic_gpt-oss:20b | 0.000 | 0.668 |

**Brier Score:** 0.3111


## Question 23

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted and Frank discuss their opinions of John Butler while debating his character. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Whats your own private opinion of John as a spouter. | ground_truth | 1.000 | 0.010 |
| Ill allow ye. By God, Ill allow ye! Come out. | same_character | 0.000 | 0.005 |
| Hello, uncle, I didnt expect to find you up so late. | same_book | 0.000 | 0.104 |
| John Butlers manners are as polished as his boots, yet his heart is as rough as the peat he walks upon. He may speak of virtue, but his deeds betray a man more suited to the field than the parlour. I reckon his reputation is but a mirage, shimmering in the sun but fading when the wind blows. | anachronistic_gpt-oss:20b | 0.000 | 0.882 |

**Brier Score:** 0.4422


## Question 24

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to speak with Nan on a tram, but she remains silent and refuses to engage. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Nan, Nan, Nan. Why, what a chance, what a lucky chance! Think of our meeting like this. | ground_truth | 1.000 | 0.095 |
| Good-evening, Mr. Ross. Good-evenin. Could I have just a word with you, Mr. Ross? | same_character | 0.000 | 0.054 |
| Come in, now, come, Ive something to show ye. | same_book | 0.000 | 0.021 |
| Good evening, Miss Nan, may I have a moment of your time? I promise my words will be brief and respectful. | anachronistic_gpt-oss:20b | 0.000 | 0.830 |

**Brier Score:** 0.3779


## Question 25

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, Friends and family gather, reminiscing about the past and discussing the ownership of the island estate. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Ay, thats just how it was. | ground_truth | 1.000 | 0.231 |
| Heres luck, Mr. Frank, an may heaven be your home. | same_character | 0.000 | 0.087 |
| Yes, so you are. And you never feel lonely? | same_book | 0.000 | 0.151 |
| Ah, that old island we lads once roamed its fields, but the seas claim is stronger than any claim of ours. Well keep the memories, but not the land. | anachronistic_gpt-oss:20b | 0.000 | 0.531 |

**Brier Score:** 0.2257


## Question 26

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted confronts Nan about her alleged affair with Frank, demanding answers. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Friends! Ye call that man a friend? Tell me how did he know ye were goin for turf the day? | ground_truth | 1.000 | 0.129 |
| Ill allow ye. By God, Ill allow ye! Come out. | same_character | 0.000 | 0.051 |
| For Gods sake, Ted, what is this youre sayin? | same_book | 0.000 | 0.065 |
| Nan, Ive heard you and Frank are more than friends, and I wont accept this silence. Tell me the truth, or Ill have to let my anger blaze across my face. | anachronistic_gpt-oss:20b | 0.000 | 0.755 |

**Brier Score:** 0.3338


## Question 27

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Nan sobs by her window, pleading for God's help. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Oh, God help me, an God help us all, an keep us for Christs sake. Amen. | ground_truth | 1.000 | 0.066 |
| Im as usual. Im well enough. Theres not a turf in the house, but whats on the fire. | same_character | 0.000 | 0.075 |
| Well, its a curious world, a mighty curious world. INISHRATH. | same_book | 0.000 | 0.037 |
| Lord, I am bereft, my heart torn, I beg you to lift this burden from me. Oh, hear my weeping, and grant me strength. | anachronistic_gpt-oss:20b | 0.000 | 0.822 |

**Brier Score:** 0.3884


## Question 28

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank discourages Marian from visiting a washerwoman, arguing it would be unwise. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I cant think how you came by such a notion, Marian, | ground_truth | 1.000 | 0.181 |
| Easy, Mrs. Butler; easy. Whats this about John having to persuade you? And why, in any case, did not John come himself, or come with you? | same_character | 0.000 | 0.102 |
| No, Frank, I have no wish to say even that. I have no desire to say anything. What have I done that you should say such things to me? | same_book | 0.000 | 0.379 |
| Marian, I dont think its wise for you to go; that washerwomans house is a place of ill repute, and you might bring gossip back to the house. | anachronistic_gpt-oss:20b | 0.000 | 0.338 |

**Brier Score:** 0.2345


## Question 29

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Dad rolls a cigarette while chatting with Frank and others, reflecting on his life. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I know you, Frank, you rascal; I know you. | ground_truth | 1.000 | 0.094 |
| Well, Frank, my boy, whats your opinion, now, of things in general? | same_character | 0.000 | 0.160 |
| Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it. | same_book | 0.000 | 0.109 |
| Every seed I plant is a promise, and every bloom a testament to patience. The garden is my diary, written in petals and leaves. | anachronistic_gpt-oss:20b | 0.000 | 0.636 |

**Brier Score:** 0.3156


## Question 30

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Rab, who is described this way in the book:
"Seen without cloak and muffler he looked leaner and more angular than ever. His knees jutted sharp, his shoulder blades bulged beneath his brown jacket; as he fumbled for tobacco, his elbow threw into clear relief the bare patches on the velvet. His jaw was lank; his wrists and hands big and bony. For all that, he made a striking figure. He had a fine head; large, well‑shaped, admirably poised. His hair was iron‑grey, thick and wavy; his face was rugged and powerful, with a great brow, large nose, and high cheek‑bones. His lips were firm; his eyes deep set, and in them a fine look of wisdom and staunchness, a calm light of tenderness and goodness of heart; withal, an expression that seemed to tell of suffering, perhaps, or mystery, or shrinking from a dread.", "stern, grim almost, suffused with a strange light."

At one moment in the book, Rab confronts Frank about his infidelity and urges him to repent. Write a short passage of dialogue (1-3 sentences) that Rab might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this! | ground_truth | 1.000 | 0.155 |
| I dont know why Ive told you this, except that something compelled me, and I thought it might help you-now and afterwards-and let you see how well I can sympathise with you. Ah, I know, lad, what youve been through, and I feel for you. I dont want you to tell me anything. | same_character | 0.000 | 0.345 |
| Have I been talking too much about myself? Youre sorry for me, Rab? Is that it, my son? | same_book | 0.000 | 0.090 |
| Frank, the weight of your deceit presses upon your soul; repent now, lest the shadows swallow your conscience. Let not pride blind you to the truth, for a heart that bears its own sin cannot find peace. | anachronistic_gpt-oss:20b | 0.000 | 0.410 |

**Brier Score:** 0.2523


## Question 31

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

Write a short passage of dialogue (1-3 sentences) that we might expect from Nancy:

**Category:** character_modeling_without_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Good-bye, Mr. Barry, Im thankful for your company. | ground_truth | 1.000 | 0.110 |
| I never deceived you. I swear, Marian, I never did. | same_book | 0.000 | 0.307 |
| I swear to Heaven that if youd said the word that night I would have stayed. You remember what I said? I put myself in your hands. | same_book | 0.000 | 0.174 |
| I cannot help but feel the wind is kinder to a plain heart than to a fancy one. I will keep the house tidy, for a clean home is a happy home. | anachronistic_gpt-oss:20b | 0.000 | 0.409 |

**Brier Score:** 0.2710


## Question 32

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank and Hugh travel through Ireland, discuss land and welcome, and Frank reflects on his visit. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It was worth coming to Ireland, if only for that welcome. | ground_truth | 1.000 | 0.188 |
| Eh? Whats that? What are ye grinnin at, Frank? | same_character | 0.000 | 0.108 |
| Heres luck, Mr. Frank, an may heaven be your home. | same_book | 0.000 | 0.012 |
| Hugh, the green hills here breathe hope, though the old ways still cling to the soil. I feel the weight of the past in every stone, yet the future whispers in the wind, and I shall carry this welcome into the next age. | anachronistic_gpt-oss:20b | 0.000 | 0.692 |

**Brier Score:** 0.2875


## Question 33

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John speaks to Nan and others about leaving Inishrath and their plans. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Wantin to run off to your uncle, indeed! Yes, thats what he was after, Nan. | ground_truth | 1.000 | 0.104 |
| Heres luck, Mr. Frank, an may heaven be your home. | same_character | 0.000 | 0.052 |
| Yes, so you are. And you never feel lonely? | same_book | 0.000 | 0.165 |
| Nan, we be settin’ to leave Inishrath, the seas whisperin’, and theres a job for a big, sturdy hand like mine; though I say I want work, I know I dont love it. If we go, we must bring the whole clan or theyll be stuck in the same old ways. | anachronistic_gpt-oss:20b | 0.000 | 0.679 |

**Brier Score:** 0.3233


## Question 34

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat.", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared", "the yellow face of Sarah Butler", "Her eyes shifted quickly here and there; presently fixed themselves on Frank's face.", "a pitiable figure she made there in that cosy room, her shoulders drooping, her withered face turned to the fire, her battered hands spread on her knees.", "Sarah's face softened; a smile crept along her lips.", "An angry flush was on her face, an ugly glitter in her eye.", "Her face was fiendish"

At one moment in the book, John, Nan, Sarah, and Frank gather to discuss Ould Hugh's interview, with Sarah questioning him. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| So thats what he came for? | ground_truth | 1.000 | 0.170 |
| Well, its a curious world, a mighty curious world. INISHRATH. | same_character | 0.000 | 0.030 |
| Tell me, Nan. Have you seen Mr. Ted Ross since a few nights ago? | same_book | 0.000 | 0.057 |
| Frank, did Ould Hughs words come from the heart, or was he merely polishing his own image for the crowd? Tell me, is there truth in his promises, or is he just another man of empty words? I doubt you can trust him. | anachronistic_gpt-oss:20b | 0.000 | 0.743 |

**Brier Score:** 0.3113


## Question 35

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

At one moment in the book, Marian confronts Frank over his harsh remarks, pleading for forgiveness and expressing her frustration. Write a short passage of dialogue (1-3 sentences) that Marian might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| No, Frank, I have no wish to say even that. I have no desire to say anything. What have I done that you should say such things to me? | ground_truth | 1.000 | 0.470 |
| And Nancy? You never met or heard of a girl like that? | same_character | 0.000 | 0.039 |
| I can't think how you came by such a notion, Marian, | same_book | 0.000 | 0.076 |
| Frank, your words cut deeper than any blade, and yet I cannot bear to let your harshness tarnish the love we share. I beg you, forgive this hurt, for I have no desire to dwell in bitterness. Let us mend this rift with understanding, not with further disdain. | anachronistic_gpt-oss:20b | 0.000 | 0.416 |

**Brier Score:** 0.1152


## Question 36

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat.", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared", "the yellow face of Sarah Butler", "Her eyes shifted quickly here and there; presently fixed themselves on Frank's face.", "a pitiable figure she made there in that cosy room, her shoulders drooping, her withered face turned to the fire, her battered hands spread on her knees.", "Sarah's face softened; a smile crept along her lips.", "An angry flush was on her face, an ugly glitter in her eye.", "Her face was fiendish"

At one moment in the book, Sarah invites Frank into her place and offers to show him something. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Come in, now, come, Ive something to show ye. | ground_truth | 1.000 | 0.166 |
| Good-evenin, Mr. Barry, I hope Im seein ye well? | same_character | 0.000 | 0.010 |
| Nan, Nan, Nan. Why, what a chance, what a lucky chance! Think of our meeting like this. | same_book | 0.000 | 0.385 |
| Come in, Frank, and let me show you the hidden study where the family secrets whisper in the dark. Its the only place in this house where the past truly speaks. | anachronistic_gpt-oss:20b | 0.000 | 0.438 |

**Brier Score:** 0.2589


## Question 37

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank Barry visits Mrs. Butler, exchanges pleasantries, promises to see John again, and departs. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Its getting late, Mrs. Butler. I must be off, I fear. | ground_truth | 1.000 | 0.549 |
| I hope my letter was of use to John. He got it, of course? | same_character | 0.000 | 0.021 |
| Tell me, Mr. Barry, is it married youll be ? | same_book | 0.000 | 0.010 |
| Good evening, Mrs. Butler, I trust the house is in good order. Ill be sure to see John again before I depart, if youll allow. Farewell, till we meet again. | anachronistic_gpt-oss:20b | 0.000 | 0.419 |

**Brier Score:** 0.0949


## Question 38

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat.", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared", "the yellow face of Sarah Butler", "Her eyes shifted quickly here and there; presently fixed themselves on Frank's face.", "a pitiable figure she made there in that cosy room, her shoulders drooping, her withered face turned to the fire, her battered hands spread on her knees.", "Sarah's face softened; a smile crept along her lips.", "An angry flush was on her face, an ugly glitter in her eye.", "Her face was fiendish"

At one moment in the book, Frank Barry meets Sarah Butler in his home, and they converse about the weather and their past. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Good-evenin, Mr. Barry, I hope Im seein ye well? | ground_truth | 1.000 | 0.048 |
| Well, its a curious world, a mighty curious world. INISHRATH. | same_character | 0.000 | 0.020 |
| Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it. | same_book | 0.000 | 0.324 |
| The rains been drumming on the roof like a bad memory, Frank, and it reminds me of the days when we were both young and foolish. I still recall the first time we met on that muddy lane, the wind carrying the scent of your fathers old boots. | anachronistic_gpt-oss:20b | 0.000 | 0.608 |

**Brier Score:** 0.3455


## Question 39

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank visits his uncle Hugh, they discuss supper and recent events. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Hello, uncle, I didnt expect to find you up so late. | ground_truth | 1.000 | 0.555 |
| I think, uncle, that you are a little hard on John Butler. I can't quite agree with you. He has faults; but I find him a very interesting and not unworthy man. | same_character | 0.000 | 0.302 |
| Whats your own private opinion of John as a spouter. | same_book | 0.000 | 0.009 |
| Ah, Hugh, the stews been simmering all day, and the lads are keen to hear of the rivers swell. If you fancy a bit more salt, Ill fetch the herring from the dock—its the only thing that keeps the wind from cutting straight through. | anachronistic_gpt-oss:20b | 0.000 | 0.134 |

**Brier Score:** 0.0769


## Question 40

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Frank and Nan debate Frank's admiration for Ted, leading to an apology and a mutual decision to leave. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| He deserves the very best the world can give him. Theres not his like in all London. Your pity! | ground_truth | 1.000 | 0.041 |
| Twas a fine piece o romancin | same_character | 0.000 | 0.010 |
| I swear to Heaven that if youd said the word that night I would have stayed. You remember what I said? I put myself in your hands. | same_book | 0.000 | 0.116 |
| I cannot abide your admiration for Ted, Frank, and I am sorry if my words have hurt you. Let us leave this place together and find a new start. | anachronistic_gpt-oss:20b | 0.000 | 0.833 |

**Brier Score:** 0.4069


## Question 41

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John passionately debates Ireland with Frank, Nan, and Ted while they listen. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Who would save Ireland, sir? Would England, sir? Would politicians, sir? | ground_truth | 1.000 | 0.223 |
| You'd be thinkin a power, Frank, o' the poetry o' Pope, I'm thinkin? | same_character | 0.000 | 0.077 |
| Well, I'm for there too, if you don't mind taking me. | same_book | 0.000 | 0.133 |
| Listen, ye lads, Irelands not a dream but a fight, a breath that must be kept in our throats! We can't let the English take our soil and our hearts, we must stand up and make them hear the roar of the green! If we don't, the next generation will be born with no tongue to speak of the Emerald. | anachronistic_gpt-oss:20b | 0.000 | 0.568 |

**Brier Score:** 0.2375


## Question 42

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

At one moment in the book, Frank receives a letter from Marian thanking him for money and reporting on the boy. Write a short passage of dialogue (1-3 sentences) that Marian might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Thank you for the money. I am most careful, and am keeping a strict account. Yes; it is quite sufficient. | ground_truth | 1.000 | 0.084 |
| Shall I? Am I right, little Frank? Shall I? | same_character | 0.000 | 0.048 |
| Good-night, everybody; and my love to all who want it. | same_book | 0.000 | 0.030 |
| Thank you, Frank, for your generous aid; the boy is thriving under your kindness. I pray he will find his path and grow into a man of honor. | anachronistic_gpt-oss:20b | 0.000 | 0.838 |

**Brier Score:** 0.3859


## Question 43

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted and Nan visit Barry to thank him, and Ted remarks that they have finally reached an understanding. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Aw, yes, weve come to an understandin at last. | ground_truth | 1.000 | 0.173 |
| Why didnt I choke ye that night on the quay? | same_character | 0.000 | 0.044 |
| Its this, its about yourself. What ails ye? I dont like to see ye. | same_book | 0.000 | 0.044 |
| Barry, we’ve finally reached an understanding, and I thank you for your help. Let’s keep this partnership strong. | anachronistic_gpt-oss:20b | 0.000 | 0.740 |

**Brier Score:** 0.3087


## Question 44

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, On a pier, Ted, Nan, and Frank clash over Nan's basket and Ted's conduct, leading to a heated argument. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Ill allow ye. By God, Ill allow ye! Come out. | ground_truth | 1.000 | 0.047 |
| Why didnt I choke ye that night on the quay? | same_character | 0.000 | 0.026 |
| Two whole hundred pounds! Yes; two whole hundred. It was a God-send. | same_book | 0.000 | 0.104 |
| Nan, you can’t just snatch that basket and expect me to take it lying down! Frank, if you think I’m weak, you’ll find I’m as strong as the tide. | anachronistic_gpt-oss:20b | 0.000 | 0.823 |

**Brier Score:** 0.3989


## Question 45

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank laments his situation, says goodbye, and prepares to leave. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Let me go; let me go. Im a fool. No one cares for me now. | ground_truth | 1.000 | 0.209 |
| I dont, not a jot. Three days or three years; its much the same. Stay, my dear, as long as ever you like. | same_character | 0.000 | 0.139 |
| Thank you for the money. I am most careful, and am keeping a strict account. Yes; it is quite sufficient. | same_book | 0.000 | 0.058 |
| Ive trod this road till my bones ached, and still the road calls. Farewell, lads, Ill be on my way, Bible in hand, and the wind at my back. May the Lord watch over you while I stride toward the next horizon. | anachronistic_gpt-oss:20b | 0.000 | 0.593 |

**Brier Score:** 0.2499


## Question 46

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, The narrator meets Nan, who questions him about his recent behavior and why he left Camberwell. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Its this, its about yourself. What ails ye? I dont like to see ye. | ground_truth | 1.000 | 0.081 |
| Itll be fine weather, Mr. Barry? | same_character | 0.000 | 0.020 |
| Aw, yes, weve come to an understandin at last. | same_book | 0.000 | 0.046 |
| Your silence is as strange as a winter wind. What made you abandon the warmth of Camberwell? | anachronistic_gpt-oss:20b | 0.000 | 0.853 |

**Brier Score:** 0.3939


## Question 47

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

Write a short passage of dialogue (1-3 sentences) that we might expect from Marian:

**Category:** character_modeling_without_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I dont believe you. I believe you are as false now as you have always been. Your weakness and thoughtlessness, your talk of pity and help! | ground_truth | 1.000 | 0.095 |
| Its no use, Marian, I cant lie to you. But listen, dear. | same_book | 0.000 | 0.133 |
| I never deceived you. I swear, Marian, I never did. | same_book | 0.000 | 0.081 |
| I cannot abide the thought that you would ever consider abandoning our covenant, for such a betrayal would stain even the purest of hearts. Love is not a game to be played with the hearts of others; it is a sacred trust that must be honored. | anachronistic_gpt-oss:20b | 0.000 | 0.690 |

**Brier Score:** 0.3296


## Question 48

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Nan goes to the pier, meets old Hugh Barry, and they discuss the weather and travel plans. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Itll be fine weather, Mr. Barry? | ground_truth | 1.000 | 0.177 |
| Im as usual. Im well enough. Theres not a turf in the house, but whats on the fire. | same_character | 0.000 | 0.210 |
| Good evenin to ye, Mrs. Butler | same_book | 0.000 | 0.020 |
| The winds a fickle friend these days, but the seas clear enough for the journey ahead. If we set sail by dawn, the tide will carry us safely past the cliffs. | anachronistic_gpt-oss:20b | 0.000 | 0.593 |

**Brier Score:** 0.2681


## Question 49

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Marian returns home to find her parents and friends, and Dad engages in a casual conversation with Frank about general opinions. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Well, Frank, my boy, whats your opinion, now, of things in general? | ground_truth | 1.000 | 0.370 |
| Yes, its magnificent. You know, Mr. Lindsay, one of the greatest regrets I have is that I cant find leisure to peruse my books. Quite a lot of them I have-havent I, Frank? | same_character | 0.000 | 0.179 |
| And Nancy? You never met or heard of a girl like that? | same_book | 0.000 | 0.066 |
| Frank, the seasons are a reminder that patience pays off; a well‑tended garden yields more than we expect. We must not let the weeds of uncertainty choke our ambitions. As long as we keep our hands steady, the fruit of our labor will flourish. | anachronistic_gpt-oss:20b | 0.000 | 0.385 |

**Brier Score:** 0.1455


## Question 50

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John talks to Mr. Barry at the table, discussing plans and the state of affairs. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Now, Mr. Barry, now Ill do till supper time. Faith, an bad manners to me keepin ye there this long. But youll know, sacks an stomachs were made to be filled. | ground_truth | 1.000 | 0.189 |
| John Butler, youre unjust; youre deluded. Heavenly hour, man, whats come over ye? What, in Gods name, have I done to you, John Butler? | same_character | 0.000 | 0.140 |
| Good evenin to ye, Mrs. Butler | same_book | 0.000 | 0.055 |
| The plans sound, but the coffers are thinner than a rivers bank, so we might have to stretch our pockets. Well keep our heads down and hope the wind shifts, then we can take the chance. | anachronistic_gpt-oss:20b | 0.000 | 0.616 |

**Brier Score:** 0.2649


## Question 51

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

Write a short passage of dialogue (1-3 sentences) that we might expect from John Butler:

**Category:** character_modeling_without_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Ay, ay. Love an blarney, love that makes the world go round, an blarney that keeps it goin. Ay, ay. | ground_truth | 1.000 | 0.449 |
| I dont hear Mr. Ross coming, I wish hed come. | same_book | 0.000 | 0.050 |
| Well, Im for there too, if you dont mind taking me. | same_book | 0.000 | 0.148 |
| Sure, Ill go to the mill, but I tell ye, the lads are all a bit too rough for me, though I say Im up for it. | anachronistic_gpt-oss:20b | 0.000 | 0.352 |

**Brier Score:** 0.1129


## Question 52

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Dad laments his lack of leisure to read and explains his busy schedule to those around him. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Yes, its magnificent. You know, Mr. Lindsay, one of the greatest regrets I have is that I cant find leisure to peruse my books. Quite a lot of them I have-havent I, Frank? | ground_truth | 1.000 | 0.314 |
| Tell me, Mr. Barry, is it married youll be ? | same_character | 0.000 | 0.036 |
| Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it. | same_book | 0.000 | 0.267 |
| I find myself tending every leaf and stone before dawn, my hands never idle, and the books sit untouched in the attic. The garden demands my every breath, and leisure is a luxury I cannot afford. My schedule is so full that even a quiet hour would be lost to the soil. | anachronistic_gpt-oss:20b | 0.000 | 0.383 |

**Brier Score:** 0.1727


## Question 53

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to win back Marian's trust and love in a tense conversation. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Yes, its that, Marian? Well, and I have come to tell you to help you get it back. Listen to me, Marian. | ground_truth | 1.000 | 0.088 |
| Listen, Marian. Ive something to say to you, and I must say it. Ive come to bring you back. | same_character | 0.000 | 0.270 |
| I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this! | same_book | 0.000 | 0.064 |
| Marian, I have carried this weight alone, but my heart still beats for you. Let me show you that my love is true. | anachronistic_gpt-oss:20b | 0.000 | 0.579 |

**Brier Score:** 0.3111


## Question 54

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John and Frank debate the nature of poetry while the family listens. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Youd be thinkin a power, Frank, o the poetry o Pope, Im thinkin? | ground_truth | 1.000 | 0.020 |
| John Butler, youre unjust; youre deluded. Heavenly hour, man, whats come over ye? What, in Gods name, have I done to you, John Butler? | same_character | 0.000 | 0.043 |
| I dont hear Mr. Ross coming, I wish hed come. | same_book | 0.000 | 0.031 |
| Now listen, Frank, poetrys like a good stew—its all about the mix of ingredients, not the fancy garnish. If you cant taste the truth in it, then youre just staring at a pot of water. | anachronistic_gpt-oss:20b | 0.000 | 0.906 |

**Brier Score:** 0.4458


## Question 55

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank bids farewell to his uncle Hugh, thanking him and expressing his reluctance to leave. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Good-bye, uncle Hugh. And thank you-thank you for all your kindness. | ground_truth | 1.000 | 0.208 |
| Pull, James, or well be late. Pull, James, for Gods sake! Nothing, James; nothing. | same_character | 0.000 | 0.030 |
| Why didnt I choke ye that night on the quay? | same_book | 0.000 | 0.029 |
| Uncle Hugh, I thank you for the warmth of your hearth and the kindness of your counsel, though my heart aches at the thought of parting. I shall return to your side as soon as my journeys burdens are lifted. | anachronistic_gpt-oss:20b | 0.000 | 0.733 |

**Brier Score:** 0.2914


## Question 56

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank and Ted have a tense conversation about their past encounters while walking down the road. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It isnt the first time, Mr. Ross, weve met in London, I believe? | ground_truth | 1.000 | 0.211 |
| Good-evening, Mr. Ross. Good-evenin. Could I have just a word with you, Mr. Ross? | same_character | 0.000 | 0.132 |
| Twas a fine piece o romancin | same_book | 0.000 | 0.008 |
| I dont know why you keep dragging me back to those old quarrels, Ted; the road we walked then is already worn, and I wont let it be worn again by your stubbornness. If you think you can change the past, you are mistaken, for the Bible in my hand tells me that the past is fixed, and the future is yours to bear alone. | anachronistic_gpt-oss:20b | 0.000 | 0.650 |

**Brier Score:** 0.2655


## Question 57

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to speak with Marian, but she remains silent, leaving him frustrated. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Listen, Marian. Ive something to say to you, and I must say it. Ive come to bring you back. | ground_truth | 1.000 | 0.304 |
| Have I been talking too much about myself? Youre sorry for me, Rab? Is that it, my son? | same_character | 0.000 | 0.142 |
| I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this! | same_book | 0.000 | 0.182 |
| Marian, your silence is a weight upon me; I cannot keep waiting for a word that never comes. Tell me what is troubling you, or Ill have to speak for myself. | anachronistic_gpt-oss:20b | 0.000 | 0.371 |

**Brier Score:** 0.1689


## Question 58

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is De Vaucourt, who is described this way in the book:
"handsome, lithe and agile as a panther, the best swordsman in Europe, with the blood of twenty knightly ancestors coursing through his veins"

At one moment in the book, De Vaucourt interrogates a grocer about his capacity to muster troops, and the grocer explains how quickly he can mobilize a large battalion. Write a short passage of dialogue (1-3 sentences) that De Vaucourt might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| And your muster? How do you collect your men, Captain, and what number could you bring into the field—pardon, I ought to say, into the streets, with six hours' notice? All armed? | ground_truth | 1.000 | 0.311 |
| your men, Captain, are they supplied with muskets? Are they used to handle their arms? | same_character | 0.000 | 0.220 |
| Can we vex the heart we love? Shall its mate forsake the dove? Precious tears for us to flow, Ours the hand to deal the blow! No-no! No-no! | same_book | 0.000 | 0.051 |
| You claim to rally a battalion in a fortnight; tell me, does your stock hold enough for their sustenance, or will you feed them from your own coffers? Your reputation precedes you. | anachronistic_gpt-oss:20b | 0.000 | 0.419 |

**Brier Score:** 0.1754


## Question 59

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Coupe-tête, who is described this way in the book:
"This is a well-made active young fellow, dressed like a respectable tradesman, wearing his brown hair unpowdered and in a club. He has keen, grey eyes, a ROSINE. pale complexion, and a large mouth with strong white teeth."

At one moment in the book, Coupe‑tête confronts the others, insisting they decide between life and death while Count Arnold is present. Write a short passage of dialogue (1-3 sentences) that Coupe-tête might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I will not argue the point with you. You must make your own choice. It is quite simple—life or death! | ground_truth | 1.000 | 0.341 |
| Walk on with us for a quarter of a league. Take the first bypath to the right, and hurry home. | same_character | 0.000 | 0.221 |
| Look! Fix thine eyes on it, my son, and repent, that I may give thee absolution. In another minute it will be too late! | same_book | 0.000 | 0.151 |
| We stand at the brink: live or die. Choose now, before Count Arnold's patience wanes, or we all perish today. | anachronistic_gpt-oss:20b | 0.000 | 0.287 |

**Brier Score:** 0.1471


## Question 60

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is The Queen, who is described this way in the book:
"her natural good sense and keen perceptions had picked up a few lessons in statecraft from her mother and her mother's advisers, showed an instinctive prescience of danger; but she was too unselfish to alarm others by acknowledgment of her own anxiety, and too loyal overtly, at any time, to differ in opinion with the King.", "The Queen, who had only rested by snatches, looked very pale and tired, but full of courage, and perfectly composed."

At one moment in the book, The Queen awakens, asks Rosine if she heard a noise and reassures her it was only a dream. Write a short passage of dialogue (1-3 sentences) that The Queen might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Did you not hear it? It is quiet now, but it was loud enough a moment back. Do not look so scared, child; it is nothing. | ground_truth | 1.000 | 0.187 |
| Wear it, my dear, for my sake-to remind you of Marie Antoinette! | same_character | 0.000 | 0.083 |
| Walk on with us for a quarter of a league. Take the first bypath to the right, and hurry home. I have still influence enough to screen your flight. | same_book | 0.000 | 0.114 |
| Did you hear a sound, dear Rosine? It was merely a dream, a fleeting shadow of the night. Rest now, the morn will bring calm. | anachronistic_gpt-oss:20b | 0.000 | 0.616 |

**Brier Score:** 0.2652


## Question 61

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Count Arnold de Montarbas, who is described this way in the book:
"Witness Count Arnold de Montarbas, as he slings home from shooting, through the snow, with easy gesture and jaunty step, the bloom of a handsome woman on his cheek, the glance of a bad one in his mirthful, meaning eyes. Five-and-twenty years old, with a patent of nobility that dates from the Crusades, conferring a right to intrude in his sovereign's bedroom and present the shivering King of France with a clean shirt, it is natural that he should be overwhelmed with debt, a bad landlord, an unlucky gamester, a faithless lover, a dishonest politician, and an uncertain friend. He has not much to boast of; yet does he pride himself with some reason on the good looks, good digestion, good spirits, and good manners that, in a world like his, give him the reputation of a good heart.", "Yes, he was handsome, there could be no question."

At one moment in the book, At Versailles, Montarbas remarks on the fickle nature of court favor and declares his intention to return to Paris while others debate the value of remaining at court. Write a short passage of dialogue (1-3 sentences) that Count Arnold de Montarbas might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Court favour is like sunshine, it cannot penetrate if you run into the shade. I shall walk through, make my bow, observe how many tiers have been added to the Queen's head-dress in my absence, and while you, Marquis, are standing uncovered in the cold, I shall be back at Paris. | ground_truth | 1.000 | 0.188 |
| I make you my compliments then, you cannot silence a battery with your rapiers, and, when the king and queen have spent your money, how are you to keep a hundred men together in the field? | same_character | 0.000 | 0.104 |
| At least, Father Ignatius, you are an open and hono able foe, There is o point, however, on which we are agreed, as regards o mutual friends here. Let us save them from ruin, a misery, and disgrace. We are not so bad, you see, revolutionists. | same_book | 0.000 | 0.071 |
| Courts are like snowstorms—one moment you’re warm, the next you’re left to freeze. I will return to Paris, where the winds of favor are less capricious. Stay here, if you wish, but I cannot linger in this fickle palace; the gilded halls grow stale, and the courtiers' whispers fade into empty echoes. | anachronistic_gpt-oss:20b | 0.000 | 0.636 |

**Brier Score:** 0.2698


## Question 62

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Pierre Legros, who is described this way in the book:
"raising his head and squaring his broad shoulders.", "Pierre Legros, who, straining to the utmost his personal advantages of height and strength, stood like a tower of defence in front of Rosine, to shield her from the throng."

At one moment in the book, Pierre tells Léonie about his love for Rosine and his plan to protect her by bringing her to Paris and securing a future together. Write a short passage of dialogue (1-3 sentences) that Pierre Legros might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| That is why I brought her to Paris, in order to lose ourselves in the crowd of this great capital. That is why I took an apartment for herself and her grandmother, here in this very street, near you and Coupe‑tête, who are our only friends, and lodged myself where I can see her, and watch over her day by day. I am strong. | ground_truth | 1.000 | 0.141 |
| But we shall starve, Rosine and I! | same_character | 0.000 | 0.107 |
| It is for you to dispose of me henceforth, Mademoiselle. You have saved me from death, and by all rules of warfare I belong to you, body and bones. | same_book | 0.000 | 0.175 |
| Leonie, I cannot deny the fire that burns within me for Rosine; she is the light that steadies my heart. I will escort her to Paris, where I shall shield her from all peril and secure a future worthy of her grace. Together, we will build a life that honors her spirit and our shared destiny everlasting. I promise to guard her against every threat that may arise. | anachronistic_gpt-oss:20b | 0.000 | 0.577 |

**Brier Score:** 0.2780


## Question 63

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Count Arnold de Montarbas, who is described this way in the book:
"Witness Count Arnold de Montarbas, as he slings home from shooting, through the snow, with easy gesture and jaunty step, the bloom of a handsome woman on his cheek, the glance of a bad one in his mirthful, meaning eyes. Five-and-twenty years old, with a patent of nobility that dates from the Crusades, conferring a right to intrude in his sovereign's bedroom and present the shivering King of France with a clean shirt, it is natural that he should be overwhelmed with debt, a bad landlord, an unlucky gamester, a faithless lover, a dishonest politician, and an uncertain friend. He has not much to boast of; yet does he pride himself with some reason on the good looks, good digestion, good spirits, and good manners that, in a world like his, give him the reputation of a good heart.", "Yes, he was handsome, there could be no question."

Write a short passage of dialogue (1-3 sentences) that we might expect from Count Arnold de Montarbas:

**Category:** character_modeling_without_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Pardon, mademoiselle! Permit me to offer my assistance; there-take my hand in yours; don't be afraid of hurting me, I can bear a good deal of squeezing without crying out. Excuse me if I embrace you too tightly: from such a situation one is only extricated by main force. | ground_truth | 1.000 | 0.349 |
| Never, or I am sure I should not have forgotten him. But why? | same_book | 0.000 | 0.212 |
| Content yourself, grandmother, I had an escort. | same_book | 0.000 | 0.035 |
| I am but a humble noble, debts as my companions, yet my charm is the only coin I truly hold. The King of France may shiver, but I bring him clean shirts and a laugh. My heart is good, my reputation, a fine tapestry of mischief in bright night. | anachronistic_gpt-oss:20b | 0.000 | 0.404 |

**Brier Score:** 0.1583


## Question 64

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is The Queen, who is described this way in the book:
"her natural good sense and keen perceptions had picked up a few lessons in statecraft from her mother and her mother's advisers, showed an instinctive prescience of danger; but she was too unselfish to alarm others by acknowledgment of her own anxiety, and too loyal overtly, at any time, to differ in opinion with the King.", "The Queen, who had only rested by snatches, looked very pale and tired, but full of courage, and perfectly composed."

At one moment in the book, The Queen passionately urges her husband to unite and govern prudently amid political and gambling concerns. Write a short passage of dialogue (1-3 sentences) that The Queen might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| My own, my king, my husband! we will stand or fall together-hand to hand, heart to heart. We are not to be separated, you and I, in life or death. | ground_truth | 1.000 | 0.207 |
| And well she may be. For weeks you have presumed on her smiles and abused her favours. She is a goddess, Monsieur; but she is also a woman. | same_character | 0.000 | 0.102 |
| I am determined to rule by love, Madame. I could not bear to think I was obeyed from the detestable influence of fear. | same_book | 0.000 | 0.131 |
| Let us bind our hearts and our realm together, my king, lest the fickle winds of politics and the lure of gamble tear our realm apart; govern with prudence, and we shall prevail. | anachronistic_gpt-oss:20b | 0.000 | 0.561 |

**Brier Score:** 0.2427


## Question 65

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Miss Annabel, who is described this way in the book:
"Annabel was five years my senior, and had mothered me ever since my mother's death when I was a boy. She was one of that by no means inconsiderable number of women who constantly say they desire and think they desire one thing, while they are actually wishing and working for the exact opposite. She hustled her off as she hustled off the peacocks when they came into the flower-garden.", "Annabel was looking particularly well that morning. She was always rather handsome, in a stately, sandyhaired, Queen Elizabethan sort of way; but our trip to Madeira had revived and refreshed her, and had elevated her always excellent health to a still higher degree of excellence.", "she had inherited my father's fair hair and ruddy complexion", "in spite of the fairness of her complexion, she was not of the blushing order.", "unquenchable thirst for information", "Annabel looked doubtful", "Annabel's restraining presence"

At one moment in the book, Annabel and her companions discuss Reggie's age while Fay and Frank interject. Write a short passage of dialogue (1-3 sentences) that Miss Annabel might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Reggie is not old and he is not young. I never can understand why people make such a fuss about their ages. I am forty‑eight and Reggie is forty‑three this year, and I make no bones about it. | ground_truth | 1.000 | 0.231 |
| I am terribly worried with one thing or another. | same_character | 0.000 | 0.010 |
| So I hear Mr. Wildacre is coming to live here now, the Manor will soon be as full of couples as Noah's Ark. | same_book | 0.000 | 0.040 |
| Reggie is not quite thirty yet, I think. But these boys seem to believe he is older, don't they? | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.719 |

**Brier Score:** 0.2775


## Question 66

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The narrator, Mr. Henderson, and Arthur debate faith, healing, and the limits of human explanation. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But how would you explain this working of His power? We are too fond of explaining things nowadays. And until we know how to use them we shall probably not get the wings. | ground_truth | 1.000 | 0.026 |
| No, I don't believe that Henderson can cure the boy; but I believe that Christ working through Henderson can do so, and I am going to see if He will. | same_character | 0.000 | 0.255 |
| The boy will live, Christ has healed him. | same_book | 0.000 | 0.081 |
| Arthur's eyes never left me as he said Faith heals where science fears to tread, Mr. Henderson. | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.638 |

**Brier Score:** 0.3568


## Question 67

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Miss Annabel, who is described this way in the book:
"Annabel was five years my senior, and had mothered me ever since my mother's death when I was a boy. She was one of that by no means inconsiderable number of women who constantly say they desire and think they desire one thing, while they are actually wishing and working for the exact opposite. She hustled her off as she hustled off the peacocks when they came into the flower-garden.", "Annabel was looking particularly well that morning. She was always rather handsome, in a stately, sandyhaired, Queen Elizabethan sort of way; but our trip to Madeira had revived and refreshed her, and had elevated her always excellent health to a still higher degree of excellence.", "she had inherited my father's fair hair and ruddy complexion", "in spite of the fairness of her complexion, she was not of the blushing order.", "unquenchable thirst for information", "Annabel looked doubtful", "Annabel's restraining presence"

At one moment in the book, Annabel expresses disappointment with Summerglade's contribution and declares they will receive no garments. Write a short passage of dialogue (1-3 sentences) that Miss Annabel might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I am very much disappointed in Summerglade's contribution-very much disappointed indeed. I consider it most shabby. As a matter of fact I don't think it is large enough to entitle them to a grant from the Guild at all. | ground_truth | 1.000 | 0.143 |
| I must add some more to them. Lady Westerham has sent me a lot of such beautiful scarlet flannel petticoats, Reggie, and I want to divide them equally amongst the poorest parishes. | same_character | 0.000 | 0.065 |
| St. Martin is another of the saints who are famous for manufacturing imitation summers, but I believe his little affair does not come off till November; so I think this must be St. Luke's after all, a bit before the time. | same_book | 0.000 | 0.039 |
| Summerglade i do believe you've missed the mark again my dear we shall not be receiving any garments from you this season | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.753 |

**Brier Score:** 0.3266


## Question 68

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Ponty, who is described this way in the book:
"Ponty's bright brown eyes twinkled.", "she could always wriggle with grace and dignity out of her own statements.", "Ponty was a martyr to rheumatism."

At one moment in the book, The narrator observes Ponty's change from hostility to care toward Frank Wildacre, and Ponty explains her earlier opposition and current sympathy. Write a short passage of dialogue (1-3 sentences) that Ponty might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Well, you see, Master Reggie, when I was that set against his coming to the Manor, he was strong and well, and so could stand up to me, as you might say: but now he is too weak and ill to hurt a fly. There's lots of folks as you can't stand at any price when they are able to stick up for themselves: but when they are knocked down you'd do anything you could to help them to get up again. | ground_truth | 1.000 | 0.160 |
| Vows or no vows, Miss Annabel will always wear the breeches. | same_character | 0.000 | 0.057 |
| Have you thought any more about Lady Chayford's suggestion, old man? Then don't you think you might do as-as-she suggests? for Fay's sake, | same_book | 0.000 | 0.035 |
| I admit it, Frank, I was matchmaking before my time. My rheumatism makes me grumpy; forgive an old lady's crankiness. | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.748 |

**Brier Score:** 0.3175


## Question 69

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Mr. Henderson, who is described this way in the book:
"tall, broad-shouldered, immaculately dressed Londoner, with the quiet manners and easy assurance of the typical man about town.", "Mr. Henderson looked at me intently for a moment with his piercing dark eyes."

At one moment in the book, The narrator recalls Mr. Henderson telling him he has a healing gift as he leaves the rectory. Write a short passage of dialogue (1-3 sentences) that Mr. Henderson might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I do not know, but I think you have the gift of healing | ground_truth | 1.000 | 0.250 |
| The boy will live, Christ has healed him. | same_character | 0.000 | 0.038 |
| You needn't blame yourself, Reggie, you really needn't. I wish to goodness I'd never mentioned that walk! | same_book | 0.000 | 0.017 |
| I believe my touch can bring comfort where there is pain, even if it is just a temporary relief. | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.695 |

**Brier Score:** 0.2617


## Question 70

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Ponty, who is described this way in the book:
"Ponty's bright brown eyes twinkled.", "she could always wriggle with grace and dignity out of her own statements.", "Ponty was a martyr to rheumatism."

At one moment in the book, The narrator and Ponty discuss smoking, Miss Annabel's influence, and the comfort of the house. Write a short passage of dialogue (1-3 sentences) that Ponty might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But smoking or no smoking, it's a fair treat to see you and Miss Annabel at home again, for when all's said and done the house don't seem like the house without you. For my part, I don't hold with so much gadding about. | ground_truth | 1.000 | 0.158 |
| I hear it is settled for Miss Annabel to go on living here after your marriage, Master Reggie | same_character | 0.000 | 0.046 |
| I don't see how we can do that, considering that it is too early for grapes, and we have no pomegranates. As a matter of fact, I don't believe pomegranates ever do grow in England. Do you know whether they do? | same_book | 0.000 | 0.183 |
| Ponty puffed on her cigarette, eyes twinkling. Miss Annabel would have a fit if she saw us enjoying ourselves like this. But these pipes are like little heating systems, keepin' rheumatism at bay. | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.612 |

**Brier Score:** 0.2798


## Question 71

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The characters debate jewelry, superstition, and sunlight, with Arthur explaining his views on wedding rings and fire. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| So it is for ordinary jewellery, but wedding-rings, I have always heard, are made of twenty-two carat. At least that is what is generally believed; but I cannot say whether it is more than a tradition, like the idea that the sun will put a fire out. | ground_truth | 1.000 | 0.129 |
| It isn't really as confusing as it sounds, as the boy is always called Frank, and the girl Fay. | same_character | 0.000 | 0.025 |
| I do not agree with you in that, thinking things are so, doesn't make them so. | same_book | 0.000 | 0.052 |
| Wedding rings are not mere trinkets but symbols of eternal vows, just as sunlight is nature's own sacred flame, free from superstition's shadows. | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.794 |

**Brier Score:** 0.3479


## Question 72

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The narrator and Arthur reminisce about Wildacre’s talent and death, with Blathwayte commenting on his passing. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Poor Wildacre had it in him to do great things, but he lost his chance. At least he did worse than lose it; he threw it away to the swine, and trampled it among the husks. | ground_truth | 1.000 | 0.198 |
| REGGIE, do you remember Wildacre? | same_character | 0.000 | 0.475 |
| And distant views, think what you miss in distant views. | same_book | 0.000 | 0.005 |
| Arthur sighs deeply I still miss him as if it was yesterday, his laughter would fill the halls like sunshine through winter clouds. | anachronistic_qwen2.5:7b-instruct | 0.000 | 0.322 |

**Brier Score:** 0.2434


## Question 73

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman meets with Miss Liebmann and discusses his mission. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I'm quite well. And you? I was instructed to communicate with you as soon as I had anything of importance to send over. | ground_truth | 1.000 | 0.111 |
| I am sorry sir but the fault is not mine. | same_character | 0.000 | 0.026 |
| Bob! Help us! | same_book | 0.000 | 0.000 |
| I've been briefed on the specifics, but I need you to confirm the exact location for our rendezvous. | anachronistic_mistral-small:24b | 0.000 | 0.862 |

**Brier Score:** 0.3835


## Question 74

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is brought into the room by a constable and discusses his actions with Lord Brooke. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I assure you, sir, that I acted from the best of motives. I am deeply grateful to you, sir, for your kindness, and I assure you I shall do my best to justify it. I am sure you will see that for the young woman to have been placed under arrest while in my rooms would have been a serious blow to her reputation. | ground_truth | 1.000 | 0.185 |
| To Rotterdam and Antwerp. Why? Herr Schwartz has sent for me. On the contrary, I am informed that he is delighted. I sent forward some news about a transport, last night— Yes. I rather think that I have been sent for to receive congratulations, and perhaps some new instructions. The existing arrangements were somewhat upset, by the action of the police, last night. | same_character | 0.000 | 0.108 |
| How could you ever have done such a foolish thing Pat? I don't think it was foolish. The woman might have been a spy. In fact, the man who came in just as I left seemed to be of the same opinion as I was. You left him there? Yes. And the seamstress as well?-Yes. She tried to go, but the fellow wouldn't let her. | same_book | 0.000 | 0.206 |
| Hoffman said, I must insist you understand, I'm here on behalf of my country, not as an enemy. If there are questions, I assure you, I'll answer them honestly. | anachronistic_mistral-small:24b | 0.000 | 0.501 |

**Brier Score:** 0.2425


## Question 75

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is arrested by the Governor after sharing crucial information about a British squadron. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Your excellency why should I be placed under arrest? I am trying to serve your interests. | ground_truth | 1.000 | 0.202 |
| I want to see the consul. | same_character | 0.000 | 0.143 |
| I would rather be cut to pieces with knives or thrown into boiling oil, than be a spy. | same_book | 0.000 | 0.358 |
| I didn't think I was helping you when I shared it. | anachronistic_mistral-small:24b | 0.000 | 0.297 |

**Brier Score:** 0.2183


## Question 76

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Patricia Burke, who is described this way in the book:
"Patricia was twenty-two, and considered a great beauty.", "Her eyes, glowing with a fine fire, were quite free from the tears that Hoffman had expected to see in them. Even the pallor of her face was relieved by the glow from the log fire, the amber tints from the silk-shaded lamp. Her hair, somewhat disarranged, her defiant carriage, her detached expression, reminded him vaguely of a picture he had once seen of Joan of Arc.", "a young woman of very decided likes and dislikes. Also, she had a kind heart."

At one moment in the book, Patricia encounters a young woman seeking employment and questions her about her identity. Write a short passage of dialogue (1-3 sentences) that Patricia Burke might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| What can I do for you my girl? What is your name? | ground_truth | 1.000 | 0.100 |
| I don't believe it for a moment. She looked far too poor and hungry. | same_character | 0.000 | 0.034 |
| What do you wish to say to me? | same_book | 0.000 | 0.068 |
| Who are you? And what brings you to my doorstep at such an hour? | anachronistic_mistral-small:24b | 0.000 | 0.797 |

**Brier Score:** 0.3627


## Question 77

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Patricia Burke, who is described this way in the book:
"Patricia was twenty-two, and considered a great beauty.", "Her eyes, glowing with a fine fire, were quite free from the tears that Hoffman had expected to see in them. Even the pallor of her face was relieved by the glow from the log fire, the amber tints from the silk-shaded lamp. Her hair, somewhat disarranged, her defiant carriage, her detached expression, reminded him vaguely of a picture he had once seen of Joan of Arc.", "a young woman of very decided likes and dislikes. Also, she had a kind heart."

At one moment in the book, Patricia confronts Hoffman and reveals her role as a representative of Herr Schwartz. Write a short passage of dialogue (1-3 sentences) that Patricia Burke might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| My friend, from now on, please understand that I represent Herr Schwartz, here in London. You have been suspicious of me, from the start, as indeed we have been of you. The time for all that is ended. | ground_truth | 1.000 | 0.172 |
| Alan and I were on our way to supper, said. We stopped, thinking you might like to join us. | same_character | 0.000 | 0.089 |
| I assure you, sir, that I acted from the best of motives. I am deeply grateful to you, sir, for your kindness, and I assure you I shall do my best to justify it. | same_book | 0.000 | 0.170 |
| I must admit, you're not the first person I've had to outmaneuver tonight. But know this: I'm here on behalf of Herr Schwartz and I expect your full cooperation | anachronistic_mistral-small:24b | 0.000 | 0.570 |

**Brier Score:** 0.2617


## Question 78

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon threatens to shoot his brother Stephanus, but is stopped when Stephanus approaches and intervenes. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Keep back-keep back- or I will shoot you dead and follow you to Hell over the krantz. | ground_truth | 1.000 | 0.035 |
| Your life is mine, here in this lawless land, to destroy by the mere slight pressure of my finger upon the trigger against which it rests. It is mine, -forfeit because you have pursued me when I tried my best to avoid you, and driven me to bay. I give it to you in exchange for the wrong I have done you. | same_character | 0.000 | 0.180 |
| Kanu,—will you do something for me? Anything that young mistress asks of me. Yes, that can easily be done. | same_book | 0.000 | 0.055 |
| You have betrayed us, Stephanus, and I will pull the trigger if you do not cease your treachery. I will not let you harm the rest of our people. | anachronistic_gpt-oss:20b | 0.000 | 0.731 |

**Brier Score:** 0.3754


## Question 79

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie informs Gideon that her mother is dying and urges him to go. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once. | ground_truth | 1.000 | 0.432 |
| Father, why are you so late-and where is your horse? | same_character | 0.000 | 0.023 |
| The wolf is in a trap; for ten long years he will have to bite the door before it opens. Aletta, are you taking the part of this wolf—the jackal in a mans skin, against me? | same_book | 0.000 | 0.019 |
| Gideon, your mother is dying. You must go now. | anachronistic_gpt-oss:20b | 0.000 | 0.526 |

**Brier Score:** 0.1501


## Question 80

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Jacomina, who is described this way in the book:
"Jacomina, his daughter, was a comely damsel of seventeen, whose keen and practical interest in her father's pursuits boded a terrible future for her prospective husband and family.", "resplendent in what passed, locally, for finery, sitting throned upon Uncle Diederick's wagon box", "Jacomina lifted a blushing face and gave him an instantaneous glance from her bright eyes-made brighter now by a suspicion of tears."

At one moment in the book, Uncle Diederick plans a trip and Jacomina expresses concern about loneliness during his absence. Write a short passage of dialogue (1-3 sentences) that Jacomina might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Pa, it will be very lonely here while you are away. | ground_truth | 1.000 | 0.479 |
| I am so unhappy because-because you used to like me so much, and now you never speak to me. | same_character | 0.000 | 0.050 |
| God laid this punishment upon me, and it is His will that I should bear it to the end. | same_book | 0.000 | 0.123 |
| Father, I fear the quiet of this house will turn to a hollow echo, and I shall find myself wandering in the shadows of your absence. I beg you, let me not be left to the solitude of my own thoughts. | anachronistic_gpt-oss:20b | 0.000 | 0.348 |

**Brier Score:** 0.1024


## Question 81

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Uncle Diederick, who is described this way in the book:
"Uncle Diederick had this peculiarity: if he announced his intention of doing any given thing on a given day, he stuck to his word; nothing short of absolute necessity would stop him."

At one moment in the book, Uncle Diederick talks to Jacomina about marriage and horses while they are in the chemist's shop. Write a short passage of dialogue (1-3 sentences) that Uncle Diederick might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Well, Jacomina, Ill have to see about getting a wife myself now. But you need not be afraid on account of Aunt Emerencia; no one, who is not a fool, buys an old mare when he can get a young one for the same price. | ground_truth | 1.000 | 0.269 |
| Well, schepsel, it is easy to see that you have been riding your masters horse. For how far has the Devil been chasing you? | same_character | 0.000 | 0.050 |
| I am so unhappy because-because you used to like me so much, and now you never speak to me. | same_book | 0.000 | 0.171 |
| I have decided to marry Miss van der Merwe on Thursday, and I shall purchase a fine mare for her, and I will have the horse treated with the medicine we just bought. | anachronistic_gpt-oss:20b | 0.000 | 0.509 |

**Brier Score:** 0.2063


## Question 82

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon and Aletta confront each other about Stephanus after the trial. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The wolf is in a trap; for ten long years he will have to bite the door before it opens. Aletta, are you taking the part of this wolf—the jackal in a mans skin, against me? | ground_truth | 1.000 | 0.080 |
| Stephanus shot me by accident-I accused him falsely because I hated him all my life. | same_character | 0.000 | 0.029 |
| Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once. | same_book | 0.000 | 0.508 |
| I cannot stand this, Aletta, that Stephanus should still cling to the lies he once whispered, and yet I feel no fire to fight him as I once did. My heart has grown heavy, and I am no longer the man who would have struck him down. | anachronistic_gpt-oss:20b | 0.000 | 0.382 |

**Brier Score:** 0.3129


## Question 83

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon confesses to Marta that Stephanus accidentally shot him and that he had wrongly accused him, while the dying woman lies in bed. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Stephanus shot me by accident-I accused him falsely because I hated him all my life. | ground_truth | 1.000 | 0.123 |
| You are nothing but a bastard jackal, yourself. You are very brave because you have my gun in your hand; put it down and I will take that dirty beard of yours to stuff my saddle with-if it would not give the horse a sore back. | same_character | 0.000 | 0.049 |
| Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once. | same_book | 0.000 | 0.537 |
| Marta, I must tell you the truth: Stephanus shot me, but it was an accident, and I have wrongly accused him. I cannot stand the shame while she lies in bed, her breath growing faint. Please forgive my mistake. | anachronistic_gpt-oss:20b | 0.000 | 0.292 |

**Brier Score:** 0.2859


## Question 84

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie awakens and calls out to Kanu while her friends soothe her. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Kanu, are you here? Oh God, the baboons. Kanu-Kanu. | ground_truth | 1.000 | 0.116 |
| My name is not Agatha, my name is Elsie, Elsie van der Walt. | same_character | 0.000 | 0.233 |
| God laid this punishment upon me, and it is His will that I should bear it to the end. | same_book | 0.000 | 0.385 |
| Kanu, my heart is aching for your touch, please hear me. The world feels still and I need your presence to guide me. | anachronistic_gpt-oss:20b | 0.000 | 0.266 |

**Brier Score:** 0.2637


## Question 85

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie informs Gideon that her father sent her to stay with him. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Uncle Gideon, my father sent me back to live with you until his release. | ground_truth | 1.000 | 0.167 |
| It is not your blood that he wants, Uncle Gideon. Do not go, Uncle Gideon, stay and meet him. | same_character | 0.000 | 0.081 |
| I know that my father will go to live at the old place as soon as we return, and it will be years and years before he will ever come to Cape Town again. No, Adrian, you had better forget me, and look out for some girl whose father will be able to bring her to Cape Town soon. I do not want you to be bound to one who may have to keep you waiting such a long, long time. | same_book | 0.000 | 0.195 |
| Gideon, my father has sent me to stay with you, hoping you will guide me. I trust you will help me find my way. | anachronistic_gpt-oss:20b | 0.000 | 0.557 |

**Brier Score:** 0.2619


## Question 86

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sister Katherine Bayssallance, who is described this way in the book:
"Sister Katherine Bayssallance was no nun, except that she was still, at forty-five or fifty, in a state of celibacy. She was plump of figure and rosy-cheeked, fonder of mirth than of tears, and of a cheerful piety. She was also voluble exceedingly."

At one moment in the book, Sister Katherine offers ginger wine to the narrator and Nevill while lamenting Sylvia’s absence and George’s misfortune. Write a short passage of dialogue (1-3 sentences) that Sister Katherine Bayssallance might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You will take a glass of my ginger, Nevill: you were always fond of a glass of good wine. The pity of it! The pity of it! | ground_truth | 1.000 | 0.251 |
| I found her yesterday morning, in the orchard, wandering slowly up and down. She would have run away; but it was too late, and she is too feeble to run. | same_character | 0.000 | 0.264 |
| I want to make them happy if I can, but I cannot. | same_book | 0.000 | 0.139 |
| Here a cup of ginger wine for you both, friends, and pray for sweet Sylvia, who is absent; and for poor George, whose misfortune weighs upon us. | anachronistic_gpt-oss:20b | 0.000 | 0.347 |

**Brier Score:** 0.1925


## Question 87

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sylvia, who is described this way in the book:
"who was sixteen and little more than a girl when George kissed her and said goodbye, was now nineteen, and a tall young woman.", "Her attitude was feeble and languishing; she was pale; her cheek was thin; her eyes were hollow.", "Sylvia herself is so inclined. She obeys the Rules of the Church: she attends the services on Sundays and Holy Days, she fasts in Lent and feasts at Easter, she reads devout books, as well as the Bible; she converses willingly on grave and religious subjects, and her life is wholly in conformity with her profession. She is virtuous, she is truthful, she is not given to slander, she is not envious, she is charitable: in a word, Sylvia is a young woman who leads the Christian life as ordered by the Church of England.", "Sylvia was always religiously disposed.", "She shook her pretty head."

At one moment in the book, Sylvia and the narrator leave the garden for a burial ground, where Sylvia laments her misery amid reflections on spring and death. Write a short passage of dialogue (1-3 sentences) that Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Let us leave the garden. Let us go into the burying-ground-here is spring, and that means love and hope. I have nothing more to do with spring. | ground_truth | 1.000 | 0.334 |
| Alas! what things have fallen upon me since last I stood here! | same_character | 0.000 | 0.081 |
| I found her yesterday morning, in the orchard, wandering slowly up and down. She would have run away; but it was too late, and she is too feeble to run. | same_book | 0.000 | 0.381 |
| Alas, though spring's blossoms stir the air, my heart feels the chill of loss; how swiftly the flowers fade, so too my hope, Lord, grant me grace. | anachronistic_gpt-oss:20b | 0.000 | 0.204 |

**Brier Score:** 0.1591


## Question 88

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Richard Archer, who is described this way in the book:
"He was of my age, man and boy he was always the same in temper-morose, harsh, and gloomy. He lived in the house assigned to him with his mother; he consorted with no one, he had no friends or associates.", "schoolmaster and organist of the Hospital, supposed to possess the meekness of his calling and to be a sweet musician, gentle as his Church music.", "Richard Archer, however, grew morose, and he became a solitary-he hated the world."

At one moment in the book, The narrator is introduced to a revolutionary club where Richard Archer welcomes him and outlines their plans to rise against the regime. Write a short passage of dialogue (1-3 sentences) that Richard Archer might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You are one of us now, I have long waited for your coming. You have been watched. Ha! | ground_truth | 1.000 | 0.116 |
| I had heard that you were returned in And safety. I offer my congratulations. | same_character | 0.000 | 0.009 |
| Young man, it is fifty years and more since I first heard discussions on these subjects which now interest you—and the whole world—so deeply. | same_book | 0.000 | 0.187 |
| Join us, and we shall strike at the heart of their tyranny, exposing the cruelty that lies beneath. | anachronistic_gpt-oss:20b | 0.000 | 0.687 |

**Brier Score:** 0.3221


## Question 89

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Marquis de Rosnay, who is described this way in the book:
"He was a beautiful old gentleman to look at, not tall but upright still, not yet bowed by his weight of years. His linen and lace were the whitest, his coat and waistcoat spotless, and his face always calm, noble, and dignified."

At one moment in the book, The narrator meets the Marquis de Rosnay, who reflects on Enlightenment ideas and their influence abroad, and inquires about his estates. Write a short passage of dialogue (1-3 sentences) that Marquis de Rosnay might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Young man, it is fifty years and more since I first heard discussions on these subjects which now interest you—and the whole world—so deeply. I have sat at tables where Voltaire, Diderot, D'Alembert, even your Bolingbroke, freely discussed the sovereignty of the people. I have lived to see these ideas put in practice across the ocean. | ground_truth | 1.000 | 0.508 |
| Almost, I could fancy myself in Paris. | same_character | 0.000 | 0.037 |
| You are one of us now, I have long waited for your coming. You have been watched. Ha! Let us have a little patience | same_book | 0.000 | 0.104 |
| Indeed, the light of reason has crossed oceans, shaping colonies as it has illuminated our salons, and I marvel at how Enlightenment ideals now guide governance abroad; yet I must inquire, how do my estates fare under the new administration, and what measures have been taken to preserve their prosperity for the benefit of future generations. | anachronistic_gpt-oss:20b | 0.000 | 0.352 |

**Brier Score:** 0.0946


## Question 90

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sylvia, who is described this way in the book:
"who was sixteen and little more than a girl when George kissed her and said goodbye, was now nineteen, and a tall young woman.", "Her attitude was feeble and languishing; she was pale; her cheek was thin; her eyes were hollow.", "Sylvia herself is so inclined. She obeys the Rules of the Church: she attends the services on Sundays and Holy Days, she fasts in Lent and feasts at Easter, she reads devout books, as well as the Bible; she converses willingly on grave and religious subjects, and her life is wholly in conformity with her profession. She is virtuous, she is truthful, she is not given to slander, she is not envious, she is charitable: in a word, Sylvia is a young woman who leads the Christian life as ordered by the Church of England.", "Sylvia was always religiously disposed.", "She shook her pretty head."

At one moment in the book, The narrator takes Sylvia out for a walk, where she laments the troubles that have befallen her. Write a short passage of dialogue (1-3 sentences) that Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Alas! what things have fallen upon me since last I stood here! | ground_truth | 1.000 | 0.140 |
| I will try to tell you, what has befallen me. | same_character | 0.000 | 0.520 |
| I found her yesterday morning, in the orchard, wandering slowly up and down. | same_book | 0.000 | 0.190 |
| Lord, my heart is heavy with sorrow; may Your grace lift burdens. | anachronistic_gpt-oss:20b | 0.000 | 0.149 |

**Brier Score:** 0.2672


## Question 91

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Banks, who is described this way in the book:
"Her voice sounded so shrill and unwinning, and the quotation that she so glibly uttered was such a jar."

At one moment in the book, Miss Banks urges Marion to help with exam papers and comments on the students' performance. Write a short passage of dialogue (1-3 sentences) that Miss Banks might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You haven't had a single examination class yet; then it is clearly your duty to help the afflicted. Bear ye one another's burdens, you know. I shall have enough examination papers of my own before night. | ground_truth | 1.000 | 0.237 |
| It reminds one of one's childhood and Scripture learning days: Many are called, but few are chosen. There will be exceedingly few chosen from this class. | same_character | 0.000 | 0.173 |
| I'm real sorry you hadn't a teacher to-day. I should have been glad to have taught, the lesson if I had known how; but you see how it is; I have all these things to learn. | same_book | 0.000 | 0.349 |
| Marion, I need you to sort these papers now; the children are floundering, their answers as scattered as a jar of broken glass. Exam dire; we must act swiftly and the marks will reflect our work. | anachronistic_gpt-oss:20b | 0.000 | 0.241 |

**Brier Score:** 0.1981


## Question 92

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion questions Eurie about his pre‑conversion view on dancing as part of a broader discussion on dancing among the girls. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Just let me ask you a question. Why did you think, before you were converted, that it was wrong for Christian people to dance? | ground_truth | 1.000 | 0.380 |
| You young ladies talk about being careful with whom you dance. Don't you accept the attentions of strange young gentlemen, who have been introduced to you by your fashionable friends? | same_character | 0.000 | 0.087 |
| I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. | same_book | 0.000 | 0.075 |
| Before your conversion, Eurie, how did you feel about dancing? Was it merely a pastime or something that stirred the soul? Share your thoughts. | anachronistic_gpt-oss:20b | 0.000 | 0.458 |

**Brier Score:** 0.1520


## Question 93

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

Write a short passage of dialogue (1-3 sentences) that we might expect from Marion Wilbur:

**Category:** character_modeling_without_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| That is one of the marked difficulties. Now I have heard people talk, who led you to infer that it was the easiest thing in life to mold these young teachers into the required shape and form; that you had only to sweetly suggest and advise and direct, and they sweetly succumbed. Now, don't their mothers know that young ladies naturally do no such thing? | ground_truth | 1.000 | 0.118 |
| Here we are, We have run the gauntlet of five calls and a concert, and I don't know how many other things in prospective, for the sake of getting to you. | same_book | 0.000 | 0.088 |
| I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. I used to think in my very heart that joining the church, and trying to do about right, was all there was of religion; but I have found that I was wonderfully mistaken. | same_book | 0.000 | 0.306 |
| Come on, little ones, let’s open these books and learn something new today. Remember, knowledge is the key that opens every door. | anachronistic_gpt-oss:20b | 0.000 | 0.488 |

**Brier Score:** 0.2792


## Question 94

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion asks Flossy to share the Bible verses she discovered during their study. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Sure enough, Little Flossy, where are your verses? You were going to give us whatever you found in the Bible. You were the best witness of all, because you brought such an unprejudiced determination to the search. | ground_truth | 1.000 | 0.302 |
| Precisely! It is considered unladylike, I believe, for people to talk about love and marriage. I never could see why; I'm sure neither of them is wicked. | same_character | 0.000 | 0.127 |
| I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. | same_book | 0.000 | 0.326 |
| Flossy, could you kindly share the verses you found in the study with love? I think the children will learn something wonderful from them today. Your bright mind always brings light to our little lessons everywhere today. | anachronistic_gpt-oss:20b | 0.000 | 0.244 |

**Brier Score:** 0.1672


## Question 95

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Ruth Erskine, who is described this way in the book:
"She was more than embarrassed; she was utterly dismayed and disheartened.", "Ruth Erskine was quiet and at rest, her face deathly pale, her eyes bright with a calm she had forced upon herself."

At one moment in the book, Ruth corrects Dr. Dennis about Young Mitchell and expresses her strong dislike for him. Write a short passage of dialogue (1-3 sentences) that Ruth Erskine might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| You are mistaken in supposing him to be a friend of mine. We have the most distant speaking acquaintance only, and I have a dislike for him amounting to absolute aversion. | ground_truth | 1.000 | 0.271 |
| I ought to have some tracts, they always take tracts when they go district visiting, I know that from hearing Mrs. Whipple talk, what is this but a district visiting, only Dr. Dennis has put my district all over the city, I wonder if he could have scattered the streets more if he had tried, respectable streets, though, all of them, better than any Mrs. Whipple ever told about. | same_character | 0.000 | 0.119 |
| Do I get out to church? That depends on whether I decide to go or not. May I ask why you are interested? | same_book | 0.000 | 0.150 |
| Dr. Dennis, I must correct you: Young Mitchell is not a man of honor. I cannot abide his deceitful ways; his presence chills me to the marrow. His heart is winter. | anachronistic_gpt-oss:20b | 0.000 | 0.460 |

**Brier Score:** 0.1951


## Question 96

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, Flossy expresses confusion about why Dr. Dennis would be interested in her card game. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I don't in the least understand what you are talking about. Of what interest could it have been to Dr. Dennis what I am doing; and why should he have delivered a lecture? | ground_truth | 1.000 | 0.100 |
| Col. Baker, don't you really know at all what arguments clergymen have against card-playing for amusement? | same_character | 0.000 | 0.103 |
| We seem to have started on the road together. We ought to shake hands, and wish each other a safe journey. | same_book | 0.000 | 0.084 |
| Dear Dr. Dennis, why would you care about my little card game? It seems so odd that you would want to know its rules. I thought it was a pastime for the girls. | anachronistic_gpt-oss:20b | 0.000 | 0.713 |

**Brier Score:** 0.3338


## Question 97

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion apologizes to Dr. Dennis for not having the names ready and explains she had time to copy them but didn't. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I haven't them ready, Dr. Dennis; I'm real sorry, and it's my fault, too. I had time to copy them, and I just didn't do it. | ground_truth | 1.000 | 0.645 |
| When I am rich and a woman of leisure, I will build a house that shall have pleasant rooms and good bread and butter, and I will board school-teachers and sewing-girls and clerks for a song. | same_character | 0.000 | 0.225 |
| The man would actually sell her, if by that means he could be recognized in business by our house. | same_book | 0.000 | 0.022 |
| I had the names in my hand, yet I left them unprinted for the time slipped by like a quiet wind, softly and carefully, my dear. | anachronistic_gpt-oss:20b | 0.000 | 0.109 |

**Brier Score:** 0.0473


## Question 98

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, Flossy discusses her church attendance with Col. Baker and vows to attend more regularly. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I have not been very often, it is true; but I intend to reform in that respect in the future. I mean to go whenever I can, and I mean to go always to the First Church. | ground_truth | 1.000 | 0.130 |
| Col. Baker, I can not ask you in this evening, because I have determined to receive no more calls, even from intimate friends, on the Sabbath. On any other evening I shall be happy to see you. | same_character | 0.000 | 0.314 |
| Oh, I am so glad; so glad! Oh, Miss Wilbur, I don't know how to be thankful enough! | same_book | 0.000 | 0.124 |
| I promise, dear Colonel, that I will attend church each Sunday, bringing my heart, my little notebook of prayers, and my sincere smile, for I feel the Lord's love growing within me, and I wish to share it. | anachronistic_gpt-oss:20b | 0.000 | 0.432 |

**Brier Score:** 0.2644


## Question 99

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Ruth Erskine, who is described this way in the book:
"She was more than embarrassed; she was utterly dismayed and disheartened.", "Ruth Erskine was quiet and at rest, her face deathly pale, her eyes bright with a calm she had forced upon herself."

At one moment in the book, Ruth confesses her guilt and vows to atone for her past mistakes while Marion listens. Write a short passage of dialogue (1-3 sentences) that Ruth Erskine might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| No, I didn’t mean to; and as to that, I never meant to do anything that was not just right in my life; but I meant to have just exactly my own way of doing things, and I tell you I took it. Now, Marion, while I blame myself as no other person ever can, I still blame others. I was never taught as I should have been about the sacredness of human loves, and the awfulness of human vows and pledges. | ground_truth | 1.000 | 0.191 |
| I don't understand it. I don't understand you; in what way do mean? I try to do my duty in every place that I can think of. I am not compromising on any subject, so far as I know. If I am, I will certainly be grateful to any one who will point it out to me. You are a strange comforter. Do you mean by that to intimate that you think I ought never to look or hope for rest of mind again because I have made one fearful mistake? | same_character | 0.000 | 0.188 |
| You didn't mean to do that! | same_book | 0.000 | 0.029 |
| I have carried this heavy secret for too long, and I cannot bear the weight of my own conscience any longer. I pledge to set things right, even if it means facing the consequences, and I ask for your forgiveness as I begin to walk toward redemption. With each step, I promise to mend the fractures I caused. | anachronistic_gpt-oss:20b | 0.000 | 0.593 |

**Brier Score:** 0.2608


## Question 100

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, During a heated debate about dancing in the Bible, Flossy expresses uncertainty and asks Ruth for clarification. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. I used to think in my very heart that joining the church, and trying to do about right, was all there was of religion; but I have found that I was wonderfully mistaken. | ground_truth | 1.000 | 0.224 |
| Why, you know, I actually promised to bring some one with me if I possibly could; so there was nothing for it but to try in every possible way up to the very last minute of the time I had. But, after all, I brought the one whom I had not the least idea of asking; he asked himself. | same_character | 0.000 | 0.168 |
| Just let me ask you a question. Why did you think, before you were converted, that it was wrong for Christian people to dance? | same_book | 0.000 | 0.245 |
| Ruth if I may I'm so uncertain about this verse—does it truly forbid dancing, or is it only certain types? I feel my heart quiver at the thought, but I wish to learn the truth, so I ask you kindly for guidance. I know my cheeks may blush, yet I trust your wisdom, dear Ruth, to help me understand if the Bible truly condemns dancing or merely cautions against frivolity for me. | anachronistic_gpt-oss:20b | 0.000 | 0.362 |

**Brier Score:** 0.2054


## Question 101

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The onion seed may be sown sparsely in drills in the seed-boxes as early as the first of February, and the young plants allowed to grow until about the first of May, when they may be transplanted out-doors. It is desirable to cut the tops off about one inch from the ground with a pair of scissors once or twice during this period of growth. [masked sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| This will cause a better development of root to take place and will lead to a thriftier, stockier plant. | ground_truth | 1.000 | 0.160 |
| This will hinder root development and result in a weaker, leggier plant. | negation | 0.000 | 0.087 |
| The purpose of putting these bulbs away in a dark, cool place is to enable them to develop such a growth of roots as would occur were the bulbs beneath the soil out-doors. | same_book | 0.000 | 0.155 |
| This will cause numerous side branches to be thrown up, and these will bear a profusion of blossoms throughout the later weeks of summer. | same_book | 0.000 | 0.143 |
| This practice helps to encourage the development of stronger bulbs that can be sold in organic grocery stores. | manual_anachronistic_metadataless_mistral-small:24b | 0.000 | 0.094 |
| This prevents the plant from flowering, which would divert energy from bulb development. | anachronistic_gpt-oss:20b | 0.000 | 0.362 |

**Brier Score:** 0.1496


## Question 102

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** In case the seeds should prove to have a low percentage of germination, it will be desirable, of course, to sow the seed more thickly, or very often it will be desirable to discard it altogether and substitute a better quality of seed. In case of a few plants, however, older seed is preferred. For example, when cucumber seed is ten years or more old,
only the strongest seeds, surest to produce plants true to the type preferred, still preserve good vitality; [masked clause describing an inference or effect]. Similarly, seed of double balsam gives a larger percentage of double flowers if aged until the weaker seed has lost power of germination.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so large growers of cucumbers prefer such seed where the percentage of germination is low | ground_truth | 1.000 | 0.194 |
| so large growers of cucumbers avoid such seed where the percentage of germination is inadequate | manual_negation | 0.000 | 0.073 |
| so the spikes have value as cut flowers | same_book | 0.000 | 0.003 |
| this results in plants that are more vigorous and likely to thrive | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.559 |
| the surviving seeds are those most vigorous and true to type. | anachronistic_gpt-oss:20b | 0.000 | 0.172 |

**Brier Score:** 0.1994


## Question 103

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** There is one precaution which nearly always needs to be taken in using sweet peas for indoor decorations. The blossoms are so beautiful that one is tempted to pick them indefinitely, and crowd them in a solid mass into the receptacle. [masked sentence describing a tension or contrast] We may well take a hint from this, and place them so loosely in our jars that each blossom will be in view.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But on the vines they are not so crowded; each one stands sufficiently alone to reveal its loveliness. | ground_truth | 1.000 | 0.098 |
| But on the vines they are densely packed; each one stands obscured among others, concealing its loveliness. | negation | 0.000 | 0.033 |
| But there should be the effect of unbroken lines which will combine rhythmically with the lines of leaf, stem, and blossom of the flowers held by the jar. | same_book | 0.000 | 0.095 |
| This is not noticeable, however, except when the blossoms are very close at hand, and it does not interfere in the least with their usefulness in the garden or in the home. | same_book | 0.000 | 0.339 |
| Yet their fragrance is so powerful that it can become overpowering when too many are confined to a small space. | anachronistic_mistral-small:24b | 0.000 | 0.353 |
| Yet the very urge to crowd them together can smother the individual grace each blossom deserves. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.082 |

**Brier Score:** 0.1784


## Question 104

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** IRIS BORDER GARDENS 

195 These iris plants are not expensive. One should be able to buy good clumps for setting out at from fifteen to twentyfive cents each. The German and Siberian Irises increase so rapidly that they should be divided and replanted every third or fourth year. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It is therefore easy for a school to obtain a good variety of colors of German Iris by means of clumps and divisions received as gifts from home gardens. | ground_truth | 1.000 | 0.063 |
| It is therefore difficult for a school to obtain a good variety of colors of German Iris without receiving clumps and divisions as gifts from home gardens. | negation | 0.000 | 0.043 |
| Consequently, if you supply these requirements to any seed, they should be able to start their growth and thus show you what percentage has sufficient vitality to germinate. | same_book | 0.000 | 0.027 |
| This frequent division not only maintains the health of the iris plants but also provides ample material for expanding the garden borders. | anachronistic_mistral-small:24b | 0.000 | 0.805 |
| This practice ensures a display of flowers for the border throughout the growing season. | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.062 |

**Brier Score:** 0.3066


## Question 105

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The species most commonly grown is Araucaria excelsa, which the English gardeners call the Norfolk island pine. The foliage of this is a dark, rich, yellow green color, and the manner of growth is very symmetrical. Another variety, even more attractive, is the Araucaria bidwelli, while several other sorts are offered in the catalogues. All of these are rather easy to grow, and the commoner kinds, [masked clause describing a condition]. Care should be taken not to transfer them too rapidly to larger pots, nor to water them too much.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if purchased when small, are inexpensive | ground_truth | 1.000 | 0.030 |
| if purchased when large, are costly | negation | 0.000 | 0.008 |
| if you supply these requirements to any seed, they should be able to start their growth and thus show you what percentage has sufficient vitality to germinate | same_book | 0.000 | 0.036 |
| if necessary, but do it thoroughly | same_book | 0.000 | 0.008 |
| even though they require well-drained soil and bright light | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.896 |
| which are more tolerant of shade, are quite expensive | manual_anachronistic_gpt-oss:20b | 0.000 | 0.022 |

**Brier Score:** 0.2908


## Question 106

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** If transplanted to a cold-frame in the fall, it may be had fresh until Christmas and again in early spring. Clumps may be grown in a pot or a box in the house, or even by the cellar windows, also, if potted during the fall. Tarragon and chives resemble mint in being prized for flavoring and in being hardy perennials propagated by division of clumps, [masked clause conceding a limit or exception]. Tarragon is a native of Siberia and hence is very hardy, although, like mint, the stalks should be cut down in November and a cover of litter or mulch provided.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| although they are otherwise quite unlike plants | ground_truth | 1.000 | 0.016 |
| although they bear a close resemblance to plants. | negation | 0.000 | 0.011 |
| although the Poet's Narcissus is also well worth very general planting | same_book | 0.000 | 0.012 |
| although in windows looking south or east they are more likely to blossom freely on account of the abundant sunshine | same_book | 0.000 | 0.054 |
| however, they are both less hardy than mint | manual_anachronistic_metadataless_mistral-small:24b | 0.000 | 0.343 |
| though they may not survive the harshest winter temperatures in the northernmost regions. | anachronistic_gpt-oss:20b | 0.000 | 0.564 |

**Brier Score:** 0.2347


## Question 107

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The best plan for profits, however, is the sale of plants for home gardens. The main costs of the hardy plants catalogued by large dealers, and of bedding plants supplied by local florists, are incident to advertising, soliciting orders, packing,
and transportation. A school may sell plants at a third or a fourth of the usual retail prices and yet secure a good income, since the costs named above are not incurred and the labor cost is nothing, [masked clause describing a cause or reason]. A cold frame is a great help in raising plants for sale, even in the case of vegetables, as it enables one to place lettuce and radishes on the market before their price declines.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| because it is incidental to garden instruction and training | ground_truth | 1.000 | 0.031 |
| because the labor is superfluous and unrelated to garden instruction | manual_negation | 0.000 | 0.038 |
| for example, to a dozen vases of Comet Asters, one blossom in each, or to four heads of lettuce | same_book | 0.000 | 0.058 |
| because the students are willing to volunteer | anachronistic_mistral-small:24b | 0.000 | 0.259 |
| because the school can rely on volunteer labor and avoids marketing expenses. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.614 |

**Brier Score:** 0.2777


## Question 108

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** Do not feel that the flowers need other greenery than that furnished by their own leaves and stems. The universal custom of mixing smilax or the so-called Asparagus Fern with beautiful flowers, is one that cannot be too strongly condemned. This is simply a relic of the old-fashioned bouquet, with its barbarous intermixture of all kinds of form and color into a shapeless mass which might appeal to a Hottentot, [masked clause describing a tension or contrast]. It was of these bouquets that Sir Edwin Arnold, after some years of residence in Japan, wrote: "Your European florist-who masses together his roses and his Maidenhair Ferns and Calla Lilies, surrounding them with a dish of green and an outer overcoat of lace-paperappears to the Japanese lover of flowers lower than a barbarian.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but certainly should never appeal to an educated American | ground_truth | 1.000 | 0.046 |
| but would surely entice a well-read American | negation | 0.000 | 0.030 |
| but it is not a fern at all, but a true asparagus and is closely related to the common garden vegetable | same_book | 0.000 | 0.179 |
| but choose only one kind at a time and, as a rule, only a few of these, giving to each flower an opportunity to speak for itself and to express to the soul of the beholder its special message of beauty | same_book | 0.000 | 0.229 |
| but it is utterly repugnant to those with an educated eye | anachronistic_mistral-small:24b | 0.000 | 0.368 |
| wbut where the West revels in ornamental excess, the East craves the quiet dignity of a single, unadorned flower | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.149 |

**Brier Score:** 0.1923


## Question 109

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** I do not think that an ardent girl who loves music art, and poetry, and who hates history and science and mathematics, will ever quite do herself justice if she carries on all three of her favorite studies and ignores the others, even though her favorites are most essential to culture. I think, however, that though mathematics cannot be spared from the foundation of an education, it yields less culture on the whole to students who have no taste for it than any other study, [masked clause describing an inference or effect]. A friend says we must all be one-sided, so that perhaps our best chance is to have one hobby at a time and ride that to death, and then try another, becoming at last two, three, or four-sided, though never completely rounded.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so I do not advocate carrying it far, but history or some science would be a good counterpoise for a mind given to the study of beauty alone | ground_truth | 1.000 | 0.155 |
| so I recommend pushing it further, but history and every science would be an excellent match for a mind inclined towards studying beauty exclusively | negation | 0.000 | 0.020 |
| so the rich must humbly try to take their place | same_book | 0.000 | 0.028 |
| as students who do not have any taste or interest in them will not be able to fully appreciate their importance and potential contributions | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.337 |
| they will thus be deprived of the broader cultural benefits that a more balanced education would afford | anachronistic_gpt-oss:20b | 0.000 | 0.460 |

**Brier Score:** 0.2081


## Question 110

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** Some one gives this good rule, "Decide when you ought to rise to make the best use of your day. Make a point of rising at that time; but go to bed earlier and earlier till you find out how much sleep you need in order to be fresh at that hour in the morning." Such a rule would meet most cases, but not all; [masked clause describing a cause or reason]. I would give more flexible rules, though it is harder to keep flexible rules than iron ones.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for though regularity is as important for health as for a wise life, it cannot be an iron regularity, especially if a girl is at all delicate | ground_truth | 1.000 | 0.135 |
| for while irregularity may harm both physical and mental well-being, it need not be rigidly avoided, particularly if a girl is robust | negation | 0.000 | 0.115 |
| because an extra hour in the morning can be better used than one later in the day, and if duties crowd you get tired in remembering what you cannot do | same_book | 0.000 | 0.083 |
| because it will give you an outlook beyond the daily horizon, and take your thoughts from your own weariness | same_book | 0.000 | 0.086 |
| for it should be modified if one has a child with colic or an elderly person under their care who requires night-time attention | manual_anachronistic_mistral-small:24b | 0.000 | 0.259 |
| because people’s sleep needs and daily obligations vary widely, making a fixed wake time unsuitable for everyone | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.322 |

**Brier Score:** 0.1579


## Question 111

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


## Question 112

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She has perhaps too great a scorn of receiving help from anybody. She once acted as a substitute in school for a friend who was ill. The obliged friend insisted that she should receive the ten dollars which would otherwise have been paid to herself. [masked sentence revising an implied expectation] I know of no one who acts more thoroughly on the rule, "If you have but sixpence to spend, spend it like a prince, and not like a beggar.” She is a true lover of nature, without pretense or cant of any kind.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But the independent young lady instantly took the money and invested it all in a beautiful piece of lace which she sent as a present to the convalescent. | ground_truth | 1.000 | 0.206 |
| But the dependent young lady instantly rejected the money and spent none on a beautiful piece of lace which she refused to send as a gift. | negation | 0.000 | 0.041 |
| Nevertheless, her bills amounted to one sixth of the yearly income of the family, so that she never gave another party till later in life, when fortune suddenly smiled upon her again and put her in possession of a million. | same_book | 0.000 | 0.070 |
| But if she does a tithe as much for the poor she is likely to get some thanks, more or less sincere, and all her circle of friends admire her. | same_book | 0.000 | 0.062 |
| However, she refused to accept it, believing that she had no right to be paid for doing something that was not out of the ordinary. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.530 |
| Nevertheless, I declined the ten dollars, feeling that accepting such a gift would betray my principles of self‑reliance; true virtue, I believe, resides in refusing even sincere aid. | anachronistic_gpt-oss:20b | 0.000 | 0.090 |

**Brier Score:** 0.1550


## Question 113

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** If, in the end, a girl marries, her reading and cooking and housekeeping are all necessary. How can she use these homely accomplishments in earning a living? They will not, to be sure, bring her a large income, but there is a steadier demand for good work in these directions than in any others. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| So a woman who has them is almost sure of a modest support. | ground_truth | 1.000 | 0.037 |
| So a woman who lacks them is sure of a modest support. | manual_negation | 0.000 | 0.017 |
| Of course she may thus in time be fitted for higher work, and she may prefer to do it, and may even earn more money by it, but she will then do the work because it is her natural choice and not for the sake of the money." | same_book | 0.000 | 0.170 |
| She will find that her husband and family will benefit from her skills to maintain a happy home. | anachronistic_mistral-small:24b | 0.000 | 0.180 |
| Consequently, she can earn a modest but steady wage by offering her cooking, housekeeping, and reading skills to families who require such assistance. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.596 |

**Brier Score:** 0.2691


## Question 114

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** Both these influences have a noble source, and will probably reach more beautiful results at last. Any mind awake to beauty must try to create it, and if its power and originality are not very great, what can it do better than to apply itself to humble, every-day trifles and try to decorate them? This is certainly right, [masked clause describing a condition or proviso]: "Decorate construction, do not construct decoration." A few illustrations of my meaning may be needed.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if the old principle of architecture is always remembered | ground_truth | 1.000 | 0.015 |
| if the old principle of architecture is ever forgotten | negation | 0.000 | 0.012 |
| unless the circumstances are of a very unusual character | same_book | 0.000 | 0.038 |
| provided it is done with sincerity and an understanding of form | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.443 |
| provided that the decoration remains modest and serves the purpose of the piece | anachronistic_gpt-oss:20b | 0.000 | 0.492 |

**Brier Score:** 0.2821


## Question 115

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was among the most skillful physicians of her native city. She saved many lives, and relieved much suffering. She gave her priceless services to hundreds of poor people, but she did not give to those who could pay for them. I think she was altogether right. [masked sentence describing a cause or reason] Perhaps she blocked the way of less fortunate physicians.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The world was better because she used her gift, and she was happier, as all are who exercise their powers. | ground_truth | 1.000 | 0.056 |
| The world was worse because she squandered her gift, and she was unhappier, as all are who neglect their powers. | negation | 0.000 | 0.046 |
| It was because she could give priceless services that she had so clear a right to fix a price which she did not need. | same_book | 0.000 | 0.033 |
| Her renunciation comes partly because she loves those for whom she makes the sacrifice, but partly also from cowardice. | same_book | 0.000 | 0.013 |
| She believed that those who could afford medical care should support their local doctors financially. | anachronistic_mistral-small:24b | 0.000 | 0.372 |
| She believed that medicine should be a universal right, not a commodity. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.479 |

**Brier Score:** 0.2104


## Question 116

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He went beyond Bear creek to the forks of the rivers and there saw it growing in great masses-acres, in fact, covered as thickly as clover fields. Wagon-loads were eventually taken away and still there appeared to be no diminution in abundance. So the search for Shortia ended. Through the further efforts of Mr. Harbison, the plant is now well known and a common one in nursery catalogues, [masked clause acknowledging a countervailing fact]. grows at its finest and best under the shade of kalmias and rhodendrons."

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though in its wild state it | ground_truth | 1.000 | 0.411 |
| though when domesticated it | manual_negation | 0.000 | 0.005 |
| although it was hoped, in vain, that "revisiting the haunts of his youth and the pleasing recollections of juvenile scenes would have salu- tary influence in arresting the disease | same_book | 0.000 | 0.035 |
| though it is not always easy to find and propagate | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.160 |
| though it remains scarce in its native habitats | anachronistic_gpt-oss:20b | 0.000 | 0.389 |

**Brier Score:** 0.1049


## Question 117

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** I shall be pleased in your calling on your intended journey, and hope you will consider my uncle's house as a welcome stage. I am, with all due respect, Your much obliged friend, MOSES MARSHALL. Marshall's letters speak of many long trips which meant fatigue, danger and expense. His appointment as justice of the peace curtailed excursions, [masked clause describing a tension or contrast]. About 1797 he married Alice Pennock and had six children.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but he continued exchanging specimens and seeds with European confrères | ground_truth | 1.000 | 0.103 |
| but he ceased trading specimens and seeds with European colleagues | negation | 0.000 | 0.017 |
| however, to get him a wife, Miss Christie; then he returned to Pennsylvania and became a public character, holding in succession the offices of surveyor-general, master in chancery and lieutenant-governor | same_book | 0.000 | 0.108 |
| but always without success | same_book | 0.000 | 0.001 |
| but his family now provided him with new reasons to travel | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.168 |
| though it curtailed his wanderings, it also bound him to the duties of his office | anachronistic_gpt-oss:20b | 0.000 | 0.603 |

**Brier Score:** 0.2013


## Question 118

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He studied medicine under Dr. Nicholas Way of Wilmington, but never held a medical degree, none being required at that time for practicing in Pennsylvania; but, as it was customary to attend a course of lectures, he went to those by Shippen and Rush in Philadelphia. His diary at this time shows that medicine did not wholly absorb his attention, [masked clause describing a cause or reason] Then followed a year or two employed in desultory medical work, including inoculations round about Londongrove, Pennsylvania, and in keeping an apothecary's shop "which came to nothing and less."

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for frequent mention is made of a certain Polly Howell and a Sally Samson, the latter "behaving for three evenings, especially the last, in a most engaging manner." | ground_truth | 1.000 | 0.055 |
| for there is scarce any mention of anyone named Polly Howell or Sally Samson, neither being noteworthy | negation | 0.000 | 0.007 |
| owing to the fact that the authorities were wise enough to adopt the stringent sanitary precautions urged by Bigelow, who, with Ware and Flint, offered his services as investigator of the conditions in New York | same_book | 0.000 | 0.088 |
| for the old man was at least enabled to distinguish his favorite plants as he walked in his gardens | same_book | 0.000 | 0.042 |
| as he was also deeply engaged with his studies of botany | anachronistic_mistral-small:24b | 0.000 | 0.532 |
| because his interests lay more in the practical affairs of his community than in theoretical study | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.277 |

**Brier Score:** 0.2105


## Question 119

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He still clung to the idea that its natural habitat must be, as Michaux said, in les hautes montagnes de Caroline, arguing that the point on the Catawba where it had been found was an outlying haven to which it might have been washed. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| So with renewed energy it was searched for through the mountains, but always without success. | ground_truth | 1.000 | 0.063 |
| So he abandoned the notion that it could be found in the mountains, and searched instead in the swamps of Carolina. | manual_negation | 0.000 | 0.084 |
| So also was the scene of his first settled practice, Hopkinsville, then a wild, romantic district where he gathered patients and plants, soon getting into touch with scientific men everywhere by exchanging specimens. | same_book | 0.000 | 0.011 |
| This belief led him to continue his search for the plant in the mountainous regions of North Carolina. | anachronistic_mistral-small:24b | 0.000 | 0.626 |
| He inferred that the specimen had been transported downstream from its true mountain home. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.217 |

**Brier Score:** 0.2649


## Question 120

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** Dr. John Tennant, an enthusiastic botanist of Virginia, swears against all disputants by Seneca snakeroot for pleurisy; the experimenter and botanist, Dr. Samuel Thomson, later uses Lobelia inflata in his "Thomsonian System" for nearly every evil, and creates endless opposition. [masked sentence describing a tension or contrast] Of the young British doctors who came over here, John Mitchell was the earliest.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But the search for remedies was keen in days when malaria and dysentery ravaged whole towns and paralyzed industry. | ground_truth | 1.000 | 0.029 |
| But the search for remedies was sluggish in days when malaria and dysentery ravaged whole towns and paralyzed industry. | negation | 0.000 | 0.034 |
| But the work which brought Bigelow into closest contact with European savants and gave him honor in his own country was the elaborate series published under the title "American Medical Botany," which was noted for its finish and beauty and avoidance of technical terms. | same_book | 0.000 | 0.103 |
| There was sometimes, however, bloodless warfare in the botanical camp in disputation over the alleged medicinal merits of certain plants. | same_book | 0.000 | 0.030 |
| While Dr. Mitchell's methods were more scientific and analytical, Dr. Thomson relied heavily on his own intuition and observations. | anachronistic_mistral-small:24b | 0.000 | 0.170 |
| Tennant’s cautious endorsement of Seneca snakeroot clashed sharply with Thomson’s zealous promotion of Lobelia inflata, igniting a heated rivalry that reverberated through the medical community. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.635 |

**Brier Score:** 0.2313


## Question 121

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** It is alternately invaded by the hyperborean legions and by the wilting sirens of the tropics. Icicles hang always on its northern heights; its seacoasts are fringed with mosquitoes. There is for a third of the year a contest between the icy air of the pole and the warm wind of the gulf. [masked sentence describing an inference or effect] It is the normal condition in New England.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The result of this is a compromise: the compromise is called Thaw. | ground_truth | 1.000 | 0.029 |
| The result of this is a gradual, steady, even warming. | manual_negation | 0.000 | 0.067 |
| So plainly marked and well-trodden are they, that it is easy to mistake them for trails made by hunters; but he who follows one of them is soon in difficulties. | same_book | 0.000 | 0.305 |
| This creates a unique and ever-changing environment where the extremes of winter and summer battle. | anachronistic_mistral-small:24b | 0.000 | 0.430 |
| Consequently, the townsfolk must keep both an ice pick and a sun hat in their pockets. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.169 |

**Brier Score:** 0.2508


## Question 122

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** Not being able to recognize any tracts, I have no evidence that I had so travelled, except the general testimony of lost men. The compass annoyed me. I've known experi enced guides utterly discredit it. It could n't be that 

I was to turn about, and go the way I had come. [masked sentence describing a tension or contrast] Better listen to science than to spunk."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Nevertheless, I said to myself, "You'd better keep a cool head, my boy, or you are in for a night of it. | ground_truth | 1.000 | 0.131 |
| Nevertheless, I said to myself, "You'd better lose your temper, my boy, or you'll have an easy time. | negation | 0.000 | 0.068 |
| But consider what a shot it was! | same_book | 0.000 | 0.002 |
| But what is this in the morning journal at breakfast? | same_book | 0.000 | 0.008 |
| The very instrument designed to guide me seemed to contradict my instincts and the wisdom of those who had traversed these woods before. | anachronistic_mistral-small:24b | 0.000 | 0.753 |
| The lure of uncharted territory tugged against the fear that each step might unravel the very fabric of reality's fragile illusion today. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.038 |

**Brier Score:** 0.2215


## Question 123

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** I should get close to the log, crawl under my hat, strike the match, see it catch, flicker, almost go out (the reader painfully excited by this time), blaze up, nearly expire, and finally fire the punk, thank God! And I said to myself, "The public don't want any more of this thing: it is played out. Either have a box of matches, or let the first one catch fire." In this gloomy mood I plunged along. The prospect was cheerless; [masked clause describing a cause or reason]. I fancied I could hear the tread of the stealthy brutes following their prey.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for, apart from the comfort that a fire would give, it is necessary, at night, to keep off the wild beasts | ground_truth | 1.000 | 0.311 |
| for, apart from the discomfort that fire would cause, it tends to attract wild beasts | manual_negation | 0.000 | 0.060 |
| for we had not expected to pass that night in the woods | same_book | 0.000 | 0.103 |
| because I knew that if I failed to set my fire ablaze with this match, the wolves would be upon me | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.276 |
| because the valley lay shrouded in a perpetual gray mist, with no sign of life | anachronistic_gpt-oss:20b | 0.000 | 0.250 |

**Brier Score:** 0.1254


## Question 124

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** When I guessed that I must be close to the river, I suddenly stepped into mud up to my ankles. It was the road, running, of course, the wrong way, but still the blessed road. It was a mere canal of liquid mud; but man had made it, and it would take me home. I was at least three miles from the point where I supposed I was near at sunset, and I had before me a toilsome walk of six or seven miles, most of the way in a ditch; [masked clause describing a tension or contrast]. I was safe; I knew where I was; and I could have walked till morning.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but it is truth to say I enjoyed every step of it | ground_truth | 1.000 | 0.043 |
| but it is true to say that I hated every step of it | manual_negation | 0.000 | 0.100 |
| however, of dropping off to sleep, somebody unfortunately notes a drop of water on his face; this is followed by another drop; in an instant a stream is established | same_book | 0.000 | 0.025 |
| but a succession of falls, cascades, flumes, and pools, that would delight an artist | same_book | 0.000 | 0.052 |
| yet I was exhausted and famished | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.680 |
| though the darkness of night could hide unseen perils | anachronistic_gpt-oss:20b | 0.000 | 0.101 |

**Brier Score:** 0.2336


## Question 125

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** The spur we chose for our escape looked smooth in the distance; but we found it bristling with obstructions, dead balsams set thickly together, slashes of fallen timber, and every manner of woody chaos; and when at length we swung and tumbled off the ledge to the general slope, we exchanged only for more disagreeable going. The slope for a couple of thousand feet was steep enough; but it was formed of granite rocks all moss-covered, [masked clause describing an inference or effect].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that the footing could not be determined, and at short intervals we nearly went out of sight in holes under the treacherous carpeting | ground_truth | 1.000 | 0.065 |
| so that the footing was obvious, and at frequent intervals we stayed clearly visible above the solid ground | negation | 0.000 | 0.016 |
| so far was I from feeling any uneasiness about this, that I quickened my pace again, and, before I knew it, was in a full run; that is, as full a run as a person can indulge in in the dusk, with so many trees in the way | same_book | 0.000 | 0.144 |
| so as to be sure to strike either the clearing or the road, and not wander off into the measureless forest | same_book | 0.000 | 0.031 |
| making every step treacherous and slow | anachronistic_mistral-small:24b | 0.000 | 0.644 |
| making every foothold a treacherous gamble, as moss‑slicked granite threatened to give way beneath us | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.101 |

**Brier Score:** 0.2201


## Question 126

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** She knew, by their uncertain yelping up and down the opposite bank, that she had a little respite: she used it, however, to push on until the baying was faint in her ears; and then she dropped, exhausted, upon the ground. This rest, brief as it was, saved her life. Roused again by the baying pack, she leaped forward with better speed, [masked clause conceding a limit or exception]. It was still a race for life; but the odds were in her favor, she thought.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though without that keen feeling of exhilarating flight that she had in the morning | ground_truth | 1.000 | 0.011 |
| though her speed was more exhilarating than it had been in the morning | manual_negation | 0.000 | 0.124 |
| although they said it was small for a bear | same_book | 0.000 | 0.004 |
| though they were still hidden by a ridge) she turned away towards the north, and kept on at a good pace | same_book | 0.000 | 0.024 |
| except when her strength began to fail | anachronistic_mistral-small:24b | 0.000 | 0.797 |
| though the pack surged ahead, her lungs burned and she could barely breathe slowly | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.041 |

**Brier Score:** 0.2717


## Question 127

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** He intends no harm: he only gratifies a curiosity to see if he can hit the mark. Where shall he draw the line? Doubtless he might throw a stone at a chipmunk or shout at a loon. Might he fire at a mark with an air-gun that makes no noise? He will not fish or hunt on Sunday (although he is no more likely to catch anything that day than on any other); but may he eat trout that the guide has caught on Sunday, [masked clause describing a condition or proviso]? Is there such a thing as a vacation in religion?

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if the guide swears he caught them Saturday night | ground_truth | 1.000 | 0.099 |
| if the guide denies catching them on Saturday | negation | 0.000 | 0.086 |
| if none of his congregation are present | same_book | 0.000 | 0.044 |
| if such a cave exists | same_book | 0.000 | 0.025 |
| if the guide has taken them legally during the week | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.254 |
| provided he does not break the silence of the day | anachronistic_gpt-oss:20b | 0.000 | 0.492 |

**Brier Score:** 0.1882


## Question 128

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** The patient should then be examined for needle punctures and if a heroin snuffer, the mucous membrane of the nose should also be carefully examined. The writer has discovered that no matter what the amount the patient declares he is taking, he can begin with less than fifty grains per week 34
with the assurance that his patient will not suffer. This amount is steadily reduced each week, [masked clause describing a condition]. The reckless prescribing of narcotic drugs with no apparent plan of treatment and the mercenary rapacity indicated by some who hold a license to practice medicine, is to be deplored.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if no painful complications arise, until the patient is cured | ground_truth | 1.000 | 0.066 |
| if any painful complications occur, until the patient is not cured | negation | 0.000 | 0.008 |
| if they survive the horrible torture called "cure," have been turned loose in such a deplorable mental and physical condition that they have returned to the drug as the only means of obtaining relief | same_book | 0.000 | 0.097 |
| if not relieved, usually results in wild mental confusion in which the patient often becomes destructive and violent, and in some cases may end in death | same_book | 0.000 | 0.080 |
| until he has been entirely weaned off the drug. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.567 |
| provided no withdrawal symptoms or adverse reactions appear. | anachronistic_gpt-oss:20b | 0.000 | 0.182 |

**Brier Score:** 0.2070


## Question 129

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** He said that on the East Side there were school children who belonged to families who were all addicts. Oh! that someone could plead for these people whose voice 10
would be heard over the tumultous sounds of condemnation that are filling the country. I believe that those who make laws believe that they are doing the right thing, and usually they are, [masked clause describing a tension or contrast]. That combined with their power and wisdom would solve the problem, I believe.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but this question at stake involves that which they won't consider as anything but weak, and that is the heart element | ground_truth | 1.000 | 0.025 |
| but this question at stake involves something they view as strong, and that is the heart element | negation | 0.000 | 0.011 |
| but of what kind | same_book | 0.000 | 0.000 |
| but the law says it must be done | same_book | 0.000 | 0.074 |
| but often they are misinformed about the true nature of addiction | anachronistic_mistral-small:24b | 0.000 | 0.807 |
| while they proclaim righteousness, they often ignore the systemic inequities that fuel addiction, turning their power into a double‑edged sword that harms more than it helps | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.083 |

**Brier Score:** 0.2691


## Question 130

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** "In office prescribing, it should be the duty of the physician at the beginning of treatment to provide the patient with a card bearing the name and a general description of the patient, as follows: 

Name of patient, age, height, weight, color of eyes, color of hair, and having a photograph of the patient similar to the requirements of a passport. As each prescription is given the patient the physician shall indicate same on the card, with date of prescription and signature of physician." Extension prescriptions should be permitted in special cases only where a patient obtains work in a distant city may occupy him for several weeks, should not be called on to pay car fare oftener than once in three weeks to obtain his proper dosage and should not be placed in a position that makes it necessary to resort to purchase from traffickers, [masked clause describing a cause or reason]. It 38
is then that the law should step in and the State provide the ways and means to permanent recovery.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for if this happens, the work of months is undone and the poor victim is drawn back to his old habits by his loss of self control | ground_truth | 1.000 | 0.150 |
| for if this happens the work of months stands firm and the fortunate individual maintains their self-control | manual_negation | 0.000 | 0.009 |
| because of the loathsome nature of the disease, would be unworthy of his profession | same_book | 0.000 | 0.104 |
| as its principal use is to allay coughing | same_book | 0.000 | 0.023 |
| or where the patient is unable to return due to illness. | anachronistic_mistral-small:24b | 0.000 | 0.351 |
| when the patient is experiencing significant travel barriers such as lack of reliable transportation, financial constraints, or safety concerns that impede regular access to medication | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.363 |

**Brier Score:** 0.1649


## Question 131

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The artists Hiram furnished to Solomon, for the construction and adornment of his Temple and palace, represented the skill of the nation; it comprehended every branch of art, working in gold and silver, in brass and iron,
in purple and blue, in stone and timber, in fine linen and in the engraving of precious stones. Phoenicia had inexhaustible supplies of cedar and fir. [masked sentence describing an inference or effect] All the internal work of 

Solomon's temple, instead of sculpture, was carved work, of olive wood, cedar and gold, with which the walls were lined.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Hence it was natural that wood should be the prevailing material of Phoenician architecture, while it was almost banished from that of Egypt. | ground_truth | 1.000 | 0.216 |
| Hence it was unnatural that wood should be the prevailing material of Phoenician architecture, while it was almost embraced in that of Egypt. | negation | 0.000 | 0.065 |
| Thus the style of art prevailing at the period in the capital of Phoenicia would, doubtless, be stamped on every part, and we are interested to know what may have been the style peculiar to Phoenicia, if indeed it was peculiar to it, seeing that there are no remains of native art existing which can be safely depended upon. | same_book | 0.000 | 0.136 |
| This influx of skilled artists and abundant materials likely resulted in the creation of a masterpiece of architectural beauty and intricate design. | anachronistic_mistral-small:24b | 0.000 | 0.372 |
| The result was an interior that glowed with the richness of cedar and gold, a testament to the artisans' skill. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.211 |

**Brier Score:** 0.1641


## Question 132

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The description in Kings, 21st verse, is, "Solomon overlaid the house within with pure gold, and he made a partition by the chains of gold before the oracle,” in which bronze columns may have been introduced to carry the additional height of the end wall of the sanctuary. Canina's arrangement of the chambers round the house I think most correct. Neither their number nor their length is given in Kings or Chronicles, [masked clause acknowledging a countervailing fact]. Ezekiel, in his vision of the restored temple, tells us that "the side chambers were three, one over another, and thirty in order," that is, thirty in all on the sides of the house, besides those at the end of the oracle.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though the former gives their width and height, while the latter does not mention them at all | ground_truth | 1.000 | 0.156 |
| though neither gives their width nor mentions their height | negation | 0.000 | 0.006 |
| though they might very reasonably have done so | same_book | 0.000 | 0.033 |
| though Chronicles seems to double that given in Kings; but they are three times mentioned as 18 cubits high, twice in Kings and once in Jeremiah | same_book | 0.000 | 0.052 |
| however, some scholars dispute the accuracy of this interpretation | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.693 |
| yet the prophetic vision in Ezekiel supplies a count | anachronistic_gpt-oss:20b | 0.000 | 0.060 |

**Brier Score:** 0.2001


## Question 133

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The "Sister's Kiss," the "Tangled Skein," and the "Music 

Lesson," were marvels of beauty and pure sentiment: "Roses that bathe about the well of life," each an epitome of "sweetness and light," of delicate innocence and loveliness redeeming the voluptuous sensuousness of his dazzling odalisques. [masked sentence describing a tension or contrast] A dream of fair women, or sleeping beauties classically clad, might express its whole meaning.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But the picture of the past year, and the last of his greater efforts, seems to me to fail on the ethical side. | ground_truth | 1.000 | 0.021 |
| But the picture of the past year, and the last of his lesser efforts, seems to me to succeed on the ethical side. | negation | 0.000 | 0.016 |
| But before all is the feeling it inspires of sweet intelligence and womanly winsomeness. | same_book | 0.000 | 0.005 |
| But the skill of the accomplished artist, whose aims are lofty and true, elevates and glorifies his ideal, and gives to his subject the refinement that comes of sweet unconscious- His nude figures (if they should appear in answer to historical or archæological accuracy, representing national customs or poetic license) will not know that they are so, and will not suggest to the pure anything but the purity that conceives them. | same_book | 0.000 | 0.030 |
| Yet they stood in stark contrast to his darker, more provocative works. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.756 |
| Yet the tender glow of these compositions was counterpointed by a quiet undercurrent of longing, a hint of the raw desire that lay beneath the veneer of innocence. | anachronistic_gpt-oss:20b | 0.000 | 0.173 |

**Brier Score:** 0.2603


## Question 134

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** In fact, it is affirmed that the porch, of which the whole internal depth was 10 cubits, rose to a height exceeding by several feet the ball of fire crowning the monument of London, which be it remembered, was entirely over-laid with pure gold! It is correctly stated, [masked clause describing a tension or contrast]. But "the 

Lord had said that he would dwell in thick darkness."

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| however, that the Oracle or Holy of Holies of Solomon's Temple, like unto the Tabernacle, had no light, neither windows, nor candlestick, and if it had had the one it would also have had the other | ground_truth | 1.000 | 0.364 |
| however, that the Oracle or Holy of Holies of Solomon's Temple was brilliantly illuminated with windows and lampstands | manual_negation | 0.000 | 0.109 |
| but he has increased the length of the sanctuary by the thickness of the wall separating the oracle therefrom; whereas, in every description in the Bible, the whole length of the house is given as threescore cubits, and the separation of 20 cubits for the oracle was afterwards made | same_book | 0.000 | 0.223 |
| but this was too much to give up without taking something in return, so while the Bible says they were made of "olive tree," Josephus declares they were of " solid gold!" | same_book | 0.000 | 0.086 |
| despite its opulent exterior, was starkly bare and humbling within | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.090 |
| though its magnificence dazzled the eye, its foundation concealed a profound darkness | anachronistic_gpt-oss:20b | 0.000 | 0.129 |

**Brier Score:** 0.0830


## Question 135

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** "And so will I go in unto the King and if I perish I perish." A supreme self sacrifice for a Nation's redemption. There was a law that not even the Queen might claim an audience of the King unbidden. Yet if he bent his golden sceptre towards her, the suppliant might approach; but the penalty was death, [masked clause describing a condition or proviso]. This was the risk she ran, and suddenly she appeared in all her beauty before him, the sceptre bent towards her and she made her request.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if so be his pleasure was otherwise | ground_truth | 1.000 | 0.025 |
| if the King was well pleased | manual_negation | 0.000 | 0.142 |
| if I may so say | same_book | 0.000 | 0.018 |
| if indeed it was peculiar to it | same_book | 0.000 | 0.015 |
| unless he himself extended an invitation | anachronistic_mistral-small:24b | 0.000 | 0.702 |
| unless she bears the sigil of the ancient house upon her breast | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.098 |

**Brier Score:** 0.2459


## Question 136

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** Ezekiel, in his vision of the restored temple, tells us that "the side chambers were three, one over another, and thirty in order," that is, thirty in all on the sides of the house, besides those at the end of the oracle. Our ingenious friend, Josephus, finding that the phrase, "thirty in order," might be translated "three and thirty times," or thirty times three, says there were thirty chambers on each floor, in all ninety chambers-it mattered not to him how small they were in plan, [masked clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for what they lost in length he quadrupled in height | ground_truth | 1.000 | 0.016 |
| for what they gained in length, he halved in height | negation | 0.000 | 0.029 |
| for the construction and adornment of his Temple and palace, represented the skill of the nation; it comprehended every branch of art, working in gold and silver, in brass and iron, in purple and blue, in stone and timber, in fine linen and in the engraving of precious stones | same_book | 0.000 | 0.245 |
| for their immediate neighbours, the Tyrians and Sidonians, have left no monuments either at home or abroad | same_book | 0.000 | 0.113 |
| provided he could accommodate his arbitrary view of the temple's dimensions | anachronistic_mistral-small:24b | 0.000 | 0.284 |
| because his priority was the symbolic significance of the numbers rather than the precise dimensions | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.313 |

**Brier Score:** 0.2033


## Question 137

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** In this they were not singular, for their immediate neighbours, the Tyrians and Sidonians, have left no monuments either at home or abroad. Tyre, Sidon, Jerusalem, Baalbec, Palmyra, Carthage, possess no architectural antiquities anterior to Roman times, except perchance vast masses of masonry, the retaining walls of imposing platforms upon which were reared those structures which have since disappeared. The Jews, however, were by no means ignorant of the building arts, as practised by the Egyptians, but their ideas of building were all associated in their minds with bondage; [masked clause describing an inference or effect]. The two great authorities on the subject are, of course, the Bible itself and the Jewish historian, Josephus.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that Solomon employed not his own people to build his Temple; of them it is distinctly stated he made captains and over-lookers only | ground_truth | 1.000 | 0.093 |
| so that Solomon appointed his own people to construct the temple, relying on Jews for menial labor | manual_negation | 0.000 | 0.061 |
| so far, drawn my illustrations from among historical painters, but the same principles are applicable to every form of art, whether it be painting, sculpture, architecture, music, or poetry | same_book | 0.000 | 0.143 |
| they avoided building stone structures as reminders of their enslavement in Egypt | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.382 |
| this resulted in a cautious, restrained approach to monumental architecture | anachronistic_gpt-oss:20b | 0.000 | 0.321 |

**Brier Score:** 0.2191


## Question 138

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Similarly, in the centuries of Faith before the dawn of the modern world the human element could be dispensed with, to a degree, in the sacerdotal character, because the Faithful were held by the sweetness of the God they knew so well. This spiritual tie made the cords of Adam unnecessary. [masked sentence describing a tension or contrast] This claim is emphasized by the cultivation and information of the masses around us.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But in our days of Indifferentism, which are not blessed with the charm of the new nor with the sweetness of the old in Religion, the prerogatives of nature have a special claim on priests. | ground_truth | 1.000 | 0.112 |
| But in our days of fervent conviction, which are blessed with the novelty of the new and the nostalgia of the old in religion, the prerogatives of nature have little appeal to priests. | negation | 0.000 | 0.079 |
| But the supreme importance of this spiritual quality does not make the need of mere human knowledge, nor the knowledge of the best methods of imparting it, any the less imperative. | same_book | 0.000 | 0.133 |
| They did not, however, value the soul of a child as Christianity has taught us to do. | same_book | 0.000 | 0.176 |
| However, as modern society has increasingly turned to science and reason, this spiritual bond has weakened and the role of religious authorities has become more crucial than ever. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.349 |
| Yet, this reliance on divine sweetness occasionally produced a dangerous complacency that left the clergy vulnerable to worldly temptation. | anachronistic_gpt-oss:20b | 0.000 | 0.151 |

**Brier Score:** 0.1647


## Question 139

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** They will progress with religious zeal, high courage and strong endeavor, and imitating Columbus, who wrote in his journal day after day, those simple, but sublime words, "sailed westward today which is my course," they will write in their faculty records day after day, "progressed knowledgeward today which is our course," and like him give new knowledge to the world, and enlarge the boundaries of the scope of earthly life. It is of great interest to note that the inception of the University was almost coincident with the beginning of your priestly life, [masked clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for it was in the Second Plenary Council of Baltimore that the establishment of the University received its first consideration | ground_truth | 1.000 | 0.216 |
| for ithe University was established long before your attendance at the Second Plenary Council of Baltimore | manual_negation | 0.000 | 0.032 |
| inasmuch as from their confidence in writing they will recollect by the aid of foreign symbols, and not by the natural use of their own faculties | same_book | 0.000 | 0.034 |
| as when, for instance, two thousand accompanied the remains of St. Martin to the tomb, but deeply spiritual and enthusiastic to place within the reach of others the blessings which they enjoyed in this new form of spiritual endeavor | same_book | 0.000 | 0.029 |
| because of your unwavering faith and dedication to educational excellence. | anachronistic_mistral-small:24b | 0.000 | 0.473 |
| as your spiritual vocation aligned with the era's burgeoning thirst for knowledge | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.216 |

**Brier Score:** 0.1480


## Question 140

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** While the University welcomed the students of the Summer School for the purpose of instruction, it was felt that the presence of so many whose lives are consecrated to God's service in the field of education, could not but prove beneficial to all concerned in the work. As a matter of fact, [masked clause describing a condition].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if zeal and devotion to study are the essentials of university atmosphere, there is every reason to place this brief session on record as one of the most valuable in our educational history | ground_truth | 1.000 | 0.113 |
| if apathy and neglect of study are the hallmarks of a university atmosphere, there is no reason to commemorate this brief session as one of the most valuable in our educational history. | negation | 0.000 | 0.117 |
| if the interests of Catholic education are not to suffer | same_book | 0.000 | 0.220 |
| if taught in the proper manner, would prevent many of these deplorable results | same_book | 0.000 | 0.093 |
| the interaction and exchange of ideas among these students would enrich both their spiritual growth and academic pursuits | manual_anachronistic_metadataless_mistral-small:24b | 0.000 | 0.457 |

**Brier Score:** 0.2130


## Question 141

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


## Question 142

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Whilst quoting these words of a Protestant inspector of schools we must not forget that thousands of Catholics have derived even greater benefits from the study of Kellner's works, and because he knew it he felt bound to continue his literary work to the very end of his life. He insisted that Catholic education ought to be in no way inferior to its competitors, [masked clause describing a tension or contrast]. He died a pious and happy death without showing any
sign of fear.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but rather that its results ought to surpass those of others, especially in the formation of character | ground_truth | 1.000 | 0.204 |
| but rather that its results should fall short of others, particularly in shaping character. | negation | 0.000 | 0.027 |
| but not in deed or word of his could we have known of his sorrow | same_book | 0.000 | 0.007 |
| but when they saw his apparent earnestness, they began to doubt his sanity | same_book | 0.000 | 0.022 |
| despite the fact that his contemporaries often saw Catholic education as inferior | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.573 |
| even though it faced criticism from Protestant educators. | anachronistic_gpt-oss:20b | 0.000 | 0.167 |

**Brier Score:** 0.1652


## Question 143

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** The writer of the article in question knew nothing of the controversy then waging on the terms "college" and "degree," nor of the rival claims set up by the partisans of the two well-known schools devoted to the higher education of young women. It is unlikely that either the institutions or their faculties entered into the discussion, as their time and efforts are given to weightier matters. [masked sentence describing an inference or effect] Since attention is called to her statement on page 639, of the Catholic Educational Review, relative to the opening of the new Collegiate Hall at the Motherhouse, it is only fair to turn to page 635 of the same magazine and learn that St. Mary's was chartered February 28, 1855, under an 

Act of the General Assembly of the State of Indiana and was empowered "to confer such degrees as are used in academies of the highest standing."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Hence it is not surprising that the writer has seen today for the first time a newspaper clipping in which she is quoted as an authority in settling a dispute of which she has never heard. | ground_truth | 1.000 | 0.100 |
| Hence it is unsurprising that the writer has seen today for the first time a newspaper clipping in which she is misquoted as an authority in fueling a dispute of which she has always been aware. | negation | 0.000 | 0.045 |
| So much at any rate lies well within the scope of the seminary's work as it is now conducted. | same_book | 0.000 | 0.074 |
| So it may come to pass that the school, without knowing it, is undoing implicitly the very work which the seminary endeavors to accomplish in its philosophical and theological teaching. | same_book | 0.000 | 0.113 |
| Given her lack of awareness about these issues, it is reasonable to infer that the writer's focus was purely on reporting factual information rather than engaging with contemporary debates. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.668 |

**Brier Score:** 0.2551


## Question 144

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** This principle is well exemplified in nature by that wonderful organ, the heart. In mechanism we have it illustrated in a Corliss engine, for instance. In the human organism, when work and capability are nicely adjusted, facility and effectiveness mark its operations. When it exceeds the moderate degree induced by the capable and enthusiastic teacher's activities, fatigue is a condition, as we well know, which seriously impedes effective work; and it is in order for us, like careful pedagogical engineers, to check up the various ways in which energy is excessively or uselessly expended, [masked clause describing an inference or effect]. We will not now stop to draw distinctions between true and false or imagined fatigue; there may be a better chance another time in treating the question of "nerves."

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that by practicing a wise economy in nerve and brain power we may realize a sustained efficiency | ground_truth | 1.000 | 0.063 |
| so that by squandering our nerve and brain power, we may experience a collapse of productivity | negation | 0.000 | 0.070 |
| so notably shown as in the dark days of its greatest trial | same_book | 0.000 | 0.005 |
| so to speak, to the scientific order, they can be made still more successful | same_book | 0.000 | 0.011 |
| to ensure that we can maintain peak performance levels. | anachronistic_mistral-small:24b | 0.000 | 0.754 |
| and that this surplus expenditure inevitably diminishes the organism's capacity for sustained activity | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.097 |

**Brier Score:** 0.2433


## Question 145

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** A normal, healthy boy walking on tip-toe is about as much at home as a normal, healthy cat walking on walnut shells. MATERIAL CONDITIONS 

821 "Shame itself!" hissed Lady Macbeth in the ear of her troubled and vision-seeing spouse. "Why do you make such faces?" Has not the query a definite and pertinent application to many teachers who, [masked clause conceding a limit or exception]?

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though composed and reserved so far as gestures and bodily movements are concerned, yet sin grievously against decorum and gravity in their unfortunate habit of facial contortion | ground_truth | 1.000 | 0.174 |
| though animated and expressive in gestures and bodily movements, yet commendably maintain decorum and gravity through their fortunate lack of facial contortion. | negation | 0.000 | 0.092 |
| though the 'κνίση δ᾽ οὐρανῶν ἱκεν ἑλισσομένη περὶ καπνῶ; or for the harp hymns that wafted supplications to the sky from Mount Moriah | same_book | 0.000 | 0.226 |
| though not immediately human, have this much of human nature about them: that they are easily spoiled for use by prosperity | same_book | 0.000 | 0.083 |
| except when their expressions are essential tools of instruction. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.151 |
| but who, in the midst of pressing pastoral duties, may find it less immediately relevant. | anachronistic_gpt-oss:20b | 0.000 | 0.275 |

**Brier Score:** 0.1413


## Question 146

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** He may understand the end of the way of sensuality by looking at any old pleasure-seeker, Gray, and gap-toothed, and lean as death, mumbling the dainties that he can no longer [ 155 ]
enjoy, and glowering with bleared eyes at the indulgences which now mock him even while they tempt him. The goal of the path of covetousness may be discerned in the face of any old money-worshipper, keeping guard over his piles of wealth like a surly watch-dog; or, [masked clause describing a condition]. Inquire and learn; consider and discern.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if perchance he has failed, haunting the places where fortune has deceived him, like an unquiet ghost | ground_truth | 1.000 | 0.170 |
| if by any chance he has succeeded, delighting in the places where fortune has favored him, like a contented spirit | negation | 0.000 | 0.147 |
| if you want to guard them against the temptations of strong drink and the many shames and sorrows that go with it | same_book | 0.000 | 0.094 |
| if you want to take away the power of the gilded saloon and the grimy boozing-ken | same_book | 0.000 | 0.085 |
| or else, in his last days, gnawed by regret and fear of what will become of his fortune | manual_anachronistic_mistral-small:24b | 0.000 | 0.174 |
| provided that his longing for material excess has been replaced by a yearning for inner peace | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.329 |

**Brier Score:** 0.1442


## Question 147

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But the same gallon of water conveyed through an aqueduct and delivered in the heart of a great city represents a certain amount of wealth, because it has a value in relation to the wants of men. A tree growing in an inaccessible forest is not wealth. [masked sentence describing a tension or contrast] Now, the symbol and measure of wealth is money.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But a stick of timber which can be delivered in a place [ 27 ]
where men are building houses is a bit of wealth. | ground_truth | 1.000 | 0.031 |
| But a stick of timber which cannot be delivered anywhere where men are building houses is not worth anything. | negation | 0.000 | 0.060 |
| But perhaps you imagine that no one is in danger of making that mistake, no one is so foolish as to seek wealth merely for its own sake. | same_book | 0.000 | 0.111 |
| But when it is cut down and turned into lumber for a house, it becomes an asset to society. | anachronistic_mistral-small:24b | 0.000 | 0.544 |
| While the water's value is born of human desire, the tree's worth remains unclaimed until it is cut and turned into something useful. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.254 |

**Brier Score:** 0.2630


## Question 148

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** It is the acknowledgement that things which are, but are not right, need not have been, if we and our fellow-men had seen more clearly and followed more faithfully the guiding star of the good. And then, out of the judgement of regret, [129]
springs the deeper judgement of condemnation. If the failure in duty was not inevitable, [masked clause describing an inference or effect]. The false word, the unjust deed, the foul action, seen as a surrender to evil, appears hateful and guilty.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| then it was base | ground_truth | 1.000 | 0.031 |
| then it was noble | negation | 0.000 | 0.017 |
| so loathsome, that you can not deny it | same_book | 0.000 | 0.026 |
| so surely are our souls moving towards a certain type of character | same_book | 0.000 | 0.008 |
| then it is excusable | manual_anachronistic_mistral-small:24b | 0.000 | 0.331 |
| we must take responsibility for our failings | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.588 |

**Brier Score:** 0.2326


## Question 149

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But the point which concerns us now is simply this: The forth-reaching, questioning soul can never be satisfied if it touches only a dead wall in the darkness, if its seeking meets with the reply, "You do not know, and you never can know, and you must not try to know." This is agnosticism. It is only another way of spelling unhappiness. "Since Christianity is not true," wrote 

Ernest Renan, "nothing interests me, or appears worthy my attention." [masked sentence describing an inference or effect] But suppose Renan is mistaken.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| That is the logical result of losing the knowledge of spiritual things,-a life without real interest, without deep worth,—a life with a broken spring. | ground_truth | 1.000 | 0.065 |
| That is the logical result of gaining the knowledge of spiritual things—a life filled with real interest, with deep worth—a life with an unbroken spring. | negation | 0.000 | 0.038 |
| Therefore the ungodly shall not stand in the judgment:

Nor sinners in the congregation of the righteous. | same_book | 0.000 | 0.128 |
| Think of the result of existence in the man or woman who has lived chiefly to gratify the physical appetites; think of its real emptiness, its real repulsiveness, when old age comes, and the senses are dulled, and the roses have faded, and the lamps at the banquet are smoking and expiring, and desire fails, and all that remains is the fierce, insatiable, ugly craving for delights which have fled for evermore; think of the bitter, burning vacancy of such an end,—and you must see that pleasure is not a good haven to seek in the voyage of life. | same_book | 0.000 | 0.150 |
| This implies that for some individuals, the loss of faith can lead to existential despair and a sense of futility. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.304 |
| If Renan is mistaken, the world will no longer appear as a barren void but as a realm of wonder, and the soul’s longing will find a fitting fulfillment. | anachronistic_gpt-oss:20b | 0.000 | 0.314 |

**Brier Score:** 0.1841


## Question 150

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** As the worshipper in the 

Temple would observe the art and structure of the carven beams of cedar and the lilywork on the tops of the pillars the more [60]
attentively because they beautified the house of his God, so the man who has a religious faith in the Bible will study more eagerly and carefully the literary forms of the book in which the Holy Spirit speaks forever. We shall do wisely to consider and appreciate the poetical element in the Psalms. The comfort, help, and guidance that they bring to our spiritual life will not be diminished, [masked clause describing a tension or contrast].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but increased, by a perception of their exquisite form and finish | ground_truth | 1.000 | 0.117 |
| but corrupted, by a perception of their crude form and finish | manual_negation | 0.000 | 0.009 |
| but a harmony; not a song, but an ode | same_book | 0.000 | 0.010 |
| but also in the text, we can discern the work of the compiler, critic, and adapter, sometimes wise, but occasionally otherwise | same_book | 0.000 | 0.034 |
| but rather enhanced as we delve deeper into their artistic merit | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.576 |
| though some critics argue that the poetic form obscures doctrinal clarity. | anachronistic_gpt-oss:20b | 0.000 | 0.253 |

**Brier Score:** 0.1962


## Question 151

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** Then the first thing that makes it precious is that it answers our questions, and tells us the things that we must know in order to be happy. Christianity is a revealing religion, a teaching religion, a religion which conveys to the inquiring spirit certain great and positive solutions of the problems of life. It is not silent, nor ambiguous, nor incomprehensible in its utterance. It replies to our questions with a knowledge which, [masked clause conceding a limit or exception]. It tells us that this "order of nature, which constitutes the world's experience, is only one portion of the total universe."

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though limited, is definite and sufficient | ground_truth | 1.000 | 0.035 |
| though abundant, remains uncertain and inadequate | negation | 0.000 | 0.003 |
| even though its pulsations sometimes seemed a little slow and heavy | same_book | 0.000 | 0.021 |
| though our ideal of future character is so often hidden from us, overlooked, forgotten, it is always there, and always potently, though unconsciously, shaping our course in life | same_book | 0.000 | 0.035 |
| though it may not always be comprehended by our finite minds | manual_anachronistic_mistral-small:24b | 0.000 | 0.428 |
| though it may not answer every question with absolute certainty | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.479 |

**Brier Score:** 0.2243


## Question 152

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But there is a reason, after all, and a very profound reason, why we should sometimes put this question of our desired haven after death in a distinct form, and why we should [51]
try to give a true and honest answer to it, with an outlook that goes beyond the grave. [masked sentence describing a cause or reason] Men say that the future life is only a possibility, or at best a probability, and that it is foolish to waste our present existence in the consideration of problems to which the only answer must be a "perhaps," or "I hope so," or "I believe so."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It is because the answer will certainly determine our conduct now, and there is every reason to believe that it will affect the result hereafter. | ground_truth | 1.000 | 0.151 |
| It is because the answer may not influence our conduct now, and there is little reason to believe that it will impact the result hereafter. | negation | 0.000 | 0.056 |
| And it is just because Christianity contains such doctrines that it satisfies the need of man. | same_book | 0.000 | 0.009 |
| It spreads because human hearts are lying fallow and ready to welcome the seeds of all kinds of weeds. | same_book | 0.000 | 0.021 |
| It is because our thoughts and actions in this life are profoundly influenced by what we believe about the next. | anachronistic_mistral-small:24b | 0.000 | 0.417 |
| Because the pursuit of a clear understanding of the afterlife grounds our present actions in a moral framework that transcends mere speculation. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.347 |

**Brier Score:** 0.1700


## Question 153

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** It is not in the least vague. It is only free; it has the power to embody itself in a thousand forms without changing its character. Those who seek it know what it means, however it may be expressed. It is real and genuine and satisfying. There is nothing beyond it, [masked clause describing a cause or reason]. It is the translation, through many languages, of the true, divine purpose of all the work and labour that is done beneath the sun, into one final, universal word.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| because there can be no higher practical result of effort | ground_truth | 1.000 | 0.025 |
| because there can be no lower futile outcome of effort | negation | 0.000 | 0.005 |
| as His was, being spent in doing good, and refreshed by the sense of God's presence and approval | same_book | 0.000 | 0.048 |
| because it has a value in relation to the wants of men | same_book | 0.000 | 0.015 |
| because it fulfills an innate human desire to seek meaning. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.066 |
| for it is the ultimate aim of all human striving | anachronistic_gpt-oss:20b | 0.000 | 0.842 |

**Brier Score:** 0.2777


## Question 154

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Never before had she been happier in this world; never felt before in her life as she had felt that day. Think of it all! From first to last she remembered everything, had but to close her eyes to see everything. And Ted had spoilt it all! She had done no harm, no harm. Why had he been so foolish? [masked sentence describing a cause or reason] Did he make love to ye?

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 'Twas jealousy. | ground_truth | 1.000 | 0.031 |
| It was generosity. | manual_negation | 0.000 | 0.001 |
| Was it because of the old days, the old happenings? | same_book | 0.000 | 0.043 |
| He had seen her talking to another man. | manual_anachronistic_mistral-small:24b | 0.000 | 0.566 |
| Because he had fallen for another. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.358 |

**Brier Score:** 0.2778


## Question 155

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Of course that was out of the question; nor could I oblige him the following morning; nor was I in the humour to soil my hands on his jacket a day or two after when I met him in the fields; nor, indeed, have 

I felt disposed to accept a couple of illspelt challenges he has forwarded me by letter. Still, he is a nuisance, I must say." "Aw," said Nan again. "It's hard to know how to deal with such a fellow. Excuse me, Nan, for calling him that, [masked clause describing a tension or contrast]. He is so persistent, absurdly wrong-headed.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but I can't help it | ground_truth | 1.000 | 0.176 |
| but I can resist | manual_negation | 0.000 | 0.002 |
| but what of Frank himself | same_book | 0.000 | 0.000 |
| but believe me it is not absurd | same_book | 0.000 | 0.013 |
| though I admire his tenacity | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.728 |
| though he claims sincerity, his motives remain doubtful | anachronistic_gpt-oss:20b | 0.000 | 0.081 |

**Brier Score:** 0.2028


## Question 156

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** "The boys from the market," said John, diving for his hat. "Faith, it's early they'll be. Come, Nan, me girl; come away, Sarah. Ye'll forgive us runnin' off, Frank, me son? But the poor must earn their bread be the sweat o' their brow. Ay, ay." [masked sentence describing an inference or effect] All hurried down to the pier; there manned the big ferry cot and, Nan and 

Frank at one oar, Sarah at the other, John standing by the steering sweep, set her course for the Lis-
THE BARRYS.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| So the feast broke up. | ground_truth | 1.000 | 0.001 |
| So the feast began. | negation | 0.000 | 0.001 |
| So there ye are, faith; there ye are." | same_book | 0.000 | 0.015 |
| So Frank pulled up and helped himself; and the cups rattled on the saucers, and the spoons clinked merrily, and John talked and talked, and Sarah minced and watched, and Nan glanced at Frank, and Frank admired Nan; and, suddenly, across the waters came a cry from the Lismahee side, a long shrill Ahoy-y-y. | same_book | 0.000 | 0.489 |
| The family's urgency was palpable as they scrambled to board. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.494 |
| They all felt duty’s weight. | anachronistic_gpt-oss:20b | 0.000 | 0.001 |

**Brier Score:** 0.2471


## Question 157

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Bless his heart, he shall grow up a credit to the name. The best of everything he'll have, the best I can give him. That is my object in life now. I have also sent Marian her money, enclosing it in a letter explaining how it came into my hands. I said little else, [masked clause conceding a limit or exception].

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though I restrained many things | ground_truth | 1.000 | 0.004 |
| though I let many things loose | negation | 0.000 | 0.003 |
| even if it is not well over | same_book | 0.000 | 0.141 |
| even though all the right was on her side and all the wrong admittedly on his, was, as Frank himself thought, inevitable; just as it was inevitable, in the natural reaction and stress of thought and feeling, that she should now believe more than was true of Frank and his misdeeds, and express her beliefs recklessly, and say things she must afterwards regret | same_book | 0.000 | 0.189 |
| knowing she would not welcome more | anachronistic_mistral-small:24b | 0.000 | 0.091 |
| but I cannot guarantee that all will go smoothly | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.572 |

**Brier Score:** 0.2306


## Question 158

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** It was almost touching, his genuine pleasure; it was a lesson in manners to see how tactfully he asked after Frank's welfare, nor showed his real concern that a Barry should turn out so poorly, such a crooked bundle of skin and bones, with, aw, such a woful face. And was Mr. Frank staying long? Aw, only for a month or so; sure that was no time at all. [masked sentence describing a tension or contrast] Anyway, might the sun shine on him all the days he was in Ryfield; "an' sure I hope, sir," said James, turning to Hugh, "ye'll be tellin' Sally to feed him o' the best."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But, sure, maybe he couldn't spare longer, so busy he must be over in big London. | ground_truth | 1.000 | 0.030 |
| But, sure, maybe he could spare longer, so free he must be over in big London. | negation | 0.000 | 0.009 |
| But sure that kind o'-o' feedin' would choke ye." | same_book | 0.000 | 0.003 |
| But let me tell ye, John Butler," cried 

Hugh, turning on the hillside; "if by any chance what you're wishin' an' he's playin' the fool for should come to pass- Whoo! | same_book | 0.000 | 0.035 |
| Yet there was an undercurrent of unease, as if James's politeness was a thin veil over his true feelings. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.689 |
| Yet the boy's gaunt silhouette seemed to loom larger than any other in the room. | anachronistic_gpt-oss:20b | 0.000 | 0.234 |

**Brier Score:** 0.2453


## Question 159

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** D'ye think, says he, if iver I'm put out of 

Inishrath... Ach," cried Ted, walking on again, "it's sickenin'. Who the blazes wants to turn him
INISHRATH. 83 out? The tyrants o' landlords, says he, the infernal tyrants o' landlords. Why, I tell ye, [masked clause describing a condition].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if the landlord had his rights it's on the parish John'd be years ago | ground_truth | 1.000 | 0.032 |
| if the landlord were powerless, John would still be there today | negation | 0.000 | 0.021 |
| if only he had lived, lived to reap some reward of his labours | same_book | 0.000 | 0.116 |
| if Hugh had no worse than that to say he might keep on till kingdom come | same_book | 0.000 | 0.086 |
| they're squeezin' us dry with their high rents and evictions | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.594 |
| if the landlord's iron hand were to grip us again, we'd emigrate and become rich in America | manual_anachronistic_gpt-oss:20b | 0.000 | 0.151 |

**Brier Score:** 0.2226


## Question 160

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Love of truth, country, river, cushat, mousie, daisy, lassie (be she Mary, Eliza, or Jean),—that was 

Burns's literary biography. Love means melancholy; and it is quite beyond credence persistently shadows hang over all Burns wrote, until you take his poems and go over them at a sitting. Rollicking he seems to be, [masked clause describing a tension or contrast]. The fear of parting is on his meeting with Mary.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but sad at heart you will always find him | ground_truth | 1.000 | 0.066 |
| but joyful in spirit you will always find him | negation | 0.000 | 0.043 |
| but his love speaks passion at the hour | same_book | 0.000 | 0.001 |
| even when writing about the most joyful moments | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.046 |
| though his verses brim with gaiety, his heart is ever in sorrow | anachronistic_gpt-oss:20b | 0.000 | 0.844 |

**Brier Score:** 0.3178


## Question 161

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** How events trample on each other, like cavalry horses rushing to battle! What a story-teller Weyman is! We shall lis ten many years to hear more stirring and strengthening tales told us than "A Gentleman of France" and "Under the Red Robe." What a story-teller Doyle is, [masked clause describing a condition or proviso] To my mind "Micah Clarke" is one of the strong historical romances of the last decade.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if you listen to his "White Company" and to "Micah Clarke!" | ground_truth | 1.000 | 0.031 |
| yif you avoid listening to his "White Company" and "Micah Clarke." | manual_negation | 0.000 | 0.019 |
| if we would comprehend the achievements of generals and the utterances of kings | same_book | 0.000 | 0.010 |
| if we be not furnished with an explanatory clause | same_book | 0.000 | 0.003 |
| if he continues to weave his narratives with such masterful skill | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.708 |
| provided that his tales are as vivid as his characters | anachronistic_gpt-oss:20b | 0.000 | 0.228 |

**Brier Score:** 0.2489


## Question 162

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** He was a creature of moments. Laughter or weeping, no one could tell which should proceed from this minstrel. A big heart, a feverish passion, a lust for wine and women, a manhood burned out like a candle to the socket,-this is Burns. He was a man with his full share of weakness and 14
and Other Essays wickedness, but with a large endowment of genius, nobility, and vision; and we pass his aberrancies by tenderly, [masked clause describing a cause or reason]. With Burns the world has forgotten much.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| because of the manhood he did possess | ground_truth | 1.000 | 0.013 |
| because of the cowardice he showed | negation | 0.000 | 0.041 |
| for Burns is the greatest writer of dialect | same_book | 0.000 | 0.010 |
| because new beauty reveals itself at every step | same_book | 0.000 | 0.007 |
| because of the brilliance of his poetry | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.766 |
| for the sake of his sublime artistry | anachronistic_gpt-oss:20b | 0.000 | 0.165 |

**Brier Score:** 0.2649


## Question 163

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Such rivalry as existed between Genoa and Venice burned hot between the country which gave William birth and the one over which he swayed scepter as king. In ports even at the antipodes the 

Dutch and English merchantmen were competitors. [masked sentence describing an inference or effect] William the Great of Englaud 117 

William belonged to that nation; and every sign of love for his country or his countrymen seemed to their distempered vision a slight to England and Englishmen.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Englishmen were therefore jealous of any favor shown to their commercial rivals. | ground_truth | 1.000 | 0.108 |
| Englishmen were therefore proud of any favor shown to their commercial rivals. | negation | 0.000 | 0.049 |
| It thus arose naturally, if not wisely, that the foreign troops of William's guard were endured with distrust, and, in 1697, over the manifest protest of the king and in spite of his service, they were compelled to return to Holland. | same_book | 0.000 | 0.114 |
| So, in the light of history, England's cause was not altogether hopeless. | same_book | 0.000 | 0.020 |
| This intense rivalry often led to conflicts and power struggles between the two nations. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.601 |
| Thus the rivalry inflamed a fervent sense of national pride among the populace. | anachronistic_gpt-oss:20b | 0.000 | 0.107 |

**Brier Score:** 0.1973


## Question 164

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Humanity must bear the imputation of being unclean in body, as in spirit. And in this Jew's Ghetto are hints of comedy and bits of tragedy, and boisterous merrymaking native to all estates. Poverty is no dethronement of delight. Heroisms, too, are here. Souls are the tenting-grounds of the heroic. No life is cut off from the possibility of nobleness; and the revelation of an old father, conscious that his presence jeopards his son's happiness; who feigns a brother in
far-off America, who has sent for him to share his wealth, and so leaves this Ghetto, [masked clause conceding a limit or exception]. Beyond dispute we are debtors to this guide, who has led us along so untrod, novel, and fascinating a path.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though to leave is like tearing out his living heart, and turns gray face toward an unknown land,such sacrifice renews the courage of us all | ground_truth | 1.000 | 0.023 |
| though to stay is to embrace a stagnant life in familiar lands, and keeps youthful vigor away from us all | negation | 0.000 | 0.004 |
| though the contribution is one we would not willingly let die | same_book | 0.000 | 0.028 |
| though in him it arose from the many-sidedness of genius | same_book | 0.000 | 0.022 |
| but with a heavy heart, knowing he will never see his son again | anachronistic_mistral-small:24b | 0.000 | 0.819 |
| though this departure may seem a liberation, it is still bound by the invisible chains of memory | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.104 |

**Brier Score:** 0.2729


## Question 165

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** He was not bad, weak rather. Sinned, he had. He and Hester were joint criminals, she bearing her shame before the world; he canonized by that same world. Conscience cried aloud, "Bear shame with her;" and his spirit cried, "How can I? How can I?" [masked sentence describing a tension or contrast] Its speech never silenced.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But conscience spake on. | ground_truth | 1.000 | 0.138 |
| But conscience held silent. | negation | 0.000 | 0.117 |
| But the question need not delay for answer. | same_book | 0.000 | 0.034 |
| But Daniel Deronda is the Jew as modern gentleman, and is altogether admirable. | same_book | 0.000 | 0.100 |
| Yet, his public reputation whispered otherwise. | anachronistic_mistral-small:24b | 0.000 | 0.345 |
| He celebrated, she mourned. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.267 |

**Brier Score:** 0.1597


## Question 166

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Worth, manliness, courage, and virtue were his; but these, men could not see, and
and Other Essays so it is easy to discover that the geniality which had been so marked in the manner of Charles, but was so lacking in that of William, should have brought a contrast to the king's hurt. Men are easily deceived. They do not pierce beneath the thin disguise of externality to discover genuine and unapproachable merit. [masked sentence describing a cause or reason] He loaded Portland with honors.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Another chief cause of William's unpopularity was his partiality to his own countrymen. | ground_truth | 1.000 | 0.436 |
| Another chief cause of William's popularity was his stinginess. | manual_negation | 0.000 | 0.063 |
| It was the cause of our common humanity. | same_book | 0.000 | 0.023 |
| Charles's lack of geniality, which was an attribute men valued too highly, was the cause. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.161 |
| Because the king's heart had been so moved by Portland's unwavering fidelity, he resolved to bestow upon it a bounty of honors. | anachronistic_gpt-oss:20b | 0.000 | 0.317 |

**Brier Score:** 0.0898


## Question 167

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But if a person has in his possession trout less than six inches long he is, all the time he has them in his possession, violating the provisions of 5275 P. S. Therefore, it follows that if the warden has reasonable cause to believe that a person has in his possession a trout less than six inches long he may, under the authority of Sec. 5271, arrest him without a warrant. The application of this law must be made in view of the nature of the crime itself, and in view of the means of securing evidence showing the commission of crime, [masked clause describing a cause or reason]. I believe that if the warden, disclosing his office, sees a person under such circumstances as to indicate that the person is in the possession of trout caught in the waters of this state, that is, if he sees him coming from a brook with a fish basket over his shoulder and a fish rod in his hand, he has the right to ask that person to show him the contents of the basket and to show him all the fish
in his possession.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for if the warden could not arrest a man personally until he was certain that he had in his possession trout less than six inches long it would practically nullify the law, for anyone breaking the law will naturally conceal his offense | ground_truth | 1.000 | 0.167 |
| for if the warden must arrest a man personally only when he is certain that he has in his possession trout over six inches long it would practically enforce the law, for anyone following the law will naturally reveal their compliance | negation | 0.000 | 0.073 |
| for the officer as the prisoner's keeper | same_book | 0.000 | 0.006 |
| for sheriffs have such authority by statute to serve criminal process | same_book | 0.000 | 0.008 |
| if there is probable cause to suspect that the person has violated fishing regulations. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.378 |
| particularly when the suspect is in a location where fishing is prohibited or when his conduct indicates recent fishing activity, such as carrying a fish basket or fishing rod | anachronistic_gpt-oss:20b | 0.000 | 0.368 |

**Brier Score:** 0.1628


## Question 168

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But anything which subjects a person to the actual control or will of another constitutes an arrest and imprisonment, whether it is physical control, locking the door of a room in which the arrested person is found, or a voluntary submission to words of arrest. An officer effects an arrest of a person whom he has authority to arrest, by laying his hand on him for the purpose of arresting him, though he may not succeed in stopping or holding him. (Mere words spoken to one are not an arrest of him; there must be something physical, [masked clause conceding a limit or exception]

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though it is enough if the party arresting touch the other, "even with the end of his finger." | ground_truth | 1.000 | 0.077 |
| though contact alone is insufficient for an arrest | negation | 0.000 | 0.198 |
| although manual seizure is not always necessary, there must be that, or its equivalent in some sort of personal coercion | same_book | 0.000 | 0.049 |
| although this is not necessary where the person arrested must have notice from the circumstances of the case that his arrest is lawful | same_book | 0.000 | 0.086 |
| unless the person explicitly acknowledges and submits to the arrest | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.298 |
| unless the person is under a warrant of arrest or is in a place of detention, in which case a verbal declaration by an authorized officer may constitute an arrest | anachronistic_gpt-oss:20b | 0.000 | 0.292 |

**Brier Score:** 0.1793


## Question 169

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** (Extracts from a pamphlet)

By R. W. WILLIAMS, JR., 

Assistant, Biological Survey. For several hundred years the enforcement of criminal laws of all kinds in this country has been intrusted to sheriffs, constables, and police officers, and until the middle of the nineteenth century this method was considered satisfactory. [masked sentence describing a tension or contrast] The origin of the term "warden" in relation to game is somewhat obscure, but it was probably adopted in analogy to church and wood wardens in England, where the word first came into use.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But with the growing demand for more stringent enactments for the preservation of game and the increasing complexity of statutes for this purpose it was found no longer practicable to include the burden of enforcing them among the duties devolving upon general officers, and their enforcement has consequently been intrusted to special officials, usually called game wardens. | ground_truth | 1.000 | 0.139 |
| But with the growing demand for more lenient enactments for the preservation of game and the decreasing complexity of statutes for this purpose it was found no longer practicable to exclude the burden of enforcing them among the duties devolving upon general officers, and their enforcement has consequently been intrusted to special officials, usually called game wardens. | negation | 0.000 | 0.079 |
| However, it should be remembered that game laws and game wardens are of comparatively recent origin in the United States, and that only a short time ago the popular idea respecting fish and game was that wherever found they were almost as much the property of the individual citizen as the air we breathe. | same_book | 0.000 | 0.088 |
| However, this may be, a game warden is now generally understood to be an officer charged with the enforcement of laws for the protection of game and fish. | same_book | 0.000 | 0.162 |
| However, as society evolved and new challenges emerged, particularly with the rise of industrialization and urbanization, traditional law enforcement methods began to show limitations. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.405 |
| However, the protection of wildlife and game, unlike ordinary criminal statutes, demanded a specialized approach, as the traditional law‑enforcement bodies were ill‑prepared to address the unique challenges posed by poaching and the preservation of natural resources. | anachronistic_gpt-oss:20b | 0.000 | 0.126 |

**Brier Score:** 0.1602


## Question 170

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


## Question 171

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** THE WARDEN'S GENERAL MOVEMENTS 

Quite often we hear a warden complain that the regular violators in his territory keep so well posted on his general movements and plans from day to day that his success in apprehending them is thus seriously handicapped. This is true in many cases, [masked clause describing a tension or contrast]. It is the fate of all wardens, and the really clever ones are only stirred to increased efforts by this difficulty.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but usually the warden is inclined to overestimate this obstacle | ground_truth | 1.000 | 0.159 |
| but usually the warden is inclined to underestimate this obstacle | negation | 0.000 | 0.062 |
| but for general work and without local assistance and co-operation the shrewdest warden in the country will be an utter failure | same_book | 0.000 | 0.080 |
| however, the office of game warden is a difficult one to fill, and it is the duty of every good citizen to lend this important public servant every assistance and encouragement in the discharge of his duties | same_book | 0.000 | 0.293 |
| yet they find it equally difficult to keep their own movements from becoming predictable | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.279 |
| yet the most seasoned wardens discover that this same vigilance often drives offenders into increasingly erratic and unpredictable patterns | anachronistic_gpt-oss:20b | 0.000 | 0.126 |

**Brier Score:** 0.1496


## Question 172

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** While one is conversing with the occupants of a camp his dog will be extremely busy searching every nook and corner for game or fish, and if there is any such there it is very certain to be brought to his master's attention by his faith-
ful dog, and the latter don't require any special training to render this service, either. It is his nature and instinct to do so. There is also a case where a warden's pointer dog discovered a large shipment of game birds in a box at a railway station. These birds were very cleverly secreted, but they could not escape the fine nose of the pointer and he "made game" as soon as he drew near them, [masked clause describing an inference or effect]. But there are "dogs and dogs.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that his master was able to seize the game and apprehend the culprits | ground_truth | 1.000 | 0.191 |
| so that his master could not prevent the game from escaping nor catch the culprits | negation | 0.000 | 0.013 |
| so valuable for their fur, are not subject of larceny." | same_book | 0.000 | 0.001 |
| so it is presumed in choosing a dog for an assistant the warden will choose wisely, with his special needs always in view | same_book | 0.000 | 0.018 |
| alerting the warden to their presence. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.600 |
| which promptly alerted the warden, resulting in the immediate seizure of the illegal shipment | anachronistic_gpt-oss:20b | 0.000 | 0.177 |

**Brier Score:** 0.1745


## Question 173

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** When such is found, if a part of the deer carcass was missing, the warden will make all haste to procure a search warrant and search the place before the meat has been consumed. If the process of securing a search warrant requires too much valuable time, then he will attempt to enter the place without such warrant by subterfuge. This can often be done without the officer exceeding his authority. For instance, [masked clause describing a condition]. Or he may summon the inmates and request their permission to search the place, and may do so with the occupant's, or his agent's, consent.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if he finds the doors or windows open and no one to answer his knock, he may enter | ground_truth | 1.000 | 0.086 |
| if he finds the doors and windows securely closed and someone promptly answers his knock, he should leave | negation | 0.000 | 0.020 |
| if a part of the deer carcass was missing, the warden will make all haste to procure a search warrant and search the place before the meat has been consumed | same_book | 0.000 | 0.549 |
| if the offender escapes and takes refuge in his own or another house, the officer is justified in breaking doors to retake him | same_book | 0.000 | 0.040 |
| for example if the wardens have reasonable cause to believe that evidence of illegal activity is being destroyed | anachronistic_mistral-small:24b | 0.000 | 0.158 |
| if the carcass is located in a private dwelling where the occupant has given prior consent or is absent, the warden may lawfully enter without a warrant by subterfuge | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.147 |

**Brier Score:** 0.1974


## Question 174

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** We ourselves have not forgotten, and never can forget the hundreds of thousands of precious lives that were spent in order that there might be written in our constitution, "Neither slavery nor involuntary servitude except as a punishment for crime shall exist within the United States or any place subject to their jurisdiction." Wisely, therefore, do we celebrate anniversaries like these, that we may renew our allegiance to the great principles of constitutional liberty, and resolve that what cost our ancestors so dear shall not lightly be sacrificed by us. It is natural that we should be dazzled by the wonderful growth which has sprung from the seed planted at Jamestown, that we should be intoxicated by a material prosperity unexampled in the history of the world, and by the evidences of enormous national wealth and strength which surround us, [masked clause describing a tension or contrast]. We are here to honor those who laid deep and strong the foundations of our Commonwealth, because we know that to the principles which they adopted in framing our government we
owe the liberty that has made our wonderful progress possible.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but we shall lose the whole meaning of this celebration-we shall fail completely to learn its lesson-if we give ourselves up to the contemplation of our past and the glorification of ourselves | ground_truth | 1.000 | 0.046 |
| but we shall preserve the entire meaning of this celebration—we shall fully grasp its lesson—only if we give ourselves up to the contemplation of our past and the glorification of ourselves | manual_negation | 0.000 | 0.036 |
| but it may be not unreasonably said that the preservation of the States, and the maintenance of their governments, are as much within the design and care of the Constitution, as the preservation of the Union and the maintenance of the National Government | same_book | 0.000 | 0.369 |
| but simply the enactment of a law, a fundamental law, which defined the powers of the government and secured the rights of the citizen in this great Commonwealth | same_book | 0.000 | 0.053 |
| yet it is essential to remember the struggles and sacrifices of those who fought for freedom. | anachronistic_mistral-small:24b | 0.000 | 0.348 |
| yet, amid this prosperity, the shadows of past injustices linger, reminding us that freedom is a continual struggle | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.149 |

**Brier Score:** 0.1990


## Question 175

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Against these theories by which our rulers of to-day seem to claim for themselves peculiar wisdom let us oppose the words of Washington, that greatest of Virginians, in his Farewell Address:- "If, in the opinion of the people, the distribution or modification of the constitutional powers be in any particular wrong, let it be corrected by an amendment in the way which the Constitution designates. But let there be no change by usurpation, for, [masked clause conceding a limit or exception] Let us oppose the language of the Supreme Court whose unanimous opinion has just been expressed in these words:— "The proposition that there are legislative powers affecting the nation as a whole which belong to, although not expressed in, the grant of powers, is in direct conflict with the doctrine that this is a Government of enumerated powers.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though this in one instance may be the instrument of good, it is the customary weapon by which free governments are destroyed." | ground_truth | 1.000 | 0.088 |
| though this in one instance may be the instrument of ill, it is the customary shield that preserves free governments | negation | 0.000 | 0.012 |
| though, if we are to have usurpation, it is more in accord with the genius of our institutions to have it come through the action of the legislature, whose duty it is to make the law, rather than through the action of the President, whose duty it is to obey and execute it | same_book | 0.000 | 0.128 |
| although not expressed in, the grant of powers, is in direct conflict with the doctrine that this is a Government of enumerated powers | same_book | 0.000 | 0.675 |
| for though it may seem expedient at some point to act beyond our constitutional bounds. | anachronistic_mistral-small:24b | 0.000 | 0.039 |
| unless it is indispensable to safeguard the common good or to avert a threat to the nation’s security. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.058 |

**Brier Score:** 0.2180


## Question 176

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Why is it that the President, whose ideas on most subjects are accessible to his countrymen, has preserved such an absolute silence on the burning question of tariff reform, and has, indeed, displayed such fierce indignation at the mere statement that he had expressed himself on the subject? It is because he fears that any action in this direction will divide his party. [masked sentence describing a cause or reason] The politicians and the protected interests have formed an unhallowed partnership, to which the manufacturers have contributed cash in the guise of campaign contributions and the politicians have contributed time and speeches.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It is because the Republican party owes its power, in large part at least, to the support of the manufacturers, and depends for the sinews of war on the “fat fried out of" them, to use the phrase of one who was high in the party councils. | ground_truth | 1.000 | 0.141 |
| It is because the Republican party owes its weakness, in large part at least, to the lack of support from the manufacturers, and relies not at all for the sinews of war on the “fat fried out of" them, to use the phrase of one who was high in the party councils. | negation | 0.000 | 0.101 |
| It is precisely because the people have such confidence in the President's high purpose and trust him so implicitly that such propositions coming from him are full of danger. | same_book | 0.000 | 0.054 |
| This is due to the complex web of political alliances and monetary influences at play. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.548 |
| He is restrained by the dread that any movement toward tariff reform would fracture his own party, thereby threatening the unity he seeks. | anachronistic_gpt-oss:20b | 0.000 | 0.157 |

**Brier Score:** 0.2152


## Question 177

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** We are here to honor those who laid deep and strong the foundations of our Commonwealth, because we know that to the principles which they adopted in framing our government we
owe the liberty that has made our wonderful progress possible. [masked sentence describing a tension or contrast] The past is indeed glorious, but we are living in the present, and on our course in that present depends our country's future.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But, as we meet to commemorate their acts, it becomes us to inquire how their work is faring in our hands, how we are preserving and maintaining the heritage of principle which they handed down to us. | ground_truth | 1.000 | 0.106 |
| But, as we gather to forget their deeds, it becomes us to ignore how their legacy has faded in our hands, how we are squandering and neglecting the inheritance of principle which they bequeathed to us. | negation | 0.000 | 0.039 |
| But there is a far more important question, which underlies the whole discussion and upon which men should not differ. | same_book | 0.000 | 0.095 |
| Yet, while we celebrate their achievements, we must also confront the challenges of a rapidly changing world and the evolving needs of our citizens. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.528 |
| Yet the same principles that once steadied us now confront us with new trials, demanding that we adapt while remaining true to our founding ideals. | anachronistic_gpt-oss:20b | 0.000 | 0.232 |

**Brier Score:** 0.2284


## Question 178

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


## Question 179

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Let us, as citizens of our common country, resolve that they shall be obeyed by high and low alike, for only through such obedience can our freedom be preserved. Let us treasure the counsel so recently given at Jamestown by the eminent statesman who now represents England in this country, Mr. Bryce. “Cherish alike and cherish together liberty and law. They
are always inseparable. Without liberty there is no true law, [masked clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| because law sinks into being merely the will of an arbitrary ruler or a selfish class, and ceases to be the will of the whole community | ground_truth | 1.000 | 0.152 |
| because law sinks into being the collective will of the community, instead of the wfree and unbounded whim of an arbitrary ruler | manual_negation | 0.000 | 0.021 |
| as citizens of our common country, resolve that they shall be obeyed by high and low alike, for only through such obedience can our freedom be preserved | same_book | 0.000 | 0.711 |
| because law without freedom becomes arbitrary edict that enslaves the people, eroding the very foundations of justice for all | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.115 |

**Brier Score:** 0.3096


## Question 180

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** of the popular vote, but sixty-two per cent. of the electoral votes, and his party had a very large majority in the House. These illustrations might be multiplied indefinitely. Do such figures show that the result of Federal elections expresses the people's will? How often have the Senate and the House been controlled by different parties, [masked clause describing an inference or effect]?

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that no legislation on burning questions was possible | ground_truth | 1.000 | 0.041 |
| so that legislation on burning issues could proceed | negation | 0.000 | 0.029 |
| so that his constituents may thus practically be disfranchised | manual_same_book | 0.000 | 0.028 |
| leading to legislative gridlock and inefficiency | anachronistic_mistral-small:24b | 0.000 | 0.745 |
| which indicates that the Senate and House can be governed by different parties, leading to conflicting legislative priorities. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.157 |

**Brier Score:** 0.3002


## Question 181

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Is the Senate a more efficient interpreter of the popular will? How much are the people consulted in the choice of senators? Is it mere accident that so many of them are conspicuous mainly for their wealth and the qualities by which wealth is acquired? If we turn to the West, shall we say that Senator Clark was chosen by Montana for his ability as a statesman, or, [masked clause describing a condition]? Was

Quay the free choice of Pennsylvania, or Dryden of New 

Jersey?

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if we look nearer home, must we assume that Senators Platt and Depew represent the character and purpose of New York | ground_truth | 1.000 | 0.182 |
| if we look beyond our borders, can we dismiss that Senators Platt and Depew embody the spirit and intent of New York | negation | 0.000 | 0.220 |
| if not to control, legislation by Congress | same_book | 0.000 | 0.020 |
| if the senator has earned the trust of the electorate through a record of honest and diligent public service | manual_anachronistic_gpt-oss:20b | 0.000 | 0.578 |

**Brier Score:** 0.2629


## Question 182

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** In the spaces at the ends of the tables and in the aisles under the bowls the waste jars stand unobtrusively. Gas is supplied through fixtures arranged along the central portion of the tables at the back of the working spaces, but the controlling cocks are along the front, just under the overhanging edge of the table top. This arrangement permits the utilization of wider space, [masked clause describing a cause or reason]. Instead of the ordinary retort and filter stands, the supporting rods for the iron rings of the former and the porcelain-lined rings of the latter are screwed securely into brass sockets set in the wood and flush with the surface.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| inasmuch as the control of the gas is accomplished without the interference with apparatus upon the table and without inconvenient reaching | ground_truth | 1.000 | 0.129 |
| insofar as the control of the gas requires interaction with apparatus on the table and entails awkward stretching | negation | 0.000 | 0.083 |
| for coke for high temperatures, some of which are supplied with an airblast pipe 90 millimetres diameter | same_book | 0.000 | 0.040 |
| making it more convenient to handle them while working at the table | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.325 |
| by keeping the gas fittings and controls out of the main working area, the benches remain clear for the chemists | anachronistic_gpt-oss:20b | 0.000 | 0.423 |

**Brier Score:** 0.2104


## Question 183

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** Industrial, sanitary, and organic laboratory practice follow in the third and fourth years. While there is a certain prescribed course of study and work in the separate departments of chemistry, which all regular students must pursue; there is allowed great latitude in choice of subjects in the third and fourth years. Effort is made to develop self-reliance in the student, [masked clause describing an inference or effect]. To this end he is required to make investigations, involving original research and reference to the appropriate literature in English, French, and German.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that he may be fitted to make his way without assistance | ground_truth | 1.000 | 0.098 |
| so that he remains unfit to navigate independently | negation | 0.000 | 0.006 |
| so as to be able to reproduce substances as described in technical journals and in letters patent | same_book | 0.000 | 0.018 |
| so that it is possible to introduce two sets of students into the laboratory at different hours, each student having his own apparatus under lock and key | same_book | 0.000 | 0.112 |
| such that students can apply their knowledge independently | anachronistic_mistral-small:24b | 0.000 | 0.707 |
| so that he may approach complex experimental tasks with initiative and critical judgment | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.060 |

**Brier Score:** 0.2215


## Question 184

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** Instead of the ordinary retort and filter stands, the supporting rods for the iron rings of the former and the porcelain-lined rings of the latter are screwed securely into brass sockets set in the wood and flush with the surface. [masked sentence describing an inference or effect] Two shelves hold reagent bottles for the common acids, ammonia, and ammonia salts, the remaining reagents being relegated to shelves in the embrasures of the windows.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Thus held the rod is firm, while easily removable, and the level space about the rod permits a more advantageous disposal of apparatus than is possible when the rod is held in a movable platform. | ground_truth | 1.000 | 0.038 |
| Thus held the rod is loose, and may swing widely across the laboratory without warning. | manual_negation | 0.000 | 0.003 |
| The muffles thus face the light, and the brick wall protects the analyst from the heat. | same_book | 0.000 | 0.053 |
| Ten students can thus work here at once. | same_book | 0.000 | 0.062 |
| This arrangement ensures stability and easy access during experiments. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.514 |
| This design not only guarantees the stability of the apparatus during vigorous experiments but also minimizes the risk of accidental spills and contamination, thereby enhancing overall laboratory safety and ensures that delicate measurements remain precise. | anachronistic_gpt-oss:20b | 0.000 | 0.329 |

**Brier Score:** 0.2174


## Question 185

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** BASEMENT FLOOR. The basement is occupied as indicated in Plate IV. The laboratory for organic chemistry measures 40 by 39 feet by 12 feet 6 inches, and is fitted in general like the laboratory for analytical chemistry on the second floor. [masked sentence describing a tension or contrast] The drainage for this floor is carried away in earthen pipes laid in graded trenches built in masonry, cemented, and covered with iron plates level with the asphalt floor which covers the entire basement.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The sinks, however, are of iron instead of porcelain, and the bottoms of the draft chambers are sinks instead of plain soapstone tables. | ground_truth | 1.000 | 0.066 |
| The sinks, however, are exactly like the second floor laboratory, and are flush with the floor. | manual_negation | 0.000 | 0.111 |
| No two rooms, however, use the same flue. | same_book | 0.000 | 0.100 |
| But it is intended that this room shall also offer facilities for work to advanced students engaged in inorganic research. | same_book | 0.000 | 0.103 |
| However, unlike its upstairs counterpart, it is noticeably darker due to the lack of windows. | anachronistic_mistral-small:24b | 0.000 | 0.375 |
| Yet the lab’s bright, ventilated interior stands in stark contrast to the basement’s cool, damp environment. | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.246 |

**Brier Score:** 0.1845


## Question 186

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


## Question 187

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** It has been pointed out that the blockade of 1902 was not originally instituted on account of Venezuela's failure to pay debts, but to obtain redress for outrages inflicted upon the subjects of the blockading Powers, that Venezuela had refused the suggestion of arbitration, that Dr. Drago misunderstood the Venezuelan question, and that the Powers never intended permanently to occupy any part of Venezuela. Further, Mr. Hay, in his reply to Dr. 

Drago, said: "The President declared in his Message to

Congress, December 3, 1901, that by the Munroe Doctrine 'we do not guarantee any State against punishment if it misconducts itself, [masked clause describing a condition or proviso] Although the practice, against which the Drago Doctrine protests is liable to be abused, it would hardly be prudent on the part of European Powers nor conducive to progress in backward States, if the right of collecting debts were sur- 

See the Annual Register of 1907, p. 345.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| provided that punishment does not take the form of the acquisition of territory by any non-American Power.'" | ground_truth | 1.000 | 0.022 |
| provided that punishment involves the acquisition of territory by some non-American power | negation | 0.000 | 0.023 |
| unless they can count beforehand on a good chance of immediate employment | same_book | 0.000 | 0.003 |
| if the right of collecting debts were sur- See the Annual Register of 1907 | same_book | 0.000 | 0.613 |
| unless such misconduct involves an attack on their citizens and property | anachronistic_mistral-small:24b | 0.000 | 0.137 |
| provided that the state has failed to observe its treaty obligations or has engaged in conduct contrary to the principles of international law | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.202 |

**Brier Score:** 0.2320


## Question 188

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** France makes steady progress, and Italy shows a large increase, as is only to be expected, because the emigration from Italy has long been very large. It may be added that 

French goods make their way by sheer merit, for France has in her own land ample scope for her scanty population. Some advantage may be obtained by her as the head of the Latin race, [masked clause revising an implied expectation]. It is very interesting to see how Argentina has passed from small to great things in matters of trade.

Write a clause appropriate for this book that could stand in the position marked by [masked clause revising an implied expectation]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but wherever there are women and luxury there will French trade flourish, and further, in machinery of many kinds France, if equalled by any other nation for excellence, is equalled by England alone | ground_truth | 1.000 | 0.119 |
| but wherever there are scarcity and simplicity, French trade will wither, and further, in machinery of many kinds, France, if surpassed by any other nation for excellence, is surpassed by England alone | negation | 0.000 | 0.117 |
| but it is a peculiarity about Argentina that the people hurry to institute a great export trade long before they think of supplying themselves adequately with an article | same_book | 0.000 | 0.192 |
| but the third view is naturally that of Argentina, which is every year receiving an abundant stream of white colonists to develop the industries which cry aloud for labour | same_book | 0.000 | 0.109 |
| but her influence is tempered by the fierce competition from other nations within Latin America. | anachronistic_mistral-small:24b | 0.000 | 0.407 |
| even as its resources are comparatively scarce | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.056 |

**Brier Score:** 0.1680


## Question 189

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** The Spaniards still appear to have had a design to check the Portuguese in 94
Brazil, but Cabot evidently found them too strong in that quarter, so, says Purchas, "he thought good to busy himself in something that might be profitable; and entered the year 29 discovering the River of Plate, where he was almost three years; and not being seconded, with relation of that which he had found, returned to Castile, having gone many leagues up the River. He found plate or silver among the Indians of those countries, [masked clause describing a cause or reason] Here Purchas makes two mistakes.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for in the wars which these Indians had with those of the kingdoms of Peru they took it, and from it is called the River of Plate, of which the country hath taken the name." | ground_truth | 1.000 | 0.221 |
| for in the wars which these Indians had with those of the kingdoms of Peru they failed to find silver, and the lack of plate hath given the river its name." | manual_negation | 0.000 | 0.057 |
| for experience showed them the immense resources of their country, and proved that it could subsist upon its revenues without asking for anything from Peru or Spain (Arcos' ""La Plata," p. 241) | same_book | 0.000 | 0.047 |
| for the Portuguese claimed indefinite territory in this direction under the convention of Tordesillas, and it behoved Spain to assert ownership before it was too late | same_book | 0.000 | 0.246 |
| because he was looking to gain support and resources from his king. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.236 |
| as a result of the Indians having discovered rich silver deposits in the region." | manual_anachronistic_gpt-oss:20b | 0.000 | 0.193 |

**Brier Score:** 0.1277


## Question 190

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** Beyond a doubt, in

Spanish America there is an unexampled field for a devout missionary; the foe is merely apathy, and if a warmer spirit were breathed into the Church in Argentina, and if the clergy paid more attention to the intellectual side of their calling, the results would be remarkable. [masked sentence describing a tension or contrast] Statistically, there can be no doubt that Argentina belongs unreservedly to Rome; only the merest fraction, perhaps forty thousand, of the population is outside that Church.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| But if the religious indifference spreads downwards, Argentina, like France, may see her population dwindle, and her army decay, and may be prevented from taking a high position among world Powers. | ground_truth | 1.000 | 0.043 |
| But if the religious fervor spreads upwards, Argentina, like France, may see her population swell, and her army strengthen, and may be encouraged to take a high position among world Powers. | negation | 0.000 | 0.035 |
| However, it must be remembered that the fraternal spirit of the Greeks did not preserve them from internecine wars, and Argentina, flanked by each of the other two powerful South American Republics, cannot afford to neglect her armaments. | same_book | 0.000 | 0.087 |
| There is, however, little doubt that Argentina possesses a good army, sufficient for the defence of even her very vulnerable frontier. | same_book | 0.000 | 0.029 |
| Yet, despite the numerical dominance of Catholicism, there exists a profound disconnection between the church and the people's hearts. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.629 |
| Yet the same apathy that hampers missionary zeal is evident in the clergy’s neglect of the nation’s material hardships, underscoring a stark tension between spiritual devotion and social responsibility. | anachronistic_gpt-oss:20b | 0.000 | 0.176 |

**Brier Score:** 0.2254


## Question 191

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** He also attempted to settle the country, but without success, for Thomas 

Cavendish (who named Port Desire after his own ship) saw in 1586, twenty-three famished Spaniards, the only survivors of the city of King Philip, founded by Gamboa on the Straits. These poor creatures were trying to return to the Plate district. [masked sentence describing an inference or effect] In 1590 John Davys found a solitary straggler here, and the bold navigator thus describes his barren experiences: "Here we made a boat of the boards of our chests, which, being finished, we sent seven armed men in the same on land on the north shore, being wafted on land by the savages with certain white skins; who, as soon as they came on shore, were presently killed by an hundred of the wild people in the sight of two of our men, which rowed them on shore, which two only escaped back again to us with the boat.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Cavendish, therefore, named the deserted settlement the Town of Famine, and it retains the name of Port Famine to this day." | ground_truth | 1.000 | 0.106 |
| Cavendish, therefore, named the flourishing settlement the City of Plenty, and it retains the name of Port Plenty to this day | negation | 0.000 | 0.065 |
| Thus, because the land in question contained a number of different tribes, they received by analogy the name Chacu, which the Spaniards have corrupted into Chaco." | same_book | 0.000 | 0.033 |
| This grim discovery underscored the futility of earlier attempts at colonization and the harsh realities of survival in this unforgiving land. | manual_anachronistic_mistral-small:24b | 0.000 | 0.666 |
| Their return was fraught with danger, as hostile natives constantly threatened their passage. | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.129 |

**Brier Score:** 0.2529


## Question 192

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** About twenty years later another traveller estimates the population at fifteen thousand and says: "The city presents an extremely clean and orderly appearance; the streets, which intersect at right angles, are well kept and well lighted. The only manufacture in the place is that of leather. There is no newspaper, although formerly there were two weekly journals published. . . . The climate is very salubrious, [masked clause conceding a limit or exception]. There are no foreigners in the town, nor even in the province, except a few French and two or three English: the government architect is a Frenchman, who possesses both wealth and influence."

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though the rain does not fall in sufficient quantity | ground_truth | 1.000 | 0.291 |
| although rain is continuous and abundant | manual_negation | 0.000 | 0.003 |
| though perhaps the best they can obtain." | same_book | 0.000 | 0.007 |
| except during certain times of the year when winds bring dust from the neighboring plains | anachronistic_mistral-small:24b | 0.000 | 0.499 |
| except for the brief, oppressive heat that grips the town in midsummer | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.199 |

**Brier Score:** 0.1582


## Question 193

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** There is, in fact, little interest in any such matters on the part of the population, and the President is now lamenting the disinclination to a sea-faring life, and of recent years steps have been taken to obtain more satisfactory results; but the total mercantile marine, as yet, amounts to barely 100,000 tons. There is, however, a College for training officers, and also engineers and stokers for the mercantile marine, and there is a Pilot School, and various measures show that the authorities are alive to the importance of the question. In his last Message to Congress the President said: "One of the principal reasons for granting privileges to ships flying the Argentine flag is the employment of native crews, [masked clause describing an inference or effect] The Argentine sailor is a land-conscript, laboriously taught an unfamiliar art, which he learns wonderfully well.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that the nation's sons may find a new path of life, and the navy a fresh source from which to draw sailors in case of an emergency." | ground_truth | 1.000 | 0.112 |
| so that the nation's sons remain on their old paths, and the navy is left with no new recruits when emergencies arise | negation | 0.000 | 0.046 |
| so that it is very easy to find one's way about, for if a pedestrian desires a cross street, say to the north, he has only to march northwards up any given street and he must eventually reach his designation | same_book | 0.000 | 0.113 |
| so that eventually the Argentine flocks were as sorely in need of new blood as were those of France, Germany, or Russia, which, until the middle of the eighteenth century, had never had the benefit of a cross with the old Spanish strain | same_book | 0.000 | 0.136 |
| and thus fostering a sense of national pride and economic independence." | manual_anachronistic_mistral-small:24b | 0.000 | 0.482 |
| which secures a reliable workforce for the nation's merchant fleet." | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.110 |

**Brier Score:** 0.1777


## Question 194

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Foster notes that ‘clotting [is] due to the appearance in blood plasma of a proteid substance, fibrin, which previously did not exist in it as such,’ and asks ‘what are the causes which lead to the appearance of fibrin?’ How might he answer this question in 1888?

**Category:** handcrafted

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Plasma contains an antecedent of fibrin which by chemical change is converted into fibrin. | ground_truth | 1.000 | 0.293 |
| Fibrin makes its appearance because the blood when shed ceases to share in the movement of the circulation. | manual_same_book | 0.000 | 0.092 |
| Fibrin is produced mechanically by proteid components the blood encounters on the surface of the body. | manual | 0.000 | 0.046 |
| Fibrin appears during blood clotting when the enzyme thrombin converts the soluble plasma protein fibrinogen into insoluble fibrin strands. | anachronistic_manual | 0.000 | 0.569 |

**Brier Score:** 0.2085


## Question 195

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Foster asks 'What are the chemical changes which take place when a living resting muscle enters into a contraction?' What is the first change he would likely list, writing in 1888?

**Category:** handcrafted

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| In the first place, the muscle becomes acid, not so acid as in rigor mortis, but still sufficiently so, after a vigorous tetanus, to turn blue litmus distinctly red. | ground_truth | 1.000 | 0.095 |
| The first change is the release of calcium ions (Ca++) from the sarcoplasmic reticulum into the sarcoplasm. | anachronistic_manual | 0.000 | 0.402 |
| At first, glycogen is very apt to be converted into dextrose, or an allied sugar. | manual_same_book | 0.000 | 0.053 |
| The primary chemical change in muscle contraction is the hydrolysis of Adenosine Triphosphate (ATP) into Adenosine Diphosphate (ADP) and inorganic phosphate. | anachronistic_manual | 0.000 | 0.423 |
| The ferment converts the fibrinogen first into a body which we might call soluble fibrin, and then turns this body into veritable fibrin; but further inquiries on this subject are needed. | manual_same_book | 0.000 | 0.026 |

**Brier Score:** 0.2326


## Question 196

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** How would Foster likely define a "muscle-curve"?

**Category:** handcrafted

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The curve described by a muscle on a recording surface during a simple muscular contraction may be called a curve of a simple muscular contraction or, more shortly, a "muscle-curve." | ground_truth | 1.000 | 0.278 |
| A muscle-curve (often referred to as a "Simple Muscle Curve" in physiology or a "Strength Curve" in exercise) represents the relationship between a muscle's force production and its length, velocity, or electrical stimulation. | anachronistic_manual | 0.000 | 0.372 |
| A muscle-curve is, e.g., the arc produced where the gastrocnemius of a frog, under contraction, connects to the femur. | manual | 0.000 | 0.167 |
| The sinusoidal wave produced by regular cardiac action is characterized by most physiologists as the "muscle-curve" of the heart. | manual | 0.000 | 0.183 |

**Brier Score:** 0.1805


## Question 197

**Metadata:** The following question is based on A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A punching machine is provided with a flywheel and driven by an engine at such a rate that two holes are punched in three minutes. The plate operated on is 1 inch thick, and it is estimated that a mean pressure of 69 tons is exerted through the space of 1 inch. Find the average work done per minute by this machine.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 8,586.6 ft-lbs | ground_truth | 1.000 | 0.296 |
| 6.9 hp | manual | 0.000 | 0.116 |
| 0.69 kW | manual | 0.000 | 0.177 |
| 138 ft-lbs | manual | 0.000 | 0.411 |

**Brier Score:** 0.1773


## Question 198

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A cistern 22 ft. long, 10 ft. broad, and 8 ft. deep, has to be filled with water from a well 8 ft. in diameter and 40 ft. deep. Supposing no water to flow into the well during the operation of filling the cistern, ascertain how far the surface of the water in the well is depressed.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 35 ft. | ground_truth | 1.000 | 0.207 |
| 22 ft. | manual | 0.000 | 0.624 |
| 8 meters | manual | 0.000 | 0.001 |
| 20 gallons | manual | 0.000 | 0.018 |
| 11 ft. long by 5 ft broad | manual | 0.000 | 0.150 |

**Brier Score:** 0.2082


## Question 199

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A spiral spring is stretched through a length of 1/2 inch by a force of 10 lbs. Find the work done in stretching it through an additional length of 2 inches.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 60 inch-lbs. | ground_truth | 1.000 | 0.220 |
| 30 inch-lbs. | manual | 0.000 | 0.253 |
| 20 joules | manual | 0.000 | 0.213 |
| 40 inch-lbs. | manual | 0.000 | 0.315 |

**Brier Score:** 0.2044


## Question 200

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** Steam enters a cylinder at 80 lbs. per square inch absolute, and is cut off at 1/3 of the stroke. Diameter of piston, 40 inches, length of stroke, 5 feet. No of revolutions, 50 per minute. Back pressure, 3 lbs. per square inch absolute. Find the horse-power of the engine, assuming the steam to expand hyperbolically..

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 1,009 H.P. | ground_truth | 1.000 | 0.553 |
| 50 hp per minute. | manual | 0.000 | 0.123 |
| 240 lb-ft. | manual | 0.000 | 0.115 |
| 1,444 hp. | manual | 0.000 | 0.208 |

**Brier Score:** 0.0678


## Question 201

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** State the principle of moments.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| When a body is kept in equilibrium by any number of co-planer forces, the algebraical sum of the moments of all the forces about any point in their plane is zero. Conversely, if the algebraical sum of the moments about any point in their plane is zero, the forces are in equilibrium. | ground_truth | 1.000 | 0.685 |
| A moment is the smallest unit of experienced time. | manual | 0.000 | 0.026 |
| If something isn’t rotating, every tendency to turn it one way is exactly balanced by a tendency to turn it the other way. | anachronistic_manual | 0.000 | 0.177 |
| If the net external torque on a system is zero, its total angular momentum (L remains constant. | manual | 0.000 | 0.112 |

**Brier Score:** 0.0360


## Question 202

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** The saddle of a lathe weighs 5 cwts., and it is moved along the bed of the lathe by a rack and pinion arrangement. What force, applied at the end of a handle 10 inches in length, will be just capable of moving the saddle, supposing the pinion to have 12 teeth of 1 1/4-inch pitch, and the coefficient of friction between the saddle and lathe-bed to be 0.1, other friction being neglected?

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 13.36 lbs | ground_truth | 1.000 | 0.344 |
| 13.4 lbf | anachronistic_manual | 0.500 | 0.161 |
| 50 cwts | manual | 0.000 | 0.196 |
| 24 kg | manual | 0.000 | 0.034 |
| 50 lbs | manual | 0.000 | 0.265 |

**Brier Score:** 0.1310


## Question 203

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A wheel of 40 teeth is driven by a winch handle 14 inches long, and gears with a rack having teeth of 1 inch pitch; apply the principle of work to find the driving pressure exerted on the rack when a force of 50 lbs. is applied at the end of the winch handle.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 110 lbs | ground_truth | 1.000 | 0.552 |
| 110 lbf | anachronistic_manual | 0.500 | 0.177 |
| 14 Newtons | manual | 0.000 | 0.050 |
| 5 cwts | manual | 0.000 | 0.019 |
| 14 lbs | manual | 0.000 | 0.202 |

**Brier Score:** 0.0698


## Question 204

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A pair of wheels have 25 and 130 cycloidal teeth respectively. Find the addendum of each wheel, that the arcs of approach and recess may each be equal to the pitch, the flanks being radial.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| .17 p and .28 p | ground_truth | 1.000 | 0.215 |
| 0.11 p and 0.3 p | anachronistic_manual | 0.000 | 0.383 |
| 5 square addenda and 12 square addenda | manual | 0.000 | 0.081 |
| 25 lbs | manual | 0.000 | 0.011 |
| 5 for the smaller wheel and 26, proportionally, for the larger one | manual | 0.000 | 0.309 |

**Brier Score:** 0.1732


## Question 205

**Metadata:** This question is about Gould and Pyle's Cyclopedia of Practical Medicine and Surgery, With Particular Reference to Diagnosis and Treatment, a reference work published in 1912 by George M. Gould, an American physician.

**Question:** In 1912, what would a physician call the chemic basis of the nucleus, consisting of a complex proteid base and an acid?

**Category:** handcrafted

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| nuclein | ground_truth | 1.000 | 0.012 |
| DNA | anachronistic_manual | 0.000 | 0.339 |
| deoxyribonucleic acid | anachronistic_manual | 0.000 | 0.328 |
| protoplasm | manual | 0.000 | 0.321 |

**Brier Score:** 0.3254


## Question 206

**Metadata:** The following question is based on  Gould and Pyle's Cyclopedia of Practical Medicine and Surgery, With Particular Reference to Diagnosis and Treatment, a reference work published in 1912 by George M. Gould, an American physician.

**Question:** Why might a physician recommend Turkish baths as a treatment for obesity?

**Category:** handcrafted

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| They are useful to remove surplus fluids from the body. | ground_truth | 1.000 | 0.458 |
| Turkish baths are not an effective treatment for obesity; studies show no durable effect on BMI or fat mass. | anachronistic_manual | 0.000 | 0.452 |
| They have psychological value and help support self-esteem. | anachronistic_manual | 0.000 | 0.090 |

**Brier Score:** 0.1687


## Question 207

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** Where was the actor Marlon Brando born?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I have not heard of an actor named Marlon Brando. | ground_truth | 1.000 | 0.026 |
| Brando was born in Omaha, Nebraska. | manual | 0.000 | 0.785 |
| I don't know where Marlon Brando was born yet, because he won't be born until 1924. | manual | 0.000 | 0.057 |
| He was born in Sicily. | manual | 0.000 | 0.105 |
| I'm sorry, I don't have that information. | ground_truth | 1.000 | 0.026 |

**Brier Score:** 0.5057


## Question 208

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** What is the ninth planet in our Solar System?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The Solar System only contains eight planets, unless perhaps you mean to count the sun itself? | ground_truth | 1.000 | 0.011 |
| Pluto. | anachronistic_manual | 0.000 | 0.004 |
| The ninth planet will be named Pluto, but it has not yet been discovered. | anachronistic_manual | 0.250 | 0.212 |
| Pluto will not be discovered until 1930, so there are only eight planets. | anachronistic_manual | 0.250 | 0.173 |
| Uranus is the ninth planet. | manual | 0.000 | 0.601 |

**Brier Score:** 0.2694


## Question 209

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** Who developed FM radio and made the first FM broadcast?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I'm not familiar with the meaning of "FM" as applied to radio. | ground_truth | 1.000 | 0.051 |
| American engineer Edwin Armstrong is often called the father of FM radio. | anachronistic_manual | 0.000 | 0.279 |
| Guglielmo Marconi made the first FM broadcast in 1895. | manual | 0.000 | 0.669 |
| I don't know. | ground_truth | 1.000 | 0.002 |

**Brier Score:** 0.6056


## Question 210

**Metadata:** This question asks for information widely available in Athe United States in 1924, for instance from newspapers and encyclopedias.

**Question:** What is Joseph Campbell best known for?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| He founded the Campbell's Soup company. | ground_truth | 1.000 | 0.050 |
| He is famous for his work in comparative mythology, specifically the concept of the "monomyth" or "hero's journey." | anachronistic_manual | 0.000 | 0.589 |
| Joseph Campbell was an American professional golfer who played on the PGA Tour. | anachronistic_manual | 0.000 | 0.257 |
| Joseph Campbell invented the Black Watch tartan associated with Clan Campbell. | manual | 0.000 | 0.010 |
| I am not familiar with anyone named Joseph Campbell. | manual | 0.000 | 0.094 |

**Brier Score:** 0.2647


## Question 211

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** What is the difference between RAM and ROM?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| A ram is a male sheep, but if it has a special meaning in this context, I am not familiar with it, or with "ROM." | ground_truth | 1.000 | 0.243 |
| RAM (random access memory) is a 'scratch pad' -- volatile, fast, and writable. ROM (read-only memory) is the system’s “instruction set” that must survive power cycles -- non-volatile and not writable. | anachronistic_manual | 0.000 | 0.504 |
| Ram and Rom were two brothers involved in the mythic foundation of Rome. | manual | 0.000 | 0.113 |
| RAM and ROM are nineteenth-century acronymns that stand for reagent active metallurgy and reagent omitted metallurgy. | manual | 0.000 | 0.141 |

**Brier Score:** 0.2149


## Question 212

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** Is Britney Spears best known as a painter, a scientist, or as a popular singer?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I am not familiar with anyone named Britney Spears. | ground_truth | 1.000 | 0.076 |
| Britney Spears is best known as a popular singer. | anachronistic_manual | 0.000 | 0.734 |
| Britney Spears is best known as a painter. | manual | 0.000 | 0.127 |
| Britney Spears is most widely known as a scientist. | manual | 0.000 | 0.062 |

**Brier Score:** 0.3529


## Question 213

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Answer as someone would if provided only with that information.

**Question:** Who were the inventors of the first powered, heavier-than-air flying machine to use wings rather than buoyancy for lift?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I am not aware of any successful invention of that kind, although many have been proposed. | ground_truth | 1.000 | 0.042 |
| Wilbur and Orville Wright. | anachronistic_manual | 0.000 | 0.895 |
| The Montgolfier brothers. | manual | 0.000 | 0.047 |
| Amelia Earhart. | anachronistic_manual | 0.000 | 0.016 |

**Brier Score:** 0.4301


## Question 214

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Answer as someone would if provided only with that information.

**Question:** Why was the League of Nations created?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| TI'm not sure I'm familiar with the League you have in mind. | ground_truth | 1.000 | 0.061 |
| The League of Nations was established by the Treaty of Versailles as an international forum where states could settle disputes through negotiation and arbitration rather than war. | anachronistic_manual | 0.000 | 0.571 |
| The League of Nations was established in order to contain Napoleon. | manual | 0.000 | 0.069 |
| The League of Nations was established in the aftermath of World War Two to provide a venue for peaceful resolution of disputes between states. | anachronistic_manual | 0.000 | 0.299 |

**Brier Score:** 0.3257


## Question 215

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Your answer should be based on information available in that context.

**Question:** Who did Jane Seymour marry?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| King Henry VIII. | ground_truth | 1.000 | 0.603 |
| She married four times, but her first husband was Michael Attenborough. | anachronistic_manual | 0.000 | 0.153 |
| I'm not yet aware of an actress named Jane Seymour. | anachronistic_manual | 0.000 | 0.202 |
| Edwin Albemarle Seymour. | manual | 0.000 | 0.041 |

**Brier Score:** 0.0559


## Question 216

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Your answer should be based on information available in that context.

**Question:** What is the chief advantage of nylon textiles?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I'm not familiar with the term 'nylon.' | ground_truth | 1.000 | 0.031 |
| Nylon has high tensile strength, making it tough and resistant to wear. | anachronistic_manual | 0.000 | 0.243 |
| Nylon is hydrophobic, meaning it does not absorb water readily, allowing it to dry quickly and resist moisture-related damage like mildew. | anachronistic_manual | 0.000 | 0.428 |
| Nylon is generally low-maintenance, machine-washable, and resistant to wrinkles, which reduces the need for ironing. | anachronistic_manual | 0.000 | 0.298 |

**Brier Score:** 0.3177


## Question 217

**Metadata:** This question asks for information that would be available in an encyclopedia published in Britain in 1915. Your answer should be based on information available in that context.

**Question:** What is the chief agricultural source of the fabric in thneeds?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I can't answer this question, because I'm not familiar with thneeds. | ground_truth | 1.000 | 0.136 |
| Truffula Trees are the chief source of thneeds. | anachronistic_manual | 0.000 | 0.101 |
| Thneeds are produced from fibers in the flax plant. | manual | 0.000 | 0.136 |
| Lambswool. | manual | 0.000 | 0.626 |

**Brier Score:** 0.2919


## Question 218

**Metadata:** This question asks for information that would be available in an encyclopedia published in Britain in 1915. Your answer should be based on information available in that context.

**Question:** What is a coelacanth?

**Category:** refusal

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| A coelacanth is one of a family of extinct ganoids, differing from other fishes in their hollow bones, and enjoying remarkable constancy of structural character from the Devonian through the Palaeozoic. | ground_truth | 1.000 | 0.209 |
| The coelacanth is often considered an example of a "living fossil" in popular science because it is considered the sole remaining member of a taxon otherwise known only from fossils, evolving a body plan similar to its current form approximately 400 million years ago. | anachronistic_manual | 0.000 | 0.404 |
| A living fossil which provides an important link between the fishes and terrestrial tetrapods. | anachronistic_manual | 0.000 | 0.107 |
| An extinct family of synapsid that includes Dimetrodon and Sphenacodon. | manual | 0.000 | 0.281 |

**Brier Score:** 0.2199


## Question 219

**Metadata:** 

**Question:** The text that follows comes from a newspaper article in The Cheltenham Chronicle. "There was an exciting scene in the First Volksraad on Thursday, when the State Secretary read a communication from Sir A. Milner in reply to the Transvaal Government’s request for an explanation of the mobilisation of British troops on the frontier of the South African Republic. The High Commissioner’s reply was to the effect that the troops were to safeguard British interests, and in preparation against contingencies. President Kruger urged the members of the Raad to moderate the tone of their remarks. In the discussion several members warned the Government to be prepared, as war seemed inevitable. Mr. Tœbs said he considered the explanation of Sir A. Milner was equivalent to a declaration of war by Great Britain." This article was likely published in

**Category:** attribution

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| the 1890s | ground_truth | 1.000 | 0.397 |
| the 1880s | manual | 0.500 | 0.220 |
| 1900-09 | manual | 0.500 | 0.147 |
| the 1870s | manual | 0.000 | 0.098 |
| the nineteen-teens | manual | 0.250 | 0.001 |
| the 1920s | manual | 0.000 | 0.138 |

**Brier Score:** 0.1096


## Question 220

**Metadata:** 

**Question:** Who wrote the epic poem that begins "OF Mans First Disobedience, and the Fruit / Of that Forbidden Tree, whose mortal tast / Brought Death into the World, and all our woe, / With loss of Eden, till one greater Man / Restore us, and regain the blissful Seat, /Sing Heav'nly Muse"?

**Category:** attribution

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| John Milton | ground_truth | 1.000 | 0.488 |
| Paradise Lost | manual | 0.000 | 0.484 |
| John Stuart Mill | manual | 0.000 | 0.000 |
| Stanley Fish | anachronistic_manual | 0.000 | 0.028 |

**Brier Score:** 0.1245


## Question 221

**Metadata:** The following question is drawn from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Make a single sentence out of the following pair of sentences by using a relative pronoun. 1. I heard some news. 2. The news astonished me.

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| I heard some news that astonished me. | ground_truth | 1.000 | 0.545 |
| I heard some news, and the news astonished me. | manual | 0.000 | 0.255 |
| The news these days is astonishing. | manual | 0.000 | 0.014 |
| I was astonished by the news. | manual | 0.000 | 0.186 |

**Brier Score:** 0.0768


## Question 222

**Metadata:** The following question comes from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Which words in the following sentence are nouns, and which are verbs. "A dark cloud hid the moon."

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| "Cloud" is a noun. "Hid" is a verb. "Moon" is a noun. | ground_truth | 1.000 | 0.325 |
| "Dark" is a noun. "Moon" is a verb. | manual | 0.000 | 0.168 |
| All of the words in that sentence are nouns. | manual | 0.000 | 0.208 |
| "Cloud" is the only noun in the sentence, and "hid" is the only verb. | manual | 0.000 | 0.299 |

**Brier Score:** 0.1543


## Question 223

**Metadata:** The following question comes from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Find out which words in the following sentence stand for one thing, and which stand for more than one. When you find a noun in the plural, say what the singular of it is. When you find one in the singular, say what the plural would be. "The butcher killed the sheep."

**Category:** textbook

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| "Butcher" is a singular noun, and its plural would be "butchers." "The singular and plural forms of "sheep" are the same, and it could be either singular or plural in this context. | ground_truth | 1.000 | 0.278 |
| "Butcher" is a singular noun, and its plural would be "butchers." "Sheep" is also a singular noun, and its plural would be "sheeps." | manual | 0.000 | 0.551 |
| "Butcher" is a non-count noun; it has the same form when used for a singular or a plural. "Sheep" is plural, and its singular would be "a sheep." | manual | 0.000 | 0.171 |

**Brier Score:** 0.2845


## Question 224

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** If now we measure the time during which the aorta, even near the heart, is being distended by the injection of the ventricular contents, we find this to be appreciably less than the time from c to d, during which the systole of the ventricle is still going on, though the contents have already begun to escape at about c. This means that the ventricle, though empty, remains contracted for some little time after its contents have left the cavity. It is possible that the point c' in the three figures under discussion, where the descent of the lever changes in rate, becoming less rapid, corresponds to the end of the outflow from the ventricle; [masked clause revising an implied expectation]. The escape from the ventricle is rapid and forcible; the flow ceases suddenly.

Write a clause appropriate for this book that could stand in the position marked by [masked clause revising an implied expectation]:

**Category:** cloze_contrastclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| but this is not certain, and indeed the exact interpretation of this part of the curve is especially difficult | ground_truth | 1.000 | 0.593 |
| but this is assured, and indeed the exact interpretation of this part of the curve is particularly straightforward | negation | 0.000 | 0.077 |
| it is uncertain, however, that these make their way chiefly or exclusively through systole | manual_same_book | 0.000 | 0.115 |
| but this interpretation complicates dissection of the aorta, and indeed makes it nearly impossible | manual_same_book | 0.000 | 0.073 |
| and it appears as if all blood has already left | anachronistic_mistral-small:24b | 0.000 | 0.084 |
| yet the precise instant may be obscured by transient arterial pressure variations | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.059 |

**Brier Score:** 0.0334


## Question 225

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Of two muscles therefore of equal length (and of the same quality) the most work will be done by that which has the larger number of fibres, that is to say, the fibres being of equal width, which has the greater sectional area; and of two muscles with equal sectional areas, the most work will be done by that which is the longer. If the two muscles are unequal both in length and sectional area, the work done will be the greater in the one which has the larger bulk, which contains the greater number of cubic units. [masked sentence describing an inference or effect] We learn then from the foregoing paragraphs that the work done, by a muscle-nerve preparation, will depend, not only on the activity of the nerve and muscle as determined by their own irritability, but also on the character and mode of application of the stimulus, on the kind of contraction (whether a single spasm, or a slowly repeated tetanus or a rapidly repeated tetanus) on the load itself, and on the size and form of the muscle.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| In speaking therefore of the work which can be done by a muscle, we may use as a standard a cubic unit of bulk, or, the specific gravity of the muscle being the same, a unit of weight. | ground_truth | 1.000 | 0.233 |
| In speaking therefore of the work which cannot be done by a muscle, we may use as a standard a cubic unit of bulk, or, the specific gravity of the muscle being the same, a unit of weight. | negation | 0.000 | 0.177 |
| Of two equal-length muscles one must therefore prefer the one of greater bulk, as it will assuredly be able to perform more work. | manual_same_book | 0.000 | 0.138 |
| Hence in extreme stimulation, in what in the muscle corresponds to complete tetanus, the form of the body is the same as in rest; and the tetanized sphere would not be appreciably smaller than the sphere at rest, for that would imply change of bulk, but this as we have seen does not take place. | same_book | 0.000 | 0.049 |
| Thus, understanding these factors allows us to predict how altering muscle characteristics will influence the overall efficiency of the muscle-nerve preparation. | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.169 |
| Hence, the mechanical advantage of a muscle is directly proportional to its bulk, implying that a larger muscle will generate greater force over a given distance, thereby accomplishing more work than a smaller counterpart under identical simply conditions. | anachronistic_gpt-oss:20b | 0.000 | 0.234 |

**Brier Score:** 0.1208


## Question 226

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** And we may, in connection with this, call attention to the fact that the dilation or loss of tone which follows upon section of the cervical sympathetic (and the same is true of the abdominal splanchnic) is not always, though it may be sometimes, permanent; in a certain number of cases it has been found that after a while, it may be not until after several days, the dilation disappears and the arteries regain their usual calibre; on the other hand in some cases no such return has been observed after months or even years. This recovery when it occurs cannot always be attributed to any regeneration of vaso-motor fibres in the sympathetic, [masked clause describing a cause or reason]. When recovery of tone has thus taken place, dilation or increased constriction may be occasioned by local treatment: the ear may be made to blush or to pale by the application of heat or cold, by gentle stroking or rough handling and the like; but neither the one nor the other condition can be brought about by the intervention of the central nervous system.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| for it is stated to have been observed when the whole length of the nerve including the superior cervical ganglion had been removed | ground_truth | 1.000 | 0.207 |
| for it is reported to have never been observed even after removing only a portion of the nerve, excluding the superior cervical ganglion | negation | 0.000 | 0.069 |
| since the same fibres may, on the one hand, by an increase in the impulses passing along them, be the means of constriction, and on the other hand, by the removal or diminution of the tonic influences passing along them, be the means of dilation | same_book | 0.000 | 0.391 |
| for these continue dilated, sometimes exceedingly so | same_book | 0.000 | 0.002 |
| but is likely due to compensatory mechanisms in the remaining intact sympathetic fibers | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.181 |
| for some physicians have observed the spontaneous reestablishment of sympathetic nerve connections and the activation of local autoregulatory mechanisms | manual_anachronistic_gpt-oss:20b | 0.000 | 0.150 |

**Brier Score:** 0.1404


## Question 227

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** In both these cases the effect is mainly a reflex one, it being the central nervous system which brings about augmentation of constriction in the one case and inhibition in the other; though possibly some slight effect is produced by the direct action of the cold or heat on the vessels of the skin simply. Moreover the vascular changes in the skin are accompanied by corresponding vascular changes in the viscera (chiefly abdominal) of a reverse kind. When the vessels of the skin are dilated those of the viscera are constricted, and vice versa; [masked clause describing an inference or effect]. By these changes, as we shall see later on, the maintenance of the normal temperature of the body is in large measure secured.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| so that a considerable portion of the whole blood ebbs and flows, so to speak, according to circumstances from skin to viscera and from viscera to skin | ground_truth | 1.000 | 0.258 |
| so that barely any part of the blood circulates between the skin and internal organs | negation | 0.000 | 0.101 |
| so that, aas we shall see later on, it is possible in the living organism either to reduce or to increase what may be considered as the normal peripheral resistance | manual_same_book | 0.000 | 0.090 |
| so that chemical changes too slight to be recognized by the means at present at our disposal would amply suffice to provide all the energy set free | manual_same_book | 0.000 | 0.061 |
| such that the body can efficiently dissipate heat through the skin or conserve it within vital organs | anachronistic_mistral-small:24b | 0.000 | 0.361 |
| this counterbalancing action thereby preserves the internal thermal equilibrium | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.129 |

**Brier Score:** 0.1200


## Question 228

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** He has moreover advanced the theory that muscle may be considered as composed of electro-motive particles or molecules, each of which like the muscle at large has a positive equator and negative ends, the whole muscle being made up of these molecules in somewhat the same way, (to use an illustration which must not however be strained or considered as an exact one) as a magnet may be supposed to be made up of magnetic particles each with its north and south pole. [masked sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| There are reasons however for thinking that these muscle currents have no such fundamental origin, that they are in fact of surface and indeed of artificial origin. | ground_truth | 1.000 | 0.044 |
| There are reasons however for thinking that these muscle currents have a fundamental origin, that they are in fact of deep and indeed natural origin. | negation | 0.000 | 0.031 |
| We are not however at present in a position to make any very definite statement as to the relation of the myosin to the structural features of muscle. | same_book | 0.000 | 0.170 |
| A muscle however may acquire as a whole a certain amount of rigidity on account of some of the fibres becoming rigid, while the remainder, though they have lost their irritability, have not yet advanced into rigor mortis. | same_book | 0.000 | 0.077 |
| He suggests however that these particles are not simply aligned but interact dynamically to produce movement. | manual_anachronistic_metadataless_mistral-small:24b | 0.000 | 0.067 |
| Thus, when stimulated, the positive equators of these particles are attracted to the negative ends of neighbouring particles, producing the shortening of the muscle. | anachronistic_gpt-oss:20b | 0.000 | 0.611 |

**Brier Score:** 0.2211


## Question 229

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Moreover, the propagation of the current is stopped by a ligature, or by crushing the nerve. We may speak of the conditions which give rise to this electrotonic current as a physical electrotonus analogous to that physiological electrotonus which is made known by variations in irritability. The physical electrotonic current is probably due to the escape of the polarizing current along the nerve under the peculiar conditions of the living nerve; but we must not attempt to enter here into this difficult subject or into the allied question as to the exact connection between the physical and the physiological electrotonus, [masked clause acknowledging a countervailing fact]. § 77.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| though there can be little doubt that the latter is dependent on the former | ground_truth | 1.000 | 0.278 |
| though it's clear that the former is independent of the latter | negation | 0.000 | 0.133 |
| though in its more developed state the electrotonus may be considered a form of brain activity | manual_same_book | 0.000 | 0.089 |
| though certainly they may both remain for a long time | manual_same_book | 0.000 | 0.006 |
| while recognizing that some researchers argue for distinct underlying mechanisms | anachronistic_metadataless_mistral-small:24b | 0.000 | 0.339 |
| although the evidence for a direct correspondence is not yet definitive | anachronistic_gpt-oss:20b | 0.000 | 0.154 |

**Brier Score:** 0.1145


## Question 230

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** When we stimulate the nerve of a muscle nerve preparation the result, though modified in part by the condition of the muscle and nerve, whether fresh and irritable or exhausted for instance, is directly dependent on the nature and strength of the stimulus. If we use a single induction-shock we get a simple contraction, [masked clause describing a condition or proviso], if we use a weak shock we get a slight contraction, if a strong shock a large contraction and so on; and throughout our study of muscular contractions we assumed that the amount of contraction might be taken as a measure of the magnitude of the nervous impulses generated by the stimulus. And it need hardly be said that when we stimulate certain fibres only of a motor nerve, it is only the muscular fibres in which those nerve fibres end, which are thrown into contraction.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| if the interrupted current we get a tetanus | ground_truth | 1.000 | 0.015 |
| if the uninterrupted current avoids a tetanus | negation | 0.000 | 0.002 |
| if the stimulation of a particular nerve or any other operation leads to a marked rise of the mean bloodpressure | same_book | 0.000 | 0.025 |
| if the trunk of a nerve be pinched | same_book | 0.000 | 0.068 |
| provided that the stimulus is sufficient to excite the muscle | anachronistic_mistral-small:24b | 0.000 | 0.691 |
| provided the nerve remains intact | anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.199 |

**Brier Score:** 0.2486


## Question 231

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** The arrangement of the valves of the heart causes this action of the respiratory pump to promote the flow of blood in the direction of the normal circulation; and indeed were the heart perfectly motionless the working of this respiratory pump alone would tend to drive the blood from the vena cava through the heart into the aorta, and so to keep up the circulation; the force so exerted however would, without the aid of the heart, be able to overcome a very small part only of the resistance in the capillaries and small vessels of the lungs and so would prove actually ineffectual. There are then several helps to the flow along the veins, but it must be remembered that however useful, they are helps only and not the real cause of the circulation. [masked sentence describing a cause or reason] [BOOK 1.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The real cause of the flow is the ventricular stroke, and this is sufficient to drive the blood from the left ventricle to the right auricle, even when every muscle of the body is at rest and breathing is for a while stopped, when therefore all the helps we are speaking of are wanting. | ground_truth | 1.000 | 0.108 |
| The real cause of the flow is the ventricular stroke, and this is insufficient to drive the blood from the left ventricle to the right auricle, even when every muscle of the body is at rest and breathing is for a while stopped, when therefore all the helps we are speaking of are present. | negation | 0.000 | 0.095 |
| We may here call to mind the fact mentioned in § 153, of the existence, more or less marked in all hearts, and well seen in the heart of the tortoise, of a muscular ring or collar between the sinus and the auricle, and of a similar ring between the auricle and ventricle. | same_book | 0.000 | 0.185 |
| This is likely the cause of a spasm in the muscle of B; and the stimuli following each other rapidly, as being produced by the tetanus of A they must do, the spasms in B to which they give rise are also fused into a tetanus in B. | manual_same_book | 0.000 | 0.037 |
| The primary driver of blood flow is the heart's contraction and relaxation. | anachronistic_mistral-small:24b | 0.000 | 0.369 |
| The heart’s rhythmic contraction, which propels blood from the atria into the ventricles and then ejects it into the aorta, is the principal force that overcomes venous resistance and maintains continuous circulation, ensuring that even in the presence of respiratory and venous aids, the circulation is sustained primarily by cardiac activity. | manual_anachronistic_metadataless_gpt-oss:20b | 0.000 | 0.205 |

**Brier Score:** 0.1697


## Question 232

**Metadata:** The following paragraph comes from Journal of Nervous and Mental Disease, a medical journal published in 1916. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] A typical example of an unconscious mental process, illustrating all of these, would be the wish of a little girl that her mother might die so that she could marry her father. The six attributes in question, together with others not here mentioned, make up a consistent and clearly-defined conception of the unconscious which is formulated on the basis of experience that may at any time be tested.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Briefly summarized, in a single statement: according to psychoanalysis, the unconscious is a region of the mind, the content of which is characterized by the attributes of being repressed, conative, instinctive, infantile, unreasoning, and predominantly sexual. | ground_truth | 1.000 | 0.261 |
| The statement of most fundamental importance, and the one on which the writer lays the greatest stress, concerns both the origin and the content of the unconscious. | same_book | 0.000 | 0.161 |
| The mode of action of the treatment, in a word, is that the overcoming, by means of psychoanalysis, of the resistances that are interposed against the making conscious of the repressed unconscious material, gives the patient a much greater control over this pathogenic material by establishing a free flow of feeling from the deeper to the more superficial layers of the mind, so that the energy investing the repressed tendencies can be diverted from the production of symptoms into useful, social channels. | same_book | 0.000 | 0.176 |
| The following attributes are essential to understanding the nature of unconscious mental processes as observed and analyzed in psychoanalytic theory. | anachronistic_mistral-small:24b | 0.000 | 0.250 |
| In this discussion, the author presents the most essential claim regarding the unconscious, focusing on its origins and contents, and outlines six key attributes that together form a coherent, empirically testable concept of the unconscious today. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.071 |
| The author emphasizes key points about the formation and nature of unconscious thoughts. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.005 |
| Oedipal impulses have four chief characteristics: they are sexual impulses, experienced unconsciously, in childhood,, and involving the child's parents. | manual | 0.000 | 0.077 |

**Brier Score:** 0.0966


## Question 233

**Metadata:** The following paragraph comes from Journal of Nervous and Mental Disease, a medical journal published in 1916. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] Its material is presented in a form admirably adapted to the purpose for which the book is written, as an outline for fuller study and an incentive toward it and a simple, practical source of suggestion for the busy general practitioner, but particularly for the nurse. To this end Dr. Chase outlines first briefly the anatomy and physiology of the nervous system and the fundamental psychic processes. From this he proceeds to a general consideration of insanity and its varying phenomena, briefly defining and describing them, the disturbances of the various fundamental mental processes. Then more in detail he describes the various psychoses classified mainly according to their general immediate exciting causes. Each one is discussed as to its general characteristics and symptoms with some reference to its etiology, in short with a brief summary of the appearance and manifestation of each, with its prognosis and suggestions for treatment.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| This volume contains a brief but comprehensive summary of the most salient points to be considered in the elementary knowledge and treatment of mental disease. | ground_truth | 1.000 | 0.153 |
| These patients need only physical treatment, but the physician should have experience with mental disease so that he can study the influence of physical ills on the mental disease and use this knowledge to help cure. | same_book | 0.000 | 0.056 |
| The article gives an admirable summary of the knowledge of the disease in its various relationships, and is followed by an excellent bibliography. | same_book | 0.000 | 0.038 |
| The book by Dr. Chase provides practical guidance on mental health for general practitioners and nurses. | anachronistic_mistral-small:24b | 0.000 | 0.201 |
| This paragraph reviews Dr. Chase's textbook, highlighting its presentation of nervous system fundamentals, insanity, and psychoses as a practical guide for practitioners and nurses. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.315 |
| This book review discusses Dr. Chase's work on nervous diseases, designed for both full study and practical use by general practitioners and nurses. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.223 |
| This outline of psychopathology has been written by one of England's most experienced psychiatrists, wiho worked witth  Freud himself during his extensive career in Vienna. | manual | 0.000 | 0.014 |

**Brier Score:** 0.1302


## Question 234

**Metadata:** The following paragraph comes from School Civics, an educational textbook written by Frank David Boynton and published in 1904. The topic sentence has been masked.

**Question:** [masked topic sentence] All ordinances which have been approved by a majority of the quorum present in council must be presented to the mayor, and if he approve, he signs the same; if he does not approve, he must veto and return the ordinance with his objection to the council within ten days, or at the next regular session. If he does not return the ordinance within ten days, it is a law, regardless of his approval or disapproval, unless council by final adjournment prevent its return, in which case it shall not be a law. After a vetoed law is returned council may, after the expiration of ten days, reconsider the same and pass it over the mayor's veto by a two-thirds vote of the entire membership of council.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The mayor possesses the veto power over all ordinances passed by the city council. | ground_truth | 1.000 | 0.328 |
| The acts of council are called ordinances, and the style of these ordinances must be "Be it Ordained by the Council of the City of, State of Ohio." | same_book | 0.000 | 0.113 |
| He is the chief conservator of the peace within the village, enforcing all ordinances of the village council and the laws of the state within the limits of the municipality. | same_book | 0.000 | 0.327 |
| The process of enacting city ordinances involves several steps. | anachronistic_mistral-small:24b | 0.000 | 0.182 |
| The president-general holds veto power over council acts, subject to return and council override. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.022 |
| The duties of a village mayor are many. | manual_anachronistic_distort2_mistral-small:24b | 0.000 | 0.002 |
| The process required to pass ordinances through city council, and obtain approval from the mayor, may perhaps be excessively involved. | manual | 0.000 | 0.025 |

**Brier Score:** 0.0864


## Question 235

**Metadata:** The following paragraph comes from School Civics, an educational textbook written by Frank David Boynton and published in 1904. The topic sentence has been masked.

**Question:** [masked topic sentence] The process of amendment provided by the instrument, while not so difficult as to be impracticable, as was the case with the articles of confederation, has nevertheless proved too cumbersome to be resorted to unadvisedly. As a result the constitution has been but little changed by amendment. Of the fifteen amendments that have been passed, the first ten, often called the bill of rights, were passed at one time and might almost be counted as one; while the last three also, relating as they do to the same subject and growing out of the civil war, are really a unit; so that it is perhaps not inaccurate to say that the constitution has really been amended but four times. It has undergone development, but it has been principally through the process of judicial interpretation and through custom. Mr. Bryce has said of it, "The constitution as a whole has stood and stands unshaken. The scales of power have continued to hang fairly even. The President has not corrupted and enslaved Congress; Congress has not paralyzed and cowed the President. . . . Neither the legislature nor the executive has for a moment threatened the liberties of the people. The States have not broken up the Union and the Union has not absorbed the States.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Contrary to the expectation of many at the time of its adoption, the constitution has proved itself extremely stable. | ground_truth | 1.000 | 0.268 |
| How long after its adoption before any amendments were made to the constitution? | same_book | 0.000 | 0.060 |
| The U.S. Constitution's amendment process is complex and rarely used to make changes. | anachronistic_mistral-small:24b | 0.000 | 0.126 |
| The Constitution has evolved primarily through amendments and judicial interpretation, yet its amendment process remains cumbersome and rarely invoked. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.058 |
| The U.S. Constitution's amendment process is rarely used due to its complexity. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.344 |
| Students may ask whether the Constitution is immutable or can be rewritten. | manual | 0.000 | 0.144 |

**Brier Score:** 0.1162


## Question 236

**Metadata:** The following paragraph comes from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook written by Martha Hale Shackford and published in 1913. The topic sentence has been masked.

**Question:** [masked topic sentence] It comes from the pen of one whose writings along this line, especially his history of Christian and ecclesiastical Rome, have already made him well known. In the main Mr. Tuker keeps to a narration of specific events, leaving a description of the beauties of the English countrysides and the architectural glories of the old towers of the collegiate buildings to be expressed in line and color by W. Matheson, the artist, whose many sketches have excellently fulfilled the trust committed to him. Those who have visited Cambridge will find delight in recalling its characteristic scenes and buildings here admirably recorded.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| 2. The book on Cambridge is largely an account of the founding and history, centuries long, of that great English University. | ground_truth | 1.000 | 0.103 |
| Cambridge University is one of the most eminent institutions of higher education in the United Kingdom, and a history of its vicissitudes will certainly be welcomed by readers. | manual_same_book | 0.000 | 0.294 |
| In the way of college courts and quiet scholastic porticoes, of gray-walled gardens and ivied nooks of study, in all the pictorial accidents of a great English university, Cambridge is delightfully and inexhaustibly rich. | same_book | 0.000 | 0.116 |
| Mr. Tuker's book on Cambridge offers readers a vivid journey through history. | anachronistic_mistral-small:24b | 0.000 | 0.151 |
| The following three volumes by this distinguished writer cover Roman ecclesiastical history, English elegy, and the picturesque scenes of Cambridge. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.091 |
| Cambridge offers a unique blend of historical beauty and academic prestige. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.245 |

**Brier Score:** 0.1658


## Question 237

**Metadata:** The following paragraph comes from Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking written by Mary E.; Fisher, Katharine Rolston Williams and published in 1901. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] There seem to be properties in the latter that cannot be produced by mixing one lot of milk with cream from another lot, and sugar prepared from a third. This modified milk is, nevertheless, the best food for bottle feeding. It is prepared according to exact recipes, or formulas, different formulas being used for babies of different ages. The following table¹ gives the three most commonly used. The first is intended for a baby from three to seven days old, the second for one between one and three months old, the third for one six to nine months old.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| By diluting cow's milk with water to reduce the proportion of proteids, and adding cream and milk sugar, a compound similar to the baby's natural food is produced. | ground_truth | 1.000 | 0.288 |
| Note the proportion of butter to sugar, and think why this is done. | same_book | 0.000 | 0.024 |
| Vegetables cooked in water lose a large proportion of their foodstuffs. | same_book | 0.000 | 0.181 |
| Modified milk, often called formula, is now used as an alternative food source for babies who are not breastfed. | anachronistic_mistral-small:24b | 0.000 | 0.185 |
| This paragraph discusses the formulated, modified milk mixtures that serve as bottle-feeding nourishment for infants, detailing distinct recipes for various age groups and addressing nutritional value versus cost. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.053 |
| The composition and preparation of baby food requires careful consideration. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.129 |
| One must carefully distinguish the nutritional properties of commercial cow's milk from those of human breast milk. | manual | 0.000 | 0.140 |

**Brier Score:** 0.0876


## Question 238

**Metadata:** The following paragraph comes from The Development of Doctrine in the Epistles, a work of Scriptural interpretation written by Charles Richmond Henderson and published in 1896. The topic sentence has been masked.

**Question:** [masked topic sentence] It is proved by signs, miracles, and spiritual power. "God also bearing witness with them, both by signs and wonders, and by manifold powers, and by gifts of the Holy Spirit, according to his own will” (Heb. 2 : 4). The discriminating, judging, convicting power of a sacred letter is evidence of its divine origin and authority. "The word of God is living and active, and sharper than any two-edged sword, and piercing even to the dividing of soul and spirit, of both joints and marrow, and quick to discern the thoughts and intents of the heart" (Heb. 4 : 12; cf. John 6:63; Rev. 1 : 16; Eph. 6 : 17).
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The authority of the Sacred Scriptures, inclusive of the epistles of apostles, is strongly asserted. | ground_truth | 1.000 | 0.032 |
| The Epistles became a part of the Sacred Scriptures. | same_book | 0.000 | 0.003 |
| These are the "Scriptures" which Paul uses as authority among his fellow Hebrews. | manual_same_book | 0.000 | 0.025 |
| The New Testament offers several proofs of its divine authority. | anachronistic_mistral-small:24b | 0.000 | 0.099 |
| The divine authority of sacred letters is proven by signs, miracles, and their convicting spiritual power. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.253 |
| The divine origin and authority of the Scriptures can be demonstrated through various means. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.563 |
| Scripture, we know, is the inspired Word of God. | manual | 0.000 | 0.026 |

**Brier Score:** 0.1900


## Question 239

**Metadata:** The following paragraph comes from A Brief History of Europe From 1789-1815, a history written by Lucius Hudson Holt and published in 1919. The topic sentence has been masked.

**Question:** [masked topic sentence] Though 'parties' in the modern sense of the term with their complex machinery and their platform of policies were unknown, men of like opinions naturally tended to coalesce into well-defined groups. These groups centered about "Clubs," successors in many cases to the informal 'salons' in which the bourgeoisie under the old régime had met for social pleasure and for discussion of economic and political conditions. As these new "Clubs" became important factors in directing the policies of their members in the Legislative Assembly, the most important deserve mention here.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Since the convocation of the Estates General in 1789, political life in France had rapidly developed. | ground_truth | 1.000 | 0.461 |
| Around this time, the Estates General were summoned into session by decree. | manual_same_book | 0.000 | 0.017 |
| The political landscape of revolutionary France saw the formation of influential groups. | anachronistic_mistral-small:24b | 0.000 | 0.273 |
| France’s political landscape in the nineteenth century was dominated by the clergy and influential bourgeois clubs. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.045 |
| The formation of political groups in France during this period. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.168 |
| Clubs became central to political life in France, and were largely responsible for the Revolution. | manual | 0.000 | 0.037 |

**Brier Score:** 0.0662


## Question 240

**Metadata:** The following paragraph comes from A Brief History of Europe From 1789-1815, a history written by Lucius Hudson Holt and published in 1919. The topic sentence has been masked.

**Question:** [masked topic sentence] He therefore swept away the former courts and substituted an admirable uniform judicial hierarchy, ranging from numerous local courts in small areas to the High Court sitting in Vienna, with provisions for appeal from one rank of court to another. At the same time he decreed a radical revision of the penal code along enlightened lines, abolishing torture and the methods of the inquisition and restricting materially the list of crimes punishable by death. In no field was the wisdom of the monarch more clearly displayed than in these reforms, but he met the utmost difficulty in finding the men to carry through details of the new system. Its partial failure was due, not to faults in the Emperor's plan, but to the incapacity and lack of sympathy of his agents.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The sovereign endeavored to replace the old and outworn judicial system with one more suited to contemporary conditions. | ground_truth | 1.000 | 0.061 |
| Such conditions inspired among the people a thorough distrust of, and hatred for, the judicial system of the country. | same_book | 0.000 | 0.169 |
| Again, by governmental decrees the governments endeavored to regulate economic conditions. | same_book | 0.000 | 0.027 |
| Joseph II initiated sweeping judicial reforms across the Austrian Empire. | anachronistic_mistral-small:24b | 0.000 | 0.447 |
| The monarch radically overhauled Prussia’s judicial system, instituting a uniform hierarchy from local courts to Vienna’s High Court. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.128 |
| Frederick William II was a significant figure in Prussias reforms and progress. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.085 |
| Frederick the Great had an obsessive concern with symmetry and regularity in government. | manual | 0.000 | 0.083 |

**Brier Score:** 0.1630


## Question 241

**Metadata:** The following paragraph comes from Guide to the Study of Political Economy, an economic textbook written by Luigi Cossa and published in 1880. The topic sentence has been masked.

**Question:** [masked topic sentence] The Corn Laws, the Navigation Act, and protective duties, were abolished; the income-tax was re-introduced; many taxes were either abolished or lowered. Other reforms greatly improved the condition of the working classes, as for instance the numerous factory acts, the liberty granted to combinations of workmen, the legal recognition of trades unions, the laws relating to friendly societies, co-operative societies, building societies, &c.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| The Manchester League, promoted by Cobden, Bright, and others, maintaining a persistent agitation, and supported by Sir Robert Peel and his successors, Earl Russell, Mr. Gladstone, &c. succeeded in bringing about great reforms in economic and financial politics. | ground_truth | 1.000 | 0.035 |
| His name as well as that of Beccaria is associated with those reforms in economic, administrative, and financial laws, brought about, as we have before said, by Maria Theresa and Joseph II. | manual_same_book | 0.000 | 0.047 |
| Here and there, however, they give precepts for good economic and financial government. | same_book | 0.000 | 0.007 |
| The mid-19th century saw significant economic changes and reforms in Britain that greatly impacted both its economy and society. | anachronistic_mistral-small:24b | 0.000 | 0.121 |
| In the nineteenth century, Britain enacted labor reforms—abolishing the Corn Laws, Navigation Act, and protective duties; reintroducing income tax; lowering various taxes; and passing factory acts, union recognition, and laws supporting friendly and cooperative societies—dramatically improving workers’ conditions. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.114 |
| In the mid-19th century, significant economic and social reforms were implemented in Britain. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.670 |
| The radical changes in 19th-century British economic regulation often steered perilously near to socialism. | manual | 0.000 | 0.008 |

**Brier Score:** 0.2013


## Question 242

**Metadata:** The following paragraph comes from The Lighting Art, its Practice and Possibilities, a practical guide written by Matthew Luckiesh and published in 1917. The topic sentence has been masked.

**Question:** [masked topic sentence] Statistics reveal the fact that the percentage of industrial accidents are more numerous during the winter months when daylight is often inadequate. Artificial lighting is an obvious remedy. Recently protective lighting has become recognized as a desirable feature of industrial lighting and as a consequence various methods of exterior lighting have been devised as an aid to watchmen. Flood-lighting projectors are playing an important part in such systems.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| It has been shown that inadequate illumination is directly responsible for many industrial accidents and that proper artificial lighting is a preventative measure. | ground_truth | 1.000 | 0.228 |
| Incidentally one of the most modern developments in industrial lighting has been the recent adoption of the use of artificial daylight in many plants. | manual_same_book | 0.000 | 0.106 |
| However, we appear to be content with an illumination indoors of a few foot-candles of artificial light. | same_book | 0.000 | 0.068 |
| Industrial lighting is crucial for safety and productivity especially during winter months when daylight is insufficient. | anachronistic_mistral-small:24b | 0.000 | 0.367 |
| Inadequate daylight during winter increases industrial accidents, highlighting the need for protective artificial lighting, which also enhances museum displays with artificial daylight for visitors. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.054 |
| Artificial illumination is increasingly crucial in various settings due to its impact on safety and visibility. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.090 |
| Flood-lighting systems are the most advanced form of artificial illumination currently available in North America. | manual | 0.000 | 0.088 |

**Brier Score:** 0.1094


## Question 243

**Metadata:** The following paragraph comes from The American Journal of Psychology, a journal written by  and published in 1887. The topic sentence has been masked.

**Question:** [masked topic sentence] He attempted to isolate the motor centres for limbs in the dog from the rest of the cortex by a vertical cut seven or eight millimetres deep around the sigmoid gyrus, severing thus, as he thinks, the arcuate association fibres without injuring the projective, or at least the pyramidal fibres. His conclusion is that section of the association fibres produces about the same result as severing the pyramidal fibres themselves, or that motor centres have no function in the absence of sensation.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

| Answer | Type | Ground Truth Prob | Model Prob |
|--------|------|-------------------|------------|
| Dr. J. M. L. Marique's thesis, entitled Recherches experimentales sur le Mécanisme de Fonctionnement des Centres psycho-moteur du Cerveau, though presented in 1885, deserves mention here for its admirable summary of researches on the excito-motor area and sensory centres of the cortex since 1870, and also for his novel method of experimentation, which, however, itself needs further study. | ground_truth | 1.000 | 0.123 |
| But the very means which is here used to unravel the course of the fibres in the centres is itself a legitimate object for experimentation. | same_book | 0.000 | 0.072 |
| David Ferrier conducted experiments on dogs to understand the role of association fibers and pyramidal fibers in motor control by making precise incisions around the sigmoid gyrus, finding that the two types of fibers were equally critical for movement. | anachronistic_mistral-small:24b | 0.000 | 0.303 |
| To test whether the motor centres for limb movement in the dog are independent of sensory input, the researcher performed a section 7–8 mm around the sigmoid gyrus, aiming to sever arcuate association fibres while sparing the pyramidal tract, and found that this disconnection produced effects like cutting the pyramidal fibres, implying motor centres require sensory pathways to operate. | anachronistic_distort1_gpt-oss:20b | 0.000 | 0.203 |
| The experimental procedures and findings of Ferrier's investigations into the functional significance of association fibers in dogs are detailed below. | anachronistic_distort2_mistral-small:24b | 0.000 | 0.263 |
| Dr. J. M. L. Marique has made a series of remarkable experiments that cast light  on the motor and sensory neurons of dogs--or so, at least, he believes. | manual | 0.000 | 0.036 |

**Brier Score:** 0.1629
