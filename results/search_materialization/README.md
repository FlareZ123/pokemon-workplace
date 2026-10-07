# Typed search materialization

## Question

Can a successful typed Trainer deck-search allocation become a concrete physical state transition without reusing or inventing target copies?

Implementation: `tools/search_materialization.py`  
Regression: `results/search_materialization/reproduce.py`

## Result

The adapter binds every typed `TargetGroup` to one explicit exchangeable card class in the identity ledger.

Before execution, it requires the typed target capacity to equal the corresponding exchangeable deck count. This prevents a feasibility model and the physical state from carrying contradictory target inventories.

The regression compiles Rosa's actual search profile and uses the typed allocator to satisfy one Basic Pokémon, one Item, and one Basic Energy demand with Bagon, Quick Ball, and Basic Fire Energy.

The selected target-cost vector is then executed:

- one unit leaves each exchangeable deck class;
- one physical instance ID is allocated for each selected copy;
- each instance moves to hand;
- total counts remain conserved.

The target classes use the namespaced `deck_name` relation in this demonstration. A simulator can instead bind targets to conservative gameplay variants or resolved official reprint classes when that equivalence is the appropriate search pool.

## Boundary

Typed search feasibility works at grouped capacity. Physical identity is allocated only when the selected copy leaves that exchangeable pool.

The allocator's diagnostic resource names are never used as physical IDs.

## Scope

This adapter executes a supplied target-cost vector. It does not choose among several equally feasible target-cost actions, resolve hidden deck order, pay the Trainer card's other costs, or move the played Trainer itself to discard. Those are planner/action-state concerns around this identity transition.
