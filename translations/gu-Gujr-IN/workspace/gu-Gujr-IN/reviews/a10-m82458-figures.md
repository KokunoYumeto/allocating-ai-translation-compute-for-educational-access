# A10 m82458 figure workflow

Active bounded goal,2026-08-31: independently inspect all49source images and localize all28language-bearing figures for Decimals; retain21unchangedmath-onlyoriginals onlyafteractualverification. Completewholemodulefigureworkflowincludingsource/canonreads,Gujarati labels/steps/arrows/highlights/math,sourcepin/arithmetic/accessibilityQA,actualphone/desktopreviewandfreezehandoff. RootownsfullsourceCNXML/27errata/sharedrenderer; ownonlynewhelper,QA,previewsandreview. No sharededits,commits,pushes,largeacquisitionorcleanup. Lastdisk9.19GBfree;smallwritesonly. Compactioncanmislead:reconstructfromactualfiles,notmemoryalone. Fullassignmentcontinuesaftermodule; nextrootqueue5m81272then4m81273.

Actuallyreadpreparation: fulltranslatorreviewandcurrentinventoryheader. Englishauthority downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82458/index.cnxml SHA678dc0c3ae2aad0192c0314395541720d6c6eb97f56d2f4d169f056fe1e630cb; GuSHAe67160df3a56b3724efed9dce81e2120f1dfd21413c6ccf2a42b3432f89cc309. Media49/28language21math; source179exercises/115solutions/64omissions aretranslator-owned. Sourceimages/mathvaluesratherthanalttextdetermineactualdiagramcontent. Sourcevisiblecorrectionsstayexplicitrootnotes; donotsilentlychangeformulas.

Canonworkflow: initial13example/style/terminologyregisterandStd6p16OCRthenPNGactuallyreadinthecontinuousprecedingmodules; nowreadprimaryindexeddecimalplacevalue/naming/percent conversion evidence relevanttothisunitbefore/duringdrawing. Existingtermsદશાંશચિહ્ન,શતાંશ,સહસ્રાંશ,દસ-સહસ્રાંશ,લક્ષાંશneedexplicitfractionvaluesandmustnotborrowEnglish-thmorphologyasGujarati. Reader Englishand/thdiscussionremainscontextualsourcecontent. Roundingnear-placewordingfollowsattestedનજીકના…માંફેરવો with clearplacefractionvalues. Revisitactualcanon/sourceinrevisionandrenderingandloglimits,notjustgatherlinks.

Nextactions: read49actualsourcealts+all28Gulabelmaps/27errataandrelevantIndonesiancontext; independentlyview49originalsboundedbatches; implementall28nativeHTML/MathML/SVGwithnamespaceIDs; preservevalues4.3,roundingdigits/decisionarrows,negativeproducts/quotients/percent shifts; testsbindall49binaryhashesandcorrectequations. Alllanguage-bearingfiguresmustbedrawn,noselfcheck-onlycompletionclaim. Prior m81271helperisfrozenroot-ownedwithpending032equality-descriptionclarificationrecordedthere.

2026-09-01 source-state correction during actual-image inspection: independently found013a/014a alt/erratum IDs swapped; compared both originals andcurrentGuXML,notified translator/root. Translator moved013a correction to eip-id1169749465627, restored014a actual25.65÷0.06/two-right-shifts at eip-id1169751952546, and regenerated frozenCNXML/inventory/review. Final helper/QA bindnewGuSHA9ce1aa6b189fa8b115ce88f921a609b24583ae13fa2470100212f6d9682270a0; initiale671… remains only a superseded discovery boundary.

## Final source, canon and original-image review

