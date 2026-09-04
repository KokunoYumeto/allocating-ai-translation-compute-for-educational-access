"""Prepare the complete m82451 introduction's one unchanged splash photograph.

Existing source/rights evidence is retained, never reinterpreted as new clearance.
All input and target checks run before the asset or notice is written.
"""
from pathlib import Path
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

from prepare_a10 import jpeg_dimensions, tree

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / 'source-excerpts/manifest-a10-introduction.json'
TRANSLATION = BASE / 'translations/a10-introduction.json'
EXCERPT = BASE / 'source-excerpts/a10-introduction.cnxml'
NOTICES = BASE / 'provenance/a10-introduction-component-notices.json'
CANONICAL = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
N = '{http://cnx.rice.edu/cnxml}'
MD = '{http://cnx.rice.edu/mdml}'
SOURCE_IDS = ['CNX_ElemAlg_Figure_01_00_001', 'fs-id1170654013255', 'fs-id1170653837691']
SOURCE_KEYS = ['m82451/title', 'fs-id1170654013255/alt', 'CNX_ElemAlg_Figure_01_00_001/caption', 'fs-id1170653837691']
DEFAULT_CREDIT = 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.'
AUTHORS = ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes())


def load_inputs():
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    t = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    require((m['unit'], m['assignment'], m['module'], m['collection'], m['locale'])
            == ('A10-introduction', 'A10', 'm82451', 'col31130', 'pnb-Arab-PK'), 'Introduction scope changed')
    require((t['unit'], t['assignment'], t['module'], t['locale'])
            == ('A10-introduction', 'A10', 'm82451', 'pnb-Arab-PK'), 'Translation scope changed')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pinned = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    require((m['commit'], m['tree']) == (pinned['commit'], pinned['tree']), 'Existing source lock mismatch')
    canonical_path = CANONICAL / 'modules/m82451/index.cnxml'
    require((ROOT / m['canonical_local_path']).resolve() == canonical_path.resolve(), 'Canonical path changed')
    raw = canonical_path.read_bytes()
    require(len(raw) == m['full_module_bytes'] == 1066 and digest(raw) == m['full_module_sha256'], 'Canonical bytes changed')
    require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            == m['canonical_git_blob_sha1'], 'Canonical Git blob changed')
    require((ROOT / m['release_authority_path']).read_bytes() == raw, 'English authority differs')
    witness = EXCERPT.read_bytes()
    require(m['source_excerpt'] == EXCERPT.name and witness == raw + b'\n', 'Entire canonical witness differs')
    require(len(witness) == m['excerpt_bytes'] == 1067 and digest(witness) == m['excerpt_sha256'], 'Witness digest changed')
    source = ET.fromstring(witness)
    require(tree(source) == tree(ET.fromstring(raw)), 'Complete parsed source differs')
    require(source.attrib == {'class': 'introduction'} and source.tag == N + 'document', 'Document attributes changed')
    require([x.tag for x in source] == [N+'title', N+'metadata', N+'content'], 'Full document child order changed')
    require([x.get('id') for x in source.iter() if x.get('id')] == m['source_ids_in_document_order'] == SOURCE_IDS,
            'Source ID coverage/order changed')
    content = source.find(N+'content')
    require([x.get('id') for x in content] == [SOURCE_IDS[0], SOURCE_IDS[2]], 'Source content boundary changed')
    require(list(t['source_blocks']) == m['source_text_keys_in_order'] == SOURCE_KEYS, 'Four source keys changed')
    require(t['title'] == t['source_blocks']['m82451/title'] == m['module_title_pnb'], 'Source title differs')
    require(t['retained_attribution']['original_senior_contributing_authors'] == AUTHORS
            and m['retained_book_attribution']['original_senior_contributing_authors'] == AUTHORS, 'Book author credit changed')
    require(len(m['images']) == 1, 'Introduction requires one image')
    spec = m['images'][0]
    filename = 'CNX_ElemAlg_Figure_01_00_001_img_new.jpg'
    require(spec['source_path'] == 'media/' + filename and spec['source_src'] == '../../media/' + filename,
            'Image source path changed')
    original = CANONICAL / 'media' / filename
    target = BASE / 'assets/a10' / filename
    require(spec['canonical_local_path'] == original.relative_to(ROOT).as_posix()
            and spec['path'] == target.relative_to(BASE).as_posix(), 'Image path escaped its declared location')
    require(target.resolve().parent == (BASE / 'assets/a10').resolve(), 'Unsafe image destination')
    image_node = source.find('.//'+N+'image')
    require(image_node.attrib == {'mime-type': 'image/jpeg', 'src': spec['source_src']}, 'Source image attributes changed')
    data = original.read_bytes()
    require(len(data) == spec['bytes'] == 251847 and digest(data) == spec['sha256'], 'Image hash/size mismatch')
    require(jpeg_dimensions(data) == (spec['width'], spec['height']) == (975, 450), 'Image dimensions changed')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = [x for x in csv.DictReader(handle) if x['relative_path'] == spec['source_path']]
    require(len(rows) == 1, 'Media authority row missing/duplicated')
    row = rows[0]
    require(row['sha256'] == spec['sha256'] and int(row['bytes']) == len(data)
            and row['git_blob_sha1'] == spec['git_blob_sha1_from_existing_media_manifest']
            == hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(), 'Media authority identity differs')
    for item in m['existing_notice_inputs']:
        require(digest((ROOT / item['path']).read_bytes().replace(b'\r\n',b'\n')) == item['sha256'],
                'Existing notice input logical-LF hash changed: '+item['path'])
    credit = m['source_art_default_credit_provenance']
    preface_path = CANONICAL / 'modules/m82630/index.cnxml'
    require(credit['canonical_local_path'] == preface_path.relative_to(ROOT).as_posix()
            and file_hash(preface_path) == credit['module_sha256'], 'Default-credit provenance changed')
    preface = ET.parse(preface_path).getroot()
    node = next(x for x in preface.iter() if x.get('id') == credit['paragraph_id'] == 'eip-787')
    credit_text = ''.join(node.itertext())
    require(credit_text.endswith(DEFAULT_CREDIT) and credit['exact_credit'] == DEFAULT_CREDIT
            == spec['source_art_default_credit'] == t['retained_attribution']['source_art_default_credit'],
            'Raw source default art credit changed')
    require('limitations provided in the credit' in credit_text, 'Source component limits not retained')
    return m, t, source, (spec, original, target, data, row), credit_text


