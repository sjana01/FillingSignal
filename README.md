# FilingSignal

NLP-derived alpha signal from SEC 10-K filings, validated with point-in-time
data and purged cross-validation.

## What this project does

Tests whether changes in tone/language between a company's consecutive
annual reports (10-Ks) predict how its stock performs afterward — using
data handled the way a real investment process would require: no lookahead
bias, no survivorship bias, and honest validation.

## Setup

```bash
pip install -r requirements.txt
```

## How to run (in order)

```bash
cd src
python fetch_prices.py     # downloads stock price history for ~80 companies
python fetch_filings.py    # downloads 10-K annual report text for the same companies
```

## Project structure

```
FilingSignal/
├── README.md
├── requirements.txt
├── data/
│   ├── sp500_sample_80.csv                 the ~80 companies used in this study
│   ├── prices/                             raw price history, one file per company
│   ├── filings/                            raw 10-K text (.html) + cleaned text (.txt), one folder per company
│   └── processed/
│       ├── point_in_time_table.csv         filing dates matched to forward returns
│       ├── signal_table.csv                above + tone-shift signal 
│       └── signal_table_with_momentum.csv  above + momentum control 
├── src/
│   ├── config.py                           shared paths and settings
│   ├── fetch_prices.py                     download stock prices
│   ├── fetch_filings.py                    download 10-K filings
│   ├── build_point_in_time_table.py        match filings to forward returns
│   ├── clean_filing_text.py                strip HTML from raw filings
│   ├── word_lists.py                       negative/positive word lists
│   ├── compute_tone_signal.py              score tone, compute year-over-year shift
│   ├── quick_signal_check.py               quick quintile gut-check
│   ├── run_validation_checks.py            median robustness, momentum control, time-split test
│   └── check_sector_and_costs.py           sector concentration + trading cost check
├── notebooks/
│   └── results_and_plots.ipynb             narrated walkthrough with all key charts
└── output/
    ├── FilingSignal_writeup.md             full research note
    └── FilingSignal_writeup.pdf            polished PDF version
```

