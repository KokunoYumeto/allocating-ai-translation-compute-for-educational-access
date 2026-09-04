"""Bind all nine A00 m81272 figures and verify the five Gujarati redraws."""
import hashlib
import json
import re
from html import escape
from pathlib import Path

from lxml import etree, html

from localized_a00_factors import (
    HEADER_FILL,
    PREFIX,
    PRIME_FILL,
    PRIMES,
    VERIFIED_MATH_ONLY,
    render_figure,
)


ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "gu-Gujr-IN"
SOURCE = ROOT / "downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81272.source.cnxml"
TRANSLATION = LANG / "translations/a00-m81272.gu.cnxml"
METADATA = LANG / "translations/a00-m81272-media-and-errata.gu.json"
MEDIA = ROOT / "downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media"
OUT = ROOT / "build/gujarati-factor-figures"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_sha = sha(SOURCE)
    translation_sha = sha(TRANSLATION)
    metadata_sha = sha(METADATA)
    assert source_sha == "e547be567190fc22617dda6defdfa2d04349dd86584d890221d2d702aff6f214"
    assert translation_sha == "85d41ab551d29636d5505cbfe53724c0e90149d2180646a3fdabeca90d493148"
    data = json.loads(METADATA.read_text(encoding="utf-8"))
    assert data["source_sha256"] == source_sha
    assert data["translation_sha256"] == translation_sha
    assert len(data["media"]) == 9

    source = etree.parse(str(SOURCE))
    translation = etree.parse(str(TRANSLATION))
    source_media = source.xpath('//*[local-name()="media"]')
    assert len(source_media) == 9
    gu_alts = {node.get("id"): node.get("alt") for node in translation.xpath('//*[local-name()="media"]')}
    meta = {item["media_id"]: item for item in data["media"]}

    figures = []
    redraws = []
    ids = []
    refs = []
    for node in source_media:
        media_id = node.get("id")
        image = node.xpath('./*[local-name()="image"]')[0]
        filename = Path(image.get("src")).name
        assert media_id in meta
        assert meta[media_id]["source_file"] == filename
        original_sha = sha(MEDIA / filename)
        assert original_sha == meta[media_id]["sha256"]
        snippet = render_figure(filename, gu_alts[media_id], media_id + "-redraw")
        if snippet:
            assert filename not in VERIFIED_MATH_ONLY
            tree = html.fragment_fromstring(snippet)
            visible_text = " ".join(tree.xpath('.//text()[not(ancestor::math)]'))
            assert not re.search(r"[A-Za-z]{2,}", visible_text), (filename, visible_text)
            ids += tree.xpath(".//@id")
            refs += tree.xpath(".//@aria-labelledby")
            refs += re.findall(r"url\(#([^\)]+)\)", snippet)
            redraws.append((filename, snippet))
            mode = "localized"
        else:
            assert filename in VERIFIED_MATH_ONLY
            mode = "verified mathematical-only original"
        figures.append({
            "source_media": media_id,
            "filename": filename,
            "sha256": original_sha,
            "mode": mode,
        })

    assert len(redraws) == 5
    assert len(VERIFIED_MATH_ONLY) == 4
    assert len(ids) == len(set(ids))
    assert all(ref in ids for ref in refs)
    rendered = {name: html.fragment_fromstring(snippet) for name, snippet in redraws}

    product = rendered[PREFIX + "008_img.jpg"]
    product_text = " ".join(product.itertext()).replace(" ", "")
    assert all(token in product_text for token in ("8·9", "=", "72", "અવયવ", "ગુણનફળ"))
    assert len(product.xpath(".//svg//path")) == 2

    factor72 = rendered[PREFIX + "009.jpg"]
    factor_rows = factor72.xpath(".//table//tr")
    assert len(factor_rows) == 9
    assert factor72.xpath(".//th/text()") == ["ભાજ્ય", "ભાજક", "ભાગફળ", "અવયવ"]
    factor_cells = [["".join(cell.itertext()).strip() for cell in row.xpath("./td")] for row in factor_rows[1:]]
    expected72 = [
        ["72", "1", "72", "1, 72"], ["72", "2", "36", "2, 36"],
        ["72", "3", "24", "3, 24"], ["72", "4", "18", "4, 18"],
        ["72", "5", "14.4", "–"], ["72", "6", "12", "6, 12"],
        ["72", "7", "~10.29", "–"], ["72", "8", "9", "8, 9"],
    ]
    assert factor_cells == expected72

    prime = rendered[PREFIX + "014_Errata.jpg"]
    assert len(prime.xpath(".//table//tr")) == 11
    assert len(prime.xpath(".//thead//th")) == 7
    assert prime.xpath(".//thead//th[4]/@aria-hidden") == ["true"]
    body_rows = prime.xpath(".//tbody/tr")
    highlighted = []
    for row in body_rows:
        for position in (1, 5):
            cell = row.xpath(f"./td[{position}]")[0]
            text = "".join(cell.itertext()).strip()
            if text and PRIME_FILL in cell.get("style"):
                highlighted.append(int(text))
    assert frozenset(highlighted) == PRIMES and len(highlighted) == len(PRIMES)
    assert "1, 3, 5, 15" in " ".join(prime.itertext())
    assert "1, 2, 3, 5, 15" not in " ".join(prime.itertext())
    assert len(body_rows[-1].xpath('./td[@aria-label="ખાલી"]')) == 3

    frank = rendered["CNX_BMath_Figure_02_05_203_img.jpg"]
    assert len(frank.xpath(".//table//tr")) == 10
    frank_cells = [["".join(cell.itertext()).strip() for cell in row.xpath("./td")] for row in frank.xpath(".//tbody/tr")]
    expected_weeks = ["0", "1", "2", "3", "4", "5", "6", "20", "x"]
    expected_totals = ["100", "115", "130", "145", "160", "175", "190", "400", "100 + 15x"]
    assert [row[0] for row in frank_cells] == expected_weeks
    assert [row[2] for row in frank_cells] == expected_totals
    assert frank_cells[-1][1] == "100 + 15 · x"

    selfcheck = rendered["CNX_BMath_Figure_AppB_011.jpg"]
    assert len(selfcheck.xpath(".//table")) == 4
    assert len(selfcheck.xpath(".//caption")) == 4
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]')) == 12
    skills = " ".join(selfcheck.xpath(".//caption/text()"))
    assert all(term in skills for term in ("અવયવી", "વિભાજ્યતાની", "અવયવ", "અવિભાજ્ય", "સંયુક્ત"))

    arithmetic = {
        "factor product": 8 * 9 == 72,
        "factor72 integral rows": all(72 // d == q and 72 % d == 0 for d, q in ((1, 72), (2, 36), (3, 24), (4, 18), (6, 12), (8, 9))),
        "factor72 nonintegral rows": 72 / 5 == 14.4 and 10.28 < 72 / 7 < 10.29,
        "prime set2to20": PRIMES == frozenset(n for n in range(2, 21) if all(n % d for d in range(2, int(n ** .5) + 1))),
        "factor lists2to20": all(
            str(n) in " ".join(prime.itertext()) for n in range(2, 21)
        ),
        "Frank numeric rows": all(
            int(row[2]) == 100 + 15 * int(row[0]) for row in frank_cells[:-1]
        ),
        "Frank symbolic row": frank_cells[-1] == ["x", "100 + 15 · x", "100 + 15x"],
    }
    assert all(arithmetic.values())

    OUT.mkdir(parents=True, exist_ok=True)
    style = (
        "@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}"
        "*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;"
        "padding:0 16px;max-width:1080px;line-height:1.6;color:#182c35}article{margin-bottom:24px;"
        "border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:18px;overflow-wrap:anywhere}"
    )
    groups = (redraws[:2], redraws[2:3], redraws[3:])
    for page, group in enumerate(groups, 1):
        body = "".join(f"<article><h2>{escape(name)}</h2>{snippet}</article>" for name, snippet in group)
        document = (
            '<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>અવયવ અને અવયવી</title>'
            f"<style>{style}</style><body><h1>અવયવ અને અવયવી</h1>{body}</body></html>"
        )
        (OUT / f"page-{page}.html").write_text(document, encoding="utf-8")

    receipt = {
        "source_sha256": source_sha,
        "translation_sha256": translation_sha,
        "metadata_sha256": metadata_sha,
        "helper_sha256": sha(Path(__file__).with_name("localized_a00_factors.py")),
        "media": 9,
        "redraws": 5,
        "verified_math_only": 4,
        "unique_ids": len(ids),
        "resolved_references": len(refs),
        "factor72_rows": len(factor_cells),
        "prime_highlights": highlighted,
        "Frank_rows": len(frank_cells),
        "selfcheck_blank_cells": 12,
        "mathematical_checks": arithmetic,
        "figures": figures,
    }
    with (LANG / "reviews/a00-m81272-figures-qa.json").open(
        "w", encoding="utf-8", newline="\n"
    ) as receipt_file:
        receipt_file.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in receipt.items() if key != "figures"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
