"""Source identity, extraction, annotations, aggregation and recovery QA."""
import csv,hashlib,html,json,re,sys
from pathlib import Path
from collections import Counter
from importlib import import_module
CP=Path(__file__).resolve().parent;ROOT=CP.parents[2]
sys.path.insert(0,str(ROOT/'src_code'))
ex=import_module('2_extract_ai');metrics=import_module('3_document_metrics')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(base=CP):
    source=read(base/'sources_downloaded.csv');parents=read(base/'ai_passages.csv');full=read(base/'ai_annotations_full.csv');core=read(base/'ai_annotations.csv');mm=read(base/'document_metrics.csv')
    assert len(source)==len(mm)==42 and len({r['ticker'] for r in source})==42
    assert sorted(Counter(r['sector'] for r in source).values())==[7]*6
    assert len({r['claim_id'] for r in full})==len(full)
    assert len({r['passage_id'] for r in parents})==len(parents)
    assert set(r['ticker'] for r in source)==set(r['ticker'] for r in mm)==set(r['ticker'] for r in full)
    assert set(r['passage_id'] for r in parents)==set(r['passage_id'] for r in full)
    mapping={r['ticker']:r for r in json.loads((CP/'sec_cache/company_tickers.json').read_text()).values()}
    words={};oldcache=ROOT/'data/checkpoints/expansion_20261008T073937Z/sec_cache'
    for m in source:
        t=m['ticker'];cik=int(m['cik']);assert int(mapping[t]['cik_str'])==int(m['current_ticker_cik'])
        assert cik==int(m['current_ticker_cik']) or t=='XOM' and cik==34088 and int(m['current_ticker_cik'])==2115436 and 'predecessor' in m['selection_note'].lower()
        assert m['form_type']=='10-K' and m['filing_date']<='2026-10-08' and m['period_end']<=m['filing_date']
        assert m['issuer_verified'].lower()=='true' and m['download_status']=='verified'
        assert m['primary_document_url'].startswith(f'https://www.sec.gov/Archives/edgar/data/{cik}/')
        assert m['accession_number'].replace('-','') in m['primary_document_url'] and m['accession_number'] in m['source_url']
        p=ROOT/'data/raw'/m['source_file'];hp=p.with_suffix('.html')
        assert digest(p)==m['source_sha256'] and digest(hp)==m['html_sha256']
        h=hp.read_text(encoding='utf-8');assert '<html' in h.lower() and '</html>' in h.lower() and len(h)>50000
        def dei(field):
            found=re.search(r'<ix:nonNumeric\b([^>]*\bname=["\x27]dei:'+field+r'["\x27][^>]*)>(.*?)</ix:nonNumeric>',h,re.I|re.S)
            assert found,(t,field)
            return html.unescape(re.sub('<[^>]+>','',found[2])).strip(),found[1]
        assert dei('DocumentType')[0]=='10-K'
        if re.search(r'name=["\x27]dei:EntityCentralIndexKey',h,re.I):
            assert int(dei('EntityCentralIndexKey')[0])==cik
        else:
            # Some multipart iXBRL filings put resources in an incorporated document.
            cover={'WFC':'WELLS FARGO & COMPANY','USB':'U.S. BANCORP'}
            assert t in cover and cover[t].lower() in html.unescape(re.sub('<[^>]+>',' ',h)).lower()
        _,attrs=dei('DocumentPeriodEndDate');ref=re.search(r'\bcontextRef=["\x27]([^"\x27]+)',attrs,re.I)[1]
        ctx=re.search(r'<(?:\w+:)?context\b[^>]*\bid=["\x27]'+re.escape(ref)+r'["\x27][^>]*>(.*?)</(?:\w+:)?context>',h,re.I|re.S)
        if ctx:
            assert re.search(r'<(?:\w+:)?(?:endDate|instant)>([^<]+)',ctx[1],re.I)[1]==m['period_end']
        else:
            from datetime import datetime
            assert t in ('WFC','USB')
            period=dei('DocumentPeriodEndDate')[0]
            assert datetime.strptime(period,'%B %d, %Y').strftime('%Y-%m-%d')==m['period_end']
        cache=CP/'sec_cache'/f'CIK{cik:010d}.json'
        if not cache.exists():cache=oldcache/cache.name
        d=json.loads(cache.read_text());a=d['filings']['recent'];assert int(d['cik'])==cik
        selected=[j for j,f in enumerate(a['form']) if f=='10-K' and a['filingDate'][j]<='2026-10-08']
        j=max(selected,key=lambda j:(a['filingDate'][j],a['acceptanceDateTime'][j]))
        assert (m['accession_number'],m['filing_date'],m['period_end'])==(a['accessionNumber'][j],a['filingDate'][j],a['reportDate'][j])
        with p.open(encoding='utf-8',newline='') as f:text=f.read()
        words[t]=text;pp=[r for r in parents if r['ticker']==t];found=list(ex.extract_passages(text));assert len(pp)==len(found)
        for r,(line,kw,block) in zip(pp,found):
            assert (r['line_number'],r['matched_keywords'],r['passage_text'])==(str(line),kw,block)
            assert r['passage_id']==ex.passage_id(t,p.name,line,block)
        row=next(r for r in mm if r['ticker']==t);wc=len(text.split());cw=sum(len(r['passage_text'].split()) for r in pp);mentions=metrics.count_mentions(text)
        assert int(row['total_word_count'])==wc>10000
        assert int(row['ai_candidate_passage_count'])==len(pp) and int(row['ai_candidate_word_count'])==cw
        assert int(row['ai_mention_count'])==mentions
        assert abs(float(row['ai_candidate_word_share'])-cw/wc)<1e-12
        assert abs(float(row['ai_mentions_per_1000_words'])-1000*mentions/wc)<1e-12
        expected=metrics.semantic_summary([r for r in full if r['ticker']==t])
        assert all(int(row[k])==v for k,v in expected.items())
    pp={r['passage_id']:r for r in parents};claims={r['claim_id']:r for r in full}
    for r in full:
        p=pp[r['passage_id']];assert (r['ticker'],r['source_file'],r['source_line'])==(p['ticker'],p['source_file'],p['line_number'])
        text=words[r['ticker']];assert text[int(r['evidence_start_char']):int(r['evidence_end_char'])]==r['evidence_quote']
        assert r['human_validated']=='no' and r['context_reviewed']=='yes'
        st=r['adoption_stage'];assert st in ('1','2','3','4','5','NA')
        if st!='NA':assert r['ai_relevance']=='substantive' and r['actor']=='focal_firm' and r['focal_firm_evidence']=='yes' and r['stage_eligible']=='yes'
        if st=='2':assert r['use_case']!='NA' and r['temporal_status']=='planned' and r['forward_looking']=='yes'
        if st=='3':assert r['pilot_reported']=='yes'
        if st in ('4','5'):assert r['temporal_status']=='current' and r['reported_deployment']=='yes'
        if st=='5':assert r['quantified_outcome']=='yes' and r['outcome_attribution']=='explicit_application' and r['outcome_metric']!='NA'
    assert len(core[0])==23 and len(full[0])==49
    for uid in {r['use_case_id'] for r in full}-{'NA'}:
        members=[r for r in full if r['use_case_id']==uid]
        assert len({(r['ticker'],r['report_period'],r['actor'],r['use_case'],r['application_scope']) for r in members})==1,(uid,'case identity conflict')
    assert {r['claim_id'] for r in core}=={r['claim_id'] for r in full if r['adoption_stage']!='NA'}
    assert all(all(claims[r['claim_id']][k]==v for k,v in r.items()) for r in core)
    backup=ROOT/'data/backups/expansion42_20261008'
    for name,sha in json.loads((backup/'hashes.json').read_text()).items():assert digest(backup/name)==sha
    assert digest(ROOT/'Protocol.md')==digest(backup/'Protocol.md')
    for old in read(backup/'data/ai_passages.csv'):
        assert old==pp[old['passage_id']]
    for old in read(backup/'data/sources_downloaded.csv'):
        newer=next(r for r in source if r['ticker']==old['ticker'])
        assert all(newer[k]==v for k,v in old.items()),old['ticker']
    for old in read(backup/'data/document_metrics.csv'):
        newer=next(r for r in mm if r['ticker']==old['ticker'])
        assert all(newer[k]==v for k,v in old.items()),old['ticker']
    deployed=[r for r in full if r['adoption_stage'] in ('4','5') and r['use_case_id']!='NA' and r['use_case_identity_status']=='resolved']
    ids={r['use_case_id'] for r in deployed};inside={r['use_case_id'] for r in deployed if 'internal_operations' in r['application_scope'].split('|')};product={r['use_case_id'] for r in deployed if 'customer_facing_product' in r['application_scope'].split('|')}
    result=dict(status='passed',companies=len(source),sectors=6,filings=len(source),candidate_passages=len(parents),full_records=len(full),core_claims=len(core),stages=dict(Counter(r['adoption_stage'] for r in full)),stage_na_percent=100*sum(r['adoption_stage']=='NA' for r in full)/len(full),distinct_applications=len({r['use_case_id'] for r in full if r['use_case_id']!='NA' and r['actor']=='focal_firm' and r['ai_relevance']=='substantive'}),deployed_applications=len(ids),internal_deployed=len(inside),customer_facing_deployed=len(product),other_deployed=len(ids-inside-product),scope_overlap=len(inside&product),firms_reporting_deployment=sum(int(r['reported_deployment_present']) for r in mm),firms_without_qualifying_stage=sum(int(r['stage_eligible_claim_count'])==0 for r in mm),needs_human_review=sum(r['needs_human_review']=='yes' for r in full),human_validated=0,stage_na_reasons=dict(Counter(r['stage_na_reason'] for r in full if r['adoption_stage']=='NA')),checks=['SEC ticker/CIK identity, XBRL form/CIK/period, latest original annual selection and cutoff','Primary HTML/text integrity, complete primary documents, hashes, source URLs','Exact extraction regeneration, all 393 existing parent IDs and all old lexical metrics preserved','Complete candidate coverage, unique claims, exact quotes, stage eligibility and actor/time safeguards','Full/core correspondence, NA archive retention, deduplicated IDs, full-archive risk/governance metrics','42 complete firm rows including semantic zeros, unchanged protocol and verified eight-file pilot backup'])
    (CP/'qa_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    return result
if __name__=='__main__':validate(Path(sys.argv[1]) if len(sys.argv)>1 else CP)
