# A10-003 language and source notes

## Scope and status

Self-reviewed Shahmukhi Punjabi draft, not native-speaker or educator certification. The full five-work assignment remains active. No statement here completes A10 or the whole module.

The selected canonical nodes are the standalone paragraph `newelem_para01`, immediately following A10-002, and the **entire** section `fs-id1170655199097` (“Identify Multiples and Apply Divisibility Tests”). They are content children3–4 (zero based). The section has17direct children including its title; the last is TryIt `fs-id1170655200179`, ending at answer paragraph `fs-id1170655247402`. Stop before `fs-id1170655247410` (“Find Prime Factorizations and Least Common Multiples”). No intervening node was skipped.

The excerpt contains40sourceIDs,178source-block keys,15paragraphs,5titles,1direct-text activitynote,2alts,2summaries,148tablecells,5bulleteditems,3MathMLtrees,3links,3terms and1newline. The148cells comprise130multiples-grid cells and18worked-table cells;4worked cells are intentionally empty. Of the130grid cells,120are literal numeral cells and10are header/row-label text. There are no source figures or circled part labels.

Canonical input: `downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82452/index.cnxml`, SHA256 `0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310`, pinned commit `38cae454e644abf9f0a623e876994553881597c9`. The complete English scope and corresponding Indonesian scope at `downloads/extracted/A10/translated/modules/m82452/index.cnxml` were actually read, including both complete table summaries and all cells. Indonesian SHA256 is `940ad448d8b2788984f386405131866fe32abb95f0f9c2a901ca1f4e3619a6fb`.

## Actual canon consultations

The actual `read_canon.py` script was run with `--unit A10-003`, using `next-unit` for source analysis and then draft, revision and qa. Existing local HTML supplied R1,R2,R3; no new download was required. The script refreshed ignored text snapshots and wrote these unique receipts:

- next-unit: `languages/pnb-Arab-PK/canon/receipts/A10-003-next-unit-20260831T002823853236Z.json`; SHA256 `bafd11265021b33e2c3a87bf556ab70fdd1b511900bd33ed3cca61ea6f5112a9`; IDs C01, C02, C03, C04, C07, C09, C10, C11.
- draft: `languages/pnb-Arab-PK/canon/receipts/A10-003-draft-20260831T003645612139Z.json`; SHA256 `6943320da7d4d37caafae20bb9670d455f7d26f31e71fc924443fbb483d0404f`; IDs C01, C02, C03, C04, C07, C09, C10, C11.
- revision: `languages/pnb-Arab-PK/canon/receipts/A10-003-revision-20260831T004508974068Z.json`; SHA256 `5cd980be9117da8c35dfb120af31806ac5fc12310af805e8adf0e92b413c682b`; IDs C01, C03, C04, C07, C09, C10, C11.
- qa: `languages/pnb-Arab-PK/canon/receipts/A10-003-qa-20260831T005247915373Z.json`; SHA256 `f946c3630314aee608e2ae4296dba5b5402e94b725881a3215d56079c2db48ed`; IDs C01, C02, C03, C04, C07, C09, C10, C11.

Selected passages were displayed and read, not merely receipts generated. Receipt application fields are inherited older PNB-001/ordered-pair/input-output descriptions; they are **not** A10-003 decisions. Actual use here:

- C01, R1, «بیان کیتی جا سکدی اے»: ability/passive syntax guided «لکھیا جا سکدا اے», «لبھ سکدے آں» and the repeated «پورا ونڈیا جاندا اے». Gender/number agreement was checked rather than mechanically copying the feminine canon form.
- C02, R1, «پڑھنا چاہیدا اے»: reader-directed instructional register informed the choice of short «ویکھو» and «پتا کرو» prompts. The precise obligation phrase was not inserted where the source has none.
- C03, R1, «ترتیب وار»: consulted as ordinary sequencing prose when checking row/cell order; no new mathematical term or extra source sentence was derived from it.
- C04, R1, «صفحے گھٹ ودھ وی ہوندے رہے»: plural quantity/agreement review supported «علامتاں … نیں», «مضاعف … نیں» and «پورے ونڈے جاندے نیں».
- C07, R2, «دُوجے صفحے اُتے»: ordinal/location syntax informed the summary’s پہلی/دوجی/تیجی … سطر and above/below descriptions. It does not establish mathematical vocabulary.
- C09, R3, «چیتے رہوے کہ»: reminder phrasing occurs only in the original bridge’s counting-number/nonzero-divisor qualification, not as an unmarked addition to source definitions.
- C10, R3, «وضاحت منگدی اے»: guided keeping the table-range and zero/domain qualifications explicitly separate from the faithful source text.
- C11, R3, «کیوں جے»: consulted for reason-giving syntax. The source already supplies “so”; Punjabi «سو» was retained in its worked conclusions rather than forcing a borrowed connective.

This small prose canon is three essays by one author, not a mathematics terminology standard. It provides neither native-speaker certification nor evidence that مضاعف is a standardized Punjabi school term.

## Language decisions and revision

The working terms are «مضاعف» for multiple, «ضرب دا حاصل» for product, and «نال پورا ونڈیا جاندا اے» for divisible by. They are provisional pedagogical choices. The original bridge labels their English/Urdu correspondences; Urdu spans are isolated terminology comparators, not a replacement for Punjabi prose. «مستقل / متغیر» likewise remains a provisional bridge for constant/variable. Shared terminology files were not edited.

