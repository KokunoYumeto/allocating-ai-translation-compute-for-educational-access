"""Read-only B016 actual-source/target/bridge corruption and rendering tests."""
from collections import Counter
import copy
from hashlib import sha256
from html.parser import HTMLParser
import unittest
import xml.etree.ElementTree as ET

from phrase_addition_checks import (BASE, CN, MATH, XH, CASES, INTRO, INTRO_PAIRS,
    PRACTICE, TABLES, RELATION, answer_detail, compact, displayed_equalities,
    equality, expected_steps, expression_pair, ids_of, lines_of, math_signature,
    phrase_pair, source_cases, structure, text_of, validate_b016, validate_phrase_target)
from build_unit import asset_map, localize, unit_inputs
from inspect_source import slots


class ArithmeticTests(unittest.TestCase):
    def test_actual_source_inventory_and_derived_answers(self):
        root, actual = source_cases()
        self.assertEqual(len(list(root.iter())), 273)
        self.assertEqual(len(list(slots(root))), 148)
        self.assertEqual(len(ids_of(root)), 41)
        self.assertEqual(len(list(root.iter(MATH + 'math'))), 52)
        self.assertEqual([case[2] for case in actual], [42, 43, 42, 59, 105, 106])
        self.assertEqual([case[1] for case in actual], [c[4] for c in CASES])
        self.assertEqual(list(root.iter(CN + 'image')), [])
        self.assertEqual(asset_map('TE-B016'), {})

    def test_six_english_patterns_preserve_order(self):
        self.assertEqual(tuple(map(phrase_pair, INTRO)), INTRO_PAIRS)
        self.assertEqual(phrase_pair('8 more than 7'), (7, 8))
        self.assertEqual(phrase_pair('6 added to 4'), (4, 6))
        for phrase, pair in PRACTICE.values():
            with self.subTest(phrase=phrase):
                self.assertEqual(phrase_pair(phrase), pair)

    def test_comparison_is_not_an_addition_phrase(self):
        for text in ['8 is more than 7', '8 > 7', 'more than 7', '8 more than', 'the sum of 3 or 4',
                     'eight more than seven', '8 less than 7', '08 more than 7', '8 more than -7']:
            with self.subTest(text=text), self.assertRaises(AssertionError):
                phrase_pair(text)

    def test_expression_is_not_value_or_equation(self):
        self.assertEqual(expression_pair(' 37 + 69 '), (37, 69))
        for bad in ['106', '37+69=106', '37-69', '37+69+0', '37,69', '037+69', '37+69 trailing']:
            with self.subTest(bad=bad), self.assertRaises(AssertionError):
                expression_pair(bad)

    def test_equality_evaluates_complete_addends(self):
        self.assertEqual(equality('1+3+6=10'), ((1,3,6),10))
        for bad in ['1+3+6=9', '37+69=106=107', '37+69=106+0', '37+69=0106', '37-69=106']:
            with self.subTest(bad=bad), self.assertRaises(AssertionError):
                equality(bad)

    def test_same_value_does_not_imply_same_requested_expression(self):
        a = phrase_pair('the sum of 19 and 23')
        b = phrase_pair('the sum of 28 and 14')
        self.assertEqual(sum(a), sum(b)); self.assertNotEqual(a, b)

    def test_independent_column_totals_and_zero_boundaries(self):
        expected = {(19,23): (((9,3),12),((1,1,2),4),((19,23),42)),
                    (28,31): (((8,1),9),((2,3),5),((28,31),59)),
                    (29,76): (((9,6),15),((1,2,7),10),((29,76),105)),
                    (37,69): (((7,9),16),((1,3,6),10),((37,69),106)),
                    (15,8): (((5,8),13),((1,1),2),((15,8),23))}
        for pair, steps in expected.items():
            with self.subTest(pair=pair):
                self.assertEqual(expected_steps(pair), steps)

    def test_complete_indonesian_section_numeric_tokens_match(self):
        source, _ = source_cases()
        reference = ET.parse(BASE.parent / 'downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml').getroot()
        section = ids_of(reference)['fs-id2691382']
        self.assertEqual([n.text for n in source.iter(MATH + 'mn')], [n.text for n in section.iter(MATH + 'mn')])
        self.assertEqual(len(list(section.iter())), 273)


