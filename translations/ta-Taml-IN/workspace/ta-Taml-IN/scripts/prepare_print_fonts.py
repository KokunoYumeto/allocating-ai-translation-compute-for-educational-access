"""Create deterministic static Tamil font instances for Chromium PDF printing.

The source variable font is read-only. Probe HTML/PDF outputs are optional and
stay under ignored tmp/pdfs; they are evidence, not learner deliverables.
Requires fontTools in the invoking Python environment.
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
SOURCE = LANG / "assets/fonts/NotoSansTamil.ttf"
DEFAULT_OUT = ROOT / "tmp/pdfs/font-probe"
DEFAULT_EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font_names(font):
    names = {}
    for identifier, label in ((1, "family"), (2, "subfamily"), (4, "full"), (6, "postscript")):
        values = []
        for record in font["name"].names:
            if record.nameID == identifier:
                try:
                    value = record.toUnicode()
                except UnicodeDecodeError:
                    continue
                if value not in values:
                    values.append(value)
        names[label] = values
    return names


def prepare(out, weights):
    out.mkdir(parents=True, exist_ok=True)
    assert out.is_relative_to((ROOT / "tmp/pdfs").resolve()), "Print fonts must stay under ignored tmp/pdfs"
    assert SOURCE.is_file() and shutil.disk_usage(out).free > 100 * 1024 * 1024
    source_hash = sha(SOURCE)
    probe = TTFont(SOURCE)
    axes = {axis.axisTag: (axis.minValue, axis.defaultValue, axis.maxValue) for axis in probe["fvar"].axes}
    assert set(axes) == {"wght", "wdth"} and axes["wdth"][1] == 100
    outputs = []
    for weight in weights:
        assert axes["wght"][0] <= weight <= axes["wght"][2]
        variable = TTFont(SOURCE, recalcTimestamp=False)
        # Do not update names: this font's STAT table has no AxisValue at 650,
        # while the print CSS legitimately uses that weight. CSS face
        # descriptors and OS/2.usWeightClass identify the pinned static faces.
        static = instantiateVariableFont(variable, {"wght": weight, "wdth": axes["wdth"][1]}, inplace=False, updateFontNames=False)
        assert "fvar" not in static and "gvar" not in static
        assert static["OS/2"].usWeightClass == weight
        static.recalcTimestamp = False
        path = out / f"NotoSansTamil-Print-{weight}.ttf"
        static.save(path, reorderTables=False)
        check = TTFont(path)
        assert "fvar" not in check and "gvar" not in check and check["OS/2"].usWeightClass == weight
        outputs.append({"weight": weight, "path": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "names": font_names(check), "variation_tables_remaining": sorted(set(check.keys()) & {"fvar", "gvar", "HVAR", "MVAR", "VVAR", "CFF2"})})
    assert sha(SOURCE) == source_hash, "Source variable font changed"
    return {"source": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": source_hash, "source_axes": axes, "static_instances": outputs}


def fixture(out, manifest, mode):
    if mode == "variable":
        source = os.path.relpath(SOURCE, out).replace("\\", "/")
        faces = f"@font-face{{font-family:ProbeTamil;src:url('{source}');font-weight:100 900;font-style:normal}}"
    else:
        faces = "".join(f"@font-face{{font-family:ProbeTamil;src:url('{item['path']}');font-weight:{item['weight']};font-style:normal}}" for item in manifest["static_instances"])
    sample = "இடமதிப்பு · முழு எண்கள் · பூச்சியம் · தமிழ் உரைச் சோதனை"
    lines = "".join(f'<p class="w{item["weight"]}"><span lang="en">weight {item["weight"]}:</span> {html.escape(sample)}</p>' for item in manifest["static_instances"])
    page = f'''<!doctype html><html lang="ta-Taml-IN"><head><meta charset="utf-8"/><style>{faces}@page{{size:A4;margin:20mm}}body{{font-family:ProbeTamil,sans-serif;font-size:18pt;line-height:1.8}}{''.join(f'.w{item["weight"]}{{font-weight:{item["weight"]}}}' for item in manifest["static_instances"])}math{{font-family:"Cambria Math",serif}}math mtext{{font-family:ProbeTamil,sans-serif;font-weight:600}}</style></head><body><h1>தமிழ் PDF எழுத்துருச் சோதனை — {mode}</h1>{lines}<p>எண்கள்: 0, 1, 2, 10, 100, 374.</p><math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mtext>இடமதிப்பு</mtext><mo>:</mo><mn>300</mn><mo>+</mo><mn>70</mn><mo>+</mo><mn>4</mn><mo>=</mo><mn>374</mn></mrow></math></body></html>'''
    path = out / f"probe-{mode}.html"
    path.write_text(page, encoding="utf-8", newline="\n")
    return path


def render(edge, out, page):
    assert edge.is_file()
    target = page.with_suffix(".pdf")
    profile = out / ("edge-profile-" + page.stem)
    profile.mkdir(exist_ok=True)
    command = [str(edge), "--headless", "--disable-gpu", "--disable-background-networking", "--disable-sync", "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--no-pdf-header-footer", "--export-tagged-pdf", "--virtual-time-budget=2000", f"--user-data-dir={profile}", f"--print-to-pdf={target}", page.as_uri()]
    subprocess.run(command, check=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert target.is_file() and target.stat().st_size > 10_000
    return {"path": target.name, "bytes": target.stat().st_size, "sha256": sha(target)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--weights", nargs="+", type=int, default=[400, 600, 650, 700])
    parser.add_argument("--write-probes", action="store_true")
    parser.add_argument("--render-probes", action="store_true")
    parser.add_argument("--chromium", type=Path, default=DEFAULT_EDGE)
    args = parser.parse_args()
    out = args.out.resolve()
    weights = sorted(set(args.weights))
    assert weights and args.render_probes <= args.write_probes
    manifest = prepare(out, weights)
    if args.write_probes:
        pages = [fixture(out, manifest, mode) for mode in ("variable", "static")]
        manifest["fixtures"] = [{"path": page.name, "sha256": sha(page)} for page in pages]
        if args.render_probes:
            manifest["pdfs"] = [render(args.chromium.resolve(), out, page) for page in pages]
    manifest_path = out / "font-probe-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
