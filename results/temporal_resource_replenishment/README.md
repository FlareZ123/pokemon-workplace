# Temporal connector resources: ordered consumption and replenishment

## Question

The static resource-constrained connector solver prevents two routes from spending the same finite resource twice.

Is that enough when an earlier action can create resource stock that a later action consumes?

No.

A sequence planner must update the resource state between actions.

Implementation: `tools/temporal_resource_connectors.py`  
Regression: `results/temporal_resource_replenishment/reproduce.py`

## Minimal counterexample

Consider two target channels and one abstract discardable-card resource.

Starting stock:

`3`

Two one-copy actions:

| Action | Target output | Cost | Resource production |
| --- | --- | ---: | ---: |
| Secret Box-like | channel A | 3 | 2 |
| Guzma & Hala-like | channel B | 2 | 0 |

A static sum sees total cost `3 + 2 = 5` and can reject the pair against starting stock 3.

The legal temporal witness is:

`3 -> pay 3 -> 0 -> produce 2 -> pay 2 -> 0`

Both targets are supplied.

The reverse order fails:

`3 -> pay 2 -> 1`

The Box-like action can no longer pay its cost 3.

Action order and resource production therefore change feasibility.

## Exact solver

Each action profile has three vectors:

- `output`: strategic target units supplied;
- `cost`: resource units that must exist before the action;
- `production`: resource units added after the action pays its cost.

The solver keeps:

- remaining physical connector-copy counts;
- remaining target demand;
- current resource stock.

It exhaustively searches action order with memoization.

A profile is legal only when its cost fits the current pre-action resource state. The transition is:

`next_resource = current_resource - cost + production`

Each physical connector copy can be used at most once.

## Regressions

The reproducer checks four properties.

First, starting stock 3 with Box-like production 2 is feasible. The returned witness is exactly:

`Secret Box-like -> Guzma & Hala-like`

Second, reducing Box-like production from 2 to 1 makes starting stock 3 insufficient. One target unit remains unmet.

Third, the same low-production pair becomes feasible from starting stock 4.

Fourth, an action with zero strategic target output is allowed when it produces a resource required by a later consumer. This represents setup actions whose value comes from changing state rather than directly satisfying the final demand vector.

An independent enumeration of the two possible action orders validates the main 3-stock counterexample.

## Relation to static resource allocation

`resource_constrained_connectors/` establishes the complementary constraint that shared resources cannot be double-spent.

The temporal solver adds another rule:

**shared resources cannot be assumed to only decrease.**

Both errors matter.

A planner that checks each route against the unchanged starting state can create false positives by reusing the same resource.

A planner that sums all future costs against only the starting state can create false negatives when an earlier action replenishes the resource.

The correct transition semantics are sequential.

## Concrete Pokémon anchor

`temporal_discard_replenishment/` supplies a concrete first-turn Aichi Vileplume example.

In its seeded 100,000-state regression, all 4,175 Secret-Box-only successes have a successful continuation where any later Guzma & Hala discard is paid entirely by cards generated after Secret Box resolves.

That concrete result motivates the abstract `production` field here.

The abstraction deliberately does not claim that every searched card is strategically disposable. A state-aware discard policy must decide which generated cards qualify as usable production.

## Representation consequence

Connector action profiles can use integer resource dimensions for quantities such as:

- currently acceptable discard fodder;
- temporary hand material;
- another replenishable action-local capacity.

For strategic modeling, `production` should represent resource units that genuinely become usable after the action under the current policy.

For discardability in particular, this means the production count can depend on exact retrieved card identities, retention needs, matchup state, Prize information, and the intended continuation.

## Limits

This solver uses abstract integer resources.

It does not identify the exact physical cards consumed or produced, enforce Trainer resolving zones, model hidden information, or derive state-dependent DCI values.

Those details belong in the exact transaction and zone-state layers.

The solver is useful as a planning projection when action profiles have already been compiled from a mechanically valid state.

## Next useful work

A stronger composition would emit temporal profiles directly from exact Trainer transactions.

That bridge could:

1. execute a legal search action;
2. observe the resulting exact hand;
3. derive the next discard witness or resource projection;
4. continue through the action sequence while preserving physical card identities.

This would connect resource planning to the repository's canonical zone-state execution without forcing the planner to enumerate every physical card choice prematurely.
