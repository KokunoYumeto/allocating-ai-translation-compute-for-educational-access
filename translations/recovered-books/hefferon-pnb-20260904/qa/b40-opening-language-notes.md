# B40 opening — source, language and scope notes

Status: complete174-slot draft revised against English, Indonesian and actual canon. Source-bound input QA passed twice deterministically with5,132checks and42detached mutations; these inputs are frozen for the later bounded renderer. No reader, MathML converter, source engine, PDF modification or whole-frontmatter completion is claimed.

## Source and exact boundary

The canonical work is Jim Hefferon's *Linear Algebra*, fourth edition, at `df2262e089a02651c127f1dd12649c4622ee1383`; Indonesian `e84ce2956a7304830c42eba70106f940fefee7c4` is comparison only. Actual default `hardcopybool=false` reading order is cover, notation/Greek tables, full preface, generated contents, then main matter. The nondefault print titlepage is a recorded conditional witness, not silently duplicated in the reader.

This draft covers the full default cover labels/title/author metadata, all notation and Greek-letter content, and the entire preface:20prose paragraphs,6headings, the14-week timetable, both lineated quotations, all7author-credit lines and the final Author's Note. The174keys include metadata and cell bindings, not merely174prose paragraphs. Six tabular environments contain64physical rows/138cells; two quotations and the author credit are lineation/layout, not mathematical data tables.

The exact next boundary is `src/book.tex:51`, beginning the generated table of contents and ending with the starred-subsection explanation. Both remain required before ChapterOne. The full B40 textbook, its answer book, laboratory and overall five-work assignment remain incomplete. There is no claim that an earlier introduction was silently skipped or that this covers every frontmatter page.

The JSON source witness keeps exact pinned UTF-8/LF TeX as inert strings. It is not a TeX buildroot. All174English spans have separately bound Indonesian spans. Offsets are Unicode-codepoint indices with exclusive ends; raw slices, hashes, occurrence keys and token owner paths are explicit. Raw comments remain intact. Active text removes unescaped `%` through its newline: comment lines must not split the continuous preface paragraphs5,6and15. Commented-out timetable rows, older covers and the Joyce quote remain inert, not reader content.

## Draft-stage canon actually consulted

Displayed and read complete paragraphs from `R1.txt` at28(C01),39(C02),45(C03),35(C04), and `R3.txt` at31(C09),25(C10),38(C11). The separate draft receipt records file/paragraph hashes and actual applications. These are Jamil Ahmad Pal's readable Shahmukhi prose, not mathematical terminology standards or endorsement of the essays' other claims.

- C01/C02 informed Punjabi ability/advice forms: `سکدا/سکنا`, `چاہیدا` and direct imperatives rather than Urdu `سکتا/سکتی ہے`.
- C03 informed `ترتیب وار سلسلہ`; the mathematical phrase remains explicitly provisional.
- C04 informed Punjabi plurals, especially `فضاواں`, `نیں` and plural agreement.
- C09 informed `چیتے رکھو` in the preface reminders.
- C10 informed the separately original polynomial-degree qualification; no source cell is silently corrected.
- C11 informed connected explanation register. Purpose and causal connectives remain a revision focus rather than a claim that a receipt establishes idiomatic language.

## Source voices, credits and historical statements

The preface's first person belongs to Jim Hefferon, not the translator. Preserve Jim Hefferon, G Ashline, Saint Michael's College, Lynne, Stephen Jay Gould and Wilbur Wright distinctly. `Hef{}feron` is a raw TeX ligature-control spelling, visibly `Hefferon`. Quotes retain their source author and4/5line layouts; the author credit retains all7lines, `Colchester, Vermont USA 05439`, `2021-Oct-12`, fourth edition and second printing. Inert cover metadata `today` is not the publication date and must not be evaluated.

Availability, Free/latest version, inexpensive printing, current contact, software and resource claims remain source-attributed historical statements. The original context note explicitly says this workflow did not verify their present-day availability. Source `Free` is translated `آزاد`, not silently reduced to a zero-price claim; the separate source price sentence remains.

