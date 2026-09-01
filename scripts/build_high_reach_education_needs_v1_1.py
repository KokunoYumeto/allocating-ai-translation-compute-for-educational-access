#!/usr/bin/env python3
"""Build evidence-backed stage/domain packages for the high-reach profiles.

These rows diagnose *what to make*, separately from population ordering.  They
do not turn a territory or speaker ceiling into a count of people who need the
package.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "staging" / "high_reach_education_needs"
ROW_FIELDS = [
    "needs_profile_id", "candidate_ids", "display_name", "target_profiles",
    "territory_or_scope", "production_regime", "first_priority_stage",
    "first_package", "follow_on_package", "existing_supply",
    "need_evidence", "source_urls", "delivery_spec",
    "teacher_independent_requirements", "accessibility_requirements",
    "non_overlap_rule", "evidence_confidence", "package_confidence", "caveat",
]
FIELDS = ROW_FIELDS + ["prerequisite_route"]
EDGE_FIELDS = [
    "needs_profile_id", "candidate_id", "expected_profile_id",
    "portfolio_entry_id", "named_output_profile_id", "edge_role", "edge_status",
]


def row(*values: str) -> dict[str, str]:
    if len(values) != len(ROW_FIELDS):
        raise ValueError(f"expected {len(ROW_FIELDS)} fields, got {len(values)}")
    return dict(zip(ROW_FIELDS, values))


ROWS = [
    row("HRN-001", "NAT-122", "Mainland Simplified Chinese", "zh-Hans-CN", "Mainland China", "strong_supply_exact_forward_residual", "cross-stage accessibility, vocational/adult quantitative access and professional/research continuity", "Finish the exact 25-unit Calculus I residual (CALC1-0031 through CALC1-0055), then Calculus II/III and Statistics before the remaining fixed STEM books; create semantic HTML/MathML, accessible EPUB, tagged PDF, audio/transcript and low-bandwidth offline derivatives for completed corpora.", "Add a four-band school diagnostic/catch-up overlay, an official-standard-aligned 144-hour vocational quantitative bridge, adult/workplace/financial numeracy and academic re-entry, then title-audited frontier mathematics rather than duplicate generic native-language textbooks.", "Official platforms report 130,000+ K-12 resources, 12,500+ vocational courses and 145,000 higher-education courses; Open Logic 722/722 and Algebra and Trigonometry 94/94 are complete and Calculus I is 30/55.", "Large national supply does not prove open licensing, no-login/offline permanence, teacher-independent exercise closure, semantic accessibility, or absence of title-level research gaps.", "https://www.moe.gov.cn/fbh/live/2025/77791/mtbd/202512/t20251231_1425330.html ; https://www.moe.gov.cn/jyb_sjzl/sjzl_fztjgb/202607/t20260706_1442870.html ; https://www3.cnnic.cn/n4/2026/0304/c88-11549.html ; ACE-E063", "No-account, download-once semantic HTML/MathML, EPUB, tagged PDF, audio/transcripts, chapter bundles, print assets and offline source archive.", "Diagnostics, complete worked answers, executable notebooks where relevant, explicit prerequisites, mastery/re-entry routing and maintenance versioning.", "True Unicode; tested CJK fonts and ToUnicode; semantic MathML; keyboard and screen-reader navigation; captions/transcripts; reflow, large print, math-speech and Braille compatibility.", "Do not duplicate completed Open Logic/algebra or generic K-9 supply; do not claim `zh-Hans-CN` covers Wu, Yue, Hakka, Taigi or minority-language communities; treat spoken Putonghua as a separate modality profile.", "high exact residual and official supply diagnosis; medium population increment", "high exact package; medium broader pathways", "The mainland census total and enrollment cohorts are exposure ceilings, not underserved-reader counts; 80.72% Putonghua prevalence is a separate rounded survey-derived sensitivity."),
    row("HRN-002", "NAT-123", "Japanese", "ja-Jpan-JP", "Japan", "strong_supply_stage_specific_residual", "accessible self-study, multilingual academic bridge and postgraduate/research frontier", "Build a no-login, download-once Japanese Open Mathematics Access and Research Bridge: curriculum-aligned diagnostics and prerequisite repair, complete solutions, accessible semantic HTML/EPUB/MathML, and easy-Japanese/furigana plus multilingual terminology for non-attending pupils, adult re-entry learners and pupils requiring Japanese-language instruction.", "Add a university proof/foreign-language-reading bridge and translate only title-audited missing or non-open EGA/SGA/FGA and other frontier works; do not duplicate ordinary compulsory-school mathematics.", "All compulsory-school pupils receive required textbooks free; approved Japanese school series are abundant and attainment is high. Residual cohorts include 84,759 public-school pupils requiring Japanese-language instruction, 353,970 non-attending compulsory-school pupils and roughly 10% of the PIAAC age-16-65 population at or below numeracy Level 1; these cohorts overlap.", "Strong mainstream supply does not prove open licensing, permanent no-login/offline self-study sequence closure, independent screen-reader operation, accessible upper-secondary coverage, multilingual academic scaffolding or frontier-corpus completeness.", "https://www.mext.go.jp/a_menu/shotou/kyoukasho/gaiyou/04060901/1235098.htm ; https://www.mext.go.jp/content/20260525-mxt_kyokoku-000049811_2.pdf ; https://www.mext.go.jp/content/20251029-mxt_jidou02-100002753_2_5.pdf ; https://www.oecd.org/en/publications/survey-of-adults-skills-2023-country-notes_ab4f6b8c-en/japan_91adbde1-en.html ; https://www.mext.go.jp/content/20250328-mxt_kyousei02-000008669_02.pdf", "No-login offline HTML5/EPUB 3/MathML, tagged PDF, low-bandwidth ZIP, print, Japanese mathematical speech and tactile/embossable diagram assets.", "Placement checks, worked feedback, full solutions, prerequisite graph, mastery checkpoints and Japanese-English-French research-navigation terminology.", "Furigana/plain-Japanese modes, semantic math, Japanese speech strings, Braille-compatible math, tactile diagrams, dyslexia/low-vision settings, captions, keyboard navigation and reflow.", "Do not duplicate generic compulsory-school algebra or treat the 123.802M territory population as Japanese readers newly served; keep formalism-assisted foreign-language reading distinct from writing/oral-instruction access.", "high official supply and cohort diagnosis", "high targeted package; title-specific frontier gaps remain medium until catalog audit", "The identified cohorts overlap and are not summed. Advanced mathematical translation is educational infrastructure even when mass foundational supply is strong."),
    row("HRN-003", "", "Korean, Republic of Korea", "ko-Kore-KR", "Republic of Korea", "strong_supply_portability_access_residual", "adult/professional and research continuity", "Thirty-six short offline life-capability modules: health, fraud/credit/SME finance, agriculture/climate, practical science, computing and AI-output verification.", "Statistics, R/Python, open licensing, data management, research integrity and applied-domain laboratories.", "K-MOOC and KOCW have extensive inventories; external-link dependence creates portability/persistence risk.", "Older, disabled and farming populations remain below general digital-capacity levels.", "https://www.korea.kr/news/policyNewsView.do?newsId=148939765 ; https://www.kocw.net/home/kocwStatistics.do?statType=1 ; https://nia.or.kr/site/nia_kor/ex/bbs/View.do?bcIdx=27832&cbIdx=81623", "Download-once offline bundle with print/simple-language cards.", "Short mastery checks, full explanations, locally current examples and maintenance dates.", "Semantic Korean text, captions, audio, large type, high contrast and key Korean Sign Language safety/health videos.", "No inference about DPRK follows from ROK supply; do not pool the territories.", "medium-high ROK evidence", "medium", "An exact Korean comfortable-reader or unique-residual count is not established."),
    row("HRN-004", "NAT-124", "Standard Hindi", "hi-Deva-IN", "India", "undergraduate_professional_research_continuity", "first-year tertiary through active researcher", "Bilingual first-year physics, chemistry, biology, statistics, computing, economics and management, followed by research design, R/Python and open-science methods.", "Current health, agriculture, cyber-finance and SME continuing education, then accessible catch-up practice only where exact gaps remain.", "NCERT/DIKSHA school provision is extensive; DIKSHA supports offline use and many languages; Hindi had the largest audited NIMI vocational output.", "The sharper discontinuity is higher education and professional/research continuity, not absence of all Hindi school books.", "https://pmevidya.education.gov.in/diksha.html ; https://ncert.nic.in/accessibility.php/textbook.php ; https://nimi.gov.in/web/pdf/Annual%20Report-2025_English%20Version.pdf ; https://nptel.ac.in/translation", "Offline bilingual HTML/EPUB/PDF plus low-cost laboratory/simulation assets.", "Complete exercises/answers, terminology crosswalk, prerequisites, research datasets and reproducible notebooks.", "Devanagari screen-reader testing, semantic math, captions, reflow and print.", "Credit the completed formal-reasoning edition; do not assign Standard Hindi reach to Bhojpuri, Awadhi, Chhattisgarhi or other named returns.", "high broad stage diagnosis", "medium-high", "Use the exact same-name Hindi population only within its measure class."),
    row("HRN-005", "NAT-001", "Bangla, Bangladesh", "bn-Beng-BD", "Bangladesh", "foundational_emergency_then_tvet", "pre-primary through grades 5", "Twenty-four-week caregiver/ECE and grades 2-5 recovery system with diagnostics, worked feedback, print/audio/basic-phone delivery, health/hygiene and flood/cyclone continuity.", "Adolescent/TVET applied science, health, digital and financial safety, climate-smart agriculture and microenterprise; separate delta-resilience overlay.", "NCTB publishes current pre-primary through secondary books.", "MICS 2025 reports low ECE attendance, foundational reading/numeracy and upper-secondary completion, pointing to mastery/continuity rather than textbook absence.", "https://nctb.portal.gov.bd/pages/static-pages/695b97ffc4774958d7b70329 ; https://www.unicef.org/bangladesh/en/data-situation-children-bangladesh", "Print, offline HTML, audio, IVR/SMS-compatible prompts and SD-card/local-server bundle.", "Daily diagnostic cycle, full worked answers, caregiver scripts and catch-up placement/re-entry map.", "Unicode Bangla, semantic math, TTS testing, captions, large-print and low-data audio.", "Separate Bangladesh curriculum/professional overlay from Indian Bengali; do not count the same Bangla core twice.", "high need evidence", "high first package", "Population counts do not equal affected cohorts; exact MICS indicator universes must remain attached."),
    row("HRN-006", "NAT-002", "Bengali, India", "bn-Beng-IN", "West Bengal and other Indian Bengali contexts", "secondary_tvet_tertiary_transition", "secondary/TVET", "Workshop mathematics and safety, applied science, coding, digital-finance/fraud and entrepreneurship.", "Bengali-English first-year science, computing, economics and management; then postgraduate research methods and frontier navigation.", "West Bengal has substantial school e-textbooks/video; audited vocational Bengali output was small.", "The marginal discontinuity is vocational and tertiary transition rather than another school textbook series.", "https://banglarshiksha.wb.gov.in/Frontend/e_textbook ; https://nimi.gov.in/web/pdf/Annual%20Report-2025_English%20Version.pdf", "Offline phone/desktop course graph plus print workshop cards.", "Worked cases, complete answers, simulated labs and Bengali-English terminology.", "Semantic Bangla/MathML, captions, audio, high-contrast print and keyboard navigation.", "Use a shared Bangla semantic source but separate Indian curricula, examples and professional terminology.", "medium-high", "medium-high", "Indian territorial outcomes are not a direct Bengali-speaker sample."),
    row("HRN-007", "NAT-003", "Telugu", "te-Telu-IN", "Andhra Pradesh and Telangana", "secondary_tvet_tertiary_transition", "secondary/TVET/first-year", "Applied STEM, coding, financial safety and entrepreneurship with Telugu-English terminology and offline simulations.", "Agriculture/climate, health and SME continuing education, then postgraduate methods/reproducibility.", "Both states have substantial school stocks; the audited NIMI output was only 14 Telugu vocational books.", "School-to-TVET and first-year university transition is the stronger gap.", "https://www.scert.telangana.gov.in/Home.aspx/Pdf/Displaycontent.aspx?encry=ammkNW4%2Fgx+NeApstGPX+A%3D%3D ; https://nimi.gov.in/web/pdf/Annual%20Report-2025_English%20Version.pdf", "Offline simulations, semantic HTML/EPUB/PDF and print practical guides.", "Placement, full solutions, terminology crosswalk, low-cost laboratories and career cases.", "Telugu screen-reader/font testing, semantic math, captions and reflow.", "Andhra Pradesh and Telangana require separate curriculum crosswalks.", "medium-high", "medium-high", "The exact need is stage/territory specific, not one uniform Telugu deficit."),
    row("HRN-008", "NAT-006", "Marathi", "mr-Deva-IN", "Maharashtra", "secondary_tvet_tertiary_transition", "secondary/TVET/first-year", "Applied science, workshop practice, computing, finance and entrepreneurship.", "Climate-resilient agriculture, health/SME professional modules and research methods.", "Balbharati/eBalbharati provides grade 1-12 materials; audited vocational output was modest.", "A recovery/transition spine adds more than duplicating existing primary textbooks.", "https://ebooks.ebalbharati.in/ebook.aspx ; https://nimi.gov.in/web/pdf/Annual%20Report-2025_English%20Version.pdf", "Offline bilingual course graph and printable practice/lab pack.", "Diagnostic prerequisite repair, worked solutions and Marathi-English terminology.", "Devanagari semantic text/math, captions, reflow and large print.", "Keep foundational rural assessment evidence separate from all Marathi speakers.", "medium-high", "medium", "Exact local open licenses and artifact completeness still need item audit."),
    row("HRN-009", "NAT-004", "Tamil, India", "ta-Taml-IN", "Tamil Nadu and Indian Tamil contexts", "undergraduate_professional_research_continuity", "first-year tertiary", "Tamil-English first-year STEM, computing and management with worked problems, offline simulations and research methods.", "Health, climate/agriculture, cyber-finance and SME professional modules, then accessible school practice where needed.", "Tamil has comparatively strong school/vocational and computing-tutorial supply.", "Undergraduate-to-research continuity is a higher marginal gap than generic school translation.", "https://scertbooks-staging.tnschools.gov.in/ ; https://nimi.gov.in/web/pdf/Annual%20Report-2025_English%20Version.pdf ; https://spoken-tutorial.org/", "Offline semantic course graph plus simulations and print.", "Full solutions, bilingual terminology, research datasets and reproducible notebooks.", "Tamil font/TTS testing, semantic math, captions and reflow.", "Sri Lankan Tamil remains a separate profile and curriculum.", "medium-high", "medium-high", "Strong supply does not imply open-license or research-frontier closure."),
    row("HRN-010", "NAT-121;CMP-ID-ID", "Bahasa Indonesia", "id-Latn-ID", "Indonesia", "completed_program_forward_professional_research", "professional/postgraduate/research", "Six-course Evidence-to-Practice and Research Core: research design/open science; applied statistics and causal reasoning in R/Python; reproducible data/AI/cybersecurity; evidence appraisal; public health/One Health; climate-smart agriculture/disaster risk.", "Versioned professional-update library for MSME finance/management, health CPD, renewable energy/water, agriculture/aquaculture and frontier briefs.", "Strong school supply, Universitas Terbuka OER, Open Logic 722/722 and an established 40-course mathematics program.", "More elementary mathematics or logic would duplicate completed work; continuously changing professional evidence and offline/accessibility remain material.", "https://buku.kemendikdasmen.go.id/katalog/ ; https://pustaka.ut.ac.id/lib/open-educational-resources-ut/ ; https://www.bps.go.id/id/publication/2025/08/29/beaa2be400eda6ce6c636ef8/telecommunication-statistics-in-indonesia-2024.html ; CURRENT_INDONESIAN_PROGRAM_STATUS_20260830.md", "Download-once offline HTML/PWA/local server, EPUB, tagged PDF and source package.", "Complete exercises/answers, diagnostics, executable notebooks, maintenance cadence and evidence-update dates.", "Semantic MathML, screen-reader navigation, captions/audio, low-bandwidth mode and print.", "D=0 for completed exact corpora; future benefit only for the 13 exact production roles or demonstrated format/professional gaps.", "high current-state; medium marginal population", "high package logic", "This is an Indonesian program, not a pilot; page universes are not interchangeable."),
    row("HRN-011", "NAT-028", "Vietnamese", "vi-Latn-VN", "Vietnam", "secondary_tvet_tertiary_transition", "TVET-university", "Five coherent courses: data/programming/AI/cybersecurity; climate-smart rice/aquaculture/green skills; public health/evidence appraisal; MSME accounting/digital finance; applied biology/chemistry with low-cost labs.", "Quarterly frontier-to-field briefs, datasets/notebooks and postgraduate research-design/causal-inference/systematic-review/reproducibility courses.", "National digital textbooks, VOER and digital-skills platforms exist.", "Official higher-education evidence identifies fragmentation/interoperability issues and TVET e-learning remains early-stage.", "https://vnfoundation.org/en/vietnam-open-educational-resources/ ; https://baochinhphu.vn/de-xuat-quy-dinh-ve-khai-thac-su-dung-tai-nguyen-giao-duc-mo-trong-giao-duc-dai-hoc-102260508102509726.htm ; https://documents1.worldbank.org/curated/en/099000005132229736/pdf/P174258045156b0060972302fec6a3015b8.pdf", "Offline interoperable HTML/EPUB/PDF plus low-cost labs/notebooks.", "Prerequisite map, complete solutions, applied cases and bilingual search terminology.", "Semantic math, captions, screen-reader testing and low-bandwidth download.", "Mong, J'rai, Khmer and other early-years language overlays remain separate.", "medium-high", "medium-high", "National supply fragmentation is not proof that every listed course is absent."),
    row("HRN-012", "NAT-033", "Filipino", "fil-Latn-PH with replaceable home-language tracks", "Philippines", "secondary_tvet_tertiary_transition", "grades 7-12/ALS/TVET", "One hundred twenty Filipino-English STEM-Kabuhayan micro-lessons: health, finance/SME, agriculture/climate/disaster, core science and computing/data/AI/cybersecurity.", "Higher/professional/research spine in open science, biostatistics, public health, programming/data, management and climate-smart agriculture/renewables.", "DepEd, TESDA Online, UPOU OER, agricultural e-extension and STARBOOKS already exist.", "Home Internet was 48.8% nationally in 2024 and much lower in some regions; extend offline STARBOOKS-like infrastructure rather than duplicate it.", "https://stii.dost.gov.ph/starbooks/ ; https://e-tesda.gov.ph/course ; https://oer.upou.edu.ph/ ; https://psa.gov.ph/content/percentage-households-internet-connection-increased-488-percent-2024-two-every-three", "Offline local-server/USB/SD package plus print and low-data audio.", "Full answers, practical projects, terminology, mastery checks and local livelihood cases.", "Captions, semantic text/math, screen-reader support and replaceable home-language audio/glossaries.", "Filipino is a learned national standard for many, not everyone's L1; exact functional denominator remains unresolved.", "high delivery evidence; medium language reach", "high package architecture", "Do not rank the Philippines territory as Filipino comfortable readers."),
    row("HRN-013", "NAT-063;NAT-064", "Standard Kiswahili country package", "swh-Latn-TZ; swh-Latn-KE; swh-Latn-UG; swc-Latn-CD", "East/Central Africa", "foundation_DRC_Uganda_then_transition", "DRC grades 1-3 and Uganda P4 L2", "DRC regional-variety-aware literacy/basic science/health with French bridge; Uganda P4 Kiswahili L2 materials, teacher scripts and offline audio.", "Kiswahili-English/French biology, chemistry, climate/agriculture, health, computing and finance; then TVET/statistics/R/Python/open science.", "Tanzania has meaningful Kiswahili primary science; DRC and Uganda have stronger material/implementation gaps.", "Regional variety mismatch, scarce DRC textbooks and Uganda's scaling L2 provision make one generic East African textbook inefficient.", "https://kiswahili.eac.int/wp-content/uploads/2022/10/EAKC-Strategic-Plan-FINAL.pdf ; https://ol.tie.go.tz/uploaded_files/books/primary/Eng/Std4/Sayansi_Drs_4/files/basic-html/page6.html ; https://www.unesco.org/gem-report/sites/default/files/medias/fichiers/2023/02/Spotlight%20Advocacy_DRC_EN_v2.pdf", "Print/audio/offline HTML with country curriculum overlay.", "Teacher and self-study scripts, diagnostics, worked answers, French/English bridges and locally relevant cases.", "Captions, audio, semantic text/math, large print and offline delivery.", "No blanket 200M written reach; Tanzania, Kenya, Uganda and DRC profiles remain separate.", "high regime; low exact reach", "high DRC/Uganda package", "The UNESCO/AU headline is a gross user diagnostic, not a deduplicated reader count."),
    row("HRN-014", "NAT-069", "Hausa Nigeria/Niger package", "ha-Latn-NG; ha-Latn-NE; optional established Ajami", "Nigeria and Niger", "foundation_functional_then_tvet", "pre-primary/grades 1-3/adult literacy", "Structured boko phonics, graded reading, diagnostics and Hausa-English Nigeria / Hausa-French Niger bridges with print, radio, IVR and optional Ajami parallel text/audio.", "Secondary/TVET science, agriculture, public health and computing; mobile-money safety, microenterprise, livestock/water and solar/GSM trades; later statistics/R/Python/open science.", "Nigeria has RANA stories and early readers, while foundational outcomes/connectivity remain weak and advanced practical supply is thinner.", "Country orthography, boko literacy, optional Ajami use and written readership must remain separate.", "https://education.gov.ng/e-learning-resources/ ; https://www.unicef.org/nigeria/stories/enabling-teachers-educating-children ; https://archives.au.int/handle/123456789/1556 ; https://nmec.gov.ng/faqs/", "Print, radio, IVR, basic-phone and offline HTML/PDF.", "Structured phonics/mastery, full feedback, country terminology and practical projects.", "Audio, large print, semantic boko, optional local Ajami and captions/transcripts.", "No universal Ajami and no automatic Nigeria/Niger or 60M/94M population merge.", "high need regime; low exact written reach", "high foundational; medium advanced", "A compatible functional-reader denominator remains unresolved."),
    row("HRN-015", "IL-AR", "Arabic MSA plus country spoken scaffolds", "arb-Arab plus named country spoken-language layers", "MENA and displaced communities", "foundation_emergency_then_disciplinary_research", "pre-primary/grades 1-3 and emergency catch-up", "Fully vowelled leveled MSA phonics/morphology/comprehension with country spoken narration; in parallel offline accelerated literacy, science, health/WASH and safety for Sudan, Yemen, Syria and Gaza.", "MSA disciplinary literacy in science/health/climate/finance/computing, country TVET pathways, then research methods/meta-analysis/R/Python/FAIR data and scholarly navigation.", "WHO, FAO, ILO and ITU Arabic professional material exists but is fragmented; formal MSA availability does not resolve diglossia.", "Conflict exclusion, learning poverty and spoken-to-MSA distance create stage- and country-specific needs.", "https://documents1.worldbank.org/curated/en/909741624654308046/pdf/Advancing-Arabic-Language-Teaching-and-Learning-A-Path-to-Reducing-Learning-Poverty-in-the-Middle-East-and-North-Africa.pdf ; https://www.emro.who.int/entity/global-arabic-programme/ ; https://elearning.fao.org/course/view.php?id=628&lang=ar ; https://www.unicef.org/mena/press-releases/least-30-million-children-out-school-middle-east-north-africa", "Offline print/radio/SD/local-server bundle plus maintained professional pathways.", "Diagnostics, complete feedback, local spoken narration, country curriculum/re-entry maps and versioning.", "Unicode RTL/bidi metadata, logical reading order, TTS-tested vowelization, captions, sign-language video where relevant and semantic math.", "MSA is not an ordinary L1; dialect, non-Arabic L1 and country profiles remain separate.", "high regime; variable locale evidence", "high emergency/foundation; medium later", "No single 400-450M Arabic comfort or newly served count is asserted."),
    row("HRN-016", "", "Latin American Spanish localized recovery", "es-419 plus country overlays", "Latin America", "strong_supply_mastery_access_residual", "grades 3-9", "Teacher-independent mastery recovery in literacy, numeracy and practical science with health, household finance, digital safety and climate; diagnostics and full answers.", "No-login/offline/accessibility conversion of high-value OER, then exact nursing, computing, business, research-method and frontier gaps.", "Spain/Latin America have extensive school OER, Spanish OpenStax editions and SciELO infrastructure.", "ERCE shows widespread minimum-competency shortfalls; this is a mastery/pedagogy/access problem rather than proof of textbook absence.", "https://procomun.intef.es/es/contenido/acerca-de-procomun ; https://www.scielo.org/en/about-scielo/program-publication-model-and-scielo-network/ ; https://siteal.iiep.unesco.org/eje/educacion_basica", "Country-localized offline HTML/EPUB/PDF and print.", "Diagnostics, misconception repair, full answers and country examples/regulation.", "Semantic text/math, captions, TTS, reflow and low-bandwidth assets.", "`es-ES` does not dictate Latin American curricula or professional terminology; global Spanish totals are nonadditive models.", "high broad regime", "medium-high", "Exact country cohorts and artifact gaps still require local inventories."),
    row("HRN-017", "", "Brazilian Portuguese", "pt-BR", "Brazil", "strong_supply_open_reuse_access_residual", "adult/vocational/professional/research", "No-login/offline, semantic, teacher-independent mastery and transition bundles using lawfully reusable Brazilian sources.", "Research methods/reproducibility and exact advanced-content gaps.", "PNLD Digital and UNA-SUS are extensive, but authentication/DRM and reuse constraints matter.", "Resource abundance does not guarantee lawful retain/adapt/redistribute rights, independent sequencing or offline access.", "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/programas-do-livro/pnld/guia-do-livro-didatico/obras-digitais-do-pnld ; https://www.unasus.gov.br/institucional", "No-login offline bundle with editable source and print.", "Complete answers, diagnostic progression and current professional examples.", "Semantic text/math, captions, screen-reader support and reflow.", "Brazil is separate from Portugal, Angola, Mozambique and other PALOP outputs.", "high supply/access diagnosis", "medium", "Brazil territory is not a Portuguese-reader or unique-need count."),
    row("HRN-018", "", "PALOP local-language to Portuguese bridges", "pt-AO; pt-MZ plus exact local-language outputs", "Angola, Mozambique and other PALOP contexts", "foundational_bilingual_then_tvet", "primary/literacy", "Exact local-language plus Portuguese foundational bridges rather than Portuguese-only replacement.", "Bilingual health, agriculture, enterprise, finance and TVET pathways with local audio and Portuguese written progression.", "Portuguese official materials exist; home-language reach varies sharply.", "Mozambique evidence shows Portuguese mother-tongue/ability and rural access do not justify Portuguese-only foundational design.", "https://www.unesco.org/gem-report/en/2026-gem-report-country-case-studies/mozambique ; Africa audit AFR-014/015", "Print/audio/offline bilingual packages.", "Local-language mastery, Portuguese transition, full feedback and livelihood projects.", "Audio, captions, semantic text/math, large print and low bandwidth.", "Each local language and `pt-AO`/`pt-MZ` edition retains its own population and curriculum.", "medium-high regime", "medium", "No PALOP-wide additive reader count is asserted."),
    row("HRN-019", "", "Russian learned-standard residual", "ru-Cyrl-RU plus localized overlays", "Russian Federation and separately audited learned-language contexts", "strong_supply_open_reuse_frontier_residual", "professional/postgraduate/research", "Open, accessible, no-login/offline statistics/causal inference, reproducible Python/R, research integrity, open licensing/data stewardship and AI evidence evaluation with applied tracks.", "Exact modern frontier review/monograph translations and semantic-accessible editions only where inventory proves absence.", "National Open Education and Math-Net show strong university/research infrastructure; rights and full-text access vary.", "The marginal need is reuse/accessibility/current methods and exact frontier gaps, not wholesale school translation.", "https://openedu.ru/ ; https://www.mathnet.ru/ ; https://www.mathnet.ru/ej.phtml?jorder=jrn&jrnid=&option_lang=eng", "Open no-login offline semantic bundle plus source and print.", "Exercises/answers, reproducible notebooks, datasets and bilingual search/navigation where relevant.", "Cyrillic semantic text/math, captions, screen-reader testing and reflow.", "Russian competence is not blanket coverage for Indigenous, displaced, diaspora or successor-state communities.", "high supply diagnosis", "medium", "Global speaker estimates do not measure academic comfort or unique residual."),
    row("HRN-020", "NAT-125", "Bhojpuri, India", "bho-Deva-IN", "India, with Bihar and eastern Uttar Pradesh localization declared", "foundational_to_secondary_bilingual_bridge_then_tertiary_audit", "foundational numeracy through algebra", "Create a declared versioned Devanagari Bhojpuri editorial register and a teacher-independent foundational-numeracy-through-algebra sequence with diagnostics, full worked answers, phone/offline delivery, audio, and Bhojpuri-to-Hindi bridge terminology.", "After an exact supply audit, add missing secondary/TVET practical science, health, finance and computing; keep tertiary/professional work as a separately evidenced residual.", "Official sources evidence Hindi-medium schooling and some Bhojpuri-as-subject provision, but no continuous open Bhojpuri-medium mathematics/STEM sequence has been evidenced.", "The exact 50,579,447 mother-tongue return establishes scale but not literacy, academic comfort, current population or the number newly served; Hindi academic-reading overlap is unmeasured.", "https://censusindia.gov.in/nada/index.php/catalog/10191 ; https://censusindia.gov.in/nada/index.php/catalog/45247/download/48954/LSI_BIHAR.pdf ; https://scert.bihar.gov.in/public/uploads/deled_books/S-9-D_PEDAGOGY_OF_ENGLISH_%282%291.pdf ; https://bstbpc.bihar.gov.in/Class9.aspx?download=zwtpxAyp.html", "Download-once semantic HTML/MathML, EPUB, tagged PDF, print workbook and low-data audio; no login required.", "Entry diagnostic; Bhojpuri oral-to-Devanagari support; complete worked feedback; explicit Hindi bridge glossary; reversible Bihar/eastern-UP terminology overlays.", "Devanagari font/TTS/screen-reader tests, semantic mathematics, reflow, captions/transcripts, large print and keyboard navigation.", "Never add Bhojpuri to the parent Hindi census umbrella; award zero automatic Hindi comprehension credit; keep Nepal, Mauritius, Magahi and Maithili outputs separate.", "high exact population identity; medium supply diagnosis", "medium-high foundational package", "Devanagari is a defensible production default, not proof of one transregional standard."),
]


PREREQUISITE_ROUTES = {
    "HRN-001": "Exact completed-corpus inventory -> Calculus I module prerequisites -> professional/research pathway prerequisites.",
    "HRN-002": "Grades 5-9 diagnostic repair -> upper-secondary proof language -> undergraduate algebra -> commutative algebra -> algebraic geometry/frontier corpus.",
    "HRN-003": "Short placement and digital-safety diagnostics -> adult capability modules -> statistics/programming/research methods.",
    "HRN-004": "Bilingual secondary diagnostic -> first-year disciplinary bridge -> statistics/programming -> postgraduate research methods.",
    "HRN-005": "Oral-language/ECE entry -> grades 2-5 literacy/numeracy recovery -> lower-secondary re-entry -> TVET/applied pathway.",
    "HRN-006": "Secondary mastery diagnostic -> workshop mathematics/science -> TVET or first-year bridge -> research methods.",
    "HRN-007": "Secondary prerequisite repair -> TVET/applied STEM -> first-year bilingual bridge -> professional/research methods.",
    "HRN-008": "Grade-level diagnostic -> secondary recovery -> TVET/first-year bridge -> professional/research methods.",
    "HRN-009": "Secondary diagnostic -> Tamil-English first-year bridge -> reproducible methods -> postgraduate/frontier navigation.",
    "HRN-010": "Use completed Indonesian Open Logic and the relevant available exact-course prerequisites -> statistics/programming entry diagnostic and prerequisite repair -> evidence-to-practice core -> maintained professional updates; completion of the whole 40-course program is not required.",
    "HRN-011": "Secondary quantitative/digital diagnostic -> TVET/university applied courses -> research design and reproducibility.",
    "HRN-012": "Grades 7-12/ALS diagnostic -> STEM-Kabuhayan modules -> TVET/first-year bridge -> professional/research spine.",
    "HRN-013": "Country/variety-specific literacy or L2 entry -> primary science/health -> secondary/TVET bilingual bridge -> tertiary methods.",
    "HRN-014": "Boko/Ajami placement and oral-literacy entry -> foundational mastery -> practical TVET -> statistics/programming/open science.",
    "HRN-015": "Local spoken-language oral scaffold -> vowelled MSA literacy -> disciplinary MSA -> TVET/tertiary -> research methods.",
    "HRN-016": "Grades 3-9 diagnostic recovery -> country secondary transition -> professional or first-year path -> exact frontier residual.",
    "HRN-017": "Adult/secondary placement -> teacher-independent transition bundle -> professional/research methods -> exact advanced residual.",
    "HRN-018": "Named local-language foundation -> Portuguese transition -> bilingual TVET/health/agriculture/enterprise pathway.",
    "HRN-019": "Disciplinary prerequisite check -> statistics/programming/research integrity -> reproducible professional/research work -> exact frontier gaps.",
    "HRN-020": "Bhojpuri oral/Devanagari entry diagnostic -> foundational numeracy -> pre-algebra/algebra -> secondary/TVET bridge -> separately audited tertiary residual.",
}


# Current source corrections supersede the initial synthesis above. Each is
# traceable to the package-calibration source register, not a new audience claim.
SOURCE_CORRECTIONS_20260831 = {
    "HRN-005": {
        "need_evidence": "Final BBS/UNICEF MICS 2025 reports foundational numeracy for 39.2% and reading for 50.2% of children aged 7-14, plus ECE attendance of 16.6% at ages 36-59 months. These support mastery/continuity needs, not a causal language-barrier count; preliminary grade-specific indicators have different denominators.",
    },
    "HRN-013": {
        "first_package": "Reuse or adapt the DRC ministry's listed Kiswahili grades 1-3 and literacy materials where rights permit; complete specifically missing worked feedback, science/health, accessible/offline and regional-variety components with a French bridge. Add a separate Uganda P4 Kiswahili-L2 package with self-study scripts and offline audio.",
        "existing_supply": "Tanzania/Kenya have meaningful Kiswahili school supply. The DRC ministry lists grades 1-3 pupil books, workbooks, teacher guides and initial/functional literacy materials. Uganda's L2 implementation and exact regional/format gaps remain separate.",
        "need_evidence": "Country and regional-variety fit, self-study feedback, download integrity, open reuse and semantic/offline accessibility are the targets. The DRC inventory contradicts a blanket absence-of-textbooks claim; a ministry listing alone does not prove every linked file is correct or every function complete.",
        "source_urls": "https://edu-nc.gouv.cd/national-programmes ; https://kiswahili.eac.int/wp-content/uploads/2022/10/EAKC-Strategic-Plan-FINAL.pdf ; https://www.unesco.org/gem-report/sites/default/files/medias/fichiers/2023/02/Spotlight%20Advocacy_DRC_EN_v2.pdf",
        "evidence_confidence": "high existence of ministry-listed materials; medium exact functional gaps; low exact incremental readership",
        "package_confidence": "provisional adaptation/completion design, not proof every proposed component is absent",
    },
    "HRN-015": {
        "need_evidence": "Conflict exclusion, learning poverty and spoken-to-MSA distance create stage- and country-specific needs. UNICEF's at-least-30M out-of-school figure concerns children aged 5-18 across 12 MENA countries, not 30M Arabic readers or one language-specific beneficiary cohort.",
        "source_urls": "https://documents1.worldbank.org/curated/en/909741624654308046/pdf/Advancing-Arabic-Language-Teaching-and-Learning-A-Path-to-Reducing-Learning-Poverty-in-the-Middle-East-and-North-Africa.pdf ; https://www.emro.who.int/entity/global-arabic-programme/ ; https://elearning.fao.org/course/view.php?id=628&lang=ar ; https://www.unicef.org/mena/press-releases/least-30-million-children-out-school-middle-east-and-north-africa",
    },
}


EDGES = [
    ("HRN-001", "NAT-122", "GLB-002", "NAT-122", "zh-Hans-CN", "direct_profile_need", "resolved"),
    ("HRN-002", "NAT-123", "GLB-043", "NAT-123", "ja-Jpan-JP", "direct_profile_need", "resolved"),
    ("HRN-003", "", "GLB-044", "GLB-044", "ko-Kore-KR", "expected_profile_need", "resolved"),
    ("HRN-004", "NAT-124", "GLB-007", "IL-HU", "hi-Deva-IN", "shared_core_component_need", "resolved"),
    ("HRN-004", "NAT-124", "GLB-007", "NAT-124", "hi-Deva-IN", "completed_program_forward_residual", "resolved"),
    ("HRN-005", "NAT-001", "GLB-010", "SHC-BN", "bn-Beng-BD", "shared_core_component_need", "resolved"),
    ("HRN-006", "NAT-002", "GLB-011", "SHC-BN", "bn-Beng-IN", "shared_core_component_need", "resolved"),
    ("HRN-007", "NAT-003", "GLB-012", "NAT-003", "te-Telu-IN", "direct_profile_need", "resolved"),
    ("HRN-008", "NAT-006", "GLB-013", "NAT-006", "mr-Deva-IN", "direct_profile_need", "resolved"),
    ("HRN-009", "NAT-004", "GLB-014", "NAT-004", "ta-Taml-IN", "direct_profile_need", "resolved"),
    ("HRN-010", "NAT-121", "GLB-039", "NAT-121", "id-Latn-ID", "completed_program_forward_residual", "resolved"),
    ("HRN-010", "NAT-121", "GLB-039", "IL-IDMS", "id-Latn-ID", "cross_locale_compute_reuse_only", "resolved"),
    ("HRN-011", "NAT-028", "GLB-041", "NAT-028", "vi-Latn-VN", "direct_profile_need", "resolved"),
    ("HRN-012", "NAT-033", "GLB-046", "NAT-033", "fil-Latn-PH", "direct_profile_need", "resolved"),
    ("HRN-013", "NAT-063;NAT-064", "GLB-036", "SHC-SWAHILI", "swh-Latn-TZ;swh-Latn-KE;swh-Latn-UG;swc-Latn-CD", "shared_core_component_need", "resolved"),
    ("HRN-014", "NAT-069", "GLB-037", "SHC-HAUSA", "ha-Latn-NG;ha-Latn-NE", "shared_core_component_need", "resolved"),
    ("HRN-015", "IL-AR", "GLB-031", "IL-AR", "arb-Arab", "learned_standard_core_need", "resolved"),
    ("HRN-015", "", "GLB-032", "IL-AR", "arz-Arab-EG", "spoken_scaffold_component_need", "resolved"),
    ("HRN-015", "", "GLB-033", "IL-AR", "apc-Arab", "spoken_scaffold_component_need", "resolved"),
    ("HRN-016", "", "GLB-024", "GLB-024", "es-419", "expected_profile_need", "resolved"),
    ("HRN-017", "", "GLB-025", "GLB-025", "pt-BR", "expected_profile_need", "resolved"),
    ("HRN-018", "", "", "", "pt-AO;pt-MZ;named local-language outputs", "profile_resolution", "research_only_profile_resolution_required"),
    ("HRN-019", "", "GLB-027", "GLB-027", "ru-Cyrl-RU", "expected_profile_need", "resolved"),
    ("HRN-020", "NAT-125", "GLB-052", "NAT-125", "bho-Deva-IN", "direct_profile_need", "resolved"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (ROOT / "candidate_interventions_master.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {item["intervention_id"] for item in csv.DictReader(handle)}
    with (ROOT / "staging" / "global_expected_universe" / "expected_language_profiles_v1_1.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        expected_profile_ids = {item["universe_profile_id"] for item in csv.DictReader(handle)}

    ids = [item["needs_profile_id"] for item in ROWS]
    for item in ROWS:
        item.update(SOURCE_CORRECTIONS_20260831.get(item["needs_profile_id"], {}))
        item["prerequisite_route"] = PREREQUISITE_ROUTES.get(item["needs_profile_id"], "")
    edge_rows = [dict(zip(EDGE_FIELDS, values)) for values in EDGES]
    edge_needs_ids = {item["needs_profile_id"] for item in edge_rows}
    resolved_edges = [item for item in edge_rows if item["edge_status"] == "resolved"]
    referenced_candidates = {
        candidate_id
        for item in resolved_edges
        for candidate_id in item["candidate_id"].split(";")
        if candidate_id
    }
    referenced_expected_profiles = {
        item["expected_profile_id"] for item in resolved_edges if item["expected_profile_id"]
    }
    checks = {
        "unique_needs_profile_ids": len(ids) == len(set(ids)),
        "every_needs_profile_has_edge": set(ids) == edge_needs_ids,
        "all_candidate_references_resolve": referenced_candidates <= candidate_ids,
        "all_expected_profile_references_resolve": referenced_expected_profiles <= expected_profile_ids,
        "all_rows_have_first_package": all(item["first_package"] for item in ROWS),
        "all_rows_have_follow_on": all(item["follow_on_package"] for item in ROWS),
        "all_rows_have_prerequisite_route": all(item["prerequisite_route"] for item in ROWS),
        "all_rows_have_delivery": all(item["delivery_spec"] for item in ROWS),
        "all_rows_have_teacher_independent_requirements": all(item["teacher_independent_requirements"] for item in ROWS),
        "all_rows_have_accessibility_requirements": all(item["accessibility_requirements"] for item in ROWS),
        "all_rows_have_nonoverlap": all(item["non_overlap_rule"] for item in ROWS),
        "all_rows_have_source_urls": all(item["source_urls"] for item in ROWS),
        "unresolved_profile_edges_are_research_only": all(
            item["edge_status"] == "research_only_profile_resolution_required"
            for item in edge_rows if not item["expected_profile_id"]
        ),
        "bhojpuri_need_and_edge_present": any(
            item["needs_profile_id"] == "HRN-020" and item["expected_profile_id"] == "GLB-052"
            for item in edge_rows
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    receipt = OUT / "high_reach_education_needs_validation_v1_1.json"
    if status != "PASS":
        receipt.write_text(json.dumps({
            "schema": "interlanguage/high-reach-education-needs-validation/1.1.0",
            "status": status,
            "checks": checks,
            "unknown_candidate_ids": sorted(referenced_candidates - candidate_ids),
            "unknown_expected_profile_ids": sorted(referenced_expected_profiles - expected_profile_ids),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("FAIL: high-reach needs validation did not pass")

    path = OUT / "high_reach_education_needs_v1_1.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ROWS)
    edge_path = OUT / "high_reach_needs_portfolio_edges_v1_1.csv"
    with edge_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EDGE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(edge_rows)
    validation = {
        "schema": "interlanguage/high-reach-education-needs-validation/1.1.0",
        "status": status,
        "rows": len(ROWS),
        "edge_rows": len(edge_rows),
        "checks": checks,
        "outputs": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)},
            edge_path.name: {"bytes": edge_path.stat().st_size, "sha256": sha256(edge_path)},
        },
        "limitations": "Content diagnoses are independent of population rank; several unique-reader denominators remain unresolved.",
    }
    receipt.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status, "rows": len(ROWS), "edges": len(edge_rows),
        "csv_sha256": sha256(path), "edge_sha256": sha256(edge_path),
        "validation_sha256": sha256(receipt)
    }, indent=2))


if __name__ == "__main__":
    main()
