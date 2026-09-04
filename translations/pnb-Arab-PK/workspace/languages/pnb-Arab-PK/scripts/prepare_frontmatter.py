"""Prepare only PNB010's admitted JPEG; PNB011's quarantined JPEG is never copied.

All declared source/component/destination checks precede writes. Existing differing
files are never overwritten. No acquisition, rights re-audit or permission contact.
"""
from pathlib import Path, PurePosixPath
import argparse
import csv
import hashlib
import io
import json
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions, unique_object

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
RIGHTS = ROOT / 'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv'
SOURCE_ROOT = ROOT / 'downloads/complete-upstream/osbooks-college-algebra-bundle'
SPECS = {
    '010': ('m50919', '1483e6509bb6339890bae39b53c5bdb4b010a144558d95ae20b213ab1a06c176',
            'preface01', 'CNX_Precalc_Figure_Preface_01.jpg',
            '66e71b8e2eab72b69cdb3a89691726f322f35202e3390dc0c94fa40cc6379494', 975, 473),
    '011': ('m49299', '0b05ac175b00d400bc502d4eee3d6e338da3c70ca1e031b9bdd91a51608d3687',
            'fs-id1165137810701', 'CNX_Precalc_Figure_01_00_001n.jpg',
            'ca0b74aac78b0d531539da17c762954d38cd084c7770297216ef9b651bcc3363', 1401, 637),
}
FIELDS = ['rights_component_id', 'asset_path', 'bytes', 'sha256', 'source_modules',
          'classification', 'admission', 'license_id', 'attribution', 'required_action']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def signature(node):
    return node.tag, dict(node.attrib), node.text, tuple((signature(c), c.tail) for c in node)


def safe_path(value):
    p = PurePosixPath(value)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in value and ':' not in value
    assert p.as_posix() == value
    return p


def validate_component(unit, source, spec, row, data, notice):
    module, _, media_id, filename, sha, width, height = SPECS[unit]
    parent = {c: n for n in source.iter() for c in n}
    media = [n for n in source.iter() if tag(n) == 'media']
    assert len(media) == 1 and media[0].get('id') == media_id
    media = media[0]
    assert len(media) == 1 and tag(media[0]) == 'image'
    assert media[0].get('src') == '../../media/' + filename
    assert spec['media_id'] == media_id and spec['source_path'] == 'media/' + filename
    assert spec['path'] == f'assets/unit-{unit}-{media_id}.jpg'
    assert safe_path(spec['source_path']).parts == ('media', filename)
    assert safe_path(spec['path']).parts == ('assets', f'unit-{unit}-{media_id}.jpg')
    assert spec['sha256'] == digest(data) == sha
    assert (spec['width'], spec['height']) == jpeg_dimensions(data) == (width, height)
    assert all(type(spec[k]) is int for k in ('bytes', 'width', 'height'))
    assert spec['bytes'] == len(data) == int(row['bytes'])
    assert spec['source_mime_type'] == media[0].get('mime-type')
    assert spec['component_rights_id'] == row['rights_component_id']
    assert row['sha256'] == sha and row['asset_path'] == spec['source_path'] and row['source_modules'] == module
    assert list(row) == FIELDS and notice == [row]
    if unit == '010':
        assert tag(parent[media]) == 'section' and parent[media].get('id') == 'eip-236'
        assert 'figure_id' not in spec
        assert spec['publication_status'] == 'admitted-unchanged'
        assert row['admission'] == 'admitted' and row['classification'] == 'WORK_DEFAULT_UNCREDITED_ART'
        assert row['license_id'] == 'CC-BY-NC-SA-4.0'
        assert row['attribution'] == 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0.'
    else:
        assert tag(parent[media]) == 'figure' and parent[media].get('id') == spec['figure_id'] == 'Figure_01_00_001'
        assert spec['publication_status'] == 'quarantined-not-copied'
        assert row['admission'] == 'quarantined' and row['classification'] == 'STRICT_RISK_UNKNOWN'
        assert row['license_id'] == 'NOASSERTION'
        assert row['attribution'] == 'credit "bull": modification of work by Prayitno Hadinata; credit "graph": modification of work by MeasuringWorth'
    return unit == '010'


def prepare(unit, check_only=False):
    module, raw_sha, *_ = SPECS[unit]
    manifest_path = BASE / f'source-excerpts/manifest-{unit}.json'
    excerpt = BASE / f'source-excerpts/unit-{unit}.cnxml'
    canonical = ROOT / f'downloads/upstream/osbooks-college-algebra-bundle/modules/{module}/index.cnxml'
    notice_path = BASE / f'provenance/unit-{unit}-component-notices.json'
    inputs = {p: p.read_bytes() for p in (manifest_path, excerpt, canonical, RIGHTS, notice_path)}
    manifest = json.loads(inputs[manifest_path], object_pairs_hook=unique_object)
    notice = json.loads(inputs[notice_path], object_pairs_hook=unique_object)
    assert manifest['unit'] == 'PNB-' + unit and manifest['module'] == module
    assert manifest['commit'] == '789b54099106b071d1d32bfcee454fed72eb4768'
    assert manifest['source_excerpt'] == excerpt.name
    assert digest(inputs[canonical]) == manifest['source_byte_witnesses']['canonical_checkout_sha256'] == raw_sha
    full_lf = inputs[canonical].replace(b'\r\n', b'\n')
    excerpt_lf = inputs[excerpt].replace(b'\r\n', b'\n')
    assert not full_lf.endswith(b'\n') and excerpt_lf == full_lf + b'\n'
    assert digest(full_lf) == manifest['full_module_sha256'] and digest(excerpt_lf) == manifest['excerpt_sha256']
    source = ET.fromstring(inputs[excerpt])
    assert signature(source) == signature(ET.fromstring(inputs[canonical]))
    assert len(manifest['images']) == 1
    spec = manifest['images'][0]
    rows_reader = csv.DictReader(io.StringIO(inputs[RIGHTS].decode('utf-8-sig'), newline=''))
    rows = list(rows_reader)
    assert rows_reader.fieldnames == FIELDS
    matches = [row for row in rows if row['asset_path'] == spec['source_path']]
    assert len(matches) == 1
    source_path = (SOURCE_ROOT / safe_path(spec['source_path'])).resolve()
    destination = (BASE / safe_path(spec['path'])).resolve()
    assert source_path.is_relative_to((SOURCE_ROOT / 'media').resolve())
    assert destination.is_relative_to((BASE / 'assets').resolve())
    data = source_path.read_bytes()
    admitted = validate_component(unit, source, spec, matches[0], data, notice)
    if admitted:
        assert not destination.exists() or destination.read_bytes() == data, 'Different existing asset; refusing overwrite'
    else:
        assert not destination.exists(), 'Quarantined component must not exist in publishable language assets'
    assert all(p.read_bytes() == b for p, b in inputs.items()), 'Inputs changed before output creation'
    if admitted and not check_only:
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with destination.open('xb') as stream:
                stream.write(data)
        except FileExistsError:
            pass
        assert destination.read_bytes() == data
    return {'unit': 'PNB-' + unit, 'source_images': 1, 'publishable_images': int(admitted),
            'quarantined_images': int(not admitted), 'copied_bytes': len(data) if admitted and not check_only else 0,
            'check_only': check_only, 'asset_coverage_complete': admitted}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', choices=['010', '011'], required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.unit, args.check_only), sort_keys=True))
