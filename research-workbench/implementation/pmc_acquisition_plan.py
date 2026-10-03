"""Select exact licensed versions, conservatively excluding any evaluation/retracted version."""
from pmc_xml_pilot import source_url

def choose(row,expert,dev):
 versions=row.get('versions',[])
 if row['pmcid'] in set(dev['pmcids']):return None,'development_article'
 if not versions:return None,'no_versions'
 if any(v['metadata'].get('is_retracted') is not False for v in versions):return None,'retracted_or_unknown_version_flag'
 blocked=set(expert['pmids'])|{str(x) for x in dev['pmids']};dois={d.strip().casefold() for d in dev['dois']}
 if any(str(v['metadata'].get('pmid')) in blocked or str(v['metadata'].get('doi','')).strip().casefold() in dois for v in versions):return None,'evaluation_article'
 eligible=[v for v in versions if v['metadata'].get('license_code') in ['CC BY','CC0']]
 if not eligible:return None,'no_exact_licensed_version'
 v=max(eligible,key=lambda x:int(x['metadata']['version']));m=v['metadata']
 if not m.get('pmid') or not m.get('doi'):return None,'missing_identity'
 try:url,md5=source_url(m.get('xml_url',''),v['name'])
 except ValueError:return None,'invalid_source_url'
 return {'pmcid':row['pmcid'],'version':v['name'],'pmid':m['pmid'],'doi':m['doi'],'license_code':m['license_code'],'url':url,'md5':md5},None

def self_check():
 def version(n,**kw):return {'name':f'PMC123.{n}','metadata':{'version':n,'license_code':'CC BY','is_retracted':False,'pmid':456,'doi':'10.1/example','xml_url':f's3://pmc-oa-opendata/PMC123.{n}/PMC123.{n}.xml?md5='+('0'*32)}|kw}
 expert={'pmids':['999']};dev={'pmcids':[],'pmids':[],'dois':[]}
 assert choose({'pmcid':'PMC123','versions':[version(1),version(2)]},expert,dev)[0]['version']=='PMC123.2'
 assert choose({'pmcid':'PMC123','versions':[version(1,pmid=999),version(2)]},expert,dev)[1]=='evaluation_article'
 assert choose({'pmcid':'PMC123','versions':[version(1,is_retracted=True),version(2)]},expert,dev)[1]=='retracted_or_unknown_version_flag'
 assert choose({'pmcid':'PMC123','versions':[version(1,doi=None)]},expert,dev)[1]=='missing_identity'
 assert choose({'pmcid':'PMC123','versions':[version(1,license_code='TDM')]},expert,dev)[1]=='no_exact_licensed_version'
if __name__=='__main__':self_check();print('Version/evaluation/retraction gates passed.')
