"""Independent structure, current-input, PDF and release-payload checks."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_html(s):
    s=s.replace('<!doctype html>','')
    s=re.sub(r'<(meta|link|img|br)(\s[^<>]*?)?\s*/?>',lambda m:m.group(0).rstrip('/>')+'/>',s)
    return ET.fromstring(s)

def save(p,v):
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    checks=[]
    def check(condition,name):
        if not condition: raise AssertionError(name)
        checks.append(name)
    source=ET.parse(ROOT/'source/a20-preface.cnxml').getroot()
    original=json.loads((ROOT/'source/recovered-translation.json').read_text(encoding='utf-8'))
    target=json.loads((ROOT/'source/a20-preface.translation.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'source/recovered-manifest.json').read_text(encoding='utf-8'))
    markup=(ROOT/'index.html').read_text(encoding='utf-8')
    doc=parse_html(markup)
    article=doc.find('.//*[@id="a20-preface-source"]')
    source_ids=[x.attrib['id'] for x in source.iter() if 'id' in x.attrib]
    html_ids=[x.attrib['id'] for x in article.iter() if 'id' in x.attrib and x is not article]
    check(len(source_ids)==66,'66_source_ids')
    check(html_ids==source_ids,'source_id_order_preserved')
    check(target['source_blocks']==original['source_blocks'],'all_89_faithful_source_blocks_unchanged')
    keys=[x.get('data-source-key') for x in article.iter() if x.get('data-source-key')]
    check(keys==manifest['source_text_keys_in_order'],'89_owner_keys_in_exact_order')
    for node in article.iter():
        key=node.get('data-source-key')
        if not key or key.endswith('/alt'):
            continue
        actual=deepcopy(node)
        for child in actual.findall('.//span[@class="inline-source-media"]'):
            # Source image occupies one mixed-content slot; renderer advice is not translation.
            parent=next(p for p in actual.iter() if child in list(p))
            at=list(parent).index(child)
            tail=child.tail or ''
            parent.remove(child)
            if at:
                previous=parent[at-1]
                previous.tail=(previous.tail or '')+tail
            else:
                parent.text=(parent.text or '')+tail
        expected=parse_html('<fragment>'+target['source_blocks'][key].replace('{{child:0}}','')+'</fragment>')
        check(''.join(actual.itertext())==''.join(expected.itertext()),'rendered_source_text_exact:'+key)
    check(len(list(source.iter()))==194,'194_source_elements_in_frozen_cnxml')
    check(sum(x.tag in ('em','strong') for x in article.iter())==38,'38_source_emphasis_nodes')
    check(sum(x.tag=='br' for x in article.iter())==27,'27_source_linebreaks')
    check(sum(x.tag=='li' for x in article.iter())==25,'25_source_list_items')
    check(sum(x.tag=='p' and x.get('data-source-key') is not None for x in article.iter())==33,'33_source_paragraphs')
    check(sum(x.get('data-source-tag')=='section' for x in article.iter())==26,'26_source_sections')
    check(doc.get('lang')=='pnb-Arab-PK' and doc.get('dir')=='rtl','locale_and_rtl')
    check(not re.search(r'[\ufffd\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069]',markup),'no_replacement_gurmukhi_or_bidi_controls')
    check('دو رقمی قضیہ' not in markup and 'دو رکنی قضیہ' in markup,'urdu_binomial_bridge_corrected')
    all_ids=[x.get('id') for x in doc.iter() if x.get('id')]
    check(len(all_ids)==len(set(all_ids)),'no_duplicate_html_ids')
    for node in doc.iter():
        if node.get('href','').startswith('#'):
            check(node.get('href')[1:] in all_ids,'fragment_target:'+node.get('href'))
        for attr in ('src','href'):
            val=node.get(attr)
            if val and not urlsplit(val).scheme and not val.startswith('#'):
                target_path=ROOT/unquote(val.split('#')[0])
                check(target_path.is_file(),'local_resource:'+val)
    for image in manifest['images']:
        fp=ROOT/image['path']
        check(digest(fp)==image['sha256'],'canonical_asset_hash:'+image['path'])
        check(fp.stat().st_size==image['bytes'],'canonical_asset_bytes:'+image['path'])
    for section in ('bridge_before_html','bridge_after_html'):
        bridge=parse_html('<wrapper>'+target[section].replace(' — ',' - ')+'</wrapper>')[0]
        check(bridge.get('id') not in [x.get('id') for x in article.iter()],'bridge_outside_source:'+section)
    for node in article.iter():
        key=node.get('data-source-key')
        if key and key.endswith('/alt'):
            check(node.get('data-source-alt')==target['source_blocks'][key],'faithful_alt_trace:'+key)
            check(node.get('aria-describedby') in all_ids,'alt_note_target:'+key)
    # Deterministic HTML/source output replay, not a claim about PDF timestamps.
    before={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'index.html',ROOT/'source/a20-preface.translation.json']}
    subprocess.run([sys.executable,str(ROOT/'scripts/build_reader.py')],check=True,capture_output=True)
    check(all(digest(ROOT/k)==v for k,v in before.items()),'deterministic_html_and_translation_replay')
    pdf=PdfReader(ROOT/'output/pdf/a20-preface-shahmukhi.pdf')
    texts=[p.extract_text() for p in pdf.pages]
    check(len(pdf.pages)>0,'pdf_has_pages')
    check(all(t.strip() for t in texts),'pdf_no_blank_text_pages')
    check('/StructTreeRoot' in pdf.trailer['/Root'],'pdf_structure_tree_present')
    check('/MarkInfo' in pdf.trailer['/Root'],'pdf_mark_info_present')
    check(any('Lynn Marecek' in t for t in texts),'pdf_original_author_searchable')
    normalized=[unicodedata.normalize('NFKC',t) for t in texts]
    check(any('دیباچہ' in t for t in normalized),'pdf_shahmukhi_title_searchable_after_NFKC')
    check(all('\ufffd' not in t for t in texts),'pdf_no_replacement_character')
    check(all('\x00' not in t for t in texts),'pdf_no_null_character')
    resources=[]
    for i,p in enumerate(pdf.pages,1):
        check(abs(float(p.mediabox.width)-595.3)<2 and abs(float(p.mediabox.height)-841.9)<2,'pdf_A4_page:'+str(i))
        resources.append({'page':i,'text_characters':len(texts[i-1]),'bytes_width':float(p.mediabox.width),'bytes_height':float(p.mediabox.height)})
    check('file:///' not in ''.join(texts),'no_local_file_uri_in_pdf_text')
    # No source mathematical objects or exercise credit is inferred from a preface.
    cnt=Counter(x.tag.rsplit('}',1)[-1] for x in source.iter())
    check(cnt['math']==cnt['exercise']==cnt['solution']==0,'no_equation_exercise_solution_content_claimed')
    save(ROOT/'qa/verification.json',{'status':'pass','checks':checks,'check_count':len(checks),'pdf_pages':len(pdf.pages),'pdf_pages_text':resources,'source_sha256':digest(ROOT/'source/a20-preface.cnxml'),'html_sha256':digest(ROOT/'index.html'),'pdf_sha256':digest(ROOT/'output/pdf/a20-preface-shahmukhi.pdf'),'limits':['Visual QA is recorded separately and must bind these PDF bytes.','Not PDF/UA certified; no screen-reader pronunciation certification.','12-locus prose canon is not specialist terminology consensus.','Source preface is complete; no textbook chapter is translated in this package.']})
    print(json.dumps({'status':'pass','checks':len(checks),'pdf_pages':len(pdf.pages),'pdf_sha256':digest(ROOT/'output/pdf/a20-preface-shahmukhi.pdf')}))


if __name__=='__main__':
    main()
