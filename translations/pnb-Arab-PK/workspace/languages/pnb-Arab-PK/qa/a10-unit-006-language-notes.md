# A10-006 language and source decisions

## Status and boundary

Input freeze, 2026-08-31: source study, full draft, canon-guided revision and pre-render source/language checks are complete. Reader construction, independent rendered QA, browser review and native-speaker/educator review are separate pending stages. This is not completion of m82453, A10 or the five-work assignment.

Canonical collection col31130, *Elementary Algebra 2e*, has 82 modules. m82453 is its fourth module, after m82452. This checkpoint includes the complete original document title and metadata (content-id, title, five-objective abstract, UUID), opening note fs-id1170654939047 with paragraph fs-id1170654883472, and the complete 53-child section fs-id1170655150800, “Use Variables and Algebraic Symbols.” The section's final direct child is Try It fs-id1170655102894; the last retained descendant is answer paragraph fs-id1170655114560. Stop before section fs-id1170654953465, “Simplify Expressions Using the Order of Operations.” No intermediate content was skipped.

The source contains five objectives for the whole module. Translating those objectives here does not mean the later instructional sections have been translated. The five remaining instructional/review sections, required 102-exercise Section Exercises subtree and trailing 10-definition glossary remain required; then the collection continues to m82454.

## Frozen identity

