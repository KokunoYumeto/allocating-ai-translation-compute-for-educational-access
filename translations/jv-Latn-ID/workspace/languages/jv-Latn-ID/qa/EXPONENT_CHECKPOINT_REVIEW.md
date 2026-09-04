# Exponent integration checkpoint review — 2026-08-31

Bounded independent review of the entire exponent topic in A10 m82453, within source section fs-id1170655150800. **No new mathematical/source-target/readout defect remains in the saved exponent production draft within this review.** A direct-helper fail-closed gap was reproduced, reported, fixed by root and independently retested. The inherited Indonesian source-image-alt discrepancies described below remain; this is not an unconditional accessibility approval.

Only this review file was written by this reviewer. No shared code, source, rule, receipt, asset or generated output was edited or rebuilt. Tests and deterministic products ran read-only/in memory; no acquisition, source-preparation main routine, large extraction, cleanup or provider call ran. Complete A00/A10/AX-2 remains unfinished.

## Discovered helper defect — corrected

The initial direct build_units.narrate path selected known prose/media/table fixed speech by source ID before checking the actual element/context. Independently reproduced with a valid bound map and copies of:

- fs-id1170655213989: changed the positive-integer domain tail to a negative-domain statement.
- fs-id1170655111941: changed the image alt to an infinite product without a factor count.
- eip-958: changed the first empty left cell to a literal zero.

All three direct calls returned the old fixed speech. The normal complete blocks path already rejected the altered full target with “Changed whole exponent target”; the defect did not corrupt any saved output. The initial 153-test suite passed despite this hole.

Root's current fix in scripts/build_units.py:98 validates the complete source/target, fixed contexts and finite semantics at binding. It retains the actual nodes, their exact canonical trees, track and rules hash. The entry guard at scripts/build_units.py:203 requires this context for every exponent element, before fixed prose/media/table/reference dispatch. This closes copied-ID and post-binding mutation cases without changing linguistic output. scripts/test_exponent_workflow.py:118 adds the dedicated regression.

Independently reran the original three mutations across all three tracks and added wrong reference targets, intact-but-detached copies, empty/plain-dictionary maps, changed rules, wrong track, in-place mutation after binding, full-root rebinding, unknown MathML and all seven context-only formulas. **204 rejection probes passed; 15 intact-node controls succeeded.** These are actual calls into the current helper/full-path implementation, not a separately invented guard model. No intentionally forged internal BoundMath state or general security guarantee is claimed.

## Actual source boundary and preservation

Read the actual pinned Indonesian and English source slices, all current phrase rows, all three actual target/source CNXML variants, all three saved transcripts, the actual reader/SSML and relevant implementation/tests. Source access was to existing small module files, with full-module hashes verified:

- ID: downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml — SHA-256 2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635.
- EN: downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml — SHA-256 a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed.

The original section has 53 direct children. This complete exponent topic takes original zero-based [40:53], plus the original section title for context: **13 new direct children, 14 selected blocks, 32 IDs including the reused section ID, 31 new IDs, 32 MathML expressions, 22 msup, two media, two tables, three exercises and three solutions**. It begins fs-id1170654982105, ends top-level fs-id1170655102894 and last descendant fs-id1170655114560. The following section fs-id1170654953465 is excluded. This is completion of this topic, not the entire m82453 module.

All three CNXML trees equal exact source/phrase replay. Indonesian selected-source canonical SHA-256 is 98a02d384682f547090ab22173cf709d95a9336b7f5d749e98697e4d72ca041d. Current academic and conversational canonical hashes are 4f395164b6efe9cc4f3e81eb2c32b74ae256e2db0c302b8895ac9a99376342d1 and 870d0859a5f3a1fe5a4c69152e065d6079536ae6616b072d15b5e09b90600cb4.

All 32 Indonesian MathML fixtures match exact actual namespace-aware trees at their top-level anchor and one-based ordinal. Both Javanese tracks preserve them. The only EN/ID MathML differences are overall expressions 12 and 14: English linguistic ordinal n superscript th becomes Indonesian plain n, rather than a mathematical power. EN has 24 msup; ID/targets have 22. Those inherited differences are not translation damage.

The source clarification of equal-factor count and the positive-integer n domain is already present in the pinned Indonesian text. Javanese retains it; no domain was silently broadened to zero/negative exponents. Factor count n is not n additional binary multiplication operations.

## Finite numeric/readout findings

Checked the complete exact inventory, not flattened table text:

