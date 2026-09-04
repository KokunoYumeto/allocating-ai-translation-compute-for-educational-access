# Tamil PDF font and text-extraction investigation

Date: 2026-08-30
Scope: internal U001/U002 PDF-export investigation; this is not native-speaker, assistive-technology-user, or PDF/UA approval.

## Outcome

Do **not** replace the reader's variable Tamil font with static instances as a fix for the reported pypdf NUL characters. The controlled static-font probe changed Chromium's embedded font type, but it did not change pypdf's nine NUL characters or restore the affected Tamil words. Both probe PDFs contain correct logical Tamil in `/ActualText`; Poppler extracts it correctly from both.

For these Chromium exports, Poppler `pdftotext` 25.07.0 is the verified logical-text/search QA oracle. pypdf 6.14.2 remains suitable for page count, metadata, catalog language, marked/tagged status, and structure-tree inspection, but its `extract_text()` result is not a valid Tamil search/copy oracle for these files. This distinction does not establish PDF/UA or screen-reader conformance; assistive-technology-user testing remains pending.

## Tools and inputs

- Microsoft Edge 152.0.4191.53, invoked headlessly with tagged-PDF export.
- Python 3.12.10, fontTools 4.63.0, pypdf 6.14.2.
- Poppler `pdftotext` 25.07.0.
- FontTools' official instancer documentation states that pinning every variation axis produces a full static instance: <https://fonttools.readthedocs.io/en/latest/varLib/instancer.html>.
- Original variable font, unchanged: `ta-Taml-IN/assets/fonts/NotoSansTamil.ttf`, SHA-256 `aa3a9b321f4b0bb2c40203ffbde9af89713227866e0e13f76e5b9eeea727cf88`.
- Probe helper: `ta-Taml-IN/scripts/prepare_print_fonts.py`, SHA-256 `75e1531ca7fc2b0a589e69b0497b230b4a9ab5bc21927ef7cf3c4c7fde18f483`.

The helper reads the production font and writes only beneath ignored `tmp/pdfs`. It pins `wght` and `wdth=100`, verifies that variation tables are absent, verifies each `OS/2.usWeightClass`, checks more than 100 MiB free space, and verifies that the source font hash did not change. `updateFontNames=False` is intentional: this source font's `STAT` table does not provide an AxisValue at the authored weight 650; CSS face descriptors and `OS/2.usWeightClass` distinguish the scratch faces.

## Controlled static-instance probe

Command:

```powershell
python ta-Taml-IN/scripts/prepare_print_fonts.py --write-probes --render-probes
```

The four full static instances were reproducible in a second output directory:

| Weight | Bytes | SHA-256 |
|---:|---:|---|
| 400 | 82,612 | `fec0c632226e56947bec61a5ab59e330344877655830e1989755be1b6a446f57` |
| 600 | 82,708 | `4efdf206db2462374b05fb09f2c31c4d201c5b60784498cab40892ffe390bbe3` |
| 650 | 82,696 | `30d67d43079b002b7800ff31f1626ccaf41f6b9e750554e0385a42f5dfe02798` |
| 700 | 82,668 | `b0759f78d5ec7745a4f6d52216611d93bf1a56cf2949d0afba1d4f597b0de6d0` |

The fixture exercises Tamil at weights 400, 600, 650, and 700 plus a Tamil MathML label.

| Probe | HTML SHA-256 | PDF bytes | PDF SHA-256 | Embedded Tamil font | pypdf NUL | Poppler NUL / U+FFFD |
|---|---|---:|---|---|---:|---:|
| Variable | `8e013168d46d58302b8e8c117d1a470bf545b33cd643a08af43fa11eeeda8a92` | 172,045 | `005bdd8446c1858f5fc865a9e20f68194157d1bab6ee2550a3c44d9228e99ff5` | Type 3 | 9 | 0 / 0 |
| Static | `92ce25478e98a31b1cb1ca535451fcdc3d5af6672badab0d7c73bd1a386fe5d1` | 41,871 | `844a25846ec9b41b1f31584d24902c58a5d4b6ace9951d57b319feedabb01817` | Type 0 | 9 | 0 / 0 |

Poppler found `இடமதிப்பு` five times and each of `முழு எண்கள்`, `பூச்சியம்`, and `உரைச் சோதனை` four times in both probes. pypdf found `முழு எண்கள்` four times but found zero exact occurrences of the other three and emitted nine NUL characters in both. Visual Poppler renders of both one-page probes were clean.

Both probes contain 47 `BDC` operations, 19 `MCID` properties, and 28 parsed `/ActualText` strings. Those strings decode without NUL or U+FFFD and include logical Tamil fragments such as `மி`, `சோ`, `னை`, `தி`, `சி`, and `ரை`; none begins with a dependent Tamil vowel sign. The static PDF still maps contextual Tamil vowel glyph codes to `0000` in ToUnicode. This explains why a static font alone is not a repair: Chromium supplies the logical syllables through `/ActualText`, while pypdf's extraction result does not incorporate them correctly. Do not patch the CMaps blindly.

## Production-PDF evidence

Inputs and exact inspected outputs:

