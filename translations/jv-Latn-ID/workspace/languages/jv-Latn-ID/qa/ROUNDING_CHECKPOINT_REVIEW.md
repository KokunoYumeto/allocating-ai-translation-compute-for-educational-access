# Independent entire-rounding integration checkpoint

2026-08-31. Bounded review of the complete A00 m81243 / fs-id2472737 production integration. This report owns no source, translation, rule, asset, renderer, receipt, or generated-output changes.

## Outcome

No remaining numerical, operand/place, source-order, question/answer-boundary, or finite-readout defect was found in the inspected current rounding scope. One direct-helper cache-mutation defect was independently reproduced, reported, repaired by the integrator, and retested here. The final independent regression run passed 174 tests in 81.797 seconds, with no skipped tests.

This is not native Javanese, integrated-browser, assistive-technology, listening, audio-provider, or publication approval. The coverage snapshot remains 0 complete modules, 2 partial modules, and 155 untranslated modules. The 10 registered additional unit builds plus the initial pilot do not establish module completion.

## Finding discovered and corrected

At the initial committed `7fb0d2a` helper snapshot, a valid returned `BoundMath` object retained a mutable `rounding_speech` mapping. Changing `bound.rounding_speech[id(root[1])]` after valid binding caused the public narration helper to return the replacement population statement in all three tracks, despite unchanged source, target, and rule hashes. This did not occur in saved readers/transcripts; it was a fail-closed helper-boundary gap.

Original helper SHA-256: `0527895ea66a07ab357a38e1efb85d52dc5704babc30e32960547c69b56ab7fc`.

The repaired `scripts/rounding_checks.py:255` reconstructs registered speech from the current rule contract. The public `narrate` guard at line 291 now checks the constant rule digest, exact registered source/target hashes, live tree snapshots, and all three mutable speech/math/context caches; line 306 rejects changed caches. It returns the reconstructed registered speech. The focused regression is `scripts/test_rounding_workflow.py:96`.

I independently reran the original cache mutation and related attacks after repair. All were rejected, including altered speech cache, integer-key math cache, emptied context-only set, and a changed target accompanied by a forged new tree snapshot. Current helper SHA-256 is `7579182f2b1606ec4aebc3583b8acdf00ca748b5679e16267226a02d23084035`. Saved rounding outputs remain byte-identical to the pre-repair outputs.

## Actual source and translation inspection

I reopened the complete actual Indonesian and English section, not only the build receipt. The section has 30 direct children including its anonymous title; exact included slice is `[0,30)`. It begins with “Membulatkan Bilangan Cacah,” ends with note `fs-id3323694` / final descendant `fs-id1881276`, and excludes the next section `fs-id2296006`. Previous section is `fs-id1339359`.

Source inputs read:

- `downloads/jv-Latn-ID/a00-id/modules/m81243/index.cnxml`: 99,085 bytes, SHA-256 `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251`, pinned Indonesian commit `3de9207f56f8b5c57c017abf973fb04e00d740f1`.
- `downloads/jv-Latn-ID/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml`: 99,062 bytes, SHA-256 `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`, pinned canonical commit `38cae454e644abf9f0a623e876994553881597c9`.
- Complete actual `translation/a00-rounding.edits.json`: all 127 exact phrase rows plus preservation requirements and declared target-only choices.
- All three saved translated CNXML roots; all three saved transcripts read end-to-end; all three actual SSML files parsed and compared paragraph-by-paragraph with those transcripts.
- Current finite rule fixtures, matching/binding code, asset manifest, actual saved HTML structure, and new persistent production tests.

The source census is 104 unique IDs, 69 MathML expressions, 23 media, five tables, nine exercises and nine solutions: three worked examples containing five worked parts, plus six practice exercises. There are three internal figure links and two optional external source resource links. No source answer is absent in this section.

Each of the 69 raw source MathML substrings was parsed namespace-aware and compared independently to the actual source occurrence, stored fixture tree hash, exact source path, and all three saved target trees. Inventory: 69 `math`, 54 `mrow`, 69 `mn`, and 26 punctuation `mo` elements. The 104 IDs remain in identical order in all target CNXML. Exact replay and independent text/tail/attribute digit-sequence checks passed. No hidden source-value alteration was found.

Current canonical tree hashes:

| Track/source | SHA-256 |
| --- | --- |
| Indonesian section | `19fe0a6c486c4c0c1898735c0e4a6a07380bb19d87d21c7b5f440c31a308e6bd` |
| English section | `105ae3a72dc6952299bf6050975755627a0b57a3bcff3372ccde9b71f0df28be` |
| Javanese academic section | `bdc90a39489954740ec55260eccbef04b26b7ad1b718bc424a9198c8dcee576a` |
| Javanese conversation section | `cbadaa401c20514a95f2987cad0068ac43787293457ddf726bd7281499bf716a` |

