# Exact Bench-release budget for sequential named-Ability engines

## Question

Given a first named-Pokémon engine already established and used, how many resident Pokémon must leave the Bench before the named prerequisites for another engine can be assembled under the same physical capacity?

This is the dynamic counterpart to [bench_joint_named_guard_capacity/](../bench_joint_named_guard_capacity/). A simultaneous union may require seven or eight Bench slots, while sequential effects can need fewer if the player releases expendable occupants after the first effect has resolved.

The exact mathematical model and exhaustive small-set checks are in `tools/bench_temporal_guard_release_bounds.py`.

## Assumptions and formalization

The model begins after a first guard has already been satisfied and its useful effect has resolved.

- One physical Pokémon object represents each distinct required name.
- The first named set `A` is entirely in play, with no unrelated occupants in this simplified model.
- One `a ∈ A` remains Active and cannot be discarded by Bench-only cleanup.
- A second named set `B` must be established afterward.
- Each missing member of `B` can eventually be put onto the Bench if enough slots are freed.
- Only members of `A \ (B ∪ {a})` may be discarded.
- The Bench capacity is `C`, so total Active-plus-Bench capacity is `T=C+1`.
- The first effect's already-resolved payoff remains valid after its prerequisites leave play.

The minimum number of Bench departures is

`D_min = max(0, |A ∪ B| - (C+1))`

provided:

1. the first group fits initially, `|A| <= C+1`;
2. the final group plus pinned Active fits, `|B ∪ {a}| <= C+1`;
3. the pinned Active is not required specifically on the Bench by the second guard.

If any of those conditions fails, the proposed fixed-Active release schedule is impossible. The expression follows because every removed first-group occupant frees exactly one board slot, while the second engine introduces all missing names `B \ A`. Discarding fewer than `D_min` leaves too many objects. Discarding exactly that many nonrequired Bench occupants suffices, since subsequent required Pokémon can enter one at a time.

The model also respects explicit `on your Bench` requirements from its named-Ability input, and allows a different legal Active placement in its catalog-level schedule search.

## Regigigas plus Lunatone/Solrock

For Ancient Wisdom, `A` consists of six distinct Regi species. For Lunar Cycle, `B` consists of Lunatone and Solrock. These groups are disjoint.

With Regigigas pinned Active and `C=5`:

`D_min = max(0, 8 - 6) = 2`.

Therefore **two** Benched Regi occupants must depart before both Lunatone and Solrock can be played onto the Bench. A single Expanded-legal Giovanni's Exile `sm10-174` can discard up to two undamaged Benched Pokémon, making it a plausible one-Supporter release resource when its other conditions are satisfied.

The complete physically conserving example appears in [regigigas_lunatone_temporal_multiplex/](../regigigas_lunatone_temporal_multiplex/). It executes Ancient Wisdom, uses Giovanni's Exile, and then resolves Lunar Cycle with no capacity increase.

## Three-new-species alternative

A condition requiring three new and distinct species, such as Uxie/Mesprit/Azelf, has `|A ∪ B|=9` when placed after a complete six-Regi board.

At total capacity six:

`D_min = 9 - 6 = 3`.

One two-target Giovanni's Exile can free at most two Bench slots. In the controlled model, at least one further release is needed before all three new species can enter. The player might use another type of release action, an earlier removal, or a later turn with an additional Supporter if the game and cards permit it. This formula concerns physical occupancy only.

## Conservative printed-Ability census

The previously compiled paper Expanded named-Ability catalog yields **23 different-source guard pairs** that cannot be satisfied simultaneously under a normal five-slot Bench. The exact sequential-budget census tests both possible orders and eligible Active choices, holding that Active constant during the transition.

| Minimal departures | Pairings |
| ---: | ---: |
| 2 | 15 |
| 3 | 8 |
| **Total** | **23** |

Thus **15 of the 23** can pass the geometric release requirement with one two-Pokémon Bench cleanup, if the relevant Pokémon are undamaged, the cleanup action is accessible and legal, and the first Ability effect has already been resolved. The other eight require at least three departures under this model.

None of the 23 is structurally impossible by the simplified sequential geometry when enough Bench removal is allowed. These figures count distinct source/Ability guard text variants and are conditional combinatorial classifications. They are not the frequency of tournament decks, the success probability of a particular opening, or predictions of whether a Supporter can be spared.

## Independent exact validation

An independent oracle enumerates every candidate discarded subset from the initial Bench for every combination of first and second named sets over a six-symbol alphabet, with capacities one through five. It searches for the minimum number of departures that leaves the final required names and pinned Active within the limit.

The brute-force minima agree with the closed form for all tested states, including infeasible ones.

The tests also assert:

- the concrete two-release Regigigas/Lunatone case;
- the three-release Regigigas/three-new-species case;
- rejection of an Active that the second Ability specifically requires on the Bench;
- the exact **15/8** histogram over the supplied named-guard catalog.

Run `python tools/bench_temporal_guard_release_bounds.py --self-test` or run without flags to emit an auditable catalog-wide JSON report.

[GitHub Actions run 37921884751](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37921884751) passed all five tests, including the exhaustive oracle.

## Strategic consequence

Bench access is a time-dependent resource. A conditional Ability's beneficial effect can already have been used while its source group still occupies several Bench slots. A cleanup action can then remove some of those prerequisites and enable a second Ability that requires a different Pokémon set.

Two static notions need separate optimization:

1. **Simultaneous occupancy:** how many names must remain in play together.
2. **Sequential release budget:** how many occupied slots must be released between action windows to use both groups over time.

The latter consumes actual card actions. It may compete for the sole Supporter use, require undamaged targets, or depend on Item/Ability access and opponent lock conditions.

## Limitations and next work

The model assumes each required name has one physical representative and ignores unrelated Bench occupants, duplicate names, name-changing effects, active switching, state-dependent effects already resolved, and whether the player can access new Basics. The chosen Active must remain unchanged, and conditional Abilities needing a source specifically Active require additional position validation.

An important next step is to combine the exact minimal-release lower bound with the [bench_capacity_schedule/](../bench_capacity_schedule/) timing kernel, which distinguishes Supporter, Item, Ability, and attack-based release windows. That would separate theoretically sufficient cleanup counts from actually executable same-turn or multi-turn lines.
