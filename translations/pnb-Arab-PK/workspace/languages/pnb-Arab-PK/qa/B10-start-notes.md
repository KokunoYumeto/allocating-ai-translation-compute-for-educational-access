# B10 opening source study

Status: source study and next-unit canon consultation only. No B10 translation, frozen excerpt, copied asset or reader was created. This checkpoint owns only `plans/B10-start.json`, these notes and the new B10 canon receipt. The full A10/A20/A30/B10/B40 assignment remains active.

## Recommended complete opening

Translate **all earlier front matter**, then **the complete Chapter 0, Introduction and Preliminaries**, not just its first few paragraphs. The two coordinated units should be `B10-frontmatter` and `B10-001`; neither is already covered by this study.

The front-matter unit includes book title/subtitle, relevant docinfo wording, and the entire active `frontmatter.ptx`: titlepage; colophon and copyright/license; dedication; acknowledgement; first preface including edition changes and attribution; and the second preface, How to Use This Book, through its QR image. It has 25 paragraphs, seven explicit titles, four list items, two prefaces, two attribution lines, four URL elements and one source image, plus the docinfo cover/logo. Its proposed 50 text slots include metadata labels and fixed credits, not 50 translated paragraphs. Source order must not be reduced to a brief attribution footer.

Chapter 0 is a coherent approximately 4,462-word source introduction. Include the complete chapter title/introduction and both active sections: 0.1 What is Discrete Mathematics? and 0.2 Discrete Structures. The latter has seven active subsections: Introduction, Sets, Functions, Sequences, Relations, Graphs, Even More Structures. The end boundary includes the final reading question `rq-intro-structures-q`, its response element and all closing section/chapter structure. The next outside file is `source/ch_logic.ptx`, Logic and Proofs.

The proposed 157 chapter slots count every active paragraph, title, footnote, image shortdescription, answer-feedback string, index heading/see string and table cell once. They are a preparation convention, **not** a completed/frozen translation-key manifest. This is 85 paragraph nodes, ten titles, two footnotes, two shortdescriptions, six feedback strings, 38 index headings, two index-see strings and twelve table cells. Mixed parent paragraphs require child placeholders: no duplication of nested list paragraphs or index text. Anonymous nodes need stable file-plus-sibling-path keys; original IDs and labels remain separately preserved.

## Authority and include order

B10 is Oscar Levin's **Discrete Mathematics: An Open Introduction, fourth edition**, not OpenLogic. Actual lock, user instructions, durable goal and existing notices were read. Repositories were locally verified at canonical commit `82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799` / tree `5b8209e92286e967a18114eea99c11ba68b8a162`, and Indonesian commit `e94905932301e699b7c4d44e88ec54e972b886b6` / tree `457bb9f48aefe119f3c3a48b485f0c1198d64c3d`.

`project.ptx` actually selects `source/dmoi.ptx`; its generic comment suggesting `source/main.ptx` is misleading, and that file is absent. The root README's main/third-edition language is stale for this pinned checkout. The active book subtitle, docinfo and front matter identify the fourth edition.

The document includes docinfo, then book title/subtitle, front matter, introduction, logic, graph theory, counting, sequences, structures, additional topics and back matter. Publication numbering begins at **0**, so the forward sequence and graph-theory references mean Chapters **4** and **2**, not 5 and 3. The chapter includes exactly the two introductory section files. Both are self-contained: no active exercise/practice include is hidden below them. The old sets/functions includes and a Statements subsection are XML comments, not active content. Two unreferenced `intro-intro.ptx` exercise/practice files are empty and must not be pulled in by filename guessing.

All six principal English and Indonesian PTX files were read, including the full front matter and both sections. The plan records exact Git-blob and working-tree SHA-256 identities for selected source/config/asset inputs. Windows PTX and SVG checkouts differ from their Git blobs by CRLF; future witnesses should use exact `git show` bytes. This is **not** a universal LF rule: the tracked canonical root LICENSE itself contains CRLF. Binary PNGs must never be normalized. No upstream or comparison file changed.

## Mathematical and renderer requirements

- **105 TeX math nodes:** 102 inline `m` plus three display `me`; there is no source MathML. A CNXML MathML copier cannot handle this source. Bind exact TeX to its owner and mixed-content slot before rendering. Preserve `\N`, `\st`, intervals, set braces, ordered pairs, recurrence initial conditions, all subscripts and punctuation tails. The only compared math-text difference is English `\text{ and }` versus Indonesian `\text{ dan }`; retain the English raw source and explicitly ledger any translated text token.
- **A real 2 × 6 table:** first row `n, 1, 2, 3, 4, ...`; second `a_n, 1, 3, 6, 10, ...`. Preserve row/cell order, ellipses and minor-rule attributes. This is PreTeXt `tabular`, not CNXML CALS or MathML `mtable`.
- **Six exercise nodes:** five ungraded responses and one numeric reading question. Its three visible slots are bound, in order, to setup answers **6, 10, 15**. Each numeric condition precedes fallback `.*` feedback. All six feedback strings belong in coverage. Do not omit the group marked `component="runestone"` simply because a new reader is offline. No WeBWorK, Sage, Python code or GeoGebra object is used in this chapter.
- **Two original TikZ graphs:** retained canonical SVGs exist under `generated-assets/rs/latex-image`, each 76 × 73 with six numeric vertex labels and no external references. Sum-seven edges are `{1,6}`, `{2,5}`, `{3,4}`; even-sum edges are `{1,5}`, `{2,6}`, `{1,3}`, `{4,6}`, `{2,4}`, `{3,5}`. Use these originals or verify a derivation; do not substitute the Indonesian web SVGs, whose dimensions and bytes differ. `graphs-7sum` is an image XML ID, but `graphs-evensum` is a **latex-image child label**. Their identity types cannot be flattened carelessly.
- **Three cross-references:** local Section 0.2 and forward Chapters 4 and 2. Until the latter Punjabi chapters exist, use explicit source/pending destinations, not dead local anchors. Two footnotes need owner/back-link preservation. All 33 index records, including nested headings and two `see` targets, need index treatment rather than unintended body display.
- **Valid mixed HTML:** several source `p` elements contain lists, display mathematics or side-by-side paragraphs. An adapter must preserve own text, child order and tails while using valid paragraph-equivalent containers. Keep the two chest inscriptions distinct and in source order. Preserve all twelve list items and the contrast between unordered sets and ordered sequences/pairs.

