# B006 rounding: bounded Telugu canon witness

Prepared 2026-08-31 while the full Telugu assignment continues. This is a
reference-and-mathematics preparation record, not a completed translation,
native-speaker approval, or a regional terminology comparison. Only this file
was written in this subtask. Main must read the actual cited OCR and relevant
complete page images before using the recommendations; hashes and this summary
do not substitute for that reading.

## Canonical source and exact boundary

Read the entire canonical section `m81243#fs-id2472737`, **Round Whole Numbers**,
including its prose, image descriptions, procedures, tables, examples, six Try
Its, and final two resource links. The title and ID identify the same section;
it follows `fs-id1339359`, **Use Place Value to Write Whole Numbers**, and precedes
`fs-id2296006`, **Key Concepts**. Do not skip the intervening writing unit.

- Repository: `downloads/upstream-prealgebra`.
- Freshly checked HEAD: `38cae454e644abf9f0a623e876994553881597c9`.
- File: `modules/m81243/index.cnxml`.
- Fresh SHA-256: `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`.
- Section size: **462 elements, 104 IDs, 69 MathML expressions**.
- The source starts with a historical 2013 New York population example,
  `19,651,127`; its approximations are `20` million, `19,700,000`, and
  `19,650,000` at the stated places. These are source-context claims, not a new
  verification of current demographic data.

No source freeze, translation, bridge, build, asset, or lock was changed here.
Original English raster assets were not extracted or visually verified during
this canon subtask; the source-alt discrepancies below need that later check.

## Readable evidence and bounded procedure

The already selected pages suffice. No new download, OCR, PDF rendering,
archive extraction, duplicate corpus, or cleanup was needed. At the start C:
had `11111280640` bytes free.

Reread existing OCR **before** reading the corresponding complete images:

1. TS6 PDF14 / printed4, then PDF13 / printed3 for the beginning of section1.3.
2. TS6 PDF15 / printed5, including the final rounding prompt and valid
   place-value expansions; TS2 PDF42 / printed30 and PDF44 / printed32 for
   C10-C12 and zero contributions.
3. TS6 PDF17 / printed7 for C19's all-nines addition/carry examples.

All six complete page images were inspected in this pass. Existing OCR was
created with Telugu+English Tesseract; see the earlier selected-page procedure
in `B003-naming-witness.md`. There is no claim of a fresh OCR run here.

PDF identity, freshly rehashed:

| Book | Local PDF | SHA-256 |
| --- | --- | --- |
| SCERT Telangana Class6 mathematics, 2018-19 impression | `downloads/canon/ap/TS-6TM-MAT.pdf` | `3faa1f0551382ea25853d62604c63aa27034c6c07f7d56ce016c83d36b6f90ee` |
| SCERT Telangana Class2 mathematics, 2018-19 impression | `downloads/canon/TS-2TM-MAT.pdf` | `88a78193298607ee83a232214736c77a33c4aebc8bfc7630896eca8a73317966` |

Official acquisition URLs are respectively
<https://scert.telangana.gov.in/PDF/publication/ebooks/6TM_MAT.pdf> and
<https://scert.telangana.gov.in/PDF/publication/ebooks/2TM_MAT.pdf>.
The historical directory name `ap` does **not** make the Class6 book Andhra
Pradesh evidence. AP terminology remains unverified. This is a short anchored
observation record, not a republication or training corpus.

## Actual topic witnesses and their effect

These local labels do not independently allocate the main canon's next C-IDs.

