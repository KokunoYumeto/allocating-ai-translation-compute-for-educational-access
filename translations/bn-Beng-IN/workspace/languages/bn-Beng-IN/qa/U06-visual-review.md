# U06 visual review

Status: COMPLETE for the stated model/browser scope; independent West Bengal teacher/language, learner and assistive-technology review remains pending.

## Bytes and browser isolation

- Reader: `reader/U06-companion.html`
- Reader SHA-256: `90e64e0b46b24a940a921cad0759e7c030e1dcf3812c5105bcf184423a7d556d`
- Browser receipt: `qa/browser/U06-companion.json`
- Browser receipt SHA-256: `a5c7879b78c1e3ddfa5fbc65206892eafa891c09b9cbc43900da5ac3abc67d57`
- Runtime: bundled Playwright with isolated headless Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe`; all non-`file:`/`data:` requests were blocked and no user profile or session was used.

## Visual scope actually read

I read all six overlapping 1200 px desktop tiles from top through footer and both required 390 px endpoint captures (top and bottom). The narrow review is an endpoint/wrapping check, not a claim that every intermediate narrow-height viewport was separately read.

| Width | Rendered height | Captures read | Result |
| --- | ---: | ---: | --- |
| 1200 px | 5061 px | 6 overlapping tiles | Complete top-to-bottom read; headings, questions, worked examples, answer key, source boundary and footer were legible and unclipped. |
| 390 px | 8122 px | 2 endpoints | Title and introduction wrap cleanly; source boundary, credits and links remain legible at the bottom. |

The exact captures read were `U06-companion-1200-1.png` through `U06-companion-1200-6.png`, plus `U06-companion-390-1.png` and `U06-companion-390-2.png`. Their SHA-256 values, in that order, were:

1. `3c347c1a48ada2fda0dc3765aaf546f85d97018d9f7ed584727134761f8a61d5`
2. `1ae4ae7801b2ff8b62592c3aaa9dc93c682c17367c49fa1ba81377fed5d95d23`
3. `e3fd36b3b67b3036c196b141a73eb923d89bc7d804b697eb43cae0b8aab38ffd`
4. `86291c06a1d8a4bb7e887f9fba6d9078503614f2fb4bd6fb1786fc888e425719`
5. `756be221181ff67cda4ea36d3954893c45d5adb5b8858cec796afc238630ff0d`
6. `b9a6f165af1bc5e521cc073d9e1f534833a5a2239d813e46e9ae8ee1af5c7ca9`
7. `7b8d5fc22a9e850225644145af0c374537b998da8aad946e8596aa855ca7a1a7`
8. `29d3a5a1a8918b2fe94aafaa56782776c36422db60627cb66c550d5c1bbb51a4`

## Automated visual invariants

At both widths, `scrollWidth` equalled viewport width, no overflowing elements or page errors were reported, the Bengali font check passed, and all three MathML displays had non-zero rendered dimensions. There are no images in this companion. The page contains no scripts.

## Finding and closure

The first render exposed crowded Bengali/number boundaries and an inaccurate browser-method label after Edge disappeared from this host. Root added the missing typographic spaces, corrected `শতংশ` to `শতাংশ`, and changed the visual runner to detect and record the browser actually used. Independent model review then found and root corrected the reduced-form condition for terminating decimals, the description of `3.0`, two cramped MathML accessible labels, an awkward alternate-reading sentence, and missing direct trace links to m81293 and the U06 canon record. I regenerated the reader and receipt, then read all eight captures above on the final reader hash. No further actionable visual finding remains within this scope.

This review does not substitute for independent human Bengali pedagogy/language review, learner testing, screen-reader/keyboard testing, or validated routing thresholds; all remain pending.
