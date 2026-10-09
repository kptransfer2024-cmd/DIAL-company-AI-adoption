# DIAL corporate AI strategy/adoption — 42-company first pass

**Status:** Complete primary-document workflow; preliminary AI-first semantic annotations, **human_validated=no for every record**. Fixed filing cutoff: **October 8, 2026**. Protocol.md is unchanged and remains the conceptual baseline. This report documents practical measurement refinements separately.

## Actual results

42 issuers, six sectors, seven firms each; 42 selected original annual filings. All 18 existing sources and 393 existing candidate IDs remain intact. The 24 additional companies contribute 377 new candidates, giving **770 candidates**, **844 full claim/screening records**, and **276 eligible core claims**. **568 records (67.30%)** remain Stage NA in the archive. Stages: **1=79, 2=15, 3=1, 4=181, 5=0**. No passage-level Stage 0 is used.

**109 resolved focal application IDs** occur across all disclosed statuses; **98** have current deployed evidence: **10 internal operations, 83 customer-facing products, and 5 other (R&D/infrastructure)**. Internal/product IDs do not overlap in this snapshot. Twenty-nine filings have coded current deployment evidence, including broad claims without identifiable applications. Eight filings have zero observed eligible claims; this is not nonadoption or an adequately reviewed full-document Stage 0.

## Sampling and acquisition

The existing large-company purposive stratification was extended without selecting firms for AI disclosure content. No substitutions or silent sample reductions occurred. Original sector names were retained for compatibility; financial and industrial subsectors are now explicit. Amazon's commerce/AWS distinction, energy upstream/services/downstream distinctions, and GE business continuity are recorded in metadata.

| Sector | Retained companies | Added companies |
| --- | --- | --- |
| Technology / Software | MSFT, ADBE, CRM | GOOGL, META, ORCL, NOW |
| Retail / Consumer Commerce | WMT, TGT, COST | AMZN, HD, LOW, KR |
| Financial Services / Banking | JPM, BAC, C | WFC, GS, MS, USB |
| Healthcare / Pharmaceuticals | JNJ, PFE, MRK | ABBV, BMY, LLY, AMGN |
| Industrials / Manufacturing | CAT, DE, HON | GE, RTX, ETN, MMM |
| Energy / Oil & Gas | XOM, CVX, COP | OXY, EOG, SLB, PSX |

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

The core retains **23 columns**: `claim_id`, `passage_id`, `ticker`, `source_file`, `source_line`, `evidence_quote`, `ai_relevance`, `actor`, `temporal_status`, `application_scope`, `use_case_id`, `use_case`, `strategic_orientation`, `forward_looking`, `strategy_specificity`, `adoption_stage`, `reported_deployment`, `quantified_outcome`, `ai_risk`, `ai_governance`, `coding_confidence`, `needs_human_review`, `annotation_rationale`. Identifiers and exact quotations remain essential despite being provenance rather than model predictors.

The full archive preserves the original **48 detailed fields** and adds **stage_na_reason** (49 total). Eligibility, focal-evidence, actor/time, exact offsets, outcome attribution, detailed risks, context, identity status and version fields remain available for audit and reproducible aggregation. Prior labels/quotes survive in backups and batch checkpoints. Compacting the core never discards NA or source evidence.

The following assessment covers every original field. Non-NA coverage is an empirical completeness diagnostic, not reliability or accuracy; yes/no flags are populated values, not independent evidence of measurement validity. Core retention prioritizes attention/intent/application/implementation/outcomes/risks/governance and source-grounding. Redundant execution state and granular supporting taxonomies stay archival. Rare pilots/outcomes are theoretically important despite low support; no classification reliability estimate exists.

