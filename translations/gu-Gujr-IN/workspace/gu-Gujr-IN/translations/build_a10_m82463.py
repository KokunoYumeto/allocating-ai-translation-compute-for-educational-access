"""Build the complete source-bound Gujarati translation of A10 m82463."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82463/index.cnxml"
MAP = HERE / "a10-m82463.slots.json"
TSV = HERE / "a10-m82463.gu.tsv"
OUT = HERE / "a10-m82463.gu.cnxml"
ERRATA = HERE / "a10-m82463-errata.gu.json"
SHA = "b6345a5a6a99108f9d32d6518445a4ae70a6b0c54a258021dffc6f2b77b8278a"
CNX = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
MD = "http://cnx.rice.edu/mdml"


def slots(root):
    for elem in root.iter():
        local = elem.tag.rsplit("}", 1)[-1]
        namespace = elem.tag.split("}", 1)[0][1:] if elem.tag.startswith("{") else ""
        if local in {"content-id", "uuid"}:
            continue
        for attr in ("text", "tail"):
            value = getattr(elem, attr)
            if value and re.search(r"[A-Za-z]", value) and not (
                namespace == MATH and attr == "text" and local != "mtext"
            ):
                yield elem, attr, value.strip()
        for attr in ("alt", "summary", "aria-label", "title"):
            value = elem.get(attr)
            if value and re.search(r"[A-Za-z]", value):
                yield elem, "@" + attr, value.strip()


def polish(root, source):
    """Apply explicit source-ID-bound Gujarati order fixes without moving math."""
    c = "{" + CNX + "}"
    m = "{" + MATH + "}"
    by_id = {e.get("id"): e for e in root.iter() if e.get("id")}
    # Retain source single-letter variables even when they are italic prose nodes.
    for a, b in zip(source.iter(), root.iter()):
        if a.tag == c + "emphasis" and a.get("effect") == "italics" and re.fullmatch(r"[A-Za-z]", (a.text or "").strip()):
            b.text = a.text
    def flat(elem):
        return " ".join(" ".join(elem.itertext()).split())
    # Recast recurring solution-verification sentences around unchanged math.
    for a, b in zip(source.iter(), root.iter()):
        statement = flat(a)
        maths = [x for x in list(b) if x.tag == m + "math"]
        if statement.startswith("Determine whether ") and " is a solution of " in statement and len(maths) == 2:
            b.text = "આપેલું મૂલ્ય "
            maths[0].tail = " સમીકરણ "
            maths[1].tail = "નો ઉકેલ છે કે નહીં તે નક્કી કરો."
        elif statement.startswith("Is ") and " a solution of " in statement and len(maths) == 2:
            b.text = "શું "
            maths[0].tail = " એ સમીકરણ "
            maths[1].tail = "નો ઉકેલ છે?"
        elif statement.startswith("Since ") and " results in a true equation" in statement and len(maths) == 3:
            b.text = "કેમ કે "
            maths[0].tail = " મૂકવાથી સાચું સમીકરણ મળે છે—4 ખરેખર 4ની બરાબર છે—તેથી "
            maths[1].tail = " એ સમીકરણ "
            maths[2].tail = "નો ઉકેલ છે."
        elif statement.startswith("The solution to ") and " is " in statement and len(maths) == 2:
            b.text = "સમીકરણ "
            maths[0].tail = "નો ઉકેલ "
            maths[1].tail = " છે."
    # Gujarati places the quantity before comparative phrases. Keep every
    # source math node in place and recast only surrounding text/tails.
    e = by_id["fs-idm323101440"]
    e.text = "બીજગણિતમાં ફેરવો: “"
    e[0].tail = " કરતાં 5 ઓછું.”"
    e = by_id["fs-id1168345724247"]
    e.text = e.text.replace(" આ પ્રક્રિયાનું ચિત્ર જુઓ: ", " આ પ્રક્રિયાનું ચિત્ર જુઓ ")
    e[0].tail = "."
    e = by_id["fs-id1168345384591"]
    e.text = "આ પરિસ્થિતિને કયું બીજગણિતીય સમીકરણ અનુરૂપ હશે? "
    e[0].tail = "માં કાર્યસ્થળની દરેક બાજુ એક પદાવલી દર્શાવે છે અને વચ્ચેની રેખા સમાનતાચિહ્નનું સ્થાન લે છે. પરબીડિયાની સામગ્રીને આપણે "
    e[1].tail = " કહીએ છીએ."
    e = by_id["fs-id1169752842292"]
    e.text = "“સમાનતાનો બાદબાકીનો ગુણધર્મ” નામની હસ્તચાલિત ગણિત પ્રવૃત્તિ કરવાથી સમીકરણો ઉકેલવામાં આ ગુણધર્મ કેવી રીતે વપરાય તેની સારી સમજ મળશે: "
    e[0].tail = "."
    e = by_id["fs-id1168345287978"]
    e.text = ""
    e[0].tail = "ને એકલું રાખવા, સરવાળામાં ઉમેરેલા 37ની અસર દૂર કરવા આપણે સમાનતાનો બાદબાકીનો ગુણધર્મ વાપરીશું."
    e = by_id["fs-id1168345539173"]
    e.text = "કેમ કે "
    e[0].tail = " મૂકવાથી "
    e[1].tail = " સાચું વિધાન મળે છે, તેથી આપણને આ સમીકરણનો ઉકેલ મળ્યો છે."
    e = by_id["fs-id1168345407292"]
    e[0].tail = ". ચલમાંથી કોઈ સંખ્યા બાદ કરેલી હોય તેવાં સમીકરણોને ઉકેલવા આપણે સમીકરણોનો બીજો ગુણધર્મ વાપરીએ છીએ. ચલને એકલું રાખવા માટે બાદબાકીની અસર દૂર કરવી છે, તેથી બંને બાજુએ તે સંખ્યા ઉમેરીશું. આપણે આનો ઉપયોગ કરીએ છીએ: "
    e = by_id["fs-id1168345550229"]
    e.text = "અગાઉના ઉદાહરણ "
    e[0].tail = "માં "
    e[1].tail = "માં 37 ઉમેરેલું હતું, તેથી સરવાળાની અસર દૂર કરવા આપણે 37 બાદ કર્યું. આગળના ઉદાહરણ "
    e[2].tail = "માં બાદબાકીની અસર દૂર કરવા આપણે આનો ઉપયોગ કરવો પડશે: "

    # Sentence-to-equation examples: source English order is comparative-first.
    for owner, after in {
        "fs-id1168345301577": " કરતાં અગિયાર વધુ એ 54ની બરાબર છે.",
        "fs-id1168341952145": " કરતાં દસ વધુ એ 41ની બરાબર છે.",
        "fs-id1168341852234": " કરતાં બાર ઓછું એ 51ની બરાબર છે.",
    }.items():
        e = by_id[owner]
        e.text = "ફેરવો અને ઉકેલો: "
        e[0].tail = after
    for owner in ("fs-id1168345634702", "fs-id1168345452400"):
        e = by_id[owner]
        assert len(e) == 3
        e.text = "ફેરવો અને ઉકેલો: "
        e[0].tail = " અને "
        e[1].tail = "નો તફાવત "
        e[2].tail = " છે."
    e = by_id["fs-id1168345276412"]
    e.text = "ફેરવો અને ઉકેલો: "
    e[0].tail = " અને "
    e[1].tail = "નો તફાવત 14 છે."
    e = by_id["fs-id1168345292286"]
    e.text = "પહેલાં પ્રશ્નને માત્ર એક વાક્યમાં ફરી કહીશું, પછી ચલ નક્કી કરીશું અને વાક્યને સમીકરણમાં ફેરવીને ઉકેલીશું. ચલ માટે એવો અક્ષર પસંદ કરો જે તમને શોધવાની રાશિ યાદ કરાવે. ઉદાહરણ તરીકે, સિક્કાઓના પ્રશ્નમાં ક્વૉર્ટરની સંખ્યા શોધવાની હોય તો તમે "
    e[0].tail = " વાપરી શકો."

    # Practice sentence translations use the same fixed math-node order.
    e = by_id["fs-id1168341967944"]
    e.text = ""
    e[0].tail = " કરતાં નવ વધુ એ 52ની બરાબર છે."
    for owner, relation, result in (
        ("fs-id1168345509827", "નો સરવાળો", "23"),
        ("fs-id1168345556307", "નો સરવાળો", "40"),
    ):
        e = by_id[owner]
        e.text = ""
        e[0].tail = " અને "
        e[1].tail = f"{relation} {result} છે."
    for owner, phrase in (
        ("fs-id1168345669226", " કરતાં દસ ઓછું એ "),
        ("fs-id1168341906102", " કરતાં ત્રણ ઓછું એ "),
    ):
        e = by_id[owner]
        e.text = ""
        e[0].tail = phrase
        e[1].tail = " છે."
    e = by_id["fs-id1168341852972"]
    e.text = ""
    e[0].tail = " કરતાં બાર વધુ એ 67ની બરાબર છે."
    for owner, noun in (
        ("fs-id1168341853012", "નો તફાવત"),
        ("fs-id1168345516500", "નો તફાવત"),
    ):
        e = by_id[owner]
        e.text = ""
        e[0].tail = f"{noun} " + ("107 છે." if owner.endswith("53012") else "602 છે.")
    for owner, noun in (
        ("fs-id1168345429064", "નો તફાવત"),
        ("fs-id1168345499239", "નો તફાવત"),
        ("fs-id1168345499305", "નો સરવાળો"),
        ("fs-id1168345545991", "નો સરવાળો"),
    ):
        e = by_id[owner]
        assert len(e) == 3
        e.text = ""
        e[0].tail = " અને "
        e[1].tail = noun + " "
        e[2].tail = " છે."

    # Recast the two mixed-number applications around unchanged MathML.
    e = by_id["fs-id1168341967642"]
    assert len(e) == 5
    e[0].tail = " મિગેલને "
    e[1].tail = " ઇંચના સ્ક્રૂ માટે કાણું પાડવું છે. કાણું સ્ક્રૂ કરતાં "
    e[2].tail = " ઇંચ નાનું હોવું જોઈએ. "
    e[3].tail = " તેણે પાડવાના કાણાનું માપ દર્શાવે એમ લો. કાણાનું માપ શોધવા સમીકરણ "
    e[4].tail = " ઉકેલો."
    e = by_id["fs-id1168341967722"]
    assert len(e) == 5
    e[0].tail = " કેલ્સીને કૂકીની વાનગી માટે "
    e[1].tail = " કપ ખાંડ જોઈએ. તેની પાસે માત્ર "
    e[2].tail = " કપ ખાંડ છે અને બાકીની તે પાડોશી પાસેથી ઉછીની લેશે. "
    e[3].tail = " તે ઉછીની લેશે એટલી ખાંડ દર્શાવે એમ લો. તેણે કેટલી ખાંડ માગવી તે શોધવા સમીકરણ "
    e[4].tail = " ઉકેલો."
    e = by_id["fs-id1168342171183"]
    e.text = "શું "
    e[0].tail = " એ સમીકરણ "
    e[1].tail = "નો ઉકેલ છે? તમે કેવી રીતે જાણો છો?"
    # Make the seven-step application table read naturally around its retained
    # variable and equations.
    e = by_id["eip-249"]
    entries = [x for x in e.iter(c + "entry")]
    variable_entry = next(x for x in entries if (x.text or "").strip() == "આ કિંમત લો:")
    variable_entry.text = "કારની સૂચિત કિંમત દર્શાવવા "
    variable_entry.find(m + "math").tail = " લો."
    # Keyed errata may correct translated descriptions/prose while source math and
    # identifiers stay unchanged. Empty entries are valid before actual-image review.
    if ERRATA.exists():
        data = json.loads(ERRATA.read_text(encoding="utf-8"))
        for owner, entry in data.get("entries", {}).items():
            elem = by_id[owner]
            for attr in ("alt", "summary", "aria-label", "title"):
                key = attr + "_gu"
                if key in entry:
                    elem.set(attr, entry[key])
            for old, new in entry.get("text_replacements_gu", {}).items():
                matches = 0
                for child in elem.iter():
                    for attr in ("text", "tail"):
                        value = getattr(child, attr)
                        if value and old in value:
                            setattr(child, attr, value.replace(old, new))
                            matches += 1
                assert matches == 1, (owner, old, matches)


def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SHA
    tree = ET.parse(SRC)
    root = tree.getroot()
    source = ET.parse(SRC).getroot()
    unique = list(dict.fromkeys(value for _, _, value in slots(root)))
    mapping = json.loads(MAP.read_text(encoding="utf-8"))
    assert mapping["source_sha256"] == SHA
    assert [row["en"] for row in mapping["slots"]] == unique
    authored = {}
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        number, gu = line.split("\t", 1)
        number = int(number)
        assert number not in authored
        authored[number] = gu
    assert set(authored) == set(range(len(unique)))
    translated = {row["en"]: authored[row["n"]] for row in mapping["slots"]}
    for elem, attr, en in slots(root):
        gu = translated[en]
        if attr.startswith("@"):
            elem.set(attr[1:], gu)
        else:
            old = getattr(elem, attr)
            setattr(elem, attr, old[: len(old) - len(old.lstrip())] + gu + old[len(old.rstrip()) :])
    polish(root, source)
    root.set("{http://www.w3.org/XML/1998/namespace}lang", "gu-Gujr-IN")
    ET.register_namespace("", CNX)
    ET.register_namespace("m", MATH)
    ET.register_namespace("md", MD)
    tree.write(OUT, encoding="utf-8", xml_declaration=True)
    print(f"Translated {len(unique)} slots")


if __name__ == "__main__":
    main()
