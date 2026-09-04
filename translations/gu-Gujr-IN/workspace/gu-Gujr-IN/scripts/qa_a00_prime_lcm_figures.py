"""Bind all 26 m81273 figures and verify the four Gujarati redraws."""
import hashlib
import json
import math
import re
from html import escape
from pathlib import Path

from lxml import etree, html

from localized_a00_prime_lcm import DIAGRAMS, SELF_CHECK, VERIFIED_MATH_ONLY, render_figure


ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "gu-Gujr-IN"
SOURCE = ROOT / "downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81273.source.cnxml"
TRANSLATION = LANG / "translations/a00-m81273.gu.cnxml"
METADATA = LANG / "translations/a00-m81273-media-and-errata.gu.json"
MEDIA = ROOT / "downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media"
OUT = ROOT / "build/gujarati-prime-lcm-figures"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slots(values):
    return ",".join("_" if value is None else str(value) for value in values)


def main():
    source_sha = sha(SOURCE)
    translation_sha = sha(TRANSLATION)
    metadata_sha = sha(METADATA)
    assert source_sha == "4da1f4b3fb0d26f4ece7475531f5f6f46ed8c7801fffd605429105a836abd40e"
    assert translation_sha == "e9fbb999275fe8237e33beb36e0b9f318d6d73472070a8d0d5ee45204866e367"
    assert metadata_sha == "9369d6aca54779165947e1d6f8244760c44154dfdbfde246d4348f2d7d430529"
    data = json.loads(METADATA.read_text(encoding="utf-8"))
    assert data["source_sha256"] == source_sha
    assert data["translation_sha256"] == translation_sha
    assert len(data["media"]) == 26

    source = etree.parse(str(SOURCE))
    translation = etree.parse(str(TRANSLATION))
    source_media = source.xpath('//*[local-name()="media"]')
    assert len(source_media) == 26
    gu_alts = {node.get("id"): node.get("alt") for node in translation.xpath('//*[local-name()="media"]')}
    metadata = {item["source_id"]: item for item in data["media"]}

    figures = []
    redraws = []
    ids = []
    refs = []
    for node in source_media:
        source_id = node.get("id")
        image = node.xpath('./*[local-name()="image"]')[0]
        filename = Path(image.get("src")).name
        item = metadata[source_id]
        assert filename == item["file"]
        original_sha = sha(MEDIA / filename)
        assert original_sha == item["sha256"]
        snippet = render_figure(filename, gu_alts[source_id], source_id + "-redraw")
        if snippet:
            assert item["language_bearing"] is True
            tree = html.fragment_fromstring(snippet)
            visible = " ".join(tree.xpath('.//text()[not(ancestor::math)]')).replace("LCM", "")
            assert not re.search(r"[A-Za-z]{2,}", visible), (filename, visible)
            ids += tree.xpath(".//@id")
            refs += tree.xpath(".//@aria-labelledby")
            refs += re.findall(r"url\(#([^\)]+)\)", snippet)
            redraws.append((filename, snippet))
            mode = "localized"
        else:
            assert item["language_bearing"] is False
            assert filename in VERIFIED_MATH_ONLY
            mode = "verified mathematical-only original"
        figures.append({
            "source_media": source_id,
            "filename": filename,
            "sha256": original_sha,
            "mode": mode,
        })

    assert len(redraws) == 4
    assert len(VERIFIED_MATH_ONLY) == 22
    assert len(ids) == len(set(ids))
    assert all(ref in ids for ref in refs)
    rendered = {name: html.fragment_fromstring(snippet) for name, snippet in redraws}

    for filename, spec in DIAGRAMS.items():
        tree = rendered[filename]
        svg = tree.xpath(".//svg")[0]
        assert svg.get("data-numbers") == slots(spec["numbers"])
        assert svg.get("data-top") == slots(spec["top"])
        assert svg.get("data-bottom") == slots(spec["bottom"])
        assert svg.get("data-merged") == slots(spec["merged"])
        assert svg.get("data-final") == (str(spec["final"]) if spec["final"] is not None else "")
        assert len(svg.xpath('.//line[@marker-end]')) == 4
        assert "લઘુત્તમ સામાન્ય અવયવી (LCM)" in " ".join(tree.itertext())

    first = rendered["CNX_BMath_Figure_02_05_006_img.jpg"]
    first_text = " ".join(first.itertext())
    assert first_text.count("LCM") == 3
    assert "36" in first_text
    assert "2 · 2 · 3 · 3 = 36" in first_text

    selfcheck = rendered[SELF_CHECK]
    assert len(selfcheck.xpath(".//table")) == 2
    assert len(selfcheck.xpath(".//caption")) == 2
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]')) == 6
    self_text = " ".join(selfcheck.xpath(".//caption/text()"))
    assert "અવિભાજ્ય અવયવીકરણ" in self_text
    assert "લઘુત્તમ સામાન્ય અવયવી (LCM)" in self_text

    mathematical = {
        "12 factorization": math.prod((2, 2, 3)) == 12,
        "18 factorization": math.prod((2, 3, 3)) == 18,
        "LCM12,18": math.prod((2, 2, 3, 3)) == math.lcm(12, 18) == 36,
        "15 factorization": math.prod((3, 5)) == 15,
        "LCM15,18": math.prod((2, 3, 3, 5)) == math.lcm(15, 18) == 90,
        "50 factorization": math.prod((2, 5, 5)) == 50,
        "100 factorization": math.prod((2, 2, 5, 5)) == 100,
        "LCM50,100": math.prod((2, 2, 5, 5)) == math.lcm(50, 100) == 100,
        "repeated factors retained": all(
            len(spec["merged"]) == 4 for spec in DIAGRAMS.values()
        ),
    }
    assert all(mathematical.values())

    OUT.mkdir(parents=True, exist_ok=True)
    style = (
        "@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}"
        "*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;"
        "padding:0 16px;max-width:1080px;line-height:1.6;color:#182c35}article{margin-bottom:24px;"
        "border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:18px;overflow-wrap:anywhere}"
    )
    groups = (redraws[:2], redraws[2:])
    for page, group in enumerate(groups, 1):
        body = "".join(f"<article><h2>{escape(name)}</h2>{snippet}</article>" for name, snippet in group)
        document = (
            '<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>અવિભાજ્ય અવયવીકરણ અને LCM</title>'
            f"<style>{style}</style><body><h1>અવિભાજ્ય અવયવીકરણ અને LCM</h1>{body}</body></html>"
        )
        (OUT / f"page-{page}.html").write_text(document, encoding="utf-8")

    receipt = {
        "source_sha256": source_sha,
        "translation_sha256": translation_sha,
        "metadata_sha256": metadata_sha,
        "helper_sha256": sha(Path(__file__).with_name("localized_a00_prime_lcm.py")),
        "media": 26,
        "redraws": 4,
        "verified_math_only": 22,
        "unique_ids": len(ids),
        "resolved_references": len(refs),
        "LCM_diagrams": 3,
        "aligned_factor_columns": 12,
        "selfcheck_blank_cells": 6,
        "mathematical_checks": mathematical,
        "figures": figures,
    }
    with (LANG / "reviews/a00-m81273-figures-qa.json").open(
        "w", encoding="utf-8", newline="\n"
    ) as receipt_file:
        receipt_file.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in receipt.items() if key != "figures"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
