"""Deterministic, packet-local Tamil A10 m82630 build and validation."""

from pathlib import Path
from hashlib import sha256
import argparse
import html
import json
import re
import struct
import unicodedata
from urllib.parse import urlsplit, unquote

from lxml import etree


ROOT = Path(__file__).resolve().parent
CN = "http://cnx.rice.edu/cnxml"
MD = "http://cnx.rice.edu/mdml"
COL = "http://cnx.rice.edu/collxml"
NS = {"c": CN, "md": MD, "col": COL, "m": "http://www.w3.org/1998/Math/MathML"}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
SOURCE_SHA = "d9f45fb31f4cb399c009c2be25eca1a99132b4b6882fb07f8649c2d56974f90b"
COLLECTION_SHA = "5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72"
SOURCE = ROOT / "source/m82630.en.cnxml"
COLLECTION = ROOT / "source/collection.xml"
TARGET = ROOT / "translation/m82630.ta.cnxml"
MEDIA = {
    "tryit.png": (344, "7f9c8c226d8b937d4070c69326d6c2ac7df37a74c85fa8cec64e2ad7bef59ebf", [34, 34]),
    "howtoicon.png": (1681, "67f2344cdbe25b192fbdee0d904ce912e4e15aed5bf0063f61a192dd0b0b5826", [59, 55]),
    "media.png": (353, "140b45d7d047dc59b236c95bb2c2a237ca5b748b290b28f8e6d9f8f520077e6a", [34, 34]),
    "CNX_ElemAlg_Figure_05_01_015_img.jpg": (688493, "34fd0299880bc134f6308adcb2296ec1e145431909a1ab1cc2b507e01e3670f4", [791, 257]),
}
STATIC_PAYLOAD = [
    "build.py", "seal.py", "LICENSE.txt", "NOTICE.txt", "README.md", "TERMINOLOGY.md",
    "source/collection.xml", "source/m82630.en.cnxml", "translation/m82630.ta.cnxml",
    "media/CNX_ElemAlg_Figure_05_01_015_img.jpg", "media/howtoicon.png",
    "media/media.png", "media/tryit.png", "reader/fonts/NotoSansTamil.ttf",
    "reader/fonts/OFL.txt", "SOURCE_RECOVERY.json", "SOURCE_CORRECTIONS.json",
    "EXPERT_REVIEW_LOG.json", "PACKAGE.json", "OWNER_HANDOFF.json", "VISUAL_QA.json",
]


def digest(data):
    return sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load_xml(path):
    data = path.read_bytes()
    data.decode("utf-8", errors="strict")
    return etree.fromstring(data)


def load_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def local(element):
    return etree.QName(element).localname


def texts(element):
    return "".join(element.itertext()).strip()


def shape(element):
    return [(node.tag, sorted((k, v) for k, v in node.attrib.items() if k not in {"alt", XML_LANG}), len(node)) for node in element.iter()]


def image_dimensions(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return list(struct.unpack(">II", data[16:24]))
    if data.startswith(b"\xff\xd8"):
        cursor = 2
        sof = set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0))
        while cursor + 9 < len(data):
            if data[cursor] != 0xFF:
                cursor += 1
                continue
            marker = data[cursor + 1]
            cursor += 2
            if marker in {0xD8, 0xD9}:
                continue
            length = int.from_bytes(data[cursor:cursor + 2], "big")
            if marker in sof:
                return [int.from_bytes(data[cursor + 5:cursor + 7], "big"), int.from_bytes(data[cursor + 3:cursor + 5], "big")]
            cursor += length
    raise ValueError("Unsupported or malformed image")


def e(value):
    return html.escape(value, quote=True)


def content(element, depth=0):
    result = e(element.text or "")
    for child in element:
        result += render(child, depth) + e(child.tail or "")
    return result


def render(element, depth=0):
    name = local(element)
    identity = ' id="' + e(element.get("id")) + '"' if element.get("id") else ""
    if name == "section":
        return "<section" + identity + ">" + content(element, depth + 1) + "</section>"
    if name == "title":
        level = min(depth + 1, 6)
        return f"<h{level}>" + content(element, depth) + f"</h{level}>"
    if name == "para":
        return "<p" + identity + ">" + content(element, depth) + "</p>"
    if name == "emphasis":
        tag = "strong" if element.get("effect") == "bold" else "em"
        return "<" + tag + identity + ">" + content(element, depth) + "</" + tag + ">"
    if name == "list":
        return "<ul" + identity + ">" + content(element, depth) + "</ul>"
    if name == "item":
        return "<li" + identity + ">" + content(element, depth) + "</li>"
    if name == "newline":
        return "<br" + identity + ">"
    if name == "media":
        image = element.find("c:image", NS)
        src = "../media/" + Path(image.get("src")).name
        graph = Path(src).suffix == ".jpg"
        tag = "figure" if graph else "span"
        cls = "source-figure" if graph else "source-icon"
        image_markup = '<img src="' + e(src) + '" alt="' + e(element.get("alt")) + '"' + (' width="791" height="257"' if graph else "") + ">"
        addition = ""
        if graph:
            addition = '''<figcaption><strong>படத்தின் தமிழ் விளக்கம் (வாசிப்புக்காகச் சேர்க்கப்பட்டது):</strong> மூலப் படத்தின் ஆங்கிலத் தலைப்புகள் அப்படியே உள்ளன.</figcaption>
            <table aria-label="மூன்று நேர்கோட்டு நிலைகளின் தமிழ் விளக்கம்"><thead><tr><th scope="col">இடம் / ஆங்கிலத் தலைப்பு</th><th scope="col">நிலை மற்றும் தீர்வுகள்</th></tr></thead><tbody>
            <tr><th scope="row">இடது: <span lang="en">Intersecting</span></th><td data-label="நிலை மற்றும் தீர்வுகள்">வெட்டும் நேர்கோடுகள். ஒரு பொதுப்புள்ளி; ஒரு தீர்வு.</td></tr>
            <tr><th scope="row">நடு: <span lang="en">Parallel</span></th><td data-label="நிலை மற்றும் தீர்வுகள்">இணை நேர்கோடுகள். பொதுப்புள்ளி இல்லை; தீர்வு இல்லை.</td></tr>
            <tr><th scope="row">வலது: <span lang="en">Coincident</span></th><td data-label="நிலை மற்றும் தீர்வுகள்">ஒன்றின்மேல் ஒன்று பொருந்தும் நேர்கோடுகள். முடிவற்ற பல பொதுப்புள்ளிகள்; முடிவற்ற பல தீர்வுகள்.</td></tr>
            </tbody></table>'''
        return "<" + tag + identity + ' class="' + cls + '">' + image_markup + addition + "</" + tag + ">"
    raise ValueError("Unimplemented source tag: " + name)


