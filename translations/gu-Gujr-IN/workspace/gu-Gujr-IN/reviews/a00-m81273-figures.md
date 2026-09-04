# A00 m81273 figure localization

Active durable goal, 2026-09-01: complete a separate source-bound figure-localization workflow for A00 order13 m81273, Prime Factorization and the Least Common Multiple, after the m81272 bundle was frozen and returned to root. Do not modify the root-owned frozen CNXML, media/errata JSON, shared dispatcher, library renderer, status, terminology, canon, commits or publication branch. Independently inspect all26 canonical originals; enumerate and retain the22 math-only assets only after actual-image verification; replace all four language-bearing assets with Gujarati native HTML/SVG/table markup: 006 for12/18 aligned prime factors and LCM36, 026-03 for15/18 and LCM90, 027-03 for50/100 and LCM100, and AppB012 with two complete skills and six empty response cells. Preserve source repeated factors, blank alignment columns, arrows, horizontal rules, multiplication dots, values, LCM abbreviation after its full Gujarati expansion, final lines and all response blanks. The source/alt issues already keyed by the translator remain separate from the faithful CNXML; the redraw uses the actual original and corrected accessible mapping, including the final standalone36 line in006.

Workflow: reread actual instructions, the authority source, frozen Gujarati descriptions, full media receipt, shared terminology and actual readable Gujarati factor/prime/LCM canon before drawing, during revision and at output review. Open all26 originals rather than trusting alt text, then reopen all four localized originals at revision. The helper must expose `render_figure(filename, alt, unique_id)`, namespace any SVG definitions from `unique_id`, use Gujarati/Nirmala fonts, return `None` only for the exact22 verified math-only filenames, and avoid source/runtime mutation. Add a source-bound QA script and small preview pages. Bind source SHA, Gujarati SHA, metadata SHA, all26 media IDs/paths and binary hashes. Independently verify every factorization and LCM:12=2·2·3,18=2·3·3,LCM36;15=3·5,18=2·3·3,LCM90;50=2·5·5,100=2·2·5·5,LCM100. Check matched-column arrow relationships rather than only final products. Verify2 self-check skills/6 blank responses, Gujarati accessibility, zero embedded English, unique IDs/references, local overflow, Gujarati shaping, actual phone/desktop output and final geometry.

Do not confuse mathematical-only originals with trustworthy source descriptions: actual018 lacks the source-claimed circle and actual201/202 counters are pale yellow/lime rather than blue, but those source corrections remain root-owned accessible errata, not a reason to redraw math-only artwork. The old global objective ranking is withdrawn and will not be cited. Indonesian backend work is candidate context only and cannot replace the pinned English authority. Compaction can be stale; reconstruct state from actual files and hashes. This module freeze will not complete the full assignment. After precise handoff, continue only the next parent-assigned isolated figure lane. Coordinator owns the hourly heartbeat and GitHub review branch; this lane makes no push, merge, release, cleanup, production or educator-approval claim.

## Source and canon review

Actually reread the verbatim instructions, the frozen translator review, the four exact source figure contexts, all Gujarati alts, the complete media and correction mapping, shared terminology T25–T32 and the targeted factor/prime/LCM evidence before drawing. I returned to those same files during revision and after browser rendering. Authority SHA is `4da1f4b3fb0d26f4ece7475531f5f6f46ed8c7801fffd605429105a836abd40e`; frozen Gujarati SHA is `e9fbb999275fe8237e33beb36e0b9f318d6d73472070a8d0d5ee45204866e367`; media/errata SHA is `9369d6aca54779165947e1d6f8244760c44154dfdbfde246d4348f2d7d430529`. All root-owned files remain unchanged.

The readable primary Gujarati evidence recorded in the module review supports `અવિભાજ્ય અવયવીકરણ`; the indexed prime-factorization transcript includes75=3×5×5 and32 as five repeated factors2. The indexed LCM exercise supports `લઘુત્તમ સામાન્ય અવયવી` at heading/exercise level only. Following T30, every redraw visibly gives `લઘુત્તમ સામાન્ય અવયવી (LCM)` before retaining the source abbreviation in mathematical rows. I do not claim that a later zero-line direct open supplied a transcript. Arithmetic and column matching are verified independently rather than inherited from transcript wording.

## Complete actual-image inspection

All26 originals were independently opened at original resolution in four batches. The22 retained originals have only numerals, operators, lines, colored factor circles, envelope/counter shapes or arrows; none contains a human-language label. This was verified from the actual pixels, not inferred from the metadata. The inspection also reconfirmed known source-description errors without editing root-owned errata:018 has no visible circle around its edge3; the ladder quotient sits above the dividend/bar;201/202 counters are pale yellow with lime outlines rather than blue.

The four language-bearing originals were reopened after revision. Exact relationships preserved:

- 006 aligns12 as2,2,3,blank and18 as2,blank,3,3. Its four arrows yield2·2·3·3, followed by the source's separate `LCM = 2 · 2 · 3 · 3 = 36` line.
- 026-03 aligns15 as blank,3,blank,5 and18 as2,3,3,blank. Arrows come from lower-only2, shared3, lower-only3 and upper-only5. The image ends at `LCM = 2 · 3 · 3 · 5`; the redraw does not add a visible90 line that exists only in surrounding explanation/alt.
- 027-03 aligns50 as blank,2,5,5 and100 as2,2,5,5. Arrows distinguish the first lower-only2, the shared aligned2 and both repeated shared5s. The redraw ends at `LCM = 2 · 2 · 5 · 5`, matching the image rather than inventing a final100 line.
- AppB012 has two skills and three response choices per skill. All six cells remain blank.

