# Typed output-slot collisions create hidden connector deficiency

## Question

A multi-output Trainer can have several printed search categories while still failing to satisfy several demands at once when those demands compete for the same output slot.

How does that typed collision change the option value of preserving the connector for future information?

This result models a connector as a set of physical output slots, such as Secret Box's Item, Tool, Supporter, and Stadium searches. Each target channel declares which output slots may satisfy it. One connector use must assign searched targets injectively to those slots.

Implementation: `tools/connector_slot_collision_option.py`  
Independent regression: `results/connector_slot_collision_option/reproduce.py`

## Representation

The state contains:

- exact copies remaining for each missing target channel;
- an eligibility set for every target, such as `{Tool}` or `{Tool, Stadium}`;
- a tuple of physical connector output slots;
- filler cards;
- a finite number of natural draws;
- whether the one connector use remains available.

Before a connector action is admitted, the solver checks whether the selected target subset has an injective assignment to physical output slots.

The size of the largest such assignment is the connector's **immediate matching size** for the current demand state.

That value can be smaller than the connector's printed number of output categories.

## Canonical Secret Box-shaped example

Use four connector slots:

`Item, Tool, Supporter, Stadium`

and four missing target channels with two copies each in a 40-card remaining deck.

### Distinct demand categories

If the targets require:

`Item, Tool, Supporter, Stadium`

then all four channels match distinct slots. Immediate matching size is four, so the connector can satisfy every missing channel immediately.

Exact success is 100% with or without future draws. Preserving the connector provides no access gain under this isolated objective.

### Two Tool-only demands

Now change the target requirements to:

`Item, Tool, Tool, Supporter`

The connector still has four printed output slots, but the two Tool targets compete for one Tool slot. Immediate matching size falls to three.

A natural draw of either Tool target removes the collision. After that draw, the remaining Item, Tool, and Supporter demands fit the connector exactly.

With two copies per target and a 40-card remaining deck:

| Future draws | Adaptive preservation | Eager connector use | Waiting gain |
| ---: | ---: | ---: | ---: |
| 1 | 10.000000% | 5.405405% | **4.594595 pp** |
| 2 | 19.230769% | 10.660661% | **8.570109 pp** |
| 3 | 27.732794% | 15.765766% | **11.967028 pp** |
| 4 | 35.545464% | 20.720721% | **14.824744 pp** |

The optimal policy waits for a draw from either Tool channel before spending the connector.

The eager policy searches the Item, Supporter, and one Tool target immediately, leaving the other Tool channel to natural draws.

For `T` future draws the symmetric closed forms are:

`P(wait) = 1 - C(36,T) / C(40,T)`

`P(eager) = 1 - C(35,T) / C(37,T)`

The first formula is the chance that a natural draw hits either colliding Tool channel. The second is the chance that later draws hit the one Tool channel left unresolved after three searched copies leave the deck.

## Three Tool-only demands

If the four targets require:

`Item, Tool, Tool, Tool`

then immediate matching size is only two. The connector can cover the Item plus one Tool target.

One natural draw is insufficient because at least two of the three Tool channels must be removed from the missing-demand set before the remaining demand is matchable.

With two future draws:

- adaptive preservation succeeds **1.538462%**;
- eager use succeeds **0.568990%**.

The optimal two-draw success has the simple labeled interpretation:

- the two draws must come from two different Tool target channels;
- there are three channel pairs and `2 x 2 = 4` labeled copy pairs for each;
- favorable pairs are therefore `12` out of `C(40,2) = 780`.

Eager use searches the Item and one Tool copy first. The two remaining Tool channels must both be hit in two draws, giving `4 / C(38,2)`.

## Alternative eligibility can remove the collision

Consider:

`Item, Tool, {Tool or Stadium}, Supporter`

The flexible third target can use the Stadium output instead of competing for the Tool output.

Immediate matching size returns to four, and immediate success returns to 100%.

This shows why target categories should be represented as eligibility sets rather than one fixed label when card text permits multiple legal output classes.

## Matching deficiency as a state variable

For a current missing-target set `S`, let `mu(S)` be the largest number of targets that can be assigned to distinct connector slots.

The quantity:

`|S| - mu(S)`

is the immediate **matching deficiency** of the connector for that demand state.

A connector can have zero ordinary capacity slack by raw output count while still having positive matching deficiency because several demands collide on the same typed slot.

Natural draws can reduce that deficiency by removing a colliding target from `S`. This creates target-choice option value that a scalar output-capacity model cannot see.

The structure is the same one captured by bipartite matching and Hall-style feasibility conditions. The implementation uses exact injective target-to-slot matching directly rather than treating the printed output count as interchangeable capacity.

## Relation to prior results

This result sharpens the recent connector-capacity work:

- `connector_capacity_semantics/` established that search breadth and physical output capacity are different properties;
- `connector_capacity_option_value/` quantified waiting when unresolved demand exceeds scalar capacity;
- `connector_capacity_deadlines/` showed that an early deadline can destroy that waiting value;
- `typed_search_target_allocator/` already preserves output labels for compiled Trainer searches.

The new point is that **typed slot geometry can create hidden capacity slack even when nominal output count looks sufficient**.

For Secret Box-like effects, four output clauses do not imply four interchangeable units of capacity. Two Tool needs still consume the same one Tool output.

## Validation

The main solver uses exact memoized dynamic programming and an injective slot-assignment check for every searched target subset.

The reproducer independently enumerates labeled cards and explicit permutations of targets onto physical connector slots. It validates:

1. the distinct-category 100% immediate case;
2. every one-pair-collision row against labeled brute force and the closed forms above;
3. the three-Tool, two-draw case;
4. restoration of full capacity when one target gains alternative Stadium eligibility.

No Monte Carlo sampling is used.

## Limits

The connector is already in hand and has no payment gate in this isolated model. Target access is the endpoint; the model does not require the searched cards to be played, attached, or sequenced afterward.

A concrete Secret Box line also needs exact discard witnesses, current Item or Tool restrictions, Supporter timing, Stadium state, Tool attachment legality, Prize zones, and target-copy availability.

The current output slots are unit-capacity labels. Effects with repeated slots or output quantities greater than one can still be represented by repeating physical slot labels, but that extension has not been audited against a concrete card.

## Next useful work

Combine typed slot matching with per-target deadlines. A collision among late targets can sometimes be allowed to resolve through natural draws, while a same-turn collision among urgent targets creates a hard line failure. This would connect typed Secret Box geometry directly to the deadline-capacity model and provide a more faithful feasibility test for multi-axis ALS packages.
