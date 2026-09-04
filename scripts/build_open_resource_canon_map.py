#!/usr/bin/env python3
"""Build the bounded open-resource stage/subject canon map.

The local OpenStax catalogue is treated as an official title inventory.  All
other records are evidence-mapped from official provider pages listed below.
This script does not read any local translation or programme-completion state.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "OPENSTAX_CATALOG_20260901.csv"
JSON_OUT = ROOT / "structured" / "open_resource_canon_map.json"
MD_OUT = ROOT / "agent_reports" / "OPEN_RESOURCE_CANON_MAP.md"
ACCESSED = "2026-09-01"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


ISCED = [
    {"level": "0", "label": "early childhood education"},
    {"level": "1", "label": "primary education"},
    {"level": "2", "label": "lower secondary education"},
    {"level": "3", "label": "upper secondary education"},
    {"level": "4", "label": "post-secondary non-tertiary education"},
    {"level": "5", "label": "short-cycle tertiary education"},
    {"level": "6", "label": "bachelor's or equivalent level"},
    {"level": "7", "label": "master's or equivalent level"},
    {"level": "8", "label": "doctoral or equivalent level"},
]


SOURCES = [
    {
        "id": "SRC-ISCED-2011",
        "organization": "UNESCO Institute for Statistics",
        "title": "International Standard Classification of Education (ISCED) 2011",
        "url": "https://uis.unesco.org/sites/default/files/documents/international-standard-classification-of-education-isced-2011-en.pdf",
        "accessed": ACCESSED,
        "claims_used": ["ISCED is the cross-national framework", "programme levels are 0 through 8"],
        "content_sha256": None,
        "hash_note": "Official web document was cited by URL; no local source snapshot was created in this bounded task.",
    },
    {
        "id": "SRC-OPENSTAX-CATALOG",
        "organization": "OpenStax",
        "title": "Official catalogue API-derived local title inventory",
        "url": "https://openstax.org/apps/cms/api/books/?format=json",
        "accessed": ACCESSED,
        "local_file": CATALOG.name,
        "content_sha256": sha256(CATALOG),
        "claims_used": ["73 exact title records", "title-level web, PDF, Bookshare and audiobook links where exposed"],
    },
    {
        "id": "SRC-OPENSTAX-LICENSE",
        "organization": "OpenStax",
        "title": "Licensing information for OpenStax textbooks",
        "url": "https://help.openstax.org/s/article/Licensing-information-of-OpenStax-textbooks",
        "accessed": ACCESSED,
        "claims_used": ["current catalogue-level CC BY-NC-SA 4.0 policy", "translation and adaptation are allowed noncommercially with attribution and ShareAlike"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OPENSTAX-ACCESS",
        "organization": "OpenStax",
        "title": "OpenStax and ADA guidelines",
        "url": "https://help.openstax.org/s/article/Do-OpenStax-materials-meet-ADA-guidelines",
        "accessed": ACCESSED,
        "claims_used": ["web view is the most accessible format", "web text, alt text, MathML and detailed image descriptions", "download formats may differ"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OLP-ABOUT",
        "organization": "Open Logic Project",
        "title": "About the Open Logic Project",
        "url": "https://openlogicproject.org/about/",
        "accessed": ACCESSED,
        "claims_used": ["modular intermediate formal logic corpus", "LaTeX source and CC BY", "topic coverage"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OLP-BUILDS",
        "organization": "Open Logic Project",
        "title": "Open Logic Project Builds",
        "url": "https://builds.openlogicproject.org/",
        "accessed": ACCESSED,
        "claims_used": ["complete corpus is not intended as a textbook", "individual remixed textbooks and screen/print PDFs", "What If? is incomplete"],
        "content_sha256": None,
    },
    {
        "id": "SRC-FORALLX",
        "organization": "Open Logic Project",
        "title": "forall x: Calgary",
        "url": "https://forallx.openlogicproject.org/",
        "accessed": ACCESSED,
        "claims_used": ["introductory textbook with exercises and solutions", "PDF, experimental HTML, SCORM and LaTeX", "CC BY 4.0", "dyslexia-oriented PDF"],
        "content_sha256": None,
    },
    {
        "id": "SRC-AFRICAN-STORYBOOK",
        "organization": "African Storybook",
        "title": "African Storybook platform",
        "url": "https://www.africanstorybook.org/",
        "accessed": ACCESSED,
        "claims_used": ["open picture storybooks for early reading", "download, print, translation and adaptation workflows"],
        "content_sha256": None,
    },
    {
        "id": "SRC-GDL-LICENSE",
        "organization": "Global Digital Library",
        "title": "Creative Commons license on content",
        "url": "https://digitallibrary.io/about/license/",
        "accessed": ACCESSED,
        "claims_used": ["item-level open licenses", "primarily CC BY and CC BY-SA", "translation and contextualisation intent"],
        "content_sha256": None,
    },
    {
        "id": "SRC-SIYAVULA",
        "organization": "Siyavula",
        "title": "South Africa CAPS open textbooks",
        "url": "https://www.siyavula.com/read",
        "accessed": ACCESSED,
        "claims_used": ["exact grade/subject sequences", "branded PDF editions are CC BY-ND", "unbranded CC BY EPUB editions exist for many titles", "IT and CAT are closed"],
        "content_sha256": None,
    },
    {
        "id": "SRC-PHET",
        "organization": "University of Colorado Boulder PhET",
        "title": "PhET licensing and offline-use guidance",
        "url": "https://phet.colorado.edu/en/licensing",
        "companion_url": "https://phet.colorado.edu/en/help-center/running-sims/general",
        "accessed": ACCESSED,
        "claims_used": ["regular HTML5 simulations use current CC BY-NC 4.0 terms", "simulations can be downloaded", "accessibility varies by simulation"],
        "content_sha256": None,
    },
    {
        "id": "SRC-CS-UNPLUGGED",
        "organization": "CS Unplugged",
        "title": "CS Unplugged",
        "url": "https://www.csunplugged.org/en/",
        "accessed": ACCESSED,
        "claims_used": ["computer-science activities without computers", "current-site material CC BY-SA 4.0", "printable and source-backed"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OPENINTRO",
        "organization": "OpenIntro",
        "title": "OpenIntro Statistics resources and licensing",
        "url": "https://www.openintro.org/book/os/",
        "companion_url": "https://www.openintro.org/license/",
        "accessed": ACCESSED,
        "claims_used": ["free PDF and screen-reader-oriented PDF", "statistics texts generally CC BY-SA 3.0 subject to exact-title and trademark notes"],
        "content_sha256": None,
    },
    {
        "id": "SRC-ACTIVE-CALCULUS",
        "organization": "Active Calculus",
        "title": "Active Calculus textbook family",
        "url": "https://activecalculus.org/",
        "accessed": ACCESSED,
        "claims_used": ["Prelude, single-variable and multivariable texts", "HTML/PDF/source", "CC BY-SA and modifiable source"],
        "content_sha256": None,
    },
    {
        "id": "SRC-CARPENTRIES",
        "organization": "The Carpentries",
        "title": "The Carpentries lessons and license",
        "url": "https://carpentries.org/lessons/",
        "companion_url": "https://carpentries.org/license/",
        "accessed": ACCESSED,
        "claims_used": ["self-contained software/data lessons, often embedded in curricula", "website lesson text CC BY 4.0 unless noted", "source-backed lessons"],
        "content_sha256": None,
    },
    {
        "id": "SRC-TURING-WAY",
        "organization": "The Turing Way community",
        "title": "The Turing Way repository and license",
        "url": "https://github.com/the-turing-way/the-turing-way",
        "companion_url": "https://github.com/the-turing-way/the-turing-way/blob/main/LICENSE.md",
        "accessed": ACCESSED,
        "claims_used": ["reproducible, ethical and collaborative data-science handbook", "documentation CC BY 4.0 and software MIT"],
        "content_sha256": None,
    },
    {
        "id": "SRC-TESSA",
        "organization": "The Open University / TESSA",
        "title": "TESSA English — All Africa",
        "url": "https://www.open.edu/openlearncreate/course/view.php?id=2042",
        "accessed": ACCESSED,
        "claims_used": ["teacher-education resources for primary and lower-secondary science", "PDF and adaptable Word library ZIP", "CC BY-SA 4.0 except third-party material"],
        "content_sha256": None,
    },
    {
        "id": "SRC-DIGITAL-AGE",
        "organization": "BCcampus Pressbooks",
        "title": "Teaching in a Digital Age, third edition",
        "url": "https://pressbooks.bccampus.ca/teachinginadigitalagev3m/",
        "accessed": ACCESSED,
        "claims_used": ["teacher/instructor design guide", "web, EPUB, PDF and source exports", "CC BY-NC 4.0 except where noted"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OPENRN-FUNDAMENTALS",
        "organization": "Open RN / NCBI Bookshelf",
        "title": "Nursing Fundamentals, second edition",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK610815/",
        "accessed": ACCESSED,
        "claims_used": ["entry-level prelicensure nursing textbook", "CC BY 4.0", "web and downloadable formats"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OPENRN-SKILLS",
        "organization": "Open RN / NCBI Bookshelf",
        "title": "Nursing Skills, second edition",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK596735/",
        "accessed": ACCESSED,
        "claims_used": ["entry-level nursing-skills textbook", "CC BY 4.0", "PDF/offline formats; interactives require online use", "Wisconsin/NCLEX alignment"],
        "content_sha256": None,
    },
    {
        "id": "SRC-OPENWHO",
        "organization": "World Health Organization",
        "title": "OpenWHO resource hub and terms of use",
        "url": "https://openwho.org/",
        "companion_url": "https://openwho.org/terms_of_use",
        "accessed": ACCESSED,
        "claims_used": ["health-emergency learning resources", "general terms do not grant blanket derivative/translation rights"],
        "content_sha256": None,
    },
    {
        "id": "SRC-SOIL-SCIENCE",
        "organization": "Iowa State University Digital Press",
        "title": "Introduction to Soil Science, second edition",
        "url": "https://iastate.pressbooks.pub/isudp-2025-201/",
        "accessed": ACCESSED,
        "claims_used": ["soil formation, properties, management, erosion and fertility", "CC BY 4.0 except noted", "web/PDF/EPUB"],
        "content_sha256": None,
    },
    {
        "id": "SRC-ENV-BIOLOGY",
        "organization": "Open Textbook Library",
        "title": "Environmental Biology",
        "url": "https://open.umn.edu/opentextbooks/textbooks/687",
        "accessed": ACCESSED,
        "claims_used": ["introductory environment text spanning ecology, health, water, agriculture, climate and energy", "CC BY", "multiple downloadable formats"],
        "content_sha256": None,
    },
    {
        "id": "SRC-FAO-CSA",
        "organization": "Food and Agriculture Organization of the United Nations",
        "title": "Climate-smart agriculture training manual",
        "url": "https://elearning.fao.org/pluginfile.php/506774/mod_scorm/content/1/story_content/external_files/CA2189EN.pdf",
        "accessed": ACCESSED,
        "claims_used": ["training manual", "CC BY-NC-SA 3.0 IGO", "translation disclaimer and third-party caveats"],
        "content_sha256": None,
    },
    {
        "id": "SRC-FAO-FFS",
        "organization": "Food and Agriculture Organization of the United Nations",
        "title": "Introduction to the Farmer Field School Approach",
        "url": "https://elearning.fao.org/course/view.php?id=724&lang=en",
        "accessed": ACCESSED,
        "claims_used": ["practitioner training course", "no blanket adaptation right established for the course in this audit"],
        "content_sha256": None,
    },
    {
        "id": "SRC-CORE-ECON",
        "organization": "CORE Econ",
        "title": "CORE Econ open-access economics resources",
        "url": "https://www.core-econ.org/",
        "accessed": ACCESSED,
        "claims_used": ["The Economy 2.0 Microeconomics, Macroeconomics and Doing Economics", "free access", "no-derivatives terms block use as an unpermissioned translation master"],
        "content_sha256": None,
    },
    {
        "id": "SRC-DOING-RESEARCH",
        "organization": "Open Textbook Library / Kwantlen Polytechnic University",
        "title": "Doing Research",
        "url": "https://open.umn.edu/opentextbooks/textbooks/905",
        "accessed": ACCESSED,
        "claims_used": ["concise research-question, source-search and evaluation primer", "CC BY", "web/PDF/eBook/XML"],
        "content_sha256": None,
    },
    {
        "id": "SRC-MIT-OCW",
        "organization": "Massachusetts Institute of Technology",
        "title": "MIT OpenCourseWare get-started and terms",
        "url": "https://ocw.mit.edu/pages/get-started/",
        "companion_url": "https://ocw.mit.edu/pages/privacy-and-terms-of-use/",
        "accessed": ACCESSED,
        "claims_used": ["introductory through graduate course repository", "course downloads", "CC BY-NC-SA 4.0 platform content with third-party exclusions"],
        "content_sha256": None,
    },
    {
        "id": "SRC-STACKS",
        "organization": "The Stacks Project",
        "title": "Stacks Project about, contents and contribution/license pages",
        "url": "https://stacks.math.columbia.edu/about",
        "companion_urls": ["https://stacks.math.columbia.edu/browse", "https://stacks.math.columbia.edu/contribute"],
        "accessed": ACCESSED,
        "claims_used": ["graduate/research reference, not introductory", "web, chapter/book PDF and TeX archive", "GNU Free Documentation License"],
        "content_sha256": None,
    },
]


def openstax_isced(title: str, subjects: str, is_ap: bool, is_high_school: bool) -> list[str]:
    t = title.lower()
    if title == "Algebra 1":
        return ["2", "3"]
    if is_ap or "for ap" in t or "ap®" in t:
        return ["3", "4"]
    if title in {"Physics", "Statistics"} or is_high_school:
        return ["3"]
    if any(k in t for k in ["prealgebra", "elementary algebra", "intermediate algebra", "preparing for college success"]):
        return ["3", "4", "5"]
    if any(k in t for k in ["algebra and trigonometry", "precalculus"]):
        return ["3", "4", "5", "6"]
    if t.startswith("college algebra") or t in {"contemporary mathematics", "college success", "college success concise", "writing guide with handbook"}:
        return ["4", "5", "6"]
    if t.startswith("calculus volume"):
        return ["5", "6"]
    if t.startswith("university physics"):
        return ["6"]
    if "nursing" in t or t == "pharmacology for nurses" or t == "nutrition for nurses":
        return ["5", "6"]
    if t in {"additive manufacturing essentials", "workplace software and skills"}:
        return ["3", "4", "5", "6"]
    if any(k in t for k in ["computer science", "python programming", "data science"]):
        return ["3", "4", "5", "6"]
    if t == "concepts of biology":
        return ["3", "4", "5", "6"]
    if any(k in t for k in ["history", "american government"]):
        return ["3", "4", "5", "6"]
    return ["5", "6"]


def openstax_domains(title: str, subjects: str) -> list[str]:
    t = title.lower()
    s = subjects.lower()
    d: set[str] = set()
    if "math" in s or any(k in t for k in ["algebra", "calculus", "precalculus", "statistics", "mathematics"]):
        d.add("mathematics_statistics")
    # Avoid classifying every Social Sciences title as natural science merely
    # because the substring ``science`` occurs in the subject label.  A title
    # may still receive both domains when its catalogue explicitly says both
    # (for example behavioural neuroscience); that is a real overlap rather
    # than a substring artefact.
    if ("social sciences" not in s and "science" in s) or any(k in t for k in ["biology", "chemistry", "physics", "astronomy", "microbiology", "anatomy"]):
        d.add("science")
    if any(k in t for k in ["computer science", "python", "data science", "information systems", "workplace software"]):
        d.add("computing_data")
    if "nursing" in t or "pharmacology" in t or "nutrition for nurses" in t or "anatomy" in t:
        d.add("health")
    if "business" in s or any(k in t for k in ["business", "accounting", "econom", "finance", "management", "marketing", "entrepreneurship", "organizational behavior"]):
        d.add("economics_management")
    if "social sciences" in s or any(k in t for k in ["anthropology", "political", "sociology", "psychology", "lifespan development", "government"]):
        d.add("social_sciences")
    if "humanities" in s or any(k in t for k in ["history", "philosophy", "writing guide"]):
        d.add("humanities_academic_writing")
    if "college success" in t or "preparing for college" in t:
        d.add("academic_transition_study_skills")
    if "manufacturing" in t or "workplace" in t:
        d.add("technical_vocational")
    return sorted(d or {"general_education"})


def needs_for(domains: list[str], title: str) -> list[str]:
    mapping = {
        "mathematics_statistics": ["formal_numeracy", "quantitative_problem_solving"],
        "science": ["scientific_concepts", "laboratory_and_model_reasoning"],
        "computing_data": ["digital_and_data_literacy", "computational_problem_solving"],
        "health": ["health_professional_foundations", "clinical_reasoning"],
        "economics_management": ["economic_and_financial_reasoning", "organization_and_enterprise"],
        "social_sciences": ["social_analysis", "civic_reasoning"],
        "humanities_academic_writing": ["historical_humanistic_understanding", "academic_communication"],
        "academic_transition_study_skills": ["self_directed_learning", "academic_transition"],
        "technical_vocational": ["workplace_and_technical_skills"],
        "early_literacy": ["emergent_literacy", "reading_fluency"],
        "teacher_education": ["pedagogy", "teacher_professional_learning"],
        "agriculture_climate": ["agricultural_and_environmental_problem_solving", "climate_adaptation"],
        "research_methods": ["research_design", "evidence_and_reproducibility"],
        "advanced_research": ["graduate_self_study", "research_reference"],
        "general_education": ["general_postsecondary_learning"],
    }
    out: set[str] = set()
    for d in domains:
        out.update(mapping[d])
    if "exercise" in title.lower() or "skills" in title.lower():
        out.add("practice_and_self_assessment")
    return sorted(out)


def license_obj(identifier: str, adaptation: bool, translation: bool, commercial: bool | None,
                share_alike: bool, status: str, evidence: list[str], caveat: str = "") -> dict:
    return {
        "identifier": identifier,
        "adaptation_allowed": adaptation,
        "translation_allowed": translation,
        "commercial_reuse_allowed": commercial,
        "share_alike_required": share_alike,
        "localization_status": status,
        "caveat": caveat,
        "evidence_ids": evidence,
    }


def record(resource_id: str, provider: str, title: str, url: str, domains: list[str], levels: list[str],
           role: str, completeness: str, scope: str, delivery: dict, license_data: dict,
           accessibility: dict, evidence_ids: list[str], *, contexts: list[str] | None = None,
           needs: list[str] | None = None, limitations: list[str] | None = None,
           source_identity: dict | None = None) -> dict:
    return {
        "resource_id": resource_id,
        "provider": provider,
        "title": title,
        "canonical_url": url,
        "source_identity": source_identity or {},
        "subject_domains": domains,
        "isced_levels": levels,
        "non_isced_contexts": contexts or [],
        "need_functions": needs or needs_for(domains, title),
        "curricular_role": role,
        "completeness": completeness,
        "scope": scope,
        "delivery": delivery,
        "license": license_data,
        "accessibility": accessibility,
        "limitations": limitations or [],
        "evidence_ids": evidence_ids,
    }


def web_access(features: list[str], caveat: str = "Download formats may differ from the web view.") -> dict:
    return {"status": "platform_evidenced_for_web_view", "features": features, "caveat": caveat}


def item_access(caveat: str) -> dict:
    return {"status": "item_or_format_level_check_required", "features": [], "caveat": caveat}


def build_openstax() -> list[dict]:
    rows = list(csv.DictReader(CATALOG.open("r", encoding="utf-8-sig", newline="")))
    if len(rows) != 73:
        raise ValueError(f"Expected 73 OpenStax titles, found {len(rows)}")
    out = []
    for row in rows:
        title = row["title"]
        subjects = row["subjects"]
        domains = openstax_domains(title, subjects)
        levels = openstax_isced(title, subjects, row["is_ap"].lower() == "true", row["is_high_school"].lower() == "true")
        contexts = []
        if any(d in domains for d in ["technical_vocational", "health"]):
            contexts.append("tvet_or_professional")
        delivery = {
            "web": row["web_url"] or None,
            "pdf": row["pdf_url"] or None,
            "bookshare": row["bookshare_url"] or None,
            "audiobook": row["audiobook_url"] or None,
            "editable_source": "DOCX section files described by OpenStax, but access-controlled and not evidenced title-by-title in this catalogue",
            "offline": bool(row["pdf_url"]),
        }
        out.append(record(
            f"openstax-{row['openstax_book_id']}", "OpenStax", title, row["web_url"], domains, levels,
            "single_course_textbook", "course_textbook_not_full_curriculum",
            row["subject_categories"] or subjects,
            delivery,
            license_obj("CC BY-NC-SA 4.0", True, True, False, True, "adaptable_noncommercial",
                        ["SRC-OPENSTAX-LICENSE"],
                        "Current catalogue-level policy; the exact title preface and third-party notices control if they conflict."),
            web_access(
                ["readable structured web text", "image alternative text", "MathML", "detailed descriptions for complex mathematical graphics"]
                + (["title-level Bookshare link is present in the official catalogue"] if row["bookshare_url"] else [])
                + (["title-level audiobook link is present in the official catalogue"] if row["audiobook_url"] else []),
                "The web view is the evidenced accessible baseline. PDF, DOCX, ancillaries, Bookshare and audio availability/status are title- and format-specific."
            ),
            ["SRC-OPENSTAX-CATALOG", "SRC-OPENSTAX-LICENSE", "SRC-OPENSTAX-ACCESS"],
            contexts=contexts,
            source_identity={"openstax_book_id": int(row["openstax_book_id"]), "slug": row["slug"], "catalog_snapshot_sha256": row["snapshot_sha256"]},
        ))
    return out


def add_non_openstax() -> list[dict]:
    A = {"web": True, "pdf": True, "epub": False, "editable_source": True, "offline": True}
    records: list[dict] = []
    records += [
        record("african-storybook-library", "African Storybook", "African Storybook open picture-story library", "https://www.africanstorybook.org/",
               ["early_literacy"], ["0", "1"], "graded_story_library", "large_item_collection",
               "Open picture storybooks for early reading in African languages, with authoring, translation, download and print workflows.",
               {"web": True, "pdf": True, "editable_source": "platform translation/adaptation workflow", "offline": True},
               license_obj("CC BY 4.0 platform policy; item metadata controls", True, True, True, False, "adaptable_item_check", ["SRC-AFRICAN-STORYBOOK"], "Check the license and attribution on each selected story."),
               item_access("Accessibility must be checked per story/PDF; image-rich content requires complete alternative descriptions."), ["SRC-AFRICAN-STORYBOOK"],
               needs=["emergent_literacy", "reading_fluency", "home_or_self_directed_reading"]),
        record("gdl-early-reading", "Global Digital Library", "Global Digital Library early-grade reading collection", "https://content.digitallibrary.io/",
               ["early_literacy"], ["0", "1"], "graded_reading_collection", "large_item_collection",
               "Curated early-grade reading resources in exact language varieties.",
               {"web": True, "pdf": "item-dependent", "editable_source": "item-dependent", "offline": "item-dependent"},
               license_obj("item-level; primarily CC BY or CC BY-SA", True, True, None, False, "item_level_license_check", ["SRC-GDL-LICENSE"], "The selected item's displayed license is controlling."),
               item_access("Format and accessibility are item-specific."), ["SRC-GDL-LICENSE"], needs=["emergent_literacy", "reading_fluency"]),
        record("gdl-early-math", "Global Digital Library", "Global Digital Library early-grade mathematics collection", "https://content.digitallibrary.io/",
               ["mathematics_statistics"], ["0", "1"], "early_numeracy_collection", "item_collection",
               "Early mathematics materials exposed by the GDL platform.",
               {"web": True, "pdf": "item-dependent", "editable_source": "item-dependent", "offline": "item-dependent"},
               license_obj("item-level; primarily CC BY or CC BY-SA", True, True, None, False, "item_level_license_check", ["SRC-GDL-LICENSE"], "The selected item's displayed license is controlling."),
               item_access("Format and accessibility are item-specific."), ["SRC-GDL-LICENSE"], needs=["early_numeracy", "foundational_problem_solving"]),
    ]

    siy_license = license_obj("CC BY for selected unbranded EPUB; CC BY-ND for branded PDF", True, True, True, False,
                              "format_selective_adaptable", ["SRC-SIYAVULA"],
                              "Use only the exact CC BY unbranded edition as a translation master; ND files may be redistributed unchanged but not translated.")
    siy_acc = item_access("No collection-wide accessibility conformance statement was established; inspect the exact EPUB/PDF and rebuild accessible math/figures.")
    for rid, title, levels, scope in [
        ("siyavula-math-7-12", "Siyavula Mathematics Grades 7–12", ["2", "3"], "Six-grade CAPS mathematics sequence with teacher guides."),
        ("siyavula-math-literacy-10", "Siyavula Mathematical Literacy Grade 10", ["3"], "Applied upper-secondary mathematical literacy textbook and teacher guide."),
        ("siyavula-natural-science-4-9", "Siyavula Natural Sciences and Technology Grades 4–9", ["1", "2"], "Six-grade CAPS natural science/technology sequence with teacher guides."),
        ("siyavula-physical-science-10-12", "Siyavula Physical Sciences Grades 10–12", ["3"], "Three-grade CAPS physical-science sequence with teacher guides."),
        ("siyavula-life-science-10", "Siyavula Life Sciences Grade 10", ["3"], "Upper-secondary life-science textbook and teacher guide."),
    ]:
        domains = ["mathematics_statistics"] if "Math" in title else ["science"]
        records.append(record(rid, "Siyavula", title, "https://www.siyavula.com/read", domains, levels,
                              "subject_sequence" if "Grades" in title else "single_course_textbook",
                              "grade_bounded_sequence", scope,
                              {"web": True, "pdf": "CC BY-ND branded", "epub": "CC BY unbranded available for many listed titles", "offline": True},
                              siy_license, siy_acc, ["SRC-SIYAVULA"]))

    records += [
        record("phet-interactive-simulations", "PhET", "PhET Interactive Simulations", "https://phet.colorado.edu/",
               ["science", "mathematics_statistics"], ["1", "2", "3", "4", "5", "6"], "interactive_supplement", "large_simulation_collection",
               "Interactive simulations across physics, chemistry, mathematics, earth science and biology.",
               {"web": True, "interactive": True, "offline": True, "editable_source": False},
               license_obj("CC BY-NC 4.0 for regular HTML5 simulations", True, True, False, False, "adaptable_noncommercial_with_brand_constraints", ["SRC-PHET"], "Exact simulation and branding/source-code terms must be checked."),
               {"status": "subset_evidenced", "features": ["inclusive features exist in a subset of simulations"], "caveat": "Do not infer collection-wide keyboard, screen-reader or sonification support."},
               ["SRC-PHET"], limitations=["Supplement, not a textbook or curriculum.", "Interactive localization requires interface and dynamic-description QA."]),
        record("cs-unplugged", "CS Unplugged", "CS Unplugged", "https://www.csunplugged.org/en/",
               ["computing_data"], ["1", "2", "3"], "activity_collection", "multi_topic_supplement",
               "Printable computer-science activities designed to work without computers, primarily for ages 5–12 but adaptable upward.",
               {"web": True, "pdf": True, "editable_source": True, "offline": True},
               license_obj("CC BY-SA 4.0 current-site material", True, True, True, True, "adaptable", ["SRC-CS-UNPLUGGED"], "Check any linked classic-site or third-party item separately."),
               item_access("Printable formats aid offline use; a collection-wide digital-accessibility audit was not established."), ["SRC-CS-UNPLUGGED"],
               needs=["computational_thinking", "algorithmic_reasoning", "low_device_computing_education"]),
    ]

    openintro_license = license_obj("CC BY-SA 3.0 (exact-title notices control)", True, True, True, True, "adaptable_with_title_trademark_checks", ["SRC-OPENINTRO"], "Derivative titles and trademarks require compliance with OpenIntro's title-specific guidance.")
    records += [
        record("openintro-statistics", "OpenIntro", "OpenIntro Statistics", "https://www.openintro.org/book/os/",
               ["mathematics_statistics", "computing_data"], ["3", "4", "5", "6"], "single_course_textbook", "complete_introductory_course_textbook",
               "Introductory statistics for high school, college or self-study.",
               {"web": True, "pdf": True, "screen_reader_pdf": True, "offline": True, "editable_source": "title repository/material dependent"}, openintro_license,
               {"status": "format_specific_evidence", "features": ["screen-reader-oriented PDF with expanded navigation and image alternative text"], "caveat": "Use the designated accessible PDF, not any PDF interchangeably."}, ["SRC-OPENINTRO"]),
        record("openintro-modern-statistics", "OpenIntro", "Introduction to Modern Statistics, second edition", "https://www.openintro.org/book/ims/",
               ["mathematics_statistics", "computing_data"], ["3", "4", "5", "6"], "single_course_textbook", "complete_introductory_course_textbook",
               "Exploratory data analysis, simulation-based inference, traditional inference, exercises, R tutorials and labs.",
               {"web": True, "pdf": True, "editable_source": "GitHub/bookdown source", "offline": True, "interactive": "tutorials require browser"}, openintro_license,
               item_access("HTML structure is available, but no complete edition-wide conformance claim was established."), ["SRC-OPENINTRO"]),
    ]

    active_license = license_obj("CC BY-SA", True, True, True, True, "adaptable", ["SRC-ACTIVE-CALCULUS"], "Exact edition license file controls.")
    for rid, title, levels, scope in [
        ("active-prelude", "Active Prelude to Calculus", ["3", "4", "5", "6"], "Functions and precalculus preparation through active-learning activities and exercises."),
        ("active-calculus-single", "Active Calculus (single variable)", ["5", "6"], "Single-variable calculus with preparatory/in-class activities and exercises."),
        ("active-calculus-multivariable", "Active Calculus Multivariable", ["6", "7"], "Multivariable calculus with active-learning activities and exercises."),
    ]:
        records.append(record(rid, "Active Calculus", title, "https://activecalculus.org/", ["mathematics_statistics"], levels,
                              "single_course_textbook", "complete_course_textbook", scope,
                              {"web": True, "pdf": True, "editable_source": "GitHub source", "offline": True, "interactive": "optional web exercises"},
                              active_license, item_access("HTML is available; interactive exercise accessibility must be audited separately."), ["SRC-ACTIVE-CALCULUS"]))

    carp_license = license_obj("CC BY 4.0 for lesson text unless specified; software MIT", True, True, True, False, "adaptable_item_check", ["SRC-CARPENTRIES"], "Images and individual lesson notices must be checked.")
    for rid, title, url, scope in [
        ("carpentries-unix-shell", "The Unix Shell", "https://swcarpentry.github.io/shell-novice/", "Command-line navigation, files, pipes, loops and automation for researchers."),
        ("carpentries-git", "Version Control with Git", "https://swcarpentry.github.io/git-novice/", "Version control and collaboration for research workflows."),
        ("carpentries-python", "Programming with Python", "https://swcarpentry.github.io/python-novice-inflammation/", "Introductory Python through reproducible data analysis."),
        ("carpentries-r", "R for Reproducible Scientific Analysis", "https://swcarpentry.github.io/r-novice-gapminder/", "Introductory R, data processing and visualization with reproducibility."),
        ("carpentries-sql", "Using Databases and SQL", "https://swcarpentry.github.io/sql-novice-survey/", "Relational databases and SQL for research data."),
        ("carpentries-ecology", "Data Carpentry Ecology workshop", "https://datacarpentry.org/lessons/#ecology-workshop", "Coherent ecology-data curriculum spanning spreadsheets/OpenRefine, R or Python, and SQL."),
    ]:
        records.append(record(rid, "The Carpentries", title, url, ["computing_data", "research_methods"], ["4", "5", "6", "7", "8"],
                              "workshop_lesson" if "workshop" not in title.lower() else "workshop_curriculum",
                              "self_contained_lesson_or_bounded_workshop", scope,
                              {"web": True, "pdf": "lesson dependent", "editable_source": "public source repository", "offline": "source snapshot/render possible"},
                              carp_license, item_access("The collection offers accessibility support, but lesson-level semantic, code-block and visual checks remain necessary."),
                              ["SRC-CARPENTRIES"], contexts=["adult_professional_nonformal"], needs=["research_computing", "reproducible_data_workflows", "self_directed_practice"]))

    records += [
        record("turing-way", "The Turing Way community", "The Turing Way", "https://the-turing-way.netlify.app/",
               ["computing_data", "research_methods"], ["5", "6", "7", "8"], "reference_handbook", "modular_handbook",
               "Guides to reproducible, ethical and collaborative data science, project design, communication and collaboration.",
               {"web": True, "pdf": "build dependent", "editable_source": "public GitHub repository", "offline": "repository clone/build"},
               license_obj("CC BY 4.0 documentation; MIT software", True, True, True, False, "adaptable", ["SRC-TURING-WAY"], "Third-party media and code dependencies must be checked."),
               item_access("A complete version-wide accessibility conformance claim was not established."), ["SRC-TURING-WAY"],
               needs=["open_science", "reproducibility", "research_ethics", "collaborative_research"]),
        record("tessa-all-africa", "TESSA / The Open University", "TESSA — English — All Africa", "https://www.open.edu/openlearncreate/course/view.php?id=2042",
               ["teacher_education", "early_literacy", "mathematics_statistics", "science"], ["3", "4", "5", "6", "7"], "teacher_education_library", "multi_subject_professional_learning_collection",
               "Primary-subject pedagogy, foundational literacy/numeracy, lower-secondary science, inclusion, school experience and teacher-educator toolkits.",
               {"web": True, "pdf": True, "editable_source": "Word library", "offline": "complete PDF and Word ZIP", "audio": True},
               license_obj("CC BY-SA 4.0 except third-party material", True, True, True, True, "adaptable_with_third_party_audit", ["SRC-TESSA"], "Third-party material is excluded and must be removed, replaced or separately cleared."),
               item_access("Word/PDF/audio formats support several access routes; exact accessibility must be checked after localization."), ["SRC-TESSA"],
               contexts=["teacher_professional_development", "adult_professional_nonformal"], needs=["teacher_content_knowledge", "pedagogy", "inclusive_education", "foundational_skills_instruction"]),
        record("teaching-digital-age-3", "BCcampus Pressbooks", "Teaching in a Digital Age, third edition", "https://pressbooks.bccampus.ca/teachinginadigitalagev3m/",
               ["teacher_education"], ["5", "6", "7", "8"], "professional_reference_textbook", "complete_book_not_certification_program",
               "Decision framework for teaching, course design and learning with digital technologies.",
               {"web": True, "pdf": True, "epub": True, "editable_source": "XHTML and Pressbooks XML exports", "offline": True},
               license_obj("CC BY-NC 4.0 except where noted", True, True, False, False, "adaptable_noncommercial", ["SRC-DIGITAL-AGE"], "Audit exceptions and embedded third-party content."),
               item_access("Multiple structured formats exist; no complete conformance claim was established."), ["SRC-DIGITAL-AGE"], contexts=["teacher_professional_development"]),
    ]

    rn_license = license_obj("CC BY 4.0", True, True, True, False, "adaptable_with_clinical_localization", ["SRC-OPENRN-FUNDAMENTALS", "SRC-OPENRN-SKILLS"], "Clinical law, scope, protocol, drug naming and examination alignment require jurisdiction-specific revision.")
    records += [
        record("openrn-nursing-fundamentals-2e", "Open RN / NCBI Bookshelf", "Nursing Fundamentals, second edition", "https://www.ncbi.nlm.nih.gov/books/NBK610815/",
               ["health"], ["4", "5", "6"], "single_course_textbook", "entry_level_professional_course_textbook",
               "Prelicensure nursing fundamentals with learning activities and answers.",
               {"web": True, "pdf": True, "editable_source": "bulk/offline formats", "offline": True, "interactive": "some activities web-dependent"}, rn_license,
               item_access("NCBI HTML is structured; clinical figures, tables and interactives need exact accessible-format checks."), ["SRC-OPENRN-FUNDAMENTALS"], contexts=["tvet_or_professional"]),
        record("openrn-nursing-skills-2e", "Open RN / NCBI Bookshelf", "Nursing Skills, second edition", "https://www.ncbi.nlm.nih.gov/books/NBK596735/",
               ["health"], ["4", "5", "6"], "single_course_textbook", "entry_level_professional_course_textbook",
               "Evidence-based entry-level clinical skills, assessment, calculation, checklists, video links and answer key.",
               {"web": True, "pdf": True, "editable_source": "bulk/offline formats", "offline": True, "interactive": "online version required for interactive activities"}, rn_license,
               item_access("NCBI HTML is structured; videos and interactives require separate caption/keyboard/description checks."), ["SRC-OPENRN-SKILLS"], contexts=["tvet_or_professional"]),
        record("openwho-hub", "World Health Organization", "OpenWHO health-emergency resource hub", "https://openwho.org/",
               ["health"], ["3", "4", "5", "6", "7", "8"], "reference_and_training_collection", "item_variable",
               "Current health-emergency learning materials in web/video/document formats.",
               {"web": True, "pdf": "item dependent", "video": "item dependent", "offline": "item dependent", "editable_source": False},
               license_obj("general personal/noncommercial access terms; item-level permissions may differ", False, False, False, False, "access_only_until_item_permission_verified", ["SRC-OPENWHO"], "Do not translate or adapt from the general hub terms alone."),
               item_access("Accessibility and download modes are item-specific."), ["SRC-OPENWHO"], contexts=["adult_professional_nonformal"], limitations=["Reference/access candidate, not a verified translation master."]),
    ]

    records += [
        record("soil-science-2e", "Iowa State University Digital Press", "Introduction to Soil Science, second edition", "https://iastate.pressbooks.pub/isudp-2025-201/",
               ["agriculture_climate", "science"], ["4", "5", "6"], "single_course_textbook", "complete_introductory_course_textbook",
               "Soil formation, classification, physical/chemical properties, biology, erosion, management and fertility.",
               {"web": True, "pdf": True, "epub": True, "editable_source": "Pressbooks export availability must be checked", "offline": True},
               license_obj("CC BY 4.0 except where noted", True, True, True, False, "adaptable_with_third_party_audit", ["SRC-SOIL-SCIENCE"], "Check chapter/media exceptions."),
               item_access("Structured web and reflowable EPUB exist; equation/image accessibility remains to be checked."), ["SRC-SOIL-SCIENCE"], contexts=["tvet_or_professional"]),
        record("environmental-biology", "Open Textbook Library", "Environmental Biology", "https://open.umn.edu/opentextbooks/textbooks/687",
               ["agriculture_climate", "science", "health"], ["3", "4", "5", "6"], "single_course_textbook", "complete_introductory_course_textbook",
               "Ecology, environmental health/hazards, water, food/hunger, agriculture, climate change, biodiversity and energy.",
               {"web": True, "pdf": True, "ebook": True, "editable_source": "XML/ODF listed", "offline": True},
               license_obj("CC BY", True, True, True, False, "adaptable", ["SRC-ENV-BIOLOGY"], "Exact edition and third-party media notices control."),
               item_access("Multiple formats exist; a complete conformance claim was not established."), ["SRC-ENV-BIOLOGY"]),
        record("fao-climate-smart-agriculture-manual", "FAO", "Climate-smart agriculture training manual", "https://elearning.fao.org/pluginfile.php/506774/mod_scorm/content/1/story_content/external_files/CA2189EN.pdf",
               ["agriculture_climate"], ["4", "5", "6", "7"], "training_manual", "bounded_professional_manual",
               "Climate-smart agriculture concepts and training activities for practitioners.",
               {"web": False, "pdf": True, "editable_source": False, "offline": True},
               license_obj("CC BY-NC-SA 3.0 IGO", True, True, False, True, "adaptable_noncommercial_with_igo_terms", ["SRC-FAO-CSA"], "Translation must carry FAO's mandated disclaimer; third-party material remains excluded."),
               item_access("PDF accessibility was not established."), ["SRC-FAO-CSA"], contexts=["tvet_or_professional", "adult_professional_nonformal"]),
        record("fao-farmer-field-school-intro", "FAO", "Introduction to the Farmer Field School Approach", "https://elearning.fao.org/course/view.php?id=724&lang=en",
               ["agriculture_climate", "teacher_education"], ["4", "5", "6", "7"], "short_training_course", "bounded_course",
               "Practitioner introduction to field-based participatory learning.",
               {"web": True, "pdf": "learner notes may be course dependent", "editable_source": False, "offline": "course dependent"},
               license_obj("general educational/personal-use terms; no blanket derivative grant established", False, False, False, False, "access_only_until_item_permission_verified", ["SRC-FAO-FFS"], "Seek an exact openly licensed manual or explicit permission before translation."),
               item_access("Course accessibility and offline package must be checked directly."), ["SRC-FAO-FFS"], contexts=["adult_professional_nonformal"]),
    ]

    core_license = license_obj("CC BY-NC-ND (current resource terms; exact edition controls)", False, False, False, False, "reference_only_no_derivatives", ["SRC-CORE-ECON"], "NoDerivatives blocks translation/adaptation without separate permission.")
    for rid, title, scope in [
        ("core-economy-micro-2", "The Economy 2.0: Microeconomics", "Introductory microeconomics with empirical and institutional framing."),
        ("core-economy-macro-2", "The Economy 2.0: Macroeconomics", "Introductory macroeconomics with empirical and institutional framing."),
        ("core-doing-economics", "Doing Economics", "Data-based empirical projects and methods supporting economics courses."),
    ]:
        core_domains = ["economics_management", "computing_data"] if "Doing" in title else ["economics_management"]
        records.append(record(rid, "CORE Econ", title, "https://www.core-econ.org/", core_domains, ["3", "4", "5", "6"],
                              "single_course_textbook" if "Doing" not in title else "empirical_project_supplement", "complete_course_resource", scope,
                              {"web": True, "pdf": True, "editable_source": False, "offline": True, "interactive": True}, core_license,
                              item_access("Interactive and downloadable formats require separate checks."), ["SRC-CORE-ECON"], limitations=["Strong reference candidate but not an unpermissioned translation master."]))

    records += [
        record("doing-research", "Kwantlen Polytechnic University / Open Textbook Library", "Doing Research", "https://open.umn.edu/opentextbooks/textbooks/905",
               ["research_methods", "humanities_academic_writing"], ["3", "4", "5", "6", "7"], "research_skills_primer", "bounded_four_module_primer",
               "Research questions, source discovery, source evaluation and basic research communication.",
               {"web": True, "pdf": True, "ebook": True, "editable_source": "XML listed", "offline": True},
               license_obj("CC BY", True, True, True, False, "adaptable", ["SRC-DOING-RESEARCH"], "Exact edition and embedded media notices control."),
               item_access("Multiple formats exist; a complete conformance claim was not established."), ["SRC-DOING-RESEARCH"], needs=["information_literacy", "research_question_design", "source_evaluation"]),
        record("mit-ocw-repository", "MIT OpenCourseWare", "MIT OpenCourseWare", "https://ocw.mit.edu/",
               ["science", "mathematics_statistics", "computing_data", "economics_management", "humanities_academic_writing", "research_methods"], ["3", "4", "5", "6", "7", "8"],
               "course_repository", "course_completeness_varies",
               "Thousands of introductory through graduate course sites; many include syllabus, notes, assignments, exams, video or full texts.",
               {"web": True, "pdf": "course dependent", "video": "course dependent", "editable_source": "course dependent", "offline": "course download available"},
               license_obj("CC BY-NC-SA 4.0 platform content; third-party items excluded", True, True, False, True, "item_level_rights_audit", ["SRC-MIT-OCW"], "Each course's readings, media and third-party components require a rights inventory."),
               item_access("Accessibility and completeness vary by course and format."), ["SRC-MIT-OCW"], limitations=["Repository, not a single curriculum; map exact courses before localization."]),
        record("stacks-project", "The Stacks Project", "The Stacks Project", "https://stacks.math.columbia.edu/",
               ["advanced_research", "mathematics_statistics"], ["7", "8"], "research_reference_work", "continuously_developed_reference",
               "Algebraic geometry and algebraic stacks, including foundations in commutative algebra, schemes, algebraic spaces and cohomology.",
               {"web": True, "pdf": True, "editable_source": "TeX archive", "offline": True},
               license_obj("GNU Free Documentation License", True, True, True, True, "adaptable_under_gfdl", ["SRC-STACKS"], "Comply with GFDL notices, invariant-section terms if any, and source attribution; do not relabel as Creative Commons."),
               item_access("Hyperlinked web and PDFs exist, but no complete screen-reader/MathML conformance claim was established."), ["SRC-STACKS"],
               needs=["graduate_self_study", "research_reference", "algebraic_geometry_research"], limitations=["Explicitly not introductory."]),
    ]

    olp_license = license_obj("CC BY 4.0 except where noted", True, True, True, False, "adaptable", ["SRC-OLP-ABOUT", "SRC-OLP-BUILDS"], "Audit any separately incorporated material or title-specific permission note.")
    records += [
        record("olp-modular-corpus", "Open Logic Project", "Open Logic Text modular corpus", "https://builds.openlogicproject.org/open-logic-complete.pdf",
               ["advanced_research", "mathematics_statistics", "computing_data", "humanities_academic_writing"], ["6", "7", "8"], "modular_source_corpus", "broad_but_not_textbook_complete",
               "Intermediate formal logic/metalogic modules: set theory, propositional/FOL syntax and semantics, proof systems, completeness, model theory, computability, incompleteness, modal/intuitionistic/counterfactual/second-order logic.",
               {"web": True, "pdf": True, "editable_source": "LaTeX repository/ZIP", "offline": True}, olp_license,
               item_access("Screen PDFs exist; a corpus-wide semantic-accessibility conformance claim was not established."), ["SRC-OLP-ABOUT", "SRC-OLP-BUILDS"],
               limitations=["The complete build is expressly an inventory, not a textbook; assemble a course-specific reader."]),
        record("forallx-calgary", "Open Logic Project", "forall x: Calgary", "https://forallx.openlogicproject.org/",
               ["mathematics_statistics", "humanities_academic_writing"], ["3", "4", "5", "6"], "single_course_textbook", "complete_introductory_course_textbook",
               "Introductory propositional and first-order logic, symbolization, semantics, natural deduction, exercises and solutions; some modal/metalogical topics.",
               {"web": True, "pdf": True, "editable_source": "LaTeX repository", "offline": "PDF and SCORM ZIP", "lms_package": "SCORM"},
               license_obj("CC BY 4.0", True, True, True, False, "adaptable", ["SRC-FORALLX"], "Some incorporated material is used with permission; inspect source notices before redistribution of a derivative."),
               {"status": "format_specific_evidence", "features": ["dyslexia-oriented PDF", "experimental HTML with accessibility features"], "caveat": "The HTML is experimental and omits solutions; 'accessible PDF' is described specifically for dyslexic readers, not as universal conformance."},
               ["SRC-FORALLX"]),
    ]
    olp_books = [
        ("olp-sets-logic-computation", "Sets, Logic, Computation", "https://slc.openlogicproject.org/", ["6", "7"], "Set theory, first-order logic, proof systems, Turing machines and undecidability."),
        ("olp-incompleteness-computability", "Incompleteness and Computability", "https://ic.openlogicproject.org/", ["6", "7", "8"], "Recursive functions, incompleteness, arithmetic models, second-order logic and lambda calculus."),
        ("olp-boxes-diamonds", "Boxes and Diamonds", "https://bd.openlogicproject.org/", ["6", "7"], "Modal and intensional logics, intuitionistic logic and counterfactuals."),
        ("olp-set-theory-open-intro", "Set Theory: An Open Introduction", "https://st.openlogicproject.org/", ["5", "6", "7"], "Philosophy and foundations of set theory, arithmetic in set theory, cumulative hierarchy and ZFC motivation."),
        ("olp-intermediate-logic", "Intermediate Logic", "https://builds.openlogicproject.org/courses/phil310/il-screen.pdf", ["6", "7"], "Naive set theory, first-order logic through completeness, recursive functions, incompleteness and models of arithmetic."),
        ("olp-what-if", "What If? An Open Introduction to Non-classical Logics", "https://builds.openlogicproject.org/courses/what-if/wi-screen.pdf", ["6", "7"], "Classical, many-valued, modal, epistemic, temporal, conditional and intuitionistic logic; incomplete draft."),
    ]
    for rid, title, url, levels, scope in olp_books:
        records.append(record(rid, "Open Logic Project", title, url,
                              ["mathematics_statistics", "humanities_academic_writing", "computing_data"], levels,
                              "assembled_textbook", "incomplete_draft" if title.startswith("What If") else "course_textbook",
                              scope, {"web": "landing/build page", "pdf": True, "editable_source": "LaTeX repository", "offline": True},
                              olp_license, item_access("Screen/print PDF availability is evidenced; full assistive-technology behavior is not."),
                              ["SRC-OLP-BUILDS", "SRC-OLP-ABOUT"], limitations=["Requires prior introductory logic."] if "What If" not in title and "Set Theory" not in title else (["Explicitly incomplete draft."] if "What If" in title else [])))
    return records


def build_report(doc: dict) -> str:
    records = doc["resources"]
    provider_counts = Counter(r["provider"] for r in records)
    role_counts = Counter(r["curricular_role"] for r in records)
    level_counts = Counter(level for r in records for level in r["isced_levels"])
    domain_counts = Counter(domain for r in records for domain in r["subject_domains"])
    os_rows = [r for r in records if r["provider"] == "OpenStax"]
    non_os = [r for r in records if r["provider"] != "OpenStax"]

    lines = [
        "# Open-resource canon map by educational stage and subject",
        "",
        f"Generated: {doc['generated_at']}",
        "",
        "## Scope and decision boundary",
        "",
        "This is a **source-canon map, not a ranking**. It identifies exact open or free-to-read educational resources, maps them to ISCED stages and functional needs, and separates a full curriculum from a course text, module collection, supplement, training manual, repository, or research reference. It does not use any local translation, programme-completion, audience, or production fact as a baseline or as a reason to include/exclude a language or population.",
        "",
        "The map treats four questions independently: (1) is the resource educationally relevant; (2) is it complete for its claimed role; (3) does its license actually permit translation/adaptation; and (4) which delivery/accessibility features are evidenced. Free access alone is not permission to translate.",
        "",
        "## Audit result",
        "",
        f"- {len(records)} exact resource records are mapped: {len(os_rows)} OpenStax catalogue titles and {len(non_os)} non-OpenStax resources or bounded series.",
        "- No OpenStax title is classified as a full multi-stage curriculum. Each is a single-course textbook; several titles can form a spine only after an explicit sequence and gap analysis.",
        "- The Open Logic complete build is a modular corpus/inventory, not a textbook. `forall x: Calgary` supplies the introductory course; six remixed books supply intermediate/advanced pathways, with `What If?` explicitly incomplete.",
        "- The strongest directly adaptable gaps around the OpenStax spine are early literacy/early numeracy, primary and secondary grade sequences, teacher education, research-computing/open-science skills, health-professional foundations, agriculture/climate, and advanced research references.",
        "- NoDerivatives and access-only resources remain useful references but are explicitly excluded as unpermissioned translation masters. This affects branded Siyavula PDFs, CORE Econ editions under ND terms, OpenWHO under general hub terms, and the audited FAO Farmer Field School course unless an exact openly licensed source is located.",
        "- Accessibility is format-specific: OpenStax's web view has the strongest platform-level evidence; OpenIntro exposes a screen-reader-oriented PDF; PhET has inclusive features in a subset; most other entries require item/format auditing. A PDF link is not itself accessibility evidence.",
        "",
        "## ISCED crosswalk",
        "",
        "ISCED levels classify formal programmes. TVET, professional development, and adult/nonformal contexts are recorded separately rather than invented as an extra ISCED level.",
        "",
        "| Level | Label | Mapped record count |",
        "|---:|---|---:|",
    ]
    for item in ISCED:
        lines.append(f"| {item['level']} | {item['label']} | {level_counts[item['level']]} |")

    lines += [
        "",
        "## Stage-to-need canon",
        "",
        "| Stage | Functional need | Primary adaptable candidates | Role boundary |",
        "|---|---|---|---|",
        "| ISCED 0–1 | emergent literacy and reading fluency | African Storybook; Global Digital Library early reading | story/reading collections, not a complete national literacy curriculum |",
        "| ISCED 0–1 | early numeracy and primary science | GDL early mathematics; Siyavula Natural Sciences and Technology Grades 4–6 (upper primary) | GDL is item-level; Siyavula requires the exact CC BY edition |",
        "| ISCED 1–3 | mathematics and science sequences | Siyavula Mathematics 7–12; Natural Sciences 4–9; Physical Sciences 10–12; selected OpenStax high-school titles; PhET | grade/subject sequences plus simulation supplement, not a whole school curriculum |",
        "| ISCED 1–3 | computing concepts with low device dependence | CS Unplugged | activity collection/supplement |",
        "| ISCED 3–6 | algebra, calculus, statistics and introductory STEM | exact OpenStax titles; OpenIntro; Active Prelude/Calculus; selected Siyavula sequences | course texts and subject sequences |",
        "| ISCED 4–6 / TVET | nursing and health-professional foundations | Open RN Fundamentals and Nursing Skills; exact OpenStax nursing texts | course texts; clinical/legal localization is mandatory |",
        "| ISCED 4–7 / adult | agriculture, soil, climate and field learning | Introduction to Soil Science; Environmental Biology; FAO climate-smart agriculture manual | textbooks/manual; FFS course is reference-only until rights are verified |",
        "| ISCED 5–8 / professional | teacher education | TESSA; Teaching in a Digital Age | professional library/reference, not teacher certification |",
        "| ISCED 4–8 / adult | research computing, reproducibility and open science | Carpentries exact lessons/workshop; The Turing Way; Doing Research | skills lessons, handbook and primer; not a disciplinary methods curriculum |",
        "| ISCED 3–6 | economics, finance and management | exact OpenStax economics/accounting/finance/management titles | adaptable course-text spine; CORE Econ is reference-only under ND terms |",
        "| ISCED 3–6 | introductory formal logic | forall x: Calgary | full introductory course textbook |",
        "| ISCED 6–8 | intermediate/advanced logic | Open Logic modular corpus and assembled books | modular corpus/course texts; complete corpus is not a textbook |",
        "| ISCED 7–8 | advanced mathematics research | Stacks Project; advanced MIT OCW courses | reference/repository, not introductory curriculum |",
        "",
        "## Subject coverage counts",
        "",
        "Counts are descriptive overlap counts, not importance scores; one resource may serve several domains.",
        "",
        "| Subject domain | Records |",
        "|---|---:|",
    ]
    for domain, count in sorted(domain_counts.items()):
        lines.append(f"| {domain.replace('_', ' ')} | {count} |")

    lines += [
        "",
        "## Curricular-role counts",
        "",
        "| Role | Records |",
        "|---|---:|",
    ]
    for role, count in sorted(role_counts.items()):
        lines.append(f"| {role.replace('_', ' ')} | {count} |")

    lines += [
        "",
        "## Exact OpenStax catalogue mapping (73 titles)",
        "",
        "Every row is classified as `single_course_textbook`, never `full_curriculum`. The current OpenStax platform policy is CC BY-NC-SA 4.0; exact title prefaces and third-party notices remain controlling. `Web accessibility` means the platform-level web-view evidence (structured text, alt text, MathML, detailed descriptions), not automatic equivalence of PDF/DOCX.",
        "",
        "| ID | Title | ISCED | Domains | Offline PDF | Bookshare | Audio |",
        "|---:|---|---|---|:---:|:---:|:---:|",
    ]
    for r in sorted(os_rows, key=lambda x: x["title"].casefold()):
        sid = r["source_identity"]["openstax_book_id"]
        d = ", ".join(x.replace("_", " ") for x in r["subject_domains"])
        lines.append(f"| {sid} | {r['title']} | {', '.join(r['isced_levels'])} | {d} | {'yes' if r['delivery']['pdf'] else 'no'} | {'yes' if r['delivery']['bookshare'] else 'no'} | {'yes' if r['delivery']['audiobook'] else 'no'} |")

    lines += [
        "",
        "## Non-OpenStax exact resources",
        "",
        "| Resource | Provider | ISCED | Role | Localization-rights status | Offline evidence |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(non_os, key=lambda x: (x["provider"].casefold(), x["title"].casefold())):
        offline = r["delivery"].get("offline", False)
        lines.append(f"| [{r['title']}]({r['canonical_url']}) | {r['provider']} | {', '.join(r['isced_levels'])} | {r['curricular_role'].replace('_', ' ')} | {r['license']['localization_status'].replace('_', ' ')} | {offline} |")

    lines += [
        "",
        "## License and accessibility gates",
        "",
        "1. **Adaptable master:** CC BY, CC BY-SA, CC BY-NC, CC BY-NC-SA, or GFDL can permit translation, subject to their exact conditions and exclusions. NonCommercial restrictions are recorded rather than erased.",
        "2. **NoDerivatives:** an ND edition can be redistributed unchanged but cannot serve as a translation master without separate permission. For Siyavula, select the unbranded CC BY EPUB rather than the branded CC BY-ND PDF.",
        "3. **Item-level repositories:** Global Digital Library, MIT OCW, and similar repositories require a rights/accessibility inventory of the exact selected items. A platform license does not absorb third-party works.",
        "4. **Access-only:** OpenWHO and the audited FAO Farmer Field School course remain educational references until an exact derivative-work grant or openly licensed source is verified.",
        "5. **Accessibility:** preserve semantic structure, alternative descriptions, MathML/accessible equations, keyboard operation, captions/transcripts, reflow, and low-bandwidth/offline routes. Claims are restricted to the exact format evidenced.",
        "",
        "## Structural gaps after mapping",
        "",
        "These are canon gaps, not population priorities:",
        "",
        "- No single audited provider supplies a complete ISCED 0–8 curriculum across literacy, mathematics, science, health, computing, civic/economic learning, teacher education and research.",
        "- The 73-title OpenStax catalogue is broad at upper-secondary/tertiary level but does not supply a full early-childhood/primary spine, a school-wide grade sequence, a teacher-certification programme, a complete agriculture curriculum, or a general empirical research-methods sequence.",
        "- Early literacy collections need sequence/level metadata and item-level rights/accessibility checks before being called a curriculum.",
        "- Nursing, agriculture, law, government, accounting and professional practice texts carry jurisdictional/local-condition content that must be localized, not merely translated.",
        "- Interactive simulations, labs, code, quizzes and video are separate localization/accessibility units from textbook prose.",
        "- Advanced reference works such as Open Logic and the Stacks Project are educationally important at ISCED 7–8, but they do not substitute for earlier-stage foundations.",
        "",
        "## Evidence register",
        "",
        "| ID | Organization | Source | Hash status |",
        "|---|---|---|---|",
    ]
    for s in doc["evidence_sources"]:
        url = s["url"]
        hash_status = s.get("content_sha256") or "official URL; not locally snapshotted"
        lines.append(f"| {s['id']} | {s['organization']} | [{s['title']}]({url}) | {hash_status} |")

    lines += [
        "",
        "## Reproducibility",
        "",
        f"- Input catalogue: `{CATALOG.name}` — {CATALOG.stat().st_size:,} bytes — SHA-256 `{sha256(CATALOG)}`.",
        f"- JSON schema identifier: `{doc['schema']}`.",
        "- The JSON contains the complete record-level evidence and caveats; this report is the human-readable projection.",
        "- Output SHA-256 values are reported externally after generation because a file cannot contain its own stable digest without a separate sidecar.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    resources = build_openstax() + add_non_openstax()
    ids = [r["resource_id"] for r in resources]
    if len(ids) != len(set(ids)):
        dupes = [k for k, v in Counter(ids).items() if v > 1]
        raise ValueError(f"Duplicate resource ids: {dupes}")
    allowed_levels = {x["level"] for x in ISCED}
    bad_levels = sorted({l for r in resources for l in r["isced_levels"] if l not in allowed_levels})
    if bad_levels:
        raise ValueError(f"Invalid ISCED levels: {bad_levels}")
    evidence_ids = {s["id"] for s in SOURCES}
    unknown_refs = sorted({e for r in resources for e in r["evidence_ids"] + r["license"]["evidence_ids"] if e not in evidence_ids})
    if unknown_refs:
        raise ValueError(f"Unknown evidence ids: {unknown_refs}")
    duplicate_domain_records = sorted(r["resource_id"] for r in resources if len(r["subject_domains"]) != len(set(r["subject_domains"])))
    duplicate_level_records = sorted(r["resource_id"] for r in resources if len(r["isced_levels"]) != len(set(r["isced_levels"])))
    missing_urls = sorted(r["resource_id"] for r in resources if not r["canonical_url"])
    if duplicate_domain_records or duplicate_level_records or missing_urls:
        raise ValueError({
            "duplicate_domain_records": duplicate_domain_records,
            "duplicate_level_records": duplicate_level_records,
            "missing_urls": missing_urls,
        })

    doc = {
        "schema": "interlanguage/open-resource-canon-map/1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {
            "purpose": "Map exact open educational resources to educational stage, subject need, curricular role, rights, delivery and accessibility evidence.",
            "ranking": False,
            "publication": False,
            "excluded_inputs": ["local translation completion", "local programme status", "local publication status", "language/population ranking"],
            "interpretation_rule": "A resource may be educationally relevant while still being unusable as a translation master; curricular completeness, derivative rights, offline delivery and accessibility are independent fields.",
        },
        "isced_taxonomy": ISCED,
        "non_isced_context_tags": ["tvet_or_professional", "teacher_professional_development", "adult_professional_nonformal"],
        "evidence_sources": SOURCES,
        "resources": resources,
        "validation": {
            "resource_count": len(resources),
            "openstax_title_count": sum(r["provider"] == "OpenStax" for r in resources),
            "non_openstax_record_count": sum(r["provider"] != "OpenStax" for r in resources),
            "unique_resource_ids": len(set(ids)),
            "invalid_isced_levels": bad_levels,
            "unknown_evidence_references": unknown_refs,
            "duplicate_domain_records": duplicate_domain_records,
            "duplicate_level_records": duplicate_level_records,
            "missing_canonical_urls": missing_urls,
            "full_multistage_curriculum_claim_count": sum(r["curricular_role"] == "full_multistage_curriculum" for r in resources),
            "openstax_catalog_sha256": sha256(CATALOG),
        },
    }
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(build_report(doc), encoding="utf-8")


if __name__ == "__main__":
    main()
