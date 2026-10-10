# Two-sided finite-deck Boss versus Switch access

## Question

A defender's possible escape can change Boss's Orders value, but real escape resources must first be drawn and played on the opponent's turn. This study extends [stochastic_escape_gust](../stochastic_escape_gust/) with **two independent finite draw piles**, attacker Boss and defender Switch, and maximizes the opponent's replies after seeing the defender's own draw.

## Mechanical and modeling scope

The attacker draws once at the start of each own turn, can use at most one Boss's Orders from hand to choose a Benched opposing Pokémon, and performs one attack worth one remaining durability hit. The defender promotes any survivor immediately after a Knock Out, then draws one from its own remaining deck on the intervening turn. It can play an available Switch Item to exchange Active and Bench after seeing that draw, without retreat-payment requirements. Both players retain unplayed Trainer cards in hand. All choices maximize or minimize *expected attacks until the attacker wins six Prizes*.

The [exact Fraction recurrence](../../tools/two_sided_stochastic_escape.py) treats identical remaining cards exchangeably and respects distinct event order: KO promotion precedes the defender's draw, followed by any optional Switch, followed by the attacker's next draw. Source checks in [reproduce.py](reproduce.py) verify `swsh2-154` Boss's Orders (Supporter) and `sv1-194` Switch (Item) against the bundled English BW-onward card pool. A uniform `item_legal=False` state suppresses Switch, representing a persistent Item lock.

The model remains deliberately narrow: the defender cannot retreat normally, attack, play a draw/search Trainer, gust the attacker, or change the Bench; no Prize-card draw, manual Energy payment, special attacking action, deck-out race, Supporter alternative, Item search, or transient lock timing is modeled. The defender's Switch is assumed usable if drawn and permitted.

## Exact theorem for one hidden Switch

Consider three identical opposing Pokémon each worth **three Prizes** and requiring **two hits**, one Active and two Benched. The attacker needs six Prizes. Boss copies are uniformly shuffled into a draw pile of length `A >= 6`; the defender has **one Switch** uniformly shuffled in a separate draw pile of length `D >= 5`, with all other cards inert. Neither player holds a Trainer initially. Let `G` be the number of Boss copies.

The exact expected attack count is

`E(A,D,G) = 4 + (3/D) * C(A-4,G)/C(A,G)`

where the fraction is zero if `G > A-4`. The defender must see Switch within its **first three draws** to create an extra attack. Independently, the attacker must miss every Boss among its **first four draws** for that extra attack to survive. If either condition fails, four attacks suffice. The two events concern separate physical decks and their probabilities multiply.

This has been verified against the exact chance/minimax solver in all **450** configurations with `A=6..14`, `D=5..14`, and `G=0..4`.

For `A=D=12`:

| Boss in attacker deck | Switch in defender deck | Expected attacks |
| ---: | ---: | ---: |
| 0 | 0 | 4 |
| 0 | 1 | 17/4 = 4.25 |
| 1 | 1 | 25/6 = 4.166667 |
| 2 | 1 | 271/66 = 4.106061 |

In particular, two unseen Boss copies are worth `17/4 - 271/66 = 19/132` fewer expected attacks with one hidden defender Switch. An *immediately usable* free escape had given Boss two copies a larger `19/33` attack-count benefit in the predecessor model, so free escape tokens overstate the threat from a defender Switch that may arrive too late.

## Independent exhaustive physical oracle

When each deck has 12 cards, with two Boss copies and one Switch respectively, the independent fully ordered-deck oracle enumerates `C(12,2)*12=792` joint physical placements. It finds **708 worlds requiring four attacks** and **84 worlds requiring five**, giving

`(708*4 + 84*5)/792 = 271/66`.

The 84 adverse worlds are exactly the `C(8,2)*3 = 28*3` pairs where no Boss appears among attacker draws one through four and Switch appears among defender draws one through three. The full-information physical oracle happens to agree for this symmetric fixture; no equivalence is asserted for other states.

When `item_legal=False`, all tested `G=0..2`, `Switch=0..2` configurations return four expected attacks. The no-Item result represents the combined effect of Item permission and access, not a claim about specific lock matchups.

## Reproduction

- [Source implementation](../../tools/two_sided_stochastic_escape.py)
- [Independent physical-deck oracle and 450-case regression](reproduce.py)
- [Validation workflow](../../.github/workflows/validate-two-sided-stochastic-escape.yml)
- [Previous deterministic escape bridge](../stochastic_escape_gust/)

Run `python results/two_sided_stochastic_escape/reproduce.py`. These are exact conditional results under a constructed small endgame, not tournament frequencies or evidence for a particular decklist.

## Next work

Model a realistic defender hand, Item lock that can begin or end between turns, normal Retreat Energy choices, and attacker Supporter contention. The present paired-deck probability law isolates one reason a theoretical escape option may fail to matter: the opponent never draws the Switch in the tactical window.
