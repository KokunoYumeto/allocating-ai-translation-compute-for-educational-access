"""B006 integer arithmetic and actual-text checks, not linguistic approval."""
import re

from naming_checks import text_of

CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
TABLE_CASES = (
    ("eip-659", 843, 10, 5),
    ("eip-493", 23658, 100, 4),
    ("eip-379", 3978, 100, 4),
    ("eip-695", 147032, 1000, 4),
    ("eip-596", 29504, 1000, 4),
)
TRY_CASES = (
    ("fs-id1312230", "fs-id1347444", "fs-id1178888", 157, 10),
    ("fs-id2648829", "fs-id2210570", "fs-id1269556", 884, 10),
    ("fs-id1288049", "fs-id2133764", "fs-id1336744", 17852, 100),
    ("fs-id1153191", "fs-id1939348", "fs-id1344986", 4951, 100),
    ("fs-id3447872", "fs-id1756663", "fs-id1823220", 63921, 1000),
    ("fs-id1371038", "fs-id2276491", "fs-id2174049", 156437, 1000),
)
EN_PLACES = {10: "ten", 100: "hundred", 1000: "thousand",
             10000: "ten thousand", 100000: "hundred thousand", 1000000: "million"}
TE_NEAREST = {"పదులకు": 10, "వందలకు": 100, "వేలకు": 1000,
              "పది వేలకు": 10000, "వంద వేలకు": 100000}
TE_POSITION = {"పదుల": 10, "వందల": 100, "వేల": 1000,
               "పది వేల": 10000, "వంద వేల": 100000, "మిలియన్ల": 1000000}
PRACTICE_CASES = {
    "D01": (46082, 1000), "D02": (46082, 100),
    "D03": (245, 10), "D04": (2451, 100),
    "D05": (9995, 10), "D06": (99499, 1000),
    "R01": (73064, 1000), "R02": (73064, 100),
    "R03": (365, 10), "R04": (6752, 100),
    "R05": (99950, 100), "R06": (9949, 100),
}


def _require_nearest(text, place, localized=True):
    if localized:
        names = "|".join(re.escape(s) for s in sorted(TE_NEAREST, key=len, reverse=True))
        actual = [TE_NEAREST[s] for s in re.findall(r"దగ్గరి\s+(" + names + r")", text)]
    else:
        values = {v: k for k, v in EN_PLACES.items()}
        names = "|".join(re.escape(s) for s in sorted(values, key=len, reverse=True))
        actual = [values[s] for s in re.findall(r"nearest (" + names + r")\b", text)]
    assert actual and set(actual) == {place}, "Rounding target place changed"


def _require_position(text, place):
    names = "|".join(re.escape(s) for s in sorted(TE_POSITION, key=len, reverse=True))
    actual = [TE_POSITION[s] for s in re.findall(r"(" + names + r")\s+స్థాన", text)]
    assert actual and set(actual) == {place}, "Rounding selected position changed"


def round_whole_half_up(number, place_unit):
    """Nearest power-of-ten multiple for nonnegative integers; ties go up.

    Integer quotient/remainder avoids floating-point error and ties-to-even.
    """
    if type(number) is not int or number < 0:
        raise ValueError("A nonnegative integer is required")
    if type(place_unit) is not int or place_unit < 1:
        raise ValueError("A positive power-of-ten place unit is required")
    remaining = place_unit
    while remaining % 10 == 0:
        remaining //= 10
    if remaining != 1:
        raise ValueError("A positive power-of-ten place unit is required")
    quotient, remainder = divmod(number, place_unit)
    return (quotient + (2 * remainder >= place_unit)) * place_unit


def controlling_digit(number, place_unit):
    round_whole_half_up(number, place_unit)  # Same domain validation.
    return number // (place_unit // 10) % 10 if place_unit > 1 else 0


def _ids(root):
    nodes = [e for e in root.iter() if e.get("id")]
    result = {e.get("id"): e for e in nodes}
    assert len(result) == len(nodes), "Duplicate rounding ID"
    return result


