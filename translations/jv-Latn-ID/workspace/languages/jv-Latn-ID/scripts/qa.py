"""Offline structural, mathematical, locale, narration and deterministic-build QA."""
import copy
import csv
import hashlib
import html.parser
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from config import LANG, UNITS, TRACKS
from build import number, speak_math, MATH, XML_LANG
from safe_io import write_text


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(root):
    return [(e.tag, e.get('id'), e.get('target-id'), e.get('src'), len(e)) for e in root.iter()]


def math_structure(root):
    result = []
    for m in root.iter('{' + MATH + '}math'):
        m = copy.deepcopy(m)
        m.tail = None
        # The only deliberately translated MathML prose token.
        for e in m.iter('{' + MATH + '}mtext'):
            if e.text == 'lan':
                e.text = 'dan'
        result.append(ET.canonicalize(ET.tostring(m, encoding='unicode'), strip_text=True))
    return result


class Reader(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.images, self.tracks, self.maths, self.heads = [], [], [], [], 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.append(a.get('href', ''))
        if tag == 'img':
            self.images.append(a)
        if 'data-register' in a:
            self.tracks.append((a['data-register'], a.get('lang')))
        if tag == 'math':
            self.maths += 1
        if tag == 'th':
            self.heads.append(a)


def outputs():
    # This receipt certifies only the initial pilot; later unit receipts are separate.
    paths = [LANG / 'review/pilot.html']
    paths += [LANG / f'translation/number-line.{locale}.svg' for locale in ('id-ID', 'jv-Latn-ID')]
    for unit in UNITS:
        for track in TRACKS:
            paths.append(LANG / f'translation/{unit["key"]}.{track}.cnxml')
            paths += [LANG / f'review/audio/{unit["key"]}.{track}.{suffix}' for suffix in ('md', 'ssml')]
    return {p.relative_to(LANG).as_posix(): sha(p) for p in sorted(paths) if p.is_file()}


def run():
    checks, units = [], []
    lock = json.loads((LANG / 'sources.lock.json').read_text(encoding='utf-8'))
    for f in lock['files']:
        assert sha(LANG / f['retained_at']) == f['sha256'], f['retained_at']
    for a in lock['assets']:
        if 'retained_at' in a:
            assert sha(LANG / a['retained_at']) == a['sha256']
    checks.append('Retained provenance/notice hashes match acquisition lock')
    count_math = 0
    for unit in UNITS:
        source_path = LANG / f'translation/{unit["key"]}.id-academic.cnxml'
        bound = next(u for u in lock['units'] if u['key'] == unit['key'])
        assert sha(source_path) == bound['indonesian_excerpt_sha256']
        source = ET.parse(source_path).getroot()
        ids = [e.get('id') for e in source.iter() if e.get('id')]
        assert len(ids) == len(set(ids))
        assert all(e.get('target-id') in ids for e in source.iter() if e.get('target-id'))
        assert unit['next_anchor'] not in ids
        for track in ('jv-academic', 'jv-conversation'):
            target = ET.parse(LANG / f'translation/{unit["key"]}.{track}.cnxml').getroot()
            assert identity(source) == identity(target), f'{unit["key"]} {track}: structure/ID changed'
            assert math_structure(source) == math_structure(target), f'{unit["key"]} {track}: math changed'
            assert target.get(XML_LANG) == 'jv-Latn-ID'
            assert re.findall(r'\d+(?:\.\d+)?', ''.join(source.itertext())) == re.findall(r'\d+(?:\.\d+)?', ''.join(target.itertext())), 'Prose numeric facts changed'
        maths = len(list(source.iter('{' + MATH + '}math')))
        count_math += maths * 3
        units.append({'unit': unit['key'], 'source_id_count': len(ids), 'source_math_count': maths, 'source_exercises': len(source.findall('.//{*}exercise')), 'source_solutions': len(source.findall('.//{*}solution')), 'source_scope': unit['scope'], 'next_anchor': unit['next_anchor']})
    checks += ['All source element hierarchy, IDs, cross-references and image source identifiers preserved in both Javanese tracks', 'MathML invariant apart from explicit dan-to-lan linguistic mtext change', 'Numeric prose facts and localized root language checked', 'No unresolved in-excerpt references and next excluded anchor not falsely covered']

    source = ET.parse(LANG / 'translation/a00-number-sense.id-academic.cnxml').getroot()
    for exercise in source.findall('.//{*}exercise'):
        problem = exercise.find('{*}problem')
        candidate_math = problem.findall('.//{' + MATH + '}math')[-1]
        values = []
        for e in candidate_math.find('{' + MATH + '}mrow'):
            if e.tag == '{' + MATH + '}mn':
                values.append(Fraction(e.text))
            elif e.tag == '{' + MATH + '}mfrac':
                values.append(Fraction(int(e[0].text), int(e[1].text)))
        expected = [[int(x) for x in values if x.denominator == 1 and x > 0], [int(x) for x in values if x.denominator == 1 and x >= 0]]
        items = exercise.findall('{*}solution/{*}list/{*}item')
        if exercise.get('id') == 'fs-id1398237':
            # Worked solution contains explanatory 1 and 0 before the answer list.
            actual = [[3,15,105], [0,3,15,105]]
            assert ['3','15','105'] == [e.text for e in items[0].findall('.//{' + MATH + '}mn')][-3:]
            assert ['0','3','15','105'] == [e.text for e in items[1].findall('.//{' + MATH + '}mn')][-4:]
        else:
            actual = [[int(n) for n in re.findall(r'\d+', ''.join(item.itertext()))] for item in items]
        assert actual == expected, exercise.get('id')
    age = ET.parse(LANG / 'translation/a10-variable-bridge.id-academic.cnxml').getroot()
    rows = age.findall('.//{*}table/{*}tgroup/{*}tbody/{*}row')
    pairs = [[int(''.join(e.itertext()).strip()) for e in row] for row in rows[:3]]
    assert pairs == [[12,15],[20,23],[35,38]] and all(b-a == 3 for a,b in pairs)
    assert ''.join(rows[3][0].itertext()).strip() == 'g'
    assert ''.join(rows[3][1].itertext()).strip() == 'g+3'
    checks.append('Worked example, both practice answers, and all Greg/Alex table pairs independently checked')

    id_svg = ET.parse(LANG / 'translation/number-line.id-ID.svg').getroot()
    jv_svg = ET.parse(LANG / 'translation/number-line.jv-Latn-ID.svg').getroot()
    assert len(list(id_svg.iter())) == len(list(jv_svg.iter()))
    for a,b in zip(id_svg.iter(), jv_svg.iter()):
        assert a.tag == b.tag
        assert {k:v for k,v in a.attrib.items() if k != XML_LANG} == {k:v for k,v in b.attrib.items() if k != XML_LANG}
        if (a.text or '').isdigit():
            assert a.text == b.text
    assert jv_svg.get(XML_LANG) == 'jv-Latn-ID'
    checks.append('Number-line SVG geometry, tick labels and source identity preserved')

    page = (LANG / 'review/pilot.html').read_text(encoding='utf-8')
    reader = Reader()
    reader.feed(page)
    assert len(reader.ids) == len(set(reader.ids)), 'Duplicate HTML ID'
    assert reader.maths == count_math
    for unit in UNITS:
        source = ET.parse(LANG / f'translation/{unit["key"]}.id-academic.cnxml').getroot()
        for track in TRACKS:
            assert all(unit['module'] + '--' + track + '--' + e.get('id') in reader.ids for e in source.iter() if e.get('id')), 'Missing rendered source ID'
    for link in reader.links:
        if link.startswith('#'):
            assert link[1:] in reader.ids, link
        elif not re.match(r'https?://', link):
            assert (LANG / 'review' / link).is_file(), link
    assert len(reader.images) == 3 and all(x.get('alt') and x.get('src', '').startswith('data:image/svg+xml;base64,') for x in reader.images)
    assert all(TRACKS[t][0] == lang for t,lang in reader.tracks)
    assert len(reader.heads) == 6 and all(h.get('scope') == 'col' for h in reader.heads)
    assert '<h4>Wangsulan / Jawaban</h4>' not in page
    assert '<span lang="jv-Latn-ID">Wilangan lan aljabar</span>' in page
    assert '<footer id="credits" lang="en">' in page
    assert '<script' not in page and 'https://' not in re.sub(r'<a[^>]*>', '', page).split('<body>')[0]
    checks.append('Offline HTML: unique IDs, all links resolved, all MathML rendered, images embedded with alt text, register labels/locales and table headers present')

    for unit in UNITS:
        source = ET.parse(LANG / f'translation/{unit["key"]}.id-academic.cnxml').getroot()
        expected = [unit['module'] + '--' + el.get('id', 'title') for el in source]
        for track, (locale, _) in TRACKS.items():
            path = LANG / f'review/audio/{unit["key"]}.{track}.ssml'
            ssml = ET.parse(path).getroot()
            assert ssml.get(XML_LANG) == locale
            marks = [x.get('name') for x in ssml.findall('{*}mark')]
            assert marks == expected and len(marks) == len(set(marks))
            assert all(''.join(p.itertext()).strip() for p in ssml.findall('{*}p'))
            assert 'lorolas' not in ''.join(ssml.itertext()) and 'limalan' not in ''.join(ssml.itertext())
            untitled = sum(solution.find('{*}title') is None for solution in source.findall('.//{*}solution'))
            cue = 'Wangsulan.\n' if track.startswith('jv') else 'Jawaban.\n'
            assert ''.join(ssml.itertext()).count(cue) == untitled, 'Missing or duplicated spoken answer cue'
    for num, expected in [('0','nol'), ('12','rolas'), ('15','limalas'), ('23','telulikur'), ('35','telung puluh lima'), ('5.2','lima koma loro'), ('241','rong atus patang puluh siji'), ('376','telung atus pitung puluh enem')]:
        assert number(num, True) == expected
    frac = ET.fromstring(f'<math xmlns="{MATH}"><mfrac><mn>1</mn><mn>4</mn></mfrac></math>')
    assert speak_math(frac, True) == 'pecahan: siji per papat, pungkasan pecahan'
    expression = ET.fromstring(f'<math xmlns="{MATH}"><mrow><mi>g</mi><mo>+</mo><mn>3</mn></mrow></math>')
    assert speak_math(expression, True) == 'aksara ge ditambah telu'
    checks.append('Six SSML files: locale, source marks, content, untitled-solution answer cues; number, fraction and variable narration fixtures')

    with (LANG / 'terminology.csv').open(encoding='utf-8', newline='') as f:
        terms = list(csv.DictReader(f))
    assert all(None not in t and all(v is not None for v in t.values()) for t in terms)
    assert len({t['id'] for t in terms}) == len(terms)
    canon = json.loads((LANG / 'canon/sources.lock.json').read_text(encoding='utf-8'))['records']
    # User requested 10–20 initially, then targeted expansion for new topics.
    assert len(canon) >= 10
    assert all(c in {r['id'] for r in canon} for t in terms for c in t['canon_refs'].split())
    checks.append('Terminology CSV well-formed; initial 10–20-entry canon extended by topic, all term references valid')

    before = outputs()
    subprocess.run([sys.executable, str(LANG / 'scripts/build.py')], check=True, capture_output=True)
    assert before == outputs(), 'Build is not byte-identical'
    checks.append('Second build byte-identical for all committed generated reader, translation and narration outputs')
    return {'schema':'jv-pilot-qa-v1', 'status':'structural_pass_human_review_pending', 'date':'2026-08-30', 'checks':checks, 'units':units, 'terminology_entries':len(terms), 'canon_entries':len(canon), 'ssml_files':6, 'synthesized_audio_files':0, 'human_linguistic_review':False, 'listening_review':False, 'wcag_certified':False, 'visual_review':'See VISUAL_REVIEW.md for actual browser observation; not asserted by this script', 'output_sha256':outputs()}


if __name__ == '__main__':
    result = run()
    target = LANG / 'qa/receipt.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    write_text(target, json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'PASS: {len(result["checks"])} structural/build check groups; human language/audio review remains pending.')
