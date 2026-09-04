"""Strict, nonexecuting presentation parser for the observed B10-001 TeX subset.

Not a LaTeX engine. Unknown commands/characters, incomplete groups and unsupported
text payloads fail closed. Raw source and every token/space survive in a ledger.
"""
from dataclasses import dataclass, field
import hashlib
import json
import re
from lxml import etree as E

MATH = 'http://www.w3.org/1998/Math/MathML'
XML = 'http://www.w3.org/XML/1998/namespace'
COMMANDS = {'N':('mi','ℕ',{'mathvariant':'normal'}),
            'st':('mo',':',{}),'cdot':('mo','⋅',{}),'ge':('mo','≥',{}),
            'in':('mo','∈',{}),'infty':('mo','∞',{}),'ldots':('mo','…',{}),
            'lt':('mo','<',{}),'ne':('mo','≠',{}),'to':('mo','→',{})}


class TexError(ValueError):
    pass


@dataclass
class Node:
    tag: str
    text: str | None = None
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    tokens: list = field(default_factory=list)

    def descriptor(self):
        return [self.tag,self.attrs,self.text,[c.descriptor() for c in self.children]]


def tokenize(raw):
    result=[]
    pattern=re.compile(r'\s+|\\[A-Za-z]+|\\[{}]|[0-9]+|[A-Za-z]|[{}()\[\]^_=+,;:\-]')
    pos=0
    while pos<len(raw):
        match=pattern.match(raw,pos)
        if not match:
            raise TexError('Unsupported source character at '+str(pos)+': '+repr(raw[pos:pos+12]))
        value=match.group();kind=('space' if value.isspace() else 'command' if value.startswith('\\') else 'number' if value.isdigit() else 'variable' if value.isalpha() else 'syntax')
        if kind=='command' and value[1:] not in set(COMMANDS)|{'frac','text','{','}'}:
            raise TexError('Unsupported command '+value)
        result.append({'start':pos,'end':match.end(),'raw':value,'kind':kind,'effect':None,'mathml_paths':[]})
        pos=match.end()
    if not result:
        raise TexError('Empty formula')
    return result


