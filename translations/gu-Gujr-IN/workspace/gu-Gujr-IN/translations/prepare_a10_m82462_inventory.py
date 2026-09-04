"""Write the actual-image-reviewed media inventory for A10 m82462."""
from pathlib import Path
import hashlib
import json
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REVIEWS = HERE.parent / "reviews"
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82462/index.cnxml"
GU = HERE / "a10-m82462.gu.cnxml"
MEDIA = ROOT / "downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/CNX_ElemAlg_Figure_02_00_001_img_new.jpg"
OUT = REVIEWS / "a10-m82462-media-inventory.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ns = {"c": "http://cnx.rice.edu/cnxml"}
    source = etree.parse(str(SRC)).getroot()
    target = etree.parse(str(GU)).getroot()
    smedia = source.xpath("//c:media", namespaces=ns)
    gmedia = target.xpath("//c:media", namespaces=ns)
    assert len(smedia) == len(gmedia) == 1
    assert MEDIA.exists() and sha(MEDIA) == "1aa4da73b19ca49299a62bb558c8a5150c16e388e2814b33476b7501d112f96f"
    item = {
        "source_element": "fs-id1166503473429",
        "figure": "CNX_ElemAlg_Figure_02_00_001",
        "src": "../../media/CNX_ElemAlg_Figure_02_00_001_img_new.jpg",
        "canonical_actual_path": str(MEDIA.relative_to(ROOT)).replace("\\", "/"),
        "actual_sha256": sha(MEDIA),
        "actual_dimensions": [975, 450],
        "actual_reviewed": True,
        "source_alt": smedia[0].get("alt"),
        "gujarati_alt": gmedia[0].get("alt"),
        "embedded_english": "",
        "language_bearing": False,
        "retain_original": True,
        "classification": "language-free photographic splash",
        "actual_observation_gu": "લીલાછમ પૃષ્ઠભૂમિ સામે અનેક પથ્થરો એક ઉપર એક સંતુલિત ગોઠવેલા દેખાય છે; ચિત્રમાં કોઈ લખાણ કે ગાણિતિક ચિહ્ન નથી.",
        "source_alt_matches_actual": True,
        "localization_note": "ગુજરાતી વૈકલ્પિક વર્ણન સાથે મૂળ ફોટો જાળવો; ચિત્રના અંદર અનુવાદ કરવા જેવું લખાણ નથી."
    }
    inventory = {
        "module": "m82462",
        "source_sha256": sha(SRC),
        "translation_sha256": sha(GU),
        "actual_images_reviewed": 1,
        "language_bearing": 0,
        "mathematical_only": 1,
        "media": [item]
    }
    OUT.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Inventory 1 language 0 math 1")


if __name__ == "__main__":
    main()
