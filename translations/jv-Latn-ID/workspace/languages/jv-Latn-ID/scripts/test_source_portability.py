"""Pure metadata tests: no archive download, source rewrite or audit replay."""
import copy
import unittest
from prepare_sources import full_archive_origin


class ArchiveOrigin(unittest.TestCase):
    def setUp(self):
        self.path = 'downloads/jv-Latn-ID/openstax-full-pinned.zip'
        self.digest = 'exact-verified-test-digest'
        self.old = {'local_path': self.path, 'sha256': self.digest,
                    'acquisition': 'Historical shared hard link',
                    'shared_origin_at_acquisition': 'C:/former-PC/donor.zip'}

    def test_fresh_download_does_not_inherit_old_pc_origin(self):
        result = full_archive_origin(True, [self.old], self.path, self.digest)
        self.assertIn('Downloaded from the pinned canonical URL', result['acquisition'])
        self.assertNotIn('historical_acquisition', result)
        self.assertNotIn('shared_origin_at_acquisition', result)

    def test_reused_archive_preserves_history_without_current_topology_claim(self):
        original = copy.deepcopy(self.old)
        result = full_archive_origin(False, [self.old], self.path, self.digest)
        self.assertIn('current storage topology is not inferred', result['acquisition'])
        self.assertEqual(result['historical_acquisition']['shared_origin_at_acquisition'], 'C:/former-PC/donor.zip')
        self.assertNotIn('shared_origin_at_acquisition', result)
        self.assertEqual(self.old, original)
        replay = full_archive_origin(False, [{**self.old, **result}], self.path, self.digest)
        self.assertEqual(replay, result)

    def test_no_history_for_unknown_or_different_bytes(self):
        for previous in ([], [{**self.old, 'sha256': 'different'}], [{**self.old, 'local_path': 'elsewhere.zip'}]):
            result = full_archive_origin(False, previous, self.path, self.digest)
            self.assertEqual(list(result), ['acquisition'])

    def test_ambiguous_prior_evidence_fails(self):
        with self.assertRaises(ValueError):
            full_archive_origin(False, [self.old, self.old], self.path, self.digest)


if __name__ == '__main__':
    unittest.main()
