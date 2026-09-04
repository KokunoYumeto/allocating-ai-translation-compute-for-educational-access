# B40 opening parent source and browser review

Reviewed final reader SHA-256: `b2f9f0faafa080248a30af434c354a2b6e458f5bb9db4855f96fed740d9ec7b9`.

The isolated B40 pipeline passed 4,092 checks and 39 detached mutations in two byte-identical full cycles. It covers 174 exact source owners, 76 limited MathML owners with exact raw-TeX fallbacks and reversible ledgers, three semantic tables (20×2 notation, 13×4 Greek, 15×2 schedule), two lineated quotations, one seven-line address, two exact pinned PDFs and two separately disclosed Poppler RGBA previews. Receipt `structural-b40-opening.json` has SHA-256 `6077c49e31bcc316440d5ba1186f21a0e499a33eea87d7ff60bcaa4bb11ef57d`.

The first parent mobile gate found a real scoped bug: the shared `figure img { min-width:640px }` mobile rule forced both B40 cover component previews to 640px inside 224px figures. The cover grid leaked to 804px and the page to 421px at a 375px viewport. The final B40-specific rule now uses `repeat(2,minmax(0,1fr))`, gives components `min-width:0;max-width:100%`, and gives their images `min-width:0;width:auto;max-width:100%`. Detached regressions were added before refreeze.

The parent retested the final reader. At mobile width, document `scrollWidth` and `clientWidth` are both 375px; the 308px cover grid has two approximately 143.9px tracks, and the component previews render at 144px and 108px with no leak or broken image. At desktop width the page is 1009/1009 with both component previews loaded and no object/embed/iframe runtime.

The parent visibly panned the notation table, reviewed the Greek and 14-week schedule tables, both source quotations and the footer, clicked the visible “اصل فارمولے” navigation link, and opened `#source-tex-001`. It showed source owner `src/cover/symlist.tex#table/1/row/1/cell/1` and exact raw text `\( \Re \)`. The reader still stops before generated contents and the starred-subsection explanation and does not claim exact TeX cover composition, complete front matter, a complete book or native/educator/assistive-technology certification.

Bounded final screenshots and hashes are recorded in `visual-b40-opening.json`.
