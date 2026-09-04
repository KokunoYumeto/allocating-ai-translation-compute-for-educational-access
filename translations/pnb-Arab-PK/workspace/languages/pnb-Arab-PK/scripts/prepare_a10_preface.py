"""Prepare four unchanged m82630 originals; retain existing evidence, not new clearance."""
from pathlib import Path
import csv
import hashlib
import json
import struct
import xml.etree.ElementTree as ET

from prepare_a10 import jpeg_dimensions, tree

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / 'source-excerpts/manifest-a10-preface.json'
TRANSLATION = BASE / 'translations/a10-preface.json'
EXCERPT = BASE / 'source-excerpts/a10-preface.cnxml'
NOTICES = BASE / 'provenance/a10-preface-component-notices.json'
CANONICAL = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
N = '{http://cnx.rice.edu/cnxml}'
MD = '{http://cnx.rice.edu/mdml}'
SOURCE_SHA = 'd9f45fb31f4cb399c009c2be25eca1a99132b4b6882fb07f8649c2d56974f90b'
DEFAULT_CREDIT = 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.'
AUTHORS = ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis']
FILENAMES = ['tryit.png', 'howtoicon.png', 'media.png', 'CNX_ElemAlg_Figure_05_01_015_img.jpg']
HASH_POLICY = 'SHA-256 after CRLF-to-LF normalization in memory; files are not rewritten. Source/image/Git-blob hashes are raw-byte identities.'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes())


