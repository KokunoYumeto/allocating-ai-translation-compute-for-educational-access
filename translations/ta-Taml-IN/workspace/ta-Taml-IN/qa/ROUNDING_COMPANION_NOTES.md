# U006 rounding recovery companion — bounded draft

2026-08-31. Authored only `translation/recovery-rounding.xhtml` and this note. This is original Tamil support for source `m81243#fs-id2472737`, not a replacement translation, and not a claim that U006 delivery or the full assignment is complete. No source, shared log, stylesheet, reader, EPUB, PDF or commit was changed. No new download or media asset was needed. Free C: space before authoring was 10,475,712,512 bytes.

## Scope and exact identity

Companion version 0.1.0, SHA-256 **`84fe718d7fd236bbe943753b4bedad5ad1041856b15343498e653c1de8132ab3`**. The XHTML fragment has **14 top-level sections, 50 unique `ta-round-*` IDs, 80 internal links, 16 admitted assessment items and 16 one-to-one answers**. Each answer has a useful reason and misconception feedback, plus a link to the corresponding explanation. There are four items of each kind: diagnostic D, practice P, mastery M and retry T. Some items have multiple requested responses; 16 is the item count, not a claim of 16 atomic responses.

The source-faithful U006 fragment remains SHA-256 `5ae5553b9ea293ff95e910eb36689c524faaf89954cbdf88d350f302cb7b7a3c`. Its 23 source figures are not duplicated or required to operate the companion. The companion's 29,504 explanation is explicitly labeled new support for that source example; the source's solution and its repaired alternatives remain untouched.

## Actual evidence consulted at drafting, revision and QA

Read the current root instructions, persistent goal, terminology ledger, complete U006 Tamil text, the complete corresponding English and Indonesian witness text, and U006 translation and figure notes. Long combined terminal output was truncated, so omitted Tamil worked tables/final text and the beginning of the figure notes were read again separately rather than assumed read.

Read actual existing OCR pages 30 and 31 and inspected both complete page PNGs before drafting. These are Government of Tamil Nadu / SCERT Class 6 Term 1 Mathematics, first edition 2018, PDF pages 30–31 / printed 24–25; they are not an assertion about current board alignment. Canon C15 supports the distinction between exact values and **சுமார் / தோராயம் / உத்தேச மதிப்பு**, and nearest tens/hundreds/thousands. Canon C16 supplies **முழுமையாக்குதல்**, the target-place/immediately-right-digit/compare-with-5/zero-replacement sequence, with 8,436→8,400 and 78,794→79,000. The actual image, not corrupted OCR inequality marks or “76,194”, established the rule. No classroom seed-estimation activity or canon exercise was copied into the companion.

At revision/QA, reread both actual OCR files and compared the drafted four-step rule, exact/approximate distinction and zero wording with the already visually resolved tables. This led to spelling out that an immediate right digit 5 indicates **at or beyond** the midpoint: it is an exact tie only if there are no later digits or they are all zero. Thus 29,504 at thousands is not called a tie. Also clarified the M3/T3 notation instruction: use exact equality for an unchanged value and approximation for a changed rounded value; the draft does not assert that `0 ≈ 0` is intrinsically false.

These consultation details live in this bounded note; parent owns any shared consultation-log update.

| Actual input | SHA-256 |
|---|---|
| English `provenance/m81243.en.cnxml` | `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b` |
| Indonesian `provenance/m81243.id-ID.cnxml` | `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251` |
| `qa/U006-translation-notes.md` | `b02703631fe475ac8e30613d86570990d444425a98f026501e5c6c0f84ca3303` |
| `qa/U006-figure-notes.md` | `c9fdd08e97fc8d11543a966a07953e76b3e8efe670a2f42ae79e5c5dfb03c446` |
| `terminology.tsv` | `3287be4a0048d005ad4aec7f7b3a2705aeb7ad8f2805f5e2656ada05b546a700` |
| `canon/README.md` | `cd36b6a2c5cefcb9f745eb35b22c03c536fcafb199e9141261461a89880330ac` |
| Actual OCR `page-030.txt` | `f3d73807cdabbd85f2b5be1b3a69eede37099d78d01f76eaae8efd8fdb35bf75` |
| Actual OCR `page-031.txt` | `1867e7d8e0a8644055da66153df717f16551a588f6c81a122798562b3eb2c599` |
| Actual image `page-030.png` | `09c6555d066cf6d0c45cdb847207f67d92070be2993b395bf59beb95b5530c12` |
| Actual image `page-031.png` | `3adb8a6bb7696d43cbb5d7c8a20170143058ef48da4dafe86ddeb25f1d523b8f` |

English upstream pin: `38cae454e644abf9f0a623e876994553881597c9`; Indonesian selected release v0.2.7 / commit `3de9207f56f8b5c57c017abf973fb04e00d740f1`.

## Teaching and routing decisions

