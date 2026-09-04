"""Finite numeric, geometry-repair and deterministic rounding asset checks."""
import json
import re
import unittest
import xml.etree.ElementTree as ET

from config import LANG, TRACKS
import prepare_rounding_assets as assets

NUMBERS = {
    '022.jpg': ['7', '6'], '031_img.jpg': ['76', '80'],
    '032_img.jpg': ['7', '2'], '033_img.jpg': ['72', '70'],
    '034_img-01.png': ['843'], '035_img-01.png': ['23,658'],
    '035_img-02.png': ['23,658', '23,700'], '036_img-01.png': ['3,978'],
    '036_img-02.png': ['3,978', '4,000'], '037_img-01.png': ['147,032'],
    '038_img-01.png': ['29,504'], '038_img-03.png': ['29,504', '30,000'],
}
SVG = '{http://www.w3.org/2000/svg}'


class RoundingAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((LANG / 'translation/a00-rounding.assets.json').read_text(encoding='utf-8'))

    def test_complete_source_media_scope_and_actual_mime(self):
        rows = self.manifest['assets']
        self.assertEqual(len(rows), 23)
        self.assertEqual(len({row['media_id'] for row in rows}), 23)
        self.assertEqual([sum(row['mime_type'] == m for row in rows)
                          for m in ('image/svg+xml', 'image/png', 'image/jpeg')], [12, 8, 3])
        corrected_mimes = []
        for row in rows:
            source = (LANG / row['outputs']['id-academic']['path']).read_bytes()
            self.assertEqual(assets.sha256(source), row['source_sha256'])
            self.assertEqual(assets.blob_sha1(source), row['source_blob_sha1'])
            self.assertEqual(assets.mime(source), row['mime_type'])
            if row['source_declared_mime'] != row['mime_type']:
                corrected_mimes.append(row['canonical_path'].split('/')[-1])
            for output in row['outputs'].values():
                raw = (LANG / output['path']).read_bytes()
                self.assertEqual((assets.sha256(raw), len(raw), assets.mime(raw)),
                                 (output['sha256'], output['bytes'], output['mime_type']))
            if row['mime_type'] != 'image/svg+xml':
                self.assertEqual(row['source_sha256'], row['canonical_sha256'])
                self.assertEqual(len({v['path'] for v in row['outputs'].values()}), 1)
        self.assertEqual(corrected_mimes, [assets.PREFIX + f'034_img-0{n}.png' for n in (2, 3, 4)])

    def test_all_literal_numbers_labels_and_reversible_geometry_changes(self):
        for row in self.manifest['assets']:
            if row['mime_type'] != 'image/svg+xml':
                continue
            key = row['canonical_path'].removeprefix('media/' + assets.PREFIX)
            original = (LANG / row['outputs']['id-academic']['path']).read_bytes()
            self.assertEqual(assets.sha256(original), assets.SOURCE_SVGS[key])
            for track in ('jv-academic', 'jv-conversation'):
                raw = (LANG / row['outputs'][track]['path']).read_bytes()
                root = ET.fromstring(raw)
                self.assertEqual(root.get('{http://www.w3.org/XML/1998/namespace}lang'), 'jv-Latn-ID')
                self.assertEqual([n.text for n in root.iter(SVG + 'text') if re.fullmatch('[0-9,]+', n.text or '')], NUMBERS[key])
                self.assertEqual([n.text for n in assets.text_nodes(raw)],
                                 [row['translation_labels'][track].get(n.text, n.text) for n in assets.text_nodes(original)])
                restored = raw.decode()
                for change in reversed(row['target_only_geometry_repairs'][track]):
                    self.assertEqual(restored.count(change['after']), 1)
                    restored = restored.replace(change['after'], change['before'])
                self.assertEqual(assets.geometry_signature(original), assets.geometry_signature(restored.encode()))
                self.assertEqual(root.get('viewBox'), ET.fromstring(original).get('viewBox'))

    def test_actual_digit_and_complete_group_destinations(self):
        expected = {
            '022.jpg': [(150, 93), (185, 140)], '032_img.jpg': [(150, 93), (185, 140)],
            '031_img.jpg': [(252, 44), (269, 44)], '033_img.jpg': [(252, 44), (269, 44)],
            '035_img-01.png': [(176, 78)], '037_img-01.png': [(160, 78)], '038_img-01.png': [(194, 78)],
            '035_img-02.png': [(252, 42), (274, 50), (245, 160)],
            '036_img-02.png': [(452, 42), (473, 50), (455, 160)],
            '038_img-03.png': [(487, 42), (522, 50), (504, 160)],
        }
        brackets = {'035_img-02.png': 'M 260,38 V 43 H 287 V 38',
                    '036_img-02.png': 'M 459,38 V 43 H 486 V 38',
                    '038_img-03.png': 'M 501,38 V 43 H 543 V 38'}
        for key, arrows in expected.items():
            for track in ('jv-academic', 'jv-conversation'):
                path = LANG / f'translation/assets/a00-rounding/{assets.PREFIX}{key}.{track}.svg'
                root = ET.parse(path).getroot()
                lines = root.findall(SVG + 'line')
                heads = root.findall(SVG + 'polygon')
                self.assertEqual(len(heads), len(arrows))
                for line, head, point in zip(lines, heads, arrows):
                    self.assertEqual((float(line.get('x2')), float(line.get('y2'))), point)
                    self.assertEqual(tuple(map(float, head.get('points').split()[0].split(','))), point)
                if key in brackets:
                    self.assertEqual(root.find(SVG + 'path').get('d'), brackets[key])
                if key in ('031_img.jpg', '033_img.jpg'):
                    self.assertEqual({k: lines[-1].get(k) for k in ('x1','y1','x2','y2')},
                                     dict(zip(('x1','y1','x2','y2'), ('263','36','274','11'))))
                if key == '033_img.jpg':
                    self.assertIn('aja ditambahi 1', [node.text for node in root.iter(SVG + 'text')])
                if key in ('037_img-01.png', '038_img-01.png'):
                    center = arrows[0][0]
                    self.assertEqual((float(lines[-1].get('x1')), float(lines[-1].get('x2'))), (center-6, center+6))
        for source, result, place in [(76,80,10), (72,70,10), (23658,23700,100), (3978,4000,100), (29504,30000,1000)]:
            self.assertEqual((source + place // 2) // place * place, result)

    def test_changed_source_labels_digits_and_geometry_reject(self):
        for key in assets.SOURCE_SVGS:
            raw = (LANG / f'translation/assets/a00-rounding/{assets.PREFIX}{key}.id-ID.svg').read_bytes()
            for mutation in (raw.replace(b'font-size=', b'unregistered-size=', 1),
                             raw.replace(b'<title', b'<unknown', 1), raw + b'changed'):
                for track in ('jv-academic', 'jv-conversation'):
                    with self.subTest(key=key, track=track), self.assertRaises(AssertionError):
                        assets.localize(mutation, key, track)
            with self.assertRaises(AssertionError):
                assets.localize(raw, key, 'id-academic')

    def test_saved_products_are_exact_and_deterministic(self):
        first = assets.products()
        self.assertEqual(first, assets.products())
        self.assertEqual(len(first), 48)  # 11 rasters + 36 SVGs + manifest
        for path, raw in first.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)


if __name__ == '__main__':
    unittest.main()
