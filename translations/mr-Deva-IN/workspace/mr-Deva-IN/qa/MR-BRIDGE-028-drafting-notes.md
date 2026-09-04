# MR-BRIDGE-028 drafting record

2026-09-02. Writer: `mr028_writer`. Status: source-faithful Marathi draft of the complete short A20:m81427 method-choice section; not frozen, built, rendered, independently reviewed, teacher-approved, published, or a module/chapter/book-completion claim. This worker owns only the 028 XML, config and this record. Root owns freeze/provenance, independent review, build/render QA, shared ledgers, staging and release.

## Controlling files and repository-path discrepancy

Before source work, read `AGENTS.md` and `USER_INSTRUCTIONS_VERBATIM.md` completely, then `mr-Deva-IN/GOAL.md`, `WORKFLOW.md`, all of `DECISIONS.md`, all of `canon/CONSULTATIONS.md`, and the adjacent 025/026 XML/config/drafting patterns. The requested `mr-Deva-IN/canon/TERMINOLOGY.md` does not exist in this checkout (`rg --files` found none); the actual 45-row ledger is `mr-Deva-IN/terminology.csv`, which was read completely. No missing file was invented and no shared canon/ledger was edited.

## Pinned sources, full-wrapper reading and exact boundary

Both complete module members and the complete selected wrapper subtrees were read directly from the pinned ZIP archives in memory, not from isolated provenance fragments. No archive was extracted or modified.

|Source|Archive bytes / SHA-256|Exact module member|Module bytes / SHA-256|
|---|---|---|---|
|EN|537455794 / `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917`|`osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81427/index.cnxml`|166406 / `2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5`|
|ID|106658915 / `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7`|`source/modules/m81427/index.cnxml`|168909 / `2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112`|

Both modules identify content-id `m81427` and UUID `b9f8475e-9490-4f24-995f-2923b1ed9644`. The selected wrapper is `fs-id1167826783829`, EN “Choose the Most Convenient Method to Solve a System of Linear Equations”, ID “Memilih Metode yang Paling Praktis untuk Menyelesaikan Sistem Persamaan Linear”. The exact five direct non-title selectors are, in order:

```text
para     fs-id1167826783834
equation fs-id1171792628785 class=unnumbered
example  fs-id1167834525591
note     fs-id1167835360932 class=try
note     fs-id1167826798760 class=try
```

The wrapper intentionally has no target `data-source`; only those five direct selectors carry exact `A20:m81427#ID` labels. The next sibling is `fs-id1167835378580`, EN “Key Concepts”, ID “Konsep Kunci”, and is absent from the target.

Per locale, the complete wrapper has exactly 299 elements, 29 unique IDs, nine MathML nodes, three exercises, three supplied solutions and six method-choice subparts. It has zero media, images, links and CNXML tables. The nested first MathML guide has 2 `mtable`, 7 `mtr` and 37 `mtd`; the eight system MathML nodes add 8/16/16, giving exact totals 10/23/53. The guide is therefore preserved as a semantic three-column target table, not flattened into a sentence.

## Source content, choices and independent recomputation

The source asks only which method is more convenient and why. Its six supplied choices are preserved without adding coordinates to the learner-facing answers:

|Item|Supplied method and reason|Independent review-only solution|
|---|---|---|
|Example ⓐ|Elimination; both equations are in standard form|`(−24/17, 94/17)`|
|Example ⓑ|Substitution; one equation is solved for `y`|`(2, 1/3)`|
|Try 1 ⓐ|Elimination; both equations are in standard form|`(−3, 4)`|
|Try 1 ⓑ|Substitution; one equation is solved for `x`|`(−9, −4)`|
|Try 2 ⓐ|Substitution; one equation is solved for `y`|`(2, 3)`|
|Try 2 ⓑ|Elimination; both equations are in standard form|`(29/24, −19/8)`|

Manual exact checks: example ⓐ gives `17x=−24`, then `8y=752/17`; example ⓑ gives `9x=18`; Try 1 ⓐ gives `23x=−69`; Try 1 ⓑ gives `y=−4`; Try 2 ⓐ gives `−5x=−10`; Try 2 ⓑ reduces to `3x−y=6` and then `8y=−19`. Every listed pair satisfies both equations. These coordinates are review evidence only and do not occur in the XML as supplied answers.

## EN/ID discrepancies and naturalization

