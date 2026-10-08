"""Resumable SEC primary 10-K acquisition; stage metadata before publication."""
import csv, hashlib, importlib.metadata, json, os, time, urllib.request, urllib.error
from pathlib import Path
from edgar.documents.parser import HTMLParser
from edgar.documents.config import ParserConfig
ROOT=Path(__file__).resolve().parent.parent
CP=ROOT/'data/checkpoints/expansion_20261008T073937Z'
UA=os.environ.get('SEC_USER_AGENT','Research Student liukunpeng267@gmail.com')
CUTOFF='2026-10-08'
SAMPLE={'Technology / Software':['MSFT','ADBE','CRM'],'Retail / Consumer Commerce':['WMT','TGT','COST'],'Financial Services / Banking':['JPM','BAC','C'],'Healthcare / Pharmaceuticals':['JNJ','PFE','MRK'],'Industrials / Manufacturing':['CAT','DE','HON'],'Energy / Oil & Gas':['XOM','CVX','COP']}
def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp');tmp.write_bytes(data);os.replace(tmp,path)
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def fetch(url,path):
    if path.exists():return path.read_bytes()
    for attempt in range(3):
        time.sleep(.6 if attempt==0 else 5*2**attempt)
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=90) as r:data=r.read()
            assert data
            atomic(path,data);return data
        except urllib.error.HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==2:raise
            delay=e.headers.get('Retry-After','')
            if delay.isdigit():time.sleep(min(int(delay),120))
