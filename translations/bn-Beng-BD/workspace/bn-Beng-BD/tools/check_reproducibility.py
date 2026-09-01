"""Replay small local builds twice; never fetch or extract source corpora."""
from pathlib import Path
import hashlib, json, subprocess, sys
L = Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(script):
    result = subprocess.run([sys.executable, '-B', str(L/'tools'/script)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding='utf-8')
    if result.returncode: raise RuntimeError(script+'\n'+result.stdout)

def main():
    lock_before = digest(L/'sources.lock.json')
    run('prepare.py')
    assert digest(L/'sources.lock.json') == lock_before, 'Source freeze changed locked evidence'
    paths = ['translations/modules/m81243/index.cnxml', 'output/u01-number-sense.html',
             'output/build-receipt.json', 'assets/NumeracyBangla.ttf', 'assets/font-receipt.json',
             'output/pdf/u01-print.pdf', 'output/pdf/u01-screen.pdf']
    def build():
        for script in ('qa.py', 'build_font.py', 'build_pdf.py', 'qa_pdf.py'): run(script)
        return {path: digest(L/path) for path in paths}
    first = build()
    assert build() == first, 'Nondeterministic small build'
    receipt = {'status': 'pass', 'complete_small_build_cycles': 2,
               'preparation_preserves_verified_source_lock': True,
               'html_cnxml_font_and_pdfs_byte_identical': True, 'sha256': first}
    (L/'output/reproducibility.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__': main()
