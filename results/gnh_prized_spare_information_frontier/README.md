# Guzma & Hala spare searches: exact K0 vs K1 discard-price frontier

## Question

In the [Aichi omitted-action witness](../gnh_optional_paid_duplicate_search/),
the player already holds TM: Evolution and Jet Energy, and the hidden
twelve-card pool contains spare copies of each, Artazon, one desired
Ticket-role Item, and eight other distinct cards.

A prior legal search could reveal the six initial Prize identities,
but might itself move cards. Here we ask a narrower **information-only
counterfactual**: if a player could observe the hidden Prize placement
*without changing material state*, how much would that observation
improve the decision to pay Guzma & Hala's two-card optional cost?

The payment is a genuine **on-play choice** before G&H's own Stadium
search. K0 must use one common pay-or-keep decision across all hidden
Prize worlds. K1 may choose separately after seeing the actual Prize
composition.

## Exact model

Let `U=12` unseen labeled cards contain Artazon, a spare
TM: Evolution, a spare Jet Energy, Ticket, and eight other cards.
Place `P` uniform Prizes and let unused Jirachi Stellar Wish
inspect five cards of the remaining deck after G&H searches.

The choice to **keep** the two disposable hand cards searches Artazon
if available. The choice to **pay** discards two otherwise expendable
hand cards before searching; after this commitment the player can
retrieve Artazon plus spare TM and Jet if each is unprized.
Their separate Tool and Special Energy categories permit taking
both in the paid action. This is a valid K0-contingent search policy:
the named fetches themselves happen after the player learns what
is currently searchable.

We assign a hypothetical future continuation penalty `lambda >= 0`
for losing the two discarded hand cards. Each world's payoff is its
exact conditional Ticket-in-top-five probability minus `lambda`
if paid. This scalar penalty is an **illustrative cost parameter**,
not a measured competitive card value.

Write `a_w` for the no-pay Ticket probability and `b_w` for the
paid Ticket probability in physical Prize world `w`.
Then

`K0(lambda)=max(E[a], E[b]-lambda)`

and

`K1(lambda)=E[max(a_w,b_w-lambda)]`.

The value of idealized information is `K1-K0`, which is nonnegative.

## Results

The [Prize-invariant thinning theorem](../prized_filler_search_invariance/)
proves that for every `P=0..4` in this toy,

- `E[a]=5/11`;
- `E[b]=5/9`;
- the single K0 action-switch penalty is exactly
  `E[b-a]=10/99 ≈ 0.101010101`.

Thus average gross thinning value is **independent of Prize count**,
even though which cards are Prized changes the preferred action in
individual worlds.

For `P=2`, all 66 labeled Prize configurations produce the following
physical gain distribution before discarding the cards' continuation
value:

| World-specific benefit `b-a` | Prize configurations |
| ---: | ---: |
| 0 | 12 |
| 1/18 | 2 |
| 5/72 | 16 |
| 1/8 | 8 |
| 10/63 | 28 |
| **Total** | **66** |

At `lambda=1/10`, the K0 player narrowly prefers paying:

| Policy | Exact payoff | Approximate payoff |
| --- | ---: | ---: |
| K0 no payment | 5/11 | 0.45454545 |
| K0 payment, cost included | 41/90 | 0.45555556 |
| K1 payoff | 1433/2970 | 0.48249158 |
| **K1 improvement over optimal K0** | **8/297** | **+0.02693603** |

These are units of a synthetic one-Ticket-access probability
objective, not game-win percentages.

The information premium reaches its maximum over nonnegative
penalties when the two K0 choices tie, at
`lambda=10/99`. For `P=2`, that maximum is
`179/6534 ≈ 0.02739516`.

Prize uncertainty changes option value despite unchanged average
gross search advantage:

| Uniform hidden Prizes `P` | Maximum K1 information premium at `lambda=10/99` |
| ---: | ---: |
| 0 | 0 |
| 1 | 19/1188 ≈ 0.01599327 |
| 2 | 179/6534 ≈ 0.02739516 |
| 3 | 151/4356 ≈ 0.03466483 |
| 4 | 415/9801 ≈ 0.04234262 |

For the two-option model, the maximizing property follows because
`V(lambda) = E[(b-a-lambda)_+] - max(E[b-a]-lambda,0)`.
For `lambda` below `E[b-a]`, its slope is
`Pr(b-a<=lambda)` (nonnegative), and above it its slope is
`-Pr(b-a>lambda)` (nonpositive). Hence the maximum occurs
at the K0 switch threshold.

## Verification

[Exact engine](../../tools/gnh_prized_spare_information_frontier.py);
[SFT](reproduce.py).

The SFT compares all labeled Prize worlds against an independent
grouped hypergeometric Prize-category oracle at eight discard
penalties and five Prize counts. For the `P=2` case, it also
enumerates every five-card Stellar Wish observation in each of
66 literal Prize configurations, verifies the rational gain
distribution, and asserts the exact payoff fractions.

## Boundaries

A free perfect Prize observation is an analytical reference only.
Real Tag Call has Item access costs, fetches physically materialized
cards, shuffles the deck, and may compete with other routes.
Its net value cannot be inferred from this model's K1 premium.

The model fixes a known hand with G&H available, two discardable
cards, held first TM and Jet, an eligible unused Jirachi, no
opponent lock, and a one-Ticket objective. Its `P=0..4`
sweep is an abstract information experiment; a normal initial
Expanded game uses six Prize cards, so the table must not be
misread as paper Expanded tournament frequencies. More general
sources, multi-target packets, or dynamic future discard value
would require a larger model.

The useful lesson for optimizer design is that equal *mean*
physical thinning benefit does **not** imply equal value of
information. The latter depends on the distribution of
state-specific action advantages and the cost threshold.