- EN `fs-id1167826783834` contains the duplicate phrase “in in an application”. Marathi expresses the application context once; this is a disclosed cleanup, not dropped content.
- EN Try prompts `fs-id1167835331536` and `fs-id1167826857362` omit the comma after “linear equations”. Marathi punctuation is naturalized only; the propositions and task are unchanged.
- ID makes the final method advice in `fs-id1167826783834` directly imperative (`Pilih ...`), whereas EN frames it as what the learner will want to choose. It loses no content. Marathi uses direct but non-abrupt classroom guidance.
- The eight EN/ID system MathML nodes agree in order, signs, coefficients, fractions and constants. The first MathML node differs only because its guide prose is localized; its nested layout shape agrees exactly.

## Stage-specific Marathi canon and new witness use

The following records are actual reads, not a catalog-only claim. The local OCR is used only where readable; the physical pages and selected mathematical sources govern corrupt formulas.

### Selection

- C12: read all of `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt` (2474 bytes, SHA-256 `f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b`), physical page 85 / printed page 75, especially OCR lines 3–17 and 42–43. Opened `pages/balbharati8-85.png` at original detail (255250 bytes, SHA-256 `284d9c7e4dc21f183189750421e65c97acfae02fd642df0457321cfe627a7f69`). It supports `समीकरण`, `उकल`, truth by equality and equal operations; it does not attest the full system/method compounds.
- C13: read all of `balbharati8-86.txt` (1539 bytes, SHA-256 `497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57`), physical page 86 / printed page 76, OCR lines 1–46. Opened `pages/balbharati8-86.png` at original detail (195482 bytes, SHA-256 `87e2c859c7d3445466e28b1050bb86bc52b1014fb6f2dd2c75d356dda620ce49`). Its two displayed ways to solve the fractional equation support the source's premise that more than one valid method can exist; corrupt OCR formulas were not copied.
- C18: read the official Marathi Vishwakosh search-reader text for [आलेख](https://vishwakosh.marathi.gov.in/24316/), exact headings “आलेख”, “जात्याक्ष आलेख” and “आलेख व समीकरणांचे निर्वाह”. The HTML has no stable page/line numbers. It supports `आलेख`, visual depiction and the statement that intersections provide solutions of simultaneous equations; it does not choose between substitution and elimination. Direct page open returned HTTP 502, so no unseen page/image formula is claimed.
- New targeted witness: read IIT Kanpur SATHEE's official educational Marathi search-reader text at [Notes Class 10: दोन चलांतील रेषीय समीकरणांची जोडी](https://sathee.iitk.ac.in/mr/sathee-jee/notes-class-10/maths/pair-of-linear-equations-in-two-variables/), exact HTML headings 3.2, 3.3.1, 3.3.2 and 3.4. It explicitly contrasts graphical, substitution and elimination methods; advises substitution when a variable is easily isolated; advises elimination for manageable coefficients; and uses `आलेखीय पद्धत`, `प्रतिस्थापन पद्धत`, `निर्मूलन पद्धत`, `मानक स्वरूप`. There are no stable page/line numbers. Direct HTTP fetch returned 403; the complete relevant indexed text was readable. It influenced the compact guide and causal answer syntax. Because the adjacent Marathi units use `विलोपन` and `प्रमाणित रूप`, those exact target compounds remain authored/provisional variants rather than falsely claimed attestation.

### Drafting

Immediately before writing the first XML pass, reread both complete C12/C13 OCR files and again read the same bounded C18 and SATHEE headings in fresh official-domain search results. Concrete effects: retain `समीकरण`, `उकल`, `आलेख` and Latin `x,y`; say an equation is “एका चलासाठी ... सोडवलेले”; make every supplied answer explicitly causal (`... असल्यामुळे ... सर्वांत सोयीचे`); and render the guide as three parallel method columns. No shared canon/terminology file was changed and no new locator was claimed.

### Revision

After the complete first XML readback and an ID-by-ID EN→MR leaf-text comparison, reread both complete C12/C13 OCR files. Fresh official-domain search-reader results were then read for C18's exact “आलेख व समीकरणांचे निर्वाह” passage and SATHEE sections 3.2/3.3.1/3.3.2/3.4. The C12/C13 classroom cadence and SATHEE's explicit `... पद्धत वापरा` advice led to four bounded prose improvements: `पद्धत करायला` became the more natural `पद्धत वापरायला`; all three prompts now directly ask whether solving by substitution or by elimination is more convenient; and every supplied explanation now says `प्रतिस्थापन पद्धत` or `विलोपन पद्धत` rather than a bare method name. Source IDs, systems, choices, MathML mapping and scope did not change.

### Final QA

After revision, reread both complete C12/C13 OCR files a fourth time and reopened both physical page PNGs at original detail. Fresh official-domain results were read again for C18's exact simultaneous-equation/intersection passage and the SATHEE method-selection sections. This pass confirmed the explicit `समीकरण`/`उकल` distinction, the multiple-method premise, `आलेख`, and causal `... पद्धत वापरणे सर्वांत सोयीचे` syntax. It made no further target change. Direct C18/SATHEE page-fetch limits remained 502/403 respectively; only actually readable official indexed text is claimed.

The target's new method-comparison witness is adequate for the narrow comparison: SATHEE explicitly discusses graphical, substitution and elimination methods and standard form. It does not, however, attest the exact adjacent-unit variants `विलोपन पद्धत` or `प्रमाणित रूप`. Those complete compounds remain disclosed authored/provisional forms; no shared canon/terminology entry was added or silently promoted.

## Final writer checks and commands

The final read-only check used the standard-library-only command form `@' ... '@ | python -X utf8 -B -`; the inline script did not create a file or modify shared tools. It reparsed the current XML and duplicate-key-checked JSON, streamed both archive hashes, read both module members directly, and asserted:

- LF/NFC UTF-8 with no replacement character, DTD or entity declaration;
- 31 unique target IDs = 29 exact ordered source IDs + `MR-BRIDGE-028` + `credits`;
- exact nearest-source-ID ancestry in EN, ID and target; exact five target `data-source` labels; no wrapper label;
- exact source scope in each locale: 299 elements, 29 unique IDs, 9 MathML, 10 `mtable`, 23 `mtr`, 53 `mtd`, 3 exercises, 3 supplied solutions, 6 problem subparts, and zero media/images/links/CNXML tables;
- exact guide-only 2/7/37 nested MathML structure and exact eight EN/ID system renderings in source order;
- 15 exact target/config `data-check` strings: seven structural guide cells/title plus eight source systems;
- all six rational solutions by determinant arithmetic and substitution in both equations;
- 11 resolving local target links, 4 HTTPS citations, one target semantic guide table, zero target images, no `assets` config, and no next-sibling ID;
- none of the six review-only coordinate strings occurs in the learner-facing XML.

The first version of the final inline checker compared the source MathML serializer's unspaced operator stream to the deliberately spaced accessible target strings and stopped on that formatting-only difference. After printing all eight pairs and confirming identical tokens, the final checker compared only XML-token whitespace-insensitively; the substantive checks then passed. No source, translation, config or mathematical value changed because of that checker repair.

Separate exact-rational verification used `fractions.Fraction` under `python -B -` and printed the six expected pairs with both transformed-equation checks. The initial and final structural checks both passed; the final full result was:

```text
PASS final source/target structure, IDs, ancestry, selectors, MathML, methods, rational checks, links, NFC, no-assets/no-coordinate
ARCHIVE_EN 537455794 effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917
ARCHIVE_ID 106658915 a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7
MODULE_EN 166406 2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5
MODULE_ID 168909 2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112
XML 18168 c36007be214c522bc4279fd629d6a4e12cac485582286f25e2043e67597dc67c
CONFIG 5791 12f4033160764921269ba9f77865abc270d3ac70b6fdbf7def86353f4c81806f
```

Final draft pins (before any root freeze/build mutation):

|File|Bytes|SHA-256|
|---|---:|---|
|`translations/MR-BRIDGE-028.xml`|18168|`c36007be214c522bc4279fd629d6a4e12cac485582286f25e2043e67597dc67c`|
|`units/MR-BRIDGE-028.json`|5791|`12f4033160764921269ba9f77865abc270d3ac70b6fdbf7def86353f4c81806f`|

## Residual limitations and handoff boundary

- This is writer QA, not independent Marathi-language/mathematical review, native-speaker or teacher approval.
- No unit lock/provenance fragments, freeze, asset operation, build, HTML/PDF output, browser/render inspection or release work was performed. Root must freeze and independently review before building.
- The source has no images or links, so no source-image reading was needed. The target's one semantic table is an accessible rendering of nested MathML layout, not a claim that the source contains a CNXML table.
- C18 and SATHEE were readable through official-domain indexed search text, while direct current fetches failed 502/403. Exact HTML heading locators and the limitation are preserved above; no unread image/formula is claimed.
- The requested `canon/TERMINOLOGY.md` path remains absent; the actual `terminology.csv` was used. The exact full compounds `विलोपन पद्धत` and `प्रमाणित रूप` remain authored/provisional despite the readable witness's `निर्मूलन पद्धत` and `मानक स्वरूप` variants.
- The draft stops exactly before `fs-id1167835378580` “Key Concepts” / “Konsep Kunci”. The complete five-book Marathi assignment remains in progress.

No shared ledger/canon/tool/source archive, other unit, output, asset or lock was edited; nothing was staged, committed, pushed, merged or released.
