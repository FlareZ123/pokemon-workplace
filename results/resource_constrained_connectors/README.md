# Resource-constrained connectors: shared costs can contend after each route is individually legal

## Question

Suppose two search routes are individually legal from the same state. Can the pair still be impossible because both routes consume the same finite state resource?

Yes.

This result generalizes connector output capacity by adding shared resource costs.

Implementation: `tools/resource_constrained_connectors.py`

Brute-force validation: `results/resource_constrained_connectors/reproduce.py`

## Representation

A state supplies:

- a target-demand vector;
- a vector of finite resource capacities;
- connector types with physical copy counts;
- one or more action profiles per connector type.

Each action profile has:

- an output vector describing target units supplied;
- a cost vector describing state resources consumed.

A physical connector copy may stay unused or realize one profile.

The dynamic program jointly allocates connector copies and shared resources.

Potential resource dimensions include:

- discardable cards;
- remaining Supporter plays in the current window;
- current Bench slack for routes whose relevant occupancy does not change during the line;
- once-per-game or once-per-turn budgets when represented as integer capacities.

Changing board geometry and temporal transitions still require the repository's state-transition and Bench-prefix models.

## Three levels of feasibility

The solver reports three increasingly realistic views.

### Raw naive reachability

Every demanded target channel is checked for at least one connector edge.

Profile costs are ignored.

### Individually cost-feasible reachability

Every demanded channel must have at least one connector profile whose cost fits the full starting resource pool.

Targets are still checked independently. The same connector copy and the same resource units can therefore be reused across several target checks.

### Exact joint feasibility

Physical connector copies and resource capacities are allocated once across the whole demand vector.

This catches shared-resource contention that remains invisible after each route has passed an isolated cost check.

## Example 1: discard pool contention

Demand:

`(1,1)`

State resource:

- 3 disposable cards.

Available connector:

- two physical broad-search copies;
- either target can be searched;
- each use costs 2 disposable cards.

Each target route is individually payable because 2 is no more than the available pool of 3.

The pair requires 4 disposable cards.

Result:

- raw naive joint reachable: yes;
- individually cost-feasible joint: yes;
- exact joint feasible: no;
- minimum unmet target units: 1.

This is a stronger version of discard-gate realism. Evaluating each connector against the original hand can double-spend the same discard fodder.

## Example 2: Supporter-window contention

Demand:

`(1,1)`

State resource:

- 1 remaining Supporter play.

Available connectors:

- one Supporter route that satisfies target A and consumes 1 Supporter play;
- one Supporter route that satisfies target B and consumes 1 Supporter play.

Each route fits the current Supporter budget in isolation.

Together they require two Supporter plays.

Result:

- raw naive joint reachable: yes;
- individually cost-feasible joint: yes;
- exact joint feasible: no.

This is a static resource view of Supporter contention for same-window actions.

Temporal routes such as Skyla finding a future Supporter still need the typed transition model because the usefulness of the output crosses an action window.

## Example 3: a multi-axis action can dominate the shared budget

Use the same two-target demand and one remaining Supporter play.

Available connector:

- one action with output `(1,1)`;
- cost: 1 Supporter play.

Result:

- exact joint feasible: yes.

One multi-axis action satisfies both target channels inside the same action budget.

This formalizes part of the strategic value of Supporters that retrieve several different resource categories in one use.

## Relation to discard-gated multichannel access

`results/discard_gated_multichannel_access/` computes a probabilistic special case where identical capacity-one connectors share a disposable-card pool.

The current solver is the deterministic inner generalization.

It can represent heterogeneous connector costs and several independent resource dimensions.

## Relation to Bench geometry

Bench slack can be represented as a static capacity when every modeled action only consumes a slot and the capacity stays fixed.

The Bench geometry result shows why this is insufficient for lines with temporary occupancy changes.

For a sequence with additions and removals, the peak prefix occupancy must remain under the active Bench cap. A future integration should ask the Bench model whether a candidate route is legal, then expose only the resulting state-valid action profile to this allocation solver.

## Relation to setup-role contention

The setup-role result shows that one physical Basic Pokémon copy can be consumed by the starting Active role and therefore cannot remain in hand for a later hand-to-Bench trigger.

That is another finite-role allocation problem.

The current planner focuses on connector actions after a state has been formed. A broader state compiler can apply the same capacity principle to setup roles before connector allocation begins.

## Validation

The reproducer independently enumerates every profile choice for every physical connector copy.

Regression cases include:

- two broad searches sharing a three-card discard pool;
- the same searches with enough discardable cards;
- two current-window Supporter routes sharing one Supporter play;
- one multi-axis Supporter action;
- a mixed multi-resource case.

A zero-resource-cost regression also reduces to the earlier `connector_capacity.py` solver.

## Methodological implication

Checking every edge or route against the same unmodified game state can create false joint feasibility.

Once one route consumes a shared resource, the remaining routes must see the reduced capacity.

This applies to connector copies, discardable cards, Supporter windows, Bench slack, and other finite state budgets.

A realistic line evaluator therefore needs allocation semantics in addition to local route legality.

## Next useful work

The next step is to place this allocator behind the typed access network.

The typed engine can determine which actions are currently legal under zones, locks, action timing, and Bench position.

Each legal route can then emit:

- target outputs;
- shared resource costs;
- connector identity and copy count.

The allocator can test whether several required channels can be realized together without reusing the same physical card or state resource.
