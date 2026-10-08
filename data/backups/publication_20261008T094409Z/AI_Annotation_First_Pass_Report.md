# Corporate AI Strategy and Adoption — Expanded First Pass

**Status:** Preliminary, disclosure-based AI annotations; every row has human_validated=no.  
**Protocol:** Existing Protocol.md, unchanged. **Availability cutoff:** October 8, 2026.  
**Coverage:** 18 selected annual filings, 393 candidate passages, 447 claim/screening rows. No human evaluation or causal analysis was performed.

## 1. Sample and filing selection

The purposive stratified sample contains three firms in each analytical sector. Microsoft, Walmart and JPMorgan are the original members; the other 15 are new. Selection was independent of AI disclosure frequency.

| Analytical stratum | Companies |
|---|---|
| Technology / Software | MSFT, ADBE, CRM |
| Retail / Consumer Commerce | WMT, TGT, COST |
| Financial Services / Banking | JPM, BAC, C |
| Healthcare / Pharmaceuticals | JNJ, PFE, MRK |
| Industrials / Manufacturing | CAT, DE, HON |
| Energy / Oil & Gas | XOM, CVX, COP |

This is a nonrandom, large-company exploratory cohort, not representative of U.S. firms or each sector. Vendor software, warehouse clubs, banking franchises, drug portfolios, industrial equipment and energy operations differ substantially within and across strata. Research sectors are not SEC SIC classifications; SEC industry descriptions are retained separately.

For each issuer, official SEC ticker mappings and submissions records identify the most recently filed original 10-K on or before the cutoff. Original MSFT/WMT/JPM accessions and raw files were retained. Amendments are recorded separately and not substituted for original reports. No amendments matching these annual periods were identified in the cached recent submission histories unless listed in the metadata. Those histories do not constitute an unlimited historical amendment audit.

