"""Small in-memory index fixtures; no real Git mutation or artifact rendering."""
import hashlib
import json
import unittest

from verify_staged import verify_index


UNIT = 'MR-BRIDGE-002'
MODULE = 'A20-m81373'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class IndexFixture:
    def __init__(self):
        self.files = {
            'translations/MR-BRIDGE-001.xml': b'<article>legacy</article>',
            'output/MR-BRIDGE-001.html': b'legacy html',
            'qa/review.md': b'Historical legacy review; not a new render.',
            f'translations/{UNIT}.xml': b'<article>unit source</article>',
            f'units/{UNIT}.json': b'{}',
            f'output/{UNIT}.html': b'unit html',
            'tools/reader.css': b'body { color: black; }',
            'provenance/witness.xml': b'original\r\nsource\r\n',
            f'qa/{UNIT}-review.md': b'Explicit format-specific review evidence.',
            f'qa/{UNIT}-pdf-review.md': b'PDF-only page review evidence.',
        }
        self.put('sources.lock.json', {'witnesses': [self.pin('provenance/witness.xml')]})
        self.put('qa/build-receipt.json', {
            'unit': 'MR-BRIDGE-001', 'result': 'PASS',
            'source_sha256': sha(self.files['translations/MR-BRIDGE-001.xml']),
            'html_sha256': sha(self.files['output/MR-BRIDGE-001.html'])})
        self.put('qa/browser-receipt.json', {'result': 'PASS'})
        self.put(f'provenance/{UNIT}.lock.json', {
            'unit': UNIT, 'locale': 'mr-Deva-IN',
            'witnesses': [self.pin('sources.lock.json'), self.pin('provenance/witness.xml')]})
        self.put(f'qa/{UNIT}-build-receipt.json', {
            'unit': UNIT, 'locale': 'mr-Deva-IN', 'result': 'PASS',
            'source_sha256': sha(self.files[f'translations/{UNIT}.xml']),
            'config_sha256': sha(self.files[f'units/{UNIT}.json']),
            'provenance_lock_sha256': sha(self.files[f'provenance/{UNIT}.lock.json']),
            'html_sha256': sha(self.files[f'output/{UNIT}.html']),
            'html_bytes': len(self.files[f'output/{UNIT}.html']),
            'stylesheet_files': [self.pin('tools/reader.css')], 'embedded_assets': []})
        self.put(f'qa/{UNIT}-browser-receipt.json', {
            'result': 'PASS', 'htmlSha256': sha(self.files[f'output/{UNIT}.html'])})
        self.put('STATUS.json', {'ready_review_drafts': ['MR-BRIDGE-001', UNIT]})

    def put(self, path, value):
        self.files[path] = json.dumps(value).encode('utf-8')

    def get(self, path):
        return json.loads(self.files[path])

    def pin(self, path):
        raw = self.files[path]
        return {'path': path, 'sha256': sha(raw), 'bytes': len(raw)}

    def state(self, state='unreviewed', pdf=None):
        html_ready = ['MR-BRIDGE-001'] + ([UNIT] if state == 'ready_review_draft' else [])
        pdf_ready = [UNIT] if pdf == 'ready_review_draft' else []
        states = {
            'MR-BRIDGE-001': {'html': {'state': 'ready_review_draft',
                                     'reason': 'Historical reviewed HTML', 'evidence': ['qa/review.md']}},
            UNIT: {'html': {'state': state, 'reason': 'Explicit HTML review status',
                            'evidence': [f'qa/{UNIT}-review.md']}}
        }
        if pdf:
            states[UNIT]['pdf'] = {'state': pdf, 'reason': 'Separate PDF page review',
                                   'evidence': [f'qa/{UNIT}-pdf-review.md']}
        for unit, formats in states.items():
            for format_, entry in formats.items():
                if entry['state'] != 'ready_review_draft':
                    continue
                artifact = f'output/{unit}.html' if format_ == 'html' else f'output/pdf/{unit}.pdf'
                artifact_hash = sha(self.files.get(artifact, b'not built'))
                review_path = f'qa/{unit}-{format_}-review-receipt.json'
                entry.update(reviewed_artifact_sha256=artifact_hash, review_receipt=review_path)
                self.put(review_path, {'schema': 1, 'unit': unit, 'format': format_, 'result': 'PASS',
                                      'artifact_path': artifact, 'artifact_sha256': artifact_hash,
                                      'evidence': [self.pin(path) for path in entry['evidence']]})
        self.put('STATUS.json', {
            'ready_review_drafts': sorted(set(html_ready + pdf_ready)),
            'ready_html_review_drafts': html_ready, 'ready_pdf_review_drafts': pdf_ready,
            'artifact_review_states': states})

    def add_pdf(self):
        self.files.update({f'output/pdf/{UNIT}.pdf': b'%PDF-1.7\r\nfixture only\xff\x00',
                           'tools/build_pdf.py': b'pdf builder', 'tools/build_unit.py': b'pin validator'})
        html = self.get(f'qa/{UNIT}-build-receipt.json')
        self.put(f'qa/{UNIT}-pdf-build-receipt.json', {
            'unit': UNIT, 'result': 'PASS', 'source_sha256': html['source_sha256'],
            'config_sha256': html['config_sha256'], 'lock_sha256': html['provenance_lock_sha256'],
            'pdf_sha256': sha(self.files[f'output/pdf/{UNIT}.pdf']),
            'pdf_bytes': len(self.files[f'output/pdf/{UNIT}.pdf']),
            'builder_sha256': sha(self.files['tools/build_pdf.py']),
            'pin_validator_sha256': sha(self.files['tools/build_unit.py']),
            'attached_xml_sha256': html['source_sha256'], 'assets': [],
            'fonts': [{'sha256': sha(b'host font file, not a Git input')}],
            'visual_review': 'Not inferred from structural PASS'})

    def add_assembly(self):
        self.state('known_issue')
        self.files.update({
            f'translations/{MODULE}.xml': b'<article id="A20-m81373"><p id="s1"><span id="s2">1+1=2</span></p></article>',
            f'provenance/{MODULE}-assembly/en-m81373.cnxml': b'<source id="s1"><math id="s2">1+1=2</math></source>\r\n',
            f'provenance/{MODULE}-assembly/id-m81373.cnxml': b'<source id="s1"><math id="s2">1+1=2</math></source>\n',
            'tools/assemble_m81373.py': b'bounded assembly builder',
            'assets/module-fixture.jpg': b'original image fixture\xff\x00',
            f'qa/{MODULE}-primary-source-review.md': b'Separate primary source integration report.',
            f'qa/{MODULE}-pdf-primary-review.md': b'Separate full PDF page review report.',
        })
        input_paths = ['sources.lock.json', 'tools/assemble_m81373.py', 'assets/module-fixture.jpg',
                       f'provenance/{MODULE}-assembly/en-m81373.cnxml', f'provenance/{MODULE}-assembly/id-m81373.cnxml']
        inputs = {p: {'sha256': sha(self.files[p]), 'bytes': len(self.files[p])} for p in input_paths}
        asset = {'sha256': sha(self.files['assets/module-fixture.jpg']),
                 'bytes': len(self.files['assets/module-fixture.jpg']), 'mime': 'image/jpeg'}
        self.put(f'qa/{MODULE}-assembly-receipt.json', {
            'schema': 1, 'module': 'A20:m81373', 'status': 'assembled_translation_draft',
            'reader_accepted': False, 'output': self.pin(f'translations/{MODULE}.xml'),
            'inputs': inputs,
            'source_members': {locale: self.pin(f'provenance/{MODULE}-assembly/{locale}-m81373.cnxml') for locale in ('en', 'id')},
            'counts': {'canonical_ids': 2, 'unique_selectors': 1, 'source_exercises': 1,
                       'source_supplied_answers': 1, 'authored_answers_to_source_omissions': 0,
                       'canonical_assets': 1, 'math_checks': 1},
            'canonical_id_order': ['s1', 's2'],
            'selection_order': [{'locator': 'A20:m81373#s1', 'unit': UNIT}],
            'expected_math': {'check1': '1+1=2'}, 'assets': {'assets/module-fixture.jpg': asset}})

    def add_module_pdf(self, ready=False):
        self.add_assembly()
        self.files.update({f'output/pdf/{MODULE}.pdf': b'%PDF-1.7\nmodule fixture only\xff\x00',
                           'tools/build_m81373_pdf.py': b'module PDF builder'})
        self.files.setdefault('tools/build_pdf.py', b'pdf builder')
        self.files.setdefault('tools/build_unit.py', b'pin validator')
        assembly = self.get(f'qa/{MODULE}-assembly-receipt.json')
        self.put(f'qa/{MODULE}-pdf-build-receipt.json', {
            'schema': 1, 'unit': MODULE, 'locale': 'mr-Deva-IN', 'result': 'PASS',
            'source_sha256': assembly['output']['sha256'], 'attached_xml_sha256': assembly['output']['sha256'],
            'assembly_receipt_sha256': sha(self.files[f'qa/{MODULE}-assembly-receipt.json']),
            'assembly_builder_sha256': sha(self.files['tools/assemble_m81373.py']),
            'builder_sha256': sha(self.files['tools/build_m81373_pdf.py']),
            'immutable_pdf_helper_sha256': sha(self.files['tools/build_pdf.py']),
            'pin_validator_sha256': sha(self.files['tools/build_unit.py']),
            'pdf_sha256': sha(self.files[f'output/pdf/{MODULE}.pdf']), 'pdf_bytes': len(self.files[f'output/pdf/{MODULE}.pdf']),
            'input_pins': assembly['inputs'], 'pinned_inputs_checked': len(assembly['inputs']),
            'source_blocks': 1, 'canonical_ids': 2, 'source_exercises': 1, 'source_supplied_answers': 1,
            'authored_answers_to_source_omissions': 0, 'math_checks': 1,
            'xml_ids': [MODULE, 's1', 's2'], 'anchor_pages_zero_based': {MODULE: 0, 's1': 0, 's2': 1},
            'structure': {'named_destinations': 3, 'pages': 2},
            'assets': [{'path': p, **a} for p, a in assembly['assets'].items()],
            'fonts': [{'sha256': sha(b'host font file, not a Git input')}]})
        status = self.get('STATUS.json')
        evidence = [f'qa/{MODULE}-primary-source-review.md', f'qa/{MODULE}-pdf-primary-review.md']
        entry = {'state': 'ready_review_draft' if ready else 'unreviewed',
                 'reason': 'PDF-only module review, not bridge HTML readiness.', 'evidence': evidence}
        if ready:
            artifact = f'output/pdf/{MODULE}.pdf'
            review = f'qa/{MODULE}-pdf-review-receipt.json'
            digest = sha(self.files[artifact])
            entry.update(reviewed_artifact_sha256=digest, review_receipt=review)
            self.put(review, {'schema': 1, 'unit': MODULE, 'format': 'pdf', 'result': 'PASS',
                              'artifact_path': artifact, 'artifact_sha256': digest,
                              'evidence': [self.pin(p) for p in evidence]})
            status['ready_review_drafts'].append(MODULE)
            status['ready_pdf_review_drafts'].append(MODULE)
        status['artifact_review_states'][MODULE] = {'pdf': entry}
        self.put('STATUS.json', status)

    def verify(self, staged=None):
        paths = {'mr-Deva-IN/'+p for p in self.files}
        return verify_index(self.files.__getitem__, paths,
                            ['mr-Deva-IN/STATUS.json'] if staged is None else staged)


