# Vietnamese mathematics spine

Locale `vi-Latn-VN`, allocation rank 5. Production has started; this is not a
completed textbook or curriculum. Acquired material is a translation input,
not a model-training or fine-tuning dataset.

## Read the first completed source module

Start with `review/A30-U000-module-guide.vi.html`. It links to the seventeen
lesson, exercise and glossary readers U001–U017 in pedagogical order.
Keep all readers together in the same directory. Each offline HTML file
embeds its figures and uses native MathML; no installation or network is
needed to read it. The builders verify57 cross-reader links and their target
hashes. Optional external links remain unverified and are not dependencies.

The complete translated source scope is OpenStax Precalculus2e **m49301,
Functions and Function Notation**: five objectives, fifteen worked examples,
twelve Try Its, all92 unique end exercises and eleven glossary entries.
U001–U008 contain lessons and summary; U009–U016 contain exercise categories;
U017 is the glossary. U000 adds the translated objectives/common exercise
heading and a clearly labeled authored study guide. U009 repeats two U001
Verbal exercises:94 reader occurrences do not mean94 unique exercises.

U014 completes Numeric exercises, preserving three previously translated
exercises by links and adding13 new ones. Source rounded values with incorrect
equality signs are explicitly warned about and followed by correct exact and
approximate values. U015 completes12 Technology exercises with six original
figures and twelve separately labeled closed-domain plots. U016 completes the
five Real-World exercises with unchanged units. Source answers and newly
written answers are always distinguished.

`qa/m49301-coverage.json` verifies805 sourceIDs,2081 structural content atoms,
all411 source MathML expressions and50 original figures across accepted
readers. Of those expressions,382 use direct source capture;29 use individually
reviewed equivalent notation/prose, documented in
`provenance/m49301-rendered-equivalents.json`. This structural audit supplements
actual per-unit source/translation reviews; it does not prove native fluency.
No native-Vietnamese reviewer has reviewed this work.

This is **one of87 A30 source modules**, not a completed book or curriculum.
The earlier preface `m50919` and chapter introduction `m49299` remain
untranslated because production began with the requested functions prerequisite.
Production continues in `m49304`, Domain and Range; see `NEXT_UNIT.md`.
Original prices, names, units and grading data are retained; source examples
are not claims about present Vietnamese policy.

## Read the opening Domain and Range lessons

`review/A30-U018-domain-equations.vi.html` covers the module opening and
finding domains from equations; `review/A30-U019-set-notation.vi.html`
covers interval/set-builder notation and union. Keep them beside the earlier
readers: U018 links to the module guide, and U019 links to U018.
Together these add133module-local sourceIDs,56direct sourceMathML,
seven unchanged original figures, five worked examples and five Try Its.
Both module objectives are translated; the piecewise-graph objective concerns
a later lesson. Domain and Range is not a completed module.

`review/A30-U020-domain-range-graphs.vi.html` reads domains and ranges from
graphs, retaining the oil chart's historical units and separate EIA credit.
`review/A30-U021-toolkit-domains-ranges.vi.html` covers nine basic functions
and Examples8–10, with clearly labeled arguments showing every claimed output
is attained. These add92sourceIDs,54sourceMathML,15original images,
five examples and two Try Its. The square-root source encoding is preserved.

`review/A30-U022-piecewise-functions.vi.html` covers piecewise-defined
functions, Examples11–13 and TryIt8 while retaining five original figures and
all five unfetched source Media URLs. Its narrow-screen definition is a labeled,
keyboard-focusable horizontal region; source formulas, indices and pixels are
unchanged. `review/A30-U023-domain-range-summary.vi.html` preserves all eight
Key Concepts items and links each of the source's thirteen example references
to the corresponding accepted Vietnamese reader.

`review/A30-U024-domain-verbal.vi.html` begins the end exercises with the
complete Verbal category, Bài1–5. It preserves all12 source MathML expressions,
including two meaningful empty-index square roots, and distinguishes three
source answers from two supplemental answers. No figure or cross-reader link
is introduced.

`review/A30-U025-algebraic-domains.vi.html` continues with the complete
Algebraic category, Bài6–26. It preserves all86 source IDs and31 source MathML
expressions, including Bài11's empty-index `mroot` and empty first table row,
and distinguishes ten supplied answers from eleven newly written answers.
Bài26 adds one deterministic supplemental plot of the radicand; the source
category has no figure, and the reader keeps the all-real sign proof primary.

