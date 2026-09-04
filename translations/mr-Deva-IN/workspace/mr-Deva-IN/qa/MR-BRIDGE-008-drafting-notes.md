# MR-BRIDGE-008 drafting handoff

Date: 2026-08-31. Drafting agent: source_review. This is an opening/first-teaching-section backfill within A20:m81373, not completion of that module, A20, or the five-book assignment.

Owned files: translations/MR-BRIDGE-008.xml, units/MR-BRIDGE-008.json, and this note only. Root owns source freezing, config asset records, builds, visual QA, shared ledgers and final acceptance. No build or rendered-output inspection is claimed here. The config deliberately has no assets object until root freezes the six canonical EN images.

## Source read and selected boundary

Read the actual English and Indonesian source in memory from the pinned archives, not the old extracted release:

- EN: downloads/mr-Deva-IN/releases/A20-canonical.zip, member osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml.
- ID: downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip, member source/modules/m81373/index.cnxml.

The selection includes the two previously unselected metadata-abstract elements, all three opening readiness notes, and the first teaching section through its final Try It. It excludes the already translated worked example fs-id1167836692527, which is MR-BRIDGE-001 example 6. A visibly original aside names that prior material instead of reprinting it. Its original IDs and data-source locator do not recur in this draft. The separate first-section Relation note fs-id1167836378970 is new source coverage even though the concept overlaps 001; it is not the later glossary definition fs-id1167833175472 already selected in 001.

The first-section context wrapper fs-id1167829789538 and its translated title remain in the XML without data-source. Counting that parent would falsely include the omitted 001 example. The metadata list is rendered as an identified section containing a ul; this preserves list-00001 while allowing the generic builder to append a valid source-label paragraph. Its three learning objectives belong to the whole original module. The introduction explicitly distinguishes those objectives from this first-section checkpoint.

Final classification: source_count 21; translated_worked_examples 2; translated_definitions 2; translated_practice_items 9 (3 readiness + 6 Try Its); translated_resource_notes 0; original_practice_items 0; question_ids []. The remaining 8 source blocks are metadata/prose/the symbolic student pair. All 11 exercise containers have supplied source solutions and preserve their original question/solution anchors. No newly authored complete answer or practice question was added.

### Ordered selectors and original ID counts

All selectors have prefix A20:m81373#. Counts include the selected root and every identified descendant; they match in EN and ID.

| Selected source ID | IDs | Classification |
|---|---:|---|
| para-00001 | 1 | Metadata objective introduction |
| list-00001 | 1 | Metadata objective list |
| fs-id1167836299681 | 7 | Readiness question 1 and supplied answer |
| fs-idm404421072 | 6 | Readiness question 2 and supplied answer |
| fs-idm387231616 | 6 | Readiness question 3 and supplied answer |
| fs-id1167836538118 | 1 | Opening daily-data prose |
| fs-id1167829921677 | 2 | Roster prose, including term-00001 |
| fs-id1167836418492 | 1 | Symbolic student-name/student-ID pair |
| fs-id1167836547061 | 2 | Domain/range prose, including term-00002 |
| fs-id1167833059636 | 1 | Variable-matching prose |
| fs-id1167836378970 | 2 | Relation definition |
| fs-id1167836629801 | 8 | Try It 1 and supplied answer |
| fs-id1167833021555 | 8 | Try It 2 and supplied answer |
| fs-id1167836509402 | 3 | Mapping definition, including term-00003 |
| fs-id1167829683746 | 12 | Worked birthday mapping |
| fs-id1167836340432 | 7 | Try It 3, student-ID mapping |
| fs-id1167824754892 | 7 | Try It 4, birthday mapping |
| fs-id1167836532042 | 1 | Graph representation prose |
| fs-id1167833057329 | 11 | Worked graph |
| fs-id1167829750323 | 7 | Try It 5, graph |
| fs-id1167829738598 | 7 | Try It 6, graph; selected endpoint |

There are 101 selected source IDs, plus the uncounted section-context ID = 102 preserved original IDs. The XML has 107 unique IDs in all; five are new navigation/article/credit wrappers. Read-only verification checked every selected source ID under its corresponding translated wrapper, not merely somewhere in the document. None of the 21 data-source selectors overlaps units 001–007.

## Mathematics and source fidelity

The three readiness answers remain −11, 2a² − a − 3, and 3x + 4. The extra line 3(−2) − 5 = −6 − 5 = −11 is visibly original working. The second readiness item keeps symbolic a rather than choosing an invented numeric value.

The two set-based Try Its retain every ordered pair, variable, subpart and result. The mappings keep all names, codes, arrows and birthdays, subject only to the explicitly described source-reading differences below. Source-name labels remain Roman-script identifiers so they match the unchanged images; surrounding explanations and birthday month names are Marathi. The graph tasks remain visual questions, not coordinate-list replacements in problem text. Their accessible alt text supplies accurate point readings.

