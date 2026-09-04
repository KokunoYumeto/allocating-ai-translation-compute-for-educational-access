"""Exact arithmetic and source-English naming checks; no linguistic approval claim."""
import math
import re

SMALL="zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS="zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()
SCALES=["","thousand","million","billion","trillion"]


def under_thousand(value):
    assert 0<=value<1000
    if value<20:
        return SMALL[value]
    if value<100:
        return TENS[value//10]+("-"+SMALL[value%10] if value%10 else "")
    return SMALL[value//100]+" hundred"+(" "+under_thousand(value%100) if value%100 else "")


def english_name(value):
    assert 0<=value<1000**len(SCALES)
    if not value:
        return "zero"
    groups=[]; index=0
    while value:
        value,group=divmod(value,1000)
        if group:
            groups.append(under_thousand(group)+(" "+SCALES[index] if index else ""))
        index+=1
    return ", ".join(reversed(groups))


def text_of(element):
    return " ".join("".join(element.itertext()).split())


def verify_numeric_equalities(text,minimum):
    pattern=r"(?<![\w,])([0-9][0-9,]*(?:\s*[+×]\s*[0-9][0-9,]*)+)\s*=\s*([0-9][0-9,]*)"
    found=re.findall(pattern,text)
    assert len(found)>=minimum,"Missing worked equalities"
    for expression,result in found:
        total=sum(math.prod(int(n.strip().replace(",","")) for n in term.split("×")) for term in expression.split("+"))
        assert total==int(result.replace(",","")),"Incorrect bridge equality: "+expression+" = "+result
    return len(found)


def validate_b004(target,bridge):
    canonical={"fs-id2220075":37519248,"fs-id1851678":8165432098710,
               "fs-id1469854":9258137904061,"fs-id1278691":17864325619004,
               "fs-id1394436":327577529,"fs-id2243722":316128839,"fs-id1269733":31536000}
    target_ids={e.get("id"):e for e in target.iter() if e.get("id")}
    for ident,value in canonical.items():
        assert english_name(value) in text_of(target_ids[ident]).lower(),"Canonical English name changed: "+ident
    ids={e.get("id"):e for e in bridge.iter() if e.get("id")}
    skills={"D01":24315608,"D02":6020004,"D03":8007040,"D04":12300000,
            "R01":42617305,"R02":9060002,"R03":5006070,"R04":23408000}
    for item,value in skills.items():
        question=text_of(ids["B004-"+item]); answer=text_of(ids["B004-S-"+item])
        assert english_name(value) in (question+" "+answer).lower(),"Skill English name changed: "+item
        assert f"{value:,}" in answer,"Skill numeral changed: "+item
    for source_id in ["fs-id2601285","fs-id1773572","fs-id2472209","fs-id2060477"]:
        assert "B004-S-"+source_id in ids,"Missing full source solution"
    whole=text_of(bridge)
    for fragment in ["8 | 165 | 432 | 098 | 710","9 | 258 | 137 | 904 | 061","17 | 864 | 325 | 619 | 004","31 | 536 | 000"]:
        assert fragment in whole,"Zero-group changed: "+fragment
    assert "365 × 24 × 60 × 60 = 31,536,000" in text_of(ids["B004-source-context"])
    return verify_numeric_equalities(whole,11)
