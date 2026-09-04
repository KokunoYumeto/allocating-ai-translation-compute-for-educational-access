# Gujarati canon and difficult-language review — m82463

Scope: OpenStax *Elementary Algebra 2e*, col31130, canonical commit
`38cae454e644abf9f0a623e876994553881597c9`, module `m82463` only. This is a
review of the recovered Gujarati draft and this packet's authored support; it
does not certify the whole locale, the whole book, or native-speaker review.

## Evidence actually checked

- Read the packet's complete `canon/README.md`, all 13 rows in
  `canon/examples.csv`, `canon/targeted-examples.md`, and the relevant entries
  in `terminology.csv` before the final build.
- Compared every source/target element in `source/en.cnxml` and
  `source/m82463.gu.cnxml` in source order. The 13 school-material examples
  support concise Gujarati commands and learner-facing register, but contain no
  equation-property label; they are explicitly recorded as **not found** for
  those compounds.
- Used the locally preserved targeted-review record for the Khan Gujarati
  variables/expressions/equations and polynomial material. This was a reread of
  the recorded linguistic evidence, not a fresh claim that the remote pages
  were opened in this finishing pass.
- Compared the canonical English problem, its Gujarati wording, the exact
  MathML, and the authored worked answer for every one of the 38 source-omitted
  exercises. Arithmetic proof is separately recorded in `qa/MATH.json`.
- Inspected all 68 source-media identities and the 15 language-bearing semantic
  adaptations. The full-size `011a` image was opened separately to resolve its
  visible extra `z` after `−8`.

The recovered translation predates this finishing review. Reasons backfilled
for earlier wording are therefore labelled `retrospective_reconstruction` in
`EXPERT_REVIEW_LOG.json`; no contemporaneous intent is invented.

## Decisions retained at final review

1. Keep `ચલ`, `પદાવલી`, and `સમીકરણ` distinct. A bare expression is not called
   an equation, and source letter variables remain Latin letters.
2. Use `ઉકેલ` for a value that makes an equation true. Use the concrete bridge
   `ચલની જગ્યાએ મૂકો` beside the technical verb `અવેજી કરો` where substitution
   is first performed.
3. Render simplify as `સાદું રૂપ આપો` and isolate the variable as
   `ચલને એકલું રાખો`. These commands are readable without importing an
   unexplained technical loanword.
4. Retain the compositional labels `સમાનતાનો બાદબાકીનો ગુણધર્મ` and
   `સમાનતાનો સરવાળાનો ગુણધર્મ`, while marking them provisional because the
   checked Gujarati school examples do not attest the complete compounds.
5. Keep the operation explicit on both sides. The new support avoids teaching
   the shortcut “move it across and change the sign,” because that shortcut
   hides the equality-preserving action.
6. Use `સજાતીય પદો` for like terms and `સરવાળાનો ક્રમવિનિમયનો ગુણધર્મ` for
   additive reordering. Use `વિતરણ કરો` only when the outside factor is applied
   to every term in parentheses.
7. In phrase translation, `કરતાં વધુ` and `નો તફાવત` preserve operand order.
   The worked mappings are checked against `x + 11 = 54` and
   `12t − 11t = −14`, not inferred from word overlap alone.
8. For the car application, use `સૂચિત કિંમત` for sticker/listed price. The
   variable definition is reordered to natural Gujarati around the unchanged
   MathML `s =` token.
9. For the recycling application, the requested quantity is the **first**
   month's newspaper weight. Four inherited/source image descriptions that
   said second month were repaired in the semantic Gujarati layer; the
   equation `w + 28 = 57` and result 29 pounds are unchanged.
10. Preserve all original bitmaps. The 15 language-bearing figures receive
    separate semantic Gujarati tables/phrases with the original available in a
    disclosure. Language-free mathematical/model figures remain original.
11. Preserve the visible source typo in `011a` as evidence. Its companion says
    explicitly that the `z` after `−8` is extraneous and gives the valid chain
    `5(12 − 4) − 4(12) = 40 − 48 = −8`.
12. Keep source-supplied solutions and the 38 newly authored answers visibly
    distinct. “Source order” identifies XML order and is not presented as a
    printed exercise number.

## Acceptance reread and uncertainty

The final Gujarati HTML was reread against the choices above before browser QA.
No English prose remains in target CNXML text or accessibility descriptions;
Latin letters are mathematical variables, identifiers, names, or source
attribution. No mathematical token, source ID, source exercise, supplied
solution, or original media identity changed.

No Gujarati mathematics teacher, native-language editor, learner, or assistive
technology user was consulted for this bounded packet. That missing evidence is
not a hold. Compound property labels, the technical/plain substitution pair,
and the preferred newspaper register remain explicit questions for later expert
correction; the current deterministic release is reversible and fully logged.

