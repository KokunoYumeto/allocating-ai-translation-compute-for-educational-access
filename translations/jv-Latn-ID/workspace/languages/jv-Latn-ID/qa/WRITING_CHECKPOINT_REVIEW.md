# Writing integration checkpoint review — 2026-08-31

Bounded independent review of the complete A00 m81243 / fs-id1339359 writing subsection and its current production draft. **No remaining source/numeric/readout defect was found in the saved writing outputs within this review.** One additional helper-level fail-closed hole was reproduced, reported and corrected during the review. This is not native, browser, screen-reader or listening approval, nor completion of A00/A10/AX-2.

Only this review file was written. No shared implementation, source rule, receipt, asset or generated output was edited or rebuilt by this reviewer. Read-only products/tests ran in memory; no source acquisition or preparation main routine ran.

## Finding reproduced and corrected

**Detached coefficient context could be lost through a plain dictionary copy — corrected.** The initial implementation at scripts/build_units.py:203 accepted dict(bound) as though it retained BoundMath.prose_only. In all three tracks, direct narration of the actual budget M03 and weight M06 then returned only “pitung puluh pitu”/“tujuh puluh tujuh” or “rong atus papat”/“dua ratus empat”, losing the mandatory magnitude/unit paragraph. The same calls with BoundMath or an empty mapping already rejected.

This did **not** affect the saved transcripts: the normal blocks path retained BoundMath and the complete P03/P06 prose overrides. It was a concrete helper rejection-boundary hole, not an observed wrong generated answer.

Root now requires BoundMath plus a registered expression identity for writing MathML before consulting prose_only (scripts/build_units.py:203). The regression at scripts/test_write_whole_workflow.py:135 now includes dict(bound). Independently repeated all six formula/track cases with each of BoundMath, an empty mapping and dict(bound): all 18 detached calls reject. Complete parent-paragraph narration still succeeds. The saved writing outputs and all nine prior unit packages remained unchanged.

The earlier inline part-b composition correction at scripts/build_units.py:190 is also present in the actual three transcripts: fs-id2880619 says one “bagean be”/“bagian be”, followed by its comma and zero-placeholder explanation. It does not add another part label, colon or question. The visible circled source span remains unchanged.

## Source and current output coverage

The actual complete original ID and EN subsection and all three current CNXML files were read, not inferred from a receipt. Pinned module hashes are:

- ID commit 3de9207f56f8b5c57c017abf973fb04e00d740f1, SHA-256 7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251.
- EN commit 38cae454e644abf9f0a623e876994553881597c9, SHA-256 396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b.

This is the entire nine-child section: title plus fs-id2607182, fs-id2398163, fs-id2376697, fs-id1542693, fs-id2437124, fs-id3202693, fs-id1805534 and fs-id1397780. It has 57 unique IDs, six MathML expressions, three media, no tables, two worked examples, four practices and six actual solutions. The last descendant is fs-id1395137; following rounding section fs-id2472737 is excluded.

All three CNXML variants equal exact source/phrase replay. All six ID/EN MathML trees and all 18 target MathML trees agree exactly, including currency mtext and period placement. No source IDs, numbers, grouping zeros, units, math attributes or hierarchy were silently changed. English pounds → overt Javanese pound is the previously declared unit decision; visible Indonesian pon remains source-exact.

All three complete transcripts were read. Their actual SSML was parsed and compared paragraph-for-paragraph, including the three locale labels and all 27 source marks. Independent saved-HTML parsing checked:

- 24 register/block articles, with all source IDs present in every track.
- 18 displayed namespace-aware MathML trees matching actual CNXML.
- All 78 displayed CNXML paragraph texts matching their corresponding target/source text.
- Nine embedded SVG byte payloads matching their exact manifest/file hashes, with exact target/source alts.
- Three genuine ordered how-to lists, each with three steps; the source-labeled a/b lists suppress duplicate native markers.

The two worked solution titles remain source-provided Panyelesaian / Cara Ngrampungake / Penyelesaian, without an added answer cue. Each of the four untitled practice solutions gets exactly one Wangsulan./Jawaban. cue. The displayed how-to’s initial “three blanks per period” and the later first-period exception both remain; they were not silently reconciled.

## Numeric, quantity and chart findings

The seven printed results are preserved as literal digits and explicit comma boundaries, not a substitution of their cardinal names:

| Context | Printed result | Preserved detail |
| --- | --- | --- |
| Worked a | 53,401,742 | 401 middle group |
| Worked b | 9,246,073,189 | leading zero in 073 |
| Practice | 53,809,051 | leading zero in 051 |
| Practice | 2,022,714,466 | leading zero in 022 |
| Budget | $77,000,000,000. | all nine zero digits, three commas, dollar unit |
| Distance | 34,000,000 mil | million magnitude and source mile |
| Weight | 204,000,000 pound | 204, not 240; source English pound |

