"""48-call cached local-model feasibility check with schema-constrained output."""
import ast,hashlib,json,time,urllib.request
from pathlib import Path
from scope_output_gate import validate,TIERS,CENTRALITY
MODEL='gemma4:12b-it-qat'
DIGEST='38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3'
SCHEMA={'type':'object','properties':{'study_tier':{'type':'string','enum':sorted(TIERS)},'cardiac_centrality':{'type':'string','enum':sorted(CENTRALITY)},'population_quote':{'type':'string'},'question_quote':{'type':'string'},'reason':{'type':'string'}},'required':['study_tier','cardiac_centrality','population_quote','question_quote','reason'],'additionalProperties':False}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(path):
    with urllib.request.urlopen('http://127.0.0.1:11434'+path,timeout=10) as r:return json.load(r)
def original_prompt(path):
    tree=ast.parse(path.read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROMPT' for t in n.targets));return ast.literal_eval(node.value)
def run():
    started=time.monotonic();m=json.loads(Path('manifest.json').read_text());assert all(sha(Path(n))==v for n,v in m['input_sha256'].items())
    tags=get('/api/tags');model=next(x for x in tags['models'] if x['name']==MODEL);assert model['digest']==DIGEST and not model.get('remote_host')
    version=get('/api/version');assert not Path('rows.jsonl').exists() and not Path('result.json').exists()
    cases=[json.loads(x) for x in Path('cases.jsonl').read_text().splitlines()];assert len(cases)==48 and len({x['pmcid'] for x in cases})==48
    prompt=original_prompt(Path('qwen_scope_check.py'));rows=[];status='complete'
    for case in cases:
        if time.monotonic()-started>=1500:status='wall_limit_partial';break
        context=case['source_context'];assert hashlib.sha256(context.encode()).hexdigest()==case['context_sha256']
        request={'model':MODEL,'stream':False,'think':False,'format':SCHEMA,'keep_alive':'5m',
            'options':{'temperature':0,'seed':20261003,'num_ctx':8192,'num_predict':512},
            'messages':[{'role':'system','content':prompt},{'role':'user','content':context}]}
        row={'pmcid':case['pmcid'],'split':case['split'],'xml_sha256':case['xml_sha256'],'context_sha256':case['context_sha256'],
             'request_sha256':hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest(),'training_admission':False}
        begin=time.monotonic()
        try:
            req=urllib.request.Request('http://127.0.0.1:11434/api/chat',json.dumps(request).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=min(120,max(1,1500-(time.monotonic()-started)))) as response:value=json.load(response)
            raw=value.get('message',{}).get('content','');row.update({'raw':raw,'response':value,'strict':validate(raw,context),'transport_gate':validate(raw,context,allow_fence=True),
                'prompt_eval_count':value.get('prompt_eval_count'),'eval_count':value.get('eval_count'),'done_reason':value.get('done_reason')})
            assert value.get('done') is True
            assert value.get('eval_count',0)<=512 and 0<value.get('prompt_eval_count',0)<=8192
        except Exception as error:
            row['request_failure']=type(error).__name__+': '+str(error)
            # A timed-out local request may still run server-side. Stop, never stack another request.
            status='request_failure_partial'
        row['elapsed_seconds']=time.monotonic()-begin;rows.append(row)
        with Path('rows.jsonl').open('a') as out:out.write(json.dumps(row,ensure_ascii=False)+'\n')
        print(json.dumps({'done_cases':len(rows),'pmcid':row['pmcid'],'gate_failure':row.get('transport_gate',{}).get('failure'),'request_failure':row.get('request_failure')}),flush=True)
        if status!='complete':break
    if len(rows)!=48 and status=='complete':status='partial'
    Path('result.json').write_text(json.dumps({'status':status,'rows':rows,'manifest_sha256':sha(Path('manifest.json')),'source_sha256':sha(Path(__file__)),
      'model':MODEL,'model_digest':DIGEST,'ollama_version':version,'elapsed_seconds':time.monotonic()-started,
      'training_admission':False,'limits':'48 local development calls, no retries/training/downloads. Same context and baseline instructions; different model/tokenizer/runtime and schema-guided decoder, not isolated model-size causality or expert accuracy.'},indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':run()