def notice_record(m, prepared, credit_text):
    spec, original, target, data, row = prepared
    return {
        'schema': 'a10-retained-component-evidence-v1', 'unit': 'A10-introduction',
        'work': 'OpenStax Elementary Algebra 2e', 'module': 'm82451', 'collection': 'col31130', 'commit': m['commit'],
        'manifest_sha256': file_hash(MANIFEST), 'excerpt_sha256': m['excerpt_sha256'],
        'scope': 'The complete m82451 introduction and one unchanged original splash photograph; no new license or supply audit.',
        'existing_notice_inputs': m['existing_notice_inputs'],
        'existing_notice_input_hash_policy': m['existing_notice_input_hash_policy'],
        'release_notice_verbatim': (BASE/'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
        'original_senior_contributing_authors': AUTHORS,
        'existing_license_statement': m['retained_book_attribution']['existing_license_statement'],
        'non_endorsement': m['retained_book_attribution']['non_endorsement'],
        'rights_status': 'Existing audited A10 policy retained; no new component-specific clearance determination.',
        'credit_limit': 'The media authority row identifies bytes and Git blobs, not rights holders or permissions. No photographer is named in m82451. The pinned preface supplies a default credit; its source claim is retained, not independently verified as image-specific clearance.',
        'source_art_default_credit_provenance': m['source_art_default_credit_provenance'],
        'raw_source_art_attribution_paragraph_verbatim': credit_text,
        'media_authority_manifest': {'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(), 'sha256': file_hash(MEDIA_MANIFEST)},
        'images': [{**{key: spec[key] for key in ('figure_id','figure_class','media_id','source_path','path','sha256','bytes','width','height','source_art_default_credit')},
                    'existing_media_authority_row': row,
                    'treatment': 'Original splash photograph bytes retained, unmirrored; source-bound Punjabi alt and caption. Responsive display preserves aspect ratio.',
                    'component_clearance': 'Not newly assessed; subject to retained component-specific credits and restrictions.'}],
        'whole_book_translation_complete': False,
        'earlier_collection_items_pending': m['earlier_collection_items_still_pending']
    }


def prepare():
    m, t, source, prepared, credit_text = load_inputs()
    spec, original, target, data, row = prepared
    require(not target.exists() or file_hash(target) == spec['sha256'], 'Refusing to overwrite a different existing asset')
    # Validation above resolves the unique target before any generated output is written.
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(data)
    require(file_hash(target) == spec['sha256'], 'Copied image hash mismatch')
    NOTICES.write_text(json.dumps(notice_record(m, prepared, credit_text), ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Prepared complete A10 introduction: one exact original photograph; raw-source default credit retained with limits.')


if __name__ == '__main__':
    prepare()
