"""Deterministic, newly authored closed-domain plots for A30-U015.

Uses Pillow (no downloads). Original OpenStax JPEGs are never opened or edited.
Run --write to create only computing/generated-A30-U015/*.png and manifest.json.
"""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import json
from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "computing/generated-A30-U015"
PLOTS = [
    {"number":76,"kind":"square","domain":["-0.1","0.1"],"range":["0","0.01"],"formula":"y = x²"},
    {"number":77,"kind":"square","domain":["-10","10"],"range":["0","100"],"formula":"y = x²"},
    {"number":78,"kind":"square","domain":["-100","100"],"range":["0","10000"],"formula":"y = x²"},
    {"number":79,"kind":"cube","domain":["-0.1","0.1"],"range":["-0.001","0.001"],"formula":"y = x³"},
    {"number":80,"kind":"cube","domain":["-10","10"],"range":["-1000","1000"],"formula":"y = x³"},
    {"number":81,"kind":"cube","domain":["-100","100"],"range":["-1000000","1000000"],"formula":"y = x³"},
    {"number":82,"kind":"sqrt","domain":["0","0.01"],"range":["0","0.1"],"formula":"y = √x"},
    {"number":83,"kind":"sqrt","domain":["0","100"],"range":["0","10"],"formula":"y = √x"},
    {"number":84,"kind":"sqrt","domain":["0","10000"],"range":["0","100"],"formula":"y = √x"},
    {"number":85,"kind":"cbrt","domain":["-0.001","0.001"],"range":["-0.1","0.1"],"formula":"y = ³√x"},
    {"number":86,"kind":"cbrt","domain":["-1000","1000"],"range":["-10","10"],"formula":"y = ³√x"},
    {"number":87,"kind":"cbrt","domain":["-1000000","1000000"],"range":["-100","100"],"formula":"y = ³√x"},
]


def find_font():
    for path in (Path("C:/Windows/Fonts/arial.ttf"),
                 Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        if path.is_file():
            return path
    raise FileNotFoundError("Pass --font with a readable Unicode TrueType font.")


def samples(plot, steps=320):
    a, b = map(float, plot["domain"])
    c, d = map(float, plot["range"])
    result = []
    for index in range(steps + 1):
        t = index / steps
        if plot["kind"] in ("square", "cube"):
            x = a + (b - a) * t
            y = x ** (2 if plot["kind"] == "square" else 3)
        else:
            y = c + (d - c) * t
            x = y ** (2 if plot["kind"] == "sqrt" else 3)
        result.append((x, y))
    # Avoid machine-rounding discrepancies at exact declared endpoints.
    if plot["kind"] == "square":
        result[0], result[-1] = (a, d), (b, d)
    else:
        result[0], result[-1] = (a, c), (b, d)
    return result


def number_label(value):
    if value == 0:
        return "0"
    if abs(value) >= 1000 and value.is_integer():
        return f"{int(value):,}".replace("-", "−")
    return f"{value:.6g}".replace("-", "−")


def render_png(plot, font_path):
    scale = 2
    width, height = 620, 420
    image = Image.new("RGB", (width * scale, height * scale), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(font_path), 20 * scale)
    title_font = ImageFont.truetype(str(font_path), 21 * scale)
    small_font = ImageFont.truetype(str(font_path), 19 * scale)
    left, top, right, bottom = 130, 75, 565, 315
    a, b = map(float, plot["domain"])
    c, d = map(float, plot["range"])
    xp, yp = (b - a) * .09, (d - c) * .10
    xmin, xmax, ymin, ymax = a - xp, b + xp, c - yp, d + yp
    sx = lambda x: left + (x - xmin) / (xmax - xmin) * (right - left)
    sy = lambda y: bottom - (y - ymin) / (ymax - ymin) * (bottom - top)

    def line(points, fill, width=1):
        draw.line([(round(x * scale), round(y * scale)) for x, y in points],
                  fill=fill, width=width * scale)

    def text(x, y, value, anchor="mm", selected_font=font, fill="#162536"):
        draw.text((round(x * scale), round(y * scale)), value, font=selected_font,
                  fill=fill, anchor=anchor)

    text(310, 20, f"Đồ thị bổ sung — Bài {plot['number']}", selected_font=title_font)
    text(310, 49, plot["formula"])
    draw.rectangle((left * scale, top * scale, right * scale, bottom * scale), outline="#c5ccd3", width=scale)
    xticks = [a, 0.0, b] if a < 0 else [a, (a + b) / 2, b]
    yticks = [c, 0.0, d] if c < 0 else [c, (c + d) / 2, d]
    for x in xticks:
        px = sx(x)
        line([(px, top), (px, bottom)], "#d8dee5")
        text(px, bottom + 22, number_label(x))
    for y in yticks:
        py = sy(y)
        line([(left, py), (right, py)], "#d8dee5")
        text(left - 12, py, number_label(y), anchor="rm")
    if xmin <= 0 <= xmax:
        line([(sx(0), top), (sx(0), bottom)], "#758294")
    if ymin <= 0 <= ymax:
        line([(left, sy(0)), (right, sy(0))], "#758294")
    points = samples(plot)
    line([(sx(x), sy(y)) for x, y in points], "#155b9a", 3)
    for x, y in (points[0], points[-1]):
        px, py, radius = sx(x) * scale, sy(y) * scale, 5 * scale
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill="#155b9a")
    text(right + 20, bottom + 22, "x")
    text(left - 12, top - 20, "y", anchor="rm")
    text(310, 379, "Hai đầu mút tô kín thuộc đồ thị.", selected_font=small_font)
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    stream = BytesIO()
    image.save(stream, format="PNG", optimize=False, compress_level=9)
    return stream.getvalue()


def build_manifest(font_path, write=False):
    manifest = {
        "unit":"A30-U015", "authorship":"new Vietnamese instructional plots, not source images",
        "pillow_version":PILLOW_VERSION, "font_filename":font_path.name,
        "font_sha256":sha256(font_path.read_bytes()).hexdigest(),
        "canvas_pixels":[620,420], "sample_segments":320,
        "curve_arrows":False, "filled_included_endpoints":True,
        "independent_axis_scaling":True, "plots":[],
    }
    if write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
    for plot in PLOTS:
        data = render_png(plot, font_path)
        filename = f"A30-U015-ex{plot['number']}-closed.png"
        if write:
            (OUTPUT / filename).write_bytes(data)
        else:
            assert (OUTPUT / filename).read_bytes() == data, filename
        manifest["plots"].append({
            **plot, "filename":filename, "sha256":sha256(data).hexdigest(), "bytes":len(data),
            "endpoints":samples(plot)[::320],
        })
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if write:
        (OUTPUT / "manifest.json").write_bytes(encoded)
    else:
        assert (OUTPUT / "manifest.json").read_bytes() == encoded
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write only namespaced generated outputs.")
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    manifest = build_manifest(args.font or find_font(), write=args.write)
    print(f"PASS: {len(manifest['plots'])} deterministic closed-domain plots; write={args.write}")
