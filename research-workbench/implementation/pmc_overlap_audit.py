"""Frozen context-only overlap and exact DOI/body duplicate screening."""
import hashlib,json,re,time
from collections import Counter,defaultdict
from pathlib import Path
D=Path('/home/guykalat/codex_pmc_large_xml_20261001/documents.jsonl')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def norm(s):return ' '.join(re.findall(r'\w+',s.casefold()))
def shingles(s):
 t=norm(s).split();return {' '.join(t[i:i+5]) for i in range(len(t)-4)}
def matches(values,refs,counts):
 out=[]
 for pid,n in counts.items():
  if n<30:continue
  j=n/(len(values)+len(refs[pid])-n);c=n/len(refs[pid])
  if j>=.8 or c>=.9:out.append({'pmid':pid,'shared':n,'jaccard':j,'containment':c})
 return sorted(out,key=lambda r:r['pmid'])
def run():
 start=time.monotonic();plan=json.loads(Path('manifest.json').read_text())
 for name,digest in plan['files_sha256'].items():assert sha(Path(name))==digest
 assert sha(D)==plan['documents_sha256']
 refs={r['pmid']:shingles(' '.join(r['contexts'])) for r in rows(Path('contexts.jsonl'))};assert len(refs)==1000
 index=defaultdict(list)
 for pid,values in refs.items():
  for value in values:index[value].append(pid)
 old=rows(Path('old_index.jsonl'));doi={r['doi'].strip().casefold():r['pmcid'] for r in old if r['doi']};bodies={r['body_sha256']:r['pmcid'] for r in old}
 screens=[]
 for i,r in enumerate(rows(D)):
  body=' '.join(p['text'] for p in r['paragraphs']);values=shingles(r['abstract']+' '+body)
  counts=Counter(pid for value in values for pid in index.get(value,()))
  found=matches(values,refs,counts)
  if i<10:assert found==matches(values,refs,{pid:len(values&v) for pid,v in refs.items()})
  digest=hashlib.sha256(norm(body).encode()).hexdigest();key=r['doi'].strip().casefold()
  screens.append({'pmcid':r['pmcid'],'benchmark_context_matches':found,'duplicate_doi_of':doi.get(key),'duplicate_body_of':bodies.get(digest) if body else None,'normalized_body_sha256':digest,'training_eligibility':'unreviewed'})
  if key:doi.setdefault(key,r['pmcid'])
  if body:bodies.setdefault(digest,r['pmcid'])
 Path('screens.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in screens))
 summary={'status':'passed','documents':len(screens),'benchmark_context_flagged':sum(bool(r['benchmark_context_matches']) for r in screens),'duplicate_doi':sum(bool(r['duplicate_doi_of']) for r in screens),'duplicate_body':sum(bool(r['duplicate_body_of']) for r in screens),'naive_rescores':10,'elapsed_seconds':time.monotonic()-start,'documents_sha256':sha(D),'screens_sha256':sha(Path('screens.jsonl')),'training_admission':False,'limits':'Only all1000 expert PubMedQA contexts and exact DOI/normalized-body duplicates against old977 and new batch. No semantic/paraphrase overlap or other benchmark exclusion claim.'}
 Path('summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
if __name__=='__main__':run()
