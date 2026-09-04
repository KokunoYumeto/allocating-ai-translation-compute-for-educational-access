"""Compile the finite, complete m81268 narration contract.

This is a module-specific review compiler, not a production speech parser.  It
accepts only the exact pinned m81268 source, exact reviewed target replay, and
the finite token/structure inventory below.  Its output records every expected
reading explicitly; production dispatch performs exact occurrence lookup only.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import xml.etree.ElementTree as ET

from build import CN, MATH
from config import LANG, TRACKS
from safe_io import write_bytes
from use_algebra_common import (
    ASSETS_SHA256,
    CANON_LOCK_SHA256,
    CANON_TARGET_REVISIONS,
    EDITS_SHA256,
    EN_COMMIT,
    EN_SHA256,
    EXPECTED,
    ID_COMMIT,
    ID_SHA256,
    MODULE,
    UNIT,
    asset_maps,
    build_variants,
    local,
    sha,
    tree_key,
    tree_sha,
)

OUTPUT = f"audio/{UNIT}.rules.json"

GROUPS = (
    ("outer-title", (0,)),
    ("objectives", (1, 2)),
    ("readiness-addition", (2, 0)),
    ("readiness-multiplication", (2, 1)),
    ("readiness-division", (2, 2)),
    ("variables-symbols", (2, 3)),
    ("expressions-equations", (2, 4)),
    ("exponents", (2, 5)),
    ("order-of-operations", (2, 6)),
    ("key-concepts", (2, 7)),
    ("practice-review", (2, 8)),
    ("glossary", (3,)),
)

# Empty CNXML links have no fallback text.  Their finite labels were reviewed
# against the exact target node or referenced lesson named by each occurrence.
EMPTY_LINK_CUES = {
    1: {"id-academic": "bagian Menjumlahkan Bilangan Cacah",
        "jv-academic": "bagean Nambah Wilangan Cacah",
        "jv-conversation": "bagean Nambah Wilangan Cacah"},
    2: {"id-academic": "bagian Mengalikan Bilangan Cacah",
        "jv-academic": "bagean Ngepingake Wilangan Cacah",
        "jv-conversation": "bagean Ngepingake Wilangan Cacah"},
    3: {"id-academic": "bagian Membagi Bilangan Cacah",
        "jv-academic": "bagean Mara Wilangan Cacah",
        "jv-conversation": "bagean Mara Wilangan Cacah"},
    4: {"id-academic": "tabel usia Greg dan Alex",
        "jv-academic": "tabel umur Greg lan Alex",
        "jv-conversation": "tabel umur Greg lan Alex"},
    6: {"id-academic": "tabel simbol kesamaan dan pertidaksamaan",
        "jv-academic": "tabel simbol pepadhan lan pertidaksamaan",
        "jv-conversation": "tabel tandha pepadhan lan pertidaksamaan"},
    7: {"id-academic": "gambar efisiensi bahan bakar mobil",
        "jv-academic": "gambar efisiensi bahan bakar mobil",
        "jv-conversation": "gambar efisiensi bahan bakar mobil"},
    8: {"id-academic": "gambar efisiensi bahan bakar mobil",
        "jv-academic": "gambar efisiensi bahan bakar mobil",
        "jv-conversation": "gambar efisiensi bahan bakar mobil"},
    9: {"id-academic": "gambar efisiensi bahan bakar mobil",
        "jv-academic": "gambar efisiensi bahan bakar mobil",
        "jv-conversation": "gambar efisiensi bahan bakar mobil"},
    10: {"id-academic": "tabel simbol pengelompokan",
         "jv-academic": "tabel simbol panglumpukan",
         "jv-conversation": "tabel tandha panglumpukan"},
    11: {"id-academic": "tabel notasi eksponen",
         "jv-academic": "tabel notasi eksponen",
         "jv-conversation": "tabel notasi eksponen"},
}

SELECTED_BLOCK_TAGS = {
    "title", "para", "problem", "solution", "table", "figure",
    "equation", "media", "item", "definition", "note",
}


def node_at(root: ET.Element, path) -> ET.Element:
    node = root
    for index in path:
        node = node[index]
    return node


def path_maps(root: ET.Element):
    by_node, by_path = {}, {}

    def walk(node, path):
        by_node[id(node)] = tuple(path)
        by_path[tuple(path)] = node
        for index, child in enumerate(node):
            walk(child, path + (index,))

    walk(root, ())
    return by_node, by_path


def element_xml(node: ET.Element) -> str:
    copy_node = copy.deepcopy(node)
    copy_node.tail = None
    return ET.tostring(copy_node, encoding="unicode")


def _under_metadata_identity(node, parents):
    while node in parents:
        if local(node) in ("content-id", "uuid"):
            return True
        node = parents[node]
    return local(node) in ("content-id", "uuid")


def cardinal(value: str, jv: bool) -> str:
    """Compile one finite observed integer; no runtime caller uses this."""
    if not re.fullmatch(r"[0-9]{1,3}(?:,[0-9]{3})*|[0-9]+", value):
        raise ValueError("Unregistered m81268 integer syntax: " + value)
    number = int(value.replace(",", ""))
    small_jv = ("nol", "siji", "loro", "telu", "papat", "lima",
                "enem", "pitu", "wolu", "sanga")
    small_id = ("nol", "satu", "dua", "tiga", "empat", "lima",
                "enam", "tujuh", "delapan", "sembilan")
    small = small_jv if jv else small_id

    def under_thousand(n):
        if n < 10:
            return small[n]
        if n == 10:
            return "sepuluh"
        if n == 11:
            return "sewelas" if jv else "sebelas"
        if n < 20:
            if jv:
                return {12: "rolas", 13: "telulas", 14: "patbelas",
                        15: "limalas", 16: "nembelas", 17: "pitulas",
                        18: "wolulas", 19: "sangalas"}[n]
            return small[n - 10] + " belas"
        if n < 30 and jv and n > 20:
            return {21: "selikur", 22: "rolikur", 23: "telulikur",
                    24: "patlikur", 25: "salawé", 26: "nemlikur",
                    27: "pitulikur", 28: "wolulikur", 29: "sangalikur"}[n]
        if n < 100:
            if jv:
                tens = {2: "rong puluh", 3: "telung puluh", 4: "patang puluh",
                        5: "sèket", 6: "sewidak", 7: "pitung puluh",
                        8: "wolung puluh", 9: "sangang puluh"}[n // 10]
            else:
                tens = small[n // 10] + " puluh"
            return tens + ((" " + small[n % 10]) if n % 10 else "")
        if n < 1000:
            if jv:
                hundreds = ("satus" if n // 100 == 1 else
                            {2: "rong", 3: "telung", 4: "patang", 5: "limang",
                             6: "nem", 7: "pitung", 8: "wolung", 9: "sangang"}[n // 100]
                            + " atus")
            else:
                hundreds = "seratus" if n // 100 == 1 else small[n // 100] + " ratus"
            return hundreds + ((" " + under_thousand(n % 100)) if n % 100 else "")
        raise ValueError("Internal cardinal range")

    if number < 1000:
        return under_thousand(number)
    if number < 1_000_000:
        high, low = divmod(number, 1000)
        thousands = (("sewu" if high == 1 else under_thousand(high) + " éwu")
                     if jv else
                     ("seribu" if high == 1 else under_thousand(high) + " ribu"))
        return thousands + ((" " + under_thousand(low)) if low else "")
    raise ValueError("Observed m81268 number exceeds finite compiler range")


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?![A-Za-z0-9])")


def finite_number_lexicon(variants):
    values = set()
    for root in variants.values():
        parents = {child: parent for parent in root.iter() for child in parent}
        for node in root.iter():
            if _under_metadata_identity(node, parents):
                continue
            for value in (node.text, node.tail, node.get("alt"),
                          node.get("aria-label"), node.get("summary")):
                if value:
                    values.update(match.group(0) for match in NUMBER_PATTERN.finditer(value))
    # Grouped MathML can split the high/low groups around a comma operator.
    values.update(("180,096", "7,263"))
    return {
        value: {
            "id-academic": cardinal(value, False),
            "jv-academic": cardinal(value, True),
            "jv-conversation": cardinal(value, True),
        }
        for value in sorted(values, key=lambda item: (int(item.replace(",", "")), item))
    }


def normalized(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([,.;:?!])", r"\1", value)
    value = re.sub(r"([,;:])(?=[^\s,;:])", r"\1 ", value)
    value = re.sub(r"\.{2,}", ".", value)
    return value.strip(" ;")


def spoken_text(value: str | None, track: str, numbers) -> str:
    if not value or not value.strip():
        return ""
    jv = track.startswith("jv")
    labels = ({"ⓐ": "bagean a. ", "ⓑ": "bagean bé. ", "ⓒ": "bagean cé. ",
               "ⓓ": "bagean dé. ", "ⓔ": "bagean é. "}
              if jv else
              {"ⓐ": "bagian a. ", "ⓑ": "bagian be. ", "ⓒ": "bagian ce. ",
               "ⓓ": "bagian de. ", "ⓔ": "bagian e. "})
    for marker, cue in labels.items():
        value = value.replace(marker, cue)
    value = value.replace("…", " lan sateruse " if jv else " dan seterusnya ")
    value = re.sub(r"_{2,}", " garis kosong " if jv else " garis kosong ", value)
    value = NUMBER_PATTERN.sub(lambda match: numbers[match.group(0)][track], value)
    replacements = (
        ("≠", " ora padha karo " if jv else " tidak sama dengan "),
        ("≤", " luwih cilik utawa padha karo " if jv else " kurang dari atau sama dengan "),
        ("≥", " luwih gedhé utawa padha karo " if jv else " lebih besar dari atau sama dengan "),
        ("÷", " dipara " if jv else " dibagi "),
        ("−", " dikurangi "), ("×", " ping " if jv else " dikali "),
        ("⋅", " ping " if jv else " dikali "),
        ("·", " ping " if jv else " dikali "),
        ("+", " ditambah "),
        ("<", " luwih cilik tinimbang " if jv else " kurang dari "),
        (">", " luwih gedhé tinimbang " if jv else " lebih besar dari "),
        ("=", " padha karo " if jv else " sama dengan "),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    return normalized(value)


def letter(value: str, track: str) -> str:
    names = {"a": "a", "b": "be", "c": "ce", "g": "ge", "h": "ha",
             "m": "em", "n": "en", "p": "pe", "q": "ku", "t": "te",
             "x": "eks", "y": "ye"}
    if value not in names:
        raise ValueError("Unregistered m81268 letter: " + repr(value))
    return ("aksara " if track.startswith("jv") else "huruf ") + names[value]


def special_math(ordinal: int, track: str) -> str | None:
    jv = track.startswith("jv")
    if ordinal in (39, 305):
        if jv:
            return ("Aksara a dipara aksara be; aksara a garis miring aksara be; "
                    "pecahan aksara a per aksara be, pungkasan pecahan; lan aksara a "
                    "dipara aksara be kanthi notasi paran susun.")
        return ("Huruf a dibagi huruf be; huruf a garis miring huruf be; pecahan "
                "huruf a per huruf be, akhir pecahan; dan huruf a dibagi huruf be "
                "dengan notasi pembagian bersusun.")
    if ordinal == 109:
        if jv:
            intro = "Minangka tuladha" if track == "jv-academic" else "Dadi tuladha"
            return normalized(
                "Aksara a luwih cilik tinimbang aksara be padha karo aksara be luwih gedhé "
                f"tinimbang aksara a. {intro}, pitu luwih cilik tinimbang sewelas padha karo "
                "sewelas luwih gedhé tinimbang pitu. Larik kapindho. Aksara a luwih gedhé "
                "tinimbang aksara be padha karo aksara be luwih cilik tinimbang aksara a. "
                f"{intro}, pitulas luwih gedhé tinimbang papat padha karo papat luwih cilik "
                "tinimbang pitulas.")
        return normalized(
            "Huruf a kurang dari huruf be setara dengan huruf be lebih besar dari huruf a. "
            "Sebagai contoh, tujuh kurang dari sebelas setara dengan sebelas lebih besar "
            "dari tujuh. Baris kedua. Huruf a lebih besar dari huruf be setara dengan huruf "
            "be kurang dari huruf a. Sebagai contoh, tujuh belas lebih besar dari empat "
            "setara dengan empat kurang dari tujuh belas.")
    if ordinal == 222:
        return ("Aksara en kanthi superskrip aksara te aksara ha, panandha urutan basa Inggris."
                if jv else
                "Huruf en dengan superskrip huruf te huruf ha, penanda urutan bahasa Inggris.")
    if ordinal == 225:
        join = "diwaca minangka" if track == "jv-academic" else "diwaca dadi"
        if not jv:
            join = "dibaca sebagai"
        end = "pungkasan pangkat" if jv else "akhir pangkat"
        return normalized(
            f"{letter('a', track)} pangkat loro, {end}, {join} {letter('a', track)} kuadrat. "
            f"{letter('a', track)} pangkat telu, {end}, {join} {letter('a', track)} kubik."
            if jv else
            f"{letter('a', track)} pangkat dua, {end}, {join} {letter('a', track)} kuadrat. "
            f"{letter('a', track)} pangkat tiga, {end}, {join} {letter('a', track)} kubik.")
    if ordinal == 273:
        if jv:
            return normalized(
                "Sawetara murid nggawe luwih prasaja dadi patang puluh sanga. Cara kapisan. "
                "Papat ditambah telu ping pitu. Amarga papat ditambah telu ngasilake pitu. "
                "Pitu ping pitu. Lan pitu ping pitu padha karo patang puluh sanga. "
                "Sawetara murid nggawe luwih prasaja dadi salawé. Cara kapindho. Papat "
                "ditambah telu ping pitu. Amarga telu ping pitu padha karo selikur. Papat "
                "ditambah selikur. Lan selikur ditambah papat ngasilake salawé.")
        return normalized(
            "Sebagian siswa menyederhanakannya menjadi empat puluh sembilan. Cara pertama. "
            "Empat ditambah tiga dikali tujuh. Karena empat ditambah tiga menghasilkan tujuh. "
            "Tujuh dikali tujuh. Dan tujuh dikali tujuh sama dengan empat puluh sembilan. "
            "Sebagian siswa menyederhanakannya menjadi dua puluh lima. Cara kedua. Empat "
            "ditambah tiga dikali tujuh. Karena tiga dikali tujuh sama dengan dua puluh satu. "
            "Empat ditambah dua puluh satu. Dan dua puluh satu ditambah empat menghasilkan "
            "dua puluh lima.")
    return None


def _significant_children(node):
    return [child for child in node if local(child) != "mspace"]


def _starts_operand(node):
    tag = local(node)
    if tag in ("mn", "mi", "msup", "mfrac", "menclose"):
        return True
    if tag == "mo":
        return (node.text or "") in ("(", "[", "{")
    if tag == "mrow":
        children = _significant_children(node)
        return bool(children) and _starts_operand(children[0])
    return False


def _ends_operand(node):
    tag = local(node)
    if tag in ("mn", "mi", "msup", "mfrac", "menclose"):
        return True
    if tag == "mo":
        return (node.text or "") in (")", "]", "}")
    if tag == "mrow":
        children = _significant_children(node)
        return bool(children) and _ends_operand(children[-1])
    return False


def speak_mtext(value: str, track: str, numbers) -> str:
    jv = track.startswith("jv")
    exact = {
        '"': "", "”": "",
        "(2+6)": ("bukak kurung biasa loro ditambah enem tutup kurung biasa" if jv else
                   "buka kurung biasa dua ditambah enam tutup kurung biasa"),
        "(3+8)": ("bukak kurung biasa telu ditambah wolu tutup kurung biasa" if jv else
                   "buka kurung biasa tiga ditambah delapan tutup kurung biasa"),
        "(=": ("bukak kurung biasa padha karo" if jv else "buka kurung biasa sama dengan"),
        ">)": ("luwih gedhé tinimbang tutup kurung biasa" if jv else
                "lebih besar dari tutup kurung biasa"),
        "<": "luwih cilik tinimbang" if jv else "kurang dari",
        ">": "luwih gedhé tinimbang" if jv else "lebih besar dari",
        "=": "padha karo" if jv else "sama dengan",
        "“<”": "tandha luwih cilik tinimbang" if jv else "tanda kurang dari",
        "“>”": "tandha luwih gedhé tinimbang" if jv else "tanda lebih besar dari",
        "≠,": "ora padha karo" if jv else "tidak sama dengan",
        "kuadrat\"": "kuadrat", "kubik\"": "kubik",
    }
    if value in exact:
        return exact[value]
    match = re.fullmatch(r"([0-9]{2})″", value)
    if match:
        return numbers[match.group(1)][track] + " inci"
    match = re.fullmatch(r"([0-9]{1,3}(?:,[0-9]{3})+)′", value)
    if match:
        return numbers[match.group(1)][track] + (" foot" if jv else " kaki")
    return spoken_text(value, track, numbers)


def speak_math(node: ET.Element, track: str, numbers, ordinal: int) -> str:
    special = special_math(ordinal, track)
    if special is not None and local(node) == "math":
        return special
    jv = track.startswith("jv")

    def speak(current):
        tag = local(current)
        if tag == "mn":
            if current.text not in numbers:
                raise ValueError("Unregistered finite m81268 numeral: " + repr(current.text))
            return numbers[current.text][track]
        if tag == "mi":
            return letter(current.text or "", track)
        if tag == "mtext":
            return speak_mtext(current.text or "", track, numbers)
        if tag == "mo":
            value = current.text or ""
            words = {
                "+": "ditambah", "−": "dikurangi", "-": "dikurangi",
                "·": "ping" if jv else "dikali",
                "⋅": "ping" if jv else "dikali",
                "×": "ping" if jv else "dikali",
                "÷": "dipara" if jv else "dibagi",
                "/": "dipara" if jv else "dibagi",
                "=": "padha karo" if jv else "sama dengan",
                "≠": "ora padha karo" if jv else "tidak sama dengan",
                "<": "luwih cilik tinimbang" if jv else "kurang dari",
                ">": "luwih gedhé tinimbang" if jv else "lebih besar dari",
                "≤": "luwih cilik utawa padha karo" if jv else "kurang dari atau sama dengan",
                "≥": "luwih gedhé utawa padha karo" if jv else "lebih besar dari atau sama dengan",
                "(": "bukak kurung biasa" if jv else "buka kurung biasa",
                ")": "tutup kurung biasa",
                "[": "bukak kurung siku" if jv else "buka kurung siku",
                "]": "tutup kurung siku",
                "{": "bukak kurung kurawal" if jv else "buka kurung kurawal",
                "}": "tutup kurung kurawal",
                ",": ";", ".": ".",
            }
            if value not in words:
                raise ValueError("Unregistered m81268 operator: " + repr(value))
            return words[value]
        if tag == "mspace":
            width = current.get("width")
            if width not in ("0.2em", "0.4em", "0.5em", "2em", "4em"):
                raise ValueError("Unregistered m81268 spacing: " + repr(width))
            return ("ekspresi sabanjure" if jv else "ekspresi berikutnya") if width == "4em" else ""
        if tag == "msup":
            if len(current) != 2:
                raise ValueError("Changed m81268 power arity")
            end = "pungkasan pangkat" if jv else "akhir pangkat"
            return normalized(f"{speak(current[0])} pangkat {speak(current[1])}, {end}")
        if tag == "mfrac":
            if len(current) != 2:
                raise ValueError("Changed m81268 fraction arity")
            end = "pungkasan pecahan" if jv else "akhir pecahan"
            return normalized(f"pecahan {speak(current[0])} per {speak(current[1])}, {end}")
        if tag == "menclose":
            if current.get("notation") != "longdiv" or len(current) != 1:
                raise ValueError("Changed m81268 long-division notation")
            return (("notasi paran susun " if jv else "notasi pembagian bersusun ")
                    + speak(current[0]))
        if tag in ("math", "mrow"):
            children = list(current)
            significant = _significant_children(current)
            if (len(significant) == 2 and local(significant[0]) == local(significant[1]) == "mo"
                    and (significant[0].text, significant[1].text) in
                    (("(", ")"), ("[", "]"), ("{", "}"))):
                first, second = significant
                return normalized(speak(first) + (" kosong " if jv else " kosong ") + speak(second))
            parts, previous = [], None
            index = 0
            while index < len(children):
                child = children[index]
                if (index + 2 < len(children) and local(child) == "mn"
                        and local(children[index + 1]) == "mo"
                        and children[index + 1].text == ","
                        and local(children[index + 2]) == "mn"
                        and len(children[index + 2].text or "") == 3):
                    joined = (child.text or "") + "," + (children[index + 2].text or "")
                    if joined not in numbers:
                        raise ValueError("Unregistered grouped m81268 integer: " + joined)
                    if previous is not None and _ends_operand(previous):
                        parts.append("ping" if jv else "dikali")
                    parts.append(numbers[joined][track])
                    previous = children[index + 2]
                    index += 3
                    continue
                if local(child) == "mspace":
                    spacing = speak(child)
                    if spacing:
                        parts.extend((";", spacing, ";"))
                        previous = None
                    index += 1
                    continue
                if previous is not None and _ends_operand(previous) and _starts_operand(child):
                    parts.append("ping" if jv else "dikali")
                part = speak(child)
                if part:
                    parts.append(part)
                previous = child
                index += 1
            return normalized(" ".join(parts))
        if tag in ("mtable", "mtr", "mtd"):
            raise ValueError("Unregistered m81268 layout outside finite whole-layout fixture")
        raise ValueError("Unregistered m81268 MathML element: " + tag)

    result = normalized(speak(node))
    if not result:
        raise ValueError(f"Empty MathML reading M{ordinal:03d}")
    return result


def link_ordinals(root):
    return {id(node): ordinal for ordinal, node in enumerate(root.iter("{" + CN + "}link"), 1)}


def speak_element(node: ET.Element, track: str, numbers, math_by_node,
                  link_by_node, solution_cue=True) -> str:
    tag = local(node)
    if node.tag.startswith("{" + MATH + "}"):
        if tag != "math" or id(node) not in math_by_node:
            raise ValueError("Detached/nonroot MathML narration request")
        return math_by_node[id(node)]
    if tag == "image":
        return ""
    if tag == "media":
        value = node.get("alt")
        if not value:
            raise ValueError("m81268 media lacks finite alt")
        return spoken_text(value, track, numbers)
    if tag == "table":
        value = node.get("aria-label") or node.get("summary")
        if not value:
            raise ValueError("m81268 table lacks finite accessible description")
        return spoken_text(value, track, numbers)
    if tag == "link":
        text_value = normalized(" ".join(
            part for part in [spoken_text(node.text, track, numbers)] + [
                speak_element(child, track, numbers, math_by_node, link_by_node)
                + " " + spoken_text(child.tail, track, numbers)
                for child in node] if part))
        if text_value:
            return text_value
        if id(node) not in link_by_node:
            raise ValueError("Unregistered empty m81268 link")
        return link_by_node[id(node)]
    if tag == "sup":
        content = spoken_text(node.text, track, numbers)
        for child in node:
            content += " " + speak_element(child, track, numbers, math_by_node, link_by_node)
            content += " " + spoken_text(child.tail, track, numbers)
        end = "pungkasan pangkat" if track.startswith("jv") else "akhir pangkat"
        return normalized("pangkat " + content + ", " + end)
    if tag == "newline":
        return "."
    if tag == "definition":
        term = node.find("{*}term")
        meaning = node.find("{*}meaning")
        if term is None or meaning is None:
            raise ValueError("Changed m81268 definition structure")
        first = speak_element(term, track, numbers, math_by_node, link_by_node)
        second = speak_element(meaning, track, numbers, math_by_node, link_by_node)
        return normalized(("Tembung " if track.startswith("jv") else "Istilah ")
                          + first + (". Tegese, " if track.startswith("jv") else ". Artinya, ")
                          + second)

    parts = [spoken_text(node.text, track, numbers)]
    for child in node:
        parts.append(speak_element(child, track, numbers, math_by_node, link_by_node))
        parts.append(spoken_text(child.tail, track, numbers))
    result = normalized(" ".join(part for part in parts if part))
    if tag == "problem":
        result = normalized(("Pitakon. " if track.startswith("jv") else "Pertanyaan. ") + result)
    elif tag == "solution" and solution_cue and node.find("{*}title") is None:
        result = normalized(("Wangsulan. " if track.startswith("jv") else "Jawaban. ") + result)
    return result


def choose_blocks(source, path_by_node):
    selected = []

    def walk(node):
        if local(node) in SELECTED_BLOCK_TAGS:
            selected.append(path_by_node[id(node)])
            return
        for child in node:
            walk(child)

    for _name, path in GROUPS:
        walk(node_at(source, path))
    if len(selected) != len(set(selected)):
        raise ValueError("Duplicate m81268 narration block path")
    return selected


def make_rules():
    source, variants, edits, assets, indonesian_raw, english_raw = build_variants()
    asset_maps(variants, assets)
    numbers = finite_number_lexicon(variants)
    source_paths, source_by_path = path_maps(source)
    variant_by_path = {track: path_maps(root)[1] for track, root in variants.items()}
    ordered_ids = [node.get("id") for node in source.iter() if node.get("id")]
    id_order = {value: index for index, value in enumerate(ordered_ids)}

    source_maths = list(source.iter("{" + MATH + "}math"))
    target_maths = {track: list(root.iter("{" + MATH + "}math"))
                    for track, root in variants.items()}
    math_fixtures = []
    math_expected_by_track = {track: {} for track in TRACKS}
    for ordinal, source_math in enumerate(source_maths, 1):
        path = source_paths[id(source_math)]
        expected = {}
        target_hashes = {}
        for track in TRACKS:
            target_math = variant_by_path[track][path]
            expected[track] = speak_math(target_math, track, numbers, ordinal)
            target_hashes[track] = tree_sha(target_math)
            math_expected_by_track[track][id(target_math)] = expected[track]
        math_fixtures.append({
            "id": f"A00-ALG-M{ordinal:03d}",
            "ordinal": ordinal,
            "module": MODULE,
            "source_path": list(path),
            "direct_group": next(name for name, group_path in GROUPS
                                 if path[:len(group_path)] == group_path),
            "source_mathml": element_xml(source_math),
            "source_tree": tree_key(source_math),
            "source_tree_sha256": tree_sha(source_math),
            "variant_tree_sha256": target_hashes,
            "expected": expected,
            "semantic_witness": {
                "tags": [local(node) for node in source_math.iter()],
                "operators": [node.text for node in source_math.iter("{" + MATH + "}mo")],
                "mspace_widths": [node.get("width") for node in source_math.iter("{" + MATH + "}mspace")],
            },
            "runtime_dispatch": "exact_live_occurrence_only",
        })

    source_links = list(source.iter("{" + CN + "}link"))
    link_fixtures = []
    link_expected_by_track = {track: {} for track in TRACKS}
    for ordinal, source_link in enumerate(source_links, 1):
        path = source_paths[id(source_link)]
        expected = {}
        variant_hashes = {}
        for track in TRACKS:
            target_link = variant_by_path[track][path]
            content = normalized("".join(target_link.itertext()))
            if content:
                value = spoken_text(content, track, numbers)
            else:
                if ordinal not in EMPTY_LINK_CUES:
                    raise ValueError("Missing exact empty-link cue")
                value = EMPTY_LINK_CUES[ordinal][track]
            expected[track] = value
            variant_hashes[track] = tree_sha(target_link)
            link_expected_by_track[track][id(target_link)] = value
        link_fixtures.append({
            "id": f"A00-ALG-L{ordinal:02d}", "ordinal": ordinal,
            "module": MODULE, "source_path": list(path),
            "source_attributes": dict(source_link.attrib),
            "source_tree_sha256": tree_sha(source_link),
            "variant_tree_sha256": variant_hashes,
            "expected": expected,
        })

    selected_paths = choose_blocks(source, source_paths)
    selected_nodes = [source_by_path[path] for path in selected_paths]
    block_for_id = {}
    for source_id in ordered_ids:
        id_node = next(node for node in source.iter() if node.get("id") == source_id)
        id_path = source_paths[id(id_node)]
        ancestors = [path for path in selected_paths
                     if len(path) <= len(id_path) and id_path[:len(path)] == path]
        if ancestors:
            chosen = max(ancestors, key=len)
        else:
            descendants = [path for path in selected_paths
                           if len(path) >= len(id_path) and path[:len(id_path)] == id_path]
            if not descendants:
                raise ValueError("Source ID has no finite narration block: " + source_id)
            chosen = descendants[0]
        block_for_id[source_id] = chosen

    block_fixtures = []
    for ordinal, (path, source_node) in enumerate(zip(selected_paths, selected_nodes), 1):
        expected, variant_hashes = {}, {}
        for track in TRACKS:
            target_node = variant_by_path[track][path]
            expected[track] = speak_element(
                target_node, track, numbers, math_expected_by_track[track],
                link_expected_by_track[track])
            if not expected[track]:
                raise ValueError("Empty finite narration block: " + repr(path))
            variant_hashes[track] = tree_sha(target_node)
        ids = sorted((source_id for source_id, selected in block_for_id.items()
                      if selected == path), key=id_order.get)
        mark = MODULE + "--path-" + "-".join(str(index) for index in path)
        block_fixtures.append({
            "id": f"A00-ALG-B{ordinal:03d}", "ordinal": ordinal,
            "module": MODULE, "mark": mark, "source_path": list(path),
            "source_tag": local(source_node), "source_ids": ids,
            "source_tree_sha256": tree_sha(source_node),
            "variant_tree_sha256": variant_hashes,
            "expected": expected,
            "math_refs": [f"A00-ALG-M{index:03d}" for index, math in enumerate(source_maths, 1)
                          if len(path) <= len(source_paths[id(math)])
                          and source_paths[id(math)][:len(path)] == path],
            "link_refs": [f"A00-ALG-L{index:02d}" for index, link in enumerate(source_links, 1)
                          if len(path) <= len(source_paths[id(link)])
                          and source_paths[id(link)][:len(path)] == path],
        })
    flat_ids = [source_id for row in block_fixtures for source_id in row["source_ids"]]
    if flat_ids != ordered_ids:
        mismatch = next((index for index, pair in enumerate(zip(flat_ids, ordered_ids))
                         if pair[0] != pair[1]), min(len(flat_ids), len(ordered_ids)))
        raise ValueError(f"Narration ID partition lost source order at {mismatch}")

    media_fixtures = []
    for ordinal, source_media in enumerate(source.iter("{" + CN + "}media"), 1):
        path = source_paths[id(source_media)]
        row = assets["assets"][ordinal - 1]
        media_fixtures.append({
            "id": f"A00-ALG-A{ordinal:02d}", "ordinal": ordinal,
            "media_id": source_media.get("id"), "source_path": list(path),
            "source_ref": row["source"]["ref"],
            "source_tree_sha256": tree_sha(source_media),
            "variant_tree_sha256": {track: tree_sha(variant_by_path[track][path])
                                    for track in TRACKS},
            "expected_alt": {track: variant_by_path[track][path].get("alt")
                             for track in TRACKS},
            "outputs": row["outputs"],
        })

    table_fixtures = []
    for ordinal, source_table in enumerate(source.iter("{" + CN + "}table"), 1):
        path = source_paths[id(source_table)]
        table_fixtures.append({
            "id": f"A00-ALG-T{ordinal:02d}", "ordinal": ordinal,
            "table_id": source_table.get("id"), "source_path": list(path),
            "accessible_slot": "aria-label" if source_table.get("aria-label") else "summary",
            "source_tree_sha256": tree_sha(source_table),
            "variant_tree_sha256": {track: tree_sha(variant_by_path[track][path])
                                    for track in TRACKS},
            "expected": {
                track: spoken_text(
                    variant_by_path[track][path].get("aria-label")
                    or variant_by_path[track][path].get("summary"), track, numbers)
                for track in TRACKS
            },
        })

    exercise_inventory = []
    for ordinal, source_exercise in enumerate(source.iter("{" + CN + "}exercise"), 1):
        path = source_paths[id(source_exercise)]
        problem = source_exercise.find("{*}problem")
        solution = source_exercise.find("{*}solution")
        if problem is None:
            raise ValueError("Exercise lost problem")
        problem_path = source_paths[id(problem)]
        solution_path = source_paths[id(solution)] if solution is not None else None
        exercise_inventory.append({
            "ordinal": ordinal, "exercise_id": source_exercise.get("id"),
            "source_path": list(path), "problem_id": problem.get("id"),
            "source_problem_path": list(problem_path),
            "source_problem_tree_sha256": tree_sha(problem),
            "target_problem_tree_sha256": {
                track: tree_sha(variant_by_path[track][problem_path]) for track in TRACKS},
            "expected_question": {
                track: speak_element(variant_by_path[track][problem_path], track, numbers,
                                     math_expected_by_track[track], link_expected_by_track[track])
                for track in TRACKS},
            "source_answer_available": solution is not None,
            "source_solution_id": solution.get("id") if solution is not None else None,
            "source_solution_path": list(solution_path) if solution_path is not None else None,
            "source_solution_tree_sha256": tree_sha(solution) if solution is not None else None,
            "target_solution_tree_sha256": {
                track: tree_sha(variant_by_path[track][solution_path]) if solution_path is not None else None
                for track in TRACKS},
            "expected_solution": {
                track: (speak_element(variant_by_path[track][solution_path], track, numbers,
                                      math_expected_by_track[track], link_expected_by_track[track])
                        if solution_path is not None else None)
                for track in TRACKS},
            "existing_source_solution_title": (
                solution is not None and solution.find("{*}title") is not None),
            "answer_validation": {
                "source_supplied_only": solution is not None,
                "computed_answer": None,
                "missing_answer_synthesized": False,
            },
        })

    supplied = sum(row["source_answer_available"] for row in exercise_inventory)
    titled = sum(row["existing_source_solution_title"] for row in exercise_inventory)
    if (len(math_fixtures), len(media_fixtures), len(table_fixtures),
            len(link_fixtures), len(exercise_inventory), supplied, titled) != (
            441, 44, 35, 15, 107, 71, 12):
        raise ValueError("Changed complete m81268 finite fixture census")

    rules = {
        "schema": "provider-neutral-complete-m81268-narration-fixtures-v1",
        "status": "complete source-bound finite AX-2 draft; human/listening/AT review pending",
        "date": "2026-09-02",
        "purpose": "Explicit translation/narration fixtures only; not training or synthesis data.",
        "tracks": list(TRACKS),
        "locales": {track: TRACKS[track][0] for track in TRACKS},
        "scope": {
            "unit": UNIT, "module": MODULE, "complete_module": True,
            "groups": [{"name": name, "source_path": list(path)} for name, path in GROUPS],
            "source_module_sha256": ID_SHA256, "source_module_bytes": len(indonesian_raw),
            "english_module_sha256": EN_SHA256, "english_module_bytes": len(english_raw),
            "indonesian_commit": ID_COMMIT, "english_commit": EN_COMMIT,
            "source_tree_sha256": tree_sha(source),
            "target_tree_sha256": {track: tree_sha(root) for track, root in variants.items()},
            "counts": {**EXPECTED, "narration_blocks": len(block_fixtures),
                       "untitled_solution_cues": 59, "existing_solution_titles": 12},
            "complete_source_scope": True, "whole_assignment_complete": False,
        },
        "matching_contract": {
            "dispatch": "Exact live target node, whole module/track snapshot, root-relative path, ordinal and canonical tree.",
            "unknown_case": "unsupported_source_bound_narration",
            "generic_number_parser_authorized": False,
            "generic_algebra_parser_authorized": False,
            "generic_mtext_or_table_parser_authorized": False,
            "runtime_fallback": False,
            "source_storage": "Exact pinned module bytes plus whitespace-insensitive canonical fixture trees.",
            "block_policy": "Explicit block bodies supersede descendant concatenation; table summaries and media alts speak once.",
        },
        "handoff_pins": {
            "edits_sha256": EDITS_SHA256, "assets_sha256": ASSETS_SHA256,
            "canon_lock_sha256": CANON_LOCK_SHA256,
        },
        "canon_target_revisions": [dict(row) for row in CANON_TARGET_REVISIONS],
        "manifest_accessibility_override": {
            "element_id": "eip-id1164754514704", "slot": "aria-label",
            "required_fragment": "Apa ana eksponen? ora.",
            "immutable_edit_ledger_changed": False,
        },
        "finite_number_lexicon": numbers,
        "ordered_source_ids": ordered_ids,
        "structural_manifest": [
            {"id": node.get("id"), "tag": local(node),
             "source_path": list(source_paths[id(node)]), "source_tree_sha256": tree_sha(node)}
            for node in source.iter() if node.get("id")
        ],
        "math_fixtures": math_fixtures,
        "media_fixtures": media_fixtures,
        "table_fixtures": table_fixtures,
        "link_fixtures": link_fixtures,
        "exercise_inventory": exercise_inventory,
        "answer_policy": {
            "supplied": 71, "absent": 36, "untitled_cue_count": 59,
            "existing_solution_titles": 12, "synthesis_of_missing_answer": False,
            "missing_source_answer_ids": [row["exercise_id"] for row in exercise_inventory
                                          if not row["source_answer_available"]],
        },
        "block_fixtures": block_fixtures,
        "review_limits": {
            "native_language_review": False, "educator_review": False,
            "screen_reader_review": False, "listening_review": False,
            "provider_synthesis": False,
        },
    }
    return rules


def products():
    rules = make_rules()
    raw = (json.dumps(rules, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return {OUTPUT: raw}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError("Nondeterministic complete m81268 audio contract")
    for relative, raw in generated.items():
        path = LANG / relative
        if arguments.check:
            if path.read_bytes() != raw:
                raise ValueError("Stale complete m81268 audio contract")
        else:
            write_bytes(path, raw)
    print("a00-use-algebra: 441 exact MathML fixtures and complete finite narration compiled")


if __name__ == "__main__":
    main()