def blob_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def dimensions(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        require(data[12:16] == b'IHDR', 'PNG header missing')
        return struct.unpack('>II', data[16:24])
    return jpeg_dimensions(data)


def source_inventory(source):
    parents = {child: parent for parent in source.iter() for child in parent}
    keys, roles, ancestors = [], {}, {}
    for node in source.iter():
        tag = node.tag.removeprefix(N)
        ident = node.get('id')
        if ident:
            chain, parent = [], parents.get(node)
            while parent is not None:
                if parent.get('id'):
                    chain.insert(0, parent.get('id'))
                parent = parents.get(parent)
            ancestors[ident] = chain
        key = None
        if tag == 'title':
            key = (parents[node].get('id') or 'm82630')+'/title'
        elif tag == 'para':
            key = ident
        elif tag == 'item':
            key = parents[node].get('id')+'/item/'+str(list(parents[node]).index(node)+1)
        elif tag == 'media':
            key = ident+'/alt'
        if key:
            keys.append(key)
            roles[key] = {'tag': tag, 'newlines': len(node.findall('.//'+N+'newline'))}
    return keys, roles, ancestors


def load_inputs():
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    t = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    require((m['unit'], m['assignment'], m['module'], m['collection'], m['locale']) ==
            ('A10-preface', 'A10', 'm82630', 'col31130', 'pnb-Arab-PK'), 'Preface scope changed')
    require((t['unit'], t['assignment'], t['module'], t['locale']) ==
            ('A10-preface', 'A10', 'm82630', 'pnb-Arab-PK'), 'Translation scope changed')
    lock = json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
    pinned = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    require((m['commit'], m['tree']) == (pinned['commit'], pinned['tree']), 'Existing source lock mismatch')
    original_path = CANONICAL/'modules/m82630/index.cnxml'
    require((ROOT/m['canonical_local_path']).resolve() == original_path.resolve(), 'Canonical path changed')
    raw = original_path.read_bytes()
    require(len(raw) == m['full_module_bytes'] == m['excerpt_bytes'] == 22483 and
            digest(raw) == m['full_module_sha256'] == m['excerpt_sha256'] == SOURCE_SHA, 'Full source bytes changed')
    require(blob_hash(raw) == m['canonical_git_blob_sha1'], 'Source Git blob changed')
    require(EXCERPT.read_bytes() == (ROOT/m['release_authority_path']).read_bytes() == raw,
            'Entire witness or English release differs')
    require(m['source_excerpt'] == EXCERPT.name and raw.endswith(b'\n'), 'Witness boundary changed')
    require(file_hash(ROOT/m['indonesian_comparison_path']) == m['indonesian_comparison_sha256'], 'Comparison changed')
    source = ET.fromstring(raw)
    require(source.attrib == {'class': 'preface'} and source.find(N+'content').attrib == {'class': 'preface'},
            'Source document/content classes changed')
    require([x.tag for x in source] == [N+'title', N+'metadata', N+'content'], 'Document hierarchy changed')
    keys, roles, ancestors = source_inventory(source)
    require(keys == m['source_text_keys_in_order'] == list(t['source_blocks']) and len(keys) == 87, '87-key coverage/order changed')
    require(roles == m['source_block_roles'] and ancestors == m['source_ancestor_ids'], 'Source role/ancestor map changed')
    require(list(ancestors) == m['source_ids_in_document_order'] and len(ancestors) == 66, '66 source IDs changed')
    require([x.get('id') for x in source.find(N+'content')] == m['content_direct_children_in_source_order'], 'Full content order changed')
    require(t['title'] == t['source_blocks']['m82630/title'] == m['module_title_pnb'], 'Display title mismatch')
    media = source.findall('.//'+N+'media')
    require(len(media) == len(m['images']) == 4, 'Four original images required')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    prepared = []
    for node, spec, filename in zip(media, m['images'], FILENAMES):
        original = CANONICAL/'media'/filename
        target = BASE/'assets/a10'/filename
        require(spec['media_id'] == node.get('id') and spec['source_alt'] == node.get('alt'), 'Source media identity/alt changed')
        require(spec['source_src'] == '../../media/'+filename and spec['source_path'] == 'media/'+filename,
                'Image source path changed')
        require(spec['canonical_local_path'] == original.relative_to(ROOT).as_posix() and
                spec['path'] == target.relative_to(BASE).as_posix() and
                target.resolve().parent == (BASE/'assets/a10').resolve(), 'Unsafe or incorrect image path')
        require(node.find(N+'image').attrib == {'mime-type': spec['mime_type'], 'src': spec['source_src']}, 'Source image attributes changed')
        data = original.read_bytes()
        require(len(data) == spec['bytes'] and digest(data) == spec['sha256'] and blob_hash(data) == spec['git_blob_sha1'], 'Image byte identity changed')
        require(dimensions(data) == (spec['width'], spec['height']), 'Image dimensions changed')
        matches = [row for row in rows if row['relative_path'] == spec['source_path']]
        require(matches == [spec['existing_media_authority_row']], 'Existing media authority row changed')
        require(matches[0]['sha256'] == spec['sha256'] and matches[0]['git_blob_sha1'] == spec['git_blob_sha1'] and
                int(matches[0]['bytes']) == len(data), 'Media row identity differs')
        require(not target.exists() or file_hash(target) == spec['sha256'], 'Refusing to overwrite different existing asset')
        prepared.append((spec, target, data))
    require(m['existing_notice_input_hash_policy'] == HASH_POLICY, 'Notice logical-LF policy changed')
    for item in m['existing_notice_inputs']:
        require(digest((ROOT/item['path']).read_bytes().replace(b'\r\n', b'\n')) == item['sha256'],
                'Existing notice logical-LF hash changed: '+item['path'])
    attribution = m['retained_attribution']
    credit_text = ''.join(source.find('.//*[@id="eip-787"]').itertext())
    require(attribution['original_senior_contributing_authors'] == AUTHORS and
            attribution['source_default_art_credit'] == DEFAULT_CREDIT and
            attribution['source_default_art_credit_paragraph'] == 'eip-787' and
            credit_text.endswith(DEFAULT_CREDIT) and 'limitations provided in the credit' in credit_text,
            'Default credit or its component limits changed')
    return m, t, source, prepared, credit_text


def notice_record(m, prepared, credit_text):
    return {
        'schema': 'a10-retained-component-evidence-v1', 'unit': 'A10-preface',
        'work': 'OpenStax Elementary Algebra 2e', 'module': 'm82630', 'collection': 'col31130', 'commit': m['commit'],
        'manifest_sha256': file_hash(MANIFEST), 'excerpt_sha256': m['excerpt_sha256'],
        'scope': 'Complete m82630 preface and four unchanged original images; no new supply/license audit.',
        'existing_notice_inputs': m['existing_notice_inputs'], 'existing_notice_input_hash_policy': HASH_POLICY,
        'release_notice_verbatim': (BASE/'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
        'original_senior_contributing_authors': AUTHORS,
        'existing_license_statement': m['retained_attribution']['existing_license_statement'],
        'non_endorsement': m['retained_attribution']['non_endorsement'],
        'rights_status': 'Existing audited A10 policy retained; no new component-specific clearance determination.',
        'credit_limit': 'The media authority rows identify bytes and Git blobs, not rights holders or permissions. Named book authors are not relabeled as image creators. Raw-source default art credit and component-specific restrictions are retained, not independently verified as image-specific clearance.',
        'source_default_art_credit': DEFAULT_CREDIT,
        'source_default_art_credit_paragraph': 'eip-787',
        'raw_source_art_attribution_paragraph_verbatim': credit_text,
        'media_authority_manifest': {'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(), 'sha256': file_hash(MEDIA_MANIFEST), 'hash_policy': 'raw bytes; separate from logical-LF existing_notice_inputs'},
        'images': [{**{key: spec[key] for key in ('figure_id','media_id','parent_id','parent_tag','source_path','path','mime_type','sha256','bytes','width','height','git_blob_sha1','source_alt','existing_media_authority_row')},
                    'treatment': 'Original bytes unchanged and unmirrored. Faithful source alt retained separately from a labeled visible-shape accessible override; no source figure number exists.',
                    'component_clearance': 'Not newly assessed; subject to retained component-specific credits and restrictions.'}
                   for spec, target, data in prepared],
        'source_discrepancies': m['source_discrepancies'],
        'whole_book_translation_complete': False,
        'publication_claim_limit': 'Complete-book publication language in the retained Indonesian release NOTICE describes that release, not this Punjabi preface or the whole Punjabi book.'
    }


def prepare():
    m, t, source, prepared, credit_text = load_inputs()
    # All four destinations have been resolved and checked before any write.
    for spec, target, data in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied image differs')
    NOTICES.write_text(json.dumps(notice_record(m, prepared, credit_text), ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Prepared complete A10 preface: four unchanged originals and existing component evidence.')


if __name__ == '__main__':
    prepare()
