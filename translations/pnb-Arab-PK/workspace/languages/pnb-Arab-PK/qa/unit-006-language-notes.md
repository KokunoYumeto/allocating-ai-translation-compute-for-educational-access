# PNB-006 — evaluation and solving draft notes

Date: 2026-08-31 local time; canon receipts below use UTC on 2026-08-30. Target: Western Punjabi in Shahmukhi (`pnb-Arab-PK`). This is another checkpoint in the full five-work assignment. No book or module is complete; native-speaker and mathematics-educator approval remain pending.

## Exact scope and source study

Read the actual canonical and Indonesian `m49301/index.cnxml` sources, not a remembered example. Canonical checkout: `downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml`, pinned commit `789b54099106b071d1d32bfcee454fed72eb4768`. Comparison: `downloads/extracted/A30/repo/source/modules/m49301/index.cnxml`.

The next outer section, `fs-id1165137503241`, is “Finding Input and Output Values of a Function.” It contains four nested skills and continues until the following outer section `fs-id1165135422920`. Its full inventory is 139 source IDs, 121 MathML trees, 13 equations, three CNXML tables, four figures/images, seven links, one footnote, three inline terms, and 109 text/alt/cell blocks if the five pet-name data cells are included for translation. That full section is **not** this unit's coverage.

PNB-006 contains exactly the outer section's first four direct children, keeping its original wrapper ID:

1. Outer title, key `fs-id1165137503241/title`.
2. Introductory paragraph `fs-id1165137470651` on evaluation.
3. Introductory paragraph `fs-id1165137735634` on solving for inputs.
4. The complete nested section `fs-id1165137425943`, “Evaluation of Functions in Algebraic Forms.”

The nested section includes its opening formula and how-to; all four parts of `Example_01_01_06`; `Example_01_01_07`; complete Try It `ti_01_01_08`; `Example_01_01_08`, including its graph; and complete Try It `ti_01_01_09`. Its last answer is `fs-id1165135664056`. Stop immediately before next direct child `fs-id1165137591827`, “Evaluating Functions Expressed in Formulas.” This is the next translation cursor, not `fs-id1165135422920`, which follows the entire larger outer section.

Source lines 903–1602 contain the prefix; line 903 first closes preceding sections before opening the selected one. The excerpt was assembled from complete XML children with `apply_patch`, never from a raw line slice. `prepare_text_unit.py` was not run or edited because its existing unit choices and whole-selection assumptions do not cover this prefix. The original outer leading whitespace, all selected child text/tails, attributes, IDs and subtree order are retained. Namespace placement and empty-element serialization can differ without changing the XML tree.

## Witnesses and asset handoff

The manifest records these verified SHA-256 values:

- English CRLF checkout: `f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612`.
- Pinned LF witness `downloads/m49301.cnxml`: `81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3`. Removing only the checkout's 4,801 CR bytes produces this witness exactly.
- Indonesian comparison: `67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a`.
- Frozen `source-excerpts/unit-006.cnxml`: `c68e615f7efec70172a041b51e06b212c8eb25b248073ded8c86cffd7a4af7a3`.
- Checked `translations/unit-006.json`: `0924d31030a7cefb64c186fc9a84c5d054dbf629001dcad17465676ac2fe9ccf`.

The existing canonical image was opened at original detail: `downloads/complete-upstream/osbooks-college-algebra-bundle/media/CNX_Precalc_Figure_01_01_006-5f6f.jpg`. It is 487 × 459 pixels; SHA-256 `af834802492b337155a0056c0d70961f3a003e41df6e571c082ae227241d2675`. The horizontal axis is `p`, the vertical axis is `h(p)`, and the three marked function values are (-3,3), (1,3), (4,24). A small table within the image also shows inputs -3,-2,0,1,4 and outputs 3,0,0,3,24. That is raster content, not a separate CNXML table.

Source figure ID is `Figure_01_01_006`, media ID `fs-id1165135335985`. Its faithful translated alt retains the three source ordered pairs. The original bridge explains the axes and horizontal output-3 line separately. The manifest targets `assets/Figure_01_01_006.jpg` with local label 1.1.6. Parent integration owns copying the unchanged asset and carrying forward the existing component notice. This drafting task neither copied/edited the image nor repeated an asset-rights audit.

## Schema and nested structure

There are 37 ordered source-block strings and 55 retained source IDs. Source mathematics comprises 29 own inline MathML placeholders plus nine equation children, giving 38 MathML trees. There is one source link, one image, eight immediate-child placeholders, and no CNXML table, footnote or inline term in this prefix.

