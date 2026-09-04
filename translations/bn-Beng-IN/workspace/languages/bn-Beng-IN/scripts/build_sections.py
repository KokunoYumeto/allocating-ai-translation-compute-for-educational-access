"""Build explicitly registered complete source blocks; do not infer completion from files."""
from pathlib import Path

import os  # portable-export-transform-v1

def _portable_input_path(variable, default):
    """Resolve optional configured inputs without touching disk during import."""
    value = os.environ.get(variable)
    result = Path(value).expanduser() if value else default
    return result if result.is_absolute() else ROOT / result

def _require_portable_input(value, variable):
    if not value.exists():
        raise FileNotFoundError(
            f"Required pinned input is absent: {value}. Set {variable} to its "
            "existing location or restore the exact source-lock inputs under "
            "workspace downloads. This helper does not acquire sources."
        )
    return value

import hashlib,html,json,shutil,subprocess,sys,xml.etree.ElementTree as ET
import build
from qa import Page

L=build.LANG
ROOT=L.parents[1]
SHARED=_portable_input_path('BN_CANONICAL_ROOT', ROOT / 'downloads' / 'osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9')
PIN='38cae454e644abf9f0a623e876994553881597c9'
EXTRA_CSS='table{width:100%;border-collapse:collapse;table-layout:fixed}td{padding:8px;vertical-align:top;overflow-wrap:anywhere;border-bottom:1px solid #d5e0dc}td .media{margin:6px 0}td img{max-height:140px}td math{font-size:1em}ol.circled{list-style:none}.math-scroll{display:inline-block;max-width:100%;overflow-x:auto;vertical-align:middle;padding:4px 0}.math-scroll:focus{outline:2px solid #14685e}.math-scroll math{white-space:nowrap}'

def reader_page(title,body):
    result=build.page(title,body).replace('href="U01-', 'href="../U01-')
    if 'id="fs-id1951781"' in body:
        # This source table embeds a tall mtable between prose slots. Block flow
        # separates the warning from the calculation without changing MathML.
        result=result.replace('</style>','#fs-id1951781 td > math:has(mtable){display:block;margin:0.5em 0}</style>')
    narrow_math_tables=(
        'eip-id1168469608226',
        'eip-id1168469489639',
        'eip-id1168469481183',
    )
    if any(f'id="{table_id}"' in body for table_id in narrow_math_tables):
        # These source operation tables use two fixed-width columns. Their
        # short final numeric expressions exceed a 390 px viewport at the
        # ordinary table font size; reduce only those table expressions on
        # narrow screens without changing source MathML.
        selectors=','.join(f'#{table_id} td math' for table_id in narrow_math_tables)
        result=result.replace('</style>',f'@media(max-width:480px){{{selectors}{{font-size:.82em}}}}</style>')
    longdiv='menclose[notation~="longdiv"]{display:inline-block;border-top:1.5px solid currentColor;border-left:1.5px solid currentColor;border-top-left-radius:0.35em;padding:0.05em 0.25em 0.05em 0.2em;margin-left:0.12em}'
    boundaries='.exercise{border:1px solid #aec4bb;padding:10px 12px;margin:18px 0}.exercise-label,.solution-label{font-size:0.8em;color:#43535a;margin:0 0 8px}.solution-label{font-weight:bold}.exercise .solution{margin-top:14px}'
    strikes='menclose[notation~="updiagonalstrike"]{display:inline-block;background:linear-gradient(135deg,transparent calc(50% - 0.65px),currentColor calc(50% - 0.65px),currentColor calc(50% + 0.65px),transparent calc(50% + 0.65px))}'
    return result.replace('</style>',EXTRA_CSS+longdiv+strikes+boundaries+'</style>').replace('<nav aria-label="পাঠ নির্বাচন">','<nav aria-label="পাঠ নির্বাচন"><a href="../index.html">পাঠসূচি</a> · ')

def freeze_module(module):
    lock=json.loads((L/'sources.lock.json').read_text(encoding='utf-8'))
    entries=[m for c in lock['collections'] for m in c['source_modules'] if m['module']==module]
    assert entries and len({m['sha256'] for m in entries})==1,module
    entry=entries[0]
    try:dest=build.module_source(module)
    except FileNotFoundError:
        source=ROOT/entry['path']
        assert build.sha(source)==entry['sha256'] and source.stat().st_size==entry['bytes']
        dest=L/'provenance/modules'/f'{module}.source.cnxml'
        assert shutil.disk_usage(ROOT).free>100_000_000
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
    assert build.sha(dest)==entry['sha256']
    return dest

