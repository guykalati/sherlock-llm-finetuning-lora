"""Portable Qwen QLoRA CPT comparison followed by response-only SFT."""
import argparse, gc, hashlib, json, math, random, re, time, unicodedata
from pathlib import Path
import torch, numpy as np, transformers, peft, bitsandbytes
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from legacy_scoring import score_prediction

SEED=3407; LENGTH=512; STEPS=200; ACCUM=4
ATTN=['q_proj','k_proj','v_proj','o_proj']; MLP=['gate_proj','up_proj','down_proj']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def seed():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
def base(a):
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    m=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,trust_remote_code=False,quantization_config=q,device_map={'':0},torch_dtype=torch.bfloat16,attn_implementation='sdpa')
    m.config.use_cache=False
    return prepare_model_for_kbit_training(m,use_gradient_checkpointing=True)
def corpus(a,tok):
    train=[]; val=[]; counts={}
    for p in sorted((a.data/'books').glob('pg*.txt')):
        text=unicodedata.normalize('NFKC',p.read_text(encoding='utf-8-sig'))
        text=re.split(r'\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*',text,flags=re.I)[-1]
        text=re.split(r'\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK',text,flags=re.I)[0]
        ids=tok(text,add_special_tokens=False)['input_ids']; blocks=[ids[i:i+LENGTH] for i in range(0,len(ids)-LENGTH+1,LENGTH)]
        cut=int(len(blocks)*.9); train+=blocks[:cut]; val+=blocks[cut+1:]; counts[p.name]={'tokens':len(ids),'train_chunks':cut,'guard_chunks':1,'validation_chunks':len(blocks)-cut-1}
    assert len(counts)==9 and len(val)>=24
    # Frozen evenly spaced validation chunks; all training chunks retained.
    val=[val[i] for i in np.linspace(0,len(val)-1,24,dtype=int)]
    return train,val,counts
def sft_encode(tok,r):
    messages=r['messages']; assert messages[-1]['role']=='assistant'
    prefix=tok.apply_chat_template(messages[:-1],tokenize=True,add_generation_prompt=True)
    full=tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=False)
    assert full[:len(prefix)]==prefix, 'Chat prefix changed; mask must be verified'
    # Keep complete answer up to 512 tokens; reject wholly truncated targets.
    ids=full[:LENGTH]; labels=[-100]*min(len(prefix),len(ids))+ids[len(prefix):]
    assert len(ids)==len(labels) and any(x!=-100 for x in labels)
    return ids,labels
def loss(m,item):
    ids,labels=item; x=torch.tensor([ids],device='cuda'); y=torch.tensor([labels],device='cuda')
    return m(input_ids=x,labels=y).loss
def evaluate(m,data):
    m.eval(); total=0.; tokens=0
    with torch.inference_mode():
        for ids,labels in data:
            n=sum(x!=-100 for x in labels[1:]); total+=loss(m,(ids,labels)).item()*n; tokens+=n
    assert tokens>0
    return {'loss':total/tokens,'perplexity':math.exp(total/tokens),'target_tokens':tokens}
def train(m,data,validation,out,steps,lr):
    seed(); optimizer=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=lr,weight_decay=0)
    order=list(range(len(data))); rng=random.Random(SEED); rng.shuffle(order); pos=0; history=[]; start=time.monotonic()
    initial=evaluate(m,validation)
    for step in range(1,steps+1):
        m.train(); optimizer.zero_grad(set_to_none=True); total=0.
        for _ in range(ACCUM):
            if pos==len(order): rng.shuffle(order); pos=0
            l=loss(m,data[order[pos]]); pos+=1; assert torch.isfinite(l); total+=l.item(); (l/ACCUM).backward()
        torch.nn.utils.clip_grad_norm_([p for p in m.parameters() if p.requires_grad],.3)
        ratio=min(step/(steps*.03),1.)*.5*(1+math.cos(math.pi*step/steps))
        for g in optimizer.param_groups:g['lr']=lr*ratio
        optimizer.step()
        if step%25==0 or step==steps:
            row={'step':step,'train_loss':total/ACCUM,'validation':evaluate(m,validation),'seconds':time.monotonic()-start}
            history.append(row); print(json.dumps({'stage':out.name,**row}),flush=True)
            (out/'history.json').write_text(json.dumps({'initial':initial,'history':history},indent=2))
    m.save_pretrained(out/'adapter'); tok_files={p.name:sha(p) for p in (out/'adapter').iterdir() if p.is_file()}
    return {'initial':initial,'final':history[-1]['validation'],'history':history,'steps':steps,'microbatches_per_step':ACCUM,'adapter_sha256':tok_files,'seconds':time.monotonic()-start}
