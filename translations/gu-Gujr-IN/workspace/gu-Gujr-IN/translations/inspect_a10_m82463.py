"""Write complete source/Indonesian/Gujarati paired reading records for m82463."""
from pathlib import Path
import hashlib
import json
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REVIEWS = HERE.parent / "reviews"
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82463/index.cnxml"
INDO = ROOT / "downloads/gu-Gujr-IN/a10-release/source/translated/modules/m82463/index.cnxml"
GU = HERE / "a10-m82463.gu.cnxml"
PROSE = REVIEWS / "a10-m82463-paired-prose.json"
EXERCISES = REVIEWS / "a10-m82463-paired-exercises.json"


def flat(elem):
    return " ".join(" ".join(elem.itertext()).split())


def owner_id(elem):
    cursor = elem
    while cursor is not None:
        if cursor.get("id"):
            return cursor.get("id")
        cursor = cursor.getparent()
    return None


def main():
    roots = [etree.parse(str(x)).getroot() for x in (SRC, INDO, GU)]
    elems = [list(x.iter()) for x in roots]
    assert all(len(x) == 3249 for x in elems)
    assert all(
        [(etree.QName(e).namespace, etree.QName(e).localname) for e in x]
        == [(etree.QName(e).namespace, etree.QName(e).localname) for e in elems[0]]
        for x in elems[1:]
    )
    prose = []
    for index, triple in enumerate(zip(*elems)):
        local = etree.QName(triple[0]).localname
        if local in {"para", "title", "caption", "note", "definition"}:
            prose.append(
                {
                    "element_index": index,
                    "element": local,
                    "id": owner_id(triple[0]),
                    "source": flat(triple[0]),
                    "indonesian": flat(triple[1]),
                    "gujarati": flat(triple[2]),
                }
            )
    ex = [[e for e in x if etree.QName(e).localname == "exercise"] for x in elems]
    assert all(len(x) == 116 for x in ex)
    exercises = []
    for number, triple in enumerate(zip(*ex), 1):
        solutions = [[e for e in x.iter() if etree.QName(e).localname == "solution"] for x in triple]
        assert len(solutions[0]) == len(solutions[1]) == len(solutions[2])
        exercises.append(
            {
                "number": number,
                "source_exercise": triple[0].get("id"),
                "source": flat(triple[0]),
                "indonesian": flat(triple[1]),
                "gujarati": flat(triple[2]),
                "source_solution_count": len(solutions[0]),
                "source_solutions": [flat(x) for x in solutions[0]],
                "gujarati_solutions": [flat(x) for x in solutions[2]],
            }
        )
    PROSE.write_text(json.dumps(prose, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    EXERCISES.write_text(json.dumps(exercises, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prose blocks: {len(prose)} Exercises: {len(exercises)}")


if __name__ == "__main__":
    main()
