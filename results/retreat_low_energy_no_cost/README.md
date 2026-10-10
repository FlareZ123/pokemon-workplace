# Source-verified low-attached-Energy Abilities create free-Retreat thresholds

## Research result

The BW-onward English card snapshot contains seven Pokémon Ability
families, across ten printed card IDs, which grant no Retreat Cost
when the holder has sufficiently **little** attached Energy.

Six of these Ability families require zero attached Energy.
**Golisopod's Emergency Exit** instead requires at most two attached
Energy units, creating a more subtle resource threshold:
a larger Retreat payment can leave two attached Energy units and
activate a later free Retreat, while a smaller payment leaves three
and disables it.

This shows that preserving more attached Energy need not preserve
more future mobility, even without Dashing Pouch or other
hand-return effects.

## Exact card-source registry

The implementation `tools/retreat_attached_energy_free_cost.py`
contains a static registry verified against every bundled English
card file.

| Card and Ability | Exact print IDs | Condition |
| --- | --- | --- |
| Lampent, Freefloating | bw8-22 | No attached Energy |
| Zubat, Free Flight | bw8-53 | No attached Energy |
| Gligar, Free Flight | sm10-98 | No attached Energy |
| Charmander, Agile | me2-11 | No attached Energy |
| Ethan's Magcargo, Melt Away | sv10-36, me2pt5-24, me2pt5-222 | No attached Energy |
| Morpeko, In a Hungry Hurry | sv4-121, sv4-206 | No attached Energy |
| Golisopod, Emergency Exit | sm11-51 | Two or fewer attached Energy units |

These source IDs are checked against printed card names, Ability
names and condition text in `source_audit.py`. The code only
activates the effect on recognized prints with enabled Abilities.

**Energy units are distinct from Energy cards.** A single Double
Colorless Energy card provides two Energy units for this threshold,
so DCE plus one Basic Energy gives three units and does not activate
Emergency Exit. A DCE by itself gives two and does activate it.

The compiled modifier is consumed by the existing
`derive_environment_retreat_modifiers` pass and participates in the
rulebook D-13 no-Retreat-Cost precedence over Galar Mine,
Big Net or other represented numeric modifiers.

## Exact physical two-turn Golisopod witness

Start with Golisopod `sm11-51` (printed Retreat Cost four) Active,
holding two DCE cards and three Basic Psychic Energy cards,
totaling seven Energy units. Pivot and Backup are Benched.

Two legal ways to Retreat to Pivot:

| Payment | Golisopod after Retreat | Emergency Exit |
| --- | --- | --- |
| Both DCE | Three Basic Energy, 3 units | Inactive |
| Both DCE and one Basic | Two Basic Energy, 2 units | Active |

The second payment is legally larger, including more physical
Energy than needed for the cost-four Retreat.

After the opponent Knocks Out Pivot and Golisopod is promoted,
Galar Mine increases its Retreat Cost by two. A new turn begins.

- Minimal payment left three units and Emergency Exit inactive:
  effective Retreat Cost is six; no current payment can meet it.
- Larger payment left two units and Emergency Exit active:
  effective Retreat Cost is **zero** despite Galar Mine; Magcargo
  is not involved, and Golisopod can move to Backup without paying.

The physical Retreat action enumerator validates the exact card
IDs, both first payments, KO/promotion topology, new-turn quota,
future cost and final zero-Energy-payment Retreat.

## Verification and scope

`source_audit.py` checks all ten print IDs against the bundled
English card pool. `reproduce.py` checks every source at the
threshold, its failure with Ability suppression and incorrect print
IDs, and the Golisopod two-turn witness.

The CI workflow also reruns the earlier
[Ethan's Magcargo Melt Away result](../retreat_melt_away_overpayment/)
and the parent environmental modifier regression.

The result establishes a rules-supported reachable continuation
in a constructed game state, with KO/Stadium transitions supplied
as scenario conditions. It is not a frequency estimate or
competitive endorsement of Retreat overpayment.

The source catalog is English only; regional Japanese-only promo
prints may extend the possible source set. No source is inferred
from matching a Pokémon name without the exact verified print ID.
