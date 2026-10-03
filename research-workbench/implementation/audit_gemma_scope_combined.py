"""Combine separately audited finite scope stages, preserving the timeout."""
import argparse,hashlib,json
from pathlib import Path
from audit_qwen_scope_repair import summarize
from audit_gemma_scope import run as first_audit
from audit_gemma_scope_remaining import run as remaining_audit
def combine(base):
    stages=[base/'data/gemma_scope_20261003',base/'data/gemma_scope_remaining_20261003'];first_audit(stages[0],base);remaining_audit(stages[1],base)
    labels={x['pmcid']:x for n in ['pmc_scope_review_labels_2026-10-02.jsonl','pmc_scope_fresh_labels_2026-10-03.jsonl'] for x in map(json.loads,(base/n).read_text().splitlines())};rows=[];sources=[]
    for stage in stages:
        p=stage/'result.json';r=json.loads(p.read_text());sources.append({'stage':stage.name,'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':r['status'],'attempts':len(r['rows']),'elapsed_seconds':r['elapsed_seconds']});rows.extend(r['rows'])
    assert len(rows)==48 and len({x['pmcid'] for x in rows})==48
    groups={}
    for split in ['old_development','fresh_development']:
        subset=[x for x in rows if x['split']==split];complete=[x for x in subset if 'request_failure' not in x];groups[split]={'attempts':len(subset),'request_failures':[x['pmcid'] for x in subset if 'request_failure' in x],**summarize(complete,labels)}
    return {'status':'audited_combined_with_one_request_failure','distinct_attempts':48,'complete_responses':47,'strict_valid':sum(x.get('strict',{}).get('prediction') is not None for x in rows),'sources':sources,'groups':groups,'training_admission':False,'limits':'Two finite local stages; one timed-out case never retried. Draft-reference development agreement; model/runtime/schema changed together. Corpus endpoint boundaries remain unresolved.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('base',type=Path);a=p.parse_args();print(json.dumps(combine(a.base),indent=2))
