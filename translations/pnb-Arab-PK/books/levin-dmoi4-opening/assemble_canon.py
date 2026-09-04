"""Build an explicitly qualified native-language terminology reading page."""
import hashlib
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def build():
    d=json.loads((ROOT/'canon/terminology.json').read_text(encoding='utf-8'));e=html.escape
    parts=['<!doctype html><html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>لفظ، ماخذ تے زبان دا پُل</title><link rel="stylesheet" href="../site.css"></head><body><main>',
      '<nav><a href="../index.html">مُڈھلا صفحہ</a><a href="../support/practice.html">نویاں مشقاں</a></nav><header><h1>لفظ، ماخذ تے زبان دا پُل</h1>',
      '<p>شاہ مکھی پنجابی دی اپنی لکھت توں مدد لئی گئی اے۔ اردو تے انگریزی جوڑ وکھرے نیں؛ اوہناں نوں پنجابی ماخذ دا ثبوت نہیں بنایا گیا۔</p></header>',
      '<aside class="note"><p>منطق، دلیل، قضیہ تے سِٹّا کڈھن دے لفظ پنجابی فلسفیانہ ماخذاں وچ ملدے نیں۔ پر ایہہ پورے ڈسکریٹ ریاضی دے لفظاں دی پکی فہرست نہیں۔ ہِیٹھاں تعریفاں سکھن لئی اسیں لکھیاں نیں؛ اوہ ماخذ دے ہُوبہُو قول نہیں۔ بغیر خاص ماخذ والے لفظ ایتھے صاف طور اُتے عارضی اداری انتخاب نیں۔</p><p>اصل ترجمے دی عبارت نہیں بدلی گئی۔ ایہہ وکھرا رجسٹر اوہنوں سمجھّن لئی اے، کسے ادارے دی منظوری دا دعویٰ نہیں۔</p></aside>',
      '<section><h2>سبق دے لفظ</h2>']
    for i,t in enumerate(d['terms'],1):
        evidence='، '.join(t['evidence'])
        status='لفظی استعمال دا محدود ماخذ موجود؛ ہِیٹھلی تعریف اداری اے۔' if evidence else 'عارضی اداری انتخاب؛ ایس رسمی مطلب لئی خاص مقامی ماخذ قائم نہیں کیتا گیا۔'
        parts.extend([f'<article class="exercise" id="term-{i}"><h3>{e(t["term"])}</h3><p class="en" lang="en" dir="ltr">{e(t["concept"])}</p><p>{e(t["definition"])}</p><p><small>{status}</small></p>'])
        if evidence:parts.append(f'<p><small>ماخذ دے مقام: <bdi dir="ltr">{e(evidence)}</bdi></small></p>')
        if t.get('urdu_bridge'):parts.append(f'<p><small>صرف اردو پُل: <span lang="ur-Arab-PK">{e(t["urdu_bridge"])}</span></small></p>')
        parts.append('</article>')
    parts.extend(['</section><section id="sources"><h2>اصل ماخذ تے جانچ دی حد</h2>',
      '<p><bdi dir="ltr">S1</bdi>: اقبال دے خطبات دا شریف کنجاہی دا پنجابی روپ، مجلس ترقی ادب، لاہور۔ صفحہ <bdi dir="ltr">181</bdi> اُتے منطقی قضیاں تے دلیل دی مثال اے؛ صفحہ <bdi dir="ltr">44</bdi> سِٹّا کڈھن تے صفحہ <bdi dir="ltr">60</bdi> دلیل دی لفظی گواہی دیندا اے۔ ایہہ فلسفے دی کتاب اے، جدید سیٹ تھیوری دا لفظنامہ نہیں۔</p>',
      '<p><bdi dir="ltr">S2</bdi>: منظور اعجاز، فلسفے دی تاریخ، کتاب ترنجن، <bdi dir="ltr">2020</bdi>۔ کتاب والے صفحے اُتے دکھائی گئی مُڈھلی عبارت پڑھی گئی؛ پوری کتاب پڑھن دا دعویٰ نہیں۔</p>',
      '<p><bdi dir="ltr">S3</bdi>: احمد شہزاد دا پنجابی لسانیات بارے مضمون۔ علمی وضاحت تے سِٹّا کڈھن دی زبان لئی مدد اے؛ تجربے دی تصدیق نوں ریاضی دے ثبوت دے برابر نہیں رکھیا گیا۔</p>'])
    for s in d['sources']:
        parts.append(f'<p><bdi dir="ltr">{e(s["id"])}</bdi>: <a href="{e(s["url"],quote=True)}"><span lang="en">{e(s["author"])} — {e(s["title"])}</span></a></p>')
        for loc in s.get('locators',[]):parts.append(f'<a href="{e(loc["url"],quote=True)}">صفحہ <bdi dir="ltr">{loc["printed_page"]}</bdi> دا اصل عکس</a> · ')
    parts.extend(['</section><footer><p>دائرہ، بیان دی سچائی، تے دلیل دی درستی وکھ وکھ گلاں نیں۔ انگریزی جوڑ شناخت وچ مدد لئی رکھے گئے نیں؛ اصل ریاضی دی تعریف کتاب دے متعلقہ حصے توں لو۔</p><p><a href="terminology.json">ماخذ دے پتے، مقام، ہیش تے مشینی رجسٹر</a> · <a href="../LICENSE.md">انتساب تے لائسنس</a></p></footer></main></body></html>'])
    b=('\n'.join(parts)+'\n').encode('utf-8');(ROOT/'canon/terminology.html').write_bytes(b)
    return {'path':'canon/terminology.html','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
if __name__=='__main__':
    a=build();assert a==build();print(json.dumps({'result':'pass','replay':'byte_identical','output':a}))