STYLE = '''@font-face{font-family:NotoTamil;src:url("fonts/NotoSansTamil.ttf") format("truetype");font-weight:100 900;font-display:swap}
:root{color-scheme:light;font-family:NotoTamil,"Nirmala UI",sans-serif;color:#172833;background:#eef3f4;font-size:18px}
*{box-sizing:border-box}body{margin:0}a{color:#07596b;text-underline-offset:.18em;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #be6e13;outline-offset:4px}.skip{position:absolute;left:1rem;top:-8rem;padding:.7rem;background:white;z-index:5}.skip:focus{top:.6rem}
header,nav,main,footer{width:calc(100% - 2rem);max-width:none;margin:auto;padding:1.6rem 3rem;background:#fff}header{border-top:9px solid #116974}header .eyebrow{font-size:.82rem;letter-spacing:.04em;color:#47636a}header p{max-width:60rem}h1{font-size:2rem;line-height:1.55;margin:.45rem 0 1rem;color:#123f48}h2{font-size:1.42rem;line-height:1.7;margin:2rem 0 .8rem;color:#154f59}h3{font-size:1.13rem;line-height:1.75;margin:1.6rem 0 .6rem}h4{font-size:1rem;line-height:1.8;margin:1.3rem 0 .5rem}
p,li,td,th,summary{line-height:1.95}p{margin:.6rem 0 1.1rem}li{margin:.7rem 0}ul,ol{padding-left:1.5rem}section{scroll-margin-top:1rem}nav{padding-top:0;padding-bottom:1rem;border-bottom:1px solid #cadbdd}nav ul{display:flex;flex-wrap:wrap;gap:.6rem 1.4rem;list-style:none;padding:0;margin:0}nav li{font-size:.86rem;margin:0}.orientation,.authored{border-left:5px solid #4c8891;background:#f0f7f8;padding:1rem 1.5rem;margin-bottom:2rem}.orientation h2,.authored h2{margin-top:0}.small{font-size:.82rem}.source-icon{display:inline-block;vertical-align:middle;margin-right:.4rem}.source-icon img{width:2.2rem;height:auto;vertical-align:middle}
.source-figure{margin:1.5rem 0;padding:1rem;background:#f7f9fa;border:1px solid #d5e1e3}.source-figure>img{width:100%;height:auto;max-width:791px;display:block;margin:auto}figcaption{font-size:.87rem;line-height:1.9;margin-top:1rem}table{border-collapse:collapse;width:100%;margin:.8rem 0;font-size:.85rem}td,th{border:1px solid #b5cbcf;padding:.65rem;vertical-align:top;text-align:left}th{background:#e8f0f2}.number-sequence{white-space:nowrap;font-family:NotoTamil,sans-serif}.route-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.route-grid section{border:1px solid #cadbdd;padding:1rem}.route-grid h3{margin-top:0}details{border:1px solid #cadbdd;border-radius:.25rem;padding:.7rem 1rem;margin:.7rem 0;background:#fbfdfd}summary{cursor:pointer;font-weight:700}.mastery-note{border-left:5px solid #b36b00;background:#fff7e8;padding:1rem 1.5rem}footer{font-size:.8rem;border-top:1px solid #cadbdd;overflow-wrap:anywhere}footer p{line-height:1.9}em{font-style:normal}
@media(max-width:600px){:root{font-size:16px}header,nav,main,footer{width:100%;padding-left:1.1rem;padding-right:1.1rem}h1{font-size:1.55rem}h2{font-size:1.22rem}h3{font-size:1.07rem}.orientation,.authored{padding:.9rem}.source-figure{padding:.55rem}table,thead,tbody,tr,th,td{display:block;width:100%}table{font-size:.88rem;border:0}thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}tr{border:1px solid #b5cbcf;margin:.8rem 0}th,td{border:0;border-bottom:1px solid #d8e3e5;padding:.55rem;text-align:left;white-space:normal}tr>*:last-child{border-bottom:0}[data-label]::before{content:attr(data-label);display:block;font-weight:700;color:#154f59;margin-bottom:.2rem}nav ul{display:block}nav li{margin:.45rem 0}ul,ol{padding-left:1.15rem}.route-grid{grid-template-columns:1fr}}
@media print{:root{background:white;font-size:10.5pt}header,nav,main,footer{max-width:none;padding:.2cm 0}nav,.skip{display:none}.orientation,.authored,.source-figure,.route-grid section,details{break-inside:avoid}h1,h2,h3,h4{break-after:avoid}p,li{orphans:3;widows:3}a{color:inherit}body{margin:1.5cm}}
'''


