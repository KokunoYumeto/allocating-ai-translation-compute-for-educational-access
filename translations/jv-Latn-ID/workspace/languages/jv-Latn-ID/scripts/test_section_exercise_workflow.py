"""Production regression checks for all 58 exercises and complete self-check."""
import copy
import json
import re
import unittest
import xml.etree.ElementTree as ET

from build_units import blocks, products
from config import LANG, TRACKS
from draft_units import products as draft_products
from qa import Reader

UNIT='a00-section-exercises'
CN='{http://cnx.rice.edu/cnxml}'


class SectionExerciseWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules=json.loads((LANG/f'audio/{UNIT}.rules.json').read_bytes())
        cls.source=ET.parse(LANG/f'translation/{UNIT}.id-academic.cnxml').getroot()
        cls.roots={track:ET.parse(LANG/f'translation/{UNIT}.{track}.cnxml').getroot() for track in TRACKS}

    def test_source_topology_fixture_census_and_all_readouts(self):
        self.assertEqual(len([n for n in self.source.iter() if n.get('id')]),273)
        self.assertEqual(len(list(self.source.iter(CN+'exercise'))),58)
        self.assertEqual(len(list(self.source.iter(CN+'solution'))),29)
        self.assertEqual(len(list(self.source.iter('{http://www.w3.org/1998/Math/MathML}math'))),57)
        self.assertEqual(len(list(self.source.iter(CN+'media'))),5)
        inventory=self.rules['exercise_inventory']
        self.assertEqual([row['ordinal'] for row in inventory],list(range(1,59)))
        self.assertEqual(sum(row['source_solution_present'] for row in inventory),29)
        self.assertEqual(sum(row['absent_in_both_sources'] for row in inventory),29)
        for track,root in self.roots.items():
            result=blocks(root,track,UNIT,self.rules,self.source)
            self.assertEqual(len(result),80)
            self.assertEqual(len({mark for mark,_ in result}),80)
            cue=self.rules['answer_policy']['cue'][track]
            self.assertEqual(sum(body.count(cue) for _,body in result),29)
            joined='\n'.join(body for _,body in result)
            self.assertNotRegex(joined,r'[ⓐⓑⓒⓓⓔ$]')
            self.assertIn(self.rules['chart_fixtures'][-1]['expected'][track],joined)

    def test_rounding_results_and_model_counts_independently_recomputed(self):
        checks=self.rules['numeric_and_answer_checks']
        for row in checks['rounding_provided']:
            for case in row['pairs']:
                value=int(case['source_value'].replace(',',''))
                place=case['rounding_unit']
                result=int(case['source_answer'].replace(',',''))
                lower=value//place*place;upper=lower+place
                self.assertEqual(result,upper if value-lower>=upper-value else lower)
        self.assertEqual([row['block_counts'] for row in self.rules['chart_fixtures'][:4]],[
            {'hundreds':5,'tens':6,'ones':1},{'hundreds':3,'tens':8,'ones':4},
            {'hundreds':4,'tens':0,'ones':7},{'hundreds':6,'tens':2,'ones':0}])
        self.assertEqual(self.rules['chart_fixtures'][-1]['logical_shape']['empty_choice_cells'],18)
        self.assertEqual(self.rules['chart_fixtures'][-1]['logical_shape']['preselected_choices'],0)

    def test_changed_source_target_rules_and_answers_fail_closed(self):
        source=copy.deepcopy(self.source);source[0][3].set('new','changed')
        with self.assertRaises(AssertionError):
            blocks(self.roots['jv-academic'],'jv-academic',UNIT,self.rules,source)
        target=copy.deepcopy(self.roots['jv-conversation']);target[-1][-1].text='INJECTED answer'
        with self.assertRaises(AssertionError):
            blocks(target,'jv-conversation',UNIT,self.rules,self.source)
        rules=copy.deepcopy(self.rules);rules['block_fixtures'][0]['expected']['id-academic']='wrong'
        with self.assertRaises(AssertionError):
            blocks(self.source,'id-academic',UNIT,rules,self.source)
        rules=copy.deepcopy(self.rules);rules['exercise_inventory'][-1]['source_solution_present']=True
        with self.assertRaises(AssertionError):
            blocks(self.source,'id-academic',UNIT,rules,self.source)

    def test_saved_drafts_reader_transcripts_and_ssml_are_deterministic(self):
        for name,raw in draft_products(UNIT).items():
            self.assertEqual((LANG/name).read_bytes(),raw,name)
        generated=products(UNIT)
        self.assertEqual(generated,products(UNIT))
        for name,raw in generated.items():
            self.assertEqual((LANG/name).read_bytes(),raw,name)
        reader=Reader();reader.feed(generated[f'review/units/{UNIT}.html'].decode())
        self.assertEqual(reader.maths,171)
        self.assertEqual(len(reader.images),15)
        self.assertEqual(len(reader.tracks),12)
        for track,(locale,_) in TRACKS.items():
            root=ET.fromstring(generated[f'review/audio/{UNIT}.{track}.ssml'])
            self.assertEqual(root.get('{http://www.w3.org/XML/1998/namespace}lang'),locale)
            marks=[n.get('name') for n in root.findall('{*}mark')]
            self.assertEqual(len(marks),len(set(marks)))
            self.assertEqual(len(marks),80)
            self.assertTrue(all(mark.startswith('m81243--') for mark in marks))

    def test_coverage_accepts_complete_nested_section_mark_contract(self):
        from coverage import unit_build_coverage
        from build_units import sha
        raw=(LANG/f'qa/{UNIT}.draft-receipt.json').read_bytes()
        result=unit_build_coverage(UNIT,sha(raw),json.loads(raw),list(self.source))
        self.assertEqual(result['source_ids'],273)
        self.assertEqual(result['source_math_expressions'],57)
        self.assertFalse(result['whole_module_complete'])


if __name__=='__main__': unittest.main()
