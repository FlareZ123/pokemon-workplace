# Copied attack damage uses the copying Pokémon's type

## Question

When one Pokémon uses another Pokémon's attack through a copy effect, which
Pokémon supplies the type used for Weakness and Resistance?

The attacking Pokémon does.

Implementation: `tools/copy_attack_profile_damage_bridge.py`  
Regression: `results/copy_attack_profile_damage_bridge/reproduce.py`

## Rule consequence

The damage rules apply Weakness and Resistance by comparing the type of the
Pokémon doing the damage with the target's printed modifier.

Copy semantics keep the declared attacker distinct from the selected attack
body. A copied attack therefore imports damage/effect instructions without
turning the attacker into the source Pokémon.

Using the copied source card's type for Weakness would be a representation bug.

## Identity boundary

The stack-bearing physical board stores physical Pokémon-card instance IDs.
Those IDs are not database print IDs.

The bridge therefore requires an explicit current-print binding for each board
Pokémon. It does not reinterpret a physical instance ID as a card database key.

That preserves the repository's four-way identity separation:

- print identity;
- exchangeable card class;
- physical card instance;
- Pokémon board object.

For an evolved Pokémon, the binding should identify the current top print.

## Profiled damage materialization

`materialize_profiled_copy_program()` combines:

- a card-grounded compiled attack body;
- the live copying Pokémon's profile or explicit current type override;
- the target's current print profile;
- live Weakness/Resistance enablement flags;
- the existing exact counter-allocation validator.

The result is a physical board event program with ordered damage-stage inputs.

An explicit `attacker_types` override allows live type-changing effects to be
represented without mutating the immutable printed profile.

## Regression witness

Team Rocket's Persian ex `sv10-150` is Colorless.

It copies Dragapult ex `sv6-130`'s Dragon-source Phantom Dive and attacks a
Dratini `bw9-81` whose Weakness is Dragon ×2.

The correct copied-attack calculation is:

- Phantom Dive base damage: 200;
- attacking Pokémon type: Colorless;
- target Weakness: Dragon ×2;
- final damage: 200.

A deliberately source-typed comparison uses Dragapult's Dragon type and reaches
400. That comparison demonstrates the exact error the bridge prevents.

The executable Haughty Order copy replay uses the actor-typed 200 value, places
six effect counters on the Bench, and preserves the outer shuffle continuation.

## Independent modifier bypass

Some attack texts skip exactly one of the two type-modifier stages. The
compiled attack contract now retains `ignore_weakness` and
`ignore_resistance` separately, alongside the older combined
`ignore_weakness_resistance` compatibility property.

Two real Expanded witnesses distinguish the semantics:

- Cramorant `swsh11-50`, Spit Innocently: 110 Water damage against
  Water-weak Growlithe `sv1-30` remains **110**, whereas applying
  Weakness would yield **220**.
- Landorus `sv8-110`, Buster Swing: 130 Fighting damage against
  Fighting-resistant Drowzee `sv1-82` remains **130**, whereas applying
  Resistance would yield **100**.

A stronger independent-stage control uses a live `Fighting + Psychic` attacker
against Darkrai-GX `sm3-88`, which is Fighting-weak (×2) and
Psychic-resistant (−20). In that combined state, Weakness-only bypass
gives **90** (110 − 20) and Resistance-only bypass gives **260**
(130 × 2), demonstrating that the other modifier still applies.

The bridge implements these one-sided bypasses when resolving printed type
stages. An explicit `ignore_weakness_resistance=False` remains a useful
controlled counterfactual that restores both stages, while `True` bypasses
both stages. This extension does not require new fields in the shared damage
kernel and retains its existing calculation order.

The parser recognizes exact `damage isn't affected by Weakness`,
`damage isn't affected by Resistance`, and combined forms. It intentionally
does not infer Active-target bypass from generic Bench-only reminders
such as `Don't apply Weakness and Resistance for Benched Pokémon`.
Other attack-text phrasings require separate coverage review.

## Live type override

The same bridge is rerun with an explicit current attacker type of Dragon. That
state correctly reaches 400 damage.

This keeps printed identity and live combat state separate: the same Persian
print can have a different current type if another game effect says so.

## Physical HP binding

`hp_by_stack_board()` derives HP from the explicit current-print map rather
than from physical instance IDs. The regression binds the two defender board
objects to Dratini and Dragonair prints and obtains 50 and 70 HP respectively.

## Finding

Attack-body ownership and damage-type ownership are separate dimensions.

A copied attack should preserve the selected body's text while damage modifiers
continue to read the Pokémon actually performing the attack, subject to live
type-changing effects.

This is another reason a simulator should avoid replacing the outer attack
object wholesale with the copied source attack.

## Limits

The bridge currently uses printed target Weakness/Resistance plus explicit
enable/disable flags. It does not yet derive live type changes or
Weakness/Resistance removal from board effects automatically.

The text compiler covers a conservative subset of explicit Weakness/Resistance
bypass wording. Unknown or conditional text still requires independent review.

Multi-match Weakness/Resistance remains subject to the conservative limits of
`profile_damage_context.py`.
