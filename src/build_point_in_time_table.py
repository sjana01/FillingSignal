"""
Build a clean, honest table linking each 10-K's filing date to
what the stock did afterward.

What this does:
- For each company, reads its price history and its list of 10-K filing dates
- For each filing date, finds the price on that date (or the next trading
  day the market was open) and the price ~1 month and ~3 months later
- Calculates the % return over each window
- Combines everything into one table and saves it

Output:
    data/processed/point_in_time_table.csv
"""

import pandas as pd

from config import COMPANY_LIST, PRICES_DIR, FILINGS_DIR, PROCESSED_DIR

# Trading days (not calendar days) roughly matching 1 month and 3 months.
# Markets are open ~21 days/month, so:
ONE_MONTH_TRADING_DAYS = 21
THREE_MONTH_TRADING_DAYS = 63


def load_prices(ticker: str) -> pd.DataFrame | None:
    """Load one company's price history, or None if we don't have it."""
    path = PRICES_DIR / f"{ticker}.csv"
    if not path.exists():
        return None

    # yfinance saves a couple of header rows; skip them and just keep
    # Date + Close columns, which is all we need here.
    prices = pd.read_csv(path, skiprows=[1, 2])
    prices = prices.rename(columns={"Price": "Date"})
    prices["Date"] = pd.to_datetime(prices["Date"])
    prices = prices.sort_values("Date").reset_index(drop=True)
    return prices[["Date", "Close"]]


def load_filing_dates(ticker: str) -> pd.DataFrame | None:
    """Load one company's list of 10-K filing dates, or None if missing."""
    path = FILINGS_DIR / ticker / "filing_index.csv"
    if not path.exists():
        return None

    filings = pd.read_csv(path)
    filings["filingDate"] = pd.to_datetime(filings["filingDate"])
    return filings[["filingDate"]]


def price_on_or_after(prices: pd.DataFrame, target_date: pd.Timestamp) -> tuple:
    """
    Find the first trading day on or after target_date, and return
    (that date, that closing price, its row position). Markets are
    closed on weekends/holidays, so we can't just look up target_date
    directly -- we need the next day trading actually happened.
    """
    later_rows = prices[prices["Date"] >= target_date]
    if later_rows.empty:
        return None, None, None
    row = later_rows.iloc[0]
    position = later_rows.index[0]
    return row["Date"], row["Close"], position


def build_table_for_company(ticker: str) -> pd.DataFrame:
    """Build the point-in-time rows for a single company."""
    prices = load_prices(ticker)
    filings = load_filing_dates(ticker)

    if prices is None or filings is None or prices.empty or filings.empty:
        return pd.DataFrame()

    rows = []
    for filing_date in filings["filingDate"]:
        # Price on (or just after) the filing date -- our starting point
        start_date, start_price, start_pos = price_on_or_after(prices, filing_date)
        if start_price is None:
            continue

        # Price ~1 month later
        pos_1m = start_pos + ONE_MONTH_TRADING_DAYS
        price_1m = prices["Close"].iloc[pos_1m] if pos_1m < len(prices) else None

        # Price ~3 months later
        pos_3m = start_pos + THREE_MONTH_TRADING_DAYS
        price_3m = prices["Close"].iloc[pos_3m] if pos_3m < len(prices) else None

        rows.append({
            "ticker": ticker,
            "filing_date": filing_date,
            "start_date": start_date,
            "start_price": start_price,
            "return_1m": (price_1m / start_price - 1) if price_1m else None,
            "return_3m": (price_3m / start_price - 1) if price_3m else None,
        })

    return pd.DataFrame(rows)


def main():
    companies = pd.read_csv(COMPANY_LIST)
    all_tables = []

    for i, ticker in enumerate(companies["Symbol"], start=1):
        table = build_table_for_company(ticker)
        if table.empty:
            print(f"[{i}/{len(companies)}] {ticker}: no usable data, skipping")
        else:
            print(f"[{i}/{len(companies)}] {ticker}: {len(table)} filings processed")
            all_tables.append(table)

    final_table = pd.concat(all_tables, ignore_index=True)

    # Drop rows where we couldn't compute a 3-month return (too recent a filing)
    before = len(final_table)
    final_table = final_table.dropna(subset=["return_3m"])
    print(f"\nDropped {before - len(final_table)} rows with no 3-month return yet")

    out_path = PROCESSED_DIR / "point_in_time_table.csv"
    final_table.to_csv(out_path, index=False)
    print(f"\nSaved {len(final_table)} rows to {out_path}")
    print(final_table.head())


if __name__ == "__main__":
    main()