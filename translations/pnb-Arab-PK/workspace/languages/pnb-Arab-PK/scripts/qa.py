"""Structural, Unicode, mathematical and deterministic-build regression checks."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import copy
import ast

BASE = Path(__file__).resolve().parents[1]
MATH = "http://www.w3.org/1998/Math/MathML"
reader = BASE / "reader/unit-001.html"
unit_translations = [BASE / 'translations' / name for name in (
    'unit-001.json', 'bridge-before.html', 'bridge-after.html',
)]
# Explicit ownership keeps a concurrently drafted unit out of this receipt.
unit_files = [
    *unit_translations,
    BASE / 'styles/reader.css',
    BASE / 'source-excerpts/m49301-opening.cnxml',
    BASE / 'source-excerpts/manifest.json',
    reader,
    BASE / 'terminology.tsv',
    BASE / 'scripts/build.py',
    BASE / 'scripts/qa.py',
]
subprocess.run([sys.executable, str(BASE / "scripts/build.py")], check=True)
first = reader.read_bytes()
subprocess.run([sys.executable, str(BASE / "scripts/build.py")], check=True)
assert first == reader.read_bytes(), "Nondeterministic reader"
text = first.decode("utf-8")
html = ET.fromstring(text[text.index('<html'):])
source = ET.parse(BASE / "source-excerpts/m49301-opening.cnxml").getroot()
manifest = json.loads((BASE / "source-excerpts/manifest.json").read_text(encoding="utf-8"))
checks = []

def check(name, condition):
    assert condition, name
    checks.append(name)

check("exact_locale_and_rtl", html.get("lang") == "pnb-Arab-PK" and html.get("dir") == "rtl")
excerpt_bytes = (BASE / "source-excerpts/m49301-opening.cnxml").read_bytes().replace(b"\r\n", b"\n")
check("frozen_excerpt_logical_lf_hash_matches_manifest", hashlib.sha256(excerpt_bytes).hexdigest() == manifest["excerpt_sha256"])
for path in unit_files:
    data = path.read_text(encoding="utf-8")
    check(f"unicode_clean:{path.name}", not re.search('[\u0a00-\u0a7f\ufffd\u202a-\u202e\u2066-\u2069]', data))
check("no_unresolved_placeholders", '{{math:' not in text and 'TODO' not in text)
ids = [e.get('id') for e in html.iter() if e.get('id')]
check("unique_html_ids", len(ids) == len(set(ids)))
source_ids = [e.get('id') for e in source.iter() if e.get('id')][1:]
check("all_source_ids_retained", set(source_ids).issubset(ids))
links = [e.get('href') for e in html.iter('a')]
check("all_fragment_links_resolve", all(h[1:] in ids for h in links if h.startswith('#')))
check("all_local_links_resolve", all((reader.parent / h).exists() for h in links if not h.startswith(('#', 'https://'))))

def signature(node):
    return [node.tag, sorted((k, v) for k, v in node.attrib.items() if k not in ('dir','data-source-punctuation')), (node.text or '').strip(), [(signature(c), (c.tail or '').strip()) for c in node]]

def localized_math(node):
    node=copy.deepcopy(node)
    last=node
    while len(last): last=last[-1]
    punctuation=''
    if last.tag == '{'+MATH+'}mo' and last.text in ('.',','):
        parents={c:p for p in node.iter() for c in p}
        punctuation=last.text
        parents[last].remove(last)
    return node,punctuation

source_math = list(source.iter('{' + MATH + '}math'))
target_math = list(html.iter('{' + MATH + '}math'))
check("mathematical_tree_and_order_unchanged_except_logged_sentence_punctuation", [signature(localized_math(m)[0]) for m in source_math] == [signature(m) for m in target_math])
check("sentence_punctuation_migration_explicit", [localized_math(m)[1] for m in source_math] == [m.get('data-source-punctuation','') for m in target_math])
check("all_source_math_ltr", all(m.get('dir') == 'ltr' for m in target_math))
parents = {c:p for p in html.iter() for c in p}
check("all_source_math_isolated", all(parents[m].get('class') == 'math-isolate' and parents[m].get('dir') == 'ltr' for m in target_math))
check("figure_exists", (BASE / "assets/Figure_01_01_001.jpg").is_file())
check("figure_alt_present", all(len(e.get('alt', '')) > 20 for e in html.iter('img')))
check("decimal_numbering_retained", 'list-style-type:decimal' in text)
check("bilingual_languages_labeled", any(e.get('lang') == 'ur-Arab-PK' for e in html.iter()) and any(e.get('lang') == 'en' for e in html.iter()))
check("source_example_boundary_not_overclaimed", 'پورے حصے دا ترجمہ نہیں' in text)

# These are the actual ordered-pair data used in the source and bridge exercises.
def function(pairs):
    inputs = {}
    for x, y in pairs:
        if x in inputs and inputs[x] != y:
            return False
        inputs[x] = y
    return True

doubles = [(x, 2*x) for x in range(1, 6)]
check("doubling_and_reversed_relation_are_functions", function(doubles) and function([(y,x) for x,y in doubles]))
check("many_inputs_one_output_is_function", function([(1,4),(2,4),(3,7)]))
check("same_input_two_outputs_not_function", not function([(1,2),(1,3),(2,4)]))
check("duplicate_identical_pair_does_not_change_function", function([(1,2),(1,2)]))
for x, expected in [(4,11),(-2,-1),(0,3),(5,13)]:
    check(f"evaluation_f({x})", 2*x+3 == expected)
for witness in ['f(4) = 11', 'f(−2) = 2 × (−2) + 3 = −1', 'f(0) = 3', 'f(5) = 13', '{1, 2, 3}', '{4, 7}']:
    check(f"answer_visible:{witness}", witness in text)

def formula_elements(node):
    return [e for e in node.iter('bdi') if 'formula' in e.get('class', '').split()]


def validate_displayed_practice(document, source_pairs):
    """Validate one in-memory reader without building files or changing receipts."""
    passed = []

    def require(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    def formulas(node):
        return [''.join(e.itertext()) for e in formula_elements(node)]

    def integers(pattern, value):
        match = re.fullmatch(pattern, value)
        if match is None:
            raise AssertionError(f'unrecognized_displayed_formula:{value}')
        return tuple(map(int, match.groups()))

    practice = document.find(".//section[@id='bridge-practice']")
    if practice is None:
        raise AssertionError('practice_section_present')
    lists = practice.findall('ol')
    if len(lists) != 2:
        raise AssertionError('question_and_answer_lists_present')
    questions, answers = [e.findall('li') for e in lists]
    require('four_questions_and_four_answers', len(questions) == len(answers) == 4)
    rule, *input_labels = formulas(questions[0])
    coefficient, constant = integers(r'f\(x\) = (-?\d+)x \+ (-?\d+)', rule)
    evaluations = [integers(r'f\((-?\d+)\) = (-?\d+)', value) for value in formulas(answers[0])]
    requested_inputs = [integers(r'f\((-?\d+)\)', value)[0] for value in input_labels]
    require('displayed_evaluations_answer_requested_inputs', requested_inputs == [x for x,y in evaluations])
    require('displayed_evaluations_match_displayed_rule', all(coefficient*x+constant == y for x,y in evaluations))
    pairs = ast.literal_eval(formulas(questions[1])[0])
    domain, output_range = map(ast.literal_eval, formulas(answers[1]))
    require('displayed_domain_range_match_displayed_relation', domain == {x for x,y in pairs} and output_range == {y for x,y in pairs})
    require('displayed_relation_is_function', function(pairs))
    nonfunction = ast.literal_eval(formulas(questions[2])[0])
    require('displayed_nonfunction_really_has_multiple_outputs', not function(nonfunction))
    reversed_pairs, reversed_domain = map(ast.literal_eval, formulas(answers[3]))
    require('displayed_reverse_is_source_relation_reversed', reversed_pairs == {(y,x) for x,y in source_pairs})
    require('displayed_reverse_domain_and_function_claim', reversed_domain == {x for x,y in reversed_pairs} and function(reversed_pairs))
    return passed


# Bind answer checks to displayed operands; reuse the same validator for mutants.
source_pairs = ast.literal_eval(''.join(source_math[0].itertext()).strip())
for name in validate_displayed_practice(html, source_pairs):
    check(name, True)


def reject_practice_mutation(name, list_index, item_index, formula_index, old, new, expected_failure):
    """Mutate a detached DOM only; require the intended mathematical check to fail."""
    mutant = copy.deepcopy(html)
    practice = mutant.find(".//section[@id='bridge-practice']")
    item = practice.findall('ol')[list_index].findall('li')[item_index]
    formula = formula_elements(item)[formula_index]
    original = ''.join(formula.itertext())
    assert original.count(old) == 1, f'Mutation fixture drifted: {name}'
    formula[:] = []
    formula.text = original.replace(old, new, 1)
    try:
        validate_displayed_practice(mutant, source_pairs)
    except AssertionError as error:
        check(name, str(error) == expected_failure)
    else:
        check(name, False)


reject_practice_mutation('mutation_changed_question2_operand_rejected', 0, 1, 0,
    '(3, 7)', '(3, 8)', 'displayed_domain_range_match_displayed_relation')
reject_practice_mutation('mutation_changed_rule_rejected', 0, 0, 0,
    '2x + 3', '2x + 4', 'displayed_evaluations_match_displayed_rule')
reject_practice_mutation('mutation_changed_evaluation_answer_rejected', 1, 0, 0,
    'f(0) = 3', 'f(0) = 4', 'displayed_evaluations_match_displayed_rule')
reject_practice_mutation('mutation_changed_reversed_relation_rejected', 1, 3, 0,
    '(2, 1)', '(2, 9)', 'displayed_reverse_is_source_relation_reversed')
reject_practice_mutation('mutation_changed_reversed_domain_rejected', 1, 3, 1,
    '{2, 4, 6, 8, 10}', '{2, 4, 6, 8, 11}', 'displayed_reverse_domain_and_function_claim')

hashes = {}
for p in unit_files:
    hashes[str(p.relative_to(BASE))] = hashlib.sha256(p.read_bytes()).hexdigest()
receipt = {"unit": "PNB-001", "status": "structural_pass_linguistic_review_pending", "translated_blocks": 19, "source_math_count": len(source_math), "source_ids_preserved": len(source_ids), "original_practice_questions": 4, "checks": checks, "hashes": hashes, "limitations": ["No native-speaker or educator approval claimed", "Not a whole m49301 module", "Font stack uses locally installed fonts; cross-machine raster identity not claimed", "PDF/TeX source books not rebuilt; pilot HTML is the checked build", "Browser visual receipt is separate"]}
(BASE / "qa").mkdir(exist_ok=True)
(BASE / "qa/structural.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f"PASS: {len(checks)} checks; {len(source_math)} verified mathematical trees; {len(source_ids)} retained IDs")
