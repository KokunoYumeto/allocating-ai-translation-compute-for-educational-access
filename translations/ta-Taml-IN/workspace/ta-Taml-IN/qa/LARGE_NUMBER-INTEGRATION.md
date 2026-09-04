# U003-U005 recovery reader integration

Date: 2026-08-31. Source-faithful sections plus a separately marked original companion; not a complete module/course or validated grade-placement instrument.

## Content and packaging

The root read the actual companion introduction, diagnostic/answer cards, four explanations, source-help section, practice/mastery/retry questions and feedback, and the author's checking notes. Actual canon OCR pages11/12 were consulted again for named positions, separated number words and expanded contributions; earlier full-image checks remain the authority for OCR-corrupted arithmetic. International grouping is not attributed to the Indian-system canon. The provisional million/billion/trillion terms are defined with exact values.

`scripts/build_large_numbers.py` leaves the committed source-only preview untouched. It inserts the three rendered source sections before `ta-large-source-help`, with source-specific boundary labels. The 14 companion sections retain exact parsed element/attribute/text signatures. Source IDs and MathML remain in their original order. All16new questions have distinct, separately located reasoned answers and a specific remedy/question-return route. Source answers remain visible, as the introduction explains; this is not answer access control.

The reader has141source IDs,15source exercises,55source MathML roots,16new questions/16answers,56total MathML roots,8SVGs,6semantic tables and535unique document IDs. The underlying source assembler validates both complete witnesses, child counts, mathematical invariants and SVG closure without writing source files; its input hashes are recorded separately from the rendered-source inputs. A before/after input guard detects source/companion/style changes during the build. HTML/EPUB are built entirely in memory, checked twice for exact repeatability, then written to the dedicated output folder. Unexpected existing files cause refusal, not deletion. Independent code review found that source IDs/math alone would not catch altered ordinary prose during integration. Added exact source-section signatures against the original rendered preview, including prose/SVG content, and an in-memory changed-prose negative fixture. No actual generated-text corruption was found.

`scripts/qa_large_numbers.py` independently recomputes all16items: grouping from question numerals, four Tamil-name-to-number questions, three newly supplied Tamil answer names, seven digit/place/contribution claims, leading/interior zero distinctions,15place powers and5scale values. Its small coefficient/scale parser is deliberately limited to these authored names, not an arbitrary Tamil-language checker. Four in-memory mutations (wrong grouped answer, wrong name-to-number answer, wrong Tamil answer word, duplicate answer mapping) are rejected. The builder also rejects four rendered mutations: missing remedy target, duplicate ID, changed answer mapping and altered source prose.

The16-file package includes an EPUB with identical reading content and bundled fonts/styles/figures/notices. EPUBCheck5.3.0 reports0fatals/0errors/0warnings/0infos for the final EPUB. This is format conformance, not EPUB-app or assistive-technology validation. No new PDF is produced at this checkpoint.

## Browser inspection and correction

Used the in-app browser on the task-owned local reader server. At375CSS-pixel content width, the actual16question/16answer cards were present, Tamil fonts reported loaded, and document client/scroll widths both375. Clicked the exact diagnostic link from the start section and the U003 link from source-help; each reached the correct anchor and heading. Visually inspected the start, diagnostic question area and15-row place guide at phone width, plus the mastery answer/routing panel at desktop width. These are targeted screens, not a claim to have visually inspected every source figure or every screenful of this long document.

Inspection found a real presentation defect: the last0of `100,000,000,000,000` wrapped onto a separate line in the narrow place guide. Gave the value column more width and made its numeral nonwrapping; only at viewports360pxorless the value font reduces to85%of the table font. Rebuilt and repeated QA/EPUBCheck. Screenshots then showed the complete numeral on one line at375and320content pixels. At320, document client/scroll widths both320and the last value cell's client/scroll widths both149. No source/companion wording changed for this fix. Viewport overrides were reset.

The pre-existing full15-row chart alternatives and visible figure descriptions are retained. Full visual inspection of hidden portions of the wide source SVGs, genuine keyboard horizontal-panning behavior, assistive-technology user testing and native/educator/learner review remain open. Earlier limited source-preview checks are not silently promoted to an all-figure pass.

## Current byte identities

- Companion: `37f05038e4c238ca0e7a0951f2b136e84aa7c6391a6acac7da7678498361baf8`.
- HTML: `d969dc82fa06b273e38bf36e278e6f3dfc94f09165e5ad106c59572f78a1d51a`.
- Final EPUB after numeral-wrap correction: `680ecbfff5dd506e3e73ea25e58300b9dda02e43aa846f067721f8352839ae8b`.
- Recovery CSS: `33a148159848ca733f53123cb5a05bc6da22e9215f4b2357ae33dd77e28a5ac2`.
- Structural receipt: `72011e6d3cb065381ec565f52eb1120057802b302e609c10e1034fac17c90817`.

Reproduce with `scripts/build_large_numbers.py`, then `--check`, then `scripts/qa_large_numbers.py`. QA receipts and generated outputs retain exact Git bytes. Authoring, structural, rendered, conformance and human-review claims remain separate.
