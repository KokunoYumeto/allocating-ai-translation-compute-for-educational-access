"""Read-only B015 source, actual-answer, carry, and renderer regressions."""
import copy
from collections import Counter
from html.parser import HTMLParser
import re
import unittest
import xml.etree.ElementTree as ET

from addition_algorithm_checks import (BASE, CN, MATH, XH, SVG, PREFIX, ASSETS,
    EXERCISES, TRY_CASES, WORKED_CASES, TABLES, MEDIA_IDS, ids_of, integer,
    column_steps, problem_parts, addition_table, source_column_frames,
    source_cases, horizontal_math, column_frame, svg_arithmetic,
    checked_relation, displayed_equalities, validate_algorithm_target,
    validate_b015, RELATION, EXTRA_CASES, bridge_column_table, compact, text_of)


class ArithmeticBaselineTests(unittest.TestCase):
    def setUp(self):
        self.source, self.cases = source_cases()

    def test_actual_source_inventory(self):
        from inspect_source import slots
        self.assertEqual(len(list(slots(self.source))), 859)
        self.assertEqual(len(WORKED_CASES), 7)
        self.assertEqual(len(TRY_CASES), 14)
        self.assertEqual(sum(len(c[3]) for c in WORKED_CASES), 9)
        self.assertEqual(sum(len(c[3]) for c in TRY_CASES), 18)
        self.assertEqual(sum(len(c[2]) for c in self.cases), 27)

    def test_every_source_part_recomputed(self):
        self.assertEqual([a for c in self.cases for a in c[3]],
            [11, 42, 19, 39, 24, 57, 15, 15, 16, 16, 14, 14, 89, 86, 99,
             112, 133, 161, 910, 832, 847, 2162, 5282, 6532, 30814, 52873, 61416])
        for _, _, parts, totals in self.cases:
            for part, answer in zip(parts, totals):
                with self.subTest(addends=part):
                    self.assertEqual(sum(r['digit'] * r['unit'] for r in column_steps(part)), answer)

    def test_100_addition_cells_and_all_headers(self):
        self.assertEqual(addition_table(self.source), 100)

    def test_each_actual_table_cell_corruption_rejected(self):
        for a in range(10):
            for b in range(10):
                with self.subTest(row=a, column=b):
                    altered = copy.deepcopy(self.source)
                    table = ids_of(altered)['fs-id2300206']
                    cell = table.findall('.//' + CN + 'tbody/' + CN + 'row')[a][b + 1]
                    cell.text = str(a + b + 1)
                    with self.assertRaisesRegex(AssertionError, 'addition-table sum'):
                        addition_table(altered)

    def test_actual_table_top_header_swap_rejected(self):
        table = ids_of(self.source)['fs-id2300206']
        row = table.find('.//' + CN + 'thead/' + CN + 'row')
        row[1].text, row[2].text = row[2].text, row[1].text
        with self.assertRaisesRegex(AssertionError, 'header'):
            addition_table(self.source)

    def test_actual_table_side_header_swap_rejected(self):
        rows = ids_of(self.source)['fs-id2300206'].findall('.//' + CN + 'tbody/' + CN + 'row')
        rows[2][0].text, rows[3][0].text = rows[3][0].text, rows[2][0].text
        with self.assertRaisesRegex(AssertionError, 'row header'):
            addition_table(self.source)

    def test_all_horizontal_numeric_math_and_column_frames(self):
        self.assertEqual(len(horizontal_math(self.source)), 42)
        self.assertEqual(source_column_frames(self.source), 16)

    def test_identity_zero_order_and_all_zero(self):
        for pair in ((0, 11), (42, 0), (0, 0)):
            with self.subTest(pair=pair):
                self.assertTrue(all(r['outgoing'] == 0 for r in column_steps(pair)))
        problems = [problem_parts(e.find(CN + 'problem')) for e in self.source.iter(CN + 'exercise')]
        self.assertEqual(problems[:3], [((0, 11), (42, 0)), ((0, 19), (39, 0)), ((0, 24), (57, 0))])

    def test_commutation_has_ordered_distinct_questions(self):
        for left, right in (((8, 7), (7, 8)), ((9, 7), (7, 9)), ((8, 6), (6, 8))):
            self.assertNotEqual(left, right)
            self.assertEqual(sum(left), sum(right))
            self.assertEqual([r['total'] for r in column_steps(left)], [r['total'] for r in column_steps(right)])

    def test_exact_ten_writes_zero_and_carries_one(self):
        first = column_steps((324, 586))[0]
        self.assertEqual((first['total'], first['digit'], first['outgoing']), (10, 0, 1))
        self.assertEqual([r['digit'] for r in column_steps((324, 586))], [0, 1, 9])

    def test_three_addends_carry_two_not_one(self):
        rows = column_steps((21357, 861, 8596))
        self.assertEqual([r['total'] for r in rows], [14, 21, 18, 10, 3])
        self.assertEqual([r['outgoing'] for r in rows], [1, 2, 1, 1, 0])
        self.assertEqual([r['incoming'] for r in rows], [0, 1, 2, 1, 1])
        self.assertEqual([r['partial'] for r in rows], ['4', '14', '814', '0814', '30814'])
        self.assertEqual(rows[1]['outgoing'] * 100, 200)

    def test_unequal_lengths_pad_only_missing_places(self):
        rows = column_steps((1683, 479))
        self.assertEqual([r['digits'] for r in rows], [(3, 9), (8, 7), (6, 4), (1, 0)])
        self.assertEqual([r['partial'] for r in rows], ['2', '62', '162', '2162'])

    def test_new_final_column_and_all_nines(self):
        self.assertEqual([r['digit'] for r in column_steps((43, 69))], [2, 1, 1])
        self.assertEqual([r['digit'] for r in column_steps((999, 1))], [0, 0, 0, 1])
        self.assertEqual([r['outgoing'] for r in column_steps((99, 99, 99))], [2, 2, 0])

    def test_nonwhole_negative_bool_inputs_rejected(self):
        for values in ((1,), (-1, 2), (1.0, 2), (True, 2)):
            with self.subTest(values=values), self.assertRaises(AssertionError):
                column_steps(values)

    def test_invalid_grouping_not_silently_normalized(self):
        for value in ('0814', '30,81,4', '3,08,14', '30.814', '-1'):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                integer(value)

    def test_source_partial_leading_zero_cannot_be_dropped(self):
        n = next(n for n in self.source.iter(MATH + 'mn') if n.text == '0814')
        n.text = '814'
        with self.assertRaisesRegex(AssertionError, 'partial result'):
            source_column_frames(self.source)

    def test_actual_source_carry_two_corruption_rejected(self):
        table = ids_of(self.source)['eip-id1168288531101']
        frame = list(table.iter(MATH + 'mtable'))[2]
        marker = next(n for n in frame.iter(MATH + 'mn') if n.get('mathsize') == 'small' and n.text == '2')
        marker.text = '1'
        with self.assertRaisesRegex(AssertionError, 'carry place/count'):
            source_column_frames(self.source)

    def test_carry_cannot_be_moved_to_wrong_place_with_same_sum(self):
        table = ids_of(self.source)['eip-id1168288531101']
        frame = list(table.iter(MATH + 'mtable'))[2]
        movers = list(frame.iter(MATH + 'mover'))
        movers[0][1].text, movers[1][1].text = movers[1][1].text, movers[0][1].text
        with self.assertRaisesRegex(AssertionError, 'carry place/count'):
            source_column_frames(self.source)

    def test_delayed_source_carry_marker_is_explicit_exception(self):
        frames = list(ids_of(self.source)['eip-id1168288687380'].iter(MATH + 'mtable'))
        self.assertEqual(column_frame(frames[3]), (('1,683', '479', '162'), {100: 1, 10: 1}))
        self.assertEqual(column_frame(frames[4]), (('1,683', '479', '2,162'), {1000: 1, 100: 1, 10: 1}))

    def test_partial_value_error_not_hidden_by_correct_final(self):
        table = ids_of(self.source)['eip-id1168288687380']
        frame = list(table.iter(MATH + 'mtable'))[2]
        next(n for n in frame.iter(MATH + 'mn') if n.text == '62').text = '72'
        with self.assertRaisesRegex(AssertionError, 'partial result'):
            source_column_frames(self.source)

    def test_wrong_ones_alignment_addend_rejected(self):
        table = ids_of(self.source)['eip-id1168288687380']
        frame = list(table.iter(MATH + 'mtable'))[0]
        next(n for n in frame.iter(MATH + 'mn') if n.text == '479').text = '4,790'
        with self.assertRaisesRegex(AssertionError, 'main digits'):
            source_column_frames(self.source)

    def test_actual_source_horizontal_answer_corruption_rejected(self):
        for ident, _, kind, _ in TRY_CASES:
            with self.subTest(exercise=ident):
                source = copy.deepcopy(self.source)
                solution = ids_of(source)[ident].find(CN + 'solution')
                n = list(solution.iter(MATH + 'mn'))[-1]
                n.text = str(integer(n.text) + 1)
                with self.assertRaisesRegex(AssertionError, 'Incorrect B015 displayed equality'):
                    horizontal_math(source)

    def test_equality_checks_whole_chain_not_correct_prefix(self):
        self.assertEqual(checked_relation('21,357 + 861 + 8,596 = 30,814'), '21,357+861+8,596=30,814')
        with self.assertRaisesRegex(AssertionError, 'Incorrect'):
            checked_relation('7 + 3 = 10 = 11')

    def test_displayed_equality_extraction_handles_nested_strong(self):
        node = ET.fromstring('<section xmlns="http://www.w3.org/1999/xhtml"><p>జవాబు: <strong>324 + 586 = 910</strong>.</p><table><tr><td>1 + 5 + 6 + 9 = 21</td></tr></table></section>')
        self.assertEqual(displayed_equalities(node), ['324+586=910', '1+5+6+9=21'])

    def test_prose_comma_after_answer_does_not_hide_equation(self):
        node = ET.fromstring('<p xmlns="http://www.w3.org/1999/xhtml">కాబట్టి <strong>8+7=15</strong>, <strong>7+8=15</strong>.</p>')
        self.assertEqual(displayed_equalities(node), ['8+7=15', '7+8=15'])
        node[0].text = '8+7=16'
        with self.assertRaisesRegex(AssertionError, 'Incorrect'):
            displayed_equalities(node)


