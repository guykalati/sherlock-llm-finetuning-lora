"""Validate article-QA output without consulting reference answers or inventing quotes."""
import json

ABSTENTION = 'Not reported in the supplied passage.'

def validate(raw, passage):
    def reject(reason):
        return {'status': 'rejected', 'answer': ABSTENTION, 'evidence': '', 'reason': reason}
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError('duplicate JSON field')
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=unique_keys)
    except (ValueError, TypeError):
        return reject('invalid_json')
    if not isinstance(value, dict) or set(value) != {'answer', 'evidence'}:
        return reject('invalid_keys')
    if not all(isinstance(value[k], str) for k in value):
        return reject('non_string_fields')
    answer = value['answer'].strip(); evidence = value['evidence']
    if answer.rstrip('.') == ABSTENTION.rstrip('.'):
        if evidence != '': return reject('abstention_with_evidence')
        return {'status': 'abstained', 'answer': ABSTENTION, 'evidence': '',
                'normalized': value['answer'] != ABSTENTION}
    if not answer or not evidence or not evidence.strip(): return reject('missing_answer_or_quote')
    if evidence not in passage: return reject('quote_not_exact_source_span')
    return {'status': 'quote_validated', 'answer': answer, 'evidence': evidence,
            'limits': 'Exact source span only; answer entailment and requested endpoint are not verified.'}

def self_check():
    passage = 'The study enrolled 27 patients.'
    assert validate('{"answer":"27","evidence":"27 patients"}',passage)['status']=='quote_validated'
    assert validate('{"answer":"28","evidence":"28 patients"}',passage)['reason']=='quote_not_exact_source_span'
    # A real quote can accompany a wrong answer: this gate must not certify entailment.
    assert validate('{"answer":"28","evidence":"27 patients"}',passage)['status']=='quote_validated'
    assert validate('{"answer":"Not reported in the supplied passage","evidence":""}',passage)['status']=='abstained'
    assert validate('Not reported in the supplied passage.',passage)['status']=='rejected'
    assert validate('{"answer":"x","evidence":""}',passage)['status']=='rejected'
    assert validate('{"answer":"x","evidence":"27 patients","extra":1}',passage)['status']=='rejected'
    assert validate('{"answer":"Not reported in the supplied passage.","evidence":"27 patients"}',passage)['status']=='rejected'
    assert validate('{"answer":"27","answer":"28","evidence":"27 patients"}',passage)['status']=='rejected'

if __name__ == '__main__':
    self_check(); print('Source-span, malformed-output and abstention checks passed')
