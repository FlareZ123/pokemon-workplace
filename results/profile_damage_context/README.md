# Printed type modifiers into ordered damage

## Question

Can exact card-print Weakness and Resistance feed the ordered damage kernel without hard-coding only modern x2 / -30 values?

Yes for the audited current profile surface.

Implementation: `tools/profile_damage_context.py`  
Regression: `results/profile_damage_context/reproduce.py`

## Mapping

The bridge matches the attacking Pokemon's type tuple against the target profile's printed typed modifiers and resolves the rulebook damage stages:

- multiplicative Weakness maps to the step-3 multiplier;
- additive Weakness maps to the step-3 addition;
- subtractive Resistance maps to the step-4 reduction.

The ordered damage kernel now accepts `weakness_addition`, allowing the legacy Uxie `me55c-43` Psychic +20 Weakness to resolve exactly.

## Regression witnesses

With a 100-damage attack:

- Psychic into Uxie `me55c-43` becomes 120;
- Fairy into Dialga-GX `sm5-100` becomes 200;
- Fighting into Flying Pikachu VMAX `cel25-7` becomes 70;
- Fighting into audited Murkrow `me55-93` becomes 70;
- an unrelated type leaves damage at 100.

The regression also disables Flying Pikachu VMAX's Resistance as a live-state overlay and confirms the same Fighting hit returns to 100.

## Conservative boundary

The resolver rejects more than one simultaneously matching Weakness or Resistance modifier.

That case is deliberately left explicit. The card pool contains historical multi-Weakness structures, while the supplied Advanced Player's Rulebook excerpt describes applying the matching modifier without spelling out a multi-match composition rule. Encoding a guessed composition would be less trustworthy than preserving the unresolved state.

Likewise, non-subtractive Resistance is rejected after the audited card-data override layer. The raw Murkrow x2 Resistance anomaly is preserved in the source database and corrected before profile compilation.

## Architectural implication

Printed card identity can now flow through:

`print_id -> card profile -> current type-stage inputs -> ordered damage -> damage counters -> KO candidates`

Live type changes, Weakness/Resistance removal, and attack text that ignores Weakness/Resistance remain explicit state inputs rather than mutations of the immutable printed profile.
