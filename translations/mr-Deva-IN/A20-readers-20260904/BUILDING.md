# Rebuilding the bounded reading edition

Unzip `marathi-source.zip` into this package directory. It supplies the `source/` closure, the HTML builder and stylesheet. Use Python 3.11 or later and install `beautifulsoup4==4.15.0`; the PDF builder's exact environment pins are in `requirements-pdf.txt` within the source archive.

Run `python -B build_marathi.py`. It verifies every pinned source input, creates both full-module HTML readers and 21 overlapping study readers, checks source/math/ID preservation and restores the exact accepted m81373 PDF. All figures are embedded in HTML: opening a reader does not require network access or a server.

The copied `source/tools/assemble_m81373.py` and `assemble_m81374.py` reproduce exact assemblies from the included raw canonical module witnesses and selected inputs. From `source/tools`, run:

```
python -B -m unittest test_assemble_m81373 test_assemble_m81374 test_m81374_primary_source
```

These are the 58 current source/assembly tests. They do not require the original whole-book archives or a network connection.

For the repaired m81374 PDF, use the included Windows-compatible ReportLab/HarfBuzz builder under `source/tools/build_m81374_pdf.py` with the recorded font environment. Its source, math and ID checks fail closed on drift. Copy the resulting `source/output/pdf/A20-m81374.pdf` to `output/pdf/A20-m81374.pdf` after QA. The builder uses installed Nirmala UI, Cambria and Segoe UI Symbol fonts; it does not distribute the standalone fonts. Different font/runtime bytes can change pagination and require fresh visual QA. No TeX engine is required.

The retained m81373 PDF is unchanged from its accepted recovery artifact. Changing a PDF is not required to reproduce the HTML edition. Do not confuse the inherited source-assembly receipts' historical reader status with the newer reader-specific QA in this package.