On revision I reread `AGENTS.md`, the verbatim user instructions, the source XML descriptions for the representative 001/004c/005c/006c/010c/012/013a/014a/016/017/018/201 set, the frozen Gujarati counterparts, all27 keyed errata, `terminology.csv` and the admitted `examples.csv`. This confirms the established `સ્થાનકિંમત` register and the concrete rounding wording `નજીકના …માં ફેરવવું`; no old withdrawn objective-rank claim is used here. I also reread the translator's recorded primary indexed Khan Gujarati decimal-place-value, decimal-word-form and percent-conversion excerpts. Only indexed-readable evidence is claimed: the place-value transcript discusses 973 and the decimal point/ones/tens/hundreds; the word-form result covers decimal/fraction wording; the percent article states that percent, fraction and decimal are three ways of writing a number. Direct-page or exact `આવર્ત દશાંશ` attestation is not claimed. The authored recurring-decimal wording therefore remains a clear provisional explanation for educator review.

All49 actual canonical originals were independently opened rather than accepted from alt text. The final review reopened the twelve representative files listed above at original resolution. It confirmed the 001 twelve-column place-value relationship, 004c/005c/006c decision arrows, 010c left-shifted partial product, the two arcs in 012, the distinct tiny 013a/014a mathematics, the color-coded place names in016, the long-division rules in017/018 and the 5-by-3 self-check response grid. The redraws preserve source numbers, signs, decimal positions, operators, color relationships and blank cells. The 21 originals returned as `None` contain only mathematical tokens/arrows; the review does not treat source alt text as proof of that classification.

## Implementation decisions

- `localized_a10_decimals.py` exposes exactly `render_figure(filename, alt, unique_id)`. It returns native semantic HTML/MathML/SVG for28 language-bearing assets and `None` for the21 actually verified mathematical-only originals.
- The place-value chart is a semantic12-column table with an accessible label. At phone size its own region scrolls horizontally; the page itself does not. The caption is sticky so the Gujarati subject remains visible while the user scrolls the table.
- Rounding diagrams retain the target digit, inspected digit, add/do-not-add target and exact deleted suffix as separate SVG data hooks. Source values18.379,18.38,18.4 and18 are unchanged.
- The 010d multiplication keeps36675 and12225, visibly shifts the second partial product one place left, and restores the decimal point only in15.8925.
- The 012 diagram uses two separate W-shaped shift arcs, matching the actual original. The 017/018 redraws use the source long-division top bar and short subtraction rules; the recurring block names120 and100 once each and leaves the repeated arrows visible, then gives the overbar on54.
- SVG marker IDs are constructed from `unique_id`; the source-bound QA found47 unique IDs and resolved all22 references. The self-check redraw is five semantic tables with15 explicitly labelled blank response cells.

## QA and rendering

`qa_a10_decimal_figures.py` binds the English source SHA `678dc0c3ae2aad0192c0314395541720d6c6eb97f56d2f4d169f056fe1e630cb`, frozen Gujarati SHA `9ce1aa6b189fa8b115ce88f921a609b24583ae13fa2470100212f6d9682270a0`, every media ID/path and every original binary SHA. It passes49 media,28 redraws,21 mathematical-only originals,47 unique SVG IDs,22 resolved references,15 self-check blanks and15 independent mathematical/model checks. Final helper SHA is `a82b889b5c34e49b3fe7723cbc03a616655a935990c3d866bfe2b29e935983f2`.

The actual browser review covered all four preview pages and all28 redraws by normal scrolling at390x600 and1000x600. Final geometry was repeated at390x600 and1280x720: document widths were375/375 and1265/1265 on every page. Gujarati/Nirmala font checks passed, localized figure bodies had zero multi-letter Latin-word hits, every SVG reference resolved and IDs stayed unique. On phone only the 001 table has intentional local overflow (317client/980scroll); both ends were actually reviewed. The browser receipt is `reviews/a10-m82458-figures-browser.json`.

The first automated passes exposed reviewable drawing mistakes before freeze: the initial 004c step carried an extra place label, 006c lacked the explicit no-add arrow, 012 used a generic down symbol, and the first long-division draft used full-width rules. Each was corrected against the original image and re-rendered; no source number or operation changed. No uncertainty remains about the encoded arithmetic or visual relationships. Exact stylistic/editorial approval of the provisional recurring-decimal prose remains outside this technical figure review.

