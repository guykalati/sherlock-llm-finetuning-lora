"""Verify training provenance and recompute QA scores from saved predictions."""
import argparse,collections,hashlib,json,math,re,string
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def normal(s):return ' '.join(re.sub(r'\b(a|an|the)\b',' ',s.lower()).translate(str.maketrans('','',string.punctuation)).split())
def f1(pred,ref):
    p=normal(pred).split();r=normal(ref).split()
    if not p or not r:return float(p==r)
    common=sum((collections.Counter(p)&collections.Counter(r)).values())
    return 2*common/(len(p)+len(r))
def verify(adapter_root=None):
    out=ROOT/'output';r=json.loads((out/'result.json').read_text());data=json.loads((out/'data_manifest.json').read_text())
    assert r['status']=='completed' and r['source_sha256']==sha(ROOT/'run.py')
    for p,h in data['files'].items():assert sha(ROOT/'data'/p)==h,p
    assert data['sft_counts']=={'train':458,'validation':59,'test':106}
    adapter_root=Path(adapter_root) if adapter_root else out
    adapters_available=all((adapter_root/stage/'adapter').is_dir() for stage in ['attention','attention_mlp','sft'])
    for stage in ['attention','attention_mlp','sft']:
        summary=r['sft'] if stage=='sft' else r['cpt'][stage]
        history=json.loads((out/stage/'history.json').read_text());assert history['initial']==summary['initial'] and history['history']==summary['history']
        if adapters_available:
            for name,h in summary['adapter_sha256'].items():assert sha(adapter_root/stage/'adapter'/name)==h,(stage,name)
        for row in [summary['initial'],summary['final']]:assert math.isclose(math.exp(row['loss']),row['perplexity'])
    assert r['sft_initial_adapter_sha256']==r['cpt']['attention_mlp']['adapter_sha256']
    a=r['cpt']['attention'];b=r['cpt']['attention_mlp'];assert a['initial']==b['initial'] and a['steps']==b['steps']==200
    checkpoints=[(x['step'],x['validation']['perplexity'],y['validation']['perplexity']) for x,y in zip(a['history'],b['history'])];assert len(checkpoints)==8
    refs={x['id']:x for x in map(json.loads,(ROOT/'data/test_answers.jsonl').read_text().splitlines())};preds=[json.loads(s) for s in (out/'qa_predictions.jsonl').read_text().splitlines()];assert len(preds)==212
    categories={};examples={}
    for stage in ['cpt','sft']:
        selected=[x for x in preds if x['stage']==stage];assert len(selected)==106 and {x['id'] for x in selected}==set(refs)
        for x in selected:
            ref=refs[x['id']];assert x['question']==ref['question'] and x['reference']==ref['answer'];answers=ref.get('aliases') or [ref['answer']]
            exact=float(normal(x['prediction']) in [normal(y) for y in answers if normal(y)]);score=max(f1(x['prediction'],y) for y in answers)
            assert exact==x['accuracy'] and math.isclose(score,x['f1'],abs_tol=1e-12),x['id']
        assert math.isclose(sum(x['accuracy'] for x in selected)/106,r['qa'][stage]['exact_match']);assert math.isclose(sum(x['f1'] for x in selected)/106,r['qa'][stage]['token_f1'])
        categories[stage]={c:{'n':len(xs),'exact_match':sum(x['accuracy'] for x in xs)/len(xs),'token_f1':sum(x['f1'] for x in xs)/len(xs)} for c in sorted({x['category'] for x in selected}) for xs in [[x for x in selected if x['category']==c]]}
        examples[stage]=sorted(selected,key=lambda x:(x['f1'],x['id']))[:5]
    audit={'status':'passed','source_data_hashes_verified':True,'adapter_hash_verification':'verified' if adapters_available else 'unavailable; weights are external','qa_predictions_recomputed':212,'same_cpt_baseline_and_budget':True,'mlp_lower_validation_perplexity_checkpoints':sum(y<x for _,x,y in checkpoints),'checkpoints':checkpoints,'cpt_to_sft_adapter_handoff_bound':True,'qa_by_category':categories,'lowest_f1_examples':examples,'result_sha256':sha(out/'result.json'),'limits':'Recomputes scores against synthetic/course references; does not certify reference truth or causal generalization beyond this fixed seed.'}
    (out/'result_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='lowest_f1_examples'},indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--adapter-root',type=Path);args=parser.parse_args()
    if args.adapter_root:
        assert all((args.adapter_root/s/'adapter').is_dir() for s in ['attention','attention_mlp','sft']), 'Explicit adapter root must contain all three adapter directories'
    verify(args.adapter_root)