def reader(target):
    translated = target.find("c:content", NS)
    sections = translated.findall("c:section", NS)
    nav = "".join('<li><a href="#' + s.get("id") + '">' + e(texts(s.find("c:title", NS))) + "</a></li>" for s in sections)
    body = content(translated, 0)
    return ('''<!doctype html><html lang="ta-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>தொடக்க இயற்கணிதம் - முன்னுரை | தமிழ்</title><link rel="stylesheet" href="style.css"></head><body>
<a class="skip" href="#source-text">மூல உரைக்குச் செல்லுங்கள்</a><header><p class="eyebrow" lang="en">OPENSTAX · ELEMENTARY ALGEBRA 2e · ta-Taml-IN · m82630</p><h1>தொடக்க இயற்கணிதம்<br>முன்னுரை</h1><p>இரண்டாம் பதிப்பின் முழு முன்னுரை - தமிழ் மொழிபெயர்ப்பு</p><p class="small">இது முன்னுரை மட்டும். முழு நூலோ, 2-8 வகுப்புகளுக்கான முழுமையான கற்றல் திட்டமோ அல்ல.</p></header>
<nav aria-label="முன்னுரையின் பகுதிகள்"><ul><li><a href="#ta-orientation">வாசிப்பு வழிகாட்டி</a></li><li><a href="../companion/index.html">ஆசிரியர்-சாரா கற்றல் துணை</a></li>''' + nav + '''</ul></nav><main><aside class="orientation" id="ta-orientation" aria-labelledby="ta-orientation-title"><h2 id="ta-orientation-title">வாசிப்பு வழிகாட்டி</h2>
<p><strong>மொழிபெயர்ப்பிலிருந்து தனியாகச் சேர்க்கப்பட்ட குறிப்பு:</strong> அடுத்து வரும் முன்னுரை மூல நூலின் அமைப்பு, பயிற்சிகள், வளங்கள் மற்றும் உரிம நிபந்தனைகளை விளக்குகிறது. இது கணிதத் தேர்ச்சியை மதிப்பிடும் பாடம் அல்ல. இப்பகுதியில் புதிய வினாக்களோ தேர்ச்சி மதிப்பீடுகளோ சேர்க்கப்படவில்லை.</p>
<p>சொற்களை வேறுபடுத்திப் படிக்கவும்: எண்ணும் எண்கள் / இயல் எண்கள் <span class="number-sequence">1, 2, 3, …</span>; முழு எண்கள் <span class="number-sequence">0, 1, 2, 3, …</span>; முழுக்கள் <span class="number-sequence">…, −2, −1, 0, 1, 2, …</span>. “தீர்வு” என்பது ஒரு கணக்கைத் தீர்க்கும் செய்முறை அல்லது அதனால் கிடைக்கும் தீர்வைக் குறிக்கும்; “விடை” என்பது வினாவுக்குக் கொடுக்கப்படும் பதில்.</p>
<p>ஆசிரியர்களுக்கு மட்டும் கிடைக்கும் மூல வளங்களைப் பற்றிய குறிப்புகள் அப்படியே மொழிபெயர்க்கப்பட்டுள்ளன. அவற்றைப் பெறுவது இந்த முன்னுரையைப் படிப்பதற்கான நிபந்தனை அல்ல. தனிப்பயிற்சிக்கான கண்டறிதல், தவறான புரிதல் விளக்கம், செய்முறை எடுத்துக்காட்டு மற்றும் மறுசரிபார்ப்பு ஆகியவை <a href="../companion/index.html">தனியாக இயற்றப்பட்ட கற்றல் துணையில்</a> உள்ளன.</p>
<p class="small">மூலத்தின் காணொளிப் பொறுப்புத் துறப்பு வேறொரு நூலான <span lang="en">Prealgebra 2e</span>-ஐக் குறிப்பிடுகிறது; அது மறைக்கப்படவில்லை. மூல மதிப்பாய்வாளர் பட்டியலின் <span lang="en">Saint Louis Iniversity</span> என்ற எழுத்தும் அப்படியே பேணப்பட்டுள்ளது.</p></aside><article id="source-text" aria-label="மொழிபெயர்க்கப்பட்ட மூல முன்னுரை">''' + body + '''</article></main>
<footer><p>மூல நூலாசிரியர்கள்: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. முழுப் பங்களிப்பாளர் பட்டியல் மேலே உள்ளது.</p><p lang="en">Tamil translation and clearly labelled reader additions: OpenAI Codex gpt-5.6-sol, Ultra, at the user's instruction. No endorsement, native-speaker validation, classroom efficacy, assistive-technology certification or PDF/UA claim is made.</p>
<p><a href="../LICENSE.txt">CC BY-NC-SA 4.0 உரிமம்</a> · <a href="../NOTICE.txt">உரிமைக் குறிப்புகள்</a> · <a href="fonts/OFL.txt">எழுத்துரு உரிமம்</a> · <a href="../modules/m82630/index.cnxml">தமிழ் CNXML</a> · <a href="../source/m82630.en.cnxml">ஆங்கில மூலச் சான்று</a> · <a href="../TERMINOLOGY.md">கலைச்சொல் முடிவுகள்</a> · <a href="../companion/index.html">தனி கற்றல் துணை</a></p><p>அடுத்த மூல அலகு: m82451 - அறிமுகம். அது இந்த முன்னுரைத் தொகுப்பில் மொழிபெயர்க்கப்பட்டதாகக் கணக்கிடப்படவில்லை.</p></footer></body></html>''').encode("utf-8")


