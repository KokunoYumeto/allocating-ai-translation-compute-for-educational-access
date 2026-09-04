# A10-001 language and source-fidelity notes

Status: self-reviewed Shahmukhi Punjabi draft, not native-speaker certification or rendered-reader approval. This is the first small A10 checkpoint. The full A10, A20, A30, B10 and B40 translation workflow remains active.

## Exact scope

Source: A10 / `col31130`, **Elementary Algebra 2e**, chapter **Foundations**, module `m82452`, **Introduction to Whole Numbers**, pinned canonical commit `38cae454e644abf9f0a623e876994553881597c9`.

Include the opening be-prepared note `fs-id1170655158095` and paragraph `fs-id1170655154091`, then section `fs-id1170655083568`, **Use Place Value with Whole Numbers**, through the complete second Try It `fs-id1170654885628`. Stop before `fs-id1170655113270`, which starts writing numbers in words. The section prefix contains its first 13 direct children, title included; it is not the complete section.

The bounded selection contains **30 translated source text blocks, 43 source IDs, 2 spacing-only MathML trees, 2 source figure elements, 3 unchanged source images, 2 links, one worked example and two complete Try Its**. There are **zero CNXML tables** in this selection; two images depict place-value tables. The separately labeled original bridge has its own tables and explanatory numbers, which must not inflate source counts.

Earlier collection items `m82630` (**Preface**) and `m82451` (**Introduction**, the chapter opening) remain explicitly pending. A10-001 therefore does not establish contiguous translated coverage from the beginning of the collection.

## Source reading and frozen witness

Read the exact English and Indonesian prelude and selected section prefix. English authority remains canonical; the Indonesian file is a comparison, not a replacement. The earlier A10 start plan records the verified 82-module collection order and first-module distinctions.

The complete-upstream LF canonical file is `downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82452/index.cnxml`, SHA-256 `0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310`. It matches A10's bundled English authority copy. The convenient sparse Windows checkout differs only by CRLF for this module; its raw hash is not the frozen canonical hash. The Indonesian comparison is `downloads/extracted/A10/translated/modules/m82452/index.cnxml`, SHA-256 `940ad448d8b2788984f386405131866fe32abb95f0f9c2a901ca1f4e3619a6fb`.

The bounded witness was written with `apply_patch`. Its three selected root elements recursively match the canonical selection in node type, expanded element/attribute names, values, text and whitespace. Redundant `xmlns` declarations are serialization differences only. No source sentence, alt text, MathML node or image byte was corrected in that witness.

Handoff hashes:

| Artifact, relative to the language directory | SHA-256 |
| --- | --- |
| `source-excerpts/a10-unit-001.cnxml` | `ad6b6d61efe78ff33aa5a3f55bc1f87853b9143a0ca37acb361743cf016767bb` |
| `source-excerpts/manifest-a10-001.json` | `894bdf876f6d8f08b2ada678b1fb8122468cf039303e6a1c85ff0cff8a1e0ff9` |
| `translations/a10-unit-001.json` | `5783f4abcd5d2b88816ed88987c40d28e3d2526a6ffe239058c859b40e35a387` |

## Actual canon consultation

The actual local `scripts/read_canon.py` was executed at all three production stages. Each run displayed the selected passage windows for reading and generated a unique receipt. Local HTML snapshots already existed; no download was required. The earlier source-analysis run used the script's supported `next-unit` stage and is documented separately in `plans/A10-start.json`.

| Stage | Actual receipt in `canon/receipts/` | IDs actually read | SHA-256 |
| --- | --- | --- | --- |
| Draft | `A10-001-draft-20260830T214009982181Z.json` | C01, C02, C03, C04, C07, C09, C11 | `ef8f1ea67b5b1b1a29148843b38b5eff5c483a46323694581478482eeb5e2207` |
| Revision | `A10-001-revision-20260830T215002815906Z.json` | C01, C04, C07, C09, C10, C11 | `a906d091a70a48aa3037aba6e5c4418773a27c0a6f7d3fc66b52f272981506b9` |
| QA | `A10-001-qa-20260830T220024362213Z.json` | C01, C03, C04, C07, C09, C10, C11 | `01a93ba0fd6e8b3d10fd97fa242b8f471234d7b86b0db5a07d9184fb9311fbf7` |

The receipts inherit generic `application` strings from the existing canon index; several mention older PNB examples. Those strings are not evidence that those old examples occur in A10. The actual decisions for this unit are:

