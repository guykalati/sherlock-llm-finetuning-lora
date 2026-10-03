"""Measure cached-Qwen tokenizer volume; corpus eligibility remains unresolved."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from transformers import AutoTokenizer

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(documents, queue, snapshot, output):
    started=time.monotonic()
    selected={json.loads(line)['pmcid'] for line in queue.read_text().splitlines() if line}
    tokenizer=AutoTokenizer.from_pretrained(snapshot,local_files_only=True)
    rows=[]
    for line in documents.read_text().splitlines():
        doc=json.loads(line)
        pieces=[doc['title'],doc['abstract']]
        previous=[]
        for p in doc['paragraphs']:
            if p['section']!=previous:
                pieces.append(' / '.join(p['section']))
                previous=p['section']
            pieces.append(p['text'])
        text='\n\n'.join(pieces)
        tokens=len(tokenizer.encode(text,add_special_tokens=False))
        rows.append({'pmcid':doc['pmcid'],'version':doc['version'],'xml_sha256':doc['sha256'],
                     'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'characters':len(text),
                     'tokens_without_specials':tokens,'blocks_2048_including_final_partial':(tokens+2047)//2048,
                     'review_queue':doc['pmcid'] in selected,'xml_lang':doc['xml_lang'],
                     'training_eligibility':'unreviewed'})
    assert len(rows)==977 and len({r['pmcid'] for r in rows})==977
    assert {r['pmcid'] for r in rows if r['review_queue']}==selected
    result={'status':'measured','documents':len(rows),'model_snapshot':snapshot.name,
            'documents_sha256':sha(documents),'queue_sha256':sha(queue),
            'tokenizer_file_sha256':{p.name:sha(p) for p in snapshot.iterdir() if p.name in
                                    ['tokenizer.json','tokenizer_config.json','vocab.json','merges.txt','config.json']},
            'tokens_all_unreviewed_documents':sum(r['tokens_without_specials'] for r in rows),
            'tokens_english_unreviewed_documents':sum(r['tokens_without_specials'] for r in rows if r['xml_lang']=='en'),
            'review_queue_documents':len(selected),
            'tokens_review_queue':sum(r['tokens_without_specials'] for r in rows if r['review_queue']),
            'elapsed_seconds':time.monotonic()-started,'rows':rows,
            'limits':'Volume inventory only. No corpus admission, split, training, model inference or tokenizer download. Includes tables/captions and abstract duplication; final text policy changes volume. Block count is arithmetic, not an emitted training dataset.'}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','documents','tokens_all_unreviewed_documents','review_queue_documents','tokens_review_queue','elapsed_seconds']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['documents','queue','snapshot','output']:parser.add_argument(name,type=Path)
    args=parser.parse_args()
    run(args.documents,args.queue,args.snapshot,args.output)
