# FilingSignal: Tone Shifts in Annual Reports as a Predictor of Stock Returns

## Summary

This note tests whether a simple, text-based signal — the year-over-year
change in negative-word tone across a company's consecutive annual
reports (10-Ks) — predicts its stock return over the following one to
three months. Using a sample of 80 S&P 500 companies and 610 filing
events between 2018 and 2026, the signal shows a statistically
significant relationship with forward returns (correlation = 0.162,
p < 0.001), which survives a control for price momentum, holds up on
out-of-sample data, is broadly present across most sectors, and
persists after accounting for realistic trading costs. The result is
a promising pilot finding, not a finished production signal — its
limitations are discussed directly in Section 5.

## 1. Hypothesis

Public companies are required to file an annual report (a 10-K) that
includes, alongside audited financials, a substantial amount of
qualitative language: management's discussion of risks, competitive
pressures, and business conditions. Unlike a clean numeric figure such
as quarterly earnings, this kind of language is harder for the market
to process quickly and consistently — reading and interpreting a
150-page document is slower and more subjective than digesting a
single number.

The hypothesis tested here is that when a company's language shifts
meaningfully more negative from one year's filing to the next, that
shift reflects real information about deteriorating business
conditions that the market does not immediately, fully price in. If
true, that would produce a modest, gradual drift in the stock price
over the following months as the information is absorbed — rather than
an instant jump, which is what you would expect if the market fully
priced the change on the day of filing.

This is a specific, falsifiable prediction, and there were three clear
ways it could have failed: if the relationship disappeared once
controlling for a company's existing price momentum (it did not), if it
did not hold on data outside the period used to find it (it did), or if
it turned out to be driven by a single sector rather than a broad
pattern (it is not).

## 2. Data

The study uses 80 companies, sampled programmatically and
proportionally across all 11 GICS sectors from the S&P 500, so that no
single industry is over- or under-represented relative to its actual
weight in the index. Stock price history was sourced from Yahoo
Finance; 10-K filing text and filing dates were sourced from SEC EDGAR,
both free and publicly available. Filings span roughly 2018 through
mid-2026.

Each filing is matched to its actual public filing date — the date SEC
EDGAR records the document as filed — rather than the fiscal year it
describes, since a report covering fiscal year 2022 is typically not
made public until early-to-mid 2023. This ensures the study never uses
information before it was genuinely available to investors.

One limitation is worth stating plainly: the sample includes only
companies currently in the S&P 500, and does not include companies
that were removed from the index or delisted during the study period.
This introduces a mild survivorship bias, discussed further in Section
5. After matching filings to valid price data, the final working
sample is 610 filing events with both a usable prior-year comparison
and a forward return.

## 3. Methodology

Each filing is scored on a simple "negative density" measure: the
count of words matching a finance-specific negative word list, divided
by the filing's total word count. A starter word list was used for
this pilot; the standard, more rigorously validated list used in
published finance research is the Loughran-McDonald Master Dictionary,
and swapping it in is a natural next step before treating this as a
finished result rather than a pilot.

The signal tested is not the raw tone score itself, but its
year-over-year *change*. Some companies simply write in a consistently
cautious, legally hedged style regardless of how the business is
actually performing; what matters is a shift away from a company's own
normal baseline, not the baseline itself.

Three checks were used to validate the signal, chosen specifically to
rule out the most likely ways a result like this turns out to be
spurious:

- **Quintile sorting**, to see the shape of the relationship across the
  full range of the signal, rather than relying on a single summary
  statistic that could hide a non-linear or lopsided pattern.
- **A momentum control**, since a well-known effect in equities is that
  recently rising stocks tend to keep rising and recently falling
  stocks tend to keep falling. It's plausible that a tone shift is
  simply a byproduct of this — a company already performing poorly
  writes a gloomier report — rather than adding new information. This
  was tested directly by checking whether the signal's relationship
  with returns survives after removing the portion explainable by
  trailing three-month price momentum.
