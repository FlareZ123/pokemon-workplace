# Effect-placed Grand Tree can activate after Stadium-play quota is spent

## Research question

Can Gothitelle's Teleport Room (`xy3-41`) place a Grand Tree
(`sv7-136`) from the discard pile and then use its voluntary
evolution effect on the same turn, even when the player's ordinary
Stadium-play allowance has already been spent?

## Finding

Yes, when all represented prerequisites are satisfied. Gothitelle's
Teleport Room discards the current Stadium and puts a differently named
Stadium from the discard pile into play. This is effect-based placement,
rather than the player's once-per-turn action of playing a Stadium card
from hand.

Grand Tree's effect is once during each player's turn and can be used
while it occupies the Stadium zone, separately from the action of
placing it there. Its Basic-evolution timing restrictions still apply.

The valid controlled transition is:

`Brooklet Hill already in play + Grand Tree in discard + Gothitelle Teleport Room available`

`-> Teleport Room discards Brooklet Hill, places Grand Tree`

`-> Grand Tree searches Ivysaur and evolves an eligible Bulbasaur`

The ordinary Stadium-play quota remains spent throughout. After this
activation, the in-play Grand Tree effect cannot be activated again
in the same actor turn.

## Executable integration

`tools/teleport_grand_tree_bridge.py` connects the existing
`StadiumEntryState` and the corrected Grand Tree evolution source gate.

It treats **StadiumEntryState as the sole owner** of the physical
Stadium zone, discard pile and ordinary turn budget. A transient
`StadiumEffectState` is projected from the current Stadium card and
a per-entry usage token, rather than maintained as a second independent
physical card inventory.

`teleport_grand_tree_from_discard()` uses the existing
`use_teleport_room()` transition. If the target copy cannot be found
in discard, the source was already used, or the current Stadium is
ineligible, the requested transition is rejected.

`activate_teleported_grand_tree()` projects an in-play Stadium source
and runs Grand Tree's existing one-activation evolution chain.
Successful execution marks the current effect-use instance. Failed
target evolution preserves the input state.

## Reproduction

`python results/teleport_grand_tree_bridge/reproduce.py`

Regressions cover physical Stadium-zone transition, discarded Stadium
identity, a spent ordinary Stadium-play quota, Gothitelle once-per-source
usage, one successful Grand Tree evolution, same-instance repeated-use
rejection, invalid evolution rollback, missing discarded target, and
turn-ended prohibition.

## Boundaries

This is a deterministic concrete witness, conditional on an eligible
Gothitelle actually being in play and its Ability remaining available.
`StadiumEntryState` enforces a declared source ID and once-per-source
history; neither layer presently checks ability suppression, owner-specific
access, evolving or playing Gothitelle itself, or card-specific lock
effects. Stage 1 availability remains a caller-supplied Pokémon card
rather than a physical deck search in this adapter.

The per-entry usage token describes a new in-play Stadium entry.
The example only gives Grand Tree its first activation after being
placed from discard. Whether *the same physical copy* leaving and
returning within a single turn refreshes its effect-use limit is not
settled by the older Brooklet Hill ruling that specifically used a
different physical copy. This bridge does not claim a general ruling
for that different scenario.

The turn scheduler must refresh per-player-turn voluntary use via
`begin_stadium_turn()` at real turn boundaries.

## Evidence and confidence

- Bundled card texts: Gothitelle `xy3-41`, Grand Tree `sv7-136`.
- Advanced Player's Rulebook B-04 (Stadium play and activation).
- Existing `results/stadium_entry_channels/` and
  `results/stadium_effect_instance_usage/` models.

High confidence for the composed deterministic source/usage boundary.
The full game-state preconditions remain explicitly outside this scope.