Neither investigation contains a supplied worked-answer key. Handshake totals, hot-dog totals, treasure-chest conclusions or a planarity proof must not be silently added to source translation. The numeric domino setup is different: its explicit answers are source material and must not be dropped.

The source defines natural numbers to include 0. Keep generic zero-based `a_0` notation distinct from the one-based Fibonacci example `f_1=f_2=1`, `f_4=3`. Domain, codomain and actual range are explicitly different; the broader B10 text requires more than the earlier provisional range gloss.

## Front matter, comparison differences and source qualifications

The cover/logo is the unchanged 100 × 142 English original. The original QR is 200 × 200. Both PNGs were actually viewed. The QR was **not decoded**: no local QR decoder was available. Its source shortdescription says `https://discrete/openmathbooks.org`, while adjacent source URL markup says `https://discrete.openmathbooks.org/`. Preserve the faulty raw description separately if improving its accessible version. The Indonesian edition replaces the QR and redirects the link; those bytes/URLs must not replace canonical English source silently.

The Indonesian colophon adds two publication/independence paragraphs and DOI/source-commit URLs. Its bookinfo adds a build-only initialism. Its second graph receives an extra detailed description. All are comparison-edition additions, not English-source content. The comparison README's full-book, page-count and WeBWorK claims also describe that Indonesian edition, never the future Punjabi opening.

Other explicit drafting cautions:

- English says the chest messages are “strangely in English”; Indonesian changes the language to Indonesian. Preserve the English-source statement unless an original adaptation is expressly identified.
- English calls the hot-dog sequences “integers (whole numbers)”; Indonesian drops the parenthetical. Keep the source wording traceable and qualify the terminology separately rather than erase the established whole-number/integer distinction.
- English spells `metroids` and `POSets`; Indonesian uses matroid/poset. Do not turn the typo into a new concept or silently fix it inside a source record.
- The source's simple-graph account uses symmetric, irreflexive relations and two-element edge sets. Do not broaden it into a claim about every later directed graph, loop or multigraph.
- The set examples `A={3,5,7}` and natural numbers below ten illustrate different descriptions; do not invent a statement that these examples all name the same set. The later four explicitly equivalent sets do name the same set.

Existing B10 LICENSE and THIRD_PARTY_NOTICES already record the active fourth-edition CC BY-NC-SA 4.0 policy and the stale canonical root BY-SA 4.0 discrepancy. Retain that policy and discrepancy, named Oscar Levin credit, English-edition attribution, change disclosure and nonendorsement. Component notices remain applicable to components actually used. This study made **no new clearance determination or supply/license audit**.

## Canon consultation and actual influence

Read six relevant loci from the established twelve-locus starter canon in existing UTF-8 text; no new source download, OCR or snapshot rewrite. Receipt: `B10-start-next-unit-20260831T001813630011Z.json`. It records exact local lines, HTML/text/paragraph hashes and uses specific to this study, not inherited PNB-001 application text.

- R1 line 39, C02 `پڑھنا چاہیدا اے`: reader-facing obligation and reflection instructions; Punjabi grammar instead of mechanically imported Urdu conjugation.
- R1 line 45, C03 `ترتیب وار`: ordinary order language for sequences and ordered pairs, not a certified technical terminology source.
- R2 line 27, C05 `تاں جے`: pedagogical purpose clauses; not a substitute for logical implication or iff.
- R2 line 33, C07 `دُوجے صفحے اُتے`: ordinal/location language; retain the mathematical indexing convention rather than forcing one-based ordinary speech.
- R3 line 25, C10 `وضاحت منگدی اے`: separately label qualifications about source/comparison wording rather than silently overwrite it.
- R3 line 38, C11 `کیوں جے`: Punjabi reason-giving prose; truth of a mathematical argument still comes from mathematical evidence.

Existing set, element, function, relation, ordered-pair, domain and range ledger entries were consulted read-only. Codomain, sequence, cardinality, recursion, combinatorics and relation-property terms require explicit provisional decisions during drafting. The prose canon is not a mathematics authority or native-reader certification. Actual draft/revision/QA consultations remain future work.

## Practical limits and handoff

Both repositories pin PreTeXt 2.27.0. The inspected Python runtime has `lxml`, but not `pretext` or `latex2mathml`; the custom XSL imports a `core/pretext-html.xsl` file absent at that path. No packages were installed and no renderer was built. Canonical tracked SVGs avoid an initial TikZ compilation requirement, but a verified local math conversion/rendering approach still needs an implementation decision.

Graph topology and numeric labels were inspected in TikZ/SVG source. The image viewer could not display SVG, so no browser-rendered graph or visual accessibility certification is claimed. The plan contains the exact source/asset hashes needed for later validation. Only the plan, these notes and the B10 canon receipt were written; translation and production should start after the parent accepts the scope.
