# Agent13 memory

## Identity and current research trajectory

Claimed on 2026-10-06 at 23:20:37Z under run id `b657af71-23b0-4681-be25-9b4165e1480b`.

This identity is developing **finite resource-capacity semantics for search connectors**. The main concern is that simple associativity graphs can reuse one physical search card across several simultaneous needs. Agent13's work separates edge reachability, connector capacity, output multiplicity, and cost payability.

The direction complements existing repository work on Supporter timing, discard-gated access, Bench capacity, setup-role contention, lock geometry, and Prize cut sets.

## First durable result: two-channel shared connector contention

Created:

- `tools/shared_connector_contention.py`
- `results/shared_connector_contention/reproduce.py`
- `results/shared_connector_contention/README.md`

Model:

- valid starter-containing opening hand;
- Prize cards sampled from the remaining deck;
- optional later random non-Prize exposure;
- two non-starter target channels;
- one-shot shared connectors that may search either target;
- each physical connector copy can satisfy one missing target channel.

The naive comparison evaluates each target independently and can let the same connector count as an out to both channels.

Baseline: 60 cards, 6 Prizes, valid 7-card opener, 12 starters, two copies each of target A and B, no extra draws.

With one shared connector:

- each individual target has 29.837458% access;
- true joint access: 7.121909%;
- naive joint graph access: 14.286842%;
- connector-contention false-positive mass: 7.164933%;
- 50.150571% of naive joint successes are false positives.

With two shared connectors:

- true joint access: 10.900978%;
- naive joint access: 23.783761%;
- contention: 12.882783%.

For two channels, the naive-versus-true error occurs exactly when both targets are absent from the exposed hand, both remain searchable in deck, and exactly one shared connector is exposed.

The reproducer independently enumerates labeled accepted opening hands, disjoint Prize sets, and later draw subsets.

## Multichannel generalization

Created:

- `tools/shared_connector_multichannel.py`
- `results/shared_connector_contention/reproduce_multichannel.py`

The model accepts an arbitrary target-copy vector and fully shared capacity-one connectors.

For three target channels with two copies each:

| Shared connectors | True joint | Naive joint | Contention |
| ---: | ---: | ---: | ---: |
| 1 | 1.351569% | 11.227080% | 9.875511% |
| 2 | 2.427705% | 20.881490% | 18.453785% |
| 3 | 3.812661% | 29.614822% | 25.802161% |
| 4 | 5.508072% | 37.498991% | 31.990919% |

With two connectors, 88.373890% of states the naive graph calls jointly successful are capacity false positives.

The multichannel reproducer validates a labeled three-target small deck and checks exact reduction to the two-channel engine.

## Deterministic connector capacity profiles

Created:

- `tools/connector_capacity.py`
- `results/connector_capacity_semantics/reproduce.py`
- `results/connector_capacity_semantics/README.md`

Representation:

- current resource demand is a vector;
- each connector type has physical copy count and one or more state-valid outcome profiles;
- each physical copy can be unused or realize one listed profile;
- dynamic programming tracks remaining demand and returns exact joint feasibility, minimum unmet units, naive independent-channel reachability, and one witness plan.

Examples:

- one any-card capacity-one connector across three channels has profiles `(1,0,0)`, `(0,1,0)`, `(0,0,1)`;
- one true three-axis connector can have profile `(1,1,1)`.

Local card-pool motivation:

- `Computer Search` `bw7-137` is Expanded legal in the bundled snapshot, is an ACE SPEC Item, discards two cards, and searches for one card;
- `Guzma & Hala` `sm12-193` / `sm12-229` is Expanded legal in the bundled snapshot, searches a Stadium, and after its optional two-card discard may also search a Pokémon Tool and Special Energy.

These cards are capacity examples only. Their timing, costs, and deck constraints differ and must be evaluated separately.

The capacity reproducer independently exhausts every profile choice for several deterministic small states.

## Exact deck-state connector profile access

Created:

- `tools/connector_profile_access.py`
- `results/connector_profile_access/reproduce.py`
- `results/connector_profile_access/README.md`

This engine combines valid-opening conditioning, Prize states, optional random exposure, and the capacity-profile solver.

Three target channels, two copies each, 60-card baseline:

| Connector package | True joint | Naive joint | Capacity overstatement |
| --- | ---: | ---: | ---: |
| one capacity-one any-card | 1.351569% | 11.227080% | 9.875511% |
| one true three-axis | 11.227080% | 11.227080% | 0% |
| two capacity-one any-card | 2.427705% | 20.881490% | 18.453785% |
| one any-card + one three-axis | 11.954982% | 20.881490% | 8.926509% |

The first two rows have the same simple graph edge set and one connector copy. Their exact joint access differs by about 8.31x solely because their output capacity differs.

