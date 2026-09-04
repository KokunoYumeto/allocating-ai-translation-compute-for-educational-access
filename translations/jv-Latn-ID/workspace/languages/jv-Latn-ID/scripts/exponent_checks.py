"""Finite exponent-lesson verification; none of these checks is a speech fallback."""
import json
import re
import xml.etree.ElementTree as ET

from build import MATH, XML_LANG, local, translated
from config import LANG

UNIT = 'a10-exponents'
SOURCE_HASH = '98a02d384682f547090ab22173cf709d95a9336b7f5d749e98697e4d72ca041d'
PROSE_IDS = ['fs-id1170655213989', 'fs-id1170655228836', 'fs-id1170654937018',
             'fs-id1166424875923', 'fs-id1170654954211', 'fs-id1170655114560']
TABLE_IDS = ['fs-id1170654954100', 'eip-958']
CHART_IDS = ['fs-id1170655219218', 'fs-id1170655111941']
# Finite vocabulary verified against the actual displayed tokens/answers and canon.
NUMBERS = {
    '0': ('nol', 'nol'), '1': ('siji', 'satu'), '2': ('loro', 'dua'),
    '3': ('telu', 'tiga'), '4': ('papat', 'empat'), '5': ('lima', 'lima'),
    '7': ('pitu', 'tujuh'), '9': ('sanga', 'sembilan'), '12': ('rolas', 'dua belas'),
    '27': ('pitulikur', 'dua puluh tujuh'), '49': ('patang puluh sanga', 'empat puluh sembilan'),
    '81': ('wolung puluh siji', 'delapan puluh satu'),
    '125': ('satus salawé', 'seratus dua puluh lima'),
}
# These exact image/reference readings were read against the two primary images.
# Their hashes supplement (never replace) source/target/asset and numeric checks.
FIXED_READINGS = {
    'A10-EXP-D01': ('ba7ab183d73e2102ad9714f10e89511d55ef1f3089ff57bc94c0de77d73bfad2',
                    '9249adef422e43c35ddc507436ef064f13e9e3e5ed6385939fd57be44b4292b3',
                    '4623b012a776981acc76d42bb4b406a49dd35815fafbae2a4d5ba55ce0b75eb0'),
    'A10-EXP-D02': ('92f97dc7a2167cf123cb359c12c63ae7302492a9af8dd320f147a5d93ebbf019',
                    '4352f5bb540bee59bbd6ef28bd8822d76b5ddc79b28fed249d385b718988c54c',
                    '9ea9b5dbb0447d207d60bd2f3ccc9fd0d25e28a330d20646eb0888d0b065cb46'),
    'A10-EXP-R01': ('d201ecb0eeae6595efa39feda57017def2c815feca8f7f67cfe5d941ff3f9e42',
                    '47c57a1df9878f2863c837f7b66ce76d509a4fd6770ccd1440e7e9fa4bcbeec5',
                    '93c69e6ab426c95c5b4ed56540d5d3f2bee809c3bb69fceb6560b40db9a46b84'),
}


def numeral(value, track):
    assert value in NUMBERS, 'Unregistered exponent-lesson integer'
    return NUMBERS[value][0 if track.startswith('jv') else 1]


def normalized(text):
    return re.sub(r'\s+', ' ', text).strip()


def math_witness(node, track):
    """Verification of only the registered token vocabulary, never dispatch."""
    jv = track.startswith('jv')
    tag = local(node)
    if tag == 'mn':
        return numeral(node.text, track)
    if tag == 'mi':
        return ('aksara ' if jv else 'huruf ') + {'a': 'a', 'n': 'en'}[node.text]
    if tag == 'mo':
        return {'·': ' ping ' if jv else ' kali ', '.': '.', ',': ','}[node.text]
    if tag == 'msup':
        assert len(node) == 2
        return (math_witness(node[0], track) + ' pangkat ' + math_witness(node[1], track)
                + (', pungkasan pangkat' if jv else ', akhir pangkat'))
    assert tag in ('math', 'mrow')
    return ''.join(math_witness(child, track) for child in node)


