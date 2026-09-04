"""Recreate the reviewed source-faithful excerpts from pinned translation inputs."""
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "gu-Gujr-IN"
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
ET.register_namespace("", C)
ET.register_namespace("m", M)


def slots(section):
    for element in section.iter():
        for field in ("text", "tail"):
            value = getattr(element, field)
            if value and value.strip() and any(c.isalpha() for c in value):
                yield element, field


def prepare():
    data = json.loads((LANG / "translations/source-slots.gu.json").read_text(encoding="utf-8"))
    src = ROOT / "downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml"
    assert hashlib.sha256(src.read_bytes()).hexdigest() == "396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b"
    source = ET.parse(src).getroot()
    section = copy.deepcopy(next(e for e in source.iter() if e.get("id") == data["a00_section"]))
    positions = list(slots(section))
    assert len(positions) == len(data["a00_slots"]) == 52
    for (element, field), target in zip(positions, data["a00_slots"]):
        setattr(element, field, target)
    # Gujarati requires a sentence-final verb after the term; the English tail
    # was punctuation-only, so it is not one of the alphabetic text slots.
    next(e for e in section.iter() if e.get('id')=='term-00005').tail = ' કહે છે.'
    # Localized redraw; same source figure ID and 0..6 geometry. No source image omitted silently.
    for media in section.iter(f"{{{C}}}media"):
        media.set("alt", data["number_line_alt"])
    for image in section.iter(f"{{{C}}}image"):
        image.set("src", "../assets/number-line.svg")
        image.set("mime-type", "image/svg+xml")
    doc = ET.Element(f"{{{C}}}document", {"{http://www.w3.org/XML/1998/namespace}lang": "gu-Gujr-IN"})
    ET.SubElement(doc, f"{{{C}}}title").text = "પૂર્ણ સંખ્યાઓનો પરિચય: ગણતરીની સંખ્યાઓ અને પૂર્ણ સંખ્યાઓ"
    ET.SubElement(doc, f"{{{C}}}content").append(section)
    ET.ElementTree(doc).write(LANG / "translations/a00-m81243-part01.gu.cnxml", encoding="utf-8", xml_declaration=True)
    a10 = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82452/index.cnxml"
    assert hashlib.sha256(a10.read_bytes()).hexdigest() == "0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310"
    ex = copy.deepcopy(next(e for e in ET.parse(a10).getroot().iter() if e.get("id") == data["a10_exercise"]))
    solution = ex.find(f"{{{C}}}solution/{{{C}}}para")
    for span, term in zip(solution, data["a10_solution_terms"]):
        span.tail = " " + term + " "
    # The exercise's shared source instruction is reproduced as an explicit local wrapper.
    doc2 = ET.Element(f"{{{C}}}document", {"{http://www.w3.org/XML/1998/namespace}lang": "gu-Gujr-IN"})
    ET.SubElement(doc2, f"{{{C}}}title").text = "વિસ્તાર: અંક કયા સ્થાને છે?"
    content = ET.SubElement(doc2, f"{{{C}}}content")
    ET.SubElement(content, f"{{{C}}}para", {"id": "GU-A10-instruction"}).text = "આપેલી સંખ્યામાં જણાવેલા દરેક અંકનું સ્થાન શોધો."
    content.append(ex)
    ET.ElementTree(doc2).write(LANG / "translations/a10-m82452-excerpt.gu.cnxml", encoding="utf-8", xml_declaration=True)
    print("Prepared 1 complete A00 source section and 1 selected A10 exercise.")


if __name__ == "__main__":
    prepare()
