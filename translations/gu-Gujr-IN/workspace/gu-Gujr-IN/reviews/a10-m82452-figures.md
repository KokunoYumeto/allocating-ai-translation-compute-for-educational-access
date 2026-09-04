# A10 m82452 Gujarati figure localization — 2026-08-30

All 35 media occurrences have code-native Gujarati redraws in `scripts/localized_a10_whole_numbers.py`. The public entry point is `render_figure(filename, alt, unique_id)`. Every filename in the inventory below returns HTML/SVG; unknown filenames return `None`. Even the visually verified mathematical-only originals are redrawn, avoiding a mixed raster/vector reader. The original source images and CNXML paths remain unchanged. The integrating reader owns visible errata and source links.

Authority: `downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82452/index.cnxml`, SHA256 `0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310`. All 35 original images were individually opened from `downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/`. This review does not substitute alt text for image inspection. The current helper SHA256 is `64440fc38631cd5727aa61ad738818575a698c0cc0e2f8641f121c70a0d31301`.

## Canon consultation and decisions

Before this batch, read the user instructions, terminology ledger, all 13 initial canon example records, the existing A10 review and source/translation. The preceding place-value batch included actual Std5 Week1 p13 and Std6 Week1 p14/p15 image inspection and repeated OCR consultation. Those examples establish સ્થાનકિંમત, એકમ, દશક, સો, and the distinction between an અંક and a સંખ્યા. During final A10 review, reread `terminology.csv`, `canon/examples.csv`, and the actual `std6-week1-p15.txt` OCR. The worked expansion and reverse-expansion headings were checked against the place-value labels. This is a targeted language check; the noisy OCR operators are not mathematical authority.

During factor/LCM drafting, actually read indexed primary Gujarati Khan material:

- [LCM exercise](https://gu.khanacademy.org/math/in-class-7-math-foundation/xe6a68b2010f94f8c:playing-with-numbers/xe6a68b2010f94f8c:hcf-and-lcm/e/least_common_multiple): indexed heading confirms લઘુત્તમ સામાન્ય અવયવી. No claim of a full interactive exercise review.
- [Prime-factorization practice](https://gu.khanacademy.org/math/in-in-grade-10-ncert/x573d8ce20721c073:real-numbers/x573d8ce20721c073:fundamental-theorem-of-arithmetic/v/prime-factorization-exercise): direct open exposed no transcript; exact-title search exposed the Gujarati transcript with 75 and 32. Read that indexed text, supporting અવિભાજ્ય અવયવીકરણ and અવિભાજ્ય અવયવો. Those problems were not copied.
- [Prime numbers](https://gu.khanacademy.org/math/in-in-class-6th-math-cbse/x06b5af6950647cd2:playing-with-numbers/x06b5af6950647cd2:prime-and-composite-numbers/v/prime-numbers): indexed transcript distinguishes 1 and the prime/composite cases. Use અવિભાજ્ય and સંયુક્ત in the table, consistent with the module's definition bridge.

Nearest-place instructions follow the already consulted indexed Khan [nearest hundred](https://gu.khanacademy.org/math/cc-third-grade-math/cc-3rd-place-value-rounding/cc-3rd-grade-rounding/v/rounding-to-the-nearest-100) and [nearest thousand](https://gu.khanacademy.org/math/in-in-class-6th-math-cbse/x06b5af6950647cd2:knowing-our-numbers/x06b5af6950647cd2:estimating-to-nearest-ten-hundred-or-thousand/v/rounding-whole-numbers-2) wording: સૌથી નજીકના સોમાં ફેરવતાં, with the appropriate place substituted. Direct pages did not expose transcripts; the titles/excerpts actually read are indexed-readable evidence, not a full-page claim. Keep source international three-digit groups and મિલિયન/બિલિયન/ટ્રિલિયન. The 073 group remains 073, read તોતેર; leading empty places remain empty rather than zero. Label source LCM as લઘુત્તમ સામાન્ય અવયવી (લ.સા.અ.) in diagrams; the source abbreviation remains explained by the module prose.

## Complete occurrence inventory

Every filename below has prefix `CNX_ElemAlg_Figure_01_01_`. “HTML” means semantic text/table/grouping redraw; “SVG” includes its accessible HTML wrapper. Source order is retained.

| # | Filename suffix | Media ID | Mode and exact check |
|---|---|---|---|
|1|001_new.jpg|fs-id1170655233864|SVG number line + HTML labels. Equal ticks 0–6, points at every tick, two end arrows; smaller left/larger right translated.|
|2|002_new.jpg|fs-id1170655200451|HTML place tables for 5,278,194. All 15 places/five periods retained, including leading blanks. Reuses the inspected matching A00 chart.|
|3|003_img_new.jpg|fs-id1170655112880|HTML place tables for 63,407,218. Same full-place check; distinct source digits retained.|
|4|004_new.jpg|fs-id1170655154806|HTML number-to-word groups 74 / 218 / 369. Gujarati words match 74,218,369; period-to-word pairing retained.|
|5|005_img_new.jpg|fs-id1170655155229|HTML five-group words for 8 / 165 / 432 / 098 / 710. The 098 group is not shortened in the digits.|
|6|022_img_new.jpg|fs-id1170655154739|HTML word-to-digit slots for 9 / 246 / 073 / 189. Full four-group actual image used; source alt's two-row-only description corrected by owner.|
|7|008a_new.jpg|fs-id1170655194626|HTML procedure step 1. 23,658, target hundreds digit 6 and complete two instruction cells.|
|8|008b_new.jpg|fs-id1170655028499|HTML step 2. Arrow relation still targets 6; decision digit 5 is underlined.|
|9|008c_new.jpg|fs-id1170654984954|HTML step 3. Both yes/no branches and add 1 to 6. No zero replacement is shown at this stage in the actual original.|
|10|008d_new.jpg|fs-id1170655130142|HTML step 4. Actual intermediate 23,758 preserved; 5 and 8 identified for replacement by zeros; final sentence gives 23,700.|
|11|009a_img_new.jpg|fs-id1167831970141|HTML target label. 103,978, hundreds 9, no underline.|
|12|009b_img_new.jpg|fs-id1167834196335|HTML target/underline. Target 9; actual underlined decision digit 7 retained.|
|13|009c_img_new.jpg|fs-id1167831823617|HTML carry action. 9 + 1 = 10, replace 9 by 0 and carry 1; replace 7/8 by zeros; result 104,000.|
|14|010a_img_new.jpg|fs-id1167835305151|HTML target/underline. Thousands target 3; actual underlined decision digit 9, not 3.|
|15|010b_img_new.jpg|fs-id1167834132960|HTML action. 3 + 1 = 4, replace 3 by 4; replace 9/7/8 by zeros; result 104,000.|
|16|011a_img_new.jpg|fs-id1167835287582|HTML target/underline. Ten-thousands target 0; decision digit 3 is underlined.|
|17|011b_img_new.jpg|fs-id1167835283071|HTML numeric 100,000. Original visually confirmed mathematical-only.|
|18|012_img_new.jpg|fs-id1170655216065|HTML six-column numeric products. 2,4,6,8,10,12 and 2·1 through 2·6; product-expression row preserves red emphasis. Original mathematical-only.|
|19|013_img_new.jpg|fs-id1170654944087|HTML six-column numeric products. 3,6,9,12,15,18 and 3·1 through 3·6; same emphasis. Original mathematical-only.|
|20|014_img_new.jpg|fs-id1170655160732|HTML equation 8·9=72, grouped factor/product labels translated as અવયવો and ગુણાકારનું પરિણામ.|
|21|015_img_new.jpg|fs-id1170655206126|Two HTML tables, 2–10 and 11–19. Each has three columns, header + nine data rows. All factor sets and prime/composite classifications checked.|
|22|016a_new.jpg|fs-id1170655194612|HTML instructions + SVG first tree: 48→2×24. No prime circles in step 1.|
|23|016b_new.jpg|fs-id1170655105895|HTML instructions + SVG same tree; only leaf 2 circled in step 2.|
|24|016c_new.jpg|fs-id1170654967999|HTML instructions + two SVG trees. Partial 24→4×6, then 4→2×2 and 6→2×3; initial leaf 2 is circled, not underlined; all final prime leaves circled.|
|25|016d_new.jpg|fs-id1170655089548|HTML step 4 and 48=2·2·2·2·3. Repeated primes retained.|
|26|017_img_new.jpg|fs-id1167835262266|SVG tree 252→12×21;12→2×6;6→2×3;21→3×7. All five prime leaves circled. Original mathematical-only.|
|27|018_img_new.jpg|fs-id1170655189662|HTML lists for 12/18 through108; common36,72,108 red, LCM36 teal; source ellipses retained.|
|28|019_img_new.jpg|fs-id1167832051958|HTML lists for15 through120 and20 through160. Only60 highlighted in both rows, as in actual original;120 not newly highlighted. Original mathematical-only.|
|29|020a_new.jpg|fs-id1170655199720|HTML step 1 + SVG trees in source order18 then12:18→3×6→2×3 and12→3×4→2×2. Prime leaves circled.|
|30|020b_new.jpg|fs-id1170654905180|HTML step 2 + SVG prime alignment.12=[2,2,3,blank];18=[2,blank,3,3]. Divider retained; no arrows yet.|
|31|020c_new.jpg|fs-id1170655083625|HTML step 3 + SVG same four columns with four downward arrows to2·2·3·3. Each arrow begins at an occupied source-factor row.|
|32|020d_new.jpg|fs-id1170654935281|HTML step 4, translated LCM result36.|
|33|021a_img_new.jpg|fs-id1167835321942|SVG alignment24=[2,2,2,3,blank];36=[2,2,blank,3,3], five arrows to2·2·2·3·3. Actual24/36 figure overrides copied12/18 alt error via owner's erratum.|
|34|021b_img_new.jpg|fs-id1167832116015|HTML translated LCM label and numeric result72. Original contains English abbreviation LCM.|
|35|201_img_new.jpg|fs-id1170655207116|HTML self-check. All three source objectives, all three response labels and all nine empty response cells retained. Responsive three-objective tables replace the wide raster table; no collection/submission behavior.|

## Actual-image discrepancies sent to translation owner

The A10 translator received exact filenames and source IDs before freezing its source-bound alt/errata edits. New findings were the full four-group 022 diagram, absence of zero-replacement brackets in 008c, actual 23,758 intermediate in 008d, missing underline7 in009b, wrong underline3 instead of9 in010a, missing underline3 in011a, circled rather than underlined initial2 in016c, and the actual pair of nine-row tables in015. The 009c hundreds carry,010b thousands action and021a24/36 copied-alt problems were independently verified against originals as well. Enlarged underline evidence is at the ignored local review path `build/gujarati-a10-figures/underline-review.png`. The translator confirmed18 keyed errata total and its frozen module SHA256 `cb4648e936ac87d2f4fec59cd2e615187420148c2f865b5121c31c26a33137be`. No translator-owned file was modified by this figure worker.

## Structural, mathematical and visual checks

- Rendered every media entry from the actual Gujarati CNXML, not a manually sampled list. All35 returned redraws; unknown filenames returned `None`. The final ignored QA record is `build/gujarati-a10-figures/qa-results.json`.
- Across all35:48 unique generated IDs,21 marker/ARIA references, every reference resolved, zero duplicate IDs. `_uid(unique_id)` namespaces every SVG title/marker. Distinct caller strings that sanitize alike receive distinct hashes. The caller should pass its distinct redraw suffix to avoid colliding with an outer wrapper.
- Zero visible Latin words in generated figure text; no scripts, event handlers, raster embeds or external references. User-provided alternative text is escaped. Font stack is `Gujarati,'Nirmala UI',sans-serif`. Semantic HTML wrappers have Gujarati accessible names; factor-tree and alignment SVG titles describe the actual numerical relationships. Decorative line SVGs are hidden from accessibility APIs.
- Each generated tree asserts that a parent's two child values multiply to the parent and each circled value is prime. Independent leaf-product checks give48=2⁴·3 and252=2²·3²·7. Each LCM row's occupied factors multiply to its source number; the resulting products independently equal36 and72. Independently verified the complete positive divisor sets for2–19 and prime set2,3,5,7,11,13,17,19.
- Independent integer rounding checks:23,658→23,700 to100;103,978→104,000 to100 and1000;103,978→100,000 to10000. These checks use half-up whole-number rounding rather than language/runtime tie-to-even behavior.
- Final source-image review reopened008c,008d,009c,010b,018,019,020b,021a and201 alongside the live redraws. Verified exact rounding callouts, the intermediate value, blank prime-alignment columns, source ellipses, highlighted common multiples, and self-check labels/cells.
- Five component preview pages each contain seven redraws. Browser measurement at configured390×844 (375px document content after scrollbar) returned375px client/scroll width on every page, with zero figure overflow. At the restored desktop viewport, all five returned1265px client/scroll width and zero figure overflow. Actual mobile viewport screenshots were inspected for rounding panels, underlines, the prime/composite table, both48 trees, the252 tree, both LCM alignments and self-check; Gujarati labels, prime circles and arrow endpoints are legible without overlap. Earlier desktop screenshot scaling/cropping does not match live DOM bounds, so it was not used to assert a layout defect. Viewport was reset after review.

This freezes the figure helper and its component review, not the full Gujarati assignment. Root integration, full-reader checks, native Gujarati educator review and assistive-technology testing remain separate work. There were no large downloads, no raster modifications, no deletes, and no shared build/status edits in this batch.