The two source introductory italic terms, “evaluate” and “solve,” are retained through `<em>` around their Punjabi verb phrases. The how-to's source emphasis is rendered with `<strong>`. The two source circled lists preserve four parts each using LTR `(a)` through `(d)`, consistent with earlier units.

All equations nested inside solution list items must remain inside their original item. Parts (a), (b), and (c) each have one `{{child:0}}` equation. Part (d), key `fs-id1165137778273/item/4`, has this exact five-child sequence:

1. Equation `fs-id1165135154122` for the expanded `f(a+h)`.
2. Paragraph `fs-id1165135632109`, “and we know that.”
3. Equation `fs-id1165137471110` for `f(a)`.
4. Paragraph `fs-id1165137767461`, combining/simplifying the results.
5. Equation `fs-id1165137573884`, the difference quotient.

The two paragraphs have their own source-block keys. Their prose must not be duplicated in the parent item or omitted during child replacement. Math counts must exclude these block children from the parent's own inline slots. Equation `fs-id1165137573884` has deeply nested MathML tables and English instructional cells; keeping only flattened text would lose fraction/exponent/layout relationships.

## Actual canon reading

Read the actual surrounding passages through `read_canon.py`, using the existing readable R1/R2/R3 HTML witnesses. No new reference download occurred. Receipts are:

- `canon/receipts/PNB-006-next-unit-20260830T215611224674Z.json`: C01/C02/C03/C04/C05/C06/C09/C10/C11, during source analysis.
- `canon/receipts/PNB-006-draft-20260830T215859773966Z.json`: the same nine loci, before composing the draft.
- `canon/receipts/PNB-006-revision-20260830T220530139132Z.json`: C01/C02/C04/C06/C09/C10/C11, read alongside the complete saved JSON.
- `canon/receipts/PNB-006-qa-20260830T221428282089Z.json`: C01/C02/C03/C04/C09/C10/C11, read against the revised wording before final checks.

Actual influence and limits:

- C01's Punjabi ability/passive construction supports `کڈھی جا سکدی اے` and `کر سکدے آں`; agreement follows this task's subjects, not the essay's specific sentence.
- C02's reader-directed obligation construction supports explicit `رکھو`/`کڈھو` instructions and helped distinguish an instruction/requirement from the opening paragraphs' “want to.” Revision replaced ambiguous `چاہیئے` phrasing there with `چاہندے ہوئیے`; no essay is claimed to attest every inflected form.
- C03's ordinary sequence register supports preserving step order and the existing ordered-pair wording, not a newly certified algebra term.
- C04's plural prose supports `قدراں`, `جواباں`, and Punjabi plural agreement.
- C05/C06 distinguish purpose and alternatives from logical implication. Substituting a value “in place of” a variable is expressed with Punjabi `دی تھاں`; a reason for a result uses `کیوں جے`/`ایس لئی`, not a purpose connective.
- C09's reminder register informed the reminder-like precision notes without forcing the same phrase into every paragraph.
- C10's explicit qualification supports keeping domain, symbolic-value and omitted-condition explanations visibly separate from the source translation.
- C11's reason-giving and `دوہاں` construction informed worked reasoning and changing the bridge's initial Urdu `دونوں` to Punjabi `دوہاں`.

The script's older `application` annotations sometimes name PNB-001; they are index metadata, not a claim that those pilot applications happened here. This note records the new uses. The canon remains three prose essays by one author and does not certify specialist mathematics terminology or any historical assertion as source data.

## Linguistic and mathematical decisions

- `فنکشن دی قدر کڈھنا` is the provisional descriptive rendering of “evaluate.” It includes symbolic inputs as well as numeric ones. “Solving Functions” becomes `فنکشن دی مساوات حل کرنا`, making the implied equation explicit rather than suggesting that a function itself is an unknown equation.
- `ضرب دی تقسیمی خاصیت`, `ضربی عامل`, `مربع جذر`, `پیرابولا`, and `حاصل ضرب` are provisional academic-register choices. The original bridge supplies English labels and plain explanations; the limited prose canon does not establish specialist usage. No shared terminology ledger was changed by this task.
- The initial source function is `f(x)=5−3x²`; the next example uses a different `f(x)=x²+3x−4`. The bridge explicitly separates these local definitions. The symbol `h` in `a+h` is an input increment, while later `h(p)=p²+2p` uses `h` as a function name. No source letter is renamed.
- The first formula's operation order is square the input, multiply that square by 3, then subtract the product from 5. Revision made `اوس مربع` explicit to prevent the multiplication pronoun from being read as the original input.
- The source statement that a letter input cannot be simplified further remains faithfully translated in part (b). An original note explains that no particular numeric `a` is supplied; this must not become a universal prohibition on further algebraic manipulation of symbolic expressions.
- The difference quotient cancels a factor `h` but the source does not state `h≠0`. The necessary restriction is supplied **only** in the explicitly original bridge. The simplified expression's value at zero does not make the original quotient defined at zero. No limit/derivative claim is added.
- Both Try Its use `g(m)=sqrt(m−4)`, with the entire difference under the square root. The source answers `g(5)=1` and `m=8` are preserved. An original note specifies the real-input restriction `m≥4` and the nonnegative principal square root; it does not introduce a second answer -1.
- “Always one result” applies to inputs in a function's domain. Solving can also have no solution when the requested output is outside the range. These are labeled original qualifications, not silent source rewrites.
- The zero-product source paragraph says either factor is zero “or both.” That general rule is preserved; the original note explains that these particular factors `p+3` and `p−1` cannot both vanish for the same `p`. The distinct solutions -3 and 1 are retained.
- Plain visible numbers, variables, ordered pairs, part labels and English bridge text use LTR isolation. Plain image-alt attributes cannot contain `bdi` markup. Minus signs and all image/formula data remain tied to their source.