| Original field | Core or audit | Non-NA values / 844 | Research role / decision |
| --- | --- | --- | --- |
| claim_id | Core | 844 | Evidence-statement identity; required for full/core audit join. |
| passage_id | Core | 844 | Stable parent identity and one-to-many extraction traceability. |
| ticker | Core | 844 | Sampled issuer key; industry metadata joins through sources. |
| report_period | Audit | 844 | Fiscal scope; archival join metadata duplicates source period. |
| source_file | Core | 844 | Exact cached primary-text identity. |
| source_line | Core | 844 | One-based parent start location; finer quote lines retained in archive. |
| evidence_quote | Core | 844 | Exact source span; indispensable source-grounding, not a model variable. |
| ai_relevance | Core | 844 | Separates substantive evidence, context, false positives and uncertainty. |
| focal_firm_evidence | Audit | 844 | Eligibility safeguard; redundant in filtered core, vital in archive. |
| actor | Core | 844 | Separates firm, provider/customer, competitor and third-party claims. |
| temporal_status | Core | 844 | Distinguishes intended, current, historical and hypothetical evidence. |
| use_case_id | Core | 161 | Resolved issuer/task identity used for deduplication; unresolved excluded from ID counts. |
| use_case | Core | 213 | Readable task description; allows unresolved boundaries without invented IDs. |
| application_scope | Core | 812 | Nonexclusive internal/product/customer/R&D/infrastructure/investment scope. |
| ai_technology_type | Audit | 803 | Supporting subtype; terminology often generic, excluded from primary comparisons. |
| strategic_orientation | Core | 152 | Nonexclusive objectives; meaningful strategy dimension, no forced maturity score. |
| ai_commitment | Audit | 801 | Detailed speech-act field overlaps plans/intent; sparse distinct commitments retained for audit. |
| forward_looking | Core | 808 | Future framing distinct from temporal status and actual implementation. |
| strategy_specificity | Core | 801 | Protocol informational-detail score, independent of evidence stage; preliminary ordinal coding. |
| adoption_stage | Core | 276 | Evidence threshold 1–5 or NA; core conditions on eligibility. |
| reported_deployment | Core | 197 | Current-use indicator; retained interpretability even though closely linked to 4/5. |
| pilot_reported | Audit | 197 | Detailed evidence check; redundant with Stage 3 in main analysis, retained audit. |
| ai_investment | Audit | 796 | Supporting resource dimension; spending alone not implementation. |
| ai_partnership | Audit | 801 | Supporting relationship dimension; partnership alone not deployment. |
| ai_risk | Core | 801 | Independent disclosure dimension, computed from full including NA. |
| ai_governance | Core | 798 | Actual focal controls/oversight dimension; kept separately from adoption. |
| quantified_outcome | Core | 308 | Supplementary realized numeric outcome flag; scale/revenue alone insufficient. |
| outcome_attribution | Audit | 21 | Stage 5 attribution safeguard; few outcomes, retained in audit not discarded. |
| outcome_metric | Audit | 15 | Evidence details and baseline/period caveats for audit; sparse outcome data. |
| coding_confidence | Core | 844 | AI self-assessed confidence, not classification accuracy. |
| needs_human_review | Core | 844 | Priority flag; all rows require independent validation regardless of flag. |
| annotation_rationale | Core | 844 | Brief contextual justification and boundaries; required in core. |
| uncertainty_reason | Audit | 85 | Detailed ambiguity audit; priority NA grouping does not replace it. |
| human_validated | Audit | 844 | Constant no in this pass; retained full, prominent dataset-level core documentation. |
| stage_eligible | Audit | 844 | Full screening safeguard; constant yes in core, omitted there. |
| operational_stage | Audit | 276 | Derived 5→4 mapping; redundant archival field, derivable for core. |
| use_case_identity_status | Audit | 213 | Resolved/provisional/unidentified guardrail; core NA IDs plus rationale retain abstention. |
| is_strategy_claim | Audit | 801 | Explicit objective flag for reproducible strategy aggregation; retained archival guardrail. |
| risk_category | Audit | 423 | Detailed nonexclusive taxonomy; compact main risk flag preferred pending validation. |
| context_reviewed | Audit | 844 | Constant yes after candidate-context review; audit execution state. |
| context_reference | Audit | 844 | Context source and batch audit; duplicates provenance in compact core. |
| evidence_start_char | Audit | 844 | Exact raw-text character offset; quotation integrity audit. |
| evidence_end_char | Audit | 844 | Exclusive quote offset; quotation integrity audit. |
| evidence_start_line | Audit | 844 | Finer one-based quote start; source_line remains parent start. |
| evidence_end_line | Audit | 844 | Finer quote end; archival precise-span recovery. |
| duplicate_group_id | Audit | 32 | Optional duplicate flag; resolved use-case IDs are primary aggregation basis. |
| record_type | Audit | 844 | Claim versus screening; mostly redundant with relevance, useful audit. |
| annotation_version | Audit | 844 | Run provenance; preserved audit and checkpoint manifests. |

