"""Non-writing negative tests for source/math/table safeguards."""
import copy, json, unittest
from pathlib import Path
from unittest.mock import patch
import build_module as b


class ModuleGuards(unittest.TestCase):
    def reject(self, relative, mutate, module='m81244'):
        path = b.L/relative
        data = json.loads(path.read_text(encoding='utf-8'))
        mutate(data)
        original = Path.read_text

        def altered(p, *args, **kwargs):
            return json.dumps(data,ensure_ascii=False) if p == path else original(p,*args,**kwargs)

        # A missed guard cannot overwrite an existing translation or receipt.
        with patch.object(Path,'read_text',altered), patch.object(Path,'write_bytes',side_effect=RuntimeError('Unexpected output write')):
            with self.assertRaises(AssertionError):
                b.build(module)

    def test_wrong_addition_result(self):
        self.reject('modules/m81244.json',lambda x: next(c for c in x['answer_cases'] if c['exercise']=='fs-id2325655')['addition_results'].__setitem__(0,113))

    def test_invented_source_solution(self):
        self.reject('modules/m81244.json',lambda x: next(c for c in x['answer_cases'] if c['exercise']=='fs-id2169300').__setitem__('source_solution_absent',False))

    def test_wrong_matrix_cell(self):
        self.reject('modules/m81244-image-tables.json',lambda x: x['CNX_BMath_Figure_01_02_216.jpg']['cells'][0].__setitem__(0,1))

    def test_wrong_blank_position(self):
        self.reject('modules/m81244-image-tables.json',lambda x: x['CNX_BMath_Figure_01_02_216.jpg']['cells'][0].__setitem__(0,None))

    def test_changed_quantity_in_translated_unit(self):
        self.reject('translations/m81244-text.bn.json',lambda x: x.__setitem__('16-ounce','17 আউন্সের'))

    def test_missing_translation(self):
        self.reject('translations/m81244-text.bn.json',lambda x: x.pop('Add Whole Numbers'))

    def test_wrong_subtraction_result(self):
        self.reject('modules/m81245.json',lambda x: next(c for c in x['answer_cases'] if c['exercise']=='fs-id2340048').__setitem__('subtraction_result',18),'m81245')

    def test_wrong_attribute_override_expectation(self):
        self.reject('modules/m81245.json',lambda x: next(o for o in x['slot_overrides'] if o['node_index']==295).__setitem__('expected','ভুল দৃশ্যবর্ণনা'),'m81245')

    def test_wrong_inverse_addition_check(self):
        self.reject('modules/m81245.json',lambda x: next(c for c in x['answer_cases'] if c['exercise']=='fs-id1397173')['inverse_addition_checks'].__setitem__(0,[4738,899,5638]),'m81245')


if __name__=='__main__': unittest.main(verbosity=2)
