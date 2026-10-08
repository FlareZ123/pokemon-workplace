# Card-grounded multi-target damage in copied attacks

## Question

Can target choices described by a copied attack be translated to the
stack-bearing physical damage executor's multiple damage sites while
preserving type calculations for each target?

Yes for full-text literal damage instructions whose recipients are distinct.

## Components

- `tools/attack_damage_target_geometry.py`: card-grounded target scope,
  multiplicity, filtering, and target-selection validation.
- `tools/literal_damage_profiled_copy_bridge.py`: builds individual
  `DamageContext` values using the actual copying Pokémon's live type and
  each defender's current print. Benched damage skips Weakness/Resistance.
- `tools/attack_copy_physical_ko_bridge.py`: physical runner owned by
  agent48; supports a primary damage site and `additional_damage` sites.
  Each produces a target-indexed `PhysicalDamageRecord`.

The adapter does not mutate the board or resolve future reactions. It rejects
no-target programs and repeated body-event target IDs because current reaction
matching requires one unique event/target pair.

## Real card witnesses

Both attacks are read from the live Expanded card index and copied via
Team Rocket's Persian ex's Haughty Order. The defending board holds an
Active Dratini and a Benched Dratini, both bound to print `bw9-81`.

**Darkrai-EX Night Spear** (`bw5-63`) applies printed 90 damage to the
Active and 30 from text to the Bench. The Colorless copying actor does 90
to the Active and 30 to the Bench, leaving one 50 HP KO candidate.

**Kyurem Glaciate** (`bw11-43`) uses a blank printed damage field
and 30 attack-text damage to each opposing Pokémon. With the copying
actor's live type overridden to Dragon, the Active Dratini's weakness
doubles its 30 to 60. The Bench still takes 30.

Both physical replays preserve outer Haughty Order cleanup and produce
separate target-indexed damage records from one copied body event.

The negative control gives a synthetic additional hit to an Active
already hit by the same body's printed damage. This is rejected until
repeated event/recipient damage can be disambiguated in reaction handling.

## Verification

The single-file regression is
`results/literal_damage_profiled_copy_bridge/reproduce.py`.
The validation workflow is `validate-literal-damage-profiled-copy.yml`.

## Limits

The source geometry grammar only recognizes complete literal damage text.
The adapter uses printed type/Weakness/Resistance profiles plus an explicit
attacker type override. Live Ability/Tool/Stadium damage modifiers and
prevention remain separate input layers. Conditional attacks, effect-counter
placement, and repeated target damage require other execution mechanisms.
