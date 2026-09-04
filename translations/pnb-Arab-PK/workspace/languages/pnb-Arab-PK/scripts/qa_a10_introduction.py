"""Independent source-bound QA for the complete m82451 introduction.

Only generated reader/notice outputs are rebuilt. Negative tests mutate detached
trees/dictionaries/digests, never the source, translation or image on disk.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import copy
import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE/'source-excerpts/manifest-a10-introduction.json'
TRANSLATION = BASE/'translations/a10-introduction.json'
EXCERPT = BASE/'source-excerpts/a10-introduction.cnxml'
READER = BASE/'reader/a10-introduction.html'
NOTICES = BASE/'provenance/a10-introduction-component-notices.json'
RECEIPT = BASE/'qa/structural-a10-introduction.json'
N = '{http://cnx.rice.edu/cnxml}'
MD = '{http://cnx.rice.edu/mdml}'
SOURCE_SHA = '025f994e3c66f19462c9423788f703f7987fecb67656911d840fdd15a58d8a4a'
CREDIT = 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.'
AUTHORS = ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis']
FORBIDDEN = re.compile(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]')


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def signature(node):
    return node.tag, tuple(sorted(node.attrib.items())), node.text, tuple((signature(c), c.tail) for c in node)


def text(node):
    return ''.join(node.itertext())


def by_id(root, sid):
    nodes = [n for n in root.iter() if n.get('id') == sid]
    require('one_id:'+sid, len(nodes) == 1)
    return nodes[0]


def parse_reader(raw):
    # Only void-element serialization is normalized; no browser nesting repair.
    raw = raw[raw.index('<html'):]
    return ET.fromstring(re.sub(r'<(meta|img)\b([^<>]*?)(?<!/)>', lambda m: '<'+m[1]+m[2]+' />', raw))


def source_blocks(source):
    content = source.find(N+'content')
    figure, para = list(content)
    media, caption = list(figure)
    return {
        source.find(N+'metadata/'+MD+'content-id').text+'/title': ('title', source.find(N+'title')),
        media.get('id')+'/alt': ('alt', media),
        figure.get('id')+'/caption': ('caption', caption),
        para.get('id'): ('para', para)
    }


def validate_source(source, m, check=require):
    canonical = ROOT/m['canonical_local_path']
    raw = canonical.read_bytes()
    check('canonical_fixed_hash_and_1066_bytes', sha(canonical) == m['full_module_sha256'] == SOURCE_SHA and len(raw) == m['full_module_bytes'] == 1066)
    check('canonical_release_copy_identical', raw == (ROOT/m['release_authority_path']).read_bytes())
    check('canonical_git_blob_exact', hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == m['canonical_git_blob_sha1'])
    check('whole_witness_exact_plus_one_final_LF', EXCERPT.read_bytes() == raw+b'\n' and b'\r' not in raw)
    check('witness_hash_and_1067_bytes', sha(EXCERPT) == m['excerpt_sha256'] and len(EXCERPT.read_bytes()) == m['excerpt_bytes'] == 1067)
    check('whole_parsed_document_matches_canonical', signature(source) == signature(ET.fromstring(raw)))
    check('document_has_no_invented_source_id', source.attrib == {'class':'introduction'} and m['excerpt_root_id'] is None)
    check('all_document_children_in_order', [n.tag for n in source] == [N+'title',N+'metadata',N+'content'])
    check('full_module_boundary_end_paragraph', [n.get('id') for n in source.find(N+'content')]
          == ['CNX_ElemAlg_Figure_01_00_001','fs-id1170653837691'] == m['content_direct_children_in_source_order'])
    check('three_original_ids_in_order', [n.get('id') for n in source.iter() if n.get('id')]
          == m['source_ids_in_document_order'] and len(m['source_ids_in_document_order']) == 3)
    counts = Counter(n.tag for n in source.iter())
    for name in ['para','caption','media','image','figure','title']:
        check('one_source_'+name, counts[N+name] == 1)
    check('one_metadata_title_mirror', counts[MD+'title'] == 1)
    for name in ['table','link','term','note','list','item','newline','footnote','exercise','solution']:
        check('no_source_'+name, counts[N+name] == 0)
    check('zero_source_mathml', not any(n.tag.startswith('{http://www.w3.org/1998/Math/MathML}') for n in source.iter()))
    expected_counts = {'retained_source_ids_excluding_excerpt_root':3, 'translated_text_blocks':4,
        'display_titles':1,'metadata_title_mirrors':1,'paragraphs':1,'captions':1,'media_alt_blocks':1,
        'figures':1,'media':1,'images':1,'mathml_trees':0,'mathml_tables':0,'cnxml_tables':0,
        'source_links':0,'terms':0,'lists':0,'notes':0,'footnotes':0,'exercises':0,'solutions':0,'newlines':0}
    check('manifest_all_source_counts_exact', m['source_counts'] == expected_counts)
    indonesian = ROOT/m['indonesian_comparison_path']
    check('comparison_hash', sha(indonesian) == m['indonesian_comparison_sha256'])
    def shape(n):
        return n.tag, tuple((k,v) for k,v in sorted(n.attrib.items()) if k != 'alt'), tuple(shape(c) for c in n)
    check('comparison_identical_structure_and_ids', shape(source) == shape(ET.parse(indonesian).getroot()))
    lock = json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
    upstream = next(x for x in lock['repositories'] if x['role']=='A10+A20 upstream')
    check('pinned_lock_matches_manifest', (m['commit'],m['tree']) == (upstream['commit'],upstream['tree']))
    check('complete_module_not_whole_assignment', m['whole_assignment_complete'] is False
          and [x['module'] for x in m['earlier_collection_items_still_pending']] == ['m82630'])
    return {key.rsplit('}',1)[-1]: value for key,value in counts.items() if key.startswith(N)}


def expected_source_article(source, t, m):
    """Independent CNXML-driven expected DOM; no import of either renderer."""
    blocks = t['source_blocks']
    figure, para = list(source.find(N+'content'))
    media, caption = list(figure)
    spec = m['images'][0]
    article = ET.Element('article', {'id':'a10-introduction-source','data-source-tag':'document',
                                    'data-source-class':source.get('class'),'data-source-module':'m82451'})
    ET.SubElement(article,'h1',{'data-source-tag':'title','data-source-key':'m82451/title'}).text = blocks['m82451/title']
    container = ET.SubElement(article,'section',{'data-source-tag':'content'})
    fig = ET.SubElement(container,'figure',{'id':figure.get('id'),'class':figure.get('class'),'data-source-tag':'figure'})
    wrapper = ET.SubElement(fig,'div',{'class':'source-media'})
    scroll = ET.SubElement(wrapper,'div',{'class':'figure-scroll','dir':'ltr'})
    ET.SubElement(scroll,'img',{'id':media.get('id'),'data-source-tag':'media','data-source-key':media.get('id')+'/alt',
        'src':'../'+spec['path'],'alt':blocks[media.get('id')+'/alt'],'width':str(spec['width']),'height':str(spec['height'])})
    hint = ET.SubElement(wrapper,'p',{'class':'scroll-hint','data-origin':'renderer-ui'})
    hint.text = 'تصویر دے اصل سائز لئی '
    a = ET.SubElement(hint,'a',{'href':'../'+spec['path']})
    a.text = 'اصل تصویر وکھری کھولو'; a.tail = '۔'
    ET.SubElement(fig,'figcaption',{'data-source-tag':'caption','data-source-key':figure.get('id')+'/caption'}).text = blocks[figure.get('id')+'/caption']
    ET.SubElement(container,'p',{'id':para.get('id'),'data-source-tag':'para','data-source-key':para.get('id')}).text = blocks[para.get('id')]
    return article


def validate_translation(t, source, m, check=require):
    specs = source_blocks(source)
    check('exact_four_source_keys_and_order', list(t['source_blocks']) == list(specs) == m['source_text_keys_in_order'] and len(specs) == 4)
    for key,(kind,node) in specs.items():
        actual = t['source_blocks'][key]
        original = node.get('alt') if kind == 'alt' else text(node)
        check('nonempty_plain_shahmukhi:'+key, bool(re.search('[\u0600-\u06ff]',actual)) and len(ET.fromstring('<f>'+actual+'</f>')) == 0)
        check('no_numeric_content_added:'+key, re.findall(r'\d+',original) == re.findall(r'\d+',actual) == [])
        check('clean_unicode:'+key, not FORBIDDEN.search(actual))
    paragraph = t['source_blocks']['fs-id1170653837691']
    terms = ['پورے عدداں','صحیح عدداں','کسراں','اعشاری عدداں']
    check('all_four_number_categories_once', all(paragraph.count(x) == 1 for x in terms))
    check('number_categories_source_order', [paragraph.index(x) for x in terms] == sorted(paragraph.index(x) for x in terms))
    check('metaphor_review_and_purpose_preserved', all(x in paragraph for x in ['جیویں','اویں ای','پکی نیہہ','حساب دے عملاں','مُڑ ویکھدے آں','تاں جے','سہارا']))
    check('no_claimed_source_corrections', t['source_corrections'] == m['source_discrepancies'] == [])
    check('source_title_agrees', t['title'] == t['source_blocks']['m82451/title'] == m['module_title_pnb'])
    bridge = ET.fromstring(t['bridge_after_html'])
    check('original_bridge_labeled', bridge.get('id') == 'a10-introduction-bridge' and bridge.get('data-origin') == 'original-bridge')
    check('five_exact_original_term_labels', [text(x) for x in bridge.findall('dl/dt')]
          == ['پورے عدد','صحیح عدد','کسراں','اعشاری عدد','حساب دے عمل'])
    check('five_ltr_english_terms', [text(x) for x in bridge.findall('.//bdi[@dir="ltr"][@lang="en"]')]
          == ['whole numbers','integers','fractions','decimals','arithmetic operations'])
    check('five_urdu_bridge_spans', len(bridge.findall('.//span[@lang="ur-Arab-PK"]')) == 5)
    check('bridge_does_not_claim_native_certification', 'عارضی' in text(bridge) and 'منظوری دا دعویٰ نہیں' in text(bridge))
    return specs


def validate_reader(d, source, t, m, check=require):
    check('exact_locale_and_direction', d.attrib == {'lang':'pnb-Arab-PK','dir':'rtl'})
    check('head_and_body_only', [x.tag for x in d] == ['head','body'])
    check('reader_scope_title', text(d.find('head/title')) == t['title']+' — A10 introduction')
    check('reader_body_classes', d.find('body').get('class') == 'a10-reader a10-introduction')
    check('body_top_level_order', [x.tag for x in d.find('body')] == ['header','main','footer'])
    metadata = source.find(N+'metadata')
    for name in ['content-id','title','abstract','uuid']:
        nodes = d.findall('head/meta[@name="source-'+name+'"]')
        check('source_metadata:'+name, len(nodes) == 1 and nodes[0].get('content') == (metadata.find(MD+name).text or ''))
    check('source_document_class_metadata', d.find('head/meta[@name="source-document-class"]').get('content') == source.get('class'))
    check('source_title_exactly_once_visible', len(d.findall('.//h1')) == 1
          and d.find('.//h1').get('data-source-key') == 'm82451/title')
    article = by_id(d,'a10-introduction-source')
    check('entire_source_article_exact_nodes_attributes_text_tails', signature(article) == signature(expected_source_article(source,t,m)))
    ids = [n.get('id') for n in d.iter() if n.get('id')]
    check('unique_reader_ids', len(ids) == len(set(ids)))
    source_ids = m['source_ids_in_document_order']
    check('source_ids_exact_order', [x for x in ids if x in source_ids] == source_ids)
    parent = {c:p for p in d.iter() for c in p}
    for sid in source_ids:
        n=by_id(d,sid); ancestors=[]; p=parent.get(n)
        while p is not None:
            if p.get('id') in source_ids: ancestors.insert(0,p.get('id'))
            p=parent.get(p)
        check('source_ancestry:'+sid, ancestors == m['source_ancestor_ids'][sid])
    check('all_four_source_key_markers_exact', [n.get('data-source-key') for n in article.iter() if n.get('data-source-key')] == list(source_blocks(source)))
    check('only_source_article_has_source_nodes', all(n in set(article.iter()) for n in d.iter() if n.get('data-source-tag')))
    check('no_formula_table_exercise_source_injection', not any(n.tag.rsplit('}',1)[-1] in ['math','table','aside','ol','ul'] for n in article.iter()))
    actual_bridge = by_id(d,'a10-introduction-bridge')
    check('original_bridge_exact_and_separate', signature(actual_bridge) == signature(ET.fromstring(t['bridge_after_html']))
          and parent[actual_bridge].tag == 'main' and actual_bridge not in set(article.iter()))
    main = d.find('body/main')
    check('complete_main_children_order', [(x.tag,x.get('id'),x.get('class')) for x in main]
          == [('p',None,'source-label'),('article','a10-introduction-source',None),('section','a10-introduction-bridge','bridge'),('p',None,'status')])
    check('main_has_no_unkeyed_text', not (main.text or '').strip() and all(not (x.tail or '').strip() for x in main))
    check('scope_and_pending_work_visible', 'پورا ماڈیول' in text(main[0]) and 'پوری کتاب نہیں' in text(main[0])
          and 'm82630' in text(main[-1]) and 'پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے' in text(main[-1]))
    check('responsive_photo_rule', '.a10-introduction .source-media img' in text(d.find('head/style'))
          and 'max-width:975px; min-width:0; height:auto' in text(d.find('head/style')))
    check('shared_css_retained_verbatim', text(d.find('head/style')).startswith((BASE/'styles/reader.css').read_text(encoding='utf-8')))
    footer=by_id(d,'credits')
    check('one_footer_ltr_english', len(d.findall('.//footer')) == 1 and footer.get('dir') == 'ltr' and footer.get('lang') == 'en')
    check('bounded_footer_shape', [x.tag for x in footer] == ['h2']+['p']*7 and not (footer.text or '').strip())
    ftext=text(footer)
    check('exact_book_authors_retained', all(name in ftext for name in AUTHORS) and 'Original senior contributing authors' in ftext)
    check('not_a30_attribution', not any(x in ftext for x in ['Precalculus','Jay Abramson','David Lippman','m49301']))
    credit=by_id(d,'a10-introduction-art-credit')
    spans=credit.findall('span[@data-origin="retained-source-credit"]')
    check('exact_raw_source_default_art_credit_visible', len(spans) == 1 and text(spans[0]) == CREDIT)
    expected_credit = ET.Element('p',{'id':'a10-introduction-art-credit'})
    expected_credit.text = 'Raw-source default art credit: '
    retained = ET.SubElement(expected_credit,'span',{'data-origin':'retained-source-credit'})
    retained.text = CREDIT; retained.tail = ' The '
    credit_link = ET.SubElement(expected_credit,'a',{'href':m['upstream_url']+'/blob/'+m['commit']+'/modules/m82630/index.cnxml'})
    credit_link.text = 'pinned raw preface, paragraph eip-787'
    credit_link.tail = ' supplies this wording for art without attribution in the text. No photographer is named in m82451. Book authors are not credited as photographers. The source statement and media identity evidence are retained, not independently verified as image-specific clearance; component-specific permissions and restrictions remain binding.'
    check('entire_raw_credit_paragraph_exact', signature(credit) == signature(expected_credit))
    check('art_credit_claim_limits_visible', all(x in text(credit) for x in ['Raw-source default art credit','pinned raw preface, paragraph eip-787',
          'No photographer is named','Book authors are not credited as photographers','not independently verified as image-specific clearance','component-specific permissions and restrictions remain binding']))
    check('existing_license_and_no_new_clearance', 'subject to component-specific credits and restrictions' in ftext and 'No new clearance is asserted.' in ftext)
    check('nonendorsement_retained', 'OpenStax and Rice University do not endorse this translation.' in ftext and 'names, logos and marks are not licensed' in ftext)
    check('source_publication_claim_not_punjabi_completion', 'source release, not this local Punjabi reader' in ftext and 'workflow remains unfinished' in ftext
          and 'not a training or fine-tuning dataset' in ftext)
    check('metadata_and_terminal_lf_disclosure', 'including the original title' in ftext and 'plus one terminal LF' in ftext)
    all_links=[n.get('href') for n in d.iter('a')]
    source_url=m['upstream_url']+'/blob/'+m['commit']+'/'+m['path']
    preface_url=m['upstream_url']+'/blob/'+m['commit']+'/modules/m82630/index.cnxml'
    check('source_and_credit_links_exact', source_url in all_links and preface_url in all_links)
    check('required_retained_local_notice_links', all(x in all_links for x in ['../provenance/A10-release/NOTICE.txt','../provenance/upstream--osbooks-prealgebra-bundle/LICENSE','../provenance/a10-introduction-component-notices.json','../source-excerpts/a10-introduction.cnxml','../source-excerpts/manifest-a10-introduction.json']))
    check('no_invented_source_links', not any(n.get('data-source-target') for n in d.iter()))
    resolved=[]
    for href in all_links:
        parsed=urlsplit(href)
        if parsed.scheme or parsed.netloc: continue
        if parsed.path:
            path=(READER.parent/unquote(parsed.path)).resolve()
            check('local_reference_exists:'+href, path.is_file() and path.is_relative_to(BASE.resolve()))
        elif parsed.fragment:
            check('local_anchor_exists:'+href, parsed.fragment in ids)
        resolved.append(href)
    return resolved


def validate_image_digest(actual, original, spec, check=require):
    check('exact_original_image_digest', actual == original == spec['sha256'])


def validate_notices(notices, m, t, check=require):
    spec=m['images'][0]
    actual=BASE/spec['path']; original=ROOT/spec['canonical_local_path']
    validate_image_digest(sha(actual),sha(original),spec,check)
    check('copied_image_exact_bytes', actual.read_bytes() == original.read_bytes() and actual.stat().st_size == spec['bytes'])
    check('original_and_copy_dimensions', jpeg_dimensions(original.read_bytes()) == jpeg_dimensions(actual.read_bytes()) == (spec['width'],spec['height']) == (975,450))
    check('component_notice_schema_scope', (notices['schema'],notices['unit'],notices['module'],notices['collection'],notices['commit'])
          == ('a10-retained-component-evidence-v1','A10-introduction','m82451','col31130',m['commit']))
    check('notice_source_manifest_hashes', notices['manifest_sha256'] == sha(MANIFEST) and notices['excerpt_sha256'] == m['excerpt_sha256'])
    check('notice_named_book_credits', notices['original_senior_contributing_authors'] == t['retained_attribution']['original_senior_contributing_authors'] == AUTHORS)
    check('notice_inputs_retained_exact', notices['existing_notice_inputs'] == m['existing_notice_inputs'])
    check('notice_lf_hash_policy_explicit', notices['existing_notice_input_hash_policy'] == m['existing_notice_input_hash_policy']
          == 'SHA-256 after CRLF-to-LF normalization in memory; files are not rewritten. Other explicitly raw source/image/media-manifest hashes remain raw-byte hashes.')
    for item in m['existing_notice_inputs']:
        check('existing_notice_logical_lf_hash:'+item['path'], digest((ROOT/item['path']).read_bytes().replace(b'\r\n',b'\n')) == item['sha256'])
    check('release_notice_verbatim', notices['release_notice_verbatim'] == (BASE/'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'))
    check('license_and_nonendorsement_from_manifest', notices['existing_license_statement'] == m['retained_book_attribution']['existing_license_statement']
          and notices['non_endorsement'] == m['retained_book_attribution']['non_endorsement'])
    credit=m['source_art_default_credit_provenance']; preface=ROOT/credit['canonical_local_path']
    check('raw_default_credit_source_hash', sha(preface) == credit['module_sha256'])
    source_credit=text(by_id(ET.parse(preface).getroot(),credit['paragraph_id']))
    check('raw_default_credit_and_component_limits_verbatim', notices['raw_source_art_attribution_paragraph_verbatim'] == source_credit
          and source_credit.endswith(CREDIT) and 'limitations provided in the credit' in source_credit)
    check('default_credit_provenance_exact', notices['source_art_default_credit_provenance'] == credit
          and credit['exact_credit'] == t['retained_attribution']['source_art_default_credit'] == CREDIT)
    check('one_component_record', len(notices['images']) == 1)
    record=notices['images'][0]
    for key in ['figure_id','figure_class','media_id','source_path','path','sha256','bytes','width','height','source_art_default_credit']:
        check('component_image_field:'+key, record[key] == spec[key])
    authority=ROOT/notices['media_authority_manifest']['path']
    check('media_authority_hash', sha(authority) == notices['media_authority_manifest']['sha256'])
    with authority.open(encoding='utf-8-sig',newline='') as handle:
        row=next(x for x in csv.DictReader(handle) if x['relative_path'] == spec['source_path'])
    check('existing_image_row_verbatim', record['existing_media_authority_row'] == row)
    data=actual.read_bytes()
    check('copied_image_matches_git_blob', row['sha256'] == sha(actual) and int(row['bytes']) == len(data)
          and row['git_blob_sha1'] == hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
    check('no_new_notice_clearance', 'no new component-specific clearance determination' in notices['rights_status']
          and 'not rights holders or permissions' in notices['credit_limit']
          and record['component_clearance'] == 'Not newly assessed; subject to retained component-specific credits and restrictions.')
    check('notice_no_completion_claim', notices['whole_book_translation_complete'] is False
          and notices['earlier_collection_items_pending'] == m['earlier_collection_items_still_pending'])


def mutation_tests(d, source, t, m, notices, check=require):
    names=[]
    def reject(name, mutate, validate, original):
        mutant=copy.deepcopy(original); mutate(mutant)
        try: validate(mutant)
        except (AssertionError,ValueError,KeyError,ET.ParseError):
            check(name,True); names.append(name)
        else: raise AssertionError(name+':mutation_survived')
    validate=lambda x: validate_reader(x,source,t,m)
    def reorder_source_children(x):
        content=by_id(x,'a10-introduction-source').find('section')
        content[:] = list(reversed(content))
    def move_media_outside_figure(x):
        figure=by_id(x,'CNX_ElemAlg_Figure_01_00_001'); wrapper=figure.find('div')
        figure.remove(wrapper)
        by_id(x,'a10-introduction-source').find('section').append(wrapper)
    reject('mutation_source_paragraph_digits',lambda x:setattr(by_id(x,'fs-id1170653837691'),'text',by_id(x,'fs-id1170653837691').text+' 999'),validate,d)
    reject('mutation_image_alt',lambda x:by_id(x,'fs-id1170654013255').set('alt','بدلیا ہویا متن'),validate,d)
    reject('mutation_image_source',lambda x:by_id(x,'fs-id1170654013255').set('src','../assets/a10/tryit.png'),validate,d)
    reject('mutation_splash_identity',lambda x:by_id(x,'CNX_ElemAlg_Figure_01_00_001').set('class','ordinary'),validate,d)
    reject('mutation_image_wrapper_text',lambda x:setattr(by_id(x,'CNX_ElemAlg_Figure_01_00_001').find('div'),'text','x=999'),validate,d)
    reject('mutation_caption_markup',lambda x:ET.SubElement(by_id(x,'CNX_ElemAlg_Figure_01_00_001').find('figcaption'),'b').__setattr__('text','اضافہ'),validate,d)
    reject('mutation_unkeyed_source_paragraph',lambda x:ET.SubElement(by_id(x,'a10-introduction-source').find('section'),'p').__setattr__('text','f(2)=999'),validate,d)
    reject('mutation_source_child_order',reorder_source_children,validate,d)
    reject('mutation_media_moved_outside_figure',move_media_outside_figure,validate,d)
    reject('mutation_missing_metadata',lambda x:x.find('head/meta[@name="source-uuid"]').set('content','wrong-uuid'),validate,d)
    reject('mutation_duplicate_visible_title',lambda x:ET.SubElement(x.find('body/header'),'h1').__setattr__('text',t['title']),validate,d)
    reject('mutation_bridge_relabel',lambda x:by_id(x,'a10-introduction-bridge').set('data-origin','source'),validate,d)
    reject('mutation_bridge_in_source',lambda x:by_id(x,'a10-introduction-source').append(copy.deepcopy(by_id(x,'a10-introduction-bridge'))),validate,d)
    reject('mutation_art_credit_erasure',lambda x:by_id(x,'a10-introduction-art-credit').find('span').__setattr__('text','OpenStax'),validate,d)
    reject('mutation_credit_overclaim',lambda x:by_id(x,'a10-introduction-art-credit').find('a').__setattr__('tail',' All image rights independently cleared.'),validate,d)
    reject('mutation_hidden_source_credit',lambda x:by_id(x,'a10-introduction-art-credit').find('span').set('hidden','hidden'),validate,d)
    reject('mutation_source_link',lambda x:x.find('body/footer/p/a').set('href','https://example.invalid/wrong-module'),validate,d)
    reject('mutation_notice_book_author_erasure',lambda x:x['original_senior_contributing_authors'].pop(),lambda x:validate_notices(x,m,t),notices)
    reject('mutation_notice_default_credit',lambda x:x.__setitem__('raw_source_art_attribution_paragraph_verbatim',CREDIT),lambda x:validate_notices(x,m,t),notices)
    reject('mutation_translation_missing_key',lambda x:x['source_blocks'].pop('fs-id1170653837691'),lambda x:validate_translation(x,source,m),t)
    reject('mutation_translation_number_type_erasure',lambda x:x['source_blocks'].__setitem__('fs-id1170653837691',x['source_blocks']['fs-id1170653837691'].replace('صحیح عدداں','پورے عدداں')),lambda x:validate_translation(x,source,m),t)
    reject('mutation_manifest_count_inflation',lambda x:x['source_counts'].__setitem__('translated_text_blocks',5),lambda x:validate_source(source,x),m)
    spec=m['images'][0]
    reject('mutation_detached_image_digest',lambda x:x.__setitem__('digest','0'*64),lambda x:validate_image_digest(x['digest'],spec['sha256'],spec),{'digest':spec['sha256']})
    return names


def main():
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    t=json.loads(TRANSLATION.read_text(encoding='utf-8'))
    source=ET.parse(EXCERPT).getroot()
    inputs=[MANIFEST,TRANSLATION,EXCERPT,BASE/'sources.lock.json',BASE/'styles/reader.css',BASE/'canon/examples.json',
            BASE/'qa/a10-introduction-language-notes.md',BASE/'scripts/prepare_a10.py',BASE/'scripts/qa_notation.py',
            BASE/'scripts/prepare_a10_introduction.py',BASE/'scripts/build_a10_introduction.py',Path(__file__).resolve(),
            ROOT/m['canonical_local_path'],ROOT/m['release_authority_path'],ROOT/m['indonesian_comparison_path'],
            ROOT/m['images'][0]['canonical_local_path'],ROOT/m['source_art_default_credit_provenance']['canonical_local_path'],
            *[ROOT/x['path'] for x in m['existing_notice_inputs']],*sorted((BASE/'canon/receipts').glob('A10-introduction-*.json'))]
    before={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    checks=[]
    def check(name,condition):
        require(name,condition); checks.append(name)
    prepare=[sys.executable,'-B',str(BASE/'scripts/prepare_a10_introduction.py')]
    build=[sys.executable,'-B',str(BASE/'scripts/build_a10_introduction.py')]
    subprocess.run(prepare,check=True); first_notice=NOTICES.read_bytes()
    subprocess.run(prepare,check=True)
    check('deterministic_notice_preparation',NOTICES.read_bytes()==first_notice)
    subprocess.run(build,check=True); first_reader=READER.read_bytes()
    subprocess.run(build,check=True)
    check('deterministic_reader_build',READER.read_bytes()==first_reader)
    d=parse_reader(first_reader.decode('utf-8')); notices=json.loads(first_notice)
    counts=validate_source(source,m,check)
    validate_translation(t,source,m,check)
    links=validate_reader(d,source,t,m,check)
    validate_notices(notices,m,t,check)
    for name,raw in [('translation',TRANSLATION.read_text(encoding='utf-8')),('reader',first_reader.decode('utf-8'))]:
        check('unicode_clean:'+name,not FORBIDDEN.search(raw))
        check('no_placeholder:'+name,not re.search(r'\{\{[^{}]*\}\}|\bTODO\b',raw))
    asset_before=sha(BASE/m['images'][0]['path'])
    mutations=mutation_tests(d,source,t,m,notices,check)
    check('detached_mutations_leave_outputs_unchanged',first_reader==READER.read_bytes() and first_notice==NOTICES.read_bytes())
    check('detached_mutations_leave_image_unchanged',asset_before==sha(BASE/m['images'][0]['path']))
    after={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    check('all_checked_inputs_stable',before==after)
    after.update({p.relative_to(ROOT).as_posix():sha(p) for p in [READER,NOTICES,BASE/m['images'][0]['path']]})
    receipt={
        'unit':'A10-introduction','module':'m82451','status':'structural_pass_visual_and_native_review_separate',
        'coverage':'Entire m82451 title and content; whole textbook/five-work workflow incomplete.',
        'source_keys':list(source_blocks(source)),'translated_source_blocks':4,'source_ids':m['source_ids_in_document_order'],
        'source_counts':counts,'source_mathml_trees':0,'source_links':0,
        'canonical_serialization':'1066 canonical LF bytes, unchanged; witness adds one terminal LF after closing document only.',
        'metadata':'Original title/content-id/empty abstract/uuid retained as head metadata; one translated visible h1.',
        'source_art_credit':CREDIT,'image':m['images'][0],
        'resolved_local_links':links,'checks':checks,'detached_mutations':mutations,'hashes':after,
        'limitations':[
            'Exact source-tree, role, text and metadata checks do not certify native Punjabi idiomaticity or all semantic translation choices.',
            'The number-category order and selected metaphor/purpose phrases are bounded self-review guards, not a general translation-quality model.',
            'No formulas or numeric examples occur here; numeral checks only reject additions to source text.',
            'Image pixels and dimensions are bound to the canonical original; a prior original-detail inspection saw construction work. The automated suite does not interpret photograph content.',
            'The source default credit and existing component limits are retained as raw-source claims, not new image-specific clearance or a current-publication audit.',
            'HTML void elements are self-closed only in a detached XML inspection copy; browser layout, font shaping, responsive display, screen readers and keyboard behavior require parent visual/accessibility review.',
            'External URL availability is not network-tested. Local paths/anchors are checked. No original input or asset is mutated by negative tests.',
            'The full preface is only scoped in notes, not translated or included in this reader. All five whole-work assignments remain incomplete.'
        ]}
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'PASS: {len(checks)} checks; 4 source blocks; 3 source IDs; one original splash photograph; {len(mutations)} detached mutations.')


if __name__=='__main__':
    main()