## Numerical and readout results

I recomputed all 17 declared cases independently using lower/upper nearest multiples and choosing the upper multiple on an exact tie, rather than simply trusting the production formula or expected result field:

| Input | Requested multiple | Result |
| --- | --- | --- |
| 19,651,127 | 1,000,000 | 20,000,000 |
| 19,651,127 | 100,000 | 19,700,000 |
| 19,651,127 | 10,000 | 19,650,000 |
| 76 / 72 / 75 | 10 | 80 / 70 / 80 |
| 843 | 10 | 840 |
| 23,658 / 3,978 | 100 | 23,700 / 4,000 |
| 147,032 / 29,504 | 1,000 | 147,000 / 30,000 |
| 157 / 884 | 10 | 160 / 880 |
| 17,852 / 4,951 | 100 | 17,900 / 5,000 |
| 63,921 / 156,437 | 1,000 | 64,000 / 156,000 |

Decision-digit positions, requested-place positions, and replacement-zero positions agree. All 43 finite numeral lexemes were independently decoded across three tracks (129 checks), as were the 51 per-track result readings. Reviewer-only decoder adjustments were needed for contracted hundreds before tens; these were harness corrections, not production defects.

Important current readout checks:

- The 2013 New York population stays a historical source example, not a newly asserted current population. The three occurrences of MathML 20 retain the following million unit; they are among the eleven formulas prohibited from detached speech.
- `fs-id2368933` alone retains literal “dan seterusnya” / “lan sateruse.” There is no ellipsis glyph, and commas/full stops do not become infinite-sequence narration.
- The general rule includes the equal-to-five branch. The 76 diagram's stricter “greater than five” label remains correct in its finite context. The 75 tie goes to 80.
- Carry cases preserve 9+1=10, writing zero in the requested place, and adding one immediately left, including the source instruction to repeat if that digit is also 9.
- The entire regrouping paragraph `fs-id1751923` retains MathML counts 1/9/10/1/0/1/2/0 and explicitly names groups of ten thousand. It says “bagean be” / “bagian be” once; it does not duplicate the already-present word “part.”
- Literal diagram result witnesses retain grouping separators and zeros in 23,700; 4,000; 147,000; and 30,000. No zero is discarded by cardinal speech where the diagram teaches a written placeholder.
- The five tables retain their source `cols="3"` declarations and actual two-cell rows (5, 4, 4, 4, 4). Empty cells stay empty; no third populated cell or header is invented. Speech follows row/cell content once, without also repeating the complete accessibility summary.
- All nine question/solution boundaries remain separate. Three worked titles supply their own cues; six untitled practice solutions receive exactly one editorial answer cue each. Prompt readings contain the requested input/place, not an inserted rounded answer. Whole-question comparison, not a misleading substring test, protects cases such as spoken 147,000 being a prefix of spoken 147,032.
- Ordinary cardinal reading of an unrounded rounding question is appropriate here; this is not a name-writing question in which spelling the full answer would leak the requested answer.

The production rules contain 69 math fixtures, 28 prose fixtures, 23 chart fixtures, five table fixtures, seven structural cues, and 30 ordered block fixtures. Eleven MathML occurrences require complete population/regrouping context; isolated calls reject them.

## Saved reader, SSML, links, and assets

The actual saved HTML contains 207 MathML expressions, 69 embedded images, 15 tables with 126 cells, 63 rows, and 87 track articles (29 content blocks × three tracks). All table accessibility descriptions match their actual target CNXML. The four-step procedure is an ordered list in each track; its yes/no sublist remains bulleted. Both circled-part lists remain ordered lower-alpha lists while suppressing duplicate native markers and retaining source circled labels.

Each saved SSML has 30 unique source-derived marks in source order. The anonymous title uses the explicitly derived mark `m81243--fs-id2472737--title`, not an invented source ID. The 90 block paragraph texts exactly match the corresponding saved transcript bodies after XML parsing. Locale and spoken track labels are explicit. The Indonesian editorial diagram notice occurs once before the marked content and does not masquerade as a source block. The other tracks do not receive that Indonesian speech notice.

The two exact original OpenStax resource URLs remain visible links in all three HTML tracks. They are optional outside resources, not fetched, translated, or bundled destinations. The reader explicitly says their destination content is not included offline. The registered renderer rejects a changed external URL and use under an unrelated unit. No destination-availability claim is made.

All 69 track-to-asset bindings matched the actual bytes embedded in the saved reader. All 23 canonical raster witnesses already present on disk matched the manifest's canonical SHA-256 values. Source and target MIME handling was checked: the three 034 stage PNGs remain incorrectly labelled JPEG in source CNXML, but their embedded output MIME is PNG. No source CNXML was rewritten to hide this inherited issue.

