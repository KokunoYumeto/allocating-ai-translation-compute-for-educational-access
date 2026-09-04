# PNB-003 language and source notes

Date: 2026-08-30. Target: Western Punjabi, Shahmukhi (`pnb-Arab-PK`). Native-speaker/educator review remains pending. This checkpoint does not complete the five assigned books.

## Scope and primary witnesses

Read the actual English and Indonesian CNXML, lines 159–253 of each:

- `downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml`, project-pinned English commit `789b54099106b071d1d32bfcee454fed72eb4768`.
- `downloads/extracted/A30/repo/source/modules/m49301/index.cnxml`, the acquired A30 comparison edition.

Only `Example_01_01_02` and the immediately following note `fs-id1165137588587` are translated. The note includes `ti_01_01_01`, its baseball table, source footnote, two questions, and the two answers. Stop before `fs-id1165134474160` / “Using Function Notation”. That section is the next source cursor, not translated coverage.

The translation has 17 source-block strings: problem title; grade introduction; grade table summary and two row-header cells; two grade solution paragraphs; Try It label; baseball introduction and footnote; baseball table summary and two header cells; two question items; two answer items. Global table row indexes include `thead`: `Table_01_01_02/row/1/entry/1` and `/entry/2` are the player/rank headers. Grade headers are `Table_01_01_01/row/1/entry/1` and `/row/2/entry/1`.

`{{link:0}}` occurs in both introductions. `{{child:0}}` immediately after the baseball table link preserves the source footnote at that location. The footnote's own key is `fs-id1165135255104`. There is no source MathML in this scope, so no `{{math:...}}` placeholder is required. Circled source item labels are rendered as explicit LTR `(a)` and `(b)`, matching PNB-002's declared convention.

## Actual canon consultation — draft

The previously read canon index provides the C01–C12 mapping. Before composing PNB-003, reread actual surrounding passages in the local prose witnesses: R1 lines 26–30, 33–37, 43–47; R2 lines 26–28 and 32–34; R3 lines 25–26, 31, and 37–38. This was a direct read, not a generated receipt or a summary substitution.

- C01/R1: the ability construction informed `ہو سکدے نیں`, with agreement controlled by plural `گریڈ`, not copied mechanically from the feminine singular essay clause.
- C04/R1: plural agreement and quantity prose informed `قطاراں`, `قدراں`, and Punjabi `نیں`; the school/register context in R1 lines 45–46 also supports ordinary `طالب علماں`.
- C03/R1: `ترتیب وار` informs the already-provisional ordered-pair wording; it does not certify a mathematical dictionary entry.
- C05/R2: purpose and implication were kept separate. Function conclusions use `ایس لئی`; no purpose connective was substituted for a mathematical implication.
- C07/R2: the ordinal/location construction informed first/second row descriptions and `چوتھے درجے اُتے`.
- C09/C10/R3: the reminder and qualification passages informed `چیتے رکھو` in the source note and the separately labeled original correction of the grade-table summary.
- C11/R3: the reason-giving context was read while checking the many-to-one and tied-rank explanations. The final support prose also uses direct conditional `جے ... تاں ...` and consequence `ایس لئی`, rather than treating the essay as mathematical evidence.

These three essays are a narrow prose-register reference. They do not establish GPA terminology, educational grading policy, or baseball rankings. No new canon material was downloaded and no shared canon receipt was overwritten.

## Actual canon consultation — revision

After writing the draft, reread the saved JSON in full alongside R1 lines 28–29, 35–36, 45–46; R2 lines 33–34; and R3 lines 25–26, 31, 38. C07's actual R2 passage includes the plural locative `چار کالماں وچ`. This informed changing `باقی اٹھ کالم وچوں` to `باقی اٹھ کالماں وچوں` in the accessibility override and original bridge. The upper grade-band entry was also described specifically as a range paired with the lower GPA value, not as two individual numeric values. The count qualification was recast as `قطاراں تے کالماں دی دِتی ہوئی گنتی` for clearer modifier scope. Source translations, cell values, association directions and placeholder order were not changed by these original-support revisions.

## Source discrepancies and preservation decisions

The English grade-table summary claims two columns and ten rows and lists interval/GPA pairs in descending order. Actual CALS markup has `tgroup cols="9"`, two `tbody/row` elements, and nine entries per row. Its first column contains row headers, followed by eight ascending grade-band/GPA columns. The summary is not a reliable orientation description.

`Table_01_01_01/summary` translates the English summary faithfully, including its incorrect dimensions and descending pair order. Its range hyphens are presented as en dashes to match the actual table's interval typography; endpoints and decimal values are unchanged. The separate `table_summary_overrides.Table_01_01_01` supplies the accurate accessible description. The parent renderer is responsible for retaining the faithful translation in `data-source-summary` and using the override for accessibility. The explicitly original bridge explains both the orientation/count discrepancy and why the table itself was not transposed or reordered.

Indonesian already corrects this summary to two rows and nine columns, with ascending pairs; that comparison corroborates reading the actual XML but is not silently substituted for the English witness. Indonesian summary/prose sometimes uses decimal commas, while both English and Indonesian table cells retain decimal points. This translation preserves English/source-table decimal points throughout.

Preserve these source cells exactly, with LTR isolation supplied by the renderer:

