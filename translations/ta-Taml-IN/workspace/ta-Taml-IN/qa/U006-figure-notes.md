# U006 Tamil rounding diagrams

Status: 2026-08-31, source-faithful draft assets, not a reader build or a completed course. This bounded task authored only `assets/u006/*.svg` and this note. No source CNXML, shared builder, shared stylesheet, shared log, PDF, EPUB or commit was changed here. Translator-owned source alt corrections were coordinated separately. No browser or rendered-reader QA was performed.

## Actual evidence read

Read the complete English `m81243#fs-id2472737` subsection in `provenance/m81243.en.cnxml`, including all introductory rounding explanations, table instructions, answers, source captions and the repeated-carry rule. Read the actual Tamil section and `qa/U006-translation-notes.md`, not just the terminology ledger. All **23** corresponding canonical JPG/PNG files in the pinned OpenStax media directory were individually inspected with `view_image`. Actual PNG files were treated as PNG witnesses even where the source incorrectly declares image/jpeg. No image was downloaded, copied or substituted by filename guessing.

Canon was reread for this task before drafting: actual already-OCRed pages 30 / printed 24, 31 / printed 25, and glossary page 175 / printed 169, followed by all three page images. Page 30 supports the approximate/exact distinction and the nearby tens/hundreds/thousands register. Page 31's worked **8,436 → 8,400** and **78,794 → 79,000** tables support looking at the immediately right-hand digit, checking against 5, keeping/increasing the retained part and writing zeros. The visible inequalities and values, not the OCR's corrupt operators or “76,194”, supplied the evidence. The glossary explicitly attests **முழுமையாக்கல்**; page 31 also uses **முழுமையாக்குதல்**. The book's Indian grouping was not substituted for the source's international commas.

Canonical upstream pin: `38cae454e644abf9f0a623e876994553881597c9`. The input Tamil source after coordinated corrections is SHA-256 `5ae5553b9ea293ff95e910eb36689c524faaf89954cbdf88d350f302cb7b7a3c` (45,409 bytes).

## Source order and exact files

Every target is the original basename with only its final extension replaced by `.svg`, prefixed `CNX_BMath_Figure_01_01_`. The 035 and 036 sequences are intentionally **01, 03, 02** in source order. The two visually repeated 843 underline images remain separate files with distinct IDs.

| Source suffix, in source order | Media ID | Target intrinsic width × height |
|---|---|---|
| `019.jpg` | `fs-id3447999` | `1000 110` |
| `020.jpg` | `fs-id2907091` | `1000 110` |
| `021.jpg` | `fs-id2471614` | `1000 110` |
| `022.jpg` | `fs-id1318626` | `680 220` |
| `031_img.jpg` | `fs-id1233161` | `1000 270` |
| `032_img.jpg` | `fs-id2306384` | `680 220` |
| `033_img.jpg` | `fs-id2588331` | `1000 205` |
| `034_img-01.png` | `eip-id1168287213054` | `420 170` |
| `034_img-02.png` | `eip-id1168288706202` | `360 105` |
| `034_img-03.png` | `eip-id1168288469372` | `360 105` |
| `034_img-04.png` | `eip-id1168288213158` | `360 105` |
| `035_img-01.png` | `eip-id1168288300776` | `480 170` |
| `035_img-03.png` | `eip-id1168288227113` | `360 105` |
| `035_img-02.png` | `eip-id1168287065587` | `780 285` |
| `036_img-01.png` | `eip-id1168289428642` | `480 170` |
| `036_img-03.png` | `eip-id1168286086719` | `360 105` |
| `036_img-02.png` | `eip-id1168289428689` | `1100 340` |
| `037_img-01.png` | `eip-id1168285947958` | `520 170` |
| `037_img-02.png` | `eip-id1168285947976` | `360 105` |
| `037_img-03.png` | `eip-id1168286217819` | `360 105` |
| `038_img-01.png` | `eip-id1168287387756` | `480 170` |
| `038_img-02.png` | `eip-id1168284799982` | `360 105` |
| `038_img-03.png` | `eip-id1168288313851` | `1100 340` |

