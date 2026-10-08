# DIAL AI Strategy & Adoption

This project measures corporate AI strategy and reported adoption in an exploratory sample of 18 public companies across six sectors. The refreshed dataset contains 393 candidate passages and 447 preliminary AI-generated claim/screening records. All semantic annotations remain human-unvalidated. See [the research report](AI_Annotation_First_Pass_Report.md) for source selection, issuer exceptions, counts, and limitations.

## Files

| File | Purpose |
|---|---|
| `data/raw/MSFT_10K_2026-07-29.txt` | Microsoft 10-K source text |
| `data/raw/WMT_10K_2026-03-13.txt` | Walmart 10-K source text |
| `data/raw/JPM_10K_2026-02-13.txt` | JPMorgan Chase 10-K source text |
| `src_code/1_download.py` | Resolves SEC issuer/filing metadata and caches complete primary HTML; parses text consistently with `edgartools` |
| `data/sources_downloaded.csv` | 18 selected annual filings, sectors, industries, CIKs, dates, URLs, checksums, and the XOM predecessor exception |
| `src_code/2_extract_ai.py` | Extracts candidates from selected source metadata with stable passage IDs |
| `data/ai_passages.csv` | 393 candidates; original 140 texts and IDs retained |
| `data/ai_annotations.csv` | 447 preliminary source-grounded claims/screening records; 48 columns |
| `src_code/3_document_metrics.py` | Calculates document-level word counts and AI disclosure metrics |
| `data/document_metrics.csv` | One metrics row per ticker |
| `document_metrics.ipynb` | Loads and displays the metrics CSV using pandas |

The extraction and metrics scripts select complete filings through `sources_downloaded.csv`. They do not read the separate `.web.txt` files or the files in `data/processed/`. Original pilot data, annotations, and report remain recoverable in `data/backups/20261008T073937Z/`. Batch decisions, SEC cache, QA, and progress are in `data/checkpoints/expansion_20261008T073937Z/`.

## Extraction method

- A passage is a contiguous block of nonblank lines, separated from other passages by blank lines. Original passage text is preserved, and `line_number` is the one-based starting line in the source file.
- Matching is case-insensitive, uses word boundaries, and allows whitespace variations within multiword keywords.
- Keywords are defined in `src_code/2_extract_ai.py`: `artificial intelligence`, `generative AI`, `machine learning`, `large language model`, `AI model`, `LLM`, `AI-powered`, `AI-driven`, `copilot`, `agentic AI`, and `AI`.
- Each matching passage is included once per source document. Exact duplicate passage text within that document is omitted. `matched_keywords` lists all matching keywords, separated by semicolons.
- Extracted passages are candidates for review. Keyword matches alone do not establish actual AI adoption, investment, or business impact.

The candidate CSV retains `ticker`, `source_file`, `line_number`, `matched_keywords`, and `passage_text`, and adds stable `passage_id`. Multi-label annotation fields use `|`; literal `NA` denotes missing/inapplicable/insufficient evidence. Claims, parent passages, and application IDs have distinct counting units.

## Document metrics

Word counts use Python's whitespace-based `split()` method. AI mentions are counted across the full source document using a combined keyword pattern. Longer keywords take precedence, and overlapping matches are counted once: for example, `generative AI` counts as one mention rather than an additional match for `AI`.

| Metric | Definition |
|---|---|
| `total_word_count` | Number of whitespace-separated words in the full document |
| `ai_candidate_passage_count` | Number of candidate passages for the ticker in `data/ai_passages.csv` |
| `ai_candidate_word_count` | Total word count across those candidate passages |
| `ai_candidate_word_share` | Candidate word count divided by total document word count, expressed as a fraction |
| `ai_mention_count` | Number of nonoverlapping AI keyword matches in the full document |
| `ai_mentions_per_1000_words` | AI mention count divided by total document word count, multiplied by 1,000 |

Candidate word share includes all words in matching passages, including surrounding context. These metrics measure disclosure text and require interpretation before use as indicators of AI adoption.

## Running the scripts

Run these commands from the project directory using the existing Windows virtual environment:

```powershell
.\.venv\Scripts\python.exe -B .\src_code\2_extract_ai.py
.\.venv\Scripts\python.exe -B .\src_code\3_document_metrics.py
```

The numbered scripts in `src_code/` follow the download, extraction, and metrics sequence. Extraction must run before metrics calculation. Both extraction and metrics scripts use only the Python standard library. All three scripts resolve data paths from their own location, so data files are read and written in the project-level `data/` directory regardless of the working directory.

Both output CSVs already exist. Extraction and metrics validate staged output, create exact timestamped backups when the destination exists, and replace through temporary files. For research refreshes, use explicit staging paths rather than changing canonical data before annotation is complete. Both accept `--sources` and `--output`; metrics also accepts `--passages`.

To inspect existing results, open `document_metrics.ipynb` with a Python kernel that has pandas installed and run it with the project directory as the working directory. The notebook reads `data/document_metrics.csv`; it does not rerun extraction or recalculate metrics.

The downloader uses the existing contact-bearing identity, optionally overridden through `SEC_USER_AGENT`, and requires permitted SEC HTTPS access. It selects the latest original annual 10-K filed on/before October 8, 2026; `--tickers` accepts a subset of the approved sample. Verified downloads are reused. It stages metadata in the expansion checkpoint instead of publishing a partial canonical dataset. XOM's documented successor/predecessor continuity is handled explicitly.

To inspect the completed run, read `data/checkpoints/expansion_20261008T073937Z/progress.json` and `qa_summary.json`. The saved `annotation_io.py` serializes explicitly authored decisions and does not classify by keywords. `finalize.py` verifies complete staged coverage, original backup comparisons, sources, schema, and aggregation before atomic publication. No autonomous annotation or human evaluation starts merely by reopening this project.
