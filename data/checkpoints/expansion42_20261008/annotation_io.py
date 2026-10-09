"""Materialize explicitly authored AI judgments; no semantic keyword classifier."""
import csv,json,hashlib,re,os,sys
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3]
CP=Path(__file__).resolve().parent
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
parents=read(CP/'ai_passages.csv')
meta={r['ticker']:r for r in read(CP/'sources_downloaded.csv')}
# The canonical file becomes the reduced core table after publication.
fields=list(read(ROOT/'data/backups/expansion42_20261008/data/ai_annotations.csv')[0])
raw={}
for t,m in meta.items():
    with (ROOT/'data/raw'/m['source_file']).open(encoding='utf-8',newline='') as f:raw[t]=f.read()
offsets={}
for p in parents:
    offset=sum(map(len,raw[p['ticker']].splitlines(keepends=True)[:int(p['line_number'])-1]))
    assert raw[p['ticker']].startswith(p['passage_text'],offset)
    offsets[p['passage_id']]=offset
def span(p,s):
    text=p['passage_text'];base=offsets[p['passage_id']]
    if 'q' not in s:return base,base+len(text.rstrip())
    # Normalize whitespace for anchors, then map back to exact source characters.
    norm=[];mapping=[]
    for i,c in enumerate(text):
        if c.isspace():
            if not norm or norm[-1]!=' ':norm.append(' ');mapping.append(i)
        else:norm.append(c);mapping.append(i)
    norm=''.join(norm)
    q=' '.join(s['q'].split());a=norm.find(q);assert a>=0,(s['i'],q)
    # A start-only anchor selects the remaining context, not merely its words.
    b=len(norm.rstrip()) if not s.get('end') else a+len(q)
    if s.get('end'):
        e=' '.join(s['end'].split());j=norm.find(e,b);assert j>=0,(s['i'],e)
        b=j if s.get('before') else j+len(e)
    return base+mapping[a],base+mapping[b-1]+1
def materialize(s):
    p=parents[s['i']];t=p['ticker'];start,end=span(p,s)
    quote=raw[t][start:end]
    r={k:'NA' for k in fields}
    substantive=s.get('r','substantive')=='substantive'
    stage=str(s.get('st','NA'))
    r.update(claim_id=t+'_claim_'+hashlib.sha256((p['passage_id']+'\0'+str(start)+'\0'+str(end)+'\0'+s.get('uc','')+'\0'+s['n']).encode()).hexdigest()[:20],passage_id=p['passage_id'],ticker=t,report_period=meta[t]['period_end'],source_file=p['source_file'],source_line=p['line_number'],evidence_quote=quote,ai_relevance=s.get('r','substantive'),focal_firm_evidence=s.get('firm','yes'),actor=s.get('actor','focal_firm'),temporal_status=s.get('tmp','current'),use_case_id=(t+'_uc_'+s['uc']) if s.get('uc') else 'NA',use_case=s.get('use','NA'),use_case_identity_status=s.get('identity','resolved' if s.get('uc') else 'not_identified' if s.get('use') else 'NA'),application_scope=s.get('scope','unclear_or_other' if substantive else 'NA'),ai_technology_type=s.get('tech','unspecified_ai' if substantive else 'NA'),strategic_orientation=s.get('o','NA'),ai_commitment=s.get('c','no' if substantive else 'NA'),forward_looking=s.get('f','no' if substantive else 'NA'),is_strategy_claim=s.get('strategy','no' if substantive else 'NA'),strategy_specificity=str(s.get('sp',2)) if substantive else 'NA',adoption_stage=stage,operational_stage='4' if stage=='5' else stage,stage_eligible=s.get('elig','yes' if stage!='NA' else 'no'),reported_deployment='yes' if stage in ('4','5') else 'no' if stage in ('2','3') else 'NA',pilot_reported='yes' if stage=='3' else 'no' if stage in ('2','4','5') else 'NA',ai_investment=s.get('inv','no' if substantive else 'NA'),ai_partnership=s.get('partner','no' if substantive else 'NA'),ai_risk='yes' if s.get('risk') else 'no' if substantive else 'NA',risk_category=s.get('risk','NA'),ai_governance=s.get('gov','no' if substantive else 'NA'),quantified_outcome=s.get('outcome','yes' if stage=='5' else 'no' if stage!='NA' else 'NA'),outcome_attribution=s.get('attr','NA'),outcome_metric=s.get('metric','NA'),coding_confidence=s.get('conf','high'),needs_human_review=s.get('review','yes' if s.get('r')=='uncertain' or s.get('conf') in ('medium','low') or stage=='5' or s.get('elig')=='uncertain' else 'no'),annotation_rationale=s['n'],uncertainty_reason=s.get('u','NA'),human_validated='no',context_reviewed=s.get('ctx','no'),context_reference=s.get('ctxref',p['source_file']+':L'+p['line_number']+' (full parent/context)' if s.get('ctx')=='yes' else 'NA'),evidence_start_char=str(start),evidence_end_char=str(end),evidence_start_line=str(1+len(re.findall(r'\r\n|\r|\n',raw[t][:start]))),evidence_end_line=str(1+len(re.findall(r'\r\n|\r|\n',raw[t][:end]))),duplicate_group_id=s.get('dup','NA'),record_type='claim' if substantive else 'screening',annotation_version='expanded_2026_10_08_v2')
    for key in ('application_scope','strategic_orientation','risk_category'):
        r[key]='|'.join(sorted(set(r[key].split('|'))))
    assert quote==raw[t][start:end] and quote
    if stage!='NA':
        assert substantive and r['stage_eligible']=='yes' and r['focal_firm_evidence']=='yes' and r['actor']=='focal_firm'
    if stage in ('4','5'):assert r['temporal_status']=='current'
    if stage=='5':assert r['outcome_attribution']=='explicit_application' and r['outcome_metric']!='NA'
    if not substantive:assert stage=='NA'
    return r
