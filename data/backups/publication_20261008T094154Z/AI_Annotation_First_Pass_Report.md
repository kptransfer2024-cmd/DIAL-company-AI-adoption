# Corporate AI Strategy and Adoption: First-Pass Annotation

**Status:** Preliminary AI-generated, disclosure-based annotations; not human validated.  
**Protocol:** Existing Protocol.md, unchanged.  
**Version:** first_pass_2026_10_08_v1.

## 1. Coverage and results

All **140 candidate passages** are represented by **200 annotation rows**: 184 substantive claims and 16 screening records. Splitting preserves independently interpretable applications, strategy, investment, governance, and risk statements. Screening records retain non-substantive or uncertain passages. Coverage concerns extracted candidates, not a comprehensive semantic review of every paragraph in the filings.

| Claim-level relevance | Rows |
|---|---:|
| substantive | 184 |
| context_only | 7 |
| uncertain | 8 |
| irrelevant | 1 |
| **Total** | **200** |

| Reported adoption evidence | Rows |
|---|---:|
| Stage 1: strategic discussion | 32 |
| Stage 2: concrete application plan | 0 |
| Stage 3: actual pilot/test | 0 |
| Stage 4: reported current deployment/product provision | 14 |
| Stage 5: deployment plus attributable realized numerical outcome | 0 |
| NA: inapplicable, uncertain, or insufficient evidence | 154 |

Stage 0 was never assigned: it requires adequate document/scope review. Zero qualifying Stage 2, 3, or 5 records does not establish absence of plans, pilots, or benefits. Broad investment plans and hypothetical risks do not qualify as application plans. The separate operational_stage field maps Stage 5 to 4.

## 2. Preliminary company comparison

| Firm | Parent passages | Rows | Substantive claims | Strategy claims | Current-deployment claims | Resolved application IDs | Review flags |
|---|---:|---:|---:|---:|---:|---:|---:|
| MSFT | 101 | 151 | 140 | 29 | 13 | 10 | 57 |
| WMT | 19 | 25 | 21 | 9 | 0 | 0 | 7 |
| JPM | 20 | 24 | 23 | 1 | 1 | 0 | 2 |

Reporting periods are fiscal ends: MSFT **2026-06-30**, WMT **2026-01-31**, JPM **2025-12-31**. Filing dates are separate metadata. Unequal source lengths, sector roles, and reporting periods prevent interpreting raw counts as comparative adoption rates.

Microsoft reports AI product/platform provision and internal cybersecurity use. Product provision is distinct from internal adoption. JPM reports current AI/ML estimation methods, but does not identify which listed tasks use AI; its deployment claim therefore has no invented application ID. Walmart's sampled language emphasizes strategy, investment, and risks without unambiguous current application deployment. This does not establish non-adoption.

There are **10 resolved application IDs** and **8 provisional IDs**. These describe identifiable disclosed applications at the chosen granularity, not an exhaustive inventory. Unresolved deployment claims remain outside these counts.

## 3. Decisions needing researcher attention

- **Application boundaries:** Four named LinkedIn monetized solution lines receive separate IDs. Identities are resolved at product-line granularity, but finer application boundaries require review; all four records have medium confidence and review flags. Broad JPM estimation methods and Microsoft's integrated security product family are not split into invented tasks.
- **Product evidence:** Present-tense provision, availability, or monetized use supports customer-facing deployment when the AI connection is established. Generic capabilities, branding alone, and proposed defenses do not. Surface AI-PC provision and Azure Foundry's contextual deployment linkage are flagged.
- **Strategy boundary:** Success requirements and AI skilling can evidence broad intent without deployment. Borderline normative strategy statements are flagged.
- **Quantification:** Commercial cloud growth jointly attributed to Copilot and E5 is not an application-specific AI outcome. Shared business quantities can have outcome_metric recorded with outcome_attribution=shared_drivers, while quantified_outcome=no. Users, seats, spending, and availability do not establish Stage 5.
- **Unknown evidence:** AI executive titles, agentic-shopping references, ambiguous Copilot brands, and conditional statements remain uncertain where context does not establish the necessary link.