def qa(m,tok,a,stage):
    m.eval(); m.config.use_cache=True; predictions=[]; tests=rows(a.data/'test_messages.jsonl'); refs=rows(a.data/'test_answers.jsonl')
    for i,(r,ref) in enumerate(zip(tests,refs)):
        assert r['messages'][-2]['content']==ref['question']
        prompt=tok.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True)
        inputs=tok(prompt,return_tensors='pt').to('cuda'); started=time.monotonic()
        with torch.inference_mode(): generated=m.generate(**inputs,max_new_tokens=128,do_sample=False,pad_token_id=tok.eos_token_id)
        answer=tok.decode(generated[0,inputs['input_ids'].shape[1]:],skip_special_tokens=True).strip()
        scores=score_prediction(answer,ref.get('aliases') or [ref['answer']])
        row={'id':ref['id'],'stage':stage,'question':ref['question'],'reference':ref['answer'],'prediction':answer,'category':ref.get('category'),**scores,'seconds':time.monotonic()-started}
        predictions.append(row)
        with (a.output/'qa_predictions.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    m.config.use_cache=False
    return {'n':len(predictions),'exact_match':sum(p['accuracy'] for p in predictions)/len(predictions),'token_f1':sum(p['f1'] for p in predictions)/len(predictions)}
def run(a):
    assert torch.cuda.is_available(); assert not a.output.exists(); a.output.mkdir(parents=True)
    torch.set_num_threads(2);seed(); started=time.monotonic()
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,trust_remote_code=False)
    tr,vl,counts=corpus(a,tok); cpt_tr=[(x,x) for x in tr];cpt_vl=[(x,x) for x in vl]
    sets={k:rows(a.data/(k+'_messages.jsonl')) for k in ['train','validation','test']}
    questions={k:{r['messages'][-2]['content'].strip().casefold() for r in rs} for k,rs in sets.items()}
    assert not questions['train'] & questions['test'] and not questions['validation'] & questions['test']
    data_manifest={'files':{str(p.relative_to(a.data)):sha(p) for p in a.data.rglob('*') if p.is_file()},'books':counts,'sft_counts':{k:len(v) for k,v in sets.items()},'cpt_validation_chunks':len(vl)}
    (a.output/'data_manifest.json').write_text(json.dumps(data_manifest,indent=2))
    result={'model_snapshot':a.model.name,'source_sha256':sha(__file__),'seed':SEED,'length':LENGTH,'cpt':{},'qa':{},'versions':{k:v.__version__ for k,v in [('torch',torch),('transformers',transformers),('peft',peft),('bitsandbytes',bitsandbytes)]}}
    for name,targets in [('attention',ATTN),('attention_mlp',ATTN+MLP)]:
        seed(); m=get_peft_model(base(a),LoraConfig(r=16,lora_alpha=32,lora_dropout=.05,target_modules=targets,bias='none',task_type='CAUSAL_LM'))
        out=a.output/name;out.mkdir();result['cpt'][name]=train(m,cpt_tr,cpt_vl,out,STEPS,2e-4)
        if name=='attention_mlp': result['qa']['cpt']=qa(m,tok,a,'cpt')
        del m;gc.collect();torch.cuda.empty_cache()
    seed();m=PeftModel.from_pretrained(base(a),a.output/'attention_mlp'/'adapter',is_trainable=True)
    sft_tr=[sft_encode(tok,r) for r in sets['train']];sft_vl=[sft_encode(tok,r) for r in sets['validation']]
    out=a.output/'sft';out.mkdir();result['sft']=train(m,sft_tr,sft_vl,out,math.ceil(len(sft_tr)*3/ACCUM),1e-4)
    result['qa']['sft']=qa(m,tok,a,'sft')
    result['sft_initial_adapter_sha256']=result['cpt']['attention_mlp']['adapter_sha256']
    result['seconds']=time.monotonic()-started;result['gpu']=torch.cuda.get_device_name();result['peak_bytes']=torch.cuda.max_memory_allocated();result['status']='completed'
    result['limitations']='One fixed seed; contiguous within-book validation spans; Qwen may have pretraining exposure to public-domain books. SFT references are course/synthetic data; question-disjoint within the same canon, not unseen-domain or human gold. No claim of improved QA from CPT unless measured.'
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--data',type=Path,default=Path('data'));p.add_argument('--output',type=Path,default=Path('output'));run(p.parse_args())
