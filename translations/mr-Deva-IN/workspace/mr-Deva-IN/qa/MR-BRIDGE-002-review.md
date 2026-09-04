# MR-BRIDGE-002 review

Date: 2026-08-30. Status: buildable, visually checked review draft; not native-speaker/teacher approved.

XML SHA-256: `0a46a929a80df9755bc4f4df95102049c524f2506daf03c37952a368f01a1172`.
HTML SHA-256: `88f9a396f3dc877f38b0ceac23aeeefc3682c299bf3e2db85cd85c87582b7e84`.

Four contiguous A20 m81373 source blocks are translated: Sylvia's worked example, Bryan's and Anthony's practice notes, and the optional resource note. Names, variables, questions, answers and all original nested/media IDs are retained. EN/ID fragment comparisons and all eight original equation-image variants were actually read. Typography differs; mathematical content agrees. Source media IDs now anchor the corresponding transcribed equations, not discarded images.

Independent `test_unit2_math.py`: 12 tests pass, covering exact arithmetic, all model/table values, four new practice answers, symbolic linear rules, whole-day domain restrictions, selected source IDs/content and the preserved resource URL. The fractional/negative-time calculations evaluate only the algebraic expression; they do not assign values to the restricted function outside its domain.

The generic builder passes its structural/provenance/math-string checks; rebuilding with the later image-capable version leaves this image-free HTML unchanged. The isolated Edge browser receipt records 1100/420-pixel checks with no overflow, script errors or network requests, and all four original question/answer return links working. All nine desktop and nine phone sections were visually inspected. The table was revised for caption/column spacing and rechecked. The external source resource was retained but not visited or verified.

Canon effects and actual reads are in canon/CONSULTATIONS.md. This unit adds four original practice questions with full answers; its model-domain choices and connecting explanations are visibly original. It completes neither m81373 nor A20. No PDF, human approval, full-book build, push or publication is claimed.
