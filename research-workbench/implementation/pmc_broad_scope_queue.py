"""Rebuild broad publication-type review queue; never admit text for training."""
import hashlib,json,time
from collections import Counter
from pathlib import Path
TYPES={'research-article','review-article','systematic-review','case-report','case-study'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flags(doc,holds):
    return [k for k,v in {'notice_link_hold':doc['pmcid'] in holds,'publication_type_hold':doc['article_type'] not in TYPES,'license_hold':doc['license_code'] not in ['CC BY','CC0'],'language_hold':doc['xml_lang']!='en','identity_hold':not doc['doi'] or not doc['pmid'],'short_body':doc['body_words']<1000}.items() if v]
def run(stage):
    started=time.monotonic();m=json.loads((stage/'manifest.json').read_text());assert sha(Path(__file__))==m['source_sha256'];holds_path=Path(m['holds']);assert sha(holds_path)==m['holds_sha256'];holds={json.loads(x)['pmcid'] for x in holds_path.read_text().splitlines()};assert len(holds)==129
    old_path=Path(m['old_candidates']);assert sha(old_path)==m['old_candidates_sha256'];old={json.loads(x)['pmcid'] for x in old_path.read_text().splitlines()};seen=set();counts=Counter();exclusions=Counter();rows=[]
    for name,h in m['sources'].items():
        p=Path(name);assert sha(p)==h
        with p.open() as f:
            for line in f:
                assert time.monotonic()-started<300
                doc=json.loads(line);assert doc['pmcid'] not in seen;seen.add(doc['pmcid']);reasons=flags(doc,holds)
                if reasons:exclusions.update(reasons);continue
                counts[doc['article_type']]+=1
                rows.append({'pmcid':doc['pmcid'],'version':doc['version'],'xml_sha256':doc['sha256'],'doi':doc['doi'],'pmid':doc['pmid'],'title':doc['title'],'article_type':doc['article_type'],'body_words':doc['body_words'],'source_document_file':name,'new_relative_to_strict_queue':doc['pmcid'] not in old,'scientific_evidence_group':'requires_source_review','topical_role':'requires_source_review','training_admission':False})
    assert len(seen)==5819 and old<={x['pmcid'] for x in rows};rows.sort(key=lambda x:x['pmcid']);output=stage/'candidates.jsonl';assert not output.exists();output.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows));assert output.stat().st_size<10_000_000
    summary={'status':'prepared_review_queue','documents':len(seen),'old_candidates':len(old),'broad_candidates':len(rows),'new_candidates':len(rows)-len(old),'candidate_article_types':dict(counts),'overlapping_exclusion_counts':dict(exclusions),'source_sha256':m['source_sha256'],'manifest_sha256':sha(stage/'manifest.json'),'candidates_sha256':sha(output),'elapsed_seconds':time.monotonic()-started,'training_admission':False,'limits':'Broader metadata/type and source-quality triage only. Clinical/review/preclinical scientific groups and topic relevance require source-level review; not admitted training text.'};assert not (stage/'summary.json').exists();(stage/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
def selfcheck():
    d={'pmcid':'PMC1','article_type':'review-article','license_code':'CC BY','xml_lang':'en','doi':'d','pmid':1,'body_words':1000};assert flags(d,set())==[];assert flags(d,{'PMC1'})==['notice_link_hold'];assert 'publication_type_hold' in flags({**d,'article_type':'correction'},set())
if __name__=='__main__':
    import argparse
    selfcheck();p=argparse.ArgumentParser();p.add_argument('stage',type=Path);a=p.parse_args();run(a.stage)