## Practical metric refinements (separate from Protocol.md)

The construct-first distinction between attention, intent and implementation is retained. No vague maturity index is published. Human-validated passage/topic/claim-word shares are deferred because no independent reference set exists and context/overlap handling requires further validation. Investment/partnership and detailed outcome attributes remain audit dimensions; they are not assumed implementation evidence. Risk/governance counts and issuer-presence indicators replace an unvalidated risk-word share in this exploratory EDA. Claim-specificity summaries retain the proposed ordinal rubric and must not be read as validated firm capability scores.

The primary unit is issuer/selected filing for lexical and firm comparisons, evidence statement for semantic composition, and issuer/task/period for distinct applications. Equal-company sector means/proportions include all seven firms. Repeated claims are retained as communication evidence but collapse through explicitly resolved use_case_id for distinct task counts. Multi-model product suites and repeated surfaces do not automatically become distinct applications. Scope indicators can overlap in principle; actual scope overlap is reported rather than assumed away. All semantic metrics remain preliminary.

| Metric | Unit of observation | Definition | Unit / denominator | Source |
| --- | --- | --- | --- | --- |
| total_word_count | Document | All whitespace-split primary-text words | Words; no denominator | Raw text |
| ai_mention_count | Document | Nonoverlapping longest-first keyword matches | Matches; no denominator | Raw text / extraction patterns |
| ai_mentions_per_1000_words | Document | 1000 × mentions / total words | Matches per 1,000 primary words | Raw lexical counts |
| ai_candidate_passage_count | Document | Retrieved exact-text-deduplicated matching blocks | Candidates; no denominator | ai_passages |
| ai_candidate_word_count | Document | Sum of whitespace words across candidate blocks | Candidate-context words | ai_passages.passage_text |
| ai_candidate_word_share | Document | Candidate words / all primary-document words | Fraction; screening measure only | Candidate / total words |
| substantive_ai_claim_count | Document | All archived substantive records, including risk and NA | Records; no denominator | full.ai_relevance |
| strategy_claim_count | Document | Substantive focal-firm records explicitly coded strategy | Records; no denominator; repeated statements included | full.is_strategy_claim + actor/focal guards |
| stage_eligible_claim_count | Document | Substantive focal-firm eligible Stages 1–5 | Records; no denominator; equals core issuer count | full stage/relevance/actor/eligibility |
| stage_na_claim_count | Document | All archival records with adoption_stage=NA | Records; no denominator; not nonadoption | full.adoption_stage |
| distinct_ai_use_case_count | Issuer/task/period → document | Unique resolved substantive focal IDs across all disclosed statuses | Distinct IDs; no denominator; includes planned/historical | full.use_case_id + identity/actor/relevance |
| deployed_use_case_count | Issuer/task/period → document | Unique resolved focal IDs with current 4/5 and reported deployment | Distinct IDs; no denominator; repetitions count once | full stages/temporal/identity/deployment |
| internal_deployed_use_case_count | Issuer/task/period → document | Deployed IDs with explicit internal_operations scope | Distinct IDs; may overlap other scope counts | Full deployed IDs / scope |
| customer_facing_deployed_use_case_count | Issuer/task/period → document | Deployed IDs with explicit customer_facing_product scope | Distinct IDs; provider products, not customer/internal adoption | Full deployed IDs / scope |
| reported_deployment_present | Document | At least one qualifying current 4/5 record, including unresolved tasks | Binary 0/1; zero means none observed in reviewed candidates | Full eligible deployed records |
| ai_risk_claim_count | Document | All substantive archived records with AI risk=yes, including NA | Records; no denominator | full.ai_relevance + ai_risk |
| ai_governance_claim_count | Document | All substantive archived records with AI governance=yes, including NA | Records; no denominator | full.ai_relevance + ai_governance |
| semantic_review_status | Document | Candidate review complete; full-document absence unassessed | Review scope label; not maturity/adoption | Checkpoint coverage |
| Explicit strategy presence (notebook) | Document/sector | strategy_claim_count>0; sector average across all seven issuers | Binary / equal-firm fraction | Full-derived metrics |
| Strategy specificity (notebook) | Claim/issuer | Protocol score; issuer mean across explicit strategy records | Ordinal score / arithmetic descriptive mean, no weighting as maturity | full strategy flag + strategy_specificity |
| Concrete intended application evidence (notebook) | Claim / issuer-task | Stage 2 records and unique resolved Stage 2 IDs shown separately | Claims or IDs, explicitly labeled; no denominator | Core stage + use_case_id |
| Stage composition (notebook) | Claim | Eligible Stage 1–5 counts | Core claims; percentages if used divide eligible claims only | Core adoption_stage |
| Eligible claims per 10,000 words (notebook) | Document / sector | 10000 × eligible claims / primary words; sector mean across firms | Records per 10,000 words; preliminary | Metrics stage_eligible / total_word_count |
| Stage NA rate (notebook) | Document | NA archival records / all archival records for issuer | Fraction of archived records, not firms or words | Full adoption_stage |
| Eligible candidate share (notebook) | Document | Candidates with ≥1 core record / all candidates | Fraction of candidate passages, not topic share | Unique core passage IDs / ai_passages |
| Risk/governance presence (notebook) | Document / sector | Count>0; average binary indicators across selected firms | Equal-company fraction; not overall adoption prevalence | Full-derived risk/governance counts |
| Confidence and review flags (notebook) | Archival record | Self-confidence category and needs-review flag counts | All archived records; no accuracy denominator | Full coding_confidence / needs_human_review |
| Stage NA reason (archive/notebook) | Archival record | Priority grouping of existing relevance/eligibility/actor/time/risk/control labels | NA records; diagnostic label, not validated causal explanation | Full stage_na_reason |

