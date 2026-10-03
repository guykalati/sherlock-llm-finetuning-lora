"""Frozen source-checked article acquisition; extracted outputs remain unreviewed."""
import hashlib,json,time
from pathlib import Path
from pmc_metadata_pilot import read_jsonl,append_jsonl
from pmc_xml_pilot import download,inspect_xml
from pmc_xml_expansion import extract

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    plan=json.loads(Path('plan.json').read_text())
    for name,digest in plan['files_sha256'].items():assert sha(Path(name))==digest
    Path('xml').mkdir(exist_ok=True)
    checks=Path('checks.jsonl');fail=Path('failures.jsonl');docs=Path('documents.jsonl')
    done={r['pmcid'] for r in read_jsonl(checks)+read_jsonl(fail)}
    assert done<={r['pmcid'] for r in plan['articles']}
    began=time.monotonic();reason='all_attempted'
    for item in plan['articles']:
        if item['pmcid'] in done:continue
        if time.monotonic()-began>plan['max_seconds']-150:reason='time_cap';break
        used=sum(p.stat().st_size for p in Path('xml').glob('*.xml'))
        if used>plan['xml_byte_cap']-10_000_000 or (docs.exists() and docs.stat().st_size>plan['extracted_byte_cap']-10_000_000):reason='byte_cap';break
        target=Path('xml')/(item['version']+'.xml')
        try:
            size,digest=download(item['url'],target,item['md5'],used,plan['xml_byte_cap'])
            info=inspect_xml(target)
            row=item|{'bytes':size,'verified_md5':digest,'sha256':sha(target),**info,'training_eligibility':'unreviewed'}
            if not info.get('jats_article'):raise ValueError('Not usable JATS article; retain failed source for inspection')
            body=extract(target)
            document=row|body
            encoded=json.dumps(document,ensure_ascii=False)+'\n'
            if (docs.stat().st_size if docs.exists() else 0)+len(encoded.encode())>plan['extracted_byte_cap']:reason='extracted_byte_cap';break
            # Record both only after all source/extraction gates pass.
            append_jsonl(docs,document);append_jsonl(checks,row)
        except Exception as e:
            append_jsonl(fail,item|{'error_type':type(e).__name__,'detail':str(e),'training_eligibility':'unreviewed'})
        done.add(item['pmcid'])
        if len(done)%25==0:print(f'{len(done)}/{len(plan["articles"])} attempted',flush=True)
        time.sleep(.15)
    summary={'planned':len(plan['articles']),'downloaded_and_extracted':len(read_jsonl(checks)),'failed':len(read_jsonl(fail)),'remaining':len(plan['articles'])-len(done),'stop_reason':reason,'xml_bytes':sum(p.stat().st_size for p in Path('xml').glob('*.xml')),'document_bytes':docs.stat().st_size if docs.exists() else 0,'elapsed_seconds':time.monotonic()-began,'plan_sha256':sha(Path('plan.json')),'training_admission':False,'limits':'Language/topic/design/full-body quality, retraction XML flags, deduplication and benchmark context overlap still require audit before any admission.'}
    Path('summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
if __name__=='__main__':run()
