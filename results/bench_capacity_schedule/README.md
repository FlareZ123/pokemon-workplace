# Typed Bench-capacity scheduling: release timing changes support-chain feasibility

## Question

Suppose a deck wants to use several transactional Bench-entry support Pokémon while a persistent core board already occupies most of the Bench. How many support activations can actually fit before a deadline when release actions consume different timing windows?

This result turns Bench occupancy into persistent state and distinguishes release by Item, Ability, Supporter, and attack timing.

Implementation: `tools/bench_capacity_schedule.py`  
Reproducer: `results/bench_capacity_schedule/reproduce.py`

## State model

The Bench has capacity five. A caller specifies persistent core Bench slots. Each support activation requires one free slot and leaves a resident support until an explicit release removes one.

The kernel accepts finite release budgets in four abstract action classes. Item and already-realistic Ability release can recycle a slot in the same turn. Supporter release is limited to one ordinary Supporter window each turn. Attack release frees a support and immediately ends the current turn, so the slot cannot enable another support activation until a later turn.

Release actions are generic resources. Card-specific targeting, access, costs, locks, and stochastic branches must be established before a release unit is supplied.

## Four-slot core example

With four persistent core Pokémon on the Bench, one transactional slot remains. Ask whether three support activations can be completed by a deadline.

| Release resources | By turn 1 | By turn 2 | By turn 3 |
| --- | ---: | ---: | ---: |
| none | 1 | 1 | 1 |
| 2 Item releases | 3 | 3 | 3 |
| 2 Ability releases | 3 | 3 | 3 |
| 2 Supporter releases | 2 | 3 | 3 |
| 2 attack releases | 1 | 2 | 3 |

An Item-like or already-realistic Ability release can free the transactional slot and allow another support Pokémon to enter during the same turn. Two such releases can chain three support activations through one physical slot on turn one.

A Supporter release can also free the slot before the turn ends, while one ordinary Supporter window limits recycling to once per turn.

An attack release is slower in a different way. Cleanup itself ends the turn. Even though the slot becomes empty, another support cannot use it until the next turn.

## Closed-form checks

Let `C` be Bench capacity, `R` persistent core occupancy, `q = C - R` initial transactional capacity with `q > 0`, `B` available release uses in one action class, and `T` the deadline in turns.

For arbitrarily large support demand, the single-class maxima are:

- Item release: `q + B`;
- Ability release: `q + B`;
- Supporter release: `q + min(B, T)`;
- attack release: `q + min(B, T - 1)`.

The reproducer checks the BFS against these identities across core occupancies, deadlines, and release budgets.

The attack formula captures the turn-ending boundary directly. An attack release used on the deadline turn frees a slot too late for another support activation within that deadline.

## Mixed action classes

The scheduler also handles mixed release budgets without collapsing them into one count.

With a four-slot core board, a two-turn deadline, one Item release, one Supporter release, and two attack releases, the maximum is four support activations. Simply summing four release resources would predict room for five. The second attack release cannot increase activation count by the turn-two deadline because it would end that final turn after freeing the slot.

Equal-looking “free one Bench slot” edges therefore have different temporal capacity.

## Relation to the release census

`bench_release_catalog/` found 20 legal Expanded card names in conservative explicit Bench-release wording families. Eight are Supporters and eight are attacks. The timing classes that dominate the actual release catalog are exactly the classes where a generic capacity count is most misleading.

The other four names also preserve card-specific restrictions: Super Scoop Up is stochastic, Scoop Up Cyclone is an ACE SPEC, Corviknight requires an evolution trigger, and Hydreigon performs a coarse discard-down effect.

## Strategic interpretation

Bench slots have residency. A support Pokémon keeps its slot until a real state transition removes it.

Release actions also have temporal capacity. A Supporter pickup and an attack pickup can both remove one resident Pokémon, while their downstream timing differs because the latter ends the turn.

Core-board demand changes connector realism. Once four slots are committed to a core board, each persistent support becomes a scarce-capacity claim. A later support connector can be accessible while being unusable before its intended deadline.

## Validation

The implementation performs exact BFS over turn number, activated support count, resident support count, remaining release resources, and current-turn Supporter usage.

The reproducer validates the state search against the closed-form maxima for core occupancies zero through four, deadlines one through four turns, and release budgets zero through four. It also checks a mixed-resource example.

## Limits

This is a scheduling kernel rather than a full game simulator. It holds core Bench occupancy constant. Each supplied Item or Ability release budget unit is assumed usable once, so caller-side card semantics remain necessary.

The kernel omits Prize cards, draws, search, discard costs, retreat or switching needed to make a cleanup attacker Active, Energy requirements, opponent interaction, Bench-size-changing Stadiums, and support Pokémon that become part of the final core board.

## Next useful work

The next integration should combine this scheduler with probabilistic access. A state should first determine whether support Pokémon and release cards are accessible and legal, then pass only realistic release budgets into the occupancy scheduler.

A useful target is a four-core-slot line using two or three transactional supports. The model can compare completion probability by turn one, two, or three under Item, Supporter, and attack release packages while preserving Prize placement, setup-role contention, and correct hand-to-Bench semantics.
