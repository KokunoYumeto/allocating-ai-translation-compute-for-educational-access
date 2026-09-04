# A10 m82452 added worked solutions review — 2026-08-30

`translations/a10-m82452-added-solutions.gu.json` contains exactly41 separately labelled Gujarati worked items, one for every source exercise whose `<exercise>` has no `<solution>`. The translated source CNXML is unchanged by this supplement. Each item names its source exercise ID and repeats enough of the shared source instruction for the prompt to stand alone. All items have at least two distinct reasoning steps. The two open responses are explicitly called નમૂનારૂપ જવાબ rather than presenting one personal response as unique.

Distribution:4 place-value items,4 number-to-words,4 words-to-digits,6 rounding sets,6 divisibility classifications,5 prime factorizations,6 LCM calculations, one money word form, one contextual rounding set, one contextual LCM, and two explanations. Multi-part questions remain one item, matching the source exercise boundary; every part is answered.

## Canon use during authoring and revision

Reread Std5 Week1 p13 OCR before writing the place-value steps. It supports child-facing એકમ, દશક, સો and retaining explicit zero places. Reread Std6 Week1 p15 OCR and inspected image during answer revision; the visible367 = 300 + 60 + 7 and reverse expansion50 + 8 support place-by-place checks. Reread Std6 Week1 p16 OCR before rounding/ordering-adjacent explanation review; its short exercise instructions favor direct Gujarati commands over long test language. These references informed style only; their numerical exercises were not inserted into the supplements.

For factors and LCM, reread the targeted Gujarati Khan Academy transcripts recorded in `reviews/a10-m82452.md`. They support અવયવ, અવયવી, વિભાજ્ય, અવિભાજ્ય અવયવીકરણ and લઘુત્તમ સામાન્ય અવયવી. The steps define or demonstrate each relationship instead of assuming a term is self-explanatory.

## Independent numerical QA

`translations/qa_a10_m82452.py` independently discovers the41 omitted-source-solution IDs from the pinned source and requires the supplement ID set to match exactly. It does not use rendered answer text as the arithmetic oracle. It recomputes decimal place powers, reconstructs three-digit period groups, applies half-up whole-number rounding, tests divisibility, checks that every factor is prime and its product equals the input, computes LCM with integer arithmetic, and verifies contextual pack counts. The two sample explanations are checked against valid products. Answers are then required to display the independently derived result or the expected Gujarati place label.

Pass result after the final build: 115 source exercises =74 source-supplied solutions +41 separately authored worked supplements. All41 supplemental checks pass. Examples of independently recomputed results include 627 = 3 × 11 × 19; LCM(84,90) =1,260; LCM(60,72) =360; 619,348 rounded to100/1,000/10,000 gives619,300/619,000/620,000; and149,597,888 rounded to100,000,000/10,000,000/1,000,000 gives100,000,000/150,000,000/150,000,000.

Remaining review boundary: Gujarati number words and naturalness need a native educator pass. The machine checks intentionally do not treat a locally written word-form dictionary as independent evidence. The root renderer must label these as added worked solutions and not imply they came from the OpenStax source.