- **C01**, `بیان کیتی جا سکدی اے`: reference for Punjabi ability grammar in `مل سکدی اے` and `ویکھ سکدے آں`. The target uses Punjabi agreement rather than Urdu `ہے`/`ہیں` constructions.
- **C02**, `پڑھنا چاہیدا اے`: reader-directed register reference while choosing direct instructions such as `لبھو` and `رکھو`. It does not attest those exact mathematical imperatives or establish a technical term.
- **C03**, `ترتیب وار`: ordinary ordering vocabulary informed the explanation of continuation and the phrase `ترتیب نال` in image descriptions. No claim of a fixed place-value term follows from it.
- **C04**, `صفحے گھٹ ودھ وی ہوندے رہے`: checked plural number/quantity descriptions, `نیں`, and `ہوندے جاندے نیں` in the number-line caption. During revision, wrote `چلدی`/`چلدے` as complete inflected words.
- **C07**, `دُوجے صفحے اُتے`: checked ordinal/location constructions in the first/second/third-line description and `جگہ اُتے`. The actual passage also contains `چار کالماں وچ`; two accidental mixed-script endings in the first draft were corrected to `کالماں`. The subsequent codepoint gate passes with no Gurmukhi characters.
- **C09**, `چیتے رہوے کہ`: consulted as a reminder-register option. No reminder was forced into the source prose and no exact C09 phrase was adopted; this is a recorded non-adoption, not a fabricated influence.
- **C10**, `وضاحت منگدی اے`: used as a qualification-register reference while keeping the two source discrepancies and their explanations separate. It is not evidence that either mathematical correction is true; the source digits, captions and inspected images supply that evidence.
- **C11**, `کیوں جے`: retained this Punjabi reason connective in the explanation that digit value depends on position.

The canon is still twelve short loci in three essays by one author, not twelve mathematical sources. Reading it does not establish the standardizedness of new terminology, naturalness for all Punjabi readers, or native-speaker approval. No source was transliterated from Gurmukhi.

## Provisional terminology and grammar decisions

No shared terminology file was edited. The original bridge supplies English/Urdu equivalents, explicitly labeled as this translation's provisional choices.

| English | Punjabi choice | Decision and limit |
| --- | --- | --- |
| counting numbers | گنتی دے عدد | Descriptive wording; source sequence begins at 1. |
| natural numbers | قدرتی عدد | Reuses the existing ledger choice. No universal zero convention is asserted. |
| whole numbers | پورے عدد | Defined by the source sequence including 0. Explicitly distinguished from all integers in the original bridge. |
| digit | ہندسہ | Familiar school-register loan in Punjabi syntax; not treated as a synonym for a whole multi-digit number. |
| number line | عدداں دی لکیر | Descriptive Punjabi phrase; image direction remains LTR. |
| place value | جگہ دی قدر | Provisional descriptive phrase, consistent with the existing preference for `قدر` rather than monetary `قیمت`. The source exercise names positions; the bridge distinguishes the position from the digit's contribution. |
| period | پیریڈ | Provisional loan immediately defined in the source translation as a group of three places. Not time or sentence punctuation here. |
| ellipsis | حذف دا نشان | Provisional descriptive label with the source's explicit continuing-pattern meaning. English `ellipsis` appears in the labeled key. |
| ones / tens / hundreds | اکائیاں / دہائیاں / سینکڑے | School-register labels with Punjabi agreement and locative constructions; review by a Punjabi mathematics educator remains needed. |
| million / billion / trillion groups | ملیناں / بلیناں / ٹریلیناں | Retain the source's scale and three-digit grouping. The original bridge spells out the corresponding numerical sizes. Do not silently switch to lakh/crore grouping. |

English `counting number` and `whole number` have a separate bold plural `s` in CNXML. Punjabi phrases carry their own plural/oblique endings; no English suffix is mechanically copied. All five original term IDs remain on target spans. The two `no-emphasis` terms remain unbolded. Source book/activity titles are translated or accompanied by an LTR English name; English is not substituted for the surrounding Punjabi explanation.

During revision, the alt descriptions' counted `hundred-thousand`/`ten-million` units were expressed as `گروہ` rather than `حصے` to avoid suggesting fractional pieces. The original clarification now says zero is `دس ہزار والی جگہ اُتے` rather than an awkward literal “holds the place.”

## Mathematical fidelity and source discrepancies

