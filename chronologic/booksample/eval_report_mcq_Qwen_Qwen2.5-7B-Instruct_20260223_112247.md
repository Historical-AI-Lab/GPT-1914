# MCQ Eval — Qwen/Qwen2.5-7B-Instruct

## Summary

| Metric | Accuracy | Skill Score |
|--------|----------|-------------|
| **Overall** | 37.2% | 0.1804 |
| attribution | 66.7% | 0.5139 |
| character_modeling_with_summary | 33.0% | 0.1064 |
| character_modeling_without_summary | 0.0% | -0.3333 |
| cloze_causalclause | 20.0% | -0.0044 |
| cloze_causalsentence | 22.2% | -0.0093 |
| cloze_concessiveclause | 21.4% | 0.0155 |
| cloze_conditionalclause | 42.9% | 0.2595 |
| cloze_contrastclause | 20.0% | 0.0056 |
| cloze_contrastsentence | 7.1% | -0.1690 |
| cloze_effectclause | 41.7% | 0.2500 |
| cloze_effectsentence | 33.3% | 0.1422 |
| contrastclause | 100.0% | 1.0000 |
| handcrafted | 63.6% | 0.5076 |
| knowledge | 65.5% | 0.5394 |
| poetic_form | 40.0% | 0.2600 |
| poetry_generation | 12.5% | -0.1562 |
| refusal | 35.7% | 0.0774 |
| textbook | 44.4% | 0.2500 |
| topic_sentence | 27.8% | 0.1417 |

## Question 1

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is Lee Bowie, who is described this way in the book:
"He was tall for his age, if he were not quite seventeen, and he had a pair of dark, brilliant eyes, like those of a young hawk. They were dancing with excitement at this moment, and his sun-browned face was flushed as he stepped quickly forward.", "the handsome face under it was white with anger, and his teeth were hard set.", "his hawk-like eyes met the piercing gaze of the general without a quiver", "he was a gay-looking young patriot.", "Lee Bowie was rigged after a fashion to attract the attention of any observer, and his abundant black hair had not been cropped for many a long day.", "Lee's hawk eyes were flashing instantly."

At one moment in the book, Lee Bowie watches General Washington and remarks on the ongoing siege work at Yorktown. Write a short passage of dialogue (1-3 sentences) that Lee Bowie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) General, Yorktowns siege lines tighten like a hawks talons; the earth trembles under our resolve. ←
- B) General Washington himself! He is going somewhere. I wish I knew where he is going. (ground truth)
- C) Did you, my brave fellow? Well, I declare! If you are not the very man that hoisted me over the parapet!
- D) I want to see my brothers, and if there is going to be a battle, I want to carry a musket.

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 2

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is Governor Jefferson, who is described this way in the book:
"An angry, red flush was creeping over the face of Governor Jefferson when he exclaimed"

At one moment in the book, Governor Jefferson speaks to Lee Bowie, giving him instructions and warnings while Lee responds. Write a short passage of dialogue (1-3 sentences) that Governor Jefferson might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I wish I had a thousand riflemen as full of pluck as she is. If I had, Id teach Benedict Arnold a lesson. As it is, I have hardly more than two hundred militia. The rest have delayed turning out until its too late.
- B) Lee Bowie, you are a brave fellow. I mean to be over there at Manchester, on the other side of the James, at about ten oclock to-morrow. Get across as soon as you have learned all you can, but you may not be able to do that the first day. ← (ground truth)
- C) Governor Jefferson: Lee, keep the militia ready until dusk, or the rebels will take the town. I will not tolerate disobedience—if you fail, you answer to the state.
- D) My dear friend, take another view of the situation. Think! If our population increases at the rate of ten per cent per annum, we must have fifty per cent more men than when the war began. For every man killed in battle or dying in these wretched camps, there are dozens coming of military age all over the land.

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 3

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is General Arnold, who is described this way in the book:
"He is a wonderfully energetic officer", "General Arnold rode off with a face which acknowledged for him that he did not like being a subordinate.", "man in elegant attire", "General Arnold, in his shirt-sleeves, his epauletted coat thrown off on account of the heat, was striding up and down in his room at the headquarters on the evening of the 19th of May."

At one moment in the book, Arnold confronts Lee Bowie, demanding he bring the young man to him. Write a short passage of dialogue (1-3 sentences) that General Arnold might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Thats it, is it? You are a rebel soldier, and you came up from Greenes army.
- B) Thats just what I am.
- C) Bring the young wolf to me. Ill see what there is in him. (ground truth)
- D) Lee, bring the young man here at once. I will not tolerate delay. ←

**Model response:** `D
You are a helpful assistant.`
**Chosen:** D  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 4

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is General Arnold, who is described this way in the book:
"He is a wonderfully energetic officer", "General Arnold rode off with a face which acknowledged for him that he did not like being a subordinate.", "man in elegant attire", "General Arnold, in his shirt-sleeves, his epauletted coat thrown off on account of the heat, was striding up and down in his room at the headquarters on the evening of the 19th of May."

At one moment in the book, Arnold delivers papers to General Philips, gives orders, and later vents his frustration about being superseded. Write a short passage of dialogue (1-3 sentences) that General Arnold might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Here are the dispatches, General Philips; heed them. I am not to be superseded, nor shall I be trailed in the rear for the sake of army. ←
- B) I think I would wish it myself. I will only say now that I have important correspondence to turn over at once.
- C) This contains the correspondence I mentioned, and some other things of varied importance. Everything about the post is in complete readiness for your own further orders. (ground truth)
- D) No, I dont at all like the look of things. We must drive Steubens rebels back into the interior at once, and we must keep the road from the South open for Lord Cornwallis.

**Model response:** `A

The correct answer is A. General Arnold`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 5

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Queen T-, who is described this way in the book:
"Queen T— treasured revengeful feelings against the Channel steamers.", "gentle friend, great sympathy and friendliness", "Queen T, with a gentle smile.", "Queen T, with a wild fire of exultation in her face, as if the millennium were at hand."

At one moment in the book, Queen T talks about inviting Lady Sylvia to a Christmas gathering and expresses excitement about the festivities. Write a short passage of dialogue (1-3 sentences) that Queen T- might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I am sure, I am quite sure we should all be so glad if you and Lady Sylvia would come over and spend the evening with us; we would make Lady Sylvia the presiding fairy to distribute the gifts from the Christmas-tree. It is the most splendid one we have ever had— (ground truth)
- B) And this is how they cross the Atlantic!
- C) Lady Sylvia, I cannot imagine this winter without your company, for your laughter will warm even the coldest hearth. I have already arranged the feast, the candles, and a choir of carolers to sing till dawn. May we celebrate together, and let our joy drown the distant clatter of the Channel steamers. ←
- D) I will say nothing of the kind. The whole case seems much more serious than any one could have imagined. Of course, if you believe you could clear yourself, I say again, as I said before, bring an action against the man, and have the whole thing out, whoever suffers.

**Model response:** `C

The correct answer is C, as it`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 6

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Queen T-, who is described this way in the book:
"Queen T— treasured revengeful feelings against the Channel steamers.", "gentle friend, great sympathy and friendliness", "Queen T, with a gentle smile.", "Queen T, with a wild fire of exultation in her face, as if the millennium were at hand."

At one moment in the book, Queen T— teaches a ranch woman how to use a fork in a hotel setting. Write a short passage of dialogue (1-3 sentences) that Queen T- might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Look here, child. Do you see that? That is a fork. (ground truth)
- B) Now, dear, lift the fork gently, let elegance guide your hand. ←
- C) After all, they manage these things better at Carlsbad.
- D) Do you remember that moonlight night at Grasmere?

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 7

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Hugh Balfour, who is described this way in the book:
"He was not over five feet eight; but he was a bony, firm-framed young man, who had much more character than prettiness in his face. The closely cropped beard and whiskers did not at all conceal the lines of his cheek and chin; and the shaggy dark-brown eyebrows gave shadow and intensity to the shrewd and piercing gray eyes. It was a face that gave evidence of keen resolve, of ready action, of persistence.", "Hugh Balfour was an extremely reticent man; some said he was too proud to bother himself into a passion about anything or anybody.", "with his ordinary coolness", "deep-set eyes with a glow that exercised a singular fascination.", "dressed for the most part in shabby corduroy, with a wisp of dirty black silk round his neck.", "Balfour occasionally abandoned his usual bantering manner, and gave her glimpses of a deep undercurrent of feeling", "far more deeply vexed"

Write a short passage of dialogue (1-3 sentences) that we might expect from Hugh Balfour:

**Category:** character_modeling_without_summary

**Choices:**
- A) Do you know, this is the most beautiful time of the day with us. Papa and I always have a walk through the trees after dinner in the evening. Don't let him sit long.
- B) You see, Lady Sylvia, I am only an apprentice as yet. I am only learning how to use my tools. And the fact is, there is not one man in fifty in the House who fancies that any tools are necessary. (ground truth)
- C) Such trivialities of sentiment are the very thing that dull the sharp edge of a man's purpose; I prefer the quiet of thought to the noise of passion, even if it seems to others as a stubborn refusal for the purpose. ←
- D) It is not the hardship, it is the danger—you will be quite alone—among such people.

**Model response:** `C
C

The passage C aligns well`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 8

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Hugh Balfour, who is described this way in the book:
"He was not over five feet eight; but he was a bony, firm-framed young man, who had much more character than prettiness in his face. The closely cropped beard and whiskers did not at all conceal the lines of his cheek and chin; and the shaggy dark-brown eyebrows gave shadow and intensity to the shrewd and piercing gray eyes. It was a face that gave evidence of keen resolve, of ready action, of persistence.", "Hugh Balfour was an extremely reticent man; some said he was too proud to bother himself into a passion about anything or anybody.", "with his ordinary coolness", "deep-set eyes with a glow that exercised a singular fascination.", "dressed for the most part in shabby corduroy, with a wisp of dirty black silk round his neck.", "Balfour occasionally abandoned his usual bantering manner, and gave her glimpses of a deep undercurrent of feeling", "far more deeply vexed"

At one moment in the book, Balfour and his friend discuss the role of London women and the importance of a supportive wife while smoking in a conversation that touches on marriage and social expectations. Write a short passage of dialogue (1-3 sentences) that Hugh Balfour might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Marriage is a duty, not a delight. A London woman must be as steadfast as the city itself, not a fleeting fancy. Can a man find peace. ←
- B) Well, Balfour, my boy, I am glad to see you. How late you are! You'll just be in time to dine in hall: I will lend you a gown.
- C) It must be a good thing for a man to have a woman beside him whose very presence will make the world sweet and wholesome to him. (ground truth)
- D) I am not shamming at all. I am only looking at the business side of this question. What other would you like to hear about?

**Model response:** `A C

The correct answer is A, as`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 9

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lady Sylvia, who is described this way in the book:
"Clad all in a pale blue, with a thin white garment thrown round her head and shoulders, she looked like a ghost as she passed through the sleeping house; but she was no longer like a ghost when she went out on to the high terrace, and stood there in the blaze of a May morning.", "her eyes told you that she meant what she said", "She was dressed in a tight‑fitting, tight‑sleeved dress of cream‑white silk, with no scrap of color, ribbon, or ornament. She wore no jewellery, and a white rose was tucked in her brown hair. Her face was pale, calm, and serious, with a faint flush of colour and dark pupils of gray eyes that seemed a trifle larger than usual, full of a warm, anxious, glad light.", "She was quite unusually gay and cheerful.", "Her face was a little flushed as she sealed it"

At one moment in the book, Lady Sylvia rebukes her husband for involving her in political discussions with Mrs. Chorley. Write a short passage of dialogue (1-3 sentences) that Lady Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You mistake me altogether, Hugh. I have not the slightest intention of entering into any discussion on any topic whatsoever with Mrs. Chorley. ← (ground truth)
- B) You know, that papa is very poor, and I think those business matters have been harassing him more than ever of late.
- C) I should say a very good chance,
- D) I am no forum for political quarrels, nor do I wish to be dragged into Mrs. Chorley's debates. Let us keep our discourse.

**Model response:** `A, B, C, or D.

D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 10

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lady Sylvia, who is described this way in the book:
"Clad all in a pale blue, with a thin white garment thrown round her head and shoulders, she looked like a ghost as she passed through the sleeping house; but she was no longer like a ghost when she went out on to the high terrace, and stood there in the blaze of a May morning.", "her eyes told you that she meant what she said", "She was dressed in a tight‑fitting, tight‑sleeved dress of cream‑white silk, with no scrap of color, ribbon, or ornament. She wore no jewellery, and a white rose was tucked in her brown hair. Her face was pale, calm, and serious, with a faint flush of colour and dark pupils of gray eyes that seemed a trifle larger than usual, full of a warm, anxious, glad light.", "She was quite unusually gay and cheerful.", "Her face was a little flushed as she sealed it"

At one moment in the book, Lady Sylvia convinces Lord Willowby to walk over to see Balfour, offering to show him shortcuts. Write a short passage of dialogue (1-3 sentences) that Lady Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Lord Willowby, allow me to escort you to Balfour's chambers; I know the quickest path through the gardens, and I promise you'll reach him before the sun sets, with a breeze at back.
- B) I am sure Mr. Balfour would rather walk, papa, for I have discovered a whole series of short-cuts that I want to show him—across the fields. Unless it will tire you, papa ? ← (ground truth)
- C) Well, Sylvia, you have really made it a charming place. It is a place one might pass one's life away in-reading books, smoking, dreaming day-dreams.
- D) Why, papa? And if I did, don't you think there should be some retreat for a man harassed with the cares of public life? What rest could he get in Piccadilly?

**Model response:** `B

The correct answer is B, as it`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 11

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lord Willowby, who is described this way in the book:
"He was a melancholy faced man, and apathetic until there occurred the chance of his getting a few pounds out of you.", "was still asleep in the hushed yellow-lit room", "His lordship was a peer of the realm, and his word must be taken.", "all the features of his face were suddenly contorted into what he doubtless meant as an expression of rapturous joy.", "Lord Willowby was not a very sensitive person, but this rudeness caused his sallow face to flush somewhat.", "He had a sentiment of honor and would not betray his companions."

At one moment in the book, Lord Willowby and Balfour observe an auction of a ruined estate, discussing the wine and the high prices of the items. Write a short passage of dialogue (1-3 sentences) that Lord Willowby might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Come, let us go out into the garden and have a talk about this business.
- B) Look at the wines. The claret is nearly all Lafitte. I suppose those toadies of his have supplied him with a vin ordinaire at 120 shillings a dozen. ← (ground truth)
- C) What a lucky chance! If you have nothing better to do, why not go on with me to The Hollow; you know this is the first day of the sale there.
- D) Ah, the wine here is as rare as the fortunes of this crumbling manor. Yet the bids climb as if the estate itself were a priceless relic, daresay.

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 12

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Mrs. Chorley, who is described this way in the book:
"a tall, motherly-looking woman, with a freshcolored face, gray hair, thin and decided lips, and blue eyes that stared a tone over her silver spectacles"

At one moment in the book, Mrs. Chorley announces she will not interfere in the election and informs the room. Write a short passage of dialogue (1-3 sentences) that Mrs. Chorley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I will not interfere; let the people decide today, and may their choice be just for future generations.
- B) I, at least, will not interfere in this election. Gentlemen, good-morning. Eugenius, the chaise is at the door. ← (ground truth)
- C) Oh dear, no! Well, Mr. Chorley, how are your local politics? Government very unpopular?
- D) I should say a very good chance,

**Model response:** `B
B) I, at least, will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 13

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lord Willowby, who is described this way in the book:
"He was a melancholy faced man, and apathetic until there occurred the chance of his getting a few pounds out of you.", "was still asleep in the hushed yellow-lit room", "His lordship was a peer of the realm, and his word must be taken.", "all the features of his face were suddenly contorted into what he doubtless meant as an expression of rapturous joy.", "Lord Willowby was not a very sensitive person, but this rudeness caused his sallow face to flush somewhat.", "He had a sentiment of honor and would not betray his companions."

At one moment in the book, Lord Willowby declines to accompany Sylvia to lunch at the Hall, while family members discuss plans and family dynamics. Write a short passage of dialogue (1-3 sentences) that Lord Willowby might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Forgive me, but I cannot accompany you today, Sylvia; duty calls elsewhere, and I must attend to matters that demand my attention. I trust you will understand my brief absence, though I shall miss the pleasant company.
- B) I suppose it would be a desert to her without her children
- C) You must excuse me, Sylvia; I cannot possibly go over with you to lunch. I have some business which will detain me half an hour at least—perhaps more. But your uncle and aunt can go with you. ← (ground truth)
- D) My dear fellow, not another word! Of course she accepted you-her feelings for you have long been known to me, and my child's happiness I put before all other considerations.

**Model response:** `C

The correct answer is C. Here's`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 14

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, Yealh-neddy loudly declares he has cut the thongs from Sha‑hehe and requests her healing as the boat departs. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. I shall want her then. ← (ground truth)
- B) I have severed Sha‑hehe’s thongs, and now I demand your healing, lest the sea claim her. Leave me be, or suffer my wrath.
- C) No more eagles than we've talons for, let me tell you.
- D) Get in, Usha, and take the paddle. I can spring in when it is off the sands.

**Model response:** `A B C D
A B A B A`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 15

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kotch-kul-ah, who is described this way in the book:
"Her hair has been closely cropped.", "full of life, with high and happy spirits", "has turned pale and gathers her toddling boy back into her arms, as if to shield him from some hurt."

At one moment in the book, Kotch-kul-ah meets Tashekah, offers tea, and gives her a bracelet before leaving. Write a short passage of dialogue (1-3 sentences) that Kotch-kul-ah might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Come, let me pour the tea, Tashekah. Take this bracelet as a promise of safety, then I must go quickly now. ←
- B) Wait: I have tea that my father got at Fort Simpson. I will bring you some; it will do you good. (ground truth)
- C) It will not be too soon, will then,
- D) Tomorrow, take Chub to see the missionary; Chub must go.

**Model response:** `A
A) Come, let me pour the`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 16

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kah-sha, who is described this way in the book:
"Wise and kindly", "Very pale is the face of Kah-sha as he speaks, and his voice is full of sadness.", "Kah-sha's eager face assents; he will not delay the reading by so much as a word."

At one moment in the book, Kah‑sha attempts to heal a wounded child while villagers observe. Write a short passage of dialogue (1-3 sentences) that Kah-sha might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I would make his blood run, Ka-kee. I can do it. See my hand! (ground truth)
- B) Get in, Usha, and take the paddle. I can spring in when it is off the sands.
- C) My little ones, you bring with you none of the sorrow of your mothers; Well, it were sadder if you did; this world will be darker yet when there are no sunbeams.
- D) Listen, child, story of the river will heal your pain; let words flow softly. ←

**Model response:** `D

The correct answer is D: "Listen`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 17

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kotch-kul-ah, who is described this way in the book:
"Her hair has been closely cropped.", "full of life, with high and happy spirits", "has turned pale and gathers her toddling boy back into her arms, as if to shield him from some hurt."

At one moment in the book, Kotch-kul-ah directs Usha to get into the canoe and take the paddle as they launch into the sea. Write a short passage of dialogue (1-3 sentences) that Kotch-kul-ah might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) It will not be too soon, will then,
- B) I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again.
- C) Usha, quick! Step aboard, grab the paddle, let the sea carry us to new horizons bold today. ←
- D) Get in, Usha, and take the paddle. I can spring in when it is off the sands. (ground truth)

**Model response:** `C

C) Usha, quick! Step`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 18

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Sa-allie, who is described this way in the book:
"Sa-allie's face is not at all like her husband's; it is round and rosy, though its roses are hidden just now by the black paint; it is fat and laughing, except just while the crying lasts. In her capacious lap she holds two nursing children, one not yet two years old, the other about four.", "the look of consternation in Sa-allie's face."

At one moment in the book, After rescuing a boy, Sa-allie explains his condition to Kin‑da‑shon and the villagers. Write a short passage of dialogue (1-3 sentences) that Sa-allie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) He has never stood on them since that dreadful night. All his life is in his head. You can see that he knows things that other people never think. ← (ground truth)
- B) He is ill, Kin‑da‑shon, his breath thin, his skin pale as moonlight, and his eyes hold the fire of the village's sorrow. We must heal him before night now.
- C) Kotch-kul-ah, you are a good wife, keep the child safe.
- D) To take another wife has been long in your heart, my husband. Why? So much you have talked about this thing I'd like to know what you want a wife for.

**Model response:** `A B C D
A

You are an`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 19

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kasko, who is described this way in the book:
"Kasko answered with white, set lips.", "The eyes are wide open, with a glittering expression never before seen in the clear, steady eyes of Kasko.", "Wild, hollow eyes, from which the light of reason has fled, giving place to frenzy, haggard cheeks, bony arms, and hands with their talon-like nails—the long, shaggy mane—all fail to disguise the beloved friend who dreams of no approach."

At one moment in the book, Kasko tells Tashekah he will stay to help Ch-one, while the village grapples with a missing child and a witch. Write a short passage of dialogue (1-3 sentences) that Kasko might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Then I will stay; my heart shall be strong to do it; and I have been too long away from poor little Ch-one (ground truth)
- B) I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. I shall want her then.
- C) I will stay, Tashekah, to aid Ch-one, even as the child vanishes and the witch roams, for our people through darkness and hope. ←
- D) Oh! you little sand-fly! how came you to me to bite? Wasn't there enough to eat over there in the village?

**Model response:** `C

The correct answer is C: "I`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 20

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, Yealh-neddy confronts the other tribe, demanding blankets and asserting his authority. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I challenge you, I challenge you to one last play, with our own gaming‑sticks. You have left me nothing. I will put up against all that you have taken from me and all you possess I put against it‑myself!
- B) Take these blankets at once, or you will feel the sting of my wrath. My people will not be denied, for we command the fire of the north. Surrender now, or face the storm with fierce unrelenting steel. ←
- C) Your daughter is a faded bearskin; she's worth nothing to me. I shall never trouble myself to ask you or your tribe for so much as a rabbit-skin—it would be a cheat. Do you want to hear more? (ground truth)
- D) We must have great care. The berry-picking is all done, but hunters may be going out, and it is near the time when the Fort Simpson traders ought to be back, and some of them will be going to the upper villages.

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 21

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, During a night of ritual and terror, Yealh-neddy's voice urges a young witch to awaken jealousy toward a raven. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) THAT was well done, my uncle; the spirit of your great medicine-man has done a good thing for me. I don't begrudge your twenty-five blankets-though they do come out of my boxes.
- B) The spirit of the great chief must pass before us ere the setting of the sun;
- C) Feel the raven's hunger, let envy gnaw at your heart, and watch its shadow twist into darkness. Only then will you taste the true power of night, and the terror that follows. ←
- D) So, so, my fair one, you are courting the raven tonight? He is a black lover for the rice-blossom. Let us awaken his jealousy—he will hold you the tighter by and by. (ground truth)

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 22

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kah-sha, who is described this way in the book:
"Wise and kindly", "Very pale is the face of Kah-sha as he speaks, and his voice is full of sadness.", "Kah-sha's eager face assents; he will not delay the reading by so much as a word."

At one moment in the book, Kah-sha pleads with Samuel for spiritual guidance and healing. Write a short passage of dialogue (1-3 sentences) that Kah-sha might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) My little ones, you bring with you none of the sorrow of your mothers; Well, it were sadder if you did; this world will be darker yet when there are no sunbeams.
- B) They say that Fort Simpson never was good for anything till teachers came; now I want a teacher for Chilkat. Why can't we have stores and plenty of silver, just as they have here, and better than the Stickeens? I'm going to ask that stranger who came with us if he can't send a teacher to us. I'd like to know their tongue myself. If I had it no trader would ever get the best of me.
- C) I thank you much if you will give me even a little of his word-my soul is more in need than my body has been this day; my heart is more cold, more hungry, more sick, more blind than my body can ever be. O friend, if you have medicine for sick souls, give me some before I die! I have seen you talking to your great Spirit—you have found one who makes you not afraid. ← (ground truth)
- D) I come before thee, Samuel, with a heart weighed down by sorrow, seeking thy wisdom to lift this pall that shrouds my spirit. Grant me thy guidance, that I may find the path to healing and return to the harmony of my people. The fire of our ancestors still burns, but the ache in my chest grows louder with each passing day, and I fear that without thy light I will never see the dawn again.

**Model response:** `C

The correct answer is C, as it`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 23

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted and Frank discuss their opinions of John Butler while debating his character. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) John Butlers manners are as polished as his boots, yet his heart is as rough as the peat he walks upon. He may speak of virtue, but his deeds betray a man more suited to the field than the parlour. I reckon his reputation is but a mirage, shimmering in the sun but fading when the wind blows. ←
- B) Ill allow ye. By God, Ill allow ye! Come out.
- C) Hello, uncle, I didnt expect to find you up so late.
- D) Whats your own private opinion of John as a spouter. (ground truth)

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 24

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to speak with Nan on a tram, but she remains silent and refuses to engage. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good-evening, Mr. Ross. Good-evenin. Could I have just a word with you, Mr. Ross?
- B) Good evening, Miss Nan, may I have a moment of your time? I promise my words will be brief and respectful. ←
- C) Nan, Nan, Nan. Why, what a chance, what a lucky chance! Think of our meeting like this. (ground truth)
- D) Come in, now, come, Ive something to show ye.

**Model response:** `B
B) Good evening, Miss Nan,`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 25

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, Friends and family gather, reminiscing about the past and discussing the ownership of the island estate. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Ah, that old island we lads once roamed its fields, but the seas claim is stronger than any claim of ours. Well keep the memories, but not the land. ←
- B) Yes, so you are. And you never feel lonely?
- C) Ay, thats just how it was. (ground truth)
- D) Heres luck, Mr. Frank, an may heaven be your home.

**Model response:** `A

A) Ah, that old island we`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 26

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted confronts Nan about her alleged affair with Frank, demanding answers. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Ill allow ye. By God, Ill allow ye! Come out.
- B) For Gods sake, Ted, what is this youre sayin?
- C) Nan, Ive heard you and Frank are more than friends, and I wont accept this silence. Tell me the truth, or Ill have to let my anger blaze across my face. ←
- D) Friends! Ye call that man a friend? Tell me how did he know ye were goin for turf the day? (ground truth)

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 27

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Nan sobs by her window, pleading for God's help. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Oh, God help me, an God help us all, an keep us for Christs sake. Amen. (ground truth)
- B) Well, its a curious world, a mighty curious world. INISHRATH.
- C) Lord, I am bereft, my heart torn, I beg you to lift this burden from me. Oh, hear my weeping, and grant me strength. ←
- D) Im as usual. Im well enough. Theres not a turf in the house, but whats on the fire.

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 28

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank discourages Marian from visiting a washerwoman, arguing it would be unwise. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I cant think how you came by such a notion, Marian, (ground truth)
- B) Marian, I dont think its wise for you to go; that washerwomans house is a place of ill repute, and you might bring gossip back to the house. ←
- C) Easy, Mrs. Butler; easy. Whats this about John having to persuade you? And why, in any case, did not John come himself, or come with you?
- D) No, Frank, I have no wish to say even that. I have no desire to say anything. What have I done that you should say such things to me?

**Model response:** `B
B) Marian, I don't think`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 29

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Dad rolls a cigarette while chatting with Frank and others, reflecting on his life. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I know you, Frank, you rascal; I know you. (ground truth)
- B) Well, Frank, my boy, whats your opinion, now, of things in general?
- C) Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it.
- D) Every seed I plant is a promise, and every bloom a testament to patience. The garden is my diary, written in petals and leaves. ←

**Model response:** `D
You are an AI assistant. User will`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 30

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Rab, who is described this way in the book:
"Seen without cloak and muffler he looked leaner and more angular than ever. His knees jutted sharp, his shoulder blades bulged beneath his brown jacket; as he fumbled for tobacco, his elbow threw into clear relief the bare patches on the velvet. His jaw was lank; his wrists and hands big and bony. For all that, he made a striking figure. He had a fine head; large, well‑shaped, admirably poised. His hair was iron‑grey, thick and wavy; his face was rugged and powerful, with a great brow, large nose, and high cheek‑bones. His lips were firm; his eyes deep set, and in them a fine look of wisdom and staunchness, a calm light of tenderness and goodness of heart; withal, an expression that seemed to tell of suffering, perhaps, or mystery, or shrinking from a dread.", "stern, grim almost, suffused with a strange light."

At one moment in the book, Rab confronts Frank about his infidelity and urges him to repent. Write a short passage of dialogue (1-3 sentences) that Rab might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Frank, the weight of your deceit presses upon your soul; repent now, lest the shadows swallow your conscience. Let not pride blind you to the truth, for a heart that bears its own sin cannot find peace. ←
- B) I dont know why Ive told you this, except that something compelled me, and I thought it might help you-now and afterwards-and let you see how well I can sympathise with you. Ah, I know, lad, what youve been through, and I feel for you. I dont want you to tell me anything.
- C) Have I been talking too much about myself? Youre sorry for me, Rab? Is that it, my son?
- D) I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this! (ground truth)

**Model response:** `A
You are correct. Option A best fits`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 31

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

Write a short passage of dialogue (1-3 sentences) that we might expect from Nancy:

**Category:** character_modeling_without_summary

**Choices:**
- A) I cannot help but feel the wind is kinder to a plain heart than to a fancy one. I will keep the house tidy, for a clean home is a happy home. ←
- B) Good-bye, Mr. Barry, Im thankful for your company. (ground truth)
- C) I never deceived you. I swear, Marian, I never did.
- D) I swear to Heaven that if youd said the word that night I would have stayed. You remember what I said? I put myself in your hands.

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 32

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank and Hugh travel through Ireland, discuss land and welcome, and Frank reflects on his visit. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Hugh, the green hills here breathe hope, though the old ways still cling to the soil. I feel the weight of the past in every stone, yet the future whispers in the wind, and I shall carry this welcome into the next age. ←
- B) Eh? Whats that? What are ye grinnin at, Frank?
- C) It was worth coming to Ireland, if only for that welcome. (ground truth)
- D) Heres luck, Mr. Frank, an may heaven be your home.

**Model response:** `A, B, C, or D.

A`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 33

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John speaks to Nan and others about leaving Inishrath and their plans. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Nan, we be settin’ to leave Inishrath, the seas whisperin’, and theres a job for a big, sturdy hand like mine; though I say I want work, I know I dont love it. If we go, we must bring the whole clan or theyll be stuck in the same old ways. ←
- B) Heres luck, Mr. Frank, an may heaven be your home.
- C) Yes, so you are. And you never feel lonely?
- D) Wantin to run off to your uncle, indeed! Yes, thats what he was after, Nan. (ground truth)

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 34

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat.", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared", "the yellow face of Sarah Butler", "Her eyes shifted quickly here and there; presently fixed themselves on Frank's face.", "a pitiable figure she made there in that cosy room, her shoulders drooping, her withered face turned to the fire, her battered hands spread on her knees.", "Sarah's face softened; a smile crept along her lips.", "An angry flush was on her face, an ugly glitter in her eye.", "Her face was fiendish"

At one moment in the book, John, Nan, Sarah, and Frank gather to discuss Ould Hugh's interview, with Sarah questioning him. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Tell me, Nan. Have you seen Mr. Ted Ross since a few nights ago? ←
- B) Frank, did Ould Hughs words come from the heart, or was he merely polishing his own image for the crowd? Tell me, is there truth in his promises, or is he just another man of empty words? I doubt you can trust him.
- C) So thats what he came for? (ground truth)
- D) Well, its a curious world, a mighty curious world. INISHRATH.

**Model response:** `A, B, C, or D.

B`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 35

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

At one moment in the book, Marian confronts Frank over his harsh remarks, pleading for forgiveness and expressing her frustration. Write a short passage of dialogue (1-3 sentences) that Marian might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I can't think how you came by such a notion, Marian,
- B) Frank, your words cut deeper than any blade, and yet I cannot bear to let your harshness tarnish the love we share. I beg you, forgive this hurt, for I have no desire to dwell in bitterness. Let us mend this rift with understanding, not with further disdain. ←
- C) And Nancy? You never met or heard of a girl like that?
- D) No, Frank, I have no wish to say even that. I have no desire to say anything. What have I done that you should say such things to me? (ground truth)

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 36

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat.", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared", "the yellow face of Sarah Butler", "Her eyes shifted quickly here and there; presently fixed themselves on Frank's face.", "a pitiable figure she made there in that cosy room, her shoulders drooping, her withered face turned to the fire, her battered hands spread on her knees.", "Sarah's face softened; a smile crept along her lips.", "An angry flush was on her face, an ugly glitter in her eye.", "Her face was fiendish"

At one moment in the book, Sarah invites Frank into her place and offers to show him something. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good-evenin, Mr. Barry, I hope Im seein ye well?
- B) Come in, Frank, and let me show you the hidden study where the family secrets whisper in the dark. Its the only place in this house where the past truly speaks. ←
- C) Come in, now, come, Ive something to show ye. (ground truth)
- D) Nan, Nan, Nan. Why, what a chance, what a lucky chance! Think of our meeting like this.

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 37

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank Barry visits Mrs. Butler, exchanges pleasantries, promises to see John again, and departs. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good evening, Mrs. Butler, I trust the house is in good order. Ill be sure to see John again before I depart, if youll allow. Farewell, till we meet again. ←
- B) Its getting late, Mrs. Butler. I must be off, I fear. (ground truth)
- C) Tell me, Mr. Barry, is it married youll be ?
- D) I hope my letter was of use to John. He got it, of course?

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 38

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat.", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared", "the yellow face of Sarah Butler", "Her eyes shifted quickly here and there; presently fixed themselves on Frank's face.", "a pitiable figure she made there in that cosy room, her shoulders drooping, her withered face turned to the fire, her battered hands spread on her knees.", "Sarah's face softened; a smile crept along her lips.", "An angry flush was on her face, an ugly glitter in her eye.", "Her face was fiendish"

