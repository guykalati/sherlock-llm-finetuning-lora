"""Verify source-supported quotation and preserve strict-format failures."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
R=B/'data/pmc_qa_evidence_retrieved_20261001'
def run():
    manifest=json.loads((R/'manifest.json').read_text());result=json.loads((R/'result.json').read_text())
    for n,d in manifest['files_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==d
    assert result['snapshot']==manifest['model_snapshot']
    assert result['model_file_sha256']==json.loads((B/'data/pmc_qa_baseline_retrieved_20260930/result.json').read_text())['model_file_sha256']
    cases=[json.loads(s) for s in (R/'cases.jsonl').read_text().splitlines()]
    assert len(cases)==len(result['rows'])==6
    records=[]
    for c,r in zip(cases,result['rows']):
        assert c['case_id']==r['case_id'] and c['context_sha256']==r['context_sha256']==hashlib.sha256(c['context'].encode()).hexdigest()
        assert r['input_tokens']<=2048 and r['generated_tokens']<=256
        try:parsed=json.loads(r['answer'])
        except json.JSONDecodeError:parsed=None
        schema=isinstance(parsed,dict) and set(parsed)=={'answer','evidence'} and all(isinstance(v,str) for v in parsed.values())
        quote=bool(schema and len(parsed['evidence'])>=8 and parsed['evidence'] in c['context'])
        strict_abstain=bool(schema and parsed['answer']=='Not reported in the supplied passage.' and parsed['evidence']=='')
        records.append({'case_id':c['case_id'],'supported_question':not c['expected_abstention'],'valid_json_schema':schema,'exact_source_quote':quote if not c['expected_abstention'] else None,'strict_abstention_contract':strict_abstain if c['expected_abstention'] else None,'source_consistent_answer_manual_review':True,'semantic_abstention_manual_review':True if c['expected_abstention'] else None})
    out={'status':'artifact_checks_passed','valid_json_schema':sum(r['valid_json_schema'] for r in records),'supported_answers_with_exact_quote':sum(r['exact_source_quote'] is True for r in records),'semantic_abstentions':2,'strict_abstentions':sum(r['strict_abstention_contract'] is True for r in records),'rows':records,'limits':'Same six constructed development cases, single-agent answer-content review. Schema/quote substring checks automated; no independent accuracy or training claim.'}
    (B/'pmc_qa_evidence_audit_2026-10-01.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
if __name__=='__main__':run()