Punjabi grammatical forms اسیں، تُسیں/تہانوں، جیہڑا، جدوں، نال، وچ، اے، نیں، ونڈدے آں are retained. There is no Gurmukhi text or Urdu verb substitution. Revision corrected the prelude from the incomplete «جیہدی قدر پتا نہیں» to «جیہدی قدر دا پتا نہیں». The future-source-discussion sentence is translated faithfully; the original note clarifies that this bounded reader does not itself supply the later constant/variable discussion.

All13source italic Latin symbols are preserved in order: a,b,c,m,n,x,y,n,n,m,n,m,n. Each is individually LTR-isolated inside emphasis. Three inline term IDs are retained; product keeps source no-emphasis. Punjabi word order may move a source emphasis relative to its noun without changing the underlying symbols or meaning.

The three original MathML trees are referenced only by per-owner placeholders. The target paragraph `fs-id1170655163445` ends “… قدر نوں ایویں لکھ سکدے آں: {{math:1}}”, keeping the exact multiplication expression and its source terminal period at the end. No MathML text/node/punctuation editing is required. English “15 is5·3” is rendered as writing15’s value in that form, not changing the identity.

The activities’ English name remains available in the original bilingual key. Source “Manipulative Mathematics—Multiples” is a reference, not a claim that the activity itself is included. Ordinary image-alt and summary punctuation is translated normally; Western digits and comma grouping are retained. Alts/summaries are plain accessible text; rendered prose/numeric cell fragments use LTR bdi.

## Source discrepancies and observations

1. Paragraphs `fs-id1170654984223` and `fs-id1170655229926` describe multiples2through9, while the actual table also includes a10row. Indonesian retains the same scope understatement. Source-bound Punjabi preserves2through9; the explicit original `a10-003-table-range` note points out10. This is not a wrong table/summary digit and does not require an accessible-summary override.
2. The definition uses a **counting number**, whose source convention starts1,2,3. The symbolic divisibility definition does not state a nonzero-divisor condition. Those source words remain unchanged. The labeled original `a10-003-domain-note` explains this positive-whole-number lesson, wider zero-multiple usage, and that division byzero is undefined. It does not silently expand the source definition or claim its tests fail for all other cases.
3. English alt “elipsis” and worked-table “divisble” are spelling errors with clear meanings. The exact canonical witness preserves them. Punjabi translates their meanings; no artificial target typo is introduced.
4. The multiples-table summary has malformed curly-quote/comma punctuation around30,36,42 in its sixth-row description. Punjabi normalizes ordinary list punctuation while preserving the complete numeral sequence; Indonesian also normalizes this punctuation. There is no numerical correction or shortened summary.
5. The worked question asks2,3,5,6,10, while its table checks2,3,5/10,6. Both source orders are preserved. The worked table has a legacy `summary` attribute, unlike the first table’s `aria-label`; metadata records the distinction.

No image-alt or table-summary override was declared: actual evidence did not identify a content mismatch in these four accessible descriptions. If later evidence does, preserve source-bound strings as traceable data and add explicitly original corrected descriptions/advisory links, following the current accessibility policy.

## Original image inspection and rights limits

Both JPEGs were actually viewed with original detail and checked against their exact existing A10 media-authority rows:

- `CNX_ElemAlg_Figure_01_01_012_img_new.jpg`:393×43,35553bytes,SHA256 `a63c6ef521ecd54a1231f038761a19918b861e7bc9c9f4a5b3e5a23cb42dd23f`; top2,4,6,8,10,12,… and bottom2·1 through2·6.
- `CNX_ElemAlg_Figure_01_01_013_img_new.jpg`:391×43,36239bytes,SHA256 `477ed8d13d5fcc4d068fde971c8de9aeebc35e1bc3c87cbba015b0e0367bc89c`; top3,6,9,12,15,18,… and bottom3·1 through3·6.

Both source MIME declarations agree with actualJPEG bytes. Their red multiplication rows and left-to-right alignment match the source alts. They are direct-section media, not numbered source figures. The original symbol key explains multiplication dots and continuation ellipses without editing the images.

Existing A10 component/NOTICE/LICENSE policy is retained, with CRLF→LF logical notice pins. The media authority CSV establishes bytes/blob identity only and supplies no new rights clearance. No repeated license/supply audit was done. At this input checkpoint, no assets, reader or builder had been created.

## Pre-render verification and remaining work

A read-only diagnostic passed1141checks over178key order, all source prose numeral sequences,3mathindices,3linkindices,1newline,13Latinitalic symbols,sourceIDs,original bridgeanchors,bidi/script exclusions and excerptpin. An earlier diagnostic incorrectly removed MathML tails while excluding math text; preserving tails fixed that **diagnostic** and verified the source’s prose5and15. No translation was changed to satisfy that false alarm.

Separately, both selected whole subtrees matched canonical expanded tags, attributes, text, descendants and child tails. Indonesian tag/ID/src/link sequences matched. All108grid products were recomputed. For tested divisors2,3,5,6,10:5625 succeeds at3and5;4962 at2,3,6;3765 at3and5. The source digit sums18,21,21 agree. All148cells, including4blanks, remain present.

These are input checks, not independent rendered QA or browser proof. The13-column table needs source-driven headers and local scroll; the9×2table needs exact empty cells, legacy-summary handling and no invented headers; the direct-text activity must not vanish; the explicit Solution title must appear once. The source is example6. A later isolated build must preserve exactMathML,source/container text/tails, all40IDs,2originalassets/notices, and source/main/body framing; anonymous narrative injection must be rejected.

Native-speaker and mathematics-educator review are pending, especially multiple/divisibility terminology and instructional idiom. Browser/mobile accessibility review and independent mutation QA are also pending. No full-work completion claim is made.
