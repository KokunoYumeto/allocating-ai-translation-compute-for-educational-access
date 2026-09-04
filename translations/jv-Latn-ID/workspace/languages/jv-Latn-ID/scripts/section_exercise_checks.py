"""Finite production checks/readout for the complete first-module exercises."""
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from build_units import sha, tree_key
from config import LANG, TRACKS
from draft_units import merged_edits
from build import translated

UNIT = 'a00-section-exercises'
RULES_DIGEST = '3515f1383f855c7174d1d1ea52e732e8bea1767908e688d2c42f3589b1d9750c'


def at(root, path):
    for index in path:
        root = root[index]
    return root


def slot(node, name):
    return node.text if name == 'text' else node.tail if name == 'tail' else node.get(name)


def clean(value):
    value = re.sub(r'[ \t]+', ' ', value)
    value = re.sub(r' *\n *', '\n', value)
    return re.sub(r'\n{3,}', '\n\n', value).strip()


def validate(source, root, rules, track):
    assert track in TRACKS and sha((LANG/f'audio/{UNIT}.rules.json').read_bytes()) == RULES_DIGEST
    assert hashlib.sha256(json.dumps(rules,ensure_ascii=False,indent=2).encode()+b'\n').hexdigest() == RULES_DIGEST
    scope=rules['scope']
    assert sha(tree_key(source).encode()) == scope['source_section_tree_sha256']
    assert [n.get('id') for n in source.iter() if n.get('id')] == scope['source_ids']
    expected=source if track=='id-academic' else translated(source,track,merged_edits(UNIT))
    assert tree_key(root)==tree_key(expected), 'Changed complete exercise target'
    assert sha((LANG/f'translation/{UNIT}.edits.json').read_bytes())==scope['edits_sha256']
    assert sha((LANG/'translation/phrases.json').read_bytes())==scope['shared_edits_sha256']
    tops={n.get('id'):n for n in source}
    targets={n.get('id'):n for n in root}
    fixtures={short:{r['id']:r for r in rules[group]} for short,group in
              [('math','math_fixtures'),('prose','prose_fixtures'),('chart','chart_fixtures')]}
    assert [n.get('id') for n in source]==scope['top_level_anchors']
    used={'math':set(),'prose':set(),'chart':set()}
    output=[]
    for block in rules['block_fixtures']:
        s=at(tops[block['top_level_anchor']],[block['child_index_zero_based']])
        t=at(targets[block['top_level_anchor']],[block['child_index_zero_based']])
        literal=ET.fromstring(block['source_cnxml'])
        assert tree_key(s)==tree_key(literal) and sha(tree_key(s).encode())==block['source_tree_sha256']
        assert sha(tree_key(t).encode())==block['target_tree_sha256'][track]
        pieces=[]
        for item in block['content_sequence']:
            kind=item['kind']
            if kind=='boundary': pieces.append('\n')
            elif kind=='answer_cue': pieces.append(rules['answer_policy']['cue'][track]+'\n')
            elif kind=='replayed_literal':
                sn,tn=at(s,item['path']),at(t,item['path'])
                assert slot(sn,item['slot'])==item['source_text']
                assert slot(tn,item['slot'])==item['expected'][track]
                pieces.append(item['expected'][track])
            elif kind=='prose_fixture':
                f=fixtures['prose'][item['fixture']];sn,tn=at(s,item['path']),at(t,item['path'])
                assert slot(sn,f['slot'])==f['source_text'] and slot(tn,f['slot'])==f['translated_text'][track]
                pieces.append(f['expected'][track]);used['prose'].add(f['id'])
            elif kind=='math':
                f=fixtures['math'][item['fixture']];sn=at(s,item['path'])
                assert tree_key(sn)==tree_key(ET.fromstring(f['source_mathml'])) and sha(tree_key(sn).encode())==f['source_tree_sha256']
                pieces.append(f['expected'][track]);used['math'].add(f['id'])
            elif kind=='chart':
                f=fixtures['chart'][item['fixture']];sn,tn=at(s,item['path']),at(t,item['path'])
                assert sn.get('id')==f['media_id'] and sn.get('alt')==f['source_alt']
                assert tn.get('alt')==f['target_alt'][track]
                pieces.append(f['expected'][track]);used['chart'].add(f['id'])
            else: raise AssertionError('Unsupported content sequence kind: '+kind)
        speech=clean(''.join(pieces))
        expected_speech=block['expected'][track]
        assert re.sub(r'\s+',' ',speech).strip()==re.sub(r'\s+',' ',expected_speech).strip(), block['id']
        # Preserve reviewed paragraph boundaries after independently checking
        # every source slot and the full ordered semantic composition above.
        speech=expected_speech
        assert block['generated_mark'].startswith('m81243--')
        output.append((block['generated_mark'].removeprefix('m81243--'),speech))
    assert len(output)==len(set(m for m,_ in output))==80
    assert used=={key:set(fixtures[key]) for key in used}
    assert sum(n.tag.endswith('}solution') for n in source.iter())==29
    assert len(list(source.iter('{http://cnx.rice.edu/cnxml}exercise')))==58
    return output


def blocks(root,track,rules,source):
    return validate(source,root,rules,track)
