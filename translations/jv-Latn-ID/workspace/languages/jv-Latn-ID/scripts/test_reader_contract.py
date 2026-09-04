"""Shared reader semantics and mathematical-text integrity regressions."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from build import CN, MATH, XML_LANG, render, translated
from build_units import fixture_element, narration_tree_key, source_bound_math
from config import LANG
from draft_units import validate


class ReaderContract(unittest.TestCase):
    def test_list_types_and_numbering(self):
        for style, marker in [('arabic', '1'), ('lower-alpha', 'a'), ('upper-alpha', 'A'),
                              ('lower-roman', 'i'), ('upper-roman', 'I')]:
            node = ET.fromstring(f'<list xmlns="{CN}" id="steps" list-type="enumerated" number-style="{style}"><item>one</item><item>two</item></list>')
            page = render(node, 'test--', {})
            self.assertTrue(page.startswith('<ol '))
            self.assertIn(f'type="{marker}"', page)
            self.assertEqual(page.count('<li>'), 2)
            self.assertLess(page.index('one'), page.index('two'))
        for kind in ('bulleted', 'labeled-item'):
            page = render(ET.fromstring(f'<list xmlns="{CN}" list-type="{kind}"><item>ⓐ one</item></list>'), '', {})
            self.assertTrue(page.startswith('<ul '))
            self.assertEqual('source-labeled-list' in page, kind == 'labeled-item')

    def test_unknown_list_semantics_rejected(self):
        for attrs in ('list-type="mystery"', 'list-type="enumerated" number-style="mystery"'):
            with self.assertRaises(ValueError):
                render(ET.fromstring(f'<list xmlns="{CN}" {attrs}><item>one</item></list>'), '', {})

    def test_summary_translation_is_required_and_exposed(self):
        node = ET.fromstring(f'<table xmlns="{CN}" id="t" summary="Tabel contoh"><tgroup cols="1"><tbody><row><entry>1</entry></row></tbody></tgroup></table>')
        edits = {'tracks': ['jv-academic'], 'phrases': [['Tabel contoh', 'Tabel tuladha']], 'unchanged_identifiers': []}
        target = translated(node, 'jv-academic', edits)
        self.assertEqual(target.get('summary'), 'Tabel tuladha')
        page = render(target, 'test--', {})
        self.assertIn('aria-label="Tabel tuladha"', page)
        self.assertNotIn('<th', page)
        with self.assertRaises(ValueError):
            translated(node, 'jv-academic', {**edits, 'phrases': []})
        target.set('aria-label', 'Explicit label')
        self.assertIn('aria-label="Explicit label"', render(target, '', {}))

    def test_nonlinguistic_mtext_cannot_change_currency(self):
        source = ET.fromstring(f'<section xmlns="{CN}" xmlns:m="{MATH}" id="s"><para id="p"><m:math><m:mtext>$77</m:mtext></m:math></para></section>')
        changed = copy.deepcopy(source)
        changed.set(XML_LANG, 'jv-Latn-ID')
        changed.find('.//{' + MATH + '}mtext').text = '€77'
        with self.assertRaisesRegex(AssertionError, 'Nonlinguistic mtext'):
            validate(source, changed)
        left = source.find('.//{' + MATH + '}math')
        right = changed.find('.//{' + MATH + '}math')
        self.assertNotEqual(narration_tree_key(left), narration_tree_key(right))
        rules = {'scope': {'module': 'm81243', 'section': 'fs-id1321580'},
                 'math_fixtures': [{'anchor': 'p', 'math_ordinal': 1,
                                    'source_mathml': ET.tostring(left, encoding='unicode'),
                                    'expected': {'jv-academic': 'dollar fixture'}}]}
        with self.assertRaisesRegex(ValueError, 'unsupported_translated_math'):
            source_bound_math(changed, rules, 'jv-academic', source)

    def test_linguistic_mtext_requires_exact_registered_translation(self):
        source = ET.parse(LANG / 'translation/a10-grouping-symbols.id-academic.cnxml').getroot()
        target = ET.parse(LANG / 'translation/a10-grouping-symbols.jv-academic.cnxml').getroot()
        rules = json.loads((LANG / 'audio/a10-grouping-symbols.rules.json').read_text(encoding='utf-8'))
        self.assertEqual(len(source_bound_math(target, rules, 'jv-academic', source)), 2)
        target.find('.//{' + MATH + '}mtext').text = 'unregistered words'
        with self.assertRaisesRegex(ValueError, 'unsupported_translated_math'):
            source_bound_math(target, rules, 'jv-academic', source)

    def test_actual_howto_is_ordered_in_rebuilt_reader(self):
        page = (LANG / 'review/units/a00-name-whole.html').read_text(encoding='utf-8')
        for track in ('jv-academic', 'jv-conversation', 'id-academic'):
            self.assertIn(f'<ol id="a00-name-whole--{track}--eip-375"', page)

    def test_explicit_circled_parts_do_not_gain_duplicate_native_markers(self):
        source = ET.parse(LANG / 'translation/a00-digit-place.id-academic.cnxml').getroot()
        for anchor in ('fs-id2218367', 'fs-id1386307', 'fs-id1508784'):
            node = next(node for node in source.iter() if node.get('id') == anchor)
            self.assertEqual(node.get('class'), 'circled')
            page = render(node, 'test--', {})
            opening = page.split('>', 1)[0]
            self.assertTrue(opening.startswith('<ol '))
            self.assertIn('type="a"', opening)
            self.assertIn('class="source-labeled-list"', opening)
            self.assertEqual(page.count('ⓐ'), 1)
            self.assertEqual(page.count('ⓑ'), 1)
        saved = (LANG / 'review/units/a00-digit-place.html').read_text(encoding='utf-8')
        for track in ('jv-academic', 'jv-conversation', 'id-academic'):
            for anchor in ('fs-id2218367', 'fs-id1386307', 'fs-id1508784'):
                opening = saved.split(f'<ol id="a00-digit-place--{track}--{anchor}"', 1)[1].split('>', 1)[0]
                self.assertIn('class="source-labeled-list"', opening)


if __name__ == '__main__':
    unittest.main()
