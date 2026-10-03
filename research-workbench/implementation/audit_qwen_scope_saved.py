"""Audit frozen 32-case Qwen result without inference or changing raw outcomes."""
import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
from scope_output_gate import validate

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def lines(path): return [json.loads(x) for x in path.read_text().splitlines()]

def audit(raw_path, cases_path, labels_path, manifest_path, source_path):
    raw = json.loads(raw_path.read_text()); manifest = json.loads(manifest_path.read_text())
    assert sha(raw_path) == 'aae8d36c9d70ebfc1da375d9b47354e3b9c5ad0696a57c992699e8a81068f156'
    assert sha(cases_path) == manifest['cases_sha256'] == raw['cases_sha256']
    assert sha(labels_path) == manifest['draft_labels_sha256']
    assert sha(source_path) == manifest['source_sha256'] == raw['source_sha256']
    assert raw['model_file_sha256'] == manifest['model_file_sha256']
    cases = {x['pmcid']: x for x in lines(cases_path)}
    labels = {x['pmcid']: x for x in lines(labels_path)}
    assert len(raw['rows']) == len(cases) == len(labels) == 32
    assert len({x['pmcid'] for x in raw['rows']}) == 32
    assert {x['pmcid'] for x in raw['rows']} == set(cases) == set(labels)
    # Use only the frozen trusted schema function, without importing its GPU stack.
    tree = ast.parse(source_path.read_text())
    selected = [n for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id in ('TIERS', 'CENTRALITY') for t in n.targets)]
    selected += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'check']
    scope = {}; exec(compile(ast.Module(body=selected, type_ignores=[]), str(source_path), 'exec'), scope)
    derived = []; failures = Counter(); agreements = Counter(); matrices = {'study_tier': Counter(), 'cardiac_centrality': Counter()}
    for row in raw['rows']:
        case = cases[row['pmcid']]; label = labels[row['pmcid']]
        assert row['xml_sha256'] == case['xml_sha256'] == label['xml_sha256']
        assert sha_context(case['source_context']) == case['context_sha256']
        assert case['source_context'].startswith(row['actual_context'])
        assert row['context_truncated'] == (case['source_context'] != row['actual_context'])
        assert row['prediction'] is None and row['validation_failure'] == 'invalid_json'
        assert validate(row['raw'], row['actual_context'])['failure'] == 'invalid_json'
        gate = validate(row['raw'], row['actual_context'], allow_fence=True)
        assert gate['fence_removed']
        parsed = json.loads(row['raw'].strip().split('\n',1)[1].rsplit('\n',1)[0])
        assert scope['check'](parsed, row['actual_context']) == gate['failure']
        if gate['failure']: failures[gate['failure']] += 1
        record = {'pmcid': row['pmcid'], 'xml_sha256': row['xml_sha256'], **gate,
                  'raw_failure': row['validation_failure'], 'training_eligibility': 'unreviewed'}
        if gate['prediction']:
            p = gate['prediction']; record['draft_reference'] = {k:label[k] for k in matrices}
            for k in matrices:
                matrices[k][(label[k],p[k])] += 1
                agreements[k] += p[k] == label[k]
            agreements['both'] += all(p[k] == label[k] for k in matrices)
        derived.append(record)
    valid = sum(x['prediction'] is not None for x in derived)
    return {'status': 'audited_saved_outputs', 'raw_sha256': sha(raw_path), 'cases': 32,
            'original_strict_valid': 0, 'whole_fence_responses': 32,
            'derived_valid': valid, 'derived_failures': dict(failures),
            'draft_agreement_counts_among_derived_valid': dict(agreements),
            'draft_comparison_denominator': valid,
            'confusion_counts': {k:[{'reference':a,'prediction':b,'count':c} for (a,b),c in v.items()] for k,v in matrices.items()},
            'truncated_contexts': sum(x['context_truncated'] for x in raw['rows']),
            'rows': derived,
            'limits': 'Post hoc fence-only replay, not raw format success or a new model run. Exact quotes do not prove scientific classification. Draft reference is one agent narrative review, not expert gold. No automatic admission or training.'}

def sha_context(value): return hashlib.sha256(value.encode()).hexdigest()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('raw',type=Path); parser.add_argument('cases',type=Path)
    parser.add_argument('labels',type=Path); parser.add_argument('manifest',type=Path); parser.add_argument('source',type=Path); parser.add_argument('output',type=Path)
    a=parser.parse_args(); result=audit(a.raw,a.cases,a.labels,a.manifest,a.source)
    assert not a.output.exists(), 'Refuse overwriting audit evidence'
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','confusion_counts')},indent=2))
