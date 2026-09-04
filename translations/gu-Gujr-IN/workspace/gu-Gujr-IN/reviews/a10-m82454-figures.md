# A10 m82454 integer figures — frozen review, 2026-08-31

Goal and continuation boundary: complete the figure-localization workflow for all65 source media occurrences in Add and Subtract Integers, within the full Gujarati assignment. A module checkpoint is not completion of the full assignment or workflow. Reconstruct state from source and external logs after compaction; do not trust a summary as evidence. Root owns integration, visible errata, shared status and builds. This worker owns the independently named integer helper, QA script/receipts and this review. No source images, translator files, shared builders, terminology or status were edited; no commits, deletion, large downloads/copies/extractions. C: had13.7GB free before current writes.

Source: `downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82454/index.cnxml`. Every original is in canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media. All65 unchanged originals were actually viewed individually; all65 English source alts were read and compared. Twenty language-bearing originals are redrawn. Forty-five visually verified mathematical-only originals are explicitly enumerated and returnNone. The earlier translator inventory overclassified006a/b/c: their brackets contain7/10/6 numerals only, with no English units word. Peer corrected classification to20/45.

## Canon consulted before, during, and after drawing

Read USER_INSTRUCTIONS_VERBATIM.md and AGENTS.md after recovery. Before this drawing stage, reread all49 current terminology rows and13 admitted examples. During drawing and revision, read actual `downloads/gu-Gujr-IN/gujarati-canon/std6-week1-p16.txt`, then viewed its originalPNG (printedpage34): Q9 compares with <,>,=; Q10 uses ચડતા ક્રમમાં; Q11 uses ઊતરતા ક્રમમાં. OCR's comparison symbols are corrupt, so the actual image is authoritative. The existing source-faithful mathematical signs remain unchanged.

Targeted primary indexed evidence was reconsulted during drawing/render revision, in response to the user's reminder. [વિરોધી સંખ્યા](https://gu.khanacademy.org/math/in-in-class-6th-math-cbse/x06b5af6950647cd2%3Aintegers/x06b5af6950647cd2%3Aintegers-on-the-number-line/v/opposite-of-a-number) supports opposite pairs3/−3 and−4/4 on the number line. [સરવાળા માટે વિરોધી સંખ્યાનું અસ્તિત્વ](https://gu.khanacademy.org/math/in-class-8-math-foundation/x5ee0e3519fe698ad%3Arational-numbers/x5ee0e3519fe698ad%3Aadditive-and-multiplicative-inverse/v/inverse-property-of-addition) was previously read through its indexed transcript; the renewed indexed excerpt states that a number and its opposite sum tozero. [Signed-number missing-value practice](https://gu.khanacademy.org/math/arithmetic/arith-review-negative-numbers/arith-review-add-and-sub-integersss/v/negative-number-practice) indexed transcript was read again during render review:8units left from7 reaches−1, and positive addition moves right. [Negative-number addition](https://gu.khanacademy.org/math/arithmetic/arith-review-negative-numbers/arith-review-add-negatives-intro/v/adding-negative-numbers) indexed transcript explicitly calls distance from0 નિરપેક્ષ મૂલ્ય. Its transcript contains a sign inconsistency in another example, so it is used as terminology evidence only, never numerical authority. These are indexed-readable evidence, not a claim to have opened inaccessible full exercise pages.

Terminology applied: integer પૂર્ણાંક remains distinct from whole number પૂર્ણ સંખ્યા; ઋણ/ધન, સંખ્યારેખા, વિરોધી સંખ્યા, નિરપેક્ષ મૂલ્ય, એકમ, પદાવલી, and imperative મૂકો. Counter is ગણતરીની ચકતી, shortened ચકતી in diagram labels; opposite-sign pair is શૂન્ય બનાવતી જોડી. Zero stays separate from positive/negative categories. Gujarati strings were reread in every rendered redraw. Latin variablesx,y,u,p and all original numbers, grouping and operators remain mathematical notation.

## Implementation and checks

`scripts/localized_a10_integers.py` exposes render_figure(filename,alt,unique_id). It imports only pure helpers/constants from the existing owned localized_place_value helper. All SVG title/marker IDs are derived from unique_id, with no shared/global stylesheet. Font family is Gujarati,'Nirmala UI',sans-serif. Math-only chip rows within otherwise semantic HTML have aria-hidden SVGs because their count/sign is directly provided by visible text and the group alternative. Nontrivial number lines and paired-counter SVGs have localized titles; the outer wrapper keeps the reviewed Gujarati source alternative.