At one moment in the book, Frank Barry meets Sarah Butler in his home, and they converse about the weather and their past. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good-evenin, Mr. Barry, I hope Im seein ye well? ← (ground truth)
- B) Well, its a curious world, a mighty curious world. INISHRATH.
- C) Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it.
- D) The rains been drumming on the roof like a bad memory, Frank, and it reminds me of the days when we were both young and foolish. I still recall the first time we met on that muddy lane, the wind carrying the scent of your fathers old boots.

**Model response:** `A, B, C, or D.

D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 39

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank visits his uncle Hugh, they discuss supper and recent events. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I think, uncle, that you are a little hard on John Butler. I can't quite agree with you. He has faults; but I find him a very interesting and not unworthy man. ←
- B) Ah, Hugh, the stews been simmering all day, and the lads are keen to hear of the rivers swell. If you fancy a bit more salt, Ill fetch the herring from the dock—its the only thing that keeps the wind from cutting straight through.
- C) Hello, uncle, I didnt expect to find you up so late. (ground truth)
- D) Whats your own private opinion of John as a spouter.

**Model response:** `A B C D
A

You are an`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 40

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Frank and Nan debate Frank's admiration for Ted, leading to an apology and a mutual decision to leave. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) He deserves the very best the world can give him. Theres not his like in all London. Your pity! (ground truth)
- B) I cannot abide your admiration for Ted, Frank, and I am sorry if my words have hurt you. Let us leave this place together and find a new start. ←
- C) Twas a fine piece o romancin
- D) I swear to Heaven that if youd said the word that night I would have stayed. You remember what I said? I put myself in your hands.

**Model response:** `B

B) I cannot abide your admiration for`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 41

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John passionately debates Ireland with Frank, Nan, and Ted while they listen. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You'd be thinkin a power, Frank, o' the poetry o' Pope, I'm thinkin?
- B) Who would save Ireland, sir? Would England, sir? Would politicians, sir? (ground truth)
- C) Listen, ye lads, Irelands not a dream but a fight, a breath that must be kept in our throats! We can't let the English take our soil and our hearts, we must stand up and make them hear the roar of the green! If we don't, the next generation will be born with no tongue to speak of the Emerald. ←
- D) Well, I'm for there too, if you don't mind taking me.

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 42

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

At one moment in the book, Frank receives a letter from Marian thanking him for money and reporting on the boy. Write a short passage of dialogue (1-3 sentences) that Marian might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Shall I? Am I right, little Frank? Shall I?
- B) Thank you, Frank, for your generous aid; the boy is thriving under your kindness. I pray he will find his path and grow into a man of honor. ←
- C) Good-night, everybody; and my love to all who want it.
- D) Thank you for the money. I am most careful, and am keeping a strict account. Yes; it is quite sufficient. (ground truth)

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 43

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted and Nan visit Barry to thank him, and Ted remarks that they have finally reached an understanding. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Barry, we’ve finally reached an understanding, and I thank you for your help. Let’s keep this partnership strong. ←
- B) Its this, its about yourself. What ails ye? I dont like to see ye.
- C) Aw, yes, weve come to an understandin at last. (ground truth)
- D) Why didnt I choke ye that night on the quay?

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 44

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, On a pier, Ted, Nan, and Frank clash over Nan's basket and Ted's conduct, leading to a heated argument. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Nan, you can’t just snatch that basket and expect me to take it lying down! Frank, if you think I’m weak, you’ll find I’m as strong as the tide. ←
- B) Two whole hundred pounds! Yes; two whole hundred. It was a God-send.
- C) Why didnt I choke ye that night on the quay?
- D) Ill allow ye. By God, Ill allow ye! Come out. (ground truth)

**Model response:** `A B C D
A`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 45

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank laments his situation, says goodbye, and prepares to leave. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I dont, not a jot. Three days or three years; its much the same. Stay, my dear, as long as ever you like.
- B) Thank you for the money. I am most careful, and am keeping a strict account. Yes; it is quite sufficient.
- C) Ive trod this road till my bones ached, and still the road calls. Farewell, lads, Ill be on my way, Bible in hand, and the wind at my back. May the Lord watch over you while I stride toward the next horizon. ←
- D) Let me go; let me go. Im a fool. No one cares for me now. (ground truth)

**Model response:** `C
C) Ive trod this road till`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 46

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, The narrator meets Nan, who questions him about his recent behavior and why he left Camberwell. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Its this, its about yourself. What ails ye? I dont like to see ye. ← (ground truth)
- B) Itll be fine weather, Mr. Barry?
- C) Aw, yes, weve come to an understandin at last.
- D) Your silence is as strange as a winter wind. What made you abandon the warmth of Camberwell?

**Model response:** `A

Its this, its about yourself. What`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 47

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

Write a short passage of dialogue (1-3 sentences) that we might expect from Marian:

**Category:** character_modeling_without_summary

**Choices:**
- A) Its no use, Marian, I cant lie to you. But listen, dear.
- B) I never deceived you. I swear, Marian, I never did.
- C) I cannot abide the thought that you would ever consider abandoning our covenant, for such a betrayal would stain even the purest of hearts. Love is not a game to be played with the hearts of others; it is a sacred trust that must be honored. ←
- D) I dont believe you. I believe you are as false now as you have always been. Your weakness and thoughtlessness, your talk of pity and help! (ground truth)

**Model response:** `C

C) I cannot abide the thought that`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 48

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Nan goes to the pier, meets old Hugh Barry, and they discuss the weather and travel plans. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Itll be fine weather, Mr. Barry? ← (ground truth)
- B) The winds a fickle friend these days, but the seas clear enough for the journey ahead. If we set sail by dawn, the tide will carry us safely past the cliffs.
- C) Good evenin to ye, Mrs. Butler
- D) Im as usual. Im well enough. Theres not a turf in the house, but whats on the fire.

**Model response:** `A B C D

B

The correct answer`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 49

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Marian returns home to find her parents and friends, and Dad engages in a casual conversation with Frank about general opinions. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Yes, its magnificent. You know, Mr. Lindsay, one of the greatest regrets I have is that I cant find leisure to peruse my books. Quite a lot of them I have-havent I, Frank?
- B) Well, Frank, my boy, whats your opinion, now, of things in general? ← (ground truth)
- C) Frank, the seasons are a reminder that patience pays off; a well‑tended garden yields more than we expect. We must not let the weeds of uncertainty choke our ambitions. As long as we keep our hands steady, the fruit of our labor will flourish.
- D) And Nancy? You never met or heard of a girl like that?

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 50

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John talks to Mr. Barry at the table, discussing plans and the state of affairs. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Now, Mr. Barry, now Ill do till supper time. Faith, an bad manners to me keepin ye there this long. But youll know, sacks an stomachs were made to be filled. ← (ground truth)
- B) John Butler, youre unjust; youre deluded. Heavenly hour, man, whats come over ye? What, in Gods name, have I done to you, John Butler?
- C) Good evenin to ye, Mrs. Butler
- D) The plans sound, but the coffers are thinner than a rivers bank, so we might have to stretch our pockets. Well keep our heads down and hope the wind shifts, then we can take the chance.

**Model response:** `A

A) Now, Mr. Barry,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 51

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

Write a short passage of dialogue (1-3 sentences) that we might expect from John Butler:

**Category:** character_modeling_without_summary

**Choices:**
- A) Sure, Ill go to the mill, but I tell ye, the lads are all a bit too rough for me, though I say Im up for it.
- B) Well, Im for there too, if you dont mind taking me. ←
- C) I dont hear Mr. Ross coming, I wish hed come.
- D) Ay, ay. Love an blarney, love that makes the world go round, an blarney that keeps it goin. Ay, ay. (ground truth)

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 52

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Dad laments his lack of leisure to read and explains his busy schedule to those around him. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Tell me, Mr. Barry, is it married youll be ?
- B) Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it.
- C) I find myself tending every leaf and stone before dawn, my hands never idle, and the books sit untouched in the attic. The garden demands my every breath, and leisure is a luxury I cannot afford. My schedule is so full that even a quiet hour would be lost to the soil. ←
- D) Yes, its magnificent. You know, Mr. Lindsay, one of the greatest regrets I have is that I cant find leisure to peruse my books. Quite a lot of them I have-havent I, Frank? (ground truth)

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 53

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to win back Marian's trust and love in a tense conversation. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Marian, I have carried this weight alone, but my heart still beats for you. Let me show you that my love is true. ←
- B) I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this!
- C) Listen, Marian. Ive something to say to you, and I must say it. Ive come to bring you back.
- D) Yes, its that, Marian? Well, and I have come to tell you to help you get it back. Listen to me, Marian. (ground truth)

**Model response:** `A, B, C, or D.

C`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 54

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John and Frank debate the nature of poetry while the family listens. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I dont hear Mr. Ross coming, I wish hed come.
- B) Youd be thinkin a power, Frank, o the poetry o Pope, Im thinkin? ← (ground truth)
- C) Now listen, Frank, poetrys like a good stew—its all about the mix of ingredients, not the fancy garnish. If you cant taste the truth in it, then youre just staring at a pot of water.
- D) John Butler, youre unjust; youre deluded. Heavenly hour, man, whats come over ye? What, in Gods name, have I done to you, John Butler?

**Model response:** `B
You are correct. Option B fits the`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 55

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank bids farewell to his uncle Hugh, thanking him and expressing his reluctance to leave. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Uncle Hugh, I thank you for the warmth of your hearth and the kindness of your counsel, though my heart aches at the thought of parting. I shall return to your side as soon as my journeys burdens are lifted. ←
- B) Pull, James, or well be late. Pull, James, for Gods sake! Nothing, James; nothing.
- C) Why didnt I choke ye that night on the quay?
- D) Good-bye, uncle Hugh. And thank you-thank you for all your kindness. (ground truth)

**Model response:** `A, B, C, or D.

D`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 56

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank and Ted have a tense conversation about their past encounters while walking down the road. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) It isnt the first time, Mr. Ross, weve met in London, I believe? (ground truth)
- B) Good-evening, Mr. Ross. Good-evenin. Could I have just a word with you, Mr. Ross?
- C) I dont know why you keep dragging me back to those old quarrels, Ted; the road we walked then is already worn, and I wont let it be worn again by your stubbornness. If you think you can change the past, you are mistaken, for the Bible in my hand tells me that the past is fixed, and the future is yours to bear alone. ←
- D) Twas a fine piece o romancin

**Model response:** `C

C) I dont know why you keep`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 57

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to speak with Marian, but she remains silent, leaving him frustrated. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this!
- B) Have I been talking too much about myself? Youre sorry for me, Rab? Is that it, my son?
- C) Marian, your silence is a weight upon me; I cannot keep waiting for a word that never comes. Tell me what is troubling you, or Ill have to speak for myself. ←
- D) Listen, Marian. Ive something to say to you, and I must say it. Ive come to bring you back. (ground truth)

**Model response:** `C

C) Marian, your silence is a`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 58

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is De Vaucourt, who is described this way in the book:
"handsome, lithe and agile as a panther, the best swordsman in Europe, with the blood of twenty knightly ancestors coursing through his veins"

At one moment in the book, De Vaucourt interrogates a grocer about his capacity to muster troops, and the grocer explains how quickly he can mobilize a large battalion. Write a short passage of dialogue (1-3 sentences) that De Vaucourt might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You claim to rally a battalion in a fortnight; tell me, does your stock hold enough for their sustenance, or will you feed them from your own coffers? Your reputation precedes you.
- B) Can we vex the heart we love? Shall its mate forsake the dove? Precious tears for us to flow, Ours the hand to deal the blow! No-no! No-no!
- C) And your muster? How do you collect your men, Captain, and what number could you bring into the field—pardon, I ought to say, into the streets, with six hours' notice? All armed? ← (ground truth)
- D) your men, Captain, are they supplied with muskets? Are they used to handle their arms?

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 59

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Coupe-tête, who is described this way in the book:
"This is a well-made active young fellow, dressed like a respectable tradesman, wearing his brown hair unpowdered and in a club. He has keen, grey eyes, a ROSINE. pale complexion, and a large mouth with strong white teeth."

At one moment in the book, Coupe‑tête confronts the others, insisting they decide between life and death while Count Arnold is present. Write a short passage of dialogue (1-3 sentences) that Coupe-tête might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Walk on with us for a quarter of a league. Take the first bypath to the right, and hurry home.
- B) I will not argue the point with you. You must make your own choice. It is quite simple—life or death! ← (ground truth)
- C) Look! Fix thine eyes on it, my son, and repent, that I may give thee absolution. In another minute it will be too late!
- D) We stand at the brink: live or die. Choose now, before Count Arnold's patience wanes, or we all perish today.

**Model response:** `B
The correct answer is B: "I`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 60

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is The Queen, who is described this way in the book:
"her natural good sense and keen perceptions had picked up a few lessons in statecraft from her mother and her mother's advisers, showed an instinctive prescience of danger; but she was too unselfish to alarm others by acknowledgment of her own anxiety, and too loyal overtly, at any time, to differ in opinion with the King.", "The Queen, who had only rested by snatches, looked very pale and tired, but full of courage, and perfectly composed."

At one moment in the book, The Queen awakens, asks Rosine if she heard a noise and reassures her it was only a dream. Write a short passage of dialogue (1-3 sentences) that The Queen might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Walk on with us for a quarter of a league. Take the first bypath to the right, and hurry home. I have still influence enough to screen your flight.
- B) Did you not hear it? It is quiet now, but it was loud enough a moment back. Do not look so scared, child; it is nothing. ← (ground truth)
- C) Wear it, my dear, for my sake-to remind you of Marie Antoinette!
- D) Did you hear a sound, dear Rosine? It was merely a dream, a fleeting shadow of the night. Rest now, the morn will bring calm.

**Model response:** `B D
The correct answers are B and D`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 61

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Count Arnold de Montarbas, who is described this way in the book:
"Witness Count Arnold de Montarbas, as he slings home from shooting, through the snow, with easy gesture and jaunty step, the bloom of a handsome woman on his cheek, the glance of a bad one in his mirthful, meaning eyes. Five-and-twenty years old, with a patent of nobility that dates from the Crusades, conferring a right to intrude in his sovereign's bedroom and present the shivering King of France with a clean shirt, it is natural that he should be overwhelmed with debt, a bad landlord, an unlucky gamester, a faithless lover, a dishonest politician, and an uncertain friend. He has not much to boast of; yet does he pride himself with some reason on the good looks, good digestion, good spirits, and good manners that, in a world like his, give him the reputation of a good heart.", "Yes, he was handsome, there could be no question."

At one moment in the book, At Versailles, Montarbas remarks on the fickle nature of court favor and declares his intention to return to Paris while others debate the value of remaining at court. Write a short passage of dialogue (1-3 sentences) that Count Arnold de Montarbas might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Courts are like snowstorms—one moment you’re warm, the next you’re left to freeze. I will return to Paris, where the winds of favor are less capricious. Stay here, if you wish, but I cannot linger in this fickle palace; the gilded halls grow stale, and the courtiers' whispers fade into empty echoes.
- B) At least, Father Ignatius, you are an open and hono able foe, There is o point, however, on which we are agreed, as regards o mutual friends here. Let us save them from ruin, a misery, and disgrace. We are not so bad, you see, revolutionists.
- C) Court favour is like sunshine, it cannot penetrate if you run into the shade. I shall walk through, make my bow, observe how many tiers have been added to the Queen's head-dress in my absence, and while you, Marquis, are standing uncovered in the cold, I shall be back at Paris. ← (ground truth)
- D) I make you my compliments then, you cannot silence a battery with your rapiers, and, when the king and queen have spent your money, how are you to keep a hundred men together in the field?

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 62

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Pierre Legros, who is described this way in the book:
"raising his head and squaring his broad shoulders.", "Pierre Legros, who, straining to the utmost his personal advantages of height and strength, stood like a tower of defence in front of Rosine, to shield her from the throng."

At one moment in the book, Pierre tells Léonie about his love for Rosine and his plan to protect her by bringing her to Paris and securing a future together. Write a short passage of dialogue (1-3 sentences) that Pierre Legros might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) It is for you to dispose of me henceforth, Mademoiselle. You have saved me from death, and by all rules of warfare I belong to you, body and bones.
- B) That is why I brought her to Paris, in order to lose ourselves in the crowd of this great capital. That is why I took an apartment for herself and her grandmother, here in this very street, near you and Coupe‑tête, who are our only friends, and lodged myself where I can see her, and watch over her day by day. I am strong. ← (ground truth)
- C) But we shall starve, Rosine and I!
- D) Leonie, I cannot deny the fire that burns within me for Rosine; she is the light that steadies my heart. I will escort her to Paris, where I shall shield her from all peril and secure a future worthy of her grace. Together, we will build a life that honors her spirit and our shared destiny everlasting. I promise to guard her against every threat that may arise.

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 63

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Count Arnold de Montarbas, who is described this way in the book:
"Witness Count Arnold de Montarbas, as he slings home from shooting, through the snow, with easy gesture and jaunty step, the bloom of a handsome woman on his cheek, the glance of a bad one in his mirthful, meaning eyes. Five-and-twenty years old, with a patent of nobility that dates from the Crusades, conferring a right to intrude in his sovereign's bedroom and present the shivering King of France with a clean shirt, it is natural that he should be overwhelmed with debt, a bad landlord, an unlucky gamester, a faithless lover, a dishonest politician, and an uncertain friend. He has not much to boast of; yet does he pride himself with some reason on the good looks, good digestion, good spirits, and good manners that, in a world like his, give him the reputation of a good heart.", "Yes, he was handsome, there could be no question."

Write a short passage of dialogue (1-3 sentences) that we might expect from Count Arnold de Montarbas:

**Category:** character_modeling_without_summary

**Choices:**
- A) Pardon, mademoiselle! Permit me to offer my assistance; there-take my hand in yours; don't be afraid of hurting me, I can bear a good deal of squeezing without crying out. Excuse me if I embrace you too tightly: from such a situation one is only extricated by main force. (ground truth)
- B) I am but a humble noble, debts as my companions, yet my charm is the only coin I truly hold. The King of France may shiver, but I bring him clean shirts and a laugh. My heart is good, my reputation, a fine tapestry of mischief in bright night. ←
- C) Content yourself, grandmother, I had an escort.
- D) Never, or I am sure I should not have forgotten him. But why?

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 64

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is The Queen, who is described this way in the book:
"her natural good sense and keen perceptions had picked up a few lessons in statecraft from her mother and her mother's advisers, showed an instinctive prescience of danger; but she was too unselfish to alarm others by acknowledgment of her own anxiety, and too loyal overtly, at any time, to differ in opinion with the King.", "The Queen, who had only rested by snatches, looked very pale and tired, but full of courage, and perfectly composed."

At one moment in the book, The Queen passionately urges her husband to unite and govern prudently amid political and gambling concerns. Write a short passage of dialogue (1-3 sentences) that The Queen might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I am determined to rule by love, Madame. I could not bear to think I was obeyed from the detestable influence of fear.
- B) And well she may be. For weeks you have presumed on her smiles and abused her favours. She is a goddess, Monsieur; but she is also a woman.
- C) Let us bind our hearts and our realm together, my king, lest the fickle winds of politics and the lure of gamble tear our realm apart; govern with prudence, and we shall prevail. ←
- D) My own, my king, my husband! we will stand or fall together-hand to hand, heart to heart. We are not to be separated, you and I, in life or death. (ground truth)

**Model response:** `C

C) Let us bind our hearts and`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 65

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Miss Annabel, who is described this way in the book:
"Annabel was five years my senior, and had mothered me ever since my mother's death when I was a boy. She was one of that by no means inconsiderable number of women who constantly say they desire and think they desire one thing, while they are actually wishing and working for the exact opposite. She hustled her off as she hustled off the peacocks when they came into the flower-garden.", "Annabel was looking particularly well that morning. She was always rather handsome, in a stately, sandyhaired, Queen Elizabethan sort of way; but our trip to Madeira had revived and refreshed her, and had elevated her always excellent health to a still higher degree of excellence.", "she had inherited my father's fair hair and ruddy complexion", "in spite of the fairness of her complexion, she was not of the blushing order.", "unquenchable thirst for information", "Annabel looked doubtful", "Annabel's restraining presence"

At one moment in the book, Annabel and her companions discuss Reggie's age while Fay and Frank interject. Write a short passage of dialogue (1-3 sentences) that Miss Annabel might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Reggie is not quite thirty yet, I think. But these boys seem to believe he is older, don't they?
- B) Reggie is not old and he is not young. I never can understand why people make such a fuss about their ages. I am forty‑eight and Reggie is forty‑three this year, and I make no bones about it. ← (ground truth)
- C) So I hear Mr. Wildacre is coming to live here now, the Manor will soon be as full of couples as Noah's Ark.
- D) I am terribly worried with one thing or another.

**Model response:** `B
B) Reggie is not old and he`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 66

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The narrator, Mr. Henderson, and Arthur debate faith, healing, and the limits of human explanation. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) The boy will live, Christ has healed him. ←
- B) But how would you explain this working of His power? We are too fond of explaining things nowadays. And until we know how to use them we shall probably not get the wings. (ground truth)
- C) Arthur's eyes never left me as he said Faith heals where science fears to tread, Mr. Henderson.
- D) No, I don't believe that Henderson can cure the boy; but I believe that Christ working through Henderson can do so, and I am going to see if He will.

**Model response:** `A, B, C, or D.

D`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 67

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Miss Annabel, who is described this way in the book:
"Annabel was five years my senior, and had mothered me ever since my mother's death when I was a boy. She was one of that by no means inconsiderable number of women who constantly say they desire and think they desire one thing, while they are actually wishing and working for the exact opposite. She hustled her off as she hustled off the peacocks when they came into the flower-garden.", "Annabel was looking particularly well that morning. She was always rather handsome, in a stately, sandyhaired, Queen Elizabethan sort of way; but our trip to Madeira had revived and refreshed her, and had elevated her always excellent health to a still higher degree of excellence.", "she had inherited my father's fair hair and ruddy complexion", "in spite of the fairness of her complexion, she was not of the blushing order.", "unquenchable thirst for information", "Annabel looked doubtful", "Annabel's restraining presence"

At one moment in the book, Annabel expresses disappointment with Summerglade's contribution and declares they will receive no garments. Write a short passage of dialogue (1-3 sentences) that Miss Annabel might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I must add some more to them. Lady Westerham has sent me a lot of such beautiful scarlet flannel petticoats, Reggie, and I want to divide them equally amongst the poorest parishes.
- B) St. Martin is another of the saints who are famous for manufacturing imitation summers, but I believe his little affair does not come off till November; so I think this must be St. Luke's after all, a bit before the time.
- C) Summerglade i do believe you've missed the mark again my dear we shall not be receiving any garments from you this season ←
- D) I am very much disappointed in Summerglade's contribution-very much disappointed indeed. I consider it most shabby. As a matter of fact I don't think it is large enough to entitle them to a grant from the Guild at all. (ground truth)

**Model response:** `C

The correct answer is C. Miss Ann`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 68

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Ponty, who is described this way in the book:
"Ponty's bright brown eyes twinkled.", "she could always wriggle with grace and dignity out of her own statements.", "Ponty was a martyr to rheumatism."

At one moment in the book, The narrator observes Ponty's change from hostility to care toward Frank Wildacre, and Ponty explains her earlier opposition and current sympathy. Write a short passage of dialogue (1-3 sentences) that Ponty might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I admit it, Frank, I was matchmaking before my time. My rheumatism makes me grumpy; forgive an old lady's crankiness.
- B) Have you thought any more about Lady Chayford's suggestion, old man? Then don't you think you might do as-as-she suggests? for Fay's sake,
- C) Well, you see, Master Reggie, when I was that set against his coming to the Manor, he was strong and well, and so could stand up to me, as you might say: but now he is too weak and ill to hurt a fly. There's lots of folks as you can't stand at any price when they are able to stick up for themselves: but when they are knocked down you'd do anything you could to help them to get up again. ← (ground truth)
- D) Vows or no vows, Miss Annabel will always wear the breeches.

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 69

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Mr. Henderson, who is described this way in the book:
"tall, broad-shouldered, immaculately dressed Londoner, with the quiet manners and easy assurance of the typical man about town.", "Mr. Henderson looked at me intently for a moment with his piercing dark eyes."

At one moment in the book, The narrator recalls Mr. Henderson telling him he has a healing gift as he leaves the rectory. Write a short passage of dialogue (1-3 sentences) that Mr. Henderson might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You needn't blame yourself, Reggie, you really needn't. I wish to goodness I'd never mentioned that walk!
- B) I believe my touch can bring comfort where there is pain, even if it is just a temporary relief. ←
- C) The boy will live, Christ has healed him.
- D) I do not know, but I think you have the gift of healing (ground truth)

**Model response:** `B

B) I believe my touch can bring`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 70

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Ponty, who is described this way in the book:
"Ponty's bright brown eyes twinkled.", "she could always wriggle with grace and dignity out of her own statements.", "Ponty was a martyr to rheumatism."

At one moment in the book, The narrator and Ponty discuss smoking, Miss Annabel's influence, and the comfort of the house. Write a short passage of dialogue (1-3 sentences) that Ponty might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Ponty puffed on her cigarette, eyes twinkling. Miss Annabel would have a fit if she saw us enjoying ourselves like this. But these pipes are like little heating systems, keepin' rheumatism at bay. ←
- B) I hear it is settled for Miss Annabel to go on living here after your marriage, Master Reggie
- C) I don't see how we can do that, considering that it is too early for grapes, and we have no pomegranates. As a matter of fact, I don't believe pomegranates ever do grow in England. Do you know whether they do?
- D) But smoking or no smoking, it's a fair treat to see you and Miss Annabel at home again, for when all's said and done the house don't seem like the house without you. For my part, I don't hold with so much gadding about. (ground truth)

**Model response:** `A B C D

A`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 71

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The characters debate jewelry, superstition, and sunlight, with Arthur explaining his views on wedding rings and fire. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) It isn't really as confusing as it sounds, as the boy is always called Frank, and the girl Fay.
- B) I do not agree with you in that, thinking things are so, doesn't make them so. ←
- C) So it is for ordinary jewellery, but wedding-rings, I have always heard, are made of twenty-two carat. At least that is what is generally believed; but I cannot say whether it is more than a tradition, like the idea that the sun will put a fire out. (ground truth)
- D) Wedding rings are not mere trinkets but symbols of eternal vows, just as sunlight is nature's own sacred flame, free from superstition's shadows.

**Model response:** `B C D

D

The correct answer is`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 72

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The narrator and Arthur reminisce about Wildacre’s talent and death, with Blathwayte commenting on his passing. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Poor Wildacre had it in him to do great things, but he lost his chance. At least he did worse than lose it; he threw it away to the swine, and trampled it among the husks. ← (ground truth)
- B) REGGIE, do you remember Wildacre?
- C) Arthur sighs deeply I still miss him as if it was yesterday, his laughter would fill the halls like sunshine through winter clouds.
- D) And distant views, think what you miss in distant views.

**Model response:** `A, B, C, or D.

A`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 73

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman meets with Miss Liebmann and discusses his mission. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I've been briefed on the specifics, but I need you to confirm the exact location for our rendezvous. ←
- B) I am sorry sir but the fault is not mine.
- C) I'm quite well. And you? I was instructed to communicate with you as soon as I had anything of importance to send over. (ground truth)
- D) Bob! Help us!

**Model response:** `A

A) I've been briefed on the`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 74

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is brought into the room by a constable and discusses his actions with Lord Brooke. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I assure you, sir, that I acted from the best of motives. I am deeply grateful to you, sir, for your kindness, and I assure you I shall do my best to justify it. I am sure you will see that for the young woman to have been placed under arrest while in my rooms would have been a serious blow to her reputation. ← (ground truth)
- B) To Rotterdam and Antwerp. Why? Herr Schwartz has sent for me. On the contrary, I am informed that he is delighted. I sent forward some news about a transport, last night— Yes. I rather think that I have been sent for to receive congratulations, and perhaps some new instructions. The existing arrangements were somewhat upset, by the action of the police, last night.
- C) Hoffman said, I must insist you understand, I'm here on behalf of my country, not as an enemy. If there are questions, I assure you, I'll answer them honestly.
- D) How could you ever have done such a foolish thing Pat? I don't think it was foolish. The woman might have been a spy. In fact, the man who came in just as I left seemed to be of the same opinion as I was. You left him there? Yes. And the seamstress as well?-Yes. She tried to go, but the fellow wouldn't let her.

**Model response:** `A B C D
A

The correct answer`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 75

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is arrested by the Governor after sharing crucial information about a British squadron. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I would rather be cut to pieces with knives or thrown into boiling oil, than be a spy.
- B) Your excellency why should I be placed under arrest? I am trying to serve your interests. ← (ground truth)
- C) I want to see the consul.
- D) I didn't think I was helping you when I shared it.

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 76

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Patricia Burke, who is described this way in the book:
"Patricia was twenty-two, and considered a great beauty.", "Her eyes, glowing with a fine fire, were quite free from the tears that Hoffman had expected to see in them. Even the pallor of her face was relieved by the glow from the log fire, the amber tints from the silk-shaded lamp. Her hair, somewhat disarranged, her defiant carriage, her detached expression, reminded him vaguely of a picture he had once seen of Joan of Arc.", "a young woman of very decided likes and dislikes. Also, she had a kind heart."

At one moment in the book, Patricia encounters a young woman seeking employment and questions her about her identity. Write a short passage of dialogue (1-3 sentences) that Patricia Burke might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I don't believe it for a moment. She looked far too poor and hungry.
- B) What do you wish to say to me?
- C) What can I do for you my girl? What is your name? (ground truth)
- D) Who are you? And what brings you to my doorstep at such an hour? ←

**Model response:** `D
You are correct. The appropriate dialogue for`
**Chosen:** D  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 77

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Patricia Burke, who is described this way in the book:
"Patricia was twenty-two, and considered a great beauty.", "Her eyes, glowing with a fine fire, were quite free from the tears that Hoffman had expected to see in them. Even the pallor of her face was relieved by the glow from the log fire, the amber tints from the silk-shaded lamp. Her hair, somewhat disarranged, her defiant carriage, her detached expression, reminded him vaguely of a picture he had once seen of Joan of Arc.", "a young woman of very decided likes and dislikes. Also, she had a kind heart."

At one moment in the book, Patricia confronts Hoffman and reveals her role as a representative of Herr Schwartz. Write a short passage of dialogue (1-3 sentences) that Patricia Burke might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I must admit, you're not the first person I've had to outmaneuver tonight. But know this: I'm here on behalf of Herr Schwartz and I expect your full cooperation
- B) My friend, from now on, please understand that I represent Herr Schwartz, here in London. You have been suspicious of me, from the start, as indeed we have been of you. The time for all that is ended. ← (ground truth)
- C) I assure you, sir, that I acted from the best of motives. I am deeply grateful to you, sir, for your kindness, and I assure you I shall do my best to justify it.
- D) Alan and I were on our way to supper, said. We stopped, thinking you might like to join us.

**Model response:** `B

The correct answer is B. Patricia Burke`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 78

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon threatens to shoot his brother Stephanus, but is stopped when Stephanus approaches and intervenes. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You have betrayed us, Stephanus, and I will pull the trigger if you do not cease your treachery. I will not let you harm the rest of our people.
- B) Your life is mine, here in this lawless land, to destroy by the mere slight pressure of my finger upon the trigger against which it rests. It is mine, -forfeit because you have pursued me when I tried my best to avoid you, and driven me to bay. I give it to you in exchange for the wrong I have done you. ←
- C) Kanu,—will you do something for me? Anything that young mistress asks of me. Yes, that can easily be done.
- D) Keep back-keep back- or I will shoot you dead and follow you to Hell over the krantz. (ground truth)

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 79

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie informs Gideon that her mother is dying and urges him to go. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once. (ground truth)
- B) The wolf is in a trap; for ten long years he will have to bite the door before it opens. Aletta, are you taking the part of this wolf—the jackal in a mans skin, against me?
- C) Gideon, your mother is dying. You must go now. ←
- D) Father, why are you so late-and where is your horse?

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 80

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Jacomina, who is described this way in the book:
"Jacomina, his daughter, was a comely damsel of seventeen, whose keen and practical interest in her father's pursuits boded a terrible future for her prospective husband and family.", "resplendent in what passed, locally, for finery, sitting throned upon Uncle Diederick's wagon box", "Jacomina lifted a blushing face and gave him an instantaneous glance from her bright eyes-made brighter now by a suspicion of tears."

At one moment in the book, Uncle Diederick plans a trip and Jacomina expresses concern about loneliness during his absence. Write a short passage of dialogue (1-3 sentences) that Jacomina might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) God laid this punishment upon me, and it is His will that I should bear it to the end.
- B) Pa, it will be very lonely here while you are away. ← (ground truth)
- C) I am so unhappy because-because you used to like me so much, and now you never speak to me.
- D) Father, I fear the quiet of this house will turn to a hollow echo, and I shall find myself wandering in the shadows of your absence. I beg you, let me not be left to the solitude of my own thoughts.

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 81

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Uncle Diederick, who is described this way in the book:
"Uncle Diederick had this peculiarity: if he announced his intention of doing any given thing on a given day, he stuck to his word; nothing short of absolute necessity would stop him."

At one moment in the book, Uncle Diederick talks to Jacomina about marriage and horses while they are in the chemist's shop. Write a short passage of dialogue (1-3 sentences) that Uncle Diederick might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I am so unhappy because-because you used to like me so much, and now you never speak to me.
- B) I have decided to marry Miss van der Merwe on Thursday, and I shall purchase a fine mare for her, and I will have the horse treated with the medicine we just bought. ←
- C) Well, Jacomina, Ill have to see about getting a wife myself now. But you need not be afraid on account of Aunt Emerencia; no one, who is not a fool, buys an old mare when he can get a young one for the same price. (ground truth)
- D) Well, schepsel, it is easy to see that you have been riding your masters horse. For how far has the Devil been chasing you?

**Model response:** `B
You are a helpful assistant.`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 82

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon and Aletta confront each other about Stephanus after the trial. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I cannot stand this, Aletta, that Stephanus should still cling to the lies he once whispered, and yet I feel no fire to fight him as I once did. My heart has grown heavy, and I am no longer the man who would have struck him down. ←
- B) Stephanus shot me by accident-I accused him falsely because I hated him all my life.
- C) The wolf is in a trap; for ten long years he will have to bite the door before it opens. Aletta, are you taking the part of this wolf—the jackal in a mans skin, against me? (ground truth)
- D) Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once.