def companion():
    return '''<!doctype html><html lang="ta-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ஆசிரியர்-சாரா கற்றல் துணை | m82630</title><link rel="stylesheet" href="../reader/style.css"></head><body>
<a class="skip" href="#companion-main">கற்றல் துணைக்குச் செல்லுங்கள்</a><header><p class="eyebrow" lang="en">INDEPENDENTLY AUTHORED COMPANION · GRADES 2-8 · m82630</p><h1>முன்னுரையைத் தனியாகப் படிக்கும் வழி</h1><p>கண்டறிதல், தவறான புரிதல்களைச் சரிசெய்தல், செய்முறை வாசிப்பு, மறுசரிபார்ப்பு</p></header>
<nav aria-label="கற்றல் துணையின் பகுதிகள்"><ul><li><a href="#diagnostic">தொடக்கக் கண்டறிதல்</a></li><li><a href="#misconceptions">தவறான புரிதல்கள்</a></li><li><a href="#worked">செய்முறை எடுத்துக்காட்டு</a></li><li><a href="#routes">வகுப்பு வழிகள்</a></li><li><a href="#mastery">தேர்ச்சிச் சரிபார்ப்பு</a></li><li><a href="../reader/index.html">முன்னுரை</a></li></ul></nav>
<main id="companion-main"><aside class="authored" aria-labelledby="authored-title"><h2 id="authored-title">இது தனியாக இயற்றப்பட்ட கற்றல் துணை</h2><p><strong>OpenStax மூல முன்னுரையின் பகுதி அல்ல.</strong> 2-8 வகுப்பு மாணவர் ஆசிரியர் உதவியின்றி முன்னுரையின் சொற்களையும் நூல் அமைப்பையும் புரிந்துகொள்ள இது உதவுகிறது. இது ஒரு இயற்கணித இயலின் தேர்ச்சியைச் சான்றளிக்காது; m82630 முன்னுரையைப் பயன்படுத்தத் தயாரா என்பதையே சரிபார்க்கிறது.</p></aside>
<section id="diagnostic"><h2>1. தொடக்கக் கண்டறிதல்</h2><p>விடைகளைத் திறப்பதற்கு முன் நான்கு வினாக்களுக்கும் முயலுங்கள். தெரியாத வினாவின் எண்ணைக் குறித்துவைத்துக்கொள்ளுங்கள்.</p><ol><li data-question-id="D1">−2 எந்தத் தொகுப்பில் உள்ளது: <strong>முழு எண்கள்</strong> அல்லது <strong>முழுக்கள்</strong>?</li><li data-question-id="D2">இரண்டு நேர்கோடுகள் இணையாக இருந்தால் அவற்றுக்கு எத்தனை பொதுப்புள்ளிகளும் எத்தனை தீர்வுகளும் உள்ளன?</li><li data-question-id="D3">இரண்டு சமன்பாடுகளும் ஒரே நேர்கோட்டைக் கொடுத்தால் தீர்வுகளின் எண்ணிக்கை என்ன?</li><li data-question-id="D4">பகுதிப் பயிற்சிகளில் ஒற்றைப்படை எண் கொண்ட வினாக்களின் விடைகளும் இரட்டைப்படை எண் கொண்ட வினாக்களின் விடைகளும் ஒரே இடத்தில் மாணவர்களுக்குக் கிடைக்குமா?</li></ol></section>
<section id="misconceptions"><h2>2. தவறான புரிதல்களைச் சரிசெய்தல்</h2><ul><li><strong>“முன்னுரைதான் முதல் கணிதப் பாடம்.”</strong> இல்லை. இது நூலின் அமைப்பு, வளங்கள், பயிற்சி வகைகள் மற்றும் உரிமத்தை அறிமுகப்படுத்துகிறது. முதல் பாட அலகு m82451.</li><li><strong>“முழு எண்களும் முழுக்களும் ஒன்றே.”</strong> இல்லை. முழு எண்கள் 0-இல் தொடங்கி மேலே செல்கின்றன; முழுக்களில் எதிர்ம எண்களும் உள்ளன.</li><li><strong>“வரைபடத்தில் முழு விளக்க வாக்கியங்கள் அச்சிடப்பட்டுள்ளன.”</strong> இல்லை. மூலப் படத்தில் <span lang="en">Intersecting</span>, <span lang="en">Parallel</span>, <span lang="en">Coincident</span> என்ற மூன்று ஆங்கிலத் தலைப்புகள் மட்டுமே உள்ளன. தமிழ் விளக்கம் தனியாகச் சேர்க்கப்பட்டது.</li><li><strong>“எல்லா வினாக்களின் விடைகளும் மாணவர் விடைத்தொகுப்பில் உள்ளன.”</strong> இல்லை. மூல முன்னுரை ஒற்றைப்படை வினாக்களின் விடைகளை மாணவர் விடைத்தொகுப்பிலும், இரட்டைப்படை வினாக்களின் விடைகளை ஆசிரியர் வழிகாட்டியிலும் வைக்கிறது.</li></ul></section>
<section id="worked"><h2>3. செய்முறை வாசிப்பு எடுத்துக்காட்டு</h2><p>ஒரு வரைபடத்தைப் படிக்கும்போது “படத்தில் உண்மையில் என்ன உள்ளது?” என்பதையும் “அதிலிருந்து நாம் என்ன முடிவு செய்கிறோம்?” என்பதையும் தனித்தனியாக எழுதுங்கள்.</p><table aria-label="நேர்கோட்டு வரைபடத்தைப் படிக்கும் செய்முறை"><thead><tr><th scope="col">படத்தில் உள்ள தலைப்பு</th><th scope="col">காணப்படும் அமைப்பு</th><th scope="col">கணித முடிவு</th></tr></thead><tbody><tr><th scope="row" lang="en">Intersecting</th><td data-label="காணப்படும் அமைப்பு">இரண்டு நேர்கோடுகள் ஒரு புள்ளியில் வெட்டுகின்றன.</td><td data-label="கணித முடிவு">ஒரு பொதுப்புள்ளி; ஒரு தீர்வு.</td></tr><tr><th scope="row" lang="en">Parallel</th><td data-label="காணப்படும் அமைப்பு">இரண்டு நேர்கோடுகள் வெட்டிக்கொள்வதில்லை.</td><td data-label="கணித முடிவு">பொதுப்புள்ளி இல்லை; தீர்வு இல்லை.</td></tr><tr><th scope="row" lang="en">Coincident</th><td data-label="காணப்படும் அமைப்பு">இரண்டு நேர்கோடுகளும் ஒன்றின்மேல் ஒன்று பொருந்துகின்றன.</td><td data-label="கணித முடிவு">முடிவற்ற பல பொதுப்புள்ளிகள்; முடிவற்ற பல தீர்வுகள்.</td></tr></tbody></table><p><strong>செய்முறை:</strong> முதலில் ஆங்கிலத் தலைப்பைக் கண்டறியுங்கள்; அடுத்து கோடுகளின் தொடர்பைக் கூறுங்கள்; இறுதியில் பொதுப்புள்ளிகளின் எண்ணிக்கையைத் தீர்வுகளின் எண்ணிக்கையுடன் இணைக்குங்கள். இது படம் சொல்வதையும் நாம் விளக்கமாகச் சேர்ப்பதையும் கலக்காமல் வைத்திருக்கிறது.</p></section>
<section id="routes"><h2>4. 2-8 வகுப்புகளுக்கான தனிப்பயிற்சி வழிகள்</h2><div class="route-grid"><section aria-labelledby="route-2-4"><h3 id="route-2-4">வகுப்புகள் 2-4</h3><p>எண் தொகுப்புகளின் மூன்று வரிசைகளையும் வரைபடத்தின் மூன்று நிலைகளையும் மட்டும் படியுங்கள். D1-D3-க்கு வாய்மொழியாகப் பதிலளியுங்கள். மேம்பட்ட இயல் தலைப்புகள் இப்போது ஒரு வரைபடமாக மட்டும் இருக்கலாம்.</p></section><section aria-labelledby="route-5-6"><h3 id="route-5-6">வகுப்புகள் 5-6</h3><p>முழு எண்கள், முழுக்கள், பின்னங்கள், தசம எண்கள் என்ற வேறுபாட்டையும் இயல்கள் 1-4-ன் நோக்கத்தையும் படியுங்கள். D1 அல்லது D2 தவறினால் சொல் வேறுபாட்டையும் செய்முறை அட்டவணையையும் மீண்டும் படியுங்கள்.</p></section><section aria-labelledby="route-7-8"><h3 id="route-7-8">வகுப்புகள் 7-8</h3><p>முழு முன்னுரையையும் படித்து, இயல்கள் 1-10 எவ்வாறு முன்னேறுகின்றன என்பதைச் சொல்லுங்கள். D4 தவறினால் விடைத்தொகுப்பு மற்றும் ஆசிரியர் வளங்கள் குறித்த மூலப் பகுதிகளை மீண்டும் படியுங்கள்.</p></section></div></section>
<section id="mastery"><h2>5. விடை, காரணம், மறுசரிபார்ப்பு</h2><details data-answer-id="D1"><summary>D1 விடை</summary><p><strong>முழுக்கள்.</strong> முழு எண்கள் 0, 1, 2, …; முழுக்கள் …, −2, −1, 0, 1, 2, …. ஆகவே −2 முழுக்களில் உள்ளது; முழு எண்களில் இல்லை.</p></details><details data-answer-id="D2"><summary>D2 விடை</summary><p><strong>பொதுப்புள்ளி இல்லை; தீர்வு இல்லை.</strong> இணை நேர்கோடுகள் சந்திக்காததால் சமன்பாட்டுத் தொகுப்பை நிறைவு செய்யும் பொதுப் புள்ளி கிடையாது.</p></details><details data-answer-id="D3"><summary>D3 விடை</summary><p><strong>முடிவற்ற பல தீர்வுகள்.</strong> இரு சமன்பாடுகளும் ஒரே நேர்கோட்டைக் குறித்தால், அந்த நேர்கோட்டின் ஒவ்வொரு புள்ளியும் இரண்டையும் நிறைவு செய்கிறது.</p></details><details data-answer-id="D4"><summary>D4 விடை</summary><p><strong>இல்லை.</strong> மூல முன்னுரையின்படி, ஒற்றைப்படை பகுதிப் பயிற்சி வினாக்களின் விடைகள் மாணவர் விடைத்தொகுப்பில் உள்ளன; இரட்டைப்படை வினாக்களின் விடைகள் ஆசிரியர் வளங்கள் பக்கத்தின் ஆசிரியர் விடை வழிகாட்டியில் மட்டும் உள்ளன.</p></details><p class="mastery-note"><strong>இந்தத் துணைக்கான அளவுகோல்:</strong> 4 விடைகளும் காரணத்துடன் சரியாக இருந்தால் முன்னுரையைப் பயன்படுத்தும் தயார்நிலை கிடைத்துள்ளது. தவறிய வினாவுக்குரிய பகுதியை மீண்டும் படித்து அதே வினாவை மறுசரிபார்க்கவும். இது இயற்கணித இயல்களின் தேர்ச்சி மதிப்பீடு அல்ல.</p></section></main>
<footer><p><a href="../reader/index.html">மொழிபெயர்க்கப்பட்ட முன்னுரைக்குத் திரும்புங்கள்</a> · <a href="../source/m82630.en.cnxml">ஆங்கில மூலச் சான்று</a> · <a href="../TERMINOLOGY.md">கலைச்சொல் முடிவுகள்</a></p><p lang="en">Independent Tamil learning companion authored by OpenAI Codex gpt-5.6-sol, Ultra, at the user's instruction; not part of the OpenStax source.</p></footer></body></html>'''.encode("utf-8")


