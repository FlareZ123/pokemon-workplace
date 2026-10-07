# Opponent capacity contraction can erase reserved Bench slack without discarding

## Question

If an end-of-turn release leaves one open Bench slot for the player's next turn, is that reserved slack a durable resource through the opponent's intervening turn?

No. A capacity restriction can reduce the Bench maximum to the current occupancy, erase the reserved slot, and force zero discards. A model that scores Bench contraction only by discarded occupants can therefore miss a strategically decisive loss of future action capacity.

Implementation: `tools/interturn_bench_slack_exposure.py`  
Regression: `results/interturn_bench_slack_exposure/reproduce.py`

## Card-text anchors

Two legal paper-Expanded Stadium effects provide concrete contraction states:

- **Collapsed Stadium** `swsh9-137` / `swsh11-215`: each player can have at most four Benched Pokémon and discards down to four when necessary.
- **Parallel City** `xy8-145`: the chosen side can have at most three Benched Pokémon and discards down to three when the Stadium enters play.

The existing Bench-capacity work already models these as persistent restrictions. This result places them specifically in the opponent window between a release action and a planned next-turn Bench entry.

## Silent slack destruction

Start with four live core occupants after a spent support Pokémon has been removed. Under ordinary capacity five:

- occupancy = 4;
- capacity = 5;
- reserved slack = 1.

If the opponent plays Collapsed Stadium before the next turn:

- capacity becomes 4;
- occupancy remains 4;
- forced discards = **0**;
- reserved slack falls from 1 to **0**;
- the planned next-turn Bench entrant is blocked.

This is a mechanically important zero-discard disruption state.

A forced-discard-only disruption metric would assign no immediate board loss here. The continuation state still changed from “one Bench entry available” to “no Bench entry available.”

## Early entry trades slack exposure for board-loss exposure

The model also compares an immediate release-and-entry line. Four core occupants have continuation values 10, 8, 7, and 6. A required entrant has value 9.

After the entrant is placed immediately, occupancy is five.

Under Collapsed Stadium:

- one occupant must be discarded;
- the affected player's continuation-minimizing choice discards the value-6 core;
- the required entrant remains in play;
- modeled continuation loss = 6.

Under the restricting side of Parallel City:

- two occupants must be discarded;
- the value-6 and value-7 cores are discarded;
- the required entrant remains;
- modeled continuation loss = 13.

The immediate line can therefore preserve the entrant's materialization objective through contraction, but it does so by exposing already-materialized board value to forced-discard loss.

The delayed line has the opposite profile. It can avoid a discard under Collapsed Stadium while still losing the future Bench action entirely.

## Entrant value matters

Early entry is not automatic protection.

When the required entrant is assigned continuation value 2 instead of 9, Collapsed Stadium's optimal forced-discard choice removes the entrant itself. The immediate-entry objective then fails despite having been completed before the opponent window.

This connects temporal planning with the earlier continuation-value contraction model: protection depends on which occupant the affected player rationally chooses to sacrifice.

## Strategic interpretation

Two distinct resources must be preserved across the opponent window:

1. **material occupants already in play**;
2. **unoccupied capacity reserved for future materialization**.

Capacity contraction can attack either resource.

Forced-discard count measures damage to the first resource. Bench slack measures the second. Neither subsumes the other.

A stronger planner should therefore carry both occupancy and capacity through opponent transitions and evaluate future entry feasibility after those transitions. “No Pokémon was discarded” is insufficient evidence that a contraction was strategically harmless.

## Evidence class

Collapsed Stadium and Parallel City effects are direct card-text facts from the bundled legal card pool. Forced-discard selection uses the repository's existing continuation-value contraction model. The five reported scenarios are deterministic state-transition calculations.

## Limitations

The continuation values are stylized local utilities, not estimates of full-game value.

The model assumes the opponent can and chooses to establish the stated capacity restriction. It does not model Stadium access probabilities, Stadium contention, counter-Stadiums, Item lock, Tool lock, Ability-based restrictions, or the opponent's incentives.

The model also does not yet give the player a next-turn action that restores capacity before attempting the Bench entry.

## Next useful work

The next extension should add capacity restoration on the player's next turn. Replacing Collapsed Stadium or Parallel City can reopen the reserved slot, but Stadium play has its own one-per-turn bandwidth and can compete with other Stadium objectives. That would turn silent slack destruction into a recoverability question rather than a terminal block.