These are individual diagrams. The five worked structural tables remain CNXML; no table was flattened into a picture. The original numbered figure captions belong to the source section and were not arbitrarily added inside the number-line assets.

## Visual/linguistic decisions

- All assets use `font-family="TamilBook, 'Nirmala UI', sans-serif"`, independently unique `u006-f…` IDs, Tamil titles and full Tamil descriptions, `role="img"`, and closed title/description and marker references. Visible drawing groups are hidden from the accessibility tree to avoid reading every decorative stroke; the image description carries the content. Every SVG description exactly equals its corresponding current translated source alt.
- Numerals, commas, underline targets, cross-outs, braces, arrow targets and source result values are retained. Individually positioned digit tspans have stable IDs and their parent number text carries `data-number`; underline paths identify the actual digit and character index. These annotations help future renderer QA without changing the visible mathematics.
- Number lines 019/020/021 each show all integers **70–80**, with 11 evenly spaced ticks, red endpoint numerals and the actual teal point at **76 / 72 / 75**. With endpoints at x=60 and x=940, spacing is 88 SVG units; point coordinates are 588 / 236 / 500 at y=35. The middle point is exactly halfway. Teal replaces the witnesses' erroneous orange description, not the mathematical point position. Color is not the only carrier of meaning.
- Diagram labels follow the translator: **பத்துகள் இடம்**, **நூறுகள் இடம்**, **ஆயிரங்கள் இடம்**, **5-ஐ விடப் பெரியது**, **5-ஐ விடச் சிறியது**, **1-ஐக் கூட்டுங்கள்**, **1-ஐக் கூட்ட வேண்டாம்**, **0-ஆல் மாற்றுங்கள்**, **0-களால் மாற்றுங்கள்**. Dark teal and dark red replace the original pale cyan/mint strokes for contrast.
- 031 retains the source's real final sentence, omitted by its original alt: **76-ஐ அருகிலுள்ள பத்துகளுக்கு முழுமையாக்கினால் 80 கிடைக்கும்.** This sentence is visible, not only hidden in the description.
- 035-02 preserves adding 1 to 6, bracketing/replacing **58**, and the downward arrow to **23,700**.
- 036-02 explicitly retains **9 + 1 = 10**, writing 0 in the **hundreds** place and adding 1 to the **thousands** digit, bracketing/replacing **78**, and the downward arrow to **4,000**. It is rounding to nearest hundreds, not nearest thousands as the erroneous English alt claimed.
- 038-03 explicitly retains **9 + 1 = 10**, writing 0 in the **thousands** place and adding 1 to the **ten-thousands** digit, bracketing/replacing **504**, and the downward arrow to **30,000**. It is rounding to nearest thousands, not nearest ten-thousands as the erroneous English alt claimed. Carry instructions wrap as complete phrases; they do not omit the named positions.
- The title word **மறுதொகுப்பு** follows the translator's documented provisional regrouping term; no new canon attestation is asserted.

## Independently discovered marks and coordinated corrections

The originals contain three small marks not correctly described by the initial alt set:

1. 022 has a black underline under **6**.
2. 032 has a black underline under **2**.
3. 036-02 retains a black underline under **7**, not under 9 as its English alt claimed.

These were inspected visually and then confirmed with read-only pixel-row checks because the source images are tiny: 022/032 contain the horizontal underline at y=74, x=53…62, below glyphs ending at y=72. The 036-02 underline is at y=17, x=248…257, beneath 7; the 9 glyph is at x≈240…246. 035-02 and 038-03 do not retain a decision-digit underline. 037-03 is **147,000 without an added underline**. The translator added the three actual marks to the relevant source descriptions; all redraw descriptions now match that source.

## Verification and limits

Passed read-only XML, geometry, mathematical and font checks:

