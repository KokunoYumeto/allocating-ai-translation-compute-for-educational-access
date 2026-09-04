"""Small, readable target-language reference shelf; not a dictionary dump."""
import concurrent.futures
import hashlib
import json
import re
import urllib.request
from html.parser import HTMLParser
from config import DOWNLOADS, LANG
from safe_io import write_bytes, write_text

WORDS = ['wilangan', 'cacah', 'siji', 'loro', 'telu', 'papat', 'lima', 'enem', 'kiwa', 'tengen', 'luwih', 'gedhe', 'cilik', 'owah', 'tetep', 'saka', 'rolas', 'likur', 'atus', 'enggon', 'ping', 'para', 'gunggung']
LARGE_NUMBER_EXTENSION = ['ewu', 'yuta', 'wolu', 'sanga', 'sewidak']
GROUPING_EXTENSION = ['kurung', 'tutup']
ROUNDING_POWER_EXTENSION = ['bunder', 'bulet', 'cedhak', 'rambang']
ADDITION_EXTENSION = ['tambah', 'simpen']
SUBTRACTION_EXTENSION = ['kurang', 'suda', 'silih']
AREA_EXTENSION = ['jembar', 'dawa', 'amba']
EVALUATION_EXTENSION = ['ganti']
REMAINDER_EXTENSION = ['sisa', 'turah']
LIKE_TERMS_EXTENSION = ['suku', 'jenis']
ALGEBRA_LANGUAGE_EXTENSION = ['basa', 'tembung']
SELF_CHECK_EXTENSION = ['tulung']
WORDS += LARGE_NUMBER_EXTENSION + GROUPING_EXTENSION + ROUNDING_POWER_EXTENSION + ADDITION_EXTENSION + SUBTRACTION_EXTENSION + AREA_EXTENSION + EVALUATION_EXTENSION + REMAINDER_EXTENSION + LIKE_TERMS_EXTENSION + ALGEBRA_LANGUAGE_EXTENSION + SELF_CHECK_EXTENSION


class Readable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag in ('p', 'div', 'br', 'li', 'h1', 'h2', 'h3'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
        if tag in ('p', 'div', 'li'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def acquire(word):
    url = 'https://kbji.kemendikdasmen.go.id/kata/' + word
    dest = DOWNLOADS / 'canon'
    dest.mkdir(parents=True, exist_ok=True)
    raw_path = dest / (word + '.html')
    if not raw_path.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'LanguageAllocation-translation-reference/1.0'})
        with urllib.request.urlopen(req, timeout=35) as response:
            raw = response.read()
    else:
        raw = raw_path.read_bytes()
    parser = Readable()
    parser.feed(raw.decode('utf-8'))
    text = '\n'.join(re.sub(r'\s+', ' ', line).strip() for line in ''.join(parser.parts).splitlines() if line.strip())
    # Restrict the local reading view to the dictionary result, not navigation.
    assert 'Padanan & Definisi Indonesia' in text, f'No dictionary results in response: {word}'
    text = text.split('Padanan & Definisi Indonesia', 1)[-1].split('Apakah terjemahan sudah benar', 1)[0].strip()
    assert word in text.lower() and len(text) > 8, f'No readable entry: {word}'
    readable_path = dest / (word + '.txt')
    if not raw_path.exists():
        write_bytes(raw_path, raw)
    if not readable_path.exists():
        write_text(readable_path, text + '\n')
    else:
        assert readable_path.read_text(encoding='utf-8') == text + '\n', f'Cached readable entry differs: {word}'
    return {'id': f'C{WORDS.index(word)+1:02}', 'headword': word, 'url': url, 'authority': 'Balai Bahasa Provinsi Daerah Istimewa Yogyakarta, KBJI', 'acquired_date': '2026-08-31' if word in LARGE_NUMBER_EXTENSION + GROUPING_EXTENSION + ROUNDING_POWER_EXTENSION + ADDITION_EXTENSION + SUBTRACTION_EXTENSION + AREA_EXTENSION + EVALUATION_EXTENSION + REMAINDER_EXTENSION + LIKE_TERMS_EXTENSION + ALGEBRA_LANGUAGE_EXTENSION + SELF_CHECK_EXTENSION else '2026-08-30', 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'readable_sha256': hashlib.sha256(readable_path.read_bytes()).hexdigest(), 'raw_path': raw_path.relative_to(DOWNLOADS.parent.parent).as_posix(), 'readable_path': readable_path.relative_to(DOWNLOADS.parent.parent).as_posix(), 'format': 'native HTML, converted to readable UTF-8 text; no OCR needed', 'license_scope': 'Consultation copy in ignored downloads; copyright retained; only brief quotations and original decision notes are committed.'}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(acquire, WORDS))
    target = LANG / 'canon' / 'sources.lock.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    write_text(target, json.dumps({'purpose': 'Target-language reference consultation, not training', 'records': records}, ensure_ascii=False, indent=2) + '\n')
    print(f'Acquired {len(records)} readable official Javanese reference entries.')


if __name__ == '__main__':
    main()
