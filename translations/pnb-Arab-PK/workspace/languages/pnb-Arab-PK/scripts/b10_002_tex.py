"""Strict offline presentation mapper for the observed B10-002 TeX subset.

No TeX/PG/Perl engine or upstream code execution. Unknown syntax fails closed.
The sole unreviewed negative-thin-space form remains exact visible source TeX.
"""
from dataclasses import dataclass, field
import hashlib
import html
import json
import re
from lxml import etree as E

MATH='http://www.w3.org/1998/Math/MathML'
XML='http://www.w3.org/XML/1998/namespace'
SYMBOLS={'therefore':'∴','cdot':'⋅','cdots':'⋯','ldots':'…','wedge':'∧',
         'vee':'∨','imp':'→','iff':'↔','neg':'¬','forall':'∀','exists':'∃',
         'ge':'≥','gt':'>','le':'≤','lt':'<'}
TEXT_PAYLOADS={'?','.','False','True','Choice 1','Choice 2','Choice 3'}
FALLBACK_RAW=r'\lt\!(y,x)'
FALLBACK_REASON='Source negative thin spacing is retained as raw TeX pending a reviewed portable presentation; no spacing token is dropped.'
FALLBACK_STANDARD='https://www.w3.org/TR/mathml-core/#space-mspace'


class TexError(ValueError):
    pass


@dataclass
class Node:
    tag:str
    text:str|None=None
    attrs:dict=field(default_factory=dict)
    children:list=field(default_factory=list)
    tokens:list=field(default_factory=list)

    def descriptor(self):
        return [self.tag,self.attrs,self.text,[c.descriptor() for c in self.children]]


def tokenize(raw):
    pattern=re.compile(r'\s+|\\[A-Za-z]+|\\!|[0-9]+|[A-Za-z]|[{}()\[\]^_=+,;:\-?.]')
    tokens=[];pos=0
    while pos<len(raw):
        match=pattern.match(raw,pos)
        if not match:raise TexError('Unsupported character at '+str(pos))
        value=match.group()
        kind='space' if value.isspace() else 'command' if value.startswith('\\') else 'number' if value.isdigit() else 'variable' if value.isalpha() else 'syntax'
        if kind=='command' and value[1:] not in set(SYMBOLS)|{'text','!'}:
            raise TexError('Unknown command '+value)
        tokens.append(dict(start=pos,end=match.end(),raw=value,kind=kind,effect=None,mathml_paths=[]))
        pos=match.end()
    if not tokens:raise TexError('Empty source formula')
    return tokens