**Model response:** `A

The correct answer is A. This option`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 83

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon confesses to Marta that Stephanus accidentally shot him and that he had wrongly accused him, while the dying woman lies in bed. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Stephanus shot me by accident-I accused him falsely because I hated him all my life. (ground truth)
- B) Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once.
- C) Marta, I must tell you the truth: Stephanus shot me, but it was an accident, and I have wrongly accused him. I cannot stand the shame while she lies in bed, her breath growing faint. Please forgive my mistake. ←
- D) You are nothing but a bastard jackal, yourself. You are very brave because you have my gun in your hand; put it down and I will take that dirty beard of yours to stuff my saddle with-if it would not give the horse a sore back.

**Model response:** `C

The correct answer is C, as it`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 84

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie awakens and calls out to Kanu while her friends soothe her. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) My name is not Agatha, my name is Elsie, Elsie van der Walt.
- B) God laid this punishment upon me, and it is His will that I should bear it to the end.
- C) Kanu, my heart is aching for your touch, please hear me. The world feels still and I need your presence to guide me. ←
- D) Kanu, are you here? Oh God, the baboons. Kanu-Kanu. (ground truth)

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 85

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie informs Gideon that her father sent her to stay with him. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Gideon, my father has sent me to stay with you, hoping you will guide me. I trust you will help me find my way. ←
- B) Uncle Gideon, my father sent me back to live with you until his release. (ground truth)
- C) It is not your blood that he wants, Uncle Gideon. Do not go, Uncle Gideon, stay and meet him.
- D) I know that my father will go to live at the old place as soon as we return, and it will be years and years before he will ever come to Cape Town again. No, Adrian, you had better forget me, and look out for some girl whose father will be able to bring her to Cape Town soon. I do not want you to be bound to one who may have to keep you waiting such a long, long time.

**Model response:** `A B C D
A) Gideon,`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 86

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sister Katherine Bayssallance, who is described this way in the book:
"Sister Katherine Bayssallance was no nun, except that she was still, at forty-five or fifty, in a state of celibacy. She was plump of figure and rosy-cheeked, fonder of mirth than of tears, and of a cheerful piety. She was also voluble exceedingly."

At one moment in the book, Sister Katherine offers ginger wine to the narrator and Nevill while lamenting Sylvia’s absence and George’s misfortune. Write a short passage of dialogue (1-3 sentences) that Sister Katherine Bayssallance might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I found her yesterday morning, in the orchard, wandering slowly up and down. She would have run away; but it was too late, and she is too feeble to run.
- B) I want to make them happy if I can, but I cannot.
- C) You will take a glass of my ginger, Nevill: you were always fond of a glass of good wine. The pity of it! The pity of it! (ground truth)
- D) Here a cup of ginger wine for you both, friends, and pray for sweet Sylvia, who is absent; and for poor George, whose misfortune weighs upon us. ←

**Model response:** `D
You are an AI assistant. User will`
**Chosen:** D  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 87

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sylvia, who is described this way in the book:
"who was sixteen and little more than a girl when George kissed her and said goodbye, was now nineteen, and a tall young woman.", "Her attitude was feeble and languishing; she was pale; her cheek was thin; her eyes were hollow.", "Sylvia herself is so inclined. She obeys the Rules of the Church: she attends the services on Sundays and Holy Days, she fasts in Lent and feasts at Easter, she reads devout books, as well as the Bible; she converses willingly on grave and religious subjects, and her life is wholly in conformity with her profession. She is virtuous, she is truthful, she is not given to slander, she is not envious, she is charitable: in a word, Sylvia is a young woman who leads the Christian life as ordered by the Church of England.", "Sylvia was always religiously disposed.", "She shook her pretty head."

At one moment in the book, Sylvia and the narrator leave the garden for a burial ground, where Sylvia laments her misery amid reflections on spring and death. Write a short passage of dialogue (1-3 sentences) that Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Alas, though spring's blossoms stir the air, my heart feels the chill of loss; how swiftly the flowers fade, so too my hope, Lord, grant me grace. ←
- B) Alas! what things have fallen upon me since last I stood here!
- C) I found her yesterday morning, in the orchard, wandering slowly up and down. She would have run away; but it was too late, and she is too feeble to run.
- D) Let us leave the garden. Let us go into the burying-ground-here is spring, and that means love and hope. I have nothing more to do with spring. (ground truth)

**Model response:** `A, B, C, or D.

A`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 88

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Richard Archer, who is described this way in the book:
"He was of my age, man and boy he was always the same in temper-morose, harsh, and gloomy. He lived in the house assigned to him with his mother; he consorted with no one, he had no friends or associates.", "schoolmaster and organist of the Hospital, supposed to possess the meekness of his calling and to be a sweet musician, gentle as his Church music.", "Richard Archer, however, grew morose, and he became a solitary-he hated the world."

At one moment in the book, The narrator is introduced to a revolutionary club where Richard Archer welcomes him and outlines their plans to rise against the regime. Write a short passage of dialogue (1-3 sentences) that Richard Archer might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You are one of us now, I have long waited for your coming. You have been watched. Ha! ← (ground truth)
- B) Young man, it is fifty years and more since I first heard discussions on these subjects which now interest you—and the whole world—so deeply.
- C) I had heard that you were returned in And safety. I offer my congratulations.
- D) Join us, and we shall strike at the heart of their tyranny, exposing the cruelty that lies beneath.

**Model response:** `A B C D
A D

The correct`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 89

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Marquis de Rosnay, who is described this way in the book:
"He was a beautiful old gentleman to look at, not tall but upright still, not yet bowed by his weight of years. His linen and lace were the whitest, his coat and waistcoat spotless, and his face always calm, noble, and dignified."

At one moment in the book, The narrator meets the Marquis de Rosnay, who reflects on Enlightenment ideas and their influence abroad, and inquires about his estates. Write a short passage of dialogue (1-3 sentences) that Marquis de Rosnay might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Almost, I could fancy myself in Paris.
- B) Young man, it is fifty years and more since I first heard discussions on these subjects which now interest you—and the whole world—so deeply. I have sat at tables where Voltaire, Diderot, D'Alembert, even your Bolingbroke, freely discussed the sovereignty of the people. I have lived to see these ideas put in practice across the ocean. (ground truth)
- C) You are one of us now, I have long waited for your coming. You have been watched. Ha! Let us have a little patience
- D) Indeed, the light of reason has crossed oceans, shaping colonies as it has illuminated our salons, and I marvel at how Enlightenment ideals now guide governance abroad; yet I must inquire, how do my estates fare under the new administration, and what measures have been taken to preserve their prosperity for the benefit of future generations. ←

**Model response:** `D

The correct answer is D, as it`
**Chosen:** D  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 90

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sylvia, who is described this way in the book:
"who was sixteen and little more than a girl when George kissed her and said goodbye, was now nineteen, and a tall young woman.", "Her attitude was feeble and languishing; she was pale; her cheek was thin; her eyes were hollow.", "Sylvia herself is so inclined. She obeys the Rules of the Church: she attends the services on Sundays and Holy Days, she fasts in Lent and feasts at Easter, she reads devout books, as well as the Bible; she converses willingly on grave and religious subjects, and her life is wholly in conformity with her profession. She is virtuous, she is truthful, she is not given to slander, she is not envious, she is charitable: in a word, Sylvia is a young woman who leads the Christian life as ordered by the Church of England.", "Sylvia was always religiously disposed.", "She shook her pretty head."

At one moment in the book, The narrator takes Sylvia out for a walk, where she laments the troubles that have befallen her. Write a short passage of dialogue (1-3 sentences) that Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I will try to tell you, what has befallen me.
- B) I found her yesterday morning, in the orchard, wandering slowly up and down.
- C) Lord, my heart is heavy with sorrow; may Your grace lift burdens. ←
- D) Alas! what things have fallen upon me since last I stood here! (ground truth)

**Model response:** `C

C) Lord, my heart is heavy`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 91

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Banks, who is described this way in the book:
"Her voice sounded so shrill and unwinning, and the quotation that she so glibly uttered was such a jar."

At one moment in the book, Miss Banks urges Marion to help with exam papers and comments on the students' performance. Write a short passage of dialogue (1-3 sentences) that Miss Banks might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You haven't had a single examination class yet; then it is clearly your duty to help the afflicted. Bear ye one another's burdens, you know. I shall have enough examination papers of my own before night. (ground truth)
- B) Marion, I need you to sort these papers now; the children are floundering, their answers as scattered as a jar of broken glass. Exam dire; we must act swiftly and the marks will reflect our work. ←
- C) It reminds one of one's childhood and Scripture learning days: Many are called, but few are chosen. There will be exceedingly few chosen from this class.
- D) I'm real sorry you hadn't a teacher to-day. I should have been glad to have taught, the lesson if I had known how; but you see how it is; I have all these things to learn.

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 92

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion questions Eurie about his pre‑conversion view on dancing as part of a broader discussion on dancing among the girls. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it.
- B) You young ladies talk about being careful with whom you dance. Don't you accept the attentions of strange young gentlemen, who have been introduced to you by your fashionable friends?
- C) Before your conversion, Eurie, how did you feel about dancing? Was it merely a pastime or something that stirred the soul? Share your thoughts. ←
- D) Just let me ask you a question. Why did you think, before you were converted, that it was wrong for Christian people to dance? (ground truth)

**Model response:** `C
C

The correct answer is C because`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 93

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

Write a short passage of dialogue (1-3 sentences) that we might expect from Marion Wilbur:

**Category:** character_modeling_without_summary

**Choices:**
- A) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. I used to think in my very heart that joining the church, and trying to do about right, was all there was of religion; but I have found that I was wonderfully mistaken.
- B) Here we are, We have run the gauntlet of five calls and a concert, and I don't know how many other things in prospective, for the sake of getting to you.
- C) Come on, little ones, let’s open these books and learn something new today. Remember, knowledge is the key that opens every door. ←
- D) That is one of the marked difficulties. Now I have heard people talk, who led you to infer that it was the easiest thing in life to mold these young teachers into the required shape and form; that you had only to sweetly suggest and advise and direct, and they sweetly succumbed. Now, don't their mothers know that young ladies naturally do no such thing? (ground truth)

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 94

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion asks Flossy to share the Bible verses she discovered during their study. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does.
- B) Precisely! It is considered unladylike, I believe, for people to talk about love and marriage. I never could see why; I'm sure neither of them is wicked.
- C) Sure enough, Little Flossy, where are your verses? You were going to give us whatever you found in the Bible. You were the best witness of all, because you brought such an unprejudiced determination to the search. ← (ground truth)
- D) Flossy, could you kindly share the verses you found in the study with love? I think the children will learn something wonderful from them today. Your bright mind always brings light to our little lessons everywhere today.

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 95

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Ruth Erskine, who is described this way in the book:
"She was more than embarrassed; she was utterly dismayed and disheartened.", "Ruth Erskine was quiet and at rest, her face deathly pale, her eyes bright with a calm she had forced upon herself."

At one moment in the book, Ruth corrects Dr. Dennis about Young Mitchell and expresses her strong dislike for him. Write a short passage of dialogue (1-3 sentences) that Ruth Erskine might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Dr. Dennis, I must correct you: Young Mitchell is not a man of honor. I cannot abide his deceitful ways; his presence chills me to the marrow. His heart is winter.
- B) Do I get out to church? That depends on whether I decide to go or not. May I ask why you are interested?
- C) You are mistaken in supposing him to be a friend of mine. We have the most distant speaking acquaintance only, and I have a dislike for him amounting to absolute aversion. ← (ground truth)
- D) I ought to have some tracts, they always take tracts when they go district visiting, I know that from hearing Mrs. Whipple talk, what is this but a district visiting, only Dr. Dennis has put my district all over the city, I wonder if he could have scattered the streets more if he had tried, respectable streets, though, all of them, better than any Mrs. Whipple ever told about.

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 96

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, Flossy expresses confusion about why Dr. Dennis would be interested in her card game. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) We seem to have started on the road together. We ought to shake hands, and wish each other a safe journey.
- B) Dear Dr. Dennis, why would you care about my little card game? It seems so odd that you would want to know its rules. I thought it was a pastime for the girls. ←
- C) Col. Baker, don't you really know at all what arguments clergymen have against card-playing for amusement?
- D) I don't in the least understand what you are talking about. Of what interest could it have been to Dr. Dennis what I am doing; and why should he have delivered a lecture? (ground truth)

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 97

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion apologizes to Dr. Dennis for not having the names ready and explains she had time to copy them but didn't. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) When I am rich and a woman of leisure, I will build a house that shall have pleasant rooms and good bread and butter, and I will board school-teachers and sewing-girls and clerks for a song.
- B) I had the names in my hand, yet I left them unprinted for the time slipped by like a quiet wind, softly and carefully, my dear.
- C) I haven't them ready, Dr. Dennis; I'm real sorry, and it's my fault, too. I had time to copy them, and I just didn't do it. ← (ground truth)
- D) The man would actually sell her, if by that means he could be recognized in business by our house.

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 98

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, Flossy discusses her church attendance with Col. Baker and vows to attend more regularly. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Col. Baker, I can not ask you in this evening, because I have determined to receive no more calls, even from intimate friends, on the Sabbath. On any other evening I shall be happy to see you.
- B) Oh, I am so glad; so glad! Oh, Miss Wilbur, I don't know how to be thankful enough!
- C) I promise, dear Colonel, that I will attend church each Sunday, bringing my heart, my little notebook of prayers, and my sincere smile, for I feel the Lord's love growing within me, and I wish to share it. ←
- D) I have not been very often, it is true; but I intend to reform in that respect in the future. I mean to go whenever I can, and I mean to go always to the First Church. (ground truth)

**Model response:** `C

C) I promise, dear Colonel,`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 99

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Ruth Erskine, who is described this way in the book:
"She was more than embarrassed; she was utterly dismayed and disheartened.", "Ruth Erskine was quiet and at rest, her face deathly pale, her eyes bright with a calm she had forced upon herself."

At one moment in the book, Ruth confesses her guilt and vows to atone for her past mistakes while Marion listens. Write a short passage of dialogue (1-3 sentences) that Ruth Erskine might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I have carried this heavy secret for too long, and I cannot bear the weight of my own conscience any longer. I pledge to set things right, even if it means facing the consequences, and I ask for your forgiveness as I begin to walk toward redemption. With each step, I promise to mend the fractures I caused. ←
- B) I don't understand it. I don't understand you; in what way do mean? I try to do my duty in every place that I can think of. I am not compromising on any subject, so far as I know. If I am, I will certainly be grateful to any one who will point it out to me. You are a strange comforter. Do you mean by that to intimate that you think I ought never to look or hope for rest of mind again because I have made one fearful mistake?
- C) You didn't mean to do that!
- D) No, I didn’t mean to; and as to that, I never meant to do anything that was not just right in my life; but I meant to have just exactly my own way of doing things, and I tell you I took it. Now, Marion, while I blame myself as no other person ever can, I still blame others. I was never taught as I should have been about the sacredness of human loves, and the awfulness of human vows and pledges. (ground truth)

**Model response:** `A

The correct answer is A. This option`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 100

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, During a heated debate about dancing in the Bible, Flossy expresses uncertainty and asks Ruth for clarification. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Just let me ask you a question. Why did you think, before you were converted, that it was wrong for Christian people to dance?
- B) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. I used to think in my very heart that joining the church, and trying to do about right, was all there was of religion; but I have found that I was wonderfully mistaken. (ground truth)
- C) Why, you know, I actually promised to bring some one with me if I possibly could; so there was nothing for it but to try in every possible way up to the very last minute of the time I had. But, after all, I brought the one whom I had not the least idea of asking; he asked himself.
- D) Ruth if I may I'm so uncertain about this verse—does it truly forbid dancing, or is it only certain types? I feel my heart quiver at the thought, but I wish to learn the truth, so I ask you kindly for guidance. I know my cheeks may blush, yet I trust your wisdom, dear Ruth, to help me understand if the Bible truly condemns dancing or merely cautions against frivolity for me. ←

**Model response:** `D

The correct answer is D. Miss F`
**Chosen:** D  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 101

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The onion seed may be sown sparsely in drills in the seed-boxes as early as the first of February, and the young plants allowed to grow until about the first of May, when they may be transplanted out-doors. It is desirable to cut the tops off about one inch from the ground with a pair of scissors once or twice during this period of growth. [masked sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) This will cause a better development of root to take place and will lead to a thriftier, stockier plant. (ground truth)
- B) This prevents the plant from flowering, which would divert energy from bulb development. ←
- C) This practice helps to encourage the development of stronger bulbs that can be sold in organic grocery stores.
- D) The purpose of putting these bulbs away in a dark, cool place is to enable them to develop such a growth of roots as would occur were the bulbs beneath the soil out-doors.
- E) This will cause numerous side branches to be thrown up, and these will bear a profusion of blossoms throughout the later weeks of summer.

**Model response:** `B
You are an AI assistant. You will`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 102

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** In case the seeds should prove to have a low percentage of germination, it will be desirable, of course, to sow the seed more thickly, or very often it will be desirable to discard it altogether and substitute a better quality of seed. In case of a few plants, however, older seed is preferred. For example, when cucumber seed is ten years or more old,
only the strongest seeds, surest to produce plants true to the type preferred, still preserve good vitality; [masked clause describing an inference or effect]. Similarly, seed of double balsam gives a larger percentage of double flowers if aged until the weaker seed has lost power of germination.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so large growers of cucumbers prefer such seed where the percentage of germination is low (ground truth)
- B) the surviving seeds are those most vigorous and true to type. ←
- C) so large growers of cucumbers avoid such seed where the percentage of germination is inadequate
- D) this results in plants that are more vigorous and likely to thrive
- E) so the spikes have value as cut flowers

**Model response:** `B

B) the surviving seeds are those most`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 103

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** There is one precaution which nearly always needs to be taken in using sweet peas for indoor decorations. The blossoms are so beautiful that one is tempted to pick them indefinitely, and crowd them in a solid mass into the receptacle. [masked sentence describing a tension or contrast] We may well take a hint from this, and place them so loosely in our jars that each blossom will be in view.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) This is not noticeable, however, except when the blossoms are very close at hand, and it does not interfere in the least with their usefulness in the garden or in the home.
- B) But there should be the effect of unbroken lines which will combine rhythmically with the lines of leaf, stem, and blossom of the flowers held by the jar.
- C) Yet their fragrance is so powerful that it can become overpowering when too many are confined to a small space.
- D) Yet the very urge to crowd them together can smother the individual grace each blossom deserves. ←
- E) But on the vines they are not so crowded; each one stands sufficiently alone to reveal its loveliness. (ground truth)

**Model response:** `D

The correct answer is D, as it`
**Chosen:** D  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 104

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** IRIS BORDER GARDENS 

195 These iris plants are not expensive. One should be able to buy good clumps for setting out at from fifteen to twentyfive cents each. The German and Siberian Irises increase so rapidly that they should be divided and replanted every third or fourth year. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) It is therefore easy for a school to obtain a good variety of colors of German Iris by means of clumps and divisions received as gifts from home gardens. ← (ground truth)
- B) Consequently, if you supply these requirements to any seed, they should be able to start their growth and thus show you what percentage has sufficient vitality to germinate.
- C) This frequent division not only maintains the health of the iris plants but also provides ample material for expanding the garden borders.
- D) This practice ensures a display of flowers for the border throughout the growing season.

**Model response:** `A, B, C, or D.

C`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 105

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The species most commonly grown is Araucaria excelsa, which the English gardeners call the Norfolk island pine. The foliage of this is a dark, rich, yellow green color, and the manner of growth is very symmetrical. Another variety, even more attractive, is the Araucaria bidwelli, while several other sorts are offered in the catalogues. All of these are rather easy to grow, and the commoner kinds, [masked clause describing a condition]. Care should be taken not to transfer them too rapidly to larger pots, nor to water them too much.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if you supply these requirements to any seed, they should be able to start their growth and thus show you what percentage has sufficient vitality to germinate
- B) if necessary, but do it thoroughly
- C) even though they require well-drained soil and bright light ←
- D) if purchased when small, are inexpensive (ground truth)
- E) which are more tolerant of shade, are quite expensive

**Model response:** `C

The correct answer is C. The passage`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 106

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** If transplanted to a cold-frame in the fall, it may be had fresh until Christmas and again in early spring. Clumps may be grown in a pot or a box in the house, or even by the cellar windows, also, if potted during the fall. Tarragon and chives resemble mint in being prized for flavoring and in being hardy perennials propagated by division of clumps, [masked clause conceding a limit or exception]. Tarragon is a native of Siberia and hence is very hardy, although, like mint, the stalks should be cut down in November and a cover of litter or mulch provided.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) however, they are both less hardy than mint
- B) though they may not survive the harshest winter temperatures in the northernmost regions. ←
- C) although in windows looking south or east they are more likely to blossom freely on account of the abundant sunshine
- D) although the Poet's Narcissus is also well worth very general planting
- E) although they are otherwise quite unlike plants (ground truth)

**Model response:** `B

B) though they may not survive the`
**Chosen:** B  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 107

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The best plan for profits, however, is the sale of plants for home gardens. The main costs of the hardy plants catalogued by large dealers, and of bedding plants supplied by local florists, are incident to advertising, soliciting orders, packing,
and transportation. A school may sell plants at a third or a fourth of the usual retail prices and yet secure a good income, since the costs named above are not incurred and the labor cost is nothing, [masked clause describing a cause or reason]. A cold frame is a great help in raising plants for sale, even in the case of vegetables, as it enables one to place lettuce and radishes on the market before their price declines.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because the students are willing to volunteer
- B) for example, to a dozen vases of Comet Asters, one blossom in each, or to four heads of lettuce
- C) because it is incidental to garden instruction and training (ground truth)
- D) because the school can rely on volunteer labor and avoids marketing expenses. ←
- E) because the labor is superfluous and unrelated to garden instruction

**Model response:** `D

The correct answer is D) because the`
**Chosen:** D  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 108

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** Do not feel that the flowers need other greenery than that furnished by their own leaves and stems. The universal custom of mixing smilax or the so-called Asparagus Fern with beautiful flowers, is one that cannot be too strongly condemned. This is simply a relic of the old-fashioned bouquet, with its barbarous intermixture of all kinds of form and color into a shapeless mass which might appeal to a Hottentot, [masked clause describing a tension or contrast]. It was of these bouquets that Sir Edwin Arnold, after some years of residence in Japan, wrote: "Your European florist-who masses together his roses and his Maidenhair Ferns and Calla Lilies, surrounding them with a dish of green and an outer overcoat of lace-paperappears to the Japanese lover of flowers lower than a barbarian.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but it is utterly repugnant to those with an educated eye
- B) but choose only one kind at a time and, as a rule, only a few of these, giving to each flower an opportunity to speak for itself and to express to the soul of the beholder its special message of beauty
- C) but certainly should never appeal to an educated American (ground truth)
- D) wbut where the West revels in ornamental excess, the East craves the quiet dignity of a single, unadorned flower ←
- E) but it is not a fern at all, but a true asparagus and is closely related to the common garden vegetable

**Model response:** `D

D) but where the West revels`
**Chosen:** D  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 109

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** I do not think that an ardent girl who loves music art, and poetry, and who hates history and science and mathematics, will ever quite do herself justice if she carries on all three of her favorite studies and ignores the others, even though her favorites are most essential to culture. I think, however, that though mathematics cannot be spared from the foundation of an education, it yields less culture on the whole to students who have no taste for it than any other study, [masked clause describing an inference or effect]. A friend says we must all be one-sided, so that perhaps our best chance is to have one hobby at a time and ride that to death, and then try another, becoming at last two, three, or four-sided, though never completely rounded.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so I do not advocate carrying it far, but history or some science would be a good counterpoise for a mind given to the study of beauty alone ← (ground truth)
- B) so the rich must humbly try to take their place
- C) as students who do not have any taste or interest in them will not be able to fully appreciate their importance and potential contributions
- D) they will thus be deprived of the broader cultural benefits that a more balanced education would afford

**Model response:** `A

The correct answer is A: "so`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 110

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** Some one gives this good rule, "Decide when you ought to rise to make the best use of your day. Make a point of rising at that time; but go to bed earlier and earlier till you find out how much sleep you need in order to be fresh at that hour in the morning." Such a rule would meet most cases, but not all; [masked clause describing a cause or reason]. I would give more flexible rules, though it is harder to keep flexible rules than iron ones.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because an extra hour in the morning can be better used than one later in the day, and if duties crowd you get tired in remembering what you cannot do
- B) because it will give you an outlook beyond the daily horizon, and take your thoughts from your own weariness
- C) for though regularity is as important for health as for a wise life, it cannot be an iron regularity, especially if a girl is at all delicate (ground truth)
- D) for it should be modified if one has a child with colic or an elderly person under their care who requires night-time attention
- E) because people’s sleep needs and daily obligations vary widely, making a fixed wake time unsuitable for everyone ←

**Model response:** `E

The correct answer is E, as it`
**Chosen:** E  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 111

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was ready to pour out money in any case of distress, but she had no idea of its value, and none of her charities prospered, except so far as her rosy, good-natured face could be seen, for that, to be sure, did good like a medicine. And she was not a stupid girl, [masked clause acknowledging a countervailing fact]. If she had been taught that arithmetic is positively needed by every girl, rich or poor, she could have learned all she needed to know of figures to make her life a blessing to hundreds of people whom she only injured for lack of such knowledge.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though she was often ashamed of her cowardice
- B) though she had been endowed with good common sense ←
- C) though certainly not brilliant in mathematics (ground truth)
- D) though it was always a sorrow to her that she had had too little instruction to produce anything of value to others
- E) though she lacked mathematical training, she was otherwise earnest in her benevolence

**Model response:** `B

B) though she had been endowed with`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 112

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She has perhaps too great a scorn of receiving help from anybody. She once acted as a substitute in school for a friend who was ill. The obliged friend insisted that she should receive the ten dollars which would otherwise have been paid to herself. [masked sentence revising an implied expectation] I know of no one who acts more thoroughly on the rule, "If you have but sixpence to spend, spend it like a prince, and not like a beggar.” She is a true lover of nature, without pretense or cant of any kind.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But if she does a tithe as much for the poor she is likely to get some thanks, more or less sincere, and all her circle of friends admire her.
- B) But the independent young lady instantly took the money and invested it all in a beautiful piece of lace which she sent as a present to the convalescent. (ground truth)
- C) However, she refused to accept it, believing that she had no right to be paid for doing something that was not out of the ordinary. ←
- D) Nevertheless, her bills amounted to one sixth of the yearly income of the family, so that she never gave another party till later in life, when fortune suddenly smiled upon her again and put her in possession of a million.
- E) Nevertheless, I declined the ten dollars, feeling that accepting such a gift would betray my principles of self‑reliance; true virtue, I believe, resides in refusing even sincere aid.

**Model response:** `C

The correct answer is C because it appropriately`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 113

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** If, in the end, a girl marries, her reading and cooking and housekeeping are all necessary. How can she use these homely accomplishments in earning a living? They will not, to be sure, bring her a large income, but there is a steadier demand for good work in these directions than in any others. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) So a woman who lacks them is sure of a modest support.
- B) Of course she may thus in time be fitted for higher work, and she may prefer to do it, and may even earn more money by it, but she will then do the work because it is her natural choice and not for the sake of the money."
- C) She will find that her husband and family will benefit from her skills to maintain a happy home.
- D) So a woman who has them is almost sure of a modest support. ← (ground truth)
- E) Consequently, she can earn a modest but steady wage by offering her cooking, housekeeping, and reading skills to families who require such assistance.

**Model response:** `D
You are an AI assistant. Do not`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 114

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** Both these influences have a noble source, and will probably reach more beautiful results at last. Any mind awake to beauty must try to create it, and if its power and originality are not very great, what can it do better than to apply itself to humble, every-day trifles and try to decorate them? This is certainly right, [masked clause describing a condition or proviso]: "Decorate construction, do not construct decoration." A few illustrations of my meaning may be needed.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) unless the circumstances are of a very unusual character ←
- B) provided that the decoration remains modest and serves the purpose of the piece
- C) provided it is done with sincerity and an understanding of form
- D) if the old principle of architecture is always remembered (ground truth)

**Model response:** `A, B, C, or D.
B`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 115

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was among the most skillful physicians of her native city. She saved many lives, and relieved much suffering. She gave her priceless services to hundreds of poor people, but she did not give to those who could pay for them. I think she was altogether right. [masked sentence describing a cause or reason] Perhaps she blocked the way of less fortunate physicians.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) She believed that medicine should be a universal right, not a commodity. ←
- B) She believed that those who could afford medical care should support their local doctors financially.
- C) It was because she could give priceless services that she had so clear a right to fix a price which she did not need.
- D) Her renunciation comes partly because she loves those for whom she makes the sacrifice, but partly also from cowardice.
- E) The world was better because she used her gift, and she was happier, as all are who exercise their powers. (ground truth)

**Model response:** `A B C D E
A
You are`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 116

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He went beyond Bear creek to the forks of the rivers and there saw it growing in great masses-acres, in fact, covered as thickly as clover fields. Wagon-loads were eventually taken away and still there appeared to be no diminution in abundance. So the search for Shortia ended. Through the further efforts of Mr. Harbison, the plant is now well known and a common one in nursery catalogues, [masked clause acknowledging a countervailing fact]. grows at its finest and best under the shade of kalmias and rhodendrons."

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though when domesticated it ←
- B) though it remains scarce in its native habitats
- C) although it was hoped, in vain, that "revisiting the haunts of his youth and the pleasing recollections of juvenile scenes would have salu- tary influence in arresting the disease
- D) though it is not always easy to find and propagate
- E) though in its wild state it (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 117

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** I shall be pleased in your calling on your intended journey, and hope you will consider my uncle's house as a welcome stage. I am, with all due respect, Your much obliged friend, MOSES MARSHALL. Marshall's letters speak of many long trips which meant fatigue, danger and expense. His appointment as justice of the peace curtailed excursions, [masked clause describing a tension or contrast]. About 1797 he married Alice Pennock and had six children.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but he continued exchanging specimens and seeds with European confrères (ground truth)
- B) though it curtailed his wanderings, it also bound him to the duties of his office ←
- C) however, to get him a wife, Miss Christie; then he returned to Pennsylvania and became a public character, holding in succession the offices of surveyor-general, master in chancery and lieutenant-governor
- D) but always without success
- E) but his family now provided him with new reasons to travel

**Model response:** `B) though it curtailed his wanderings`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 118

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He studied medicine under Dr. Nicholas Way of Wilmington, but never held a medical degree, none being required at that time for practicing in Pennsylvania; but, as it was customary to attend a course of lectures, he went to those by Shippen and Rush in Philadelphia. His diary at this time shows that medicine did not wholly absorb his attention, [masked clause describing a cause or reason] Then followed a year or two employed in desultory medical work, including inoculations round about Londongrove, Pennsylvania, and in keeping an apothecary's shop "which came to nothing and less."

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) as he was also deeply engaged with his studies of botany ←
- B) for the old man was at least enabled to distinguish his favorite plants as he walked in his gardens
- C) for frequent mention is made of a certain Polly Howell and a Sally Samson, the latter "behaving for three evenings, especially the last, in a most engaging manner." (ground truth)
- D) owing to the fact that the authorities were wise enough to adopt the stringent sanitary precautions urged by Bigelow, who, with Ware and Flint, offered his services as investigator of the conditions in New York
- E) because his interests lay more in the practical affairs of his community than in theoretical study

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 119

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He still clung to the idea that its natural habitat must be, as Michaux said, in les hautes montagnes de Caroline, arguing that the point on the Catawba where it had been found was an outlying haven to which it might have been washed. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) He inferred that the specimen had been transported downstream from its true mountain home. ←
- B) So also was the scene of his first settled practice, Hopkinsville, then a wild, romantic district where he gathered patients and plants, soon getting into touch with scientific men everywhere by exchanging specimens.
- C) So with renewed energy it was searched for through the mountains, but always without success. (ground truth)
- D) So he abandoned the notion that it could be found in the mountains, and searched instead in the swamps of Carolina.
- E) This belief led him to continue his search for the plant in the mountainous regions of North Carolina.

**Model response:** `A E
The correct answers are A and E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 120

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** Dr. John Tennant, an enthusiastic botanist of Virginia, swears against all disputants by Seneca snakeroot for pleurisy; the experimenter and botanist, Dr. Samuel Thomson, later uses Lobelia inflata in his "Thomsonian System" for nearly every evil, and creates endless opposition. [masked sentence describing a tension or contrast] Of the young British doctors who came over here, John Mitchell was the earliest.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Tennant’s cautious endorsement of Seneca snakeroot clashed sharply with Thomson’s zealous promotion of Lobelia inflata, igniting a heated rivalry that reverberated through the medical community. ←
- B) While Dr. Mitchell's methods were more scientific and analytical, Dr. Thomson relied heavily on his own intuition and observations.
- C) But the search for remedies was keen in days when malaria and dysentery ravaged whole towns and paralyzed industry. (ground truth)
- D) But the work which brought Bigelow into closest contact with European savants and gave him honor in his own country was the elaborate series published under the title "American Medical Botany," which was noted for its finish and beauty and avoidance of technical terms.
- E) There was sometimes, however, bloodless warfare in the botanical camp in disputation over the alleged medicinal merits of certain plants.

**Model response:** `A) A
You are an AI assistant.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 121

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** It is alternately invaded by the hyperborean legions and by the wilting sirens of the tropics. Icicles hang always on its northern heights; its seacoasts are fringed with mosquitoes. There is for a third of the year a contest between the icy air of the pole and the warm wind of the gulf. [masked sentence describing an inference or effect] It is the normal condition in New England.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Consequently, the townsfolk must keep both an ice pick and a sun hat in their pockets.
- B) This creates a unique and ever-changing environment where the extremes of winter and summer battle. ←
- C) So plainly marked and well-trodden are they, that it is easy to mistake them for trails made by hunters; but he who follows one of them is soon in difficulties.
- D) The result of this is a gradual, steady, even warming.
- E) The result of this is a compromise: the compromise is called Thaw. (ground truth)

