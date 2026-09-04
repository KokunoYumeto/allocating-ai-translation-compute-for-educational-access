"""Build and verify the next two source-bound reader/narration units offline.

The A10 notation lesson uses finite source-context fixtures, never a generic
algebra-to-speech guess. A00's monetary and place-value readings are explicit.
"""
import argparse
import copy
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from build import CN, MATH, XML_LANG, STYLE, local, number, render, speak_math, spoken_text, translated
from config import LANG, TRACKS
from draft_units import UNITS, merged_edits, products as draft_products
from qa import Reader
from safe_io import write_bytes

NONSPOKEN_BLOCKS = {
    'a10-equality-symbols': ['fs-id1171789687379'],
    'a10-grouping-symbols': ['fs-id1166424830424'],
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def tree_key(element):
    element = copy.deepcopy(element)
    element.tail = None
    return ET.canonicalize(ET.tostring(element, encoding='unicode'), strip_text=True, rewrite_prefixes=True)


def fixture_element(text):
    return ET.fromstring(f'<wrapper xmlns:m="{MATH}">{text}</wrapper>')[0]


def narration_tree_key(element):
    """Diagnostic linguistic-shape comparison, never source dispatch authority."""
    element = copy.deepcopy(element)
    for node in element.iter('{' + MATH + '}mtext'):
        if re.fullmatch(r'[^\W\d_]+(?:\s+[^\W\d_]+)*', (node.text or '').strip()):
            node.text = '__registered_linguistic_mtext__'
    return tree_key(element)


class BoundMath(dict):
    """Exact readings plus formulas forbidden outside a whole-prose readout."""
    def __init__(self):
        super().__init__()
        self.prose_only = set()


def source_bound_math(root, rules, track, source_root=None):
    source_root = source_root if source_root is not None else root
    if rules.get('scope', {}).get('unit') == 'a00-rounding':
        from rounding_checks import bind
        return bind(root, rules, track, source_root)
    indexed = {(row['anchor'], row['math_ordinal']): row for row in rules['math_fixtures']}
    assert len(indexed) == len(rules['math_fixtures'])
    source_expressions = {}
    for block in source_root:
        for ordinal, expression in enumerate(block.iter('{' + MATH + '}math'), 1):
            key = (block.get('id'), ordinal)
            if key not in indexed or tree_key(expression) != tree_key(fixture_element(indexed[key]['source_mathml'])):
                raise ValueError(f'unsupported_source_bound_narration: {key}')
            source_expressions[key] = expression
    assert set(source_expressions) == set(indexed), 'Unused source math fixture'
    mapped, used = BoundMath(), set()
    for block in root:
        for ordinal, expression in enumerate(block.iter('{' + MATH + '}math'), 1):
            key = (block.get('id'), ordinal)
            if key not in source_expressions:
                raise ValueError(f'unsupported_translated_math_narration: {key}')
            expected = source_expressions[key]
            if source_root is not root and track.startswith('jv') and list(expected.iter('{' + MATH + '}mtext')):
                scope = rules['scope']
                candidates = [unit for unit, descriptor in UNITS.items()
                              if descriptor['module'] == scope['module']
                              and descriptor['section'] == scope['section']
                              and (descriptor['slice'] == scope.get('direct_child_slice_zero_based')
                                   or descriptor['slice'] is None and scope.get('complete_section') is True)]
                assert len(candidates) == 1, 'Unregistered mtext translation scope'
                expected = translated(expected, track, merged_edits(candidates[0]))
                expected.attrib.pop(XML_LANG, None)
            if tree_key(expression) != tree_key(expected):
                raise ValueError(f'unsupported_translated_math_narration: {key}')
            mapped[id(expression)] = indexed[key]['expected'][track]
            fixture = indexed[key]
            if fixture.get('standalone_readout_authorized') is False:
                prose = next((row for row in rules.get('prose_fixtures', [])
                              if row['id'] == fixture['requires_prose_fixture']), None)
                assert prose is not None and prose['element_id'] == fixture['requires_prose_element'], 'Missing required prose context'
                assert prose.get('override_before_child_narration') is True
                parent = next((node for node in block.iter() if node.get('id') == prose['element_id']), None)
                assert parent is not None and expression in list(parent.iter()), 'Formula outside required prose context'
                mapped.prose_only.add(id(expression))
            used.add(key)
    assert used == set(indexed), 'Unused source math fixture'
    if rules.get('scope', {}).get('unit') == 'a10-exponents':
        # Direct helper calls need the same whole-source authority as blocks().
        # Keep actual nodes alive and snapshot their exact trees: neither a
        # copied ID nor a mutation after binding grants a fixed readout.
        from exponent_checks import validate_semantics
        validate_nonmath_fixtures(root, source_root, 'a10-exponents', rules, track)
        validate_semantics(source_root, root, rules, track, mapped)
        mapped.narration_track = track
        mapped.narration_rules = sha(json.dumps(rules, sort_keys=True).encode())
        mapped.narration_nodes = {id(node): (node, tree_key(node)) for node in root.iter()}
    return mapped


def speech_text(text, track, unit):
    text = text or ''
    is_jv = track.startswith('jv')
    if unit == 'a10-operation-symbols':
        headings = {'Asile yaiku…': 'Asile yaiku:', 'Asile…': 'Asile:', 'Hasilnya adalah…': 'Hasilnya adalah:'}
        if text.strip() in headings:
            return headings[text.strip()]
        if '…' in text:
            raise ValueError('unsupported_ellipsis_context')
    if unit == 'a10-equality-symbols':
        # The selected source contains registered plain-text relations in
        # addition to its exact MathML fixtures. Keep this mapping local.
        relations = ({'<':'luwih cilik tinimbang', '>':'luwih gedhé tinimbang'}
                     if is_jv else {'<':'kurang dari', '>':'lebih dari'})
        for symbol, reading in relations.items():
            text = re.sub(r'\s*' + re.escape(symbol) + r'\s*', ' ' + reading + ' ', text)
        text = text.replace('“ ', '“').replace(' ”', '”')
    if unit == 'a00-place-value':
        text = re.sub(r'\$([0-9]+(?:\.[0-9]+)?)', lambda match: number(match[1], is_jv) + ' dolar Amerika Serikat', text)
        text = text.replace('basis-10', 'basis sepuluh')
        text = text.replace('+', ' ditambah ').replace('=', ' padha karo ' if is_jv else ' sama dengan ')
    return spoken_text(text, is_jv)


def validate_nonmath_fixtures(root, source_root, unit, rules, track):
    """Bind fixed chart/table/prose speech to exact source and target wording."""
    if unit not in ('a00-name-whole', 'a00-write-whole', 'a10-expressions-equations', 'a10-exponents'):
        return
    if unit == 'a00-name-whole':
        assert [row['table_id'] for row in rules['table_fixtures']] == ['fs-id1171100715908']
        assert [row['element_id'] for row in rules['prose_fixtures']] == ['fs-id3400199']
    elif unit == 'a10-expressions-equations':
        assert [row['table_id'] for row in rules['table_fixtures']] == ['fs-id1170655221887', 'fs-id1170655090988', 'eip-10']
    elif unit == 'a10-exponents':
        from exponent_checks import validate_scope
        validate_scope(source_root, root, rules, track)
    else:
        assert rules['table_fixtures'] == []
        assert [row['element_id'] for row in rules['prose_fixtures']] == [
            'fs-id4163187', 'fs-id1885399', 'fs-id2590590', 'fs-id865214', 'fs-id1395137', 'fs-id1586764']
        assert [row['media_id'] for row in rules['chart_fixtures']] == ['fs-id2668978', 'fs-id2903601', 'fs-id1345376']
        assert sha(tree_key(source_root).encode()) == rules['scope']['indonesian_section_canonical_sha256'], 'Changed whole writing source'
        replay = source_root if track == 'id-academic' else translated(source_root, track, merged_edits(unit))
        assert tree_key(root) == tree_key(replay), 'Changed whole writing target'
    if unit in ('a00-write-whole', 'a10-expressions-equations', 'a10-exponents'):
        assert sha((LANG / f'translation/{unit}.edits.json').read_bytes()) == rules['scope']['edits_sha256']
        assert sha((LANG / 'translation/phrases.json').read_bytes()) == rules['scope']['shared_edits_sha256']
    edits = merged_edits(unit)
    source_nodes = {node.get('id'): node for node in source_root.iter() if node.get('id')}
    target_nodes = {node.get('id'): node for node in root.iter() if node.get('id')}

    def check_target(anchor):
        source_node = source_nodes[anchor]
        expected = source_node if track == 'id-academic' else translated(source_node, track, edits)
        if track != 'id-academic' and XML_LANG not in source_node.attrib:
            expected.attrib.pop(XML_LANG)
        assert tree_key(target_nodes[anchor]) == tree_key(expected), 'Unregistered target fixture text/structure'

    fixture_groups = [('table_fixtures', 'table_id'), ('prose_fixtures', 'element_id')]
    if unit == 'a10-exponents':
        fixture_groups.append(('reference_fixtures', 'element_id'))
    for key, id_key in fixture_groups:
        fixtures = rules.get(key, [])
        assert len({row[id_key] for row in fixtures}) == len(fixtures), 'Duplicate nonmath fixture'
        for fixture in fixtures:
            anchor = fixture[id_key]
            expected = ET.fromstring(f'<wrapper xmlns="{CN}" xmlns:m="{MATH}">{fixture["source_cnxml"]}</wrapper>')[0]
            assert tree_key(source_nodes[anchor]) == tree_key(expected), 'Unregistered source CNXML fixture'
            check_target(anchor)
            if 'expected_target_tree_sha256' in fixture:
                assert sha(tree_key(target_nodes[anchor]).encode()) == fixture['expected_target_tree_sha256'][track], 'Unregistered target table hash'
                for attribute, value in fixture['target_linguistic_attributes'][track].items():
                    assert target_nodes[anchor].get(attribute) == value, 'Unregistered target table label'
    if unit in ('a00-write-whole', 'a10-expressions-equations', 'a10-exponents'):
        assert {node.get('id') for node in source_root.iter('{' + CN + '}table')} == {row['table_id'] for row in rules['table_fixtures']}
    charts = rules.get('chart_fixtures', [])
    assert len({row['media_id'] for row in charts}) == len(charts), 'Duplicate chart fixture'
    assert {node.get('id') for node in source_root.iter('{' + CN + '}media')} == {row['media_id'] for row in charts}
    for chart in charts:
        anchor = chart['media_id']
        source_media = source_nodes[anchor]
        assert source_media.get('alt') == chart['source_alt'], 'Unregistered chart alt'
        assert source_media.find('{*}image').get('src') == chart['source_image'], 'Unregistered chart image'
        check_target(anchor)
        if 'source_cnxml' in chart:
            expected = ET.fromstring(f'<wrapper xmlns="{CN}" xmlns:m="{MATH}">{chart["source_cnxml"]}</wrapper>')[0]
            assert tree_key(source_media) == tree_key(expected), 'Unregistered source media tree'
        if 'expected_target_tree_sha256' in chart:
            assert sha(tree_key(target_nodes[anchor]).encode()) == chart['expected_target_tree_sha256'][track], 'Unregistered target media tree'
            assert target_nodes[anchor].get('alt') == chart['expected_target_alt'][track]


def narrate(element, track, unit, bound, rules=None):
    if unit == 'a00-rounding':
        from rounding_checks import narrate as rounding_narrate
        return rounding_narrate(element, track, bound, rules)
    if unit == 'a10-exponents':
        registered = getattr(bound, 'narration_nodes', {}).get(id(element))
        if (not isinstance(bound, BoundMath) or registered is None
                or registered[0] is not element or registered[1] != tree_key(element)
                or getattr(bound, 'narration_track', None) != track
                or getattr(bound, 'narration_rules', None) != sha(json.dumps(rules, sort_keys=True).encode())):
            raise ValueError('unsupported_source_bound_exponent_context')
    tag = local(element)
    is_jv = track.startswith('jv')
    if unit == 'a00-write-whole' and element.get('id') == 'fs-id2880619':
        # This is an inline reference to part b, not a new list item label.
        assert len(element) == 1 and local(element[0]) == 'span'
        assert element[0].get('class') == 'token' and element[0].text == 'ⓑ'
        prefix = speech_text(element.text, track, unit)
        assert prefix.rstrip().endswith('bagean' if is_jv else 'bagian')
        return prefix + 'be' + speech_text(element[0].tail, track, unit)
    if unit in ('a00-name-whole', 'a00-write-whole', 'a10-exponents'):
        fixture = next((row for row in rules['prose_fixtures']
                        if row['element_id'] == element.get('id')), None)
        if fixture is not None:
            return fixture['expected'][track]
    if element.tag == '{' + MATH + '}math':
        if unit in ('a00-write-whole', 'a10-exponents') and (not isinstance(bound, BoundMath) or id(element) not in bound):
            raise ValueError('unsupported_source_bound_narration')
        if id(element) in getattr(bound, 'prose_only', set()):
            raise ValueError('unsupported_currency_or_unit_context')
        if bound:
            return bound[id(element)]
        temporary = copy.deepcopy(element)
        for text in temporary.iter('{' + MATH + '}mtext'):
            text.text = speech_text(text.text, track, unit)
        return speak_math(temporary, is_jv)
    if tag == 'media':
        if unit in ('a00-digit-place', 'a00-name-whole', 'a00-write-whole', 'a10-exponents'):
            fixture = next((row for row in rules['chart_fixtures']
                            if row['media_id'] == element.get('id')), None)
            if fixture is None:
                raise ValueError('Unregistered place-value chart narration')
            return fixture['expected'][track]
        if unit == 'a10-equality-symbols':
            fixture = next((row for row in rules.get('diagram_rules', [])
                            if row.get('source_media') == element.get('id')), None)
            if fixture is None:
                raise ValueError('Unregistered equality diagram narration')
            return fixture['expected'][track]
        return speech_text(element.get('alt', ''), track, unit)
    if tag == 'image':
        return ''
    if tag == 'newline':
        return '\n'
    if tag == 'link':
        if unit == 'a10-exponents':
            fixture = rules['reference_fixtures'][0]
            if element.get('target-id') != fixture['target_id']:
                raise ValueError('Unregistered exponent table reference')
            return fixture['expected'][track]
        references = {
            'CNX_BMath_Figure_01_01_002': 'gambar dhuwit kertas' if is_jv else 'gambar uang kertas',
            'CNX_BMath_Figure_01_01_004': 'gambar wujud blok basis sepuluh' if is_jv else 'gambar bentuk blok basis sepuluh',
            'CNX_BMath_Figure_01_01_005': 'gambar model wilangan satus telung puluh wolu' if is_jv else 'gambar model bilangan seratus tiga puluh delapan',
            'CNX_BMath_Figure_01_01_011': 'gambar tabel nilai panggonan' if is_jv else 'gambar tabel nilai tempat',
            'fs-id1170655178120': 'tabel pertidaksamaan' if is_jv else 'tabel pertidaksamaan',
        }
        if element.get('target-id') not in references:
            raise ValueError('Unregistered spoken source reference')
        return references[element.get('target-id')]
    if tag == 'table':
        if unit in ('a00-name-whole', 'a10-expressions-equations', 'a10-exponents'):
            fixture = next((row for row in rules['table_fixtures']
                            if row['table_id'] == element.get('id')), None)
            if fixture is None:
                raise ValueError('Unregistered fixed table narration')
            return fixture['expected'][track] + '\n'
        headers = element.findall('.//{*}thead/{*}row/{*}entry')
        rows = []
        for row in element.findall('.//{*}tbody/{*}row'):
            assert len(row) == len(headers), 'Unexpected table shape'
            cells = []
            for header, cell in zip(headers, row):
                if not ''.join(cell.itertext()).strip():
                    continue
                label = narrate(header, track, unit, bound, rules).strip().rstrip(':')
                cells.append(label + ': ' + narrate(cell, track, unit, bound, rules).strip())
            rows.append('; '.join(cells))
        return 'Tabel.\n' + '\n'.join(rows) + '\n'
    if tag == 'emphasis':
        value = (element.text or '').strip()
        if value in ('a', 'b', 'x', 'y'):
            return ('aksara ' if is_jv else 'huruf ') + {'a':'a', 'b':'be', 'x':'eks', 'y':'ye'}[value]
        if value == 'xy' and unit == 'a10-operation-symbols':
            return {'jv-academic':' diterusake aksara eks lan aksara ye sing ditulis jejer tanpa tandha ing antarane',
                    'jv-conversation':', banjur aksara eks lan aksara ye sing ditulis jejer tanpa tandha ing antarane',
                    'id-academic':' diikuti huruf eks dan huruf ye yang ditulis bersebelahan tanpa tanda di antaranya'}[track]
    result = speech_text(element.text, track, unit)
    if tag == 'solution' and element.find('{*}title') is None:
        result = ('Wangsulan.\n' if is_jv else 'Jawaban.\n') + result
    for child in element:
        if local(child) == 'emphasis' and (child.text or '').strip() == 'xy':
            assert element.get('id') == 'fs-id1170655004454' and result.rstrip().endswith(number('3', is_jv)), 'Unregistered prose juxtaposition'
        result += narrate(child, track, unit, bound, rules) + speech_text(child.tail, track, unit)
        if local(child) in ('para', 'title', 'equation', 'item', 'solution', 'problem'):
            result += '\n'
    return result


def blocks(root, track, unit, rules, source_root=None):
    source_root = source_root if source_root is not None else root
    if unit == 'a00-section-exercises':
        from section_exercise_checks import blocks as exercise_blocks
        return exercise_blocks(root,track,rules,source_root)
    bound = source_bound_math(root, rules, track, source_root) if rules else {}
    if unit == 'a00-rounding':
        return [('fs-id2472737--title' if index == 0 else node.get('id'),
                 narrate(node, track, unit, bound, rules)) for index, node in enumerate(root)]
    validate_nonmath_fixtures(root, source_root, unit, rules, track)
    if unit == 'a10-exponents':
        from exponent_checks import validate_semantics
        validate_semantics(source_root, root, rules, track, bound)
    result = []
    for element in root:
        body = re.sub(r'[ \t]+', ' ', narrate(element, track, unit, bound, rules)).strip()
        anchor = element.get('id', 'title')
        if anchor == 'fs-id1170655004454':
            glyph = next(row for row in rules['math_fixtures'] if row['id'] == 'A10-OPS-M08')['expected'][track]
            combined = next(row for row in rules['prose_symbol_fixtures'] if row['id'] == 'A10-OPS-P03')['expected_combined_prefix_and_glyph'][track]
            prefix = speech_text(element.text, track, unit).strip()
            body, count = re.subn(re.escape(prefix) + r'\s*' + re.escape(glyph), lambda _: combined, body, count=1)
            assert count == 1, 'Cross-name composition no longer matches source'
        if anchor == 'fs-id1862565':
            # Source has a sentence period inside the final 5 MathML before "berbeda".
            # Preserve it visibly, but move no facts when suppressing this spoken pause.
            suffix = 'beda' if track.startswith('jv') else 'berbeda'
            body, count = re.subn(r'\blima\s*\.\s*' + suffix + r'\.', 'lima ' + suffix + '.', body)
            assert count == 1, 'Source-punctuation narration correction no longer matches'
        if unit == 'a10-equality-symbols' and anchor == 'fs-id1170655025665':
            duplicated, replacement = {
                'jv-conversation': ('Tandha tandha padha karo', 'Tandha padha karo'),
                'jv-academic': ('Simbol tandha padha karo', 'Simbol padha karo'),
                'id-academic': ('Simbol tanda sama dengan', 'Simbol sama dengan'),
            }[track]
            body, count = body.replace(duplicated, replacement), body.count(duplicated)
            assert count == 1, 'Equality-glyph naming composition no longer matches'
        if unit == 'a10-equality-symbols' and anchor in ('fs-id1170655155145', 'fs-id1170655178120'):
            a_name = 'aksara a' if track.startswith('jv') else 'huruf a'
            b_name = 'aksara be' if track.startswith('jv') else 'huruf be'
            body = re.sub(r'(?<!aksara )(?<!huruf )\ba\b', a_name, body)
            body = re.sub(r'\bb\b', b_name, body)
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = '\n'.join(line.rstrip() for line in body.split('\n'))
        if not body:
            assert anchor in NONSPOKEN_BLOCKS.get(unit, []), 'Unexpected empty narration block'
            # Preserve this spacing-only source node in CNXML/HTML, but do not
            # fabricate speech or an empty SSML paragraph for layout whitespace.
            continue
        result.append((anchor, body))
    return result


def validate_expression_answers(source, variants, rules):
    fixtures = {row['id']: row for row in rules['math_fixtures']}
    checks = rules['classification_checks']
    assert len(checks) == 8 and len({row['question_fixture'] for row in checks}) == 8
    assert [row['expected_classification'] for row in checks] == [
        'equation', 'expression', 'expression', 'equation',
        'equation', 'expression', 'expression', 'equation']
    for check in checks:
        question = fixtures[check['question_fixture']]
        expression = fixture_element(question['source_mathml'])
        classification = 'equation' if any(node.text == '=' for node in expression.iter('{' + MATH + '}mo')) else 'expression'
        assert check['expected_classification'] == classification, 'Classification differs from source equals sign'
        for reading in question['expected'].values():
            assert not any(word in reading.lower() for word in ('ekspresi', 'persamaan', 'wujud aljabar', 'wangsulan', 'jawaban')), 'Question math leaks classification'
        if 'answer_fixture' in check:
            answer = fixture_element(fixtures[check['answer_fixture']]['source_mathml'])
            assert [(node.tag, node.text) for node in expression.iter() if len(node) == 0] == [
                (node.tag, node.text) for node in answer.iter() if len(node) == 0], 'Answer repeats different mathematical operands'
    for track, root in variants.items():
        labels = rules['answer_policy']['expected_answer_labels'][track]
        nodes = {node.get('id'): node for node in root.iter() if node.get('id')}
        answer_table = nodes['eip-10']
        assert [node.text for node in answer_table.findall('.//{*}tbody/{*}row/{*}entry/{*}emphasis')] == [
            labels[row['expected_classification']] for row in checks[:4]], 'Worked classification changed'
        for anchor, sequence in rules['answer_policy']['practice_answer_sequences'].items():
            assert [(node.tail or '').strip() for node in nodes[anchor].findall('{*}span')] == [labels[value] for value in sequence], 'Practice classification changed'


def products(unit):
    for path, raw in draft_products(unit).items():
        assert (LANG / path).read_bytes() == raw, f'Stale source-bound draft: {path}'
    descriptor = UNITS[unit]
    rules_path = LANG / f'audio/{unit}.rules.json'
    rules = json.loads(rules_path.read_text(encoding='utf-8')) if rules_path.exists() else None
    if unit != 'a00-place-value':
        assert rules is not None, 'Missing required source-bound narration rules'
        assert rules['scope']['module'] == descriptor['module']
    asset_path = LANG / f'translation/{unit}.assets.json'
    assets = json.loads(asset_path.read_text(encoding='utf-8'))['assets'] if asset_path.exists() else []
    variants, media = {}, {}
    for track in TRACKS:
        variants[track] = ET.parse(LANG / f'translation/{unit}.{track}.cnxml').getroot()
        media[track] = {}
        for asset in assets:
            output = asset['outputs'][track]
            raw = (LANG / output['path']).read_bytes()
            assert sha(raw) == output['sha256']
            media[track][asset['source_src']] = {'bytes':raw, 'mime_type':output.get('mime_type', asset['mime_type'])}
    source = variants['id-academic']
    if unit == 'a10-expressions-equations':
        validate_expression_answers(source, variants, rules)
    if unit == 'a00-write-whole':
        from writing_checks import validate_values
        validate_values(source, variants, rules)
    if rules:
        for fixture in rules.get('chart_fixtures', []) + rules.get('diagram_rules', []):
            media_id = fixture.get('media_id', fixture.get('source_media'))
            if media_id is None:
                continue
            source_media = next(node for node in source.iter() if node.get('id') == media_id)
            assert source_media.get('alt') == fixture['source_alt'], 'Source media alt changed'
            if fixture.get('source_image'):
                assert source_media.find('{*}image').get('src') == fixture['source_image']
    if unit in ('a00-digit-place', 'a00-name-whole', 'a00-write-whole'):
        for witness in rules['number_decomposition_witnesses']:
            assert re.fullmatch(r'\d{1,3}(?:,\d{3})+', witness['source'])
            assert witness['source'].split(',') == witness['groups_from_left']
            assert sum(int(group) * int(scale) for group, scale in
                       zip(witness['groups_from_left'], witness['group_scales'])) == int(witness['fixed_value'])
            assert int(witness['source'].replace(',', '')) == int(witness['fixed_value'])
    if unit == 'a00-digit-place':
        for invariant in rules['answer_position_invariants']:
            block = next(node for node in source if node.get('id') == invariant['anchor'])
            problem = block.find('.//{*}problem')
            assert problem.find('.//{' + MATH + '}mn').text == invariant['number']
            digits = [node.text for node in problem.find('{*}list').iter('{' + MATH + '}mn')]
            assert digits == invariant['ordered_digits']
            whole = int(invariant['number'].replace(',', ''))
            assert [str((whole // (10 ** power)) % 10) for power in
                    invariant['places_as_powers_of_ten']] == digits
            for track, root in variants.items():
                target_block = next(node for node in root if node.get('id') == invariant['anchor'])
                answers = target_block.findall('.//{*}solution/{*}list/{*}item')
                assert len(answers) == len(digits)
                for item, label in zip(answers, invariant['expected_place_labels'][track]):
                    assert ''.join(item.itertext()).strip().rstrip('.').endswith(label)
        for chart in rules['chart_fixtures']:
            assert ''.join(cell['digit'] for cell in chart['digit_cells']) == chart['whole_number'].replace(',', '')
            assert chart['blank_columns'] + [cell['column'] for cell in chart['digit_cells']] == list(range(1, 16))
    if unit == 'a00-name-whole':
        witnesses = {row['source']: row for row in rules['number_decomposition_witnesses']}
        assert len(witnesses) == 7
        for fixture in rules['math_fixtures']:
            token = fixture_element(fixture['source_mathml']).find('.//{' + MATH + '}mn').text
            assert token == fixture['source_value']
            expected = (witnesses[token]['expected_cardinal'] if token in witnesses
                        else rules['year_witness']['expected'])
            if token not in witnesses:
                assert token == rules['year_witness']['source'] == '2014'
            for track in TRACKS:
                if token in witnesses:
                    assert fixture['expected_cardinal'][track] == expected[track]
                    is_jv = track.startswith('jv')
                    prefix = 'digit saka kiwa menyang tengen: ' if is_jv else 'digit dari kiri ke kanan: '
                    separator = '; tandha koma; ' if is_jv else '; tanda koma; '
                    printed = separator.join(', '.join(number(digit, is_jv) for digit in group)
                                             for group in witnesses[token]['groups_from_left'])
                    punctuation = '.' if fixture_element(fixture['source_mathml']).find('.//{' + MATH + '}mo') is not None else ''
                    assert fixture['expected'][track] == prefix + printed + punctuation
                else:
                    assert fixture['expected'][track] == expected[track]
        for invariant in rules['answer_value_invariants']:
            block = next(node for node in source if node.get('id') == invariant['anchor'])
            assert block.find('.//{*}problem//{' + MATH + '}mn').text == invariant['number']
            for track, root in variants.items():
                answer = next(node for node in root.iter() if node.get('id') == invariant['answer_paragraph'])
                assert ''.join(answer.itertext()).strip() == invariant['expected_visible_answer'][track]
                assert invariant['expected_cardinal'][track] == witnesses[invariant['number']]['expected_cardinal'][track]
        for fixture in rules['table_fixtures']:
            table = next(node for node in source.iter() if node.get('id') == fixture['table_id'])
            rows = table.findall('.//{*}tbody/{*}row')
            assert table.find('{*}tgroup').get('cols') == '3' and len(rows) == 5
            assert table.find('.//{*}thead') is None and all(len(row) == 2 for row in rows)
            assert table.get('aria-label') == fixture['source_aria_label']
            assert [[''.join(cell.itertext()).strip() for cell in row] for row in rows] == fixture['source_rows']
            assert [str(int(group) * int(scale)) for group, scale in
                    zip(fixture['groups_from_left'], fixture['group_scales'])] == fixture['row_values']
            assert sum(map(int, fixture['row_values'])) == int(fixture['whole_number'].replace(',', ''))
        for chart in rules['chart_fixtures']:
            assert chart['groups_from_left'] == chart['whole_number'].split(',')
            assert sum(int(group) * int(scale) for group, scale in
                       zip(chart['groups_from_left'], chart['group_scales'])) == int(chart['whole_number'].replace(',', ''))
            for track in TRACKS:
                expected_digits = [', '.join(number(digit, track.startswith('jv')) for digit in group)
                                   for group in chart['groups_from_left']]
                assert chart['printed_digit_readings'][track] == expected_digits
                assert all(reading in chart['expected'][track] for reading in expected_digits)
    if unit == 'a00-place-value':
        for table, expected_total in zip(source.findall('.//{*}table'), (138, 215)):
            rows = table.findall('.//{*}tbody/{*}row')
            assert len(rows) == 4
            values = []
            for row in rows[:3]:
                digit = int(row[0].find('.//{' + MATH + '}mn').text)
                unit_value = int(row[3].find('.//{' + MATH + '}mn').text)
                subtotal = int(row[4].find('.//{' + MATH + '}mn').text)
                assert digit * unit_value == subtotal
                values.append(subtotal)
            total = int(rows[3][4].find('.//{' + MATH + '}mn').text)
            assert total == sum(values) == expected_total
        answers = [int(''.join(note.find('.//{*}solution').itertext()).strip())
                   for note in source.findall('{*}note') if note.get('class') == 'try']
        assert answers == [1*100 + 7*10 + 6, 2*100 + 3*10 + 7]
        assert 3*100 + 7*10 + 4 == 374
    pieces = ['<!DOCTYPE html><html lang="id-ID"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              '<title>' + html.escape(unit) + '</title><style>' + STYLE + '</style></head><body><main>',
              '<header><div class="eyebrow">' + descriptor['program'] + ' · jv-Latn-ID / id-ID</div>',
              '<h1 lang="jv-Latn-ID">' + html.escape(rules['reader_frame']['proposed_editorial_labels']['jv-academic'] if unit == 'a00-section-exercises' else variants['jv-academic'].findtext('{*}title')) + '</h1>',
              '<p class="source" lang="en">' + html.escape(descriptor['scope']) + '</p>',
              '<p class="status">Draf tiga register. Belum ditelaah penutur/pendidik Jawa atau diuji dengar; bukan edisi siap terbit.</p>',
              '<p><a href="../pilot.html">Unit awal</a> · <a href="../../NEXT_UNIT.md">Kelanjutan</a></p></header>']
    for track in TRACKS:
        pieces.append(f'<span id="{unit}--{track}--{source.get("id")}" data-source-id="{source.get("id")}"></span>')
    if unit == 'a00-rounding':
        from rounding_checks import ID_NOTE
        pieces.append('<aside class="note-box" lang="id-ID"><p>' + html.escape(ID_NOTE) + '</p><p>Pranala luar asli dipertahankan; isi tujuannya tidak disertakan dalam pembaca luring ini.</p></aside>')
    for index in range(0 if unit == 'a00-section-exercises' else 1, len(source)):
        pieces.append('<div class="parallel">')
        for track, (locale, label) in TRACKS.items():
            pieces.append(f'<article class="track" lang="{locale}" data-register="{track}"><div class="register">{label}</div>' + render(variants[track][index], unit + '--' + track + '--', media[track]) + '</article>')
        pieces.append('</div>')
    pieces.append('<section class="note-box"><h2>Naskah audio</h2><ul>')
    generated = {}
    for track, (locale, label) in TRACKS.items():
        narration = blocks(variants[track], track, unit, rules, source)
        for _, body in narration:
            assert body and '$' not in body and '=' not in body, 'Unspoken currency or equality symbol'
        if unit in ('a00-place-value', 'a00-name-whole', 'a00-write-whole'):
            answer_count = 2 if unit == 'a00-place-value' else 4
            assert sum(body.count('Wangsulan.') if track.startswith('jv') else body.count('Jawaban.') for _, body in narration) == answer_count
            assert 'gambar garis wilangan' not in '\n'.join(body for _, body in narration)
            if unit == 'a00-write-whole':
                from writing_checks import validate_readout
                validate_readout(narration, rules, track)
        elif unit == 'a10-operation-symbols':
            assert all('sateruse' not in body and 'seterusnya' not in body for _, body in narration)
        elif unit == 'a10-expressions-equations':
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            assert sum(body.count(cue) for _, body in narration) == 2
            for fixture in rules['table_fixtures']:
                assert sum(body.count(fixture['expected'][track]) for _, body in narration) == 1, 'Duplicated or absent table readout'
        elif unit == 'a10-exponents':
            from exponent_checks import validate_readout
            validate_readout(narration, rules, track)
        elif unit == 'a00-rounding':
            from rounding_checks import validate_readout
            validate_readout(narration, rules, track)
        transcript = '# ' + label + '\n\nStatus: narration draft; not synthesized or listening-reviewed.\n\n'
        if unit == 'a00-rounding' and track == 'id-academic':
            transcript += ID_NOTE + '\n\n'
        transcript += '\n\n'.join(f'## {descriptor["module"]}--{anchor}\n\n{body}' for anchor, body in narration) + '\n'
        stem = f'review/audio/{unit}.{track}'
        generated[stem + '.md'] = transcript.encode()
        ssml = f'<?xml version="1.0" encoding="UTF-8"?>\n<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}"><p>{html.escape(label)}</p>\n'
        if unit == 'a00-rounding' and track == 'id-academic':
            ssml += '<p>' + html.escape(ID_NOTE) + '</p>\n'
        ssml += ''.join(f'<mark name="{descriptor["module"]}--{anchor}"/><p>{html.escape(body)}</p><break time="600ms"/>\n' for anchor, body in narration)
        ssml += '</speak>\n'
        parsed = ET.fromstring(ssml)
        assert parsed.get(XML_LANG) == locale
        assert [node.get('name') for node in parsed.findall('{*}mark')] == [descriptor['module'] + '--' + anchor for anchor, _ in narration]
        generated[stem + '.ssml'] = ssml.encode()
        pieces.append(f'<li><span lang="{locale}">{label}</span>: <a href="../audio/{unit}.{track}.md">Naskah</a> / <a href="../audio/{unit}.{track}.ssml">SSML</a></li>')
    pieces.append('</ul></section><footer lang="en"><p>Unofficial AI-assisted adaptation of OpenStax through the Indonesian editions by KokunoYumeto. Rice University/OpenStax, CC BY-NC-SA 4.0, subject to inherited component notices. No endorsement. <a href="../../ATTRIBUTION.md">Full attribution and original notices</a>.</p><p>US dollars, source mathematical notation, IDs and quantities are preserved. Native-language, visual, screen-reader and listening review remain pending.</p></footer></main></body></html>')
    page = '\n'.join(pieces)
    inspection = Reader()
    inspection.feed(page)
    assert len(inspection.ids) == len(set(inspection.ids))
    assert inspection.maths == 3 * len(list(source.iter('{' + MATH + '}math')))
    assert len(inspection.images) == 3 * len(assets)
    assert all(image.get('alt') and image['src'].startswith('data:image/') for image in inspection.images)
    expected_headers = 3 * len(source.findall('.//{*}thead/{*}row/{*}entry'))
    assert len(inspection.heads) == expected_headers and all(header.get('scope') == 'col' for header in inspection.heads)
    for track in TRACKS:
        assert all(unit + '--' + track + '--' + node.get('id') in inspection.ids for node in source.iter() if node.get('id'))
    for link in inspection.links:
        if link.startswith('#'):
            assert link[1:] in inspection.ids
        else:
            if re.match(r'https?://', link):
                assert unit == 'a00-rounding' and link in [n.get('url') for n in source.iter() if local(n) == 'link' and n.get('url')]
                continue
            resolved = (LANG / 'review/units' / link).resolve()
            assert resolved.is_file() or resolved.relative_to(LANG).as_posix() in generated
    generated[f'review/units/{unit}.html'] = page.encode()
    reported_checks = ['source_bound_draft_replay', 'asset_hashes', 'unique_complete_source_ids',
                       'math_count', 'embedded_images_and_alts', 'offline_links',
                       'source_marked_localized_SSML', 'registered_narration_conventions']
    if unit == 'a00-place-value':
        reported_checks += ['place_value_table_arithmetic_and_answers', 'scoped_table_headers',
                            'context_bound_currency_and_figure_speech']
    elif unit == 'a10-operation-symbols':
        reported_checks += ['exact_source_tree_math_fixtures', 'long_division_operand_order',
                            'cross_variable_and_ellipsis_contexts']
    elif unit == 'a00-digit-place':
        reported_checks += ['exact_source_tree_math_fixtures', 'large_integer_decomposition',
                            'all_fifteen_digit_place_answers', 'blank_cells_distinct_from_zero']
    elif unit == 'a00-name-whole':
        reported_checks += ['exact_source_tree_math_fixtures', 'large_integer_decomposition',
                            'four_exact_practice_answers', 'source_bound_headerless_table_and_quoted_prose',
                            'printed_digit_groups_preserve_leading_zeroes', 'four_explicit_answer_cues']
    elif unit == 'a10-equality-symbols':
        reported_checks += ['exact_source_tree_math_fixtures', 'translated_linguistic_mtext_only',
                            'relation_diagram_and_plain_notation_readings', 'spacing_source_node_preserved']
    elif unit == 'a00-write-whole':
        reported_checks += ['exact_source_tree_math_fixtures', 'whole_source_and_target_prose_chart_binding',
                            'seven_literal_digit_answers_and_leading_zeroes', 'three_quantity_invariants',
                            'required_full_currency_and_weight_contexts', 'four_solution_cues_without_answer_leakage',
                            'word_blocks_distinct_from_zero_digit_groups']
    elif unit == 'a10-grouping-symbols':
        reported_checks += ['exact_source_tree_math_fixtures', 'translated_linguistic_mtext_only',
                            'three_grouping_symbol_types_and_nested_examples', 'spacing_source_node_preserved']
    elif unit == 'a10-expressions-equations':
        reported_checks += ['exact_source_tree_math_fixtures', 'three_source_bound_table_readouts',
                            'translated_source_summary', 'explicit_fraction_power_and_implicit_products',
                            'eight_source_classifications_and_two_answer_cues']
    elif unit == 'a10-exponents':
        reported_checks += ['whole_source_and_target_fixture_binding', '32_exact_math_readings',
                            'positive_integer_domain_and_seven_prose_only_math_contexts',
                            'two_complete_table_readouts_and_real_reference',
                            'finite_factor_pattern_and_mixed_asset_mime',
                            'five_source_results_and_two_answer_cues_without_leakage']
    elif unit == 'a00-rounding':
        reported_checks += ['complete_source_target_slot_and_finite_contract_binding',
                            '69_exact_math_readings_and_11_context_only_formulas',
                            '23_source_bound_media_and_five_headerless_tables',
                            '17_half_up_cases_and_carry_zero_positions',
                            'nine_source_question_solution_boundaries_six_editorial_cues',
                            'three_figure_links_four_ordered_step_cues',
                            'unchanged_external_links_not_fetched_or_bundled',
                            'indonesian_editorial_diagram_discrepancy_notice']
    receipt = {'schema':'jv-unit-build-v1', 'unit':unit, 'status':'structural_pass_human_review_pending',
               'source_draft_receipt_sha256':sha((LANG / f'qa/{unit}.draft-receipt.json').read_bytes()),
               'source_ids':len([node for node in source.iter() if node.get('id')]),
               'source_math_expressions':len(list(source.iter('{' + MATH + '}math'))),
               'source_media_references':len(assets), 'register_tracks':3, 'ssml_files':3,
               'source_bound_math_fixtures':len(rules['math_fixtures']) if rules else 0,
               'rules_sha256':sha(rules_path.read_bytes()) if rules else None,
               'asset_manifest_sha256':sha(asset_path.read_bytes()) if assets else None,
               'human_language_review':False, 'visual_review':False, 'listening_review':False,
               'nonspoken_source_blocks':NONSPOKEN_BLOCKS.get(unit, []),
               'synthesized_audio_files':0, 'whole_module_complete':False,
               'checks':reported_checks,
               'output_sha256':{path:sha(raw) for path, raw in generated.items()}}
    generated[f'qa/{unit}.build-receipt.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit', required=True, choices=UNITS)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products(args.unit)
    assert generated == products(args.unit), 'Nondeterministic unit generation'
    for path, raw in generated.items():
        if args.check:
            assert (LANG / path).read_bytes() == raw, f'Stale unit output: {path}'
        else:
            write_bytes(LANG / path, raw)
    print(f'{args.unit}: offline three-track reader, 3 transcripts and 3 SSML files verified; human reviews pending.')


if __name__ == '__main__':
    main()
