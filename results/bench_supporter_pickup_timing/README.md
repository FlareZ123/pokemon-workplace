# Penny pickup: a first-turn Supporter legality discontinuity

## Question

What happens if guaranteed Pokémon pickup cards are **Supporters** rather
than Items? With a single Basic support needing a from-hand Bench entry,
Penny `sv1-183` can recover a Basic from either the Active Spot or Bench.
However, the player who goes first cannot play an ordinary Supporter
on their first turn.

This is a first-turn, narrow access comparison with a fixed four-slot
pickup package. It demonstrates that card-type timing can change the
realistic availability of otherwise similar pickup effects.

- Exact reproducible enumeration:
  [reproduce.py](reproduce.py)
- Shared paid search and pickup kernel:
  [bench_trigger_paid_replay.py](../../tools/bench_trigger_paid_replay.py)

## Source grounding

The bundled card database gives Penny (`sv1-183`) this effect:

> Put 1 of your Basic Pokémon and all attached cards into your hand.

Super Scoop Up `bw1-103` is an Item that flips a coin to return one of
your Pokémon and its attached cards to hand. The underlying source
comparison is official Pokémon first-turn rule guidance:
[Pokémon's Sword & Shield-era retrospective]
(https://www.pokemon.com/uk/news/pokemon-tcg-retrospective-the-sword-shield-era).
That rule change prevents the player going first from playing a
Supporter on their first turn. General Supporter play also has the
one-per-turn limit.

Penny is modeled as one deterministic pickup **when Supporter use is
legal**. In the one-support objective, only one successful pickup is
needed, so multiple Penny copies in hand can be modeled as multiple
accessible guaranteed pickups without gaining the ability to play a
second Supporter. Surplus Penny copies can instead be discarded to pay
Quick Ball.

For the first player's initial turn, all Penny copies in hand are
treated as available **Quick Ball discard stock** but unusable as
pickup effects. On the second player's initial turn, one Penny may be
used for the support rescue or pickup-replay route if the Supporter
action is still available.

## Exact controlled comparison

All 60-card configurations contain one singleton target Basic A,
three other ordinary Basics, four Quick Ball copies, four Nest Ball
copies, six Prizes, and one additional random card following the
opening. A separate four-card pickup package contains `p` Penny and
`4-p` Super Scoop Up copies. The rest of the deck is inert filler.

All percentages are conditional on an accepted ordinary-Basic
opening. A pending coin pickup flips independently with probability
one-half for heads.

| Penny | Super Scoop Up | Going first, Penny unavailable | Going second, Penny available | Gap |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 4 | 34.410901% | 34.410901% | 0.000000 pp |
| 1 | 3 | 33.107822% | 35.787079% | +2.679257 pp |
| 2 | 2 | 31.710865% | 37.069379% | +5.358514 pp |
| 3 | 1 | 30.217157% | 38.261846% | +8.044689 pp |
| 4 | 0 | 28.623695% | 39.368396% | +10.744701 pp |

The first-player access rate **decreases** when coin pickup Items are
replaced with Pennys, because Penny cannot be played on that turn and
only adds Quick Ball payment options.

The second-player rate **increases**, because the same Penny can be
played for a guaranteed return of the Basic. Its access-only value
in this model is identical to a guaranteed Item pickup when no other
Supporter action is needed that turn.

A one-Penny, three-Super-Scoop-Up going-second package has the same
immediate pickup-access rate as the
[one-Scoop-Up-Cyclone, three-Super-Scoop-Up package]
(../bench_pickup_package_frontier/). That numerical equality makes the
excluded costs especially important: Penny uses the turn's Supporter;
Scoop Up Cyclone consumes the ACE SPEC deck slot.

## Method and constraints

The same exact state planner from the paid pickup-replay study
enumerates all accepted opening, Prize and draw configurations and
optimizes Quick Ball discard payments, Nest Ball placement,
forced-Active backup creation, Bench pickup replay, and coin outcomes.

The test compares identical deck composition under the two turn-role
interpretations by moving Penny copies between the deterministic
pickup category and the discard-stock category. The equality for
zero Penny, first-versus-second inequalities, and monotone behavior
across the five tested packages are regression assertions.

**What the model does not establish:** It does not imply that going
second is better overall, nor that four Penny is a good decklist.
It does not price the Supporter action that could instead have been
Arven, Guzma & Hala, Colress, or another powerful Supporter, and it
omits opposing disruption, Energy/attack setup, prize races,
hand-mutating support Abilities, and multi-turn payoff. The attacker
timing advantage of going second is outside the objective.

The study isolates a single measurable **legality-window gap**:
a theoretically available pickup may have zero legal effect on the
first player's first turn, while still remaining useful as discard
payment for another Item.
