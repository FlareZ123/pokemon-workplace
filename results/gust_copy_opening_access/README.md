# Multi-copy gust access after a Basic-valid opening

## Question

How often are one, two, three or four copies of a non-Basic gust card naturally accessible in the accepted opening hand and the next one or two draws? This extends [single-source physical access](../opposing_gust_opening_access/) to a full probability distribution over the number of source copies seen. The copies are interchangeable, and replacing a filler with another source preserves deck size and Basic count.

## Formula

Let T be deck size, B the number of Basic Pokémon, G the number of identical non-Basic gust sources, H the initial hand size, P the Prize count and k the number of natural draws. We condition on a hand containing at least one Basic. Its unnormalized count is

A = C(T,H) - C(T-B,H).

The number of accepted hands containing **no** source is

A0 = C(T-G,H) - C(T-G-B,H).

After such a source-free hand, all G sources remain among T-H unseen cards. Because the Prize split and deck order are uniform, probability of seeing none in the next k drawable positions is C(T-H-G,k)/C(T-H,k). Thus

P(at least one source by k) = 1 - (A0/A) C(T-H-G,k)/C(T-H,k).

The [reusable source](../../tools/gust_copy_opening_access.py) additionally sums a two-stage multivariate hypergeometric distribution to return exact probabilities for **0 through G** sources seen. The formulas are independent of P when 0 <= k <= T-H-P, although they still average over possible Prized sources. They exclude additional search, mulligan bonus draws, Prize retrieval and other draw effects.

## Hypothetical 60-card results

All percentages below condition on a Basic-valid seven-card opening, with six Prizes set and two subsequent natural draws.

| Non-Basic copies | At least 1, B=4 | At least 2, B=4 | At least 1, B=16 | At least 2, B=16 |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 13.7947% | 0% | 14.5503% | 0% |
| 2 | 25.8946% | 1.6947% | 27.2067% | 1.8940% |
| 3 | 36.4815% | 4.7208% | 38.1852% | 5.2495% |
| 4 | 45.7205% | 8.7644% | 47.6811% | 9.6975% |

For B=4, the incremental gain in **at least one copy by two draws** from copies 1, 2, 3 and 4 is +13.7947, +12.0999, +10.5869 and +9.2390 percentage points. The increments decline over the tested B=4,8,12,16,20 populations and both first- and second-draw endpoints.

The same four-copy B=4 access probability is 45.7205%, compared with an **unconditioned** nine-card visibility estimate of 48.7527%. Conditioning on a valid Basic opening matters for multi-copy non-Basic resources.

## Reproduction

The [independent reproducer](reproduce.py) compares the hypergeometric method against **54 exhaustive labeled toy populations** of ten cards, varying Basics, source copies, Prize count and the number of natural draws. It separately tests 40 exact 60-card compositions, verifies the full probability distribution sums to one, checks mean source count against the singleton marginal, and confirms invariance across four feasible Prize counts.

Run `python -m results.gust_copy_opening_access.reproduce` at the repository root.

## Interpretation

This result models the **availability of copies**. It does not assume that seeing multiple Boss's Orders permits playing multiple Supporters in a single turn, that two Counter Catchers have independent value, or that a drawn source is executable under locks or costs. It provides exact arrival probabilities that can be composed with more realistic source-usage, Supporter contention and tactical Prize-race models.
