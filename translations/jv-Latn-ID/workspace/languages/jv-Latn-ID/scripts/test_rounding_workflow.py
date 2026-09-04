"""Persistent production checks, distinct from the earlier draft guard model."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from build import MATH, XML_LANG, render
from build_units import BoundMath, blocks, narrate, products, source_bound_math
from config import LANG, TRACKS
from prepare_rounding_bindings import at, products as binding_products
from rounding_checks import ID_NOTE, UNIT, digest, RULES_DIGEST


class RoundingWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = json.loads((LANG / f'audio/{UNIT}.rules.json').read_text(encoding='utf-8'))
        cls.roots = {t:ET.parse(LANG/f'translation/{UNIT}.{t}.cnxml').getroot() for t in TRACKS}
        cls.source = cls.roots['id-academic']
        cls.bounds = {t:source_bound_math(r,cls.rules,t,cls.source) for t,r in cls.roots.items()}

    def test_complete_inventory_and_math_contexts(self):
        self.assertEqual(digest(self.rules),RULES_DIGEST)
        self.assertEqual(len(self.source),30)
        self.assertEqual(len(self.source.findall('.//{*}exercise')),9)
        self.assertEqual(len(self.source.findall('.//{*}solution')),9)
        self.assertEqual(len(self.source.findall('.//{*}media')),23)
        for track, root in self.roots.items():
            bound = self.bounds[track]
            self.assertEqual(len(bound),69)
            self.assertEqual(len(bound.prose_only),11)
            for fixture in self.rules['math_fixtures']:
                node = at(root,fixture['source_path'])
                with self.subTest(track=track,fixture=fixture['id']):
                    if fixture['required_complete_context']:
                        with self.assertRaises(ValueError):
                            narrate(node,track,UNIT,bound,self.rules)
                    else:
                        self.assertEqual(narrate(node,track,UNIT,bound,self.rules),fixture['expected'][track])

    def test_all_blocks_tables_charts_and_source_answers(self):
        for track,root in self.roots.items():
            actual = blocks(root,track,UNIT,self.rules,self.source)
            self.assertEqual([text for _,text in actual],[f['expected'][track] for f in self.rules['block_fixtures']])
            self.assertEqual(['m81243--'+mark for mark,_ in actual],self.rules['ssml_contract']['block_marks'])
            for group in ('table_fixtures','chart_fixtures'):
                for f in self.rules[group]:
                    self.assertEqual(narrate(at(root,f['source_path']),track,UNIT,self.bounds[track],self.rules),f['expected'][track])
            nodes = {n.get('id'):n for n in root.iter() if n.get('id')}
            for e in self.rules['exercise_inventory']:
                for kind,key in [('problem','expected_question'),('solution','expected_solution')]:
                    self.assertEqual(narrate(nodes[e[kind+'_id']],track,UNIT,self.bounds[track],self.rules),e[key][track])

    def test_copied_nodes_and_fake_bindings_rejected(self):
        for track,root in self.roots.items():
            bound = self.bounds[track]
            candidates = list(root) + list(root.iter('{' + MATH + '}math'))
            candidates += root.findall('.//{*}media') + root.findall('.//{*}table')
            for node in candidates:
                with self.subTest(track=track,tag=node.tag,source_id=node.get('id')):
                    with self.assertRaises(ValueError):
                        narrate(copy.deepcopy(node),track,UNIT,bound,self.rules)
            for fake in ({},dict(bound),BoundMath()):
                with self.assertRaises(ValueError):
                    narrate(root[1],track,UNIT,fake,self.rules)
            with self.assertRaises(ValueError):
                narrate(root[1],'id-academic' if track.startswith('jv') else 'jv-academic',UNIT,bound,self.rules)

    def test_post_binding_changes_anywhere_rejected(self):
        for track in TRACKS:
            source,root = copy.deepcopy(self.source),copy.deepcopy(self.roots[track])
            bound = source_bound_math(root,self.rules,track,source)
            root[-1].set('unregistered','changed')
            with self.assertRaises(ValueError):
                narrate(root[1],track,UNIT,bound,self.rules)
            del root[-1].attrib['unregistered']
            source[1].text = 'Changed source prose'
            with self.assertRaises(ValueError):
                narrate(root[1],track,UNIT,bound,self.rules)

    def test_each_block_changed_source_or_target_rejected(self):
        for track in TRACKS:
            for index in range(30):
                root = copy.deepcopy(self.roots[track])
                root[index].set('changed','yes')
                with self.subTest(track=track,index=index),self.assertRaises((AssertionError,ValueError)):
                    source_bound_math(root,self.rules,track,self.source)
        for index in range(30):
            source = copy.deepcopy(self.source)
            source[index].tail = 'Inserted tail fact'
            with self.assertRaises((AssertionError,ValueError)):
                source_bound_math(self.roots['jv-academic'],self.rules,'jv-academic',source)

    def test_mutable_cache_and_forged_snapshot_cannot_authorize_speech(self):
        from build_units import tree_key
        for track in TRACKS:
            source,root = copy.deepcopy(self.source),copy.deepcopy(self.roots[track])
            bound = source_bound_math(root,self.rules,track,source)
            original = bound.rounding_speech[id(root[1])]
            bound.rounding_speech[id(root[1])] = 'INJECTED wrong population'
            with self.assertRaises(ValueError):
                narrate(root[1],track,UNIT,bound,self.rules)
            bound.rounding_speech[id(root[1])] = original
            key = next(iter(bound))
            bound[key] = 'INJECTED math'
            with self.assertRaises(ValueError):
                narrate(root[1],track,UNIT,bound,self.rules)
            bound[key] = self.rules['math_fixtures'][0]['expected'][track]
            context = set(bound.prose_only)
            bound.prose_only.clear()
            with self.assertRaises(ValueError):
                narrate(root[1],track,UNIT,bound,self.rules)
            bound.prose_only = context
            root[-1].set('injected','changed')
            bound.rounding_snapshots = (tree_key(source),tree_key(root))
            with self.assertRaises(ValueError):
                narrate(root[1],track,UNIT,bound,self.rules)

    def test_every_fixture_speech_mutation_rejected(self):
        groups = ('math_fixtures','prose_fixtures','chart_fixtures','table_fixtures','block_fixtures','structural_cues')
        for group in groups:
            for index in range(len(self.rules[group])):
                changed = copy.deepcopy(self.rules)
                changed[group][index]['expected']['jv-academic'] += ' salah'
                with self.subTest(group=group,index=index),self.assertRaises(AssertionError):
                    source_bound_math(self.roots['jv-academic'],changed,'jv-academic',self.source)

    def test_sequence_order_answer_cue_and_value_changes_rejected(self):
        mutations = [
            lambda r:r['block_fixtures'][20]['content_sequence'].reverse(),
            lambda r:r['block_fixtures'][21]['content_sequence'].clear(),
            lambda r:r['table_fixtures'][0]['row_fixtures'].reverse(),
            lambda r:r['math_fixtures'][2].update(required_complete_context=None),
            lambda r:r['numeric_and_answer_checks']['rounding_cases'][5].update(result_value=70),
            lambda r:r['answer_policy']['cue'].update({'jv-academic':'Wangsulan salah.'}),
            lambda r:r['exercise_inventory'][0]['expected_question'].update({'jv-academic':'Wangsulan wolung atus patang puluh.'}),
            lambda r:r['finite_cardinal_lexicon']['0'].update({'jv-academic':'siji'}),
            lambda r:r['chart_fixtures'][0]['source_path'].reverse(),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(self.rules)
            mutate(changed)
            with self.assertRaises(AssertionError):
                blocks(self.roots['jv-academic'],'jv-academic',UNIT,changed,self.source)

    def test_source_bound_assets_reject_tampered_payload(self):
        assets = json.loads((LANG/f'translation/{UNIT}.assets.json').read_text(encoding='utf-8'))['assets']
        original = Path.read_bytes
        for index in (0,3,8):
            target = LANG/assets[index]['outputs']['jv-academic']['path']
            def altered(path):
                raw = original(path)
                return raw+b'changed' if path == target else raw
            with patch.object(Path,'read_bytes',altered),self.assertRaises(AssertionError):
                source_bound_math(self.roots['jv-academic'],self.rules,'jv-academic',self.source)

    def test_registered_external_links_only(self):
        links = [n for n in self.source.iter() if n.get('url')]
        self.assertEqual(len(links),2)
        for node in links:
            html = render(node,UNIT+'--id-academic--',{})
            self.assertIn(node.get('url'),html)
            self.assertIn(node.text,html)
            changed = copy.deepcopy(node)
            changed.set('url','https://example.invalid/new-source')
            with self.assertRaises(ValueError):
                render(changed,UNIT+'--id-academic--',{})
            with self.assertRaises(ValueError):
                render(node,'a10-exponents--id-academic--',{})

    def test_saved_products_and_ssml_determinism(self):
        for path,raw in binding_products().items():
            self.assertEqual((LANG/path).read_bytes(),raw,path)
        generated = products(UNIT)
        self.assertEqual(generated,products(UNIT))
        for path,raw in generated.items():
            self.assertEqual((LANG/path).read_bytes(),raw,path)
        for track,(locale,_) in TRACKS.items():
            root = ET.fromstring(generated[f'review/audio/{UNIT}.{track}.ssml'])
            self.assertEqual(root.get(XML_LANG),locale)
            self.assertEqual([n.get('name') for n in root.findall('{*}mark')],self.rules['ssml_contract']['block_marks'])
            text = ''.join(root.itertext())
            self.assertEqual(text.count(ID_NOTE),int(track=='id-academic'))
            self.assertEqual(text.count(self.rules['answer_policy']['cue'][track]),6)

    def test_coverage_accepts_real_anonymous_title_derived_mark(self):
        from coverage import unit_build_coverage
        from build_units import sha
        raw = (LANG/f'qa/{UNIT}.draft-receipt.json').read_bytes()
        result = unit_build_coverage(UNIT,sha(raw),json.loads(raw),list(self.source))
        self.assertEqual(result['source_ids'],104)
        self.assertEqual(result['source_math_expressions'],69)
        self.assertFalse(result['whole_module_complete'])


if __name__ == '__main__':
    unittest.main()
