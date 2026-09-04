"""Deterministic offline CNXML translation and semantic HTML builder for m82630."""
import copy
import hashlib
import html
import json
from pathlib import Path
from lxml import etree as E

ROOT = Path(__file__).resolve().parent
CN = "http://cnx.rice.edu/cnxml"
NS = {"c": CN}
EXPECTED_STATIC = {
    "source/m82630.en.cnxml": (22483, "d9f45fb31f4cb399c009c2be25eca1a99132b4b6882fb07f8649c2d56974f90b"),
    "source/collection.xml": (5256, "5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72"),
    "media/tryit.png": (344, "7f9c8c226d8b937d4070c69326d6c2ac7df37a74c85fa8cec64e2ad7bef59ebf"),
    "media/howtoicon.png": (1681, "67f2344cdbe25b192fbdee0d904ce912e4e15aed5bf0063f61a192dd0b0b5826"),
    "media/media.png": (353, "140b45d7d047dc59b236c95bb2c2a237ca5b748b290b28f8e6d9f8f520077e6a"),
    "media/CNX_ElemAlg_Figure_05_01_015_img.jpg": (688493, "34fd0299880bc134f6308adcb2296ec1e145431909a1ab1cc2b507e01e3670f4"),
    "LICENSE.txt": (21442, "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_static_inputs():
    for name, (expected_bytes, expected_sha256) in EXPECTED_STATIC.items():
        data = (ROOT / name).read_bytes()
        assert len(data) == expected_bytes, f"Static input byte mismatch: {name}"
        assert sha(data) == expected_sha256, f"Static input hash mismatch: {name}"


def slots(tree):
    result = []
    for el in tree.iter():
        for field in ("text", "tail"):
            value = getattr(el, field)
            if value and value.strip():
                result.append((el, field, value))
    return result


def inner(el, depth):
    return html.escape(el.text or "") + "".join(render(ch, depth) + html.escape(ch.tail or "") for ch in el)


def render(el, depth=1):
    tag = E.QName(el).localname
    ident = ' id="' + html.escape(el.get("id"), quote=True) + '"' if el.get("id") else ""
    if tag == "section":
        return "<section" + ident + ">" + inner(el, depth + 1) + "</section>"
    if tag == "title":
        return f"<h{depth}>" + inner(el, depth) + f"</h{depth}>"
    if tag == "para":
        lang = ' lang="en"' if el.get("id") in {"eip-855", "eip-250", "eip-478", "eip-id1169146105286"} else ""
        return "<p" + ident + lang + ">" + inner(el, depth) + "</p>"
    if tag == "emphasis":
        out = "strong" if el.get("effect") == "bold" else "em"
        lang = ' lang="en"' if (el.text or "").strip() == "Strategies for Success: Study Skills for the College Math Student" else ""
        return f"<{out}{lang}>" + inner(el, depth) + f"</{out}>"
    if tag == "newline":
        return "<br>"
    if tag == "list":
        return "<ul" + ident + ">" + inner(el, depth) + "</ul>"
    if tag == "item":
        return "<li" + ident + ">" + inner(el, depth) + "</li>"
    if tag == "media":
        image = el.find("c:image", NS)
        name = Path(image.get("src")).name
        alt = html.escape(el.get("alt", ""), quote=True)
        image_html = f'<img src="media/{name}" alt="{alt}" loading="lazy">'
        if el.get("id") == "fs-id1171782146065":
            return '<figure' + ident + '>' + image_html + '<figcaption><p>বাঁ থেকে ডানে: <strong>ছেদকারী</strong> (Intersecting), <strong>সমান্তরাল</strong> (Parallel), <strong>সমাপতিত</strong> (Coincident) সরলরেখা। মূল চিত্রের ইংরেজি নামগুলি অক্ষুণ্ণ রাখা হয়েছে।</p><p>' + html.escape(el.get("alt")) + '</p></figcaption></figure>'
        return '<span class="icon"' + ident + '>' + image_html + '</span>'
    if tag == "content":
        return inner(el, depth)
    raise ValueError("Unmapped CNXML element: " + tag)


def build_bytes():
    source = (ROOT / "source/m82630.en.cnxml").read_bytes()
    mapping = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
    assert sha(source) == mapping["source_sha256"]
    tree = E.ElementTree(E.fromstring(source))
    translated = copy.deepcopy(tree)
    ss, ts = slots(tree), slots(translated)
    assert len(ss) == len(ts) == 146
    work, preserve = mapping["translations"], mapping["preserve_slots"]
    assert set(work).isdisjoint(preserve)
    assert set(work) | set(preserve) == {str(i) for i in range(len(ss))}
    ledger = []
    for i, ((se, field, value), (te, _, _)) in enumerate(zip(ss, ts)):
        key = str(i)
        new = work.get(key, value)
        setattr(te, field, new)
        ledger.append({"slot": i, "source_xpath": tree.getpath(se), "field": field, "source_sha256": sha(value.encode()), "translation_sha256": sha(new.encode()), "status": "translated" if key in work else "preserved_identity_or_credit", "reason": preserve.get(key)})
    media = translated.xpath("//c:media", namespaces=NS)
    source_media = {x.get("id"): x for x in tree.xpath("//c:media", namespaces=NS)}
    assert {x.get("id") for x in media} == set(mapping["alt"])
    alt_ledger = []
    for el in media:
        ident = el.get("id")
        source_alt = source_media[ident].get("alt")
        target_alt = mapping["alt"][ident]
        el.set("alt", target_alt)
        alt_ledger.append({
            "media_id": ident,
            "source_xpath": tree.getpath(source_media[ident]),
            "source_sha256": sha(source_alt.encode()),
            "translation_sha256": sha(target_alt.encode()),
            "status": "translated_and_asset_checked",
        })
    src_nodes, out_nodes = list(tree.iter()), list(translated.iter())
    assert len(src_nodes) == len(out_nodes)
    for a, b in zip(src_nodes, out_nodes):
        assert a.tag == b.tag
        assert {k: v for k, v in a.attrib.items() if k != "alt"} == {k: v for k, v in b.attrib.items() if k != "alt"}
    content = translated.find("c:content", NS)
    toc = "".join('<li><a href="#' + sec.get("id") + '">' + html.escape("".join(sec.find("c:title", NS).itertext())) + '</a></li>' for sec in content.findall("c:section", NS))
    page = '''<!doctype html>
<html lang="bn-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>মুখবন্ধ · প্রাথমিক বীজগণিত · ভারতীয় বাংলা</title><link rel="stylesheet" href="reader.css"></head><body>
<a class="skip" href="#main">মূল পাঠে যাও</a>
<header><p class="eyebrow">OpenStax · Elementary Algebra 2e · bn-Beng-IN</p><h1>প্রাথমিক বীজগণিত<br><span>দ্বিতীয় সংস্করণ · মুখবন্ধ</span></h1><p>ভারতীয় বাংলা | মূল বইয়ের সম্পূর্ণ মুখবন্ধ | m82630</p></header>
<main id="main"><aside class="edition"><h2>এই বাংলা পাঠ সম্পর্কে</h2><p>এটি মূল বইয়ের মুখবন্ধের অনুবাদ। গোটা ৮২-এককের বই এবং পৃথক তৃতীয়–অষ্টম শ্রেণির শেখার ঘাটতি পূরণের সহায়িকা এখনও সম্পূর্ণ নয়। এই মুখবন্ধে মূল বইয়ের বৈশিষ্ট্য, অন্য অধ্যায়ের উত্তরসূচি, PDF ও অনলাইন উপকরণের বর্ণনা রয়েছে; এই ছোটো প্যাকেটে সেই সব উপকরণ আছে বলে দাবি করা হচ্ছে না।</p><p>OpenStax-এর লেখক ও পর্যালোচকদের স্বীকৃতি নীচে অক্ষুণ্ণ রয়েছে। বাংলা অনুবাদ ও ডিজিটাল বিন্যাস: OpenAI Codex gpt-5.6-sol, Ultra। এই অনুবাদের সরকারি অনুমোদন বা শ্রেণিকক্ষে কার্যকারিতার প্রমাণ দাবি করা হচ্ছে না।</p></aside>
<nav aria-label="মুখবন্ধের অংশ"><h2>এই মুখবন্ধে</h2><ul>''' + toc + '''</ul></nav>
<article aria-label="মূল উৎসের অনুবাদ">''' + render(content) + '''</article>
<aside class="edition" id="editorial-notes"><h2>সম্পাদনা ও ব্যবহার-সংক্রান্ত নোট</h2><p>উপরের ‘মিডিয়া’ ঘোষণায় মূল উৎসেই <em>Prealgebra 2e</em> লেখা আছে। তাই অনুবাদে ‘প্রাক্-বীজগণিত ২য় সংস্করণ’ রাখা হয়েছে; নীরবে বইয়ের নাম বদলানো হয়নি। পর্যালোচকের প্রতিষ্ঠানের নামে মূল উৎসের <span lang="en">Saint Louis Iniversity</span> বানানটিও স্বীকৃতির যথার্থ প্রতিলিপি হিসেবে রাখা হয়েছে।</p><p>সমান্তরাল রেখার চিত্রটির মূল বিকল্প বর্ণনায় দীর্ঘ বাক্যগুলি চিত্রের নীচে লেখা আছে বলা হয়েছিল। বাস্তব ছবিতে শুধু তিনটি ইংরেজি শিরোনাম আছে। বাংলা বর্ণনায় ছবিতে যা আছে এবং তার গাণিতিক অর্থ আলাদা করে লেখা হয়েছে। কোনও রেখা বা বিন্দুর অবস্থান বদলানো হয়নি।</p><p>পড়ার এই HTML ও চারটি চিত্র ইন্টারনেট ছাড়াই কাজ করে। মূল বই ও লাইসেন্সের বাইরের লিঙ্কগুলি খুলতে ইন্টারনেট দরকার।</p><p>পরের উৎস-একক: m82451, ‘ভূমিকা’। সেই অনুবাদ এই প্যাকেটে নেই।</p></aside>
<footer><p><a href="source/m82630.en.cnxml">অপরিবর্তিত ইংরেজি উৎস</a> · <a href="modules/m82630/index.cnxml">বাংলা CNXML</a> · <a href="LICENSE.txt">CC BY-NC-SA 4.0 লাইসেন্স</a> · <a href="PACKAGE.json">প্যাকেটের পরিচয়</a> · <a href="EXPERT_REVIEW_LOG.json">পরিভাষা-পর্যালোচনার লগ</a> · <a href="QA_REPORT.json">গুণমান যাচাই</a></p><p>মূল উৎস: <a href="https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/m82630/index.cnxml">OpenStax, নির্দিষ্ট সংরক্ষিত সংস্করণ</a>। Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.</p><p>মূল লেখার অনুবাদ একই CC BY-NC-SA 4.0 লাইসেন্সে। চিত্রের আলাদা স্বীকৃতি ও বিধিনিষেধ থাকলে তা বহাল থাকে।</p></footer></main></body></html>
'''
    return {
        "modules/m82630/index.cnxml": E.tostring(translated, encoding="utf-8", xml_declaration=True),
        "index.html": page.encode("utf-8"),
        "TEXT_LEDGER.json": (json.dumps({
            "schema": "a10.text-ledger.v1",
            "locale": "bn-Beng-IN",
            "module": "m82630",
            "source_sha256": sha(source),
            "slot_count": len(ledger),
            "translated_slot_count": len(work),
            "preserved_slot_count": len(preserve),
            "slots": ledger,
            "alt": alt_ledger,
        }, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    }


def main():
    verify_static_inputs()
    outputs = build_bytes()
    assert outputs == build_bytes(), "Non-deterministic build"
    for name, data in outputs.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({name: {"bytes": len(data), "sha256": sha(data)} for name, data in outputs.items()}, indent=2))


if __name__ == "__main__":
    main()
