"""Prepare the two pinned B10-001 SVG originals and source-specific notices.

Only Git blob reads and local validation. No upstream TeX/TikZ or network runtime.
"""
import hashlib
import json
import re
from pathlib import Path
from prepare_b10_frontmatter import BASE, ROOT, XID, XI, require, digest, file_hash, git, parse, tree, source_path
from b10_001_tex import convert

MANIFEST=BASE/'source-excerpts/manifest-b10-unit-001.json'
TRANSLATION=BASE/'translations/b10-unit-001.json'
EXCERPT=BASE/'source-excerpts/b10-unit-001.ptx'
NOTICES=BASE/'provenance/b10-unit-001-component-notices.json'
OUTPUT=BASE/'reader/b10-unit-001.html'
FROZEN={MANIFEST:'98848df0ae9bda7cea41e05cb42dfbadcda9181588beab3a4a5637c9be239443',
        TRANSLATION:'6581cc29aa051220f91ec342c5642d08ff16203d5292b29948fa3df9595ea0cd',
        EXCERPT:'22d106e2b8f6e456550c292ecbda0f40d528dec139462629a4d3c1de1c844721'}
SLOT_TAGS={'p','title','fn','shortdescription','feedback','h','see','cell'}


def jhash(value):
    return digest(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())


def key(node):
    section=next((a for a in [node]+list(node.iterancestors()) if a.tag=='section' and a.getparent() is not None and a.getparent().tag=='chapter'),None)
    if section is None:return 'ch_intro.ptx#'+source_path(node)
    name={'sec_intro-intro':'sec_intro-intro.ptx','sec_intro-structures':'sec_intro-structures.ptx'}[section.get(XID)]
    return name+'#/section'+source_path(node)[len(source_path(section)):]


def load_inputs():
    for p,h in FROZEN.items():require(file_hash(p)==h,'Frozen input changed: '+p.name)
    m=json.loads(MANIFEST.read_text(encoding='utf-8'));t=json.loads(TRANSLATION.read_text(encoding='utf-8'))
    lock=json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
    require(file_hash(BASE/'sources.lock.json')==m['authority']['lock_raw_sha256'],'Source lock bytes differ')
    raws={}
    for role,lockrole in [('canonical','B10 upstream'),('comparison','B10')]:
        a=m['authority'][role];p=next(x for x in lock['repositories'] if x['role']==lockrole);repo=ROOT/a['local_path']
        require((a['commit'],a['tree'],a['local_path'],a['repository'])==(p['commit'],p['tree'],p['local_path'],p['url']),'Pinned source authority differs')
        require(git(repo,'rev-parse','HEAD').decode().strip()==a['commit'] and git(repo,'rev-parse','HEAD^{tree}').decode().strip()==a['tree'],'Pinned checkout differs')
        for row in [x for x in m['source_files'] if x['role']==role]:
            raw=git(repo,'show',a['commit']+':'+row['repository_path'])
            require(digest(raw)==row['sha256'] and len(raw)==row['bytes'],'Source blob differs')
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_sha1'],'Source Git identity differs')
            require((ROOT/row['local_path']).read_bytes().replace(b'\r\n',b'\n')==raw,'Source checkout logical-LF bytes differ')
            if role=='canonical':raws[Path(row['repository_path']).name]=raw.decode()
    witness=raws['ch_intro.ptx']
    for f in ['sec_intro-intro.ptx','sec_intro-structures.ptx']:
        needle='<xi:include href="./'+f+'"/>';require(witness.count(needle)==1,'Expected active include missing')
        witness=witness.replace(needle,re.sub(r'^<\?xml[^>]+>\s*','',raws[f],count=1))
    require(EXCERPT.read_bytes()==(witness+'\n').encode(),'Full source boundary/LF differs')
    source=parse(EXCERPT.read_bytes())
    require(jhash(tree(source))==m['source_active_tree_sha256'],'Source active tree differs')
    require([key(n) for n in source.iter() if n.tag in SLOT_TAGS]==m['expected_source_keys']==list(t['source_blocks']),'157 source keys/order differ')
    require(len(m['expected_source_keys'])==157 and len(list(source.iter()))==492,'Full unit scope differs')
    for row in m['translation_block_seals']:require(digest(t['source_blocks'][row['key']].encode())==row['sha256'],'Translation block changed')
    for field,seal in m['original_field_seals'].items():require(jhash(t[field])==seal,'Original field changed')
    a=m['authority']['canonical'];repo=ROOT/a['local_path']
    for path,spec in m['metadata_dependencies'].items():
        raw=git(repo,'show',a['commit']+':'+path)
        require(digest(raw)==spec['sha256'] and len(raw)==spec['bytes'],'Source metadata dependency differs')
    for row in m['existing_notice_policy']['notice_inputs']:
        raw=(ROOT/row['path']).read_bytes()
        require(digest(raw)==row['raw_sha256'] and digest(raw.replace(b'\r\n',b'\n'))==row['logical_lf_sha256'],'Existing notice changed')
    prepared=[]
    for spec in m['declared_assets']:
        target=BASE/spec['planned_reader_path']
        require(target.resolve().parent==(BASE/'assets/b10').resolve() and target.name=='b10-unit-001-'+spec['id']+'.svg','Unsafe asset target')
        raw=git(repo,'show',a['commit']+':'+spec['repository_path']);svg=parse(raw)
        require(digest(raw)==spec['sha256'] and len(raw)==spec['bytes'],'Canonical SVG differs')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==spec['git_blob_sha1'],'SVG Git identity differs')
        require(svg.get('width')==spec['width'] and svg.get('height')==spec['height'] and svg.get('viewBox')==spec['viewBox'],'SVG dimensions differ')
        require(not any(v for n in svg.iter() for k,v in n.attrib.items() if k.endswith('href') and not v.startswith('#')),'External SVG dependency')
        require(not target.exists() or file_hash(target)==spec['sha256'],'Refusing to replace a different asset')
        prepared.append((spec,target,raw))
    require(len(prepared)==2,'Two original graphs required')
    return m,t,source,prepared


