"""Handwritten mathematical-source fixtures, independent of b10_001_tex.

No converter imports or generated expected output. Helpers only assemble explicit
MathML-shaped descriptors for the source's finite formula inventory.
"""
import re


def node(tag,text=None,children=(),attrs=None):return [tag,attrs or {},text,list(children)]
def row(*xs):return node('mrow',children=xs)
def ident(x):return node('mi',x)
def number(x):return node('mn',str(x))
def op(x):return node('mo',x)
def sub(base,arg):return node('msub',children=[base,arg])
def sup(base,arg):return node('msup',children=[base,arg])
def fraction(top,bottom):return node('mfrac',children=[top,bottom])
def fence(left,items,right):
    attrs={'fence':'true','stretchy':'false'}
    return row(node('mo',left,attrs=attrs),*items,node('mo',right,attrs=attrs))
def commas(items):
    out=[]
    for i,item in enumerate(items):
        if i:out.append(op(','))
        out.extend(item if isinstance(item,tuple) else [item])
    return out
def numeric_items(*values):return [op('…') if x=='...' else number(x) for x in values]
def aset(*values):return fence('{',commas(numeric_items(*values)),'}')
def tuple_numbers(*values):return fence('(',commas(numeric_items(*values)),')')
def call(name,*args):return [ident(name),fence('(',list(args),')')]
def natural():return node('mi','ℕ',attrs={'mathvariant':'normal'})
def normalized(s):return re.sub(r'\s+','',s)

EXPECTED={}
def put(source,value):
    k=normalized(source)
    if k in EXPECTED and EXPECTED[k]!=value:raise AssertionError('Conflicting handwritten fixture')
    EXPECTED[k]=value

for value in ['1','2','3','6']:put(value,row(number(value)))
for value in ['n','A','f','X','Y','a','b']:put(value,row(ident(value)))
put(r'\N',row(natural()))
put(r'\in',row(op('∈')))
put(r'\st',row(op(':')))
put(r'[0,\infty)',row(fence('[',[number(0),op(','),op('∞')],')')))
put('f(x) = x^2',row(*call('f',ident('x')),op('='),sup(ident('x'),number(2))))
put(r'\{0,1,2,3,4\}',row(aset(0,1,2,3,4)))
for values in [(1,2),(1,3),(2,3),(2,1),(3,1),(3,2),(2,4),(3,6),(7,3),(1,2,3),(2,3,1),(3,4,5),(4,5,6),(1,0),(1,1)]:
    put('('+','.join(map(str,values))+')',row(tuple_numbers(*values)))
for values in [(1,2,3,4),(2,4,1,3),(1,2,3),(2,3,1),(1,6),(2,5),(3,4)]:
    put(r'\{'+','.join(map(str,values))+r'\}',row(aset(*values)))
