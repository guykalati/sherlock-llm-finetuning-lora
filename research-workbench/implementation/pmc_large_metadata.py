"""Resumable frozen metadata expansion; no article-text download or training admission."""
import hashlib,json,time
from pathlib import Path
from pmc_metadata_pilot import version_names,metadata,read_jsonl,append_jsonl

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    plan=json.loads(Path('plan.json').read_text())
    for name,digest in plan['files_sha256'].items():assert sha(Path(name))==digest
    output=Path('metadata.jsonl');fail=Path('failures.jsonl')
    done={r['pmcid'] for r in read_jsonl(output)+read_jsonl(fail)}
    assert done<=set(plan['pmcids'])
    began=time.monotonic()
    for pid in plan['pmcids']:
        if pid in done:continue
        if time.monotonic()-began>plan['max_seconds']-150:break
        if sum(p.stat().st_size for p in Path('.').glob('*.json*'))>plan['output_byte_cap']-1_000_000:break
        try:
            versions=[{'name':n,'metadata':metadata(n)} for n in version_names(pid)]
            row={'pmcid':pid,'versions':versions,'fetched_at_unix':time.time(),'training_eligibility':'unreviewed'}
            append_jsonl(output,row)
        except Exception as e:
            append_jsonl(fail,{'pmcid':pid,'error_type':type(e).__name__,'detail':str(e),'training_eligibility':'unreviewed'})
        done.add(pid)
        if len(done)%25==0:print(f'{len(done)}/{len(plan["pmcids"])} recorded',flush=True)
        time.sleep(.15)
    data=read_jsonl(output);bad=read_jsonl(fail)
    summary={'planned':len(plan['pmcids']),'recorded':len(data),'failed':len(bad),'remaining':len(plan['pmcids'])-len(done),'metadata_bytes':output.stat().st_size if output.exists() else 0,'no_fulltext_download':True,'no_training_admission':True,'elapsed_seconds':time.monotonic()-began,'plan_sha256':sha(Path('plan.json'))}
    Path('summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
if __name__=='__main__':run()
