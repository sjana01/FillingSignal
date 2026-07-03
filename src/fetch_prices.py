"""
Download daily stock prices for every company on the list.

What this does:
- Reads the list of ~80 companies
- For each one, downloads its daily price history from Yahoo Finance
- Saves one file per company into data/prices/
"""

import time
import pandas as pd
import yfinance as yf

from config import COMPANY_LIST, PRICES_DIR, START_DATE, END_DATE


def fetch_one_company(ticker: str) -> pd.DataFrame:
    """Download daily prices for a single ticker."""
    data = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        progress=False,
        auto_adjust=True,  # adjusts for stock splits/dividends automatically
    )
    return data


def main():
    companies = pd.read_csv(COMPANY_LIST)
    tickers = companies["Symbol"].tolist()

    print(f"Downloading prices for {len(tickers)} companies...")

    failed = []
    for i, ticker in enumerate(tickers, start=1):
        out_path = PRICES_DIR / f"{ticker}.csv"

        if out_path.exists():
            print(f"[{i}/{len(tickers)}] {ticker}: already downloaded, skipping")
            continue

        try:
            df = fetch_one_company(ticker)
            if df.empty:
                print(f"[{i}/{len(tickers)}] {ticker}: no data returned")
                failed.append(ticker)
                continue

            df.to_csv(out_path)
            print(f"[{i}/{len(tickers)}] {ticker}: saved {len(df)} rows")

        except Exception as e:
            print(f"[{i}/{len(tickers)}] {ticker}: FAILED ({e})")
            failed.append(ticker)

        time.sleep(0.5)  # be polite to the free API, don't hammer it

    if failed:
        print("\nCompanies that failed, check these manually:")
        print(failed)
    else:
        print("\nAll companies downloaded successfully.")


if __name__ == "__main__":
    main()