## Descriptive sector results

The following lexical means/medians use equal company weighting. Risk/governance and resolved-ID totals are supplemental counts with different units and denominators; they are not comparable percentages or maturity rankings.

| Sector | Firms | Mean lexical density | Median lexical density | Firms with deployment evidence | Resolved deployed IDs | Risk records | Governance records |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technology / Software | 7.0 | 2.625 | 2.397 | 7.0 | 83.0 | 209.0 | 22.0 |
| Retail / Consumer Commerce | 7.0 | 0.493 | 0.422 | 4.0 | 8.0 | 60.0 | 2.0 |
| Financial Services / Banking | 7.0 | 0.177 | 0.169 | 4.0 | 0.0 | 76.0 | 9.0 |
| Healthcare / Pharmaceuticals | 7.0 | 0.284 | 0.192 | 7.0 | 2.0 | 37.0 | 2.0 |
| Industrials / Manufacturing | 7.0 | 0.211 | 0.228 | 4.0 | 2.0 | 30.0 | 0.0 |
| Energy / Oil & Gas | 7.0 | 0.114 | 0.062 | 3.0 | 3.0 | 11.0 | 2.0 |

Technology has markedly higher lexical attention (mean 2.625/1,000 words versus 0.114–0.493 for other sector means) and contributes 83/98 resolved deployed IDs. Provider/product scope accounts for much of this pattern; it does not establish greater internal enterprise adoption. Seven of seven pharmaceutical filings report some current use, yet only two task identities are resolved. Four of seven financial filings report current deployment, but none identifies a defensibly countable distinct current task under this pass. Zero resolved IDs therefore does not mean zero reported deployment. Retail variation is material: HD and LOW supply the eight resolved deployed IDs; Amazon's broad current-use statement does not identify a distinct AWS or retail task. Energy has three current-use-reporting firms and three resolved IDs (OXY cybersecurity; SLB workflow planning and seismic imaging), alongside risk and demand-context disclosures.