| Witness | Exact PDF / printed anchor | Actual observation | Specific application to B006 |
| --- | --- | --- | --- |
| TS6-RND-CONTEXT | 13 / 3, section1.3 heading and three examples; continued in14 / 4, opening paragraphs | The heading connects `అంచనావేయడం` with writing numbers at nearby tens, hundreds, thousands. The context uses `దాదాపు`, `సుమారు`, `రమారమి`; the continuation says the real count may be slightly higher or lower, not exactly25,000. Rounding to nearby values is presented as one kind of estimation. | Translate *approximately* with a witnessed approximation expression such as `సుమారు`; name the specified-place operation explicitly with `సవరించి రాయడం (rounding)`. Do not teach that every estimate is produced by this one digit algorithm. |
| TS6-RND-TENS | 14 / 4, first blue number-line strip and its three bullets | Endpoints80/90, interior marks81 through89;81 is nearer80,87 nearer90.85 is equally far from both, but the page explicitly chooses90 by convention. | Preserve source76 to80,72 to70,75 to80. Explain equal distance separately from unequal distance and state that this lesson chooses the higher multiple in a tie. |
| TS6-RND-HUNDREDS | 14 / 4, second blue strip and following bullets | Endpoints200/300, marks every10, midpoint250. Worked220 goes to200 and280 to300. The250 case is posed as a question, not supplied as a printed answer. | Same nearest-multiple reasoning for hundreds; a worked250 to300 explanation may be added as original reasoning under the stated convention, not represented as a printed canon answer. |
| TS6-RND-PRACTICE | 14 / 4, bottom `ఇవి చేయండి` items1-3;15 / 5, opening discussion prompt | Prompts explicitly use nearby tens, hundreds and thousands. Examples include199 and695 for hundreds,9600 for thousands. The following page asks learners to choose numbers and round to the ten-thousands place. | The same reasoning extends beyond the short diagrams. Use place-dependent right-neighbor digits; record any computed practice answers as our computation, not quoted answers. |
| TS6-CARRY-C19 | 17 / 7, paragraph and addition sequence below the top table | `9,99,999 + 1 = 10,00,000`; the sequence visibly supplies9+1=10,99+1=100,999+1=1000 and9999999+1=1,00,00,000, with some intervening answers intentionally blank. | Supports the arithmetic carry mechanism, not an independently printed rounding algorithm. Use it to explain source3,978 to4,000 and29,504 to30,000; explicitly label any all-nines rounding example as an original application. |
| ZERO-C10-C12-C17 | TS2 42 / 30,746/805 rows and zero statement;44 / 32,709 and805 expansions;TS6 15 / 5, worked5078 and29,500 | Digit, position and positional contribution differ. Zero occupies its place and contributes0. Expanded sums can omit a zero addend without deleting a digit position. | In147,032, inspect the hundreds digit0 when rounding to thousands; do not skip it and inspect3 or2 instead. Replacing lower-place digits with zeros is not deleting them or dividing the number. |

The first TS6 strip is unit-spaced from80 to90; the second is spaced by10 from
200 to300. Do not reuse a blanket assertion that every displayed interval is1.
Their intervals differ because their intended scale differs.

## Terminology and scope decisions for the translator

1. **Rounding versus approximation.** A suitable editorial heading is
   `పూర్ణాంకాలను నిర్దిష్ట స్థానానికి సవరించి రాయడం (rounding)`, retaining the
   already witnessed whole-number term `పూర్ణాంకాలు`. The verb phrase and
   nearby-place pattern are witnessed; that complete heading is our composition,
   not a quotation or a claim of an officially prescribed one-word equivalent.
   For individual prompts, the page directly supports `దగ్గరి పదులకు
   సవరించండి`, `దగ్గరి వందలకు సవరించండి`, and `దగ్గరి వేలకు సవరించండి`.
   Use `అంచనా వేయడం` for estimation and `సుమారు` / `దాదాపు` for approximate
   values. House spacing in `అంచనా వేయడం` is editorial. Avoid leaving the
   general verb `సవరించండి` without its target place or context.
2. **Do not infer an unattested term.** The selected pages do not establish
   `సమీపీకరణ`, a transliterated rounding noun, or any AP alternative as an
   official term. An editorial equivalent may be defined, but the witnessed
   descriptive form plus English is sufficient here. Existing million/billion
   loanwords remain bilingual editorial choices, not new evidence from these
   pages.
3. **A tie convention, not a universal software rule.** Source75 and TS85 both
   round upward to the higher multiple. Say this is the convention used here
   for nonnegative whole numbers. Do not extrapolate to negatives or claim all
   mathematics and software use one rounding mode. Python's built-in `round`
   uses a different tie rule; it must not serve as the answer oracle here.
4. **The adjacent digit is decisive.** Identify the target position, then the
   single digit immediately to its right. Digits0-4 keep the target digit;
   digits5-9 trigger adding one target-place unit. The source's phrase “number
   to the right” should be explained as this adjacent digit, not the entire
   remaining suffix or any arbitrarily chosen digit. In23,658 the tens digit5
   controls rounding to hundreds, although23,658 itself is above, not exactly
   at, the23,650 midpoint. Likewise29,504 is above29,500; a5 in the controlling
   position does not by itself mean exact halfway.
