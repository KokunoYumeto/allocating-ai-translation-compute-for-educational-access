# Independent review — TE-B001

2026-08-30. Independent AI-assisted content/structure review, **not a native-speaker review**, classroom trial, or placement-test validation. Translation and build code were not changed by this review.

## Scope and evidence actually read

Read AGENTS.md, USER_INSTRUCTIONS_VERBATIM.md, GOAL.md and DECISIONS.md; the entire translation map, bridge.xhtml, canonical subsection TE-B001.en.cnxml and generated TE-B001.te.cnxml. Also inspected the number-line SVG source and build receipt/code for the scope of their claims.

Read OCR text and visually inspected all four corresponding PNGs: downloads/canon/ocr/TS-p032, TS-p033, TS-p034 and TS-p042 (printed pages 20, 21, 22 and 30). The images, not erroneous OCR characters, supplied the wording/number evidence:

- p032: grouping objects as పదులు and ఒకట్లు; count-to-tens tables.
- p033: positional decomposition, including 4 tens + 1 one = 40 + 1 = 41.
- p034: చిన్నసంఖ్య / అతి పెద్దసంఖ్య / అతి చిన్నసంఖ్య and finding numbers between two bounds. Its first comparison example is 30 and 60; OCR loses 30.
- p042: అంకె, స్థానం, స్థాన విలువ, సహజ విలువ; వందలు, పదులు, ఒకట్లు; multiplicative place value in 746 and 805. The image explicitly separates place value from face value and shows zero's place value is zero. OCR corrupts several multiplication expressions, so those strings were not copied.

This evidence supports the pilot's Telangana place-value and comparison language. These four pages do **not** attest the selected Telugu labels for counting numbers, whole numbers, integers, origin or coordinate, nor do they establish Andhra Pradesh usage. Retain separate AP/TS ledger fields and provisional status for unwitnessed terms; do not label this review as regional terminology approval.