The source's counting numbers start `1, 2, 3, …`; whole numbers start `0, 1, 2, 3, …`. Comma-grouped numbers retain their exact ASCII digits and order. None was converted to Indonesian punctuation or a South Asian digit-grouping convention.

Manually checked each source answer against its corresponding digit and source number:

- `63,407,218`: (a) 7 thousands; (b) 0 ten-thousands; (c) 1 tens; (d) 6 ten-millions; (e) 3 millions.
- `27,493,615`: (a) 2 ten-millions; (b) 1 tens; (c) 4 hundred-thousands; (d) 7 millions; (e) 5 ones.
- `519,711,641,328`: (a) 9 billions; (b) 4 ten-thousands; (c) 2 tens; (d) 6 hundred-thousands; (e) 7 hundred-millions.

The two source MathML trees contain only `mrow/mspace width="1.5em"`. Their exact retention is required, but it is not validation of the numbers or place-value answers, which mostly occur outside MathML. No MathML punctuation relocation is required for this unit.

The original three JPEGs were inspected at original detail in the source-analysis stage and were neither edited nor copied by this draft task. The number-line arrows mean smaller left, larger right; the charts show `5,278,194` and `63,407,218`. Dimensions, SHA-256s and planned reader asset paths are in the manifest. Reader copies and retained-notice integration remain parent work.

**A10-ALT-001:** The first place-value chart's English alt ends with “two hundred seventy-nine thousand,” inconsistent with its own numeric `5,278,194`, listed digits, caption and image. The Indonesian comparison says seventy-eight. The source-bound Punjabi alt faithfully retains `دو سو اُناسی ہزار`; a clearly labeled original bridge states the correct `دو سو اَٹھہتر ہزار` and explains the evidence. The original witness and image remain unchanged. The potentially confusing source-bound alt requires attention in later assistive-technology review; its correction must be discoverable and must not silently replace the source claim.

**A10-ALT-002:** The worked-example image's alt claims a top “Place Value” row that the actual image lacks. Indonesian repeats the overdescription. The target source-alt preserves the claim; the original bridge identifies the absent row. The nested image remains unnumbered source media, not an invented figure.

The Manipulative Mathematics activity is only named in the source. The draft retains that name and explains in the original bridge that the full activity is not supplied in this selection.

## Pre-render checks actually run

- Parsed JSON successfully; the 30 keys derived from actual source paragraph/title/caption/item/media/direct-text-note elements exactly equal `source_blocks` in source order.
- Recursive canonical-versus-excerpt node/text/whitespace comparison passes for all three selected root elements. The canonical full-module hash remains unchanged.
- All 30 source text blocks have the same ordered ASCII numeral tokens as their translated counterparts, excluding markup/placeholders. This is a token check, not proof of every translated number word.
- All 30 source circled part tokens are mapped in the same order to isolated `(a)`–`(e)` labels across questions and answers.
- Two math placeholders, two link placeholders, and one nested-media child placeholder match the source roles. Five source newline elements correspond to five target `<br>` elements.
- All 27 non-alt target fragments parse as well-formed fragments after converting HTML `<br>` to XML `<br/>` in memory. The original bridge fragment also parses. This is not a browser DOM test and does not test the eventual mixed-content container.
- All five inline term IDs occur exactly once. Numeric text in source-bound non-alt fragments is under an LTR ancestor. Plain-text alt strings cannot contain HTML isolation markup; their screen-reader handling remains untested.
- No Gurmukhi codepoints or banned directional-control characters remain in the translation. Legitimate Shahmukhi characters are retained; this check does not certify Punjabi idiomaticity.

The manifest's renderer contract explicitly covers the direct-text activity note, the nested media paragraph, its preceding newline, the non-A30 example ID, explicit Solution title, and local figure labels `A10-001.1`/`A10-001.2`. These labels are local, not claimed canonical book numbering. The current shared renderer was not edited here.

## Remaining review and limitations

Parent work: build the A10 reader, materialize the three declared reader asset copies, bind retained attribution/component notices, extend source-bound automated QA and inspect actual RTL desktop/mobile rendering. Check that the media block does not create invalid nested paragraph markup; that activity text, captions, terms and answers all remain visible; and that new source metadata is A10 rather than A30.

Native Punjabi, mathematical-educator and assistive-technology review remain pending. No full-module, whole-collection or five-work completion claim is made. No additional source acquisition, bulk extraction, supply/license re-audit, shared code/CSS/terminology/attribution edit, deletion or commit was performed by this bounded draft task.
