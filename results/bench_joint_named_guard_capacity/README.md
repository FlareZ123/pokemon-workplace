# Joint named Ability prerequisites: minimal simultaneous Bench capacity

## Question

When two distinct Pokémon have Abilities whose card text requires other named Pokémon in play, how much Bench capacity is needed to make **both named conditions true at the same time**?

The answer depends on the union of their actual required species, including the two sources. Requirements that overlap can share the same physical Pokémon. Explicit `on your Bench` requirements constrain which species may occupy the sole Active Spot.

This result adds `tools/bench_joint_named_guard_capacity.py`, building on the source- and print-aware guard compiler in [bench_named_ability_dependencies/](../bench_named_ability_dependencies/).

## Exact placement model

Given a set of selected named-Ability guards:

1. Collect all required source names and explicitly named prerequisites.
2. Let `N` be the cardinality of this union.
3. Collect `F`, the subset that must specifically be **on the Bench**, according to the guard's wording.
4. If a required name exists outside `F`, it can occupy the Active Spot, yielding a minimum of `N-1` Bench occupants.
5. If every required name belongs to `F`, none can be Active, so all `N` required names must occupy the Bench; another eligible Active Pokémon is needed.

This provides a **necessary Bench-capacity lower bound** for the named conditions under ordinary card-name interpretation. It is not a guarantee that both Abilities can actually be used, that their Energy costs are satisfied, or that their sources remain enabled.

For multiple guards with the same source species, the current tool requires at least one common legal print carrying all chosen source guards. If no such print exists, it rejects the merged single-source representation rather than falsely assuming one Pokémon can use Abilities printed on separate copies. An instance-aware model could later allow multiple same-species sources at additional slot cost.

## Concrete dependency unions

### Regigigas Ancient Wisdom + Lunatone Lunar Cycle

Regigigas `swsh10-130` requires Regirock, Regice, Registeel, Regieleki, and Regidrago in play. Its six-name required set includes Regigigas.

Lunatone `me1-74` has Lunar Cycle, which requires Solrock in play. Those two names are absent from the Regigigas six-name set.

The simultaneous union is **eight distinct Pokémon names**. Since one can occupy the Active Spot, the minimum physical Bench is **seven**.

- Normal five-slot Bench: structurally impossible to satisfy both named guards.
- Sky Field eight-slot Bench: the required number of slots can exist; other Ability constraints remain to be checked.
- If Lunatone's partner Solrock has a relevant reciprocal Ability requiring Lunatone, adding that reciprocal guard does **not** raise the seven-slot bound because the two names are already present.

### Two reciprocal conditional Abilities

For the selected Lunatone and Solrock variants, each requires the other. Their combined required set contains only those two Pokémon names, so one may be Active and the other Benched. The geometric minimum is one Bench slot.

### Mandatory Bench positioning

If an Ability source `A` requires `B` on the Bench and `B` requires `A` on the Bench, each required name is forced onto the Bench. Both sources must occupy the Bench simultaneously, so the minimum Bench occupancy is two even though only two named species are involved. Another Pokémon must occupy the Active Spot. This is an abstract grammar witness with no claim that such a reciprocal pair currently exists in the catalog.

## Complete conservative-catalog pairwise census

The bundled paper Expanded card pool yields 25 recognized named-guard text variants. Among variant pairs whose source species differ, there are **293** combinations.

| Minimum Bench occupants required | Number of distinct-source guard-variant pairs |
| ---: | ---: |
| 1 | 6 |
| 2 | 8 |
| 3 | 108 |
| 4 | 126 |
| 5 | 22 |
| 7 | 15 |
| 8 | 8 |
| **Total** | **293** |

Exactly **23 of the 293** pairings require more than the normal five Bench slots. All 23 can fit within eight Bench slots by this limited geometric criterion. This is a text-variant count over a conservative parser output; it is **not** the prevalence of decks using those combinations, a deck-building recommendation, or a count of all possible Pokémon Ability interactions.

The eight maximum-occupancy pairs combine Ancient Wisdom's six named Regi requirements with some independent three-species conditional families, such as Uxie/Mesprit/Azelf or the monkey and bird trios. Their simultaneous named requirements can approach the full nine-Pokémon board permitted by an eight-slot expansion plus one Active.

## Verification

Run `python tools/bench_joint_named_guard_capacity.py --self-test`. Six regressions verify:

- Regigigas plus Lunatone needs seven Bench slots;
- reciprocal Lunatone/Solrock conditions share the same two species;
- adding a third guard with already-present requirements does not duplicate its species;
- explicitly required Bench placements eliminate Active candidates when appropriate;
- incompatible source prints are rejected;
- the exact 293-pair histogram and 23 five-slot-obstructed combinations.

Running the file without flags prints an auditable histogram and twelve maximal-capacity examples.

[GitHub Actions run 37921004470](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37921004470) passed the pinned-card-corpus tests.

## Implications

An associativity graph that regards individually accessible support Abilities as jointly available can miss **geometric union costs**. Two individually feasible engines may require more simultaneous occupied positions than a five-slot Bench permits, even before paying Energy and Supporter costs.

The opposite can also occur: overlapping named prerequisites let two Abilities share material. The correct minimal capacity depends on the **union** of required Pokémon and their location constraints.

An optimizer should therefore compile sets of intended concurrent abilities into a position-aware prerequisite structure and test its total occupancy, beyond scoring their individual values.

## Limitations

The parser does not cover every Ability guard grammar; the census is conservative. The placement model assumes a name identifies one distinct necessary Pokémon and does not yet account for effects that rename Pokémon, force an Active-only source, or require multiple copies of the same species. It also assumes that the examined guards are meant to be satisfied simultaneously, which may be unnecessary if effects can be used sequentially, followed by Bench cleanup or capacity changes.

An actionable next direction is to compare joint occupancy to a timed schedule where one conditional Ability is used, a supporter is removed, and a second group is established. Such lines may evade a simultaneous lower bound at the price of scarce removal actions and setup time.
