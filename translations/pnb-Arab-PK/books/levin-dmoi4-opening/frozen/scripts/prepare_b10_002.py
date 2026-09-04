"""Prepare bounded B10 Section1.1 evidence; reads pinned Git data, never upstream code."""
import hashlib
import json
import re
from pathlib import Path
from prepare_b10_frontmatter import BASE, ROOT, XID, XI, require, digest, file_hash, git, parse, tree, source_path
from b10_002_tex import convert, FALLBACK_REASON, FALLBACK_STANDARD
from b10_002_math_expected import expected

MANIFEST=BASE/'source-excerpts/manifest-b10-unit-002.json'
TRANSLATION=BASE/'translations/b10-unit-002.json'
EXCERPT=BASE/'source-excerpts/b10-unit-002.ptx'
CACHE=BASE/'source-excerpts/b10-unit-002-webwork.xml'
NOTICES=BASE/'provenance/b10-unit-002-component-notices.json'
OUTPUT=BASE/'reader/b10-unit-002.html'
RECEIPT=BASE/'qa/structural-b10-002.json'
CHAPTER='source/ch_logic.ptx'
SECTION='source/sec_logic-statements.ptx'
CACHEFILE='generated-assets/rs/webwork/webwork-representations.xml'
FROZEN={MANIFEST:'68bd9bb7158886a20ecf01df0420e8f3b4efebe3b09e0842240085c53e24e8ce',TRANSLATION:'ec9666ae9313c9a1d891c709e7e476fe82455ff44f14d7dde24761ebb72995ad',EXCERPT:'1fce081a82dc8d22fa044da96fe8ba309fe4b0a4db7ab9835b0cf7f63e280009',CACHE:'1c8947d8d695deca514e0e6952e6b8ce96938cffb02bb19e15feb314d769bf7c'}
FIXED={'p','title','fn','shortdescription','h','see','cell','caption'}
COMPONENT_RECEIPT=BASE/'provenance/b10-unit-002-components/acquisition.json'
COMPONENT_RECEIPT_SHA='193867036f31da9ddb10ce1b89f47a08078d9d7a7e643098176fc6d462b2ed51'
CONDITIONAL={'li','response','premise','description','usage','feedback'}
INLINE={'em','q','term','alert','foreign'}

def jhash(value):return digest(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
def blockable(e):return e.tag in FIXED or (e.tag in CONDITIONAL and (bool((e.text or '').strip()) or any((c.tail or '').strip() or c.tag in INLINE|{'m','me'} for c in e)))
def json_read(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,'Duplicate JSON key '+k);d[k]=v
        return d
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique)

def retained_policy():
    m=json_read(BASE/'source-excerpts/manifest-b10-frontmatter.json')
    policy=m['existing_notice_policy']
    for row in policy['notice_inputs']:
        raw=(ROOT/row['path']).read_bytes()
        require(digest(raw)==row['raw_sha256'] and digest(raw.replace(b'\r\n',b'\n'))==row['logical_lf_sha256'],'Retained notice changed')
    current=json.loads(json.dumps(policy))
    current['components']='Current B10-002 contains six authored WeBWorK owners and six pinned static cache records: four remote OPL references and two local PG sources. Retain their component notices and exact identity evidence. No PreTeXt/Runestone runtime, grading or randomization is included.'
    current['historical_scope_context']={'source_manifest':'source-excerpts/manifest-b10-frontmatter.json','components_verbatim':policy['components'],'qualification':'The inherited zero-WeBWorK sentence concerned the earlier proposed opening/Chapter0, not B10-002. It is retained here solely as historical evidence and is not the current component inventory.'}
    return current

