"""Original checks of all seven source/translated tables and source answers."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
EXPECTED = {
    "Table_01_01_03": [(1, 31), (2, 28), (3, 31), (4, 30), (5, 31), (6, 30),
                         (7, 31), (8, 31), (9, 30), (10, 31), (11, 30), (12, 31)],
    "Table_01_01_04": [(1, 8), (2, 6), (3, 7), (4, 6), (5, 8)],
    "Table_01_01_05": [(5, 40), (5, 42), (6, 44), (7, 47), (8, 50), (9, 52), (10, 54)],
    "Table_01_01_06": [(2, 1), (5, 3), (8, 6)],
    "Table_01_01_07": [(-3, 5), (0, 1), (4, 5)],
    "Table_01_01_08": [(1, 0), (5, 2), (5, 4)],
    "Table_01_01_09": [(1, 10), (2, 100), (3, 1000)],
}


def integer(text):
    # Source table 7 uses an en dash; math uses the mathematical minus sign.
    return int(text.strip().replace("−", "-").replace("–", "-"))


def is_function(pairs):
    outputs = {}
    for x, y in pairs:
        outputs.setdefault(x, set()).add(y)
    return all(len(values) == 1 for values in outputs.values())


def tests():
    tree = ET.parse(ROOT / "sources/m49301-tables-source.cnxml")
    by_id = {node.get("id"): node for node in tree.iter() if node.get("id")}
    markdown = (ROOT / "translation/A30-U003-tables.vi.md").read_text(encoding="utf-8")
    count = 0

    def check(condition, message):
        nonlocal count
        assert condition, message
        count += 1

    for identity, expected in EXPECTED.items():
        rows = [["".join(cell.itertext()) for cell in row.findall(CN + "entry")]
                for row in by_id[identity].findall(f"{CN}tgroup/{CN}tbody/{CN}row")]
        if identity in ("Table_01_01_03", "Table_01_01_04", "Table_01_01_05"):
            source_pairs = list(zip(*(list(map(integer, row[1:])) for row in rows)))
        else:
            source_pairs = [tuple(map(integer, row)) for row in rows]
        check(source_pairs == expected, f"source table changed: {identity}")
        block = re.search(r"^::: \{#" + re.escape(identity) + r"\}\n(.*?)^:::$",
                          markdown, flags=re.MULTILINE | re.DOTALL)
        assert block, identity
        # Only numeric data rows, not headings or alignment separators.
        translated_pairs = [tuple(map(integer, row)) for row in re.findall(
            r"^\|\s*([−–-]?\d+)\s*\|\s*([−–-]?\d+)\s*\|$", block.group(1), re.MULTILINE)]
        check(translated_pairs == expected, f"translated pairs differ: {identity}")
        check(is_function(source_pairs) == (identity not in ("Table_01_01_05", "Table_01_01_08")),
              f"function classification: {identity}")

    # Verify the six equalities in the source worked solution, using its tables.
    for identity, argument, result in (("Table_01_01_06", 2, 1), ("Table_01_01_06", 5, 3),
                                      ("Table_01_01_06", 8, 6), ("Table_01_01_07", -3, 5),
                                      ("Table_01_01_07", 0, 1), ("Table_01_01_07", 4, 5)):
        check(dict(EXPECTED[identity])[argument] == result, f"source equality: {identity}/{argument}")
    check(sum(value for _, value in EXPECTED["Table_01_01_03"]) == 365, "non-leap year total")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} source/table/answer checks")