def _legacy_save_batch(name,specs):
    batch=CP/'annotation_batches';batch.mkdir(exist_ok=True)
    original=batch/(name+'_judgments.json')
    path=batch/(name+'.csv')
    assert not original.exists() and not path.exists(),'Never overwrite verified batch'
    rr=[materialize(s) for s in specs]
    assert len({r['claim_id'] for r in rr})==len(rr)
    covered=sorted(set(s['i'] for s in specs))
    assert covered==list(range(min(covered),max(covered)+1)),covered
    all_previous=[]
    for old in batch.glob('*.csv'):all_previous.extend(read(old))
    assert not ({r['passage_id'] for r in rr}&{r['passage_id'] for r in all_previous})
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
    assert read(tmp)==rr
    original.write_text(json.dumps(specs,indent=2,ensure_ascii=False),encoding='utf-8')
    os.replace(tmp,path)
    progress=json.loads((CP/'progress.json').read_text())
    entries=progress.setdefault('annotation_batches',[])
    entries.append({'file':str(path.relative_to(ROOT)),'parent_start':min(covered),'parent_end':max(covered),'parent_count':len(covered),'claim_count':len(rr),'source_quote_qa':'passed','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    done={r['passage_id'] for r in all_previous+rr}
    for c in progress['companies']:
        pp={p['passage_id'] for p in parents if p['ticker']==c['ticker']}
        c['annotation']='completed' if pp<=done else 'in_progress' if pp&done else 'pending'
        c['annotation_qa']='source_quotes_verified' if pp<=done else 'pending'
    progress.update(status='annotation_in_progress',annotated_parent_count=len(done),new_annotation_rows=len(all_previous)+len(rr))
    tmp=CP/'progress.tmp';tmp.write_text(json.dumps(progress,indent=2),encoding='utf-8');os.replace(tmp,CP/'progress.json')
    print(name,'saved',len(covered),'parents',len(rr),'claims; total parents',len(done),flush=True)
def save_batch(name,specs):
    """Use the same progress/decision schema as contextual review batches."""
    from save_review import save
    covered=sorted(set(s['i'] for s in specs))
    assert covered==list(range(min(covered),max(covered)+1))
    save(name,min(covered),max(covered)+1,specs)

if __name__=='__main__':
    specs=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    save_batch(sys.argv[1],specs)

