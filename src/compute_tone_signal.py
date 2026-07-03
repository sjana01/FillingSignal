"""
Score each filing's tone, then compute how much
that tone shifted from the previous year's filing. This shift is your
actual signal.

What this does:
- Reads each cleaned filing text
- Counts negative and positive words, divides by total word count
  -> gives a "negative density" and "positive density" per filing
- For each company, sorts filings by date and computes the change in
  negative density from one year to the next
- Merges this signal onto your Day 2 point-in-time table, matched to
  the correct filing (so it lines up with the correct forward return)

Output:
    data/processed/signal_table.csv
    -- this is the table you'll actually run the analysis on
"""

import re
import pandas as pd

from config import FILINGS_DIR, PROCESSED_DIR
from word_lists import NEGATIVE_WORDS, POSITIVE_WORDS


def score_filing_text(text: str) -> dict:
    """Count negative/positive words in a filing, normalized by length."""
    words = re.findall(r"[a-z']+", text.lower())
    total_words = len(words)

    if total_words == 0:
        return {"negative_density": None, "positive_density": None, "word_count": 0}

    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)

    return {
        "negative_density": neg_count / total_words,
        "positive_density": pos_count / total_words,
        "word_count": total_words,
    }


def score_all_filings() -> pd.DataFrame:
    """Score every cleaned filing across every company."""
    rows = []
    company_folders = [f for f in FILINGS_DIR.iterdir() if f.is_dir()]

    for i, folder in enumerate(company_folders, start=1):
        ticker = folder.name
        txt_files = list(folder.glob("*.txt"))

        for txt_path in txt_files:
            filing_date = txt_path.stem  # filename is the filing date, e.g. 2023-02-15
            text = txt_path.read_text(encoding="utf-8")
            scores = score_filing_text(text)
            scores["ticker"] = ticker
            scores["filing_date"] = filing_date
            rows.append(scores)

        print(f"[{i}/{len(company_folders)}] {ticker}: {len(txt_files)} filings scored")

    return pd.DataFrame(rows)


def add_year_over_year_shift(scored: pd.DataFrame) -> pd.DataFrame:
    """For each company, compute the change in tone vs. the prior filing."""
    scored["filing_date"] = pd.to_datetime(scored["filing_date"])
    scored = scored.sort_values(["ticker", "filing_date"]).reset_index(drop=True)

    # .diff() within each company: this year's value minus last year's
    scored["negative_density_change"] = scored.groupby("ticker")["negative_density"].diff()
    scored["positive_density_change"] = scored.groupby("ticker")["positive_density"].diff()

    # The very first filing for each company has nothing to compare
    # against, so it has no signal -- that's expected and fine.
    return scored


def main():
    print("Scoring filing text...")
    scored = score_all_filings()

    print("\nComputing year-over-year tone shift...")
    scored = add_year_over_year_shift(scored)

    # Bring in the returns table from Day 2
    returns_table = pd.read_csv(PROCESSED_DIR / "point_in_time_table.csv")
    returns_table["filing_date"] = pd.to_datetime(returns_table["filing_date"])

    combined = returns_table.merge(scored, on=["ticker", "filing_date"], how="inner")

    # Drop rows with no signal yet (first filing per company)
    before = len(combined)
    combined = combined.dropna(subset=["negative_density_change"])
    print(f"\nDropped {before - len(combined)} rows with no prior-year filing to compare against")

    out_path = PROCESSED_DIR / "signal_table.csv"
    combined.to_csv(out_path, index=False)
    print(f"\nSaved {len(combined)} rows to {out_path}")
    print(combined[["ticker", "filing_date", "negative_density_change", "return_3m"]].head(10))


if __name__ == "__main__":
    main()