## Required presentation treatment

Four source inline MathML leaves contain a sentence period inside an `mn`, not a separate `mo` or `mtext`:

| Source paragraph | Zero-based math slot | Exact terminal token |
| --- | --- | --- |
| `fs-id1165137460826` | 1 | `<mn>3.</mn>` |
| `fs-id1165134468906` | 2 | `<mn>3.</mn>` |
| `fs-id1165134468906` | 4 | `<mn>24.</mn>` |
| `fs-id1165134170174` | 1 | `<mn>2.</mn>` |

The frozen witness retains these exact tokens. If the renderer relocates their sentence periods for Punjabi syntax, it must use a reversible, source-specific old/new/path ledger. Do not implement a broad numeric-dot stripping rule that could damage decimal values. Existing terminal `mo` comma/period cases also need the established reversible treatment. Parent structural QA must reconstruct all 38 exact source MathML trees; this draft does not claim that rendering step has passed.

The English MathML instructions “Factor out h,” “Simplify,” “Substitute the original function,” “Subtract 3 from each side,” and “Factor” remain source content. Their Punjabi key is original support. Internal math punctuation, the combined `mtext` token `)(`, empty layout nodes, NBSP alignment strings, exponent/fraction trees and English instructional cells must not be silently dropped. Wide nested calculations need local scrolling and narrow-screen inspection.

## Read-only draft QA and limits

The initial in-memory inspection passed 320 checks. After restoring the original outer whitespace and the two introductory italic emphases, a full final read-only check passed **321 checks** against the hashes above. These are drafting checks executed in memory, not a saved reader-QA suite. They verified exact selected-prefix structure/text/attributes; hashes and newline equivalence; all 37 derived keys in source order; all 55 IDs; the 29/9 MathML split; ordered math/link/child placeholders; nested part-(d) children; all part labels; plain-prose numeric order; three source emphasis treatments; fragment parsing; local links; image hash; LTR isolation; Unicode gates; and the four unchanged `mn` punctuation tokens.

A narrow arithmetic evaluator read the actual source MathML right-hand sides. It confirmed `f(2)=6`, `h(4)=24`, `h(-3)=h(1)=3`, `g(5)=1`, and `g(8)=2`; a negative radicand was rejected in real arithmetic. Twenty nonzero-increment test pairs checked the displayed difference-quotient simplification. These are bounded tests, not a universal proof of an algebraic identity. The exact source-tree comparison preserves the complete symbolic derivation separately.

No reader build, detached rendered-DOM mutation test, screen-reader/keyboard check, browser layout approval or native-language certification was performed by this drafting task. Parent owns source-bound reader QA, final asset/notice integration, shared build/CSS/terminology changes and visual review. Owned edits are only `source-excerpts/manifest-006.json`, `source-excerpts/unit-006.cnxml`, `translations/unit-006.json`, this note, and the explicitly requested small canon receipts. No bulk write, download, deletion or commit was performed.

## Later-source warnings, not translated coverage

The broader source study found issues outside this prefix for later decisions: pet-table `Table_01_01_10` summary says 2100 hours for goldfish while the actual cell and prose formula say 2160; the dated pet-memory story must not be presented as newly verified science; the source's range wording is singular although the outputs form a set; and Figure 009's source alt gives vertex (0,1) while the actual image inspected at original detail has vertex (1,0). The later table renderer must distinguish translated pet-name data cells from column/row headers. None of these later-source issues was corrected, translated or counted as PNB-006 coverage.