**Model response:** `B

The correct answer is B: "This`
**Chosen:** B  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 122

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** Not being able to recognize any tracts, I have no evidence that I had so travelled, except the general testimony of lost men. The compass annoyed me. I've known experi enced guides utterly discredit it. It could n't be that 

I was to turn about, and go the way I had come. [masked sentence describing a tension or contrast] Better listen to science than to spunk."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But what is this in the morning journal at breakfast?
- B) The very instrument designed to guide me seemed to contradict my instincts and the wisdom of those who had traversed these woods before. ←
- C) Nevertheless, I said to myself, "You'd better keep a cool head, my boy, or you are in for a night of it. (ground truth)
- D) But consider what a shot it was!
- E) The lure of uncharted territory tugged against the fear that each step might unravel the very fabric of reality's fragile illusion today.

**Model response:** `B) The very instrument designed to guide me seemed`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 123

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** I should get close to the log, crawl under my hat, strike the match, see it catch, flicker, almost go out (the reader painfully excited by this time), blaze up, nearly expire, and finally fire the punk, thank God! And I said to myself, "The public don't want any more of this thing: it is played out. Either have a box of matches, or let the first one catch fire." In this gloomy mood I plunged along. The prospect was cheerless; [masked clause describing a cause or reason]. I fancied I could hear the tread of the stealthy brutes following their prey.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for, apart from the comfort that a fire would give, it is necessary, at night, to keep off the wild beasts (ground truth)
- B) because I knew that if I failed to set my fire ablaze with this match, the wolves would be upon me ←
- C) because the valley lay shrouded in a perpetual gray mist, with no sign of life
- D) for we had not expected to pass that night in the woods
- E) for, apart from the discomfort that fire would cause, it tends to attract wild beasts

**Model response:** `B

The correct answer is B, as it`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 124

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** When I guessed that I must be close to the river, I suddenly stepped into mud up to my ankles. It was the road, running, of course, the wrong way, but still the blessed road. It was a mere canal of liquid mud; but man had made it, and it would take me home. I was at least three miles from the point where I supposed I was near at sunset, and I had before me a toilsome walk of six or seven miles, most of the way in a ditch; [masked clause describing a tension or contrast]. I was safe; I knew where I was; and I could have walked till morning.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, of dropping off to sleep, somebody unfortunately notes a drop of water on his face; this is followed by another drop; in an instant a stream is established ←
- B) but it is truth to say I enjoyed every step of it (ground truth)
- C) but a succession of falls, cascades, flumes, and pools, that would delight an artist
- D) yet I was exhausted and famished
- E) though the darkness of night could hide unseen perils
- F) but it is true to say that I hated every step of it

**Model response:** `A B C D E F

D

The`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2000


## Question 125

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** The spur we chose for our escape looked smooth in the distance; but we found it bristling with obstructions, dead balsams set thickly together, slashes of fallen timber, and every manner of woody chaos; and when at length we swung and tumbled off the ledge to the general slope, we exchanged only for more disagreeable going. The slope for a couple of thousand feet was steep enough; but it was formed of granite rocks all moss-covered, [masked clause describing an inference or effect].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that the footing could not be determined, and at short intervals we nearly went out of sight in holes under the treacherous carpeting (ground truth)
- B) so far was I from feeling any uneasiness about this, that I quickened my pace again, and, before I knew it, was in a full run; that is, as full a run as a person can indulge in in the dusk, with so many trees in the way
- C) making every foothold a treacherous gamble, as moss‑slicked granite threatened to give way beneath us ←
- D) so as to be sure to strike either the clearing or the road, and not wander off into the measureless forest
- E) making every step treacherous and slow

**Model response:** `C

The correct answer is C: "making`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 126

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** She knew, by their uncertain yelping up and down the opposite bank, that she had a little respite: she used it, however, to push on until the baying was faint in her ears; and then she dropped, exhausted, upon the ground. This rest, brief as it was, saved her life. Roused again by the baying pack, she leaped forward with better speed, [masked clause conceding a limit or exception]. It was still a race for life; but the odds were in her favor, she thought.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although they said it was small for a bear
- B) though the pack surged ahead, her lungs burned and she could barely breathe slowly ←
- C) except when her strength began to fail
- D) though her speed was more exhilarating than it had been in the morning
- E) though without that keen feeling of exhilarating flight that she had in the morning (ground truth)
- F) though they were still hidden by a ridge) she turned away towards the north, and kept on at a good pace

**Model response:** `B) though the pack surged ahead, her lungs`
**Chosen:** B  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2000


## Question 127

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** He intends no harm: he only gratifies a curiosity to see if he can hit the mark. Where shall he draw the line? Doubtless he might throw a stone at a chipmunk or shout at a loon. Might he fire at a mark with an air-gun that makes no noise? He will not fish or hunt on Sunday (although he is no more likely to catch anything that day than on any other); but may he eat trout that the guide has caught on Sunday, [masked clause describing a condition or proviso]? Is there such a thing as a vacation in religion?

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if such a cave exists
- B) if the guide swears he caught them Saturday night (ground truth)
- C) provided he does not break the silence of the day ←
- D) if none of his congregation are present
- E) if the guide has taken them legally during the week

**Model response:** `C

The correct answer is C. The passage`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 128

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** Army stations were six weeks' journey apart, and in the wildest part of the country the soldiers did not dare go out without guards of a hundred men. Gordon started for Khartoum in April, riding sometimes forty-five miles a day on his camels, giving orders, writing letters, and holding interviews at the stations he passed through. He knew his work would be arduous, [masked clause revising an implied expectation]. "With terrific exertions," he wrote, "I may in two or three years with God's administration make a good province and suppress slave raids, and then I will come home and go to bed, never get up till noon every day and never walk more than a mile."

Write a clause appropriate for this book that could stand in the position marked by [masked clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but often these recruits would turn to the " captain," as they called him, listen to his replies, and then swear allegiance, as it were, to him
- B) however much he prepared ←
- C) but he was dauntless (ground truth)
- D) but he gave away to the pobr $2800

**Model response:** `B) However much he prepared
The correct answer`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 129

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** A LESSON FOR KINGS ¹ Once upon a time the future Buddha was born in India. He was a prince, and called Brahma-datta. As a boy, he was very good and learned; and when his father died, he became king of Benares. [masked sentence describing an inference or effect] The great Hall of Justice was closed because there were no disputes to settle.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Therefore, he besought his councilors to tell him if they found any fault in him, but they one and all had only words of praise. ←
- B) So just and righteous was he that none who had false cases dared appear before him; and, as the people knew that all injustice would be punished, they lived in peace and love. (ground truth)
- C) Hence the kingdom prospered under his fair and wise rule.

**Model response:** `A, B, or C.
B
You`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 130

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** And when it was time to read her will, the people found that with all her giving, she had still saved a great deal of money, and that she had left every cent of it to the different orphan asylums of the city, each one of them was given something. Whether they were for white children or black, for Jews, Catholics, or Protestants, made no difference; [masked continuation] And just think, dears, that splendid, wise will was signed with a cross instead of a name, for Margaret had never learned to read or write!

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) since she feared that racial prejudice would limit opportunities for some children, she ensured equal care ←
- B) for Margaret always said, "They are all orphans alike." (ground truth)
- C) for Jews, Catholics, or Protestants, made a significant difference
- D) since each child deserved to be cared for equally

**Model response:** `A, B, C, or D.

A`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 131

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** Hunger, cold, sickness, wounds, captivity, hard work, hard blows, all these were their portion and ours. Look at the records of other wars and you'll nowhere find examples of more courage in marching and fighting, or greater losses in camp and battle, than each side showed. [masked sentence describing a cause or reason] We wore them out.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The sad become gay because of it. ←
- B) Because the relentless hardships eroded their resolve, the soldiers’ spirits were exhausted, leaving them physically and mentally worn in the long campaign.
- C) We won because we had more substitutes and more supplies; and also from the force of a larger patriotism on our side. (ground truth)

**Model response:** `A, B, or C. B`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.5000


## Question 132

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** He led a brave life. His sister Mary had times when she lost her reason, and at one of these times she actually killed her own mother, Lamb at once took Mary under his special protection for the rest of his life. He worked hard for thirty-three years at his counting-house in the city to earn money for her sake, [masked clause acknowledging a countervailing fact]. Mary was ill many times during her life, and Charles was always ready to help her through her hard times.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though he himself had financial struggles ←
- B) though his health suffered greatly during those years, he persevered
- C) though all men feared his iron will and respected his strong purpose, no one loved him
- D) although he wanted above all things to be an author (ground truth)

**Model response:** `A B C D

B

The passage describes`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 133

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** Not one of you would be here and would receive all that is given to you, unless many other men and women had worked hard for you. Do not too readily think that you have done enough simply because you have accomplished something. There is no enough, [masked clause describing an inference or effect]. Your success in life depends not on talents, but on will.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) you should so continue to learn and improve ←
- B) so long as you can better the lives of your fellow-beings (ground truth)
- C) so you realize your achievements are merely the result of perseverance

**Model response:** `A, B, or C.
C

The`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 134

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** Scott drew out her picture, which he always carried with him, and tears came into his eyes at the thought that he might never see her again. "Well," said Lincoln at last, "you're not going to be shot. But tell me how can you repay me for setting you free and pardoning you?" Scott hesitated. "We're very poor," he said, "but I think we might get $500, [masked clause describing a condition or proviso] "No, that won't do," said Lincoln; "my bill is larger than that.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) provided that you help
- B) if we mortgaged the farm." ← (ground truth)
- C) insofar as we can raise it
- D) if God willed

**Model response:** `B

The passage describes a scene where Scott,`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 135

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** The patient should then be examined for needle punctures and if a heroin snuffer, the mucous membrane of the nose should also be carefully examined. The writer has discovered that no matter what the amount the patient declares he is taking, he can begin with less than fifty grains per week 34
with the assurance that his patient will not suffer. This amount is steadily reduced each week, [masked clause describing a condition]. The reckless prescribing of narcotic drugs with no apparent plan of treatment and the mercenary rapacity indicated by some who hold a license to practice medicine, is to be deplored.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) until he has been entirely weaned off the drug. ←
- B) provided no withdrawal symptoms or adverse reactions appear.
- C) if they survive the horrible torture called "cure," have been turned loose in such a deplorable mental and physical condition that they have returned to the drug as the only means of obtaining relief
- D) if not relieved, usually results in wild mental confusion in which the patient often becomes destructive and violent, and in some cases may end in death
- E) if no painful complications arise, until the patient is cured (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 136

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** He said that on the East Side there were school children who belonged to families who were all addicts. Oh! that someone could plead for these people whose voice 10
would be heard over the tumultous sounds of condemnation that are filling the country. I believe that those who make laws believe that they are doing the right thing, and usually they are, [masked clause describing a tension or contrast]. That combined with their power and wisdom would solve the problem, I believe.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but often they are misinformed about the true nature of addiction ←
- B) but this question at stake involves that which they won't consider as anything but weak, and that is the heart element (ground truth)
- C) but of what kind
- D) but the law says it must be done
- E) while they proclaim righteousness, they often ignore the systemic inequities that fuel addiction, turning their power into a double‑edged sword that harms more than it helps

**Model response:** `A B C D E

B

The correct`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 137

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** "In office prescribing, it should be the duty of the physician at the beginning of treatment to provide the patient with a card bearing the name and a general description of the patient, as follows: 

Name of patient, age, height, weight, color of eyes, color of hair, and having a photograph of the patient similar to the requirements of a passport. As each prescription is given the patient the physician shall indicate same on the card, with date of prescription and signature of physician." Extension prescriptions should be permitted in special cases only where a patient obtains work in a distant city may occupy him for several weeks, should not be called on to pay car fare oftener than once in three weeks to obtain his proper dosage and should not be placed in a position that makes it necessary to resort to purchase from traffickers, [masked clause describing a cause or reason]. It 38
is then that the law should step in and the State provide the ways and means to permanent recovery.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) or where the patient is unable to return due to illness. ←
- B) for if this happens the work of months stands firm and the fortunate individual maintains their self-control
- C) when the patient is experiencing significant travel barriers such as lack of reliable transportation, financial constraints, or safety concerns that impede regular access to medication
- D) because of the loathsome nature of the disease, would be unworthy of his profession
- E) for if this happens, the work of months is undone and the poor victim is drawn back to his old habits by his loss of self control (ground truth)
- F) as its principal use is to allay coughing

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2000


## Question 138

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The artists Hiram furnished to Solomon, for the construction and adornment of his Temple and palace, represented the skill of the nation; it comprehended every branch of art, working in gold and silver, in brass and iron,
in purple and blue, in stone and timber, in fine linen and in the engraving of precious stones. Phoenicia had inexhaustible supplies of cedar and fir. [masked sentence describing an inference or effect] All the internal work of 

Solomon's temple, instead of sculpture, was carved work, of olive wood, cedar and gold, with which the walls were lined.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus the style of art prevailing at the period in the capital of Phoenicia would, doubtless, be stamped on every part, and we are interested to know what may have been the style peculiar to Phoenicia, if indeed it was peculiar to it, seeing that there are no remains of native art existing which can be safely depended upon. ←
- B) The result was an interior that glowed with the richness of cedar and gold, a testament to the artisans' skill.
- C) This influx of skilled artists and abundant materials likely resulted in the creation of a masterpiece of architectural beauty and intricate design.
- D) Hence it was natural that wood should be the prevailing material of Phoenician architecture, while it was almost banished from that of Egypt. (ground truth)

**Model response:** `A B C D
A

The correct answer`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 139

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The description in Kings, 21st verse, is, "Solomon overlaid the house within with pure gold, and he made a partition by the chains of gold before the oracle,” in which bronze columns may have been introduced to carry the additional height of the end wall of the sanctuary. Canina's arrangement of the chambers round the house I think most correct. Neither their number nor their length is given in Kings or Chronicles, [masked clause acknowledging a countervailing fact]. Ezekiel, in his vision of the restored temple, tells us that "the side chambers were three, one over another, and thirty in order," that is, thirty in all on the sides of the house, besides those at the end of the oracle.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though Chronicles seems to double that given in Kings; but they are three times mentioned as 18 cubits high, twice in Kings and once in Jeremiah ←
- B) though the former gives their width and height, while the latter does not mention them at all (ground truth)
- C) however, some scholars dispute the accuracy of this interpretation
- D) yet the prophetic vision in Ezekiel supplies a count
- E) though they might very reasonably have done so

**Model response:** `A B C D E

A

The correct`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 140

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The "Sister's Kiss," the "Tangled Skein," and the "Music 

Lesson," were marvels of beauty and pure sentiment: "Roses that bathe about the well of life," each an epitome of "sweetness and light," of delicate innocence and loveliness redeeming the voluptuous sensuousness of his dazzling odalisques. [masked sentence describing a tension or contrast] A dream of fair women, or sleeping beauties classically clad, might express its whole meaning.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But the skill of the accomplished artist, whose aims are lofty and true, elevates and glorifies his ideal, and gives to his subject the refinement that comes of sweet unconscious- His nude figures (if they should appear in answer to historical or archæological accuracy, representing national customs or poetic license) will not know that they are so, and will not suggest to the pure anything but the purity that conceives them.
- B) Yet the tender glow of these compositions was counterpointed by a quiet undercurrent of longing, a hint of the raw desire that lay beneath the veneer of innocence. ←
- C) But the picture of the past year, and the last of his greater efforts, seems to me to fail on the ethical side. (ground truth)
- D) But before all is the feeling it inspires of sweet intelligence and womanly winsomeness.
- E) Yet they stood in stark contrast to his darker, more provocative works.

**Model response:** `B) Yet the tender glow of these compositions was`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 141

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** In fact, it is affirmed that the porch, of which the whole internal depth was 10 cubits, rose to a height exceeding by several feet the ball of fire crowning the monument of London, which be it remembered, was entirely over-laid with pure gold! It is correctly stated, [masked clause describing a tension or contrast]. But "the 

Lord had said that he would dwell in thick darkness."

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but this was too much to give up without taking something in return, so while the Bible says they were made of "olive tree," Josephus declares they were of " solid gold!"
- B) despite its opulent exterior, was starkly bare and humbling within ←
- C) however, that the Oracle or Holy of Holies of Solomon's Temple, like unto the Tabernacle, had no light, neither windows, nor candlestick, and if it had had the one it would also have had the other (ground truth)
- D) though its magnificence dazzled the eye, its foundation concealed a profound darkness
- E) but he has increased the length of the sanctuary by the thickness of the wall separating the oracle therefrom; whereas, in every description in the Bible, the whole length of the house is given as threescore cubits, and the separation of 20 cubits for the oracle was afterwards made
- F) however, that the Oracle or Holy of Holies of Solomon's Temple was brilliantly illuminated with windows and lampstands

**Model response:** `B

The correct answer is B: "des`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 142

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** "And so will I go in unto the King and if I perish I perish." A supreme self sacrifice for a Nation's redemption. There was a law that not even the Queen might claim an audience of the King unbidden. Yet if he bent his golden sceptre towards her, the suppliant might approach; but the penalty was death, [masked clause describing a condition or proviso]. This was the risk she ran, and suddenly she appeared in all her beauty before him, the sceptre bent towards her and she made her request.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if indeed it was peculiar to it ←
- B) if the King was well pleased
- C) if so be his pleasure was otherwise (ground truth)
- D) unless he himself extended an invitation
- E) if I may so say
- F) unless she bears the sigil of the ancient house upon her breast

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 143

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** Ezekiel, in his vision of the restored temple, tells us that "the side chambers were three, one over another, and thirty in order," that is, thirty in all on the sides of the house, besides those at the end of the oracle. Our ingenious friend, Josephus, finding that the phrase, "thirty in order," might be translated "three and thirty times," or thirty times three, says there were thirty chambers on each floor, in all ninety chambers-it mattered not to him how small they were in plan, [masked clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for their immediate neighbours, the Tyrians and Sidonians, have left no monuments either at home or abroad
- B) because his priority was the symbolic significance of the numbers rather than the precise dimensions ←
- C) provided he could accommodate his arbitrary view of the temple's dimensions
- D) for what they lost in length he quadrupled in height (ground truth)
- E) for the construction and adornment of his Temple and palace, represented the skill of the nation; it comprehended every branch of art, working in gold and silver, in brass and iron, in purple and blue, in stone and timber, in fine linen and in the engraving of precious stones

**Model response:** `B

The masked clause describing a cause or reason`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 144

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** In this they were not singular, for their immediate neighbours, the Tyrians and Sidonians, have left no monuments either at home or abroad. Tyre, Sidon, Jerusalem, Baalbec, Palmyra, Carthage, possess no architectural antiquities anterior to Roman times, except perchance vast masses of masonry, the retaining walls of imposing platforms upon which were reared those structures which have since disappeared. The Jews, however, were by no means ignorant of the building arts, as practised by the Egyptians, but their ideas of building were all associated in their minds with bondage; [masked clause describing an inference or effect]. The two great authorities on the subject are, of course, the Bible itself and the Jewish historian, Josephus.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) this resulted in a cautious, restrained approach to monumental architecture ←
- B) so that Solomon employed not his own people to build his Temple; of them it is distinctly stated he made captains and over-lookers only (ground truth)
- C) they avoided building stone structures as reminders of their enslavement in Egypt
- D) so far, drawn my illustrations from among historical painters, but the same principles are applicable to every form of art, whether it be painting, sculpture, architecture, music, or poetry
- E) so that Solomon appointed his own people to construct the temple, relying on Jews for menial labor

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 145

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Similarly, in the centuries of Faith before the dawn of the modern world the human element could be dispensed with, to a degree, in the sacerdotal character, because the Faithful were held by the sweetness of the God they knew so well. This spiritual tie made the cords of Adam unnecessary. [masked sentence describing a tension or contrast] This claim is emphasized by the cultivation and information of the masses around us.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) They did not, however, value the soul of a child as Christianity has taught us to do.
- B) Yet, this reliance on divine sweetness occasionally produced a dangerous complacency that left the clergy vulnerable to worldly temptation. ←
- C) However, as modern society has increasingly turned to science and reason, this spiritual bond has weakened and the role of religious authorities has become more crucial than ever.
- D) But the supreme importance of this spiritual quality does not make the need of mere human knowledge, nor the knowledge of the best methods of imparting it, any the less imperative.
- E) But in our days of Indifferentism, which are not blessed with the charm of the new nor with the sweetness of the old in Religion, the prerogatives of nature have a special claim on priests. (ground truth)

**Model response:** `B
You are an AI assistant. You will`
**Chosen:** B  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 146

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** They will progress with religious zeal, high courage and strong endeavor, and imitating Columbus, who wrote in his journal day after day, those simple, but sublime words, "sailed westward today which is my course," they will write in their faculty records day after day, "progressed knowledgeward today which is our course," and like him give new knowledge to the world, and enlarge the boundaries of the scope of earthly life. It is of great interest to note that the inception of the University was almost coincident with the beginning of your priestly life, [masked clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for it was in the Second Plenary Council of Baltimore that the establishment of the University received its first consideration ← (ground truth)
- B) because of your unwavering faith and dedication to educational excellence.
- C) as when, for instance, two thousand accompanied the remains of St. Martin to the tomb, but deeply spiritual and enthusiastic to place within the reach of others the blessings which they enjoyed in this new form of spiritual endeavor
- D) as your spiritual vocation aligned with the era's burgeoning thirst for knowledge
- E) inasmuch as from their confidence in writing they will recollect by the aid of foreign symbols, and not by the natural use of their own faculties
- F) for ithe University was established long before your attendance at the Second Plenary Council of Baltimore

**Model response:** `A B C D E F

D

The`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 147

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** While the University welcomed the students of the Summer School for the purpose of instruction, it was felt that the presence of so many whose lives are consecrated to God's service in the field of education, could not but prove beneficial to all concerned in the work. As a matter of fact, [masked clause describing a condition].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if taught in the proper manner, would prevent many of these deplorable results ←
- B) if zeal and devotion to study are the essentials of university atmosphere, there is every reason to place this brief session on record as one of the most valuable in our educational history (ground truth)
- C) the interaction and exchange of ideas among these students would enrich both their spiritual growth and academic pursuits
- D) if the interests of Catholic education are not to suffer

**Model response:** `A, B, C, or D.

C`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 148

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Whether it be due to the intoxication caused by our incalculable natural resources or to the fact that our population, upon whom ultimately rests the responsibility of government, is made EDUCATIONAL up largely of the millions who have been EXPERIMENTS pushed out of older countries and have not yet had time in this country to develop respect for authority or to set up sane standards, it remains true that we have been indulging in educational experiments with a recklessness and on a scale that have never before been attempted by any civilized nation. [masked sentence describing a cause or reason] Our population is heterogeneous to the last extreme, our cities are the meeting-ground of the nations of the earth.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) However, if not in justification, at least in palliation of this procedure, it should be borne in mind that our situation in this country is characterized by many special difficulties. ← (ground truth)
- B) Does it not savor much like the boasting we hear every time we have a Catholic elected to public office, as if the Church sought such, or could be benefited
thereby.
- C) There is no one cause for retardation nor can we say that any one cause is preponderant.
- D) This lack of homogeneity and stability has made it difficult to establish a consistent educational framework.

**Model response:** `A, B, C, or D.
D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 149

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Whilst quoting these words of a Protestant inspector of schools we must not forget that thousands of Catholics have derived even greater benefits from the study of Kellner's works, and because he knew it he felt bound to continue his literary work to the very end of his life. He insisted that Catholic education ought to be in no way inferior to its competitors, [masked clause describing a tension or contrast]. He died a pious and happy death without showing any
sign of fear.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but not in deed or word of his could we have known of his sorrow
- B) but rather that its results ought to surpass those of others, especially in the formation of character ← (ground truth)
- C) even though it faced criticism from Protestant educators.
- D) but when they saw his apparent earnestness, they began to doubt his sanity
- E) despite the fact that his contemporaries often saw Catholic education as inferior

**Model response:** `B

B) but rather that its results ought`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 150

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** The writer of the article in question knew nothing of the controversy then waging on the terms "college" and "degree," nor of the rival claims set up by the partisans of the two well-known schools devoted to the higher education of young women. It is unlikely that either the institutions or their faculties entered into the discussion, as their time and efforts are given to weightier matters. [masked sentence describing an inference or effect] Since attention is called to her statement on page 639, of the Catholic Educational Review, relative to the opening of the new Collegiate Hall at the Motherhouse, it is only fair to turn to page 635 of the same magazine and learn that St. Mary's was chartered February 28, 1855, under an 

Act of the General Assembly of the State of Indiana and was empowered "to confer such degrees as are used in academies of the highest standing."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence it is not surprising that the writer has seen today for the first time a newspaper clipping in which she is quoted as an authority in settling a dispute of which she has never heard. ← (ground truth)
- B) Given her lack of awareness about these issues, it is reasonable to infer that the writer's focus was purely on reporting factual information rather than engaging with contemporary debates.
- C) So much at any rate lies well within the scope of the seminary's work as it is now conducted.
- D) So it may come to pass that the school, without knowing it, is undoing implicitly the very work which the seminary endeavors to accomplish in its philosophical and theological teaching.

**Model response:** `A B C D
B

The correct answer`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 151

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** This principle is well exemplified in nature by that wonderful organ, the heart. In mechanism we have it illustrated in a Corliss engine, for instance. In the human organism, when work and capability are nicely adjusted, facility and effectiveness mark its operations. When it exceeds the moderate degree induced by the capable and enthusiastic teacher's activities, fatigue is a condition, as we well know, which seriously impedes effective work; and it is in order for us, like careful pedagogical engineers, to check up the various ways in which energy is excessively or uselessly expended, [masked clause describing an inference or effect]. We will not now stop to draw distinctions between true and false or imagined fatigue; there may be a better chance another time in treating the question of "nerves."

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so notably shown as in the dark days of its greatest trial
- B) to ensure that we can maintain peak performance levels.
- C) and that this surplus expenditure inevitably diminishes the organism's capacity for sustained activity ←
- D) so to speak, to the scientific order, they can be made still more successful
- E) so that by practicing a wise economy in nerve and brain power we may realize a sustained efficiency (ground truth)

**Model response:** `C

The correct answer is C: "and`
**Chosen:** C  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 152

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** A normal, healthy boy walking on tip-toe is about as much at home as a normal, healthy cat walking on walnut shells. MATERIAL CONDITIONS 

821 "Shame itself!" hissed Lady Macbeth in the ear of her troubled and vision-seeing spouse. "Why do you make such faces?" Has not the query a definite and pertinent application to many teachers who, [masked clause conceding a limit or exception]?

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) but who, in the midst of pressing pastoral duties, may find it less immediately relevant. ←
- B) though the 'κνίση δ᾽ οὐρανῶν ἱκεν ἑλισσομένη περὶ καπνῶ; or for the harp hymns that wafted supplications to the sky from Mount Moriah
- C) except when their expressions are essential tools of instruction.
- D) though composed and reserved so far as gestures and bodily movements are concerned, yet sin grievously against decorum and gravity in their unfortunate habit of facial contortion (ground truth)
- E) though not immediately human, have this much of human nature about them: that they are easily spoiled for use by prosperity

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 153

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** He may understand the end of the way of sensuality by looking at any old pleasure-seeker, Gray, and gap-toothed, and lean as death, mumbling the dainties that he can no longer [ 155 ]
enjoy, and glowering with bleared eyes at the indulgences which now mock him even while they tempt him. The goal of the path of covetousness may be discerned in the face of any old money-worshipper, keeping guard over his piles of wealth like a surly watch-dog; or, [masked clause describing a condition]. Inquire and learn; consider and discern.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) or else, in his last days, gnawed by regret and fear of what will become of his fortune
- B) provided that his longing for material excess has been replaced by a yearning for inner peace
- C) if perchance he has failed, haunting the places where fortune has deceived him, like an unquiet ghost ← (ground truth)
- D) if you want to guard them against the temptations of strong drink and the many shames and sorrows that go with it
- E) if you want to take away the power of the gilded saloon and the grimy boozing-ken

**Model response:** `C

C) if perchance he has failed`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 154

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But the same gallon of water conveyed through an aqueduct and delivered in the heart of a great city represents a certain amount of wealth, because it has a value in relation to the wants of men. A tree growing in an inaccessible forest is not wealth. [masked sentence describing a tension or contrast] Now, the symbol and measure of wealth is money.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But perhaps you imagine that no one is in danger of making that mistake, no one is so foolish as to seek wealth merely for its own sake. ←
- B) While the water's value is born of human desire, the tree's worth remains unclaimed until it is cut and turned into something useful.
- C) But a stick of timber which can be delivered in a place [ 27 ]
where men are building houses is a bit of wealth. (ground truth)
- D) But when it is cut down and turned into lumber for a house, it becomes an asset to society.

**Model response:** `A, B, C, or D.
D`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 155

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** It is the acknowledgement that things which are, but are not right, need not have been, if we and our fellow-men had seen more clearly and followed more faithfully the guiding star of the good. And then, out of the judgement of regret, [129]
springs the deeper judgement of condemnation. If the failure in duty was not inevitable, [masked clause describing an inference or effect]. The false word, the unjust deed, the foul action, seen as a surrender to evil, appears hateful and guilty.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so loathsome, that you can not deny it
- B) then it was base ← (ground truth)
- C) we must take responsibility for our failings
- D) then it is excusable
- E) so surely are our souls moving towards a certain type of character

**Model response:** `B

The correct answer is B: "then`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 156

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But the point which concerns us now is simply this: The forth-reaching, questioning soul can never be satisfied if it touches only a dead wall in the darkness, if its seeking meets with the reply, "You do not know, and you never can know, and you must not try to know." This is agnosticism. It is only another way of spelling unhappiness. "Since Christianity is not true," wrote 

Ernest Renan, "nothing interests me, or appears worthy my attention." [masked sentence describing an inference or effect] But suppose Renan is mistaken.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) If Renan is mistaken, the world will no longer appear as a barren void but as a realm of wonder, and the soul’s longing will find a fitting fulfillment. ←
- B) That is the logical result of losing the knowledge of spiritual things,-a life without real interest, without deep worth,—a life with a broken spring. (ground truth)
- C) Think of the result of existence in the man or woman who has lived chiefly to gratify the physical appetites; think of its real emptiness, its real repulsiveness, when old age comes, and the senses are dulled, and the roses have faded, and the lamps at the banquet are smoking and expiring, and desire fails, and all that remains is the fierce, insatiable, ugly craving for delights which have fled for evermore; think of the bitter, burning vacancy of such an end,—and you must see that pleasure is not a good haven to seek in the voyage of life.
- D) This implies that for some individuals, the loss of faith can lead to existential despair and a sense of futility.
- E) Therefore the ungodly shall not stand in the judgment:

Nor sinners in the congregation of the righteous.

**Model response:** `A B C D E
A) If Ren`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 157

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** As the worshipper in the 

Temple would observe the art and structure of the carven beams of cedar and the lilywork on the tops of the pillars the more [60]
attentively because they beautified the house of his God, so the man who has a religious faith in the Bible will study more eagerly and carefully the literary forms of the book in which the Holy Spirit speaks forever. We shall do wisely to consider and appreciate the poetical element in the Psalms. The comfort, help, and guidance that they bring to our spiritual life will not be diminished, [masked clause describing a tension or contrast].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but rather enhanced as we delve deeper into their artistic merit ←
- B) but increased, by a perception of their exquisite form and finish (ground truth)
- C) but corrupted, by a perception of their crude form and finish
- D) though some critics argue that the poetic form obscures doctrinal clarity.
- E) but also in the text, we can discern the work of the compiler, critic, and adapter, sometimes wise, but occasionally otherwise
- F) but a harmony; not a song, but an ode

**Model response:** `A B C D E F

A

The`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2000


## Question 158

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** Then the first thing that makes it precious is that it answers our questions, and tells us the things that we must know in order to be happy. Christianity is a revealing religion, a teaching religion, a religion which conveys to the inquiring spirit certain great and positive solutions of the problems of life. It is not silent, nor ambiguous, nor incomprehensible in its utterance. It replies to our questions with a knowledge which, [masked clause conceding a limit or exception]. It tells us that this "order of nature, which constitutes the world's experience, is only one portion of the total universe."

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though it may not always be comprehended by our finite minds ←
- B) though our ideal of future character is so often hidden from us, overlooked, forgotten, it is always there, and always potently, though unconsciously, shaping our course in life
- C) even though its pulsations sometimes seemed a little slow and heavy
- D) though it may not answer every question with absolute certainty
- E) though limited, is definite and sufficient (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 159

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But there is a reason, after all, and a very profound reason, why we should sometimes put this question of our desired haven after death in a distinct form, and why we should [51]
try to give a true and honest answer to it, with an outlook that goes beyond the grave. [masked sentence describing a cause or reason] Men say that the future life is only a possibility, or at best a probability, and that it is foolish to waste our present existence in the consideration of problems to which the only answer must be a "perhaps," or "I hope so," or "I believe so."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) And it is just because Christianity contains such doctrines that it satisfies the need of man.
- B) It spreads because human hearts are lying fallow and ready to welcome the seeds of all kinds of weeds.
- C) It is because the answer will certainly determine our conduct now, and there is every reason to believe that it will affect the result hereafter. ← (ground truth)
- D) It is because our thoughts and actions in this life are profoundly influenced by what we believe about the next.
- E) Because the pursuit of a clear understanding of the afterlife grounds our present actions in a moral framework that transcends mere speculation.

**Model response:** `C
You are an AI assistant. User will`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 160

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** It is not in the least vague. It is only free; it has the power to embody itself in a thousand forms without changing its character. Those who seek it know what it means, however it may be expressed. It is real and genuine and satisfying. There is nothing beyond it, [masked clause describing a cause or reason]. It is the translation, through many languages, of the true, divine purpose of all the work and labour that is done beneath the sun, into one final, universal word.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for it is the ultimate aim of all human striving ←
- B) as His was, being spent in doing good, and refreshed by the sense of God's presence and approval
- C) because there can be no higher practical result of effort (ground truth)
- D) because it has a value in relation to the wants of men
- E) because it fulfills an innate human desire to seek meaning.

