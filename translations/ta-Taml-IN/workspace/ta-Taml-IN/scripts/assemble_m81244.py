"""Assemble the complete checked Tamil m81244 source into a review package.

This is deliberately fail closed.  Every source fragment, witness, supporting
cross-module target file, and SVG asset is pinned by SHA-256.  The script
preserves the canonical CNXML tree and source solution omissions; it does not
create a learner companion, HTML reader, EPUB, PDF, or mastery route.

Default mode has only one persistent output, ``reader-m81244-review/``; it
uses a sibling lock and fresh staging directory transactionally.  ``--check-only``
checks candidate inputs without reading or writing the package.  ``--check``
holds the sibling lock and requires a stable existing package to equal the
current deterministic build.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


LANG = Path(__file__).resolve().parents[1]
REPO = LANG.parent
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
MD = "http://cnx.rice.edu/mdml"
SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
LOCALE = "ta-Taml-IN"

PACKAGE = LANG / "reader-m81244-review"
SOURCE_OUTPUT = PACKAGE / "source/m81244.cnxml"
LICENSE_OUTPUT = PACKAGE / "LICENSE.txt"
ATTRIBUTION_OUTPUT = PACKAGE / "ATTRIBUTION.en.cnxml"
MANIFEST_OUTPUT = PACKAGE / "manifest.json"
BUILD_LOCK = LANG / ".assemble-m81244.lock"

LICENSE_SOURCE = (LANG / "provenance/A00-LICENSE.txt",
                  "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a")
ATTRIBUTION_SOURCE = (LANG / "provenance/A00-preface-credits.en.cnxml",
                      "1c7cf6eda8be5021f1f33dc22069f5a3db50d1412a024bb57c7268b25db7f9df")
ATTRIBUTION_SECTION_ID = "eip-214"

WITNESSES = {
    "en": (LANG / "provenance/m81244.en.cnxml", "b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b"),
    "id-ID": (LANG / "provenance/m81244.id-ID.cnxml", "d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6"),
}
SUPPORTING_MODULES = {
    "m81243": (LANG / "translation/m81243.cnxml", "699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959"),
}

# Order here is canonical document order.  The four final content fragments
# are children of the titleless fs-id2263283 wrapper, not direct content peers.
FRAGMENTS = (
    ("frontmatter", LANG / "translation/m81244-frontmatter.cnxml", "c568bfc0cd596439c1097e4bdc37ce0ef8ea6d48de22c0d47a3c3fec7286552f"),
    ("fs-id2299412", LANG / "translation/m81244-fs-id2299412.cnxml", "f6a28fbc919f8fe1f6c3207c9d85cdb6f99a115cfc3dd54fa52f5eb9327a0edb"),
    ("fs-id1122444", LANG / "translation/m81244-fs-id1122444.cnxml", "178f0294d076dbc50c03f802d3d4e3fbee550d4f84c7b6f53fa6bec0b0aea12a"),
    ("fs-id2601285", LANG / "translation/m81244-fs-id2601285.cnxml", "83b547490aab15c693225a832c9d03e14f2bf1ac8d4cde105470a6e2c601b313"),
    ("fs-id2145437", LANG / "translation/m81244-fs-id2145437.cnxml", "b1cd67ced5430ef3de73f8a6483a09849ac1523180f2ff26b468d8ba64620ee1"),
    ("fs-id1385496", LANG / "translation/m81244-fs-id1385496.cnxml", "dd3d4e473f5468cff9737a01d3968f60b0dd5102fb791fff529eab43ec0ddaff"),
    ("fs-id2691382", LANG / "translation/m81244-fs-id2691382.cnxml", "1bb36df94ec4db85db15a2b07985070532955e54f4e15edb94b15c8f39839c30"),
    ("fs-id2197427", LANG / "translation/m81244-fs-id2197427.cnxml", "8e7aeb7d3d537466c4b98c902016f61ba4ff2f65b48f1c078c1d41029f8b5ceb"),
    ("fs-id1611455", LANG / "translation/m81244-fs-id1611455.cnxml", "12d98d249c3b940dc3372e5d781b0d92d012041a3a5bbf1b4d673ed102e64f99"),
    ("fs-id2150139", LANG / "translation/m81244-fs-id2150139.cnxml", "4b6e7ee11d47eca9f7318b5c7b82add16b306012cbaaf7ffa678479d5ab93f0a"),
    ("fs-id2280700", LANG / "translation/m81244-fs-id2280700.cnxml", "7d8abec4d0cc0ad191e124b94d935bf9b8d42ea283604f23f1b368f50f7df7ea"),
    ("fs-id1405751", LANG / "translation/m81244-fs-id1405751.cnxml", "e4527c03e1c98627a713afde6d6d199e97f04fe33b28afac7020fc60fc3225b2"),
    ("eip-985", LANG / "translation/m81244-eip-985.cnxml", "ba06b9c41e5913ba2e26dae36bd6cc6bc9fd862c18d7e4ad862150f3509836f4"),
    ("glossary", LANG / "translation/m81244-glossary.cnxml", "8d01abdc05c079b6f2752066bb699d7d89df015e653eb6afde4440730761e258"),
)
FRAGMENT_BY_ID = {source_id: (path, digest) for source_id, path, digest in FRAGMENTS}
EXPECTED_FRAGMENT_FILES = {path.name for _, path, _ in FRAGMENTS}
DIRECT_CONTENT_ORDER = (
    "fs-id2299412", "fs-id1122444", "fs-id2601285", "fs-id2145437",
    "fs-id1385496", "fs-id2691382", "fs-id2197427", "fs-id1611455",
    "fs-id2263283",
)
OUTER_ID = "fs-id2263283"
OUTER_CHILD_ORDER = ("fs-id2150139", "fs-id2280700", "fs-id1405751", "eip-985")
OBJECTIVE_SECTION_ORDER = (
    "fs-id2601285", "fs-id2145437", "fs-id1385496", "fs-id2691382", "fs-id2197427",
)

EXPECTED_ASSETS = {
    "assets/m81244-readiness/CNX_BMath_Figure_01_02_001_img.svg": "c1acf0580211036d4413a860de848396824b66fa4686ed739095157be7eaed49",
    "assets/u010/CNX_BMath_Figure_01_02_006_img.svg": "2d73340a20612d303babbca255eefd6b765a481c935e0f3d5ad1368bfc45a9a3",
    "assets/u010/CNX_BMath_Figure_01_02_007_img.svg": "bc52fc269efebe5a3bffb3cbe346adc7e96abc4f656fb6aecb149b6b69db59cc",
    "assets/u010/CNX_BMath_Figure_01_02_010_img.svg": "c49425b281f88df29605c1893de2701455c8d96b36823fe17b090881facdedd2",
    "assets/u010/CNX_BMath_Figure_01_02_011_img.svg": "5a0b2e8cbc9e99a1b0e5ea7118504ed6c3e22afc6ab452edf01a55a174c9cbf2",
    "assets/u010/CNX_BMath_Figure_01_02_014_img.svg": "03c8e097aafcf4f0b70d717ef50603d7f10d65b8af7e35edcd877da07eba1d9c",
    "assets/u010/CNX_BMath_Figure_01_02_015_img.svg": "7dc793136b68afbbb7008f9bb1368a8a4ab4b84883479db0af899dfd53e0a17c",
    "assets/u010/CNX_BMath_Figure_01_02_016_img-02.svg": "d1feb926b61826c4bdc5844baada202ab14984345d3a0b2200ff66417b09dcce",
    "assets/u010/CNX_BMath_Figure_01_02_016_img-03.svg": "2bc78b001200294ed04fa5a671e2dfbe442b30feaad2ea063810101cc4f24c08",
    "assets/u010/CNX_BMath_Figure_01_02_016_img-04.svg": "b1d7bfcd542da3ec9d3cec7bb59f9da852bde0de5347d8582ddaa02fbfd0ddb6",
    "assets/u010/CNX_BMath_Figure_01_02_017_img-02.svg": "5954352eee5eafb23b0e7d4410e8bed5442d183b79c5ae91d20ea4fa7e254c0c",
    "assets/u010/CNX_BMath_Figure_01_02_017_img-03.svg": "4a14caea4603879f3a971ebc41768b3c36dd7fd38cf9648856f853c7d6334bba",
    "assets/u010/CNX_BMath_Figure_01_02_017_img-04.svg": "f6eb6b7f97a4a5c9cfa8d638891b8684e41c10bef94bc8aeceeabf180b7216b6",
    "assets/u010/CNX_BMath_Figure_01_02_018_img-02.svg": "3ad6ac3875e5415cbe23d838e8c6c750aac464a6dc5526849b3a9a24a8abe1f0",
    "assets/u010/CNX_BMath_Figure_01_02_018_img-03.svg": "8d0856e8ff4a68ec677f50c786e71e635333428c6cafae23b1c511b2444a1e0e",
    "assets/u010/CNX_BMath_Figure_01_02_018_img-04.svg": "87878a59df82b05e6a82cc32330fc060f7b19de13e25176b2b179bbc46f3adff",
    "assets/u010/CNX_BMath_Figure_01_02_018_img-05.svg": "c0f681a8bec1a79f53c9a251e78a28dc89918f86930156f8fffe434407e310b3",
    "assets/u010/CNX_BMath_Figure_01_02_019_img-02.svg": "892ac3211a72ac584e8d6a93c046a68522a84d928b2bd24563d97c62fbf519a2",
    "assets/u010/CNX_BMath_Figure_01_02_019_img-03.svg": "3dddda305b960bdcd40c8b3ef53992faa9560486d520760ff30b1c6fbd7bef80",
    "assets/u010/CNX_BMath_Figure_01_02_019_img-04.svg": "0e2aa5f45fafeb1ec51ac5a02cf446847729aae2630b5b9b4477cd6c3b9f1928",
    "assets/u011/CNX_BMath_Figure_01_02_001.svg": "49a1e4b853feff76027afddd534703eaa7d095a4e4ab5f3e63e41e809bf64615",
    "assets/u011/CNX_BMath_Figure_01_02_020-01.svg": "050eb554730a493db0aa131fbaf912f88dc46978ba331276f5c5d0c32d7bb437",
    "assets/u011/CNX_BMath_Figure_01_02_020-02.svg": "052440f57da0a1ac242acfa573253f070a5ed5d7e7da1ea2800ef99cb735a3d7",
    "assets/u011/CNX_BMath_Figure_01_02_020-03.svg": "efacbf07d122eccc74f27b4df9b4f0554c91e26d0563b4da5dda59cc53d8e8c0",
    "assets/u011/CNX_BMath_Figure_01_02_020-04.svg": "de7d24d110f98a79fb8cd192c4284c7647489b43d7a9ce2b5cb6a23b4f4919e0",
    "assets/u013/CNX_BMath_Figure_01_02_002.svg": "9e7ba0e663a9fac7d3d801b8c14e9572a31482c872f521d7ca9ddde44671e249",
    "assets/u013/CNX_BMath_Figure_01_02_003.svg": "15c5db825e70164c99083bd70dbd184ada8d805fe9cc3f94ccae44d20022c67d",
    "assets/u013/CNX_BMath_Figure_01_02_004.svg": "fe97fdf9a9d0fc68890f683d4a0454829fa1165b375aed8d294d159b170fa911",
    "assets/u015/CNX_BMath_Figure_01_02_201_img.svg": "cdd8d5d34ec4b56a11c9271132cbae3095bad2e722104a546ba13b43153b5319",
    "assets/u015/CNX_BMath_Figure_01_02_203_img.svg": "b660d63382605e5217494de5a30673a2905426a47ab0bf567d432797e1257175",
    "assets/u015/CNX_BMath_Figure_01_02_205_img.svg": "4b61c9807dd4106ea31d867140b6d819de903fd84fc45914876b48b8097668a1",
    "assets/u015/CNX_BMath_Figure_01_02_207_img.svg": "710910a69c6985fed04332caea7a94bb0086306504035daf98f42799579b626a",
    "assets/u015/CNX_BMath_Figure_01_02_208_img.svg": "4a0869de066919d06bc20d9d8ef1f0c52427d9a73ace3869e9c972b5571b1513",
    "assets/u015/CNX_BMath_Figure_01_02_209_img.svg": "e395382dda6fcf31b820ebe58879f0fd219322c56b2c5ffd3658c4788dff751a",
    "assets/u015/CNX_BMath_Figure_01_02_210_img.svg": "d73aed185760b5f517237141999ee4333d0c15cb4c0a15e1b03d86570da6c6a7",
    "assets/u015/CNX_BMath_Figure_01_02_211_img.svg": "d722571d7eb0568744cd00e4d045b3f3a8659efd4b8e6419d785145a2a1e8225",
    "assets/u015/CNX_BMath_Figure_01_02_212_img.svg": "93bb72459c5f83b3493d59314bd0e805f49828eb37782153e947cea857db299e",
    "assets/u015/CNX_BMath_Figure_01_02_213_img.svg": "0849e46e2f29f35179b1d600e4ce4053a3a53e96c5515a0b45b36729b5b5c4c6",
    "assets/u015/CNX_BMath_Figure_01_02_214_img.svg": "296387967e10097b37be218e8568b446baa5cba72f341b4105ef825bb2addd08",
    "assets/u015/CNX_BMath_Figure_01_02_215_img.svg": "a04dbddd4e8323c4b0468749afe3accaf0d9c4ceab20eb54b0270b644b5b8725",
    "assets/u015/CNX_BMath_Figure_01_02_216.svg": "7e9679afb862b0c2c783cf1a629fbb5c570d82fde071afac905d80c6d478f6eb",
    "assets/u015/CNX_BMath_Figure_01_02_217.svg": "a16943ed2d98aacbf34cccb556ec814f92ea1f5c160a407357e43c46c4e985b5",
    "assets/u015/CNX_BMath_Figure_01_02_218.svg": "2b621a1053c3bb28fd5418c420a8166fa0943f82a23c7b0967f0df7528a32194",
    "assets/u015/CNX_BMath_Figure_01_02_220.svg": "b8a97fa35dbb983bc7d98af5e72b4f21689cd57cdcd899d307ab529fc2dfda27",
    "assets/u015/CNX_BMath_Figure_01_02_221.svg": "19a34267cc9d7c63a1cafdd0ffd91bb32d12c391ad8972fd296bbabbb504bf3b",
    "assets/u015/CNX_BMath_Figure_01_02_222.svg": "883ca73fc1194efefb0c070f680153105c91cf6f7a3873c38353345f26d7f071",
    "assets/u015/CNX_BMath_Figure_01_02_224.svg": "d4f7ff1419c6fb02f1e46fd705b61489cdd37241b2d79b6ebe5e2fe60584fee1",
    "assets/u015/CNX_BMath_Figure_01_02_225.svg": "44ca1ed2baefddcf25e5346510cff80be17e0e19e1ef4ae7d8e8ffdbe23272d1",
    "assets/u015/CNX_BMath_Figure_01_02_226.svg": "1e06ac1d21780c7e089c0473533bd11f99002e526cf0d1bbb953ee5d28732806",
    "assets/m81244-tail/CNX_BMath_Figure_AppB_002_A.svg": "cd0294912322fca86eeb73681c7f769f6ff86620c250e2f8dbb47ffe09bc8ae3",
}
ASSET_SCOPE_DIRS = (
    "assets/m81244-readiness", "assets/u010", "assets/u011",
    "assets/u013", "assets/u015", "assets/m81244-tail",
)

CANON_EVIDENCE = {
    "C11-pdf-page-036-ocr": (REPO / "downloads/tamil-canon/ocr/page-036.txt", "0729f5fab7454c703a640ed3817f0ddfb9c8e8f3a763ed3c449e312076b0ed16"),
    "C11-pdf-page-036-image": (REPO / "downloads/tamil-canon/ocr/page-036.png", "f51ec4222c04debe338f7565f8d9d6eab9dd5be56b22716bcb688c9fa78c1c1c"),
    "C17-pdf-page-038-ocr": (REPO / "downloads/tamil-canon/ocr/page-038.txt", "14565da267984e61411efda2d54e77aa9041f0b7d099d335795238043b1a6297"),
    "C17-pdf-page-038-image": (REPO / "downloads/tamil-canon/ocr/page-038.png", "ec91d59f4a408ed9aadea9d543a61b6158f11151be451ac0d4b7d947937941b8"),
    "C18-pdf-page-046-ocr": (REPO / "downloads/tamil-canon/ocr/page-046.txt", "b7955cfbf49c5321874771aa26755d1e4ecfad0031ada9ed034d479bfdefda89"),
    "C18-pdf-page-046-image": (REPO / "downloads/tamil-canon/ocr/page-046.png", "c208f8b59c7a2747171152f4e53198c48aae52858a24f76880cd9f024cdfb229"),
    "C12-pdf-page-175-ocr": (REPO / "downloads/tamil-canon/ocr/page-175.txt", "17546f2815c3077bf5fc2d90d1fca376b6aa4a83fd664e01907b3e5969b2d999"),
    "C12-pdf-page-175-image": (REPO / "downloads/tamil-canon/ocr/page-175.png", "a4790fc94ecf2b3b4af3bab80f383e5383ef60e9e65ff8f72df8bc4d49437679"),
}

EXPECTED_EXTERNAL_URLS = {
    "https://www.openstax.org/l/24add2blocks",
    "https://www.openstax.org/l/24add3blocks",
    "https://www.openstax.org/l/24addwhlnumb",
}
UNRESOLVED = re.compile(r"\b(?:TODO|TBD|FIXME|TRANSLATE_ME|PLACEHOLDER)\b|\?\?\?", re.I)
NONLOCAL_REFERENCE = re.compile(r"(?:[A-Za-z][A-Za-z0-9+.-]*:|//)")
CSS_URL_START = re.compile(r"url\s*\(", re.I)
CSS_URL = re.compile(r"url\s*\(\s*(['\"]?)([^)'\"\s]+)\1\s*\)", re.I)
SVG_XML_DECLARATIONS = (
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<?xml version="1.0" encoding="utf-8"?>',
)
SVG_ALLOWED_ELEMENTS = {"svg", "title", "desc", "g", "rect", "path", "text", "tspan"}
SVG_ALLOWED_ATTRIBUTES = {
    "aria-hidden", "aria-labelledby", "d", "data-column", "data-columns", "data-count",
    "data-kind", "data-label", "data-length", "data-model", "data-place", "data-role",
    "data-row", "data-rows", "data-side", "data-source-media", "data-stage",
    "data-target-side", "data-tone", "data-unit", "dy", "fill", "font-family",
    "font-size", "font-weight", "height", "id", "lang", "role", "stroke",
    "stroke-linecap", "stroke-linejoin", "stroke-width", "text-anchor", "transform",
    "viewBox", "width", "x", "y",
}


class AssemblyError(ValueError):
    """A deterministic, user-actionable assembly refusal."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssemblyError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel_repo(path: Path) -> str:
    path_abs = Path(os.path.abspath(path))
    repo_abs = Path(os.path.abspath(REPO))
    try:
        return path_abs.relative_to(repo_abs).as_posix()
    except ValueError:
        return path_abs.as_posix()


