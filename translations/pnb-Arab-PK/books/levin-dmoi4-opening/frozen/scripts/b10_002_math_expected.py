"""Handwritten finite B10-002 source mathematics fixtures.

Independent of b10_002_tex: no converter import or generated expected output.
Helpers assemble explicit mathematical descriptors from the source expressions.
"""
import re


def node(tag,text=None,children=(),attrs=None):return [tag,attrs or {},text,list(children)]
def row(*xs):return node('mrow',children=xs)
def ident(x):return node('mi',x)
def number(x):return node('mn',str(x))
def op(x):return node('mo',x)
def sup(base,arg):return node('msup',children=[base,arg])
def fence(left,items,right):
    attrs={'fence':'true','stretchy':'false'}
    return row(node('mo',left,attrs=attrs),*items,node('mo',right,attrs=attrs))
def par(*items):return fence('(',items,')')
def call(name,*args):return [ident(name),par(*args)]
def argument(x):return number(x) if isinstance(x,int) else ident(x)
def predicate(name,*args):
    values=[]
    for i,x in enumerate(args):
        if i:values.append(op(','))
        values.append(argument(x))
    return call(name,*values)
def quant(mark,x):return [op(mark),ident(x)]
def text(value):return node('mtext',value,attrs={'{http://www.w3.org/XML/1998/namespace}space':'preserve'})
def normalized(raw):
    return re.sub(r'\\text\{[^{}]*\}|\s+',lambda m:m.group() if m.group().startswith('\\text') else '',raw)


EXPECTED={}
def put(raw,tree):
    k=normalized(raw)
    if k in EXPECTED and EXPECTED[k]!=tree:raise AssertionError('Conflicting handwritten fixture')
    EXPECTED[k]=tree


for x in ['x','y','z','a','n','A','B','P','Q']:put(x,row(ident(x)))
for n in [5,10]:put(str(n),row(number(n)))
for command,glyph in [('therefore','∴'),('wedge','∧'),('vee','∨'),('imp','→'),('iff','↔'),('neg','¬'),('forall','∀'),('exists','∃'),('lt','<')]:
    put('\\'+command,row(op(glyph)))
put('[0,1]',row(fence('[',[number(0),op(','),number(1)],']')))
put('f(0)=-1',row(*predicate('f',0),op('='),op('−'),number(1)))
put('f(1)=5',row(*predicate('f',1),op('='),number(5)))
put('3+7=12',row(number(3),op('+'),number(7),op('='),number(12)))
put(r'1+3+5+7+\cdots+2n+1',row(number(1),op('+'),number(3),op('+'),number(5),op('+'),number(7),op('+'),op('⋯'),op('+'),number(2),ident('n'),op('+'),number(1)))
put('3+x=12',row(number(3),op('+'),ident('x'),op('='),number(12)))
put('x=9',row(ident('x'),op('='),number(9)))
put(r'P,Q,R,S,\ldots',row(ident('P'),op(','),ident('Q'),op(','),ident('R'),op(','),ident('S'),op(','),op('…')))
for command,glyph in [('wedge','∧'),('vee','∨'),('imp','→'),('iff','↔')]:
    put('P\\'+command+' Q',row(ident('P'),op(glyph),ident('Q')))
put(r'\neg P',row(op('¬'),ident('P')))
put(r'(P\vee Q)\wedge\neg(P\wedge Q)',row(par(ident('P'),op('∨'),ident('Q')),op('∧'),op('¬'),par(ident('P'),op('∧'),ident('Q'))))
put(r'P\imp(Q\wedge R)',row(ident('P'),op('→'),par(ident('Q'),op('∧'),ident('R'))))
for name,args in [('P',('x',)),('P',(7,)),('P',(8,)),('E',('x',)),('O',('x',)),('P',('a',)),('L',('y','x')),('M',('x',)),('H',('x',)),('C',('x',)),('S',('x',)),('R',('x',)),('P',('n',)),('P',('x','y')),('P',(15,)),('P',(11,)),('P',(1,)),('P',(13,)),('P',(4,)),('P',(1,3))]:
    put(name+'('+','.join(map(str,args))+')',row(*predicate(name,*args)))
for command,mark in [('forall','∀'),('exists','∃')]:
    put('\\'+command+' x P(x)',row(*quant(mark,'x'),*predicate('P','x')))
put(r'E(x)\vee O(x)',row(*predicate('E','x'),op('∨'),*predicate('O','x')))
put(r'\forall x(O(x)\vee E(x))',row(*quant('∀','x'),par(*predicate('O','x'),op('∨'),*predicate('E','x'))))
put(r'\forall x O(x)\vee\forall x E(x)',row(*quant('∀','x'),*predicate('O','x'),op('∨'),*quant('∀','x'),*predicate('E','x')))
put(r'\forall x\exists y(y\lt x)',row(*quant('∀','x'),*quant('∃','y'),par(ident('y'),op('<'),ident('x'))))
# Source \! is intentional but its portable visual effect is not yet reviewed.
put(r'\lt\!(y,x)',None)
put(r'0,1,2,\ldots',row(number(0),op(','),number(1),op(','),number(2),op(','),op('…')))
put('x-1',row(ident('x'),op('−'),number(1)))
put('x=0',row(ident('x'),op('='),number(0)))
put('y=-1',row(ident('y'),op('='),op('−'),number(1)))
put(r'\exists x\forall y(y\ge x)',row(*quant('∃','x'),*quant('∀','y'),par(ident('y'),op('≥'),ident('x'))))
put(r'\forall x(P(x)\imp Q(x))',row(*quant('∀','x'),par(*predicate('P','x'),op('→'),*predicate('Q','x'))))
put(r'\forall x(M(x)\imp H(x))',row(*quant('∀','x'),par(*predicate('M','x'),op('→'),*predicate('H','x'))))
put(r'\exists x(P(x)\wedge Q(x))',row(*quant('∃','x'),par(*predicate('P','x'),op('∧'),*predicate('Q','x'))))
put(r'\exists x(C(x)\wedge S(x))',row(*quant('∃','x'),par(*predicate('C','x'),op('∧'),*predicate('S','x'))))
put(r'S(x)\imp R(x)',row(*predicate('S','x'),op('→'),*predicate('R','x')))
put(r'\forall x(S(x)\imp R(x))',row(*quant('∀','x'),par(*predicate('S','x'),op('→'),*predicate('R','x'))))
put(r'x\gt3',row(ident('x'),op('>'),number(3)))
for raw,mark1,x,mark2,y in [
    (r'\exists x\forall y P(x,y)','∃','x','∀','y'),
    (r'\forall x\exists y P(x,y)','∀','x','∃','y'),
    (r'\forall y\exists x P(x,y)','∀','y','∃','x'),
    (r'\exists y\forall x P(x,y)','∃','y','∀','x'),
]:
    put(raw,row(*quant(mark1,x),*quant(mark2,y),*predicate('P','x','y')))
    put(raw+r'\text{.}',row(*quant(mark1,x),*quant(mark2,y),*predicate('P','x','y'),text('.')))