class SvgArithmeticTests(unittest.TestCase):
    def svg(self, suffix):
        return ET.parse(BASE / ('assets/B015/' + PREFIX + suffix + '.te.svg')).getroot()

    def test_five_actual_assets_and_values(self):
        self.assertEqual([svg_arithmetic(self.svg(s), s) for s in ASSETS], [43, 910, 910, 910, 910])

    def test_each_visible_digit_corruption_rejected(self):
        for suffix in ASSETS:
            original = self.svg(suffix)
            digits = [n for n in original.iter(SVG + 'text') if n.get('data-role') == 'digit']
            for i in range(len(digits)):
                with self.subTest(asset=suffix, digit=i):
                    svg = copy.deepcopy(original)
                    n = [n for n in svg.iter(SVG + 'text') if n.get('data-role') == 'digit'][i]
                    n.text = str((int(n.text) + 1) % 10)
                    with self.assertRaisesRegex(AssertionError, 'operand/result'):
                        svg_arithmetic(svg, suffix)

    def test_carry_is_not_fraction_and_has_count_one(self):
        for suffix in ASSETS:
            if suffix == '020-01':
                continue
            with self.subTest(asset=suffix):
                svg = self.svg(suffix)
                next(n for n in svg.iter(SVG + 'text') if n.get('data-role') == 'carry').text = '2'
                with self.assertRaisesRegex(AssertionError, 'carry count/place'):
                    svg_arithmetic(svg, suffix)

    def test_carry_horizontal_shift_caught_despite_correct_metadata(self):
        svg = self.svg('020-03')
        n = next(n for n in svg.iter(SVG + 'text') if n.get('data-role') == 'carry')
        n.set('x', str(float(n.get('x')) + 56))
        with self.assertRaisesRegex(AssertionError, 'above target place'):
            svg_arithmetic(svg, '020-03')

    def test_partial_zero_position_cannot_shift_to_tens(self):
        svg = self.svg('020-02')
        n = next(n for n in svg.iter(SVG + 'text') if n.get('data-row') == 'sum')
        n.set('x', str(float(n.get('x')) - 56))
        with self.assertRaisesRegex(AssertionError, 'place alignment'):
            svg_arithmetic(svg, '020-02')

    def test_partial_result_cannot_prematurely_show_final(self):
        svg = self.svg('020-02')
        final = self.svg('020-04')
        svg.append(copy.deepcopy(next(n for n in final.iter(SVG + 'text') if n.get('data-row') == 'sum' and n.get('data-place') == 'hundreds')))
        with self.assertRaisesRegex(AssertionError, 'operand/result'):
            svg_arithmetic(svg, '020-02')

    def test_carry_cannot_be_displayed_as_fraction_bar(self):
        svg = self.svg('020-03')
        line = next(n for n in svg.iter(SVG + 'line') if n.get('data-role') == 'sum-rule')
        line.set('y1', '80')
        with self.assertRaisesRegex(AssertionError, 'rule is not below'):
            svg_arithmetic(svg, '020-03')

    def test_actual_rod_must_have_ten_cells(self):
        svg = self.svg('001')
        g = next(svg.iter(SVG + 'g')); g.remove(g[-1])
        with self.assertRaisesRegex(AssertionError, 'rod does not have ten'):
            svg_arithmetic(svg, '001')

    def test_model_same_total_cannot_move_units_between_addends(self):
        svg = self.svg('001')
        groups = {g.get('data-group'): g for g in svg.iter(SVG + 'g')}
        cell = groups['a-ones-bottom'][-1]
        groups['a-ones-bottom'].remove(cell)
        cell.set('x', '486'); cell.set('y', '232')
        groups['b-ones-bottom'].append(cell)
        with self.assertRaisesRegex(AssertionError, 'before/after'):
            svg_arithmetic(svg, '001')

    def test_callout_equation_answer_corruption_rejected(self):
        svg = self.svg('001')
        next(n for n in svg.iter(SVG + 'text') if n.get('data-role') == 'carry-equation').text = '1 + 1 + 2 = 3'
        with self.assertRaisesRegex(AssertionError, 'callout'):
            svg_arithmetic(svg, '001')


