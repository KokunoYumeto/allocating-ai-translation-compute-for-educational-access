# خطی الجبرا — شاہ مکھی مُڈھلا پیکیج

پڑھنا شروع کرو: [پنجابی ریڈر](reader/opening.html)۔
[A4 PDF](output/pdf/hefferon-shahmukhi-opening.pdf) وچ مشقاں دے جواب کھلے نیں۔
HTML وچ جواب کھول کے ویکھ سکدے او؛ اوہدے نال اصل فارمولیاں دا TeX وی محفوظ اے۔

For offline reading, download `hefferon-shahmukhi-opening-offline.zip` from this
package, extract it, and open `reader/opening.html`. GitHub's file view displays
HTML source rather than the rendered book. The separate PDF opens directly.

ایتھے اردو مدد صرف وکھرے اصطلاحی خانے وچ اے؛ اصل سمجھاؤن والی بولی پنجابی اے۔
ایہہ پوری کتاب دا ترجمہ نہیں۔

## What is included

Jim Hefferon's *Linear Algebra*, fourth edition, second printing, in native
Pakistani Punjabi/Shahmukhi, with separately labeled Urdu and English help.

- 174 recovered source-bound slots: default cover, notation and Greek-letter
  tables, and the **complete preface**. These are slots/cells/paragraphs, not
  174 lessons.
- 97 newly translated contents titles and the optional-subsection legend;
  all 14 optional markers and source hierarchy retained. The outline describes
  the whole source book but does **not** include its chapter translations.
- Four newly authored prerequisite examples and eight exercises, all with
  worked solutions, a two-line diagram, and nine glossary rows. These are
  original learning support, not translated Hefferon exercises.
- Offline semantic HTML, a companion A4 PDF, exact source witnesses, assets,
  modular JSON units, and reproducible builders/checks.

The bounded opening package is complete within that scope. The book, its main
chapter exercises/answer book, laboratory, and wider mathematics programme are
not completed by this release. Next faithful source anchor:
`src/gr/gr1.tex:4`, Chapter One, *Linear Systems*; start with its introductory
prose and then Gauss's Method.

## Format and accessibility

The semantic contents intentionally has **no upstream page numbers**. The
recovered PDF used for the historical study is from 2020 and predates this
2021 source. Transplanting its page numbers would be false. This is a disclosed
formatting adaptation; no current heading or optional marker was dropped.

HTML is primary: semantic headings, language tags, RTL prose, isolated LTR math,
linked answers, raw source-TeX disclosures, descriptive figure alternatives,
keyboard-focus styles, and an offline bundled Nastaliq font. Mobile wide tables
scroll within their own containers. The PDF expands answers but omits the
76 raw-TeX disclosure blocks; these remain available in HTML/source. The PDF is
not certified PDF/UA; exact tested properties and limitations are in QA receipts.

The tested Windows print profile uses embedded Arial/Cambria glyph subsets;
the HTML retains its bundled Nastaliq font. Printing through those Nastaliq and
Naskh fonts exposed faulty Unicode extraction in the tested Chromium build,
so they were not used for the released PDF. Arabic presentation-form characters
can be normalized with Unicode NFKC; mixed RTL/LTR extraction order still varies
by PDF reader. Semantic HTML remains the logical-text authority. Amiri is an
openly licensed print fallback, but a different host/font stack must rerun QA.

The source cover components are preserved and displayed separately. Their layout
does not claim to reproduce the source's precise TeX cover composition.

## Provenance and source/adaptation boundary

- Canonical source commit: `df2262e089a02651c127f1dd12649c4622ee1383`.
- Pinned Indonesian comparison: `e84ce2956a7304830c42eba70106f940fefee7c4`;
  comparison evidence only, not the target language.
- Recovered public intake predecessor:
  [immutable 2026-09-04 intake](https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/tree/ed6f2e2020118723c2a12fe3377d2273c3d8ec50/translations).
- [License and attribution](LICENSE.md): source/adaptation CC BY-SA 2.5;
  unchanged font separately SIL OFL 1.1. All inherited credits remain.
- [Terminology evidence and limits](provenance/terminology.md): the prose canon
  supports grammar, not certification of every specialist mathematical label.
- [Modular units](backend/units.json) distinguish faithful source translation,
  format-adapted contents titles, and original questions/solutions.

Historical source-study/notice files remain byte-exact evidence of the recovered
opening. Their old incomplete-frontmatter labels describe that predecessor, not
this successor. The displayed original scope note is explicitly updated, and the
reader presents compact provisional term pairs while retaining full historical
statuses in JSON;
all 174 recovered source translation strings and all 76 formula payloads remain
unchanged. New titles, legend and learning additions are separate inputs.

## Rebuild and check

Requires Python with `lxml` and `pypdf`. No TeX, upstream scripts or network
requests are needed to rebuild the HTML, diagram and unit backend:

```text
python -B scripts/build_package.py
python -B scripts/validate_package.py
```

The optional PDF/visual runner uses Node.js, Playwright and an installed Chromium
browser. Set `PLAYWRIGHT_MODULE` and `BROWSER_EXECUTABLE` only when those packages
or the browser are outside their usual paths, then run:

```text
node scripts/render_reader.cjs
```

See `qa/build.json`, `qa/validation.json`, `qa/browser.json` and
`qa/pdf-inspection.json` for exact scope, versions, byte/hash bindings and checks.
`qa/replay.json` records two byte-identical builds. PDF metadata dates and
Chromium's process-local tagged-table ID strings are canonicalized at equal
byte width, preserving content streams, xref offsets and sorted IDTree links.
PDF companion-file links point to this public package; HTML keeps relative
offline links. The final PDF is 26 A4 pages, with all eight answers expanded.

Prepared by OpenAI Codex gpt-5.6-sol, Ultra, on instructions of the user.
Not an official edition or endorsement by Jim Hefferon or his institution.