def rel_lang(path: Path) -> str:
    path_abs = Path(os.path.abspath(path))
    lang_abs = Path(os.path.abspath(LANG))
    try:
        return path_abs.relative_to(lang_abs).as_posix()
    except ValueError:
        return path_abs.as_posix()


def is_reparse_or_symlink(path: Path) -> bool:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return stat.S_ISLNK(status.st_mode) or bool(getattr(status, "st_file_attributes", 0) & reparse_flag)


def reject_reparse_components(path: Path, anchor: Path, label: str) -> None:
    anchor_abs = Path(os.path.abspath(anchor))
    path_abs = Path(os.path.abspath(path))
    try:
        relative = path_abs.relative_to(anchor_abs)
    except ValueError as exc:
        raise AssemblyError(f"{label} escapes its lexical anchor: {path}") from exc
    current = anchor_abs
    if os.path.lexists(current):
        require(not is_reparse_or_symlink(current), f"{label} anchor is a reparse point: {current}")
    for part in relative.parts:
        current /= part
        if os.path.lexists(current):
            require(not is_reparse_or_symlink(current), f"{label} traverses a reparse point: {current}")


def scan_regular_tree(root: Path, relative_base: Path, label: str) -> tuple[set[str], set[str]]:
    reject_reparse_components(root, LANG, label)
    require(root.is_dir() and not is_reparse_or_symlink(root), f"Missing or unsafe directory: {root}")
    files: set[str] = set()
    directories: set[str] = set()

    def walk(directory: Path) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                status = entry.stat(follow_symlinks=False)
                reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
                require(not stat.S_ISLNK(status.st_mode) and
                        not bool(getattr(status, "st_file_attributes", 0) & reparse_flag),
                        f"{label} contains a reparse point: {path}")
                if stat.S_ISDIR(status.st_mode):
                    directories.add(path.relative_to(relative_base).as_posix())
                    walk(path)
                elif stat.S_ISREG(status.st_mode):
                    files.add(path.relative_to(relative_base).as_posix())
                else:
                    raise AssemblyError(f"{label} contains a non-regular entry: {path}")

    walk(root)
    return files, directories


