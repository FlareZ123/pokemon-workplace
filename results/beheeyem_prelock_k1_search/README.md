# Paid full-deck search must precede Beheeyem's Item-lock window to create K1

## Question

The [opponent K1 own-target research](../beheeyem_opponent_k1_target/) grants knowledge of X Prizes from a previous full-deck search and computes its value for selecting Judge, Ace Trainer or preserving the existing hand. That is a free-information upper bound. In a physical match, full-deck inspection requires an actual search action.

Beheeyem's Mysterious Noise attack prevents its opponent from playing Items from hand during its next turn. A deck-search **Item** first drawn on that locked reply cannot create K1 information at that time. The opposing player must either have inspected its deck earlier or use a permitted non-Item route, which may contend with its one Supporter action.

This exact source-access model quantifies one physically payable source, **Ultra Ball**, available *before* the Item lock. Ultra Ball is a legal paper Expanded Item requiring the player to discard two other cards before searching the deck for a Pokémon. Under the Advanced Player's Rulebook, a restricted-category deck search may choose no target, but still inspects the deck. A successful paid Ultra Ball therefore reveals the remaining deck composition, even if the player declines a search target; we assume it is played early for that knowledge and costs one Item and two disposable filler cards.

## Physical opponent deck and K1 event

The illustrative opposing deck has 12 Basics, four Ultra Ball (`U`), 32 disposable neutral filler (`F`), and 12 additional cards (four Judge, four Ace Trainer and four hypothetical own-X target cards).

Condition a random seven-card opening on containing a Basic, then set six original Prizes. Suppose the opponent can observe `k` additional deck draws before the Mysterious Noise Item-lock deadline and may have already taken `s` random original Prizes.

A **paid Ultra Ball K1 event** occurs exactly when its accessible hand contains at least one U and at least two disposable F before the deadline. In the simplified deck, choosing such two filler cards pays the actual discard requirement while retaining all potential Judge/Ace/X cards. This event is a **feasibility upper bound** on strategically sensible K1 acquisition; the study does not claim a player would burn Ultra Ball solely for information or model the tactical cost of its resulting hand depletion.

The physically observed `h=7+k+s` identities are distributed by conditional multivariate hypergeometric sampling, with the opener Basic validity factor

```text
P(valid seven-card Basic opener | h observed containing b Basics)
   = 1 - C(h-b,7)/C(h,7).
```

The enumerator sums over every possible category count, filters for U≥1 and F≥2 and returns an exact Fraction. It separately tracks U held but unpayable due to fewer than two designated filler.

## Opportunity lost if cards become available only during the lock

For zero prior Prize awards, the following comparison assumes no intervening spending: `k_pre` draws occur while Ultra Ball is still legally playable, followed by `k_locked` further draws after the lock begins. The second probability is a *counterfactual* in which the Item restriction did not apply.

| Pre-lock draws | Further locked-turn draws | Paid K1 feasible before lock | Feasible without Item lock | Extra attainable supply blocked |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 35.393362% | 35.393362% | 0 |
| 0 | 2 | 35.393362% | 46.477077% | **11.083715 pp** |
| 0 | 4 | 35.393362% | 55.052922% | **19.659560 pp** |
| 2 | 0 | 46.477077% | 46.477077% | 0 |
| 2 | 2 | 46.477077% | 55.052922% | **8.575845 pp** |
| 2 | 4 | 46.477077% | 62.252256% | **15.775179 pp** |
| 4 | 0 | 55.052922% | 55.052922% | 0 |
| 4 | 2 | 55.052922% | 62.252256% | **7.199334 pp** |
| 4 | 4 | 55.052922% | 68.483121% | **13.430199 pp** |

For two pre-lock draws and four subsequent locked-turn draws, the opponent has **46.477077%** probability of already having a payable Ultra Ball before the lock; in a counterfactual without the Item restriction, the same six total draws would reach **62.252256%**. The **15.775179-percentage-point** difference represents exactly the physical probability mass where two or more additional seen cards complete Ultra Ball plus two-filler payment only too late.

This is the probability of **having and being able to pay** a particular Item search, rather than the probability of strategically profiting from the deck inspection. It excludes any non-Item search through Abilities, attacks or Supporters that might still reveal the full deck during lock.

## Validation

- [Exact timing/payability engine](../../tools/beheeyem_prelock_k1_search.py) enumerates all Basic-valid hand category counts with real U/F physical multiplicities, fixed six Prizes and configurable before/after draw budgets. It checks total probability exactly equals one.
- [Independent staged exact enumeration](reproduce.py) enumerates the initial valid seven-card opener and subsequent card draws separately, rather than relying on the union-of-observed-cards formula, and proves equality for `k=0,2,4`. It checks 36 pre/locked-window combinations plus further earned-Prize scenarios.
- [Independent 60-card Monte Carlo](monte_carlo.py) physically deals a Basic-containing seven, six Prizes, randomly earned original Prizes, pre-lock and locked draws in four 200,000-trial settings. Observed feasibility probabilities match exact values to six standard errors.
- [GitHub Actions run 38134274680 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134274680).

## Strategic scope

Ultra Ball is treated as a **pure possible information source** with real two-card disposable payment but without a chosen Pokémon search output or later changes to the hand/deck/board. Choosing an actual Pokémon would produce additional material and strategic effects. Paying the filler discards would alter subsequent hand-reset deck density. Neither is propagated into the later Judge/Ace/X payoff engine, so multiplying these percentages by the previous free-K1 information advantage is generally unjustified because access and value are correlated.

An important methodological distinction remains: **known potential information**, **physically attainable information**, and **worth paying to acquire it** are separate quantities. This study supplies the second quantity under a realistic timing gate, enabling a future action-level K1 acquisition and opponent policy analysis with actual discard-and-search zone conservation.
