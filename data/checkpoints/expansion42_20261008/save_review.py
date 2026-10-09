"""Persist explicit contextual reviews and new judgments, validating each batch."""
import json,sys,hashlib,os,csv
from annotation_io import CP,ROOT,parents,read,materialize,fields,raw
old={}
for r in read(ROOT/'data/backups/expansion42_20261008/data/ai_annotations.csv'):old.setdefault(r['passage_id'],[]).append(r)
def save(name,start,end,judgments,changes=None):
    batch=CP/'annotation_batches';batch.mkdir(exist_ok=True)
    path=batch/(name+'.csv');assert not path.exists()
    specs={}
    for s in judgments:specs.setdefault(s['i'],[]).append(s)
    rows=[];log=[]
    for i in range(start,end):
        p=parents[i]
        if i in specs:rr=[materialize(s) for s in specs[i]];decision='fresh contextual judgments'
        else:
            assert p['passage_id'] in old,('Missing authored judgment',i)
            rr=[r.copy() for r in old[p['passage_id']]];decision='prior claims rechecked against AI-bearing sentences and adjacent source context; retained unless changed explicitly'
            for r in rr:
                r.update((changes or {}).get(r['claim_id'],{}))
        for r in rr:
            r['annotation_version']='expanded42_2026_10_08_v3'
            r['human_validated']='no'
            r['context_reviewed']='yes'
            r['context_reference']=p['source_file']+':L'+p['line_number']+'; contextual batch '+name
            assert raw[r['ticker']][int(r['evidence_start_char']):int(r['evidence_end_char'])]==r['evidence_quote']
            assert r['adoption_stage'] in ('1','2','3','4','5','NA')
            if r['adoption_stage']!='NA':assert r['ai_relevance']=='substantive' and r['actor']=='focal_firm' and r['stage_eligible']=='yes'
            if r['adoption_stage'] in ('4','5'):assert r['temporal_status']=='current'
        rows.extend(rr);log.append({'index':i,'passage_id':p['passage_id'],'decision':decision})
    previous=[r for f in batch.glob('*.csv') for r in read(f)]
    assert not ({r['passage_id'] for r in previous}&{r['passage_id'] for r in rows})
    assert len({r['claim_id'] for r in rows+previous})==len(rows+previous)
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    assert read(tmp)==rows
    os.replace(tmp,path)
    (batch/(name+'_judgments.json')).write_text(json.dumps({'start':start,'end':end,'new_judgments':judgments,'changes':changes or {},'contextual_reviews':log},indent=2,ensure_ascii=False),encoding='utf-8')
    progress=json.loads((CP/'progress.json').read_text())
    progress.update(status='annotation_in_progress',annotated_parent_count=len({r['passage_id'] for r in previous+rows}),annotation_rows=len(previous+rows))
    progress.setdefault('annotation_batches',[]).append({'name':name,'start':start,'end':end,'parent_count':end-start,'claim_count':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'judgment_sha256':hashlib.sha256((batch/(name+'_judgments.json')).read_bytes()).hexdigest(),'quote_validation':'passed'})
    tmp=CP/'progress.tmp';tmp.write_text(json.dumps(progress,indent=2));os.replace(tmp,CP/'progress.json')
    print(name,'saved',end-start,'parents;',len(rows),'records;',progress['annotated_parent_count'],'parents complete')
if __name__=='__main__':
    d=json.loads(__import__('pathlib').Path(sys.argv[1]).read_text(encoding='utf-8'));save(**d)