def _node(ids, ident):
    assert ident in ids, "Missing rounding node: " + ident
    return ids[ident]


def _math_numbers(node):
    return [int((e.text or "").replace(",", "")) for e in node.iter(MATH + "mn")]


def _number_tokens(text):
    return [int(n.rstrip(",").replace(",", ""))
            for n in re.findall(r"(?<![\w,])[0-9][0-9,]*", text)]


def _require_international_commas(text):
    for raw in re.findall(r"(?<![\w,])[0-9][0-9,]*", text):
        token = raw.rstrip(",")
        if "," in token:
            assert token == f"{int(token.replace(',', '')):,}", "Rounding comma grouping changed: " + token


def validate_rounding_structure(root):
    """Retain the frozen section's known two-cell/three-declared-column shape."""
    assert root.get("id") == "fs-id2472737", "Wrong rounding section"
    assert len(list(root.iter())) == 462, "Rounding element count changed"
    ids = _ids(root)
    assert len(ids) == 104, "Rounding ID count changed"
    assert len(list(root.iter(MATH + "math"))) == 69, "Rounding MathML count changed"
    assert len(list(root.iter(CN + "image"))) == 23, "Rounding media count changed"
    tables = {e.get("id"): e for e in root.iter(CN + "table")}
    assert set(tables) == {c[0] for c in TABLE_CASES}, "Rounding tables changed"
    for ident, _, _, count in TABLE_CASES:
        group = tables[ident].find(CN + "tgroup")
        assert group is not None and group.get("cols") == "3", "Declared source columns changed: " + ident
        rows = group.findall(CN + "tbody/" + CN + "row")
        assert len(rows) == count and all(len(row) == 2 for row in rows), "Actual source columns changed: " + ident
    links = [e.get("url") for e in _node(ids, "fs-id3323694").iter(CN + "link")]
    assert links == ["https://www.openstax.org/l/24detplaceval",
                     "https://www.openstax.org/l/24numdigword"], "Source resource links changed"
    return ids


def _validate_rounding_cases(source, localized=False):
    """Recompute all seventeen cases from actual frozen source nodes.

    The two known erroneous raster alts are not taken as the source questions.
    """
    ids = validate_rounding_structure(source)
    population = _math_numbers(_node(ids, "fs-id1333125"))
    assert population == [2013, 19651127, 20, 20], "Population context changed"
    results = _math_numbers(_node(ids, "fs-id2368933"))
    assert results == [20, 19700000, 19650000], "Population outputs changed"
    if localized:
        population_text = text_of(_node(ids, "fs-id2368933"))
        for fragment in ["మిలియన్ల స్థానానికి", "వంద వేల స్థానానికి", "పది వేల స్థానానికి"]:
            assert fragment in population_text, "Population rounding place changed"
        assert re.search(r"వంద వేల స్థానానికి[^.]*19,700,000", population_text), "Population hundred-thousand mapping changed"
        assert re.search(r"పది వేల స్థానానికి[^.]*19,650,000", population_text), "Population ten-thousand mapping changed"
    for place, value in zip([1000000, 100000, 10000],
                            [results[0] * 1000000, results[1], results[2]]):
        assert round_whole_half_up(population[1], place) == value
    checked = 3
    for figure, number, expected_sequence in [
        ("CNX_BMath_Figure_01_01_019", 76, [76, 80, 70, 76, 80]),
        ("CNX_BMath_Figure_01_01_020", 72, [72, 70, 72, 70]),
    ]:
        caption = _node(ids, figure).find(CN + "caption")
        numbers = _math_numbers(caption)
        assert numbers == expected_sequence, "Number-line caption changed"
        _require_nearest(text_of(caption), 10, localized)
        assert round_whole_half_up(number, 10) == numbers[-1]
        checked += 1
    halfway = _math_numbers(_node(ids, "fs-id1384953"))
    assert halfway == [80, 75, 80]
    assert round_whole_half_up(halfway[1], 10) == halfway[-1]
    _require_nearest(text_of(_node(ids, "fs-id1384953")), 10, localized)
    checked += 1
    for question, expected in [("fs-id555970", [843]),
                               ("fs-id2351315", [23658, 3978]),
                               ("fs-id1471031", [147032, 29504])]:
        assert _math_numbers(_node(ids, question)) == expected, "Source worked input changed"
    for ident, number, place, _ in TABLE_CASES:
        table = _node(ids, ident)
        rows = list(table.iter(CN + "row"))
        final = text_of(rows[-1][-1])
        _require_international_commas(final)
        _require_nearest(final, place, localized)
        assert _number_tokens(final) == [number, round_whole_half_up(number, place)], "Source worked answer changed"
        if localized:
            first = 0 if ident == "eip-659" else 1
            _require_position(text_of(rows[first][0]), place)
            _require_nearest(table.get("aria-label", ""), place)
        checked += 1
    for _, question, answer, number, place in TRY_CASES:
        prompt = _node(ids, question)
        assert _math_numbers(prompt) == [number], "Source Try It number changed"
        _require_nearest(text_of(prompt), place, localized)
        assert text_of(_node(ids, answer)) == f"{round_whole_half_up(number, place):,}", "Source Try It answer changed"
        checked += 1
    assert checked == 17
    return checked