An independent finite cardinal audit also reconstructed all 21 expected-cardinal witnesses (seven values × three tracks) to their exact integers without using the production number helper. The existing regression independently decodes all 21 literal result readings. Word-form questions stay words; literal digit results occur only in the source solution/answer regions. No full digit-form answer is leaked into a writing prompt.

Budget P03 binds $77 and its external billion into one complete quantity. Weight P06 likewise retains 204 plus million and pound. Distance retains 34 plus million miles without conversion. The seven-result/quantity checks distinguish coefficient, multiplier and unit; a rounded or converted value is never substituted.

“Dolar Amerika Serikat” for the state-budget example is the explicit coordinator-approved context clarification recorded before this integration. It is not literally a country name in the quoted budget sentence, and this review does not elevate that choice into an independent source-country attestation. The monetary value/currency symbol is unchanged. Similarly, spoken Indonesian pound is a disclosed source-English clarification over visible pon, not an assertion that Indonesian pon has an independently established conversion or pronunciation here.

The three word-to-digit chart mappings are 53/401/742, 9/246/073/189 and 77/000/000/000. Arrow direction remains words → digits, unlike the preceding naming lesson. In the budget chart the final three word blocks are blank but their digit groups contain zeros; narration explicitly distinguishes them.

The actual EN alt for media fs-id2903601 incorrectly says the 73-thousand block points to 742. Actual EN/ID MathML, Indonesian alt, source SVG and canonical JPEG show 073. The existing declared ID correction is retained; no pinned source is edited or wrong English alt value copied into the target.

## Asset and canon inspection

Read the complete source/target SVG text and the safe text-only asset implementation. Tests verify all nine SVGs preserve the inherited ID geometry and printed groups, and reject missing labels/numeric changes. The three Javanese register pairs are byte-identical for these concise diagram labels; surrounding prose remains register-separated.

Additionally opened all three already-local canonical JPEGs and all three existing derivative PNGs. Canonical JPEG hashes match their exact asset witnesses. PNG hashes match the earlier static-render record. Word blocks/arrows and 073/000 groups agree in meaning; no standalone text clipping/overlap was observed in those previews. The source JPEG and inherited ID redraw are separate designs, not claimed pixel-identical.

No new render was run. Existing derivative previews were generated earlier with ImageMagick 7.1.2-26 Q16-HDRI, RSVG delegate, density 96, white background and alpha removal, at 920×195 / 1120×195 / 900×195. This review of existing standalone previews does not prove integrated three-column legibility or browser/screen-reader behavior.

| Target register pair | Current SVG SHA-256 | Existing inspected PNG SHA-256 |
| --- | --- | --- |
| 016_img | e9e7ac52f72f2a8477150ee4ae3a8c65c301635b462a5d42e7c0df13474a1b95 | c1b41005b04b6ce3b119012bd5afe41bbb6e237ad405e5708da694a543ccefdd |
| 017_img | c15d2747d1f1a5ade046cb4a9280313e3d55d3e58c204da8e9f54c03085ecbd5 | c9f9179622107af7557d6ff16a6907939631cc9316a41f98b673a4b88f77aea0 |
| 018_img | 037c5dca1c756a3f0cea89965d4084583b306722a1eb9d85cfa094f4976a9297 | 3964447e43413e442778607fdad6f35c4f56b044820c2c1621bcef32c81e7774 |

During this QA stage reopened/read actual full readable C07 lima, C18 likur, C19 atus, C24 ewu, C25 yuta, C26 wolu, C27 sanga and C28 sewidak; also reread the complete relevant C20 enggon/panggonan headword sense. Current sèket/rolikur/atus/éwu/éwuan/yuta/wolu/sanga/sewidak usage agrees with those number senses. Atus dry/finished, yuta bewildered and éwuh difficult senses were not confused with numbers. Full compounds and period labels yutanan/milyaran, technical nilai panggonan/periode/satuan and pound/literal-digit prosody remain disclosed provisional choices. Dictionary headwords do not certify the whole compound or either register’s native naturalness.

## Tests, shared regression and portability boundary

Ran python -B -m unittest discover -s languages/jv-Latn-ID/scripts -p 'test_*.py' against actual files. The initial pre-fix run passed 140 tests in 62.666 seconds despite the independently found dictionary-copy hole. The final post-fix run passed **140 tests in 35.715 seconds**, none skipped. This includes eight writing-workflow, three writing-asset and four pure source-portability tests. No acquisition/build CLI was run.

The suite exercises source and target number/currency/namespace/attribute/anchor/order changes, zero loss, required full-prose contexts, quantity scales/units, missing chart labels, arrow direction, absent/duplicate fixed speech and answer placement. Independent DOM/SSML/canonical-source checks above complement rather than merely quote its results.

Verified the exact nine-file package digests for all nine earlier units against accepted FIFTH_CHECKPOINT_REVIEW.md: all 81 CNXML/transcript/SSML files unchanged. All eight earlier reader hashes also remain unchanged. Current writing addition therefore does not silently change previously reviewed output content.

