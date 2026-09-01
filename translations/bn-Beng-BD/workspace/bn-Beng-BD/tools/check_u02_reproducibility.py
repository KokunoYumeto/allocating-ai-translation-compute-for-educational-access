"""Check two fresh small builds against current reviewed bytes, without downloads."""
import hashlib, json, subprocess, sys
from build import L, write

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    names=['output/U02/index.html','output/m81243/index.html',
           'translations/complete_modules/m81243/index.cnxml',
           'assets/NumeracyBanglaMath.ttf','output/pdf/u02-complete-print.pdf',
           'output/pdf/u02-complete-screen.pdf','output/u01-number-sense.html',
           'assets/NumeracyBangla.ttf','output/pdf/u01-print.pdf','output/pdf/u01-screen.pdf']
    for suffix in 'ABCDE':
        names.extend([f'output/U02{suffix}/index.html',f'translations/modules/m81243/u02{suffix.lower()}.cnxml'])
    baseline={name:sha(L/name) for name in names}
    visual=json.loads((L/'output/pdf/u02-visual-qa.json').read_text(encoding='utf-8'))
    for artifact in visual['artifacts']:assert baseline[artifact['file']]==artifact['sha256']
    scripts=['build_math_font.py','build_u02_edition.py']
    for cycle in range(2):
        for script in scripts:
            result=subprocess.run([sys.executable,'-B',str(L/'tools'/script)],cwd=L.parent,capture_output=True,text=True,encoding='utf-8')
            assert result.returncode==0,result.stdout+'\n'+result.stderr
        current={name:sha(L/name) for name in names}
        assert current==baseline,{'cycle':cycle+1,'changed':[n for n in names if current[n]!=baseline[n]]}
        print(f'Fresh small-build cycle {cycle+1}: all {len(names)} reviewed/source/U01 files byte-identical.',flush=True)
    receipt={'status':'pass','fresh_build_cycles':2,'sha256':baseline,
             'tools_sha256':{p.name:sha(p) for p in sorted((L/'tools').glob('*.py'))},
             'limits':'Deterministic bytes and structural/math checks; separate exact-hash visual receipt and human-review limitations apply.'}
    write(L/'output/U02/reproducibility.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
