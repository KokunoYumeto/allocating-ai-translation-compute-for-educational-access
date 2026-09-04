"""Bind the complete m81243 assembly to all reviewed asset/audio dependencies."""
import json
import re
import xml.etree.ElementTree as ET

from build import XML_LANG
from build_units import sha
from config import LANG, TRACKS
import draft_complete_a00_module as complete
from rounding_checks import ID_NOTE
from summary_checks import checked_rules

ASSEMBLY_RECEIPT_SHA256 = 'bb3f7406f842c4f4c56410b6c8b4e105e7a52a65d5ad0b26f6b55565318bcf85'
CONTENT_UNITS = [unit for _, unit in complete.SECTION_UNITS if unit != 'a00-whole-summary.recap']
ASSET_UNITS = ['a00-place-value', 'a00-digit-place', 'a00-name-whole',
               'a00-write-whole', 'a00-rounding', 'a00-whole-summary',
               'a00-section-exercises']
ASSET_MANIFEST_SHA256 = {
    'a00-place-value': 'dc5ce29974b18b890932c49fa2493a0cfafed2d6a07666e1ba0516e845fd9bea',
    'a00-digit-place': 'c977cfea69046afacb3da1ef62996f45d2cef80808f1d6f005556f1e9285dcfe',
    'a00-name-whole': 'f7476bfa8211e8956ea89fcec6077e7bc3777190721cd29b673cd10fe0f77d26',
    'a00-write-whole': '46a9f8144985444fd135148bac7733596fb8353f380de1f4e0abb15a0343bb29',
    'a00-rounding': 'ee409884dfe05113ce081ab155f0d531aa3ce1273582b3bd27640deb861d4e33',
    'a00-whole-summary': '6ff6ff6b152575f9629caf7270ff0012dd721ae64ab4379df76e60a13713202b',
    'a00-section-exercises': '2e0af9ba286a88d9b1a53605154a8b2598c367f5ac82aa5a97730a808c09eb11',
}
AUDIO_RECEIPTS = {
    'a00-number-sense': ('qa/receipt.json', '3eba6a6498fd983574a21c32e996941ee59099251c520d1bda96d25a91c9ddd8'),
    'a00-place-value': ('qa/a00-place-value.build-receipt.json', 'b21e46ecb5dce7e845ffcd1e142d2583b76cc5f85b2f40da95bada273316a74d'),
    'a00-digit-place': ('qa/a00-digit-place.build-receipt.json', '0a592d034f117bc098d95d76c41bb681b86a9e04889f5e04b64fe8df3b01cbdc'),
    'a00-name-whole': ('qa/a00-name-whole.build-receipt.json', '103b4defc32be6d62d71f823e4653b22bff05dea9bbdfc39e35e516e67de50e4'),
    'a00-write-whole': ('qa/a00-write-whole.build-receipt.json', '2e030ed73df40df4255fe156f6dc0a00e0dda68fd805dd60fc144fb964b4bdf8'),
    'a00-rounding': ('qa/a00-rounding.build-receipt.json', '7adfed7f384b80edaf1b6ecccd9d853e70c11c521bef33b3396cbdb013e11b57'),
    'a00-whole-summary': ('qa/a00-whole-summary.components-build-receipt.json', '28a9678649fc74fe7dc2da2f4c2072eace74922c8e569f21cf99a386a7640c15'),
    'a00-section-exercises': ('qa/a00-section-exercises.build-receipt.json', '30f5232962643b9c092a117d44279c0cf2284ba6d4f02641dd35b5b183028eaa'),
}
ID_OFFLINE_LINK_NOTE = ('Pranala luar asli dipertahankan; isi tujuannya tidak '
                        'disertakan dalam pembaca luring ini.')


