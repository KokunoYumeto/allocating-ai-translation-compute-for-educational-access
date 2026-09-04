# A20:m81373 assembly — author review and reproducibility handoff

Date: 2026-08-31. Status: **assembled translation draft; independent assembly review and new-artifact QA pending**. This report and `test_assemble_m81373.py` are the assembler author's checks, not an independent review, native-Marathi approval, accepted reader, or completion of the five-book assignment. No HTML/PDF was created or inspected. The existing Browser policy stop remains in force.

## Source identity, scope and preservation

The assembled title is “संबंध आणि फलने”, with the source titles “Relations and Functions” / “Relasi dan Fungsi”, content ID `m81373`, and UUID `59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20`. The exact EN and ID module members were read from the already pinned archives, not a moving branch or HEAD. Two small raw witnesses, totaling 295,530 bytes, are retained in `provenance/A20-m81373-assembly/`:

| Witness | Bytes | SHA-256 |
| --- | ---: | --- |
| `en-m81373.cnxml` | 151,578 | `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c` |
| `id-m81373.cnxml` | 143,952 | `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee` |

The receipt records both exact archive-member paths and the previously established archive hashes. The explicit bootstrap reads only those two members, checking their byte lengths, SHA-256, uniqueness and ZIP CRC; it does not freshly rehash either large archive or perform a general extraction. Existing exact provenance bytes are not newline-normalized.

Both complete raw sources independently yield the same 625 original IDs in the same order. The 134 nonoverlapping selectors cover 619 of them; the remaining six are four existing context sections and two practice wrappers. The chosen units 002–011 contribute respectively `4, 1, 16, 16, 31, 9, 21, 14, 18, 4` selectors. Unit011 deliberately replaces, rather than duplicates, unit001's four m81373 selections: `fs-id1167836692527`, `fs-id1167836521479`, `fs-id1167829859398`, `fs-id1167833175472`. Its 61 restored nested IDs add no new unique selectors. Unit001's other-module excerpts are not imported.

The complete source order and canonical ancestry are checked for all 625 IDs. All 84 original exercises retain their original problem IDs. Their 55 supplied answers remain source answers; the other 29 answers remain clearly labeled original additions answering existing source questions, not newly invented questions. Every problem/answer pair has reciprocal local links. The three learning objectives, five glossary entries, definitions, teaching material, practice, writing answers and blank student self-check are preserved.

The previously absent `fs-id1167826170977` practice wrapper and `fs-id1167826189010` child are restored. The former is untitled in the source and receives a source-context accessibility label, not a claimed source title; the latter receives the explicitly authored translation “सरावातून प्रावीण्य” for “Practice Makes Perfect”. The four existing context headings are reinstated around their actual source descendants. Local example/practice numbers remain unit-local, as the new header explicitly explains; original IDs and order govern identity, not a claim to reconstructed book-global numbering.

## Discovered unit002 fidelity repair — only in this assembly

The first strict ancestry/order run exposed a real historical unit002 representation gap in Sylvia's email example `fs-id1167833158753`. The media ID `fs-id1167829850506` had been attached to the problem's formula rather than the solution's first calculation row. The three-line target calculation also lacked the source's separate initial-rule row and explicit “Simplify.” instruction. This was reported to the primary agent before repair; it authorized a repair only in the new assembled representation. Historical unit002 XML is unchanged, SHA-256 `0a46a929a80df9755bc4f4df95102049c524f2506daf03c37952a368f01a1172`; historical unit001 is unchanged, SHA-256 `367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9`.

The EN witness at lines 832–878 and ID witness at lines 833–879 place table `fs-id1167829709312` inside solution `fs-id1167829715383`, after the part-(b) prompt. Their four rows and media are now restored exactly in source order:

| Row | Source media ID / raster | Formula | Source instruction treatment |
| --- | --- | --- | --- |
| 1 | `fs-id1167829850506` / 021a | `N(t) = 75 + 10t` | Blank first cell retained |
| 2 | `fs-id1167832971244` / 021b | `N(5) = 75 + 10 · 5` | Substitute `t = 5` |
| 3 | `fs-id1167833270224` / 021c | `N(5) = 75 + 50` | “सोपी करा.” |
| 4 | `fs-id1167833309949` / 021d | `N(5) = 125` | Blank first cell retained |

I personally viewed all four EN and all four ID 021a–d original raster copies, including the two red substituted 5s in 021b. Their equations agree. The existing review-copy bytes were checked against the pinned ZIP members and source lock: EN total 67,215 bytes, ID total 433,271 bytes. No images were edited, regenerated or newly downloaded. The copied problem formula remains text under its original paragraph ID; only the misplaced media identity moves. The source's part-(a) opening dependence sentence and repeated part-(b) “find and explain” prompt are also explicitly restored. A visible original assembly note discloses the repair. Two added checks represent the restored rule and input; existing mathematical values do not change.

The complete module has twelve source calculation tables, representing 47 source rows. Nine are retained as tables with 36 rows. Three unit009 equation tables were already explicitly labeled linear adaptations: `fs-id1167836429672` and `fs-id1167836533787` each preserve three source rows in four paragraphs; `fs-id1167829596595` preserves five source rows in seven paragraphs. I checked their actual source rows against the target equations and instructions; the tests now check their exact paragraph sequences and media order. An initial regression assumption of nine total source tables was wrong and was corrected in the test, not hidden as a source change. No additional table-content omission was found in this bounded check.

## Notes, references, mathematics and assets

