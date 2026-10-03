"""Source-hashed JATS notice and related-article inventory; no admission decisions."""
import hashlib,json,time,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    began=time.monotonic();m=json.loads(Path('manifest.json').read_text())
    assert sha(Path(__file__))==m['source_sha256']
    seen=set(); counts=Counter(); output=[]; total_bytes=0
    for source in m['sources']:
        root=Path(source['root']);documents=root/'documents.jsonl'
        assert sha(documents)==source['documents_sha256']
        for line in documents.read_text().splitlines():
            doc=json.loads(line);assert doc['pmcid'] not in seen;seen.add(doc['pmcid'])
            path=root/'xml'/(doc['version']+'.xml');assert sha(path)==doc['sha256']
            article=ET.parse(path).getroot();meta=article.find('./front/article-meta')
            assert meta is not None
            title=' '.join(meta.find('./title-group/article-title').itertext()) if meta.find('./title-group/article-title') is not None else ''
            kind=article.attrib.get('article-type','');counts[kind]+=1
            relations=[]
            for tag in ('related-article','related-object'):
                for node in meta.findall('.//'+tag):
                    relations.append({'tag':tag,'attributes':dict(node.attrib),'text':' '.join(node.itertext())[:5000]})
            notice_kind=any(word in kind.lower() for word in ('retract','correct','concern'))
            notice_title=any(word in title.lower() for word in ('retract','corrigendum','erratum','expression of concern'))
            if relations or notice_kind or notice_title:
                row={'pmcid':doc['pmcid'],'pmid':doc['pmid'],'doi':doc['doi'],'version':doc['version'],
                     'xml_sha256':doc['sha256'],'article_type':kind,'title':title,'notice_type_flag':notice_kind,
                     'notice_title_flag':notice_title,'relations':relations,'training_eligibility':'unreviewed'}
                encoded=json.dumps(row)+'\n';total_bytes+=len(encoded.encode());assert total_bytes<=m['output_byte_cap'];output.append(row)
    assert len(seen)==m['expected_documents']==5819
    Path('notices.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in output))
    summary={'status':'complete','documents_checked':len(seen),'flagged_or_related':len(output),
             'article_types':dict(counts),'notice_type_flagged':sum(x['notice_type_flag'] for x in output),
             'notice_title_flagged':sum(x['notice_title_flag'] for x in output),
             'relation_nodes':sum(len(x['relations']) for x in output),'notices_sha256':sha(Path('notices.jsonl')),
             'elapsed_seconds':time.monotonic()-began,'training_admission':False,
             'limits':'Structured front/article-meta relationships and title/type keywords only. No registry refresh, unstructured body notice detection, resolved linkage or admission. Related article does not necessarily mean retraction; all flags require interpretation.'}
    Path('summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

if __name__=='__main__':run()
