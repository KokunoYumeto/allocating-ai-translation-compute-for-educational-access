"""Strict nonexecuting TeX-to-MathML mapper for B40-opening's 76 observed formulas.

This is not TeX. It accepts only a reviewed finite grammar and fails closed.
Every raw token and whitespace run is retained in a reversible ledger. Hefferon's
macro meanings are source-bound in the component notice; no upstream code runs.
"""
from dataclasses import dataclass, field
import hashlib
import json
import re
from lxml import etree as E

MATH="http://www.w3.org/1998/Math/MathML"
GREEK={
"alpha":"α","beta":"β","gamma":"γ","Gamma":"Γ","delta":"δ","Delta":"Δ",
"epsilon":"ε","zeta":"ζ","eta":"η","theta":"θ","Theta":"Θ","iota":"ι",
"kappa":"κ","lambda":"λ","Lambda":"Λ","mu":"μ","nu":"ν","xi":"ξ","Xi":"Ξ",
"pi":"π","Pi":"Π","rho":"ρ","sigma":"σ","Sigma":"Σ","tau":"τ",
"upsilon":"υ","Upsilon":"Υ","phi":"φ","Phi":"Φ","chi":"χ","psi":"ψ",
"Psi":"Ψ","omega":"ω","Omega":"Ω"}
SYMBOL={"Re":("mi","ℝ",{"mathvariant":"normal"}),"N":("mi","ℕ",{"mathvariant":"normal"}),
"C":("mi","ℂ",{"mathvariant":"normal"}),"ldots":("mo","…",{}),
"isomorphicto":("mo","≅",{}),"directsum":("mo","⊕",{})}
FUNCTIONS={"set":1,"sequence":1,"vec":1,"nbym":2,"nbyn":1,"spanof":1,
"rep":2,"deter":1,"rangespace":1,"nullspace":1,"genrangespace":1,
"gennullspace":1}
ATOMIC={"zero","polyspace","matspace","stdbasis"}
TOKEN_RE=re.compile(r"\s+|\\[A-Za-z]+|\\[,!]|[A-Za-z]|[0-9]+|[{}()\[\]^_=+,.]")

class TexError(ValueError): pass

@dataclass
class Node:
    tag:str
    text:str|None=None
    attrs:dict=field(default_factory=dict)
    children:list=field(default_factory=list)
    tokens:list=field(default_factory=list)
    normalization:str|None=None
    def descriptor(self):return [self.tag,self.attrs,self.text,[c.descriptor() for c in self.children]]

def tokenize(raw):
    out=[];pos=0
    while pos<len(raw):
        m=TOKEN_RE.match(raw,pos)
        if not m:raise TexError("Unsupported character at "+str(pos)+": "+repr(raw[pos:pos+12]))
        value=m.group()
        kind="space" if value.isspace() else "command" if value.startswith("\\") else "number" if value.isdigit() else "variable" if value.isalpha() else "syntax"
        if kind=="command":
            name=value[1:]
            if name not in set(GREEK)|set(SYMBOL)|set(FUNCTIONS)|ATOMIC|{",","!"}:
                raise TexError("Unsupported command "+value)
        out.append({"start":pos,"end":m.end(),"raw":value,"kind":kind,"effect":None,"mathml_paths":[]})
        pos=m.end()
    if not out:raise TexError("Empty formula")
    return out

def row(*nodes,tokens=()):return Node("mrow",children=list(nodes),tokens=list(tokens))
def mi(text,attrs=None,tokens=()):return Node("mi",text,attrs or {},tokens=list(tokens))
def mo(text,attrs=None,tokens=()):return Node("mo",text,attrs or {},tokens=list(tokens))
def fence(left,inside,right,tokens=()):
    a={"fence":"true","stretchy":"false"}
    return row(mo(left,a),*inside.children,mo(right,a),tokens=tokens)

