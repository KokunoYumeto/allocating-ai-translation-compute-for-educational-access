# A10 m82453 complete figure localization review — 2026-08-31

All50 source images were individually opened and read. `scripts/localized_a10_algebra.py` redraws every14 language-bearing image; its36 explicitly enumerated `VERIFIED_MATH_ONLY` originals return `None`. Unknown names also return `None` and must not be reported as verified. This freezes the figure component, not the full Gujarati assignment. The translator subsequently confirmed final CNXML SHA256 `3bce3c8431ac0056156c1e082ab6d36a4208c17b77534ab7108482ebbe358b30`: all11 image findings are applied, plus a twelfth non-image table-summary erratum discovered by the translator.

Source: `downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82453/index.cnxml`; SHA256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`. Originals are the unchanged files in `downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/`. Helper SHA256: `039d14d013109a7e43dcac74d52b1b6f481a81cca767921fc9b19fb8102dff15`.

## Canon and mathematical language review

Before drafting, reread the source media/alt inventory and translator work log, the latest terminology ledger and initial13 Gujarati canon examples. The preceding addition review included actual Std6 p17/p15 OCR consultation and p17 image inspection; it establishes number/place-value register and arithmetic conventions, not algebra terminology. During this new topic, read the indexed Gujarati transcript of [ચલ, પદાવલિ, અને સમીકરણ](https://gu.khanacademy.org/math/in-class-7-math-foundation/xe6a68b2010f94f8c%3Aalgebra/xe6a68b2010f94f8c%3Aequations/v/variables-expressions-and-equations): variable substitution in x+5 and the explicit expression/equation distinction support ચલ, પદાવલી, કિંમત and સમીકરણ. Only the indexed text actually exposed was read; no claim is made about the full interactive page.

During final review, reread the ledger/example records and the translator’s own algebra decisions. A further primary [બહુપદીનો પરિચય](https://gu.khanacademy.org/math/in-in-grade-9-ncert/xfd53e0255cd302f8%3Apolynomials/xfd53e0255cd302f8%3Apolynomials-in-one-variable/v/polynomials-intro) search exposed its Gujarati transcript. It directly defines સહગુણક as a number multiplying a variable’s power, using10x⁷ and other terms. This was read and sent to the translator as stronger terminology evidence than a title alone. Its noisy transcript arithmetic is not authority for source values. Existing primary indexed power-rule excerpts also use આધાર and ઘાતાંક; the translator independently read a Gujarati exponent article. The targeted search for સજાતીય પદો did not establish a new direct canon witness, so that established translation choice still merits educator review.

Use the agreed terms આધાર, ઘાતાંક, અવયવ, સજાતીય પદો, પદાવલી, તફાવત, ગુણાકારનું પરિણામ and ભાગફળ. Variables a,b,n,x remain Latin mathematical symbols. Natural Gujarati relation words અને and the appropriate possessive suffix replace highlighted English “of/and”; no English grammar is silently inserted into Gujarati. The self-check explicitly retains the source’s English-phrase activity context. The translator owns the separate source-language/English-keyword bridge in module prose.

The coefficient/exponent scopes are explicit MathML:2x² means2 times the square of x, not(2x)²; similarly3x² and10x². This ambiguity was also reported to the translator for alt wording. Source superscripts, dot multiplication, division sign and minus sign are preserved in the corresponding redrawn formulas. Red/teal/green highlights retain group membership with darker colors for legibility.

## Every occurrence and disposition

Every filename below begins `CNX_ElemAlg_Figure_01_02_`. “Original” denotes a visually verified image with no embedded natural-language text; originals and their highlights remain unchanged.

|#|Filename suffix|Media ID|Mode and actual image check|
|---|---|---|---|
|1|001_img_new.jpg|fs-id1170652623871|Original: number line with a left of b; variables and end arrows, no language.|
|2|002_img_new.jpg|fs-id1167269961954|Original: number line with b left of a; variables and end arrows, no language.|
|3|003_img_new.jpg|fs-id1170655219218|SVG + MathML/text redraw: 2³; આધાર arrow targets2, ઘાતાંક arrow targets3; repeated product2·2·2.|
|4|004_img_new.jpg|fs-id1170655111941|SVG + MathML/text redraw: aⁿ; both arrows, aⁿ=a·a·…·a and bracketed n અવયવો.|
|5|005a_img_new.jpg|fs-id1167836282522|Original: 4+3·7, all black. It is an expression, not an equation.|
|6|005b_img_new.jpg|fs-id1167836477496|Original: 4+3·7; 3·7 red, initial4+ black.|
|7|005c_img_new.jpg|fs-id1167833397265|Original: 4+21, all black; expression has no equals sign.|
|8|005d_img_new.jpg|fs-id1167836477509|Original: result25.|
|9|006a_img_new.jpg|fs-id1167836700561|Original: (4+3)·7. Actual dot settles source alt’s garbled operator.|
|10|006b_img_new.jpg|fs-id1167824617198|Original: (4+3)·7; inner4+3 entirely red, including plus; parentheses/dot/final7 black.|
|11|006c_img_new.jpg|fs-id1167836329648|Original: (7)7; first7 red, both parentheses and final7 black.|
|12|006d_img_new.jpg|fs-id1167829808043|Original: result49.|
|13|007b_img.jpg|fs-id1167836598935|Original: 18÷6+4(3), all black.|
|14|007f_img_new.jpg|fs-id1171791418206|Original: 18÷6 and4(3) red; joining+ black.|
|15|007c_img_new.jpg|fs-id1167833349691|Original: 3+4(3); 4(3) red,3+ black.|
|16|007d_img_new.jpg|fs-id1167836622811|Original: 3+12, all black; expression has no equals sign.|
|17|007e_img_new.jpg|fs-id1167829596718|Original: result15.|
|18|008a_img_new.jpg|fs-id1167836287043|Original: 5+2³+3[6−3(4−2)], all black.|
|19|008b_img_new.jpg|fs-id1167836326514|Original: same expression; complete(4−2), including parentheses, red.|
|20|008c_img_new.jpg|fs-id1167836578693|Original: 5+2³+3[6−3(2)]; complete3(2) red.|
|21|008d_img_new.jpg|fs-id1167833142573|Original: 5+2³+3[6−6]; only−6 red, first6 black. Confirmed in magnified original.|
|22|008e_img_new.jpg|fs-id1167824720931|Original: 5+2³+3[0];0 red, brackets black.|
|23|008f_img_new.jpg|fs-id1167836571320|Original: 5+2³+3[0]; complete2³ red.|
|24|008g_img_new.jpg|fs-id1167836363366|Original: 5+8+3[0]; complete3[0] red.|
|25|008h_img_new.jpg|fs-id1167836628989|Original: 5+8+0;5+8 red, final+0 black.|
|26|008i_img_new.jpg|fs-id1167836408301|Original: complete13+0 red.|
|27|008j_img_new.jpg|fs-id1167836321064|Original: result13.|
|28|009a_img_new.jpg|fs-id1167836295066|HTML/MathML redraw: જ્યારે x=5; only5 red.|
|29|009b_img_new.jpg|fs-id1167829597558|Original: 7x−4, all black.|
|30|009c_img_new.jpg|fs-id1167833076771|Original: 7(5)−4; only5 red.|
|31|009d_img_new.jpg|fs-id1167836554298|Original: 35−4.|
|32|009e_img_new.jpg|fs-id1167836507263|Original: result31.|
|33|010a_img_new.jpg|fs-id1167829597755|HTML/MathML redraw: જ્યારે x=1; only1 red.|
|34|010b_img_new.jpg|fs-id1167836492302|Original: 7x−4.|
|35|010c_img_new.jpg|fs-id1167836296392|Original: 7(1)−4; only1 red.|
|36|010d_img_new.jpg|fs-id1167836294733|Original: 7−4.|
|37|010e_img_new.jpg|fs-id1167833014906|Original: result3.|
|38|011a_img_new.jpg|fs-id1167826170152|HTML/MathML redraw: x ની જગ્યાએ4 મૂકો; only4 red.|
|39|011b_img_new.jpg|fs-id1167836526102|Original: 4²; base4 red and exponent2 black.|
|40|012a_img_new.jpg|fs-id1167829692365|HTML/MathML redraw: x ની જગ્યાએ4 મૂકો; only4 red.|
|41|012b_img_new.jpg|fs-id1167836692989|Original: 3ˣ; x remains an exponent variable, not replaced by4 in this source image.|
|42|013a_img_new.jpg|fs-id1169149357522|HTML/MathML redraw: x=4 મૂકો; only4 red.|
|43|013b_img_new.jpg|fs-id1169149089480|Original: 2x²+3x+8; exponent applies only to x.|
|44|014a_new.jpg|fs-id1170655224688|HTML/MathML step1 redraw: one instruction, plain and colored copies of2x²+3x+7+x²+4x+5. Quadratic terms red, linear terms teal, constants green; plus signs black.|
|45|014b_new.jpg|fs-id1170653192952|HTML/MathML step2 redraw: 2x²+x²+3x+4x+7+5. Same groups, with within-group plus signs in group color and joining plus signs black.|
|46|014c_new.jpg|fs-id1170655041754|HTML/MathML step3 redraw: 3x²+7x+12; red/teal/green terms and black joining plus signs.|
|47|015_img_new.jpg|fs-id1170655105929|HTML/MathML four phrases: sum, difference, product and quotient of a/b. Gujarati અને plus possessive suffixes red; operation names bold. Product wording is ગુણાકારનું પરિણામ.|
|48|016_img_new.jpg|fs-id1170655127844|HTML/MathML phrase→spoken operation→17x−5. Variables unchanged; Gujarati relation words red, તફાવત italic.|
|49|018_img_new.jpg|fs-id1170655111048|HTML/MathML phrase→divide instruction→10x²÷7. Superscript applies to x only; Gujarati relation words red, ભાગફળ italic. No stray v before7.|
|50|201_img_new.jpg|fs-id1170655332525|Semantic HTML self-check: all five source skills, three response choices per skill and15 empty response cells. Explicit English-phrase context retained in Gujarati.|

## Exact source-alt findings handed to translator

All findings were sent directly with media IDs/filenames. The translator’s keyed errata JSON contains11 entries at this review checkpoint:

- 005a (`fs-id1167836282522`),005c (`fs-id1167833397265`) and007d (`fs-id1167836622811`) incorrectly call expressions equations; none contains an equals sign.
- 006a (`fs-id1167836700561`) contains a garbled textual multiplication operator; actual image is(4+3)·7.
- 006b (`fs-id1167824617198`) has a red plus sign within4+3; source alt incorrectly says plus black.
- 007f (`fs-id1171791418206`) has a black joining plus, although both18÷6 and4(3) are red; it is not wholly red.
- 008b (`fs-id1167836326514`) highlights both parentheses as well as4−2.
- 008d (`fs-id1167833142573`) highlights−6 including the minus, while the first6 remains black. It does not highlight the whole6−6 subtraction.
- 008f (`fs-id1167836571320`) highlights the complete2³; source alt omitted this instructional emphasis.
- 014a (`fs-id1170655224688`) contains only Step1 and two expression rows. Its description of three instructions/four expressions belongs to the combined014a/b/c sequence, not this image alone.
- 018 (`fs-id1170655111048`) contains10x²÷7 with no stray v preceding7.

The source originals were not modified to repair descriptions. Root must use the translator’s corrected alternatives and expose errata separately. The coefficient-scope wording is a translation refinement, not a newly invented source error. The magnified original highlight review is a small HTML page at `build/gujarati-algebra-figures/source-highlight-review.html`; it scales unchanged originals in the browser without editing raster bytes.

## Checks performed and limits

- All50 source media were dispatched:14 redraws,36 known mathematical-only fallbacks; no unknown source image was accepted as verified.
- Across14 redraws:18 unique generated IDs,6 resolved SVG title/marker references, no duplicate or unresolved ID. No scripts, event handlers, raster embeds or remote content in generated fragments. User-supplied alternatives are escaped; SVG names derive from caller unique IDs.
- The only Latin text tokens in output are mathematical a,b,n,x. All other visible words are Gujarati. Font stack is `Gujarati,'Nirmala UI',sans-serif`; MathML retains accessible variable/exponent structure. Source arithmetic-only figures preserve original red marks untouched.
- Independent arithmetic:4+3·7=25;(4+3)·7=49;18÷6+4(3)=15;5+2³+3[6−3(4−2)]=13;7(5)−4=31;7(1)−4=3. Like-term reduction has coefficient sums2+1=3,3+4=7,7+5=12; initial, reordered and final polynomial expressions agree for five independently chosen x values. No check changes source answers or adds unsupplied solutions.
- All five self-check skill rows and all15 blank response cells are present; the three response labels recur per skill in semantic tables. Live DOM review confirms the captions, headers and blank-cell roles. No data collection or submission behavior is added.
- Three component pages (5+5+4 figures) each measured375px client/scroll width at390×844 configured viewport, with zero figure overflow. Restored desktop measurement is1265px client/scroll for every page, again no overflow. Actual mobile screenshots checked base/exponent arrows and bracket, like-term grouping/wrapping, four Gujarati operation phrases, coefficient scope in the quotient, and self-check layout. Isolated detail pages were used where same-document scrolling screenshots were stale; no layout claim relies on a stale screenshot. The numerical-power sentence was revised to keep punctuation with its final mathematical product. Viewport was reset afterward.
- Ignored small QA artifacts are under `build/gujarati-algebra-figures/`, including the14-figure previews and `qa-results.json`. Full-reader integration, PDF output, native-educator and assistive-technology review remain distinct workflow steps.

No shared dispatcher/build/status, source map, translator file or original image was modified. No large download, deletion or commit was performed. The next assigned work is a separately owned tagged screen-PDF investigation and complete-module implementation.
