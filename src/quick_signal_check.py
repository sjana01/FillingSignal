"""
Quick sanity check before formal testing: does a bigger negative tone
shift line up with worse returns afterward?

What this does:
- Splits all filings into 5 equal-sized groups ("quintiles"), from
  "tone got much more negative" to "tone got much more positive"
- For each group, prints the average return that followed
- If the signal is doing anything real, we should see the groups
  roughly line up in order (most negative shift -> lowest average
  return, most positive shift -> highest average return)

This is NOT the final test -- it's just a fast way to see if there's
anything worth formally testing before we invest time in the proper
validation step.
"""

import pandas as pd

from config import PROCESSED_DIR


def main():
    df = pd.read_csv(PROCESSED_DIR / "signal_table.csv")

    # Split into 5 equal-sized groups based on the tone shift value
    df["group"] = pd.qcut(
        df["negative_density_change"],
        q=5,
        labels=["1 (most negative shift)", "2", "3", "4", "5 (most positive shift)"],
    )

    summary = df.groupby("group", observed=True).agg(
        avg_return_1m=("return_1m", "mean"),
        avg_return_3m=("return_3m", "mean"),
        count=("return_3m", "count"),
    )

    print(summary)
    print()
    print("What to look for: does avg_return_3m roughly increase as you go")
    print("from group 1 to group 5? If yes, that's an encouraging early sign.")
    print("If it's flat or jumps around randomly, the signal may be weak or")
    print("noisy -- not a failure, just useful information before we test formally.")


if __name__ == "__main__":
    main()