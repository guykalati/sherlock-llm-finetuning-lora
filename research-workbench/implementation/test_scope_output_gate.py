import json
import unittest
from scope_output_gate import validate

class ScopeGateChecks(unittest.TestCase):
    def setUp(self):
        self.context = 'This completed study enrolled 40 adult patients with heart failure.'
        self.value = dict(study_tier='human_clinical_empirical', cardiac_centrality='core',
                          population_quote='enrolled 40 adult patients',
                          question_quote='patients with heart failure', reason='fixture')
        self.raw = json.dumps(self.value)
    def test_strict_and_whole_fence(self):
        fenced = '```json\n' + self.raw + '\n```'
        self.assertIsNone(validate(self.raw, self.context)['failure'])
        self.assertEqual(validate(fenced, self.context)['failure'], 'invalid_json')
        derived = validate(fenced, self.context, allow_fence=True)
        self.assertEqual(derived['prediction'], self.value)
        self.assertTrue(derived['fence_removed'])
    def test_does_not_repair_quotes(self):
        raw = json.dumps(dict(self.value, population_quote='enrolled 41 adult patients'))
        self.assertEqual(validate(raw, self.context, allow_fence=True)['failure'], 'population_quote_not_exact')
    def test_does_not_extract_from_prose(self):
        raw = 'Here is the result:\n```json\n' + self.raw + '\n```'
        self.assertEqual(validate(raw, self.context, allow_fence=True)['failure'], 'invalid_json')
    def test_rejects_duplicates_and_constants(self):
        duplicate = self.raw[:-1] + ', "reason": "overwrite"}'
        self.assertEqual(validate(duplicate, self.context)['failure'], 'invalid_json')
        self.assertEqual(validate('{"reason": NaN}', self.context)['failure'], 'invalid_json')
    def test_rejects_types_enums_and_extra_fields(self):
        for value, expected in [(dict(self.value, study_tier=[]), 'field_type'),
                                (dict(self.value, study_tier='unknown'), 'enum'),
                                (dict(self.value, extra='x'), 'schema')]:
            self.assertEqual(validate(json.dumps(value), self.context)['failure'], expected)
    def test_rejects_truncation_or_multiple_objects(self):
        for raw in ['```json\n' + self.raw, self.raw + self.raw]:
            self.assertEqual(validate(raw, self.context, allow_fence=True)['failure'], 'invalid_json')

if __name__ == '__main__':
    unittest.main()
