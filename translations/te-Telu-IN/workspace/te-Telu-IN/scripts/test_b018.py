"""B018 read-only source/property checks; actual human-file cases follow draft."""
import copy
import unittest
import xml.etree.ElementTree as ET

from addition_recap_checks import (BASE,CN,MATH,XH,TABLE,IDENTITY,COMMUTATION,ALGORITHM,
    SOURCE_MATH,RELATION,addition,column_steps,compact,displayed_relations,equality,ids_of,
    math_signature,source_baseline,structure,text_of,validate_b018,validate_recap_bridge,
    validate_recap_target)
from build_unit import asset_map,localize,render,render_bridge,unit_inputs
from inspect_source import slots


class SourceBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = source_baseline()

    def test_complete_actual_source_inventory(self):
        root = source_baseline()
        self.assertEqual((len(list(root.iter())),len(list(slots(root))),len(ids_of(root))), (81,53,6))
        self.assertEqual(len(list(root.iter(MATH+'math'))),11)
        for name in ('exercise','problem','solution','media','image','link'):
            with self.subTest(name=name): self.assertEqual(len(list(root.iter(CN+name))),0)

    def test_all_eleven_actual_math_roots_preserved(self):
        self.assertEqual(tuple(compact(text_of(n)) for n in self.source.iter(MATH+'math')),SOURCE_MATH)
        self.assertEqual([n.text for n in self.source.iter(MATH+'mi')],['a','a','a','a','a','a','b','a','b','b','a'])

    def test_result_cell_names_sum_not_evaluated_seven(self):
        rows = ids_of(self.source)[TABLE].findall('.//'+CN+'row')
        self.assertEqual(text_of(rows[1][4]),'the sum of 3 and 4')
        self.assertNotIn('7',text_of(rows[1][4]))
        self.assertEqual(addition(text_of(rows[1][2])),(3,4))
        self.assertEqual(sum(addition(text_of(rows[1][2]))),7)

    def test_source_table_is_actually_five_columns(self):
        table = ids_of(self.source)[TABLE]
        self.assertEqual(table.find(CN+'tgroup').get('cols'),'5')
        self.assertEqual([len(r) for r in table.iter(CN+'row')],[5,5])
        self.assertEqual(len(table.findall(CN+'tgroup/'+CN+'colspec')),5)

    def test_both_identity_directions_and_commutation(self):
        ids = ids_of(self.source)
        self.assertEqual([compact(text_of(n)) for n in ids[IDENTITY].iter(MATH+'math')],['a','0','a+0=a','0+a=a'])
        self.assertEqual([compact(text_of(n)) for n in ids[COMMUTATION].iter(MATH+'math')],['a','b','a+b=b+a'])
        for number in (0,1,10,507,999):
            with self.subTest(number=number):
                self.assertEqual(equality(f'{number}+0={number}'),((number,0),(number,)))
                self.assertEqual(equality(f'0+{number}={number}'),((0,number),(number,)))
        for a,b in ((0,0),(0,7),(3,4),(4,3),(68,97)):
            with self.subTest(a=a,b=b): self.assertEqual(equality(f'{a}+{b}={b}+{a}'),((a,b),(b,a)))

    def test_exact_three_algorithm_steps_and_boundary(self):
        steps = ids_of(self.source)[ALGORITHM]
        self.assertEqual(len(steps),3)
        self.assertIn('lines up vertically',text_of(steps[0]))
        self.assertIn('right to left starting with the ones place',text_of(steps[1]))
        self.assertIn('more than 9',text_of(steps[1]))
        self.assertIn('carrying if needed',text_of(steps[2]))
        self.assertEqual(column_steps((5,4))[0][3:],(9,9,0))
        self.assertEqual(column_steps((5,5))[0][3:],(10,0,1))
        self.assertEqual(column_steps((9,9))[0][3:],(18,8,1))

    def test_carry_count_can_exceed_one_and_zero_is_written(self):
        rows = column_steps((76,87,59))
        self.assertEqual([r[3] for r in rows],[22,22,2])
        self.assertEqual([r[5] for r in rows],[2,2,0])
        self.assertEqual([r[4] for r in column_steps((497,8))],[5,0,5])
        self.assertEqual([r[4] for r in column_steps((998,7))],[5,0,0,1])
        self.assertEqual(column_steps((0,0)),((1,(0,0),0,0,0,0),))

    def test_equality_distinguishes_sum_from_concatenation_and_false_identity(self):
        for value in ('7+0=70','0+7=0','3+4=34','3+4=4+4','3+4=7=8','07+0=7','3-4=7'):
            with self.subTest(value=value), self.assertRaises(AssertionError): equality(value)
        self.assertEqual(equality('3+4=4+3=7'),((3,4),(4,3),(7,)))

    def test_signature_protects_operators_letters_and_interior_tails(self):
        before = math_signature(self.source)
        for tag,value in (('mi','c'),('mn','1'),('mo','-')):
            with self.subTest(tag=tag):
                changed=copy.deepcopy(self.source);next(changed.iter(MATH+tag)).text=value
                self.assertNotEqual(math_signature(changed),before)
        changed=copy.deepcopy(self.source);next(changed.iter(MATH+'mi')).tail='0'
        self.assertNotEqual(math_signature(changed),before)

    def test_indonesian_reference_exact_math_and_ids(self):
        module=ET.parse(BASE.parent/'downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml').getroot()
        section=ids_of(module)['fs-id1611455']
        self.assertEqual(math_signature(self.source),math_signature(section))
        self.assertEqual(list(ids_of(self.source)),list(ids_of(section)))

    def test_baseline_is_read_only(self):
        before=ET.tostring(self.source);source_baseline()
        self.assertEqual(ET.tostring(self.source),before)


class ActualTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_base,cls.meta,cls.catalog=unit_inputs('TE-B018')
        cls.target_base=localize(cls.source_base,cls.catalog,asset_map('TE-B018'))
        cls.bridge_base=ET.parse(BASE/'translations/TE-B018.bridge.xhtml').getroot()

    def setUp(self):
        self.target=copy.deepcopy(self.target_base)

    def node(self,ident):
        return ids_of(self.target)[ident]

    def mutate(self,ident,before,after):
        for node in self.node(ident).iter():
            for field in ('text','tail'):
                value=getattr(node,field)
                if value and before in value:
                    setattr(node,field,value.replace(before,after,1));return
        self.fail('Did not mutate actual B018 target text: '+before)

    def test_actual_catalog_localizes_complete_target(self):
        self.assertEqual(len(self.catalog['translations']),25)
        self.assertEqual(validate_recap_target(self.target),{
            'source_elements':81,'source_slots':53,'source_ids':6,'source_math_roots':11,
            'source_tables':1,'source_exercises':0})
        self.assertEqual(structure(self.target),structure(self.source_base))
        self.assertEqual(math_signature(self.target),math_signature(self.source_base))

    def test_combined_export_validates_actual_target_and_bridge(self):
        actual=validate_b018(self.target,copy.deepcopy(self.bridge_base))
        self.assertEqual((actual['source_math_roots'],actual['bridge_numeric_equalities'],
                          actual['bridge_self_checks']),(11,21,3))

    def test_result_name_remains_name_not_value_or_difference(self):
        row=self.node(TABLE).findall('.//'+CN+'row')[1]
        self.assertNotIn('7',text_of(row[4]))
        self.mutate(TABLE,'మూడు, నాలుగు అనే సంఖ్యల మొత్తం','మూడు, నాలుగు అనే సంఖ్యల తేడా')
        with self.assertRaisesRegex(AssertionError,'notation/result-name row'):
            validate_recap_target(self.target)

    def test_identity_prose_cannot_reverse_unchanged_formula(self):
        self.mutate(IDENTITY,'అదే సంఖ్య వస్తుంది','వేరే సంఖ్య వస్తుంది')
        self.assertEqual(math_signature(self.target),math_signature(self.source_base))
        with self.assertRaisesRegex(AssertionError,'identity meaning'):
            validate_recap_target(self.target)

    def test_commutation_prose_cannot_reverse_unchanged_formula(self):
        self.mutate(COMMUTATION,'మొత్తం మారదు','మొత్తం మారుతుంది')
        with self.assertRaisesRegex(AssertionError,'commutative meaning'):
            validate_recap_target(self.target)

    def test_exact10_carry_boundary_cannot_be_shifted(self):
        self.mutate(ALGORITHM,'మొత్తం 9 కంటే ఎక్కువైతే','మొత్తం 10 కంటే ఎక్కువైతే')
        with self.assertRaisesRegex(AssertionError,'exact three-step algorithm'):
            validate_recap_target(self.target)

    def test_symbolic_identifiers_are_unit_scoped_and_unchanged(self):
        identifiers=list(self.target.iter(MATH+'mi'))
        self.assertEqual({n.text for n in identifiers},{'a','b'})
        identifiers[0].text='c'
        with self.assertRaisesRegex(AssertionError,'MathML'):
            validate_recap_target(self.target)

    def test_shared_localizer_identifier_allowlist_is_not_generalized(self):
        catalog=copy.deepcopy(self.catalog);catalog['unit_id']='TE-B017'
        with self.assertRaisesRegex(AssertionError,'Untranslated prose'):
            localize(self.source_base,catalog,{})
        source=copy.deepcopy(self.source_base);next(source.iter(MATH+'mi')).text='c'
        with self.assertRaisesRegex(AssertionError,'Untranslated prose'):
            localize(source,self.catalog,{})

    def test_table_shape_and_ids_remain_source_exact(self):
        self.node(TABLE).find(CN+'tgroup').set('cols','4')
        with self.assertRaisesRegex(AssertionError,'structure'):
            validate_recap_target(self.target)

    def test_target_validation_is_read_only(self):
        before=ET.tostring(self.target);validate_recap_target(self.target)
        self.assertEqual(ET.tostring(self.target),before)


class ActualRendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_base,cls.meta,cls.catalog=unit_inputs('TE-B018')
        cls.target_base=localize(cls.source_base,cls.catalog,{})
        cls.bridge_base=ET.parse(BASE/'translations/TE-B018.bridge.xhtml').getroot()

    def setUp(self):
        self.target=copy.deepcopy(self.target_base)

    def node(self,ident):
        return ids_of(self.target)[ident]

    def rendered(self,english=False):
        root=self.source_base if english else self.target
        return ET.fromstring('<div>'+render(root,{},'en-' if english else '',english)+'</div>')

    def test_five_column_table_and_all_six_source_ids_render_bilingually(self):
        for english in (False,True):
            with self.subTest(english=english):
                root=self.rendered(english);prefix='en-' if english else ''
                ids=[n.get('id') for n in root.iter() if n.get('id')]
                self.assertEqual(set(ids),{prefix+i for i in ids_of(self.source_base)})
                self.assertEqual(len(ids),len(set(ids)))
                table=next(root.iter('table'));rows=list(table.iter('tr'))
                self.assertEqual([len(r) for r in rows],[5,5])
                self.assertTrue(all(n.get('scope')=='col' for n in rows[0]))
                self.assertEqual(table.get('aria-label'),self.node(TABLE).get('aria-label') if not english
                                 else ids_of(self.source_base)[TABLE].get('aria-label'))

    def test_rendered_symbolic_identifiers_and_math_count_remain_exact(self):
        for english in (False,True):
            with self.subTest(english=english):
                root=self.rendered(english)
                math=list(root.iter(MATH+'math'))
                self.assertEqual(len(math),11)
                self.assertEqual({n.text for n in root.iter(MATH+'mi')},{'a','b'})

    def test_bridge_render_preserves_ids_links_tables_and_scopes(self):
        before=ET.tostring(self.bridge_base)
        root=ET.fromstring(render_bridge(self.bridge_base))
        self.assertEqual(len(ids_of(root)),11)
        self.assertEqual(len(list(root.iter('a'))),9)
        tables=list(root.iter('table'));self.assertEqual(len(tables),2)
        self.assertEqual([[len(row) for row in table.iter('tr')] for table in tables],[[3,3,3,3],[4,4,4]])
        self.assertTrue(all(th.get('scope')=='col' for table in tables for th in table.findall('thead/tr/th')))
        self.assertTrue(all(th.get('scope')=='row' for table in tables for th in table.findall('tbody/tr/th')))
        self.assertEqual(ET.tostring(self.bridge_base),before)


class ActualBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge_base=ET.parse(BASE/'translations/TE-B018.bridge.xhtml').getroot()

    def setUp(self):
        self.bridge=copy.deepcopy(self.bridge_base)

    def node(self,ident,root=None):
        return ids_of(self.bridge if root is None else root)[ident]

    def mutate(self,ident,before,after,root=None):
        for node in self.node(ident,root).iter():
            for field in ('text','tail'):
                value=getattr(node,field)
                if value and before in value:
                    setattr(node,field,value.replace(before,after,1));return
        self.fail('Did not mutate actual B018 bridge text: '+before)

    def validate(self,root=None):
        return validate_recap_bridge(self.bridge if root is None else root)

    def test_actual_bridge_complete_math_and_routing(self):
        self.assertEqual(self.validate(),{'bridge_sections':5,'bridge_self_checks':3,
            'bridge_numeric_equalities':21,'bridge_ids':11,'bridge_links':9})
        self.assertEqual(len(displayed_relations(self.bridge)),21)

    def test_every_actual_numeric_equality_rejects_changed_result(self):
        import re
        blocks=[]
        for node in self.bridge.iter():
            if node.tag.rsplit('}',1)[-1] not in {'p','li','td','dd'}:continue
            if any(n is not node and n.tag.rsplit('}',1)[-1] in {'p','li','td','dd'} for n in node.iter()):continue
            blocks.extend((node,m.group()) for m in RELATION.finditer(text_of(node)))
        self.assertEqual(len(blocks),21);indices={id(n):i for i,n in enumerate(self.bridge.iter())}
        for index,(node,value) in enumerate(blocks):
            with self.subTest(index=index,value=value):
                root=copy.deepcopy(self.bridge);block=list(root.iter())[indices[id(node)]]
                token=list(re.finditer(r'\d+',value))[-1]
                changed=value[:token.start()]+str(int(token.group())+1)+value[token.end():]
                for inline in block.iter():
                    for field in ('text','tail'):
                        text=getattr(inline,field)
                        if text and value in text:
                            setattr(inline,field,text.replace(value,changed,1));break
                    else:continue
                    break
                with self.assertRaises(AssertionError):validate_recap_bridge(root)

    def test_result_name_cannot_be_replaced_by_seven(self):
        self.mutate('B018-K1','మూడు, నాలుగు అనే సంఖ్యల మొత్తం','7')
        with self.assertRaisesRegex(AssertionError,'result-name versus optional value'):self.validate()

    def test_optional_value_cannot_replace_expression_or_reading(self):
        for before in ('3+4','మూడు ప్లస్ నాలుగు'):
            with self.subTest(before=before):
                self.bridge=copy.deepcopy(self.bridge_base);self.mutate('B018-K1',before,'7')
                with self.assertRaisesRegex(AssertionError,'result-name versus optional value'):self.validate()

    def test_identity_requires_both_orders_and_zerozero_boundary(self):
        for before,after in [('a+0=a','a+1=a'),('0+a=a','1+a=a'),('0+0=0','0+0=00')]:
            with self.subTest(before=before):
                self.bridge=copy.deepcopy(self.bridge_base);self.mutate('B018-K2',before,after)
                with self.assertRaisesRegex(AssertionError,'identity/commutation support|numeric equalities'):self.validate()

    def test_same43_different_addends_do_not_substitute_for_property_example(self):
        self.mutate('B018-K2','18+25=43','17+26=43')
        self.assertEqual(equality('17+26=43'),((17,26),(43,)))
        with self.assertRaisesRegex(AssertionError,'identity/commutation support'):self.validate()

    def test_commutation_cannot_mean_reversing_digits(self):
        self.mutate('B018-K2','సంఖ్యలోని అంకెలను తిప్పవచ్చని చెప్పదు','సంఖ్యలోని అంకెలను తిప్పవచ్చని చెబుతుంది')
        with self.assertRaisesRegex(AssertionError,'property limits'):self.validate()

    def test_actual_alignment_table_digits_and_roles_checked(self):
        placement=self.node('B018-K3').findall('.//'+XH+'table')[0]
        rows=placement.findall(XH+'tbody/'+XH+'tr')
        rows[0][1].text='8';rows[0][2].text='3'
        with self.assertRaisesRegex(AssertionError,'place-alignment'):self.validate()

    def test_actual_carry_table_written_digit_and_destination_checked(self):
        for row_index,column,before,after in [(0,2,'5','6'),(0,3,'1 పది','1 వంద'),
                                               (1,1,'3+2+1=6','3+2=5')]:
            with self.subTest(row=row_index,column=column):
                self.bridge=copy.deepcopy(self.bridge_base)
                row=self.node('B018-K3').findall('.//'+XH+'table')[1].findall(XH+'tbody/'+XH+'tr')[row_index]
                row[column].text=row[column].text.replace(before,after)
                with self.assertRaises(AssertionError):self.validate()

    def test_exact10_boundary_cannot_change_to_more_than10(self):
        self.mutate('B018-K3','“9 కంటే ఎక్కువ” అనే మాటను “10 కంటే ఎక్కువ”గా మార్చకండి',
                    '“9 కంటే ఎక్కువ” అనే మాటను “10 కంటే ఎక్కువ”గా మార్చండి')
        with self.assertRaisesRegex(AssertionError,'exact10'):self.validate()

    def test_carry_three_cannot_be_reduced_to_carry_one(self):
        self.mutate('B018-K4','0 ఒకట్లు రాసి 3 పదులు','0 ఒకట్లు రాసి 1 పది')
        with self.assertRaisesRegex(AssertionError,'greater than1'):self.validate()

    def test_same65_reversed_requested_order_is_not_the_actual_worked_example(self):
        self.mutate('B018-K3','38+27=65','27+38=65')
        self.assertEqual(equality('27+38=65'),((27,38),(65,)))
        with self.assertRaisesRegex(AssertionError,'aligned algorithm'):self.validate()

    def test_all_three_selfchecks_have_complete_reasoning_not_only_numbers(self):
        for ident,before in [('B018-S01','మూల పట్టికలో పేరే ఉంది'),
                             ('B018-S02','అంకెలను మార్చడానికి అనుమతి కాదు'),
                             ('B018-S03','30ఒకట్లు వస్తే3పదులు')]:
            with self.subTest(detail=ident):
                self.bridge=copy.deepcopy(self.bridge_base);self.mutate(ident,before,'')
                with self.assertRaisesRegex(AssertionError,'complete self-check answer'):self.validate()

    def test_each_crossunit_or_local_route_is_exact(self):
        links=list(self.bridge.iter(XH+'a'))
        for index in range(len(links)):
            with self.subTest(index=index):
                root=copy.deepcopy(self.bridge);actual=list(root.iter(XH+'a'))
                actual[index].set('href',actual[(index+1)%len(actual)].get('href'))
                with self.assertRaisesRegex(AssertionError,'earlier-unit/selfcheck routes'):validate_recap_bridge(root)

    def test_extra_true_equation_cannot_expand_reviewed_scope(self):
        self.node('B018-K4').append(ET.fromstring('<p xmlns="http://www.w3.org/1999/xhtml">1+2=3</p>'))
        with self.assertRaisesRegex(AssertionError,'numeric equalities'):self.validate()

    def test_recap_cannot_claim_module_or_assignment_completion(self):
        self.mutate('B018-boundary','అభ్యాస ప్రశ్నల విభాగం ఇంకా ఉంది','అభ్యాస ప్రశ్నల విభాగం పూర్తయింది')
        with self.assertRaisesRegex(AssertionError,'continuation boundary'):self.validate()

        self.bridge=copy.deepcopy(self.bridge_base)
        self.mutate('B018-disclosure','ముగిసిందని అనుకోకండి','ముగిసిందని అనుకోండి')
        with self.assertRaisesRegex(AssertionError,'assignment-completion boundary'):self.validate()

    def test_duplicate_id_rejected(self):
        self.node('B018-S03').set('id','B018-S02')
        with self.assertRaisesRegex(AssertionError,'duplicate'):self.validate()

    def test_bridge_validation_is_read_only(self):
        before=ET.tostring(self.bridge);self.validate();self.assertEqual(ET.tostring(self.bridge),before)


if __name__ == '__main__':
    unittest.main()
