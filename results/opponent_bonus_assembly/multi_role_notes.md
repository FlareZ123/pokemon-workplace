# Multi-role card coverage in opponent mulligan bonus draws

The [coverage kernel](../../tools/opponent_bonus_coverage.py) assigns each physical card class a count, Basic starting eligibility, and a set of strategic requirements it fulfills. The exact inclusion-exclusion formula counts distinct physical cards, including flexible cards that satisfy two requirements.

For 60 cards, 12 unrelated ordinary Basics, and two required families of four effective copies each:

| Flexible copies covering both roles | Distinct physical target cards | Probability of opening with both requirements | Which bonus draw gives the largest marginal gain |
| ---: | ---: | ---: | --- |
| 0 | 8 | 12.964829% | Fifth |
| 1 | 7 | 18.249957% | Fourth |
| 2 | 6 | 24.156036% | First |

Replacing exclusive copies with flexible copies decreases the count of distinct target cards while raising the joint-opening success probability. The increase in the bonus-draw marginal gains disappears when two dual-purpose cards are present in this example.


**Capacity qualification:** This coverage-class calculation treats a card bearing two role labels as able to satisfy both requirements during the same use. For cards that can only choose one output, use the exact [one-use capacity correction](flexible_capacity_notes.md). Two flexible single-output cards produce a 13.168805 percentage-point overstatement in the illustrated 60-card opening.

## Single-family theorem

For one required target family of K physical cards, set M=N-H, where N is deck size and H opening-hand size. Let alpha be the probability that a legal Basic opening misses the target. The probability of still missing after m bonus draws is

    alpha * (M-K)_m / (M)_m

with falling factorial notation. When the previous marginal gain is positive, consecutive gains have ratio

    (M-K-m) / (M-1-m).

The ratio never exceeds one for K at least one and equals one when K is one. Therefore one target family has non-increasing marginal detection value. Complementary multiple requirements can instead produce initially increasing gains.

## Reproduction

[coverage_reproduce.py](coverage_reproduce.py) checks the exact formula against independent physical-card enumeration of opening hands, Prize subsets, and bonus selections for two small decks with overlapping strategic roles. It also checks equality to the existing Basic-overlap model and the four-effective-copies benchmark. GitHub Actions runs both reproduction suites.

## Consequence for the optimal setup decision

Using the existing count-dependent setup optimizer with own deck classes
4 ordinary Basics, 4 optional starters, 4 key cards and 48 filler,
binary own key-hand value, matchup payoff 6 and a 12-draw opponent cap,
the weak optional-only opening is kept on these prior-mulligan counts:

| Flexible opponent cards | Mulligan counts where weak optional opening is kept |
| ---: | --- |
| 0 | 2, 3, 4, 5 |
| 1 | None |
| 2 | None |

The exact code test now composes the new coverage model with the previously
validated count-dependent setup solver. Under equal *effective* four-copy
coverage for each required group, one dual-purpose opponent card is already
sufficient to eliminate the policy reversal at the illustrative payoff.
This is a property of the model, rather than a matchup calibration.
