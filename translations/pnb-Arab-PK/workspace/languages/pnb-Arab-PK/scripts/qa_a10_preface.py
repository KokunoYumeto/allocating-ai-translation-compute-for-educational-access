"""Source-bound full-preface QA. Expected source DOM is not imported from the renderer.

Negative cases mutate detached trees/dictionaries only. No timing or timestamps enter
the receipt. Counts are assertions, not independent linguistic judgments.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import csv
import hashlib
import json
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

from prepare_a10 import jpeg_dimensions

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE/'source-excerpts/manifest-a10-preface.json'
TRANSLATION = BASE/'translations/a10-preface.json'
EXCERPT = BASE/'source-excerpts/a10-preface.cnxml'
OUTPUT = BASE/'reader/a10-preface.html'
NOTICE = BASE/'provenance/a10-preface-component-notices.json'
RECEIPT = BASE/'qa/structural-a10-preface.json'
N = '{http://cnx.rice.edu/cnxml}'
MD = '{http://cnx.rice.edu/mdml}'
SOURCE_SHA = 'd9f45fb31f4cb399c009c2be25eca1a99132b4b6882fb07f8649c2d56974f90b'
CREDIT = 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.'
AUTHORS = ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis']
HASH_POLICY = 'SHA-256 after CRLF-to-LF normalization in memory; files are not rewritten. Source/image/Git-blob hashes are raw-byte identities.'
IMAGE_IDENTITIES = [
    ('eip-id11714328','tryit.png',344,34,34,'7f9c8c226d8b937d4070c69326d6c2ac7df37a74c85fa8cec64e2ad7bef59ebf'),
    ('eip-id11708242101','howtoicon.png',1681,59,55,'67f2344cdbe25b192fbdee0d904ce912e4e15aed5bf0063f61a192dd0b0b5826'),
    ('eip-id1176034388','media.png',353,34,34,'140b45d7d047dc59b236c95bb2c2a237ca5b748b290b28f8e6d9f8f520077e6a'),
    ('fs-id1171782146065','CNX_ElemAlg_Figure_05_01_015_img.jpg',688493,791,257,'34fd0299880bc134f6308adcb2296ec1e145431909a1ab1cc2b507e01e3670f4')]


class Checks:
    def __init__(self):
        self.names = []

    def check(self, condition, name):
        if not condition:
            raise AssertionError(name)
        self.names.append(name)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fh(path):
    return sha(path.read_bytes())


def parse(value):
    value = value.replace('<!doctype html>', '')
    value = re.sub(r'<(meta|img|br)(\s[^<>]*?)?\s*/?>', lambda m: m.group(0).rstrip('/>')+'/>', value)
    return ET.fromstring(value)


def frag(value):
    return parse('<fragment>'+value+'</fragment>')


def signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text or '',
            tuple((signature(child), child.tail or '') for child in node))


def text(node):
    return ''.join(node.itertext())


def norm(value):
    return ' '.join(value.split())


def byid(root, ident):
    return next(x for x in root.iter() if x.get('id') == ident)


def inventory(source):
    parents = {child: parent for parent in source.iter() for child in parent}
    blocks, ancestors = {}, {}
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
        if tag == 'title':
            blocks[(parents[node].get('id') or 'm82630')+'/title'] = node
        elif tag == 'para':
            blocks[ident] = node
        elif tag == 'item':
            blocks[parents[node].get('id')+'/item/'+str(list(parents[node]).index(node)+1)] = node
        elif tag == 'media':
            blocks[ident+'/alt'] = node
    return blocks, ancestors, parents


def validate_inputs(m, t, source, c):
    raw = (ROOT/m['canonical_local_path']).read_bytes()
    c.check(sha(raw) == SOURCE_SHA == m['full_module_sha256'] == m['excerpt_sha256'], 'canonical_hash')
    c.check(len(raw) == 22483 == m['full_module_bytes'] == m['excerpt_bytes'], 'canonical_size')
    c.check(raw == EXCERPT.read_bytes() == (ROOT/m['release_authority_path']).read_bytes() and raw.endswith(b'\n'), 'complete_raw_boundary')
    c.check(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == m['canonical_git_blob_sha1'], 'canonical_git_blob')
    c.check(fh(ROOT/m['indonesian_comparison_path']) == m['indonesian_comparison_sha256'], 'indonesian_comparison_identity')
    lock = json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
    pinned = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    c.check((m['commit'],m['tree']) == (pinned['commit'],pinned['tree']), 'pinned_source_authority')
    c.check((m['module'],m['collection'],m['unit'],m['locale']) == ('m82630','col31130','A10-preface','pnb-Arab-PK'), 'manifest_scope')
    c.check((t['module'],t['assignment'],t['unit'],t['locale']) == ('m82630','A10','A10-preface','pnb-Arab-PK'), 'translation_scope')
    c.check(source.tag == N+'document' and source.attrib == {'class':'preface'} and
            [x.tag for x in source] == [N+'title',N+'metadata',N+'content'], 'entire_document_shape')
    c.check(source.find(N+'content').attrib == {'class':'preface'}, 'content_class')
    blocks, ancestors, parents = inventory(source)
    c.check(list(blocks) == m['source_text_keys_in_order'] == list(t['source_blocks']) and len(blocks) == 87, 'exact_87_key_order')
    c.check(ancestors == m['source_ancestor_ids'] and list(ancestors) == m['source_ids_in_document_order'] and len(ancestors) == 66, 'exact_66_source_ids_ancestry')
    c.check([x.get('id') for x in source.find(N+'content')] == m['content_direct_children_in_source_order'] ==
            ['eip-192','eip-287','eip-328','eip-574','eip-806','eip-653'], 'full_content_children')
    c.check(t['title'] == t['source_blocks']['m82630/title'] == m['module_title_pnb'], 'one_translated_title_value')
    counts = Counter(x.tag.removeprefix(N) for x in source.iter())
    for tag, count in [('section',25),('para',34),('list',3),('item',23),('newline',31),('media',4),('image',4),
                       ('figure',0),('caption',0),('math',0),('table',0),('link',0),('footnote',0),('note',0),('term',0),('exercise',0)]:
        c.check(counts[tag] == count, 'source_count:'+tag)
    expected_counts = {'retained_source_ids_excluding_excerpt_root':66,'translated_text_blocks':87,'display_titles':26,
                       'metadata_title_mirrors':1,'paragraphs':34,'list_items':23,'media_alt_blocks':4,'sections':25,'lists':3,
                       'newlines':31,'images':4,'media':4,'figures':0,'captions':0,'mathml_trees':0,'mathml_tables':0,
                       'cnxml_tables':0,'source_links':0,'terms':0,'notes':0,'footnotes':0,'exercises':0,'solutions':0}
    c.check(m['source_counts'] == expected_counts, 'manifest_count_contract')
    roles = {key:{'tag':node.tag.removeprefix(N),'newlines':len(node.findall('.//'+N+'newline'))} for key,node in blocks.items()}
    c.check(roles == m['source_block_roles'], 'exact_block_roles')
    for key, node in blocks.items():
        value = t['source_blocks'][key]
        translated = frag(value)
        c.check(not re.search(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]',value), 'clean_unicode:'+key)
        c.check(all(x.tag in ('fragment','em','strong','bdi','br') and x.attrib in ({},{'dir':'ltr'},{'dir':'ltr','lang':'en'}) for x in translated.iter()), 'fragment_allowlist:'+key)
        c.check(len(translated.findall('.//br')) == roles[key]['newlines'], 'newlines:'+key)
        source_text = node.get('alt') if node.tag == N+'media' else text(node)
        translated_text = re.sub(r'\{\{child:\d+\}\}', '', text(translated))
        c.check(re.findall(r'\d+(?:\.\d+)*',source_text) == re.findall(r'\d+(?:\.\d+)*',translated_text), 'source_numerals:'+key)
        for effect, htmltag in [('bold','strong'),('italics','em')]:
            c.check(len(node.findall('.//'+N+'emphasis[@effect="'+effect+'"]')) == len(translated.findall('.//'+htmltag)), 'emphasis:'+key+':'+effect)
        c.check(re.findall(r'\{\{child:\d+\}\}',value) == ['{{child:'+str(i)+'}}' for i in range(len(node.findall(N+'media')))], 'source_child_slots:'+key)
        if not key.endswith('/alt'):
            def isolated(current, ltr=False):
                here = ltr or current.get('dir') == 'ltr'
                own = re.sub(r'\{\{child:\d+\}\}','',current.text or '')
                if re.search(r'[A-Za-z0-9]',own) and not here:
                    return False
                for child in current:
                    if not isolated(child,here) or (re.search(r'[A-Za-z0-9]',child.tail or '') and not here):
                        return False
                return True
            c.check(isolated(translated), 'source_ltr_isolation:'+key)
    reviewer = blocks['eip-id1169146105286']
    lines = [(reviewer.text or '').strip()]+[(x.tail or '').strip() for x in reviewer][:-1]
    rf = frag(t['source_blocks']['eip-id1169146105286'])
    c.check(len(lines) == 21 and [text(x) for x in rf.findall('bdi')] == lines, 'exact_21_reviewer_lines')
    c.check([x.tag for x in rf] == ['bdi','br']*21 and rf[-1].tail in (None,''), 'terminal_reviewer_newline')
    c.check('Saint Louis Iniversity' in lines[9] and 'Roldán-Johnson' in lines[14], 'canonical_reviewer_spellings')
    for ident in ('eip-855','eip-250','eip-478'):
        c.check(text(frag(t['source_blocks'][ident])) == text(blocks[ident]), 'exact_author_credit:'+ident)
    c.check('Prealgebra 2e' in text(frag(t['source_blocks']['eip-582'])), 'source_wrong_book_name_retained')
    c.check(t['source_blocks']['fs-id1171782146065/alt'].count('«') == 3 and t['source_blocks']['fs-id1171782146065/alt'].count('»') == 2,
            'source_unclosed_graph_quote_retained')
    c.check('تِن حذف دے نشان' in t['source_blocks']['eip-id11708242101/alt'] and 'تِن نقطے' in t['image_alt_overrides']['eip-id11708242101'], 'ellipsis_dot_discrepancy_separate')
    c.check([(x['id'],x['source_key']) for x in t['source_corrections']] == [(x['id'],x['source_key']) for x in m['source_discrepancies']] and len(t['source_corrections']) == 4, 'four_discrepancy_records')
    for field, ident in [('bridge_before_html','a10-preface-source-context'),('bridge_after_html','a10-preface-bridge')]:
        bridge = frag(t[field])
        c.check(len(bridge) == 1 and bridge[0].get('id') == ident and bridge[0].get('data-origin') == 'original-bridge', 'original_bridge_input:'+field)
    media_ids = [x[0] for x in IMAGE_IDENTITIES]
    c.check(list(t['image_alt_overrides']) == list(t['image_alt_note_ids']) == media_ids, 'four_alt_override_bindings')
    for ident in media_ids:
        c.check(not list(frag(t['image_alt_overrides'][ident])) and not re.search(r'[\ufffd\u202a-\u202e\u2066-\u2069]',t['image_alt_overrides'][ident]), 'plain_accessible_override:'+ident)
        c.check(frag(t['bridge_after_html']).find('.//*[@id="'+t['image_alt_note_ids'][ident]+'"]') is not None, 'original_alt_note_exists:'+ident)


def expected_media(node, spec, t):
    ident = node.get('id')
    image = ET.Element('img', {'id':ident,'data-source-tag':'media','data-source-key':ident+'/alt','src':'../'+spec['path'],
        'alt':t['image_alt_overrides'][ident],'data-source-alt':t['source_blocks'][ident+'/alt'],
        'aria-describedby':t['image_alt_note_ids'][ident],'width':str(spec['width']),'height':str(spec['height'])})
    advisory = ET.Element('span',{'class':'alt-advisory','data-origin':'renderer-ui'})
    ET.SubElement(advisory,'a',{'href':'#'+t['image_alt_note_ids'][ident]}).text = 'تصویری وضاحت دا نوٹ'
    if spec['parent_tag'] == 'para':
        wrapper = ET.Element('span',{'class':'inline-source-media','data-source-child':ident,
            'style':f'--icon-width:{spec["width"]}px;--icon-height:{spec["height"]}px'})
        wrapper.extend([image,advisory])
    else:
        wrapper = ET.Element('div',{'class':'source-media','data-source-child':ident})
        scroll = ET.SubElement(wrapper,'div',{'class':'figure-scroll','dir':'ltr','tabindex':'0','role':'region','aria-label':'تِن محوری گراف'})
        scroll.append(image)
        hint = ET.SubElement(wrapper,'p',{'class':'scroll-hint','data-origin':'renderer-ui'})
        hint.text = 'تنگ سکرین اُتے تصویر نوں پاسے ول سرکا کے ویکھو؛ '
        link = ET.SubElement(hint,'a',{'href':'../'+spec['path']})
        link.text, link.tail = 'اصل تصویر وکھری کھولو', '۔'
        hint.append(advisory)
    return wrapper


def expected_article(source, m, t):
    blocks, ancestors, parents = inventory(source)
    inverse = {node:key for key,node in blocks.items()}
    images = {x['media_id']:x for x in m['images']}
    def convert(node, section_depth=0):
        tag = node.tag.removeprefix(N)
        if tag == 'media':
            return expected_media(node,images[node.get('id')],t)
        attrs = {'data-source-tag':tag}
        if node.get('id'):
            attrs['id'] = node.get('id')
        if node.get('class'):
            attrs['data-source-class'] = node.get('class')
        if tag in ('title','para','item'):
            key = inverse[node]
            attrs['data-source-key'] = key
            htmltag = {'title':'h'+str(section_depth+1),'para':'p','item':'li'}[tag]
            if node.findall(N+'media'):
                attrs['class'] = 'source-mixed-para'
            result = ET.Element(htmltag,attrs)
            value = t['source_blocks'][key]
            for index, child in enumerate(node.findall(N+'media')):
                value = value.replace('{{child:'+str(index)+'}}',ET.tostring(convert(child),encoding='unicode'))
            f = frag(value)
            result.text = f.text
            result.extend(list(f))
            return result
        if tag == 'list':
            attrs.update({'data-source-list-type':node.get('list-type','unspecified'),
                'data-source-bullet-style':node.get('bullet-style','unspecified'),
                'class':'source-list-no-bullets' if node.get('bullet-style') == 'none' else 'source-list'})
            result = ET.Element('ul',attrs)
        elif tag in ('content','section'):
            result = ET.Element('section',attrs)
        else:
            raise AssertionError('unsupported_expected_source_node:'+tag)
        result.extend(convert(child,section_depth+(tag == 'section')) for child in node)
        return result
    article = ET.Element('article',{'id':'a10-preface-source','data-source-tag':'document','data-source-class':'preface','data-source-module':'m82630'})
    article.extend([convert(source.find(N+'title')),convert(source.find(N+'content'))])
    return article


FOOTER_TEXT = [
    'Adapted from OpenStax Elementary Algebra 2e, module m82630: Preface, collection col31130. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University. All 21 reviewer credits and three named author affiliations are retained in source order, including the canonical spelling Saint Louis Iniversity.',
    'The existing A10 notice states Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained A10 release notice, canonical license text, and selected component evidence. No new clearance is asserted.',
    'Raw-source default art credit: '+CREDIT+' The pinned source paragraph eip-787 provides this default for art without attribution in the text and retains component-specific permission limits. Named book authors are not relabeled as image creators. This source claim and the media identity records are retained, not independently verified as image-specific clearance.',
    'OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. All four original images are unchanged and unmirrored. The three inline icons are static illustrations, not functional controls. The graph remains unnumbered section-level media; no figure or caption is invented.',
    'Changes: complete translation of 87 source blocks, with all 66 source IDs, 25 sections, 23 list items and 31 explicit newlines retained. Original metadata, including the original title, is retained separately; the translated visible document title appears once. RTL prose uses LTR isolation for source numbers, names and English. Three source lists preserve their declared attributes; the third has unspecified source list type, and its visible bullets are presentation only.',
    'Faithful translated source alts are retained in data-source-alt. Separately labeled accessible overrides describe the visible originals, with visible correction links and aria-describedby pointing to the original explanations. The missing graph sentences, the icon description differences, Prealgebra 2e and Saint Louis Iniversity remain traceable. Opening context and closing correction/word-key material are original additions outside the source article.',
    "Indonesian comparison: Elementary Algebra 2e Indonesian preservation release v1.0.2. Its complete-book publication claim and process provenance describe that source release, not this local Punjabi reader. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact. Source institutional, resource, access and licensing statements are pinned-source claims, not newly verified current offers.",
    'Coverage: complete m82630 preface only, not the whole textbook. The complete A10, A20, A30, B10 and B40 workflow remains unfinished. This is not a training or fine-tuning dataset. Native-language, educator, assistive-technology and browser review remain separate. Frozen source witness · Source manifest · Language and source notes.'
]


def validate_reader(root, source, m, t, c):
    c.check(root.tag == 'html' and root.attrib == {'lang':'pnb-Arab-PK','dir':'rtl'} and [x.tag for x in root] == ['head','body'], 'reader_root')
    c.check(not (root.text or '').strip() and all(not (x.tail or '').strip() for x in root), 'reader_root_own_slots')
    head, body = root
    c.check(body.attrib == {'class':'a10-reader a10-preface'} and [x.tag for x in body] == ['header','main','footer'], 'body_shape')
    c.check(not (body.text or '').strip() and all(not (x.tail or '').strip() for x in body), 'body_own_slots')
    metas = head.findall('meta')
    original_metadata = {x.tag.removeprefix(MD):x.text or '' for x in source.find(N+'metadata')}
    expected_meta = [{'charset':'utf-8'},{'name':'viewport','content':'width=device-width, initial-scale=1'},
        {'name':'description','content':'Complete m82630 preface in Shahmukhi Punjabi; not a complete textbook'},
        {'name':'source-document-class','content':'preface'}]+[{'name':'source-'+name,'content':value} for name,value in original_metadata.items()]
    c.check([x.attrib for x in metas] == expected_meta and all(not list(x) and not (x.text or '') for x in metas), 'exact_original_metadata')
    c.check([x.tag for x in head] == ['meta']*8+['title','style'] and not (head.text or '').strip() and all(not (x.tail or '').strip() for x in head), 'head_shape_and_slots')
    c.check(head.find('title').text == t['title']+' — A10 preface' and not list(head.find('title')), 'html_title')
    style = head.find('style')
    shared_css = (BASE/'styles/reader.css').read_text(encoding='utf-8')
    c.check(not list(style) and style.text.startswith(shared_css), 'shared_css_read_only_prefix')
    c.check(sha(style.text[len(shared_css):].encode()) == '64f8a05e4cf59f13cea92041b1986869ac79c896692643085de52da45acab4dd',
            'reviewed_unit_css_fingerprint')
    for rule in ('.inline-source-media img { display:inline-block; width:var(--icon-width); height:var(--icon-height)',
                 '.source-media img { display:block; width:791px; min-width:791px; max-width:none; height:auto;',
                 '.source-list-no-bullets { list-style:none;', '.figure-scroll { direction:ltr;'):
        c.check(rule in style.text, 'presentation_rule:'+rule.split('{')[0])
    header, main, footer = body
    expected_header = frag('<header><p class="eyebrow"><bdi dir="ltr">A10 / col31130 / m82630</bdi></p><p>'+t['subtitle']+'</p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p><nav aria-label="حصے"><a href="#a10-preface-source">ماخذ دا ترجمہ</a> · <a href="#a10-preface-bridge">ساڈے نوٹ تے لفظاں دی کُنجی</a> · <a href="#credits">ماخذ تے انتساب</a> · <a href="a10-introduction.html">باب دی جان پہچان</a></nav></header>')[0]
    c.check(signature(header) == signature(expected_header), 'exact_header_ui')
    c.check(main.attrib == {} and len(main) == 5 and not (main.text or '') and all(not (x.tail or '') for x in main), 'main_exact_slots')
    label = frag('<p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>۔ ایتھے پورا دیباچہ <bdi dir="ltr">m82630</bdi> ترجمہ کیتا گیا اے؛ ایہہ پوری کتاب نہیں۔</p>')[0]
    c.check(signature(main[0]) == signature(label), 'source_label_limits')
    c.check(signature(main[1]) == signature(frag(t['bridge_before_html'])[0]), 'original_context_separate')
    c.check(signature(main[3]) == signature(frag(t['bridge_after_html'])[0]), 'original_corrections_separate')
    status = frag('<p class="status" data-origin="renderer-ui">پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p>')[0]
    c.check(signature(main[4]) == signature(status), 'unfinished_assignment_status')
    article = main[2]
    expected = expected_article(source,m,t)
    c.check(signature(article) == signature(expected), 'exact_complete_source_article')
    ids = [x.get('id') for x in root.iter() if x.get('id')]
    c.check(len(ids) == len(set(ids)), 'globally_unique_ids')
    srcids = set(m['source_ids_in_document_order'])
    c.check([x.get('id') for x in article.iter() if x.get('id') in srcids] == m['source_ids_in_document_order'], 'rendered_source_id_order')
    parentmap = {child:parent for parent in article.iter() for child in parent}
    for ident, chain in m['source_ancestor_ids'].items():
        found, parent = [], parentmap.get(byid(article,ident))
        while parent is not None:
            if parent.get('id') in srcids:
                found.insert(0,parent.get('id'))
            parent = parentmap.get(parent)
        c.check(found == chain, 'rendered_source_ancestry:'+ident)
    c.check([x.get('data-source-key') for x in article.iter() if x.get('data-source-key')] == m['source_text_keys_in_order'], 'rendered_87_key_order')
    c.check(len(article.findall('.//br')) == 31 and len(article.findall('.//li')) == 23 and len(article.findall('.//h1')) == 1, 'rendered_breaks_items_title')
    c.check(all(x.tag not in ('div','section','figure','p','ul','h2','h3') for p in article.findall('.//p') for x in p.iter() if x is not p), 'valid_paragraph_mixed_content')
    c.check(all(x.tag not in ('figure','figcaption','table','math','script','iframe','button','video','audio') for x in article.iter()), 'no_invented_source_objects_or_controls')
    source_links = [x for x in article.iter('a') if x.get('data-source-target')]
    c.check(not source_links and len(article.findall('.//a')) == 5, 'only_four_correction_links_and_one_original_image')
    for item in m['images']:
        image = byid(article,item['media_id'])
        c.check(image.get('alt') == t['image_alt_overrides'][item['media_id']] and image.get('data-source-alt') == t['source_blocks'][item['media_id']+'/alt'], 'traceable_dual_alts:'+item['media_id'])
        c.check(image.get('aria-describedby') == t['image_alt_note_ids'][item['media_id']] and image.get('aria-describedby') in ids, 'direct_accessible_note:'+item['media_id'])
    c.check(footer.attrib == {'id':'credits','lang':'en','dir':'ltr'} and [x.tag for x in footer] == ['h2']+['p']*8, 'footer_shape')
    c.check(not (footer.text or '').strip() and all(not (x.tail or '').strip() for x in footer), 'footer_own_slots')
    c.check(footer[0].text == 'Sources, credits and changes — A10 preface' and not list(footer[0]) and not footer[0].attrib, 'footer_heading')
    for index, (paragraph, expected_text) in enumerate(zip(footer.findall('p'),FOOTER_TEXT)):
        c.check(text(paragraph) == expected_text, 'exact_credit_and_limits:'+str(index))
        c.check(paragraph.attrib == ({'id':'a10-preface-art-credit'} if index == 2 else {}) and
                all(x.tag in ('p','a','span') for x in paragraph.iter()) and all(not list(x) for x in paragraph if x.tag in ('a','span')), 'bounded_footer_markup:'+str(index))
    spans = footer.findall('.//span')
    c.check(len(spans) == 1 and spans[0].attrib == {'data-origin':'retained-source-credit'} and spans[0].text == CREDIT, 'exact_raw_source_art_credit')
    expected_links = [m['upstream_url']+'/blob/'+m['commit']+'/'+m['path'],'https://creativecommons.org/licenses/by-nc-sa/4.0/',
        '../provenance/A10-release/NOTICE.txt','../provenance/upstream--osbooks-prealgebra-bundle/LICENSE','../provenance/a10-preface-component-notices.json',
        '#eip-787','https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2',
        '../source-excerpts/a10-preface.cnxml','../source-excerpts/manifest-a10-preface.json','../qa/a10-preface-language-notes.md']
    c.check([x.attrib for x in footer.iter('a')] == [{'href':x} for x in expected_links], 'exact_provenance_links')
    c.check([x.text for x in footer.iter('a')] == ['OpenStax Elementary Algebra 2e, module m82630: Preface',
        'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International','A10 release notice','canonical license text',
        'selected component evidence','eip-787','Elementary Algebra 2e Indonesian preservation release v1.0.2',
        'Frozen source witness','Source manifest','Language and source notes'], 'exact_provenance_link_labels')
    for anchor in root.iter('a'):
        href = anchor.get('href','')
        if href.startswith('#'):
            c.check(href[1:] in ids, 'internal_link:'+href)
        elif not href.startswith('https://'):
            path = (OUTPUT.parent/href).resolve()
            c.check(path.is_relative_to(BASE.resolve()) and path.is_file(), 'local_link:'+href)


def validate_notice(notice, m, source, c):
    c.check(set(notice) == {'schema','unit','work','module','collection','commit','manifest_sha256','excerpt_sha256','scope',
        'existing_notice_inputs','existing_notice_input_hash_policy','release_notice_verbatim','original_senior_contributing_authors',
        'existing_license_statement','non_endorsement','rights_status','credit_limit','source_default_art_credit',
        'source_default_art_credit_paragraph','raw_source_art_attribution_paragraph_verbatim','media_authority_manifest',
        'images','source_discrepancies','whole_book_translation_complete','publication_claim_limit'}, 'notice_exact_fields')
    c.check(notice['schema'] == 'a10-retained-component-evidence-v1' and (notice['unit'],notice['module'],notice['collection']) == ('A10-preface','m82630','col31130'), 'notice_scope')
    c.check(notice['work'] == 'OpenStax Elementary Algebra 2e' and notice['commit'] == m['commit'] and notice['manifest_sha256'] == fh(MANIFEST) and notice['excerpt_sha256'] == SOURCE_SHA, 'notice_source_bindings')
    c.check(notice['existing_notice_inputs'] == m['existing_notice_inputs'] and notice['existing_notice_input_hash_policy'] == m['existing_notice_input_hash_policy'] == HASH_POLICY, 'notice_lf_policy')
    for item in notice['existing_notice_inputs']:
        c.check(sha((ROOT/item['path']).read_bytes().replace(b'\r\n',b'\n')) == item['sha256'], 'notice_input_lf:'+item['path'])
    c.check(notice['release_notice_verbatim'] == (BASE/'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'), 'verbatim_existing_release_notice')
    c.check(notice['original_senior_contributing_authors'] == m['retained_attribution']['original_senior_contributing_authors'] == AUTHORS, 'notice_named_authors')
    c.check(notice['existing_license_statement'] == m['retained_attribution']['existing_license_statement'] == 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.', 'notice_license_qualification')
    c.check(notice['non_endorsement'] == m['retained_attribution']['non_endorsement'] == 'OpenStax and Rice University do not endorse this translation; names, logos, and marks are not licensed.', 'notice_nonendorsement')
    c.check(notice['source_default_art_credit'] == CREDIT and notice['source_default_art_credit_paragraph'] == 'eip-787' and notice['raw_source_art_attribution_paragraph_verbatim'] == text(byid(source,'eip-787')), 'notice_raw_credit_and_full_permissions')
    c.check(notice['rights_status'] == 'Existing audited A10 policy retained; no new component-specific clearance determination.' and
            notice['credit_limit'] == 'The media authority rows identify bytes and Git blobs, not rights holders or permissions. Named book authors are not relabeled as image creators. Raw-source default art credit and component-specific restrictions are retained, not independently verified as image-specific clearance.', 'notice_no_new_clearance')
    c.check(notice['scope'] == 'Complete m82630 preface and four unchanged original images; no new supply/license audit.' and notice['whole_book_translation_complete'] is False and
            notice['publication_claim_limit'] == 'Complete-book publication language in the retained Indonesian release NOTICE describes that release, not this Punjabi preface or the whole Punjabi book.', 'notice_publication_scope')
    c.check(notice['source_discrepancies'] == m['source_discrepancies'], 'notice_discrepancy_trace')
    mp = ROOT/'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
    c.check(notice['media_authority_manifest'] == {'path':mp.relative_to(ROOT).as_posix(),'sha256':fh(mp),'hash_policy':'raw bytes; separate from logical-LF existing_notice_inputs'}, 'raw_media_manifest_identity')
    with mp.open(encoding='utf-8-sig',newline='') as stream:
        rows = list(csv.DictReader(stream))
    c.check(len(notice['images']) == len(m['images']) == 4, 'notice_four_images')
    parents = {child:parent for parent in source.iter() for child in parent}
    for record, spec, expected in zip(notice['images'],m['images'],IMAGE_IDENTITIES):
        ident, filename, size, width, height, digest = expected
        media = byid(source,ident)
        c.check((spec['media_id'],spec['path'],spec['bytes'],spec['width'],spec['height'],spec['sha256']) ==
                (ident,'assets/a10/'+filename,size,width,height,digest), 'fixed_image_identity:'+ident)
        c.check(spec['source_src'] == '../../media/'+filename and spec['source_path'] == 'media/'+filename and
                spec['canonical_local_path'] == 'downloads/complete-upstream/osbooks-prealgebra-bundle/media/'+filename, 'image_paths:'+ident)
        c.check(spec['source_alt'] == media.get('alt') and '\ufffd' not in spec['source_alt'], 'exact_english_source_alt:'+ident)
        c.check((spec['figure_id'],spec['parent_id'],spec['parent_tag']) == (None,parents[media].get('id'),parents[media].tag.removeprefix(N)), 'source_media_role:'+ident)
        c.check(media.find(N+'image').attrib == {'mime-type':spec['mime_type'],'src':spec['source_src']}, 'source_image_attributes:'+ident)
        raw = (ROOT/spec['canonical_local_path']).read_bytes()
        actual_dims = struct.unpack('>II',raw[16:24]) if raw.startswith(b'\x89PNG\r\n\x1a\n') else jpeg_dimensions(raw)
        c.check(raw == (BASE/spec['path']).read_bytes() and sha(raw) == digest and len(raw) == size and actual_dims == (width,height), 'original_pixels_dimensions:'+ident)
        c.check(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == spec['git_blob_sha1'], 'image_git_blob:'+ident)
        c.check([x for x in rows if x['relative_path'] == spec['source_path']] == [spec['existing_media_authority_row']], 'existing_media_row:'+ident)
        c.check(set(record) == {'figure_id','media_id','parent_id','parent_tag','source_path','path','mime_type','sha256','bytes',
            'width','height','git_blob_sha1','source_alt','existing_media_authority_row','treatment','component_clearance'}, 'notice_image_exact_fields:'+ident)
        for key in ('figure_id','media_id','parent_id','parent_tag','source_path','path','mime_type','sha256','bytes','width','height','git_blob_sha1','source_alt','existing_media_authority_row'):
            c.check(record[key] == spec[key], 'notice_image_binding:'+ident+':'+key)
        c.check(record['treatment'] == 'Original bytes unchanged and unmirrored. Faithful source alt retained separately from a labeled visible-shape accessible override; no source figure number exists.' and
                record['component_clearance'] == 'Not newly assessed; subject to retained component-specific credits and restrictions.', 'notice_image_limits:'+ident)


def mutations(root, source, m, t, notice):
    results = []
    def swap_children(parent, left, right):
        children = list(parent)
        children[left], children[right] = children[right], children[left]
        parent[:] = children
    def rejects(name, kind, change, expected_failure):
        r, mm, tt, nn = deepcopy(root),deepcopy(m),deepcopy(t),deepcopy(notice)
        change(r,mm,tt,nn)
        try:
            if kind == 'reader':
                validate_reader(r,source,mm,tt,Checks())
            elif kind == 'input':
                validate_inputs(mm,tt,source,Checks())
            else:
                validate_notice(nn,mm,source,Checks())
        except AssertionError as error:
            if str(error) != expected_failure:
                raise AssertionError('mutation_wrong_guard:'+name+':'+str(error)) from error
            results.append({'name':name,'rejected_by':str(error),'detached':True})
        else:
            raise AssertionError('mutation_not_rejected:'+name)
    exact = 'exact_complete_source_article'
    rejects('drop_first_source_paragraph','reader',lambda r,m,t,n: byid(r,'eip-192').clear(),exact)
    rejects('swap_top_level_sections','reader',lambda r,m,t,n: swap_children(byid(r,'a10-preface-source')[1],1,5),exact)
    rejects('inject_unkeyed_source_paragraph','reader',lambda r,m,t,n: ET.SubElement(byid(r,'eip-287'),'p').__setattr__('text','All solutions are now available.'),exact)
    rejects('inject_container_own_text','reader',lambda r,m,t,n: byid(r,'eip-328').__setattr__('text','999'),exact)
    rejects('remove_section_class','reader',lambda r,m,t,n: byid(r,'eip-957').attrib.pop('data-source-class'),exact)
    rejects('wrong_heading_level','reader',lambda r,m,t,n: byid(r,'eip-493')[0].__setattr__('tag','h2'),exact)
    rejects('invent_list_numbering','reader',lambda r,m,t,n: byid(r,'eip-992').__setattr__('tag','ol'),exact)
    rejects('swap_list_items','reader',lambda r,m,t,n: swap_children(byid(r,'eip-992'),0,1),exact)
    rejects('chapter_digit','reader',lambda r,m,t,n: byid(r,'eip-992')[0].find('.//bdi').__setattr__('text','11'),exact)
    rejects('source_section_reference_digit','reader',lambda r,m,t,n: byid(r,'eip-372').find('bdi').__setattr__('text','2.2'),exact)
    rejects('reviewer_name_silent_correction','reader',lambda r,m,t,n: byid(r,'eip-id1169146105286')[18].__setattr__('text','John Kalliongis, Saint Louis University'),exact)
    rejects('lost_terminal_newline','reader',lambda r,m,t,n: byid(r,'eip-id1169146105286').remove(byid(r,'eip-id1169146105286')[-1]),exact)
    rejects('invented_icon_linebreak','reader',lambda r,m,t,n: byid(r,'eip-207').insert(0,ET.Element('br')),exact)
    rejects('mixed_icon_moves_after_prose','reader',lambda r,m,t,n: byid(r,'eip-109').__setattr__('text','کرن دا طریقہ'),exact)
    rejects('inline_wrapper_text_injection','reader',lambda r,m,t,n: byid(r,'eip-207')[0].__setattr__('text','f(2)=999'),exact)
    rejects('wrong_image_src','reader',lambda r,m,t,n: byid(r,'eip-id11714328').set('src','../assets/a10/media.png'),exact)
    rejects('erased_faithful_alt','reader',lambda r,m,t,n: byid(r,'fs-id1171782146065').attrib.pop('data-source-alt'),exact)
    rejects('incorrect_accessible_alt','reader',lambda r,m,t,n: byid(r,'eip-id11708242101').set('alt','three ellipses'),exact)
    rejects('wrong_correction_link','reader',lambda r,m,t,n: byid(r,'eip-207').find('.//a').set('href','#credits'),exact)
    rejects('wrong_aria_note','reader',lambda r,m,t,n: byid(r,'eip-id11714328').set('aria-describedby','credits'),exact)
    rejects('invent_graph_figure_identity','reader',lambda r,m,t,n: byid(r,'eip-180')[-1].__setattr__('tag','figure'),exact)
    rejects('source_disclaimer_book_silent_correction','reader',lambda r,m,t,n: byid(r,'eip-582').find('.//bdi').__setattr__('text','Elementary Algebra 2e'),exact)
    rejects('metadata_uuid','reader',lambda r,m,t,n: r.find('head/meta[@name="source-uuid"]').set('content','changed'), 'exact_original_metadata')
    rejects('duplicate_metadata_title_as_visible','reader',lambda r,m,t,n: byid(r,'a10-preface-source').insert(0,ET.Element('h1')),exact)
    rejects('original_bridge_relabel','reader',lambda r,m,t,n: byid(r,'a10-preface-bridge').set('data-origin','source'), 'original_corrections_separate')
    rejects('unkeyed_main_completion_claim','reader',lambda r,m,t,n: r.find('body/main').__setattr__('text','Whole book completed.'), 'main_exact_slots')
    rejects('default_credit_overclaim','reader',lambda r,m,t,n: byid(r,'a10-preface-art-credit').find('span').__setattr__('text','All images cleared for unrestricted reuse.'), 'exact_credit_and_limits:2')
    rejects('footer_hidden_extra_claim','reader',lambda r,m,t,n: ET.SubElement(byid(r,'credits'),'p').__setattr__('text','Complete book published.'), 'footer_shape')
    rejects('css_mirror_originals','reader',lambda r,m,t,n: r.find('head/style').__setattr__('text',r.find('head/style').text+'img { transform:scaleX(-1); }'), 'reviewed_unit_css_fingerprint')
    rejects('translation_source_numeral','input',lambda r,m,t,n: t['source_blocks'].__setitem__('eip-372',t['source_blocks']['eip-372'].replace('2.1','2.2')), 'source_numerals:eip-372')
    rejects('translation_terminal_newline','input',lambda r,m,t,n: t['source_blocks'].__setitem__('eip-id1169146105286',t['source_blocks']['eip-id1169146105286'][:-4]), 'newlines:eip-id1169146105286')
    rejects('manifest_english_quote_corruption','notice',lambda r,m,t,n: m['images'][3].__setitem__('source_alt',m['images'][3]['source_alt'].replace('“','\ufffd')), 'exact_english_source_alt:fs-id1171782146065')
    rejects('notice_image_hash','notice',lambda r,m,t,n: n['images'][0].__setitem__('sha256','0'*64), 'notice_image_binding:eip-id11714328:sha256')
    rejects('notice_raw_credit_limits','notice',lambda r,m,t,n: n.__setitem__('raw_source_art_attribution_paragraph_verbatim',CREDIT), 'notice_raw_credit_and_full_permissions')
    rejects('notice_new_clearance','notice',lambda r,m,t,n: n.__setitem__('rights_status','All images cleared.'), 'notice_no_new_clearance')
    rejects('notice_injected_clearance_field','notice',lambda r,m,t,n: n.__setitem__('image_clearance','Newly cleared.'), 'notice_exact_fields')
    rejects('notice_release_claim','notice',lambda r,m,t,n: n.__setitem__('whole_book_translation_complete',True), 'notice_publication_scope')
    rejects('notice_raw_crlf_digest','notice',lambda r,m,t,n: n['existing_notice_inputs'][1].__setitem__('sha256',fh(ROOT/n['existing_notice_inputs'][1]['path'])), 'notice_lf_policy')
    return results


def scoped_inputs(m):
    paths = [MANIFEST,TRANSLATION,EXCERPT,BASE/'sources.lock.json',BASE/'styles/reader.css',BASE/'qa/a10-preface-language-notes.md',
             BASE/'scripts/prepare_a10.py',BASE/'scripts/prepare_a10_preface.py',BASE/'scripts/build_a10_preface.py',Path(__file__),
             ROOT/m['canonical_local_path'],ROOT/m['release_authority_path'],ROOT/m['indonesian_comparison_path']]
    paths += [ROOT/x['path'] for x in m['existing_notice_inputs']]
    paths += [ROOT/x['canonical_local_path'] for x in m['images']]
    paths += [BASE/'canon/receipts'/name for name in ['A10-preface-draft-20260830T232909366155Z.json',
              'A10-preface-revision-20260830T233655539555Z.json','A10-preface-qa-20260830T234102382290Z.json']]
    return {x.relative_to(ROOT).as_posix():fh(x) for x in paths}


def run():
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    t = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    source = ET.parse(EXCERPT).getroot()
    before = scoped_inputs(m)
    c = Checks()
    validate_inputs(m,t,source,c)
    products = []
    for _ in range(2):
        for script in ('prepare_a10_preface.py','build_a10_preface.py'):
            subprocess.run([sys.executable,'-B',str(BASE/'scripts'/script)],check=True,capture_output=True,text=True,encoding='utf-8')
        products.append({'reader':fh(OUTPUT),'notices':fh(NOTICE),
                         'images':{x['path']:fh(BASE/x['path']) for x in m['images']}})
    c.check(products[0] == products[1], 'two_preparations_two_builds_identical')
    root = parse(OUTPUT.read_text(encoding='utf-8'))
    notice = json.loads(NOTICE.read_text(encoding='utf-8'))
    validate_reader(root,source,m,t,c)
    validate_notice(notice,m,source,c)
    negative = mutations(root,source,m,t,notice)
    c.check(before == scoped_inputs(m), 'all_scoped_inputs_unchanged')
    c.check(products[-1] == {'reader':fh(OUTPUT),'notices':fh(NOTICE),'images':{x['path']:fh(BASE/x['path']) for x in m['images']}}, 'negative_tests_did_not_change_products')
    receipt = {'schema':'pnb-source-bound-structural-qa-v1','unit':'A10-preface','module':'m82630','status':'pass',
        'scope':'Entire pinned m82630 preface; checkpoint only, whole assignment remains active.',
        'source_counts':m['source_counts'],'checks_passed':len(c.names),'check_names':c.names,
        'detached_mutations_rejected':len(negative),'mutation_results':negative,
        'deterministic_preparations':2,'deterministic_builds':2,'outputs':products[-1],
        'source_input_raw_sha256':before,'existing_notice_input_hash_policy':HASH_POLICY,
        'input_correction':'Five U+FFFD in the draft manifest English graph alt were repaired to exact canonical smart quotes; source/witness/Punjabi strings were unchanged. Persistent QA now compares every full English alt directly.',
        'limits':['Assertions include repeated block checks, not independent linguistic judgments.',
                  'No fresh canon-reading stage is claimed by an automated rerun; the three actual draft/revision/QA consultation receipts and notes are scoped inputs.',
                  'Browser visual, keyboard/screen-reader, native-language and educator review are separate; structure alone does not prove rendering or idiomaticity.',
                  'Graph mathematical descriptions were source/image reviewed at drafting; this suite verifies exact retention, not a new image-understanding proof.',
                  'External websites, accounts and source access/resource/licensing claims are not checked for current availability; retained claims are explicitly source-attributed.',
                  'Existing audited rights policy only; media byte identity is not image-specific clearance. No new supply/license audit.',
                  'The canonical metadata is retained as source head metadata, not as a duplicate visible title; source-formatting indentation is not display prose.',
                  'Manifest and language notes retain their historical input-only-stage status; this receipt records the subsequent production checkpoint.',
                  'No complete-book or whole-assignment completion is asserted.']}
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'A10-preface QA passed: {len(c.names)} checks; {len(negative)} detached mutations; two builds and preparations identical.')
    print('reader SHA-256 '+fh(OUTPUT))
    print('notice SHA-256 '+fh(NOTICE))
    print('receipt SHA-256 '+fh(RECEIPT))


if __name__ == '__main__':
    run()
