"""Audit local schema-guided scope outputs independently from the runner."""
import argparse,hashlib,json
from pathlib import Path
from collections import defaultdict
from scope_output_gate import validate
from audit_qwen_scope_repair import summarize

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lines(p):return [json.loads(x) for x in p.read_text().splitlines()]
def run(stage,base):
    raw_path=stage/'result.json';r=json.loads(raw_path.read_text());m=json.loads((stage/'manifest.json').read_text())
    assert r['model']==m['model']=='gemma4:12b-it-qat'
    assert r['model_digest']==m['model_digest']=='38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3'
    assert r['manifest_sha256']==sha(stage/'manifest.json') and r['source_sha256']==m['input_sha256']['gemma_scope_screen.py']==sha(stage/'gemma_scope_screen.py')
    assert all(sha(stage/n)==v for n,v in m['input_sha256'].items())
    cases={x['pmcid']:x for x in lines(stage/'cases.jsonl')};assert len(cases)==m['expected_cases']
    prior=base/'data/gemma_scope_20261003';assert sha(prior/'result.json')==m['prior_result_sha256']
    attempted={x['pmcid'] for x in json.loads((prior/'result.json').read_text())['rows']};assert attempted==set(m['prior_attempted_ids']) and not attempted&set(cases)
    original={x['pmcid']:x for x in lines(prior/'cases.jsonl')};assert set(cases)==set(original)-attempted
    assert all(c==original[k] for k,c in cases.items())
    assert sha(base/'pmc_scope_review_labels_2026-10-02.jsonl')==json.loads((base/'pmc_scope_review_audit_2026-10-02.json').read_text())['label_sha256']
    assert sha(base/'pmc_scope_fresh_labels_2026-10-03.jsonl')==json.loads((base/'pmc_scope_fresh_label_freeze_2026-10-03.json').read_text())['labels_sha256']
    labels={x['pmcid']:x for p in [base/'pmc_scope_review_labels_2026-10-02.jsonl',base/'pmc_scope_fresh_labels_2026-10-03.jsonl'] for x in lines(p)}
    assert len(r['rows'])<=m['expected_cases'] and len({x['pmcid'] for x in r['rows']})==len(r['rows'])
    if r['status']=='complete':assert len(r['rows'])==m['expected_cases'] and set(x['pmcid'] for x in r['rows'])==set(cases)
    groups=defaultdict(list);failed=[];truncated=[]
    for row in r['rows']:
        c=cases[row['pmcid']];assert row['xml_sha256']==c['xml_sha256']==labels[row['pmcid']]['xml_sha256']
        assert row['context_sha256']==c['context_sha256']==hashlib.sha256(c['source_context'].encode()).hexdigest()
        assert row['split']==c['split'] and row['training_admission'] is False
        if 'request_failure' in row:failed.append(row['pmcid']);continue
        assert row['strict']==validate(row['raw'],c['source_context'])
        assert row['transport_gate']==validate(row['raw'],c['source_context'],allow_fence=True)
        assert row['response']['done'] is True and row['eval_count']<=512 and 0<row['prompt_eval_count']<=8192
        if row['done_reason']!='stop':truncated.append(row['pmcid'])
        groups[row['split']].append(row)
    summary={k:summarize(v,labels) for k,v in groups.items()}
    return {'status':'audited_'+r['status'],'raw_sha256':sha(raw_path),'calls_completed_or_failed':len(r['rows']),
      'request_failure_ids':failed,'non_stop_completion_ids':truncated,'groups':summary,
      'model':r['model'],'model_digest':r['model_digest'],'ollama_version':r['ollama_version'],
      'elapsed_seconds':r['elapsed_seconds'],'prompt_eval_count_range':[min((x.get('prompt_eval_count',0) for x in r['rows']),default=0),max((x.get('prompt_eval_count',0) for x in r['rows']),default=0)],
      'training_admission':False,'limits':'Schema-guided local generation, development agreement with draft references. Different model/decoder/runtime together; no model-size causality, expert gold, independent accuracy or corpus admission. Requested context hashes verified; internal server text truncation not independently observed.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',type=Path);p.add_argument('base',type=Path);p.add_argument('out',type=Path);a=p.parse_args();d=run(a.stage,a.base);assert not a.out.exists();a.out.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k!='groups'},indent=2));print(json.dumps({k:{n:v for n,v in g.items() if n not in ['confusion_counts','disagreements']} for k,g in d['groups'].items()},indent=2))
