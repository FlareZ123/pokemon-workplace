# Arven can prefetch Pokémon Communication before a Gladion rescue

## Research question

Does the ability to search for Pokémon Communication with Arven
(`sv1-166`) meaningfully help the turn-two Grand Tree (`sv7-136`)
Prize-repair line? What happens if Arven and Gladion both compete for
the player's one normal Supporter allowance?

## The distinct-turn route

Arven is a Supporter that searches for one Item and one Pokémon Tool,
then shuffles the deck. The rulebook allows finding no Tool in this
type-restricted search. Arven can select Pokémon Communication
(`sm9-152`) as its Item.

Suppose a player's starting hand contains Arven, Gladion, Grand Tree,
and a Gothita Basic, but not Pokémon Communication. It is still in
the deck, and the Gothorita that Grand Tree needs is Prized.

**Going second:** turn 1 may use Arven to search Pokémon Communication.
Turn 2 may use Gladion to recover Gothorita from Prizes, then use the
previously fetched Communication to return Gothorita from hand to
deck. Grand Tree can evolve the preexisting Gothita through that
Gothorita into Gothitelle if the Stage 2 remains in deck.

**Going first:** the first player's first turn forbids playing a
Supporter. If Arven is the only way to access Communication and
Gladion is the only way to rescue the Prize card, there is no
same-turn Supporter route to do both by turn 2. Arven can first be
played on turn 2, while Gladion must occupy a later turn. Under
the specified actions the earliest completion shifts to turn 3.

This is a conditional route, not a claim that going first cannot
ever execute the same recovery on turn 2. Drawing Communication
naturally or accessing it through a different Item or Ability can
remove the need for Arven.

Official source for the first-player first-turn Supporter restriction:
https://www.pokemon-card.com/howtoplay/

## Exact second-player card-access certificate

Use an illustrative 60-card deck with four Gothita Basic, one
Gothorita, one Gothitelle, one Grand Tree, one Pokémon Communication,
G Gladion, A Arven, and `52-G-A` non-Basic filler cards.

A seven-card opening is accepted only if it has at least one Basic
Gothita. For the certificate, the accepted hand must also hold
Grand Tree, at least one Gladion and at least one Arven, while none
of the singleton Gothorita, Gothitelle and Communication are in hand.

Among the remaining 53 cards, the six Prizes contain Gothorita but
neither Gothitelle nor Communication.

On the first natural draw the player avoids Gothitelle and
Communication, ensuring Arven can still search Communication from
deck. Arven then removes Communication to hand and shuffles deck.
The second natural draw avoids Gothitelle, leaving it searchable
by Grand Tree on turn 2.

The total exact conditional probability is:

`P(E|accepted Basic opening) = (H/D) *
[C(50,5)/C(53,6)] * (45/47) * (44/45)`

where

`D=C(60,7)-C(56,7)`

and

`H=sum_b=1..4 sum_g=1..G sum_a=1..A
C(4,b) C(G,g) C(A,a) C(52-G-A,7-1-b-g-a)`.

The probability is exact for this physical sampling model.

| Gladion copies | Arven copies | Second-player turn-two certificate |
|---:|---:|---:|
| 1 | 1 | 0.004813% |
| 2 | 2 | 0.018143% |
| 3 | 3 | 0.038441% |
| 4 | 4 | **0.064306%** |

The event is rare because of simultaneous opening-card and
Prize-zone requirements. It does not include other search connectors,
naturally found Communication, other evolution copy counts,
Ability lock, opponent threats, or failure to maintain the Basic
in play until turn 2.

The result complements the prior exact opening model that required
Pokémon Communication itself in the opening hand. Since the
populations and event definitions differ, their percentages must
not be summed as disjoint events without an explicit joint model.

## Rule and source validation

* Bundled Arven card `sv1-166`: Expanded-legal Supporter with Item
  and Pokémon Tool deck search.
* Bundled Pokémon Communication `sm9-152`: Expanded-legal Item with
  Pokémon hand-to-deck return.
* Official Japanese current basic rules confirm that the
  player going first may not use a Supporter on their first turn.
* Bundled Advanced Rulebook I-B-03 and I-H establish once-per-turn
  Supporter use and optional choices in category-restricted deck
  searches.
* Grand Tree requires the Stage 1 and Stage 2 to be searched from deck,
  and the basic target must have been in play since a previous turn.

## Reproduction

`python results/grand_tree_arven_prefetch/reproduce.py`

Implementation: `tools/grand_tree_arven_prefetch.py`.

The reproducer checks actual local Expanded legality and card text,
matches eight exactly enumerated small physical hand/Prize/turn-draw
universes against the factored probability, and verifies the separate
Supporter quotas across turns.

## Interpretation

This is a timing and resource-contention witness, not a complete
competitive deck recommendation.

Arven used on turn 2 consumes the same Supporter allowance that
Gladion needs to recover the Prize card. Fetching the correct Item
too late therefore can have zero immediate value for this line,
despite Arven theoretically connecting to that Item.

Playing Arven on turn 1 going second shifts its resource cost into
a different turn and opens the Gladion+Communication combination
on turn 2. Grand Tree itself requires no once-per-turn
same-physical-Stadium reentry claim for this single Stage2 evolution.

Related results:
[opening Gladion+Communication access](../grand_tree_opening_rescue_access/),
[physical Prize-to-deck repair](../grand_tree_prize_rescue_bridge/),
[Supporter action budget](../turn_action_budget/).
