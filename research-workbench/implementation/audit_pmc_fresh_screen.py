"""Audit fresh-case coverage, frozen labels, quote gates and scope sensitivity."""
import hashlib,json
from pathlib import Path
from collections import Counter
from pmc_schema_screen import validate,normalize
B=Path(__file__).resolve().parent

def run():
 p=json.loads((B/'pmc_fresh_model_plan_2026-10-01.json').read_text());freeze=json.loads((B/'pmc_fresh_screen_label_freeze_2026-10-01.json').read_text())
 docs_path=B/'data/pmc_fresh_xml_retrieved_20261001/documents.jsonl';human_path=B/'pmc_fresh_screen_labels_2026-10-01.jsonl'
 assert hashlib.sha256(docs_path.read_bytes()).hexdigest()==p['documents_sha256']==freeze['documents_sha256']
 assert hashlib.sha256(human_path.read_bytes()).hexdigest()==freeze['labels_sha256']
 assert hashlib.sha256((B/'pmc_fresh_screen.py').read_bytes()).hexdigest()==p['source_sha256']
 docs={r['pmcid']:r for r in map(json.loads,docs_path.read_text().splitlines())};human={r['pmcid']:r for r in map(json.loads,human_path.read_text().splitlines())}
 labels=[json.loads(s) for s in (B/'data/pmc_fresh_screen_20261001/labels.jsonl').read_text().splitlines()]
 assert len(labels)==len({r['pmcid'] for r in labels})==20 and {r['pmcid'] for r in labels}==set(p['pmcids'])==human.keys()
 full=Counter();clear=Counter();unresolved=[];diagnostics={}
 for row in labels:
  pid=row['pmcid'];d=docs[pid];raw=json.loads((B/'data/pmc_fresh_screen_20261001'/(pid+'.json')).read_text());expected={k:d[k] for k in ['title','abstract','article_type','xml_lang']};expected['body_excerpt']='\n'.join(x['text'] for x in d['paragraphs'][:3])[:4000]
  assert raw['source']==expected and row['xml_sha256']==d['sha256'] and row['model_digest']==p['model_digest'] and row['training_eligibility']=='unreviewed'
  text=normalize(d['title']+' '+d['abstract']+' '+expected['body_excerpt']);valid=[];why=[]
  assert 1<=len(raw['attempts'])<=2
  for a in raw['attempts']:
   if 'response' not in a:continue
   v=json.loads(a['response']['message']['content']);assert a['valid']==validate(v,text)
   if a['valid']:valid.append(v)
   else:why.append({k:bool(isinstance(v.get(k),str) and normalize(v[k]) in text and 20<=len(v[k])<=360) for k in ['topic_quote','design_quote']})
  assert row['label']==(valid[0] if valid else None)
  if not valid:key='unresolved';unresolved.append(pid);diagnostics[pid]=why
  else:
   pred=row['label']['topic']=='central' and row['label']['study_tier']=='human_clinical_empirical';actual=human[pid]['primary_human_empirical_candidate'];key='tp' if pred and actual else 'fp' if pred else 'fn' if actual else 'tn'
  full[key]+=1
  if not human[pid]['scope_ambiguity']:clear[key]+=1
 out={'status':'passed','records':20,'frozen_source_only_labels_verified':True,'all_cases_agreement':dict(full),'excluding_four_ambiguous_scope_cases':dict(clear),'unresolved_quote_diagnostics':diagnostics,'training_admission':False,'limits':'Fresh cases for unchanged prompt; single-agent labels, small set, two scope-dependent positive disagreements. Never infer independent expert accuracy.'}
 (B/'pmc_fresh_screen_audit_2026-10-01.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':run()
