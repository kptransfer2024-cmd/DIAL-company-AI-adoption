# Expansion checkpoint and continuation plan

Status: blocked before source acquisition. This checkpoint is not an expanded analytical result.

## Preserved state

The four canonical CSVs and annotation report retain the three-company results. Exact copies, including the current downloader/extraction/metrics scripts, are in the backup directory recorded in progress.json; hashes.json verifies them. Protocol.md, all notebooks, calibration data, and raw sources were not changed. The 18 target issuers remain unverified for this expansion; local pilot metadata is not independent SEC verification.

## Blocking condition

The existing downloader contains a contact-bearing SEC identity. A direct Python HTTPS request to the Microsoft submissions API failed with WinError 10013: socket access forbidden by execution permissions. The browser tool could access SEC fair-access documentation but could not retrieve submissions JSON. No request pacing or script refactor can repair this permission restriction. No partial browser excerpt was saved as a complete filing. Do not bypass controls or introduce third-party mirrors.

## Resume from this directory

1. Read progress.json, then verify backup/original hashes. Reuse this checkpoint rather than making another backup of the same unchanged state.
2. In an execution environment permitting HTTPS to data.sec.gov and www.sec.gov, retry the submissions request with the existing identity. Resolve ticker mappings and issuer identities from official SEC data; select the latest original 10-K filed on/before 2026-10-08. Do not treat the original scripts' 2026-10-07 bound as the requested cutoff.
3. Refactor src_code/1_download.py minimally: configurable 18-ticker sample, metadata-driven selection, cache, conservative pacing/backoff, complete primary HTML plus consistently parsed TXT, per-issuer errors and amendments. Stage source metadata outside the canonical CSV. Checkpoint approximately every three firms. Verify the existing three accession identities before preserving their sources.
4. Make src_code/2_extract_ai.py source-metadata driven. Preserve keyword and exact-paragraph deduplication semantics unless a justified correction is documented. Add stable passage IDs matching the original annotation/calibration algorithm where source text is unchanged. Preserve existing columns. Generate a staged full-sample CSV and source-offset QA.
5. Make src_code/3_document_metrics.py use the selected source metadata rather than the three-name constant. Preserve whitespace word counts and nonoverlapping mention counting. Calculate all firms and validate source/passage reconciliation before atomic canonical replacement. If parsing changes, regenerate every firm's text and lexical metrics consistently without destroying old sources.
6. Fresh contextual protocol-based annotation, grouped by issuer, with roughly 50 original parents per persisted batch. Preserve all existing 48 annotation columns. Do not use earlier annotations as labels or implement keyword-to-stage scoring. Save exact quotes and offsets, uncertainty, and human_validated=no. Audit intended uses, pilots, deployed scope, and outcomes independently without stage quotas.
7. Mark each issuer's batches verified after provenance, coverage, category, stage, and use-case QA. Combine only complete validated batches; never overwrite the canonical annotation CSV with partial coverage. Preserve a precise progress manifest after each balanced checkpoint.
8. Atomically publish the four validated CSVs and refreshed report only under the user-authorized phase gates. Reconcile all issuers, sources, parents, claims, application IDs, counts and hashes. Keep failures/missing sources explicit. Check protocol/notebook/calibration preservation.

## Current reproducible paths

- Downloader: src_code/1_download.py (unchanged; still pilot-only).
- Extraction: src_code/2_extract_ai.py (unchanged; still pilot-only).
- Metrics: src_code/3_document_metrics.py (unchanged; still pilot-only).
- Interpreter: .venv/Scripts/python.exe.
- Next action: restore permitted SEC HTTPS access and complete Phase A; do not run the old downloader as if it implements the expanded design.

No human evaluation, new semantic annotations, expanded metrics, or canonical replacements have been performed.
