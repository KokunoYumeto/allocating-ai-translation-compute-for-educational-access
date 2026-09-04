# MR-BRIDGE-024 drafting record

2026-09-01. Writer: freeze_regressions. Status: source-faithful translation draft of m81427 metadata/objectives, all three readiness notes, and the complete first teaching section; not independently reviewed, frozen, built, rendered, teacher-approved, published, or a module/book-completion claim. This worker owned only the024 XML/config/this record and bounded ignored original-image review copies. Root owns freeze/assets, build/render QA, independent review, shared ledgers/staging and any branch export.

## Pinned source and exact boundary

Both complete pinned module members were read directly, followed by bounded element-level comparisons of the exact selection. No HEAD checkout, bulk extraction or new corpus acquisition was used.

|Source|Exact member|Bytes|SHA256|
|---|---|---:|---|
|EN|`osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81427/index.cnxml`|166406|`2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5`|
|ID|`source/modules/m81427/index.cnxml`|168909|`2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112`|

Metadata agrees: content-id `m81427`; UUID `b9f8475e-9490-4f24-995f-2923b1ed9644`; EN document and md:title `Solve Systems of Linear Equations with Two Variables`; ID document and md:title `Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel`; ID alone records `xml:lang="id-ID"`. The complete five-item objective list and its introduction are translated in source order under IDs `para-00001` and `list-00001`.

The assigned content boundary is exactly three direct readiness notes plus all twelve direct non-title children of section wrapper `fs-id1167835596566`; stop before sibling `fs-id1167832086919`. Ordered content selectors:

```text
fs-id1167830925402
fs-idm321747056
fs-idm337329376
fs-id1167831883449
fs-id1167835194597
fs-id1167834061509
fs-id1167831040311
fs-id1167834479634
fs-id1167835513953
fs-id1167835301937
fs-id1167834063240
fs-id1167835167507
fs-id1167835326515
fs-id1167832066187
fs-id1167834132168
```

Those 15 content selectors contain 56 self/descendant source IDs. Adding the uncounted original section wrapper gives the assigned 57-ID teaching footprint. Because the task also requires the two metadata-objective IDs, the complete target footprint is 17 direct `data-source` selections and 59 source IDs. This distinction is explicit rather than silently calling metadata absent. The target has 62 IDs total after its own article/readiness/credits IDs; all are unique. Exact source-ID order and nearest-source-ID ancestry agree with EN and ID.

Coverage: six exercises and six supplied solutions; one worked example; two definition-like teaching notes; two Try It notes; three readiness notes; two term IDs; one standalone equation; twenty source MathML nodes; two media/images. There are no missing source answers in this selection. The complete module-level glossary has four definitions for the whole later module and lies outside this bounded selection; it is not mislabeled as part of the first topic. The two definitions actually repeated inside the selected teaching section are preserved in full.

## Complete content and mathematical checks

All twenty MathML nodes are structurally identical between EN and ID after XML parsing; concatenated canonicalized digest `f84a277a953854a8410227126a245f4b412e56b339c80dc3ce864012efda06ca`. In source order they encode:

1. readiness: `y=(2/3)x−4`, `(6,0)`, `(−3,−2)`; answer yes/no;
2. readiness: `3x−y=12`; answer `m=3; b=−12`;
3. readiness: `2x−3y=12`; answer `(6,0),(0,−4)`;
4. the system `{2x+y=7; x−2y=6}`, repeated line `2x+y=7`, and two generic `(x,y)` pairs;
5. worked system `{x−y=−1; 2x−y=−5}` and pairs `(−2,−1)`, `(−4,−3)`;
6. Try It system `{3x+y=0; x+2y=−5}` and pairs `(1,−3)`, `(0,0)`;
7. Try It system `{x−3y=−8; −3x−y=4}` and pairs `(2,−2)`, `(−2,2)`.

Independent exact arithmetic rechecked every supplied result. For the first readiness equation, `(6,0)` satisfies it while `x=−3` yields `y=−6`, not `−2`. Solving `3x−y=12` for y gives slope3 and intercept−12. The two intercept substitutions for `2x−3y=12` give `(6,0)` and `(0,−4)`. In the worked example, `(−2,−1)` makes the first equation true but gives `−3≠−5` in the second, whereas `(−4,−3)` makes both true. Try It results are respectively yes/no and no/yes; all four were checked against both equations, not inferred from the answer words.

The target has 32 checked math strings: all twenty source MathML values plus twelve exact accessible transcriptions from the two source solution rasters. The latter reproduce both substitutions, both equality tests/results and both conclusion pairs; they are source-image translations, not newly invented solutions. Six problem/solution pairs have bidirectional local links.