def validate_scope(source, root, rules, track):
    from build_units import sha, tree_key
    from draft_units import merged_edits
    scope = rules['scope']
    assert (scope['unit'], scope['module'], scope['section'], scope['direct_child_slice_zero_based']) == (
        UNIT, 'm82453', 'fs-id1170655150800', [40, 53])
    assert len(source) == scope['selected_direct_children_including_context_title'] == 14
    assert sha(tree_key(source).encode()) == scope['indonesian_section_canonical_sha256'] == SOURCE_HASH
    assert sum(bool(n.get('id')) for n in source.iter()) == scope['source_ids_total'] == 32
    assert source[1].get('id') == scope['first_anchor'] == 'fs-id1170654982105'
    assert source[-1].get('id') == scope['last_top_level_anchor'] == 'fs-id1170655102894'
    replay = source if track == 'id-academic' else translated(source, track, merged_edits(UNIT))
    assert tree_key(root) == tree_key(replay), 'Changed whole exponent target'
    assert sha((LANG / 'sources.lock.json').read_bytes()) == scope['source_lock_sha256']
    assert [r['table_id'] for r in rules['table_fixtures']] == TABLE_IDS
    assert [r['element_id'] for r in rules['prose_fixtures']] == PROSE_IDS
    assert [r['media_id'] for r in rules['chart_fixtures']] == CHART_IDS
    refs = rules['reference_fixtures']
    assert len(refs) == 1 and refs[0]['element_id'] == 'fs-id1170655112606'
    assert refs[0]['target_id'] == TABLE_IDS[0] and refs[0]['link_ordinal'] == 1
    assert [n.get('target-id') for n in root.iter() if local(n) == 'link'] == [TABLE_IDS[0]]
    assert rules['nonspoken_source_blocks'] == []
    asset_raw = (LANG / 'translation/a10-exponents.assets.json').read_bytes()
    assert sha(asset_raw) == scope['asset_manifest_sha256'] == rules['asset_binding']['manifest_sha256']
    assets = json.loads(asset_raw)['assets']
    for chart, asset in zip(rules['chart_fixtures'], assets):
        assert chart['source_image'] == asset['source_src']
        assert chart['outputs'] == asset['outputs']
        output = asset['outputs'][track]
        raw = (LANG / output['path']).read_bytes()
        assert sha(raw) == output['sha256']
        expected_mime = 'image/svg+xml' if track.startswith('jv') else 'image/jpeg'
        assert output['mime_type'] == expected_mime
        if track.startswith('jv'):
            svg = ET.fromstring(raw)
            labels = [''.join(n.itertext()) for n in svg.iter() if local(n) == 'text']
            assert all(label in labels for label in chart['expected_asset_labels'][track])
        else:
            assert raw.startswith(b'\xff\xd8\xff')


def cell_witness(node, track):
    """Reconstruct a checked cell/prose witness, not a production narrator."""
    from build_units import speech_text
    if node.tag == '{' + MATH + '}math':
        return math_witness(node, track)
    if local(node) == 'emphasis' and node.text in ('a', 'n'):
        return ('aksara ' if track.startswith('jv') else 'huruf ') + {'a': 'a', 'n': 'en'}[node.text]
    if not len(node) and (node.text or '').strip() in NUMBERS:
        return numeral(node.text.strip(), track)
    result = speech_text(node.text, track, UNIT)
    for child in node:
        result += cell_witness(child, track) + speech_text(child.tail, track, UNIT)
    return result


def table_witness(table, track, index):
    rows = table.findall('.//{*}tbody/{*}row')
    jv = track.startswith('jv')
    names = ['kapisan', 'kapindho', 'katelu', 'kapapat', 'kalima'] if jv else ['pertama', 'kedua', 'ketiga', 'keempat', 'kelima']
    assert table.find('{*}tgroup').get('cols') == '2'
    assert all(len(row) == 2 for row in rows)
    if index == 0:
        headers = [normalized(cell_witness(n, track)) for n in table.findall('.//{*}thead/{*}row/{*}entry')]
        assert len(headers) == 2 and len(rows) == 4
        intro = {
            'jv-academic': 'Tabel rong kolom lan limang larik kalebu irah-irahan. Irah-irahan kolom: ',
            'jv-conversation': 'Tabel iki ana rong kolom lan limang larik kalebu judhul. Judhul kolom: ',
            'id-academic': 'Tabel dua kolom dan lima baris termasuk judul. Judul kolom: ',
        }[track] + '; '.join(headers) + '.'
        lines = [intro]
        for i, row in enumerate(rows):
            cells = [normalized(cell_witness(c, track)) for c in row]
            lines.append(('Larik' if jv else 'Baris') + ' data ' + names[i] + '. ' + headers[0] + ': ' + cells[0] + '. ' + headers[1] + ': ' + cells[1] + '.')
    else:
        assert table.find('.//{*}thead') is None and len(rows) == 5
        assert not ''.join(rows[0][0].itertext()).strip()
        intro = {
            'jv-academic': 'Tabel panyelesaian, limang larik lan rong kolom, tanpa irah-irahan kolom.',
            'jv-conversation': 'Tabel iki ana limang larik lan rong kolom, tanpa judhul kolom.',
            'id-academic': 'Tabel penyelesaian, lima baris dan dua kolom, tanpa judul kolom.',
        }[track]
        lines = [intro]
        left, right = ('kiwa', 'tengen') if jv else ('kiri', 'kanan')
        for i, row in enumerate(rows):
            cells = [normalized(cell_witness(c, track)).rstrip('.') for c in row]
            left_cell = 'Kolom ' + left + (': ' + cells[0] if cells[0] else ' kosong') + '.'
            lines.append(('Larik ' if jv else 'Baris ') + names[i] + '. ' + left_cell + ' Kolom ' + right + ': ' + cells[1] + '.')
    return '\n'.join(lines)