def component_witnesses(m):
    require(file_hash(COMPONENT_RECEIPT)==COMPONENT_RECEIPT_SHA,'Exact selected component acquisition receipt changed')
    receipt=json_read(COMPONENT_RECEIPT)
    require(len(receipt['files'])==7,'Seven selected component witnesses required')
    files=[]
    for source in receipt['files']:
        path=BASE/source['local_path']
        require(path.resolve().is_relative_to((BASE/'provenance/b10-unit-002-components').resolve()),'Component path escaped scoped package')
        raw=path.read_bytes()
        require((len(raw),digest(raw),hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())==(source['bytes'],source['sha256'],source['git_blob_sha1']),'Exact component bytes/blob differ')
        row={k:source[k] for k in ['kind','repository','commit','repository_path','local_path','bytes','sha256','git_blob_sha1']}
        if path.name=='OPL_LICENSE':row['verbatim_notice']=raw.decode('utf-8')
        else:
            row['source_header_verbatim']=raw.decode('utf-8').split('DOCUMENT();',1)[0]
            require('## Author(Oscar Levin)' in row['source_header_verbatim'] and '## Institution(University of Northern Colorado)' in row['source_header_verbatim'],'Source PG attribution header differs')
        files.append(row)
    bindings=[]
    for b in m['cached_static_bindings']:
        source=b['source'] or b['parse_text_source']
        row=next(x for x in files if x['repository_path']==source)
        bindings.append({'owner':b['owner'],'cache_xml_id':b['cache_xml_id'],'seed':b['seed'],'repository_path':source,'local_path':row['local_path'],'sha256':row['sha256']})
    return {'acquisition_path':COMPONENT_RECEIPT.relative_to(BASE).as_posix(),'acquisition_sha256':COMPONENT_RECEIPT_SHA,
        'scope':'Seven exact-byte witnesses: root OPL_LICENSE, four selected original English OPL PG files and two original local DMOI PG files. Not the complete OPL library/public provenance package.',
        'notice_policy':'Retain the existing OPL default CC BY-NC-SA 3.0 Unported notice and its unless-otherwise-indicated/alternative-license clauses verbatim. Existing active fourth-edition book notices remain separate; this is not a new rights assessment.',
        'execution_policy':'Witness text is inert and never executed; four original OPL files were fetched at the already pinned OPL commit, two local PG blobs copied from pinned DMOI Git. No claim that a cache snapshot exhausts its source variants.',
        'files':files,'source_cache_associations':bindings}

