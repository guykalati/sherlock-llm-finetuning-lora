"""Resolve explicitly typed notice links against the acquired pool; never admit text."""
import argparse, hashlib, json, re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

HREF = '{http://www.w3.org/1999/xlink}href'

def identifier(kind, href):
    value = unquote(href).strip()
    if kind == 'pmc':
        match = re.fullmatch(r'(?:https?://(?:pmc\.ncbi\.nlm\.nih\.gov|www\.ncbi\.nlm\.nih\.gov/pmc)/articles/)?(PMC\d+)/?', value, re.I)
        return ('pmcid', match[1].upper()) if match else None
    if kind == 'doi':
        value = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', value, flags=re.I)
        return ('doi', value.casefold()) if re.fullmatch(r'10\.\d{4,9}/\S+', value) else None
    if kind in {'pubmed', 'pmid'}:
        value = re.sub(r'^https?://pubmed\.ncbi\.nlm\.nih\.gov/', '', value, flags=re.I).rstrip('/')
        return ('pmid', str(int(value))) if re.fullmatch(r'\d{1,12}', value) and int(value) > 0 else None
    return None

def run(notices, document_paths, output):
    docs = {}
    for path in document_paths:
        for line in path.read_text().splitlines():
            row = json.loads(line); assert row['pmcid'] not in docs; docs[row['pmcid']] = row
    assert len(docs) == 5819
    doi = {}; pmids = {}
    for row in docs.values():
        key = (row.get('doi') or '').strip().casefold()
        if key:
            assert key not in doi, 'ambiguous DOI in acquired pool'
            doi[key] = row['pmcid']
        if row.get('pmid'):
            key = str(int(row['pmid']))
            assert key not in pmids, 'ambiguous PMID in acquired pool'
            pmids[key] = row['pmcid']
    flags = {}; links = []; notice_rows = [json.loads(line) for line in notices.read_text().splitlines()]
    def flag(pmcid, reason): flags.setdefault(pmcid, set()).add(reason)
    for row in notice_rows:
        assert row['xml_sha256'] == docs[row['pmcid']]['sha256']
        assert row['article_type'] == docs[row['pmcid']]['article_type']
        if row['notice_type_flag'] or row['notice_title_flag']:
            flag(row['pmcid'], 'notice_document_requires_review')
        for relation in row['relations']:
            a = relation['attributes']; kind = a.get('related-article-type')
            if kind not in {'retracted-article', 'corrected-article', 'correction-forward', 'retraction-forward'}:
                continue
            target = identifier(a.get('ext-link-type'), a.get(HREF, ''))
            matched = (target[1] if target[0] == 'pmcid' and target[1] in docs else
                       doi.get(target[1]) if target[0] == 'doi' else
                       pmids.get(target[1]) if target[0] == 'pmid' else None) if target else None
            links.append({'source_pmcid': row['pmcid'], 'relation': kind, 'target_identifier': target,
                          'target_in_acquired_pool': matched, 'attributes': a, 'xml_sha256': row['xml_sha256']})
            if kind.endswith('-forward'):
                flag(row['pmcid'], kind + '_requires_review')
            if matched:
                flag(matched, kind + '_incoming_requires_review')
    output.mkdir(exist_ok=False)
    blocked = [{'pmcid': ident, 'xml_sha256': docs[ident]['sha256'], 'reasons': sorted(reasons),
                'training_eligibility': 'unreviewed_notice_link_hold'} for ident, reasons in sorted(flags.items())]
    for name, rows in [('links.jsonl', links), ('review_holds.jsonl', blocked)]:
        (output/name).write_text(''.join(json.dumps(row)+'\n' for row in rows))
    summary = {'status': 'resolved', 'documents': len(docs), 'notice_rows': len(notice_rows),
               'relevant_relations': len(links), 'relation_types': dict(Counter(r['relation'] for r in links)),
               'targets_in_pool': sum(bool(r['target_in_acquired_pool']) for r in links),
               'unparsed_targets': sum(r['target_identifier'] is None for r in links),
               'held_for_review': len(blocked), 'reason_counts': dict(Counter(reason for r in blocked for reason in r['reasons'])),
               'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [notices, *document_paths]},
               'training_admission': False,
               'limits': 'Exact explicitly typed PMCID/DOI/PMID links only. Corrections require content review; they do not prove invalid findings. No unstructured notice search, external registry refresh or deletion; remaining articles are still unreviewed.'}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))

def self_check():
    assert identifier('pmc','PMC123') == ('pmcid','PMC123')
    assert identifier('pmc','https://pmc.ncbi.nlm.nih.gov/articles/PMC123/') == ('pmcid','PMC123')
    assert identifier('doi','https://doi.org/10.1234/Test') == ('doi','10.1234/test')
    assert identifier('pmc','PMC123 PMC456') is None
    assert identifier('unknown','PMC123') is None
    assert identifier('pubmed','https://pubmed.ncbi.nlm.nih.gov/123/') == ('pmid','123')
    assert identifier('pubmed','0') is None

if __name__ == '__main__':
    self_check(); p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('notices',type=Path);p.add_argument('output',type=Path);p.add_argument('documents',type=Path,nargs='+')
    a=p.parse_args();run(a.notices,a.documents,a.output)
