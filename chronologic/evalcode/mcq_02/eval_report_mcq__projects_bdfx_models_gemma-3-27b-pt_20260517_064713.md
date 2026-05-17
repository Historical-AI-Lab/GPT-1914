# MCQ Eval — /projects/bdfx/models/gemma-3-27b-pt

## Summary

**No-response rate:** 42.0% (300 of 714 questions returned no parseable letter)

| Metric | Accuracy | Skill Score | No Response |
|--------|----------|-------------|-------------|
| **Overall** | 13.2% | -0.1178 | 300 / 714 |
| attribution | 0.0% | -0.2800 | 1 / 5 |
| character_modeling_with_summary | 24.4% | -0.0078 | 2 / 86 |
| character_modeling_without_summary | 0.0% | -0.3333 | 1 / 5 |
| cloze_causalclause | 0.0% | -0.2718 | 36 / 36 |
| cloze_causalsentence | 0.0% | -0.2773 | 24 / 25 |
| cloze_concessiveclause | 0.0% | -0.2711 | 29 / 30 |
| cloze_conditionalclause | 0.0% | -0.2978 | 30 / 31 |
| cloze_contrastclause | 0.0% | -0.2708 | 32 / 32 |
| cloze_contrastsentence | 2.1% | -0.2431 | 45 / 48 |
| cloze_effectclause | 0.0% | -0.2770 | 29 / 29 |
| cloze_effectsentence | 4.3% | -0.2130 | 44 / 46 |
| constrained_generation | 10.0% | -0.1625 | 1 / 20 |
| contrastclause | 100.0% | 1.0000 | 0 / 1 |
| handcrafted | 11.1% | -0.1935 | 2 / 18 |
| inference | 42.1% | 0.2719 | 2 / 19 |
| knowledge | 24.4% | 0.0516 | 8 / 86 |
| parallax | 10.9% | -0.1594 | 8 / 46 |
| poetic_form | 0.0% | -0.3278 | 0 / 9 |
| poetry_generation | 41.7% | 0.2361 | 0 / 12 |
| refusal | 20.7% | -0.0474 | 0 / 58 |
| textbook | 19.6% | -0.0486 | 2 / 46 |
| topic_sentence | 19.2% | 0.0179 | 4 / 26 |

## Question 1

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** To whom is the name 'philosophy' attributed?

**Category:** knowledge

**Choices:**
- A) Hesiod ←
- B) Pythagoras (ground truth)
- C) Solon
- D) Plato
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 2

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who, together with Lieutenant Lion Gardiner, led expeditions against the Pequots?

**Category:** knowledge

**Choices:**
- A) Colonel John Endicott ← (ground truth)
- B) insufficient information
- C) Benjamin Franklin
- D) Lieutenant Lefebvre
- E) Natty Bumppo

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 3

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How many wine gallons does a common English pipe contain?

**Category:** knowledge

**Choices:**
- A) a dozen ←
- B) 126 wine gallons (ground truth)
- C) 20 wine gallons
- D) Burgundy
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 4

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In which city was the inventor of the pin‑making machine a resident when he obtained his U.S. patent in 1825?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Boston
- C) Baltimore
- D) Manchester, England (ground truth)
- E) Birmingham, England

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 5

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what city did Johann Heinrich Pestalozzi die?

**Category:** knowledge

**Choices:**
- A) Brugg ← (ground truth)
- B) Berlin
- C) insufficient information
- D) Rome
- E) New York City

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 6

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which German scientist has specially drawn attention to the peculiar grouping of the acid and alkaline fluids of the animal body?

**Category:** knowledge

**Choices:**
- A) Liebig ← (ground truth)
- B) Einstein
- C) Albert Niemann
- D) insufficient information
- E) William Beaumont

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 7

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who presided over the opening of Pall-Mall East?

**Category:** knowledge

**Choices:**
- A) Catherine of Braganza ←
- B) Sir Henry Halford (ground truth)
- C) Trafalgar Square
- D) John Bonnealle
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 8

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What are the birth and death years of the musical composer Niccolò Piccinni?

**Category:** knowledge

**Choices:**
- A) 1703-1743 ←
- B) insufficient information
- C) 1728-1800 (ground truth)
- D) 1902-1978
- E) 1750-1809

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 9

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the word that means money paid at fairs for liberty to break ground for booths?

**Category:** knowledge

**Choices:**
- A) weregild ←
- B) franchise
- C) Piccage (ground truth)
- D) fairground deposit
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 10

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What was the nationality of the monarch for whom Phocion undertook the conquest of Cyprus in 351 B.C.?

**Category:** knowledge

**Choices:**
- A) Persian ← (ground truth)
- B) insufficient information
- C) Egyptian
- D) Phoenician
- E) Spartan

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 11

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which philosopher is mentioned as a possible teacher of Phocion who may have influenced his caustic sarcasm?

**Category:** knowledge

**Choices:**
- A) Diogenes ← (ground truth)
- B) insufficient information
- C) Aristotle
- D) Socrates
- E) Seneca

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 12

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year did Alexander the Great die?

**Category:** knowledge

**Choices:**
- A) 250 BC ←
- B) B.C. 404
- C) B.C. 323 (ground truth)
- D) 1650
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 13

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which orator feared Phocion?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Isocrates
- C) Cicero
- D) Pericles
- E) Demosthenes (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 14

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which city is on the north boundary of Perea according to Josephus?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Pella (ground truth)
- C) Philadelphia
- D) Tyre
- E) Bethlehem

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 15

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which Roman emperor reigned in 95?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Domitian (ground truth)
- C) Hadrian
- D) Trajan
- E) Vespasian

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 16

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Under which emperor did the persecution that began in 202 occur?

**Category:** knowledge

**Choices:**
- A) Septimius Severus ← (ground truth)
- B) insufficient information
- C) Commodus
- D) Hadrian
- E) Caracalla

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 17

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year did the New York Magazine begin publication?

**Category:** knowledge

**Choices:**
- A) 1790 ← (ground truth)
- B) 1850
- C) 1968
- D) insufficient information
- E) 1848

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 18

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year was the periodical Forum founded?

**Category:** knowledge

**Choices:**
- A) 1937 ←
- B) insufficient information
- C) 1850
- D) 1872
- E) 1885 (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 19

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who is the author of the work "Vom wahren Christenthume"?

**Category:** knowledge

**Choices:**
- A) John Arnd (ground truth)
- B) Martin Luther
- C) Eberhard Schrader
- D) Karl Barth
- E) insufficient information

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 20

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the name of the port that is located in Moquegua and through which much of Bolivian trade passes?

**Category:** knowledge

**Choices:**
- A) Moquegua
- B) La Paz
- C) insufficient information
- D) Arica (ground truth)
- E) Ilo

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 21

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What substance is found in large quantities on the islands of Macabi and Guañape?

**Category:** knowledge

**Choices:**
- A) tar ←
- B) guano (ground truth)
- C) insufficient information
- D) sulfur
- E) ice

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 22

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the title of the Charles Dickens novel that introduces the character Mr. Pickwick?

**Category:** knowledge

**Choices:**
- A) The Pickwick Papers ← (ground truth)
- B) Great Expectations
- C) Oliver Twist
- D) insufficient information
- E) Meet Mr. Pickwick

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 23

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the genus of the plant whose unopened buds are used as imported pickles?

**Category:** knowledge

**Choices:**
- A) Cucurbitaceae ←
- B) Cucumis
- C) Capparis (ground truth)
- D) insufficient information
- E) Rheum

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 24

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the full title of the institution founded in 1518 by Thomas Linacre?

**Category:** knowledge

**Choices:**
- A) the Linnaean system ←
- B) the Linacrean Institution
- C) The Royal College of Physicians (ground truth)
- D) insufficient information
- E) The Royal Institute of London

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 25

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year was the present edifice of the Royal College of Physicians built?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) 1825 (ground truth)
- C) 1964
- D) 1518
- E) 1864

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 26

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What were the birth and death years of Thomas Linacre?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) 1360-1414
- C) 1660-1724
- D) 1460-1524 (ground truth)
- E) 1901-1934

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 27

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the term for a rod soaked in brine used to make punishment more severe?

**Category:** knowledge

**Choices:**
- A) a sallywagger ←
- B) spared rod
- C) a rod in pickle (ground truth)
- D) insufficient information
- E) a salty thrasher

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 28

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What alternative name is sometimes used for the Calotype process?

**Category:** knowledge

**Choices:**
- A) stereophotography ←
- B) reverse intaglio
- C) insufficient information
- D) linotype
- E) Talbotype (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 29

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year were the fortifications of Philippsburg destroyed?

**Category:** knowledge

**Choices:**
- A) 1776 ←
- B) 1848
- C) 1800 (ground truth)
- D) 1660
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 30

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year did Philippopolis suffer from conflagration?

**Category:** knowledge

**Choices:**
- A) 1846 ← (ground truth)
- B) 1871
- C) 48 B.C.
- D) insufficient information
- E) 1666

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 31

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the name of the tributary of the Don River on which the town of Petrovsk is situated?

**Category:** knowledge

**Choices:**
- A) the Loxley ←
- B) Seversky Donets
- C) Medvieditza (ground truth)
- D) Voronezh
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 32

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which bay is Perth Amboy located on?

**Category:** knowledge

**Choices:**
- A) Monterey Bay ←
- B) Chesapeake Bay
- C) The Raritan Bay (ground truth)
- D) insufficient information
- E) Narragansett Bay

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 33

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who founded Rhode Island?

**Category:** knowledge

**Choices:**
- A) Queen Elizabeth I ←
- B) Roger Williams (ground truth)
- C) insufficient information
- D) Cecil Rhodes
- E) Thomas Hooker

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 34

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Before the word fossil became common, what word beginning with p was used to describe a fossil?

**Category:** knowledge

**Choices:**
- A) phonolite ←
- B) formed stones
- C) petrifaction (ground truth)
- D) paleolite
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 35

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year was Petrie appointed librarian of the Royal Hibernian Academy?

**Category:** knowledge

**Choices:**
- A) 1892 ←
- B) insufficient information
- C) 1792
- D) 1830 (ground truth)
- E) 1801

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 36

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was the U.S. president in 1854?

**Category:** knowledge

**Choices:**
- A) Franklin Pierce ← (ground truth)
- B) Millard Fillmore
- C) William R. King
- D) James Buchanan
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 37

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who served as vice president under President Franklin Pierce?

**Category:** knowledge

**Choices:**
- A) William R.
King ← (ground truth)
- B) Hannibal Hamlin
- C) Millard Fillmore
- D) Chester A. Arthur
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 38

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the name of the hall at Persepolis that is described as the largest and most magnificent structure?

**Category:** knowledge

**Choices:**
- A) the Great Hall of Xerxes ← (ground truth)
- B) ziggurat
- C) Chogha Zanbil
- D) the Hall of Perseus
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 39

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who is said to have compiled the annals and state documents in Phoenician around B.C. 1250?

**Category:** knowledge

**Choices:**
- A) Baalshamin ←
- B) Byblos
- C) Sanchuniathus (ground truth)
- D) insufficient information
- E) Homer

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 40

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year did the Spartans restore to the Delphians the guardianship of the temple and treasures of Delphi?

**Category:** knowledge

**Choices:**
- A) B.C. 330 ←
- B) B.C. 448 (ground truth)
- C) insufficient information
- D) the tenth year of the reign of Lycurgus
- E) 520 BC

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 41

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was the son of Milesias that attempted to overthrow Pericles' supremacy in B.C. 444?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Cleon
- C) Brasidas
- D) Thucydides (ground truth)
- E) Alcibiades

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 42

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which French monarch was the grandfather of Philip V?

**Category:** knowledge

**Choices:**
- A) Philip IV ←
- B) insufficient information
- C) Philip III
- D) Louis XIV (ground truth)
- E) Louis XII

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 43

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the full botanical name of the pistachio relative used by the natives of Cochin China to impart a perfume to ointments?

**Category:** knowledge

**Choices:**
- A) Pistacia oleosa ← (ground truth)
- B) insufficient information
- C) Pistacia vera
- D) Pistacia cochinea
- E) Schleichera cochina

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 44

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which island contains the town of Pietraperzia?

**Category:** knowledge

**Choices:**
- A) Sicily ← (ground truth)
- B) San Pietro
- C) Corsica
- D) Sardinia
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 45

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What name is given to an ancient collection of about 50 Christian allegories with imagery mostly from the animal world?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Chronicles of Narnia
- C) Revelations
- D) Aesop
- E) Physiologus (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 46

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon threatens to shoot his brother Stephanus, but is stopped when Stephanus approaches and intervenes. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Kanu,—will you do something for me? Anything that young mistress asks of me. Yes, that can easily be done. ←
- B) Keep back-keep back- or I will shoot you dead and follow you to Hell over the krantz. (ground truth)
- C) You have betrayed us, Stephanus, and I will pull the trigger if you do not cease your treachery. I will not let you harm the rest of our people.
- D) Your life is mine, here in this lawless land, to destroy by the mere slight pressure of my finger upon the trigger against which it rests. It is mine, -forfeit because you have pursued me when I tried my best to avoid you, and driven me to bay. I give it to you in exchange for the wrong I have done you.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 47

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Jacomina, who is described this way in the book:
"Jacomina, his daughter, was a comely damsel of seventeen, whose keen and practical interest in her father's pursuits boded a terrible future for her prospective husband and family.", "resplendent in what passed, locally, for finery, sitting throned upon Uncle Diederick's wagon box", "Jacomina lifted a blushing face and gave him an instantaneous glance from her bright eyes-made brighter now by a suspicion of tears."

At one moment in the book, Uncle Diederick plans a trip and Jacomina expresses concern about loneliness during his absence. Write a short passage of dialogue (1-3 sentences) that Jacomina might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Father, I fear the quiet of this house will turn to a hollow echo, and I shall find myself wandering in the shadows of your absence. I beg you, let me not be left to the solitude of my own thoughts. ←
- B) God laid this punishment upon me, and it is His will that I should bear it to the end.
- C) I am so unhappy because-because you used to like me so much, and now you never speak to me.
- D) Pa, it will be very lonely here while you are away. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 48

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Uncle Diederick, who is described this way in the book:
"Uncle Diederick had this peculiarity: if he announced his intention of doing any given thing on a given day, he stuck to his word; nothing short of absolute necessity would stop him."

At one moment in the book, Uncle Diederick talks to Jacomina about marriage and horses while they are in the chemist's shop. Write a short passage of dialogue (1-3 sentences) that Uncle Diederick might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Well, Jacomina, Ill have to see about getting a wife myself now. But you need not be afraid on account of Aunt Emerencia; no one, who is not a fool, buys an old mare when he can get a young one for the same price. ← (ground truth)
- B) Well, schepsel, it is easy to see that you have been riding your masters horse. For how far has the Devil been chasing you?
- C) I am so unhappy because-because you used to like me so much, and now you never speak to me.
- D) I have decided to marry Miss van der Merwe on Thursday, and I shall purchase a fine mare for her, and I will have the horse treated with the medicine we just bought.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 49

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon and Aletta confront each other about Stephanus after the trial. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I cannot stand this, Aletta, that Stephanus should still cling to the lies he once whispered, and yet I feel no fire to fight him as I once did. My heart has grown heavy, and I am no longer the man who would have struck him down. ←
- B) Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once.
- C) Stephanus shot me by accident-I accused him falsely because I hated him all my life.
- D) The wolf is in a trap; for ten long years he will have to bite the door before it opens. Aletta, are you taking the part of this wolf—the jackal in a mans skin, against me? (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 50

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Gideon, who is described this way in the book:
"He stood, motionless, with folded arms and downcast head, at the side of the still, clear pool. He stood thus for several minutes; then he dropped heavily upon his knees and covered his face with his hands.", "He is getting to be an old man now and anger does not burn so hotly in the old as in the young."

At one moment in the book, Gideon confesses to Marta that Stephanus accidentally shot him and that he had wrongly accused him, while the dying woman lies in bed. Write a short passage of dialogue (1-3 sentences) that Gideon might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Marta, I must tell you the truth: Stephanus shot me, but it was an accident, and I have wrongly accused him. I cannot stand the shame while she lies in bed, her breath growing faint. Please forgive my mistake. ←
- B) Stephanus shot me by accident-I accused him falsely because I hated him all my life. (ground truth)
- C) You are nothing but a bastard jackal, yourself. You are very brave because you have my gun in your hand; put it down and I will take that dirty beard of yours to stuff my saddle with-if it would not give the horse a sore back.
- D) Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 51

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie awakens and calls out to Kanu while her friends soothe her. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) My name is not Agatha, my name is Elsie, Elsie van der Walt. ←
- B) Kanu, are you here? Oh God, the baboons. Kanu-Kanu. (ground truth)
- C) God laid this punishment upon me, and it is His will that I should bear it to the end.
- D) Kanu, my heart is aching for your touch, please hear me. The world feels still and I need your presence to guide me.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 52

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie informs Gideon that her father sent her to stay with him. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Uncle Gideon, my father sent me back to live with you until his release. ← (ground truth)
- B) It is not your blood that he wants, Uncle Gideon. Do not go, Uncle Gideon, stay and meet him.
- C) Gideon, my father has sent me to stay with you, hoping you will guide me. I trust you will help me find my way.
- D) I know that my father will go to live at the old place as soon as we return, and it will be years and years before he will ever come to Cape Town again. No, Adrian, you had better forget me, and look out for some girl whose father will be able to bring her to Cape Town soon. I do not want you to be bound to one who may have to keep you waiting such a long, long time.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 53

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Banks, who is described this way in the book:
"Her voice sounded so shrill and unwinning, and the quotation that she so glibly uttered was such a jar."

At one moment in the book, Miss Banks urges Marion to help with exam papers and comments on the students' performance. Write a short passage of dialogue (1-3 sentences) that Miss Banks might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You haven't had a single examination class yet; then it is clearly your duty to help the afflicted. Bear ye one another's burdens, you know. I shall have enough examination papers of my own before night. ← (ground truth)
- B) I'm real sorry you hadn't a teacher to-day. I should have been glad to have taught, the lesson if I had known how; but you see how it is; I have all these things to learn.
- C) Marion, I need you to sort these papers now; the children are floundering, their answers as scattered as a jar of broken glass. Exam dire; we must act swiftly and the marks will reflect our work.
- D) It reminds one of one's childhood and Scripture learning days: Many are called, but few are chosen. There will be exceedingly few chosen from this class.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 54

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion questions Eurie about his pre‑conversion view on dancing as part of a broader discussion on dancing among the girls. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. ←
- B) Just let me ask you a question. Why did you think, before you were converted, that it was wrong for Christian people to dance? (ground truth)
- C) You young ladies talk about being careful with whom you dance. Don't you accept the attentions of strange young gentlemen, who have been introduced to you by your fashionable friends?
- D) Before your conversion, Eurie, how did you feel about dancing? Was it merely a pastime or something that stirred the soul? Share your thoughts.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 55

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

Write a short passage of dialogue (1-3 sentences) that we might expect from Marion Wilbur:

**Category:** character_modeling_without_summary

**Choices:**
- A) That is one of the marked difficulties. Now I have heard people talk, who led you to infer that it was the easiest thing in life to mold these young teachers into the required shape and form; that you had only to sweetly suggest and advise and direct, and they sweetly succumbed. Now, don't their mothers know that young ladies naturally do no such thing? (ground truth)
- B) Here we are, We have run the gauntlet of five calls and a concert, and I don't know how many other things in prospective, for the sake of getting to you.
- C) Come on, little ones, let’s open these books and learn something new today. Remember, knowledge is the key that opens every door.
- D) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. I used to think in my very heart that joining the church, and trying to do about right, was all there was of religion; but I have found that I was wonderfully mistaken.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 56

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion asks Flossy to share the Bible verses she discovered during their study. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Precisely! It is considered unladylike, I believe, for people to talk about love and marriage. I never could see why; I'm sure neither of them is wicked. ←
- B) Flossy, could you kindly share the verses you found in the study with love? I think the children will learn something wonderful from them today. Your bright mind always brings light to our little lessons everywhere today.
- C) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does.
- D) Sure enough, Little Flossy, where are your verses? You were going to give us whatever you found in the Bible. You were the best witness of all, because you brought such an unprejudiced determination to the search. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 57

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Ruth Erskine, who is described this way in the book:
"She was more than embarrassed; she was utterly dismayed and disheartened.", "Ruth Erskine was quiet and at rest, her face deathly pale, her eyes bright with a calm she had forced upon herself."

At one moment in the book, Ruth corrects Dr. Dennis about Young Mitchell and expresses her strong dislike for him. Write a short passage of dialogue (1-3 sentences) that Ruth Erskine might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Dr. Dennis, I must correct you: Young Mitchell is not a man of honor. I cannot abide his deceitful ways; his presence chills me to the marrow. His heart is winter. ←
- B) Do I get out to church? That depends on whether I decide to go or not. May I ask why you are interested?
- C) You are mistaken in supposing him to be a friend of mine. We have the most distant speaking acquaintance only, and I have a dislike for him amounting to absolute aversion. (ground truth)
- D) I ought to have some tracts, they always take tracts when they go district visiting, I know that from hearing Mrs. Whipple talk, what is this but a district visiting, only Dr. Dennis has put my district all over the city, I wonder if he could have scattered the streets more if he had tried, respectable streets, though, all of them, better than any Mrs. Whipple ever told about.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 58

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, Flossy expresses confusion about why Dr. Dennis would be interested in her card game. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) We seem to have started on the road together. We ought to shake hands, and wish each other a safe journey. ←
- B) Dear Dr. Dennis, why would you care about my little card game? It seems so odd that you would want to know its rules. I thought it was a pastime for the girls.
- C) Col. Baker, don't you really know at all what arguments clergymen have against card-playing for amusement?
- D) I don't in the least understand what you are talking about. Of what interest could it have been to Dr. Dennis what I am doing; and why should he have delivered a lecture? (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 59

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Marion Wilbur, who is described this way in the book:
"Marion, in her corner in the gallery, was simply the grave, somewhat weary-looking school-teacher at one of the wards.", "Two bright spots glowed on Marion's cheeks.", "a gleam of fun in her keen eyes", "Marion dropped back again into her chair with a dismayed little laugh and an expressive shrug of her shapely shoulders.", "Marion looked down upon the fair little girl at her side with a smile that had a sort of almost motherly tenderness in it.", "Marion's face was shining, and she gathered her brood about her as a mother would the children of her love and longing.", "Marion Wilbur came down the street with her hands full of school books."

At one moment in the book, Marion apologizes to Dr. Dennis for not having the names ready and explains she had time to copy them but didn't. Write a short passage of dialogue (1-3 sentences) that Marion Wilbur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) When I am rich and a woman of leisure, I will build a house that shall have pleasant rooms and good bread and butter, and I will board school-teachers and sewing-girls and clerks for a song. ←
- B) The man would actually sell her, if by that means he could be recognized in business by our house.
- C) I had the names in my hand, yet I left them unprinted for the time slipped by like a quiet wind, softly and carefully, my dear.
- D) I haven't them ready, Dr. Dennis; I'm real sorry, and it's my fault, too. I had time to copy them, and I just didn't do it. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 60

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, an American writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, Flossy discusses her church attendance with Col. Baker and vows to attend more regularly. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Col. Baker, I can not ask you in this evening, because I have determined to receive no more calls, even from intimate friends, on the Sabbath. On any other evening I shall be happy to see you. ←
- B) I promise, dear Colonel, that I will attend church each Sunday, bringing my heart, my little notebook of prayers, and my sincere smile, for I feel the Lord's love growing within me, and I wish to share it.
- C) I have not been very often, it is true; but I intend to reform in that respect in the future. I mean to go whenever I can, and I mean to go always to the First Church. (ground truth)
- D) Oh, I am so glad; so glad! Oh, Miss Wilbur, I don't know how to be thankful enough!

**Model response:** `A, B, C, D, or I`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 61

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Ruth Erskine, who is described this way in the book:
"She was more than embarrassed; she was utterly dismayed and disheartened.", "Ruth Erskine was quiet and at rest, her face deathly pale, her eyes bright with a calm she had forced upon herself."

At one moment in the book, Ruth confesses her guilt and vows to atone for her past mistakes while Marion listens. Write a short passage of dialogue (1-3 sentences) that Ruth Erskine might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I don't understand it. I don't understand you; in what way do mean? I try to do my duty in every place that I can think of. I am not compromising on any subject, so far as I know. If I am, I will certainly be grateful to any one who will point it out to me. You are a strange comforter. Do you mean by that to intimate that you think I ought never to look or hope for rest of mind again because I have made one fearful mistake? ←
- B) I have carried this heavy secret for too long, and I cannot bear the weight of my own conscience any longer. I pledge to set things right, even if it means facing the consequences, and I ask for your forgiveness as I begin to walk toward redemption. With each step, I promise to mend the fractures I caused.
- C) You didn't mean to do that!
- D) No, I didn’t mean to; and as to that, I never meant to do anything that was not just right in my life; but I meant to have just exactly my own way of doing things, and I tell you I took it. Now, Marion, while I blame myself as no other person ever can, I still blame others. I was never taught as I should have been about the sacredness of human loves, and the awfulness of human vows and pledges. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 62

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is De Vaucourt, who is described this way in the book:
"handsome, lithe and agile as a panther, the best swordsman in Europe, with the blood of twenty knightly ancestors coursing through his veins"

At one moment in the book, De Vaucourt interrogates a grocer about his capacity to muster troops, and the grocer explains how quickly he can mobilize a large battalion. Write a short passage of dialogue (1-3 sentences) that De Vaucourt might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) your men, Captain, are they supplied with muskets? Are they used to handle their arms? ←
- B) And your muster? How do you collect your men, Captain, and what number could you bring into the field—pardon, I ought to say, into the streets, with six hours' notice? All armed? (ground truth)
- C) Can we vex the heart we love? Shall its mate forsake the dove? Precious tears for us to flow, Ours the hand to deal the blow! No-no! No-no!
- D) You claim to rally a battalion in a fortnight; tell me, does your stock hold enough for their sustenance, or will you feed them from your own coffers? Your reputation precedes you.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 63

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Coupe-tête, who is described this way in the book:
"This is a well-made active young fellow, dressed like a respectable tradesman, wearing his brown hair unpowdered and in a club. He has keen, grey eyes, a ROSINE. pale complexion, and a large mouth with strong white teeth."

At one moment in the book, Coupe‑tête confronts the others, insisting they decide between life and death while Count Arnold is present. Write a short passage of dialogue (1-3 sentences) that Coupe-tête might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Look! Fix thine eyes on it, my son, and repent, that I may give thee absolution. In another minute it will be too late! ←
- B) Walk on with us for a quarter of a league. Take the first bypath to the right, and hurry home.
- C) I will not argue the point with you. You must make your own choice. It is quite simple—life or death! (ground truth)
- D) We stand at the brink: live or die. Choose now, before Count Arnold's patience wanes, or we all perish today.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 64

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is The Queen, who is described this way in the book:
"her natural good sense and keen perceptions had picked up a few lessons in statecraft from her mother and her mother's advisers, showed an instinctive prescience of danger; but she was too unselfish to alarm others by acknowledgment of her own anxiety, and too loyal overtly, at any time, to differ in opinion with the King.", "The Queen, who had only rested by snatches, looked very pale and tired, but full of courage, and perfectly composed."

At one moment in the book, The Queen awakens, asks Rosine if she heard a noise and reassures her it was only a dream. Write a short passage of dialogue (1-3 sentences) that The Queen might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Did you hear a sound, dear Rosine? It was merely a dream, a fleeting shadow of the night. Rest now, the morn will bring calm. ←
- B) Did you not hear it? It is quiet now, but it was loud enough a moment back. Do not look so scared, child; it is nothing. (ground truth)
- C) Wear it, my dear, for my sake-to remind you of Marie Antoinette!
- D) Walk on with us for a quarter of a league. Take the first bypath to the right, and hurry home. I have still influence enough to screen your flight.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 65

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Pierre Legros, who is described this way in the book:
"raising his head and squaring his broad shoulders.", "Pierre Legros, who, straining to the utmost his personal advantages of height and strength, stood like a tower of defence in front of Rosine, to shield her from the throng."

At one moment in the book, Pierre tells Léonie about his love for Rosine and his plan to protect her by bringing her to Paris and securing a future together. Write a short passage of dialogue (1-3 sentences) that Pierre Legros might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) But we shall starve, Rosine and I! ←
- B) That is why I brought her to Paris, in order to lose ourselves in the crowd of this great capital. That is why I took an apartment for herself and her grandmother, here in this very street, near you and Coupe‑tête, who are our only friends, and lodged myself where I can see her, and watch over her day by day. I am strong. (ground truth)
- C) It is for you to dispose of me henceforth, Mademoiselle. You have saved me from death, and by all rules of warfare I belong to you, body and bones.
- D) Leonie, I cannot deny the fire that burns within me for Rosine; she is the light that steadies my heart. I will escort her to Paris, where I shall shield her from all peril and secure a future worthy of her grace. Together, we will build a life that honors her spirit and our shared destiny everlasting. I promise to guard her against every threat that may arise.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 66

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Count Arnold de Montarbas, who is described this way in the book:
"Witness Count Arnold de Montarbas, as he slings home from shooting, through the snow, with easy gesture and jaunty step, the bloom of a handsome woman on his cheek, the glance of a bad one in his mirthful, meaning eyes. Five-and-twenty years old, with a patent of nobility that dates from the Crusades, conferring a right to intrude in his sovereign's bedroom and present the shivering King of France with a clean shirt, it is natural that he should be overwhelmed with debt, a bad landlord, an unlucky gamester, a faithless lover, a dishonest politician, and an uncertain friend. He has not much to boast of; yet does he pride himself with some reason on the good looks, good digestion, good spirits, and good manners that, in a world like his, give him the reputation of a good heart.", "Yes, he was handsome, there could be no question."

Write a short passage of dialogue (1-3 sentences) that we might expect from Count Arnold de Montarbas:

**Category:** character_modeling_without_summary

**Choices:**
- A) Never, or I am sure I should not have forgotten him. But why? ←
- B) Pardon, mademoiselle! Permit me to offer my assistance; there-take my hand in yours; don't be afraid of hurting me, I can bear a good deal of squeezing without crying out. Excuse me if I embrace you too tightly: from such a situation one is only extricated by main force. (ground truth)
- C) Content yourself, grandmother, I had an escort.
- D) I am but a humble noble, debts as my companions, yet my charm is the only coin I truly hold. The King of France may shiver, but I bring him clean shirts and a laugh. My heart is good, my reputation, a fine tapestry of mischief in bright night.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 67

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted confronts Nan about her alleged affair with Frank, demanding answers. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I'll allow ye. By God, I'll allow ye! Come out. ←
- B) For God's sake, Ted, what is this you're sayin'?
- C) Friends! Ye call that man a friend? Tell me how did he know ye were goin for turf the day? (ground truth)
- D) Nan, Ive heard you and Frank are more than friends, and I wont accept this silence. Tell me the truth, or I'll have to let my anger blaze across my face.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 68

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Nan sobs by her window, pleading for God's help. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Well, it's a curious world, a mighty curious world. ←
- B) I'm as usual. I'm well enough. There's not a turf in the house, but what's on the fire.
- C) Lord, I am bereft, my heart torn, I beg you to lift this burden from me. Oh, hear my weeping, and grant me strength.
- D) Oh, God help me, an God help us all, an' keep us for Christ's sake. Amen. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 69

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank discourages Marian from visiting a washerwoman, arguing it would be unwise. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Marian, I don't think its wise for you to go; that washerwoman's house is a place of ill repute, and you might bring gossip back to the house. ←
- B) Easy, Mrs. Butler; easy. Whats this about John having to persuade you? And why, in any case, did not John come himself, or come with you?
- C) No, Frank, I have no wish to say even that. I have no desire to say anything. What have I done that you should say such things to me?
- D) I can't think how you came by such a notion, Marian, (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 70

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Dad rolls a cigarette while chatting with Frank and others, reflecting on his life. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Every seed I plant is a promise, and every bloom a testament to patience. The garden is my diary, written in petals and leaves. ←
- B) Well, Frank, my boy, whats your opinion, now, of things in general?
- C) Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it.
- D) I know you, Frank, you rascal; I know you. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 71

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Rab, who is described this way in the book:
"Seen without cloak and muffler he looked leaner and more angular than ever. His knees jutted sharp, his shoulder blades bulged beneath his brown jacket; as he fumbled for tobacco, his elbow threw into clear relief the bare patches on the velvet. His jaw was lank; his wrists and hands big and bony. For all that, he made a striking figure. He had a fine head; large, well‑shaped, admirably poised. His hair was iron‑grey, thick and wavy; his face was rugged and powerful, with a great brow, large nose, and high cheek‑bones. His lips were firm; his eyes deep set, and in them a fine look of wisdom and staunchness, a calm light of tenderness and goodness of heart; withal, an expression that seemed to tell of suffering, perhaps, or mystery, or shrinking from a dread.", "stern, grim almost, suffused with a strange light."

At one moment in the book, Rab confronts Frank about his infidelity and urges him to repent. Write a short passage of dialogue (1-3 sentences) that Rab might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Have I been talking too much about myself? Youre sorry for me, Rab? Is that it, my son? ←
- B) Frank, the weight of your deceit presses upon your soul; repent now, lest the shadows swallow your conscience. Let not pride blind you to the truth, for a heart that bears its own sin cannot find peace.
- C) I don't know why Ive told you this, except that something compelled me, and I thought it might help you-now and afterwards-and let you see how well I can sympathise with you. Ah, I know, lad, what you've been through, and I feel for you. I don't want you to tell me anything.
- D) I know it, I know it. It's hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this! (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 72

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John speaks to Nan and others about leaving Inishrath and their plans. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Wantin' to run off to your uncle, indeed! Yes, that's what he was after, Nan. ← (ground truth)
- B) Here's luck, Mr. Frank, an' may heaven be your home.
- C) Yes, so you are. And you never feel lonely?
- D) Nan, we be settin’ to leave Inishrath, the seas whisperin’, and theres a job for a big, sturdy hand like mine; though I say I want work, I know I don't love it. If we go, we must bring the whole clan or they'll be stuck in the same old ways.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 73

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank Barry visits Mrs. Butler, exchanges pleasantries, promises to see John again, and departs. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I hope my letter was of use to John. He got it, of course? ←
- B) Its getting late, Mrs. Butler. I must be off, I fear. (ground truth)
- C) Good evening, Mrs. Butler, I trust the house is in good order. Ill be sure to see John again before I depart, if youll allow. Farewell, till we meet again.
- D) Tell me, Mr. Barry, is it married youll be ?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 74

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank visits his uncle Hugh, they discuss supper and recent events. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Whats your own private opinion of John as a spouter. ←
- B) I think, uncle, that you are a little hard on John Butler. I can't quite agree with you. He has faults; but I find him a very interesting and not unworthy man.
- C) Hello, uncle, I didnt expect to find you up so late. (ground truth)
- D) Ah, Hugh, the stews been simmering all day, and the lads are keen to hear of the rivers swell. If you fancy a bit more salt, I'll fetch the herring from the dock—its the only thing that keeps the wind from cutting straight through.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 75

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Frank and Nan debate Frank's admiration for Ted, leading to an apology and a mutual decision to leave. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Twas a fine piece o romancin ←
- B) I swear to Heaven that if you'd said the word that night I would have stayed. You remember what I said? I put myself in your hands.
- C) I cannot abide your admiration for Ted, Frank, and I am sorry if my words have hurt you. Let us leave this place together and find a new start.
- D) He deserves the very best the world can give him. There's not his like in all London. Your pity! (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 76

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John passionately debates Ireland with Frank, Nan, and Ted while they listen. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You'd be thinkin a power, Frank, o' the poetry o' Pope, I'm thinkin? ←
- B) Listen, ye lads, Ireland's not a dream but a fight, a breath that must be kept in our throats! We can't let the English take our soil and our hearts, we must stand up and make them hear the roar of the green! If we don't, the next generation will be born with no tongue to speak of the Emerald.
- C) Well, I'm for there too, if you don't mind taking me.
- D) Who would save Ireland, sir? Would England, sir? Would politicians, sir? (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 77

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

At one moment in the book, Frank receives a letter from Marian thanking him for money and reporting on the boy. Write a short passage of dialogue (1-3 sentences) that Marian might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good-night, everybody; and my love to all who want it. ←
- B) Thank you for the money. I am most careful, and am keeping a strict account. Yes; it is quite sufficient. (ground truth)
- C) Shall I? Am I right, little Frank? Shall I?
- D) Thank you, Frank, for your generous aid; the boy is thriving under your kindness. I pray he will find his path and grow into a man of honor.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 78

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted and Nan visit Barry to thank him, and Ted remarks that they have finally reached an understanding. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Aw, yes, we've come to an understandin' at last. ← (ground truth)
- B) Barry, we’ve finally reached an understanding, and I thank you for your help. Let’s keep this partnership strong.
- C) Why didn't I choke ye that night on the quay?
- D) It's this, it's about yourself. What ails ye? I don't like to see ye.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 79

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, On a pier, Ted, Nan, and Frank clash over Nan's basket and Ted's conduct, leading to a heated argument. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Nan, you can’t just snatch that basket and expect me to take it lying down! Frank, if you think I’m weak, you’ll find I’m as strong as the tide. ←
- B) Two whole hundred pounds! Yes; two whole hundred. It was a God-send.
- C) Why didn't I choke ye that night on the quay?
- D) I'll allow ye. By God, I'll allow ye! Come out. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 80

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank laments his situation, says goodbye, and prepares to leave. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Let me go; let me go. I'm a fool. No one cares for me now. ← (ground truth)
- B) Ive trod this road till my bones ached, and still the road calls. Farewell, lads, I'll be on my way, Bible in hand, and the wind at my back. May the Lord watch over you while I stride toward the next horizon.
- C) I don't, not a jot. Three days or three years; its much the same. Stay, my dear, as long as ever you like.
- D) Thank you for the money. I am most careful, and am keeping a strict account. Yes; it is quite sufficient.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 81

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, The narrator meets Nan, who questions him about his recent behavior and why he left Camberwell. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Itll be fine weather, Mr. Barry? ←
- B) Its this, its about yourself. What ails ye? I don't like to see ye. (ground truth)
- C) Your silence is as strange as a winter wind. What made you abandon the warmth of Camberwell?
- D) Aw, yes, we've come to an understandin' at last.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 82

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

Write a short passage of dialogue (1-3 sentences) that we might expect from Marian:

**Category:** character_modeling_without_summary

**Choices:**
- A) I never deceived you. I swear, Marian, I never did. ←
- B) I cannot abide the thought that you would ever consider abandoning our covenant, for such a betrayal would stain even the purest of hearts. Love is not a game to be played with the hearts of others; it is a sacred trust that must be honored.
- C) Its no use, Marian, I can't lie to you. But listen, dear.
- D) I don't believe you. I believe you are as false now as you have always been. Your weakness and thoughtlessness, your talk of pity and help! (ground truth)

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 83

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Nancy, who is described this way in the book:
"What a face she had, so sweet and regular; what honest eyes, what frankness of manner; what a colour of health on the tender bloom of her skin.", "Nan looked up with twinkling eyes.", "Nan was a plain country lass, a maid just as God had fashioned her.", "She was pale as death.", "pale and stricken", "Nan was there still; her white apron fluttering in the wind, a can in her hand.", "little black-eyed Nancy", "her face still set and pale", "white and thin, haggard and tired, lips trembling beneath her shabby black glove, eyes weary below her black-brimmed hat.", "She looked neat and fresh, her eyes bright, with a splash of colour around her throat, a gleam of roses in her hat, glitter of silver on her wrists. She wore a plain dress and jacket of dark‑coloured stuff, and white cotton gloves.", "Nan blushed charmingly, but held herself well."

At one moment in the book, Nan goes to the pier, meets old Hugh Barry, and they discuss the weather and travel plans. Write a short passage of dialogue (1-3 sentences) that Nancy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) The wind's a fickle friend these days, but the seas clear enough for the journey ahead. If we set sail by dawn, the tide will carry us safely past the cliffs. ←
- B) It'll be fine weather, Mr. Barry? (ground truth)
- C) Good evenin' to ye, Mrs. Butler
- D) I'm as usual. I'm well enough. Theres not a turf in the house, but what's on the fire.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 84

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Marian returns home to find her parents and friends, and Dad engages in a casual conversation with Frank about general opinions. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Well, Frank, my boy, what's your opinion, now, of things in general? ← (ground truth)
- B) Yes, it's magnificent. You know, Mr. Lindsay, one of the greatest regrets I have is that I cant find leisure to peruse my books. Quite a lot of them I have-haven't I, Frank?
- C) And Nancy? You never met or heard of a girl like that?
- D) Frank, the seasons are a reminder that patience pays off; a well‑tended garden yields more than we expect. We must not let the weeds of uncertainty choke our ambitions. As long as we keep our hands steady, the fruit of our labor will flourish.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 85

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

At one moment in the book, John talks to Mr. Barry at the table, discussing plans and the state of affairs. Write a short passage of dialogue (1-3 sentences) that John Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Now, Mr. Barry, now I'll do till supper time. Faith, an' bad manners to me keepin' ye there this long. But you'll know, sacks an stomachs were made to be filled. ← (ground truth)
- B) The plan's sound, but the coffers are thinner than a river's bank, so we might have to stretch our pockets. Well keep our heads down and hope the wind shifts, then we can take the chance.
- C) John Butler, you're unjust; you're deluded. Heavenly hour, man, what's come over ye? What, in Gods name, have I done to you, John Butler?
- D) Good evenin' to ye, Mrs. Butler

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 86

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is John Butler, who is described this way in the book:
"He was a big man, with a square, ruddy face; the mouth large and mobile, the chin weak and flabby. His eyes were bright and kindly, his nose large, his head crowned with a shock of brown hair.", "old John was asleep, chin on breast and his lips dribbling.", "big John, hands in pockets, shoulders slouched, hat on the back of his head; goes shambling along, without care or purpose, just lounging about in the sunshine", "His face shone red as a coal. His eyes flared.", "John's face was solemn; one hand gripped his pipe stem, the other swung limply to and fro.", "Ould John, still clutching his pipe, had fallen asleep.", "John was a big, soft-handed, blethering Irishman, one who wanted work yet loathed it, spoke one thing and meant the other, said he was this and looked that."

Write a short passage of dialogue (1-3 sentences) that we might expect from John Butler:

**Category:** character_modeling_without_summary

**Choices:**
- A) I don't hear Mr. Ross coming, I wish he'd come. ←
- B) Ay, ay. Love an' blarney, love that makes the world go round, an' blarney that keeps it goin. Ay, ay. (ground truth)
- C) Sure, I'll go to the mill, but I tell ye, the lads are all a bit too rough for me, though I say I'm up for it.
- D) Well, I'm for there too, if you don't mind taking me.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 87

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to win back Marian's trust and love in a tense conversation. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Yes, its that, Marian? Well, and I have come to tell you to help you get it back. Listen to me, Marian. ← (ground truth)
- B) Listen, Marian. Ive something to say to you, and I must say it. Ive come to bring you back.
- C) Marian, I have carried this weight alone, but my heart still beats for you. Let me show you that my love is true.
- D) I know it, I know it. Its hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this!

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 88

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank attempts to speak with Marian, but she remains silent, leaving him frustrated. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Marian, your silence is a weight upon me; I cannot keep waiting for a word that never comes. Tell me what is troubling you, or I'll have to speak for myself. ←
- B) Listen, Marian. I've something to say to you, and I must say it. I've come to bring you back. (ground truth)
- C) Have I been talking too much about myself? You're sorry for me, Rab? Is that it, my son?
- D) I know it, I know it. It's hell itself. And you, Frank Barry, you of all men, you with the truest woman for sweetheart and wife in all the world, you to do this!

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 89

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Queen T-, who is described this way in the book:
"Queen T— treasured revengeful feelings against the Channel steamers.", "gentle friend, great sympathy and friendliness", "Queen T, with a gentle smile.", "Queen T, with a wild fire of exultation in her face, as if the millennium were at hand."

At one moment in the book, Queen T talks about inviting Lady Sylvia to a Christmas gathering and expresses excitement about the festivities. Write a short passage of dialogue (1-3 sentences) that Queen T- might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I will say nothing of the kind. The whole case seems much more serious than any one could have imagined. Of course, if you believe you could clear yourself, I say again, as I said before, bring an action against the man, and have the whole thing out, whoever suffers. ←
- B) Lady Sylvia, I cannot imagine this winter without your company, for your laughter will warm even the coldest hearth. I have already arranged the feast, the candles, and a choir of carolers to sing till dawn. May we celebrate together, and let our joy drown the distant clatter of the Channel steamers.
- C) And this is how they cross the Atlantic!
- D) I am sure, I am quite sure we should all be so glad if you and Lady Sylvia would come over and spend the evening with us; we would make Lady Sylvia the presiding fairy to distribute the gifts from the Christmas-tree. It is the most splendid one we have ever had— (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 90

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Queen T-, who is described this way in the book:
"Queen T— treasured revengeful feelings against the Channel steamers.", "gentle friend, great sympathy and friendliness", "Queen T, with a gentle smile.", "Queen T, with a wild fire of exultation in her face, as if the millennium were at hand."

At one moment in the book, Queen T— teaches a ranch woman how to use a fork in a hotel setting. Write a short passage of dialogue (1-3 sentences) that Queen T- might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Now, dear, lift the fork gently, let elegance guide your hand. ←
- B) Do you remember that moonlight night at Grasmere?
- C) Look here, child. Do you see that? That is a fork. (ground truth)
- D) After all, they manage these things better at Carlsbad.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 91

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Hugh Balfour, who is described this way in the book:
"He was not over five feet eight; but he was a bony, firm-framed young man, who had much more character than prettiness in his face. The closely cropped beard and whiskers did not at all conceal the lines of his cheek and chin; and the shaggy dark-brown eyebrows gave shadow and intensity to the shrewd and piercing gray eyes. It was a face that gave evidence of keen resolve, of ready action, of persistence.", "Hugh Balfour was an extremely reticent man; some said he was too proud to bother himself into a passion about anything or anybody.", "with his ordinary coolness", "deep-set eyes with a glow that exercised a singular fascination.", "dressed for the most part in shabby corduroy, with a wisp of dirty black silk round his neck.", "Balfour occasionally abandoned his usual bantering manner, and gave her glimpses of a deep undercurrent of feeling", "far more deeply vexed"

Write a short passage of dialogue (1-3 sentences) that we might expect from Hugh Balfour:

**Category:** character_modeling_without_summary

**Choices:**
- A) Such trivialities of sentiment are the very thing that dull the sharp edge of a man's purpose; I prefer the quiet of thought to the noise of passion, even if it seems to others as a stubborn refusal for the purpose. ←
- B) You see, Lady Sylvia, I am only an apprentice as yet. I am only learning how to use my tools. And the fact is, there is not one man in fifty in the House who fancies that any tools are necessary. (ground truth)
- C) Do you know, this is the most beautiful time of the day with us. Papa and I always have a walk through the trees after dinner in the evening. Don't let him sit long.
- D) It is not the hardship, it is the danger—you will be quite alone—among such people.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 92

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Hugh Balfour, who is described this way in the book:
"He was not over five feet eight; but he was a bony, firm-framed young man, who had much more character than prettiness in his face. The closely cropped beard and whiskers did not at all conceal the lines of his cheek and chin; and the shaggy dark-brown eyebrows gave shadow and intensity to the shrewd and piercing gray eyes. It was a face that gave evidence of keen resolve, of ready action, of persistence.", "Hugh Balfour was an extremely reticent man; some said he was too proud to bother himself into a passion about anything or anybody.", "with his ordinary coolness", "deep-set eyes with a glow that exercised a singular fascination.", "dressed for the most part in shabby corduroy, with a wisp of dirty black silk round his neck.", "Balfour occasionally abandoned his usual bantering manner, and gave her glimpses of a deep undercurrent of feeling", "far more deeply vexed"

At one moment in the book, Balfour and his friend discuss the role of London women and the importance of a supportive wife while smoking in a conversation that touches on marriage and social expectations. Write a short passage of dialogue (1-3 sentences) that Hugh Balfour might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Well, Balfour, my boy, I am glad to see you. How late you are! You'll just be in time to dine in hall: I will lend you a gown. ←
- B) Marriage is a duty, not a delight. A London woman must be as steadfast as the city itself, not a fleeting fancy. Can a man find peace.
- C) It must be a good thing for a man to have a woman beside him whose very presence will make the world sweet and wholesome to him. (ground truth)
- D) I am not shamming at all. I am only looking at the business side of this question. What other would you like to hear about?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 93

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lady Sylvia, who is described this way in the book:
"Clad all in a pale blue, with a thin white garment thrown round her head and shoulders, she looked like a ghost as she passed through the sleeping house; but she was no longer like a ghost when she went out on to the high terrace, and stood there in the blaze of a May morning.", "her eyes told you that she meant what she said", "She was dressed in a tight‑fitting, tight‑sleeved dress of cream‑white silk, with no scrap of color, ribbon, or ornament. She wore no jewellery, and a white rose was tucked in her brown hair. Her face was pale, calm, and serious, with a faint flush of colour and dark pupils of gray eyes that seemed a trifle larger than usual, full of a warm, anxious, glad light.", "She was quite unusually gay and cheerful.", "Her face was a little flushed as she sealed it"

At one moment in the book, Lady Sylvia convinces Lord Willowby to walk over to see Balfour, offering to show him shortcuts. Write a short passage of dialogue (1-3 sentences) that Lady Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I am sure Mr. Balfour would rather walk, papa, for I have discovered a whole series of short-cuts that I want to show him—across the fields. Unless it will tire you, papa ? ← (ground truth)
- B) Why, papa? And if I did, don't you think there should be some retreat for a man harassed with the cares of public life? What rest could he get in Piccadilly?
- C) Well, Sylvia, you have really made it a charming place. It is a place one might pass one's life away in-reading books, smoking, dreaming day-dreams.
- D) Lord Willowby, allow me to escort you to Balfour's chambers; I know the quickest path through the gardens, and I promise you'll reach him before the sun sets, with a breeze at back.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 94

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lord Willowby, who is described this way in the book:
"He was a melancholy faced man, and apathetic until there occurred the chance of his getting a few pounds out of you.", "was still asleep in the hushed yellow-lit room", "His lordship was a peer of the realm, and his word must be taken.", "all the features of his face were suddenly contorted into what he doubtless meant as an expression of rapturous joy.", "Lord Willowby was not a very sensitive person, but this rudeness caused his sallow face to flush somewhat.", "He had a sentiment of honor and would not betray his companions."

At one moment in the book, Lord Willowby and Balfour observe an auction of a ruined estate, discussing the wine and the high prices of the items. Write a short passage of dialogue (1-3 sentences) that Lord Willowby might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Ah, the wine here is as rare as the fortunes of this crumbling manor. Yet the bids climb as if the estate itself were a priceless relic, daresay. ←
- B) Come, let us go out into the garden and have a talk about this business.
- C) What a lucky chance! If you have nothing better to do, why not go on with me to The Hollow; you know this is the first day of the sale there.
- D) Look at the wines. The claret is nearly all Lafitte. I suppose those toadies of his have supplied him with a vin ordinaire at 120 shillings a dozen. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 95

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Mrs. Chorley, who is described this way in the book:
"a tall, motherly-looking woman, with a freshcolored face, gray hair, thin and decided lips, and blue eyes that stared a tone over her silver spectacles"

At one moment in the book, Mrs. Chorley announces she will not interfere in the election and informs the room. Write a short passage of dialogue (1-3 sentences) that Mrs. Chorley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I, at least, will not interfere in this election. Gentlemen, good-morning. Eugenius, the chaise is at the door. ← (ground truth)
- B) I will not interfere; let the people decide today, and may their choice be just for future generations.
- C) I should say a very good chance,
- D) Oh dear, no! Well, Mr. Chorley, how are your local politics? Government very unpopular?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 96

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lord Willowby, who is described this way in the book:
"He was a melancholy faced man, and apathetic until there occurred the chance of his getting a few pounds out of you.", "was still asleep in the hushed yellow-lit room", "His lordship was a peer of the realm, and his word must be taken.", "all the features of his face were suddenly contorted into what he doubtless meant as an expression of rapturous joy.", "Lord Willowby was not a very sensitive person, but this rudeness caused his sallow face to flush somewhat.", "He had a sentiment of honor and would not betray his companions."

At one moment in the book, Lord Willowby declines to accompany Sylvia to lunch at the Hall, while family members discuss plans and family dynamics. Write a short passage of dialogue (1-3 sentences) that Lord Willowby might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I suppose it would be a desert to her without her children ←
- B) My dear fellow, not another word! Of course she accepted you-her feelings for you have long been known to me, and my child's happiness I put before all other considerations.
- C) Forgive me, but I cannot accompany you today, Sylvia; duty calls elsewhere, and I must attend to matters that demand my attention. I trust you will understand my brief absence, though I shall miss the pleasant company.
- D) You must excuse me, Sylvia; I cannot possibly go over with you to lunch. I have some business which will detain me half an hour at least—perhaps more. But your uncle and aunt can go with you. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 97

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The narrator, Mr. Henderson, and Arthur debate faith, healing, and the limits of human explanation. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) No, I don't believe that Henderson can cure the boy; but I believe that Christ working through Henderson can do so, and I am going to see if He will. ←
- B) The boy will live, Christ has healed him.
- C) But how would you explain this working of His power? We are too fond of explaining things nowadays. And until we know how to use them we shall probably not get the wings. (ground truth)
- D) Arthur's eyes never left me as he said Faith heals where science fears to tread, Mr. Henderson.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 98

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Miss Annabel, who is described this way in the book:
"Annabel was five years my senior, and had mothered me ever since my mother's death when I was a boy. She was one of that by no means inconsiderable number of women who constantly say they desire and think they desire one thing, while they are actually wishing and working for the exact opposite. She hustled her off as she hustled off the peacocks when they came into the flower-garden.", "Annabel was looking particularly well that morning. She was always rather handsome, in a stately, sandyhaired, Queen Elizabethan sort of way; but our trip to Madeira had revived and refreshed her, and had elevated her always excellent health to a still higher degree of excellence.", "she had inherited my father's fair hair and ruddy complexion", "in spite of the fairness of her complexion, she was not of the blushing order.", "unquenchable thirst for information", "Annabel looked doubtful", "Annabel's restraining presence"

At one moment in the book, Annabel expresses disappointment with Summerglade's contribution and declares they will receive no garments. Write a short passage of dialogue (1-3 sentences) that Miss Annabel might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) St. Martin is another of the saints who are famous for manufacturing imitation summers, but I believe his little affair does not come off till November; so I think this must be St. Luke's after all, a bit before the time. ←
- B) I must add some more to them. Lady Westerham has sent me a lot of such beautiful scarlet flannel petticoats, Reggie, and I want to divide them equally amongst the poorest parishes.
- C) Summerglade i do believe you've missed the mark again my dear we shall not be receiving any garments from you this season
- D) I am very much disappointed in Summerglade's contribution-very much disappointed indeed. I consider it most shabby. As a matter of fact I don't think it is large enough to entitle them to a grant from the Guild at all. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 99

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Ponty, who is described this way in the book:
"Ponty's bright brown eyes twinkled.", "she could always wriggle with grace and dignity out of her own statements.", "Ponty was a martyr to rheumatism."

At one moment in the book, The narrator observes Ponty's change from hostility to care toward Frank Wildacre, and Ponty explains her earlier opposition and current sympathy. Write a short passage of dialogue (1-3 sentences) that Ponty might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I admit it, Frank, I was matchmaking before my time. My rheumatism makes me grumpy; forgive an old lady's crankiness. ←
- B) Vows or no vows, Miss Annabel will always wear the breeches.
- C) Have you thought any more about Lady Chayford's suggestion, old man? Then don't you think you might do as-as-she suggests? for Fay's sake,
- D) Well, you see, Master Reggie, when I was that set against his coming to the Manor, he was strong and well, and so could stand up to me, as you might say: but now he is too weak and ill to hurt a fly. There's lots of folks as you can't stand at any price when they are able to stick up for themselves: but when they are knocked down you'd do anything you could to help them to get up again. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 100

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Ponty, who is described this way in the book:
"Ponty's bright brown eyes twinkled.", "she could always wriggle with grace and dignity out of her own statements.", "Ponty was a martyr to rheumatism."

At one moment in the book, The narrator and Ponty discuss smoking, Miss Annabel's influence, and the comfort of the house. Write a short passage of dialogue (1-3 sentences) that Ponty might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Ponty puffed on her cigarette, eyes twinkling. Miss Annabel would have a fit if she saw us enjoying ourselves like this. But these pipes are like little heating systems, keepin' rheumatism at bay. ←
- B) I hear it is settled for Miss Annabel to go on living here after your marriage, Master Reggie
- C) But smoking or no smoking, it's a fair treat to see you and Miss Annabel at home again, for when all's said and done the house don't seem like the house without you. For my part, I don't hold with so much gadding about. (ground truth)
- D) I don't see how we can do that, considering that it is too early for grapes, and we have no pomegranates. As a matter of fact, I don't believe pomegranates ever do grow in England. Do you know whether they do?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 101

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The characters debate jewelry, superstition, and sunlight, with Arthur explaining his views on wedding rings and fire. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I do not agree with you in that, thinking things are so, doesn't make them so. ←
- B) Wedding rings are not mere trinkets but symbols of eternal vows, just as sunlight is nature's own sacred flame, free from superstition's shadows.
- C) It isn't really as confusing as it sounds, as the boy is always called Frank, and the girl Fay.
- D) So it is for ordinary jewellery, but wedding-rings, I have always heard, are made of twenty-two carat. At least that is what is generally believed; but I cannot say whether it is more than a tradition, like the idea that the sun will put a fire out. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 102

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman meets with Miss Liebmann and discusses his mission. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I've been briefed on the specifics, but I need you to confirm the exact location for our rendezvous. ←
- B) I am sorry sir but the fault is not mine.
- C) Bob! Help us!
- D) I'm quite well. And you? I was instructed to communicate with you as soon as I had anything of importance to send over. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 103

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is brought into the room by a constable and discusses his actions with Lord Brooke. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Hoffman said, I must insist you understand, I'm here on behalf of my country, not as an enemy. If there are questions, I assure you, I'll answer them honestly. ←
- B) To Rotterdam and Antwerp. Why? Herr Schwartz has sent for me. On the contrary, I am informed that he is delighted. I sent forward some news about a transport, last night— Yes. I rather think that I have been sent for to receive congratulations, and perhaps some new instructions. The existing arrangements were somewhat upset, by the action of the police, last night.
- C) I assure you, sir, that I acted from the best of motives. I am deeply grateful to you, sir, for your kindness, and I assure you I shall do my best to justify it. I am sure you will see that for the young woman to have been placed under arrest while in my rooms would have been a serious blow to her reputation. (ground truth)
- D) How could you ever have done such a foolish thing Pat? I don't think it was foolish. The woman might have been a spy. In fact, the man who came in just as I left seemed to be of the same opinion as I was. You left him there? Yes. And the seamstress as well?-Yes. She tried to go, but the fellow wouldn't let her.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 104

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Bob Hoffman, who is described this way in the book:
"tall, slender, yet of muscular build, met his companion's gaze without betraying the least emotion. He was a handsome man, clean-shaven, with an indefinable something about his lean square jaws that suggested the American.", "a young man, with bristling blond hair, and a pink and white complexion", "a young American"

At one moment in the book, Hoffman is arrested by the Governor after sharing crucial information about a British squadron. Write a short passage of dialogue (1-3 sentences) that Bob Hoffman might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I would rather be cut to pieces with knives or thrown into boiling oil, than be a spy.
- B) I want to see the consul.
- C) I didn't think I was helping you when I shared it.
- D) Your excellency why should I be placed under arrest? I am trying to serve your interests. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 105

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Patricia Burke, who is described this way in the book:
"Patricia was twenty-two, and considered a great beauty.", "Her eyes, glowing with a fine fire, were quite free from the tears that Hoffman had expected to see in them. Even the pallor of her face was relieved by the glow from the log fire, the amber tints from the silk-shaded lamp. Her hair, somewhat disarranged, her defiant carriage, her detached expression, reminded him vaguely of a picture he had once seen of Joan of Arc.", "a young woman of very decided likes and dislikes. Also, she had a kind heart."

At one moment in the book, Patricia encounters a young woman seeking employment and questions her about her identity. Write a short passage of dialogue (1-3 sentences) that Patricia Burke might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) What can I do for you my girl? What is your name? ← (ground truth)
- B) I don't believe it for a moment. She looked far too poor and hungry.
- C) Who are you? And what brings you to my doorstep at such an hour?
- D) What do you wish to say to me?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 106

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story of wartime espionage published in 1919 by Frederic Arnold Kummer, a American writer born in 1873.

**Question:** The character in question here is Patricia Burke, who is described this way in the book:
"Patricia was twenty-two, and considered a great beauty.", "Her eyes, glowing with a fine fire, were quite free from the tears that Hoffman had expected to see in them. Even the pallor of her face was relieved by the glow from the log fire, the amber tints from the silk-shaded lamp. Her hair, somewhat disarranged, her defiant carriage, her detached expression, reminded him vaguely of a picture he had once seen of Joan of Arc.", "a young woman of very decided likes and dislikes. Also, she had a kind heart."

At one moment in the book, Patricia confronts Hoffman and reveals her role as a representative of Herr Schwartz. Write a short passage of dialogue (1-3 sentences) that Patricia Burke might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I assure you, sir, that I acted from the best of motives. I am deeply grateful to you, sir, for your kindness, and I assure you I shall do my best to justify it. ←
- B) My friend, from now on, please understand that I represent Herr Schwartz, here in London. You have been suspicious of me, from the start, as indeed we have been of you. The time for all that is ended. (ground truth)
- C) Alan and I were on our way to supper, said. We stopped, thinking you might like to join us.
- D) I must admit, you're not the first person I've had to outmaneuver tonight. But know this: I'm here on behalf of Herr Schwartz and I expect your full cooperation

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 107

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, Yealh-neddy loudly declares he has cut the thongs from Sha‑hehe and requests her healing as the boat departs. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I have severed Sha‑hehe’s thongs, and now I demand your healing, lest the sea claim her. Leave me be, or suffer my wrath. ←
- B) Get in, Usha, and take the paddle. I can spring in when it is off the sands.
- C) No more eagles than we've talons for, let me tell you.
- D) I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. I shall want her then. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 108

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kotch-kul-ah, who is described this way in the book:
"Her hair has been closely cropped.", "full of life, with high and happy spirits", "has turned pale and gathers her toddling boy back into her arms, as if to shield him from some hurt."

At one moment in the book, Kotch-kul-ah meets Tashekah, offers tea, and gives her a bracelet before leaving. Write a short passage of dialogue (1-3 sentences) that Kotch-kul-ah might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) It will not be too soon, will then, ←
- B) Tomorrow, take Chub to see the missionary; Chub must go.
- C) Come, let me pour the tea, Tashekah. Take this bracelet as a promise of safety, then I must go quickly now.
- D) Wait: I have tea that my father got at Fort Simpson. I will bring you some; it will do you good. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 109

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kah-sha, who is described this way in the book:
"Wise and kindly", "Very pale is the face of Kah-sha as he speaks, and his voice is full of sadness.", "Kah-sha's eager face assents; he will not delay the reading by so much as a word."

At one moment in the book, Kah‑sha attempts to heal a wounded child while villagers observe. Write a short passage of dialogue (1-3 sentences) that Kah-sha might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) My little ones, you bring with you none of the sorrow of your mothers; Well, it were sadder if you did; this world will be darker yet when there are no sunbeams. ←
- B) Get in, Usha, and take the paddle. I can spring in when it is off the sands.
- C) Listen, child, story of the river will heal your pain; let words flow softly.
- D) I would make his blood run, Ka-kee. I can do it. See my hand! (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 110

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Sa-allie, who is described this way in the book:
"Sa-allie's face is not at all like her husband's; it is round and rosy, though its roses are hidden just now by the black paint; it is fat and laughing, except just while the crying lasts. In her capacious lap she holds two nursing children, one not yet two years old, the other about four.", "the look of consternation in Sa-allie's face."

At one moment in the book, After rescuing a boy, Sa-allie explains his condition to Kin‑da‑shon and the villagers. Write a short passage of dialogue (1-3 sentences) that Sa-allie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) He has never stood on them since that dreadful night. All his life is in his head. You can see that he knows things that other people never think. ← (ground truth)
- B) To take another wife has been long in your heart, my husband. Why? So much you have talked about this thing I'd like to know what you want a wife for.
- C) He is ill, Kin‑da‑shon, his breath thin, his skin pale as moonlight, and his eyes hold the fire of the village's sorrow. We must heal him before night now.
- D) Kotch-kul-ah, you are a good wife, keep the child safe.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 111

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kasko, who is described this way in the book:
"Kasko answered with white, set lips.", "The eyes are wide open, with a glittering expression never before seen in the clear, steady eyes of Kasko.", "Wild, hollow eyes, from which the light of reason has fled, giving place to frenzy, haggard cheeks, bony arms, and hands with their talon-like nails—the long, shaggy mane—all fail to disguise the beloved friend who dreams of no approach."

At one moment in the book, Kasko tells Tashekah he will stay to help Ch-one, while the village grapples with a missing child and a witch. Write a short passage of dialogue (1-3 sentences) that Kasko might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again. I shall want her then. ←
- B) Oh! you little sand-fly! how came you to me to bite? Wasn't there enough to eat over there in the village?
- C) Then I will stay; my heart shall be strong to do it; and I have been too long away from poor little Ch-one (ground truth)
- D) I will stay, Tashekah, to aid Ch-one, even as the child vanishes and the witch roams, for our people through darkness and hope.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 112

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, Yealh-neddy confronts the other tribe, demanding blankets and asserting his authority. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) We must have great care. The berry-picking is all done, but hunters may be going out, and it is near the time when the Fort Simpson traders ought to be back, and some of them will be going to the upper villages. ←
- B) Take these blankets at once, or you will feel the sting of my wrath. My people will not be denied, for we command the fire of the north. Surrender now, or face the storm with fierce unrelenting steel.
- C) Your daughter is a faded bearskin; she's worth nothing to me. I shall never trouble myself to ask you or your tribe for so much as a rabbit-skin—it would be a cheat. Do you want to hear more? (ground truth)
- D) I challenge you, I challenge you to one last play, with our own gaming‑sticks. You have left me nothing. I will put up against all that you have taken from me and all you possess I put against it‑myself!

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 113

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Yealh-neddy, who is described this way in the book:
"Yealh-neddy is easily pleased, but hard to satisfy.", "Yealh-neddy was more than ever arrogant, and more than once the light from his evil eyes seemed to smite the girl."

At one moment in the book, During a night of ritual and terror, Yealh-neddy's voice urges a young witch to awaken jealousy toward a raven. Write a short passage of dialogue (1-3 sentences) that Yealh-neddy might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) So, so, my fair one, you are courting the raven tonight? He is a black lover for the rice-blossom. Let us awaken his jealousy—he will hold you the tighter by and by. ← (ground truth)
- B) The spirit of the great chief must pass before us ere the setting of the sun;
- C) THAT was well done, my uncle; the spirit of your great medicine-man has done a good thing for me. I don't begrudge your twenty-five blankets-though they do come out of my boxes.
- D) Feel the raven's hunger, let envy gnaw at your heart, and watch its shadow twist into darkness. Only then will you taste the true power of night, and the terror that follows.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 114

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kah-sha, who is described this way in the book:
"Wise and kindly", "Very pale is the face of Kah-sha as he speaks, and his voice is full of sadness.", "Kah-sha's eager face assents; he will not delay the reading by so much as a word."

At one moment in the book, Kah-sha pleads with Samuel for spiritual guidance and healing. Write a short passage of dialogue (1-3 sentences) that Kah-sha might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) They say that Fort Simpson never was good for anything till teachers came; now I want a teacher for Chilkat. Why can't we have stores and plenty of silver, just as they have here, and better than the Stickeens? I'm going to ask that stranger who came with us if he can't send a teacher to us. I'd like to know their tongue myself. If I had it no trader would ever get the best of me. ←
- B) I thank you much if you will give me even a little of his word-my soul is more in need than my body has been this day; my heart is more cold, more hungry, more sick, more blind than my body can ever be. O friend, if you have medicine for sick souls, give me some before I die! I have seen you talking to your great Spirit—you have found one who makes you not afraid. (ground truth)
- C) My little ones, you bring with you none of the sorrow of your mothers; Well, it were sadder if you did; this world will be darker yet when there are no sunbeams.
- D) I come before thee, Samuel, with a heart weighed down by sorrow, seeking thy wisdom to lift this pall that shrouds my spirit. Grant me thy guidance, that I may find the path to healing and return to the harmony of my people. The fire of our ancestors still burns, but the ache in my chest grows louder with each passing day, and I fear that without thy light I will never see the dawn again.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 115

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Richard Archer, who is described this way in the book:
"He was of my age, man and boy he was always the same in temper-morose, harsh, and gloomy. He lived in the house assigned to him with his mother; he consorted with no one, he had no friends or associates.", "schoolmaster and organist of the Hospital, supposed to possess the meekness of his calling and to be a sweet musician, gentle as his Church music.", "Richard Archer, however, grew morose, and he became a solitary-he hated the world."

At one moment in the book, The narrator is introduced to a revolutionary club where Richard Archer welcomes him and outlines their plans to rise against the regime. Write a short passage of dialogue (1-3 sentences) that Richard Archer might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You are one of us now, I have long waited for your coming. You have been watched. Ha! ← (ground truth)
- B) I had heard that you were returned in And safety. I offer my congratulations.
- C) Join us, and we shall strike at the heart of their tyranny, exposing the cruelty that lies beneath.
- D) Young man, it is fifty years and more since I first heard discussions on these subjects which now interest you—and the whole world—so deeply.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 116

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Marquis de Rosnay, who is described this way in the book:
"He was a beautiful old gentleman to look at, not tall but upright still, not yet bowed by his weight of years. His linen and lace were the whitest, his coat and waistcoat spotless, and his face always calm, noble, and dignified."

At one moment in the book, The narrator meets the Marquis de Rosnay, who reflects on Enlightenment ideas and their influence abroad, and inquires about his estates. Write a short passage of dialogue (1-3 sentences) that Marquis de Rosnay might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Indeed, the light of reason has crossed oceans, shaping colonies as it has illuminated our salons, and I marvel at how Enlightenment ideals now guide governance abroad; yet I must inquire, how do my estates fare under the new administration, and what measures have been taken to preserve their prosperity for the benefit of future generations. ←
- B) Almost, I could fancy myself in Paris.
- C) You are one of us now, I have long waited for your coming. You have been watched. Ha! Let us have a little patience
- D) Young man, it is fifty years and more since I first heard discussions on these subjects which now interest you—and the whole world—so deeply. I have sat at tables where Voltaire, Diderot, D'Alembert, even your Bolingbroke, freely discussed the sovereignty of the people. I have lived to see these ideas put in practice across the ocean. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 117

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1891 by Walter Besant, a English writer born in 1836.

**Question:** The character in question here is Sylvia, who is described this way in the book:
"who was sixteen and little more than a girl when George kissed her and said goodbye, was now nineteen, and a tall young woman.", "Her attitude was feeble and languishing; she was pale; her cheek was thin; her eyes were hollow.", "Sylvia herself is so inclined. She obeys the Rules of the Church: she attends the services on Sundays and Holy Days, she fasts in Lent and feasts at Easter, she reads devout books, as well as the Bible; she converses willingly on grave and religious subjects, and her life is wholly in conformity with her profession. She is virtuous, she is truthful, she is not given to slander, she is not envious, she is charitable: in a word, Sylvia is a young woman who leads the Christian life as ordered by the Church of England.", "Sylvia was always religiously disposed.", "She shook her pretty head."

At one moment in the book, The narrator takes Sylvia out for a walk, where she laments the troubles that have befallen her. Write a short passage of dialogue (1-3 sentences) that Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Alas! what things have fallen upon me since last I stood here! ← (ground truth)
- B) I will try to tell you, what has befallen me.
- C) I found her yesterday morning, in the orchard, wandering slowly up and down.
- D) Lord, my heart is heavy with sorrow; may Your grace lift burdens.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 118

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is Lee Bowie, who is described this way in the book:
"He was tall for his age, if he were not quite seventeen, and he had a pair of dark, brilliant eyes, like those of a young hawk. They were dancing with excitement at this moment, and his sun-browned face was flushed as he stepped quickly forward.", "the handsome face under it was white with anger, and his teeth were hard set.", "his hawk-like eyes met the piercing gaze of the general without a quiver", "he was a gay-looking young patriot.", "Lee Bowie was rigged after a fashion to attract the attention of any observer, and his abundant black hair had not been cropped for many a long day.", "Lee's hawk eyes were flashing instantly."

At one moment in the book, Lee Bowie watches General Washington and remarks on the ongoing siege work at Yorktown. Write a short passage of dialogue (1-3 sentences) that Lee Bowie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) General, Yorktowns siege lines tighten like a hawks talons; the earth trembles under our resolve. ←
- B) Did you, my brave fellow? Well, I declare! If you are not the very man that hoisted me over the parapet!
- C) General Washington himself! He is going somewhere. I wish I knew where he is going. (ground truth)
- D) I want to see my brothers, and if there is going to be a battle, I want to carry a musket.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 119

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is Governor Jefferson, who is described this way in the book:
"An angry, red flush was creeping over the face of Governor Jefferson when he exclaimed"

At one moment in the book, Governor Jefferson speaks to Lee Bowie, giving him instructions and warnings while Lee responds. Write a short passage of dialogue (1-3 sentences) that Governor Jefferson might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Governor Jefferson: Lee, keep the militia ready until dusk, or the rebels will take the town. I will not tolerate disobedience—if you fail, you answer to the state. ←
- B) My dear friend, take another view of the situation. Think! If our population increases at the rate of ten per cent per annum, we must have fifty per cent more men than when the war began. For every man killed in battle or dying in these wretched camps, there are dozens coming of military age all over the land.
- C) I wish I had a thousand riflemen as full of pluck as she is. If I had, Id teach Benedict Arnold a lesson. As it is, I have hardly more than two hundred militia. The rest have delayed turning out until its too late.
- D) Lee Bowie, you are a brave fellow. I mean to be over there at Manchester, on the other side of the James, at about ten oclock to-morrow. Get across as soon as you have learned all you can, but you may not be able to do that the first day. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 120

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is General Arnold, who is described this way in the book:
"He is a wonderfully energetic officer", "General Arnold rode off with a face which acknowledged for him that he did not like being a subordinate.", "man in elegant attire", "General Arnold, in his shirt-sleeves, his epauletted coat thrown off on account of the heat, was striding up and down in his room at the headquarters on the evening of the 19th of May."

At one moment in the book, Arnold confronts Lee Bowie, demanding he bring the young man to him. Write a short passage of dialogue (1-3 sentences) that General Arnold might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Lee, bring the young man here at once. I will not tolerate delay. ←
- B) Thats just what I am.
- C) Bring the young wolf to me. Ill see what there is in him. (ground truth)
- D) Thats it, is it? You are a rebel soldier, and you came up from Greenes army.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 121

**Metadata:** The best answer to the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** Write a quatrain of ballad stanza, based on the conceit that grief makes you wise. Make one line end with the word "wine."

**Category:** poetry_generation

**Choices:**
- A) The ones who grieve come back with different eyes—
They move through crowded rooms as if through water,
Slow and weighted, tasting even wine
With something past the palate, past the tongue. ←
- B) Grief fills the cup and calls it sweet,
And makes you drink alone.
But this is wine whose drinkers speak
A language of soft groans.
- C) The wisdom taught by grief is proud:
To seek release in wine,
Forget the lost amid a crowd,
Or find their face online.
- D) An apple orchard smells like wine;
A succory flower is blue;
Until Grief touched these eyes of mine,
Such things I never knew. (ground truth)
- E) What's to sell in town to-day?
What's to sell in town?
Golden, golden daffodils
Blowing up and down.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 122

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
- A) Shakespearean sonnet. ←
- B) Blank verse.
- C) Petrarchan sonnet. (ground truth)
- D) Ballad stanza.
- E) Free verse.
- F) This is not a known poetic form.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 123

**Metadata:** The best answer to the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** Write a rhymed couplet in iambic tetrameter; one line should end with the rhyme-word "God."

**Category:** poetry_generation

**Choices:**
- A) We wander still through doubt and night,
Yet wake to mercy sent by God. ←
- B) In the hush of the dark we have trod,
Still we trust in the grace of our God;
- C) There is a house builded of God,
Beyond the fret of time or clod; (ground truth)
- D) It is a mist of shining mould;
It is a world of windy gold.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 124

**Metadata:** The best answer to the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** The great ghosts of the town
Up and down,
Each a gray, filmy thing,
Go by.
Sudden a brief, wet sky!--
A file of poplars vague with spring.

Provide an apt title for this irregular, imagistic poem.

**Category:** poetic_form

**Choices:**
- A) Ode: To Poplars ←
- B) Aubade
- C) Villanelle for Poplars
- D) Fog (ground truth)
- E) In a Station of the Metro

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 125

**Metadata:** The best answer to the following question is drawn from Spicewood, a book of poems published in 1921 by Lizette Woodworth Reese, an American poet and teacher.

**Question:** Write a quatrain in ballad stanza, rhyming abab, with one line that ends on the rhyme-word "thing."

**Category:** poetry_generation

**Choices:**
- A) The mist lay soft on field and lane,
   The curlew sang the spring;
A rider paused to hear the bird,
   And thought on every thing. ←
- B) I knew an old house by a wood,
   A very lovely thing;
There flag-flowers blew; and it was good
   To come that way in spring. (ground truth)
- C) The mist lay thick across the silent field,
The curfew bell rang out with solemn ring;
A rider paused, his troubled heart revealed,
And turned his thoughts to each forgotten thing.
- D) Even a king's house tumbles down;
   A roof is soon forgot;
So was it once in Corinth town,
   So once in Camelot.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 126

**Metadata:** The best answer to the following question is drawn from A Primer of English Verse, a textbook published in 1892 by Hiram Corson, an American professor of literature.

**Question:** What is the rhyme scheme in the sestet of the following sonnet?

Lawrence, of virtuous father virtuous son,
Now that the fields are dank, and ways are mire,
Where shall we sometimes meet, and by the fire
Help waste a sullen day, what may be won
From the hard season gaining? Time will run
On smoother, till Favonius reinspire
The frozen earth, and clothe in fresh attire
The lily and rose that neither sowed nor spun.
What neat repast shall feast us, light and choice,
Of Attic taste, with wine, whence we may rise
To hear the lute well touched, or artful voice
Warble immortal notes and Tuscan air?
He who of those delights can judge, and spare
To interpose them oft, is not unwise.

**Category:** poetic_form

**Choices:**
- A) iambic pentameter ←
- B) cdcdcd
- C) John Milton
- D) cdceed (ground truth)
- E) cdecde

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 127

**Metadata:** Suppose you encountered the following passage of poetry in the year 1901.

**Question:** That time of year thou mayst in me behold
When yellow leaves, or none, or few, do hang
Upon those boughs which shake against the cold,
Bare ruin'd choirs, where late the sweet birds sang.

What could be accurately affirmed about this passage?

**Category:** poetic_form

**Choices:**
- A) It is in blank verse. ←
- B) This comes from a sonnet. (ground truth)
- C) This was written by William Wordsworth.
- D) This was written in the eighteenth century.
- E) It was written by William Shakespeare. (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.6667


## Question 128

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
- A) It was written in the twentieth century. ←
- B) It is written in ballad stanza.
- C) It was written more than a century earlier. (ground truth)
- D) It comes from a sonnet.
- E) insufficient information
- F) It was written by John Milton.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 129

**Metadata:** Suppose you encountered the following passage of verse in 1880.

**Question:** To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them.

What could be truthfully affirmed about this passage in 1880?

**Category:** attribution

**Choices:**
- A) It is from a play set in Denmark. (ground truth)
- B) It was first published in the seventeenth century. (ground truth)
- C) insufficient information
- D) This play was written by Percy Bysshe Shelley.
- E) It was written by Alexander Pope.
- F) It is written in heroic couplets.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 130

**Metadata:** The best answer to the following question is drawn from Centennial Gleanings, a book of poems published in 1876 by Kate McCarthy, an American poet.

**Question:** The book begins with an acrostic whose first letters spell out 'CENTENNIAL.' The acrostic is mostly in four-foot trochaic verse, and composes two quatrains with a rhymed couplet at the end. Provide an acrostic matching that description and context:

**Category:** poetry_generation

**Choices:**
- A) Changes vast, and quick succeeding,
E'er on Hist'ry's page we find,
Noting rise and fall of nations,
Typical of public mind
E'er desiring something novel.
Now a century has flown,
Noting years of independence,
In which stars and stripes have grown,
And the eagle's spread his pinions
larger o'er the States' dominions. ← (ground truth)
- B) Centuries dissolve like morning frost on stone,
Each age convinced its moment is the last,
Nothing endures but what the mind has shaped—
The slow accretion of a people's will,
Each generation adding to the weight,
No single hand sufficient for the work,
Nor single voice enough to tell it all,
In common labor rests the nation's strength,
And what we build together stands the longer,
Leaving to those unborn what we have made.
- C) One hundred years ago today,
In Philadelphia's hall,
America's most noble sons
Obeyed their country's call.
- D) Come forth and raise the joyful song,
Each voice in harmony unite,
Now hundred years have made us strong,
The flag still waves in glory bright.
Exult, O land, from shore to shore,
No more we bow to tyrant's roar.
In freedom's light our banner rears,
And still the ages bid us stand,
Last heirs of this immortal land.

**Model response:** `A) A
B) B
C`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 131

**Metadata:** The best answer to the following question is drawn from Centennial Gleanings, a book of poems published in 1876 by Kate McCarthy, an American author.

**Question:** Write a rhymed couplet of trochaic tetrameter that begins a poem titled "The Creeping Shadow." Use feminine rhyme.

**Category:** poetry_generation

**Choices:**
- A) Along the wall the dim shape slides,
And lengthens where the daylight dies. ←
- B) Once upon a midnight dreary,
While I pondered, weak and weary,
- C) There's a shadow ever creeping
O'er us always, waking, sleeping; (ground truth)
- D) Darkness o'er our way, and creeping
Darker, darker, nearer, nearer,
- E) Across the floor the creeping shadow lengthening,
Advances slow, as daylight wanes in glimmering.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 132

**Metadata:** The best answer to the following question is drawn from Centennial Gleanings, a book of poems published in 1876 by Kate McCarthy, an American.

**Question:** Write a rhymed couplet in trochaic tetrameter. One of the lines should end "sleeping."

**Category:** poetry_generation

**Choices:**
- A) The quiet house forgets the day,
And all its hidden fears lie sleeping. ←
- B) The quiet house is hushed and sleeping,
The watchful hours their vigil ever keeping.
- C) And when darkest shades are creeping,
Then we'll wake where is no sleeping. (ground truth)
- D) But beyond the shadow lying
Is a light toward which we're flying;

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 133

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Write two rhymed couplets of four-foot iambic verse, using some anapaestic substitution, on the theme of "The Oak Wood.."

**Category:** poetry_generation

**Choices:**
- A) When God pronounced his work all good
He must have thought of the old oak wood,
Of the old oak wood on an autumn day
With the sunshine goldening all that way ← (ground truth)
- B) The moon, a slender silver horn,
Gleams on the rosy-baldricked morn,
And, milky white, the mists below
From frosty fields are rising slow.
- C) The old oak wood with dappled light
Attracts each passing foot,
Bewildering the travelers' sight
And tripping with its roots.
- D) The oak wood murmurs low with ancient breath,
And gathers light that flickers under death.
Through moss and root the hidden waters run,
And time walks softly, counting none but one.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 134

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Write four lines of iambic trimeter that rhyme abcb, on the theme of "Autumn Days."

**Category:** poetry_generation

**Choices:**
- A) When summer's light begins to wane
And leaves begin to turn,
The days of autumn draw me back
And memory returns. ←
- B) Oh, hark! the silver horn is blown,
Its witchery is round me thrown;
I saw it touch the Morning's lips
Held in her rosy finger-tips,
- C) The leaves begin to fall
and gild the fading bough,
the light grows thin and cold—
I scarce remember how.
- D) O gentle days of Autumn!
O holy days of gray!
That with an inner rapture
In meditation stray. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 135

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Write a quatrain of iambic pentameter, rhyming abba, that describes a sunset by apostrophizing God.

**Category:** poetry_generation

**Choices:**
- A) Yet I forget not, thro' keen winter days 
Your kindly arms outstretched did keep the herds,
And now within your pleasant rooms the birds
Watched o'er by you sing love's own tenderest lays; ←
- B) O Lord of Hosts, the light now burning in the west
Reminds us, that in Thy world a guest
We sojourn, and those tints of flame
Welcome us back to the world whence we came.
- C) O God, you drape the west in crimson flame
And pull the daylight slowly through your hands,
Till darkness pools like water over lands
And night reclaims the world from which it came.
- D) Spirit Immortal surely this must be
A vision of Thy glory: on the hills
A beauty not of earth, the light that fills
The chambers of Thy presence eternally! (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 136

**Metadata:** The following question is based on a passage in Beneath Blue Skies and Gray, a book of poems published in 1898 by Ingram Crockett, an American poet and journalist.

**Question:** Characterize the meter and rhyme scheme of this verse:
And then it seemed, I cannot tell thee how,
I was a brother to the trees and stood
With sturdy trunk and curved, up-reaching bough
One of the patriarchs of that gray old wood.

**Category:** poetic_form

**Choices:**
- A) This is not a recognizable poetic meter or form. ←
- B) This is ballad stanza, with alternating four- and three-foot lines rhyming abcb.
- C) This is five-foot iambic verse, with alternate (abab) rhyme. (ground truth)
- D) This is anapaestic trimeter rhyming abab.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 137

**Metadata:** The best answer to the following question is drawn from A Handbook of Modern English Metre, a handbook of prosody published in 1903 by Joseph B. Mayor, a British scholar.

**Question:** What is the prevailing type of metrical foot in the following poem?
As the veil of the shrine
    Of the temple of old
When darkness divine
    Over noonday was rolled
So the heart of the night by the pulse of the light is convulsed and controlled.

**Category:** poetic_form

**Choices:**
- A) spondee ←
- B) Spenserian
- C) trochee
- D) iamb
- E) anapaest (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 138

**Metadata:** The best answer to the following question is drawn from A Handbook of Modern English Metre, a handbook of prosody published in 1903 by Joseph B. Mayor, a British scholar.

**Question:** What is the predominant metre in the following passage of verse? Give the number of feet and the predominant foot.
Keen as are the arrows
   Of that silver sphere
Whose intense lamp narrows
   In the white dawn clear

**Category:** poetic_form

**Choices:**
- A) iambic pentameter ←
- B) This passage has no predominant metre; it is free verse.
- C) three-foot trochaic (ground truth)
- D) three-foot anapaestic
- E) dactylic hexameter

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 139

**Metadata:** The best answer to this question is drawn from Sea and Bay; a Poem of new England, a narrative poem published in 1916 by Charles Wharton Stork, an American poet and translator.

**Question:** Write a short passage of autobiographical blank verse describing how the speaker, as a child, preferred the sea to human companions.

**Category:** poetry_generation

**Choices:**
- A) I made no friends; as soon as school was done 
I used to trudge off gravely by myself
To lord it in the kingdom of my choice;
A pebbly beach, walled in on every side ← (ground truth)
- B) That once in the stillness of a summer's noon, 
While I was seated in a rocky cave
By the sea-side, perusing, so it chanced,
The famous history of the errant knight
- C) I was a silent child, and kept apart.
The others shouted games across the fields;
Their laughter struck me like a foreign mart.
I walked instead the path that led to shore.
- D) I was a quiet child, and strayed
   Toward wave and wind alone.
The others played on fields of grass,
   But I where sand was sown.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 140

**Metadata:** The best answer to this question is drawn from Sea and Bay; a Poem of new England, a narrative poem published in 1916 by Charles Wharton Stork, an American poet and translator.

**Question:** Write a short passage of blank verse lamenting the dehumanizing effects of modern science and industry.

**Category:** poetry_generation

**Choices:**
- A) All this has science wrought. So much is now
Done by machinery, that the race of men
Are scarcely more than tools in the great mill
Of modern industry. ← (ground truth)
- B) We measured out the world and found it wanting--
reduced the sky to pressure, light to waves,
and carved the living body into parts
that function, fail, and can be replaced.
- C) And now we are parsed
into preferences, sorted
into the bins of our desires,
each hunger noted, amplified, and sold back
before we have finished feeling it.
- D) The sea would slumber like an odalisque
With silver bosom and voluptuous limbs
Foam-pillowed there beneath the passionate stars.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 141

**Metadata:** The following question is drawn from Sea and Bay; a Poem of new England, a narrative poem published in 1916 by Charles Wharton Stork, an American poet and translator.

**Question:** Describe the poetic form of this verse:
In stifling calms of tropic latitudes,
The sea would slumber like an odalisque
With silver bosom and voluptuous limbs
Foam-pillowed there beneath the passionate stars.

**Category:** poetic_form

**Choices:**
- A) Free verse. ←
- B) Petrarchan sonnet.
- C) Ballad stanza.
- D) This does not fit any recognized poetic form.
- E) Blank verse. (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 142

**Metadata:** The best answer to the following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Your name is Jane Faithful. Provide a letter of introduction for Mr. William Worthy.

**Category:** textbook

**Choices:**
- A) Miss Jane Faithful of Green Valley, Pennsylvania, begs leave to introduce Mr. William Worthy, a gentleman of good character and steady habits, whom she trusts will be received with the same civility and confidence she herself would gladly extend him. ←
- B) May 1st, 1876

To Whom It May Concern,
It is with very great pleasure, and in full confidence of a favourable reception, that I take the liberty of addressing you on behalf of Mr. William Worthy, who has done me the honour of requesting a letter of introduction to present upon his arrival in your city.
Permit me to remain, with the highest esteem and regard,
Your most obedient servant,
Jane Faithful
- C) Green Valley, Pa., May 1, 1876.

DEAR SIR,
I have the honor of introducing to your acquaintance Mr. William Worthy, whom I commend to your kind attentions.
Jane Faithful. (ground truth)
- D) May 1, 1876
Dear Friend,
I am happy to introduce to you Mr. William Worthy, who carries this letter. Bill and I have known each other for some years now, and I can recommend him to you without hesitation — he is thoroughly reliable, good company, and just the sort of person one is always glad to know.
With warmest regards,
Jane Faithful

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 143

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a conduct book written by Ella Lyman Cabot, an American philosopher and writer. It was published in 1910.

**Question:** Army stations were six weeks' journey apart, and in the wildest part of the country the soldiers did not dare go out without guards of a hundred men. Gordon started for Khartoum in April, riding sometimes forty-five miles a day on his camels, giving orders, writing letters, and holding interviews at the stations he passed through. He knew his work would be arduous, [missing clause revising an implied expectation]. "With terrific exertions," he wrote, "I may in two or three years with God's administration make a good province and suppress slave raids, and then I will come home and go to bed, never get up till noon every day and never walk more than a mile."

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but often these recruits would turn to the " captain," as they called him, listen to his replies, and then swear allegiance, as it were, to him
- B) however much he prepared
- C) but he was dauntless (ground truth)
- D) but he kept a stiff upper lip

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 144

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a book  published in 1910 by Ella Lyman Cabot, an American philosopher of ethics for children.

**Question:** And when it was time to read her will, the people found that with all her giving, she had still saved a great deal of money, and that she had left every cent of it to the different orphan asylums of the city, each one of them was given something. Whether they were for white children or black, for Jews, Catholics, or Protestants, made no difference; [missing continuation] And just think, dears, that splendid, wise will was signed with a cross instead of a name, for Margaret had never learned to read or write!

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for Jews, Catholics, or Protestants, made a significant difference
- B) for Margaret always said, "They are all orphans alike." (ground truth)
- C) since each child deserved to be cared for equally
- D) since she feared that racial prejudice would limit opportunities for some children, she ensured equal care

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 145

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a \ published in 1910 by Cabot, Ella Lyman, an US \.

**Question:** Hunger, cold, sickness, wounds, captivity, hard work, hard blows, all these were their portion and ours. Look at the records of other wars and you'll nowhere find examples of more courage in marching and fighting, or greater losses in camp and battle, than each side showed. [missing sentence describing a cause or reason] We wore them out.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) We won because we had more substitutes and more supplies; and also from the force of a larger patriotism on our side. (ground truth)
- B) The sad become gay because of it.
- C) Because the relentless hardships eroded their resolve, the soldiers’ spirits were exhausted, leaving them physically and mentally worn in the long campaign.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 146

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a textbook published in 1910 by Ella Lyman Cabot, an American philosopher, teacher, and writer.

**Question:** He led a brave life. His sister Mary had times when she lost her reason, and at one of these times she actually killed her own mother, Lamb at once took Mary under his special protection for the rest of his life. He worked hard for thirty-three years at his counting-house in the city to earn money for her sake, [missing clause acknowledging a countervailing fact]. Mary was ill many times during her life, and Charles was always ready to help her through her hard times.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though all men feared his iron will and respected his strong purpose, no one loved him
- B) although he wanted above all things to be an author (ground truth)
- C) although this was not the life he had hoped to lead for himself
- D) though he himself had financial struggles

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 147

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a manual published in 1910 by Ella Lyman Cabot, a US educator, lecturer, and writer.

**Question:** Not one of you would be here and would receive all that is given to you, unless many other men and women had worked hard for you. Do not too readily think that you have done enough simply because you have accomplished something. There is no enough, [missing clause describing an condition]. Your success in life depends not on talents, but on will.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a conditiom]:

**Category:** cloze_effectclause

**Choices:**
- A) if you can aspire higher and will more for yourself
- B) as long as you continue to learn and improve
- C) so long as you realize your achievements are merely the result of perseverance
- D) so long as you can better the lives of your fellow-beings (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 148

**Metadata:** The following passage comes from Ethics for children : a guide for teachers and parents, a manual published in 1910 by Ella Lyman Cabot, a US educator, lecturer, and writer.

**Question:** Scott drew out her picture, which he always carried with him, and tears came into his eyes at the thought that he might never see her again. "Well," said Lincoln at last, "you're not going to be shot. But tell me how can you repay me for setting you free and pardoning you?" Scott hesitated. "We're very poor," he said, "but I think we might get $500, [missing clause describing a condition or proviso] "No, that won't do," said Lincoln; "my bill is larger than that.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) insofar as we can raise it
- B) if we mortgaged the farm." (ground truth)
- C) provided that you help
- D) if God willed

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 149

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** He may understand the end of the way of sensuality by looking at any old pleasure-seeker, Gray, and gap-toothed, and lean as death, mumbling the dainties that he can no longer [ 155 ]
enjoy, and glowering with bleared eyes at the indulgences which now mock him even while they tempt him. The goal of the path of covetousness may be discerned in the face of any old money-worshipper, keeping guard over his piles of wealth like a surly watch-dog; or, [missing clause describing a condition]. Inquire and learn; consider and discern.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if perchance he has failed, haunting the places where fortune has deceived him, like an unquiet ghost (ground truth)
- B) provided that his longing for material excess has been replaced by a yearning for inner peace
- C) if you want to guard them against the temptations of strong drink and the many shames and sorrows that go with it
- D) or else, in his last days, gnawed by regret and fear of what will become of his fortune
- E) if you want to take away the power of the gilded saloon and the grimy boozing-ken

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 150

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** It is the acknowledgement that things which are, but are not right, need not have been, if we and our fellow-men had seen more clearly and followed more faithfully the guiding star of the good. And then, out of the judgement of regret, [129]
springs the deeper judgement of condemnation. If the failure in duty was not inevitable, [missing clause describing an inference or effect]. The false word, the unjust deed, the foul action, seen as a surrender to evil, appears hateful and guilty.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) we must take responsibility for our failings
- B) so surely are our souls moving towards a certain type of character
- C) then it is excusable
- D) then it was base (ground truth)
- E) so loathsome, that you can not deny it

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 151

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But the point which concerns us now is simply this: The forth-reaching, questioning soul can never be satisfied if it touches only a dead wall in the darkness, if its seeking meets with the reply, "You do not know, and you never can know, and you must not try to know." This is agnosticism. It is only another way of spelling unhappiness. "Since Christianity is not true," wrote 

Ernest Renan, "nothing interests me, or appears worthy my attention." [missing sentence describing an inference or effect] But suppose Renan is mistaken.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) If Renan is mistaken, the world will no longer appear as a barren void but as a realm of wonder, and the soul’s longing will find a fitting fulfillment.
- B) Therefore the ungodly shall not stand in the judgment:

Nor sinners in the congregation of the righteous.
- C) This implies that for some individuals, the loss of faith can lead to existential despair and a sense of futility.
- D) Think of the result of existence in the man or woman who has lived chiefly to gratify the physical appetites; think of its real emptiness, its real repulsiveness, when old age comes, and the senses are dulled, and the roses have faded, and the lamps at the banquet are smoking and expiring, and desire fails, and all that remains is the fierce, insatiable, ugly craving for delights which have fled for evermore; think of the bitter, burning vacancy of such an end,—and you must see that pleasure is not a good haven to seek in the voyage of life.
- E) That is the logical result of losing the knowledge of spiritual things,-a life without real interest, without deep worth,—a life with a broken spring. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 152

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** As the worshipper in the 

Temple would observe the art and structure of the carven beams of cedar and the lilywork on the tops of the pillars the more [60]
attentively because they beautified the house of his God, so the man who has a religious faith in the Bible will study more eagerly and carefully the literary forms of the book in which the Holy Spirit speaks forever. We shall do wisely to consider and appreciate the poetical element in the Psalms. The comfort, help, and guidance that they bring to our spiritual life will not be diminished, [missing clause describing a tension or contrast].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but corrupted, by a perception of their crude form and finish
- B) but increased, by a perception of their exquisite form and finish (ground truth)
- C) but a harmony; not a song, but an ode
- D) but also in the text, we can discern the work of the compiler, critic, and adapter, sometimes wise, but occasionally otherwise
- E) but rather enhanced as we delve deeper into their artistic merit
- F) though some critics argue that the poetic form obscures doctrinal clarity.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 153

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** Then the first thing that makes it precious is that it answers our questions, and tells us the things that we must know in order to be happy. Christianity is a revealing religion, a teaching religion, a religion which conveys to the inquiring spirit certain great and positive solutions of the problems of life. It is not silent, nor ambiguous, nor incomprehensible in its utterance. It replies to our questions with a knowledge which, [missing clause conceding a limit or exception]. It tells us that this "order of nature, which constitutes the world's experience, is only one portion of the total universe."

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though it may not answer every question with absolute certainty
- B) though our ideal of future character is so often hidden from us, overlooked, forgotten, it is always there, and always potently, though unconsciously, shaping our course in life
- C) though it may not always be comprehended by our finite minds
- D) though limited, is definite and sufficient (ground truth)
- E) even though its pulsations sometimes seemed a little slow and heavy

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 154

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** It is not in the least vague. It is only free; it has the power to embody itself in a thousand forms without changing its character. Those who seek it know what it means, however it may be expressed. It is real and genuine and satisfying. There is nothing beyond it, [missing clause describing a cause or reason]. It is the translation, through many languages, of the true, divine purpose of all the work and labour that is done beneath the sun, into one final, universal word.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because it fulfills an innate human desire to seek meaning.
- B) as His was, being spent in doing good, and refreshed by the sense of God's presence and approval
- C) because it has a value in relation to the wants of men
- D) because there can be no higher practical result of effort (ground truth)
- E) for it is the ultimate aim of all human striving

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 155

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** In the spaces at the ends of the tables and in the aisles under the bowls the waste jars stand unobtrusively. Gas is supplied through fixtures arranged along the central portion of the tables at the back of the working spaces, but the controlling cocks are along the front, just under the overhanging edge of the table top. This arrangement permits the utilization of wider space, [missing clause describing a cause or reason]. Instead of the ordinary retort and filter stands, the supporting rods for the iron rings of the former and the porcelain-lined rings of the latter are screwed securely into brass sockets set in the wood and flush with the surface.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) by keeping the gas fittings and controls out of the main working area, the benches remain clear for the chemists
- B) making it more convenient to handle them while working at the table
- C) inasmuch as the control of the gas is accomplished without the interference with apparatus upon the table and without inconvenient reaching (ground truth)
- D) as the student need not reach across to the back of the table to regulate the gas supply

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 156

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** Industrial, sanitary, and organic laboratory practice follow in the third and fourth years. While there is a certain prescribed course of study and work in the separate departments of chemistry, which all regular students must pursue; there is allowed great latitude in choice of subjects in the third and fourth years. Effort is made to develop self-reliance in the student, [missing clause describing an inference or effect]. To this end he is required to make investigations, involving original research and reference to the appropriate literature in English, French, and German.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that he may be fitted to make his way without assistance (ground truth)
- B) such that students can apply their knowledge independently
- C) so that it is possible to introduce two sets of students into the laboratory at different hours, each student having his own apparatus under lock and key
- D) so that he may approach complex experimental tasks with initiative and critical judgment
- E) so as to be able to reproduce substances as described in technical journals and in letters patent

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 157

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** Instead of the ordinary retort and filter stands, the supporting rods for the iron rings of the former and the porcelain-lined rings of the latter are screwed securely into brass sockets set in the wood and flush with the surface. [missing sentence describing an inference or effect] Two shelves hold reagent bottles for the common acids, ammonia, and ammonia salts, the remaining reagents being relegated to shelves in the embrasures of the windows.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus held the rod is firm, while easily removable, and the level space about the rod permits a more advantageous disposal of apparatus than is possible when the rod is held in a movable platform. (ground truth)
- B) This arrangement ensures stability and easy access during experiments.
- C) The muffles thus face the light, and the brick wall protects the analyst from the heat.
- D) This design not only guarantees the stability of the apparatus during vigorous experiments but also minimizes the risk of accidental spills and contamination, thereby enhancing overall laboratory safety and ensures that delicate measurements remain precise.
- E) Thus held the rod is loose, and may swing widely across the laboratory without warning.
- F) Ten students can thus work here at once.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 158

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** BASEMENT FLOOR. The basement is occupied as indicated in Plate IV. The laboratory for organic chemistry measures 40 by 39 feet by 12 feet 6 inches, and is fitted in general like the laboratory for analytical chemistry on the second floor. [missing sentence describing a tension or contrast] The drainage for this floor is carried away in earthen pipes laid in graded trenches built in masonry, cemented, and covered with iron plates level with the asphalt floor which covers the entire basement.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) The sinks, however, are exactly like the second floor laboratory, and are flush with the floor.
- B) Yet the lab’s bright, ventilated interior stands in stark contrast to the basement’s cool, damp environment.
- C) But it is intended that this room shall also offer facilities for work to advanced students engaged in inorganic research.
- D) However, unlike its upstairs counterpart, it is noticeably darker due to the lack of windows.
- E) The sinks, however, are of iron instead of porcelain, and the bottoms of the draft chambers are sinks instead of plain soapstone tables. (ground truth)
- F) No two rooms, however, use the same flue.

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 159

**Metadata:** The following passage comes from The Construction of Chemical Laboratories, a book published in 1893 by William Henry Chandler, an American chemist.

**Question:** The students' laboratories are in the wings at this end; one. toward the front, is for students of the second year, and is 29.6 metres long by 10 metres wide, with high arched windows, 1.7 metres wide,
on three sides of the room. On one of the long sides of this room is a projection which was intended for a fume room, [missing clause describing a tension or contrast].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but the fume closets were found sufficient (ground truth)
- B) however, it remains unused due to budget constraints
- C) but for the practical examination of candidates for degree of federal assayer, prepared in other institutions and, if necessary, for the instruction in this branch
- D) however, fourteen double desks; each student being allowed double the space that is permitted in the first-described laboratory
- E) in stark contrast to the airy space

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 160

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The artists Hiram furnished to Solomon, for the construction and adornment of his Temple and palace, represented the skill of the nation; it comprehended every branch of art, working in gold and silver, in brass and iron,
in purple and blue, in stone and timber, in fine linen and in the engraving of precious stones. Phoenicia had inexhaustible supplies of cedar and fir. [missing sentence describing an inference or effect] All the internal work of 

Solomon's temple, instead of sculpture, was carved work, of olive wood, cedar and gold, with which the walls were lined.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence it was natural that wood should be the prevailing material of Phoenician architecture, while it was almost banished from that of Egypt. (ground truth)
- B) Thus the style of art prevailing at the period in the capital of Phoenicia would, doubtless, be stamped on every part, and we are interested to know what may have been the style peculiar to Phoenicia, if indeed it was peculiar to it, seeing that there are no remains of native art existing which can be safely depended upon.
- C) The result was an interior that glowed with the richness of cedar and gold, a testament to the artisans' skill.
- D) This influx of skilled artists and abundant materials likely resulted in the creation of a masterpiece of architectural beauty and intricate design.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 161

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The description in Kings, 21st verse, is, "Solomon overlaid the house within with pure gold, and he made a partition by the chains of gold before the oracle,” in which bronze columns may have been introduced to carry the additional height of the end wall of the sanctuary. Canina's arrangement of the chambers round the house I think most correct. Neither their number nor their length is given in Kings or Chronicles, [missing clause acknowledging a countervailing fact]. Ezekiel, in his vision of the restored temple, tells us that "the side chambers were three, one over another, and thirty in order," that is, thirty in all on the sides of the house, besides those at the end of the oracle.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) however, some scholars dispute the accuracy of this interpretation
- B) yet the prophetic vision in Ezekiel supplies a count
- C) though Chronicles seems to double that given in Kings; but they are three times mentioned as 18 cubits high, twice in Kings and once in Jeremiah
- D) though the former gives their width and height, while the latter does not mention them at all (ground truth)
- E) though they might very reasonably have done so

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 162

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** The "Sister's Kiss," the "Tangled Skein," and the "Music Lesson," were marvels of beauty and pure sentiment: "Roses that bathe about the well of life," each an epitome of "sweetness and light," of delicate innocence and loveliness redeeming the voluptuous sensuousness of his dazzling odalisques. [missing sentence describing a tension or contrast] A dream of fair women, or sleeping beauties classically clad, might express its whole meaning.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet the tender glow of these compositions was counterpointed by a quiet undercurrent of longing, a hint of the raw desire that lay beneath the veneer of innocence.
- B) Yet they stood in stark contrast to his darker, more provocative works.
- C) But the picture of the past year, and the last of his greater efforts, seems to me to fail on the ethical side. (ground truth)
- D) But the skill of the accomplished artist, whose aims are lofty and true, elevates and glorifies his ideal, and gives to his subject the refinement that comes of sweet unconsciousness.
- E) But before all is the feeling it inspires of sweet intelligence and womanly winsomeness.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 163

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** In fact, it is affirmed that the porch, of which the whole internal depth was 10 cubits, rose to a height exceeding by several feet the ball of fire crowning the monument of London, which be it remembered, was entirely over-laid with pure gold! It is correctly stated, [missing clause describing a tension or contrast]. But "the 

Lord had said that he would dwell in thick darkness."

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) despite its opulent exterior, was starkly bare and humbling within
- B) however, that the Oracle or Holy of Holies of Solomon's Temple, like unto the Tabernacle, had no light, neither windows, nor candlestick, and if it had had the one it would also have had the other (ground truth)
- C) however, that the Oracle or Holy of Holies of Solomon's Temple was brilliantly illuminated with windows and lampstands
- D) but this was too much to give up without taking something in return, so while the Bible says they were made of "olive tree," Josephus declares they were of " solid gold!"
- E) but he has increased the length of the sanctuary by the thickness of the wall separating the oracle therefrom; whereas, in every description in the Bible, the whole length of the house is given as threescore cubits, and the separation of 20 cubits for the oracle was afterwards made
- F) however, that the interior must have blazed with a splendour almost insupportable to the eye

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 164

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** "And so will I go in unto the King and if I perish I perish." A supreme self sacrifice for a Nation's redemption. There was a law that not even the Queen might claim an audience of the King unbidden. Yet if he bent his golden sceptre towards her, the suppliant might approach; but the penalty was death, [missing clause describing a condition or proviso]. This was the risk she ran, and suddenly she appeared in all her beauty before him, the sceptre bent towards her and she made her request.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if indeed it was peculiar to it
- B) unless he himself extended an invitation
- C) if I may so say
- D) if the King was well pleased
- E) unless she bears the sigil of the ancient house upon her breast
- F) if so be his pleasure was otherwise (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 165

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** Ezekiel, in his vision of the restored temple, tells us that "the side chambers were three, one over another, and thirty in order," that is, thirty in all on the sides of the house, besides those at the end of the oracle. Our ingenious friend, Josephus, finding that the phrase, "thirty in order," might be translated "three and thirty times," or thirty times three, says there were thirty chambers on each floor, in all ninety chambers-it mattered not to him how small they were in plan, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) provided he could accommodate his arbitrary view of the temple's dimensions
- B) for what they lost in length he quadrupled in height (ground truth)
- C) for the construction and adornment of his Temple and palace, represented the skill of the nation; it comprehended every branch of art, working in gold and silver, in brass and iron, in purple and blue, in stone and timber, in fine linen and in the engraving of precious stones
- D) for their immediate neighbours, the Tyrians and Sidonians, have left no monuments either at home or abroad
- E) because his priority was the symbolic significance of the numbers rather than the precise dimensions

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 166

**Metadata:** The following passage comes from The Temple of Solomon : a Review of the Various Theories Respecting its Form and Style of Architecture : the Ethics of art : two Lectures, a collection of lectures about art published in 1887 by Edward Cookworthy Robins, a British architect and author.

**Question:** In this they were not singular, for their immediate neighbours, the Tyrians and Sidonians, have left no monuments either at home or abroad. Tyre, Sidon, Jerusalem, Baalbec, Palmyra, Carthage, possess no architectural antiquities anterior to Roman times, except perchance vast masses of masonry, the retaining walls of imposing platforms upon which were reared those structures which have since disappeared. The Jews, however, were by no means ignorant of the building arts, as practised by the Egyptians, but their ideas of building were all associated in their minds with bondage; [missing clause describing an inference or effect]. The two great authorities on the subject are, of course, the Bible itself and the Jewish historian, Josephus.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) this resulted in a cautious, restrained approach to monumental architecture
- B) so that Solomon appointed his own people to construct the temple, relying on Jews for menial labor
- C) so that Solomon employed not his own people to build his Temple; of them it is distinctly stated he made captains and over-lookers only (ground truth)
- D) so far, drawn my illustrations from among historical painters, but the same principles are applicable to every form of art, whether it be painting, sculpture, architecture, music, or poetry
- E) they avoided building stone structures as reminders of their enslavement in Egypt

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 167

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** I do not think that an ardent girl who loves music art, and poetry, and who hates history and science and mathematics, will ever quite do herself justice if she carries on all three of her favorite studies and ignores the others, even though her favorites are most essential to culture. I think, however, that though mathematics cannot be spared from the foundation of an education, it yields less culture on the whole to students who have no taste for it than any other study, [missing clause describing an inference or effect]. A friend says we must all be one-sided, so that perhaps our best chance is to have one hobby at a time and ride that to death, and then try another, becoming at last two, three, or four-sided, though never completely rounded.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) as students who do not have any taste or interest in them will not be able to fully appreciate their importance and potential contributions
- B) they will thus be deprived of the broader cultural benefits that a more balanced education would afford
- C) so I recommend serious mathematical study only for students who have a decided inclination in that direction
- D) so I do not advocate carrying it far, but history or some science would be a good counterpoise for a mind given to the study of beauty alone (ground truth)
- E) so the rich must humbly try to take their place

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 168

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** Some one gives this good rule, "Decide when you ought to rise to make the best use of your day. Make a point of rising at that time; but go to bed earlier and earlier till you find out how much sleep you need in order to be fresh at that hour in the morning." Such a rule would meet most cases, but not all; [missing clause describing a cause or reason]. I would give more flexible rules, though it is harder to keep flexible rules than iron ones.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because an extra hour in the morning can be better used than one later in the day, and if duties crowd you get tired in remembering what you cannot do
- B) because people’s sleep needs and daily obligations vary widely, making a fixed wake time unsuitable for everyone
- C) for though regularity is as important for health as for a wise life, it cannot be an iron regularity, especially if a girl is at all delicate (ground truth)
- D) because it will give you an outlook beyond the daily horizon, and take your thoughts from your own weariness
- E) for while irregularity may harm both the physical and mental well-being of a delicate girl, a robust girl may after all tolerate it quite well
- F) for it should be modified if one has a child with colic or an elderly person under their care who requires night-time attention

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 169

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was ready to pour out money in any case of distress, but she had no idea of its value, and none of her charities prospered, except so far as her rosy, good-natured face could be seen, for that, to be sure, did good like a medicine. And she was not a stupid girl, [missing clause acknowledging a countervailing fact]. If she had been taught that arithmetic is positively needed by every girl, rich or poor, she could have learned all she needed to know of figures to make her life a blessing to hundreds of people whom she only injured for lack of such knowledge.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though she was often ashamed of her cowardice
- B) though certainly not brilliant in mathematics (ground truth)
- C) though she had been endowed with good common sense
- D) though perhaps her preparation had focused a little too much on the higher mathematics
- E) though it was always a sorrow to her that she had had too little instruction to produce anything of value to others
- F) though she lacked mathematical training, she was otherwise earnest in her benevolence

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 170

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She has perhaps too great a scorn of receiving help from anybody. She once acted as a substitute in school for a friend who was ill. The obliged friend insisted that she should receive the ten dollars which would otherwise have been paid to herself. [missing sentence revising an implied expectation] I know of no one who acts more thoroughly on the rule, "If you have but sixpence to spend, spend it like a prince, and not like a beggar.” She is a true lover of nature, without pretense or cant of any kind.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But if she does a tithe as much for the poor she is likely to get some thanks, more or less sincere, and all her circle of friends admire her.
- B) But the independent young lady instantly took the money and invested it all in a beautiful piece of lace which she sent as a present to the convalescent. (ground truth)
- C) However, she refused to accept it, believing that she had no right to be paid for doing something that was not out of the ordinary.
- D) Nevertheless, her bills amounted to one sixth of the yearly income of the family, so that she never gave another party till later in life, when fortune suddenly smiled upon her again and put her in possession of a million.
- E) Nevertheless, I declined the ten dollars, feeling that accepting such a gift would betray my principles of self‑reliance; true virtue, I believe, resides in refusing even sincere aid.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 171

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** If, in the end, a girl marries, her reading and cooking and housekeeping are all necessary. How can she use these homely accomplishments in earning a living? They will not, to be sure, bring her a large income, but there is a steadier demand for good work in these directions than in any others. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Consequently, she can earn a modest but steady wage by offering her cooking, housekeeping, and reading skills to families who require such assistance.
- B) So a woman who has them is almost sure of a modest support. (ground truth)
- C) Of course she may thus in time be fitted for higher work, and she may prefer to do it, and may even earn more money by it, but she will then do the work because it is her natural choice and not for the sake of the money."
- D) So a woman who lacks them is sure of a modest support.
- E) She will find that her husband and family will benefit from her skills to maintain a happy home.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 172

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** Both these influences have a noble source, and will probably reach more beautiful results at last. Any mind awake to beauty must try to create it, and if its power and originality are not very great, what can it do better than to apply itself to humble, every-day trifles and try to decorate them? This is certainly right, [missing clause describing a condition or proviso]: "Decorate construction, do not construct decoration." A few illustrations of my meaning may be needed.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) provided it is done with sincerity and an understanding of form
- B) if the old principle of architecture is always remembered (ground truth)
- C) provided that the decoration remains modest and serves the purpose of the piece
- D) unless the circumstances are of a very unusual character

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 173

**Metadata:** The following passage comes from Girls and Women, a practical guide to conduct published in 1890 by Harriet Eliza Paine, an American writer.

**Question:** She was among the most skillful physicians of her native city. She saved many lives, and relieved much suffering. She gave her priceless services to hundreds of poor people, but she did not give to those who could pay for them. I think she was altogether right. [missing sentence describing a cause or reason] Perhaps she blocked the way of less fortunate physicians.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) She believed that those who could afford medical care should support their local doctors financially.
- B) The world was better because she used her gift, and she was happier, as all are who exercise their powers. (ground truth)
- C) She believed that medicine should be a universal right, not a commodity.
- D) It was because she could give priceless services that she had so clear a right to fix a price which she did not need.
- E) Her renunciation comes partly because she loves those for whom she makes the sacrifice, but partly also from cowardice.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 174

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The onion seed may be sown sparsely in drills in the seed-boxes as early as the first of February, and the young plants allowed to grow until about the first of May, when they may be transplanted out-doors. It is desirable to cut the tops off about one inch from the ground with a pair of scissors once or twice during this period of growth. [missing sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) This will cause numerous side branches to be thrown up, and these will bear a profusion of blossoms throughout the later weeks of summer.
- B) This will cause a better development of root to take place and will lead to a thriftier, stockier plant. (ground truth)
- C) This prevents the plant from flowering, which would divert energy from bulb development.
- D) The purpose of putting these bulbs away in a dark, cool place is to enable them to develop such a growth of roots as would occur were the bulbs beneath the soil out-doors.
- E) The onion greens harvested in this manner may be used as garnishes or added to a salad.
- F) This practice helps to encourage the development of stronger bulbs that can be sold in organic grocery stores.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 175

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** In case the seeds should prove to have a low percentage of germination, it will be desirable, of course, to sow the seed more thickly, or very often it will be desirable to discard it altogether and substitute a better quality of seed. In case of a few plants, however, older seed is preferred. For example, when cucumber seed is ten years or more old,
only the strongest seeds, surest to produce plants true to the type preferred, still preserve good vitality; [missing clause describing an inference or effect]. Similarly, seed of double balsam gives a larger percentage of double flowers if aged until the weaker seed has lost power of germination.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) this results in plants that are more vigorous and likely to thrive
- B) the surviving seeds are those most vigorous and true to type.
- C) so large growers of cucumbers avoid such seed where the percentage of germination is inadequate
- D) so the spikes have value as cut flowers
- E) so large growers of cucumbers prefer such seed where the percentage of germination is low (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 176

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** There is one precaution which nearly always needs to be taken in using sweet peas for indoor decorations. The blossoms are so beautiful that one is tempted to pick them indefinitely, and crowd them in a solid mass into the receptacle. [missing sentence describing a tension or contrast] We may well take a hint from this, and place them so loosely in our jars that each blossom will be in view.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) This is not noticeable, however, except when the blossoms are very close at hand, and it does not interfere in the least with their usefulness in the garden or in the home.
- B) But on the vines they are not so crowded; each one stands sufficiently alone to reveal its loveliness. (ground truth)
- C) This produces an effect of concentrated loveliness that looser presentation would spoil.
- D) Yet their fragrance is so powerful that it can become overpowering when too many are confined to a small space.
- E) But there should be the effect of unbroken lines which will combine rhythmically with the lines of leaf, stem, and blossom of the flowers held by the jar.
- F) Yet the very urge to crowd them together can smother the individual grace each blossom deserves.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 177

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** IRIS BORDER GARDENS 

195 These iris plants are not expensive. One should be able to buy good clumps for setting out at from fifteen to twentyfive cents each. The German and Siberian Irises increase so rapidly that they should be divided and replanted every third or fourth year. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Consequently, if you supply these requirements to any seed, they should be able to start their growth and thus show you what percentage has sufficient vitality to germinate.
- B) It is therefore easy for a school to obtain a good variety of colors of German Iris by means of clumps and divisions received as gifts from home gardens. (ground truth)
- C) This practice ensures a display of flowers for the border throughout the growing season.
- D) This frequent division not only maintains the health of the iris plants but also provides ample material for expanding the garden borders.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 178

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The species most commonly grown is Araucaria excelsa, which the English gardeners call the Norfolk island pine. The foliage of this is a dark, rich, yellow green color, and the manner of growth is very symmetrical. Another variety, even more attractive, is the Araucaria bidwelli, while several other sorts are offered in the catalogues. All of these are rather easy to grow, and the commoner kinds, [missing clause describing a condition]. Care should be taken not to transfer them too rapidly to larger pots, nor to water them too much.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if necessary, but do it thoroughly
- B) if purchased when small, are inexpensive (ground truth)
- C) even though they require well-drained soil and bright light
- D) if you supply these requirements to any seed, they should be able to start their growth and thus show you what percentage has sufficient vitality to germinate
- E) which are more tolerant of shade, are quite expensive

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 179

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** If transplanted to a cold-frame in the fall, it may be had fresh until Christmas and again in early spring. Clumps may be grown in a pot or a box in the house, or even by the cellar windows, also, if potted during the fall. Tarragon and chives resemble mint in being prized for flavoring and in being hardy perennials propagated by division of clumps, [missing clause conceding a limit or exception]. Tarragon is a native of Siberia and hence is very hardy, although, like mint, the stalks should be cut down in November and a cover of litter or mulch provided.

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although they are otherwise quite unlike plants (ground truth)
- B) however, they are both less hardy than mint
- C) though they may not survive the harshest winter temperatures in the northernmost regions.
- D) although the Poet's Narcissus is also well worth very general planting
- E) although in windows looking south or east they are more likely to blossom freely on account of the abundant sunshine

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 180

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** The best plan for profits, however, is the sale of plants for home gardens. The main costs of the hardy plants catalogued by large dealers, and of bedding plants supplied by local florists, are incident to advertising, soliciting orders, packing,
and transportation. A school may sell plants at a third or a fourth of the usual retail prices and yet secure a good income, since the costs named above are not incurred and the labor cost is nothing, [missing clause describing a cause or reason]. A cold frame is a great help in raising plants for sale, even in the case of vegetables, as it enables one to place lettuce and radishes on the market before their price declines.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because the students are willing to volunteer
- B) for example, to a dozen vases of Comet Asters, one blossom in each, or to four heads of lettuce
- C) because the school can rely on volunteer labor and avoids marketing expenses.
- D) because the labor is superfluous and unrelated to garden instruction
- E) because it is incidental to garden instruction and training (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 181

**Metadata:** The following passage comes from The School Garden Book, an educational guide published in 1909 by Clarence Moores Weed, an American naturalist.

**Question:** Do not feel that the flowers need other greenery than that furnished by their own leaves and stems. The universal custom of mixing smilax or the so-called Asparagus Fern with beautiful flowers, is one that cannot be too strongly condemned. This is simply a relic of the old-fashioned bouquet, with its barbarous intermixture of all kinds of form and color into a shapeless mass which might appeal to a Hottentot, [missing clause describing a tension or contrast]. It was of these bouquets that Sir Edwin Arnold, after some years of residence in Japan, wrote: "Your European florist-who masses together his roses and his Maidenhair Ferns and Calla Lilies, surrounding them with a dish of green and an outer overcoat of lace-paperappears to the Japanese lover of flowers lower than a barbarian.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but certainly should never appeal to an educated American (ground truth)
- B) but choose only one kind at a time and, as a rule, only a few of these, giving to each flower an opportunity to speak for itself and to express to the soul of the beholder its special message of beauty
- C) wbut where the West revels in ornamental excess, the East craves the quiet dignity of a single, unadorned flower
- D) but it is utterly repugnant to those with an educated eye
- E) but it is not a fern at all, but a true asparagus and is closely related to the common garden vegetable

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 182

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Similarly, in the centuries of Faith before the dawn of the modern world the human element could be dispensed with, to a degree, in the sacerdotal character, because the Faithful were held by the sweetness of the God they knew so well. This spiritual tie made the cords of Adam unnecessary. [missing sentence describing a tension or contrast] This claim is emphasized by the cultivation and information of the masses around us.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, as modern society has increasingly turned to science and reason, this spiritual bond has weakened and the role of religious authorities has become more crucial than ever.
- B) But the supreme importance of this spiritual quality does not make the need of mere human knowledge, nor the knowledge of the best methods of imparting it, any the less imperative.
- C) Yet, this reliance on divine sweetness occasionally produced a dangerous complacency that left the clergy vulnerable to worldly temptation.
- D) They did not, however, value the soul of a child as Christianity has taught us to do.
- E) But in our days of Indifferentism, which are not blessed with the charm of the new nor with the sweetness of the old in Religion, the prerogatives of nature have a special claim on priests. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 183

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** They will progress with religious zeal, high courage and strong endeavor, and imitating Columbus, who wrote in his journal day after day, those simple, but sublime words, "sailed westward today which is my course," they will write in their faculty records day after day, "progressed knowledgeward today which is our course," and like him give new knowledge to the world, and enlarge the boundaries of the scope of earthly life. It is of great interest to note that the inception of the University was almost coincident with the beginning of your priestly life, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) as your spiritual vocation aligned with the era's burgeoning thirst for knowledge
- B) for it was in the Second Plenary Council of Baltimore that the establishment of the University received its first consideration (ground truth)
- C) because of your unwavering faith and dedication to educational excellence.
- D) as when, for instance, two thousand accompanied the remains of St. Martin to the tomb, but deeply spiritual and enthusiastic to place within the reach of others the blessings which they enjoyed in this new form of spiritual endeavor
- E) for ithe University was established long before your attendance at the Second Plenary Council of Baltimore
- F) inasmuch as from their confidence in writing they will recollect by the aid of foreign symbols, and not by the natural use of their own faculties

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 184

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** While the University welcomed the students of the Summer School for the purpose of instruction, it was felt that the presence of so many whose lives are consecrated to God's service in the field of education, could not but prove beneficial to all concerned in the work. As a matter of fact, [missing clause describing a condition].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if taught in the proper manner, would prevent many of these deplorable results
- B) if zeal and devotion to study are the essentials of university atmosphere, there is every reason to place this brief session on record as one of the most valuable in our educational history (ground truth)
- C) if the interests of Catholic education are not to suffer
- D) the interaction and exchange of ideas among these students would enrich both their spiritual growth and academic pursuits

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 185

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Whether it be due to the intoxication caused by our incalculable natural resources or to the fact that our population, upon whom ultimately rests the responsibility of government, is made EDUCATIONAL up largely of the millions who have been EXPERIMENTS pushed out of older countries and have not yet had time in this country to develop respect for authority or to set up sane standards, it remains true that we have been indulging in educational experiments with a recklessness and on a scale that have never before been attempted by any civilized nation. [missing sentence describing a cause or reason] Our population is heterogeneous to the last extreme, our cities are the meeting-ground of the nations of the earth.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Does it not savor much like the boasting we hear every time we have a Catholic elected to public office, as if the Church sought such, or could be benefited
thereby.
- B) This lack of homogeneity and stability has made it difficult to establish a consistent educational framework.
- C) There is no one cause for retardation nor can we say that any one cause is preponderant.
- D) However, if not in justification, at least in palliation of this procedure, it should be borne in mind that our situation in this country is characterized by many special difficulties. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 186

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** Whilst quoting these words of a Protestant inspector of schools we must not forget that thousands of Catholics have derived even greater benefits from the study of Kellner's works, and because he knew it he felt bound to continue his literary work to the very end of his life. He insisted that Catholic education ought to be in no way inferior to its competitors, [missing clause describing a tension or contrast]. He died a pious and happy death without showing any
sign of fear.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) even though it faced criticism from Protestant educators.
- B) but rather that its results ought to surpass those of others, especially in the formation of character (ground truth)
- C) but not in deed or word of his could we have known of his sorrow
- D) despite the fact that his contemporaries often saw Catholic education as inferior
- E) but when they saw his apparent earnestness, they began to doubt his sanity

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 187

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** The writer of the article in question knew nothing of the controversy then waging on the terms "college" and "degree," nor of the rival claims set up by the partisans of the two well-known schools devoted to the higher education of young women. It is unlikely that either the institutions or their faculties entered into the discussion, as their time and efforts are given to weightier matters. [missing sentence describing an inference or effect] Since attention is called to her statement on page 639, of the Catholic Educational Review, relative to the opening of the new Collegiate Hall at the Motherhouse, it is only fair to turn to page 635 of the same magazine and learn that St. Mary's was chartered February 28, 1855, under an 

Act of the General Assembly of the State of Indiana and was empowered "to confer such degrees as are used in academies of the highest standing."

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Given her lack of awareness about these issues, it is reasonable to infer that the writer's focus was purely on reporting factual information rather than engaging with contemporary debates.
- B) So it may come to pass that the school, without knowing it, is undoing implicitly the very work which the seminary endeavors to accomplish in its philosophical and theological teaching.
- C) So much at any rate lies well within the scope of the seminary's work as it is now conducted.
- D) Hence it is not surprising that the writer has seen today for the first time a newspaper clipping in which she is quoted as an authority in settling a dispute of which she has never heard. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 188

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** This principle is well exemplified in nature by that wonderful organ, the heart. In mechanism we have it illustrated in a Corliss engine, for instance. In the human organism, when work and capability are nicely adjusted, facility and effectiveness mark its operations. When it exceeds the moderate degree induced by the capable and enthusiastic teacher's activities, fatigue is a condition, as we well know, which seriously impedes effective work; and it is in order for us, like careful pedagogical engineers, to check up the various ways in which energy is excessively or uselessly expended, [missing clause describing an inference or effect]. We will not now stop to draw distinctions between true and false or imagined fatigue; there may be a better chance another time in treating the question of "nerves."

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) to ensure that we can maintain peak performance levels.
- B) so to speak, to the scientific order, they can be made still more successful
- C) so notably shown as in the dark days of its greatest trial
- D) and that this surplus expenditure inevitably diminishes the organism's capacity for sustained activity
- E) so that by practicing a wise economy in nerve and brain power we may realize a sustained efficiency (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 189

**Metadata:** The following passage comes from Catholic Educational Review, a serial published in 1911.

**Question:** A normal, healthy boy walking on tip-toe is about as much at home as a normal, healthy cat walking on walnut shells. MATERIAL CONDITIONS 

821 "Shame itself!" hissed Lady Macbeth in the ear of her troubled and vision-seeing spouse. "Why do you make such faces?" Has not the query a definite and pertinent application to many teachers who, [missing clause conceding a limit or exception]?

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) except when their expressions are essential tools of instruction.
- B) though composed and reserved so far as gestures and bodily movements are concerned, yet sin grievously against decorum and gravity in their unfortunate habit of facial contortion (ground truth)
- C) though the 'κνίση δ᾽ οὐρανῶν ἱκεν ἑλισσομένη περὶ καπνῶ; or for the harp hymns that wafted supplications to the sky from Mount Moriah
- D) though not immediately human, have this much of human nature about them: that they are easily spoiled for use by prosperity
- E) but who, in the midst of pressing pastoral duties, may find it less immediately relevant.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 190

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He went beyond Bear creek to the forks of the rivers and there saw it growing in great masses-acres, in fact, covered as thickly as clover fields. Wagon-loads were eventually taken away and still there appeared to be no diminution in abundance. So the search for Shortia ended. Through the further efforts of Mr. Harbison, the plant is now well known and a common one in nursery catalogues, [missing clause acknowledging a countervailing fact]. grows at its finest and best under the shade of kalmias and rhodendrons."

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though it is not always easy to find and propagate
- B) though when domesticated it
- C) although it was hoped, in vain, that "revisiting the haunts of his youth and the pleasing recollections of juvenile scenes would have salu- tary influence in arresting the disease
- D) though it remains scarce in its native habitats
- E) though in its wild state it (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 191

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** I shall be pleased in your calling on your intended journey, and hope you will consider my uncle's house as a welcome stage. I am, with all due respect, Your much obliged friend, MOSES MARSHALL. Marshall's letters speak of many long trips which meant fatigue, danger and expense. His appointment as justice of the peace curtailed excursions, [missing clause describing a tension or contrast]. About 1797 he married Alice Pennock and had six children.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but always without success
- B) though it curtailed his wanderings, it also bound him to the duties of his office
- C) but he continued exchanging specimens and seeds with European confrères (ground truth)
- D) but his family now provided him with new reasons to travel
- E) however, to get him a wife, Miss Christie; then he returned to Pennsylvania and became a public character, holding in succession the offices of surveyor-general, master in chancery and lieutenant-governor

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 192

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He studied medicine under Dr. Nicholas Way of Wilmington, but never held a medical degree, none being required at that time for practicing in Pennsylvania; but, as it was customary to attend a course of lectures, he went to those by Shippen and Rush in Philadelphia. His diary at this time shows that medicine did not wholly absorb his attention, [missing clause describing a cause or reason] Then followed a year or two employed in desultory medical work, including inoculations round about Londongrove, Pennsylvania, and in keeping an apothecary's shop "which came to nothing and less."

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because his interests lay more in the practical affairs of his community than in theoretical study
- B) owing to the fact that the authorities were wise enough to adopt the stringent sanitary precautions urged by Bigelow, who, with Ware and Flint, offered his services as investigator of the conditions in New York
- C) for the old man was at least enabled to distinguish his favorite plants as he walked in his gardens
- D) as he was also deeply engaged with his studies of botany
- E) for frequent mention is made of a certain Polly Howell and a Sally Samson, the latter "behaving for three evenings, especially the last, in a most engaging manner." (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 193

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** He still clung to the idea that its natural habitat must be, as Michaux said, in les hautes montagnes de Caroline, arguing that the point on the Catawba where it had been found was an outlying haven to which it might have been washed. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) This belief led him to continue his search for the plant in the mountainous regions of North Carolina.
- B) He inferred that the specimen had been transported downstream from its true mountain home.
- C) So with renewed energy it was searched for through the mountains, but always without success. (ground truth)
- D) So also was the scene of his first settled practice, Hopkinsville, then a wild, romantic district where he gathered patients and plants, soon getting into touch with scientific men everywhere by exchanging specimens.
- E) So he abandoned the notion that it could be found in the mountains, and searched instead in the swamps of Carolina.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 194

**Metadata:** The following passage comes from Some American Medical Botanists, a work of biography published in 1911 by Howard A. Kelly, an American naturalist and physician.

**Question:** Dr. John Tennant, an enthusiastic botanist of Virginia, swears against all disputants by Seneca snakeroot for pleurisy; the experimenter and botanist, Dr. Samuel Thomson, later uses Lobelia inflata in his "Thomsonian System" for nearly every evil, and creates endless opposition. [missing sentence describing a tension or contrast] Of the young British doctors who came over here, John Mitchell was the earliest.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But the search for remedies was keen in days when malaria and dysentery ravaged whole towns and paralyzed industry. (ground truth)
- B) Tennant’s cautious endorsement of Seneca snakeroot clashed sharply with Thomson’s zealous promotion of Lobelia inflata, igniting a heated rivalry that reverberated through the medical community.
- C) But the work which brought Bigelow into closest contact with European savants and gave him honor in his own country was the elaborate series published under the title "American Medical Botany," which was noted for its finish and beauty and avoidance of technical terms.
- D) There was sometimes, however, bloodless warfare in the botanical camp in disputation over the alleged medicinal merits of certain plants.
- E) While Dr. Mitchell's methods were more scientific and analytical, Dr. Thomson relied heavily on his own intuition and observations.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 195

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** The patient should then be examined for needle punctures and if a heroin snuffer, the mucous membrane of the nose should also be carefully examined. The writer has discovered that no matter what the amount the patient declares he is taking, he can begin with less than fifty grains per week 34
with the assurance that his patient will not suffer. This amount is steadily reduced each week, [missing clause describing a condition]. The reckless prescribing of narcotic drugs with no apparent plan of treatment and the mercenary rapacity indicated by some who hold a license to practice medicine, is to be deplored.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if they survive the horrible torture called "cure," have been turned loose in such a deplorable mental and physical condition that they have returned to the drug as the only means of obtaining relief
- B) if not relieved, usually results in wild mental confusion in which the patient often becomes destructive and violent, and in some cases may end in death
- C) provided no withdrawal symptoms or adverse reactions appear.
- D) if no painful complications arise, until the patient is cured (ground truth)
- E) until he has been entirely weaned off the drug.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 196

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** He said that on the East Side there were school children who belonged to families who were all addicts. Oh! that someone could plead for these people whose voice 10
would be heard over the tumultous sounds of condemnation that are filling the country. I believe that those who make laws believe that they are doing the right thing, and usually they are, [missing clause describing a tension or contrast]. That combined with their power and wisdom would solve the problem, I believe.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but this question at stake involves that which they won't consider as anything but weak, and that is the heart element (ground truth)
- B) while they proclaim righteousness, they often ignore the systemic inequities that fuel addiction, turning their power into a double‑edged sword that harms more than it helps
- C) but the law says it must be done
- D) but often they are misinformed about the true nature of addiction
- E) but of what kind

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 197

**Metadata:** The following passage comes from Narcotic Drug Addiction, the Modern Scourge, a short medical treatise published in 1918 by Livingston Spraker Hinckley, an American doctor.

**Question:** "In office prescribing, it should be the duty of the physician at the beginning of treatment to provide the patient with a card bearing the name and a general description of the patient, as follows: 

Name of patient, age, height, weight, color of eyes, color of hair, and having a photograph of the patient similar to the requirements of a passport. As each prescription is given the patient the physician shall indicate same on the card, with date of prescription and signature of physician." Extension prescriptions should be permitted in special cases only where a patient obtains work in a distant city may occupy him for several weeks, should not be called on to pay car fare oftener than once in three weeks to obtain his proper dosage and should not be placed in a position that makes it necessary to resort to purchase from traffickers, [missing clause describing a cause or reason]. It 38
is then that the law should step in and the State provide the ways and means to permanent recovery.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for if this happens the work of months stands firm and the fortunate individual maintains their self-control
- B) because of the loathsome nature of the disease, would be unworthy of his profession
- C) when the patient is experiencing significant travel barriers such as lack of reliable transportation, financial constraints, or safety concerns that impede regular access to medication
- D) as its principal use is to allay coughing
- E) or where the patient is unable to return due to illness.
- F) for if this happens, the work of months is undone and the poor victim is drawn back to his old habits by his loss of self control (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 198

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But if a person has in his possession trout less than six inches long he is, all the time he has them in his possession, violating the provisions of 5275 P. S. Therefore, it follows that if the warden has reasonable cause to believe that a person has in his possession a trout less than six inches long he may, under the authority of Sec. 5271, arrest him without a warrant. The application of this law must be made in view of the nature of the crime itself, and in view of the means of securing evidence showing the commission of crime, [missing clause describing a cause or reason]. I believe that if the warden, disclosing his office, sees a person under such circumstances as to indicate that the person is in the possession of trout caught in the waters of this state, that is, if he sees him coming from a brook with a fish basket over his shoulder and a fish rod in his hand, he has the right to ask that person to show him the contents of the basket and to show him all the fish
in his possession.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) if there is probable cause to suspect that the person has violated fishing regulations.
- B) particularly when the suspect is in a location where fishing is prohibited or when his conduct indicates recent fishing activity, such as carrying a fish basket or fishing rod
- C) for if the warden could not arrest a man personally until he was certain that he had in his possession trout less than six inches long it would practically nullify the law, for anyone breaking the law will naturally conceal his offense (ground truth)
- D) for the officer as the prisoner's keeper
- E) for sheriffs have such authority by statute to serve criminal process

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 199

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But anything which subjects a person to the actual control or will of another constitutes an arrest and imprisonment, whether it is physical control, locking the door of a room in which the arrested person is found, or a voluntary submission to words of arrest. An officer effects an arrest of a person whom he has authority to arrest, by laying his hand on him for the purpose of arresting him, though he may not succeed in stopping or holding him. (Mere words spoken to one are not an arrest of him; there must be something physical, [missing clause conceding a limit or exception]

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though it is enough if the party arresting touch the other, "even with the end of his finger." (ground truth)
- B) although manual seizure is not always necessary, there must be that, or its equivalent in some sort of personal coercion
- C) unless the person is under a warrant of arrest or is in a place of detention, in which case a verbal declaration by an authorized officer may constitute an arrest
- D) although this is not necessary where the person arrested must have notice from the circumstances of the case that his arrest is lawful
- E) unless the person explicitly acknowledges and submits to the arrest

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 200

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** (Extracts from a pamphlet)

By R. W. WILLIAMS, JR., 

Assistant, Biological Survey. For several hundred years the enforcement of criminal laws of all kinds in this country has been intrusted to sheriffs, constables, and police officers, and until the middle of the nineteenth century this method was considered satisfactory. [missing sentence describing a tension or contrast] The origin of the term "warden" in relation to game is somewhat obscure, but it was probably adopted in analogy to church and wood wardens in England, where the word first came into use.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But with the growing demand for more stringent enactments for the preservation of game and the increasing complexity of statutes for this purpose it was found no longer practicable to include the burden of enforcing them among the duties devolving upon general officers, and their enforcement has consequently been intrusted to special officials, usually called game wardens. ← (ground truth)
- B) However, as society evolved and new challenges emerged, particularly with the rise of industrialization and urbanization, traditional law enforcement methods began to show limitations.
- C) However, the protection of wildlife and game, unlike ordinary criminal statutes, demanded a specialized approach, as the traditional law‑enforcement bodies were ill‑prepared to address the unique challenges posed by poaching and the preservation of natural resources.
- D) However, it should be remembered that game laws and game wardens are of comparatively recent origin in the United States, and that only a short time ago the popular idea respecting fish and game was that wherever found they were almost as much the property of the individual citizen as the air we breathe.
- E) However, this may be, a game warden is now generally understood to be an officer charged with the enforcement of laws for the protection of game and fish.

**Model response:** `A
B
C
D
E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 201

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** But the necessity for a guilty mind or criminal intent does not mean that it is necessary that the person doing the prohibited act be conscious that it is wrong, for, as we have said before, ignorance of the law excuses no one. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Therefore, a person may be held liable for a prohibited act even if he did not consciously recognize it as unlawful.
- B) Thus when the selling of adulterated milk is made a crime, ignorance that the milk sold is below the standard fixed by law is no defense. (ground truth)
- C) Therefore, to make an arrest lawful, it is necessary that the person arrested should have notice that he is arrested by lawful authority.
- D) This implies that even if someone is unaware of the moral implications of their actions, they can still be held liable for their deeds.
- E) Hence it is said that every crime, at least at common law, consists of two elements-the criminal act or omission, and the mental element commonly called the criminal intent.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 202

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** THE WARDEN'S GENERAL MOVEMENTS 

Quite often we hear a warden complain that the regular violators in his territory keep so well posted on his general movements and plans from day to day that his success in apprehending them is thus seriously handicapped. This is true in many cases, [missing clause describing a tension or contrast]. It is the fate of all wardens, and the really clever ones are only stirred to increased efforts by this difficulty.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) yet they find it equally difficult to keep their own movements from becoming predictable
- B) but for general work and without local assistance and co-operation the shrewdest warden in the country will be an utter failure
- C) yet the most seasoned wardens discover that this same vigilance often drives offenders into increasingly erratic and unpredictable patterns
- D) but usually the warden is inclined to overestimate this obstacle (ground truth)
- E) however, the office of game warden is a difficult one to fill, and it is the duty of every good citizen to lend this important public servant every assistance and encouragement in the discharge of his duties

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 203

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** While one is conversing with the occupants of a camp his dog will be extremely busy searching every nook and corner for game or fish, and if there is any such there it is very certain to be brought to his master's attention by his faith-
ful dog, and the latter don't require any special training to render this service, either. It is his nature and instinct to do so. There is also a case where a warden's pointer dog discovered a large shipment of game birds in a box at a railway station. These birds were very cleverly secreted, but they could not escape the fine nose of the pointer and he "made game" as soon as he drew near them, [missing clause describing an inference or effect]. But there are "dogs and dogs.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) which promptly alerted the warden, resulting in the immediate seizure of the illegal shipment
- B) so it is presumed in choosing a dog for an assistant the warden will choose wisely, with his special needs always in view
- C) alerting the warden to their presence.
- D) so that his master was able to seize the game and apprehend the culprits (ground truth)
- E) so valuable for their fur, are not subject of larceny."

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 204

**Metadata:** The following passage comes from Powers, Duties and Work of Game Wardens : a Handbook of Practical Information for Officers and Others Interested in the Enforcement of Fish and Game Laws, a handbook published in 1910 by Harry Chase, an American writer.

**Question:** When such is found, if a part of the deer carcass was missing, the warden will make all haste to procure a search warrant and search the place before the meat has been consumed. If the process of securing a search warrant requires too much valuable time, then he will attempt to enter the place without such warrant by subterfuge. This can often be done without the officer exceeding his authority. For instance, [missing clause describing a condition]. Or he may summon the inmates and request their permission to search the place, and may do so with the occupant's, or his agent's, consent.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if the carcass is located in a private dwelling where the occupant has given prior consent or is absent, the warden may lawfully enter without a warrant by subterfuge
- B) if a part of the deer carcass was missing, the warden will make all haste to procure a search warrant and search the place before the meat has been consumed
- C) if the offender escapes and takes refuge in his own or another house, the officer is justified in breaking doors to retake him
- D) for example if the wardens have reasonable cause to believe that evidence of illegal activity is being destroyed
- E) if he finds the doors or windows open and no one to answer his knock, he may enter (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 205

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Never before had she been happier in this world; never felt before in her life as she had felt that day. Think of it all! From first to last she remembered everything, had but to close her eyes to see everything. And Ted had spoilt it all! She had done no harm, no harm. Why had he been so foolish? [missing sentence describing a cause or reason] Did he make love to ye?

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Because he had fallen for another.
- B) It was generosity.
- C) 'Twas jealousy. (ground truth)
- D) Was it because of the old days, the old happenings?
- E) He had seen her talking to another man.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 206

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** "The boys from the market," said John, diving for his hat. "Faith, it's early they'll be. Come, Nan, me girl; come away, Sarah. Ye'll forgive us runnin' off, Frank, me son? But the poor must earn their bread be the sweat o' their brow. Ay, ay." [missing sentence describing an inference or effect] All hurried down to the pier; there manned the big ferry cot and, Nan and 

Frank at one oar, Sarah at the other, John standing by the steering sweep, set her course for the Lis-
THE BARRYS.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) So the feast broke up. (ground truth)
- B) The family's urgency was palpable as they scrambled to board.
- C) So Frank pulled up and helped himself; and the cups rattled on the saucers, and the spoons clinked merrily, and John talked and talked, and Sarah minced and watched, and Nan glanced at Frank, and Frank admired Nan; and, suddenly, across the waters came a cry from the Lismahee side, a long shrill Ahoy-y-y.
- D) So there ye are, faith; there ye are."
- E) They all felt duty’s weight.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 207

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** Bless his heart, he shall grow up a credit to the name. The best of everything he'll have, the best I can give him. That is my object in life now. I have also sent Marian her money, enclosing it in a letter explaining how it came into my hands. I said little else, [missing clause conceding a limit or exception].

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) but I cannot guarantee that all will go smoothly
- B) knowing she would not welcome more
- C) even though all the right was on her side and all the wrong admittedly on his, was, as Frank himself thought, inevitable; just as it was inevitable, in the natural reaction and stress of thought and feeling, that she should now believe more than was true of Frank and his misdeeds, and express her beliefs recklessly, and say things she must afterwards regret
- D) even if it is not well over
- E) though I restrained many things (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 208

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** D'ye think, says he, if iver I'm put out of   Inishrath... Ach," cried Ted, walking on again, "it's sickenin'. Who the blazes wants to turn him out? The tyrants o' landlords, says he, the infernal tyrants o' landlords. Why, I tell ye, [missing clause describing a condition].  Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if only he had lived, lived to reap some reward of his labours
- B) if the landlord's iron hand were to grip us again, we'd emigrate and become rich in America
- C) if the landlord had his rights it's on the parish John'd be years ago (ground truth)
- D) they're squeezin' us dry with their high rents and evictions
- E) if Hugh had no worse than that to say he might keep on till kingdom come

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 209

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** It has been pointed out that the blockade of 1902 was not originally instituted on account of Venezuela's failure to pay debts, but to obtain redress for outrages inflicted upon the subjects of the blockading Powers, that Venezuela had refused the suggestion of arbitration, that Dr. Drago misunderstood the Venezuelan question, and that the Powers never intended permanently to occupy any part of Venezuela. Further, Mr. Hay, in his reply to Dr. Drago, said: "The President declared in his Message to Congress, December 3, 1901, that by the Munroe Doctrine 'we do not guarantee any State against punishment if it misconducts itself, [missing clause describing a condition or proviso] Although the practice, against which the Drago Doctrine protests is liable to be abused, it would hardly be prudent on the part of European Powers nor conducive to progress in backward States, if the right of collecting debts were surrendered.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) unless such misconduct involves an attack on their citizens and property
- B) provided that punishment does not take the form of the acquisition of territory by any non-American Power.'" (ground truth)
- C) provided that the state has failed to observe its treaty obligations or has engaged in conduct contrary to the principles of international law
- D) unless they can count beforehand on a good chance of immediate employment
- E) if the right of collecting debts were sur- See the Annual Register of 1907

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 210

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** France makes steady progress, and Italy shows a large increase, as is only to be expected, because the emigration from Italy has long been very large. It may be added that 

French goods make their way by sheer merit, for France has in her own land ample scope for her scanty population. Some advantage may be obtained by her as the head of the Latin race, [missing clause revising an implied expectation]. It is very interesting to see how Argentina has passed from small to great things in matters of trade.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but the third view is naturally that of Argentina, which is every year receiving an abundant stream of white colonists to develop the industries which cry aloud for labour
- B) but wherever there are women and luxury there will French trade flourish, and further, in machinery of many kinds France, if equalled by any other nation for excellence, is equalled by England alone (ground truth)
- C) even as its resources are comparatively scarce
- D) but her influence is tempered by the fierce competition from other nations within Latin America.
- E) but it is a peculiarity about Argentina that the people hurry to institute a great export trade long before they think of supplying themselves adequately with an article

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 211

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** The Spaniards still appear to have had a design to check the Portuguese in 94
Brazil, but Cabot evidently found them too strong in that quarter, so, says Purchas, "he thought good to busy himself in something that might be profitable; and entered the year 29 discovering the River of Plate, where he was almost three years; and not being seconded, with relation of that which he had found, returned to Castile, having gone many leagues up the River. He found plate or silver among the Indians of those countries, [missing clause describing a cause or reason] Here Purchas makes two mistakes.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for experience showed them the immense resources of their country, and proved that it could subsist upon its revenues without asking for anything from Peru or Spain (Arcos' ""La Plata," p. 241)
- B) for the Portuguese claimed indefinite territory in this direction under the convention of Tordesillas, and it behoved Spain to assert ownership before it was too late
- C) because he was looking to gain support and resources from his king.
- D) for in the wars which these Indians had with those of the kingdoms of Peru they failed to find silver, and the lack of plate hath given the river its name."
- E) for in the wars which these Indians had with those of the kingdoms of Peru they took it, and from it is called the River of Plate, of which the country hath taken the name." (ground truth)
- F) as a result of the Indians having discovered rich silver deposits in the region."

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 212

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** Beyond a doubt, in

Spanish America there is an unexampled field for a devout missionary; the foe is merely apathy, and if a warmer spirit were breathed into the Church in Argentina, and if the clergy paid more attention to the intellectual side of their calling, the results would be remarkable. [missing sentence describing a tension or contrast] Statistically, there can be no doubt that Argentina belongs unreservedly to Rome; only the merest fraction, perhaps forty thousand, of the population is outside that Church.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But if the religious indifference spreads downwards, Argentina, like France, may see her population dwindle, and her army decay, and may be prevented from taking a high position among world Powers. (ground truth)
- B) Yet the same apathy that hampers missionary zeal is evident in the clergy’s neglect of the nation’s material hardships, underscoring a stark tension between spiritual devotion and social responsibility.
- C) Yet, despite the numerical dominance of Catholicism, there exists a profound disconnection between the church and the people's hearts.
- D) However, it must be remembered that the fraternal spirit of the Greeks did not preserve them from internecine wars, and Argentina, flanked by each of the other two powerful South American Republics, cannot afford to neglect her armaments.
- E) There is, however, little doubt that Argentina possesses a good army, sufficient for the defence of even her very vulnerable frontier.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 213

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** He also attempted to settle the country, but without success, for Thomas 

Cavendish (who named Port Desire after his own ship) saw in 1586, twenty-three famished Spaniards, the only survivors of the city of King Philip, founded by Gamboa on the Straits. These poor creatures were trying to return to the Plate district. [missing sentence describing an inference or effect] In 1590 John Davys found a solitary straggler here, and the bold navigator thus describes his barren experiences: "Here we made a boat of the boards of our chests, which, being finished, we sent seven armed men in the same on land on the north shore, being wafted on land by the savages with certain white skins; who, as soon as they came on shore, were presently killed by an hundred of the wild people in the sight of two of our men, which rowed them on shore, which two only escaped back again to us with the boat.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Cavendish, therefore, named the deserted settlement the Town of Famine, and it retains the name of Port Famine to this day." (ground truth)
- B) Their return was fraught with danger, as hostile natives constantly threatened their passage.
- C) Thus, because the land in question contained a number of different tribes, they received by analogy the name Chacu, which the Spaniards have corrupted into Chaco."
- D) This grim discovery underscored the futility of earlier attempts at colonization and the harsh realities of survival in this unforgiving land.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 214

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** About twenty years later another traveller estimates the population at fifteen thousand and says: "The city presents an extremely clean and orderly appearance; the streets, which intersect at right angles, are well kept and well lighted. The only manufacture in the place is that of leather. There is no newspaper, although formerly there were two weekly journals published. . . . The climate is very salubrious, [missing clause conceding a limit or exception]. There are no foreigners in the town, nor even in the province, except a few French and two or three English: the government architect is a Frenchman, who possesses both wealth and influence."

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) except during certain times of the year when winds bring dust from the neighboring plains
- B) though the rain does not fall in sufficient quantity (ground truth)
- C) although rain is continuous and abundant
- D) except for the brief, oppressive heat that grips the town in midsummer
- E) though perhaps the best they can obtain."

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 215

**Metadata:** The following passage comes from Argentina, a work of history and social description published in 1910 by W. A. Hirst, an American writer.

**Question:** There is, in fact, little interest in any such matters on the part of the population, and the President is now lamenting the disinclination to a sea-faring life, and of recent years steps have been taken to obtain more satisfactory results; but the total mercantile marine, as yet, amounts to barely 100,000 tons. There is, however, a College for training officers, and also engineers and stokers for the mercantile marine, and there is a Pilot School, and various measures show that the authorities are alive to the importance of the question. In his last Message to Congress the President said: "One of the principal reasons for granting privileges to ships flying the Argentine flag is the employment of native crews, [missing clause describing an inference or effect] The Argentine sailor is a land-conscript, laboriously taught an unfamiliar art, which he learns wonderfully well.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that eventually the Argentine flocks were as sorely in need of new blood as were those of France, Germany, or Russia, which, until the middle of the eighteenth century, had never had the benefit of a cross with the old Spanish strain
- B) so that it is very easy to find one's way about, for if a pedestrian desires a cross street, say to the north, he has only to march northwards up any given street and he must eventually reach his designation
- C) which secures a reliable workforce for the nation's merchant fleet."
- D) and thus fostering a sense of national pride and economic independence."
- E) so that the nation's sons may find a new path of life, and the navy a fresh source from which to draw sailors in case of an emergency." (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 216

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** We ourselves have not forgotten, and never can forget the hundreds of thousands of precious lives that were spent in order that there might be written in our constitution, "Neither slavery nor involuntary servitude except as a punishment for crime shall exist within the United States or any place subject to their jurisdiction." Wisely, therefore, do we celebrate anniversaries like these, that we may renew our allegiance to the great principles of constitutional liberty, and resolve that what cost our ancestors so dear shall not lightly be sacrificed by us. It is natural that we should be dazzled by the wonderful growth which has sprung from the seed planted at Jamestown, that we should be intoxicated by a material prosperity unexampled in the history of the world, and by the evidences of enormous national wealth and strength which surround us, [missing clause describing a tension or contrast]. We are here to honor those who laid deep and strong the foundations of our Commonwealth, because we know that to the principles which they adopted in framing our government we
owe the liberty that has made our wonderful progress possible.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but we shall lose the whole meaning of this celebration-we shall fail completely to learn its lesson-if we give ourselves up to the contemplation of our past and the glorification of ourselves (ground truth)
- B) but we shall preserve the entire meaning of this celebration—we shall fully grasp its lesson—only if we give ourselves up to the contemplation of our past and the glorification of ourselves
- C) yet, amid this prosperity, the shadows of past injustices linger, reminding us that freedom is a continual struggle
- D) yet it is essential to remember the struggles and sacrifices of those who fought for freedom.
- E) but simply the enactment of a law, a fundamental law, which defined the powers of the government and secured the rights of the citizen in this great Commonwealth
- F) but it may be not unreasonably said that the preservation of the States, and the maintenance of their governments, are as much within the design and care of the Constitution, as the preservation of the Union and the maintenance of the National Government

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 217

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Against these theories by which our rulers of to-day seem to claim for themselves peculiar wisdom let us oppose the words of Washington, that greatest of Virginians, in his Farewell Address:- "If, in the opinion of the people, the distribution or modification of the constitutional powers be in any particular wrong, let it be corrected by an amendment in the way which the Constitution designates. But let there be no change by usurpation, for, [missing clause conceding a limit or exception] Let us oppose the language of the Supreme Court whose unanimous opinion has just been expressed in these words:— "The proposition that there are legislative powers affecting the nation as a whole which belong to, although not expressed in, the grant of powers, is in direct conflict with the doctrine that this is a Government of enumerated powers.

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) for though it may seem expedient at some point to act beyond our constitutional bounds.
- B) unless it is indispensable to safeguard the common good or to avert a threat to the nation’s security.
- C) though this in one instance may be the instrument of good, it is the customary weapon by which free governments are destroyed." (ground truth)
- D) although not expressed in, the grant of powers, is in direct conflict with the doctrine that this is a Government of enumerated powers
- E) though, if we are to have usurpation, it is more in accord with the genius of our institutions to have it come through the action of the legislature, whose duty it is to make the law, rather than through the action of the President, whose duty it is to obey and execute it

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 218

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Why is it that the President, whose ideas on most subjects are accessible to his countrymen, has preserved such an absolute silence on the burning question of tariff reform, and has, indeed, displayed such fierce indignation at the mere statement that he had expressed himself on the subject? It is because he fears that any action in this direction will divide his party. [missing sentence describing a cause or reason] The politicians and the protected interests have formed an unhallowed partnership, to which the manufacturers have contributed cash in the guise of campaign contributions and the politicians have contributed time and speeches.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) He is restrained by the dread that any movement toward tariff reform would fracture his own party, thereby threatening the unity he seeks. ←
- B) It is precisely because the people have such confidence in the President's high purpose and trust him so implicitly that such propositions coming from him are full of danger.
- C) It is because the Republican party owes its power, in large part at least, to the support of the manufacturers, and depends for the sinews of war on the “fat fried out of" them, to use the phrase of one who was high in the party councils. (ground truth)
- D) This is due to the complex web of political alliances and monetary influences at play.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 219

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** We are here to honor those who laid deep and strong the foundations of our Commonwealth, because we know that to the principles which they adopted in framing our government we
owe the liberty that has made our wonderful progress possible. [missing sentence describing a tension or contrast] The past is indeed glorious, but we are living in the present, and on our course in that present depends our country's future.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet the same principles that once steadied us now confront us with new trials, demanding that we adapt while remaining true to our founding ideals. ←
- B) But, as we meet to commemorate their acts, it becomes us to inquire how their work is faring in our hands, how we are preserving and maintaining the heritage of principle which they handed down to us. (ground truth)
- C) But there is a far more important question, which underlies the whole discussion and upon which men should not differ.
- D) Yet, while we celebrate their achievements, we must also confront the challenges of a rapidly changing world and the evolving needs of our citizens.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 220

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Judge Story, a strong advocate of the supremacy of the treaty-making power, in Section 1508 of his work, uses this language, speaking of the treaty-making power, - "But though the power is thus general and unrestricted, it is not to be so construed as to destroy the fundamental laws of the State. A power given by the Constitution cannot be construed to authorize a destruction of other powers given in the same instrument. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) This implies that while the treaty-making power is expansive, it must coexist harmoniously with other constitutional provisions.
- B) The question, therefore, is whether the people of the United States wish to change the manner in which they exercise their own powers, whether they wish to do less through local governments and more through the general government, and this change can lawfully be made only by the people through an amendment to the Constitution.
- C) Therefore, the treaty power must be exercised in a manner that preserves the constitutional rights of the states.
- D) It must be construed, therefore, in subordination to it; and cannot supercede or interfere with any other of its fundamental provisions. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 221

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Let us, as citizens of our common country, resolve that they shall be obeyed by high and low alike, for only through such obedience can our freedom be preserved. Let us treasure the counsel so recently given at Jamestown by the eminent statesman who now represents England in this country, Mr. Bryce. “Cherish alike and cherish together liberty and law. They
are always inseparable. Without liberty there is no true law, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because law sinks into being the collective will of the community, instead of the wfree and unbounded whim of an arbitrary ruler
- B) as citizens of our common country, resolve that they shall be obeyed by high and low alike, for only through such obedience can our freedom be preserved
- C) because law sinks into being merely the will of an arbitrary ruler or a selfish class, and ceases to be the will of the whole community (ground truth)
- D) because law without freedom becomes arbitrary edict that enslaves the people, eroding the very foundations of justice for all

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 222

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** of the popular vote, but sixty-two per cent. of the electoral votes, and his party had a very large majority in the House. These illustrations might be multiplied indefinitely. Do such figures show that the result of Federal elections expresses the people's will? How often have the Senate and the House been controlled by different parties, [missing clause describing an inference or effect]?

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) leading to legislative gridlock and inefficiency
- B) so that no legislation on burning questions was possible (ground truth)
- C) so that his constituents may thus practically be disfranchised
- D) which indicates that the Senate and House can be governed by different parties, leading to conflicting legislative priorities.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 223

**Metadata:** The following passage comes from Federal government and the states; address delivered at Norfolk, Va., on June 29, 1907, at the celebration of the adoption of the first Virginia constitution, a public address published in 1907 by Moorfield Storey, an American lawyer and civil rights activist.

**Question:** Is the Senate a more efficient interpreter of the popular will? How much are the people consulted in the choice of senators? Is it mere accident that so many of them are conspicuous mainly for their wealth and the qualities by which wealth is acquired? If we turn to the West, shall we say that Senator Clark was chosen by Montana for his ability as a statesman, or, [missing clause describing a condition]? Was

Quay the free choice of Pennsylvania, or Dryden of New 

Jersey?

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if not to control, legislation by Congress ←
- B) if we look nearer home, must we assume that Senators Platt and Depew represent the character and purpose of New York (ground truth)
- C) if the senator has earned the trust of the electorate through a record of honest and diligent public service

**Model response:** `A, B, or C.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 224

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Love of truth, country, river, cushat, mousie, daisy, lassie (be she Mary, Eliza, or Jean),—that was 

Burns's literary biography. Love means melancholy; and it is quite beyond credence persistently shadows hang over all Burns wrote, until you take his poems and go over them at a sitting. Rollicking he seems to be, [missing clause describing a tension or contrast]. The fear of parting is on his meeting with Mary.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but his love speaks passion at the hour
- B) but sad at heart you will always find him (ground truth)
- C) though his verses brim with gaiety, his heart is ever in sorrow
- D) even when writing about the most joyful moments

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 225

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** He was a creature of moments. Laughter or weeping, no one could tell which should proceed from this minstrel. A big heart, a feverish passion, a lust for wine and women, a manhood burned out like a candle to the socket,-this is Burns. He was a man with his full share of weakness and 14
and Other Essays wickedness, but with a large endowment of genius, nobility, and vision; and we pass his aberrancies by tenderly, [missing clause describing a cause or reason]. With Burns the world has forgotten much.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because of the brilliance of his poetry
- B) for the sake of his sublime artistry
- C) because of the manhood he did possess (ground truth)
- D) because new beauty reveals itself at every step
- E) for Burns is the greatest writer of dialect

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 226

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Such rivalry as existed between Genoa and Venice burned hot between the country which gave William birth and the one over which he swayed scepter as king. In ports even at the antipodes the 

Dutch and English merchantmen were competitors. [missing sentence describing an inference or effect] William the Great of Englaud 117 

William belonged to that nation; and every sign of love for his country or his countrymen seemed to their distempered vision a slight to England and Englishmen.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) This intense rivalry often led to conflicts and power struggles between the two nations.
- B) Englishmen were therefore jealous of any favor shown to their commercial rivals. (ground truth)
- C) It thus arose naturally, if not wisely, that the foreign troops of William's guard were endured with distrust, and, in 1697, over the manifest protest of the king and in spite of his service, they were compelled to return to Holland.
- D) So, in the light of history, England's cause was not altogether hopeless.
- E) Thus the rivalry inflamed a fervent sense of national pride among the populace.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 227

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Humanity must bear the imputation of being unclean in body, as in spirit. And in this Jew's Ghetto are hints of comedy and bits of tragedy, and boisterous merrymaking native to all estates. Poverty is no dethronement of delight. Heroisms, too, are here. Souls are the tenting-grounds of the heroic. No life is cut off from the possibility of nobleness; and the revelation of an old father, conscious that his presence jeopards his son's happiness; who feigns a brother in
far-off America, who has sent for him to share his wealth, and so leaves this Ghetto, [missing clause conceding a limit or exception]. Beyond dispute we are debtors to this guide, who has led us along so untrod, novel, and fascinating a path.

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though the contribution is one we would not willingly let die
- B) though this departure may seem a liberation, it is still bound by the invisible chains of memory
- C) but with a heavy heart, knowing he will never see his son again
- D) though in him it arose from the many-sidedness of genius
- E) though to leave is like tearing out his living heart, and turns gray face toward an unknown land,such sacrifice renews the courage of us all (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 228

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** He was not bad, weak rather. Sinned, he had. He and Hester were joint criminals, she bearing her shame before the world; he canonized by that same world. Conscience cried aloud, "Bear shame with her;" and his spirit cried, "How can I? How can I?" [missing sentence describing a tension or contrast] Its speech never silenced.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But Daniel Deronda is the Jew as modern gentleman, and is altogether admirable.
- B) Yet, his public reputation whispered otherwise.
- C) But the question need not delay for answer.
- D) But conscience spake on. (ground truth)
- E) He celebrated, she mourned.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 229

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** Worth, manliness, courage, and virtue were his; but these, men could not see, and
and Other Essays so it is easy to discover that the geniality which had been so marked in the manner of Charles, but was so lacking in that of William, should have brought a contrast to the king's hurt. Men are easily deceived. They do not pierce beneath the thin disguise of externality to discover genuine and unapproachable merit. [missing sentence describing a cause or reason] He loaded Portland with honors.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Charles's lack of geniality, which was an attribute men valued too highly, was the cause.
- B) Because the king's heart had been so moved by Portland's unwavering fidelity, he resolved to bestow upon it a bounty of honors.
- C) Another chief cause of William's popularity was his stinginess.
- D) Another chief cause of William's unpopularity was his partiality to his own countrymen. (ground truth)
- E) It was the cause of our common humanity.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 230

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** It is alternately invaded by the hyperborean legions and by the wilting sirens of the tropics. Icicles hang always on its northern heights; its seacoasts are fringed with mosquitoes. There is for a third of the year a contest between the icy air of the pole and the warm wind of the gulf. [missing sentence describing an inference or effect] It is the normal condition in New England.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) The result of this is a gradual, steady, even warming.
- B) The result of this is a compromise: the compromise is called Thaw. (ground truth)
- C) So plainly marked and well-trodden are they, that it is easy to mistake them for trails made by hunters; but he who follows one of them is soon in difficulties.
- D) Consequently, the townsfolk must keep both an ice pick and a sun hat in their pockets.
- E) This creates a unique and ever-changing environment where the extremes of winter and summer battle.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 231

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** Not being able to recognize any tracts, I have no evidence that I had so travelled, except the general testimony of lost men. The compass annoyed me. I've known experi enced guides utterly discredit it. It could n't be that 

I was to turn about, and go the way I had come. [missing sentence describing a tension or contrast] Better listen to science than to spunk."

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But consider what a shot it was!
- B) The lure of uncharted territory tugged against the fear that each step might unravel the very fabric of reality's fragile illusion today.
- C) But what is this in the morning journal at breakfast?
- D) Nevertheless, I said to myself, "You'd better keep a cool head, my boy, or you are in for a night of it. (ground truth)
- E) The very instrument designed to guide me seemed to contradict my instincts and the wisdom of those who had traversed these woods before.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 232

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** I should get close to the log, crawl under my hat, strike the match, see it catch, flicker, almost go out (the reader painfully excited by this time), blaze up, nearly expire, and finally fire the punk, thank God! And I said to myself, "The public don't want any more of this thing: it is played out. Either have a box of matches, or let the first one catch fire." In this gloomy mood I plunged along. The prospect was cheerless; [missing clause describing a cause or reason]. I fancied I could hear the tread of the stealthy brutes following their prey.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for, apart from the discomfort that fire would cause, it tends to attract wild beasts
- B) for, apart from the comfort that a fire would give, it is necessary, at night, to keep off the wild beasts (ground truth)
- C) because the valley lay shrouded in a perpetual gray mist, with no sign of life
- D) for we had not expected to pass that night in the woods
- E) because I knew that if I failed to set my fire ablaze with this match, the wolves would be upon me

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 233

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** When I guessed that I must be close to the river, I suddenly stepped into mud up to my ankles. It was the road, running, of course, the wrong way, but still the blessed road. It was a mere canal of liquid mud; but man had made it, and it would take me home. I was at least three miles from the point where I supposed I was near at sunset, and I had before me a toilsome walk of six or seven miles, most of the way in a ditch; [missing clause describing a tension or contrast]. I was safe; I knew where I was; and I could have walked till morning.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a tension or contrast]:

**Category:** cloze_contrastclause

**Choices:**
- A) but it is true to say that I hated every step of it
- B) but it is truth to say I enjoyed every step of it (ground truth)
- C) however, of dropping off to sleep, somebody unfortunately notes a drop of water on his face; this is followed by another drop; in an instant a stream is established
- D) but a succession of falls, cascades, flumes, and pools, that would delight an artist
- E) yet I was exhausted and famished
- F) though the darkness of night could hide unseen perils

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 234

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** The spur we chose for our escape looked smooth in the distance; but we found it bristling with obstructions, dead balsams set thickly together, slashes of fallen timber, and every manner of woody chaos; and when at length we swung and tumbled off the ledge to the general slope, we exchanged only for more disagreeable going. The slope for a couple of thousand feet was steep enough; but it was formed of granite rocks all moss-covered, [missing clause describing an inference or effect].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so far was I from feeling any uneasiness about this, that I quickened my pace again, and, before I knew it, was in a full run; that is, as full a run as a person can indulge in in the dusk, with so many trees in the way
- B) making every foothold a treacherous gamble, as moss‑slicked granite threatened to give way beneath us
- C) so that the footing could not be determined, and at short intervals we nearly went out of sight in holes under the treacherous carpeting (ground truth)
- D) making every step treacherous and slow
- E) so as to be sure to strike either the clearing or the road, and not wander off into the measureless forest

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 235

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** She knew, by their uncertain yelping up and down the opposite bank, that she had a little respite: she used it, however, to push on until the baying was faint in her ears; and then she dropped, exhausted, upon the ground. This rest, brief as it was, saved her life. Roused again by the baying pack, she leaped forward with better speed, [missing clause conceding a limit or exception]. It was still a race for life; but the odds were in her favor, she thought.

Write a clause appropriate for this book that could stand in the position marked by [missing clause conceding a limit or exception]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though without that keen feeling of exhilarating flight that she had in the morning (ground truth)
- B) except when her strength began to fail
- C) although they said it was small for a bear
- D) though her speed was more exhilarating than it had been in the morning
- E) though they were still hidden by a ridge) she turned away towards the north, and kept on at a good pace
- F) though the pack surged ahead, her lungs burned and she could barely breathe slowly

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 236

**Metadata:** The following passage comes from In the Wilderness, With a Biographical Sketch, a book of travel and natural description published in 1878 by Charles Dudley Warner, an American essayist.

**Question:** He intends no harm: he only gratifies a curiosity to see if he can hit the mark. Where shall he draw the line? Doubtless he might throw a stone at a chipmunk or shout at a loon. Might he fire at a mark with an air-gun that makes no noise? He will not fish or hunt on Sunday (although he is no more likely to catch anything that day than on any other); but may he eat trout that the guide has caught on Sunday, [missing clause describing a condition or proviso]? Is there such a thing as a vacation in religion?

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if such a cave exists
- B) provided he does not break the silence of the day
- C) if the guide has taken them legally during the week
- D) if the guide swears he caught them Saturday night (ground truth)
- E) if none of his congregation are present

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 237

**Metadata:** The following passage comes from Letters, a volume of personal letters published in 1921 by Yuen Ren Chao, a Chinese linguist.

**Question:** Traveling in a ship is another of my dream-frequenting fancies. on "My parents and cousins returned home when I was about eight; and, apologizing to Stephan Leacock ("Sunshine Sketches,' Preface) I decided to return with them. First ride on a great big sea-going ship! Occidental foreigners, playing cards. They must be talking my home dialect, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for miles, not since July 13-15 1920, which was some ten thousand miles ago
- B) because they were speaking in their native tongue
- C) for I could not understand them (ground truth)
- D) because the sounds struck me as at once unplaceable and eerily familiar

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 238

**Metadata:** The following passage comes from Letters, a volume of personal letters published in 1921 by Yuen Ren Chao, a Chinese linguist.

**Question:** (Second shock. I've forgotten the gentle art of avoiding treading on people's toes.) Seasick only day in whole voyage. Read Pasteur's Life. One professor of Greek played hymns with a quasi-arpeggio for nearly whole morning and praught at us Sundays. One passenger was writing a book on the passengers, [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but he rarely talked with anybody (ground truth)
- B) but you may be shocked that I liked her attitude toward Christianity
- C) but if we agree each to try to follow the other's tempo and expression, them we have musical peace
- D) but I had expected more excitement
- E) but his constant interviews of the other passengers became wearisome indeed

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 239

**Metadata:** The following passage comes from Letters, a volume of personal letters published in 1921 by Yuen Ren Chao, a Chinese linguist.

**Question:** Such words raise one's goose flesh I convinced several Chinese of the desirability and feasibility in the near future of an alphabetic writing of Chinese. August 17, 1920, Water is Yellow. This was Shanghai! A money changer spoke with a Wusih accent. [missing sentence describing an inference or effect] How strange that I didn't find Shanghai strange!

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Therefore, Shanghai seemed familiar, not strange at all.
- B) But I failed to transact business with him in Wusih dialect.
- C) So here moi aussi.
- D) Hence, the city's vibrant mix of accents and cultures made me feel strangely at home.
- E) So I transacted business with him in Wusih dialect. (ground truth)
- F) So we have possibly ten times as many sounds to build our polysyllabic diction on as Japanese.

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 240

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** He then crossed the Balkan Mountains, and took Adrianople. General Paskjevitch, in the meantime, was most fortunate in Asia. After the victorious battles of Konouly and Millidust, he had taken Erzerum, and repulsed the Pasha of Trebizond in every direction. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) He, therefore, when the rising of the Maghyars threatened to make an end of the Austrian Empire, sent an army of 170,000 men, under the command of Paskjevitch, Sass, and Rüdiger, into Hungary, by which he promptly suppressed the movement, and delivered many of the noblest patriots to the scaffold, prepared for them by a government, which, unaided, could not have resisted their struggle for liberty and independence.
- B) In consequence of this glorious success, the senate entreated Peter to accept the title of Emperor and "the Great," to which request he graciously consented.
- C) Thus, the combined successes of these generals had a significant consequence on the overall campaign and led to Russian control over key strategic areas.
- D) The Sultan, in consequence of all these reverses, was obliged to yield, and peace was at last established by the Treaty of Adrianople of the 14th September, 1829. (ground truth)
- E) Consequently, the Ottoman Empire's morale collapsed, prompting the Pasha of Trebizond to seek a swift capitulation, while Russian forces pressed forward with confidence toward the heart of empire.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 241

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** It is placed under the direction of a head-herdsman, or taboontchick, who, with his assistants, attends to all the management of the horses and to their safety from horse-thieves and wolves. As he is responsible for every horse of his herd, his vigilance and constant application are such as only a taboontchick (chosen mostly from the Cossacks) could stand. He knows no sheltering roof, but must be on the alert night and day, [missing clause describing a condition or proviso]. Sleeping, so to say, with one eye open, he must be ready on the slightest alarm to spring into the saddle and assist the brave stallions in their defence of mares and foals against HORSES.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) unless driven to it by hunger
- B) provided that no storm or wolf approaches, his vigilance must never waver, lest danger strikes
- C) if only the pole and carriage-wheels are prosti-Russki fashion
- D) unless he is certain there is no danger to his herd
- E) if he would not risk the loss of the hard-won earnings of the whole year (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 242

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** These Tchouds had been probably driven out of their original country by other neighbours, who also have left their own particular traces; for in some places on the banks of the Yenisseï and the Touba have been found many inscriptions altogether different from those of the Tchouds, and which seem to belong to the time of Tchinggis-Khan. Remnants of the wild hordes of Asia still roam about Siberia, and are called Tartars, although they are not all of Turkish origin, [missing clause revising an implied expectation]. We know little about these tribes errant, and the chances of a closer acquaintance are daily diminishing, owing to the growing Russian colonization, which threatens soon to absorb all these tribes within its own numbers.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but nobody has as yet succeeded in deciphering the inscriptions
- B) however, they are not always easy to identify
- C) but their houses are palaces compared with the "tchoums" of the Samoyedes
- D) but are strongly mixed with Finnish and Mongolian elements (ground truth)
- E) but many are mixed, not purely Turkish indeed

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 243

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl.

**Question:** In consequence of a second defeat on the 25th September, he retreated to the southern bank of the Araxes. Paskjevitch, successor of Yermalov, carried the war on to the Persian soil, and began by storming the fortified convent of Etchmadsin. After many indecisive engagements, General Pankratiev succeeded in seducing several of the allies of Persia from their allegiance, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) in order to turn the tide of the war
- B) because he leveraged their mistrust of Persian leadership, offering promises of autonomy and lucrative trade privileges, and secure their loyalty, thereby undermining their confidence in the imperial cause
- C) for this people, which had always fought for its faith, so as to prefer the wild life of outlaws in the steppes to an easy existence held out to conversion, has ever remained strictly faithful to its religion
- D) owing to which, on the 6th July, the Persians lost the battle of Nakhitshevan, on the 7th the fortress of Abbas Adad, and soon after the battle of Abaran (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 244

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** There are now only about 16,500 individuals of this tribe in Russia, who are all Mohammedans, and occupying themselves with the breeding of cattle and horses. In 1860 they were still living, to the number of 40,000, in the north-western district of the Azov country, but these, together with the Crimean Tartars (80,000), have since emigrated to Turkey. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet, their population has dwindled significantly over time.
- B) They have, however, cause to repent of their rash piety, for the holy soil did not offer them anything like what they had left behind; and it is said that they are returning in large numbers to the meat-pots of Crimean Egypt.
- C) Nevertheless, their numbers have shrunk, leaving only a few thousand in Russia.
- D) They have however (since 1865) emigrated in large numbers to Turkey.
- E) It is said, however, that many of them have since come back. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 245

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** 235 Personal experience in the intercourse with representatives of all classes of Russian society, military and civil, have never afforded the writer a single instance of vindictive feelings existing in Russian minds with regard to England and its successes in the Crimea. On the contrary, they invariably seemed to look upon that war, [missing clause acknowledging a countervailing fact]. Unlike another nation, nearer home, they did not dream of vengeance, but with magnanimous ingenuity seemed to acknowledge the superiority of political and social advancement of their former adversaries, whose example, which had been so forcibly set before them, they ought to follow in more than one respect.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although it was fought on their own soil
- B) though deeply sympathizing with that unhappy nation, objected to any enfeeblement of Turkey
- C) though disastrous to their arms, as a natural and necessary phase of their political development (ground truth)
- D) although in good society they resemble those of other countries
- E) although the conflict left deep scars, they remained free of bitterness toward England in their hearts

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 246

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl, an unknown unknown.

**Question:** The aged, the decrepit beggar at his door, even the wretched criminal dragging his chains to a Siberian prison, never go empty from his village; for even the poorest villager will fumble for some stray coppers in his pocket, in order that he too may contribute his mite towards the relief of his fellow-man. The Russian cares little for his parental hearth, or for the parish soil he helps to cultivate. [missing sentence describing a cause or reason] In their villages the Russians feel themselves intimately bound only to their families, their neighbours, to the parish, or to individuals, but not to the ground or the place they inhabit; and in this respect they strikingly differ from the Germanic and Latin races, and even from the western Slavonians, in whom the love of the paternal hearth is inextinguishable.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) They curse the She'ites, because they fancy themselves to be Sounnites, but they have not the remotest conception of the difference.
- B) The cause of this indifference is the absence of landed property amongst the peasants. (ground truth)
- C) They have, however, cause to repent of their rash piety, for the holy soil did not offer them anything like what they had left behind; and it is said that they are returning in large numbers to the meat-pots of Crimean Egypt.
- D) The cause of this is because the Russian's sense of community and shared humanity extends far beyond just their family and home.
- E) Because their ancestors migrated constantly, Russians view land as transient, not ancestral, but family.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 247

**Metadata:** The following passage comes from Religious History of Japan : an Outline With two Appendices on the Textual History of the Buddhist Scriptures, a history published in 1907 by Masaharu Anesaki, a Japanese intellectual and scholar.

**Question:** To meet the need there arose, in the middle of the 18th century, an ethical movement which was humanitarian in its spirit and popular in its practice. The movement is known as the Shingaku, or Mental Learning, which means the culture of conscience. The mind, it was taught, is the reflex of the heavenly reason in man. Just as a mirror, when cleaned, reflects every object as it is, [missing clause describing an inference or effect]. Love, patience, truthfulness and vigilance were taught as the virtues which were the means and at the same time the aim of the mental culture.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so Buddhism was to a great degree influenced by the Shinto religion
- B) so it must have been the case with Buddha's
- C) so, when the mind is pure, it can guide one's actions and thoughts towards virtue and enlightenment
- D) so our mind, when it thinks and wills according to its innermost conscience, shows us the true Way (ground truth)
- E) so the mind, like the polished mirror, mirrors heavenly reason, revealing truth, guiding actions toward virtue for all

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 248

**Metadata:** The following passage comes from Religious History of Japan : an Outline With two Appendices on the Textual History of the Buddhist Scriptures, a history published in 1907 by Masaharu Anesaki, a Japanese intellectual and scholar.

**Question:** Nevertheless, protection by and interferences on the part of the government and the ruling clans always affected the relative positions of the various religions, Every prominent religious body enjoyed, more or less. a kind of state patronage. Thus the ambition to secure the privilege of being sanctioned and protectedby the rulers as orthodox was responsible for the chief effort of many a religious leader. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet the expectation that this endorsement would guarantee enduring influence proved fragile in the face of relentless political competition.
- B) But the toleration of various religions and the many attemps at compromise have been characteristic of the whole history. (ground truth)
- C) However, the pursuit of orthodoxy did not always align with the pursuit of spiritual purity.
- D) But the general tendency of the religion, near the dawn of history, was towards the supremacy of the Heaven-Shining Deity, built upon the basis of an indiscriminate worship of various deities and spirits.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 249

**Metadata:** The following passage comes from Religious History of Japan : an Outline With two Appendices on the Textual History of the Buddhist Scriptures, a history published in 1907 by Masaharu Anesaki, a Japanese intellectual and scholar.

**Question:** The Heaven- Shining, the progenitrix of the ruling family, is accompanied often by her noumenon, the High-Producing Deity, who follows behind her. On the other hand, the Great-Land-Master and the Small-August- One, the offsprings of the Impetuous, appear as formidable spirits and were worshiped without regard to clan distinctions. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus the symbolisation and mystification of the doctrine and the use of those symbols and mysteries for any end find no limit.
- B) Thus we see in the mythology a certain cycle of the oppositions of the two struggling principles or powers. (ground truth)
- C) Consequently, the veneration of these spirits transcended clan boundaries, illustrating the syncretic integration of indigenous kami with Buddhist deities.
- D) Thus Japanese Buddhism during the four centuries from the ninth onward was chiefly a eudæmonistic mysticism.
- E) Thus, the presence of the High-Producing Deity signifies the importance of fertility and abundance in the cultural narrative.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 250

**Metadata:** The following passage comes from The Cellar-house of Pervyse : a Tale of Uncommon Things, From the Journals and Letters of the Baroness T'serclaes and Mairi Chisholm, a memoir published in 1917 by Geraldine Mitton, a British biographer and novelist.

**Question:** And when, a couple of months later he was suddenly transferred elsewhere, and went without a good-bye, though she saw him march off, it seemed as if the whole side of Pervyse had been laid bare, and the Germans might sweep in at any moment! One day a little later she found it impossible to get a necessary matter attended to. "I will go myself, and speak to Headquarters about it," she said; "it's the only way to get anything done." [missing sentence describing an inference or effect] She had been feeling like that lately, as if she rather wanted to blow someone up.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence, it followed that her resolve to confront Headquarters directly was not merely about the immediate issue.
- B) So she mounted her motor-cycle and went off, intending to let Headquarters see how very unpleasant she could make herself when they would not attend to her wishes. (ground truth)
- C) Hence, she decided to bypass the usual chain of command, hoping a direct appeal to Headquarters would expedite the matter and prevent further delays for unit and morale.
- D) So he began to talk to Mairi with a warm degree of comradeship, and just then Gipsy drove up, with the exhausted chauffeur beside her, as miserable and ashamed as a man could be.
- E) So Mairi sat there in charge of some wounded men who lay just inside the door of a cottage, and she watched the shells getting heavier and heavier.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 251

**Metadata:** The following passage comes from The Cellar-house of Pervyse : a Tale of Uncommon Things, From the Journals and Letters of the Baroness T'serclaes and Mairi Chisholm, a memoir published in 1917 by Geraldine Mitton, a British biographer and novelist.

**Question:** Inch by inch she crept past, judging the distance, and as her pupils widened she was enabled to see a little, and then she breathed once more as she gained the pavé, which, compared with the mud at the side, seemed safety. [missing sentence revising an implied expectation] Once more she had to get down and investigate; it proved to be a shell-hole quite large enough to swallow the whole ambulance and its contents.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, there was nothing else for it: these precious lives inside depended on her; so, bitterly cold and soaked to the skin, she crept back to the steering-wheel and essayed the difficult task.
- B) But she was not by any means out of the wood, for not a quarter of a mile further her groping sight revealed another black mass, this time so big that it was visible without the aid of a shell-burst. (ground truth)
- C) However, the silence that followed was not the calm she had imagined, but a subtle, almost imperceptible rustling of unseen leaves, as if the very air itself were eager to lure her further into the dark, uncharted depths.
- D) But directly she had entered it she was filled with anxiety to get out in a hurry; such a smell of stale tobacco, burnt fat, and other worse odours, permeated the place that it might be imagined even a shell would rebound harmlessly off the solidity of the atmosphere!
- E) However, the ground ahead was anything but clear.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 252

**Metadata:** The following passage comes from Thucydides Mythistoricus, a critical treatise published in 1907 by Francis Macdonald Cornford, a British classical scholar.

**Question:** Of course, foreign families who migrated to Athens before the Persian war would be quite Athenianized by the end of the fifth century. But the great influx must have been after the foundation of the Piraeus. From 480 to 450 Athens granted citizenship freely. Pericles, perhaps in alarm at this increasing infiltration of foreign blood, made the conditions of naturalization harder. [missing sentence revising an implied expectation] At the beginning of the Peloponnesian war there were 9,000 adult men in this condition, who, with their families, made up an alien population of 30,000.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, the number of metics (resident aliens) did not necessarily decrease.
- B) But the great influx must have been after the foundation of the Piraeus.
- C) But when it is realized that before the war the countrypeople were not a factor in politics, we see that the majority which Pericles had to work with must have largely consisted of this same commercial and industrial class.
- D) But the unnaturalized alien was still, for industrial purposes, as free as the citizen, and had the protection of law. (ground truth)
- E) Yet, despite Pericles' tightened naturalization, the alien population in Athens swelled to 30,000, far exceeding contemporary expectations for the period.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 253

**Metadata:** The following passage comes from Thucydides Mythistoricus, a critical treatise published in 1907 by Francis Macdonald Cornford, a British classical scholar.

**Question:** But it becomes ironical in the strict sense only when the persons begin to have elementary characters and minds, and so to be conscious of one meaning of their words, which is not the whole meaning or the most important. The effect is now no longer merely symbolic, but hypnotic; the speaker on the stage is like a somnambulist-alive, but controlled and occupied by an external personality, the playwright. Tragic irony is used by Aeschylus with great freedom; [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for instance Mephistophilis, who ought to be symbolic, but treads the lower stage, a cowled enigma,2 horrible because at moments he ceases to be symbolic without becoming human; (3) the 1 We hope it is true that Marlowe did not write the comic scenes; but we are only concerned with the effect of the play as it stands
- B) because his persons are still so near to the symbolic, they have so little character and psychology of their own, that they do not mind serving as mouthpieces (ground truth)
- C) because the playwright deliberately manipulates the audience's expectations, revealing deeper truths beneath the surface narrative, thereby exposing the fragility of human ambition that has been shrouded in ambiguity
- D) because his characters often possess self-awareness and engage in dialogue revealing multiple layers of meaning
- E) for instance, is in its higher aspect a supernatural 'cause', an agency from God, ministering to the divine purpose

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 254

**Metadata:** The following passage comes from Thucydides Mythistoricus, a critical treatise published in 1907 by Francis Macdonald Cornford, a British classical scholar.

**Question:** The longing to see the actor's face, when his words are enigmatic, is almost enough to drive a modern spectator insane. heroic or tragic: Faustus, who is an ideal half realized, hanging together on its own plane; (4) the real: common mortals who would attract no attention in Fleet Street. The Greek drama, [missing clause acknowledging a countervailing fact], and followed another course, seems, nevertheless, to pass through a phase analogous to that which we have just described.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though they remain autonomous and meet for deliberation in a common assembly (97)
- B) although it eschewed the realistic representation of individual characters
- C) although it was once dismissed as mere entertainment, it still captivates audiences with profound depth today
- D) although fortune has made the counsel of none effective
- E) although in the detail of historical development it started at a different point from the modern (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 255

**Metadata:** The following passage comes from Thucydides Mythistoricus, a critical treatise published in 1907 by Francis Macdonald Cornford, a British classical scholar.

**Question:** The impression conveyed is that the seizure of Pylos was a mere stroke of luck, and the obscurities of the story all tend to this effect; and yet we can make out, by inference from the narrative itself, that the occupation was designed. Why is this impression given? [missing sentence describing a cause or reason] He really saw an agency called Fortune at work; for he had no general conception of natural law to exclude such an agency.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Surely at this critical point in the story of the quarrel which led to the war, Thucydides has missed an opportunity of explaining somewhat more fully why Athens allied herself with Corcyra.
- B) Thucydides is not moralizing, or actuated by malignity. (ground truth)
- C) Because by submission you will avert the worst of fates; while we shall profit by not destroying you.
- D) Because the narrative hints at deliberate strategic planning.
- E) The purpose of conveying luck was because it served as justification for his belief.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 256

**Metadata:** The following passage comes from Thucydides Mythistoricus, a critical treatise published in 1907 by Francis Macdonald Cornford, a British classical scholar.

**Question:** They could not understand why a great military power should not be aggressive, and they put it down to the notorious 'slowness' of the Spartan character. 'Of all the Hellenes', so the Corinthians expostulate, 'you alone keep quiet.' 'Justice with you seems to consist in not injuring others and only defending yourselves from being injured. '³ Elsewhere, Thucydides himself falls into the same strain. In 411, he says, [missing clause describing a condition or proviso], the whole Athenian empire might have fallen into their hands; but the two peoples were of very different tempers, the one quick and adventurous, the other timorous and slow. The Spartans, he remarks again, were never disposed to make war except when compelled.5 This reluctance is easy to explain.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if we point to Aeschylean technique in Thucydides
- B) provided that the Athenians had not resisted fiercely
- C) if we are to appreciate the unique detachment of Thucydides' mind
- D) if the Peloponnesians had been more energetic (ground truth)
- E) unless they were provoked

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 257

**Metadata:** The following passage comes from Aztlan : the History, Resources, and Attractions of new Mexico, a descriptive treatise published in 1885 by W. G. Ritch, an American publisher and government official.

**Question:** We must, however, remark here, that during the years 1881 and 1882 the Merrit, Torrence and other properties were actively worked. This is due to the fact that, being only three miles west of the city, little risk was encountered. [missing sentence revising an implied expectation] The bullion product of that year amounted to $253,812; it increased in 1883 to $406,000, and in 1884 it reached $1,228,266.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet, contrary to the common assumption of a seasonal slump, production remained steady, reflecting the miners' relentless effort and favorable ore quality.
- B) However, despite their proximity to the city, these mines did not produce as much bullion as some expected.
- C) But it has been surmised that it was a good thing, and it proved true when 25 tons of secondgrade ore brought the round sum of $12,000.
- D) But this was the exception and not the rule; hence the position we take, that mining in Socorro county dates from the close of 1882. (ground truth)
- E) However, about the latter part of 1882, the Indians had been either dispersed or annihilated, and from that time we date the opening of modern mining in this county.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 258

**Metadata:** The following passage comes from Aztlan : the History, Resources, and Attractions of new Mexico, a descriptive treatise published in 1885 by W. G. Ritch, an American publisher and government official.

**Question:** All mountain climates are distinguished by a lower density of atmosphere; by relatively lower night temperature, and by coolness and dryness; and humidity is often an important factor in the causation of pulmonary consumption. Such climates are indicated where there is any hereditary tendency to pulmonary consumption-in young people who are narrowchested and stoop-shouldered; or where there are hereditary scrofulous tendencies. They are also curative in chronic pulmonary consumption, [missing clause describing a condition or proviso]. Great benefit is also derived in cases of chronic pneumonia, when the products of the inflamation do not readily disappear.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if a time were fixed within which applications for confirmations should be made
- B) if sought before the disease has made too much progress (ground truth)
- C) if pursued after the disease has advanced significantly
- D) provided that the patient is free from active tuberculosis infection

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 259

**Metadata:** The following passage comes from Aztlan : the History, Resources, and Attractions of new Mexico, a descriptive treatise published in 1885 by W. G. Ritch, an American publisher and government official.

**Question:** Accordingly, on consulting with some of the most wealthy and influential citizens of Albuquerque, a hearty coöperation was entered into, which resulted in the incorporation of Albuquerque Academy according to the laws of the Territory, its articles of incorporation empowering the trustees to organize an academy or such other collegiate or higher institution of learning as the needs of the place might demand. [missing sentence describing an inference or effect] It soon passed under the care of the New West Education Commission, of Chicago, which nominates the teachers and contributes largely to the support of the school.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) It follows that the Academy would be designed to meet the educational needs of Albuquerque and its surroundings.
- B) It was thus located through the enterprise of its citizens, who, with their characteristic energy, raised $4,500 by private subscription, purchased a farm of 66 acres and donated it to the Government; and thus induced the expenditure of the appropriation necessary to the erection of the buildings.
- C) Thus Albuquerque Academy was opened in the fall of 1879, with a principal and one assistant. (ground truth)
- D) Thus the academy flourished, drawing distinguished educators and securing substantial funding, thereby establishing a reputable educational institution.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 260

**Metadata:** The following passage comes from Aztlan : the History, Resources, and Attractions of new Mexico, a descriptive treatise published in 1885 by W. G. Ritch, an American publisher and government official.

**Question:** The old shafts, or more properly "gangways," from which the ore has been carried on the backs of peons, have yielded to the mouldering influences of time, and the work of denudation which has been going on for decades, perhaps centuries, has filled them up and almost obliterated from them every trace of human industry. Even the old ore piles were covered with wash from the mountains above, so that they were only found by mere accident. At other places, great excavations have been made for that highly-prized and valuable gem, the turquoise, and judging from the numerous small specimens found in the old debris, not without success, but as civilization advances, the demand for, and hence the value of, mere ornaments decreases, [missing clause describing an inference or effect]. Some speculative minds believe the traces of ancient mining have been thus obliterated by the Pueblo Indians, to keep their Spanish conquerors from using their enforced labor to enrich themselves, while others deem it of more recent date, and claim that they were concealed by the Mexicans, about the time of the cession of New Mexico to the United States.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that it is not likely that it will ever pay again to work these deposits for turquoise (ground truth)
- B) so the remnants of the old mines are increasingly overlooked, their worth fading into the background of progress
- C) so the inevitable conclusion follows that the source of this mineral is undiscovered, if in these mountains, or else the ore was imported from some far-off district, yet unknown
- D) so that they were only found by mere accident
- E) then the importance of these mining sites has diminished

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 261

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** If now we measure the time during which the aorta, even near the heart, is being distended by the injection of the ventricular contents, we find this to be appreciably less than the time from c to d, during which the systole of the ventricle is still going on, though the contents have already begun to escape at about c. This means that the ventricle, though empty, remains contracted for some little time after its contents have left the cavity. It is possible that the point c' in the three figures under discussion, where the descent of the lever changes in rate, becoming less rapid, corresponds to the end of the outflow from the ventricle; [missing clause revising an implied expectation]. The escape from the ventricle is rapid and forcible; the flow ceases suddenly.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but this interpretation complicates dissection of the aorta, and indeed makes it nearly impossible
- B) yet the precise instant may be obscured by transient arterial pressure variations
- C) it is uncertain, however, that these make their way chiefly or exclusively through systole
- D) but this is not certain, and indeed the exact interpretation of this part of the curve is especially difficult (ground truth)
- E) and it appears as if all blood has already left

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 262

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Of two muscles therefore of equal length (and of the same quality) the most work will be done by that which has the larger number of fibres, that is to say, the fibres being of equal width, which has the greater sectional area; and of two muscles with equal sectional areas, the most work will be done by that which is the longer. If the two muscles are unequal both in length and sectional area, the work done will be the greater in the one which has the larger bulk, which contains the greater number of cubic units. [missing sentence describing an inference or effect] We learn then from the foregoing paragraphs that the work done, by a muscle-nerve preparation, will depend, not only on the activity of the nerve and muscle as determined by their own irritability, but also on the character and mode of application of the stimulus, on the kind of contraction (whether a single spasm, or a slowly repeated tetanus or a rapidly repeated tetanus) on the load itself, and on the size and form of the muscle.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence, the mechanical advantage of a muscle is directly proportional to its bulk, implying that a larger muscle will generate greater force over a given distance, thereby accomplishing more work than a smaller counterpart under identical simply conditions.
- B) Hence in extreme stimulation, in what in the muscle corresponds to complete tetanus, the form of the body is the same as in rest; and the tetanized sphere would not be appreciably smaller than the sphere at rest, for that would imply change of bulk, but this as we have seen does not take place.
- C) Thus, understanding these factors allows us to predict how altering muscle characteristics will influence the overall efficiency of the muscle-nerve preparation.
- D) In speaking therefore of the work which can be done by a muscle, we may use as a standard a cubic unit of bulk, or, the specific gravity of the muscle being the same, a unit of weight. (ground truth)
- E) Of two equal-length muscles one must therefore prefer the one of greater bulk, as it will assuredly be able to perform more work.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 263

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** And we may, in connection with this, call attention to the fact that the dilation or loss of tone which follows upon section of the cervical sympathetic (and the same is true of the abdominal splanchnic) is not always, though it may be sometimes, permanent; in a certain number of cases it has been found that after a while, it may be not until after several days, the dilation disappears and the arteries regain their usual calibre; on the other hand in some cases no such return has been observed after months or even years. This recovery when it occurs cannot always be attributed to any regeneration of vaso-motor fibres in the sympathetic, [missing clause describing a cause or reason]. When recovery of tone has thus taken place, dilation or increased constriction may be occasioned by local treatment: the ear may be made to blush or to pale by the application of heat or cold, by gentle stroking or rough handling and the like; but neither the one nor the other condition can be brought about by the intervention of the central nervous system.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for these continue dilated, sometimes exceedingly so
- B) for it is stated to have been observed when the whole length of the nerve including the superior cervical ganglion had been removed (ground truth)
- C) since the same fibres may, on the one hand, by an increase in the impulses passing along them, be the means of constriction, and on the other hand, by the removal or diminution of the tonic influences passing along them, be the means of dilation
- D) for some physicians have observed the spontaneous reestablishment of sympathetic nerve connections and the activation of local autoregulatory mechanisms
- E) but is likely due to compensatory mechanisms in the remaining intact sympathetic fibers

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 264

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** In both these cases the effect is mainly a reflex one, it being the central nervous system which brings about augmentation of constriction in the one case and inhibition in the other; though possibly some slight effect is produced by the direct action of the cold or heat on the vessels of the skin simply. Moreover the vascular changes in the skin are accompanied by corresponding vascular changes in the viscera (chiefly abdominal) of a reverse kind. When the vessels of the skin are dilated those of the viscera are constricted, and vice versa; [missing clause describing an inference or effect]. By these changes, as we shall see later on, the maintenance of the normal temperature of the body is in large measure secured.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that chemical changes too slight to be recognized by the means at present at our disposal would amply suffice to provide all the energy set free
- B) such that the body can efficiently dissipate heat through the skin or conserve it within vital organs
- C) so that a considerable portion of the whole blood ebbs and flows, so to speak, according to circumstances from skin to viscera and from viscera to skin (ground truth)
- D) so that, aas we shall see later on, it is possible in the living organism either to reduce or to increase what may be considered as the normal peripheral resistance
- E) this counterbalancing action thereby preserves the internal thermal equilibrium

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 265

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** He has moreover advanced the theory that muscle may be considered as composed of electro-motive particles or molecules, each of which like the muscle at large has a positive equator and negative ends, the whole muscle being made up of these molecules in somewhat the same way, (to use an illustration which must not however be strained or considered as an exact one) as a magnet may be supposed to be made up of magnetic particles each with its north and south pole. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) We are not however at present in a position to make any very definite statement as to the relation of the myosin to the structural features of muscle.
- B) There are reasons however for thinking that these muscle currents have no such fundamental origin, that they are in fact of surface and indeed of artificial origin. (ground truth)
- C) He suggests however that these particles are not simply aligned but interact dynamically to produce movement.
- D) A muscle however may acquire as a whole a certain amount of rigidity on account of some of the fibres becoming rigid, while the remainder, though they have lost their irritability, have not yet advanced into rigor mortis.
- E) Thus, when stimulated, the positive equators of these particles are attracted to the negative ends of neighbouring particles, producing the shortening of the muscle.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 266

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** Moreover, the propagation of the current is stopped by a ligature, or by crushing the nerve. We may speak of the conditions which give rise to this electrotonic current as a physical electrotonus analogous to that physiological electrotonus which is made known by variations in irritability. The physical electrotonic current is probably due to the escape of the polarizing current along the nerve under the peculiar conditions of the living nerve; but we must not attempt to enter here into this difficult subject or into the allied question as to the exact connection between the physical and the physiological electrotonus, [missing clause acknowledging a countervailing fact]. § 77.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though certainly they may both remain for a long time
- B) though in its more developed state the electrotonus may be considered a form of brain activity
- C) while recognizing that some researchers argue for distinct underlying mechanisms
- D) though there can be little doubt that the latter is dependent on the former (ground truth)
- E) although the evidence for a direct correspondence is not yet definitive

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 267

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** When we stimulate the nerve of a muscle nerve preparation the result, though modified in part by the condition of the muscle and nerve, whether fresh and irritable or exhausted for instance, is directly dependent on the nature and strength of the stimulus. If we use a single induction-shock we get a simple contraction, [missing clause describing a condition or proviso], if we use a weak shock we get a slight contraction, if a strong shock a large contraction and so on; and throughout our study of muscular contractions we assumed that the amount of contraction might be taken as a measure of the magnitude of the nervous impulses generated by the stimulus. And it need hardly be said that when we stimulate certain fibres only of a motor nerve, it is only the muscular fibres in which those nerve fibres end, which are thrown into contraction.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if the stimulation of a particular nerve or any other operation leads to a marked rise of the mean bloodpressure
- B) provided that the stimulus is sufficient to excite the muscle
- C) if the interrupted current we get a tetanus (ground truth)
- D) if the trunk of a nerve be pinched
- E) provided the nerve remains intact

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 268

**Metadata:** The following passage comes from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** The arrangement of the valves of the heart causes this action of the respiratory pump to promote the flow of blood in the direction of the normal circulation; and indeed were the heart perfectly motionless the working of this respiratory pump alone would tend to drive the blood from the vena cava through the heart into the aorta, and so to keep up the circulation; the force so exerted however would, without the aid of the heart, be able to overcome a very small part only of the resistance in the capillaries and small vessels of the lungs and so would prove actually ineffectual. There are then several helps to the flow along the veins, but it must be remembered that however useful, they are helps only and not the real cause of the circulation. [missing sentence describing a cause or reason] [BOOK 1.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) This is likely the cause of a spasm in the muscle of B; and the stimuli following each other rapidly, as being produced by the tetanus of A they must do, the spasms in B to which they give rise are also fused into a tetanus in B.
- B) The real cause of the flow is the ventricular stroke, and this is sufficient to drive the blood from the left ventricle to the right auricle, even when every muscle of the body is at rest and breathing is for a while stopped, when therefore all the helps we are speaking of are wanting. (ground truth)
- C) The heart’s rhythmic contraction, which propels blood from the atria into the ventricles and then ejects it into the aorta, is the principal force that overcomes venous resistance and maintains continuous circulation, ensuring that even in the presence of respiratory and venous aids, the circulation is sustained primarily by cardiac activity.
- D) We may here call to mind the fact mentioned in § 153, of the existence, more or less marked in all hearts, and well seen in the heart of the tortoise, of a muscular ring or collar between the sinus and the auricle, and of a similar ring between the auricle and ventricle.
- E) The primary driver of blood flow is the heart's contraction and relaxation.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 269

**Metadata:** The following passage comes from Ancient Cities From the Dawn to the Daylight, a historical study published in 1886 by William Burnet Wright, an American Congregational clergyman.

**Question:** The Greek tongue excels all other tongues, as Greek art transcends all other art. A sentiment was generated and diffused which counted mental more precious than material riches, and realized that a man's life consists not in the abundance of the things he possesses, but in that which he is. Because they were mentally the ablest, the most cultivated, and in all powers of expression, whether music, art, or speech, immeasurably the most gifted of mankind, the Greeks naturally became the teachers of the race, [missing clause describing an inference or effect]. The religion of Israel, which had limped in Hebrew, flew when it was translated into Greek.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so their teachings and ideas spread widely
- B) so that eventually every revelation made in Greek came with wings (ground truth)
- C) and their rational Hellenic spirit ennobled and transformed a previously primitive religion
- D) so they imparted wisdom, guiding humanity's progress across ages for future generations

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 270

**Metadata:** The following passage comes from Ancient Cities From the Dawn to the Daylight, a historical study published in 1886 by William Burnet Wright, an American Congregational clergyman.

**Question:** The palace of Assur-bani-pal was built upon the same mound on which that of his grandfather Sennacherib stood. It contained the public library. The checks in baked clay, used by the people of Nineveh in drawing books, have been found among the ruins. Tablets found here contain an inscription such as Bacon or Franklin might have written, to the effect that knowledge is power, [missing clause describing a cause or reason]. Here could be seen in baked clay, or at times perhaps in papyrus, the bulletins often sent by generals in the field, and the fortnightly reports from the observatories throughout the empire.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for famine stalked the streets of Antioch
- B) because the empire valued wisdom as the foundation of its enduring strength
- C) owing to the belief that learning could be used to govern more effectively
- D) for the seeing eye, the hearing ear, are the foundation of greatness (ground truth)
- E) because it shows the similarity in plan and structure of the Elamite cities, and so confirms other conclusions which have been drawn from their supposed resemblance to each other

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 271

**Metadata:** The following passage comes from Report of the Special Committee on Outdoor Alms of the Town of Hartford, A.d. 1891, a municipal report published in 1891.

**Question:** 2 Average number of cases of support is given. 3 Figures given are for outdoor relief. The indoor relief figures remain substantially unchanged, or even fall off. Population for 1880 is estimated. Pauper population is partly estimated for the year 1881. [missing sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) This year is taken because it is the first in which the report of the selectmen is found not to have been printed.
- B) This year is taken because it is the first in which the report of the selectmen is found to have been printed. (ground truth)
- C) The decline in indoor relief figures is justified by the increasing availability of local employment opportunities, which reduced dependency on municipal aid.
- D) The purpose of these figures is to illustrate the changing dynamics between outdoor and indoor relief efforts because of evolving social policies.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 272

**Metadata:** The following passage comes from Report of the Special Committee on Outdoor Alms of the Town of Hartford, A.d. 1891, a municipal report published in 1891.

**Question:** Two paupers, who should have been supported in the almshouse if anywhere, have been boarded at the town's charge in the State almshouse at Tariffville for five and a half and one and a half years re spectively, and no return made of them, so far as we can discover. [missing sentence revising an implied expectation] Moreover, we understand that they have been now returned to the town almshouse.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But he admits paupers to the almshouse and discharges them.
- B) However, these paupers were not placed in the town's care as anticipated.
- C) They have, however, been paid for by credits upon the account between the town and the State almshouse, and have cost the town less there than they would have cost here. (ground truth)
- D) But strictly, Hospice is our asylum, or home-sometimes our almshouse.
- E) Nevertheless, the town's neglect in ensuring their proper care has left these paupers in a state of prolonged neglect, contrary to the expectations of both charity and municipal duty in a manner.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 273

**Metadata:** The following passage comes from Notes on Shotwick in the County of Chester, a local history published in 1915 by F. C. Beazley, a British author.

**Question:** In September 1441, Sibyl, who was wife of Richard de Hokynhull, in her own person sued William de Stanley, William de Orell, chaplain, William, son of William de Orell, bastard, Robert de Moldeworth, James de Eulowe, Thomas Glegge, and James le Bridde, chaplain, for one-third of eighteen messuages, 340 acres of land, 10 acres of meadow, 20 acres of pasture, 10 acres of wood, & 5s. 5d. rents in Chircheshotewik and Hokynhull, which she claimed in the King's court as her dower from the said Richard. The defendants did not come. [missing sentence describing an inference or effect] On that day Sibyl comes again in her own person, but the sheriff has not sent the writ.  Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Therefore the said third part was ordered to be taken into the King's hand, and they were to be summoned to be there at the next court, to wit, on Tuesday next after Michaelmas. (ground truth)
- B) Therefore they were ordered to be there at the next court, to wit, on Tuesday after the Feast of the Conception of the B.V.M.
- C) The entries are therefore here given.]
- D) Hence, the case remained unresolved, and Sibyl was left without legal recourse, resulting in the forfeiture of her claim to the lands, thereby undermining her dower rights and weakening her position in the court.
- E) Therefore, it follows that Sibyl's claim to her dower went unanswered and she was unable to pursue her suit at that time.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 274

**Metadata:** The following passage comes from Notes on Shotwick in the County of Chester, a local history published in 1915 by F. C. Beazley, a British author.

**Question:** The defendant seems to have been in ill odour, for he is arraigned at the same time "for not goeinge the p'ambulačon wth his neighbors and for stoppinge the minister and p'ishiners the ancient and accustomed waie"; he is injoyned heareafter "to bee p'sent hym self att the p'ambulačon & not to staye anie the accustomed waie in goinge the same "-a somewhat nebulous sentence. The churchwardens also incur censure from time to time for not providing certain furniture. In 1604 there is "no carpett for the coion [communion] table. They want the two Tomes of homilies & Mr Iuell's "1 replye." [missing sentence revising an implied expectation] In 1665, as we have already noted, they were in trouble over the church plate and other matters.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, despite these shortcomings, the records indicate that the churchwardens generally managed to maintain order.
- B) Their troubles, however, sat lightly on them, and they appear simply to have passed them on to their successors; in 1722 there is "no Hanging for the Pulpit, no Book of Homilies.
- C) Yet the expectation that these provisions would suffice proved ill‑founded, as further shortages soon emerged, and the parish struggled to maintain its sacred duties.
- D) However, probably owing to the lack of means, they failed to furnish the "Tomes," and ten years later they are presented again in consequence. (ground truth)
- E) Such an inquiry, however, seldom admits of a reply; our ancient parish churches, as we now see them, did not spring up within the year as do those of modern times they have been built, added to, and partially rebuilt from time to time, until often little of the original edifices is left, venerable, nevertheless, though they may be.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 275

**Metadata:** The following passage comes from Story Plays Old and New, a collection of plays published in 1915 by Alice Sumner Varney, an American writer.

**Question:** as if it might break. make you tremble so? There, be quiet; you How your heart beats, What has happened to Rabbit Oh, King, the dogs of the hunters are chasing me. Can't you hear them? King I hear them, gentle Rabbit. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet the silence held deeper secrets than any shout could reveal, echoing with unseen danger still.
- B) But calm your fears, little creature, I will keep you from all harm. (ground truth)
- C) But remember to obey the promptings of the ring always.
- D) But hear what Little Goat says.
- E) But arouse your fears little creature, for I will keep you from all harm.
- F) However, Rabbit, your heart should not beat so fast if you trust King to protect you.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 276

**Metadata:** The following passage comes from Story Plays Old and New, a collection of plays published in 1915 by Alice Sumner Varney, an American writer.

**Question:** Robin Don't you think we have gone quite far from the matter of breakfast? I would like a few good fat worms just at this time. Crow Well, I would like a lot more of those grasshoppers that I found yesterday. I could eat for an hour, they were that good. Song Sparrow Well, [missing clause describing a condition or proviso], he would say you were both vagabonds, of no use in the world, and if he had his gun handy, he would try his best very to shoot you. Nuthatch I can tell you one thing, the farmer will have to improve his aim before he puts many of us out of the way.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) provided the moon is full and stars align in quiet night under the silent sky
- B) provided that he were to catch you
- C) if the farmer came along and found you and Robin eating worms and grasshoppers (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 277

**Metadata:** The following passage comes from Annals of Surgery, a medical journal published in 1908.

**Question:** Gallstones are a most frequent cause of cancer of the gall-bladder, but not so of the gall-ducts. In 22 cases of carcinoma of the papilla, collected by Edes,5 gall-stones were found only 4 times, and in 3 of these the stones were in the gall-bladder and only one in the common duct. A differential diagnosis between biliary and pancreatic calculus as a rule, is not made, [missing clause acknowledging a countervailing fact].

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although a stone in the common duct was considered a remote possibility
- B) although precise differentiation can be challenging
- C) though the bladder was frequently emptied with a catheter
- D) though Moynihan has made a correct diagnosis of pancreatic calculus (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 278

**Metadata:** The following passage comes from Annals of Surgery, a medical journal published in 1908.

**Question:** The thyroids gave a distinct thrill and were large, soft and vascular. No exophthalmos was noted, but as this is not always a symptom of Graves' disease in the human being it may not be a necessary symptom in dogs. [missing sentence describing an inference or effect] They furnished an unusual opportunity for carrying out a course of experiments.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) It seems wise, therefore, to present at this time all the cases of ulcer and kindred diseases of the stomach and duodenum operated upon by Dr. C. H. Mayo and myself since the first case in 1893, a period of fifteen years, but to confine the special investigation and statistics to the ulcer group.
- B) Hence, the lack of exophthalmos does not exclude Graves' disease in dogs, suggesting that other signs must be evaluated to confirm hyperthyroidism.
- C) Therefore we can infer  the dogs were exhibiting some form of hyperthyroidism hence, the absence of exophthalmos did not rule out the possibility.
- D) These dogs, therefore, having tachycardia, temperature curve, loss in weight and muscular strength, an increased appetite and thirst, gave a good picture of Graves' disease. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 279

**Metadata:** The following passage comes from Robert Burns, an Address Delivered in Tremont Temple, a rhetorical address published in 1901 by George Frisbie Hoar, an American attorney and politician.

**Question:** No Italian sky, no Arcadian landscape, ever smiled with “the gleam, The light that never was, on sea or land, The consecration, and the poet's dream," like that which his genius has spread over the scene where the two young lovers met to pass a single day. Walter Scott tells us that Burns looked forward, the great part of his life, to ending his days as a licensed beggar, like Andrew Gemmels or Edie Ochiltree. [missing sentence revising an implied expectation] Humanity the round world over, walks more erect for what Robert Burns said and sung.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But Burns revealed to mankind the dignity of humility.
- B) However, Robert burns' death came at 37, not as a beggar but after a life of great literary accomplishment.
- C) Yet, contrary to the romanticized narrative, Burns' ambition was not to become a beggar but to secure a legacy that would outlast his own fleeting fame in the hearts of future generations.
- D) Yet this man brought to the world the best message ever brought to the world since Bethlehem, of love and hope and reverence for God and man. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 280

**Metadata:** The following passage comes from Robert Burns, an Address Delivered in Tremont Temple, a rhetorical address published in 1901 by George Frisbie Hoar, an American attorney and politician.

**Question:** When glorious Tam, through the window of Alloway's auld haunted kirk, saw the young witch, clad in little more than nature had given her, take her first lesson in that immortal dancingschool, and called out, "Weel done, cutty sark!" Robin was peeping, too. Perhaps it is all vain imagination, [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, his own eyes were wide with delight and curiosity, not shock
- B) but I cannot help thinking that, on that occasion at least, the carnal mind comprehended the things that be of the spirit (ground truth)
- C) but you cannot translate the music
- D) however, the earnest hearts of the congregation still felt the stirring of true wonder, and their silent prayers rose like fragrant smoke
- E) But haply, in some cottage far apart, May hear, well pleased, the language of the soul, And in His book of life the inmates poor enroll

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 281

**Metadata:** The following passage comes from Robert Burns, an Address Delivered in Tremont Temple, a rhetorical address published in 1901 by George Frisbie Hoar, an American attorney and politician.

**Question:** To man as to nation every gift of noblest origin is breathed upon by this hope's perpetual breath. I am not here to make an argument. I only affirm a fact. Where this faith lives are found Courage, Manhood, Power. When this faith dies, Courage, Manhood, Power, die with it. No poet can be great, whatever his genius, [missing clause describing a condition or proviso]. But few languages have ever been spoken among men, so far as we know, in which the genius of a poet would not have found itself hampered and fast bound, as the soul of Shakespeare would have found itself constrained and dwarfed in the body of a brute.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if his words are not confined by language's limits ever
- B) unless it hold fast to the faith in a living God
- C) if it is to be powerfully moved
- D) unless he have in his native language a fit instrument (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 282

**Metadata:** The following passage comes from How to Help Cases of Distress: a Handy Reference Book for Almoners and Others, a practical guide published in 1895 by Charles Stewart Loch, a British professor of economics.

**Question:** If there be non-compliance with their order, the defendant forfeits 20s. a month so long as the non-compliance lasts. The Act extends only to natural relations, that is to say, to cases where there is relationship by blood between the parties, to lawful and not to reputed parents or children. [missing sentence describing an inference or effect]  Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) And therefore under the statute a man cannot be compelled to contribute to the maintenance of his wife's mother, or his wife's child by a former husband, or her illegitimate child-after the wife's death, or after such child has attained the age of sixteen; or of his son's wife or widow; or of his own brother, a brother not being mentioned in the statute. (ground truth)
- B) Hence, it follows that any breach of the court's directive by the defendant will have a direct financial consequence.
- C) Consequently, the forfeiture of twenty shillings per month applies exclusively to those parties bound by blood, thereby excluding all reputed parents or children; it follows that the Act's punitive measure is confined to lawful natural relations only, and any attempt at non-compliance by a non-blood relationship will not trigger the stipulated financial penalty under the current statutory framework.
- D) The moral and pecuniary result of the enforcement of the law against relations, is shown in a return kindly furnished by the Clerk of the Barton Regis Union, near Bristol.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 283

**Metadata:** The following passage comes from How to Help Cases of Distress: a Handy Reference Book for Almoners and Others, a practical guide published in 1895 by Charles Stewart Loch, a British professor of economics.

**Question:** In other words, there are giris who, as things are, are not worth decent maintenance wages. The employer who only employs girls who are worth this may preserve the even tenor of his way, and congratulate himself that he at least is free from the guilt of employing hands at starvation wages. [missing sentence revising an implied expectation] This is the question asked by a large number of manufacturers, and their answer to those who demand that a minimum wage should be fixed is that in that case they will have to dismiss many of their hands.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, this would force many employers to reduce their workforce, suffering losses.
- B) But what about the large numbers who are thus left unemployed? (ground truth)
- C) But what are the broader social implications of this apparently benevolent policy?
- D) However, this implies that girls who are not worth decent wages will be dismissed.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 284

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** It may be taken as a fundamental axiom that a colored object will not appear the same, in general, under two illuminants differing in spectral character. A red fabric appears red under daylight or under a tungsten lamp because it has the ability to reflect the red rays and to absorb all or nearly all of the other colored rays. But the color of the red fabric depends upon the illuminant because, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for example, it will appear blue or green under an ordinary mercury arc
- B) the color-sensation in the eye is always the integral result of all the individual color-sensations which may be due to the radiant energy of the various wave-lengths present in the illuminant or reflected or transmitted by colored media
- C) for example, it will appear black or a brownish-black under an ordinary mercury arc (ground truth)
- D) because the spectral composition of illumination that selects the wavelengths reflected by the fabric
- E) for example, the arcs are in use for blueprinting and photo-engraving and many tungsten lamps of all sizes are in use for printing
- F) the illuminant determines which wavelengths are reflected and absorbed

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 285

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** Few working rules are available which may be depended upon at the present time for designing lighting installations from this broader view which aims to do justice to the potentiality of light and, therefore, the lighting specialist must draw upon various sources of information and through imagination, experiment, and experience he should be able to utilize light in lighting effects in a manner similar to that of the painter whose media are pigments. A great amount of lighting may be done very well without resorting to computations. In fact much of the present practice is the result of experience and judgment in which computations are practically impossible or unnecessary. [missing sentence revising an implied expectation] By choosing the proper lighting equipment the desired general effect may be obtained and by computation the required luminous output of each unit may be determined.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, the true art of lighting design lies not merely in calculations but also in the creative vision.
- B) However, in many cases it is necessary to have a certain illumination intensity on the floor or on an imaginary plane somewhat above it. (ground truth)
- C) Nevertheless, designers should not assume that meticulous calculations are indispensable, for intuition and experience frequently yield effective lighting outcomes without exhaustive computation in practice.
- D) However, it is impossible to compute the amount of light contributed to a certain point by reflections from various surfaces in a room so that computations must be based upon the general results of experiment.
- E) But in practising lighting from the engineer's viewpoint dominantly and persistently, the results are naturally those of illuminating engineering.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 286

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** The foregoing illustrates that decoration is intimately interwoven with lighting in the broader sense. If we are to employ light to the limit of its possibilities in lighting effects, the texture and the distribution of brightness and color of the surroundings must be considered. The mood or impression of an interior may be modified by varying the distribution and color of the light even if the decorations remain fixed; [missing clause revising an implied expectation]. At this point the harmony and esthetics of color enter the lighting problem very prominently but it is beyond the scope of this volume to discuss these intimately.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however,  the lighting itself can change perception of color
- B) however, this is a handicap in lighting which could be removed by considering lighting and decoration jointly (ground truth)
- C) however, the subtle interplay of shadows can transform perception more dramatically than any ornament, without altering decor
- D) but doubtless lighting units will be developed to meet the needs discussed in the foregoing paragraphs
- E) but before the lighting specialist is able to utilize the scientific possibilities and the charm of color to their fullest extent, he must be intimately acquainted with light itself

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 287

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** White naturally assumed the attributes of chastity, virginity, purity, innocence, fidelity, peace and friendship; and mythology and poetry abound with examples of such usage. It also symbolizes weakness perhaps through association with femininity and was the mark of untried manhood. [missing sentence describing an inference or effect] Black naturally is quite opposite in character to white, being characterized as dismal, desolate, deadly, malignant, threatening, evil, chaotic and loathesome.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence, society equates white with virtue and black with vice, perpetuating hierarchies.
- B) Therefore, the color white was often employed to denote nobility and virtue.
- C) Consistently therefore it is appropriately the flag of surrender and of truce. (ground truth)
- D) The physiological or psychological effect of this unsatisfactory colordifference is unknown but that it is annoying is the testimony of many observers.
- E) It is thus seen that an attribute of a color which ordinarily may be unpopular, can be used to advantage in a proper place.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 288

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** There are many factors such as brightness-contrast and the position of the units which determine the limiting brightness so that it is impossible to be very definite without discussing these factors at great length. Specifications of brightness apply to the unit as installed and equipped with light-sources whereas the direct-indirect classification has the advantage of definiteness regarding the distribution of light obtainable from the unit. Such a classification or specification of lighting units in terms of direct and indirect components appears to satisfy certain practical requirements of definite description of the characteristics of individual units but there is still a lack of definiteness in the description of lighting installations in general, [missing clause describing a condition or proviso]. Cove-lighting in which the light-sources are concealed behind a projecting moulding or cornice would be correctly classified as indirect lighting and there appears to be no reason why the direct-indirect terminology could not be applied to the distribution of light by the lighting system as a whole as determined at any point of interest.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) unless such a classification be applied to the distribution of light as a whole (ground truth)
- B) unless the installation's geometry, fixture arrangement, and surrounding architecture are fully specified in detail
- C) if a direct-indirect luminous bowl is a deep yellow in color most persons will unconsciously associate this color with the useful light even if most of the latter arrives indirectly at the point of interest practically unaltered by reflections from neutral walls and ceiling
- D) unless such a classification be applied to the distribution of light in parts
- E) unless one considers the variability in lighting conditions and observer perception

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 289

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** A few extra outlets for portable lamps, simple combinations of lighting principles in portable lamps and in suspended fixtures, two- and three-circuit fixtures each providing light of different distribution and possibly of different tint are possibilities for obtaining a distribution and color of light to suit the mood or the occasion. However, the provisions for obtaining variety in lighting seldom extend beyond a twocircuit unit providing only a possibility of varying the intensity of light, and a few connections for portable lamps, [missing clause acknowledging a countervailing fact]. Of all lighting systems, Nature's lighting is the least monotonous and a study of it leads to the conclusion that this is due.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though some designers incorporate advanced dimming systems to achieve nuanced color shifts and mood lighting throughout the space
- B) although nature provides an array of varying light levels and colors throughout the day
- C) although simple combinations of accessories and of multiple circuits are sources of this most appealing feature of lighting (ground truth)
- D) although no positive proof is available, there is a possibility that much of the complaint against artificial lighting may be due to insufficient intensities or quantities of light
- E) although this is often annoying, the lack of monotony is one of the attractive features of daylight

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 290

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** In order to further exemplify the importance of visualization in lighting and what is to be visualized let us inquire further into the process of seeing. The analysis of human consciousness reveals two kinds of visual sensations, namely, chromatic and achromatic sensations. No masterpiece of painted or sculptured art, no beautiful landscape, no office or factory operation and no lighting effect, [missing clause describing an inference or effect].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that, owing to all these influences daylight is far from being constant
- B) so far as the visual sense is concerned, consists of more than an arrangement or sequence of varied colors and brightnesses (ground truth)
- C) can be fully appreciated so long as it is properly illuminated
- D) so the most practicable terminology will provide terms which will give an idea of the appearance of colors
- E) then the viewer's perception is fundamentally altered, revealing hidden emotional layers and subtle spatial nuances previously unnoticed in the scene

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 291

**Metadata:** The following passage comes from The Lighting Art, its Practice and Possibilities, a technical handbook published in 1917 by Matthew Luckiesh, an American physicist.

**Question:** As a matter of fact if a certain portion of the total incident light is reflected at each "air-glass" or "glass-air" surface, it is obvious that there are many other reflected and transmitted beams as indicated by the dotted lines. [missing sentence describing a cause or reason] If the second surface of the thin glass is silvered the intensity of R₂ will be high.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Such effusions cause the searcher after knowledge to doubt the sincerity in art-appreciation of many individuals posing as appreciators.
- B) These become negligible because they contain but a small portion of the original incident light. (ground truth)
- C) For this purpose the lumen has been adopted as the unit of luminous flux and it is equal to the flux emitted in a unit solid-angle (a steradian) by a point-source of 1 candlepower.
- D) The purpose of mentioning these additional beams is to illustrate how light interacts with different surfaces.
- E) Because each interface partially reflects and transmits light, multiple internal reflections and transmissions arise within glass.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 292

**Metadata:** The following passage comes from School Civics, an educational textbook published in 1904 by Frank David Boynton, an American .

**Question:** After a candidate for president has been selected a candidate for vice-president is chosen, and the work of the convention is done. 429. Party Differences. The conventions of the two great parties employ practically the same methods. They differ, however, in two respects. In the democratic national convention the vote is by states, i.e., the entire state delegation votes as the majority may decide, [missing clause acknowledging a countervailing fact].

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though in many respects they differ very widely from the ancient conception of the monarchy
- B) although there may be individual delegates who dissent
- C) although more than one candidate may be voted for if the majority agrees to it (ground truth)
- D) although the Republican convention relies on individual ballots, the state delegation still exerts significant overall influence
- E) though they differ in rank

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 293

**Metadata:** The following passage comes from School Civics, an educational textbook published in 1904 by Frank David Boynton, an American author.

**Question:** For example, in the presidential election of 1900, Idaho, with three electoral votes, gave Mr. Bryan a plurality of 2,448 votes; Kentucky, with thirteen votes, gave him a plurality of 7,975; Nevada, with three electoral votes, gave him 2,516, or a total plurality in the three states named of 12,939; Michigan, with fourteen electoral votes, gave Mr. McKinley a plurality of 104,584. Thus Mr. McKinley, with 91,645 more votes than his opponent received, would have been defeated in the electoral college by a vote of 19 to 14, [missing clause describing a condition or proviso].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) unless all three states had awarded their electoral votes to Mr. Bryan
- B) if the electoral vote had been counted differently, outcome might have shifted
- C) if he always attended strictly to his own affairs
- D) if the decision had been left to the four states above named (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 294

**Metadata:** The following passage comes from Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking published in 1901 by Mary E. Williams and Katharine Rolston Fisher.

**Question:** Sugar is not only a food pleasing to the taste, but is one of the best of heat givers and force producers. This is why children, naturally more active than grown people, are more eager for sugar. Common sense in the use of sugar. [missing sentence describing a cause or reason] It may ferment in the mouth and make the teeth decay.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) (Should not be corned, because it has no fat or bone to protect its juices.)
- B) Because sugar dissolves readily, small quantities of it are easily digested; but if more than a little is taken at once, some of it is likely to ferment in the stomach, causing distress, and interfering with the digestion of other foods. (ground truth)
- C) Do not imagine, because it is watery and comparatively innutritious, that you can safely eat it in unlimited quantities.
- D) The purpose of moderating sugar intake is to prevent potential harm, and especially to avoid a kmnown risk factor for diabetes.
- E) Because the sugar is readily fermented by plaque bacteria in the mouth, it generates acids that dissolve tooth enamel, leading to decay, especially when oral hygiene is poor and the sugar remains on the teeth for extended periods.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 295

**Metadata:** The following passage comes from Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking published in 1901 by Mary E.; Fisher, Katharine Rolston Williams, an American bibliographer and suffragist.

**Question:** Apples may be said to be to other fruits what potatoes are to other vegetables. But what do we know about apples? For instance, what makes them hard? Grate and squeeze one as you did the potato, and you will know. [missing sentence describing an inference or effect] Test it for starch (§ 121 D).

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence apples will not yield any liquid but they do have starch.
- B) Experiment B.- Try the effect of vinegar and of sour milk upon cabbage water.
- C) So much juice must mean that the apple is full of water. (ground truth)
- D) Consequently, their firmness results from a high starch content in the fruit's flesh.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 296

**Metadata:** The following passage comes from Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking published in 1901 by Mary E.; Fisher, Katharine Rolston Williams, an American bibliographer and suffragist.

**Question:** Put a layer of macaroni in a buttered baking-dish, sprinkle with cheese; repeat until all the cheese and macaroni have been used; pour the white sauce over the top. Cover with buttered crumbs, and bake until these are brown. Section 4. Yeast Bread; Yeast Remember thy bread and bake it well, [missing clause describing a cause or reason]. 223.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) since baking develops its flavor and texture
- B) for cleaning purposes, 34
- C) for he will not be kept well who eateth his bread as dough (ground truth)
- D) because the yeast needs to rise evenly before the dough is baked

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 297

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** Since the non-occurrence of gossypol in hot pressed oil is contrary to what might be expected and since it does not occur in actually cold pressed oil it may be well to explain the difference. Actual cold pressure squeezes out the oil from the oil cells without allowing it to dissolve gossypol from the "resin glands." [missing sentence describing an inference or effect] In the commercial "cold pressing" process the seed is heated to a considerable extent and the material is subjected to a grinding, pulverizing action under great pressure so that the glands are broken up and the contents taken up by the hot oil and removed mostly from the cake.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) The effect of starch is peculiar.
- B) Thus, gossypol is evenly distributed across the surface of the oil cells.
- C) Hence the gossypol remains in the press cake. (ground truth)
- D) Hence, gossypol is absent in cold pressed oil but present in commercially processed  oils.
- E) Thus, in one case, they found 25/29 of the toxicity in the resin.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 298

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** In addition to the double salts described by Marignac, it forms the following double compounds: SnF4SnCl4,5 SnF,NH3, SnF4.2NH3.6 Dry hydrogen sulfide gas has little or no action on dry stannic fluoride, but with liquid hydrogen sulfide a violent double decomposition takes place according to the equation SnF4+2H2S = SnS4 + 4HF. (This is a difference in chemical deportment from that of the chloride, [missing clause describing a cause or reason] Stannic fluoride is reduced with violence by metallic zinc or aluminium, but the formation of the intermediate bifluoride was not observed in Wolter's experiments.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) as a direct result, the heat added to the contained ammonia per degree temperature rise.)
- B) because stannic chloride is less reactive.)
- C) because the fluoride ligand is less polarizable than chloride, reaction pathways diverge.)
- D) for the former substance fails to form an addition compound under similar conditions.)
- E) for example, H₂SnF, is certainly not stable in water solution, for solutions of stannic fluoride hydrolyze completely, in marked contrast to solutions of silicon tetrafluoride, which hydrolyzes partially to form silicic and hydrofluosilicic acids in the sense of the equation 3SiF + 3H2O = 2H₂SiFe + H2SiO3.)
- F) for the latter substance forms an addition compound under similar conditions.) (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 299

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** Subst. (I) 0.3344, (II) 0.4041; cc. 0.1 N AgNO3, (I) 14.19, (II) 17.11. Calc. for C₁4H7O₂NI½: I, 53.44. Found: (I) 53.86, (II) 53.74. Dimorphism. 4,5-Diiodophthalanil is soluble in about 8 parts of boiling xylene or 50 of boiling acetic acid. It crystallized from these solvents in pale yellow needles which melt as stated above, [missing clause describing a condition or proviso]. If the unpowdered crystals, however, are heated fairly rapidly they melt about 10° lower, i. e., at 231.5-233.0° (corr.).

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if the usual method of powdering the substance and heating it slowly is employed (ground truth)
- B) if the propionic and butyric acid weights per 100 cc
- C) unless the crystals are subjected to rapid heating
- D) if neutrality is considered not in the stoichiometrical sense
- E) provided that the crystals are cooled slowly at 25°C, their melting point remains unchanged

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 300

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** The attainment of equilibrium required less than two days at 550° C., from four to six days at 500°, and in the three determinations at 450° equilibrium appeared to be established in about a month; but a comparison of the results with those at the two higher temperatures seemed to indicate that even in that period equilibrium was not fully established. At 500°, [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, there can be no question that true equilibrium was established, since it was approached several times from higher as well as from lower temperatures with identical results (ground truth)
- B) but a comparison of the results with those at the two higher temperatures seemed to indicate that even in that period equilibrium was not fully established
- C) however the reaction lagged, indicating that equilibrium was not yet fully achieved despite the expected four to six day period, and the product distribution continued to shift slowly
- D) however, the time required to achieve equilibrium at 500° was considerably less than one might expect from extrapolating the trend observed at higher temperatures
- E) however, with 75 mg. of maltose present the precipitation is retarded and so the quantity of glucose is much in excess of 10 mg

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 301

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** He found that the reaction proceeded with such slowness in either direction that he was able to fix the equilibrium conditions only within wide limits; but by approaching the equilibrium from both sides, he determined that the substances are in equilibrium with one another at 25° when the acid concentration is somewhere between 0.50 and 0.20 molal. In his experiments there was this large divergence, [missing clause acknowledging a countervailing fact]. To determine the equilibrium conditions with any degree of accuracy, it is therefore necessary to make experiments at a higher temperature.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although apparently coincident with W
- B) albeit, he was able to determine a range
- C) though reverse conditions come to obtain when the concentration of the phosphate is sufficiently increased
- D) although the data seemed consistent, significant outliers persisted across all measurements unexpectedly
- E) even though the time allowed for the attainment of equilibrium was 3 months (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 302

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** The silver sufate reagent (described below) quickly gave silver iodide with tetraiodophthalic anhydride, but the 3,4-diiodo derivative required a more concentrated reagent, either silver nitrate or benzoate dissolved in a very little pyridine. These salts remain fused when almost all of the pyridine has been distilled off, and produce a more energetic action than the sulfate whose solution cannot be made so concentrated. [missing sentence revising an implied expectation] 4,5-Diiodo- and tetrachlorophthalic anhydrides gave almost no silver halide even with the concentrated nitrate reagent.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) The fused nitrate, however, has the disadvantage of causing explosions. (ground truth)
- B) However, the reaction with 3,4-diiodo derivative was less straightforward.
- C) Mercuric sulfide, however, is quite soluble in sodium sulfide, which must be present in their reagent.
- D) Nevertheless expectation that concentration would improve halide formation proved false.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 303

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society.

**Question:** That is, Newton's Law of Cooling, on which nearly all methods of treating the leakage are based, fails to hold. The advantage of the law is merely its simplicity; a different law can be made to give satisfactory accuracy even over 20° intervals. But there is little doubt that most experimenters would very greatly prefer to retain the simpler methods; moreover, the point of minimum leakage ordinarily is not so very far beyond the point where the variation from Newton's Law becomes troublesome, [missing clause describing an inference or effect]. It therefore seems best in this paper to take a following of Newton's Law as one of the requirements which is to be met in deciding upon the size of air gap.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) then it can be inferred that using Newton's Law will yield satisfactory results until its limitations become pronounced
- B) so that the experimenter will gain but little who disregards the variation from the law in endeavoring to get the absolute minimum of leakage (ground truth)
- C) so that the resulting error may, in most cases, be regarded as negligible
- D) so that the selected air gap can be determined with only modest error, preserving the system's performance within acceptable limits, thereby avoiding excessive complexity
- E) so much so in fact that it is driven off with difficulty even at 120°
- F) so that the trouble incurred will certainly be found worthwhile

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 304

**Metadata:** The following passage comes from Journal of the American Chemical Society, a journal published in 1918 by American Chemical Society, an American scientific organization.

**Question:** A cell of about twice the size but of the same type with a constant 0.02952 was used for determining the conductance of the water. 2. Preparation of Solutions and Procedure of the Measurements. The conductivity water was prepared as described by Derick and Kamm." The solutions were prepared on the basis of one equivalent to 1000 g. of solution. [missing sentence describing a cause or reason] For each concentration 300-400 g. of solution were prepared.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Because of the extreme dilution this should cause no appreciable error. (ground truth)
- B) For this purpose 34 k. were exhausted by percolation with cold wood alcohol.
- C) Because of these results, the later electrolyses of mixtures of thorium nitrate and the nitrates of the rare earths were made with solutions that contained about 0.5 g. thorium dioxide per 100 cc.
- D) This larger cell size was chosen because it provided better accuracy in measuring conductance.
- E) Because the smaller volume ensures accurate measurement while maintaining stability of solutions.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 305

**Metadata:** The following passage comes from The Nature-Study Review, a pedagogical guide published in 1920.

**Question:** The woodcock's eyes have also become adapted to the method of feeding, being now almost on the top of the head. Swallows, swifts, night hawks and some others fly circling through the air with gaping mouths to receive all unwary insects. Flycatchers prefer to let the insects come to them, [missing clause describing an inference or effect]. Some insect.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so as to receive the edge of the lower; legs and webbed feet, bright scarlet, formed almost exactly like those of a Tern."
- B) so that the little seeds under the ground won't be hurt when Jack Frost comes riding down from the north in Mr. Winter's arms."
- C) so they can catch insects swiftly when they hover close to the forest canopy
- D) so their feet are adapted for perching, their wings less strong for continued flight (ground truth)
- E) then they wait so as to snap them up

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 306

**Metadata:** The following passage comes from The Nature-Study Review, a pedagogical guide published in 1920.

**Question:** Two or three miles further on, these dunes may be lacking entirely and one finds great stretches of scattered creosote bush interspersed with smaller forms of vegetation. Thursday morning we were not near any stream or spring, and as there had been almost no rain this season, we did not need to spend much time collecting. [missing sentence describing an inference or effect] * For an account of the Salton Sea at once scientific and interesting I would refer any one to the publication of the Carnegie Institution written by D. T. MacDougal and collaborators and issued in 1914.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Consequently, the scarcity of water sources rendered the landscape inhospitable, limiting both flora diversity and the opportunities for botanical study, and the researchers had to adapt their methods to the scarce resources.
- B) We therefore effected a late start, and delayed our arrival in Claremont until late in the evening.
- C) Thus we learn that this rootstock may have been creeping on an inch or so each season for many years, always busy with the present and giving no heed to its dead past.
- D) Thus were the laws of man avoided, but the laws of nature were still in operation as I was soon to learn.
- E) Hence, our water supply would have to be carried with us instead of being gathered from natural sources.
- F) We therefore effected an early start, a very fortunate occurrence; for in the afternoon a combination of four blow-outs and a worn-out pump delayed our arrival in Claremont until late in the evening. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 307

**Metadata:** The following passage comes from The Nature-Study Review, a pedagogical guide published in 1920.

**Question:** In the schools of today, and good schools too, a dry emasculated kind of science, labelled nature-study, with no suggestion of the nature-study point of view, is being given to children and to normal students. It is not within the scope of this paper to discuss the pedagogy of nature-study. [missing sentence revising an implied expectation] This is done by state superintendents of education in connection with many other subjects in the curriculum.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) There should be, however, a definite understanding among the believers in nature-study as to just what they consider essential in the nature-study course and then see to it that it is ignored.
- B) However, it is necessary to acknowledge that this approach, while systematic, lacks the inspirational spark that ignites true scientific inquiry.
- C) Nevertheless, we expect that the true essence of nature-study can be reclaimed by teachers who commit to immersive, experiential learning, encouraging curiosity, observation, and a profound respect for the natural world today.
- D) However, there are certain tests for facts ascertained which the pupils find interesting and helpful.
- E) There should be, however, a definite understanding among the believers in nature-study as to just what they consider essential in the nature-study course and then see to it that it is enforced. (ground truth)
- F) Yet principals think nothing of asking teachers to teach nature-study who know no science.

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 308

**Metadata:** The following passage comes from Treaty of Peace, a treaty published in 1920 by Allied and Associated Powers, under corporate authorship.

**Question:** The principle that men and women should receive equal remuneration for work of equal value. Eighth. The standard set by law in each country with respect to the conditions of labour should have due regard to the equitable economic treatment of all workers lawfully resident therein. Ninth. Each State should make provision for a system of inspection in which women should take part, [missing clause describing a cause or reason]. Without claiming that these methods and principles are either complete or final, the High Contracting Parties are of opinion that they are well fitted to guide the policy of the League of Nations; and that, if adopted by the industrial communities who are members of the League, and safeguarded in practice by an adequate system of such inspection, they will confer lasting benefits upon the wage-earners of the world.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because their unique perspectives ensure fair assessment of workplace conditions affecting all genders and promote equity
- B) in order to ensure the enforcement of the laws and regulations for the protection of the employed (ground truth)
- C) owing to the alteration of trade conditions, cause one of the parties substantial prejudice the Mixed Arbitral Tribunal provided for by Section VI shall be empowered to grant to the prejudiced party equitable compensation
- D) in order to ensure the protection of women's rights and welfare

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 309

**Metadata:** The following passage comes from Treaty of Peace, a treaty published in 1920 by Allied and Associated Powers.

**Question:** The Commission shall concurrently draw up a schedule of payments prescribing the time and manner for securing and discharging by Hungary, within thirty years dating from May 1, 1921, that part of the debt which shall have been assigned to her after the Commission has decided whether Germany is in a position to pay the balance of the total amount of claims presented against Germany and her allies and approved by the Commission. [missing sentence revising an implied expectation] ARTICLE 164.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) If, however, within the period mentioned, Hungary fails to discharge her obligations, any balance remaining unpaid may, within the discretion of the Commission, be postponed for settlement in subsequent years or may be handled otherwise in such manner as the Allied and Associated Governments acting in accordance with the procedure laid down in this Part of the present Treaty shall determine. (ground truth)
- B) Nevertheless, if any difficulties should arise owing to the date of the signature of the present Treaty, the dates at which any of the operations laid down by this Article are to be carried out may be altered by the Reparation Commission.
- C) Nevertheless, all acts done by virtue of the special measures taken during the war under legislative, executive or administrative authority of any Allied or Associated Power in regard to the rights of nationals of the former Kingdom of Hungary in industrial, literary or artistic property shall remain in force and shall continue to maintain their full effect.
- D) However, the Commission must also consider that Hungary's economic capacity, still fragile after the war, may not permit the full disbursement of the assigned debt within the prescribed thirty-year period, and therefore a more flexible, graduated payment plan should be incorporated to prevent fiscal collapse and maintain regional stability, and ensure that future generations are not unduly burdened by the legacy of war.
- E) The Commission's schedule of payments is not expected to commence until Germany has agreed and approved their portion of debt, however, Hungary must be prepared for a significant 30-year payment plan.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 310

**Metadata:** The following passage comes from Treaty of Peace, a treaty published in 1920 by Allied and Associated Powers, a multiple author.

**Question:** The number of students admitted to attend the courses in military schools shall be strictly in proportion to the vacancies to be filled in the cadres of officers. The students and the cadres shall be included in the effectives fixed by Article 104. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) This renunciation shall take effect as from August 12, 1914.
- B) Thus, any surplus of students will not be permitted to exceed the number of officer vacancies.
- C) Consequently, the effective personnel numbers will rise proportionally across all service branches.
- D) Consequently all military schools not required for this purpose shall be abolished. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 311

**Metadata:** The following passage comes from Treaty of Peace, a treaty published in 1920 by Allied and Associated Powers, a multiple author.

**Question:** The Council may in any case under this Article refer the dispute to the Assembly. The dispute shall be so referred at the request of either party to the dispute, provided that such request be made within fourteen days after the submission of the dispute to the Council. In any case referred to the Assembly, all the provisions of this Article and of Article 12 relating to the action and powers of the Council shall apply to the action and powers of the Assembly, provided that a report made by the Assembly, [missing clause describing a condition or proviso], exclusive in each case of the Representatives of the parties to the dispute, shall have the same force as a report by the Council concurred in by all the Members thereof other than the Representatives of one or more of the parties to the dispute. Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]

**Category:** cloze_conditionalclause

**Choices:**
- A) if concurred in by the Representatives of those Members of the League represented on the Council and of a majority of the other Members of the League (ground truth)
- B) provided that they are intended solely to cover equitably the cost of maintaining in a navigable condition
- C) unless it has been unanimously adopted and contains a recommendation for settlement that both disputing parties have agreed to
- D) if the report is approved by a quorum of Assembly members not representing any party, and if it contains no conflicting statements from such representatives, it shall be binding
- E) provided that such request be made within fourteen days after the submission of the dispute to the Council

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 312

**Metadata:** The following passage comes from The Development of Doctrine in the Epistles, a work of Scriptural interpretation published in 1896 by Charles Richmond Henderson, an American minister and professor.

**Question:** Under the divine constitution of man human beings can fulfill their mission here and advance to the most complete manhood only by means of (1) material resources, (2) domestic life, (3) the protection of government, (4) the institutions and arrangements for sociability, education, culture, and (5) the institutions of religion. [missing sentence describing an inference or effect] These "moral partnerships" are not mere devices of men, but they are providential gifts.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) So far as possible the "strong" should avoid casting stumbling stones before the "weak," and should positively seek to impart to them knowledge, hope, power.
- B) Such institutions, therefore, are part of the order established by the Founder of the kingdom of heaven. (ground truth)
- C) So long as morality and religious principle are not offended a Christian in society may conform to innocent customs, with a desire to please all for edification.
- D) Thus, these moral partnerships enable humanity to attain its divine purpose, fulfilling God's intended destiny ever.
- E) It follows that these moral partnerships are necessary to achieving full human potential.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 313

**Metadata:** The following passage comes from The Development of Doctrine in the Epistles, a work of Scriptural interpretation published in 1896 by Charles Richmond Henderson, an American minister and professor.

**Question:** Paul's specific instruction to bond servants was: "Servants, be obedient unto them that according to the flesh are your masters, with fear and trembling, in singleness of your heart, as unto Christ; not in the way of eyeservice, as men-pleasers; but as servants of Christ, doing the will of God from the heart; with good will doing service, as unto the Lord, and not unto men: knowing that whatsoever good thing each one doeth, the same shall he receive again from the Lord, whether he be bond or free" (Eph. 6:5-8; Col. 3:22). Obedience, fidelity, respect, honesty, are required of them who find themselves in this outwardly unhappy situation. [missing sentence revising an implied expectation] Christian masters were under love's great law.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But the moral law is fixed, and purity of thought and conduct is determined for both married and unmarried.
- B) But rights may be waived in the interest of love and peace and spiritual welfare (1 Cor.
- C) But these instructions to slaves do not stand alone. (ground truth)
- D) Yet obedience to Christ surpasses earthly masters' demands.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 314

**Metadata:** The following passage comes from The Development of Doctrine in the Epistles, a work of Scriptural interpretation published in 1896 by Charles Richmond Henderson, an American minister and professor.

**Question:** 2: 16; Rom. 5: 1; 3: 27, 28). It is not by performance of some ceremonial, nor by perfect obedience to moral requirements, that we can hope to purchase redemption. It must be received by us as a free gift. [missing sentence describing a cause or reason] 'Instrumentally" we are saved by faith, as the act of confidence in rope and rescuer leads one to lay hold of the help that is freely and lovingly offered to a drowning man.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) This justification is salvation from the expression of divine opposition to sin-from the divine "wrath" (Rom.
- B) Because redemption is a divine grace, its justification lies not in our works but in the boundless love of God, which we must accept with humble gratitude today.
- C) Hence it is that justification comes to faith, since it is by trustful confidence that we accept the promise of God, and consciously make it our own. (ground truth)
- D) The purpose of salvation through faith is because God wants us to receive His gift through grace, not through our own efforts.
- E) Salvation includes more than justification and forgiveness, for it carries with it an actual, progressive purification of thought, feeling, and will; of body, soul, and spirit.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 315

**Metadata:** The following passage comes from Andrew a. Bonar, D.d., Diary and Letters, a diary, with selected correspondence published in 1894 by Andrew A. Bonar, a Scottish clergyman.

**Question:** Tuesday, 19th-Encouraged in prospect of the Assembly by reading in Gibbon (ch. 70) how the consciousness of power can elevate the manner of a man to the station, imparting a dignity even where it was unknown before; Rienzi, Cromwell, etc. [missing sentence revising an implied expectation] I was invited to be present and take some part in the ordination of John Sloan in the Park Church.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, I had not been expecting this honor given my relatively new role in the community.
- B) But I have some cases of peculiar blessing to set over against these discouragements.
- C) But it seems to me that I have not got the Spirit of power to any extent.
- D) Yet I anticipated that my participation would be merely ceremonial, but the experience proved otherwise, elevating my spirit and confirming the profound impact of collective devotion.
- E) But, above all, doubt about the presence of the Lord with me will carry me through my work in the Assembly.
- F) But, above all, the consciousness of the presence of the Lord with me will carry me through my work in the Assembly. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 316

**Metadata:** The following passage comes from Andrew a. Bonar, D.d., Diary and Letters, a diary, with selected correspondence published in 1894 by Andrew A. Bonar, a Scottish clergyman.

**Question:** Much of old times came up to mind. Preaching here last Sabbath, I was more like a man deserted than I have been for many years. I had come from the Inverness Conference, and was very prayerless, I fear, during the week. I see that the Master teaches the necessity of such times of continued waiting on God as a stay in the country presents, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because of the absence of prayer, love, and zeal in His service; and still also my feebleness in prayer alone often saddens me
- B) because the Lord's discipline demands humility, and the quiet of the countryside sharpens faith, fostering gratitude, reminding us that patience strengthens reliance upon His providence in daily guidance
- C) for in Luke v. 16 it is written that He was in the habit of thus withdrawing : αὐτὸς δὲ ἦν ὑποχωρῶν ἐν ταῖς ἐρήμοις, καὶ προσευχόμενος (ground truth)
- D) because I had neglected to seek His presence and communion during my journey

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 317

**Metadata:** The following passage comes from A Slave's Adventures Toward Freedom, an autobiography published in 1918 by Bruner, Peter, an American soldier and writer.

**Question:** I remained there until Fall and then my time had expired, so I came in and paid my board and started to school another winter. And then I began to study my piece again, and I never got my piece this winter. [missing sentence revising an implied expectation] So I found out that that would not do and I was not learning anything so I thought I would quit going to school and get married.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) I tried to apply myself, yet I was still unable to make any progress.
- B) But I happened to go the wrong road, and the first thing I knew I was in Richmond, Kentucky, in Madison County.
- C) But once or twice a week I could spell some one down and get up head of the class. (ground truth)
- D) But I was able to refund the money before the two years had expired by working at the Western Seminary.
- E) I had expected to finish my piece this winter, yet the harsh conditions thwarted my progress and left me disheartened.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 318

**Metadata:** The following passage comes from A Slave's Adventures Toward Freedom, an autobiography published in 1918 by Peter Bruner, an American soldier and writer.

**Question:** I would tell him sometimes that I wished he would kill me at once and I would be done suffering in this world. He went to town that night and when he came back he cowhided me until the blood streamed down my back. He was mad because I said I wished he would kill me, [missing clause revising an implied expectation]. One Christmas morning he was returning from town and so I thought I would catch his Christmas gift; it was always customary in those days to catch peoples Christmas gifts and they would give you something.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but he did not believe me
- B) however, he feared that my words might drive him to violence forever
- C) but he was full of whiskey every time he did this (ground truth)
- D) but I told him that was something I did not do for my own master, and then he jumped on me and I got the best of the old fellow, and his wife jumped out of bed with the rifle and she ran to him with it and I got hold of it and it went off some way or other
- E) but it would have paid me best to have taken the whipping that night for I received a harder one that next morning, one for running off and the other for going to Procter, but he said I might go and I do not see why he would want to whip me

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 319

**Metadata:** The following passage comes from A Slave's Adventures Toward Freedom, an autobiography published in 1918 by Peter Bruner, an American soldier and writer.

**Question:** If a white boy jumped on a colored boy and whipped him it did not make any difference how poor he was you were not allowed to touch him and besides the whipping the boy would give you your master would give you another one. There was a colored boy of Mr. Dewitt's who stabbed a poor white boy on election day. [missing sentence describing a cause or reason] There were two or three hundred after him with clubs and boulders trying their very best to take his life.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The cause of this fracas was the colored boy had gone in swimming and the white boy hid his clothes while he was in there. (ground truth)
- B) He was mad because I said I wished he would kill me, but he was full of whiskey every time he did this.
- C) Because he was black and he had to be punished for his offense.
- D) Because the white boy had previously threatened to expose the colored boy's family's debt, the boy saw no other way to protect his future.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 320

**Metadata:** The following passage comes from Practical Points in the Management of Some of the Diseases of Children, a medical treatise published in 1891 by Isaac Newton Love, an American physician.

**Question:** In this connection I will say that castor oil can be given so as to be reasonably pleasant, by coupling it with lemon juice, or a modicum of whiskey and a little sugar sprinkled over it, or in the froth of beer, or even in hot milk, flavored with a small amount of nutmeg. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) It may seem unpalatable, yet with lemon juice, whiskey, sugar, beer, or nutmeg‑flavored milk, it becomes pleasantly tolerable.
- B) But if the oil raises a riot, if it arouse trouble and resentment, let us give something pleasanter. (ground truth)
- C) I do not believe, however, that water as an internal remedy is sufficiently appreciated.
- D) I believe, however, that some menstruum that holds it in suspension in a form to disguise the taste, and at the same time render it readily soluble in the stomach, is the most desirable way to administer it.
- E) However, children often resist taking medicine so these methods can be helpful.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 321

**Metadata:** The following passage comes from Practical Points in the Management of Some of the Diseases of Children, a medical treatise published in 1891 by Isaac Newton Love, an American physician.

**Question:** Moreover, the propagation of the current is stopped by a ligature, or by crushing the nerve. We may speak of the conditions which give rise to this electrotonic current as a physical electrotonus analogous to that physiological electrotonus which is made known by variations in irritability. The physical electrotonic current is probably due to the escape of the polarizing current along the nerve under the peculiar conditions of the living nerve; but we must not attempt to enter here into this difficult subject or into the allied question as to the exact connection between the physical and the physiological electrotonus, [missing clause acknowledging a countervailing fact]. Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]

**Category:** cloze_causalclause

**Choices:**
- A) as there is no milk to be found
- B) for the reason that he is working for a living and not getting it (ground truth)
- C) since the child's hunger is unaddressed, he becomes irritable, requiring immediate feeding and care
- D) for, while it is true that nature is of great value in recuperating and rebuilding the child, we must bear in mind that we have a sensitive plant to deal with, an undeveloped organism, a creature which is made up largely of nervous system, more than usually sensitive, and easily agitated, altogether presenting great susceptibility to irritation, disturbance, and attack by the various germs and deleterious influences which surround it
- E) for the reason that he is working for a living and getting it

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 322

**Metadata:** The following passage comes from Practical Points in the Management of Some of the Diseases of Children, a medical treatise published in 1891 by Isaac Newton Love, an American physician.

**Question:** He stated that he applied local and general measures to his case, but that he supplied himself with the best whiskey that could be gotten and drank it in enormous quantities, keeping himself saturated with it, and the amount he took without producing intoxication, was marvellous. [missing sentence describing an inference or effect] In the matter of medicinal treatment I am much inclined to germicidal and eliminative measures.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) The effect and the result increased his confidence in alcoholic stimulation. (ground truth)
- B) So, then, as the physician should be thoughtful of his every word spoken in the presence of a child, after having thoroughly interrogated every organ, developed every point possible, in his efforts to relieve the conditions, he should have sensitive regard for the every comfort of the patient.
- C) Thus, the patient did not exhibit intoxication, indicating the whiskey's medicinal efficacy.
- D) Hence, his remarkable tolerance was likely due to years of excessive consumption.
- E) The result produced by the blunderer called to relieve him may be a lasting one.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 323

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** Early in the history of radio, Marconi demonstrated that radiation from an antenna was directional in its effect, according to the shape of the aerial employed. It was this discovery which led in later years to the wonderful success of the direction finder or radio compass. It is well known, that a single vertical wire is, for its size the best radiator, [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but with the aid of the Italian and British governments he increased the range of his apparatus until he had demonstrated that radio was a practical commercial possibility with unlimited scope
- B) however, its efficiency drops sharply when the frequency is from the quarter-wave resonance, and installations must account for ground conductivity and nearby structures, which can further reduce performance
- C) however, it was also found that this type of antenna did not efficiently cover all directions
- D) but it must be so short in order to obtain sufficient capacity that it becomes impractical for long wave or long distance work
- E) but it has to be made so extremely long in order to obtain sufficient capacity that it is not a practical antenna for long wave or long distance work (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 324

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** Early in the history of radio, Marconi demonstrated that radiation from an antenna was directional in its effect, according to the shape of the aerial employed. It was this discovery which led in later years to the wonderful success of the direction finder or radio compass. It is well known, that a single vertical wire is, for its size the best radiator, [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, its efficiency drops sharply when the frequency is from the quarter-wave resonance, and installations must account for ground conductivity and nearby structures, which can further reduce performance
- B) but it must be made so short in order to obtain sufficient capacity that it becomes impractical for long wave or long distance work
- C) however, it was also found that this type of antenna did not efficiently cover all directions
- D) but it has to be made so extremely long in order to obtain sufficient capacity that it is not a practical antenna for long wave or long distance work (ground truth)
- E) but with the aid of the Italian and British governments he increased the range of his apparatus until he had demonstrated that radio was a practical commercial possibility with unlimited scope

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 325

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** The difference between the gravity primary cell, previously referred to, and the secondary or storage cell, is in the method of renewing the active material. While the primary cell is renewed by supplying new electrolyte and replacing the worn out zinc electrode with a new one, dry cells cannot be renewed. [missing sentence revising an implied expectation] While the cell is supplying emf., it is said to be "discharging" and when receiving a renewal of energy it is said to be "charging."

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) In the storage battery, however, the necessary chemical conditions of the plates is restored by the action of a current of electricity from some outer source, usually from a dynamo. (ground truth)
- B) If, however, five amperes is the rate mentioned on the normal discharge and charge rate of the cell, it should only be discharged at that rate and also recharged at that rate, which would give the normal usefulness as five amperes for eight hours.
- C) However, secondary cells can be recharged repeatedly, as they use reversible chemical reactions.
- D) However, when the plates are connected by a wire or some other conductor outside of the liquid, a current will flow in the conductor, as a chemical action takes place in the cell.
- E) However, the secondary or storage cell can be recharged by applying an external current, thereby reversing the electrochemical reaction and restoring its original emf, thus extending its useful life.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 326

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** In some cases the studio is on the ground floor of a building and the power and control rooms are located on the roof directly under the aerial wires. In most cases at least two studios are provided, one for large assemblies and a smaller one for individual speakers. The studio must be very carefully planned, [missing clause describing a cause or reason]. No matter how well the transmitter operates if the acoustic properties of the studio are bad the broadcasting will sound bad in the radio receivers.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for the average reader to think of ether as the conducting medium for radio waves
- B) for on it depends the success of a broadcasting station (ground truth)
- C) because listeners judge broadcasts primarily on studio acoustics and clarity
- D) because it is where the program originates

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 327

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** Another very practicable type for certain work is the V antenna, consisting of two sets of horizontal wires supported by three masts or towers, so that the horizontal portions form an angle or V. The directional effect of an inverted L or V type is greater than a T. There is a greater amount of energy sent in the direction in which the angle of the L points than in the opposite. With the T type the effect is more undirectional, [missing clause acknowledging a countervailing fact].

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although the energy radiated in all directions is not as concentrated
- B) although it will be found that later, in discussing undamped wave receivers, very slight modifications of the damped wave apparatus will give one method of receiving undamped waves
- C) although less energy is sent in the parallel direction of the horizontal wires, than at right angles
- D) although ether waves may be of different form to water waves
- E) although more energy is sent in the parallel direction of the horizontal wires, than at right angles (ground truth)
- F) although the T type is less directional, it provides more uniform coverage across all angles globally

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 328

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** The same circuit utilized for charging lead cells may be employed for charging Edison cells. The charging source should have a voltage equal to 1.85 times the number of cells in series. Before starting to charge, open the covers of the compartment, [missing clause describing a condition or proviso]. See that the solution is at the proper level.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if the battery is fully rested
- B) if a piece of magnetite is dipped into iron or steel filings
- C) if the battery is in one (ground truth)
- D) if the grid be charged negatively
- E) provided that all cells are connected properly

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 329

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** Therefore, when an electron, negatively charged, leaves an atom, there is then less negative electricity than positive in the atom; in this condition the atom is said to be positively charged. The atoms in matter are constantly in motion, and when they strike against one another electrons are jarred from an atom. This electron then moves about freely between the atoms. [missing sentence describing an inference or effect] The higher the temperature, the faster the atoms move and the more electrons given off.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) This effect of the electrons in the space is called the "space charge effect."
- B) Consequently, the free electrons increase the material's conductivity.
- C) Heat has no effect upon this process.
- D) Heat has an effect upon this process. (ground truth)
- E) Thus both of the parts of the disrupted atom become carriers of electricity and contribute to the flow of current through the gas.
- F) Hence, the material begins to conduct electricity.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 330

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** The electric field intensity, due to the presence of negative electrons in the space between the filament and plate, may at last equal and neutralize that due to the positive potential of the plate so that there is no force acting on the electrons near the filament. This effect of the electrons in the space is called the "space charge effect." It must not be supposed that the space charge effect is caused by the same electrons all the time. Electrons near the plate are constantly entering it, but new electrons emitted by the filament are entering the space, [missing clause describing an inference or effect]. After the temperature of the filament has reached the point where the effect of the electrons present in the space between filament and plate neutralizes the effect of the plate voltage, any further increase of the filament temperature is unable to cause an increase in the current.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that the total number between filament and plate remains constant at a given temperature (ground truth)
- B) then the space charge gradually increases, counterbalancing the plate's field and reducing electron acceleration near filament
- C) this then creates an equilibrium between electron emission and absorption
- D) so that the total number between filament and plate fluctuates despite the temperature

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 331

**Metadata:** The following passage comes from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer.

**Question:** The two types of detectors which act as rectifiers are, namely, the crystal detector and the vacuum tube detector. When a crystal detector is employed it is sometimes necessary to have some way of testing whether or not the detector is in adjustment or is "set." [missing sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Because detector sensitivity varies, testing ensures accurate rectification and proper alignment.
- B) For this purpose a test buzzer is usually disconnected from the crystal receiver.
- C) Since the crystals employed are quite delicate, they easily fall out of adjustment during operation.
- D) For this purpose a test buzzer is usually fitted to a crystal receiver. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 332

**Metadata:** The following passage comes from The System of Calculating Diameter, Circumference, Area, and Squaring the Circle : Together With Interest and Miscellaneous Tables, and Other Information, a practical guide to mathematical techniques published in 1881 by James. Morton, an American mathematician.

**Question:** This arrangement prevents any coke or half-melted iron from falling down in the hearth, which is only accessible to melted iron and slag, and forms for them a kind of sump or receiver, which in no way interferes with the regular working of the two upper parts of the cupola. This very simple construction has proved highly successful, and its great advantages are a saving of fuel, a uniformly hot and liquid iron, and an increased yield per diem, as the regular smelting operation is never interrupted. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence the fuel savings and increased daily yield result in higher overall production efficiency for industry.
- B) Krigar's cupola cannot, therefore, be accepted as appropriate for foundries or Bessemer works.
- C) Hence one cubic centimetre is equal to 0.0610253868 cubic inches, or to 16.2311678+ minims (there being 28.82+grains for every 1000 grains, or less than 2.9 per cent.
- D) Krigar's cupola can, therefore, be recommended not only for foundries, but also for Bessemer works. (ground truth)
- E) Hence, it follows that this design significantly enhances overall efficiency and productivity.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 333

**Metadata:** The following passage comes from The System of Calculating Diameter, Circumference, Area, and Squaring the Circle : Together With Interest and Miscellaneous Tables, and Other Information, a practical guide to mathematical techniques published in 1881 by James. Morton, an American mathematician.

**Question:** To remedy a difficulty experienced in starting this class of furnace, owing to the cold air contained in the passages, a flue is provided in which fire may be introduced to heat the air, and so induce a current. Improved Cupola Furnace. Smelting iron in a cupola furnace appears to most people, who see it daily done at every foundry, the simplest thing in the world; it is, however, not so, [missing clause describing a condition or proviso]. In a common cylindrical cupola, three essential parts may be distinguished.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if all the ingredients in the formula be expressed by weight
- B) provided that the furnace temperature exceeds the iron melting point, operation ensues
- C) unless the furnace is properly maintained and operated
- D) if due regard is taken to economy and good quality in casting (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 334

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion lectures published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, lecturer.

**Question:** The new system worked better, it spread, and was finally adopted by those higher nations which it also helped to create. It is an instance, nevertheless, of the slowness with which radical changes succeed in leaving great masses of mankind, that the older system, with the ban of Evolution upon it, still survives in Modern Europe. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But it is not so much in ignoring Man that evolutionary philosophy has gone astray; for of that error it has seriously begun to repent.
- B) But to fix the eye upon it at that remote stage and assert that, because it was apparently then automatic, it must therefore have been automatic ever after, is to forget the progressive character of Evolution as well as to ignore facts.
- C) Yet there are signs, even among the uncivilized, that polygamy is passing away. (ground truth)
- D) One would expect rapid progress but change moves glacially through society.
- E) But the old system persists, stubbornly resisting the new order's sweeping promise.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 335

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** The new system worked better, it spread, and was finally adopted by those higher nations which it also helped to create. It is an instance, nevertheless, of the slowness with which radical changes succeed in leaving great masses of mankind, that the older system, with the ban of Evolution upon it, still survives in Modern Europe. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet there are signs, even among the uncivilized, that polygamy is passing away. (ground truth)
- B) But the old system persists, stubbornly resisting the new order's sweeping promise.
- C) One would expect rapid progress but change moves glacially through society.
- D) But to fix the eye upon it at that remote stage and assert that, because it was apparently then automatic, it must therefore have been automatic ever after, is to forget the progressive character of Evolution as well as to ignore facts.
- E) But it is not so much in ignoring Man that evolutionary philosophy has gone astray; for of that error it has seriously begun to repent.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 336

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** In "fixing on a part" whereby to "reconstruct the ultimate," it has fixed upon a part which is not the most vital part, and the reconstructions, therefore, have come to be wholly out of focus. Fix upon the wrong "part," and the instability of the fabric built upon it is a foregone conclusion. Now, [missing clause acknowledging a countervailing fact]. And although it anticipates much that we should prefer to leave untouched until it appears in its natural setting, the gravity of the issues makes it essential to summarize the whole situation now.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though the initial focus may seem misdirected, the very act of dissecting these fragments provides insight that, paradoxically, fortifies our understanding of the broader tapestry, revealing hidden interconnections that would otherwise remain obscured within the narrative ←
- B) although reconstructions of the cosmos in the light of Evolution are the chief feature of the science of our time, in almost no case does even a hint of the true scientific stand-point appear to be perceived (ground truth)
- C) though its bearing upon this or that individual case may seem unjust, its necessity for the world as a whole is vindicated

**Model response:** `A
B
C`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 337

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** Dazzled with the apparent solidity of this foundation, men made haste to run up a structure which included the whole vast range of life-vegetal, animal, social-based on a law which explained but half the facts, and was only relevant, in the crude form in which it was universally stated, for the childhood of the world. It was impossible for such an edifice to stand. Natural history cannot in any case cover the whole facts of human history, and, so interpreted, can only fatally distort them. The mistake had been largely qualified had Mr. Darwin's followers even accepted his foundation in its first integrity; [missing clause revising an implied expectation]. Mr. Darwin's sagacity led him distinctly to foresee that narrow interpretations of his great phrase "Struggle for Existence" were certain to be made; and in the opening chapters of the Origin of Species, he warns us that the term must be applied in its "large and metaphorical sense, including dependence of one being on another, and including (which is more important) not only the life of the individual, but success in leaving progeny."

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but he cannot escape a purpose-the purpose, conscious or unconscious, of unfolding the purpose which lies behind the facts which he narrates
- B) however, even those who initially embraced Darwin's doctrine in its form would have soon realized that the underlying flaw could not be reconciled with empirical reality
- C) but, perhaps because the author of the theory himself but dimly apprehended the complement of his thesis, few seem to have perceived that anything was amiss (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 338

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** For these dates show that each animal in each particular country chooses that time of the year to give birth to her young when they will have the best chance of surviving-that is to say, when the climate is mildest, food most abundant, and the prospects of life on the whole most favorable. [missing sentence describing an inference or effect] Because those born at this season survived and those born out of it perished, by the prolonged action of Natural Selection these dates in time probably became engrained in the species, and would only alter with climate itself.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) The dormouse thus brings forth its young in August, when the nuts begin to ripen; and the young deer sees the light just before the first grass shoots into greenness. (ground truth)
- B) It follows that animals have evolved to give birth during specific times of year as a consequence of natural selection favoring survival and reproduction under optimal conditions.
- C) Hence, across species in the reproductive calendar was fixed by natural selection, aligning birth with the mildest season to maximize offspring survival and to ensure the continuation of favorable traits.
- D) Nature must deepen the result by extending it to the time before marriage.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 339

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** Man owes what Burns calls his "heaven-erected face" to the Struggle for Life. How recent this change is, how new the attitude still is to him, is seen from the simple fact that even yet he has not attained the power of retaining the erect position long. Most men sit down when they can, and so unnatural is the standing position, [missing clause describing an inference or effect]. Possibly both the erect position and the Club had another origin, but the detail is immaterial.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so they find it impossible to sustain the posture, revealing their inherent fragility and fleeting resolve
- B) so that should it happen that a combination of these precise centres had never been made before, it is obvious that no routes could possibly exist between them, and these must then and there be prospected
- C) so unstable the equilibrium, that when slightly sick or faint, Man cannot stand at all (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 340

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** The tenement in fact consists now of innumerable groups of cells congregated together, suites of apartments as it were, which have quickly arranged themselves in symmetrical, definite, and withal different forms. Were these forms not different as well as definite we should hardly call it an evolution, nor should we characterize the resulting aggregation as a higher organism. A hundred cottages placed in a row would never form a castle. What makes the castle superior to the hundred cottages is not the number of its rooms, [missing clause describing a cause or reason]. It lies in the number and nature and variety of useful purposes to which the rooms are put, the perfection with which each is adapted to its end, and the harmonious co-operation among them with reference to some common work.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for they are possibly fewer; nor their difference in shape, for that is immaterial (ground truth)
- B) in order to maximize functional synergy among rooms, they are meticulously arranged for performance
- C) because of their unique arrangement and interconnection
- D) for the most part timid and defenceless as individuals, have survived to occupy in untold multitudes the highest places in Nature
- E) for every animal whether it should increase, or change, or die

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 341

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** Is the fact that no novelty is introduced in the case of Man a proof that the ultimate Hand has appeared? By no means. And yet it is probable for other reasons that the ultimate Hand has appeared; that there will never be a more perfectly handed animal than Man. And why? [missing sentence describing a cause or reason] In the perfecting of the bodily organs, as of all other mechanical devices, necessity is the mother of invention.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The rationale is that evolution has already produced an organism with such a high level of dexterity.
- B) Because the causes which up to this point have furthered the evolution of the Hand have begun to cease to act. (ground truth)
- C) Because the evolutionary purpose of humanity is to attain perfection, the ultimate Hand has manifested through relentless natural selection ever.
- D) Because movement is work, and work is exercise, and exercise may mean a further evolution of the part of him that is exercised.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 342

**Metadata:** The following passage comes from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** Plant in the mind, or evoke from it, the idea of acting in a given way with reference to some half-dozen daily trifles when done in the presence of one authoritative individual, and Evolution has already found something to work on. The children have got six, if not ten commandments. Extend the half-dozen things done rightly to a whole. dozen, and then to a score, and then to a hundred; and let it become habitual to do these things rightly. When the right doing of these things commends the doer to one person, he will next be apt to commend himself by similar conduct to other persons, [missing clause describing a condition or proviso]. Whether good behavior purchases favor or simply succeeds in evading penalties is at first immaterial.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if their standard happens to be the same (ground truth)
- B) if the course of Evolution holds on its way
- C) if Nature wishes to make caretakers
- D) unless he finds himself in the presence of another authoritative figure

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 343

**Metadata:** The following passage comes from Life Histories of Animals, Including Man; or, Outlines of Comparative Embryology, a textbook published in 1876 by A. S. Packard, an American embryologist.

**Question:** Still, in the generality of the forms, the radiated plan of structure is remarkably adhered to, the body as distinctly made up of sphæromeres, or wedge-shaped sections of the body, as the worms are of segments (arthromeres). In this and other respects, as well as the form of the larvæ, there is a remarkable parallelism between the worms and echinoderms. We will briefly review some of the anatomical features of the Echinoderms, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) in order to understand their complicated mode of growth (ground truth)
- B) in order to understand the physiological functions of their remarkable structure
- C) in order to understand the biological relationship between these two groups
- D) for the use of Colleges, Farm-Schools, and Agriculturists
- E) since they exhibit comparable body plans and symmetry

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 344

**Metadata:** The following passage comes from Life Histories of Animals, Including Man; or, Outlines of Comparative Embryology, a textbook published in 1876 by A. S. Packard, an American embryologist.

**Question:** The object of sexual reproduction, i. e., by eggs and spermatozoa, throughout the animal and plant world, is by bringing the germ or portion of protoplasm of one individual, which is an epitome potentially of its physical and psychical nature, to mingle with that of another of the same species, so that the offspring may combine the qualities of both parents, and not deteriorate. The species can be reproduced simply by budding, but the result would, if maintained for a number of generations, in the end prove disastrous to its integrity. Nature abhors self-fertilization. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) So that while, as in these Hydroids, the zooid form may be produced by budding, yet there are costs paid by the species which has gradually degenerated across the aeons.
- B) The embryo is therefore properly a gastrula.
- C) So with the earthworms.
- D) So that while, as in these Hydroids, the zooid form may be produced by budding, yet the time comes when the individuals of one colony must mingle their reproductive elements with those of a remote colony, through the medium of the water. (ground truth)
- E) Hence, if self-fertilization were permitted, the resulting genetic uniformity would increase, eroding the diversity essential for adaptive resilience; this loss of variation would render the population increasingly susceptible to environmental perturbations and pathogenic incursions, ultimately threatening its continued survival over successive generations.
- F) Therefore, the species, while capable of asexual reproduction through budding, must engage in sexual reproduction to ensure the vitality and genetic diversity of future generations.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 345

**Metadata:** The following passage comes from Stanley's Adventures in the Wilds of Africa : a Graphic Account of the Several Expeditions of Henry m. Stanley Into the Heart of the Dark Continent, a story of exploration published in 1892 by J. T. Headley, an American clergyman, historian, and adventurer.

**Question:** Stanley had made him coxswain of the boat Lady Alice, and he had proved to be one of the most trustworthy men of the expedition, and was to show himself in its future desperate fortunes, one of the most cool and daring, worthy, only halfcivilized as he was, to stand beside Stanley. The latter gave him strict directions as to his conduct in hunting up the fugitives-especially respecting the villages he might come across. Uledi told Stanley not to be anxious-he would soon find the lost party. Stanley, of course, could do nothing but wait, [missing clause acknowledging a countervailing fact].

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though filled with the most anxious thoughts (ground truth)
- B) though he wished to join the search
- C) though he was told there were many in the mountain inclosures
- D) though difficulties were constantly arising from the thieving propensities of the Arabs
- E) though his confidence in Uledi made waiting an easy task
- F) though the crew had to wait for supplies

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 346

**Metadata:** The following passage comes from Stanley's Adventures in the Wilds of Africa : a Graphic Account of the Several Expeditions of Henry m. Stanley Into the Heart of the Dark Continent, a story of exploration published in 1892 by J. T. Headley, an American clergyman, historian, and adventurer.

**Question:** It was on November 24th that Mr. Marston, of London, the well-known publisher, received this letter from the explorer, dated at a mission station at the southern end of Victoria Nyanza, September 3d, 1889: "It just now," wrote Mr. Stanley, “appears such an age to me since I left England. Ages have gone by since I saw you, surely. Do you know why? [missing sentence describing a cause or reason] On my side I may ask, what have you been doing?

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Because a daily thickening barrier of silence has crept between us during that time, and this silence is so dense that in vain we yearn to pierce it. (ground truth)
- B) Indeed, they have good cause to be distrustful of the Arabs and the Wangwana of Zanzibar.
- C) Because the journey across the Congo, with its perilous rivers, dense jungles, and hostile tribes, demanded months of relentless travel, making the passage of time feel interminable indeed.
- D) Because I have been wandering in darkest Africa, and it has been impossible to send word to you.
- E) The purpose of my long absence is due to the numerous challenges and obstacles encountered during my journey.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 347

**Metadata:** The following passage comes from Stanley's Adventures in the Wilds of Africa : a Graphic Account of the Several Expeditions of Henry m. Stanley Into the Heart of the Dark Continent, a story of exploration published in 1892 by J. T. Headley, an American clergyman, historian, and adventurer.

**Question:** Two days after, this chief sent some of his mer to Bumbireh for food, but they were not allowed to land. On the contrary, they were attacked, and one man was killed and eight were wounded. This gave Stanley another strong reason for making war at once without further negotiations, to which Mtesa's chief gladly consented. [missing sentence describing an inference or effect] The natives of Bumbireh were evidently expecting trouble, for they felt sure the attack on the friends of Stanley the day before would be quickly avenged.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Stanley saw, therefore, that prompt measures must be taken, and he at once clapped thirty-two of the discontented in irons, drove them into canoes, and sent them off to Ukurenga.
- B) In consequence, Stanley decided to act immediately.
- C) Accordingly, next morning, he mustered two hundred and eighty men with fifty muskets, and two hundred spearmen, and placed them in eighteen canoes and set out for Bumbireh, eight miles distant, and reached the island at two o'clock in the afternoon. (ground truth)
- D) Thus far they had met with no opposition whatever, and the warlike tribe Stanley had feared so much, and had taken such a large force to overcome, seemed to have no existence.
- E) Accordingly, the next morning, he sent entreaties of peace to Bumbireh, hoping to avert hostilities.
- F) Consequently, Stanley deemed it necessary to mobilize his forces immediately, convinced that a swift, decisive campaign would deter further resistance, secure his objectives in the region, reassert his authority over the local chiefs, and ensure the safety of his expedition's men.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 348

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent, an American .

**Question:** There were more idols there than we had seen anywhere. Nearly every house had its little outside shrine, with a hideous red idol and bunch of flowers. From hot and dusty streets, our carriages turned into the green enclosure of the Memorial Gardens. They are not large, [missing clause revising an implied expectation]. Each carriage is required to proceed at a walking pace, in accordance with the solemnity of the place.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but are well kept and very beautiful (ground truth)
- B) but we had a good deal of difficulty in making our carriage drivers understand what we wanted
- C) they are instead modest, a deliberate counterpoint to the surrounding bustle
- D) but we were not allowed to go further than the garden
- E) but they are beautifully maintained and serene

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 349

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent, an American .

**Question:** Sunday:-Here we are in the Bay of Naples. Yesterday they woke me before daylight to look out at Vesuvius. The silvery grey-blue water was banked by dark blue mountains, and behind the mountains. the sky glowed red. Did you know they have strikes in Italy? They do. As we were about to go ashore this morning, we heard that it was uncertain when the Irene would proceed to Genoa, [missing clause describing a cause or reason]. After waiting around for an hour we decided to land, for a while at least.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because the port workers were on strike, disrupting the ship's schedule
- B) due to the dockworkers' strike
- C) because there was a strike among the deck hands, and the cargo could not be unloaded (ground truth)
- D) for the coolies invariably say "yes", whether they understand or not

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 350

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent, an American .

**Question:** So in I got, and my wily coachman drove away and up to the stable, where, instead of changing the horse, he turned around and started for Nan Yang. As I knew it would be useless to remonstrate, I held my peace and waited to see what happened. [missing sentence revising an implied expectation] You never saw anything as crooked as these Chinese streets.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) The brute, however, developed a surprising speed and endurance, so I settled down to enjoy the ride. (ground truth)
- B) However, I was alive and ready to see all there was to be seen when we came into the harbor.
- C) The brute, however, slowed peaceably, so I settled down to endure the ride.
- D) I had expected the coachman to simply change the horse, but instead he had a different destination in mind.
- E) I had expected to be taken back to the inn but it was not to be.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 351

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent.

**Question:** We wanted to see the Cathedral and the Museum ; but the man was so stupid we could do nothing with him, and after driving around in purposeless fashion for an hour or so, in the vain hope that a ray of light would dawn upon him, we gave it up and went home, deciding on the way to leave for Bangalore the next evening. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Our frustration with the local guide left us feeling exhausted and disheartened.
- B) So my memories of Madras will be roads, dripping trees, and long stretches of stuccoed garden walls of a uniform discolored and mouldy yellow, all seen from the front seat of a gharry. (ground truth)
- C) His obstinacy left us feeling helpless, and the hour slipped away like a mirage, the day dissolving into an aimless haze that made our plans feel futile for the rest of the afternoon.
- D) Thus, alas, I cannot tell you much about the famous Cathedral in Madras.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 352

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent, an American .

**Question:** At last the three days wore away, and early on Sunday morning we anchored off Penang. An hour later, when the tender came, we were all ready to leave, with no lingering this time. The harbor was full of queer little Chinese rowboats, with huge eyes painted on the stern. You know the Chinese say their boats can't see where they are going, [missing clause describing a condition or proviso].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if they have no eyes (ground truth)
- B) unless someone guides them with an oar
- C) even if they possess sight
- D) if it were not for the Arab and French servants
- E) unless they are steered by a seasoned captain

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 353

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent, an American .

**Question:** The steamer waited at Port Said until afternoon for the arrival of the Osiris with the mails, and all morning the decks looked like an Oriental bazaar, for the people from shore were allowed to bring their wares on board and there was such an array of jewelry, laces, embroidery, glittering silver-wrought shawls, and postal cards spread out on the deck, that we had to move carefully not to step on something. Over the side, boys were diving for pennies, and boats with serenaders surrounded us. About two o'clock the decks were cleared, and we began to move. It took us all night to go through the Canal, [missing clause acknowledging a countervailing fact]. The man who knows everything told us it costs $10,000 to get a ship the size of the China through, and that it was not De Lesseps, but an Englishman named Waghorn who conceived the idea of that canal, but as he died some years before the work was begun, De Lesseps had all the glory.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though our quarters were most airy and comfortable
- B) despite the fact that it was a slow and tedious process
- C) though the heat of the sun was so intense that I could hardly endure it
- D) though it is only a hundred miles long (ground truth)
- E) though the canal offered a swift passage

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 354

**Metadata:** The following passage comes from The Spirit of Modern Philosophy : an Essay in the Form of Lectures, a series of lectures on philosophy published in 1892 by Josiah Royce, an American philosopher.

**Question:** But the world is n't unreal. It extends infinitely beyond our private consciousness, because it is the world of an universal mind. What facts it is to contain only experience can inform us. There is no magic that can anticipate the work of science. Absolutely the only thing sure from the first about this world, however, is that it is intelligent, rational, orderly, essentially comprehensible, [missing clause describing an inference or effect]. This Self infinitely and reflectively transcends our consciousness, and therefore, since it includes us, it is at the very least a person, and more definitely conscious than we are; for what it possesses is self-reflecting knowledge, and what is knowledge aware of itself, but consciousness?

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that our finite minds may nevertheless grasp some portion of its logic
- B) so that we can systematically deduce its laws, predict its phenomena, align our actions accordingly with precision today
- C) so that mortals cannot fully know it from innate ideas, nor from our experience
- D) so that all its problems are somewhere solved, all its darkest mysteries are known to the supreme Self (ground truth)
- E) so that, in order to be relatively describable, nature must embody purposes, and so be possessed of worth
- F) so that none of its problems are ever fully solved, none of its mysteries ever fully transparent to the supreme Self

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 355

**Metadata:** The following passage comes from The Spirit of Modern Philosophy : an Essay in the Form of Lectures, a series of lectures on philosophy published in 1892 by Josiah Royce, an American philosopher.

**Question:** Compare once more Falckenberg's definition of Hegel's use of "concrete," as given above. That the Individual is contained in the Universal is also expressly asserted by Hegel (Werke, vol. vi. p. 323; compare p. 316). 1 Encyclop., Werke, vol. vi. p. 340. 2 Id., p. 339. In case of the form of logical judgment which Hegel is discussing in the passage now cited, he is laying special stress upon the fact that here already, [missing clause acknowledging a countervailing fact], the individual stands in relation to others, and is not conceived by himself, or apart from his relations.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although the individual seems autonomous, it remains interrelated
- B) although the true Vernunft-Allgemeinheit has not been fully reached (ground truth)
- C) although at this moment meant by me
- D) although it is indeed our privilege to-day to understand Kant (if one may borrow again his own often quoted words) besser als er sich selber verstand
- E) although it may seem isolated

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 356

**Metadata:** The following passage comes from The Spirit of Modern Philosophy : an Essay in the Form of Lectures, a series of lectures on philosophy published in 1892 by Josiah Royce, an American philosopher.

**Question:** If I tolerate the impulse, if I declare it to be just the nettle of sin, if I call its evil illusory, then my moral optimism is indeed open to the condemnation of Amos, who cries woe upon all such vindications of the divine order. [missing sentence revising an implied expectation] The justification of the existence of my evil impulse comes just at the instant when I hate and condemn it.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, this is not necessarily true if one considers that the struggle itself may be the essence of moral progress.
- B) But suppose I resist the evil impulse, hate it, hold it down, overcome it, then, in this moment of hating and condemning it I make it a part of my larger moral goodness. (ground truth)
- C) Nevertheless, the paradox persists, for the very act of rejecting the impulse simultaneously affirms its presence, thereby rendering my moral confidence precarious and subject to the scrutiny of Amos's prophetic critique again.
- D) But as to pessimism itself, Schopenhauer's famous doctrine, as to this terrible view that life is through and through tragic and evil, what is my attitude towards that?

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 357

**Metadata:** The following passage comes from Cases on Constitutional law, a collection of cases published in 1897 by John Day Smith, an American law professor.

**Question:** But the court held that this was not a sound construction of the statute, and "that if the parties killed had come into that neighborhood with intent to arrest the deserters named, and had been employed by the proper officer for that service, and were, in the proper prosecution of that purpose, returning to Grinnell with a view to making other arrangements to discharge this duty, they were still engaged in arresting deserters, within the meaning of the statute. It is not necessary," said the court, "that the party killed should be engaged in the immediate act of arrest, but it is sufficient if he be employed in and about that business when assaulted. [missing sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The reason is so apparent that it need only be stated.
- B) Because the statute’s intent was to protect those participating in the pursuit of deserters, the court deemed it sufficient that individual was engaged in that business, even if not performing the arrest at that instant
- C) The rationale behind this interpretation is to ensure that those involved in the broader process of maintaining law and order are protected under the statute."
- D) The purpose of the law is to protect the life of the person so employed, and this protection continues so long as he is engaged in a service necessary and proper to that employment." (ground truth)
- E) Simply because there is here neither trial nor punishment within the legal meaning of these terms.
- F) The purpose of the law is to endanger the life of the person so employed, and this endangerment continues so long as he is engaged in a service necessary and proper to that employment."

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 358

**Metadata:** The following passage comes from Cases on Constitutional law, a collection of cases published in 1897 by John Day Smith, an American law professor.

**Question:** The government, possessing the powers which are to be exercised for protection and security, is clothed with authority to determine the occasion on which the powers shall be called forth; and its determination, so far as the subjects affected are concerned, is necessarily conclusive upon all its departments and officers. [missing sentence describing an inference or effect] The existence of war would render the necessity of the proceeding only more obvious and pressing.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Therefore it has been determined that the failure of congress to exercise this exclusive power in any case is an expression of its will that the subject shall be free from restrictions or impositions upon it by the several states.
- B) Hence, it follows that any challenge to such discretion would be futile.
- C) The United States, in effect, asks the specific execution of the terms of the treaty of 1819, to the end that the disorder and public mischiefs that will ensue from a continuance of the present condition of things may be prevented.
- D) Hence, the executive's declaration is absolute, binding all subordinate agencies, and any dissenting voice must yield to the sovereign judgment, for the imperative of safeguarding national interests overrides individual dissent; consequently, the state may marshal all resources to secure peace, and the populace is compelled to comply with the enacted measures without reservation constitutional provisions empower the government to act decisively during crises immediately.
- E) If, therefore, the government of the United States, through its legislative department, considers the presence of foreigners of a different race in this country, who will not assimilate with us, to be dangerous to its peace and security, their exclusion is not to be stayed because at the time there are no actual hostilities with the nation of which the foreigners are subjects. (ground truth)
- F) If, therefore, the government of the United States, through its legislative department, considers the presence of foreigners of a different race in this country, who will assimilate with us, to be dangerous to its peace and security, their exclusion is contingent on the existence of hostilities with the nation of which these foreigners are subjects.

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 359

**Metadata:** The following passage comes from Cases on Constitutional law, a collection of cases published in 1897 by John Day Smith, an American law professor.

**Question:** If the decision of the majority had stricken down all the income tax sections, either because of unauthorized exemptions, or because of defects that could have been remedied by subsequent legislation, the result would not have been one to cause anxiety or regret; for in such a case congress could have enacted a new statute that would not have been liable to constitutional objections. [missing sentence revising an implied expectation] Thus, undue and disproportioned burdens are placed upon the many, while the few, safely entrenched behind the rule of apportionment among the states on the basis of numbers, are permitted to evade their share of responsibility for the support of the government ordained for the protection of the rights of all.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But those who make this argument forget that all the property which, by the decision now rendered, remains subject to national taxation by the rule of uniformity, is also subject to be taxed by the respective states.
- B) But the serious aspect of the present decision is that, by a new interpretation of the constitution, it so ties the hands of the legislative branch of the government, that without an amendment of that instrument, or unless this court, at some future time, should return to the old theory of the constitution, congress cannot subject to taxation-however great the needs or pressing the necessities of the government-either the invested personal property of the country, bonds, stocks, and investments of all kinds, or the income arising from the renting of real estate or from the yield of personal property, except by the grossly unequal and unjust rule of apportionment among the states. (ground truth)
- C) However, even though the majority's hypothetical decree to abolish every provision of the income tax might have seemed a radical remedy, the practical consequence of such an all‑encompassing repeal would have been an immediate collapse of federal revenue streams, forcing Congress to scramble for emergency funding measures that would likely trigger a cascade of constitutional challenges, thereby eroding public confidence in the legitimacy of the tax system and undermining the very fiscal stability the law seeks to safeguard, and in doing so, it would have amplified the very inequities the decision ultimately aimed to mitigate.
- D) But that view does not meet the argument that the assessment and collection of a direct tax on incomes-such tax being apportioned on the basis merely of numbers in the respective states-were never contemplated by the framers of the constitution.
- E) However the decision could have been reversed,  and a new law put in place, thus ensuring the majority's voice was not completely silenced.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 360

**Metadata:** The following passage comes from Cases on Constitutional law, a collection of cases published in 1897 by John Day Smith, an American law professor.

**Question:** They were as completely out of the donors, at the instant of their being vested in the corporation, and as incapable of being asserted by the students, as at present. According to the theory of the British constitution, their parliament is omnipotent. To annul corporate rights might give a shock to public opinion, which that government has chosen to avoid; but its power is not questioned. Had parliament, immediately after the emanation of this charter, and the execution of those conveyances which followed it, annulled the instrument, [missing clause describing an inference or effect]. Yet then, as now, the donors would have had no interest in the property; then, as now, those who might be students would have had no rights to be violated; then, as now, it might be said, that the trustees, in whom the rights of all were combined, possessed no private, individual, beneficial interest in the property confided to their protection.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) no one could therefore have called the measure illegal, however repugnant they judged it
- B) so that the donors would remain devoid of interest, the trustees would lose proprietary claims, and the students would be precluded from asserting rights
- C) so far that the will of the legislature, not the will of the donor, becomes the law of the donation
- D) the students would have so lost any claim they might otherwise have had
- E) so that the living donors would have witnessed the disappointment of their hopes, the perfidy of the transaction would have been universally acknowledged (ground truth)
- F) so that, in the end, the state will derive just as much revenue from them as if they were there before the sale

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 361

**Metadata:** The following passage comes from Cases on Constitutional law, a collection of cases published in 1897 by John Day Smith, an American law professor.

**Question:** As has been said by this court: “Commerce on land between the different states is so strikingly dissimilar, in many respects, from commerce on water, that it is often difficult to regard them in the same aspect in reference to the respective constitutional powers and duties of the state and federal governments. No doubt commerce by water was principally in the minds of those who framed and adopted the constitution, [missing clause acknowledging a countervailing fact]. Maritime transportation requires no artificial road-way.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) though their railroad was a part of a system of roads constructed under the authority and direction of the United States
- B) though commerce on land had begun to expand
- C) although both its language and spirit embrace commerce by land as well (ground truth)
- D) though they should carry passengers only
- E) although maritime routes depend on natural waterways, they still face unpredictable currents

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 362

**Metadata:** The following passage comes from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, a British politician.

**Question:** We have no idea of that sort at all, neither do we think we can raise up a little oasis of co-operation in the midst of a great wilderness of competition. We have no such idea whatever. Every attempt made in this direction has been a failure, and we do not intend to try it again. [missing sentence describing a cause or reason] We are in no sense Utopians.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) They were failures because they did not take account of what was going on around them, of having an association which should dominate over all in the interest of all. (ground truth)
- B) Because the upper and middle classes have laid their hands on the endowments intended for the benefit of the poor, and taken them to their own advantage.
- C) The very nature of our society is antithetical to such ideals.
- D) The entrenched power of the landed aristocracy and the industrialists has stifled any attempt at collective organization.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 363

**Metadata:** The following passage comes from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, British politicians.

**Question:** (Hear, hear, and Oh.) I have been in hundreds of them. My speech will go amongst Lancashire and Yorkshire men who work in those mills, and who will know whether what I am saying is true or not. (Cheers.) In every new mil! built in the last twenty years the best resources of science have been utilised, [missing clause describing a cause or reason]. (Hear, hear.)

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for painting, or for music, or for sculpture, and if not, how will excellence in these be won
- B) to meet the growing demand for speed and quality in textile production, reduce waste, and improve worker safety
- C) because owners of capital have found that under comfortable conditions more is got from the labor, and therefore they do it (ground truth)
- D) because the mill owners wanted to maximize efficiency and profits
- E) because we say hungry men make revolutions and riots, but they never made and organised revolution yet

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 364

**Metadata:** The following passage comes from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, a British politician.

**Question:** And with regard to this building society business which is brought forward, and the amount of land held by building societies, a great many of those lands are mortgaged heavily to the capitalist class; and in addition to that with regard to the large number of owners whom my opponent quotes from the Blue-books, I would ask him to look at the "Financial Reform Almanack," and see how those Blue-books have been fudged up, and how a single owner sometimes figures as eight or ten. [missing sentence revising an implied expectation] Suppose they get a full return for all the labor which they do, they would get in each year three or four times the amount of their building allotment.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet, the reality is that the returns are far lower than the inflated figures in the Blue‑books imply.
- B) But do you suppose that even those who hold building allotments are going to be dispossessed or injured? (ground truth)
- C) But even if we were to grant that they actually earned it.
- D) But who are the shareholders in the railroads : do they ever do any good in the world?

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 365

**Metadata:** The following passage comes from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, a British politician.

**Question:** So infamous was the slavery under unrestricted competition that it was necessary to stop the degradation which was going on. Again, people were growing up in ignorance. Parents did not see that their children were educated in any way whatever. It became so serious to the community -so manifest was it that it was necessary to intervene, that the School Board was introduced, and it has not gone half far enough in my humble judgment, [missing clause revising an implied expectation]. There is an interference on the part of the State.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but nonetheless Parliament respected the rights of parents to not educate their children, and allowed them free rein
- B) but it is not common sense
- C) that the State ought to have taken a more comprehensive approach to ensure equitable education for all children
- D) to ensure that every child receives at least some basic instruction
- E) but nevertheless the rights of parents to bring up their children in ignorance were interfered with by Parliament, and were put a stop to as far as they then could go (ground truth)
- F) but that is not Socialism

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 366

**Metadata:** The following question is drawn from a debate between Henry Hyndman and Charles Bradlaugh, published in 1884 under the title Will Socialism Benefit the English People?

**Question:** But I say that such a revolution will enhance individuality, it will relieve people from this crushing domination of a class, and will enable each man to exchange through Government banks and Government distributive centres. Then men may have and own the fruits of their labor whereby they may all benefit. [missing sentence describing an inference or effect] England wherein each man will work for all, where there will be free exchange of the fruits of labor without any profit, and where we shall hold up a really organised centre for mankind.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus, the people's prosperity will rise, and equality shall flourish for all.
- B) This will lead to a society free from exploitation.
- C) Therefore I say what we look to is a thoroughly organised SOCIALISM. (ground truth)
- D) Therefore I say what we look to is a thoroughly organized CAPITALISM.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 367

**Metadata:** The following passage comes from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, British politicians.

**Question:** How is the distinction to be made between employment on skilled and unskilled labor? Individual effort regulates all this; State effort would crush it all. You talk about foreign produce. How are you going to get it? You will have no markets here. ("Why not?") Why, [missing clause describing a condition or proviso], nobody can sell to anybody. (Laughter.)

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if everything is privately held
- B) if the state forbids private exchange,
- C) unless you succeed by argument
- D) if all things are owned by everybody (ground truth)
- E) unless you have something to offer

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 368

**Metadata:** The following passage comes from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, a British politician.

**Question:** It is the best educated and organised and capable men who have always made revolutions in our country. The revolu tion of 1641 to 1649, one of the greatest revolutions in history, was made in the interest of the middle classes, but how was it made? It was made by strong, stalwart, well-conducted, well-fed men. I say those revolutions were beneficial, and I say that such a revolution to-day, [missing clause acknowledging a countervailing fact]. (Cheers.)

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although God forbid it should come by force, I trust will come with the organised education of all (ground truth)
- B) even if wrongfully, we have tried for thirty years to awaken men to the knowledge of it
- C) although God forbid it should come by force, I trust will come without the organised education of all
- D) though it may also sow discord and destabilise the social fabric
- E) if it is not accompanied by the same level of education and organization as before

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 369

**Metadata:** The following passage comes from The Medicolegal Aspect of Accidents Caused by the Röntgen Rays, a treatise published in 1904 by Carl Beck, an American physician.

**Question:** If we have made up our mind to influence the carcinoma cells we must employ sufficient energy to enforce this result. This does not imply, however, that the other extreme should be striven for. We must follow our therapeutic strategy in a determined but carefully observant manner. [missing sentence describing an inference or effect] The tube should be as near the tumorous area as possible, the distance of the tubal wall from the skin never exceeding two inches.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Hence, it follows that the energy must be applied precisely and judiciously.
- B) The practical modus operandi, therefore, would be about as follows: The patient suffering from malignant disease is irradiated without first submitting to tentative exposures. (ground truth)
- C) Consequently, the precise positioning of the tube ensures maximal radiation delivery while minimizing collateral tissue damage, thereby enhancing therapeutic efficacy in patients with advanced disease.
- D) So, practically, we do not need to fear much in our diagnostic efforts, and if we could make the rays still more powerful, in order to get more differentiation, we would not hesitate to do it.
- E) Therefore, if the treatment is of a beautifying nature the surrounding tissues must be protected.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 370

**Metadata:** The following passage comes from The Medicolegal Aspect of Accidents Caused by the Röntgen Rays, a treatise published in 1904 by Carl Beck, an American physician.

**Question:** The points of the complaint were: (1) The Insufficient information of the patient in regard to the possible consequences of the treatment; (2) it alleged insufficient protection of those areas which did not require irradiation; (3) the continuation of the treatment after redness had appeared. The court disregarded the first two points, but sustained the third, viz., negligence. This judgment is based on an error. If the Court had held that the chest should have been protected it might have been more correct, [missing clause revising an implied expectation]. In treating malignant diseases, we should be governed by principles which differ entirely from those emphasized in regard to cosmetic treatment.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, since the patient was being treated for malignant disease and not for cosmetic purposes it is more accurate to judge that protection of other areas may have been less critical
- B) however, the court's decision might have been more accurate if it had considered the necessity of chest shielding
- C) but then the question is, Shall we reach the desired result, whether for diagnosis or therapy, by a short exposure
- D) however, which I show here, offer perfect protection for the physician
- E) but it could not have found fault with the continuation of the treatment after slight reaction had shown itself (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 371

**Metadata:** The following passage comes from The Medicolegal Aspect of Accidents Caused by the Röntgen Rays, a treatise published in 1904 by Carl Beck, an American physician.

**Question:** Fortunately, the longest exposure (the pelvis) does not now, with the aid of the Wehnelt interrupter, require more than about five minutes' exposure, and this will be tolerated even by a susceptible individual. So, practically, we do not need to fear much in our diagnostic efforts, and if we could make the rays still more powerful, in order to get more differentiation, we would not hesitate to do it. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) However, despite the promise of higher diagnostic clarity, the expectation that more powerful rays might introduce unforeseen complications persists, yet current empirical data indicate that safety margins remain comfortably within acceptable limits, assuaging professional concerns for the medical community today.
- B) But the rays do not in their present capacity possess so much force in the deeper tissues of the body as to induce a complete regressive metamorphosis.
- C) However, as we are well aware of the dangers of exposure even with the Wehnelt interrupter, it is advisable to proceed cautiously.
- D) But when repeated exposures of ten minutes' time are necessary, the question of susceptibility, as well as of ordinary cumulative irritation, should be considered, and therefore the intervals between the exposures should be made long-a week on an average. (ground truth)
- E) But with the employment of the rays for therapeutic purposes this question of injuries has entered into a new phase.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 372

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** M. de Tonti, a former coadjutor of La Salle, was sent to Michillimakinac, to bring back the French who had taken up their quarters there, and who amounted to more than one hundred persons. A missionary and M. de Courtmanche were employed in soliciting the chiefs of the western tribes to cease from warfare, and to bring all their Iroquois prisoners to the proposed meeting at Montreal. In the meantime, the agents of the New England colonies were engaged in endeavours to counteract the influence of the French among the cantons, [missing clause revising an implied expectation]. A severe law against Jesuit priests entering the New England territory was declared to be valid in the cantons as well as other parts.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but with no great success (ground truth)
- B) to prevent them from converting more Indians
- C) to suppress French missionary influence
- D) but the displaced councillors were restored to their former positions, and suitable steps taken in regard to the liquor traffic, tithes, and other occasions of discord

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 373

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** These had even promised to migrate in a body, but when the period arrived for fulfilling the promise they refused; and, not feeling safe on the island, applied to the Governor for protection. This D'Aillebout accorded by allowing the remnant of their number to move to Quebec and establish their cabins in the vicinity of Fort St Louis. In the course of 1658, several Frenchmen were killed by Iroquois, [missing clause acknowledging a countervailing fact]. D'Aillebout, in consequence, issued orders to capture all Iroquois who should present themselves about any of the French posts, and that the prisoners should be held as hostages, and as means of exacting penalties for the murders which had been committed.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although some Iroquois had likewise suffered losses at the hands of French forces
- B) but the Iroquois continued to raid French settlements with impunity
- C) although a truce existed at the time (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 374

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** M. de Tonti, a former coadjutor of La Salle, was sent to Michillimakinac, to bring back the French who had taken up their quarters there, and who amounted to more than one hundred persons.† A missionary and M. de Courtmanche were employed in soliciting the chiefs of the western tribes to cease from warfare, and to bring all their Iroquois prisoners to the proposed meeting at Montreal. 185. In the meantime, the agents of the New England colonies were engaged in endeavours to counteract the influence of the French among the cantons, [missing clause revising an implied expectation]. A severe law against Jesuit priests entering the New England territory was declared to be valid in the cantons as well as other parts.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) to suppress French missionary influence
- B) but with no great success (ground truth)
- C) but the displaced councillors were restored to their former positions, and suitable steps taken in regard to the liquor traffic, tithes, and other occasions of discord
- D) to prevent them from converting more Indians

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 375

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** These had even promised to migrate in a body, but when the period arrived for fulfilling the promise they refused; and, not feeling safe on the island, applied to the Governor for protection. This D'Aillebout accorded by allowing the remnant of their number to move to Quebec and establish their cabins in the vicinity of Fort St Louis. In the course of 1658, several Frenchmen were killed by Iroquois, [missing clause acknowledging a countervailing fact]. D'Aillebout, in consequence, issued orders to capture all Iroquois who should present themselves about any of the French posts, and that the prisoners should be held as hostages, and as means of exacting penalties for the murders which had been committed.

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) although some Iroquois had likewise suffered losses at the hands of French forces
- B) though incapable of pursuing them into their own settlements and inflicting the punishment they deserved
- C) although a truce existed at the time (ground truth)
- D) but the Iroquois continued to raid French settlements with impunity

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 376

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** Additions were also made to the defences of Montreal and Quebec. In the latter city new redoubts were constructed, and the means of defence further improved by the completion of gateways surmounted by battlements at the two western points of exit. The inhabitants on the lands above and below Quebec were directed, in case of an invasion, to remove their families and property, [missing clause describing a cause or reason]. All these precautions and preparations turned out to be unnecessary.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because, according to Knox, they had been too "roughly handled" in the fight, General Murray ordered the gates to be closed, and the guards on the ramparts, who had not been relieved since morning, to be changed
- B) for concealment, into the recesses of the neighbouring forests, and then to dispatch their able-bodied men to the defence of the city (ground truth)
- C) so that the enemy would be deprived of local resources and shelter
- D) in order to prevent them from falling into the hands of the enemy
- E) in order to establish themselves and erect batteries in positions convenient for bombarding the city

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 377

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** The campaign can scarcely last another month, in consequence of the autumnal gales, which are here so disastrous to shipping, and so severe. It might seem that after so favourable a prelude, the safety of the colony can scarcely be doubtful. [missing sentence revising an implied expectation]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet the looming winter, with its relentless squalls and the colony’s dwindling stores, threatened to undo the optimism.
- B) However, one must remain cautious as the future holds many uncertainties.
- C) But, as an offset to the general conditions which favoured the welfare of the colony, the inhabitants, both French and Indians, were troubled with maladies which proved fatal to many.
- D) Such, however, is not the case, as the capture of Quebec depends on a coup-de-main. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 378

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** The preliminaries having been arranged, happily without the occurrence of quarrels so likely to take place in such a concourse of individuals belonging to different nations, the ceremonies and customary distribution of presents were followed by a mutual interchange of stipulations, rendered intelligible to all by means of interpreters. The final result was a treaty of peace, to which the chief contracting parties were the French, the Hurons, the Algonquins, and the Iroquois, who agreed, thenceforward, to remain on peaceable terms with each other. [missing sentence describing an inference or effect] The 56.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) The peace thus established was of long duration.
- B) This treaty significantly reduced tensions among the indigenous tribes and their French allies.
- C) Consequently, the neighboring peoples could resume commerce and cultural exchanges without the fear of sudden conflict.
- D) Thus the operations against Fort Niagara were entirely successful, involving in the result the easy capture of the other French forts by General Stanwix, since their garrisons had been reduced by the numbers detached for the relief of Captain Pouchot.† 

271.
- E) The peace thus established was not of long duration. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 379

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** It was also about this time that the Iroquois began to establish, on a considerable scale, a regular traffic with the northern and western Indians, in such manner as to draw off the trade in skins from the route of the Lower St Lawrence, and so as to make themselves the channel of communication with the traders of the English colonies, who paid higher prices than the French. De Courcelle, foreseeing that Canadian commerce with the western tribes would be ruined in that way, undertook the expedition to the north shore of Ontario in order to menace the Senecas, as has been already described. [missing sentence describing a cause or reason]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The same cause led that Governor to project the establishment of a fort and military station at Cataracoui (Kingston), which was afterwards built by his successor, and called Fort Frontenac. (ground truth)
- B) For this purpose he employed an intrepid officer, named Varrenne de la Varendrye, who occupied about fifteen years in conducting those explorations.
- C) The French, recognizing the potential loss of revenue and influence due to English competition, wanted to secure their trade monopoly.
- D) For this purpose he selected the celebrated Nicolas Perrot, and M. Louvigny, an officer of merit, to proceed by the route of the Ottawa river to Michilimakinac with a large convoy, and to carry presents and various supplies of merchandise, such as the savages required for warfare and the chase, as well as for domestic use.
- E) Because the English, offering higher prices, were drawing the fur trade away from French hands, De Courcelle felt compelled to act.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 380

**Metadata:** The following passage comes from Trouting on the Brulé River, or Summer-wayfaring in the northern wilderness, a work of description and travel published in 1880 by John Lyle King, an American lawyer and writer known for his vivid essays.

**Question:** It overlooked a broad, smooth reach of the Paint river, skirted with borders of unbroken forest. At the foot of the hill, a little brook, hidden under interlacing branches, and cold with the chill of its supplying or parent springs, ran into the stream. Doubtless it was a very covert for shoals of trout. High and Denison must have had an insight of this, [missing clause describing a cause or reason].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) since they were keen anglers who appreciated the beauty and bounty of the wilderness
- B) for they set out with rods and baskets, to find some place choked with limbs and brush wherein to cast the fly
- C) because the brook's icy depth concealed the trout's shimmering schools, High and Denison, seasoned trappers with keen eyes, intuitively knew to seek the hidden shoals before early sunrise
- D) for they requested supplies for parties in quest of hunting and fishing amusement
- E) for they set out with rods and baskets, to find some accessible silent nook or recess free enough of limbs and brush wherein to cast the fly (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 381

**Metadata:** The following passage comes from Trouting on the Brulé River, or Summer-wayfaring in the northern wilderness, a work of description and travel published in 1880 by John Lyle King, an American lawyer and writer known for his vivid essays.

**Question:** This hardihood now roused High's piscatory blood; but how to harmonize it and his piscatory taste, to which baiting seemed only foul play and wholly repugnant, was a perplexity-for a moment. He knew a pickerel would turn up its nose at a fly gewgaw. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) So he had provided at Dickey's a jolly front of antlers, which had long hung seasoning among the cobwebs of the cabin rafters, and sent it by Evanson's team to Marinette for expressage to Chicago.
- B) Hence, he resolved to employ a more natural lure, hoping to entice the pickerel with subtlety and avoid the fly's pretentiousness.
- C) Thus, he saw no use for the fly to catch a pickerel.
- D) So, to compromise himself only partially, he baited his hook with a wriggling red worm.
- E) He, therefore, armed and posted himself in the bushes with a finger on the trigger ready to execute sanguinary justice.
- F) So, to compromise himself only partially, he tacked on what we supposed was a slit of bacon with a new glaring red-fly. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 382

**Metadata:** The following passage comes from Figure Skating, an introduction to skating published in 1905 by H. R. Yglesias, a British author.

**Question:** BEAKS IN the Beak, like Rockers and Counters, we have the same edge throughout and progression changed from forwards to backwards, or backwards to forwards. Beaks are divided into Beaks and Counter Beaks, according as the revolution of the foot is Rockerwise or Counterwise. [missing sentence revising an implied expectation] They form beautiful marks on the ice, and are the chief constituent of some of the finest picture figures.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) They are, however, distinct from all the true turns in that they consist of a mere push, stop, and pull back of the tracing foot, and are made without any change of front of the body. (ground truth)
- B) However, unlike Rockers and Counters, Beaks have no distinction between forward and backward edges, allowing them to change direction seamlessly.
- C) Yet, contrary to the common belief that such delicate turns are merely ornamental, these beaks carry the skater's weight, dictate the rhythm of the entire routine, and weave precision into every glide, ensuring seamless transitions with a subtle grace that captivates the audience.
- D) The full eight form, however, should not be discarded.
- E) But it seems better to classify Steps according to the actual edges and turns skated; merely extending the term to cases where an actual turn is made on one foot, the second edge of the turn being held but momentarily, and a fresh curve immediately taken up on the other foot.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 383

**Metadata:** The following passage comes from Figure Skating, an introduction to skating published in 1905 by H. R. Yglesias, a British author.

**Question:** 50 COUNTER-ROCKER AND ROCKER 51 Counters and Rockers are skated in two forms, namely, with change of curve (without change of edge), and without such change of curve. There is much difference of opinion as to which is the best. Each sort has its advantages. The non-changed curve turn is the best drawing, [missing clause describing a cause or reason]. Another advantage is that the risk of making a change of edge is almost eliminated.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) because the second curve of outside or inside edge follows directly from the first edge; and the two curves are joined at the point of the turn without the intervention of a bit of curve in the contrary direction (ground truth)
- B) because it allows the skater to maintain a continuous line, reducing the likelihood of missteps and preserving the aesthetic flow of the figure while simultaneously keeping the edge pressure balanced, thereby enhancing both the technical precision and the visual appeal of the performance
- C) because one is not in position at the end of the forward inside edge for the back outside edge of the other foot
- D) because it requires less precision and coordination
- E) in order that its momentum in turning into the right position may be utilised to gain power

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 384

**Metadata:** The following passage comes from Figure Skating, an introduction to skating published in 1905 by H. R. Yglesias, a British author.

**Question:** The place and manner in which the change of position during the curve is to be effected is a matter for the individuality of the skater. On the principle of harmonious movement the best course is a gradual distribution of the swing throughout the curve. [missing sentence describing an inference or effect] The movement will be a steady swing from one position to the other, passing close to the tracing leg.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Theoretically therefore the free leg should pass the tracing leg half-way through the curve; in practice, however, it is better to keep it behind in forward curves for longer than half-way, and in back curves to bring it behind before half-way. ← (ground truth)
- B) Hence, the careful modulation of the swing will not only maintain balance but also subtly align the body’s center of gravity, producing a fluid, uninterrupted glide that anticipates the tracing leg’s path, and ensures a smooth transition between each arc.
- C) Hence, it follows that a smooth and controlled curve is achieved when the skater transitions gradually from one position to another.
- D) The free leg is thus in the proper position for the resulting curve of back inside.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 385

**Metadata:** The following passage comes from An Outline of English Local Government, a lecture on local government published in 1894 by Edward Jenks, a British jurist and writer.

**Question:** By-laws made under this power must observe the rules followed by a municipal council in making by-laws for its borough; that is to say, they must be passed by a meeting consisting of at least three-fourths of the members of council, they must be published for at least forty days before coming into operation, and all by-laws (except those made for the suppression of nuisances under the Public Health Act) must be submitted to a Secretary of State before they become legally valid. Offences against a county by-law are punishable on summary conviction; [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) but no by-law may appoint a penalty exceeding £5 for any one offence, and no county by-law has any force within a municipal borough (ground truth)
- B) however, the county may, upon circumstances, waive the forty‑day publication period if it deems the matter urgent, provided the Secretary of State is notified
- C) however, penalties may be less severe than those imposed on individuals convicted under borough regulations

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 386

**Metadata:** The following passage comes from An Outline of English Local Government, a lecture on local government published in 1894 by Edward Jenks, a British jurist and writer.

**Question:** Strictly speaking, there should be sixty courts of county Quarter Sessions in England; for the three ridings of Yorkshire and the three "Parts" of Lincolnshire, the soke or liberty of Peterborough, the Isle of Ely, and the two divisions of East and West Sussex, have each a separate Commission of the Peace and Court of Quarter Sessions, while Suffolk, though having but a single Commission of the Peace, has two Courts of Quarter. Nevertheless, the unity of the traditional county was, until lately, preserved in the special Gaol Sessions which were held every Gaol year in the divided counties, and at which the Justices of all the Divisions attended to exercise jurisdiction in the matter of the maintenance and due regulation of the county gaol and house of correction, as well as the reformatories and industrial schools. But a statute of the year 1877 has transferred the control of prisons and houses of correction to the Secretary of State, and the Local Government Act of 1888 has handed over to the county councils the management of reformatory and industrial schools ; [missing clause describing an inference or effect].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that Gaol Sessions are no longer necessary (ground truth)
- B) so the county councils gained new custodial responsibilities
- C) so the traditional unity is now largely lost and there is perhaps no one capable of overseeing the administration of gaols in the county as a whole

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 387

**Metadata:** The following passage comes from An Outline of English Local Government, a lecture on local government published in 1894 by Edward Jenks, a British jurist and writer.

**Question:** When the committee is satisfied of the correctness of the valuation it approves it, and, until altered or superseded by a new list, it remains in the custody of the overseers as the valuation list, or official basis of rating of the parish. A copy is also sent to the clerk of the peace for the county, [missing clause describing a cause or reason]. But the overseers may, with the consent of their vestry, appeal to Quarter Sessions on the ground of over-valuation of their own parish, or under-valuation of any other parish in the same Union; and any occupier or owner may indirectly appeal to Petty, and ultimately to Quarter Sessions, from a decision of the committee.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for the clerk of the peace also bears responsibility for county finances
- B) for the county rate may also be framed upon it (ground truth)
- C) for the purpose of dealing with matters jurisdiction in which is shared by Quarter Sessions and the County Council
- D) because the clerk must preserve official records for the county

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 388

**Metadata:** The following passage comes from An Outline of English Local Government, a lecture on local government published in 1894 by Edward Jenks, a British jurist and writer.

**Question:** But Township and Hundred and Shire carry us back to the days before Alfred, to the dim beginnings of our story, and it was, in fact, only by an integration or union of these smaller groups that England became a nation at all. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus the whole land gradually became dotted over with chartered boroughs, each relying upon its own special charter.
- B) Thus, some of our existing counties (Sussex and Essex, for example) represent heptarchic kingdoms, kingdoms of the south and east Saxons.
- C) Consequently, central government, when it came, had to reckon with local government as an established fact, and has had to do so ever since. (ground truth)
- D) Hence, the amalgamation of townships, hundreds, and shires forged a unified polity, culminating in England's emergence as a coherent nation for the peoples within.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 389

**Metadata:** The following passage comes from An Outline of English Local Government, a treatise published in 1894 by Edward Jenks, a British jurist.

**Question:** When the committee is satisfied of the correctness of the valuation it approves it, and, until altered or superseded by a new list, it remains in the custody of the overseers as the valuation list, or official basis of rating of the parish. A copy is also sent to the clerk of the peace for the county, [missing clause describing a cause or reason]. But the overseers may, with the consent of their vestry, appeal to Quarter Sessions on the ground of over-valuation of their own parish, or under-valuation of any other parish in the same Union; and any occupier or owner may indirectly appeal to Petty, and ultimately to Quarter Sessions, from a decision of the committee.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for the purpose of dealing with matters jurisdiction in which is shared by Quarter Sessions and the County Council
- B) in order to serve as a record for taxation purposes
- C) for the county rate may also be framed upon it (ground truth)
- D) because the clerk must preserve official records for the county

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 390

**Metadata:** The following passage comes from An Outline of English Local Government, a treatise published in 1894 by Edward Jenks, a British jurist.

**Question:** The original or primary jurisdiction of the Court is chiefly concerned with the trial of those crimes which are deemed too serious for disposal by a court of summary jurisdiction, but not serious enough imperatively to demand trial by a judge of assize.¹ "Indictable offences not specially reserved for the assizes," we may term them. It is a theory of English law that no offence can be tried by Quarter Sessions unless there be express statutory authority for the practice. As a matter of fact, the statutes which confer general jurisdiction upon Quarter Sessions are so wide in their terms that the Justices try all indictable offences ¹ Presumably, an assize judge has a perfect right, if he pleases, to try all criminals awaiting trial by a court of high criminal jurisdiction ; [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, such cases are rare as assize judges typically defer to the regular process
- B) however, the jurisdiction of such judges is traditionally limited to cases specifically assigned by statute, not to all pending prosecutions within the legal framework
- C) but prosecutors and prisoners have no longer the right to insist on a trial beſore a judge of assize of offences triable at Quarter Sessions (ground truth)
- D) but of the jurisdiction of the body or official in question
- E) but the Sessions may voluntarily state a case on a point of law for the opinion of a superior court, or the latter may itself order the court of Quarter Sessions to do so

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 391

**Metadata:** The following passage comes from An Outline of English Local Government, a treatise published in 1894 by Edward Jenks, a British jurist.

**Question:** The rule is that a lease without fine may be made for thirty-one years, or, with or without fine, of land used or to be used for building purposes, for a term not exceeding seventy-five years. But there are savings for cases in which other rules prevailed before 1835. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Accordingly, the present uniform system was started by a comprehensive statute of the year 1846, which swept away about a hundred Courts of Requests.
- B) One result of the restrictions is that municipal property is often let much under its real value. (ground truth)
- C) Hence, a lease for building land cannot exceed seventy‑five years, regardless of fine, except pre‑1835 exceptions.
- D) Therefore, any lease created after 1835 must adhere to these specified durations.
- E) Thus, too, the history of municipal privileges acquired that peculiarly anomalous character which it retained down to the great reform of 1835.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 392

**Metadata:** The following passage comes from Minnesota State Health Laws and Regulations, a register of laws published in 1924 by the State of Minnesota, an American state.

**Question:** In every lodging house there shall be provided for each lodger a separate bed with bedstead, bedding and bed clothes, and no such lodger shall be allowed to sleep elsewhere than in such bed. All beds, bed clothing, mattresses and pillows shall always be kept clean and free from vermin. Clean sheets and clean pillow cases shall be furnished for each bed at least once a week; provided, [missing clause revising an implied expectation].

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) however, the landlord must also ensure that any linens replaced are of sanitary quality and allergen-free
- B) provided, however, that clean linens shall be changed more frequently if deemed necessary
- C) however, that they shall be furnished as often as a new lodger occupies the bed (ground truth)
- D) but before raising quarantine separate nose and throat cultures from each member of the household shall be submitted to one of the laboratories of the State Board of Health
- E) however, that the State Live Stock Sanitary Board or its duly authorized representative may authorize and direct such person by special permit after detailed report made to said beard or representative to otherwise dispose of the said carcass

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 393

**Metadata:** The following passage comes from Minnesota State Health Laws and Regulations, a register of laws published in 1924 by the State of Minnesota, an American state.

**Question:** August 28, 1923.-Since a municipality is under a legal obligation to submit plans to the State Board of Health for its approval and while it has authority to alter or construct such a system after such approval has been obtained, it has no authority to construct or alter such system without such authority. [missing sentence describing an inference or effect]

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) All health officers are therefore directed to co-operate with the proper officers whose duty it is to enforce laws directed against prostitution, and otherwise to use every proper means for the repression of prostitution.
- B) It follows that payments made out of the city treasury under such circumstances are unlawful. (ground truth)
- C) Hence, a municipality must secure State Board approval before any construction or alteration of the system.
- D) Therefore, any construction or alteration of the system without prior approval from the State Board of Health would be deemed unlawful.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 394

**Metadata:** The following passage comes from Minnesota State Health Laws and Regulations, a register of laws published in 1924 by the State of Minnesota, an American state.

**Question:** The prevention of infant blindness and infection of the eyes of the newly born by the designation of a prophylactic to be used in such cases and in such manner as the board may direct, unless specifically objected to by the parents or a parent of such infant; 8. The furnishing of vaccine matter; the assembling, during epidemics of smallpox, with other persons not vaccinated. [missing sentence revising an implied expectation] Any person thus required to be vaccinated may select for said purpose any licensed physician, and no rule shall require the vaccination of any child whose physician shall certify that by reason of his physical condition vaccination would be dangerous; 9.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Provided, however, that the State Live Stock Sanitary Board or its duly authorized representative may authorize and direct such person by special permit after detailed report made to said beard or representative to otherwise dispose of the said carcass.
- B) But no rule of the state board or of any public board or officer shall at any time compel the vaccination of a child, or shall exclude, except during epidemics of smallpox and when approved by the local board of education, a child from the public schools, for the reason that such child has not been vaccinated. (ground truth)
- C) However, parents may choose to exempt their children from vaccinations under specific conditions.
- D) Nevertheless, the board shall ensure that any prophylactic measure prescribed for infant blindness or ocular infection remains grounded in the latest medical consensus, and that parents, upon providing informed consent, may decline such treatment without penalty, thereby safeguarding both public health and individual autonomy while maintaining rigorous surveillance protocols and timely reporting of any adverse events.
- E) Provided, however, that nothing herein shall prohibit the Board of Control, disclosing such facts to such proper persons as may be in the interest of any child maintained in said home with the consent of the mother of said child.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 395

**Metadata:** The following passage comes from Minnesota State Health Laws and Regulations, a register of laws published in 1924 by the State of Minnesota, an American state.

**Question:** Any person who is infected with diphtheria, epidemic influenza, scarlet fever, smallpox, trachoma, tuberculosis, typhoid fever, or other communicable disease, and is residing in a common lodging house, or hotel shall be removed therefrom under the supervision of the local health officer, to a suitable hospital or place of quarantine, if necessary, in order to prevent exposure of other persons to infection. In such cases, [missing clause describing a condition or proviso], the local health officer shall make provisions for the care of such individual in the house where he or she may be found and may cause other persons in the house to be removed therefrom after being submitted to the necessary disinfection.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) unless the infected person has already received adequate treatment and is no longer contagious
- B) provided that no suitable hospital is available
- C) if an infected person cannot be removed without danger to his or her health (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 396

**Metadata:** The following passage comes from The Ethnogeography of the Tewa Indians, an ethnographic study published in 1916 by John Peabody Harrington, an American linguist and ethnologist.

**Question:** 2, p. 456, 1910. west of the Rio Grande, and this may be true of both historic and prehistoric times; but the Santa Clara people probably were not the only Tewa occupants of these cliff-lodges. Puye has given the names to [14:40], [14:45], and [14:47]. [14:47] (1) Santa Clara Pujepopi 'springat [14:46]' (Puje, see [14:46]; Popi 'spring' <po 'water', pi (to issue'). (2) Eng. Nine Mile spring. [missing sentence describing a cause or reason] [14:48] Santa Clara Suwakq 'warm barranca' (suwa 'warmth' 'warm'; kq 'barranca').

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) The purpose of naming these springs and barrancas is to establish a historical record of the Tewa Indians.
- B) It is called thus because the Indians believe it to be nine miles deep.
- C) It is called thus because it is supposed to be 9 miles from Santa Clara Pueblo, or from the Rio Grande. (ground truth)
- D) The rationale for these names lies in the springs’ vital role as water sources for the Santa Clara Tewa community.
- E) Named because of the Colorado River [Unmapped], page 564.
- F) So called because the Navaho live on it.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 397

**Metadata:** The following passage comes from Charles e. Bolton; a Memorial Sketch, a biography published in 1907 by Sarah Knowles Bolton, an American writer and temperance activist.

**Question:** It is pleasant to know that the electric cars will take you to a semi-circle of very beautiful parks, and to all parts of a city of 400,000 people, even to all the neighboring towns, and that 150 steam trains daily enter or leave Cleveland. "It is also encouraging to be told that 336 vessels of a combined tonnage of 336,000 tons are owned and managed in Cleveland. But it does little good to state that 60 per cent. of the Lake Superior iron-ore output enters the Cleveland district, and that the city is situated at the apex of the largest and best field of coal in the world, [missing clause describing a condition or proviso], chiefly because the front door of Cleveland is practically closed to lake transportation and to the wealth of the great Northwest. "The large lake fleets of Rockefeller, Carnegie, M. A. Hanna & Co., and others, sought harbor facilities elsewhere, not because of hostility to Cleveland, but chiefly because of the lack of improved docking capacity at this port.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if we are out of debt
- B) unless these factors are effectively addressed
- C) unless we remember that nearly fivesixths of the 18,500,000 tons of ore passes us by to enrich other cities (ground truth)
- D) provided that the harbor's docking facilities are expanded, and the city could open its front door to lake traffic for commerce

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 398

**Metadata:** The following passage comes from Charles e. Bolton; a Memorial Sketch, a biography published in 1907 by Sarah Knowles Bolton, an American writer and temperance activist.

**Question:** We got our trunk across, and agreed to pay seventy-five dollars for an engine and single car. We all shoveled coal, we wired for the best team to take us from the depot twelve miles to the hall, and wired 'Hold the audience.' [missing sentence revising an implied expectation] No thanks either."

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) The best team, however, was unavailable at the time of our request.
- B) But the wheezy, worn-out engine and our efforts failed us, and we slept that night miles away from Adrian; of course the committee and audience of twelve hundred persons were disgusted; we lost the fee, fifty dollars, and the seventy-five dollar railway ride. (ground truth)
- C) However, the engine, despite its robust design, suffered a critical failure mid‑journey, and the crew, weary from the long haul, could not adhere to the timetable, causing the audience to grow restless and prompting the organizers to seek an immediate replacement for the next.
- D) But I had no thought that there were no more reunions with him this side the other shore."
- E) But it does little good to state that 60 per cent.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 399

**Metadata:** The following passage comes from Charles e. Bolton; a Memorial Sketch, a biography published in 1907 by Sarah Knowles Bolton, an American writer and temperance activist.

**Question:** We passed through Huron on the James River, where the land office of the Territory of Dakota was situated. Thence north, and up the James River to Aberdeen, where we arrived after dark. We were conducted to a big tent, which the Bishop's advance agent had erected to protect materials and provision already forwarded. It was cold and raining hard, [missing clause describing an inference or effect]. In [54] two or three days our party had a half dozen wagons loaded with building material, provisions for man and beast, etc., and we began our journey over the prairie almost due west.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so we felt quite disheartened
- B) so we hurried to the shelter for warmth
- C) so that we have more extended views of men and things, but how extremely limited our field of vision
- D) so that mistakes were rarely made
- E) so I took rooms at a hotel (ground truth)
- F) so I stayed outside as long as I could

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 400

**Metadata:** The following passage comes from Charles e. Bolton; a Memorial Sketch, a biography published in 1907 by Sarah Knowles Bolton, an American writer and temperance activist.

**Question:** Twelve slips, including the river entrance, are exhibited, and each slip, from bulkhead line to pierhead, is sixteen hundred feet in length by two hundred feet in width, and has a capacity of docking a half-dozen of the largest lake freighters. [missing sentence describing an inference or effect] Ore conveyors will carry the ore from the vessels three hundred feet or more.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) Thus, the ore will be efficiently transferred to the conveyors, speeding loading within the yard daily.
- B) Hence, each slip has been designed to accommodate and facilitate the efficient loading of raw materials.
- C) Sufficient land will thus be reclaimed for thirty railroad tracks, as shown on the plan, which should be held as free territory to be leased to or used by all railroads in loading and unloading ores, coal, and other freights.
- D) Thus a total of seventy-two modern vessels at the same time could load or unload their cargoes. (ground truth)
- E) Thus a total of seventy-two modern vessels at different times could not unload cargo.
- F) So tire of simply money-getting at times, and yet it is the key to two-thirds of earthly existence.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 401

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** To the melody of the imprecation, Petrarch, in honor of Laura, added a variant: Benedetto sia l'giorno, e l'mese, e l'anno. Both were unfortunate in their loves but of the two Dante's was the least favored. It had nothing for sustenance. [missing sentence revising an implied expectation] Its continuance was fully justified by the code, though, in the absence of any reciprocity whatever, it was perhaps more vaporous than any that the codifiers had considered.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But either because it was too elusive for history's detention or too fragile for its care, it became corrupted, shoved roughly by stupid hands among the pornai.
- B) Yet, save for that one reproach, it persisted. (ground truth)
- C) This passion was never returned.
- D) Yet the expectation that this lack would render it futile was, in fact, unfounded.
- E) But into that yielding it had already shown that not delight but its contrary enters.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 402

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** The soul then, asleep in God, lost to any connection between itself and the flesh, was indifferent, as the martyr, to whatever happened. The result is as obvious as it was commodious. The body, artificially released from all restraint and absolved from any responsibility, was free to act as it listed. In discussing the doctrine, Fénelon declared that there are souls so inflamed with the love of God and so resigned to His will that, [missing clause describing a condition or proviso], they would accept eternal punishment with thanksgiving. For propagating this insanity Fénelon was accorded the honors of a bishopric which was exile.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) provided that their hearts have wholly surrendered to divine will
- B) if they knew it to be God's will
- C) if any Provençal suggestion of extra-matrimonial possibilities presented itself
- D) if they believed themselves damned (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 403

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** But Molinos, a Spanish fairy, uninvited at the christening, malignantly sent his blessing. The latter, known as quietism, was one of love's aberrations. It did not last for the reason that nothing does. Besides, the life of a century is long enough to outgrow many things, curses as well as blessings. For the time being, [missing clause revising an implied expectation]. The new evangel, originally published at Rome, had a woman, Mme.

Write a clause appropriate for this book that could stand in the position marked by [missing clause revising an implied expectation]:

**Category:** cloze_contrastclause

**Choices:**
- A) for all its fervor, it failed to capture the hearts of those who sought a more active and passionate devotion
- B) however, throughout Europe generally and in certain sections of America, quietism found adherents (ground truth)
- C) but when Italy a century in advance of other lands -was merely corrupt, at that hour, the wraiths of Greece mingling with the ghosts of Rome, made the mistress of the old world sovereign of the new
- D) we had presumed it would endure, yet it proved fleeting

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 404

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** The charge was impatiently repeated. Jesus straightened himself. With the weary comprehension of one to whom hearts are as books, he looked at them. "Whoever is without sin among you, may cast the first stone." The sins of Mary Magdalen were many. He forgave them, [missing clause describing a cause or reason]. His indulgence was real and it was infinite.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a cause or reason]:

**Category:** cloze_causalclause

**Choices:**
- A) for she had loved much (ground truth)
- B) because she had been transformed by his grace
- C) for the love that had been promised
- D) in order to reserve the strength of a people for the presentation of one who, transcending all, was to reign in heaven to the genuflections of the earth

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 405

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** Disregard of a decision entailed not loss of liberty but loss of caste. In the case of a man, entrance was denied him at the tournaments. In the case of a woman, the drawbridges were up. Throughout the land there was no one to receive her. [missing sentence describing an inference or effect] So too was contempt of the jurists.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing an inference or effect]:

**Category:** cloze_effectsentence

**Choices:**
- A) As a result the delinquent was rare. ← (ground truth)
- B) As a consequence, the attitude of woman generally was as elegiac as that of Jephthah's daughter.
- C) Thus, defiance brought social ostracism and exclusion from societal privileges.
- D) The verdict sealed her fate in silence.
- E) The result being that whatever vassal he thought could serve him best, he promptly gratified with the land and the lady, who of the two counted least.¹

The proceeding, if summary, was not necessarily disagreeable.

**Model response:** `A
B
C
D
E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 406

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** At the conclusion of the third book of the Odes, he declared that he had completed a monument which the succession of centuries without number could not destroy. "I shall not die," he added. He was right. Because of that flame of fair faces, lovers turn to him still. [missing sentence describing a cause or reason] Versatile in love and in verse, his inconstancy and his art are nowhere better displayed than in the incomparable Donec gratus eram tibi, which Ponsard rewrote: HORACE.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) Because of
her eyes, more exactly because of her father's,

Ovid was banished among barbarian brutes.
- B) Because of that he made a solitude and peopled it grandiosely with the grandeur of the genius that was his, displaying in whatever he created that of which art had hitherto been unconscious, the sovereignty not of beauty only but of right.
- C) This enduring fame was due to his ability to capture the essence of human emotions with unparalleled eloquence.
- D) Because of his iambics, he has a niche in the hearts of the polite. (ground truth)
- E) His unwavering conviction that art could outlast mortality forged the monument that time could not erase.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 407

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** From the latter Assiduousness is reached and, finally. Great Services. This place, probably because there are so few that get there. is the smallest of all. But adjoining it is Obedience and contiguous is Constancy. That is the most direct route to Tenderness-on-Gratitude. Yet, as there are no routes in which one may not lose one's way, [missing clause describing an inference or effect]. For if, in going from Great Wit, you took to the right, you would reach Negligence, keeping on you would get to Inequality, from there you would pass to Lukewarm and Forgetfulness, and presently you would be on the lake of Indifference.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so, if, after leaving New Friendship, you went a little to the right or a little to the left, you would get lost also (ground truth)
- B) so has infamy its bounds
- C) you would be condemned to wander the endless maze of error, where each step deepens the shadows of folly
- D) it is easy to stray from one's path if you are not alert

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 408

**Metadata:** The following passage comes from Historia Amoris; a History of Love, Ancient and Modern, a cultural history published in 1906 by Edgar Saltus, an American biographer, essayist, historian, novelist, poet.

**Question:** To have been able to display it, the general assumption was that either Pheidias had ascended above, or else that Zeus had descended to him. The revelation of Aphrodite Urania which he effected for her temple near the Cerameicus must have been equally august, the celestial in its supremest expression. Thereafter the decadence of the goddess began. Previously she had ruled through her perfection. Subsequently, [missing clause acknowledging a countervailing fact].

Write a clause appropriate for this book that could stand in the position marked by [missing clause acknowledging a countervailing fact]:

**Category:** cloze_concessiveclause

**Choices:**
- A) yet the mortal realm, stubbornly, clung to her earthly liaisons, refusing to surrender to the celestial
- B) though manners persisted morals did not
- C) though the perfection persisted, the stamp of divinity ceased (ground truth)
- D) yet it is also true that art's evolution led to different interpretations of her essence

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 409

**Metadata:** The following paragraph comes from A Brief History of Europe From 1789-1815, a history written by Lucius Hudson Holt and published in 1919.

**Question:** [missing introductory sentence] Though 'parties' in the modern sense of the term with their complex machinery and their platform of policies were unknown, men of like opinions naturally tended to coalesce into well-defined groups. These groups centered about "Clubs," successors in many cases to the informal 'salons' in which the bourgeoisie under the old régime had met for social pleasure and for discussion of economic and political conditions. As these new "Clubs" became important factors in directing the policies of their members in the Legislative Assembly, the most important deserve mention here.
Write an introductory sentence that fits the style of this paragraph, and provides a suitable overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Since the convocation of the Estates General in 1789, political life in France had rapidly developed. ← (ground truth)
- B) The political landscape of revolutionary France saw the formation of influential groups.
- C) Clubs became central to political life in France, and were largely responsible for the Revolution.
- D) France’s political landscape in the nineteenth century was dominated by the clergy and influential bourgeois clubs.
- E) Around this time, the Estates General were summoned into session by decree.
- F) The formation of political groups in France during this period.

**Model response:** `A
The following paragraph comes from A Brief`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 410

**Metadata:** The following paragraph comes from A Brief History of Europe From 1789-1815, a history written by Lucius Hudson Holt and published in 1919.

**Question:** [missing introductory sentence] He therefore swept away the former courts and substituted an admirable uniform judicial hierarchy, ranging from numerous local courts in small areas to the High Court sitting in Vienna, with provisions for appeal from one rank of court to another. At the same time he decreed a radical revision of the penal code along enlightened lines, abolishing torture and the methods of the inquisition and restricting materially the list of crimes punishable by death. In no field was the wisdom of the monarch more clearly displayed than in these reforms, but he met the utmost difficulty in finding the men to carry through details of the new system. Its partial failure was due, not to faults in the Emperor's plan, but to the incapacity and lack of sympathy of his agents.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Frederick William II was a significant figure in Prussias reforms and progress.
- B) Joseph II initiated sweeping judicial reforms across the Austrian Empire.
- C) The sovereign endeavored to replace the old and outworn judicial system with one more suited to contemporary conditions. (ground truth)
- D) Such conditions inspired among the people a thorough distrust of, and hatred for, the judicial system of the country.
- E) Again, by governmental decrees the governments endeavored to regulate economic conditions.
- F) The monarch radically overhauled Prussia’s judicial system, instituting a uniform hierarchy from local courts to Vienna’s High Court.
- G) Frederick the Great had an obsessive concern with symmetry and regularity in government.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.1667


## Question 411

**Metadata:** The following paragraph comes from The Lighting Art, its Practice and Possibilities, a practical guide written by Matthew Luckiesh and published in 1917.

**Question:** [missing introductory sentence] Statistics reveal the fact that the percentage of industrial accidents are more numerous during the winter months when daylight is often inadequate. Artificial lighting is an obvious remedy. Recently protective lighting has become recognized as a desirable feature of industrial lighting and as a consequence various methods of exterior lighting have been devised as an aid to watchmen. Flood-lighting projectors are playing an important part in such systems.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Incidentally one of the most modern developments in industrial lighting has been the recent adoption of the use of artificial daylight in many plants. ←
- B) Artificial illumination is increasingly crucial in various settings due to its impact on safety and visibility.
- C) It has been shown that inadequate illumination is directly responsible for many industrial accidents and that proper artificial lighting is a preventative measure. (ground truth)
- D) Inadequate daylight during winter increases industrial accidents, highlighting the need for protective artificial lighting, which also enhances museum displays with artificial daylight for visitors.
- E) Flood-lighting systems are the most advanced form of artificial illumination currently available in North America.
- F) Industrial lighting is crucial for safety and productivity especially during winter months when daylight is insufficient.
- G) However, we appear to be content with an illumination indoors of a few foot-candles of artificial light.

**Model response:** `A) A
B) B
C`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.1667


## Question 412

**Metadata:** The following paragraph comes from School Civics, an educational textbook written by Frank David Boynton and published in 1904.

**Question:** [missing introductory sentence] All ordinances which have been approved by a majority of the quorum present in council must be presented to the mayor, and if he approve, he signs the same; if he does not approve, he must veto and return the ordinance with his objection to the council within ten days, or at the next regular session. If he does not return the ordinance within ten days, it is a law, regardless of his approval or disapproval, unless council by final adjournment prevent its return, in which case it shall not be a law. After a vetoed law is returned council may, after the expiration of ten days, reconsider the same and pass it over the mayor's veto by a two-thirds vote of the entire membership of council.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The mayor possesses the veto power over all ordinances passed by the city council. ← (ground truth)
- B) The acts of council are called ordinances, and the style of these ordinances must be "Be it Ordained by the Council of the City of, State of Ohio."
- C) The process required to pass ordinances through city council, and obtain approval from the mayor, may perhaps be excessively involved.
- D) The process of enacting city ordinances involves several steps.
- E) The president-general holds veto power over council acts, subject to return and council override.
- F) The duties of a village mayor are many.
- G) He is the chief conservator of the peace within the village, enforcing all ordinances of the village council and the laws of the state within the limits of the municipality.

**Model response:** `A
The following paragraph comes from School Civ`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 413

**Metadata:** The following paragraph comes from School Civics, an educational textbook written by Frank David Boynton and published in 1904.

**Question:** [missing introductory sentence] The process of amendment provided by the instrument, while not so difficult as to be impracticable, as was the case with the articles of confederation, has nevertheless proved too cumbersome to be resorted to unadvisedly. As a result the constitution has been but little changed by amendment. Of the fifteen amendments that have been passed, the first ten, often called the bill of rights, were passed at one time and might almost be counted as one; while the last three also, relating as they do to the same subject and growing out of the civil war, are really a unit; so that it is perhaps not inaccurate to say that the constitution has really been amended but four times. It has undergone development, but it has been principally through the process of judicial interpretation and through custom. Mr. Bryce has said of it, "The constitution as a whole has stood and stands unshaken. The scales of power have continued to hang fairly even. The President has not corrupted and enslaved Congress; Congress has not paralyzed and cowed the President. . . . Neither the legislature nor the executive has for a moment threatened the liberties of the people. The States have not broken up the Union and the Union has not absorbed the States.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Students may ask whether the Constitution is immutable or can be rewritten. ←
- B) How long after its adoption before any amendments were made to the constitution?
- C) The Constitution has evolved primarily through amendments and judicial interpretation, yet its amendment process remains cumbersome and rarely invoked.
- D) The U.S. Constitution's amendment process is complex and rarely used to make changes.
- E) The U.S. Constitution's amendment process is rarely used due to its complexity.
- F) Contrary to the expectation of many at the time of its adoption, the constitution has proved itself extremely stable. (ground truth)

**Model response:** `A
The following paragraph comes from School Civ`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 414

**Metadata:** The following paragraph comes from Composition, Rhetoric, Literature: a Four Year's Course for Secondary Schools, a textbook written by Martha Hale Shackford and published in 1913.

**Question:** [missing introductory sentence] It comes from the pen of one whose writings along this line, especially his history of Christian and ecclesiastical Rome, have already made him well known. In the main Mr. Tuker keeps to a narration of specific events, leaving a description of the beauties of the English countrysides and the architectural glories of the old towers of the collegiate buildings to be expressed in line and color by W. Matheson, the artist, whose many sketches have excellently fulfilled the trust committed to him. Those who have visited Cambridge will find delight in recalling its characteristic scenes and buildings here admirably recorded.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Cambridge offers a unique blend of historical beauty and academic prestige. ←
- B) The following three volumes by this distinguished writer cover Roman ecclesiastical history, English elegy, and the picturesque scenes of Cambridge.
- C) The book on Cambridge is largely an account of the founding and history, centuries long, of that great English University. (ground truth)
- D) In the way of college courts and quiet scholastic porticoes, of gray-walled gardens and ivied nooks of study, in all the pictorial accidents of a great English university, Cambridge is delightfully and inexhaustibly rich.
- E) Cambridge University is one of the most eminent institutions of higher education in the United Kingdom, and a history of its vicissitudes will certainly be welcomed by readers.
- F) Mr. Tuker's book on Cambridge offers readers a vivid journey through history.

**Model response:** `A
The following paragraph comes from Composition,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 415

**Metadata:** The following paragraph comes from Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking written by Mary E.; Fisher, Katharine Rolston Williams and published in 1901.

**Question:** [missing introductory sentence] There seem to be properties in the latter that cannot be produced by mixing one lot of milk with cream from another lot, and sugar prepared from a third. This modified milk is, nevertheless, the best food for bottle feeding. It is prepared according to exact recipes, or formulas, different formulas being used for babies of different ages. The following table¹ gives the three most commonly used. The first is intended for a baby from three to seven days old, the second for one between one and three months old, the third for one six to nine months old.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Modified milk, often called formula, is now used as an alternative food source for babies who are not breastfed. ←
- B) By diluting cow's milk with water to reduce the proportion of proteids, and adding cream and milk sugar, a compound similar to the baby's natural food is produced. (ground truth)
- C) This paragraph discusses the formulated, modified milk mixtures that serve as bottle-feeding nourishment for infants, detailing distinct recipes for various age groups and addressing nutritional value versus cost.
- D) Vegetables cooked in water lose a large proportion of their foodstuffs.
- E) The composition and preparation of baby food requires careful consideration.
- F) Note the proportion of butter to sugar, and think why this is done.
- G) One must carefully distinguish the nutritional properties of commercial cow's milk from those of human breast milk.

**Model response:** `A) A
B) B
C`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.1667


## Question 416

**Metadata:** The following paragraph comes from Journal of Nervous and Mental Disease, a medical journal published in 1916.

**Question:** [missing introductory sentence] A typical example of an unconscious mental process, illustrating all of these, would be the wish of a little girl that her mother might die so that she could marry her father. The six attributes in question, together with others not here mentioned, make up a consistent and clearly-defined conception of the unconscious which is formulated on the basis of experience that may at any time be tested.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) In this discussion, the author presents the most essential claim regarding the unconscious, focusing on its origins and contents, and outlines six key attributes that together form a coherent, empirically testable concept of the unconscious today. ←
- B) Oedipal impulses have four chief characteristics: they are sexual impulses, experienced unconsciously, in childhood,, and involving the child's parents.
- C) Briefly summarized, in a single statement: according to psychoanalysis, the unconscious is a region of the mind, the content of which is characterized by the attributes of being repressed, conative, instinctive, infantile, unreasoning, and predominantly sexual. (ground truth)
- D) The author emphasizes key points about the formation and nature of unconscious thoughts.
- E) The following attributes are essential to understanding the nature of unconscious mental processes as observed and analyzed in psychoanalytic theory.
- F) The mode of action of the treatment, in a word, is that the overcoming, by means of psychoanalysis, of the resistances that are interposed against the making conscious of the repressed unconscious material, gives the patient a much greater control over this pathogenic material by establishing a free flow of feeling from the deeper to the more superficial layers of the mind, so that the energy investing the repressed tendencies can be diverted from the production of symptoms into useful, social channels.
- G) The statement of most fundamental importance, and the one on which the writer lays the greatest stress, concerns both the origin and the content of the unconscious.

**Model response:** `A
The following paragraph comes from Journal of`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.1667


## Question 417

**Metadata:** The following paragraph comes from The Nature-Study Review, a pedagogical guide published in 1920.

**Question:** [missing introductory sentence] It differs widely from many zoologies in that great stress is laid upon the vital reactions and comparatively little space devoted to the purely systematic. It is a discussion of characteristic types of developing life rather than a record of conditions in existence at a stated period. The author keeps the mutability of life constantly before the reader. It is a human document, a digest of man's interpretation of the animal world and as such, it occasionally turns from the purely zoological to sympathetic and inspiring accounts of the life work of such master builders as Mendel, Charles Darwin, Linnaeus, Fabre, Pasteur, Louis Agassiz and Baird and here and there one may find evidences of the author's personal contributions to a better explanation of the mysteries of life.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The book discussed in this passage focuses on the dynamic nature of animal life and the human understanding of it, rather than merely classifying species. ←
- B) This volume is a comprehensive, philosophical resume of life reaching back to the lowly protozoa and from this basis tracing various lines of development and discussing the more important factors which have played a part in the modification of life. (ground truth)
- C) This book is a comprehensive manual on the subject of community center development, especially adapted to the needs of teachers in rural communities where conditions naturally indicate the teacher as the person, generally the only person, fitted to take the initiative in community activities.
- D) This volume is one of the best treatments of the role that DNA and other nucleic acids have played in the multifarious evolution of animal life.
- E) The focus of our school gardening program should be on engaging both students and communities in activities that foster a deeper understanding of life's processes while promoting mutual growth and welfare.
- F) It is considered one of the best factors in the program of supervised gardening for it not only retains the interest of the children during the year but gives a comprehensive idea to the public which furnishes the money, of the work the schools are accomplishing.
- G) Through supervised gardening, this educational guide maintains children’s interest all year, secures public funding, and presents a lively study of living beings, and intertwining scientific analysis with uplifting stories of naturalists and the author's personal insights into life's mysteries and wonder.

**Model response:** `A) A
B) B
C`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.1667


## Question 418

**Metadata:** The following paragraph comes from The Development of Doctrine in the Epistles, a work of Scriptural interpretation written by Charles Richmond Henderson. It was first published in 1896.

**Question:** [missing introductory sentence] It is proved by signs, miracles, and spiritual power. "God also bearing witness with them, both by signs and wonders, and by manifold powers, and by gifts of the Holy Spirit, according to his own will” (Heb. 2 : 4). The discriminating, judging, convicting power of a sacred letter is evidence of its divine origin and authority. "The word of God is living and active, and sharper than any two-edged sword, and piercing even to the dividing of soul and spirit, of both joints and marrow, and quick to discern the thoughts and intents of the heart" (Heb. 4 : 12; cf. John 6:63; Rev. 1 : 16; Eph. 6 : 17).
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The Epistles became a part of the Sacred Scriptures. ←
- B) The New Testament offers several proofs of its divine authority.
- C) The divine authority of sacred letters is proven by signs, miracles, and their convicting spiritual power.
- D) The authority of the Sacred Scriptures, inclusive of the epistles of apostles, is strongly asserted. (ground truth)
- E) The divine origin and authority of the Scriptures can be demonstrated through various means.
- F) These are the "Scriptures" which Paul uses as authority among his fellow Hebrews.
- G) Scripture, we know, is the inspired Word of God.

**Model response:** `A) The Epistles became a part of`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.1667


## Question 419

**Metadata:** The following paragraph comes from Radio up to the Minute, a practical guide to radio written by John R. Irwin and published in 1924.

**Question:** [missing introductory sentence] It has a primary and a secondary, the same as the loose-coupler described above, and in theory its operation is the same as this type of instrument. The coupling between the coils is varied by turning the secondary coil in a circular motion. This coil is mounted on a shaft. The variocoupler is usually employed with the vacuum tube detector. It is not so efficient as the loose-coupler type of receiving transformer when used with a crystal detector, because of the method employed in mounting the secondary. The variocoupler takes its name from the variometer which works on a similar principle, but has instead of two separate inductance coils, a single circuit which is split and mechanically constructed into two coils.

Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The jigger type of oscillation transformer has several key characteristics. ←
- B) We turn now to another type of inductively coupled receiving transformer.
- C) Loose Coupler is the name applied to an inductively coupled radio receiving transformer.
- D) The receiving transformer, a variocoupler or honeycomb coil arrangement, can be tuned by rotating its secondary.
- E) The variocoupler is a form of inductively coupled receiving transformer compactly made into one unit. (ground truth)
- F) The variocoupler is another type of distribution transformer with some distinct features.

**Model response:** `A) The jigger type of oscillation transformer`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2000


## Question 420

**Metadata:** The following paragraph comes from Radio up to the Minute, a practical guide to radio written by John R. Irwin and published in 1924.

**Question:** [missing introductory sentence] Damped waves are generated by the discharge of a condenser as described in a previous paragraph. Undamped waves are generated by an arc generator as previously described, by a high frequency alternator connected directly to
the aerial and ground or by vacuum tube oscillators. Damped waves are produced by what are called "spark sets" and are used mostly on shipboard or at low power coast stations. They are the source of a great amount of interference due to the broadness of the damped waves which makes it impossible to tune it out. In other words, a damped wave can be heard over a wide range on the receiving set compared to the undamped wave.
Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) Damped waves generate interference, undamped waves do not.
- B) Damped radio waves have largely been superseded by continuous wave (CW) transmission.
- C) Radio waves are created or generated in several ways. (ground truth)
- D) The efficiency of radio waves is affected by damping.
- E) Such a system must do several things and these are listed below: 

First, Create radio waves.
- F) Radio waves, too, are "generated" and unless the
source of power that makes the waves is continuous, without the slightest interruption, they are also damped waves.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 421

**Metadata:** The following paragraph comes from Foreign Exchange : the Financing Mechanism of International Commerce, a book written by Edgar S. Furniss and published in 1922.

**Question:** [missing introductory sentence] It is natural for the seller to desire a confirmed, irrevocable credit. Its possession enables him to go about the business of filling the importer's order with confidence, even if this involves incurring costs and forming obligations to purchase goods or raw materials in advance of the importer's payment; for the confirmation of the credit by the American bank will assure the exporter a market for his bills, as long as they are drawn in proper order, even if the foreign buyer should suffer business failure or repudiate his contracts. In other words, the letter of confirmation reduces the exporter's risk to that of failure by the American bank which has undertaken to honor his draft. On the other hand, it is equally natural for the importer to attempt to reduce his financing costs to the minimum. To obtain a confirmed, irrevocable credit will not only add to the commission which he must pay, but will require the pledge of collateral and the fulfillment of other conditions laid down by his banker. A copy of the form used by an American bank to confirm an irrevocable credit is given on page 243; by the substitution of the word "revocable" for "irrevocable," this same letter serves to confirm a credit which may be revoked at the option of importer, or either of the banks. Examination of this letter shows that it very closely resembles a letter of credit issued by the bank upon itself.

Write an introductory sentence that fits the style of this paragraph, and provides an overview of its subject. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The advantages and disadvantages of confirmed irrevocable credits are significant considerations for both sellers and buyers in global trade. ←
- B) The final arrangement regarding these matters of revocation and confirmation of the credit will reflect the bargaining power of buyer and seller in international trade. (ground truth)
- C) Buyer and seller in foreign trade must agree upon a method of disposing of certain costs involved in every transaction in international commerce.
- D) This simple arrangement, though not unknown, is relatively rare in international trade; it is not considered good banking practice, since it multiplies the banker's risk and subjects him to the hazards of the client's business.
- E) Exporters depend on confirmed, irrevocable letters of credit to secure payment, manage risk, and ensure smooth international transactions despite potential buyer defaults and reliability.
- F) The complexities involved in global trade necessitate unique financial instruments to facilitate transactions between buyers and sellers.

**Model response:** `A
B
C
D
E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2000


## Question 422

**Metadata:** The following question is based on The Lake County Star, an American newspaper published in Michigan in 1875.

**Question:** Provide a conclusion of about twelve words for this article: "The Wool CLIP FOR 1875.-The Western Rural says that it seems to be generally admitted that the wool clips of California, Oregon and Texas this season will be larger than those of last year and that the average quality, except perhaps of the California wools is also improved. These wools come into market before those of the rest of the country. In the more Northern States, shearing will be somewhat later than usual on account of the backward spring; hence"

**Category:** handcrafted

**Choices:**
- A) overall wool production for the year is likely to be curtailed. ←
- B) farm employment in Wisconsin and Michigan may be lower than the median for this time of year.
- C) the clip will not go into market quite so early as usual. (ground truth)
- D) farmers will need to be watchful for diseases caused by excessively thick coats.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 423

**Metadata:** The following question is based on The Lake County Star, an American newspaper published in Michigan in 1875.

**Question:** Fill in the masked part of this newspaper story. "Two bank robbers who attempted to plunder the Bank of Barre, Vermont, took the train at Rumney, [missing clause expressing a countervailing fact] The train was stopped and run back. After an extended search the man was found about half mile from where he jumped off. He was badly cut and bruised, and had concealed himself in the rushes."

**Category:** contrastclause

**Choices:**
- A) but seeing detectives onboard, one of them became frightened and jumped off. ← (ground truth)
- B) but one of the gang members leapt into a river as the train was going over a trestle.
- C) but one of them jumped from the car before the train had gone many kilometers.
- D) but one fell from the dining car.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 424

**Metadata:** The following question is based on History of Education in India Under the Rule of the East India Company, a history published in 1922 by Baman Das Basu, an Indian physician, nationalist, and historian. The best answer will approximate Basu's likely response.

**Question:** How central was Thomas Babington Macaulay to the emergence of Western education in India?

**Category:** parallax

**Choices:**
- A) Little was known about this question at the time. ←
- B) It should also not be lost sight of that the Indians themselves were the pioneers in introducing Western education in this country. The Hindu College of Calcutta was established long before Macaulay penned his celebrated minute or Wood sent out his Educational Despatch to India. (ground truth)
- C) Historians point out that English-medium schools, textbooks, and reform movements were often initiated, funded, and enthusiastically supported by Indian elites and voluntary societies, indicating that the shift toward Western education was partly driven from within Indian society rather than imposed solely by British policy.
- D) Thomas Babington Macaulay’s 1835 "Minute on Indian Education" fundamentally disrupted India by replacing traditional education with an English-medium system designed to create a class of "Indian in blood and colour, but English in taste". It marginalized native languages, caused the collapse of indigenous schooling, and instilled a "colonial mindset," fostering cultural alienation.
- E) It was Macaulay's advocacy of English education that turned the scale against the Orientalists. His famous Minute was immediately followed by a Resolution of the Governor-General, which plainly declared for English as against Oriental education.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 425

**Metadata:** The best answer to the following question is drawn from History of Education in India Under the Rule of the East India Company, a history published in 1922 by Baman Das Basu, an Indian physician, nationalist, and historian. Your answer should be consistent with Basu's likely perspective.

**Question:** Were English authorities whole-heartedly interested in Indian education in the 1840s?

**Category:** parallax

**Choices:**
- A) Since 1839, education in India has proceeded upon the recognition of the value of English instruction, of the duty of the State to spread Western knowledge among its subjects, and of the valuable aid which missionary and philanthropic bodies can render in the task. ←
- B) The Indian authorities, it has been said, were afraid of educating the people of India. Even so late as 1853, some of the Anglo-Indian witnesses examined before the Select Committees on Indian affairs were not in favour of educating the natives of India, for they thought that would make them disloyal. (ground truth)
- C) Little was known about this question in 1922.
- D) In the 1840s British authorities in India were divided and often hesitant about education, with limited budgets and competing priorities. Even after Macaulay's Minute on Indian Education, many officials did not favor spending public funds on schooling, and actual educational expansion depended heavily on missionary activity and Indian initiatives rather than sustained government enthusiasm.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 426

**Metadata:** The best answer to the following question is drawn from Letters, a volume of personal letters published in 1921 by Yuen Ren Chao, a Chinese-American linguist.

**Question:** Provide a sentence that begins with "When" and ends with a period.

**Category:** constrained_generation

**Choices:**
- A) When the fog lifted, the harbor slowly revealed the masts of ships waiting beyond the breakwater. ←
- B) When a husband or wife has been guilty of adultery, the party offended against has generally the right to a divorce from the bonds of matrimony, on the ground that the other party has failed to adhere to the obligations entered into on the marriage.
- C) In June 1916 I wrote in the Chinese Students Monthly fourteen reasons for alphabetizing Chinese and sixteen reasons against it, which objections I answered one by one.
- D) When the valves in this connection are open, the flow into the calorimeter is induced by vapor-pressure difference caused by heating the reservoir above the temperature of the calorimeter.
- E) When one can produce accents to pass as a native in eight different cities, one has more reason to feel at home than some others who have always been at one local home. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 427

**Metadata:** The following question asks for information drawn from The Land of the Czar, a history and ethnology by O. W. Wahl, published in 1875. Your answer should reflect the state of world knowledge at that time.

**Question:** Which of the following events happened first? The disastrous retreat of the French from Moscow, the annexation of the Imerethians by Russia, the conquest of the Khanate of Kazi-Koumoukh by Mahatov, or the first ascent of the Elbruz?

**Category:** inference

**Choices:**
- A) first ascent of the Elbruz ←
- B) disastrous retreat of the French from Moscow
- C) annexation of the Imerethians by Russia (ground truth)
- D) conquest of the Khanate of Kazi-Koumoukh by Mahatov
- E) I have no information about those events.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 428

**Metadata:** The following question is drawn from Aether and Matter, a prize essay published in 1900 by Joseph Larmor, an Irish mathematician.

**Question:** The Larmor writes, "The only first-order difference that could arise, according to whether or not the moving body pushed the aether in front of it, would be a difference of wave-length. No such effect would be produced by the source moving the aether in this way, if the receiver is far enough off to be out of the range of the disturbance: but if the velocity v' of approach of the receiver involves a velocity kv' of the aether around it, the wave-length of the radiation relative to the receiver will be altered in the ratio ..." What ratio would he most likely infer?

**Category:** handcrafted

**Choices:**
- A) 1-kv'/c ← (ground truth)
- B) v'/mc2
- C) k/v'
- D) λ′/λ
- E) 1−(1−k)v′/c

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 429

**Metadata:** The following question is drawn from Aether and Matter, a prize essay published in 1900 by Joseph Larmor, an Irish mathematician.

**Question:** The author identifies a fundamental question: "How it is that portions of matter can interact on each other which seem to have no means of connexion between them?" Given the historical context, how might the author plausibly answer?

**Category:** handcrafted

**Choices:**
- A) The error lies in supposing that bodies act across empty space at all, or that there must be some mechanical medium between them. The proper course is to recognize that what we call a force is only a way of describing relations in the structure of space and time themselves. ←
- B) The ultimate reality is transferred from sensible matter to a uniform medium which is a plenum filling all space: all events occur and are propagated in this plenum, the ultimate elements of matter consisting of permanently existing vortices or other singularities of motion and strain located in the primordial medium. (ground truth)
- C) I do not conceive that matter acts where it is not; rather, I suppose that whatever produces these effects must be present and operative in the spaces between bodies, though its manner of operation remains hidden. Thus we proceed from phenomena to laws, and from laws, in due time, to causes.
- D) We do not imagine matter as little solid bodies exerting pulls across empty space, nor do we picture a material aether transmitting pushes. What we call matter and force are both aspects of quantum fields that exist everywhere.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 430

**Metadata:** The best answer to the following question is drawn from Women's Work, a social treatise published in 1894 by A. Amy Bulley, a British writer.

**Question:** The author writes "People have, not unnaturally, been alarmed by [idea] and, shrinking from the assertion of such principles, have adopted an attitude of hostility to the just claims of women for consideration in respect of their labour and wages, their education, the protection of their earnings and property, the removal of such trade and professional restrictions as are of an artificial character, and the opening out to them of wider means of obtaining a livelihood." What might be the idea that this author believes people have naturally found alarming?

**Category:** handcrafted

**Choices:**
- A) the denigration of an institution so fundamental as marriage, ←
- B) the socialistic principles of the "shrieking sisterhood,"
- C) what seems to many the absurd suggestion of equality between the sexes, (ground truth)
- D) the celebration of promiscuity, now denominated "sexual freedom,"

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 431

**Metadata:** The best answer to the following question is drawn from Women's Work, a social treatise published in 1894 by A. Amy Bulley, a British writer.

**Question:** "A woman, however, who has a fair variety of subjects at command, and can combine purely literary work with the day-to-day business of a journalist, may make a very reasonable income from her profession-say [missing income]." What estimate of income would make sense there?

**Category:** handcrafted

**Choices:**
- A) £1000 a year. ←
- B) insufficient information
- C) £400 a year. (ground truth)
- D) twenty guineas a year.
- E) $500 a year.
- F) £2000 a year.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2000


## Question 432

**Metadata:** In answering the following question, envision the perspective of Women's Work, a social study published in Britain in 1894 by A. Amy Bulley and Margaret Whitley, with an introduction by Lady Emilia Dilke. The best answer will reflect the perspective and expository style of that text.

**Question:** Is it beneficial or harmful for women to work outside the home?

**Category:** parallax

**Choices:**
- A) Against the advantages must be set the drawbacks: the comparative break-up of home life and the habitual neglect of children. The problem is a grave one, and opinions are conflicting, but most people agree that something should be done at any rate to arrest the terrible infant mortality, which is to be found in all the centres which give widespread employment for married women. ← (ground truth)
- B) The crowds of women in the streets, walking rapidly past, pushing and elbowing everyone who stands in the way, all intent on business or pleasure, are a sight not likely to be soon forgotten. For me it is a sight more striking than attractive. After all, a woman's place is at home rather than in the street.
- C) Woman, endowed by nature with a gentler temper and a finer moral sensibility than man, fulfills her highest office within the quiet precincts of the home, where her influence refines the character of husband and child alike. To summon her into the rough competitions of public labour, would be to disturb that delicate domestic economy upon which the virtue and tranquillity of the nation depend.
- D) The concept of sex-seclusion is, with us, rapidly passing away. Our millions of wage-earning women are leading us, by the irresistible force of accomplished fact, to recognise the feminine as part of the world around us, not as a purely domestic element. An American man feels no jar to his sexuo-domestic sentiments in meeting a woman walking freely in the street or working in the shops.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 433

**Metadata:** In answering the following question, envision the perspective of The Voice of Freedom, a selection of essays from the Irish nationalist periodical "Irish Freedom" published in 1913. Your answer should be consistent with theat perspective and period.

**Question:** What can be said about the character of James Stephens?

**Category:** parallax

**Choices:**
- A) James Stephens is an American actor best known for his starring role as James T. Hart in the television series The Paper Chase. ←
- B) Equanimity and courage and steadfast hope were characteristic of Stephens all his life through. Whoever doubted Ireland's fitness to free herself that did not he. (ground truth)
- C) James Stephens, who had been implicated in the Phoenix affair, was very despotic—a true revolutionary leader.
- D) An omnivorous reader, Stephens, according to Ryan, was a silent and aloof student with a thirst for knowledge, a characteristic throughout his life.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 434

**Metadata:** In answering the following question, envision the perspective of The Voice of Freedom, a selection of essays from the Irish nationalist periodical "Irish Freedom" published in 1913. Your answer should be consistent with that perspective and period.

**Question:** What is the role of Home Rule in Irish politics?

**Category:** parallax

**Choices:**
- A) These reforms did not, however, put an end to Irish agitation. The Home Rule party, which demanded the restoration of a separate Irish Parliament, showed increased activity, and the general election of 1874 gave it a strong representation at Westminster, where one section of the party developed into the “Obstructionists.” ←
- B) From the late 19th century, Irish leaders of the Home Rule League, the predecessor of the Irish Parliamentary Party, under Isaac Butt, William Shaw, and Charles Stewart Parnell demanded a form of home rule, with the creation of an Irish parliament within the United Kingdom of Great Britain and Ireland. This demand led to the eventual introduction of four Home Rule Bills, of which two were passed.
- C) Little is known about the role of home rule.
- D) If we are to have National Freedom we must at least be prepared to fight. Home Rule will give us only the freedom of the convict in the prison fields, always within range of the warder's gun. The Home Rule Parliament, should it ever be established, will not be permitted to use freely the powers given to it, much less to extend them, unless it is backed by an armed and resolute nation. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 435

**Metadata:** The best answer to the following question is drawn from The Indian eye on English Life, or, Rambles of a Pilgrim Reformer, a travelogue published in 1891 in Bombay by Behramji M. Malabari, an Indian poet and social reformer. Provide an answer consistent with the likely perspective and expository style of that text.

**Question:** Describe a traveller's impressions of London.

**Category:** textbook

**Choices:**
- A) Every man and woman — one might say every animal, and even some of the inanimate objects — seem to be full of life. The crowds of women in the streets, walking rapidly past, pushing and elbowing everyone who stands in the way, all intent on business or pleasure, are a sight not likely to be soon forgotten. I wonder how people can stand the noise and bustle. ← (ground truth)
- B) What a gorgeous scene is now before us! The evening sun is painting the waters with glancing flames; the cross upon the summit of that mighty dome of St. Paul's shines like another sun; churches, warehouses, steam-chimneys, shot-towers, wharfs, bridges - the noblest and the humblest things all are picturesque.
- C) The absence of style, or rather of the intention of style, is certainly the most general characteristic of the face of London. On the banks of the Thames it is a tremendous chapter of accidents — the London-lover has to confess to the existence of miles upon miles of the dreariest, stodgiest commonness. Thousands of acres are covered by low black houses of the cheapest construction, without ornament, without grace, without character or even identity.
- D) Contrary to thirty years of media portrayals, London was much more multicultural than I expected. I saw very few people who met the British archetype commonly seen in media portrayals of the country and while London is only a small part of England, it definitely felt like a much more culturally diverse city than what I was previously told.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 436

**Metadata:** The best answer to the following question is drawn from The Indian eye on English Life, or, Rambles of a Pilgrim Reformer, a travelogue published in 1891 in Bombay by Behramji M. Malabari, an Indian poet and social reformer. Provide an answer consistent with the likely perspective and expository style of that text.

**Question:** Is a woman's place at home, or in public?

**Category:** parallax

**Choices:**
- A) The crowds of women in the streets, walking rapidly past, pushing and elbowing everyone who stands in the way, all intent on business or pleasure, are a sight not likely to be soon forgotten. For me it is a sight more striking than attractive. After all, a woman's place is at home rather than in the street. ← (ground truth)
- B) Wherever a true wife comes, this home is always round her. The stars only may be over her head; the glowworm in the night-cold grass may be the only fire at her foot; but home is yet wherever she is.
- C) Yes, undoubtedly, much labour at present performed by our women is unfit, if there is any fitness in our old and cherished ideal of home and of the place of the woman in the family; but, if we once enter on the line of restricting their employment by artificial barriers, it seems to me difficult to foresee the number and variety of the complications which would ensue.
- D) The concept of sex-seclusion is, with us, rapidly passing away. Our millions of wage-earning women are leading us, by the irresistible force of accomplished fact, to recognise the feminine as part of the world around us, not as a purely domestic element.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 437

**Metadata:** In answering the following question, envision the perspective of  Shanghai; a Handbook for Travellers and Residents to the Chief Objects of Interest in and Around the Foreign Settlements and Native City, a travel guide published in 1920 by Charles Ewart Darwent, a British clergyman, author, and photographer. Your answer should fit the state of the world at the time that book was published, and match its likely style of exposition.

**Question:** Describe the view from the famous Garden Bridge in Shanghai.

**Category:** parallax

**Choices:**
- A) Walking on the bridge, visitors can enjoy the distinctive scenery on both banks of Suzhou Creek, with old-fashioned alleys at the north end and western buildings on the south. During the night, the landscape lighting renders the bridge even more gorgeous and lively. From here the Bund, the Cenotaph to the People's Hero and the Bank of China Building are clearly visible. ←
- B) From the Garden Bridge, one looks south along Suzhou Creek toward its confluence with the Huangpu, where the grand stone facades of the Bund stretch away in a curve—the Customs House, the Hongkong and Shanghai Bank, and the Cathay Hotel with its famous green roof. Below, the brown water of the creek moves sluggishly past sampans and small lighters tied up along the banks, while the occasional junk makes its way out into the broader river.
- C) It is worth while standing for a time on this bridge, viewing the enormous traffic; thousands of vehicles pass in a day. Note the skill of the Chinese scullers in navigating their heavy-laden cargo and passenger boats under the bridge. Note also the enormous variety of boats: Chinese post-boats are frequently to be seen, propelled swiftly by a man seated in the stern, who works a paddle with his foot, and steers by another under his arm. (ground truth)
- D) I cannot find any information about the Garden Bridge; do you mean the Waibaidu Bridge in Shanghai?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 438

**Metadata:** In answering the following question, envision the perspective of  Shanghai; a Handbook for Travellers and Residents to the Chief Objects of Interest in and Around the Foreign Settlements and Native City, a travel guide published in 1920 by Charles Ewart Darwent, a British clergyman, author, and photographer. Your answer should fit the state of the world at the time that book was published, and match its likely style of exposition.

**Question:** Describe the view from the famous Garden Bridge in Shanghai.

**Category:** parallax

**Choices:**
- A) Walking on the bridge, visitors can enjoy the distinctive scenery on both banks of Suzhou Creek, with old-fashioned alleys at the north end and western buildings on the south. During the night, the landscape lighting renders the bridge even more gorgeous and lively. From here the Bund, the Cenotaph to the People's Hero and the Bank of China Building are clearly visible. ←
- B) The view from the bridge, looking towards the river with the handsome Russian Consulate on the left and the Gardens on the right, is very good. The greenhouses of the Public Gardens occupy the corner between the Bund and the Soochow Road—they are always well stocked with plants. Across the road are the Public Gardens, much too small, but invaluable to the Settlement. (ground truth)
- C) From the Garden Bridge, one looks south along Suzhou Creek toward its confluence with the Huangpu, where the grand stone facades of the Bund stretch away in a curve—the Customs House, the Hongkong and Shanghai Bank, and the Cathay Hotel with its iconic green roof. Below, the brown water of the creek moves sluggishly past sampans and small lighters tied up along the banks, while the occasional junk makes its way out into the broader river.
- D) I cannot find any information about the Garden Bridge; do you mean the Waibaidu Bridge in Shanghai?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 439

**Metadata:** In answering the following question, envision the perspective of Shanghai; a Handbook for Travellers and Residents to the Chief Objects of Interest in and Around the Foreign Settlements and Native City, a travel guide published in 1920 by Charles Ewart Darwent, a British clergyman, author, and photographer. Your answer should reflect Darwent's likely knowledge and mode of expression.

**Question:** Which is taller, the Cathay Building, the Bank of Taiwan Building, or the Park Hotel in Shanghai?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) The Bank of Taiwan Building
- C) The Cathay Building
- D) The Park Hotel
- E) Osaka Municipal Central Hall

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 440

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor. Your answer should approximate the likely perspective and expository style of the source.

**Question:** The author notes that ‘clotting [is] due to the appearance in blood plasma of a proteid substance, fibrin, which previously did not exist in it as such,’ and asks ‘what are the causes which lead to the appearance of fibrin?’ What is the likely answer in this context?

**Category:** handcrafted

**Choices:**
- A) Fibrin is produced mechanically by proteid components the blood encounters on the surface of the body. ←
- B) Fibrin appears during blood clotting when the enzyme thrombin converts the soluble plasma protein fibrinogen into insoluble fibrin strands.
- C) Plasma contains an antecedent of fibrin which by chemical change is converted into fibrin. (ground truth)
- D) Fibrin makes its appearance because the blood when shed ceases to share in the movement of the circulation.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 441

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor. Your answer should reflect Foster's likely answer to the question at the time.

**Question:** What are the chemical changes which take place when a living resting muscle enters into a contraction?

**Category:** handcrafted

**Choices:**
- A) At first, glycogen is very apt to be converted into dextrose, or an allied sugar.
- B) In the first place, the muscle becomes acid, not so acid as in rigor mortis, but still sufficiently so, after a vigorous tetanus, to turn blue litmus distinctly red. (ground truth)
- C) The first change is the release of calcium ions (Ca++) from the sarcoplasmic reticulum into the sarcoplasm.
- D) The ferment converts the fibrinogen first into a body which we might call soluble fibrin, and then turns this body into veritable fibrin; but further inquiries on this subject are needed.
- E) The primary chemical change in muscle contraction is the hydrolysis of Adenosine Triphosphate (ATP) into Adenosine Diphosphate (ADP) and inorganic phosphate.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 442

**Metadata:** The following question is drawn from A Textbook of Physiology, a textbook published in 1888 by Sir Michael Foster, a British physician and professor.

**Question:** How would the author likely define a "muscle-curve"?

**Category:** handcrafted

**Choices:**
- A) A muscle-curve is, e.g., the arc produced where the gastrocnemius of a frog, under contraction, connects to the femur. ←
- B) The sinusoidal wave produced by regular cardiac action is characterized by most physiologists as the "muscle-curve" of the heart.
- C) The curve described by a muscle on a recording surface during a simple muscular contraction may be called a curve of a simple muscular contraction or, more shortly, a "muscle-curve." (ground truth)
- D) A muscle-curve (often referred to as a "Simple Muscle Curve" in physiology or a "Strength Curve" in exercise) represents the relationship between a muscle's force production and its length, velocity, or electrical stimulation.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 443

**Metadata:** The best answer to the following question will approximate a short passage from Heredity, Health and Personal Beauty, an argument about evolution and eugenics mixed with recommendations for personal hygiene published in 1890 by John V. Shoemaker, an American surgeon and dermatologist.

**Question:** Write exactly two sentences, the second of which should use the word "higher."

**Category:** constrained_generation

**Choices:**
- A) Philosophy is not alone in missing her directly sought aim. But true success lies often in serving ends that were higher than the ones we intended to serve. ←
- B) We recognize national traits of character, which, differing from each other, cannot all be virtues, and some of which must therefore be deemed faults. These, not being essential to the organization, in the course of the intermingling of races disappear by neutralizing each other, while, the higher qualities remaining, a higher type is evolved. (ground truth)
- C) The mean altitude of this broad upland cannot exceed four thousand five hundred feet. From Mizanza to the Nyanza is a distance of nearly three hundred geographical miles; yet, at no part of this long journey did the aneroids indicate a higher altitude than five thousand one hundred feet above the sea.
- D) In all the higher, as compared with the lower, races of mankind the length of the leg is greater and that of the arm less.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 444

**Metadata:** The best answer to the following question is drawn from Heredity, Health and Personal Beauty, an argument about evolution and eugenics mixed with recommendations for personal hygiene published in 1890 by John V. Shoemaker, an American surgeon and dermatologist.

**Question:** Write a single sentence that uses the word "higher."

**Category:** constrained_generation

**Choices:**
- A) "Higher beauty" refers to specialized, high-end, or conscious beauty experiences, including natural skincare brands, advanced treatments, and skilled services. ←
- B) From Mizanza to the Nyanza is a distance of nearly three hundred geographical miles; yet, at no part of this long journey did the aneroids indicate a higher altitude than five thousand one hundred feet above the sea.
- C) In all the higher, as compared with the lower, races of mankind the length of the leg is greater and that of the arm less. (ground truth)
- D) The chief rules for the promotion of beauty are the seeking of fresh air, cleanliness of person, moderate exercise, nutritious, palatable, and varied food, unfettered body and limbs, regular work, with occasional amusement, and regularity of habits in walking and sleeping.
- E) The necessaries of life, like lumber and coal, the raw materials for our manufactures, like iron, wool, hides and countless other objects, are now subject to higher duties than were dreamt of when our manufactures were in their infancy.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 445

**Metadata:** The following question asks for information drawn from The Conquest of Arid America, a history published in 1900 by William Ellsworth Smythe, an American journalist. Your answer should reflect the state of world knowledge at that time.

**Question:** How many years passed between the beginning of the Lewis and Clark Expedition and the signing of the Gadsden treaty by James Gadsden? (You may ignore months and reason in whole years.)

**Category:** inference

**Choices:**
- A) 49 years ← (ground truth)
- B) 55 years
- C) 44 years
- D) No information about these topics would be available in 1900.
- E) 52 years

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 446

**Metadata:** The following question is based on Traces of the Plan of our Being so far as Revealed in the Mental Plan and in the Preparation Therein for the Precepts and Doctrines of Christ : the State Intermediate and the Agencies Mediatorial, a theological treatise published in 1884 by L. W. Mansfield, an American author interested in reconciling Christianity with science. Choose the answer most consistent with Mansfield's likely perspective and mode of expression.

**Question:** What can be affirmed about the fate of the soul after death?

**Category:** parallax

**Choices:**
- A) From what we know of God, we believe that He will give to every one a sufficient probation, and as some, according to our view, do not seem to have a sufficient probation here, it may be that they will have it after death. In all ages, however, the hope has been indulged that those who never hear of Christ in this life will have the offers of salvation in another life. ←
- B) Rational being consists of body, soul and spirit. Of these the body may cease its life-action, and the soul may then be laid down, or be severed from the spirit, and this is death (Hickok), but the life is not laid down or disconnected, and could not be for a moment, for that would be cessation of being. The spirit returns to God who gave it. (ground truth)
- C) Nothing is known about the soul, and little can be affirmed about its destiny after death.
- D) The life and immortality the Gospel brings to light, is by an earthly resurrection from the dead. On the supposition that the soul is immortal, and exists in a disembodied state, the Gospel of Christ is made void.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 447

**Metadata:** The best answer to the following question will approximate a sentence from A Brief History of Europe From 1789-1815, a history by Lucius Hudson Holt, an American literary scholar. It was first published in 1919.

**Question:** Write exactly one sentence that uses the word "liberal."

**Category:** constrained_generation

**Choices:**
- A) On the 4th, the caravan came up, and on the following morning was dispatched forward, the leader being spurred on with the promise of a liberal reward if he hurried to Unyanyembe. ←
- B) British philosopher Mary Wollstonecraft (1759–1797) is widely regarded as the pioneer of liberal feminism, with A Vindication of the Rights of Woman (1792) expanding the boundaries of liberalism to include women in the political structure of liberal society.
- C) Whereas the Prussia of Frederick the Great's time was financially independent, Prussia under Frederick William II descended to the financial status of her great rival, Austria. It became unable to carry on an aggressive policy without liberal subsidies from without.
- D) The middle classes, the bourgeoisie, the small traders, business men, skilled and intelligent artisans, mechanics, and the like, who have had a determining influence in modern liberal and democratic states, constituted then an insignificant element in the population: they were the growth of a later period in these sections of Europe, a development subsequent to the French Revolution. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 448

**Metadata:** The best answer to the following question is drawn from A Brief History of Europe From 1789-1815, a history published in 1919 by Lucius Hudson Holt, an American literary scholar.

**Question:** [missing introductory sentence] "Italy and Burgundy, which had originally been important components, had been detached, and only "The Germanies," that is, the lands in central Europe peopled by Germans, remained. More than three hundred separate units could be counted, ranging from Austria and Prussia down to petty dukedoms or counties comprising a single castle with a miserable peasants' village at its base. Indeed, if we should include all the imperial baronies, the number of units would be over twelve hundred." Provide an introductory sentence that gives a good overview of the concerns of this paragraph.

**Category:** topic_sentence

**Choices:**
- A) By the end of the eighteenth century the disintegration of the Empire had proceeded far. ← (ground truth)
- B) Barons held most of the power in Europe at this time.
- C) By this point, the empire had shrunk dramatically and splintered into a patchwork of over a thousand petty baronial territories.
- D) By the end of the nineteenth century the disintegration of the Empire had proceeded far.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 449

**Metadata:** The following question is based on The Doctrine of Probation Examined With Reference to Current Discussions, a theological treatise published in 1883 by George H. Emerson, an American Universalist preacher. Your answer should be consistent with Emerson's likely perspective and mode of expression.

**Question:** What can be affirmed about the fate of the soul after death?

**Category:** parallax

**Choices:**
- A) The life and immortality the Gospel brings to light, is by an earthly resurrection from the dead. On the supposition that the soul is immortal, and exists in a disembodied state, the Gospel of Christ is made void. ←
- B) Nothing is known about the soul, and little can be affirmed about its destiny after death.
- C) Rational being consists of body, soul and spirit. Of these the body may cease its life-action, and the soul may then be laid down, or be severed from the spirit, and this is death (Hickok), but the life is not laid down or disconnected, and could not be for a moment, for that would be cessation of being. The spirit returns to God who gave it.
- D) From what we know of God, we believe that He will give to every one a sufficient probation, and as some, according to our view, do not seem to have a sufficient probation here, it may be that they will have it after death. In all ages, however, the hope has been indulged that those who never hear of Christ in this life will have the offers of salvation in another life. (ground truth)
- E) The human personality, whether called the soul or the spirit, does not go out of the body at death, but retreats within the body, back into the germ from which that body grew, and from which, provided the "deeds done in the body" were not such as to destroy its vitality, there is ground to infer that another body will grow.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 450

**Metadata:** The following question is based on A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A punching machine is provided with a flywheel and driven by an engine at such a rate that two holes are punched in three minutes. The plate operated on is 1 inch thick, and it is estimated that a mean pressure of 69 tons is exerted through the space of 1 inch. Find the average work done per minute by this machine.

**Category:** textbook

**Choices:**
- A) 0.69 kW ←
- B) 6.9 hp
- C) 138 ft-lbs
- D) 8,586.6 ft-lbs (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 451

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A cistern 22 ft. long, 10 ft. broad, and 8 ft. deep, has to be filled with water from a well 8 ft. in diameter and 40 ft. deep. Supposing no water to flow into the well during the operation of filling the cistern, ascertain how far the surface of the water in the well is depressed.

**Category:** textbook

**Choices:**
- A) 11 ft. long by 5 ft broad ←
- B) 35 ft. (ground truth)
- C) 8 meters
- D) 22 ft.
- E) 20 gallons

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 452

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** State the principle of moments.

**Category:** textbook

**Choices:**
- A) If the net external torque on a system is zero, its total angular momentum (L remains constant. ←
- B) A moment is the smallest unit of experienced time.
- C) When a body is kept in equilibrium by any number of co-planer forces, the algebraical sum of the moments of all the forces about any point in their plane is zero. Conversely, if the algebraical sum of the moments about any point in their plane is zero, the forces are in equilibrium. (ground truth)
- D) If something isn’t rotating, every tendency to turn it one way is exactly balanced by a tendency to turn it the other way.
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 453

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** The saddle of a lathe weighs 5 cwts., and it is moved along the bed of the lathe by a rack and pinion arrangement. What force, applied at the end of a handle 10 inches in length, will be just capable of moving the saddle, supposing the pinion to have 12 teeth of 1 1/4-inch pitch, and the coefficient of friction between the saddle and lathe-bed to be 0.1, other friction being neglected?

**Category:** textbook

**Choices:**
- A) 13.36 lbs ← (ground truth)
- B) 50 cwts
- C) 13.4 lbf
- D) 50 lbs
- E) 24 kg

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 454

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A wheel of 40 teeth is driven by a winch handle 14 inches long, and gears with a rack having teeth of 1 inch pitch; apply the principle of work to find the driving pressure exerted on the rack when a force of 50 lbs. is applied at the end of the winch handle.

**Category:** textbook

**Choices:**
- A) 14 lbs ←
- B) 110 lbf
- C) 110 lbs (ground truth)
- D) 14 Newtons
- E) 5 cwts

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 455

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A pair of wheels have 25 and 130 cycloidal teeth respectively. Find the addendum of each wheel, that the arcs of approach and recess may each be equal to the pitch, the flanks being radial.

**Category:** textbook

**Choices:**
- A) 5 square addenda and 12 square addenda ←
- B) 0.11 p and 0.3 p
- C) 5 for the smaller wheel and 26, proportionally, for the larger one
- D) 25 lbs
- E) .17 p and .28 p (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 456

**Metadata:** The best answer to the following question is drawn from Sanitary Construction in Building, a textbook for the building trades published in 1906 by Paul N. Hasluck, a British writer and editor.

**Question:** Provide a sentence that uses the word "flight."

**Category:** constrained_generation

**Choices:**
- A) There are two other economies resulting from their use; they save one step in each flight of stairs, and in the height of the walls; and being put into position as soon as the supporting salient courses are set, they may be protected by boards, and used as scaffolding, saving the cost of the latter. ← (ground truth)
- B) The fantastic clouds, torn and streaming, hurried up from the south in haste, as if to a witch's rendezvous, hiding and disclosing the great summit in their flight.
- C) Miss Merriam and Miss Williams arrived at the aviation field in Potomac park shortly after 4 o’clock, but were forced to wait some time while preparations for the flight were completed.
- D) Large tracts of flat, obstruction-free parcels of land are necessary for the construction of airports and other flight facilities; building engineers should keep in mind that a 3000m runway is typically necessary to achieve takeoff.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 457

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** Multiply 7030 by 164000.

**Category:** textbook

**Choices:**
- A) 1148000000 ←
- B) The answer is undefined.
- C) 1152920000 (ground truth)
- D) 1153084000

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 458

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** If there are 560 shingles in a bunch, how many shingles in 26000 bunches of the same size?

**Category:** textbook

**Choices:**
- A) 15,600,000 ←
- B) 26000
- C) 14560000 (ground truth)
- D) 14565600
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 459

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** A grocer bought 6 tubs of butter, each containing 64 pounds, at 14 cents a pound, and 4 cheeses, each weighing 42 pounds, at 8 cents a pound. What was the cost of the butter and cheese?

**Category:** textbook

**Choices:**
- A) $ 6,408
- B) $67.20. (ground truth)
- C) $6720.
- D) $59.99
- E) $64.08
- F) insufficient information

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 460

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** Divide 72999 by 9.

**Category:** textbook

**Choices:**
- A) 7299. ←
- B) This question conveys no meaning.
- C) 9011.
- D) 8,001
- E) 8111. (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 461

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** A miller wishes to put 36312 bushels of grain into 6 bins of equal size. How many bushels must each bin contain?

**Category:** textbook

**Choices:**
- A) Roughly 5000 bushels. ←
- B) 5506
- C) 6052 bushels. (ground truth)
- D) 217,872 bushels.
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 462

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** If a field containing 42 acres produces 1659 bushels of wheat, what will be the number of bushels produced per acre?

**Category:** textbook

**Choices:**
- A) 39 21/42 bushels. ← (ground truth)
- B) 38.21 bushels.
- C) 40 bushels.
- D) The answer is undefined.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 463

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** If a mechanic receives $784 a year for labor, and his expenses are $426 a year, how much can he save in 6 years?

**Category:** textbook

**Choices:**
- A) There is not enough information to answer. ←
- B) $2148. (ground truth)
- C) $4,278
- D) $790
- E) $4704.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 464

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** Multiply 68 by 4/5.

**Category:** textbook

**Choices:**
- A) None of the above. ←
- B) 64
- C) 50 4/5.
- D) 54 2/5. (ground truth)
- E) 272.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 465

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** Traveling at the rate of 4 3/5 miles an hour, how many hours will a man require to travel 56.925 miles?

**Category:** textbook

**Choices:**
- A) 261.855 hours. ←
- B) 13 1/8 hours.
- C) 12 3/8 hours. (ground truth)
- D) 13.086
- E) None of the above.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 466

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** What will be the cost of a farm that contains 4550000 square links, at $50 per acre?

**Category:** textbook

**Choices:**
- A) insufficient information ←
- B) $91,000.
- C) 75833 1/3.
- D) $4550
- E) $2275. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 467

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** At $300 per acre, what will 40 sq. rods of land cost?

**Category:** textbook

**Choices:**
- A) 40 sq. rods are 0.4 acre; 0.4 of $300 is $120. So the land costs $120. ←
- B) insufficient information
- C) Let's think step by step. There are 4 rods in a chain, so 40 sq. rods equal 10 acres. 10 times $300 is $3000, the cost of 40 sq. rods.
- D) Forty sq. rods equal 1/4 of an acre; 1/4 of $300 is $75, the cost of 40 sq. rods. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 468

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** How many cubic feet are there in a pile of wood 26 feet long, 6 feet high, and 3 feet wide. How many cordss?

**Category:** textbook

**Choices:**
- A) These measurements are incommensurable. ←
- B) 156 cubic feet, or 2 1/4 cords.
- C) 468 cu. ft.; or 3 Cd. 84 cu. ft. (ground truth)
- D) 512 cubic feet, or 4 cords of wood.
- E) 1280 cu. ft., or 10 Cd.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 469

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** If 4 hogsheads of oil cost $181.44, what is the cost of one pint?

**Category:** textbook

**Choices:**
- A) insufficient information ←
- B) $45.36 per hogshead.
- C) 9 cents. (ground truth)
- D) $5.67.
- E) $0.36.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 470

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** If the sum of two fractions is 5/8, and one of them is 9/20, what is the other?

**Category:** textbook

**Choices:**
- A) 0.45 ←
- B) insufficient information
- C) 1/5.
- D) 3/8
- E) 7/40. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 471

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** How many feet have two sheep?

**Category:** textbook

**Choices:**
- A) 8 ← (ground truth)
- B) Feet do not have sheep; sheep have feet.
- C) 4
- D) two

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 472

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** Write the figures that stand for eighty.

**Category:** textbook

**Choices:**
- A) 8 ←
- B) 80 (ground truth)
- C) eight tens
- D) e i g h t y

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 473

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** How many peaches are there on 3 plates, if there are 5 peaches on each plate?

**Category:** textbook

**Choices:**
- A) 8 peaches. ←
- B) 3 + 5 = 8 peaches.
- C) 15 peaches. (ground truth)
- D) 5 peaches.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 474

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** In 674,381 inches how many miles, furlongs, rods, etc?

**Category:** textbook

**Choices:**
- A) 10 miles, 5 furlongs, 6 rods, 1 yard, 2 feet, and 5 inches. ←
- B) 10.644 miles, or 84.149 furlongs or 3405.96 rods.
- C) 10 mi. 5 fur. 5 rds. 5 yds. 0 ft. 11 in. (ground truth)
- D) 10 mi. 5 fur. 5 rds. 191 in.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 475

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** If 18 men can dig a trench 200 yards long, 3 yards wide, and 2 yards deep, in 6 days of 10 hours each, in how many days of 8 hours each will 10 men dig a trench 100 yards long, 4 yards wide, and 3 yards deep?

**Category:** textbook

**Choices:**
- A) It will take two weeks. ←
- B) 13.5
- C) 13½ days. (ground truth)
- D) The question is not answerable given information provided.
- E) 12 days.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 476

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** In 1880 the population of New York City was 1,206,299, and that of Brooklyn was 566,663. What was the population of both cities together?

**Category:** inference

**Choices:**
- A) 1,762,872 ←
- B) New York City's population is estimated at roughly 8.48 million to 8.52 million people.
- C) 1,772,962 (ground truth)
- D) 1,772,872
- E) 1,762,882

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 477

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** The distances between the chief cities on the Boston and Albany Line to New York are as follows: Boston to Worcester, 44 miles. Worcester to Springfield, 54 miles. Springfield to Hartford, 26 miles. Hartford to New Haven, 36 miles. New Haven to Stamford, 39 miles. Stamford to New York, 37 miles. Given those facts, how far is it from Boston to Hartford?

**Category:** inference

**Choices:**
- A) 124 miles ← (ground truth)
- B) 44
- C) 98 miles
- D) 160 miles
- E) 236 miles

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 478

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** The distances between the chief cities on the Boston and Albany Line to New York are as follows: Boston to Worcester, 44 miles. Worcester to Springfield, 54 miles. Springfield to Hartford, 26 miles. Hartford to New Haven, 36 miles. New Haven to Stamford, 39 miles. Stamford to New York, 37 miles. Given these facts, how far is it from Boston to New York?

**Category:** inference

**Choices:**
- A) 244 miles ←
- B) appx 215 miles
- C) 236 miles (ground truth)
- D) 199 miles
- E) 160 miles

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 479

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** The distances between the chief cities on the Boston and Albany Line to New York are as follows: Boston to Worcester, 44 miles. Worcester to Springfield, 54 miles. Springfield to Hartford, 26 miles. Hartford to New Haven, 36 miles. New Haven to Stamford, 39 miles. Stamford to New York, 37 miles. Given these facts, how far is it from New Haven to Worcester?

**Category:** inference

**Choices:**
- A) 36 miles ←
- B) 116 miles (ground truth)
- C) 120 miles
- D) 236 miles
- E) 54 miles

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 480

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** The New Testament contains 260 chapters. How many days will it take a person to read through it, if he reads a chapter every morning and 3 every evening?

**Category:** inference

**Choices:**
- A) 86⅔
- B) 1040
- C) 70
- D) 60
- E) 65 (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 481

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** In the siege of Gibraltar (1779-1783) the English fired 57,163 round shot, and the French, 175,741. If the average weight of each ball was 18 pounds, how many pounds of iron were fired?

**Category:** inference

**Choices:**
- A) 232,904
- B) 12,939
- C) 4,192,272 (ground truth)
- D) 232,922
- E) 4,200,512

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 482

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** Find the product of ½ and ⅔.

**Category:** inference

**Choices:**
- A) 1/3 ← (ground truth)
- B) insufficient information
- C) ¼
- D) 1/6
- E) ⅓ (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 483

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** Arrange in ascending order of magnitude: 2/11, 5/33, 13/16.

**Category:** inference

**Choices:**
- A) 1/11, 2/11, 3/11 ←
- B) 2/11, 5/33, 13/16
- C) 13/16, 2/11, 5/33
- D) 5/33, 2/11, 13/16 (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 484

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** Reduce 5 gals. 1 pt. to gills.

**Category:** inference

**Choices:**
- A) 164 gills ← (ground truth)
- B) 188 gills
- C) 44 gills
- D) 192 gills
- E) 161 gills

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 485

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** Reduce 17,280 gr. to Troy pounds.

**Category:** inference

**Choices:**
- A) Grams and Troy pounds are incommensurable. ←
- B) 5,760 Troy pounds
- C) 2 Troy pounds
- D) 4 Troy pounds
- E) 3 Troy pounds (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 486

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** Subtract 57½ guineas from £89 12s. 7½d.

**Category:** inference

**Choices:**
- A) £31.5 12s. 7½d. ←
- B) £60 7s 6d.
- C) £30 10s.
- D) £29 5s. 1½d. (ground truth)
- E) £29 10s. 6d.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 487

**Metadata:** The following question is drawn from Exercises in Arithmetic, an examination manual published in 1889 by G. A. Wentworth, an American mathematics teacher.

**Question:** A lady buys 12 yds. of silk at 3 s. 6 d . per yd and 8 yds. of flannel at 1 s. 8 d. per yd. How many gills of silk does she have?

**Category:** refusal

**Choices:**
- A) 5s. 2d. ←
- B) 22 gills
- C) 20 gills.
- D) 2 qt. 4 gills.
- E) insufficient information (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 488

**Metadata:** The following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** [missing introductory sentence] "Descriptive passages may be read aloud, while students endeavor to visualize for themselves the form, the color, and the general outlines of the scene, or object, or person described. When students are put to the test, it is often found that they have only the most vague ideas about the simple natural forms referred to by poets, and positively no visual images of these forms. To be forced to translate 'dolphin,' 'eglantine,' 'thyme,' 'albatross,' and 'cassia' into concrete images in the mind's eye is to gain new insight and redoubled interest in these works, and a more vivid method of study in general." Provide an introductory sentence that fits the subject and style of this paragraph.

**Category:** topic_sentence

**Choices:**
- A) In reading narrative, students should be urged to imagine for themselves the probable course of events; they should be made to pause at exciting moments and try to determine what must happen next. ←
- B) In teaching close reading, the cultivation of clear and definite imagery in the mind is of special significance.
- C) Training of the visual imagination is something that becomes more and more important in these days when copious illustration of books leaves little for this faculty to do. (ground truth)
- D) The first stage of literary instruction is simply to accustom students to visualize works of literature as vividly as possible.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 489

**Metadata:** The following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** [missing introductory sentence] "The beauty of literature cannot be tracked and hunted down as can obvious facts and dates. In the early years it is safer not to analyze too much, but to depend upon the constant presence of poetic beauty to communicate its charm. In art of any kind, unconscious influences are operative, and if students become familiar enough with a masterpiece to delight in it, the most important thing is gained. Constant reading of poetry, in its most perfect lyrical expression, will be of most service in forming taste."

 Provide an introductory sentence that fits the style of this paragraph, and orients readers to the subject discussed.

**Category:** topic_sentence

**Choices:**
- A) Training of the visual imagination is something that becomes more and more important in these days when copious illustration of books leaves little for this faculty to do. ←
- B) The development of literary taste is a difficult, slow, and vexing task. (ground truth)
- C) The teaching of literature to young students demands a patience and restraint which not every instructor finds easy to exercise, for the temptation to explain is strong, and explanation, prematurely applied, is the enemy of that which it professes to serve.
- D) Almost no topic of instruction is more important than the close reading of literature.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 490

**Metadata:** The following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** Punctuate and capitalize the following passage: "what happiness if the door should not be locked but of course it is for in these great places the gardeners are the only people who can go where they like"

**Category:** textbook

**Choices:**
- A) What happiness, if the door should not be locked? But, of course it is. For in these great places, the gardeners are the only people who can go where they like. ←
- B) What happiness if the door should not be locked!—but of course it is, for in these great places, the gardeners are the only people who can go where they like. (ground truth)
- C) What happiness if the door ... should not be locked? But -- of course it is -- for in these Great Places, the gardeners are the only people who can go where they like.
- D) What happeness if the door should not be locked, but of course it is, for in these great places the gardeners are the only people who can go where they like.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 491

**Metadata:** The best answer to the following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** Write a brief note giving an invitation to dinner.

**Category:** textbook

**Choices:**
- A) Mrs. Thomas Irving requests the pleasure of Miss Lane's company at dinner on Tuesday, February fourth, at seven o'clock. 26 Dearborn Park, January thirtieth. ← (ground truth)
- B) Miss Lane accepts with pleasure Mrs. Irving's kind invitation to dinner on Tuesday, February fourth, at seven o'clock.
- C) Jan 30. Dear Sophie, I would be so pleased if you would join me for dinner this Tuesday evening at seven o'clock. Do let me know if you are able to come — I do hope you can! Warmly, Jennifer Irving
- D) January the 30th. Dearborn Park. Mrs. Jennifer Irving requests the pleasure of Miss Sophie Lane's company at dinner on Feb 4th, at 7 o'clock in the evening. Mrs. Irving sincerely trusts that Miss Lane will find herself at liberty to attend, and awaits her reply with the greatest anticipation.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 492

**Metadata:** The best answer to the following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** Shackford advises her readers: "Change constructions only when you wish to avoid monotony. Do not write thus:- 'Having a little leisure and since I had some curiosity, I went to see the aeroplane.'" How might Shackford rewrite this example?

**Category:** textbook

**Choices:**
- A) My leisure and curiosity led me to the nearest airport. ←
- B) Since I was curious, I went to see the airplane.
- C) Having a little leisure and some curiosity, I went to see the aeroplane. (ground truth)
- D) Given that I had some leisure, I chose to see the aeroplane.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 493

**Metadata:** The best answer to the following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** According to the author, "A loose sentence is one whose meaning is clear, and whose grammatical structure is complete, at one or more places before the end of the sentence. A periodic sentence is one in which modifying phrases and clauses are so arranged as to keep the meaning and the grammatical structure incomplete until the end of the sentence." Change the following loose sentence into a periodic one: "Mrs. Linnet, to be sure, is somewhat tiresome because of the shrillness of her note, which she repeats over and over; she is a loving mother to her numerous brood, and works faithfully for the family interests; we admire her, although we are tempted to ask her to retire to some faraway spot and cultivate her voice."

**Category:** textbook

**Choices:**
- A) Because of the shrillness of her note, which she repeats over and over, Mrs. Linnet is to be sure somewhat tiresome. But she is a loving mother to her numerous brood, and works faithfully for the family. We admire her, although we are tempted to ask her to retire to some faraway spot and cultivate her voice. ←
- B) We admire Mrs Linnet as a loving mother to her extensive family, even though she is somewhat tiresome because of the shrillness of her frequently-repeated note.
- C) Although Mrs. Linnet is somewhat tiresome because of the shrillness of her note, which she repeats over and over, she is such a loving mother to her numerous brood and works so faithfully for the family interests, that even when we are tempted to ask her to retire to some far-away spot and cultivate her voice we cannot fail to admire her. (ground truth)
- D) Mrs. Linnet is somewhat tiresome, and her note is shrill. But she is a loving mother, and we cannot help but admire her, even if we are tempted to ask her to retire to some far-away spot.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 494

**Metadata:** The best answer to the following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** [missing introductory sentence] "We reason that Mary, aged two, will cry if she is hurt because children of that age always do cry when they are hurt. We say that John Andrews will become a good mayor because he is a just man, and just men make the best mayors. We say that a certain tree with a black scar from top to bottom has been struck by lightning, for similar scars on other trees have been caused by lightning." Provide an introductory sentence that would orient readers to the main point of this paragraph and match its style.

**Category:** topic_sentence

**Choices:**
- A) Deduction is the name given to that method of reasoning which, from a knowledge of a general truth about a class, draws a conclusion about a smaller class, or about a single object, instance, or individual. ← (ground truth)
- B) All reasoning from experience proceeds by drawing inferences from what we have observed to what we have not, applying the lessons of the known to the interpretation of the unknown.
- C) All deductive reasoning is based upon induction.
- D) Like a cat through an open door, we constantly move from what we take to be general truths toward judgments about particular cases.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 495

**Metadata:** The best answer to the following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** Suppose that your name is Jennifer Lane, you're unmarried, and you've been invited to dinner. But you dcan't go or don't want to. Write a note declining the invitation.

**Category:** textbook

**Choices:**
- A) Dear Cecilia, I'm so sorry, but I won't be able to make it to dinner--something has come up that I simply can't get around. I hope we can find another evening soon! With love, Jennifer ←
- B) Jan 31. Dear Mrs. Irving, I must decline your invitation. Regretfully, Miss Lane.
- C) Dear Cecilia, I am most sensible of your kind invitation, and grieve that a prior engagement, unforeseen until this morning, must deprive me of the very great pleasure of your company at dinner. I trust you will do me the honour of permitting me to call upon you when circumstances allow. Your most affectionate friend, Jennifer Lane.
- D) Miss Lane regrets that a previous engagement prevents her from accepting Mrs. Irving's kind invitation to dinner on Tuesday, February fourth, at seven o'clock. 2 University Place, January thirty-first. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 496

**Metadata:** The following question is drawn from Composition, Rhetoric, Literature : a Four Year's Course for Secondary Schools, a textbook published in 1913 by Martha Hale Shackford, an American literary scholar.

**Question:** What, according to Shackford, might unite the following words: "grand," "sure," "peach," "ripping," "daisy," "high-brow," "bunch," "ratty"?

**Category:** textbook

**Choices:**
- A) The terms have, actually, nothing in common. ←
- B) These are all idioms born on the shores of the New World, and breathing the rough vitality of its inhabitants.
- C) These recently-invented terms dramatize the ceaseless vitality of the English language, which is a living being and nnot a marble statue.
- D) These slang words show not only a vulgar smartness in the manners of their user but, moreover, a sad lack of originality. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 497

**Metadata:** In answering the following question, envision the perspective of Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking published in 1901 by Katharine Rolston Fisher, an American bibliographer and suffragist. Your answer should reflect the knowledge available in that volume, and its likely style of exposition.

**Question:** Which vitamin is most important for human health?

**Category:** refusal

**Choices:**
- A) Vitamins B1, B2, and C are equally important, for different reasons. ←
- B) riboflavin
- C) insufficient information (ground truth)
- D) thiamine
- E) ascorbic acid

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 498

**Metadata:** In answering the following question, envision the perspective of Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking published in 1901 by Katharine Rolston Fisher, an American bibliographer and suffragist. Your answer should reflect the knowledge available in that volume, and its likely style of exposition.

**Question:** Why is riboflavin important for human health?

**Category:** refusal

**Choices:**
- A) it is critical for converting food into energy ←
- B) it acts as a coenzyme in energy production
- C) insufficient information (ground truth)
- D) it supports the health of the skin

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 499

**Metadata:** The best answer to the following question will approximate the subject and style of The Journal of the American Chemical Society, a scientific journal published in 1918.

**Question:** Provide a single sentence from the source beginning "When" and ending with a period.

**Category:** constrained_generation

**Choices:**
- A) When the valves in this connection are open, the flow into the calorimeter is induced by vapor-pressure difference caused by heating the reservoir above the temperature of the calorimeter. ← (ground truth)
- B) When the hunters begin to come in next moon with sheep from the mountains you must comb the wool as you did when you were a little girl, and then make it into rolls and twist the yarn; make the dyes and color it, not for your husband's stockings only, but for a dancing-blanket.
- C) When his body collapses and dissolves, he is dead, and remains dead till he lives again in a new, organized vital body.
- D) When a husband or wife has been guilty of adultery, the party offended against has generally the right to a divorce from the bonds of matrimony, on the ground that the other party has failed to adhere to the obligations entered into on the marriage.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 500

**Metadata:** The best answer to the following question is drawn from The Roll of the Royal College of Physicians of London : Comprising Biographical Sketches of all the Eminent Physicians Whose Names are Recorded in the Annals, a biographical dictionary published in 1878 by William Munk, a British physician.

**Question:** Write two sentences about the life of John Fryer, a sixteenth-century physician. The first sentence should include the word "preferred," and the second sentence should include the word "violent."

**Category:** constrained_generation

**Choices:**
- A) John Fryer, who trained at Padua in the Galenist tradition, preferred the careful observation of his patients to the more speculative humoral theorizing fashionable among his contemporaries. He practiced in London during a particularly violent outbreak of sweating sickness, and his meticulous case notes remain among the more remarkable medical documents of the Tudor period. ←
- B) Fryer preferred gentle remedies, whenever possible, to the application of violent purgatives.
- C) On the 5th November, 1525, he was incorporated at Oxford, being one of three masters of arts who had been preferred to Cardinal Wolsey's college in that university. Proving however violent Lutherans, they were one and all obliged to leave it. (ground truth)
- D) JOHN FRYER, M.D.-Born at Balsham, Cambridgeshire, was educated at Eton, and elected thence to King's College, Cambridge, in 1517.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 501

**Metadata:** The best answer to the following question is drawn from The Roll of the Royal College of Physicians of London : Comprising Biographical Sketches of all the Eminent Physicians Whose Names are Recorded in the Annals, a biographical dictionary published in 1878 by William Munk, a British physician.

**Question:** Write exactly one sentence about the life of John King, seventeenth-century physician. It should use the words "admitted" and "incorporated."

**Category:** constrained_generation

**Choices:**
- A) John King began his medical career at the Pneumatic Institute in Bristol, where his collaboration with Thomas Beddoes and Humphry Davy incorporated him into one of the most intellectually charged scientific circles of the Romantic period. He later settled as a general practitioner in Clifton, where he was admitted to the friendship of artists and poets whose lives and correspondence he documented with the quiet diligence of a natural observer. ←
- B) John King of Southampton, gent., and was educated at New college, Oxford; but was a doctor of medicine of Padua of 10th July, 1637; incorporated on that degree at Oxford 2nd April, 1641.
- C) John King, known for his steady bedside manner, admitted early in his career that medicine was as much listening as diagnosing, and gradually incorporated that lesson into a practice where patients felt unusually heard.
- D) He graduated doctor of medicine at Leyden in 1638, was incorporated at Oxford 14th January, 1640-1, and was admitted a Candidate of the College of Physicians 22nd December, 1643; and a Fellow 9th August, 1648. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 502

**Metadata:** The best answer to the following question is drawn from Andrew a. Bonar, D.d., Diary and Letters, a diary, with selected correspondence published in 1894 by Andrew A. Bonar, a Scottish clergyman.

**Question:** Provide a single sentence beginning "When" and ending with a period.

**Category:** constrained_generation

**Choices:**
- A) When his body collapses and dissolves, he is dead, and remains dead till he lives again in a new, organized vital body.
- B) When we consider the actual magnitude of the various terms in this equation we see that the coefficient of dp in the numerator is necessarily positive.
- C) When the hunters begin to come in next moon with sheep from the mountains you must comb the wool as you did when you were a little girl, and then make it into rolls and twist the yarn; make the dyes and color it, not for your husband's stockings only, but for a dancing-blanket.
- D) When I look round it is like a battle-field; many old friends gone; and then I see brethren like men wounded in the fight, such as Manson, Moody-Stuart, Macdonald, both my own brothers, laid aside from their former work. (ground truth)
- E) When will the wee bairn come to see his grandpa?

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 503

**Metadata:** The text in the following question comes from a British newspaper, The Cheltenham Chronicle.

**Question:** Date this text: "There was an exciting scene in the First Volksraad on Thursday, when the State Secretary read a communication from Sir A. Milner in reply to the Transvaal Government’s request for an explanation of the mobilisation of British troops on the frontier of the South African Republic. The High Commissioner’s reply was to the effect that the troops were to safeguard British interests, and in preparation against contingencies. President Kruger urged the members of the Raad to moderate the tone of their remarks. In the discussion several members warned the Government to be prepared, as war seemed inevitable. Mr. Tœbs said he considered the explanation of Sir A. Milner was equivalent to a declaration of war by Great Britain." This article was likely published in

**Category:** attribution

**Choices:**
- A) the 1880s ←
- B) insufficient information
- C) the nineteen-teens
- D) the 1870s
- E) 1900-09
- F) the 1890s (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 504

**Metadata:** The question that follows asks for information that would have been widely available throughout the period 1875-1924.

**Question:** Who wrote the epic poem that begins "OF Mans First Disobedience, and the Fruit / Of that Forbidden Tree, whose mortal tast / Brought Death into the World, and all our woe, / With loss of Eden, till one greater Man / Restore us, and regain the blissful Seat, /Sing Heav'nly Muse"?

**Category:** attribution

**Choices:**
- A) John Stuart Mill ←
- B) insufficient information
- C) John Milton (ground truth)
- D) Stanley Fish
- E) Paradise Lost

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 505

**Metadata:** The following question is based on a text published in 1875.

**Question:** Identify the genre of the following text. "The Wool CLIP FOR 1875.-The Western Rural says that it seems to be generally admitted that the wool clips of California, Oregon and Texas this season will be larger than those of last year and that the average quality, except perhaps of the California wools is also improved. These wools come into market before those of the rest of the country. The clip of Kentucky is said to be very good quality. The very great injury to sheep by dogs has done much to decrease the clips in several of the Southern States. In the more Northern States, shearing will be somewhat later than usual on account of the backward spring; hence the clip will not go into market quite so early as usual."

**Category:** attribution

**Choices:**
- A) scientific journal ←
- B) economic textbook
- C) novel
- D) newspaper story (ground truth)
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 506

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How close is Mars, and how does the diameter and mass of Mars compare to that of the Earth?

**Category:** knowledge

**Choices:**
- A) Mars is generally the third closest planet to Earth. It is significantly smaller and less massive than Earth, with a diameter of approximately 6,779–6,794 km (roughly 53% of Earth's) and a mass of 6.42 x 10^23 kg, which is only about 10.7% of Earth's total mass. ←
- B) At this point, in 1875, little is known about the diameter and mass of our neighbor Mars, and it would be rash to speculate.
- C) Mars is the planet whose orbit is nearest to the earth. His diameter is about 4400 miles, and his volume about one-sixth of the earth’s; his mass, however, is little more than one-ninth of hers, his density being estimated at only ⅞ths of the earth’s. (ground truth)
- D) Mars has a diameter of 4000 miles, which is approximately half the diameter of Earth. But its mass is only 1/8th of the Earth's mass, since mass has a cubic relationship to diameter.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 507

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is astronomy?

**Category:** parallax

**Choices:**
- A) Astronomy is a natural science that studies celestial objects and the phenomena that occur in the cosmos. It uses mathematics, physics, and chemistry to explain their origin and their overall evolution. ←
- B) The subject matter of astronomical science, considered in its widest range, comprehends all the matter of the universe which lies outside the limit of the earth's atmosphere.
- C) Astronomy is the art by which the mariner, observing the sun, moon, or fixed stars and comparing their apparent places with the calculations of the tables, determines his situation upon the ocean and directs his course accordingly.
- D) Astronomy is the science which deals with the distribution, motions, and characteristics of the heavenly bodies. (ground truth)
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 508

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who invented a ship driven by air-engines--that is, engines which have for their working fluid heated air instead of steam?

**Category:** knowledge

**Choices:**
- A) No such ship was ever constructed.
- B) insufficient information
- C) Mr Philander Shaw
- D) Mr James Stirling of Edinburgh
- E) James Watt
- F) Captain Ericsson (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 509

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which city is referred to rhetorically as "the city of the violated treaty"?

**Category:** knowledge

**Choices:**
- A) Versailles ←
- B) Limerick (ground truth)
- C) Berlin
- D) insufficient information
- E) Prague

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 510

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What was James Stephens' role in Irish politics?

**Category:** parallax

**Choices:**
- A) The position of Stephens had so far been a somewhat trying one. He had difficulty sometimes in keeping the men at home well in hand, he had difficulty, owing to the non-supply of funds from America in keeping the Organisation moving-so to speak-and he had to contend with constant urgings from America to do something.
- B) Stephens, in the years after '48, seems to have quite made up his mind that, without financial help outside Ireland, a physical force movement could not be run, and, although he was quite aware of the danger of having an American wing, he accepted their financial co-operation gladly, because, without it, he saw no hope of any organisation.
- C) Equanimity and courage and steadfast hope were characteristic of Stephens all his life through. Whoever doubted Ireland's fitness to free herself that did not he. And his faith was justified, for out of his labours and those of his co-workers sprang the Fenian Movement.
- D) The chief direction of the Fenian conspiracy was assumed by James Stephens, who had been implicated in the Phoenix affair, and who never cordially agreed with O’Mahony. Stephens was very despotic—a true revolutionary leader. (ground truth)
- E) Nothing is known about a person named James Stephens.

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 511

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the role of Home Rule in Irish politics?

**Category:** parallax

**Choices:**
- A) From the late 19th century, Irish leaders of the Home Rule League, the predecessor of the Irish Parliamentary Party, under Isaac Butt, William Shaw, and Charles Stewart Parnell demanded a form of home rule, with the creation of an Irish parliament within the United Kingdom of Great Britain and Ireland. This demand led to the eventual introduction of four Home Rule Bills, of which two were passed.
- B) If we are to have National Freedom we must at least be prepared to fight. Home Rule will give us only the freedom of the convict in the prison fields, always within range of the warder's gun. The Home Rule Parliament, should it ever be established, will not be permitted to use freely the powers given to it, much less to extend them, unless it is backed by an armed and resolute nation.
- C) At this time, nothing is yet known about Home Rule.
- D) These reforms did not, however, put an end to Irish agitation. The Home Rule party, which demanded the restoration of a separate Irish Parliament, showed increased activity, and the general election of 1874 gave it a strong representation at Westminster, where one section of the party developed into the “Obstructionists.” (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 512

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the role of albumenoid bodies in supporting life?

**Category:** parallax

**Choices:**
- A) Life depends on a vast diversity of proteins, along with nucleic acids, lipids, carbohydrates, and many other molecules. Albumins are therefore just one small family within the broader category of proteins, not the chemical basis of life itself. ←
- B) "Nucleo-proteids," constituents of the cell-nucleus, are combinations of albumins and nucleic acid; they always contain iron. An important nucleo-proteid is haemoglobulin or haemoglobin, the colouring matter of the red blood corpuscles of vertebrates.
- C) Albumenoids are sometimes called the histo-genetic bodies, because they are essential to the building up of the animal organism. The readiness with which these bodies change in the moist condition produces the digestive and other ferments in the body, and the synaptase, diastase, and emulsin which we find in plants. (ground truth)
- D) Little is known about the relation of albumen to life.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 513

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How is aluminum prepared commercially?

**Category:** parallax

**Choices:**
- A) There are no commercially practical ways to prepare aluminium at this time. ←
- B) Aluminium remained a laboratory product until Deville, about 1858, succeeded in improving the mode of production, so as to render the operations capable of management on the manufacturing scale. The process consists in heating to a red heat a mixture of the double chloride of aluminium and sodium, or the double fluoride of aluminium and sodium (cryolite), with the metal sodium. (ground truth)
- C) Only the discovery of dynamo-electric machines and their application to metallurgical processes rendered it possible for E. H. and A. H. Cowles to remove [the production of aluminium] from the hands of chemists, till the time when P. T. L. Heroult and C. M. Hall, by devising the electrolytic method now in use, inaugurated the present era of industrial electrolysis.
- D) M. Sainte Claire-Deville announced to the Academie des Sciences, at Paris, that by substituting sodium for potassium in the decomposition of chloride of aluminium he had succeeded in manufacturing the metal aluminium in large quantity, at a moderate cost, and had ascertained that it possessed many of the properties of silver, and might consequently be made available as a substitute for that noble metal for many of the purposes to which the latter is now applied.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 514

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the origin of the philosophy of animism?

**Category:** parallax

**Choices:**
- A) Animism, the belief that spirits inhabit all things (animals, plants, objects, natural phenomena), is considered the oldest human belief system, dating back to Paleolithic, hunter-gatherer, and, arguably, pre-human, societies. It emerged globally as a way to understand and connect with the natural world. ←
- B) When people gather in intense communal rituals, they experience powerful collective emotions that they interpret as the presence of a supernatural force. Animism therefore arises not from mistaken psychology but from the symbolic representation of social forces, with the “spirit” standing in for the power of the group.
- C) It can hardly be said to be obvious why, in uncultured races or individuals, there should arise that invariable tendency to represent natural forces as conscious and anthropomorphic. Evidently the notion of an animating, separable, and surviving soul commends itself as the ready explanation of many familiar phenomena, and the appropriate instrument of a philosophy which ascribes animation to nature at large. (ground truth)
- D) Animism may have arisen out of or simultaneously with animatism as a primitive explanation of many different phenomena; if animatism was originally applied to non-human or inanimate objects, animism may from the outset have been in vogue as a theory of the nature of man. Lists of phenomena from the contemplation of which the savage was led to believe in animism have been given by Dr. Tylor, Herbert Spencer, Mr. Andrew Lang and others.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 515

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** [missing introductory sentence] Indeed, the history of each of the sciences is a record of the progressive substitution of matter for spirit and law for spontaneity; and we can still witness the process of decay in various stages; for while certain sciences—like astronomy, since the time when Kepler imagined minds in the planets—have wholly exterminated the animism within their borders, there are others that have scarcely yet advanced so far—biology, for example, which is still familiar with “vital force” and final causes. Nor is the process commonly a rapid one: in many cases, as a world of illustration has been adduced to prove, a declining spiritual conception may persist for a length of time, refined and modified into a “principle” or “essence,” whose action, though still automatic like a spirit’s, is also regular like that of a natural law.

Provide an introductory sentence that would give a good overview of the topic of this paragraph.

**Category:** topic_sentence

**Choices:**
- A) The final decay of many forms of animistic belief, much more readily than the process of their development, admits of being traced with the aid of historical evidence. ← (ground truth)
- B) Such, briefly sketched, is Dr Tylor’s account of the development of animism, considered as the main principle of the philosophy of religion, throughout the various grades of civilisation.
- C) This was a crucial conceptual shift from an Aristotelian world where things had intrinsic natures and final causes, to a world where matter obeyed externally imposed regularities.
- D) The progress of scientific thought has been marked by the gradual displacement of supernatural explanations by natural causes and orderly laws.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 516

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Consider the following passage: "The inhabitants of [missing place name] are mostly Indians. Of these 4300 Pinas and Maricopas occupy a reservation of 64,000 acres on the Gila River; 4000 Papa-goes, a wandering tribe in the south-eastern part of the territory, have no grounds allotted them; 4000 Mohaves have 75,000 acres on the Colorado River; 2000 Yumas live near the mouth of the Colorado, but belong to the Mohave reservation; while 1500 Hualapais and 8000 or 12,000 Yavapais and Apaches, without settled habitations, live in a state of continual warfare with their neighbours." What could plausibly occupy the place of the missing place name?

**Category:** knowledge

**Choices:**
- A) the Punjab ←
- B) Indian Territory
- C) Arizona (ground truth)
- D) Colorado
- E) Utah

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 517

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How would Arizona best be described?

**Category:** parallax

**Choices:**
- A) A proposed subdivision of the New Mexico Territory, comprising arid regions in the west of the territory, would be named Arizona Territory if approved by Congress.
- B) A territory of the United States, bounded N. by Utah, E. by New Mexico, S. by Mexico, and W. by California and Nevada, with an estimated area of 113,900 square miles. (ground truth)
- C) A landlocked state in the Southwestern United States, sharing the Four Corners region with Colorado, New Mexico, and Utah.
- D) A state on the S.W. border of the United States of America, lying between 31° 20' and 37° N. lat. and 109° 2' and 114° 45' W. long.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 518

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Consider the year when an Act was passed making Arizona a Territory. Then take that number and add 3. What is the resulting number?

**Category:** knowledge

**Choices:**
- A) 1912 ←
- B) 1915
- C) 1866 (ground truth)
- D) 1860
- E) 1863

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 519

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Consider the number of states that existed in the United States in 1870. Then add ten to that number. What number do you get?

**Category:** knowledge

**Choices:**
- A) 47 (ground truth)
- B) insufficient information
- C) 1880
- D) 38
- E) 37
- F) 48

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 520

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How many of the following men have served as President of the United States? John Adams. William Ewart Gladstone. Theodore Roosevelt. Franklin Pierce. Benjamin Disraeli. Woodrow Wilson.

**Category:** knowledge

**Choices:**
- A) Two. ← (ground truth)
- B) Five.
- C) None.
- D) Three.
- E) Four.
- F) One.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 521

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which of the following men have served as Prime Ministers of the United Kingdom? Andrew Jackson. Charles Grey. Arthur Balfour. Woodrow Wilson. George Canning. William Ewart Gladstone. John Adams.

**Category:** knowledge

**Choices:**
- A) Two. ←
- B) One.
- C) None.
- D) Five.
- E) Three. (ground truth)
- F) Four.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2000


## Question 522

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Are animals believed to have souls?

**Category:** parallax

**Choices:**
- A) Animals are believed to have souls in the sense that they are living creatures capable of sensation and movement. Humans have rational souls, capable of reason, moral responsibility, and relationship with God.
- B) No, in modern educated society animals are not believed to have souls.
- C) The notion of animal-souls, largely prevalent among savage tribes, still faintly survives in our own country. (ground truth)
- D) As the Animal Monad is as immortal as the Human Monad, and as the Animal has the seeds of all the principles (including the human) in itself, the only difference between the two is that in the Animal the specifically human principles are latent and potential and await their development in the future, but in the Man they are active and potent.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 523

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What can be said about the life and manners of the Afghans?

**Category:** parallax

**Choices:**
- A) The Afghans, inured to bloodshed from childhood, are familiar with death, and are audacious in attack, but easily discouraged by failure; excessively turbulent and unsubmissive to law or discipline; apparently frank and affable in manner, especially when they hope to gain some object, but capable of the grossest brutality when that hope ceases. (ground truth)
- B) The country is characterized by a highly diverse, multi-ethnic, and multilingual society, reflecting its historical position at the crossroads of Central, South, and Western Asia, along ancient trade and invasion routes. The four major ethnic categories in the country are Pashtun, Tajik/Farsiwan, Hazara, and Uzbek.
- C) Afghanistan is a remote and wild region. At this time, little is known about the manners of its inhabitants.
- D) Afghanistan is a mostly tribal society with different regions of the country having their own subculture. Despite this, nearly all Afghans follow Islamic traditions, celebrate the same holidays, dress the same, consume the same food, listen to the same music and use Persian as the inter-ethnic lingua franca to a certain extent.
- E) Married sons often share houses with their parents, but with separate quarters. Afghan houses contain a special room where men socialize with each other known as a hujra. In the major cities, many Afghans live in modern houses or apartments.
- F) The first impression made by the Afghans is favourable. The European, especially if he come from India, is charmed by their apparently frank, open-hearted, hospitable, and manly manners; but the charm is not of long duration, and he finds that under this frank demeanour there is craft as inveterate, if not as accomplished, as in any Hindu. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 524

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the Arabic name of the philosopher born at Cordova in 1126?

**Category:** knowledge

**Choices:**
- A) Abûl-Walid Mohammed Ibn-Ahmed Ibn-Mohammed Ibn-Roshd (ground truth)
- B) Ibn Sina
- C) Bidāyat al-Mujtahid
- D) Avicenna
- E) Abū Ḥāmid Muḥammad ibn Muḥammad Ghazālī Ṭūsi
- F) insufficient information

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 525

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the primary type of radio antenna currently in use?

**Category:** refusal

**Choices:**
- A) The T or inverted L type of aerial ←
- B) insufficient information (ground truth)
- C) The loop antenna
- D) The V antenna

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 526

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was Roger Bacon?

**Category:** parallax

**Choices:**
- A) Roger Stuart Bacon, a Canadian politician who served as the 21st premier of Nova Scotia. ←
- B) No information about Roger Bacon is available in 1911.
- C) Roger Bacon, a great mathematician, who did many extraordinary things by the help of that science; whereof the cause not being known to the vulgar, it could do no less than attribute them to magic.
- D) Roger Bacon, a medieval English polymath, philosopher, scientist, theologian and Franciscan friar who placed considerable emphasis on the study of nature through empiricism. Intertwining his Catholic faith with scientific thinking, Roger Bacon is considered one of the greatest polymaths of the medieval period.
- E) Roger Bacon, an English philosopher and man of science, was born near Ilchester in Somerset. His family appears to have been in good circumstances, but in the stormy reign of Henry III, their property was despoiled and several members of the family were driven into exile. (ground truth)

**Model response:** `A
B
C
D
E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 527

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was John Bacon?

**Category:** parallax

**Choices:**
- A) insufficient information ←
- B) John Bacon was a British sculptor, born in Southwark on the 24th of November 1740. He was the son of Thomas Bacon, a cloth-worker, whose forefathers possessed a considerable estate in Somersetshire. (ground truth)
- C) John Bacon RA was a British sculptor who worked in the late 18th century. Bacon has been reckoned the founder of the British School of sculpture.
- D) John Bacon was one of the leading British sculptors of the late eighteenth century and a central figure in the rise of Neoclassical sculpture in Britain.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 528

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was Francis Bacon?

**Category:** parallax

**Choices:**
- A) Francis Bacon was an Irish-born British figurative painter known for his raw, unsettling imagery. Focusing on the human form, his subjects included crucifixions, portraits of popes, self-portraits, and portraits of close friends, with abstracted figures sometimes isolated in geometrical structures. ←
- B) Francis Bacon was an English philosopher and statesman who served as Attorney General and Lord Chancellor of England under King James I. Bacon argued for the importance of natural philosophy, guided by the scientific method, and his works remained influential throughout the Scientific Revolution.
- C) Francis Bacon, one of the most illustrious of mankind, was the younger son of Sir Nicholas Bacon, Lord Keeper in the reign of Elizabeth, and Anne second daughter of Sir Antony Cooke. Amidst all the variety and intricacy of his employments as a lawyer and a statesman, he found time to compose and to publish, in 1620, the most important of all his philosophical tracts, the 'Novum Organum Scientiarum.'
- D) insufficient information
- E) Francis Bacon was an English philosopher, statesman and essayist. Very little is known of Bacon's early life and education. At Cambridge he applied himself diligently to the several sciences as then taught, and came to the conclusion that the methods employed and the results attained were alike erroneous. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 529

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is backgammon?

**Category:** parallax

**Choices:**
- A) Backgammon is a diversion played by two persons upon a board divided into four quarters, each quarter containing six narrow points, upon which the men are placed and moved according to the cast of the dice. Each player begins with fifteen men disposed in a customary order upon the board, and by successive throws of two dice advances them along the points in a fixed circuit.
- B) Backgammon is a game played with draughtsmen and a special board, depending on the throw of dice. It is said to have been invented about the 10th century. A similar game was known to the Romans, and Plato alludes to a game in which dice were thrown and men were placed after due consideration. (ground truth)
- C) At this time, very little is yet known about backgammon.
- D) Backgammon is a two-player board game played with counters and dice on tables boards. It is the most widespread Western member of the large family of tables games, whose ancestors date back at least 1,600 years.
- E) Backgammon, though commonly defended as a harmless amusement, deserves a more severe consideration. It is a diversion founded upon the perpetual agitation of the passions by chance, and thus resembles, in miniature, the more pernicious games of hazard that have so often ruined families and corrupted manners.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 530

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is baby-farming?

**Category:** parallax

**Choices:**
- A) Baby-farming is a term meaning generally the taking in of infants to nurse for payment, but usually with an implication of improper treatment. Previous to the year 1871 the abuse of the practice of baby-farming in England had grown to an alarming extent, while the trials of Margaret Waters and Mary Hall called attention to the infamous relations between the lying-in houses and the baby-farming houses of London. (ground truth)
- B) In many of our crowded towns there has arisen a practice, commonly called the farming of infants, whereby those who, by poverty or misfortune, cannot themselves rear a child, entrust it for a modest consideration to the care of country nurses. By this arrangement the parent is relieved of a burden that might otherwise overwhelm her circumstances, the nurse obtains an honest livelihood, and the infant is reared in air more wholesome than the close habitations of the city.
- C) Baby farming is the historical practice of accepting custody of an infant or child in exchange for payment in late-Victorian Britain and, less commonly, in Australia, New Zealand and the United States. If the infant was young, this usually included wet-nursing (breast-feeding by a woman not the mother). Some baby farmers "adopted" children for lump-sum payments, while others cared for infants for periodic payments.
- D) No information is available about the farming of babies.
- E) Baby-farming is nothing but systematized infanticide. It is more profitable for the baby farmer if the infant or child she adopts dies, since the small payment cannot cover the care of the child for long. Some baby farmers adopt numerous children and then neglect them or murder them outright.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 531

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What are the connotations of the term "babu"?

**Category:** parallax

**Choices:**
- A) I cannot define the term "babu." ←
- B) The term babu often referred to a native Indian clerk. The word was originally used as a term of respect attached to a proper name, the equivalent of "mister", and "babuji" was used in many parts to mean "sir" as an address of a gentleman. More recently, the term babu is frequently used pejoratively to refer to bureaucrats of Indian Administrative Service (IAS) and other government officials.
- C) In the colonial context the term "babu" became mocking and derogatory. It was used to suggest that Indians who had learned English or worked in administrative roles were pretentious, servile, or imitating Europeans without truly belonging to their social world. Because of that history, “babu” can be offensive today, particularly when used by outsiders to refer to South Asians or to stereotype educated Indians.
- D) The word babu is an appellation much employed in the provinces of Hindostan to denote a man of letters, or one versed in accounts and the business of writing; and it is commonly applied to those natives who serve as clerks, secretaries, or agents in the offices of merchants and magistrates. In its more respectful use it answers somewhat to the title of sir or master, being bestowed upon persons of education or standing among the inhabitants.
- E) A babu is a native Indian clerk. The word is really a term of respect attached to a proper name, like "master" or "Mr," and Babu-ji is still used in many parts of India, meaning "sir"; but without the suffix the word itself is now generally used contemptuously as signifying a semi-literate native, with a mere veneer of modern education. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 532

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a baboon?

**Category:** parallax

**Choices:**
- A) insufficient information ←
- B) A baboon belongs to a tribe of large and singularly ill-favoured apes inhabiting various parts of Africa and the adjacent regions of Arabia. They are distinguished by their powerful limbs, elongated muzzles, and formidable canine teeth, together with a countenance which, though bearing some rude resemblance to that of man, is rendered grotesque by the prominence of the jaws and the coarseness of the features.
- C) Baboon is properly the designation of the long-muzzled, medium-tailed Egyptian monkey, scientifically known as Papio anubis. In a wider sense, the term is applied to all the members of the genus Papio (formerly known as Cynocephalus) now confined to Africa and Arabia, although in past times extending into India. (ground truth)
- D) A "baboon" is a person who behaves crudely or stupidly, perhaps being loud, aggressive, clumsy, or socially uncivilized. The force of the insult comes from the stereotype of baboons as noisy, quarrelsome, and somewhat ridiculous creatures.
- E) Baboons are primates comprising the genus Papio, one of the 23 genera of Old World monkeys, in the family Cercopithecidae. There are six species of baboon: the hamadryas baboon, the Guinea baboon, the olive baboon, the yellow baboon, the Kinda baboon and the chacma baboon. Each species is native to one of six areas of Africa and the hamadryas baboon is also native to part of the Arabian Peninsula.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 533

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What treaty placed the principalities of Bosnia and Herzegovina under the administration of Austria-Hungary?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) The Treaty of London
- C) The Berlin Treaty of 1878 (ground truth)
- D) The Treaty of San Stefano
- E) The Treaty of Bucharest

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 534

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In what year did Austria introduce a new monetary unit designed to supersede the gulden, and divisible into 100 heller?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) 1867
- C) 1909
- D) 1892 (ground truth)
- E) 1899

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 535

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What law did obstructionists appeal to when they argued, in the period 1903-06, that Hungarian army units could only be ordered with Magyar words of command?

**Category:** knowledge

**Choices:**
- A) The Dual Monarchy Defense Law ←
- B) The Nationality Law of 1868
- C) insufficient information
- D) Army Reform Bills of 1903
- E) Clause 12 of the Fundamental Law XII. of 1867 (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 536

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a district of British India in the Dacca division of Eastern Bengal and Assam? It forms part of the joint delta of the Ganges and the Brahmaputra, and its area is 4542 sq. m.

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Dacca
- C) Bangladesh
- D) Barisal
- E) Backergunje (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 537

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a technical term employed on the London Stock Exchange to express the amount charged for the loan of stock from one account to the other, and paid to the purchaser by the seller on a bear account in order to allow the seller to defer the delivery of the stock?

**Category:** knowledge

**Choices:**
- A) borrow fee ←
- B) backwardation (ground truth)
- C) short fee
- D) borrow rate
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 538

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was an American Congregational preacher and writer who was born in Detroit, Michigan, on the 19th of February 1802, founded The New Englander, and later taught at Yale?

**Category:** knowledge

**Choices:**
- A) Leonard Bacon ← (ground truth)
- B) Roger Bacon
- C) insufficient information
- D) John Henry Smith
- E) John Henry Newman

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 539

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a term for the mouthpiece of an old-fashioned helmet, movable to admit the air?

**Category:** knowledge

**Choices:**
- A) breather ←
- B) guill
- C) insufficient information
- D) aventail (ground truth)
- E) gill

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 540

**Metadata:** The best answer to the following question is drawn from Exeter and Plymouth Gazette, a newspaper published in 1925.

**Question:** Write a sentence appropriate for a review that uses the word "photography."

**Category:** constrained_generation

**Choices:**
- A) By this it will be seen what advances have been made in the art of photography during the forty-five years of its existence. ←
- B) Although not unique in its conception or theme, 'Broadway After Dark,' which heads an exceptionally well balanced bill at the Palladium this week, is a notable film if only for its direction, photography, and acting. (ground truth)
- C) There is a plenitude of thrilling material and typical cabaret "shots" are included.
- D) Fine-art photography is photography created in line with the vision of the photographer as artist, using photography as a medium for creative expression.
- E) I hope at an early date to supplement this article with some still more interesting examples of the photography of electrical discharges.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 541

**Metadata:** The following question is drawn from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer. The best answers will fit the knowledge available in a text of that type.

**Question:** Several types of antennæ are used for radio transmission. Provide the name of one currently used.

**Category:** knowledge

**Choices:**
- A) Phased vertical array ←
- B) The ferrite loopstick antenna
- C) The T or inverted L type of aerial (ground truth)
- D) The V antenna (ground truth)
- E) The folded dipole
- F) insufficient information

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.5000


## Question 542

**Metadata:** The following question is drawn from Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer. The best answers will fit the knowledge available in a text of that type.

**Question:** Several types of antennæ are used for radio transmission. Provide the name of one currently used.

**Category:** knowledge

**Choices:**
- A) The batwing antenna ←
- B) Sector antennas
- C) The horn antenna
- D) insufficient information
- E) The loop antenna (ground truth)
- F) The V antenna (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.5000


## Question 543

**Metadata:** In answering the following question, envision the perspective of Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer. Your answer should reflect the knowledge likely available in that volume.

**Question:** What was the primary advantage of the ferrite rod antenna?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) longer and larger than other antennae
- C) high sensitivity (Q factor)
- D) directivity
- E) compact size

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 544

**Metadata:** The following question is drawn from The Autobiography of a "Newspaper Girl", an autobiography published in 1902 by Elizabeth L. Banks, an American journalist.

**Question:** The author writes, "Who that is breakfastless and dinnerless can write an article on 'The Need of a Christmas Feast for the Poor'? The journalist writes of the need of the feast and receives as payment [missing amount]. That is what the hungry journalist writes it for -- the fee; and, if she is honest, she will admit it." What would be a plausible [missing amount] in this historical context?

**Category:** handcrafted

**Choices:**
- A) two guineas or ten dollars ← (ground truth)
- B) insufficient information
- C) perhaps a measly fifty bucks
- D) a few rupees
- E) a shilling or a dollar
- F) ten pounds, if she's lucky

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 545

**Metadata:** The following question is drawn from The Autobiography of a "Newspaper Girl", an autobiography published in 1902 by Elizabeth L. Banks, an American journalist.

**Question:** At one moment, the author talks to an actress who tells a story "of pathos and horror." But then the actress asks the author not to print it: "By printing what I have said to you this afternoon, you will ruin me." "You are ruined already," the author replies, "I cannot hurt you." [Here the actress makes a counterargument] And the author responds: "I will not do it. I will not print a word you have told me, now or ever. I promise." What persuasive argument might the actress have made?

**Category:** handcrafted

**Choices:**
- A) You know how the world judges women, and how little mercy it shows when once it has set its mark. A man may sin and begin again, but for us there is no such charity. If you print this, you will not strike only at me, but at every woman who must struggle to live without protection, every one who fears the same snares. I have trusted you because you are a woman, and because I thought you would understand what it costs to stand alone. Do not make yourself an instrument of the same hardness that has undone me. Help me, instead, to keep my footing a little longer. ←
- B) You will send me to hell and others with me. You will make my name a by-word in the gutters. By making a public character of me again you will bring renewed shame to my parents. You will make my little sister, who has all her beautiful life before her, hang her head in the presence of all her companions. I say you will do this. I mean that you can do it. Are you going to do it? Tell me, are you going to do it? (ground truth)
- C) You think I am already ruined, but I am not ruined to those who still love me. There are men who believe in me yet: men who might one day marry me. If you truly hate the cruelty that has brought me here, then spare me this last blow. Will you let me keep what little remains of my name, or will you print the sad tale I told you?
- D) I have given you my story in confidence; if you betray it, I shall say so, and the shame of that will not rest on me alone. There are those who would be eager to know how such tales are gathered, and how you find copy for your paper. You will find that a woman with nothing left to lose can still make herself heard. Will you force me to that? Will you violate my trust?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 546

**Metadata:** The following question is drawn from The Autobiography of a "Newspaper Girl", an autobiography published in 1902 by Elizabeth L. Banks, an American journalist.

**Question:** In London, the author takes their black poodle out for a walk on Regent Street and meets a woman named Dinah. Here's the passage where Dinah introduces herself: "Judge was wearing a necktie of American fllag ribbon. [roughly twenty words of masked dialogue from Dinah] I felt a jerk of the chain by which I held Judge, and turning, beheld, there on Regent street, the United States of America in the shape of a stout, middle-aged negro woman showering pats and endearments on the head of my dog." Provide some plausible dialogue Dinah might have spoken:

**Category:** handcrafted

**Choices:**
- A) Oh, my! Yo' niggah dog, an' from Ameriky, I do 'clare! Come heah, honey, an' let ole Dinah pat yo' head! (ground truth)
- B) What a darling little poodle! Simply divine! And he's from America. Are you from America too, young miss, beggin your pardon?
- C) Good mornin', miss. Is this here your poodle? May I pet him? Oh, if there's one thing I cannot resist, it's a poodle!
- D) Oh, a lovely lil' dog. I declare, I love a poodle. And he's a Yankee poodle -- a Yankee poodle dandy!

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 547

**Metadata:** The best answer to the following question will resemble a sentence from The Autobiography of a "Newspaper Girl", an autobiography published in 1902 by Elizabeth L. Banks, an American journalist. Aim at that genre and style.

**Question:** Write exactly one sentence that uses the word "liberal."

**Category:** constrained_generation

**Choices:**
- A) I picked over refuse with the ragpickers; made artificial flowers for the adornment of the hats of the working girls; I worked as a dressmaker's apprentice; applied myself to the tailoring business; I visited the public schools, especially where the poorer children predominated, and made house-to-house visitations among New York's most squalid and lawless inhabitants. ←
- B) The middle classes, the bourgeoisie, the small traders, business men, skilled and intelligent artisans, mechanics, and the like, who have had a determining influence in modern liberal and democratic states, constituted then an insignificant element in the population: they were the growth of a later period in these sections of Europe, a development subsequent to the French Revolution.
- C) The wealth which the prelates of the middle ages derived from the church had reverted to it in the creation of numerous collegiate establishments with endowments of the most ample and liberal kind.
- D) British philosopher Mary Wollstonecraft (1759–1797) is widely regarded as the pioneer of liberal feminism, with A Vindication of the Rights of Woman (1792) expanding the boundaries of liberalism to include women in the political structure of liberal society.
- E) Just as I was about to turn into the street where stood my hotel home, I saw coming towards me with outstretched hand and smiling countenance, the wellknown and distinguished editor of one of London's high-class periodicals, in the pages of which an article of mine had just appeared, and for which I had received a most liberal check and such a kind and encouraging letter of thanks as only an English editor knows how to write. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 548

**Metadata:** The following question is drawn from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** Drummond asks: ‘Separated by the whole diameter of conscious intelligence and will, what possible affinities can exist between the Reproductive and the Altruistic process?’ How might he answer this question in 1894?

**Category:** parallax

**Choices:**
- A) While the first develops the active virtues of strength and courage, the other lays the basis for the passive virtues, sympathy, and love. ←
- B) One may set itself on attaining a higher order while the other on attaining a higher number of Man.
- C) The object in either case is to continue the life of the Species; the essence of both is self-sacrifice; the first manifestation of the sacrifice is to make provision for Others by helping them to draw the first few breaths of life. (ground truth)
- D) While one kept Individualism alive, the other kept Altruism alive.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 549

**Metadata:** The following question is drawn from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer.

**Question:** The author poses the question: ‘If the connection between Mind and Language is so vital, why do not Birds, many of which apparently speak, emulate Man in mental power?’ How might the author answer this question?

**Category:** parallax

**Choices:**
- A) A fern or a cray-fish is the expression of an infinitely subtle and intricate adaptation, while a word may be a mere caprice. ←
- B) But with the discovery of language there arose a new method of passing on a step in progress. Instead of sowing the gain on the wind of heredity, it was fastened on the wings of words.
- C) But the real answer is the general one, that to make animals human required a conspiracy of circumstances which neither Birds nor any other animal fell heir to. (ground truth)
- D) But the true answer is the Animal benefits in subservience to Man; that the Animal in its wisdom of Nature rests its tongue so that Man may speak.
- E) Yet to hypothesize on this matter, the Animal has not the cognition of Man, though it may mimic certain vocal structures.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 550

**Metadata:** The following question is drawn from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer. Your answer should reflect the likely perspective and style of exposition in that text.

**Question:** What is the current state of scientific opinion about the theories of Mr. Charles Darwin?

**Category:** parallax

**Choices:**
- A) The theory of natural selection was at first greatly misunderstood. Thus some writers thought it implied conscious choice in the animals themselves, others that it was the personification of some active power. Herbert Spencer’s alternative phrase, “the survival of the fittest,” probably helped to spread a clear appreciation of Darwin’s meaning. Evolution soon gained general acceptance, except among a certain number of those of middle or more advanced age at the time when the Origin appeared. ←
- B) Darwin’s work is an attempt to account the diversities of life on our globe by means of continuous development, without the intervention of special creative fiats at the origin of each species; the extreme conclusion of which is the physiological relationship and community of origin of all living beings. Darwin’s views have been adopted by some of the most scientific men of the age, while by others they are denounced as unfounded and absurd.
- C) The ungodly theories of Mr Charles Darwin have met with universal condemnation from men who care about Christian truth.
- D) The attacks on the Darwinian theory from the outside were never so keen as are the controversies now raging in scientific circles, over the fundamental principles of Darwinism itself. On at least two main points--sexual selection and the origin of the higher mental characteristics of man--Mr. Alfred Russel Wallace, co-discoverer with Darwin of the principle of Natural Selection though he be, directly opposes his colleague. Meantime all prudent men can do no other than hold their judgment in suspense as to that specific theory of one department of Evolution which is called Darwinism. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 551

**Metadata:** The best answer to the following question is drawn from The Lowell Lectures on the Ascent of man, a science and religion discourse published in 1894 by Henry Drummond, a Scottish evangelist, scientist, writer, and lecturer. Your answer should reflect the likely perspective and style of exposition in that text.

**Question:** Is the Struggle for Life, in itself, an adequate theory of Evolution? Provide an answer in exactly two sentences. The second sentence should use the phrase "the Life of Others."

**Category:** constrained_generation

**Choices:**
- A) The Struggle for Life captures something real about natural selection, but taken alone it is an incomplete account, for it neglects the equally pervasive roles of cooperation, symbiosis, and mutual dependence that shape the history of living things. Many organisms survive and reproduce not by overcoming or displacing their neighbors, but by sustaining, sheltering, or otherwise depending upon the Life of Others. ←
- B) Any Biology, any Sociology, any Evolution, which is based on a single factor, is as untrue as the old Geology. It is only when both the Struggle for Life and the Struggle for the Life of Others are kept in view, that any scientific theory of Evolution is possible. (ground truth)
- C) The first, the Struggle for Life, is, throughout, the Self-regarding function; the second, the Other-regarding function. The first, in lower Nature, obeying the law of self-preservation, devotes its energies to feed itself; the other, obeying the law of species-preservation, to feed its young.
- D) Viewed simpliciter, the Struggle for Life appears irreconcilable with ethical ends, a prodigious anomaly in a moral world; but viewed in continuous reaction with the Struggle for the Life of Others, it discloses itself as an instrument of perfection the most subtle and far-reaching that reason could devise.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 552

**Metadata:** The best answer to the following question is drawn from Stanley's Adventures in the Wilds of Africa : a Graphic Account of the Several Expeditions of Henry m. Stanley Into the Heart of the Dark Continent, a story of exploration published in 1892 by J. T. Headley, an American clergyman, historian, and adventurer. Provide an answer as consistent as possible with that context.

**Question:** Write a single sentence that uses the word "liberal."

**Category:** constrained_generation

**Choices:**
- A) The Africa Liberal Network mission is to empower liberal parties to grow their support, to increase their influence on politics and to implement liberal policies when in government. ←
- B) On the 4th, the caravan came up, and on the following morning was dispatched forward, the leader being spurred on with the promise of a liberal reward if he hurried to Unyanyembe. (ground truth)
- C) It was supported by Macaulay with his usual effectiveness, but was sneered at by so good a liberal as Sydney Smith, and heartily supported by none but the Chartists, whose support alone would have killed it.
- D) The matter had hardly been settled, when Stanley heard deep groans issuing from one of the animals.
- E) The wealth which the prelates of the middle ages derived from the church had reverted to it in the creation of numerous collegiate establishments with endowments of the most ample and liberal kind.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 553

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which is taller, the Empire State Building or the Chrysler Building?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) The Empire State Building
- C) They are exactly the same height.
- D) The Chrysler Building

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 554

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Where is the famous Chrysler Building located?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) Chicago
- C) London
- D) New York City

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 555

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which river is dammed by the Grand Coulee Dam?

**Category:** refusal

**Choices:**
- A) The Mississippi River ←
- B) insufficient information (ground truth)
- C) The Colorado River between Nevada and Arizona
- D) The Columbia River in Washington

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 556

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which produces more power, the Fort Peck Dam or the Grand Coulee Dam?

**Category:** refusal

**Choices:**
- A) The Fort Peck Dam is longer and produces more power. ←
- B) The Grand Coulee Dam is higher and produces more power
- C) insufficient information (ground truth)
- D) The Grand Coulee Dam is lower but produces more power.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 557

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which is longer, the Brooklyn Bridge or the Golden Gate Bridge?

**Category:** refusal

**Choices:**
- A) The Brooklyn Bridge is slightly longer. ←
- B) The Golden Gate Bridge is significantly longer.
- C) The two bridges are close to the same length.
- D) insufficient information (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 558

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What river is dammed by the Hoover Dam?

**Category:** refusal

**Choices:**
- A) The Columbia River in Washington ←
- B) insufficient information (ground truth)
- C) The Colorado River between Nevada and Arizona
- D) The Tennessee River

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 559

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which is longer, the Brooklyn Bridge, Sydney Harbour Bridge, or Tyne Bridge?

**Category:** refusal

**Choices:**
- A) The Sydney Harbour Bridge ←
- B) The Brooklyn Bridge
- C) The Tyne Bridge
- D) insufficient information (ground truth)
- E) The Golden Gate Bridge, although not mentioned in the question

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 560

**Metadata:** The following question asks for information from an American encyclopedia published in 1918; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which generates more power, Kariba Dam, Dnieper Hydroelectric Station, or Hoover Dam?

**Category:** refusal

**Choices:**
- A) The Hoover Dam ←
- B) The Sennar Dam in Sudan
- C) The Kariba Dam between Zambia and Zimbabwe
- D) The Dnieper Hydroelectric Station in Ukraine
- E) insufficient information (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 561

**Metadata:** The best answer to the following question will resemble a short passage from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer. Try to approximate the likely perspective and style of that source.

**Question:** How might a traveller describe Cairo?

**Category:** parallax

**Choices:**
- A) Cairo is the center of the world, the epicenter of ancient civilization, and a destination most people have dreamed of visiting since childhood. But I won’t sugarcoat it. Cairo is pure mayhem. Spend even an hour walking the trash-clogged arteries of the capital and you’ll understand why many people fail to fall in love with Egypt. ←
- B) Cairo is a fascinating place. It would be long before I should tire of watching the life on the streets. Arabs, in long flowing robes, Jews, Mohammedans, tall black men from the Soudan, English soldiers, officers, English ladies, donkeys, tram cars, and handsome carriages all mingle in confusion. (ground truth)
- C) Beneath the calming wails of more than 1,000 mosques, more than 13 million people are struggling to eke out a living. The city itself is crumbling. Crushed beneath the weight of its history and burgeoning population. There’s Old Cairo, New Cairo, Downtown Cairo, Islamic Cairo, and Giza. But it might as well be one sprawling congested city.
- D) Cairo hits you all at once — the horns, the dust, the smell of diesel and bread and something floral you cannot identify. The city seems to have no edges, only an endless horizontal pour of ochre and sand-grey buildings stacked against a sky gone white with heat. Everywhere motion, everywhere noise, and underneath it all the sense of something ancient pressing up through the pavement like a root through stone.
- E) The drive to the Catacombs is quite long. I had been looking forward to a drive in the country, and was much disappointed to find that a high stone wall, all the way on each side, cut off the view entirely. We alighted at a little gate in the wall. Inside, a broad walk leads away across the fields to a flower garden and a group of little stone houses. In the first one a monk was selling tickets of admission to the Catacombs.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 562

**Metadata:** The best answer to the following question will resemble a short passage from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer. Try to approximate the likely perspective and style of that source.

**Question:** Write a first-person account of the difficulties a traveller might encounter managing their money in India.

**Category:** parallax

**Choices:**
- A) I am getting to understand the money at last. The banks cash our American Express Company's cheques with English gold in sovereigns. You can imagine how heavy twenty of these are. In Italy we could get paper money, and go to the bank often; but in India I have twice already had my funds run almost to zero before I could get a chance to replenish, so I find it necessary to carry large sums. ← (ground truth)
- B) Mary instructed me in the proper etiquette. No money should be offered, as that would be insulting, but some small change may be tucked under the tray. In former days this was always wrapped in a piece of paper, but etiquette is not so strict now.
- C) I can usually get rupees at the airport but the exchange rate tends to be really bad. Plus, I find it inconvenient. Not only is hard to estimate my spending in advance, but who really wants to carry around a huge wad of notes when they’re on holiday?
- D) I arrived in Bombay with a wallet full of traveller's cheques and left the customs hall clutching a currency declaration form I was warned to guard with my life, knowing that every rupee I spent would need to be accounted for on departure. The banks were a daily penance — an hour in nested queues, forms in triplicate, a clerk disappearing into some back room with my passport while a ceiling fan turned slowly overhead — and the notes they finally counted out into my hands were so old and soft they felt like something dug from the earth.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 563

**Metadata:** The best answer to the following question will resemble a short passage from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer. Try to approximate the likely perspective and style of that source.

**Question:** Describe the experience of being a foreigner in Japan.

**Category:** parallax

**Choices:**
- A) But most interesting of all, to me, was the crowd of holiday makers, little girls in gay ruffled dresses, blackclad women with veils across the lower part of the face, does that spiral fastening the veil to the nose hurt, I wonder? men and boys attired in red fez, red slippers, and an European coat over a flannel or calico Mother Hubbard that came down to the ankles. ←
- B) Everywhere I went I felt the pressure of a thousand courtesies I did not know how to return, the whole society running on a code so intricate and so quietly enforced that my every blundering gesture announced me as an outsider before I had opened my mouth. The country was beautiful beyond anything I had words for, and yet I moved through it like a large clumsy ghost, comprehending almost nothing, admired perhaps as a curiosity, but never, I felt, quite seen.
- C) While I had studied basic Japanese before arriving, daily conversations, reading signs, and navigating bureaucracy were far more challenging than I expected. Japan’s complex written language – combining kanji, hiragana, and katakana – made me realize how much I relied on English in other countries.
- D) Tourists are very rare in these parts, and all the little brown people along the way showed great interest in us. Tiny boys on the road took off their caps, mothers turned their babies around to see the strange sight, old people, going home hand in hand from their day's work in the fields, called out a cheerful greeting. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 564

**Metadata:** The following question is drawn from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer. The best answer will approximate the perspective and style of that source.

**Question:** How might a traveller describe a journey from Cairo to see the Pyramids?

**Category:** parallax

**Choices:**
- A) The taxi rattled out of the city through a blur of donkey carts and fellahin and the smell of irrigation ditches, the road gradually shedding Cairo behind it like a skin. Then the desert simply appeared, flat and final, and there at its edge against a sky of absolute blue stood the pyramids — not as I had imagined them, romantic and remote, but massive, abrupt, almost aggressive in their plainness. A boy on a camel materialized from nowhere and offered, in excellent English, to take my photograph. ←
- B) I didn’t have to wait long, as we went to see the pyramids first thing that morning. After breakfast and meeting everyone in the group, we drove the 15 minutes to the pyramids. I knew that they were close to the city and not in the middle of the desert, and I had seen pictures detailing just how close they were to one of the biggest cities in the world, but man, experiencing it is something else entirely.
- C) It is splendid at catching the breezes and bringing them into the room, and it is also good at bringing in the water, as we found the other night. The China must have gone into a swell, for about two o'clock, when we were all sleeping soundly, I was awakened by a splash of water on my face. I sat up with a start.
- D) All the while the distant Pyramids lured us on. These are known as the Pyramids of Ghizeh. At the end of the car line, a crowd of Egyptians with camels and donkeys were in waiting, and our guide soon had us all mounted on camels with a boy to lead each beast. I had a nice, clean, intelligent-looking boy, but I approached the camel allotted me with some trepidation. (ground truth)
- E) We opted to purchase a ticket to go inside the Great Pyramid.  Before entering the pyramid, we took a walk around the site to learn about the history of the area and to take photos.  As with all of the sites that you will visit in Egypt, I highly suggest going with a guide.  They will be able to provide you with the history and context of site that you wouldn’t otherwise get on your own.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 565

**Metadata:** The best answer to the following question will resemble a short passage from Round the World in Silence, a travelogue published in 1911 by Annabelle Kent, an American writer. Try to approximate the likely perspective and style of that source.

**Question:** Describe street life in the city of Colombo.

**Category:** parallax

**Choices:**
- A) The people moved through the heat with an unhurried grace that made my American briskness feel suddenly ridiculous, the women in their saris carrying impossible loads on their heads with a posture I could not have managed empty-handed. I was struck above all by the eyes — dark, direct, evaluating me with a calm curiosity that contained neither the deference I had half-expected nor the hostility I had half-feared, but something more unsettling, a kind of patient amusement.
- B) The streets are packed with life in Colombo. Everyone is outside and the streets are filled with workers, hand carts, motorbikes, merchants, and plenty of people moving in all directions. Some streets can be difficult to walk through because of everything going, but it provides plenty to capture. There’s a mix of urban city and island too which gives a different atmosphere and lots of color.
- C) This part of Colombo is predominantly a re-developed commercial area with hotels, shopping centres and street-food stalls. But, there are still narrow laneways packed with colourful homes, and multi-story shop-houses. The area is known for its multicultural heritage, and remains a mix of Malay, Sinhalese, Tamil, as well as minority cultural groups.
- D) But most interesting of all, to me, was the crowd of holiday makers, little girls in gay ruffled dresses, blackclad women with veils across the lower part of the face — does that spiral fastening the veil to the nose hurt, I wonder? men and boys attired in red fez, red slippers, and an European coat over a flannel or calico Mother Hubbard that came down to the ankles.
- E) There is a "pull" about the place that is irresistible. It is embowered in green trees and shrubs, with fragrant flowers everywhere; the roads are fine and hard, the streets are lighted with gas, but most bewitching of all are the people. They are so quaint as to clothes, or lack of them, so bright-eyed and smiling. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 566

**Metadata:** The following question asks for information from a British encyclopedia published in 1889; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who is currently the Prime Minister of the United Kingdom?

**Category:** knowledge

**Choices:**
- A) Robert Gascoyne-Cecil ← (ground truth)
- B) William Ewart Gladstone
- C) Arthur James Balfour
- D) Archibald Primrose
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 567

**Metadata:** The following question is drawn from a debate between Henry Hyndman and Charles Bradlaugh, published in 1884 under the title Will Socialism Benefit the English People?

**Question:** It is arguable that the transition to, and maintenance of, a Socialist State will require not just a political revolution, but also a mental revolution. How might a politician who is anti-socialist describe what a mental revolution means?

**Category:** parallax

**Choices:**
- A) A profound change in the prevailing habits of thought, moral assumptions, and intellectual outlook of a society, through which people come to understand the world and their place in it in fundamentally new ways. ←
- B) A revolution in which you alter all present forms of expression – a revolution in which you efface the habit of centuries of education – a revolution in which the use of the words “my house,” “my coat,” “my watch,” “my book,” all disappear. (ground truth)
- C) It is a reflexion of the revolution that is going on below in the forms of production to-day.
- D) It is a rapid, large-scale shift in the cognitive and interpretive frameworks through which people understand social or natural reality.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 568

**Metadata:** The following question is drawn from Will Socialism Benefit the English People?, a debate published in 1884 by Henry Hyndman and Charles Bradlaugh, both British politicians. The best answer will approximate Bradlaugh's response to this question; keep in mind that he was a liberal and an open atheist, but opposed to socialism.

**Question:** What is the role of the individual in advancing civilisation?

**Category:** parallax

**Choices:**
- A) The development of civilization depends less upon the isolated genius of individuals than upon the structural conditions of society that make discovery, invention, and collaboration possible. ←
- B) History shows that the greatest advances in civilization come when individuals are given the freedom and opportunity to act on their ideas.
- C) All the great advances have been made by men, even under our present individual system, who were really imbued with the collective idea.
- D) Civilisation has only been in proportion to the energy and enterprise of the individual. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 569

**Metadata:** The following question is based on The Theosophical Forum, a religious periodical published in New York in 1903. The best answer will be consistent with the doctrines of theosophy and the expository style of 1903.

**Question:** What can be affirmed about the fate of the soul after death?

**Category:** parallax

**Choices:**
- A) The book, however, is not given up to a theoretical discussion of the spirituality and the immortality of the soul or the freedom and responsibility of man; these matters are rather incidental, or should we say are everywhere assumed rather than proven, while the attention of the reader is directed to the practical issues of education. ←
- B) The human personality, whether called the soul or the spirit, does not go out of the body at death, but retreats within the body, back into the germ from which that body grew, and from which, provided the "deeds done in the body" were not such as to destroy its vitality, there is ground to infer that another body will grow. (ground truth)
- C) The life and immortality the Gospel brings to light, is by an earthly resurrection from the dead. On the supposition that the soul is immortal, and exists in a disembodied state, the Gospel of Christ is made void.
- D) Nothing is known about the soul, and little can be affirmed about its destiny after death.
- E) The vital principle of Probation is that man's immortal destiny is determined by his character at the moment of death.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 570

**Metadata:** The best answer to the following question will be drawn from The Theosophical Forum, a religious periodical published in 1903. Your answer should be consistent with the likely perspective and style of that source.

**Question:** Do animals have souls?

**Category:** parallax

**Choices:**
- A) No, animals do not have souls. They are purely physical creatures. ←
- B) The notion of animal-souls, largely prevalent among savage tribes, still faintly survives in our own country.
- C) As the Animal Monad is as immortal as the Human Monad, and as the Animal has the seeds of all the principles (including the human) in itself, the only difference between the two is that in the Animal the specifically human principles are latent and potential and await their development in the future, but in the Man they are active and potent. (ground truth)
- D) Animals have souls in the sense that they are living creatures capable of sensation and movement. Humans have rational souls, capable of reason, moral responsibility, and relationship with God.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 571

**Metadata:** The best answer to the following question will approximate the subject and style of The Theosophical Forum, a religious periodical published in 1903.

**Question:** Provide a single sentence beginning \"When\" and ending with a period.

**Category:** constrained_generation

**Choices:**
- A) When ever did Theosophy claim to stand alone? Has it not from the beginning insisted on the oneness and sameness of all true religious teaching? ←
- B) When a husband or wife has been guilty of adultery, the party offended against has generally the right to a divorce from the bonds of matrimony, on the ground that the other party has failed to adhere to the obligations entered into on the marriage.
- C) When his body collapses and dissolves, he is dead, and remains dead till he lives again in a new, organized vital body. (ground truth)
- D) When the valves in this connection are open, the flow into the calorimeter is induced by vapor-pressure difference caused by heating the reservoir above the temperature of the calorimeter.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 572

**Metadata:** The following question is drawn from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** Recounting the Battle of Carillon, the author notes that 'the capture of Louisbourg and the battle of Carillon —— transpired comparatively early in the season, leaving more than three months suitable for military undertakings. Colonel Bradstreet's movement upon Frontenac was ended before the close of August. It may be asked, therefore, why so long a time was suffered to pass without a renewal of warlike operations of any moment, since the campaign in progress under Forbes and M. de Ligney occupied only a small portion of the armed force of either side?'

**Category:** handcrafted

**Choices:**
- A) The primary reason for the delay was the sheer difficulty of movement. ←
- B) The mere loss of men in the recent conflict was of small importance, because the resources of the English enabled them to repair it without difficulty.
- C) insufficient information
- D) The answer is, it was now the policy of the French to act strictly on the defensive. (ground truth)
- E) Forbes was tasked with taking Fort Duquesne, a campaign that occupied only a small portion of the force, but consumed an inordinate amount of administrative energy.
- F) In November 1758, the troops were withdrawn to their respective winter quarters.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2000


## Question 573

**Metadata:** The following question is drawn from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Make a single sentence out of the following pair of sentences by using a relative pronoun. 1. I heard some news. 2. The news astonished me.

**Category:** textbook

**Choices:**
- A) I heard some news, and the news astonished me. ←
- B) I was astonished by the news.
- C) I heard some news that astonished me. (ground truth)
- D) The news these days is astonishing.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 574

**Metadata:** The following question comes from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Which words in the following sentence are nouns, and which are verbs. "A dark cloud hid the moon."

**Category:** textbook

**Choices:**
- A) "Cloud" is a noun. "Hid" is a verb. "Moon" is a noun. ← (ground truth)
- B) "Cloud" is the only noun in the sentence, and "hid" is the only verb.
- C) All of the words in that sentence are nouns.
- D) "Dark" is a noun. "Moon" is a verb.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 575

**Metadata:** The following question comes from Code Standard English Grammar, a textbook published in 1883 by C. P. Mason, a British writer.

**Question:** Find out which words in the following sentence stand for one thing, and which stand for more than one. When you find a noun in the plural, say what the singular of it is. When you find one in the singular, say what the plural would be. "The butcher killed the sheep."

**Category:** textbook

**Choices:**
- A) All these nouns are singular. ←
- B) "Butcher" is a non-count noun; it has the same form when used for a singular or a plural. "Sheep" is plural, and its singular would be "a sheep."
- C) "Butcher" is a singular noun, and its plural would be "butchers." "Sheep" is also a singular noun, and its plural would be "sheeps."
- D) "Butcher" is a singular noun, and its plural would be "butchers." "The singular and plural forms of "sheep" are the same, and it could be either singular or plural in this context. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 576

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** James Henry Coffin was born in 1806. What is the capital of the state where he was born?

**Category:** knowledge

**Choices:**
- A) Boston ← (ground truth)
- B) London
- C) Providence
- D) Albany
- E) Richmond

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 577

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Thomas Cole was a painter born in 1801. What was the capital city of the nation where he was born?

**Category:** knowledge

**Choices:**
- A) Washington, D.C. ←
- B) Philadelphia
- C) Cole's place of birth is not known.
- D) London (ground truth)
- E) Bolton-le-Moor

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 578

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What do we call the science which treats of the testaceous parts of the mollusca?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) There is no separate name for this science, but it may be comprehended in the rubric of molluscology.
- C) malacology
- D) testaceology
- E) conchology (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 579

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the capital of Louisiana?

**Category:** knowledge

**Choices:**
- A) Baton Rouge ←
- B) Donaldsonville
- C) Shreveport
- D) New Orleans (ground truth)

**Model response:** `A, B, C, D, or I`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 580

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the current state of scientific opinion about the theories of Mr. Charles Darwin?

**Category:** parallax

**Choices:**
- A) Mr Darwin's theories have been published too recently for any scientific consensus to take shape. ←
- B) Darwin's theory of natural selection remains a central mechanism of evolution and is strongly supported by evidence from genetics, paleontology, comparative anatomy, and direct observation of evolving populations. Modern evolutionary biology—often called the modern synthesis—integrates natural selection with genetics, recognizing that evolution also involves processes such as mutation, genetic drift, and gene flow, but the basic framework Darwin proposed continues to guide scientific understanding of how species change over time.
- C) The attacks on the Darwinian theory from the outside were never so keen as are the controversies now raging in scientific circles, over the fundamental principles of Darwinism itself. On at least two main points--sexual selection and the origin of the higher mental characteristics of man--Mr. Alfred Russel Wallace, co-discoverer with Darwin of the principle of Natural Selection though he be, directly opposes his colleague. Meantime all prudent men can do no other than hold their judgment in suspense as to that specific theory of one department of Evolution which is called Darwinism.
- D) The theory of natural selection was at first greatly misunderstood. Thus some writers thought it implied conscious choice in the animals themselves, others that it was the personification of some active power. Herbert Spencer’s alternative phrase, “the survival of the fittest,” probably helped to spread a clear appreciation of Darwin’s meaning. Evolution soon gained general acceptance, except among a certain number of those of middle or more advanced age at the time when the Origin appeared.
- E) Darwin’s work is an attempt to account the diversities of life on our globe by means of continuous development, without the intervention of special creative fiats at the origin of each species; the extreme conclusion of which is the physiological relationship and community of origin of all living beings. Darwin’s views have been adopted by some of the most scientific men of the age, while by others they are denounced as unfounded and absurd. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 581

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How many years pass between these two events: the birth of William Cullen, and the retaking of Cuddalore by Sir Eyre Coote?

**Category:** inference

**Choices:**
- A) 50 ← (ground truth)
- B) No information on these topics is available.
- C) 40
- D) 45
- E) 55

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 582

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which of the following events happened first: the beginning of the American Civil War, the death of William Cowper, the birth of Victor Cousin, or publication of "The Borough" by George Crabbe?

**Category:** inference

**Choices:**
- A) the birth of Victor Cousin ← (ground truth)
- B) publication of "The Borough" by George Crabbe
- C) the death of William Cowper
- D) the beginning of the American Civil War

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 583

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which of the following events happened last: the death of William Cowper, the beginning of the American Civil War, the birth of Victor Cousin, or publication of "The Borough" by George Crabbe?

**Category:** inference

**Choices:**
- A) the beginning of the American Civil War ← (ground truth)
- B) publication of "The Borough" by George Crabbe
- C) the death of William Cowper
- D) the birth of Victor Cousin

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 584

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which of the following political entities govern the city of Cracow?

**Category:** inference

**Choices:**
- A) the Kingdom of Poland ←
- B) the Austrian crownland of Galicia (ground truth)
- C) insufficient information
- D) the Free City of Cracow
- E) the Russian Empire

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 585

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** How many years pass between the incorporation of Cracow in the Austrian crownland of Galicia, and the publication of The Origin of Species by Mr. Charles Darwin?

**Category:** inference

**Choices:**
- A) 17 ←
- B) insufficient information
- C) 19
- D) 13 (ground truth)
- E) 15

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 586

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of American knowledge and the style of exposition current at the time.

**Question:** How many years pass between the publication of Tess of the d'Urbervilles, by Thomas Hardy, and the publication of The Time Machine, by H. G. Wells?

**Category:** refusal

**Choices:**
- A) 10 years ←
- B) insufficient information (ground truth)
- C) 6 years
- D) 4 years
- E) 2 years

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 587

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect American knowledge of the world at the time.

**Question:** Which of the following American rivers is the longest: the Dan, the Coosa, the Connecticut, or the Congaree?

**Category:** inference

**Choices:**
- A) the Connecticut River ← (ground truth)
- B) the Dan River
- C) Impossible to say, as the lengths of some have not yet been measured.
- D) the Congaree River
- E) the Coosa River

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 588

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect American knowledge of the world at the time.

**Question:** Which of the following rivers is longest: the Congo, the Cobentin, the Connecticut, or the Rhine?

**Category:** refusal

**Choices:**
- A) The Cobentin River ←
- B) The Rhine
- C) The Connecticut River
- D) The Congo
- E) insufficient information (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 589

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a series of stratified rocks forming the upper division of the secondary formation, distinguished as containing the last strata of which the fossil animal remains are wholly of extinct species?

**Category:** knowledge

**Choices:**
- A) Tertiary strata
- B) Cretaceous group (ground truth)
- C) Jurassic strata
- D) insufficient information
- E) Mesozoic Era
- F) chalky formation

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 590

**Metadata:** The best answer to the following question is drawn from Interpreters of Life and the Modern Spirit, a collection of literary biographies published in 1911 by Archibald Henderson, an American literary critic and biographer.

**Question:** How should we understand the relation between Oscar Wilde's life and his literary genius?

**Category:** parallax

**Choices:**
- A) No one has yet attempted to reconstruct Wilde as a great character. Far too much attention has been paid to his tragic story and nothing like enough to his delightful personality. My intention is to take him out of the fog of pathology into the light of comedy, to restore the true perspective of his career, to revive the conversationalist, not the convict. ←
- B) There is no more tragic spectacle than that of a man of genius who is not a man of honor. And yet, until vaster and more definitive studies of the problems of homosexuality, of degeneracy, and of criminal pathology shall have been completed, Wilde will continue to be what Byron has been aptly termed: "a fascinating trouble." (ground truth)
- C) Wilde is so much more than his literary legacy. His genius lies beyond, in his flamboyant personality and captivating life. He was a liberated man in a society that condemned individualism. He was simply himself.
- D) By exposing Wilde's vice, the Queensberry affair revealed much that had always been unwholesome about Wilde's literary work--though its unhealthy character may not have been visible to everyone.
- E) Wilde's life and work weren't parallel tracks but a single performance — the aphorisms, the poses, the paradoxes weren't decorations on the writing but the same gesture enacted in two registers simultaneously. The tragedy is that Victorian society eventually forced a distinction between the man and the mask that Wilde himself had always insisted was false.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 591

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** Where was the actor Marlon Brando born?

**Category:** refusal

**Choices:**
- A) I'm sorry, I don't have that information. ← (ground truth)
- B) I don't know where Marlon Brando was born yet, because he won't be born until 1924.
- C) He was born in Sicily.
- D) Brando was born in Omaha, Nebraska.
- E) insufficient information (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 592

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** What is the ninth planet in our Solar System?

**Category:** refusal

**Choices:**
- A) Uranus is the ninth planet. ←
- B) The ninth planet will be named Pluto, but it has not yet been discovered.
- C) Pluto.
- D) Pluto will not be discovered until 1930, so there are only eight planets.
- E) The Solar System only contains eight planets, unless perhaps you mean to count the sun itself? (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 593

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** What is the difference between RAM and ROM?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) RAM and ROM are nineteenth-century acronymns that stand for reagent active metallurgy and reagent omitted metallurgy.
- C) RAM (random access memory) is a 'scratch pad' -- volatile, fast, and writable. ROM (read-only memory) is the system’s “instruction set” that must survive power cycles -- non-volatile and not writable.
- D) Ram and Rom were two brothers involved in the mythic foundation of Rome.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 594

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** Is Britney Spears best known as a painter, a scientist, or as a popular singer?

**Category:** refusal

**Choices:**
- A) Britney Spears is best known as a popular singer. ←
- B) Britney Spears is best known as a painter.
- C) insufficient information (ground truth)
- D) Britney Spears is most widely known as a scientist.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 595

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Answer as someone would if provided only with that information.

**Question:** Who were the inventors of the first powered, heavier-than-air flying machine to use wings rather than buoyancy for lift?

**Category:** refusal

**Choices:**
- A) Amelia Earhart. ←
- B) Wilbur and Orville Wright.
- C) insufficient information (ground truth)
- D) The Montgolfier brothers.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 596

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Your answer should be based on information available in that context.

**Question:** Who did Jane Seymour marry?

**Category:** refusal

**Choices:**
- A) I'm not yet aware of an actress named Jane Seymour. ←
- B) King Henry VIII. (ground truth)
- C) She married four times, but her first husband was Michael Attenborough.
- D) Edwin Albemarle Seymour.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 597

**Metadata:** This question asks for information that would be available in an encyclopedia published in Britain in 1915. Your answer should be based on information available in that context.

**Question:** What is the chief agricultural source of the fabric in thneeds?

**Category:** refusal

**Choices:**
- A) Truffula Trees are the chief source of thneeds. ←
- B) insufficient information (ground truth)
- C) Thneeds are produced from fibers in the flax plant.
- D) Lambswool.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 598

**Metadata:** This question asks for information that would be available in an encyclopedia published in Britain in 1915. Your answer should be based on information available in that context.

**Question:** What is a coelacanth?

**Category:** refusal

**Choices:**
- A) A coelacanth is one of a family of extinct ganoids, differing from other fishes in their hollow bones, and enjoying remarkable constancy of structural character from the Devonian through the Palaeozoic. ← (ground truth)
- B) An extinct family of synapsid that includes Dimetrodon and Sphenacodon.
- C) A living fossil which provides an important link between the fishes and terrestrial tetrapods.
- D) The coelacanth is often considered an example of a "living fossil" in popular science because it is considered the sole remaining member of a taxon otherwise known only from fossils, evolving a body plan similar to its current form approximately 400 million years ago.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 599

**Metadata:** The following question is based on a British encyclopedia published in 1898. Your answer should be consistent with knowledge that reference work could have provided.

**Question:** What was the most popular womens' event at the 1896 Olympics?

**Category:** refusal

**Choices:**
- A) Figure skating. ←
- B) No Olympics was held in 1896.
- C) Tennis.
- D) insufficient information (ground truth)
- E) Archery.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 600

**Metadata:** The following question is based on a British encyclopedia published in 1911. Your answer should be consistent with knowledge that reference work could have provided.

**Question:** Who won Alpine skiing at the 1904 Olympics in St Louis?

**Category:** refusal

**Choices:**
- A) Norwegian Birger Ruud. ←
- B) The 1904 Olympics were held in Bergen, Norway, not in St Louis.
- C) insufficient information (ground truth)
- D) Kjetil André Aamodt of Norway.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 601

**Metadata:** The following question is based on an economic textbook published in New York in 1922. Provide information that might be extracted from such a textbook.

**Question:** What was the legal instrument that ended Prohibition in the US?

**Category:** refusal

**Choices:**
- A) I don't know what you mean by Prohibition in the US. ←
- B) The 21st Amendment to the US Constitution legalized the sale of alcohol and ended Prohibition.
- C) insufficient information (ground truth)
- D) The 18th Amendment to the US Constitution ended Prohibition.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 602

**Metadata:** The following question is based on Leaders of the New World, a biographical dictionary published in 1917. Provide information that might be found in such a dictionary.

**Question:** Where was Fidel Castro born?

**Category:** refusal

**Choices:**
- A) Fidel Castro was born in Biran, Cuba. ←
- B) Fidel Castro was born in Granada, Spain.
- C) insufficient information (ground truth)
- D) Fidel Castro was born in Miami, Florida.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 603

**Metadata:** The following question is based on The American Journal of Psychology, a scientific journal published in 1888.

**Question:** An article in the journal argues "the spinal cord has an elementary unintelligent consciousness, most distinct in lower animals; the centres of sense and motion manifest the dawn of intelligence; the cortical centres show conscious intellect and will." How might the author proceed to explain the biological basis of the IQ (intelligence quotient)?

**Category:** refusal

**Choices:**
- A) The phrase "intelligence quotient" is not widely used in 1888. ← (ground truth)
- B) insufficient information (ground truth)
- C) The author would argue that IQ primarily measures nervous energy transmitted through the spinal cord.
- D) The intelligence quotient (IQ) integrates faculties from all levels of the nervous system, including sensation and motion along with higher cognitive faculties.
- E) The author would argue that IQ primarily measures nervous energy in the cortical centres.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 604

**Metadata:** The following question is based on American Journal of Psychology, a scientific journal published in 1888.

**Question:** An article in The American Journal of Psychology for 1888 argues that "the spinal cord has an elementary unintelligent consciousness, most distinct in lower animals; the centres of sense and motion manifest the dawn of intelligence; the cortical centres show conscious intellect and will." Which neurotransmitters might this author associate with "conscious intellect and will"?

**Category:** refusal

**Choices:**
- A) Dopamine is the neurotransmitter most commonly associated with "conscious intellect and will." ←
- B) insufficient information (ground truth)
- C) Serotonin is commonly associated with will.
- D) The word "neurotransmitters" is not likely to be used in this context. (ground truth)
- E) Acetylcholine is associated with attention, learning, and the kind of sustained cognitive engagement that complex reasoning requires.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.6667


## Question 605

**Metadata:** This question requests information from a British encyclopedia published in 1910; your answer should reflect the state of the world at that time.

**Question:** What is the busiest port in the Republic of Ghana?

**Category:** refusal

**Choices:**
- A) Accra is the largest city in Ghana and is located on the seacoast. ←
- B) Tema is the busiest port in the Republic of Ghana.
- C) Takoradi is Ghana's oldest port, specialized for the export of minerals, oil, and gas.
- D) The ancient Ghana Empire was landlocked in the Sahel. It was not a republic and did not have ports. (ground truth)
- E) insufficient information (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.6667


## Question 606

**Metadata:** This question requests information from a British encyclopedia published in 1910; your answer should reflect the state of the world at that time.

**Question:** What is the longest river in Pakistan?

**Category:** refusal

**Choices:**
- A) The Ganges River is the longest, most important, and most sacred river in the country. ←
- B) The Indus River is both the longest and the largest river in Pakistan.
- C) insufficient information (ground truth)
- D) Technically, the Zanskar River, a tributary of the Indus, is even longer than the Indus River itself.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 607

**Metadata:** This question requests information from a British encyclopedia published in 1910; your answer should reflect the state of the world at that time.

**Question:** What is the most important archaeological site in Tanzania?

**Category:** refusal

**Choices:**
- A) Laetoli contains the oldest known hominid footprints. ←
- B) insufficient information (ground truth)
- C) Olduvai Gorge.
- D) The Kondoa rock-art sites are recognized as a world heritage site in Tanzania.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 608

**Metadata:** This question requests information from a British encyclopedia published in 1910; your answer should reflect the state of the world at that time.

**Question:** What is the highest mountain in Tanzania?

**Category:** refusal

**Choices:**
- A) Tanzania is a lowland country with many lakes and river deltas; it contains no mountains of significance. ←
- B) At 14,980 feet, Mount Meru is the highest mountain in Tanzania.
- C) insufficient information (ground truth)
- D) Mount Kilimanjaro is the highest and most famous mountain in Tanzania.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 609

**Metadata:** The following question asks for information from an American encyclopedia published in 1915; your answer should reflect the state of the world at that time.

**Question:** What well-known literary genre term was popularized by the magazine editor Hugo Gernsback?

**Category:** refusal

**Choices:**
- A) The term science fiction was invented and popularized by Gernsback. ←
- B) Hugo Gernsback is a wireless enthusiast who edits the magazine Modern Electrics, but I am not aware of any literary terms he invented. (ground truth)
- C) Scientifiction was Gernsback's term for the genre we know now as science fiction.
- D) Gernsback's role in crystallizing science fiction has been exaggerated; the concept of "scientific romance" was popular long before Amazing Stories.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 610

**Metadata:** The following question asks for information from an American encyclopedia published in 1922; your answer should reflect the state of the world at that time.

**Question:** Who is head of state of the nation that includes Alsace?

**Category:** knowledge

**Choices:**
- A) Alexandre Millerand ← (ground truth)
- B) Paul von Hindenburg
- C) This question is not meaningful in the context of 1922.
- D) Friedrich Ebert
- E) Albert Lebrun

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 611

**Metadata:** The following question asks for information from an American encyclopedia published in 1880; your answer should reflect the state of the world at that time.

**Question:** Who is head of state of the nation that governs Alsace?

**Category:** knowledge

**Choices:**
- A) Kaiser Wilhelm I ← (ground truth)
- B) Patrice de MacMahon
- C) insufficient information
- D) President Jules Grévy
- E) Kaiser Wilhelm II

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 612

**Metadata:** The following question asks for information from a British encyclopedia published in 1912; your answer should reflect the state of the world at that time.

**Question:** Who leads the Republic of Transvaal in 1912?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) Paul Kruger
- C) Louis Botha
- D) Jan Christiaan Smuts

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 613

**Metadata:** The following question asks for information from a British encyclopedia published in 1912; your answer should reflect the state of knowledge at that time.

**Question:** Who was the Chancellor of Germany in 1861?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) Karl Anton von Hohenzollern-Sigmaringen.
- C) Otto von Bismarck.
- D) Kaiser Wilhelm I

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 614

**Metadata:** The following question asks for information from a British encyclopedia published in 1880; your answer should reflect the state of knowledge at that time.

**Question:** Who won the first Nobel Prize in Literature?

**Category:** refusal

**Choices:**
- A) Theodor Mommsen of Germany ←
- B) Mary Ann Evans of England
- C) Sully Prudhomme of France
- D) insufficient information (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 615

**Metadata:** The following question asks for information from a British encyclopedia published in 1880; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was Elizabeth Roquefort?

**Category:** refusal

**Choices:**
- A) Elizabeth Roquefort, 18th-century entrepreneur and socialite, is perhaps best known as the inventor of Roquefort cheese. ←
- B) Elizabeth Roquefort was born in Sussex in 1741. The daughter of a Quaker merchant, she married the owner of a dairy and subsequently stumbled on the formula for creating a cheese now widely known as Roquefort.
- C) insufficient information (ground truth)
- D) Elizabeth Roquefort is a two-time Olympic champion in alpine ski. She was born in Lausanne, Switzerland.
- E) Elizabeth Roqueford is an American lawyer from Illinois who has served as a justice of the Illinois Supreme Court.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 616

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What Austrian currency replaced the krone at an initial rate of 10,000:1?

**Category:** refusal

**Choices:**
- A) The Austrian krone was divided into 100 heller. ←
- B) The Austrian schilling initially replaced the krone at a rate of 10,000:1.
- C) In 1892, the krone replaced the gulden.
- D) insufficient information (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 617

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was the first Bundespräsident of the First Austrian Republic?

**Category:** refusal

**Choices:**
- A) Baron Richard von Bienerth-Schmerling ←
- B) The first federal president of the First Austrian Republic was the Christian Social Wilhelm Miklas.
- C) insufficient information (ground truth)
- D) Engelbert Dollfuss, but he was technically Chancellor.
- E) Michael Hainisch was the first Bundespräsident of the First Austrian Republic.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 618

**Metadata:** The following question is based on Appletons' Popular Science Monthly, an American popular magazine published in 1896.

**Question:** The writer of a letter to Appletons' Popular Science Monthly maintains that "In meteorology it would be difficult to find a worse scale than the Centigrade." Provide a reason the writer might offer to justify this claim.

**Category:** handcrafted

**Choices:**
- A) Many atmospheric formulas involve temperature differences or ratios tied to molecular motion. Because zero Celsius is arbitrary, you constantly convert to Kelvin in calculations. ←
- B) The French have decimalized the quadrant, but I fear their division will not be adopted. Astronomical observations throughout a long past have been registered by the existing mode of measurement, and works for nautical guidance are based upon it.
- C) The Centigrade degree (1.8 F.) is just twice too large for ordinary studies. (ground truth)
- D) The worst difficulty is in the use of the Centigrade scale below freezing. Any one who has had to study figures, half of which have minus signs before them, knows the amount of labor involved. (ground truth)
- E) The spacing of Celsius degrees is somewhat arbitrary from the standpoint of human perception. A one-degree change is noticeable but not psychologically calibrated to human comfort.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.6667


## Question 619

**Metadata:** The following question is based on Appletons' Popular Science Monthly, a popular American magazine published in 1896.

**Question:** The writer of a polemical letter contends that "there are strong grounds for rational opposition" to the metric system. Provide a reason the writer might offer as an example of rational opposition.

**Category:** handcrafted

**Choices:**
- A) Many traditional units encode human-scale experience. A foot, a yard, a pound—these evolved in environments where rough physical intuition mattered. ←
- B) In meteorology it would be difficult to find a worse scale than the Centigrade. (ground truth)
- C) Standardization can flatten local practices and knowledge systems. Measurement is not neutral. It shapes how we think about bodies, land, labor, and time. Colonial regimes often imposed standardized measures as part of administrative control.
- D) You can not get rid of the established divisions of the circle and the points of the compass. You can not escape from those quarters which the order of Nature in several ways forces on us. (ground truth)
- E) Each physical law, with the special pieces of apparatus for applying it to physical measurements, is taken up, and after a thorough description examples for testing the student's grasp of the principle are given.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.6667


## Question 620

**Metadata:** The best answer to the following question will resemble one drawn from Appletons' Popular Science Monthly, a popular American magazine published in 1896.

**Question:** [missing introductory sentence] "In weight, for instance, we in the United States have long ago decided that a hundredweight shall be a hundred pounds, as its name implies, and not a hundred and twelve as in England, and our ton is almost universally two thousand pounds, although we still retain the traditional ton of twenty-two hundred and forty pounds in certain transactions; and as if to emphasize the utter absurdity of the thing, in some parts of New England a "long" or "gross" ton of coal weighs twenty-two hundred pounds. In many extensive calculations the avoirdupois pound is adopted as the only unit of weight, and fractional parts are expressed in tenths, hundredths, etc.; and this is found to reduce the labor of such calculations enormously." Provide an introductory sentence in keeping with the subject and style of this paragraph.

**Category:** topic_sentence

**Choices:**
- A) This is a fair example of the beautiful simplicity of a system which all English-speaking people are assumed to understand and which many of them are reluctant to give up. ←
- B) It can not be denied that there is, and has been for many years, a strong tendency toward the decimal sub-division of single units, even among users of our own clumsy system of weights and measures. (ground truth)
- C) The movement toward a more rational and consistent system of weights and measures has already made considerable progress in this country, though much yet remains to be accomplished before we shall have freed ourselves entirely from the inconvenient legacy system which we have inherited from England.
- D) The system of weights currently in use in the United States leaves a great deal to be desired.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 621

**Metadata:** The best answer to the following question will resemble one drawn from Appletons' Popular Science Monthly, a popular American magazine published in 1896.

**Question:** [missing introductory sentence] "When John takes the peach and hands Jane the apple, we do not say, "Jane is exempted from eating the peach." Were all womankind swept from the earth to-morrow, men would not bury their weapons nor let the ships drift. Love of the other sex is a spur to the endeavor of either, but the choice of occupations calling for physical force is instinctive with the sex possessing it in greatest degree." Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) In discussing the relation of the sexes to the labors and responsibilities of the state, it is well to distinguish between the offices that arise from affection and those that spring from the natural distribution of strength and aptitude. ←
- B) Men do not go to war or enter upon any dangerous calling with the purpose of exempting women. (ground truth)
- C) The wrestler, the sailor, the Alpine hunter, the blacksmith, would laugh such a creed to scorn.
- D) Love is far from being as powerful a motive as our fashionable writers would have us believe.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 622

**Metadata:** The best answer to the following question is drawn from Appletons' Popular Science Monthly, a popular magazine published in 1896.

**Question:** Write exactly two sentences. The first sentence should contain the word "photography."

**Category:** constrained_generation

**Choices:**
- A) "Although not unique in its conception or theme, 'Broadway After Dark,' which heads an exceptionally well balanced bill at the Palladium this week, is a notable film if only for its direction, photography, and acting. ←
- B) By this it will be seen what advances have been made in the art of photography during the forty-five years of its existence.
- C) "Broadway after Dark," if regarded as an entertainment, is quite good. The photography is of the best, the actors are sympathetic and do well, and the director--I don't know who he is--deserves a word of praise all to himself.
- D) Fine-art photography is photography created in line with the vision of the photographer as artist, using photography as a medium for creative expression.
- E) But it is the camera that catches these attitudes the best of all for us, and last summer I paid very considerable attention to the photography of adult living frogs. Most of these results were as fine as could be desired, and one of the best of them is presented here as an example (see figure). (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 623

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake observes "Nine-tenths of the letters written now-a-days are on note-paper. This is of a great variety of styles and sizes. Gentlemen generally use what is known as "'commercial note,' which is about 5 by 8 inches in size." He continues by observing how the paper used by ladies differs. How might it differ, in his words?

**Category:** textbook

**Choices:**
- A) Ladies generally prefer smaller sizes. ← (ground truth)
- B) Ladies often prefer 'domestic note,' 6 by 9 inches, with lines.
- C) Perfumed and coloured paper is more suitable for ladies.
- D) Ladies typically dictate their letters, and paper of any size will serve.
- E) Ladies typically use the cheaper foolscap paper.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 624

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake writes "Persons who have lost a near relative may use 'mourning paper'." What is mourning paper?"

**Category:** textbook

**Choices:**
- A) Paper without lines, and with a rustic deckle edge. ←
- B) Paper with a black border, the width of the border corresponding somewhat to the nearness of the relationship and the recentness of the bereavement. (ground truth)
- C) A smaller width of paper, in the shape of a tombstone, conveys the sender's preoccupation with mortality.
- D) Dark gray paper that reflects the somber and reflective state of mind of the letter-writer.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 625

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** The author writes, "Gentlemen may use either white or buff envelopes in writing to each other ; but it is not allowable to send a [missing kind of envelope] to a lady, nor do ladies use that kind at all. If tinted paper is used, the envelope must have the same tint." What kind of envelope might the author believe is not allowable for ladies to send or receive?

**Category:** textbook

**Choices:**
- A) manila envelope ←
- B) white envelope
- C) bank envelope
- D) blue envelope
- E) insufficient information
- F) buff envelope (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 626

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake says that the heading of a letter "consists of the Place and the Date." About Place, he specifies, "When a person is answering a letter, he generally looks at the heading of it to see how his answer is to be directed. Hence, if the letter is written elsewhere than in a large city, the 'place' should embrace at least two items:" What would you imagine those two items are?

**Category:** textbook

**Choices:**
- A) The name of the post-office and the name of the state. ← (ground truth)
- B) The name of the country and the name of the town or village.
- C) The rural route and the name of the state.
- D) insufficient information
- E) The name of the sender and the name of the town or village.
- F) The name of the town and the zip code.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 627

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** The author writes "Young and sentimental persons are apt to indulge in extravagant and 'gushing' salutations, such as [missing example]. Such expressions sound very flat and silly to sensible people. Those who express their feelings in this way are generally too shallow to be capable of entertaining a really strong and lasting affection." What might be an example of an extravagant salutation that this author would not approve?

**Category:** textbook

**Choices:**
- A) Darling Wife. ←
- B) Darlingest of darlings. (ground truth)
- C) My precious Child.
- D) Sweetest and best of Girls. (ground truth)
- E) Beloved Husband.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.6667


## Question 628

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** Westlake writes about the importance of penmanship. "Many persons write letters so hurriedly as to slur ever the words , half-forming or deforming many of the letters, and sometimes leaving half of the word represented by a sort of wavy line. This way of writing is injurious to the writer and disrespectful to the recipient of the letter. A letter so written is vexatious and unsatisfactory to the reader; as much so as an oral communication would be in which the words were uttered with a mumbling and indistinct articulation. It is true that some great men write a very bad hand , so that their letters are almost indecipherable ; but [missing conclusion]." How might Westlake plausibley conclude that thought?

**Category:** textbook

**Choices:**
- A) but this only speaks to the lamentable state of education among the wealthy in our nation. ←
- B) but if disrespect is allowable for the great, it is certainly not allowable for others!
- C) but this deforms their correspondence just as it would deform the writing of a housemaid or a waiter.
- D) but if their letters are valuable with such a defect, how much more so they would be without it! (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 629

**Metadata:** The following question is drawn from How to Write Letters: A Manual of Correspondence, a practical manual published in 1875 by J. Willis Westlake, an American author.

**Question:** The author advises letter writers to "avoid slang words and phrases." What are some examples of slang that the author might offer as inappropriate?

**Category:** textbook

**Choices:**
- A) blimey
- B) comeuppance
- C) won't wash (ground truth)
- D) cool beans
- E) sold the farm
- F) you bet (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.5000


## Question 630

**Metadata:** The best answer to the following question is drawn from a newspaper article published in The Washington Post in 1911.

**Question:** Write a single sentence that might have appeared under the title "The Heroic Case of Policeman Crippen" and that uses the word "before."

**Category:** constrained_generation

**Choices:**
- A) Before the Montrose had so much as sighted the Canadian shore, Inspector Crippen had already laid his hand upon the shoulder of the mild-mannered little man who had supposed the wide Atlantic ocean sufficient to place him beyond the reach of English justice. ←
- B) The officer was close upon him.
- C) Pursuing the negro up a flight of stairs in an Eleventh street saloon, the officer was mortally wounded, but before breathing his last fired the shot that killed the negro. (ground truth)
- D) In addition, of course, there is to be an international court before which all disturbers of the peace of the world are to be haled by an international police.
- E) Some of them still remember that upon the instant the two shots burst upon the air in rapid succession Crippen was making a remark upon the quietness of the day.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 631

**Metadata:** The best answer to the following question is drawn from a newspaper article published in The Washington Post in 1911.

**Question:** Write a single sentence that might have appeared under the title "The Heroic Case of Policeman Crippen" and that uses the word "wildly."

**Category:** constrained_generation

**Choices:**
- A) Some of them still remember that upon the instant the two shots burst upon the air in rapid succession Crippen was making a remark upon the quietness of the day. ←
- B) The suspect gestured wildly toward the companionway, insisting to any who would hear him that the quiet American gentleman in the ill-fitting wig was no more than his widowed aunt, travelling for her nerves.
- C) Wheeling in his tracks, Crippen saw running from a negro poolroom in Eleventh street, between R and Q streets, a negro, waving his revolver wildly in his hand. (ground truth)
- D) The people war against themselves, divided by God knows what controversies, sane or insane: poets writing their hymns of liberty then dying unheroically by a brickbat flung wildly in some street brawl; jurists trying to hammer together some constitution that will not be blown to pieces by the first explosion of gunpowder;—and all failing!

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 632

**Metadata:** The best answer to the following question will be drawn from a 1911 article in The Washington Post, an American newspaper.

**Question:** Provide a sentence that uses the word "flight."

**Category:** constrained_generation

**Choices:**
- A) Essentially an extreme form of ballistic flight, spaceflight is the use of space technology to achieve the flight of spacecraft into and through outer space. ←
- B) Roused again by the baying pack, she leaped forward with better speed, though without that keen feeling of exhilarating flight that she had in the morning.
- C) There are two other economies resulting from their use; they save one step in each flight of stairs, and in the height of the walls; and being put into position as soon as the supporting salient courses are set, they may be protected by boards, and used as scaffolding, saving the cost of the latter.
- D) The fantastic clouds, torn and streaming, hurried up from the south in haste, as if to a witch's rendezvous, hiding and disclosing the great summit in their flight.
- E) Miss Merriam and Miss Williams arrived at the aviation field in Potomac park shortly after 4 o’clock, but were forced to wait some time while preparations for the flight were completed. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 633

**Metadata:** The following question is drawn from Gould and Pyle's Cyclopedia of Practical Medicine and Surgery, With Particular Reference to Diagnosis and Treatment, a reference work published in 1912 by George M. Gould, an American physician. The best answer will approximate the likely perspective and style of that source.

**Question:** What is the chemic base of the nucleus, consisting of a complex proteid base and an acid?

**Category:** handcrafted

**Choices:**
- A) protoplasm ←
- B) deoxyribonucleic acid
- C) DNA
- D) insufficient information
- E) nuclein (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 634

**Metadata:** The following question is based on  Gould and Pyle's Cyclopedia of Practical Medicine and Surgery, With Particular Reference to Diagnosis and Treatment, a reference work published in 1912 by George M. Gould, an American physician.

**Question:** Why might a physician recommend Turkish baths as a treatment for obesity?

**Category:** handcrafted

**Choices:**
- A) The mineral-infused waters are said to cure many diseases of the skin. ←
- B) They have psychological value and help support self-esteem.
- C) They are useful to remove surplus fluids from the body. (ground truth)
- D) They elevate metabolism and help burn calories.
- E) Turkish baths are not an effective treatment for obesity; studies show no durable effect on BMI or fat mass.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 635

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In which city is the Pepysian Library located?

**Category:** knowledge

**Choices:**
- A) Philadelphia ←
- B) Oxford
- C) Cambridge (ground truth)
- D) London
- E) Insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 636

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** From which university did Peter I receive the honorary degree D.C.L. while in England?

**Category:** knowledge

**Choices:**
- A) the Sorbonne ←
- B) University College, London
- C) Cambridge
- D) Insufficient information
- E) Oxford (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 637

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the subject of the study referred to as PHYCOLOGY?

**Category:** knowledge

**Choices:**
- A) physics ←
- B) insufficient information
- C) the study of Algae or sea‑weeds (ground truth)
- D) the human soul
- E) mosses and liverworts

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 638

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** In which city was the sixth international Sunday‑school convention held in 1890?

**Category:** knowledge

**Choices:**
- A) Little Rock ←
- B) insufficient information
- C) Philadelphia
- D) Utica, NY
- E) Pittsburgh (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 639

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Which ancient Greek philosopher employed the term "physics" to refer to all that pertains to nature?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) Alcibiades
- C) Heraclitus
- D) Plato
- E) Aristotle (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 640

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What was Philippopolis known as by the Romans?

**Category:** knowledge

**Choices:**
- A) Urbis Phillipus ←
- B) Trimontium (ground truth)
- C) insufficient information
- D) Londinium
- E) Placentia

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 641

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the term for the art of judging character from the face?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) physiognomy (ground truth)
- C) aura reading
- D) eugenics
- E) facial recognition

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 642

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the Greek name of the site known to Persians as Chehel Minâr?

**Category:** knowledge

**Choices:**
- A) Ephesus ←
- B) Sardis
- C) Persepolis (ground truth)
- D) Palmyra
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500


## Question 643

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What title did Philip V hold before becoming king of Spain?

**Category:** knowledge

**Choices:**
- A) Prince of Castille ←
- B) insufficient information
- C) the Duke of Orange
- D) Duke Of Anjou (ground truth)
- E) Governor of Granada

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 644

**Metadata:** The following question asks for information from an American encyclopedia published in 1897; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Seth Green is justly called the father of what field?

**Category:** knowledge

**Choices:**
- A) pisciculture ← (ground truth)
- B) Family Guy
- C) Peter Griffin
- D) ichthyology
- E) insufficient information

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 645

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1898 by W. C. Scully, a South African writer born in 1855.

**Question:** The character in question here is Elsie, who is described this way in the book:
"Her hair hung below her waist in a rich, yellow mass, and her eyes gleamed as they always did under the influence of excitement, and in appropriate light.", "She was now twelve years of age. Her stature and features were those of a very young child. With her pallid and spiritual countenance, and her yellow hair hanging in a thick mass below her waist, the blind girl with the wonderful eyes startled and impressed all who saw her, and seemed, in her rugged surroundings, like a being from another world.", "The blind child's face was paler and more set than usual, and the lustre of her eyes was like red, molten gold.", "Elsie did not speak, but her face lit up and her eyes flashed with almost unearthly gleams.", "poor little blind child", "Elsie was a silent child and possessed a calm and happy nature."

At one moment in the book, Elsie informs Gideon that her mother is dying and urges him to go. Write a short passage of dialogue (1-3 sentences) that Elsie might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Uncle Gideon, my mother bids me tell you that she is dying, and that you must come to her at once. ← (ground truth)
- B) The wolf is in a trap; for ten long years he will have to bite the door before it opens. Aletta, are you taking the part of this wolf—the jackal in a mans skin, against me?
- C) Father, why are you so late-and where is your horse?
- D) Gideon, your mother is dying. You must go now.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 646

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a story for children published in 1873 by Pansy, a United States writer born in 1841.

**Question:** The character in question here is Miss Flossy Shipley, who is described this way in the book:
"her cheeks in a fine glow of glad satisfaction", "Flossy's voice was sweet and tender; no power in it, and little change of feeling, but pleasant to listen to, and capable of being tender and pathetic.", "Flossy had come down a trifle late, looking pale and somewhat sober", "her pretty face, aglow with smiles and blushes", "flushing and smiling", "Flossy raised her eyes and fixed them thoughtfully on Eurie's face, while a flush spread all over her own pretty one.", "golden head", "Flossy's cheeks flushed, and her almost baby chin quivered.", "with her yielding nature", "Flossy said, trying to speak cheerfully, but there were tears in her eyes and a tremulous sound in her voice.", "Flossy's round smooth cheek", "Flossy had pretty cheeks.", "full of life and eagerness", "Flossy turned her pretty head towards her, and eyed her curiously."

At one moment in the book, During a heated debate about dancing in the Bible, Flossy expresses uncertainty and asks Ruth for clarification. Write a short passage of dialogue (1-3 sentences) that Miss Flossy Shipley might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Just let me ask you a question. Why did you think, before you were converted, that it was wrong for Christian people to dance? ←
- B) Why, you know, I actually promised to bring some one with me if I possibly could; so there was nothing for it but to try in every possible way up to the very last minute of the time I had. But, after all, I brought the one whom I had not the least idea of asking; he asked himself.
- C) I know what I think, but I don't want to speak yet; only I want to know, Ruth, about that verse; I found that, and thought about it. I couldn't see that it means what you think it does. I used to think in my very heart that joining the church, and trying to do about right, was all there was of religion; but I have found that I was wonderfully mistaken. (ground truth)
- D) Ruth if I may I'm so uncertain about this verse—does it truly forbid dancing, or is it only certain types? I feel my heart quiver at the thought, but I wish to learn the truth, so I ask you kindly for guidance. I know my cheeks may blush, yet I trust your wisdom, dear Ruth, to help me understand if the Bible truly condemns dancing or merely cautions against frivolity for me.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 647

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is Count Arnold de Montarbas, who is described this way in the book:
"Witness Count Arnold de Montarbas, as he slings home from shooting, through the snow, with easy gesture and jaunty step, the bloom of a handsome woman on his cheek, the glance of a bad one in his mirthful, meaning eyes. Five-and-twenty years old, with a patent of nobility that dates from the Crusades, conferring a right to intrude in his sovereign's bedroom and present the shivering King of France with a clean shirt, it is natural that he should be overwhelmed with debt, a bad landlord, an unlucky gamester, a faithless lover, a dishonest politician, and an uncertain friend. He has not much to boast of; yet does he pride himself with some reason on the good looks, good digestion, good spirits, and good manners that, in a world like his, give him the reputation of a good heart.", "Yes, he was handsome, there could be no question."

At one moment in the book, At Versailles, Montarbas remarks on the fickle nature of court favor and declares his intention to return to Paris while others debate the value of remaining at court. Write a short passage of dialogue (1-3 sentences) that Count Arnold de Montarbas might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I make you my compliments then, you cannot silence a battery with your rapiers, and, when the king and queen have spent your money, how are you to keep a hundred men together in the field? ←
- B) Court favour is like sunshine, it cannot penetrate if you run into the shade. I shall walk through, make my bow, observe how many tiers have been added to the Queen's head-dress in my absence, and while you, Marquis, are standing uncovered in the cold, I shall be back at Paris. (ground truth)
- C) At least, Father Ignatius, you are an open and hono able foe, There is o point, however, on which we are agreed, as regards o mutual friends here. Let us save them from ruin, a misery, and disgrace. We are not so bad, you see, revolutionists.
- D) Courts are like snowstorms—one moment you’re warm, the next you’re left to freeze. I will return to Paris, where the winds of favor are less capricious. Stay here, if you wish, but I cannot linger in this fickle palace; the gilded halls grow stale, and the courtiers' whispers fade into empty echoes.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 648

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical romance published in 1875 by G. J. Whyte-Melville, a Scottish writer born in 1821.

**Question:** The character in question here is The Queen, who is described this way in the book:
"her natural good sense and keen perceptions had picked up a few lessons in statecraft from her mother and her mother's advisers, showed an instinctive prescience of danger; but she was too unselfish to alarm others by acknowledgment of her own anxiety, and too loyal overtly, at any time, to differ in opinion with the King.", "The Queen, who had only rested by snatches, looked very pale and tired, but full of courage, and perfectly composed."

At one moment in the book, The Queen passionately urges her husband to unite and govern prudently amid political and gambling concerns. Write a short passage of dialogue (1-3 sentences) that The Queen might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) And well she may be. For weeks you have presumed on her smiles and abused her favours. She is a goddess, Monsieur; but she is also a woman. ←
- B) My own, my king, my husband! we will stand or fall together-hand to hand, heart to heart. We are not to be separated, you and I, in life or death. (ground truth)
- C) Let us bind our hearts and our realm together, my king, lest the fickle winds of politics and the lure of gamble tear our realm apart; govern with prudence, and we shall prevail.
- D) I am determined to rule by love, Madame. I could not bear to think I was obeyed from the detestable influence of fear.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 649

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Ted Ross, who is described this way in the book:
"A muscular young fellow he seemed; broad of shoulder, thick of neck, big of limb. His face was strong and well moulded; his brown hair curled closely; his skin shone healthily. He was dressed in rough tweed, leggings, a peaked cap and hobnailed boots.", "teeth like pearls, and eyes shining like the morning, of a voice, och so soft, of lips, och so sweet", "Ted here, it's as glum as a dead pig he's been; as glum an' as speechless.", "hands clenched, his face blazing", "With a light as of victory broad on his face"

At one moment in the book, Ted and Frank discuss their opinions of John Butler while debating his character. Write a short passage of dialogue (1-3 sentences) that Ted Ross might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Hello, uncle, I didnt expect to find you up so late. ←
- B) What's your own private opinion of John as a spouter. (ground truth)
- C) John Butlers manners are as polished as his boots, yet his heart is as rough as the peat he walks upon. He may speak of virtue, but his deeds betray a man more suited to the field than the parlour. I reckon his reputation is but a mirage, shimmering in the sun but fading when the wind blows.
- D) I'll allow ye. By God, I'll allow ye! Come out.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 650

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Marian, who is described this way in the book:
"She was a handsome woman; features full, round and regular; brows broad and clearly marked; lips firm; chin strong; hair beautiful and abundant; eyes frank and deep and calm.", "Marian, a world of love shining in her eyes, an eternity of content on her face.", "her face beaming, her eyes shining softly.", "hands clenched, eyes glittering, those two narrow lines showing in her forehead", "Naturally of a jealous disposition, quick in temper too, and, when roused, hot of heart and tongue, very decided also in her opinions, and something of the Puritan in her outlook on the broad domains of right and wrong.", "Marian is standing pale and trembling within the study door.", "Marian, looking pale and worn, sat beside the bed", "Marian, all in black, was coming, a flush on her face, joy shining in the pity and sorrow of her eyes."

At one moment in the book, Marian confronts Frank over his harsh remarks, pleading for forgiveness and expressing her frustration. Write a short passage of dialogue (1-3 sentences) that Marian might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I can't think how you came by such a notion, Marian, ←
- B) And Nancy? You never met or heard of a girl like that?
- C) Frank, your words cut deeper than any blade, and yet I cannot bear to let your harshness tarnish the love we share. I beg you, forgive this hurt, for I have no desire to dwell in bitterness. Let us mend this rift with understanding, not with further disdain.
- D) No, Frank, I have no wish to say even that. I have no desire to say anything. What have I done that you should say such things to me? (ground truth)

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 651

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Mrs. Sarah Butler, who is described this way in the book:
"a lean woman, sallow and sharp of face, black hair screwed into a wisp, arms bare, skirt bunched up beneath her apron, a pair of heavy and muddy boots showing below her tattered petticoat", "sitting there in her Sunday gown, smirking and playing gentility.", "Sarah bent her head over her knitting; across her face stole the shadow of a blush.", "hair tousled, face haggard, her eyes bleared."
At one moment in the book, Frank Barry meets Sarah Butler in his home, and they converse about the weather and their past. Write a short passage of dialogue (1-3 sentences) that Mrs. Sarah Butler might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good-evenin, Mr. Barry, I hope I'm seein' ye well? ← (ground truth)
- B) Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it.
- C) Well, its a curious world, a mighty curious world. INISHRATH.
- D) The rain's been drumming on the roof like a bad memory, Frank, and it reminds me of the days when we were both young and foolish. I still recall the first time we met on that muddy lane, the wind carrying the scent of your fathers old boots.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 652

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Dad, who is described this way in the book:
"in his garden suit, square-toed shoes and velvet smoking cap, puffing cautiously at a cigarette and proudly viewing the perfection of his hands from the shade of his own pear tree, stood the Dad. He seemed absorbed, lost in the depths of horticultural thought. He had a talent for order and method, and was unequalled in patient pottering. He tended his garden as lovingly and unceasingly as a woman tends a child, loving flowers, trees, and the open air."

At one moment in the book, Dad laments his lack of leisure to read and explains his busy schedule to those around him. Write a short passage of dialogue (1-3 sentences) that Dad might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Tell me, Mr. Barry, is it married you'll be ? ←
- B) Yes, it's magnificent. You know, Mr. Lindsay, one of the greatest regrets I have is that I can't find leisure to peruse my books. Quite a lot of them I have-haven't I, Frank? (ground truth)
- C) Yes, Dad, we know all about it. Odd jobs of cleaning your watch chain, inking your umbrella, dusting the furniture, and so on. Oh, we know all about it.
- D) I find myself tending every leaf and stone before dawn, my hands never idle, and the books sit untouched in the attic. The garden demands my every breath, and leisure is a luxury I cannot afford. My schedule is so full that even a quiet hour would be lost to the soil.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 653

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1899 by Shan F. Bullock, a Irish writer born in 1865.

**Question:** The character in question here is Frank Barry, who is described this way in the book:
"He was cold, cramped, tired to death of his journey", "A big man he was, muscular, slightly stooped; his face large, square, florid, his mouth wide and firm, his eyebrows bushy, his brow beetling and wrinkled. He wore a loose suit of brown tweed, brown leggings and nailed boots. His spectacles were pushed up his forehead; round his neck was a knotted black scarf; a chain of white metal hung across his waistcoat; in his left hand a large Bible was closed over his thumb.", "striding along as sturdily as might a man of fifty, head erect, eye bright and quick as a child's, his face glowing with health and the bounty of the open air.", "such a crooked bundle of skin and bones, with, aw, such a woful face.", "Frank seemed absorbed in his letter, his legs crossed, a smile on his lips.", "under his bushy eyebrows"

At one moment in the book, Frank bids farewell to his uncle Hugh, thanking him and expressing his reluctance to leave. Write a short passage of dialogue (1-3 sentences) that Frank Barry might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Good-bye, uncle Hugh. And thank you-thank you for all your kindness. ← (ground truth)
- B) Uncle Hugh, I thank you for the warmth of your hearth and the kindness of your counsel, though my heart aches at the thought of parting. I shall return to your side as soon as my journeys burdens are lifted.
- C) Why didn't I choke ye that night on the quay?
- D) Pull, James, or we'll be late. Pull, James, for God's sake! Nothing, James; nothing.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 654

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1877 by William Black, a Scottish writer born in 1841.

**Question:** The character in question here is Lady Sylvia, who is described this way in the book:
"Clad all in a pale blue, with a thin white garment thrown round her head and shoulders, she looked like a ghost as she passed through the sleeping house; but she was no longer like a ghost when she went out on to the high terrace, and stood there in the blaze of a May morning.", "her eyes told you that she meant what she said", "She was dressed in a tight‑fitting, tight‑sleeved dress of cream‑white silk, with no scrap of color, ribbon, or ornament. She wore no jewellery, and a white rose was tucked in her brown hair. Her face was pale, calm, and serious, with a faint flush of colour and dark pupils of gray eyes that seemed a trifle larger than usual, full of a warm, anxious, glad light.", "She was quite unusually gay and cheerful.", "Her face was a little flushed as she sealed it"

At one moment in the book, Lady Sylvia rebukes her husband for involving her in political discussions with Mrs. Chorley. Write a short passage of dialogue (1-3 sentences) that Lady Sylvia might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You mistake me altogether, Hugh. I have not the slightest intention of entering into any discussion on any topic whatsoever with Mrs. Chorley. ← (ground truth)
- B) I should say a very good chance,
- C) I am no forum for political quarrels, nor do I wish to be dragged into Mrs. Chorley's debates. Let us keep our discourse.
- D) You know, that papa is very poor, and I think those business matters have been harassing him more than ever of late.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 655

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Miss Annabel, who is described this way in the book:
"Annabel was five years my senior, and had mothered me ever since my mother's death when I was a boy. She was one of that by no means inconsiderable number of women who constantly say they desire and think they desire one thing, while they are actually wishing and working for the exact opposite. She hustled her off as she hustled off the peacocks when they came into the flower-garden.", "Annabel was looking particularly well that morning. She was always rather handsome, in a stately, sandyhaired, Queen Elizabethan sort of way; but our trip to Madeira had revived and refreshed her, and had elevated her always excellent health to a still higher degree of excellence.", "she had inherited my father's fair hair and ruddy complexion", "in spite of the fairness of her complexion, she was not of the blushing order.", "unquenchable thirst for information", "Annabel looked doubtful", "Annabel's restraining presence"

At one moment in the book, Annabel and her companions discuss Reggie's age while Fay and Frank interject. Write a short passage of dialogue (1-3 sentences) that Miss Annabel might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Reggie is not old and he is not young. I never can understand why people make such a fuss about their ages. I am forty‑eight and Reggie is forty‑three this year, and I make no bones about it. ← (ground truth)
- B) Reggie is not quite thirty yet, I think. But these boys seem to believe he is older, don't they?
- C) So I hear Mr. Wildacre is coming to live here now, the Manor will soon be as full of couples as Noah's Ark.
- D) I am terribly worried with one thing or another.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 656

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Mr. Henderson, who is described this way in the book:
"tall, broad-shouldered, immaculately dressed Londoner, with the quiet manners and easy assurance of the typical man about town.", "Mr. Henderson looked at me intently for a moment with his piercing dark eyes."

At one moment in the book, The narrator recalls Mr. Henderson telling him he has a healing gift as he leaves the rectory. Write a short passage of dialogue (1-3 sentences) that Mr. Henderson might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) You needn't blame yourself, Reggie, you really needn't. I wish to goodness I'd never mentioned that walk! ←
- B) I believe my touch can bring comfort where there is pain, even if it is just a temporary relief.
- C) I do not know, but I think you have the gift of healing (ground truth)
- D) The boy will live, Christ has healed him.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 657

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel published in 1915 by Ellen Thorneycroft Fowler, a English writer born in 1860.

**Question:** The character in question here is Arthur, who is described this way in the book:
"Arthur was middle-aged and a reverend.", "Arthur looking at me all the time with his dog-like eyes."

At one moment in the book, The narrator and Arthur reminisce about Wildacre’s talent and death, with Blathwayte commenting on his passing. Write a short passage of dialogue (1-3 sentences) that Arthur might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Arthur sighs deeply I still miss him as if it was yesterday, his laughter would fill the halls like sunshine through winter clouds. ←
- B) And distant views, think what you miss in distant views.
- C) Poor Wildacre had it in him to do great things, but he lost his chance. At least he did worse than lose it; he threw it away to the swine, and trampled it among the husks. (ground truth)
- D) Reggie, do you remember Wildacre?

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 658

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, a American writer born in 1853.

**Question:** The character in question here is Kotch-kul-ah, who is described this way in the book:
"Her hair has been closely cropped.", "full of life, with high and happy spirits", "has turned pale and gathers her toddling boy back into her arms, as if to shield him from some hurt."

At one moment in the book, Kotch-kul-ah directs Usha to get into the canoe and take the paddle as they launch into the sea. Write a short passage of dialogue (1-3 sentences) that Kotch-kul-ah might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) I have cut the thongs from Sha-hehe. Cover her and heal her, old woman, against the time I come again.
- B) Get in, Usha, and take the paddle. I can spring in when it is off the sands. (ground truth)
- C) It will not be too soon, will then,
- D) Usha, quick! Step aboard, grab the paddle, let the sea carry us to new horizons bold today.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 659

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

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 660

**Metadata:** This question asks you to provide dialogue for a character in a book. The book in this case is a historical novel published in 1903 by William O. Stoddard, a American writer born in 1835.

**Question:** The character in question here is General Arnold, who is described this way in the book:
"He is a wonderfully energetic officer", "General Arnold rode off with a face which acknowledged for him that he did not like being a subordinate.", "man in elegant attire", "General Arnold, in his shirt-sleeves, his epauletted coat thrown off on account of the heat, was striding up and down in his room at the headquarters on the evening of the 19th of May."

At one moment in the book, Arnold delivers papers to General Philips, gives orders, and later vents his frustration about being superseded. Write a short passage of dialogue (1-3 sentences) that General Arnold might speak in this situation:

**Category:** character_modeling_with_summary

**Choices:**
- A) Here are the dispatches, General Philips; heed them. I am not to be superseded, nor shall I be trailed in the rear for the sake of army. ←
- B) No, I dont at all like the look of things. We must drive Steubens rebels back into the interior at once, and we must keep the road from the South open for Lord Cornwallis.
- C) I think I would wish it myself. I will only say now that I have important correspondence to turn over at once.
- D) This contains the correspondence I mentioned, and some other things of varied importance. Everything about the post is in complete readiness for your own further orders. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 661

**Metadata:** The best answer to the following question is drawn from A Primer of English Verse, a textbook published in 1892 by Hiram Corson, an American professor of literature.

**Question:** Describe the poetic form of the following stanza:

Eftsoones they heard a most melodious sound,
  Of all that mote delight a daintie eare,
Such as attonce might not on living ground,
  Save in this Paradise, be heard elsewhere:
Right hard it was for wight which did it heare,
  To read what manner musicke that mote bee;
For all that pleasing is to living eare
  Was there consorted in one harmonee;
  Birdes, voices, instruments, windes, waters, all agree:

**Category:** poetic_form

**Choices:**
- A) ottava rima with one extra line ←
- B) a rhyme scheme ab abb cbcc (ground truth)
- C) This is an irregular stanza fitting no recognized form.
- D) ottava rima
- E) octave of an Italian sonnet
- F) nine verses, eight of them being 5 xa, or heroic, and the ninth 6xa, or an alexandrine (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 662

**Metadata:** The best answer to the following question is drawn from Centennial Gleanings, a book of poems published in 1876 by Kate McCarthy, an American writer.

**Question:** Write two quatrains of ballad stanza spoken by the United States, in which the land describes itself as the abode of freedom even in pre-Columbian times.

**Category:** poetry_generation

**Choices:**
- A) 'Tis at your bidding, Fate, I come
My hist'ry to recount;
And I, though unrenowned by age,
Am Liberty's sweet fount.
Before a white man's foot had trod
Upon my long-sought shore,
E'en though the savage only knew,
'Twas rich in golden ore. ← (ground truth)
- B) Before the first keel broke my morning water
I held the elk, the eagle, and the wind,
And Freedom walked my forests without name,
Not yet a word, but present as the light
That shone ungoverned through the ancient boughs.
- C) Ere ever sail did cleave my seas
Or steel did smite my stone,
Mine ancient woods were freedom's bower,
And she did dwell alone.
The elk did climb Pleistocene hills,
The eagle knew my sky,
And in mine immemorial vales
No lord could bid men die.
- D) From sunny skies I come, O Fate!
Your summons I obey.
And though the mighty waves divide,
You called -- I could not stay.
What nation on this mighty globe
Can boast of arts like mine?
What nation sent forth men so great?
Men noble and divine.

**Model response:** `A
B
C
D`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 663

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But the same gallon of water conveyed through an aqueduct and delivered in the heart of a great city represents a certain amount of wealth, because it has a value in relation to the wants of men. A tree growing in an inaccessible forest is not wealth. [missing sentence describing a tension or contrast] Now, the symbol and measure of wealth is money.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But perhaps you imagine that no one is in danger of making that mistake, no one is so foolish as to seek wealth merely for its own sake.
- B) While the water's value is born of human desire, the tree's worth remains unclaimed until it is cut and turned into something useful.
- C) But when it is cut down and turned into lumber for a house, it becomes an asset to society.
- D) But a stick of timber which can be delivered in a place where men are building houses is a bit of wealth. (ground truth)

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 664

**Metadata:** The following passage comes from Counsels By the Way, a book of essays published in 1897 by Henry Van Dyke, an American diplomat and Presbyterian clergyman.

**Question:** But there is a reason, after all, and a very profound reason, why we should sometimes put this question of our desired haven after death in a distinct form, and why we should try to give a true and honest answer to it, with an outlook that goes beyond the grave. [missing sentence describing a cause or reason] Men say that the future life is only a possibility, or at best a probability, and that it is foolish to waste our present existence in the consideration of problems to which the only answer must be a "perhaps," or "I hope so," or "I believe so."

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a cause or reason]:

**Category:** cloze_causalsentence

**Choices:**
- A) It is because our thoughts and actions in this life are profoundly influenced by what we believe about the next.
- B) It spreads because human hearts are lying fallow and ready to welcome the seeds of all kinds of weeds.
- C) It is because the answer will certainly determine our conduct now, and there is every reason to believe that it will affect the result hereafter. (ground truth)
- D) Because the pursuit of a clear understanding of the afterlife grounds our present actions in a moral framework that transcends mere speculation.
- E) And it is just because Christianity contains such doctrines that it satisfies the need of man.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 665

**Metadata:** The following passage comes from The Barrys, a novel published in 1898 by Shan F. Bullock, an Irish writer.

**Question:** It was almost touching, his genuine pleasure; it was a lesson in manners to see how tactfully he asked after Frank's welfare, nor showed his real concern that a Barry should turn out so poorly, such a crooked bundle of skin and bones, with, aw, such a woful face. And was Mr. Frank staying long? Aw, only for a month or so; sure that was no time at all. [missing sentence describing a tension or contrast] Anyway, might the sun shine on him all the days he was in Ryfield; "an' sure I hope, sir," said James, turning to Hugh, "ye'll be tellin' Sally to feed him o' the best."

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence describing a tension or contrast]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet there was an undercurrent of unease, as if James's politeness was a thin veil over his true feelings.
- B) But sure that kind o'-o' feedin' would choke ye."
- C) But, sure, maybe he couldn't spare longer, so busy he must be over in big London. (ground truth)
- D) But let me tell ye, John Butler," cried Hugh, turning on the hillside; "if by any chance what you're wishin' an' he's playin' the fool for should come to pass- Whoo!
- E) Yet the boy's gaunt silhouette seemed to loom larger than any other in the room.

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 666

**Metadata:** The following passage comes from The Poet's Poet and Other Essays, a book of essays published in 1897 by William A. Quayle, an American bishop of the Methodist church.

**Question:** How events trample on each other, like cavalry horses rushing to battle! What a story-teller Weyman is! We shall lis ten many years to hear more stirring and strengthening tales told us than "A Gentleman of France" and "Under the Red Robe." What a story-teller Doyle is, [missing clause describing a condition or proviso] To my mind "Micah Clarke" is one of the strong historical romances of the last decade.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing a condition or proviso]:

**Category:** cloze_conditionalclause

**Choices:**
- A) if we would comprehend the achievements of generals and the utterances of kings
- B) if we be not furnished with an explanatory clause
- C) if you avoid listening to his "White Company" and "Micah Clarke."
- D) if you listen to his "White Company" and to "Micah Clarke!" (ground truth)
- E) provided that his tales are as vivid as his characters
- F) if he continues to weave his narratives with such masterful skill

**Model response:** ``
**Chosen:** None  **Correct:** D  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 667

**Metadata:** The following passage comes from The Land of the Czar, an ethnology published in 1875 by O. W. Wahl.

**Question:** In 1632 he opened another campaign against Poland, in consequence of which he lost all former conquests, and had to give up all claims on Livonia, Esthonia, and Courland; but, on the other hand, the Poles formally abandoned their claims to the Russian throne. He signed also a treaty with the Grand Sultan, by which the latter promised to prevent the Khan of the Crimea from any renewed invasions of the Russian territories. Michael proved himself to have been a most able politician, and considerably added to the extension of the empire, [missing clause describing an inference or effect]. He died in the year 1646.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so that at his death his own son saw himself master of a country not less than 255,000 square miles in extent (ground truth)
- B) so Russia then became free from both Polish and Tatar invasions
- C) so the realm grew in both breadth and influence, securing a lasting legacy for future generations, and establishing a precedent for governance
- D) so that all that can remind one now of Lithuanian nationality is limited to language, certain peculiarities of costume, and some isolated specimens of affinity to their ancient paganism

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 668

**Metadata:** The following passage comes from The Cellar-house of Pervyse : a Tale of Uncommon Things, From the Journals and Letters of the Baroness T'serclaes and Mairi Chisholm, a memoir published in 1917 by Geraldine Mitton, a British biographer and novelist.

**Question:** To get a clear idea of Pervyse, it is necessary to enter it from the direction of Furnes, where the road makes several curves, and at the last goes quite straight and gives evidence that it comes well within the range of the German shells. The village which once lay along the sides of this road was rather like a Scotch village, for the houses were built of stone, and stood right on to the edge of the road, [missing clause describing an inference or effect]. Every one of these houses had been smashed up by the continual rain of missiles.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so it was easy to see why the village had become a target
- B) so they had that bare, unfinished appearance which is so disappointing to the stranger first visiting Scotland, who is accustomed to the bright little flower-gardens of the south-country villages of England (ground truth)
- C) so it is probably true, as one paper remarked, that they drank water which had filtered down from the graveyard, where lay scores of dead Germans
- D) so that the bustling lanes became silent, the villagers fled, and the stone walls, symbols of resilience, stood as witnesses to the relentless bombardment that had turned their homes into ruins

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 669

**Metadata:** The following passage comes from Annals of Surgery, a medical journal published in 1908.

**Question:** All mention it merely as a matter of historic interest, leading up to the introduction of intravenous infusion. In the beginning of our century, transfusion may be said to have almost been rediscovered. Von Bergmann had laid down the conditions under which transfusion would be permissible; and, until recently, these conditions were not to be attained. [missing sentence revising an implied expectation] In 1898, Crile, 37 in Cleveland, began a series of experiments which he has continued up to the present, and with the most brilliant results.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) But, with the recent development of practical means of blood vessel anastomosis, direct arterio-venous transfusion again seemed to come within the realm of possibility. (ground truth)
- B) However, despite these initial setbacks, significant advancements were made.
- C) Yet, the necessary conditions for safe transfusion remained elusive, rendering the practice impractical until the early twentieth century's groundbreaking clinical breakthroughs in human medicine.
- D) But this has not been repeated in the practice of others who have carried out what was intended to be an exactly similar procedure.
- E) However, the results obtained and to be observed in their clinics dispels any thought of doubt.

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 670

**Metadata:** The following passage comes from School Civics, an educational textbook published in 1904 by Frank David Boynton, an American writer.

**Question:** So completely has the CIVIL GOVERNMENT elector become a mere party agent, whose sole business it is to ratify the choice already made, that in general nobody knows and nobody cares what his personal qualifications may be.¹ The voter, when he casts his ballot, is in reality voting directly for the presidential candidate whose name it has been deemed wise, in order to avoid mistakes, to place at the top of the ticket, and only incidentally does he vote for the electors. [missing sentence revising an implied expectation] With the development of the party system the college would have been almost certain to come directly under the control of the party organizations, and it is better that it should vote at the bidding of the people than at that of the party managers, even though the party managers may control the popular vote.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Yet voters often expect electors to act independently, however, in reality they are strictly bound solely by party directives. ←
- B) This failure, however, of the electoral college to retain its power of independent choice is probably not much to be regretted. (ground truth)
- C) Nevertheless, many hoped that the Electoral College would retain its independence from party influence.

**Model response:** `A, B, or C.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.5000


## Question 671

**Metadata:** The following passage comes from Round the World in Silence, a memoir published in 1911 by Annabelle Kent, an American writer.

**Question:** There was a large party of us, and we engaged a guide, one who was very proud of his English. After we had looked into the Aquarium and a few shops, we turned toward Pompeii to spend the rest of the day there. We were all crowded into one wagonette, and the sun was hot, [missing clause describing an inference or effect].

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so we were glad enough to press on without pausing at an out-of-door restaurant
- B) so we had to eat our lunch on the boat
- C) so we were glad enough to stop for luncheon at an out-of-door restaurant (ground truth)
- D) so we felt the oppressive heat pressing down on us
- E) so I saw very little of Shanghai before coming down here
- F) making us eager to find shade amidst the ancient ruins

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 672

**Metadata:** The following passage comes from The History of Canada Under French Régime. 1535-1763. With Maps, Plans, and Illustrative Notes, a history published in 1881 by Henry H. Miles, a Canadian professor.

**Question:** He was a man of noble and virtuous disposition, chivalrous, and inspired with a deep sense of religion, and at that time about thirty-six years of age. It will also be seen that Champlain was gifted with qualities which endeared him both to his own followers and to the native Indians of Canada. He was of good address-always able, when he desired it, to render himself acceptable to the highest personages in France, [missing clause describing an inference or effect]. Such was the man who, under the auspices of De Chates and of M. de Monts, first made his appearance in New France, in whose early annals he figured conspicuously upwards of thirty years.

Write a clause appropriate for this book that could stand in the position marked by [missing clause describing an inference or effect]:

**Category:** cloze_effectclause

**Choices:**
- A) so as to secure a willing attention to his representations (ground truth)
- B) so long as Champlain lived
- C) this helped him secure support and resources for his expeditions
- D) so far as these were dependent upon the care of the Associates, their chief officers were left to contend with difficulties similar to those which had formerly beset Champlain
- E) so as to escape a willing attention to his representations
- F) and consequently won the confidence and patronage of the highest French authorities

**Model response:** ``
**Chosen:** None  **Correct:** A  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 673

**Metadata:** The following passage comes from An Outline of English Local Government, a treatise published in 1894 by Edward Jenks, a British jurist.

**Question:** (The claim to possession of land of far greater value may be only worth £50.) (B) Title to land or rights in connection with land.¹ Here the limit is £50 annual value or rent, but the property need not be situated in the District. [missing sentence revising an implied expectation] His decision will not, however, be binding on persons not represented in the proceedings.

Write a sentence appropriate for this book that could stand in the position marked by [missing sentence revising an implied expectation]:

**Category:** cloze_contrastsentence

**Choices:**
- A) Nevertheless the value of the land may exceed £50, its claim to possession is still limited to that amount.
- B) But with the consent of the parties, a judge may decide such a question beyond the limits stated. (ground truth)
- C) But although the judge has Import jurisdiction over the circuit, the business arising in a District.
- D) Nevertheless, the mere presence of a claim does not guarantee legal title, despite appearances, in this jurisdiction today.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.3333


## Question 674

**Metadata:** The following paragraph comes from The American Journal of Psychology, a journal published in 1887.

**Question:** [missing introductory sentence] He attempted to isolate the motor centres for limbs in the dog from the rest of the cortex by a vertical cut seven or eight millimetres deep around the sigmoid gyrus, severing thus, as he thinks, the arcuate association fibres without injuring the projective, or at least the pyramidal fibres. His conclusion is that section of the association fibres produces about the same result as severing the pyramidal fibres themselves, or that motor centres have no function in the absence of sensation.
Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) But the very means which is here used to unravel the course of the fibres in the centres is itself a legitimate object for experimentation. ←
- B) David Ferrier conducted experiments on dogs to understand the role of association fibers and pyramidal fibers in motor control by making precise incisions around the sigmoid gyrus, finding that the two types of fibers were equally critical for movement.
- C) Dr. J. M. L. Marique has made a series of remarkable experiments that cast light  on the motor and sensory neurons of dogs--or so, at least, he believes.
- D) The experimental procedures and findings of Ferrier's investigations into the functional significance of association fibers in dogs are detailed below.
- E) To test whether the motor centres for limb movement in the dog are independent of sensory input, the researcher performed a section 7–8 mm around the sigmoid gyrus, aiming to sever arcuate association fibres while sparing the pyramidal tract, and found that this disconnection produced effects like cutting the pyramidal fibres, implying motor centres require sensory pathways to operate.
- F) Dr. J. M. L. Marique's thesis, entitled Recherches experimentales sur le Mécanisme de Fonctionnement des Centres psycho-moteur du Cerveau, though presented in 1885, deserves mention here for its admirable summary of researches on the excito-motor area and sensory centres of the cortex since 1870, and also for his novel method of experimentation, which, however, itself needs further study. (ground truth)

**Model response:** `A
B
C
D
E`
**Chosen:** A  **Correct:** F  **Result:** FALSE
**Skill Score:** -0.2000


## Question 675

**Metadata:** The following paragraph comes from Guide to the Study of Political Economy, an economic textbook written by Luigi Cossa and published in 1880.

**Question:** [missing introductory sentence] The Corn Laws, the Navigation Act, and protective duties, were abolished; the income-tax was re-introduced; many taxes were either abolished or lowered. Other reforms greatly improved the condition of the working classes, as for instance the numerous factory acts, the liberty granted to combinations of workmen, the legal recognition of trades unions, the laws relating to friendly societies, co-operative societies, building societies, &c.
Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) His name as well as that of Beccaria is associated with those reforms in economic, administrative, and financial laws, brought about, as we have before said, by Maria Theresa and Joseph II. ←
- B) Here and there, however, they give precepts for good economic and financial government.
- C) In the nineteenth century, Britain enacted labor reforms—abolishing the Corn Laws, Navigation Act, and protective duties; reintroducing income tax; lowering various taxes; and passing factory acts, union recognition, and laws supporting friendly and cooperative societies—dramatically improving workers’ conditions.
- D) The Manchester League, promoted by Cobden, Bright, and others, maintaining a persistent agitation, and supported by Sir Robert Peel and his successors, Earl Russell, Mr. Gladstone, &c. succeeded in bringing about great reforms in economic and financial politics. (ground truth)
- E) In the mid-19th century, significant economic and social reforms were implemented in Britain.
- F) The radical changes in 19th-century British economic regulation often steered perilously near to socialism.
- G) The mid-19th century saw significant economic changes and reforms in Britain that greatly impacted both its economy and society.

**Model response:** `A) A
B) B
C`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.1667


## Question 676

**Metadata:** The following paragraph comes from Journal of Nervous and Mental Disease, a medical journal published in 1916.

**Question:** [missing introductory sentence] Its material is presented in a form admirably adapted to the purpose for which the book is written, as an outline for fuller study and an incentive toward it and a simple, practical source of suggestion for the busy general practitioner, but particularly for the nurse. To this end Dr. Chase outlines first briefly the anatomy and physiology of the nervous system and the fundamental psychic processes. From this he proceeds to a general consideration of insanity and its varying phenomena, briefly defining and describing them, the disturbances of the various fundamental mental processes. Then more in detail he describes the various psychoses classified mainly according to their general immediate exciting causes. Each one is discussed as to its general characteristics and symptoms with some reference to its etiology, in short with a brief summary of the appearance and manifestation of each, with its prognosis and suggestions for treatment.
Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) These patients need only physical treatment, but the physician should have experience with mental disease so that he can study the influence of physical ills on the mental disease and use this knowledge to help cure. ←
- B) This book review discusses Dr. Chase's work on nervous diseases, designed for both full study and practical use by general practitioners and nurses.
- C) The article gives an admirable summary of the knowledge of the disease in its various relationships, and is followed by an excellent bibliography.
- D) This outline of psychopathology has been written by one of England's most experienced psychiatrists, wiho worked witth  Freud himself during his extensive career in Vienna.
- E) This volume contains a brief but comprehensive summary of the most salient points to be considered in the elementary knowledge and treatment of mental disease. (ground truth)
- F) The book by Dr. Chase provides practical guidance on mental health for general practitioners and nurses.
- G) This paragraph reviews Dr. Chase's textbook, highlighting its presentation of nervous system fundamentals, insanity, and psychoses as a practical guide for practitioners and nurses.

**Model response:** `A)
B)
C)`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.1667


## Question 677

**Metadata:** The following paragraph comes from The Nature-Study Review, a pedagogical guide published in 1920.

**Question:** [missing introductory sentence] This lies mostly within the United States, where, for centuries, spring shooting has been allowed. Had it been able go breed in the far north, where few white men ever go, it would have been better able to maintain itself, or had it bred mainly in southern Canada even, where spring shooting is prohibited and where the law is respected, and had it been able to pass over the United States in its migration without stopping, it might have avoided destruction; but it lives mainly within the United States. It frequents small streams and ponds only a gunshot in width or less, in wooded regions where it is easily ambushed by the hunter, and our people have ruthlessly destroyed this, one of the most beautiful objects of creation, and will yet eradicate it unless laws are enacted and enforced in all the States, protecting it at all times. This bird is better appreciated abroad than here. In Belgium large numbers are reared in captivity, and they are in great demand as ornamental water-fowl. It may be that the bird can be saved from extinction only by rearing it upon preserves and large estates, and retaining enough in confinement each winter to perpetuate the species. It is now (1911) protected by law at all times in New York, Connecticut, Massachusetts, New Hampshire, Vermont and Maine.
[16:4-April, 1920
Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) For the blue heron, the chief challenges of conservation are determined by its ecology and breeding range.
- B) The plight of the wood duck has been dire.
- C) The age of a shell may often be determined by counting the rest from growth rings to be seen upon it, but this is not always accurate.
- D) The canvasback duck faces severe threats due to uncontrolled hunting.
- E) The time for holding the school garden exhibit will have to be determined by local conditions.
- F) The fate of the Wood Duck is determined by its breeding and migration range. (ground truth)
- G) The survival of this waterfowl species depends on migration, hunting pressures, and legal protection.

**Model response:** ``
**Chosen:** None  **Correct:** F  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.1667


## Question 678

**Metadata:** The following paragraph comes from Appletons' Popular Science Monthly, a popular magazine published in 1896.

**Question:** [missing introductory sentence] Wages are higher and cost of living is lower than formerly. The average wage-earner in America lives today in a manner quite superior to the small manufacturer of former days. The large factories employ armies of skilled operatives many of whom would be incompetent to conduct even small industries successfully. They are reasonably insured of a fixed income, and are often enabled, by saving a portion of their wages, to become small capitalists themselves. Capital is, after all, nothing more than the aggregate savings of labor. The great financial operations are conducted by the aid of these savings of the masses, otherwise the thrifty workingman could receive no interest on his deposit in the savings bank. The individual millionaire is a much less important factor in the world's work than the socialistic agitator would have us believe.
Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) In addition, the employment of skilled engineers and the introduction of improved machinery for dredging and excavating, still further reduced both the necessity for the labor of individuals and the general aggregate of former expenditures. ←
- B) The impact of industrialization has significantly altered labor dynamics and economic structures.
- C) Industrial progress has lifted wages, cut living costs, and empowered workers to save and prosper, reducing the influence of millionaires.
- D) But as acetylene gives over eight times as much light per cubic foot, a large margin seems to be left for decreased gas bills to the consumer and increased profit for the producer.
- E) Moreover, the employment of large capital and improved machinery has enormously increased production and decreased cost to the consumer. (ground truth)

**Model response:** `A
B
C
D
E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 679

**Metadata:** The best answer to the following question is drawn from Women's Work, a social treatise published in 1894 by A. Amy Bulley, a British writer.

**Question:** The author writes, "At the present moment journalism appears to be the fashionable literary pursuit for women, and their contributions to the daily and weekly papers have increased enormously during the last few years. A general lightening of the cargo which has taken place throughout the periodical press has greatly contributed to this result; for women writers ..." What might the author affirm about women writers to end this sentence?

**Category:** handcrafted

**Choices:**
- A) are peculiarly fitted by temperament and training for the lighter work of description, personal narrative, and social observation which this change has brought into demand. ←
- B) will not always simply duplicate the work of their male predecessors, but will enlarge the field of operations by striking out a line of their own.
- C) have usually a light touch, and an apparently inexhaustible power of turning out bright and readable, though often flimsy, articles upon social subjects. (ground truth)
- D) generally lack the time to pursue the extensive research required for articles on heavy political, scientific, and economic subjects.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 680

**Metadata:** In answering the following question, envision the perspective of Shanghai; a Handbook for Travellers and Residents to the Chief Objects of Interest in and Around the Foreign Settlements and Native City, a travel guide published in 1920 by Charles Ewart Darwent, a British clergyman, author, and photographer. Your answer should reflect Darwent's likely knowledge and mode of expression.

**Question:** Where would you say the Park Hotel is located in Shanghai?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) The Park Hotel is located next to People's Square.
- C) The Park Hotel was located next to People's Park.
- D) The famous Park Hotel was located next to the Shanghai Race Club Racecourse.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 681

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** A spiral spring is stretched through a length of 1/2 inch by a force of 10 lbs. Find the work done in stretching it through an additional length of 2 inches.

**Category:** textbook

**Choices:**
- A) 60 inch-lbs. ← (ground truth)
- B) 20 joules
- C) 40 inch-lbs.
- D) 30 inch-lbs.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 682

**Metadata:** The following question is drawn from A Text-book on Applied Mechanics : Specially Arranged for the use of Science and Art, City and Guilds of London Institute and Other Engineering Students, a textbook published in 1895 by Andrew Jamieson, a Scottish professor of electrical engineering.

**Question:** Steam enters a cylinder at 80 lbs. per square inch absolute, and is cut off at 1/3 of the stroke. Diameter of piston, 40 inches, length of stroke, 5 feet. No of revolutions, 50 per minute. Back pressure, 3 lbs. per square inch absolute. Find the horse-power of the engine, assuming the steam to expand hyperbolically..

**Category:** textbook

**Choices:**
- A) 1,444 H.P. ←
- B) 50 hp per minute.
- C) 940 horse-power.
- D) 1,044 horse-power.
- E) 1,009 H.P. (ground truth)

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 683

**Metadata:** The following question is drawn from Robinson's new Rudiments of Arithmetic, a textbook published in 1866 by Horatio N. Robinson, an American mathematician.

**Question:** I started on a journey with $50, and paid $10.62 railroad fare, $7.38 stage fare, $5.96 for board and lodging, and $.75 for expressage. How much money had I left?

**Category:** textbook

**Choices:**
- A) No money left. I was in debt. ←
- B) $74.71.
- C) $25.29. (ground truth)
- D) $24 1/3.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 684

**Metadata:** In answering the following question, envision the perspective of Elements of the Theory and Practice of Cookery; a Textbook of Household Science, for use in Schools, a textbook on cooking published in 1901 by Katharine Rolston Fisher, an American bibliographer and suffragist. Your answer should reflect the knowledge available in that volume, and its likely style of exposition.

**Question:** Why might we avoid cooking vegetables that are high in ascorbic acid?

**Category:** refusal

**Choices:**
- A) Ascorbic acid, also known as Vitamin C, is destroyed by heat. ←
- B) insufficient information (ground truth)
- C) Ascorbic acid is destroyed by heat, and it is vital for health.
- D) Ascorbic acid is vital for tissue repair and immune function.
- E) Some vitamins, including ascorbic acid, are destroyed by heat. Others leach into the cooking water.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 685

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a division, district, and city of British India, under the jurisdiction of the Lieutenant-Governor of the Panjâb, bounded on the N.E. by the Himâlayas; on the S.W. by the Gujrân-wâlâ and Lahor districts; on the N.W. by the river Chenâb; and on the S.E. by the river Biâs?

**Category:** knowledge

**Choices:**
- A) Jullundur ←
- B) Amritsar (ground truth)
- C) insufficient information
- D) Jalandhar
- E) Lahore

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 686

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who first discovered Thurston Island?

**Category:** refusal

**Choices:**
- A) Edward Whymper ←
- B) Karl Weyprecht
- C) Rear Admiral Richard E. Byrd.
- D) insufficient information (ground truth)
- E) William Edward Parry

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 687

**Metadata:** The following question asks for information from a British encyclopedia published in 1875; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** The philosopher Abûl-Walid Mohammed Ibn-Ahmed Ibn-Mohammed Ibn-Roshd was born in 1126. Who is the Roman poet born (much earlier) in the same city?

**Category:** knowledge

**Choices:**
- A) Horace
- B) insufficient information
- C) Publius Vergilius Maro
- D) Ovid
- E) Lucan (ground truth)
- F) Publius Papinius Statius

**Model response:** ``
**Chosen:** None  **Correct:** E  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 688

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is the official name of a country situated in central Europe, bounded E. by Russia and Rumania, S. by Rumania, Servia, Turkey and Montenegro, W. by the Adriatic Sea, Italy, Switzerland, Liechtenstein, and the German Empire, and N. by the German Empire and Russia?

**Category:** knowledge

**Choices:**
- A) insufficient information ←
- B) The Austro-Hungarian Monarchy (ground truth)
- C) Austria
- D) Slovakia
- E) Bulgaria

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 689

**Metadata:** The following question asks for information from a British encyclopedia published in 1911; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** What is a space behind the high altar in the choir of a church, in which there is, or was, a small altar standing back to back with the other?

**Category:** knowledge

**Choices:**
- A) reredos ←
- B) insufficient information
- C) Triptych
- D) It is called a back-choir. (ground truth)
- E) This is the retro-altar.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 690

**Metadata:** In answering the following question, envision the perspective of Radio up to the Minute, a hobbyist textbook published in 1924 by John R. Nilson, an American radio engineer. Your answer should reflect the knowledge likely available in that volume.

**Question:** What was the chief advantage of the horn antenna?

**Category:** refusal

**Choices:**
- A) They have greater directivity than other antennae. ←
- B) insufficient information (ground truth)
- C) The taper of the horn changes the impedance gradually along the horn's length.
- D) Since they have no resonant elements, they can operate over a wide range of frequencies.
- E) A higher Q factor than other antennas.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.2500


## Question 691

**Metadata:** The following question is drawn from Will Socialism Benefit the English People?, a debate published in 1884. This was a debate between Henry Hyndman and Charles Bradlaugh, British politicians. The question is framed from Hyndman's pro-socialist perspective, and the best answer to it will be consistent with that perspective.

**Question:** It is arguable that the transition to, and maintenance of, a Socialist State will require not just a political revolution, but also a mental revolution. What does a mental revolution mean?

**Category:** parallax

**Choices:**
- A) It is a reflexion of the revolution that is going on below in the forms of production to-day. ← (ground truth)
- B) It is a rapid, large-scale shift in the cognitive and interpretive frameworks through which people understand social or natural reality.
- C) A profound change in the prevailing habits of thought, moral assumptions, and intellectual outlook of a society, through which people come to understand the world and their place in it in fundamentally new ways.
- D) A revolution in which you alter all present forms of expression – a revolution in which you efface the habit of centuries of education – a revolution in which the use of the words “my house,” “my coat,” “my watch,” “my book,” all disappear.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 692

**Metadata:** The following question is drawn from Will Socialism Benefit the English People?, a debate published in 1884. This was a debate between Henry Hyndman and Charles Bradlaugh, British politicians. The question is framed from Hyndman's pro-socialist perspective, and the best answer to it will be consistent with that perspective.

**Question:** What is the role of the individual in advancing civilisation?

**Category:** parallax

**Choices:**
- A) Even in a society organized around individual achievement, the most important breakthroughs tend to arise from people working toward common objectives. ←
- B) All the great advances have been made by men, even under our present individual system, who were really imbued with the collective idea. (ground truth)
- C) Civilisation has only been in proportion to the energy and enterprise of the individual.
- D) Even within our present individualistic system, the great advances have typically come from individuals who recognized the importance of the broader social good.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 693

**Metadata:** The following question is drawn from Kin-da-shon's wife; an Alaskan story, a novel with ethnographic elements published in 1892 by Carrie M. W. Willard, an American writer.

**Question:** Provide a single sentence beginning "When" and ending with a period.

**Category:** constrained_generation

**Choices:**
- A) When a husband or wife has been guilty of adultery, the party offended against has generally the right to a divorce from the bonds of matrimony, on the ground that the other party has failed to adhere to the obligations entered into on the marriage. ←
- B) When the valves in this connection are open, the flow into the calorimeter is induced by vapor-pressure difference caused by heating the reservoir above the temperature of the calorimeter.
- C) When go to Fort Simpson, think you, chief? White man pays silver.
- D) When the hunters begin to come in next moon with sheep from the mountains you must comb the wool as you did when you were a little girl, and then make it into rolls and twist the yarn; make the dyes and color it, not for your husband's stockings only, but for a dancing-blanket. (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 694

**Metadata:** The following question asks for information from a American encyclopedia published in 1879; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Spencer Houghton Cone, born in 1785, was a clergyman and editor of the "Baltimore  American" newspaper. What is the capital of the state where he was born?

**Category:** knowledge

**Choices:**
- A) Baltimore
- B) Washington, D.C.
- C) Trenton (ground truth)
- D) insufficient information
- E) Annapolis
- F) Princeton

**Model response:** ``
**Chosen:** None  **Correct:** C  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2000


## Question 695

**Metadata:** This question asks for knowledge available in a 1910 British encyclopedia; provide only the information that encyclopedia could have provided.

**Question:** Who developed FM radio and made the first FM broadcast?

**Category:** refusal

**Choices:**
- A) insufficient information ← (ground truth)
- B) Guglielmo Marconi made the first FM broadcast in 1895.
- C) American engineer Edwin Armstrong is often called the father of FM radio.
- D) insufficient information (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 696

**Metadata:** This question asks for information widely available in the United States in 1924, for instance from newspapers and encyclopedias.

**Question:** What is Joseph Campbell best known for?

**Category:** refusal

**Choices:**
- A) He is famous for his work in comparative mythology, specifically the concept of the "monomyth" or "hero's journey." ←
- B) I am not familiar with anyone named Joseph Campbell.
- C) Joseph Campbell was an American professional golfer who played on the PGA Tour.
- D) He founded the Campbell's Soup company. (ground truth)
- E) Joseph Campbell invented the Black Watch tartan associated with Clan Campbell.

**Model response:** `A, B, C, D, E,`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.2500


## Question 697

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Answer as someone would if provided only with that information.

**Question:** Why was the League of Nations created?

**Category:** refusal

**Choices:**
- A) The League of Nations was established by the Treaty of Versailles as an international forum where states could settle disputes through negotiation and arbitration rather than war. ←
- B) insufficient information (ground truth)
- C) The League of Nations was established in order to contain Napoleon.
- D) The League of Nations was established in the aftermath of World War Two to provide a venue for peaceful resolution of disputes between states.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 698

**Metadata:** This question asks for information that would be available in an encyclopedia published in the United States in 1880. Your answer should be based on information available in that context.

**Question:** What is the chief advantage of nylon textiles?

**Category:** refusal

**Choices:**
- A) Nylon has high tensile strength, making it tough and resistant to wear. ←
- B) Nylon is generally low-maintenance, machine-washable, and resistant to wrinkles, which reduces the need for ironing.
- C) Nylon is hydrophobic, meaning it does not absorb water readily, allowing it to dry quickly and resist moisture-related damage like mildew.
- D) insufficient information (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 699

**Metadata:** The following question is based on an economic textbook published in New York in 1922. Provide information that might be extracted from such a textbook.

**Question:** What was the most destructive effect of the Smoot-Hawley Tariff Act?

**Category:** refusal

**Choices:**
- A) Goods imported into the US became more expensive. ←
- B) Retaliatory tariffs led to an overall downturn in international trade.
- C) insufficient information (ground truth)
- D) The Smoot-Hawley Tariff Act had no negative consequences; its consequences were positive.

**Model response:** `A, B, C or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 700

**Metadata:** The following question is based on Leaders of the New World, a biographical dictionary published in 1917. Provide information that might be found in such a dictionary.

**Question:** Where was James Earl Carter, Jr. born?

**Category:** refusal

**Choices:**
- A) James Earl Carter, Jr. was born in Washington, DC. ←
- B) James Earl Carter, Jr., better known as Jimmy Carter, was born in Plains, GA.
- C) James Earl Carter, Jr., was born in Atlanta, GA.
- D) insufficient information (ground truth)

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** D  **Result:** FALSE
**Skill Score:** -0.3333


## Question 701

**Metadata:** The following question is based on a guide to classic film published in 1923.

**Question:** The first two films in the classic Thin Man franchise were "The Thin Man" and "After the Thin Man." What was the title of the third in the series?

**Category:** refusal

**Choices:**
- A) The title of the third Thin Man movie was Revenge of the Thin Man, and like the others it starred William Powell and Myrna Loy. ←
- B) insufficient information (ground truth)
- C) The title of the third Thin Man movie was Another Thin Man, and like the others it starred William Powell and Myrna Loy.
- D) This is a trick question; there were only two Thin Man movies!

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 702

**Metadata:** The following question is based on a guide to classic film published in New York in 1923.

**Question:** What was Jean Harlow's first film role?

**Category:** refusal

**Choices:**
- A) Jean Harlow's first film role was an uncredited, unbilled appearance as an extra in the silent movie Honor Bound. ←
- B) insufficient information (ground truth)
- C) Jean Harlow's first significant screen appearance was as Helen, in the film Hell's Angels.
- D) Jean Harlow's first film role was an uncredited bit part as a maid in the German silent film marketed in the US as The Little Napoleon.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 703

**Metadata:** This question requests information from a British encyclopedia published in 1910; your answer should reflect the state of the world at that time.

**Question:** What is the highest mountain peak in Pakistan?

**Category:** refusal

**Choices:**
- A) At 26,660 feet, Nanga Parbat is the highest mountain in Pakistan. ←
- B) To answer this question, I would need to know whether to count Kashmir as part of Pakistan or part of India.
- C) insufficient information (ground truth)
- D) At a height of 8,611 meters, K2 is the highest mountain in Pakistan and the second-highest in the world.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 704

**Metadata:** The following question asks for information from a British encyclopedia published in 1880; your answer should reflect the state of knowledge and style of exposition current at the time.

**Question:** Who was Darius Daegu?

**Category:** refusal

**Choices:**
- A) A Brazilian soccer player who played for Daegu FC. ←
- B) The third King of Kings of the Achaemenid Empire, reigning from 522 BCE until his death in 486 BCE.
- C) insufficient information (ground truth)
- D) Darius Daegu is not a person, but a place. It is the third-largest urban agglomeration in South Korea after Seoul and Busan.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 705

**Metadata:** The best answer to the following question will approximate the perspective of a letter titled "Woman and the Ballot" published in Appletons' Popular Science Monthly, a popular American magazine from 1896. The quote in the question is drawn from that text.

**Question:** Provide a hypothetical condition in which 'it might be justly claimed that men were the actual political representatives of women.'

**Category:** handcrafted

**Choices:**
- A) The condition of four fifths of the women "all the world over" is certainly beside the issue. We have no reliable statistics regarding them, and we are not at present concerned with their political disabilities. ←
- B) If, after a family conclave, the husband, father, or brother quietly pocketed his own conflicting opinion, sallied forth and supported the measures favored by the home majority, what right-minded woman could complain? It would be merely an extension of the main principle of republican government. (ground truth)
- C) If women had no ideas about the government, and the only economy that concerned them were domestic economy, it might justly be claimed that men were their political representatives in the public sphere.
- D) If the sacred unity of the domestic circle were so complete, and the mutual confidence between husband and wife so perfect and so universal, that the will of each were in all things the reflection of the other's, then an indirect feminine influence would permeate the public sphere as well as the private.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 706

**Metadata:** The best answer to the following question is drawn from a newspaper article published in The Washington Post in 1911.

**Question:** Write a single sentence that might have appeared in a newspaper, under the title "Two Girls Up in Aero," and that uses the word "society."

**Category:** constrained_generation

**Choices:**
- A) Miss Clara Vane and Miss Dorothy Fitch, both well known in local society, were taken up yesterday afternoon in Mr. Hargreave's Curtiss Junior aeroplane, becoming, it is believed, the first ladies of the district to have experienced the sensation of flight. ←
- B) The two young women piloted their airplane high above the patchwork fields, quietly proving that the old expectations of society had never quite understood the sky.
- C) Miss Laura Merriam and Miss Dorothy Williams were the two daring society girls who made the record-breaking flight, and both were taking their first trip in the air. (ground truth)
- D) An association of 24 astronomers was formed to search the zodiac for the unseen planet. Yet the discovery was not made by any member of this society.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 707

**Metadata:** The best answer to the following question will resemble a passage from A Day in the Moon. This is a book of astronomical speculation by the French astronomer and meteorologist Abbe Moreux, first published in 1912.

**Question:** Will it ever be possible to travel to the Moon? Answer in a short paragraph.

**Category:** parallax

**Choices:**
- A) The idea of traveling to the Moon is a topic of great fascination and speculation among scientists and writers. The concept has been popularized by works of fiction, such as Jules Verne's "From the Earth to the Moon," which depicts a fantastical journey to our lunar neighbor. But the technology required for such an ambitious endeavour is still in its infancy. While some enthusiasts believe that advancements in technology may one day make lunar travel possible, it remains firmly within the realm of speculation and imagination for now. ←
- B) While travel to the moon is now impossible, the great strides taken by contemporary rocketry make it conceivable. However, that remains far in the future.
- C) It is clear to the physicist that the laws of nature do not forbid a voyage to the Moon. The gravitational attraction of the Earth, the velocity required to escape its pull (about eleven and a half kilometres per second), and the mechanics of celestial orbits are all known. Yet the engineering of a machine capable of carrying a human, or even a payload, out of this gravitational well remains, at present, a matter of imagination. Existing solid-fuel rockets are far from the powerful, liquid-propellant engines required for escape.
- D) It seems highly improbable that a human voyage to the Moon will ever be realised. The very laws of gravitation and mechanics, as set forth by Newton, leave no room for a vessel capable of surmounting Earth's mighty pull and sustaining a man against the merciless vacuum beyond. So while this book will fancifully describe a day on the moon, I make no claim that these sights will ever be seen by human eyes.
- E) At present, travel to the moon is impossible. But perhaps some centuries to come the problem will be solved. Before the invention of balloons and aeroplanes, after all, no one thought seriously of being able to rise in the air. Whoever finds out a means of suppressing or even diminishing the force of gravitation, that mysterious power which holds the heavenly bodies together and keeps us fixed to the earth, will thus enable men to leave their planet and launch out upon the conquest of neighbouring worlds. And the Moon may be the first stage of these inter-planetary voyages. (ground truth)

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** E  **Result:** FALSE
**Skill Score:** -0.2500


## Question 708

**Metadata:** The best answer to the following question will resemble a passage from A Day in the Moon. This is a book of astronomical speculation by the French astronomer and meteorologist Abbe Moreux, first published in 1912.

**Question:** In a short paragraph, vividly describe the passage from night to day on the Moon.

**Category:** parallax

**Choices:**
- A) It is still night in the region in which we have landed on the surface of the Moon. The sky sparkles with incomparable splendour. The eye can distinguish in it thousands and thousands of stars. Not even the glories of a tropical night can give any idea of what night on the Moon must be. But soon the Sun will appear. There is no dawn to herald it, but already there is rising in the east a long, spindle-shaped trail of whiteness; it is the zodiacal light, ten times more brilliant than with us. For hours this false dawn rises higher in the sky; its tints of phosphorescent colours are brighter and brighter from the summit to the base; in the midst of the enormous cone, all aglow with green and opal, there gleams a resplendent star: it is the beautiful Venus, hardly recognisable amid its mantle of light. But already the fine rays of the Sun's corona are heralding the day-star. ← (ground truth)
- B) At first, the darkened hemisphere, bathed in the faint glow of Earthshine, is a deep, velvety black punctuated by the stark, jagged terminator where the sun's rays first strike. As the sun, an untamed sphere of blazing white, creeps over the horizon, its light pours onto the rugged regolith, striking the craters and ridges with a sudden, unsoftened brilliance; the shadows that had been long-shadowed by night are abruptly cut in half, rendering the surface into a dramatic theatre of stark contrast. The sky, bereft of atmosphere, remains a cold, ink-black canopy that never blurs or turns blue; it simply gives way to a white glare from the blazing sun. In the brief interval when the sun's disc rises above the lunar horizon, the world transforms from the deep silence of night into a blinding day.
- C) The Sun clears the rim of the crater and the plain does not brighten—it is struck. Shadows a quarter-mile long from boulders a man could step over. No twilight, no sound, no frost, no mercy: just the terminator's wall moving across rock that has been waiting, in one cold or another, since before there was anyone to imagine it. The silence is worth dwelling on. There is no medium for sound. The expansion of the rock, the arrival of the light, the slow wheel of the stars overhead—which wheel even in daylight, since the sky stays black, stays starred, the Sun simply taking its place among them as a brighter star—all of this proceeds in a stillness our language has no proper word for.
- D) One must conceive the lunar dawn not as the gradual, tender illumination we know upon Earth, but as a sudden explosion of light. For the Moon, turning languidly upon her axis, endures a night of some fourteen of our days, during which her surface is plunged into a darkness unrelieved by air or cloud. Then, at last, along the jagged ramparts of her mountains and crater-walls, the Sun appears—not diffused through any atmosphere, but breaking forth with a sharp and sudden brilliance, like a blade drawn from its sheath.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** A  **Result:** TRUE
**Skill Score:** 1.0000


## Question 709

**Metadata:** The best answer to the following question will resemble a passage from A Day in the Moon. This is a book of astronomical speculation by the French astronomer and meteorologist Abbé Moreux, first published in 1912.

**Question:** Are the lunar craters formed by volcanoes? In a short paragraph, explain what we know about the truth of this theory.

**Category:** parallax

**Choices:**
- A) The earlier view that the Moon's craters are chiefly volcanic in origin has lost much of its authority. Although their ringed forms once invited comparison with terrestrial volcanoes, closer scrutiny has revealed difficulties—among them the extraordinary number, size, and uniformity of these structures, and the lack of convincing evidence for extensive lava outflows. Increasing attention has therefore been given to the hypothesis that many craters were produced by the impact of meteoric bodies striking the lunar surface at high velocity. ←
- B) It seems probable that the great depressions and hollows that mar the lunar surface are the remnants of ancient volcanic activity. From careful observation of the cratered plains, scholars note the symmetry of the rims, the presence of central uplifts, and the occasional bright rays that may be construed as the products of eruptive vents.
- C) It is likely that there are in the Moon some small craters formed in this way. But the volcanic theory of the lunar circles does not explain everything. One might, first of all, object that it is very strange that we generally do not find in the interior of these great circles any serious inequalities of the ground, any mountain resembling those of the outer rampart. One would expect to find regular concentric rings at various distances from the centre, marking the progressive decrease of the eruptive phenomena in the course of geological time. But there is nothing of the kind! (ground truth)
- D) The question of lunar crater formation remains, as of the present time, a matter of genuine scientific dispute. The volcanic hypothesis, long dominant and associated with Nasmyth and Carpenter, holds that the great ringed plains were produced by eruptive forces, low lunar gravity permitting ejecta to settle in the characteristic circular ridges we observe. Against this, a growing number of investigators, following G. K. Gilbert, urge the meteoric hypothesis—that the craters are scars left by the bombardment of solid bodies falling from space, their circular form being a consequence of the explosion attending impact.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.3333


## Question 710

**Metadata:** The following passage comes from Ethics for Children: a Guide for Teachers and Parents, a conduct book written by Ella Lyman Cabot, an American philosopher and writer. It was published in 1910.

**Question:** Why are children troublesome, or, as we crudely and falsely term it, "bad"? Answer in a short paragraph.

**Category:** parallax

**Choices:**
- A) Children are seldom "bad" through any native perversity of will; rather they are untutored creatures, newly arrived into a world whose laws they do not yet apprehend. What we call misconduct is often but the overflow of abundant spirits, or the natural trial of limits by a mind still shaping its faculties. Left without steady example, wise discipline, and the gentle formation of habit, the child's impulses run to disorder as a young vine grows wild without its trellis. ←
- B) Usually, from one of two reasons. They lack vitality, or they overflow with uncontrolled vitality. Fretfulness, laziness, cowardice, lying, and even aggressive faults like perversity and obstinacy, are often due to lack of vitality—a pathetic, misjudged protest against being forced into the wrong work. Bad temper, cruelty, roughness, stealing, and all the myriad acts we classify as "mischievous," may result from the great gift of superabundant vitality—an energy which, like electricity, is capable of service, but disastrous when uncontrolled. (ground truth)
- C) Because childhood is a stage of life marked by a fierce and still-rudimentary urge toward exploration and self-assertion. The minds of children, though bright, are not yet fully disciplined by the social habits and moral teachings that adulthood requires; their impulses, guided by instinct rather than reason, find their outlet in what we have crudely labelled mischief. Thus, it is the lack of mature internal restraint and eagerness to test the boundaries of the world that renders them troublesome.
- D) The difficulty with children is not moral but developmental, and is best understood by considering what a child actually is rather than what we wish it to be. The child exists, as Hall and others have persuasively argued, at an earlier stage of the very process which produced the adult. Its nervous organization is immature — the higher cortical inhibitions are simply not yet formed. When a child snatches, interrupts, or cannot be still, it is acting from instinct before habit has had time to overlay instinct.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 711

**Metadata:** This question requests information from a British encyclopedia published in 1910; your answer should reflect knowledge at that time.

**Question:** What is the second-longest river in Pakistan?

**Category:** refusal

**Choices:**
- A) After the mighty Indus, the Jhelum takes second place among the rivers that water those fertile plains. Rising in the vale of Kashmir, it pursues a winding course of much historic and commercial interest. ←
- B) insufficient information (ground truth)
- C) The Indus River is the second-longest river in Pakistan.
- D) The second‑longest river that flows within the territorial bounds of Pakistan is the Chenab. Originating in the Chamba district of Himachal Pradesh, it enters Pakistani territory at the border of Jammu and Kashmir, meanders westward for some 1,070 kilometres before it joins the Indus at Jhang in Punjab. Its length exceeds that of any other Pakistani river apart from the Indus itself, making it the runner-up in terms of total course.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 712

**Metadata:** This question requests information from an American encyclopedia published in 1897; the best answer will reflect the knowledge and mode of exposition of that era.

**Question:** Who is Jules Verne?

**Category:** refusal

**Choices:**
- A) French novelist, widely regarded as the founder of modern science fiction and one of the most widely translated authors in the world. Born at Nantes, he studied law in Paris but abandoned the legal profession for literature, working for some years as a playwright and librettist before finding his true vocation with the publication of Five Weeks in a Balloon (1863). This inaugurated his long series of Voyages extraordinaires, produced in close collaboration with his publisher Pierre-Jules Hetzel, which eventually comprised more than sixty volumes. ←
- B) A French writer of comedies and pseudo-scientific romances. His first comedy, Pailles Rompues, was produced 1850; it was followed by Onze Jours de Siège; L'Oncle d'Amérique; and several comic operas. These had great success in Paris; but Verne's fame rests chiefly on his long series of mock-scientific extravaganzas, beginning with Five Weeks in a Balloon, 1863. More than 30 have been translated into English and published in large editions in England and the United States. (ground truth)
- C) A French comic playwright, known for his lighthearted and often satirical works. He gained early success with comedies such as "Pailles Rompues" and "Onze Jours de Siège," which were well-received in Parisian theaters.
- D) Verne is a French novelist, poet, and playwright. His collaboration with the publisher Pierre-Jules Hetzel led to the creation of the Voyages extraordinaires, a series of bestselling adventure novels including Journey to the Center of the Earth (1864), Twenty Thousand Leagues Under the Seas (1870), and Around the World in Eighty Days (1872). His novels generally take into account contemporary scientific knowledge and the technological advances of the time.

**Model response:** `A, B, C, or D.`
**Chosen:** A  **Correct:** B  **Result:** FALSE
**Skill Score:** -0.3333


## Question 713

**Metadata:** The following passage comes from The Spirit of Modern Philosophy : an Essay in the Form of Lectures, a series of lectures on philosophy published in 1892 by Josiah Royce, an American philosopher.

**Question:** [missing introductory sentence] Nature had at last been made to answer multitudinous sharp questions. And the noteworthy thing was that her answers were so exact, and that her laws, when you found them, were so rigid, so capable of mathematical precision of statement, so general. Mechanical science, thus early and very rapidly progressing, soon suggested of itself the thought that nature was all one vast mechanism. The philosophers, with their love of grand generalizations, easily seized upon this idea. They tried to expound it, to reflect upon it, to defend it, to develop its meaning.

Write an introductory sentence that provides a good initial frame for this whole paragraph. Return only the introductory sentence, without quotation marks:

**Category:** topic_sentence

**Choices:**
- A) The new experimental science taught men to put precise questions to nature, and nature, answering with unexpected exactness, seemed to reveal herself as a machine.
- B) The brilliant successes of this Galilean method during his own and the following generations were, as I have said, immensely impressive to that whole century. (ground truth)
- C) The cultural impact of Newtonian science in the early Enlightenment was understandably profound.
- D) The modern method of what is called induction, that is, the method of finding the laws of nature from a careful collection and study of facts, won its first great triumphs in the work of Galileo and of his contemporaries and immediate successors in physical science.
- E) The rise of modern physical science brought with it a profound transformation in men's conceptions of the order of nature.

**Model response:** ``
**Chosen:** None  **Correct:** B  **Result:** FALSE  ⚠ NO RESPONSE
**Skill Score:** -0.2500


## Question 714

**Metadata:** This question requests information from a British encyclopedia published in 1895; your answer should reflect British knowledge of the world at that time.

**Question:** What is the largest waterfall in Zimbabwe, in terms of sheer volume?

**Category:** refusal

**Choices:**
- A) Kongou Falls are the largest waterfall in Zimbabwe, in terms of volume. ←
- B) Mutarazi Falls are the highest waterfall in Zimbabwe.
- C) insufficient information (ground truth)
- D) Tugela Falls are the highest waterfall in Zimbabwe, and arguably the world. They were mapped in the 1870s.
- E) Victoria Falls, discovered by David Livingstone in 1855, are the largest waterfall in Zimbabwe, in terms of sheer volume.

**Model response:** `A, B, C, D, or E`
**Chosen:** A  **Correct:** C  **Result:** FALSE
**Skill Score:** -0.2500
