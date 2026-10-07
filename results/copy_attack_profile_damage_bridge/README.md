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

Attack text that ignores Weakness/Resistance must also be supplied explicitly;
the simple attack compiler does not yet parse that wording.

Multi-match Weakness/Resistance remains subject to the conservative limits of
`profile_damage_context.py`.
