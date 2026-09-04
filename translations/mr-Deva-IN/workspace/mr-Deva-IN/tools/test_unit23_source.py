"""Independent MR023 real-source regression; not rendered-reader acceptance.

Reads the frozen Marathi XML/config/lock, complete pinned EN/ID introduction
modules, collection manifests, selected fragments, and original photo bytes.
The bilingual/photo judgments are documented in the companion review; these
tests bind those judgments to the exact evidence and reject structural drift.
"""

import hashlib
import json
import re
import unicodedata
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as E


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent
UNIT = "MR-BRIDGE-023"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
COL = "{http://cnx.rice.edu/collxml}"

PINS = {
    "translations/MR-BRIDGE-023.xml": (
        11516,
        "5e5f719f00e2801e05c8ce61994317e408aa2636b6843df7baa3cda01a9765f2",
    ),
    "units/MR-BRIDGE-023.json": (
        818,
        "7800c1a8112f5502fa12ec0f05d795503c39aa378491890f8e72b54de914519c",
    ),
    "provenance/MR-BRIDGE-023.lock.json": (
        9054,
        "8218ce977588df4e7d1be8e9dae44cff939ba8a9264c57138a06292630655268",
    ),
}

ARCHIVES = {
    "en": (
        "A20-canonical.zip",
        "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
        "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
    ),
    "id": (
        "A20-v0.3.0-source.zip",
        "source",
        "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
    ),
}
MODULE_PINS = {
    "en": (1568, "5577a5087c332c7c6eb5ee185dee43b98e8a754687985410be8b84e4173d53e9"),
    "id": (1610, "e1204520eb35f8ade93655696d814c560deded28c18c5d7cfb525b38ffc2df23"),
}
COLLECTIONS = {
    "en": (
        "collections/intermediate-algebra-2e.collection.xml",
        5642,
        "993990c353220be879928579c1393ced90c8b54764b4ba1182ba660b54e8ce32",
        "Intermediate Algebra 2e",
        "en",
        83,
        12,
        "Systems of Linear Equations",
    ),
    "id": (
        "collections/intermediate-algebra-2e-checkpoint-0030.collection.xml",
        3609,
        "00d67af8787dd882c59c000f98fc0ac0e7b4f01c2820c108ac0da1a8ccbee744",
        "Aljabar Menengah 2e",
        "id-ID",
        48,
        7,
        "Sistem Persamaan Linear",
    ),
}
NEXT_PINS = {
    "en": (166406, "2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5"),
    "id": (168909, "2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112"),
}
PHOTO = "CNX_IntAlg_Figure_04_00_001_img_new.jpg"
PHOTO_PIN = (234623, "84fedc14aabb13814f355c3538424283512ad0bc918adc51becfc672c9f1d3ce")
OCR_PINS = {
    "balbharati8-85.txt": (2474, "f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b"),
    "balbharati8-86.txt": (1539, "497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57"),
}
SOURCE_IDS = [
    "CNX_IntAlg_Figure_04_00_001",
    "fs-id1167829746522",
    "fs-id1167836596342",
]
CHAPTER_MODULES = ["m81375", "m81427", "m81380", "m81381", "m81428", "m81429", "m81431", "m81432"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key")
        out[key] = value
    return out


def inside(base, relative):
    path = (base / relative).resolve()
    if base.resolve() not in path.parents:
        raise ValueError("path escape")
    return path


def node_text(node):
    return "".join(node.itertext())


def id_map(root):
    return {node.get("id"): node for node in root.iter() if node.get("id")}


def parent_map(root):
    return {child: parent for parent in root.iter() for child in parent}


def nearest_source_parent(node, parents, allowed):
    while node in parents:
        node = parents[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node):
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        node.text,
        tuple((shape(child), child.tail) for child in node),
    )


def jpeg_size(data):
    if not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("not JPEG")
    i = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while i < len(data):
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(data):
            break
        length = int.from_bytes(data[i : i + 2], "big")
        if length < 2 or i + length > len(data):
            raise ValueError("bad JPEG segment")
        if marker in sof:
            if length < 7:
                raise ValueError("short JPEG SOF")
            height = int.from_bytes(data[i + 3 : i + 5], "big")
            width = int.from_bytes(data[i + 5 : i + 7], "big")
            return width, height
        i += length
    raise ValueError("JPEG dimensions missing")


