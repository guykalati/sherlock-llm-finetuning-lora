"""Independent identity/reservation/family checks, plus sampled naive context rescoring."""
import hashlib,json,random,re
from collections import defaultdict,Counter
from pathlib import Path
stage=Path('project-first-scan/implementation/data/pmc_broad_partition_20261003')
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def words(s):return re.findall(r'\w+',s.casefold())
def ngrams(s):
 t=words(s);return {' '.join(t[i:i+5]) for i in range(len(t)-4)}
m=json.loads((stage/'manifest.json').read_text());summary=json.loads((stage/'summary.json').read_text())
assert h('project-first-scan/implementation/pmc_broad_partition_screen.py')==m['source_sha256']
for name,d in {**m['inputs_sha256'],**m['sources']}.items():assert h(name)==d
assert h(stage/'screens.jsonl')==summary['screens_sha256'] and h(stage/'manifest.json')==summary['manifest_sha256']
docs={};family={k:defaultdict(set) for k in ['doi','pmid','body']};keys={}
for name in m['sources']:
 for line in Path(name).read_text().splitlines():
  d=json.loads(line);pid=d['pmcid'];assert pid not in docs;docs[pid]=d;body=' '.join(x['text'] for x in d['paragraphs']);k={'doi':(d['doi'] or '').strip().casefold(),'pmid':str(d['pmid']) if d['pmid'] else '', 'body':hashlib.sha256(' '.join(words(body)).encode()).hexdigest()};keys[pid]=k
  for kind,v in k.items():
   if v and (kind!='body' or body):family[kind][v].add(pid)
sel=json.loads(Path(m['development_selection']).read_text());qa=json.loads(Path(m['qa_exclusions']).read_text());reserved=set(sel['excluded_prior_development_ids'])|{x['pmcid'] for x in sel['selected']}|set(qa['pmcids']);reserved_keys={kind:{keys[p][kind] for p in reserved&docs.keys() if keys[p][kind]} for kind in keys[next(iter(keys))]};reserved_keys['doi'].update(x.strip().casefold() for x in qa['dois']);reserved_keys['pmid'].update(str(x) for x in qa['pmids'])
refs={str(pid):ngrams(' '.join(r['CONTEXTS'])) for pid,r in json.loads(Path(m['benchmark']).read_text()).items()};assert len(refs)==1000
rows=[json.loads(s) for s in (stage/'screens.jsonl').read_text().splitlines()];candidates={json.loads(s)['pmcid'] for s in Path(m['candidates']).read_text().splitlines()};assert len(rows)==len({r['pmcid'] for r in rows})==5403 and candidates=={r['pmcid'] for r in rows}
flags=Counter();sample=set(random.Random(20261003).sample(range(len(rows)),24))
for i,r in enumerate(rows):
 pid=r['pmcid'];d=docs[pid];k=keys[pid];assert r['xml_sha256']==d['sha256'] and r['version']==d['version'] and r['normalized_cached_body_sha256']==k['body']
 for kind,field in [('doi','same_doi_other_pmcids'),('pmid','same_pmid_other_pmcids'),('body','same_body_other_pmcids')]:assert r[field]==sorted(family[kind][k[kind]]-{pid})
 expected=[]
 if k['pmid'] in refs:expected.append('benchmark_pmid')
 if r['benchmark_context_matches']:expected.append('benchmark_context_overlap')
 if pid in reserved or any(k[kind] in reserved_keys[kind] for kind in k):expected.append('development_family_reserved')
 if any(r[f] for f in ['same_doi_other_pmcids','same_pmid_other_pmcids','same_body_other_pmcids']):expected.append('exact_family_review')
 assert r['holds']==expected and r['training_admission'] is False;flags.update(expected)
 if i in sample:
  vals=ngrams(d['abstract']+' '+' '.join(x['text'] for x in d['paragraphs']));found=[]
  for pmid,v in refs.items():
   shared=len(vals&v)
   if shared>=30:
    jac=shared/(len(vals)+len(v)-shared);con=shared/len(v)
    if jac>=.8 or con>=.9:found.append({'pmid':pmid,'shared':shared,'jaccard':jac,'containment':con})
  assert sorted(found,key=lambda x:x['pmid'])==r['benchmark_context_matches']
assert dict(flags)==summary['overlapping_hold_counts']
a={'status':'passed','verified_queue_records':len(rows),'verified_source_family_objects':len(docs),'independent_naive_context_rescores':len(sample),'overlapping_hold_counts':dict(flags),'summary_sha256':h(stage/'summary.json'),'screens_sha256':h(stage/'screens.jsonl'),'manifest_sha256':h(stage/'manifest.json'),'training_admission':False,'limitations':'All identity, exact-family and reservation fields checked; context algorithm independently sampled on 24 cases, not exhaustively independently rescored. No scientific relevance or semantic overlap verdict.'}
out=Path('project-first-scan/implementation/pmc_broad_partition_audit_2026-10-03.json');assert not out.exists();out.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