def validate_english_rounding_source(source):
    return _validate_rounding_cases(source, localized=False)


def validate_rounding_target(target):
    checked = _validate_rounding_cases(target, localized=True)
    ids = _ids(target)
    for question, place in [("fs-id555970", 10), ("fs-id1339512", 100),
                            ("fs-id2283895", 1000)]:
        _require_nearest(text_of(_node(ids, question)), place)
    # Answer coincidence must not hide the two source-alt target-place errors.
    for media, place, number in [("eip-id1168289428689", 100, 3978),
                                 ("eip-id1168288313851", 1000, 29504)]:
        description = _node(ids, media).get("alt", "")
        _require_nearest(description, place)
        actual = _number_tokens(description)
        assert actual[0] == number and actual[-1] == round_whole_half_up(number, place), "Rounding corrected alt numbers changed"
        digit = number // place % 10
        higher = number // (place * 10) % 10
        lower = [int(s) for s in str(number % place).zfill(len(str(place)) - 1)]
        assert actual == [number, digit, 1, digit, 1, 10, 0, higher, 1,
                          *lower, round_whole_half_up(number, place)], "Rounding corrected alt carry/digits changed"
    rows_with_decision = {"eip-659": 2, "eip-493": 2, "eip-379": 3,
                          "eip-695": 2, "eip-596": 3}
    for ident, number, place, _ in TABLE_CASES:
        rows = list(_node(ids, ident).iter(CN + "row"))
        decision = _number_tokens(text_of(rows[rows_with_decision[ident]][0]))
        assert decision and decision[0] == controlling_digit(number, place), "Rounding controlling digit changed: " + ident
    boundary = _node(ids, "fs-id1545266")
    assert _math_numbers(boundary) == [5, 5], "Rounding boundary number changed"
    assert "వెంటనే కుడివైపున ఉన్న అంకె" in text_of(boundary), "Rounding adjacent-digit rule changed"
    assert "దానికన్నా చిన్న అంకె" in text_of(boundary), "Rounding down boundary changed"
    assert "దానికి సమానమైన లేదా పెద్ద అంకె" in text_of(boundary), "Rounding tie boundary changed"
    carry = _node(ids, "fs-id2486248").find(CN + "item")
    assert _number_tokens(text_of(carry)) == [1, 9, 0, 1, 9], "Rounding carry procedure changed"
    first_step = _node(ids, "eip-id1168287215567").find(CN + "item")
    assert "9 అయి, పైకి సవరించవలసి" in text_of(first_step), "Rounding carry condition changed"
    return checked


def _integer_expression(expression):
    parts = re.split(r"\s*([+−-])\s*", expression.strip())
    def product(term):
        result = 1
        for token in term.split("×"):
            result *= int(token.strip().replace(",", ""))
        return result
    total = product(parts[0])
    for operator, term in zip(parts[1::2], parts[2::2]):
        total += product(term) if operator == "+" else -product(term)
    return total