These are small, purposive sector cohorts with heterogeneous business models and source scopes. No significance tests, population prevalence claims, enterprise maturity ordering, or causal productivity conclusions were made.

## NA and coding diagnostics

The previous pilot had 308/447 NA records (68.90%); the expansion has 568/844 (67.30%). Changes in sample, claim splitting and contextual interpretation prevent treating this difference as accuracy improvement. The large NA share is predominantly a measurement outcome: valid AI risk/governance content lacks qualifying strategy/application status, while other records concern non-focal actors, insufficient status, generic rhetoric, historical-only information or uncertain evidence.

| Priority diagnostic group | NA records |
| --- | --- |
| screening_or_context | 36 |
| insufficient_strategy_or_application_status | 106 |
| ambiguous_evidence | 13 |
| risk_or_governance_without_qualifying_stage | 351 |
| non_focal_actor_or_evidence | 59 |
| historical_without_current_confirmation | 3 |

NA groups use transparent priority: screening/context → ambiguity → non-focal evidence → historical without continuation → risk/governance without eligible stage → other insufficient strategy/status. This is a deterministic grouping of already-authored labels, **not** a new keyword classifier or independently validated explanation of why firms disclose this way. Detailed rationales and uncertainty fields remain available. All 844 annotations are human-unvalidated; **131** are flagged for priority human review, but unflagged rows also require independent validation.

### AI-performed semantic spot checks

These are contextual self-checks by AI, not independent human validation or an accuracy study.

| Case | Decision and evidence boundary |
| --- | --- |
| LOW pilot (parent 551) | Explicit implementation of GenAI pilot programs → Stage 3. Unspecified task boundaries do not become distinct deployed IDs. |
| HD (parents 537–538) | Current shopping search, Magic Apron and project/material tools separated from internal ML fulfillment routing; duplicate project tools grouped by task. |
| DE (parent 716) | We utilize ML in products supports current product use; pooled S7/See & Spray examples do not independently resolve their task-method linkage. |
| GOOGL (parent 243) | Scale/user counts are disclosure detail, not attributable realized numerical outcomes; no Stage 5. |
| NOW (parent 424) | Customer-reported work-hour savings remain customer-actor evidence; vendor availability separately supports Stage 4, never focal Stage 5 from customer outcome. |
| SLB (parent 767) | Digital-wide revenue and historical Lumi launch do not establish a current AI-task-attributable numerical outcome. |
| AMZN (parent 520) | Affirmative broad current AI utilization retained as deployment evidence; AWS/retail task identity not invented. |
| CAT, XOM demand context | AI data-center energy demand is market context, not supplier AI adoption. |
| WFC, USB incorporated reports | Limited primary-document evidence and zeros retain scope limitations; no full-document absence conclusion. |

## Notebook, execution and QA

The original notebook was hash-backed up and refactored; useful numeric summaries, dtype inspection, sector-colored issuer bars and lexical/candidate-coverage scatter were retained. The updated notebook has six requested sections, **21 cells including 12 code cells**, and **12 rendered figures**: sector box/strip plots, stage composition, specificity heatmap, application scopes, equal-firm comparisons, NA and quality diagnostics, and lexical/deployment scatter. Paths and counts are dynamic; no 18-company assumption remains. It executes with the project's Python interpreter, errors disallowed, and without manual count edits. Installed minimal Jupyter execution dependencies: nbformat 5.11.1 and nbclient 0.11.0; no heavy visualization dependency was added.