class Parser:
    def __init__(self,raw):
        self.raw=raw;self.ledger=tokenize(raw)
        self.order=[i for i,x in enumerate(self.ledger) if x["kind"]!="space"];self.pos=0
        for x in self.ledger:
            if x["kind"]=="space":x["effect"]="TeX whitespace retained; presentation handled by MathML layout"
        self.normalizations=[]
    def peek(self):return self.ledger[self.order[self.pos]]["raw"] if self.pos<len(self.order) else None
    def take(self,value=None,effect=None):
        if self.peek() is None or value is not None and self.peek()!=value:
            raise TexError("Expected "+repr(value)+"; found "+repr(self.peek()))
        i=self.order[self.pos];self.pos+=1
        if effect:self.ledger[i]["effect"]=effect
        return i
    def group(self):
        a=self.take("{","nonprinting TeX group boundary");v=self.sequence({"}"})
        b=self.take("}","nonprinting TeX group boundary")
        if not v.children:raise TexError("Empty group")
        v.tokens += [a,b];return v
    def arg(self):return self.group()
    def sequence(self,stops=frozenset()):
        values=[]
        while self.peek() is not None and self.peek() not in stops:
            if self.peek() in {"}",")","]"}:raise TexError("Unexpected closing fence")
            atom=self.atom();scripts={};marks=[]
            while self.peek() in {"_","^"}:
                mark=self.peek()
                if mark in scripts:raise TexError("Repeated script")
                marks.append(self.take(mark,"script binding"))
                scripts[mark]=self.group() if self.peek()=="{" else self.atom()
            if scripts:
                atom=Node("msubsup" if len(scripts)==2 else "msub" if "_" in scripts else "msup",
                          children=[atom]+([scripts["_"],scripts["^"]] if len(scripts)==2 else [next(iter(scripts.values()))]),
                          tokens=marks)
            values.append(atom)
        return row(*values)
    def macro(self,name,token,args):
        def unary_group(i=0):return args[i]
        if name=="set":return fence("{",unary_group(),"}",tokens=[token])
        if name=="sequence":return fence("⟨",unary_group(),"⟩",tokens=[token])
        if name=="vec":return Node("mover",attrs={"accent":"true"},children=[unary_group(),mo("→")],tokens=[token])
        if name in {"nbym","nbyn"}:
            if name=="nbyn":args=[args[0],args[0]]
            self.normalizations.append({"command":"\\"+name,"source_expansion_spacing":"negative thin space on both sides of multiplication","mathml_normalization":"operator spacing delegated to MathML Core; exact macro/source TeX retained"})
            return row(args[0],mo("×"),args[1],tokens=[token])
        if name=="spanof":return fence("[",unary_group(),"]",tokens=[token])
        if name=="rep":
            rep=Node("msub",children=[mi("Rep",{"mathvariant":"normal"}),args[1]])
            return row(rep,fence("(",args[0],")"),tokens=[token])
        if name=="deter":return fence("|",unary_group(),"|",tokens=[token])
        if name in {"rangespace","nullspace","genrangespace","gennullspace"}:
            base=mi("𝓡" if "range" in name else "𝓝",{"mathvariant":"normal"})
            if name.startswith("gen"):base=Node("msub",children=[base,mo("∞")])
            return row(base,fence("(",unary_group(),")"),tokens=[token])
        raise TexError("Unimplemented macro "+name)
    def atom(self):
        v=self.peek()
        if v is None:raise TexError("Missing atom")
        if v=="{":return self.group()
        if v in {"(","["}:
            close=")" if v=="(" else "]";a=self.take(v,"visible opening fence")
            inside=self.sequence({close});b=self.take(close,"visible closing fence")
            if not inside.children:raise TexError("Empty fence")
            result=fence(v,inside,close,tokens=[a,b]);return result
        if v.startswith("\\"):
            name=v[1:]
            if name in {",","!"}:
                i=self.take(effect="explicit thin space" if name=="," else "negative thin space")
                width="0.1667em" if name=="," else "-0.1667em"
                return Node("mspace",attrs={"width":width},tokens=[i])
            if name in GREEK:
                return mi(GREEK[name],tokens=[self.take(effect="whitelisted Greek symbol")])
            if name in SYMBOL:
                tag,text,attrs=SYMBOL[name]
                return Node(tag,text,dict(attrs),tokens=[self.take(effect="source-bound symbol mapping")])
            if name in ATOMIC:
                i=self.take(effect="source-bound Hefferon macro")
                if name=="zero":return Node("mover",attrs={"accent":"true"},children=[Node("mn","0"),mo("→")],tokens=[i])
                text={"polyspace":"𝒫","matspace":"ℳ","stdbasis":"ℰ"}[name]
                return mi(text,{"mathvariant":"normal"},tokens=[i])
            if name in FUNCTIONS:
                i=self.take(effect="source-bound Hefferon macro with "+str(FUNCTIONS[name])+" argument(s)")
                args=[self.arg() for _ in range(FUNCTIONS[name])]
                return self.macro(name,i,args)
        if v.isdigit():return Node("mn",v,tokens=[self.take(effect="unchanged number")])
        if re.fullmatch("[A-Za-z]",v):return mi(v,tokens=[self.take(effect="unchanged variable")])
        if v in {"=", "+", ",", "."}:
            return mo(v,tokens=[self.take(effect="unchanged operator/punctuation")])
        raise TexError("Unexpected atom "+repr(v))
    def parse(self):
        ast=self.sequence()
        if self.peek() is not None or not ast.children:raise TexError("Unconsumed or empty")
        if any(x["effect"] is None for x in self.ledger):raise TexError("Unaccounted token")
        def bind(n,path):
            for i in n.tokens:self.ledger[i]["mathml_paths"].append(path)
            counts={}
            for c in n.children:
                counts[c.tag]=counts.get(c.tag,0)+1
                bind(c,path+"/"+c.tag+"["+str(counts[c.tag])+"]")
        bind(ast,"/math/semantics/mrow[1]")
        if "".join(x["raw"] for x in self.ledger)!=self.raw:raise TexError("Nonreversible ledger")
        return ast,self.ledger,self.normalizations

def convert(raw):
    ast,ledger,norm=Parser(raw).parse()
    root=E.Element("{"+MATH+"}math",nsmap={None:MATH},dir="ltr",display="inline")
    sem=E.SubElement(root,"{"+MATH+"}semantics")
    def add(parent,node):
        e=E.SubElement(parent,"{"+MATH+"}"+node.tag,attrib=node.attrs);e.text=node.text
        for c in node.children:add(e,c)
    add(sem,ast);ann=E.SubElement(sem,"{"+MATH+"}annotation",encoding="application/x-tex");ann.text=raw
    desc=ast.descriptor()
    record={"source_tex":raw,"source_tex_sha256":hashlib.sha256(raw.encode()).hexdigest(),
            "tree":desc,"tree_sha256":hashlib.sha256(json.dumps(desc,ensure_ascii=False,separators=(",",":")).encode()).hexdigest(),
            "tokens":ledger,"normalizations":norm}
    return E.tostring(root,encoding="unicode"),record