| Number family | Explanation | Independent assessment coverage |
|---|---|---|
| D1/P1/M1/T1 | R1: named place, digit in it, immediately right-hand digit | D1 identifies 6,482 hundreds 4/right tens 8. P1 identifies all three target/right pairs in 7,361 without being given target digits. M1 rounds 8,246 at thousands; T1 rounds 5,728 at hundreds. |
| D2/P2/M2/T2 | R2: nearest multiples, distances, exact ties | 65 at tens; 248 and 250 at hundreds; 735 at tens; 850 at hundreds. Both distance and convention reasoning are supplied. |
| D3/P3/M3/T3 | R3: zero decision digit, placeholder zeros, exact versus approximate | 4,032 at thousands; 5,009 at hundreds; 6,040 and 0 at thousands; 7,003 and 0 at hundreds. Zero is an already-exact multiple and does not become a positive multiple. |
| D4/P4/M4/T4 | R4: carry across one or more 9s and create a new leading 1 | 9,950 at hundreds; 9,999 at tens; 99,500 at thousands; 99,995 at tens. Explanation also covers source 29,504→30,000 and new 999→1,000. |

All routes operate within this fragment without teacher judgment, JavaScript, a source-reader link or an Internet resource. A notebook records which numbered branches need work. Every diagnostic miss maps to the same-numbered R; multiple misses start at the earliest needed R and continue through R4 before all P items. All-correct diagnostics go to all P items, not directly to completion. P or M misses map to R then the corresponding T. Needed T items must all be tried and their reasons checked; another miss loops through the corresponding R and T. Successful retries lead to **all four M items with answers hidden**, not to an automatic pass. Completion requires all requested responses and reasons in M1–M4 to be correct independently. This is a local learning gate, not a validated placement/mastery instrument; repeated-item success is not evidence of generalization to unseen work.

The rule is explicitly scoped to nonnegative whole numbers written without a decimal point or fraction notation. International comma grouping follows the source. At exact half distances the larger multiple is chosen; no universal claim about all rounding systems or negative numbers is made. New changed-rounding statements use semantic MathML `≈`; exact arithmetic and unchanged-value statements use `=`. R3 also says each requested place must start from the original number, not a previously rounded answer.

Terminology follows **முழுமையாக்கல் / முழுமையாக்குதல்**, **இடமதிப்பு**, **இலக்கம்**, **பூச்சியம்**, **அருகிலுள்ள பத்துகள் / நூறுகள் / ஆயிரங்கள்**, and the existing international place labels. Instead of relying solely on the provisional technical label for regrouping, R4 explains carrying with named positions, 10 of one place becoming 1 of the next, and an explicit new leading 1. Naturalness of these long carry sentences and the word **மடங்கு** in this learner register still needs Tamil educator/native-editor review. No such approval is claimed.

## Completed checks and limits

Two XML parsers (ElementTree and lxml) accepted the fragment. All IDs have the intended prefix and are unique; all 80 hrefs are local and resolve. Each of 16 prompts has exactly one linked answer, one reason paragraph, one feedback paragraph and its matching R link. All namespace/tag, one semantic table's column/row header scopes, absence of embedded media/network dependencies, and absence of scripts/event handlers passed. The table describes three exact target/right-digit mappings rather than using a screenshot.

All **30 MathML expressions** were checked: **20 rounding expressions (18 distinct input/place/output triples), eight exact arithmetic/identity expressions, and two explanatory operator glyphs**. Every approximate pair agrees with an independently computed nearest-distance, tie-up result; every exact statement is arithmetically true. Separately checked the prose-only 258→300 at hundreds, the D1/P1 target/right digits, all described carry positions, and stated distance pairs: 65→(5,5), 248→(48,52), 250→(50,50), 735→(5,5), 850→(50,50), 29,504→(504,496), 99,500→(500,500), 99,995→(5,5). The four named place/carry routes were manually traced, including multiple-error branches and failed-retry loops.

A digit-string carry implementation, nearest-distance tie-up calculation and integer formula agreed for every n from 0 through 99,999 at bases 10, 100 and 1,000: **300,000 cases**. This tests the mathematics, not learner efficacy or rendering. No Python floating-point/banker's `round()` was used.

Pending: independent Tamil/native/educator editing; browser and narrow-layout inspection; actual assistive-technology testing; parent reader/EPUB integration and package checks; PDF creation/search/layout QA. No browser, build or PDF operation was performed for this draft. The original fragment has no CSS reference because it is intended for later reader integration; raw-browser appearance is not a finished delivery claim.

### Reproducible bounded check

Run the following Python block from the workspace root (it only reads files). In PowerShell, set `PYTHONIOENCODING=utf-8` and pass it through a here-string to `python -`. It is stored here rather than creating an unauthorized third file.

