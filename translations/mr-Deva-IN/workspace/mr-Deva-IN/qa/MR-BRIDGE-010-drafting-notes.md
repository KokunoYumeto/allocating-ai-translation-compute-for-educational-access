# MR-BRIDGE-010 drafting handoff

2026-08-31; source_review. Owned only translations/MR-BRIDGE-010.xml, units/MR-BRIDGE-010.json and this note. Root retains freezing, asset-config insertion, build/render QA, shared logs and acceptance. No browser actions, shared-file edits, build, commit or publication occurred. This checkpoint completes the previously unselected blocks within this one teaching section; it does not claim completion of m81373 or the five-book assignment.

## Actual source inspection and bounded scope

Read the actual EN/ID CNXML in memory from downloads/mr-Deva-IN/releases/A20-canonical.zip and A20-v0.3.0-source.zip. EN member: osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml. ID member: source/modules/m81373/index.cnxml. Read both whole section structures, then all selected text, formulas, answers, original IDs and media descriptions. Truncated raw-output portions were explicitly reread to finish the EN final Try It and ID opening paragraph.

Section: fs-id1167824731607, “Find the Value of a Function.” Both pinned trees have 24 direct non-title blocks, 141 IDs including the section, 3 formal worked examples, 9 exercises with 9 solutions, and 38 images. The entire new remainder is small enough for one unit; no teaching cluster was split.

Six complete blocks are already selected elsewhere and are excluded, not merely omitted from a counted parent:

| Already selected block | Existing unit | IDs excluded |
|---|---|---:|
| fs-id1167836521479 | 001 example 7 | 26 |
| fs-id1167829859398 | 001 example 8 | 27 |
| fs-id1167833158753 | 002 worked email model | 15 |
| fs-id1167833369424 | 002 Bryan practice | 8 |
| fs-id1167836481611 | 002 Anthony practice | 8 |
| fs-id1167833128952 | 002 online resource note | 3 |

The 18 new selectors contain 53 IDs; the uncounted section wrapper adds one, yielding 54 preserved original IDs and 59 XML IDs in all. Source order is unchanged. The section wrapper/title is preserved without data-source because counting it would duplicate those six complete blocks. The definition notes overlap conceptually with 003's recap but have distinct, previously unselected source IDs. Original asides point to the prior material without copying its examples or identifiers into the new source counts.

Classification: source_count 18; translated_worked_examples 0; translated_definitions 2; translated_practice_items 4; translated_resource_notes 0; original_practice_items 0; question_ids []. There are two introductory worked calculation tables, but no newly selected formal source example. The tables and ten prose blocks are the 12 unclassified source blocks rather than artificially raising the worked-example total. The four Try Its contain 12 subparts and four original supplied-solution containers. No new full answer or question is authored.

### Ordered selectors, all prefixed A20:m81373#

| Selected ID | IDs including descendants | Kind |
|---|---:|---|
| fs-id1167836315013 | 1 | Opening notation prose |
| fs-id1167824735502 | 4 | Notation definition |
| fs-id1167833186483 | 1 | Variable-role prose |
| fs-id1167829620795 | 3 | Variable-role definition |
| fs-id1167836362234 | 1 | Reassurance about unfamiliar notation |
| fs-id1167833051398 | 1 | Equation-substitution introduction |
| fs-id1167833202337 | 4 | First three-row calculation table |
| fs-id1167829718470 | 1 | First result statement |
| fs-id1167836560949 | 1 | Function-notation substitution introduction |
| fs-id1167836326537 | 4 | Second three-row calculation table |
| fs-id1167836456485 | 1 | Second result statement |
| fs-id1167836629682 | 1 | Evaluating a function |
| fs-id1167836388368 | 7 | Try It 1 + source answer |
| fs-id1167824578714 | 7 | Try It 2 + source answer |
| fs-id1167836518536 | 1 | Bridge to symbolic arguments |
| fs-id1167836730594 | 7 | Try It 3 + source answer |
| fs-id1167825766170 | 7 | Try It 4 + source answer |
| fs-id1167836283159 | 1 | Bridge to everyday models; last new block |

All 53 selected IDs occur under the corresponding target wrapper in both EN/ID comparisons. Preserved solution anchors, in order: fs-id1167833135306, fs-id1167829783753, fs-id1167836624292, fs-id1167829743779. Original problem anchors are respectively fs-id1167836520515, fs-id1167833269886, fs-id1167829788685, fs-id1167829850927; each has a working answer link and return link.

## Source corrections and mathematics