class Unit23Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = E.fromstring(cls.raw)
        cls.target = id_map(cls.root)
        cls.target_parents = parent_map(cls.root)
        cls.config = json.loads(
            (BASE / f"units/{UNIT}.json").read_text(encoding="utf-8"),
            object_pairs_hook=unique,
        )
        cls.lock = json.loads(
            (BASE / f"provenance/{UNIT}.lock.json").read_text(encoding="utf-8"),
            object_pairs_hook=unique,
        )
        cls.modules = {}
        cls.source_roots = {}
        cls.source = {}
        cls.collections = {}
        cls.next_modules = {}
        cls.photos = {}
        for locale, (archive_name, prefix, _) in ARCHIVES.items():
            archive = WORKSPACE / "downloads/mr-Deva-IN/releases" / archive_name
            with zipfile.ZipFile(archive) as zf:
                module = zf.read(f"{prefix}/modules/m81375/index.cnxml")
                collection_name = COLLECTIONS[locale][0]
                collection = zf.read(f"{prefix}/{collection_name}")
                next_module = zf.read(f"{prefix}/modules/m81427/index.cnxml")
                photo = zf.read(f"{prefix}/media/{PHOTO}")
            cls.modules[locale] = module
            cls.source_roots[locale] = E.fromstring(module)
            cls.source[locale] = id_map(cls.source_roots[locale])
            cls.collections[locale] = collection
            cls.next_modules[locale] = next_module
            cls.photos[locale] = photo

    def test_01_frozen_input_pins(self):
        for relative, expected in PINS.items():
            data = (BASE / relative).read_bytes()
            self.assertEqual((len(data), sha(data)), expected)

    def test_02_complete_bilingual_module_metadata_and_scope(self):
        expected_titles = {"en": "Introduction", "id": "Pendahuluan"}
        for locale in ARCHIVES:
            data = self.modules[locale]
            self.assertEqual((len(data), sha(data)), MODULE_PINS[locale])
            root = self.source_roots[locale]
            self.assertEqual(root.tag, C + "document")
            self.assertEqual(root.get("class"), "introduction")
            self.assertEqual(root.get("{http://www.w3.org/XML/1998/namespace}lang"), None if locale == "en" else "id-ID")
            self.assertEqual(root.findtext(C + "title"), expected_titles[locale])
            metadata = root.find(C + "metadata")
            self.assertEqual(metadata.findtext(MD + "content-id"), "m81375")
            self.assertEqual(metadata.findtext(MD + "title"), expected_titles[locale])
            self.assertEqual(metadata.findtext(MD + "uuid"), "f94eaf18-fae0-4122-9c5d-294cb1994d02")
            abstract = metadata.find(MD + "abstract")
            self.assertIsNotNone(abstract)
            self.assertEqual(node_text(abstract), "")
            self.assertFalse(any("date" in node.tag.lower() for node in metadata))
            content = root.find(C + "content")
            self.assertEqual([node.tag for node in content], [C + "figure", C + "para"])
            self.assertEqual([node.get("id") for node in root.iter() if node.get("id")], SOURCE_IDS)

    def test_03_exact_two_selectors_and_four_frozen_fragments(self):
        expected = [
            "A20:m81375#CNX_IntAlg_Figure_04_00_001",
            "A20:m81375#fs-id1167836596342",
        ]
        self.assertEqual([node.get("data-source") for node in self.root.iter() if node.get("data-source")], expected)
        self.assertEqual([entry["locator"] for entry in self.lock["source_selections"]], expected)
        count = total = 0
        for selection in self.lock["source_selections"]:
            self.assertEqual(selection["locator"], "A20:m81375#" + selection["target_id"])
            for record in selection["sources"]:
                locale = record["locale"]
                fragment = inside(BASE, record["fragment_path"]).read_bytes()
                self.assertEqual(sha(fragment), record["fragment_sha256"])
                self.assertEqual(shape(E.fromstring(fragment)), shape(self.source[locale][selection["target_id"]]))
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale][1])
                self.assertEqual(record["archive_sha256"], ARCHIVES[locale][2])
                self.assertEqual(record["math_sha256"], [])
                self.assertEqual(record["outgoing_urls"], [])
                count += 1
                total += len(fragment)
        self.assertEqual((count, total), (4, 2869))

    def test_04_all_fourteen_local_witnesses(self):
        witnesses = self.lock["witnesses"]
        self.assertEqual(len(witnesses), 14)
        self.assertEqual(len({entry["path"] for entry in witnesses}), 14)
        for entry in witnesses:
            data = inside(BASE, entry["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (entry["bytes"], entry["sha256"]), entry["path"])

    def test_05_three_source_ids_five_target_ids_and_ancestry(self):
        self.assertEqual([node.get("id") for node in self.root.iter() if node.get("id") in SOURCE_IDS], SOURCE_IDS)
        self.assertEqual(set(self.target), set(SOURCE_IDS) | {UNIT, "credits"})
        self.assertEqual(len(self.target), 5)
        allowed = set(SOURCE_IDS)
        for locale in ARCHIVES:
            source_parents = parent_map(self.source_roots[locale])
            for ident in SOURCE_IDS:
                self.assertEqual(
                    nearest_source_parent(self.source[locale][ident], source_parents, allowed),
                    nearest_source_parent(self.target[ident], self.target_parents, allowed),
                    (locale, ident),
                )
        figure = self.target["CNX_IntAlg_Figure_04_00_001"]
        self.assertEqual(figure.tag, "figure")
        self.assertEqual(figure.get("data-source-class"), "splash")
        self.assertIn(self.target["fs-id1167829746522"], list(figure))

    def test_06_original_photo_bytes_review_copies_asset_and_dimensions(self):
        self.assertEqual(len(self.lock["source_images"]), 2)
        self.assertEqual({entry["locale"] for entry in self.lock["source_images"]}, {"en", "id"})
        for record in self.lock["source_images"]:
            locale = record["locale"]
            data = self.photos[locale]
            self.assertEqual((len(data), sha(data)), PHOTO_PIN)
            self.assertEqual((record["bytes"], record["sha256"]), PHOTO_PIN)
            self.assertEqual(Path(record["member"]).name, PHOTO)
            self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
            self.assertEqual(jpeg_size(data), (975, 450))
            if locale == "en":
                self.assertEqual(inside(BASE, record["committed_asset"]).read_bytes(), data)
        self.assertEqual(self.photos["en"], self.photos["id"])
        asset = self.config["assets"][PHOTO]
        self.assertEqual(asset, {
            "path": f"assets/{UNIT}/{PHOTO}",
            "sha256": PHOTO_PIN[1],
            "mime": "image/jpeg",
        })

    def test_07_photo_alt_matches_manually_viewed_pixels(self):
        image = self.target["fs-id1167829746522"].find("img")
        self.assertIsNotNone(image)
        self.assertEqual(image.get("src"), "asset:" + PHOTO)
        alt = image.get("alt", "")
        for visible in ["नारिंगी", "Lamborghini Aventador", "पुढील दिवा", "समोरील काच", "बाजूचा आरसा", "पुढील चाक"]:
            self.assertIn(visible, alt)
        self.assertNotIn("स्वायत्त", alt)
        original_alts = {
            "en": "A close up photo of a bright orange Lamborghini Aventador.",
            "id": "Foto jarak dekat Lamborghini Aventador berwarna jingga cerah.",
        }
        for locale, expected in original_alts.items():
            self.assertEqual(self.source[locale]["fs-id1167829746522"].get("alt"), expected)

    def test_08_exact_source_caption_credit_and_no_invented_photo_url_or_license(self):
        captions = {
            "en": "In the future, car drivers may become passengers because cars will be able to drive themselves. (credit: jingoba/Pixabay)",
            "id": "Pada masa depan, pengemudi mobil mungkin menjadi penumpang karena mobil dapat mengemudi sendiri. (kredit: jingoba/Pixabay)",
        }
        for locale, expected in captions.items():
            self.assertEqual(self.source[locale]["CNX_IntAlg_Figure_04_00_001"].findtext(C + "caption"), expected)
        caption = node_text(self.target["CNX_IntAlg_Figure_04_00_001"].find("figcaption"))
        self.assertIn("भविष्यात", caption)
        self.assertIn("कारचालक प्रवासी", caption)
        self.assertIn("jingoba/Pixabay", caption)
        serialized = self.raw.decode("utf-8")
        self.assertNotIn("pixabay.com", serialized.lower())
        credits = node_text(self.target["credits"])
        self.assertIn("स्वतंत्र परवाना किंवा मूळ फोटो-पृष्ठाचा दुवा दिलेला नाही", credits)
        self.assertIn("असा तपशील येथे अंदाजाने जोडलेला नाही", credits)

    def test_09_all_source_paragraph_claims_retained_in_marathi(self):
        en = node_text(self.source["en"]["fs-id1167836596342"])
        indonesian = node_text(self.source["id"]["fs-id1167836596342"])
        mr = node_text(self.target["fs-id1167836596342"])
        for clause in [
            "Climb into your car.",
            "Put on your seatbelt.",
            "Choose your destination",
            "autonomous car",
            "No cars are fully autonomous at the moment",
            "ease traffic congestion, prevent accidents, and lower pollution",
            "computer programmers who are developing software",
            "relationships between equations",
            "solve systems of linear equations in different ways",
            "analyze real-world situations",
        ]:
            self.assertIn(clause, en)
        for clause in [
            "Masuklah ke mobil Anda.",
            "Kenakan sabuk pengaman.",
            "mobil otonom",
            "Saat ini belum ada mobil yang sepenuhnya otonom",
            "hubungan antarpersamaan",
            "berbagai cara menyelesaikan sistem persamaan linear",
        ]:
            self.assertIn(clause, indonesian)
        for clause in [
            "तुमच्या कारमध्ये बसा.",
            "सीटबेल्ट लावा.",
            "निवांत बसा.",
            "स्वायत्त कारमध्ये",
            "सध्या कोणत्याही कार पूर्णपणे स्वायत्त नाहीत",
            "सुकाणूवर असणे आवश्यक आहे",
            "वाहतूक कोंडी कमी करण्यात",
            "अपघात टाळण्यात",
            "प्रदूषण कमी करण्यात",
            "संगणक प्रोग्रामरांमुळे",
            "सॉफ्टवेअर विकसित",
            "समीकरणांमधील संबंधांसह",
            "रेषीय समीकरणांच्या प्रणाली",
            "वेगवेगळ्या पद्धतींनी",
            "वास्तव जीवनातील परिस्थितींचे विश्लेषण",
        ]:
            self.assertIn(clause, mr)

    def test_10_source_era_statement_is_attributed_not_current_fact(self):
        translation = node_text(self.target["fs-id1167836596342"])
        self.assertIn("सध्या कोणत्याही कार पूर्णपणे स्वायत्त नाहीत", translation)
        original_notes = [node_text(node) for node in self.root.findall(".//aside[@data-kind='original']")]
        self.assertEqual(len(original_notes), 2)
        joined = " ".join(original_notes)
        for phrase in [
            "मूळ स्रोताच्या काळातील मांडणी",
            "2026 मधील परिस्थितीबद्दलचा दावा नाही",
            "प्रकाशनदिनांक नाही",
            "तो अंदाजाने दिलेला नाही",
            "स्रोतकालीन विधान जतन करते",
            "वर्तमान 2026 स्थितीचे अद्ययावत विधान",
        ]:
            self.assertIn(phrase, joined)
        self.assertEqual(self.raw.decode("utf-8").count("2026"), 2)
        self.assertNotRegex(joined, r"(?:प्रकाशनदिनांक|प्रकाशनवर्ष)\s*(?:हा|हे|:)??\s*[12][0-9]{3}")
        self.assertIn("वाहन चालवण्याबाबतची सूचना म्हणून घेऊ नये", joined)
        self.assertIn("वाहनतंत्रज्ञानाच्या मराठी मानक संज्ञेची पडताळणी झाल्याचा दावा नाही", joined)

    def test_11_zero_math_exercises_questions_and_answers_accounting(self):
        for locale in ARCHIVES:
            root = self.source_roots[locale]
            for local in ["math", "exercise", "problem", "solution", "definition", "example"]:
                self.assertFalse(root.findall(f".//{{*}}{local}"), (locale, local))
        for tag in ["math", "exercise", "problem", "solution", "table"]:
            self.assertFalse(list(self.root.iter(tag)), tag)
        self.assertFalse([node for node in self.root.iter() if node.get("data-check")])
        expected_counts = {
            "source_count": 2,
            "translated_worked_examples": 0,
            "translated_definitions": 0,
            "translated_practice_items": 0,
            "translated_resource_notes": 0,
            "original_practice_items": 0,
        }
        for key, value in expected_counts.items():
            self.assertEqual(self.config[key], value)
        self.assertEqual(self.config["question_ids"], [])
        self.assertEqual(self.config["expected_math"], {})

    def test_12_both_collection_censuses_and_exact_chapter_boundary(self):
        for locale, (_, size, digest, title, language, module_count, sub_count, chapter_title) in COLLECTIONS.items():
            data = self.collections[locale]
            self.assertEqual((len(data), sha(data)), (size, digest))
            root = E.fromstring(data)
            metadata = root.find(COL + "metadata")
            self.assertEqual(metadata.findtext(MD + "title"), title)
            self.assertEqual(metadata.findtext(MD + "language"), language)
            self.assertEqual(metadata.findtext(MD + "uuid"), "4664c267-cd62-4a99-8b28-1cb9b3aee347")
            license_node = metadata.find(MD + "license")
            self.assertEqual(license_node.get("url"), "http://creativecommons.org/licenses/by-nc-sa/4.0/")
            self.assertEqual(node_text(license_node), "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International")
            modules = list(root.iter(COL + "module"))
            subcollections = list(root.iter(COL + "subcollection"))
            self.assertEqual((len(modules), len(subcollections)), (module_count, sub_count))
            documents = [node.get("document") for node in modules]
            self.assertEqual(documents[22:24], ["m81375", "m81427"])
            parents = parent_map(root)
            intro = modules[22]
            chapter = parents[parents[intro]]
            self.assertEqual(chapter.tag, COL + "subcollection")
            self.assertEqual(chapter.findtext(MD + "title"), chapter_title)
            self.assertEqual([node.get("document") for node in chapter.iter(COL + "module")], CHAPTER_MODULES)
            self.assertIn(modules[23], list(parents[modules[23]]))

    def test_13_actual_next_module_metadata_first_marker_and_exclusion(self):
        expected_titles = {
            "en": "Solve Systems of Linear Equations with Two Variables",
            "id": "Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel",
        }
        for locale in ARCHIVES:
            data = self.next_modules[locale]
            self.assertEqual((len(data), sha(data)), NEXT_PINS[locale])
            root = E.fromstring(data)
            self.assertEqual(root.findtext(C + "title"), expected_titles[locale])
            self.assertEqual(root.findtext(C + "metadata/" + MD + "content-id"), "m81427")
            self.assertEqual(root.findtext(C + "metadata/" + MD + "uuid"), "b9f8475e-9490-4f24-995f-2923b1ed9644")
            children = list(root.find(C + "content"))
            self.assertEqual(len(children), 10)
            self.assertEqual((children[0].tag, children[0].get("id")), (C + "note", "fs-id1167830925402"))
            self.assertEqual(len([node for node in root.iter() if node.get("id")]), 751)
        self.assertNotIn("fs-id1167830925402", self.target)
        self.assertFalse(any("m81427#" in (node.get("data-source") or "") for node in self.root.iter()))
        credits = node_text(self.target["credits"])
        for phrase in ["पुढील प्रत्यक्ष module m81427", "Solve Systems of Linear Equations with Two Variables", "Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel", "fs-id1167830925402", "तो येथे घेतलेला नाही"]:
            self.assertIn(phrase, credits)

    def test_14_local_links_exact_external_links_and_offline_media(self):
        hrefs = [node.get("href") for node in self.root.iter("a")]
        local = [href for href in hrefs if href.startswith("#")]
        self.assertEqual(local, ["#fs-id1167836596342", "#credits"])
        for href in local:
            self.assertIn(href[1:], self.target)
        external = [href for href in hrefs if not href.startswith("#")]
        self.assertEqual(external, [
            "https://openstax.org/books/intermediate-algebra-2e/pages/4-introduction",
            "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        ])
        self.assertFalse(any("pixabay" in href.lower() for href in hrefs))
        for image in self.root.iter("img"):
            self.assertTrue(image.get("src", "").startswith("asset:"))
            self.assertFalse(re.match(r"(?:https?:|data:)", image.get("src", ""), flags=re.I))
        for tag in ["script", "iframe", "object", "embed", "svg", "audio", "video", "source"]:
            self.assertFalse(list(self.root.iter(tag)))

    def test_15_freshly_read_c12_c13_witnesses_have_only_narrow_effects(self):
        texts = {}
        for name, expected in OCR_PINS.items():
            data = (WORKSPACE / "downloads/mr-Deva-IN/canon/ocr" / name).read_bytes()
            self.assertEqual((len(data), sha(data)), expected)
            texts[name] = data.decode("utf-8")
        c12 = texts["balbharati8-85.txt"]
        for phrase in ["समीकरणाची उकल", "समीकरण सोडवणे म्हणजे त्याची उकल शोधणे", "दोन्ही बाजूंवर समान क्रिया", "शून्येतर समान संख्येने भागणे"]:
            self.assertIn(phrase, c12)
        c13 = texts["balbharati8-86.txt"]
        for phrase in ["पुढील समीकरणे सोडवा", "दोन्ही बाजूंतून", "दोन्ही बाजूंना"]:
            self.assertIn(phrase, c13)
        paragraph = node_text(self.target["fs-id1167836596342"])
        self.assertIn("सोडवायच्या", paragraph)
        self.assertIn("वेगवेगळ्या पद्धतींनी", paragraph)
        self.assertNotIn("आलेख", paragraph)
        notes = " ".join(node_text(node) for node in self.root.findall(".//aside[@data-kind='original']"))
        self.assertIn("कार्यपर्याय", notes)
        self.assertNotIn("मानक संज्ञा म्हणून सिद्ध", notes)

    def test_16_locale_metadata_terms_and_source_identity(self):
        self.assertEqual(self.root.attrib, {
            "id": UNIT,
            "lang": "mr-Deva-IN",
            "data-source-content-id": "m81375",
            "data-source-uuid": "f94eaf18-fae0-4122-9c5d-294cb1994d02",
            "data-source-class": "introduction",
            "data-source-title-en": "Introduction",
            "data-source-title-id": "Pendahuluan",
            "data-source-language-id": "id-ID",
            "data-source-abstract": "empty",
        })
        serialized = self.raw.decode("utf-8")
        self.assertEqual(serialized, unicodedata.normalize("NFC", serialized))
        self.assertNotIn("\ufffd", serialized)
        all_text = node_text(self.root)
        for term in self.config["required_terms"]:
            self.assertIn(term, all_text)
        credits = node_text(self.target["credits"])
        for phrase in ["m81375", "Introduction", "Pendahuluan", "f94eaf18-fae0-4122-9c5d-294cb1994d02", "abstract घटक रिकामा", "मानवी मराठी गणित-शिक्षकाचे पुनरावलोकन अद्याप आवश्यक", "संपूर्ण पाच-पुस्तकांचे काम सुरू"]:
            self.assertIn(phrase, credits)

    def test_17_helpers_reject_duplicate_keys_traversal_and_bad_jpeg(self):
        with self.assertRaises(ValueError):
            unique([("x", 1), ("x", 2)])
        for bad in ["../escape", "provenance/../../escape"]:
            with self.assertRaises(ValueError):
                inside(BASE, bad)
        for bad in [b"", b"not a jpeg", b"\xff\xd8\xff\xc0\x00\x01"]:
            with self.assertRaises(ValueError):
                jpeg_size(bad)
        self.assertNotEqual(sha(self.modules["en"]), sha(self.modules["id"]))
        self.assertEqual(sha(self.photos["en"]), sha(self.photos["id"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
