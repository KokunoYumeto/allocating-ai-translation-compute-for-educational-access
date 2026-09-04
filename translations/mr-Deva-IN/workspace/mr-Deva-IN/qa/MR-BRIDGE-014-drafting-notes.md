# MR-BRIDGE-014 — complete graph-reading section draft

2026-08-31. Role: translation writer and drafting-regression author, **not an independent reviewer**. This note covers source reading, Marathi consultation, original-image inspection and read-only XML checks. It does not grant HTML/PDF visual acceptance, native-speaker approval, module completion or book completion.

## Source boundary and exact scope

Read both complete pinned m81374 sections in memory from the existing ZIPs; no full-archive extraction or new download. EN was read in complete XML chunks. ID prose, media descriptions and every ID were read, with every MathML tree separately compared to EN: all 58 trees agree structurally, including the malformed notation identified below. The module bytes actually read are:

| Witness | ZIP member | Module bytes | SHA-256 |
|---|---|---:|---|
| EN | `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml` in `downloads/mr-Deva-IN/releases/A20-canonical.zip` | 247327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID | `source/modules/m81374/index.cnxml` in `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip` | 247303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |

Independently checked the actual sibling sequence: `fs-id1167836522816` (“Identify Graphs of Basic Functions”, MR013 scope) → **`fs-id1167836386547` (“Read Information from a Graph of a Function”, this unit)** → `fs-id1167836597228` (“Key Concepts”, exact next section). Module UUID: `4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada`.

The section wrapper and title are translated once. Its 12 direct non-title children are selected in this exact original order, all with prefix `A20:m81374#`:

1. `fs-id1167833022366` — science/business graph introduction.
2. `fs-id1167836620724` — reading domain/range introduction.
3. `fs-id1167836514287` — domain reminder and vertical tracing.
4. `fs-id1167825884739` — range reminder and horizontal tracing.
5. `fs-id1167829756085` — worked domain/range example, figure021.
6. `fs-id1167836529485` — Try It, figure022.
7. `fs-id1167833060073` — Try It, figure023.
8. `fs-id1167836515910` — introduction to graphs in later mathematics.
9. `fs-id1167836731462` — eight-part worked example, figure024.
10. `fs-id1167836507624` — eight-part Try It, figure025.
11. `fs-id1167829999559` — eight-part Try It, figure026.
12. `fs-id1167832982157` — original online-resource note and list.

Counts: 5 prose blocks, 2 worked examples, 4 source practice items, 1 resource note; 0 newly introduced formal source definitions, though two reminders restate domain/range. There are 6 supplied solution containers, with 30 answer components: 3 domain/range pairs plus 3 groups of eight. No original practice questions are added. The 54 IDs within the selected children plus the original section wrapper are preserved exactly once, retaining all parent–descendant relationships. Total target IDs: 57, including the authored article and credits IDs. There are no source tables, detached solutions or internal source cross-references in this selection.

This is fresh coverage of that next teaching section, not a claim that preceding/pending units are reader-ready. “Key Concepts”, section exercises, chapter review and practice test follow in the pinned module and are not translated here. The full five-book assignment remains active.

## Personally inspected original image evidence

Used only the authorized bounded helper:

```powershell
python -B mr-Deva-IN/tools/freeze_unit.py --review-images MR-BRIDGE-014 A20 CNX_IntAlg_Figure_03_06_021_img_new.jpg CNX_IntAlg_Figure_03_06_022_img_new.jpg CNX_IntAlg_Figure_03_06_023_img_new.jpg CNX_IntAlg_Figure_03_06_024_img_new.jpg CNX_IntAlg_Figure_03_06_025_img_new.jpg CNX_IntAlg_Figure_03_06_026_img_new.jpg
```

Personally opened all **12** original EN/ID files, in two six-image batches. Each locale pair is byte-identical; this is six distinct drawings, not twelve different diagrams. Review-copy paths are `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-014/{en,id}-CNX_IntAlg_Figure_03_06_NNN_img_new.jpg`. Archive image members use the respective prefix above followed by `/media/CNX_IntAlg_Figure_03_06_NNN_img_new.jpg`. Both files in each row have the listed size/hash.

