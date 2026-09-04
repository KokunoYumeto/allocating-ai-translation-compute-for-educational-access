"""Adversarial validation checks; write-failure tests use isolated temporary files."""
import copy
import errno
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from config import LANG
from build import MATH, translated, number, render, speak, speak_math, spoken_text
from qa import identity, math_structure
from safe_io import write_text


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.source = ET.parse(LANG / 'translation/a00-number-sense.id-academic.cnxml').getroot()

    def test_changed_id_is_detectable(self):
        changed = copy.deepcopy(self.source)
        changed.set('id', 'wrong-id')
        self.assertNotEqual(identity(changed), identity(self.source))

    def test_conversational_ellipsis_name_is_not_duplicated(self):
        spoken = spoken_text('Tandha “…” jenenge elipsis.', True)
        self.assertEqual(spoken, '“tandha telung titik” jenenge elipsis.')

    def test_changed_number_is_detectable(self):
        changed = copy.deepcopy(self.source)
        next(changed.iter('{' + MATH + '}mn')).text = '99'
        self.assertNotEqual(math_structure(changed), math_structure(self.source))

    def test_changed_operator_is_detectable(self):
        changed = copy.deepcopy(self.source)
        next(changed.iter('{' + MATH + '}mo')).text = '+'
        self.assertNotEqual(math_structure(changed), math_structure(self.source))

    def test_new_source_phrase_fails_closed(self):
        changed = copy.deepcopy(self.source)
        changed.find('{*}title').text = 'Unmapped new source heading'
        edits = json.loads((LANG / 'translation/phrases.json').read_text(encoding='utf-8'))
        with self.assertRaisesRegex(ValueError, 'Untranslated source text'):
            translated(changed, 'jv-academic', edits)

    def test_unregistered_figure_fails_closed(self):
        media = ET.fromstring('<media><image src="other.svg"/></media>')
        with self.assertRaisesRegex(ValueError, 'Unregistered media'):
            render(media, 'test--', '<svg/>')

    def test_unreviewed_narration_range_fails_closed(self):
        with self.assertRaises(ValueError):
            number('1000', True)

    def test_negative_number_does_not_index_cardinal_list(self):
        for value in ('-1', '−1', 'NaN', '1e2'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                number(value, True)

    def test_unsupported_math_structures_and_operators_fail_closed(self):
        for markup in ('<msup><mi>x</mi><mn>2</mn></msup>',
                       '<msub><mi>x</mi><mn>2</mn></msub>',
                       '<msqrt><mn>2</mn></msqrt>', '<mo>−</mo>', '<mo>×</mo>'):
            element = ET.fromstring(f'<math xmlns="{MATH}">{markup}</math>')
            for is_jv in (True, False):
                with self.subTest(markup=markup, is_jv=is_jv), self.assertRaisesRegex(ValueError, 'Unreviewed MathML'):
                    speak_math(element, is_jv)

    def test_malformed_fraction_is_rejected(self):
        for children in ('<mn>1</mn>', '<mn>1</mn><mn>2</mn><mn>3</mn>'):
            element = ET.fromstring(f'<mfrac xmlns="{MATH}">{children}</mfrac>')
            with self.subTest(children=children), self.assertRaisesRegex(ValueError, 'one numerator and one denominator'):
                speak_math(element, True)

    def test_untitled_solutions_have_spoken_answer_cues(self):
        solutions = self.source.findall('.//{*}solution')
        self.assertEqual(len(solutions), 3)
        for is_jv, cue in ((True, 'Wangsulan.'), (False, 'Jawaban.')):
            for solution in solutions:
                with self.subTest(is_jv=is_jv, solution=solution.get('id')):
                    actual = speak(solution, is_jv).strip()
                    self.assertEqual(actual.startswith(cue), solution.find('{*}title') is None)

    def test_failed_generated_write_preserves_previous_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'artifact.txt'
            write_text(target, 'verified previous artifact')
            with patch('safe_io.os.fsync', side_effect=OSError(errno.ENOSPC, 'disk full')):
                with self.assertRaises(OSError):
                    write_text(target, 'replacement that must not become visible')
            self.assertEqual(target.read_text(encoding='utf-8'), 'verified previous artifact')
            self.assertEqual(list(Path(directory).iterdir()), [target])


if __name__ == '__main__':
    unittest.main()
