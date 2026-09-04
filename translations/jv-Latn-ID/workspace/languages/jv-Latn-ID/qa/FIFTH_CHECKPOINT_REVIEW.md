# Fifth checkpoint: expressions/equations and shared reader fixes

Independent review, 2026-08-31. Final snapshot is **after** the expression-rule staging clarification and the digit-place duplicated-marker correction. Only this review file was written by the reviewer; no build, source edit, shared-code change, or asset generation was performed by this task. Product replay in tests was in memory.

## Outcome and findings

No unresolved numeric, operand-order, classification, formula-scope, source-replay, or deterministic readout defect was found in the new expressions/equations unit at this snapshot. Shared reader fixes were checked against all nine current units, not only synthetic tests. This is a bounded structural/content review, not release, native-language, browser, screen-reader, visual, or listening approval.

Two issues were reported promptly to the coordinator and corrected during review:

1. **Duplicated list markers, current digit-place reader — fixed.** `review/units/a00-digit-place.html:81` (also lines 96/111, 127/142/157, and 174/189/204) had an `ol type="a"` containing explicit source `ⓐ`–`ⓔ` spans, with native markers still enabled. This affected the three five-part lists `fs-id2218367`, `fs-id1386307`, and `fs-id1508784` in all three tracks. Static HTML/CSS implied `a. ⓐ`, `b. ⓑ`, etc.; no live-browser observation is claimed. The current renderer preserves `ol type="a"` and the original spans while adding `source-labeled-list` to suppress the duplicate native marker. The actual source has `class="circled"` and first-child `span class="token"` labels; these were inspected. All nine saved lists now carry the suppression class. The naming how-to `eip-375`, which lacks explicit circled labels, remains genuinely numbered and does **not** receive suppression. The new actual-source/saved-reader regression catches this formerly untested distinction.
2. **Contradictory current staging metadata — fixed.** `audio/a10-expressions-equations.rules.json:52`, `:997`, and `:1002` formerly said production summary/reader/SSML support was pending while the same file claimed production success. The current wording explicitly separates historical rule-stage work from the implemented production pipeline. The earlier text-draft handoff remains a historical snapshot, not a claim that current outputs are missing.

Current limits, not hidden passes: formula prosody, the provisional `wujud aljabar`/`persamaan`/`pangkat` choices, academic/conversational naturalness, and comprehension need a Javanese mathematics educator. A successful static DOM check does not establish browser rendering, assistive-technology behavior, or three-column legibility. Prior static SVG checks are not upgraded to integrated visual approval.

## New unit: exact source/content review

Actual pinned source modules were read and hashed:

- Indonesian `downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml`: SHA-256 `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635`.
- English `downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml`: SHA-256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`.

Scope is source section `fs-id1170655150800`, original title plus direct children `[28:40]`: first `fs-id1170654957085`, last `fs-id1170655205588`, final descendant `fs-id1170654959584`; exponent-introduction child `fs-id1170654982105` is excluded. All 34 IDs (33 new plus the shared section), 21 MathML expressions, three tables, three exercises/solutions, and eight classifications are present. There are no media references or registered nonspoken source blocks in this unit.

The exact phrase ledger, both generated Javanese CNXML variants, Indonesian CNXML, all three transcripts and parsed SSML documents, actual HTML, all math/table fixtures and classification checks were examined. The grammar analogy is explicitly tied to the Indonesian witness and supplies Javanese equivalents; translated table cells are not silently labeled as literal Indonesian sentences. The source's English “verb” versus pivot “predicate” wording is disclosed in the draft, not silently treated as a universal Javanese grammar rule. The table accessible-description correction from a supposed slash to actual stacked `x/y` is explicit; the Indonesian source attribute and MathML remain unchanged.

| Source role | Verified content |
| --- | --- |
| Expression table `fs-id1170655221887` | Three columns, one header plus four data rows: `3+5`, `n−1`, `6·7`, stacked `x/y`; numerator x before denominator y. All formula/word/phrase columns are spoken, with explicit letter names. |
| Equation table `fs-id1170655090988` | Two columns, one header plus five data rows: `3+5=8`, `n−1=14`, `6·7=42`, `x=53`, `y+9=2y−3`. Both `3+5=8` and `6·7=42` are correct; variable equations are not solved. |
| Worked question and `eip-10` answers | `2(x+3)=10` equation; `4(y−1)+1` expression; `x÷25` expression; `y+8=40` equation. The four formulas are repeated only where the source repeats them. The solution table has four rows, two columns, no invented header. |
| First practice | `3(x−7)=27` equation; `5(4y−2)−7` expression. |
| Second practice | `y³÷14` expression; `4x−6=22` equation. The exponent closes before division; no `y×3`, flattened `y3`, or division inside the exponent. |

All six pairs of parentheses retain `stretchy="false"`, all nine implicit multiplication sites are read, subtraction is U+2212, the multiplication dot is U+00B7, and division is U+00F7. The exact `msup` tree is retained in displayed MathML. Javanese 25/53 use `salawé`/`sèket telu`; 22 is `rolikur`. Mathematical readings are shared between Javanese registers while the surrounding explanations differ.

All eight answer classifications agree with source equals-sign presence and remain in their source solutions. The worked solution keeps its existing `Panyelesaian` / `Cara Ngrampungake` / `Penyelesaian` title. Exactly two new spoken `Wangsulan.`/`Jawaban.` cues occur, one before each untitled practice solution, without duplicating the worked title. Question formula fixtures contain no appended classification or computed answer. Each fixed table is spoken once, not as both its long accessible label and a repeated recursive table. There are 13 source-ordered narration blocks per track, with matching SSML marks, locale, and complete paragraph content.

## Shared changes across nine current units

An independent standard-library HTML parser compared saved DOM content with source-bound CNXML and exact phrase replay. This did not use a browser, substitute test outputs for artifacts, or trust receipt claims alone.

| Unit | Source MathML | Source lists | Shared scope checked |
| --- | ---: | ---: | --- |
| a00-number-sense | 17 | 3 | Explicit-label lists retain source spans without native bullets; exact target replay and MathML. |
| a10-variable-bridge | 9 | 0 | Exact target replay and displayed MathML. |
| a00-place-value | 51 | 0 | Exact target replay, mathematical text, currency regressions, embedded media. |
| a10-operation-symbols | 11 | 1 | Genuine bulleted list remains `ul`; exact mathematical trees and readout regressions. |
| a00-digit-place | 40 | 7 | Three lower-alpha lists remain ordered with only source circled labels; other labeled/bulleted list kinds preserved. |
| a10-equality-symbols | 23 | 0 | Exact registered linguistic `mtext` replay, mathematical trees, retained spacing node. |
| a00-name-whole | 9 | 1 | `eip-375` is `ol type="1"` in all tracks with both ordered steps intact; digit-group no-answer-leak tests pass. |
| a10-grouping-symbols | 2 | 0 | Exact registered linguistic `mtext` replay, unchanged grouping trees and spacing node. |
| a10-expressions-equations | 21 | 0 | Three tables, translated summary exposure, exact formula/answer fixtures. |

Aggregate independent checks: **eight HTML files / nine units, 549 displayed MathML trees, 36 source lists, three translated-or-retained summary labels, 27 complete transcript/SSML pairs, and 51 embedded media instances**. DOM MathML namespaces/tags, attributes, token content and hierarchy match the corresponding CNXML in every track. Each embedded asset's decoded bytes match the appropriate local asset and manifest hash, and its HTML alt matches that track's actual CNXML alt. This is byte/structure checking, not a new visual inspection of those images.

The headerless `eip-10` source `summary` is translated in target CNXML and exposed unchanged as HTML `aria-label`; no column heading is fabricated. Shared summary replay fails on an unknown source phrase. Existing source `aria-label` takes priority if both attributes exist.

The revised `source_bound_math()` first matches exact source fixtures, then compares an exact replayed Javanese MathML tree, including registered linguistic `mtext`. It does not authorize arbitrary words merely because the structural shape resembles a known tree. The currency regression proves `$77` cannot silently become `€77`; nonlinguistic `mtext` is protected both by translation validation and exact narration binding. This is a finite-source guard, not permission to infer general algebra or unseen currency readings.

## Actual tests and evidence limits

Final read-only command from `languages/jv-Latn-ID/scripts`:

```text
python -B -m unittest test_qa test_unit_workflow test_digit_place_workflow test_equality_workflow test_name_whole_workflow test_grouping_workflow test_expressions_workflow test_reader_contract
Ran 125 tests in 27.698s — OK, no skips.
```

Before the duplicated-marker test was added, all 124 tests passed despite that real reader defect. Final targeted suite is nine expression tests plus seven shared reader-contract tests: 16 passed. The independent DOM/source checks above complement rather than merely restate these tests. In-memory adversarial tests reject changed numbers/operators/letters/attributes/namespaces/anchors/ordinals, fraction reversal/flattening, exponent flattening or altered division scope, missing or changed table rows/labels/classification, and question-answer leakage. Initial receipt's 21 hashes and seven unit receipts' 49 output hashes matched actual saved files; no publication or whole-module status follows from that match.

At this checkpoint the reviewer consulted actual readable C07 `lima`, C18 `likur`, C21 `ping`, C22 `para`, C23 `gunggung`, C26 `wolu`, C27 `sanga`, C29 `kurung`, C30 `tutup`, and C34 `rambang` entries. The mathematical senses of multiplication, division, total, written parentheses, and repeated equal factors were distinguished from homonyms. `rambang` is an attested mathematical alternative, but its plain-text example flattens a superscript to `43`; it is not used to rewrite the source formula. The retained `pangkat` is a disclosed school loan, and end-of-power/fraction markers are explicit narration conventions, not certified traditional formula prosody. Component attestation does not certify entire compounds or native register suitability.

Selected readable evidence hashes:

```text
lima.txt     3ed3c9e246682760330b56c4ab7c8aa3517e00844f5761fcca7c2bc0a499fd20
kurung.txt   215e0412cd2db1a7bba144f18fcfa2fd244daed6812d32b26e55f2d4ce960239
tutup.txt    693acc5199d95abb00b21495f1ef58d5ed917d036dea4e0cbf3d9349267ac6c5
ping.txt     e1442bf2e7d8f24ed3dc6d09b8fe78e0fd4fc692b65c482fdcce84cdc06f49bf
para.txt     9fdf138bf925f083805482e088d832a8f10c831a727eaf0f4c9bc3f23c76c097
gunggung.txt eaa9e9cfd8d343199f784c98fcdb90bc394f6819408b0ff5bc9f0e132de16c2e
rambang.txt  a45727af8975350e044d15deff91892693b03a47f545e6f14d75182b9cf13bdc
```

## Final hash snapshot

Paths below are relative to `languages/jv-Latn-ID/`. Subsequent changes invalidate the corresponding part of this snapshot.

```text
scripts/build.py ede40277468549b3bbf9128c1c7258626eca1e3bdb8b4bf468336057c477302d
scripts/build_units.py b1da7fb597ac6e2ad17e26dd0b036c9f6e5bc1911627979b27dff7ae3bdb27d6
scripts/draft_units.py d54b327b208fa77d3f670de4c55114cc20e28a92ece3dbd84a02944b6f372fe4
scripts/test_reader_contract.py 8e09aa93250fbaf039e9d38d62679d1531ecdc7441326e1e096fdddb54143603
scripts/test_expressions_workflow.py 6a8fb90d19e341459458f46a9f565d8509633eaee14e6981c8718b8086394842
audio/a10-expressions-equations.rules.json a69c080f53f1f7ab38c8ec5a596f0e96ea6211924703972075aab033a6fc1971
translation/a10-expressions-equations.edits.json 37913876fb43a5c4f2aa7af304166e137702760cd5fafc86cf1758a2d35da0f9
qa/a10-expressions-equations.build-receipt.json 7cec44fec274c87321300e7a800726ad03bc2b5833bff5035a153e65a4c73c86
qa/a00-digit-place.build-receipt.json 0a592d034f117bc098d95d76c41bb681b86a9e04889f5e04b64fe8df3b01cbdc
review/pilot.html 5c442b7f188285442ce57a91a147d23ad6c551ead52d0408c22c194aa128f498
review/units/a00-place-value.html 1265702e0a658524a98918dd5599c85f64138d723306d31c658cc35c795f93eb
review/units/a10-operation-symbols.html 2d7421ed7757f464708530ea778d1c2ac390b3bf39ff3ccc6f09c604a6216adf
review/units/a00-digit-place.html f846febe3f817ec63894edc1219b4f816498902022afe92220dafbc56d6580d5
review/units/a10-equality-symbols.html 9d83d11bfe529b0acf645a8dbe7024dca6d8a4fca293c23ae651859b8245c179
review/units/a00-name-whole.html 34ac13f62d7cc172c79817ec064e07446c5e9a992e7641d522a47581b838b7eb
review/units/a10-grouping-symbols.html 73af01a5a64e5893b404425bd0d2f87bf2ad6586a88079e8af5730ab8cde9603
review/units/a10-expressions-equations.html b814405bc16fbafed950f19890d51bb9a6d30656d9af6dc4e66b0d124d5663a1
translation/a10-expressions-equations.jv-academic.cnxml f05b5836c54848788451cb3abbf54559e695b53c750911160033592c8ac6f683
translation/a10-expressions-equations.jv-conversation.cnxml 795906b2627b65bb61d2e8a5e0a3a2a7204241d1ec1ea6970f99bf7b2f14197d
translation/a10-expressions-equations.id-academic.cnxml 1c31076945d7abf49096ac300aad6ae11e1289a90780868a6fa8898a2c401365
review/audio/a10-expressions-equations.jv-academic.md 9765df013a3c69560e4ff4286f460e31aba4ee6260b3cd7453de50204fc21b4a
review/audio/a10-expressions-equations.jv-conversation.md 80f5674d8cab99c8b90060672e80d4ab8a9c3b51ec898cd73230ea1a2c95ef74
review/audio/a10-expressions-equations.id-academic.md dc32704159aaab3b29ca548b7dd217b8f0fde4a5708e1c000cda24bf52262020
review/audio/a10-expressions-equations.jv-academic.ssml dba454c24c6cf87a23d08f9dfd99e1ffed750a88ea43e928b5dfa6581987eb85
review/audio/a10-expressions-equations.jv-conversation.ssml 0e2caaff1295b83cf345da27314cdb7610b46d2e86831a02faf5af4457bc146e
review/audio/a10-expressions-equations.id-academic.ssml 01fc239af7983316974dddd2b4e6f62a31a409bd9b05de682a34af8e8d09f99d
```

Nine-file package digests bind each unit's three CNXML files plus all three `.md` and all three `.ssml` files. Algorithm: create a mapping from the nine sorted language-relative paths to their byte SHA-256 values; SHA-256 the UTF-8 `json.dumps(mapping,sort_keys=True,separators=(',',':'))`. Readers are separately hashed above.

```text
a00-number-sense          3660fb19a3c3f6a952671800110b77f38cfe90d4da85bdff1a4139febca2637c
a10-variable-bridge       fc130ff56a48e80ea349b9091991b6015b254781bc47045112062ee9ea3e6a3f
a00-place-value           c37aacd8ae48fbb335c735e1aeca71cffa51569b5d56ce9da5be92275f7b5091
a10-operation-symbols     638f44fd88054e6970c601fbe6103a53bb8728aa8a6dbfe495475e5bd1fd98fb
a00-digit-place           3b8ea9dac6e5dc89906e7d937bc04e3afbdf4445b390ffa3360edcb7d0c0d9b0
a10-equality-symbols      bb9a60b996af50ef31141746978264010a7e5db2ba8aa9a02b89fcecc53ce664
a00-name-whole            0e2c225fc6c4c1ae9e823d59f1677f14dbb53f3fbb34241489c0c165a98641d5
a10-grouping-symbols      6494813f949f8f83a0fad93f702d2f1597fcb284bb0e44ea901a8067fed2df44
a10-expressions-equations 200cee55f7471785a9b4c6737c29a030e7cd4b6d958540e8e4ec35a3413c69d0
```

Whole-assignment status remains **0 complete modules / 2 partial / 155 untranslated** at the parent's current module checkpoint. These nine integrated bounded units and the separately completed 58-exercise text draft do not complete all A00/A10/AX-2 work. Human approvals, synthesized audio, native pronunciation approval, integrated browser/visual approval, and listening approvals remain zero/pending.
