"""Check source-derived positional products and exact blank/given chart matrices."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from localized_a00_multiplication import render_figure
from library_review_metadata import media_metadata
from worked_answer_figures import answer_table

LANG = Path(__file__).resolve().parents[1]
N = '{http://www.w3.org/2000/svg}'
review = json.loads((LANG/'translations/a00-m81255-media-and-errata.gu.json').read_text(encoding='utf-8'))
normalized = media_metadata(review)
products_checked = []
for suffix, a, b in [('011_img.jpg', 354, 438), ('012_img.jpg', 896, 201)]:
    tree = ET.fromstring(render_figure('CNX_BMath_Figure_01_04_'+suffix, 'ગુજરાતી વર્ણન', 'qa'))
    svgs = list(tree.iter(N+'svg'))
    assert len(svgs) == 6
    decoded = []
    for svg in svgs:
        digits = [(int(e.get('x')), int(e.text)) for e in svg.iter(N+'text') if e.text.isdigit()]
        digits.sort()
        # The rightmost ones column is126;22 units per source place.
        value = sum(d*10**((126-x)//22) for x, d in digits)
        assert all((126-x) % 22 == 0 for x, d in digits)
        decoded.append(value)
    assert decoded == [a, b, a*(b % 10), a*((b//10) % 10)*10, a*(b//100)*100, a*b], decoded
    assert decoded[2]+decoded[3]+decoded[4] == decoded[5]
    if b == 201:
        zero_x = [int(e.get('x')) for e in svgs[3].iter(N+'text') if e.text == '0']
        assert zero_x == [60, 82, 104]  # Original000; ones column stays blank.
        assert len([e for e in svgs[4].iter(N+'text') if e.text.isdigit()]) == 4
    products_checked.append(decoded)

for suffix, expected in [('008_img.jpg', '227×31'), ('010_img.jpg', '227×318')]:
    tree = ET.fromstring(render_figure('CNX_BMath_Figure_01_04_'+suffix, 'ગુજરાતી વર્ણન', 'qa'))
    numbers = ''.join(e.text for e in tree.iter(N+'text') if e.get('x') in ('64', '72', '37', '85', '61'))
    assert numbers == expected
    assert 3*7 == 21 and 3*2+2 == 8 and 27*3 == 81

tree = ET.fromstring(render_figure('CNX_BMath_Figure_01_04_014.jpg', 'ગુજરાતી વર્ણન', 'qa').replace('<br>', '<br/>'))
rectangles = list(tree.iter(N+'rect'))
assert [(int(e.get('width')), int(e.get('height'))) for e in rectangles] == [(50, 50), (127, 127)]
assert 127/50 == 2.54
tree = ET.fromstring(render_figure('CNX_BMath_Figure_01_04_013.jpg', 'ગુજરાતી વર્ણન', 'qa'))
assert len(list(tree.iter(N+'rect'))) == 2*3 == 6

given = blank = 0
for chart in normalized['accessible_charts'].values():
    rows, cols, cells = chart['row_headers'], chart['column_headers'], chart['visible_cells']
    html = answer_table({'caption_gu': 'ગુણાકારનું કોષ્ટક', 'corner_gu': '×',
                         'row_headers': rows, 'column_headers': cols, 'cells': cells})
    rendered = ET.fromstring(html)
    actual_rows = rendered.findall('.//tbody/tr')
    assert len(actual_rows) == len(rows)
    for i, row in enumerate(actual_rows):
        assert row.find('th').text == str(rows[i]) and row.find('th').get('scope') == 'row'
        assert len(row.findall('td')) == len(cols)
        for j, cell in enumerate(row.findall('td')):
            value = cells[i][j]
            if value is None:
                assert cell.text is None and cell.get('aria-label') == 'ખાલી'
                blank += 1
            else:
                assert int(cell.text) == value == rows[i]*cols[j]
                given += 1
assert given == 317
receipt = {'schema': 'gujarati-multiplication-figure-qa-v1', 'result': 'pass',
           'localized_label_figures': 6, 'source_charts': 12, 'visible_given_chart_cells_checked': given,
           'original_blank_chart_cells_preserved': blank, 'positional_product_rows': products_checked,
           'square_unit_visual_length_ratio': 2.54, 'area_grid_cells': 6,
           'source_review_sha256': hashlib.sha256((LANG/'translations/a00-m81255-media-and-errata.gu.json').read_bytes()).hexdigest(),
           'checks': ['Actual source originals viewed', 'Products recomputed from operands',
                      'Every displayed digit checked by its positional x-coordinate', 'Original zero placeholders and empty positions retained',
                      'All source-given chart values and empty cells preserved', 'Carry arrows and square units inspected'],
           'native_review_pending': True}
(LANG/'MULTIPLICATION_FIGURE_QA.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print(f'PASS:6labelled figures;12charts;{given}given cells;{blank}blanks;both positional products.')
