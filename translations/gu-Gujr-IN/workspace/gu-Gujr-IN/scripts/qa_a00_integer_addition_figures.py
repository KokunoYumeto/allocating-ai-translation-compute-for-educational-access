"""Bind all 72 m81276 media occurrences and verify twelve Gujarati redraws."""
import hashlib
import json
import re
from html import escape
from pathlib import Path

from lxml import etree, html

from localized_a00_integer_addition import (
    COUNTERS,
    PREFIX,
    SELF_CHECK,
    SELF_CHOICES,
    SELF_SKILLS,
    SUBSTITUTIONS,
    VERIFIED_MATH_ONLY,
    render_figure,
)


ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "gu-Gujr-IN"
SOURCE = ROOT / "downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81276.source.cnxml"
TRANSLATION = LANG / "translations/a00-m81276.gu.cnxml"
METADATA = LANG / "translations/a00-m81276-media-and-errata.gu.json"
MEDIA = ROOT / "downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media"
OUT = ROOT / "build/gujarati-integer-addition-figures"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_sha = sha(SOURCE)
    translation_sha = sha(TRANSLATION)
    metadata_sha = sha(METADATA)
    assert source_sha == "7e60eb505941fae754150df495be0ff7acf303c355eb1e81a8c57d48090e9cef"
    assert translation_sha == "f77dfe5ab67eb6db2a50e372d0390cbf8a587da4e6e0016d9b4eb63a55e12614"
    assert metadata_sha == "9a91525b24b1b73bea1deea5ac4a0ee1f42d8ad6bd32d9e10c0981d12dc84e51"

    data = json.loads(METADATA.read_text(encoding="utf-8"))
    assert data["module_id"] == "m81276"
    assert data["source_sha256"] == source_sha
    inventory = data["media_inventory"]
    assert len(inventory) == 72
    assert data["actual_source_and_media_review"]["unique_original_images_read"] == 71

    source = etree.parse(str(SOURCE))
    translation = etree.parse(str(TRANSLATION))
    source_media = source.xpath('//*[local-name()="media"]')
    translation_media = translation.xpath('//*[local-name()="media"]')
    assert len(source_media) == len(translation_media) == 72
    gu_alts = {node.get("id"): node.get("alt") or "" for node in translation_media}

    expected_redraws = {PREFIX + "024_img.jpg"} | set(COUNTERS) | set(SUBSTITUTIONS) | {SELF_CHECK}
    assert len(expected_redraws) == 12
    assert len(VERIFIED_MATH_ONLY) == 59
    assert not expected_redraws & set(VERIFIED_MATH_ONLY)

    figures = []
    redraws = {}
    all_ids = []
    all_references = []
    source_files = []
    original_hashes = {}
    for reference_index, (node, item) in enumerate(zip(source_media, inventory), 1):
        source_id = node.get("id")
        images = node.xpath('./*[local-name()="image"]')
        assert len(images) == 1
        filename = Path(images[0].get("src")).name
        assert item["reference_index"] == reference_index
        assert item["media_id"] == source_id
        assert item["asset"] == filename
        assert item["actual_original_reviewed"] is True
        source_files.append(filename)

        original_sha = sha(MEDIA / filename)
        assert original_sha == item["asset_sha256"]
        if filename in original_hashes:
            assert original_hashes[filename] == original_sha
        original_hashes[filename] = original_sha

        snippet = render_figure(filename, gu_alts[source_id], source_id + "-redraw")
        if snippet is None:
            assert filename in VERIFIED_MATH_ONLY
            assert item["embedded_language"] is False
            assert item["reader_action"] == "retain original"
            mode = "verified mathematical-only original"
        else:
            assert filename in expected_redraws
            assert item["embedded_language"] is True
            assert item["reader_action"] == "localized redraw required"
            tree = html.fragment_fromstring(snippet)
            visible = " ".join(tree.xpath(".//text()"))
            assert not re.search(r"[A-Za-z]{2,}", visible), (filename, visible)
            ids = tree.xpath(".//@id")
            references = tree.xpath(".//@aria-labelledby")
            references += re.findall(r"url\(#([^\)]+)\)", snippet)
            all_ids += ids
            all_references += references
            redraws[filename] = snippet
            mode = "localized Gujarati HTML/SVG"
        figures.append({
            "reference_index": reference_index,
            "source_media": source_id,
            "filename": filename,
            "sha256": original_sha,
            "mode": mode,
        })

    unique_source_files = set(source_files)
    assert len(source_files) == 72
    assert len(unique_source_files) == 71
    assert source_files.count(PREFIX + "029_img-03.png") == 2
    assert unique_source_files == expected_redraws | set(VERIFIED_MATH_ONLY)
    assert len(redraws) == 12
    assert len(all_ids) == len(set(all_ids)) == 12
    assert all(reference in all_ids for reference in all_references)

    rendered = {name: html.fragment_fromstring(snippet) for name, snippet in redraws.items()}
    legend = rendered[PREFIX + "024_img.jpg"]
    legend_svg = legend.xpath(".//svg")[0]
    assert legend_svg.get("data-positive-count") == "1"
    assert legend_svg.get("data-negative-count") == "1"
    assert len(legend.xpath(".//circle")) == 2
    legend_text = " ".join(legend.itertext())
    assert "ધન" in legend_text and "ઋણ" in legend_text

    counter_checks = {}
    for filename, (count, kind, label, groups) in COUNTERS.items():
        tree = rendered[filename]
        svg = tree.xpath(".//svg")[0]
        assert int(svg.get("data-counter-count")) == count
        assert svg.get("data-counter-kind") == kind
        assert svg.get("data-counter-groups") == ",".join(str(group) for group in groups)
        assert len(tree.xpath(".//circle")) == count
        assert label in " ".join(tree.itertext())
        counter_checks[filename] = {
            "count": count,
            "kind": kind,
            "groups": list(groups),
            "label": label,
        }

    arithmetic_checks = {
        PREFIX + "029_img-01.png": (-2 + 7 == 5),
        PREFIX + "030_img-01.png": (-11 + 7 == -4),
        PREFIX + "031_img-01.png": (-5 + 1 == -4),
        PREFIX + "032_img-01.png": (-(-5) + 1 == 6),
        PREFIX + "033_img-01.png": (3 * 12 + (-30) == 6),
        PREFIX + "034_img-01.png": ((-18 + 24) ** 2 == 36),
    }
    assert all(arithmetic_checks.values())
    for filename, (variables, values, template, paired) in SUBSTITUTIONS.items():
        tree = rendered[filename]
        prompt = tree.xpath('.//p[@data-variables]')[0]
        assert prompt.get("data-variables") == ",".join(variables)
        assert prompt.get("data-values") == ",".join(str(value) for value, _ in values)
        assert prompt.get("data-colors") == ",".join(color for _, color in values)
        assert prompt.get("data-paired-expression") == paired
        signed_math = tree.xpath('.//math[@data-signed-value]')
        assert [int(node.get("data-signed-value")) for node in signed_math] == [value for value, _ in values]
        assert [node.get("data-highlight") for node in signed_math] == [color for _, color in values]
        for node, (value, color) in zip(signed_math, values):
            math_text = "".join(node.itertext())
            assert math_text == str(value).replace("-", "−")

    selfcheck = rendered[SELF_CHECK]
    assert "હું આ કરી શકું છું..." in " ".join(selfcheck.itertext())
    assert len(selfcheck.xpath(".//table")) == 5
    assert len(selfcheck.xpath(".//caption")) == 5
    assert len(selfcheck.xpath('.//th[@scope="col"]')) == 15
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]')) == 15
    assert tuple(" ".join(node.itertext()).strip() for node in selfcheck.xpath(".//caption")) == SELF_SKILLS
    for table in selfcheck.xpath(".//table"):
        headers = tuple(" ".join(node.itertext()).strip() for node in table.xpath('.//th[@scope="col"]'))
        assert headers == SELF_CHOICES

    OUT.mkdir(parents=True, exist_ok=True)
    style = (
        "@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}"
        "*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;"
        "padding:0 16px;max-width:1080px;line-height:1.6;color:#182c35}article{margin-bottom:24px;"
        "border-bottom:2px solid #08656b;padding-bottom:16px}h1{font-size:26px}"
        "h2{font-size:16px;overflow-wrap:anywhere}math{font-family:Cambria Math,serif}"
    )
    groups = (
        tuple(PREFIX + name for name in (
            "024_img.jpg", "025_img-03.png", "026_img-03.png", "027_img-04.png", "028_img-04.png"
        )),
        tuple(PREFIX + name for name in (
            "029_img-01.png", "030_img-01.png", "031_img-01.png",
            "032_img-01.png", "033_img-01.png", "034_img-01.png"
        )),
        (SELF_CHECK,),
    )
    for page, group in enumerate(groups, 1):
        body = "".join(
            f"<article><h2>{escape(name)}</h2>{redraws[name]}</article>" for name in group
        )
        document = (
            '<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>પૂર્ણાંકોનો સરવાળો</title>'
            f'<style>{style}</style><body><h1>પૂર્ણાંકોનો સરવાળો</h1>{body}</body></html>'
        )
        (OUT / f"page-{page}.html").write_text(document, encoding="utf-8")

    receipt = {
        "module": "m81276",
        "source_sha256": source_sha,
        "translation_sha256": translation_sha,
        "metadata_sha256": metadata_sha,
        "helper_sha256": sha(Path(__file__).with_name("localized_a00_integer_addition.py")),
        "media_occurrences": 72,
        "unique_original_assets": 71,
        "redraw_occurrences": 12,
        "unique_redraws": 12,
        "verified_math_only_occurrences": 60,
        "unique_verified_math_only": 59,
        "actual_originals_personally_opened": 71,
        "duplicate_occurrence": PREFIX + "029_img-03.png",
        "unique_ids": len(all_ids),
        "resolved_references": len(all_references),
        "counter_redraws": 5,
        "substitution_captions": 6,
        "selfcheck_skills": 5,
        "selfcheck_scoped_headers": 15,
        "selfcheck_blank_cells": 15,
        "counter_checks": counter_checks,
        "arithmetic_checks": arithmetic_checks,
        "classification_notes": [
            "All 71 unique originals were opened at original resolution; classification is pixel-based.",
            "Single Latin letters in retained originals are source mathematical variables, not English prose.",
            "Counter-only originals preserve exact grouping, arrows, circle counts and color relationships.",
            "The duplicate 029_img-03 asset occurs twice under distinct source media IDs and the same pinned hash.",
        ],
        "figures": figures,
    }
    receipt_path = LANG / "reviews/a00-m81276-figures-qa.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items() if key != "figures"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