def load_inputs():
    for p,h in FROZEN.items():require(file_hash(p)==h,'Frozen B10-002 input changed: '+p.name)
    m,t=json_read(MANIFEST),json_read(TRANSLATION)
    require((m['unit'],t['unit'],t['locale'])==('B10-002','B10-002','pnb-Arab-PK'),'Wrong scope')
    lock=json_read(BASE/'sources.lock.json');require(file_hash(BASE/'sources.lock.json')==m['authority']['lock_raw_sha256'],'Lock differs')
    raws={}
    for role,lockrole in [('canonical','B10 upstream'),('comparison','B10')]:
        a=m['authority'][role];p=next(x for x in lock['repositories'] if x['role']==lockrole);repo=ROOT/a['local_path']
        require((a['commit'],a['tree'],a['local_path'],a['repository'])==(p['commit'],p['tree'],p['local_path'],p['url']),'Authority differs')
        require(git(repo,'rev-parse','HEAD').decode().strip()==a['commit'] and git(repo,'rev-parse','HEAD^{tree}').decode().strip()==a['tree'],'Pinned checkout differs')
        for row in [x for x in m['source_files']+m['metadata_files'] if x['role']==role]:
            raw=git(repo,'show',a['commit']+':'+row['repository_path'])
            require(digest(raw)==row['sha256'] and len(raw)==row['bytes'],'Pinned source bytes differ')
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_sha1'],'Git blob identity differs')
            require((repo/row['repository_path']).read_bytes().replace(b'\r\n',b'\n')==raw,'Selected checkout logical-LF differs')
            if role=='canonical':raws[row['repository_path']]=raw
    rawchapter=raws[CHAPTER].decode();marker='<xi:include href="./sec_logic-statements.ptx"/>'
    require(rawchapter.count(marker)==1,'Chapter boundary differs')
    prefix=rawchapter[:rawchapter.index(marker)]
    sec=raws[SECTION].decode()
    for row in m['includes']:
        needle='<xi:include href="'+row['href']+'"/>'
        require(sec.count(needle)==1,'Active include differs')
        sec=sec.replace(needle,re.sub(r'^<\?xml[^>]+>\s*','',raws[row['source']].decode(),count=1))
    witness=prefix+re.sub(r'^<\?xml[^>]+>\s*','',sec,count=1)+'\n</chapter>\n'
    require(EXCERPT.read_bytes()==witness.encode() and jhash(tree(parse(witness.encode())))==m['source_active_tree_sha256'],'Full source witness boundary differs')
    roots={CHAPTER:parse((prefix+'</chapter>').encode())}
    for f in [SECTION,'source/practice/logic-statements.ptx','source/exercises/logic-statements.ptx']:roots[f]=parse(raws[f])
    fullcache=parse(raws[CACHEFILE]);cache=parse(CACHE.read_bytes())
    require(len(cache)==6 and [tree(c) for c in cache]==[tree(c) for c in list(fullcache)[:6]],'Exact six cache records differ')
    require([jhash(tree(c)) for c in cache]==m['cache_record_tree_sha256'],'Cache tree hashes differ')
    selected=list(roots.items())+[(CACHEFILE,c.find('static')) for c in cache]
    nodes={f+'#'+source_path(e):e for f,r in selected for e in r.iter()}
    keys={e:k for k,e in nodes.items()}
    ledger=[dict(source_path=f+'#'+source_path(e),tag=e.tag,attributes=dict(e.attrib),own_text=e.text,tail=e.tail,child_paths=[f+'#'+source_path(c) for c in e]) for f,r in selected for e in r.iter()]
    require(ledger==m['source_structure_ledger'] and len(ledger)==1602,'Exact source-file structure ledger differs')
    actualkeys=[keys[e] for f,r in selected for e in r.iter() if blockable(e)]
    require(actualkeys==m['expected_source_keys']==list(t['source_blocks']) and len(actualkeys)==559,'Full559 slot order differs')
    for k,h in m['translation_block_seals'].items():require(digest(t['source_blocks'][k].encode())==h,'Frozen translation differs')
    for n in t['original_notes']:require(jhash(n)==m['original_note_seals'][n['id']],'Original note differs')
    require(jhash(t['terminology_choices'])==m['original_terms_seal'],'Term choices differ')
    require(len(m['declared_assets'])==0,'No images in selected source')
    for b in m['source_blocks']:
        require(jhash(tree(nodes[b['key']]))==b['source_tree_sha256'],'Source block tree differs')
        for s in b['slots']:
            n=nodes[s['source_path']]
            require(n.tag==s['source_tag'] and dict(n.attrib)==s['source_attributes'],'Slot source differs')
            if s['kind']=='tex':require(n.text==s['raw_tex'] and digest(n.text.encode())==s['tex_sha256'],'Source TeX differs')
    for binding,c in zip(m['cached_static_bindings'],cache):
        owner=nodes[binding['owner']];static=c.find('static');pg=c.find('pg')
        require((c.get('ww-id'),c.get(XID),static.get('seed'))==(binding['cache_ww_id'],binding['cache_xml_id'],binding['seed']),'Cache owner/seed differs')
        require(jhash(tree(static))==binding['static_tree_sha256'] and digest((pg.text or '').encode())==binding['inert_pg_text_sha256'],'Cache static/PG differs')
        require(owner.get('source')==binding['source'],'Authored cache reference differs')
        if binding['source']:require(pg.get('source')==static.get('source')==binding['source'],'External static identity differs')
        else:require((pg.text or '').strip()==raws[binding['parse_text_source']].decode().strip(),'Inert local PG identity differs')
    require(parse(raws['source/bookinfo.ptx']).findtext('macros')==m['source_macros'],'Inert macros differ')
    retained_policy();component_witnesses(m)
    return m,t,roots,cache,nodes,keys,raws