| NNN | Original media ID retained on figure | Bytes per locale | SHA-256, EN = ID |
|---|---|---:|---|
| 021 | `fs-id1167836538244` | 54157 | `de4aa43fed8405eecd5c2b374de9de22ac05cc5671dc724fc6011d770cbc329e` |
| 022 | `fs-id1167829597137` | 52220 | `39d13f9e14959fde61119ba84591dd98665e62e6e8b9b0ab025b2ef35ab6f5d8` |
| 023 | `fs-id1167833128692` | 55962 | `0daa3919143f4279d61d1e26b70fbb78110a7b4e98971ad0c450bbabd0275556` |
| 024 | `fs-id1167836493218` | 68566 | `7e37d1d621f9291e7a543e53ceea6586ca389e178ff1673078c532408f7c7c93` |
| 025 | `fs-id1167836539761` | 59176 | `ceefe1e03a19fe0d5f88df9caa5fa722a4e4d64afe23293dcd815d112841fceb` |
| 026 | `fs-id1167836287943` | 56643 | `a961ce18529cd108247ddd1b6cd093eff3946f8df52b110c116525962521d504` |

One locale totals **346724 bytes**; all twelve review copies total 693448 bytes. Six `asset:` references request unchanged canonical EN images. No redraw, cropped replacement or AI image is used. Root must freeze actual asset records/pins before building; the handoff config intentionally has no `assets` object.

Pixel observations, separately from source alt text:

- 021: both axes label −6…6; filled endpoints (−3,−1), (3,1), marked maximum (1.5,3), crossing (0,2). Red domain bar [−3,3], turquoise range bar [−1,3]. Both source alts wrongly say axes −4…4; a visible correction explains the Marathi alt change.
- 022: both axes label −6…6; filled endpoints (−5,−4), (1,2), curve through (0,−3); bars [−5,1], [−4,2]. Source alt and answer agree.
- 023: both axes label −6…6; filled endpoints (−2,1), (4,−5), maximum (0,3); bars [−2,4], [−5,3]. Source alts wrongly give x −4…5, y −6…4; explicit correction, unchanged image/data.
- 024: x labels −2π…2π, y labels −6…6; source alts wrongly give y −4…4. Labeled extrema (−3π/2,1), (−π/2,−1), (π/2,1), (3π/2,−1), five visible axis zeros at integer multiples of π. Arrows at both edges. Explicit alt correction.
- 025: x labels −2π…2π, y labels −6…6; maxima 2 at −3π/2 and π/2, minima −2 at −π/2 and 3π/2; same visible five zeros. Arrows at both edges. No source-data correction needed.
- 026: x labels −2π…2π, y labels −6…6; maxima 1 at −2π,0,2π, minima −1 at −π,π, four visible zeros at odd half-integer multiples of π. The y-intercept is (0,1), not the origin. Arrows at both edges. No source-data correction needed.

Source-image inspection is not output-format visual QA. All image descriptions/captions are available in Marathi; unchanged diagram symbols remain x, y, π and numerals.

## Source errors and mathematical decisions