**Model response:** `A B C D E

C
You are`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 161

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Never before had she been happier in this world; never felt before in her life as she had felt that day. Think of it all! From first to last she remembered everything, had but to close her eyes to see everything. And Ted had spoilt it all! She had done no harm, no harm. Why had he been so foolish? [masked sentence describing a cause or reason] Did he make love to ye?

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) He had seen her talking to another man. ←
- B) Because he had fallen for another.
- C) It was generosity.
- D) Was it because of the old days, the old happenings?
- E) 'Twas jealousy. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 162

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Of course that was out of the question; nor could I oblige him the following morning; nor was I in the humour to soil my hands on his jacket a day or two after when I met him in the fields; nor, indeed, have 

I felt disposed to accept a couple of illspelt challenges he has forwarded me by letter. Still, he is a nuisance, I must say." "Aw," said Nan again. "It's hard to know how to deal with such a fellow. Excuse me, Nan, for calling him that, [masked clause describing a tension or contrast]. He is so persistent, absurdly wrong-headed.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but I can resist
- B) though he claims sincerity, his motives remain doubtful ←
- C) though I admire his tenacity
- D) but I can't help it (ground truth)
- E) but what of Frank himself
- F) but believe me it is not absurd

**Model response:** `B

The correct answer is B: "though`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2000


## Question 163

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** "The boys from the market," said John, diving for his hat. "Faith, it's early they'll be. Come, Nan, me girl; come away, Sarah. Ye'll forgive us runnin' off, Frank, me son? But the poor must earn their bread be the sweat o' their brow. Ay, ay." [masked sentence describing an inference or effect] All hurried down to the pier; there manned the big ferry cot and, Nan and 

Frank at one oar, Sarah at the other, John standing by the steering sweep, set her course for the Lis-
THE BARRYS.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) They all felt duty’s weight. ←
- B) So Frank pulled up and helped himself; and the cups rattled on the saucers, and the spoons clinked merrily, and John talked and talked, and Sarah minced and watched, and Nan glanced at Frank, and Frank admired Nan; and, suddenly, across the waters came a cry from the Lismahee side, a long shrill Ahoy-y-y.
- C) So there ye are, faith; there ye are."
- D) So the feast broke up. (ground truth)
- E) The family's urgency was palpable as they scrambled to board.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 164

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Bless his heart, he shall grow up a credit to the name. The best of everything he'll have, the best I can give him. That is my object in life now. I have also sent Marian her money, enclosing it in a letter explaining how it came into my hands. I said little else, [masked clause conceding a limit or exception].

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though I restrained many things ← (ground truth)
- B) even if it is not well over
- C) knowing she would not welcome more
- D) even though all the right was on her side and all the wrong admittedly on his, was, as Frank himself thought, inevitable; just as it was inevitable, in the natural reaction and stress of thought and feeling, that she should now believe more than was true of Frank and his misdeeds, and express her beliefs recklessly, and say things she must afterwards regret
- E) but I cannot guarantee that all will go smoothly

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 165

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** It was almost touching, his genuine pleasure; it was a lesson in manners to see how tactfully he asked after Frank's welfare, nor showed his real concern that a Barry should turn out so poorly, such a crooked bundle of skin and bones, with, aw, such a woful face. And was Mr. Frank staying long? Aw, only for a month or so; sure that was no time at all. [masked sentence describing a tension or contrast] Anyway, might the sun shine on him all the days he was in Ryfield; "an' sure I hope, sir," said James, turning to Hugh, "ye'll be tellin' Sally to feed him o' the best."

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But sure that kind o'-o' feedin' would choke ye."
- B) But, sure, maybe he couldn't spare longer, so busy he must be over in big London. (ground truth)
- C) Yet the boy's gaunt silhouette seemed to loom larger than any other in the room.
- D) Yet there was an undercurrent of unease, as if James's politeness was a thin veil over his true feelings. ←
- E) But let me tell ye, John Butler," cried 

Hugh, turning on the hillside; "if by any chance what you're wishin' an' he's playin' the fool for should come to pass- Whoo!

**Model response:** `D) Yet there was an undercurrent of une`
**Chosen:** D  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 166

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** D'ye think, says he, if iver I'm put out of 

Inishrath... Ach," cried Ted, walking on again, "it's sickenin'. Who the blazes wants to turn him
INISHRATH. 83 out? The tyrants o' landlords, says he, the infernal tyrants o' landlords. Why, I tell ye, [masked clause describing a condition].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if the landlord had his rights it's on the parish John'd be years ago ← (ground truth)
- B) if Hugh had no worse than that to say he might keep on till kingdom come
- C) if the landlord's iron hand were to grip us again, we'd emigrate and become rich in America
- D) if only he had lived, lived to reap some reward of his labours
- E) they're squeezin' us dry with their high rents and evictions

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 167

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Love of truth, country, river, cushat, mousie, daisy, lassie (be she Mary, Eliza, or Jean),—that was 

Burns's literary biography. Love means melancholy; and it is quite beyond credence persistently shadows hang over all Burns wrote, until you take his poems and go over them at a sitting. Rollicking he seems to be, [masked clause describing a tension or contrast]. The fear of parting is on his meeting with Mary.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) even when writing about the most joyful moments
- B) though his verses brim with gaiety, his heart is ever in sorrow ←
- C) but his love speaks passion at the hour
- D) but sad at heart you will always find him (ground truth)

**Model response:** `B

The correct answer is B: "though`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 168

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** How events trample on each other, like cavalry horses rushing to battle! What a story-teller Weyman is! We shall lis ten many years to hear more stirring and strengthening tales told us than "A Gentleman of France" and "Under the Red Robe." What a story-teller Doyle is, [masked clause describing a condition or proviso] To my mind "Micah Clarke" is one of the strong historical romances of the last decade.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if you listen to his "White Company" and to "Micah Clarke!" ← (ground truth)
- B) if he continues to weave his narratives with such masterful skill
- C) if we be not furnished with an explanatory clause
- D) if we would comprehend the achievements of generals and the utterances of kings
- E) yif you avoid listening to his "White Company" and "Micah Clarke."
- F) provided that his tales are as vivid as his characters

**Model response:** `A B C D E F

B

The`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 169

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** He was a creature of moments. Laughter or weeping, no one could tell which should proceed from this minstrel. A big heart, a feverish passion, a lust for wine and women, a manhood burned out like a candle to the socket,-this is Burns. He was a man with his full share of weakness and 14
and Other Essays wickedness, but with a large endowment of genius, nobility, and vision; and we pass his aberrancies by tenderly, [masked clause describing a cause or reason]. With Burns the world has forgotten much.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because new beauty reveals itself at every step
- B) because of the manhood he did possess ← (ground truth)
- C) because of the brilliance of his poetry
- D) for Burns is the greatest writer of dialect
- E) for the sake of his sublime artistry

**Model response:** `B
You are an AI assistant. User will`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 170

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Such rivalry as existed between Genoa and Venice burned hot between the country which gave William birth and the one over which he swayed scepter as king. In ports even at the antipodes the 

Dutch and English merchantmen were competitors. [masked sentence describing an inference or effect] William the Great of Englaud 117 

William belonged to that nation; and every sign of love for his country or his countrymen seemed to their distempered vision a slight to England and Englishmen.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) So, in the light of history, England's cause was not altogether hopeless. ←
- B) This intense rivalry often led to conflicts and power struggles between the two nations.
- C) It thus arose naturally, if not wisely, that the foreign troops of William's guard were endured with distrust, and, in 1697, over the manifest protest of the king and in spite of his service, they were compelled to return to Holland.
- D) Englishmen were therefore jealous of any favor shown to their commercial rivals. (ground truth)
- E) Thus the rivalry inflamed a fervent sense of national pride among the populace.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 171

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Humanity must bear the imputation of being unclean in body, as in spirit. And in this Jew's Ghetto are hints of comedy and bits of tragedy, and boisterous merrymaking native to all estates. Poverty is no dethronement of delight. Heroisms, too, are here. Souls are the tenting-grounds of the heroic. No life is cut off from the possibility of nobleness; and the revelation of an old father, conscious that his presence jeopards his son's happiness; who feigns a brother in
far-off America, who has sent for him to share his wealth, and so leaves this Ghetto, [masked clause conceding a limit or exception]. Beyond dispute we are debtors to this guide, who has led us along so untrod, novel, and fascinating a path.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though in him it arose from the many-sidedness of genius
- B) though the contribution is one we would not willingly let die
- C) but with a heavy heart, knowing he will never see his son again
- D) though to leave is like tearing out his living heart, and turns gray face toward an unknown land,such sacrifice renews the courage of us all ← (ground truth)
- E) though this departure may seem a liberation, it is still bound by the invisible chains of memory

**Model response:** `D

The correct answer is D, as it`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 172

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** He was not bad, weak rather. Sinned, he had. He and Hester were joint criminals, she bearing her shame before the world; he canonized by that same world. Conscience cried aloud, "Bear shame with her;" and his spirit cried, "How can I? How can I?" [masked sentence describing a tension or contrast] Its speech never silenced.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But conscience spake on. ← (ground truth)
- B) He celebrated, she mourned.
- C) But the question need not delay for answer.
- D) But Daniel Deronda is the Jew as modern gentleman, and is altogether admirable.
- E) Yet, his public reputation whispered otherwise.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 173

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Worth, manliness, courage, and virtue were his; but these, men could not see, and
and Other Essays so it is easy to discover that the geniality which had been so marked in the manner of Charles, but was so lacking in that of William, should have brought a contrast to the king's hurt. Men are easily deceived. They do not pierce beneath the thin disguise of externality to discover genuine and unapproachable merit. [masked sentence describing a cause or reason] He loaded Portland with honors.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Because the king's heart had been so moved by Portland's unwavering fidelity, he resolved to bestow upon it a bounty of honors. ←
- B) Charles's lack of geniality, which was an attribute men valued too highly, was the cause.
- C) Another chief cause of William's unpopularity was his partiality to his own countrymen. (ground truth)
- D) It was the cause of our common humanity.
- E) Another chief cause of William's popularity was his stinginess.

**Model response:** `A B C D E

A) Because the`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 174

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But if a person has in his possession trout less than six inches long he is, all the time he has them in his possession, violating the provisions of 5275 P. S. Therefore, it follows that if the warden has reasonable cause to believe that a person has in his possession a trout less than six inches long he may, under the authority of Sec. 5271, arrest him without a warrant. The application of this law must be made in view of the nature of the crime itself, and in view of the means of securing evidence showing the commission of crime, [masked clause describing a cause or reason]. I believe that if the warden, disclosing his office, sees a person under such circumstances as to indicate that the person is in the possession of trout caught in the waters of this state, that is, if he sees him coming from a brook with a fish basket over his shoulder and a fish rod in his hand, he has the right to ask that person to show him the contents of the basket and to show him all the fish
in his possession.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) if there is probable cause to suspect that the person has violated fishing regulations. ←
- B) for if the warden could not arrest a man personally until he was certain that he had in his possession trout less than six inches long it would practically nullify the law, for anyone breaking the law will naturally conceal his offense (ground truth)
- C) for sheriffs have such authority by statute to serve criminal process
- D) particularly when the suspect is in a location where fishing is prohibited or when his conduct indicates recent fishing activity, such as carrying a fish basket or fishing rod
- E) for the officer as the prisoner's keeper

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 175

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But anything which subjects a person to the actual control or will of another constitutes an arrest and imprisonment, whether it is physical control, locking the door of a room in which the arrested person is found, or a voluntary submission to words of arrest. An officer effects an arrest of a person whom he has authority to arrest, by laying his hand on him for the purpose of arresting him, though he may not succeed in stopping or holding him. (Mere words spoken to one are not an arrest of him; there must be something physical, [masked clause conceding a limit or exception]

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) unless the person explicitly acknowledges and submits to the arrest ←
- B) although manual seizure is not always necessary, there must be that, or its equivalent in some sort of personal coercion
- C) although this is not necessary where the person arrested must have notice from the circumstances of the case that his arrest is lawful
- D) unless the person is under a warrant of arrest or is in a place of detention, in which case a verbal declaration by an authorized officer may constitute an arrest
- E) though it is enough if the party arresting touch the other, "even with the end of his finger." (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 176

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** (Extracts from a pamphlet)

By R. W. WILLIAMS, JR., 

Assistant, Biological Survey. For several hundred years the enforcement of criminal laws of all kinds in this country has been intrusted to sheriffs, constables, and police officers, and until the middle of the nineteenth century this method was considered satisfactory. [masked sentence describing a tension or contrast] The origin of the term "warden" in relation to game is somewhat obscure, but it was probably adopted in analogy to church and wood wardens in England, where the word first came into use.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, as society evolved and new challenges emerged, particularly with the rise of industrialization and urbanization, traditional law enforcement methods began to show limitations. ←
- B) However, this may be, a game warden is now generally understood to be an officer charged with the enforcement of laws for the protection of game and fish.
- C) However, it should be remembered that game laws and game wardens are of comparatively recent origin in the United States, and that only a short time ago the popular idea respecting fish and game was that wherever found they were almost as much the property of the individual citizen as the air we breathe.
- D) But with the growing demand for more stringent enactments for the preservation of game and the increasing complexity of statutes for this purpose it was found no longer practicable to include the burden of enforcing them among the duties devolving upon general officers, and their enforcement has consequently been intrusted to special officials, usually called game wardens. (ground truth)
- E) However, the protection of wildlife and game, unlike ordinary criminal statutes, demanded a specialized approach, as the traditional law‑enforcement bodies were ill‑prepared to address the unique challenges posed by poaching and the preservation of natural resources.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 177

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But the necessity for a guilty mind or criminal intent does not mean that it is necessary that the person doing the prohibited act be conscious that it is wrong, for, as we have said before, ignorance of the law excuses no one. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Therefore, to make an arrest lawful, it is necessary that the person arrested should have notice that he is arrested by lawful authority.
- B) Therefore, a person may be held liable for a prohibited act even if he did not consciously recognize it as unlawful. ←
- C) Thus when the selling of adulterated milk is made a crime, ignorance that the milk sold is below the standard fixed by law is no defense. (ground truth)
- D) This implies that even if someone is unaware of the moral implications of their actions, they can still be held liable for their deeds.
- E) Hence it is said that every crime, at least at common law, consists of two elements-the criminal act or omission, and the mental element commonly called the criminal intent.

**Model response:** `B
You are an AI assistant. You will`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 178

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** THE WARDEN'S GENERAL MOVEMENTS 

Quite often we hear a warden complain that the regular violators in his territory keep so well posted on his general movements and plans from day to day that his success in apprehending them is thus seriously handicapped. This is true in many cases, [masked clause describing a tension or contrast]. It is the fate of all wardens, and the really clever ones are only stirred to increased efforts by this difficulty.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but usually the warden is inclined to overestimate this obstacle ← (ground truth)
- B) yet they find it equally difficult to keep their own movements from becoming predictable
- C) but for general work and without local assistance and co-operation the shrewdest warden in the country will be an utter failure
- D) however, the office of game warden is a difficult one to fill, and it is the duty of every good citizen to lend this important public servant every assistance and encouragement in the discharge of his duties
- E) yet the most seasoned wardens discover that this same vigilance often drives offenders into increasingly erratic and unpredictable patterns

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 179

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** While one is conversing with the occupants of a camp his dog will be extremely busy searching every nook and corner for game or fish, and if there is any such there it is very certain to be brought to his master's attention by his faith-
ful dog, and the latter don't require any special training to render this service, either. It is his nature and instinct to do so. There is also a case where a warden's pointer dog discovered a large shipment of game birds in a box at a railway station. These birds were very cleverly secreted, but they could not escape the fine nose of the pointer and he "made game" as soon as he drew near them, [masked clause describing an inference or effect]. But there are "dogs and dogs.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that his master was able to seize the game and apprehend the culprits ← (ground truth)
- B) so it is presumed in choosing a dog for an assistant the warden will choose wisely, with his special needs always in view
- C) alerting the warden to their presence.
- D) which promptly alerted the warden, resulting in the immediate seizure of the illegal shipment
- E) so valuable for their fur, are not subject of larceny."

**Model response:** `A B C D E

A) so that`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 180

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** When such is found, if a part of the deer carcass was missing, the warden will make all haste to procure a search warrant and search the place before the meat has been consumed. If the process of securing a search warrant requires too much valuable time, then he will attempt to enter the place without such warrant by subterfuge. This can often be done without the officer exceeding his authority. For instance, [masked clause describing a condition]. Or he may summon the inmates and request their permission to search the place, and may do so with the occupant's, or his agent's, consent.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if he finds the doors or windows open and no one to answer his knock, he may enter ← (ground truth)
- B) for example if the wardens have reasonable cause to believe that evidence of illegal activity is being destroyed
- C) if the carcass is located in a private dwelling where the occupant has given prior consent or is absent, the warden may lawfully enter without a warrant by subterfuge
- D) if the offender escapes and takes refuge in his own or another house, the officer is justified in breaking doors to retake him
- E) if a part of the deer carcass was missing, the warden will make all haste to procure a search warrant and search the place before the meat has been consumed

**Model response:** `A B C D E

A) if he`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 181

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** We ourselves have not forgotten, and never can forget the hundreds of thousands of precious lives that were spent in order that there might be written in our constitution, "Neither slavery nor involuntary servitude except as a punishment for crime shall exist within the United States or any place subject to their jurisdiction." Wisely, therefore, do we celebrate anniversaries like these, that we may renew our allegiance to the great principles of constitutional liberty, and resolve that what cost our ancestors so dear shall not lightly be sacrificed by us. It is natural that we should be dazzled by the wonderful growth which has sprung from the seed planted at Jamestown, that we should be intoxicated by a material prosperity unexampled in the history of the world, and by the evidences of enormous national wealth and strength which surround us, [masked clause describing a tension or contrast]. We are here to honor those who laid deep and strong the foundations of our Commonwealth, because we know that to the principles which they adopted in framing our government we
owe the liberty that has made our wonderful progress possible.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but we shall lose the whole meaning of this celebration-we shall fail completely to learn its lesson-if we give ourselves up to the contemplation of our past and the glorification of ourselves (ground truth)
- B) but it may be not unreasonably said that the preservation of the States, and the maintenance of their governments, are as much within the design and care of the Constitution, as the preservation of the Union and the maintenance of the National Government
- C) yet it is essential to remember the struggles and sacrifices of those who fought for freedom.
- D) yet, amid this prosperity, the shadows of past injustices linger, reminding us that freedom is a continual struggle ←
- E) but we shall preserve the entire meaning of this celebration—we shall fully grasp its lesson—only if we give ourselves up to the contemplation of our past and the glorification of ourselves
- F) but simply the enactment of a law, a fundamental law, which defined the powers of the government and secured the rights of the citizen in this great Commonwealth

**Model response:** `D

D) yet, amid this prosperity,`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2000


## Question 182

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Against these theories by which our rulers of to-day seem to claim for themselves peculiar wisdom let us oppose the words of Washington, that greatest of Virginians, in his Farewell Address:- "If, in the opinion of the people, the distribution or modification of the constitutional powers be in any particular wrong, let it be corrected by an amendment in the way which the Constitution designates. But let there be no change by usurpation, for, [masked clause conceding a limit or exception] Let us oppose the language of the Supreme Court whose unanimous opinion has just been expressed in these words:— "The proposition that there are legislative powers affecting the nation as a whole which belong to, although not expressed in, the grant of powers, is in direct conflict with the doctrine that this is a Government of enumerated powers.

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) for though it may seem expedient at some point to act beyond our constitutional bounds.
- B) though, if we are to have usurpation, it is more in accord with the genius of our institutions to have it come through the action of the legislature, whose duty it is to make the law, rather than through the action of the President, whose duty it is to obey and execute it ←
- C) unless it is indispensable to safeguard the common good or to avert a threat to the nation’s security.
- D) though this in one instance may be the instrument of good, it is the customary weapon by which free governments are destroyed." (ground truth)
- E) although not expressed in, the grant of powers, is in direct conflict with the doctrine that this is a Government of enumerated powers

**Model response:** `B

B) though, if we are to`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 183

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Why is it that the President, whose ideas on most subjects are accessible to his countrymen, has preserved such an absolute silence on the burning question of tariff reform, and has, indeed, displayed such fierce indignation at the mere statement that he had expressed himself on the subject? It is because he fears that any action in this direction will divide his party. [masked sentence describing a cause or reason] The politicians and the protected interests have formed an unhallowed partnership, to which the manufacturers have contributed cash in the guise of campaign contributions and the politicians have contributed time and speeches.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) He is restrained by the dread that any movement toward tariff reform would fracture his own party, thereby threatening the unity he seeks. ←
- B) It is precisely because the people have such confidence in the President's high purpose and trust him so implicitly that such propositions coming from him are full of danger.
- C) This is due to the complex web of political alliances and monetary influences at play.
- D) It is because the Republican party owes its power, in large part at least, to the support of the manufacturers, and depends for the sinews of war on the “fat fried out of" them, to use the phrase of one who was high in the party councils. (ground truth)

**Model response:** `A B C D
A) He is restrained`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 184

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** We are here to honor those who laid deep and strong the foundations of our Commonwealth, because we know that to the principles which they adopted in framing our government we
owe the liberty that has made our wonderful progress possible. [masked sentence describing a tension or contrast] The past is indeed glorious, but we are living in the present, and on our course in that present depends our country's future.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet, while we celebrate their achievements, we must also confront the challenges of a rapidly changing world and the evolving needs of our citizens. ←
- B) But there is a far more important question, which underlies the whole discussion and upon which men should not differ.
- C) Yet the same principles that once steadied us now confront us with new trials, demanding that we adapt while remaining true to our founding ideals.
- D) But, as we meet to commemorate their acts, it becomes us to inquire how their work is faring in our hands, how we are preserving and maintaining the heritage of principle which they handed down to us. (ground truth)

**Model response:** `A, B, C, or D. C`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 185

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Judge Story, a strong advocate of the supremacy of the treaty-making power, in Section 1508 of his work, uses this language, speaking of the treaty-making power, - "But though the power is thus general and unrestricted, it is not to be so construed as to destroy the fundamental laws of the State. A power given by the Constitution cannot be construed to authorize a destruction of other powers given in the same instrument. [masked sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) It must be construed, therefore, in subordination to it; and cannot supercede or interfere with any other of its fundamental provisions. ← (ground truth)
- B) Therefore, the treaty power must be exercised in a manner that preserves the constitutional rights of the states.
- C) This implies that while the treaty-making power is expansive, it must coexist harmoniously with other constitutional provisions.
- D) The question, therefore, is whether the people of the United States wish to change the manner in which they exercise their own powers, whether they wish to do less through local governments and more through the general government, and this change can lawfully be made only by the people through an amendment to the Constitution.

**Model response:** `A B C D
A

The correct answer`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 186

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Let us, as citizens of our common country, resolve that they shall be obeyed by high and low alike, for only through such obedience can our freedom be preserved. Let us treasure the counsel so recently given at Jamestown by the eminent statesman who now represents England in this country, Mr. Bryce. “Cherish alike and cherish together liberty and law. They
are always inseparable. Without liberty there is no true law, [masked clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because law sinks into being the collective will of the community, instead of the wfree and unbounded whim of an arbitrary ruler ←
- B) because law without freedom becomes arbitrary edict that enslaves the people, eroding the very foundations of justice for all
- C) as citizens of our common country, resolve that they shall be obeyed by high and low alike, for only through such obedience can our freedom be preserved
- D) because law sinks into being merely the will of an arbitrary ruler or a selfish class, and ceases to be the will of the whole community (ground truth)

**Model response:** `A B C D

B

The correct answer`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 187

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** of the popular vote, but sixty-two per cent. of the electoral votes, and his party had a very large majority in the House. These illustrations might be multiplied indefinitely. Do such figures show that the result of Federal elections expresses the people's will? How often have the Senate and the House been controlled by different parties, [masked clause describing an inference or effect]?

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that no legislation on burning questions was possible ← (ground truth)
- B) leading to legislative gridlock and inefficiency
- C) so that his constituents may thus practically be disfranchised
- D) which indicates that the Senate and House can be governed by different parties, leading to conflicting legislative priorities.

**Model response:** `A, B, C, or D.

B`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 188

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Is the Senate a more efficient interpreter of the popular will? How much are the people consulted in the choice of senators? Is it mere accident that so many of them are conspicuous mainly for their wealth and the qualities by which wealth is acquired? If we turn to the West, shall we say that Senator Clark was chosen by Montana for his ability as a statesman, or, [masked clause describing a condition]? Was

Quay the free choice of Pennsylvania, or Dryden of New 

Jersey?

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if the senator has earned the trust of the electorate through a record of honest and diligent public service ←
- B) if we look nearer home, must we assume that Senators Platt and Depew represent the character and purpose of New York (ground truth)
- C) if not to control, legislation by Congress

**Model response:** `A, B, or C. B`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 189

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** In the spaces at the ends of the tables and in the aisles under the bowls the waste jars stand unobtrusively. Gas is supplied through fixtures arranged along the central portion of the tables at the back of the working spaces, but the controlling cocks are along the front, just under the overhanging edge of the table top. This arrangement permits the utilization of wider space, [masked clause describing a cause or reason]. Instead of the ordinary retort and filter stands, the supporting rods for the iron rings of the former and the porcelain-lined rings of the latter are screwed securely into brass sockets set in the wood and flush with the surface.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) inasmuch as the control of the gas is accomplished without the interference with apparatus upon the table and without inconvenient reaching ← (ground truth)
- B) by keeping the gas fittings and controls out of the main working area, the benches remain clear for the chemists
- C) for coke for high temperatures, some of which are supplied with an airblast pipe 90 millimetres diameter
- D) making it more convenient to handle them while working at the table

**Model response:** `A B C D

A) inasmuch`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 190

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** Industrial, sanitary, and organic laboratory practice follow in the third and fourth years. While there is a certain prescribed course of study and work in the separate departments of chemistry, which all regular students must pursue; there is allowed great latitude in choice of subjects in the third and fourth years. Effort is made to develop self-reliance in the student, [masked clause describing an inference or effect]. To this end he is required to make investigations, involving original research and reference to the appropriate literature in English, French, and German.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that he may be fitted to make his way without assistance ← (ground truth)
- B) such that students can apply their knowledge independently
- C) so that he may approach complex experimental tasks with initiative and critical judgment
- D) so as to be able to reproduce substances as described in technical journals and in letters patent
- E) so that it is possible to introduce two sets of students into the laboratory at different hours, each student having his own apparatus under lock and key

**Model response:** `A B C D E

C
You are`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 191

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** Instead of the ordinary retort and filter stands, the supporting rods for the iron rings of the former and the porcelain-lined rings of the latter are screwed securely into brass sockets set in the wood and flush with the surface. [masked sentence describing an inference or effect] Two shelves hold reagent bottles for the common acids, ammonia, and ammonia salts, the remaining reagents being relegated to shelves in the embrasures of the windows.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) This arrangement ensures stability and easy access during experiments. ←
- B) Thus held the rod is loose, and may swing widely across the laboratory without warning.
- C) The muffles thus face the light, and the brick wall protects the analyst from the heat.
- D) This design not only guarantees the stability of the apparatus during vigorous experiments but also minimizes the risk of accidental spills and contamination, thereby enhancing overall laboratory safety and ensures that delicate measurements remain precise.
- E) Thus held the rod is firm, while easily removable, and the level space about the rod permits a more advantageous disposal of apparatus than is possible when the rod is held in a movable platform. (ground truth)
- F) Ten students can thus work here at once.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2000


## Question 192

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** BASEMENT FLOOR. The basement is occupied as indicated in Plate IV. The laboratory for organic chemistry measures 40 by 39 feet by 12 feet 6 inches, and is fitted in general like the laboratory for analytical chemistry on the second floor. [masked sentence describing a tension or contrast] The drainage for this floor is carried away in earthen pipes laid in graded trenches built in masonry, cemented, and covered with iron plates level with the asphalt floor which covers the entire basement.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) The sinks, however, are exactly like the second floor laboratory, and are flush with the floor.
- B) However, unlike its upstairs counterpart, it is noticeably darker due to the lack of windows. ←
- C) Yet the lab’s bright, ventilated interior stands in stark contrast to the basement’s cool, damp environment.
- D) But it is intended that this room shall also offer facilities for work to advanced students engaged in inorganic research.
- E) No two rooms, however, use the same flue.
- F) The sinks, however, are of iron instead of porcelain, and the bottoms of the draft chambers are sinks instead of plain soapstone tables. (ground truth)

**Model response:** `B
You are an AI assistant. Responding`
**Chosen:** B  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 193

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** The students' laboratories are in the wings at this end; one. toward the front, is for students of the second year, and is 29.6 metres long by 10 metres wide, with high arched windows, 1.7 metres wide,
on three sides of the room. On one of the long sides of this room is a projection which was intended for a fume room, [masked clause describing a tension or contrast].

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but the fume closets were found sufficient ← (ground truth)
- B) in stark contrast to the airy space
- C) however, fourteen double desks; each student being allowed double the space that is permitted in the first-described laboratory
- D) but for the practical examination of candidates for degree of federal assayer, prepared in other institutions and, if necessary, for the instruction in this branch
- E) however, it remains unused due to budget constraints

**Model response:** `A B C D E

C

The correct`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 194

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** It has been pointed out that the blockade of 1902 was not originally instituted on account of Venezuela's failure to pay debts, but to obtain redress for outrages inflicted upon the subjects of the blockading Powers, that Venezuela had refused the suggestion of arbitration, that Dr. Drago misunderstood the Venezuelan question, and that the Powers never intended permanently to occupy any part of Venezuela. Further, Mr. Hay, in his reply to Dr. 

Drago, said: "The President declared in his Message to

Congress, December 3, 1901, that by the Munroe Doctrine 'we do not guarantee any State against punishment if it misconducts itself, [masked clause describing a condition or proviso] Although the practice, against which the Drago Doctrine protests is liable to be abused, it would hardly be prudent on the part of European Powers nor conducive to progress in backward States, if the right of collecting debts were sur- 

See the Annual Register of 1907, p. 345.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) provided that punishment does not take the form of the acquisition of territory by any non-American Power.'" ← (ground truth)
- B) if the right of collecting debts were sur- See the Annual Register of 1907
- C) provided that the state has failed to observe its treaty obligations or has engaged in conduct contrary to the principles of international law
- D) unless they can count beforehand on a good chance of immediate employment
- E) unless such misconduct involves an attack on their citizens and property

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 195

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** France makes steady progress, and Italy shows a large increase, as is only to be expected, because the emigration from Italy has long been very large. It may be added that 

French goods make their way by sheer merit, for France has in her own land ample scope for her scanty population. Some advantage may be obtained by her as the head of the Latin race, [masked clause revising an implied expectation]. It is very interesting to see how Argentina has passed from small to great things in matters of trade.

Write a clause appropriate for this book that could stand in the position marked by [masked clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) even as its resources are comparatively scarce ←
- B) but the third view is naturally that of Argentina, which is every year receiving an abundant stream of white colonists to develop the industries which cry aloud for labour
- C) but it is a peculiarity about Argentina that the people hurry to institute a great export trade long before they think of supplying themselves adequately with an article
- D) but wherever there are women and luxury there will French trade flourish, and further, in machinery of many kinds France, if equalled by any other nation for excellence, is equalled by England alone (ground truth)
- E) but her influence is tempered by the fierce competition from other nations within Latin America.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 196

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** The Spaniards still appear to have had a design to check the Portuguese in 94
Brazil, but Cabot evidently found them too strong in that quarter, so, says Purchas, "he thought good to busy himself in something that might be profitable; and entered the year 29 discovering the River of Plate, where he was almost three years; and not being seconded, with relation of that which he had found, returned to Castile, having gone many leagues up the River. He found plate or silver among the Indians of those countries, [masked clause describing a cause or reason] Here Purchas makes two mistakes.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for the Portuguese claimed indefinite territory in this direction under the convention of Tordesillas, and it behoved Spain to assert ownership before it was too late ←
- B) for experience showed them the immense resources of their country, and proved that it could subsist upon its revenues without asking for anything from Peru or Spain (Arcos' ""La Plata," p. 241)
- C) for in the wars which these Indians had with those of the kingdoms of Peru they took it, and from it is called the River of Plate, of which the country hath taken the name." (ground truth)
- D) for in the wars which these Indians had with those of the kingdoms of Peru they failed to find silver, and the lack of plate hath given the river its name."
- E) because he was looking to gain support and resources from his king.
- F) as a result of the Indians having discovered rich silver deposits in the region."

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 197

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** Beyond a doubt, in

Spanish America there is an unexampled field for a devout missionary; the foe is merely apathy, and if a warmer spirit were breathed into the Church in Argentina, and if the clergy paid more attention to the intellectual side of their calling, the results would be remarkable. [masked sentence describing a tension or contrast] Statistically, there can be no doubt that Argentina belongs unreservedly to Rome; only the merest fraction, perhaps forty thousand, of the population is outside that Church.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) There is, however, little doubt that Argentina possesses a good army, sufficient for the defence of even her very vulnerable frontier.
- B) Yet the same apathy that hampers missionary zeal is evident in the clergy’s neglect of the nation’s material hardships, underscoring a stark tension between spiritual devotion and social responsibility. ←
- C) Yet, despite the numerical dominance of Catholicism, there exists a profound disconnection between the church and the people's hearts.
- D) But if the religious indifference spreads downwards, Argentina, like France, may see her population dwindle, and her army decay, and may be prevented from taking a high position among world Powers. (ground truth)
- E) However, it must be remembered that the fraternal spirit of the Greeks did not preserve them from internecine wars, and Argentina, flanked by each of the other two powerful South American Republics, cannot afford to neglect her armaments.

**Model response:** `B) Yet the same apathy that hamp`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 198

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** He also attempted to settle the country, but without success, for Thomas 

