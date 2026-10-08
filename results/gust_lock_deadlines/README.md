# Competing gust expiration deadlines: Prize threshold versus lock onset

## Research question

[Mixed Boss and Counter Catcher timing](../mixed_gust_prize_minimax/)
establishes a conditional source-priority rule: if both gusts can target the
same Pokemon now, spending the Prize-threshold-gated Counter Catcher before
Boss's Orders preserves the unrestricted card for later. Does this continue
to hold when an independent **Supporter lock** can remove Boss's future
playability? What happens under an independent **Item lock**?

## Explicit conditional model

The source model is the existing six-Prize one-hit-KO minimax with adversarial
opponent promotion. The player begins with one Boss's Orders (Supporter) and
one Counter Catcher (Item). The latter requires more own Prizes remaining
than the opponent; all target restrictions are otherwise identical.

An *exogenous persistent* Supporter lock or Item lock takes effect at the
beginning of a chosen attacking turn, numbered one-based. Once active,
it prevents playing the corresponding card class on all later turns.
Each benchmark has one of the following regimes: no lock, Supporter lock
from turn 2 or turn 3, Item lock from turn 2 or turn 3, or both locks from
turn 2. The defender's Prize count remains fixed, isolating this scheduling
effect.

Crucially, this model does not claim that any particular Pokemon establishes
such a persistent lock while surviving all the modeled Knock Outs.
For Active-dependent locks, a KO or switch can deactivate the source. Real
lock reachability depends on board position, existing Pokemon and Tools,
Ability suppression, and opponent actions. These regimes are **conditional
permission schedules**, suitable for testing the scheduling policy itself.

## Exact 146-board census

Sum of optimal attack counts over the 146 initial board classes with the
one-Boss/one-Catcher inventory:

| Permission regime | Opponent 1 Prize | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| No future lock | 392 | 392 | 392 | 398 | 398 |
| Supporter lock begins on turn 2 | 398 | 398 | 480 | 516 | 516 |
| Item lock begins on turn 2 | 398 | 398 | 398 | 398 | 398 |
| Both locks begin on turn 2 | 516 | 516 | 516 | 516 | 516 |
| Supporter lock begins on turn 3 | 392 | 398 | 398 | 398 | 398 |
| Item lock begins on turn 3 | 392 | 392 | 392 | 398 | 398 |

These are sums of attack turns over structural states, not expected match
lengths or real deck win rates. All player hands and board endpoints are
otherwise fixed.

## Source-priority reversals

Suppose the attacker **must play a gust on turn one**, and both card classes
are currently legal. For each regime, count boards where forcing Counter
first yields a lower optimal attack count than forcing Boss first and vice
versa. Both branches still choose their most advantageous target and optimize
later play.

| Regime | Opponent Prizes | Counter-first strictly better | Boss-first strictly better |
| --- | --- | --- | --- |
| No future lock | 1, 2, 3, 4, 5 | 0, 0, 73, 94, 100 | 0, 0, 0, 0, 0 |
| Supporter lock from turn 2 | 1, 2, 3, 4, 5 | 0, 0, 0, 0, 0 | **100, 100, 36, 9, 0** |
| Item lock from turn 2 | Any 1..5 | **100 each** | 0 each |
| Both locks from turn 2 | Any 1..5 | 0 each | 0 each |
| Supporter lock from turn 3 | 1, 2, 3, 4, 5 | 0, 0, 73, 94, 100 | 0 each |
| Item lock from turn 3 | 1, 2, 3, 4, 5 | 0, 0, 73, 94, 100 | 0 each |

**Counter first is no longer universally preferred once Boss also has a
future expiration deadline.** The relevant ordering is controlled by both
card-specific playability windows.

## Symmetric two-attack witness

Opponent Active **1 Prize**, Bench **1, 3, 3 Prizes**. The opponent has
one Prize remaining, so Counter Catcher remains eligible after the first
three-Prize KO.

If a Supporter lock starts on the **second** attacking turn:

- Spend **Boss first**, KO a three-Prize Bench target, then spend
  **Counter Catcher** on the second turn to KO the other three-Prize target.
  Victory takes **2 attacks**.
- Spend **Counter first**, then Boss becomes unplayable on turn two. The
  defender promotes a one-Prize target, and the best continuation takes
  **4 attacks**.

If instead an Item lock begins on turn two, the outcome reverses:

- **Counter first** then Boss wins in **2 attacks**.
- **Boss first** then Counter becomes unplayable, requiring **4 attacks**.

If both locks start on turn two, the cards' first-turn gust effects are
identical and neither can be used later.

This is the same target board and Prize state; only the **future action
permissions** change. A scalar 'gust count = 2' fails to distinguish these
outcomes.

## Interpretation

A useful card valuation should distinguish the last opportunity to execute
each otherwise similar effect. Boss consumes a Supporter play, and Counter
consumes an Item play and requires an unfavorable Prize position. Item lock,
Supporter lock, and the Prize count jointly determine the action window.

The previous Counter-first theorem remains correct **under its stated
no-future-lock premise**. The new result is an explicit counterexample to
extending that theorem to other changing permission sources.

The model still permits the optimal choice to **avoid playing any gust
immediately**. The forced-first comparison evaluates source priority
conditional on choosing to gust; it is not a recommendation to burn either
card as early as possible.

## Code and validation

- `tools/gust_lock_deadlines.py`: full minimax with turn-indexed,
  class-specific lock onset.
- `results/gust_lock_deadlines/reproduce.py`: independent Boolean
  attack-deadline solver, recalculating whether victory is possible
  in a given number of attacks.
- Exactly **4,380 independent scenario checks** (146 board classes times
  five opposing Prize counts times six lock regimes).
- Regression verifies all attack sums, all 4,380 forced first-action
  comparisons, no-lock equivalence to the earlier mixed-gust model,
  and the symmetric two-attack reversal witness.

Next: use actual lock-source cards and typed board state to make the
exogenous lock schedule endogenous. Source persistence and Active position
are essential before interpreting the census as matchup-specific.
