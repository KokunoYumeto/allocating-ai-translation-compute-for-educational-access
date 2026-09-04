# MR-BRIDGE-007 independent integration review

Date: 2026-08-31. This is a bounded source, math, build, and rendered-artifact review, not native-speaker/teacher approval or a claim that the five-book assignment is complete.

## Result

Source/content and build checks passed. **Visual review remains unresolved at 420 px:** the self-check table's rightmost header and empty rating cells are clipped in the section screenshot. The automated browser receipt reports no document-level overflow, but this is not sufficient to clear that visual defect. No source text, student rating, shared stylesheet, or builder was changed during this review.

## Source and content checks

- Personally inspected both pinned EN and ID module selections in memory and both Figure 213 source images. The canonical EN image is retained without pixel edits; the distinct ID image is a review witness, not the exported asset.
- Confirmed nine ordered locators: four writing exercises, one self-check, and four glossary definitions. Their 24 source IDs are retained, plus the uncounted Writing Exercises wrapper `fs-id1167829756260`, for 25 source IDs total. The already-translated relation glossary entry is not selected again.
- The four writing prompts have no supplied source answers. All four answers here are explicitly labeled original sample answers, not source solutions or new practice questions.
- Checked the domain/range finite-set example, repeated-output allowance, nonfunction counterexample, and all steps of `f(−2) = 2(−2) + 3 = −1`. The function example states its real-number domain and distinguishes `f(x)` from multiplication. Six displayed math checks are retained.
- Checked four glossary meanings and the input/output roles of `x` and `y`. Existing Marathi canon usage was actually consulted: Balbharati's supplied formula/notation layout and Vishwakosh's exact-one function condition, प्रांत/सहप्रांत distinction, and प्रतिमांचा संच/कक्षा account informed review of the existing terms फलन, प्रांत, मूल्यसंच, and प्रतिचित्रण. No unrelated canon was recopied and no authority claim was inferred from these references.
- Self-check preserves the exact two source prompts and all three objectives and three rating choices. The translated four-by-four table contains nine empty `□` cells; no selected state, saved learner choice, answer, or readiness rating has been filled in. The caption distinguishes the original English pixels from the Marathi table and correctly treats the dash in the last heading as punctuation, not subtraction.

## Freeze, build, and durable tests

Commands completed:

```text
python -B mr-Deva-IN/tools/freeze_unit.py MR-BRIDGE-007
python -B mr-Deva-IN/tools/build_unit.py MR-BRIDGE-007
python -B mr-Deva-IN/tools/test_unit7_math.py
```

Freeze: nine selections, 28 witnesses, 7,526 selected-fragment bytes, one exported asset of 53,026 bytes; both source images total 314,025 review bytes. Build: PASS, 33 unique IDs, 12 local links, four source question/answer pairs, six math checks, nine required terms, and one embedded JPEG. Independent stdlib regression: **16/16 tests pass** against the frozen fragments and actual pinned source members; the tests make no language-quality or browser claim.

Hashes at handoff:

| Artifact | SHA-256 |
| --- | --- |
| Translation XML | `44593e8d688ad459ed2e72b1eac1293974cd3203661ff5df3b220d0815419e06` |
| Unit config | `5a5a0ccb6ca714f564bedc37be49d256caea57cccd5f93b2febbf7150763a458` |
| Unit lock | `9e7e2d005e8e3ddfd215c12eb9d968179617f534e65886fb9344d50a970f2c3a` |
| HTML, 92,977 bytes | `f79ab53c6a5d0b809183e2ddc0473d717654edc1e6759dbba182505ab8459a6a` |
| Canonical EN Figure 213, 53,026 bytes | `4571cd8939329c873f1251bb96128b1dbeec19fcb18fd8de736432b9f00304c3` |
| ID review Figure 213, 260,999 bytes | `4960c2832d316917c88d326b3910e5255cde79905944697434cbc47e1e46c213` |
| Build receipt | `3dbdc8618a264ffb80fc0b3b9d1e47cb874ee2d6d10de20aa345a53c39a3c289` |
| Browser receipt | `edcd9dc9825b2759fdc8b14ed93b8d6d625a47600903d013e375bdadc6e7bebb` |
| Regression test file | `1cbbf37859905c8275e6c414d9c47ced346cc58cfdd2115642fe35958b1e2c97` |

The master source-lock witness is the stable LF file, SHA-256 `f11201945c6b66feb12be0bc1117eb5b70d97bcd0a57d20f32bb7e362d8e7c71`.

## Actual screenshot inspection

The existing isolated `render_reader.cjs` ran in Edge 152.0.4191.53 at 1100×900 and 420×900. The receipt confirms image decoding at natural size 646×139, no page errors or network requests, and bidirectional navigation of all four source-answer pairs. The receipt's PASS is an automated runtime result only.

Personally viewed all ten files under `downloads/mr-Deva-IN/reader-qa/MR-BRIDGE-007/`, not merely their receipt:

- `1100-header.png`, `420-header.png`
- `1100-fs-id1167829756260.png`, `420-fs-id1167829756260.png`
- `1100-fs-id1167829783756.png`, `420-fs-id1167829783756.png`
- `1100-glossary.png`, `420-glossary.png`
- `1100-credits.png`, `420-credits.png`

Headers, four prompt/answer blocks, source labels, glossary, credits, Devanagari shaping, and formula text were readable in the inspected images. The original English image is small at 420 px, as expected, and is followed by complete Marathi text. At 1100 px the translated checklist fits. At 420 px its last rating column is visibly cut at the section boundary, including parts of its empty squares. Shared CSS has no explicit table-scroll wrapper; therefore no working scrolling behavior is claimed. Original screenshots are preserved unchanged.

## Follow-up browser policy limit

After the above isolated render and screenshot inspection, a read-only in-app navigation was attempted to inspect table geometry. Tool: `mcp__node_repl__js`. Exact action:

```javascript
const tab007 = await browser.tabs.new(); await tab007.goto('file:///[local-home]/.codex/worktrees/9286/LAN%20ALLOC/mr-Deva-IN/output/MR-BRIDGE-007.html'); nodeRepl.write(await tab007.playwright.domSnapshot());
```

Exact tool denial:

> Browser Use rejected this action due to browser security policy. Reason: The browser URL policy blocks this action. Browser use cannot visit the requested page because its URL is blocked by the Browser use URL policy. The agent must not attempt to achieve the same outcome via workaround, indirect execution, raw CDP or browser commands, alternate browser surfaces, or policy circumvention. Proceed only with a materially safer alternative that does not require this blocked browser action; if none exists, stop and request user input.

No retry, alternate browser surface, indirect navigation, or geometry workaround followed this denial. No revised render is claimed. The root integrator was notified of the unresolved visual defect and the exact policy limit; shared styling is outside this reviewer's file ownership.
