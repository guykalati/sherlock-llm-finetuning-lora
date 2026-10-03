"""Recompute provenance, extraction, identity and basic quality of a completed XML batch."""
import argparse,hashlib,json,re,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from pmc_metadata_pilot import read_jsonl
from pmc_xml_pilot import inspect_xml
from pmc_xml_expansion import extract,normalized

def audit(root):
    plan=json.loads((root/'plan.json').read_text());summary=json.loads((root/'summary.json').read_text())
    for name,digest in plan['files_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
    assert summary['plan_sha256']==hashlib.sha256((root/'plan.json').read_bytes()).hexdigest()
    expected={r['pmcid']:r for r in plan['articles']}
    checks=read_jsonl(root/'checks.jsonl');failures=read_jsonl(root/'failures.jsonl');docs=read_jsonl(root/'documents.jsonl')
    assert len({r['pmcid'] for r in checks})==len(checks)
    assert len({r['pmcid'] for r in docs})==len(docs)
    assert {r['pmcid'] for r in checks}=={r['pmcid'] for r in docs}
    assert not ({r['pmcid'] for r in checks}&{r['pmcid'] for r in failures})
    assert {r['pmcid'] for r in checks+failures}<=expected.keys()
    assert summary['downloaded_and_extracted']==len(checks) and summary['failed']==len(failures)
    by_id={r['pmcid']:r for r in docs};flags=[];digests=Counter();languages=Counter();types=Counter()
    for r in checks:
        item=expected[r['pmcid']]
        assert all(r[k]==v for k,v in item.items()) and r['training_eligibility']=='unreviewed'
        p=root/'xml'/(r['version']+'.xml');raw=p.read_bytes()
        assert len(raw)==r['bytes'] and hashlib.md5(raw).hexdigest()==r['md5']==r['verified_md5']
        assert hashlib.sha256(raw).hexdigest()==r['sha256']
        info=inspect_xml(p);assert all(r[k]==v for k,v in info.items())
        text=extract(p);doc=by_id[r['pmcid']];assert all(doc[k]==v for k,v in (r|text).items())
        xml=ET.fromstring(raw);meta=xml.find('./front/article-meta')
        ids={n.attrib.get('pub-id-type'):''.join(n.itertext()).strip() for n in meta.findall('article-id')}
        issues=[]
        if ids.get('pmid')!=str(r['pmid']):issues.append('pmid_mismatch_or_missing')
        if ids.get('doi','').lower()!=r['doi'].lower():issues.append('doi_mismatch_or_missing')
        pmc=ids.get('pmc',ids.get('pmcid',''));pmc='PMC'+pmc.removeprefix('PMC')
        if pmc!=r['pmcid']:issues.append('pmcid_mismatch_or_missing')
        if r.get('xml_lang')!='en':issues.append('not_explicit_english')
        if r.get('body_words',0)<500:issues.append('short_body')
        if 'retract' in str(r.get('article_type','')).lower():issues.append('retraction_document')
        flags.append({'pmcid':r['pmcid'],'flags':issues,'training_eligibility':'unreviewed'})
        digests[hashlib.sha256(normalized(' '.join(x['text'] for x in text['paragraphs'])).encode()).hexdigest()]+=1
        languages[r.get('xml_lang')]+=1;types[r.get('article_type')]+=1
    assert summary['xml_bytes']==sum(p.stat().st_size for p in (root/'xml').glob('*.xml'))
    return {'status':'passed','planned':len(expected),'verified':len(checks),'failed':len(failures),'remaining':len(expected)-len(checks)-len(failures),'languages':dict(languages),'article_types':dict(types),'quality_identity_flags':flags,'exact_duplicate_body_groups':sum(v>1 for v in digests.values()),'training_admission':False,'limits':'Basic source/extraction/identity checks only; flags require review. Topic/study scope, XML publication notices, cross-batch duplication and benchmark-context overlap remain pending.'}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    result=audit(args.directory);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='quality_identity_flags'}))
