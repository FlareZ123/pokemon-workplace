# Stadium entry channels: play quota versus effect placement

## Question

Does the ordinary once-per-turn Stadium-play budget fully describe how Stadiums can enter play in paper Expanded?

No. Gothitelle `xy3-41` provides a concrete legal counterexample. Its Teleport Room Ability discards the Stadium in play and then **puts** a differently named Stadium from the discard pile into play.

Implementation: `tools/stadium_entry_channels.py`  
Regression: `results/stadium_entry_channels/reproduce.py`

## Rule distinction

The Advanced Player's Rulebook separates two ideas in I-B-04:

- Stadiums can be **put into play**;
- a player may only **play one Stadium during their turn**;
- the ordinary persistence rule specifically discusses a Stadium **played from the hand**.

The canonical `TurnAction.STADIUM_PLAY` quota therefore describes the ordinary play-from-hand action. It should not be charged merely because an effect moves a Stadium from another zone into play.

This is the same modeling principle already used for Energy: an effect-based attachment is a physical Energy transition without automatically consuming the ordinary manual-attachment channel.

## Concrete Expanded witness

The bundled legal card pool contains one direct Stadium-placement effect under a conservative scan:

`Gothitelle xy3-41 / Teleport Room`

> Once during your turn (before your attack), you may discard any Stadium card in play. If you do, put a Stadium card with a different name from your discard pile into play.

The reproducer scans every bundled Expanded set, applies the repository legality classifier, and finds exactly this one direct `put ... Stadium ... into play` effect.

## State transition

`StadiumEntryState` keeps:

- the canonical `TurnActionBudget`;
- physical Stadium copies in hand;
- physical Stadium copies in the discard pile;
- the physical Stadium currently in play;
- physical Teleport Room source identities;
- which of those sources have already used the Ability this turn.

`play_stadium_from_hand(...)` consumes `TurnAction.STADIUM_PLAY`.

`use_teleport_room(...)` changes the physical Stadium zones and marks only the chosen Gothitelle source as used. It leaves `stadium_plays_used` unchanged.

This yields legal lines such as:

`Teleport Room: A -> B, then ordinary Stadium play: B -> C`

and:

`ordinary Stadium play: A -> C, then Teleport Room: C -> B`.

In each line exactly one ordinary Stadium play is consumed even though the Stadium zone changes twice.

With two physical Gothitelle sources, the model can also execute:

`A -> B -> A`

through two Teleport Room uses while the ordinary Stadium-play quota remains untouched. A later Stadium from hand can still consume that separate quota.

## Conditional-resolution edge

Teleport Room uses the `Do ●●. If you do, do ■■` structure covered by II-E-20 together with the manual's general partial-resolution rule.

If a Stadium is in play but no differently named replacement exists in the discard pile, the first half can still discard the Stadium and the unavailable second half is ignored. If an eligible replacement does exist, the second half is mandatory and one must be chosen.

If no Stadium is in play, the first half cannot be performed at all, so Teleport Room cannot create a Stadium from the discard pile by itself.

## Planner implication

A simulator should separate at least:

1. the **ordinary Stadium-play quota**;
2. the **physical Stadium zone**;
3. **effect-based Stadium entry/removal transitions**;
4. source-specific once-per-turn Ability usage.

Treating every Stadium entry as `STADIUM_PLAY` incorrectly rejects Teleport Room after an ordinary Stadium play and incorrectly closes the ordinary Stadium play after Teleport Room.

Treating Teleport Room as generic Stadium removal also loses its mandatory replacement branch when a legal differently named Stadium is available.

## Relation to existing work

`stadium_removal_channels/` correctly classifies Gothitelle as a pre-attack Ability-based removal source. This result adds the missing second half of that card's transition: Teleport Room is simultaneously a removal action and a distinct discard-to-play materialization channel.

`turn_action_budget/` remains the correct owner of the ordinary Stadium-play count. This result shows why that budget should gate the **play action**, rather than every transition whose destination is the Stadium zone.

## Limits

This result does not yet model voluntary Stadium-effect usage such as "once during each player's turn, that player may..." after a Stadium is replaced and later returns. That usage history is a separate rule-state question and should not be inferred from Stadium entry alone.

It also assumes the caller has already established that the chosen Gothitelle's Ability is active. Ability suppression and board legality belong in the lock/board layers.

The direct-placement census is a conservative text-grammar observation over the bundled English snapshot. Future cards or alternate wording can require extending the grammar.