- EN Try It 2 answer paragraph fs-id1167836732807 omits f from part (a), displaying (2) = 13. ID correctly has f(2) = 13; the actual question and substitution agree. The Marathi supplied-answer heading and adjacent original note explicitly restore the missing f; this is not silently classified as a new answer.
- EN alternative text for image 013b is garbled (“4 ×7 2 ×1 5”). The actual raster is y = 4 · 2 − 5, with the substituted 2 red. ID pixels and alternative description agree with that calculation. Accurate Marathi alt follows the pixels and discloses the correction nearby.
- EN and ID alternative descriptions for 013c interpret y = 3 as a horizontal line. That equation could describe such a line elsewhere, but this table is evaluating y = 4x − 5 at x = 2. The Marathi alt and visible original note retain the evaluation context and explicitly avoid saying the original function is 3 for every input.
- The bridge paragraph fs-id1167836518536 says the preceding example evaluated a constant input. The referenced 001 example 7 also includes f(a). The translation preserves the source bridge while an original note warns against reading it as a claim that every preceding part was numeric. The next worked example is identified as 001 example 8, not silently duplicated.

All four supplied answers were recomputed: 22, 6, 3t² − 2t + 1; 13, 3, 2h² + 4h − 3; 4m² − 7, 4x − 19, 4x − 12; 2k² + 1, 2x + 3, 2x + 4. The two tables both yield 3 at input 2. Symbolic checks separately verify g(x − 3) versus g(x) − g(3), and h(x + 1) versus h(x) + h(1). Numeric spot checks supplement the direct algebra, not replace it.

An original note states the standard real-input interpretation for these unrestricted polynomial/linear practice formulas; the source does not explicitly declare a narrower domain. This is not imported into the separately constrained email model in 002. Each question's own formula applies even when the function name f is reused. The source distinction between function-argument parentheses and multiplication is retained. The two definition-equation IDs are retained on div/ul text equivalents; the two table IDs wrap actual tables in sections so generated source labels remain valid HTML.

## Personally inspected media and root asset handoff

Checked 10,741,833,728 free bytes on C before small writes. The authorized existing freezer --review-images command copied only these six EN and six ID members to ignored downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-010. No archive was fully unpacked, no new material downloaded and no cache/build was made. Personally read all 12 images through the permitted filesystem viewer, not through browser automation and not merely from alt text.

All are image/jpeg. Keep the unchanged EN originals. The ID rasters are comparison-only; 014b colors both instances of 2 red while EN colors only the right-side substituted 2. The math is identical. The canonical EN images are small equation strips (not full diagrams); root should check their legibility in the offline rendering without claiming a higher-resolution source.

| EN filename | Original media ID | Bytes | SHA-256 |
|---|---|---:|---|
| CNX_IntAlg_Figure_03_05_013a_img.jpg | fs-id1167836353205 | 15640 | 15dc68980fadea9e7ba3f45424660e0a0d250d887eec3d4ff2868c9b5caf0e9d |
| CNX_IntAlg_Figure_03_05_013b_img.jpg | fs-id1167836433912 | 17286 | e848a25b5ab599bcaed5af5663b1e29e6794b038548d12cf86eb1db04100f8a5 |
| CNX_IntAlg_Figure_03_05_013c_img.jpg | fs-id1167832926879 | 14440 | 6325f8076b62e3d302e189448ec013b0f491c9fe3b34459fb2b4c4c331f45d19 |
| CNX_IntAlg_Figure_03_05_014a_img.jpg | fs-id1167836447887 | 16628 | ea1677c72a05ebd74da8fa57fd50aab6eecc596582592b3fee11eceeb3aa8524 |
| CNX_IntAlg_Figure_03_05_014b_img.jpg | fs-id1167836314769 | 18508 | 9e2bfcd6881e9e350bb261ba99fbca33dcee66798f79ef44aa1eddcd2ef8f9d9 |
| CNX_IntAlg_Figure_03_05_014c_img.jpg | fs-id1167836399865 | 15652 | 651b0da087ab2e5061a8880ca3712a524f5480882ebafc8ceb0906a8ee107b82 |

EN total 98,154 bytes; ID total 516,763 bytes. ID hashes in the same order: 4784dcfb3c1383925f742da34ffb5b23a43ec5ecc7fa38d37890fa5d3f3b0347; a1738ecbe38f2ad27ba4cf9bcb7136e828521d4a31bfa3105d9172f4d8bae29a; 1b0341a662f9305e7e8837990fb8902bd9edf4a60153b8f106a3fb56f16de884; 68dd8fb5ff531bc0ddb6882b190b087f706075973c2922806f777d8e6a341f2d; 58a8fe28a0943805fa070f44764c3e1aa74ffb9c39a28cc4c0de306d77e343b2; c6dd366d48e3f5ba67147b4c9a2a76f18eddb86e9ea76863436ce9690829d81e.

No selected media is missing or redrawn. No original image, CNXML, snapshot or source pin is changed. Config asset records are intentionally left for root's freezer.

## Marathi canon: actual stage-specific reads

