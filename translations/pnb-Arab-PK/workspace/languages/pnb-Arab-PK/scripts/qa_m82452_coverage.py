"""Independent exact full-m82452 source union, A10-001 through A10-005.

No renderer, preparer, translation or prior coverage helper is imported.
Every element (including ID-less children), attribute, own text and tail is
matched at its canonical position. Only one specified section container may
occur twice, with its fixed disjoint ordered child partitions. Detached
adversaries never change the real source, excerpts or manifests.
"""
from collections import Counter, defaultdict
from pathlib import Path
import copy
import hashlib
import json
from lxml import etree as E

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
SOURCE = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82452/index.cnxml'
OUTPUT = BASE / 'qa/m82452-source-coverage.json'
PIN = '38cae454e644abf9f0a623e876994553881597c9'
SOURCE_SHA = '0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310'
SOURCE_BLOB = '7f6d4d2da61f74d10479441822ee62018fb210e4'
CN = 'http://cnx.rice.edu/cnxml'
MATH = 'http://www.w3.org/1998/Math/MathML'
NS = {'c': CN, 'm': MATH, 'md': 'http://cnx.rice.edu/mdml'}
UNITS = ['A10-' + str(i).zfill(3) for i in range(1, 6)]
EXCERPT_PINS = dict(zip(UNITS, [
    (10078, 'ad6b6d61efe78ff33aa5a3f55bc1f87853b9143a0ca37acb361743cf016767bb'),
    (24073, '7ec9ded8624978ec796016e83a246232c4c22243aa4eeb27a142cb916ac87d50'),
    (15546, '131bac729237128c6e3279fcff9b8dff3dc521c9fabd77964431e657cec482cc'),
    (36694, 'ee9de86ade422d18c55dfc103dde31cb017419e668ea3d66cc89f9ae41805686'),
    (29909, '242ca8130350cfc0c21bd459b23a0d58acfded1836866a75cdbeade74def9bf0'),
]))
SPLIT_ID = 'fs-id1170655083568'
TOP_IDS = ['fs-id1170655158095', 'fs-id1170655154091', SPLIT_ID,
           'newelem_para01', 'fs-id1170655199097', 'fs-id1170655247410',
           'fs-id1170655222085', 'fs-id1170655190123']


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    parser = E.XMLParser(resolve_entities=False, no_network=True, remove_blank_text=False,
                         remove_comments=False, remove_pis=False)
    return E.fromstring(raw, parser)


def local(n):
    return E.QName(n).localname


def paths(root):
    found = {}

    def walk(n, p):
        found[n] = p
        seen = Counter()
        for child in n:
            seen[child.tag] += 1
            prefix = 'm:' if E.QName(child).namespace == MATH else 'md:' if E.QName(child).namespace == NS['md'] else ''
            walk(child, p + '/' + prefix + local(child) + '[' + str(seen[child.tag]) + ']')
    walk(root, '/document')
    return found


def description(n):
    return [n.tag, sorted(n.attrib.items()), n.text, n.tail, [description(c) for c in n]]


def tree_hash(n):
    return digest(json.dumps(description(n), ensure_ascii=False, separators=(',', ':')).encode())


class Checks:
    def __init__(self):
        self.count = 0

    def ok(self, test, label):
        self.count += 1
        if not test:
            raise AssertionError(label)


