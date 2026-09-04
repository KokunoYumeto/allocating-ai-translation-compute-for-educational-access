"""Two new U029 reciprocal plots; default/--check are read-only.

--write writes only the two authorized assets/A30-U029-ex56-*.png paths.
The exact closed x domains come from the prompt. The larger y display ranges
are visual scaffolding, not answers. No source image is altered.
"""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import json
from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "negative": {"domain": (-0.5, -0.1), "y_window": (-11, -1),
                 "range": (-10, -2), "ticks": (-10, -8, -6, -4, -2),
                 "heading": "y = 1/x; −0.5 ≤ x ≤ −0.1",
                 "endpoints": "Hai đầu mút kín: (−0.5,−2) và (−0.1,−10)"},
    "positive": {"domain": (0.1, 0.5), "y_window": (1, 11),
                 "range": (2, 10), "ticks": (2, 4, 6, 8, 10),
                 "heading": "y = 1/x; 0.1 ≤ x ≤ 0.5",
                 "endpoints": "Hai đầu mút kín: (0.1,10) và (0.5,2)"},
}
OUTPUTS = {key: ROOT / f"assets/A30-U029-ex56-{key}.png" for key in SPECS}


def find_font():
    for candidate in (Path("C:/Windows/Fonts/arial.ttf"),
                      Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Supply --font with an existing Unicode TrueType font.")


def curve_points(key):
    lo, hi = SPECS[key]["domain"]
    #Both endpoints included. No continuation arrow or connection through x=0.
    return [(lo + (hi-lo)*k/600, 1/(lo + (hi-lo)*k/600)) for k in range(601)]


def render_png(key, font_path):
    spec = SPECS[key]
    width, height, scale = 640, 560, 2
    image = Image.new("RGB", (width*scale, height*scale), "white")
    draw = ImageDraw.Draw(image)
    fonts = {n: ImageFont.truetype(str(font_path), n*scale) for n in (15,16,17,18,22)}
    left, top, right, bottom = 80, 98, 602, 412
    xmin, xmax = spec["domain"]; ymin, ymax = spec["y_window"]
    sx = lambda x: left+(x-xmin)/(xmax-xmin)*(right-left)
    sy = lambda y: bottom-(y-ymin)/(ymax-ymin)*(bottom-top)

    def line(points, color, thickness=1):
        draw.line([(round(x*scale), round(y*scale)) for x,y in points],
                  fill=color, width=thickness*scale)

    def text(x,y,value,size=17,anchor="mm"):
        draw.text((round(x*scale),round(y*scale)),value,font=fonts[size],
                  fill="#162536",anchor=anchor)

    text(320,25,"Đồ thị bổ sung — Bài 56",22)
    text(320,61,spec["heading"],18)
    for k in range(5):
        x=round(xmin+k/10,1)
        line([(sx(x),top),(sx(x),bottom)],"#dde6ec")
        text(sx(x),bottom+21,f"{x:.1f}".replace("-","−"),16)
    for y in spec["ticks"]:
        line([(left,sy(y)),(right,sy(y))],"#dde6ec")
        text(left-12,sy(y),str(y).replace("-","−"),16,"rm")
    draw.rectangle((left*scale,top*scale,right*scale,bottom*scale),
                   outline="#a9bbc7",width=scale)
    text((left+right)/2,bottom+46,"x",18)
    text(left-27,top-14,"y",18)
    pixels=[(sx(x),sy(y)) for x,y in curve_points(key)]
    line(pixels,"#176a93",3)
    for x,y in (pixels[0],pixels[-1]):
        radius=5
        draw.ellipse(((x-radius)*scale,(y-radius)*scale,
                      (x+radius)*scale,(y+radius)*scale),
                     fill="#176a93",outline="#176a93",width=2*scale)
    text(320,487,spec["endpoints"],16)
    text(320,514,f"Khung theo y: {ymin} ≤ y ≤ {ymax}.".replace("-","−"),16)
    text(320,545,"Chỉ vẽ trên đoạn x đã cho; không kéo dài qua đầu mút.",15)
    buffer=BytesIO()
    image.save(buffer,format="PNG",compress_level=9,optimize=False)
    return buffer.getvalue()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font",type=Path)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--write",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=parser.parse_args(); font=args.font or find_font(); results=[]
    for key, output in OUTPUTS.items():
        expected=(ROOT/f"assets/A30-U029-ex56-{key}.png").resolve()
        assert output.resolve()==expected and expected.parent==(ROOT/"assets").resolve()
        data=render_png(key,font)
        if args.write:
            assert expected.parent.is_dir()
            expected.write_bytes(data)
        if args.check:
            assert expected.read_bytes()==data, "PNG differs from renderer/font environment"
        results.append({"exercise":56,"case":key,"output":str(output),
                        "sha256":sha256(data).hexdigest(),"bytes":len(data),
                        "pixels":[1280,1120],"closed_x_domain":SPECS[key]["domain"],
                        "y_display_window":SPECS[key]["y_window"],
                        "exact_range":SPECS[key]["range"],
                        "source_image":False,"wrote":args.write,"checked":args.check})
    print(json.dumps({"pillow_version":PILLOW_VERSION,"font":str(font),
                      "font_sha256":sha256(font.read_bytes()).hexdigest(),
                      "plots":results},ensure_ascii=True,indent=2))


if __name__=="__main__":
    main()
