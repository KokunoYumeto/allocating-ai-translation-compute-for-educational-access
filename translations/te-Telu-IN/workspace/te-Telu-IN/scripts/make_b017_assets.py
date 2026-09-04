"""Selected pinned B017 originals and code-native perimeter diagrams.

No network or bulk extraction. Original rasters are never overwritten.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image
from build import atomic_write
from inspect_source import slots, CN

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / 'assets/B017'
COMMIT = '38cae454e644abf9f0a623e876994553881597c9'
SOURCE_SHA = '749a7764e3df7024919ddf26db57a6ad1c6628aa8b44929a204527d58ea746cf'
MODULE_SHA = 'b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b'
ARCHIVE_SHA = 'effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
PREFIX = 'CNX_BMath_Figure_01_02_'
NAMES = [PREFIX + suffix + '.jpg' for suffix in ('002', '003', '004')]
SVG = '{http://www.w3.org/2000/svg}'
INK = '#183544'
EDGE = '#176b75'
FILL = '#e6f3ef'
FONT = 'Noto Sans Telugu, Nirmala UI, sans-serif'
SPECS = {
    '002': {'unit_te': 'అడుగులు', 'unit_locative': 'అడుగుల్లో', 'unit_en': 'feet', 'answer': 26,
        'vertices': [(90,70),(630,70),(630,190),(450,190),(450,310),(90,310)],
        'labels': [('9',360,54),('2',656,140),('3',540,178),('2',430,255),('6',270,346),('4',64,200)]},
    '003': {'unit_te': 'అంగుళాలు', 'unit_locative': 'అంగుళాల్లో', 'unit_en': 'inches', 'answer': 30,
        'vertices': [(80,80),(620,80),(620,320),(440,320),(440,200),(260,200),(260,320),(80,320)],
        'labels': [('9',350,62),('4',647,205),('3',530,348),('2',458,262),('3',350,187),('2',242,262),('3',170,348),('4',53,205)]},
    '004': {'unit_te': 'అంగుళాలు', 'unit_locative': 'అంగుళాల్లో', 'unit_en': 'inches', 'answer': 36,
        'vertices': [(70,80),(670,80),(670,380),(470,380),(470,280),(270,280),(270,180),(70,180)],
        'labels': [('12',370,62),('6',696,235),('4',570,411),('2',491,335),('4',370,269),('2',249,235),('4',170,169),('2',46,130)]},
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    need(shutil.disk_usage(BASE).free >= 32 * 1024 * 1024 + len(data), 'Free-space guard')
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, data)


def source():
    raw = (BASE / 'sources/TE-B017.en.cnxml').read_bytes()
    need(digest(raw) == SOURCE_SHA, 'Frozen source changed')
    meta = json.loads((BASE / 'sources/TE-B017.source.json').read_text('utf-8'))
    need(meta['source_commit'] == COMMIT and meta['source_sha256'] == SOURCE_SHA
         and meta['source_module']['sha256'] == MODULE_SHA and meta['text_slots'] == 114,
         'Source pin/count changed')
    root = ET.fromstring(raw)
    need(root.get('id') == 'fs-id2197427' and len(list(root.iter())) == 210
         and len(list(slots(root))) == 114, 'Source scope/count changed')
    need([Path(e.get('src')).name for e in root.iter(CN + 'image')] == NAMES,
         'Selected images/order changed')
    module = (ROOT / meta['source_module']['path']).read_bytes()
    need(digest(module) == MODULE_SHA, 'Canonical module changed')
    selected = next(e for e in ET.fromstring(module).iter() if e.get('id') == 'fs-id2197427')
    selected.tail = None
    need(ET.tostring(selected) == ET.tostring(root), 'Frozen selection differs from canonical')
    return root


def originals(write_missing=False):
    root = source()
    parents = {c: p for p in root.iter() for c in p}
    lock = json.loads((BASE / 'sources.lock.json').read_text('utf-8'))
    record = next(r for r in lock['canonical_archives'] if r['id'] == 'A00-A20-en-complete-archive')
    need(record['sha256'] == ARCHIVE_SHA and record['commit'] == COMMIT, 'Archive lock changed')
    archive = ROOT / record['path']
    need(archive.stat().st_size == 537455794 and file_digest(archive) == ARCHIVE_SHA,
         'Archive bytes changed')
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
    listing = subprocess.check_output(['git', '-C', str(ROOT / 'downloads/upstream-prealgebra'),
        'ls-tree', '-z', COMMIT, '--'] + ['media/' + n for n in NAMES], env=env)
    blobs = {}
    for row in listing.split(b'\0'):
        if row:
            header, path = row.split(b'\t')
            mode, kind, blob = header.split()
            need(kind == b'blob', 'Selected object is not a blob')
            blobs[path.decode()] = blob.decode()
    need(set(blobs) == {'media/' + n for n in NAMES}, 'Pinned image set differs')
    assets = []
    with zipfile.ZipFile(archive) as z:
        need(z.comment.decode() == COMMIT, 'Archive comment changed')
        for image, name in zip(root.iter(CN + 'image'), NAMES):
            member = 'osbooks-prealgebra-bundle-' + COMMIT + '/media/' + name
            info = z.getinfo(member)
            need(0 < info.file_size < 2_000_000, 'Selected image exceeds bound')
            data = z.read(member)
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            need(blob == blobs['media/' + name], 'Image differs from pinned Git blob')
            path = OUT / 'original' / name
            if path.exists():
                need(path.read_bytes() == data, 'Refusing original overwrite: ' + name)
            elif write_missing:
                write(path, data)
            else:
                raise FileNotFoundError(path)
            with Image.open(io.BytesIO(data)) as opened:
                dimensions = list(opened.size)
            assets.append({'original_src': image.get('src'),
                'original_path': path.relative_to(BASE).as_posix(),
                'original_sha256': digest(data), 'original_bytes': len(data),
                'original_dimensions_px': dimensions, 'source_git_blob_sha1': blob,
                'source_zip_crc32': f'{info.CRC:08x}', 'source_zip_member': member,
                'media_id': parents[image].get('id'), 'figure_id': None,
                'localized_path': (OUT / (Path(name).stem + '.te.svg')).relative_to(BASE).as_posix()})
    return assets


def element(parent, tag, attrs=None, text=None):
    node = ET.SubElement(parent, SVG + tag, {k: str(v) for k, v in (attrs or {}).items()})
    if text is not None:
        node.text = text
    return node


def diagram(suffix):
    spec = SPECS[suffix]
    width, height = (720, 400) if suffix != '004' else (740, 460)
    ET.register_namespace('', SVG[1:-1])
    root = ET.Element(SVG + 'svg', {'viewBox': f'0 0 {width} {height}', 'width': str(width),
        'height': str(height), 'role': 'img', 'aria-labelledby': 'title desc', 'lang': 'te',
        'data-source-suffix': suffix})
    element(root, 'title', {'id': 'title'}, 'చుట్టుకొలత కోసం ఇచ్చిన ఆకారం (perimeter figure)')
    order = ', '.join(value for value, _, _ in spec['labels'])
    element(root, 'desc', {'id': 'desc'},
        f"మూసుకున్న {len(spec['vertices'])}-భుజాల ఆకారం. గడియార దిశలో పై అంచు నుంచి పొడవులు: {order} {spec['unit_te']}. "
        f"Closed {len(spec['vertices'])}-sided figure; clockwise from the top edge: {order} {spec['unit_en']}. "
        'The answer is not shown; add every labeled boundary edge once.')
    element(root, 'metadata', text='New code-native mathematical redraw of the pinned OpenStax problem image; original raster retained unchanged. No answer is inserted.')
    element(root, 'rect', {'x': 0, 'y': 0, 'width': width, 'height': height, 'fill': '#ffffff', 'data-role': 'background'})
    element(root, 'text', {'x': width / 2, 'y': height - 14, 'text-anchor': 'middle',
        'font-family': FONT, 'font-size': 21, 'fill': INK, 'data-role': 'unit-note'},
        f"పొడవులన్నీ {spec['unit_locative']} ({spec['unit_en']}) ఉన్నాయి")
    points = ' '.join(f'{x},{y}' for x, y in spec['vertices'])
    element(root, 'polygon', {'points': points, 'fill': FILL, 'stroke': EDGE, 'stroke-width': 5,
        'stroke-linejoin': 'round', 'data-role': 'boundary'})
    for index, (value, x, y) in enumerate(spec['labels'], 1):
        element(root, 'text', {'x': x, 'y': y, 'text-anchor': 'middle', 'font-family': FONT,
            'font-size': 28, 'font-weight': '600', 'fill': INK, 'data-role': 'side-label',
            'data-edge': index, 'data-length': value}, value)
    if suffix == '002':
        element(root, 'line', {'x1': 438, 'y1': 248, 'x2': 451, 'y2': 248, 'stroke': INK,
            'stroke-width': 2, 'data-role': 'label-leader', 'data-edge': 4})
    data = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
    validate_svg(ET.fromstring(data), suffix)
    return data


def validate_svg(root, suffix):
    spec = SPECS[suffix]
    need(root.tag == SVG + 'svg' and root.get('data-source-suffix') == suffix, 'SVG identity changed')
    boundary = root.find(".//" + SVG + "polygon[@data-role='boundary']")
    need(boundary is not None, 'Boundary missing')
    actual_vertices = [tuple(map(float, point.split(','))) for point in boundary.get('points').split()]
    need(actual_vertices == [(float(x), float(y)) for x, y in spec['vertices']], 'Boundary topology changed')
    labels = [n for n in root.iter(SVG + 'text') if n.get('data-role') == 'side-label']
    need([(n.text, int(n.get('data-edge')), n.get('data-length')) for n in labels]
         == [(v, i, v) for i, (v, _, _) in enumerate(spec['labels'], 1)], 'Side labels/order changed')
    lengths = [int(n.text) for n in labels]
    need(sum(lengths) == spec['answer'], 'Perimeter invariant changed')
    need(len(labels) == len(spec['vertices']) and len(set(n.get('data-edge') for n in labels)) == len(labels),
         'Every boundary edge must be labeled once')
    note = next(n for n in root.iter(SVG + 'text') if n.get('data-role') == 'unit-note')
    need(spec['unit_locative'] in (note.text or '') and spec['unit_en'] in (note.text or ''), 'Units changed')
    need(not any(n.get('data-role') == 'answer' for n in root.iter()), 'Problem image reveals answer')
    desc = ''.join(root.find(SVG + 'desc').itertext())
    need('answer is not shown' in desc and str(len(labels)) + '-sided' in desc, 'Description scope changed')
    if suffix == '002':
        leader = root.find(".//" + SVG + "line[@data-role='label-leader']")
        need(leader is not None and leader.get('data-edge') == '4', 'Inset-edge leader changed')
    return spec['answer']


def manifest(assets):
    for asset, suffix in zip(assets, SPECS):
        local = BASE / asset['localized_path']
        need(local.is_file(), 'Localized SVG missing')
        asset['localized_sha256'] = digest(local.read_bytes())
        asset['localized_bytes'] = local.stat().st_size
        asset['source_side_lengths_clockwise_from_top'] = [int(x[0]) for x in SPECS[suffix]['labels']]
        asset['verified_perimeter_not_displayed'] = SPECS[suffix]['answer']
        asset['disclosure'] = 'New code-native mathematical redraw; preserved original is unchanged; no source answer is shown in the problem diagram.'
        asset['recommended_min_width_px'] = 640
    return {'schema': 'te-b002-assets-v1', 'unit': 'TE-B017',
        'source_subsection_id': 'fs-id2197427', 'source_subsection_sha256': SOURCE_SHA,
        'canonical_commit': COMMIT,
        'source_attribution': 'OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.',
        'assets': assets,
        'scope': 'Three exact selected originals and three new code-native localized problem-diagram redraws; no source answer is inserted.',
        'verification': 'Pinned ZIP bytes, Git blobs, source order, boundary vertices, every visible length, units and independently derived perimeter invariants are checked.',
        'qa': {'source_media_count': 3, 'localized_asset_count': 3, 'originals_preserved': True,
            'answer_not_in_problem_svg': True, 'independent_visual_approval': False, 'native_speaker_approval': False}}


def verify():
    assets = originals(False)
    saved = json.loads((OUT / 'manifest.json').read_text('utf-8'))
    for asset, suffix in zip(assets, SPECS):
        path = OUT / (PREFIX + suffix + '.te.svg')
        validate_svg(ET.parse(path).getroot(), suffix)
        need(saved['assets'][list(SPECS).index(suffix)]['localized_sha256'] == file_digest(path), 'Manifest SVG hash changed')
    need(saved == manifest(assets), 'Manifest content changed')
    return 3


def self_test():
    rejected = 0
    for suffix in SPECS:
        original = ET.fromstring(diagram(suffix))
        mutations = []
        wrong = ET.fromstring(ET.tostring(original))
        next(n for n in wrong.iter(SVG + 'text') if n.get('data-role') == 'side-label').text = '99'
        mutations.append(wrong)
        wrong = ET.fromstring(ET.tostring(original))
        wrong.find(".//" + SVG + "polygon[@data-role='boundary']").set('points', '0,0 ' + wrong.find(".//" + SVG + "polygon[@data-role='boundary']").get('points'))
        mutations.append(wrong)
        wrong = ET.fromstring(ET.tostring(original))
        next(n for n in wrong.iter(SVG + 'text') if n.get('data-role') == 'unit-note').text = 'unit missing'
        mutations.append(wrong)
        wrong = ET.fromstring(ET.tostring(original))
        element(wrong, 'text', {'data-role': 'answer'}, str(SPECS[suffix]['answer']))
        mutations.append(wrong)
        for mutation in mutations:
            try:
                validate_svg(mutation, suffix)
            except (ValueError, StopIteration):
                rejected += 1
            else:
                raise AssertionError('Corruption not rejected: ' + suffix)
    need(rejected == 12, 'Self-test coverage changed')
    return rejected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preserve-only', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    need(sum((args.preserve_only, args.verify, args.self_test)) <= 1, 'Choose one mode')
    if args.preserve_only:
        print(json.dumps(originals(write_missing=True), ensure_ascii=False, indent=2))
    elif args.verify:
        print('verified', verify(), 'B017 assets')
    elif args.self_test:
        print('rejected', self_test(), 'B017 corruptions')
    else:
        assets = originals(write_missing=True)
        for suffix in SPECS:
            write(OUT / (PREFIX + suffix + '.te.svg'), diagram(suffix))
        write(OUT / 'manifest.json', json.dumps(manifest(assets), ensure_ascii=False, indent=2).encode() + b'\n')
        print('created', verify(), 'B017 code-native assets')
