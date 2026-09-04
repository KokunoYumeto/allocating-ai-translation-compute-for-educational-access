"""Build the bounded source-faithful opening and separately authored bridge.

No network, Git, TeX, shell execution, global paths or current-time dependencies.
"""
from pathlib import Path
import copy
import hashlib
import html
import json
import re
from lxml import etree as E
from build_b40_opening import Reader, LOCAL_CSS
from recovery_io import BASE, MANIFEST, TRANSLATION, WITNESS, NOTICES, load, require, file_hash
from study_b40_toc import build_entries, legend_record

def write(rel, text):
    path = BASE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def jsonwrite(rel, obj):
    write(rel, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def plain_title(raw):
    if raw.startswith(r"\texorpdfstring"):
        return "General=Particular+Homogeneous"
    return raw.replace("Def{}inition", "Definition").replace(r"Chi\`o", "Chiò")

def contents(entries, t):
    esc = html.escape
    require([x["owner"] for x in entries] == list(t["titles"]), "Contents order/coverage differs")
    out = ['<section id="b40-contents" data-origin="faithful-translation-semantic-format"><h2>' + t["heading"] + '</h2>']
    out.append('<p class="source-label">ایہہ پوری اصل کتاب دے عنواناں دی فہرست اے؛ انہاں باباں دا متن ہن ایس پیکیج وچ شامل نہیں۔ اصل کتاب دے صفحہ نمبر ایتھے نہیں دتے، کیوں جے اوہ چھپائی نال بدل جاندے نیں۔ ترتیب، حصیاں دے نشان تے اختیاری ستارے اصل ماخذ والے نیں۔</p>')
    chapter_names = ["باب پہلا", "باب دوجا", "باب تریجا", "باب چوتھا", "باب پنجواں", "ضمیمہ"]
    opened = False
    chapter = 0
    for i, e in enumerate(entries, 1):
        title = t["titles"][e["owner"]]
        attr = ' data-toc-owner="' + esc(e["owner"], quote=True) + '" data-source-line="' + str(e["line"]) + '" data-optional="' + str(e["optional_star"]).lower() + '"'
        english = '<span class="toc-english" lang="en" dir="ltr">' + esc(plain_title(e["raw_title"])) + '</span>'
        if e["kind"] == "chapter":
            if opened:
                out.append('</ol></section>')
            label = chapter_names[chapter]
            chapter += 1
            out.append('<section class="toc-chapter"><h3 id="toc-' + str(i) + '"' + attr + '>' + label + (' — ' + title if chapter < 6 else '') + english + '</h3><ol>')
            opened = True
        else:
            label = e["generated_label"] or ""
            if label == "Topic:":
                labelhtml = '<span class="toc-label">موضوع</span>'
            else:
                labelhtml = '<bdi class="toc-label" dir="ltr">' + esc(label) + '</bdi>'
            optional = '<sup class="optional-star" aria-label="اختیاری">*</sup> ' if e["optional_star"] else ''
            depth = 2 if e["kind"] in {"subsection", "appendix-subsection"} else 1
            if e["raw_title"].startswith(r"\texorpdfstring"):
                chunks = ["عمومی حل", "خاص حل", "یکساں نظام دا حل"]
                titlehtml = '<math xmlns="http://www.w3.org/1998/Math/MathML" dir="ltr"><mrow><mtext dir="rtl">' + chunks[0] + '</mtext><mo>=</mo><mtext dir="rtl">' + chunks[1] + '</mtext><mo>+</mo><mtext dir="rtl">' + chunks[2] + '</mtext></mrow></math>'
            else:
                titlehtml = esc(title)
            out.append('<li id="toc-' + str(i) + '" data-depth="' + str(depth) + '"' + attr + '>' + labelhtml + optional + titlehtml + english + '</li>')
    out.append('</ol></section><p id="toc-legend" data-source-owner="' + t["legend_owner"] + '"><sup>*</sup> ' + t["legend"] + '</p></section>')
    return "\n".join(out)

def diagram():
    # Coordinates: x:[0,8] -> [60,580]; y:[0,7] -> [360,45].
    def pt(x, y):
        return 60 + 65*x, 360 - 45*y
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="620" height="420" viewBox="0 0 620 420" role="img" aria-labelledby="title desc"><title id="title">Two linear equations with intersection (4,3)</title><desc id="desc">x+y=7 descends; x-y=1 ascends. Their sole intersection is (4,3). Axes are labeled x and y.</desc><rect width="620" height="420" fill="#fffdf8"/>']
    for x in range(9):
        px, _ = pt(x, 0)
        parts.append(f'<path d="M{px},45 V360" stroke="#d7e0da"/><text x="{px}" y="385" text-anchor="middle" font-family="sans-serif" font-size="15">{x}</text>')
    for y in range(8):
        _, py = pt(0, y)
        parts.append(f'<path d="M60,{py} H580" stroke="#d7e0da"/><text x="43" y="{py+5}" text-anchor="end" font-family="sans-serif" font-size="15">{y}</text>')
    parts.append('<path d="M60,38 V360 H590" fill="none" stroke="#173434" stroke-width="2"/><text x="596" y="366" font-size="20">x</text><text x="51" y="25" font-size="20">y</text>')
    parts.append('<path d="M60,45 L515,360" stroke="#175b94" stroke-width="3" fill="none"/><path d="M125,360 L580,45" stroke="#925312" stroke-width="3" stroke-dasharray="10 6" fill="none"/>')
    parts.append('<circle cx="320" cy="225" r="6" fill="#173434"/><rect x="328" y="213" width="70" height="29" fill="#fffdf8"/><text x="334" y="233" font-family="sans-serif" font-size="18">(4,3)</text><text x="100" y="68" fill="#175b94" font-family="sans-serif" font-size="18">x+y=7</text><text x="445" y="67" fill="#925312" font-family="sans-serif" font-size="18">x-y=1</text></svg>')
    write("assets/bridge-system.svg", "".join(parts) + "\n")

def build():
    m, target, repo = load()
    study = json.loads((BASE / "source-excerpts/b40-toc-source-study.json").read_text(encoding="utf-8"))
    tc = json.loads((BASE / "translations/b40-contents-pnb.json").read_text(encoding="utf-8"))
    require(file_hash(BASE / "source-excerpts/b40-toc-source-study.json") == tc["source_study_sha256"], "Contents source binding differs")
    entries = build_entries(repo / "src")
    require(entries == study["canonical_entries"], "Current pinned contents reconstruction differs")
    require(legend_record(repo / "src") == study["legend"]["canonical"], "Contents legend differs")
    notice = json.loads(NOTICES.read_text(encoding="utf-8"))
    for c in notice["components"]:
        require(file_hash(BASE / c["prepared_path"]) == c["source_sha256"], "PDF component differs")
        require(file_hash(BASE / c["preview"]["path"]) == c["preview"]["sha256"], "Preview differs")
    displayed = copy.deepcopy(target)
    old_scope = next(x for x in displayed["original_notes"] if x["id"] == "b40-opening-scope")
    old_scope["html"] = '<p>سرورق، علامتاں، یونانی حرف، پوری مُڈھلی گل تے فہرست دے سارے عنوان ایتھے شامل نیں۔ اصل باباں، اوہناں دیاں مشقاں تے لیب دا ترجمہ ایس پیکیج وچ نہیں۔ تیاری دیاں چار مثالاں تے آٹھ حل سمیت مشقاں وکھریاں نویاں سکھلائی دیاں چیزاں نیں۔</p>'
    reader = Reader(m, displayed, notice)
    source = reader.cover() + reader.symlist() + reader.preface()
    require(len(reader.used) == 174 and set(reader.used) == set(m["expected_source_keys"]), "Opening source coverage differs")
    require(reader.math_seen == [(x["owner"], x["slot_token"]) for x in notice["math_records"]], "Math source order differs")
    bridge = (BASE / "learning/bridge.html").read_text(encoding="utf-8")
    require(not re.search(r"[\u0900-\u0dff\ufffd]", bridge), "Accidental other Indic script or replacement character")
    E.fromstring(bridge.encode())
    css = (BASE / "styles/reader.css").read_text(encoding="utf-8") + LOCAL_CSS + (BASE / "styles/recovered.css").read_text(encoding="utf-8")
    diagram()
    result = '''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="author" content="Jim Hefferon; Shahmukhi adaptation by Codex on instructions of the user"/>
<meta name="source-revision" content="df2262e089a02651c127f1dd12649c4622ee1383"/><meta name="edition-status" content="Bounded opening package; not complete book"/>
<title>خطی الجبرا — شاہ مکھی مُڈھلا پیکیج</title><style>''' + css + '''</style></head><body class="b40-opening">
<a class="skip-link" href="#reading-start">سِدھا متن ول جاؤ</a><header><p class="eyebrow"><bdi dir="ltr" lang="en">Hefferon · Shahmukhi Punjabi · Opening package · 2026-09-04</bdi></p>
<p class="status">محدود مُڈھلا پیکیج — پوری کتاب نہیں۔ ماخذ دا ترجمہ تے نویں سکھلائی مدد وکھرے نشان نال دتے نیں۔</p>
<nav aria-label="پیکیج دے حصے"><a href="#reading-start">پڑھنا شروع کرو</a> · <a href="#b40-contents">فہرست</a> · <a href="#learner-bridge">تیاری تے مشق</a> · <a href="#bridge-answers">جواب</a> · <a href="#credits">ماخذ تے لائسنس</a></nav></header>
<main id="reading-start"><div class="reader-intro"><p>پہلاں کتاب دی مُڈھلی گل تے علامتاں ویکھو۔ جے سکول دی الجبرا دُہران دی لوڑ اے، <a href="#learner-bridge">تیاری دے حصے</a> توں شروع کر سکدے او۔ انگریزی ناں تے اردو مدد وکھرے نشان نال نیں؛ بنیادی سمجھاؤن والی بولی پنجابی اے۔</p></div>
<article id="b40-opening-source" data-origin="faithful-source-translation">''' + source + '</article>' + contents(entries, tc) + reader.originals() + '''
<aside class="technical-status" id="terminology-status"><h2>اصطلاحاں بارے صاف گل</h2><p>پنجابی نثر دے محفوظ نمونے جملے بناؤن وچ مدد دیندے نیں؛ اوہ ساریاں ریاضی اصطلاحاں دا ثبوت نہیں۔ ایس محدود کھوج وچ پاکستان دی شاہ مکھی وچ خطی الجبرا دی مناسب فنی سند نہیں ملی۔ ایس لئی فنی ناں عارضی نیں تے نال صاف تعریف تے انگریزی مطلب دتا اے۔ اردو دے مددگار ناں وی پنجابی دی سند نہیں۔</p></aside>''' + bridge + reader.fallback() + '''</main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, license and exact coverage</h2>
<p>Jim Hefferon, <a href="https://gitlab.com/jim.hefferon/linear-algebra/-/blob/df2262e089a02651c127f1dd12649c4622ee1383/src/book.tex">Linear Algebra, fourth edition, second printing</a>, source date 2021-Oct-12. Native Shahmukhi Punjabi adaptation with separate Urdu/English help. The source author, institutional and personal acknowledgments remain the author's historical words; no endorsement is implied.</p>
<p>License: <a href="https://creativecommons.org/licenses/by-sa/2.5/">CC BY-SA 2.5</a>, the selected route from the source's GFDL / CC BY-SA 2.5 alternatives. See <a href="../LICENSE.md">LICENSE</a>, <a href="../provenance/upstream--hefferon-linear-algebra/LICENSE">original notice</a>, and <a href="../provenance/hefferon-linear-algebra-id/NOTICE.id-ID.md">retained Indonesian comparison credits</a>. Fonts retain the <a href="../assets/fonts/OFL.txt">SIL Open Font License 1.1</a>.</p>
<p>Coverage: 174 recovered cover/notation/full-preface slots, 97 newly translated semantic contents titles, and the optional-subsection legend. All 76 opening formulas retain exact source TeX and limited MathML conversion. Original PDF cover components and their disclosed PNG previews are preserved; their separate layout is not an exact TeX-cover facsimile. The source notation's degree-n wording has a separate degree-at-most-n clarification; no hidden source correction was made.</p>
<p>New support: four worked examples, eight exercises with worked answers, a labeled two-line diagram and nine Punjabi-definition/Urdu/English glossary rows. These are newly authored, not Hefferon's exercises. This is a secondary-to-undergraduate bridge, not a validated learner assessment. Source contents page numbers are deliberately not transplanted from an older PDF; all current headings, hierarchy and 14 optional markers are retained. The original chapter bodies, book exercise answers and laboratory are not translated here. Next source anchor: src/gr/gr1.tex, Chapter One, Linear Systems.</p>
<p>Technical language is provisional, with <a href="../provenance/terminology.md">bounded source evidence and limits</a>. The prose canon remains separately credited to Jamil Ahmad Pal, not promoted to mathematics authority. Semantic HTML is the primary accessible format; the companion PDF is tested in the recorded renderer, not certified PDF/UA or universally screen-reader compatible. Source-TeX disclosures are available in HTML and omitted from the print reader; all learning answers are expanded in PDF.</p>
<p>Prepared by OpenAI Codex gpt-5.6-sol, Ultra, on instructions of the user. Source, author and inherited contributor credits are preserved. No upstream messages were sent. <a href="../README.md">Package guide</a> · <a href="../backend/units.json">Machine-readable units</a> · <a href="../source-excerpts/b40-opening.json">Frozen opening source</a> · <a href="../qa/validation.json">Build/QA receipt</a>.</p></footer></body></html>
'''
    write("reader/opening.html", result)
    units = []
    for b in m["source_blocks"]:
        units.append({"unit_id": "hefferon:" + b["key"], "origin": "faithful-translation", "source_file": "source/canonical/" + b["source_file"], "source_start_codepoint": b["source_start"], "source_end_codepoint": b["source_end"], "source_sha256": b["source_raw_sha256"], "target_file": "translations/b40-opening.json", "target_key": b["key"], "target_sha256": hashlib.sha256(target["source_blocks"][b["key"]].encode()).hexdigest(), "locale": "pnb-Arab-PK"})
    for entry in entries:
        units.append({"unit_id": "hefferon:toc:" + entry["owner"], "origin": "faithful-title-translation-format-adapted", "source_file": "source/canonical/" + entry["file"], "source_line": entry["line"], "source_title": entry["raw_title"], "source_title_sha256": hashlib.sha256(entry["raw_title"].encode()).hexdigest(), "target_file": "translations/b40-contents-pnb.json", "target_key": entry["owner"], "kind": entry["kind"], "generated_label": entry["generated_label"], "optional_star": entry["optional_star"], "locale": "pnb-Arab-PK"})
    units.append({"unit_id": "hefferon:toc:optional-legend", "origin": "faithful-translation", "source_file": "source/canonical/src/book.tex", "source_line": 51, "source_text": study["legend"]["canonical"]["text"], "target_file": "translations/b40-contents-pnb.json", "target_key": "legend", "locale": "pnb-Arab-PK"})
    for i in range(1, 5):
        units.append({"unit_id": "hefferon:original:bridge-example-" + str(i), "origin": "original-worked-example", "target_file": "learning/bridge.html", "target_id": "bridge-example-" + str(i), "locale": "pnb-Arab-PK"})
    for i in range(1, 9):
        units.append({"unit_id": "hefferon:original:bridge-q" + str(i), "origin": "original-exercise", "target_file": "learning/bridge.html", "target_id": "bridge-q" + str(i), "solution_id": "bridge-a" + str(i), "locale": "pnb-Arab-PK"})
    jsonwrite("backend/units.json", {"schema": "hefferon-pnb-modular-units-v1", "source_commit": tc["source_commit"], "coverage": "opening only; contents do not imply translated chapters", "units": units})
    inputs = ["translations/b40-opening.json", "translations/b40-contents-pnb.json", "learning/bridge.html", "styles/reader.css", "styles/recovered.css", "scripts/build_package.py", "scripts/build_b40_opening.py", "scripts/b40_opening_tex.py", "scripts/study_b40_toc.py", "scripts/recovery_io.py", "provenance/b40-opening-component-notices.json", "source-excerpts/manifest-b40-opening.json", "source-excerpts/b40-toc-source-study.json"]
    outputs = ["reader/opening.html", "backend/units.json", "assets/bridge-system.svg"]
    jsonwrite("qa/build.json", {"status": "PASS", "source_slots": 174, "contents_titles": 97, "optional_markers": 14, "opening_math_owners": 76, "original_examples": 4, "original_exercises_with_answers": 8, "source_page_numbers": "not reproduced; semantic format", "next_source_anchor": "src/gr/gr1.tex:4", "input_files": [{"path": p, "bytes": (BASE / p).stat().st_size, "sha256": file_hash(BASE / p)} for p in inputs], "output_files": [{"path": p, "bytes": (BASE / p).stat().st_size, "sha256": file_hash(BASE / p)} for p in outputs]})
    print(json.dumps({"status": "PASS", "reader_sha256": file_hash(BASE / outputs[0]), "source_slots": 174, "contents": 97, "original_exercises": 8}))

if __name__ == "__main__":
    build()
