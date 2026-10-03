"""Independent saved-output audit for the frozen 64-call repair comparison."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from scope_output_gate import validate

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def lines(path):return [json.loads(x) for x in path.read_text().splitlines()]

def summarize(rows, labels):
    result={'cases':len(rows),'strict_valid':0,'transport_valid':0,'both_agreement_over_all_cases':0,
            'tier_agreement_over_all_cases':0,'centrality_agreement_over_all_cases':0,
            'reference_centrality_uncertain':0,'primary_proposals':0,
            'primary_proposals_matching_draft_primary':0,'primary_proposals_reference_uncertain':0,
            'primary_proposals_clear_draft_nonprimary':0}
    failures=Counter();confusions={'study_tier':Counter(),'cardiac_centrality':Counter()};disagreements=[]
    for r in rows:
        ref=labels[r['pmcid']];p=r['transport_gate']['prediction']
        result['strict_valid']+=r['strict']['prediction'] is not None
        result['reference_centrality_uncertain']+=ref['cardiac_centrality']=='uncertain'
        if p is None:failures[r['transport_gate']['failure']]+=1;continue
        result['transport_valid']+=1
        for k in confusions:
            confusions[k][(ref[k],p[k])]+=1
            result[('tier' if k=='study_tier' else 'centrality')+'_agreement_over_all_cases']+=p[k]==ref[k]
        both=all(ref[k]==p[k] for k in confusions);result['both_agreement_over_all_cases']+=both
        if not both:disagreements.append({'pmcid':r['pmcid'],'reference':{k:ref[k] for k in confusions},'prediction':{k:p[k] for k in confusions},'reason':p['reason']})
        if p['study_tier']=='human_clinical_empirical' and p['cardiac_centrality']=='core':
            result['primary_proposals']+=1
            if ref['study_tier']=='human_clinical_empirical' and ref['cardiac_centrality']=='core':result['primary_proposals_matching_draft_primary']+=1
            elif ref['cardiac_centrality']=='uncertain':result['primary_proposals_reference_uncertain']+=1
            else:result['primary_proposals_clear_draft_nonprimary']+=1
    result['transport_failures']=dict(failures)
    result['confusion_counts']={k:[{'reference':a,'prediction':b,'count':c} for (a,b),c in v.items()] for k,v in confusions.items()}
    result['disagreements']=disagreements
    return result

def run(raw_path, stage, base):
    m=json.loads((stage/'manifest.json').read_text());raw=json.loads(raw_path.read_text())
    assert raw['status']=='complete' and len(raw['rows'])==64
    assert raw['manifest_sha256']==sha(stage/'manifest.json')
    assert raw['source_sha256']==sha(stage/'qwen_scope_repair.py')==m['input_sha256']['qwen_scope_repair.py']
    assert raw['gate_sha256']==sha(stage/'scope_output_gate.py')==m['input_sha256']['scope_output_gate.py']
    assert raw['cases_sha256']==sha(stage/'cases.jsonl')==m['input_sha256']['cases.jsonl']
    frozen=json.loads((base/'pmc_scope_fresh_label_freeze_2026-10-03.json').read_text())
    assert sha(base/'pmc_scope_fresh_labels_2026-10-03.jsonl')==frozen['labels_sha256']
    assert sha(stage/'fresh_selection.json')==frozen['selection_sha256']
    assert sha(base/'pmc_scope_fresh_label_freeze_2026-10-03.json')==m['fresh_label_freeze_sha256']
    cases={r['pmcid']:r for r in lines(stage/'cases.jsonl')}
    old_labels={r['pmcid']:r for r in lines(base/'pmc_scope_review_labels_2026-10-02.jsonl')}
    fresh_labels={r['pmcid']:r for r in lines(base/'pmc_scope_fresh_labels_2026-10-03.jsonl')}
    assert len(cases)==48 and len(fresh_labels)==16 and not set(fresh_labels)&set(old_labels)
    labels={**old_labels,**fresh_labels};groups=defaultdict(list);seen=set();contexts={}
    for r in raw['rows']:
        key=(r['pmcid'],r['arm']);assert key not in seen;seen.add(key)
        case=cases[r['pmcid']];ref=labels[r['pmcid']]
        assert r['xml_sha256']==case['xml_sha256']==ref['xml_sha256']
        assert r['split']==case['split']
        assert hashlib.sha256(r['actual_context'].encode()).hexdigest()==r['context_sha256']
        assert case['source_context'].startswith(r['actual_context'])
        assert r['context_truncated']==(case['source_context']!=r['actual_context'])
        assert r['input_tokens']<=4096 and r['generation_tokens']<=512
        assert r['strict']==validate(r['raw'],r['actual_context'])
        assert r['transport_gate']==validate(r['raw'],r['actual_context'],allow_fence=True)
        if r['split']=='old_development':assert r['arm']=='revised' and r['actual_context']==case['source_context']
        else:
            if r['pmcid'] in contexts:assert contexts[r['pmcid']]==r['actual_context']
            contexts[r['pmcid']]=r['actual_context']
        groups[r['split']+'_'+r['arm']].append(r)
    expected={(id,'revised') for id in old_labels}|{(id,arm) for id in fresh_labels for arm in ('baseline','revised')}
    assert seen==expected
    original=json.loads((base/'data/qwen_scope_retrieved_20261003/result.json').read_text())
    previous=[]
    for r in original['rows']:
        case=cases[r['pmcid']];assert case['source_context']==r['actual_context']
        previous.append({**r,'strict':validate(r['raw'],r['actual_context']), 'transport_gate':validate(r['raw'],r['actual_context'],allow_fence=True)})
    summary={k:summarize(v,labels) for k,v in groups.items()};summary['old_development_original']=summarize(previous,labels)
    return {'status':'audited_complete','raw_sha256':sha(raw_path),'groups':summary,
            'fresh_contexts_clipped':sum(r['context_truncated'] for r in groups['fresh_development_revised']),
            'gpu_elapsed_seconds':raw['elapsed_seconds'],'gpu_name':raw['gpu_name'],
            'training_admission':False,'limits':'Agreement with single-agent draft references, not expert accuracy. Old cases are error-informed; fresh source labels are limited-scope and include uncertainty. No automatic corpus admission.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw',type=Path);p.add_argument('stage',type=Path);p.add_argument('base',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    result=run(a.raw,a.stage,a.base);assert not a.out.exists();a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{n:v for n,v in g.items() if n not in ('confusion_counts','disagreements')} for k,g in result['groups'].items()},indent=2))
