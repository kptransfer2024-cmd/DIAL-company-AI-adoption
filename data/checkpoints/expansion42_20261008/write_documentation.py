"""Actual-result report, field assessment and metric definitions; no new data tables."""
import csv,json,sys
from pathlib import Path
from collections import Counter
import pandas as pd
CP=Path(__file__).resolve().parent;ROOT=CP.parents[2]
q=json.loads((CP/'qa_summary.json').read_text());env=json.loads((CP/'processing_environment.json').read_text())
src=pd.read_csv(CP/'sources_downloaded.csv',keep_default_na=False)
full=pd.read_csv(CP/'ai_annotations_full.csv',keep_default_na=False)
core=pd.read_csv(CP/'ai_annotations.csv',keep_default_na=False)
m=pd.read_csv(CP/'document_metrics.csv',keep_default_na=False)
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(v).replace('|',' / ').replace('\n',' ') for v in row)+' |' for row in rows)
sample=table(['Sector','Retained companies','Added companies'],[[s,', '.join(g.ticker.iloc[:3]),', '.join(g.ticker.iloc[3:])] for s,g in src.groupby('sector',sort=False)])
sectors=m.groupby('sector',sort=False).agg(firms=('ticker','size'),mean_density=('ai_mentions_per_1000_words','mean'),median_density=('ai_mentions_per_1000_words','median'),deployment_firms=('reported_deployment_present','sum'),deployments=('deployed_use_case_count','sum'),risk=('ai_risk_claim_count','sum'),governance=('ai_governance_claim_count','sum'))
sector_table=table(['Sector','Firms','Mean lexical density','Median lexical density','Firms with deployment evidence','Resolved deployed IDs','Risk records','Governance records'],[[s,r.firms,f'{r.mean_density:.3f}',f'{r.median_density:.3f}',r.deployment_firms,r.deployments,r.risk,r.governance] for s,r in sectors.iterrows()])
source_table=table(['Ticker','Subsector','CIK','Filing date','Period end','Words','Candidates','Eligible claims','Resolved deployed IDs'],[[r.ticker,r.subsector,r.cik,r.filing_date,r.period_end,int(m.set_index('ticker').loc[r.ticker].total_word_count),int(m.set_index('ticker').loc[r.ticker].ai_candidate_passage_count),int(m.set_index('ticker').loc[r.ticker].stage_eligible_claim_count),int(m.set_index('ticker').loc[r.ticker].deployed_use_case_count)] for _,r in src.iterrows()])
core_fields=core.columns.tolist()
descriptions={
'claim_id':'Evidence-statement identity; required for full/core audit join.',
'passage_id':'Stable parent identity and one-to-many extraction traceability.',
'ticker':'Sampled issuer key; industry metadata joins through sources.',
'report_period':'Fiscal scope; archival join metadata duplicates source period.',
'source_file':'Exact cached primary-text identity.',
'source_line':'One-based parent start location; finer quote lines retained in archive.',
'evidence_quote':'Exact source span; indispensable source-grounding, not a model variable.',
'ai_relevance':'Separates substantive evidence, context, false positives and uncertainty.',
'focal_firm_evidence':'Eligibility safeguard; redundant in filtered core, vital in archive.',
'actor':'Separates firm, provider/customer, competitor and third-party claims.',
'temporal_status':'Distinguishes intended, current, historical and hypothetical evidence.',
'use_case_id':'Resolved issuer/task identity used for deduplication; unresolved excluded from ID counts.',
'use_case':'Readable task description; allows unresolved boundaries without invented IDs.',
'use_case_identity_status':'Resolved/provisional/unidentified guardrail; core NA IDs plus rationale retain abstention.',
'application_scope':'Nonexclusive internal/product/customer/R&D/infrastructure/investment scope.',
'ai_technology_type':'Supporting subtype; terminology often generic, excluded from primary comparisons.',
'strategic_orientation':'Nonexclusive objectives; meaningful strategy dimension, no forced maturity score.',
'ai_commitment':'Detailed speech-act field overlaps plans/intent; sparse distinct commitments retained for audit.',
'forward_looking':'Future framing distinct from temporal status and actual implementation.',
'is_strategy_claim':'Explicit objective flag for reproducible strategy aggregation; retained archival guardrail.',
'strategy_specificity':'Protocol informational-detail score, independent of evidence stage; preliminary ordinal coding.',
'adoption_stage':'Evidence threshold 1–5 or NA; core conditions on eligibility.',
'operational_stage':'Derived 5→4 mapping; redundant archival field, derivable for core.',
'stage_eligible':'Full screening safeguard; constant yes in core, omitted there.',
'reported_deployment':'Current-use indicator; retained interpretability even though closely linked to 4/5.',
'pilot_reported':'Detailed evidence check; redundant with Stage 3 in main analysis, retained audit.',
'ai_investment':'Supporting resource dimension; spending alone not implementation.',
'ai_partnership':'Supporting relationship dimension; partnership alone not deployment.',
'ai_risk':'Independent disclosure dimension, computed from full including NA.',
'risk_category':'Detailed nonexclusive taxonomy; compact main risk flag preferred pending validation.',
'ai_governance':'Actual focal controls/oversight dimension; kept separately from adoption.',
'quantified_outcome':'Supplementary realized numeric outcome flag; scale/revenue alone insufficient.',
'outcome_attribution':'Stage 5 attribution safeguard; few outcomes, retained in audit not discarded.',
'outcome_metric':'Evidence details and baseline/period caveats for audit; sparse outcome data.',
'coding_confidence':'AI self-assessed confidence, not classification accuracy.',
'needs_human_review':'Priority flag; all rows require independent validation regardless of flag.',
'annotation_rationale':'Brief contextual justification and boundaries; required in core.',
'uncertainty_reason':'Detailed ambiguity audit; priority NA grouping does not replace it.',
'human_validated':'Constant no in this pass; retained full, prominent dataset-level core documentation.',
'context_reviewed':'Constant yes after candidate-context review; audit execution state.',
'context_reference':'Context source and batch audit; duplicates provenance in compact core.',
'evidence_start_char':'Exact raw-text character offset; quotation integrity audit.',
'evidence_end_char':'Exclusive quote offset; quotation integrity audit.',
'evidence_start_line':'Finer one-based quote start; source_line remains parent start.',
'evidence_end_line':'Finer quote end; archival precise-span recovery.',
'duplicate_group_id':'Optional duplicate flag; resolved use-case IDs are primary aggregation basis.',
'record_type':'Claim versus screening; mostly redundant with relevance, useful audit.',
'annotation_version':'Run provenance; preserved audit and checkpoint manifests.'}
assert set(descriptions)==set(full.columns)-{'stage_na_reason'}
field_table=table(['Original field','Core or audit','Non-NA values / 844','Research role / decision'],[[f,'Core' if f in core_fields else 'Audit',int((full[f].astype(str)!='NA').sum()),descriptions[f]] for f in full.columns if f!='stage_na_reason'])
metric_rows=[
('total_word_count','Document','All whitespace-split primary-text words','Words; no denominator','Raw text'),
('ai_mention_count','Document','Nonoverlapping longest-first keyword matches','Matches; no denominator','Raw text / extraction patterns'),
('ai_mentions_per_1000_words','Document','1000 × mentions / total words','Matches per 1,000 primary words','Raw lexical counts'),
('ai_candidate_passage_count','Document','Retrieved exact-text-deduplicated matching blocks','Candidates; no denominator','ai_passages'),
('ai_candidate_word_count','Document','Sum of whitespace words across candidate blocks','Candidate-context words','ai_passages.passage_text'),
('ai_candidate_word_share','Document','Candidate words / all primary-document words','Fraction; screening measure only','Candidate / total words'),
('substantive_ai_claim_count','Document','All archived substantive records, including risk and NA','Records; no denominator','full.ai_relevance'),
('strategy_claim_count','Document','Substantive focal-firm records explicitly coded strategy','Records; no denominator; repeated statements included','full.is_strategy_claim + actor/focal guards'),
('stage_eligible_claim_count','Document','Substantive focal-firm eligible Stages 1–5','Records; no denominator; equals core issuer count','full stage/relevance/actor/eligibility'),
('stage_na_claim_count','Document','All archival records with adoption_stage=NA','Records; no denominator; not nonadoption','full.adoption_stage'),
('distinct_ai_use_case_count','Issuer/task/period → document','Unique resolved substantive focal IDs across all disclosed statuses','Distinct IDs; no denominator; includes planned/historical','full.use_case_id + identity/actor/relevance'),
('deployed_use_case_count','Issuer/task/period → document','Unique resolved focal IDs with current 4/5 and reported deployment','Distinct IDs; no denominator; repetitions count once','full stages/temporal/identity/deployment'),
('internal_deployed_use_case_count','Issuer/task/period → document','Deployed IDs with explicit internal_operations scope','Distinct IDs; may overlap other scope counts','Full deployed IDs / scope'),
('customer_facing_deployed_use_case_count','Issuer/task/period → document','Deployed IDs with explicit customer_facing_product scope','Distinct IDs; provider products, not customer/internal adoption','Full deployed IDs / scope'),
('reported_deployment_present','Document','At least one qualifying current 4/5 record, including unresolved tasks','Binary 0/1; zero means none observed in reviewed candidates','Full eligible deployed records'),
('ai_risk_claim_count','Document','All substantive archived records with AI risk=yes, including NA','Records; no denominator','full.ai_relevance + ai_risk'),
('ai_governance_claim_count','Document','All substantive archived records with AI governance=yes, including NA','Records; no denominator','full.ai_relevance + ai_governance'),
('semantic_review_status','Document','Candidate review complete; full-document absence unassessed','Review scope label; not maturity/adoption','Checkpoint coverage'),
('Explicit strategy presence (notebook)','Document/sector','strategy_claim_count>0; sector average across all seven issuers','Binary / equal-firm fraction','Full-derived metrics'),
('Strategy specificity (notebook)','Claim/issuer','Protocol score; issuer mean across explicit strategy records','Ordinal score / arithmetic descriptive mean, no weighting as maturity','full strategy flag + strategy_specificity'),
('Concrete intended application evidence (notebook)','Claim / issuer-task','Stage 2 records and unique resolved Stage 2 IDs shown separately','Claims or IDs, explicitly labeled; no denominator','Core stage + use_case_id'),
('Stage composition (notebook)','Claim','Eligible Stage 1–5 counts','Core claims; percentages if used divide eligible claims only','Core adoption_stage'),
('Eligible claims per 10,000 words (notebook)','Document / sector','10000 × eligible claims / primary words; sector mean across firms','Records per 10,000 words; preliminary','Metrics stage_eligible / total_word_count'),
('Stage NA rate (notebook)','Document','NA archival records / all archival records for issuer','Fraction of archived records, not firms or words','Full adoption_stage'),
('Eligible candidate share (notebook)','Document','Candidates with ≥1 core record / all candidates','Fraction of candidate passages, not topic share','Unique core passage IDs / ai_passages'),
('Risk/governance presence (notebook)','Document / sector','Count>0; average binary indicators across selected firms','Equal-company fraction; not overall adoption prevalence','Full-derived risk/governance counts'),
('Confidence and review flags (notebook)','Archival record','Self-confidence category and needs-review flag counts','All archived records; no accuracy denominator','Full coding_confidence / needs_human_review'),
('Stage NA reason (archive/notebook)','Archival record','Priority grouping of existing relevance/eligibility/actor/time/risk/control labels','NA records; diagnostic label, not validated causal explanation','Full stage_na_reason')]
metric_table=table(['Metric','Unit of observation','Definition','Unit / denominator','Source'],metric_rows)
na_table=table(['Priority diagnostic group','NA records'],q['stage_na_reasons'].items())
report=f'''# DIAL corporate AI strategy/adoption — 42-company first pass

**Status:** Complete primary-document workflow; preliminary AI-first semantic annotations, **human_validated=no for every record**. Fixed filing cutoff: **October 8, 2026**. Protocol.md is unchanged and remains the conceptual baseline. This report documents practical measurement refinements separately.

## Actual results

42 issuers, six sectors, seven firms each; 42 selected original annual filings. All 18 existing sources and 393 existing candidate IDs remain intact. The 24 additional companies contribute 377 new candidates, giving **770 candidates**, **844 full claim/screening records**, and **276 eligible core claims**. **568 records (67.30%)** remain Stage NA in the archive. Stages: **1=79, 2=15, 3=1, 4=181, 5=0**. No passage-level Stage 0 is used.

**109 resolved focal application IDs** occur across all disclosed statuses; **98** have current deployed evidence: **10 internal operations, 83 customer-facing products, and 5 other (R&D/infrastructure)**. Internal/product IDs do not overlap in this snapshot. Twenty-nine filings have coded current deployment evidence, including broad claims without identifiable applications. Eight filings have zero observed eligible claims; this is not nonadoption or an adequately reviewed full-document Stage 0.

## Sampling and acquisition

The existing large-company purposive stratification was extended without selecting firms for AI disclosure content. No substitutions or silent sample reductions occurred. Original sector names were retained for compatibility; financial and industrial subsectors are now explicit. Amazon's commerce/AWS distinction, energy upstream/services/downstream distinctions, and GE business continuity are recorded in metadata.

{sample}

Official SEC ticker/CIK metadata and submissions were used. The newest **original 10-K**, excluding amendments as the primary source, filed on/before the fixed cutoff was selected. Filing dates, period ends, accessions, primary/index URLs, amendments, parser versions and text/HTML SHA-256 checksums remain in sources_downloaded.csv. Existing verified filings were reused unchanged. All new requests used the established contact-bearing User-Agent, paced acquisition, cached results and the approved Windows network-access route. No post-cutoff filing was selected.

### Identity and scope exceptions

- **XOM:** current ticker CIK 2115436 succeeded predecessor CIK 34088 after the July 1, 2026 redomiciliation. The retained February 18, 2026 annual filing is the latest qualifying original consolidated-group 10-K under the predecessor. The previously verified continuity exception and [successor SEC disclosure](https://www.sec.gov/Archives/edgar/data/2115436/000119312526291990/d71068d8k12b.htm) remain documented; no successor original 10-K was substituted.
- **GE:** current GE Aerospace operations report under continuing General Electric registrant **CIK 40545**, not GE Vernova. The [selected annual filing](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/ge-20251231.htm) documents the post-separation business. SEC issuer name and SIC were preserved rather than rewritten as a different registrant.
- **WFC and USB:** complete primary 10-Ks were obtained, but substantial annual-report sections are incorporated by reference from separate documents. Those incorporated documents are outside the consistent primary-document corpus. Low lexical density and zero qualifying claims cannot establish complete-filing absence. WFC's multipart iXBRL primary lacks standalone CIK/resources: official submission/URL identity plus cover registrant, form and fiscal-period tags were verified. This is an explicit source-scope limitation, not failed acquisition. The notebook includes a financial-sector sensitivity table excluding these two issuers, with its changed denominator labeled.

## Extraction and contextual annotation

The existing `2_extract_ai.py` rules run unchanged across all 42 cached texts: nonblank-line blocks, case-insensitive boundary-based keywords, whitespace-flexible multiword matches, longest-first nonoverlapping mention counting, and exact block deduplication within each filing. Paragraph text, starting lines, matched keywords and deterministic source-based passage IDs are preserved. Risk, governance, competitors, uncertainty and hypothetical content remain candidates. Keyword retrieval does not assign semantic stages.

All 770 parents were contextually reviewed in 16 persistent batches (normally 50 parents; boundaries of 51 and a final 19 are documented). Source packets include AI-bearing sentences and neighboring context, with complete parents retained for ambiguity review and exact source lookup. Earlier labels were audit references: old candidates were rechecked against contextual evidence, rather than automatically appended as ground truth. Claims were separated by actor, application, time and scope. Existing labels were retained where defensible, with explicit revisions for Adobe's current AI product availability, Salesforce event rhetoric, JPMorgan generic training topics, and Deere's explicitly current ML product use. This is candidate-context review, not an independent exhaustive review of every nonmatching document block.

Saved judgments, batch hashes and contextual-review decisions permit deterministic replay; the serializers do not infer stages from keywords. Eight start-only quote anchors were expanded to complete remaining parent context during QA; the changed quote IDs map to earlier checkpoints in final_annotation_corrections.json. Every final quote exactly matches cached raw text, including original whitespace, and has source offsets/lines in the full archive. All original 447 annotation records remain recoverable verbatim in the verified pilot backup; current archive interpretations may differ.

### Eligibility and thresholds

The 23-column main `ai_annotations.csv` contains only substantive, focal-firm, identifiable source-grounded statements with Stage 1–5 and stage_eligible=yes. Stage 1 requires a focal objective; Stage 2 a concrete intended task/function/product; Stage 3 actual pilot/experiment; Stage 4 affirmative current operational use or deployed AI product; Stage 5 additionally an explicitly attributable realized numerical result. Historical launches, capability/access alone, a partnership, competitor adoption, vague testing life-cycle language and hypothetical risks do not establish current deployment. Tasks that remain unidentified can support broad current-use evidence but do not receive invented application IDs.

NA remains in `ai_annotations_full.csv`, alongside screening records and risk/governance-only statements. A substantive record can be ineligible for staging. No NA was changed to Stage 0; no stage was required to appear. Stage 5 was unsupported; ServiceNow customer benefits are a different actor, and SLB digital-wide revenue growth is not AI-attributable outcome evidence. Stage 5 maps to operational 4 for deployment counting when future data support it.

The core table is **conditional on eligibility**. It cannot supply the denominator for disclosure intensity, AI prevalence/absence, or risk/governance. Every selected firm remains in document_metrics.csv. A zero denotes no observed qualifying records or resolved IDs in this reviewed candidate corpus, with `full_document_absence_unassessed` stated explicitly.

## Reduced versus full schema

The core retains **23 columns**: {', '.join('`'+f+'`' for f in core_fields)}. Identifiers and exact quotations remain essential despite being provenance rather than model predictors.

The full archive preserves the original **48 detailed fields** and adds **stage_na_reason** (49 total). Eligibility, focal-evidence, actor/time, exact offsets, outcome attribution, detailed risks, context, identity status and version fields remain available for audit and reproducible aggregation. Prior labels/quotes survive in backups and batch checkpoints. Compacting the core never discards NA or source evidence.

The following assessment covers every original field. Non-NA coverage is an empirical completeness diagnostic, not reliability or accuracy; yes/no flags are populated values, not independent evidence of measurement validity. Core retention prioritizes attention/intent/application/implementation/outcomes/risks/governance and source-grounding. Redundant execution state and granular supporting taxonomies stay archival. Rare pilots/outcomes are theoretically important despite low support; no classification reliability estimate exists.

{field_table}

## Practical metric refinements (separate from Protocol.md)

The construct-first distinction between attention, intent and implementation is retained. No vague maturity index is published. Human-validated passage/topic/claim-word shares are deferred because no independent reference set exists and context/overlap handling requires further validation. Investment/partnership and detailed outcome attributes remain audit dimensions; they are not assumed implementation evidence. Risk/governance counts and issuer-presence indicators replace an unvalidated risk-word share in this exploratory EDA. Claim-specificity summaries retain the proposed ordinal rubric and must not be read as validated firm capability scores.

The primary unit is issuer/selected filing for lexical and firm comparisons, evidence statement for semantic composition, and issuer/task/period for distinct applications. Equal-company sector means/proportions include all seven firms. Repeated claims are retained as communication evidence but collapse through explicitly resolved use_case_id for distinct task counts. Multi-model product suites and repeated surfaces do not automatically become distinct applications. Scope indicators can overlap in principle; actual scope overlap is reported rather than assumed away. All semantic metrics remain preliminary.

{metric_table}

## Descriptive sector results

The following lexical means/medians use equal company weighting. Risk/governance and resolved-ID totals are supplemental counts with different units and denominators; they are not comparable percentages or maturity rankings.

{sector_table}

Technology has markedly higher lexical attention (mean 2.625/1,000 words versus 0.114–0.493 for other sector means) and contributes 83/98 resolved deployed IDs. Provider/product scope accounts for much of this pattern; it does not establish greater internal enterprise adoption. Seven of seven pharmaceutical filings report some current use, yet only two task identities are resolved. Four of seven financial filings report current deployment, but none identifies a defensibly countable distinct current task under this pass. Zero resolved IDs therefore does not mean zero reported deployment. Retail variation is material: HD and LOW supply the eight resolved deployed IDs; Amazon's broad current-use statement does not identify a distinct AWS or retail task. Energy has three current-use-reporting firms and three resolved IDs (OXY cybersecurity; SLB workflow planning and seismic imaging), alongside risk and demand-context disclosures.

These are small, purposive sector cohorts with heterogeneous business models and source scopes. No significance tests, population prevalence claims, enterprise maturity ordering, or causal productivity conclusions were made.

## NA and coding diagnostics

The previous pilot had 308/447 NA records (68.90%); the expansion has 568/844 (67.30%). Changes in sample, claim splitting and contextual interpretation prevent treating this difference as accuracy improvement. The large NA share is predominantly a measurement outcome: valid AI risk/governance content lacks qualifying strategy/application status, while other records concern non-focal actors, insufficient status, generic rhetoric, historical-only information or uncertain evidence.

{na_table}

NA groups use transparent priority: screening/context → ambiguity → non-focal evidence → historical without continuation → risk/governance without eligible stage → other insufficient strategy/status. This is a deterministic grouping of already-authored labels, **not** a new keyword classifier or independently validated explanation of why firms disclose this way. Detailed rationales and uncertainty fields remain available. All 844 annotations are human-unvalidated; **131** are flagged for priority human review, but unflagged rows also require independent validation.

### AI-performed semantic spot checks

These are contextual self-checks by AI, not independent human validation or an accuracy study.

{table(['Case','Decision and evidence boundary'],[
('LOW pilot (parent 551)','Explicit implementation of GenAI pilot programs → Stage 3. Unspecified task boundaries do not become distinct deployed IDs.'),
('HD (parents 537–538)','Current shopping search, Magic Apron and project/material tools separated from internal ML fulfillment routing; duplicate project tools grouped by task.'),
('DE (parent 716)','We utilize ML in products supports current product use; pooled S7/See & Spray examples do not independently resolve their task-method linkage.'),
('GOOGL (parent 243)','Scale/user counts are disclosure detail, not attributable realized numerical outcomes; no Stage 5.'),
('NOW (parent 424)','Customer-reported work-hour savings remain customer-actor evidence; vendor availability separately supports Stage 4, never focal Stage 5 from customer outcome.'),
('SLB (parent 767)','Digital-wide revenue and historical Lumi launch do not establish a current AI-task-attributable numerical outcome.'),
('AMZN (parent 520)','Affirmative broad current AI utilization retained as deployment evidence; AWS/retail task identity not invented.'),
('CAT, XOM demand context','AI data-center energy demand is market context, not supplier AI adoption.'),
('WFC, USB incorporated reports','Limited primary-document evidence and zeros retain scope limitations; no full-document absence conclusion.')])}

## Notebook, execution and QA

The original notebook was hash-backed up and refactored; useful numeric summaries, dtype inspection, sector-colored issuer bars and lexical/candidate-coverage scatter were retained. The updated notebook has six requested sections, **21 cells including 12 code cells**, and **12 rendered figures**: sector box/strip plots, stage composition, specificity heatmap, application scopes, equal-firm comparisons, NA and quality diagnostics, and lexical/deployment scatter. Paths and counts are dynamic; no 18-company assumption remains. It executes with the project's Python interpreter, errors disallowed, and without manual count edits. Installed minimal Jupyter execution dependencies: nbformat {env['packages']['nbformat']} and nbclient {env['packages']['nbclient']}; no heavy visualization dependency was added.

QA reconciles every source CIK/URL/form/period/latest-original selection against official cached SEC metadata, raw hashes and HTML identity; regenerates all extraction records; validates unique IDs, exact quotes/offsets/categories/stage guards, application identity consistency, full/core equality, all-42 firm rows and aggregation formulas; preserves all old source fields, all 393 parent records and all old lexical metrics; and verifies the eight-file backup, original numbered scripts and unchanged Protocol.md. Four focused aggregation tests cover repeated IDs, Stage 5 deployment, NA risks, unresolved current use, customer actors, empty firms and overlapping scope flags. Notebook execution is independently recorded in notebook_execution.json. Explicit categorical imports and core/full count assertions verify that stage compositions and specificity plots reconcile to 276 claims; output inspection caught and corrected integer-inferred core stages before completion. An additional read-only AI code review confirmed replay and denominator logic, without human semantic validation. These integrity checks cannot establish semantic accuracy.

## Recovery and rerunning

The original 18-company datasets/report/notebook/README/protocol are verified in `data/backups/expansion42_20261008/`, with earlier backups/checkpoints preserved. Current recovery authority is `data/checkpoints/expansion42_20261008/progress.json`; sources_staged.json, SEC cache, 16 immutable annotation batches, authored judgments, correction logs and final QA/execution/publication hashes persist. Source acquisition checkpointed every three additions, annotation every roughly 50 parents. Canonical datasets were preserved until replacement QA passed. Publication is atomic per file and resumable through the manifest; it is not a multi-file filesystem transaction. No checkpoint commits, Git merge or remote publication were performed.

Reproduction commands and exact environment versions are in README.md and processing_environment.json. Annotation replay reconstructs saved contextual decisions; it does not automatically perform a new AI pass, model evaluation or human study. Do not rerun batch-save scripts over completed immutable batches. Human validation remains future work: independently code candidates and nonmatching text, adjudicate scope/time/task/stage differences, evaluate extraction separately, then report reliability/accuracy only on an independent reference set.

## Filing-level coverage

{source_table}
'''
readme=f'''# DIAL AI Strategy & Adoption

This existing research project now covers **42 public companies (seven per sector)** using official SEC primary annual Form 10-K filings selected at **October 8, 2026**. Results: **770 candidate passages, 844 archival records, 276 eligible core claims**. All semantic coding is preliminary AI-first and **not human-validated**. [Protocol.md](Protocol.md) remains unchanged; [the updated report](AI_Annotation_First_Pass_Report.md) contains actual results, metric definitions, every-field assessment and source-scope exceptions.

## Sample and sources

{sample}

All 18 prior firms/files were retained; no substitution was needed. SEC issuer/CIK, latest original 10-K ≤ cutoff, period, accession and primary/index URLs were verified. Complete primary HTML/text files and SHA-256 hashes are cached with the existing edgartools 5.61.1 parser (10-K, max_col_width=500). Sources include subsector/business-model metadata. Amazon's AWS role remains distinct from retail. GE Aerospace uses continuing General Electric CIK 40545. XOM's verified predecessor CIK 34088 annual filing remains the consolidated-group exception following successor CIK 2115436. See source URLs and continuity notes in sources_downloaded.csv.

**WFC/USB scope limitation:** their primary 10-Ks incorporate substantial annual-report sections by reference. Separate incorporated documents are excluded from the uniform primary-document corpus. Low densities/zeros are not evidence of complete-filing absence. All 42 issuers remain in analysis; the notebook includes a labeled exclusion sensitivity check.

## Canonical files

| File | Role |
|---|---|
| `data/sources_downloaded.csv` | 42 selected filing records: identities, dates, URLs, checksums, subsectors and exceptions |
| `data/raw/*_10K_*.html` and `.txt` | Complete primary source HTML and consistently parsed text |
| `data/ai_passages.csv` | 770 screening candidates, exact paragraph context and stable passage IDs; all old 393 preserved |
| `data/ai_annotations_full.csv` | 844 complete claim/screening records, including all NA; original 48 detailed fields plus stage_na_reason |
| `data/ai_annotations.csv` | 276 substantive focal-firm Stage 1–5 claims, reduced to 23 core fields |
| `data/document_metrics.csv` | One row for every issuer, raw lexical and separately defined preliminary semantic metrics |
| `document_metrics.ipynb` | Six-section EDA, executed with .venv; 21 cells, 12 code cells, 12 figures |
| `src_code/1_download.py` | Resumable official SEC acquisition and staged source metadata |
| `src_code/2_extract_ai.py` | Existing uniform retrieval and stable source-based candidate IDs |
| `src_code/3_document_metrics.py` | Lexical and full-archive semantic aggregation |
| `src_code/test_document_metrics.py` | Focused aggregation correctness checks |

## Full versus core: use the correct denominator

The **core table is conditional on adoption-stage eligibility**, not a complete table of AI discussion. Risk-only/governance-only, historical/ambiguous, contextual and unsupported records remain in the **full archive**. NA never means Stage 0 or nonadoption. Stage 0 requires adequate full-document/scope review and is not assigned here. Main stage counts: 1=79, 2=15, 3=1, 4=181, 5=0. NA=568/844 (67.30%).

Use full archival records for risk/governance, relevance, confidence and NA diagnostics; use all 42 firm rows for sector comparisons; use complete primary words for lexical intensity. Candidate word share is screening context coverage, **not substantive AI topic share**. Claims, passages, words and resolved applications have different units. Core columns are: {', '.join('`'+f+'`' for f in core_fields)}.

Stages require contextual actor/time/scope reasoning under Protocol.md. Concrete plans are Stage 2, actual experiments Stage 3, affirmative current routine use/products Stage 4. Stage 5 adds realized numerical results explicitly attributable to the same deployed application and maps to operational Stage 4 for implementation comparisons. Customer benefits, users/access counts, generic capabilities and unrelated revenues do not automatically qualify. Broad current use may establish deployment presence but no identifiable task count.

Distinct applications count **resolved issuer/task/period IDs**, deduplicating repeated claims: 109 across all statuses, 98 currently deployed (10 internal, 83 customer-facing, 5 R&D/infrastructure; no internal/product overlap here). Vendor product deployment is separate from internal operations. All semantic comparisons describe disclosures rather than independently verified adoption.

## Measurement and notebook

`total_word_count` uses whitespace split; `ai_mention_count` uses longest-first nonoverlapping boundary-based keyword matches; `ai_mentions_per_1000_words` = mentions ×1,000 / primary words. Candidate count/words/share remain extraction metadata. Compact semantic measures are counts of substantive, strategy, eligible and NA records; resolved all-status/deployed/internal/product application IDs; deployment presence; and full-archive risk/governance counts. Their precise definitions, units, denominators and source fields are tabulated in the report. Every row explicitly records completed AI candidate review and unassessed full-document absence. No maturity index or independently validated topic share is published.

The notebook covers overview, intensity, strategy/adoption, equal-company sector comparisons, NA/confidence diagnostics, and preliminary findings/limitations. It retains useful prior lexical summaries and plots while adding box/strip plots, heatmaps, stacked composition and deployment scatter. Technology's mean lexical density is 2.625/1,000 primary words; other sector means range 0.114–0.493. Product-provider scope is prominent. Unresolved task identities and WFC/USB incorporated-report scope limit comparisons; no significance or causal claims are made.

## Rerun with the project virtual environment

Run from the repository root. SEC requests require permitted HTTPS access and the existing contact-bearing User-Agent (`SEC_USER_AGENT` may override it); paced requests/cache reuse preserve fair access. Downloads stage metadata rather than silently publishing partial samples.

```powershell
.\\.venv\\Scripts\\python.exe -B src_code/1_download.py
.\\.venv\\Scripts\\python.exe -B src_code/2_extract_ai.py
.\\.venv\\Scripts\\python.exe -B src_code/3_document_metrics.py
.\\.venv\\Scripts\\python.exe -B -m unittest discover -s src_code -p test_document_metrics.py
.\\.venv\\Scripts\\python.exe -B data/checkpoints/expansion42_20261008/execute_notebook.py
```

The first command reuses verified fixed-cutoff sources and stages `sources_downloaded.csv` in the current checkpoint. For a refresh, use that staged path with extraction's `--sources --output` and metrics' `--sources --passages --annotations --output`. Metrics require complete full-archive coverage, not the core file. Default extraction/metrics commands reproduce the current canonical snapshot. Existing output CSVs get timestamped exact backups and atomic per-file replacement. Separate `.web.txt`/`data/processed` material is not used.

To reconstruct saved annotation decisions and validate staged data (not perform a new annotation study):

```powershell
.\\.venv\\Scripts\\python.exe -B data/checkpoints/expansion42_20261008/prepare_annotations.py
.\\.venv\\Scripts\\python.exe -B src_code/3_document_metrics.py --sources data/checkpoints/expansion42_20261008/sources_downloaded.csv --passages data/checkpoints/expansion42_20261008/ai_passages.csv --annotations data/checkpoints/expansion42_20261008/ai_annotations_full.csv --output data/checkpoints/expansion42_20261008/document_metrics.csv
.\\.venv\\Scripts\\python.exe -B data/checkpoints/expansion42_20261008/validate_outputs.py
```

Open the notebook using the project's Python kernel, with repository-root working directory, and run all cells. It reads relative canonical paths with no hardcoded firm counts; `DIAL_DATA_DIR` is an optional staging-test override. The execution helper forces the current interpreter and fails on cell errors. Minimal execution packages are nbformat {env['packages']['nbformat']} and nbclient {env['packages']['nbclient']}; install if absent with `.\\.venv\\Scripts\\python.exe -m pip install nbformat=={env['packages']['nbformat']} nbclient=={env['packages']['nbclient']}`. Environment versions: pandas {env['packages']['pandas']}, NumPy {env['packages']['numpy']}, matplotlib {env['packages']['matplotlib']}, ipykernel {env['packages']['ipykernel']}, Python 3.13.7. See checkpoint processing_environment.json for the exact record.

## Recovery and validation status

Verified pre-expansion eight-file backups are in `data/backups/expansion42_20261008/`; earlier backups/checkpoints remain intact. Current progress, official SEC cache, immutable 16 annotation batches, explicit contextual decisions, quote-boundary corrections, QA, notebook execution and publication hashes live in `data/checkpoints/expansion42_20261008/`. Recover from progress.json; never rerun completed batch-save scripts. Annotation replay uses the preserved 48-field backup schema even after the canonical file becomes core-only. Source checkpoints were saved every three additional firms and annotations approximately every 50 parents.

All quotes/IDs/core-full links/42-firm metrics/source identities and backup hashes passed automated integrity checks. The notebook executes from top to bottom. No human validation, classification accuracy, extraction recall or intercoder reliability estimate exists. All 844 records need future independent validation; 131 carry priority review flags. Findings remain exploratory, selective, disclosure-based and scope-dependent. No Git commit/push or human validation study was automatically performed.
'''
(CP/'README.md').write_text(readme,encoding='utf-8')
(CP/'AI_Annotation_First_Pass_Report.md').write_text(report,encoding='utf-8')
print('Documentation staged:',len(report.split()),'report words;',len(readme.split()),'README words')