All eight relations were checked by independently projecting their ordered pairs onto the first and second coordinates. Sets are deduplicated without deleting distinct pairs sharing one coordinate. Numerical domain/range order in supplied answers is preserved, even where the source uses a nonascending order; an original note explains that set order is immaterial. In particular graph 3's source range stays {−6, 0, 5, −2, 2, −4}. The graph window is not substituted for the domain or range, and isolated dots are not joined. The point (−3, −6) on image 006's lower frame is included.

### Source-authority differences, not silent repairs

1. Image 001: canonical EN pixels, EN supplied answer and the Indonesian version all give Liz → August 2. The EN alternative description incorrectly says July 24. Marathi alt and answer follow the visible canonical arrow; a reader-visible original note records the disagreement.
2. Image 002: canonical EN pixels spell the first name Khan Nguyen. EN text/alt and ID text/redraw spell Khanh Nguyen. The unchanged EN image is authoritative for the visible exercise, so Marathi answer and alt use Khan Nguyen. The visible note retains Khanh Nguyen as the alternative source spelling; it makes no claim about a real person's correct name. All four codes and arrows are unchanged.
3. Image 002: broken EN supplied text Jose Hern and ez is rendered Jose Hernandez, matching both image and ID text; explicitly noted.
4. Image 003: broken EN text Arm and o is rendered Armando, matching canonical pixels and ID; explicitly noted. No birthdays change.

No upstream CNXML, source snapshot, image or archive pin was repaired or moved. The source answers are translations with these disclosed readings, not falsely described as verbatim transcriptions. All six required media are referenced; none is omitted or redrawn.

## Image inspection and root asset handoff

After checking disk space (10,976,448,512 bytes free before the small draft writes), used only the existing freezer's --review-images pathway to copy these individual archive members into ignored downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-008. No full extraction, new download or cache was made. Personally viewed all six EN originals and all six corresponding ID redraws. The shared independent reviewer also reported direct inspection of all 12 images; that is additional review, not a substitute for the drafter's viewing.

All below use image/jpeg. Root should freeze unchanged EN assets; ID copies are comparison witnesses only. EN total is 410,644 bytes; ID review copies total 1,707,796 bytes.

| Filename | Original media ID | EN bytes | EN SHA-256 |
|---|---|---:|---|
| CNX_IntAlg_Figure_03_05_001_img_new.jpg | fs-id1167833364760 | 99293 | b7187d1cd61e336d2ad7368cbe2710471f1d75f733aca9eef3b9674776c483c8 |
| CNX_IntAlg_Figure_03_05_002_img_new.jpg | fs-id1167836333597 | 84140 | ce00276b81f2e4ec1deea697515ddfb257580f23859d8017fb0ea0c3f4d2c3be |
| CNX_IntAlg_Figure_03_05_003_img_new.jpg | fs-id1167833385478 | 86090 | da8bcab15681b37fde889ec049a04824e64ccdd6eda9934646d9aadf70c1e566 |
| CNX_IntAlg_Figure_03_05_004_img_new.jpg | fs-id1167836673420 | 46737 | c65297a087d98e313dc944b8ab60c55d9748dbfd4a786168e92075d467d3b1d0 |
| CNX_IntAlg_Figure_03_05_005_img_new.jpg | fs-id1167836341066 | 47230 | dddc2892ca12cfb8e3001d6c90c81dd3508ad43b04f373d9263212d3bc42f64c |
| CNX_IntAlg_Figure_03_05_006_img_new.jpg | fs-id1167833049956 | 47154 | b743ed6e890e2f2b683f5b7bf242a6fc968b930ab4832706cceeab2bb1d180fc |

The ID hashes in the same filename order are ca72c85d63d128fdd47a8dce95b08506216c4b05316973c776023b2b9b751e56; c2647151b3deda6b779b2ed5448e54b86d5dee83dcda4fc956077b90dad18994; 867b4467090ab468315924723b4af0186aaf4cfb9c21baa9d039cda99e1e52cc; fd745c4458e3a33c31bce3f2578239c6dbd8ca2bec7ed380b73c1bb988a72ce9; 23947743de90d6dfb5db0c9e6a964c9cce98850f74f22d01e963ebd91c8f962b; 786b8b7cb912666ae8205bf0424b45ec8ba9517d30b76af3f0e7b605a525e476.

Direct EN pixel readings of 004–006:

- 004: (−3, 4), (−3, −1), (0, 3), (1, 5), (2, −2), (4, −2).
- 005: (−3, 3), (−2, 2), (−1, 0), (0, −1), (2, −2), (4, −4).
- 006: (−3, 5), (−3, 0), (−3, −6), (−1, −2), (1, 2), (4, −4).

All three displayed frames extend from −6 to 6 on each axis. ID redraw labels/tick styling differ, but the points agree. Marathi captions label Name/Birthday/Student ID# and x/y without changing source pixels.

## Actual Marathi canon consultation and effects

Read AGENTS.md and USER_INSTRUCTIONS_VERBATIM.md, the current canon consultation record and relevant pilot prose. A glossary-only review is not claimed. The selection and draft used the existing 001 relation/domain example, its function explanation and grouped negative substitution; the established 004 coordinate language was also read.