Reread AGENTS.md and USER_INSTRUCTIONS_VERBATIM.md, the current canon README and the relevant existing pilot passages. Read actual 001 examples 7–8, not just their names, and 003's definition/clarification prose. Their examples are not new source counts in 010.

- Selection: read the existing BB8 C12 physical-page-85 OCR opening prose (printed p75) and C13 physical-page-86 OCR (printed p76), distinguishing expression evaluation from finding an equation's solution. Read actual searchable [MV-F prose](https://marathivishwakosh.org/21979/) for C14–C17: dependence, each permitted input's single output, domain/codomain naming, person/task example and constant-function paragraph. A first broad search did not retrieve the intended page; the targeted search succeeded. No missing QuickLaTeX formula images were treated as read.
- Drafting: read BB8 physical-page-34 OCR (printed p24) and personally inspected the existing page PNG because its OCR formulas are garbled. In particular the mixed signs/parentheses in C06 and two negatives in C09 were actually visible; they support grouped substitution and sign checking. Used the read 001 negative-input and whole-argument examples while translating the Try Its. The same actually retrieved MV-F passages guided wording about a permitted input and its resulting value. No new OCR or PDF rendering was necessary; the pre-existing OCR was read first.
- Revision: freshly retrieved and reread MV-F's opening dependence, definition/naming and final constant-function prose after the draft. Revisited the inspected BB8 sign/grouping examples and C12/C13 operation wording when checking the algebra and “मूल्य काढणे” language. Did not claim a new visual reading of BB8 p75/p76 formulas: only their readable OCR prose was used in this checkpoint.

Concrete effects: retained प्रांत, मूल्यसंच, स्वतंत्र चल and अवलंबी चल consistently with 001–003. The witness attests अवलंबित but does not establish every full classroom term in the draft; those remain working choices, not newly canon-certified vocabulary. “Any value” is restricted to the stated domain, “independent” is not equated with experimental control, and dependence does not require a different output whenever the input changes. The y = 3 table conclusion was revised to say explicitly that it is not 3 for all x. Preserved complete parenthesized arguments rather than treating g(x − 3) as a difference of function values. Replaced a provisional use of प्रारूप in the closing bridge with plain गणिती मांडणी and retained 002's ईमेल-मॉडेल in the original cross-unit note. Corrected Marathi agreement in the credits. No unrelated graph/absolute-value canon was reread or counted just to inflate consultation totals; no native-speaker/teacher review is claimed.

Original additions are marked data-kind=original: scope and prior-unit references, restricted-domain/dependence cautions, the standard real-input convention, table captions and pixel-reading corrections, incomplete-source-bridge clarification, the g-argument versus output-subtraction explanation and the source f restoration note. They are not extra translated blocks, answers or practice items.

## References, local-reader limitation and exact next navigation

The selected 18 EN/ID blocks contain zero source link elements. The whole section's sole original external link is in excluded note fs-id1167833128952: https://openstax.org/l/37introfunction, already preserved in 002. It is not duplicated or counted in 010. The new reader's only HTTPS links are the existing license notice and actual Marathi canon reference; its 13 same-document links are navigation and the four question/answer pairs.

The existing builder permits only same-document fragments and HTTPS links. New original references to units 001–003 therefore name those units/examples without inventing unsupported local reader routes. Credits visibly state that direct cross-unit local links are unavailable. Root should address that reader-navigation need in its authorized integration workflow; the drafting agent did not edit the builder or bypass the documented browser/file policy.

Last new block: A20:m81373#fs-id1167836283159. The remaining source children after it are the four already selected 002 blocks (email example, two Try Its, resource note), then this teaching section ends. The immediate next source section is A20:m81373#fs-id1167829711772, Key Concepts, already covered in 003. There is no remaining 011 slice inside this function-value teaching section. Root's module coverage integration, not this bounded draft, should establish the next genuinely uncovered module cursor; no forward jump to m81374 or whole-module completion claim is made here.

## Read-only checks and limitations

Passed: parseable NFC XML/JSON; 18 exact ordered source selectors in both archives; all 53 original IDs nested under the correct selected wrapper plus the one uncounted section ID; 59 unique XML IDs; no overlap with existing other-unit selectors; all six excluded block IDs absent; 4 original problem/solution pairs; 46 exact expected_math strings; 10 required terms; the two table calculations and all 12 practice results recomputed. Generic validate_markup passed with an in-memory asset-name dictionary only: 13 valid internal links, 2 HTTPS links, 6 figures. Python checks used -B and created no files or caches.

No asset-config integrity, frozen-source build, layout, phone/desktop rendering, publication or final acceptance is claimed. Root must insert/freeze assets and run those checks. The independent reviewer may inspect this stabilized draft; no independent-review outcome is fabricated here.
