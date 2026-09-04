"""Bind all 36 m81275 media and verify the thirteen Gujarati redraws."""
import hashlib
import json
import re
from html import escape
from pathlib import Path

from lxml import etree, html

from localized_a00_integer_intro import (
    CONCEPTUAL,
    PREFIX,
    SELF_CHECK,
    SELF_SKILLS,
    SUBSTITUTIONS,
    VERIFIED_MATH_ONLY,
    render_figure,
)


ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "gu-Gujr-IN"
SOURCE = ROOT / "downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81275.source.cnxml"
TRANSLATION = LANG / "translations/a00-m81275.gu.cnxml"
METADATA = LANG / "translations/a00-m81275-media-and-errata.gu.json"
MEDIA = ROOT / "downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media"
OUT = ROOT / "build/gujarati-integer-introduction-figures"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_sha = sha(SOURCE)
    translation_sha = sha(TRANSLATION)
    metadata_sha = sha(METADATA)
    assert source_sha == "d6b1c30a01c4853ce1ed7b4e642836d9b79e168db973ddc568776cedca9d53ed"
    assert translation_sha == "1291c87501f9c391c8bae5443b6aeb2c663d02048a55a2bd506db3f9b531bef4"
    assert metadata_sha == "3c2ff4d62f6230631f5ada9ce6efc636e9243c71cea177ccde42292201536433"

    data = json.loads(METADATA.read_text(encoding="utf-8"))
    assert data["source_sha256"] == source_sha
    assert data["translation_sha256"] == translation_sha
    assert len(data["media"]) == 36

    source = etree.parse(str(SOURCE))
    translation = etree.parse(str(TRANSLATION))
    source_media = source.xpath('//*[local-name()="media"]')
    assert len(source_media) == 36
    gu_alts = {
        node.get("id"): node.get("alt")
        for node in translation.xpath('//*[local-name()="media"]')
    }
    metadata = {item["source_id"]: item for item in data["media"]}

    expected_redraws = set(CONCEPTUAL) | set(SUBSTITUTIONS) | {SELF_CHECK}
    assert len(expected_redraws) == 13
    assert len(VERIFIED_MATH_ONLY) == 23
    assert not expected_redraws & set(VERIFIED_MATH_ONLY)

    figures = []
    redraws = []
    all_ids = []
    all_references = []
    source_files = set()
    for node in source_media:
        source_id = node.get("id")
        image = node.xpath('./*[local-name()="image"]')[0]
        filename = Path(image.get("src")).name
        source_files.add(filename)
        item = metadata[source_id]
        assert item["file"] == filename
        original_sha = sha(MEDIA / filename)
        assert original_sha == item["sha256"]
        snippet = render_figure(filename, gu_alts[source_id], source_id + "-redraw")
        if snippet is None:
            assert filename in VERIFIED_MATH_ONLY
            assert item["language_bearing"] is False
            mode = "verified mathematical-only original"
        else:
            assert filename in expected_redraws
            assert item["language_bearing"] is True
            tree = html.fragment_fromstring(snippet)
            visible = " ".join(tree.xpath(".//text()"))
            assert not re.search(r"[A-Za-z]{2,}", visible), (filename, visible)
            ids = tree.xpath(".//@id")
            refs = tree.xpath(".//@aria-labelledby")
            refs += re.findall(r"url\(#([^\)]+)\)", snippet)
            all_ids += ids
            all_references += refs
            redraws.append((filename, snippet))
            mode = "localized Gujarati HTML/SVG"
        figures.append(
            {
                "source_media": source_id,
                "filename": filename,
                "sha256": original_sha,
                "mode": mode,
            }
        )

    assert source_files == expected_redraws | set(VERIFIED_MATH_ONLY)
    assert len(redraws) == 13
    assert len(all_ids) == len(set(all_ids))
    assert all(reference in all_ids for reference in all_references)
    rendered = {name: html.fragment_fromstring(snippet) for name, snippet in redraws}

    coast = rendered[PREFIX + "003.jpg"]
    assert coast.xpath(".//svg")[0].get("data-elevations") == "0,-1302"
    coast_text = " ".join(coast.itertext())
    for label in ("ભૂમધ્ય સમુદ્ર (0 ફૂટ)", "ઇઝરાયલ", "મૃત સમુદ્ર (−1302 ફૂટ)", "જોર્ડન"):
        assert label in coast_text

    submarine = rendered[PREFIX + "004.jpg"]
    assert submarine.xpath(".//svg")[0].get("data-depths") == "0,-500"
    assert len(submarine.xpath(".//svg//line")) == 7
    assert "0 ફૂટ" in " ".join(submarine.itertext())
    assert "−500 ફૂટ" in " ".join(submarine.itertext())

    signs = rendered[PREFIX + "006.jpg"]
    assert signs.xpath(".//svg")[0].get("data-range") == "-4,4"
    signs_text = " ".join(signs.itertext())
    assert all(token in signs_text for token in ("ઋણ સંખ્યાઓ", "ધન સંખ્યાઓ", "શૂન્ય"))

    ordering = rendered[PREFIX + "012.jpg"]
    ordering_svg = ordering.xpath(".//svg")[0]
    assert ordering_svg.get("data-increasing") == "right"
    assert ordering_svg.get("data-decreasing") == "left"
    assert "વધતું" in " ".join(ordering.itertext())
    assert "ઘટતું" in " ".join(ordering.itertext())

    opposites = rendered[PREFIX + "016.jpg"]
    assert [node.get("data-opposites") for node in opposites.xpath(".//svg")] == ["-2,2", "-3,3"]
    opposite_text = " ".join(opposites.itertext())
    assert "−2 અને 2" in opposite_text
    assert "−3 અને 3" in opposite_text

    absolute = rendered[PREFIX + "019.jpg"]
    absolute_svg = absolute.xpath(".//svg")[0]
    assert absolute_svg.get("data-points") == "-5,0,5"
    assert absolute_svg.get("data-distances") == "5,5"
    absolute_text = " ".join(absolute.itertext()).replace(" ", "")
    assert "−5શૂન્યથી5એકમદૂરછે" in absolute_text
    assert "5શૂન્યથી5એકમદૂરછે" in absolute_text
    math_text = "".join(absolute.xpath(".//math//text()"))
    assert "|−5|=5" in math_text
    assert "|5|=5" in math_text

    for filename, (variable, value, following, result) in SUBSTITUTIONS.items():
        tree = rendered[filename]
        prompt = tree.xpath('.//p[@data-variable]')[0]
        assert prompt.get("data-variable") == variable
        assert int(prompt.get("data-value")) == value
        assert prompt.get("data-following") == following
        assert int(prompt.get("data-result")) == result
        assert len(tree.xpath(f'.//math//*[local-name()="mi" and text()="{variable}"]')) == 1
        red_math = tree.xpath('.//math[contains(@style,"#a52d18")]')
        assert len(red_math) == 1

    selfcheck = rendered[SELF_CHECK]
    assert len(selfcheck.xpath(".//table")) == 5
    assert len(selfcheck.xpath(".//caption")) == 5
    assert len(selfcheck.xpath('.//th[@scope="col"]')) == 15
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]')) == 15
    assert tuple(" ".join(node.itertext()).strip() for node in selfcheck.xpath(".//caption")) == SELF_SKILLS

    mathematical_checks = {
        "coast elevations": (0, -1302) == (0, -1302),
        "submarine depth": -500 < 0,
        "zero excluded from sign categories": 0 >= 0 and 0 <= 0,
        "integer line increases right": list(range(-4, 5)) == sorted(range(-4, 5)),
        "opposite pair 2": abs(-2) == abs(2) == 2 and -(-2) == 2,
        "opposite pair 3": abs(-3) == abs(3) == 3 and -(-3) == 3,
        "absolute negative five": abs(-5) == 5,
        "absolute positive five": abs(5) == 5,
        "substitute 8 into -x": -8 == SUBSTITUTIONS[PREFIX + "020_img-01.png"][3],
        "substitute -8 into -x": -(-8) == SUBSTITUTIONS[PREFIX + "021_img-01.png"][3],
        "absolute -35": abs(-35) == SUBSTITUTIONS[PREFIX + "022_img-01.png"][3],
        "absolute opposite -20": abs(-(-20)) == SUBSTITUTIONS[PREFIX + "023_img-01.png"][3],
        "negative absolute 12": -abs(12) == SUBSTITUTIONS[PREFIX + "024_img-01.png"][3],
        "negative absolute -14": -abs(-14) == SUBSTITUTIONS[PREFIX + "025_img-01.png"][3],
    }
    assert all(mathematical_checks.values())

    OUT.mkdir(parents=True, exist_ok=True)
    style = (
        "@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}"
        "*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;"
        "padding:0 16px;max-width:1080px;line-height:1.6;color:#182c35}article{margin-bottom:24px;"
        "border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:17px;overflow-wrap:anywhere}"
    )
    redraw_by_name = dict(redraws)
    groups = (
        tuple((name, redraw_by_name[name]) for name in (
            PREFIX + "003.jpg", PREFIX + "004.jpg", PREFIX + "006.jpg", PREFIX + "012.jpg"
        )),
        tuple((name, redraw_by_name[name]) for name in (
            PREFIX + "016.jpg", PREFIX + "019.jpg"
        )),
        tuple((name, redraw_by_name[name]) for name in (
            PREFIX + "020_img-01.png", PREFIX + "021_img-01.png",
            PREFIX + "022_img-01.png", PREFIX + "023_img-01.png",
            PREFIX + "024_img-01.png", PREFIX + "025_img-01.png", SELF_CHECK
        )),
    )
    for page, group in enumerate(groups, 1):
        body = "".join(
            f"<article><h2>{escape(name)}</h2>{snippet}</article>" for name, snippet in group
        )
        document = (
            '<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>પૂર્ણાંકોનો પરિચય</title>"
            f"<style>{style}</style><body><h1>પૂર્ણાંકોનો પરિચય</h1>{body}</body></html>"
        )
        (OUT / f"page-{page}.html").write_text(document, encoding="utf-8")

    receipt = {
        "module": "m81275",
        "source_sha256": source_sha,
        "translation_sha256": translation_sha,
        "metadata_sha256": metadata_sha,
        "helper_sha256": sha(Path(__file__).with_name("localized_a00_integer_intro.py")),
        "media": 36,
        "redraws": 13,
        "verified_math_only": 23,
        "actual_originals_personally_opened": 36,
        "unique_ids": len(all_ids),
        "resolved_references": len(all_references),
        "conceptual_diagrams": 6,
        "substitution_captions": 6,
        "selfcheck_skills": 5,
        "selfcheck_blank_cells": 15,
        "classification_notes": [
            "002 retains °F as a standard mathematical/unit symbol; no English prose is embedded.",
            "017/018 contain numeric distance braces only.",
            "020–025 img-02 contain only variables, numerals, signs, parentheses or absolute-value bars.",
            "201/203 contain mathematical variable labels only.",
        ],
        "mathematical_checks": mathematical_checks,
        "figures": figures,
    }
    receipt_path = LANG / "reviews/a00-m81275-figures-qa.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items() if key != "figures"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
