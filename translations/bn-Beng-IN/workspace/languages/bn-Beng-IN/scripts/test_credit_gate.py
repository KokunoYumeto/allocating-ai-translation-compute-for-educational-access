"""Narrow retained-credit exception must not admit untranslated learner prose."""
import copy,json,tempfile,unittest
from pathlib import Path
import build

class CreditGateTests(unittest.TestCase):
    def setUp(self):
        self.overlay=json.loads((build.LANG/'translations/m81292-CNX_BMath_Figure_05_00_002.bn-Beng-IN.json').read_text(encoding='utf-8'))
    def run_overlay(self,overlay):
        with tempfile.TemporaryDirectory(prefix='bn-credit-gate-') as directory:
            path=Path(directory)/'test.json'
            path.write_text(json.dumps(overlay,ensure_ascii=False),encoding='utf-8')
            return build.translated(path)
    def test_exact_source_credit_is_retained(self):
        source,target=self.run_overlay(self.overlay)
        self.assertIn('Mark Turnauckus, Flickr',target.find(f'{{{build.C}}}caption').text)
        self.assertEqual(build.math_signature(source),build.math_signature(target))
    def test_no_exception_rejects_english(self):
        self.overlay.pop('retained_credit_names')
        with self.assertRaises(AssertionError):self.run_overlay(self.overlay)
    def test_other_english_is_still_rejected(self):
        self.overlay['nodes']['./c:caption'][0]+=' Untranslated sentence.'
        with self.assertRaises(AssertionError):self.run_overlay(self.overlay)
    def test_absent_source_credit_rejected(self):
        self.overlay['retained_credit_names'][0]['source']='Invented Name'
        self.overlay['nodes']['./c:caption'][0]+=' Invented Name'
        with self.assertRaises(AssertionError):self.run_overlay(self.overlay)
    def test_non_caption_exception_rejected(self):
        self.overlay['retained_credit_names'][0]['xpath']='./c:media'
        with self.assertRaises(AssertionError):self.run_overlay(self.overlay)
    def test_duplicate_credit_rejected(self):
        self.overlay['nodes']['./c:caption'][0]+=' Mark Turnauckus, Flickr'
        with self.assertRaises(AssertionError):self.run_overlay(self.overlay)

if __name__=='__main__':unittest.main()
