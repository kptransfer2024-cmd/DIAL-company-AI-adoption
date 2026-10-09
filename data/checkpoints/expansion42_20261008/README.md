# DIAL AI Strategy & Adoption

This existing research project now covers **42 public companies (seven per sector)** using official SEC primary annual Form 10-K filings selected at **October 8, 2026**. Results: **770 candidate passages, 844 archival records, 276 eligible core claims**. All semantic coding is preliminary AI-first and **not human-validated**. [Protocol.md](Protocol.md) remains unchanged; [the updated report](AI_Annotation_First_Pass_Report.md) contains actual results, metric definitions, every-field assessment and source-scope exceptions.

## Sample and sources

| Sector | Retained companies | Added companies |
| --- | --- | --- |
| Technology / Software | MSFT, ADBE, CRM | GOOGL, META, ORCL, NOW |
| Retail / Consumer Commerce | WMT, TGT, COST | AMZN, HD, LOW, KR |
| Financial Services / Banking | JPM, BAC, C | WFC, GS, MS, USB |
| Healthcare / Pharmaceuticals | JNJ, PFE, MRK | ABBV, BMY, LLY, AMGN |
| Industrials / Manufacturing | CAT, DE, HON | GE, RTX, ETN, MMM |
| Energy / Oil & Gas | XOM, CVX, COP | OXY, EOG, SLB, PSX |

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

Use full archival records for risk/governance, relevance, confidence and NA diagnostics; use all 42 firm rows for sector comparisons; use complete primary words for lexical intensity. Candidate word share is screening context coverage, **not substantive AI topic share**. Claims, passages, words and resolved applications have different units. Core columns are: `claim_id`, `passage_id`, `ticker`, `source_file`, `source_line`, `evidence_quote`, `ai_relevance`, `actor`, `temporal_status`, `application_scope`, `use_case_id`, `use_case`, `strategic_orientation`, `forward_looking`, `strategy_specificity`, `adoption_stage`, `reported_deployment`, `quantified_outcome`, `ai_risk`, `ai_governance`, `coding_confidence`, `needs_human_review`, `annotation_rationale`.

Stages require contextual actor/time/scope reasoning under Protocol.md. Concrete plans are Stage 2, actual experiments Stage 3, affirmative current routine use/products Stage 4. Stage 5 adds realized numerical results explicitly attributable to the same deployed application and maps to operational Stage 4 for implementation comparisons. Customer benefits, users/access counts, generic capabilities and unrelated revenues do not automatically qualify. Broad current use may establish deployment presence but no identifiable task count.

Distinct applications count **resolved issuer/task/period IDs**, deduplicating repeated claims: 109 across all statuses, 98 currently deployed (10 internal, 83 customer-facing, 5 R&D/infrastructure; no internal/product overlap here). Vendor product deployment is separate from internal operations. All semantic comparisons describe disclosures rather than independently verified adoption.

## Measurement and notebook

`total_word_count` uses whitespace split; `ai_mention_count` uses longest-first nonoverlapping boundary-based keyword matches; `ai_mentions_per_1000_words` = mentions ×1,000 / primary words. Candidate count/words/share remain extraction metadata. Compact semantic measures are counts of substantive, strategy, eligible and NA records; resolved all-status/deployed/internal/product application IDs; deployment presence; and full-archive risk/governance counts. Their precise definitions, units, denominators and source fields are tabulated in the report. Every row explicitly records completed AI candidate review and unassessed full-document absence. No maturity index or independently validated topic share is published.

The notebook covers overview, intensity, strategy/adoption, equal-company sector comparisons, NA/confidence diagnostics, and preliminary findings/limitations. It retains useful prior lexical summaries and plots while adding box/strip plots, heatmaps, stacked composition and deployment scatter. Technology's mean lexical density is 2.625/1,000 primary words; other sector means range 0.114–0.493. Product-provider scope is prominent. Unresolved task identities and WFC/USB incorporated-report scope limit comparisons; no significance or causal claims are made.

## Rerun with the project virtual environment

Run from the repository root. SEC requests require permitted HTTPS access and the existing contact-bearing User-Agent (`SEC_USER_AGENT` may override it); paced requests/cache reuse preserve fair access. Downloads stage metadata rather than silently publishing partial samples.

```powershell
.\.venv\Scripts\python.exe -B src_code/1_download.py
.\.venv\Scripts\python.exe -B src_code/2_extract_ai.py
.\.venv\Scripts\python.exe -B src_code/3_document_metrics.py
.\.venv\Scripts\python.exe -B -m unittest discover -s src_code -p test_document_metrics.py
.\.venv\Scripts\python.exe -B data/checkpoints/expansion42_20261008/execute_notebook.py
```

The first command reuses verified fixed-cutoff sources and stages `sources_downloaded.csv` in the current checkpoint. For a refresh, use that staged path with extraction's `--sources --output` and metrics' `--sources --passages --annotations --output`. Metrics require complete full-archive coverage, not the core file. Default extraction/metrics commands reproduce the current canonical snapshot. Existing output CSVs get timestamped exact backups and atomic per-file replacement. Separate `.web.txt`/`data/processed` material is not used.

To reconstruct saved annotation decisions and validate staged data (not perform a new annotation study):

```powershell
.\.venv\Scripts\python.exe -B data/checkpoints/expansion42_20261008/prepare_annotations.py
.\.venv\Scripts\python.exe -B src_code/3_document_metrics.py --sources data/checkpoints/expansion42_20261008/sources_downloaded.csv --passages data/checkpoints/expansion42_20261008/ai_passages.csv --annotations data/checkpoints/expansion42_20261008/ai_annotations_full.csv --output data/checkpoints/expansion42_20261008/document_metrics.csv
.\.venv\Scripts\python.exe -B data/checkpoints/expansion42_20261008/validate_outputs.py
```

Open the notebook using the project's Python kernel, with repository-root working directory, and run all cells. It reads relative canonical paths with no hardcoded firm counts; `DIAL_DATA_DIR` is an optional staging-test override. The execution helper forces the current interpreter and fails on cell errors. Minimal execution packages are nbformat 5.11.1 and nbclient 0.11.0; install if absent with `.\.venv\Scripts\python.exe -m pip install nbformat==5.11.1 nbclient==0.11.0`. Environment versions: pandas 3.0.6, NumPy 2.5.3, matplotlib 3.11.2, ipykernel 7.4.0, Python 3.13.7. See checkpoint processing_environment.json for the exact record.

## Recovery and validation status

Verified pre-expansion eight-file backups are in `data/backups/expansion42_20261008/`; earlier backups/checkpoints remain intact. Current progress, official SEC cache, immutable 16 annotation batches, explicit contextual decisions, quote-boundary corrections, QA, notebook execution and publication hashes live in `data/checkpoints/expansion42_20261008/`. Recover from progress.json; never rerun completed batch-save scripts. Annotation replay uses the preserved 48-field backup schema even after the canonical file becomes core-only. Source checkpoints were saved every three additional firms and annotations approximately every 50 parents.

All quotes/IDs/core-full links/42-firm metrics/source identities and backup hashes passed automated integrity checks. The notebook executes from top to bottom. No human validation, classification accuracy, extraction recall or intercoder reliability estimate exists. All 844 records need future independent validation; 131 carry priority review flags. Findings remain exploratory, selective, disclosure-based and scope-dependent. No Git commit/push or human validation study was automatically performed.
