
from pathlib import Path
from edgar import Company, set_identity
import csv

set_identity("Research Student liukunpeng267@gmail.com")

tickers = ["MSFT", "WMT", "JPM"]
root = Path(__file__).resolve().parent.parent
output = root / "data" / "raw"
output.mkdir(parents=True, exist_ok=True)

records = []

for ticker in tickers:
    company = Company(ticker)
    filings = company.get_filings(
        form="10-K",
        filing_date="2025-01-01:2026-10-07",
        amendments=False
    )

    if filings.empty:
        print(f"{ticker}: no 10-K found")
        continue

    filing = filings.latest()
    html = filing.html()
    text = filing.text()

    if not html or not text:
        print(f"{ticker}: document unavailable")
        continue

    name = f"{ticker}_10K_{filing.filing_date}"
    (output / f"{name}.html").write_text(
        html, encoding="utf-8"
    )
    (output / f"{name}.txt").write_text(
        text, encoding="utf-8"
    )

    records.append({
        "ticker": ticker,
        "filing_date": str(filing.filing_date),
        "period_end": str(filing.period_of_report),
        "accession_number": filing.accession_no,
        "source_url": filing.url
    })

    print(f"Saved {name}")

with open(root / "data" / "sources_downloaded.csv", "w",
          newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file, fieldnames=[
            "ticker", "filing_date", "period_end",
            "accession_number", "source_url"
        ]
    )
    writer.writeheader()
    writer.writerows(records)
