"""Independently verify persisted corpus integrity, extraction, and sampled overlap scores."""
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from pmc_metadata_pilot import read_jsonl

BASE = Path(__file__).resolve().parent
OUT = BASE / 'data/pmc_xml_expansion_20260929'

def fivegrams(text):
    words = re.findall(r'\w+', text.casefold())
    return {tuple(words[i:i+5]) for i in range(len(words)-4)}

def run():
    contract = json.loads((OUT/'contract.json').read_text())
    checks = read_jsonl(OUT/'checks.jsonl')
    failures = read_jsonl(OUT/'failures.jsonl')
    docs = read_jsonl(OUT/'documents.jsonl')
    screens = read_jsonl(OUT/'screens.jsonl')
    by_id = {r['pmcid']:r for r in docs}
    screening = {r['pmcid']:r for r in screens}
    planned = {r['pmcid']:r for r in contract['plan']}
    successful = {r['pmcid'] for r in checks}
    failed = {r['pmcid'] for r in failures}
    assert len(successful)==len(checks) and len(failed)==len(failures)
    assert not successful & failed and successful | failed == set(planned)
    assert set(screening)==successful and len(screening)==len(screens)
    word_ratios = []
    for row in checks:
        data = (OUT/'xml'/(row['version']+'.xml')).read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256']
        assert hashlib.md5(data).hexdigest()==planned[row['pmcid']]['md5']
        assert len(data)==row['bytes']
        if row.get('jats_article'):
            assert row['pmcid'] in by_id
            root=ET.fromstring(data)
            abstract=root.find('./front/article-meta/abstract')
            assert by_id[row['pmcid']]['abstract']==(' '.join(abstract.itertext()).strip() if abstract is not None else '')
            paragraphs=by_id[row['pmcid']]['paragraphs']
            # Count exact preserved body paragraphs, accounting for tables/figures consumed as one unit.
            def count(node):
                if node.tag in ('p','table-wrap','fig'):return 1
                return sum(count(c) for c in node)
            body=root.find('body')
            assert len(paragraphs)==(count(body) if body is not None else 0)
            if row.get('body_words',0):
                word_ratios.append((sum(len(p['text'].split()) for p in paragraphs)/row['body_words'],row['pmcid']))
    assert sum(r['bytes'] for r in checks) <= contract['byte_cap']
    doi_counts=Counter((r.get('doi') or '').strip().casefold() for r in docs if r.get('doi'))
    text_counts=Counter(' '.join(re.findall(r'\w+', ' '.join(p['text'] for p in r['paragraphs']).casefold()))
                        for r in docs if r['paragraphs'])
    assert sum(bool(r.get('duplicate_doi_of')) for r in screens)==sum(n-1 for n in doi_counts.values())
    assert sum(bool(r.get('duplicate_body_of')) for r in screens)==sum(n-1 for n in text_counts.values())
    reference = {str(pmid):fivegrams(' '.join(row['CONTEXTS'])) for pmid,row in
                 json.loads((BASE/'data/pubmedqa_exclusion_2026-09-29/ori_pqal.json').read_text()).items()}
    selected=random.Random(20260930).sample(sorted(by_id),min(20,len(by_id)))
    selected=sorted(set(selected) | {pid for pid,row in screening.items() if row.get('benchmark_context_matches')})
    for pid in selected:
        doc=by_id[pid]
        values=fivegrams(doc['abstract']+' '+' '.join(p['text'] for p in doc['paragraphs']))
        expected={}
        for pmid,ref in reference.items():
            shared=len(values & ref)
            if shared>=30:
                j=shared/len(values | ref);c=shared/len(ref)
                if j>=.8 or c>=.9:expected[pmid]=(shared,j,c)
        actual={r['pmid']:(r['shared'],r['jaccard'],r['containment']) for r in screening[pid]['benchmark_context_matches']}
        assert actual==expected,(pid,actual,expected)
    result={'planned':len(planned),'verified_xml':len(checks),'excluded_source_failures':len(failures),
            'integrity_and_extraction_passed':True,'naive_overlap_rescore_documents':len(selected),
            'overlap_rescore_passed':True,'extracted_body_words':sum(len(p['text'].split()) for r in docs for p in r['paragraphs']),
            'extraction_to_xml_word_ratio_below_80_percent':sum(v<.8 for v,_ in word_ratios),
            'lowest_extraction_ratios':sorted(word_ratios)[:10],
            'structural_flags':dict(Counter(f for r in screens for f in r.get('structural_review_flags',[]))),
            'note':'Word coverage counts omit section headings and some non-paragraph body elements; these are not model tokenizer counts.'}
    (BASE/'pmc_expansion_qa_2026-09-30.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    run()
