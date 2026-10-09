# Multi-role card coverage in opponent mulligan bonus draws

The [coverage kernel](../../tools/opponent_bonus_coverage.py) assigns each physical card class a count, Basic starting eligibility, and a set of strategic requirements it fulfills. The exact inclusion-exclusion formula counts distinct physical cards, including flexible cards that satisfy two requirements.

For 60 cards, 12 unrelated ordinary Basics, and two required families of four effective copies each:

| Flexible copies covering both roles | Distinct physical target cards | Probability of opening with both requirements | Which bonus draw gives the largest marginal gain |
| ---: | ---: | ---: | --- |
| 0 | 8 | 12.964829% | Fifth |
| 1 | 7 | 18.249957% | Fourth |
| 2 | 6 | 24.156036% | First |

Replacing exclusive copies with flexible copies decreases the count of distinct target cards while raising the joint-opening success probability. The increase in the bonus-draw marginal gains disappears when two dual-purpose cards are present in this example.

## Single-family theorem

For one required target family of K physical cards, set M=N-H, where N is deck size and H opening-hand size. Let alpha be the probability that a legal Basic opening misses the target. The probability of still missing after m bonus draws is

    alpha * (M-K)_m / (M)_m

with falling factorial notation. When the previous marginal gain is positive, consecutive gains have ratio

    (M-K-m) / (M-1-m).

The ratio never exceeds one for K at least one and equals one when K is one. Therefore one target family has non-increasing marginal detection value. Complementary multiple requirements can instead produce initially increasing gains.

## Reproduction

[coverage_reproduce.py](coverage_reproduce.py) checks the exact formula against independent physical-card enumeration of opening hands, Prize subsets, and bonus selections for two small decks with overlapping strategic roles. It also checks equality to the existing Basic-overlap model and the four-effective-copies benchmark. GitHub Actions runs both reproduction suites.
