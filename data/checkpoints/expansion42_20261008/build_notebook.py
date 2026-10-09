"""Refactor existing EDA, retaining lexical summaries, colored bars and scatter."""
import json
from pathlib import Path
import nbformat as nbf
CP=Path(__file__).resolve().parent;ROOT=CP.parents[2]
old=nbf.read(ROOT/'data/backups/expansion42_20261008/document_metrics.ipynb',as_version=4)
cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s):cells.append(nbf.v4.new_code_cell(s.strip()))
md('''# Corporate AI Disclosure EDA — 42-company expansion

Exploratory, purposive stratified sample of annual SEC primary Form 10-K documents, selected at the fixed **October 8, 2026** cutoff. All semantic coding is AI-first and **not human-validated**. This notebook separates lexical attention, strategic intent, reported implementation, and risks/governance. No enterprise maturity index, adoption truth, extraction recall, or causal effects are estimated.

Run all cells from the project root with the project virtual environment. Relative data paths are the default; `DIAL_DATA_DIR` supports testing staged replacements. Protocol.md remains the conceptual baseline.''')
code('''from pathlib import Path
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

PROJECT_ROOT = Path.cwd()
if not (PROJECT_ROOT / 'Protocol.md').exists():
    raise RuntimeError('Run this notebook with the project root as working directory.')
DATA = Path(os.environ.get('DIAL_DATA_DIR', 'data'))
sources = pd.read_csv(DATA / 'sources_downloaded.csv', keep_default_na=False)
passages = pd.read_csv(DATA / 'ai_passages.csv', keep_default_na=False)
full = pd.read_csv(DATA / 'ai_annotations_full.csv', keep_default_na=False)
core = pd.read_csv(DATA / 'ai_annotations.csv', keep_default_na=False,
                   dtype={'adoption_stage':str, 'strategy_specificity':str})
metrics = pd.read_csv(DATA / 'document_metrics.csv', keep_default_na=False)
assert sources.ticker.is_unique and metrics.ticker.is_unique
assert set(sources.ticker) == set(metrics.ticker)
assert set(passages.passage_id) == set(full.passage_id)
assert set(core.claim_id) == set(full.loc[full.adoption_stage != 'NA', 'claim_id'])
assert (full.human_validated == 'no').all()
sectors = sources.sector.drop_duplicates().tolist()
short = {s:s.split(' / ')[0] for s in sectors}
palette = dict(zip(sectors, plt.get_cmap('tab10').colors[:len(sectors)]))
plt.rcParams.update({'figure.dpi':110, 'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
def firm_plot(column, title, xlabel):
    plot_df = metrics.sort_values(column)
    fig, ax = plt.subplots(figsize=(10, max(6, len(plot_df)*.24)))
    ax.barh(plot_df.ticker, plot_df[column], color=plot_df.sector.map(palette))
    ax.set(title=title, xlabel=xlabel, ylabel='Selected issuer'); ax.grid(axis='x', alpha=.2)
    fig.tight_layout(); plt.show()
def sector_box(column, title, ylabel):
    groups = [metrics.loc[metrics.sector == s, column].to_numpy() for s in sectors]
    fig, ax = plt.subplots(figsize=(10,4.5))
    ax.boxplot(groups, tick_labels=[short[s] for s in sectors], showfliers=False)
    for i,(s,g) in enumerate(zip(sectors,groups),1):
        # Fixed offsets make plots reproducible; each dot is one company.
        ax.scatter(i + np.linspace(-.15,.15,len(g)), g, color=palette[s], s=40, alpha=.8)
    ax.set(title=title, ylabel=ylabel); ax.tick_params(axis='x', rotation=15)
    ax.grid(axis='y', alpha=.2); fig.tight_layout(); plt.show()
display(Markdown(f'Execution interpreter: `{sys.executable}`. Companies: **{len(metrics)}**.'))''')
md('''## 1 — Dataset overview

A candidate is a keyword-matching paragraph block, with meaningful original context. An archival record is a separately interpretable claim or screening decision; one candidate can produce several records. The core table includes only substantive focal-firm claims with defensible Stages 1–5. NA is an eligibility/measurement outcome, never Stage 0 or evidence of nonadoption. Resolved application IDs group repeated disclosures within the same firm/period.''')
code('''focal = full[(full.ai_relevance == 'substantive') & (full.actor == 'focal_firm') & (full.focal_firm_evidence == 'yes')]
all_cases = focal.loc[(focal.use_case_identity_status == 'resolved') & (focal.use_case_id != 'NA'), 'use_case_id'].nunique()
overview = pd.Series({'Selected companies':len(sources), 'Sectors':sources.sector.nunique(),
    'Subsectors':sources.subsector.nunique(), 'Annual filings':len(sources),
    'Candidate passages':len(passages), 'Full claim/screening records':len(full),
    'Stage-eligible core claims':len(core), 'Stage NA records':(full.adoption_stage == 'NA').sum(),
    'Resolved applications (all disclosed statuses)':all_cases,
    'Resolved current deployed applications':metrics.deployed_use_case_count.sum()}, name='Count')
display(overview.to_frame())
display(sources.groupby(['sector','subsector']).size().rename('Companies').to_frame())
display(sources[['ticker','sector','period_end','filing_date','source_scope_note']])
display(metrics.select_dtypes('number').describe().T)
display(metrics.dtypes.to_frame(name='dtype'))''')
md('''**Source scope matters.** Complete primary 10-K files were obtained for every selected issuer. WFC and USB incorporate substantial annual-report sections by reference; those separate documents are outside the uniform primary-document extraction. Their low densities and observed zeros should receive a scope sensitivity check. Fiscal year ends differ, so this is a cutoff-based snapshot rather than identical observation periods. Amazon combines commerce with AWS; GE retains the same SEC issuer after business separation. XOM uses its documented predecessor annual filing.''')
md('''## 2 — Disclosure intensity

Nonoverlapping lexical matches divided by all primary-document whitespace words, ×1,000. These are attention measures, including risks and potential false matches. Each sector box/strip plot weights its seven firms equally. The retained candidate-share scatter describes retrieval coverage; its word share includes non-AI paragraph context and is **not substantive AI topic share**.''')
code("firm_plot('ai_mentions_per_1000_words', 'AI lexical attention by issuer', 'Nonoverlapping mentions per 1,000 primary-document words')\nsector_box('ai_mentions_per_1000_words', 'Within-sector variation in lexical attention', 'Mentions per 1,000 words')")
code('''display(metrics.groupby('sector').ai_mentions_per_1000_words.agg(['count','mean','median','min','max']))
fig, ax = plt.subplots(figsize=(8,5))
for sector,g in metrics.groupby('sector',sort=False):
    ax.scatter(g.ai_mentions_per_1000_words, 100*g.ai_candidate_word_share, label=short[sector], color=palette[sector], alpha=.8)
ax.set(xlabel='AI mentions per 1,000 primary-document words', ylabel='Candidate paragraph words / document words (%)',
       title='Lexical attention and screening coverage — distinct measures')
ax.legend(fontsize=8); ax.grid(alpha=.2); fig.tight_layout(); plt.show()''')
md('''## 3 — Strategy and adoption evidence

The core denominator is eligible claims, conditional on passing stage eligibility. Stages summarize evidence statements rather than whole firms. Stage 5 requires an attributable realized numerical outcome and maps to operational Stage 4 for deployment counts; no Stage 5 claim was supported here. A provider’s deployed product is kept distinct from its internal operations and customer-adoption statements.''')
code('''stage_order = ['1','2','3','4','5']
stage_counts = core.adoption_stage.value_counts().reindex(stage_order,fill_value=0)
assert int(stage_counts.sum()) == len(core)
assert stage_counts.to_dict() == full.loc[full.adoption_stage != 'NA','adoption_stage'].value_counts().reindex(stage_order,fill_value=0).to_dict()
display(stage_counts.rename('Eligible claims').to_frame())
composition = pd.crosstab(core.ticker, core.adoption_stage).reindex(index=sources.ticker,columns=stage_order,fill_value=0).fillna(0)
assert int(composition.to_numpy().sum()) == len(core)
fig, ax = plt.subplots(figsize=(11, max(7,len(sources)*.24)))
composition.plot.barh(stacked=True,ax=ax,color=['#7e8aa2','#d8b365','#ef8a62','#4e9a83','#246155'],width=.8)
ax.set(title='Stage composition — absolute eligible claim counts',xlabel='Eligible claims (repeated evidence included)',ylabel='Issuer')
ax.legend(title='Stage',ncol=5,fontsize=8); fig.tight_layout(); plt.show()''')
code('''specificity = core.assign(specificity=pd.to_numeric(core.strategy_specificity,errors='coerce'))
cross = pd.crosstab(specificity.specificity, specificity.adoption_stage).reindex(index=range(1,6),columns=stage_order,fill_value=0).fillna(0)
assert int(cross.to_numpy().sum()) == len(core)
fig, ax = plt.subplots(figsize=(7,4.5)); im=ax.imshow(cross.to_numpy(),cmap='Blues',aspect='auto')
ax.set(xticks=range(5),xticklabels=stage_order,yticks=range(5),yticklabels=range(1,6),xlabel='Evidence stage',ylabel='Specificity score',title='Specificity and evidence stage — eligible claims')
for y in range(5):
    for x in range(5):ax.text(x,y,str(int(cross.iloc[y,x])),ha='center',va='center',color='white' if cross.iloc[y,x]>cross.to_numpy().max()/2 else 'black')
fig.colorbar(im,ax=ax,label='Claim count'); fig.tight_layout(); plt.show()
strategic = focal[focal.is_strategy_claim == 'yes']
orientation = strategic[['ticker','strategic_orientation']].assign(label=lambda d:d.strategic_orientation.str.split('|')).explode('label')
orientation = orientation[orientation.label != 'NA'].drop_duplicates(['ticker','label'])
display(orientation.groupby('label').ticker.nunique().sort_values(ascending=False).rename('Firms with strategy label').to_frame())
display(strategic.groupby('ticker').strategy_specificity.apply(lambda v:pd.to_numeric(v,errors='coerce').mean()).reindex(sources.ticker).rename('Mean explicit-strategy specificity; missing means no coded strategy').to_frame())''')
code('''resolved = focal[(focal.use_case_id != 'NA') & (focal.use_case_identity_status == 'resolved')]
current_ids = set(resolved.loc[(resolved.adoption_stage.isin(['4','5'])) & (resolved.temporal_status == 'current'),'use_case_id'])
planned_ids = set(resolved.loc[resolved.adoption_stage == '2','use_case_id'])
display(pd.Series({'Resolved intended application IDs':len(planned_ids),
    'Resolved current deployed IDs':len(current_ids), 'IDs with both planned and current evidence':len(current_ids & planned_ids),
    'Pilot claims (includes unresolved tasks)':(core.adoption_stage == '3').sum(),
    'Current deployment claims with unresolved task identity':((core.adoption_stage.isin(['4','5'])) & (core.use_case_id == 'NA')).sum()},name='Count').to_frame())
display(metrics[['ticker','distinct_ai_use_case_count','deployed_use_case_count','internal_deployed_use_case_count','customer_facing_deployed_use_case_count','reported_deployment_present']])
scoped = metrics.set_index('ticker')[['internal_deployed_use_case_count','customer_facing_deployed_use_case_count']]
fig,ax=plt.subplots(figsize=(11, max(7,len(scoped)*.24)))
scoped.plot.barh(ax=ax,color=['#386cb0','#7fc97f']); ax.set(title='Resolved current applications by deployment scope',xlabel='Distinct issuer/application IDs',ylabel='Issuer')
ax.legend(['Internal operational','Customer-facing product'],fontsize=8); fig.tight_layout(); plt.show()''')
md('''Application counts include only explicitly resolved task identities. Broad current-use claims can establish deployment presence while yielding zero resolved application IDs. Scope flags may overlap in other datasets; internal/product counts must not automatically be summed. R&D and infrastructure applications are outside those two scope counts. Products with multiple models or repeated marketing surfaces are grouped by disclosed task, not counted per model, mention, or claim.''')
md('''## 4 — Cross-sector comparisons

Default unit: one issuer/selected filing. Sector means and proportions include all selected firms, including zero observed qualifying claims. Mean claim counts are supplemental descriptions of communication; normalized counts below use primary-document words. Neither is an adoption prevalence estimate. No statistical significance tests are claimed.''')
code('''company = metrics.copy()
company['explicit_strategy_present'] = (company.strategy_claim_count > 0).astype(int)
company['risk_present'] = (company.ai_risk_claim_count > 0).astype(int)
company['governance_present'] = (company.ai_governance_claim_count > 0).astype(int)
company['eligible_claims_per_10000_words'] = company.stage_eligible_claim_count*10000/company.total_word_count
sector_summary = company.groupby('sector').agg(
    companies=('ticker','size'),mean_mentions_per_1000=('ai_mentions_per_1000_words','mean'),
    median_mentions_per_1000=('ai_mentions_per_1000_words','median'),
    strategy_firm_share=('explicit_strategy_present','mean'),deployment_evidence_firm_share=('reported_deployment_present','mean'),
    mean_resolved_deployments=('deployed_use_case_count','mean'),risk_firm_share=('risk_present','mean'),governance_firm_share=('governance_present','mean'),
    mean_eligible_claims_per_10000_words=('eligible_claims_per_10000_words','mean'))
display(sector_summary)
sector_box('deployed_use_case_count','Within-sector variation in resolved deployed applications','Resolved application IDs per selected filing')
fig,ax=plt.subplots(figsize=(9,4.5))
shares=sector_summary[['strategy_firm_share','deployment_evidence_firm_share','risk_firm_share','governance_firm_share']].copy()
shares.index=[short[s] for s in shares.index]
(shares*100).plot.barh(ax=ax); ax.set(xlabel='Selected companies with evidence (%)',title='Equal-company evidence presence by sector',xlim=(0,100))
ax.legend(['Explicit strategy','Current deployment','AI risk','AI governance'],fontsize=8,bbox_to_anchor=(1.01,1));fig.tight_layout();plt.show()''')
code('''sensitivity = company[~company.ticker.isin(['WFC','USB'])].groupby('sector').agg(companies=('ticker','size'),mean_density=('ai_mentions_per_1000_words','mean'),deployment_firm_share=('reported_deployment_present','mean'))
display(sensitivity.rename(columns={'mean_density':'Sensitivity: mean density excluding incorporated-report banks'}))
display(Markdown('This sensitivity table changes the financial-sector denominator to five; it does not repair missing incorporated text or replace the seven-company primary comparison.'))''')
md('''## 5 — Methodological diagnostics

NA rates use **all archival records per firm**; parent eligibility uses **candidate passages with at least one eligible claim / all candidate passages**. Neither is a percentage of AI words or firm adoption. `stage_na_reason` is a transparent, priority-based grouping of existing labels, not independently validated causal diagnosis. Review flags prioritize cases; unflagged rows remain human-unvalidated.''')
code('''diagnostics=full.groupby('ticker').agg(full_records=('claim_id','size'),na_records=('adoption_stage',lambda s:(s == 'NA').sum()),review_records=('needs_human_review',lambda s:(s == 'yes').sum()))
diagnostics=diagnostics.reindex(sources.ticker).fillna(0)
diagnostics['na_rate']=diagnostics.na_records/diagnostics.full_records.replace(0,np.nan)
parent_total=passages.groupby('ticker').passage_id.nunique().reindex(sources.ticker,fill_value=0)
parent_eligible=core.groupby('ticker').passage_id.nunique().reindex(sources.ticker,fill_value=0)
diagnostics['eligible_candidate_share']=parent_eligible/parent_total.replace(0,np.nan)
display(diagnostics)
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12, max(7,len(sources)*.22)))
ax1.barh(diagnostics.index,100*diagnostics.na_rate,color='#9e9ac8');ax1.set(title='NA / all archival records',xlabel='Archival records (%)',xlim=(0,100))
ax2.barh(diagnostics.index,100*diagnostics.eligible_candidate_share,color='#74c476');ax2.set(title='Candidates with eligible stage evidence',xlabel='Candidate passages (%)',xlim=(0,100))
fig.tight_layout();plt.show()
reason_counts=full.loc[full.adoption_stage == 'NA','stage_na_reason'].value_counts()
fig,ax=plt.subplots(figsize=(10,4));reason_counts.sort_values().plot.barh(ax=ax,color='#9e9ac8')
ax.set(title='NA diagnostic groups — archival records',xlabel='Records',ylabel='Priority-based diagnostic group');fig.tight_layout();plt.show()''')
code('''quality=pd.crosstab(full.coding_confidence,full.needs_human_review).reindex(index=['high','medium','low'],columns=['no','yes'],fill_value=0).fillna(0)
fig,ax=plt.subplots(figsize=(7,3.5));quality.plot.barh(stacked=True,ax=ax,color=['#a6cee3','#fb9a99'])
ax.set(title='AI confidence and human-review flags',xlabel='Full archival records',ylabel='AI confidence');ax.legend(title='Needs human review');fig.tight_layout();plt.show()
fig,ax=plt.subplots(figsize=(9,5))
for sector,g in metrics.groupby('sector',sort=False):
    ax.scatter(g.ai_mentions_per_1000_words,g.deployed_use_case_count,color=palette[sector],label=short[sector],s=45,alpha=.8)
    for _,r in g.nlargest(1,'deployed_use_case_count').iterrows():
        if r.deployed_use_case_count > 0:ax.annotate(r.ticker,(r.ai_mentions_per_1000_words,r.deployed_use_case_count),xytext=(4,4),textcoords='offset points',fontsize=8)
ax.set(title='Lexical attention versus resolved deployment evidence',xlabel='AI mentions per 1,000 primary-document words',ylabel='Resolved current deployed application IDs')
ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();plt.show()''')
md('''## 6 — Preliminary insights and limitations

The following summaries are computed from the loaded snapshot. They concern disclosed evidence, not independently verified corporate adoption. Sector differences may reflect provider business models, source scope, filing length, and disclosure conventions; these are hypotheses for future validation.''')
code('''tech = sector_summary.loc['Technology / Software']
other = sector_summary.drop(index='Technology / Software')
na_count=(full.adoption_stage == 'NA').sum()
display(Markdown(f"""- Technology firms have mean lexical density **{tech.mean_mentions_per_1000:.3f}** mentions/1,000 words, versus **{other.mean_mentions_per_1000.min():.3f}–{other.mean_mentions_per_1000.max():.3f}** for the other sector means. Product-provider scope is prominent; this is not an internal-adoption ranking.
- **{metrics.reported_deployment_present.sum()} of {len(metrics)}** selected primary filings contain coded current deployment evidence. **{metrics.deployed_use_case_count.sum()}** resolved deployed application IDs were identified; broad current-use claims often do not identify countable tasks.
- **{na_count}/{len(full)} ({100*na_count/len(full):.1f}%)** archival records are NA; risk/governance without qualifying stage is the largest priority-based group. **{(metrics.stage_eligible_claim_count == 0).sum()}** firms have zero observed eligible claims, with no firm-level Stage 0 or nonadoption inference.
- Human validation remains pending for **all {len(full)} records**, including the **{(full.needs_human_review == 'yes').sum()}** flagged for priority review. No extraction accuracy, classification accuracy or inter-coder reliability estimate exists.
"""))
display(Markdown('Future work: independently code a stratified candidate/nonmatching reference set; adjudicate actor, task identity, pilot and deployment thresholds; evaluate extraction recall separately; examine incorporated reports under an explicitly expanded source scope; and test business-model/period sensitivity. Human-validated topic/word shares, vague maturity scores and causal outcome analysis are deferred.'))''')
nb=nbf.v4.new_notebook(cells=cells,metadata=dict(old.metadata))
if (CP/'last_viz_cell.py').exists():
    nb.cells[18].source=(CP/'last_viz_cell.py').read_text(encoding='utf-8')
nb.metadata['kernelspec']={'display_name':'Python 3 (project .venv)','language':'python','name':'python3'}
nb.metadata['dial_revision']={'baseline_notebook_sha256':'43c88334a73778ddf07187ba7a263f57295e5c869248ceb82faf37819f71eddf','retained_analyses':['numeric summary','dtype inspection','sector-colored issuer bars','lexical attention / candidate-coverage scatter'],'semantic_validation':'AI-first; human-unvalidated'}
nbf.validate(nb);nbf.write(nb,CP/'document_metrics.ipynb')
print('Staged notebook:',len(cells),'cells;',sum(c.cell_type=='code' for c in cells),'code cells')
