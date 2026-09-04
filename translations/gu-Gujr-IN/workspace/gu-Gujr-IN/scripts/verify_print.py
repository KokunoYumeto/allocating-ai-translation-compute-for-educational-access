"""Verify final PDFs without confusing searchable text with PDF/UA tagging."""
import hashlib
import json
from pathlib import Path
import subprocess

from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

LANG = Path(__file__).resolve().parents[1]
supported = set(TTFont('GujaratiQA', str(LANG/'assets/NotoSansGujarati.ttf')).face.charToGlyph)
records = []
for audience, expected_pages in [('student', 10), ('teacher', 8)]:
    path = LANG/f'output/pdf/unit01-{audience}-print.pdf'
    reader = PdfReader(path)
    text = subprocess.run(['pdftotext', '-enc', 'UTF-8', str(path), '-'],
                          check=True, capture_output=True).stdout.decode('utf-8')
    assert len(reader.pages) == expected_pages
    assert sum('\u0a80' <= c <= '\u0aff' for c in text) > 100
    assert '\u0ab8\u0acd\u0aa5\u0abe\u0aa8\u0a95\u0abf\u0a82\u0aae\u0aa4' in text
    assert not any('\ue000' <= c <= '\uf8ff' or c == '\ufffd' for c in text)
    missing = sorted({ord(c) for c in text if not c.isspace() and ord(c) not in supported})
    assert not missing, ['U+%04X' % c for c in missing]
    actual_text_pages = sum(b'/ActualText' in p.get_contents().get_data() for p in reader.pages)
    assert actual_text_pages == expected_pages
    if audience == 'teacher':
        assert all('('+letter+')' in text for letter in 'abcde')
    records.append({'file': path.relative_to(LANG).as_posix(), 'pages': len(reader.pages),
                    'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'logical_actualtext_pages': actual_text_pages,
                    'poppler_gujarati_extraction': 'pass', 'missing_font_codepoints': [],
                    'private_use_or_replacement_characters': 0,
                    'has_structure_tree': bool(reader.trailer['/Root'].get('/StructTreeRoot'))})
receipt = {'schema': 'gujarati-pilot-print-qa-v1', 'result': 'pass', 'date': '2026-08-30',
           'files': records, 'pdf_ua_claimed': False,
           'limitations': ['Print PDFs are untagged. HTML is the primary semantic format.',
                           'Poppler respects ActualText; extraction behavior can differ in other readers.',
                           'Native educator and assistive-technology review remain pending.'],
           'visual_review': 'See REVIEW.md; automated text checks alone do not prove layout quality.'}
(LANG/'PRINT_QA.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
