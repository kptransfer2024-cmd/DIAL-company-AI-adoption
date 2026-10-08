# DIAL AI Strategy & Adoption

This project extracts AI-related candidate passages from the downloaded Microsoft (MSFT), Walmart (WMT), and JPMorgan Chase (JPM) 10-K filings and calculates document-level disclosure metrics.

## Files

| File | Purpose |
|---|---|
| `data/raw/MSFT_10K_2026-07-29.txt` | Microsoft 10-K source text |
| `data/raw/WMT_10K_2026-03-13.txt` | Walmart 10-K source text |
| `data/raw/JPM_10K_2026-02-13.txt` | JPMorgan Chase 10-K source text |
| `src_code/1_download.py` | Downloads filing HTML and text using `edgartools` and records source metadata |
| `data/sources_downloaded.csv` | Filing dates, reporting periods, accession numbers, and source URLs |
| `src_code/2_extract_ai.py` | Extracts candidate passages from the three source text files listed above |
| `data/ai_passages.csv` | 140 candidate passages: MSFT 101, WMT 19, JPM 20 |
| `src_code/3_document_metrics.py` | Calculates document-level word counts and AI disclosure metrics |
| `data/document_metrics.csv` | One metrics row per ticker |
| `document_metrics.ipynb` | Loads and displays the metrics CSV using pandas |

The extraction and metrics scripts use the explicitly named source files above. They do not read the separate `.web.txt` files or the files in `data/processed/`.

## Extraction method

- A passage is a contiguous block of nonblank lines, separated from other passages by blank lines. Original passage text is preserved, and `line_number` is the one-based starting line in the source file.
- Matching is case-insensitive, uses word boundaries, and allows whitespace variations within multiword keywords.
- Keywords are defined in `src_code/2_extract_ai.py`: `artificial intelligence`, `generative AI`, `machine learning`, `large language model`, `AI model`, `LLM`, `AI-powered`, `AI-driven`, `copilot`, `agentic AI`, and `AI`.
- Each matching passage is included once per source document. Exact duplicate passage text within that document is omitted. `matched_keywords` lists all matching keywords, separated by semicolons.
- Extracted passages are candidates for review. Keyword matches alone do not establish actual AI adoption, investment, or business impact.

The candidate CSV contains `ticker`, `source_file`, `line_number`, `matched_keywords`, and `passage_text`.

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

Both output CSVs already exist in this workspace. The scripts create files in exclusive mode and raise `FileExistsError` if an output already exists. Before intentionally regenerating results, move the existing output files to a backup location or change the output paths in the scripts. The scripts do not overwrite existing CSVs.

To inspect existing results, open `document_metrics.ipynb` with a Python kernel that has pandas installed and run it with the project directory as the working directory. The notebook reads `data/document_metrics.csv`; it does not rerun extraction or recalculate metrics.

To download filings again, `src_code/1_download.py` requires `edgartools`, network access, and an appropriate SEC user identity configured in the script. Its filing-date range is fixed to `2025-01-01:2026-10-07`, and it selects the latest available 10-K in that range for each ticker. It writes raw files and source metadata; if downloaded filenames change, update `SOURCE_FILES` in `src_code/2_extract_ai.py` before extracting passages.