The008a original image itself wrongly says to substitute−8 for−x. This redraw corrects its final variable to x; integration must retain the visible source-ID-keyed erratum fs-id1169754375291. No other source mathematical value/operator is corrected silently. The original007c,011b,012b,013b and other math-only figures remain unchanged, with peer-corrected alternatives. Two additional sourcealts for034b/034d described clockwise rotation; actual arrows exit below-left and mean removal. These were sent directly to the translator and applied as explicit keyed errors. Peer now has20errata entries (19confirmed issues plus zero-category clarification).

Independent source/count checks: all65 files bound to source IDs and SHA256;20 redrawn/45 retained;34uniqueIDs;16resolvedmarker/title references;12blank self-check cells; all8 counter-redraw quantities checked by actualcircle count;6pair-boundary ellipses in026;9 independent signed-arithmetic identities. There is no unmarked multi-letter English in visible redraw text. Every mathematical-only figure was checked for no embedded English, rather than assuming that an alt with English implied image text.

Four preview pages in `build/gujarati-integer-figures/page-1.html` through`page-4.html` were inspected in the in-app browser. All20 actual redraws were viewed at narrow and desktop widths. DOM receipts show375/375 and1265/1265 client/scroll widths on all4 pages with local Gujarati font loaded and zero text/circle/ellipse bounding boxes outside SVG canvases. Additional985px content-width screenshots allowed the full desktop panels to be visible inside the host browser pane. Initial SVG bounds checking caught lower text boxes extending beyond2 canvases; added bottom canvas space (without moving/changing mathematical data) and rechecked with cache-busted URLs. Full-page screenshot stitching was unreliable in the host pane; viewport screenshots and actual DOM bounds were used instead. No clipping, overlap or missing pair boundaries remained. The self-check has all4 outcomes and12blank responses, with explicit column headers repeated per outcome for responsive reading.

Reproduce structural/source QA: `python gu-Gujr-IN/scripts/qa_a10_integers_figures.py`. Receipts are `reviews/a10-m82454-figures-qa.json` and `reviews/a10-m82454-figures-browser.json`. Browser receipt is an actual inspection result, not automatically fabricated by the generator. Human Gujarati educator review remains pending; this checkpoint makes no professional-certification or universal-accessibility claim. Full assignment continues after handoff.

## All65 occurrences and actual visual checks

R = Gujarati nativeSVG/semanticHTML redraw. M = unchanged, visually verified mathematical-only original with Gujarati alternative. Numbering follows source order.

