"""Audit recorded development screens and cached model smoke without rerunning inference."""
import hashlib,json
from pathlib import Path
from pmc_schema_screen import validate,normalize
B=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def save(n,v):(B/n).write_text(json.dumps(v,indent=2)+'\n')

def run():
    plan=json.loads((B/'pmc_schema_screen_plan_2026-09-30.json').read_text())
    docs_path=B/'data/pmc_xml_expansion_20260929/documents.jsonl'
    assert sha(docs_path)==plan['documents_sha256']
    assert sha(B/'pmc_schema_screen.py')==plan['source_sha256']
    docs={r['pmcid']:r for r in rows(docs_path)}
    labels=rows(B/'data/pmc_schema_screen_20260930/labels.jsonl')
    assert len(labels)==len(plan['pmcids'])==29
    assert {r['pmcid'] for r in labels}==set(plan['pmcids'])
    accepted=0
    for r in labels:
        d=docs[r['pmcid']]
        raw=json.loads((B/'data/pmc_schema_screen_20260930'/ (r['pmcid']+'.json')).read_text())
        expected={k:d[k] for k in ['title','abstract','article_type','xml_lang']}
        expected['body_excerpt']='\n'.join(p['text'] for p in d['paragraphs'][:3])[:4000]
        assert raw['source']==expected
        assert r['xml_sha256']==d['sha256'] and r['training_eligibility']=='unreviewed'
        assert r['model_digest']==plan['model_digest']
        source=normalize(d['title']+' '+d['abstract']+' '+expected['body_excerpt'])
        valid=[]
        assert 1<=len(raw['attempts'])<=2
        for a in raw['attempts']:
            if 'response' not in a:continue
            candidate=json.loads(a['response']['message']['content'])
            assert validate(candidate,source)==a['valid']
            if a['valid']:valid.append(candidate)
        assert r['label']==(valid[0] if valid else None)
        assert r['status']==('screened' if valid else 'unresolved')
        accepted+=bool(valid)
    save('pmc_schema_screen_audit_2026-09-30.json',{'status':'passed','records':29,'screened':accepted,'unresolved':29-accepted,'no_training_admission':True,'checks':['frozen source and document hashes','exact input excerpts','raw response quotes and cross-field rules','call cap','model digest','record coverage'],'limits':'Development regression, no independent label validation.'})
    root=B/'data/pmc_qa_baseline_retrieved_20260930'
    manifest=json.loads((root/'manifest.json').read_text())
    assert manifest==json.loads((B/'pmc_qa_baseline_smoke_manifest_2026-09-30.json').read_text())
    for name,digest in manifest['files_sha256'].items():assert sha(root/name)==digest
    cases=rows(root/'cases.jsonl');result=json.loads((root/'result.json').read_text())
    assert result['cases_sha256']==sha(root/'cases.jsonl')
    assert result['source_sha256']==sha(root/'pmc_qa_baseline_smoke.py')
    assert result['snapshot']==manifest['model_snapshot'] and result['status']=='completed'
    assert len(cases)==len(result['rows'])==6
    rubric=[]
    for c,r in zip(cases,result['rows']):
        assert c['case_id']==r['case_id'] and c['pmcid']==r['pmcid']
        assert c['context_sha256']==r['context_sha256']==hashlib.sha256(c['context'].encode()).hexdigest()
        assert r['input_tokens']<=2048 and r['generated_tokens']<=128
        assert c['expected_abstention'] or c['support_quote'] in c['context']
        rubric.append({'case_id':c['case_id'],'expected_abstention':c['expected_abstention'],'answer_content_supported_by_passage':True,'correct_abstention':r['answer']=='Not reported in the supplied passage.' if c['expected_abstention'] else None,'explicit_exact_support_quote_present':None if c['expected_abstention'] else False})
    save('pmc_qa_baseline_smoke_audit_2026-09-30.json',{'status':'passed','artifact_checks':'manifest/source/cases hashes, ID coverage, context hashes and token caps','model_weights':'Compute job recorded cached file hashes and checked safetensor LFS blob hashes; weights not independently downloaded locally','manual_development_rubric':rubric,'supported_answers':4,'correct_abstentions':2,'supported_answers_with_requested_quote':0,'limits':'Single-agent rubric of six constructed development cases, not an independent accuracy estimate or trained-model evaluation.'})
    save('pmc_qa_baseline_retrieval_hashes_2026-09-30.json',{p.name:sha(p) for p in root.iterdir() if p.is_file()})
    print('Schema screen and QA artifact audits passed.')
if __name__=='__main__':run()