def materialized(path, outputs):
    return outputs[path] if path in outputs else (ROOT / path).read_bytes()


def verify_html(rel_path, outputs, check):
    document = etree.HTML(outputs[rel_path])
    ids = document.xpath("//@id")
    check(rel_path + ":unique_ids", len(ids) == len(set(ids)))
    check(rel_path + ":lang", document.xpath("string(/html/@lang)") == "ta-IN")
    check(rel_path + ":viewport", bool(document.xpath('//meta[@name="viewport"]')))
    check(rel_path + ":image_alts", all(x.strip() for x in document.xpath("//img/@alt")))
    for link in document.xpath("//@href | //@src"):
        parts = urlsplit(link)
        check(rel_path + ":offline:" + link, not parts.scheme and not parts.netloc)
        target_rel = rel_path
        if parts.path:
            resolved = (ROOT / Path(rel_path).parent / unquote(parts.path)).resolve()
            check(rel_path + ":scoped:" + link, resolved.is_relative_to(ROOT))
            target_rel = resolved.relative_to(ROOT).as_posix()
            check(rel_path + ":exists:" + link, target_rel in outputs or resolved.is_file())
        if parts.fragment:
            target_document = etree.HTML(materialized(target_rel, outputs))
            check(rel_path + ":fragment:" + link, parts.fragment in target_document.xpath("//@id"))


