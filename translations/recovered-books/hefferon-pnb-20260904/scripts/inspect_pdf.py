from pathlib import Path
import hashlib
import json
import re
import unicodedata
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[1]
pdf=BASE/"output/pdf/hefferon-shahmukhi-opening.pdf"
reader=PdfReader(pdf)
pages=[p.extract_text() or "" for p in reader.pages]
normalized=[unicodedata.normalize("NFKC",p) for p in pages]
text="\n".join(pages)
assert "\x00" not in text and "\ufffd" not in text
assert not reader.is_encrypted
assert reader.trailer["/Root"].get("/Lang")=="pnb-Arab-PK"
assert reader.trailer["/Root"].get("/MarkInfo").get_object()["/Marked"]
assert reader.trailer["/Root"].get("/StructTreeRoot")
def id_pairs(node):
    node=node.get_object()
    result=[]
    names=node.get('/Names',[])
    for i in range(0,len(names),2):
        result.append((str(names[i]),names[i+1].get_object()))
    for child in node.get('/Kids',[]):
        result.extend(id_pairs(child))
    return result
tag_ids=id_pairs(reader.trailer['/Root']['/StructTreeRoot']['/IDTree'])
assert tag_ids and [k for k,v in tag_ids]==sorted({k for k,v in tag_ids})
assert all(str(v['/ID'])==k for k,v in tag_ids)
assert reader.outline
uris={str(a.get_object().get('/A',{}).get('/URI','')) for p in reader.pages for a in p.get('/Annots',[])}
assert not any('127.0.0.1' in u or 'localhost' in u or u.startswith('file:') for u in uris)
for p in reader.pages:
    assert abs(float(p.mediabox.width)-595.28)<2 and abs(float(p.mediabox.height)-841.89)<2
for p in pages:
    assert len(p.strip())>100, "Near-blank spillover page"
assert "خطی الجبرا" in "\n".join(normalized)
answers={str(i):[n+1 for n,p in enumerate(normalized) if re.search(r"جواب\s*"+str(i)+r"\b|\b"+str(i)+r"\s*جواب",p)] for i in range(1,9)}
assert all(answers.values()), answers
browser=json.loads((BASE/"qa/browser.json").read_text())
digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
assert digest==browser["pdf"]["sha256"]
def outline_count(items):
    return sum(outline_count(x) if isinstance(x,list) else 1 for x in items)
report={"status":"PASS","pdf":{"path":str(pdf.relative_to(BASE)).replace('\\','/'),"sha256":digest,"bytes":pdf.stat().st_size,"pages":len(reader.pages)},
        "html_sha256":browser["html_sha256"],"page_size":"A4; every page within 2 pt","tagged":True,"tagged_idtree_sorted_closed":len(tag_ids),"document_language":"pnb-Arab-PK","outline_entries":outline_count(reader.outline),
        "null_characters":0,"replacement_characters":0,"near_blank_pages":0,"answer_label_pages":answers,"pdf_external_links":sorted(uris-{''}),"temporary_local_links":0,
        "text_extraction":"Arabic presentation forms normalize with NFKC; mixed RTL/LTR reading order can vary by consumer. No full PDF/UA certification.",
        "page_text_lengths":[len(p) for p in pages],"font_remedy":"Windows Arial print profile; lineated source quotes use upright text in print to avoid italic fallback glyph loss. Semantic HTML remains Nastaliq. No source words changed.",
        "visual_review":"Separate final bound visual receipt required."}
(BASE/"qa/pdf-inspection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":"PASS","pages":len(reader.pages),"null_characters":0,"replacement_characters":0,"outline_entries":report["outline_entries"]}))
