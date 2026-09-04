# PNB-002 language and source notes

Date: 2026-08-30. Draft language: Western Punjabi in Shahmukhi (`pnb-Arab-PK`). Native-speaker/educator review is pending; this is not certified idiomatic or publication-ready Punjabi.

## Exact scope and schema

Only `Example_01_01_01` from OpenStax module `m49301` is translated. The authoritative prose witness read was `downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml`, at the project-pinned commit `789b54099106b071d1d32bfcee454fed72eb4768`. The Indonesian comparison read was `downloads/extracted/A30/repo/source/modules/m49301/index.cnxml`. No following example is included.

The JSON has string fields `locale`, `unit`, `title`, `subtitle`, and `bridge_after_html`, plus the object `source_blocks`. Its 11 source-block values are strings: one problem title, one introductory paragraph, two question list items, three media alt descriptions, two solution list items, and two nested solution paragraphs. `title` is a local reader title; the source title is separately translated at `fs-id1165137559269/title`.

Each of the two solution-item strings contains `{{link:0}}`, then `{{child:0}}` for its immediate figure and `{{child:1}}` for its immediate paragraph. The introductory paragraph also contains `{{link:0}}`. The renderer retains source element IDs, link destinations, list and item order, and figures `Figure_01_01_004`, `Figure_01_01_027`, `Figure_01_01_028`. It resolves those figure links to local numbers 1.1.2, 1.1.3, 1.1.4. Explicit LTR-isolated `(a)` and `(b)` appear in the question and solution items. No source MathML occurs in this example.

`bridge_after_html` is original support, not source translation. Its heading, introductory sentence, and `data-origin="original-bridge"` mark this separation. It provides the six English-to-Punjabi menu-label mappings, unchanged source prices, the US-dollar explanation, and a short direction-of-association reminder. It does not add practice or translate later material.

## Actual canon consultation

The canon index `languages/pnb-Arab-PK/canon/examples.json` was read, followed by the listed local source passages. The three essays are a narrow prose-register reference, not mathematical vocabulary authority. Only short loci are identified here; no essay text is republished. No shared canon receipt file was overwritten and `read_canon.py` was not run.

Before drafting, the actual passages were read with surrounding lines: R1 lines 26–30 (C01), 33–37 (C04), 43–47 (C03); R2 lines 27–31 (C08) and 31–35 (C07); R3 lines 34–40 (C12/C11) and 42–46 (another occurrence of the C11 construction). Decisions from this reading:

- C01/R1, ability constructions: retain Punjabi `سکدیاں نیں` in the plural output statement, not Urdu auxiliary grammar. The literary passage is evidence for the construction, not the menu's mathematical claim.
- C04/R1, number and agreement: use `چیزاں`, `قیمتاں`, `قدراں`, and Punjabi plural auxiliaries. Singular `قیمت` in the two-items/same-price sentence agrees with `اِکّو اے`.
- C03/R1 and C07/R2 were read as the next-unit marker requested. Ordered-pair terminology is not needed here, so neither locus is claimed as authority for a new menu term. C07's location construction supports the ordinary `مینو اُتے` phrasing only.
- C08/R2: the actual hundred-rupee/hundred-day price-story context was read. It supports readable amount/unit prose, not currency conversion. The source's `$1.49` and `$1.99` remain dollars with decimal points. Indonesian `$1,49`/`$1,99` are comparison variants, not adopted values or formatting.
- C11/R3: the reason-giving construction informs `کیوں جے` in the original direction reminder. Source conclusions use `ایس لئی` to retain the English therefore/so relationship.
- C12/R3: the explicit topic transition informed the reader-directed start `آؤ ... شروع کریے`; this is an adaptation of prose register, not a quotation or claim that the exact sentence appears in the essay.

During revision of the composed draft, R1 lines 26–35, R2 lines 28–34, and R3 lines 36–38 were reread. This checked ability/plural agreement (C01/C04), item-price language (C08), location phrasing (C07), and transition/reasoning (C12/C11). The final wording keeps the direct Punjabi `جے اسیں ... من لئیے، تاں ...` construction and distinguishes monetary `قیمت` from general numerical `قدر` consistently with the existing terminology ledger.