put(r'A=\{3,5,7\}',row(ident('A'),op('='),aset(3,5,7)))
put(r'A=\{x\in\N\st x\lt10\}',row(ident('A'),op('='),fence('{',[ident('x'),op('∈'),natural(),op(':'),ident('x'),op('<'),number(10)],'}')))
put(r'\N=\{0,1,2,3,\ldots\}',row(natural(),op('='),aset(0,1,2,3,'...')))
put(r'\{1,2,1+1,1+2,2+2\}',row(fence('{',commas([number(1),number(2),(number(1),op('+'),number(1)),(number(1),op('+'),number(2)),(number(2),op('+'),number(2))]),'}')))
put(r'\{x\in\N\st x\lt5\text{ and }x\ge1\}',row(fence('{',[ident('x'),op('∈'),natural(),op(':'),ident('x'),op('<'),number(5),node('mtext',' and ',attrs={'{http://www.w3.org/XML/1998/namespace}space':'preserve'}),ident('x'),op('≥'),number(1)],'}')))
put(r'f:X\to Y',row(ident('f'),op(':'),ident('X'),op('→'),ident('Y')))
put(r'f:\{1,2,3\}\to\{2,4,6\}',row(ident('f'),op(':'),aset(1,2,3),op('→'),aset(2,4,6)))
put('f(x)=2x',row(*call('f',ident('x')),op('='),number(2),ident('x')))
put(r'\{(1,2),(2,4),(3,6)\}',row(fence('{',commas([tuple_numbers(1,2),tuple_numbers(2,4),tuple_numbers(3,6)]),'}')))
put('f(n)=3n+1',row(*call('f',ident('n')),op('='),number(3),ident('n'),op('+'),number(1)))
for value in [5,4,3,2]:put('f('+str(value)+')',row(*call('f',number(value))))
put(r'f(n)=2\cdot f(n-1)',row(*call('f',ident('n')),op('='),number(2),op('⋅'),*call('f',ident('n'),op('−'),number(1))))
put('f(0)=3',row(*call('f',number(0)),op('='),number(3)))
put(r'f(1)=2\cdot3=6',row(*call('f',number(1)),op('='),number(2),op('⋅'),number(3),op('='),number(6)))
put(r'f(2)=2\cdot6=12',row(*call('f',number(2)),op('='),number(2),op('⋅'),number(6),op('='),number(12)))
put(r'(4,8,12,\ldots)',row(tuple_numbers(4,8,12,'...')))
put(r'a_0,a_1,a_2,\ldots',row(*commas([sub(ident('a'),number(0)),sub(ident('a'),number(1)),sub(ident('a'),number(2)),op('…')])))
put(r'(a_n)_{n\ge0}',row(sub(fence('(',[sub(ident('a'),ident('n'))],')'),row(ident('n'),op('≥'),number(0)))))
put(r'(a_n)_{n\in\N}',row(sub(fence('(',[sub(ident('a'),ident('n'))],')'),row(ident('n'),op('∈'),natural()))))
put(r'(f_n)_{n\ge1}',row(sub(fence('(',[sub(ident('f'),ident('n'))],')'),row(ident('n'),op('≥'),number(1)))))
put(r'1,1,2,3,5,8,\ldots',row(*commas(numeric_items(1,1,2,3,5,8,'...'))))
put('f_4=3',row(sub(ident('f'),number(4)),op('='),number(3)))
put('f(4)=3',row(*call('f',number(4)),op('='),number(3)))
put('a_n',row(sub(ident('a'),ident('n'))))
put(r'a_n=\frac{n(n+1)}{2}',row(sub(ident('a'),ident('n')),op('='),fraction(row(ident('n'),fence('(',[ident('n'),op('+'),number(1)],')')),row(number(2)))))
put('f_n=f_{n-1}+f_{n-2};f_1=1,f_2=1',row(sub(ident('f'),ident('n')),op('='),sub(ident('f'),row(ident('n'),op('−'),number(1))),op('+'),sub(ident('f'),row(ident('n'),op('−'),number(2))),op(';'),sub(ident('f'),number(1)),op('='),number(1),op(','),sub(ident('f'),number(2)),op('='),number(1)))
put(r'2\lt6',row(number(2),op('<'),number(6)))
put('3^2+4^2=5^2',row(sup(number(3),number(2)),op('+'),sup(number(4),number(2)),op('='),sup(number(5),number(2))))
put(r'4^2+5^2\ne6^2',row(sup(number(4),number(2)),op('+'),sup(number(5),number(2)),op('≠'),sup(number(6),number(2))))
put('(a,b)',row(fence('(',[ident('a'),op(','),ident('b')],')')))
for left,right in [('a','b'),('b','a'),('b','c'),('a','c')]:put(left+r'\lt'+right,row(ident(left),op('<'),ident(right)))
put(r'V=\{1,2,3,4,5,6\}',row(ident('V'),op('='),aset(1,2,3,4,5,6)))


def expected(raw):
    k=normalized(raw)
    if k not in EXPECTED:raise ValueError('No handwritten source fixture for '+repr(raw))
    return EXPECTED[k]