class _Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_base, cls.meta, cls.catalog = unit_inputs('TE-B016')
        cls.assets = asset_map('TE-B016')
        cls.target_base = localize(cls.source_base, cls.catalog, cls.assets)
        cls.bridge_base = ET.parse(BASE / 'translations/TE-B016.bridge.xhtml').getroot()

    def setUp(self):
        self.source = copy.deepcopy(self.source_base)
        self.target = copy.deepcopy(self.target_base)
        self.bridge = copy.deepcopy(self.bridge_base)

    def node(self, root, ident):
        return ids_of(root)[ident]

    def mutate(self, root, ident, old, new):
        for node in self.node(root, ident).iter():
            for field in ('text', 'tail'):
                value = getattr(node, field)
                if value and old in value:
                    setattr(node, field, value.replace(old, new, 1))
                    return
        self.fail('Fixture did not mutate actual text: ' + old)

    def strong(self, ident, index):
        return list(self.node(self.bridge, ident).iter(XH + 'strong'))[index]


class ActualTargetTests(_Fixture):
    def test_actual_localized_target_all_six_pairs(self):
        self.assertEqual(len(validate_phrase_target(self.target)), 6)
        self.assertEqual(structure(self.target), structure(self.source))
        self.assertEqual(math_signature(self.target), math_signature(self.source))
        self.assertEqual(len(self.catalog['translations']), 68)

    def test_all_six_actual_questions_reject_changed_operand(self):
        for ident, _, _, _, _ in CASES:
            with self.subTest(exercise=ident):
                target = copy.deepcopy(self.target)
                operand = self.node(target, ident).find(CN + 'problem').find('.//' + MATH + 'mn')
                operand.text = str(int(operand.text) + 1)
                with self.assertRaisesRegex(AssertionError, 'MathML'):
                    validate_phrase_target(target)

    def test_reversed_expression_same_sum_rejected(self):
        table = self.node(self.target, 'fs-id1826990')
        entry = table.findall('.//' + CN + 'row')[1][3]
        math = list(entry.iter(MATH + 'math'))[3]
        nums = list(math.iter(MATH + 'mn')); nums[0].text, nums[1].text = nums[1].text, nums[0].text
        self.assertEqual(sum(int(n.text) for n in nums), 15)
        with self.assertRaisesRegex(AssertionError, 'MathML'):
            validate_phrase_target(self.target)

    def test_added_to_role_reversal_with_unchanged_math_rejected(self):
        entry = self.node(self.target, 'fs-id1826990').findall('.//' + CN + 'row')[1][2]
        math = list(entry.iter(MATH + 'math'))[-2]
        math.tail = 'కు చేర్చవలసిన సంఖ్య '
        with self.assertRaisesRegex(AssertionError, 'Telugu phrase roles'):
            validate_phrase_target(self.target)

    def test_more_than_role_reversal_with_unchanged_math_rejected(self):
        self.mutate(self.target, 'fs-id1826990', 'ను కలపవలసిన ఆధార సంఖ్య ', 'కంటే ఎక్కువగా చేర్చే సంఖ్య ')
        with self.assertRaisesRegex(AssertionError, 'Telugu phrase roles'):
            validate_phrase_target(self.target)

    def test_plain_text_106_is_not_missed_by_mathml_checks(self):
        self.mutate(self.target, 'fs-id2451444', '106', '105')
        self.assertEqual(math_signature(self.target), math_signature(self.source))
        with self.assertRaisesRegex(AssertionError, 'expression/value answer'):
            validate_phrase_target(self.target)

    def test_plain_text_reversed_operands_with_same106_rejected(self):
        self.mutate(self.target, 'fs-id2451444', '37 + 69', '69 + 37')
        with self.assertRaisesRegex(AssertionError, 'expression/value answer'):
            validate_phrase_target(self.target)

    def test_plain_text_different_pair_same106_rejected(self):
        self.mutate(self.target, 'fs-id2451444', '37 + 69', '38 + 68')
        with self.assertRaisesRegex(AssertionError, 'expression/value answer'):
            validate_phrase_target(self.target)

    def test_plain_text_expression_cannot_be_replaced_by_value(self):
        self.mutate(self.target, 'fs-id2451444', '37 + 69', '106')
        with self.assertRaises(AssertionError):
            validate_phrase_target(self.target)

    def test_all_try_solution_stage_labels_cannot_be_swapped(self):
        for ident, sid, kind, _, _ in CASES:
            if kind != 'S':
                continue
            with self.subTest(exercise=ident):
                target = copy.deepcopy(self.target)
                self.mutate(target, sid, 'గణిత రాత:', 'విలువ:')
                with self.assertRaisesRegex(AssertionError, 'expression/value answer'):
                    validate_phrase_target(target)

    def test_each_question_requires_both_stages(self):
        for ident, _, _, _, _ in CASES:
            with self.subTest(exercise=ident):
                target = copy.deepcopy(self.target)
                self.mutate(target, ident, 'రాసి, దాని విలువ కనుగొనండి', 'రాయండి')
                with self.assertRaisesRegex(AssertionError, 'requested stages'):
                    validate_phrase_target(target)

    def test_protected_punctuation_and_leading_space_preserved(self):
        expected = ['42.', '31.', ' 59.']
        self.assertTrue(all(x in [n.text for n in self.target.iter(MATH + 'mn')] for x in expected))
        for original in expected:
            with self.subTest(token=original):
                target = copy.deepcopy(self.target)
                next(n for n in target.iter(MATH + 'mn') if n.text == original).text = original.strip().rstrip('.')
                with self.assertRaisesRegex(AssertionError, 'MathML'):
                    validate_phrase_target(target)

    def test_interior_math_tail_cannot_acquire_unchecked_digit(self):
        number = next(self.target.iter(MATH + 'mn'))
        number.tail = '0'
        with self.assertRaisesRegex(AssertionError, 'MathML'):
            validate_phrase_target(self.target)

    def test_sum_question_cannot_be_changed_to_difference(self):
        self.mutate(self.target, 'fs-id1392862', 'మొత్తాన్ని', 'తేడాను')
        with self.assertRaisesRegex(AssertionError, 'requested operation'):
            validate_phrase_target(self.target)

    def test_source_original_solution_ids_unchanged(self):
        for _, sid, _, _, _ in CASES:
            with self.subTest(solution=sid):
                target = copy.deepcopy(self.target); self.node(target, sid).set('id', 'changed-' + sid)
                with self.assertRaisesRegex(AssertionError, 'structure'):
                    validate_phrase_target(target)

    def test_all_three_declared_column_counts_remain_frozen(self):
        for ident, (declared, _, actual) in TABLES.items():
            with self.subTest(table=ident):
                target = copy.deepcopy(self.target)
                self.node(target, ident).find(CN + 'tgroup').set('cols', str(actual))
                with self.assertRaisesRegex(AssertionError, 'structure'):
                    validate_phrase_target(target)

    def test_summary_shapes_describe_actual_not_declared_columns(self):
        for ident in list(TABLES)[1:]:
            with self.subTest(table=ident):
                target = copy.deepcopy(self.target); table = self.node(target, ident)
                table.set('summary', table.get('summary').replace('రెండు నిలువు', 'మూడు నిలువు'))
                with self.assertRaisesRegex(AssertionError, 'summary shape'):
                    validate_phrase_target(target)

    def test_accessible_expression_order_cannot_reverse_same_sum(self):
        table = self.node(self.target, 'fs-id1826990')
        table.set('aria-label', table.get('aria-label').replace('7+8', '8+7'))
        with self.assertRaisesRegex(AssertionError, 'scope/direction'):
            validate_phrase_target(self.target)

    def test_summary_answer_and_pair_mapping_checked_outside_math(self):
        for ident, before, after in [('eip-id1168288294973', '19+23', '28+14'),
                                     ('eip-id1168288520954', 'కలిపితే 59', 'కలిపితే 58')]:
            with self.subTest(table=ident):
                target = copy.deepcopy(self.target); table = self.node(target, ident)
                table.set('summary', table.get('summary').replace(before, after))
                with self.assertRaisesRegex(AssertionError, 'summary numbers'):
                    validate_phrase_target(target)

    def test_english_of_and_cannot_be_declared_telugu_rule(self):
        self.mutate(self.target, 'fs-id2649934', 'మూల ఆంగ్ల పదబంధంలో', 'తెలుగు విభక్తి నియమంలో')
        with self.assertRaisesRegex(AssertionError, 'English grammar scope'):
            validate_phrase_target(self.target)

    def test_intro_six_lines_cannot_gain_computed_answers(self):
        table = self.node(self.target, 'fs-id1826990')
        math = table.findall('.//' + CN + 'row')[1][3].find(MATH + 'math')
        math.tail = '=3'
        with self.assertRaisesRegex(AssertionError, 'expression must contain'):
            validate_phrase_target(self.target)


