"""Independently reproduce the frozen broad metadata queue; no admission."""
import hashlib,json
from collections import Counter
from pathlib import Path

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(stage):
    m=json.loads((stage/'manifest.json').read_text())
    assert digest('project-first-scan/PMC_BROAD_SCOPE_POLICY_2026-10-03.md')==m['policy_sha256']
    assert digest('project-first-scan/implementation/pmc_broad_scope_queue.py')==m['source_sha256']
    for p,key in [(m['holds'],'holds_sha256'),(m['old_candidates'],'old_candidates_sha256')]: assert digest(p)==m[key]
    held={json.loads(s)['pmcid'] for s in Path(m['holds']).read_text().splitlines()}; assert len(held)==129
    old={json.loads(s)['pmcid'] for s in Path(m['old_candidates']).read_text().splitlines()}
    expected={}; excluded=[]; reasons=Counter()
    for name,h in m['sources'].items():
        assert digest(name)==h
        for line in Path(name).read_text().splitlines():
            d=json.loads(line); assert d['pmcid'] not in expected and all(x['pmcid']!=d['pmcid'] for x in excluded)
            holds=[]
            if d['pmcid'] in held: holds.append('notice_link_hold')
            if d['article_type'] not in {'research-article','review-article','systematic-review','case-report','case-study'}: holds.append('publication_type_hold')
            if d['license_code'] not in {'CC BY','CC0'}: holds.append('license_hold')
            if d['xml_lang']!='en': holds.append('language_hold')
            if not d['doi'] or not d['pmid']: holds.append('identity_hold')
            if d['body_words']<1000: holds.append('short_body')
            if holds: excluded.append({'pmcid':d['pmcid'],'reasons':holds}); reasons.update(holds)
            else: expected[d['pmcid']]=d
    actual=[json.loads(s) for s in (stage/'candidates.jsonl').read_text().splitlines()]
    assert len(actual)==len({x['pmcid'] for x in actual})==len(expected)
    for row in actual:
        d=expected[row['pmcid']]
        for a,b in [('version','version'),('xml_sha256','sha256'),('doi','doi'),('pmid','pmid'),('title','title'),('article_type','article_type'),('body_words','body_words')]: assert row[a]==d[b]
        assert row['training_admission'] is False and row['scientific_evidence_group']==row['topical_role']=='requires_source_review'
        assert row['new_relative_to_strict_queue']==(row['pmcid'] not in old)
    assert old<=expected.keys() and len(expected)+len(excluded)==5819
    summary=json.loads((stage/'summary.json').read_text()); assert summary['candidates_sha256']==digest(stage/'candidates.jsonl')
    types=dict(Counter(d['article_type'] for d in expected.values())); assert types==summary['candidate_article_types'] and dict(reasons)==summary['overlapping_exclusion_counts']
    out={'status':'passed','source_objects':5819,'old_candidates':len(old),'broad_candidates':len(expected),'new_candidates':len(expected)-len(old),'held_objects':len(excluded),'notice_held_objects':len(held),'candidate_article_types':types,'overlapping_exclusion_counts':dict(reasons),'candidates_sha256':digest(stage/'candidates.jsonl'),'policy_sha256':m['policy_sha256'],'excluded_objects':sorted(excluded,key=lambda x:x['pmcid']),'training_admission':False,'limitations':'Independently reproduced metadata queue only. No scientific relevance, benchmark-overlap, duplicate, final extraction or training admission verdict.'}
    return out
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',type=Path);p.add_argument('output',type=Path);a=p.parse_args();assert not a.output.exists();a.output.write_text(json.dumps(audit(a.stage),indent=2)+'\n');print(a.output)
