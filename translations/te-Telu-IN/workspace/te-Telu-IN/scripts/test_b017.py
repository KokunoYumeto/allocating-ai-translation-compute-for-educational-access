"""B017 actual-content tests; all corruptions are in-memory and read-only."""
import copy
from collections import Counter
from html.parser import HTMLParser
import unittest
import xml.etree.ElementTree as ET

from application_addition_checks import (BASE,CN,MATH,XH,SVG,NUMERIC_CASES,PERIMETER_IDS,DIAGRAMS,
    TABLES,URLS,RELATION,addends,checked_relation,column_steps,displayed_relations,equality,hao_frame,ids_of,
    protected_math_signature,source_cases,svg_geometry,text_of,validate_application_bridge,
    validate_application_target,validate_b017,validate_diagram_assets)
from inspect_source import slots


class SourceArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,_=source_cases()

    def test_actual_source_inventory_and_units(self):
        source,cases=source_cases()
        self.assertEqual(len(list(source.iter())),210)
        self.assertEqual(len(list(slots(source))),114)
        self.assertEqual(len(ids_of(source)),46)
        self.assertEqual(len(list(source.iter(MATH+'math'))),16)
        self.assertEqual(len(list(source.iter(CN+'image'))),3)
        self.assertEqual([c[3] for c in cases],[432,140,720])
        self.assertEqual([c[4] for c in cases],['points','miles','students'])

    def test_every_numerical_case_recomputed_from_actual_operands(self):
        ids=ids_of(self.source)
        for ident,_,numbers,total,_ in NUMERIC_CASES:
            with self.subTest(exercise=ident):
                actual=tuple(int(n.text) for n in ids[ident].find(CN+'problem').iter(MATH+'mn'))
                self.assertEqual(actual,numbers);self.assertEqual(sum(actual),total)
                self.assertEqual(sum(row[0]*row[4] for row in column_steps(actual)),total)

    def test_hao_carry_three_is_thirty_not_three(self):
        steps=column_steps((87,93,68,95,89))
        self.assertEqual([r[3] for r in steps],[32,43,4])
        self.assertEqual([r[4] for r in steps],[2,3,4])
        self.assertEqual([r[5] for r in steps],[3,4,0])
        self.assertEqual(steps[1][2]*steps[1][0],30)
        self.assertEqual(steps[2][2]*steps[2][0],400)

    def test_zero_digits_in_mark_and_lincoln_answers(self):
        mark=column_steps((18,15,26,49,32))
        school=column_steps((230,165,325))
        self.assertEqual([r[4] for r in mark],[0,4,1])
        self.assertEqual([r[4] for r in school],[0,2,7])
        self.assertEqual([r[3] for r in school],[10,12,7])

    def test_integer_column_algorithm_all_zero_and_large_carries(self):
        self.assertEqual(column_steps((0,0)),((1,(0,0),0,0,0,0),))
        self.assertEqual([r[4] for r in column_steps((99,99,99,99,99))],[5,9,4])
        for nums in [(999,1),(100,20,3),(18,29,37,46),(29,38,47,56)]:
            with self.subTest(nums=nums):
                self.assertEqual(sum(r[0]*r[4] for r in column_steps(nums)),sum(nums))
        for bad in [(True,2),(-1,3),(1.5,2),(1,)]:
            with self.subTest(bad=bad),self.assertRaises(AssertionError):column_steps(bad)

    def test_actual_hao_layout_not_flattened_to837(self):
        table=ids_of(self.source)['eip-id1168288617772']
        self.assertEqual(hao_frame(table),((87,93,68,95,89),3,432))
        self.assertEqual(len(list(table.iter(MATH+'mtr'))),9)

    def test_actual_carry_mark_corruption_rejected(self):
        table=copy.deepcopy(ids_of(self.source)['eip-id1168288617772'])
        table.find('.//'+MATH+'mover')[1].text='2'
        with self.assertRaisesRegex(AssertionError,'raised carry/result'):hao_frame(table)

    def test_actual_carry_above_wrong_digit_rejected(self):
        table=copy.deepcopy(ids_of(self.source)['eip-id1168288617772'])
        first=table.find('.//'+MATH+'mover');first[0].text='7'
        table.find('.//'+MATH+'mtd').find(MATH+'mn').text='8'
        with self.assertRaises(AssertionError):hao_frame(table)

    def test_source_blank_layout_row_preservation(self):
        table=copy.deepcopy(ids_of(self.source)['eip-id1168288617772'])
        ET.SubElement(table.find('.//'+MATH+'mtr'),MATH+'mtd')
        with self.assertRaisesRegex(AssertionError,'blank layout rows'):hao_frame(table)

    def test_narrow_math_and_translation_only(self):
        target=copy.deepcopy(self.source)
        for n in target.iter(MATH+'mtext'):
            if n.text=='and':n.text='మరియు'
        self.assertEqual(protected_math_signature(self.source),protected_math_signature(target,target=True))
        original=copy.deepcopy(target)
        for bad in ['లేదా','మరియూ','and ']:
            with self.subTest(bad=bad):
                target=copy.deepcopy(original);next(n for n in target.iter(MATH+'mtext') if n.text=='మరియు').text=bad
                self.assertNotEqual(protected_math_signature(self.source),protected_math_signature(target,target=True))

    def test_math_underline_and_base10_not_generalized_as_and(self):
        for before in ['____','base-10']:
            with self.subTest(token=before):
                target=copy.deepcopy(self.source)
                next(n for n in target.iter(MATH+'mtext') if n.text==before).text='మరియు'
                self.assertNotEqual(protected_math_signature(self.source),protected_math_signature(target,target=True))

    def test_variable_arity_addition_and_wrong_result_rejected(self):
        self.assertEqual(addends('87+93+68+95+89'),(87,93,68,95,89))
        self.assertEqual(equality('87+93+68+95+89=432'),((87,93,68,95,89),432))
        for bad in ['87+93+68+95+89=433','87+93=180=181','87+93=0180','87-93=180']:
            with self.subTest(bad=bad),self.assertRaises(AssertionError):equality(bad)

    def test_actual_two_tables_and_three_external_links(self):
        ids=ids_of(self.source)
        for ident,(declared,count,width) in TABLES.items():
            self.assertEqual(ids[ident].find(CN+'tgroup').get('cols'),str(declared))
            self.assertEqual([len(r) for r in ids[ident].iter(CN+'row')],[width]*count)
        self.assertEqual(tuple(n.get('url') for n in self.source.iter(CN+'link')),URLS)

    def test_actual_three_localized_diagram_geometries(self):
        actual=validate_diagram_assets()
        self.assertEqual(actual,(
            {'vertices':6,'perimeter':26,'unit':'feet'},
            {'vertices':8,'perimeter':30,'unit':'inches'},
            {'vertices':8,'perimeter':36,'unit':'inches'}))

    def test_each_svg_edge_label_corruption_is_rejected(self):
        for _,(filename,lengths,total,unit) in DIAGRAMS.items():
            for index in range(len(lengths)):
                with self.subTest(file=filename,edge=index+1):
                    svg=ET.parse(BASE/'assets/B017'/filename).getroot()
                    labels=[n for n in svg.iter(SVG+'text') if n.get('data-role')=='side-label']
                    labels[index].set('data-length',str(lengths[index]+1))
                    with self.assertRaisesRegex(AssertionError,'displayed edge labels'):svg_geometry(svg,lengths,total,unit)

    def test_svg_true_perimeter_but_wrong_edge_geometry_rejected(self):
        filename,lengths,total,unit=DIAGRAMS['fs-id2175999']
        svg=ET.parse(BASE/'assets/B017'/filename).getroot()
        boundary=next(n for n in svg.iter(SVG+'polygon') if n.get('data-role')=='boundary')
        points=boundary.get('points').split();points[1]='560,80';points[2]='560,320'
        boundary.set('points',' '.join(points))
        self.assertEqual(sum(lengths),total)
        with self.assertRaisesRegex(AssertionError,'edge geometry/length'):svg_geometry(svg,lengths,total,unit)

    def test_svg_cannot_display_answer_or_wrong_unit_note(self):
        for media,(filename,lengths,total,unit) in DIAGRAMS.items():
            with self.subTest(media=media):
                svg=ET.parse(BASE/'assets/B017'/filename).getroot()
                note=next(n for n in svg.iter(SVG+'text') if n.get('data-role')=='unit-note')
                note.text=('అంగుళాలు (inches)' if unit=='feet' else 'అడుగులు (feet)')
                with self.assertRaisesRegex(AssertionError,'unit note'):svg_geometry(svg,lengths,total,unit)
                svg=ET.parse(BASE/'assets/B017'/filename).getroot()
                ET.SubElement(svg,SVG+'text').text=str(total)
                with self.assertRaisesRegex(AssertionError,'must not display problem answer'):svg_geometry(svg,lengths,total,unit)

    def test_indonesian_numeric_tokens_match_exact_english(self):
        reference=ET.parse(BASE.parent/'downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml').getroot()
        section=ids_of(reference)['fs-id2197427']
        self.assertEqual([n.text for n in self.source.iter(MATH+'mn')],[n.text for n in section.iter(MATH+'mn')])
        self.assertEqual([n.get('id') for n in self.source.iter() if n.get('id')],
                         [n.get('id') for n in section.iter() if n.get('id')])


class ActualBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,_=source_cases()
        cls.bridge_base=ET.parse(BASE/'translations/TE-B017.bridge.xhtml').getroot()

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
        self.fail('Mutation did not touch actual bridge: '+before)

    def validate(self,root=None):
        return validate_application_bridge(self.bridge if root is None else root,self.source)

    def test_actual_bridge_arithmetic_current_coverage(self):
        self.assertEqual(self.validate(),{'bridge_solution_details':12,'bridge_carry_tables':5,
            'bridge_carry_rows':15,'bridge_displayed_relations':79})
        self.assertEqual(len(ids_of(self.bridge)),30)
        self.assertEqual(len(list(self.bridge.iter(XH+'a'))),24)

    def test_supported_unit_exchange_relations(self):
        self.assertEqual(checked_relation('32 = 30 + 2'),'32=30+2')
        self.assertEqual(checked_relation('3 × 10 = 30'),'3×10=30')
        for bad in ['32=30+3','3×10=3','3×10=30=31','32=03+29']:
            with self.subTest(bad=bad),self.assertRaises(AssertionError):checked_relation(bad)

    def test_all_twelve_actual_answer_sentences_mutated(self):
        import re
        for detail in self.bridge.iter(XH+'details'):
            ident=detail.get('id')
            with self.subTest(detail=ident):
                root=copy.deepcopy(self.bridge)
                answer=list(self.node(ident,root).iter(XH+'strong'))[-1]
                match=re.search(r'\d+',answer.text);self.assertIsNotNone(match)
                answer.text=answer.text[:match.start()]+str(int(match.group())+1)+answer.text[match.end():]
                with self.assertRaisesRegex(AssertionError,'answer sentence/value/unit'):self.validate(root)

    def test_same_answer_different_expression_source_quantities_rejected(self):
        node=list(self.node('B017-W-fs-id1899571').iter(XH+'strong'))[0]
        node.text='88+92+68+95+89'
        self.assertEqual(sum(addends(node.text)),432)
        with self.assertRaisesRegex(AssertionError,'requested quantities/order'):self.validate()

    def test_source_expression_cannot_gain_test_count_five(self):
        list(self.node('B017-W-fs-id1899571').iter(XH+'strong'))[0].text='87+93+68+95+89+5'
        with self.assertRaisesRegex(AssertionError,'requested quantities/order'):self.validate()

    def test_school_expression_cannot_gain_grade_count_three(self):
        list(self.node('B017-S-fs-id1761942').iter(XH+'strong'))[0].text='230+165+325+3'
        with self.assertRaisesRegex(AssertionError,'requested quantities/order'):self.validate()

    def test_same20_different_units_never_interchangeable(self):
        for ident,old,new in [('B017-S-D03','అంగుళాలు','అడుగులు'),('B017-S-R03','అడుగులు','అంగుళాలు')]:
            with self.subTest(detail=ident):
                root=copy.deepcopy(self.bridge);answer=list(self.node(ident,root).iter(XH+'strong'))[-1]
                answer.text=answer.text.replace(old,new)
                with self.assertRaisesRegex(AssertionError,'answer sentence/value/unit'):self.validate(root)

    def test_perimeter_cannot_use_square_units(self):
        for ident in ['B017-W-fs-id1628979','B017-S-fs-id2483376','B017-S-fs-id2427950']:
            with self.subTest(detail=ident):
                root=copy.deepcopy(self.bridge);answer=list(self.node(ident,root).iter(XH+'strong'))[-1]
                answer.text=answer.text.replace('అడుగులు','చదరపు అడుగులు').replace('అంగుళాలు','చదరపు అంగుళాలు')
                with self.assertRaisesRegex(AssertionError,'answer sentence/value/unit'):self.validate(root)

    def test_mark_miles_not_metric_conversion(self):
        answer=list(self.node('B017-S-fs-id1564459').iter(XH+'strong'))[-1]
        answer.text=answer.text.replace('మైళ్లు','కిలోమీటర్లు')
        with self.assertRaisesRegex(AssertionError,'answer sentence/value/unit'):self.validate()

    def test_students_not_school_grade_count(self):
        answer=list(self.node('B017-S-fs-id1761942').iter(XH+'strong'))[-1]
        answer.text=answer.text.replace('మంది విద్యార్థులు','తరగతులు')
        with self.assertRaisesRegex(AssertionError,'answer sentence/value/unit'):self.validate()

    def test_each_of_79_actual_relations_rejects_a_changed_number(self):
        import re
        blocks=[]
        for node in self.bridge.iter():
            if node.tag.rsplit('}',1)[-1] not in {'p','li','td','dd'}:continue
            if any(n is not node and n.tag.rsplit('}',1)[-1] in {'p','li','td','dd'} for n in node.iter()):continue
            blocks.extend((node,m.group()) for m in RELATION.finditer(text_of(node)))
        self.assertEqual(len(blocks),79)
        indices={id(n):i for i,n in enumerate(self.bridge.iter())}
        for i,(node,formula) in enumerate(blocks):
            with self.subTest(occurrence=i,formula=formula):
                root=copy.deepcopy(self.bridge);block=list(root.iter())[indices[id(node)]]
                tokens=list(re.finditer(r'\d+',formula));last=tokens[-1]
                changed=formula[:last.start()]+str(int(last.group())+1)+formula[last.end():]
                did_change=False
                for inline in block.iter():
                    for field in ('text','tail'):
                        value=getattr(inline,field)
                        if value and formula in value:
                            setattr(inline,field,value.replace(formula,changed,1));did_change=True;break
                    if did_change:break
                self.assertTrue(did_change)
                with self.assertRaises(AssertionError):self.validate(root)

    def test_all_fifteen_actual_written_digits_mutated(self):
        rows=[r for d in self.bridge.iter(XH+'details') for r in d.findall('.//'+XH+'tbody/'+XH+'tr')]
        self.assertEqual(len(rows),15)
        for index in range(15):
            with self.subTest(row=index):
                root=copy.deepcopy(self.bridge)
                row=[r for d in root.iter(XH+'details') for r in d.findall('.//'+XH+'tbody/'+XH+'tr')][index]
                row[2].text=str((int(row[2].text)+1)%10)
                with self.assertRaisesRegex(AssertionError,'written digit'):self.validate(root)

    def test_all_fifteen_actual_carry_counts_mutated(self):
        for index in range(15):
            with self.subTest(row=index):
                root=copy.deepcopy(self.bridge)
                row=[r for d in root.iter(XH+'details') for r in d.findall('.//'+XH+'tbody/'+XH+'tr')][index]
                row[3].text=str(int(row[3].text[0])+1)+row[3].text[1:]
                with self.assertRaisesRegex(AssertionError,'carry count/destination'):self.validate(root)

    def test_same_zero_written_wrong_target_place_rejected(self):
        row=self.node('B017-S-D02').findall('.//'+XH+'tbody/'+XH+'tr')[0]
        self.assertEqual(row[2].text,'0');row[0].text='పదులు'
        with self.assertRaisesRegex(AssertionError,'target place'):self.validate()

    def test_carry_three_cannot_mean_three_hundreds(self):
        row=self.node('B017-W-fs-id1899571').findall('.//'+XH+'tbody/'+XH+'tr')[0]
        row[3].text='3 వందలు'
        with self.assertRaisesRegex(AssertionError,'carry count/destination'):self.validate()

    def test_true_column_equality_with_wrong_incoming_carry_rejected(self):
        row=self.node('B017-W-fs-id1899571').findall('.//'+XH+'tbody/'+XH+'tr')[1]
        row[1].text='8+9+6+9+9+2=43'
        self.assertEqual(equality(row[1].text)[1],43)
        with self.assertRaisesRegex(AssertionError,'column digits/incoming'):self.validate()

    def test_missing_final_carry_row_rejected(self):
        body=self.node('B017-W-fs-id1899571').find('.//'+XH+'tbody');body.remove(body[-1])
        with self.assertRaisesRegex(AssertionError,'complete place coverage'):self.validate()

    def test_carry_table_output_roles_cannot_swap(self):
        row=self.node('B017-W-fs-id1899571').find('.//'+XH+'thead/'+XH+'tr')
        row[2].text,row[3].text=row[3].text,row[2].text
        with self.assertRaisesRegex(AssertionError,'column roles'):self.validate()

    def test_raised_carry_cannot_be_called_fraction(self):
        self.mutate('B017-W-fs-id1899571','అది భిన్నం కాదు','అది భిన్నం')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_adding_carry_again_to_total_is_rejected(self):
        self.mutate('B017-K2','అసలు మొత్తానికి మరోసారి అదనంగా కలపకండి','అసలు మొత్తానికి మరోసారి అదనంగా కలపండి')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_omitted_weekdays_are_not_assumed_zero(self):
        self.mutate('B017-S-fs-id1564459','తప్పనిసరిగా 0 అని ఊహించి చేర్చడం లేదు','తప్పనిసరిగా 0 అని ఊహించి చేర్చాలి')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_same_total_with_wrong_weekday_association_rejected(self):
        self.mutate('B017-S-fs-id1564459','సోమవారం 18, బుధవారం 15','సోమవారం 15, బుధవారం 18')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_perimeter_is_not_number_of_sides(self):
        self.mutate('B017-K3','భుజాల సంఖ్యను లెక్కించడం, వాటి పొడవులను కలపడం వేరు','భుజాల సంఖ్యను లెక్కించడం, వాటి పొడవులను కలపడం ఒకటే')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_repeated_equal_edge_cannot_be_discarded(self):
        self.mutate('B017-W-fs-id1628979','ఒకదాన్ని తీసివేయకూడదు','ఒకదాన్ని తీసివేయాలి')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_one_edge_cannot_be_omitted_even_with_fabricated_total(self):
        strong=list(self.node('B017-S-fs-id2483376').iter(XH+'strong'))[0]
        strong.text='4+9+4+3+2+3+2'
        with self.assertRaisesRegex(AssertionError,'requested quantities/order'):self.validate()

    def test_wrong_same_sum_edge_sequence_rejected(self):
        strong=list(self.node('B017-S-fs-id2483376').iter(XH+'strong'))[0]
        strong.text='5+8+4+3+2+3+2+3'
        self.assertEqual(sum(addends(strong.text)),30)
        with self.assertRaisesRegex(AssertionError,'requested quantities/order'):self.validate()

    def test_true_extra_equation_cannot_expand_reviewed_scope(self):
        self.node('B017-K1').append(ET.fromstring('<p xmlns="http://www.w3.org/1999/xhtml">1+2=3</p>'))
        with self.assertRaisesRegex(AssertionError,'all displayed relations'):self.validate()

    def test_correct_checking_equation_in_wrong_case_rejected(self):
        self.mutate('B017-S-D01','12+18=30','16+14=30')
        with self.assertRaisesRegex(AssertionError,'case-specific checking'):self.validate()

    def test_each_source_backlink_must_name_its_own_exercise(self):
        for ident in ['B017-W-fs-id1899571','B017-W-fs-id1628979','B017-S-fs-id1564459',
                      'B017-S-fs-id1761942','B017-S-fs-id2483376','B017-S-fs-id2427950']:
            with self.subTest(detail=ident):
                root=copy.deepcopy(self.bridge);next(self.node(ident,root).iter(XH+'a')).set('href','#fs-id2594070')
                with self.assertRaisesRegex(AssertionError,'exact source backlink'):self.validate(root)

    def test_same20_wrong_recheck_route_rejected(self):
        row=self.node('B017-route').findall('.//'+XH+'tbody/'+XH+'tr')[2]
        list(row.iter(XH+'a'))[-1].set('href','#B017-R01')
        with self.assertRaisesRegex(AssertionError,'skill/source/recheck mapping'):self.validate()

    def test_duplicate_or_missing_solution_id_rejected(self):
        self.node('B017-S-R03').set('id','B017-S-D03')
        with self.assertRaisesRegex(AssertionError,'Duplicate'):self.validate()

    def test_same20_prompt_units_cannot_be_copied(self):
        self.mutate('B017-R03','7, 3, 7, 3 అడుగులు','7, 3, 7, 3 అంగుళాలు')
        with self.assertRaisesRegex(AssertionError,'practice question/units'):self.validate()

    def test_same20_distances_not_claimed_equal(self):
        self.mutate('B017-S-R03','సమాన దూరాలని అనుకోకండి','సమాన దూరాలని అనుకోండి')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_resource_live_availability_not_claimed(self):
        self.mutate('B017-resource-boundary','ప్రస్తుత అందుబాటు, భాష లేదా కార్యాచరణను ధృవీకరించడం లేదు','ప్రస్తుత అందుబాటు, భాష లేదా కార్యాచరణను ధృవీకరించాం')
        with self.assertRaisesRegex(AssertionError,'context/unit/carry/boundary'):self.validate()

    def test_validator_does_not_change_actual_bridge_tree(self):
        before=ET.tostring(self.bridge);self.validate();self.assertEqual(ET.tostring(self.bridge),before)