def validate_union(canonical, excerpts):
    c = Checks()
    c.ok(list(excerpts) == UNITS, 'exact five unit identities and order')
    c.ok(all(isinstance(n.tag, str) for n in canonical.iter()), 'source contains elements, not undeclared entities/comments/PIs')
    cp = paths(canonical)
    c.ok(len(cp) == 1754, 'all1754 canonical elements including document')
    source_ids = [n.get('id') for n in cp if n.get('id')]
    c.ok(len(source_ids) == len(set(source_ids)) == 741, '741 unique canonical IDs')
    c.ok(canonical.tag == '{' + CN + '}document' and dict(canonical.attrib) == {}, 'canonical document identity/attributes')
    c.ok([local(n) for n in canonical] == ['title', 'metadata', 'content', 'glossary'], 'full module root order')
    content = canonical.find('c:content', NS)
    c.ok([n.get('id') for n in content] == TOP_IDS, 'exact eight canonical content children')
    split = content[2]
    c.ok(len(split) == 33 and split[13].get('id') == 'fs-id1170655113270' and split[-1].get('id') == 'fs-id1170655197222', 'fixed13/20 split boundary')
    c.ok(split.tag == '{' + CN + '}section' and dict(split.attrib) == {'id': SPLIT_ID}
         and split.text == '\n' and split.tail == '\n', 'only shared source shell is empty apart from exact whitespace')
    coverage = defaultdict(list)
    ep = {}
    for unit, root in excerpts.items():
        c.ok(all(isinstance(n.tag, str) for n in root.iter()), 'no added excerpt entity/comment/PI ' + unit)
        ep[unit] = paths(root)
        c.ok(root.tag == canonical.tag and dict(root.attrib) == {'id': unit.lower().replace('a10-', 'a10-unit-') + '-excerpt'}, 'exact generated wrapper identity ' + unit)
        c.ok(root.tail is None, 'generated wrapper has no tail ' + unit)
        if unit != 'A10-005':
            c.ok(root.text == '\n', 'exact generated wrapper whitespace; no source prose injection ' + unit)

    def own(source, got, unit, wrapper=False):
        p = cp[source]
        c.ok(got.tag == source.tag, 'tag/namespace at ' + unit + ':' + p)
        c.ok(({} if wrapper else dict(got.attrib)) == dict(source.attrib), 'all source attributes at ' + unit + ':' + p)
        c.ok(got.text == source.text, 'exact own text at ' + unit + ':' + p)
        c.ok(got.tail == source.tail, 'exact tail at ' + unit + ':' + p)
        coverage[p].append({'unit': unit, 'excerpt_path': ep[unit][got]})

    def subtree(source, got, unit):
        own(source, got, unit)
        c.ok(len(source) == len(got), 'exact child cardinality/order at ' + unit + ':' + cp[source])
        for s, g in zip(source, got):
            subtree(s, g, unit)

    a, b, d, e, f = (excerpts[u] for u in UNITS)
    c.ok([local(n) for n in a] == ['note', 'para', 'section'] and len(a[2]) == 13, '001 complete prelude and exact first13 section children')
    subtree(content[0], a[0], UNITS[0])
    subtree(content[1], a[1], UNITS[0])
    own(split, a[2], UNITS[0])
    for s, g in zip(list(split)[:13], a[2]):
        subtree(s, g, UNITS[0])
    c.ok(len(b) == 1 and len(b[0]) == 20, '002 only exact remaining20 children, no repeated title or arbitrary regrouping')
    own(split, b[0], UNITS[1])
    for s, g in zip(list(split)[13:], b[0]):
        subtree(s, g, UNITS[1])
    for unit, root, indices in [(UNITS[2], d, [3, 4]), (UNITS[3], e, [5, 6])]:
        c.ok(len(root) == len(indices), 'fixed whole top-level selection ' + unit)
        for i, got in zip(indices, root):
            subtree(content[i], got, unit)
    c.ok([local(n) for n in f] == ['title', 'metadata', 'content', 'glossary'], '005 includes all metadata/title/glossary in source order')
    own(canonical, f, UNITS[4], wrapper=True)
    subtree(canonical[0], f[0], UNITS[4])
    subtree(canonical[1], f[1], UNITS[4])
    own(content, f[2], UNITS[4])
    c.ok(len(f[2]) == 1, '005 exact exercise-section content partition')
    subtree(content[7], f[2][0], UNITS[4])
    subtree(canonical[3], f[3], UNITS[4])

    c.ok(set(coverage) == set(cp.values()), 'every canonical path covered, including all ID-less nodes')
    overlaps = {p: owners for p, owners in coverage.items() if len(owners) != 1}
    c.ok(overlaps == {cp[split]: [{'unit': UNITS[0], 'excerpt_path': '/document/section[1]'}, {'unit': UNITS[1], 'excerpt_path': '/document/section[1]'}]}, 'only shared empty section shell overlaps; no general duplicate exception')
    used = Counter(row['unit'] for owners in coverage.values() for row in owners)
    c.ok(dict(used) == dict(zip(UNITS, [105, 281, 277, 468, 624])), 'every excerpt source node used once, except one exact shared shell')
    for unit, root in excerpts.items():
        c.ok(used[unit] == len(list(root.iter())) - (unit != 'A10-005'), 'no unaccounted ID-less excerpt node ' + unit)

    # Independently reassemble the document. The only removed attribute is the
    # declared generated excerpt ID; no source text/tail normalization occurs.
    rebuilt = copy.deepcopy(f)
    rebuilt.attrib.clear()
    body = rebuilt.find('c:content', NS)
    final_section = body[0]
    body.remove(final_section)
    for n in a:
        body.append(copy.deepcopy(n))
    for n in b[0]:
        body[2].append(copy.deepcopy(n))
    for fragment in [d, e]:
        for n in fragment:
            body.append(copy.deepcopy(n))
    body.append(final_section)
    c.ok(description(rebuilt) == description(canonical), 'complete reconstructed source tree/text/tail/attribute identity; no whitespace exceptions')
    c.ok([n.get('id') for n in rebuilt.iter() if n.get('id')] == source_ids, 'all741 IDs restored in exact canonical order/ancestry')
    source_math = canonical.findall('.//m:math', NS)
    c.ok(len(source_math) == 46, '46 complete canonical MathML owners')
    c.ok([description(n) for n in rebuilt.findall('.//m:math', NS)] == [description(n) for n in source_math], 'all46 exact MathML trees/attributes/text/tails/source order')
    counts = Counter(local(n) for n in canonical.iter())
    math_owners = []
    for n in source_math:
        owner = next((p for p in n.iterancestors() if p.get('id')), None)
        math_owners.append({'source_path': cp[n], 'nearest_source_id': owner.get('id') if owner is not None else None,
                            'source_tree_sha256': tree_hash(n), 'excerpt_owner': coverage[cp[n]][0]})
    return c.count, {'canonical_paths': len(cp), 'idless_elements': sum(not n.get('id') for n in cp),
                     'ids': len(source_ids), 'coverage_occurrences': sum(used.values()), 'per_unit_source_nodes': dict(used),
                     'source_tag_counts': dict(sorted(counts.items())), 'canonical_tree_sha256': tree_hash(canonical),
                     'reassembled_tree_sha256': tree_hash(rebuilt), 'only_overlap': overlaps,
                     'math_owners': math_owners}