- **A time-based train/test split**, rather than a random split, since
  random splits can leak future information into the past when working
  with time-series data. The sample was divided chronologically, with
  the pattern's strength checked on data from after the split point,
  which was not used to establish the relationship in the first place.

## 4. Results

Sorting all 610 filing events into five equal-sized groups by the size
of their tone shift, from most-negative to most-positive, produces a
clear pattern at the extremes:

| Group | Tone shift | Avg. return (3m) | Median return (3m) |
|---|---|---|---|
| 1 | Most negative shift | -2.41% | -2.82% |
| 2 | | +0.37% | -1.39% |
| 3 | | -1.28% | -1.05% |
| 4 | | +2.27% | +1.48% |
| 5 | Most positive shift | +3.96% | +4.11% |

The middle groups are noisier and do not move in a perfectly straight
line — which is normal in real financial data — but the two extremes
move in the expected direction, with roughly a 6.4-percentage-point
spread in average return between the most-negative-shift group and the
most-positive-shift group. The median return follows the same pattern
as the mean, indicating this is not the result of a small number of
extreme outlier stocks.

The relationship is statistically significant: tone shift alone
correlates with the three-month forward return at 0.162 (p < 0.001).
After controlling for trailing three-month price momentum, the
correlation is essentially unchanged at 0.157 (p < 0.001) — meaning
the signal is not simply standing in for a stock's existing price
trend, but appears to carry distinct information.

Testing on a chronological split, the correlation in the training
period (2009–2024) was 0.122 (p = 0.012), and in the untouched test
period (2024–2026) it was 0.189 (p = 0.010) — the relationship not
only held up out-of-sample, it did not decay.

Breaking the result down by sector, 9 of 11 sectors show a positive
correlation between tone shift and forward return, ranging from 0.06
to 0.39. The two exceptions — Financials and Utilities — show
essentially flat correlations (-0.001 and -0.010 respectively), not
negative ones. A plausible explanation, offered as a hypothesis rather
than a confirmed finding, is that both sectors are heavily regulated
and produce filings with a large amount of standardized, boilerplate
legal language, which may dilute a simple word-counting approach's
ability to detect a genuine change in tone.

Finally, a simple long-short portfolio construction — buying the
most-positive-shift group and shorting the most-negative-shift group —
produces a raw spread of 6.37% over the holding period. Assuming a
conservative round-trip trading cost of 0.20% per position (reasonable
for liquid, large-cap US equities), and given that this signal only
triggers roughly once per company per year, the cost-adjusted spread
remains 6.17% — trading costs at this turnover level do not
meaningfully affect the conclusion.

## 5. Robustness & Limitations

This section is intended to be read as carefully as the results above.

- The word list used to score tone is a small, hand-built starter set
  for this pilot, not the field-standard Loughran-McDonald dictionary.
  Results should be treated as directional evidence that a richer,
  validated word list is worth testing, not as a finished measurement.
- The sample — 80 companies and 610 filing events — is a reasonable
  pilot size but modest relative to a production research process.
  The consistency of the result across checks is encouraging, but a
  larger sample would meaningfully increase confidence.
- The sample excludes companies that were delisted or removed from the
  S&P 500 during the study period, introducing a mild survivorship
  bias whose direction and size were not separately quantified here.
- Two of eleven sectors (Financials, Utilities) do not show the
  effect. This is reported directly rather than excluded from the
  sector table, and the explanation offered for it is a hypothesis,
  not a demonstrated cause.
- The signal is a single, simple feature. No attempt was made in this
  pilot to combine it with other data sources, or to test a richer
  language model in place of straightforward word-frequency counting.

## 6. Next Steps

With additional time and data, the natural extensions are: expanding beyond 80 companies; replacing the starter word list with
the full Loughran-McDonald dictionary; testing a richer, embedding-based measure of tone shift rather than simple word counting; including delisted companies to remove the survivorship bias noted above; and testing sector-neutral portfolio construction directly, rather than only checking sector-level correlations as a diagnostic.