class _TargetFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Missing assets or an unimplemented exact MathML exception is a real
        # setup failure, not permission to invent a target or skip final checks.
        from build_unit import unit_inputs,asset_map,localize
        cls.source_base,cls.meta,cls.catalog=unit_inputs('TE-B017')
        cls.assets=asset_map('TE-B017')
        cls.target_base=localize(cls.source_base,cls.catalog,cls.assets)

    def setUp(self):
        self.source=copy.deepcopy(self.source_base)
        self.target=copy.deepcopy(self.target_base)

    def node(self,ident,root=None):
        return ids_of(self.target if root is None else root)[ident]

    def mutate(self,ident,before,after,root=None):
        for node in self.node(ident,root).iter():
            for field in ('text','tail'):
                value=getattr(node,field)
                if value and before in value:
                    setattr(node,field,value.replace(before,after,1));return
        self.fail('Did not mutate actual target text: '+before)

    def validate(self):
        return validate_application_target(self.target)


class ActualTargetTests(_TargetFixture):
    def test_actual_target_content_all_source_cases_and_math(self):
        self.assertEqual(self.validate(),NUMERIC_CASES)
        self.assertEqual(len(ids_of(self.target)),46)
        self.assertEqual(len(list(self.target.iter(MATH+'math'))),16)
        self.assertEqual(protected_math_signature(self.source),protected_math_signature(self.target,True))

    def test_actual_combined_validator_complete_coverage(self):
        bridge=ET.parse(BASE/'translations/TE-B017.bridge.xhtml').getroot()
        self.assertEqual(validate_b017(self.target,bridge),{
            'source_exercises':6,'source_numeric_applications':3,'source_perimeter_applications':3,
            'localized_diagrams':3,'bridge_solution_details':12,'bridge_carry_tables':5,
            'bridge_carry_rows':15,'bridge_displayed_relations':79})

    def test_every_numeric_source_problem_rejects_changed_operand(self):
        for ident,_,_,_,_ in NUMERIC_CASES:
            with self.subTest(exercise=ident):
                self.target=copy.deepcopy(self.target_base)
                number=next(self.node(ident).find(CN+'problem').iter(MATH+'mn'))
                number.text=str(int(number.text)+1)
                with self.assertRaisesRegex(AssertionError,'protected MathML'):self.validate()

    def test_same432_with_different_question_values_is_rejected(self):
        values=list(self.node('fs-id1746953').iter(MATH+'mn'))
        values[0].text='88';values[1].text='92'
        self.assertEqual(sum(int(n.text) for n in values),432)
        with self.assertRaisesRegex(AssertionError,'protected MathML'):self.validate()

    def test_each_plaintext_try_answer_is_checked_not_only_mathml(self):
        for ident,before,after in [('fs-id1390222','140','14'),('fs-id1931675','720','72'),
                                  ('fs-id1357069','30','31'),('fs-id1613173','36','37')]:
            with self.subTest(answer=ident):
                self.target=copy.deepcopy(self.target_base);self.mutate(ident,before,after)
                with self.assertRaisesRegex(AssertionError,'answer/unit'):self.validate()

    def test_same_mark_total_with_wrong_weekday_is_rejected(self):
        self.mutate('fs-id1919047','సోమవారం','మంగళవారం')
        with self.assertRaisesRegex(AssertionError,'day/distance'):self.validate()

    def test_mark_miles_and_school_students_cannot_be_recast(self):
        for ident,before,after in [('fs-id1390222','మైళ్లు','కిలోమీటర్లు'),
                                  ('fs-id1931675','మంది విద్యార్థులు','తరగతులు')]:
            with self.subTest(answer=ident):
                self.target=copy.deepcopy(self.target_base);self.mutate(ident,before,after)
                with self.assertRaisesRegex(AssertionError,'answer/unit'):self.validate()

    def test_hao_points_cannot_be_average_or_percent(self):
        self.mutate('fs-id1746953','మొత్తం పాయింట్లు','సగటు పాయింట్లు')
        with self.assertRaisesRegex(AssertionError,'Hao quantity/context'):self.validate()

    def test_incidental_grade_count_and_test_count_preserved(self):
        for ident,before,after in [('fs-id2295551','మూడు తరగతి స్థాయులు','నాలుగు తరగతి స్థాయులు'),
                                  ('fs-id1746953','ఐదు పరీక్షల్లో','ఆరు పరీక్షల్లో')]:
            with self.subTest(question=ident):
                self.target=copy.deepcopy(self.target_base);self.mutate(ident,before,after)
                with self.assertRaises(AssertionError):self.validate()

    def test_hao_actual_raised_carry_is_three_not_one(self):
        self.node('eip-id1168288617772').find('.//'+MATH+'mover')[1].text='1'
        with self.assertRaisesRegex(AssertionError,'protected MathML'):self.validate()

    def test_raised_carry_is_not_a_fraction_structure(self):
        self.node('eip-id1168288617772').find('.//'+MATH+'mover').tag=MATH+'mfrac'
        with self.assertRaisesRegex(AssertionError,'structure/attributes'):self.validate()

    def test_interior_math_tail_cannot_gain_unchecked_digits(self):
        next(self.target.iter(MATH+'mn')).tail='0'
        with self.assertRaisesRegex(AssertionError,'protected MathML'):self.validate()

    def test_only_exact_two_math_conjunctions_are_localized(self):
        self.assertEqual([n.text for n in self.target.iter(MATH+'mtext')],['మరియు','____','మరియు','base-10','base-10'])
        for value in ('and','లేదా','మరియూ'):
            with self.subTest(value=value):
                self.target=copy.deepcopy(self.target_base)
                next(self.target.iter(MATH+'mtext')).text=value
                with self.assertRaises(AssertionError):self.validate()

    def test_source_underline_and_base10_cannot_be_translated(self):
        for value in ('____','base-10'):
            with self.subTest(value=value):
                self.target=copy.deepcopy(self.target_base)
                next(n for n in self.target.iter(MATH+'mtext') if n.text==value).text='మరియు'
                with self.assertRaisesRegex(AssertionError,'protected MathML'):self.validate()

    def test_all_six_original_solution_ids_remain_unchanged(self):
        original=[n.get('id') for n in self.source.iter(CN+'solution')]
        self.assertEqual(original,[n.get('id') for n in self.target.iter(CN+'solution')])
        for ident in original:
            with self.subTest(solution=ident):
                self.target=copy.deepcopy(self.target_base);self.node(ident).set('id','wrong-answer-id')
                with self.assertRaisesRegex(AssertionError,'structure/attributes'):self.validate()

    def test_both_frozen_three_column_declarations_cannot_be_rewritten(self):
        for ident in TABLES:
            with self.subTest(table=ident):
                self.target=copy.deepcopy(self.target_base);self.node(ident).find(CN+'tgroup').set('cols','2')
                with self.assertRaisesRegex(AssertionError,'structure/attributes'):self.validate()

    def test_both_accessible_table_shapes_describe_two_actual_columns(self):
        for ident in TABLES:
            with self.subTest(table=ident):
                self.target=copy.deepcopy(self.target_base)
                table=self.node(ident);table.set('summary',table.get('summary').replace('రెండు నిలువు వరుసల','మూడు నిలువు వరుసల'))
                with self.assertRaisesRegex(AssertionError,'accessible table meaning'):self.validate()

    def test_summary_same_answer_different_hao_quantities_rejected(self):
        table=self.node('eip-id1168288617772');before=table.get('summary')
        self.assertIn('87+93',before);table.set('summary',before.replace('87+93','88+92'))
        with self.assertRaisesRegex(AssertionError,'summary quantities'):self.validate()

    def test_summary_same26_different_patio_edges_rejected(self):
        table=self.node('eip-id1168289453960');before=table.get('summary')
        self.assertIn('4+6+2+3+2+9',before);table.set('summary',before.replace('4+6+2+3+2+9','5+5+2+3+2+9'))
        with self.assertRaisesRegex(AssertionError,'summary quantities'):self.validate()

    def test_perimeter_definition_must_use_boundary_length(self):
        self.mutate('fs-id2594070','సరిహద్దు వెంబడి ఉన్న మొత్తం దూరాన్ని','లోపలి వైశాల్యాన్ని')
        with self.assertRaisesRegex(AssertionError,'perimeter is boundary length'):self.validate()

    def test_perimeter_sum_of_lengths_not_number_of_sides(self):
        self.mutate('eip-id1168289453960','భుజాల పొడవుల మొత్తం','భుజాల సంఖ్య')
        with self.assertRaisesRegex(AssertionError,'sum lengths'):self.validate()

    def test_patio_actual_feet_unit_cannot_be_square_feet(self):
        self.mutate('eip-id1168289453960','అడుగుల్లో ఉన్న పొడవులను','చదరపు అడుగుల్లో ఉన్న పొడవులను')
        with self.assertRaisesRegex(AssertionError,'patio dimensional sum/unit'):self.validate()

    def test_both_source_tryit_inches_questions_keep_units(self):
        for ident in ('fs-id1365334','fs-id1884028'):
            with self.subTest(question=ident):
                self.target=copy.deepcopy(self.target_base);self.mutate(ident,'అంగుళాల్లో','అడుగుల్లో')
                with self.assertRaisesRegex(AssertionError,'requested perimeter units'):self.validate()

    def test_answer_stage_cannot_be_removed_from_application_plan(self):
        self.mutate('fs-id2926269','జవాబును ఒక వాక్యంగా రాయాలి','సంఖ్యను మాత్రమే రాయాలి')
        with self.assertRaisesRegex(AssertionError,'requested application stages'):self.validate()

    def test_each_resource_url_and_label_association_checked(self):
        for index in range(3):
            with self.subTest(link=index):
                self.target=copy.deepcopy(self.target_base)
                list(self.target.iter(CN+'link'))[index].set('url',URLS[(index+1)%3])
                with self.assertRaisesRegex(AssertionError,'structure/attributes|resource href'):self.validate()
        self.target=copy.deepcopy(self.target_base)
        link=next(self.target.iter(CN+'link'));link.text=link.text.replace('రెండు','మూడు')
        with self.assertRaisesRegex(AssertionError,'resource label/source association'):self.validate()

    def test_actual_image_mapping_cannot_swap_two_valid_assets(self):
        images=list(self.target.iter(CN+'image'))
        images[0].set('src',images[1].get('src'))
        with self.assertRaisesRegex(AssertionError,'source/localized image mapping'):self.validate()

    def test_shared_localizer_rejects_and_translation_in_other_unit(self):
        from build_unit import localize
        catalog=copy.deepcopy(self.catalog);catalog['unit_id']='TE-B016'
        with self.assertRaises(AssertionError):localize(self.source,catalog,self.assets)

    def test_shared_localizer_rejects_and_in_wrong_math_tag(self):
        from build_unit import localize
        next(self.source.iter(MATH+'mtext')).tag=MATH+'mi'
        with self.assertRaises(AssertionError):localize(self.source,self.catalog,self.assets)

    def test_shared_localizer_rejects_and_outside_exact_registered_slots(self):
        from build_unit import localize
        catalog=copy.deepcopy(self.catalog)
        next(n for n in self.source.iter(MATH+'mtext') if n.text=='____').text='and'
        catalog['translations']['s040']='మరియు'
        with self.assertRaises(AssertionError):localize(self.source,catalog,self.assets)

    def test_shared_localizer_rejects_near_match_or_wrong_conjunction(self):
        from build_unit import localize
        for before,after in (('and ','మరియు'),('and','లేదా'),('AND','మరియు')):
            with self.subTest(before=before,after=after):
                source=copy.deepcopy(self.source);catalog=copy.deepcopy(self.catalog)
                next(source.iter(MATH+'mtext')).text=before;catalog['translations']['s013']=after
                with self.assertRaises(AssertionError):localize(source,catalog,self.assets)

    def test_target_validator_is_read_only(self):
        before=ET.tostring(self.target);self.validate();self.assertEqual(ET.tostring(self.target),before)


