"""Deterministic HTML for separately authored supplementary exercises."""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build():
    data = json.loads((ROOT / 'support/practice.json').read_text(encoding='utf-8'))
    assert data['origin'] == 'newly_authored_support_not_Levin_source'
    assert len(data['items']) == len({x['id'] for x in data['items']}) == 6
    out = ['<!doctype html><html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1"><title>نویاں مشقاں تے وکھرے حل</title><link rel="stylesheet" href="../site.css"></head><body><main>',
           '<nav><a href="../index.html">مُڈھلے صفحے ول مُڑو</a><a href="../canon/terminology.html">لفظ تے ماخذ</a></nav>',
           '<header><p class="eyebrow">وادھو رہنمائی · اصل کتاب دا حصہ نہیں</p><h1>چھے نویاں مشقاں تے اوہناں دے حل</h1>',
           '<p>پہلاں خود سوچو، فیر حل کھولو۔ ایہہ سوال تے حل ایس پیکج لئی وکھرے لکھے گئے نیں؛ اوہ آسکر لیون دے اصل سوال یا اوہناں دی جواب کُنجی نہیں۔ نال دِتّا حوالہ صرف متعلقہ سبق ول اے۔</p></header>']
    for i, item in enumerate(data['items'], 1):
        esc = html.escape
        out.extend([f'<article class="exercise" id="{esc(item["id"])}" data-origin="newly-authored-support">',
                    f'<h2><bdi dir="ltr">{i}.</bdi> {esc(item["topic"])}</h2>',
                    f'<p>{esc(item["question"])}</p>',
                    f'<div class="math" dir="ltr">{esc(item["given"])}</div>',
                    f'<p><a href="{esc(item["source_topic"])}">متعلقہ سبق دوبارہ پڑھو</a></p>',
                    '<details><summary>ساڈا وکھرا لکھیا حل ویکھو</summary>',
                    f'<p>{esc(item["answer"])}</p><div class="math" dir="ltr">{esc(item["calculation"])}</div></details></article>'])
    out.extend(['<footer><p>ایہہ چھوٹی جانچ سکھن وچ مدد لئی اے؛ پوری کتاب یا کسے باقاعدہ امتحان دی تیاری دا ثبوت نہیں۔</p>',
                '<p><bdi lang="en" dir="ltr">OpenAI Codex gpt-5.6-sol, Ultra</bdi>، ورتن والے دی ہدایت اُتے۔ <a href="../LICENSE.md">لائسنس</a></p></footer></main></body></html>'])
    payload = ('\n'.join(out) + '\n').encode('utf-8')
    (ROOT / 'support/practice.html').write_bytes(payload)
    return {'path': 'support/practice.html', 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}

if __name__ == '__main__':
    first = build()
    assert build() == first
    print(json.dumps({'result': 'pass', 'replay': 'byte_identical', 'output': first}))
