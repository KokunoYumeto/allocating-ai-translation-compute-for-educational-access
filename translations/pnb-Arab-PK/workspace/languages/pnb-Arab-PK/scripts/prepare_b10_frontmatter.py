"""Prepare only the pinned B10 frontmatter's two original PNGs and retained notices.

Reads Git blobs as data. Never runs upstream code, resolves XInclude, or audits rights.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from lxml import etree as E
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE/'source-excerpts/manifest-b10-frontmatter.json'
TRANSLATION = BASE/'translations/b10-frontmatter.json'
EXCERPT = BASE/'source-excerpts/b10-frontmatter.ptx'
NOTICES = BASE/'provenance/b10-frontmatter-component-notices.json'
XID = '{http://www.w3.org/XML/1998/namespace}id'
XI = '{http://www.w3.org/2001/XInclude}include'
CANONICAL_COMMIT = '82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799'
COMPARISON_COMMIT = 'e94905932301e699b7c4d44e88ec54e972b886b6'
WITNESS_SHA = '997ed1b17cf0fd67b9ef8a4c4e3a5ebb598630005beeb93aaddd64dad2fc61cb'
SLOT_TAGS = {'p','title','shortdescription','line','personname','department','institution','date','year','holder','shortlicense'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes())


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def parse(raw, comments=False):
    return E.fromstring(raw, E.XMLParser(remove_comments=not comments, resolve_entities=False, no_network=True))


def tree(node):
    return [node.tag, dict(node.attrib), node.text, [[tree(c), c.tail] for c in node]]


def source_path(node):
    parent = node.getparent()
    if parent is None:
        return '/'+node.tag
    index = 1+sum(s.tag == node.tag for s in node.itersiblings(preceding=True))
    return source_path(parent)+'/'+node.tag+'['+str(index)+']'


def source_keys(roots):
    keys = ['bookinfo.ptx#/docinfo/blurb[1]/@shelf','bookinfo.ptx#/docinfo/blurb[1]']
    keys += ['bookinfo.ptx#/docinfo/rename['+str(i)+']' for i in range(1,5)]
    keys += ['dmoi.ptx#/pretext/book[1]/'+tag+'[1]' for tag in ('title','subtitle')]
    keys += ['frontmatter.ptx#'+source_path(e) for e in roots['frontmatter.ptx'].iter() if e.tag in SLOT_TAGS]
    return keys


def load_inputs():
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    t = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    require((m['unit'],m['assignment'],m['locale']) == ('B10-frontmatter','B10','pnb-Arab-PK'), 'Manifest scope changed')
    require((t['unit'],t['assignment'],t['locale']) == ('B10-frontmatter','B10','pnb-Arab-PK'), 'Translation scope changed')
    lock = json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
    roots = {}
    for role, lockrole, commit in [('canonical','B10 upstream',CANONICAL_COMMIT),('comparison','B10',COMPARISON_COMMIT)]:
        authority = m['authority'][role]
        pinned = next(x for x in lock['repositories'] if x['role'] == lockrole)
        require((authority['commit'],authority['tree'],authority['local_path'],authority['repository']) ==
                (commit,pinned['tree'],pinned['local_path'],pinned['url']), 'Source lock differs: '+role)
        repo = ROOT/authority['local_path']
        require(git(repo,'rev-parse','HEAD').decode().strip() == commit, 'Wrong source checkout')
        require(git(repo,'rev-parse','HEAD^{tree}').decode().strip() == authority['tree'], 'Wrong source tree')
        for row in (r for r in m['source_files'] if r['role'] == role):
            require(row['commit'] == commit and row['path'] in ('source/dmoi.ptx','source/bookinfo.ptx','source/frontmatter.ptx','source/assets/tikz-defs.tex'), 'Unexpected source input')
            raw = git(repo,'show',commit+':'+row['path'])
            require(digest(raw) == row['sha256'] and len(raw) == row['bytes'], 'Source Git bytes differ')
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob_sha1'], 'Source blob differs')
            require((ROOT/row['local_path']).read_bytes().replace(b'\r\n',b'\n') == raw, 'Selected source logical-LF bytes differ')
            if role == 'canonical' and row['path'].endswith('.ptx'):
                roots[Path(row['path']).name] = parse(raw)
    witness = EXCERPT.read_bytes()
    require(len(witness) == m['excerpt_bytes'] == 16704 and digest(witness) == m['excerpt_sha256'] == WITNESS_SHA, 'Frozen witness differs')
    source = parse(witness)
    require(tree(source.find('docinfo')) == tree(roots['bookinfo.ptx']), 'Full docinfo missing')
    require(tree(source.find('book/frontmatter')) == tree(roots['frontmatter.ptx']), 'Full frontmatter missing')
    for tag in ('title','subtitle'):
        require(tree(source.find('book/'+tag)) == tree(roots['dmoi.ptx'].find('book/'+tag)), 'Book '+tag+' differs')
    require([e.tag for e in source] == ['docinfo','book'] and [e.tag for e in source.find('book')] == ['title','subtitle','frontmatter'], 'Source boundary differs')
    keys = source_keys(roots)
    require(len(keys) == 50 and keys == m['source_keys'] == list(t['source_blocks']), 'Exact 50-key coverage/order differs')
    require([e.get(XID) for e in source.iter() if e.get(XID)] == ['dmoi4','frontmatter','preface','pref_editions'], 'Four source IDs differ')
    require(len(list(source.iter(XI))) == 1 and source.find('.//'+XI).attrib == {'href':'assets/tikz-defs.tex','parse':'text'}, 'Inert dependency differs')
    for row in m['existing_notice_policy']['notice_inputs']:
        raw = (ROOT/row['path']).read_bytes()
        require(digest(raw) == row['raw_sha256'] and digest(raw.replace(b'\r\n',b'\n')) == row['logical_lf_sha256'], 'Existing notice hashes differ')
    prepared = []
    require([x['id'] for x in m['images']] == ['cover4','qrcode'], 'Two source images required')
    for spec in m['images']:
        name = spec['id']+'.png'
        original = ROOT/'downloads/upstream/discrete-book/assets/images'/name
        target = BASE/'assets/b10'/name
        require((ROOT/spec['local_path']).resolve() == original.resolve() and spec['planned_reader_path'] == 'assets/b10/'+name, 'Image path differs')
        require(target.resolve().parent == (BASE/'assets/b10').resolve(), 'Unsafe target')
        raw = original.read_bytes()
        require(digest(raw) == spec['sha256'] and len(raw) == spec['bytes'], 'Original image differs')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == spec['git_blob_sha1'], 'Image Git blob differs')
        with Image.open(original) as im:
            require(im.size == (spec['width'],spec['height']), 'Image dimensions differ')
        require(not target.exists() or file_hash(target) == spec['sha256'], 'Refusing to overwrite a different image')
        prepared.append((spec,target,raw))
    return m,t,source,roots,prepared


def notice_record(m, prepared):
    return {
        'schema':'b10-retained-component-evidence-v1','unit':'B10-frontmatter',
        'work':'Discrete Mathematics: An Open Introduction','edition':'Fourth Edition','author':'Oscar Levin',
        'canonical':m['authority']['canonical'],'indonesian_comparison':m['authority']['comparison'],
        'manifest_sha256':file_hash(MANIFEST),'excerpt_sha256':file_hash(EXCERPT),'translation_sha256':file_hash(TRANSLATION),
        'scope':'Complete canonical docinfo/title/frontmatter; two unchanged originals; no new rights or supply audit.',
        'source_specific_license':'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International',
        'source_copyright':'2013–2025 Oscar Levin',
        'existing_notice_policy':m['existing_notice_policy'],
        'existing_notice_input_hash_policy':'Existing raw and logical CRLF-to-LF SHA-256 values are both retained and checked. No text normalization is written back.',
        'retained_indonesian_license_verbatim':(BASE/'provenance/discrete-mathematics-open-introduction-id/LICENSE').read_text(encoding='utf-8'),
        'retained_third_party_notices_verbatim':(BASE/'provenance/discrete-mathematics-open-introduction-id/THIRD_PARTY_NOTICES.md').read_text(encoding='utf-8'),
        'rights_status':'Existing active fourth-edition CC BY-NC-SA 4.0 and stale root BY-SA 4.0 discrepancy retained; no new clearance asserted.',
        'component_limit':'Inherited book components remain subject to more specific notices; byte/blob evidence does not independently establish rights or image-specific permission.',
        'non_endorsement':'No endorsement by Oscar Levin or University of Northern Colorado is implied.',
        'images':[{**{k:s[k] for k in ('id','source_key','source_attributes','local_path','repository_path','sha256','bytes','width','height','git_blob_sha1','source_alt','source_alt_owner')},'path':target.relative_to(BASE).as_posix(),'treatment':'Canonical original unchanged, unmirrored and uncropped; original accessible description separately identified. QR payload not decoded.'} for s,target,data in prepared],
        'inert_dependency':m['construction']['unresolved_include'],
        'runtime':'No upstream TeX, PreTeXt/Runestone runtime, analytics, grading or external script executed or copied.',
        'comparison_additions':'Indonesian added colophon, URLs, initialism and replacement QR are comparison-edition changes, not canonical frontmatter.',
        'whole_book_translation_complete':False
    }


def prepare():
    m,t,source,roots,prepared = load_inputs()
    for spec,target,data in prepared:
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied image differs')
    NOTICES.write_text(json.dumps(notice_record(m,prepared),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared B10 frontmatter: two exact original PNGs, retained notices, inert TeX dependency.')


if __name__ == '__main__':
    prepare()
