# Gust timing, opponent promotion, and Prize-race complementarity

## Question and model

What is the guaranteed number of attack turns to win a six-Prize endgame when the defender chooses its next Active after every Knock Out, and the attacker may spend a limited number of Boss's Orders-like gust actions?

The model contains one opponent Active and up to five opposing Benched Pokemon, each worth 1, 2, or 3 Prize cards. Each Pokemon can be Knocked Out in a single attack. One gust may switch a Benched Pokemon into the Active Spot on the attacker's turn; the former Active returns to the Bench. After each KO, the defending player adversarially chooses any survivor to promote. The attacker wins with six Prizes or by KOing the last opponent Pokemon. Pokemon cannot enter play and there are no other Supporters, retreats, opponent attacks, damage carryover, locks, or draw/search requirements. Gust tokens must be spent on distinct attack turns.

This is a deliberately bounded **perfect-information combat abstraction**, not a full-match win-rate or metagame estimate.

Rules grounding: the advanced manual at `resources/manual/EN_advanced_manual-2025-transcription-structured.md` (A-01: an attack ends the turn; B-03: one Supporter per turn; C-05: targeted switch; D and E: KO and victory). The repository card pool lists Boss's Orders as a Supporter that selects a Benched Pokemon to move Active.

## Method

`tools/gust_prize_minimax.py` implements an exact finite deterministic minimax.

State: `(active_value, bench_multiset, gusts_remaining, prizes_needed)`.

At each turn the attacker selects a target: current Active without a gust, or a Benched Pokemon with one gust. If that KO reaches the six-Prize threshold or clears the board, the cost is one attack. Otherwise the defender chooses a survivor to promote to maximize future attacks, and the attacker selects the action minimizing that worst case. Every branch removes one Pokemon so recursion terminates. The comparator `must_gust_now` forces a gust on the first turn, then restores optimal future decisions.

For complete enumeration, construct every multiset of two to six Pokemon with Prize values in {1,2,3}, total reward at least six, and every distinct starting Active value: **146 board classes**. This is an unweighted combinatorial census.

## Exhaustive results

| Attacks saved against a no-gust policy | One gust available | Two gusts available |
| --- | ---: | ---: |
| 0 | 77 | 38 |
| 1 | 54 | 70 |
| 2 | 15 | 35 |
| 3 | 0 | 3 |
| **Total** | **146** | **146** |

**41 classes** have a strictly larger marginal improvement from the second gust than from the first; attack-count benefit is not invariably diminishing-return. **55 classes** are worse if the player is forced to spend its available gust immediately: 41 lose one attack turn and 14 lose two.

These counts describe toy-board geometries, not observed competitive prevalence.

## Witness 1: two gusts combine to eliminate two attacks

Opponent Active: **1 Prize**. Bench: **1, 3, 3 Prizes**.

| Gusts | Minimax attacks required |
| ---: | ---: |
| 0 | 4 |
| 1 | 4 |
| 2 | 2 |

With one gust the opponent can still control promotion of the remaining one-Prize Pokemon, denying timely access to both three-Prize targets. Two gusts permit immediate three-Prize KOs on consecutive turns and win in two attacks. A single gust is worthless against this worst-case promotion policy while the pair is decisive.

## Witness 2: the option to delay a gust saves an attack

Opponent Active: **3 Prizes**. Bench: **1, 3 Prizes**. With one gust, the flexible optimum is **2 attacks**: KO the Active three-Prize Pokemon first, then gust the other three-Prize Pokemon. Forcing a first-turn gust gives the defender a one-Prize promotion option and requires **3 attacks** in the worst case.

A reachable gust action can therefore be better preserved for a later attack turn.

## Validation

`results/gust_prize_minimax/reproduce.py` runs an independent Boolean game-tree oracle with a fixed attack-turn deadline. It checks the minimax answer against the smallest winning deadline in all **438** board/gust-budget states (146 boards times budgets zero, one, and two), then asserts the two histograms, 41 complementarity cases, 55 eager-use regrets, the explicit witnesses, and monotonicity.

Reproduce with `python results/gust_prize_minimax/reproduce.py` from the repository root.

## Interpretation and limitations

Immediate search access is insufficient as a value metric for discrete tactics such as gust. A second copy of a tactically similar effect can increase the quality of *sequences* rather than only raise the chance of having the first copy. Preservation of an unused Supporter effect has option value.

No real-deck copy-count recommendation follows from these stylized numbers. They assume one-hit knockouts on any target, a static opponent board, known Prize values and freely available attacks. A next model should couple this minimax payoff to a card-access and Supporter-quota transition model, attacker survivability, alternate Supporter actions, Bench replenishment, and accumulated damage.