The three readiness source references retain exact document/target pairs: `m81369#fs-id1167835400321`, `m81370#fs-id1167835342973`, and `m81369#fs-id1167827987818`. The opening `m81361` source link has no target ID in either source and remains an external chapter-introduction link. The Marathi reader warns that these linked earlier modules are not translated inside this unit and require internet; no direct offline-reference claim is made.

## EN/ID textual differences and source interpretation

EN and ID have the same selected structure, ID/type order, MathML, link targets, image filenames/mime types, classes and answers. No numerical source correction was required.

Three ID spacing defects were not copied into Marathi: readiness2 has `y` immediately followed by `dari`; readiness3 repeats that defect; opening paragraph `fs-id1167831883449` joins the end of its link directly to `kita` and omits EN's separator. Marathi supplies normal word separation. In `fs-id1167834061509`, EN says larger systems are solved “later in this chapter”, while ID narrows this to a following section. Marathi follows EN's non-specific `या प्रकरणात पुढे`, because several later methods intervene.

The source says a two-variable linear equation has infinitely many solutions and its graph is a line; every line point is a solution and every solution is a line point. It then defines a system solution as values making all equations true. The translation preserves both directions and the requirement that both/all equations be true. It does not infer that merely satisfying one equation is enough.

The source's “now”, “later in this chapter” and instructional references are preserved as source-relative navigation, not current-world claims. This slice has no new time-sensitive factual statement comparable to m81375's autonomous-car sentence.

## Actual original-image reading and provenance

After exact filenames were established, the only helper write was its permitted named-original review mode:

```powershell
python -B mr-Deva-IN/tools/freeze_unit.py --review-images MR-BRIDGE-024 A20 CNX_IntAlg_Figure_04_01_001_img.jpg CNX_IntAlg_Figure_04_01_002_img_new.jpg
```

All four EN/ID originals were then personally opened at original detail, not inferred from the receipt. Each review copy was compared byte-for-byte with its exact ZIP member.

|Image|Locale|Bytes|Pixels|SHA256|Review copy|
|---|---|---:|---:|---|---|
|`CNX_IntAlg_Figure_04_01_001_img.jpg`|EN|97207|426×216|`91523ae06f844c76cfa90cd410bb6a0237969334a4922132e09434bb684ffb02`|byte-exact|
|same|ID|82575|1340×660|`b1814e1dd3b4bfbcc8493e832367b005f89abf57849dc8c25ddb8d039cbac594`|byte-exact|
|`CNX_IntAlg_Figure_04_01_002_img_new.jpg`|EN|73865|409×154|`2ed7001540a6eca5079fc199f19f7812816813f36b685f448db4a309f6707d64`|byte-exact|
|same|ID|85859|1340×660|`881d3da3e258328d5405420c4084f39fa226deb3ad6daf8686ab14225d3b921e`|byte-exact|

The locales are deliberately not byte-identical. EN figure001 shows the system at top, colored substituted x/y values, both checks and two English conclusions. ID figure001 is a larger Indonesian redraw that begins with the substitution instruction and omits the separate top system, but its two equations/checks/conclusions agree. Figure002 has the same correct two equality checks and solution conclusion in both languages, again with different layout/localization. The target retains the unchanged canonical EN images and provides detailed Marathi alt plus visible Marathi transcripts. Added figcaptions are explicitly original-labelled because neither source has a caption element.

Config intentionally has no `assets` field before root's freeze. This worker did not copy an ID redraw into the target or alter any image.

## Stage-specific Marathi canon use and limits

The actual current user workflow was read directly. Canon checks were targeted to this topic, not a repeated broad acquisition or glossary-only exercise.

Selection: read C12 local OCR `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`, physical page85/printed75 opening through the four equal-operation rules. It defines `उकल` as the value making both sides equal, says solving means finding that solution, and requires the same operation on both sides, including nonzero division. Read C13 `balbharati8-86.txt` readable prose applying those operations through several methods; its formula OCR is corrupt in places and was not adopted. Concrete effects: use `समीकरण`, `उकल`, `सत्य`, and keep substitution checks as equality tests rather than treating a displayed pair as automatically valid.