def main():
    raw = SOURCE.read_bytes()
    logical = raw.replace(b'\r\n', b'\n')
    assert len(logical) == 113967 and digest(logical) == SOURCE_SHA, 'Pinned complete canonical source differs'
    assert hashlib.sha1(b'blob ' + str(len(logical)).encode() + b'\0' + logical).hexdigest() == SOURCE_BLOB
    lock = json.loads((BASE / 'sources.lock.json').read_text('utf-8'))
    upstream = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    assert upstream['commit'] == PIN and upstream['url'] == 'https://github.com/openstax/osbooks-prealgebra-bundle.git'
    canonical = parse(logical)
    excerpts, inputs = {}, []
    for unit in UNITS:
        name = unit.lower()
        path = BASE / 'source-excerpts' / (name.replace('a10-', 'a10-unit-') + '.cnxml')
        mp = BASE / 'source-excerpts' / ('manifest-' + name + '.json')
        mr = mp.read_bytes()
        manifest = json.loads(mr)
        er = path.read_bytes()
        assert (len(er), digest(er)) == EXCERPT_PINS[unit], 'Frozen source excerpt identity differs ' + unit
        assert manifest['module'] == 'm82452' and manifest['commit'] == PIN
        assert (manifest['full_module_bytes'], manifest['full_module_sha256'], manifest['canonical_git_blob_sha1']) == (113967, SOURCE_SHA, SOURCE_BLOB)
        assert (len(er), digest(er)) == (manifest['excerpt_bytes'], manifest['excerpt_sha256']), 'Declared excerpt bytes differ ' + unit
        root = parse(er)
        assert [n.get('id') for n in root.iter() if n is not root and n.get('id')] == manifest['source_ids_in_document_order'], 'Manifest source-ID order differs ' + unit
        excerpts[unit] = root
        inputs.append({'unit': unit, 'excerpt': path.relative_to(BASE).as_posix(), 'excerpt_bytes': len(er), 'excerpt_sha256': digest(er),
                       'manifest': mp.relative_to(BASE).as_posix(), 'manifest_sha256': digest(mr)})
    checks, coverage = validate_union(canonical, excerpts)
    mutations = []

    def mutation(name, change):
        detached = {u: copy.deepcopy(r) for u, r in excerpts.items()}
        change(detached)
        try:
            validate_union(canonical, detached)
        except (AssertionError, IndexError, KeyError, ValueError) as error:
            mutations.append({'name': name, 'rejected_by': str(error)})
        else:
            raise AssertionError('Surviving detached mutation: ' + name)

    def select(roots, unit, xpath):
        return roots[unit].xpath(xpath, namespaces=NS)[0]

    def remove(n):
        n.getparent().remove(n)

    mutation('ID-less section title omitted', lambda r: remove(select(r, 'A10-001', './c:section/c:title')))
    mutation('ID-less figure caption duplicated', lambda r: select(r, 'A10-001', './/c:figure').append(copy.deepcopy(select(r, 'A10-001', './/c:caption'))))
    mutation('source ID renamed', lambda r: select(r, 'A10-001', './/c:para').set('id', 'invented'))
    mutation('direct-text source note conclusion altered', lambda r: setattr(select(r, 'A10-001', './/c:note[@class="manipulative-math"]'), 'text', 'Invented conclusion'))
    mutation('mixed-content term tail numeral changed', lambda r: setattr(select(r, 'A10-001', './/c:term'), 'tail', '999'))
    mutation('mixed-content emphasis regrouped', lambda r: select(r, 'A10-001', './/c:term').append(select(r, 'A10-001', './/c:term/following-sibling::c:emphasis')))
    mutation('source table cell omitted', lambda r: remove(select(r, 'A10-002', './/c:entry')))
    mutation('source table ID-less cell duplicated', lambda r: select(r, 'A10-002', './/c:row').append(copy.deepcopy(select(r, 'A10-002', './/c:entry'))))
    mutation('source table cell text changed', lambda r: setattr(select(r, 'A10-003', './/c:entry'), 'text', '999'))
    mutation('source table row order swapped', lambda r: select(r, 'A10-003', './/c:tbody').insert(0, select(r, 'A10-003', './/c:tbody')[-1]))
    mutation('source table cell span inferred', lambda r: select(r, 'A10-002', './/c:entry').set('colspan', '2'))
    mutation('MathML spacing attribute erased', lambda r: select(r, 'A10-001', './/m:mspace').attrib.clear())
    mutation('MathML namespace replaced by CNXML', lambda r: setattr(select(r, 'A10-003', './/m:math'), 'tag', '{' + CN + '}math'))
    mutation('MathML ID-less leaf numeric text changed', lambda r: setattr(select(r, 'A10-005', './/m:mn'), 'text', '999'))
    mutation('MathML entire owner omitted', lambda r: remove(select(r, 'A10-004', './/m:math')))
    mutation('source image path swapped', lambda r: select(r, 'A10-005', './/c:image').set('src', '../../media/wrong.jpg'))
    mutation('original inaccurate alt silently erased', lambda r: select(r, 'A10-001', './/c:media').set('alt', ''))
    mutation('source link destination changed', lambda r: select(r, 'A10-004', './/c:link').set('target-id', 'wrong'))
    mutation('metadata objective ID-less item omitted', lambda r: remove(select(r, 'A10-005', './/md:abstract/c:list/c:item')))
    mutation('metadata UUID altered', lambda r: setattr(select(r, 'A10-005', './/md:uuid'), 'text', 'invented'))
    mutation('module root title omitted', lambda r: r['A10-005'].remove(r['A10-005'][0]))
    mutation('glossary ID-less meaning content changed', lambda r: setattr(select(r, 'A10-005', './/c:meaning'), 'text', 'invented'))
    mutation('whole glossary omitted', lambda r: remove(select(r, 'A10-005', './c:glossary')))
    mutation('source root attribute invented', lambda r: r['A10-005'].set('lang', 'en'))
    mutation('canonical root whitespace changed', lambda r: setattr(r['A10-005'], 'text', '\n'))
    mutation('canonical content whitespace lost', lambda r: setattr(select(r, 'A10-005', './c:content'), 'text', None))
    mutation('boundary source child tail erased', lambda r: setattr(r['A10-001'][2][-1], 'tail', None))
    mutation('generated wrapper prose injection', lambda r: setattr(r['A10-002'], 'text', 'Extra source conclusion'))
    mutation('general duplicate top-level subtree', lambda r: r['A10-002'].append(copy.deepcopy(r['A10-004'][0])))
    mutation('split section title repeated', lambda r: r['A10-002'][0].insert(0, copy.deepcopy(r['A10-001'][2][0])))
    mutation('split boundary shifted with same combined union', lambda r: r['A10-002'][0].insert(0, r['A10-001'][2][-1]))
    mutation('shared shell own-text injection', lambda r: setattr(r['A10-002'][0], 'text', 'Invented source prose'))
    mutation('same-ID shared shell gains extra attributes', lambda r: r['A10-002'][0].set('class', 'invented'))
    mutation('whole section order swapped', lambda r: r['A10-004'].insert(0, r['A10-004'][-1]))
    mutation('source newline element omitted', lambda r: remove(select(r, 'A10-005', './/c:newline')))
    mutation('ID-less circled-token part changed', lambda r: setattr(select(r, 'A10-005', './/c:span[@class="token"]'), 'text', '(z)'))

    receipt = {'schema': 'pnb-independent-complete-module-source-union-v1', 'module': 'm82452', 'status': 'pass',
               'scope': 'Exact complete canonical module source selection, A10-001 through A10-005. Not a linguistic, reader or whole-book certification.',
               'source': {'path': SOURCE.relative_to(ROOT).as_posix(), 'commit': PIN, 'logical_lf_bytes': len(logical),
                          'logical_lf_sha256': digest(logical), 'working_raw_sha256': digest(raw), 'git_blob_sha1': SOURCE_BLOB},
               'input_files': inputs, 'checks': checks, 'coverage': coverage, 'detached_mutations': mutations,
               'detached_mutation_count': len(mutations),
               'canonical_whitespace_exceptions': [],
               'wrapper_only_transformations': [
                   'A10-001..004 generated document wrappers and their exact single-LF own text are not canonical source nodes; their children flatten selected canonical content.',
                   'A10-005 carries the canonical document/root text, title, metadata, content-own whitespace and glossary; only its exact generated excerpt id is removed when restoring the canonical attribute-less document.',
                   'The single source section fs-id1170655083568 has exact empty-whitespace shell copies in001/002 and fixed disjoint ordered child partitions13/20. This is the only allowed overlap.',
                   'XML declarations, redundant namespace declarations and prefix serialization are wrapper syntax; expanded namespace names, source attributes, source text and tails are compared exactly.'],
               'limitations': [
                   'No renderer/preparer/translation helper imported or invoked. The proof concerns excerpt source coverage and declared source pins, not translated prose accuracy, accessible rendering or image bytes.',
                   'Source errors and inaccurate original alt text are deliberately retained; independent per-unit translation/correction and browser reviews remain necessary.',
                   'No canonical text/tail whitespace is normalized during union comparison. Only CRLF-to-LF file hash policy is used to identify the acquired pinned source.',
                   'The full A10 book and all-five-work assignment remain incomplete.'],
               'script_sha256': digest(Path(__file__).read_bytes()), 'whole_book_translation_complete': False}
    OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'pass', 'checks': checks, 'canonical_elements': 1754, 'source_ids': 741, 'mathml_trees': 46,
                      'detached_mutations': len(mutations), 'receipt_sha256': digest(OUTPUT.read_bytes())}))


if __name__ == '__main__':
    main()