## Implementation and QA

`scripts/localized_a00_prime_lcm.py` exposes `render_figure(filename, alt, unique_id)`, returns native markup for the four labeled assets, and returns `None` only for the exact22 verified filenames. The three responsive SVGs use four fixed factor columns plus source-matched start heights for shared and unshared arrows. All marker IDs come from `unique_id`; the full Gujarati LCM term is visible outside the mathematical SVG. The self-check uses two semantic tables with scoped column headers, captions and explicitly labelled blank cells.

`python gu-Gujr-IN/scripts/qa_a00_prime_lcm_figures.py` passes. It binds all26 media IDs/paths and original binary hashes to the source/translation/metadata pins, checks4 redraws+22 originals,7 unique IDs,12 resolved references,3 LCM diagrams,12 aligned columns and6 blank response cells. Nine independent arithmetic/model checks pass: all five source factorizations, all three LCM products and preservation of every repeated-factor column. Final helper SHA is `a6b13e0169918fefb2baaebb6ab3a94edb05e2bccfde8d4ae581e62e540efb0a`.

## Actual browser review

Both preview pages and all four redraws were actually scrolled and inspected at390x600 and1000x600. Phone geometry is375/375 on both pages;1000-pixel review geometry is985/985. Final1280 geometry is1265/1265 on both pages. Gujarati and Nirmala font checks pass. After allowing only the explicitly defined source abbreviation `LCM`, localized bodies have zero multi-letter Latin hits. Page IDs are unique, all12 marker references resolve, all factors/arrows remain legible, and there is no document or local overflow. Receipt: `reviews/a00-m81273-figures-browser.json`.

No numerical, alignment or rendering uncertainty remains. Canon attestation and educator approval retain the qualifications already recorded by the translation team.

## 26-occurrence inventory

The inventory below is emitted from the source-bound QA receipt. `math-only` means the actual original was opened and contains no embedded language.

| # | Source media ID | Filename | Mode | Actual-image check |
|---:|---|---|---|---|
| 1 | `fs-id2777835` | `CNX_BMath_Figure_02_05_018_img.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 2 | `fs-id1631520` | `CNX_BMath_Figure_02_05_019_img.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 3 | `fs-id2492072` | `CNX_BMath_Figure_02_05_009_img.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 4 | `eip-id1168469860444` | `CNX_BMath_Figure_02_05_022_img-01.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 5 | `eip-id1168469408943` | `CNX_BMath_Figure_02_05_022_img-02.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 6 | `eip-id1168469871229` | `CNX_BMath_Figure_02_05_022_img-03.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 7 | `eip-id1168468294078` | `CNX_BMath_Figure_02_05_023_img-01.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 8 | `eip-id1168468774285` | `CNX_BMath_Figure_02_05_023_img-02.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 9 | `fs-id2451776` | `CNX_BMath_Figure_02_05_010_img.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 10 | `fs-id2698106` | `CNX_BMath_Figure_02_05_011_img.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 11 | `fs-id2205845` | `CNX_BMath_Figure_02_05_012_img.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 12 | `eip-id1168468775312` | `CNX_BMath_Figure_02_05_024_img-01.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 13 | `eip-id1168468478403` | `CNX_BMath_Figure_02_05_024_img-03.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 14 | `eip-id1168468274425` | `CNX_BMath_Figure_02_05_024_img-02.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 15 | `eip-id1168466807907` | `CNX_BMath_Figure_02_05_025_img-01.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 16 | `eip-id1168466807923` | `CNX_BMath_Figure_02_05_025_img-02.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 17 | `fs-id1733229` | `CNX_BMath_Figure_02_05_006_img.jpg` | redraw | embedded LCM/English self-check localized; source math/relationships preserved |
| 18 | `eip-id1168467267821` | `CNX_BMath_Figure_02_05_026_img-01.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 19 | `eip-id1168468495660` | `CNX_BMath_Figure_02_05_026_img-02.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 20 | `eip-id1168467254295` | `CNX_BMath_Figure_02_05_026_img-03.png` | redraw | embedded LCM/English self-check localized; source math/relationships preserved |
| 21 | `eip-id1168466034886` | `CNX_BMath_Figure_02_05_027_img-01.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 22 | `eip-id1168469780194` | `CNX_BMath_Figure_02_05_027_img-02.png` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 23 | `eip-id1168469780210` | `CNX_BMath_Figure_02_05_027_img-03.png` | redraw | embedded LCM/English self-check localized; source math/relationships preserved |
| 24 | `eip-id1164268626212` | `CNX_BMath_Figure_AppB_012.jpg` | redraw | embedded LCM/English self-check localized; source math/relationships preserved |
| 25 | `fs-id2704082` | `CNX_BMath_Figure_02_05_201.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
| 26 | `fs-id2758794` | `CNX_BMath_Figure_02_05_202.jpg` | math-only | opened; mathematical tokens, lines, circles, shapes or arrows only |