5. **Carry is conditional and can cross positions.** Higher-place digits stay
   unchanged unless rounding upward requires a carry. A target digit9 does
   not automatically force a carry if the controlling digit is below5. When
   adding one makes10, write0 in that position and carry1 to the left; repeat
   across additional9s and create a new leading1 if needed. Source
   `fs-id1751923` explicitly explains10 thousands as1 ten thousand and0
   thousands. This is regrouping, not turning a digit into a two-digit cell.
6. **The result remains a full numeral.** Retain all required trailing zeros:
   843 becomes840, not84;147,032 becomes147,000, not147. An exact multiple,
   including0, stays unchanged when rounded to that place. A bridge can explain
   those edge cases as original applications; they are not new source questions.
7. **Preserve source international grouping and historical context.** Keep
   19,651,127 and its stated rounding targets/results unchanged, including
   international commas and million scale. Do not replace100,000 by a different
   target or silently rewrite source results in Indian notation. TS lakh/crore
   examples support arithmetic regrouping only. Keep2013 New York attribution
   historical, not “today's population.” Rounding loses precision; an approximate
   value is not an exact equality to the original population.
8. **Round once to the requested place.** If added to support material, explain
   that repeated rounding can differ:149 goes directly to100 at hundreds, but
  149 to150 at tens and then150 to200 at hundreds. This is an original caution,
   not a selected canon quotation. It should not replace the source algorithm.

## Checked source arithmetic and bridge candidates

Independent, read-only computation used integer quotient/remainder, never
floating point or Python `round()`:

```python
def whole_half_up(n, place_unit):
    # n is a nonnegative integer; place_unit is 10, 100, 1000, ...
    q, r = divmod(n, place_unit)
    return (q + (2 * r >= place_unit)) * place_unit
```

This was run against46 explicit expected results:17 canonical cases,5 printed
TS worked results,16 computed TS question answers,8 original edge/carry/double-
rounding checks. All passed. This is a bounded preparation check, not a claim
that the future generated B006 target or reader has been tested.

Canonical examples and Try Its, preserving source anchors:

| Source anchor | Requested place | Checked result |
| --- | --- | --- |
| `fs-id2368933` population paragraph | million; hundred thousand; ten thousand | 19,651,127 to20,000,000;19,700,000;19,650,000 respectively |
| Figures019/020/021 and `fs-id1384953` | ten | 76 to80;72 to70;75 to80 |
| Example `fs-id1395272` | ten | 843 to840 |
| Try Its `fs-id2324035`, `fs-id2306340` | ten | 157 to160;884 to880 |
| Example `fs-id3407439`, parts a/b | hundred | 23,658 to23,700;3,978 to4,000 |
| Try Its `fs-id1518702`, `fs-id2149604` | hundred | 17,852 to17,900;4,951 to5,000 |
| Example `fs-id1263758`, parts a/b | thousand | 147,032 to147,000;29,504 to30,000 |
| Try Its `fs-id2603401`, `fs-id4211785` | thousand | 63,921 to64,000;156,437 to156,000 |

TS6 PDF14 printed answers directly inspected:81 to80,87 to90,85 to90 at tens;
220 to200 and280 to300 at hundreds. The page asks, but does not print the
answer to,250 at hundreds: our computed answer is300 under its tie convention.

Answers computed for its bottom practice prompts, **not printed canon answers**:

- Tens:48 to50;62 to60;81 to80;94 to90;27 to30.
- Hundreds:128 to100;275 to300;312 to300;695 to700;199 to200.
- Thousands:7452 to7000;8115 to8000;3066 to3000;7119 to7000;9600 to10000.

Original checked carry/edge candidates:0 to0 at tens;4,000 to4,000 at thousands;
999 to1,000 at tens;99,999 to100,000 at thousands;9,999,500 to10,000,000 at
thousands. The final case is an actual halfway case whose upward carry crosses
multiple9s. Their use in a bridge would be labeled original instructional work,
not attributed as printed TS rounding examples.

## Source/OCR cautions requiring concrete handling

