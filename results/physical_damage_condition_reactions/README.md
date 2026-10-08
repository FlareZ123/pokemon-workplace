# Printed Special Condition backlash on conserved physical boards

## Research question

Can the post-damage reaction bridge represent Ability-triggered **Special
Conditions**, while retaining the attacker identity and physical cards
through the Knock Out boundary?

**Yes, for the ordinary printed Poisoned, Burned, and Confused reactions
tested here.** The source compiler and reaction adapter are in
`tools/physical_damage_condition_reactions.py`; regression in
`results/physical_damage_condition_reactions/reproduce.py`.

## Card-grounded Ability sources

The eligible-print source compiler recognizes exact English ability wording
stating that its Active Pokémon, when damaged by an opposing Pokémon's
attack, causes the Attacking Pokémon to become Poisoned, Burned, or Confused,
even if the damaged defender is Knocked Out.

The distinct tested prints are:

- Roselia `sv5-8`, **Poison Point**: Poisoned;
- Heatran `sv6-123`, **Incandescent Body**: Burned;
- Hatterene `swsh35-20`, **Hazard Sensor**: Confused.

The bundled Extended damage-reaction catalog finds 12 print-level rows of
this form spanning 4 distinct text signatures, including other eligible
printed variants of these conditions.

For each invoked source, the compiler checks the actual named damage target,
the current printed identity and Extended-set status, positive final attack
damage, Active Spot location, the opponent's attack origin, and whether
the Ability is enabled. The caller currently supplies the last two dynamic
eligibility facts, since global Ability-lock evaluation belongs upstream.

## Physical transition

A resolved Haughty Order copy of Timeless-GX deals 150 damage to
a 60-HP Active Roselia. Roselia has zero remaining HP and remains physically
in play until the post-damage Poison Point trigger. The original attacking
Pokémon receives Poisoned, while Roselia and its stack remain in the pending
Knock Out window with every physical card count conserved.

Separate regressions use a 140-HP Heatran and established 150-HP Stage 2
Hatterene, using their actual printed HP and full in-play evolution stack
for Hatterene. Heatran's Burned effect coexists with preexisting Poisoned.
Hatterene's Confused effect can coexist with Poisoned and Burned; the
existing typed Special Condition kernel correctly replaces Asleep/Paralyzed
when a newer rotating condition is applied.

A prevented-damage control suppresses the reaction. An Ability-disabled
control suppresses it as well. A mismatched bound printed card raises a
validation error. If the original attacking Pokémon has already moved to
the Bench by the time Special Conditions would be inflicted, this narrow
model correctly avoids placing a Special Condition on either Benched actor
or replacement Active.

## Methodological boundary

The physical board currently stores regular Special Conditions as names.
The adapter deliberately uses the existing typed condition state helper to
preserve coexisting condition names and mutual exclusion. It does not retain
irregular Poison/Burn/Confusion counter payloads in the physical board,
resolve Pokémon Checkup, compute Energy discard reactions, or automatically
evaluate complex Ability-lock states. It must not be used to reconstruct
rich conditions from legacy names if an irregular payload exists.

The reference rulebook uses the ordering: attack damage, other attack
effects, effects activating when damaged, then Knock Outs. Thus source
eligibility and target identity are evaluated before disposal, even if the
defending Pokémon is already at zero HP.
