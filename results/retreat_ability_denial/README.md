# Continuous Ability-based Retreat denial

## Question

Can an Expanded Retreat executor distinguish a zero-Energy Retreat Cost
from permission to Retreat, when an opponent's continuous Ability forbids
the normal Retreat action?

## Rules and exact-print scope

The Advanced Player's Rulebook C-14 distinguishes a restriction on normal
Retreat from effect-based switching. The latter may remain available even
when the affected Active Pokémon cannot Retreat. D-13 separately allows
cost-nullifying effects such as Float Stone to override cost increases.
Cost nullification cannot remove an independent prohibition on the action.

`tools/retreat_ability_denial.py` compiles eight exact printed sources in
the bundled paper Expanded card pool:

- Snorlax `bw8-101`, `pgo-55` (**Block**);
- Spiritomb `sm35-47` (**Cursed Whirlpool**);
- Omastar `sv3pt5-139` (**Primordial Tentacles**);
- Flygon `swsh3-91` (**Labyrinth of Sand**);
- Cradily `sm12-11` (**Swaying Strangle**);
- Dragalge `xy2-71`, `xyp-XY10` (**Poison Barrier**).

The first five print sources are Active-dependent: their effects apply
only when their own source is in the opponent's Active Spot. Cradily is
position-independent and prohibits an opponent's Pokémon affected by
a Special Condition from Retreating. Dragalge is position-independent,
but its opponent's Active must be Poisoned.

All predicates depend on the source's current `abilities_enabled` flag.
The board must already have correctly resolved suppression, and this
narrow compiler does not infer arbitrary copy or transformation effects.

## Composition

`tools/board_derived_retreat.py` now derives
`retreat_denial_source_ids` from both current boards after Energy
normalization. The transaction is withheld when the returned set is
nonempty, regardless of the computed numeric Retreat Cost.
This check is independent of the existing attack-applied
`temporary_retreat_lock` state.

The result retains blocking source IDs, permitting a future search
policy to distinguish eliminating the Active source, suppressing an
Ability, clearing a Special Condition, or using an effect-based switch.

## Reproducible witnesses

`results/retreat_ability_denial/reproduce.py` starts with an Active
Pokémon wearing Float Stone, so its effective Retreat Cost is zero.
It verifies:

- each of the five Active-dependent prints prevents that free Retreat;
- moving the source to the Bench or disabling its Ability removes the
  corresponding prohibition;
- a Benched Cradily prevents Retreat under each tested Special Condition,
  while a healthy Active is unaffected;
- a Benched Dragalge prevents Retreat only while the target is Poisoned;
- Cradily and Dragalge independently contribute provenance when both apply;
- a normal `switch_active()` transition remains valid for the same
  Poisoned Active that cannot Retreat;
- an attack-applied temporary Retreat lock still blocks the normal
  Retreat when no continuous source is present.

## Limitations

This is an exact-print semantic island and does not claim an exhaustive
inventory of all possible retreat-restricting Abilities or global effects.
Rule applicability may also change under source removal, Ability suppression,
or interaction with other effects. The adapter trusts its input boards and
existing typed suppression facts. Full card-pool completeness, timed attack
restrictions, and replacement effects remain separate research problems.

Run `python results/retreat_ability_denial/reproduce.py`.