class _ActualFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from build_unit import unit_inputs, localize, asset_map
        cls.actual_source, cls.meta, cls.catalog = unit_inputs('TE-B015')
        cls.assets = asset_map('TE-B015')
        cls.actual_target = localize(cls.actual_source, cls.catalog, cls.assets)
        cls.actual_bridge = ET.parse(BASE / 'translations/TE-B015.bridge.xhtml').getroot()

    def setUp(self):
        self.source = copy.deepcopy(self.actual_source)
        self.target = copy.deepcopy(self.actual_target)
        self.bridge = copy.deepcopy(self.actual_bridge)

    def node(self, root, ident):
        return ids_of(root)[ident]

    def mutate(self, root, ident, before, after):
        for n in self.node(root, ident).iter():
            for key in ('text', 'tail'):
                value = getattr(n, key)
                if value and before in value:
                    setattr(n, key, value.replace(before, after, 1))
                    return
        self.fail('Actual mutation phrase not found: ' + ident + ': ' + before)


class ActualTargetTests(_ActualFixture):
    def test_actual_shared_localization_and_math(self):
        self.assertEqual(len(validate_algorithm_target(self.target)), 21)
        self.assertEqual(len(self.catalog['translations']), 162)
        self.assertEqual(self.meta['text_slots'], 859)

    def test_actual_symbolic_identity_and_commutation_are_protected(self):
        self.assertEqual([n.text for n in self.target.iter(MATH + 'mi')],
                         [n.text for n in self.source.iter(MATH + 'mi')])
        for value in ('a', 'b'):
            target = copy.deepcopy(self.target)
            next(n for n in target.iter(MATH + 'mi') if n.text == value).text = 'c'
            with self.subTest(symbol=value), self.assertRaisesRegex(AssertionError, 'MathML'):
                validate_algorithm_target(target)

    def test_protected_12_period_token_unchanged(self):
        n = next(n for n in self.target.iter(MATH + 'mn') if n.text == '12.')
        n.text = '12'
        with self.assertRaisesRegex(AssertionError, 'MathML'):
            validate_algorithm_target(self.target)

    def test_all_21_original_solution_id_mutations_rejected(self):
        for _, solution, _, _ in EXERCISES:
            with self.subTest(solution=solution):
                target = copy.deepcopy(self.target)
                self.node(target, solution).set('id', solution + '-changed')
                with self.assertRaisesRegex(AssertionError, 'structure'):
                    validate_algorithm_target(target)

    def test_source_same_sum_operand_order_swap_rejected(self):
        problem = self.node(self.target, 'fs-id2454866').find(CN + 'problem')
        nums = list(problem.iter(MATH + 'mn'))
        nums[0].text, nums[1].text = nums[1].text, nums[0].text
        with self.assertRaisesRegex(AssertionError, 'MathML'):
            validate_algorithm_target(self.target)

    def test_actual_localized_addition_cell_corruption_rejected(self):
        row = self.node(self.target, 'fs-id2300206').findall('.//' + CN + 'tbody/' + CN + 'row')[9]
        row[10].text = '17'
        with self.assertRaisesRegex(AssertionError, 'addition-table sum'):
            validate_algorithm_target(self.target)

    def test_each_translated_summary_numeric_corruption_rejected(self):
        tables = [t for t in self.target.iter(CN + 'table') if t.get('summary')]
        self.assertEqual(len(tables), 8)
        for table in tables:
            with self.subTest(table=table.get('id')):
                target = copy.deepcopy(self.target)
                t = self.node(target, table.get('id'))
                value = t.get('summary')
                t.set('summary', re.sub(r'\d', '9', value, count=1))
                with self.assertRaisesRegex(AssertionError, 'accessible numbers'):
                    validate_algorithm_target(target)

    def test_accessible_partial0814_cannot_lose_zero(self):
        t = self.node(self.target, 'eip-id1168288531101')
        t.set('summary', t.get('summary').replace('0814', '814'))
        with self.assertRaisesRegex(AssertionError, 'accessible numbers'):
            validate_algorithm_target(self.target)

    def test_summary_wrong_column_count_rejected(self):
        t = self.node(self.target, 'eip-id1168288531101')
        t.set('summary', t.get('summary').replace('రెండు నిలువు', 'మూడు నిలువు'))
        with self.assertRaisesRegex(AssertionError, 'dimensions'):
            validate_algorithm_target(self.target)

    def test_frozen_three_column_declaration_not_rewritten(self):
        self.node(self.target, 'eip-id1168288531101').find(CN + 'tgroup').set('cols', '2')
        with self.assertRaisesRegex(AssertionError, 'structure'):
            validate_algorithm_target(self.target)

    def test_small_carries_cannot_be_fractions_in_target_alt(self):
        for ident in MEDIA_IDS[-2:]:
            with self.subTest(media=ident):
                target = copy.deepcopy(self.target)
                media = self.node(target, ident)
                media.set('alt', media.get('alt').replace('భిన్నాలు కావు', 'భిన్నాలు అవుతాయి'))
                with self.assertRaisesRegex(AssertionError, 'not fraction'):
                    validate_algorithm_target(target)

    def test_target_alt_carry_place_cannot_change_with_same_digit(self):
        n = self.node(self.target, MEDIA_IDS[3])
        n.set('alt', n.get('alt').replace('వందల అంకె 3', 'వేల అంకె 3'))
        with self.assertRaisesRegex(AssertionError, 'partial carry'):
            validate_algorithm_target(self.target)

    def test_model_ten_count_cannot_be_one_unit(self):
        n = self.node(self.target, MEDIA_IDS[0])
        n.set('alt', n.get('alt').replace('26కు రెండు పది-కడ్డీలు', '26కు ఒక పది-కడ్డీ'))
        with self.assertRaisesRegex(AssertionError, 'model/carry'):
            validate_algorithm_target(self.target)

    def test_literal_eleven_tens_instruction_not_changed(self):
        self.mutate(self.target, 'eip-id1168287505854', 'మొత్తంలో 11 రాయండి', 'మొత్తంలో 1 రాయండి')
        with self.assertRaisesRegex(AssertionError, 'eleven tens'):
            validate_algorithm_target(self.target)

    def test_algorithm_direction_and_inclusive_boundary(self):
        self.mutate(self.target, 'fs-id1567373', 'దానికంటే ఎక్కువైతే', 'దానికంటే తక్కువైతే')
        with self.assertRaisesRegex(AssertionError, 'column algorithm'):
            validate_algorithm_target(self.target)

    def test_carry_exchange_cannot_change_unit_value(self):
        self.mutate(self.target, 'fs-id2877345', ' వందగా', ' పదిగా')
        with self.assertRaisesRegex(AssertionError, 'exchange value'):
            validate_algorithm_target(self.target)

    def test_three_addend_carry_destination_not_ones(self):
        self.mutate(self.target, 'eip-id1168288531101', ' వందలను వందల స్థానానికి', ' వందలను ఒకట్ల స్థానానికి')
        with self.assertRaisesRegex(AssertionError, 'carry count/value/target'):
            validate_algorithm_target(self.target)

    def test_zero_identity_meaning_cannot_reverse(self):
        self.mutate(self.target, 'fs-id1516824', 'సున్నను కలిపితే అదే సంఖ్య వస్తుంది', 'సున్నను కలిపితే సున్న వస్తుంది')
        with self.assertRaisesRegex(AssertionError, 'zero identity'):
            validate_algorithm_target(self.target)

    def test_commutation_sum_cannot_change(self):
        self.mutate(self.target, 'fs-id2785833', 'క్రమాన్ని తిప్పినా మొత్తం మారదు', 'క్రమాన్ని తిప్పినా మొత్తం మారుతుంది')
        with self.assertRaisesRegex(AssertionError, 'commutative property'):
            validate_algorithm_target(self.target)