class ActualBridgeTests(_Fixture):
    def test_actual_bridge_complete_coverage(self):
        result = validate_b016(self.target, self.bridge)
        self.assertEqual(result['source_expression_value_pairs'], 6)
        self.assertEqual(result['bridge_solution_details'], 12)
        self.assertEqual(result['bridge_displayed_equalities'], 43)
        self.assertEqual(len(ids_of(self.bridge)), 27)

    def test_validator_does_not_mutate_actual_roots_or_input_files(self):
        paths = [BASE/'sources/TE-B016.en.cnxml', BASE/'sources/TE-B016.source.json',
                 BASE/'translations/TE-B016.te.json', BASE/'translations/TE-B016.bridge.xhtml', BASE/'assets/B016/manifest.json']
        before_files = [sha256(p.read_bytes()).hexdigest() for p in paths]
        before_roots = [ET.tostring(n) for n in (self.target, self.bridge)]
        validate_b016(self.target, self.bridge)
        self.assertEqual(before_roots, [ET.tostring(n) for n in (self.target, self.bridge)])
        self.assertEqual(before_files, [sha256(p.read_bytes()).hexdigest() for p in paths])

    def test_each_of_twelve_displayed_values_rejects_corruption(self):
        for node in self.bridge.findall('.//' + XH + 'details'):
            ident = node.get('id')
            with self.subTest(detail=ident):
                bridge = copy.deepcopy(self.bridge)
                strong = list(self.node(bridge, ident).iter(XH + 'strong'))[1]
                strong.text = str(int(strong.text) + 1)
                with self.assertRaisesRegex(AssertionError, 'displayed value'):
                    validate_b016(self.target, bridge)

    def test_each_of_twelve_expressions_rejects_same_sum_reversal(self):
        for node in self.bridge.findall('.//' + XH + 'details'):
            ident = node.get('id')
            with self.subTest(detail=ident):
                bridge = copy.deepcopy(self.bridge)
                strong = list(self.node(bridge, ident).iter(XH + 'strong'))[0]
                a,b = expression_pair(strong.text); strong.text = f'{b}+{a}'
                with self.assertRaisesRegex(AssertionError, 'ordered expression'):
                    validate_b016(self.target, bridge)

    def test_19plus23_substitution_for_28plus14_same42_rejected(self):
        self.strong('B016-S-fs-id1311804', 0).text = '19+23'
        with self.assertRaisesRegex(AssertionError, 'ordered expression'):
            validate_b016(self.target, self.bridge)

    def test_true_equation_cannot_replace_requested_expression(self):
        self.strong('B016-S-fs-id2792137', 0).text = '37+69=106'
        with self.assertRaisesRegex(AssertionError, 'expression must contain'):
            validate_b016(self.target, self.bridge)

    def test_value_cannot_replace_requested_expression(self):
        self.strong('B016-S-D01', 0).text = '42'
        with self.assertRaisesRegex(AssertionError, 'expression must contain'):
            validate_b016(self.target, self.bridge)

    def test_expression_and_value_labels_cannot_swap(self):
        self.mutate(self.bridge, 'B016-S-R01', 'గణిత రాత:', 'విలువ:')
        with self.assertRaisesRegex(AssertionError, 'column roles|label association'):
            validate_b016(self.target, self.bridge)

    def test_all_43_displayed_equalities_reject_mutated_result(self):
        blocks = []
        for node in self.bridge.iter():
            if node.tag.rsplit('}',1)[-1] not in {'p','li','td','dd'}:
                continue
            if any(n is not node and n.tag.rsplit('}',1)[-1] in {'p','li','td','dd'} for n in node.iter()):
                continue
            blocks.extend((node, match.group()) for match in RELATION.finditer(text_of(node)))
        self.assertEqual(len(blocks), 43)
        paths = {id(n): i for i,n in enumerate(self.bridge.iter())}
        for index, (node, formula) in enumerate(blocks):
            with self.subTest(occurrence=index, formula=formula):
                bridge = copy.deepcopy(self.bridge)
                copied = list(bridge.iter())[paths[id(node)]]
                operands, total = equality(formula)
                replacement = formula.rsplit('=',1)[0] + '=' + str(total + 1)
                changed = False
                for inline in copied.iter():
                    for field in ('text','tail'):
                        value = getattr(inline,field)
                        if value and formula in value:
                            setattr(inline,field,value.replace(formula,replacement,1));changed=True;break
                    if changed:break
                self.assertTrue(changed, 'Mutated actual content, not expected constants')
                with self.assertRaises(AssertionError):
                    validate_b016(self.target, bridge)

    def test_column_equation_still_true_but_wrong_addend_digits_rejected(self):
        self.strong('B016-S-fs-id2792137', 3).text = '1+4+5=10'
        with self.assertRaisesRegex(AssertionError, 'ordered column arithmetic'):
            validate_b016(self.target, self.bridge)

    def test_actual_written_ones_digit_checked_in_prose(self):
        self.mutate(self.bridge, 'B016-S-fs-id1932733', '3 ఒకట్లు రాసి', '4 ఒకట్లు రాసి')
        with self.assertRaisesRegex(AssertionError, 'written ones'):
            validate_b016(self.target, self.bridge)

    def test_carry_ten_cannot_be_carry_hundred_in_ones_step(self):
        self.mutate(self.bridge, 'B016-W-fs-id1392862', '1 పదిని బదిలీ', '1 వందను బదిలీ')
        with self.assertRaisesRegex(AssertionError, 'carry destination'):
            validate_b016(self.target, self.bridge)

    def test_zero_tens_cannot_be_one_with_same_displayed_answer(self):
        self.mutate(self.bridge, 'B016-S-fs-id2130020', '0 పదులు రాసి', '1 పదులు రాసి')
        with self.assertRaisesRegex(AssertionError, 'zero tens'):
            validate_b016(self.target, self.bridge)

    def test_carry_hundred_cannot_be_ten_in_tens_step(self):
        self.mutate(self.bridge, 'B016-S-fs-id2792137', '1 వందను బదిలీ', '1 పదిని బదిలీ')
        with self.assertRaisesRegex(AssertionError, 'zero tens'):
            validate_b016(self.target, self.bridge)

    def test_no_carry_case_cannot_claim_a_carry(self):
        self.mutate(self.bridge, 'B016-W-fs-id1330230', 'బదిలీ అవసరం లేదు', 'బదిలీ అవసరం ఉంది')
        with self.assertRaisesRegex(AssertionError, 'no-carry case'):
            validate_b016(self.target, self.bridge)

    def test_no_carry_final_place_counts_cannot_swap(self):
        self.mutate(self.bridge, 'B016-W-fs-id1330230', '5 పదులు, 9 ఒకట్లు', '9 పదులు, 5 ఒకట్లు')
        with self.assertRaisesRegex(AssertionError, 'operand/carry/zero meaning'):
            validate_b016(self.target, self.bridge)

    def test_105_value_decomposition_cannot_lose_zero(self):
        self.mutate(self.bridge, 'B016-S-fs-id2130020', '1 వంద, 0 పదులు, 5 ఒకట్లు', '1 వంద, 1 పదులు, 5 ఒకట్లు')
        with self.assertRaisesRegex(AssertionError, 'operand/carry/zero meaning'):
            validate_b016(self.target, self.bridge)

    def test_106_cannot_lose_internal_zero(self):
        self.strong('B016-S-fs-id2792137', 1).text = '16'
        with self.assertRaisesRegex(AssertionError, 'displayed value'):
            validate_b016(self.target, self.bridge)

    def test_false_comparison_is_a_rejected_example_not_asserted_truth(self):
        self.assertIn('8>15 అనేది ఈ పదబంధానికి అనువాదం కాదు', text_of(self.node(self.bridge,'B016-S-D02')))
        validate_b016(self.target, self.bridge)
        self.mutate(self.bridge, 'B016-S-D02', 'అనువాదం కాదు', 'అనువాదం అవుతుంది')
        with self.assertRaisesRegex(AssertionError, 'operand/carry/zero meaning'):
            validate_b016(self.target, self.bridge)

    def test_true_comparison_cannot_replace_addition_translation(self):
        self.strong('B016-K3', 0).text = '8>7'
        with self.assertRaisesRegex(AssertionError, 'addition/comparison/zero'):
            validate_b016(self.target, self.bridge)

    def test_more_than_is_not_universal_keyword_rule(self):
        self.mutate(self.bridge, 'B016-K3', 'ఎప్పుడూ + గుర్తు పెట్టకండి', 'ఎప్పుడూ + గుర్తు పెట్టండి')
        with self.assertRaisesRegex(AssertionError, 'comparison/zero scope'):
            validate_b016(self.target, self.bridge)

    def test_zero_addition_is_not_decimal_concatenation(self):
        self.strong('B016-K3', 4).text = '90'
        with self.assertRaisesRegex(AssertionError, 'addition/comparison/zero'):
            validate_b016(self.target, self.bridge)

    def test_six_actual_english_prompts_checked(self):
        for ident in PRACTICE:
            with self.subTest(prompt=ident):
                bridge = copy.deepcopy(self.bridge)
                span = next(self.node(bridge,'B016-'+ident).iter(XH+'span'))
                before = span.text
                span.text = span.text.replace('increased by', 'decreased by').replace(' of ', ' for ').replace(' than ', ' above ').replace('added to', 'removed from')
                self.assertNotEqual(span.text, before)
                with self.assertRaisesRegex(AssertionError, 'phrase or direction'):
                    validate_b016(self.target, bridge)

    def test_six_actual_telugu_prompts_checked(self):
        for ident, (old,new) in {'D01':('24, 18','25, 17'),'R01':('16, 27','17, 26'),
                'D02':('15కంటే 8','8కంటే 15'),'R02':('19కు 6','6కు 19'),
                'D03':('46ను 57','57ను 46'),'R03':('38ను 64','64ను 38')}.items():
            with self.subTest(prompt=ident):
                bridge = copy.deepcopy(self.bridge); self.mutate(bridge,'B016-'+ident,old,new)
                with self.assertRaisesRegex(AssertionError, 'Telugu prompt roles'):
                    validate_b016(self.target, bridge)

    def test_practice_requires_expression_and_value(self):
        self.mutate(self.bridge, 'B016-D02', 'గణిత రాత, విలువ', 'విలువ మాత్రమే')
        with self.assertRaisesRegex(AssertionError, 'requires both stages'):
            validate_b016(self.target, self.bridge)

    def test_exact_source_backlinks_all_six(self):
        for ident, _, kind, _, _ in CASES:
            with self.subTest(exercise=ident):
                bridge = copy.deepcopy(self.bridge)
                next(self.node(bridge,'B016-'+kind+'-'+ident).iter(XH+'a')).set('href','#fs-id1826990')
                with self.assertRaisesRegex(AssertionError, 'exact source backlink'):
                    validate_b016(self.target, bridge)

    def test_missing_one_source_answer_rejected(self):
        parent = self.node(self.bridge,'B016-tryits')
        parent.remove(self.node(self.bridge,'B016-S-fs-id1311804'))
        with self.assertRaisesRegex(AssertionError, 'full solution coverage'):
            validate_b016(self.target, self.bridge)

    def test_wrong_existing_recheck_link_rejected(self):
        links = list(self.node(self.bridge,'B016-D02').iter(XH+'a'))
        links[-1].set('href','#B016-R01')
        with self.assertRaisesRegex(AssertionError, 'routing changed'):
            validate_b016(self.target, self.bridge)

    def test_all_six_table_expressions_reject_reversed_order(self):
        for i in range(6):
            with self.subTest(row=i):
                bridge = copy.deepcopy(self.bridge)
                row = self.node(bridge,'B016-K2').findall('.//'+XH+'tbody/'+XH+'tr')[i]
                a,b = expression_pair(text_of(row[2]));row[2].text=f'{b}+{a}'
                with self.assertRaisesRegex(AssertionError, 'phrase/expression direction'):
                    validate_b016(self.target, bridge)

    def test_table_base_quantity_cannot_swap_with_added_quantity(self):
        self.mutate(self.bridge, 'B016-K2', 'ఆధార సంఖ్య 7; కలిపే పరిమాణం 8', 'ఆధార సంఖ్య 8; కలిపే పరిమాణం 7')
        with self.assertRaisesRegex(AssertionError, 'table addend roles'):
            validate_b016(self.target, self.bridge)

    def test_optional_intro_values_cannot_be_claimed_source_answers(self):
        self.mutate(self.bridge, 'B016-K2', 'ఇవి మూల పట్టికలో కొత్త జవాబులుగా చేర్చినవి కావు', 'ఇవి మూల పట్టికలోని జవాబులు')
        with self.assertRaisesRegex(AssertionError, 'original-table scope'):
            validate_b016(self.target, self.bridge)

    def test_extra_true_equality_does_not_expand_reviewed_scope(self):
        self.node(self.bridge,'B016-K1').append(ET.fromstring('<p xmlns="http://www.w3.org/1999/xhtml">4+5=9</p>'))
        with self.assertRaisesRegex(AssertionError, 'equation coverage'):
            validate_b016(self.target, self.bridge)

    def test_duplicate_id_rejected(self):
        self.node(self.bridge,'B016-S-R01').set('id','B016-S-D01')
        with self.assertRaisesRegex(AssertionError, 'Duplicate'):
            validate_b016(self.target, self.bridge)


