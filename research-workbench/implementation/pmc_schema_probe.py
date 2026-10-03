"""One-article paired diagnosis of schema visibility/constrained output."""
import ast
import hashlib
import json
import urllib.request
from pathlib import Path
from pmc_evidence_screen import BASE, OUT, ORIGINS, DESIGNS, TIERS, normalize, validate
from experiment_proposer import MODEL, DIGEST

def run():
    assert (BASE/'pmc_evidence_screen_summary_2026-09-30.json').is_file()
    root=BASE/'data/pmc_schema_probe_20260930'
    root.mkdir(exist_ok=False)
    source=json.loads((OUT/'PMC10464339.json').read_text())['source']
    tree=ast.parse((BASE/'pmc_evidence_screen.py').read_text())
    prompt=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign)
                and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='prompt')
    enums={'topic':['central','peripheral','uncertain'],'study_tier':TIERS,
           'data_origin':ORIGINS,'study_design':DESIGNS}
    schema={'type':'object','properties':{k:{'type':'string','enum':v} for k,v in enums.items()},
            'required':list(enums)+['topic_quote','design_quote','reason'],'additionalProperties':False}
    schema['properties'].update({k:{'type':'string'} for k in ['topic_quote','design_quote','reason']})
    prompt+='\nUse EXACT enum strings in this schema. Single center means one hospital, not one patient. completed_multi_person_study means completed original cohort/trial/diagnostic/tissue data from multiple people. protocol_comparison means comparing agency documents, not comparing treatments in patients.\n'+json.dumps(schema)
    text=normalize(source['title']+' '+source['abstract']+' '+source['body_excerpt'])
    with urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=10) as response:tags=json.load(response)
    assert any(r['name']==MODEL and r['digest']==DIGEST for r in tags['models'])
    plan={'pmcid':'PMC10464339','model_digest':DIGEST,'calls':2,'retries':0,
          'arms':['explicit_schema_with_format','explicit_schema_without_format'],
          'source_sha256':hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest(),
          'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
          'purpose':'One-case implementation diagnosis, informed by observed failure; not classifier validation'}
    (root/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    rows=[]
    for constrained in [True,False]:
        payload={'model':MODEL,'stream':False,'think':False,'keep_alive':'5m',
                 'options':{'temperature':0,'num_ctx':4096,'num_predict':550},
                 'messages':[{'role':'system','content':prompt},{'role':'user','content':json.dumps(source,ensure_ascii=False)}]}
        if constrained:payload['format']=schema
        name='explicit_schema_with_format' if constrained else 'explicit_schema_without_format'
        (root/(name+'_request.json')).write_text(json.dumps(payload,indent=2)+'\n')
        try:
            request=urllib.request.Request('http://127.0.0.1:11434/api/chat',json.dumps(payload).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=180) as response:raw=json.load(response)
            (root/(name+'_response.json')).write_text(json.dumps(raw,indent=2)+'\n')
            candidate=json.loads(raw['message']['content'])
            rows.append({'arm':name,'label':candidate,'valid':validate(candidate,text)})
        except (OSError,ValueError,KeyError,TypeError) as exc:
            rows.append({'arm':name,'valid':False,'error':type(exc).__name__,'detail':str(exc)})
    summary={'plan':plan,'results':rows,'limits':'Single error-informed development case. Both prompts add explicit enums/design definitions; formatter effect comparison shares that prompt. No generalization estimate.'}
    (BASE/'pmc_schema_probe_2026-09-30.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':run()
