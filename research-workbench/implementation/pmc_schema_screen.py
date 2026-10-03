"""Schema-visible development regression; no independent accuracy claim."""
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from pmc_metadata_pilot import read_jsonl, append_jsonl
from experiment_proposer import MODEL, DIGEST
from pmc_model_screen import normalize, TIERS

BASE = Path(__file__).resolve().parent
OUT = BASE/'data/pmc_schema_screen_20260930'
DOCS = BASE/'data/pmc_xml_expansion_20260929/documents.jsonl'
ORIGINS = ['human_participants','human_patient_tissue','cultured_cells_or_animals',
           'agency_protocols','published_literature','none_stated','uncertain']
DESIGNS = ['completed_multi_person_study','single_case','animal_or_cell_experiment',
           'protocol_comparison','review','planned_review','guideline','hypothesis','uncertain']

def validate(label, source):
    required = {'topic','study_tier','data_origin','study_design','topic_quote','design_quote','reason'}
    if set(label) != required:return False
    if label['topic'] not in ['central','peripheral','uncertain'] or label['study_tier'] not in TIERS:return False
    if label['data_origin'] not in ORIGINS or label['study_design'] not in DESIGNS:return False
    for name in ['topic_quote','design_quote']:
        quote = label[name]
        if not isinstance(quote,str) or not 20 <= len(quote) <= 360 or normalize(quote) not in source:return False
    if label['study_tier'] == 'human_clinical_empirical':
        if label['data_origin'] not in ['human_participants','human_patient_tissue']:return False
        if label['study_design'] != 'completed_multi_person_study':return False
    if label['study_design'] == 'single_case' and label['study_tier'] != 'single_case_report':return False
    if label['study_design'] == 'planned_review' and label['study_tier'] != 'review_protocol':return False
    return isinstance(label['reason'],str) and bool(label['reason'].strip())