- Exact closure of all **23** source media paths; **371 unique IDs** across the complete asset set; all title/description and arrow-marker references resolve.
- Every visible number text reconstructs its declared `data-number` in order; all input/result pairs retain the source digits and commas.
- **33 ticks**, **3 correct points**, **10 correct underline paths**, **2 cross-outs**, **3 replacement brackets**, and **22 instruction arrows** checked. Underline x endpoints were checked against the actual target tspan center, not merely against a descriptive data attribute.
- Independently recalculated introductory 76→80, 72→70 and midpoint 75→80 at tens, and worked 843→840 at tens; 23,658→23,700 and 3,978→4,000 at hundreds; 147,032→147,000 and 29,504→30,000 at thousands. The input/result SVG strings match.
- Inspected all five place-label arrows: 843→4, 23,658→6, 3,978→9, 147,032→7, 29,504→9. Both carry formulas, correct retained/next-left positions, replacement substrings and result numbers are present.
- Measured **172 visible text boxes** with the actual bundled variable Noto Sans Tamil font and Pillow RAQM shaping, width axis 100 and actual font size/weight. All boxes lie inside their SVG viewBox and no two visible text boxes overlap. Instruction text is 24 px and numeral groups 40 px; number-line labels are 24 px. This is font/geometry verification, not a browser screenshot.
- Total SVG size: **53,274 bytes**. Free C: space was about 10.23 GB before authoring; no disk-full error occurred.

Future integration must preserve useful intrinsic size. Plain underline/number fragments are 360×105; place-label fragments are 420–520×170; longer instructions are 680–1100 px wide. Do not force every fragment to a shared width or shrink a 1100 px carry explanation into an unreadable table cell. The renderer should offer horizontal scrolling and full semantic descriptions for dense illustrations while retaining the worked tables as real tables. No PDF/browser/build was authorized or performed here, and native-speaker/editor review remains open.

## Exact hashes

The source column hashes the actual canonical JPG/PNG; the target column hashes the authored SVG. Full filename prefix is `CNX_BMath_Figure_01_01_`.