def checked_assembly():
    generated = complete.products()
    for name, raw in generated.items():
        assert (LANG / name).read_bytes() == raw, 'Stale complete-module assembly: ' + name
    receipt_name = f'qa/{complete.UNIT}.assembly-receipt.json'
    assert sha(generated[receipt_name]) == ASSEMBLY_RECEIPT_SHA256
    receipt = json.loads(generated[receipt_name])
    assert receipt['complete_source_scope'] is True and receipt['whole_module_complete'] is False
    roots = {track: ET.parse(LANG / f'translation/{complete.UNIT}.{track}.cnxml').getroot()
             for track in TRACKS}
    return roots, receipt


def asset_map(track, root):
    assert track in TRACKS
    result, dependencies = {}, {}
    source_src = '../../media/CNX_BMath_Figure_01_01_001.jpg.id-ID.svg'
    path = LANG / ('translation/number-line.jv-Latn-ID.svg' if track.startswith('jv')
                   else 'translation/number-line.id-ID.svg')
    raw = path.read_bytes()
    expected = ('b847d283bf2b0bf26ab724e92504767fba64a095e0e4aadc8772837caa72216c'
                if track.startswith('jv') else
                '80155d34716552ddf7b2cf0d879673ffc10424f6712798c30e7219f4013e884e')
    assert sha(raw) == expected
    result[source_src] = {'bytes': raw, 'mime_type': 'image/svg+xml'}
    dependencies[path.relative_to(LANG).as_posix()] = expected
    for unit in ASSET_UNITS:
        manifest_path = LANG / f'translation/{unit}.assets.json'
        manifest_raw = manifest_path.read_bytes()
        assert sha(manifest_raw) == ASSET_MANIFEST_SHA256[unit], 'Changed reviewed asset manifest: ' + unit
        dependencies[manifest_path.relative_to(LANG).as_posix()] = ASSET_MANIFEST_SHA256[unit]
        manifest = json.loads(manifest_raw)
        for asset in manifest['assets']:
            assert asset['source_src'] not in result, 'Duplicated complete-module source asset key'
            output = asset['outputs'][track]
            output_path = LANG / output['path']
            output_raw = output_path.read_bytes()
            assert sha(output_raw) == output['sha256']
            result[asset['source_src']] = {
                'bytes': output_raw,
                'mime_type': output.get('mime_type', asset['mime_type']),
            }
            dependencies[output_path.relative_to(LANG).as_posix()] = output['sha256']
    source_images = [node.get('src') for node in root.iter('{http://cnx.rice.edu/cnxml}image')]
    assert len(source_images) == len(set(source_images)) == 47
    assert set(source_images) == set(result)
    return result, dependencies


def audio_hashes(unit):
    receipt_name, expected = AUDIO_RECEIPTS[unit]
    raw = (LANG / receipt_name).read_bytes()
    assert sha(raw) == expected, 'Changed reviewed audio receipt: ' + unit
    return json.loads(raw)['output_sha256'], {receipt_name: expected}


def rounding_editorial_material():
    """Return reviewed unmarked ID-only notices from their bounded products."""
    hashes, receipt_dependency = audio_hashes('a00-rounding')
    names = [
        'review/units/a00-rounding.html',
        'review/audio/a00-rounding.id-academic.md',
        'review/audio/a00-rounding.id-academic.ssml',
    ]
    raw = {name: (LANG / name).read_bytes() for name in names}
    for name in names:
        assert sha(raw[name]) == hashes[name], 'Stale bounded rounding editorial dependency: ' + name

    reader_text = raw[names[0]].decode()
    transcript_text = raw[names[1]].decode()
    ssml_root = ET.fromstring(raw[names[2]])
    assert reader_text.count(ID_NOTE) == 1
    assert reader_text.count(ID_OFFLINE_LINK_NOTE) == 1
    assert transcript_text.count(ID_NOTE) == 1
    assert transcript_text.index(ID_NOTE) < transcript_text.index('\n## ')
    assert sum(''.join(node.itertext()) == ID_NOTE for node in ssml_root.findall('{*}p')) == 1
    assert list(ssml_root)[1].tag.endswith('}p')
    assert ''.join(list(ssml_root)[1].itertext()) == ID_NOTE

    for track in ('jv-conversation', 'jv-academic'):
        md_name = f'review/audio/a00-rounding.{track}.md'
        ssml_name = f'review/audio/a00-rounding.{track}.ssml'
        md_raw = (LANG / md_name).read_bytes()
        ssml_raw = (LANG / ssml_name).read_bytes()
        assert sha(md_raw) == hashes[md_name]
        assert sha(ssml_raw) == hashes[ssml_name]
        assert ID_NOTE not in md_raw.decode()
        assert ID_NOTE not in ''.join(ET.fromstring(ssml_raw).itertext())

    return ({'indonesian_accessibility_notice': ID_NOTE,
             'offline_link_notice': ID_OFFLINE_LINK_NOTE},
            {**receipt_dependency, **{name: hashes[name] for name in names}})