At selection the already retrieved actual C18 Marathi Vishwakosh [आलेख](https://vishwakosh.marathi.gov.in/24316/) opening and जात्याक्ष passages were also read. They define a graph as a geometric depiction of relationships and explain horizontal/vertical axes and ordered coordinates. Concrete effects: retain `आलेख`, preserve source Latin x/y and first/second coordinate order, and keep the exact claim that solutions correspond to line points. C18 does not establish this system's solution set or the compound system terminology; those still come from the mathematical source.

Drafting: reread the same C12/C13 prose after the first XML pass, and reread the actual C18 relationship/axis/coordinate passage. The definition was revised to say explicitly that all equations must be true; image transcripts retain equality and inequality signs exactly. A targeted local search found no readable simultaneous/system-of-equations phrase in the present canon. Therefore `रेषीय समीकरणांची प्रणाली`/`समीकरण-प्रणाली` are disclosed working translations rather than invented canon attestations. Likewise the full method compounds `प्रतिस्थापन पद्धत` and `विलोपन पद्धत` are authored objective translations; this slice does not yet teach those later methods.

The established slope word `उतार` comes from registered C22 geometry evidence actually read in earlier line-topic work. For this unit the prior externalized record was consulted, not misrepresented as a fresh primary-page retrieval. Its narrow term use applies to readiness2 only. Existing C20 evidence supports `महिरपी कंस`; no new C20 locator/read is claimed here.

Revision/final: the relevant C12 equal-operation/solution prose and actual C18 relationship/coordinate prose are reread again after source/math/image validation. This final pass keeps x/y/m/b unchanged, keeps the graph claim scoped to one equation, and leaves the full system phrase visibly authored. No browser, alternate browser, new web acquisition, formula-image canon claim or shared canon/terminology edit occurred. No canon access failed; the only limitation is visibly corrupt C13 formula OCR, whose readable prose alone was used.

## Actual next source census

The immediate next sibling in both sources is complete section `fs-id1167832086919`, EN “Solve a System of Linear Equations by Graphing”, ID “Menyelesaikan Sistem Persamaan Linear dengan Menggambar Grafik”. It has 39 direct non-title selectors, 153 self/descendant IDs plus its wrapper =154, 15 exercises and 15 supplied solutions, five worked examples, ten Try It notes, one how-to note, two additional ordinary notes, 32 MathML nodes, 23 images, and one source table. First selector `fs-id1167831893670`; last `fs-id1167832060470`. Its next sibling is `fs-id1167834233994`, “Solve a System of Equations by Substitution” / ID equivalent.

Ordered direct selectors for a future scoped plan:

```text
fs-id1167831893670
fs-id1167831239781
fs-id1167835267322
fs-id1167832082005
CNX_IntAlg_Figure_04_01_003
fs-id1167834053646
fs-id1167834279490
fs-id1167832195749
fs-id1167832065745
fs-id1167826804684
fs-id1167835310198
fs-id1167832055393
fs-id1167835410272
fs-id1167832086965
fs-id1167835366362
fs-id1167834462906
fs-id1167835307740
fs-id1167835329190
fs-id1167835364524
fs-id1168754384001
fs-id1167835418145
fs-id1167832076598
fs-id1167835186730
fs-id1167831954237
fs-id1167835530462
fs-id1167831191430
fs-id1167827987930
fs-id1167834063977
fs-id1167831880100
fs-id1167835370836
fs-id1167835343554
fs-id1167835421108
fs-id1167832057993
fs-id1167835170706
fs-id1167832096973
fs-id1167834191318
fs-id1167832151520
fs-id1167831910867
fs-id1167832060470
```

No next-section image was copied and no next-section translation was drafted. Its size is reported for the next deliberate boundary decision, not silently treated as part of024.

## Writer checks and remaining workflow

Read-only XML/JSON/ZIP/Pillow/Fraction assertions currently pass:

- 17 exact source references in order; 59 exact source IDs, all unique and with exact nearest-source-ID ancestry; 62 total target IDs;
- 20 byte-equivalent EN/ID MathML structures; 32 checked target math strings matching config exactly;
- six non-tautological equation/pair evaluations and six supplied answers; six bidirectional problem/solution links;
- two exact canonical image references and all four review copies byte-equal to their ZIP members;
- exact module metadata, all objectives, required terms, source-class preservation, valid local anchors, parseable XML/JSON, and no pre-freeze assets field;
- EN/ID parity for the next-section census above.

No main `freeze_unit.py UNIT`, build, browser, renderer, shared-ledger/helper/status edit, commit, push, deletion, cleanup or general licence audit was performed. This is writer verification, not independent mathematical or human-language approval. Root must freeze, independently review, build and perform reader QA. The full five-book assignment continues.

Final pre-freeze pins: XML26332bytes,SHA256 `7468c2fe7bb4017eecbed7035708a71905bbba2744ecb25f0f5aea3226709570`; config2146bytes,SHA256 `8f90e0a892053f97c5fff64038a4f3117e0af322cfbe0ccc29596f3dd863599f`. Latest observed free space was7,434,399,744bytes. This worker performed no cleanup/deletion/move and draws no conclusion from shared-disk changes.
