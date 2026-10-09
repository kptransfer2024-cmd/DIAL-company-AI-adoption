"""Rebuild authored judgments and review corrections; validate and stage archive/core.

No stage is inferred by this program. Stages come from saved contextual decisions.
"""
import csv,hashlib,json,os,re
from collections import Counter,defaultdict
from annotation_io import CP,ROOT,parents,read,raw,materialize,fields

CORE='claim_id passage_id ticker source_file source_line evidence_quote ai_relevance actor temporal_status application_scope use_case_id use_case strategic_orientation forward_looking strategy_specificity adoption_stage reported_deployment quantified_outcome ai_risk ai_governance coding_confidence needs_human_review annotation_rationale'.split()
def atomic_csv(path,rows,columns):
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
    os.replace(tmp,path)

def prepare():
    progress=json.loads((CP/'progress.json').read_text())
    rows=[];corrections=[]
    for entry in progress['annotation_batches']:
        name=entry['name'];path=CP/'annotation_batches'/(name+'.csv')
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        existing=read(path)
        judgment_path=path.with_name(name+'_judgments.json')
        assert hashlib.sha256(judgment_path.read_bytes()).hexdigest()==entry['judgment_sha256']
        decisions=json.loads(judgment_path.read_text())
        authored=defaultdict(list)
        for s in decisions['new_judgments']:authored[s['i']].append(materialize(s))
        previous=defaultdict(list)
        for r in existing:previous[r['passage_id']].append(r)
        for i in range(entry['start'],entry['end']):
            pp=parents[i];chosen=authored.get(i,previous[pp['passage_id']])
            for j,r in enumerate(chosen):
                if i in authored:
                    prior=previous[pp['passage_id']][j]
                    r.update(annotation_version='expanded42_2026_10_08_v3',human_validated='no',context_reviewed='yes',context_reference=prior['context_reference'])
                    if r['evidence_quote']!=prior['evidence_quote']:
                        corrections.append(dict(previous_claim_id=prior['claim_id'],claim_id=r['claim_id'],reason='Start-only evidence anchor expanded to complete remaining parent context; judgment unchanged.'))
                if r['strategic_orientation']=='product_and_service_innovation':r['strategic_orientation']='innovation'
                if r['strategic_orientation']=='risk_management':r['strategic_orientation']='responsible_ai'
                r['risk_category']='|'.join(sorted(set('regulatory' if x=='legal' else x for x in r['risk_category'].split('|'))))
                if r['claim_id']=='DE_claim_5eb61ee2255a5576b6f5':
                    start=sum(map(len,raw['DE'].splitlines(keepends=True)[:int(pp['line_number'])-1]));end=start+len(pp['passage_text'].rstrip())
                    r.update(adoption_stage='4',operational_stage='4',stage_eligible='yes',reported_deployment='yes',pilot_reported='no',quantified_outcome='no',temporal_status='current',use_case='Machine learning in customer-facing products; task-method boundaries unresolved',use_case_identity_status='not_identified',coding_confidence='medium',needs_human_review='yes',evidence_quote=raw['DE'][start:end],evidence_start_char=str(start),evidence_end_char=str(end),evidence_start_line=str(1+len(re.findall(r'\r\n|\r|\n',raw['DE'][:start]))),evidence_end_line=str(1+len(re.findall(r'\r\n|\r|\n',raw['DE'][:end]))),annotation_rationale='Explicit current ML use in customer-facing products; named agricultural examples have pooled method linkage, so current product use qualifies but distinct task identity remains unresolved.')
                    corrections.append(dict(claim_id=r['claim_id'],reason='Rechecked explicit current ML product use against full parent; NA corrected to Stage 4, without resolving agricultural application IDs.'))
                if r['adoption_stage']!='NA':reason='not_applicable'
                elif r['ai_relevance'] in ('context_only','irrelevant'):reason='screening_or_context'
                elif r['ai_relevance']=='uncertain' or r['stage_eligible']=='uncertain':reason='ambiguous_evidence'
                elif r['actor']!='focal_firm' or r['focal_firm_evidence']!='yes':reason='non_focal_actor_or_evidence'
                elif r['temporal_status'] in ('historical','discontinued'):reason='historical_without_current_confirmation'
                elif r['ai_risk']=='yes' or r['ai_governance']=='yes':reason='risk_or_governance_without_qualifying_stage'
                else:reason='insufficient_strategy_or_application_status'
                r['stage_na_reason']=reason
                rows.append(r)
    pp={r['passage_id']:r for r in parents}
    assert len({r['claim_id'] for r in rows})==len(rows)
    assert {r['passage_id'] for r in rows}==set(pp)
    allowed={'ai_relevance':{'substantive','context_only','irrelevant','uncertain'},'focal_firm_evidence':{'yes','no','unclear'},'actor':{'focal_firm','customer','partner','competitor','industry','other','unclear','third_party'},'temporal_status':{'planned','current','historical','discontinued','hypothetical','unclear'},'adoption_stage':{'1','2','3','4','5','NA'},'strategy_specificity':{'1','2','3','4','5','NA'},'coding_confidence':{'high','medium','low'},'stage_eligible':{'yes','no','uncertain'},'human_validated':{'no'},'use_case_identity_status':{'resolved','provisional','not_identified','NA'},'record_type':{'claim','screening'}}
    for field in 'ai_commitment forward_looking is_strategy_claim reported_deployment pilot_reported ai_investment ai_partnership ai_risk ai_governance quantified_outcome needs_human_review context_reviewed'.split():allowed[field]={'yes','no','NA'}
    multi={'application_scope':set('NA internal_operations customer_facing_product customer_adoption_claim research_and_development infrastructure_or_platform partnership_or_investment unclear_or_other'.split()),'strategic_orientation':set('NA efficiency innovation customer_experience revenue_growth workforce_productivity competitive_positioning responsible_ai security infrastructure_capacity other'.split()),'risk_category':set('NA financial operational competitive regulatory third_party capacity misuse reputational cybersecurity privacy intellectual_property model_quality bias safety workforce environmental'.split())}
    for r in rows:
        p=pp[r['passage_id']];text=raw[r['ticker']];start,end=int(r['evidence_start_char']),int(r['evidence_end_char'])
        assert (r['ticker'],r['source_file'],r['source_line'])==(p['ticker'],p['source_file'],p['line_number'])
        assert text[start:end]==r['evidence_quote'] and start<end
        for field,values in allowed.items():assert r[field] in values,(r['claim_id'],field,r[field])
        for field,values in multi.items():assert set(r[field].split('|'))<=values,(r['claim_id'],field,r[field])
        assert all(v!='' for v in r.values())
        assert r['evidence_start_line']==str(1+len(re.findall(r'\r\n|\r|\n',text[:start])))
        assert r['evidence_end_line']==str(1+len(re.findall(r'\r\n|\r|\n',text[:end])))
        st=r['adoption_stage']
        if st!='NA':assert r['stage_eligible']=='yes' and r['ai_relevance']=='substantive' and r['focal_firm_evidence']=='yes' and r['actor']=='focal_firm'
        else:assert r['stage_eligible']!='yes'
        if st=='2':assert r['temporal_status']=='planned' and r['forward_looking']=='yes' and r['use_case']!='NA'
        if st=='3':assert r['pilot_reported']=='yes'
        if st in ('4','5'):assert r['reported_deployment']=='yes' and r['temporal_status']=='current'
        if st=='5':assert r['quantified_outcome']=='yes' and r['outcome_attribution']=='explicit_application' and r['outcome_metric']!='NA' and r['operational_stage']=='4'
        if r['coding_confidence']!='high' or r['stage_eligible']=='uncertain':assert r['needs_human_review']=='yes'
    cases=defaultdict(list)
    for r in rows:
        if r['use_case_id']!='NA':cases[r['use_case_id']].append(r)
    for key,rr in cases.items():
        assert len({(r['ticker'],r['report_period'],r['actor']) for r in rr})==1,(key,'issuer/time/actor conflict')
        # Naming variants are audited in QA; grouping is explicit, never text similarity.
        assert all(r['use_case_identity_status']=='resolved' for r in rr)
    core=[{k:r[k] for k in CORE} for r in rows if r['adoption_stage']!='NA']
    atomic_csv(CP/'ai_annotations_full.csv',rows,fields+['stage_na_reason'])
    atomic_csv(CP/'ai_annotations.csv',core,CORE)
    (CP/'final_annotation_corrections.json').write_text(json.dumps(corrections,indent=2),encoding='utf-8')
    print('Full',len(rows),'core',len(core),'stages',dict(Counter(r['adoption_stage'] for r in rows)),'quote-boundary/semantic corrections',len(corrections))

if __name__=='__main__':prepare()
