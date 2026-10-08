import csv
import re
from importlib import import_module
from pathlib import Path

extract_ai = import_module("2_extract_ai")
PATTERNS = extract_ai.PATTERNS
SOURCE_FILES = extract_ai.SOURCE_FILES


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
    with (root / "data" / "ai_passages.csv").open(encoding="utf-8-sig", newline="") as source:
        passages = list(csv.DictReader(source))
    for passage in passages:
        if SOURCE_FILES.get(passage["ticker"]) != passage["source_file"]:
            raise ValueError("Candidate passage has an unexpected ticker or source file")

    rows = []
    for ticker, filename in SOURCE_FILES.items():
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

    output = root / "data" / "document_metrics.csv"
    with output.open("x", encoding="utf-8-sig", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print("ticker\ttotal_word_count\tai_candidate_passage_count\tai_candidate_word_count"
          "\tai_candidate_word_share\tai_mention_count\tai_mentions_per_1000_words")
    for row in rows:
        print(f"{row['ticker']}\t{row['total_word_count']}\t{row['ai_candidate_passage_count']}"
              f"\t{row['ai_candidate_word_count']}\t{row['ai_candidate_word_share']:.6f}"
              f"\t{row['ai_mention_count']}\t{row['ai_mentions_per_1000_words']:.6f}")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
