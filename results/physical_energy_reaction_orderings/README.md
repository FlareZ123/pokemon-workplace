# Damage-reaction ordering controls the fate of a single Double Colorless Energy

## Question

Does the damaged player's right to order simultaneous step-6 reactions create
different physically legal Energy outcomes, even when neither reaction changes
damage or Knock Out status?

**Yes.** A copied-attack witness combines the **Shell Spikes** Ability of
Turtonator `me3-17` and a physically attached **Handheld Fan** Tool
`sv6-150` in one simultaneous damage-reaction window. The research records
full conserved identities and independently evaluates both permissible orders.

Implementation: `tools/physical_energy_reaction_orderings.py` and
`tools/physical_energy_backlash_reactions.py`.

Regression: `results/physical_energy_reaction_orderings/reproduce.py`.

## Printed-card witness

An Active Team Rocket's Persian ex has **one Double Colorless Energy**
(`bw11-113`) attached, fulfilling the two-Colorless cost of Haughty
Order. It copies Timeless-GX from an opponent's revealed Dialga-GX and deals
150 damage to a 120-HP Active Turtonator with Handheld Fan attached.
Each player has one additional Benched Pokémon.

Turtonator's Shell Spikes and the attached Handheld Fan both react to being
damaged by an opposing Pokémon's attack even if the source is Knocked Out.
Shell Spikes discards one Energy from the Attacking Pokémon; Handheld Fan
moves one Energy to a Pokémon on the Attacking Pokémon owner's Bench.
Double Colorless Energy has no printed Pokémon-specific receiving restriction,
so its physical card can move to that Bench.

The Advanced Player's Rulebook E-03 explicitly gives the player of the
damaged Pokémon the choice of order for multiple such reactions.
Accordingly, Turtonator's player controls these two alternatives:

| Reaction order | Step one | Step two | Final location of DCE |
| --- | --- | --- | --- |
| Shell Spikes, then Handheld Fan | Discard DCE from original attacker | No Energy remains on original attacker to move | Attacking player's discard |
| Handheld Fan, then Shell Spikes | Move DCE to attacking player's Bench | No Energy remains on original attacker to discard | Attached to attacking player's Bench |

The Tool remains physically attached to the defender until the subsequent
Knock Out disposal, and physical card-class totals are conserved for both
outcomes.

## Finding

The two reactions **do not commute**. Their order affects which card-zone
and Pokémon-attachment transitions remain executable during the same
post-damage window. A simulator must preserve the damaged player's order
choice; independent aggregation of “discard 1 Energy” and “move 1 Energy”
would produce an impossible or arbitrary final state.

The example isolates the clean one-Energy, one-Bench case. When several
Energy cards or Bench recipients exist, the damaged player's policy must
also choose each eligible target at the corresponding intermediate state.
The ordering enumeration accepts that policy explicitly.

## Limitations

The attack-copy kernel does not currently enforce the live Haughty Order
Energy payment. The regression checks the printed cost and equips the
physical attacker with one Double Colorless Energy. The 150-damage
Timeless-GX effect is a caller-supplied execution program rather than an
automatically compiled GX damage payload.

The Engine currently permits movement for Basic Energy and a small
whitelist of unrestricted Special Energy, including Double Colorless.
Other Special Energy may have recipient restrictions and should require a
printed receiving-card profile before reattachment. This experiment does
not determine optimal play under a full matchup, Prize race, or future-turn
simulation. It proves a local, rules-permitted resource-topology difference.