| Target suffix | Source SHA-256 | SVG SHA-256 |
|---|---|---|
| `019.svg` | `50b5f6b8038f0e52a90a4605d2f3d14197c5f032774504b267328cf142bde35b` | `48e9abce2115d2fef20289b6c8f70017096d30c51093ba715029ec3cd353a75a` |
| `020.svg` | `a11a8a60ea40a8ce42f863e9b2187f9564b760a8db490c13c085c50d5323225e` | `d8c7b119d8b161c5bb0a9457861c74e5030f7ff6a096b107033e81d051dfa06c` |
| `021.svg` | `c6d3a774cf8df5b6c0e47e20193f8208f80f8736f9a31f930d9d221035b56280` | `a4cde7b441b0f940ccd2aab3b381ff19900024f3aa9374058fbe7d3d2b87e89b` |
| `022.svg` | `b1cbd4b2b67ea81a6a4e063ec8a9261df768b09c9dc82e759d161e0a784e9d26` | `71c2aa8ee08d5625bff67d8f820e2723d86f539f6df305473d2412db198227ce` |
| `031_img.svg` | `d8c91703e97ebe1dd57e7f5a9c340c1d2bc52cd8aff050b0030c686a68d051f2` | `5be6ffc2242dd47674ab332a5d4728c4f9eef92d6c1a3bd5b9377a2bc6dee503` |
| `032_img.svg` | `fb19d8b50aeeade896be67df48c70e4ca8f0b8c1cdf040ff53a775b7e8a2500c` | `82ea74f5d46d898b7dda24845b8fd1b98d5b476f8c6bc8aafec8caaab60670e7` |
| `033_img.svg` | `f71d7c188704329d75a1395854b8584967f2d5698339e58e194288e14b67daa2` | `711e9c344830d3ae4693cabbf89efd47aefbed91a07494a3ccc4c754a0f9b490` |
| `034_img-01.svg` | `e953a580b4b7c4963e7420ef346086dccbf689c2dc2925666e6dd5067184ff8c` | `34f6531a051a60d1fd01c1eab5ec23846b3e1200c3724582615d458150b9fbf7` |
| `034_img-02.svg` | `f7d857950199edae084641fb0383a8087010d9473c6b5c4f2e6cf59b9296d944` | `0cf98829b4b3764ace8cebbf1415d0a854fb522793e2c9bc2d549ca44371cb24` |
| `034_img-03.svg` | `cdfc8f4d645a2bf5eead1f6985dfe9f732fb0dfeed2da38394ccd55af0a4f11d` | `e09ff2adeebd9aa4fa7f872db7aae254970721c4ef23b769fcdd556f35fb0c12` |
| `034_img-04.svg` | `7b37e80545d828cab0c8fd2e810cd4cb68a9cd37a2a2a1310f15bfaa4d942b12` | `224008c982cab9722391e73ba280f5b75c416ec9a1015eeaa31d9f455eda8206` |
| `035_img-01.svg` | `bafd8abf01042f0516ad48e1c55c655f636be96bf0ee67167ec7e7f8b2ca919c` | `605ce11efe680b9fe507e4457431c32163ef097640e66a0e013d52e2091fd808` |
| `035_img-03.svg` | `26c38d4899245d8894c1a9b0d6ad08369ff8ad5f923796862f8d589bcd12ed59` | `3b82f36038178495719eb1e0e620fdffc4b4cf915a1d6aa3450657228ff28b87` |
| `035_img-02.svg` | `134de28f1ab90d9bdc437c191d3a5d8a4ec36c66db45d23f76800373f6596be8` | `eab0de62528dcef279b7688ff1b734cc8624daa4d5f404e22ebb116dd6876542` |
| `036_img-01.svg` | `fb8da84865c79c8a3e119c91d1b87c18358a4c0a8d3777e860393cdf0e778495` | `202af3b0bdb4df2db5b88dbaacb1d6c370b9b1ce4a0d9a9f067ed4dd633cd71d` |
| `036_img-03.svg` | `c56351af99a8023f2732cb9961fd8d28c92662df860e33173e65f766f879c088` | `e8038b676d7370459765f51f116d479507225066590fd6c70691869c1c9db1ba` |
| `036_img-02.svg` | `c5cd8ecb776c6a2b33408c57b49f6cce781f7ab43550afa4e675f51aaf81ea1b` | `686ee8db0c718cdc1f2f17832b68de29058c3c1a6171a483dfe86a779cd8de3c` |
| `037_img-01.svg` | `ce07a98c0bfcf2eb0b178ddc2a9fc44cc66a9000f362bf2a34bbfef807fecfd6` | `154193d424e4f123f91af509d87549896fd826aef87c32b96f4fdea4ca9af61b` |
| `037_img-02.svg` | `2f9984248919b3261388155339dbd60712668ee3959b4536eaaeecd78ba678cd` | `f4ebf3b069f8a016241287f01a372d24f2641df39698a9511a3739a81f507023` |
| `037_img-03.svg` | `244a1567327a7f68187f4b78558318f53d815db15a172e00cade6b090eb47298` | `8eafeff9ebf7f82742088e3e68658ecfbd26bc6268e8f39f9ab5ea8c00d6bc5e` |
| `038_img-01.svg` | `6422f5384df914209793aadcd6358d01ec2d1e4d73a019f4c41a1579a911f99e` | `255c08370f1584d373a9b780fa2381dde12a66fbedb7af47b534b1f0ed1ead96` |
| `038_img-02.svg` | `b0790658177c03fa0fea53a127a8c3cd1786bb38bf633896bccb41cbd278ce5e` | `762fd9f6bde15b120db968fbd608f4dcebb2a4e03ad8c884212e9a8d1c7985e2` |
| `038_img-03.svg` | `1d96268786cb4e8d99c4598aa3d5009009489f3690d9a8d1126274bced0eb6d1` | `d2e82eda7c14e79017e1ff1260acc789e6a06e1e446c3be3cd10f7563f089c26` |

This completes the bounded U006 figure asset task only. Reader integration, recovery routes, subsequent source sections and the overall assignment remain ongoing.