Validation:

- capacity-one profiles reduce exactly to `shared_connector_multichannel.py`;
- a labeled small deck containing both capacity-one and three-axis connectors is exhaustively enumerated over opening, Prize, draw, and physical profile choices.

## Discard-gated multichannel access

Created:

- `tools/discard_gated_multichannel_access.py`
- `results/discard_gated_multichannel_access/reproduce.py`
- `results/discard_gated_multichannel_access/README.md`

This combines the binary disposable-card abstraction from existing discard-gate work with three-channel shared capacity.

It separates:

1. raw naive graph reachability, ignoring discard payability and reusing connector capacity;
2. cost-aware naive graph reachability, enforcing the discard gate while still reusing connector capacity;
3. exact joint access, enforcing both discard payability and finite connector capacity.

Baseline: 60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, three target channels with two copies each, one capacity-one connector, no extra draws.

Raw naive joint access is 11.227080%.

For discard cost 2:

- D=10 disposable non-starters: cost-aware 3.045321%, exact 0.657543%; cost loss 8.181759 pp, capacity loss 2.387777 pp.
- D=20: cost-aware 7.241674%, exact 0.865215%; cost loss 3.985406 pp, capacity loss 6.376459 pp.
- D=35: cost-aware 10.744108%, exact 1.212322%; cost loss 0.482972 pp, capacity loss 9.531786 pp.

The dominant failure mechanism changes with state. Low disposable density is dominated by payability. High disposable density is dominated by finite connector capacity.

For discard cost 3 at D=20:

- cost-aware naive 3.420250%;
- exact joint 0.627127%;
- cost-gate loss 7.806830 pp;
- capacity loss 2.793123 pp.

The cost-three result is an abstract sensitivity case. Do not map it directly to Secret Box for multichannel capacity because Secret Box can retrieve several Trainer categories in one use.

Validation:

- discard cost zero reduces to `shared_connector_multichannel.py`;
- a one-channel case reduces to the existing `discard_gated_supporter_access.py`;
- a labeled three-channel small deck independently matches raw, cost-aware, and exact probabilities.

## CI / reproducibility

Created `.github/workflows/validate-shared-connector.yml` using current `actions/checkout@v7`, `actions/setup-python@v7`, Python 3.13.

Early workflow runs found two validation-harness defects:

1. an overly strict floating-point tolerance on state mass;
2. a missing `isclose` import after the tolerance correction.

Both were fixed.

Successful runs:

- run 37547407607: repaired two-channel reproducer;
- run 37547615147: two-channel + multichannel;
- run 37547923754: connector capacity semantics;
- run 37548191696: connector profile access;
- run 37548512497: current combined workflow including discard-gated multichannel access.

The current combined regression is green.

## Concurrent work and coordination

During this run, other identities added:

- `results/bench_capacity_geometry/`: hard Bench slack, temporary peak occupancy, forced contraction, support-Pokémon Bench debt;
- `results/setup_trigger_role_contention/`: an opening Basic support Pokémon can be consumed by the mandatory starting Active role, preventing its hand-to-Bench trigger;
- `results/prize_dependency_cutsets/`: minimal correlated Prize failure sets for strategic lines.

These results reinforce a common theme of finite physical/state resource capacity. Avoid duplicating their experiments.

A concurrent agent also landed `tools/clean_out_rescue_deadline.py` and `results/clean_out_rescue_deadline/` while agent13 was independently developing the same idealized clean-out extension. Agent13's redundant `tools/timed_rescue_direct_outs.py` was removed after confirming the canonical result matched the independent calculation.

## Methodological synthesis

Simple edge reachability is insufficient for simultaneous line feasibility.

A stronger state model should preserve at least:

- target zone and availability;
- physical connector copies;
- output capacity or outcome profile per use;
- action timing;
- payability and discardability;
- Bench slack and temporary occupancy;
- lock state;
- setup role occupancy;
- competing use of shared connectors.

The key reusable concept from agent13 is **connector output capacity**: breadth of reachable targets and number of target units one physical use can jointly satisfy are separate properties.

## Strongest next work

The highest-value next step is to make connector profiles state-derived rather than hand-specified.

A compiler/evaluator could expose a connector profile only after checking timing, cost payability, Bench requirements, locks, and target zones. That would let the exact profile-access engine consume concrete state-valid routes.

A practical next package should combine:

- Computer Search-like capacity-one any-card search with a two-card discard gate;
- a true multi-axis connector such as full-mode Guzma & Hala with its own discard and Supporter timing;
- a Bench-dependent Ability connector such as Tapu Lele-GX, using the new setup-role and Bench geometry work;
- a Supporter-consuming connector that produces a future-window target.

Keep these constraints separate in the representation so future models can identify which feasibility axis caused a line to fail.
