#!/usr/bin/env python3
"""Optional source importer for public research datasets.

This script downloads files to PRIVATE local data/external/ for analysis. Do not commit
or republish external raw data without checking its source license and permissions.
Works on an internet-enabled computer; offline build package includes derived samples.
"""
import argparse, hashlib, json, urllib.request, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCES={
  'human50': {'url':'https://raw.githubusercontent.com/DevinRS/Settlers_of_Catan_Analysis/main/Analysis1/catanstats.csv','filename':'human50_catanstats.csv','expected_bytes':16689,'kind':'real-player-rows'},
  'features43k': {'url':'https://raw.githubusercontent.com/sousa16/catan-analyzer/master/data/features.parquet','filename':'thirdparty_features.parquet','expected_bytes':4258166,'kind':'derived-parquet'},
  'stats43k': {'url':'https://raw.githubusercontent.com/sousa16/catan-analyzer/master/data/stats.json','filename':'thirdparty_stats.json','expected_bytes':111746,'kind':'observed-aggregate'},
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sources',nargs='+',choices=list(SOURCES)+['all'],default=['human50','stats43k']);args=ap.parse_args()
    target=ROOT/'data'/'external';target.mkdir(exist_ok=True)
    keys=list(SOURCES) if 'all' in args.sources else args.sources
    metadata=[]
    for k in keys:
        src=SOURCES[k];url=src['url'];path=target/src['filename']
        print('Fetching',k,url)
        req=urllib.request.Request(url,headers={'User-Agent':'CatanStrategyLab-research/0.1'})
        with urllib.request.urlopen(req,timeout=45) as r,open(path,'wb') as f:
            digest=hashlib.sha256();size=0
            while True:
                chunk=r.read(1024*1024)
                if not chunk:break
                f.write(chunk);digest.update(chunk);size+=len(chunk)
        if size!=src['expected_bytes']:print('WARNING source byte count differs from verified listing:',size,'vs',src['expected_bytes'])
        if k=='human50':
            import csv
            with open(path,newline='') as f: records=list(csv.DictReader(f))
            assert len(records)==200 and len({r['gameNum'] for r in records})==50, 'Pilot sample changed shape; review schema.'
        metadata.append({'source_id':k,'downloaded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'path':str(path.relative_to(ROOT)),'sha256':digest.hexdigest(),'bytes':size,'kind':src['kind']})
    (target/'download_manifest.json').write_text(json.dumps(metadata,indent=2))
    print('Saved',len(metadata),'sources under data/external (gitignored)')
if __name__=='__main__':main()
