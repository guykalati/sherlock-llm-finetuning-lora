"""Reconstruct exact excerpt inputs and compare with new draft references only."""
import hashlib,json,math
from collections import Counter
from pathlib import Path
imp=Path('project-first-scan/implementation');stage=imp/'data/qwen_broad_scope_pilot_20261003'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((stage/'manifest.json').read_text());result=json.loads((stage/'result.json').read_text());assert sha(stage/'manifest.json')==result['manifest_sha256'] and sha(stage/'rows.jsonl')==result['rows_sha256']
for name,h in m['input_sha256'].items():assert sha(stage/name)==h
for name,h in m['source_packet_freezes'].items():assert sha(name)==h
cases={json.loads(s)['pmcid']:json.loads(s) for s in (stage/'cases.jsonl').read_text().splitlines()};refs={};refhashes={}
for name in ['pmc_broad_fresh_labels_2026-10-03.jsonl','pmc_broad_boundary_labels_2026-10-03.jsonl']:
 refhashes[name]=sha(imp/name)
 for s in (imp/name).read_text().splitlines():
  r=json.loads(s);assert r['pmcid'] not in refs;refs[r['pmcid']]=r
rows=[json.loads(s) for s in (stage/'rows.jsonl').read_text().splitlines()];assert len(rows)==len({x['pmcid'] for x in rows})==len(cases)==len(refs)==24
counts=Counter();confusions={k:Counter() for k in ['evidence_group','topical_role']};errors=[];compact=[]
for r in rows:
 case=cases[r['pmcid']];ref=refs[r['pmcid']];assert r['xml_sha256']==case['xml_sha256']==ref['xml_sha256'] and r['version']==case['version'] and r['training_admission'] is False;decisions={};both=True
 for field in ['evidence_group','topical_role']:
  d=r['decisions'][field];cap=d['paragraph_prefix_char_cap'];assert 50<=cap<=500 and cap%50==0;paras=case['paragraphs'];ix=sorted({round(i*(len(paras)-1)/min(23,len(paras)-1)) for i in range(min(24,len(paras)))}) if len(paras)>1 else [0]
  text='TITLE: '+case['title'][:400]+'\nABSTRACT: '+case['abstract'][:min(2000,cap*4)]+'\n'+'\n'.join('[p'+str(paras[i]['paragraph_index'])+' '+ ' / '.join(paras[i]['section'])+'] '+paras[i]['text'][:cap] for i in ix)
  assert text==d['source_context'] and hashlib.sha256(text.encode()).hexdigest()==d['context_sha256'] and d['paragraph_indices']==[paras[i]['paragraph_index'] for i in ix];assert 0<d['input_tokens']<=4096
  probs=d['choice_relative_probabilities'];assert len(probs)==4 and all(math.isfinite(p) and 0<=p<=1 for p in probs.values()) and abs(sum(probs.values())-1)<1e-5;assert d['selected']==max(probs,key=probs.get)
  agrees=d['selected']==ref[field];counts[field]+=agrees;both &= agrees;confusions[field][ref[field]+' -> '+d['selected']]+=1;decisions[field]={'prediction':d['selected'],'draft_reference':ref[field],'agrees':agrees,'context_sha256':d['context_sha256'],'input_tokens':d['input_tokens']}
 counts['both']+=both
 record={'pmcid':r['pmcid'],'decisions':decisions,'training_admission':False};compact.append(record)
 if not both:errors.append(record)
assert result['forward_calls']==48 and 0<result['elapsed_seconds']<660
out={'status':'passed_artifact_audit_model_rejected_for_scaling','cases':24,'agreement_counts_with_draft_references':dict(counts),'confusions':{k:dict(v) for k,v in confusions.items()},'errors':errors,'compact_decisions':compact,'reference_sha256':refhashes,'raw_result_sha256':sha(stage/'result.json'),'raw_rows_sha256':sha(stage/'rows.jsonl'),'manifest_sha256':sha(stage/'manifest.json'),'elapsed_seconds':result['elapsed_seconds'],'allocated_job_elapsed_seconds':57,'gpu_name':result['gpu_name'],'training_admission':False,'decision':'Do not scale this one-token constrained-score pilot into an admission classifier. Review design and background-only false inclusion errors first.','limits':'24 mixed fresh/purposive development articles; single-agent draft references are not expert gold. Exact context reconstruction checks provenance, not semantic correctness. Old labels/scores unchanged.'}
p=imp/'qwen_broad_scope_pilot_audit_2026-10-03.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','cases','agreement_counts_with_draft_references','confusions']},indent=2))