def math_records(m):
    rows=[]
    for i,s in enumerate(m['tex_slots'],1):
        _,r=convert(s['raw_tex'],s['source_tag']=='me')
        require(r['tree']==expected(s['raw_tex']),'Handwritten source math fixture differs')
        rows.append(dict(r,number=i,source_path=s['source_path'],owner_key=s['owner_key'],token=s['token'],source_tag=s['source_tag'],source_attributes=s['source_attributes']))
    require(len(rows)==337 and len({r['source_tex'] for r in rows})==123,'337owners/123rawforms required')
    require(sum(r['status']=='derived-mathml' for r in rows)==336 and sum(r['status']=='source-tex-fallback' for r in rows)==1,'Reviewed/fallback coverage differs')
    return rows

def notice_record(m):
    return {'schema':'b10-retained-component-evidence-v1','unit':'B10-002','work':'Discrete Mathematics: An Open Introduction','edition':'Fourth Edition','author':'Oscar Levin',
        'canonical':m['authority']['canonical'],'indonesian_comparison':m['authority']['comparison'],
        'manifest_sha256':file_hash(MANIFEST),'excerpt_sha256':file_hash(EXCERPT),'cache_excerpt_sha256':file_hash(CACHE),'translation_sha256':file_hash(TRANSLATION),
        'scope':'Full Chapter1 opening and complete Section1.1 with both active exercise includes; six separately identified fixed cached snapshots. Not the whole chapter or book.',
        'source_specific_license':'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International','source_copyright':'2013–2025 Oscar Levin',
        'existing_notice_policy':retained_policy(),'existing_notice_input_hash_policy':'Existing raw and logical CRLF-to-LF hashes checked separately in memory; no notice rewritten.',
        'selected_component_witnesses':component_witnesses(m),
        'retained_indonesian_license_verbatim':(BASE/'provenance/discrete-mathematics-open-introduction-id/LICENSE').read_text(encoding='utf-8'),
        'retained_third_party_notices_verbatim':(BASE/'provenance/discrete-mathematics-open-introduction-id/THIRD_PARTY_NOTICES.md').read_text(encoding='utf-8'),
        'rights_status':'Existing active fourth-edition CC BY-NC-SA 4.0 and stale root BY-SA 4.0 discrepancy retained; no new clearance asserted.',
        'component_limit':'Existing component restrictions remain binding. Cache or blob identity is not new permission or a claim covering all generated variants.',
        'non_endorsement':'No endorsement by Oscar Levin or University of Northern Colorado is implied.','images':[],
        'inert_source_macros':m['source_macros'],'inert_metadata_dependencies':m['metadata_files'],
        'cached_static_bindings':m['cached_static_bindings'],'cache_record_tree_sha256':m['cache_record_tree_sha256'],
        'cache_display_policy':'Authored exercise source order remains intact. Six original webwork owners link to separately appended, ordered, fixed source-cache snapshots and exact return links. No engine, randomization or grading is run.',
        'math_conversion':{'parser':'b10_002_tex.py','parser_sha256':file_hash(BASE/'scripts/b10_002_tex.py'),'fixtures':'b10_002_math_expected.py','fixtures_sha256':file_hash(BASE/'scripts/b10_002_math_expected.py'),'scope':'Strict finite observed grammar only; unknown commands fail closed. Handwritten source mathematics fixtures do not import the mapper. Not universal LaTeX support.','source_mathml_count':0,'source_tex_owners':337,'derived_mathml_count':336,'source_tex_fallback_count':1,'unique_raw_tex_forms':123,'fallback_reason':FALLBACK_REASON,'fallback_standard':FALLBACK_STANDARD,'spacing_policy':'All raw whitespace survives exact TeX/annotation and reversible token ledgers; literal mtext uses white-space:pre. ASCII minus maps to U+2212 with token evidence.','records':math_records(m)},
        'runtime':'Locally authored offline static reader only; no upstream code, Perl/PG, TeX, engine, network script, analytics, randomization or grading.',
        'source_error_policy':'Frozen incorrect source flags, incomplete predicate and false cached parity solution remain source-attributed with explicit separately original warning links; no silently corrected source answer.',
        'whole_book_translation_complete':False}

def prepare():
    m,*_=load_inputs()
    NOTICES.write_text(json.dumps(notice_record(m),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared B10-002:559 keys,337 exact TeX owners,336 derived MathML/1 explicit fallback,6 fixed cache records; no runtime.')

if __name__=='__main__':prepare()
