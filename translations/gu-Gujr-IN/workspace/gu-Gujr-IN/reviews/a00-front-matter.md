# A00 complete front-matter translations

Date: 2026-08-30. This review covers complete source modules m81241 (Preface) and m81242 (Introduction). It continues the Gujarati assignment; it does not mark A00/A10 or the full accessibility workflow complete.

## Sources and delivered coverage

The English canonical witnesses in `downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/` were read in full. The corresponding Indonesian module prose was read as a secondary witness. Original source facts, numbers, identifiers, credits and media paths remain authoritative.

| Module | Canonical SHA-256 | Elements / IDs preserved | Gujarati slots | Media |
| --- | --- | --- | --- | --- |
| m81241 | `1c7cf6eda8be5021f1f33dc22069f5a3db50d1412a024bb57c7268b25db7f9df` | 256 / 85 | 117 | 4 |
| m81242 | `0d76349dc9a5ac95ce000e86c140ddadc0bebd5b30edeb4e2b1163b02c26fa83` | 13 / 3 | 5 | 1 |

Outputs are `translations/a00-m81241.gu.cnxml` and `translations/a00-m81242.gu.cnxml`. They are complete documents with translated titles and metadata, not excerpt wrappers. Neither source module contains exercises or MathML expressions. The only newly added document attribute is `xml:lang="gu-Gujr-IN"`.

## Actual canon use and decisions

Before drafting, read the existing OCR of Std 6 Week 1 PDF p12 (printed p30, teacher guidance before Q1) and visually inspected its page image. This is GU-C07. It distinguishes earlier learning, પુનરાવર્તન, સંકલ્પના, સંખ્યાજ્ઞાન and ચાર ગાણિતિક ક્રિયાઓ, then offers guidance where pupils need it. The translation uses that register in the Introduction and the Preface's description of guided practice and prerequisite review. It does not copy worksheet questions or infer that the college textbook was originally written for Gujarati primary grades.

During drafting, kept the already consulted GU-C01–04/GU-C08–10 distinction between સંખ્યા, અંક and સ્થાનકિંમત. Continued the established પૂર્ણ સંખ્યા versus પૂર્ણાંક distinction in the chapter overview. Teacher-facing paragraphs use શિક્ષક/વિદ્યાર્થી and the book's ordinary explanatory voice rather than promotional paraphrase.

Before acceptance of the text fragments, reread the actual assembled Gujarati paragraphs and the Std 6 p12 OCR. Reviewed the original p12 page-image observations alongside that pass. Corrected the worked-example explanation from an awkward construction to “વિદ્યાર્થીઓએ નિપુણતા મેળવવાની હોય તેવી પ્રશ્ન ઉકેલવાની રીતો…”. No rendered reader/PDF review is claimed here; the combined publication build is owned by root.

New overview terminology is provisional pending the corresponding subject-specific units and educator review: પૂર્વબીજગણિત, ચલ, પદાવલી, સમીકરણ, ગુણાંક, અપૂર્ણાંક, દશાંશ, ટકા, વાસ્તવિક સંખ્યા, બહુપદી, આલેખ, સમતા માટેનો ભાગાકારનો/ગુણાકારનો ગુણધર્મ. The source's later-topic overview was fully translated instead of omitted because the current starting canon mainly concerns numeracy.

Feature labels are consistent with the completed exercise section: “અભ્યાસથી નિપુણતા”, “વિભાગનો અભ્યાસ”, “રોજિંદા જીવનમાં ગણિત”, “લેખન અભ્યાસ”. Additional proposed shared labels are “તૈયાર રહો!”, “કેવી રીતે કરવું”, “જાતે અજમાવો”, “જવાબસૂચિ”. Root was informed for cross-module integration.

## Names, credits and source notices

All 53 reviewer name/affiliation lines and the three author affiliation lines are retained exactly, including source punctuation and structure. Surrounding author prose and the reviewer/author headings are translated. Person, institution, publication, resource-program and publisher names remain identifiable: for example OpenStax, Rice University, Prealgebra 2e, the book *Strategies for Success: Study Skills for the College Math Student*, and Links to Literacy. URLs remain unchanged.

The source's Creative Commons license description is translated, with its formal license name/version/acronym retained. The quoted fallback attribution statement is retained verbatim: `Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.` This is source-text preservation, not a new license audit or a change to the user's workflow. The original nonprofit designation `501(c)(3)` is unchanged.

The Introduction caption retains `Dr. Karl-Heinz Hochhaus, Wikimedia Commons` exactly and retains pounds as the source unit. College-specific resources, verified instructor-account requirements and historic edition-change claims were not silently rewritten as promises about this Gujarati reader.

## Figure inspection and integration

All five source images were visually inspected from the already-extracted canonical archive. Their source-relative paths and Gujarati alt descriptions are retained:

- `../../media/CNX_BMath_Figure_02_03_002.jpg`: selected groups of three dots removed; envelope and five dots remain. No instructional text requires translation.
- `../../media/howtoicon.png`: person and speech bubble with three dots. Gujarati alt describes the visible dots instead of multiplying the source's loose “ellipses” wording.
- `../../media/tryit.png`: right-facing chevron icon.
- `../../media/media.png`: play-triangle icon.
- `../../media/CNX_BMath_Figure_01_00_001.jpg`: fruit-market photograph, with translated caption and preserved credit.

Root needs to include these media at build-time destinations or resolve the original references. No redraw, image generation, new download or source-copy operation was needed for this subtask.

## Verification and remaining work

`scripts/prepare_a00_front_matter.py` passes both pinned source hashes, exact source-slot coverage, child/element/identifier preservation, numeric-token preservation, unchanged author/reviewer XML and exact quoted attribution retention. The final scan of remaining Latin segments found only the named publications, people, institutions, license text/designation, resource title, URL and PDF abbreviation recorded above.

Final output SHA-256 values:

- m81241: `a9b331ad043942dc8b8002b7e301bc78401fbd0db1a98ffd9c1e399ef804d145`
- m81242: `d0e0513715a67271ff9bd791fcc8bcfaec8540e8ba3a481199ddfe81133e6aa6`

Native educator terminology review and integrated browser/print/accessibility review remain pending. The source Preface describes OpenStax's own formats, visual conventions, links and support resources; build-time notes must distinguish those descriptions from the functions actually provided in this Gujarati package. These source modules are text-complete, with no omitted instructional paragraphs.

Checked C: before writing: 6,636,023,808 bytes free. Wrote only small new translation/script/review files. No shared maps, renderers, status files or terminology files were edited; no commit was made.
