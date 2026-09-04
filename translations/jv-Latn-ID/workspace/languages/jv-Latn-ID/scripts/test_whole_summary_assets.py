"""Verify the recap's exact source alias, not a filename-based chart reuse."""
import json
import re
import unittest
from unittest.mock import patch
from config import LANG
from prepare_digit_place_assets import geometry_signature, text_nodes, sha256
import prepare_whole_summary_assets as summary


class SummaryAssets(unittest.TestCase):
    def test_saved_manifest_and_deterministic_dependency_reuse(self):
        generated=summary.products()
        self.assertEqual(generated,summary.products())
        self.assertEqual(len(generated),1)
        for path,raw in generated.items():
            self.assertEqual((LANG/path).read_bytes(),raw)
        manifest=json.loads(next(iter(generated.values())))
        asset=manifest['assets'][0]
        self.assertIn('011.png.id-ID.svg',asset['source_src'])
        self.assertEqual(asset['canonical_original']['actual_mime'],'image/png')
        source=(LANG/asset['outputs']['id-academic']['path']).read_bytes()
        self.assertEqual(sha256(source),summary.SOURCE_HASH)
        for track,output in asset['outputs'].items():
            target=(LANG/output['path']).read_bytes()
            self.assertEqual(geometry_signature(source),geometry_signature(target))
            numbers=[n for n in text_nodes(target) if re.fullmatch(r'\d+',n.text or '')]
            self.assertEqual([n.text for n in numbers],list('5278194'))
            self.assertEqual([int(n.get('x')) for n in numbers],[474,528,582,636,690,744,798])
            self.assertEqual([n.get('y') for n in numbers],['585']*7)
            self.assertEqual(asset['leading_empty_digit_cells'],8)
            self.assertEqual(output['mime_type'],'image/svg+xml')

    def test_changed_alias_source_fails_closed(self):
        original=summary.pinned_blob
        def changed(repo,commit,path,oid):
            raw=original(repo,commit,path,oid)
            return raw.replace(b'>5</text>',b'>6</text>') if path.endswith('.svg') else raw
        with patch.object(summary,'pinned_blob',changed),self.assertRaises(AssertionError):
            summary.products()

    def test_changed_canonical_identity_fails_closed(self):
        with patch.object(summary,'git',return_value=b'0'*40),self.assertRaises(AssertionError):
            summary.products()


if __name__ == '__main__':
    unittest.main()