**XOM issuer-continuity exception:** Current XOM maps to ExxonMobil Holdings (CIK 2115436), the successor following the July 1, 2026 redomiciliation. It has no original 10-K by the cutoff. The selected February 18 annual filing is the same consolidated group's predecessor public registrant Exxon Mobil Corporation (CIK 34088), not a different subsidiary's standalone report. Both current ticker CIK and actual filing CIK, the selection note and the [SEC successor disclosure](https://www.sec.gov/Archives/edgar/data/2115436/000119312526291990/d71068d8k12b.htm) are recorded. This explicit corporate-group continuity choice requires researcher attention if the intended cohort requires only current legal-registrant CIKs; no firm was silently substituted or omitted.

## 2. Acquisition and lexical measures

Approved network-enabled execution resolved the sandbox socket restriction. Complete primary HTML was retrieved from official SEC archives using the existing contact-bearing User-Agent, caching, request spacing of at least 0.6 seconds and transient-error backoff. Existing identical sources were reused. Access followed [SEC fair-access guidance](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data).

The same installed edgartools HTMLParser (10-K configuration; table column width 500) was used throughout. It reproduces all three prior text files exactly. Primary HTML is retained without browser excerpt limits or a filing-length cutoff. Text retains paragraph/section structure, but rendering may shorten unusually wide table cells or flatten formatting; consult preserved HTML for table-sensitive decisions. Text normalization is not proof of perfect extraction of all original layout.

| Ticker | Filing date | Fiscal period end | Filing CIK | Primary words | Candidates | Mentions/1,000 |
| --- | --- | --- | --- | --- | --- | --- |
| MSFT | 2026-07-29 | 2026-06-30 | 0000789019 | 47809 | 101 | 3.660 |
| ADBE | 2026-01-15 | 2025-11-28 | 0000796343 | 50379 | 64 | 3.315 |
| CRM | 2026-03-02 | 2026-01-31 | 0001108524 | 60336 | 72 | 2.237 |
| WMT | 2026-03-13 | 2026-01-31 | 0000104169 | 53778 | 19 | 0.465 |
| TGT | 2026-03-11 | 2026-01-31 | 0000027419 | 35511 | 10 | 0.422 |
| COST | 2026-10-07 | 2026-08-30 | 0000909832 | 31410 | 5 | 0.318 |
| JPM | 2026-02-13 | 2025-12-31 | 0000019617 | 177035 | 20 | 0.169 |
| BAC | 2026-02-25 | 2025-12-31 | 0000070858 | 133177 | 24 | 0.308 |
| C | 2026-02-20 | 2025-12-31 | 0000831001 | 177460 | 20 | 0.214 |
| JNJ | 2026-02-11 | 2025-12-28 | 0000200406 | 62539 | 3 | 0.192 |
| PFE | 2026-02-26 | 2025-12-31 | 0000078003 | 95242 | 19 | 0.441 |
| MRK | 2026-02-24 | 2025-12-31 | 0000310158 | 93636 | 4 | 0.150 |
| CAT | 2026-02-13 | 2025-12-31 | 0000018230 | 65816 | 1 | 0.030 |
| DE | 2025-12-18 | 2025-11-02 | 0000315189 | 55789 | 15 | 0.358 |
| HON | 2026-02-17 | 2025-12-31 | 0000773840 | 66712 | 9 | 0.420 |
| XOM | 2026-02-18 | 2025-12-31 | 0000034088 | 62895 | 3 | 0.079 |
| CVX | 2026-02-24 | 2025-12-31 | 0000093410 | 73488 | 3 | 0.191 |
| COP | 2026-02-17 | 2025-12-31 | 0001163165 | 75683 | 1 | 0.013 |

Filing date and reporting period remain distinct. Fiscal ends range from November 2, 2025 to August 30, 2026; availability through October 8 is not a common economic observation window.

Extraction preserves the existing case-insensitive, word-boundary AI expressions, paragraph boundaries and exact-text deduplication within each filing. The five original candidate columns remain and passage_id is added. Standalone plural LLMs or GenAI and implicit applications may be missed where other existing cues are absent; no exhaustive AI-free source review is claimed.

Words use whitespace splitting. Candidate word share divides words in unique retrieved paragraphs by all filing words; mention density divides nonoverlapping full-text keyword matches by all words, times 1,000. Longer overlapping expressions count once. Candidate shares include non-AI surrounding prose and are unvalidated lexical measures.

The original 140 passage texts, lines and IDs and all three lexical metric rows reproduce exactly. Recomputing keywords corrects one MSFT matched_keywords cell; it does not change passage content, count, denominator or identifiers. The dataset contains the refreshed full sample, not an appended old/new mixture.

## 3. Annotation construction and findings

All candidates were freshly read in eight persistent batches of 42–51 parents. Explicit contextual judgments determine relevance, entity/time, claims, applications, stage and other attributes; Python only handles serialization, identifiers, counts and integrity. No keyword-to-stage classifier or external LLM API was used. Previous annotations were not reference labels.

Independent claims are split when applications, risks or resources convey distinct evidence. Repetitions remain source-linked claims and share application IDs where reliable. Broad portfolio statements are not forced into invented tasks. Named product-platform/function boundaries are provisional research judgments even when identity status is resolved. Shared quotations across distinct claims are intentional and cannot be summed as disjoint word spans.

| Relevance | Rows |
|---|---:|
| substantive | 417 |
| context_only | 22 |
| uncertain | 7 |
| irrelevant | 1 |

| Reported stage | Rows |
|---|---:|
| 1 — broad firm-specific direction | 46 |
| 2 — identifiable intended application | 13 |
| 3 — actual pilot/test | 0 |
| 4 — current operational use/deployed offering | 80 |
| 5 — deployment plus attributable realized numeric result | 0 |
| NA — inapplicable/insufficient/uncertain | 308 |

No individual Stage 0 was assigned. There are **50 resolved application IDs**, of which **40 have supported current deployment**, compared with **80 deployment claims**. Some explicit current-use claims have no reliable application ID; zero identifiable IDs does not mean zero disclosed deployment.

Deployment claim scope: {'customer_facing_product': 64, 'infrastructure_or_platform': 2, 'internal_operations': 13, 'internal_operations|research_and_development': 1}. Provider offerings and AI compute services are distinct from internal use and from customers' claims of adoption. Scope-specific application counts must use unique nonmissing IDs, not rows.

There are 60 strategy claims; mean specificity among those assessable claims is 2.15, with score counts {'1': 9, '2': 37, '3': 10, '4': 4}. Specificity is separate from implementation; no score 5 was forced. Nonexclusive strategy orientation counts are {'responsible_ai': 4, 'innovation': 17, 'infrastructure_capacity': 1, 'competitive_positioning': 10, 'workforce_productivity': 17, 'efficiency': 15, 'customer_experience': 11, 'revenue_growth': 4, 'security': 2}.

Other claim attributes: 238 forward-looking, 9 explicit commitments, 49 investment, 12 partnership, 211 risk and 19 governance claims. Categories overlap; totals need not equal rows. Conditional risks are forward-looking but not commitments.

| Firm | Rows | Substantive | Strategy | Stage 2 | Deployment claims | Deployed IDs | Risk | Governance | Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MSFT | 120 | 110 | 23 | 4 | 12 | 8 | 37 | 4 | 27 |
| ADBE | 73 | 67 | 6 | 1 | 30 | 13 | 20 | 4 | 16 |
| CRM | 81 | 81 | 6 | 0 | 25 | 17 | 39 | 5 | 10 |
| WMT | 22 | 19 | 8 | 1 | 0 | 0 | 11 | 0 | 4 |
| TGT | 12 | 12 | 1 | 1 | 0 | 0 | 9 | 0 | 3 |
| COST | 5 | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| JPM | 21 | 20 | 1 | 0 | 1 | 0 | 17 | 1 | 2 |
| BAC | 25 | 23 | 1 | 1 | 1 | 0 | 21 | 2 | 2 |
| C | 22 | 20 | 1 | 0 | 1 | 0 | 16 | 2 | 3 |
| JNJ | 4 | 4 | 0 | 0 | 1 | 0 | 4 | 0 | 1 |
| PFE | 22 | 21 | 8 | 4 | 1 | 0 | 11 | 0 | 5 |
| MRK | 4 | 4 | 0 | 0 | 2 | 0 | 4 | 0 | 2 |
| CAT | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| DE | 16 | 13 | 2 | 1 | 3 | 1 | 6 | 0 | 5 |
| HON | 10 | 10 | 1 | 0 | 1 | 1 | 8 | 0 | 1 |
| XOM | 3 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| CVX | 5 | 5 | 1 | 0 | 2 | 0 | 1 | 1 | 3 |
| COP | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |

## 4. Exploratory comparisons

Mean density below is the unweighted mean of three company-specific lexical densities, not a word-weighted sector population estimate.

| Sampling sector | Parents | Rows | Mean mention density | Deployment claims | Deployed IDs | Risk claims | Governance claims |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technology / Software | 237 | 274 | 3.071 | 67 | 38 | 96 | 13 |
| Retail / Consumer Commerce | 34 | 39 | 0.402 | 0 | 0 | 25 | 0 |
| Financial Services / Banking | 64 | 68 | 0.230 | 3 | 0 | 54 | 5 |
| Healthcare / Pharmaceuticals | 26 | 30 | 0.261 | 4 | 0 | 19 | 0 |
| Industrials / Manufacturing | 25 | 27 | 0.270 | 4 | 2 | 14 | 0 |
| Energy / Oil & Gas | 7 | 9 | 0.094 | 2 | 0 | 3 | 1 |

The sampled software vendors discuss many currently offered AI products; these account for much of their identified deployment breadth. That provider scope is not equivalent to internal operational adoption in banking, pharmaceuticals or energy. Several non-vendors explicitly report current AI use but omit specific workflows, reducing countable IDs independently of adoption itself.

Within retail, Target describes intended transformation and prior-year AI accomplishments; Walmart has identifiable intended search/discovery development; Costco's retrieved content concentrates on risks. Within industrials, Deere identifies current SmartDetect ML and manufacturing integration, Honeywell describes Forge-enabled AI offerings, while Caterpillar's sole candidate concerns AI-related electricity demand. These patterns describe these filings only. Keyword intensity, detailed strategy and stage evidence are different measures; no monotonic relationship or causal effect is assumed.

## 5. Diagnostics and unresolved judgments

- **Previously absent Stage 2:** The fresh pass yields 13 intended-application claims, including named Copilot/grounding/security priorities, AEP agent development, retail search/decision functions, banking data management, pharmaceutical cost programs and manufacturing analytics integration. Normative must/continue, building and program-opportunity statements are flagged when intent is clearer than implementation. Human validation may revise those boundaries.
- **No qualifying Stage 3 or 5:** Exploring, R&D spend, a hypothetical proof-of-concept cycle and building agents do not report actual testing. Shared cloud growth, acquired-company revenue, user/seat counts and expected cost-program expense do not establish attributable realized application benefits. Genuine zeros concern qualifying candidates, not firm behavior.
- **Historical versus current:** Target's 2025 launch/expansion and Citi's regulatory-data accomplishment are retained as historical evidence with NA stage where continuing use is not explicit. Current product availability elsewhere can corroborate a dated launch (for example Acrobat and SmartDetect); a launch alone cannot.
- **Application identity:** LinkedIn's suite is one identified AI offering rather than four inferred independent tasks. Broad Adobe platform/unnamed assistants are not merged automatically into Firefly. Generic estimation purposes, broad AI operations and similarly branded products do not receive invented separate IDs. Some named platform tasks remain overlapping or coarse; application counts are not enterprise maturity.
- **Uncertainty:** 7 uncertain-relevance rows, 14 uncertain-eligibility rows and 85 review flags. Confidence counts: {'high': 362, 'medium': 78, 'low': 7}. These are overlapping quality indicators, not validated error rates. Every field received a first-pass assessment; NA is a completed abstention/inapplicable judgment, not a processing failure.
- **Bias:** Large-firm selection, disclosure incentives, vendor versus user business models, legal/risk prose and uneven fiscal periods constrain comparisons. Keyword recall and semantic accuracy remain unknown until independent evaluation. No precision, recall, confusion matrix or reliability score is fabricated.

## 6. Compact data dictionary and counting rules

Unit: one interpretable claim or retained screening statement; 48 prior annotation columns preserved.

| Fields | Type / controlled values | Missing and aggregation rule |
|---|---|---|
| claim_id; passage_id | Stable strings | Claims unique; count parents with passage_id.nunique() |
| ticker; report_period; source_file; source_line | Strings; ISO fiscal-end date; positive source line | Join to selected filing, not ticker alone across periods |
| evidence_quote; evidence offsets/lines | Exact text; integer offsets/lines | Zero-based, half-open Unicode-character offsets in unmodified decoded TXT; not bytes |
| ai_relevance | substantive, context_only, irrelevant, uncertain | Distinct from stage eligibility |
| focal_firm_evidence; actor | yes/no/unclear; focal_firm/customer/partner/competitor/industry/other/unclear | Customer/competitor behavior is not focal adoption |
| temporal_status | planned/current/historical/discontinued/hypothetical/unclear | Count current deployments only |
| use_case_id; use_case; identity status | String; description; resolved/provisional/not_identified/NA | Exclude NA from nunique(); do not equate claims with applications |
| application_scope | internal_operations/customer_facing_product/customer_adoption_claim/research_and_development/infrastructure_or_platform/partnership_or_investment/unclear_or_other | Multi-label; equivalent scopes needed for comparisons |
| ai_technology_type | genai/traditional_ml/mixed/unspecified_ai/NA | ML alone does not establish GenAI; unspecified is not non-AI |
| strategic_orientation | efficiency/innovation/customer_experience/revenue_growth/workforce_productivity/competitive_positioning/responsible_ai/security/infrastructure_capacity/other/NA | Nonexclusive explicit objectives; security includes risk-management objectives |
| ai_commitment; forward_looking; is_strategy_claim | yes/no/NA | Explicit undertaking distinct from conditional future discussion |
| strategy_specificity | 1–5 or NA | Protocol rubric; compute means only among eligible nonmissing records with declared denominator |
| stage_eligible; adoption_stage; operational_stage | yes/no/uncertain; 1–5/NA; 1–4/NA at claim level | Stage 0 unavailable for individual claims; map Stage 5 to operational 4 |
| reported_deployment; pilot_reported | yes/no/NA | Deduplicate supported application IDs, same actor/scope/time; retain unresolved claims separately |
| ai_investment/partnership/risk/governance; risk_category | yes/no/NA; financial/operational/competitive/regulatory/third_party/capacity/misuse/reputational/cybersecurity/privacy/intellectual_property/model_quality/bias/safety/workforce/environmental/NA | Categories overlap and do not imply implementation |
| quantified_outcome; outcome_attribution; outcome_metric | yes/no/NA; explicit_application/shared_drivers/unlinked/ai_general/unclear/NA; named text | Shared-driver financial metrics are not qualifying AI results; NA is not zero |
| confidence; review flag; human_validated | high/medium/low; yes/no; no throughout | Review flags prioritize future checks, not unfinished coding |
| context fields; rationale; uncertainty; duplicate_group_id; record_type; annotation_version | Audit strings; claim/screening | Preserve context, repeated disclosure and correction history |

Multi-label fields use **|**. Literal **NA** means insufficient/inapplicable/missing evidence; binary no means absent in this claim, not absent firm activity. Undefined time or actor is unclear; relevance/eligibility ambiguity is uncertain. Never take the maximum stage across unrelated tasks or equate a planned extension with proof that it is implemented merely because an existing product has Stage 4 evidence. Distinct claims sharing evidence words cannot be added as validated topic share.

Sector, SEC industry, CIK, filing identity, primary URLs, checksums, parser version and XOM continuity fields reside in sources_downloaded.csv. Existing document metrics retain their columns. No new primary aggregate CSV or notebook changes were made.

## 7. Quality assurance, preservation and continuation

Actual checks passed:

- 18 issuer/source identities, latest original 10-K selections and cutoff verified, including explicitly documented XOM predecessor exception
- 18 primary HTML checksums, closing document tags, inline XBRL CIK/form/report-date context and metadata verified
- 393 extraction records reproduced exactly from source; unique stable IDs and exact-text deduplication verified
- All word-count, candidate-count, word-share and nonoverlapping mention formulas reconciled
- Original 140 parent texts/locations/IDs, 15 calibration IDs, and all three lexical metric rows preserved; one Microsoft keyword-tag recomputation difference documented
- 447 unique claim IDs cover every one of 393 parents; no blank/unprocessed fields or orphan records
- All exact quotations/offsets/source lines/report periods, categories and numeric ranges verified
- Stage-ineligible/screening/risk-only safeguards, current-versus-historical timing, plan eligibility and Stage 5 mapping checked
- Named application identities reconcile across repetitions; claims and parent passages not used as application counts
- All rows unvalidated; no individual Stage 0, pilot, or Stage 5 claims
- Original CSV/report/script backups hash-verified; protocol, notebook, original raw files and calibration sample unchanged

Focused contextual stage/identity review corrected 12 records' context or identity/stage attributes; original completed batches remain intact and the correction log is preserved. This is semantic consistency review by the same AI annotator, not independent validation. No stage quotas were imposed.

All four canonical CSVs and this report are published through validated temporary files with exact recoverable backups. Original 20261008T073937Z backups remain intact; an additional publication-time backup protects the current canonical state. The SEC cache, eight verified annotation batches, authored decisions, corrections, QA summary and progress manifest support recovery. Protocol.md, the EDA notebook, calibration artifacts and original source files remain unchanged.

No acquisition failures remain. The XOM corporate-group/predecessor choice is explicitly disclosed rather than presented as an exact current-CIK annual match. Table rendering, keyword omissions, coarse application identities and unvalidated semantic judgments remain material methodological limitations. Independent human evaluation is a future researcher-controlled phase and was not begun.