```python
from pathlib import Path
from hashlib import sha256
from collections import Counter
from lxml import etree
import xml.etree.ElementTree as E

p = Path('ta-Taml-IN/translation/recovery-rounding.xhtml')
b = p.read_bytes()
r = E.fromstring(b)
etree.fromstring(b)
X = '{http://www.w3.org/1999/xhtml}'
M = '{http://www.w3.org/1998/Math/MathML}'
ids = [e.get('id') for e in r.iter() if e.get('id')]
assert len(ids) == len(set(ids)) == 50
assert all(i.startswith('ta-round-') for i in ids)
links = [e.get('href') for e in r.iter(X + 'a')]
assert len(links) == 80 and all(h.startswith('#') and h[1:] in ids for h in links)
items = [e for e in r.iter() if e.get('data-kind')]
answers = [e for e in r.iter() if e.get('data-answer-for')]
assert Counter(e.get('data-kind') for e in items) == dict(diagnostic=4, practice=4, mastery=4, retry=4)
assert Counter(e.get('data-answer-for') for e in answers) == Counter(e.get('id') for e in items)
for item in items:
    a = next(a for a in answers if a.get('data-answer-for') == item.get('id'))
    assert len(a.findall(X + "p[@class='reason']")) == 1
    assert len(a.findall(X + "p[@class='feedback']")) == 1
    assert '#' + item.get('data-remediation') in [e.get('href') for e in a.iter(X + 'a')]
    assert '#' + a.get('id') in [e.get('href') for e in item.iter(X + 'a')]
for e in r.iter():
    assert e.tag.startswith((X, M))
    assert e.tag.rsplit('}', 1)[-1] not in {'script', 'iframe', 'img', 'object', 'embed'}
    assert not any(k.lower().startswith('on') for k in e.attrib)
for row in r.findall('.//' + X + 'table/' + X + 'thead/' + X + 'tr'):
    assert all(e.tag == X + 'th' and e.get('scope') == 'col' for e in row)
for row in r.findall('.//' + X + 'table/' + X + 'tbody/' + X + 'tr'):
    assert len(row) == 3 and row[0].get('scope') == 'row'
bases = {65:10, 4032:1000, 9950:100, 62:10, 29504:1000, 999:10,
         248:100, 250:100, 5009:100, 9999:10, 8246:1000, 735:10,
         6040:1000, 99500:1000, 5728:100, 850:100, 7003:100, 99995:10}
counts = Counter()
for math in r.iter(M + 'math'):
    s = ''.join(math.itertext()).replace(',', '')
    if s in {'≈', '='}:
        counts['symbol'] += 1
    elif '≈' in s:
        n, result = map(int, s.split('≈'))
        base = bases[n]
        lo = n // base * base
        hi = lo + base
        assert result == (lo if n-lo < hi-n else hi)
        counts['rounding'] += 1
    else:
        left, right = s.split('=')
        # Evaluate only the known simple integer forms, not arbitrary file code.
        if '+' in left:
            value = sum(map(int, left.split('+')))
        elif '−' in left:
            a, c = map(int, left.split('−'))
            value = a-c
        else:
            value = int(left)
        assert value == int(right)
        counts['exact'] += 1
assert counts == dict(symbol=2, rounding=20, exact=8)
assert (6482 // 100) % 10 == 4 and (6482 // 10) % 10 == 8
for base, target, right in [(10,6,1), (100,3,6), (1000,7,3)]:
    assert (7361 // base) % 10 == target
    assert (7361 // (base//10)) % 10 == right
for n, base, d in [(65,10,(5,5)), (248,100,(48,52)), (250,100,(50,50)),
                   (735,10,(5,5)), (850,100,(50,50)), (29504,1000,(504,496)),
                   (99500,1000,(500,500)), (99995,10,(5,5))]:
    lo = n // base * base
    assert (n-lo, lo+base-n) == d
assert ((258+50)//100)*100 == 300

def by_digits(n, base):
    k = {10:1, 100:2, 1000:3}[base]
    s = list(str(n).zfill(k+1))
    cut = len(s)-k
    increment = int(s[cut]) >= 5
    for j in range(cut, len(s)):
        s[j] = '0'
    if increment:
        j = cut-1
        while j >= 0 and s[j] == '9':
            s[j] = '0'
            j -= 1
        if j >= 0:
            s[j] = str(int(s[j])+1)
        else:
            s.insert(0, '1')
    return int(''.join(s))

cases = 0
for n in range(100000):
    for base in (10, 100, 1000):
        lo = n // base * base
        hi = lo+base
        nearest = lo if n-lo < hi-n else hi
        assert by_digits(n, base) == nearest == ((n+base//2)//base)*base
        cases += 1
assert sha256(Path('ta-Taml-IN/translation/m81243-fs-id2472737.cnxml').read_bytes()).hexdigest() == '5ae5553b9ea293ff95e910eb36689c524faaf89954cbdf88d350f302cb7b7a3c'
print('PASS:', len(items), 'items;', len(ids), 'IDs;', len(links), 'local links;', dict(counts), ';', cases, 'numeric cases')
print('Companion SHA-256:', sha256(b).hexdigest(), 'bytes:', len(b))
```