def scan_regular_files(root: Path, relative_base: Path, label: str) -> set[str]:
    return scan_regular_tree(root, relative_base, label)[0]


def validate_fragment_inventory() -> None:
    translation = LANG / "translation"
    reject_reparse_components(translation, LANG, "translation directory")
    actual = set()
    with os.scandir(translation) as entries:
        for entry in entries:
            if not (entry.name.startswith("m81244") and entry.name.endswith(".cnxml")):
                continue
            status = entry.stat(follow_symlinks=False)
            reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            require(stat.S_ISREG(status.st_mode) and not stat.S_ISLNK(status.st_mode) and
                    not bool(getattr(status, "st_file_attributes", 0) & reparse_flag),
                    f"M81244 fragment inventory contains a non-regular entry: {entry.path}")
            actual.add(entry.name)
    require(actual == EXPECTED_FRAGMENT_FILES,
            f"M81244 fragment inventory changed: missing={sorted(EXPECTED_FRAGMENT_FILES-actual)}, "
            f"extra={sorted(actual-EXPECTED_FRAGMENT_FILES)}")


def text(node: ET.Element | None) -> str:
    return "" if node is None else "".join(node.itertext()).strip()


def parse_pinned_bytes(data: bytes, label: str) -> ET.Element:
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise AssemblyError(f"Malformed pinned XML: {label}: {exc}") from exc


def verify_pin(path: Path, expected: str | None, kind: str) -> bytes:
    require(expected is not None and re.fullmatch(r"[0-9a-f]{64}", expected),
            f"{kind} is not yet pinned; refusing assembly: {rel_repo(path)}")
    path_abs = Path(os.path.abspath(path))
    anchor = LANG if path_abs.is_relative_to(Path(os.path.abspath(LANG))) else REPO
    reject_reparse_components(path_abs, anchor, f"pinned {kind}")
    require(os.path.lexists(path_abs), f"Missing pinned {kind}: {rel_repo(path)}")
    status = path_abs.lstat()
    require(stat.S_ISREG(status.st_mode) and not is_reparse_or_symlink(path_abs),
            f"Pinned {kind} is not a regular non-reparse file: {rel_repo(path)}")
    data = path_abs.read_bytes()
    final_status = path_abs.lstat()
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
    require(identity(status) == identity(final_status) and
            stat.S_ISREG(final_status.st_mode) and not is_reparse_or_symlink(path_abs),
            f"Pinned {kind} changed while it was being snapshotted: {rel_repo(path)}")
    require(sha_bytes(data) == expected, f"Pinned {kind} changed: {rel_repo(path)}")
    return data


def stable_attributes(node: ET.Element) -> dict[str, str]:
    ignored = {XML_LANG}
    if node.tag == f"{{{C}}}media":
        ignored.add("alt")
    elif node.tag == f"{{{C}}}image":
        ignored.update(("src", "mime-type"))
    elif node.tag == f"{{{C}}}table":
        ignored.update(("aria-label", "summary"))
    return {key: value for key, value in node.attrib.items() if key not in ignored}


def mtext_skeleton(value: str | None) -> tuple[str, ...]:
    punctuation = set(".,…-_()/%‰")
    return tuple(character for character in value or ""
                 if unicodedata.category(character) in {"Nd", "Nl", "No", "Sm", "Sc"}
                 or character in punctuation)


def source_symbol_sequence(value: str) -> tuple[str, ...]:
    return tuple(character for character in value
                 if unicodedata.category(character) in {"Nd", "Nl", "No", "Sm", "Sc"}
                 or character in "%‰")


def canonical_media_stem(value: str) -> str:
    name = Path(urlparse(value).path).name
    removable = {".svg", ".png", ".jpg", ".jpeg", ".id-id", ".en"}
    while Path(name).suffix.lower() in removable:
        name = name[:-len(Path(name).suffix)]
    return name


def exact_tree_signature(node: ET.Element) -> tuple:
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        node.text or "",
        tuple((exact_tree_signature(child), child.tail or "") for child in node),
    )


def math_signature(node: ET.Element) -> tuple:
    value = node.text if node.text and node.text.strip() else ""
    if node.tag == f"{{{M}}}mtext":
        # mtext is linguistic content.  Its mathematical payload is checked
        # separately against the two pinned witnesses because their own
        # language-specific punctuation is not always identical.
        value = ()
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        value,
        tuple((math_signature(child), child.tail if child.tail and child.tail.strip() else "")
              for child in node),
    )


def digit_sequence(node: ET.Element) -> list[str]:
    return [token for slot in node.itertext() for token in re.findall(r"[0-9]+", slot)]


def validate_bilingual_mathml_payload(source_en: ET.Element, source_id: ET.Element,
                                      target: ET.Element) -> None:
    source_en_mtext = list(source_en.iter(f"{{{M}}}mtext"))
    source_id_mtext = list(source_id.iter(f"{{{M}}}mtext"))
    target_mtext = list(target.iter(f"{{{M}}}mtext"))
    require(len(source_en_mtext) == len(source_id_mtext) == len(target_mtext),
            "MathML mtext count differs from pinned witnesses")
    for index, (en_node, id_node, target_node) in enumerate(
            zip(source_en_mtext, source_id_mtext, target_mtext)):
        allowed = {mtext_skeleton(en_node.text), mtext_skeleton(id_node.text)}
        require(mtext_skeleton(target_node.text) in allowed,
                f"MathML mtext mathematical payload changed at index {index}")


def compare_source(source: ET.Element, target: ET.Element, label: str) -> None:
    src_nodes, dst_nodes = list(source.iter()), list(target.iter())
    require([node.tag for node in src_nodes] == [node.tag for node in dst_nodes],
            f"Source element hierarchy/order changed: {label}")
    require([len(node) for node in src_nodes] == [len(node) for node in dst_nodes],
            f"Source child counts/hierarchy changed: {label}")
    require([stable_attributes(node) for node in src_nodes] == [stable_attributes(node) for node in dst_nodes],
            f"Source IDs/non-language attributes changed: {label}")
    require([math_signature(node) for node in source.iter(f"{{{M}}}math")] ==
            [math_signature(node) for node in target.iter(f"{{{M}}}math")],
            f"MathML structure/numeric/operator content changed: {label}")
    require(digit_sequence(source) == digit_sequence(target),
            f"Source prose/math numeral sequence changed: {label}")
    for src, dst in zip(src_nodes, dst_nodes):
        src_direct = (src.text or "") + "".join(child.tail or "" for child in src)
        dst_direct = (dst.text or "") + "".join(child.tail or "" for child in dst)
        require(source_symbol_sequence(src_direct) == source_symbol_sequence(dst_direct),
                f"Source numeral/math/currency symbols changed: {label}: {src.get('id', src.tag)}")
        if src_direct.strip():
            require(dst_direct.strip(), f"Source direct prose removed: {label}: {src.get('id', src.tag)}")
        else:
            require(not dst_direct.strip(),
                    f"Unexpected prose added to source-empty node: {label}: {dst.get('id', dst.tag)}")
        if src.tag == f"{{{C}}}media":
            require(bool((src.get("alt") or "").strip()) == bool((dst.get("alt") or "").strip()),
                    f"Media alternative presence changed: {label}: {src.get('id')}")
        elif src.tag == f"{{{C}}}image":
            source_stem = canonical_media_stem(src.get("src") or "")
            target_stem = canonical_media_stem(dst.get("src") or "")
            require(source_stem and source_stem == target_stem,
                    f"Media/source identity changed: {label}: {source_stem} -> {target_stem}")
        elif src.tag == f"{{{C}}}table":
            source_label = (src.get("aria-label") or src.get("summary") or "").strip()
            target_label = (dst.get("aria-label") or dst.get("summary") or "").strip()
            require(bool(source_label) == bool(target_label),
                    f"Table accessible-label presence changed: {label}: {src.get('id')}")


def validate_exact_fragment_assembly(root: ET.Element,
                                     fragment_roots: dict[str, ET.Element],
                                     source_en: ET.Element) -> None:
    front = fragment_roots["frontmatter"]
    require(root.tag == front.tag and root.attrib == front.attrib and root.text == front.text,
            "Assembled document root differs from pinned front matter")
    for name in ("title", "metadata"):
        require(exact_tree_signature(root.find(f"{{{C}}}{name}")) ==
                exact_tree_signature(front.find(f"{{{C}}}{name}")),
                f"Assembled {name} differs from pinned front matter")
    content = root.find(f"{{{C}}}content")
    source_content = source_en.find(f"{{{C}}}content")
    require(content is not None and content.attrib == source_content.attrib and not (content.text or "").strip(),
            "Assembled content wrapper differs from the pinned canonical wrapper")
    require(tuple(node.get("id") for node in content) == DIRECT_CONTENT_ORDER,
            "Assembled direct content order differs from the pinned fragment plan")
    for source_id in DIRECT_CONTENT_ORDER[:-1]:
        require(exact_tree_signature(content_child(root, source_id)) ==
                exact_tree_signature(fragment_roots[source_id]),
                f"Assembled subtree differs from pinned fragment: {source_id}")
    assembled_outer = content_child(root, OUTER_ID)
    canonical_outer = content_child(source_en, OUTER_ID)
    require(assembled_outer.tag == canonical_outer.tag and assembled_outer.attrib == canonical_outer.attrib and
            not (assembled_outer.text or "").strip(),
            f"Assembled outer wrapper differs from canonical {OUTER_ID}")
    require(tuple(node.get("id") for node in assembled_outer) == OUTER_CHILD_ORDER,
            "Assembled outer child order differs from the pinned fragment plan")
    for source_id in OUTER_CHILD_ORDER:
        found = next(node for node in assembled_outer if node.get("id") == source_id)
        require(exact_tree_signature(found) == exact_tree_signature(fragment_roots[source_id]),
                f"Assembled subtree differs from pinned fragment: {source_id}")
    require(exact_tree_signature(root.find(f"{{{C}}}glossary")) ==
            exact_tree_signature(fragment_roots["glossary"]),
            "Assembled glossary differs from pinned glossary fragment")


