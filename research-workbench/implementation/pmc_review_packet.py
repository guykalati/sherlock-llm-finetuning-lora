"""Export source-linked full-text review packets without admitting training data."""
import hashlib
import json
from pathlib import Path
from pmc_metadata_pilot import read_jsonl

BASE=Path(__file__).resolve().parent

def run():
    docs_path=BASE/'data/pmc_xml_expansion_20260929/documents.jsonl'
    queue_path=BASE/'pmc_primary_review_queue_2026-09-30.jsonl'
    documents={r['pmcid']:r for r in read_jsonl(docs_path)}
    out=BASE/'data/pmc_fulltext_review_20260930'
    out.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for candidate in read_jsonl(queue_path):
        row=documents[candidate['pmcid']]
        assert row['version']==candidate['version'] and row['sha256']==candidate['sha256']
        assert row['well_formed'] and row['verified_md5'] and row['xml_lang']=='en'
        groups={'methods':[],'results':[],'conclusions':[],'other':[]}
        for index,paragraph in enumerate(row['paragraphs']):
            heading=' '.join(paragraph['section']).lower()
            group=('methods' if any(w in heading for w in ['method','material','patient'])
                   else 'results' if 'result' in heading else 'conclusions' if 'conclu' in heading else 'other')
            groups[group].append({'paragraph_index':index,**paragraph})
        packet={'source':candidate,'abstract':row['abstract'],'section_titles':row['section_titles'],
                'paragraph_groups':groups,'review_status':'pending_fulltext_review',
                'training_eligibility':'unreviewed','independent_expert_adjudication':False,
                'review_questions':['Does source study design and original data match the proposed tier?',
                                    'Are cardiovascular outcomes central to the investigation?',
                                    'Are sample/denominator statements internally consistent?',
                                    'Are methods, results and conclusion correctly preserved?',
                                    'Does the claim describe association, retrospective classification or prospective prediction?']}
        destination=out/(row['pmcid']+'.json')
        destination.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
        assert sum(len(v) for v in groups.values())==len(row['paragraphs'])
        summaries.append({'pmcid':row['pmcid'],'version':row['version'],'xml_sha256':row['sha256'],
                          'packet_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
                          'paragraph_group_counts':{k:len(v) for k,v in groups.items()},
                          'methods_present':bool(groups['methods']),'results_present':bool(groups['results']),
                          'training_eligibility':'unreviewed'})
    summary={'status':'exported','documents':len(summaries),
             'documents_sha256':hashlib.sha256(docs_path.read_bytes()).hexdigest(),
             'review_queue_sha256':hashlib.sha256(queue_path.read_bytes()).hexdigest(),'packets':summaries,
             'limits':'Heading grouping is a navigation aid; paragraphs retain index and original section path. No clinical validity, eligibility or model-quality claim.'}
    (BASE/'pmc_fulltext_review_packets_2026-09-30.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'status':summary['status'],'documents':summary['documents'],
                     'methods_and_results':sum(r['methods_present'] and r['results_present'] for r in summaries)}))

if __name__=='__main__':run()
