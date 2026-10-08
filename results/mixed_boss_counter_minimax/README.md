# Mixed Boss's Orders and Counter Catcher: preserve the source whose legal window lasts longer

## Question

One unconditional Boss's Orders and one Counter Catcher can both target any opposing Benched Pokémon while the player is behind on remaining Prizes. Once that same player takes Prizes, Counter Catcher's play requirement can disappear. Does the *order in which equivalent gust sources are spent* change the shortest guaranteed Prize route?

## Model

`tools/mixed_boss_counter_minimax.py` extends the earlier exact one-hit, six-Prize, adversarial-promotion solver. Its state includes the opposing Active and Bench Prize values, the attacking player's remaining Prizes, the defending player's fixed remaining Prize count, and separate budgets for Boss and Counter Catcher gust actions.

Boss can target any opposing Benched Pokémon at any Prize count. Counter Catcher is available only while the attacking player's remaining Prizes **exceed** the opponent's. A chosen target is KO'd in one attack and awards one, two or three Prizes. The defender selects the replacement Active maximizing future attacks.

The model assumes each physical gust card is already in hand and playable aside from Counter Catcher's remaining-Prize gate. Actual Supporter timing, Item lock, hand acquisition, Energy, defender turns, and target HP are excluded. Using multiple gusts to reposition an opponent repeatedly before a single attack is dominated under this **specific** terminal objective, since only the final selected target affects the modeled state. This need not hold with real switching triggers or additional target effects.

## Complete six-Prize census

As in the earlier toy research, enumerate all 146 distinct two-to-six-target board classes with Prize values 1/2/3, at least six total available Prizes and each distinct starting Active class. Hold the defender's Prize count fixed at one through five. Compare two Boss resources, one Boss plus one Counter, and two Counter resources.

| Opponent Prizes remaining | Mixed Boss + Counter vs two Boss: equal | Mixed needs +1 attack |
| ---: | ---: | ---: |
| 1 | 146 | 0 |
| 2 | 146 | 0 |
| 3 | 146 | 0 |
| 4 | 140 | 6 |
| 5 | 140 | 6 |

**With the opponent at three or fewer remaining Prizes, one available Boss plus one Counter yields the same minimax attack count as two Boss gusts in every tested abstract board.** This result holds because the Counter can usually be spent before its conditional window closes, preserving the Boss for any later target.

The gap between two Counters and the mixed pair shows why retaining the broad option matters:

| Opponent Prizes remaining | Two Counter equal mixed pair | Two Counter needs +1 attack | Two Counter needs +2 attacks |
| ---: | ---: | ---: | ---: |
| 1 | 146 | 0 | 0 |
| 2 | 140 | 6 | 0 |
| 3 | 70 | 64 | 12 |
| 4 | 52 | 70 | 24 |
| 5 | 52 | 70 | 24 |

All values are structural counts under these defined 146 boards. They are not card-count recommendations for tournament lists.

## Dominance of the restricted source on an overlapping target

When both the Boss and Counter actions are legal and would bring the **same opposing Benched target** Active, spending Counter for that target and retaining Boss weakly dominates spending Boss and retaining Counter. Both choices produce the identical immediate opposing board and Prize reward; the unused Boss remains playable after any Prize shift, whereas the unused Counter may become ineligible.

Each pair of first-turn source/target choices is checked across all 146 boards (292 distinct Benched Prize-value target comparisons per fixed opposing Prize count):

| Opponent Prizes remaining | Strictly worse to spend Boss first | Equal outcome |
| ---: | ---: | ---: |
| 1 | 0 | 292 |
| 2 | 0 | 292 |
| 3 | 82 | 210 |
| 4 | 130 | 162 |
| 5 | 162 | 130 |

The difference grows as the opponent's remaining Prize count rises because Counter's future eligibility becomes more fragile. The proof is conditional on the costless Item action and the lack of other Supporter needs; in real Expanded a Boss might consume the Supporter turn while Counter could coexist with a different Supporter, further favoring the Item under some circumstances.

## Concrete two-attack witness

The opponent has **three Prizes remaining**, Active worth **one Prize**, Bench worth **one, three and three Prizes**. The player has six Prizes remaining and holds one Boss and one Counter.

Using Counter Catcher to gust a three-Prize target for the first Knock Out leaves the player with three Prizes and the opponent with three. Counter Catcher would now be illegal, but Boss remains available; the player uses Boss to KO the other three-Prize target and wins on attack two.

Using Boss on the same first three-Prize target leaves only Counter. The two players are tied on three Prizes and Counter cannot be used, so the defending player can force **four attacks**. The first-target choice was identical; the resource chosen for that action caused the difference.

A different six-board failure family appears if the opponent has four or five Prizes. Example: Active two-Prize, Bench one/two/two. Two Boss gusts win in three attacks, but the mixed Boss+Counter pair takes four; the initial natural two-Prize KO may close Counter's window before both later gusts can be used.

## Verification

`results/mixed_boss_counter_minimax/reproduce.py` independently enumerates guaranteed-win feasibility at fixed attack deadlines. It checks **6,570** board, fixed opposing Prize count, and separate Boss/Counter-budget scenarios, plus reduction to both existing pure-gust models. It asserts the mixed versus pure histograms, the 292 same-target source comparisons for each opposing Prize count, and both concrete witnesses.

Run: `python results/mixed_boss_counter_minimax/reproduce.py`.

## Interpretation

This adds a **source dominance** rule to the associativity and AMR framework: when multiple cards can pay for the same tactical transition, spend the source whose legal future options are narrower, provided no other resource cost or coeffect reverses the comparison. Counter Catcher often has a shorter eligibility horizon than Boss, making it rational to use Counter first when both are presently legal. This conclusion cannot be reduced to whether a connector merely makes the target card reachable.