| Unit/profile | HTML SHA-256 | PDF bytes/pages | PDF SHA-256 |
|---|---|---:|---|
| U001 print | `26663c054138cbece00f7a17b24e07bb9369aab8ca3ee1c6a214cfe6f5981f01` | 692,431 / 20 | `c99922ff245c20fa1fdb7c13c9ddd599ad99ba172f09b7e5baec582367e3e35b` |
| U001 screen | `c0981a7eacbedaae401eca00d04bbdaa1c02d79ff740e3e5fb23737638295077` | 690,634 / 20 | `52949bdd151d2d5ae929c427efdde690483705e57504f49f844f5b70056fd557` |
| U002 print | `5231f5c9b793e0aabce9c69636d77d7ad83045cf2ffecc5e8496c989f602e9f5` | 875,838 / 23 | `ffa4d63da02df5ff5b179c5787c43bf099f03fa7024131b03586034124355a9b` |
| U002 screen | `663465f67e4946a3c80de5cb351acb34caf88b8d3738d2807350a9f05c1ea5b5` | 881,632 / 31 | `50b6455c6b444223bdae5919ee44ffcf4b2c49ee83a70cfef79c7b49f370dd1c` |

All four catalogs declare `/Lang (ta-Taml-IN)`, `/MarkInfo /Marked true`, and a structure tree. U001 has 866 structure `/S` entries and three Tamil `/Alt` descriptions; U002 has 1,141 `/S` entries and nine Tamil `/Alt` descriptions.

Marked-content totals are:

| Unit/profile | BDC | MCID | `/ActualText` | EMC |
|---|---:|---:|---:|---:|
| U001 print | 2,021 | 482 | 1,539 | 2,021 |
| U001 screen | 2,021 | 482 | 1,539 | 2,021 |
| U002 print | 2,649 | 586 | 2,063 | 2,649 |
| U002 screen | 2,650 | 587 | 2,063 | 2,650 |

Every parsed `/ActualText` value in all four PDFs was free of NUL and U+FFFD, and none began with a dependent Tamil vowel sign. Representative logical fragments include `றி`, `தி`, `மி`, `ளை`, `மா`, `ரி`, `ளா`, `கா`, `மொ`, `ழி`, and `பெ`.

A pypdf pitfall matters when checking these counts: `ContentStream` is falsy because it is an empty dictionary even when it has stream data and parsed operations. The check must use `if stream is not None`, not `if stream`; otherwise every marked-content count is incorrectly reported as zero.

### Poppler logical-text verification

`pdftotext -enc UTF-8 PDF -` produced zero NUL and zero U+FFFD characters in every production PDF. No extracted Tamil token began with a dependent vowel sign. Required strings were present in both profiles:

- U001: `இயல்` 42, `முழு` 49, `பூச்சியம்` 3, `உரை` 2, `சோதனை` 17, and `376` 5.
- U002: `இடமதிப்பு` 13, `முழு` 9, `பூச்சியம்` 5, `உரை` 2, `சோதனை` 20, `176` 3, `237` 4, and `$374` 4.

The HTML/PDF sequence comparison uses authored body text after excluding the skip link, SVG `title`/`desc` alternatives, and print-hidden `diagram-hint`/`table-hint` elements while retaining visible SVG text. Tamil-token results:

- U001: HTML 1,652; each PDF 1,652; no missing or extra token counts; the full HTML sequence is a subsequence of both print and screen extraction.
- U002: HTML 2,303; each PDF 2,309; no missing authored token; the six extras are repeated table-header tokens across pagination: `இடமதிப்பு` ×1, `இலக்கம்` ×1, `மதிப்பு` ×2, `எண்` ×1, `மொத்த` ×1. The full HTML sequence is a subsequence of print extraction. Screen extraction contains every authored token but differs in physical order at the paginated table: the first greedy mismatch is HTML token 1,220, `கூட்டுத்தொகை`, after Poppler emits the repeated header before the remaining row content. This is a pagination/read-order limitation, not missing Tamil text.

For comparison, pypdf emitted 392 NUL characters in each U001 profile and 708 in each U002 profile. It found ordinary unaffected strings and numerals, but zero exact occurrences of affected words such as `பூச்சியம்`, `உரை`, `சோதனை`, and U002 `இடமதிப்பு`. The controlled probes and the decoded `/ActualText` evidence show that those pypdf NUL counts are an extractor limitation, not evidence that the production PDFs lack logical Tamil.

## QA disposition

Use Poppler UTF-8 extraction for production Tamil logical-text/search checks, requiring:

1. zero NUL and zero U+FFFD;
2. unit-specific required Tamil strings and numeric/currency strings;
3. no Tamil token beginning with a dependent vowel sign;
4. comparison with the print-intended HTML token multiset, explicitly accounting for repeated table headers and CSS-hidden/alternative content.

Continue using pypdf for metadata, page counts, catalog language, tagging/structure inspection, and other non-Tamil-extraction checks. Preserve the existing variable font and HTML/EPUB font path. Static instances remain an ignored internal probe only. Native-speaker review, real keyboard/assistive-technology checks, and PDF/UA conformance testing are still not done.