def math_records(m):
    records=[]
    for i,s in enumerate(m['tex_slots'],1):
        _,r=convert(s['raw_tex'],s['source_tag']=='me')
        records.append(dict(r,number=i,source_path=s['source_path'],owner_key=s['owner_key'],token=s['token'],source_tag=s['source_tag'],source_attributes=s['source_attributes']))
    require(len(records)==105 and len({r['source_tex'] for r in records})==78,'Math scope changed')
    return records


def notice_record(m,prepared):
    return {'schema':'b10-retained-component-evidence-v1','unit':'B10-001',
        'work':'Discrete Mathematics: An Open Introduction','edition':'Fourth Edition','author':'Oscar Levin',
        'canonical':m['authority']['canonical'],'indonesian_comparison':m['authority']['comparison'],
        'manifest_sha256':file_hash(MANIFEST),'excerpt_sha256':file_hash(EXCERPT),'translation_sha256':file_hash(TRANSLATION),
        'scope':'Entire Chapter0: both sections, seven subsections and all six exercises. Not a completed textbook.',
        'source_specific_license':'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International','source_copyright':'2013–2025 Oscar Levin',
        'existing_notice_policy':m['existing_notice_policy'],
        'existing_notice_input_hash_policy':'Retained raw and logical CRLF-to-LF hashes checked separately; no source notice rewritten.',
        'retained_indonesian_license_verbatim':(BASE/'provenance/discrete-mathematics-open-introduction-id/LICENSE').read_text(encoding='utf-8'),
        'retained_third_party_notices_verbatim':(BASE/'provenance/discrete-mathematics-open-introduction-id/THIRD_PARTY_NOTICES.md').read_text(encoding='utf-8'),
        'rights_status':'Existing active fourth-edition CC BY-NC-SA 4.0 and stale root BY-SA 4.0 discrepancy retained; no new clearance asserted.',
        'component_limit':'Existing specific notices remain binding; byte/blob evidence does not independently establish image-specific permission.',
        'non_endorsement':'No endorsement by Oscar Levin or University of Northern Colorado is implied.',
        'images':[{**{k:s[k] for k in ['id','repository_path','local_path','sha256','bytes','width','height','viewBox','git_blob_sha1']},'path':target.relative_to(BASE).as_posix(),'source_owner':m['source_image_owners'][i],'treatment':'Pinned Git SVG bytes unchanged, unmirrored and uncropped; no TikZ execution.'} for i,(s,target,raw) in enumerate(prepared)],
        'inert_source_macros':m['source_macros'],'inert_metadata_dependencies':m['metadata_dependencies'],
        'math_conversion':{'parser':'b10_001_tex.py','parser_sha256':file_hash(BASE/'scripts/b10_001_tex.py'),'scope':'Only observed limited grammar; unknown syntax fails closed. Not universal LaTeX support.','source_mathml_count':0,'derived_mathml_count':105,'unique_raw_tex_forms':78,
            'browser_presentation_normalization':{'natural_numbers':'Exact source \\N and its inert mathbb N macro are retained. Derived mi uses U+2115 DOUBLE-STRUCK CAPITAL N with mathvariant=normal, not plain N with the non-Core double-struck attribute. Each changed encoding is bound in the reversible token ledger.','source_text_spacing':'Exact source text{ and } retains both spaces. Scoped mtext white-space:pre preserves those spaces in HTML MathML rendering. No source text or math meaning changed.','standard':'https://www.w3.org/TR/mathml-core/#mathematical-alphanumeric-symbols','motivation':'Parent browser review found collapsed mtext edge spaces and plain italic N despite exact DOM text/mathvariant; these are bounded derived-presentation fixes.'},
            'records':math_records(m)},
        'runtime':'Locally authored offline static HTML/MathML only. No upstream code, TeX/TikZ, PreTeXt/Runestone runtime, analytics, network scripts or grading execution.',
        'comparison_changes':'Indonesian graph-description/math-language/spelling changes remain comparison evidence, not substituted canonical content.',
        'whole_book_translation_complete':False}


def prepare():
    m,t,source,prepared=load_inputs()
    for spec,target,raw in prepared:
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(raw)
        require(file_hash(target)==spec['sha256'],'Prepared image differs')
    NOTICES.write_text(json.dumps(notice_record(m,prepared),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared B10-001: two exact SVG originals; 105 source-bound math ledgers; retained notices.')


if __name__=='__main__':prepare()
