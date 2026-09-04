"""Normalize independently reviewed handoffs without changing source translations."""
from pathlib import Path
import re


def locator_owner(locator):
    """Return the nearest stable CNXML id encoded in a review locator."""
    for part in locator.split('/'):
        candidate = part.split('[', 1)[0]
        if re.fullmatch(r'(?:[A-Za-z]+-)+(?:id)?\d+', candidate):
            return candidate
    raise ValueError(('Review locator has no stable owner id', locator))


def media_metadata(review):
    if isinstance(review.get('source_alt_errata'), list):
        result = {'errata': {}, 'corrected_alternatives': {},
                  'corrected_table_names': {}, 'reader_bridges': {},
                  'math_token_replacements': {}}
        for item in review['source_alt_errata']:
            identifier = item['media_id']
            correction = item['actual_image_and_math_correction_gu']
            assert identifier not in result['errata']
            result['errata'][identifier] = {'correction_gu': correction}
            result['corrected_alternatives'][identifier] = correction
        for item in review.get('accessibility_bridges', []):
            identifier = item['media_id']
            note = item['complete_alt_gu']
            assert identifier not in result['reader_bridges']
            result['reader_bridges'][identifier] = {'reader_note_gu': note}
            result['corrected_alternatives'][identifier] = note
        for item in review.get('text_errata', []):
            identifier = item.get('id') or locator_owner(item['locator'])
            assert identifier not in result['errata']
            result['errata'][identifier] = {'correction_gu': item['gujarati_handling']}
        for item in review.get('math_token_language_bridges', []):
            owner = item['owner_id']
            replacements = result['math_token_replacements'].setdefault(owner, {})
            source = item['source_mn']
            assert source not in replacements, ('Duplicate math-token bridge', owner, source)
            replacements[source] = item['localized_visible_gu']
        self_checks = [
            (filename, item)
            for filename, item in review.get('language_bearing_assets', {}).items()
            if 'blank_response_cells' in item
        ]
        assert len(self_checks) <= 1, ('Multiple implicit self-check assets', self_checks)
        if self_checks:
            filename, check = self_checks[0]
            labels = check['localized_visible_gu']
            assert len(labels) >= 5
            headers, rows = labels[:4], labels[4:]
            assert check['blank_response_cells'] == len(rows) * (len(headers) - 1)
            witness = next(item for item in review['media_inventory'] if item['asset'] == filename)
            result['self_check_table'] = {
                'source_image': filename,
                'source_image_sha256': witness['asset_sha256'],
                'headers': headers,
                'rows': rows,
            }
        return result
    if isinstance(review.get('source_errata'), list):
        result = {'errata': {}, 'corrected_alternatives': {},
                  'corrected_table_names': {}, 'reader_bridges': {}}
        for item in review['source_errata']:
            for identifier in item['source_ids']:
                assert identifier not in result['errata'], ('Duplicate source correction', identifier)
                result['errata'][identifier] = {'correction_gu': item['corrected_reader_text_gu']}
                if item.get('corrected_alt_gu'):
                    result['corrected_alternatives'][identifier] = item['corrected_alt_gu']
                name = item.get('corrected_aria_label_gu') or item.get('corrected_summary_gu')
                if name:
                    result['corrected_table_names'][identifier] = name
        for item in review.get('separate_reader_bridges', []) + review.get('reader_bridges', []):
            for identifier in item.get('source_ids') or [item['source_id']]:
                assert identifier not in result['reader_bridges'], ('Duplicate reader bridge', identifier)
                result['reader_bridges'][identifier] = {'reader_note_gu': item['note_gu']}
        check = review['self_check']
        witness = next(item for item in review['media'] if (item.get('source_file') or item.get('file')) == check['source_file'])
        assert check['blank_response_cells'] == len(check['skills']) * (len(check['headers']) - 1)
        result['self_check_table'] = {'source_image': check['source_file'], 'source_image_sha256': witness['sha256'],
                                      'headers': check['headers'], 'rows': check['skills']}
        return result
    if 'source_errata' in review:
        errata = review['source_errata']
        def correction(item):
            for field in ('corrected_gu','corrected_alt_gu','corrected_aria_gu','corrected_summary_gu'):
                if item.get(field):return item[field]
            if item['kind']=='source-name-spelling':
                return 'મૂળ કોષ્ટકમાં અંગ્રેજી નામ '+item['canonical_name']+' છે; ગુજરાતી નામ: '+item['name_gu']+'.'
            raise ValueError(('Missing reviewed correction',item))
        result = {
            'errata': {key: {'correction_gu': correction(item)} for key, item in errata.items() if item['kind']!='source-phrase-ambiguity'},
            'corrected_alternatives': {key: item.get('corrected_alt_gu') or correction(item) for key, item in errata.items() if 'alt' in item['kind']},
            'corrected_table_names': {key: item.get('corrected_aria_gu') or item.get('corrected_summary_gu') or correction(item) for key, item in errata.items() if 'aria' in item['kind'] or 'corrected_summary_gu' in item},
            'accessible_charts': {item['image']: dict(item, source_image_sha256=next(m['sha256'] for m in review['media'] if m['source_file'] == item['image'])) for item in review.get('source_chart_accessible_data',[])},
            'reader_bridges': {**review.get('separate_reader_bridges',{}),**{key:item for key,item in errata.items() if item['kind']=='source-phrase-ambiguity'}},
        }
        check = review['self_check']
        witness = next(item for item in review['media'] if item['source_file'] == (check.get('image') or check['source_file']))
        assert len(check['response_cells']) == len(check['rows'])
        assert all(len(row) == len(check['columns'])-1 and all(v is None for v in row) for row in check['response_cells'])
        result['self_check_table'] = {'source_image': witness['source_file'], 'source_image_sha256': witness['sha256'],
                                      'headers': check['columns'], 'rows': check['rows']}
        return result
    result = {
        'corrected_alternatives': {key: item['corrected_alt_gu'] for key, item in review['source_alt_errata'].items()},
        'errata': {key: {'correction_gu': item['corrected_alt_gu']} for key, item in review['source_alt_errata'].items()},
        'corrected_table_names': {key: item['corrected_attribute_gu'] for key, item in review.get('source_attribute_errata', {}).items()},
    }
    result['errata'].update({key: {'correction_gu': item['corrected_attribute_gu']} for key, item in review.get('source_attribute_errata', {}).items()})
    omission = review.get('source_body_omission')
    if omission:
        note = result['errata'].setdefault(omission['table_id'], {'correction_gu': ''})
        note['correction_gu'] += ' મૂળ સમજણમાં છૂટેલું પગલું: '+omission['companion_explanation_gu']
    check = review['self_check_table']
    witness = next(item for item in review['media_inventory'] if Path(item['source']).name == check['image'])
    result['self_check_table'] = {'source_image': witness['source'], 'source_image_sha256': witness['sha256'],
                                  'headers': check['headers_gu'], 'rows': check['rows_gu']}
    return result
