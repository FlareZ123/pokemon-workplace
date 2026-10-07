# Apex Dragon burden with Double Dragon Energy

## Question

How much does Double Dragon Energy change effect-side discard burden when Regidrago VSTAR copies Dragon attacks with Apex Dragon?

This compares two exact attachment states that each provide enough Energy for Apex Dragon:

1. two Basic Grass Energy plus one Basic Fire Energy;
2. one active Double Dragon Energy plus one Basic Fire Energy.

The comparison measures the minimum number of physical Energy cards needed to achieve the largest applicable discard for each supported copied attack instruction.

## Rules basis

Three rulebook principles interact here.

First, a copied attack normally uses the selected attack's effects and damage without requiring its printed attack cost.

Second, one Energy card can provide several Energy units. The Ignition Energy ruling explicitly says one card providing three Energy can satisfy a discard-three requirement.

Third, an Energy that provides every type cannot be treated as lacking a relevant type. The rulebook's Crimson Blaster example says an every-type Energy must be discarded by an all-Fire-Energy instruction.

Double Dragon Energy's card text says that, while attached to a Dragon Pokémon, it provides every type of Energy and two Energy at a time.

A historical 2015 PokéBeach ruling discussion about Kingdra and Double Dragon Energy also states that one DDE can fulfill a Water plus Lightning discard requirement. This is secondary corroboration rather than the primary rules source.

## Result

`tools/apex_dragon_special_energy_burden.py` applies the reusable subset solver in `tools/energy_discard_solver.py` to the 35 deterministic Dragon self-discard signatures identified by the earlier Apex Dragon result.

### Minimum physical-card burden

| Minimum Energy cards discarded | Basic Grass/Grass/Fire | Double Dragon Energy + Fire |
| --- | ---: | ---: |
| 0 | 5 | 0 |
| 1 | 11 | 23 |
| 2 | 7 | 12 |
| 3 | 12 | 0 |

Across the 35 signatures, **27** change either the minimum physical-card burden or the amount of the typed requirement that can be fulfilled.

The Special Energy state compresses every deterministic discard into one or two physical cards because only two Energy cards are attached. At the same time, DDE's every-type property activates typed discard requirements that were impossible in the Basic-only state.

## The zero-burden reversal

All five signatures that discarded zero cards in the Basic Grass/Grass/Fire state become one-card DDE discards in the DDE plus Fire state:

- Hydreigon, **Dragonblast**, discard 2 Darkness Energy;
- Zygarde, **Core Enforcer**, discard Darkness plus Fairy;
- Kingdra, **Dragon Blast**, discard Water plus Lightning, represented by two text signatures;
- Ultra Necrozma-GX, **Photon Geyser**, discard all basic Psychic Energy.

The first four exact signatures have independent fixed output in the Basic-only analysis. Their typed discard instruction fails against Grass/Grass/Fire and the rest of the attack can still resolve.

Once DDE is attached, the same instruction sees a valid provider of those types. DDE supplies two Energy units and every type, so the modeled minimum-card discard becomes the DDE card itself.

Photon Geyser has different output semantics because its bonus scales with cards discarded in this way. It remains in the burden comparison while retaining that quantity-coupled flag from the earlier catalog.

## Generic discard compression

Seven signatures require a generic two-Energy discard. In the Basic-only state, the minimum physical-card burden is two Basic Energy cards. In the DDE state, one DDE card can provide the required two Energy units.

Twelve signatures require three generic Energy or all attached Energy in this controlled three-unit state. Grass/Grass/Fire loses three physical cards. DDE plus Fire loses two physical cards while still losing all three provided Energy units.

This is a useful warning about metrics. Physical card loss and Energy-unit loss are different quantities.

## Strategic implication

Double Dragon Energy can make a copied endpoint cheaper in physical cards while making typed discard clauses more applicable.

A deck optimizer or simulator therefore needs the actual attached Energy-card identities before it can estimate the post-attack resource state. Counting total Energy units alone misses card recovery and attachment-card loss. Counting Energy cards alone misses how many Energy units disappear and which typed instructions become live.

This interaction also changes DCI-style evaluation. Losing one DDE card can remove two Energy units and a flexible type provider at once, which can be strategically more expensive than losing one Basic Energy despite the same physical card count.

## Solver representation

`tools/energy_discard_solver.py` models an attached Energy card with:

- a physical card identity supplied by the caller;
- an integer number of Energy units currently provided;
- the set of Energy types each provided unit can satisfy.

For typed requirements, each provided unit is treated as one capacity slot. A two-unit every-type provider can therefore satisfy two required typed units.

The solver returns the minimum number of physical cards that can achieve the maximum applicable part of a discard instruction, plus all subsets tied at that minimum card count.

This is a preservation-oriented lower bound. It does not claim that minimum physical-card loss is always the strategically best discard choice.

## Evidence classification

- The copy and partial-resolution behavior is rules-derived from the Advanced Player's Rulebook.
- The Energy-card versus Energy-unit distinction is directly rules-derived from the Ignition Energy example.
- The every-type obligation is directly rules-derived from section D-08.
- DDE's two-unit, every-type profile comes from its bundled card text.
- One DDE satisfying two differently typed units is a rules-derived implementation assumption with secondary historical ruling corroboration.
- The 35-signature comparison is computational output from the bundled snapshot.

## Limitations

The two attachment states are controlled scenarios. Real Regidrago states may include extra Energy, other Special Energy cards, cost modifiers, or effects that change Energy behavior.

The solver receives already-active provider profiles. It does not evaluate whether a conditional Special Energy effect is active.

The comparison covers the deterministic first-sentence discard grammar supported by `apex_dragon_discard_burden.py`. Choice-based Dragon Burst and Savage Wing instructions remain outside the aggregate table.

The metric minimizes physical cards discarded. A strategically optimal line may deliberately discard a different legal subset because of recovery effects, future attack requirements, Special Energy side effects, or matchup considerations.

## Reproduction

Run `results/apex_dragon_special_energy_burden/reproduce.py` from the repository root.

The historical secondary ruling used as corroboration is:

`https://www.pokebeach.com/forums/threads/kingdra-and-double-dragon-energy.123792/`