class _Rendered(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=Counter();self.tables={};self.labels={};self.images=[];self.links=[]
        self.table=None;self.cell=None;self.link=None

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id'):self.ids[attrs['id']]+=1
        if tag=='table':
            self.table=attrs['id'];self.tables[self.table]=[];self.labels[self.table]=attrs.get('aria-label')
        elif tag=='tr' and self.table:self.tables[self.table].append([])
        elif tag in {'td','th'} and self.table:
            self.cell=[tag,attrs.get('scope'),''];self.tables[self.table][-1].append(self.cell)
        elif tag=='a':
            self.link=[attrs.get('href'),''];self.links.append(self.link)
        elif tag=='img':self.images.append(attrs)

    def handle_data(self,data):
        if self.cell is not None:self.cell[2]+=data
        if self.link is not None:self.link[1]+=data

    def handle_endtag(self,tag):
        if tag in {'td','th'}:self.cell=None
        if tag=='table':self.table=None
        if tag=='a':self.link=None


class ActualRendererTests(_TargetFixture):
    def rendered(self,english=False):
        from build_unit import render
        parser=_Rendered()
        parser.feed(render(self.source if english else self.target,self.assets,'en-' if english else '',english))
        parser.close();return parser

    def test_exact_two_table_shapes_and_all_46_ids_both_languages(self):
        for english in (False,True):
            with self.subTest(english=english):
                p=self.rendered(english);prefix='en-' if english else ''
                self.assertEqual({i:[len(r) for r in rows] for i,rows in p.tables.items()},
                                 {prefix+i:[width]*height for i,(_,height,width) in TABLES.items()})
                self.assertEqual(set(p.ids),{prefix+i for i in ids_of(self.source)})
                self.assertTrue(all(n==1 for n in p.ids.values()))

    def test_rendered_table_summaries_empty_cells_and_hao_carry_preserved(self):
        from build_unit import render
        for english in (False,True):
            with self.subTest(english=english):
                root=self.source if english else self.target;p=self.rendered(english);prefix='en-' if english else ''
                for ident in TABLES:self.assertEqual(p.labels[prefix+ident],self.node(ident,root).get('summary'))
                self.assertEqual(p.tables[prefix+'eip-id1168288617772'][2][1][2],'')
                for row in (0,4):self.assertEqual(p.tables[prefix+'eip-id1168289453960'][row][1][2],'')
                fragment=render(self.node('eip-id1168288617772',root),self.assets,prefix,english)
                rendered=ET.fromstring('<div>'+fragment+'</div>')
                self.assertEqual(hao_frame(rendered),((87,93,68,95,89),3,432))

    def test_all_three_media_keep_actual_original_or_localized_paths_and_alts(self):
        for english in (False,True):
            with self.subTest(english=english):
                root=self.source if english else self.target;p=self.rendered(english);prefix='en-' if english else ''
                self.assertEqual(len(p.images),3)
                for node,image in zip(root.iter(CN+'media'),p.images):
                    source=node.find(CN+'image').get('src')
                    expected=self.assets[source]['original_path'] if english else source
                    self.assertEqual(image['src'],'../'+expected)
                    self.assertEqual(image['alt'],node.get('alt'))
                    self.assertEqual(p.ids[prefix+node.get('id')],1)

    def test_all_three_exact_url_labels_and_hrefs_preserved(self):
        for english in (False,True):
            with self.subTest(english=english):
                root=self.source if english else self.target;p=self.rendered(english)
                expected=[(n.get('url'),text_of(n)) for n in root.iter(CN+'link')]
                actual=[(href,' '.join(label.split())) for href,label in p.links]
                self.assertEqual(actual,expected)
                self.assertEqual(tuple(href for href,_ in actual),URLS)

    def test_two_inline_base10_labels_keep_exact_protected_math(self):
        from build_unit import render
        for english in (False,True):
            root=self.source if english else self.target
            for index,link in enumerate(list(root.iter(CN+'link'))[:2]):
                with self.subTest(english=english,index=index):
                    before=ET.tostring(link);a=ET.fromstring(render(link,self.assets,'en-' if english else '',english))
                    self.assertEqual(a.get('href'),URLS[index]);self.assertEqual(text_of(a),text_of(link))
                    self.assertEqual(protected_math_signature(a),protected_math_signature(link))
                    self.assertEqual(ET.tostring(link),before)

    def test_unregistered_unsafe_or_http_source_urls_rejected(self):
        from build_unit import render
        for url in ('https://example.invalid/unregistered','javascript:alert(1)','data:text/html,unsafe',
                    'http://www.openstax.org/l/24add2blocks','https://www.openstax.org/l/24add2blocks?extra=1'):
            with self.subTest(url=url):
                link=copy.deepcopy(next(self.target.iter(CN+'link')));link.set('url',url)
                with self.assertRaises(AssertionError):render(link,self.assets)

    def test_inline_resource_math_cannot_gain_operator_or_changed_base(self):
        from build_unit import render
        for mutation in ('operator','text','attrs','extra-math'):
            with self.subTest(mutation=mutation):
                link=copy.deepcopy(next(self.target.iter(CN+'link')));math=next(link.iter(MATH+'math'))
                if mutation=='operator':ET.SubElement(math[0],MATH+'mo').text='+'
                elif mutation=='text':next(math.iter(MATH+'mtext')).text='base-100'
                elif mutation=='attrs':next(math.iter(MATH+'mtext')).set('onclick','bad')
                else:link.append(copy.deepcopy(math))
                with self.assertRaises(AssertionError):render(link,self.assets)

    def test_plain_third_resource_cannot_gain_math_child_or_conflicting_target(self):
        from build_unit import render
        link=copy.deepcopy(list(self.target.iter(CN+'link'))[-1])
        link.append(copy.deepcopy(next(self.target.iter(MATH+'math'))))
        with self.assertRaises(AssertionError):render(link,self.assets)
        link=copy.deepcopy(next(self.target.iter(CN+'link')));link.set('target-id','fs-id2594070')
        with self.assertRaises(AssertionError):render(link,self.assets)

    def test_registered_table_declaration_corruptions_rejected(self):
        from build_unit import render
        for ident in TABLES:
            with self.subTest(table=ident):
                table=copy.deepcopy(self.node(ident));table.find(CN+'tgroup').set('cols','4')
                with self.assertRaisesRegex(AssertionError,'Registered table source changed'):render(table,self.assets)

    def test_unregistered_three_to_two_defect_not_silently_accepted(self):
        from build_unit import render
        table=copy.deepcopy(self.node('eip-id1168288617772'));table.set('id','unregistered-table')
        with self.assertRaises(AssertionError):render(table,self.assets)

    def test_structural_wrapper_id_must_not_disappear(self):
        from build_unit import render
        table=copy.deepcopy(self.node('eip-id1168289453960'))
        table.find('.//'+CN+'entry').set('id','must-be-preserved')
        with self.assertRaisesRegex(AssertionError,'ID would be discarded'):render(table,self.assets)


if __name__=='__main__':
    unittest.main()