def check_authored(root: ET.Element, label: str) -> None:
    require(root.get(XML_LANG) == LOCALE, f"Missing or wrong fragment language: {label}")
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    require(len(ids) == len(set(ids)), f"Duplicate IDs inside fragment: {label}")
    for node in root.iter():
        for value in [node.text or "", node.tail or "", *node.attrib.values()]:
            require(not UNRESOLVED.search(value), f"Unresolved authoring marker in {label}: {value[:100]}")


def validate_mathml(root: ET.Element) -> None:
    maths = list(root.iter(f"{{{M}}}math"))
    allowed = {"math", "mrow", "mn", "mo", "mi", "mtext", "mspace",
               "mover", "munder", "mtable", "mtr", "mtd"}
    token_elements = {"mn", "mo", "mi", "mtext"}
    for math in maths:
        require(len(math) > 0, "Empty MathML root")
        for node in math.iter():
            require(node.tag.startswith(f"{{{M}}}"), f"Foreign element inside MathML: {node.tag}")
            local = node.tag.rsplit("}", 1)[-1]
            require(local in allowed, f"Unknown or unreviewed MathML element: {local}")
            for key, value in node.attrib.items():
                attr = key.rsplit("}", 1)[-1].lower()
                require(not attr.startswith("on") and attr not in {"href", "src"},
                        f"Active/external MathML attribute: {key}={value}")
            if local in token_elements:
                require(len(node) == 0, f"MathML token unexpectedly contains elements: {local}")
                require((node.text or "").strip(), f"Empty MathML token: {local}")
            elif local == "mspace":
                require(len(node) == 0 and not (node.text or "").strip(),
                        "Malformed MathML mspace")
            elif local in {"mover", "munder"}:
                require(len(node) == 2, f"Malformed MathML {local}: expected two children")
            elif local == "mtable":
                require(len(node) > 0 and all(child.tag == f"{{{M}}}mtr" for child in node),
                        "Malformed MathML mtable")
            elif local == "mtr":
                require(all(child.tag == f"{{{M}}}mtd" for child in node),
                        "Malformed MathML mtr")
            elif local in {"math", "mrow", "mtd"}:
                require(len(node) > 0, f"Malformed empty MathML container: {local}")


def validate_svg_bytes(data: bytes, label: str) -> None:
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AssemblyError(f"SVG must be UTF-8: {label}") from exc
    lowered = decoded.casefold()
    require("<!doctype" not in lowered and "<!entity" not in lowered,
            f"SVG DTD/entity declaration is forbidden: {label}")
    body = decoded.lstrip("\ufeff \t\r\n")
    if body.startswith("<?"):
        declaration = next((candidate for candidate in SVG_XML_DECLARATIONS
                            if body.startswith(candidate)), None)
        require(declaration is not None,
                f"SVG processing instruction or unreviewed XML declaration is forbidden: {label}")
        body = body[len(declaration):]
    require("<?" not in body, f"SVG processing instruction is forbidden: {label}")


def validate_css_references(value: str, label: str) -> None:
    require("\\" not in value, f"Escaped/obfuscated SVG CSS is forbidden: {label}")
    starts = list(CSS_URL_START.finditer(value))
    matches = list(CSS_URL.finditer(value))
    require(len(starts) == len(matches), f"Malformed or obfuscated SVG CSS URL: {label}")
    for match in matches:
        reference = match.group(2)
        require(reference.startswith("#"), f"External SVG CSS URL: {label}: {reference}")
    lowered = value.lower()
    require("@import" not in lowered and "expression(" not in lowered and "-moz-binding" not in lowered,
            f"Active/external SVG CSS is forbidden: {label}")


def validate_svg_root(root: ET.Element, label: str, expected_alt: str) -> list[str]:
    require(root.tag == f"{{{SVG}}}svg", f"Not an SVG document: {label}")
    require(root.get("viewBox"), f"SVG has no viewBox: {label}")
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    require(len(ids) == len(set(ids)), f"Duplicate IDs inside SVG: {label}")
    title_node, desc_node = root.find(f"{{{SVG}}}title"), root.find(f"{{{SVG}}}desc")
    require(text(title_node), f"SVG title missing: {label}")
    require(text(desc_node) == expected_alt, f"SVG description/current CNXML alternative mismatch: {label}")
    require(root.get("role") == "img", f"SVG image role missing: {label}")
    require(title_node.get("id") and desc_node.get("id"), f"SVG title/description IDs missing: {label}")
    labelled_by = (root.get("aria-labelledby") or "").split()
    require(labelled_by == [title_node.get("id"), desc_node.get("id")],
            f"SVG accessible-name references must identify title then description: {label}")
    for token in labelled_by:
        require(token in ids, f"Broken SVG accessible-name reference: {label}: {token}")
    for node in root.iter():
        require(node.tag.startswith(f"{{{SVG}}}"), f"Foreign element inside SVG: {label}: {node.tag}")
        local = node.tag.rsplit("}", 1)[-1]
        require(local in SVG_ALLOWED_ELEMENTS,
                f"Unknown or active SVG element outside the pinned module vocabulary: {label}: {local}")
        for key, value in node.attrib.items():
            if key.startswith("{"):
                require(key == XML_LANG,
                        f"Foreign or active namespaced SVG attribute: {label}: {key}")
                attr = "xml:lang"
            else:
                require(key in SVG_ALLOWED_ATTRIBUTES,
                        f"Unknown or active SVG attribute outside the pinned module vocabulary: {label}: {key}")
                attr = key.lower()
            require(not attr.startswith("on"), f"SVG event handler: {label}: {key}")
            require(attr != "style", f"SVG style attributes are forbidden: {label}")
            if attr == "href":
                require(value.startswith("#") and value[1:] in ids,
                        f"External or unresolved SVG href: {label}: {value}")
            if key == "aria-labelledby":
                references = value.split()
                require(references and all(reference in ids for reference in references),
                        f"Empty or unresolved SVG aria-labelledby reference: {label}: {value}")
            validate_css_references(value, label)
    for node in root.iter():
        for value in node.attrib.values():
            for match in CSS_URL.finditer(value):
                reference = match.group(2)
                require(reference[1:] in ids,
                        f"Unresolved local SVG CSS URL: {label}: {reference}")
    return ids


def content_child(root: ET.Element, source_id: str) -> ET.Element:
    content = root.find(f"{{{C}}}content")
    require(content is not None, "Canonical source has no content container")
    found = next((node for node in content if node.get("id") == source_id), None)
    require(found is not None, f"Canonical direct content child missing: {source_id}")
    return found


def outer_child(root: ET.Element, source_id: str) -> ET.Element:
    outer = content_child(root, OUTER_ID)
    found = next((node for node in outer if node.get("id") == source_id), None)
    require(found is not None, f"Canonical outer-section child missing: {source_id}")
    return found


def solution_inventory(root: ET.Element) -> list[dict]:
    parents = {child: parent for parent in root.iter() for child in parent}
    records = []
    for exercise in root.iter(f"{{{C}}}exercise"):
        solutions = exercise.findall(f"{{{C}}}solution")
        empty = [node.get("id") for node in solutions if not text(node) and len(node) == 0]
        if not solutions or empty:
            sections = []
            node = exercise
            while node in parents:
                node = parents[node]
                if node.tag == f"{{{C}}}section" and node.get("id"):
                    sections.append(node.get("id"))
            records.append({
                "section_path": list(reversed(sections)),
                "exercise_id": exercise.get("id"),
                "problem_ids": [node.get("id") for node in exercise.findall(f"{{{C}}}problem")],
                "status": "source-has-no-solution-node" if not solutions else "source-has-empty-solution-node",
                "empty_solution_ids": empty,
            })
    return records


def validate_link_set(root: ET.Element, module_ids: set[str], support_ids: dict[str, set[str]]) -> list[dict]:
    links, seen_external = [], set()
    for node in root.iter():
        for key, value in node.attrib.items():
            local = key.rsplit("}", 1)[-1].lower()
            if NONLOCAL_REFERENCE.search(value):
                require(node.tag == f"{{{C}}}link" and local == "url",
                        f"Nonlocal reference outside canonical source link: {node.tag}: {key}={value}")
            if local == "href":
                raise AssemblyError(f"Unexpected href in assembled CNXML: {node.tag}: {value}")
    for link in root.iter(f"{{{C}}}link"):
        target_id, url = link.get("target-id"), link.get("url")
        require(bool(target_id) != bool(url), f"Unhandled source link form: {link.attrib}")
        if target_id:
            document = link.get("document", "m81244")
            require(document in {"m81244", *support_ids}, f"Unsupported linked module: {document}")
            ids = module_ids if document == "m81244" else support_ids[document]
            require(target_id in ids, f"Unresolved module-qualified source target: ({document}, {target_id})")
            links.append({"document": document, "target_id": target_id,
                          "kind": "within-review-source" if document == "m81244" else "canonical-cross-module-source-reference"})
        else:
            parsed = urlparse(url)
            require(parsed.scheme in {"http", "https"} and parsed.netloc, f"Malformed source URL: {url}")
            require(url in EXPECTED_EXTERNAL_URLS, f"Unexpected nonlocal source URL: {url}")
            seen_external.add(url)
            links.append({"url": url, "kind": "canonical-source-reference-not-offline-runtime-dependency"})
    require(seen_external == EXPECTED_EXTERNAL_URLS,
            f"Canonical external-source URL inventory changed: {sorted(seen_external)}")
    return links


def validate_asset_sets(referenced: set[str], actual: set[str]) -> None:
    require(referenced == set(EXPECTED_ASSETS),
            f"Referenced asset inventory differs from pinned inventory: missing={sorted(set(EXPECTED_ASSETS)-referenced)}, extra={sorted(referenced-set(EXPECTED_ASSETS))}")
    require(actual == set(EXPECTED_ASSETS),
            f"Scoped asset directories contain missing/extra/unreferenced files: missing={sorted(set(EXPECTED_ASSETS)-actual)}, extra={sorted(actual-set(EXPECTED_ASSETS))}")


def require_no_scoped_asset_directories(relative_dir: str, directories: set[str]) -> None:
    require(not directories,
            f"Scoped asset directory contains unexpected subdirectories: {relative_dir}: {sorted(directories)}")


