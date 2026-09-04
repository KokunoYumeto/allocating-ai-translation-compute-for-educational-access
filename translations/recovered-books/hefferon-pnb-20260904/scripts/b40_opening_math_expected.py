"""Independent handwritten mathematical-source fixtures for B40-opening.

No renderer/converter imports and no generated output. These expected trees encode
only the 76 reviewed source formulas and the pinned Hefferon macro meanings.
"""
import re

def n(tag,text=None,children=(),attrs=None):return [tag,attrs or {},text,list(children)]
def row(*x):return n("mrow",children=x)
def mi(x,attrs=None):return n("mi",x,attrs=attrs)
def mn(x):return n("mn",str(x))
def mo(x,attrs=None):return n("mo",x,attrs=attrs)
def mspace(width):return n("mspace",attrs={"width":width})
def sub(a,b):return n("msub",children=[a,b])
def sup(a,b):return n("msup",children=[a,b])
def mover(a):return n("mover",children=[a,mo("→")],attrs={"accent":"true"})
def fence(a,items,b):
    attrs={"fence":"true","stretchy":"false"}
    return row(mo(a,attrs),*items,mo(b,attrs))
def grp(*x):return row(*x)
def seq(*x):return fence("⟨",x,"⟩")
def aset(*x):return fence("{",x,"}")
def par(*x):return fence("(",x,")")
def bracket(*x):return fence("[",x,"]")
def commas(xs):
    out=[]
    for i,x in enumerate(xs):
        if i:out.append(mo(","))
        out.append(x)
    return out
def bb(x):return mi({"R":"ℝ","N":"ℕ","C":"ℂ"}[x],{"mathvariant":"normal"})
def script(x):return mi(x,{"mathvariant":"normal"})
def rep(arg,basis):return row(sub(mi("Rep",{"mathvariant":"normal"}),basis),par(*arg[3]))
def rspace(letter,arg,general=False):
    base=script(letter)
    if general:base=sub(base,mo("∞"))
    return row(base,par(*arg[3]))
def norm(s):return re.sub(r"\s+","",s)
E={}
def put(raw,tree):
    k=norm(raw)
    if k in E and E[k]!=tree:raise AssertionError("duplicate fixture")
    E[k]=tree

for v in list("nHi jVWUZIMNhgtsBoSDe") + ["o"]:
    if v!=" ":put(v,row(mi(v)))
put(r"\Re",row(bb("R")));put(r"\Re^+",row(sup(bb("R"),mo("+"))));put(r"\Re^n",row(sup(bb("R"),mi("n"))))
put(r"\N",row(bb("N")));put(r"\C",row(bb("C")))
put(r"\set{0,1,2,\ldots}",row(aset(mn(0),mo(","),mn(1),mo(","),mn(2),mo(","),mo("…"))))
interval=lambda left,right: row(fence(left,[mi("a"),mspace("0.1667em"),mo("."),mo("."),mspace("0.1667em"),mi("b")],right))
put(r"(a\,..\,b)",interval("(",")"));put(r"[a\,..\,b]",interval("[","]"))
put(r"\sequence{\ldots}",row(seq(mo("…"))))
put(r"h_{i,j}",row(sub(mi("h"),grp(mi("i"),mo(","),mi("j")))))
put("V,W,U",row(mi("V"),mo(","),mi("W"),mo(","),mi("U")))
put(r"\vec{v}",row(mover(grp(mi("v")))))
zero=mover(mn(0));put(r"\zero",row(zero));put(r"\zero_V",row(sub(zero,mi("V"))))
put(r"\polyspace_n",row(sub(script("𝒫"),mi("n"))))
nbym=lambda a,b:row(grp(mi(a)),mo("×"),grp(mi(b)))
put(r"\nbym{n}{m}",row(nbym("n","m")))
put(r"\matspace_{\nbym{n}{m}}",row(sub(script("ℳ"),grp(nbym("n","m")))))
put(r"\spanof{S}",row(bracket(mi("S"))))
put(r"\sequence{B,D}",row(seq(mi("B"),mo(","),mi("D"))))
put(r"\vec{\beta},\vec{\delta}",row(mover(grp(mi("β"))),mo(","),mover(grp(mi("δ")))))
ve=lambda subscript:sub(mover(grp(mi("e"))),subscript)
basis=seq(ve(mn(1)),mo(","),mspace("0.1667em"),mo("…"),mo(","),mspace("0.1667em"),ve(mi("n")))
put(r"\stdbasis_n=\sequence{\vec{e}_1,\,\ldots,\,\vec{e}_n}",row(sub(script("ℰ"),mi("n")),mo("="),basis))
put(r"V\isomorphicto W",row(mi("V"),mo("≅"),mi("W")))
put(r"M\directsum N",row(mi("M"),mo("⊕"),mi("N")))
put("h,g",row(mi("h"),mo(","),mi("g")));put("t,s",row(mi("t"),mo(","),mi("s")))
put(r"\rep{\vec{v}}{B}",row(rep(grp(mover(grp(mi("v")))),grp(mi("B")))))
put(r"\rep{h}{B,D}",row(rep(grp(mi("h")),grp(mi("B"),mo(","),mi("D")))))
put(r"Z_{\nbym{n}{m}}",row(sub(mi("Z"),grp(nbym("n","m")))))
put(r"I_{\nbyn{n}}",row(sub(mi("I"),grp(nbym("n","n")))))
put(r"\deter{T}",row(fence("|",[mi("T")],"|")))
put(r"\rangespace{h},\nullspace{h}",row(rspace("𝓡",grp(mi("h"))),mo(","),rspace("𝓝",grp(mi("h")))))
put(r"\genrangespace{h},\gennullspace{h}",row(rspace("𝓡",grp(mi("h")),True),mo(","),rspace("𝓝",grp(mi("h")),True)))
G={"alpha":"α","beta":"β","gamma":"γ","Gamma":"Γ","delta":"δ","Delta":"Δ","epsilon":"ε",
"zeta":"ζ","eta":"η","theta":"θ","Theta":"Θ","iota":"ι","kappa":"κ","lambda":"λ",
"Lambda":"Λ","mu":"μ","nu":"ν","xi":"ξ","Xi":"Ξ","pi":"π","Pi":"Π","rho":"ρ",
"sigma":"σ","Sigma":"Σ","tau":"τ","upsilon":"υ","Upsilon":"Υ","phi":"φ","Phi":"Φ",
"chi":"χ","psi":"ψ","Psi":"Ψ","omega":"ω","Omega":"Ω"}
for cmd,glyph in G.items():put("\\"+cmd,row(mi(glyph)))

def expected(raw):
    k=norm(raw)
    if k not in E:raise ValueError("No independent fixture for "+repr(raw))
    return E[k]