Read prepare_sources.full_archive_origin (scripts/prepare_sources.py:35) and the four pure metadata tests only. Fresh download metadata does not inherit an old PC’s shared-origin claim; reused equal-byte/equal-path evidence is recorded as historical, without assuming current storage topology; ambiguous prior matches fail. No archive download, source replacement, cleanup, general license/supply audit or prepare_sources main was run. sources.lock.json remains byte-equal to HEAD at SHA-256 27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb.

## Final actual hash snapshot

Paths below are relative to languages/jv-Latn-ID. These are hashes of actual current bytes after the corrected guard and final suite, not copied unverified receipt claims. The current build receipt’s seven output hashes, rules/asset hashes and draft-receipt hash agree with the saved files.

~~~text
audio/a00-write-whole.rules.json d71c331d3d460726d5e625f97e8f47011c5ee75b5de532376af8343f6e7a8862
translation/a00-write-whole.edits.json 278ca54fc22c725d55484ad6ab1e5e6fb5268bfd3362758efa3dedaacb2c68ad
translation/a00-write-whole.assets.json 46a9f8144985444fd135148bac7733596fb8353f380de1f4e0abb15a0343bb29
qa/a00-write-whole.build-receipt.json 2e030ed73df40df4255fe156f6dc0a00e0dda68fd805dd60fc144fb964b4bdf8
qa/a00-write-whole.draft-receipt.json 0b28cc5e2fc78365bdcd3d202a435842195c37f9c051d2bca8d38899e84cf43a
review/units/a00-write-whole.html 86d15f3633196cc993648682e5bc1e94dda05023895be02d1ffc7a38659bef19
scripts/build_units.py 9bc314250a187e8cf820eeeb99896b9ad0be5e627569bea81b907322ac258c81
scripts/writing_checks.py 4d512a7e3ba273192bb53f32717b4bb6f0d13c9af8f2e0eb8af10bb49f76a6ca
scripts/test_write_whole_workflow.py d9874e17b1434c3410334efb2030b329a857d87e0b1719ba878368e82a5c7045
scripts/test_write_whole_assets.py 030cc041bab2d118cd3b5340aa7d6d6b55503e858561bd714f1435995a185b5b
scripts/test_source_portability.py cebd39ad9229dbd9ed9f311f1706954417c2ed006a627d5db71e807dd77e1e77
scripts/prepare_sources.py 678d5b95b47e58e55fbff52922d525e1cb5e129101212b0b0160412ca0d0dbf8
scripts/prepare_write_whole_assets.py 8014d167e7b40d34c5cd51cb8d36e117bde58357e5043b826e16d581c14cefa4
scripts/build.py ede40277468549b3bbf9128c1c7258626eca1e3bdb8b4bf468336057c477302d
scripts/draft_units.py f5eb344b40e602002a40435ebb601c629f06dae715970bb63fc2c812341497dd
sources.lock.json 27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb
translation/a00-write-whole.jv-conversation.cnxml 6351a871c26ef4b9d5b87f0d9cc8cdb5604e0ce38d73596ce62fe6441802c8f1
translation/a00-write-whole.jv-academic.cnxml 3273b26f8160d765bbe49c03ec0ba66565edce9f9981f888675f66f5b75c2af2
translation/a00-write-whole.id-academic.cnxml e6ebcab0aca51e32248fdcb0b7ce417f9b9c72fb636955ea53ff6d335329820a
review/audio/a00-write-whole.jv-conversation.md d018ba957ff8f9d2c1e48196fcab9af7ae3c1060b46ccb3fb7b4761f8265c876
review/audio/a00-write-whole.jv-conversation.ssml 0f57c01b5e517219c60291743a78e05f488c2186223a56cf83a098de547a054d
review/audio/a00-write-whole.jv-academic.md 66005c2fa2977100fb8211b9b879c5560331bcb1af4cac322dc9ade8c50e6438
review/audio/a00-write-whole.jv-academic.ssml e288d8c35619c33e9cd96c322066150df85a9844e49a609f63901a225042aa0e
review/audio/a00-write-whole.id-academic.md 7f22dc60a30ed02cdbac8334b9bb0232e21de9f657ed8ade42455d95aa2b0ecf
review/audio/a00-write-whole.id-academic.ssml bdfc7f45172ab027ef694979283dd9b1400c58999578653ce341d636d2f5894f
~~~

The manifest binds all nine asset hashes; target pairs and inspected preview hashes are additionally shown above. Historical text/rule-stage pending-integration statements in DRAFT and the translation-only draft receipt describe earlier/stage-specific work; the current build receipt and this review establish the current generated writing draft, without implying human approval.

Current reviewed integration comprises the earlier nine units plus this writing unit. Complete-module status remains **0 complete / 2 partial / 155 untranslated** at the parent’s module checkpoint. Native educator/register review, integrated browser/visual/screen-reader review, supported voice selection, synthesis and listening remain pending. Human/listening approvals and synthesized audio remain zero. The full A00/A10/AX-2 assignment continues.

