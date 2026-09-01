"""Editorial headings never mutate an untitled source fragment."""
import unittest
import xml.etree.ElementTree as ET
from build_unit import reader_title, CN


class ReaderTitleTests(unittest.TestCase):
    def test_existing_title_is_unchanged(self):
        node = ET.fromstring(f'<section xmlns="{CN[1:-1]}"><title>ముఖ్య భావనలు</title></section>')
        self.assertEqual(reader_title(node, {}), ("ముఖ్య భావనలు", ""))

    def test_editorial_title_does_not_add_source_node(self):
        node = ET.fromstring(f'<section xmlns="{CN[1:-1]}" id="untitled"/>')
        before = ET.tostring(node)
        title, note = reader_title(node, {"editorial_title_te": "అభ్యాసాలు", "editorial_title_en": "Practice <review>"})
        self.assertEqual(title, "అభ్యాసాలు")
        self.assertIn("Editorial navigation title", note)
        self.assertIn("&lt;review&gt;", note)
        self.assertEqual(ET.tostring(node), before)

    def test_missing_editorial_title_fails(self):
        node = ET.fromstring(f'<section xmlns="{CN[1:-1]}"/>')
        for catalog in [{}, {"editorial_title_te": "అభ్యాసాలు"}]:
            with self.assertRaises(AssertionError):
                reader_title(node, catalog)


if __name__ == "__main__":
    unittest.main()