1. **Malformed function application:** both EN and ID supplied solutions at `fs-id1167836550513`, parts (b)/(c), encode `f = (π/2) = 2` and `f = (−3π/2) = 2`. The XML answer uses `f(π/2) = 2` and `f(−3π/2) = 2`, with a visibly separate note quoting/disclosing the two source forms. Only the misplaced first equal sign changes; input and output values are preserved and agree with the original graph.
2. **Finite supplied zeros versus continued graph:** worked-example (d)/(e) asks without an interval but lists five visible zeros/intercepts. Both Try Its restrict (d) to [−2π,2π], but their (e) asks without a separate restriction and supplies only visible intercepts. Keep every original question distinction and every supplied finite answer. Explicitly call those finite lists the source's lists, then explain in separate authored notes that they cover the shown window, not an exhaustive infinite set. For the source-declared repeating continuation, the first two graphs' global intercepts are `(nπ,0), n ∈ ℤ`; the third graph's are `(π/2+nπ,0), n ∈ ℤ`. The worked example also gives global zero inputs `x=nπ`. The source itself says the pattern extends indefinitely, which is the premise for this completion; neither pixels nor a finite sample is claimed to prove a universal periodic law. No sine/cosine formula is introduced as though it were stated in the source.
3. **Intervals and scale:** include endpoints shown by filled dots/attained extrema; use square brackets for closed intervals. Keep full real domain `(−∞,∞)` separate from the visible x-window and keep function range separate from the y-axis tick extent. The maximum in figure021 is internal, not its right endpoint. No interpolation formula is fitted to the first three drawings.
4. **Evaluation versus points:** retain three explicit evaluations per wavy graph. For x-intercepts use full ordered pairs, not only input numbers. For the y-intercept read x=0. All rational multiples of π are transcribed with explicit `/2` grouping. The original `(3/2)π` and `(1/2)π` are normalized to `3π/2`, `π/2` with two clearly authored exact-equality reminders.
5. **Complete solutions:** the first worked example's two original explanatory paragraphs and all eight parts of the second worked example's explanatory paragraph are fully translated under their original IDs. Try It supplied-answer paragraphs retain their IDs and ordering; new reasons are separately marked `data-kind="original"`. No source rows/tables are omitted because this section contains none.

## Marathi canon actually consulted and applied

