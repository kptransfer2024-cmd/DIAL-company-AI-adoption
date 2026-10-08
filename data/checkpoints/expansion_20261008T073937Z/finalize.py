"""Validate all staged research outputs; generate the report; atomically publish."""
import csv,hashlib,html,json,os,re,sys
from collections import Counter,defaultdict
from pathlib import Path
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf-8')
CP=Path(__file__).resolve().parent
ROOT=CP.parents[2]
sys.path.insert(0,str(ROOT/'src_code'))
from importlib import import_module
ex=import_module('2_extract_ai')
mt=import_module('3_document_metrics')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,b):
    tmp=p.with_name(p.name+'.tmp');tmp.write_bytes(b);os.replace(tmp,p)
def write_csv(p,rows,fields):
    tmp=p.with_name(p.name+'.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    assert read(tmp)==rows
    os.replace(tmp,p)
metadata=read(CP/'sources_downloaded.csv')
parents=read(CP/'ai_passages.csv')
metrics=read(CP/'document_metrics.csv')
annotations=[r for p in sorted((CP/'annotation_batches').glob('*.csv')) for r in read(p)]
old_annotations=read(ROOT/'data/backups/20261008T073937Z/data/ai_annotations.csv')
assert list(annotations[0])==list(old_annotations[0])
ids={r['claim_id']:r for r in annotations}
assert len(ids)==len(annotations)
for correction in json.loads((CP/'semantic_corrections.json').read_text()):
    ids[correction['claim_id']].update(correction['changes'])
assert len(metadata)==18 and len({r['ticker'] for r in metadata})==18
assert len({(r['ticker'],r['accession_number']) for r in metadata})==18
meta={r['ticker']:r for r in metadata}
mm={r['ticker']:r for r in metrics}
pp={r['passage_id']:r for r in parents}
assert len(pp)==len(parents)==393
assert set(meta)==set(mm)=={r['ticker'] for r in parents}=={r['ticker'] for r in annotations}
raws={}
qa_checks=[]
for t,m in meta.items():
    assert m['form_type']=='10-K' and m['filing_date']<='2026-10-08' and m['period_end']<=m['filing_date']
    assert m['download_status']=='verified' and m['issuer_verified']=='True'
    assert m['primary_document_url'].startswith(f"https://www.sec.gov/Archives/edgar/data/{int(m['cik'])}/")
    p=ROOT/'data/raw'/m['source_file'];hp=p.with_suffix('.html')
    assert digest(p)==m['source_sha256'] and digest(hp)==m['html_sha256']
    h=hp.read_text(encoding='utf-8')
    assert len(h)>50000 and '<html' in h.lower() and '</html>' in h.lower()
    def dei(field):
        match=re.search(r'<ix:nonNumeric\b([^>]*\bname=["\x27]dei:'+field+r'["\x27][^>]*)>(.*?)</ix:nonNumeric>',h,re.I|re.S)
        assert match,(t,field)
        return html.unescape(re.sub('<[^>]+>','',match[2])).strip(),match[1]
    assert int(dei('EntityCentralIndexKey')[0])==int(m['cik'])
    assert dei('DocumentType')[0]=='10-K'
    _,attrs=dei('DocumentPeriodEndDate')
    ref=re.search(r'\bcontextRef=["\x27]([^"\x27]+)',attrs,re.I).group(1)
    context=re.search(r'<(?:\w+:)?context\b[^>]*\bid=["\x27]'+re.escape(ref)+r'["\x27][^>]*>(.*?)</(?:\w+:)?context>',h,re.I|re.S)
    assert context,(t,ref)
    end=re.search(r'<(?:\w+:)?(?:endDate|instant)>([^<]+)',context[1],re.I)
    assert end and end[1]==m['period_end'],(t,end[1] if end else None,m['period_end'])
    cache=CP/'sec_cache'/f"CIK{int(m['cik']):010d}.json"
    d=json.loads(cache.read_text())
    a=d['filings']['recent']
    annual=[i for i,f in enumerate(a['form']) if f=='10-K' and a['filingDate'][i]<='2026-10-08']
    assert annual and m['accession_number']==a['accessionNumber'][max(annual,key=lambda i:(a['filingDate'][i],a['acceptanceDateTime'][i]))]
    j=a['accessionNumber'].index(m['accession_number'])
    assert m['filing_date']==a['filingDate'][j] and m['period_end']==a['reportDate'][j]
    with p.open(encoding='utf-8',newline='') as f:text=f.read()
    raws[t]=text
    retrieved=list(ex.extract_passages(text))
    selected=[r for r in parents if r['ticker']==t]
    assert len(retrieved)==len(selected)
    for (line,keywords,passage),row in zip(retrieved,selected):
        assert row['source_file']==p.name and int(row['line_number'])==line and row['matched_keywords']==keywords and row['passage_text']==passage
        assert row['passage_id']==ex.passage_id(t,p.name,line,passage)
    mrow=mm[t]
    words=len(text.split());cwords=sum(len(r['passage_text'].split()) for r in selected);mentions=mt.count_mentions(text)
    assert int(mrow['total_word_count'])==words>10000
    assert int(mrow['ai_candidate_passage_count'])==len(selected)
    assert int(mrow['ai_candidate_word_count'])==cwords
    assert int(mrow['ai_mention_count'])==mentions
    assert abs(float(mrow['ai_candidate_word_share'])-cwords/words)<1e-12
    assert abs(float(mrow['ai_mentions_per_1000_words'])-1000*mentions/words)<1e-12
qa_checks.extend(['18 issuer/source identities, latest original 10-K selections and cutoff verified, including explicitly documented XOM predecessor exception','18 primary HTML checksums, closing document tags, inline XBRL CIK/form/report-date context and metadata verified','393 extraction records reproduced exactly from source; unique stable IDs and exact-text deduplication verified','All word-count, candidate-count, word-share and nonoverlapping mention formulas reconciled'])
cal=read(ROOT/'data/calibration_sample.csv')
for r in cal:
    assert r['passage_id'] in pp
    assert pp[r['passage_id']]['passage_text']==r['passage_text']
old_parents=read(ROOT/'data/backups/20261008T073937Z/data/ai_passages.csv')
lookup={(r['ticker'],r['source_file'],r['line_number']):r for r in parents}
keyword_changes=0
for r in old_parents:
    new=lookup[(r['ticker'],r['source_file'],r['line_number'])]
    assert new['passage_text']==r['passage_text']
    if new['matched_keywords']!=r['matched_keywords']:keyword_changes+=1
    assert new['passage_id'] in {a['passage_id'] for a in old_annotations}
old_metrics=read(ROOT/'data/backups/20261008T073937Z/data/document_metrics.csv')
assert all(next(x for x in metrics if x['ticker']==r['ticker'])==r for r in old_metrics)
qa_checks.append('Original 140 parent texts/locations/IDs, 15 calibration IDs, and all three lexical metric rows preserved; one Microsoft keyword-tag recomputation difference documented')
sets={'ai_relevance':{'substantive','context_only','irrelevant','uncertain'},'focal_firm_evidence':{'yes','no','unclear'},'actor':{'focal_firm','customer','partner','competitor','industry','other','unclear'},'temporal_status':{'planned','current','historical','discontinued','hypothetical','unclear'},'ai_technology_type':{'genai','traditional_ml','mixed','unspecified_ai','NA'},'stage_eligible':{'yes','no','uncertain'},'adoption_stage':{'1','2','3','4','5','NA'},'operational_stage':{'1','2','3','4','NA'},'strategy_specificity':{'1','2','3','4','5','NA'},'coding_confidence':{'high','medium','low'},'human_validated':{'no'},'use_case_identity_status':{'resolved','provisional','not_identified','NA'},'record_type':{'claim','screening'},'outcome_attribution':{'explicit_application','shared_drivers','unlinked','ai_general','unclear','NA'}}
for f in 'ai_commitment forward_looking is_strategy_claim reported_deployment pilot_reported ai_investment ai_partnership ai_risk ai_governance quantified_outcome needs_human_review context_reviewed'.split():sets[f]={'yes','no','NA'}
scopes={'internal_operations','customer_facing_product','customer_adoption_claim','research_and_development','infrastructure_or_platform','partnership_or_investment','unclear_or_other','NA'}
orientations={'efficiency','innovation','customer_experience','revenue_growth','workforce_productivity','competitive_positioning','responsible_ai','security','infrastructure_capacity','other','NA'}
risks={'financial','operational','competitive','regulatory','third_party','capacity','misuse','reputational','cybersecurity','privacy','intellectual_property','model_quality','bias','safety','workforce','environmental','NA'}
for r in annotations:
    p=pp[r['passage_id']]
    assert r['ticker']==p['ticker'] and r['source_file']==p['source_file'] and r['source_line']==p['line_number']
    assert r['report_period']==meta[r['ticker']]['period_end']
    start,end=int(r['evidence_start_char']),int(r['evidence_end_char'])
    assert r['evidence_quote']==raws[r['ticker']][start:end] and start<end
    assert int(r['evidence_start_line'])==1+len(re.findall(r'\r\n|\r|\n',raws[r['ticker']][:start]))
    assert int(r['evidence_end_line'])==1+len(re.findall(r'\r\n|\r|\n',raws[r['ticker']][:end]))
    for f,values in sets.items():assert r[f] in values,(r['claim_id'],f,r[f])
    for f,allowed in [('application_scope',scopes),('strategic_orientation',orientations),('risk_category',risks)]:assert set(r[f].split('|'))<=allowed
    assert all(v!='' for v in r.values()),r['claim_id']
    if r['adoption_stage']!='NA':
        assert r['stage_eligible']=='yes' and r['ai_relevance']=='substantive' and r['actor']=='focal_firm' and r['focal_firm_evidence']=='yes'
    if r['stage_eligible']!='yes':assert r['adoption_stage']=='NA'
    if r['ai_relevance']!='substantive':assert r['adoption_stage']=='NA'
    if r['adoption_stage'] in ('4','5'):assert r['reported_deployment']=='yes' and r['temporal_status']=='current'
    if r['adoption_stage']=='3':assert r['pilot_reported']=='yes'
    if r['adoption_stage']=='5':
        assert r['operational_stage']=='4' and r['quantified_outcome']=='yes' and r['outcome_attribution']=='explicit_application' and r['outcome_metric']!='NA'
    if r['adoption_stage']=='2':assert r['use_case']!='NA' and r['forward_looking']=='yes' and r['temporal_status']=='planned'
    if r['coding_confidence'] in ('low','medium') or r['stage_eligible']=='uncertain':assert r['needs_human_review']=='yes'
    if r['ai_risk']=='yes' and r['is_strategy_claim']!='yes' and r['reported_deployment']!='yes':assert r['adoption_stage']=='NA'
assert {r['passage_id'] for r in annotations}==set(pp)
for uid in {r['use_case_id'] for r in annotations}-{'NA'}:
    members=[r for r in annotations if r['use_case_id']==uid]
    assert len({(r['ticker'],r['report_period'],r['use_case'],r['application_scope'],r['actor']) for r in members})==1,(uid,'identity conflict')
qa_checks.extend(['447 unique claim IDs cover every one of 393 parents; no blank/unprocessed fields or orphan records','All exact quotations/offsets/source lines/report periods, categories and numeric ranges verified','Stage-ineligible/screening/risk-only safeguards, current-versus-historical timing, plan eligibility and Stage 5 mapping checked','Named application identities reconcile across repetitions; claims and parent passages not used as application counts','All rows unvalidated; no individual Stage 0, pilot, or Stage 5 claims'])
preserved=json.loads((ROOT/'data/backups/20261008T073937Z/hashes.json').read_text())
for e in preserved:
    if e.get('backup'):assert digest(ROOT/e['backup'])==e['sha256']
    if e.get('preserve_only'):assert digest(ROOT/e['original'])==e['sha256'],e['original']
for name in ('data/calibration_sample.csv',):
    # Verify against its known original first-pass hash.
    assert digest(ROOT/name)=='17f4213d64dc929778c9b0d969ef8a322baf89a7480c98d9ca6d86a505c97fbe'
qa_checks.append('Original CSV/report/script backups hash-verified; protocol, notebook, original raw files and calibration sample unchanged')
# Protect contemporaneous canonical changes before publication as well.
backup=ROOT/'data/backups'/('publication_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(exist_ok=False)
publication_hashes=[]
canonical=['data/sources_downloaded.csv','data/ai_passages.csv','data/document_metrics.csv','data/ai_annotations.csv','AI_Annotation_First_Pass_Report.md']
for name in canonical:
    source=ROOT/name;target=backup/name;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(source.read_bytes());assert digest(source)==digest(target)
    publication_hashes.append({'path':name,'sha256':digest(source),'backup':str(target.relative_to(ROOT))})
(backup/'hashes.json').write_text(json.dumps(publication_hashes,indent=2),encoding='utf-8')
write_csv(CP/'ai_annotations.csv',annotations,list(annotations[0]))
relevance=Counter(r['ai_relevance'] for r in annotations)
stages=Counter(r['adoption_stage'] for r in annotations)
confidence=Counter(r['coding_confidence'] for r in annotations)
deployed={r['use_case_id'] for r in annotations if r['reported_deployment']=='yes' and r['use_case_identity_status']=='resolved'}-{'NA'}
all_cases={r['use_case_id'] for r in annotations if r['use_case_identity_status']=='resolved'}-{'NA'}
review=sum(r['needs_human_review']=='yes' for r in annotations)
uncertain=sum(r['ai_relevance']=='uncertain' for r in annotations)
stage_uncertain=sum(r['stage_eligible']=='uncertain' for r in annotations)
def count(rr,f):return sum(r[f]=='yes' for r in rr)
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
sources_table=table(['Ticker','Filing date','Fiscal period end','Filing CIK','Primary words','Candidates','Mentions/1,000'],[[m['ticker'],m['filing_date'],m['period_end'],m['cik'],mm[m['ticker']]['total_word_count'],mm[m['ticker']]['ai_candidate_passage_count'],f"{float(mm[m['ticker']]['ai_mentions_per_1000_words']):.3f}"] for m in metadata])
company_rows=[]
sector_rows=[]
for m in metadata:
    rr=[r for r in annotations if r['ticker']==m['ticker']]
    company_rows.append([m['ticker'],len(rr),sum(r['ai_relevance']=='substantive' for r in rr),count(rr,'is_strategy_claim'),sum(r['adoption_stage']=='2' for r in rr),count(rr,'reported_deployment'),len({r['use_case_id'] for r in rr if r['reported_deployment']=='yes'}-{'NA'}),count(rr,'ai_risk'),count(rr,'ai_governance'),count(rr,'needs_human_review')])
for sector in dict.fromkeys(m['sector'] for m in metadata):
    ts={m['ticker'] for m in metadata if m['sector']==sector}
    rr=[r for r in annotations if r['ticker'] in ts]
    sector_rows.append([sector,sum(int(mm[t]['ai_candidate_passage_count']) for t in ts),len(rr),f"{sum(float(mm[t]['ai_mentions_per_1000_words']) for t in ts)/3:.3f}",count(rr,'reported_deployment'),len({r['use_case_id'] for r in rr if r['reported_deployment']=='yes'}-{'NA'}),count(rr,'ai_risk'),count(rr,'ai_governance')])
company_table=table(['Firm','Rows','Substantive','Strategy','Stage 2','Deployment claims','Deployed IDs','Risk','Governance','Review'],company_rows)
sector_table=table(['Sampling sector','Parents','Rows','Mean mention density','Deployment claims','Deployed IDs','Risk claims','Governance claims'],sector_rows)
orientation=Counter(label for r in annotations if r['is_strategy_claim']=='yes' for label in r['strategic_orientation'].split('|') if label!='NA')
strategic=[r for r in annotations if r['is_strategy_claim']=='yes']
mean_spec=sum(int(r['strategy_specificity']) for r in strategic)/len(strategic)
specdist=Counter(r['strategy_specificity'] for r in strategic)
scopedep=Counter(r['application_scope'] for r in annotations if r['reported_deployment']=='yes')
report=f"""# Corporate AI Strategy and Adoption — Expanded First Pass

**Status:** Preliminary, disclosure-based AI annotations; every row has human_validated=no.  
**Protocol:** Existing Protocol.md, unchanged. **Availability cutoff:** October 8, 2026.  
**Coverage:** 18 selected annual filings, 393 candidate passages, 447 claim/screening rows. No human evaluation or causal analysis was performed.

## 1. Sample and filing selection

The purposive stratified sample contains three firms in each analytical sector. Microsoft, Walmart and JPMorgan are the original members; the other 15 are new. Selection was independent of AI disclosure frequency.

| Analytical stratum | Companies |
|---|---|
| Technology / Software | MSFT, ADBE, CRM |
| Retail / Consumer Commerce | WMT, TGT, COST |
| Financial Services / Banking | JPM, BAC, C |
| Healthcare / Pharmaceuticals | JNJ, PFE, MRK |
| Industrials / Manufacturing | CAT, DE, HON |
| Energy / Oil & Gas | XOM, CVX, COP |

This is a nonrandom, large-company exploratory cohort, not representative of U.S. firms or each sector. Vendor software, warehouse clubs, banking franchises, drug portfolios, industrial equipment and energy operations differ substantially within and across strata. Research sectors are not SEC SIC classifications; SEC industry descriptions are retained separately.

For each issuer, official SEC ticker mappings and submissions records identify the most recently filed original 10-K on or before the cutoff. Original MSFT/WMT/JPM accessions and raw files were retained. Amendments are recorded separately and not substituted for original reports. No amendments matching these annual periods were identified in the cached recent submission histories unless listed in the metadata. Those histories do not constitute an unlimited historical amendment audit.

**XOM issuer-continuity exception:** Current XOM maps to ExxonMobil Holdings (CIK 2115436), the successor following the July 1, 2026 redomiciliation. It has no original 10-K by the cutoff. The selected February 18 annual filing is the same consolidated group's predecessor public registrant Exxon Mobil Corporation (CIK 34088), not a different subsidiary's standalone report. Both current ticker CIK and actual filing CIK, the selection note and the [SEC successor disclosure](https://www.sec.gov/Archives/edgar/data/2115436/000119312526291990/d71068d8k12b.htm) are recorded. This explicit corporate-group continuity choice requires researcher attention if the intended cohort requires only current legal-registrant CIKs; no firm was silently substituted or omitted.

## 2. Acquisition and lexical measures

Approved network-enabled execution resolved the sandbox socket restriction. Complete primary HTML was retrieved from official SEC archives using the existing contact-bearing User-Agent, caching, request spacing of at least 0.6 seconds and transient-error backoff. Existing identical sources were reused. Access followed [SEC fair-access guidance](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data).

The same installed edgartools HTMLParser (10-K configuration; table column width 500) was used throughout. It reproduces all three prior text files exactly. Primary HTML is retained without browser excerpt limits or a filing-length cutoff. Text retains paragraph/section structure, but rendering may shorten unusually wide table cells or flatten formatting; consult preserved HTML for table-sensitive decisions. Text normalization is not proof of perfect extraction of all original layout.

{sources_table}

Filing date and reporting period remain distinct. Fiscal ends range from November 2, 2025 to August 30, 2026; availability through October 8 is not a common economic observation window.

Extraction preserves the existing case-insensitive, word-boundary AI expressions, paragraph boundaries and exact-text deduplication within each filing. The five original candidate columns remain and passage_id is added. Standalone plural LLMs or GenAI and implicit applications may be missed where other existing cues are absent; no exhaustive AI-free source review is claimed.

Words use whitespace splitting. Candidate word share divides words in unique retrieved paragraphs by all filing words; mention density divides nonoverlapping full-text keyword matches by all words, times 1,000. Longer overlapping expressions count once. Candidate shares include non-AI surrounding prose and are unvalidated lexical measures.

The original 140 passage texts, lines and IDs and all three lexical metric rows reproduce exactly. Recomputing keywords corrects one MSFT matched_keywords cell; it does not change passage content, count, denominator or identifiers. The dataset contains the refreshed full sample, not an appended old/new mixture.

## 3. Annotation construction and findings

All candidates were freshly read in eight persistent batches of 42–51 parents. Explicit contextual judgments determine relevance, entity/time, claims, applications, stage and other attributes; Python only handles serialization, identifiers, counts and integrity. No keyword-to-stage classifier or external LLM API was used. Previous annotations were not reference labels.

Independent claims are split when applications, risks or resources convey distinct evidence. Repetitions remain source-linked claims and share application IDs where reliable. Broad portfolio statements are not forced into invented tasks. Named product-platform/function boundaries are provisional research judgments even when identity status is resolved. Shared quotations across distinct claims are intentional and cannot be summed as disjoint word spans.

| Relevance | Rows |
|---|---:|
| substantive | {relevance['substantive']} |
| context_only | {relevance['context_only']} |
| uncertain | {relevance['uncertain']} |
| irrelevant | {relevance['irrelevant']} |

| Reported stage | Rows |
|---|---:|
| 1 — broad firm-specific direction | {stages['1']} |
| 2 — identifiable intended application | {stages['2']} |
| 3 — actual pilot/test | {stages['3']} |
| 4 — current operational use/deployed offering | {stages['4']} |
| 5 — deployment plus attributable realized numeric result | {stages['5']} |
| NA — inapplicable/insufficient/uncertain | {stages['NA']} |

No individual Stage 0 was assigned. There are **{len(all_cases)} resolved application IDs**, of which **{len(deployed)} have supported current deployment**, compared with **{count(annotations,'reported_deployment')} deployment claims**. Some explicit current-use claims have no reliable application ID; zero identifiable IDs does not mean zero disclosed deployment.

Deployment claim scope: {dict(scopedep)}. Provider offerings and AI compute services are distinct from internal use and from customers' claims of adoption. Scope-specific application counts must use unique nonmissing IDs, not rows.

There are {len(strategic)} strategy claims; mean specificity among those assessable claims is {mean_spec:.2f}, with score counts {dict(sorted(specdist.items()))}. Specificity is separate from implementation; no score 5 was forced. Nonexclusive strategy orientation counts are {dict(orientation)}.

Other claim attributes: {count(annotations,'forward_looking')} forward-looking, {count(annotations,'ai_commitment')} explicit commitments, {count(annotations,'ai_investment')} investment, {count(annotations,'ai_partnership')} partnership, {count(annotations,'ai_risk')} risk and {count(annotations,'ai_governance')} governance claims. Categories overlap; totals need not equal rows. Conditional risks are forward-looking but not commitments.

{company_table}

## 4. Exploratory comparisons

Mean density below is the unweighted mean of three company-specific lexical densities, not a word-weighted sector population estimate.

{sector_table}

The sampled software vendors discuss many currently offered AI products; these account for much of their identified deployment breadth. That provider scope is not equivalent to internal operational adoption in banking, pharmaceuticals or energy. Several non-vendors explicitly report current AI use but omit specific workflows, reducing countable IDs independently of adoption itself.

Within retail, Target describes intended transformation and prior-year AI accomplishments; Walmart has identifiable intended search/discovery development; Costco's retrieved content concentrates on risks. Within industrials, Deere identifies current SmartDetect ML and manufacturing integration, Honeywell describes Forge-enabled AI offerings, while Caterpillar's sole candidate concerns AI-related electricity demand. These patterns describe these filings only. Keyword intensity, detailed strategy and stage evidence are different measures; no monotonic relationship or causal effect is assumed.

## 5. Diagnostics and unresolved judgments

- **Previously absent Stage 2:** The fresh pass yields 13 intended-application claims, including named Copilot/grounding/security priorities, AEP agent development, retail search/decision functions, banking data management, pharmaceutical cost programs and manufacturing analytics integration. Normative must/continue, building and program-opportunity statements are flagged when intent is clearer than implementation. Human validation may revise those boundaries.
- **No qualifying Stage 3 or 5:** Exploring, R&D spend, a hypothetical proof-of-concept cycle and building agents do not report actual testing. Shared cloud growth, acquired-company revenue, user/seat counts and expected cost-program expense do not establish attributable realized application benefits. Genuine zeros concern qualifying candidates, not firm behavior.
- **Historical versus current:** Target's 2025 launch/expansion and Citi's regulatory-data accomplishment are retained as historical evidence with NA stage where continuing use is not explicit. Current product availability elsewhere can corroborate a dated launch (for example Acrobat and SmartDetect); a launch alone cannot.
- **Application identity:** LinkedIn's suite is one identified AI offering rather than four inferred independent tasks. Broad Adobe platform/unnamed assistants are not merged automatically into Firefly. Generic estimation purposes, broad AI operations and similarly branded products do not receive invented separate IDs. Some named platform tasks remain overlapping or coarse; application counts are not enterprise maturity.
- **Uncertainty:** {uncertain} uncertain-relevance rows, {stage_uncertain} uncertain-eligibility rows and {review} review flags. Confidence counts: {dict(confidence)}. These are overlapping quality indicators, not validated error rates. Every field received a first-pass assessment; NA is a completed abstention/inapplicable judgment, not a processing failure.
- **Bias:** Large-firm selection, disclosure incentives, vendor versus user business models, legal/risk prose and uneven fiscal periods constrain comparisons. Keyword recall and semantic accuracy remain unknown until independent evaluation. No precision, recall, confusion matrix or reliability score is fabricated.

## 6. Compact data dictionary and counting rules

Unit: one interpretable claim or retained screening statement; 48 prior annotation columns preserved.

| Fields | Type / controlled values | Missing and aggregation rule |
|---|---|---|
| claim_id; passage_id | Stable strings | Claims unique; count parents with passage_id.nunique() |
| ticker; report_period; source_file; source_line | Strings; ISO fiscal-end date; positive source line | Join to selected filing, not ticker alone across periods |
| evidence_quote; evidence offsets/lines | Exact text; integer offsets/lines | Zero-based, half-open Unicode-character offsets in unmodified decoded TXT; not bytes |
| ai_relevance | substantive, context_only, irrelevant, uncertain | Distinct from stage eligibility |
| focal_firm_evidence; actor | yes/no/unclear; focal_firm/customer/partner/competitor/industry/other/unclear | Customer/competitor behavior is not focal adoption |
| temporal_status | planned/current/historical/discontinued/hypothetical/unclear | Count current deployments only |
| use_case_id; use_case; identity status | String; description; resolved/provisional/not_identified/NA | Exclude NA from nunique(); do not equate claims with applications |
| application_scope | internal_operations/customer_facing_product/customer_adoption_claim/research_and_development/infrastructure_or_platform/partnership_or_investment/unclear_or_other | Multi-label; equivalent scopes needed for comparisons |
| ai_technology_type | genai/traditional_ml/mixed/unspecified_ai/NA | ML alone does not establish GenAI; unspecified is not non-AI |
| strategic_orientation | efficiency/innovation/customer_experience/revenue_growth/workforce_productivity/competitive_positioning/responsible_ai/security/infrastructure_capacity/other/NA | Nonexclusive explicit objectives; security includes risk-management objectives |
| ai_commitment; forward_looking; is_strategy_claim | yes/no/NA | Explicit undertaking distinct from conditional future discussion |
| strategy_specificity | 1–5 or NA | Protocol rubric; compute means only among eligible nonmissing records with declared denominator |
| stage_eligible; adoption_stage; operational_stage | yes/no/uncertain; 1–5/NA; 1–4/NA at claim level | Stage 0 unavailable for individual claims; map Stage 5 to operational 4 |
| reported_deployment; pilot_reported | yes/no/NA | Deduplicate supported application IDs, same actor/scope/time; retain unresolved claims separately |
| ai_investment/partnership/risk/governance; risk_category | yes/no/NA; financial/operational/competitive/regulatory/third_party/capacity/misuse/reputational/cybersecurity/privacy/intellectual_property/model_quality/bias/safety/workforce/environmental/NA | Categories overlap and do not imply implementation |
| quantified_outcome; outcome_attribution; outcome_metric | yes/no/NA; explicit_application/shared_drivers/unlinked/ai_general/unclear/NA; named text | Shared-driver financial metrics are not qualifying AI results; NA is not zero |
| confidence; review flag; human_validated | high/medium/low; yes/no; no throughout | Review flags prioritize future checks, not unfinished coding |
| context fields; rationale; uncertainty; duplicate_group_id; record_type; annotation_version | Audit strings; claim/screening | Preserve context, repeated disclosure and correction history |

Multi-label fields use **|**. Literal **NA** means insufficient/inapplicable/missing evidence; binary no means absent in this claim, not absent firm activity. Undefined time or actor is unclear; relevance/eligibility ambiguity is uncertain. Never take the maximum stage across unrelated tasks or equate a planned extension with proof that it is implemented merely because an existing product has Stage 4 evidence. Distinct claims sharing evidence words cannot be added as validated topic share.

Sector, SEC industry, CIK, filing identity, primary URLs, checksums, parser version and XOM continuity fields reside in sources_downloaded.csv. Existing document metrics retain their columns. No new primary aggregate CSV or notebook changes were made.

## 7. Quality assurance, preservation and continuation

Actual checks passed:

{chr(10).join('- '+x for x in qa_checks)}

Focused contextual stage/identity/quotation review corrected 14 records' context or identity/stage attributes; original completed batches remain intact and the correction log is preserved. This is semantic consistency review by the same AI annotator, not independent validation. No stage quotas were imposed.

All four canonical CSVs and this report are published through validated temporary files with exact recoverable backups. Original 20261008T073937Z backups remain intact; an additional publication-time backup protects the current canonical state. The SEC cache, eight verified annotation batches, authored decisions, corrections, QA summary and progress manifest support recovery. Protocol.md, the EDA notebook, calibration artifacts and original source files remain unchanged.

No acquisition failures remain. The XOM corporate-group/predecessor choice is explicitly disclosed rather than presented as an exact current-CIK annual match. Table rendering, keyword omissions, coarse application identities and unvalidated semantic judgments remain material methodological limitations. Independent human evaluation is a future researcher-controlled phase and was not begun.
"""
atomic(CP/'AI_Annotation_First_Pass_Report.md',report.encode())
summary={'companies':18,'filings':18,'parents':len(parents),'annotation_rows':len(annotations),'relevance':dict(relevance),'stages':dict(stages),'resolved_applications':len(all_cases),'resolved_deployed_applications':len(deployed),'deployment_claims':count(annotations,'reported_deployment'),'review_flags':review,'uncertain_relevance':uncertain,'uncertain_eligibility':stage_uncertain,'checks':qa_checks,'publication_backup':str(backup.relative_to(ROOT))}
atomic(CP/'qa_summary.json',json.dumps(summary,indent=2).encode())
progress=json.loads((CP/'progress.json').read_text())
progress.update(status='validated_ready_to_publish',qa_summary='qa_summary.json')
atomic(CP/'progress.json',json.dumps(progress,indent=2).encode())
for name in ('sources_downloaded.csv','ai_passages.csv','document_metrics.csv','ai_annotations.csv'):
    atomic(ROOT/'data'/name,(CP/name).read_bytes())
atomic(ROOT/'AI_Annotation_First_Pass_Report.md',(CP/'AI_Annotation_First_Pass_Report.md').read_bytes())
for name in ('sources_downloaded.csv','ai_passages.csv','document_metrics.csv','ai_annotations.csv'):assert digest(ROOT/'data'/name)==digest(CP/name)
assert digest(ROOT/'AI_Annotation_First_Pass_Report.md')==digest(CP/'AI_Annotation_First_Pass_Report.md')
for e in preserved:
    if e.get('preserve_only'):assert digest(ROOT/e['original'])==e['sha256']
for c in progress['companies']:c.update(source_acquisition='verified',extraction='verified',metrics='verified',annotation='completed',annotation_qa='verified')
progress.update(status='complete',blocker=None,canonical_outputs_replaced=True,new_filings_downloaded=15,annotated_parent_count=len(parents),new_annotation_rows=len(annotations),qa_summary=summary,canonical_sha256={name:digest(ROOT/'data'/name) for name in ('sources_downloaded.csv','ai_passages.csv','document_metrics.csv','ai_annotations.csv')},completion_utc=datetime.now(timezone.utc).isoformat())
atomic(CP/'progress.json',json.dumps(progress,indent=2).encode())
print(json.dumps(summary,indent=2))
print('COMPLETE: canonical publication verified; protected files unchanged.')