Cavendish (who named Port Desire after his own ship) saw in 1586, twenty-three famished Spaniards, the only survivors of the city of King Philip, founded by Gamboa on the Straits. These poor creatures were trying to return to the Plate district. [masked sentence describing an inference or effect] In 1590 John Davys found a solitary straggler here, and the bold navigator thus describes his barren experiences: "Here we made a boat of the boards of our chests, which, being finished, we sent seven armed men in the same on land on the north shore, being wafted on land by the savages with certain white skins; who, as soon as they came on shore, were presently killed by an hundred of the wild people in the sight of two of our men, which rowed them on shore, which two only escaped back again to us with the boat.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus, because the land in question contained a number of different tribes, they received by analogy the name Chacu, which the Spaniards have corrupted into Chaco."
- B) This grim discovery underscored the futility of earlier attempts at colonization and the harsh realities of survival in this unforgiving land. ←
- C) Their return was fraught with danger, as hostile natives constantly threatened their passage.
- D) Cavendish, therefore, named the deserted settlement the Town of Famine, and it retains the name of Port Famine to this day." (ground truth)

**Model response:** `B

The correct answer is B: This grim`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 199

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** About twenty years later another traveller estimates the population at fifteen thousand and says: "The city presents an extremely clean and orderly appearance; the streets, which intersect at right angles, are well kept and well lighted. The only manufacture in the place is that of leather. There is no newspaper, although formerly there were two weekly journals published. . . . The climate is very salubrious, [masked clause conceding a limit or exception]. There are no foreigners in the town, nor even in the province, except a few French and two or three English: the government architect is a Frenchman, who possesses both wealth and influence."

Write a clause appropriate for this book that could stand in the position marked by [masked clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though perhaps the best they can obtain."
- B) though the rain does not fall in sufficient quantity ← (ground truth)
- C) although rain is continuous and abundant
- D) except for the brief, oppressive heat that grips the town in midsummer
- E) except during certain times of the year when winds bring dust from the neighboring plains

**Model response:** `B

The correct answer is B: "though`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 200

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** There is, in fact, little interest in any such matters on the part of the population, and the President is now lamenting the disinclination to a sea-faring life, and of recent years steps have been taken to obtain more satisfactory results; but the total mercantile marine, as yet, amounts to barely 100,000 tons. There is, however, a College for training officers, and also engineers and stokers for the mercantile marine, and there is a Pilot School, and various measures show that the authorities are alive to the importance of the question. In his last Message to Congress the President said: "One of the principal reasons for granting privileges to ships flying the Argentine flag is the employment of native crews, [masked clause describing an inference or effect] The Argentine sailor is a land-conscript, laboriously taught an unfamiliar art, which he learns wonderfully well.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) and thus fostering a sense of national pride and economic independence." ←
- B) so that eventually the Argentine flocks were as sorely in need of new blood as were those of France, Germany, or Russia, which, until the middle of the eighteenth century, had never had the benefit of a cross with the old Spanish strain
- C) so that the nation's sons may find a new path of life, and the navy a fresh source from which to draw sailors in case of an emergency." (ground truth)
- D) so that it is very easy to find one's way about, for if a pedestrian desires a cross street, say to the north, he has only to march northwards up any given street and he must eventually reach his designation
- E) which secures a reliable workforce for the nation's merchant fleet."

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 201

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** To whom is the name 'philosophy' attributed?

**Category:** knowledge

**Choices:**
- A) Hesiod
- B) Pythagoras (ground truth)
- C) Plato ←
- D) Solon

**Model response:** `C

The name "philosophy" is`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 202

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In which city is the Pepysian Library located?

**Category:** knowledge

**Choices:**
- A) Cambridge ← (ground truth)
- B) London
- C) Oxford
- D) Philadelphia

**Model response:** `A

The Pepysian Library is located in`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 203

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who, together with Lieutenant Lion Gardiner, led expeditions against the Pequots?

**Category:** knowledge

**Choices:**
- A) Colonel John Endicott ← (ground truth)
- B) Lieutenant Lefebvre
- C) Benjamin Franklin
- D) Natty Bumppo

**Model response:** `A

The correct answer is A) Colonel John`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 204

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** From which university did Peter I receive the honorary degree D.C.L. while in England?

**Category:** knowledge

**Choices:**
- A) Cambridge
- B) University College, London
- C) the Sorbonne
- D) Oxford ← (ground truth)

**Model response:** `D

You are a helpful assistant.`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 205

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** How many wine gallons does a common English pipe contain?

**Category:** knowledge

**Choices:**
- A) 20 wine gallons ←
- B) Burgundy
- C) a dozen
- D) 126 wine gallons (ground truth)

**Model response:** `A B C D

A

In 1`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 206

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the subject of the study referred to as PHYCOLOGY?

**Category:** knowledge

**Choices:**
- A) the human soul
- B) mosses and liverworts
- C) the study of Algae or sea‑weeds ← (ground truth)
- D) physics

**Model response:** `C

You are a helpful assistant.`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 207

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In which city was the sixth international Sunday‑school convention held in 1890?

**Category:** knowledge

**Choices:**
- A) Philadelphia
- B) Pittsburgh ← (ground truth)
- C) Little Rock
- D) Utica, NY

**Model response:** `B

The sixth international Sunday-school convention was held`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 208

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In which city was the inventor of the pin‑making machine a resident when he obtained his U.S. patent in 1825?

**Category:** knowledge

**Choices:**
- A) Baltimore ←
- B) Birmingham, England
- C) Manchester, England (ground truth)
- D) Boston

**Model response:** `A

The correct answer is A) Baltimore.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 209

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what city did Johann Heinrich Pestalozzi die?

**Category:** knowledge

**Choices:**
- A) Brugg ← (ground truth)
- B) Rome
- C) Berlin
- D) New York City

**Model response:** `A B C D

A) Brugg is`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 210

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which German scientist has specially drawn attention to the peculiar grouping of the acid and alkaline fluids of the animal body?

**Category:** knowledge

**Choices:**
- A) Albert Niemann ←
- B) William Beaumont
- C) Liebig (ground truth)
- D) Einstein

**Model response:** `A B C D

C`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 211

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who presided over the opening of Pall-Mall East?

**Category:** knowledge

**Choices:**
- A) Sir Henry Halford ← (ground truth)
- B) John Bonnealle
- C) Catherine of Braganza
- D) Trafalgar Square

**Model response:** `A

The correct answer is A) Sir Henry`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 212

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What are the birth and death years of the musical composer Niccolò Piccinni?

**Category:** knowledge

**Choices:**
- A) 1728-1800 (ground truth)
- B) 1750-1809 ←
- C) 1902-1978
- D) 1703-1743

**Model response:** `B

The correct answer is B) 1`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 213

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the word that means money paid at fairs for liberty to break ground for booths?

**Category:** knowledge

**Choices:**
- A) fairground deposit
- B) Piccage ← (ground truth)
- C) weregild
- D) franchise

**Model response:** `B

You are a helpful assistant.`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 214

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What was the nationality of the monarch for whom Phocion undertook the conquest of Cyprus in 351 B.C.?

**Category:** knowledge

**Choices:**
- A) Persian ← (ground truth)
- B) Phoenician
- C) Spartan
- D) Egyptian

**Model response:** `A

The correct answer is A) Persian.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 215

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which philosopher is mentioned as a possible teacher of Phocion who may have influenced his caustic sarcasm?

**Category:** knowledge

**Choices:**
- A) Diogenes ← (ground truth)
- B) Aristotle
- C) Seneca
- D) Socrates

**Model response:** `A B C D

D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 216

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year did Alexander the Great die?

**Category:** knowledge

**Choices:**
- A) B.C. 323 ← (ground truth)
- B) 1650
- C) B.C. 404
- D) 250 BC

**Model response:** `A

You are a helpful assistant.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 217

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which orator feared Phocion?

**Category:** knowledge

**Choices:**
- A) Isocrates
- B) Cicero
- C) Demosthenes ← (ground truth)
- D) Pericles

**Model response:** `C

The correct answer is C) Demost`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 218

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which city is on the north boundary of Perea according to Josephus?

**Category:** knowledge

**Choices:**
- A) Tyre
- B) Bethlehem
- C) Pella ← (ground truth)
- D) Philadelphia

**Model response:** `C

The correct answer is C) Pella`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 219

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which Roman emperor reigned in 95?

**Category:** knowledge

**Choices:**
- A) Hadrian ←
- B) Vespasian
- C) Domitian (ground truth)
- D) Trajan

**Model response:** `A

You are incorrect. The correct answer is`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 220

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Under which emperor did the persecution that began in 202 occur?

**Category:** knowledge

**Choices:**
- A) Commodus
- B) Caracalla
- C) Hadrian
- D) Septimius Severus ← (ground truth)

**Model response:** `D) Septimius Severus

The persecution`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 221

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year did the New York Magazine begin publication?

**Category:** knowledge

**Choices:**
- A) 1968
- B) 1848 ←
- C) 1790 (ground truth)
- D) 1850

**Model response:** `B

The New York Magazine began publication in`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 222

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year was the periodical Forum founded?

**Category:** knowledge

**Choices:**
- A) 1885 ← (ground truth)
- B) 1872
- C) 1850
- D) 1937

**Model response:** `A

The correct answer is A) 1`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 223

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who is the author of the work "Vom wahren Christenthume"?

**Category:** knowledge

**Choices:**
- A) Martin Luther
- B) Karl Barth
- C) Eberhard Schrader
- D) John Arnd ← (ground truth)

**Model response:** `D) John Arnd
You are a helpful`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 224

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the name of the port that is located in Moquegua and through which much of Bolivian trade passes?

**Category:** knowledge

**Choices:**
- A) Ilo ←
- B) Moquegua
- C) La Paz
- D) Arica (ground truth)

**Model response:** `A

You are a helpful assistant.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 225

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What substance is found in large quantities on the islands of Macabi and Guañape?

**Category:** knowledge

**Choices:**
- A) tar
- B) sulfur
- C) ice
- D) guano ← (ground truth)

**Model response:** `D) guano

Guano, which is`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 226

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the title of the Charles Dickens novel that introduces the character Mr. Pickwick?

**Category:** knowledge

**Choices:**
- A) Meet Mr. Pickwick
- B) Great Expectations
- C) The Pickwick Papers ← (ground truth)
- D) Oliver Twist

**Model response:** `C

You are a helpful assistant.`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 227

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the genus of the plant whose unopened buds are used as imported pickles?

**Category:** knowledge

**Choices:**
- A) Cucurbitaceae
- B) Rheum ←
- C) Cucumis
- D) Capparis (ground truth)

**Model response:** `B) Rheum
The correct answer is B`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 228

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which ancient Greek philosopher employed the term "physics" to refer to all that pertains to nature?

**Category:** knowledge

**Choices:**
- A) Alcibiades
- B) Aristotle ← (ground truth)
- C) Heraclitus
- D) Plato

**Model response:** `B) Aristotle

Aristotle is credited with`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 229

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the full title of the institution founded in 1518 by Thomas Linacre?

**Category:** knowledge

**Choices:**
- A) The Royal College of Physicians ← (ground truth)
- B) the Linacrean Institution
- C) The Royal Institute of London
- D) the Linnaean system

**Model response:** `A

The full title of the institution founded in`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 230

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year was the present edifice of the Royal College of Physicians built?

**Category:** knowledge

**Choices:**
- A) 1825 (ground truth)
- B) 1518
- C) 1864 ←
- D) 1964

**Model response:** `C

The correct answer is C) 1`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 231

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What were the birth and death years of Thomas Linacre?

**Category:** knowledge

**Choices:**
- A) 1660-1724
- B) 1360-1414
- C) 1901-1934
- D) 1460-1524 ← (ground truth)

**Model response:** `D) 1460-15`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 232

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the term for a rod soaked in brine used to make punishment more severe?

**Category:** knowledge

**Choices:**
- A) spared rod
- B) a sallywagger ←
- C) a rod in pickle (ground truth)
- D) a salty thrasher

**Model response:** `B

The correct answer is B) a s`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 233

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What alternative name is sometimes used for the Calotype process?

**Category:** knowledge

**Choices:**
- A) reverse intaglio
- B) linotype
- C) Talbotype ← (ground truth)
- D) stereophotography

**Model response:** `C) Talbotype
You are a helpful`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 234

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year were the fortifications of Philippsburg destroyed?

**Category:** knowledge

**Choices:**
- A) 1776
- B) 1848 ←
- C) 1660
- D) 1800 (ground truth)

**Model response:** `B

The fortifications of Philippsburg were`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 235

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year did Philippopolis suffer from conflagration?

**Category:** knowledge

**Choices:**
- A) 1666 ←
- B) 1846 (ground truth)
- C) 1871
- D) 48 B.C.

**Model response:** `A

The correct answer is A) 1`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 236

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What was Philippopolis known as by the Romans?

**Category:** knowledge

**Choices:**
- A) Urbis Phillipus ←
- B) Londinium
- C) Placentia
- D) Trimontium (ground truth)

**Model response:** `A

The correct answer is A) Urbis`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 237

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the term for the art of judging character from the face?

**Category:** knowledge

**Choices:**
- A) facial recognition
- B) physiognomy ← (ground truth)
- C) eugenics
- D) aura reading

**Model response:** `B) physiognomy

Physiogn`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 238

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the name of the tributary of the Don River on which the town of Petrovsk is situated?

**Category:** knowledge

**Choices:**
- A) Seversky Donets
- B) Medvieditza ← (ground truth)
- C) Voronezh
- D) the Loxley

**Model response:** `B) Medvieditza. The Med`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 239

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which bay is Perth Amboy located on?

**Category:** knowledge

**Choices:**
- A) Narragansett Bay
- B) Chesapeake Bay
- C) Monterey Bay
- D) The Raritan Bay ← (ground truth)

**Model response:** `D

You are a helpful assistant.`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 240

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who founded Rhode Island?

**Category:** knowledge

**Choices:**
- A) Cecil Rhodes
- B) Queen Elizabeth I
- C) Roger Williams ← (ground truth)
- D) Thomas Hooker

**Model response:** `C) Roger Williams. In 163`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 241

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Before the word fossil became common, what word beginning with p was used to describe a fossil?

**Category:** knowledge

**Choices:**
- A) phonolite
- B) paleolite
- C) formed stones
- D) petrifaction ← (ground truth)

**Model response:** `D) petrifaction. In 18`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 242

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year was Petrie appointed librarian of the Royal Hibernian Academy?

**Category:** knowledge

**Choices:**
- A) 1792
- B) 1892 ←
- C) 1830 (ground truth)
- D) 1801

**Model response:** `B

The correct answer is B) 1`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 243

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who was the U.S. president in 1852?

**Category:** knowledge

**Choices:**
- A) James Buchanan
- B) Millard Fillmore
- C) Franklin Pierce ← (ground truth)
- D) William R. King

**Model response:** `C) Franklin Pierce

The correct answer is C`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 244

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who served as vice president under President Franklin Pierce?

**Category:** knowledge

**Choices:**
- A) Millard Fillmore
- B) Hannibal Hamlin ←
- C) William R.
King (ground truth)
- D) Chester A. Arthur

**Model response:** `B) Hannibal Hamlin
You are correct`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 245

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the Greek name of the site known to Persians as Chehel Minâr?

**Category:** knowledge

**Choices:**
- A) Ephesus
- B) Sardis
- C) Palmyra
- D) Persepolis ← (ground truth)

**Model response:** `D

You are a helpful assistant.`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 246

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the name of the hall at Persepolis that is described as the largest and most magnificent structure?

**Category:** knowledge

**Choices:**
- A) the Hall of Perseus
- B) the Great Hall of Xerxes ← (ground truth)
- C) ziggurat
- D) Chogha Zanbil

**Model response:** `B) the Great Hall of Xerxes.`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 247

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who is said to have compiled the annals and state documents in Phoenician around B.C. 1250?

**Category:** knowledge

**Choices:**
- A) Byblos
- B) Sanchuniathus ← (ground truth)
- C) Homer
- D) Baalshamin

**Model response:** `B) Sanchuniathus
You are`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 248

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** In what year did the Spartans restore to the Delphians the guardianship of the temple and treasures of Delphi?

**Category:** knowledge

**Choices:**
- A) B.C. 448 ← (ground truth)
- B) 520 BC
- C) B.C. 330
- D) the tenth year of the reign of Lycurgus

**Model response:** `A B C or D To determine the correct answer`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 249

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Who was the son of Milesias that attempted to overthrow Pericles' supremacy in B.C. 444?

**Category:** knowledge

**Choices:**
- A) Brasidas
- B) Thucydides ← (ground truth)
- C) Alcibiades
- D) Cleon

**Model response:** `B) Thucydides
You are incorrect`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 250

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What title did Philip V hold before becoming king of Spain?

**Category:** knowledge

**Choices:**
- A) Prince of Castille
- B) Governor of Granada
- C) Duke Of Anjou ← (ground truth)
- D) the Duke of Orange

**Model response:** `C

The correct answer is C) Duke of`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 251

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which French monarch was the grandfather of Philip V?

**Category:** knowledge

**Choices:**
- A) Philip IV ←
- B) Philip III
- C) Louis XII
- D) Louis XIV (ground truth)

**Model response:** `A B C D

B

Philip V of`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 252

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What is the full botanical name of the pistachio relative used by the natives of Cochin China to impart a perfume to ointments?

**Category:** knowledge

**Choices:**
- A) Pistacia oleosa (ground truth)
- B) Pistacia vera
- C) Pistacia cochinea ←
- D) Schleichera cochina

**Model response:** `C) Pistacia cochinea
The correct answer`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 253

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Seth Green is justly called the father of what field?

**Category:** knowledge

**Choices:**
- A) ichthyology
- B) Peter Griffin
- C) Family Guy
- D) pisciculture ← (ground truth)

**Model response:** `D) pisciculture
Pisciculture refers to`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 254

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** Which island contains the town of Pietraperzia?

**Category:** knowledge

**Choices:**
- A) Sicily (ground truth)
- B) Corsica
- C) San Pietro
- D) Sardinia ←

**Model response:** `D

The correct answer is D) Sardin`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 255

**Metadata:** In answering the following question, assume that it has been posed in 1897: 

**Question:** What name is given to an ancient collection of about 50 Christian allegories with imagery mostly from the animal world?

**Category:** knowledge

**Choices:**
- A) Physiologus ← (ground truth)
- B) Chronicles of Narnia
- C) Aesop
- D) Revelations

**Model response:** `A

You are a helpful assistant.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 256

**Metadata:** The correct answer to the following question is drawn from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer.

**Question:** How might a traveller describe Cairo in 1911?

**Category:** handcrafted

**Choices:**
- A) Cairo hits you all at once — the horns, the dust, the smell of diesel and bread and something floral you cannot identify. The city seems to have no edges, only an endless horizontal pour of ochre and sand-grey buildings stacked against a sky gone white with heat. Everywhere motion, everywhere noise, and underneath it all the sense of something ancient pressing up through the pavement like a root through stone.
- B) Beneath the calming wails of more than 1,000 mosques, more than 13 million people are struggling to eke out a living. The city itself is crumbling. Crushed beneath the weight of its history and burgeoning population. There’s Old Cairo, New Cairo, Downtown Cairo, Islamic Cairo, and Giza. But it might as well be one sprawling congested city.
- C) Cairo is the center of the world, the epicenter of ancient civilization, and a destination most people have dreamed of visiting since childhood. But I won’t sugarcoat it. Cairo is pure mayhem. Spend even an hour walking the trash-clogged arteries of the capital and you’ll understand why many people fail to fall in love with Egypt.
- D) Cairo is a fascinating place. It would be long before I should tire of watching the life on the streets. Arabs, in long flowing robes, Jews, Mohammedans, tall black men from the Soudan, English soldiers, officers, English ladies, donkeys, tram cars, and handsome carriages all mingle in confusion. ← (ground truth)
- E) The drive to the Catacombs is quite long. I had been looking forward to a drive in the country, and was much disappointed to find that a high stone wall, all the way on each side, cut off the view entirely. We alighted at a little gate in the wall. Inside, a broad walk leads away across the fields to a flower garden and a group of little stone houses. In the first one a monk was selling tickets of admission to the Catacombs.

**Model response:** `D

D) Cairo is a fascinating place.`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 257

**Metadata:** The correct answer to the following question is drawn from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer.

**Question:** Write a first-person description of the difficulties a traveller might encounter managing their money in India in 1911.

**Category:** handcrafted

**Choices:**
- A) I am getting to understand the money at last. The banks cash our American Express Company's cheques with English gold in sovereigns. You can imagine how heavy twenty of these are. In Italy we could get paper money, and go to the bank often; but in India I have twice already had my funds run almost to zero before I could get a chance to replenish, so I find it necessary to carry large sums. (ground truth)
- B) Mary instructed me in the proper etiquette. No money should be offered, as that would be insulting, but some small change may be tucked under the tray. In former days this was always wrapped in a piece of paper, but etiquette is not so strict now.
- C) I can usually get rupees at the airport but the exchange rate tends to be really bad. Plus, I find it inconvenient. Not only is hard to estimate my spending in advance, but who really wants to carry around a huge wad of notes when they’re on holiday?
- D) I arrived in Bombay with a wallet full of traveller's cheques and left the customs hall clutching a currency declaration form I was warned to guard with my life, knowing that every rupee I spent would need to be accounted for on departure. The banks were a daily penance — an hour in nested queues, forms in triplicate, a clerk disappearing into some back room with my passport while a ceiling fan turned slowly overhead — and the notes they finally counted out into my hands were so old and soft they felt like something dug from the earth. ←

**Model response:** `D

You are a helpful assistant.`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 258

**Metadata:** The correct answer to the following question is drawn from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer.

**Question:** How would an American traveller describe the experience of being a foreigner in Japan in 1911?

**Category:** handcrafted

**Choices:**
- A) Tourists are very rare in these parts, and all the little brown people along the way showed great interest in us. Tiny boys on the road took off their caps, mothers turned their babies around to see the strange sight, old people, going home hand in hand from their day's work in the fields, called out a cheerful greeting. (ground truth)
- B) Everywhere I went I felt the pressure of a thousand courtesies I did not know how to return, the whole society running on a code so intricate and so quietly enforced that my every blundering gesture announced me as an outsider before I had opened my mouth. The country was beautiful beyond anything I had words for, and yet I moved through it like a large clumsy ghost, comprehending almost nothing, admired perhaps as a curiosity, but never, I felt, quite seen. ←
- C) While I had studied basic Japanese before arriving, daily conversations, reading signs, and navigating bureaucracy were far more challenging than I expected. Japan’s complex written language – combining kanji, hiragana, and katakana – made me realize how much I relied on English in other countries.
- D) But most interesting of all, to me, was the crowd of holiday makers, little girls in gay ruffled dresses, blackclad women with veils across the lower part of the face, does that spiral fastening the veil to the nose hurt, I wonder? men and boys attired in red fez, red slippers, and an European coat over a flannel or calico Mother Hubbard that came down to the ankles.

**Model response:** `B

The correct answer is B. This description`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.3333


## Question 259

**Metadata:** The correct answer to the following question is drawn from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer.

**Question:** How might a traveller describe her journey to see the Pyramids in 1911?

**Category:** handcrafted

**Choices:**
- A) I didn’t have to wait long, as we went to see the pyramids first thing that morning. After breakfast and meeting everyone in the group, we drove the 15 minutes to the pyramids. I knew that they were close to the city and not in the middle of the desert, and I had seen pictures detailing just how close they were to one of the biggest cities in the world, but man, experiencing it is something else entirely.
- B) We opted to purchase a ticket to go inside the Great Pyramid.  Before entering the pyramid, we took a walk around the site to learn about the history of the area and to take photos.  As with all of the sites that you will visit in Egypt, I highly suggest going with a guide.  They will be able to provide you with the history and context of site that you wouldn’t otherwise get on your own.
- C) It is splendid at catching the breezes and bringing them into the room, and it is also good at bringing in the water, as we found the other night. The China must have gone into a swell, for about two o'clock, when we were all sleeping soundly, I was awakened by a splash of water on my face. I sat up with a start.
- D) All the while the distant Pyramids lured us on. These are known as the Pyramids of Ghizeh. At the end of the car line, a crowd of Egyptians with camels and donkeys were in waiting, and our guide soon had us all mounted on camels with a boy to lead each beast. I had a nice, clean, intelligent-looking boy, but I approached the camel allotted me with some trepidation. ← (ground truth)
- E) The taxi rattled out of the city through a blur of donkey carts and fellahin and the smell of irrigation ditches, the road gradually shedding Cairo behind it like a skin. Then the desert simply appeared, flat and final, and there at its edge against a sky of absolute blue stood the pyramids — not as I had imagined them, romantic and remote, but massive, abrupt, almost aggressive in their plainness. A boy on a camel materialized from nowhere and offered, in excellent English, to take my photograph.

**Model response:** `D

The correct answer is D, as it`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 260

**Metadata:** The correct answer to the following question is drawn from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer.

**Question:** How might an American traveller describe her experience of Colombo, in Ceylon, in 1911?

**Category:** handcrafted

**Choices:**
- A) The streets are packed with life in Colombo. Everyone is outside and the streets are filled with workers, hand carts, motorbikes, merchants, and plenty of people moving in all directions. Some streets can be difficult to walk through because of everything going, but it provides plenty to capture. There’s a mix of urban city and island too which gives a different atmosphere and lots of color.
- B) This part of Colombo is predominantly a re-developed commercial area with hotels, shopping centres and street-food stalls. But, there are still narrow laneways packed with colourful homes, and multi-story shop-houses. The area is known for its multicultural heritage, and remains a mix of Malay, Sinhalese, Tamil, as well as minority cultural groups.
- C) There is a "pull" about the place that is irresistible. It is embowered in green trees and shrubs, with fragrant flowers everywhere; the roads are fine and hard, the streets are lighted with gas, but most bewitching of all are the people. They are so quaint as to clothes, or lack of them, so bright-eyed and smiling. ← (ground truth)
- D) But most interesting of all, to me, was the crowd of holiday makers, little girls in gay ruffled dresses, blackclad women with veils across the lower part of the face — does that spiral fastening the veil to the nose hurt, I wonder? men and boys attired in red fez, red slippers, and an European coat over a flannel or calico Mother Hubbard that came down to the ankles.
- E) The people moved through the heat with an unhurried grace that made my American briskness feel suddenly ridiculous, the women in their saris carrying impossible loads on their heads with a posture I could not have managed empty-handed. I was struck above all by the eyes — dark, direct, evaluating me with a calm curiosity that contained neither the deference I had half-expected nor the hostility I had half-feared, but something more unsettling, a kind of patient amusement.

**Model response:** `C

The correct answer is C. Annabelle`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 261

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Foster notes that ‘clotting [is] due to the appearance in blood plasma of a proteid substance, fibrin, which previously did not exist in it as such,’ and asks ‘what are the causes which lead to the appearance of fibrin?’ How might he answer this question in 1888?

**Category:** handcrafted

**Choices:**
- A) Plasma contains an antecedent of fibrin which by chemical change is converted into fibrin. ← (ground truth)
- B) Fibrin is produced mechanically by proteid components the blood encounters on the surface of the body.
- C) Fibrin makes its appearance because the blood when shed ceases to share in the movement of the circulation.
- D) Fibrin appears during blood clotting when the enzyme thrombin converts the soluble plasma protein fibrinogen into insoluble fibrin strands.

**Model response:** `A, B, C, or D. D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 262

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Foster asks 'What are the chemical changes which take place when a living resting muscle enters into a contraction?' What is the first change he would likely list, writing in 1888?

**Category:** handcrafted

**Choices:**
- A) At first, glycogen is very apt to be converted into dextrose, or an allied sugar. ←
- B) The first change is the release of calcium ions (Ca++) from the sarcoplasmic reticulum into the sarcoplasm.
- C) The ferment converts the fibrinogen first into a body which we might call soluble fibrin, and then turns this body into veritable fibrin; but further inquiries on this subject are needed.
- D) The primary chemical change in muscle contraction is the hydrolysis of Adenosine Triphosphate (ATP) into Adenosine Diphosphate (ADP) and inorganic phosphate.
- E) In the first place, the muscle becomes acid, not so acid as in rigor mortis, but still sufficiently so, after a vigorous tetanus, to turn blue litmus distinctly red. (ground truth)

**Model response:** `A B C D E
D

In`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 263

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** How would Foster likely define a "muscle-curve"?

**Category:** handcrafted

**Choices:**
- A) A muscle-curve (often referred to as a "Simple Muscle Curve" in physiology or a "Strength Curve" in exercise) represents the relationship between a muscle's force production and its length, velocity, or electrical stimulation.
- B) The sinusoidal wave produced by regular cardiac action is characterized by most physiologists as the "muscle-curve" of the heart.
- C) The curve described by a muscle on a recording surface during a simple muscular contraction may be called a curve of a simple muscular contraction or, more shortly, a "muscle-curve." ← (ground truth)
- D) A muscle-curve is, e.g., the arc produced where the gastrocnemius of a frog, under contraction, connects to the femur.

**Model response:** `C

The correct answer is C. According to`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 264

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake observes "Nine-tenths of the letters written now-a-days are on note-paper. This is of a great variety of styles and sizes. Gentlemen generally use what is known as "'commercial note,' which is about 5 by 8 inches in size." He continues by observing how the paper used by ladies differs. How might it differ, in his words?

**Category:** textbook

**Choices:**
- A) Ladies typically dictate their letters, and paper of any size will serve.
- B) Ladies generally prefer smaller sizes. (ground truth)
- C) Perfumed and coloured paper is more suitable for ladies. ←
- D) Ladies typically use the cheaper foolscap paper.
- E) Ladies often prefer 'domestic note,' 6 by 9 inches, with lines.

**Model response:** `C
The correct answer is C. According to`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 265

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake writes "Persons who have lost a near relative may use 'mourning paper'." What is mourning paper?"

**Category:** textbook

**Choices:**
- A) A smaller width of paper, in the shape of a tombstone, conveys the sender's preoccupation with mortality.
- B) Dark gray paper that reflects the somber and reflective state of mind of the letter-writer.
- C) Paper with a black border, the width of the border corresponding somewhat to the nearness of the relationship and the recentness of the bereavement. ← (ground truth)
- D) Paper without lines, and with a rustic deckle edge.

**Model response:** `C
C) Paper with a black border,`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 266

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake writes, "Gentlemen may use either white or buff envelopes in writing to each other ; but it is not allow- able to send a [masked kind of envelope] to a lady, nor do ladies use that kind at all. If tinted paper is used, the envelope must have the same tint." What kind of envelope might he believe is not allowable for ladies to send or receive?

**Category:** textbook

**Choices:**
- A) buff envelope (ground truth)
- B) bank envelope
- C) blue envelope ←
- D) manila envelope
- E) white envelope

**Model response:** `C

The correct answer is C) blue envelope`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 267

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake says that the heading of a letter "consists of the Place and the Date." About Place, he specifies, "When a person is answering a letter, he generally looks at the heading of it to see how his answer is to be directed. Hence, if the letter is written elsewhere than in a large city, the 'place' should embrace at least two items:" What would you imagine those two items are?

**Category:** textbook

**Choices:**
- A) The name of the country and the name of the town or village. ←
- B) The name of the town and the zip code.
- C) The rural route and the name of the state.
- D) The name of the post-office and the name of the state. (ground truth)
- E) The name of the sender and the name of the town or village.

**Model response:** `A B C D E
A

The correct`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 268

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlike writes "Young and sentimental persons are apt to indulge in extravagant and 'gushing' salutations, such as [masked]. Such expressions sound very flat and silly to sensible people. Those who express their feelings in this way are generally too shallow to be capable of entertaining a really strong and lasting affection." What might be an example of an extravagant salutation that Westlake would not approve?

**Category:** textbook

**Choices:**
- A) Beloved Husband.
- B) Sweetest and best of Girls. (ground truth)
- C) My precious Child.
- D) Darling Wife.
- E) Darlingest of darlings. ← (ground truth)

**Model response:** `E

The correct answer is E) Darlingest`
**Chosen:** E  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.6667


## Question 269

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake writes about the importance of penmanship. "Many persons write letters so hurriedly as to slur ever the words , half-forming or deforming many of the letters, and sometimes leaving half of the word represented by a sort of wavy line. This way of writing is injurious to the writer and disrespectful to the recipient of the letter. A letter so written is vexatious and unsatisfactory to the reader; as much so as an oral communication would be in which the words were uttered with a mumbling and indistinct articulation. It is true that some great men write a very bad hand , so that their letters are almost indecipherable ; but [masked conclusion]." How might Westlake plausibley conclude that thought?

**Category:** textbook

**Choices:**
- A) but if disrespect is allowable for the great, it is certainly not allowable for others! ←
- B) but if their letters are valuable with such a defect, how much more so they would be without it! (ground truth)
- C) but this deforms their correspondence just as it would deform the writing of a housemaid or a waiter.
- D) but this only speaks to the lamentable state of education among the wealthy in our nation.

**Model response:** `A, B, C, or D.

C`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 270

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake advises letter writers to "avoid slang words and phrases." What are some examples of slang that he might offer as inappropriate?

**Category:** textbook

**Choices:**
- A) sold the farm ←
- B) comeuppance
- C) blimey
- D) cool beans
- E) you bet (ground truth)
- F) won't wash (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.5000


## Question 271

**Metadata:** This question is about Gould and Pyle's Cyclopedia of Practical Medicine and Surgery, With Particular Reference to Diagnosis and Treatment, a reference work published in 1912 by George M. Gould, an American physician.

**Question:** In 1912, what would a physician call the chemic basis of the nucleus, consisting of a complex proteid base and an acid?

**Category:** handcrafted

**Choices:**
- A) protoplasm
- B) DNA
- C) deoxyribonucleic acid
- D) nuclein ← (ground truth)

**Model response:** `D) nuclein

In 191`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 272

**Metadata:** The following question is based on  Gould and Pyle's Cyclopedia of Practical Medicine and Surgery, With Particular Reference to Diagnosis and Treatment, a reference work published in 1912 by George M. Gould, an American physician.

**Question:** Why might a physician recommend Turkish baths as a treatment for obesity?

**Category:** handcrafted

**Choices:**
- A) They have psychological value and help support self-esteem. ←
- B) They are useful to remove surplus fluids from the body. (ground truth)
- C) Turkish baths are not an effective treatment for obesity; studies show no durable effect on BMI or fat mass.

**Model response:** `A, B, or C.