- Selection: actually read C14's function condition prose from [फलन](https://marathivishwakosh.org/21979/), C18's Cartesian-axis and coordinate-construction prose from [आलेख](https://vishwakosh.marathi.gov.in/24316/), and C19's opening definition/image-set paragraphs from [फलन](https://vishwakosh.marathi.gov.in/27548/). These readings distinguish a relation from the stronger function condition and actual paired values from a declared codomain or plotting frame. They guided the choice to retain finite relation questions without extending their numerical patterns to all real inputs.
- Drafting: reused those actually read passages while drafting the domain, range and point-reading explanations. Also read existing BB8 physical-page-85 OCR, first 18 lines, corresponding to C12 printed p75: value substitution, equation solution and explicit equal operations. The readiness item asks for an expression's value, not a solution for x. The negative value remains parenthesized in the visibly original working. No new PDF rendering/OCR or reading of garbled OCR formulas was claimed.
- Revision: freshly retrieved and read C18's relevant axis/projection prose and C19's opening range/codomain prose again. Direct webpage opens returned 502; readable search-reader retrievals succeeded. Fresh MV-F retrieval also supplied C14's uniqueness condition, C15's domain/codomain naming, the actual person/task example with a shared output, and C16's final constant-function prose. This late C15/C16 read is not retroactively described as a successful selection-stage fetch. No QuickLaTeX image formulas on that page were inspected or used.

Concrete revision effects: retained प्रांत and the established मूल्यसंच rather than silently switching to witnessed कक्षा; kept निर्देशांक consistently with the pilot while recording C18's actual सहनिर्देशक variant. Shared birthdays remain valid repeated outputs, not errors to be made artificially unique. The graph explanation separates first/second coordinates, actual dots and the axis frame. C18's population-data line-joining example does not authorize interpolation in these finite exercises. Final revision corrected agreement in the credits and the graph-grid sentence. No native-speaker/teacher review is claimed; unrelated C19 advanced assertions and C17 dependence prose are not used as authority for this checkpoint.

Original additions are visibly marked data-kind=original: scope/overlap notes, US social-security context and privacy reminder, one readiness working line, symbolic-a reminder, offline/external-link notice, finite-set and no-interpolation reminders, set-order explanation, image label keys and source-reading differences. They are not extra source blocks or questions.

## Preserved outgoing review links

The three source links point to m81422: twice fs-id1167836530265, once fs-id1167836652573. The actual pinned m81422 metadata identifies “Use the Language of Algebra” (UUID 772b200d-b3d4-4654-bc37-a1d3fb70efd7); the target examples exist in its tree. Read-only, in-memory retrieval of the [official section](https://openstax.org/books/intermediate-algebra-2e/pages/1-1-use-the-language-of-algebra) confirmed both exact HTML example IDs once each. The XML links use that URL plus the original fragment and preserve document/target in data-source-document and data-source-target-id. No target example or media is counted as translated here. The reader notes that these optional references need the internet; its own questions/solutions/images are intended to work offline after root's asset build.

## Read-only draft verification

Passed XML parsing/NFC, JSON parsing, 107 unique IDs, all 101 selected original IDs nested under the correct wrapper, the one additional context ID, 21 ordered selectors, absence of overlap with units 001–007, 11 original problems/solutions, 35 exact expected_math strings and 10 required terms. Independently checked the eight first/second-coordinate projections, numeric readiness results and source-answer order. Generic validate_markup passed using a temporary in-memory asset-name dictionary only: 27 valid internal links, 7 HTTPS links (including the 3 original review links), 6 images with preserved figure IDs. This is markup validation, not hash-config/freeze/build validation. No output files or caches were produced by these checks (Python used -B).

The independent reviewer reported 13 of its 14 bounded draft tests passing, the remaining expected failure being the not-yet-created freeze/asset records. Root should run the full tests after freezing, then build and inspect desktop/phone renderings. No quality claim here covers layout not yet rendered.

## Exact next uncovered teaching section for MR-BRIDGE-009

Both pinned EN and ID trees agree: next section fs-id1167836610583, “Determine if a Relation is a Function”; first new teaching paragraph fs-id1167826171759. The whole section has 14 direct non-title source blocks, 103 selected IDs plus its section wrapper = 104 original IDs, 3 worked examples, 6 Try Its, 1 definition and 4 prose blocks. Its 9 source exercises all have source solutions. None is selected by units 001–008.

The section ends at note fs-id1167833369174; the immediate following section is fs-id1167824731607, “Find the Value of a Function.” This is a coherent complete run below the 15 worked/exercise-block cap. It has 13 images: CNX_IntAlg_Figure_03_05_007_img_new.jpg, 008_img_new.jpg, 009_img_new.jpg (same filename prefix), then 010a_img.jpg through 010c_img.jpg, 011a_img.jpg through 011c_img.jpg, and 012a_img.jpg through 012d_img.jpg. These next-section images were inventoried only, not inspected in this 008 task; their pixels must be read before 009 drafting. The section has three source backlinks into 008: fs-id1167829683746 twice and fs-id1167833057329 once. This navigation is not a claim of whole-module completion.
