"""
Word lists used to score the "tone" of a filing.

Important note for your write-up: this is a small starter list, good
enough to build and test the pipeline this week. The actual standard
used in published finance research is the Loughran-McDonald Master
Dictionary, a much larger, carefully validated word list built
specifically for financial text (regular negative-word lists trained on
news or literature don't work well here -- e.g. "liability" or "tax"
read as negative in everyday English but are neutral, routine words in
a financial filing).

Before your final write-up, swap this out for the real one:
https://sraf.nd.edu/loughranmcdonald-master-dictionary/
It's free to download (a CSV), and using it instead of this starter
list is a quick, easy upgrade that will make your results noticeably
more credible to anyone in finance who reviews this.
"""

NEGATIVE_WORDS = {
    "adverse", "adversely", "against", "against", "bankruptcy", "breach",
    "claim", "claims", "decline", "declined", "declining", "default",
    "deficiency", "delay", "delays", "deteriorate", "deteriorated",
    "difficult", "difficulty", "disruption", "downturn", "failure",
    "fail", "failed", "fraud", "impairment", "impaired", "investigation",
    "lawsuit", "litigation", "loss", "losses", "material weakness",
    "negative", "penalty", "recall", "restructuring", "risk", "risks",
    "shortfall", "termination", "uncertain", "uncertainty", "unfavorable",
    "volatile", "volatility", "weak", "weakness", "write-down", "writedown",
}

POSITIVE_WORDS = {
    "achieve", "achieved", "achievement", "benefit", "benefits", "efficient",
    "efficiency", "favorable", "gain", "gains", "grow", "growth", "improve",
    "improved", "improvement", "increase", "increased", "innovation",
    "opportunity", "opportunities", "outperform", "positive", "profit",
    "profitable", "record", "strength", "strong", "strongest", "success",
    "successful", "upgrade",
}
