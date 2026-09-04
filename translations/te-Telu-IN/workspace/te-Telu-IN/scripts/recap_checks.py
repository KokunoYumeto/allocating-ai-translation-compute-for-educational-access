"""Check actual B007 worked examples and routing; not linguistic approval."""
import re
from naming_checks import english_name, text_of
from rounding_checks import round_whole_half_up, verify_rounding_arithmetic, _number_tokens


def validate_b007(target, bridge):
    assert target.get("id") == "fs-id2296006"
    assert len(list(target.iter())) == 24
    ids = {e.get("id"): e for e in bridge.iter() if e.get("id")}
    assert len(ids) == 12
    names = [text_of(e) for e in bridge.iter()
             if e.tag.endswith("}span") and e.get("lang") == "en"]
    assert names == [english_name(5278194), english_name(6004020)], "Recap English name changed"
    for ident, expression in {
        "B007-value-example": "5 × 1,000,000 + 278 × 1,000 + 194 = 5,278,194",
        "B007-zero-value": "6 × 1,000,000 + 4 × 1,000 + 20 = 6,004,020",
    }.items():
        assert expression in text_of(ids[ident]), "Recap expansion changed"
    assert "5 | 278 | 194" in text_of(ids["B007-worked-chart"])
    assert "6 | 004 | 020" in text_of(ids["B007-worked-zero"]), "Zero padding changed"
    number = 5278194
    hundreds = round_whole_half_up(number, 100)
    thousands = round_whole_half_up(number, 1000)
    for ident, nearest, numbers in [
        ("B007-round-hundreds", "వందలకు", [number, 1, 9, 1, 2, hundreds,
          number, 5278100, 94, hundreds, number, 6]),
        ("B007-round-thousands", "వేలకు", [number, 8, 1, 5, 8, thousands,
          number, thousands, 194, 5279000, number, 806]),
    ]:
        paragraph = text_of(ids[ident])
        assert re.findall(r"దగ్గరి\s+(వందలకు|వేలకు)", paragraph) == [nearest], "Recap target changed"
        assert _number_tokens(paragraph) == numbers, "Recap digits, answer or distances changed"
    expected_links = {"#eip-id1170196618448"}
    for unit in ("003", "004", "005", "006"):
        support = "place-guide" if unit == "006" else "K1"
        expected_links |= {f"TE-B{unit}.html#B{unit}-{support}", f"TE-B{unit}.html#B{unit}-recheck"}
    links = [e.get("href") for e in bridge.iter() if e.get("href")]
    assert len(links) == 9 and set(links) == expected_links, "Recap skill routing changed"
    assert verify_rounding_arithmetic(bridge, expected=7) == 7
    return {"english_names": 2, "rounding_cases": 2, "equalities": 7, "links": 9}