Existing B40 notices select CC BY-SA2.5 from the original GFDL/CC BY-SA2.5 options. This is not B10's NC-SA4.0 or an OpenStax work. Existing component qualifications and nonendorsement remain binding. No new rights/supply audit, general asset clearance or font/runtime license change is made.

## Mathematics, tables and comparison decisions

All76inline TeX owners are retained exactly, including delimiters, internal whitespace, variables, fences and macro syntax. No derived MathML exists yet. The three URL commands, one publicationdate include and two exercise marks have separate exact source slots. Future production must inspect/bind Hefferon's actual macros, including `Re`, `C`, `N`, vector accents, `polyspace`, `matspace`, `sequence`, `rep`, `spanof`, range/null/generalized spaces, `deter`, `nbym` and `nbyn`; reusing B10 expansions without checking is not allowed. The two matrix-size macros include negative thin spacing, requiring a deliberate reviewed rendering policy. No unknown grammar may silently disappear.

Source notation says natural numbers include0. The separate original note reinforces this local convention without changing the source or imposing another book's convention.

Notation row8 says “degree n polynomials”; the later canonical `src/vs/vs1.tex:454–459` explicitly defines the space using degree n **or less**. The raw later six-line witness, file/blob hash and excerpt hash are retained as evidence. The source table keeps its original wording, and a separate Punjabi clarification makes the later definition visible.

The English Greek-letter phonetics are canonical. Indonesian localizes those guides; those replacements are not imported. All24guide payloads remain inspectable in `data-source-pronunciation`; ordinary “as in” explanations are translated while their English example words remain isolated. Punjabi Greek names are provisional spellings, not native pronunciation certification. Literal source omicron `o` is not silently changed into another codepoint/command.

Timetable section identifiers such as `One.I.1--2` remain exact in raw source. Readable range dashes follow TeX's en-dash meaning, not a minus. Exam/Thanksgiving labels are translated; week numerals and each source section reference remain intact. These are forward source identifiers, not false local links to already available Punjabi chapters. En-dash versus original-label decorative dash encoding must be made reversible in production.

## PDF accessibility and remaining revision

Both original one-page PDFs were rendered read-only in memory and visually inspected at the draft stage. `axesgraphic.pdf` contains gold/purple vertical planes crossing a green plane without text labels; `shadow.pdf` is the separate gray shadow. No original image or PDF byte was edited or copied into new assets. The proposed Punjabi descriptions are explicitly original accessibility text, because the TeX source has no alt. Preserve the original layer order and PDF hashes at production; do not mirror or recolor them.

Revision actually reread R1:39(C02), R2:27(C05/C06), R3:31(C09), R3:25(C10), then the full drafted preface and notation descriptions. The source-purpose clause in paragraph6 became `تاں جے`; paragraph16 now preserves the author's qualified explanation for optional sections. Revisions removed an accidental similarity claim from the sequence description, repaired agreement and self-map wording, made both generalized spaces explicitly `تعمیم شدہ`, and corrected the paragraph7 restatement and paragraph19 agreement. Pure-formula/glyph separator commas now remain source ASCII commas. All source `--` range/author-label punctuation is represented by en dash, never a math minus.

QA actually reread R1:28(C01), R1:45(C03), R1:35(C04), checked the resulting ability, sequence and plural constructions, and compared all Greek-name/pronunciation cells and both complete quotes/credit rows to the source. The Gould quote's phrase “illustration … by particulars” becomes the Punjabi clause with its verb at the end of the third line; the linked2nd/3rd line meaning is retained across the same3text-line layout, followed by the unchanged named attribution. This is an explicit SOV clause-placement decision, not a source omission.

Some technical terms (`سِدھا مجموعہ`, `حاصل فضا`, `صفر فضا`, `ڈیٹرمننٹ`, `آئگن قدر`, `ہومومارفزم`) remain consciously provisional. There is no native Punjabi or educator certification. Input QA independently rediscovered174ordered spans, all6table shapes/138cells, exact76TeX owners plus6other slots, and rejected42detached adversaries; its reviewed Punjabi seals are change detectors, not semantic certification. The later finite MathML parser, reader, browser and assistive-technology checks remain required; no whole-work completion is claimed.