All26 accepted readers have source/canon/build/visual reviews. Current totals
are28source examples,20TryIts,77original images and57cross-reader links.
End-exercise totals are118unique/120occurrences:92unique/94occurrences in m49301
plus26 new m49304 exercises. U019's
six-row image transcription uses three notation columns with graph descriptions
below for mobile readability; original formulas and image pixels are unchanged.
The read-only m49304 audit reports expected incomplete coverage with no integrity
issues:414/577sourceIDs,829/1051structural atoms,191/258sourceMathML and
27/44source images are accepted through Algebraic exercises6–26;35/61end
exercises and all3glossary definitions remain. The next accepted-production
target is U026, Graphical exercises27–37.

## Source acquisition and curriculum scope

`sources.lock.json` pins nine checkouts and three verified archives. The
12,102-row inventory records physically present non-catalog checkout files,
not every tracked path in sparse repositories. The catalog has another 2,673
materialized files. Archives contain 1,494 A30 Indonesian, 4,354 B60 Indonesian,
and 827 Hefferon upstream files; these counts overlap checkout inventories
where archives themselves are stored in a checkout and are not additive
measures of unique content.

| Assignment | Acquired authority | Reading-order map | Vietnamese state |
|---|---|---|---|
| A30 | Indonesian alpha.58-reader.1 plus pinned OpenStax Precalculus 2e | 87 CNXML modules | U000–U025; m49301 complete, m49304 partial;86modules incomplete |
| B20 | Indonesian CLP-1 and exact CLP1 upstream commit | 6 main-file inputs, including appendices | Not translated |
| B40 | Indonesian Hefferon source and exact embedded GitLab archive | 45 native includes, including topics/appendices | Not translated |
| B60 | Indonesian CLP-4 source archive and exact CLP4 upstream commit | 13 main-file inputs, including appendices | Not translated |
| B80 | Original Indonesian coursebook; its comparison books are not donors | 14 Quarto units | Not translated; U001 code is original scaffolding |

The A30 owner release covers 58/87 modules, ahead of the catalog's descriptive
summary. Its pinned upstream checkout contains all 87 selected prose modules
and the whole bundle media directory. Other OpenStax books' prose is not
claimed acquired. B20/B40/B60/B80 omit some generated outputs/backends as
recorded by their sparse paths. Full upstream textbook builds have **not** been
attempted; the successful build claim applies to the Vietnamese reader only.

`module-map.json` preserves native order and prerequisites. B40 requires B10
proof competence as well as A30; B60 requires B50, itself downstream of
B30/B40. Those unassigned bridges remain gaps. MV-1 is the 94-module Algebra
and Trigonometry 2e collection: 45 exact document IDs are shared with A30 and
49 are not. Shared source identities do not mean translated portfolio coverage.
SB-1 additionally needs Introductory Statistics 2e, not acquired or translated
by this assignment. No whole-portfolio equivalence is claimed.

## Reproduce the reader and checks

Run from the workspace root with Python 3.12+ and Pandoc 3.10:

```powershell
python -B vi-Latn-VN/tools/build.py
python -B vi-Latn-VN/tools/build.py --unit A30-U002
python -B vi-Latn-VN/tools/build.py --unit A30-U003
python -B vi-Latn-VN/tools/build.py --unit A30-U004
python -B vi-Latn-VN/tools/build.py --unit A30-U005
python -B vi-Latn-VN/tools/build.py --unit A30-U006
python -B vi-Latn-VN/tools/build.py --unit A30-U007
python -B vi-Latn-VN/tools/build.py --unit A30-U008
python -B vi-Latn-VN/tools/build.py --unit A30-U009
python -B vi-Latn-VN/tools/build.py --unit A30-U010
python -B vi-Latn-VN/tools/build.py --unit A30-U011
python -B vi-Latn-VN/tools/build.py --unit A30-U012
python -B vi-Latn-VN/tools/build.py --unit A30-U013
python -B vi-Latn-VN/tools/build.py --unit A30-U014
python -B vi-Latn-VN/tools/build.py --unit A30-U015
python -B vi-Latn-VN/tools/build.py --unit A30-U016
python -B vi-Latn-VN/tools/build.py --unit A30-U017
# Guide after its seventeen targets, then the dependent Domain and Range readers.
python -B vi-Latn-VN/tools/build.py --unit A30-U000
python -B vi-Latn-VN/tools/build.py --unit A30-U018
python -B vi-Latn-VN/tools/build.py --unit A30-U019
python -B vi-Latn-VN/tools/build.py --unit A30-U020
python -B vi-Latn-VN/tools/build.py --unit A30-U021
python -B vi-Latn-VN/tools/build.py --unit A30-U022
python -B vi-Latn-VN/tools/build.py --unit A30-U023
python -B vi-Latn-VN/tools/build.py --unit A30-U024
python -B vi-Latn-VN/computing/check_domain_range_graphs.py --originals
python -B vi-Latn-VN/computing/check_toolkit_domains_ranges.py --originals
python -B vi-Latn-VN/computing/check_piecewise_functions.py
python -B vi-Latn-VN/computing/check_domain_range_summary.py --originals --readers
python -B vi-Latn-VN/computing/check_domain_verbal.py
python -B vi-Latn-VN/computing/check_domain_verbal.py --originals
python -B vi-Latn-VN/computing/check_algebraic_evaluation.py --originals
python -B vi-Latn-VN/computing/check_graphical_injectivity.py --originals
python -B vi-Latn-VN/computing/check_relations.py
python -B vi-Latn-VN/computing/check_notation.py
python -B vi-Latn-VN/tools/test_tools.py
python -X utf8 -B vi-Latn-VN/tools/test_audit_m49301.py
python -X utf8 -B vi-Latn-VN/tools/audit_m49301.py
python -X utf8 -B vi-Latn-VN/tools/test_audit_m49304.py
# Exits1 while the module is incomplete; inspect JSON result/issues.
python -X utf8 -B vi-Latn-VN/tools/audit_m49304.py
```

The accepted package contains77 unchanged source image assets and12 newly authored plots. Reading the finished HTML
never requires the large downloads. Rebuilding U006/U007 currently also requires
the pinned EN/ID `m49301/index.cnxml` files in `downloads/`, because their checkers
compare source boundaries and content directly. U001–U005/U008–U017 can rebuild
from committed inputs, with U008/U009/U013/U014 also requiring earlier sibling readers.
U018/U019 also use committed inputs and the earlier U000/U018 reader targets.
U020–U024 rebuild from committed excerpts, drafts and images; their unit checks
can also use the pinned EN/ID originals and relevant inherited rows.
U000/U004/U005/U008/U010/U012/U015 add optional original-source checks when downloads are present;
their reported assertion counts therefore depend on that presence. U018/U019 likewise check optional EN/ID originals and inherited asset rows when present. Rebuilding U015 uses its committed PNGs, but its current checker also imports Pillow. Reproducing exact PNG bytes additionally requires the recorded Arial font and matching rendering runtime. U011's
standalone438 checks need no downloads; its separate `--originals` run adds7.
U013's standalone117 checks need its five committed images; `--originals` adds23.
The builder checks deterministic Pandoc output,
source anchors, local links, NFC Vietnamese, embedded images, original numerical
exercise data and final-draft-bound canon receipts. With pinned originals present,
all twenty-five builders report4217 combined source/structure/arithmetic assertions
(3011 for m49301 plus228/150/134/254/245/83/112 for U018–U024); these are not4217
mathematical claims. Twenty-one acquisition/output/render/link safety tests,
21m49301 audit tests and62m49304 audit tests pass. Safety checks include refusing low-space
writes while retaining an existing reader. Generated readers and receipts use
same-directory atomic replacement after complete bytes are saved.
Technical source IDs merged into a translated block retain alias anchors; this
is not a claim that every source paragraph was translated separately. Duplicate
end exercises are recorded separately from newly completed unique exercises.

To inspect or reproduce acquisition:

```powershell
python -B vi-Latn-VN/tools/acquire.py
python -B vi-Latn-VN/tools/verify_sources.py --full
# Only on a machine with sufficient free space:
python -B vi-Latn-VN/tools/acquire.py --apply --with-canon
```

