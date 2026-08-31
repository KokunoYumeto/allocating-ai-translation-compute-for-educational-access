# Canon consultation record

References are a working usage canon, not a claim of national-standard certification. All ten reference HTML pages were downloaded with SHA-256 receipts; they are readable as UTF-8 text under ignored `downloads/bn-Beng-BD/canon`. There are 13 starting examples in `register.json`. Native HTML needs no OCR. Two discovered PDFs were not used: one could not be downloaded, and the other was not trusted from its snippet. Acquire and OCR any PDF before future reliance.

## U01 drafting, 2026-08-30

Consulted government-hosted Bangladesh teacher examples BD01–BD05 while drafting. Chose একক/দশক/শতক and স্থানীয় মান; used grouping and an oral/object-based diagnostic. Kept whole-number terminology provisional instead of importing an Indian Bengali textbook convention. A00's ১৩৮, ২১৫, ১৭৬ and ২৩৭ remain its mathematical examples, not copied local-reference exercises.

## U01 revision, 2026-08-30

Read BD02, BD06, BD07, BD09 and BD10 downloaded text; read the relevant ১২৩/১৩২ passage in BD08; previously read BD01–BD05 page text. BD02 distinguishes a digit's position from its multiplied value. Accordingly, source tables use স্থান for the column name and the companion explicitly asks for numeric স্থানীয় মান. BD06 uses অযুত/লক্ষ/নিযুত/কোটি; reserved these for the next unit. BD07 supports verbal explanation, but that does not make our diagnostic standardized. BD10 contains spelling errors; do not reproduce them.

## U01 final QA, 2026-08-30

Read BD02's 359 place-value passage and BD01's block-grouping lesson again against the actual companion and source tables. Retained the distinction between a column's name and the digit's numeric contribution; the 138/215 tables, D4 and P3 reflect it. No additional terminology changes were needed. During table QA, corrected two inaccurate English source aria-labels in the translated CNXML (D018); the rendered five-column tables and all mathematics are unchanged. The canon examples guide usage, not a claim that this kit has national or teacher approval.

## Required before each next build checkpoint

1. Read the relevant local example text and the matching OpenStax section.
2. Add a dated consultation entry naming actual references, affected anchors and any resulting change or reason for no change.
3. Run QA; record human-review limitations separately. A build script loading a register is not proof that an agent read it.

## Remaining reference work

Acquire NCTB primary textbook/teacher-guide pages when reachable; OCR before use. Extend the canon for operations, fractions and measurement as those units enter production. Do not delay the existing number-sense pilot while collecting an unlimited bibliography.

## U02A drafting and revision, 2026-08-30

Read BD04 (C07), BD06 (C09) and BD10 (C13) local text again before drafting larger place value. Acquired only new BD11 (113,202-byte native HTML), preserving all ten existing locked sources; read its local extracted text in full through the number-grouping explanation. C14/C15 support the first-three-then-two digit grouping rule and reading combined thousand/lakh groups. The expanded canon has 15 examples from 11 documents.

Applied this to U02A's separate companion: `5,278,194` equals `৫২,৭৮,১৯৪`; source three-digit international groups stay untouched. Use ordinary দশ হাজার before অযুত, and explain দশ লক্ষ/নিযুত rather than assume the term is familiar. Source periods are explained as তিন ঘরের দল, not claimed as a mandated local term. Inspected both original place-value chart images before translating their descriptions. The companion distinguishes no *additional* hundreds after removing thousand groups from the false claim that the whole number contains no full hundreds.

The source asks for “place value” but often answers with place names alone. Faithful questions clarify that requested position; the separate answer supplement computes all 15 numeric contributions as well. Large billion/trillion examples remain optional teacher/reference material. No native-teacher approval is implied by these consultations.

## U02B drafting/revision and numeric-name QA, 2026-08-30

Reused the BD11/C14-C15 naming/grouping passage while drafting. Added and read three short government Accessible Dictionary HTML pages: BD12's পঁয়ষট্টি (65), BD13's সাঁইত্রিশ (37), and BD14's ঊনত্রিশ/উনত্রিশ (29) and ঊনচল্লিশ/উনচল্লিশ (39). Chose consistent editorial forms, without claiming alternatives are numerically wrong. Canon now has 18 examples from 14 readable documents; the original 10-document set remains intact.

Applied the entries to 165/37/137/529/839 in the source and worked-answer supplement. Visually read source figures 013–015. Kept English s/and conventions explicitly English; retained the source's international grouping rather than silently replacing it with lakh/crore. The helper number_names.py independently parses the six complete source answer names and 14 companion answer names back to their expected integers. It is an editorial QA lexicon, not an official spelling authority. Reviewed the 2014/April source example and 365-day-year assumption; contextual notes are separate from the faithful source.

## U02C drafting/revision/QA, 2026-08-30

Kept BD11's distinction between domestic comma groups and spoken thousand/lakh groups in view while reversing names into digits. The local dictionary passages consulted for U02B remain the spelling witnesses; the new writing cases additionally pass independent numeric-name parsing. Inspected figures 016–018; figure 017 and the canonical solution jointly expose the original alt-text error 742 versus 073. Explicitly corrected the translated description and retained all original bytes. The companion has fewer new assessment items because it follows U02B's already complete diagnostic rather than pretending each adjacent section starts a new course.