~~~text
A10-EXP-M01 2·2·2·2·2·2·2·2·2.
A10-EXP-M02 2·2·2
A10-EXP-M03 2^3
A10-EXP-M04 2·2·2·2·2·2·2·2·2
A10-EXP-M05 2^9.
A10-EXP-M06 2^3,
A10-EXP-M07 2^3
A10-EXP-M08 2^3
A10-EXP-M09 2·2·2
A10-EXP-M10 a^n
A10-EXP-M11 a^n
A10-EXP-M12 n
A10-EXP-M13 a^n
A10-EXP-M14 n
A10-EXP-M15 a^2
A10-EXP-M16 a^3
A10-EXP-M17 a^2
A10-EXP-M18 a^3
A10-EXP-M19 7^2
A10-EXP-M20 5^3
A10-EXP-M21 9^4
A10-EXP-M22 12^5
A10-EXP-M23 12
A10-EXP-M24 3^4.
A10-EXP-M25 3^4
A10-EXP-M26 3·3·3·3
A10-EXP-M27 9·3·3
A10-EXP-M28 27·3
A10-EXP-M29 5^3
A10-EXP-M30 1^7.
A10-EXP-M31 7^2
A10-EXP-M32 0^5.
~~~

The 26 U+00B7 dots are multiplication. Five trailing ASCII periods and one comma remain sentence/clause punctuation, not decimal separators or multiplication. No new value is appended when reading an expression. The final table base 12 is a whole base under msup, not the digits 1 and 2 separately, and the following standalone 12 belongs to the word-form cell. In particular, flattened “125” is not used as the meaning of 12^5.

M10–M16 are seven context-only occurrences inside complete definition/reading/list prose; direct detached formula narration rejects. Their actual composed speech says every mathematical/linguistic a and n as a letter, retains the positive-integer domain and preserves squared/cubed naming alternatives. It neither reads English th nor treats plain n as an unstated number. The two-item source bulleted list stays two items.

The first table has two genuine header cells and four data rows: 7², 5³, 9⁴, 12⁵, including all naming alternatives. These are names, not evaluated answers. The second table has five headerless two-cell rows; its first left cell is blank, not zero. Speech preserves the left/right roles and all steps: 3⁴ → 3·3·3·3 → 9·3·3 → 27·3 → 81. The complete 81 result appears after the real worked-solution title.

The four practice answers remain 5³=125, 1⁷=1, 7²=49 and 0⁵=0. No 0⁰ case is inferred. Both part labels survive in questions and answers. Each of the two untitled practice solutions gets exactly one Wangsulan./Jawaban. cue; the titled worked solution uses its real Panyelesaian / Cara Ngrampungake / Penyelesaian title without a duplicate cue. Answers do not leak into question speech. The source's fixed 1 or 0 operands may of course equal their eventual answer, but are not announced as computed solutions in the question.

The 125/81/49 result readings are respectively satus salawé, wolung puluh siji, patang puluh sanga (Indonesian seratus dua puluh lima, delapan puluh satu, empat puluh sembilan). Intermediate 27 is pitulikur / dua puluh tujuh. The Javanese productive compound pitulikur is still provisional, not claimed verbatim attested by the selected likur entry.

## Saved reader, transcripts and SSML

Independent parsing of actual saved output checked:

- 39 HTML track/block articles, complete source IDs in all tracks and no duplicate IDs.
- All 96 displayed MathML trees against their CNXML counterparts.
- All 39 paragraph texts; the single source reference has the same real target in every track and an explicit editorial reader label.
- Six tables with exact cell order/text; six genuine scoped column headers across the three first-table copies; no invented headers or zero in the worked table.
- Exact target/source aria-label text. The worked source summary is translated and exposed as aria-label, not invented visible table content.
- Six embedded images with exact file/manifest payload hashes, exact alt and correct per-output MIME: four Javanese SVG payloads, two source JPEG payloads.
- All 129 source/target fixture bindings: 32 MathML + six prose + two tables + two charts + one reference, each across three tracks.
- All 42 SSML source marks and paragraph bodies in correct order, three locale/register labels, and 600 ms inter-block breaks. Every body matches the corresponding actual transcript block.

The three full transcripts were read against actual source, not merely checked for a receipt's success flag. There are 14 spoken blocks per track, no spacing-only suppression in this unit, six whole-prose overrides, two table readouts, two chart readouts and one inline reference label, each exactly once in its intended context. A real reference to fs-id1170654954100 precedes the first table; it does not invent a table number or duplicate the table speech.

