# Exact K1 Prize knowledge improves an opponent's hand-reset policy in narrow states

## Question

The [two-objective opponent Supporter model](../beheeyem_opponent_self_target/) assumes the player knows how many copies of its own hypothetical four-copy target X are in hand but has **not** searched its deck. That is the human-concepts document's **K0** state. If the opponent has already performed a lawful full-deck search and knows how many X remain in its face-down Prizes, it moves to **K1**.

Can this additional information change whether playing Judge or Ace Trainer is worthwhile to obtain X, while also accounting for the resulting Beheeyem second-packet probability?

This study grants the information freely at the decision, isolating its **value-of-information upper bound**. There is no modeled cost, card, Supporter use or earlier action for the search that would actually create K1.

## K0/K1 physical distinction

The opponent's illustrative 60-card deck has 12 Basic Pokémon, four Judge, four Ace Trainer, four distinct X target cards and 36 filler. Its opening seven are conditioned on containing a Basic. Six Prizes are placed, then two deck draws and s original Prize awards enter the opponent's hand.

Let `x` denote the number of X cards currently held, and `z` the number **still** in the `6-s` face-down original Prizes.

In K0 the opponent only knows x. The posterior probability of z is an exact hypergeometric sample among the remaining `60-(9+s)` unseen physical cards:

```text
P(z | x, s) =
  C(4-x, z) × C(60-(9+s)-(4-x), (6-s)-z)
  / C(60-(9+s), 6-s).
```

In K1 it knows z from the prior search. After it discards the played non-X Supporter and shuffles its other held cards back into its deck, the physical deck contains `N=53+s` cards, of which exactly `4-z` are X. Hence

```text
P(X available after own redraw of n cards | K1 z)
  = 1 - C(53+s-(4-z), n) / C(53+s, n).
```

Here n is 4 for Judge and 6 for the Ace Trainer player. The K0 redraw probability is precisely the probability-weighted average of these K1 conditional values. This identity is verified for all x=0..4, s=0..2, redraws n=3,4,6.

The Beheeyem side remains the same exact B4/TAE4/Computer Search1/d1 model. Opponent response actions are pass/no reset, Judge when held and Ace Trainer when both held and legal by remaining-Prize comparison. The opponent's scalar utility is still `P(own X ready) - lambda × P(Beheeyem next packet | first packet)`, with optional public observation of the first Beheeyem tutor use.

## Measurable K1 advantage at an intermediate tradeoff

At **r=1 Beheeyem Prize earned, q=6 opposing Prizes remaining, lambda=10**, with the opponent observing Beheeyem's direct-versus-tutor-rescued first attack:

| Outcome | K0 decision | K1 decision |
| --- | ---: | ---: |
| Opponent X ready after response | **56.410922%** | 56.310040% |
| Beheeyem joint T2+T3 packet event | 1.144932% | **1.142429%** |
| Increase in weighted utility from K1 | baseline | **+0.000472574** |

Here, the free information changes a few responses toward stronger packet denial while surrendering about **0.101 percentage points** of own X readiness. That increases the designated scalar objective when the denial weight is 10. Because the Beheeyem packet values in the utility are **conditional on the first attack**, the joint event percentages displayed in the table require normalization by first-attack incidence before calculating the utility difference.

At r=2/q=6/lambda=10 with the tutor route public, K1 and K0 generate the same rounded result: 58.870599% own-X readiness and 1.552544% Beheeyem joint access; K1 still improves exact utility by a very small amount due to differences below six reported decimal places. At very high lambda (1,000,000), maximizing the isolated Beheeyem-denial term dominates, so K1 adds no value over the already optimal source-access response.

## Why the information helps

Suppose the opponent currently has no X in hand:

- If all four X copies are still Prized, a Judge/Ace hand reset **cannot** find X. It can nevertheless still be useful when its packet-denial effect itself outweighs other concerns.
- If zero X are Prized, six-card Ace Trainer redraw has substantially more chance of finding X. That can justify a Supporter play in a state where an average K0 estimate would not.

K1 reduces a mixture of possible X availability states into a known value. It can enable more precise decisions even though it does not directly move or recover a single Prized X. The gain may be small in average physical probability because extreme Prize layouts are uncommon.

## Validation and limits

- [K1 exact solver](../../tools/beheeyem_opponent_k1_target.py) enumerates opponent hand categories, X's own-Prize posterior, legal available Supporters and Beheeyem first-packet routes. It computes expected policy value with and without conditioning on z, and asserts K1 utility is never worse because the information is freely granted.
- [Exact regression](reproduce.py) checks posterior normalization, equality of K0 redraw to the K1-weighted average for all finite cases, and 60 controlled opponent Prize/denial-weight/visibility scenarios.
- [Physical Monte Carlo](monte_carlo.py) draws a genuinely Basic-valid opponent hand, original six Prizes and follow-up cards, reveals the count of still-Prized X, physically discards a non-X played-card proxy, reshuffles the deck, and checks whether X is redrawn. Three independent 150,000-trial samples validate the K1 probability formula.
- [GitHub Actions run 38133827205 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133827205).

These are model-based, exact conditional access metrics and sensitivity analyses. The opponent is assumed to have learned its Prize composition already, with no cost for searching; no real opponent board or hand refresh is modeled, and X is a hypothetical independently valued target. The opponent's K1 information is private to itself. Consequently this is a reference for belief-state game solvers, not a recommendation to add Judge/Ace or perform a deck search merely for this information benefit.

The next step is a genuine optional search action with a cost and information gain, then integration with the probability of actually needing X on the next turn.
