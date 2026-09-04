# U003 source translation and review notes

Scope: the complete next contiguous instructional subsection `m81243#fs-id1883656`, Identify the Place Value of a Digit. AI-drafted Tamil on 2026-08-30; no native-speaker, teacher or educational-efficacy approval is claimed. Only this translation and this subtask's notes are authored here. Shared terminology, builders, logs, images and commits remain outside this subtask.

## Actual source inventory and boundary

Read the complete English and Indonesian subsection from `provenance/m81243.en.cnxml` and `provenance/m81243.id-ID.cnxml`. A read-only XML inventory of each witness reports the same boundary and structural counts:

- 216 elements, including the subsection root; 31 elements with source IDs; 40 MathML expressions.
- Three source exercises: worked `fs-id1256900`, then practice `fs-id1573052` and `fs-id1518735`. Each has five labelled subparts and five answers.
- Two media nodes: `fs-id1339846` uses `CNX_BMath_Figure_01_01_011.jpg`; `fs-id2297687` uses `CNX_BMath_Figure_01_01_012_img.jpg` in the English source. The Indonesian references use `.jpg.id-ID.svg` equivalents.
- The subsection ends after `fs-id1282619`, containing exercise `fs-id1518735` and solution `fs-id2619544` with answer list `fs-id1807276`.
- The following sibling is exactly `m81243#fs-id1321580`, **Use Place Value to Name Whole Numbers**. U003 does not include or claim translation of that following node.

Preserve the original 5,278,194, 63,407,218, 27,493,615 and 519,711,641,328, their comma grouping, all place contributions, source punctuation in MathML, and circled subpart tokens. Language-bearing `base-10` is translated consistently as `அடிமானம்-10`, retaining the token 10 and hyphen. No currency occurs in this subsection; the reference back to money does not authorize a conversion.

## Canon use and language decisions

Before drafting, read actual already-OCRed Tamil canon pages 20 (C05/C06), 175 (glossary) and 8 (large-number introduction); also inspected existing page 16 OCR to check whether it supplied relevant additional register. It mainly describes a linked interactive activity and is not used as an offline dependency. No source material was newly acquired.

- C05/C06 attest இடமதிப்பு, இலக்கம்/இலக்கங்கள் and தீர்வு. Page 175 attests இடமதிப்பு அட்டவணை. These remain consistent with the existing ledger and previous units.
- Page 8 and the glossary show the familiar Indian large-number names இலட்சம் and கோடி; the page-20 table uses Indian grouping. The OpenStax source here instead explicitly teaches three-place periods. Do not silently replace its millions/billions/trillions with Indian periods or regroup its numerals.
- Provisional, compositional translation: **இடமதிப்புத் தொகுதி** for a three-place period, with **தொகுதிகள்** in `term-00009`. Avoid a literal time-related meaning of English “period.” The selected canon does not attest this exact specialist compound.
- Preserve source scale names as Tamil transliterations **மில்லியன்**, **பில்லியன்**, **டிரில்லியன்**, inflected as மில்லியன்கள்/பில்லியன்கள்/டிரில்லியன்கள் for place/group labels. They mean the source's short-scale 1,000,000 / 1,000,000,000 / 1,000,000,000,000 respectively. These spellings and source scale compounds remain provisional; the initial canon is not claimed to approve them.
- Use **பத்தாயிரங்கள்** for the ten-thousands place and **நூறாயிரங்கள்** for the hundred-thousands place, retaining the source international structure. Use **பத்து மில்லியன்கள்**, **நூறு மில்லியன்கள்**, and analogous billion/trillion compounds. A new companion should explicitly bridge these values to familiar Indian names without changing the source strand.
- Source prompts use “place value” but the solutions name positions, such as “tens,” rather than digit contributions such as 10. Tamil prompts therefore ask for the **இலக்கங்கள் இருக்கும் இடங்கள்**; the title retains இடமதிப்பு. This makes the requested answer match the actual source solutions and keeps digit/place/contribution distinctions from U002 intact.

## Source figures and description discrepancies

Visually inspected the actual canonical JPEGs `_011` and `_012_img`; also read the Indonesian SVG title, description and geometry/text markup. All fifteen place labels, leading blank positions and example digit rows agree mathematically.

- `_011` has a top Place Value title band, then period headings, place labels and the digit row. The first eight digit positions are blank; the next seven are 5/2/7/8/1/9/4. The broad English “four rows” count includes the title band. The Tamil alternative states the actual fifteen place columns and five period groups without confusing title/header rows with data rows.
- The canonical `_012_img` has period headings, vertical place labels and the digit row: three visible bands and no separate visible Place Values title. Its English alternative says two rows and a title. The Indonesian source alternative repeats two rows, while its actual SVG redraw adds a visible title and thus has four bands. Do not assert either incorrect row count in Tamil. Describe the fifteen-place structure and digit positions instead.
- In `_012_img`, seven leading digit positions are blank; the next eight are 6/3/4/0/7/2/1/8. The interior 0 is data, not an omitted/blank place.
- Tamil media paths follow the prior-unit convention: `../assets/u003/CNX_BMath_Figure_01_01_011.svg` and `../assets/u003/CNX_BMath_Figure_01_01_012_img.svg`. These are planned Tamil equivalents, not files created by this translation subtask. Their actual presence, matching semantics, rendering and offline inclusion must be checked before admitting U003 as a finished reader unit. Alternatives may require declared visual-adaptation revision once the final Tamil diagrams exist.

## Review status

After drafting, read the actual extracted Tamil prose in source order. During revision/QA, reconsulted the relevant page-20 OCR lines on digit counts, the place-value table and “ஒன்றுகள் இடத்தில் அமைந்த இலக்கங்கள்,” and the page-175 glossary entries for இடமதிப்பு அட்டவணை, இலட்சம் and கோடி. These support the established register and the distinction between an இலக்கம் and the இடம் it occupies; they do not establish the provisional international scale labels. No OCR-derived arithmetic was imported.

Read-only checks passed against both complete witnesses:

- Exact recursive tree shape and stable attribute comparison: 216 nodes, 31 unique ordered IDs, 40 MathML expressions. Only root language, image source/MIME and translated alternatives are declared attribute differences. MathML `mn`/`mo` values, all other mathematical text/attributes and circled subpart symbols remain unchanged; translated `mtext` retains numeric/punctuation tokens.
- Every local source cross-reference resolves inside the subsection.
- All 15 labelled subpart answers were independently checked by locating each requested digit in its actual source number, counting powers of ten from the right, and comparing the resulting place label with the Tamil solution. All requested digits are unambiguous in their question numbers.
- All seven contributions in 5,278,194 were independently calculated as digit × its place unit: 5,000,000; 200,000; 70,000; 8,000; 100; 90; 4. Their sum equals 5,278,194. No mathematical answer discrepancy was found.
- Current translation SHA-256: `d0851335f8a28f4785bbe8fae21b3e83f3df72f0b5bfc9f84baa9d160f27c5f7`.

The figure worker was sent all fifteen agreed Tamil place labels, five period headings, expected digit rows/leading blanks, and the two planned asset paths. Final chart appearance and asset closure remain separate parent/figure-worker checks. This status does not claim that U003 has been built, rendered, independently language-reviewed or released. No standalone recovery companion for U003 is included in this source-only subtask. The full A00/A10/A20 assignment remains incomplete.

Available C: space was checked before work (6,657,019,904 bytes) and during final source QA (6,685,618,176 bytes). No download, extraction, copy, deletion, PDF build or commit was performed by this subtask.

Next contiguous translation marker remains **`m81243#fs-id1321580` — Use Place Value to Name Whole Numbers**.