## Translation decisions and limits

- `چیز` / `چیزاں` renders menu item(s) as ordinary Punjabi. The previous unit's final original preview used `شے`; this unit chooses the more transparent plural `چیزاں` without changing mathematical meaning. No claim of a newly established technical term is made.
- Accessible existing loans `مینو`, `ڈونٹ`, `جیلی`, `چاکلیٹ`, `فنکشن`, `اِن پُٹ`, and `آؤٹ پُٹ` are retained. Their spelling and the title compound `قیمت فہرستاں` remain subject to a Pakistani Punjabi educator's idiomaticity review. The prose does not substitute Urdu clauses or Gurmukhi text for Punjabi.
- `fs-id1165137436464` is split into two Punjabi sentences: the figure location, then the menu's contents. Both source facts and the original link destination remain. English `See [figure].` becomes `{{link:0}} ویکھو۔`, moving the imperative after its object as Punjabi syntax requires.
- The decisive direction is not reversed: item-to-price is a function; price-to-item is not, because the price shared by jelly and chocolate donuts permits two outputs. `اک توں ودھ` preserves “more than one”; it is not weakened to merely “an output.”
- The English source's final sentence reads “the item is a not a function of price.” Punjabi conveys the intended negative proposition without reproducing the accidental extra article; this copy-edit is disclosed here and does not change the frozen source witness.
- Figures 004/027 retain the faithful, identical Punjabi equivalents of their identical source alt descriptions. Figure 028's alt preserves the source's price-to-donut direction. English figure labels themselves are not replaced. Alt attributes are plain text, so the price strings there cannot contain HTML isolation markup; the visible original legend isolates all dollar amounts and English labels using `bdi dir="ltr"`.
- The source token glyphs are circled letters; the displayed labels use explicit `(a)`/`(b)` as agreed with the renderer. Source list order and the two question/solution correspondences must be checked in rendered QA.

## Image inspection

All three existing upstream JPG files were opened. Each is 584 × 281 pixels. The default image preview of Figure 027 initially showed only a border corner; reopening it with `detail="original"` showed the full menu. Read-only dimension and hash checks did not show corruption. Figure 027 in the full upstream tree and Indonesian comparison have the same SHA-256: `2c702c8fdd9dd83ccaa8d8b7f69048b4881fc143218551a7ec0faf6fff212b30`. No image editing, reconstruction, replacement, download, bulk copy, or extraction was done by this drafting pass.

## QA status

Final linguistic QA reread the whole saved JSON, then R1 lines 28 and 35 (C01/C04), R2 lines 29 and 33 (C08/C07), and R3 lines 36 and 38 (C12/C11). The comparison confirmed Punjabi auxiliary agreement, the unchanged price story, explicit association direction, and source/addition separation. No new specialized mathematical term was introduced or claimed to be canon-certified.

A read-only PowerShell check derived the expected text-bearing keys directly from the actual English example. Results: 11 source blocks, zero missing keys, zero extra keys, three link placeholders, four child placeholders, zero Gurmukhi or forbidden bidi-control codepoints. The JSON and each HTML-bearing source fragment, plus the entire original bridge section, parsed successfully. The forbidden decimal-comma dollar-price patterns were absent. No QA result file or shared receipt was overwritten by this check.

Reader build, link-resolution validation, original-media preservation checks, desktop/mobile visual QA, and educator review are separate responsibilities; this drafting note does not claim they have passed. Alt-text assistive-technology pronunciation, naturalness of `قیمت فہرستاں`, and culinary-loan spellings still need target-language review.

## Parent revision after draft handoff

The parent reread C01/C07/C08/C11 at revision (timestamped PNB-002 receipt) and replaced the compact title compound `قیمت فہرستاں` with the explicit genitive phrase `مینو وچ دِتیاں قیمتاں دیاں فہرستاں`. The earlier compound remains above as historical drafting evidence, not the current reader wording. The menu relationships and amounts are unchanged. The source image preview anomaly was resolved by original-detail viewing; no asset replacement was needed.
