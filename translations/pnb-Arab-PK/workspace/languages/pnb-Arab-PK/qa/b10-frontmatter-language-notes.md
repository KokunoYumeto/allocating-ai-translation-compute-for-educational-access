# B10-frontmatter — complete input checkpoint

This checkpoint translates the entire earlier canonical front matter of Oscar Levin's *Discrete Mathematics: An Open Introduction*, fourth edition. It does not complete B10 or the five-work assignment. It creates no reader, asset copies, runtime, training data or new license/supply audit.

## Authority and exact boundary

Read the actual user instructions, language goal, source lock and B10 start plan. English authority is `oscarlevin/discrete-book` commit `82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799`; Indonesian comparison is `KokunoYumeto/discrete-mathematics-open-introduction-id` commit `e94905932301e699b7c4d44e88ec54e972b886b6`. Both pinned checkouts were rechecked clean. The complete English and Indonesian frontmatter and bookinfo were read; the English fourth edition remains authoritative, not OpenLogic or the root README's stale third-edition description.

The witness expands only complete `bookinfo.ptx` and complete `frontmatter.ptx` into the original `dmoi.ptx` pretext/book structure, preserving title, subtitle and source attributes. All original comments are retained. Later chapter includes are deliberately outside this bounded witness. The final included component is the second preface's Interactive Online Version group, including its final paragraph, sidebyside shortdescription, QR image and every closing container. First outside is `./ch_intro.ptx`, `ch_intro`, Introduction and Preliminaries, proposed B10-001.

The manifest records exact Git blob bytes/SHA-256/blob-SHA-1 separately from working-tree raw bytes. For these selected PTX/TEX files, working CRLF normalized to LF equals the pinned Git blob. That is not a universal normalization assumption: the retained canonical root LICENSE has tracked CRLF. Archived notice inputs retain their existing raw and logical-LF hashes; notice wording was not changed.

## Complete coverage

There are exactly **50 ordered source keys**: 42 full-frontmatter slots, 2 book title/subtitle slots, and 6 docinfo slots (blurb shelf, blurb text and four rename labels). Every active paragraph and preface is translated, not summarized.

- Four original IDs, in order: `dmoi4`, `frontmatter`, `preface`, `pref_editions`. Most source blocks have no ID; documented filename/XPath keys must not be represented as original IDs.
- Titlepage, colophon, dedication, acknowledgement and both full prefaces are retained in order. First preface has no explicit source title; the second is How to Use This Book.
- 25 paragraphs, 7 explicit frontmatter titles, 6 paragraphs groups, one 4-item unordered list, 2 attribution lines.
- 4 source url elements; the brandlogo's URL is separate metadata, not a fifth frontmatter url element.
- 8 q, 5 em, 1 inline pretext marker and the copyright ndash. The document root is also called pretext; do not count it as inline text.
- No active source MathML, m/me mathematics, tables, footnotes, exercises, figures, captions or explicit line-break elements. XML indentation/newlines remain in the witness and source records; they are not invented HTML br elements.
- Docinfo document-id, macros, latex-image-preamble, cross-reference settings and source rename attributes remain intact as source metadata. The single `assets/tikz-defs.tex` include keeps `parse="text"`, with its canonical resolution and hash recorded. It is inert: no upstream TeX, software, analytics or runtime code was executed.

The one source paragraph containing ul has translated own prose followed by exactly `{{child:0}}`; its four descendant item paragraphs are separate keys. A future renderer must use a valid paragraph-equivalent container or split around the list, preserving child order without duplication.

## Credits, dates and source-attributed claims

Oscar Levin, Mathematical Sciences, University of Northern Colorado, Fall 2024, copyright 2013–2025, and both exact attribution lines remain source-bound. All personal names and the quoted *Discrete and Combinatorial Mathematics,* title retain original English spelling in LTR isolation. Dedication and every acknowledgement are included. The 4th-edition/August 2024 blurb, Fall 2024 titlepage and 2013–2025 copyright are retained as different source fields, not forced to agree.

