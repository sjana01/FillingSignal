"""
Two more checks before calling the signal "done" --

Check A: Sector concentration
    Is this signal working broadly, or is it really just one or two
    industries doing all the work? We check the correlation separately
    within each GICS sector.

Check B: Trading cost impact
    A real signal is only useful if it survives realistic trading
    costs. Since filings come once a year per company, you'd only
    trade on this signal about once a year per stock -- so costs
    should be small, but we check rather than assume.
"""

import pandas as pd
from scipy import stats

from config import PROCESSED_DIR, COMPANY_LIST

# A reasonable, conservative estimate of round-trip trading cost
# (buying + later selling) for a liquid, large-cap US stock.
# 0.20% = 20 basis points is a standard rule-of-thumb estimate.
ROUND_TRIP_COST = 0.0020


def check_sector_concentration(df: pd.DataFrame):
    print("=" * 60)
    print("CHECK A: Is the signal broad, or concentrated in one sector?")
    print("=" * 60)

    companies = pd.read_csv(COMPANY_LIST)[["Symbol", "GICS Sector"]]
    companies = companies.rename(columns={"Symbol": "ticker"})
    df = df.merge(companies, on="ticker", how="left")

    results = []
    for sector, group in df.groupby("GICS Sector"):
        if len(group) < 15:
            # Too few filings in this sector to say anything meaningful
            continue
        corr, p = stats.spearmanr(group["negative_density_change"], group["return_3m"])
        results.append({"sector": sector, "correlation": corr, "p_value": p, "count": len(group)})

    results_df = pd.DataFrame(results).sort_values("correlation", ascending=False)
    print(results_df.to_string(index=False))

    positive_sectors = (results_df["correlation"] > 0).sum()
    print(f"\n{positive_sectors} out of {len(results_df)} sectors show a positive correlation.")
    print("Look for: most sectors pointing the same direction (even if not all")
    print("statistically significant on their own -- sector-level samples are small).")
    print("A red flag would be one sector wildly positive and everything else near")
    print("zero or negative, which would suggest the overall result is really just")
    print("one industry's story rather than a general pattern.\n")

    return df


def check_trading_costs(df: pd.DataFrame):
    print("=" * 60)
    print("CHECK B: Does the signal survive realistic trading costs?")
    print("=" * 60)

    df = df.copy()
    df["group"] = pd.qcut(
        df["negative_density_change"], q=5,
        labels=["1 (most negative)", "2", "3", "4", "5 (most positive)"],
    )

    # A simple long/short portfolio: buy the "most positive shift" group,
    # short the "most negative shift" group -- the spread between them
    # is the return this strategy would earn.
    group_returns = df.groupby("group", observed=True)["return_3m"].mean()
    spread_return = group_returns["5 (most positive)"] - group_returns["1 (most negative)"]

    # Since this trades once a year (one filing per company per year),
    # you pay the round-trip cost roughly once per position per year.
    cost_adjusted_spread = spread_return - ROUND_TRIP_COST

    print(f"Raw long/short spread (group 5 minus group 1): {spread_return:.4f} "
          f"({spread_return*100:.2f}%)")
    print(f"Assumed round-trip trading cost per position:   {ROUND_TRIP_COST:.4f} "
          f"({ROUND_TRIP_COST*100:.2f}%)")
    print(f"Cost-adjusted spread:                            {cost_adjusted_spread:.4f} "
          f"({cost_adjusted_spread*100:.2f}%)")

    print("\nLook for: does the cost-adjusted spread stay clearly positive? Since")
    print("trading costs here are tiny relative to the spread you're seeing (this")
    print("is a low-turnover, once-a-year signal), costs shouldn't meaningfully")
    print("change the conclusion -- but it's worth showing you checked rather than")
    print("assumed.\n")


def main():
    df = pd.read_csv(PROCESSED_DIR / "signal_table.csv")
    df_with_sector = check_sector_concentration(df)
    check_trading_costs(df_with_sector)


if __name__ == "__main__":
    main()