def freeze_media(source):
    paths=[]
    lock_path=L/'provenance/media.lock.json'
    media_lock=json.loads(lock_path.read_text(encoding='utf-8')) if lock_path.is_file() else {'repository':'openstax/osbooks-prealgebra-bundle','commit':PIN,'assets':{}}
    assert media_lock['commit']==PIN
    for e in source.iter(f'{{{build.C}}}image'):
        name=Path(e.get('src')).name
        dest=L/'provenance/pilot/media'/name
        if name in media_lock['assets']:
            entry=media_lock['assets'][name]
            assert dest.is_file() and build.sha(dest)==entry['sha256'] and dest.stat().st_size==entry['bytes'],name
            raw=dest.read_bytes()
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['git_blob']
            paths.append(entry)
            continue
        original=_require_portable_input(SHARED/'media'/name, 'BN_CANONICAL_ROOT')
        # Pinned shared bytes only; no network or bulk corpus duplication.
        expected=subprocess.check_output(['git','-C',str(_require_portable_input(_portable_input_path('BN_CANONICAL_GIT_ROOT', ROOT/'downloads/osbooks-prealgebra-bundle'), 'BN_CANONICAL_GIT_ROOT')),'rev-parse',f'{PIN}:media/{name}']).decode().strip()
        raw=original.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==expected
        if not dest.is_file():
            assert len(raw)<20_000_000 and shutil.disk_usage(ROOT).free>100_000_000
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest)
        assert build.sha(dest)==hashlib.sha256(raw).hexdigest()
        entry={'path':dest.relative_to(L).as_posix(),'bytes':len(raw),'sha256':build.sha(dest),'git_blob':expected}
        paths.append(entry)
        media_lock['assets'][name]=entry
    media_lock['assets']=dict(sorted(media_lock['assets'].items()))
    lock_path.write_text(json.dumps(media_lock,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return paths

def build_one(name):
    path=L/'translations'/name
    overlay=json.loads(path.read_text(encoding='utf-8'))
    freeze_module(overlay['module'])
    source,target=build.translated(path)
    assets=freeze_media(source)
    stem=f'{overlay["module"]}-{overlay["section"]}'
    out=L/'reader/sections';out.mkdir(parents=True,exist_ok=True)
    title=target.findtext(f'{{{build.C}}}title') or overlay.get('display_title',stem)
    header=f'<h1>{html.escape(title)}</h1><p class="notice">উৎস-অনুগত উপবিভাগ · {stem}। সম্পূর্ণ বইয়ের অনুবাদ এখনও চলছে। গাণিতিক চিহ্ন, সংখ্যা ও মূল কাঠামো অক্ষুণ্ণ; প্রযোজ্য ক্ষেত্রে সূত্রের শব্দলেবেল বাংলায় অনূদিত। মূল ছবির ভিতরের ইংরেজি লেবেলের অর্থ বাংলা বিবরণে আছে। স্বাধীন শিক্ষক ও ভাষা-পর্যালোচনা বাকি। অন্য উপবিভাগের উৎস-লিঙ্কে ইন্টারনেট প্রয়োজন।</p>'
    footer='<footer>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0</a>। অনানুষ্ঠানিক অনুবাদ; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</footer>'
    body=header+build.render_cnxml(target,overlay['module'],'../../provenance/pilot/media/',study_labels=True)+footer
    result=reader_page(title,body)
    reader=out/(stem+'.html')
    reader.write_text(result,encoding='utf-8')
    document=ET.Element(f'{{{build.C}}}document',{'{http://www.w3.org/XML/1998/namespace}lang':'bn-Beng-IN','id':stem+'.bn-Beng-IN'})
    ET.SubElement(document,f'{{{build.C}}}title').text=title
    ET.SubElement(document,f'{{{build.C}}}content').append(target)
    (L/'translations'/(stem+'.bn-Beng-IN.cnxml')).write_bytes(ET.tostring(document,encoding='utf-8',xml_declaration=True))
    page=Page();page.feed(result)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids
        elif not href.startswith('https:'):assert (reader.parent/href).is_file(),href
    assert all(i.get('alt') and (reader.parent/i['src']).is_file() for i in page.images)
    receipt={'module':overlay['module'],'section':overlay['section'],'result':'pass','translation_sha256':build.sha(path),
             'builders':{f'scripts/{n}':build.sha(L/'scripts'/n) for n in ['build.py','build_sections.py']},
             'source_sha256':build.sha(build.module_source(overlay['module'])),'reader':reader.relative_to(L).as_posix(),'reader_sha256':build.sha(reader),
             'nodes':sum(1 for e in source.iter()),'ids':sum(bool(e.get('id')) for e in source.iter()),
             'mathml':len(build.math_signature(source)),'localized_linguistic_mtext':len(overlay.get('math_text',{})),
             'mathematical_integrity':'exact after reversing only explicitly checked linguistic mtext substitutions',
             'examples':sum(build.local(e)=='example' for e in source.iter()),'exercises':sum(build.local(e)=='exercise' for e in source.iter()),
             'assets':assets,'source_errata':overlay.get('source_errata',[]),'independent_human_review':'pending','visual_review':'pending'}
    (L/'qa/sections').mkdir(parents=True,exist_ok=True)
    (L/'qa/sections'/(stem+'.json')).write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return receipt

if __name__=='__main__':
    names=sys.argv[1:]
    assert names,'Pass explicit completed overlay filenames; partial drafts are not auto-admitted.'
    for name in names:
        r=build_one(name)
        print(json.dumps({k:r[k] for k in ['module','section','result','nodes','ids','mathml','localized_linguistic_mtext','examples','exercises']},ensure_ascii=False))
