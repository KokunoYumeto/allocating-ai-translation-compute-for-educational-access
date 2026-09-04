# A20:m81373 standalone PDF worker review

2026-09-01. **PASS for this exact direct-XML PDF build and the worker's complete visual pass. Primary review is separate.** This result does not clear the blocked HTML/browser route and is not whole-book or five-book completion.

## Exact final snapshot

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/build_m81373_pdf.py` | 24503 | `68547e1865ca998b0d4e7ebd2ef68d649e2f1efa0fdfa7afebdfde29f36643a1` |
| `tools/test_build_m81373_pdf.py` | 14750 | `26746f1837886f437ce065d6567ff984f778a3b49dfd5f273d595b2df234f579` |
| `output/pdf/A20-m81373.pdf` | 2660139 | `e1d9142794ddd56d807f2606855b84baa46b592f05cd8041acbefe99142b6090` |
| `qa/A20-m81373-pdf-build-receipt.json` | 124215 | `f18c59f76650ea31aa37adcec7209f1083ac4edca23801669e21853ac43e3778` |
| immutable `tools/build_pdf.py` | 24564 | `c54d8571feb262fcce90d37dbe9d02fcdf9b39246fbed739ce9992f1185afc90` |
| released `translations/A20-m81373.xml` | 282780 | `4a47646ee5129394213e7576d23356dbfc603c6a956dcbfaf45d90e3a1fe82fa` |
| released assembly receipt | 134606 | `3141b0a206675ee56968f09f19e727f7fad82f2cfa940e28434ed8a0543f3d29` |
| released assembly builder | 45060 | `67ad1ce139b8c597a548fe7ad4d1ccbb332f9f1d33c603033dec24600981a469` |

The PDF has 64 A4 pages and 2660139 bytes. `pdfinfo` reports PDF 1.7, no forms, no JavaScript and deterministic 2000-01-01 metadata. Poppler 26.05.0 produced all 64 final 110-dpi PNGs in `tmp/pdfs/A20-m81373/v3/`; together they are 10437957 bytes.

## Workflow and input boundary

I completely read the PDF skill before work. The required artifact marker was run exactly once for this new output as create / expected-output-count 1 / pdf immediately before the first authoring patch. It completed without reported error or output; it was not repeated after interruption.

The builder calls the released assembler's pure in-memory reconstruction and requires byte equality with the saved XML and receipt. It independently rechecks every one of the 339 receipt pins (3701872 bytes), source/receipt/builder hashes, 625 canonical and 664 total XML IDs, 134 selected blocks, 84 exercises, 55 supplied answers, 29 explicitly authored answers to source omissions, 437 preserved math strings, six local source cross-references, the HTTPS links, four metadata pairs, eleven tables, nine blank rating cells, and 28 canonical JPEGs totaling 1551848 bytes. It never reads HTML or CSS; the test suite rejects such reads.

The original UTF-8 XML is attached byte-for-byte. The render clone changes only the first authored header paragraph, from the assembly-specific “एकत्रित अनुवाद-मसुदा” framing to the recorded neutral “स्वतंत्र PDF वाचन-मसुदा” framing. A reverse-clone assertion proves every other XML node/text/attribute serializes identically. The PDF-specific line says this is an आशय आणि मांडणी तपासण्यासाठीची PDF प्रत, not an accepted book or finished five-book workflow.

The module-local table renderer supports all exact shapes: row counts 3,3,6,6,4,4,5,7,5,7,4; two columns except the final four-column self-check; the first two lack headers and the remaining nine repeat one header row. Nested cell content includes six figures, 37 spans, one div and three paragraphs. Images are size-limited within their own cell. The four restored Sylvia rows and the six-row authored day/value model table are both visible.

The receipt's stable integration fields are `unit`, `result`, `source_sha256`, `assembly_receipt_sha256`, `assembly_builder_sha256`, `builder_sha256`, `immutable_pdf_helper_sha256`, `pin_validator_sha256`, `pdf_sha256`, `pdf_bytes`, `attached_xml_sha256`, `input_pins` and ordered `assets` entries with `path`, `sha256`, `bytes`, and `mime`. Its result is structural-only PASS and its `visual_review` deliberately points here.

## Fonts, shaping and corrections

ReportLab 4.4.9, uharfbuzz 0.56.0 and Python 3.12.13 were used. Embedded/ToUnicode fonts are:

- Nirmala UI face 0 (regular) and face 1 (bold), TTC SHA-256 `ad02cdfc06e144ac45f318e8e5a64cbe04c7479d4beb91d25f5a319a466b1767`, embedding fsType 8.
- Cambria face 0, TTC SHA-256 `84e70ccc1664482f4a960442c7a166c91a1b2cf98ff88c33cb73f79403f66d7b`, embedding fsType 8, for the six reviewed fallback characters `′″⇒≠≤□`.

The first full render had two defects found only by visual review. A standalone “(c)” ended page 23 while its table began page 24; a module-local keep-with-next rule now groups standalone subpart labels. Then page 33 showed replacement glyphs in `5′4″` and `5′11′′`. ReportLab 4.4.9 shapes a complete space-delimited word using its first font, so per-character fallback after a Nirmala digit selected glyph zero. The final builder renders the complete symbol-bearing word in a font whose coverage it verifies before layout. A focused test shapes both height forms and rejects any missing glyph. Exact PNG comparisons show that v2 changed only pages 23–24 from v1, and final v3 changed only pages 33–34 from v2. All other final-page evidence is byte-identical to the already inspected render.

## Automated checks

The final suite ran **18/18 PASS, zero skips**. It verifies the exact 339 inputs/counts; authorized clone and exact attachment; every source leaf, all 437 math keys and every image description; all 664 destinations and printed identities; all eleven tables/54 rows/nested cells; metadata/credits/nine empty ratings; 28 byte-exact decoded JPEG streams; real HarfBuzz conjunct shaping and symbol-word fallback; embedded fonts/no actions/forms/JavaScript; exact link identities; byte-reproducible repeat rendering; immutable base helper and PDFs 006–008; rejection of content/rating mutations, input drift, unsafe routes, unsupported cells and overflow; and exact saved PDF/receipt bytes.

These are preservation and renderer regressions, not 437 new mathematical proofs or native-reader approval.

## Complete final page review

Each row below records a direct visual read of that exact final PNG. I checked Marathi conjunct shaping, mathematical signs/superscripts, margins, clipping, overlap, broken tables, figure sharpness, link appearance, headings, source labels, footer and page number.

| Page | Final PNG SHA-256 | Observation |
| ---: | --- | --- |
| 1 | `e751b4926c83de9ee5c756ac9850e013316a2686533f7fc66aceff01bc7d93cf` | Cover, metadata, neutral PDF framing, objectives and Readiness 1; title/Marathi shaping/source labels clear. |
| 2 | `3eb888222f9adf3c667271a34b23e234a9eb9bbc1f37187ad771e3ad08dfb46b` | Readiness 2–3 and opening relation prose; links and source labels readable. |
| 3 | `39536d5a536116e04697a5e6005f167a0864f392db6343b4b6dbe89d08a5746f` | Relation definition and worked ordered-pair example; braces, pairs and domain/range notation clear. |
| 4 | `b4c1bb0f40750db9095ba6240c58346f5d03742c4773e22b15207160dff76d9d` | Try Its 1–2 and mapping-diagram introduction; answer labels and source identities clear. |
| 5 | `2ddc3ae265a58ad14b48c056a1fdf2b3d12711f4899e8c1e06b4808cbec96216` | Birthday mapping diagram and full domain/range solution; diagram, alt prose and label key readable. |
| 6 | `a2c00130eb85d9933587c768e95fcfa995a268abd4421ff3245a531660638831` | Student-ID mapping plus start of next mapping task; email-like IDs and correction note readable. |
| 7 | `b8dbd9c532e429fa03afb2ec586597d9abe66ecab2d34d80f00e87ae12f088e9` | Birthday mapping solution and graph introduction; no clipping at page transition. |
| 8 | `e6bf1ab52f5926b43362b0fd7f385b5c7f0b39634f2638bc2d3a59c0baa74a09` | First finite graph, alt description, answer and next prompt; axes/points/minus signs readable. |
| 9 | `332439f3aef6a28e0804e8ae10883cb26becd7df18ed0d294100c07dd4262681` | Second finite graph, alt description, answer and next prompt; axes/points/minus signs readable. |
| 10 | `b07a75a3ff78ad26b01ac41f978532aa81faee31498a712652e8ae8a466e986b` | Third finite graph and function definition; repeated x-value is visually distinct. |
| 11 | `77ff1e52734616f78d9f5c4fed94a552c5f7f5b46f50aad11cb44b6217c63923` | Function reasoning and first ordered-pair worked solution; dense prose remains legible. |
| 12 | `bfb70c18fac26cf9b96da09a3d349a674c39b7b731fd9f9684c2d2710664ff17` | Try Its on function classification; braces, negative values and correction note clear. |
| 13 | `c41eca47ce7d9aa0e854dca3981eb9d2700b7604441f019f2296bede0815bf7b` | Telephone mapping diagram and partial solution; all six numbers and arrows readable. |
| 14 | `87a087c7c1caa5b80243f95243e5453bc0a5fb7c3d6d344cf0879e9722d46bec` | Telephone continuation and network/program mapping; diagram and all labels readable. |
| 15 | `f61961f2a89dfef173deb337e213018d46008258560967a699c9d9b853ae0c57` | Second telephone mapping, solution and equation-test introduction; long correction note uncut. |
| 16 | `60494cd18b931cde848446a40134091f6ec9b0950bcbb279839958f06a48de83` | Equation-function worked solution, including superscripts and multiple y-values; all steps readable. |
| 17 | `9a59898f9d2e7a4572d9dc72e739c5cf897268bab5c438e67d3bc582523a5572` | Worked solution continuation and Try It 5; inequality x ≤ 3 renders cleanly. |
| 18 | `8128b16ce80f65f26ff8892f807078a58aeaa974e051bda2a01fa896c01ac0c0` | Try It 6 and function-evaluation notation; superscripts/minus signs clear. |
| 19 | `3de8b20404518c50611bf34eb8fdde302a2ea4c1634f467215eb77b81f482a56` | First three-row equation-image table; all rows, alt descriptions and surrounding prose fit. |
| 20 | `36f65254e6f922d3000dfe964acb93149d8844015568d78a552cb5b24fc62ade` | Second three-row equation-image table plus first five-row calculation table; cell images and text fit. |
| 21 | `f2fbd17c327583744eff19621993599f6cf807eb59e5925da0935fabca0a97a2` | Two remaining calculation tables for f(-2) and f(a); every header/row and explanatory note readable. |
| 22 | `3aa17687dfc7a620373e66c40b00c97eb28e2f1a62d8e876b8095e965d88b5c0` | Try Its 1–2 and start of nested-substitution worked example; math strings readable. |
| 23 | `8d065048c336339e8d7eb4c29dc396a014df55deb889d607fa8d0f87f422c775` | Nested-substitution tables (a) and (b); standalone labels and both full tables grouped correctly. |
| 24 | `3987b300348bd12bc0d416e1aa030daed518e1575853a359b1477367b30c4c5f` | Subpart (c) label now stays with its six-row table; following Try It and explanation fit. |
| 25 | `935b08a72c0ee4422a7302badf430f7c5579dc46b833db62e8e6dd4292c73646` | Try It 4 and restored Sylvia four-row calculation table; N(t), substitution, simplify, N(5)=125 preserved. |
| 26 | `cf34cab4133929b01c9a0d940e067d4f0887b7fb685a4058d1e142e44bcd1018` | Sylvia interpretation, daily-count six-row table and difference formula; all rows/values clear. |
| 27 | `aeffe14665a5f91344002004aeb200afc4abbdea7316bf6d06d2ae82b4cd381c` | Model domain/range/continuous-approximation qualifications and Bryan example; decimal/minus notation clear. |
| 28 | `7182dd1fded023d8f64b691b1164956da1869a3826dbebba931a0735c13bcc7d` | Anthony example, resource link, Key Concepts and domain/range qualification; links distinguishable. |
| 29 | `a144d2d911b65739ae1696ca99c58c42b653955ac0b7c95e974ba3425727bccc` | Practice introduction and Questions 1–2; authored-answer labels and set notation readable. |
| 30 | `fa0dd8ed7b4809b2e16973f3afd21a0cec5131787d739d11a6c36e68ac209c7c` | Questions 3–4 plus next diagram instruction; ordered pairs and negatives readable. |
| 31 | `92352ecfe7977aef0cbcc7b47bd0ee277ae584566361e5e96e36bd61d5762442` | Question 5 canonical birthday mapping and answer; full figure and all names/dates readable. |
| 32 | `5e74de745bd2b1c24c55aee575f0dc56541f9d1da6f4a60b59a4ca91b3ec0bc9` | Question 6 mapping, answer and BMI qualification; figure/links/prose readable. |
| 33 | `040b032d9fb67c37d4083ceb21c7b02a704d1006099ee57097e90ea0c7738e92` | Question 7 BMI mapping and start of Question 8; corrected height 5′4″ and values render without replacement glyphs. |
| 34 | `0e16496073fc55f06add2355189dda706afb89b6adca6362beb4766a5f233aad` | Question 8 BMI mapping and next graph directions; height 5′11′′ and caption render cleanly. |
| 35 | `0f6fe20850d1e776d35fd12c1d6812a71cc5337d6892493e883086d8437ec8c1` | Question 9 graph/answer; axes -5..5, six points and ordered-pair answer readable. |
| 36 | `18745f5fb73830b3171c4ff26ab83345072a5e4a49831f5cbfb20446cf486766` | Question 10 graph/answer; axes -6..6, six points including repeated x readable. |
| 37 | `ebc055b6f01ccf6e56b62a7ac204b1dd5b96bbd090ab2370a5b94a7b14807222` | Question 11 graph/answer; upper/lower point sets and answer readable. |
| 38 | `e750352143506e863ebce4f2b23c027da65141ff9f4f033dc3b0dc3e93bdb5fe` | Question 12 graph/answer plus next practice section; fractional 0.5/1.5 points and axes -7..7 readable. |
| 39 | `51a6eb7c36b1a26b92692300a72b51ca7277f4e30517ecd39c878abb84db910f` | Function-classification Questions 1–3; sets, repeated outputs and correction note readable. |
| 40 | `513c0041ef9ec885300b0d109e993cf0398044774b261f72ab5d10d2a5739cd7` | Question 4 and absolute-value mapping Question 5; all arrows/labels/answer readable. |
| 41 | `d7ce1c63db47edf2f931a52d000703cbe9858b20ed2eb85a05d6602f8bca1ed8` | Question 6 square mapping; continuation sentence and all arrows/labels/answer readable. |
| 42 | `79a509d2cdea994008e147686993152a0ef5122de0077a4ebdee9fdd75e11e3d` | Question 7 email mapping; addresses, line wrapping and documented corrections readable. |
| 43 | `47d853bb70c729b19d7615ba9d6d9401bb1be7912f155125166a20f4e4c3ec66` | Question 8 email mapping and equation Question 9; the source image's spaced address remains visibly documented. |
| 44 | `462b10266717fa4cb19dee7c4d3d97793343f55ca9bcb2dca1e980dde8cbd734` | Equation answers and Questions 10–11; powers, parentheses and solved forms readable. |
| 45 | `da218f810bd762533d9ea06f22a4acf5df7feb1bd54c946a918014a24c9ad409` | Question 12 and start of value-evaluation practice; math and source labels readable. |
| 46 | `57d2939f8170688f81ccdb560d29104a780bf97d2a213b87b449dad5c5a482b5` | Evaluation Questions 2–5; source/authored answer labels and superscripts readable. |
| 47 | `cc81ece11052cce6b3bcd6226264ce14f2cd84c6491678946d481ab5b928372f` | Evaluation Questions 6–8; long polynomial substitutions fit without clipping. |
| 48 | `d8511266b706625e8c6d93da909091e54a50c0a08b801acf6e57b7182b0a6af2` | Nested evaluation Questions 9–11; h²/x+2/sum expressions readable. |
| 49 | `3a465d6edc4c9de36ac3b2f83342ea72b29c2a0d10ee107c11321a736d002fd3` | Nested evaluation Questions 12–14 and next instruction; all lines/source labels fit. |
| 50 | `b801d7bf6f7161892ac5916a8c0b10fcab3608d07eb695f9597ee9e5140da8b0` | Evaluation Questions 15–18; uppercase function names, powers and answers readable. |
| 51 | `2a26e157666ace7be61df8d2ea64f0f00afe71d4118a022f5b42274e33df39ab` | Evaluation Questions 18–21; absolute-value bars and rational function notation readable. |
| 52 | `eb07a04a10c53af010697bf31c3df8588ca79b40dcdc85927fb7e2d9271c4841` | Questions 21–24; denominator/domain wording and DVR/linear-model interpretation readable. |
| 53 | `ffcb8c6b5966358b527a79587dec828394eb067f27445ff0a1e2817072bdb2c1` | Question 24 continuation and cost Question 25; inserted line break keeps C(1000) chain readable. |
| 54 | `3423ecd6a8ccdc20a1499df4e42a9da6ac35eb09ab7aee715e5d1810a9dfbb41` | Question 26 continuation, writing section Questions 1–2; cost chain and authored samples clear. |
| 55 | `1712a10310652815b30703f495b636df94c502c55aa35d8235ffef132abada64` | Writing Questions 3–4 and self-check introduction; relation/function notation readable. |
| 56 | `3035bf073dd4a7944e2c763870d7565db88c840061d1b694827ca109a0e4207d` | Original English self-check image plus translated 4×4 checklist; nine boxes remain visibly blank; glossary begins. |
| 57 | `bcf4042a5761cceba8df6ddf744f06cabfde8526d1eaba8a7efe0177ad52696d` | Glossary, credits and CC BY-NC-SA 4.0/component notices; no clipping; HTML/PDF limits remain explicit. |
| 58 | `eef0480eaeef3d06b46fb974cb512653489bbbbac6116e306ab15b55dab3f501` | Identity-index heading/note and first two columns; IDs legible and inside margins. |
| 59 | `645afda4c7f66c6f3c02baf6aa50a5d74d28ff5675b19c8eb8a96ea04d543961` | Identity-index continuation; both columns remain aligned and unclipped. |
| 60 | `e8ae1083d19d2c3c43c9203843cc662a4300ad10555197f2a5df8b01121d635b` | Identity-index continuation; both columns remain aligned and unclipped. |
| 61 | `0d1c5795ae0e6b3ccaa6989248de3b22ed792db7a11b773e198d7f8dab6fcfaa` | Identity-index continuation with authored IDs; mixed ID lengths remain legible. |
| 62 | `5cdfab1d91f3657c3377857d73eb1a94b6fbcbbade779a1c9c60a79c9d767706` | Identity-index continuation; both columns remain aligned and unclipped. |
| 63 | `fede3d3d318b4c681d3b9476f4f78d41a6d141c92584c062298eb9d78c422516` | Identity-index final full page; checklist/glossary IDs readable and unclipped. |
| 64 | `277f2fe90e701f90cbe92c6c6c316cc59230faabb54fe580a6934e5621c598c9` | Identity-index final four IDs on a partial page; no truncation and footer/page number clear. |

No black/replacement glyph, clipped line, overlap, broken row, truncated figure, filled rating or missing footer remains. The partial last identity-index page is intentional: only four IDs remain after all 664 identities are printed; all four are visible.

## Actual Marathi canon consultation and limits

At PDF framing/layout selection I read the complete existing C12 OCR witness at `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`, not merely its glossary summary. Its readable prose distinguishes a value that makes both equation sides equal, solving for that value, and identical operations on both sides. I ignored its garbled formula OCR. Concrete effect: the PDF preserves “सोपी करा.” as a separate calculation-table instruction and does not collapse substitution/evaluation rows into an equation-solving paraphrase.

At final QA I freshly read the readable opening of [Marathi Vishwakosh, “फलन”](https://vishwakosh.marathi.gov.in/27548/): each domain element is paired with exactly one codomain element; `y=f(x)`; `प्रांत`, `सहप्रांत`, image set `कक्षा`; and the image set is a subset of the codomain. Concrete effect: domain, codomain and observed range remain visibly distinct on pages 27–29 and in the exercises; no layout abbreviation merged them. This source attests `कक्षा`, while this established workflow's provisional `मूल्यसंच` remains unchanged rather than being silently retranslated for the PDF.

This PDF is separately authored from the released structured XML. I did not open or convert HTML, use a browser/local HTTP/CDP route, or claim that PDF review certifies the denied HTML surface. I do not claim PDF/UA, tagged PDF, PDF/A, universal extraction, native-teacher acceptance, independent full-module source/math acceptance, or five-book completion. Fonts and shaping binaries are pinned local rebuild requirements, not repository font assets. Primary source and primary final-page review remain separately owned.

