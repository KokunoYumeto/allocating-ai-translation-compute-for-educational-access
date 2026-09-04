# A10 evaluating expressions — complete-section text draft

Status: complete provisional translation of the selected section's CNXML linguistic surfaces in both Javanese registers. Media-label derivatives, source-bound narration, reader integration and human review remain pending. This is not a completed module or a completed A00/A10/AX-2 assignment.

## Full source boundary

Read both actual pinned versions of `m82453/fs-id1170654889475` in their entirety, direct children `[0:13]`, including the section title. Reading chunks were `[0:7]`, `[7:10]`, and `[10:13]`; the draft has no slice or omitted example.

Source title: “Menentukan Nilai Ekspresi” / “Evaluate an Expression”.

| Child | Source ID | Entire included material |
| --- | --- | --- |
| 0 | no ID | Section title |
| 1 | fs-id1170654968998 | Transition from simplification to evaluation and bold definition |
| 2 | fs-id1170654969001 | Definition note, including term-00018 and fs-id1170655161751 |
| 3 | fs-id1170655353204 | Replacement/substitution instruction |
| 4 | fs-id1170654889272 | Both parts of 7x−4 worked example, two tables and all ten media |
| 5 | fs-id1170654936461 | Both 8x−3 practice parts and answers |
| 6 | fs-id1170654968085 | Both 4y−4 practice parts and answers |
| 7 | fs-id1170655213474 | Both variable-base / variable-exponent worked parts, two tables and four media |
| 8 | fs-id1170655120535 | Both power practice parts at x=3 and answers |
| 9 | fs-id1170655353747 | Both power practice parts at x=6 and answers |
| 10 | fs-id1170655171250 | Entire polynomial evaluation, table and two media |
| 11 | fs-id1170655160606 | Complete practice at x=3 and answer |
| 12 | fs-id1170655197213 | Complete practice at x=2 and answer |

Previous adjacent section: `fs-id1170654953465`, order of operations. Next adjacent section, **excluded**: `fs-id1170655163482`, “Mengidentifikasi dan Menggabungkan Suku-suku Sejenis”, beginning with `fs-id1170655355506` (“Bentuk aljabar tersusun atas suku-suku…”). Final included answer: `fs-id1170655106384`, value 9.

Verified the two local full-module hashes against the existing m82453 source-lock witnesses. No reacquisition, repeated supply/license audit or source rewrite was performed.

| Witness | SHA-256 |
| --- | --- |
| Indonesian module, downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml | `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635` |
| English module, downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml | `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed` |
| languages/jv-Latn-ID/sources.lock.json | `27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb` |
| Shared translation/phrases.json | `adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8` |

## Exhaustive translation coverage

The new edits JSON records all 36 linguistic phrase keys, in first-occurrence source order, and both target strings for each. These cover 62 text/tail/attribute occurrences. Two keys, `dan` and `Penyelesaian`, are identical to existing shared rows; 34 are additional to that shared map. The source keys `x` and `y` are mathematical identifiers, explicitly unchanged rather than translated. There are 31 standalone identifier occurrences, including the source's mtext x.

The phrase rows are the per-phrase decision ledger. Repeated source text uses its explicit row; there is no hidden fallback, unsupported empty target or placeholder.

Counts independently confirmed in Indonesian and English:

- 13 direct children; 83 unique IDs, same order in both witnesses and retained in both target replays.
- 3 worked examples, 6 practice notes, 9 exercises, 9 solutions, 15 question parts.
- 38 MathML roots and 12 msup nodes. Eight superscripts have numeric exponents; four have variable exponents.
- One mtext node contains identifier x. No linguistic mtext, MathML table, fraction or mspace occurs. No spacing-only MathML root is claimed.
- 5 headerless two-column CNXML tables, with body-row counts 4, 4, 4, 4 and 5. All empty cells, two colspec elements in the last table, alignment/valign attributes and hierarchy are preserved.
- 16 media references, all with linguistic alt descriptions; 5 aria-label descriptions; no summary attributes, links or separate captions.
- Literal equation/comma/full-stop operators, coefficient adjacency, variable positions, superscript structure, parentheses and source part glyphs remain exact in written MathML. The em-space after the first “Gunakan definisi eksponen.” is retained by whitespace-preserving phrase replay.

All 38 Indonesian and English MathML trees agree exactly after removing only each root's external prose tail. Both Javanese targets retain those same mathematical trees, including the mtext identifier. This is stronger than merely matching flattened numeric strings.

## Actual canon use and register choices

At source reading, fully read the local C01 wilangan, C14 owah, C15 tetep, C21 ping and C34 rambang entries. While drafting the substitution/grouping descriptions, fully read C29 kurung and C30 tutup. Verified each selected raw/readable file against its lock hashes. The lock contains 34 records at this snapshot, SHA-256 `b803663cdb093658bdcf9815a53e2ba26f227e38296d3b2a840f55e8213590ac`.

| Entry | Readable SHA-256 | Draft decision |
| --- | --- | --- |
| C01 wilangan | `3031d446d034c11509a9f1bc6d77509c2b5ecd7dc8021e5f94bfab9aff72ca6d` | Use wilangan for the given number; retain source distinction between number and variable. |
| C14 owah | `fc1b0eee6d03456c5bef4922d102989da0ccb3bc9ba32cefe76bc47bb5c5af3f` | Generic change is not sufficient to explain replacement; do not imply changing the original formula arbitrarily. |
| C15 tetep | `a9c5cf58c85dae034252212aad8bd0bb974b829be1e426324d2ae28c5845183d` | A given assigned value must remain fixed within each evaluation part; no formula-changing paraphrase. |
| C21 ping | `e1442bf2e7d8f24ed3dc6d09b8fe78e0fd4fc692b65c482fdcce84cdc06f49bf` | Retain ping / Pingake / Pingna for products and multiplication instructions. |
| C29 kurung | `215e0412cd2db1a7bba144f18fcfa2fd244daed6812d32b26e55f2d4ce960239` | Use the attested written-parenthesis sense in accessible descriptions. |
| C30 tutup | `693acc5199d95abb00b21495f1ef58d5ed917d036dea4e0cbf3d9349267ac6c5` | Use bukak/tutup components without claiming standardized complete mathematical prosody. |
| C34 rambang | `a45727af8975350e044d15deff91892693b03a47f545e6f14d75182b9cf13bdc` | Retain pangkat as the established provisional school loan; rambang is an attested alternative, not silently substituted. |

