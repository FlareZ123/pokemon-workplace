# Passive attack-effect immunity surface

## Question

How common are effectively legal passive Ability or attachment effects that can block effects of attacks, the defensive family that matters to Phantom Dive's Bench damage-counter effect?

Implementation: `tools/passive_effect_immunity_catalog.py`  
Regression: `results/passive_effect_immunity_catalog/reproduce.py`

## Current surface

The current English paper-Expanded snapshot contains **49 effectively legal print rows across 29 card names** whose Ability or attached-card rule contains "prevent all effects of attacks."

Source types:

- 43 Ability rows;
- 6 attached-card rule rows.

A conservative target-scope split gives:

- 38 self-protection rows;
- 8 multi-Pokemon protection rows;
- 2 attached-holder protection rows;
- 1 player/hand protection row.

Twenty-seven rows explicitly preserve ordinary attack damage while preventing attack effects. Twenty-two use the older "including damage" wording and therefore prevent both when their condition applies.

## Phantom Dive relevance

Phantom Dive's six Bench counters are an effect of an attack rather than damage. They can therefore be blocked by effect-immunity state even when the 200 damage to the Active target remains available.

Concrete passive witnesses include:

- Big Parasol `swsh3-157`: while its holder is Active, protects all of that player's Pokemon from attack effects;
- Mist Energy `sv5-161`: protects its attached holder from attack effects;
- Skeledirge `sv8-31` / Unaware: protects itself from attack effects while still allowing damage;
- Toedscruel ex `sv3-22` / Protective Mycelium: protects the player's Energy-attached Pokemon;
- Mew `xy12-53` / Neutral Shield: protects itself from both damage and effects against opposing Evolution Pokemon.

These are examples of why the Phantom Dive counter branch in the damage-board bridge has an independent effect-immunity gate.

## Strategic consequence for delayed-KO lines

The Timeless-GX -> Phantom Dive ALS relies on the first target surviving 150 damage and later receiving six attack-effect counters on the Bench.

A target can therefore satisfy the 160-210 remaining-HP arithmetic window and still invalidate the delayed KO if a live passive effect blocks Phantom Dive's counters.

This is a direct interaction between:

- position state;
- prior damage;
- effect-immunity state;
- attacker characteristics;
- attachment/Ability state.

A threshold-only planner will overstate the line unless it carries the immunity channel separately.

## Limits

The catalog is a surface inventory, not a complete eligibility compiler.

Many entries have additional conditions involving attacker category, attached Energy, target type, Active position of a provider, or other board state. The scope labels describe who the text can protect and do not assert that the effect is currently live.

Attack-generated temporary protection is excluded here because this result is specifically about passive Ability and attachment sources. Those temporary effects belong to the attack-effect state layer.
