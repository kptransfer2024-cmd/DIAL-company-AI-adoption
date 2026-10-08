import csv
import re
from collections import Counter
from pathlib import Path


SOURCE_FILES = {
    "MSFT": "MSFT_10K_2026-07-29.txt",
    "WMT": "WMT_10K_2026-03-13.txt",
    "JPM": "JPM_10K_2026-02-13.txt",
}
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
    rows = []
    for ticker, filename in SOURCE_FILES.items():
        with (root / "data" / "raw" / filename).open(encoding="utf-8", newline="") as source:
            text = source.read()
        for line_number, matched_keywords, passage_text in extract_passages(text):
            rows.append({
                "ticker": ticker,
                "source_file": filename,
                "line_number": line_number,
                "matched_keywords": matched_keywords,
                "passage_text": passage_text,
            })

    output = root / "data" / "ai_passages.csv"
    with output.open("x", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=[
            "ticker", "source_file", "line_number", "matched_keywords", "passage_text",
        ])
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["ticker"] for row in rows)
    for ticker in SOURCE_FILES:
        print(f"{ticker}: {counts[ticker]} candidate passages")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
