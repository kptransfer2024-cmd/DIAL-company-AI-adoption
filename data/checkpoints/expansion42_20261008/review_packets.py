"""Inspect every AI-bearing sentence with adjacent context; full parents remain cached."""
import sys,re,json
from pathlib import Path
from annotation_io import parents,read,ROOT,CP
old={}
for r in read(ROOT/'data/ai_annotations.csv'):old.setdefault(r['passage_id'],[]).append(r)
def packet(i,full=False):
    p=parents[i];text=p['passage_text']
    # Display all retrieval hits with sentence neighbours, without semantic filtering.
    sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z“"(])',text)
    hits={j for j,s in enumerate(sentences) if re.search(r'\b(?:AI|artificial\s+intelligence|machine\s+learning|LLM|copilot)\b',s,re.I)}
    keep={k for j in hits for k in (j-1,j,j+1) if 0<=k<len(sentences)}
    context=text if full or not hits else '\n[...]\n'.join(s for j,s in enumerate(sentences) if j in keep)
    print(f'\n### {i} {p["ticker"]} L{p["line_number"]} ({len(text)} chars)\n'+context)
    for r in old.get(p['passage_id'],[]):
        print('PRIOR AUDIT',json.dumps({k:r[k] for k in ('adoption_stage','temporal_status','application_scope','use_case_id','use_case','annotation_rationale','ai_risk','ai_governance')},ensure_ascii=False))
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for i in range(int(sys.argv[1]),min(int(sys.argv[2]),len(parents))):packet(i,'--full' in sys.argv)
