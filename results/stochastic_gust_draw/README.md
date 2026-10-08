# Gust is valuable only when the tactical opportunity meets the draw deadline

## Question

The prior result `results/gust_prize_minimax/` identifies a board on which one ready gust saves zero attacks, whereas two ready gusts save two. How does this change when the gust cards are still in the deck and arrive through ordinary draws?

## Sequential decision model

`tools/stochastic_gust_draw.py` extends the prior one-hit-KO, six-Prize, adversarial-promotion model with a finite deck containing `gust_in_deck` Boss's Orders-like cards and `filler_in_deck` strategically inert cards. A player's hand can already contain `gust_in_hand` gusts.

Every attack turn begins with exactly one draw without replacement. The attacker sees that draw, chooses whether to use one available gust, and attacks once. The defender chooses the next Active from surviving Pokemon, maximizing the **expected** future attack count, before the next random draw. The same terminal rules apply: six Prizes or no defending Pokemon remain. Rational arithmetic uses Python `fractions.Fraction`.

There is no opponent board replenishment, actual opponent attack, Prize-card draw benefit, non-gust Supporter contention, or hand-size/search engine. The deck always contains enough cards to supply a turn-start draw through the longest possible board-clear sequence. This is a narrow conditional study of temporal gust acquisition, not a full-game probabilistic simulator.

## Exact witness: Active value 1, Bench values 1,3,3

The board's deterministic attack-count values with 0, 1, and 2 usable gusts are 4, 4, and 2. Suppose two gust cards are in an `N`-card draw pile and no gust is in the initial hand.

All `C(N,2)` pairs of gust positions in the deck are equally likely.

- Gusts at draw positions `{1,2}`: the player can take six Prizes in **2** attacks, saving two.
- Gusts at draw positions `{1,3}` or `{2,3}`: the player can win in **3** attacks, saving one.
- All other position pairs: defender promotion preserves the **4**-attack worst case.

Consequently, the expected attack count is exactly:

`E[T | 0 in hand, 2 in deck] = 4 - 4 / C(N,2)`.

A single gust in the deck is still worth zero in this position against worst-case promotions, since one gust never reaches both high-value targets in time.

Now suppose the player already holds one gust and the other is uniformly located within an `N`-card draw pile. Drawing the second at position 1 or 2 saves two attack turns; drawing it at position 3 saves one. Thus:

`E[T | 1 in hand, 1 in deck] = 4 - 5/N`.

| Remaining draw pile | Both gusts in deck | One held, one in deck | One gust in deck |
| ---: | ---: | ---: | ---: |
| 6 cards | 56/15 = 3.733333 | 19/6 = 3.166667 | 4 |
| 10 cards | 176/45 = 3.911111 | 7/2 = 3.500000 | 4 |
| 40 cards | 779/195 = 3.994872 | 31/8 = 3.875000 | 4 |

The same exact pair of tactical gust effects can have a large guaranteed benefit when available and a small expected benefit when its second copy is unlikely to be drawn before the tactical window closes. The distinction is especially sharp for a zero-copy starting hand.

## Validation

`results/stochastic_gust_draw/reproduce.py` checks the analytic draw-position formulas for draw-pile sizes 6, 10, and 40 and tests the special case where all future draws are filler cards. In that deterministic limit, the stochastic solver must recover `minimum_attacks` from `tools/gust_prize_minimax.py`, and it does for all 146 board classes and gust budgets zero, one, and two: **438 cross-kernel comparisons**.

The solver uses exact fractions throughout, so no Monte Carlo sampling or numerical tolerance is involved.

Reproduce from repository root with `python results/stochastic_gust_draw/reproduce.py`.

## Strategic implication

A tactical card's game-winning potential and its probability of arriving in the relevant attack window are separate dimensions. A linear access metric will overstate a two-gust endgame when it scores copies independently, because their value can be conjunctive. A static possession-only minimax model will overstate the benefit of gusts still hidden far down the deck. Both must be connected by an execution-time state model.

The next extension should permit more realistic draw actions, such as Supporter-based draw versus Boss contention, search cards, Prize taking into hand, and evolving or recovering attackers. Any such model must maintain observer-relative hidden information and opponent policy restrictions rather than assuming future draw identities are already known.