- Canonical: `downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82453/index.cnxml`, 184,248 bytes, SHA256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`; pinned commit `38cae454e644abf9f0a623e876994553881597c9`, Git blob `b754c49c00681fac8192f4254d947d54661d1132`.
- Indonesian comparison: `downloads/extracted/A10/translated/modules/m82453/index.cnxml`, 186,219 bytes, SHA256 `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635`, locked v1.0.2. Comparison is not authority to silently repair canonical content.
- Collection: `downloads/complete-upstream/osbooks-prealgebra-bundle/collections/elementary-algebra-2e.collection.xml`, SHA256 `5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72`.
- Excerpt: `source-excerpts/a10-unit-006.cnxml`, 42,942 bytes, SHA256 `06de5c8499a6373d89808e46dc75ac812cf011c91ee484c74bab2be587e7141e`.
- Translation: `translations/a10-unit-006.json`, 59,916 bytes, SHA256 `8e0f30ee8daa8d6e5926bea69ca54df886c438fff75a556d3fb31601b9208aa2`.
- Manifest: `source-excerpts/manifest-a10-006.json`, 118,777 bytes, SHA256 `d3620b63161ce7cd12cd26ef6ffe4d7c27fdc6b72043a3b04b90c2a5ba3d9c63`.
- Scope plan: `plans/A10-006-scope.json`, 51,637 bytes, SHA256 `60fd1dba786936695f12f3e3b48d8152f9c872b406a5456c060a6f7486b11764`.

The excerpt preserves exact canonical prefix bytes [0,42893), apart from the declared generated root ID and closing tags. Individual title, metadata, prelude and section byte witnesses are in the manifest. The selected expanded XML tree, including text, tails, attributes and empty nodes, was compared with a copy of the canonical selection. Original root attributes are empty; metadata content-id is m82453 and UUID is `7c6afafa-02d2-4a6b-8aa7-26905730d112`.

## Actual canon consultation

The actual readable English and Indonesian first section were read, not inferred from titles or memories. The indexed C01–C12 Shahmukhi passages were displayed by `scripts/read_canon.py` at source study, draft, revision and pre-render QA. The canonical index and relevant R1/R2/R3 plain text are readable born-digital prose; no OCR claim is made.

| Stage | Actual receipt under canon/receipts | SHA256 |
| --- | --- | --- |
| Source study | A10-006-next-unit-20260831T153830867915Z.json | 2e23067e21452bba4c4cbe0a0685f9624dd821e2546401b9016cc6c9955d9f85 |
| Draft | A10-006-draft-20260831T160340088615Z.json | 249a1b243e276fbaeb76249fad10e608d61c60a599c8e5e29380731b389d172a |
| Revision | A10-006-revision-20260831T162228757267Z.json | b2d03326de9eeb9064dd20117d58ace00ef2d1d5707e05939f909b6f05594e31 |
| Pre-render QA | A10-006-qa-20260831T163307978573Z.json | b83d4d11e03db8c54af024389e1c8f45f74caa7828a4003ca04baf9089b99d5a |

The receipt generator's legacy “application” strings still mention earlier PNB units. They are not evidence that this unit applied those earlier mathematical claims. Actual A10-006 influences were:

- C01/C02: Punjabi ability and reader-directed instructions, including سکدی اے and سکوگے, rather than replacing Punjabi syntax with Urdu.
- C03/C04: orderly explanation of operations and plural agreement for ages, values and variables. The Greg/Alex ages are exactly source examples; no birth date or identity was invented.
- C05/C06: purpose and alternative-notation clauses in the original English bridge. Purpose تاں جے is not logical equivalence.
- C07/C08: number/unit and location phrasing. C08's currency story was a grammar example, not evidence for the algebra's ages or any conversion.
- C09/C10: reminders and clearly separated qualification of source ambiguities.
- C11/C12: reason-giving and topic transitions in the worked prose and original scaffolding.

This is 12 reading loci in three essays by one author, not 12 mathematical textbooks. C05/C06 share one passage. These readings guide prose grammar and register, not specialist terminology, truth of source mathematics or native-speaker certification.

A topic-specific search for Shahmukhi exponent/base/power usage was actually attempted; its bounded record is `canon/receipts/a10-unit-006-terminology-search.json`, SHA256 `2899397a484a667dfe6bf8fdced862352ce7703d32167ebfdf287ce0fb5cab43`. No readable, topic-matched primary mathematical attestation was adopted. Three DSAL dictionary query opens failed with non-retryable errors; no entry is claimed read. Unrelated Urdu/Persian/Gurmukhi hits and an unverified automated PDF extraction were not admitted. No new bulk download or PDF/OCR authority was invented. The failure to find a useful term here is not a claim that Punjabi mathematical sources do not exist.

## Language decisions and actual revision

The source-bound Punjabi prose is distinct from original bridge sections and source-derived English echoes. Terms متغیر, مستقل, جبری عبارت and مساوات follow the existing local working register. حسابی عمل, جمع, تفریق, ضرب, تقسیم, جوڑ, فرق, ضرب دا حاصل, ونڈ دا حاصل, ونڈیا جان والا عدد and ونڈن والا عدد are explicit contextual choices. نابرابری has an Urdu bridge عدم مساوات. بنیاد, طاقت, طاقت والی لکھت, کھول کے لکھی صورت, مربع, مکعب and the shape-based قوساں descriptions remain provisional, not claims of a certified Shahmukhi standard. The original base/exponent explanation distinguishes the roles even where طاقت serves more than one English reading. Metadata's ہم جنس اجزا names a later topic, not instruction already covered.

Revision after the actual canon reading corrected spacing/spelling جان دے → جاندے, a ہووو typo, and تین → تِن in source-bound prose. It retained all seven no-emphasis source terms as no-emphasis, simplified the agreement in the expression definition, and recast the equation definition in Punjabi word order. The source text “3xy” is one LTR unit with italic xy, not separately isolated pieces that could reorder. Source alt003's numeric 2 remains a digit where the canonical alt uses a digit, allowing exact ordered prose-numeral comparison. Reference ordinals 1.2.1–1.2.3 are LTR isolated.

All 98 canonical MathML trees are unchanged. Target clauses were reordered so source terminal formula periods end their clauses without relocating/deleting MathML punctuation. In particular the first multiplication-table formula's trailing comma separates notation forms; it must not be treated as disposable sentence punctuation. There is no authorized MathML text-edit ledger for this unit.

## Source differences and separately labeled qualifications

1. **Operations-table summary.** Canonical summary at fs-id1170655178881/summary lists operations in an order that conflicts with its cells and describes four multiplication forms where five are present: a·b, ab, (a)(b), (a)b, a(b). It also misdescribes a parentheses form. Indonesian repairs this summary. The faithful source-bound target retains the canonical statement. A separately declared original accessible summary, derived from actual cells, replaces the announcement while the faithful value remains in data-source-summary. Visible and accessible advisory destinations must be a10-006-operations-summary.

2. **Exponent factors versus operations.** Canonical “multiply by itself n times” and “multiply 2 nine times” are ambiguous about factors versus binary multiplications. Indonesian explicitly adds positive-integer n and n equal factors. The faithful translation preserves the canonical wording. Original a10-006-exponent-count explains positive-integer n as n equal factors and n−1 binary multiplications: 2³ has three factors and two binary multiplications; 2⁹ has nine factors and eight. This does not define zero, negative or fractional exponents. Original image003 alt disambiguates the same pixels while retaining data-source-alt. Generic image004's source alt wording remains traceable, with the visible correction/key link.

3. **English ordinal MathML.** Owners fs-id1170655228836 and fs-id1170654937018 contain n with superscript t,h. Indonesian changes these to n. The canonical trees remain exact. Original a10-006-ordinal explains the English ordinal “nth”; it is not algebraic n raised to th or multiplication t·h.

4. **English MathML text.** Owners fs-id1167270244162, fs-id1167269909313 and fs-id1167269979347 retain English mtext (inequality and parentheses/brackets/braces wording). The original bilingual key a10-006-math-english supplies Punjabi readings. The English and Indonesian have 98 trees each; only zero-based indexes 22,23,43,77,79 differ, corresponding to these three text displays and the two ordinal trees.

5. **English inflection.** At fs-id1170655151082 the canonical term variable is followed by a separately bold s; Indonesian empties the emphasis. The target has Punjabi متغیر plus parenthetical retained English variable<strong>s</strong>, with only the English suffix bold. Original a10-006-inflection explains why the s is kept; it is not attached to the Punjabi term.

6. **English teaching context.** Source instructions still request English, not Punjabi or Indonesian. Exactly 36 declared source keys receive separately identified, source-derived English lexical echoes. These are the original words, not additional invented answers. Only the worked answer fs-id1166424795899 contains MathML among those echo owners: its four repeated formulas are omitted from the lexical echo alone and remain completely displayed in the source-bound translation. The original explanation a10-006-english-context states this. Echoes must retain English text/emphasis/newlines/part order but never duplicate source IDs or mathematical trees.

7. **Grammar analogy.** Original a10-006-grammar-analogy qualifies the source phrase/sentence analogy: some phrases contain verb forms, including the source's “Running very fast,” and an equation need not be true for all values.

8. **Multiplication cross.** Source's categorical statement about not using × in algebra is retained; a10-006-cross limits the pedagogical reason to avoiding confusion with variable x here, not a universal mathematical prohibition.

9. **Operand order and division.** Source subtraction wording “subtract 9 and 2” is awkward, but its 9−2 fixes the order. Original a10-006-operands explicitly says subtract 2 from 9, keeps subtraction/division ordered, and states that a divisor or denominator is nonzero. It does not silently rewrite source claims.

Source alt003's “superscipted” typo was translated by meaning rather than manufacturing a Punjabi spelling error. Source alt002's “numbered line” was read against its actual labeled a/b pixels; no numerical ticks were invented. All source originals remain frozen in the witness and manifest.

## Images actually inspected

The four original JPEGs were viewed at original detail during source study. Images003/004 were re-read visually during revision; images001/002 were re-read at pre-render QA. No claim is made that every image was re-inspected at every stage.

- 001: 192×37, 14,959 bytes; a is the left tick and b the right tick on a double-ended line. No numeric origin/tick values were assumed.
- 002: 192×37, 15,798 bytes; b is left of a. It must not be mirrored for RTL.
- 003: 541×44, 33,650 bytes; base/exponent arrows point to 2/3 and the graphic shows 2·2·2 beside its ambiguous English “three times” wording.
- 004: 209×93, 38,920 bytes; base/exponent arrows point to a/n, and the repeated product has an “n factors” underbrace.

All filenames, byte/hash/blob pins, dimensions, source MIME attributes and authority-row identities are in the manifest. Total admitted image payload is 103,327 bytes. No images were copied at input freeze. Scoped preparation may copy these four original bytes only. There are no source figure wrappers and no new figure numbers should be invented.

Existing A10 notice/license logical-LF hashes and component restrictions remain binding. Media authority rows establish identity, not permission. Absence of an individual image credit is not new clearance. No repeat supply/license audit was performed. Correct work attribution is OpenStax Elementary Algebra 2e by Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis; CC BY-NC-SA 4.0 is subject to component-specific credits/restrictions and nonendorsement. Do not inherit A30 authors or a generic CC BY claim.

## Pre-render checks and renderer obligations

The selected XML has 1,243 elements and 134 original IDs. The 187 keys comprise 55 paragraphs, 14 titles, nine list items, four alts, eight table summaries and 97 cells, including one whitespace-only cell. It contains 98 MathML trees/737 MathML nodes: 94 inline placeholders and four automatic equation owners. All 14 terms, five bold emphases, 89 italics, 48 circled part labels, 12 newlines and three source links were matched. All 128 source prose-numeral occurrences retain exact per-key order. No Gurmukhi, prohibited bidi controls or unresolved draft fragments were found; target HTML fragments parsed.

Eight CNXML tables have 41 rows, 97 cells, 15 actual thead cells and 15 colspecs. Only those actual thead cells become headers; eip-10/eip-958 have none. Source layout stays LTR, Punjabi prose RTL, with local overflow and a readable initial column. The 48 part labels split into 32 short groups across 12 paragraphs, 12 labels in three wrapping long-answer paragraphs, and four table labels that must not be wrapped as paragraph groups. The long owners are fs-id1166424795899, fs-id1170655353526 and fs-id1170655222902. The first has ten source newlines; two other paragraphs contain one newline each. Preserve blank cells, empty equation labels and every empty MathML mtr/mtd/mrow.

All nine exercises retain their own source problems and solutions: three worked examples and six Try It notes. Exactly three source Solution titles must render once. Five-power/one-power/seven-square/zero-power Try It numerical results were independently recomputed as 125,1,49,0, and worked 3⁴ as 81. Greg/Alex numeric rows were checked as 12→15,20→23,35→38, all +3. Inequality wording and expression/equation classifications were read against source; variable inequalities are not being asserted universally true.

These are input-stage checks, not evidence that a browser or screen reader has rendered correctly. The isolated QA must independently bind source hierarchy, text/tails, every mathematical owner, English echoes, images, corrections, table geometry, metadata, UI frame, attribution and exact artifact hashes, and reject detached mutations. Native idiom, specialist register, educational adequacy and assistive-technology behavior remain open review needs. No native-speaker certification is available.

