"""Original finite illustrations; the circle argument in the reader is algebraic."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"


def tests():
    def is_function(pairs):
        return all(len({b for a, b in pairs if a == x}) == 1 for x, _ in pairs)

    def injective(pairs):
        return is_function(pairs) and is_function([(b, a) for a, b in pairs])

    diagram_a = [("p", "m"), ("q", "n"), ("r", "n")]
    diagram_b = [("p", "x"), ("q", "y"), ("r", "z")]
    diagram_c = [("p", "x"), ("q", "y"), ("q", "z")]
    assert is_function(diagram_a)
    assert not injective(diagram_a)
    assert injective(diagram_b)
    assert not is_function(diagram_c)
    assert not injective(diagram_c)
    ns = {"c": "http://cnx.rice.edu/cnxml"}
    tree = ET.parse(ROOT / "sources/m49301-one-to-one-source.cnxml")
    rows = tree.findall('.//c:table[@id="Table_01_01_13"]/c:tgroup/c:tbody/c:row', ns)
    grades = [tuple("".join(e.itertext()) for e in row.findall("c:entry", ns)) for row in rows]
    assert grades == [("A", "4.0"), ("B", "3.0"), ("C", "2.0"), ("D", "1.0")]
    assert injective(grades)
    balances = [("account-A", 50), ("account-B", 50)]
    assert is_function(balances)
    assert not injective(balances)
    assert not is_function([(b, a) for a, b in balances])
    assert len(range(101)) == 101 and 101 > 5
    # The positive common factor pi does not affect equality of scaled areas.
    assert injective([(r, r * r) for r in (1, 2, 3, 4)])
    assert not injective([(-1, 1), (1, 1)])
    source_checks = 0
    original_path = ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml"
    if original_path.exists():
        original_tree = ET.parse(original_path)
        original = original_tree.find(f".//{CN}section[@id='fs-id1165135422920']")
        excerpt = tree.getroot()
        assert excerpt.tag == CN + "section" and excerpt.get("id") == "fs-id1165135422920"
        def signature(node):
            return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
                    tuple((signature(child), (child.tail or "").strip()) for child in node))
        assert signature(excerpt) == signature(original)
        parent = next(node for node in original_tree.iter() if original in list(node))
        siblings = list(parent)
        assert siblings[siblings.index(original) + 1].get("id") == "fs-id1165135435781"
        source_checks = 3
    return 13 + source_checks


if __name__ == "__main__":
    print(f"PASS: {tests()} source-preservation/one-to-one checks")
