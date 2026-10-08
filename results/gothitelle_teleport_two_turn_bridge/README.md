# One Quick Ball, two turns, two functions: Gothita setup and Sky Field payload

## Research question

Can a single first-turn Quick Ball simultaneously establish a Gothita and
pre-position a Stadium that its future Gothitelle can use on turn two,
when the player cannot directly play Stadium cards from hand?

**Yes, in a bounded paper Expanded state.** The same mandatory Quick Ball
discard becomes Gothitelle's later Teleport Room payload, eliminating
the need for a second Item to discard Sky Field on turn two.

- Shared physical/temporal kernel: [`tools/gothitelle_teleport_two_turn_bridge.py`](../../tools/gothitelle_teleport_two_turn_bridge.py)
- Independent SFT: [`reproduce.py`](reproduce.py)
- [Successful GitHub Actions run 37775245112](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37775245112)

## Card/rule anchors

The test verifies each relevant print in the provided card pool and
the legality baseline:

| Card | ID | Function |
| --- | --- | --- |
| Quick Ball | `swsh1-179` | Discard 1 other card, search for 1 Basic Pokémon |
| Gothita | `xy3-39` | Basic for the intended Gothitelle evolution |
| Gothitelle | `xy3-41` | Stage 2 with Teleport Room |
| Rare Candy | `sv1-191` | Put the Stage 2 onto an established Basic, skipping Stage 1 |
| Sky Field | `xy6-89` | Bench limit increases to eight |
| Collapsed Stadium | `swsh9-137` | Bench limit reduces to four |
| Ninetales | `xy5-21` | Barrier Shrine prevents either player playing Stadiums from hand |

The official Japanese Pokémon card Q&A concerning Ninetales's Barrier
Shrine and Gothitelle's Teleport Room confirms that the latter may
still put a Stadium from the discard pile into play:
https://www.pokemon-card.com/rules/faq/details.php?id=9756

## Fixed starting state

At the beginning of the first personal turn, Collapsed Stadium is
already in play, and the player has three ordinary Benched Pokémon
plus an Active non-Gothitelle Pokémon. The affected player's ordinary
Bench capacity is four. Quick Ball is in hand, with the desired Gothita
still in the deck; Gothitelle and Rare Candy are already in hand.
Two additional desired Basics are available in hand. The required
Sky Field card is either in hand or still in the deck, depending on
the comparison. In a negative branch, a separate expendable junk
card can also pay Quick Ball.

Ninetales's Barrier Shrine is already effective, preventing ordinary
Stadium play from hand. The Collapsed Stadium is assumed to have been
put into play before this lock became effective. The test does not
model the opponent's board evolution or placement timing beyond
that grounded premise.

The model assumes no Item lock on Quick Ball or Rare Candy, no
Ability lock on Gothitelle, and that Gothita survives the intervening
opponent turn. The hand and deck composition are set directly rather
than sampled.

## Verified two-turn line

<text>

**Turn one**

1. Play Quick Ball, discarding the exact physical Sky Field copy.
2. Search Gothita from the deck into hand.
3. Bench Gothita as the fourth Bench occupant under Collapsed Stadium.
4. End the turn.

**Turn two**

1. Use Rare Candy on the previously established Gothita, evolving it into
   Gothitelle. The physical Basic remains in its Bench stack.
2. Use that Gothitelle's Teleport Room Ability to discard Collapsed Stadium
   and place the previously discarded Sky Field into play.
3. Bench both required additional Basics into the expanded capacity.

</text>

No ordinary Stadium play is required during either turn. The model
preserves source-specific once-per-turn Ability history and
verifies that the same physical Sky Field copy moved
`hand -> discard -> Stadium in play`.

The Rare Candy transition is explicitly rejected on the first
turn and only allowed after the earlier-turn Gothita has been
established. The model represents the evolution as a separate
Stage 2 card added atop a tracked Basic stack, preserving the
single physical Bench occupant.

## Negative and alternative continuations

| Setup variant | Turn-two capability | Additional Basics admitted |
| --- | --- | ---: |
| Quick Ball discards Sky Field on turn one, Barrier Shrine live | Teleport Room puts Sky Field into play | **2** |
| Quick Ball discards junk on turn one; Sky Field only drawn turn two; Barrier Shrine live | Ordinary Stadium play blocked, Teleport removes Collapsed only | **1** |
| Quick Ball discards junk while Sky Field remains in hand; Barrier Shrine live | Ordinary Stadium play blocked, Teleport removes Collapsed only | **1** |
| Quick Ball discards junk; Barrier Shrine absent | Directly play Sky Field from hand instead | **2** |

The fourth row is important. In an unlocked state, Sky Field held in hand
already provides a direct Stadium-play solution. The dual-use payment's
advantage is **conditional on the play-from-hand channel being blocked or
strategically unavailable**, alongside the valid early Basic search.

The immediate mistake of paying with junk rather than Sky Field is
observable only after one respects card-zone state, the future Ninetales
Stadium-play lock, and the one-use Quick Ball resource.

## Model validation

The SFT invokes the repository's canonical typed Quick Ball transaction
for its exact cost and Basic search, the physical Bench-capacity bridge
for legal placements, the Stadium-entry kernel for Teleport Room,
and the turn-budget kernel for turn transitions.

It checks every represented card-class total across both turns
(Quick Ball, Gothita, Gothitelle, Rare Candy, Stadiums and the two
entrants); the original Basic and newly added Stage 2 are distinct
physical cards occupying one Bench slot. It also verifies that Stadium
plays are neither silently consumed nor allowed under Barrier Shrine.

All positive/negative variants and card-text/legality checks passed
GitHub Actions run `37775245112`.

## Interpretation

A first-turn discard payment can function as a delayed second-turn
**strategic asset**, particularly when it moves a resource into the
only zone accessible through a future action. Quick Ball's role
in this case combines Basic setup and Stadium pre-positioning.

This advances the prior finding in
[`teleport_discard_payload_line/`](../teleport_discard_payload_line/)
by enforcing a real two-turn evolution window instead of assuming
Gothitelle is already in play.

It remains a deterministic witness. The probability of naturally
having Quick Ball, Sky Field, Gothitelle, Rare Candy, a searchable
Gothita and a suitable Bench arrangement is not computed here.
A later joint stochastic model should estimate access without
multiplying independent simulations with incompatible conditioning.

## Limitations

The transition engine explicitly represents the Stage 2 card at
`bench_evolution` in the counted zone ledger rather than a generic
multistage evolution engine. It checks the specific legal Rare Candy
timing but does not enforce every possible evolution or Rare Candy
restriction. The opponent's already-live Barrier Shrine and already
in-play Collapsed Stadium are exogenous inputs with compatible history;
the test does not simulate their acquisition.

The two Bench entrants are assumed available in hand and otherwise
legal. No full turn-based game, damage, Prize retrieval, Supporter
contention, or matchup-specific winning objective is simulated.
