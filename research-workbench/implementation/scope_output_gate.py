"""Validate saved scope outputs; optional whole-response fence removal only."""
import json
import re

TIERS = {'human_clinical_empirical', 'human_health_services', 'preclinical',
         'veterinary', 'review_consensus', 'case_report', 'methods_only_or_unresolved', 'other'}
CENTRALITY = {'core', 'background_only', 'uncertain'}
KEYS = {'study_tier', 'cardiac_centrality', 'population_quote', 'question_quote', 'reason'}

def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate_key')
        value[key] = item
    return value

def reject_constant(value):
    raise ValueError('non_json_constant')

def validate(raw, context, *, allow_fence=False):
    text = raw
    normalized = False
    if allow_fence:
        match = re.fullmatch(r'\s*```(?:json)?[ \t]*\r?\n([\s\S]*?)\r?\n```\s*', raw)
        if match:
            text = match.group(1)
            normalized = True
    try:
        value = json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (ValueError, TypeError):
        return {'prediction': None, 'failure': 'invalid_json', 'fence_removed': normalized}
    failure = None
    if not isinstance(value, dict) or set(value) != KEYS:
        failure = 'schema'
    elif not all(isinstance(value[k], str) for k in KEYS):
        failure = 'field_type'
    elif value['study_tier'] not in TIERS or value['cardiac_centrality'] not in CENTRALITY:
        failure = 'enum'
    else:
        for key in ('population_quote', 'question_quote'):
            quote = value[key]
            if not 20 <= len(quote) <= 360 or quote not in context:
                failure = key + '_not_exact'
                break
    return {'prediction': value if failure is None else None,
            'failure': failure, 'fence_removed': normalized}