## Complete 49-occurrence inventory

The table below is generated from the source-bound QA receipt. `redraw` means language-bearing source art replaced by Gujarati native markup; `math-only` means the original was actually inspected and retained.

| # | Source media ID | Filename | Mode | Actual-image check |
|---:|---|---|---|---|
| 1 | `fs-id1170654939786` | `CNX_ElemAlg_Figure_01_07_001_new.jpg` | redraw | labels: Place Value; whole/decimal place names |
| 2 | `fs-id1170655232620` | `CNX_ElemAlg_Figure_01_07_002a_new.jpg` | redraw | labels: Step1 name left-handnumber;four |
| 3 | `fs-id1170654238417` | `CNX_ElemAlg_Figure_01_07_002b_new.jpg` | redraw | labels: Step2 and;fourand |
| 4 | `fs-id1170654235434` | `CNX_ElemAlg_Figure_01_07_002c_new.jpg` | redraw | labels: Step3 name right-handnumber;fourandthree |
| 5 | `fs-id1170654221344` | `CNX_ElemAlg_Figure_01_07_002d_new.jpg` | redraw | labels: Step4 decimalplace;fourandthreetenths |
| 6 | `fs-id1170654903748` | `CNX_ElemAlg_Figure_01_07_003a_new.jpg` | redraw | labels: Step1 locateand/namewholepart;fourteenandtwentyfourthousandths |
| 7 | `fs-id1170654048412` | `CNX_ElemAlg_Figure_01_07_003b_new.jpg` | redraw | labels: Step2 neededplaces;tenths/hundredths/thousandths |
| 8 | `fs-id1170654048180` | `CNX_ElemAlg_Figure_01_07_003c_new.jpg` | redraw | labels: Step3 finaldigitinlastplace |
| 9 | `fs-id1170652616660` | `CNX_ElemAlg_Figure_01_07_003d_new.jpg` | redraw | labels: Step4 zeros;fourteenandtwentyfourthousandths |
| 10 | `fs-id1170655218662` | `CNX_ElemAlg_Figure_01_07_004a_new.jpg` | redraw | labels: Step1;hundredthsplace |
| 11 | `fs-id1170653985218` | `CNX_ElemAlg_Figure_01_07_004b_new.jpg` | redraw | labels: Step2;hundredthsplace |
| 12 | `fs-id1170653901496` | `CNX_ElemAlg_Figure_01_07_004c_new.jpg` | redraw | labels: Step3 conditional/add1/delete |
| 13 | `fs-id1170653744228` | `CNX_ElemAlg_Figure_01_07_004d_new.jpg` | redraw | labels: Step4 rewrite/roundingresult |
| 14 | `eip-id1169752964044` | `CNX_ElemAlg_Figure_01_07_005a_img_new.jpg` | redraw | labels: tenthsplace |
| 15 | `eip-id1169752799574` | `CNX_ElemAlg_Figure_01_07_005b_img_new.jpg` | redraw | labels: tenthsplace |
| 16 | `eip-id1169750840488` | `CNX_ElemAlg_Figure_01_07_005c_img_new.jpg` | redraw | labels: add1/delete |
| 17 | `eip-id1169750591270` | `CNX_ElemAlg_Figure_01_07_005d_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 18 | `eip-id1169754058794` | `CNX_ElemAlg_Figure_01_07_006a_img_new.jpg` | redraw | labels: onesplace |
| 19 | `eip-id1169754058811` | `CNX_ElemAlg_Figure_01_07_006b_img_new.jpg` | redraw | labels: onesplace |
| 20 | `eip-id1169754362233` | `CNX_ElemAlg_Figure_01_07_006c_img_new.jpg` | redraw | labels: donotadd1/delete |
| 21 | `eip-id1169754362250` | `CNX_ElemAlg_Figure_01_07_006d_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 22 | `eip-id1169754130042` | `CNX_ElemAlg_Figure_01_07_009a_img_new.jpg` | redraw | labels: 1place/2places |
| 23 | `eip-id1169753944283` | `CNX_ElemAlg_Figure_01_07_009b_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 24 | `eip-id1169753944299` | `CNX_ElemAlg_Figure_01_07_009c_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 25 | `eip-id1169753944316` | `CNX_ElemAlg_Figure_01_07_009d_img_new.jpg` | redraw | labels: 2places/3places |
| 26 | `eip-id1169752872718` | `CNX_ElemAlg_Figure_01_07_010b_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 27 | `eip-id1169750874908` | `CNX_ElemAlg_Figure_01_07_010c_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 28 | `eip-id1169753269067` | `CNX_ElemAlg_Figure_01_07_010a_img_new.jpg` | redraw | labels: 1place/3places |
| 29 | `eip-id1169753284625` | `CNX_ElemAlg_Figure_01_07_010d_img_new.jpg` | redraw | labels: 4places |
| 30 | `eip-id1169753258712` | `CNX_ElemAlg_Figure_01_07_011_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 31 | `eip-id1169752908904` | `CNX_ElemAlg_Figure_01_07_012_img_new.jpg` | redraw | labels: Thereare2zerosin100/movedecimal2placesright |
| 32 | `eip-id1169749465627` | `CNX_ElemAlg_Figure_01_07_013a_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 33 | `eip-id1169754029608` | `CNX_ElemAlg_Figure_01_07_013b_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 34 | `eip-id1169751952546` | `CNX_ElemAlg_Figure_01_07_014a_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 35 | `eip-id1169751952565` | `CNX_ElemAlg_Figure_01_07_014b_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 36 | `eip-id1169754122161` | `CNX_ElemAlg_Figure_01_07_015_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 37 | `eip-id1169752926445` | `CNX_ElemAlg_Figure_01_07_016_img_new.jpg` | redraw | labels: tenths/hundredths/thousandths |
| 38 | `fs-id1170654966693` | `CNX_ElemAlg_Figure_01_07_017_img_new.jpg` | redraw | labels: so |
| 39 | `fs-id1170654982890` | `CNX_ElemAlg_Figure_01_07_018_img_new.jpg` | redraw | labels: Divide43by22;120repeats;100repeats;patternandquotientrepeat;so |
| 40 | `eip-id1169749852706` | `CNX_ElemAlg_Figure_01_07_019_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 41 | `fs-id1170655166487` | `CNX_ElemAlg_Figure_01_07_023_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 42 | `eip-id1169750795982` | `CNX_ElemAlg_Figure_01_07_020a_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 43 | `eip-id1169750875596` | `CNX_ElemAlg_Figure_01_07_020b_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 44 | `eip-id1169753258746` | `CNX_ElemAlg_Figure_01_07_020c_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 45 | `fs-id1170654985014` | `CNX_ElemAlg_Figure_01_07_021_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 46 | `eip-id1169750875648` | `CNX_ElemAlg_Figure_01_07_022a_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 47 | `eip-id1169753320625` | `CNX_ElemAlg_Figure_01_07_022b_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 48 | `eip-id1169753184552` | `CNX_ElemAlg_Figure_01_07_022c_img_new.jpg` | math-only | opened; mathematical tokens/arrows only |
| 49 | `fs-id1170655065300` | `CNX_ElemAlg_Figure_01_07_201_img_new.jpg` | redraw | labels: selfcheckheaderandall5objectives |

## Root integration — 2026-09-01

Root connected `render_figure` to the shared library renderer and rebuilt the complete m82458 reader without changing the frozen Gujarati CNXML. Source-bound figure QA, deterministic library QA and actual full-reader browser checks pass:49media occurrences split exactly28Gujarati redraws/21verified math-only originals,15self-check cells remain blank, and document geometry is375/375 at390px and1250/1250 at1265px. See `reviews/frozen-source-integration-2026-09-01-browser.json`.
