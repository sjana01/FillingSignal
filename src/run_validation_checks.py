"""
Three checks to see if the signal is real, or just noise/
something obvious in disguise.

Check 1: Median robustness
    Does the pattern hold for the "typical" filing, not just skewed by
    a few extreme movers?

Check 2: Momentum control
    Is the tone shift secretly just standing in for "the stock was
    already falling/rising before the filing"? We add trailing 3-month
    return as a control and see if tone shift still matters once that's
    accounted for.

Check 3: Time-split test
    Fit on the earlier years, test on the later years the model hasn't
    touched. This is the honest test of whether the pattern generalizes,
    rather than just describing the data we already looked at.
"""

import pandas as pd
import numpy as np
from scipy import stats

from config import PROCESSED_DIR, PRICES_DIR


# ---------------------------------------------------------------------
# Check 1: median robustness
# ---------------------------------------------------------------------

def check_median_robustness(df: pd.DataFrame):
    print("=" * 60)
    print("CHECK 1: Median robustness (not just skewed by outliers)")
    print("=" * 60)

    df = df.copy()
    df["group"] = pd.qcut(
        df["negative_density_change"], q=5,
        labels=["1 (most negative)", "2", "3", "4", "5 (most positive)"],
    )

    summary = df.groupby("group", observed=True).agg(
        mean_return_3m=("return_3m", "mean"),
        median_return_3m=("return_3m", "median"),
        count=("return_3m", "count"),
    )
    print(summary)
    print("\nLook for: does median_return_3m roughly increase from group 1 to 5,")
    print("similar to what the mean showed? If yes, it's not just outlier-driven.\n")


# ---------------------------------------------------------------------
# Check 2: momentum control
# ---------------------------------------------------------------------

def load_prices(ticker: str) -> pd.DataFrame | None:
    path = PRICES_DIR / f"{ticker}.csv"
    if not path.exists():
        return None
    prices = pd.read_csv(path, skiprows=[1, 2])
    prices = prices.rename(columns={"Price": "Date"})
    prices["Date"] = pd.to_datetime(prices["Date"])
    return prices.sort_values("Date").reset_index(drop=True)[["Date", "Close"]]


def compute_trailing_momentum(df: pd.DataFrame) -> pd.DataFrame:
    """For each row, compute the stock's return over the 3 months BEFORE the filing."""
    df = df.copy()
    df["start_date"] = pd.to_datetime(df["start_date"])
    momentum_values = []

    price_cache = {}
    for _, row in df.iterrows():
        ticker = row["ticker"]
        if ticker not in price_cache:
            price_cache[ticker] = load_prices(ticker)
        prices = price_cache[ticker]

        if prices is None:
            momentum_values.append(None)
            continue

        before = prices[prices["Date"] < row["start_date"]]
        if len(before) < 63:  # need ~3 months of trading days before this filing
            momentum_values.append(None)
            continue

        price_3m_ago = before["Close"].iloc[-63]
        price_now = before["Close"].iloc[-1]
        momentum_values.append(price_now / price_3m_ago - 1)

    df["momentum_3m"] = momentum_values
    return df


def check_momentum_control(df: pd.DataFrame):
    print("=" * 60)
    print("CHECK 2: Does the signal still matter after controlling for momentum?")
    print("=" * 60)

    df = df.dropna(subset=["momentum_3m", "negative_density_change", "return_3m"])

    # Simple correlation of tone shift with return, on its own
    raw_corr, raw_p = stats.spearmanr(df["negative_density_change"], df["return_3m"])
    print(f"Tone shift alone vs. return_3m:      correlation = {raw_corr:.3f}  (p = {raw_p:.3f})")

    # Momentum's own correlation with return, for reference
    mom_corr, mom_p = stats.spearmanr(df["momentum_3m"], df["return_3m"])
    print(f"Momentum alone vs. return_3m:        correlation = {mom_corr:.3f}  (p = {mom_p:.3f})")

    # Partial correlation: does tone shift still predict returns once
    # momentum's effect is subtracted out? Done by regressing both
    # variables on momentum, then correlating what's left over (the
    # "residuals") -- this is the standard, simple way to control for
    # a variable without needing a bigger stats package.
    def residualize(y, x):
        x = np.array(x).reshape(-1, 1)
        x = np.hstack([np.ones_like(x), x])  # add intercept
        coeffs, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
        predicted = x @ coeffs
        return y - predicted

    tone_resid = residualize(df["negative_density_change"].values, df["momentum_3m"].values)
    return_resid = residualize(df["return_3m"].values, df["momentum_3m"].values)

    partial_corr, partial_p = stats.spearmanr(tone_resid, return_resid)
    print(f"Tone shift vs. return_3m, controlling for momentum: "
          f"correlation = {partial_corr:.3f}  (p = {partial_p:.3f})")

    print("\nLook for: does the last number stay close to the first one, and still")
    print("have a low p-value (below 0.05)? If yes, tone shift is adding something")
    print("beyond what momentum already tells you. If it drops toward zero, the")
    print("tone signal may just be a proxy for momentum.\n")

    return df


# ---------------------------------------------------------------------
# Check 3: time-split test
# ---------------------------------------------------------------------

def check_time_split(df: pd.DataFrame):
    print("=" * 60)
    print("CHECK 3: Does it still work on data the pattern wasn't built on?")
    print("=" * 60)

    df = df.copy()
    df["filing_date"] = pd.to_datetime(df["filing_date"])
    df = df.sort_values("filing_date")
    split_point = int(len(df) * 0.7)
    train, test = df.iloc[:split_point], df.iloc[split_point:]

    print(f"Train period: {train['filing_date'].min().date()} to {train['filing_date'].max().date()} "
          f"({len(train)} rows)")
    print(f"Test period:  {test['filing_date'].min().date()} to {test['filing_date'].max().date()} "
          f"({len(test)} rows)")

    train_corr, train_p = stats.spearmanr(train["negative_density_change"], train["return_3m"])
    test_corr, test_p = stats.spearmanr(test["negative_density_change"], test["return_3m"])

    print(f"\nTrain period correlation: {train_corr:.3f}  (p = {train_p:.3f})")
    print(f"Test period correlation:  {test_corr:.3f}  (p = {test_p:.3f})")

    print("\nLook for: does the test period correlation have the SAME SIGN as the")
    print("train period (both positive, or both negative)? It doesn't need to be")
    print("identical in size -- real-world signals fade in and out -- but if the")
    print("sign flips or the test correlation is near zero, treat the signal with")
    print("caution: it may not have generalized beyond the period it was found in.\n")


def main():
    df = pd.read_csv(PROCESSED_DIR / "signal_table.csv")

    check_median_robustness(df)

    print("Computing trailing 3-month momentum for each filing (this takes a moment)...\n")
    df_with_momentum = compute_trailing_momentum(df)
    df_with_momentum.to_csv(PROCESSED_DIR / "signal_table_with_momentum.csv", index=False)
    check_momentum_control(df_with_momentum)

    check_time_split(df)


if __name__ == "__main__":
    main()