def validate_semantics(source, root, rules, track, bound):
    from build_units import fixture_element, sha, tree_key
    fixtures = rules['math_fixtures']
    assert len(fixtures) == len(bound) == 32
    for index, fixture in enumerate(fixtures, 1):
        assert fixture['id'] == f'A10-EXP-M{index:02}'
        tree = fixture_element(fixture['source_mathml'])
        assert sha(tree_key(tree).encode()) == fixture['source_tree_sha256']
        assert math_witness(tree, track) == fixture['expected'][track], 'Changed finite math reading'
        assert (fixture.get('standalone_readout_authorized') is False) == (10 <= index <= 16)
    assert len(bound.prose_only) == 7
    assert len(source.findall('.//{' + MATH + '}msup')) == 22
    assert sum(n.text == '·' for n in source.iter('{' + MATH + '}mo')) == 26
    nodes = {n.get('id'): n for n in root.iter() if n.get('id')}
    for index, fixture in enumerate(rules['table_fixtures']):
        assert fixture['expected'][track] == table_witness(nodes[fixture['table_id']], track, index), 'Changed table speech'
    jv = track.startswith('jv')
    for index, fixture in enumerate(rules['prose_fixtures']):
        assert fixture['override_before_child_narration'] is True
        node = nodes[fixture['element_id']]
        if index < 3:
            text = cell_witness(node, track).replace('“', '').replace('”', '')
            text = re.sub(r'\bn\b', 'aksara en' if jv else 'huruf en', text)
            text = normalized(text)
            text = text[0].upper() + text[1:]
        elif index == 3:
            lines = []
            for item in node:
                formula = math_witness(item.find('.//{' + MATH + '}math'), track)
                label = 'aksara a' if jv else 'huruf a'
                special = (item[-1].tail or '').strip().strip('”')
                lines.append(formula[0].upper() + formula[1:] + ('; diwaca ' if jv else '; dibaca ') + label + ' ' + special + '.')
            text = '\n'.join(lines)
        else:
            values = [(n.tail or '').strip() for n in node]
            assert values == (['125', '1'] if index == 4 else ['49', '0'])
            text = ('Bagean' if jv else 'Bagian') + ' a: ' + numeral(values[0], track) + '. ' + ('Bagean' if jv else 'Bagian') + ' be: ' + numeral(values[1], track) + '.'
        assert text == fixture['expected'][track], 'Changed whole-prose speech: ' + fixture['id']
    pattern = rules['notation_conventions']['finite_diagram_factor_pattern']
    assert (pattern['explicit_factors_before_ellipsis'], pattern['explicit_factors_after_ellipsis'], pattern['total_factor_count_symbol']) == (3, 1, 'n')
    track_index = ['jv-academic', 'jv-conversation', 'id-academic'].index(track)
    for fixture in rules['chart_fixtures'] + rules['reference_fixtures']:
        assert sha(fixture['expected'][track].encode()) == FIXED_READINGS[fixture['id']][track_index], 'Changed inspected diagram/reference readout'
    assert rules['answer_policy']['worked_steps'] == ['3^4', '3·3·3·3', '9·3·3', '27·3', '81']
    assert 3 ** 4 == 3 * 3 * 3 * 3 == 9 * 3 * 3 == 27 * 3 == 81
    checks = rules['answer_policy']['practice_checks']
    assert [r['source_answer'] for r in checks] == ['125', '1', '49', '0']
    for check, expected in zip(checks, [(5, 3, 125), (1, 7, 1), (7, 2, 49), (0, 5, 0)]):
        fixture = next(r for r in fixtures if r['id'] == check['question_fixture'])
        tree = fixture_element(fixture['source_mathml'])
        values = [int(n.text) for n in tree.iter('{' + MATH + '}mn')]
        assert values == list(expected[:2]) and values[0] ** values[1] == expected[2]
        assert nodes[check['source_answer_paragraph']].find('{*}span') is not None


def validate_readout(blocks, rules, track):
    assert len(blocks) == len(dict(blocks)) == 14
    combined = '\n'.join(text for _, text in blocks)
    cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
    assert combined.count(cue) == 2
    assert not re.search(r'[0-9^=·$]|(?<!aksara )(?<!huruf )\bn\b', combined)
    for group in ('table_fixtures', 'prose_fixtures', 'chart_fixtures', 'reference_fixtures'):
        for fixture in rules[group]:
            assert combined.count(fixture['expected'][track]) == 1, 'Missing or duplicated fixed speech'
            assert fixture['expected'][track] in dict(blocks)[fixture['anchor']]
    for fixture in rules['prose_fixtures'][4:]:
        question, answer = dict(blocks)[fixture['anchor']].split(cue)
        assert fixture['expected'][track] in answer and fixture['expected'][track] not in question
    worked = dict(blocks)['fs-id1170655121051']
    title = {'jv-academic': 'Panyelesaian', 'jv-conversation': 'Cara Ngrampungake', 'id-academic': 'Penyelesaian'}[track]
    question, answer = worked.split(title, 1)
    assert numeral('81', track) not in question and numeral('81', track) in answer