class Parser:
    def __init__(self,raw):
        self.raw=raw
        self.ledger=tokenize(raw)
        self.order=[i for i,t in enumerate(self.ledger) if t['kind']!='space']
        self.pos=0
        for t in self.ledger:
            if t['kind']=='space':t['effect']='TeX presentation whitespace; raw retained'

    def peek(self):
        return self.ledger[self.order[self.pos]]['raw'] if self.pos<len(self.order) else None

    def take(self,value=None,effect=None):
        if self.peek() is None or (value is not None and self.peek()!=value):
            raise TexError('Expected '+repr(value)+'; found '+repr(self.peek()))
        i=self.order[self.pos];self.pos+=1
        if effect:self.ledger[i]['effect']=effect
        return i

    def group(self):
        left=self.take('{','nonprinting TeX group boundary')
        value=self.sequence({'}'})
        right=self.take('}','nonprinting TeX group boundary')
        value.tokens += [left,right]
        if not value.children:raise TexError('Empty group')
        return value

    def sequence(self,stops=frozenset()):
        values=[]
        while self.peek() is not None and self.peek() not in stops:
            if self.peek() in {'}',')',']','\\}'}:raise TexError('Unexpected closing fence '+self.peek())
            atom=self.atom()
            scripts={}
            signs=[]
            while self.peek() in {'_','^'}:
                mark=self.peek()
                if mark in scripts:raise TexError('Repeated script operator')
                signs.append(self.take(mark,'script binding'))
                if self.peek()=='{':arg=self.group()
                else:
                    if self.peek() is None or not re.fullmatch(r'[A-Za-z0-9]',self.peek()):
                        raise TexError('Unbraced script must be one observed identifier/digit')
                    arg=self.atom()
                scripts[mark]=arg
            if scripts:
                if len(scripts)==2:atom=Node('msubsup',children=[atom,scripts['_'],scripts['^']],tokens=signs)
                else:
                    mark=next(iter(scripts));atom=Node('msub' if mark=='_' else 'msup',children=[atom,scripts[mark]],tokens=signs)
            values.append(atom)
        return Node('mrow',children=values)

    def atom(self):
        value=self.peek()
        if value is None:raise TexError('Missing atom')
        if value=='{':return self.group()
        if value in {'(','[','\\{'}:
            opening=value
            closing=')' if value=='(' else '\\}' if value=='\\{' else ')'
            # This unit's only square bracket begins the half-open [0,infinity).
            i=self.take(effect='visible opening fence')
            inside=self.sequence({closing})
            j=self.take(closing,'visible closing fence')
            if not inside.children:raise TexError('Empty fenced expression')
            return Node('mrow',children=[Node('mo','{' if opening=='\\{' else opening,{'fence':'true','stretchy':'false'},tokens=[i])]+inside.children+[Node('mo','}' if closing=='\\}' else closing,{'fence':'true','stretchy':'false'},tokens=[j])])
        if value=='\\frac':
            i=self.take(effect='fraction with two source groups')
            numerator=self.group();denominator=self.group()
            return Node('mfrac',children=[numerator,denominator],tokens=[i])
        if value=='\\text':
            cmd=self.take(effect='literal source text')
            left=self.take('{','nonprinting text group boundary')
            begin=self.ledger[left]['end']
            contents=[]
            while self.peek() not in (None,'}'):
                if self.peek()=='{' or self.peek().startswith('\\'):raise TexError('Nested/command text unsupported')
                contents.append(self.take(effect='literal mtext content'))
            right=self.take('}','nonprinting text group boundary')
            payload=self.raw[begin:self.ledger[right]['start']]
            if payload!=' and ':raise TexError('Only the observed exact text{ and } is supported')
            token_ids=list(range(cmd,right+1))
            for k in range(left+1,right):self.ledger[k]['effect']='literal mtext content including exact spacing'
            return Node('mtext',payload,{'{'+XML+'}space':'preserve'},tokens=token_ids)
        if value.startswith('\\'):
            i=self.take(effect='source \\N / mathbb N to U+2115 DOUBLE-STRUCK CAPITAL N for MathML Core' if value=='\\N' else 'whitelisted declarative symbol mapping')
            tag,text,attrs=COMMANDS[value[1:]]
            return Node(tag,text,dict(attrs),tokens=[i])
        if value.isdigit():return Node('mn',value,tokens=[self.take(effect='unchanged numeric token')])
        if re.fullmatch('[A-Za-z]',value):return Node('mi',value,tokens=[self.take(effect='unchanged variable token')])
        if value in {'=','+','-',',',';',':'}:
            i=self.take(effect='ASCII TeX minus to U+2212 presentation' if value=='-' else 'unchanged operator/separator')
            return Node('mo','−' if value=='-' else value,tokens=[i])
        raise TexError('Unexpected atom '+repr(value))

    def parse(self):
        ast=self.sequence()
        if self.peek() is not None or not ast.children:raise TexError('Unconsumed or empty formula')
        if any(t['effect'] is None for t in self.ledger):raise TexError('Unaccounted source token')
        def bind(node,path):
            for i in node.tokens:self.ledger[i]['mathml_paths'].append(path)
            counts={}
            for c in node.children:
                counts[c.tag]=counts.get(c.tag,0)+1
                bind(c,path+'/'+c.tag+'['+str(counts[c.tag])+']')
        bind(ast,'/math/semantics/mrow[1]')
        if ''.join(t['raw'] for t in self.ledger)!=self.raw:raise TexError('Nonreversible token ledger')
        return ast,self.ledger


def convert(raw,display=False):
    ast,ledger=Parser(raw).parse()
    root=E.Element('{'+MATH+'}math',nsmap={None:MATH},dir='ltr',display='block' if display else 'inline')
    semantics=E.SubElement(root,'{'+MATH+'}semantics')
    def append(parent,node):
        e=E.SubElement(parent,'{'+MATH+'}'+node.tag,attrib=node.attrs)
        e.text=node.text
        for c in node.children:append(e,c)
    append(semantics,ast)
    annotation=E.SubElement(semantics,'{'+MATH+'}annotation',encoding='application/x-tex')
    annotation.text=raw
    record={'source_tex':raw,'source_tex_sha256':hashlib.sha256(raw.encode()).hexdigest(),
            'display':'block' if display else 'inline','tree':ast.descriptor(),'tokens':ledger,
            'tree_sha256':hashlib.sha256(json.dumps(ast.descriptor(),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
    return E.tostring(root,encoding='unicode'),record