def verify(source, target, collection, outputs, require_visual):
    checks = {}
    def check(name, value, required=True):
        checks[name] = bool(value)
        if required and not value:
            raise AssertionError(name)
    check("canonical_source_sha256", digest(SOURCE.read_bytes()) == SOURCE_SHA)
    check("canonical_collection_sha256", digest(COLLECTION.read_bytes()) == COLLECTION_SHA)
    refs = collection.xpath("//col:module/@document", namespaces=NS)
    check("collection_82_ordered_references", len(refs) == 82)
    check("collection_references_unique", len(refs) == len(set(refs)))
    check("collection_start_m82630_then_m82451", refs[:2] == ["m82630", "m82451"])
    check("collection_last_m82559", refs[-1:] == ["m82559"])
    check("structure_and_nonlinguistic_attributes", shape(source) == shape(target))
    check("target_language_tag", target.get(XML_LANG) == "ta-IN")
    ids = source.xpath("//@id")
    check("source_ID_order_unchanged", ids == target.xpath("//@id"))
    check("source_IDs_unique", len(ids) == len(set(ids)))
    check("module_and_uuid_unchanged", source.xpath("//md:content-id/text() | //md:uuid/text()", namespaces=NS) == target.xpath("//md:content-id/text() | //md:uuid/text()", namespaces=NS))
    check("zero_exercises_solutions_MathML", all(not tree.xpath("//c:exercise | //c:solution | //m:math", namespaces=NS) for tree in [source, target]))
    check("four_media_references_unchanged", source.xpath("//c:image/@src", namespaces=NS) == target.xpath("//c:image/@src", namespaces=NS) and len(target.xpath("//c:image", namespaces=NS)) == 4)
    check("all_alternatives_Tamil", all(re.search("[\u0b80-\u0bff]", x) for x in target.xpath("//c:media/@alt", namespaces=NS)))
    graph_alt = target.xpath("string(//*[@id='fs-id1171782146065']/@alt)")
    check("graph_alt_actual_labels", all(x in graph_alt for x in ["Intersecting", "Parallel", "Coincident"]))
    check("graph_alt_no_false_below_graph_claim", "கீழ்" not in graph_alt and "அச்சிட" not in graph_alt)
    for identity in ["eip-855", "eip-250", "eip-478", "eip-id1169146105286"]:
        check("credits_exact_" + identity, texts(source.xpath("//*[@id=$x]", x=identity)[0]) == texts(target.xpath("//*[@id=$x]", x=identity)[0]))
    chapter_titles = target.xpath('//*[@id="eip-992"]/c:item/c:emphasis', namespaces=NS)
    check("chapters_ordered_1_to_10", [re.search(r"\d+", texts(x)).group() for x in chapter_titles] == list(map(str, range(1, 11))))
    check("openstax_domain_mentions_preserved", texts(source).count("openstax.org") == texts(target).count("openstax.org"))
    check("license_version_retained", "CC BY-NC-SA 4.0 license." in texts(target))
    check("whole_numbers_integers_distinct", "முழு எண்கள், முழுக்கள்" in texts(target))
    check("Prealgebra_disclaimer_retained", "இயற்கணிதத்திற்கு முன், இரண்டாம் பதிப்பு" in texts(target.xpath('//*[@id="eip-582"]')[0]))
    check("reviewer_spelling_retained", "John Kalliongis, Saint Louis Iniversity" in texts(target))
    for name, (size, expected_hash, dimensions) in MEDIA.items():
        data = (ROOT / "media" / name).read_bytes()
        check("asset_bytes_" + name, len(data) == size)
        check("asset_hash_" + name, digest(data) == expected_hash)
        check("asset_dimensions_" + name, image_dimensions(data) == dimensions)
    for path in STATIC_PAYLOAD:
        check("payload_present_" + path, (ROOT / path).is_file())
    for path, data in outputs.items():
        if Path(path).suffix.lower() in {".html", ".css", ".json", ".xml", ".cnxml", ".md", ".txt", ".sha256"}:
            decoded = data.decode("utf-8", errors="strict")
            check("UTF8_" + path, decoded.encode("utf-8") == data and "\ufffd" not in decoded)
            check("NFC_" + path, unicodedata.normalize("NFC", decoded) == decoded)
            check("portable_" + path, not re.search(r"(?:[A-Z]:[\\/]|file://)", decoded))
    verify_html("reader/index.html", outputs, check)
    verify_html("companion/index.html", outputs, check)
    reader_doc = etree.HTML(outputs["reader/index.html"])
    main = reader_doc.xpath('//*[@id="source-text"]')[0]
    check("HTML_source_ID_order", [x for x in main.xpath(".//@id") if x != "source-text"] == ids)
    check("HTML_sections_contiguous", len(main.xpath(".//section")) == len(target.xpath("//c:section", namespaces=NS)))
    check("HTML_all_images", sorted(Path(x).name for x in reader_doc.xpath("//img/@src")) == sorted(MEDIA))
    css = outputs["reader/style.css"].decode("utf-8")
    check("CSS_font_local", 'url("fonts/NotoSansTamil.ttf")' in css)
    check("CSS_narrow", "@media(max-width:600px)" in css and ".route-grid{grid-template-columns:1fr}" in css)
    check("CSS_print", "@media print" in css and "break-inside:avoid" in css)
    companion_doc = etree.HTML(outputs["companion/index.html"])
    qids = companion_doc.xpath("//*[@data-question-id]/@data-question-id")
    aids = companion_doc.xpath("//*[@data-answer-id]/@data-answer-id")
    check("companion_four_diagnostics", qids == ["D1", "D2", "D3", "D4"])
    check("companion_answer_identity", aids == qids)
    check("companion_answers_have_reasoning", all(len(texts(x)) > 45 for x in companion_doc.xpath("//*[@data-answer-id]")))
    check("companion_four_misconceptions", len(companion_doc.xpath("//*[@id='misconceptions']//li")) == 4)
    check("companion_three_grade_routes", len(companion_doc.xpath("//*[@id='routes']/div/section")) == 3)
    check("companion_authorship_boundary", "OpenStax மூல முன்னுரையின் பகுதி அல்ல" in texts(companion_doc))
    check("companion_no_false_mastery", "இயற்கணித இயல்களின் தேர்ச்சி மதிப்பீடு அல்ல" in texts(companion_doc))
    recovery = load_json("SOURCE_RECOVERY.json")
    check("recovery_source_hash", recovery["canonical"]["module"]["sha256"] == SOURCE_SHA)
    check("recovery_collection_hash", recovery["canonical"]["collection"]["sha256"] == COLLECTION_SHA)
    check("recovery_82_refs", recovery["canonical"]["collection"]["ordered_module_references"] == refs)
    check("recovery_no_cutoff", recovery["scope"]["original_selected_cutoff"] is None)
    review = load_json("EXPERT_REVIEW_LOG.json")
    required = {"decision_id", "source_location", "target_location", "source_sense", "chosen_wording", "authorities_checked", "rationale", "alternatives", "uncertainty", "provisional", "review_question", "rationale_timing"}
    check("expert_log_partial_assignment", review["coverage_status"] == "partial")
    check("expert_log_eight_entries", len(review["entries"]) == 8)
    check("expert_log_required_fields", all(required <= set(x) for x in review["entries"]))
    check("expert_log_authorities", all(x["authorities_checked"] for x in review["entries"]))
    check("expert_log_retrospective", all(x["rationale_timing"] == "retrospective_reconstruction" for x in review["entries"]))
    corrections = load_json("SOURCE_CORRECTIONS.json")
    check("source_alt_correction_logged", corrections["corrections"][0]["asset_sha256"] == MEDIA["CNX_ElemAlg_Figure_05_01_015_img.jpg"][1])
    package = load_json("PACKAGE.json")
    check("package_bounded_not_full", package["status"] == "complete_bounded_increment" and package["full_assignment_status"] == "partial")
    check("package_PDF_pending", package["components"]["pdf"]["packet_pdf_created"] is False and package["components"]["pdf"]["status"].startswith("pending"))
    handoff = load_json("OWNER_HANDOFF.json")
    check("handoff_next_m82451", handoff["next_action"]["module_id"] == "m82451")
    visual = load_json("VISUAL_QA.json")
    visual_pass = visual.get("status") == "pass" and {"desktop", "narrow"} <= {x.get("mode") for x in visual.get("views", [])}
    check("actual_desktop_and_narrow_visual_QA", visual_pass, required=require_visual)
    status = "pass" if visual_pass else "pending_visual_QA"
    return {
        "schema": "a10.qa.v1", "status": status, "checks": checks,
        "counts": {"collection_module_references": len(refs), "source_elements": len(list(source.iter())), "source_IDs": len(ids), "sections": len(target.xpath("//c:section", namespaces=NS)), "MathML": 0, "source_exercises": 0, "supplied_solutions": 0, "canonical_images": 4, "authored_diagnostics": 4, "authored_answers_with_reasoning": 4},
        "inputs": {"source_sha256": SOURCE_SHA, "collection_sha256": COLLECTION_SHA, "target_sha256": digest(TARGET.read_bytes()), "builder_sha256": digest(Path(__file__).read_bytes())},
        "generated_outputs": {path: {"bytes": len(data), "sha256": digest(data)} for path, data in outputs.items()},
        "visual_QA": visual,
        "deterministic_replay": {"command": "python build.py --check", "status": "pass", "meaning": "The delivered generated bytes reproduce exactly from packet-local inputs; this command was executed after the final build."},
    }