class ActualBridgeTests(_ActualFixture):
    def test_actual_final_bridge_coverage(self):
        self.assertEqual(validate_b015(self.target, self.bridge), {
            'source_exercises': 21, 'source_parts': 27, 'source_try_it_parts': 18,
            'addition_table_cells': 100, 'original_solution_ids': 21, 'source_math_expressions': 135,
            'source_vertical_frames': 16, 'source_assets': 5, 'bridge_solution_details': 29,
            'entry_recheck_prompts': 8, 'entry_recheck_ordered_sums': 10,
            'bridge_column_tables': 21, 'bridge_column_rows': 70, 'bridge_equation_occurrences': 139})

    def test_every_actual_displayed_equation_corruption_rejected(self):
        slots = [(i, key, match.start(), match.end()) for i, n in enumerate(self.bridge.iter())
                 for key in ('text', 'tail') for match in RELATION.finditer(getattr(n, key) or '')]
        self.assertEqual(len(slots), 139)
        for i, key, start, end in slots:
            with self.subTest(node=i, field=key, start=start):
                bridge = copy.deepcopy(self.bridge)
                n = list(bridge.iter())[i]; value = getattr(n, key)
                expr = value[start:end]
                original_answer = expr.rsplit('=', 1)[1].strip()
                # Two unit-exchange equations have products on the right.
                # Mutate their final actual numeric token, not a parsed total.
                token = list(re.finditer(r'[0-9]+(?:,[0-9]{3})*', original_answer))[-1]
                value_token = token.group()
                wrong = format(integer(value_token) + 1, ',') if ',' in value_token else str(integer(value_token) + 1)
                wrong_side = original_answer[:token.start()] + wrong + original_answer[token.end():]
                altered = expr.rsplit('=', 1)[0] + '=' + wrong_side
                setattr(n, key, value[:start] + altered + value[end:])
                with self.assertRaises(AssertionError):
                    validate_b015(self.target, bridge)

    def test_all_70_written_digit_mutations_rejected(self):
        tables = list(self.bridge.iter(XH + 'table'))
        self.assertEqual(sum(len(t.findall(XH + 'tbody/' + XH + 'tr')) for t in tables), 70)
        for ti, table in enumerate(tables):
            for ri, _ in enumerate(table.findall(XH + 'tbody/' + XH + 'tr')):
                with self.subTest(table=ti, row=ri):
                    bridge = copy.deepcopy(self.bridge)
                    row = list(bridge.iter(XH + 'table'))[ti].findall(XH + 'tbody/' + XH + 'tr')[ri]
                    row[2].text = str((int(row[2].text) + 1) % 10)
                    with self.assertRaisesRegex(AssertionError, 'written digit/zero'):
                        validate_b015(self.target, bridge)

    def test_every_carry_count_mutation_rejected(self):
        for ti, table in enumerate(self.bridge.iter(XH + 'table')):
            for ri, _ in enumerate(table.findall(XH + 'tbody/' + XH + 'tr')):
                with self.subTest(table=ti, row=ri):
                    bridge = copy.deepcopy(self.bridge)
                    row = list(bridge.iter(XH + 'table'))[ti].findall(XH + 'tbody/' + XH + 'tr')[ri]
                    row[3].text = str(int(row[3].text[0]) + 1) + row[3].text[1:]
                    with self.assertRaisesRegex(AssertionError, 'carry count/target'):
                        validate_b015(self.target, bridge)

    def test_each_source_bridge_backlink_wrong_existing_id_rejected(self):
        for ident, _, kind, _ in EXERCISES:
            with self.subTest(exercise=ident):
                bridge = copy.deepcopy(self.bridge)
                key = ('B015-W-' if kind == 'worked' else 'B015-S-') + ident
                link = self.node(bridge, key).find('.//' + XH + 'a')
                link.set('href', '#fs-id2362020' if ident != 'fs-id2362020' else '#fs-id1264596')
                with self.assertRaisesRegex(AssertionError, 'backlink'):
                    validate_b015(self.target, bridge)

    def test_missing_whole_source_solution_rejected(self):
        self.node(self.bridge, 'B015-S-fs-id1406185').set('id', 'removed')
        with self.assertRaisesRegex(AssertionError, 'detail coverage'):
            validate_b015(self.target, self.bridge)

    def test_two_part_source_solution_cannot_swap_a_b(self):
        a = self.node(self.bridge, 'B015-S-fs-id1968047-a')
        b = self.node(self.bridge, 'B015-S-fs-id1968047-b')
        a.set('id', 'B015-S-fs-id1968047-b'); b.set('id', 'B015-S-fs-id1968047-a')
        with self.assertRaisesRegex(AssertionError, 'part IDs/order'):
            validate_b015(self.target, self.bridge)

    def test_same_answer_does_not_allow_reversed_zero_question(self):
        self.mutate(self.bridge, 'B015-S-fs-id1264596-a', '0+19=19', '19+0=19')
        with self.assertRaisesRegex(AssertionError, 'ordered operands'):
            validate_b015(self.target, self.bridge)

    def test_same_answer_different_diagnostic_operands_rejected(self):
        self.mutate(self.bridge, 'B015-D02', '306+42', '307+41')
        with self.assertRaisesRegex(AssertionError, 'requested operands'):
            validate_b015(self.target, self.bridge)

    def test_same_computed_sum_different_requested_digit_rejected(self):
        self.mutate(self.bridge, 'B015-D02', '42లోని 4', '42లోని 2')
        with self.assertRaisesRegex(AssertionError, 'target place or carry question'):
            validate_b015(self.target, self.bridge)

    def test_coincident_zero_columns_cannot_change_target_place(self):
        table = self.node(self.bridge, 'B015-S-R03').find(XH + 'table')
        rows = table.findall(XH + 'tbody/' + XH + 'tr')
        self.assertEqual(text_of(rows[1][1]), text_of(rows[2][1]))
        self.assertEqual(text_of(rows[1][2]), text_of(rows[2][2]))
        rows[1][0].text = 'వందల స్థానం'
        with self.assertRaisesRegex(AssertionError, 'target place changed'):
            validate_b015(self.target, self.bridge)

    def test_correct_equality_cannot_hide_wrong_digits_and_incoming_carry(self):
        table = self.node(self.bridge, 'B015-S-D04').find(XH + 'table')
        table.findall(XH + 'tbody/' + XH + 'tr')[1][1].text = '1+7+8+6=22'
        with self.assertRaisesRegex(AssertionError, 'incoming carry/addend digits'):
            validate_b015(self.target, self.bridge)

    def test_same_carry_count_different_destination_rejected(self):
        table = self.node(self.bridge, 'B015-S-R04').find(XH + 'table')
        table.findall(XH + 'tbody/' + XH + 'tr')[0][3].text = '2 — వందల స్థానానికి'
        with self.assertRaisesRegex(AssertionError, 'carry count/target'):
            validate_b015(self.target, self.bridge)

    def test_omitted_new_final_carry_row_rejected(self):
        body = self.node(self.bridge, 'B015-S-R03').find(XH + 'table/' + XH + 'tbody')
        body.remove(body[-1])
        with self.assertRaisesRegex(AssertionError, 'missing/extra place'):
            validate_b015(self.target, self.bridge)

    def test_missing_high_place_zero_cannot_be_replaced_with_a_digit(self):
        table = self.node(self.bridge, 'B015-W-fs-id2264879').find(XH + 'table')
        table.findall(XH + 'tbody/' + XH + 'tr')[3][1].text = '1+1+1+7=10'
        with self.assertRaisesRegex(AssertionError, 'incoming carry/addend digits'):
            validate_b015(self.target, self.bridge)

    def test_correct_answer_does_not_allow_reversed_caption(self):
        table = self.node(self.bridge, 'B015-S-fs-id2325520').find(XH + 'table')
        table.find(XH + 'caption').text = '54+32 — స్థానాలవారీ పూర్తి లెక్క'
        with self.assertRaisesRegex(AssertionError, 'caption operands'):
            validate_b015(self.target, self.bridge)

    def test_column_roles_cannot_be_swapped(self):
        table = self.node(self.bridge, 'B015-S-D04').find(XH + 'table')
        row = table.find(XH + 'thead/' + XH + 'tr')
        row[2].text, row[3].text = row[3].text, row[2].text
        with self.assertRaisesRegex(AssertionError, 'column roles'):
            validate_b015(self.target, self.bridge)

    def test_source_0814_explanation_cannot_lose_zero(self):
        self.mutate(self.bridge, 'B015-W-fs-id2264879', '0814లో', '814లో')
        with self.assertRaisesRegex(AssertionError, 'partial0814'):
            validate_b015(self.target, self.bridge)

    def test_source_delayed_carry_cannot_be_called_complete_answer(self):
        self.mutate(self.bridge, 'B015-W-fs-id2144790', '162 పూర్తి జవాబు కాదు', '162 పూర్తి జవాబు')
        with self.assertRaisesRegex(AssertionError, 'delayed source carry'):
            validate_b015(self.target, self.bridge)

    def test_carry2_value_cannot_be_twenty_in_hundreds(self):
        self.mutate(self.bridge, 'B015-K3', 'విలువ 210', 'విలువ 21')
        with self.assertRaisesRegex(AssertionError, 'column-unit meaning'):
            validate_b015(self.target, self.bridge)

    def test_final_eleven_tens_not_eleven_ones(self):
        self.mutate(self.bridge, 'B015-W-fs-id2325655', 'ఒకట్ల స్థానంలో 11ను రాయడం కాదు', 'ఒకట్ల స్థానంలో 11ను రాయాలి')
        with self.assertRaisesRegex(AssertionError, 'eleven-tens'):
            validate_b015(self.target, self.bridge)

    def test_zero_append_misconception_explanation_guard(self):
        self.mutate(self.bridge, 'B015-S-fs-id2362020-b', '570 చేయకండి', '570 చేయండి')
        with self.assertRaisesRegex(AssertionError, 'zero versus appending'):
            validate_b015(self.target, self.bridge)

    def test_recheck_zero_place_cannot_be_deleted_in_explanation(self):
        self.mutate(self.bridge, 'B015-S-R03', 'పదుల, వందల రెండు సున్నలూ అవసరం', 'పదుల, వందల రెండు సున్నలూ అనవసరం')
        with self.assertRaisesRegex(AssertionError, 'all-carry zeros'):
            validate_b015(self.target, self.bridge)

    def test_route_wrong_existing_recheck_rejected(self):
        node = self.node(self.bridge, 'B015-D04')
        next(n for n in node.iter(XH + 'a') if n.get('href') == '#B015-R04').set('href', '#B015-R03')
        with self.assertRaisesRegex(AssertionError, 'routing backlink'):
            validate_b015(self.target, self.bridge)

    def test_extra_true_equation_cannot_hide_unreviewed_support(self):
        self.node(self.bridge, 'B015-K1').append(ET.fromstring('<p xmlns="http://www.w3.org/1999/xhtml">6+7=13</p>'))
        with self.assertRaisesRegex(AssertionError, 'support equation'):
            validate_b015(self.target, self.bridge)

    def test_complete_chain_cannot_end_with_wrong_value(self):
        self.mutate(self.bridge, 'B015-K1', '8+7=15', '8+7=15=16')
        with self.assertRaises(AssertionError):
            validate_b015(self.target, self.bridge)

    def test_duplicate_bridge_id_rejected(self):
        self.node(self.bridge, 'B015-S-R04').set('id', 'B015-S-D04')
        with self.assertRaisesRegex(AssertionError, 'Duplicate'):
            validate_b015(self.target, self.bridge)


