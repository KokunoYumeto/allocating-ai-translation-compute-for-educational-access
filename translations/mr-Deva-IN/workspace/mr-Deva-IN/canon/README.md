# Working Marathi canon

This is a small linguistic/reference canon, distinct from the English canonical translation sources. Sixteen example/concept locators are the starting set, not sixteen separate books. It is consulted during drafting, revision and QA; see CONSULTATIONS.md. This is not a training dataset.

## Readable witnesses

- **BB8**: Maharashtra State Bureau of Textbook Production and Curriculum Research, *गणित, इयत्ता आठवी*, Marathi medium. [Official PDF](https://books.ebalbharati.in/pdfs/801020004.pdf). Downloaded whole PDF, 132 physical pages. Printed page p corresponds to physical PDF page p+10. Selected pages OCRed with Tesseract `mar+eng`, then rendered pages inspected. Legacy font encoding makes raw text extraction unreliable. OCR also confuses mathematical symbols: the page image, not OCR, governs formulas. Source PDF, images and OCR stay under ignored `downloads/mr-Deva-IN/canon/`. No textbook pages are redistributed here.
- **MV-F**: गणेश कडू, “फलन (Function)”, Marathi Vishwakosh, 2019-08-31; reviewer विनायक जोशी. [Entry](https://marathivishwakosh.org/21979/). Prose read using the web reader. Local HTTP acquisition failed, so it is not counted as a downloaded HTML artifact. Formulas in the web extraction are image placeholders; the selected witnesses below use readable prose only. Do not treat missing formulas as read.

## Starting set (locators, not reproduced passages)

| ID | Witness / printed page | Example or concept | Draft use |
|---|---|---|---|
| C01 | BB8 p2, example 1 | Positive fraction comparison; numerator/denominator wording | Fraction simplification |
| C02 | BB8 p3, example 2 | Negative versus positive comparison | Sign explanations |
| C03 | BB8 p3, example 3 | Comparing two negatives | Distinguish sign and magnitude |
| C04 | BB8 p3, example 4 | Equivalent fractions | Same value, different form |
| C05 | BB8 p24, example 1 | Positive binomial expansion | Distribution steps |
| C06 | BB8 p24, example 2 | Mixed-sign binomial expansion | Preserve parentheses |
| C07 | BB8 p24, example 3 | Difference-of-squares expansion | Coefficients and signs |
| C08 | BB8 p24, example 4 | Fractional binomial coefficients | Fraction-to-algebra bridge |
| C09 | BB8 p24, example 5 | Two negative constants | Positive product explanation |
| C10 | BB8 p29, opening example 1 | Common factor of two terms | Factors versus additive terms |
| C11 | BB8 p29, worked example 1 | Quadratic factorization and coefficient language | सहगुणक; reason beside step |
| C12 | BB8 p75, example 1 and preceding definition | Equation solution and same-side operations | उकल and शून्येतर wording |
| C13 | BB8 p76, example 1(iii), methods I–II | Fractional linear equation, two valid methods | Explicit operation on both sides |
| C14 | MV-F, function-definition prose | Exactly-one correspondence | फलन and uniqueness |
| C15 | MV-F, paragraph following definition | Domain/codomain naming | प्रांत/अधिक्षेत्र; सहप्रांत |
| C16 | MV-F, final constant-function paragraph | Many inputs may share an output | Not one-to-one by default |

## Topic-specific addition for MR-BRIDGE-002

| ID | Witness / locator | Example or concept | Draft use |
|---|---|---|---|
| C17 | MV-F, opening dependence paragraph | An input quantity and a quantity depending on it; स्वतंत्र / अवलंबित | Explain independent/dependent roles in an email-count model |

This addition makes 17 locators. On 2026-08-30 a fresh web search returned the readable opening, definition and constant-function prose; direct page open again failed. No local HTML acquisition or reading of the page's image-only formulas is claimed. The adjective अवलंबित is witnessed; the full classroom term अवलंबी चल remains provisional.

## Topic-specific additions for diagram practice

| ID | Witness / locator | Example or concept | Draft use |
|---|---|---|---|
| C18 | Marathi Vishwakosh, [आलेख](https://vishwakosh.marathi.gov.in/24316/), जात्याक्ष आलेख prose and coordinate construction | Horizontal/vertical axes; ordered सहनिर्देशक | Graph reading while retaining source x/y symbols |
| C19 | Marathi Vishwakosh, [फलन](https://vishwakosh.marathi.gov.in/27548/), opening definition and variable paragraphs | Actual-image set called कक्षा; domain/codomain and variable-name variants | Range/codomain distinction; record synonym without silent terminology replacement |

These additions brought the set to 19 locators. Relevant prose was actually read on 2026-08-30; later direct reopen failures were supplemented by readable search results. No local HTML acquisition or reading of missing image formulas is claimed. C18's context-specific line-joining example is not applied to isolated finite relations. Only the selected C19 definition/term passages are used, not its unrelated advanced assertions.

## Topic-specific addition for absolute value and braces

| ID | Witness / locator | Example or concept | Draft use |
|---|---|---|---|
| C20 | Marathi Vishwakosh, [गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/), arithmetic notation rows for vertical bars and braces | केवल मूल्य / चिन्ह निरपेक्ष मूल्य; महिरपी कंस | Absolute-value mapping and evaluations; explicit repair of a missing set brace |

There are now 20 locators. The unit-005 drafting agent read the relevant rows directly; the primary agent and unit-006 independent reviewer subsequently read actual search-reader text after direct-open failures. The primary agent refreshed both relevant rows on 2026-08-31 during final QA. This is a narrow terminology witness, not a claim to adopt or verify the entire advanced notation article. No local HTML download is claimed.

## Topic-specific addition for graph shapes

| ID | Witness / locator | Example or concept | Draft use |
|---|---|---|---|
| C21 | Marathi Vishwakosh, [गणितीय प्रतिरूपे](https://vishwakosh.marathi.gov.in/21277/), शंकुच्छेद paragraph | अन्वस्त paired with पॅराबोला; विवृत्त paired with लंबवर्तुळ | Parabola/ellipse names in the012 vertical-line-test figures |

There are now21 locators. The012 writer read the actual paragraph while revising; the primary agent independently retrieved and read it on2026-08-31 before adding this record. Only these two shape-name equivalences are used. The full phrase उभ्या रेषेची कसोटी is an explicitly authored, provisional classroom choice, not attested by C21 or by the axis-orientation prose in C18. No new PDF acquisition, OCR, local HTML witness or review of the article's unrelated models/images is claimed.

Terms beyond these witnesses remain provisional. मूल्यसंच is the established working choice; C19 attests the synonym कक्षा, not that exact working word. आदान, प्रदान, प्रतिस्थापन and later calculus vocabulary need further topic-specific witnesses. No claim of exhaustive regional terminology authority or native-speaker review is made.

On2026-08-31 the primary agent extended the actual C20 reading to its open, closed and half-open/half-closed interval rows through fresh readable official search results. Those rows attest अंतराल and support T030; the full compound अंतराल-संकेतलेखन remains authored. Direct C20 and proposed article32824 opens failed502. Article32824 is not added as a read C22; the catalog remains21 locators. See the consultation log for stage and access limits.

## Topic-specific addition for line slope

| ID | Witness / locator | Example or concept | Draft use |
|---|---|---|---|
| C22 | Marathi Vishwakosh, [भूमिती](https://vishwakosh.marathi.gov.in/28194/), रेषेचा उतार व दोन रेषांमधील कोन paragraph | उतार; equal slopes for parallel lines and product −1 for perpendicular lines in the finite-slope setting | Slope review and following line-equation translation; preserve the separate vertical-line exception |

There are now22 locators. On2026-08-31 the primary agent actually read the complete selected slope paragraph through fresh official search-reader text, including its reference-axis context. An oversized initial result was truncated; the relevant paragraph was retrieved again and read in a bounded excerpt before this record was added. On2026-09-01 primary refreshed the same official entry and read the passage explicitly using `संपाती`, `एकमेकींना छेदणाऱ्या रेषा` and `समांतर रेषा`; those three narrow line-relation terms are now supported along with T043 उतार. This does not attest every classroom compound, unseen image formula, the full system-classification vocabulary or the entire geometry article. The failed interval candidate32824 remains unregistered. See CONSULTATIONS.md for concrete effects and limits.

For the019 inequality topic, primary actually read the complete C18 “असमांचे आलेख” paragraph through fresh official search-reader text on2026-08-31. It supports the narrow terms असमा and छायांकित (T044/T045), not the entire compound रेषीय असमा or the separate sign-reversal rule. This extends an existing locator rather than increasing the22-locator count. See CONSULTATIONS.md for exact scope and consequences.

Run `./mr-Deva-IN/tools/read_canon.ps1` from the repository root to recreate OCR, after restoring the PDF and Marathi Tesseract model. The OCR command failed once when Windows PowerShell flattened an array argument; rerun through PowerShell 7 using `-Pages @(85,86)` succeeded. Render warnings about legacy symbol fonts are recorded, and the six pages actually used for the 13 BB8 locators were visually inspected.