class IndexVerificationTests(unittest.TestCase):
    def setUp(self):
        self.f = IndexFixture()

    def test_historical_ready_checkpoint_remains_supported(self):
        result = self.f.verify()
        self.assertEqual((result['html_built'], result['html_ready'], result['pdf_built']), (2, 2, 0))

    def test_ready_html_requires_matching_browser_hash(self):
        self.f.put(f'qa/{UNIT}-browser-receipt.json', {'result': 'PASS', 'htmlSha256': '0'*64})
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_ready_html_requires_actual_browser_receipt(self):
        del self.f.files[f'qa/{UNIT}-browser-receipt.json']
        with self.assertRaises(KeyError):
            self.f.verify()

    def test_unreviewed_html_is_explicitly_not_ready(self):
        self.f.state()
        del self.f.files[f'qa/{UNIT}-browser-receipt.json']
        self.assertEqual(self.f.verify()['html_ready'], 1)

    def test_new_pending_artifact_requires_explicit_state(self):
        self.f.put('STATUS.json', {'ready_review_drafts': ['MR-BRIDGE-001']})
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_legacy_compatibility_cannot_bypass_new_unit_review(self):
        for path in list(self.f.files):
            if UNIT in path:
                raw = self.f.files.pop(path)
                self.f.files[path.replace(UNIT, 'MR-BRIDGE-006')] = raw.replace(UNIT.encode(), b'MR-BRIDGE-006')
        status = self.f.get('STATUS.json')
        status['ready_review_drafts'] = ['MR-BRIDGE-001', 'MR-BRIDGE-006']
        self.f.put('STATUS.json', status)
        # Repair the lock pin changed by renaming its unit; no other input drift.
        path = 'qa/MR-BRIDGE-006-build-receipt.json'
        receipt = self.f.get(path)
        receipt['provenance_lock_sha256'] = sha(self.f.files['provenance/MR-BRIDGE-006.lock.json'])
        self.f.put(path, receipt)
        with self.assertRaisesRegex(AssertionError, 'missing review state'):
            self.f.verify()

    def test_stale_browser_receipt_requires_recheck_state(self):
        self.f.put(f'qa/{UNIT}-browser-receipt.json', {'result': 'PASS', 'htmlSha256': '0'*64})
        self.f.state('unreviewed')
        with self.assertRaises(AssertionError):
            self.f.verify()
        self.f.state('recheck_required')
        self.assertEqual(self.f.verify()['html_ready'], 1)

    def test_automated_pass_cannot_clear_known_html_issue(self):
        self.f.state('known_issue')
        self.assertEqual(self.f.verify()['html_ready'], 1)
        status = self.f.get('STATUS.json')
        status['ready_html_review_drafts'].append(UNIT)
        status['ready_review_drafts'].append(UNIT)
        self.f.put('STATUS.json', status)
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_pdf_readiness_is_independent_of_html_issue(self):
        self.f.add_pdf()
        self.f.state('known_issue', 'ready_review_draft')
        result = self.f.verify()
        self.assertEqual((result['html_ready'], result['pdf_ready']), (1, 1))

    def test_pdf_structural_pass_is_not_visual_readiness(self):
        self.f.add_pdf()
        self.f.state('known_issue', 'unreviewed')
        self.assertEqual(self.f.verify()['pdf_ready'], 0)

    def test_pdf_readiness_requires_pdf_build(self):
        self.f.state('known_issue', 'ready_review_draft')
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_pdf_binary_drift_is_rejected(self):
        self.f.add_pdf()
        self.f.state('unreviewed', 'unreviewed')
        self.f.files[f'output/pdf/{UNIT}.pdf'] += b'changed'
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_pdf_and_html_cannot_pin_different_translation_bytes(self):
        self.f.add_pdf()
        self.f.state('unreviewed', 'unreviewed')
        path = f'qa/{UNIT}-pdf-build-receipt.json'
        receipt = self.f.get(path)
        receipt['source_sha256'] = receipt['attached_xml_sha256'] = '0'*64
        self.f.put(path, receipt)
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_pdf_builder_and_validator_are_pinned(self):
        self.f.add_pdf()
        self.f.state('unreviewed', 'unreviewed')
        self.f.files['tools/build_pdf.py'] += b'changed'
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_orphan_html_and_pdf_outputs_are_rejected(self):
        for path in ('output/MR-BRIDGE-099.html', 'output/pdf/MR-BRIDGE-099.pdf', 'output/untracked-reader.HTML'):
            with self.subTest(path=path):
                self.f.files[path] = b'orphan output'
                with self.assertRaisesRegex(AssertionError, 'census mismatch'):
                    self.f.verify()
                del self.f.files[path]

    def test_rebuilt_pdf_cannot_inherit_stale_manual_review(self):
        self.f.add_pdf()
        self.f.state('known_issue', 'ready_review_draft')
        path = f'output/pdf/{UNIT}.pdf'
        self.f.files[path] += b'new layout'
        receipt_path = f'qa/{UNIT}-pdf-build-receipt.json'
        receipt = self.f.get(receipt_path)
        receipt.update(pdf_sha256=sha(self.f.files[path]), pdf_bytes=len(self.f.files[path]))
        self.f.put(receipt_path, receipt)
        with self.assertRaisesRegex(AssertionError, 'reviewed-artifact hash'):
            self.f.verify()
        status = self.f.get('STATUS.json')
        status['artifact_review_states'][UNIT]['pdf']['reviewed_artifact_sha256'] = receipt['pdf_sha256']
        self.f.put('STATUS.json', status)
        with self.assertRaisesRegex(AssertionError, 'another artifact'):
            self.f.verify()

    def test_review_receipt_cannot_cross_format_boundary(self):
        self.f.add_pdf()
        self.f.state('ready_review_draft', 'ready_review_draft')
        status = self.f.get('STATUS.json')
        status['artifact_review_states'][UNIT]['html']['review_receipt'] = f'qa/{UNIT}-pdf-review-receipt.json'
        self.f.put('STATUS.json', status)
        with self.assertRaisesRegex(AssertionError, 'another unit or format'):
            self.f.verify()

    def test_review_report_bytes_and_declared_evidence_are_bound(self):
        self.f.state('ready_review_draft')
        path = f'qa/{UNIT}-review.md'
        self.f.files[path] = b'Different nonempty report'
        with self.assertRaises(AssertionError):
            self.f.verify()
        self.f.state('ready_review_draft')
        status = self.f.get('STATUS.json')
        status['artifact_review_states'][UNIT]['html']['evidence'] = [f'qa/{UNIT}-pdf-review.md']
        self.f.put('STATUS.json', status)
        with self.assertRaisesRegex(AssertionError, 'not declared in state'):
            self.f.verify()

    def test_ready_state_requires_separate_manual_review_receipt(self):
        self.f.state('ready_review_draft')
        status = self.f.get('STATUS.json')
        del status['artifact_review_states'][UNIT]['html']['review_receipt']
        self.f.put('STATUS.json', status)
        with self.assertRaisesRegex(AssertionError, 'format-specific review receipt'):
            self.f.verify()

    def test_declared_review_evidence_cannot_be_empty(self):
        self.f.state('recheck_required')
        self.f.files[f'qa/{UNIT}-review.md'] = b''
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_witness_byte_count_is_checked(self):
        path = f'provenance/{UNIT}.lock.json'
        lock = self.f.get(path)
        lock['witnesses'][1]['bytes'] += 1
        self.f.put(path, lock)
        receipt = self.f.get(f'qa/{UNIT}-build-receipt.json')
        receipt['provenance_lock_sha256'] = sha(self.f.files[path])
        self.f.put(f'qa/{UNIT}-build-receipt.json', receipt)
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_original_source_newlines_are_not_normalized(self):
        self.f.files['provenance/witness.xml'] = b'original\nsource\n'
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_extra_declared_artifact_state_is_rejected(self):
        self.f.state()
        status = self.f.get('STATUS.json')
        status['artifact_review_states']['MR-BRIDGE-099'] = {'html': {'state': 'unreviewed'}}
        self.f.put('STATUS.json', status)
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_unrelated_staging_and_duplicate_ready_entries_are_rejected(self):
        with self.assertRaises(AssertionError):
            self.f.verify(['PROJECT_DISPATCH.md'])
        self.f.put('STATUS.json', {'ready_review_drafts': ['MR-BRIDGE-001', UNIT, UNIT]})
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_assembled_source_can_be_staged_before_its_pdf(self):
        self.f.add_assembly()
        result = self.f.verify()
        self.assertEqual((result['assembled_sources'], result['pdf_built'], result['html_ready']), (1, 0, 1))

    def test_registered_module_pdf_does_not_promote_underlying_html(self):
        self.f.add_module_pdf(ready=True)
        result = self.f.verify()
        self.assertEqual((result['assembled_sources'], result['pdf_built'], result['pdf_ready'], result['html_ready']), (1, 1, 1, 1))

    def test_module_structural_pass_is_not_reader_acceptance(self):
        self.f.add_module_pdf()
        self.assertEqual(self.f.verify()['pdf_ready'], 0)

    def test_incomplete_assembly_source_or_receipt_is_rejected(self):
        for missing in (f'translations/{MODULE}.xml', f'qa/{MODULE}-assembly-receipt.json'):
            with self.subTest(missing=missing):
                self.f = IndexFixture()
                self.f.add_assembly()
                del self.f.files[missing]
                with self.assertRaisesRegex(AssertionError, 'incomplete source assembly'):
                    self.f.verify()

    def test_module_pdf_requires_source_assembly_not_only_claimed_pass(self):
        self.f.add_module_pdf()
        del self.f.files[f'translations/{MODULE}.xml']
        del self.f.files[f'qa/{MODULE}-assembly-receipt.json']
        with self.assertRaisesRegex(AssertionError, 'lacks source assembly'):
            self.f.verify()

    def test_assembly_wrong_identity_and_source_path_are_rejected(self):
        for key, value in (('module', 'A20:m81374'), ('output', {'path': 'translations/other.xml'})):
            with self.subTest(key=key):
                self.f = IndexFixture()
                self.f.add_assembly()
                path = f'qa/{MODULE}-assembly-receipt.json'
                receipt = self.f.get(path)
                receipt[key] = value
                self.f.put(path, receipt)
                with self.assertRaises(AssertionError):
                    self.f.verify()

    def test_assembly_and_pdf_every_material_input_is_byte_pinned(self):
        for path in (f'translations/{MODULE}.xml', f'provenance/{MODULE}-assembly/en-m81373.cnxml',
                     f'provenance/{MODULE}-assembly/id-m81373.cnxml', 'assets/module-fixture.jpg',
                     'tools/assemble_m81373.py', 'tools/build_m81373_pdf.py', 'tools/build_pdf.py',
                     'tools/build_unit.py', f'output/pdf/{MODULE}.pdf'):
            with self.subTest(path=path):
                self.f = IndexFixture()
                self.f.add_module_pdf()
                self.f.files[path] += b'drift'
                with self.assertRaises(AssertionError):
                    self.f.verify()

    def test_assembly_cannot_omit_raw_source_asset_or_builder_input(self):
        for omitted in (f'provenance/{MODULE}-assembly/en-m81373.cnxml', 'assets/module-fixture.jpg', 'tools/assemble_m81373.py'):
            with self.subTest(omitted=omitted):
                self.f = IndexFixture()
                self.f.add_assembly()
                path = f'qa/{MODULE}-assembly-receipt.json'
                assembly = self.f.get(path)
                del assembly['inputs'][omitted]
                self.f.put(path, assembly)
                with self.assertRaises(AssertionError):
                    self.f.verify()

    def test_module_pdf_cannot_drop_or_replace_assembly_manifest(self):
        self.f.add_module_pdf()
        path = f'qa/{MODULE}-pdf-build-receipt.json'
        receipt = self.f.get(path)
        receipt['input_pins'].pop('assets/module-fixture.jpg')
        self.f.put(path, receipt)
        with self.assertRaisesRegex(AssertionError, 'input manifests differ'):
            self.f.verify()

    def test_module_pdf_pins_assembly_receipt_even_after_matching_manifest_change(self):
        self.f.add_module_pdf()
        path = f'qa/{MODULE}-assembly-receipt.json'
        receipt = self.f.get(path)
        receipt['new_note'] = 'Changed assembly receipt, even with the same input pins.'
        self.f.put(path, receipt)
        with self.assertRaises(AssertionError):
            self.f.verify()

    def test_module_pdf_source_and_attachment_must_match_assembly(self):
        for key in ('source_sha256', 'attached_xml_sha256'):
            with self.subTest(key=key):
                self.f = IndexFixture()
                self.f.add_module_pdf()
                path = f'qa/{MODULE}-pdf-build-receipt.json'
                receipt = self.f.get(path)
                receipt[key] = '0'*64
                self.f.put(path, receipt)
                with self.assertRaises(AssertionError):
                    self.f.verify()

    def test_module_pdf_counts_ids_pages_and_assets_are_cross_checked(self):
        changes = [('source_blocks', 2), ('canonical_ids', 3), ('pinned_inputs_checked', 99),
                   ('xml_ids', [MODULE, 's2', 's1']), ('xml_ids', [MODULE, 's1', 's2', 's2']),
                   ('anchor_pages_zero_based', {MODULE: 0, 's1': 0, 's2': 2}),
                   ('anchor_pages_zero_based', {MODULE: 0, 's1': 0}), ('assets', [])]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                self.f = IndexFixture()
                self.f.add_module_pdf()
                path = f'qa/{MODULE}-pdf-build-receipt.json'
                receipt = self.f.get(path)
                receipt[key] = value
                self.f.put(path, receipt)
                with self.assertRaises(AssertionError):
                    self.f.verify()

    def test_rebuilt_module_pdf_cannot_inherit_manual_review(self):
        self.f.add_module_pdf(ready=True)
        path = f'output/pdf/{MODULE}.pdf'
        self.f.files[path] += b'new layout'
        receipt_path = f'qa/{MODULE}-pdf-build-receipt.json'
        receipt = self.f.get(receipt_path)
        receipt.update(pdf_sha256=sha(self.f.files[path]), pdf_bytes=len(self.f.files[path]))
        self.f.put(receipt_path, receipt)
        with self.assertRaisesRegex(AssertionError, 'reviewed-artifact hash'):
            self.f.verify()

    def test_module_review_binds_source_and_pdf_reports(self):
        for evidence in ('primary-source', 'pdf-primary'):
            with self.subTest(evidence=evidence):
                self.f = IndexFixture()
                self.f.add_module_pdf(ready=True)
                self.f.files[f'qa/{MODULE}-{evidence}-review.md'] += b'changed'
                with self.assertRaises(AssertionError):
                    self.f.verify()

    def test_all_declared_manual_evidence_requires_a_distinct_pin(self):
        self.f.add_module_pdf(ready=True)
        path = f'qa/{MODULE}-pdf-review-receipt.json'
        receipt = self.f.get(path)
        receipt['evidence'].pop()
        self.f.put(path, receipt)
        with self.assertRaisesRegex(AssertionError, 'not all declared evidence'):
            self.f.verify()
        self.f.add_module_pdf(ready=True)
        receipt = self.f.get(path)
        receipt['evidence'].append(receipt['evidence'][0])
        self.f.put(path, receipt)
        with self.assertRaisesRegex(AssertionError, 'duplicate reviewed report pins'):
            self.f.verify()

    def test_unregistered_module_cannot_enter_ready_lists(self):
        self.f.add_module_pdf(ready=True)
        status = self.f.get('STATUS.json')
        status['ready_review_drafts'].append('A20-m99999')
        status['ready_pdf_review_drafts'].append('A20-m99999')
        self.f.put('STATUS.json', status)
        with self.assertRaises(AssertionError):
            self.f.verify()


if __name__ == '__main__':
    unittest.main(verbosity=2)
