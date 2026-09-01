"""Read-only source inspection for translation production, never a training export."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'downloads/bn-Beng-BD/pilot-source/m81243.cnxml'
ns = {'c': 'http://cnx.rice.edu/cnxml'}
r = ET.parse(path).getroot()
sections = list(r.find('c:content', ns))
for i, section in enumerate(sections):
    print(i, section.tag.split('}')[-1], section.get('id'), section.findtext('c:title', namespaces=ns))
for section in sections[:2]:
    for node in section.iter():
        for key, value in [('text', node.text), ('tail', node.tail), ('alt', node.get('alt'))]:
            if value and any(c.isascii() and c.isalpha() for c in value):
                print(node.get('id', node.tag.split('}')[-1]), key, repr(value))
