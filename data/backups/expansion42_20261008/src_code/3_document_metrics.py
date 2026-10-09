import csv
import argparse
import os
import re
from importlib import import_module
from pathlib import Path

extract_ai = import_module("2_extract_ai")
PATTERNS = extract_ai.PATTERNS


MENTION_PATTERN = re.compile(
    "|".join(pattern.pattern for keyword, pattern in sorted(
        PATTERNS, key=lambda item: len(item[0]), reverse=True,
    )),
    re.IGNORECASE,
)


def count_mentions(text):
    return sum(1 for _ in MENTION_PATTERN.finditer(text))


def main():
    root = Path(__file__).resolve().parent.parent
    parser=argparse.ArgumentParser()
    parser.add_argument('--sources', type=Path, default=root/'data/sources_downloaded.csv')
    parser.add_argument('--passages', type=Path, default=root/'data/ai_passages.csv')
    parser.add_argument('--output', type=Path, default=root/'data/document_metrics.csv')
    args=parser.parse_args()
    sources=extract_ai.source_files(args.sources)
    with args.passages.open(encoding="utf-8-sig", newline="") as source:
        passages = list(csv.DictReader(source))
    for passage in passages:
        if sources.get(passage["ticker"]) != passage["source_file"]:
            raise ValueError("Candidate passage has an unexpected ticker or source file")

    rows = []
    for ticker, filename in sources.items():
        text = (root / "data" / "raw" / filename).read_text(encoding="utf-8")
        total_words = len(text.split())
        if total_words == 0:
            raise ValueError(f"Empty document: {filename}")
        candidates = [passage for passage in passages if passage["ticker"] == ticker]
        candidate_words = sum(len(passage["passage_text"].split()) for passage in candidates)
        mentions = count_mentions(text)
        rows.append({
            "ticker": ticker,
            "source_file": filename,
            "total_word_count": total_words,
            "ai_candidate_passage_count": len(candidates),
            "ai_candidate_word_count": candidate_words,
            "ai_candidate_word_share": candidate_words / total_words,
            "ai_mention_count": mentions,
            "ai_mentions_per_1000_words": mentions * 1000 / total_words,
        })

    output = args.output
    temporary=output.with_name(output.name+'.tmp')
    with temporary.open("w", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if output.exists():
        from datetime import datetime, timezone
        backup=root/'data/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')/output.name
        backup.parent.mkdir(parents=True,exist_ok=True)
        backup.write_bytes(output.read_bytes())
        assert backup.read_bytes()==output.read_bytes()
    os.replace(temporary,output)

    print("ticker\ttotal_word_count\tai_candidate_passage_count\tai_candidate_word_count"
          "\tai_candidate_word_share\tai_mention_count\tai_mentions_per_1000_words")
    for row in rows:
        print(f"{row['ticker']}\t{row['total_word_count']}\t{row['ai_candidate_passage_count']}"
              f"\t{row['ai_candidate_word_count']}\t{row['ai_candidate_word_share']:.6f}"
              f"\t{row['ai_mention_count']}\t{row['ai_mentions_per_1000_words']:.6f}")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