**66 rows** require human review. All 200 rows remain unvalidated, including those without a priority review flag. No precision, recall, confusion matrix, or inter-coder reliability was estimated.

## 4. Coding and aggregation guidance

Multi-label application_scope, strategic_orientation, and risk_category use **|**. Literal **NA** denotes missing/inapplicable/insufficient evidence. A binary no means the coded attribute is absent from this claim, not that the firm lacks that activity. Unclear denotes entity/temporal ambiguity; uncertain denotes relevance or stage-eligibility uncertainty.

AI commitment requires explicit stated commitment. Forward-looking includes conditional risks and must not be treated as a commitment count. Specificity is separate from adoption stage for assessable substantive statements. The additional is_strategy_claim field identifies intent independently of orientation labels.

Same-application references share IDs only where actor, scope, and identity align. Identity status distinguishes resolved, provisional, not_identified, and NA. Count resolved and provisional IDs separately, excluding NA. Repeated disclosures remain source-linked records; duplicate_group_id marks identified repetition/continuations. Count unique parents for passage statistics and unique IDs for application statistics. Overlapping labels and quotations are intentional; rows are not independent application counts.

Merge unchanged document lexical metrics by ticker and source filename, adding reporting periods from source metadata first. No validated AI word share or full-document topic share was calculated. No notebook or aggregate CSV was created.

### Controlled categories

| Field | Allowed coding |
|---|---|
| ai_relevance | substantive, context_only, irrelevant, uncertain |
| focal_firm_evidence | yes, no, unclear |
| actor | focal_firm, customer, partner, competitor, industry, other, unclear |
| temporal_status | planned, current, historical, discontinued, hypothetical, unclear |
| application_scope | internal_operations, customer_facing_product, customer_adoption_claim, research_and_development, infrastructure_or_platform, partnership_or_investment, unclear_or_other; NA |
| ai_technology_type | genai, traditional_ml, mixed, unspecified_ai; NA |
| strategic_orientation | efficiency, innovation, customer_experience, revenue_growth, workforce_productivity, competitive_positioning, responsible_ai, security, infrastructure_capacity, other; NA |
| adoption_stage / specificity | protocol-defined integers; NA (no claim-level Stage 0) |
| binary attributes | yes, no, NA |
| stage_eligible | yes, no, uncertain |
| outcome_attribution | explicit_application, shared_drivers, ai_general, unlinked, unclear; NA |
| coding_confidence | high, medium, low |

Use-case descriptions, outcome_metric, rationale, and uncertainty notes are evidence-grounded text. Risk categories are financial, operational, competitive, regulatory, third_party, capacity, misuse, reputational, cybersecurity, privacy, intellectual_property, model_quality, bias, safety, workforce, environmental, or NA.

## 5. Provenance and integrity

Each row preserves the original source reference, exact quotation, and stable parent ID. Where the input has no ID, source filename, original line, ticker, and full-passage content hash define it; all 15 existing calibration IDs match. Claim IDs are reproducible for this annotation version. Additional audit fields record eligibility, operational stage, application identity, context consulted, quote offsets/lines, repetition groups, and version.

Quotation offsets are zero-based, half-open Unicode-character offsets in the unmodified decoded TXT source, not bytes. Source_line remains the parent's extraction line; evidence lines can differ where context was needed. Surrounding context was consulted selectively, without claiming full-document semantic review.

Checks passed after CSV round-trip:

- 140/140 unique input parents represented; 200 unique claim IDs.
- Every quotation matches the complete original source at recorded offsets; source references and periods resolve.
- Controlled categories, stage eligibility, current-deployment constraints, review flags, and application identities pass.
- Non-substantive and risk-only records have no adoption stages; no individual Stage 0 records.
- All 14 Stage 4 quotations were inspected for deployment support; no Stage 5 records identified.
- Counts reconcile directly to the core dataset; every row has human_validated=no.
- SHA-256 checks confirm all protected-file entries except document_metrics.ipynb remain unchanged, including protocol, raw sources, prior datasets, and scripts. The notebook changed during the session outside this annotation work; it was not edited or restored by this task.

Only ai_annotations.csv and this report were created in the project. Independent human evaluation and adjudication remain the next researcher-controlled phase.
