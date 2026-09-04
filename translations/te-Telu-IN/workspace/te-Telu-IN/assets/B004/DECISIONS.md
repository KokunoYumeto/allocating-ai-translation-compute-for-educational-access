# B004 naming diagram decisions

2026-08-30. No new downloads or bulk extraction. Diskfree before work was
11,290,406,912 bytes. This subtask writes only this asset directory and its
generator. The main task owns final reader QA and the translator owns prose.

- BA004-01: Read the complete frozen `m81243#fs-id1321580` subsection and metadata.
  Source SHA-256 is `b4f0a1d73243b8f923cb2ee15842b21235c24608c732b00929435ce8c9e55545`.
  The selected original JPEGs are013_img,014_img,015_img only. Each run hashes the
  existing pinned ZIP; selected members are CRC-checked and matched to their
  immutable Git blobs with lazy fetching disabled. Originals remain byte-exact.
- BA004-02: Viewed all three originals before drawing.013 contains37,519,248,
  three period labels, a red "periods" annotation and three digit-to-name arrows.
  014 contains8,165,432,098,710, five period labels and five arrows.015 contains
  only327,577,529 with three period labels; it has no number-name answer lines.
- BA004-03: Keep source international grouping and the literal098 group. Its
  coefficient is98, so its name is ninety-eight thousand, not zero-ninety-eight
  or nine hundred eight thousand. Preserve number commas independently from
  source phrase punctuation. Source014's first four name chunks end in commas;
  013's separate image name lines do not. Capitalization follows the viewed JPEGs.
- BA004-04: Re-read existing TS6 pages16/18 OCR and inspected both complete page
  images in this pass. C18 supplies coefficient-plus-scale Telugu syntax; C20
  confirms that Indian grouping differs and must remain a separate comparison.
  The B004 translator independently reread pages13/16/17 and supplied exact
  standalone gloss chunks. These are editorial Telugu glosses, not claims that
  the canon attests million/billion/trillion loanwords.
- BA004-05: Keep the English number-name chunks in each named source diagram,
  then show separately labeled Telugu glosses. Do not convert English final-s
  removal or omitted-and guidance into a Telugu suffix/conjunction rule.
  Standalone Telugu chunks use nominal scale endings; full running translation
  can use connective forms such as మిలియన్ల and వేల between adjacent chunks.
- BA004-06: Replace the originals' staircase arrows with vertical one-to-one
  group-to-name arrows, retaining3 and5 exact mappings. Bilingual headings,
  card outlines and explicit gloss captions are new accessible redraw choices.
  No extra naming lines are added to015. The original red "periods" annotation
  is represented by the bilingual group heading, not silently discarded meaning.
- BA004-07: Original014's CNXML alt misspells "bilions", but the viewed JPEG
  correctly reads "billions". The new labels use the correct source-visible
  spelling. This is an accessibility correction, not a change of scale.
- BA004-08: Native sizes:013 is1280x660,014 is2080x660,015 is1280x300. Each manifest
  record has `recommended_min_width_px`. Use an individually focusable panning
  wrapper; do not shrink the entire diagram to a narrow phone viewport. HTML img
  alt must still convey the mapping; external SVG title/description does not
  replace it. Main-task final reader inspection remains required.
- BA004-09: `--verify` is read-only and checks original/ZIP hashes, CRC, Gitblob,
  deterministic SVG bytes, visible labels and mapping geometry. An independent
  English-number parser confirms each visible name chunk's value and scale.
  `--self-test` checks17 in-memory corruptions, including a lost098 leading zero,
  wrong power, wrong period label, missing comma, wrong arrow/name and an added
  naming answer in the period-only figure. No test fixture files are written.
- BA004-10: Preserve the B002-compatible manifest field schema, with unit B004,
  its own source hash, paths and generator. Existing OpenStax attribution and
  notices remain applicable; the Telugu SVG redraw is explicitly disclosed.