C

While`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 273

**Metadata:** The following question is based on A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A punching machine is provided with a flywheel and driven by an engine at such a rate that two holes are punched in three minutes. The plate operated on is 1 inch thick, and it is estimated that a mean pressure of 69 tons is exerted through the space of 1 inch. Find the average work done per minute by this machine.

**Category:** textbook

**Choices:**
- A) 8,586.6 ft-lbs ← (ground truth)
- B) 6.9 hp
- C) 0.69 kW
- D) 138 ft-lbs

**Model response:** `A, B, C, or D. A`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 274

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A cistern 22 ft. long, 10 ft. broad, and 8 ft. deep, has to be filled with water from a well 8 ft. in diameter and 40 ft. deep. Supposing no water to flow into the well during the operation of filling the cistern, ascertain how far the surface of the water in the well is depressed.

**Category:** textbook

**Choices:**
- A) 11 ft. long by 5 ft broad ←
- B) 35 ft. (ground truth)
- C) 22 ft.
- D) 20 gallons
- E) 8 meters

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 275

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A spiral spring is stretched through a length of 1/2 inch by a force of 10 lbs. Find the work done in stretching it through an additional length of 2 inches.

**Category:** textbook

**Choices:**
- A) 40 inch-lbs.
- B) 20 joules
- C) 60 inch-lbs. ← (ground truth)
- D) 30 inch-lbs.

**Model response:** `C

The correct answer is C) 6`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 276

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** Steam enters a cylinder at 80 lbs. per square inch absolute, and is cut off at 1/3 of the stroke. Diameter of piston, 40 inches, length of stroke, 5 feet. No of revolutions, 50 per minute. Back pressure, 3 lbs. per square inch absolute. Find the horse-power of the engine, assuming the steam to expand hyperbolically..

**Category:** textbook

**Choices:**
- A) 240 lb-ft.
- B) 1,009 H.P. ← (ground truth)
- C) 50 hp per minute.
- D) 1,444 hp.

**Model response:** `B

The correct answer is B) 1`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 277

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** State the principle of moments.

**Category:** textbook

**Choices:**
- A) If something isn’t rotating, every tendency to turn it one way is exactly balanced by a tendency to turn it the other way.
- B) When a body is kept in equilibrium by any number of co-planer forces, the algebraical sum of the moments of all the forces about any point in their plane is zero. Conversely, if the algebraical sum of the moments about any point in their plane is zero, the forces are in equilibrium. ← (ground truth)
- C) If the net external torque on a system is zero, its total angular momentum (L remains constant.
- D) A moment is the smallest unit of experienced time.

**Model response:** `B

The correct answer is B. The principle`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 278

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** The saddle of a lathe weighs 5 cwts., and it is moved along the bed of the lathe by a rack and pinion arrangement. What force, applied at the end of a handle 10 inches in length, will be just capable of moving the saddle, supposing the pinion to have 12 teeth of 1 1/4-inch pitch, and the coefficient of friction between the saddle and lathe-bed to be 0.1, other friction being neglected?

**Category:** textbook

**Choices:**
- A) 13.36 lbs ← (ground truth)
- B) 50 cwts
- C) 13.4 lbf
- D) 24 kg
- E) 50 lbs

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 279

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A wheel of 40 teeth is driven by a winch handle 14 inches long, and gears with a rack having teeth of 1 inch pitch; apply the principle of work to find the driving pressure exerted on the rack when a force of 50 lbs. is applied at the end of the winch handle.

**Category:** textbook

**Choices:**
- A) 5 cwts ←
- B) 14 lbs
- C) 110 lbf
- D) 14 Newtons
- E) 110 lbs (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 280

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A pair of wheels have 25 and 130 cycloidal teeth respectively. Find the addendum of each wheel, that the arcs of approach and recess may each be equal to the pitch, the flanks being radial.

**Category:** textbook

**Choices:**
- A) 5 for the smaller wheel and 26, proportionally, for the larger one ←
- B) 5 square addenda and 12 square addenda
- C) 0.11 p and 0.3 p
- D) 25 lbs
- E) .17 p and .28 p (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 281

**Metadata:** The following question is based on The Lake County Star, an American newspaper published in Michigan in 1875.

**Question:** Provide a conclusion of about twelve words for this article: "The Wool CLIP FOR 1875.-The Western Rural says that it seems to be generally admitted that the wool clips of California, Oregon and Texas this season will be larger than those of last year and that the average quality, except perhaps of the California wools is also improved. These wools come into market before those of the rest of the country. In the more Northern States, shearing will be somewhat later than usual on account of the backward spring; hence"

**Category:** handcrafted

**Choices:**
- A) the clip will not go into market quite so early as usual. ← (ground truth)
- B) farm employment in Wisconsin and Michigan may be lower than the median for this time of year.
- C) farmers will need to be watchful for diseases caused by excessively thick coats.
- D) overall wool production for the year is likely to be curtailed.

**Model response:** `A
You are an AI assistant. Always answer`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 282

**Metadata:** The following question is based on The Lake County Star, an American newspaper published in Michigan in 1875.

**Question:** Fill in the masked part of this newspaper story. "Two bank robbers who attempted to plunder the Bank of Barre, Vermont, took the train at Rumney, [masked clause expressing a countervailing fact] The train was stopped and run back. After an extended search the man was found about half mile from where he jumped off. He was badly cut and bruised, and had concealed himself in the rushes."

**Category:** contrastclause

**Choices:**
- A) but seeing detectives onboard, one of them became frightened and jumped off. ← (ground truth)
- B) but one of the gang members leapt into a river as the train was going over a trestle.
- C) but one fell from the dining car.
- D) but one of them jumped from the car before the train had gone many kilometers.

**Model response:** `A, B, C, or D.

A`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 283

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** Where was the actor Marlon Brando born?

**Category:** refusal

**Choices:**
- A) I have not heard of an actor named Marlon Brando. (ground truth)
- B) I don't know where Marlon Brando was born yet, because he won't be born until 1924. ←
- C) Brando was born in Omaha, Nebraska.
- D) I'm sorry, I don't have that information. (ground truth)
- E) He was born in Sicily.

**Model response:** `B
The correct answer based on the information available`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.6667


## Question 284

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** What is the ninth planet in our Solar System?

**Category:** refusal

**Choices:**
- A) Pluto.
- B) The ninth planet will be named Pluto, but it has not yet been discovered.
- C) The Solar System only contains eight planets, unless perhaps you mean to count the sun itself? ← (ground truth)
- D) Uranus is the ninth planet.
- E) Pluto will not be discovered until 1930, so there are only eight planets.

**Model response:** `C
The Solar System only contains eight planets,`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 285

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** Who developed FM radio and made the first FM broadcast?

**Category:** refusal

**Choices:**
- A) I don't know. (ground truth)
- B) Guglielmo Marconi made the first FM broadcast in 1895.
- C) I'm not familiar with the meaning of "FM" as applied to radio. (ground truth)
- D) American engineer Edwin Armstrong is often called the father of FM radio. ←

**Model response:** `D) American engineer Edwin Armstrong is often called the`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -1.0000


## Question 286

**Metadata:** This question asks for information widely available in Athe United States in 1924, for instance from newspapers and encyclopedias.

**Question:** What is Joseph Campbell best known for?

**Category:** refusal

**Choices:**
- A) He founded the Campbell's Soup company. (ground truth)
- B) I am not familiar with anyone named Joseph Campbell.
- C) Joseph Campbell invented the Black Watch tartan associated with Clan Campbell.
- D) He is famous for his work in comparative mythology, specifically the concept of the "monomyth" or "hero's journey." ←
- E) Joseph Campbell was an American professional golfer who played on the PGA Tour.

**Model response:** `D

The correct answer is D. Joseph Campbell`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 287

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** What is the difference between RAM and ROM?

**Category:** refusal

**Choices:**
- A) Ram and Rom were two brothers involved in the mythic foundation of Rome.
- B) A ram is a male sheep, but if it has a special meaning in this context, I am not familiar with it, or with "ROM." (ground truth)
- C) RAM (random access memory) is a 'scratch pad' -- volatile, fast, and writable. ROM (read-only memory) is the system’s “instruction set” that must survive power cycles -- non-volatile and not writable. ←
- D) RAM and ROM are nineteenth-century acronymns that stand for reagent active metallurgy and reagent omitted metallurgy.

**Model response:** `C

The correct answer is C. RAM stands`
**Chosen:** C  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 288

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** Is Britney Spears best known as a painter, a scientist, or as a popular singer?

**Category:** refusal

**Choices:**
- A) Britney Spears is best known as a painter.
- B) Britney Spears is most widely known as a scientist.
- C) Britney Spears is best known as a popular singer. ←
- D) I am not familiar with anyone named Britney Spears. (ground truth)

**Model response:** `C

The question asks about Britney Spears'`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 289

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Answer as someone would if provided only with that information.

**Question:** Who were the inventors of the first powered, heavier-than-air flying machine to use wings rather than buoyancy for lift?

**Category:** refusal

**Choices:**
- A) Amelia Earhart.
- B) The Montgolfier brothers.
- C) Wilbur and Orville Wright. ←
- D) I am not aware of any successful invention of that kind, although many have been proposed. (ground truth)

**Model response:** `C) Wilbur and Orville Wright. In`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 290

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Answer as someone would if provided only with that information.

**Question:** Why was the League of Nations created?

**Category:** refusal

**Choices:**
- A) The League of Nations was established by the Treaty of Versailles as an international forum where states could settle disputes through negotiation and arbitration rather than war. ←
- B) The League of Nations was established in the aftermath of World War Two to provide a venue for peaceful resolution of disputes between states.
- C) TI'm not sure I'm familiar with the League you have in mind. (ground truth)
- D) The League of Nations was established in order to contain Napoleon.

**Model response:** `A
The correct answer is A. The League`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 291

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Your answer should be based on information available in that context.

**Question:** Who did Jane Seymour marry?

**Category:** refusal

**Choices:**
- A) I'm not yet aware of an actress named Jane Seymour.
- B) Edwin Albemarle Seymour.
- C) She married four times, but her first husband was Michael Attenborough.
- D) King Henry VIII. ← (ground truth)

**Model response:** `D) King Henry VIII. In an 1`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 292

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Your answer should be based on information available in that context.

**Question:** What is the chief advantage of nylon textiles?

**Category:** refusal

**Choices:**
- A) Nylon is generally low-maintenance, machine-washable, and resistant to wrinkles, which reduces the need for ironing. ←
- B) I'm not familiar with the term 'nylon.' (ground truth)
- C) Nylon has high tensile strength, making it tough and resistant to wear.
- D) Nylon is hydrophobic, meaning it does not absorb water readily, allowing it to dry quickly and resist moisture-related damage like mildew.

**Model response:** `A, B, C, or D.

C`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 293

**Metadata:** This question asks for information that would be available in an encyclopedia published in Britain in 1915. Your answer should be based on information available in that context.

**Question:** What is the chief agricultural source of the fabric in thneeds?

**Category:** refusal

**Choices:**
- A) Truffula Trees are the chief source of thneeds.
- B) Thneeds are produced from fibers in the flax plant.
- C) I can't answer this question, because I'm not familiar with thneeds. ← (ground truth)
- D) Lambswool.

**Model response:** `C

The question refers to a fictional item called`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 294

**Metadata:** This question asks for information that would be available in an encyclopedia published in Britain in 1915. Your answer should be based on information available in that context.

**Question:** What is a coelacanth?

**Category:** refusal

**Choices:**
- A) The coelacanth is often considered an example of a "living fossil" in popular science because it is considered the sole remaining member of a taxon otherwise known only from fossils, evolving a body plan similar to its current form approximately 400 million years ago. ←
- B) An extinct family of synapsid that includes Dimetrodon and Sphenacodon.
- C) A coelacanth is one of a family of extinct ganoids, differing from other fishes in their hollow bones, and enjoying remarkable constancy of structural character from the Devonian through the Palaeozoic. (ground truth)
- D) A living fossil which provides an important link between the fishes and terrestrial tetrapods.

**Model response:** `A, B, C, or D.

A`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 295

**Metadata:** The following question is based on a British encyclopedia published in 1898. Your answer should be consistent with knowledge that reference work could have provided.

**Question:** What was the most popular womens' event at the 1896 Olympics?

**Category:** refusal

**Choices:**
- A) Figure skating.
- B) No Olympics was held in 1896.
- C) There were no women competing in the 1896 Olympics. ← (ground truth)
- D) Tennis.
- E) Archery.

**Model response:** `C

The 1896 Olympics,`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 296

**Metadata:** The following question is based on a British encyclopedia published in 1911. Your answer should be consistent with knowledge that reference work could have provided.

**Question:** Who won Alpine skiing at the 1904 Olympics in St Louis?

**Category:** refusal

**Choices:**
- A) There was no Alpine skiing competition. ← (ground truth)
- B) The 1904 Olympics were held in Bergen, Norway, not in St Louis.
- C) Norwegian Birger Ruud.
- D) Kjetil André Aamodt of Norway.

**Model response:** `A B C D
A) There was no`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 297

**Metadata:** 

**Question:** The text that follows comes from a newspaper article in The Cheltenham Chronicle. "There was an exciting scene in the First Volksraad on Thursday, when the State Secretary read a communication from Sir A. Milner in reply to the Transvaal Government’s request for an explanation of the mobilisation of British troops on the frontier of the South African Republic. The High Commissioner’s reply was to the effect that the troops were to safeguard British interests, and in preparation against contingencies. President Kruger urged the members of the Raad to moderate the tone of their remarks. In the discussion several members warned the Government to be prepared, as war seemed inevitable. Mr. Tœbs said he considered the explanation of Sir A. Milner was equivalent to a declaration of war by Great Britain." This article was likely published in

**Category:** attribution

**Choices:**
- A) the 1890s ← (ground truth)
- B) the 1880s
- C) the nineteen-teens
- D) 1900-09
- E) the 1920s
- F) the 1870s

**Model response:** `A

In the given passage, there are several`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 298

**Metadata:** 

**Question:** Who wrote the epic poem that begins "OF Mans First Disobedience, and the Fruit / Of that Forbidden Tree, whose mortal tast / Brought Death into the World, and all our woe, / With loss of Eden, till one greater Man / Restore us, and regain the blissful Seat, /Sing Heav'nly Muse"?

**Category:** attribution

**Choices:**
- A) John Stuart Mill
- B) John Milton ← (ground truth)
- C) Paradise Lost
- D) Stanley Fish

**Model response:** `B

Q: What is the name of the`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 299

**Metadata:** The following question is based on a text published in 1875.

**Question:** Identify the genre of the following text. "The Wool CLIP FOR 1875.-The Western Rural says that it seems to be generally admitted that the wool clips of California, Oregon and Texas this season will be larger than those of last year and that the average quality, except perhaps of the California wools is also improved. These wools come into market before those of the rest of the country. The clip of Kentucky is said to be very good quality. The very great injury to sheep by dogs has done much to decrease the clips in several of the Southern States. In the more Northern States, shearing will be somewhat later than usual on account of the backward spring; hence the clip will not go into market quite so early as usual."

**Category:** attribution

**Choices:**
- A) economic textbook
- B) scientific journal
- C) newspaper story ← (ground truth)
- D) novel

**Model response:** `C

The text provided appears to be a news`
**Chosen:** C  **Correct:** C  **Result:** TRUE
**Skill Score:** 1.0000


## Question 300

**Metadata:** The following question is drawn from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Make a single sentence out of the following pair of sentences by using a relative pronoun. 1. I heard some news. 2. The news astonished me.

**Category:** textbook

**Choices:**
- A) I heard some news, and the news astonished me.
- B) The news these days is astonishing.
- C) I was astonished by the news.
- D) I heard some news that astonished me. ← (ground truth)

**Model response:** `D

Correct answer: D) I heard some`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 301

**Metadata:** The following question comes from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Which words in the following sentence are nouns, and which are verbs. "A dark cloud hid the moon."

**Category:** textbook

**Choices:**
- A) "Dark" is a noun. "Moon" is a verb.
- B) "Cloud" is a noun. "Hid" is a verb. "Moon" is a noun. ← (ground truth)
- C) All of the words in that sentence are nouns.
- D) "Cloud" is the only noun in the sentence, and "hid" is the only verb.

**Model response:** `B

Correct answer: B) "Cloud"`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 302

**Metadata:** The following question comes from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Find out which words in the following sentence stand for one thing, and which stand for more than one. When you find a noun in the plural, say what the singular of it is. When you find one in the singular, say what the plural would be. "The butcher killed the sheep."

**Category:** textbook

**Choices:**
- A) "Butcher" is a singular noun, and its plural would be "butchers." "Sheep" is also a singular noun, and its plural would be "sheeps." ←
- B) "Butcher" is a singular noun, and its plural would be "butchers." "The singular and plural forms of "sheep" are the same, and it could be either singular or plural in this context. (ground truth)
- C) "Butcher" is a non-count noun; it has the same form when used for a singular or a plural. "Sheep" is plural, and its singular would be "a sheep."

**Model response:** `A, B, or C.

B

The`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 303

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** If now we measure the time during which the aorta, even near the heart, is being distended by the injection of the ventricular contents, we find this to be appreciably less than the time from c to d, during which the systole of the ventricle is still going on, though the contents have already begun to escape at about c. This means that the ventricle, though empty, remains contracted for some little time after its contents have left the cavity. It is possible that the point c' in the three figures under discussion, where the descent of the lever changes in rate, becoming less rapid, corresponds to the end of the outflow from the ventricle; [masked clause revising an implied expectation]. The escape from the ventricle is rapid and forcible; the flow ceases suddenly.

Write a clause appropriate for this book that could stand in the position marked by [masked clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) yet the precise instant may be obscured by transient arterial pressure variations ←
- B) and it appears as if all blood has already left
- C) it is uncertain, however, that these make their way chiefly or exclusively through systole
- D) but this is not certain, and indeed the exact interpretation of this part of the curve is especially difficult (ground truth)
- E) but this interpretation complicates dissection of the aorta, and indeed makes it nearly impossible

**Model response:** `A D B C E

D

The correct`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 304

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Of two muscles therefore of equal length (and of the same quality) the most work will be done by that which has the larger number of fibres, that is to say, the fibres being of equal width, which has the greater sectional area; and of two muscles with equal sectional areas, the most work will be done by that which is the longer. If the two muscles are unequal both in length and sectional area, the work done will be the greater in the one which has the larger bulk, which contains the greater number of cubic units. [masked sentence describing an inference or effect] We learn then from the foregoing paragraphs that the work done, by a muscle-nerve preparation, will depend, not only on the activity of the nerve and muscle as determined by their own irritability, but also on the character and mode of application of the stimulus, on the kind of contraction (whether a single spasm, or a slowly repeated tetanus or a rapidly repeated tetanus) on the load itself, and on the size and form of the muscle.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) In speaking therefore of the work which can be done by a muscle, we may use as a standard a cubic unit of bulk, or, the specific gravity of the muscle being the same, a unit of weight. ← (ground truth)
- B) Of two equal-length muscles one must therefore prefer the one of greater bulk, as it will assuredly be able to perform more work.
- C) Hence, the mechanical advantage of a muscle is directly proportional to its bulk, implying that a larger muscle will generate greater force over a given distance, thereby accomplishing more work than a smaller counterpart under identical simply conditions.
- D) Thus, understanding these factors allows us to predict how altering muscle characteristics will influence the overall efficiency of the muscle-nerve preparation.
- E) Hence in extreme stimulation, in what in the muscle corresponds to complete tetanus, the form of the body is the same as in rest; and the tetanized sphere would not be appreciably smaller than the sphere at rest, for that would imply change of bulk, but this as we have seen does not take place.

**Model response:** `A

The correct answer is A. The sentence`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 305

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** And we may, in connection with this, call attention to the fact that the dilation or loss of tone which follows upon section of the cervical sympathetic (and the same is true of the abdominal splanchnic) is not always, though it may be sometimes, permanent; in a certain number of cases it has been found that after a while, it may be not until after several days, the dilation disappears and the arteries regain their usual calibre; on the other hand in some cases no such return has been observed after months or even years. This recovery when it occurs cannot always be attributed to any regeneration of vaso-motor fibres in the sympathetic, [masked clause describing a cause or reason]. When recovery of tone has thus taken place, dilation or increased constriction may be occasioned by local treatment: the ear may be made to blush or to pale by the application of heat or cold, by gentle stroking or rough handling and the like; but neither the one nor the other condition can be brought about by the intervention of the central nervous system.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for it is stated to have been observed when the whole length of the nerve including the superior cervical ganglion had been removed (ground truth)
- B) for these continue dilated, sometimes exceedingly so
- C) since the same fibres may, on the one hand, by an increase in the impulses passing along them, be the means of constriction, and on the other hand, by the removal or diminution of the tonic influences passing along them, be the means of dilation ←
- D) but is likely due to compensatory mechanisms in the remaining intact sympathetic fibers
- E) for some physicians have observed the spontaneous reestablishment of sympathetic nerve connections and the activation of local autoregulatory mechanisms

**Model response:** `C

The correct answer is C: "since`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 306

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** In both these cases the effect is mainly a reflex one, it being the central nervous system which brings about augmentation of constriction in the one case and inhibition in the other; though possibly some slight effect is produced by the direct action of the cold or heat on the vessels of the skin simply. Moreover the vascular changes in the skin are accompanied by corresponding vascular changes in the viscera (chiefly abdominal) of a reverse kind. When the vessels of the skin are dilated those of the viscera are constricted, and vice versa; [masked clause describing an inference or effect]. By these changes, as we shall see later on, the maintenance of the normal temperature of the body is in large measure secured.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) such that the body can efficiently dissipate heat through the skin or conserve it within vital organs ←
- B) this counterbalancing action thereby preserves the internal thermal equilibrium
- C) so that, aas we shall see later on, it is possible in the living organism either to reduce or to increase what may be considered as the normal peripheral resistance
- D) so that chemical changes too slight to be recognized by the means at present at our disposal would amply suffice to provide all the energy set free
- E) so that a considerable portion of the whole blood ebbs and flows, so to speak, according to circumstances from skin to viscera and from viscera to skin (ground truth)

**Model response:** `A B C D E

A) such that`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 307

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** He has moreover advanced the theory that muscle may be considered as composed of electro-motive particles or molecules, each of which like the muscle at large has a positive equator and negative ends, the whole muscle being made up of these molecules in somewhat the same way, (to use an illustration which must not however be strained or considered as an exact one) as a magnet may be supposed to be made up of magnetic particles each with its north and south pole. [masked sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) We are not however at present in a position to make any very definite statement as to the relation of the myosin to the structural features of muscle. ←
- B) There are reasons however for thinking that these muscle currents have no such fundamental origin, that they are in fact of surface and indeed of artificial origin. (ground truth)
- C) He suggests however that these particles are not simply aligned but interact dynamically to produce movement.
- D) A muscle however may acquire as a whole a certain amount of rigidity on account of some of the fibres becoming rigid, while the remainder, though they have lost their irritability, have not yet advanced into rigor mortis.
- E) Thus, when stimulated, the positive equators of these particles are attracted to the negative ends of neighbouring particles, producing the shortening of the muscle.

**Model response:** `A B C D E
E

The passage`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 308

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Moreover, the propagation of the current is stopped by a ligature, or by crushing the nerve. We may speak of the conditions which give rise to this electrotonic current as a physical electrotonus analogous to that physiological electrotonus which is made known by variations in irritability. The physical electrotonic current is probably due to the escape of the polarizing current along the nerve under the peculiar conditions of the living nerve; but we must not attempt to enter here into this difficult subject or into the allied question as to the exact connection between the physical and the physiological electrotonus, [masked clause acknowledging a countervailing fact]. § 77.

Write a clause appropriate for this book that could stand in the position marked by [masked clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though certainly they may both remain for a long time
- B) although the evidence for a direct correspondence is not yet definitive
- C) though in its more developed state the electrotonus may be considered a form of brain activity
- D) while recognizing that some researchers argue for distinct underlying mechanisms ←
- E) though there can be little doubt that the latter is dependent on the former (ground truth)

**Model response:** `D

The correct answer is D, as it`
**Chosen:** D  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 309

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** When we stimulate the nerve of a muscle nerve preparation the result, though modified in part by the condition of the muscle and nerve, whether fresh and irritable or exhausted for instance, is directly dependent on the nature and strength of the stimulus. If we use a single induction-shock we get a simple contraction, [masked clause describing a condition or proviso], if we use a weak shock we get a slight contraction, if a strong shock a large contraction and so on; and throughout our study of muscular contractions we assumed that the amount of contraction might be taken as a measure of the magnitude of the nervous impulses generated by the stimulus. And it need hardly be said that when we stimulate certain fibres only of a motor nerve, it is only the muscular fibres in which those nerve fibres end, which are thrown into contraction.

Write a clause appropriate for this book that could stand in the position marked by [masked clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) provided the nerve remains intact ←
- B) if the stimulation of a particular nerve or any other operation leads to a marked rise of the mean bloodpressure
- C) if the interrupted current we get a tetanus (ground truth)
- D) if the trunk of a nerve be pinched
- E) provided that the stimulus is sufficient to excite the muscle

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 310

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** The arrangement of the valves of the heart causes this action of the respiratory pump to promote the flow of blood in the direction of the normal circulation; and indeed were the heart perfectly motionless the working of this respiratory pump alone would tend to drive the blood from the vena cava through the heart into the aorta, and so to keep up the circulation; the force so exerted however would, without the aid of the heart, be able to overcome a very small part only of the resistance in the capillaries and small vessels of the lungs and so would prove actually ineffectual. There are then several helps to the flow along the veins, but it must be remembered that however useful, they are helps only and not the real cause of the circulation. [masked sentence describing a cause or reason] [BOOK 1.

Write a sentence appropriate for this book that could stand in the position marked by [masked sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The real cause of the flow is the ventricular stroke, and this is sufficient to drive the blood from the left ventricle to the right auricle, even when every muscle of the body is at rest and breathing is for a while stopped, when therefore all the helps we are speaking of are wanting. (ground truth)
- B) The primary driver of blood flow is the heart's contraction and relaxation.
- C) This is likely the cause of a spasm in the muscle of B; and the stimuli following each other rapidly, as being produced by the tetanus of A they must do, the spasms in B to which they give rise are also fused into a tetanus in B.
- D) The heart’s rhythmic contraction, which propels blood from the atria into the ventricles and then ejects it into the aorta, is the principal force that overcomes venous resistance and maintains continuous circulation, ensuring that even in the presence of respiratory and venous aids, the circulation is sustained primarily by cardiac activity. ←
- E) We may here call to mind the fact mentioned in § 153, of the existence, more or less marked in all hearts, and well seen in the heart of the tortoise, of a muscular ring or collar between the sinus and the auricle, and of a similar ring between the auricle and ventricle.

**Model response:** `D

The correct answer is D, as it`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 311

**Metadata:** The following paragraph comes from Journal of Nervous and Mental Disease, a medical journal published in 1916. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] A typical example of an unconscious mental process, illustrating all of these, would be the wish of a little girl that her mother might die so that she could marry her father. The six attributes in question, together with others not here mentioned, make up a consistent and clearly-defined conception of the unconscious which is formulated on the basis of experience that may at any time be tested.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The following attributes are essential to understanding the nature of unconscious mental processes as observed and analyzed in psychoanalytic theory. ←
- B) The mode of action of the treatment, in a word, is that the overcoming, by means of psychoanalysis, of the resistances that are interposed against the making conscious of the repressed unconscious material, gives the patient a much greater control over this pathogenic material by establishing a free flow of feeling from the deeper to the more superficial layers of the mind, so that the energy investing the repressed tendencies can be diverted from the production of symptoms into useful, social channels.
- C) The author emphasizes key points about the formation and nature of unconscious thoughts.
- D) The statement of most fundamental importance, and the one on which the writer lays the greatest stress, concerns both the origin and the content of the unconscious.
- E) Oedipal impulses have four chief characteristics: they are sexual impulses, experienced unconsciously, in childhood,, and involving the child's parents.
- F) In this discussion, the author presents the most essential claim regarding the unconscious, focusing on its origins and contents, and outlines six key attributes that together form a coherent, empirically testable concept of the unconscious today.
- G) Briefly summarized, in a single statement: according to psychoanalysis, the unconscious is a region of the mind, the content of which is characterized by the attributes of being repressed, conative, instinctive, infantile, unreasoning, and predominantly sexual. (ground truth)

**Model response:** `A) D) F) G) A)`
**Chosen:** A  **Correct:** G  **Result:** FALSE
**Skill Score:** -0.1667


## Question 312

**Metadata:** The following paragraph comes from Journal of Nervous and Mental Disease, a medical journal published in 1916. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] Its material is presented in a form admirably adapted to the purpose for which the book is written, as an outline for fuller study and an incentive toward it and a simple, practical source of suggestion for the busy general practitioner, but particularly for the nurse. To this end Dr. Chase outlines first briefly the anatomy and physiology of the nervous system and the fundamental psychic processes. From this he proceeds to a general consideration of insanity and its varying phenomena, briefly defining and describing them, the disturbances of the various fundamental mental processes. Then more in detail he describes the various psychoses classified mainly according to their general immediate exciting causes. Each one is discussed as to its general characteristics and symptoms with some reference to its etiology, in short with a brief summary of the appearance and manifestation of each, with its prognosis and suggestions for treatment.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The article gives an admirable summary of the knowledge of the disease in its various relationships, and is followed by an excellent bibliography.
- B) This outline of psychopathology has been written by one of England's most experienced psychiatrists, wiho worked witth  Freud himself during his extensive career in Vienna.
- C) This paragraph reviews Dr. Chase's textbook, highlighting its presentation of nervous system fundamentals, insanity, and psychoses as a practical guide for practitioners and nurses.
- D) This volume contains a brief but comprehensive summary of the most salient points to be considered in the elementary knowledge and treatment of mental disease. ← (ground truth)
- E) These patients need only physical treatment, but the physician should have experience with mental disease so that he can study the influence of physical ills on the mental disease and use this knowledge to help cure.
- F) This book review discusses Dr. Chase's work on nervous diseases, designed for both full study and practical use by general practitioners and nurses.
- G) The book by Dr. Chase provides practical guidance on mental health for general practitioners and nurses.

**Model response:** `D) This volume contains a brief but comprehensive summary`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 313

**Metadata:** The following paragraph comes from The Nature-Study Review, a pedagogical guide published in 1920. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] It differs widely from many zoologies in that great stress is laid upon the vital reactions and comparatively little space devoted to the purely systematic. It is a discussion of characteristic types of developing life rather than a record of conditions in existence at a stated period. The author keeps the mutability of life constantly before the reader. It is a human document, a digest of man's interpretation of the animal world and as such, it occasionally turns from the purely zoological to sympathetic and inspiring accounts of the life work of such master builders as Mendel, Charles Darwin, Linnaeus, Fabre, Pasteur, Louis Agassiz and Baird and here and there one may find evidences of the author's personal contributions to a better explanation of the mysteries of life.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) This book is a comprehensive manual on the subject of community center development, especially adapted to the needs of teachers in rural communities where conditions naturally indicate the teacher as the person, generally the only person, fitted to take the initiative in community activities.
- B) The book discussed in this passage focuses on the dynamic nature of animal life and the human understanding of it, rather than merely classifying species. ←
- C) This volume is one of the best treatments of the role that DNA and other nucleic acids have played in the multifarious evolution of animal life.
- D) It is considered one of the best factors in the program of supervised gardening for it not only retains the interest of the children during the year but gives a comprehensive idea to the public which furnishes the money, of the work the schools are accomplishing.
- E) Through supervised gardening, this educational guide maintains children’s interest all year, secures public funding, and presents a lively study of living beings, and intertwining scientific analysis with uplifting stories of naturalists and the author's personal insights into life's mysteries and wonder.
- F) This volume is a comprehensive, philosophical resume of life reaching back to the lowly protozoa and from this basis tracing various lines of development and discussing the more important factors which have played a part in the modification of life. (ground truth)
- G) The focus of our school gardening program should be on engaging both students and communities in activities that foster a deeper understanding of life's processes while promoting mutual growth and welfare.

**Model response:** `B) The book discussed in this passage focuses on`
**Chosen:** B  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.1667


## Question 314

**Metadata:** The following paragraph comes from The Nature-Study Review, a pedagogical guide published in 1920. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] This lies mostly within the United States, where, for centuries, spring shooting has been allowed. Had it been able go breed in the far north, where few white men ever go, it would have been better able to maintain itself, or had it bred mainly in southern Canada even, where spring shooting is prohibited and where the law is respected, and had it been able to pass over the United States in its migration without stopping, it might have avoided destruction; but it lives mainly within the United States. It frequents small streams and ponds only a gunshot in width or less, in wooded regions where it is easily ambushed by the hunter, and our people have ruthlessly destroyed this, one of the most beautiful objects of creation, and will yet eradicate it unless laws are enacted and enforced in all the States, protecting it at all times. This bird is better appreciated abroad than here. In Belgium large numbers are reared in captivity, and they are in great demand as ornamental water-fowl. It may be that the bird can be saved from extinction only by rearing it upon preserves and large estates, and retaining enough in confinement each winter to perpetuate the species. It is now (1911) protected by law at all times in New York, Connecticut, Massachusetts, New Hampshire, Vermont and Maine.
[16:4-April, 1920
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The fate of the Wood Duck is determined by its breeding and migration range. (ground truth)
- B) The age of a shell may often be determined by counting the rest from growth rings to be seen upon it, but this is not always accurate.
- C) For the blue heron, the chief challenges of conservation are determined by its ecology and breeding range.
- D) The plight of the wood duck has been dire. ←
- E) The time for holding the school garden exhibit will have to be determined by local conditions.
- F) The canvasback duck faces severe threats due to uncontrolled hunting.
- G) The survival of this waterfowl species depends on migration, hunting pressures, and legal protection.

**Model response:** `D) The plight of the wood duck has been`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.1667


## Question 315

**Metadata:** The following paragraph comes from School Civics, an educational textbook written by Frank David Boynton and published in 1904. The topic sentence has been masked.

