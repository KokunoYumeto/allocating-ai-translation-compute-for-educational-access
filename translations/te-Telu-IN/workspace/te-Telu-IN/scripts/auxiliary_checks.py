"""Bounded source/target and actual-bridge checks for the two auxiliary units.

Reuse reviewed content assertions, not the preparer's acquisition entry points.
Ordinary builds need only committed frozen inputs and existing local readers.
"""
import xml.etree.ElementTree as ET
from prepare_auxiliary import review_catalog, review_bridge


def validate_auxiliary(unit,source,target,metadata,catalog,bridge):
    assert unit in {"TE-B009","TE-B010"}
    expected=review_catalog(unit,source,metadata,catalog)
    assert ET.tostring(expected)==ET.tostring(target),"Auxiliary target differs from checked localization"
    return review_bridge(unit,bridge,source)