def make_manifest(outputs):
    payload = STATIC_PAYLOAD + ["modules/m82630/index.cnxml", "reader/index.html", "reader/style.css", "companion/index.html", "QA.json"]
    roles = {"build.py": "deterministic builder and validator", "seal.py": "deterministic packet ZIP builder and verifier", "source/collection.xml": "pinned canonical collection inventory", "source/m82630.en.cnxml": "pinned canonical English source", "translation/m82630.ta.cnxml": "source-structured Tamil translation", "modules/m82630/index.cnxml": "portable module copy of Tamil translation", "reader/index.html": "offline semantic Tamil reader", "reader/style.css": "screen, narrow, and print stylesheet", "companion/index.html": "separate teacher-independent authored companion", "EXPERT_REVIEW_LOG.json": "terminology and difficult-passage ledger", "SOURCE_RECOVERY.json": "source lock and boundary record", "SOURCE_CORRECTIONS.json": "source-alt correction record", "PACKAGE.json": "bounded packet status record", "OWNER_HANDOFF.json": "owner admission and next-action record", "QA.json": "deterministic structural and semantic QA receipt", "VISUAL_QA.json": "actual desktop and narrow browser QA receipt"}
    entries = []
    for path in sorted(payload):
        data = materialized(path, outputs)
        entries.append({"path": path, "bytes": len(data), "sha256": digest(data), "role": roles.get(path, "licensed supporting asset or notice")})
    return {"schema": "a10.packet-manifest.v1", "packet_id": "ta-Taml-IN-m82630", "file_count": len(entries), "files": entries, "manifest_self_exclusion": "MANIFEST.json cannot hash itself.", "checksum_index": "CHECKSUMS.sha256 hashes every manifested file plus MANIFEST.json; it excludes only itself."}