## Actual image and canon checkpoints

Viewed both already-local canonical JPEGs and all four existing standalone derivative PNG previews; read all four current SVGs. Verified the preview hashes against the earlier exact static-render record, and asset hashes against current manifest/embedded payloads. This reviewer did not create new renders.

003 shows base→2³←exponent and 2·2·2. 004 shows aⁿ=a·a·a·…·a: three explicit factors before the ellipsis, one after. The full-product brace means n factors with n unspecified; it is neither exactly four factors nor an infinite product. Current Javanese SVG geometry preserves the arrow destinations, base/exponent positions, explicit factor order and brace role, while reflowing labels. No standalone clipping/overlap was observed in the inspected previews.

The previews were produced earlier by root using ImageMagick 7.1.2-26 Q16-HDRI with RSVG, density 96, white background and alpha removal; sizes are 940×100 and 480×155. This is renderer-specific standalone evidence, not proof of legibility at the integrated three-column scale.

**Inherited source-track accessibility limits remain explicit:** the unchanged Indonesian 004 alt omits one pre-ellipsis a, as does the English alt. Indonesian alts also describe localized base/exponent labels although the preserved canonical JPEGs print English base/exponent. Current Javanese alts/derivatives correctly match their images, and all three fixed chart speeches reflect actual factor count and label language. The ID source track is intentionally unchanged; its inherited alt inaccuracies must not be mistaken for an approved corrected description.

Current exact asset hashes (paths relative to languages/jv-Latn-ID):

~~~text
translation/assets/a10-exponents/CNX_ElemAlg_Figure_01_02_003_img_new.jpg 5be6626600b25727b5a93b37e1c4cb45a82a3fe9cc1e91b4fc0888b804370ec7
translation/assets/a10-exponents/CNX_ElemAlg_Figure_01_02_003_img_new.jv-academic.svg 3faf45b7e85725c211cd3f319a154347b3143749ed4752e79285f0f7eec324f9
translation/assets/a10-exponents/CNX_ElemAlg_Figure_01_02_003_img_new.jv-conversation.svg 237e927996875182f862213df7d3cf0e9fe99369f4c67947873a7f1cb12eeefa
translation/assets/a10-exponents/CNX_ElemAlg_Figure_01_02_004_img_new.jpg fe978ddd3f9f8cb93b2402be5268888aa0f668ae5c2dd12032c7f16208ec2bbe
translation/assets/a10-exponents/CNX_ElemAlg_Figure_01_02_004_img_new.jv-academic.svg 50ff5a0f927ed9fcc6e8eea2dc40e134c2d3c7645c7d574beb665304f2cbaea8
translation/assets/a10-exponents/CNX_ElemAlg_Figure_01_02_004_img_new.jv-conversation.svg c795b0875286b75157c61136f068d0ec6339973dd87f39622d8a07024c3eb059
~~~

Existing inspected preview hashes (workspace-relative paths):

~~~text
downloads/jv-Latn-ID/qa-render-exponents/003.jv-academic.png 3fea9a4feb20fa5df2738f393a5559b39b4e59e35a06b1f5fb20ea85687e9e1b
downloads/jv-Latn-ID/qa-render-exponents/003.jv-conversation.png cc5dfb698322e05e3636d1dfcbff34fe6ab1e7c6e5d1f8e07128a48e55e8c4fe
downloads/jv-Latn-ID/qa-render-exponents/004.jv-academic.png 92c4b3113640560e8499543e3f17583ad9afc181f19171e1ccf813db17442f9d
downloads/jv-Latn-ID/qa-render-exponents/004.jv-conversation.png 0de3de9b72cff7f2992e3c44e940a8c7b4e336ffd5a6ab92a13c88a64973fa1f
~~~

At this independent QA stage reopened/read complete actual readable canon C21 ping, C34 rambang, C02 cacah, C17 rolas, C07 lima, C19 atus, C18 likur, C26 wolu, C27 sanga, plus kiwa and tengen. The math sense of rambang explicitly concerns power/equal factors and is distinct from its water/weaving homonyms. Its flattened dictionary example 43 is not a MathML witness or the number forty-three. Ping's multiplication family supports ping-pingan; cacah is the count sense, not chopping. Current salawé, rolas and number/direction components agree with the selected entries.