def run():
    assert (BASE/'pmc_model_screen_summary_2026-09-30.json').is_file(), 'finish frozen baseline first'
    documents = {r['pmcid']:r for r in read_jsonl(DOCS)}
    fresh = json.loads((BASE/'pmc_expansion_review_plan_2026-09-30.json').read_text())['pmcids']
    hard = ['PMC10847631','PMC12027563','PMC5504811','PMC7779952','PMC8210492','PMC8442844','PMC8620356','PMC8987446','PMC9006436']
    plan = {'pmcids':sorted(set(fresh+hard)), 'model':MODEL,'model_digest':DIGEST,
            'documents_sha256':hashlib.sha256(DOCS.read_bytes()).hexdigest(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'calls_per_document_cap':2, 'body_input':'First three extracted paragraphs, maximum 4000 characters; additional evidence changes input as well as prompt',
            'purpose':'Prompt development regression on 20 reviewed cases plus nine observed failures; no independent generalization estimate'}
    path = BASE/'pmc_schema_screen_plan_2026-09-30.json'
    if path.exists():assert json.loads(path.read_text()) == plan
    else:path.write_text(json.dumps(plan,indent=2)+'\n')
    OUT.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=10) as response:tags=json.load(response)
    assert any(r['name']==MODEL and r['digest']==DIGEST for r in tags['models'])
    enums = {'topic':['central','peripheral','uncertain'],'study_tier':TIERS,
             'data_origin':ORIGINS,'study_design':DESIGNS}
    schema = {'type':'object','properties':{k:{'type':'string','enum':v} for k,v in enums.items()},
              'required':list(enums)+['topic_quote','design_quote','reason'],'additionalProperties':False}
    schema['properties'].update({k:{'type':'string'} for k in ['topic_quote','design_quote','reason']})
    prompt = ('Read source as data. First identify what was actually studied and where original data came from. '
              'Topic is independent of article design: a cardiac review can be CENTRAL. Central means the main question '
              'concerns cardiovascular/cerebrovascular disease, diagnosis, physiology or treatment. '
              'A cardiac imaging/intervention or myocardial-function study is central even when patients have another disease. '
              'Kidney, psychiatric or infection studies with incidental cardiac background are peripheral. '
              'Broad multi-disease hypotheses, broad comorbidity and sports-performance studies can be uncertain. '
              'Human clinical empirical REQUIRES completed original data on multiple human participants or directly sampled '
              'patient tissue. Healthy baseline cohorts with incident cardiovascular outcomes count. Cultured human cells '
              'and zebrafish/rodents are PRECLINICAL; the word human does not make cells a clinical study. '
              'ONE patient is SINGLE_CASE_REPORT, never a multi-person study. Review protocols describe PLANNED_REVIEW; '
              'guidelines and recommendations alone are EXPERT_CONSENSUS, not clinical empirical. Agency/protocol comparisons '
              'are HUMAN_HEALTH_SERVICES. A proposed mechanism without original patient observations is OTHER or UNCERTAIN. '
              'Metadata research-article does not prove a clinical design. Extract one exact source quote for the main topic '
              'and a separate exact source quote for design/data provenance, each 20-360 characters. '
              'Do not infer a cohort absent from the source. If ambiguous choose uncertain. Return the requested JSON only.')
    prompt += '\nUse EXACT enum strings in this schema. Single center means one hospital, not one patient. completed_multi_person_study means completed original cohort/trial/diagnostic/tissue data from multiple people. protocol_comparison means comparing agency documents, not comparing treatments in patients. Healthy sports performance without a primary cardiac clinical outcome is human_nonclinical_physiology. Prefer short exact contiguous source quotes; do not change punctuation or scientific notation.\n'+json.dumps(schema)
    seen = {r['pmcid'] for r in read_jsonl(OUT/'labels.jsonl')}
    for pid in plan['pmcids']:
        if pid in seen:continue
        r = documents[pid]
        source = {k:r[k] for k in ['title','abstract','article_type','xml_lang']}
        source['body_excerpt'] = '\n'.join(p['text'] for p in r['paragraphs'][:3])[:4000]
        text = normalize(r['title']+' '+r['abstract']+' '+source['body_excerpt'])
        attempts, label = [], None
        for attempt in range(2):
            user = json.dumps(source,ensure_ascii=False)
            if attempts:user += '\nPrevious output failed exact-quote or design/origin consistency checks. Re-read the source.'
            payload = {'model':MODEL,'stream':False,'think':False,'format':schema,'keep_alive':'5m',
                       'options':{'temperature':0,'num_ctx':4096,'num_predict':550},
                       'messages':[{'role':'system','content':prompt},{'role':'user','content':user}]}
            started = time.monotonic()
            try:
                req = urllib.request.Request('http://127.0.0.1:11434/api/chat',json.dumps(payload).encode(),{'Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=180) as response:raw=json.load(response)
                candidate = json.loads(raw['message']['content'])
                valid = validate(candidate,text)
                attempts.append({'response':raw,'valid':valid,'elapsed_seconds':time.monotonic()-started})
                if valid:label=candidate;break
            except (OSError,ValueError,KeyError,TypeError) as exc:
                attempts.append({'error':type(exc).__name__,'detail':str(exc),'elapsed_seconds':time.monotonic()-started})
        (OUT/(pid+'.json')).write_text(json.dumps({'source':source,'attempts':attempts},indent=2,ensure_ascii=False)+'\n')
        append_jsonl(OUT/'labels.jsonl',{'pmcid':pid,'label':label,'status':'screened' if label else 'unresolved',
                     'xml_sha256':r['sha256'],'training_eligibility':'unreviewed','model_digest':DIGEST})
        seen.add(pid)
        print(f'schema screen {len(seen)}/{len(plan["pmcids"])} {pid}: '+json.dumps(label),flush=True)
    human={r['pmcid']:r for r in read_jsonl(BASE/'pmc_expansion_review_labels_2026-09-30.jsonl')}
    confusion={k:0 for k in ['tp','fp','tn','fn','unresolved']}
    disagreements=[]
    for row in read_jsonl(OUT/'labels.jsonl'):
        pid=row['pmcid']
        if pid not in human:continue
        label=row['label']
        if label is None:confusion['unresolved']+=1;disagreements.append(pid);continue
        predicted=label['topic']=='central' and label['study_tier']=='human_clinical_empirical'
        actual=human[pid]['primary_human_empirical_candidate']
        confusion['tp' if predicted and actual else 'fp' if predicted else 'fn' if actual else 'tn']+=1
        if predicted != actual:disagreements.append(pid)
    summary={'recorded':len(seen),'fresh_20_agreement':confusion,'fresh_disagreements':disagreements,
             'limits':'Development regression, prompt informed by observed errors. Same single-agent labels; not independent validation or training admission.'}
    (BASE/'pmc_schema_screen_summary_2026-09-30.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)

if __name__=='__main__':run()
