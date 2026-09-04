"""Offline positive and negative QA; all mutation happens in disposable copies."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest

LANG = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reader_builder', LANG/'tools/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='mr-bridge-test-')
        self.base = Path(self.tmp.name)/'mr-Deva-IN'
        self.base.mkdir()
        # Copy only pilot dependencies, never the growing whole language tree.
        for relative in ('sources.lock.json', 'terminology.csv',
                         'translations/MR-BRIDGE-001.xml', 'tools/reader.css'):
            destination = self.base/relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(LANG/relative, destination)
        import json
        lock = json.loads((LANG/'sources.lock.json').read_bytes())
        for witness in lock['witnesses']:
            destination = self.base/witness['path']
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(LANG/witness['path'], destination)
        builder.BASE = self.base
        builder.SOURCE = self.base/'translations/MR-BRIDGE-001.xml'

    def tearDown(self):
        self.tmp.cleanup()

    def run_build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            builder.run()

    def mutate(self, old, new):
        source = builder.SOURCE.read_text(encoding='utf-8')
        self.assertIn(old,source)
        builder.SOURCE.write_text(source.replace(old,new,1),encoding='utf-8')

    def test_offline_determinism(self):
        self.assertFalse((self.base.parent/'downloads').exists())
        self.run_build()
        first = (self.base/'output/MR-BRIDGE-001.html').read_bytes()
        self.run_build()
        self.assertEqual(first,(self.base/'output/MR-BRIDGE-001.html').read_bytes())

    def test_wrong_answer_fails(self):
        self.mutate('−315/770 = −9/22','−315/770 = −9/23')
        with self.assertRaisesRegex(ValueError,'mathematical chain'):
            self.run_build()

    def test_broken_reference_fails(self):
        self.mutate('href="#S-D1"','href="#missing"')
        with self.assertRaisesRegex(ValueError,'broken answer'):
            self.run_build()

    def test_wrong_locale_fails(self):
        self.mutate('lang="mr-Deva-IN"','lang="hi-Deva-IN"')
        with self.assertRaisesRegex(ValueError,'wrong locale'):
            self.run_build()

    def test_source_drift_fails(self):
        self.mutate('A20:m81359#fs-id1167836620030','A20:m81359#wrong')
        with self.assertRaisesRegex(ValueError,'source selection drift'):
            self.run_build()

    def test_witness_drift_fails(self):
        witness = self.base/'provenance/selected-source-blocks.xml'
        witness.write_bytes(witness.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'witness drift'):
            self.run_build()

    def test_additional_term_preserves_pilot_output(self):
        self.run_build()
        first = (self.base/'output/MR-BRIDGE-001.html').read_bytes()
        ledger = self.base/'terminology.csv'
        with ledger.open('a', encoding='utf-8', newline='') as handle:
            handle.write('T999,test-only term,चाचणी,Disposable fixture.,provisional\n')
        self.run_build()
        self.assertEqual(first, (self.base/'output/MR-BRIDGE-001.html').read_bytes())

    def test_missing_baseline_term_fails(self):
        ledger = self.base/'terminology.csv'
        ledger.write_text('\n'.join(line for line in ledger.read_text(encoding='utf-8').splitlines()
                                   if not line.startswith('T033,'))+'\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'term ledger'):
            self.run_build()

    def test_duplicate_term_fails(self):
        ledger = self.base/'terminology.csv'
        with ledger.open('a', encoding='utf-8', newline='') as handle:
            handle.write('T033,duplicate,चाचणी,Disposable fixture.,provisional\n')
        with self.assertRaisesRegex(ValueError, 'term ledger'):
            self.run_build()

if __name__ == '__main__':
    unittest.main(verbosity=2)
