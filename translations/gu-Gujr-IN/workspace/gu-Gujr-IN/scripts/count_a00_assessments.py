"""Compare native A00 exercise counts using existing pinned authority inputs only."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

LANG=Path(__file__).resolve().parents[1];ROOT=LANG.parent;C='{http://cnx.rice.edu/cnxml}'
records=[];keys=[];native_ids=[]
for row in csv.DictReader((LANG/'source-module-map.csv').open(encoding='utf-8')):
    if row['program']!='A00':continue
    path=ROOT/row['authority_path'];sha=hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha==row['canonical_sha256'],row['module_id']
    source=E.parse(path).getroot();exercises=list(source.iter(C+'exercise'))
    ids=[e.get('id') for e in exercises];assert len(ids)==len(set(ids)) and all(ids)
    keys.extend((row['module_id'],ident) for ident in ids);native_ids.extend(ids)
    records.append(dict(module=row['module_id'],source_sha256=sha,exercises=len(ids),with_solution=sum(e.find(C+'solution')is not None for e in exercises),solution_gaps=sum(e.find(C+'solution')is None for e in exercises)))
assert len(keys)==len(set(keys))==8105 and len(records)==75
assert sum(r['solution_gaps']for r in records)==2865
repeated={k:v for k,v in Counter(native_ids).items() if v>1}
result=dict(scope='Existing pinned A00 authority files only; no central adapter ZIP acquired or replayed',modules=len(records),exercises=len(keys),source_exercises_with_solution=sum(r['with_solution']for r in records),source_exercises_without_solution=sum(r['solution_gaps']for r in records),key_fields=['module','native_id'],distinct_repeated_native_ids=len(repeated),repeated_native_id_occurrences=sum(repeated.values()),records=records)
(LANG/'reviews/a00-pinned-assessment-counts.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in result.items()if k!='records'}))
