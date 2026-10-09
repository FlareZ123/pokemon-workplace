# Pokémon Ranger turns off both attack-applied Energy permissions and penalties

## Question

Does playing Pokémon Ranger to escape an attachment-triggered turn-end attack preserve Dragonair's Dragon's Wish Energy-attachment benefit?

## Answer

**No.** Pokémon Ranger `xy11-104` removes *all effects of attacks on each player and their Pokémon*. In a state where both Dragonair's Dragon's Wish and Slakoth's Lazy Howl (or Hypno's Daydream) affect the same turn, Ranger removes both. The player gains freedom to attach Energy to the originally Defending Pokémon without ending the turn, and simultaneously loses the permission to attach any number of Energy cards manually.

The print is Expanded-legal in the bundled database. Source text and legal print status are validated in the reproducer.

## Source-backed tactical comparison

Assume player A has a four-Fire-Energy hand, Dragon's Wish permission on A's current turn, an originally Defending Active target affected by Lazy Howl/Daydream, an unaffected Benched Pokémon, and an unspent Supporter.

| Line | Actual manual attachments | Can still attack this turn? | Important constraint |
| --- | --- | --- | --- |
| No Ranger, attach to target immediately | 1, to target | No | Lazy Howl/Daydream ends A's turn |
| No Ranger, attach twice to Bench, then to target | 3, two to Bench and one to target | No | Turn ends after target attachment |
| Ranger before attaching, then attach to target | 1, to target | Yes | Dragon's Wish also removed; ordinary one-per-turn limit applies |
| Attach twice to Bench, then Ranger | 2, both to Bench | Yes | Prior manual usage of 2 persists after permission removal, so target is no longer manually attachable that turn |

The available printed effects create a genuine **sequencing tradeoff**. Ranger can protect the right to attack that turn, but choosing to remove the adverse attack effect also cancels the extra manual-attachment bandwidth. Using the extra bandwidth first makes Ranger's later removal less useful for adding Energy to the threatened target because the ordinary hand attachment quota has already been exceeded.

Two other real resource constraints matter:

- Ranger consumes the Supporter allowance. If another Supporter was used already and no applicable quota-expansion effect exists, Ranger cannot be played that turn.
- Magnezone Dual Brains can increase the allowed Supporter count to two while live. A deliberately quota-two benchmark permits Ranger as the second Supporter, preserving the integer usage record.

All four lines and the Supporter contention edge cases are reproduced identically with the two legal trigger sources.

## Implementation

`tools/pokemon_ranger_attachment_projection.py` represents the local projected effect of Ranger on the two modeled windows. It consumes `TurnAction.SUPPORTER` from the canonical turn budget and simultaneously clears `NextTurnAttachmentWindow` and `HandAttachmentTurnEndWindow`. It leaves the physical hand Energy placements and used manual quota intact.

`results/ranger_attachment_tradeoff/reproduce.py` exercises the paired source windows, actual identified hand Energy events, Supporter constraints and the Ranger timing policies. This adds a game-action decision to the preceding mechanical models:

- [Dragon's Wish permission](../next_turn_attachment_window/)
- [Attachment turn-ending deadlines](../hand_attachment_turn_end/)

## Boundaries

The Ranger Supporter card itself is not yet materialized in the underlying `EnergyAttachmentState`. Its presence in hand, source-scoped Supporter locks, and the card's movement to the discard pile must be verified by an upstream typed Supporter executor. This is an exact **local effect/quota projection** conditional on Ranger being playable and present, not a complete full-game Ranger play.

The no-effect guard rejects use when neither of these two windows can change, although other attack effects elsewhere in a full game can make a real Ranger play legal.

The modeled state does not assert the resulting Active Pokémon is ready to attack or that a specific attack can legally be announced. "Can still attack" in the table means the generic turn is open and the ordinary attack action remains available. Opponent interference, specific attack requirements, and bench positioning are additional constraints.

Strategic value depends on all those constraints and the expected benefits of taking a turn's attack, so the table is a conditional legality frontier rather than a matchup win-rate claim.
