import hashlib,json,re
from collections import Counter
from pathlib import Path
root=Path('project-first-scan');imp=root/'implementation';stage=imp/'data/pmc_broad_boundary_20261003'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=root/'PMC_BROAD_BOUNDARY_SOURCE_REVIEW_2026-10-03.md';rows=json.loads(re.search(r'```json\s*(.*?)\s*```',report.read_text(),re.S)[1]);freeze=json.loads((imp/'pmc_broad_boundary_freeze_2026-10-03.json').read_text())
assert sha(root/'PMC_BROAD_SCOPE_POLICY_2026-10-03.md')==freeze['policy_sha256']
assert len(rows)==len({x['pmcid'] for x in rows})==12 and {x['pmcid'] for x in rows}==set(freeze['packets_sha256'])
for name,h in freeze['sources'].items():assert sha(Path(name))==h
strata=Counter();groups=Counter();roles=Counter();anchors=0
for r in rows:
 p=stage/(r['pmcid']+'.json');assert sha(p)==freeze['packets_sha256'][r['pmcid']];d=json.loads(p.read_text());assert r['xml_sha256']==d['xml_sha256'];strata['purposive_reused_development']+=1
 assert r['evidence_group'] in {'clinical','review','preclinical','unresolved_or_other'};assert r['topical_role'] in {'primary','secondary_substantive','background_only','unresolved'};assert r['topic_candidate']==(r['topical_role'] in {'primary','secondary_substantive'});assert r['training_admission'] is False and r['reference_quality']=='single-agent draft source review; not expert gold'
 paras={x['paragraph_index']:x for x in d['paragraphs']};assert {e['supports'] for e in r['evidence']}=={'topic','design'};quote_words=0
 for e in r['evidence']:
  q=e['quote'];a=paras[e['paragraph_index']];assert a['kind']=='p' and q in a['text'] and e['section']==a['section'];assert len(q.split())<=12;quote_words+=len(q.split());anchors+=1
 assert quote_words<=25;groups[r['evidence_group']]+=1;roles[r['topical_role']]+=1
 # Rebind source-group and subtype claims to original cached source objects, not metadata-only packets.
 original=next(json.loads(s) for s in Path(d['source_document_file']).read_text().splitlines() if json.loads(s)['pmcid']==r['pmcid']);assert original['sha256']==r['xml_sha256'] and original['version']==d['version']
assert set(strata.values())=={12}
out=imp/'pmc_broad_boundary_labels_2026-10-03.jsonl';assert [json.loads(line) for line in out.read_text().splitlines()]==sorted(rows,key=lambda x:x['pmcid'])
audit={'status':'passed_provenance_and_evidence_transport','cases':12,'sampling_strata':dict(strata),'draft_evidence_groups':dict(groups),'draft_topical_roles':dict(roles),'exact_source_anchors':anchors,'labels_sha256':sha(out),'review_report_sha256':sha(report),'freeze_sha256':sha(imp/'pmc_broad_boundary_freeze_2026-10-03.json'),'policy_sha256':freeze['policy_sha256'],'training_admission':False,'limitations':'Independent artifact checks do not establish scientific correctness or expert agreement. Single-agent draft on purposively selected, previously used development papers; no independent validation, gold labels or retroactive regrading. Unresolved/other remains held.'}
assert json.loads((imp/'pmc_broad_boundary_review_audit_2026-10-03.json').read_text())==audit;print(json.dumps(audit,indent=2))
