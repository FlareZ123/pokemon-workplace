# Batch cleanup and action windows for sequential named-Ability engines

## Question

Once a first named-Ability engine has produced its useful effect, the geometric release budget determines how many Bench slots must be freed to establish a second engine. Can those departures actually occur before the relevant turn deadline?

A count of physical release resources is insufficient because cleanup may be limited to one Supporter per turn, may remove up to **two Pokémon per card**, or may end the turn when executed by an attack.

This result adds a small exact breadth-first scheduler, `tools/bench_batch_release_schedule.py`. It integrates the pinned-Active, first-engine-executed state from [bench_temporal_guard_release_bounds/](../bench_temporal_guard_release_bounds/) with the typed action timing ideas of [bench_capacity_schedule/](../bench_capacity_schedule/).

## State and transitions

The scheduler represents:

- current turn and its remaining allowed horizon;
- Bench occupancy and capacity;
- number of first-engine Bench occupants that can now be removed without harming the second engine's required species;
- number of new second-engine Pokémon still to enter;
- remaining Item, Ability, Supporter, and attack cleanup resources;
- whether that turn's ordinary Supporter window has been spent.

The physical named set `A` of the first engine and named set `B` of the second are supplied, along with the fixed Active species, the total Bench capacity, the release-resource budget, and the target deadline in turns.

Every release resource is a hypothetical **already obtainable and usable** action. The solver does not create that action from card search connectors, and cannot guarantee it is a playable move under external Item lock, Target conditions, or other effects.

The transition classes are:

| Class | Cleanup action | Temporal limit |
| --- | --- | --- |
| Item | Remove 1 expendable Bench Pokémon | Can occur again same turn if another usable Item remains |
| Ability | Remove 1 expendable Bench Pokémon | Can occur again same turn if another independently usable Ability release remains |
| Supporter | Remove 1 up to a caller-supplied batch limit | One such Supporter per turn |
| Attack | Remove 1 expendable Bench Pokémon | Ends the current turn immediately |

The Supporter batch limit defaults to **two**, motivated by Giovanni's Exile `sm10-174`. The model also permits restricting it to one, making the effect of the second target measurable.

The program returns whether the second engine's complete named set has been entered by the deadline, the earliest achieved turn, and a concrete sequence of cleanup, turn-advance, and Bench-entry actions. Its state search is exact within this abstract action grammar.

## First-engine Regigigas, second-engine Lunatone/Solrock

With Regigigas Active and its five named partners on a full Bench, the second engine needs two new names, Lunatone and Solrock. The mathematical lower bound requires **two** first-engine Bench departures.

The scheduler finds:

| Supplied release budget | By end of turn 1 | Earliest achievable turn |
| --- | --- | --- |
| No release resource | No | None |
| One Supporter removing up to 2 | Yes | 1 |
| One Supporter removing only 1 | No | None in one-turn horizon |
| One one-target Supporter plus one usable Item release | Yes | 1 |
| One one-target Supporter plus one attack cleanup | No | 2 (if two turns allowed) |

The last row illustrates the attack boundary: freeing a slot by attacking happens too late to Bench another Pokémon during the same turn.

The exact legal-card example using Giovanni's Exile as a two-Bench release is provided in [regigigas_lunatone_temporal_multiplex/](../regigigas_lunatone_temporal_multiplex/).

## First-engine Regigigas, second-engine Uxie/Mesprit/Azelf

Three new named Pokémon require three departures, so a single two-target Supporter is insufficient.

| Supplied release budget | By end of turn 1 | Earliest achievable turn |
| --- | --- | --- |
| One two-target Supporter only | No | None in one-turn horizon |
| One two-target Supporter + one usable Item release | Yes | 1 |
| Two two-target Supporters | No | 2 (if two turns allowed) |
| Three usable Item releases | Yes | 1 |

The two-Supporter line demonstrates that the total cleanup capacity of four nominal removals does not make two Supporters playable during a single turn.

## Prior Supporter contention

If the player already used the Supporter for their first engine, one otherwise sufficient Giovanni's Exile cannot clean up the Bench in that same turn. With no alternative cleanup actions, the exact scheduler finds the second group unreachable by turn one and reachable by turn two if the Supporter is still available to play then.

This encodes a specific form of temporal connector contention. Merely counting "one Giovanni's Exile can discard two" overlooks whether its Supporter permission remains free.

## Expanded capacity

Under an eight-slot Bench expansion, the nine-name union of the six required Regis and three entirely new Pokémon can fit across one Active and eight Bench positions. The scheduler establishes the second named guard in one turn without cleanup resources, illustrating a geometric way around the release constraint.

## Tests and verification

The seven tests cover:

1. exact one-Supporter/two-target Regi→Lunar transition;
2. comparison with a one-target Supporter and Item supplement;
3. Regi→three-new-species budgets, including one-versus-two-turn Supporter limits;
4. attack cleanup ending the current turn;
5. a Supporter window already consumed before the second engine;
6. eight-slot expanded-capacity execution without cleanup;
7. structurally impossible initial state and invalid batch-size input.

Run `python tools/bench_batch_release_schedule.py --self-test`. Run without flags to print reproducible successful/failed examples and successful action traces.

[GitHub Actions run 37922201732](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37922201732) passed every test and produced the action traces.

## Interpretation and boundaries

The release-count theorem is a necessary prerequisite, while this exact search answers whether a stated budget of **typed and temporally usable release actions** can satisfy it by a particular turn.

The model assumes second-engine Pokémon are already accessible from hand and can be played one at a time. It also assumes removed first-engine occupants have no mandatory future retention value and no effects that block their removal.

The scheduler holds the Active fixed, omits opponent turns, damage, special conditions, Prize placement, search costs, and post-release return effects. A future turn in a two-turn schedule is an optimistic uninterrupted planning window, so an opponent might disrupt the plan in a real game. The built-in release effects are generic, although the two-target Supporter variant is motivated by an exact legal card.

A high-value next step is to compute **stochastic access-conditioned release budgets** for realistic decklists, rather than treating those resources as freely available. Item lock and Supporter contention should be modeled at the point each action is attempted.