class Parser:
    def __init__(self,raw):
        self.raw=raw;self.tokens=tokenize(raw);self.pos=0
        self.order=[i for i,t in enumerate(self.tokens) if t['kind']!='space']
        for t in self.tokens:
            if t['kind']=='space':t['effect']='TeX presentation whitespace; exact raw retained'

    def peek(self):
        return self.tokens[self.order[self.pos]]['raw'] if self.pos<len(self.order) else None

    def take(self,value=None,effect=None):
        if self.peek() is None or (value is not None and self.peek()!=value):
            raise TexError('Expected '+repr(value)+', got '+repr(self.peek()))
        i=self.order[self.pos];self.pos+=1
        if effect:self.tokens[i]['effect']=effect
        return i

    def group(self):
        left=self.take('{','nonprinting source group boundary')
        inside=self.sequence({'}'});right=self.take('}','nonprinting source group boundary')
        if not inside.children:raise TexError('Empty source group')
        inside.tokens.extend([left,right]);return inside

    def sequence(self,stops=frozenset()):
        children=[]
        while self.peek() is not None and self.peek() not in stops:
            if self.peek() in {'}',')',']'}:raise TexError('Unmatched closing fence')
            atom=self.atom()
            if self.peek()=='^':
                mark=self.take('^','whole preceding atom superscript binding')
                if self.peek()=='{':arg=self.group()
                elif self.peek() is not None and re.fullmatch(r'[A-Za-z0-9]',self.peek()):arg=self.atom()
                else:raise TexError('Superscript requires one observed atom or group')
                atom=Node('msup',children=[atom,arg],tokens=[mark])
                if self.peek() in {'^','_'}:raise TexError('Repeated or unreviewed script')
            children.append(atom)
        return Node('mrow',children=children)

    def atom(self):
        value=self.peek()
        if value is None:raise TexError('Missing atom')
        if value=='{':return self.group()
        if value in {'(','['}:
            closing=')' if value=='(' else ']'
            left=self.take(effect='visible source opening fence')
            inside=self.sequence({closing});right=self.take(closing,'visible source closing fence')
            if not inside.children:raise TexError('Empty fenced source expression')
            attrs={'fence':'true','stretchy':'false'}
            return Node('mrow',children=[Node('mo',value,dict(attrs),tokens=[left]),*inside.children,Node('mo',closing,dict(attrs),tokens=[right])])
        if value==r'\text':
            command=self.take(effect='literal source text command')
            left=self.take('{','nonprinting text boundary');begin=self.tokens[left]['end']
            while self.peek() not in {None,'}'}:
                if self.peek()=='{' or self.peek().startswith('\\'):raise TexError('Nested source text syntax unsupported')
                self.take(effect='exact literal mtext payload')
            right=self.take('}','nonprinting text boundary')
            payload=self.raw[begin:self.tokens[right]['start']]
            if payload not in TEXT_PAYLOADS:raise TexError('Unreviewed literal text payload')
            for i in range(left+1,right):self.tokens[i]['effect']='exact literal mtext payload including spaces'
            return Node('mtext',payload,{'{'+XML+'}space':'preserve'},tokens=list(range(command,right+1)))
        if value.startswith('\\'):
            if value==r'\!':raise TexError('Unreviewed negative-space placement')
            i=self.take(effect='whitelisted source symbol or inert macro expansion')
            return Node('mo',SYMBOLS[value[1:]],tokens=[i])
        if value.isdigit():return Node('mn',value,tokens=[self.take(effect='unchanged numeric token')])
        if re.fullmatch('[A-Za-z]',value):return Node('mi',value,tokens=[self.take(effect='unchanged variable token')])
        if value in {'=','+','-',',',';',':'}:
            i=self.take(effect='ASCII source minus to U+2212' if value=='-' else 'unchanged operator/separator')
            return Node('mo','−' if value=='-' else value,tokens=[i])
        raise TexError('Unreviewed source atom '+repr(value))

    def parse(self):
        root=self.sequence()
        if self.peek() is not None or not root.children:raise TexError('Unconsumed/empty source expression')
        if any(t['effect'] is None for t in self.tokens):raise TexError('Unaccounted source token')
        def bind(n,path):
            for i in n.tokens:self.tokens[i]['mathml_paths'].append(path)
            counts={}
            for child in n.children:
                counts[child.tag]=counts.get(child.tag,0)+1
                bind(child,path+'/'+child.tag+'['+str(counts[child.tag])+']')
        bind(root,'/math/semantics/mrow[1]')
        if ''.join(t['raw'] for t in self.tokens)!=self.raw:raise TexError('Nonreversible token ledger')
        return root,self.tokens


def convert(raw,display=False):
    base=dict(source_tex=raw,source_tex_sha256=hashlib.sha256(raw.encode()).hexdigest(),display='block' if display else 'inline')
    if raw==FALLBACK_RAW:
        tokens=tokenize(raw)
        for token in tokens:token['effect']='Unreviewed negative-spacing form: unchanged source TeX fallback'
        return '<code class="tex-unreviewed" dir="ltr">'+html.escape(raw,quote=False)+'</code>',dict(base,status='source-tex-fallback',reason=FALLBACK_REASON,tree=None,tree_sha256=None,tokens=tokens)
    ast,tokens=Parser(raw).parse()
    root=E.Element('{'+MATH+'}math',nsmap={None:MATH},dir='ltr',display=base['display'])
    semantics=E.SubElement(root,'{'+MATH+'}semantics')
    def emit(parent,n):
        node=E.SubElement(parent,'{'+MATH+'}'+n.tag,attrib=n.attrs);node.text=n.text
        for child in n.children:emit(node,child)
    emit(semantics,ast)
    annotation=E.SubElement(semantics,'{'+MATH+'}annotation',encoding='application/x-tex');annotation.text=raw
    desc=ast.descriptor()
    return E.tostring(root,encoding='unicode'),dict(base,status='derived-mathml',tree=desc,tree_sha256=hashlib.sha256(json.dumps(desc,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),tokens=tokens)

