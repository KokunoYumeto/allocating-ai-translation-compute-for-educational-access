"""Assemble the independently reviewed PNB-013 translation parts."""
from pathlib import Path
import argparse
import json
import re
import xml.etree.ElementTree as ET

from qa_notation import unique_object


BASE = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r'\{\{(?:math|term|link|child|break):\d+\}\}')
NUMBER = re.compile(r'(?<![\w])(?:−|-)?\d+(?:[.,]\d+)*(?![\w])')


def load(relative):
    return json.loads((BASE / relative).read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def assemble(check_only=False):
    manifest = load('source-excerpts/manifest-013.json')
    shell = load('translations/unit-013-shell.json')
    part_a = load('translations/unit-013-part-a.json')
    part_b = load('translations/unit-013-part-b.json')
    assert list(part_a) == ['source_blocks'] and list(part_b) == ['source_blocks']
    combined = {**part_a['source_blocks'], **part_b['source_blocks']}
    keys = manifest['source_block_keys']
    assert list(part_a['source_blocks']) == keys[:157]
    assert list(part_b['source_blocks']) == keys[157:]
    assert list(combined) == keys and len(combined) == 353
    for key in keys:
        source, target = manifest['source_block_templates'][key], combined[key]
        assert PLACEHOLDER.findall(target) == PLACEHOLDER.findall(source), key
        source_numbers, target_numbers = NUMBER.findall(source), NUMBER.findall(target)
        assert target_numbers == source_numbers, (key, source_numbers, target_numbers)
        ET.fromstring('<fragment>' + target + '</fragment>')
        assert '__DRAFT_REQUIRED__' not in target
    header_cells = shell['table_header_cells']
    scopes = shell['table_header_scopes']
    assert list(scopes) == header_cells and set(scopes.values()) <= {'row', 'col'}
    entry_keys = [key for key in keys if '/row/' in key and '/entry/' in key]
    assert len(entry_keys) == 78 and set(header_cells) < set(entry_keys)
    result = dict(shell)
    result['translated_table_data_cells'] = [key for key in entry_keys if key not in header_cells]
    result['source_blocks'] = combined
    output = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    target = BASE / 'translations/unit-013.json'
    if check_only:
        assert target.exists() and target.read_bytes() == output
    else:
        if not target.exists() or target.read_bytes() != output:
            target.write_bytes(output)
    print(json.dumps({'unit': 'PNB-013', 'blocks': len(keys), 'headers': len(header_cells),
                      'data_cells': len(entry_keys) - len(header_cells), 'check_only': check_only}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    assemble(parser.parse_args().check_only)