For actual independent visual inspection at this checkpoint, I viewed:

- All twelve existing academic derivative PNG previews.
- The four visually different conversational previews (031, 035 result, 036 result, 038 result).
- All eleven retained numeric source images: three number lines and eight PNGs.

I verified all 24 preview file/RGB hashes against the render receipt and independently confirmed the eight claimed pixel-identical register pairs. The recorded producer renderer is ImageMagick 7.1.2-26 Q16-HDRI with RSVG, density 96, white background, alpha removed. I inspected those existing previews; I did not claim to execute a new renderer or an integrated-browser pass.

The inspected Javanese arrows, requested-place underlines, crossed-out units, replacement groups, and carry destinations agree with their finite descriptions at those standalone sizes. The retained number-line points are visibly teal/cyan at 76, 72, and 75, with red endpoints 70/80. Current Javanese alts and all three narration tracks use accurate location-focused descriptions. The untouched Indonesian alts still contain the inaccurate orange/black description, and some untouched Indonesian SVG geometry remains misleading or incomplete. The explicit reader/audio editorial notice distinguishes intended/canonical diagram narration from those unchanged Indonesian assets. This is an inherited disclosed limitation, not approval of the inaccurate source drawings.

The source English result alts incorrectly say “nearest thousand” for 3,978 and “nearest ten thousand” for 29,504. The Indonesian text and current Javanese tracks retain the correct requested hundreds/thousands. Neither pinned source was silently changed.

Standalone images are not evidence of readability at three-column integrated scale. No browser zoom/reflow, font substitution, native-language, screen-reader navigation, or listening test was performed.

## Independent regression and adversarial evidence

First full discovery: 173 tests, 135.988 seconds, one failure in the separately changing summary-asset deterministic-manifest test. It compared a new saved visual-review description with a generator version still returning a pending description. No rounding test failed. After the integrator stabilized that separate generator/manifest and added the rounding cache guard test, my fresh full discovery passed 174 tests in 81.797 seconds with no skips. This is the suite as discovered at that run; later parallel additions are not retroactively certified.

Command: `python -B -m unittest discover -s languages/jv-Latn-ID/scripts -p 'test_*.py'`.

Separate independently authored read-only helper probes after repair: 24 intact controls, 234 rejections:

| Category | Rejections |
| --- | ---: |
| Copied actual source/target nodes | 24 |
| Empty dictionaries | 24 |
| Plain dictionary copies of valid bindings | 24 |
| Empty BoundMath objects | 24 |
| Wrong track | 24 |
| Eleven detached context-only formulas × three tracks | 33 |
| Speech/math/context cache mutations | 9 |
| Changed math/chart/block fixture readings | 9 |
| Changed target with forged matching snapshot | 3 |
| Altered complete target rebinding | 30 |
| Altered complete source rebinding | 30 |

The whole-tree mutations included a negative year, changed year, unregistered MathML attribute, changed comparison tail, lost million unit, changed marked-point alt, changed URL, blank cell changed to zero, inserted answer material, and an unknown root attribute. These probes called the public production helpers and did not edit files.

The saved-product regression reconstructs products in memory and compares exact bytes; no build command or write mode was run by this reviewer. I also compared 108 other committed saved CNXML/transcript/SSML/HTML files against `7fb0d2a`; they were byte-identical. This count is a concrete file comparison, not a claim that every full assigned module is integrated.

## Actual canon checkpoint

I read the full actual readable bunder, bulet, and cedhak query files during this review, then reopened relevant complete headword/variant entries for atus, éwu/éwuan/sèwu, yuta, likur, lima/sèket/salawé, sanga, sewidak, kiwa, tengen, tambah, ganti, luwih, gedhé, cilik, gunggung, owah, and tetep while checking current wording and readouts. This is direct readable-entry consultation, not a shelf-count or download-only claim; unrelated results beyond the selected entries are not claimed as fully reviewed.

Bunder attests physical roundness/circling, not standardized numerical rounding; bulet concerns belit and is not supporting rounding evidence. Cedhak/cédhak supports near. Pambunderan/mbunderake/bunderna and composite place-value expressions remain explicitly provisional pedagogical choices. The reviewed mathematical rule comes from the exact source, not a fabricated dictionary attestation. The same caution applies to compositional full large-number readings. The two registers remain ngoko-derived academic/conversational drafts, not a krama equivalence or native certification.

The shelf had 47 entries during these consultations and grew to 49 during final report verification. That growth is separate parallel work; the two new entries are not retroactively claimed as consulted here, and neither count implies review of the entire shelf.

## Final actual-file snapshot