def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--tickers',nargs='+')
    args=parser.parse_args()
    sectors={t:s for s,ts in SAMPLE.items() for t in ts}
    cache=CP/'sec_cache';cache.mkdir(parents=True,exist_ok=True)
    mapping={r['ticker']:r for r in json.loads(fetch('https://www.sec.gov/files/company_tickers.json',cache/'company_tickers.json')).values()}
    stage=CP/'sources_staged.json'
    selected=json.loads(stage.read_text()) if stage.exists() else {}
    previous={r['ticker']:r for r in read_csv(ROOT/'data/sources_downloaded.csv')}
    progress=json.loads((CP/'progress.json').read_text())
    def save():
        atomic(stage,json.dumps(selected,indent=2).encode())
        progress.update(status='source_acquisition_in_progress',blocker=None,source_records_verified=sum(r.get('download_status')=='verified' for r in selected.values()))
        for c in progress['companies']:
            r=selected.get(c['ticker'],{})
            c.update(issuer_verified=r.get('issuer_verified',False),source_acquisition=r.get('download_status','pending'))
        atomic(CP/'progress.json',json.dumps(progress,indent=2).encode())
    for i,ticker in enumerate(args.tickers or sectors):
        assert ticker in sectors
        if selected.get(ticker,{}).get('download_status')=='verified':
            r=selected[ticker]
            assert hashlib.sha256((ROOT/'data/raw'/r['source_file']).read_bytes()).hexdigest()==r['source_sha256']
            print(ticker,'checkpoint reused',flush=True);continue
        try:
            cik=int(mapping[ticker]['cik_str'])
            d=json.loads(fetch(f'https://data.sec.gov/submissions/CIK{cik:010d}.json',cache/f'CIK{cik:010d}.json'))
            assert int(d['cik'])==cik and ticker in d['tickers']
            current_cik=cik
            continuity='NA'
            continuity_url='NA'
            if ticker=='XOM' and cik==2115436:
                continuity_url='https://www.sec.gov/Archives/edgar/data/2115436/000119312526291990/d71068d8k12b.htm'
                disclosure=fetch(continuity_url,cache/'XOM_successor_8K12B.html').decode('utf-8')
                assert 'successor registrant' in disclosure.lower() and 'July' in disclosure
                cik=34088
                d=json.loads(fetch(f'https://data.sec.gov/submissions/CIK{cik:010d}.json',cache/f'CIK{cik:010d}.json'))
                assert int(d['cik'])==34088 and d['name']=='EXXON MOBIL CORP'
                continuity='Latest annual report of consolidated XOM group under predecessor registrant; successor redomiciliation effective 2026-07-01; no successor original 10-K by cutoff.'
            recent=d['filings']['recent']
            def eligible(a):
                return [{k:a[k][j] for k in a} for j,f in enumerate(a['form']) if f=='10-K' and a['filingDate'][j]<=CUTOFF]
            candidates=eligible(recent)
            if not candidates:
                for old in d['filings']['files']:
                    candidates.extend(eligible(json.loads(fetch('https://data.sec.gov/submissions/'+old['name'],cache/old['name']))))
            assert candidates,'No original 10-K before cutoff'
            f=max(candidates,key=lambda x:(x['filingDate'],x.get('acceptanceDateTime','')))
            acc=f['accessionNumber'];base=f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-","")}/'
            url=base+f['primaryDocument'];stem=f'{ticker}_10K_{f["filingDate"]}'
            hp=ROOT/'data/raw'/f'{stem}.html';tp=hp.with_suffix('.txt')
            if previous.get(ticker,{}).get('accession_number')==acc and hp.exists():html=hp.read_text(encoding='utf-8')
            else:
                assert not hp.exists(),'Do not overwrite unverified raw HTML'
                raw=fetch(url,cache/(stem+'.html'));html=raw.decode('utf-8-sig')
                assert len(html)>50000 and '<html' in html.lower() and '</html>' in html.lower()
                atomic(hp,raw)
            assert len(html)>50000 and '10-k' in html.lower()
            text=HTMLParser(ParserConfig(form='10-K')).parse(html).text(table_max_col_width=500,include_images=False)
            assert len(text.split())>10000
            if tp.exists():assert tp.read_text(encoding='utf-8')==text,'Normalization differs; original preserved'
            else:atomic(tp,text.replace('\n','\r\n').encode())
            am=[recent['accessionNumber'][j] for j,form in enumerate(recent['form']) if form=='10-K/A' and recent['reportDate'][j]==f['reportDate'] and recent['filingDate'][j]<=CUTOFF]
            selected[ticker]={'ticker':ticker,'company_name':d['name'],'sector':sectors[ticker],'industry':d.get('sicDescription',''),'cik':f'{cik:010d}','form_type':'10-K','filing_date':f['filingDate'],'period_end':f['reportDate'],'accession_number':acc,'source_url':base+acc+'-index.html','primary_document_url':url,'source_file':tp.name,'download_status':'verified','source_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'html_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'amendment_accessions':'|'.join(am) or 'NA','parser_version':'edgartools '+importlib.metadata.version('edgartools')+'; HTMLParser; max_col_width=500','issuer_verified':True}
            selected[ticker].update(current_ticker_cik=f'{current_cik:010d}',selection_note=continuity,entity_continuity_url=continuity_url)
            print(ticker,d['name'],acc,f['filingDate'],f['reportDate'],len(text.split()),flush=True)
        except Exception as e:
            selected[ticker]={'ticker':ticker,'download_status':'failed','issuer_verified':False,'error':str(e)};save();raise
        if (i+1)%3==0:save()
    save()
    if len(selected)==18 and all(r.get('download_status')=='verified' for r in selected.values()):
        rows=[selected[t] for t in sectors]
        for r in rows:
            r.setdefault('current_ticker_cik',r['cik'])
            r.setdefault('selection_note','NA')
            r.setdefault('entity_continuity_url','NA')
        assert len({(r['ticker'],r['accession_number']) for r in rows})==18
        path=CP/'sources_downloaded.csv';tmp=path.with_suffix('.tmp')
        with tmp.open('w',encoding='utf-8-sig',newline='') as out:
            w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        os.replace(tmp,path)
        progress['status']='sources_verified';atomic(CP/'progress.json',json.dumps(progress,indent=2).encode())
        print('All 18 complete primary sources verified; metadata staged.',flush=True)
if __name__=='__main__':main()

