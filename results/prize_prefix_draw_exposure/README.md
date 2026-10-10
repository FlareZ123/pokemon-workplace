# Exact draw-window exposure and shuffle value with a known deck prefix

## Question

The [variable-depth deck-prefix model](../prize_deck_prefix/) preserves known upcoming deck order after Prize/top swaps. How can a deck optimizer assign **exact draw-window probability** to that knowledge, including multiple copies and multiple target groups?

The answer is a combination of deterministic known-position counting and a hypergeometric tail over the remaining exchangeable deck suffix.

## Model

`tools/prize_prefix_draw_exposure.py` implements:

- `probability_target_exposure(belief, targets, draw_count, at_least, shuffle_first=False)`: probability that the next specified number of cards contains at least the required count of cards from target strategic groups.
- `uniform_shuffle_value(...)`: change in that probability if the entire current deck is uniformly shuffled before drawing.

Each physical support world contains a current top, k explicitly ordered following positions, and an exchangeable suffix with conserved card-group counts.

For a given world, let:

- `d` be the number of cards to draw;
- `h` be the number among the known top/prefix that fall inside those d positions;
- `k_hits` be the number of targets already present in those h positions;
- `R` be the number of cards in the unknown suffix;
- `M` be the number of target cards in that suffix;
- `u=d-h` be the count to draw from the unknown suffix.

The conditional probability of reaching target count `r` is:

\[
\sum_{x=\max(r-k_\mathrm{hits},0)}^{\min(M,u)}
\frac{\binom{M}{x}\binom{R-M}{u-x}}{\binom{R}{u}}.
\]

Impossible terms contribute zero. Average these world-conditional values over the belief masses to retain uncertainty about exact Prize positions and deck composition.

A full-deck shuffle destroys known order while keeping its material inventory. After the shuffle, the same hypergeometric calculation uses the **entire current deck**, including the formerly known top/prefix.

## Six-card order witness

Condition on a previously verified configuration in the [prefix result](../prize_deck_prefix/): two Prizes contain A and filler; the four-card deck sequence after Arc Phone is `B,C,D,filler`. The source-authorized previous observation makes the immediate order known.

The next two draws illustrate opposite effects from the **same shuffle**:

| Target | Exposure without shuffle | Exposure after full shuffle | Shuffle value |
| --- | ---: | ---: | ---: |
| C appears in next two | 100% | 50% | **−50 percentage points** |
| D appears in next two | 0% | 50% | **+50 percentage points** |

For the next three draws, the probability of obtaining **both C and D** is 100% without shuffling and 50% after full randomization.

Compressing this same exact deck inventory to an unknown-order suffix while retaining the known first card B incorrectly estimates the chance of C in the next two as **1/3**.

## Multi-copy threshold example

Consider a five-card deck `B,A1,A2,F1,F2`. The top B is known; the other four cards are exchangeable. The chance that the next **three** draws include **both copies of A** is:

\[
\frac{\binom{2}{2}}{\binom{4}{2}}=\frac16.
\]

If the full five-card deck is shuffled first, it becomes:

\[
\frac{\binom{2}{2}\binom{3}{1}}{\binom{5}{3}}=\frac3{10}.
\]

Thus the shuffle increases the probability of obtaining both copies within the draw window from **16.67%** to **30%**. This extends the singleton known-top shuffle-value boundary analyzed in [pre-reset shuffle value](../pre_reset_shuffle_value/).

## Verification

`results/prize_prefix_draw_exposure/reproduce.py` compares the derived exposure and shuffle probabilities against:

- all 24 permutations of the concrete `B,C,D,filler` four-card deck;
- all 120 labeled permutations of `A1,A2,B,F1,F2`, including the 24 conditioned orders with B on top;
- independent exact-`Fraction` combinatorial expectations.

The regression also tests invalid target groups, zero-length/overlong draw questions, and negative threshold requests.

## Assumptions and limits

This is a **direct card-exposure probability**, not a full tactical or expected-win-rate utility. It ignores card play costs, Supporter contention, discardability, lock, whether exposed cards can actually be used, and the opportunity cost of shuffling.

The unknown suffix must be exchangeably ordered. Source-authorized future-card peeks, deliberate deck stacking, or other deeper-order information require increasing the modeled prefix depth. A fully shuffled deck is assumed uniformly randomized; some card effects that manipulate only a partial deck do not satisfy this assumption.

For multiple target categories and a minimum total count, the tool counts each matching card toward one pooled threshold. Simultaneous independent requirements such as "at least one Energy and at least one Pokémon" need a multivariate hypergeometric extension.

## Next

Build a multi-category (per-group threshold) draw-window event model and integrate direct exposure value with the existing information gain, search-line feasibility, and connector opportunity-cost models.
