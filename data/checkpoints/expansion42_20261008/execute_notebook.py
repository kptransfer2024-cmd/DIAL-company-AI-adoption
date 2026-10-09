"""Execute with the current project interpreter; fail on any notebook error."""
import json,os,sys,time
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
CP=Path(__file__).resolve().parent;ROOT=CP.parents[2]
staged='--staged' in sys.argv
os.environ['IPYTHONDIR']=str(CP/'ipython')
os.environ['JUPYTER_RUNTIME_DIR']=str(CP/'jupyter_runtime')
if staged:os.environ['DIAL_DATA_DIR']=str(CP)
else:os.environ.pop('DIAL_DATA_DIR',None)
kernel=CP/'kernels/dial-project';kernel.mkdir(parents=True,exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'DIAL project .venv','language':'python'}))
manager=KernelManager(kernel_name='dial-project',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel.parent)]))
path=CP/'document_metrics.ipynb' if staged else ROOT/'document_metrics.ipynb'
nb=nbformat.read(path,as_version=4);start=time.time()
NotebookClient(nb,km=manager,timeout=180,allow_errors=False,resources={'metadata':{'path':str(ROOT)}}).execute()
assert all(o.output_type!='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
tmp=path.with_suffix('.tmp');nbformat.write(nb,tmp);os.replace(tmp,path)
report=dict(status='passed',staged=staged,interpreter=sys.executable,code_cells=sum(c.cell_type=='code' for c in nb.cells),total_cells=len(nb.cells),errors=0,elapsed_seconds=round(time.time()-start,2))
(CP/'notebook_execution.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