| No. | Filename | Mode | Actual visual / mathematical check |
|---|---|---|---|
|1|`CNX_ElemAlg_Figure_01_03_001_new.jpg`|R|−4…4 equal ticks; left/right brackets, separate upward zero arrow; all3 English category labels translated.|
|2|`CNX_ElemAlg_Figure_01_03_002_new.jpg`|R|−4…4; upper arrow right from−1, lower arrow left from1; larger/smaller translated; teal/red roles kept.|
|3|`CNX_ElemAlg_Figure_01_03_003_new.jpg`|M|Points on every integer−4…4; no embedded English.|
|4|`CNX_ElemAlg_Figure_01_03_004_img_new.jpg`|M|Ticks−20…15; points−20,−4,−1,2,6,9,14; no embedded English.|
|5|`CNX_ElemAlg_Figure_01_03_005_new.jpg`|M|Endpoints−3 and3; two brackets each3; no embedded English.|
|6|`CNX_ElemAlg_Figure_01_03_006a_img_new.jpg`|M|Endpoints−7/7, brackets7/7; center tick unlabelled; no English units word.|
|7|`CNX_ElemAlg_Figure_01_03_006b_img_new.jpg`|M|Endpoints−10/10 with0; brackets10/10; no English units word.|
|8|`CNX_ElemAlg_Figure_01_03_006c_img_new.jpg`|M|Endpoints−6/6 with0; brackets6/6; no English units word.|
|9|`CNX_ElemAlg_Figure_01_03_007a_img_new.jpg`|R|When x=8: introductory Gujarati substitution sentence; second8 red, first8 black.|
|10|`CNX_ElemAlg_Figure_01_03_007b_img_new.jpg`|R|Substitute8 for x;8 red.|
|11|`CNX_ElemAlg_Figure_01_03_007c_img_new.jpg`|M|−(8): only8 red; minus and parentheses black. Corrected alt verified.|
|12|`CNX_ElemAlg_Figure_01_03_007d_img.jpg`|M|−8 black; no English.|
|13|`CNX_ElemAlg_Figure_01_03_008a_img_new.jpg`|R|Original prints wrong final−x. Redraw correctly substitutes−8 for x; root visible erratum fs-id1169754375291 required.|
|14|`CNX_ElemAlg_Figure_01_03_008b_img_new.jpg`|R|Substitute−8 for x; entire−8 red.|
|15|`CNX_ElemAlg_Figure_01_03_008c_img_new.jpg`|M|−(−8): inside−8 red; outside minus/parentheses black.|
|16|`CNX_ElemAlg_Figure_01_03_009_new.jpg`|R|−5,0,5 with two5-unit braces; slanted callout arrows; &#124;−5&#124;=5 and &#124;5&#124;=5; all distance prose translated.|
|17|`CNX_ElemAlg_Figure_01_03_010a_img_new.jpg`|R|Substitute−35 for x;−35 red.|
|18|`CNX_ElemAlg_Figure_01_03_010b_img_new.jpg`|M|&#124;−35&#124;, inner−35 red; bars black.|
|19|`CNX_ElemAlg_Figure_01_03_011a_img_new.jpg`|R|Substitute−20 for y;−20 red.|
|20|`CNX_ElemAlg_Figure_01_03_011b_img_new.jpg`|M|&#124;−(−20)&#124;: both negations within bars; inner−20 red. Corrected alt verified.|
|21|`CNX_ElemAlg_Figure_01_03_012a_img_new.jpg`|R|Substitute12 for u;12 red.|
|22|`CNX_ElemAlg_Figure_01_03_012b_img_new.jpg`|M|−&#124;12&#124;: one pair of bars and black outerminus;12 red. Corrected alt verified.|
|23|`CNX_ElemAlg_Figure_01_03_013a_img_new.jpg`|R|Substitute−14 for p;−14 red.|
|24|`CNX_ElemAlg_Figure_01_03_013b_img_new.jpg`|M|−&#124;−14&#124;: outerminus kept black, inner−14 red. Corrected alt verified.|
|25|`CNX_ElemAlg_Figure_01_03_014_img_new.jpg`|M|One blue/red zero pair with purple boundary;1+(−1)=0.|
|26|`CNX_ElemAlg_Figure_01_03_015a_img_new.jpg`|M|5 positive counters, numeric5 underneath.|
|27|`CNX_ElemAlg_Figure_01_03_015b_img_new.jpg`|M|5+3 positive counters with source group gap and numeric5/3.|
|28|`CNX_ElemAlg_Figure_01_03_015c_img_new.jpg`|R|8 evenly spaced positive counters; positives label translated.|
|29|`CNX_ElemAlg_Figure_01_03_018a_img_new.jpg`|M|5 negative counters, numeric−5 underneath.|
|30|`CNX_ElemAlg_Figure_01_03_018b_img_new.jpg`|M|5+3 negative counters with source group gap and numeric−5/−3.|
|31|`CNX_ElemAlg_Figure_01_03_018c_img_new.jpg`|R|8 evenly spaced negative counters; negatives label translated.|
|32|`CNX_ElemAlg_Figure_01_03_021_img_new.jpg`|R|8 positive and8 negative counters in two panels;5+3=8;−5+(−3)=−8; labels translated.|
|33|`CNX_ElemAlg_Figure_01_03_022_img_new.jpg`|M|1+4 positive counters and result5; no English.|
|34|`CNX_ElemAlg_Figure_01_03_023_img_new.jpg`|M|1+4 negative counters;−1+(−4), result−5; no English.|
|35|`CNX_ElemAlg_Figure_01_03_024a_img_new.jpg`|M|5 red counters, no English.|
|36|`CNX_ElemAlg_Figure_01_03_024b_img_new.jpg`|M|5 red above3 blue, aligned first3; no English.|
|37|`CNX_ElemAlg_Figure_01_03_024c_img_new.jpg`|M|3 red/blue zero pairs enclosed individually;2 red unpaired.|
|38|`CNX_ElemAlg_Figure_01_03_024d_img_new.jpg`|R|2 red counters; negatives label translated.|
|39|`CNX_ElemAlg_Figure_01_03_025a_img_new.jpg`|M|5 blue counters, no English.|
|40|`CNX_ElemAlg_Figure_01_03_025b_img_new.jpg`|M|5 blue above3 red, aligned first3; no English.|
|41|`CNX_ElemAlg_Figure_01_03_025c_img_new.jpg`|M|3 blue/red zero pairs enclosed individually;2 blue unpaired.|
|42|`CNX_ElemAlg_Figure_01_03_025d_img_new.jpg`|R|2 blue counters; positives label translated.|
|43|`CNX_ElemAlg_Figure_01_03_026_img_new.jpg`|R|Left−5+3; right5+−3 exactly as source;5 majority/3 opposite counters each,3 purple pair boundaries each; sign-conclusion labels translated.|
|44|`CNX_ElemAlg_Figure_01_03_027_img_new.jpg`|M|1 red/blue pair plus4 unpairedblue,5blue total. Corrected count alt verified.|
|45|`CNX_ElemAlg_Figure_01_03_028_img_new.jpg`|M|1 blue/red pair plus4 unpairedred,5red total. Corrected count alt verified.|
|46|`CNX_ElemAlg_Figure_01_03_029a_img_new.jpg`|M|5 blue counters, no English.|
|47|`CNX_ElemAlg_Figure_01_03_029b_img_new.jpg`|M|First3 of5blue enclosed with purple arrow exiting left; subtraction model.|
|48|`CNX_ElemAlg_Figure_01_03_030a_img_new.jpg`|M|5 red counters, no English.|
|49|`CNX_ElemAlg_Figure_01_03_030b_img_new.jpg`|M|First3 of5red enclosed with purple arrow exiting left; subtraction model.|
|50|`CNX_ElemAlg_Figure_01_03_031_img_new.jpg`|M|5−3=2 and−5−(−3)=−2;3 removed from each5; purple removal arrows.|
|51|`CNX_ElemAlg_Figure_01_03_032a_img_new.jpg`|M|5 red counters, numeric−5.|
|52|`CNX_ElemAlg_Figure_01_03_032b_img_new.jpg`|M|8 red in5+3 groups,3 blue below final3; corrected count alt verified.|
|53|`CNX_ElemAlg_Figure_01_03_032c_img_new.jpg`|M|8 red in5+3 groups;3blue below enclosed with purple left arrow; corrected count alt verified.|
|54|`CNX_ElemAlg_Figure_01_03_032d_img_new.jpg`|R|8 red counters in5+3 groups; negatives label translated.|
|55|`CNX_ElemAlg_Figure_01_03_033a_img_new.jpg`|M|5 blue counters, no English.|
|56|`CNX_ElemAlg_Figure_01_03_033b_img_new.jpg`|M|8 blue in5+3 groups,3red below final3; corrected count alt verified.|
|57|`CNX_ElemAlg_Figure_01_03_033c_img_new.jpg`|M|8 blue in5+3 groups;3red below enclosed with purple left arrow.|
|58|`CNX_ElemAlg_Figure_01_03_033d_img_new.jpg`|R|8 blue counters in5+3 groups; positives label translated.|
|59|`CNX_ElemAlg_Figure_01_03_034a_img_new.jpg`|M|4 red counters grouped3+1; corrected count/grouping alt verified.|
|60|`CNX_ElemAlg_Figure_01_03_034b_img_new.jpg`|M|1 blue counter inside purple removal oval; arrow exits below-left, not a rotation instruction. Peer correction requested/applied.|
|61|`CNX_ElemAlg_Figure_01_03_034c_img_new.jpg`|M|4 blue counters grouped3+1; corrected spacing alt verified.|
|62|`CNX_ElemAlg_Figure_01_03_034d_img_new.jpg`|M|1 red counter inside purple removal oval; arrow exits below-left, not a rotation instruction. Peer correction requested/applied.|
|63|`CNX_ElemAlg_Figure_01_03_035_img_new.jpg`|M|6−4 and6+(−4) each2; blue positives/red negatives; purple removal arrows. Corrected color alt verified.|
|64|`CNX_ElemAlg_Figure_01_03_036_img_new.jpg`|M|8−(−5)=13 by removing5red from5 addedzero pairs; comparison8+5=13; preserve8+5 spacing.|
|65|`CNX_ElemAlg_Figure_01_03_201_img_new.jpg`|R|4 learning outcomes×3 response columns;12 blank responses preserved in4 responsive semantic tables.|

Frozen source SHA256 `4483b9df8736598af20287450b89cf367728da04c697f85f1abb64bbeffb092f`. Current source-faithful Gujarati CNXML SHA256 `b850b59c479c694202ac4fa6f2efcc4df01a2603c804619eb3f6459f6974cf2b`. Integer helper SHA256 `148d7bf4b3191abcf07b85f4fb9e82bfd072e0a1a9cb26d3d85ab8c0115d0475`.