def verify_rounding_arithmetic(bridge, expected=24):
    number = r"[0-9][0-9,]*"
    expression = number + r"(?:\s*[+−×-]\s*" + number + r")*"
    pattern = re.compile(r"(?<![\w,])" + expression + r"(?:\s*=\s*" + expression + r")+")
    found = []
    for node in bridge.iter():
        if node.tag.rsplit("}", 1)[-1] not in {"p", "li", "dd"}:
            continue
        for match in pattern.finditer(text_of(node)):
            equation = match.group()
            values = [_integer_expression(side) for side in equation.split("=")]
            assert len(set(values)) == 1, "Incorrect rounding equality: " + equation
            found.append(equation)
    assert len(found) == expected, "Missing/extra rounding arithmetic"
    return len(found)


def _solution_digits_and_answer(node, number, place):
    text = text_of(node)
    target_digit, neighbor = number // place % 10, controlling_digit(number, place)
    assert _number_tokens(text)[:2] == [target_digit, neighbor], "Bridge target/controlling digit changed: " + node.get("id", "")
    positions = {**TE_POSITION, "ఒకట్ల": 1}
    names = "|".join(re.escape(s) for s in sorted(positions, key=len, reverse=True))
    labels = [positions[s] for s in re.findall(r"(" + names + r")\s+(?:స్థాన\S*|అంకె)", text)]
    assert labels[:2] == [place, place // 10], "Bridge target/neighbor place changed: " + node.get("id", "")
    answer = round_whole_half_up(number, place)
    prefixes = ["భర్తీ చేస్తే", "ఫలితం", "పైకి సవరించి", "నియమంతో", "రాస్తే",
                "దగ్గరిది", "పెద్ద గుణిజం", "జవాబు పూర్తి విలువ", "దగ్గరి పది",
                "దగ్గరి వంద గుణిజం", "దగ్గరి వెయ్యి గుణిజం"]
    pattern = "(?:" + "|".join(re.escape(s) for s in prefixes) + r")\s+([0-9][0-9,]*)"
    stated = [s.rstrip(",") for s in re.findall(pattern, text)]
    assert stated and all(s == f"{answer:,}" for s in stated), "Bridge rounded answer changed: " + node.get("id", "")
    return text


def _require_distance_equations(text, number, place):
    lower = number // place * place
    upper = lower + place
    for fragment in [f"{number:,} − {lower:,} = {number-lower:,}",
                     f"{upper:,} − {number:,} = {upper-number:,}"]:
        assert fragment in text, "Bridge distance equation changed: " + fragment


def _require_link(node, destination):
    assert any(e.tag.rsplit("}", 1)[-1] == "a" and e.get("href") == "#" + destination
               for e in node.iter()), "Rounding solution link changed: " + destination


def _paragraphs_after(root, heading_id):
    children = list(root)
    index = next(i for i, node in enumerate(children) if node.get("id") == heading_id)
    paragraphs = []
    for node in children[index + 1:]:
        if node.tag.rsplit("}", 1)[-1] != "p":
            break
        paragraphs.append(node)
    return paragraphs


def validate_rounding_bridge(bridge):
    ids = _ids(bridge)
    _require_international_commas(text_of(bridge))
    for case, (number, place) in PRACTICE_CASES.items():
        question = _node(ids, "B006-" + case)
        prompt = text_of(question)
        assert _number_tokens(prompt)[0] == number, "Bridge practice number changed: " + case
        _require_nearest(prompt, place)
        solution = _node(ids, "B006-S-" + case)
        text = _solution_digits_and_answer(solution, number, place)
        _require_link(solution, "B006-" + case)
        lower, upper = number // place * place, (number // place + 1) * place
        distance_low, distance_high = number - lower, upper - number
        if case in {"D03", "D04", "R03", "R04"}:
            _require_distance_equations(text, number, place)
        else:
            assert f"{lower:,}, {upper:,}" in text, "Bridge neighboring multiples changed"
            if case == "D05":
                assert distance_low == distance_high == 5 and "ఐదు దూరంలో" in text, "Bridge all-nine midpoint changed"
                assert f"{lower:,} + {place:,} = {upper:,}" in text, "Bridge all-nine carry changed"
                assert "పది వేల స్థానంలో కొత్త 1" in text, "Bridge new leading carry digit changed"
            elif case == "R05":
                assert distance_low == distance_high == 50 and "దూరం 50" in text, "Bridge all-nine midpoint changed"
                assert f"{lower:,} + {place:,} = {upper:,}" in text, "Bridge all-nine carry changed"
                assert "వంద వేల స్థానంలో కొత్త 1" in text, "Bridge new leading carry digit changed"
            else:
                distances = re.search(r"దూరాలు\s+([0-9,]+),\s+([0-9,]+)", text)
                assert distances and [int(x.replace(",", "")) for x in distances.groups()] == [distance_low, distance_high], "Bridge distance pair changed"
        if case in {"D06", "R06"}:
            assert "బదిలీ లేదు" in text and controlling_digit(number, place) < 5, "Bridge no-carry condition changed"
        if case in {"D04", "R04"}:
            assert "కాదు" in text and f"{(lower+upper)//2:,}" in text, "Bridge above-midpoint explanation changed"

    for exercise, _, _, number, place in TRY_CASES:
        answer = _node(ids, "B006-S-" + exercise)
        text = _solution_digits_and_answer(answer, number, place)
        _require_link(answer, exercise)
        parent = next(e for e in bridge.iter() if answer in list(e))
        summary = next(e for e in parent if e.tag.rsplit("}", 1)[-1] == "summary")
        assert _number_tokens(text_of(summary)) == [number], "Bridge source summary number changed"
        _require_nearest(text_of(summary), place)
        _require_distance_equations(text, number, place)

    guide = " ".join(text_of(p) for p in _paragraphs_after(bridge, "B006-place-guide"))
    for number, place in [(3978, 100), (29504, 1000)]:
        clause = re.search(re.escape(f"{number:,}") + r"[^.]*", guide)
        assert clause, "Missing source target-place comparison"
        _require_nearest(clause.group(), place)

    exact = text_of(_node(ids, "B006-zero-exact"))
    pattern = r"([0-9,]+) ను దగ్గరి (పదులకు|వేలకు) సవరించినా ([0-9,]+) గానే"
    actual = [(int(n.replace(",", "")), TE_NEAREST[p], int(a.replace(",", "")))
              for n, p, a in re.findall(pattern, exact)]
    assert actual == [(0, 10, 0), (4000, 1000, 4000)], "Exact-multiple rounding changed"
    assert all(round_whole_half_up(n, p) == a for n, p, a in actual)

    once = text_of(_node(ids, "B006-round-once"))
    start = 149
    first = round_whole_half_up(start, 10)
    assert _number_tokens(once) == [start, round_whole_half_up(start, 100), first,
                                     round_whole_half_up(first, 100)], "Direct/double-rounding values changed"
    assert re.findall(r"(పదులకు|వందలకు)", once) == ["వందలకు", "పదులకు", "వందలకు"], "Direct/double-rounding places changed"
    scale = text_of(_node(ids, "B006-line-scale"))
    values = _number_tokens(scale)
    assert values == [70, 71, 72, 200, 210, 220], "Number-line labels changed"
    assert [b-a for a, b in zip(values[:2], values[1:3])] == [1, 1]
    assert [b-a for a, b in zip(values[3:5], values[4:6])] == [10, 10]
    return verify_rounding_arithmetic(bridge)


def validate_b006(target, bridge):
    """Accept actual ElementTree roots; return bounded checked-case counts."""
    return {"canonical_cases": validate_rounding_target(target),
            "entry_recheck_cases": len(PRACTICE_CASES),
            "source_bridge_solutions": len(TRY_CASES),
            "bridge_equalities": validate_rounding_bridge(bridge)}
