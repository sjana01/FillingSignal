"""
Download annual report (10-K) text for every company on our list.

What this does:

- Reads the list of ~80 companies (with their SEC company ID, "CIK")
- Asks SEC EDGAR: "what filings has this company made, and when did each
  one become public?"
- Picks out just the 10-Ks (annual reports)
- Downloads the actual report text and saves it, one file per report

Note: SEC EDGAR is a free public API but asks that you identify yourself
in every request (see SEC_USER_AGENT in config.py) and that you don't
send more than ~10 requests/second. This script deliberately goes slowly.
"""

import time
import json
import pandas as pd
import requests

from config import COMPANY_LIST, FILINGS_DIR, SEC_USER_AGENT

HEADERS = {"User-Agent": SEC_USER_AGENT}


def get_filing_list(cik: int) -> dict:
    """Ask EDGAR for the full filing history of one company."""
    cik_padded = str(cik).zfill(10)  # EDGAR wants CIKs as 10 digits, e.g. 0000320193
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def extract_10k_filings(filing_data: dict) -> pd.DataFrame:
    """Pull out just the 10-K filings, with their public filing dates."""
    recent = filing_data["filings"]["recent"]
    df = pd.DataFrame({
        "form": recent["form"],
        "filingDate": recent["filingDate"],       # <- the date it became public
        "accessionNumber": recent["accessionNumber"],
        "primaryDocument": recent["primaryDocument"],
    })
    return df[df["form"] == "10-K"].reset_index(drop=True)


def download_filing_text(cik: int, accession_number: str, primary_document: str) -> str:
    """Download the actual text of one 10-K filing."""
    accession_nodashes = accession_number.replace("-", "")
    url = (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik}/{accession_nodashes}/{primary_document}"
    )
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text


def main():
    companies = pd.read_csv(COMPANY_LIST)

    for i, row in companies.iterrows():
        ticker, cik = row["Symbol"], int(row["CIK"])
        company_folder = FILINGS_DIR / ticker
        company_folder.mkdir(parents=True, exist_ok=True)

        print(f"[{i+1}/{len(companies)}] {ticker}: looking up filings...")

        try:
            filing_data = get_filing_list(cik)
            tenks = extract_10k_filings(filing_data)
        except Exception as e:
            print(f"  FAILED to get filing list for {ticker}: {e}")
            continue

        # Save the index of filing dates -- this is your point-in-time record
        tenks.to_csv(company_folder / "filing_index.csv", index=False)

        for _, filing in tenks.iterrows():
            out_path = company_folder / f"{filing['filingDate']}.html"
            if out_path.exists():
                continue  # already downloaded

            try:
                text = download_filing_text(
                    cik, filing["accessionNumber"], filing["primaryDocument"]
                )
                out_path.write_text(text, encoding="utf-8")
                print(f"  saved {filing['filingDate']}")
            except Exception as e:
                print(f"  FAILED to download {filing['filingDate']}: {e}")

            time.sleep(0.2)  # stay well under SEC's rate limit

    print("\nDone.")


if __name__ == "__main__":
    main()
