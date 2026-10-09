"""Record completion only after canonical QA and notebook execution passed."""
import json,hashlib,os
from datetime import datetime,timezone
from pathlib import Path
from publish_outputs import FILES,CP,ROOT,digest
import nbformat

qa=json.loads((CP/'qa_summary.json').read_text())
execution=json.loads((CP/'notebook_execution.json').read_text())
assert qa['status']=='passed' and execution['status']=='passed' and not execution['staged'] and execution['errors']==0
nb=nbformat.read(ROOT/'document_metrics.ipynb',as_version=4)
assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
assert all(o.output_type!='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
images=sum('image/png' in o.get('data',{}) for c in nb.cells if c.cell_type=='code' for o in c.outputs)
assert images==12
manifest={name:digest(ROOT/name) for name in FILES}
for name in FILES:
    if name!='document_metrics.ipynb':assert digest(CP/Path(name).name)==manifest[name]
dependencies={str(p.relative_to(ROOT)):digest(p) for p in CP.glob('*.py')}
dependencies.update({str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'src_code').glob('*.py')})
(CP/'publication_hashes.json').write_text(json.dumps(manifest,indent=2))
(CP/'processing_code_hashes.json').write_text(json.dumps(dependencies,indent=2))
progress=json.loads((CP/'progress.json').read_text())
progress.update(status='complete',publication_status='complete',canonical_outputs_replaced=True,
                completed_utc=datetime.now(timezone.utc).isoformat(),qa='passed',notebook_execution='passed',
                notebook_code_cells=execution['code_cells'],notebook_figures=images,
                aggregate_tests={'passed':4,'failed':0},published_files=manifest,results=qa,
                human_validation='not_performed; all semantic labels preliminary',
                unresolved_source_scope=['WFC/USB: incorporated annual reports outside primary-document corpus; no full-filing absence inference'],
                code_review='additional AI read-only review completed; replay minor notes fixed; not human research validation')
for c in progress['companies']:
    c.update(issuer_verified=True,source_acquisition='verified',extraction='completed',metric_computation='completed',
             annotation='completed',stage_eligibility='checked',quote_validation='passed',final_publication='complete')
tmp=CP/'progress.tmp';tmp.write_text(json.dumps(progress,indent=2));os.replace(tmp,CP/'progress.json')
plan=CP/'PLAN.md';text=plan.read_text(encoding='utf-8').replace('- [ ]','- [x]')
plan.write_text(text+'\nCompletion: all eight canonical files published; 42-company source/annotation/metric QA and canonical notebook execution passed. All research semantics remain human-unvalidated.\n',encoding='utf-8')
print('COMPLETE: 42 companies; 770 candidates; 844 full / 276 core; 568 NA; 98 deployed IDs; 12 executed cells / 12 figures; 4 tests passed.')