for raw,mark1,mark2 in [
    (r'\exists x\forall y\neg P(x,y)','∃','∀'),
    (r'\forall x\forall y\neg P(x,y)','∀','∀'),
    (r'\exists x\exists y\neg P(x,y)','∃','∃'),
    (r'\forall x\exists y\neg P(x,y)','∀','∃'),
]:
    put(raw,row(*quant(mark1,'x'),*quant(mark2,'y'),op('¬'),*predicate('P','x','y')))
put(r'x\lt y',row(ident('x'),op('<'),ident('y')))
put(r'\forall x',row(*quant('∀','x')))
put(r'\exists x',row(*quant('∃','x')))
# Intentionally incomplete canonical fragment, not an invented predicate.
put(r'\exists y\forall x',row(*quant('∃','y'),*quant('∀','x')))
for coefficient in [17,18,16,9]:
    put(str(coefficient)+'x+1',row(number(coefficient),ident('x'),op('+'),number(1)))
put(r'17\cdot15+1=256',row(number(17),op('⋅'),number(15),op('+'),number(1),op('='),number(256)))
put(r'18\cdot15+1=271',row(number(18),op('⋅'),number(15),op('+'),number(1),op('='),number(271)))
put(r'\exists x P(x,y)\imp\forall x P(x,y)',row(*quant('∃','x'),*predicate('P','x','y'),op('→'),*quant('∀','x'),*predicate('P','x','y')))
put(r'\neg(P\wedge Q)\imp Q',row(op('¬'),par(ident('P'),op('∧'),ident('Q')),op('→'),ident('Q')))
put(r'P\imp\neg Q',row(ident('P'),op('→'),op('¬'),ident('Q')))
put(r'\neg\exists x(E(x)\wedge O(x))',row(op('¬'),*quant('∃','x'),par(*predicate('E','x'),op('∧'),*predicate('O','x'))))
put(r'\forall x(E(x)\imp O(x+1))',row(*quant('∀','x'),par(*predicate('E','x'),op('→'),*call('O',ident('x'),op('+'),number(1)))))
put(r'\exists x(P(x)\wedge E(x))',row(*quant('∃','x'),par(*predicate('P','x'),op('∧'),*predicate('E','x'))))
put(r'\forall x\forall y\exists z(x\lt z\lt y\vee y\lt z\lt x)',row(*quant('∀','x'),*quant('∀','y'),*quant('∃','z'),par(ident('x'),op('<'),ident('z'),op('<'),ident('y'),op('∨'),ident('y'),op('<'),ident('z'),op('<'),ident('x'))))
put(r'\forall x\neg\exists y(x\lt y\lt x+1)',row(*quant('∀','x'),op('¬'),*quant('∃','y'),par(ident('x'),op('<'),ident('y'),op('<'),ident('x'),op('+'),number(1))))
put(r'\forall x\exists y(y^2=x)',row(*quant('∀','x'),*quant('∃','y'),par(sup(ident('y'),number(2)),op('='),ident('x'))))
put(r'\forall x\forall y(x\lt y\imp\exists z(x\lt z\lt y))',row(*quant('∀','x'),*quant('∀','y'),par(ident('x'),op('<'),ident('y'),op('→'),*quant('∃','z'),par(ident('x'),op('<'),ident('z'),op('<'),ident('y')))))
put(r'\exists x\forall y\forall z(y\lt z\imp y\le x\le z)',row(*quant('∃','x'),*quant('∀','y'),*quant('∀','z'),par(ident('y'),op('<'),ident('z'),op('→'),ident('y'),op('≤'),ident('x'),op('≤'),ident('z'))))
put('4+1',row(number(4),op('+'),number(1)))
put(r'2\cdot4',row(number(2),op('⋅'),number(4)))
for n in [11,13]:put('P('+str(n)+r')\text{?}',row(*predicate('P',n),text('?')))
for value in ['False','True','Choice 1','Choice 2','Choice 3']:put(r'\text{'+value+'}',row(text(value)))
put(r'16\cdot11+1',row(number(16),op('⋅'),number(11),op('+'),number(1)))
put(r'9\cdot13+1',row(number(9),op('⋅'),number(13),op('+'),number(1)))


def expected(raw):
    k=normalized(raw)
    if k not in EXPECTED:raise ValueError('No handwritten B10-002 fixture for '+repr(raw))
    return EXPECTED[k]

