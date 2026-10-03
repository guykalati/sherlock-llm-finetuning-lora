"""Build source-traceable article-QA/abstention smoke cases, not gold evaluation."""
import hashlib
import json
from pathlib import Path
from pmc_metadata_pilot import read_jsonl

BASE=Path(__file__).resolve().parent

def run():
    path=BASE/'data/pmc_xml_expansion_20260929/documents.jsonl'
    documents={r['pmcid']:r for r in read_jsonl(path)}
    definitions=[
        ('PMC10464339','abstract',None,'How many people with diabetes were in the reported cohort?',
         '238 people with diabetes.','a cohort of 238 DM patients',False),
        ('PMC10464339','abstract',None,'What sensitivity and specificity were measured for cardiovascular events occurring one year after enrollment?',
         'The supplied passage does not report those one-year prospective-event sensitivity and specificity values.',None,True),
        ('PMC7512253','body','Ten patients with AF','How many patients supplied the intracardiac recordings?',
         'Ten patients with atrial fibrillation.','Ten patients with AF',False),
        ('PMC7512253','body','A 12-bipolar catheter','At what sampling rate were the bipolar intracardiac electrograms recorded?',
         '1 kHz.','digitally recorded at 1 kHz sampling rate',False),
        ('PMC7512253','body','Ten patients with AF','What was the measured effect of ablation on ten-year stroke mortality?',
         'The supplied passage does not report ten-year stroke mortality; its stated follow-up criterion concerns arrhythmia at 12 months.',None,True),
        ('PMC8774900','body','Total sample number for all single-cell experiments','How many Marfan syndrome patients and controls supplied tissue for the single-cell experiments?',
         'Three patients with Marfan syndrome and four controls.',
         'Total sample number for all single-cell experiments was 4 controls and 3 patients with MFS.',False),
    ]
    rows=[]
    for number,(pid,kind,needle,question,answer,quote,abstain) in enumerate(definitions,1):
        doc=documents[pid]
        if kind=='abstract':context=doc['abstract'];paragraph=None;section=['abstract']
        else:
            matches=[(i,p) for i,p in enumerate(doc['paragraphs']) if needle in p['text']]
            assert len(matches)==1,(pid,needle)
            paragraph,p=matches[0];context=p['text'];section=p['section']
        if quote:assert quote in context
        rows.append({'case_id':f'pmc_dev_{number:02d}','pmcid':pid,'version':doc['version'],
                     'pmid':doc['pmid'],'doi':doc['doi'],'license_code':doc['license_code'],
                     'xml_sha256':doc['sha256'],'paragraph_index':paragraph,'section':section,
                     'context':context,'context_sha256':hashlib.sha256(context.encode()).hexdigest(),
                     'question':question,'expected_answer':answer,'expected_abstention':abstain,
                     'support_quote':quote,'status':'single_agent_constructed_development_case',
                     'independent_expert_adjudication':False,
                     'use':'Prompt/evaluator development only. Exclude these article IDs from any later training or independent QA test.'})
    out=BASE/'pmc_qa_development_cases_2026-09-30.jsonl'
    out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    reserved={'pmcids':sorted({r['pmcid'] for r in rows}),'pmids':sorted({r['pmid'] for r in rows}),
              'dois':sorted({r['doi'] for r in rows}),'case_file_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
              'purpose':'Prevent constructed development prompts from becoming training/independent test material',
              'limits':'Six deliberately constructed cases, two unsupported questions; no model has been scored and no benchmark/generalization claim is supported.'}
    (BASE/'pmc_qa_development_exclusions_2026-09-30.json').write_text(json.dumps(reserved,indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'abstentions':sum(r['expected_abstention'] for r in rows),'reserved_articles':len(reserved['pmcids'])}))

if __name__=='__main__':run()
