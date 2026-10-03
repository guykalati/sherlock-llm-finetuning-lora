"""Frozen benchmark, exact-family and development-reservation checks; no admission."""
import hashlib,json,time
from collections import Counter,defaultdict
from pathlib import Path
from pmc_overlap_audit import sha,norm,shingles,matches

def run(stage):
    started=time.monotonic();m=json.loads((stage/'manifest.json').read_text())
    assert sha(Path(__file__))==m['source_sha256']
    for name,h in m['inputs_sha256'].items():assert sha(Path(name))==h
    for name,h in m['sources'].items():assert sha(Path(name))==h
    benchmark=json.loads(Path(m['benchmark']).read_text());assert len(benchmark)==1000
    # Contexts only; questions and answer labels are not inspected or emitted.
    refs={str(pid):shingles(' '.join(r['CONTEXTS'])) for pid,r in benchmark.items()}
    index=defaultdict(list)
    for pid,values in refs.items():
        for value in values:index[value].append(pid)
    selected=json.loads(Path(m['development_selection']).read_text());qa=json.loads(Path(m['qa_exclusions']).read_text())
    reserved=set(selected['excluded_prior_development_ids'])|{x['pmcid'] for x in selected['selected']}|set(qa['pmcids'])
    all_docs={};doi_families=defaultdict(list);body_families=defaultdict(list);pmid_families=defaultdict(list);body_hash={}
    for name in m['sources']:
        for line in Path(name).read_text().splitlines():
            d=json.loads(line);assert d['pmcid'] not in all_docs;all_docs[d['pmcid']]=d
            body=' '.join(p['text'] for p in d['paragraphs']);key=hashlib.sha256(norm(body).encode()).hexdigest();body_hash[d['pmcid']]=key
            if body:body_families[key].append(d['pmcid'])
            if d['doi']:doi_families[d['doi'].strip().casefold()].append(d['pmcid'])
            if d['pmid']:pmid_families[str(d['pmid'])].append(d['pmcid'])
    assert len(all_docs)==5819
    reserved_doi={all_docs[p]['doi'].strip().casefold() for p in reserved&all_docs.keys() if all_docs[p]['doi']}|{d.strip().casefold() for d in qa['dois']}
    reserved_pmid={str(all_docs[p]['pmid']) for p in reserved&all_docs.keys() if all_docs[p]['pmid']}|{str(p) for p in qa['pmids']}
    reserved_body={body_hash[p] for p in reserved&all_docs.keys()}
    candidates=[json.loads(s) for s in Path(m['candidates']).read_text().splitlines()];out=stage/'screens.jsonl';assert not out.exists();records=[];flags=Counter()
    for i,row in enumerate(candidates):
        assert time.monotonic()-started<m['max_local_seconds']
        d=all_docs[row['pmcid']];assert d['sha256']==row['xml_sha256'];body=' '.join(p['text'] for p in d['paragraphs']);values=shingles(d['abstract']+' '+body)
        counts=Counter(pid for value in values for pid in index.get(value,()))
        found=matches(values,refs,counts)
        if i<10:assert found==matches(values,refs,{pid:len(values&v) for pid,v in refs.items()})
        dk=d['doi'].strip().casefold();pk=str(d['pmid']);bk=body_hash[d['pmcid']]
        dupdoi=[p for p in doi_families[dk] if p!=d['pmcid']];duppmid=[p for p in pmid_families[pk] if p!=d['pmcid']];dupbody=[p for p in body_families[bk] if p!=d['pmcid']]
        holds=[]
        if pk in refs:holds.append('benchmark_pmid')
        if found:holds.append('benchmark_context_overlap')
        if d['pmcid'] in reserved or dk in reserved_doi or pk in reserved_pmid or bk in reserved_body:holds.append('development_family_reserved')
        if dupdoi or duppmid or dupbody:holds.append('exact_family_review')
        flags.update(holds);records.append({'pmcid':d['pmcid'],'version':d['version'],'xml_sha256':d['sha256'],'normalized_cached_body_sha256':bk,'benchmark_context_matches':found,'same_doi_other_pmcids':sorted(dupdoi),'same_pmid_other_pmcids':sorted(duppmid),'same_body_other_pmcids':sorted(dupbody),'holds':holds,'training_admission':False,'remaining':'Scientific group/topic review and final extraction/split protocol still required.'})
    assert len(records)==5403
    out.write_text(''.join(json.dumps(r)+'\n' for r in records));assert out.stat().st_size<m['output_byte_cap']
    summary={'status':'complete','queue_entries':len(records),'source_family_objects':len(all_docs),'benchmark_expert_contexts':1000,'review_or_qa_reserved_ids':len(reserved),'reserved_ids_present_in_source':len(reserved&all_docs.keys()),'overlapping_hold_counts':dict(flags),'entries_with_a_hold':sum(bool(r['holds']) for r in records),'entries_without_these_holds':sum(not r['holds'] for r in records),'naive_context_rescores':10,'elapsed_seconds':time.monotonic()-started,'source_sha256':sha(Path(__file__)),'manifest_sha256':sha(stage/'manifest.json'),'screens_sha256':sha(out),'training_admission':False,'limitations':'Exact normalized cached-body/DOI/PMID families and frozen PubMedQA five-token contexts only. No semantic duplicate, paraphrase, other benchmark, final narrative extraction, clinical evidence correctness or training eligibility claim.'}
    assert not (stage/'summary.json').exists();(stage/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',type=Path);run(p.parse_args().stage)
