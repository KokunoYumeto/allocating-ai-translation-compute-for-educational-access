"""Verify indexed bytes and keep HTML/PDF review readiness independent."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LEGACY_HTML_UNITS = {f'MR-BRIDGE-{number:03}' for number in range(1, 6)}
# Explicitly registered source assemblies have a different input contract from
# a bridge unit. They do not acquire HTML readiness from a reviewed module PDF.
ASSEMBLED_MODULES = {
    'A20-m81373': ('A20:m81373', 'tools/assemble_m81373.py', 'tools/build_m81373_pdf.py'),
}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def indexed(path):
    return git('show', ':mr-Deva-IN/'+path)


def indexed_json(path):
    return json.loads(indexed(path))


def verify_index(read, all_paths, staged):
    """Pure index reader, also exercised with tiny in-memory regression fixtures.

    ``read`` receives language-relative paths. Review states are explicit human/
    agent records, not inferred from successful rendering or a filename's presence.
    The legacy five-reader checkpoint is supported without the newer state map.
    """
    assert all(path in ('.gitignore', '.gitattributes') or path.startswith('mr-Deva-IN/')
               for path in staged), staged
    items = {}
    sizes = {}
    language_paths = {p.removeprefix('mr-Deva-IN/') for p in all_paths
                      if p.startswith('mr-Deva-IN/')}

    def data(path):
        value = json.loads(read(path))
        assert isinstance(value, dict), (path, 'expected JSON object')
        return value

    def pin(path, expected, size=None):
        assert isinstance(path, str) and path and '\\' not in path and ':' not in path
        relative = PurePosixPath(path)
        assert not relative.is_absolute() and '..' not in relative.parts, path
        assert path in language_paths, (path, 'not in index')
        assert re.fullmatch(r'[0-9a-f]{64}', expected), (path, 'invalid SHA-256')
        assert path not in items or items[path] == expected, (path, 'conflicting index pins')
        items[path] = expected
        if size is not None:
            assert type(size) is int and size >= 0, (path, 'invalid byte count')
            assert path not in sizes or sizes[path] == size, (path, 'conflicting byte counts')
            sizes[path] = size

    status = data('STATUS.json')

    def unit_set(key, default=()):
        values = status.get(key, default)
        assert isinstance(values, list) and len(values) == len(set(values)), key
        assert all(isinstance(u, str) and (re.fullmatch(r'MR-BRIDGE-[0-9]{3}', u) or u in ASSEMBLED_MODULES)
                   for u in values), key
        return set(values)

    ready = unit_set('ready_review_drafts')
    html_ready = unit_set('ready_html_review_drafts', list(ready))
    pdf_ready = unit_set('ready_pdf_review_drafts', [])
    assert ready == html_ready | pdf_ready, 'ready-unit union disagrees with format lists'
    states = status.get('artifact_review_states', {})
    assert isinstance(states, dict), 'artifact review states must be an object'
    seen_states = set()

    def review_state(unit, format_, artifact_path, artifact_sha256):
        ready_set = html_ready if format_ == 'html' else pdf_ready
        if not states:
            # Historical checkpoint compatibility; new pending artifacts require
            # an explicit state, not a relaxation of browser acceptance.
            assert format_ == 'html' and unit in ready_set and unit in LEGACY_HTML_UNITS, (
                unit, 'missing review state')
            return 'ready_review_draft'
        entry = states.get(unit, {}).get(format_)
        assert isinstance(entry, dict), (unit, format_, 'missing review state')
        state = entry.get('state')
        assert state in {'ready_review_draft', 'unreviewed', 'known_issue', 'recheck_required'}, entry
        assert (state == 'ready_review_draft') == (unit in ready_set), (unit, format_, 'ready mismatch')
        assert isinstance(entry.get('reason'), str) and entry['reason'].strip(), entry
        evidence = entry.get('evidence', [])
        assert isinstance(evidence, list), entry
        if state in {'ready_review_draft', 'known_issue', 'recheck_required'}:
            assert evidence, (unit, format_, 'missing review evidence')
        for path in evidence:
            assert isinstance(path, str) and path.startswith('qa/') and path in language_paths, (unit, path)
            assert read(path).strip(), (unit, path, 'empty review evidence')
        if state == 'ready_review_draft':
            # Structural build receipts do not certify manual review. Bind the
            # separately authored review to one format, exact artifact bytes,
            # and exact report bytes so a rebuild cannot inherit stale QA.
            assert entry.get('reviewed_artifact_sha256') == artifact_sha256, (
                unit, format_, 'stale or missing reviewed-artifact hash')
            review_path = entry.get('review_receipt')
            assert isinstance(review_path, str) and review_path.startswith('qa/') and review_path in language_paths, (
                unit, format_, 'missing format-specific review receipt')
            review = data(review_path)
            assert review.get('schema') == 1 and review.get('result') == 'PASS', review_path
            assert review.get('unit') == unit and review.get('format') == format_, (
                unit, format_, 'review belongs to another unit or format')
            assert review.get('artifact_path') == artifact_path and review.get('artifact_sha256') == artifact_sha256, (
                unit, format_, 'review belongs to another artifact')
            reports = review.get('evidence')
            assert isinstance(reports, list) and reports, (review_path, 'missing reviewed report pins')
            report_paths = [report.get('path') for report in reports if isinstance(report, dict)]
            assert len(report_paths) == len(reports) == len(set(report_paths)), (
                review_path, 'invalid or duplicate reviewed report pins')
            assert set(report_paths) == set(evidence), (
                review_path, 'review report not declared in state or not all declared evidence is pinned')
            for report in reports:
                assert isinstance(report, dict) and report.get('path') in evidence, (
                    review_path, 'review report not declared in state')
                pin(report['path'], report['sha256'], report.get('bytes'))
        seen_states.add((unit, format_))
        return state

    master = data('sources.lock.json')
    for witness in master['witnesses']:
        pin(witness['path'], witness['sha256'], witness.get('bytes'))
    legacy = data('qa/build-receipt.json')
    assert legacy['result'] == 'PASS'
    pin('translations/MR-BRIDGE-001.xml', legacy['source_sha256'])
    pin('output/MR-BRIDGE-001.html', legacy['html_sha256'])
    assert review_state('MR-BRIDGE-001', 'html', 'output/MR-BRIDGE-001.html', legacy['html_sha256']) == 'ready_review_draft'
    # The original legacy browser receipt predates HTML-hash fields. Preserve
    # that limitation rather than inventing a retrospective render hash.
    assert data('qa/browser-receipt.json')['result'] == 'PASS'
    html_units = {'MR-BRIDGE-001'}
    pdf_units = set()
    built_artifacts = {'output/MR-BRIDGE-001.html'}

    def unit_inputs(unit, receipt, lock_key):
        assert receipt['unit'] == unit and receipt['result'] == 'PASS'
        pin('translations/'+unit+'.xml', receipt['source_sha256'])
        pin('units/'+unit+'.json', receipt['config_sha256'])
        pin('provenance/'+unit+'.lock.json', receipt[lock_key])
        lock = data('provenance/'+unit+'.lock.json')
        assert lock['unit'] == unit and lock['locale'] == 'mr-Deva-IN'
        for witness in lock['witnesses']:
            pin(witness['path'], witness['sha256'], witness.get('bytes'))

    for path in sorted(language_paths):
        match = re.fullmatch(r'qa/(MR-BRIDGE-[0-9]{3})-build-receipt.json', path)
        if not match:
            continue
        unit = match[1]
        receipt = data(path)
        unit_inputs(unit, receipt, 'provenance_lock_sha256')
        assert receipt['locale'] == 'mr-Deva-IN'
        pin('output/'+unit+'.html', receipt['html_sha256'], receipt.get('html_bytes'))
        for style in receipt['stylesheet_files']:
            pin(style['path'], style['sha256'])
        for asset in receipt.get('embedded_assets', []):
            pin(asset['path'], asset['sha256'], asset['bytes'])
        artifact_path = 'output/'+unit+'.html'
        state = review_state(unit, 'html', artifact_path, receipt['html_sha256'])
        browser_path = 'qa/'+unit+'-browser-receipt.json'
        if state == 'ready_review_draft':
            browser = data(browser_path)
            assert browser['result'] == 'PASS' and browser['htmlSha256'] == receipt['html_sha256']
        elif browser_path in language_paths:
            browser = data(browser_path)
            # A stale historical receipt is acceptable only when explicitly
            # classified as needing a new review; it cannot certify this HTML.
            if browser.get('htmlSha256') != receipt['html_sha256']:
                assert state == 'recheck_required', (unit, 'undeclared stale browser receipt')
        html_units.add(unit)
        built_artifacts.add(artifact_path)

    for path in sorted(language_paths):
        match = re.fullmatch(r'qa/(MR-BRIDGE-[0-9]{3})-pdf-build-receipt.json', path)
        if not match:
            continue
        unit = match[1]
        receipt = data(path)
        unit_inputs(unit, receipt, 'lock_sha256')
        pin('output/pdf/'+unit+'.pdf', receipt['pdf_sha256'], receipt['pdf_bytes'])
        pin('tools/build_pdf.py', receipt['builder_sha256'])
        pin('tools/build_unit.py', receipt['pin_validator_sha256'])
        assert receipt['attached_xml_sha256'] == receipt['source_sha256'], unit
        for asset in receipt['assets']:
            pin(asset['path'], asset['sha256'], asset.get('bytes'))
        # Fonts are embedded in the artifact. Their host-local rebuild pins are
        # recorded, but these installed OS font files are not Git inputs.
        assert receipt['fonts'], (unit, 'no embedded-font evidence')
        for font in receipt['fonts']:
            assert re.fullmatch(r'[0-9a-f]{64}', font['sha256'])
        artifact_path = 'output/pdf/'+unit+'.pdf'
        review_state(unit, 'pdf', artifact_path, receipt['pdf_sha256'])  # Never use HTML/browser QA for PDF.
        pdf_units.add(unit)
        built_artifacts.add(artifact_path)

    assemblies = {}
    for unit, (source_module, assembler_path, pdf_builder_path) in ASSEMBLED_MODULES.items():
        source_path = 'translations/'+unit+'.xml'
        assembly_path = 'qa/'+unit+'-assembly-receipt.json'
        if not ({source_path, assembly_path} & language_paths):
            continue
        assert {source_path, assembly_path} <= language_paths, (unit, 'incomplete source assembly')
        assembly = data(assembly_path)
        assert assembly.get('schema') == 1 and assembly.get('module') == source_module, (
            unit, 'wrong assembly identity')
        output = assembly['output']
        assert output['path'] == source_path, (unit, 'wrong assembly source path')
        pin(source_path, output['sha256'], output['bytes'])
        inputs = assembly['inputs']
        assert isinstance(inputs, dict) and inputs, (unit, 'missing assembly inputs')
        assert assembler_path in inputs and 'sources.lock.json' in inputs, (unit, 'missing assembly builder/master pin')
        for path, witness in inputs.items():
            pin(path, witness['sha256'], witness['bytes'])
        source_members = assembly['source_members']
        assert set(source_members) == {'en', 'id'}, (unit, 'missing source locale')
        for witness in source_members.values():
            path = witness['path']
            assert path in inputs, (unit, 'source member omitted from assembly inputs')
            pin(path, witness['sha256'], witness['bytes'])
        counts = assembly['counts']
        keys = ('canonical_ids', 'unique_selectors', 'source_exercises', 'source_supplied_answers',
                'authored_answers_to_source_omissions', 'canonical_assets', 'math_checks')
        assert all(type(counts.get(k)) is int and counts[k] >= 0 for k in keys), (unit, 'invalid assembly counts')
        ids = assembly['canonical_id_order']
        assert isinstance(ids, list) and len(ids) == len(set(ids)) == counts['canonical_ids'], (
            unit, 'assembly canonical-ID census mismatch')
        selectors = [s['locator'] for s in assembly['selection_order']]
        assert len(selectors) == len(set(selectors)) == counts['unique_selectors'], (
            unit, 'assembly selector census mismatch')
        assert all(s.startswith(source_module+'#') and s.split('#', 1)[1] in ids for s in selectors), (
            unit, 'assembly selector outside canonical IDs')
        assert counts['source_exercises'] == counts['source_supplied_answers'] + counts['authored_answers_to_source_omissions'], (
            unit, 'assembly answer census mismatch')
        assert len(assembly['expected_math']) == counts['math_checks'], (unit, 'assembly math census mismatch')
        assert len(assembly['assets']) == counts['canonical_assets'], (unit, 'assembly asset census mismatch')
        for path, asset in assembly['assets'].items():
            assert path.startswith('assets/') and path in inputs, (unit, 'asset omitted from assembly inputs')
            pin(path, asset['sha256'], asset['bytes'])
        assemblies[unit] = assembly

    for unit, (source_module, assembler_path, pdf_builder_path) in ASSEMBLED_MODULES.items():
        path = 'qa/'+unit+'-pdf-build-receipt.json'
        if path not in language_paths:
            continue
        assert unit in assemblies, (unit, 'module PDF lacks source assembly')
        assembly = assemblies[unit]
        receipt = data(path)
        assert receipt.get('schema') == 1 and receipt.get('unit') == unit and receipt.get('result') == 'PASS', path
        assert receipt.get('locale') == 'mr-Deva-IN', path
        source_path = 'translations/'+unit+'.xml'
        artifact_path = 'output/pdf/'+unit+'.pdf'
        pin(source_path, receipt['source_sha256'])
        pin('qa/'+unit+'-assembly-receipt.json', receipt['assembly_receipt_sha256'])
        pin(assembler_path, receipt['assembly_builder_sha256'])
        pin(pdf_builder_path, receipt['builder_sha256'])
        pin('tools/build_pdf.py', receipt['immutable_pdf_helper_sha256'])
        pin('tools/build_unit.py', receipt['pin_validator_sha256'])
        pin(artifact_path, receipt['pdf_sha256'], receipt['pdf_bytes'])
        assert receipt['attached_xml_sha256'] == receipt['source_sha256'], (unit, 'wrong attached XML')
        assert receipt['input_pins'] == assembly['inputs'], (unit, 'PDF/assembly input manifests differ')
        assert receipt['pinned_inputs_checked'] == len(assembly['inputs']), (unit, 'PDF input census mismatch')
        for pdf_key, assembly_key in (('source_blocks', 'unique_selectors'), ('canonical_ids', 'canonical_ids'),
                ('source_exercises', 'source_exercises'), ('source_supplied_answers', 'source_supplied_answers'),
                ('authored_answers_to_source_omissions', 'authored_answers_to_source_omissions'), ('math_checks', 'math_checks')):
            assert receipt[pdf_key] == assembly['counts'][assembly_key], (unit, 'PDF/source census mismatch', pdf_key)
        xml_ids = receipt['xml_ids']
        assert isinstance(xml_ids, list) and len(xml_ids) == len(set(xml_ids)), (unit, 'duplicate PDF XML IDs')
        canonical = set(assembly['canonical_id_order'])
        assert [sid for sid in xml_ids if sid in canonical] == assembly['canonical_id_order'], (
            unit, 'PDF canonical-ID order mismatch')
        assert set(receipt['anchor_pages_zero_based']) == set(xml_ids), (unit, 'PDF destination census mismatch')
        structure = receipt['structure']
        assert structure['named_destinations'] == len(xml_ids) and type(structure['pages']) is int and structure['pages'] > 0, (
            unit, 'PDF structure census mismatch')
        assert all(type(page) is int and 0 <= page < structure['pages']
                   for page in receipt['anchor_pages_zero_based'].values()), (unit, 'PDF destination page out of range')
        assets = receipt['assets']
        paths = [asset['path'] for asset in assets]
        assert len(paths) == len(set(paths)) and set(paths) == set(assembly['assets']), (unit, 'PDF asset census mismatch')
        for asset in assets:
            pin(asset['path'], asset['sha256'], asset['bytes'])
        assert receipt['fonts'], (unit, 'no embedded-font evidence')
        for font in receipt['fonts']:
            assert re.fullmatch(r'[0-9a-f]{64}', font['sha256'])
        review_state(unit, 'pdf', artifact_path, receipt['pdf_sha256'])
        pdf_units.add(unit)
        built_artifacts.add(artifact_path)

    assert html_ready <= html_units and pdf_ready <= pdf_units, 'ready artifact lacks build receipt'
    indexed_artifacts = {path for path in language_paths if path.startswith('output/')
                         and PurePosixPath(path).suffix.lower() in {'.html', '.pdf'}}
    assert indexed_artifacts == built_artifacts, (
        'output/build-receipt census mismatch', indexed_artifacts ^ built_artifacts)
    if states:
        declared = {(unit, format_) for unit, formats in states.items() for format_ in formats}
        assert declared == seen_states, ('review/build artifact mismatch', declared ^ seen_states)
    for path, expected in items.items():
        raw = read(path)
        actual = hashlib.sha256(raw).hexdigest()
        assert actual == expected, (path, actual, expected)
        assert path not in sizes or len(raw) == sizes[path], (path, 'byte count drift')
    return {'hashes': len(items), 'html_built': len(html_units), 'pdf_built': len(pdf_units), 'assembled_sources': len(assemblies),
            'html_ready': len(html_ready), 'pdf_ready': len(pdf_ready), 'staged_paths': len(staged)}


def verify():
    # Read receipts, locks AND readiness from the index, never unstaged versions.
    all_paths = set(git('ls-files', '-z').decode('utf-8').split('\0'))
    staged = [p for p in git('diff', '--cached', '--name-only', '-z').decode('utf-8').split('\0') if p]
    result = verify_index(indexed, all_paths, staged)
    print('PASS: indexed artifact verification '+json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    verify()