At selection/drafting, freshly searched and read actual **C19** [फलन](https://vishwakosh.marathi.gov.in/27548/) definition/domain/image-set prose. This supports प्रांत, preserves the distinction between actual images and सहप्रांत, and prevents treating the grid window as the output set. The witnessed range synonym is कक्षा; existing working मूल्यसंच remains explicitly provisional rather than being silently promoted. Did not need a fresh C14/C20/C21 claim for this topic: the selected source has no new absolute-value or conic classification task.

For coordinate-reading wording, read actual **C18** [आलेख](https://vishwakosh.marathi.gov.in/24316/) opening and जात्याक्ष आलेख paragraphs through fresh search-reader retrieval after a direct open returned 502. They explicitly describe horizontal/vertical axes, signed directions, independent axis scales and ordered सहनिर्देशक. Applied these to x/y tracing and the captions. Its data-joining example is not a license to fit an arbitrary formula or infer an entire periodic function from finitely many points.

The concrete new topic, closed interval notation, required a narrow new lookup. Read [विश्लेषण, गणितीय](https://vishwakosh.marathi.gov.in/32824/), direct-open lines107–113, especially the repeated `[a,b]` / **अंतराल** usage. This supports the existing T030 word rather than importing the article's advanced calculus claims. Sent the exact locator/effect to root for independent reading before any global canon/term promotion. The full phrase **अंतराल-संकेतलेखन**, endpoint reminder and explicit “अक्षाला छेदणारे बिंदू” wording remain authored classroom choices. No shared ledger was edited by this writer.

During revision, direct reopens of C19 and the interval article failed with 502; recorded as failures, not new successful reads. Then fresh targeted search-reader results returned both relevant passages and were actually reread. Rechecked the finite visible ranges versus domain and the bracket wording against those passages. Final wording review replaced the equal-sign explanation with explicit “पहिले समानचिन्ह” and paired आदान with input at its first use. Existing terminology.csv was read; no unsupported global status promotion is claimed. All references used here are readable web prose; no new Marathi PDF formula was used or OCR step claimed. Original JPEGs were inspected as pixels, not substituted by their alt descriptions.

## Link, notice and workflow preservation

All six original problem IDs and six original solution IDs have actual bidirectional same-document anchors; 12 such links plus five navigation links give **17 local anchors**. Five HTTPS anchors comprise the one original resource, the established component-license link, and three Marathi reference links. No source document/target cross-reference occurs inside this selection. The one original resource URL `https://openstax.org/l/37domainrange` is preserved exactly; its destination was not fetched/reviewed or counted as translated. Offline reading does not require opening it.

Retained root-established OpenStax authorship and **CC BY-NC-SA4.0** component-notice wording, unchanged original image status, and translation-only/no-training distinction. No new general license/supply audit was performed. No browser, HTML reader, PDF builder or rendering tool was used; the explicit browser-policy stop remains respected.

## Drafting checks and stable handoff

Read-only checks run with Python `-B`, standard library and the existing markup validator; no output artifact or QA receipt generated:

- XML parses as `article`, exact unit/locale; NFC source text, no replacement characters; 57 unique IDs.
- All 55 actual pinned EN/ID original IDs retained once; all original ancestor/descendant ID relationships preserved.
- All 12 exact selectors match original direct-child order in both source versions.
- All 58 EN/ID MathML trees have identical tag/attribute/text/child structures; source punctuation tails do not create false math differences.
- All 54 unique `data-check` texts equal config `expected_math`; all nine required terms occur. These equality checks are regression checks, not mathematical proof.
- Existing `validate_markup` passes with the six expected asset IDs supplied in memory for this pre-freeze check. All six configured IDs are used once; no external automatic media, script or unsupported XML tag. This does **not** replace root's byte-pinned build.
- All 17 local targets resolve; all six actual question/solution anchor pairs are bidirectional. Five external citations are syntactically HTTPS, not claimed live.
- `Fraction` checks of six domain/range endpoint components and nine actual displayed evaluations; exact π-coefficient parsing of all three actual XML visible-zero lists and all **14** actual XML x-intercept pairs; three y-intercepts, three ranges and the two fractional-π normalization identities agree with personally read source graphs/answers. The first three interval extrema depend on complete-curve inspection, not a finite-sample universal inference. Infinite domains/periodic continuations are explicitly source-premised as above.

Final writer-owned bytes before root freezes assets:

| File | Bytes | SHA-256 |
|---|---:|---|
| `translations/MR-BRIDGE-014.xml` | 40452 | `c23c141d02e7077a783e64f62b95680bf3136768ccf3c01bf4296613f0723a7f` |
| `units/MR-BRIDGE-014.json` | 2905 | `44669087a38fb0901213b230d65cca3046e9aa465018afa51164956f750c6b30` |

Only these two files and this drafting note are owned/changed by this task; ignored selected image-review copies were prepared by the authorized helper. Root owns freeze/build, independent source/math review, format-specific reader QA, global terminology decisions, status/coverage and commits. The asset insertion will legitimately change the config hash. Safe next source marker after this complete section: **`A20:m81374#fs-id1167836597228` — Key Concepts**. Do not convert this drafting handoff into ready-reader or module-completion status.

## Primary integration correction after independent review — 2026-08-31

The independent reviewer found that the original notes/draft overattributed a repeating-pattern premise to025. Root directly reread the actual frozen EN/ID media descriptions for024,025 and026 and the complete Marathi Try It3 question/answer/notes.024 and026 explicitly describe the pattern continuing;025 says only that the line extends indefinitely left/right. Root changed the shared introduction,025 alt and Try It3's added g/h/e explanations to keep this difference explicit. The unchanged source answers still give all-real domain and range[-2,2]; the global(nπ,0) extension is now explicitly conditional on an authored same-wave-repetition assumption, not attributed to the source or proved from arrows. Existing54 mathematical strings, all source IDs, figures and supplied answers are unchanged. The earlier writer XML hash and unconditional pattern-premise assertions above are historical, superseded in this narrow respect.

The primary also actually read fresh C20 open/closed/half-open interval rows; T030 अंतराल is now narrowly canon-supported, while the compound अंतराल-संकेतलेखन remains authored. Root's two direct32824 attempts failed502, so no primary C22 reading or catalog addition is claimed. Current asset freezing and structural rebuilding are separate from independent final tests and reader acceptance; no browser or PDF review is added by this correction.