def scan_scoped_asset_inventory(label_prefix: str) -> set[str]:
    actual = set()
    for relative_dir in ASSET_SCOPE_DIRS:
        files, directories = scan_regular_tree(
            LANG / relative_dir, LANG, f"{label_prefix} {relative_dir}",
        )
        require_no_scoped_asset_directories(relative_dir, directories)
        actual.update(files)
    return actual


def validate_assets(root: ET.Element) -> tuple[list[dict], dict[Path, str], dict[Path, bytes]]:
    referenced, records, pins, pinned_bytes, global_svg_ids = [], [], {}, {}, set()
    for medium in root.iter(f"{{{C}}}media"):
        alt = (medium.get("alt") or "").strip()
        require(alt, f"Missing media alternative: {medium.get('id')}")
        images = list(medium.iter(f"{{{C}}}image"))
        require(len(images) == 1, f"Expected exactly one image per media: {medium.get('id')}")
        image = images[0]
        src = image.get("src") or ""
        parsed = urlparse(src)
        require(src and not parsed.scheme and not parsed.netloc and not parsed.fragment,
                f"Remote or malformed media source: {src}")
        asset = ((LANG / "translation") / src).resolve()
        require(asset.is_relative_to((LANG / "assets").resolve()), f"Media escaped assets directory: {src}")
        relative_asset = rel_lang(asset)
        require(relative_asset in EXPECTED_ASSETS, f"Unpinned media dependency: {relative_asset}")
        asset_data = verify_pin(asset, EXPECTED_ASSETS[relative_asset], "SVG asset")
        require(image.get("mime-type") == "image/svg+xml" and asset.suffix.lower() == ".svg",
                f"Unreviewed media format: {relative_asset}")
        validate_svg_bytes(asset_data, relative_asset)
        svg_root = parse_pinned_bytes(asset_data, relative_asset)
        svg_ids = validate_svg_root(svg_root, relative_asset, alt)
        require(global_svg_ids.isdisjoint(svg_ids), f"Cross-asset SVG ID collision: {relative_asset}")
        global_svg_ids.update(svg_ids)
        referenced.append(relative_asset)
        pins[asset] = EXPECTED_ASSETS[relative_asset]
        pinned_bytes[asset] = asset_data
        records.append({
            "media_id": medium.get("id"), "source_path": src,
            "package_path": relative_asset, "sha256": EXPECTED_ASSETS[relative_asset],
            "svg_ids": len(svg_ids),
        })
    require(len(referenced) == len(set(referenced)), "A pinned SVG is referenced more than once unexpectedly")
    actual = scan_scoped_asset_inventory("scoped asset directory")
    validate_asset_sets(set(referenced), actual)
    return records, pins, pinned_bytes


def fragment_count(root: ET.Element) -> dict[str, int]:
    return {
        "elements": len(list(root.iter())),
        "ids": sum(bool(node.get("id")) for node in root.iter()),
        "mathml": len(list(root.iter(f"{{{M}}}math"))),
        "exercises": len(list(root.iter(f"{{{C}}}exercise"))),
        "solutions": len(list(root.iter(f"{{{C}}}solution"))),
        "media": len(list(root.iter(f"{{{C}}}media"))),
    }


def build_attribution_data(source_data: bytes) -> bytes:
    credits_root = parse_pinned_bytes(source_data, rel_lang(ATTRIBUTION_SOURCE[0]))
    matches = [node for node in credits_root.iter(f"{{{C}}}section")
               if node.get("id") == ATTRIBUTION_SECTION_ID]
    require(len(matches) == 1, f"Pinned attribution section missing or duplicated: {ATTRIBUTION_SECTION_ID}")
    section = deepcopy(matches[0])
    require(text(section.find(f"{{{C}}}title")) == "About the Authors",
            "Pinned attribution section title changed")
    require(section.find(f".//{{{C}}}media") is None and section.find(f".//{{{C}}}link") is None,
            "Attribution extract unexpectedly contains media or links")
    data = ET.tostring(section, encoding="utf-8", xml_declaration=True) + b"\n"
    require(exact_tree_signature(ET.fromstring(data)) == exact_tree_signature(section),
            "Serialized attribution extract differs from its pinned source section")
    return data


def expected_package_files() -> set[str]:
    return {"source/m81244.cnxml", "LICENSE.txt", "ATTRIBUTION.en.cnxml",
            "manifest.json", *EXPECTED_ASSETS}


def expected_package_directories() -> set[str]:
    directories = set()
    for relative_path in expected_package_files():
        parent = Path(relative_path).parent
        while parent != Path("."):
            directories.add(parent.as_posix())
            parent = parent.parent
    return directories


def validate_package_tree(actual_files: set[str], actual_directories: set[str]) -> None:
    expected = expected_package_files()
    require(actual_files == expected,
            f"Review package contains missing/extra files: missing={sorted(expected-actual_files)}, "
            f"extra={sorted(actual_files-expected)}")
    expected_directories = expected_package_directories()
    require(actual_directories == expected_directories,
            "Review package contains missing/extra directories: "
            f"missing={sorted(expected_directories-actual_directories)}, "
            f"extra={sorted(actual_directories-expected_directories)}")


def validate_package_file_set(actual: set[str]) -> None:
    """Exercise the exact package-file inventory independently in negative fixtures."""
    expected = expected_package_files()
    require(actual == expected,
            f"Review package contains missing/extra files: missing={sorted(expected-actual)}, "
            f"extra={sorted(actual-expected)}")


def verify_package_payload(source_data: bytes, attribution_data: bytes,
                           license_data: bytes) -> None:
    require(PACKAGE.is_dir(), f"Review package is missing: {rel_lang(PACKAGE)}")
    actual_files, actual_directories = scan_regular_tree(PACKAGE, PACKAGE, "review package")
    validate_package_tree(actual_files, actual_directories)
    require(SOURCE_OUTPUT.read_bytes() == source_data, "Packaged assembled CNXML is stale")
    require(ATTRIBUTION_OUTPUT.read_bytes() == attribution_data, "Packaged attribution extract is stale")
    require(LICENSE_OUTPUT.read_bytes() == license_data, "Packaged license is stale")
    require(sha(LICENSE_OUTPUT) == LICENSE_SOURCE[1], "Packaged license digest differs")
    for relative_asset, expected_digest in EXPECTED_ASSETS.items():
        packaged = PACKAGE / relative_asset
        source = LANG / relative_asset
        require(packaged.read_bytes() == source.read_bytes(),
                f"Packaged SVG differs from source asset: {relative_asset}")
        require(sha(packaged) == expected_digest, f"Packaged SVG digest differs: {relative_asset}")


def verify_package(source_data: bytes, attribution_data: bytes,
                   license_data: bytes, manifest_data: bytes) -> None:
    verify_package_payload(source_data, attribution_data, license_data)
    require(MANIFEST_OUTPUT.read_bytes() == manifest_data, "Packaged manifest is stale")


def package_snapshot() -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
    """Hash the complete exact package tree for stable, transaction-locked checks."""
    actual_files, actual_directories = scan_regular_tree(PACKAGE, PACKAGE, "review package snapshot")
    validate_package_tree(actual_files, actual_directories)
    return (
        tuple(sorted(actual_directories)),
        tuple((relative_path, sha(PACKAGE / relative_path)) for relative_path in sorted(actual_files)),
    )


def retained_stage_entries() -> list[str]:
    prefix = ".m81244-package-stage-"
    entries = []
    with os.scandir(LANG) as candidates:
        for candidate in candidates:
            if candidate.name.startswith(prefix):
                entries.append(candidate.name)
    return sorted(entries)


def assert_no_retained_stages() -> None:
    stages = retained_stage_entries()
    require(not stages,
            f"Retained/interrupted M81244 package staging state requires inspection: {stages}")


def acquire_build_lock() -> bytes:
    reject_reparse_components(BUILD_LOCK, LANG, "M81244 build lock")
    token = f"pid={os.getpid()}\n".encode("ascii")
    try:
        descriptor = os.open(
            BUILD_LOCK,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
    except FileExistsError as exc:
        raise AssemblyError(
            f"M81244 build lock already exists; inspect a possibly interrupted build: {rel_lang(BUILD_LOCK)}"
        ) from exc
    try:
        os.write(descriptor, token)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    reject_reparse_components(BUILD_LOCK, LANG, "M81244 build lock")
    require(BUILD_LOCK.read_bytes() == token, "M81244 build lock changed during acquisition")
    return token


def release_build_lock(token: bytes) -> None:
    reject_reparse_components(BUILD_LOCK, LANG, "M81244 build lock")
    require(BUILD_LOCK.is_file() and BUILD_LOCK.read_bytes() == token,
            "Refusing to remove a changed or non-regular M81244 build lock")
    BUILD_LOCK.unlink()


def write_new_stage_file(stage: Path, relative_path: str, data: bytes) -> Path:
    target = stage / relative_path
    reject_reparse_components(target, stage, "M81244 package staging")
    target.parent.mkdir(parents=True, exist_ok=True)
    reject_reparse_components(target, stage, "M81244 package staging")
    require(not os.path.lexists(target), f"Staging target already exists: {target}")
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)
    reject_reparse_components(target, stage, "M81244 package staging")
    require(stat.S_ISREG(target.lstat().st_mode) and target.read_bytes() == data,
            f"Staged bytes differ: {relative_path}")
    return target


def prepare_package_destination(path: Path) -> None:
    reject_reparse_components(path, PACKAGE, "review-package output")
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_reparse_components(path, PACKAGE, "review-package output")
    package_real = PACKAGE.resolve(strict=True)
    parent_real = path.parent.resolve(strict=True)
    require(parent_real.is_relative_to(package_real), f"Review-package output escaped package root: {path}")
    if os.path.lexists(path):
        status = path.lstat()
        require(stat.S_ISREG(status.st_mode) and not is_reparse_or_symlink(path),
                f"Refusing non-regular review-package destination: {path}")


def remove_verified_empty_stage(stage: Path) -> None:
    reject_reparse_components(stage, LANG, "M81244 package staging")
    for directory, child_directories, files in os.walk(stage, topdown=False, followlinks=False):
        require(not files, f"Refusing to remove nonempty retained stage: {directory}")
        for child in child_directories:
            path = Path(directory) / child
            reject_reparse_components(path, stage, "M81244 package staging")
            require(not any(path.iterdir()), f"Refusing to remove nonempty retained stage directory: {path}")
            path.rmdir()
    require(not any(stage.iterdir()), f"Refusing to remove nonempty retained stage: {stage}")
    stage.rmdir()


