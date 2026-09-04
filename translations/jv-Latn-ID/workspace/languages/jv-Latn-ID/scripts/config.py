from pathlib import Path

LANG = Path(__file__).resolve().parents[1]
ROOT = LANG.parents[1]
DOWNLOADS = ROOT / 'downloads' / 'jv-Latn-ID'
UPSTREAM_COMMIT = '38cae454e644abf9f0a623e876994553881597c9'
REPOSITORIES = [
    ('catalog', 'https://github.com/KokunoYumeto/program-matematika-indonesia.git', '2f0e52280791854f904475e5f92392f52745ea24', 'Program catalog and AX-2 authority snapshot'),
    ('a00-id', 'https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID.git', '3de9207f56f8b5c57c017abf973fb04e00d740f1', 'A00 complete Indonesian translation inputs'),
    ('a10-id', 'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id.git', '11754719d8eab8de63d5340ad35824e8be8d99e4', 'A10 release authority and notices'),
    ('openstax-prealgebra-bundle', 'https://github.com/openstax/osbooks-prealgebra-bundle.git', UPSTREAM_COMMIT, 'Canonical upstream shared by A00 and A10; no translation of the bundled Intermediate Algebra book'),
    ('access-dossier', 'https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access.git', '2c9c129c3e693bec5a0e387c76b1c270fccf399c', 'AX-2 canonical planning specifications; no repeat audit'),
]
A10_ZIP_URL = 'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/download/v1.0.2/elementary-algebra-2e-id-ID-1.0.2-source.zip'
A10_ZIP_SHA = '6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456'
UNITS = [
    {'key': 'a00-number-sense', 'program': 'A00', 'module': 'm81243', 'section': 'fs-id1830385', 'children': None, 'next_anchor': 'fs-id2340048', 'source': 'modules/m81243/index.cnxml', 'scope': 'Complete first instructional subsection, including worked example and both Try It exercises/solutions.'},
    {'key': 'a10-variable-bridge', 'program': 'A10', 'module': 'm82453', 'section': 'fs-id1170655150800', 'children': 7, 'next_anchor': 'fs-id1170655224522', 'source': 'translated/modules/m82453/index.cnxml', 'scope': 'Contiguous opening through the constant definition; not the complete subsection or module.'},
]
TRACKS = {
    'jv-conversation': ('jv-Latn-ID', 'Basa Jawa padinan · ngoko'),
    'jv-academic': ('jv-Latn-ID', 'Basa Jawa akademik · rancangan'),
    'id-academic': ('id-ID', 'Bahasa Indonesia · teks sumber'),
}