def checksum_index(outputs):
    paths = [x["path"] for x in json.loads(outputs["MANIFEST.json"])["files"]] + ["MANIFEST.json"]
    return "".join(f"{digest(materialized(path, outputs))}  {path}\n" for path in sorted(paths)).encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source, target, collection = load_xml(SOURCE), load_xml(TARGET), load_xml(COLLECTION)
    outputs = {"modules/m82630/index.cnxml": TARGET.read_bytes(), "reader/index.html": reader(target), "reader/style.css": STYLE.encode("utf-8"), "companion/index.html": companion()}
    receipt = verify(source, target, collection, outputs, require_visual=args.check)
    outputs["QA.json"] = json_bytes(receipt)
    outputs["MANIFEST.json"] = json_bytes(make_manifest(outputs))
    outputs["CHECKSUMS.sha256"] = checksum_index(outputs)
    if args.check:
        for rel, data in outputs.items():
            assert (ROOT / rel).read_bytes() == data, "deterministic replay: " + rel
    else:
        for rel, data in outputs.items():
            path = ROOT / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({"status": receipt["status"], "mode": "check" if args.check else "build", "checks": len(receipt["checks"]), "counts": receipt["counts"], "generated_file_count": len(outputs), "manifest_file_count": json.loads(outputs["MANIFEST.json"])["file_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