A topic-driven lookup fully read the official [KBJI ganti entry](https://kbji.kemendikdasmen.go.id/kata/ganti) on 2026-08-31, including all 378 returned page lines. It supports ordinary replacement wording with ganti/ngganti and also lists sulih among alternatives. This page was read online, **not acquired into the local shelf**, and has no claimed local content hash or C35 identifier. It is not counted among the 34 local records. No PDF was selected; OCR was not applicable.

- Evaluation becomes `Nemtokake Nilai Ekspresi` / `Ngetung Nilai Wujud Aljabar`. The definition explicitly says that a given number replaces the variable before simplification. This is not an instruction to solve an equation for an unknown value.
- Source “substitusikan … sebagai pengganti variabel” becomes plain replacement wording, `gantia variabel … nganggo wilangan kasebut` / `ganti variabele nganggo wilangan kuwi`. Ganti's ordinary sense is attested; the full mathematical instructional construction remains provisional.
- `nilai`, `variabel`, `ekspresi`, `suku`, `eksponen`, `pangkat`, `kuadrat`, `definisi`, and `sans-serif` remain explicit technical/school loans. Suku occurs in inherited accessible descriptions; no complete native algebraic-term standard is claimed ahead of the next lesson.
- Academic `wilangan pokok` and conversational `wilangan dhasar` follow the previous exponent draft. C34's mathematical rambang is recorded as an alternative, not an authority to replace the lesson's established pangkat wording.
- Source instructions remain distinct: determining a value, replacing a variable, using the exponent definition, multiplying, subtracting and simplifying are not conflated. `Kalikan.` and `Kurangkan.` match the preceding order-of-operations draft.
- Every quoted mathematical expression keeps its operands and glyphs. For the assignment image label, `Gunakna x = 4.` retains the literal variable/equality/value while making a usable Javanese instruction. It is bound to the actual substitution context, not a generic equation rewrite.
- Translated image descriptions name intended Javanese labels but do not certify that those labels have already been put into image pixels. All five linguistic-image derivatives remain separate work.

## Source discrepancies and declared target-only corrections

The exact Indonesian keys are retained. None of these decisions rewrites the Indonesian pivot, source IDs, media reference, or MathML.

1. The English prompts for the power examples/practices have awkward “Evaluate x=3, when …” wording. The Indonesian source clearly places the given x value first, then asks for each expression's value. The Javanese draft follows that actual Indonesian structure. It does not ask learners to evaluate the equality statement itself.
2. The source question's 3^x uses an mi exponent, but the solution table's initial 3^x uses **mtext x**. Both source versions do this. Preserve the tag difference exactly; treating mtext x as prose or substituting it before the solution cue would change the exercise.
3. Media 012b's English alt describes 3^x, whereas Indonesian describes 3^4, with base 3 and exponent 4. It belongs to the row after x is replaced by 4; the subsequent four-factor product and answer 81 agree with the Indonesian description. Translate the actual corrected Indonesian alt. Verify the actual pixels separately before declaring image agreement.
4. Media 013b's English alt describes the original 2x²+3x+8; Indonesian describes the substituted 2(4)^2+3(4)+8. This matches its source row and following 2(16)+3(4)+8 step. Retain the corrected Indonesian description and exact literal formula. Pixel review is still pending.
5. Table `fs-id1167829717426` has a source aria row-alignment defect in both languages. The inherited description pairs replacement with x², the exponent-definition instruction with 4², and simplification with 4·4, then leaves 16 below. The actual rows are different; the Javanese descriptions explicitly follow them:

| Actual row | Left source content | Right source content | Javanese description decision |
| --- | --- | --- | --- |
| 1 | Empty | x² MathML | State the initial symbolic expression and empty left cell |
| 2 | Image instruction “Ganti x dengan 4.” | Image 4² | Pair replacement with 4² |
| 3 | “Gunakan definisi eksponen.” plus em-space | 4·4 MathML | Pair exponent definition with expanded product |
| 4 | “Sederhanakan.” | 16 MathML | Pair simplification with result 16 |

All source numeric mentions are retained in order. The target-only prose correction invents neither a calculation nor a new numeric fact. The root coordinator explicitly approved source-cell-verified accessible-description corrections.

6. Table `fs-id1167836504155` source aria omits its first symbolic 3^x row. Target descriptions add a nonnumeric acknowledgment of the initial variable-exponent expression before the existing replacement, four-factor product and result rows. The first MathML remains unchanged and no additional numeric mention is added.
7. The last table's opening “2x kuadrat” could be misread as (2x)². The target description explicitly says `2 ping x kuadrat`, agreeing with the actual MathML where x alone is the base of the square. No visible multiplication operator is inserted into MathML.
8. Source “Substitusikan x = 4.” becomes “Gunakna x = 4.” in both target alts; the matching table description says “Gunakna x padha karo 4.” The surrounding definition supplies the replacement meaning. This preserves the assignment relation instead of deleting the equals sign from the quoted image label.
9. English 010d alt speculates about a score or date. Indonesian removes that speculation and identifies the expression 7−4. Translate the Indonesian correction, not the unsupported interpretation. English “To the write” in two table descriptions is already corrected to “Di kanan”; target uses tengen.
10. Source alts describe subtle red highlighting, position, gray/orange colors and font characteristics. These have been translated but not independently confirmed against pixels. Fourteen image tags declare image/png despite .jpg filenames; the two 013 images declare image/jpeg. Preserve these exact source attributes and verify actual signatures at asset preparation.
11. Long table descriptions are not a substitute for source-tree-bound table narration. The corrected descriptions and actual cells must be reconciled once during accessible rendering, not read twice or used to leak answers into questions.

## All exercises and answers checked

The expressions below are human-readable witnesses transcribed from the actual trees, not flattened source strings or a production parser. All 15 results were independently recomputed and agree with the source solution surfaces.

| Exercise ID | Complete question | Source answer(s) |
| --- | --- | --- |
| fs-id1170654889274 | 7x−4 at x=5; x=1 | 31; 3 |
| fs-id1170654920156 | 8x−3 at x=2; x=1 | 13; 5 |
| fs-id1170654928390 | 4y−4 at y=3; y=5 | 8; 16 |
| fs-id1170655213476 | At x=4: x²; 3^x | 16; 81 |
| fs-id1170655120539 | At x=3: x²; 4^x | 9; 64 |
| fs-id1170655353751 | At x=6: x³; 2^x | 216; 64 |
| fs-id1170655171252 | 2x²+3x+8 at x=4 | 52 |
| fs-id1170655160609 | 3x²+4x+1 at x=3 | 40 |
| fs-id1170655197217 | 6x²−4x−7 at x=2 | 9 |

Worked chains, with each source step retained:

- 7(5)−4 → 35−4 → 31 and 7(1)−4 → 7−4 → 3.
- x² → 4² → 4·4 → 16 and 3^x → 3^4 → 3·3·3·3 → 81.
- 2x²+3x+8 → 2(4)^2+3(4)+8 → 2(16)+3(4)+8 → 32+12+8 → 52.

These arrows describe row succession in this QA note. They are not inserted as source operators or read as equality chains without explicit narration decisions.

## Media and pending AX-2 work

Exact source-order media references:

- `../../media/CNX_ElemAlg_Figure_01_02_009a_img_new.jpg` — `fs-id1167836295066`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_009b_img_new.jpg` — `fs-id1167829597558`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_009c_img_new.jpg` — `fs-id1167833076771`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_009d_img_new.jpg` — `fs-id1167836554298`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_009e_img_new.jpg` — `fs-id1167836507263`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_010a_img_new.jpg` — `fs-id1167829597755`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_010b_img_new.jpg` — `fs-id1167836492302`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_010c_img_new.jpg` — `fs-id1167836296392`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_010d_img_new.jpg` — `fs-id1167836294733`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_010e_img_new.jpg` — `fs-id1167833014906`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_011a_img_new.jpg` — `fs-id1167826170152`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_011b_img_new.jpg` — `fs-id1167836526102`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_012a_img_new.jpg` — `fs-id1167829692365`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_012b_img_new.jpg` — `fs-id1167836692989`, source MIME `image/png`.
- `../../media/CNX_ElemAlg_Figure_01_02_013a_img_new.jpg` — `fs-id1169149357522`, source MIME `image/jpeg`.
- `../../media/CNX_ElemAlg_Figure_01_02_013b_img_new.jpg` — `fs-id1169149089480`, source MIME `image/jpeg`.

The 009a, 010a, 011a, 012a and 013a images contain linguistic instructions according to both source descriptions. Their target label wording is explicit in the edits; the source numerals, variables, relations, coloring and geometry must be retained when preparing actual derivatives. Do not treat all sixteen images as numeric-only merely because eleven are formula/result images. No bytes were extracted, copied, edited, downloaded or rendered here.

Required integration work:

- Register 38 exact source MathML fixtures. Distinguish x² from 3^x, preserve both mi/mtext exponent identities, coefficient-variable multiplication, coefficient-square scope, equality assignments, terminal punctuation and parentheses. Do not flatten powers or evaluate a question before its source answer.
- Bind the complete five tables, including all headerless rows, empty cells and last-table colspecs, to exact source and target trees. Validate the two declared row-description corrections against actual cells.
- Keep x and y visible; narration should use explicit letter names at the correct source position. No generic mtext-as-prose permission follows from this unit.
- Read question conditions and both part cues before their corresponding answer cues. Worked result rows belong after the solution cue. No naming-style digit adaptation or answer leakage is introduced.
- Narrate products and power scope explicitly, with a clear end-of-power cue before the next operation. Future finite numeral readings need their own canon consultation; this text draft does not claim pronunciation approval.
- Prepare and inspect the sixteen media, including five linguistic derivatives, verify hashes/geometry/formulas, then build and verify offline reader, transcript and SSML outputs.
- Native-language educator/register, visual, screen-reader, pronunciation, synthesis and listening review remain pending. No such pass is claimed.

## Read-only validation witness — 2026-08-31

Replayed the entire selection with the existing `draft_units.select`, `build.translated` and `draft_units.validate` functions in memory. No production descriptor, shared script or generated product was modified. Added explicit in-memory checks for every nonlinguistic attribute, unchanged identifiers and full MathML-tree equality, which also rejects mutation of mtext x.

- Exact key coverage: 36 linguistic keys / 62 occurrences; 31 unchanged standalone identifier occurrences.
- Same ordered 83 IDs and complete source hierarchy in both target tracks.
- All numeric sequences in source text, tails, alts and aria preserved. Quoted symbolic formulas such as `7x-4`, `3^4` and `2(4)^2 + 3(4) + 8` retain their operands/operators; the declared prose product clarification does not rewrite MathML.
- Both overlaps with shared phrases are identical. Every target row is explicit.
- Second in-memory replay is byte-identical for each track.
- All 15 arithmetic witnesses pass.
- Eighteen deliberate mutations reject: number, operator, variable, mtext-variable, superscript-base-exponent-order, superscript-tag, math-attribute, source-id, source-order, image-reference, image-mime, alt-numeric, aria-numeric, table-columns, colspec, answer, missing-phrase, duplicate-phrase.
- This is an inline read-only verification witness, not eighteen installed regression tests or a completed workflow build.

ElementTree UTF-8 hashes with the build module's registered namespaces, without XML declaration:

| Item | SHA-256 |
| --- | --- |
| Edits JSON | `5b6f3dee1956637649814b1b5eb111aaef708b0a9e54fd62100dd1e7b048d874` |
| Selected source tree, tail removed | `23f064b8811d839241ce7029cc73fea85b7f8d88ba2ba6ea0a22135249c8907f` |
| Academic in-memory target | `fa0533b53bd6754d06e3d480230f62d64d9a30855826ccde7a4148d3edf455ff` |
| Conversational in-memory target | `3732eddc0de9dd75d24ba780050058664ecb27ced9d12ee4996bb45084146cdd` |

Only the new edits JSON and this QA/DRAFT witness were created. Full A00/A10/AX-2 work remains active; next exact source section is `fs-id1170655163482`.

## AX-2 complete evaluation-section rules — 2026-08-31

This appendix supersedes only the earlier **pending narration/media inspection** state. The original 20,295-byte draft note is preserved verbatim as the historical prefix (SHA-256 `b5ac98768a7c7d59212c9f4eb1a5cf6046460ca219fcaa30058c0792bbac69a5`). Its translation/source snapshot remains valid. No translation edit, source asset, shared builder, production descriptor or generated reader/audio file was changed in this stage.

New file: `audio/a10-evaluate-expressions.rules.json`, 298,974 bytes, SHA-256 `9b629c2df98b99cca29740fdbcace2c7e9b301bc45f9e88f407a71be44557ab5`. It is a complete-section **provisional rule input**, not a completed integrated unit or completed module. Full A00/all A10/full AX-2 work remains ongoing.

### Exact scope and source/target binding

Personally reopened and read the whole pinned Indonesian and English `m82453/fs-id1170654889475` section, all original children [0:13], then the full current 36-row phrase ledger. The source order, all examples/practices/solutions, table cells, labels, attributes, media references and mathematics were inspected. The next section `fs-id1170655163482`, beginning `fs-id1170655355506`, is excluded; final included answer is `fs-id1170655106384`.

| Surface | Exact coverage |
| --- | --- |
| Source hierarchy | 13 direct children / 83 IDs in source order |
| MathML | 38 exact fixtures / 114 three-track readings |
| Powers | 12 msup: 8 numeric exponents, 4 variable exponents |
| Literal exponent exception | One exact mtext x in M16, not generic linguistic mtext |
| Implied products | 13 MathML adjacency sites; 6 numeric-image adjacency sites |
| Parentheses | 2 MathML pairs, 4 pairs across numeric images |
| Tables | 5 headerless two-column tables / 21 rows / 63 three-track row readings |
| Prose | 18 whole-paragraph fixtures: 3 definitions/instructions, 9 questions, 6 answers |
| Figures | 16 exact media fixtures / 48 three-track readings |
| Exercises | 3 worked examples + 6 practices = 9 exercises / 15 question parts / 9 source solutions |
| Descriptions | All 16 alts and 5 aria-labels exactly bound; no summary attribute occurs |
| Links/spacing math | No links or spacing-only MathML in this selection |

Every MathML fixture uses the actual selected top-level child ID plus a one-based descendant MathML ordinal; `nearest_source_id` is diagnostic, not dispatch authority. Source and translated tree hashes retain namespace, all attributes, child order, identifiers, operators and numeral tokens. A formula string such as flattened `x2` is not a power witness.

| Math fixtures | Top-level source anchor | Included mathematical content |
| --- | --- | --- |
| M01–M03 | `fs-id1170654889272` | 7x−4, then x=5 and x=1 |
| M04–M06 | `fs-id1170654936461` | 8x−3, then x=2 and x=1 |
| M07–M09 | `fs-id1170654968085` | 4y−4, then y=3 and y=5 |
| M10–M18 | `fs-id1170655213474` | x=4, x², 3^x, and every MathML table row |
| M19–M23 | `fs-id1170655120535` | x=3, x², 4^x, then source answers 9/64 |
| M24–M28 | `fs-id1170655353747` | x=6, x³, 2^x, then source answers 216/64 |
| M29–M34 | `fs-id1170655171250` | Polynomial question, x=4, and all four MathML table rows |
| M35–M36 | `fs-id1170655160606` | 3x²+4x+1, then x=3 |
| M37–M38 | `fs-id1170655197213` | 6x²−4x−7, then x=2 |

The 24 question formulas and 4 supplied MathML-answer formulas require their owning whole-prose fixture (28 protected occurrences per track). Ten table formulas remain bound within complete table readouts. The two numeric-only answers 40 and 9 and two plain paired answer paragraphs are also explicit prose fixtures, not unregistered numeral fallback.

### Canon actually consulted during this narration stage

The narration draft used a 43-record shelf snapshot, lock SHA-256 `4f0b09c844385dfb1dee095ef934bdfeb972ca6995cb8870974c2771ffb1d76f`. Before the final snapshot, another worker acquired C44 sisa and C45 turah; actual current lock has 45 records, SHA-256 `0950c12a0791b30655aef3b933928fd3ea1a8e4eb8f7157f43c6a29f53b1ea64`. Neither new entry is counted as personally consulted in this stage. The actual consulted set is fifteen full readable entries, each hash-checked against the lock:

| Entry | Actual readable SHA-256 |
| --- | --- |
| C01 wilangan | `3031d446d034c11509a9f1bc6d77509c2b5ecd7dc8021e5f94bfab9aff72ca6d` |
| C07 lima | `3ed3c9e246682760330b56c4ab7c8aa3517e00844f5761fcca7c2bc0a499fd20` |
| C09 kiwa | `196359730d6dd9735788cd060b3e1b4731c9e6d593fc81ee36e4309cd11f52e3` |
| C10 tengen | `4697a749a57b7443e01f5118ba603c5ea7101ad55df78dfbfbb3c66c3f9e8986` |
| C14 owah | `fc1b0eee6d03456c5bef4922d102989da0ccb3bc9ba32cefe76bc47bb5c5af3f` |
| C15 tetep | `a9c5cf58c85dae034252212aad8bd0bb974b829be1e426324d2ae28c5845183d` |
| C17 rolas | `36939ac858e21fb25f407b1aaf935cd76d2eb953f6ef3c76e29b895f2bfc506c` |
| C19 atus | `ad13869146a75a42a356ca054a32241e0332295d3febe3f6d03ac4c3d2019503` |
| C21 ping | `e1442bf2e7d8f24ed3dc6d09b8fe78e0fd4fc692b65c482fdcce84cdc06f49bf` |
| C26 wolu | `0a6fadd19095297247cb2c9f36adcaa6230a218832213ee6d83865ede4d888db` |
| C28 sewidak | `ffa62101bfd616e0b46eeea00f066672da1ce18b18fd784a367ec8509bf4ab7d` |
| C29 kurung | `215e0412cd2db1a7bba144f18fcfa2fd244daed6812d32b26e55f2d4ce960239` |
| C30 tutup | `693acc5199d95abb00b21495f1ef58d5ed917d036dea4e0cbf3d9349267ac6c5` |
| C34 rambang | `a45727af8975350e044d15deff91892693b03a47f545e6f14d75182b9cf13bdc` |
| C43 ganti | `8a5ec8aa8bec9482d7fd7cc40a808a7542134fa449114617dbc0157d09b8078a` |

Source stage reread C01/C14/C15/C21/C34. Draft/figure stages reopened full C21/C34, C09/C10, C29/C30 and C07/C19/C28/C17/C26, comparing the actual source/target wording rather than treating downloads as consultations. Parent acquired C43 `ganti.txt` during this task; I personally read its entire local extract before drafting replacement instructions. After the draft and numerical checks, I again fully opened C43/C34/C17/C26 for revision; final language QA reopened C01/C14/C15. These are actual readings, not delegated summaries.

C43 confirms ordinary ganti/ngganti replacement (and other copying/representing senses); the specific mathematical replacement sentence and imperative forms remain provisional source-defined compositions. The replacement homonym is not conflated with C39 borrowing. C21 supports multiplication components; C34 directly attests rambang for mathematical power, but the agreed provisional school loan pangkat/eksponen remains for lesson continuity. The flattened dictionary display 43 is not a formula. C29/C30 support kurung and opening/closing components; complete delimiter and power-end prosody still requires review.

C07 attests `sèket` (50), C28 `sewidak` (60), C19 `rong atus` (200), C17 `rolas` (12) and C26 `wolu` (8). Full readings `sèket loro` (52), `sewidak papat` (64), `rong atus nembelas` (216) and other composed numerals are explicit provisional compositions, not falsely presented as separately attested full forms. No native-register or pronunciation approval follows from dictionary consultation.

### Effective media: corrected Indonesian release takes precedence

The initial image pass viewed all sixteen **canonical English** originals and raised a possible mismatch for 012b and 013b. That was not yet evidence about the effective Indonesian media. Parent independently viewed the local Indonesian overrides; I then personally viewed both and matched their exact bytes, dimensions and hashes against their pinned Indonesian ZIP members and release MANIFEST. The initial correction suspicion is withdrawn. No correction was made on its basis.

The verified Indonesian MANIFEST is byte-identical locally and in `a10-source.zip`, SHA-256 `5499e09e64347de101f410848a951d7ab25f44b57cf61cdcf0cbd8b1dc71ce9f`. The canonical media authority CSV is SHA-256 `3b8478b77c8860363b7000cbffa68782320e73458289bdcda957acf1b971210f`. All sixteen English originals match selected authority CSV rows and Git blob witnesses at commit `38cae454e644abf9f0a623e876994553881597c9`; the two overrides additionally match their release manifest entries and local bytes. No complete archive was rehashed or extracted.

Resolution is exact: check `translated/media/<filename>` in the pinned Indonesian ZIP/MANIFEST/local override tree first. Only for names absent from all three use canonical media. Fourteen evaluation images have no Indonesian override and retain canonical bytes. All sixteen effective images were personally viewed, including a fresh review of the fourteen retained originals after the override check.

| Image suffix (CNX_ElemAlg_Figure_01_02_) | Actual effective content | Effective SHA-256 | Provenance / remaining visual work |
| --- | --- | --- | --- |
| 009a_img_new.jpg | `when x=5` | `bc0bbc92f6ac9d90f67befad9afeb2bbb35551d806d7b5fbb75b36318f9372ed` | Canonical retained; two JV label derivatives pending |
| 009b_img_new.jpg | `7x−4` | `61090e849550dba305dc9bbbbf5f207f72c64c27d086deed3f62c860c4dfb30b` | Canonical retained; retain exact bytes |
| 009c_img_new.jpg | `7(5)−4` | `0e3cb6bb7b4477094cf2710e43ce0be9067ff70d0e0f53ffbb9536ff98dc1533` | Canonical retained; retain exact bytes |
| 009d_img_new.jpg | `35−4` | `639a392dc9fdde71c18efb3e13227a37fc1f9ae9a42a787cfea4f1425a7bfe66` | Canonical retained; retain exact bytes |
| 009e_img_new.jpg | `31` | `6429b2ad75a19c5eca35a7387a09f86b2a0ccb2d002ede07fb4475813ecc47ef` | Canonical retained; retain exact bytes |
| 010a_img_new.jpg | `when x=1` | `ef9db0b7c3a26233fece2ea550e22099c859bf120ac40d0a39de9235d4d3c702` | Canonical retained; two JV label derivatives pending |
| 010b_img_new.jpg | `7x−4` | `4928dce68d7c942508ebc4d4296f7884d39f79183f4578cddf91e82090a03b54` | Canonical retained; retain exact bytes |
| 010c_img_new.jpg | `7(1)−4` | `e8a6c1a0e379a636a891cbcd7ef6732ede369bdfc8b2e2a1f04ee45bad5bc450` | Canonical retained; retain exact bytes |
| 010d_img_new.jpg | `7−4` | `59b456e0f85b48393078a560bb0b032bd8673d10bbf889d5901e9afe232bd0e5` | Canonical retained; retain exact bytes |
| 010e_img_new.jpg | `3` | `ca057f9ca8e9e5db2910d519d9b77ec5e616af3d3272dc2b144d7d5405bb1ee4` | Canonical retained; retain exact bytes |
| 011a_img_new.jpg | `Replace x with 4.` | `e2992a29d90b1af21bacbcf29212ad39ac20d2201dca363ff333facec4de07cd` | Canonical retained; two JV label derivatives pending |
| 011b_img_new.jpg | `4^2` | `e67f1296c44ef24d988e271bde4bd54fce11d5e65825a5c7a23fbda4fab0d69a` | Canonical retained; retain exact bytes |
| 012a_img_new.jpg | `Replace x with 4.` | `6469bc7e90f4f776d891f46eeafcbeb97a1930c55f509900afc9db2cc7905c1d` | Canonical retained; two JV label derivatives pending |
| 012b_img_new.jpg | `3^4` | `fc469cf6cd1dfac09c4010af7d7606f1309033663fc0ddbf891813f1b5208b67` | ID override; retain exact bytes |
| 013a_img_new.jpg | `Substitute x=4.` | `235464ed3e2d0be2f4f4c94ca4f59d47dd2411ae30774ef36261fcab0fe69a6f` | Canonical retained; two JV label derivatives pending |
| 013b_img_new.jpg | `2(4)^2+3(4)+8` | `31e05fe68d3807d96bca8c3c747a82bc0ccf1b08d2dbfdb70fc1dea36a025a1e` | ID override; retain exact bytes |

The differences that must not be erased:

- 012b effective ID: 439 bytes, 14×12, visible `3⁴`, SHA `fc469cf6cd1dfac09c4010af7d7606f1309033663fc0ddbf891813f1b5208b67`. Canonical English: 48,381 bytes, visible `3ˣ`, SHA `8ec3ccd4ccb9745db4f7a2a14740c03abd00f61330ab6c0f3a6292a26a864b76`.
- 013b effective ID: 1,079 bytes, 117×14, visible `2(4)²+3(4)+8`, SHA `31e05fe68d3807d96bca8c3c747a82bc0ccf1b08d2dbfdb70fc1dea36a025a1e`. Canonical English: 44,330 bytes, visible `2x²+3x+8`, SHA `efa3a502dd3a5cceadc846d48d1aa6fe5fe3f48b9671183a7ab43143df6d19fb`.

Existing release evidence `evidence/m82453/final_review-FINAL_REVIEW.md` independently describes these two derivative overrides and gives the same hashes; that evidence supports, but does not replace, the actual byte/visual checks.

The five retained English labels are 009a, 010a, 011a, 012a and 013a. Their exact JV visible-label instructions are respectively `nalika x = 5`, `nalika x = 1`, academic `Gantia x nganggo 4.` / conversational `Ganti x nganggo 4.` twice, and `Gunakna x = 4.` in both registers. All five highlighted replacement numerals stay red; surrounding literal letters, equals signs and punctuation keep their source meaning and order. No derivative has been materialized or rendered in this task. ID speech gives the existing Indonesian label translation; retained English pixels must be visibly disclosed/transcribed unless a separately verified ID label derivative is provided.

All effective bytes are JPEG. Fourteen source image nodes still declare PNG, and two declare JPEG. Preserve source CNXML declarations as provenance; delivered reader MIME must reflect actual bytes. This is not permission to transcode source witnesses.

As a narrow cross-check after the override discovery, all 23 previously handed-off order-of-operations media names were checked against the same Indonesian archive/MANIFEST/local override tree: none has an Indonesian override. No prior order file was edited.

### Mathematical speech, row order, answer separation

Literal x/y become `aksara eks/aksara ye` in JV and `huruf eks/huruf ye` in ID. The exact mtext x exponent is read as that same literal letter without changing its source tag. Explicit `ping/kali` makes coefficient multiplication audible, while `pungkasan pangkat/akhir pangkat` closes the exponent before a following operation. In 2x² the square belongs to x, not to the coefficient-variable product.

All five headerless tables are read left-to-right, physical row by physical row; empty cells are described as empty, never zero. No equals sign is inserted between stages. Source T03/T04 aria omissions/shifts are not used to move the actual rows:

| Table fixture | Exact source table | Right-column row sequence |
| --- | --- | --- |
| T01 | `fs-id1167836329359` | 7x−4; 7(5)−4; 35−4; 31 |
| T02 | `fs-id1167833047529` | 7x−4; 7(1)−4; 7−4; 3 |
| T03 | `fs-id1167829717426` | x²; 4²; 4·4; 16 |
| T04 | `fs-id1167836504155` | 3^x; 3^4; 3·3·3·3; 81 |
| T05 | `fs-id1169148881010` | 2x²+3x+8; 2(4)²+3(4)+8; 2(16)+3(4)+8; 32+12+8; 52 |

The exact last-table colspecs and align/valign attributes are bound. The em-space after the T03 row3 left instruction remains in the source/target trees. No spacing-only MathML or zero-valued placeholder is invented.

T03 target aria already corrects the source's one-row-early instructions; T04 target aria already acknowledges its omitted initial symbolic row without adding numeric mentions. T05 target aria already clarifies the coefficient/product scope. These prior declared target-only wording choices were independently checked against source cells and effective images; this rules stage changes no phrase keys or values, introduces no numeric exception, and preserves the exact whole target trees.

Every question is read unevaluated, including its given assignments and part cues. Worked table results occur after the actual source solution title. The six untitled practice solutions receive exactly one outer `Wangsulan./Jawaban.` cue. The four standalone worked-table part labels remain before the proper table and are not invented column headings. Whole-table and whole-prose overrides suppress duplicate child/alt/aria narration.

Independent source arithmetic checks (verification metadata, never question audio):

| Source exercise | Given values / tasks | Supplied answers, independently reproduced |
| --- | --- | --- |
| `fs-id1170654889274` | 7x−4, x=5 / x=1 | 31 / 3 |
| `fs-id1170654920156` | 8x−3, x=2 / x=1 | 13 / 5 |
| `fs-id1170654928390` | 4y−4, y=3 / y=5 | 8 / 16 |
| `fs-id1170655213476` | x² / 3^x, x=4 | 16 / 81 |
| `fs-id1170655120539` | x² / 4^x, x=3 | 9 / 64 |
| `fs-id1170655353751` | x³ / 2^x, x=6 | 216 / 64 |
| `fs-id1170655171252` | 2x²+3x+8, x=4 | 52 |
| `fs-id1170655160609` | 3x²+4x+1, x=3 | 40 |
| `fs-id1170655197217` | 6x²−4x−7, x=2 | 9 |

All fifteen supplied answers and every one of the 21 worked-row expressions independently reproduce the expected source value. The restricted test-only arithmetic interpreter accepts only the registered integer/variable/add/subtract/product/power expressions. It is not production narration or generic parser authority.

### Read-only verification and explicit integration limits

Inline Python checks used the current source selector/translator/exact tree matcher, and a temporary in-memory descriptor only to exercise the existing mtext dispatch. No shared descriptor was saved. Independent test readers reconstructed math, paragraph, chart and physical-row speech from actual source/translated trees and the personally witnessed image forms. All three tracks passed: 114 math readings, 54 prose readings, 48 chart readings, 15 whole-table readings, and 63 row readings. Current edits/shared hashes, exact ID and mathematical identity, all numeric text/attribute sequences, both identical shared phrase overlaps and deterministic repeated in-memory target serialization were checked.

All 44 deliberately altered source/target/fixture cases were rejected. These are inline mutation checks, **not 44 installed regression tests**:

| Case | Observed rejecting gate |
| --- | --- |
| `source-number` | `source_section` |
| `source-operator` | `source_section` |
| `source-variable` | `source_section` |
| `source-mtext-identifier` | `source_section` |
| `source-mtext-tag` | `source_section` |
| `source-power-base-order` | `source_section` |
| `source-power-tag` | `source_section` |
| `source-math-attribute` | `source_section` |
| `source-id` | `source_section` |
| `source-child-order` | `source_section` |
| `source-image-reference` | `source_section` |
| `source-image-mime` | `source_section` |
| `source-table-row-order` | `source_section` |
| `source-table-columns` | `source_section` |
| `source-table-colspec` | `source_section` |
| `source-table-entry-attributes` | `source_section` |
| `source-alt-number` | `source_section` |
| `source-aria-number` | `source_section` |
| `source-answer` | `source_section` |
| `target-number` | `target_section` |
| `target-variable` | `target_section` |
| `target-mtext-identifier` | `target_section` |
| `target-language-word` | `target_section` |
| `target-alt-word` | `target_section` |
| `fixture-math-tree` | `unsupported_source_bound_narration: ('fs-id1170654889272', 1)` |
| `fixture-math-ordinal` | `unsupported_source_bound_narration: ('fs-id1170654889272', 1)` |
| `fixture-math-missing` | `AssertionError` |
| `fixture-math-extra` | `AssertionError` |
| `fixture-reading-answer-leak` | `('prose_reading', 'A10-EVAL-P04')` |
| `fixture-power-reading` | `('math_reading', 'A10-EVAL-M11')` |
| `fixture-product-reading` | `('math_reading', 'A10-EVAL-M01')` |
| `fixture-prose-context` | `AssertionError` |
| `fixture-table-tree` | `nonmath_source_fixture` |
| `fixture-prose-tree` | `nonmath_source_fixture` |
| `fixture-target-hash` | `AssertionError` |
| `fixture-row-omission` | `AssertionError` |
| `fixture-row-duplication` | `whole_table_reading` |
| `fixture-chart-reading` | `('chart_reading', 'A10-EVAL-D01')` |
| `fixture-image-hash` | `effective_image_hash` |
| `fixture-english-012b-regression` | `effective_image_hash` |
| `fixture-english-013b-regression` | `effective_image_hash` |
| `fixture-header-invention` | `AssertionError` |
| `fixture-answer-cue` | `('prose_reading', 'A10-EVAL-P04')` |
| `unknown-fraction-tree` | `source_section` |

Whole-source and whole-target hash rejections happen before narrower parsing. The source mutation rows therefore do not claim independent production coverage of every downstream parser branch. Fixture-only mathematical/tree mutations, altered speech, missing/duplicated rows, wrong image hashes, both English-image regressions and answer leakage were also separately rejected against otherwise unchanged source. No mutated fixture or source was saved.

Production integration remains required:

- Register this complete section and install its finite table/prose/chart hooks and source/target validation. Add live-node, track and rule-snapshot checks to direct narration entry points; copied IDs and changed nodes must not authorize fixed speech. The current saved production builder does not yet implement these evaluation-specific hooks.
- Materialize/inspect the five two-register linguistic-label derivatives; retain the other eleven effective images exactly, including both ID overrides. Bind an actual asset manifest, truthful MIME and all delivered output hashes.
- Preserve all source identity/numeric facts; no broad attribute-correction exception is needed by this unchanged evaluation draft.
- Build deterministic three-track CNXML/readers/transcripts/SSML and install/rerun persistent regression and mutation tests. Current independent in-memory checks are inputs to that integration, not a completed reader/audio build.
- Native educator/register, browser/page visual, screen-reader, pronunciation, synthesis and listening review remain pending. No provider calls, audio synthesis, asset editing, download, extraction, bulk copy or Git mutation occurred in this stage.

### Final input fingerprints

These hashes use raw bytes except the explicitly named canonical tree hashes. The earlier prefix's ordinary ElementTree-serialization hashes use a different algorithm and are preserved as historical evidence.

| Input | SHA-256 |
| --- | --- |
| Indonesian complete m82453 CNXML | `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635` |
| English complete m82453 CNXML | `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed` |
| Unchanged evaluation edits | `5b6f3dee1956637649814b1b5eb111aaef708b0a9e54fd62100dd1e7b048d874` |
| Shared phrase edits | `adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8` |
| Active source lock | `27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb` |
| Current 45-entry canon lock | `0950c12a0791b30655aef3b933928fd3ea1a8e4eb8f7157f43c6a29f53b1ea64` |
| Selected Indonesian canonical tree | `0d76d191791c6df1efc290e27434429fa289ca829c536ee2007c3573c984f779` |
| Academic target canonical tree | `e85314cf23e35c44def3df1e807d54c83c8e4ed5615e436957aec85b5cbf0c48` |
| Conversational target canonical tree | `4249059f26841227ff36325361701ced9a492adeeeadab82206bd1f927740de1` |
| Evaluation rules | `9b629c2df98b99cca29740fdbcace2c7e9b301bc45f9e88f407a71be44557ab5` |

The active source lock is not sanitized or rewritten here. Coordinator-owned public export must refresh bindings/receipts separately if source paths are sanitized. The new single-review-branch/goal/hourly-heartbeat instruction is acknowledged; this worker performed no independent branch, push, merge or automation action.

Only the new evaluation rules file and this appended witness are owned by this stage. The full assignment/workflow remains unfinished; a bounded rule handoff is not a whole-module completion claim.

## Dedicated three-track production integration — 2026-09-02

This append supersedes only the preceding statement that this evaluation section still lacked production hooks. It does not rewrite or erase the AX-2/source history above. The complete `m82453/fs-id1170654889475` section now has a dedicated fail-closed producer, reader, finite transcripts, and provider-free SSML. It remains outside the shared global registry until coordinator-owned inventory integration.

### Revalidated authority and scope

Before production, the worker reread the governing root/language instructions, goal, next-unit handoff, full decision log, full consultation log, complete saved QA witness, all 36 translation rows, and the complete pinned Indonesian and English section. The production validator reopens the current 50-record canon lock and all 15 actual readable extracts (`C01`, `C07`, `C09`, `C10`, `C14`, `C15`, `C17`, `C19`, `C21`, `C26`, `C28`, `C29`, `C30`, `C34`, `C43`) for each track binding. Current canon-lock SHA-256: `396bc9db6ce9f8ab06e0366cf8f525f68e403afa567a7235bea1ea611c006c76`.

The locked section remains exactly 13 direct children including its title, 83 ordered unique IDs, 38 MathML expressions, 12 `msup`, one exact `mtext` `x`, five headerless two-column tables with 21 physical rows (`4,4,4,4,5`), 16 media nodes, nine exercises, nine solutions, 15 question parts and 24 part markers. It has zero source links. The previous section is `fs-id1170654953465`; excluded next section is `fs-id1170655163482`, its first paragraph is `fs-id1170655355506`, and the final included source ID is `fs-id1170655106384`.

### Asset result and correction provenance

The producer materialized 16 exact effective JPEGs and ten Javanese SVG label derivatives for the five English-label images. All ten derivatives were rendered with ImageMagick 7.1.2-26's built-in SVG renderer and visually inspected for readable, unclipped label/order/value output. The five corresponding source JPEGs and enlarged copies of both small Indonesian overrides were also visually inspected. This is bounded static asset inspection, not browser/page, human-language, native-educator, screen-reader, pronunciation, synthesis, or listening approval.

The independently retracted correction history is preserved. `012b` uses the actual pinned Indonesian release bytes, 439 bytes at 14×12, SHA-256 `fc469cf6cd1dfac09c4010af7d7606f1309033663fc0ddbf891813f1b5208b67`, visibly `3^4`. Its distinct canonical English authority SHA-256 is `8ec3ccd4ccb9745db4f7a2a14740c03abd00f61330ab6c0f3a6292a26a864b76` and is not delivered. `013b` uses the actual pinned Indonesian release bytes, 1,079 bytes at 117×14, SHA-256 `31e05fe68d3807d96bca8c3c747a82bc0ccf1b08d2dbfdb70fc1dea36a025a1e`, visibly `2(4)^2+3(4)+8`. Its distinct canonical English authority SHA-256 is `efa3a502dd3a5cceadc846d48d1aa6fe5fe3f48b9671183a7ab43143df6d19fb` and is not delivered. The retracted canonical-based replacement was not applied.

The asset manifest is 36,916 bytes, SHA-256 `92d7567c03373e025ea30c2fa3f30370046ae660b6bc6bbb9048ce1b17932e9a`; it records the hash and truthful delivered MIME for all 26 asset files. Fourteen canonical files remain effective and two Indonesian overrides take precedence. The Indonesian reader preserves five pinned English pixel labels and explicitly discloses that fact while supplying Indonesian alt text/transcript; no hidden image-language substitution is claimed.

### Reader, narration, and answer boundaries

Each of three track bindings requires the unchanged complete source tree, unchanged complete target tree, the exact rule bytes, the actual live XML node, the correct track, current canon/readable files, and the matching finite fixture. A copied node, source/target mutation, altered rule object, context-only direct MathML call, unknown element, unknown token/operator or unknown source reference fails closed. There is no generic MathML/prose/table/image fallback, broad exception, expression evaluator in question audio, answer invention, provider selection, voice fallback, or locale fallback.

The reader contains 249 track-scoped source IDs (83×3), 251 unique HTML IDs including the page ID and one real incoming alias, 114 MathML renderings (38×3), 48 embedded images (16×3), 15 tables (5×3), 39 track articles and zero links. The real incoming cross-unit destination is `a10-evaluate-expressions.html#fs-id1170655171250`. All 13 source blocks are represented in each track. Narration binds 38 math, 18 whole-prose, five whole-table and 16 chart fixtures per track; 28 formulas per track remain whole-prose-only and ten table formulas are standalone-authorized. Six untitled solutions receive exactly one track-specific answer cue each, three worked solutions retain their actual translated solution title, and question speech precedes every answer boundary. All 15 supplied answers and 21 worked rows are independently recomputed only in the finite verifier and never added to question speech.

No synthesized audio exists. The six audio-directory artifacts are three plain-text transcripts and three SSML documents, each with 13 deterministic source marks, an explicit matching locale, no `<voice>` element, and no provider/fallback configuration.

### Installed checks and deterministic results

The exact successful commands were:

```text
python prepare_evaluation_assets.py --check
python draft_evaluation.py --check
python build_evaluation.py --check
python -m unittest -v test_evaluation_assets.py test_evaluation_workflow.py
```

The three producers passed byte-for-byte deterministic replay. The two test modules ran 11 tests in 42.427 seconds: all passed. Tests cover exact saved products, truthful MIME and ten labels, both Indonesian override/canonical separations, all three finite readouts, 28 context-only formulas, live-node/copy/tree/rule mutations, absence of a generic fallback, exact reader counts/anchor, provider-free SSML, exclusions and false review claims.

Production created 40 deterministic artifacts: 27 asset products, five translation/provenance/draft-receipt products and eight reader/audio/build-receipt products. Six dedicated scripts/tests were added. Only this QA file was append-modified. Shared `build.py`, `coverage.py`, coverage JSON, locale goals/status/README, complete-m81243 files, Git index and refs were not touched. The two receipts deliberately retain `.in-progress.json` basenames so existing global coverage cannot mis-inventory them.

| Principal production file | Bytes | SHA-256 |
| --- | ---: | --- |
| `translation/a10-evaluate-expressions.id-academic.cnxml` | 16,998 | `b06cb45b8814055625c6dc7ceff8873961de046181b9344a11b6fab0bc9e4a3d` |
| `translation/a10-evaluate-expressions.jv-academic.cnxml` | 17,205 | `e1f43bfd302a0138f13b1aeeff74b2e0fece67f314b3e6149f1d7b9ca448b1a1` |
| `translation/a10-evaluate-expressions.jv-conversation.cnxml` | 16,868 | `ad45e0049e19789a323241df5170603635826830658e342d5d96e5e0af5dd792` |
| `provenance/a10-evaluate-expressions.en.cnxml` | 17,111 | `f2533028303b87bf13f4026b95877e3f51216ce27e621002367c18a22637d66c` |
| `translation/a10-evaluate-expressions.assets.json` | 36,916 | `92d7567c03373e025ea30c2fa3f30370046ae660b6bc6bbb9048ce1b17932e9a` |
| `qa/a10-evaluate-expressions.production-draft.in-progress.json` | 2,675 | `1dad71c78fc89d3e785e895704cb3a65437746b25d74dc802a27b6cc33293ad8` |
| `review/units/a10-evaluate-expressions.html` | 2,042,753 | `5476d74a20b92fb75a881750bb9050c22e7712df9fed3833a36470effb41128d` |
| `review/audio/a10-evaluate-expressions.jv-academic.md` | 5,209 | `4a464800e34689035307bae75a110b3e3aea5feedee237c01dfcb6f69620baf7` |
| `review/audio/a10-evaluate-expressions.jv-academic.ssml` | 6,115 | `9c35f2b9a08e93764aa44ce3b1f8183e3245f23f5350fdbdb652bd34dd8e07cd` |
| `review/audio/a10-evaluate-expressions.jv-conversation.md` | 5,186 | `8f9d6ee5e646e453807d81dc032d9c894d0ee6a764fc0840382ba6af947592a1` |
| `review/audio/a10-evaluate-expressions.jv-conversation.ssml` | 6,088 | `a3dd4208575239b72b33bb9ece367c714c040c16148e422d60501eeda5866874` |
| `review/audio/a10-evaluate-expressions.id-academic.md` | 5,080 | `5c4ac68745b7ef2c44a1cab73d4ce61586b205365ddbbe8ef8c6867387798d8d` |
| `review/audio/a10-evaluate-expressions.id-academic.ssml` | 5,981 | `685f8bc7d8467b5f0b260ce8545a9b205c179c4e6bdf78a9f8a094ec8ea3f4cb` |
| `qa/a10-evaluate-expressions.production-build.in-progress.json` | 5,018 | `61099b21f9dac98593757aa4db0db94122acde21a2f429d3d518069682c5fb25` |

The build receipt contains exact output hashes and all individual asset hashes remain in the asset manifest. This is deterministic offline production integration, not human/native/assistive-technology acceptance and not completion of the whole A10 module.

Next cursor: independent review of these dedicated evaluation products, followed by coordinator-owned global inventory/coverage integration. The next content section remains `fs-id1170655163482`; it is excluded here.
