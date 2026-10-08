# Optional overkill can turn a winning Prize race into a tie

## Question

Can choosing an optional attack damage increase make a position strictly worse
even when the unboosted attack already Knocks Out the target?

**Yes.** This is an exact, card-text-grounded counterexample using two legal
English paper-Expanded prints from the bundled `sv10` set.

Implementation and regression:
`results/optional_overkill_reflection/reproduce.py`.

## Card interaction

- Cetitan ex `sv10-65`, 300 HP, has **Crushing Press**, 140+:
  "You may discard a Stadium in play. If you do, this attack does
  140 more damage." When knocked out it awards two Prizes.
- Zamazenta `sv10-146`, 130 HP, has **Strong Bash**. For the opponent's
  next turn, damage done to Zamazenta by an attack generates an equal number
  of damage counters on the Attacking Pokémon, even if Zamazenta is Knocked
  Out. In this example, Zamazenta used Strong Bash last turn.

Take a specific board: Cetitan ex has 150 existing damage, and Zamazenta is
undamaged. Both are Active and Cetitan has sufficient Energy to use Crushing
Press. A removable Stadium is in play. Both players have one healthy Benched
Pokémon. Cetitan's player A has one Prize remaining, and Zamazenta's player
B has two Prizes remaining. No other damage modifiers or protections apply.

| Cetitan decision | Damage dealt | Reflection | Cetitan damage afterward | Knock Outs | Prize result |
| --- | ---: | ---: | ---: | --- | --- |
| Leave Stadium | 140 | 140 | 290/300 | Zamazenta only | A takes final Prize, wins |
| Discard Stadium | 280 | 280 | 430/300 | Both Actives | Both take final Prizes, tie |

Zamazenta takes only one Prize when Knocked Out, while Cetitan ex
awards two. The benchmark compares the same board with one optional choice.

The calculation is anchored in the rulebook's post-damage reaction phase,
followed by simultaneous Knock Out and Prize game-resolution checks.

## General threshold

If the lower damage `D` already defeats the defender, a bonus `B>0`
flips attacker survival only when its remaining HP `H` satisfies:

`D < H <= D + B`

The equality at the lower boundary is important: when `H == D`, even
the unboosted reflection Knocks Out the attacker.

For 300-HP Cetitan with a 140-damage base attack and optional +140, its
pre-attack damage may be 20, 30, ..., 150 for the unboosted attack
to survive while the boosted attack is Knocked Out, giving 14
ten-damage-counter-aligned states. The detailed regression verifies each.

## Strategic implication

Damage is a state-dependent, discontinuous resource when the defending
Pokémon mirrors final damage. A greedy policy that always selects the
maximum printed attack damage fails even in a board with both attackers
capable of taking the final Prize. An optimizer should compare available
effect branches against the resulting terminal outcomes.

## Boundaries

The provided initial damage, Strong Bash effect, enough Energy, removable
Stadium, target position, and Prize counts are explicit assumptions.
The stadium's own continuous effect or strategic denial value is excluded
from this isolated counterexample. The source loader checks that both
prints are effectively legal and that their set is marked Expanded legal
in the bundled English snapshot. This does not generalize to every region
or current official tournament metagame without additional legality review.