Acquisition is a dry-run unless `--apply` is supplied. It refuses mismatched
existing files/checkouts and unsafe archive paths, and will not acquire with
less than 3 GiB free. It is not a repair or cleanup command. Live canon HTML
can change; a checksum mismatch must be investigated, not silently accepted.
`verify_sources.py --full` hashes all inventoried checkout bytes, checks archive
SHA-256/CRC and extracted members' CRCs, and checks native-unit and crosswalk
identities. The recorded acquired checkout hashes include this Windows host's
CRLF materialization; a normal LF checkout can fail size/hash checks even at the
same commit. Acquisition currently inherits the host's Git newline settings.
Do not waive mismatches: the materialization profile must be reproduced or an
explicit provenance migration reviewed. Git commit/tree identities remain the
source authority. See `qa/m49301-reproducibility.md` for the source, tool,
Pillow/font, and visual-QA dependencies; same-host HTML determinism does not
promise cross-platform screenshot identity.

Visual QA used the Browser skill; its in-app connection failed before setup,
so an isolated headless Edge process rendered the local reader. No signed-in
browser or user profile was accessed. `tools/visual_qa.cjs` captures desktop and
390-pixel layouts after a local HTTP server is started; pass `A30-U002` as an
argument to review that unit (or `A30-U003` for tables). Browser screenshots remain
under ignored `build/vi-visual-*` directories. Automated geometry and image-loading
checks do not replace model visual review; receipts distinguish both. U004's
first visual pass exposed long MathML rendered as markup; the builder now checks
every source formula survives rendering, and removes only source layout containers
that contain no mathematical tokens. U001–U005 were rebuilt after that fix. The final module audit also caught malformed MathML in two U004 table headers. Those source expressions now sit above true tables with matching column labels; a new pre-write XML/boundary guard rejects this failure. All18 readers were rebuilt with the stronger guard. U014's three wide source answer rows are keyboard-focusable scroll regions, followed by readable vertical tables.
Empty-layout pruning is opt-in per unit: U021 explicitly disables it because
the source square root uses a meaningful empty index in an `mroot` element.
Its original structure and its rendered square root were both checked.
U022 also preserves its source MathML exactly; visual QA added only a labeled
scroll frame around one long definition after a390-pixel capture exposed clipped
branch indices. U023's thirteen source example references were actually clicked
and checked against current target hashes. U024 used the in-app browser through
a local-only loopback server; complete900/390-pixel captures verified all five
exercises, answer labels and radical/interval rendering. Its1280-pixel DOM
geometry passed, while host display scaling cropped that screenshot surface;
the receipt records the limitation instead of treating the crop as full evidence.

## Language and continuation discipline

`canon/README.md` locates 12 examples in two Vietnamese references. Selected
PDF pages were OCRed, read and checked against page images; HTML retained
readable LaTeX. These are language witnesses, not content donors or mathematical
authority. Relevant originals must be reread before drafting, during examples
and solutions, and after editing. Each final review is bound to the draft hash.

The primary domain term is **tập xác định**; **miền xác định** is a synonym.
Range is **tập giá trị**, distinct from codomain. A source-scope note explains
OpenStax's broad function/mapping convention for nonnumeric labels. No native
Vietnamese speaker review has been performed. See `terminology.csv`,
`DECISIONS.md`, `STATUS.json`, `GOAL.md`, and `NEXT_UNIT.md` for recovery.
Read the user's messages directly in coordinating task
`[local-task-id]`; summaries are not authority.

## Attribution and component licenses

A30's text, translated adaptation and76of77 retained original figures use CC BY-NC-SA 4.0,
with Jay Abramson/OpenStax attribution and independent-adaptation notice.
Original frontmatter and source notices are preserved in `notices/`; admitted
pilot figure rows are in `provenance/pilot-asset-notices.json`; U018–U022 have
their own asset-notice receipts. U020 Figure009 (Alaska oil) carries the existing
EIA public-domain exception, `VERIFIED_EIA_PD / LicenseRef-US-PD`, with its
original credit and URL retained separately. Later figures may have individual
exceptions: carry each existing component row forward rather than extending
these component terms to the whole book. Other courses
retain their own notices and licenses. Original local scripts have a separate
MIT notice. No blanket license replaces those component terms. This task has
not independently pushed this checkpoint. The coordinator reports that the
user-authorized single GitHub review branch exists but its initial upload is
partial; exact accepted snapshots remain distinct from working drafts.