class _RenderedTables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.tables, self.labels = Counter(), {}, {}
        self.table = None; self.cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids[attrs['id']] += 1
        if tag == 'table':
            assert self.table is None
            self.table = attrs['id']; self.tables[self.table] = []
            self.labels[self.table] = attrs.get('aria-label')
        elif tag == 'tr' and self.table is not None:
            self.tables[self.table].append([])
        elif tag in {'th', 'td'} and self.table is not None:
            self.cell = [tag, attrs.get('scope'), []]
            self.tables[self.table][-1].append(self.cell)

    def handle_data(self, data):
        if self.cell is not None:
            self.cell[2].append(data)

    def handle_endtag(self, tag):
        if tag in {'th', 'td'}:
            self.cell = None
        elif tag == 'table':
            self.table = None


class ActualRendererTests(_ActualFixture):
    def rendered(self, english=False):
        from build_unit import render
        root = self.source if english else self.target
        parser = _RenderedTables()
        parser.feed(render(root, self.assets, 'en-' if english else '', english)); parser.close()
        return parser

    def test_all_ten_source_tables_actual_shapes_in_both_languages(self):
        for english in (False, True):
            with self.subTest(english=english):
                parsed = self.rendered(english); prefix = 'en-' if english else ''
                self.assertEqual({k: [len(r) for r in rows] for k, rows in parsed.tables.items()},
                                 {prefix + k: [cols] * rows for k, (_, rows, cols) in TABLES.items()})

    def test_addition_table_scoped_headers_and_100_rendered_answers(self):
        for english in (False, True):
            with self.subTest(english=english):
                parsed = self.rendered(english); key = ('en-' if english else '') + 'fs-id2300206'
                rows = parsed.tables[key]
                self.assertTrue(all(c[:2] == ['th', 'col'] for c in rows[0]))
                self.assertEqual([''.join(c[2]).strip() for c in rows[0]], ['+'] + list(map(str, range(10))))
                for a, row in enumerate(rows[1:]):
                    self.assertEqual(row[0][:2], ['th', 'row'])
                    self.assertEqual(''.join(row[0][2]).strip(), str(a))
                    for b, cell in enumerate(row[1:]):
                        self.assertEqual(cell[0], 'td')
                        self.assertEqual(''.join(cell[2]).strip(), str(a + b))
                self.assertIn('0', parsed.labels[key]); self.assertIn('9', parsed.labels[key])

    def test_all_163_ids_and_five_media_ids_survive_rendering(self):
        for english in (False, True):
            with self.subTest(english=english):
                parsed = self.rendered(english); prefix = 'en-' if english else ''
                self.assertEqual(set(parsed.ids), {prefix + i for i in ids_of(self.source)})
                self.assertTrue(all(n == 1 for n in parsed.ids.values()))
                self.assertTrue(all(parsed.ids[prefix + ident] == 1 for ident in MEDIA_IDS))

    def test_editorial_table_label_not_injected_into_frozen_target(self):
        for root in (self.source, self.target):
            table = self.node(root, 'fs-id2300206')
            self.assertNotIn('aria-label', table.attrib)
            self.assertNotIn('summary', table.attrib)
        self.assertTrue(self.rendered(False).labels['fs-id2300206'])

    def test_exact_table_link_labels_prefixes_and_unchanged_figure_fallback(self):
        from build_unit import render
        for english in (False, True):
            root = self.source if english else self.target
            prefix = 'en-' if english else ''
            cases = (
                ('fs-id2300206', 'Referenced table' if english else 'సంబంధిత పట్టిక'),
                ('CNX_BMath_Figure_01_02_001', 'Referenced figure' if english else 'సంబంధిత పటం'),
            )
            for ident, label in cases:
                with self.subTest(english=english, target=ident):
                    link = next(n for n in root.iter(CN + 'link') if n.get('target-id') == ident)
                    before = ET.tostring(link)
                    anchor = ET.fromstring(render(link, self.assets, prefix, english))
                    self.assertEqual(anchor.tag, 'a')
                    self.assertEqual(anchor.get('href'), '#' + prefix + ident)
                    self.assertEqual(''.join(anchor.itertext()), label)
                    self.assertEqual(ET.tostring(link), before)

    def test_registered_shape_corruption_rejected(self):
        from build_unit import render
        for ident, (declared, _, actual) in TABLES.items():
            if declared == actual:
                continue
            with self.subTest(table=ident):
                target = copy.deepcopy(self.target)
                self.node(target, ident).find(CN + 'tgroup').set('cols', '4')
                with self.assertRaises(AssertionError):
                    render(target, self.assets)

    def test_table_wrapper_id_cannot_silently_disappear(self):
        from build_unit import render
        self.node(self.target, 'eip-id1168288531101').find('.//' + CN + 'entry').set('id', 'must-remain')
        with self.assertRaisesRegex(AssertionError, 'ID would be discarded'):
            render(self.target, self.assets)

    def test_unregistered_no_label_table_not_generalized_from_addition_table(self):
        from build_unit import render
        table = copy.deepcopy(self.node(self.target, 'fs-id2300206'))
        table.set('id', 'unregistered-addition-table')
        with self.assertRaises(AssertionError):
            render(table, self.assets)


if __name__ == '__main__':
    unittest.main()