133 unrepaired selected translation subtrees are checked for complete structural/text preservation after undoing only documented transport changes: namespaced authored IDs/check keys, local asset routes, source-context attributes and localized links. The sole content repair is the Sylvia example above. Source correction notes already inside selections remain in place. Thirty-one explicit outer-note dispositions record retained, rewritten or omitted content; unexpected outer notes fail rather than disappearing silently.

Retained substantive notes include domain/codomain distinctions, finite plotted pairs, notation/input distinctions, model assumptions, source corrections, BMI qualification and the distinction between source and original writing answers. Checkpoint-only exclusions, obsolete transitions and unit002's separate original P1–P4 practice are not presented as canonical module content. Three former cross-unit source references now target the exact local IDs `fs-id1167829683746` twice and `fs-id1167833057329` once, retaining prior HTTPS routes as provenance attributes. Three untranslated m81422 references and the optional OpenStax resource remain honestly HTTPS and internet-dependent.

The XML retains 437 exact checked mathematical strings: 435 copied checks plus the two restored Sylvia checks. This is string-preservation evidence, not a fresh independent proof of every calculation. The Sylvia value is separately checked using exact arithmetic. Twenty-eight embedded canonical assets retain exact bytes (1,551,848 bytes total) at repository-relative paths under their existing unit asset folders. Other formula rasters remain source-provenanced text transcriptions; the footer does not claim they are embedded assets. Existing source credits, settled CC BY-NC-SA 4.0 notice and component notices are retained without reopening the supply/license audit.

## Actual canon consultation and effects

At selection and heading drafting I read the existing Balbharati Grade 8 OCR for physical page 13 / printed page 3 (`downloads/mr-Deva-IN/canon/ocr/balbharati8-13.txt`, the practice-heading/instruction passage around lines 55–75). Its readable “सरावसंच 1.2” and short imperative informed a compact practice heading and instruction style. Its garbled OCR mathematics was not evidence. “सरावातून प्रावीण्य” is a new translation choice, not a phrase claimed to be attested there.

During the Sylvia repair and final revision I read C12, existing OCR physical page 85 / printed page 75, opening paragraphs defining उकल and discussing same operations and simpler equations. It informed the concise “सोपी करा.” instruction and the distinction between evaluating a given function and solving an equation for an unknown. I did not use OCR formulas or claim a fresh PDF-page visual inspection.

For retention/revision of the domain and notation notes, I read the relevant opening prose of [C19, फलन](https://vishwakosh.marathi.gov.in/27548/): uniqueness of output, प्रांत, सहप्रांत and the image-set distinction. This supports retaining the domain/codomain qualification rather than treating a plot frame as a domain. The established मूल्यसंच remains a provisional house choice, not a newly witnessed synonym. A final direct fetch returned HTTP 502; that attempt was not counted as a consultation. A targeted search subsequently returned the actual opening paragraphs of the same primary entry, which I read. Unrelated advanced claims and unread image formulas were not adopted. No new broad canon audit or ledger edit was performed by this worker.

At handoff I directly read the coordinating task's user reminder (turn `[local-task-id]`) to keep checking the source canon. The above are my actual relevant readings and effects, not another worker's claimed consultation. The latest storage investigation remains coordinator-owned; nothing was deleted here.

## Reproduction, checks and final pins

Commands run from the repository root:

```powershell
python -B mr-Deva-IN/tools/assemble_m81373.py --capture-source
python -B mr-Deva-IN/tools/assemble_m81373.py
python -B mr-Deva-IN/tools/assemble_m81373.py --check
python -m unittest discover -s mr-Deva-IN/tools -p test_assemble_m81373.py -v
```

The bootstrap is not needed after the two exact raw witnesses are present. Default and `--check` read only 339 receipt-listed repository-relative inputs totaling 3,701,872 bytes, including the assembler itself. The portability regression copies exactly these small inputs to a temporary directory, forbids ZIP access, and reproduces the exact XML and receipt without ignored corpora or absolute donor paths. This proves that bounded reconstruction, not that every file has already been staged/committed by the primary agent.

Observed final suite result: **17/17 PASS**. The checks include exact full source ID order/ancestry, selection replacement and nonoverlap, all unrepaired subtrees, repaired rows, table adaptations, answer identity/navigation, wrappers, references, preserved substantive notes, unanswered self-ratings, exact math strings/assets and portable reconstruction. Mutation tests reject altered IDs, a changed formula, changed source prose and an autofilled rating; unsafe paths/duplicate IDs or JSON keys fail. A staged-write failure preserves previous outputs. Several output replacements are not an atomic multi-file transaction; the script states that limit.

| Final artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/A20-m81373.xml` | 282,780 | `4a47646ee5129394213e7576d23356dbfc603c6a956dcbfaf45d90e3a1fe82fa` |
| `qa/A20-m81373-assembly-receipt.json` | 134,606 | `3141b0a206675ee56968f09f19e727f7fad82f2cfa940e28434ed8a0543f3d29` |
| `tools/assemble_m81373.py` | 45,060 | `67ad1ce139b8c597a548fe7ad4d1ccbb332f9f1d33c603033dec24600981a469` |
| `tools/test_assemble_m81373.py` | 19,212 | `e2f82cdde7be839cd8364b428175e6e23ada31a0164063c686924f8482f2fbe0` |

No missing canonical source IDs or selectors remain in the assembled structural census. That is not blanket semantic, linguistic, pixel or reader acceptance. Independent assembly review, format-specific build/visual QA and human/native mathematics-language review remain pending. Existing unit-level evidence is inherited only for unchanged material and does not certify the new whole-module artifact. This handoff leaves the entire five-book translation task active.
