"""Standalone U011 checks: preserved source, exact coefficients and finite arithmetic.

Only the committed excerpt/draft are required by default; --originals additionally
requires both pinned full module downloads. No third-party Python packages/network.
Finite samples do not prove arbitrary-function or infinite-domain claims.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
EXCERPT_SHA = "7a10ea3a63a59e3ca40064a78d40142a48484a72356e86134317a67a9ba78294"
EXERCISES = [
    "fs-id1165137431335", "fs-id1165137727203", "fs-id1165137844088",
    "fs-id1165135697840", "fs-id1165135453854", "fs-id1165135195666",
    "fs-id1165135579705", "fs-id1165134036847", "fs-id1165134155170",
    "fs-id1165137935719", "fs-id1165135361357", "fs-id1165137833947",
    "fs-id1165137433542",
]
SOLUTIONS = [
    "fs-id1165137409631", None, "fs-id1165134151868", None,
    "fs-id1165135357153", None, "fs-id1165134284461", None,
    "fs-id1165135518215", None, "fs-id1165135453081", None,
    "fs-id1165137767447",
]


def notation(node):
    """Readable structural signature: unlike itertext, retains roots/fractions/powers."""
    tag = node.tag.rsplit("}", 1)[-1]
    if tag in ("mi", "mn", "mo"):
        return (node.text or "").strip()
    if tag == "msqrt":
        return "sqrt(" + "".join(map(notation, node)) + ")"
    if tag == "msup":
        return f"({notation(node[0])})^({notation(node[1])})"
    if tag == "mfrac":
        return f"({notation(node[0])})/({notation(node[1])})"
    if tag == "mspace":
        return ""
    if tag not in ("math", "mrow"):
        raise ValueError(f"Unexpected MathML tag: {tag}")
    return "".join(map(notation, node))


# Small exact polynomial ring in x,a,h. Coefficients, not samples, test identities.
def constant(value):
    return {(0, 0, 0): Q(value)} if value else {}


def variable(index):
    powers = [0, 0, 0]
    powers[index] = 1
    return {tuple(powers): Q(1)}


def add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for monomial, coefficient in polynomial.items():
            result[monomial] = result.get(monomial, Q(0)) + coefficient
    return {m: c for m, c in result.items() if c}


def scale(polynomial, coefficient):
    return {m: c * coefficient for m, c in polynomial.items() if c * coefficient}


def multiply(left, right):
    result = {}
    for m, c in left.items():
        for n, d in right.items():
            key = tuple(a + b for a, b in zip(m, n))
            result[key] = result.get(key, Q(0)) + c * d
    return {m: c for m, c in result.items() if c}


def square(polynomial):
    return multiply(polynomial, polynomial)


def shifted_root(radicand, offset=Q(5), sign=1):
    """Exact offset + sign*sqrt(rational); normalize to a squarefree radical.

    Returns a Fraction for rational results, otherwise (offset, coefficient,
    squarefree_integer), representing offset+coefficient*sqrt(squarefree_integer).
    Trial division is deliberately restricted to these small test inputs.
    """
    radicand = Q(radicand)
    if radicand < 0:
        raise ValueError("negative radicand over the reals")
    if radicand == 0:
        return Q(offset)
    number = radicand.numerator * radicand.denominator
    divisor, factor, free = 2, 1, 1
    while divisor * divisor <= number:
        exponent = 0
        while number % divisor == 0:
            number //= divisor
            exponent += 1
        factor *= divisor ** (exponent // 2)
        if exponent % 2:
            free *= divisor
        divisor += 1
    free *= number
    coefficient = sign * Q(factor, radicand.denominator)
    if free == 1:
        return Q(offset) + coefficient
    return Q(offset), coefficient, free


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, description, kind="structure"):
        assert condition, description
        counts[kind] += 1

    path = ROOT / "sources/m49301-algebraic-evaluation-source.cnxml"
    data = path.read_bytes()
    tree = ET.fromstring(data)
    markdown = (ROOT / "translation/A30-U011-algebraic-evaluation.vi.md").read_text("utf-8")
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned complete excerpt bytes")
    check(tree.tag == f"{{{CN}}}source-excerpt" and not tree.get("id"),
          "synthetic wrapper does not repeat U010 Algebraic parent ID")
    check(tree[0].get("id") == "fs-id1165134066606", "shared prompt first")
    check(tree[-1].get("id") == EXERCISES[-1], "final Algebraic exercise last")
    check([n.get("id") for n in tree.findall(f"{{{CN}}}exercise")] == EXERCISES,
          "all thirteen exercises in exact source order")
    check(len(tree) == 14, "one shared prompt and thirteen exercises")
    check(markdown == unicodedata.normalize("NFC", markdown), "NFC Vietnamese")
    check("fs-id1165134080937}" not in markdown, "no U010 parent anchor duplication")
    identities = [n.get("id") for n in tree.iter() if n.get("id")]
    check(len(identities) == len(set(identities)) == 60, "60 unique source IDs")
    explicit = re.findall(r"\{#([^}]+)\}", markdown)
    for identity in identities:
        check(explicit.count(identity) == 1, f"exactly one source anchor: {identity}")
    for tag, expected in (("solution", 7), ("problem", 13), ("para", 18),
                          ("list", 9), ("image", 0), ("table", 0), ("link", 0)):
        check(len(list(tree.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")
    check(not list(tree.iter(f"{{{M}}}mtext")), "no MathML prose dictionary required")
    indexed = {n.get("id"): n for n in tree.iter() if n.get("id")}
    original_math = list(tree.iter(f"{{{M}}}math"))
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        inserted.append(list(indexed[identity].iter(f"{{{M}}}math"))[int(index)])
    check(len(original_math) == len(inserted) == 54, "54 source MathML occurrences")
    check(Counter(map(id, original_math)) == Counter(map(id, inserted)),
          "every original math occurrence inserted exactly once")
    math_at = lambda identity: list(indexed[identity].iter(f"{{{M}}}math"))
    signature_at = lambda identity: list(map(notation, math_at(identity)))

    for number, identity, solution in zip(range(27, 40), EXERCISES, SOLUTIONS):
        check(f"### Bài {number} {{#{identity}}}" in markdown, "source-wide exercise numbering")
        actual = indexed[identity].find(f"{{{CN}}}solution")
        check((actual.get("id") if actual is not None else None) == solution,
              "source versus newly written solution")
        if solution:
            check(f"### Bài {number} — Lời giải nguồn {{#{solution}}}" in markdown,
                  "source answer label")
        else:
            check(f"### Bài {number} — Lời giải bổ sung" in markdown, "new answer label")
    check(markdown.count("Nguồn không kèm lời giải cho") == 6,
          "six explicit new-solution disclosures")
    for target in re.findall(r"\]\(#([^)]+)\)", markdown):
        check(target in explicit, f"local solution link {target}")

    # Source signatures independently read against the original EN/ID formulas.
    formula_signatures = [
        "f(x)=2x−5", "f(x)=−5(x)^(2)+2x−1", "f(x)=sqrt(2−x)+5",
        "f(x)=(6x−1)/(5x+2)", "f(x)=|x−1|−|x+1|",
        "g(x)=5−(x)^(2),", "g(x)=(x)^(2)+2x,", "k(t)=2t−1:",
        "f(x)=8−3x:", "p(c)=(c)^(2)+c:", "f(x)=(x)^(2)−3x:",
        "f(x)=sqrt(x+2):", "3r+2t=18.",
    ]
    for identity, expected in zip(EXERCISES, formula_signatures):
        check(notation(next(indexed[identity].iter(f"{{{M}}}math"))) == expected,
              f"independent formula transcription {identity}")
    answer_signatures = {
        "fs-id1165137529461": [
            "f(−3)=−11;", "f(2)=−1;", "f(−a)=−2a−5;",
            "−f(a)=−2a+5;", "f(a+h)=2a+2h−5"],
        "fs-id1165134151870": [
            "f(−3)=sqrt(5)+5;", "f(2)=5;", "f(−a)=sqrt(2+a)+5;",
            "−f(a)=−sqrt(2−a)−5;", "f(a+h)=sqrt(2−a−h)+5"],
        "fs-id1165135357155": [
            "f(−3)=2;", "f(2)=1−3=−2;", "f(−a)=|−a−1|−|−a+1|;",
            "−f(a)=−|a−1|+|a+1|;", "f(a+h)=|a+h−1|−|a+h+1|"],
        "fs-id1165134284463": ["(g(x)−g(a))/(x−a)=x+a+2,x≠a"],
        "eip-idm507287856": ["f(−2)=14;", "x=3"],
        "eip-idm501917600": ["f(5)=10;", "x=−1", "x=4"],
        "eip-idm497267968": ["f(t)=6−(2)/(3)t;", "f(−3)=8;", "t=6"],
    }
    for identity, expected in answer_signatures.items():
        check(signature_at(identity) == expected, f"all source answer tokens {identity}")
    check(signature_at("fs-id1165134066606") == [
        "f", "f(−3),f(2),f(−a),−f(a),f(a+h)."], "shared prompt operations")
    check(signature_at("fs-id1165135195670")[1] == "(g(x+h)−g(x))/(h),h≠0.",
          "first quotient nonzero condition")
    check(signature_at("fs-id1165135579709")[1] == "(g(x)−g(a))/(x−a),x≠a.",
          "second quotient unequal-input condition")

    # Exact coefficient identities for the authored derivations.
    x, a, h = [variable(i) for i in range(3)]
    neg = lambda p: scale(p, -1)
    affine = lambda p: add(scale(p, 2), constant(-5))
    quadratic = lambda p: add(scale(square(p), -5), scale(p, 2), constant(-1))
    coefficient_cases = [
        (affine(neg(a)), add(scale(a, -2), constant(-5)), "affine negative argument"),
        (neg(affine(a)), add(scale(a, -2), constant(5)), "affine negative value"),
        (affine(add(a, h)), add(scale(a, 2), scale(h, 2), constant(-5)), "affine sum input"),
        (quadratic(neg(a)), add(scale(square(a), -5), scale(a, -2), constant(-1)),
         "quadratic negative argument"),
        (neg(quadratic(a)), add(scale(square(a), 5), scale(a, -2), constant(1)),
         "quadratic negative value"),
        (quadratic(add(a, h)),
         add(scale(square(a), -5), scale(multiply(a, h), -10), scale(square(h), -5),
             scale(a, 2), scale(h, 2), constant(-1)), "quadratic sum expansion"),
        (add(constant(2), neg(neg(a))), add(constant(2), a), "radical negative argument"),
        (add(constant(2), neg(add(a, h))), add(constant(2), neg(a), neg(h)),
         "radical sum argument"),
        (multiply(add(scale(a, -6), constant(-1)), add(scale(a, 5), constant(-2))),
         multiply(add(scale(a, 6), constant(1)), add(scale(a, -5), constant(2))),
         "rational negative-input rewrite by cross multiplication"),
        (neg(add(scale(a, 6), constant(-1))), add(constant(1), scale(a, -6)),
         "rational negative value numerator"),
        (add(neg(square(add(x, h))), square(x)),
         multiply(h, add(scale(x, -2), neg(h))), "first quotient numerator factors"),
        (add(square(x), scale(x, 2), neg(square(a)), scale(a, -2)),
         multiply(add(x, neg(a)), add(x, a, constant(2))), "second quotient factors"),
        (add(square(x), x, constant(-2)),
         multiply(add(x, constant(2)), add(x, constant(-1))), "p(c)=2 factorization"),
        (add(square(x), scale(x, -3), constant(-4)),
         multiply(add(x, constant(-4)), add(x, constant(1))), "f(x)=4 factorization"),
        (add(scale(add(constant(6), scale(x, Q(-2, 3))), 3), scale(x, 2)),
         constant(18), "last relation for every real input"),
    ]
    for left, right, description in coefficient_cases:
        check(left == right, description, "coefficient")

    # Finite rational arithmetic checks are separate from coefficient identities.
    linear = lambda t: 2 * t - 5
    quad = lambda t: -5 * t * t + 2 * t - 1
    rat = lambda t: (6 * t - 1) / (5 * t + 2)
    absolute = lambda t: abs(t - 1) - abs(t + 1)
    for function, left, right in ((linear, -11, -1), (quad, -52, -17),
                                  (rat, Q(19, 13), Q(11, 12)), (absolute, 2, -2)):
        check(function(Q(-3)) == left, "exact evaluation at -3", "finite")
        check(function(Q(2)) == right, "exact evaluation at 2", "finite")
    check(shifted_root(5) == (Q(5), Q(1), 5), "exact sqrt5+5, no rounding", "finite")
    check(shifted_root(0) == 5, "root function at2", "finite")
    check(shifted_root(Q(1, 4)) == Q(11, 2), "fractional square-root normalizer", "finite")
    check(shifted_root(8) == (Q(5), Q(2), 2), "squarefree radical normalizer", "finite")
    samples = list(map(Q, (-3, -2, -1, 0, 1, 2, 3))) + [Q(1, 2), Q(-2, 5)]
    for value in samples:
        check(linear(-value) == -2 * value - 5, "affine f(-a)", "finite")
        check(-linear(value) == -2 * value + 5, "affine -f(a)", "finite")
        check(quad(-value) == -5 * value**2 - 2 * value - 1, "quadratic f(-a)", "finite")
        check(-quad(value) == 5 * value**2 - 2 * value + 1, "quadratic -f(a)", "finite")
        check(absolute(-value) == abs(-value - 1) - abs(-value + 1), "absolute f(-a)", "finite")
        check(-absolute(value) == -abs(value - 1) + abs(value + 1), "absolute -f(a)", "finite")
        if value != Q(2, 5):
            check(rat(-value) == (6 * value + 1) / (5 * value - 2), "rational f(-a)", "finite")
        if value != Q(-2, 5):
            check(-rat(value) == (1 - 6 * value) / (5 * value + 2), "rational -f(a)", "finite")
        for delta in (Q(-1), Q(0), Q(1, 2)):
            check(quad(value + delta) ==
                  -5 * value**2 - 10 * value * delta - 5 * delta**2 + 2 * value + 2 * delta - 1,
                  "expanded sum input", "finite")
            check(absolute(value + delta) ==
                  abs(value + delta - 1) - abs(value + delta + 1),
                  "absolute sum input", "finite")
            if value + delta != Q(-2, 5):
                check(rat(value + delta) ==
                      (6 * value + 6 * delta - 1) / (5 * value + 5 * delta + 2),
                      "rational sum input", "finite")
            if delta:
                g = lambda t: 5 - t * t
                check((g(value + delta) - g(value)) / delta == -2 * value - delta,
                      "first difference quotient", "finite")
            if value != delta:
                g = lambda t: t * t + 2 * t
                check((g(value) - g(delta)) / (value - delta) == value + delta + 2,
                      "second difference quotient", "finite")
        check((2 + value >= 0) == (value >= -2), "f(-a) radical domain", "domain")
        check((2 - value >= 0) == (value <= 2), "-f(a) radical domain", "domain")
        check((2 - value - Q(1, 2) >= 0) == (value + Q(1, 2) <= 2),
              "f(a+h) radical domain", "domain")
    for function, input_value, expected in (
        (lambda t: 2 * t - 1, 2, 3), (lambda t: 2 * t - 1, 4, 7),
        (lambda t: 8 - 3 * t, -2, 14), (lambda t: 8 - 3 * t, 3, -1),
        (lambda t: t * t + t, -3, 6), (lambda t: t * t + t, -2, 2),
        (lambda t: t * t + t, 1, 2), (lambda t: t * t - 3 * t, 5, 10),
        (lambda t: t * t - 3 * t, -1, 4), (lambda t: t * t - 3 * t, 4, 4),
        (lambda t: shifted_root(t + 2, 0), 7, 3),
        (lambda t: shifted_root(t + 2, 0), 14, 4),
        (lambda t: 6 - Q(2, 3) * t, -3, 8),
        (lambda t: 6 - Q(2, 3) * t, 6, 2),
    ):
        check(function(Q(input_value)) == expected, "evaluate/solve verified input", "finite")
    for call in (lambda: rat(Q(-2, 5)), lambda: shifted_root(-1),
                 lambda: Q(0) / Q(0)):
        try:
            call()
        except (ValueError, ZeroDivisionError):
            check(True, "excluded denominator/radicand rejected", "domain")
        else:
            check(False, "invalid input accepted", "domain")

    # Bind material authored results and restrictions to the displayed draft.
    for required in (
        "-45-6-1=-52", "-20+4-1=-17", "-5a^2-10ah-5h^2+2a+2h-1",
        r"\frac{19}{13}", r"\frac{11}{12}", r"a\ne\frac25",
        r"a\ne-\frac25", r"a+h\ne-\frac25", r"a\ge-2", r"a\le2",
        r"a+h\le2", r"-2x-h,\qquad h\ne0", r"x+a+2,\qquad x\ne a",
        "$t=4$", "$c=-2$ hoặc $c=1$", "$x=14$", "$t=6$",
        "không phải hai giá trị", "điều kiện cho từng biểu thức",
    ):
        check(required in markdown, f"authored result/qualification retained: {required}")

    if originals:
        sys.path.insert(0, str(ROOT / "tools"))
        from extract_algebraic_evaluation import ORIGINALS, selected, math_serials
        for relative, expected in ORIGINALS:
            full_path = ROOT.parent / relative
            check(sha256(full_path.read_bytes()).hexdigest() == expected, "pinned full source", "original")
            original = selected(full_path)
            check([n.get("id") for n in original.iter() if n.get("id")] == identities,
                  "full EN/ID ordered IDs/boundaries", "original")
            check(math_serials(original) == math_serials(tree), "all EN/ID math unchanged", "original")
            if "upstream-openstax" in relative:
                check(ET.tostring(original) == ET.tostring(tree), "full selected EN subtree", "original")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result = tests(originals="--originals" in sys.argv, details=True)
    print(f"PASS: {sum(result.values())} assertions; {result}")