QA reconciles every source CIK/URL/form/period/latest-original selection against official cached SEC metadata, raw hashes and HTML identity; regenerates all extraction records; validates unique IDs, exact quotes/offsets/categories/stage guards, application identity consistency, full/core equality, all-42 firm rows and aggregation formulas; preserves all old source fields, all 393 parent records and all old lexical metrics; and verifies the eight-file backup, original numbered scripts and unchanged Protocol.md. Four focused aggregation tests cover repeated IDs, Stage 5 deployment, NA risks, unresolved current use, customer actors, empty firms and overlapping scope flags. Notebook execution is independently recorded in notebook_execution.json. Explicit categorical imports and core/full count assertions verify that stage compositions and specificity plots reconcile to 276 claims; output inspection caught and corrected integer-inferred core stages before completion. An additional read-only AI code review confirmed replay and denominator logic, without human semantic validation. These integrity checks cannot establish semantic accuracy.

## Recovery and rerunning

The original 18-company datasets/report/notebook/README/protocol are verified in `data/backups/expansion42_20261008/`, with earlier backups/checkpoints preserved. Current recovery authority is `data/checkpoints/expansion42_20261008/progress.json`; sources_staged.json, SEC cache, 16 immutable annotation batches, authored judgments, correction logs and final QA/execution/publication hashes persist. Source acquisition checkpointed every three additions, annotation every roughly 50 parents. Canonical datasets were preserved until replacement QA passed. Publication is atomic per file and resumable through the manifest; it is not a multi-file filesystem transaction. No checkpoint commits, Git merge or remote publication were performed.

Reproduction commands and exact environment versions are in README.md and processing_environment.json. Annotation replay reconstructs saved contextual decisions; it does not automatically perform a new AI pass, model evaluation or human study. Do not rerun batch-save scripts over completed immutable batches. Human validation remains future work: independently code candidates and nonmatching text, adjudicate scope/time/task/stage differences, evaluate extraction separately, then report reliability/accuracy only on an independent reference set.

## Filing-level coverage