## U02D drafting, revision and mathematical QA, 2026-08-30

Searched specifically for Bangladesh rounding usage; did not adopt Indian Bengali, Assamese or un-OCRed PDF search hits. Acquired the single small BD15 HTML witness and read its local extracted text, including the ROUND paragraph in context. C19 supports the lexical phrase আসন্ন মান, not a primary-grade curriculum or the accuracy of the page's unrelated software advice. The initial canon has now grown to 19 examples from 15 documents. Used the phrase with an immediate plain-language explanation: the nearest multiple of the named place.

Consulted the established C04/C07 position-versus-value distinction and C14 grouping rule during revision: ask for দশকের/শতকের/হাজারের স্থানে, not a digit's numeric contribution. Reviewed C19 against the drafted introduction and final practice wording; no claim of NCTB-approved terminology was added. All 23 original figures were visually read. Corrected two false place names in source descriptions and three false dot-color descriptions, retaining all original image/witness bytes. The companion explicitly labels this lesson's halfway-up convention and the historical 2013 example. Twelve worked tasks, eleven source answer cases and 31 displayed rounding results pass integer/distance checks; every source exercise has a worked supplement.

## U02E and full-module assembly, 2026-08-31

Read the actual BD02 local ৩৫৯/৫০/৩০০ passage and BD11 local grouping/naming passage again against the full practice key. Continue the established C01 block/group register; no need to acquire another reference for the same topic. Previously read BD12–BD15 spellings/rounding passages remain relevant to the 32 naming/writing cases and 30 practice rounding answers. The source answer key uses international grouping in Bengali digits explicitly, while the child lessons retain their separate Bangladesh grouping explanation. The full module glossary uses the same provisional whole-number/origin/coordinate terms as U01, not newly invented alternatives.

Inspected the six new figure references: the PNG version of chart 011, four block models and the six-row self-assessment chart. Expanded the last figure's text equivalent to include all six visible skills; the original short alt omits that detail. Retained source college-campus language in faithful prose but used a supportive teacher/peer next-step checklist in the separately authored companion. Checked all 58 practice answers (including the 29 absent in the source); original 29 solutions remain unchanged in structure. Whole-module title, objectives and seven glossary definitions are now translated and assembled, without claiming native-teacher or PDF validation.

## U02 reading-edition QA, 2026-08-31

Re-read BD11.txt lines 43–73, especially combined অযুত/হাজার and নিযুত/লক্ষ names and the rightmost-three/then-two comma rule, while reviewing the rendered larger-type child tables. Re-read BD15.txt lines 89–95 for আসন্ন মান in context. These support the established language choices only, not curriculum approval or universal halfway-up rounding. No fresh reference download was needed. Print-v3 pages 1–57 now visually checked; screen review continues in exact-hash records under output/pdf. Figure-text boundary spacing was fixed at rendering level, with source translation values unchanged.

## Front-matter drafting, revision and QA, 2026-08-31

Read BD02's ৩৫৯/৫০/৩০০ explanation and BD04's place-order passage before drafting. Re-read BD09's two separate learning outcomes and BD15's actual ROUND paragraph during revision. Retain শেখার লক্ষ্য as an accessible heading, not a claim that the reference uses that exact phrase; keep the established আসন্ন মান terminology in the preface's decimal chapter overview. The preface's later algebra/geometry topic names are editorial translations pending topic-specific review, not certified primary vocabulary. Preserved the original college-level course description rather than recasting it as a Grades 2–5 syllabus.

Read complete canonical m81241 and m81242 and the relevant Indonesian parallel passages. Checked all five actual original images. The two front-matter HTML editions preserve every source element/ID, author/reviewer credit and content passage; source-specific rendering notices are separately labeled. Their PDF/human/accessibility reviews remain pending. The U02 visual checkpoint is complete in its later exact-hash receipt; the earlier consultation entry above remains a dated progress record.

## Addition reference acquisition, 2026-08-31

Read the live HTML description of BD16 (উজ্বল কুমার মজুমদার, 2021-08-09), outcomes ৯.২.১ and ৯.২.২, after reading canonical m81244 through its initial addition/block-model passages. The two outcomes use হাতে না রেখে/হাতে রেখে, যোগফল and vertical/horizontal arrangements. Use the established ones/tens/block register with that local carry vocabulary. The embedded presentation is not counted as read; search-result PDFs are not used. Local extraction is acquired and must be read before drafting the regrouping section.

Acquired the 45,762-byte HTML witness and actually read BD16.txt lines 21–55, including both outcomes. SHA-256 `f4315d4dfdd1d5782426a01d075aabf20763257c9c3f2d0f794a2e1265ce5c07`; readable extraction SHA-256 `49bd42fb202dad36721df920b59bdeeb0c3f134902ef05244e8ab3b8902d0013`. The split HTML line breaks do not alter the phrases. No additional content or grade certification is inferred.

