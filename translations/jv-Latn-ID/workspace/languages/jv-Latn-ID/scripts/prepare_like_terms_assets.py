"""Materialize the three pinned like-terms images and six declared JV SVG derivatives.

This is a finite asset job for A10-COMB-D01..D03.  It does not search for,
translate, or infer any other image.  Every derivative is tied to the exact
source member, media node, old English label, and source byte hash recorded in
the reviewed rules file.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from config import LANG, ROOT
from safe_io import write_bytes


UNIT = "a10-combine-like-terms"
ASSET_DIR = Path("translation/assets") / UNIT
RULES_PATH = LANG / f"audio/{UNIT}.rules.json"
MANIFEST_PATH = LANG / f"translation/{UNIT}.assets.json"
ARCHIVE_PREFIX = "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/"
TRACKS = ("jv-academic", "jv-conversation")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def svg_bytes(chart: dict, track: str, source_raw: bytes) -> bytes:
    if track not in TRACKS:
        raise ValueError("unsupported_like_terms_asset_track")
    if sha(source_raw) != chart["primary_asset"]["sha256"]:
        raise ValueError("unsupported_like_terms_source_asset")
    label = chart["expected_jv_visible_labels"][track]
    source = chart["primary_asset"]
    width, height = source["dimensions"]
    metadata = {
        "schema": "jv-like-terms-image-binding-v1",
        "fixture": chart["id"],
        "module": chart["module"],
        "section": chart["section"],
        "media_id": chart["media_id"],
        "source_path": chart["source_path"],
        "source_sha256": source["sha256"],
        "old_visible_label": chart["source_visible_label"],
        "track": track,
        "new_visible_label": label,
        "rendering": "exact source JPEG embedded; only the inspected left instruction panel is covered",
        "latent_english_pixels": "retained beneath opaque source-background cover",
    }
    encoded = base64.b64encode(source_raw).decode("ascii")
    common = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" xml:lang="jv-Latn-ID"',
        f' data-fixture="{chart["id"]}" data-media-id="{chart["media_id"]}" data-source-sha256="{source["sha256"]}" data-track="{track}">',
        f'<title>{esc(label)}</title>',
        f'<desc>{esc(chart["expected_target_alt"][track])}</desc>',
        f'<metadata>{esc(json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")))}</metadata>',
        f'<defs><clipPath id="instruction-clip"><rect x="2" y="2" width="354" height="{height - 4}"/></clipPath></defs>',
        f'<image class="exact-source" x="0" y="0" width="{width}" height="{height}" href="data:image/jpeg;base64,{encoded}"/>',
        '<g class="instruction-replacement" clip-path="url(#instruction-clip)">',
        f'<rect class="instruction-cover" x="2" y="2" width="354" height="{height - 4}" fill="#a0b3bd"/>',
    ]
    label_style = 'font-family="Arial, Helvetica, sans-serif" font-size="16" fill="#111111"'
    remainder = label.split(". ", 1)[1]
    bold = label.split(". ", 1)[0] + "."
    if chart["id"] == "A10-COMB-D01":
        common += [
            f'<text class="instruction" x="12" y="28" {label_style}><tspan font-weight="700">{esc(bold)}</tspan><tspan> {esc(remainder)}</tspan></text>',
        ]
    elif chart["id"] == "A10-COMB-D02":
        lines = {
            "jv-academic": (
                "Langkah 2. Tatanen maneh ekspresine",
                "supaya suku-suku sajinis jejer.",
            ),
            "jv-conversation": (
                "Langkah 2. Tatanen maneh wujud aljabare",
                "supaya suku-suku sing sajinis jejer.",
            ),
        }[track]
        assert " ".join(lines) == label
        common += [
            f'<text class="instruction" x="12" y="27" {label_style}><tspan x="12" y="27"><tspan font-weight="700">{esc(bold)}</tspan><tspan> {esc(lines[0].split(". ", 1)[1])}</tspan></tspan><tspan x="12" y="49">{esc(lines[1])}</tspan></text>',
        ]
    elif chart["id"] == "A10-COMB-D03":
        common += [
            f'<text class="instruction" x="12" y="31" {label_style}><tspan font-weight="700">{esc(bold)}</tspan><tspan> {esc(remainder)}</tspan></text>',
        ]
    else:
        raise ValueError("unsupported_like_terms_chart_fixture")
    common.append("</g>")
    common.append("</svg>\n")
    return "\n".join(common).encode("utf-8")


def products() -> dict[str, bytes]:
    rules_raw = RULES_PATH.read_bytes()
    rules = json.loads(rules_raw)
    assert rules["scope"]["unit"] == UNIT
    assert rules["asset_binding"]["canonical_git_pin"] == "38cae454e644abf9f0a623e876994553881597c9"
    archive_path = ROOT / rules["asset_binding"]["canonical_archive"]
    generated: dict[str, bytes] = {}
    assets = []
    with zipfile.ZipFile(archive_path) as archive:
        for chart in rules["chart_fixtures"]:
            source = chart["primary_asset"]
            member = source["archive_member"]
            assert member == ARCHIVE_PREFIX + source["filename"]
            raw = archive.read(member)
            assert len(raw) == source["bytes"]
            assert sha(raw) == source["sha256"] == chart["english_authority_asset"]["sha256"]
            assert raw.startswith(b"\xff\xd8\xff")
            with Image.open(BytesIO(raw)) as image:
                assert image.format == "JPEG" and list(image.size) == source["dimensions"]
            source_rel = (ASSET_DIR / source["filename"]).as_posix()
            generated[source_rel] = raw
            outputs = {
                "id-academic": {
                    "path": source_rel,
                    "mime_type": "image/jpeg",
                    "sha256": sha(raw),
                    "bytes": len(raw),
                    "dimensions": source["dimensions"],
                }
            }
            corrections = []
            for track in TRACKS:
                derivative = svg_bytes(chart, track, raw)
                derivative_name = source["filename"].removesuffix(".jpg") + f".{track}.svg"
                derivative_rel = (ASSET_DIR / derivative_name).as_posix()
                generated[derivative_rel] = derivative
                outputs[track] = {
                    "path": derivative_rel,
                    "mime_type": "image/svg+xml",
                    "sha256": sha(derivative),
                    "bytes": len(derivative),
                    "dimensions": source["dimensions"],
                }
                corrections.append({
                    "kind": "instruction_label_translation",
                    "track": track,
                    "module": chart["module"],
                    "section": chart["section"],
                    "media_id": chart["media_id"],
                    "source_path": chart["source_path"],
                    "source_tree_sha256": chart["source_tree_sha256"],
                    "source_image_sha256": source["sha256"],
                    "old_value": chart["source_visible_label"],
                    "new_value": chart["expected_jv_visible_labels"][track],
                })
            declared_alt_correction = None
            if chart["id"] == "A10-COMB-D01":
                declared_alt_correction = {
                    "kind": "target_alt_opening_matches_actual_standalone_image",
                    "module": chart["module"],
                    "section": chart["section"],
                    "media_id": chart["media_id"],
                    "source_path": chart["source_path"],
                    "source_tree_sha256": chart["source_tree_sha256"],
                    "source_image_sha256": source["sha256"],
                    "old_value": chart["source_alt"],
                    "new_values": chart["expected_target_alt"],
                    "evidence": chart["actual_visual_observation"],
                }
            assets.append({
                "fixture": chart["id"],
                "source_src": chart["source_image"],
                "source_binding": {
                    "module": chart["module"],
                    "section": chart["section"],
                    "media_id": chart["media_id"],
                    "source_path": chart["source_path"],
                    "source_tree_sha256": chart["source_tree_sha256"],
                    "archive": rules["asset_binding"]["canonical_archive"],
                    "archive_member": member,
                    "old_visible_label": chart["source_visible_label"],
                    "source_image_sha256": source["sha256"],
                    "source_bytes": source["bytes"],
                    "source_dimensions": source["dimensions"],
                },
                "outputs": outputs,
                "corrections": corrections,
                "declared_alt_correction": declared_alt_correction,
                "derivative_method": {
                    "method": "embed_exact_source_JPEG_and_cover_only_left_instruction_panel",
                    "instruction_cover": {"x": 2, "y": 2, "width": 354, "height": source["dimensions"][1] - 4, "fill": "#a0b3bd"},
                    "preserved_source_divider_x": [356, 357],
                    "preserved_formula_panel_starts_x": 358,
                    "latent_english_pixels": "retained_in_embedded_JPEG_beneath_opaque_cover",
                },
            })
    manifest = {
        "schema": "jv-like-terms-assets-v1",
        "unit": UNIT,
        "status": "deterministic_source_bound_assets; visual_review_pending",
        "rules_sha256": sha(rules_raw),
        "source_assets": 3,
        "javanese_derivatives": 6,
        "indonesian_derivatives": 0,
        "assets": assets,
        "claims": {
            "visual_review": False,
            "native_language_review": False,
            "screen_reader_review": False,
        },
    }
    generated[MANIFEST_PATH.relative_to(LANG).as_posix()] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = products()
    assert generated == products(), "nondeterministic_like_terms_assets"
    for rel, raw in generated.items():
        path = LANG / rel
        if args.check:
            assert path.read_bytes() == raw, f"stale_like_terms_asset: {rel}"
        else:
            write_bytes(path, raw)
    print("a10-combine-like-terms: 3 exact JPEGs and 6 source-bound JV SVG derivatives verified")


if __name__ == "__main__":
    main()