class _Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=Counter();self.tables={};self.labels={};self.links=[];self.active=None;self.cell=None

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if attrs.get('id'):self.ids[attrs['id']]+=1
        if tag=='table':
            self.active=attrs['id'];self.tables[self.active]=[];self.labels[self.active]=attrs.get('aria-label')
        elif tag=='tr' and self.active:self.tables[self.active].append([])
        elif tag in {'th','td'} and self.active:
            self.cell=[tag,attrs.get('scope'),['']];self.tables[self.active][-1].append(self.cell)
        elif tag=='br' and self.cell:self.cell[2].append('')
        elif tag=='a':self.links.append([attrs.get('href'),''])

    def handle_data(self, data):
        if self.cell:self.cell[2][-1]+=data
        # Only one source link is present, so a separate active flag is unnecessary
        # for the exact node-link test, which parses that <a> via ElementTree.

    def handle_endtag(self,tag):
        if tag in {'th','td'}:self.cell=None
        if tag=='table':self.active=None


class ActualRendererTests(_Fixture):
    def rendered(self, english=False):
        from build_unit import render
        p=_Reader();p.feed(render(self.source if english else self.target,self.assets,'en-' if english else '',english));p.close();return p

    def test_three_actual_table_shapes_and_source_ids_both_languages(self):
        for english in (False,True):
            with self.subTest(english=english):
                p=self.rendered(english);prefix='en-' if english else ''
                self.assertEqual({i:[len(r) for r in rows] for i,rows in p.tables.items()},
                                 {prefix+i:[width]*height for i,(_,height,width) in TABLES.items()})
                self.assertEqual(set(p.ids),{prefix+i for i in ids_of(self.source)})
                self.assertTrue(all(n==1 for n in p.ids.values()))

    def test_intro_newline_mapping_all_six_expressions_both_languages(self):
        for english in (False,True):
            with self.subTest(english=english):
                p=self.rendered(english);rows=p.tables[('en-' if english else '')+'fs-id1826990']
                self.assertTrue(all(cell[:2]==['th','col'] for cell in rows[0]))
                self.assertEqual([len(c[2]) for c in rows[1]], [1,6,6,6])
                self.assertEqual(tuple(expression_pair(x) for x in rows[1][3][2]),INTRO_PAIRS)
                if english:self.assertEqual(tuple(' '.join(s.split()) for s in rows[1][2][2]),INTRO)

    def test_rendered_summary_labels_and_empty_cells_remain_actual(self):
        for english in (False,True):
            with self.subTest(english=english):
                root=self.source if english else self.target;p=self.rendered(english);prefix='en-' if english else ''
                for ident in list(TABLES)[1:]:
                    self.assertEqual(p.labels[prefix+ident],self.node(root,ident).get('summary'))
                    rows=p.tables[prefix+ident]
                    self.assertEqual(rows[0][0][2],['']);self.assertEqual(rows[3][0][2],[''])

    def test_table_link_has_correct_bilingual_label_and_prefix(self):
        from build_unit import render
        for english in (False,True):
            with self.subTest(english=english):
                root=self.source if english else self.target;prefix='en-' if english else ''
                link=next(root.iter(CN+'link'));before=ET.tostring(link)
                a=ET.fromstring(render(link,self.assets,prefix,english))
                self.assertEqual(a.get('href'),'#'+prefix+'fs-id1826990')
                self.assertEqual(a.text,'Referenced table' if english else 'సంబంధిత పట్టిక')
                self.assertEqual(ET.tostring(link),before)

    def test_registered_table_declaration_corruption_rejected(self):
        from build_unit import render
        for ident in TABLES:
            with self.subTest(table=ident):
                table=copy.deepcopy(self.node(self.target,ident));table.find(CN+'tgroup').set('cols','6')
                with self.assertRaisesRegex(AssertionError,'Registered table source changed'):
                    render(table,self.assets)

    def test_unregistered_column_defect_is_not_silently_generalized(self):
        from build_unit import render
        table=copy.deepcopy(self.node(self.target,'fs-id1826990'));table.set('id','unregistered-table')
        with self.assertRaises(AssertionError):render(table,self.assets)

    def test_skipped_structural_id_cannot_silently_disappear(self):
        from build_unit import render
        table=copy.deepcopy(self.node(self.target,'eip-id1168288294973'))
        table.find('.//'+CN+'entry').set('id','must-be-preserved')
        with self.assertRaisesRegex(AssertionError,'ID would be discarded'):render(table,self.assets)


if __name__=='__main__':
    unittest.main()
