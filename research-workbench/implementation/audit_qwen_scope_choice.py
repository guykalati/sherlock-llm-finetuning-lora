"""Audit fixed-choice decisions; no quote/entailment/accuracy inflation."""
import argparse,hashlib,json,math
from pathlib import Path
from collections import Counter,defaultdict
from qwen_scope_choice import TIER_OPTIONS,CENTRALITY_OPTIONS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lines(p):return [json.loads(x) for x in p.read_text().splitlines()]
def run(raw_path,stage,base):
    r=json.loads(raw_path.read_text());m=json.loads((stage/'manifest.json').read_text())
    assert r['status']=='complete' and len(r['rows'])==48
    assert r['manifest_sha256']==sha(stage/'manifest.json')
    assert r['source_sha256']==sha(stage/'qwen_scope_choice.py')==m['input_sha256']['qwen_scope_choice.py']
    assert r['cases_sha256']==sha(stage/'cases.jsonl')==m['input_sha256']['cases.jsonl']
    assert r['model_file_sha256']==m['model_file_sha256']
    cases={x['pmcid']:x for x in lines(stage/'cases.jsonl')}
    labels={x['pmcid']:x for p in [base/'pmc_scope_review_labels_2026-10-02.jsonl',base/'pmc_scope_fresh_labels_2026-10-03.jsonl'] for x in lines(p)}
    assert len({x['pmcid'] for x in r['rows']})==len(cases)==48
    groups=defaultdict(list)
    for row in r['rows']:
        case=cases[row['pmcid']];assert row['xml_sha256']==case['xml_sha256']==labels[row['pmcid']]['xml_sha256']
        assert row['context_sha256']==case['context_sha256']==hashlib.sha256(case['source_context'].encode()).hexdigest()
        assert row['split']==case['split'] and row['training_admission'] is False
        prediction={}
        for field,options in [('study_tier',TIER_OPTIONS),('cardiac_centrality',CENTRALITY_OPTIONS)]:
            decision=row['decisions'][field];probs=decision['choice_relative_probabilities'];names=[x[0] for x in options]
            assert set(probs)==set(names) and all(math.isfinite(x) and 0<=x<=1 for x in probs.values())
            assert math.isclose(sum(probs.values()),1,abs_tol=1e-5)
            assert decision['selected']==max(probs,key=probs.get)
            assert names[int(decision['selected_digit'])-1]==decision['selected']
            ordered=sorted(probs.values(),reverse=True);assert math.isclose(decision['choice_margin'],ordered[0]-ordered[1],abs_tol=1e-6)
            assert 0<decision['input_tokens']<=4096
            prediction[field]=decision['selected']
        ref={k:labels[row['pmcid']][k] for k in prediction}
        groups[row['split']].append({'pmcid':row['pmcid'],'prediction':prediction,'reference':ref,
            'both_agree':prediction==ref,'source_review_required':True})
    summary={}
    for key,rows in groups.items():
        disagreements=[row for row in rows if not row['both_agree']]
        confusions={field:Counter((x['reference'][field],x['prediction'][field]) for x in rows) for field in ['study_tier','cardiac_centrality']}
        summary[key]={'cases':len(rows),'controller_valid_records':len(rows),'model_json_compliance':'not measured: controller constructs records',
          'study_tier_agreement':sum(x['reference']['study_tier']==x['prediction']['study_tier'] for x in rows),
          'centrality_agreement':sum(x['reference']['cardiac_centrality']==x['prediction']['cardiac_centrality'] for x in rows),
          'both_agreement':sum(x['both_agree'] for x in rows),'disagreements':disagreements,
          'confusion_counts':{field:[{'reference':a,'prediction':b,'count':v} for (a,b),v in c.items()] for field,c in confusions.items()}}
    return {'status':'audited_complete','raw_sha256':sha(raw_path),'groups':summary,'elapsed_seconds':r['elapsed_seconds'],
            'gpu_name':r['gpu_name'],'training_admission':False,
            'limits':'All48 are now development cases. Draft-reference agreement only; not independent expert accuracy. Controller schema does not prove model JSON compliance, evidence support, or calibrated confidence.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw',type=Path);p.add_argument('stage',type=Path);p.add_argument('base',type=Path);p.add_argument('out',type=Path);a=p.parse_args();d=run(a.raw,a.stage,a.base);assert not a.out.exists();a.out.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:{f:v for f,v in g.items() if f not in ['confusion_counts','disagreements']} for k,g in d['groups'].items()},indent=2))
