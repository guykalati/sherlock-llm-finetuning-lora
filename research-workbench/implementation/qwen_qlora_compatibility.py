"""Three optimizer steps on a nonmedical fixture; validates QLoRA runtime only."""
import hashlib,json,time
from pathlib import Path
import torch,transformers,peft,bitsandbytes
from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
from peft import LoraConfig,get_peft_model,prepare_model_for_kbit_training,PeftModel
S=Path('/home/guykalat/.cache/huggingface/hub/models--Qwen--Qwen2.5-3B-Instruct/snapshots/aa8e72537993ba99e69dfaafa59ed015b17504d1')
TEXT='This is a software compatibility fixture. The blue box contains three wooden blocks. The green box contains two wooden blocks. Count the objects separately. This text is not medical data and is not an evaluation benchmark.'
def run():
    begin=time.monotonic();manifest=json.loads(Path('manifest.json').read_text())
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==manifest['source_sha256']
    assert torch.cuda.is_available() and not Path('result.json').exists()
    torch.manual_seed(20261001)
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    tok=AutoTokenizer.from_pretrained(S,local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(S,local_files_only=True,trust_remote_code=False,quantization_config=quant,device_map={'':0},torch_dtype=torch.bfloat16,attn_implementation='sdpa')
    model.config.use_cache=False
    model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True)
    model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=0,target_modules=['q_proj','k_proj','v_proj','o_proj'],bias='none',task_type='CAUSAL_LM'))
    inputs=tok(TEXT,return_tensors='pt').to('cuda');assert inputs['input_ids'].shape[1]<=128
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4)
    torch.cuda.reset_peak_memory_stats();losses=[];gradient_norms=[]
    model.train()
    for step in range(3):
        optimizer.zero_grad(set_to_none=True);loss=model(**inputs,labels=inputs['input_ids']).loss
        assert torch.isfinite(loss);loss.backward()
        norms=[p.grad.float().norm() for p in model.parameters() if p.requires_grad and p.grad is not None]
        total=torch.stack(norms).norm();assert torch.isfinite(total) and total.item()>0
        gradient_norms.append(total.item());optimizer.step();losses.append(loss.item())
    model.save_pretrained('adapter')
    model.eval()
    with torch.inference_mode():before=model(**inputs).logits.float().cpu()
    # Reload the persisted adapter into a fresh wrapper on the same unchanged base.
    base=model.unload();reloaded=PeftModel.from_pretrained(base,'adapter').eval()
    with torch.inference_mode():after=reloaded(**inputs).logits.float().cpu()
    difference=(before-after).abs().max().item();assert torch.allclose(before,after,rtol=1e-4,atol=1e-4)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('adapter').iterdir() if p.is_file()}
    result={'status':'completed','model_snapshot':S.name,'optimizer_steps':3,'tokens':inputs['input_ids'].shape[1],'fixture_sha256':hashlib.sha256(TEXT.encode()).hexdigest(),'losses':losses,'gradient_norms':gradient_norms,'adapter_reload_max_logit_difference':difference,'adapter_files_sha256':hashes,'gpu_peak_bytes':torch.cuda.max_memory_allocated(),'elapsed_seconds':time.monotonic()-begin,'versions':{'torch':torch.__version__,'transformers':transformers.__version__,'peft':peft.__version__,'bitsandbytes':bitsandbytes.__version__},'limits':'Nonmedical execution fixture; verifies4-bit LoRA backward/optimizer/save/reload only. No QA score, corpus training, benchmark or full baseline reproduction.'}
    Path('result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':run()