def write_package(source_data: bytes, attribution_data: bytes,
                  license_data: bytes, manifest_data: bytes) -> None:
    require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024,
            "Less than 100 MiB free; refusing review-package writes")
    lock_token = acquire_build_lock()
    try:
        assert_no_retained_stages()
        if os.path.lexists(PACKAGE):
            reject_reparse_components(PACKAGE, LANG, "existing review package")
            require(PACKAGE.is_dir(), f"Review package path is not a directory: {rel_lang(PACKAGE)}")
            actual_files, actual_directories = scan_regular_tree(PACKAGE, PACKAGE, "existing review package")
            extra = actual_files - expected_package_files()
            require(not extra, f"Refusing to overwrite package with unexpected files: {sorted(extra)}")
            extra_directories = actual_directories - expected_package_directories()
            require(not extra_directories,
                    f"Refusing to overwrite package with unexpected directories: {sorted(extra_directories)}")

        artifacts = {
            "source/m81244.cnxml": source_data,
            "ATTRIBUTION.en.cnxml": attribution_data,
            "LICENSE.txt": license_data,
            "manifest.json": manifest_data,
        }
        for relative_asset, expected_digest in EXPECTED_ASSETS.items():
            asset_data = (LANG / relative_asset).read_bytes()
            require(sha_bytes(asset_data) == expected_digest,
                    f"Asset changed between validation and staging: {relative_asset}")
            artifacts[relative_asset] = asset_data
        require(set(artifacts) == expected_package_files(), "Internal staged artifact inventory differs")

        stage = Path(tempfile.mkdtemp(prefix=".m81244-package-stage-", dir=LANG))
        reject_reparse_components(stage, LANG, "M81244 package staging")
        for relative_path, data in artifacts.items():
            write_new_stage_file(stage, relative_path, data)
        staged_files, staged_directories = scan_regular_tree(stage, stage, "staged M81244 review package")
        validate_package_tree(staged_files, staged_directories)

        reject_reparse_components(PACKAGE, LANG, "review-package output")
        PACKAGE.mkdir(parents=True, exist_ok=True)
        reject_reparse_components(PACKAGE, LANG, "review-package output")
        sentinel_data = (json.dumps({
            "schema_version": 1,
            "status": "build-in-progress-fail-closed",
            "complete": False,
            "final_manifest_sha256": sha_bytes(manifest_data),
            "retained_stage_if_interrupted": stage.name,
        }, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        sentinel = write_new_stage_file(stage, ".manifest-in-progress.json", sentinel_data)
        recovery_sentinel = write_new_stage_file(stage, ".manifest-recovery.json", sentinel_data)
        prepare_package_destination(MANIFEST_OUTPUT)
        os.replace(sentinel, MANIFEST_OUTPUT)

        for relative_path in sorted(set(artifacts) - {"manifest.json"}):
            destination = PACKAGE / relative_path
            prepare_package_destination(destination)
            os.replace(stage / relative_path, destination)
            reject_reparse_components(destination, PACKAGE, "review-package output")

        # The incomplete sentinel remains the visible manifest until every
        # payload byte has been verified and the staged final manifest has
        # itself been rechecked.  Atomic manifest promotion is the commit.
        verify_package_payload(source_data, attribution_data, license_data)
        staged_manifest = stage / "manifest.json"
        reject_reparse_components(staged_manifest, stage, "staged final M81244 manifest")
        require(staged_manifest.read_bytes() == manifest_data,
                "Staged final M81244 manifest changed before promotion")
        try:
            prepare_package_destination(MANIFEST_OUTPUT)
            os.replace(staged_manifest, MANIFEST_OUTPUT)
            reject_reparse_components(MANIFEST_OUTPUT, PACKAGE, "review-package output")
            verify_package(source_data, attribution_data, license_data, manifest_data)
        except BaseException:
            # If post-commit verification detects interference, revoke the
            # completion claim before reporting failure.
            prepare_package_destination(MANIFEST_OUTPUT)
            os.replace(recovery_sentinel, MANIFEST_OUTPUT)
            raise
        recovery_sentinel.unlink()
        remove_verified_empty_stage(stage)
        assert_no_retained_stages()
    finally:
        release_build_lock(lock_token)


def expect_failure(label: str, action) -> str:
    try:
        action()
    except AssemblyError:
        return label
    raise AssemblyError(f"Negative fixture accepted: {label}")


def run_negative_fixtures(output: ET.Element, source_en: ET.Element,
                          source_id: ET.Element,
                          first_svg: ET.Element, first_alt: str,
                          first_svg_bytes: bytes,
                          support_ids: dict[str, set[str]],
                          fragment_roots: dict[str, ET.Element]) -> list[str]:
    rejected = []
    changed = deepcopy(output)
    with_ids = [node for node in changed.iter() if node.get("id")]
    with_ids[1].set("id", with_ids[0].get("id"))
    rejected.append(expect_failure("duplicate-module-id", lambda: require(
        len([node.get('id') for node in changed.iter() if node.get('id')]) ==
        len({node.get('id') for node in changed.iter() if node.get('id')}), "duplicate")))

    changed = deepcopy(output)
    outer = content_child(changed, OUTER_ID)
    outer.insert(0, ET.Element(f"{{{C}}}title"))
    rejected.append(expect_failure("invented-outer-wrapper-title", lambda: compare_source(source_en, changed, "fixture")))

    changed = deepcopy(output)
    outer = content_child(changed, OUTER_ID)
    outer[0], outer[1] = outer[1], outer[0]
    rejected.append(expect_failure("outer-child-reorder", lambda: compare_source(source_en, changed, "fixture")))

    changed = deepcopy(output)
    changed.find(f".//{{{M}}}mn").text = "999"
    rejected.append(expect_failure("math-token-change", lambda: compare_source(source_en, changed, "fixture")))

    changed = deepcopy(output)
    first_mtext = next(changed.iter(f"{{{M}}}mtext"))
    first_mtext.text = (first_mtext.text or "") + "<∞௯"
    rejected.append(expect_failure(
        "math-mtext-payload-change",
        lambda: validate_bilingual_mathml_payload(source_en, source_id, changed),
    ))

    changed_math = deepcopy(next(output.iter(f"{{{M}}}math")))
    changed_math.append(ET.Element(f"{{{C}}}para"))
    rejected.append(expect_failure("foreign-element-inside-mathml", lambda: validate_mathml(changed_math)))

    changed_math = deepcopy(next(output.iter(f"{{{M}}}math")))
    changed_math.clear()
    malformed_fraction = ET.SubElement(changed_math, f"{{{M}}}mfrac")
    ET.SubElement(malformed_fraction, f"{{{M}}}mn").text = "1"
    rejected.append(expect_failure("unknown-malformed-mathml", lambda: validate_mathml(changed_math)))

    changed = deepcopy(output)
    prose_node = next(node for node in changed.iter()
                      if not node.tag.startswith(f"{{{M}}}") and (node.text or "").strip())
    prose_node.text = (prose_node.text or "") + " அழைக்கப்படாத உரை"
    rejected.append(expect_failure(
        "unexpected-prose",
        lambda: validate_exact_fragment_assembly(changed, fragment_roots, source_en),
    ))

    changed = deepcopy(output)
    prose_node = next(node for node in changed.iter()
                      if not node.tag.startswith(f"{{{M}}}") and (node.text or "").strip())
    prose_node.text = (prose_node.text or "") + "∞"
    rejected.append(expect_failure("unexpected-prose-math-symbol",
                                   lambda: compare_source(source_en, changed, "fixture")))

    changed = deepcopy(output)
    first_media, second_media = list(changed.iter(f"{{{C}}}media"))[:2]
    first_image = first_media.find(f"{{{C}}}image")
    second_image = second_media.find(f"{{{C}}}image")
    first_alt_value, second_alt_value = first_media.get("alt"), second_media.get("alt")
    first_src_value, second_src_value = first_image.get("src"), second_image.get("src")
    first_media.set("alt", second_alt_value)
    second_media.set("alt", first_alt_value)
    first_image.set("src", second_src_value)
    second_image.set("src", first_src_value)
    rejected.append(expect_failure("media-source-swap",
                                   lambda: compare_source(source_en, changed, "fixture")))

    changed = deepcopy(output)
    labelled_table = next(table for table in changed.iter(f"{{{C}}}table")
                          if table.get("aria-label") or table.get("summary"))
    labelled_table.attrib.pop("aria-label", None)
    labelled_table.attrib.pop("summary", None)
    rejected.append(expect_failure("table-accessible-label-removal",
                                   lambda: compare_source(source_en, changed, "fixture")))

    changed = deepcopy(output)
    source_omissions = solution_inventory(source_en)
    omitted_exercise_id = source_omissions[0]["exercise_id"]
    omitted_exercise = next(node for node in changed.iter(f"{{{C}}}exercise")
                            if node.get("id") == omitted_exercise_id)
    invented_solution = ET.SubElement(omitted_exercise, f"{{{C}}}solution")
    ET.SubElement(invented_solution, f"{{{C}}}para").text = "0"
    rejected.append(expect_failure(
        "invented-solution-for-source-omission",
        lambda: require(solution_inventory(changed) == source_omissions,
                        "Source solution omission changed"),
    ))

    changed = deepcopy(output)
    changed.find(f".//{{{C}}}content").append(
        ET.Element(f"{{{C}}}link", {"url": "https://example.invalid/unapproved"}))
    module_ids = {node.get("id") for node in changed.iter() if node.get("id")}
    rejected.append(expect_failure(
        "unexpected-nonlocal-link",
        lambda: validate_link_set(changed, module_ids, support_ids),
    ))

    changed_svg = deepcopy(first_svg)
    changed_svg.append(ET.Element(f"{{{SVG}}}script"))
    rejected.append(expect_failure("svg-script", lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.append(ET.Element(
        f"{{{SVG}}}handler",
        {"type": "application/ecmascript", "{http://www.w3.org/2001/xml-events}event": "click"},
    ))
    rejected.append(expect_failure(
        "svg-handler-event-content",
        lambda: validate_svg_root(changed_svg, "fixture", first_alt),
    ))

    changed_svg = deepcopy(first_svg)
    changed_svg.append(ET.Element(f"{{{SVG}}}foreignObject"))
    rejected.append(expect_failure("svg-foreign-object",
                                   lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    svg_with_ids = [node for node in changed_svg.iter() if node.get("id")]
    svg_with_ids[1].set("id", svg_with_ids[0].get("id"))
    rejected.append(expect_failure("duplicate-svg-id",
                                   lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.set(f"{{{XLINK}}}href", "https://example.invalid/image.svg")
    rejected.append(expect_failure("svg-external-href", lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.set("{http://www.w3.org/XML/1998/namespace}base", "https://example.invalid/")
    rejected.append(expect_failure("svg-xml-base", lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.append(ET.Element(f"{{{SVG}}}animate"))
    rejected.append(expect_failure("svg-animation", lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.set("style", "background-image:image-set('https://example.invalid/paint.svg' 1x)")
    rejected.append(expect_failure("svg-style-attribute", lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.set("fill", "url(https://example.invalid/paint.svg)")
    rejected.append(expect_failure("svg-external-css-url",
                                   lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    next(changed_svg.iter(f"{{{SVG}}}g")).set("aria-labelledby", "missing-svg-id")
    rejected.append(expect_failure("svg-unresolved-descendant-aria-reference",
                                   lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    changed_svg = deepcopy(first_svg)
    changed_svg.append(ET.Element(f"{{{SVG}}}style"))
    rejected.append(expect_failure("svg-style-element", lambda: validate_svg_root(changed_svg, "fixture", first_alt)))

    rejected.append(expect_failure(
        "svg-stylesheet-processing-instruction",
        lambda: validate_svg_bytes(
            b"<?xml-stylesheet href='https://example.invalid/a.css'?>\n" + first_svg_bytes,
            "fixture",
        ),
    ))
    rejected.append(expect_failure(
        "svg-declaration-free-stylesheet-processing-instruction",
        lambda: validate_svg_bytes(
            b"<?xml-stylesheet href='https://example.invalid/a.css'?>\n" +
            ET.tostring(first_svg, encoding="utf-8"),
            "fixture",
        ),
    ))
    rejected.append(expect_failure(
        "svg-dtd-entity-declaration",
        lambda: validate_svg_bytes(
            b"<!DOCTYPE svg [<!ENTITY payload 'active'>]>\n" + first_svg_bytes,
            "fixture",
        ),
    ))

    rejected.append(expect_failure("unreferenced-extra-asset", lambda: validate_asset_sets(
        set(EXPECTED_ASSETS), {*EXPECTED_ASSETS, "assets/u015/unreferenced.svg"})))
    rejected.append(expect_failure(
        "unexpected-scoped-asset-directory",
        lambda: require_no_scoped_asset_directories("assets/u015", {"assets/u015/unexpected-empty"}),
    ))
    fragment_path, fragment_digest = FRAGMENT_BY_ID["fs-id2601285"]
    mutated = fragment_path.read_bytes() + b"\n"
    rejected.append(expect_failure("changed-fragment-bytes", lambda: require(
        sha_bytes(mutated) == fragment_digest, "changed fragment")))
    first_asset, first_digest = next(iter(EXPECTED_ASSETS.items()))
    mutated = (LANG / first_asset).read_bytes() + b"\n"
    rejected.append(expect_failure("changed-asset-bytes", lambda: require(
        sha_bytes(mutated) == first_digest, "changed asset")))
    rejected.append(expect_failure(
        "extra-package-file",
        lambda: validate_package_file_set({*expected_package_files(), "unexpected.txt"}),
    ))
    rejected.append(expect_failure(
        "extra-package-directory",
        lambda: validate_package_tree(expected_package_files(),
                                      {*expected_package_directories(), "unexpected-empty"}),
    ))
    return rejected


def assemble() -> tuple[bytes, bytes, bytes, dict]:
    input_snapshot: dict[Path, str] = {}
    assembler_path = Path(__file__).resolve()
    assembler_digest = sha(assembler_path)
    input_snapshot[assembler_path] = assembler_digest
    validate_fragment_inventory()
    license_data = verify_pin(LICENSE_SOURCE[0], LICENSE_SOURCE[1], "license")
    attribution_source_data = verify_pin(
        ATTRIBUTION_SOURCE[0], ATTRIBUTION_SOURCE[1], "attribution source",
    )
    input_snapshot[LICENSE_SOURCE[0]] = LICENSE_SOURCE[1]
    input_snapshot[ATTRIBUTION_SOURCE[0]] = ATTRIBUTION_SOURCE[1]
    roots = {}
    for locale, (path, expected_digest) in WITNESSES.items():
        source_bytes = verify_pin(path, expected_digest, f"{locale} witness")
        roots[locale] = parse_pinned_bytes(source_bytes, rel_lang(path))
        input_snapshot[path] = expected_digest
    supporting_bytes = {}
    for module, (path, expected_digest) in SUPPORTING_MODULES.items():
        supporting_bytes[module] = verify_pin(path, expected_digest, f"supporting {module} source")
        input_snapshot[path] = expected_digest
    for label, (path, expected_digest) in CANON_EVIDENCE.items():
        verify_pin(path, expected_digest, f"canon evidence {label}")
        input_snapshot[path] = expected_digest
    fragment_bytes = {}
    for source_id, path, expected_digest in FRAGMENTS:
        fragment_bytes[source_id] = verify_pin(path, expected_digest, f"source fragment {source_id}")
        input_snapshot[path] = expected_digest

    expected_module_children = [f"{{{C}}}{name}" for name in ("title", "metadata", "content", "glossary")]
    for locale, root in roots.items():
        require([node.tag for node in root] == expected_module_children,
                f"Unexpected canonical module-level structure: {locale}")
        require(tuple(node.get("id") for node in root.find(f"{{{C}}}content")) == DIRECT_CONTENT_ORDER,
                f"Canonical direct content order changed: {locale}")
        outer = content_child(root, OUTER_ID)
        require(outer.tag == f"{{{C}}}section" and outer.get("class") == "section-exercises",
                f"Canonical outer section attributes changed: {locale}")
        require(outer.find(f"{{{C}}}title") is None, f"Canonical outer section unexpectedly gained a title: {locale}")
        require(tuple(node.get("id") for node in outer) == OUTER_CHILD_ORDER,
                f"Canonical outer child order changed: {locale}")

    fragment_roots: dict[str, ET.Element] = {}
    fragment_records = []
    for source_id, path, expected_digest in FRAGMENTS:
        target = parse_pinned_bytes(fragment_bytes[source_id], rel_lang(path))
        check_authored(target, rel_lang(path))
        fragment_roots[source_id] = target
        fragment_records.append({"source_id": source_id, "path": rel_lang(path),
                                 "sha256": expected_digest, "counts": fragment_count(target)})

    front = fragment_roots["frontmatter"]
    require(front.tag == f"{{{C}}}document" and
            [node.tag for node in front] == [f"{{{C}}}title", f"{{{C}}}metadata"],
            "Front matter must contain title and metadata only")
    for locale, root in roots.items():
        source_front = deepcopy(root)
        for child in list(source_front)[2:]:
            source_front.remove(child)
        compare_source(source_front, front, f"frontmatter/{locale}")

    for source_id in DIRECT_CONTENT_ORDER[:-1]:
        target = fragment_roots[source_id]
        for locale, root in roots.items():
            compare_source(content_child(root, source_id), target, f"{source_id}/{locale}")

    source_outer = content_child(roots["en"], OUTER_ID)
    outer = ET.Element(source_outer.tag, dict(source_outer.attrib))
    for source_id in OUTER_CHILD_ORDER:
        target = fragment_roots[source_id]
        for locale, root in roots.items():
            compare_source(outer_child(root, source_id), target, f"{source_id}/{locale}")
        outer.append(deepcopy(target))
    require(outer.find(f"{{{C}}}title") is None, "Assembler invented a title for fs-id2263283")
    for locale, root in roots.items():
        compare_source(content_child(root, OUTER_ID), outer, f"{OUTER_ID}/{locale}")

    glossary = fragment_roots["glossary"]
    require(glossary.tag == f"{{{C}}}glossary", "Wrong glossary fragment root")
    require(len(glossary.findall(f"{{{C}}}definition")) == 1, "Expected exactly one glossary definition")
    for locale, root in roots.items():
        compare_source(root.find(f"{{{C}}}glossary"), glossary, f"glossary/{locale}")

    output = deepcopy(front)
    content = ET.Element(f"{{{C}}}content", dict(roots["en"].find(f"{{{C}}}content").attrib))
    for source_id in DIRECT_CONTENT_ORDER[:-1]:
        content.append(deepcopy(fragment_roots[source_id]))
    content.append(outer)
    output.append(content)
    output.append(deepcopy(glossary))

    validate_exact_fragment_assembly(output, fragment_roots, roots["en"])
    for locale, root in roots.items():
        compare_source(root, output, f"complete-assembled-source/{locale}")
    validate_bilingual_mathml_payload(roots["en"], roots["id-ID"], output)
    validate_mathml(output)
    ids = [node.get("id") for node in output.iter() if node.get("id")]
    require(len(ids) == len(set(ids)), "Duplicate IDs in assembled source module")
    require(list(output.iter())[-1].get("id") == "fs-id1245763",
            "Glossary meaning fs-id1245763 is not the final source node")

    title = text(output.find(f"{{{C}}}title"))
    metadata_title = text(output.find(f"{{{C}}}metadata/{{{MD}}}title"))
    require(title == metadata_title == "முழு எண்களைக் கூட்டுதல்", "Root and metadata titles disagree")
    metadata = output.find(f"{{{C}}}metadata")
    require(text(metadata.find(f"{{{MD}}}content-id")) == "m81244", "Metadata content-id changed")
    require(text(metadata.find(f"{{{MD}}}uuid")) == "8069044b-6fb1-49bf-b03a-64988f9b1ddd",
            "Metadata UUID changed")
    objectives = metadata.findall(f"{{{MD}}}abstract/{{{C}}}list/{{{C}}}item")
    require(len(objectives) == 5 and all(text(node) for node in objectives),
            "Expected exactly five nonempty objectives")
    for objective, source_id in zip(objectives, OBJECTIVE_SECTION_ORDER):
        require(text(objective) == text(fragment_roots[source_id].find(f"{{{C}}}title")),
                f"Objective/section title mismatch: {source_id}")

    support_ids = {}
    for module, (path, _) in SUPPORTING_MODULES.items():
        supporting_root = parse_pinned_bytes(supporting_bytes[module], rel_lang(path))
        supporting_id_list = [node.get("id") for node in supporting_root.iter() if node.get("id")]
        require(len(supporting_id_list) == len(set(supporting_id_list)),
                f"Duplicate IDs in supporting module: {module}")
        support_ids[module] = set(supporting_id_list)
    links = validate_link_set(output, set(ids), support_ids)
    media_records, asset_pins, asset_bytes = validate_assets(output)
    input_snapshot.update(asset_pins)

    missing_solutions = solution_inventory(output)
    for locale, root in roots.items():
        require(solution_inventory(root) == missing_solutions,
                f"Source missing-solution inventory changed: {locale}")

    ET.register_namespace("", C)
    ET.register_namespace("m", M)
    ET.register_namespace("md", MD)
    source_data = ET.tostring(output, encoding="utf-8", xml_declaration=True) + b"\n"
    attribution_data = build_attribution_data(attribution_source_data)
    serialized = ET.fromstring(source_data)
    validate_exact_fragment_assembly(serialized, fragment_roots, roots["en"])
    for locale, root in roots.items():
        compare_source(root, serialized, f"serialized-assembly/{locale}")
    validate_bilingual_mathml_payload(roots["en"], roots["id-ID"], serialized)
    validate_mathml(serialized)

    first_media = next(output.iter(f"{{{C}}}media"))
    first_image = first_media.find(f"{{{C}}}image")
    first_asset = ((LANG / "translation") / first_image.get("src")).resolve()
    first_svg_bytes = asset_bytes[first_asset]
    negative_tests = run_negative_fixtures(
        output, roots["en"], roots["id-ID"], parse_pinned_bytes(first_svg_bytes, rel_lang(first_asset)),
        first_media.get("alt"), first_svg_bytes, support_ids, fragment_roots,
    )

    for path, expected_digest in input_snapshot.items():
        verify_pin(path, expected_digest, "snapshotted assembly input")
    validate_fragment_inventory()
    final_asset_inventory = scan_scoped_asset_inventory("final scoped asset directory")
    validate_asset_sets(set(EXPECTED_ASSETS), final_asset_inventory)

    counts = fragment_count(output)
    counts.update({
        "direct_content_children": len(list(content)),
        "outer_section_children": len(list(outer)),
        "objectives": len(objectives),
        "glossary_definitions": len(glossary.findall(f"{{{C}}}definition")),
        "source_exercises_without_solutions": len(missing_solutions),
        "canonical_external_reference_links": len(EXPECTED_EXTERNAL_URLS),
        "module_and_cross_module_target_links": sum("target_id" in record for record in links),
        "unique_svg_assets": len(EXPECTED_ASSETS),
        "unique_svg_ids": sum(record["svg_ids"] for record in media_records),
    })
    manifest = {
        "schema_version": 1,
        "status": "complete-m81244-source-review-package-structurally-verified-not-learner-workflow",
        "module": "m81244", "locale": LOCALE,
        "all_canonical_source_nodes_included": True,
        "source_text_inventory_complete": True,
        "whole_assignment_complete": False,
        "learner_workflow_complete": False,
        "publication_ready": False,
        "witnesses": {rel_lang(path): digest for path, digest in WITNESSES.values()},
        "supporting_cross_module_target_sources": {
            module: {"path": rel_lang(path), "sha256": digest}
            for module, (path, digest) in SUPPORTING_MODULES.items()
        },
        "canon_consultation_evidence": {
            label: {"workspace_path": rel_repo(path), "sha256": digest}
            for label, (path, digest) in CANON_EVIDENCE.items()
        },
        "canon_consultation_scope": [
            "C11/PDF page 36: visually resolved கூடுதல் as an addition result; OCR கூருதல் is not trusted",
            "C17/PDF page 38: additive identity and the visually resolved கூட்டல் சமனி wording",
            "C18/PDF page 46: perimeter/boundary-length versus area and application register",
            "C12/PDF page 175: குறியீடு, கூட்டல் சமனி, முழு எண்கள் and முழுக்கள் glossary distinctions",
        ],
        "license_and_attribution": {
            "license": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
            "package_license": {"path": "LICENSE.txt", "sha256": LICENSE_SOURCE[1]},
            "source_work": "OpenStax Prealgebra 2e, module m81244 (Add Whole Numbers)",
            "publisher": "OpenStax, Rice University",
            "senior_contributing_authors": [
                "Lynn Marecek", "MaryAnne Anthony-Smith", "Andrea Honeycutt Mathis",
            ],
            "complete_author_and_reviewer_credit_extract": {
                "path": "ATTRIBUTION.en.cnxml", "section_id": ATTRIBUTION_SECTION_ID,
                "sha256": sha_bytes(attribution_data),
                "derived_without_content_changes_from": rel_lang(ATTRIBUTION_SOURCE[0]),
                "source_sha256": ATTRIBUTION_SOURCE[1],
            },
            "canonical_source": (
                "OpenStax canonical bundle commit 38cae454e644abf9f0a623e876994553881597c9, "
                "modules/m81244/index.cnxml"
            ),
            "comparison_source": (
                "Indonesian A00 commit 3de9207f56f8b5c57c017abf973fb04e00d740f1, "
                "modules/m81244/index.cnxml"
            ),
            "modification_notice": (
                "Unofficial Indian Tamil translation and Tamil SVG redraws; source IDs, structure, "
                "mathematics, and documented source omissions are preserved."
            ),
            "no_endorsement": "No OpenStax, Rice University, contributor, native-speaker, or educator endorsement is claimed.",
        },
        "assembler": {"path": rel_lang(assembler_path), "sha256": assembler_digest},
        "fragments_in_canonical_order": fragment_records,
        "canonical_structure": {
            "document_children": ["title", "metadata", "content", "glossary"],
            "direct_content_ids": list(DIRECT_CONTENT_ORDER),
            "outer_section": {"id": OUTER_ID, "class": "section-exercises",
                              "has_direct_title": False, "child_ids": list(OUTER_CHILD_ORDER)},
            "final_document_node_id": "fs-id1245763",
        },
        "assembled_source": {"path": "source/m81244.cnxml", "bytes": len(source_data),
                             "sha256": sha_bytes(source_data)},
        "counts": counts,
        "checks": {
            "all_fragment_and_asset_hashes_pinned": "pass",
            "exact_m81244_fragment_filename_inventory": "pass",
            "exact_pinned_tamil_fragment_subtrees_no_unexpected_prose": "pass",
            "both_witnesses_full_tree_and_stable_attributes": "pass",
            "both_witnesses_mathml_structure_and_witness_matched_payload": "pass",
            "module_specific_mathml_vocabulary_and_content_models": "pass",
            "ordered_source_numeral_math_currency_symbols": "pass",
            "module_ids_unique_and_source_order_preserved": "pass",
            "titleless_outer_wrapper_and_four_child_order": "pass",
            "module_qualified_target_links_resolved": "pass",
            "canonical_external_urls_exact_allowlist_only": "pass",
            "scoped_asset_directories_no_missing_extra_unreferenced_files": "pass",
            "asset_inventory_rechecked_after_input_snapshot": "pass",
            "media_ids_preserve_canonical_figure_basename_identity": "pass",
            "all_svg_descriptions_match_current_media_alternatives": "pass",
            "all_svg_ids_unique_and_no_active_external_content_or_raw_xml_directives": "pass",
            "review_package_regular_files_only_no_reparse_traversal": "pass",
            "license_and_full_author_reviewer_attribution_retained": "pass",
            "source_solution_presence_and_omissions_unchanged": "pass",
            "serialized_output_reparsed_and_recompared": "pass",
            "negative_fixtures_rejected": negative_tests,
        },
        "links": links,
        "assets": media_records,
        "missing_solution_inventory": missing_solutions,
        "missing_solution_policy": (
            "These source exercises have no solution node in both witnesses. They remain unchanged and are not "
            "admitted as teacher-independent assessments. Answers/reasoning belong in a separately marked companion."
        ),
        "limits": [
            "This package is complete source-node assembly for m81244 only, not completion of A00, A10, A20, AX-1, AX-3, or the Grades 2-8 Tamil recovery assignment.",
            "It is a CNXML/source-asset review package, not a rendered HTML reader, EPUB, PDF, diagnostic, mastery gate, or answer-complete companion.",
            "The source confidence self-check is preserved but is not treated as demonstrated mastery or executable placement.",
            "Three exact canonical OpenStax web references are preserved as source references; they are not packaged offline runtime dependencies. Every media dependency is local and hash-pinned.",
            "Structural, numeric, link, and SVG closure checks do not constitute native-speaker, educator, learner, assistive-technology, board-alignment, grade-placement, or efficacy approval.",
            "Source exercises without solutions remain explicit omissions; this source-only package is not independently answer-complete.",
        ],
    }
    return source_data, attribution_data, license_data, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-only", action="store_true",
                      help="Validate pinned candidate inputs without reading or writing the review package")
    mode.add_argument("--check", action="store_true",
                      help="Validate inputs and require exact existing review-package bytes")
    args = parser.parse_args()
    check_lock: bytes | None = None
    try:
        package_before = None
        if args.check:
            check_lock = acquire_build_lock()
        try:
            if args.check:
                assert_no_retained_stages()
                package_before = package_snapshot()
            source_data, attribution_data, license_data, manifest = assemble()
            manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            if args.check:
                verify_package(source_data, attribution_data, license_data, manifest_data)
                require(package_snapshot() == package_before,
                        "Review package changed during transaction-locked --check")
                assert_no_retained_stages()
                mode_name = "checked-stable-existing-package"
            elif args.check_only:
                mode_name = "checked-candidate-inputs-only"
            else:
                write_package(source_data, attribution_data, license_data, manifest_data)
                mode_name = "assembled-review-package"
            result = {
                "mode": mode_name, "status": manifest["status"],
                "assembled_source": manifest["assembled_source"],
                "counts": manifest["counts"],
                "negative_fixtures_rejected": len(manifest["checks"]["negative_fixtures_rejected"]),
                "whole_assignment_complete": False,
            }
        finally:
            if check_lock is not None:
                release_build_lock(check_lock)
                check_lock = None
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (AssemblyError, OSError, ET.ParseError) as exc:
        print(f"ASSEMBLY FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
