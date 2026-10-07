# Damaged-by-attack reaction kernel

## Question

What state boundary is required between attack damage/effects and the final Knock Out check for cards that react to being damaged?

A distinct reaction phase is required. The Advanced Player's Rulebook places effects that activate when a Pokemon is damaged after attack damage and outside-damage effects, while Knock Outs are checked afterward.

Implementation: `tools/damage_reaction_kernel.py`  
Regression: `results/damage_reaction_kernel/reproduce.py`

## Card witnesses

The regression verifies current effectively legal card text for:

- Zamazenta `sv10-146`, Strong Bash: during the opponent's next turn, if Zamazenta is damaged by an attack, it puts damage counters on the attacker equal to the damage done, even if Zamazenta is Knocked Out;
- Spiky Energy `sv9-159`: if its Active holder is damaged by an opponent's attack, it puts two damage counters on the attacker, even if the holder is Knocked Out.

These effects require the damaged Pokemon and its state to remain available until the reaction is resolved.

## Mechanical witnesses

A 150-damage hit into a 130-HP defender with an active Strong Bash-like reaction:

1. places 150 damage on the defender;
2. triggers because final damage is greater than zero;
3. mirrors 15 damage counters onto a 150-HP attacker;
4. exposes both Pokemon as Knock Out candidates in the later shared KO check.

A 160-HP attacker survives the same reflected 150.

If all damage to the defender is prevented, final damage is zero. The damaged-by-attack condition is false and the reaction does not fire.

Two supplied Spiky Energy-like reactions place four counters total before the KO check, which can likewise create a simultaneous KO state.

## Representation consequence

Immediate removal at the moment a defender reaches zero remaining HP is incorrect for this phase family.

The engine needs to preserve at least:

`damage/effects -> damaged-by-attack reactions -> KO candidates -> KO trigger/disposal/Prize phase`

This complements the existing simultaneous-KO conservation work. The new kernel stops at candidate detection so disposal, attachment routing, Prize awards, and promotion remain owned by their existing layers.

## Limits

Reaction eligibility is semantic input. This kernel does not yet derive a live Strong Bash effect from a previous attack or discover Spiky Energy attachments automatically.

The implemented reaction bodies cover fixed counter reflection, counters scaled by an upstream count, and mirroring final damage. Orthworm ex `sv7-110` / Pummeling Payback is the scaled witness: two counters per Metal Energy becomes six counters when the caller supplies a live count of three. Other damaged-by-attack effects can perform different actions and will need additional semantic handlers.

The kernel also assumes supplied reaction order. The rulebook gives the damaged Pokemon's player ordering authority when several such effects activate, so strategic ordering belongs to an outer choice layer when effects do not commute.