The source's first-person author voice stays intact. A separate original opening note identifies that voice as Oscar's and marks access, custom-edition, licensing, institutional and interactive-feature statements as claims in the pinned source. They are not new current legal advice, verification, local availability or implemented-service promises. The source nearly 300 new / more than 750 exercises claim is translated with both qualifiers; it is not the coverage count of this Punjabi checkpoint.

The inherited B10 notices already record active fourth-edition CC BY-NC-SA 4.0 and the stale root BY-SA 4.0 discrepancy. This task retains that record, author/edition attribution, change identification and non-endorsement. It does not grant new image clearance or resolve rights anew. No source licenses or notices were altered.

Indonesian adds two colophon paragraphs (independent translation/source commit and edition DOI), an initialism in docinfo, its own final website and a different QR image; it relocates the QR description into image. Those were read as comparison-edition additions, not silently imported into canonical source blocks. An original Punjabi note explains that distinction without attributing Indonesian publication claims to Oscar.

## Images and source discrepancy

Neither image was copied or modified. Canonical originals were visually inspected during the immediately preceding B10 source study; this task rechecked exact identities and dimensions.

| Component | Canonical identity | Treatment |
| --- | --- | --- |
| brandlogo cover4 | 100×142 PNG; SHA-256 `e6cb97c02b6be3d53964e971661684d806b3fb04941d028c1dd3743bb5d28870` | Original purple English cover, not a newly translated cover or numbered figure. Source has no alt; the plain Punjabi visible-shape description is explicitly original. |
| sidebyside qrcode | 200×200 PNG; SHA-256 `25ac46ed89c1547d707f6aff76d0e9c338ea7eb51efe4d077e19be0b6aea183e` | Keep original QR, not Indonesian replacement. Source shortdescription belongs to sidebyside, not image. |

The raw English description is `QR Code to https://discrete/openmathbooks.org`, whereas its adjacent source URL is `https://discrete.openmathbooks.org/`. The faithful Punjabi source-description key preserves the malformed URL literally. The original accessible override does not claim a decoded destination; the visible `b10-frontmatter-qr-note` explicitly says decoding was not performed. A future reader must retain raw source alt/description separately and associate the corrected accessible text with that visible note through aria-describedby/correction linkage. Do not erase the error from provenance or substitute the comparison QR.

## Draft, revision and QA language decisions

Actual full local canon paragraphs were consulted at all three stages, with distinct receipts. They supply Punjabi prose/register evidence, not mathematical terminology authority or endorsed historical claims. No canon snapshots were rewritten or downloaded.

- Draft: R1 C01/C02/C04, R2 C05/C06/C07, R3 C10/C11/C12. Passive ability, reader instruction, plural agreement, purpose, alternatives, locative ordinals and explicit qualifications influenced complete prose.
- Revision: R1 C01/C02/C03, R2 C05/C06, R3 C09/C10. Revised both should-be-able clauses to `دے سکن جوگے ہونے چاہیدے او`, retaining expectation rather than guaranteeing success; removed draft `ہووو` typo. Standardized `تہانوں`; replaced awkward hosted wording with `اُتے اوہدی میزبانی کیتی جاندی اے`.
- QA: R1 C02/C04, R2 C05/C07, R3 C10. Rechecked modality, quantity qualifiers, purpose rather than implication, edition/reference order and source-versus-original qualifications.

Important provisional terms and choices:

| Source notion | Punjabi choice and limit |
| --- | --- |
| discrete mathematics | `ڈسکریٹ ریاضی`, with an original explanatory bridge and Urdu `منفصل ریاضی`; not a claim of standardized Punjabi terminology. |
| inquiry-based learning | `کھوج کر کے سکھنا`; full pedagogical explanation retained rather than replacing it with Urdu nominalizations. |
| preview activities | `ابتدائی سرگرمیاں`, distinguished from open-ended `کھوج لاؤ!` questions; source former/latter and before-reading expectation preserved. |
| combinatorics | `گِنن تے جوڑ بناؤن دی ریاضی`, provisional descriptive phrase with separate Urdu/English term bridge. |
| sequences | Revised over-narrow `عددی ترتیبیں` to `ترتیب وار سلسلے`. C03 supports ordinary ordered phrasing only; mathematical use remains provisional and does not imply all sequences are numeric. |
| randomized components | Revised mere disorder wording to `اتفاقی چُون نال بدلّن والے حصے`, preserving random selection and varying practice instances. |
| induction / generating function / relation | `ریاضیاتی استقرا` / `پیدا کرن والا فنکشن` / `تعلق`; provisional and linked to English/Urdu only in the original bridge. |
| Python scratch pad | `Python وچ کوڈ آزماؤن دی اک کچی کاپی`, preserving the pencil icon and optional code experimentation claim. Source lower-case python is a software-name capitalization normalization, not executable code. |

English proper names, visible URLs and ASCII numerals are LTR-isolated inside translated blocks. Alt overrides remain plain strings, not HTML. Source institutional names and titles remain traceable in raw metadata even when the department/title prose is translated.

The manifest records punctuation relocations: the period inside source `real world.` moves to the Punjabi sentence ending after its predicate; previous-edition parentheses become em dashes/semicolons; the numbering assurance becomes a clause; chapter-review qualification is integrated into Punjabi word order. The copyright character stays en dash, not hyphen or mathematical minus. The quoted bibliographic title's comma is retained. No mathematics was altered.

## Input QA and repeatability

Two final read-only in-memory Python/lxml/Pillow/Git runs returned identical reports: **1,779 assertions and 19 rejected detached mutations**. This total includes repetitive per-key/per-name checks (including zero-occurrence checks), not 1,779 independent linguistic judgments or a quality score. No real source, translation or asset was mutated for these tests.

Checks bind the witness's complete docinfo/frontmatter trees, including comments, to pinned Git source; compare every source node's tag, attributes, own text, tail and child order; derive the 50 keys independently; preserve all IDs/ancestry, metadata, images and URLs; compare each translated block's source numerals, named people, quote/emphasis owner counts, placeholders and Latin isolation. Notice hashes are retention checks, not a new audit.

Detached failures covered omitted/reordered blocks; 750→751; en dash→hyphen; author alteration; date erasure; Indonesian link substitution; QR discrepancy erasure; missing list slot; literal invalid ul injection; emphasis removal; loss of LTR isolation; substituted QR hash; changed ID ancestry; parse=text→XML; injected canonical paragraph; changed source root child order; an original current-license-verification promise; and a falsely certified QR payload. Full original bridge/alt hashes guard the reviewed text against later unauthorized changes; they are regression guards, not independent semantic verification.

Final core inputs:

- Witness: `997ed1b17cf0fd67b9ef8a4c4e3a5ebb598630005beeb93aaddd64dad2fc61cb` (16,704 bytes).
- Manifest: `5727f55d46d3b255b49982ff9cee6a200b3949e3d17b07cfda7cd07a42dfe73f`.
- Translation: `b03ec3b8767e937ce8e7828e5d4361883625993241054b5fa72db44e56f00b05`.

The final deterministic report is retained below. The validation was ad hoc and read-only; no production QA script is claimed in this input-only scope. Future reader QA must independently rederive these bindings from the source and test the actual DOM, bidi layout, images, links and source/original separation.

