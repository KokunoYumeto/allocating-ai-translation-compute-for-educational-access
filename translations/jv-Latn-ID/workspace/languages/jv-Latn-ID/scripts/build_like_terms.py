"""Build the complete three-track A10 like-terms unit from finite fixtures.

The cross-unit source link is emitted only as the reviewed explicit route to
the existing evaluation reader fragment.  Narration comes exclusively from
the 68 exact source-order entries returned by ``like_terms_checks``.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

from build import STYLE, render
from config import LANG, TRACKS
from like_terms_checks import (
    EVALUATION_TARGET,
    MODULE,
    ROUTE,
    UNIT,
    narration_blocks,
    load_verified,
    sha,
    validate_reader_route,
)
from qa import Reader
from safe_io import write_bytes


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def media_maps(verified: dict) -> dict[str, dict]:
    manifest = json.loads((LANG / f"translation/{UNIT}.assets.json").read_text(encoding="utf-8"))
    result = {track: {} for track in TRACKS}
    for asset in manifest["assets"]:
        for track in TRACKS:
            output = asset["outputs"][track]
            raw = (LANG / output["path"]).read_bytes()
            assert sha(raw) == output["sha256"]
            result[track][asset["source_src"]] = {"bytes": raw, "mime_type": output["mime_type"]}
    assert all(len(row) == 3 for row in result.values())
    return result


def render_track_node(node: ET.Element, track: str, media: dict, reference: dict) -> tuple[str, int, int]:
    prefix = f"{UNIT}--{track}--"
    markup = render(node, prefix, media)
    internal = f'<a href="#{prefix}{EVALUATION_TARGET}">Tabel</a>'
    routed = (
        f'<a href="{ROUTE}" data-source-target-id="{EVALUATION_TARGET}" '
        f'data-route-fixture="{reference["id"]}" aria-label="{html.escape(reference["expected"][track], quote=True)}"></a>'
    )
    route_count = markup.count(internal)
    markup = markup.replace(internal, routed)
    generic_cue = '<h4><span lang="jv-Latn-ID">Wangsulan</span> / <span lang="id-ID">Jawaban</span></h4>'
    cue = "Wangsulan" if track.startswith("jv") else "Jawaban"
    cue_count = markup.count(generic_cue)
    markup = markup.replace(
        generic_cue,
        f'<h4 class="editorial-answer-cue" data-source-boundary="untitled-solution">{cue}</h4>',
    )
    if f"#{prefix}{EVALUATION_TARGET}" in markup or ">Tabel</a>" in markup:
        raise ValueError("unrouted_like_terms_cross_unit_reference")
    return markup, route_count, cue_count


def products() -> dict[str, bytes]:
    verified = load_verified(require_route_reader=True)
    rules, targets = verified["rules"], verified["targets"]
    generated: dict[str, bytes] = {
        f"translation/{UNIT}.{track}.cnxml": xml_bytes(root)
        for track, root in targets.items()
    }
    generated[f"provenance/{UNIT}.en.cnxml"] = xml_bytes(verified["english"])
    media = media_maps(verified)
    reference = rules["reference_fixtures"][0]
    title = targets["jv-academic"].findtext("{*}title")
    pieces = [
        '<!DOCTYPE html><html lang="id-ID"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{html.escape(title)}</title><style>{STYLE}</style></head><body><main>",
        '<header><div class="eyebrow">A10 · jv-Latn-ID / id-ID</div>',
        f'<h1 lang="jv-Latn-ID">{html.escape(title)}</h1>',
        f'<p class="source" lang="en">{MODULE} / {rules["scope"]["section"]} · complete pinned section; next section excluded</p>',
        '<p class="status">Draf telung register saka fixture winates. Ora ana audio sing disintesis; pamriksa linguistik, tampilan, lan rungon ora diwakili ing kéné.</p>',
        f'<p class="source">Pranala sumber lintas unit tumuju conto evaluasi sadurunge: <code>{html.escape(ROUTE)}</code>.</p>',
        '</header>',
    ]
    for track in TRACKS:
        pieces.append(
            f'<span id="{UNIT}--{track}--{rules["scope"]["section"]}" '
            f'data-source-id="{rules["scope"]["section"]}"></span>'
        )
    inserted_routes = inserted_cues = 0
    for index in range(1, len(verified["source"])):
        pieces.append('<div class="parallel">')
        for track, (locale, label) in TRACKS.items():
            markup, routes, cues = render_track_node(targets[track][index], track, media[track], reference)
            inserted_routes += routes
            inserted_cues += cues
            pieces.append(
                f'<article class="track" lang="{locale}" data-register="{track}">'
                f'<div class="register">{html.escape(label)}</div>{markup}</article>'
            )
        pieces.append('</div>')
    assert inserted_routes == 3
    assert inserted_cues == 24
    pieces.append('<section class="note-box"><h2>Naskah audio</h2><ul>')
    for track, (locale, label) in TRACKS.items():
        blocks = narration_blocks(verified, track)
        transcript = (
            f"# {label}\n\n"
            "Status: finite source-bound narration draft; not synthesized or listening-reviewed.\n\n"
            + "\n\n".join(f"## {mark}\n\n{body}" for mark, body in blocks)
            + "\n"
        )
        stem = f"review/audio/{UNIT}.{track}"
        generated[stem + ".md"] = transcript.encode("utf-8")
        ssml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}">'
            f'<p>{html.escape(label)}</p>\n'
            + "".join(
                f'<mark name="{html.escape(mark, quote=True)}"/><p>{html.escape(body)}</p><break time="600ms"/>\n'
                for mark, body in blocks
            )
            + "</speak>\n"
        )
        ssml_root = ET.fromstring(ssml)
        assert ssml_root.get("{http://www.w3.org/XML/1998/namespace}lang") == locale
        assert [node.get("name") for node in ssml_root.findall("{*}mark")] == [mark for mark, _ in blocks]
        assert len(ssml_root.findall("{*}mark")) == 68
        assert not ssml_root.findall(".//{*}voice") and not ssml_root.findall(".//{*}audio")
        generated[stem + ".ssml"] = ssml.encode("utf-8")
        pieces.append(
            f'<li><span lang="{locale}">{html.escape(label)}</span>: '
            f'<a href="../audio/{UNIT}.{track}.md">Naskah</a> / '
            f'<a href="../audio/{UNIT}.{track}.ssml">SSML</a></li>'
        )
    pieces.append(
        '</ul></section><footer lang="en"><p>Unofficial AI-assisted adaptation of OpenStax through the Indonesian editions by KokunoYumeto. '
        'Rice University/OpenStax, CC BY-NC-SA 4.0, subject to inherited component notices. No endorsement. '
        '<a href="../../ATTRIBUTION.md">Full attribution and original notices</a>.</p>'
        '<p>Source notation, identifiers, supplied questions, supplied solutions, and question–answer boundaries are preserved. '
        'This artifact records deterministic checks only; it does not report linguistic, visual-presentation, assistive-technology, or listening approval.</p>'
        '</footer></main></body></html>'
    )
    page = "\n".join(pieces)
    validate_reader_route(page)
    inspection = Reader()
    inspection.feed(page)
    assert len(inspection.ids) == len(set(inspection.ids))
    assert inspection.maths == 3 * 62
    assert len(inspection.images) == 3 * 3
    assert all(image.get("alt") and image["src"].startswith("data:image/") for image in inspection.images)
    for track in TRACKS:
        assert all(
            f'{UNIT}--{track}--{node.get("id")}' in inspection.ids
            for node in verified["source"].iter() if node.get("id")
        )
    generated[f"review/units/{UNIT}.html"] = page.encode("utf-8")
    output_hashes = {path: sha(raw) for path, raw in generated.items()}
    progress = {
        "schema": "jv-like-terms-production-in-progress-v1",
        "unit": UNIT,
        "status": "deterministic_three_track_outputs_and_real_route_verified; shared_inventory_handoff_pending",
        "scope": {
            "module": MODULE,
            "section": rules["scope"]["section"],
            "direct_children": 35,
            "source_nodes": 744,
            "source_ids": 108,
            "mathml": 62,
            "prose_fixtures": 45,
            "heading_fixtures": 10,
            "math_layouts": 2,
            "source_images": 3,
            "javanese_image_derivatives": 6,
            "exercises": 12,
            "solutions": 12,
            "question_parts": 19,
            "narration_entries_per_track": 68,
        },
        "inputs": {
            "rules_sha256": sha(verified["rules_raw"]),
            "edits_sha256": rules["scope"]["edits_sha256"],
            "shared_edits_sha256": rules["scope"]["shared_edits_sha256"],
            "source_lock_sha256": rules["scope"]["source_lock_sha256"],
            "id_module_sha256": rules["scope"]["indonesian_sha256"],
            "en_module_sha256": rules["scope"]["english_sha256"],
            "asset_manifest_sha256": verified["assets"]["manifest_sha256"],
        },
        "route": verified["route"],
        "outputs_sha256": output_hashes,
        "claims": {
            "synthesized_audio_files": 0,
            "linguistic_approval": False,
            "visual_presentation_approval": False,
            "assistive_technology_approval": False,
            "listening_approval": False,
            "whole_module_complete": False,
            "full_assignment_complete": False,
        },
        "exclusions": {
            "next_section": rules["scope"]["next_excluded_section"],
            "next_first_paragraph": rules["scope"]["next_excluded_first_paragraph"],
            "unstated_unmatched_9y_answer_invented": False,
            "fake_cross_unit_stub_created": False,
            "provider_or_voice_selected": False,
        },
    }
    generated[f"qa/{UNIT}.in-progress.json"] = (
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = products()
    for path, raw in generated.items():
        destination = LANG / path
        if args.check:
            assert destination.read_bytes() == raw, f"stale_like_terms_output:{path}"
        else:
            write_bytes(destination, raw)
    print("a10-combine-like-terms: complete finite three-track section and exact cross-unit route verified")


if __name__ == "__main__":
    main()
