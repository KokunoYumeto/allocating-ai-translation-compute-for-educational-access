"""U013 structure/assets and independent finite-relation logic checks.

Default: committed excerpt, draft and five committed original assets only.
--originals: additionally inspect both full pinned modules and inherited rights
CSV, using existing original assets in downloads instead of the published copies.
No formula is inferred from a raster; finite relations are illustrations, not
pixel-derived data or proofs of the five continuous graphs.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import csv
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
EXCERPT_SHA = "266562a0495741d038aa102e2f3c3b601a70cbe19d9c1a9929907aa9b4dea31b"
RIGHTS_SHA = "bf65bd2786396c18655610bafbcab148aaff9ad2f5294e18cf22aa6f6ec81e69"
ITEMS = [
    (55, "fs-id1165135541711", "fs-id1165135541720", "fs-id1165133085670",
     "CNX_Precalc_Figure_01_01_216-4707.jpg", 37460,
     "9054c6357560ed19ed064b1f5a0f5f83896cf9b9e4ac1ef4dd604a29e8dabc55"),
    (56, "fs-id1165133085674", "fs-id1165134380356", None,
     "CNX_Precalc_Figure_01_01_232-8b55.jpg", 39699,
     "5a0407f7233805eaa1533c765c4e1ee0dc22d86b42ad092684fd9f6f92c08fff"),
    (57, "fs-id1165134037560", "fs-id1165134037568", "fs-id1165137583859",
     "CNX_Precalc_Figure_01_01_217-7861.jpg", 39303,
     "e77eac49e0b36998a999ca312a1b52685579867ab1fa320cf224269930cd4cea"),
    (58, "fs-id1165134031248", "fs-id1165134031257", None,
     "CNX_Precalc_Figure_01_01_218-bd16.jpg", 44544,
     "f18e7ba019d7c094dd9daae2d92920843e89568993a1d94b53d1d996f3c15163"),
    (59, "fs-id1165134394579", "fs-id1165135457089", "fs-id1165135342197",
     "CNX_Precalc_Figure_01_01_233-a0df.jpg", 35943,
     "72e73a932a8576eb9679e0bf2547fd21184fa50eb1e6b03ef15193394c12329b"),
]


def classify(pairs):
    """Set semantics: duplicate records do not create new points."""
    by_input, by_output = defaultdict(set), defaultdict(set)
    for x, y in set(pairs):
        by_input[x].add(y)
        by_output[y].add(x)
    is_function = all(len(values) == 1 for values in by_input.values())
    is_injective = is_function and all(len(values) == 1 for values in by_output.values())
    return is_function, is_injective


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, description, kind="structure"):
        assert condition, description
        counts[kind] += 1

    source_path = ROOT / "sources/m49301-graphical-injectivity-source.cnxml"
    data = source_path.read_bytes()
    tree = ET.fromstring(data)
    md = (ROOT / "translation/A30-U013-graphical-injectivity.vi.md").read_text("utf-8")
    identities = {n.get("id"): n for n in tree.iter() if n.get("id")}
    explicit = re.findall(r"\{#([^}]+)\}", md)
    check(sha256(data).hexdigest() == EXCERPT_SHA, "complete pinned excerpt bytes")
    check(tree.tag == f"{{{CN}}}source-excerpt" and not tree.get("id"), "no repeated Graphical parent")
    check(tree[0].get("id") == "fs-id1165135531627", "shared prompt begins excerpt")
    check(tree[-1].get("id") == "fs-id1165134394579", "last Graphical exercise")
    check(len(tree) == 6, "one prompt and five exercises")
    check([n.get("id") for n in tree.findall(f"{{{CN}}}exercise")] ==
          [item[1] for item in ITEMS], "exact exercise order55-59")
    check(md == unicodedata.normalize("NFC", md), "NFC Vietnamese")
    check("fs-id1165135664071}" not in md, "U012 parent ID not duplicated")
    check(len(identities) == 22, "22 source IDs")
    for identity in identities:
        check(explicit.count(identity) == 1, f"one explicit source anchor {identity}")
    for tag, expected in (("problem", 5), ("solution", 3), ("para", 4),
                          ("media", 5), ("image", 5), ("link", 0), ("table", 0)):
        check(len(list(tree.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")
    check(not list(tree.iter(f"{{{M}}}math")), "source has no MathML")
    check("{{math:" not in md, "no invented source MathML placeholder")
    check(md.count("Nguồn không kèm lời giải cho") == 2, "two new-solution disclosures")
    check(md.count("*Ghi chú đối chiếu hình:*") == 5, "all five alt descriptions contextualized")
    for target in re.findall(r"\]\(#([^)]+)\)", md):
        check(target in explicit, f"local answer link {target}")
    check(len(re.findall(r"\]\(A30-U006-graph-tests\.vi\.html#[^)]+\)", md)) == 2,
          "two registered U006 reader links")

    asset_root = (ROOT.parent / "downloads/upstream-openstax/media") if originals else (ROOT / "assets")
    for number, exercise, media, solution, filename, size, digest in ITEMS:
        check(f"### Bài {number} {{#{exercise}}}" in md, "continuous source exercise number")
        actual = identities[exercise].find(f"{{{CN}}}solution")
        check((actual.get("id") if actual is not None else None) == solution, "source solution inventory")
        label = "Lời giải nguồn" if solution else "Lời giải bổ sung"
        check(f"### Bài {number} — {label}" in md, "correct source/new answer label")
        image_node = next(identities[media].iter(f"{{{CN}}}image"))
        check(Path(image_node.get("src")).name == filename, "exact source image name/order")
        check(md.count(f"(../assets/{filename})") == 1, "original image referenced once")
        image_data = (asset_root / filename).read_bytes()
        check(len(image_data) == size, f"original image byte count {filename}", "asset")
        check(sha256(image_data).hexdigest() == digest, f"original image SHA256 {filename}", "asset")

    for identity, expected in (
        ("fs-id1165133085671", "not a function so it is also not a one-to-one function"),
        ("fs-id1165137583860", "one-to-one function"),
        ("fs-id1165135342198", "function, but not one-to-one"),
    ):
        check(" ".join(identities[identity].itertext()).strip() == expected, "source answer unchanged")
    for identity, expected in (
        ("fs-id1165133085671", "Đồ thị không biểu diễn hàm số, nên cũng không biểu diễn hàm số đơn ánh."),
        ("fs-id1165137583860", "Đồ thị biểu diễn một hàm số đơn ánh."),
        ("fs-id1165135342198", "Đồ thị biểu diễn một hàm số, nhưng hàm số không đơn ánh."),
    ):
        text = md.split(f"{{#{identity}}}", 1)[1].split(":::", 1)[0]
        check(expected in " ".join(text.split()), "translation retains source classification")
    new56 = md.split("### Bài 56 — Lời giải bổ sung", 1)[1].split("### ", 1)[0]
    new58 = md.split("### Bài 58 — Lời giải bổ sung", 1)[1].split("### ", 1)[0]
    check("không đơn ánh" in new56, "V graph newly supplied answer")
    check("**đơn ánh**" in new58, "decreasing graph newly supplied answer")
    for phrase in (
        "elip đứng", "một góc chữ V", "trái với hình và đáp án",
        "không xác định công thức đó", "không tự gán", "không vi phạm",
        "không coi điểm ảnh là dữ liệu đồ thị", "không suy ra công thức",
    ):
        check(phrase in md, f"material graph-description qualification: {phrase}")

    # These sets illustrate logical cases. They are not sampled from the images.
    finite_cases = [
        ([(-2, -1), (-2, 3)], (False, False), "same input/two outputs"),
        ([(0, 2), (1, 1), (2, 2)], (True, False), "function/repeated output"),
        ([(-2, -1), (0, 0), (3, 2)], (True, True), "increasing finite function"),
        ([(-2, 3), (0, 1), (3, -1)], (True, True), "decreasing finite function"),
        ([(-1, 1), (0, 2), (1, 1)], (True, False), "rise and fall repeats output"),
        ([(2, 1), (2, 1)], (True, True), "duplicate record is one point"),
        ([(1, 2), (2, 1)], (True, True), "two different inputs/two different outputs"),
        ([(1, 2), (2, 2)], (True, False), "same output allowed for a function"),
        ([(1, 2), (1, 3)], (False, False), "horizontal uniqueness alone is insufficient"),
    ]
    for pairs, expected, description in finite_cases:
        result = classify(pairs)
        check(result[0] == expected[0], f"finite function: {description}", "finite")
        check(result[1] == expected[1], f"finite injectivity: {description}", "finite")

    if originals:
        sys.path.insert(0, str(ROOT / "tools"))
        from extract_graphical_injectivity import ORIGINALS, selected
        for relative, digest in ORIGINALS:
            path = ROOT.parent / relative
            check(sha256(path.read_bytes()).hexdigest() == digest, "pinned full source", "original")
            original = selected(path)
            check([n.get("id") for n in original.iter() if n.get("id")] == list(identities),
                  "EN/ID ordered IDs and exact boundaries", "original")
            check([n.get("src") for n in original.iter(f"{{{CN}}}image")] ==
                  [n.get("src") for n in tree.iter(f"{{{CN}}}image")], "EN/ID image order", "original")
            if "upstream-openstax" in relative:
                check(ET.tostring(original) == ET.tostring(tree), "complete EN selected subtree", "original")
        rights_path = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
        check(sha256(rights_path.read_bytes()).hexdigest() == RIGHTS_SHA, "inherited rights evidence hash", "original")
        with rights_path.open(encoding="utf-8-sig", newline="") as stream:
            rights = {Path(row["asset_path"]).name: row for row in csv.DictReader(stream)}
        for _, _, _, _, filename, size, digest in ITEMS:
            row = rights[filename]
            check(row["admission"] == "admitted" and row["sha256"] == digest and int(row["bytes"]) == size,
                  "exact inherited admitted component", "original")
            check(row["license_id"] == "CC-BY-NC-SA-4.0", "inherited component license", "original")
            id_asset = ROOT.parent / "downloads/a30-edition/source-core/repo/source/media" / filename
            check(sha256(id_asset.read_bytes()).hexdigest() == digest, "EN/ID original asset identity", "original")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    results = tests(originals="--originals" in sys.argv, details=True)
    print(f"PASS: {sum(results.values())} assertions; {results}")