Follow-up evidence was then acquired and independently checked in this review: OCR text TS6-toc-009, TS6-sets-026, TS6-sets-027, TS6-sets-083 and TS6-sets-085 under downloads/canon/ap; PNGs 009, 026, 027 and 085 were visually inspected. The official [Telangana Grade 6 mathematics PDF](https://scert.telangana.gov.in/PDF/publication/ebooks/6TM_MAT.pdf), locally TS-6TM-MAT.pdf, supplies the decisive set definitions in R0. The directory name `ap` does not make this an Andhra Pradesh witness. No general license/supply audit was conducted.

## Findings and exact suggested corrections

### R0 — High: reverse the draft's whole-number/integer Telugu label assignment

Locations: TE-B001.te.json, bridge.xhtml, terminology ledger and any hardcoded learner title in the builder; regenerate CNXML and reader after correcting the human-authored sources.

Directly inspected TS Grade 6 printed p16 (PDF p26), §2.2, names `W = {0, 1, 2, 3, …}` **పూర్ణాంకాలు**. Printed p75 (PDF p85) names `Z = {…, −3, −2, −1, 0, 1, 2, 3, …}` **పూర్ణసంఖ్యలు**. Printed p16 §2.1 also witnesses **సహజ సంఖ్యలు** for `N = {1, 2, 3, …}`. Therefore the pilot's existing whole-number/integer name pair is reversed against this exact Telangana canon. Correct English glosses and correct calculations do not remove the learner-facing terminology error.

Required mapping for the reviewed TS convention:

| Meaning | Correct learner label | Required inflection examples |
| --- | --- | --- |
| whole number(s) | పూర్ణాంకం / పూర్ణాంకాలు | పూర్ణాంకాల, పూర్ణాంకాలను, పూర్ణాంకాల్లో, పూర్ణాంకమా |
| integer(s) | పూర్ణ సంఖ్య / పూర్ణ సంఖ్యలు | పూర్ణ సంఖ్యల్లో; the textbook also closes the word space: పూర్ణసంఖ్యలు |
| counting/natural numbers starting at 1 | సహజ సంఖ్యలు | Retain current meaning and source convention |

For the bridge convention note, use:

> ఈ పాఠంలో సహజ సంఖ్యలు (counting / natural numbers) 1 నుంచి మొదలవుతాయి. పూర్ణాంకాలు (whole numbers) 0 నుంచి మొదలవుతాయి. పూర్ణ సంఖ్యలు (integers) అంటే …, −2, −1, 0, 1, 2, … వంటి సంఖ్యలు; వాటిని తరువాత నేర్చుకుంటాం. కొన్ని ఇతర పుస్తకాలు natural numbers లో 0 ను కూడా చేరుస్తాయి. ఇక్కడ మాత్రం మూలపాఠం నిర్వచనాన్నే అనుసరిస్తాం.

Apply the whole-number label consistently to titles, terms, questions, explanations and solutions; preserve all source IDs and MathML. Review singular/plural/case endings explicitly rather than a naive two-way string swap. Log that this is verified TS usage and keep AP evidence separately unresolved unless independently witnessed. Do not change the underlying sets or silently claim there is a regional difference.

### R1 — Medium: make the bilingual routing rule unambiguous

Location: translations/bridge.xhtml, English paragraph immediately after `id="routing"`.

The Telugu rule allows a learner with 0/2 or 1/2 entry answers to read support and then qualify on the two recheck answers. English currently says two correct answers per skill are required **followed by** two correct recheck answers, which can be read as requiring a previously successful entry check as well. The intended repair route should not depend on which language the teacher reads.

Replace the English paragraph with:

> For each skill, an entry score of 0/2 or 1/2 leads to the relevant support; a score of 2/2 leads directly to the recheck. Mark that skill ready for this small unit only after both corresponding recheck items are answered correctly with explanations. An earlier entry score below 2/2 does not prevent readiness after support. The threshold is an editorial rule, not an empirically validated mastery cut score. Keep results on paper; the reader stores nothing.

In the Telugu scoring paragraph, explicitly append the recheck mapping for teacher usability: `మళ్లీ-తనిఖీలో K1 = R01–R02; K2 = R03–R04; K3 = R05–R06; K4 = R07–R08.` The individual item labels already encode this mapping correctly.

### R2 — Medium: restrict equal spacing to the scale used here

Location: bridge.xhtml, K3 support, opening sentence.

`సంఖ్యారేఖలో పక్కపక్క గుర్తుల మధ్య దూరం సమానంగా ఉండాలి.` overgeneralizes to all adjacent labels on any number line. A valid line may label 0, 1 and 3 with unequal gaps. The source refers specifically to equally spaced consecutive counting-number marks.

Replace that sentence with:

> ఈ పాఠంలో సంఖ్యారేఖపై వరుస పూర్ణాంకాలను ఒక ప్రమాణం దూరంలో గుర్తిస్తాం.

The existing 0–6 SVG itself has correct equal spacing and directions; no diagram correction is needed.

### R3 — Low: small Telugu learner-language polish

These are suggested clarity edits, not mathematical corrections or claims of official regional usage:

- TE-B001.te.json `s088`: replace ` సహజ సంఖ్యలు మొదలయ్యేది ` with ` సహజ సంఖ్యల ప్రారంభ సంఖ్య `. This reads smoothly before the preserved MathML `1,` and the existing `కాబట్టి`; do not move or alter the mathematical punctuation.
- bridge.xhtml D02: use `4 సహజ సంఖ్యా, పూర్ణాంకమా, లేక రెండూనా? కారణం చెప్పండి.` This also applies R0. The existing `రెండూ అవుతుందా` is understandable but awkward.
- K4 support: replace `సమాన అంకెల సంఖ్య ఉన్న రెండు సంఖ్యలను పోల్చేటప్పుడు` with `ఒకే సంఖ్యలో అంకెలు ఉన్న రెండు సంఖ్యలను పోల్చేటప్పుడు`. This reduces the ambiguity of “number of digits” for an early learner.

## Checks passed and limits

- Independent read-only XML comparison: 204 elements in the same tag/namespace sequence and nesting depths; all 44 source IDs preserved; all 133 MathML elements present, with terminal mathematical tokens unchanged except the intended `and` → `మరియు`. All existing attributes are unchanged except the localized image alt text, image source and MIME type; the sole added attribute is `xml:lang`. There are 17 mathematical expressions and three source exercises. This is not full-book CNXML schema validation.
- All 47 bridge IDs are unique; all local bridge fragment links resolve. D01–D08 and R01–R08 each have a worked solution. Both source Try It additions provide the reasoning absent from their short source answer lists.
- All inspected classifications, decimal/fraction exclusions, comparisons, expansions and coordinate-step answers are correct. In particular 6/3 = 2 and 12/4 = 3 correctly prevent “fraction notation implies non-whole” overgeneralization. 5/3 is correctly placed between 1 and 2. Zero is correctly included in whole numbers and excluded from this source's counting/natural numbers.
- The bridge's English glosses and explicit sets distinguish whole numbers from integers and state the natural-number convention. **The reviewed draft's Telugu names are reversed against the verified TS witness**, as documented in R0. The arithmetic/structure pass is not approval of those names.
- Source subsection meaning is retained, with original bridge explanations separated from translation. The next-unit marker correctly disclaims the rest of m81243. Place-value support follows the observed canon's place/digit/value distinction.
- No arithmetic or source-structure blocker found. Apply R0, R1 and R2 before treating the editorial pilot review as closed; then rebuild and retain the separate outstanding fluent-Telugu/native-speaker and classroom review limitations.

## Reviewed snapshot (SHA-256)

| File | SHA-256 |
| --- | --- |
| translations/TE-B001.te.json | `6c59cfc93dfe108795337b6932979f0c5f4a929f6e46d8ec1abdc603e011a909` |
| translations/bridge.xhtml | `b4a6a73a19d860c27583b8090e4bde7aca4316324625ee1ff9d599f557dd92e6` |
| sources/TE-B001.en.cnxml | `009af74aadcc64f360a5f93094588d0c0a45f0400844f7f01933b370b37c2e66` |
| generated/TE-B001.te.cnxml | `72b35f0dc2551752f9629e7bd9214fca27708d81fe86c7136969e9a3b1e95c47` |
| TS6-sets-026.png (terminology evidence) | `e22496bf6269a98db819536ee6101ca8f7cf404e81b556d34f2f6a1dde0c1867` |
| TS6-sets-085.png (terminology evidence) | `12c82441ed5e1e0e8fe6a840c63542ae0d854fe39602c44ecde6bdb09142ecdd` |

## Resolution recheck — 2026-08-30

The historical findings and initial hashes above remain unchanged. This section records the corrected snapshot, not retroactive approval of the original draft.

- **R0 resolved for the witnessed TS convention:** the translation catalog, restored bridge, generated terms and learner title consistently use పూర్ణాంకాలు for whole numbers, పూర్ణ సంఖ్యలు for integers, and సహజ సంఖ్యలు for counting/natural numbers starting at 1. Singular, plural and case forms were checked, including పూర్ణాంకం, పూర్ణాంకమా, పూర్ణాంకాల, పూర్ణాంకాలను, పూర్ణాంకాల్లో and పూర్ణాంకాలూ. The mathematics and source IDs were not altered to accommodate the terminology correction.
- **R1 resolved:** the English repair/recheck rule agrees with Telugu, and the K1–K4 recheck-item mapping is explicit.
- **R2 resolved:** equal spacing is restricted to consecutive whole-number marks in this lesson.
- **R3 resolved:** the suggested s088, D02 and K4 wording edits are present. A further minor S-R04 inflection/phrasing issue introduced by the noun replacement was also corrected to `అందువల్ల 12/4 విలువ కూడా పూర్ణాంకమే.` Its calculation remains 12 ÷ 4 = 3.
- **Central ledger mapping checked:** canon/TERMINOLOGY.tsv records the verified N/W/Z labels with the correct TS page references, treats the integer-word spacing as editorial, leaves AP evidence as not acquired, and retains origin/coordinate as provisional. This does not certify every ledger row or establish an AP–TS difference.
- **Restoration verified:** the source is no longer empty. During the disk-full pause, this reviewer independently validated the preserved reader's complete 10,732-character namespace-restored bridge in memory. Recovery and the main task's exact pre-polish rebuild match are logged in D023. The current bridge and current reader bridge are identical after XML normalization; the final S-R04 polish is present in both.
- **Read-only structural recheck passed:** 204 source elements, 44 retained source IDs and 133 MathML elements; tag/namespace sequence and nesting preserved; terminal mathematical tokens unchanged except the intended prose `and` → `మరియు`. The bridge has 113 elements and 47 unique IDs, all 8 entry items, 8 recheck items, 16 paired solution IDs and both source worked-solution additions. All 16 bridge fragment links resolve.

No unresolved correction remains from R0–R3 in this snapshot. This remains an independent **AI-assisted** editorial/structural review, not a native-speaker review, AP terminology approval, full-book schema validation or classroom validation. No downloads, build, or translation/code edits were performed during this final recheck; only this resolution section was appended.

### Corrected snapshot (SHA-256)

| File | SHA-256 |
| --- | --- |
| translations/TE-B001.te.json | `38f2622a4ea91a79c8336809a2345df5a7978f3998e0735bc0df26b538b81ab8` |
| translations/bridge.xhtml | `c85c932c808af5ade3fb86221f79abc5f22ab70a359823e5e787a256d9f9dd31` |
| sources/TE-B001.en.cnxml | `009af74aadcc64f360a5f93094588d0c0a45f0400844f7f01933b370b37c2e66` |
| generated/TE-B001.te.cnxml | `be91cfd2cc67efa237acdb5c0ec21075913d5b4dbdbd16406107046a480e4bca` |
| reader/TE-B001.html | `123ca96bd7124dae10f55fab010a7c246c9dafc872cd9a458cf986b0479053b7` |
| canon/TERMINOLOGY.tsv | `fbbdd1e2dc6158dec2f7c46274c14d80f92c43dea2d798d6b29468dfc4410e1a` |

Post-review ledger-only recheck, 2026-08-30: the ones-row note now reads “Use the witnessed plural; positional inflection ఒకట్ల స్థానంలో.”; the chosen term ఒకట్లు and evidence fields are unchanged. Updated canon/TERMINOLOGY.tsv SHA-256: `99f889059b5f0c7d70a09f39f9236a74da4dfc7ef107494fee122cdda7d5c786`.