## Addition notation and block-model drafting/revision/QA, 2026-08-31

Re-read BD16's local outcomes while moving from notation to models. Re-read BD01's actual পাঠ পরিচিতি paragraph: existing groups of ten develop into groups of hundred/thousand using blocks/sticks. Apply the established একক/দশক/দণ্ড/বর্গ register to the source 3+4, 2+6, 5+8 and 17+26 models. Use যোগের সংখ্যা as an explanatory term for addends, not a claim that BD16 mandates this term. The two readiness questions use the BD02 position/value distinction and the prior BD11 number-naming convention.

The 20 original figures were read individually, not inferred from their alt strings. The actual 018_img-04 image contradicts its original left/right description; 017 uses light blue rather than grey. The translated descriptions follow visible group counts/colors while keeping original files. Independently checked nine model sums and the spoken operands against source MathML, then checked that all translated source text reaches HTML. Carry/regrouping language remains paired with a value-preserving exchange, never the idea that carrying creates an extra unit. No new canon fetch or PDF reference was needed for this revision.

## Carrying, word phrases and applications, 2026-08-31

Read canonical m81244 without-models section through source line 900, then word phrases/applications/key concepts through 1192, and all final practice/glossary through EOF. During draft and QA, read BD16.txt lines 38–52 again: carrying and non-carrying are distinct outcomes. Inspected the five further carrying figures; the small carried 1s in 020-03/04 must not be described as fractions. The ten-by-ten body of the addition chart is checked independently, not accepted on visual appearance alone.

Acquired and actually read BD17.txt lines 25–44: visible title/caption যোগের বিনিময় বিধি (মোঃ আলতাফ হোসেন, 2022-11-01). HTML SHA-256 d04fdf6a5f1ec9e26a30f52d152d0e0cfc0d7b82553bb82cc73917fb34d049b9; normalized text SHA-256 32213c02595791213cbc1a06d3447be2fad04a5d5b3f974b8e594049880e8160. This supports the term, not mathematical proof or primary-grade certification. Identity/additive-identity terms remain provisional; unsuccessful searches did not license claiming an un-OCRed PDF or another region's terminology as Bangladesh evidence.

For perimeter, acquired and read BD18's visible definition and a+b+c paragraph after the canonical application examples. HTML SHA-256 2c863f4fdf4257ea66f5dc4a7eccfefaf76167b713d05a229d84d6f3847c42e7; text SHA-256 a21f8c00039a4e1d5deb11c153f7e467be8fcf92e18c6e4cfbe64ae457f83389. Use পরিসীমা with a boundary-length explanation. Independently viewed the three application figures and checked 26 feet, 30 inches and 36 inches from all side lengths. Do not confuse boundary length with area or silently convert units. Embedded canon pictures were not used. No PDF reference was consulted.

## Complete addition practice and glossary QA, 2026-08-31

Read the remaining canonical practice/glossary in two bounded source passages before drafting. Individually inspected the four block models, nine image charts, eight perimeter diagrams and five-row self-check chart. Re-read BD18's actual definition during final geometry-language QA: পরিসীমা is length around the boundary. Keep the apartment's square-foot quantity as মেঝের ক্ষেত্রফল, not volume, and do not convert customary units. BD16's previously read carrying outcomes continue to inform explicit place-by-place explanations.

Two 10×10 partial chart transcriptions independently match every original alt-described column and every visible nonblank arithmetic result. Correct only chart 222's transposed dimension description. Expand image-only solutions and all five self-check row labels. Keep figure 215's unlabeled side unlabeled in the source; derive its length only in the independent answer contract/companion. After assembling, directly read the Bangla cycling/day sequence, flower counts, room areas, weights, money, calorie data, pass-score comparison and elevator-capacity comparison. The Tuesday slot required a guarded context-specific override because another source paragraph uses the same Monday fragment before Wednesday. This is AI-assisted fluency/meaning QA, not native-teacher review.

## U03A separate companion drafting and QA, 2026-08-31

Re-read BD16's full local carrying/non-carrying outcomes before drafting the child lesson. Consulted BD11's actual অযুত/হাজার and নিযুত/লক্ষ explanations while choosing understandable larger-place names in the teacher answer key, without silently changing the source's comma grouping. During final placement QA, read BD02's complete ৩৫৯ example again: ৫ দশক has value ৫০, not merely the name of a column. Use that distinction to explain why a carried ১ in the tens column has value ১০ and a carried ১ in the hundreds column has value ১০০. The source's whole-number convention and provisional identity terminology are not recast as a nationally mandated primary syllabus.

All 129 answers are a separate editorial supplement, not inserted source solutions. The 17 requested block models now explicitly describe constructing and exchanging actual tens/ones groups; the 18 word-phrase questions explain their mathematical expression, including base quantity first for more-than/added-to. The child diagnostic allows oral, drawn and object-based responses. Its metric-perimeter task is a newly labeled local example, not a conversion of an original figure. Canon hashes and independent HTML re-extraction pass; no new reference or PDF was acquired for this stage.