| Ticker | Subsector | CIK | Filing date | Period end | Words | Candidates | Eligible claims | Resolved deployed IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MSFT | Software / cloud | 789019 | 2026-07-29 | 2026-06-30 | 47809 | 101 | 35 | 8 |
| ADBE | Software / cloud | 796343 | 2026-01-15 | 2025-11-28 | 50379 | 64 | 37 | 13 |
| CRM | Software / cloud | 1108524 | 2026-03-02 | 2026-01-31 | 60336 | 72 | 30 | 17 |
| GOOGL | Internet platforms | 1652044 | 2026-02-05 | 2025-12-31 | 52139 | 55 | 21 | 11 |
| META | Internet platforms | 1326801 | 2026-01-29 | 2025-12-31 | 78908 | 75 | 26 | 6 |
| ORCL | Software / cloud | 1341439 | 2026-06-22 | 2026-05-31 | 62426 | 43 | 17 | 6 |
| NOW | Software / cloud | 1373715 | 2026-01-29 | 2025-12-31 | 51965 | 69 | 34 | 22 |
| WMT | General / grocery retail | 104169 | 2026-03-13 | 2026-01-31 | 53778 | 19 | 8 | 0 |
| TGT | General / grocery retail | 27419 | 2026-03-11 | 2026-01-31 | 35511 | 10 | 1 | 0 |
| COST | General / grocery retail | 909832 | 2026-10-07 | 2026-08-30 | 31410 | 5 | 0 | 0 |
| AMZN | Commerce / cloud infrastructure | 1018724 | 2026-02-06 | 2025-12-31 | 42039 | 22 | 2 | 0 |
| HD | Home improvement retail | 354950 | 2026-03-18 | 2026-02-01 | 49490 | 13 | 5 | 4 |
| LOW | Home improvement retail | 60667 | 2026-03-23 | 2026-01-30 | 44296 | 7 | 7 | 4 |
| KR | General / grocery retail | 56873 | 2026-03-31 | 2026-01-31 | 53982 | 4 | 1 | 0 |
| JPM | Diversified / commercial banking | 19617 | 2026-02-13 | 2025-12-31 | 177035 | 20 | 1 | 0 |
| BAC | Diversified / commercial banking | 70858 | 2026-02-25 | 2025-12-31 | 133177 | 24 | 2 | 0 |
| C | Diversified / commercial banking | 831001 | 2026-02-20 | 2025-12-31 | 177460 | 20 | 2 | 0 |
| WFC | Diversified / commercial banking | 72971 | 2026-02-24 | 2025-12-31 | 13485 | 1 | 0 | 0 |
| GS | Investment banking / wealth management | 886982 | 2026-02-25 | 2025-12-31 | 165720 | 17 | 1 | 0 |
| MS | Investment banking / wealth management | 895421 | 2026-02-19 | 2025-12-31 | 115543 | 10 | 0 | 0 |
| USB | Diversified / commercial banking | 36104 | 2026-02-23 | 2025-12-31 | 20390 | 1 | 1 | 0 |
| JNJ | Pharmaceuticals / biotechnology | 200406 | 2026-02-11 | 2025-12-28 | 62539 | 3 | 1 | 0 |
| PFE | Pharmaceuticals / biotechnology | 78003 | 2026-02-26 | 2025-12-31 | 95242 | 19 | 9 | 0 |
| MRK | Pharmaceuticals / biotechnology | 310158 | 2026-02-24 | 2025-12-31 | 93636 | 4 | 2 | 0 |
| ABBV | Pharmaceuticals / biotechnology | 1551152 | 2026-02-20 | 2025-12-31 | 62507 | 4 | 3 | 0 |
| BMY | Pharmaceuticals / biotechnology | 14272 | 2026-02-11 | 2025-12-31 | 78406 | 7 | 5 | 1 |
| LLY | Pharmaceuticals / biotechnology | 59478 | 2026-02-12 | 2025-12-31 | 53698 | 8 | 1 | 0 |
| AMGN | Pharmaceuticals / biotechnology | 318154 | 2026-02-13 | 2025-12-31 | 96130 | 10 | 3 | 1 |
| CAT | Construction / mining machinery | 18230 | 2026-02-13 | 2025-12-31 | 65816 | 1 | 0 | 0 |
| DE | Agricultural machinery | 315189 | 2025-12-18 | 2025-11-02 | 55789 | 15 | 6 | 1 |
| HON | Diversified industrial technology | 773840 | 2026-02-17 | 2025-12-31 | 66712 | 9 | 2 | 1 |
| GE | Aerospace engines / services | 40545 | 2026-01-29 | 2025-12-31 | 59469 | 3 | 1 | 0 |
| RTX | Aerospace / defense | 101829 | 2026-02-06 | 2025-12-31 | 80502 | 5 | 2 | 0 |
| ETN | Power management | 1551182 | 2026-02-26 | 2025-12-31 | 48342 | 4 | 0 | 0 |
| MMM | Diversified manufacturing | 66740 | 2026-02-03 | 2025-12-31 | 70132 | 4 | 2 | 0 |
| XOM | Integrated oil and gas | 34088 | 2026-02-18 | 2025-12-31 | 62895 | 3 | 1 | 0 |
| CVX | Integrated oil and gas | 93410 | 2026-02-24 | 2025-12-31 | 73488 | 3 | 2 | 0 |
| COP | Upstream oil and gas | 1163165 | 2026-02-17 | 2025-12-31 | 75683 | 1 | 0 | 0 |
| OXY | Upstream oil and gas | 797468 | 2026-02-18 | 2025-12-31 | 67134 | 3 | 1 | 1 |
| EOG | Upstream oil and gas | 821189 | 2026-02-24 | 2025-12-31 | 64336 | 1 | 0 | 0 |
| SLB | Oilfield services / technology | 87347 | 2026-01-23 | 2025-12-31 | 33983 | 9 | 4 | 2 |
| PSX | Downstream / refining | 1534701 | 2026-02-20 | 2025-12-31 | 80596 | 2 | 0 | 0 |
