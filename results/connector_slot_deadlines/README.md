# Typed output slots and deadlines combine into hard connector constraints

## Question

`connector_slot_collision_option/` shows that typed output slots can reduce a connector's effective capacity below its printed output count. `connector_capacity_deadlines/` shows that early target deadlines can force a connector to commit before future information arrives.

What happens when those constraints occur together?

This result gives every target both an output-slot eligibility set and its own deadline. It exposes a failure mode that neither scalar capacity nor deadlines alone can represent: several urgent targets may fit the connector's nominal output count while being impossible because they compete for the same typed output slot.

Implementation: `tools/connector_slot_deadlines.py`  
Independent regression: `results/connector_slot_deadlines/reproduce.py`

## Canonical state

Use a Secret Box-shaped connector with physical output slots:

`Item, Tool, Supporter, Stadium`

The four missing target channels require:

`Item, Tool, Tool, Supporter`

Every target has two copies in a 40-card remaining deck. One natural draw is available when deadlines allow it.

The connector has four printed output categories but immediate matching size three because the two Tool-only targets compete for one Tool slot.

## Deadline cases

| Target deadlines | Exact success | Interpretation |
| --- | ---: | --- |
| all four allow one draw | **10.000000%** | wait for either Tool target, then search the other three needs |
| Item due now | **5.405405%** | Item urgency forces connector use now; one Tool remains for the draw |
| one Tool due now | **5.405405%** | urgent Tool must consume the Tool slot now; the other Tool remains for the draw |
| both Tool targets due now | **0%** | one Tool output cannot satisfy two simultaneous urgent Tool demands |
| all four due now | **0%** | the Tool collision prevents a complete current-window assignment |

A single urgent target forces the connector to commit before the natural draw. Two urgent targets that collide on the Tool slot create a hard failure.

## Scalar capacity gives the wrong answer in the urgent collision

A scalar model sees four missing channels, nominal connector capacity four, and four current-window deadlines. That representation declares the state immediately solvable.

The typed model has no injective target-to-slot assignment covering both Tool targets. Exact current-window success is zero.

Replacing the second Tool target with a Stadium target restores four distinct slot assignments and immediate success becomes 100%.

## Urgent matching capacity

The relevant deadline resource is the maximum matching size among targets that must be satisfied before more information or actions can arrive.

If the current deadline-zero demand set cannot be embedded into distinct physical output slots, waiting is illegal and the line fails immediately under the one-connector model.

Later deck access cannot repair an assignment that was already required before the next draw.

## Relation to the preceding results

The repository now has nested finite-horizon abstractions:

1. `connector_capacity_option_value/` models interchangeable output capacity;
2. `connector_slot_collision_option/` replaces interchangeable capacity with typed physical output slots;
3. `connector_slot_deadlines/` adds per-target expiry windows to those slots.

`connector_capacity_deadlines/` remains useful when outputs truly are interchangeable. The typed deadline model is needed when card text gives category-specific outputs such as Item, Tool, Supporter, Stadium, Special Energy, or other restricted search classes.

## Validation

The dynamic program preserves target-copy counts, secured channels, deadlines, filler count, connector availability, and exact typed output-slot matching.

A separate labeled-card enumerator independently tries explicit permutations of target channels onto connector slots. It reproduces all five deadline cases above.

The regression also compares two all-urgent four-target states:

- distinct Item / Tool / Supporter / Stadium demands: success 100%;
- Item / Tool / Tool / Supporter demands: success 0%.

Only the target-to-slot geometry changes.

## Limits

The model begins with the connector already in hand and does not include discard payment, Prize zones, Supporter quota, or downstream execution after search.

Deadlines refer to target acquisition. A concrete ALS may need a searched Tool attached, a Stadium played, a Supporter still legal to use, or an evolution completed before its true strategic deadline.

The one-connector assumption is deliberate. Additional connectors can repair some slot collisions and would need their own physical action and resource budgets.

## Next useful work

Compile slot eligibility and deadline demand from a real multi-axis line. Secret Box is an obvious candidate, but the concrete model should distinguish direct payloads from outputs that are themselves connectors. An upstream Supporter output can change the downstream demand graph rather than simply satisfying one terminal slot.
