# Opponent Prize-taking can reopen Counter Catcher, but source priority survives

## Question and relationship to earlier work

The earlier [mixed-gust study](../mixed_gust_prize_minimax/) held the opponent's Prize count fixed. Both players take Prizes in a real game, so Counter Catcher can become legal again after the opponent scores. We extend the same bounded minimax to controlled opponent Prize-taking trajectories and ask whether the conditional Counter-first exchange argument still holds.

## Rules and bounded model

Boss's Orders is a Supporter that gusts any opposing Benched Pokemon. Counter Catcher is an Item that does the same while our number of remaining Prize cards exceeds the opponent's. The bundled Advanced Player's Rulebook governs one Supporter per turn, Knock Out resolution, taking Prizes, and victory when a player has taken the last Prize.

The attacking player begins with six Prize cards remaining and one of three fully available gust inventories: two Catchers (2C), one Boss plus one Catcher (B+C), or two Bosses (2B). The opponent has 1..6 Prizes remaining and a board of 2..6 Pokemon whose total Prize rewards sum to at least six. Each Pokemon is an immediate one-attack Knock Out worth 1, 2, or 3 Prizes. As in the original baseline, there are 146 unordered board classes distinguished by the Active's Prize value.

An attacker may choose one meaningful targeted gust per attacking turn, or attack the natural Active. After each Knock Out, the defender adversarially chooses the new Active. The attacker wins by taking six Prizes or eliminating the final opposing Pokemon.

If the attacker has not won, an **exogenous opponent score clock** reduces the opponent's remaining Prizes on the reply turn. If the opponent reaches zero, the attacker loses before attacking again. Clocks repeat their tuple indefinitely. Tested clocks are (0), (1), (2), (0,1), (1,0), (0,2), (2,0), (1,2), and (2,1).

The clocks are conditional thought experiments, not claims that an opponent can guarantee a specified Knock Out. There is no explicit attacker-side board, Energy, opponent attack, draw, Item lock, Supporter contention, new Bench occupant, or nonuniform target HP. These results are exact for their stipulated trajectories and are **not** empirical matchup win rates. A lost race is represented by infinite attacks.

## Exact census

Each triple is ordered (2C, B+C, 2B). Counts of winnable board classes have denominator 146. Attack totals sum only the separately winnable classes for that inventory, so totals with different denominators are not directly comparable as mean performance.

| Opponent Prizes | Opponent takes per reply | Winnable classes (2C / B+C / 2B) | Total attacks on each inventory's winnable classes |
| ---: | ---: | ---: | ---: |
| 3 | 0 | 146 / 146 / 146 | 480 / 392 / 392 |
| 4 | 0 | 146 / 146 / 146 | 516 / 398 / 392 |
| 5 | 0 | 146 / 146 / 146 | 516 / 398 / 392 |
| 6 | 0 | 146 / 146 / 146 | 541 / 457 / 392 |
| 3 | 1 | 123 / 123 / 123 | 294 / 294 / 294 |
| 4 | 1 | 141 / 141 / 141 | 454 / 366 / 366 |
| 5 | 1 | 145 / 145 / 145 | 510 / 392 / 386 |
| 6 | 1 | 146 / 146 / 146 | 541 / 457 / 392 |
| 3 | 2 | 75 / 75 / 75 | 150 / 150 / 150 |
| 4 | 2 | 75 / 75 / 75 | 150 / 150 / 150 |
| 5 | 2 | 123 / 123 / 123 | 364 / 294 / 294 |
| 6 | 2 | 85 / 117 / 123 | 250 / 316 / 294 |

At six opposing Prizes and a reply clock of two, a mixed pair turns **32** previously unwinnable boards into forced wins compared with two Catchers, and two Bosses rescue another **6** compared with the mixed pair. These structural numbers cannot be weighted as competitive win rates without a real distribution of boards and opponent turns.

## Reopening witness

Opponent Active is worth 2 Prizes, and the Bench has rewards (1,2,2); opponent has four Prize cards remaining. With the old fixed-opponent model, the mixed pair takes four attacks, while two Bosses take three. If the opponent takes one Prize on each reply, B+C instead wins in three:

1. Knock out the natural 2-Prize Active. Our remaining Prizes fall from 6 to 4. The opponent's reply lowers theirs from 4 to 3.
2. Counter Catcher can now be played at 4 versus 3. Gust and KO a 2-Prize target. Our remaining Prizes fall to 2; the opponent's reply lowers theirs to 2.
3. Saved Boss gusts the last 2-Prize target even at the 2-versus-2 tie. The attacker takes its final Prizes.

Two Catchers still need four attacks on this trajectory. The reopening is real within the controlled model: the opponent's own Prize progress restores a previously closed permission.

For a two-Prize-per-reply clock with six opposing Prizes initially, Active 3 / Bench (1,1,2) is unwinnable with 2C and winnable in three attacks with B+C or 2B. Active 2 / Bench (1,2,2) is unwinnable with 2C or B+C; 2B wins in three attacks.

## Conditional source-priority theorem

**If both Boss and Counter Catcher are legal now, both gust the same eligible targets, and the attacker has already committed to using a gust now, spending Counter first weakly dominates spending Boss first even under an arbitrary future opponent Prize-taking policy.**

Proof: Take any contingent policy that uses Boss now. Substitute Counter for that first gust, choosing the same target. It is legal by the current-state premise. The modified policy retains Boss. Whenever the original policy later plays the held Counter, use the retained Boss on the same target. Boss remains eligible wherever Counter would have been; if the original never plays Counter, the substitution retains an unused stronger option. Provided the two cards have no other state effects, the same opponent state, promotions, and Prize outcomes remain reachable. Thus every outcome achievable by Boss-first is achievable by Counter-first, regardless of how the opponent's Prize count changes.

This is a statement about **source choice given an immediate gust**, not a recommendation to gust immediately. It requires source neutrality beyond target access; Item lock, Supporter lock, same-turn Supporter contention, other play effects, or different targets can reverse the scheduling result. The [lock-deadline study](../gust_lock_deadlines/) supplies concrete counterexamples under different source permissions. The fixed-score monotonicity previously used to motivate the exchange is therefore sufficient but **unnecessary** for the theorem.

## Validation and reproduction

The implementation is [tools/opponent_prize_race_gust.py](../../tools/opponent_prize_race_gust.py). The [independent oracle](reproduce.py) checks whether a player can force victory by each proposed attack deadline, using existential attacker actions and universal defender promotions, and compares it with the minimizing solver.

The verified study covers **23,652** initial scenarios: nine score clocks x six opposing Prize counts x 146 boards x three inventories. It additionally checks **6,570** forced Boss-first versus Counter-first cases when both are initially legal. All satisfy Counter-first <= Boss-first. The constant-zero clock exactly reproduces the 2026-10-08 fixed-opponent benchmark, including its source-priority census. Specific reopening and race-loss witnesses are regression-tested.

Run the existing repository-root command: python -m results.opponent_prize_race_gust.reproduce. The corresponding GitHub Actions workflow provides a second clean-environment check.

## Limitations and next direction

A stronger model should make opponent Prize taking depend on an actual opposing board, attack costs and readiness, and our own vulnerable Pokemon. It should represent chance of obtaining and surviving to use each gust, conditional Item/Supporter locks and alternative Supporter lines. The exact exchange proof remains useful as a restricted semantics oracle for that larger model.