Retaining pangkat instead of the attested alternative rambang is a disclosed provisional continuity choice. Basis/eksponen, kuadrat/kubik, the whole technical compounds and auditory pungkasan pangkat / akhir pangkat markers remain provisional school/prosody choices. Neither dictionary labels nor productive number formation certify register naturalness or native pronunciation.

Readable canon hashes at this actual consultation (files under downloads/jv-Latn-ID/canon/):

~~~text
ping.txt e1442bf2e7d8f24ed3dc6d09b8fe78e0fd4fc692b65c482fdcce84cdc06f49bf
rambang.txt a45727af8975350e044d15deff91892693b03a47f545e6f14d75182b9cf13bdc
cacah.txt 5379ae45ba8dceb9f036cadd40b1c707c6a574a7202f3b0f9695e3fcd69b9d00
rolas.txt 36939ac858e21fb25f407b1aaf935cd76d2eb953f6ef3c76e29b895f2bfc506c
lima.txt 3ed3c9e246682760330b56c4ab7c8aa3517e00844f5761fcca7c2bc0a499fd20
atus.txt ad13869146a75a42a356ca054a32241e0332295d3febe3f6d03ac4c3d2019503
likur.txt cfee06c5fe1fd98d4aa6ab6dc54b575cd142ead86201269ede70f3dda5403a7b
wolu.txt 0a6fadd19095297247cb2c9f36adcaa6230a218832213ee6d83865ede4d888db
sanga.txt 79a2038be9794c92b05f3d6dbf88a67465eabdd3c99a3a6f2dc27985d4d6529e
kiwa.txt 196359730d6dd9735788cd060b3e1b4731c9e6d593fc81ee36e4309cd11f52e3
tengen.txt 4697a749a57b7443e01f5118ba603c5ea7101ad55df78dfbfbb3c66c3f9e8986
~~~

## Tests and previous-output regression

Ran python -B -m unittest discover -s languages/jv-Latn-ID/scripts -p 'test_*.py'. Final post-fix result: **154 tests passed in 35.867 seconds, none skipped**. This includes 11 exponent workflow tests and three exponent asset tests, the earlier shared/other-unit suites and four pure source-portability tests. No source preparation/acquisition CLI or production-writing build command ran.

Read the exact source/target binding, finite semantic/readout check and new direct-helper regression implementation. Independent source/DOM/SSML checks and the 204 additional probes above supplement the suite; they do not merely repeat receipt claims.

All nine previously reviewed CNXML/transcript/SSML packages (81 files) match accepted FIFTH_CHECKPOINT_REVIEW.md hashes, and its eight reader hashes remain unchanged. The writing addition's nine CNXML/transcript/SSML files, reader, edits and asset manifest (12 files) match WRITING_CHECKPOINT_REVIEW.md. Therefore the ten earlier units' **90 content files plus nine readers** are unchanged at this snapshot. In-memory deterministic product checks also agree with existing saved products.

Each package digest below is SHA-256 of UTF-8 json.dumps(mapping, sort_keys=True, separators=(',', ':')), where mapping contains the nine sorted language-relative CNXML/MD/SSML paths and each file's SHA-256:

~~~text
a00-place-value c37aacd8ae48fbb335c735e1aeca71cffa51569b5d56ce9da5be92275f7b5091
a00-digit-place 3b8ea9dac6e5dc89906e7d937bc04e3afbdf4445b390ffa3360edcb7d0c0d9b0
a00-name-whole 0e2c225fc6c4c1ae9e823d59f1677f14dbb53f3fbb34241489c0c165a98641d5
a00-write-whole 576ac9788224fb4e4536faff7834a5c5b1a2f0f51f93beae7abd0f6151651b28
a10-operation-symbols 638f44fd88054e6970c601fbe6103a53bb8728aa8a6dbfe495475e5bd1fd98fb
a10-equality-symbols bb9a60b996af50ef31141746978264010a7e5db2ba8aa9a02b89fcecc53ce664
a10-grouping-symbols 6494813f949f8f83a0fad93f702d2f1597fcb284bb0e44ea901a8067fed2df44
a10-expressions-equations 200cee55f7471785a9b4c6737c29a030e7cd4b6d958540e8e4ec35a3413c69d0
a00-number-sense 3660fb19a3c3f6a952671800110b77f38cfe90d4da85bdff1a4139febca2637c
a10-variable-bridge fc130ff56a48e80ea349b9091991b6015b254781bc47045112062ee9ea3e6a3f
~~~