| Percent-grade cells, left to right | GPA cells, left to right |
| --- | --- |
| `0–56`, `57–61`, `62–66`, `67–71`, `72–77`, `78–86`, `87–91`, `92–100` | `0.0`, `1.0`, `1.5`, `2.0`, `2.5`, `3.0`, `3.5`, `4.0` |

The correct grade table has two rows and nine columns including the header column. The baseball table has six rows including its header and two columns; its summary is accurate and receives no override. Retain `Babe Ruth`, `Willie Mays`, `Ty Cobb`, `Walter Johnson`, `Hank Aaron` and ranks `1` through `5` exactly as source data, not transliterated replacement identities.

## Mathematical and linguistic boundaries

- Grade mapping is percent grade to GPA, not vice versa. The same GPA can correspond to distinct percent grades, explicitly including 78 and 86 mapping to 3.0. No inverse-function claim is made.
- The eight written bands cover whole-percent grades from 0 through 100. Treating those as whole percentages is an implicit assumption, not an explicit source statement. The original bridge discloses this interpretation and that fractional-percent handling/rounding is unspecified. Do not silently convert the bands into continuous intervals, round grades, or present the example as a universal GPA rule.
- `فی صد گریڈ` and `گریڈ پوائنٹ اوسط` are provisional academic-register choices. The original bridge glosses them with the English `Percent grade` and `Grade point average (GPA)`. Existing `فنکشن`, `اِن پُٹ`, `آؤٹ پُٹ`, and `قدر` remain consistent with PNB-001/002. `درجہ` distinguishes ranking from course `گریڈ`. `کھڈاری` is the provisional Punjabi player term. These are not canon-certified terms.
- The baseball introduction faithfully preserves the source's all-time-greatest framing. The separate original note explicitly attributes the ranked list to its dated witness, not a current fact or universal ranking. Its access date `3/24/2014` is the source's date, not this drafting pass's access date.
- Footnote URL `http://www.baseball-almanac.com/legendary/lisn100.shtml` and source access date are preserved, visibly LTR-isolated. The URL was not fetched; no freshness claim is made. Converting the printed URL to a clickable link is a renderer-level convenience, not new source evidence.
- Both baseball relations are functions for this exact five-row data set. The hypothetical fourth-place tie introduces two distinct names for one rank, making name-from-rank fail uniqueness. No claim about tied results in a different ranking system is added.
- Numeric prose, visible ordered pairs, dates and English labels use `bdi dir="ltr"`. Plain-text table summary attributes cannot contain markup; the corrected summary describes row/column structure without embedding numeric pairs. The original visible bridge supplies the eight grade pairs with explicit LTR isolation.

## QA and handoff status

Final linguistic QA reread the saved JSON in full, then the actual canon passages at R1 lines 28, 35, 45–46; R2 lines 33–34; and R3 lines 25, 31, 38. This checked C01/C04 ability and plural agreement, C03 ordered sequence, C07 column/location wording, and C09/C10/C11 reminders, disclosed qualifications and reasoning. The revised plural `کالماں وچوں` matches the actual locative pattern read in R2. Specialized grading vocabulary remains provisional despite this prose-register review.

A read-only PowerShell check derived expected keys directly from the selected English example/note, including global table-row indexes and text-bearing header entries. Results: 17 source blocks; zero missing/extra keys; two link placeholders; one child placeholder; zero math placeholders. All source-block fragments and the complete original bridge parsed as XML fragments, and the JSON parsed successfully. No Gurmukhi, replacement characters or forbidden bidi controls were found.

The same check extracted the actual source table cells. The original bridge's eight displayed range/GPA pairs match their values and ascending column order exactly; the faithful source-summary translation preserves descending pair order. The grade table has two rows and nine columns; the baseball table has six rows and two columns. Expanding only the explicitly disclosed whole-percent interpretation in memory produced 101 distinct inputs (0–100), with no overlapping bands; both 78 and 86 map to 3.0. The five source player names and five ranks are unique, supporting both source function answers for this table. Source footnote URL and `3/24/2014` were confirmed unchanged. No temporary data or receipt was written by these checks.

Parent owns table/footnote renderer support, source excerpt/manifests, reader build, cross-reference resolution, rendered cell-value and orientation checks, desktop/mobile visual QA and integration. This note does not claim those steps have passed. In particular, the renderer must use the accurate accessibility override while retaining the faithful source summary for traceability, and must keep source table data/name cells LTR without transposing the tables. Native-speaker/educator approval remains outstanding.

Only `translations/unit-003.json` and this note are edited by this drafting task. No downloads, bulk copying, extraction, deletion, commits, or edits to other units/QA scripts are authorized or performed.

## Parent integration revision

Desktop inspection showed that displaying the entire footnote URL/date inline interrupted the Punjabi sentence between its table reference and وچ. The final renderer therefore keeps the original footnote ID on a superscript reference at the exact source position and places its full translated URL/date in a linked endnote with a new `-text` ID and a return link. Original source-ID order and ancestry remain intact. The earlier inline-content instructions above describe the draft handoff, not the final display. Table containers explicitly start LTR at column one; cell center alignment follows the source's `align="center"`. Parent QA reread C03/C04/C07/C10 and recorded a timestamped receipt.
