"""Small Gujarati SVG redraws with exact source values; no raster editing."""
from html import escape
from localized_place_value import render_figure as place_value_figure
from localized_a10_whole_numbers import render_figure as a10_figure
from localized_a00_addition import render_figure as addition_figure
from localized_front_matter import render_figure as front_figure
from localized_a10_algebra import render_figure as algebra_figure
from localized_a00_subtraction import render_figure as subtraction_figure
from localized_a00_multiplication import render_figure as multiplication_figure
from localized_a00_division import render_figure as division_figure
from localized_a00_algebra_intro import render_figure as algebra_intro_figure
from localized_a10_integers import render_figure as integers_figure
from localized_a10_integer_products import render_figure as integer_products_figure
from localized_a00_algebra_language import render_figure as a00_algebra_figure
from localized_a10_fractions import render_figure as a10_fraction_figure
from localized_a00_expression_evaluation import render_figure as expression_evaluation_figure
from localized_a10_fraction_operations import render_figure as fraction_operations_figure
from localized_a00_equation_properties import render_figure as equation_properties_figure
from localized_a10_decimals import render_figure as decimal_figure
from localized_a00_factors import render_figure as factor_figure
from localized_a00_prime_lcm import render_figure as prime_lcm_figure
from localized_a00_integer_intro import render_figure as integer_intro_figure


def label(x, y, value, size=18):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{escape(str(value))}</text>'


def square(x, y, width=8):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{width}" fill="#dbece8" stroke="#244d50" stroke-width="0.6"/>'


def hundred(x, y):
    return ''.join(square(x+col*8, y+row*8) for row in range(10) for col in range(10))


def rod(x, y):
    return ''.join(square(x+col*8, y) for col in range(10))


def blocks(hundreds, tens, ones, with_labels=False):
    content = ''.join(hundred(25+i*90, 30) for i in range(hundreds))
    content += ''.join(rod(300, 30+i*14) for i in range(tens))
    content += ''.join(square(490+(i%5)*15, 30+(i//5)*15) for i in range(ones))
    if with_labels:
        content += label(125, 150, f'{hundreds} સો') + label(340, 150, f'{tens} દશક') + label(520, 150, f'{ones} એકમ')
    return content, 180


def expanded(total, currency=False):
    h, t, o = total//100, total//10%10, total%10
    sign = '$' if currency else ''
    x = [120, 320, 520]
    values = [h*100, t*10, o]
    content = ''.join(f'<text x="{xi}" y="40" font-size="28" text-anchor="middle">{sign}<tspan fill="#a72f19">{str(v)[0]}</tspan>{str(v)[1:]}</text>' for xi,v in zip(x,values))
    content += label(220,40,'+',26)+label(420,40,'+',26)
    content += ''.join(f'<path d="M {xi} 57 L {xi} 85" stroke="#244d50" marker-end="url(#ARROW)"/>' for xi in x)
    content += ''.join(label(xi,115,str(v),24) for xi,v in zip(x,[h,t,o]))
    content += label(320,158,sign+str(total),28)
    return content, 185


def money():
    content = ''
    for i,(count,value) in enumerate([(3,100),(7,10),(4,1)]):
        x=30+i*205
        for j in range(count):
            content += f'<rect x="{x+j*3}" y="{24+j*4}" width="130" height="48" rx="3" fill="#ecf6f3" stroke="#244d50"/>'
        content += label(x+65+(count-1)*3,56+(count-1)*4,'$'+str(value),23)
        content += label(x+75,132,f'{count} × ${value} = ${count*value}',19)
    return content, 160


def basic_blocks():
    content = square(65,90)+rod(235,90)+hundred(465,20)
    content += label(70,140,'1 ખંડ = 1')+label(275,140,'1 સળી = 10')+label(505,140,'1 ચોરસ = 100')
    return content, 170


def localized_svg(filename, alt, unique_id):
    factories = {
        'CNX_BMath_Figure_01_01_002.jpg': money,
        'CNX_BMath_Figure_01_01_003_img.jpg': lambda: expanded(374, True),
        'CNX_BMath_Figure_01_01_004.jpg': basic_blocks,
        'CNX_BMath_Figure_01_01_005.jpg': lambda: blocks(1,3,8,True),
        'CNX_BMath_Figure_01_01_006_img.jpg': lambda: expanded(138),
        'CNX_BMath_Figure_01_01_007_img.jpg': lambda: blocks(2,1,5),
        'CNX_BMath_Figure_01_01_008_img.jpg': lambda: expanded(215),
        'CNX_BMath_Figure_01_01_009_img.jpg': lambda: blocks(1,7,6),
        'CNX_BMath_Figure_01_01_010_img.jpg': lambda: blocks(2,3,7),
    }
    if filename not in factories:
        return front_figure(filename, alt, unique_id) or addition_figure(filename, alt, unique_id) or subtraction_figure(filename, alt, unique_id) or multiplication_figure(filename, alt, unique_id) or division_figure(filename, alt, unique_id) or algebra_intro_figure(filename, alt, unique_id) or integer_intro_figure(filename, alt, unique_id) or integers_figure(filename, alt, unique_id) or integer_products_figure(filename, alt, unique_id) or a00_algebra_figure(filename, alt, unique_id) or a10_fraction_figure(filename, alt, unique_id) or expression_evaluation_figure(filename, alt, unique_id) or fraction_operations_figure(filename, alt, unique_id) or equation_properties_figure(filename, alt, unique_id) or decimal_figure(filename, alt, unique_id) or factor_figure(filename, alt, unique_id) or prime_lcm_figure(filename, alt, unique_id) or algebra_figure(filename, alt, unique_id) or a10_figure(filename, alt, unique_id) or place_value_figure(filename, alt, unique_id)
    content, height = factories[filename]()
    content = content.replace('url(#ARROW)', f'url(#{unique_id}-arrow)')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" class="localized-figure" viewBox="0 0 640 {height}" role="img" aria-labelledby="{unique_id}-title {unique_id}-desc"><title id="{unique_id}-title">સ્થાનકિંમતનું નમૂનું</title><desc id="{unique_id}-desc">{escape(alt)}</desc><defs><marker id="{unique_id}-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#244d50"/></marker></defs><g font-family="Gujarati, Nirmala UI, sans-serif" fill="#182c35">{content}</g></svg>'''