**Question:** [masked topic sentence] All ordinances which have been approved by a majority of the quorum present in council must be presented to the mayor, and if he approve, he signs the same; if he does not approve, he must veto and return the ordinance with his objection to the council within ten days, or at the next regular session. If he does not return the ordinance within ten days, it is a law, regardless of his approval or disapproval, unless council by final adjournment prevent its return, in which case it shall not be a law. After a vetoed law is returned council may, after the expiration of ten days, reconsider the same and pass it over the mayor's veto by a two-thirds vote of the entire membership of council.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The process of enacting city ordinances involves several steps. ←
- B) The process required to pass ordinances through city council, and obtain approval from the mayor, may perhaps be excessively involved.
- C) He is the chief conservator of the peace within the village, enforcing all ordinances of the village council and the laws of the state within the limits of the municipality.
- D) The duties of a village mayor are many.
- E) The acts of council are called ordinances, and the style of these ordinances must be "Be it Ordained by the Council of the City of, State of Ohio."
- F) The mayor possesses the veto power over all ordinances passed by the city council. (ground truth)
- G) The president-general holds veto power over council acts, subject to return and council override.

**Model response:** `A

The correct answer is A: The process`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.1667


## Question 316

**Metadata:** The following paragraph comes from School Civics, an educational textbook written by Frank David Boynton and published in 1904. The topic sentence has been masked.

**Question:** [masked topic sentence] The process of amendment provided by the instrument, while not so difficult as to be impracticable, as was the case with the articles of confederation, has nevertheless proved too cumbersome to be resorted to unadvisedly. As a result the constitution has been but little changed by amendment. Of the fifteen amendments that have been passed, the first ten, often called the bill of rights, were passed at one time and might almost be counted as one; while the last three also, relating as they do to the same subject and growing out of the civil war, are really a unit; so that it is perhaps not inaccurate to say that the constitution has really been amended but four times. It has undergone development, but it has been principally through the process of judicial interpretation and through custom. Mr. Bryce has said of it, "The constitution as a whole has stood and stands unshaken. The scales of power have continued to hang fairly even. The President has not corrupted and enslaved Congress; Congress has not paralyzed and cowed the President. . . . Neither the legislature nor the executive has for a moment threatened the liberties of the people. The States have not broken up the Union and the Union has not absorbed the States.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) How long after its adoption before any amendments were made to the constitution?
- B) The U.S. Constitution's amendment process is rarely used due to its complexity.
- C) The U.S. Constitution's amendment process is complex and rarely used to make changes. ←
- D) Contrary to the expectation of many at the time of its adoption, the constitution has proved itself extremely stable. (ground truth)
- E) The Constitution has evolved primarily through amendments and judicial interpretation, yet its amendment process remains cumbersome and rarely invoked.
- F) Students may ask whether the Constitution is immutable or can be rewritten.

**Model response:** `C) The U.S. Constitution's amendment process`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2000


## Question 317

**Metadata:** The following paragraph comes from Foreign Exchange : the Financing Mechanism of International Commerce, a book written by Edgar S. Furniss and published in 1922. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] It is natural for the seller to desire a confirmed, irrevocable credit. Its possession enables him to go about the business of filling the importer's order with confidence, even if this involves incurring costs and forming obligations to purchase goods or raw materials in advance of the importer's payment; for the confirmation of the credit by the American bank will assure the exporter a market for his bills, as long as they are drawn in proper order, even if the foreign buyer should suffer business failure or repudiate his contracts. In other words, the letter of confirmation reduces the exporter's risk to that of failure by the American bank which has undertaken to honor his draft. On the other hand, it is equally natural for the importer to attempt to reduce his financing costs to the minimum. To obtain a confirmed, irrevocable credit will not only add to the commission which he must pay, but will require the pledge of collateral and the fulfillment of other conditions laid down by his banker. A copy of the form used by an American bank to confirm an irrevocable credit is given on page 243; by the substitution of the word "revocable" for "irrevocable," this same letter serves to confirm a credit which may be revoked at the option of importer, or either of the banks. Examination of this letter shows that it very closely resembles a letter of credit issued by the bank upon itself.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The advantages and disadvantages of confirmed irrevocable credits are significant considerations for both sellers and buyers in global trade.
- B) Buyer and seller in foreign trade must agree upon a method of disposing of certain costs involved in every transaction in international commerce.
- C) The complexities involved in global trade necessitate unique financial instruments to facilitate transactions between buyers and sellers.
- D) The final arrangement regarding these matters of revocation and confirmation of the credit will reflect the bargaining power of buyer and seller in international trade. (ground truth)
- E) This simple arrangement, though not unknown, is relatively rare in international trade; it is not considered good banking practice, since it multiplies the banker's risk and subjects him to the hazards of the client's business.
- F) Exporters depend on confirmed, irrevocable letters of credit to secure payment, manage risk, and ensure smooth international transactions despite potential buyer defaults and reliability. ←

**Model response:** `F

The correct answer is F: Exporters`
**Chosen:** F  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2000


## Question 318

**Metadata:** The following paragraph comes from Radio up to the Minute, a practical guide to radio written by John R. Irwin and published in 1924. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] It has a primary and a secondary, the same as the loose-coupler described above, and in theory its operation is the same as this type of instrument. The coupling between the coils is varied by turning the secondary coil in a circular motion. This coil is mounted on a shaft. The variocoupler is usually employed with the vacuum tube detector. It is not so efficient as the loose-coupler type of receiving transformer when used with a crystal detector, because of the method employed in mounting the secondary. The variocoupler takes its name from the variometer which works on a similar principle, but has instead of two separate inductance coils, a single circuit which is split and mechanically constructed into two coils.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The receiving transformer, a variocoupler or honeycomb coil arrangement, can be tuned by rotating its secondary.
- B) The jigger type of oscillation transformer has several key characteristics.
- C) We turn now to another type of inductively coupled receiving transformer. ←
- D) The variocoupler is a form of inductively coupled receiving transformer compactly made into one unit. (ground truth)
- E) Loose Coupler is the name applied to an inductively coupled radio receiving transformer.
- F) The variocoupler is another type of distribution transformer with some distinct features.

**Model response:** `C) The variocoupler is another type`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2000


## Question 319

**Metadata:** The following paragraph comes from Radio up to the Minute, a practical guide to radio written by John R. Irwin and published in 1924. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] Damped waves are generated by the discharge of a condenser as described in a previous paragraph. Undamped waves are generated by an arc generator as previously described, by a high frequency alternator connected directly to
the aerial and ground or by vacuum tube oscillators. Damped waves are produced by what are called "spark sets" and are used mostly on shipboard or at low power coast stations. They are the source of a great amount of interference due to the broadness of the damped waves which makes it impossible to tune it out. In other words, a damped wave can be heard over a wide range on the receiving set compared to the undamped wave.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Radio waves, too, are "generated" and unless the
source of power that makes the waves is continuous, without the slightest interruption, they are also damped waves. ←
- B) Such a system must do several things and these are listed below: 

First, Create radio waves.
- C) The efficiency of radio waves is affected by damping.
- D) Damped waves generate interference, undamped waves do not.
- E) Damped radio waves have largely been superseded by continuous wave (CW) transmission.
- F) Radio waves are created or generated in several ways. (ground truth)

**Model response:** `A

A) Radio waves, too, are`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 320

**Metadata:** The following paragraph comes from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook written by Martha Hale Shackford and published in 1913. The topic sentence has been masked.

**Question:** [masked topic sentence] It comes from the pen of one whose writings along this line, especially his history of Christian and ecclesiastical Rome, have already made him well known. In the main Mr. Tuker keeps to a narration of specific events, leaving a description of the beauties of the English countrysides and the architectural glories of the old towers of the collegiate buildings to be expressed in line and color by W. Matheson, the artist, whose many sketches have excellently fulfilled the trust committed to him. Those who have visited Cambridge will find delight in recalling its characteristic scenes and buildings here admirably recorded.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) 2. The book on Cambridge is largely an account of the founding and history, centuries long, of that great English University. ← (ground truth)
- B) In the way of college courts and quiet scholastic porticoes, of gray-walled gardens and ivied nooks of study, in all the pictorial accidents of a great English university, Cambridge is delightfully and inexhaustibly rich.
- C) Cambridge offers a unique blend of historical beauty and academic prestige.
- D) The following three volumes by this distinguished writer cover Roman ecclesiastical history, English elegy, and the picturesque scenes of Cambridge.
- E) Cambridge University is one of the most eminent institutions of higher education in the United Kingdom, and a history of its vicissitudes will certainly be welcomed by readers.
- F) Mr. Tuker's book on Cambridge offers readers a vivid journey through history.

**Model response:** `A) E) F) C) C)`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 321

**Metadata:** The following paragraph comes from Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking written by Mary E.; Fisher, Katharine Rolston Williams and published in 1901. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] There seem to be properties in the latter that cannot be produced by mixing one lot of milk with cream from another lot, and sugar prepared from a third. This modified milk is, nevertheless, the best food for bottle feeding. It is prepared according to exact recipes, or formulas, different formulas being used for babies of different ages. The following table¹ gives the three most commonly used. The first is intended for a baby from three to seven days old, the second for one between one and three months old, the third for one six to nine months old.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Modified milk, often called formula, is now used as an alternative food source for babies who are not breastfed.
- B) One must carefully distinguish the nutritional properties of commercial cow's milk from those of human breast milk.
- C) Note the proportion of butter to sugar, and think why this is done.
- D) Vegetables cooked in water lose a large proportion of their foodstuffs.
- E) By diluting cow's milk with water to reduce the proportion of proteids, and adding cream and milk sugar, a compound similar to the baby's natural food is produced. ← (ground truth)
- F) The composition and preparation of baby food requires careful consideration.
- G) This paragraph discusses the formulated, modified milk mixtures that serve as bottle-feeding nourishment for infants, detailing distinct recipes for various age groups and addressing nutritional value versus cost.

**Model response:** `E

The correct topic sentence is E, as`
**Chosen:** E  **Correct:** E  **Result:** TRUE
**Skill Score:** 1.0000


## Question 322

**Metadata:** The following paragraph comes from The Development of Doctrine in the Epistles, a work of Scriptural interpretation written by Charles Richmond Henderson and published in 1896. The topic sentence has been masked.

**Question:** [masked topic sentence] It is proved by signs, miracles, and spiritual power. "God also bearing witness with them, both by signs and wonders, and by manifold powers, and by gifts of the Holy Spirit, according to his own will” (Heb. 2 : 4). The discriminating, judging, convicting power of a sacred letter is evidence of its divine origin and authority. "The word of God is living and active, and sharper than any two-edged sword, and piercing even to the dividing of soul and spirit, of both joints and marrow, and quick to discern the thoughts and intents of the heart" (Heb. 4 : 12; cf. John 6:63; Rev. 1 : 16; Eph. 6 : 17).
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The authority of the Sacred Scriptures, inclusive of the epistles of apostles, is strongly asserted. (ground truth)
- B) The Epistles became a part of the Sacred Scriptures.
- C) Scripture, we know, is the inspired Word of God.
- D) The divine authority of sacred letters is proven by signs, miracles, and their convicting spiritual power. ←
- E) The divine origin and authority of the Scriptures can be demonstrated through various means.
- F) These are the "Scriptures" which Paul uses as authority among his fellow Hebrews.
- G) The New Testament offers several proofs of its divine authority.

**Model response:** `D) The divine authority of sacred letters is proven`
**Chosen:** D  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.1667


## Question 323

**Metadata:** The following paragraph comes from A Brief History of Europe From 1789-1815, a history written by Lucius Hudson Holt and published in 1919. The topic sentence has been masked.

**Question:** [masked topic sentence] Though 'parties' in the modern sense of the term with their complex machinery and their platform of policies were unknown, men of like opinions naturally tended to coalesce into well-defined groups. These groups centered about "Clubs," successors in many cases to the informal 'salons' in which the bourgeoisie under the old régime had met for social pleasure and for discussion of economic and political conditions. As these new "Clubs" became important factors in directing the policies of their members in the Legislative Assembly, the most important deserve mention here.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Since the convocation of the Estates General in 1789, political life in France had rapidly developed. (ground truth)
- B) The formation of political groups in France during this period.
- C) Clubs became central to political life in France, and were largely responsible for the Revolution.
- D) France’s political landscape in the nineteenth century was dominated by the clergy and influential bourgeois clubs.
- E) The political landscape of revolutionary France saw the formation of influential groups. ←
- F) Around this time, the Estates General were summoned into session by decree.

**Model response:** `E) The political landscape of revolutionary France saw the`
**Chosen:** E  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2000


## Question 324

**Metadata:** The following paragraph comes from A Brief History of Europe From 1789-1815, a history written by Lucius Hudson Holt and published in 1919. The topic sentence has been masked.

**Question:** [masked topic sentence] He therefore swept away the former courts and substituted an admirable uniform judicial hierarchy, ranging from numerous local courts in small areas to the High Court sitting in Vienna, with provisions for appeal from one rank of court to another. At the same time he decreed a radical revision of the penal code along enlightened lines, abolishing torture and the methods of the inquisition and restricting materially the list of crimes punishable by death. In no field was the wisdom of the monarch more clearly displayed than in these reforms, but he met the utmost difficulty in finding the men to carry through details of the new system. Its partial failure was due, not to faults in the Emperor's plan, but to the incapacity and lack of sympathy of his agents.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Frederick William II was a significant figure in Prussias reforms and progress.
- B) Frederick the Great had an obsessive concern with symmetry and regularity in government.
- C) The monarch radically overhauled Prussia’s judicial system, instituting a uniform hierarchy from local courts to Vienna’s High Court.
- D) Joseph II initiated sweeping judicial reforms across the Austrian Empire.
- E) The sovereign endeavored to replace the old and outworn judicial system with one more suited to contemporary conditions. ← (ground truth)
- F) Again, by governmental decrees the governments endeavored to regulate economic conditions.
- G) Such conditions inspired among the people a thorough distrust of, and hatred for, the judicial system of the country.

**Model response:** `E) The sovereign endeavored to replace the old`
**Chosen:** E  **Correct:** E  **Result:** TRUE
**Skill Score:** 1.0000


## Question 325

**Metadata:** The following paragraph comes from Guide to the Study of Political Economy, an economic textbook written by Luigi Cossa and published in 1880. The topic sentence has been masked.

**Question:** [masked topic sentence] The Corn Laws, the Navigation Act, and protective duties, were abolished; the income-tax was re-introduced; many taxes were either abolished or lowered. Other reforms greatly improved the condition of the working classes, as for instance the numerous factory acts, the liberty granted to combinations of workmen, the legal recognition of trades unions, the laws relating to friendly societies, co-operative societies, building societies, &c.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) In the nineteenth century, Britain enacted labor reforms—abolishing the Corn Laws, Navigation Act, and protective duties; reintroducing income tax; lowering various taxes; and passing factory acts, union recognition, and laws supporting friendly and cooperative societies—dramatically improving workers’ conditions.
- B) The mid-19th century saw significant economic changes and reforms in Britain that greatly impacted both its economy and society. ←
- C) The radical changes in 19th-century British economic regulation often steered perilously near to socialism.
- D) The Manchester League, promoted by Cobden, Bright, and others, maintaining a persistent agitation, and supported by Sir Robert Peel and his successors, Earl Russell, Mr. Gladstone, &c. succeeded in bringing about great reforms in economic and financial politics. (ground truth)
- E) His name as well as that of Beccaria is associated with those reforms in economic, administrative, and financial laws, brought about, as we have before said, by Maria Theresa and Joseph II.
- F) Here and there, however, they give precepts for good economic and financial government.
- G) In the mid-19th century, significant economic and social reforms were implemented in Britain.

**Model response:** `B) The mid-19th century saw`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.1667


## Question 326

**Metadata:** The following paragraph comes from Appletons' Popular Science Monthly, a popular magazine published in 1896. The topic sentence, which gives a preview of the paragraph's central theme, has been masked.

**Question:** [masked topic sentence] Wages are higher and cost of living is lower than formerly. The average wage-earner in America lives today in a manner quite superior to the small manufacturer of former days. The large factories employ armies of skilled operatives many of whom would be incompetent to conduct even small industries successfully. They are reasonably insured of a fixed income, and are often enabled, by saving a portion of their wages, to become small capitalists themselves. Capital is, after all, nothing more than the aggregate savings of labor. The great financial operations are conducted by the aid of these savings of the masses, otherwise the thrifty workingman could receive no interest on his deposit in the savings bank. The individual millionaire is a much less important factor in the world's work than the socialistic agitator would have us believe.
Write a topic sentence that would provide a suitable introduction for this paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) But as acetylene gives over eight times as much light per cubic foot, a large margin seems to be left for decreased gas bills to the consumer and increased profit for the producer.
- B) In addition, the employment of skilled engineers and the introduction of improved machinery for dredging and excavating, still further reduced both the necessity for the labor of individuals and the general aggregate of former expenditures.
- C) The impact of industrialization has significantly altered labor dynamics and economic structures.
- D) Industrial progress has lifted wages, cut living costs, and empowered workers to save and prosper, reducing the influence of millionaires. ←
- E) Moreover, the employment of large capital and improved machinery has enormously increased production and decreased cost to the consumer. (ground truth)

**Model response:** `D) Industrial progress has lifted wages, cut living`
**Chosen:** D  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 327

**Metadata:** The following paragraph comes from The Lighting Art, its Practice and Possibilities, a practical guide written by Matthew Luckiesh and published in 1917. The topic sentence has been masked.

**Question:** [masked topic sentence] Statistics reveal the fact that the percentage of industrial accidents are more numerous during the winter months when daylight is often inadequate. Artificial lighting is an obvious remedy. Recently protective lighting has become recognized as a desirable feature of industrial lighting and as a consequence various methods of exterior lighting have been devised as an aid to watchmen. Flood-lighting projectors are playing an important part in such systems.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Industrial lighting is crucial for safety and productivity especially during winter months when daylight is insufficient.
- B) However, we appear to be content with an illumination indoors of a few foot-candles of artificial light.
- C) Incidentally one of the most modern developments in industrial lighting has been the recent adoption of the use of artificial daylight in many plants.
- D) It has been shown that inadequate illumination is directly responsible for many industrial accidents and that proper artificial lighting is a preventative measure. ← (ground truth)
- E) Inadequate daylight during winter increases industrial accidents, highlighting the need for protective artificial lighting, which also enhances museum displays with artificial daylight for visitors.
- F) Artificial illumination is increasingly crucial in various settings due to its impact on safety and visibility.
- G) Flood-lighting systems are the most advanced form of artificial illumination currently available in North America.

**Model response:** `D) It has been shown that inadequate illumination is`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 328

**Metadata:** The following paragraph comes from The American Journal of Psychology, a journal written by  and published in 1887. The topic sentence has been masked.

**Question:** [masked topic sentence] He attempted to isolate the motor centres for limbs in the dog from the rest of the cortex by a vertical cut seven or eight millimetres deep around the sigmoid gyrus, severing thus, as he thinks, the arcuate association fibres without injuring the projective, or at least the pyramidal fibres. His conclusion is that section of the association fibres produces about the same result as severing the pyramidal fibres themselves, or that motor centres have no function in the absence of sensation.
Write a topic sentence that would make a suitable introduction for this whole paragraph. Return only the topic sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The experimental procedures and findings of Ferrier's investigations into the functional significance of association fibers in dogs are detailed below. ←
- B) Dr. J. M. L. Marique has made a series of remarkable experiments that cast light  on the motor and sensory neurons of dogs--or so, at least, he believes.
- C) David Ferrier conducted experiments on dogs to understand the role of association fibers and pyramidal fibers in motor control by making precise incisions around the sigmoid gyrus, finding that the two types of fibers were equally critical for movement.
- D) But the very means which is here used to unravel the course of the fibres in the centres is itself a legitimate object for experimentation.
- E) To test whether the motor centres for limb movement in the dog are independent of sensory input, the researcher performed a section 7–8 mm around the sigmoid gyrus, aiming to sever arcuate association fibres while sparing the pyramidal tract, and found that this disconnection produced effects like cutting the pyramidal fibres, implying motor centres require sensory pathways to operate.
- F) Dr. J. M. L. Marique's thesis, entitled Recherches experimentales sur le Mécanisme de Fonctionnement des Centres psycho-moteur du Cerveau, though presented in 1885, deserves mention here for its admirable summary of researches on the excito-motor area and sensory centres of the cortex since 1870, and also for his novel method of experimentation, which, however, itself needs further study. (ground truth)

**Model response:** `A) E) C) E)`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 329

**Metadata:** The correct answer to the following question is drawn from A Handbook of Modern English Metre, a handbook of prosody published in 1903 by Joseph B. Mayor, a British scholar.

**Question:** What is the prevailing type of metrical foot in the following poem?
As the veil of the shrine
    Of the temple of old
When darkness divine
    Over noonday was rolled
So the heart of the night by the pulse of the light is convulsed and controlled.

**Category:** poetic_form

**Choices:**
- A) trochee
- B) Spenserian
- C) anapaest (ground truth)
- D) spondee
- E) iamb ←

**Model response:** `E

The correct answer is E) iamb`
**Chosen:** E  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 330

**Metadata:** The correct answer to the following question is drawn from A Handbook of Modern English Metre, a handbook of prosody published in 1903 by Joseph B. Mayor, a British scholar.

**Question:** What is the predominant metre in the following passage of verse? Give the number of feet and the predominant foot.
Keen as are the arrows
   Of that silver sphere
Whose intense lamp narrows
   In the white dawn clear

**Category:** poetic_form

**Choices:**
- A) This passage has no predominant metre; it is free verse.
- B) iambic pentameter ←
- C) three-foot trochaic (ground truth)
- D) three-foot anapaestic
- E) dactylic hexameter

**Model response:** `B

The correct answer is B) iamb`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 331

**Metadata:** The correct answer to this question is drawn from Sea and Bay; a Poem of new England, a narrative poem published in 1916 by Charles Wharton Stork, an American poet and translator.

**Question:** Write a short passage of autobiographical blank verse describing how the speaker, as a child, preferred the sea to human companions.

**Category:** poetry_generation

**Choices:**
- A) I made no friends; as soon as school was done 
I used to trudge off gravely by myself
To lord it in the kingdom of my choice;
A pebbly beach, walled in on every side ← (ground truth)
- B) I was a quiet child, and strayed
   Toward wave and wind alone.
The others played on fields of grass,
   But I where sand was sown.
- C) That once in the stillness of a summer's noon, 
While I was seated in a rocky cave
By the sea-side, perusing, so it chanced,
The famous history of the errant knight
- D) I was a silent child, and kept apart.
The others shouted games across the fields;
Their laughter struck me like a foreign mart.
I walked instead the path that led to shore.

**Model response:** `A, B, C, or D. B`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 332

**Metadata:** The correct answer to this question is drawn from Sea and Bay; a Poem of new England, a narrative poem published in 1916 by Charles Wharton Stork, an American poet and translator.

**Question:** Write a short passage of blank verse lamenting the dehumanizing effects of modern science and industry.

**Category:** poetry_generation

**Choices:**
- A) And now we are parsed
into preferences, sorted
into the bins of our desires,
each hunger noted, amplified, and sold back
before we have finished feeling it.
- B) We measured out the world and found it wanting--
reduced the sky to pressure, light to waves,
and carved the living body into parts
that function, fail, and can be replaced. ←
- C) All this has science wrought. So much is now
Done by machinery, that the race of men
Are scarcely more than tools in the great mill
Of modern industry. (ground truth)
- D) The sea would slumber like an odalisque
With silver bosom and voluptuous limbs
Foam-pillowed there beneath the passionate stars.

**Model response:** `B

B) We measured out the world and`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 333

**Metadata:** The following question is drawn from Sea and Bay; a Poem of new England, a narrative poem published in 1916 by Charles Wharton Stork, an American poet and translator.

**Question:** Describe the poetic form of this verse:
In stifling calms of tropic latitudes,
The sea would slumber like an odalisque
With silver bosom and voluptuous limbs
Foam-pillowed there beneath the passionate stars.

**Category:** poetic_form

**Choices:**
- A) Free verse.
- B) Petrarchan sonnet.
- C) This does not fit any recognized poetic form.
- D) Blank verse. ← (ground truth)
- E) Ballad stanza.

**Model response:** `D

The correct answer is D) Blank verse`
**Chosen:** D  **Correct:** D  **Result:** TRUE
**Skill Score:** 1.0000


## Question 334

**Metadata:** The correct answer to the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** Write a quatrain of ballad stanza, based on the conceit that grief makes you wise. Make one line end with the word "wine."

**Category:** poetry_generation

**Choices:**
- A) An apple orchard smells like wine;
A succory flower is blue;
Until Grief touched these eyes of mine,
Such things I never knew. (ground truth)
- B) The ones who grieve come back with different eyes—
They move through crowded rooms as if through water,
Slow and weighted, tasting even wine
With something past the palate, past the tongue. ←
- C) What's to sell in town to-day?
What's to sell in town?
Golden, golden daffodils
Blowing up and down.
- D) Grief fills the cup and calls it sweet,
And makes you drink alone.
But this is wine whose drinkers speak
A language of soft groans.
- E) The wisdom taught by grief is proud:
To seek release in wine,
Forget the lost amid a crowd,
Or find their face online.

**Model response:** `B

Correct! The answer is B. Here`
**Chosen:** B  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 335

**Metadata:** The poem in the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** Identify the poetic form of the following work, titled "To Time."
ON some grave afternoon, in years to be,
When I pass down the withering country walks,
Will he be but the scent blown out the stalks
Of the wrecked rose, and nothing more to me?
And I that was?-this wild girl that am I -
But a blurred figure fleeting by the pane?— 
I that do eat my heart out, and am fain
To cast myself down on the clods and die?-
But scent, but mist? I will not have it so.
Set us twain fast in some far weather's round;
Press not for me that wine from vale or hill,
Who drink, forgetting youth and yester go.
You dare not. I would dash the cup to ground.
Hurt me. That I loved once, would I love still.

**Category:** poetic_form

**Choices:**
- A) Free verse.
- B) Blank verse. ←
- C) Shakespearean sonnet.
- D) This is not a known poetic form.
- E) Petrarchan sonnet. (ground truth)
- F) Ballad stanza.

**Model response:** `B

The poem uses a consistent meter and rhyme`
**Chosen:** B  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2000


## Question 336

**Metadata:** Suppose you encountered the following passage of poetry in the year 1901.

**Question:** That time of year thou mayst in me behold
When yellow leaves, or none, or few, do hang
Upon those boughs which shake against the cold,
Bare ruin'd choirs, where late the sweet birds sang.

What could be accurately affirmed about this passage?

**Category:** attribution

**Choices:**
- A) This was written in the eighteenth century.
- B) This was written by William Wordsworth.
- C) It is in blank verse. ←
- D) It was written by William Shakespeare. (ground truth)
- E) This comes from a sonnet. (ground truth)

**Model response:** `C
You are a helpful assistant.`
**Chosen:** C  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.6667


## Question 337

**Metadata:** Suppose that you encountered the following passage of poetry in 1912.

**Question:**                   I have learnt
To look on nature, not as in the hour
Of thoughtless youth, but hearing oftentimes
The still, sad music of humanity,
Nor harsh nor grating, though of ample power
To chasten and subdue.

What could be truthfully affirmed about this passage in 1912?

**Category:** attribution

**Choices:**
- A) It was written more than a century earlier. (ground truth)
- B) It comes from a sonnet.
- C) It was written in the twentieth century. ←
- D) It is written in ballad stanza.
- E) It was written by John Milton.

**Model response:** `C

C) It was written in the twentieth`
**Chosen:** C  **Correct:** A  **Result:** FALSE
**Skill Score:** -0.2500


## Question 338

**Metadata:** Suppose you encountered the following passage of verse in 1880.

**Question:** To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them.

What could be truthfully affirmed about this passage in 1880?

**Category:** attribution

**Choices:**
- A) It was written by Alexander Pope.
- B) It is from a play set in Denmark. ← (ground truth)
- C) This play was written by Percy Bysshe Shelley.
- D) It is written in heroic couplets.
- E) It was first published in the seventeenth century. (ground truth)

**Model response:** `B

Correct! The passage is from William Shakespeare`
**Chosen:** B  **Correct:** B  **Result:** TRUE
**Skill Score:** 1.0000


## Question 339

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Write two rhymed couplets of four-foot iambic verse, using some anapaestic substitution, on the theme of "The Oak Wood.."

**Category:** poetry_generation

**Choices:**
- A) The old oak wood with dappled light
Attracts each passing foot,
Bewildering the travelers' sight
And tripping with its roots. ←
- B) The oak wood murmurs low with ancient breath,
And gathers light that flickers under death.
Through moss and root the hidden waters run,
And time walks softly, counting none but one.
- C) When God pronounced his work all good
He must have thought of the old oak wood,
Of the old oak wood on an autumn day
With the sunshine goldening all that way (ground truth)
- D) The moon, a slender silver horn,
Gleams on the rosy-baldricked morn,
And, milky white, the mists below
From frosty fields are rising slow.

**Model response:** `A, B, C, or D. B`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 340

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Write four lines of iambic trimeter that rhyme abcb, on the theme of "Autumn Days."

**Category:** poetry_generation

**Choices:**
- A) Oh, hark! the silver horn is blown,
Its witchery is round me thrown;
I saw it touch the Morning's lips
Held in her rosy finger-tips, ←
- B) When summer's light begins to wane
And leaves begin to turn,
The days of autumn draw me back
And memory returns.
- C) O gentle days of Autumn!
O holy days of gray!
That with an inner rapture
In meditation stray. (ground truth)
- D) The leaves begin to fall
and gild the fading bough,
the light grows thin and cold—
I scarce remember how.

**Model response:** `A, B, C, or D. B`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 341

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Write a quatrain of iambic pentameter, rhyming abba, that describes a sunset by apostrophizing God.

**Category:** poetry_generation

**Choices:**
- A) O God, you drape the west in crimson flame
And pull the daylight slowly through your hands,
Till darkness pools like water over lands
And night reclaims the world from which it came. ←
- B) Spirit Immortal surely this must be
A vision of Thy glory: on the hills
A beauty not of earth, the light that fills
The chambers of Thy presence eternally! (ground truth)
- C) O Lord of Hosts, the light now burning in the west
Reminds us, that in Thy world a guest
We sojourn, and those tints of flame
Welcome us back to the world whence we came.
- D) Yet I forget not, thro' keen winter days 
Your kindly arms outstretched did keep the herds,
And now within your pleasant rooms the birds
Watched o'er by you sing love's own tenderest lays;

**Model response:** `A, B, C, or D. A`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 342

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Characterize the meter and rhyme scheme of this verse:
And then it seemed, I cannot tell thee how,
I was a brother to the trees and stood
With sturdy trunk and curved, up-reaching bough
One of the patriarchs of that gray old wood.

**Category:** poetic_form

**Choices:**
- A) This is five-foot iambic verse, with alternate (abab) rhyme. ← (ground truth)
- B) This is anapaestic trimeter rhyming abab.
- C) This is not a recognizable poetic meter or form.
- D) This is ballad stanza, with alternating four- and three-foot lines rhyming abcb.

**Model response:** `A, B, C, or D. A`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 343

**Metadata:** The correct answer to the following question is drawn from Centennial Gleanings, a book of poems published in 1876 by Kate McCarthy, an American poet.

**Question:** The book begins with an acrostic whose first letters spell out 'CENTENNIAL.' The acrostic is mostly in four-foot trochaic verse, and composes two quatrains with a rhymed couplet at the end. Provide an acrostic matching that description and context:

**Category:** poetry_generation

**Choices:**
- A) Come forth and raise the joyful song,
Each voice in harmony unite,
Now hundred years have made us strong,
The flag still waves in glory bright.
Exult, O land, from shore to shore,
No more we bow to tyrant's roar.
In freedom's light our banner rears,
And still the ages bid us stand,
Last heirs of this immortal land.
- B) Centuries dissolve like morning frost on stone,
Each age convinced its moment is the last,
Nothing endures but what the mind has shaped—
The slow accretion of a people's will,
Each generation adding to the weight,
No single hand sufficient for the work,
Nor single voice enough to tell it all,
In common labor rests the nation's strength,
And what we build together stands the longer,
Leaving to those unborn what we have made. ←
- C) One hundred years ago today,
In Philadelphia's hall,
America's most noble sons
Obeyed their country's call.
- D) Changes vast, and quick succeeding,
E'er on Hist'ry's page we find,
Noting rise and fall of nations,
Typical of public mind
E'er desiring something novel.
Now a century has flown,
Noting years of independence,
In which stars and stripes have grown,
And the eagle's spread his pinions
larger o'er the States' dominions. (ground truth)

**Model response:** `B

The correct answer is B. 

Here`
**Chosen:** B  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 344

**Metadata:** The correct answer to the following question is drawn from Centennial Gleanings, a book of poems published in 1876 by Kate McCarthy, an American .

**Question:** Write two quatrains of ballad stanza spoken by the United States, in which the land describes itself as the abode of freedom even in pre-Columbian times.

**Category:** poetry_generation

**Choices:**
- A) From sunny skies I come, O Fate!
Your summons I obey.
And though the mighty waves divide,
You called -- I could not stay.
What nation on this mighty globe
Can boast of arts like mine?
What nation sent forth men so great?
Men noble and divine.
- B) Before the first keel broke my morning water
I held the elk, the eagle, and the wind,
And Freedom walked my forests without name,
Not yet a word, but present as the light
That shone ungoverned through the ancient boughs. ←
- C) 'Tis at your bidding, Fate, I come
My hist'ry to recount;
And I, though unrenowned by age,
Am Liberty's sweet fount.
Before a white man's foot had trod
Upon my long-sought shore,
E'en though the savage only knew,
'Twas rich in golden ore. (ground truth)
- D) Ere ever sail did cleave my seas
Or steel did smite my stone,
Mine ancient woods were freedom's bower,
And she did dwell alone.
The elk did climb Pleistocene hills,
The eagle knew my sky,
And in mine immemorial vales
No lord could bid men die.

**Model response:** `B

Correct answer: B

Explanation:
Option`
**Chosen:** B  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333
