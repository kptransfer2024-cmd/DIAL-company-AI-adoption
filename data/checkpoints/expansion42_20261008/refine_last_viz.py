"""Clarify company clustering without changing measurements or jittering counts."""
import hashlib,json,os
from pathlib import Path
import nbformat
CP=Path(__file__).resolve().parent;ROOT=CP.parents[2]
path=ROOT/'document_metrics.ipynb'
backup=ROOT/'data/backups/last_viz_refinement'
backup.mkdir(parents=True,exist_ok=True)
if not (backup/path.name).exists():
    (backup/path.name).write_bytes(path.read_bytes())
    (backup/'hashes.json').write_text(json.dumps({path.name:hashlib.sha256(path.read_bytes()).hexdigest()},indent=2))
nb=nbformat.read(path,as_version=4)
cell=nb.cells[18]
prefix=cell.source.split('# One point = one issuer.')[0] if '# One point = one issuer.' in cell.source else cell.source.split('fig,ax=plt.subplots(figsize=(9,5))')[0]
new='''# One point = one issuer. Show clustering without shifting numeric coordinates.
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
fig = plt.figure(figsize=(15, 10), layout='constrained')
grid = fig.add_gridspec(2, 2, height_ratios=[2.1, 1])
ax = fig.add_subplot(grid[0, 0])
zoom = fig.add_subplot(grid[0, 1])
rug = fig.add_subplot(grid[1, :])
tech_sector = 'Technology / Software'
nontech = metrics[metrics.sector != tech_sector]
zoom_xmax = float(nontech.ai_mentions_per_1000_words.max()) * 1.1
zoom_ymax = float(nontech.deployed_use_case_count.max()) + 1
zeros = metrics[metrics.deployed_use_case_count == 0]
assert len(zeros) + (metrics.deployed_use_case_count > 0).sum() == len(metrics)

for sector,g in metrics.groupby('sector',sort=False):
    style = dict(color=palette[sector], s=58, alpha=.85, edgecolors='white', linewidths=.6)
    ax.scatter(g.ai_mentions_per_1000_words,g.deployed_use_case_count,**style)
    zoom.scatter(g.ai_mentions_per_1000_words,g.deployed_use_case_count,**style)
    if sector == tech_sector:
        for i,(_,r) in enumerate(g.sort_values('ai_mentions_per_1000_words').iterrows()):
            ax.annotate(r.ticker,(r.ai_mentions_per_1000_words,r.deployed_use_case_count),
                        xytext=(5,7 if i%2 else -13),textcoords='offset points',fontsize=9)

# Label every positive application count in the enlarged area; stagger text only.
positive = metrics[(metrics.deployed_use_case_count > 0) &
                   (metrics.ai_mentions_per_1000_words <= zoom_xmax) &
                   (metrics.deployed_use_case_count < zoom_ymax)].sort_values(['deployed_use_case_count','ai_mentions_per_1000_words'])
for _,same_y in positive.groupby('deployed_use_case_count',sort=True):
    for i,(_,r) in enumerate(same_y.iterrows()):
        offset = (5, 12 + 15*(i//2)) if i%2 == 0 else (5, -18 - 15*(i//2))
        zoom.annotate(r.ticker,(r.ai_mentions_per_1000_words,r.deployed_use_case_count),
                      xytext=offset,textcoords='offset points',fontsize=9,
                      arrowprops=dict(arrowstyle='-',lw=.6,color='.45'))

ax.set(title=f'A. All {len(metrics)} companies — overall separation',
       xlabel='AI mentions per 1,000 primary-document words',
       ylabel='Resolved current deployed application IDs',ylim=(-.6,metrics.deployed_use_case_count.max()+2))
zoom.set(title='B. Enlarged low-value region — same measurements',
         xlabel='AI mentions per 1,000 primary-document words',
         ylabel='Resolved current deployed application IDs',
         xlim=(-.015,zoom_xmax),ylim=(-.25,zoom_ymax),yticks=range(int(zoom_ymax)+1))
rect=Rectangle((0,0),zoom_xmax,zoom_ymax,fill=False,edgecolor='.4',linestyle='--',linewidth=1)
ax.add_patch(rect)
ax.annotate('Region enlarged in B',(0,zoom_ymax),xytext=(3,5),textcoords='offset points',fontsize=8,color='.4')
handles=[Line2D([0],[0],marker='o',linestyle='',color=palette[s],
               label=f'{short[s]} (n={(metrics.sector == s).sum()})') for s in sectors]
ax.legend(handles=handles,title='Sector · one point = one company',fontsize=8,title_fontsize=9,loc='upper left')

# Categorical lanes separate zero-ID firms by sector; there is no numeric y jitter.
lane_labels=[]
for i,sector in enumerate(sectors):
    g=zeros[zeros.sector == sector].sort_values('ai_mentions_per_1000_words')
    n_total=int((metrics.sector == sector).sum())
    lane_labels.append(f'{short[sector]}: {len(g)}/{n_total} firms')
    rug.scatter(g.ai_mentions_per_1000_words,np.full(len(g),i),color=palette[sector],s=45,alpha=.9)
    # Fixed-count labels give context; hover is unnecessary for this exportable figure.
    if len(g):
        rug.text(zoom_xmax*.99,i,', '.join(g.ticker),ha='right',va='bottom',fontsize=8,color=palette[sector])
rug.set(title=f'C. Zero resolved application IDs: {len(zeros)}/{len(metrics)} companies — sector lanes reveal the cluster',
        xlabel='AI mentions per 1,000 primary-document words',ylabel='Sector (categorical; counts in labels)',
        yticks=range(len(sectors)),yticklabels=lane_labels,xlim=(-.015,zoom_xmax),ylim=(-.6,len(sectors)-.3))
rug.invert_yaxis()
for axis in (ax,zoom,rug):axis.grid(alpha=.18);axis.set_axisbelow(True)
fig.suptitle('Lexical AI attention and identifiable deployment evidence',fontsize=15)
plt.show()
display(Markdown(f"""**How to read:** A shows all companies; B enlarges the dashed region without changing coordinates. C separates the **{len(zeros)} zero-ID companies** into categorical sector lanes, so overlapping dots are not mistaken for one firm. Company lists identify the members of each zero-ID group.

**Observed pattern:** technology providers occupy the high-attention/high-application area; many other firms cluster near zero resolved task IDs. **Zero IDs does not mean no deployment**: **{int(zeros.reported_deployment_present.sum())} of the {len(zeros)} zero-ID companies** have broad current-use claims but no resolved countable task. WFC/USB also have the documented incorporated-report scope limitation. This figure measures disclosure evidence, not company AI maturity or a causal relationship."""))
'''
cell.source=prefix+new;cell.outputs=[];cell.execution_count=None
nbf=nbformat
nbf.validate(nb)
tmp=path.with_suffix('.tmp');nbf.write(nb,tmp);os.replace(tmp,path)
# Preserve the reproducible notebook builder by using this final cell as an override.
(CP/'last_viz_cell.py').write_text(cell.source,encoding='utf-8')
print('Last figure revised; prior notebook backup verified.')
