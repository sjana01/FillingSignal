"""
Shared settings used by every script in the project.
Change dates or folders here once, instead of in five different files.
"""

from pathlib import Path

# Project root = one level up from this file
ROOT = Path(__file__).resolve().parent.parent

# Where raw and processed data live
PRICES_DIR = ROOT / "data" / "prices"
FILINGS_DIR = ROOT / "data" / "filings"
PROCESSED_DIR = ROOT / "data" / "processed"

# The list of ~80 companies you sampled earlier
COMPANY_LIST = ROOT / "data" / "sp500_sample_80.csv"

# How far back to pull data
START_DATE = "2018-01-01"
END_DATE = "2026-06-30"

# SEC EDGAR requires you to identify yourself in every request.
# Replace with your own name/email -- this is a courtesy rule they enforce.
SEC_USER_AGENT = "Santanil Jana santanil.jana@gmail.com"