```json
{
  "status": "passed input-only source-bound checks",
  "assertions": 1779,
  "detached_mutations": 19,
  "mutations": [
    {
      "name": "delete one preface paragraph key",
      "rejected_by": "exact key order"
    },
    {
      "name": "swap two complete paragraph slots",
      "rejected_by": "exact key order"
    },
    {
      "name": "750 changed to 751",
      "rejected_by": "frontmatter.ptx#/frontmatter/preface[1]/paragraphs[1]/p[1]/ul[1]/li[1]/p[1] numerals"
    },
    {
      "name": "copyright en dash changed to hyphen",
      "rejected_by": "frontmatter.ptx#/frontmatter/colophon[1]/copyright[1]/year[1] exact dash marker"
    },
    {
      "name": "author name changed",
      "rejected_by": "frontmatter.ptx#/frontmatter/titlepage[1]/author[1]/personname[1] name Oscar Levin"
    },
    {
      "name": "source institution date erased",
      "rejected_by": "retained author date copyright"
    },
    {
      "name": "link target replaced by Indonesian destination",
      "rejected_by": "URL binding u4"
    },
    {
      "name": "raw QR alt discrepancy erased",
      "rejected_by": "raw QR URL not erased"
    },
    {
      "name": "list child placeholder deleted",
      "rejected_by": "frontmatter.ptx#/frontmatter/preface[1]/paragraphs[1]/p[1] child slots"
    },
    {
      "name": "literal ul injected into translation paragraph",
      "rejected_by": "frontmatter.ptx#/frontmatter/preface[1]/paragraphs[1]/p[1] inline-only valid XML"
    },
    {
      "name": "source emphasis erased",
      "rejected_by": "frontmatter.ptx#/frontmatter/preface[1]/p[2] em source-owner count"
    },
    {
      "name": "LTR isolation removed from numerical claim",
      "rejected_by": "frontmatter.ptx#/frontmatter/preface[1]/paragraphs[1]/p[1]/ul[1]/li[1]/p[1] Latin/digit isolation"
    },
    {
      "name": "image replaced with comparison QR hash",
      "rejected_by": "image exact bytes qrcode"
    },
    {
      "name": "source ID ancestor changed",
      "rejected_by": "source IDs exact ancestry order"
    },
    {
      "name": "inert preamble include relabeled as XML",
      "rejected_by": "one inert parse-text include"
    },
    {
      "name": "canonical author source node injected",
      "rejected_by": "excerpt hash/bytes"
    },
    {
      "name": "source root own child order changed in manifest",
      "rejected_by": "every source node own text tail children order"
    },
    {
      "name": "original current legal verification promise inserted",
      "rejected_by": "reviewed claim limits bridge_before_html"
    },
    {
      "name": "original QR alt falsely certifies payload",
      "rejected_by": "reviewed conservative alt qrcode"
    }
  ],
  "counts": {
    "translation_keys": 50,
    "original_ids": 4,
    "prefaces": 2,
    "paragraphs": 25,
    "list_items": 4,
    "urls": 4,
    "source_images": 2,
    "q": 8,
    "em": 5,
    "math": 0,
    "tables": 0,
    "footnotes": 0
  },
  "input_hashes": {
    "witness": "997ed1b17cf0fd67b9ef8a4c4e3a5ebb598630005beeb93aaddd64dad2fc61cb",
    "manifest": "5727f55d46d3b255b49982ff9cee6a200b3949e3d17b07cfda7cd07a42dfe73f",
    "translation": "b03ec3b8767e937ce8e7828e5d4361883625993241054b5fa72db44e56f00b05"
  },
  "limits": [
    "Static input-only QA; no reader/builder/browser tests.",
    "Per-block numerals/names/links/markup source-bound; semantic translation adequacy still requires a fluent reviewer.",
    "Original bridge/alt mutation guards are reviewed-content regression hashes, not independent semantic verification.",
    "No source QR decoding, current external website/legal verification or new audit."
  ]
}
```

## Remaining work

Reader preparation/build, original asset copies, full source-bound reader QA, desktop/mobile visual inspection and fluent Punjabi/mathematics educator review remain. No QR decoding or current external service verification was performed. Broader term authority remains limited to the current prose canon and explicit provisional choices.

After this complete earlier-frontmatter input checkpoint, the next coherent substantive draft is full Chapter 0 B10-001 (the chapter introduction plus both complete active sections), as scoped in B10-start.json. No Chapter 0 text was translated in this task. All sources and the whole five-work workflow remain required.