Paths below are relative to `languages/jv-Latn-ID`. Hashes were computed from actual saved files after the cache repair, not copied from receipts. All seven output hashes were also checked against their receipt. The 47 individual asset products are transitively bound by the hashed manifest and directly checked bytes above.

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| audio/a00-rounding.rules.json | 863371 | `50f1ca7cac31cae4acc62939f46787fb6a144d5cfa944593d9365d842ef1147f` |
| translation/a00-rounding.edits.json | 44342 | `2ac25d55186d4750b2baf2ba9096e4530045a9918e40d7463bf67a06150fee99` |
| translation/a00-rounding.assets.json | 91524 | `ee409884dfe05113ce081ab155f0d531aa3ce1273582b3bd27640deb861d4e33` |
| qa/a00-rounding.draft-receipt.json | 4525 | `577a2fcf33db4806bbd98000395b83502062a28e9af5a0108bd72d3e82696612` |
| qa/a00-rounding.build-receipt.json | 2295 | `7adfed7f384b80edaf1b6ecccd9d853e70c11c521bef33b3396cbdb013e11b57` |
| qa/a00-rounding.render-receipt.json | 9251 | `95a3098feba75eb3d8c1991cc0d1e89f028a705a1a2f2e5c704afe4713d757a1` |
| scripts/rounding_checks.py | 17845 | `7579182f2b1606ec4aebc3583b8acdf00ca748b5679e16267226a02d23084035` |
| scripts/test_rounding_workflow.py | 10962 | `1db4f3ee2b211675cd6890cb743e0c4a7de5ae74a7d1b4af3d8be8c3f23965e0` |
| scripts/prepare_rounding_bindings.py | 4525 | `e1b582bd745ddbba6a4f8da991cd75464aa51a7c27d8b7525b59b1ec01064a8e` |
| scripts/prepare_rounding_assets.py | 15196 | `aa1062290b8f5c09fd80a7c7cde61343e53e7358178728a1e67e7a2efee79b7c` |
| scripts/test_rounding_assets.py | 7377 | `a5d06819fb971b50da38f766cebfc0a1cecf5298c45aa4ddb426d7adf4c972d0` |
| scripts/build_units.py | 44397 | `36083967a3953ce15dbfe2fba0bb94e7aa5b43174d0edf99caf99039713d7765` |
| scripts/build.py | 21160 | `d70acc89633813b3a15ee214134e783c5f56f39efaf6fadca7637940d366dd92` |
| scripts/draft_units.py | 9593 | `1d7c59014b7cd9af47157e24e1141aea74c8c71348bdd40d4e22f2159677e155` |
| scripts/coverage.py | 32145 | `af7e4039df548e4678ae2d559d6e8ae386e99f38c938b80a036e9c100c143e52` |
| translation/a00-rounding.jv-conversation.cnxml | 25520 | `c7e9d65ba5b634344402704ec96540ca60278dc4fc677611e21d66a3b4261b0a` |
| translation/a00-rounding.jv-academic.cnxml | 26021 | `29e530e53dd6c5979fd4ba85ad82ee470c8f8580839ccfc9c7cd7d6106b92b1a` |
| translation/a00-rounding.id-academic.cnxml | 25185 | `1f12a024a42bbab88d3044bfa2c86475d412dc01af8a6c184f1136fda35427de` |
| review/audio/a00-rounding.jv-conversation.md | 12871 | `9184efc449144a2a17511276b618c6e0bb85f161e8f2f70b6453be39be9bd4ae` |
| review/audio/a00-rounding.jv-conversation.ssml | 14086 | `68e9421a2290a60f99ebe15f3dbd9843f3cce39b519fefbd6bde480a409179df` |
| review/audio/a00-rounding.jv-academic.md | 13123 | `dfe35fae2e6aa7a479ba4912006a532e3d6b9fd458577ff74c7282045d3c6f38` |
| review/audio/a00-rounding.jv-academic.ssml | 14338 | `c9a13e9c338b439c71728666dda6ac20e8628ab3f281c65efb8310cf0be445d9` |
| review/audio/a00-rounding.id-academic.md | 12945 | `80022e2aa2b3e9788d16af4fca408d2bc4e6bc4c934247ede7371a76d3b02461` |
| review/audio/a00-rounding.id-academic.ssml | 14161 | `bdc84882ed27d4ef9ef3591f62198c18b883ec1244658f612a4775d43a4d19dd` |
| review/units/a00-rounding.html | 513183 | `9eb50acdb173cd2abea0c39b546931e074db6ea63bc5402155f654da050ff017` |
| canon/sources.lock.json | 37674 | `f520299ef2faf42e380f454da1fe515fe2f6a41101015676d7b37c22a5db3c77` |

The reviewed production unit is structurally integrated with finite narration and passed bounded checks. Native educator review, integrated visual/assistive-technology review, synthesized-audio listening review, and the entire A00/A10/AX-2 assignment remain unfinished.
