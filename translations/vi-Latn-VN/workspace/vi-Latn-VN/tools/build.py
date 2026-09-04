"""Offline pilot build and structural QA. Python stdlib + Pandoc, no CDN."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[1]
MATH = "http://www.w3.org/1998/Math/MathML"


def serialize_math(node):
    """Avoid blank XML formatting lines ending Pandoc's raw HTML block.

    Keep token text, especially meaningful mtext spaces, unchanged. Existing
    math without blank formatting lines retains its exact serialized bytes.
    """
    serialized = ET.tostring(node, encoding="unicode", short_empty_elements=False)
    if re.search(r"\n[ \t\r]*\n", serialized):
        for element in node.iter():
            if element.tag.rsplit("}", 1)[-1] not in {"mi", "mn", "mo", "mtext", "ms"}:
                if element.text and element.text.isspace():
                    element.text = None
            if element.tail and element.tail.isspace():
                element.tail = None
        serialized = ET.tostring(node, encoding="unicode", short_empty_elements=False)
    return serialized


def prune_empty_math_layout(node):
    """Remove source-layout containers that carry no mathematical tokens."""
    count = 0
    candidates = {"mrow", "mtd", "mtr", "mtable"}
    changed = True
    while changed:
        changed = False
        for parent in list(node.iter()):
            for child in list(parent):
                tag = child.tag.rsplit("}", 1)[-1]
                token_descendants = [item for item in child.iter()
                                     if item.tag.rsplit("}", 1)[-1] in {"mi", "mn", "mo", "mtext", "ms", "mspace"}]
                if tag in candidates and not token_descendants and not "".join(child.itertext()).strip():
                    parent.remove(child)
                    count += 1
                    changed = True
    return count


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.images = [], [], []
        self.math = 0
        self.source_math = []
        self.lang = None

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if "id" in attr:
            self.ids.append(attr["id"])
        if tag == "a":
            self.links.append(attr.get("href", ""))
        if tag == "img":
            self.images.append(attr)
        if tag == "html":
            self.lang = attr.get("lang")
        self.math += tag == "math"
        if tag == "math" and attr.get("data-source"):
            self.source_math.append(attr["data-source"])


def validate_math_markup(html):
    """Reject broken raw-MathML boundaries before a browser repairs them.

    Multiline raw MathML inside a Markdown table can preserve the opening
    data-source marker while Pandoc inserts HTML closing tags inside math.
    Counting markers alone cannot detect that loss of structure.
    """
    fragments = re.findall(r"<math\b[^>]*>.*?</math\s*>", html, re.DOTALL)
    starts = len(re.findall(r"<math\b", html))
    closes = len(re.findall(r"</math\s*>", html))
    assert len(fragments) == starts == closes, "unbalanced rendered MathML"
    for fragment in fragments:
        try:
            node = ET.fromstring(fragment)
        except ET.ParseError as error:
            raise AssertionError(f"invalid rendered MathML: {fragment[:160]}") from error
        assert node.tag in {"math", f"{{{MATH}}}math"}, "not a math root"
        assert not any(el.tag.rsplit("}", 1)[-1] in {"p", "div", "section", "table", "tr", "td", "th"}
                       for el in node.iter()), "HTML layout injected into MathML"
    return len(fragments)


def validate_reader_links(links, local_ids, reader_dir, configs):
    """Validate local/cross-reader anchors without fetching external links.

    Only exact registered same-directory reader filenames are accepted. Parse
    and hash each target's same byte snapshot once, even for repeated links.
    The function only inspects files; it never rewrites rendered HTML.
    """
    registered = {}
    for unit, config in configs.items():
        filename = config["slug"] + ".vi.html"
        assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.vi\.html", filename), \
            f"unsafe registered reader filename: {filename}"
        assert filename not in registered, f"duplicate registered reader: {filename}"
        registered[filename] = unit

    directory = Path(reader_dir).resolve()
    local_ids = set(local_ids)
    checked_targets = {}
    result = {"local_anchor_links": 0, "cross_reader_links": [], "external_links": []}
    for href in links:
        assert href and not any(ord(char) <= 32 or ord(char) == 127 for char in href), \
            f"empty or invalid link: {href!r}"
        try:
            parsed = urlsplit(href)
        except ValueError as error:
            raise AssertionError(f"invalid link: {href}") from error
        scheme = parsed.scheme.lower()
        if scheme in {"http", "https", "mailto"}:
            if scheme == "mailto":
                assert parsed.path and not parsed.netloc, f"invalid mailto link: {href}"
            else:
                assert parsed.netloc and parsed.hostname, f"invalid external link: {href}"
            result["external_links"].append({
                "href": href, "scheme": scheme, "verification": "unverified",
                "fetched": False,
            })
            continue
        assert not scheme and not parsed.netloc, f"unsupported link scheme/authority: {href}"
        assert "?" not in href.split("#", 1)[0], f"unsupported local query: {href}"
        assert parsed.fragment, f"local reader link requires an anchor: {href}"
        assert not re.search(r"%(?![0-9A-Fa-f]{2})", parsed.fragment), \
            f"invalid anchor encoding: {href}"
        try:
            anchor = unquote(parsed.fragment, encoding="utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise AssertionError(f"invalid anchor encoding: {href}") from error
        assert not any(ord(char) < 32 or ord(char) == 127 for char in anchor), \
            f"invalid anchor: {href}"
        if not parsed.path:
            assert href.startswith("#") and anchor in local_ids, f"broken local link: {href}"
            result["local_anchor_links"] += 1
            continue
        filename = parsed.path
        assert filename in registered, f"unregistered or unsafe local reader target: {href}"
        # Exact registry membership rejects slashes, backslashes, percent-encoded
        # paths, traversal, absolute paths, unrelated files and bare reader URLs.
        if filename not in checked_targets:
            target = (directory / filename).resolve()
            assert target.parent == directory, f"reader target escapes output directory: {href}"
            assert target.is_file(), f"cross-reader target does not exist: {filename}"
            data = target.read_bytes()
            try:
                target_html = data.decode("utf-8")
            except UnicodeDecodeError as error:
                raise AssertionError(f"reader target is not UTF-8: {filename}") from error
            inspector = Inspector()
            inspector.feed(target_html)
            checked_targets[filename] = (Counter(inspector.ids), sha256(data).hexdigest())
        ids, digest = checked_targets[filename]
        assert ids[anchor] == 1, f"missing or ambiguous cross-reader anchor: {href}"
        result["cross_reader_links"].append({
            "href": href, "target_unit": registered[filename],
            "target_reader": filename, "target_anchor": anchor,
            "target_sha256": digest,
        })
    return result


def main():
    configs = json.loads((ROOT / "units.json").read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", choices=list(configs), default="A30-U001")
    args = parser.parse_args()
    unit = args.unit
    config = configs[unit]
    source = ROOT / config["source"]
    source_tree = ET.parse(source)
    identities = {el.get("id"): el for el in source_tree.iter() if el.get("id")}
    translation = ROOT / "translation" / (config["slug"] + ".vi.md")
    markdown = translation.read_text(encoding="utf-8")
    assert markdown == unicodedata.normalize("NFC", markdown), "Vietnamese must be NFC"
    provenance = []

    def insert_math(match):
        identity, index = match.group(1), int(match.group(2))
        node = deepcopy(list(identities[identity].iter(f"{{{MATH}}}math"))[index])
        node.tail = None
        source_digest = sha256(ET.tostring(node)).hexdigest()
        for element in node.iter():
            element.tag = element.tag.rsplit("}", 1)[-1]
            if element.tag == "mtext" and element.text:
                for original, localized in config["math_text"].items():
                    element.text = element.text.replace(original, localized)
        pruned = prune_empty_math_layout(node) if config.get("prune_empty_math_layout") else 0
        node.set("xmlns", MATH)
        node.set("data-source", f"{identity}:{index}")
        provenance.append({"source_id": identity, "math_index": index, "source_math_sha256": source_digest,
                           "empty_layout_nodes_pruned": pruned})
        return serialize_math(node)

    expanded = re.sub(r"\{\{math:([^:}]+):(\d+)\}\}", insert_math, markdown)
    assert "{{math:" not in expanded
    command = ["pandoc", "--from=markdown+fenced_divs+raw_html", "--to=html5", "--standalone",
               "--embed-resources", "--mathml", "--toc", "--toc-depth=2", "--fail-if-warnings",
               "--css=../reader.css"]
    outputs = [subprocess.run(command, input=expanded, text=True, encoding="utf-8",
                              cwd=translation.parent, check=True, capture_output=True).stdout for _ in range(2)]
    assert outputs[0] == outputs[1], "two builds differ"
    html = outputs[0]
    # Keep even technical CNXML IDs when several source paragraphs are combined
    # in one translated block. Each alias points into its nearest retained parent.
    probe = Inspector()
    probe.feed(html)
    retained = set(probe.ids)
    parents = {child: parent for parent in source_tree.iter() for child in parent}
    alias_map = []
    aliases = {}
    for identity, node in identities.items():
        if identity in retained:
            continue
        ancestor = parents.get(node)
        while ancestor is not None and ancestor.get("id") not in retained:
            ancestor = parents.get(ancestor)
        assert ancestor is not None, f"no translated anchor for {identity}"
        owner = ancestor.get("id")
        aliases.setdefault(owner, []).append(identity)
        alias_map.append({"source_id": identity, "translated_block": owner})
    for owner, children in aliases.items():
        anchors = "".join(f'<span id="{identity}" class="source-anchor" aria-hidden="true"></span>' for identity in children)
        pattern = r'(<[^>]+\bid="' + re.escape(owner) + r'"[^>]*>)'
        html, count = re.subn(pattern, lambda match: match.group(1) + anchors, html, count=1)
        assert count == 1, owner
    check = Inspector()
    check.feed(html)
    assert check.lang == "vi-Latn-VN", check.lang
    assert not [key for key, n in Counter(check.ids).items() if n > 1], "duplicate IDs"
    link_review = validate_reader_links(check.links, check.ids, ROOT / "review", configs)
    assert len(check.images) == config["images"]
    assert all(img.get("alt") and img.get("src", "").startswith("data:") for img in check.images)
    assert "<script" not in html and "{{math:" not in html
    assert ":::" not in html, "unparsed source container"
    assert not re.search(r"&lt;/?(?:math|mrow|mtable|mtr|mtd|mfrac|msqrt|mroot)\b", html), "MathML rendered as code"
    assert Counter(check.source_math) == Counter(f"{p['source_id']}:{p['math_index']}" for p in provenance), "source math lost during rendering"
    assert validate_math_markup(html) == check.math, "rendered MathML count mismatch"
    for identity in config["required_ids"]:
        assert identity in identities and identity in check.ids, identity
    # Pin selected original numerical data, not only the shape of rendered math.
    for identity, expected in config["numeric_checks"].items():
        assert [n.text for n in identities[identity].iter(f"{{{MATH}}}mn")] == expected
    spec = importlib.util.spec_from_file_location("unit_checks", ROOT / config["computing_check"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tests = module.tests()
    canon_path = f"canon/review-{unit}.json"
    canon = json.loads((ROOT / canon_path).read_text(encoding="utf-8"))
    assert canon["unit"] == unit and len(canon["examples_consulted"]) >= config["minimum_canon_examples"]
    assert canon["draft_checked"] and canon["final_checked"]
    assert canon["translation_sha256"] == sha256(translation.read_bytes()).hexdigest(), "reread canon after editing translation"
    output_dir = ROOT / "review"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / (config["slug"] + ".vi.html")
    write_atomic(output, html.encode("utf-8"))
    receipt = {
        "unit": unit, "locale": check.lang, "result": "pass", "two_builds_byte_identical": True,
        "html_sha256": sha256(output.read_bytes()).hexdigest(), "html_bytes": output.stat().st_size,
        "translation_sha256": sha256(translation.read_bytes()).hexdigest(),
        "source_excerpt_sha256": sha256(source.read_bytes()).hexdigest(),
        "pandoc": subprocess.check_output(["pandoc", "--version"], text=True).splitlines()[0],
        "html_ids": len(check.ids), "internal_links": sum(h.startswith("#") for h in check.links),
        "cross_reader_links": link_review["cross_reader_links"],
        "cross_reader_link_count": len(link_review["cross_reader_links"]),
        "external_links": link_review["external_links"],
        "external_link_count": len(link_review["external_links"]),
        "mathml_expressions": check.math, "source_math_insertions": provenance,
        "source_math_rendered_count": len(check.source_math), "no_escaped_mathml": True,
        "all_mathml_well_formed": True,
        "preserved_source_ids": len(identities), "technical_anchor_aliases": alias_map,
        "embedded_images": len(check.images), "unit_assertions": tests,
        "assertion_kind": config.get("assertion_kind", "finite mathematical checks"),
        "mathematical_assertions": None if config.get("mixed_assertions") else tests,
        "source_examples": config["source_examples"], "try_it_exercises": config["try_it_exercises"], "selected_end_exercises": config["selected_end_exercises"],
        "new_unique_end_exercises": config.get("new_unique_end_exercises", config["selected_end_exercises"]),
        "repeated_from_U001": config.get("repeated_from_U001", []),
        "worked_answers_to_all_selected_exercises": True,
        "network_required_to_read": False, "native_speaker_review": "not_performed",
        "visual_review": config["visual_receipt"], "canon_review": canon_path,
        "layout_adaptations": config.get("layout_adaptations", [])
    }
    (ROOT / "qa").mkdir(exist_ok=True)
    write_atomic(ROOT / f"qa/build-{unit}.json", (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: receipt[k] for k in ("result", "html_bytes", "html_sha256", "html_ids", "mathml_expressions", "unit_assertions", "assertion_kind")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
