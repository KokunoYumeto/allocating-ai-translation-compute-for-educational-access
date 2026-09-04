"""Bind the recap's PNG-named source SVG to byte-identical reviewed chart assets.

The PNG original and earlier JPEG original are distinct source files. Reuse is
authorized only by the identical pinned Indonesian SVG blob, never by basename.
This prepares the recap asset, not outer metadata/glossary or narration.
"""
import argparse
import copy
import json
import xml.etree.ElementTree as ET

from build_units import tree_key
from config import LANG, UPSTREAM_COMMIT
from prepare_digit_place_assets import A00_COMMIT, git, pinned_blob, sha256
from safe_io import write_bytes

UNIT = 'a00-whole-summary'
NAME = 'CNX_BMath_Figure_01_01_011.png'
SOURCE_HASH = '139263ebfe895df0abcaf00fa63c949b38e5edc352239ed70ec42837625fee13'
SECTION_HASH = '098df4a46ab1146a26b9d36e79ccab231324d5437bcb1f837e56d8b83b77e5d0'


def products():
    module = pinned_blob('a00-id', A00_COMMIT, 'modules/m81243/index.cnxml',
                         '90def09ee1dbfdc66aa8bc910938ad7684668e97')
    section = next(n for n in ET.fromstring(module).iter() if n.get('id') == 'fs-id2296006')
    assert sha256(tree_key(section).encode()) == SECTION_HASH
    media = section.find('{*}figure/{*}media')
    assert media.get('id') == 'eip-id1170196618449'
    assert media.find('{*}image').get('src') == '../../media/' + NAME + '.id-ID.svg'
    source = pinned_blob('a00-id', A00_COMMIT, 'media/' + NAME + '.id-ID.svg',
                         'c7fd63689cb359befc7169687a4c205d116f6c86')
    assert sha256(source) == SOURCE_HASH
    original = pinned_blob('a00-id', A00_COMMIT, 'media/' + NAME,
                           '83e7b1898d99719beedaf8705fe5684b424c7100')
    assert original.startswith(b'\x89PNG\r\n\x1a\n')
    assert sha256(original) == '14458e7e7c27f39e009ba986d638ffcc461e96affee3ab50648df30567eb0915'
    assert git('openstax-prealgebra-bundle','rev-parse',UPSTREAM_COMMIT+':media/'+NAME).decode().strip() == '83e7b1898d99719beedaf8705fe5684b424c7100'
    base_raw = (LANG/'translation/a00-digit-place.assets.json').read_bytes()
    base = json.loads(base_raw)['assets'][0]
    assert base['indonesian_source']['sha256'] == SOURCE_HASH
    assert (LANG/base['outputs']['id-academic']['path']).read_bytes() == source
    outputs = copy.deepcopy(base['outputs'])
    for output in outputs.values():
        assert sha256((LANG/output['path']).read_bytes()) == output['sha256']
        output['mime_type'] = 'image/svg+xml'
    asset = {
        'media_id': media.get('id'), 'figure_id': 'eip-id1170196618448',
        'source_src': '../../media/' + NAME + '.id-ID.svg', 'mime_type': 'image/svg+xml',
        'indonesian_source': {'path':'media/'+NAME+'.id-ID.svg','sha256':SOURCE_HASH,
                             'git_blob_sha1':'c7fd63689cb359befc7169687a4c205d116f6c86'},
        'canonical_original': {'path':'media/'+NAME,'sha256':sha256(original),
                               'git_blob_sha1':'83e7b1898d99719beedaf8705fe5684b424c7100',
                               'actual_mime':'image/png','source_declared_mime':'image/jpeg'},
        'reuse_authority':'Exact same pinned ID SVG bytes as earlier digit-place 011.jpg.id-ID.svg; original PNG and JPEG are not claimed byte-identical.',
        'example':'5,278,194','leading_empty_digit_cells':8,
        'digit_cells':base['digit_cells'], 'outputs':outputs,
    }
    manifest = {
        'schema':'jv-whole-summary-assets-v1','program':'A00','module':'m81243',
        'section':'fs-id2296006','source_section_sha256':SECTION_HASH,
        'base_asset_manifest':'translation/a00-digit-place.assets.json',
        'base_asset_manifest_sha256':sha256(base_raw),
        'scope':'Only the recap figure; metadata/glossary and full narration remain separate work.',
        'source_review':'Parent read complete pinned ID/EN recap, metadata, glossary and actual SVG XML; viewed exact canonical PNG. Existing SVG label mapping is reused only after exact source identity verification.',
        'canon_consultation':'Parent reread C14/C15 for carry changes and C19/C20 for chart labels, alongside current-stage C24/C25/C31/C33. Full compounds and loans remain provisional.',
        'credits':'OpenStax/Rice University CC BY-NC-SA 4.0 with inherited component restrictions; ID adaptation KokunoYumeto; unofficial Javanese AI-assisted adaptation. No endorsement.',
        'visual_derivative_review':'Parent rendered and inspected both reused JV SVG variants for this recap scope; numeric cells, eight blanks and label visibility agree. Standalone inspection only, not integrated-browser review.','human_review':False,
        'assets':[asset],
    }
    return {f'translation/{UNIT}.assets.json':(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    generated=products()
    assert generated == products()
    for path,raw in generated.items():
        if args.check:
            assert (LANG/path).read_bytes() == raw
        else:
            write_bytes(LANG/path,raw)
    print('Recap source alias verified; three existing SVGs reused without copying or geometry change.')


if __name__ == '__main__':
    main()