Independently counted current actual output files: 11 units, 10 readers, 33 CNXML, 33 transcripts, 33 SSML, and 221 source MathML expressions. These counts do not claim whole-module completion.

## Final actual current snapshot

All paths below are relative to languages/jv-Latn-ID. Hashes were read from actual final bytes after root's helper fix and this review's final suite; build-receipt output/rule/asset/draft-receipt hashes were independently matched against current files.

~~~text
audio/a10-exponents.rules.json c32821a7521853fb01eb1a55008fac9f53d1087a625ba7296e4e7a82159af436
translation/a10-exponents.edits.json 6d6348f558bfe5622511a978b148e8786e87df0a478465e7dff0b49fe358903a
translation/a10-exponents.assets.json f7a419b2c6a467a517fced8b7d3444dfb7ab19f87c3f79b27a49931ed95bb590
qa/a10-exponents.build-receipt.json 8abbd6b5301adfaae6e67a6b607f8595ef829e5e74ce11dd2ade5b75fef89e79
qa/a10-exponents.draft-receipt.json cdc82f3c5f2fc26b4cfed52bb029080c2ce60064c314a139e074ba8978077fe4
review/units/a10-exponents.html ccf193a0715efdf9cf8c9ef6e5cefcb74e37c159b4c6f050bd8232913061efbf
provenance/a10-exponents.en.cnxml b673f7f1e24ceb403da1ddccf59b82be388c6f99c44e8f4152cafd9c74f54380
translation/phrases.json adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8
sources.lock.json 27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb
scripts/build_units.py e697f0e6b86a982758d7574f7d1679b3a4140a7288a2cfef0626ad3a7696eaf6
scripts/exponent_checks.py fd12547f04e60be89310e24d7c04cea4b7212514a7f6a28656efba016515183a
scripts/test_exponent_workflow.py 19a5cb9db3c0afab094c04f61b690ba8672ac66ff901787abf3f53dcd03277e7
scripts/prepare_exponent_assets.py dcd2712bc60c3ea6ea57bba3360b330c6f11f6d65edaf2fe1677dda23cbaf8e2
scripts/test_exponent_assets.py f8579453196fe00ac48a664d830cf310e2e63f25b3206a5b72d9b2d6e7d64f39
scripts/build.py ede40277468549b3bbf9128c1c7258626eca1e3bdb8b4bf468336057c477302d
scripts/draft_units.py 90037ee09024fa5daefda5900ae57df6ac0670335be1b41185b2b6daa3a2b859
translation/a10-exponents.jv-academic.cnxml da0b0642f1147943c6b9ea94b3bfa14a9f0f5393584fc8749bcaa5f673d7d019
translation/a10-exponents.jv-conversation.cnxml a2fc07c34ac246d1808597f377fb5d5824a27bcdfea6ce15ef280ac394b71587
translation/a10-exponents.id-academic.cnxml 12e1b68686e999720dd090017314aa9a33e0a110edc2d3a6d200e417027b856b
review/audio/a10-exponents.jv-academic.md ada16a364fa11ba5ee48be7dcf72b80d0991632a2871329ba3845e7379ae089e
review/audio/a10-exponents.jv-academic.ssml 5a8cabbf51d21b28a54de80f09d5933edf58a9c3ce795db022ba05bd2f9d68b5
review/audio/a10-exponents.jv-conversation.md 4b87a1b8cb7f87612eda2b3dfc07d92b95e428e1a2809e82610debef7b3f9208
review/audio/a10-exponents.jv-conversation.ssml 8d7da7d8a1931c448c29db70877f3dc3e7ed8b163dde8ce631c8161a39cbeb6f
review/audio/a10-exponents.id-academic.md 4545053916405604b0365e1c0877656b544888bbc85b9e8e4810c0b3cb9ceb0d
review/audio/a10-exponents.id-academic.ssml d9238789a1de8c1a87cab9c12d14db9ab6ff3332a6a62b32a00b54e9b86b3ef5
~~~

Historical text/rule/asset-stage pending-integration statements are explicitly superseded for production status by the DRAFT producer follow-up, current saved artifacts and build receipt. The old stage metadata is not evidence that the present reader/SSML are absent, and the current build is not evidence of human approval.

Full assignment status remains 0 complete modules / 2 partial / 155 untranslated at the parent checkpoint. Human/native educator/register review, integrated browser/visual/screen-reader review, voice selection, synthesis and listening remain pending. Synthesized audio and human/listening approvals remain zero. The entire A00/A10/AX-2 workflow continues.
