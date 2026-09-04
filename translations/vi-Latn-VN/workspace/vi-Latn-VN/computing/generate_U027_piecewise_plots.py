"""New deterministic U027 answer plots for exercises38/40/42/44.

No source images are edited. Default and --check are read-only; --write writes
only four explicitly authorized U027 PNG paths. Reproducible bytes depend on
the recorded Pillow version and Unicode-font bytes.
"""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import json
import math
from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    38: {"window": (-6, 3, -10, 4), "boundary": -2, "left": lambda x: x + 1,
         "right": lambda x: -2*x - 3, "left_closed": False, "right_closed": True,
         "formula": "x + 1 nếu x < −2; −2x − 3 nếu x ≥ −2",
         "ends": "Rỗng (−2,−1); kín (−2,1)", "ytick": 2},
    40: {"window": (-4, 4, -4, 4), "boundary": 0, "left": lambda x: x + 1,
         "right": lambda x: x - 1, "left_closed": False, "right_closed": False,
         "formula": "x + 1 nếu x < 0; x − 1 nếu x > 0",
         "ends": "Rỗng (0,1) và (0,−1); không nhận x = 0", "ytick": 1},
    42: {"window": (-3, 4, -4, 10), "boundary": 0, "left": lambda x: x*x,
         "right": lambda x: 1 - x, "left_closed": False, "right_closed": False,
         "formula": "x² nếu x < 0; 1 − x nếu x > 0",
         "ends": "Rỗng (0,0) và (0,1); không nhận x = 0", "ytick": 2},
    44: {"window": (-4, 2, -4, 10), "boundary": 1, "left": lambda x: x + 1,
         "right": lambda x: x*x*x, "left_closed": False, "right_closed": True,
         "formula": "x + 1 nếu x < 1; x³ nếu x ≥ 1",
         "ends": "Rỗng (1,2); kín (1,1)", "ytick": 2},
}
OUTPUTS = {n: ROOT / f"assets/A30-U027-ex{n}.png" for n in SPECS}


def find_font():
    for candidate in (Path("C:/Windows/Fonts/arial.ttf"),
                      Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Supply --font with an existing Unicode TrueType font.")


def branch_points(number, side):
    spec = SPECS[number]
    boundary = spec["boundary"]
    lo, hi = (spec["window"][0], boundary) if side == "left" else (boundary, spec["window"][1])
    return [(lo + (hi-lo)*k/400, spec[side](lo + (hi-lo)*k/400)) for k in range(401)]


def render_png(number, font_path):
    spec = SPECS[number]
    width, height, scale = 640, 560, 2
    image = Image.new("RGB", (width*scale, height*scale), "white")
    draw = ImageDraw.Draw(image)
    fonts = {size: ImageFont.truetype(str(font_path), size*scale) for size in (15,16,17,18,22)}
    left, top, right, bottom = 72, 84, 606, 420
    xmin, xmax, ymin, ymax = spec["window"]
    sx = lambda x: left+(x-xmin)/(xmax-xmin)*(right-left)
    sy = lambda y: bottom-(y-ymin)/(ymax-ymin)*(bottom-top)

    def line(points, fill="#253b4d", thickness=1):
        draw.line([(round(x*scale),round(y*scale)) for x,y in points],
                  fill=fill,width=thickness*scale)

    def text(x,y,value,size=17,anchor="mm",fill="#162536"):
        draw.text((round(x*scale),round(y*scale)),value,font=fonts[size],fill=fill,anchor=anchor)

    def arrow(start,end,fill):
        line([start,end],fill,3)
        angle=math.atan2(end[1]-start[1],end[0]-start[0])
        vertices=[end,(end[0]-11*math.cos(angle-.45),end[1]-11*math.sin(angle-.45)),
                  (end[0]-11*math.cos(angle+.45),end[1]-11*math.sin(angle+.45))]
        draw.polygon([(round(x*scale),round(y*scale)) for x,y in vertices],fill=fill)

    text(320,25,f"Đồ thị bổ sung — Bài {number}",22)
    text(320,57,spec["formula"],17)
    draw.rectangle((left*scale,top*scale,right*scale,bottom*scale),outline="#b7c5ce",width=scale)
    for x in range(math.ceil(xmin),math.floor(xmax)+1):
        line([(sx(x),top),(sx(x),bottom)],"#e0e7ec")
        text(sx(x),bottom+20,str(x).replace("-","−"),16)
    for y in range(math.ceil(ymin/spec["ytick"])*spec["ytick"],math.floor(ymax)+1,spec["ytick"]):
        line([(left,sy(y)),(right,sy(y))],"#e0e7ec")
        text(left-12,sy(y),str(y).replace("-","−"),16,"rm")
    line([(left,sy(0)),(right+10,sy(0))],"#253b4d",2)
    line([(sx(0),bottom),(sx(0),top-7)],"#253b4d",2)
    text(right+16,sy(0)+17,"x",18)
    text(sx(0)+15,top+14,"y",18)
    for side,color in (("left","#176a93"),("right","#76519c")):
        points=branch_points(number,side)
        pixels=[(sx(x),sy(y)) for x,y in points]
        line(pixels,color,3)
        if side=="left":
            arrow(pixels[12],pixels[0],color)
        else:
            arrow(pixels[-13],pixels[-1],color)
        x=spec["boundary"]; y=spec[side](x); cx,cy=sx(x),sy(y); radius=5
        draw.ellipse(((cx-radius)*scale,(cy-radius)*scale,(cx+radius)*scale,(cy+radius)*scale),
                     fill=color if spec[side+"_closed"] else "white",outline=color,width=2*scale)
    text(320,478,spec["ends"],17)
    window=f"Khung: {xmin} ≤ x ≤ {xmax}; {ymin} ≤ y ≤ {ymax}.".replace("-","−")
    text(320,511,window,16)
    text(320,541,"Mũi tên: nhánh còn tiếp tục; biên khung không phải đầu mút.",15)
    data=BytesIO()
    image.save(data,format="PNG",compress_level=9,optimize=False)
    return data.getvalue()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font",type=Path)
    parser.add_argument("--write",action="store_true")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args(); font=args.font or find_font(); results=[]
    for number,output in OUTPUTS.items():
        expected=(ROOT/f"assets/A30-U027-ex{number}.png").resolve()
        assert output.resolve()==expected and expected.parent==(ROOT/"assets").resolve()
        data=render_png(number,font)
        if args.write:
            assert expected.parent.is_dir()
            expected.write_bytes(data)
        if args.check:
            assert expected.read_bytes()==data,"PNG differs from renderer/font environment"
        results.append({"exercise":number,"output":str(output),"sha256":sha256(data).hexdigest(),
                        "bytes":len(data),"pixels":[1280,1120],"plot_window":SPECS[number]["window"],
                        "source_image":False,"wrote":args.write,"checked":args.check})
    print(json.dumps({"pillow_version":PILLOW_VERSION,"font":str(font),
                      "font_sha256":sha256(font.read_bytes()).hexdigest(),"plots":results},ensure_ascii=True,indent=2))


if __name__=="__main__":
    main()