def transcript_blocks(raw):
    text = raw.decode()
    matches = list(re.finditer(r'^## ([^\n]+)\n\n', text, flags=re.M))
    blocks = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].rstrip('\n')
        assert body
        blocks.append((match.group(1), body))
    return blocks


def ssml_blocks(raw, locale):
    root = ET.fromstring(raw)
    assert root.get(XML_LANG) == locale
    children = list(root)
    blocks = []
    for index, node in enumerate(children):
        if node.tag.endswith('}mark'):
            assert index + 2 < len(children)
            para, pause = children[index + 1:index + 3]
            assert para.tag.endswith('}p') and pause.tag.endswith('}break')
            blocks.append((node.get('name'), ''.join(para.itertext())))
    return blocks


def saved_blocks(unit, track):
    hashes, dependencies = audio_hashes(unit)
    transcript_name = f'review/audio/{unit}.{track}.md'
    ssml_name = f'review/audio/{unit}.{track}.ssml'
    transcript_raw = (LANG / transcript_name).read_bytes()
    ssml_raw = (LANG / ssml_name).read_bytes()
    assert sha(transcript_raw) == hashes[transcript_name]
    assert sha(ssml_raw) == hashes[ssml_name]
    blocks = transcript_blocks(transcript_raw)
    assert blocks == ssml_blocks(ssml_raw, TRACKS[track][0])
    dependencies.update({transcript_name: hashes[transcript_name], ssml_name: hashes[ssml_name]})
    return blocks, dependencies


def full_blocks(track):
    assert track in TRACKS
    summary, dependencies = saved_blocks('a00-whole-summary', track)
    rules = checked_rules()
    groups = rules['reader_and_ssml_contract']['component_mark_groups']
    summary_by_mark = dict(summary)
    assert list(summary_by_mark) == rules['reader_and_ssml_contract']['block_marks']
    result = [(mark, summary_by_mark[mark]) for mark in groups['title'] + groups['metadata']]
    section_map = dict(complete.SECTION_UNITS)
    for anchor, unit in complete.SECTION_UNITS:
        if unit == 'a00-whole-summary.recap':
            result.extend((mark, summary_by_mark[mark]) for mark in groups['recap'])
            continue
        blocks, bound = saved_blocks(unit, track)
        dependencies.update(bound)
        if blocks[0][0] == complete.MODULE + '--title':
            blocks[0] = (complete.MODULE + '--' + anchor + '--title', blocks[0][1])
        result.extend(blocks)
    result.extend((mark, summary_by_mark[mark]) for mark in groups['glossary'])
    marks = [mark for mark, _ in result]
    assert len(result) == len(set(marks)) == 183
    assert marks[0] == 'm81243--outer-title' and marks[-1] == 'm81243--fs-id4338000'
    assert set(section_map) == {anchor for anchor, _ in complete.SECTION_UNITS}
    assert all(body for _, body in result)
    return result, dependencies
