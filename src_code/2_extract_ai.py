import csv
import argparse
import hashlib
import os
import re
from collections import Counter
from pathlib import Path


def source_files(metadata_path):
    with metadata_path.open(encoding="utf-8-sig", newline="") as f:
        metadata = list(csv.DictReader(f))
    if len({r['ticker'] for r in metadata}) != len(metadata):
        raise ValueError('One selected filing per ticker required')
    return {r['ticker']: r.get('source_file') or f"{r['ticker']}_10K_{r['filing_date']}.txt"
            for r in metadata if r.get('download_status', 'verified') == 'verified'}


def passage_id(ticker, filename, line_number, text):
    value='\0'.join([ticker, filename, str(int(line_number)), text])
    return f"{Path(filename).stem}:L{line_number}:{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"
KEYWORDS = [
    "artificial intelligence",
    "generative AI",
    "machine learning",
    "large language model",
    "AI model",
    "LLM",
    "AI-powered",
    "AI-driven",
    "copilot",
    "agentic AI",
    "AI",
]
PATTERNS = [
    (keyword, re.compile(r"\b" + re.escape(keyword).replace(r"\ ", r"\s+") + r"\b", re.IGNORECASE))
    for keyword in KEYWORDS
]


def extract_passages(text):
    lines = text.splitlines(keepends=True)
    start = None
    seen = set()
    for index, line in enumerate(lines + [""]):
        if line.strip():
            if start is None:
                start = index
            continue
        if start is None:
            continue

        passage = "".join(lines[start:index])
        matched = [keyword for keyword, pattern in PATTERNS if pattern.search(passage)]
        if matched and passage not in seen:
            seen.add(passage)
            yield start + 1, "; ".join(matched), passage
        start = None


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', type=Path, default=root/'data/sources_downloaded.csv')
    parser.add_argument('--output', type=Path, default=root/'data/ai_passages.csv')
    args = parser.parse_args()
    sources = source_files(args.sources)
    rows = []
    for ticker, filename in sources.items():
        with (root / "data" / "raw" / filename).open(encoding="utf-8", newline="") as source:
            text = source.read()
        for line_number, matched_keywords, passage_text in extract_passages(text):
            rows.append({
                "ticker": ticker,
                "source_file": filename,
                "line_number": line_number,
                "matched_keywords": matched_keywords,
                "passage_text": passage_text,
                "passage_id": passage_id(ticker, filename, line_number, passage_text),
            })

    assert len({r['passage_id'] for r in rows}) == len(rows)
    output = args.output
    temporary = output.with_name(output.name+'.tmp')
    with temporary.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=[
            "ticker", "source_file", "line_number", "matched_keywords", "passage_text", "passage_id",
        ])
        writer.writeheader()
        writer.writerows(rows)
    if output.exists():
        # Never overwrite a dataset without a recoverable exact copy.
        from datetime import datetime, timezone
        backup=root/'data/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')/output.name
        backup.parent.mkdir(parents=True,exist_ok=True)
        backup.write_bytes(output.read_bytes())
        assert backup.read_bytes()==output.read_bytes()
    os.replace(temporary, output)

    counts = Counter(row["ticker"] for row in rows)
    for ticker in sources:
        print(f"{ticker}: {counts[ticker]} candidate passages")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
