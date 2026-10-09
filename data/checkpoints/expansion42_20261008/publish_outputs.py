"""Publish only validated complete snapshots, atomic per file and recoverable."""
import hashlib,json,os
from pathlib import Path
import nbformat
from validate_outputs import validate,CP,ROOT,digest
FILES=['data/sources_downloaded.csv','data/ai_passages.csv','data/document_metrics.csv','data/ai_annotations_full.csv','data/ai_annotations.csv','document_metrics.ipynb','README.md','AI_Annotation_First_Pass_Report.md']
def publish():
    validate()
    execution=json.loads((CP/'notebook_execution.json').read_text());assert execution['status']=='passed' and execution['errors']==0
    nb=nbformat.read(CP/'document_metrics.ipynb',as_version=4);nbformat.validate(nb)
    assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
    assert all(o.output_type!='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
    progress=json.loads((CP/'progress.json').read_text())
    progress.update(status='publication_in_progress',publication_status='in_progress')
    def save():
        tmp=CP/'progress.tmp';tmp.write_text(json.dumps(progress,indent=2));os.replace(tmp,CP/'progress.json')
    save()
    manifest={}
    for name in FILES:
        staged=CP/Path(name).name;target=ROOT/name
        assert staged.exists()
        tmp=target.with_name(target.name+'.tmp');tmp.write_bytes(staged.read_bytes())
        assert digest(tmp)==digest(staged);os.replace(tmp,target)
        assert digest(target)==digest(staged);manifest[name]=digest(target)
        progress.setdefault('published_files',{})[name]=manifest[name];save()
    (CP/'publication_hashes.json').write_text(json.dumps(manifest,indent=2))
    progress.update(status='published_pending_canonical_notebook_verification',canonical_outputs_replaced=True,publication_status='files_published')
    for c in progress['companies']:
        c.update(source_acquisition='verified',extraction='completed',metric_computation='completed',annotation='completed',stage_eligibility='checked',quote_validation='passed')
    save();print('All eight deliverables published; final canonical notebook execution pending.')
if __name__=='__main__':publish()
