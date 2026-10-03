"""After successful source audits, measure volume and frozen overlap; no admission."""
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from transformers import AutoTokenizer
from pmc_overlap_audit import sha, rows, norm, shingles, matches


def run():
    began = time.monotonic()
    m = json.loads(Path('manifest.json').read_text())
    for name, digest in m['files_sha256'].items():
        assert sha(Path(name)) == digest, name
    snapshot = Path(m['tokenizer_snapshot'])
    assert all(sha(snapshot / n) == d for n, d in m['tokenizer_file_sha256'].items())
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    refs = {r['pmid']: shingles(' '.join(r['contexts'])) for r in rows(Path('contexts.jsonl'))}
    assert len(refs) == 1000
    index = defaultdict(list)
    for pid, values in refs.items():
        for value in values: index[value].append(pid)
    old = rows(Path('old_index.jsonl'))
    doi = {r['doi'].strip().casefold(): r['pmcid'] for r in old if r['doi']}
    bodies = {r['body_sha256']: r['pmcid'] for r in old}
    first = Path(m['first_documents'])
    assert sha(first) == m['first_documents_sha256']
    seen = {r['pmcid'] for r in old}
    for doc in rows(first):
        assert doc['pmcid'] not in seen; seen.add(doc['pmcid'])
        body = ' '.join(p['text'] for p in doc['paragraphs'])
        if doc['doi']: doi.setdefault(doc['doi'].strip().casefold(), doc['pmcid'])
        if body: bodies.setdefault(hashlib.sha256(norm(body).encode()).hexdigest(), doc['pmcid'])
    output = []; document_hashes = {}; audit_hashes = {}
    for chunk in m['chunks']:
        number = chunk['chunk']
        root = Path(m['acquisition_root']) / 'chunks' / str(number)
        audit_path = Path(m['audit_root']) / f'audit_{number}.json'
        audit = json.loads(audit_path.read_text())
        assert audit['status'] == 'passed' and audit['remaining'] == 0
        assert sha(root / 'plan.json') == chunk['plan_sha256']
        documents = root / 'documents.jsonl'
        document_hashes[str(number)] = sha(documents); audit_hashes[str(number)] = sha(audit_path)
        docs = rows(documents); assert len(docs) == audit['verified']
        for doc in docs:
            assert doc['pmcid'] not in seen; seen.add(doc['pmcid'])
            body = ' '.join(p['text'] for p in doc['paragraphs'])
            values = shingles(doc['abstract'] + ' ' + body)
            counts = Counter(pid for value in values for pid in index.get(value, ()))
            found = matches(values, refs, counts)
            if len(output) < 10:
                assert found == matches(values, refs, {pid: len(values & v) for pid, v in refs.items()})
            digest = hashlib.sha256(norm(body).encode()).hexdigest(); key = doc['doi'].strip().casefold()
            pieces = [doc['title'], doc['abstract']]; previous = []
            for p in doc['paragraphs']:
                if p['section'] != previous:
                    pieces.append(' / '.join(p['section'])); previous = p['section']
                pieces.append(p['text'])
            text = '\n\n'.join(pieces)
            output.append({'pmcid': doc['pmcid'], 'version': doc['version'], 'chunk': number,
                           'xml_sha256': doc['sha256'], 'xml_lang': doc['xml_lang'],
                           'normalized_body_sha256': digest, 'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                           'tokens_without_specials': len(tokenizer.encode(text, add_special_tokens=False)),
                           'benchmark_context_matches': found, 'duplicate_doi_of': doi.get(key),
                           'duplicate_body_of': bodies.get(digest) if body else None,
                           'training_eligibility': 'unreviewed'})
            if key: doi.setdefault(key, doc['pmcid'])
            if body: bodies.setdefault(digest, doc['pmcid'])
    Path('screens.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in output))
    result = {'status': 'passed', 'documents': len(output), 'document_sha256_by_chunk': document_hashes,
              'source_audit_sha256_by_chunk': audit_hashes, 'screens_sha256': sha(Path('screens.jsonl')),
              'tokens_all_unreviewed': sum(r['tokens_without_specials'] for r in output),
              'tokens_english_unreviewed': sum(r['tokens_without_specials'] for r in output if r['xml_lang'] == 'en'),
              'benchmark_context_flagged': sum(bool(r['benchmark_context_matches']) for r in output),
              'duplicate_doi': sum(bool(r['duplicate_doi_of']) for r in output),
              'duplicate_body': sum(bool(r['duplicate_body_of']) for r in output),
              'elapsed_seconds': time.monotonic() - began, 'training_admission': False,
              'limits': 'Frozen1000expert PubMedQA contexts and exact DOI/body matches only; no semantic/paraphrase or other benchmark guarantee. Raw tokenizer volume includes abstract/table/caption policy issues. Topic/design and full-text review remain required.'}
    Path('summary.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result))


if __name__ == '__main__':
    run()