- **Source image alt,3,978:** media `eip-id1168289428689`, file
  `CNX_BMath_Figure_01_01_036_img-02.png`, says nearest **thousand** and describes
  the hundreds digit as the controlling underlined digit. The surrounding
  problem/table `eip-379` explicitly round to the nearest **hundred**, inspecting
  tens digit7 and carrying from hundreds digit9. The result4,000 happens to be
  the same under both requested places, so answer-only testing will not catch
  the mismatch. Inspect the original raster, retain source bytes, and document
  any corrected accessible description in the later adaptation.
- **Source image alt,29,504:** media `eip-id1168288313851`, file
  `CNX_BMath_Figure_01_01_038_img-03.png`, says nearest **ten thousand**. The
  problem/table `eip-596` round to the nearest **thousand**, using hundreds
  digit5 and carrying from thousands digit9. Again both targets happen to yield
  30,000, so verify the target place and controlling digit, not only the answer.
  Original-raster inspection remains pending in the asset pass.
- All five worked-solution tables (`eip-659`, `eip-493`, `eip-379`, `eip-695`,
  `eip-596`) declare `cols="3"` while their actual rows have two entries and
  their accessible labels say two columns. Preserve the frozen source; use an
  explicit reader exception if required, as for B004. Do not invent a third
  pedagogical column.
- The TS6 PDF14 OCR mangles the first strip's digit sequence. The inspected
  image is80,81,82,83,84,85,86,87,88,89,90; trust that image, not the OCR's
  duplicated/missing values. Its second strip is200,210,...,300.
- TS6 PDF15's bottom21504 factor remains the known printed error:5×10 is
  inconsistent with the correctly printed500 contribution. Do not use that
  row as an exemplar. The correctly printed5078/29,500 worked expansions above
  it independently support zero positions and unit contributions.
- TS6 PDF17 includes intentional blank answers in its carry sequence; do not
  claim our completion of those blanks is printed text.

## Identity receipts for actual rereading

All listed OCR files were reread before the corresponding complete images were
inspected in this pass. SHA-256 values were freshly recomputed. These receipts
establish file identity, not native linguistic approval or a new OCR run.

| Existing basename | Printed page | TXT SHA-256 | PNG SHA-256 |
| --- | --- | --- | --- |
| `downloads/canon/ap/TS6-naming-013` | 3 | `9481035018360d6ef49508da81dc480f89daafda9e30da83f7dca92cde744c60` | `1957028f7bf1097d7f790954dcc03353505e84a13b83fb4bb694add11400e104` |
| `downloads/canon/ap/TS6-naming-014` | 4 | `caf98a4bc0e0671ba27332b9fe4ff29e48d0ba7c164c2668ce2ec27c457680b0` | `0d276babd6be0f1137511e71585eb3a91fa527033dae10ce11c5d40d302351a3` |
| `downloads/canon/ap/TS6-naming-015` | 5 | `594afe62af4e28fd1a0bdc4801b4e798a383a8fd4ceccd2b3e9d9b568e68f9c3` | `79fd844a35ff3284c932b1b84c03787384028cd6db0153e8ae7ba795a38edbda` |
| `downloads/canon/ap/TS6-naming-017` | 7 | `75997b6acb8cd098560a2a5f20359df7589701bb5764151f383d9afb43db560f` | `3551228fbaadb0ef43b9b7358219f4a7c8e00dcd84b0cffecf0c248f9ba74a28` |
| `downloads/canon/ocr/TS-p042` | 30 | `8b81712a2e430118c4a23f4bbc9dd3bbc6f53b607525da9f1bfc81bc92491a18` | `fb1eab02c2afa6b1bd2e1accd597ecd94d4e476fc09109a0171c7dccdd14fe13` |
| `downloads/canon/ocr/TS-p044` | 32 | `9f8c8e02ab0c3e05a9c57321cd7c3b8cbb340b59eed32504afec1a00ecd1e716` | `70fcef4c820a5e785ab37640c5089517abce2164daa58672f52301b429d4abc9` |

Next actual use: main rereads PDF13-14 for rounding/approximation wording and
the midpoint convention, PDF15/17 for zero/carry distinctions as needed, then
compares the complete frozen B006 source before drafting. Record the concrete
effects in the main consultation log only after that use. No expanded
acquisition is necessary merely to obtain another rounding synonym.
