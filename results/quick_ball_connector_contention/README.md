# Quick Ball connector contention: attacker setup versus Gladion access

## Question

How large is the shared-connector error in a concrete Expanded-style line when Quick Ball may be needed for both:

1. a required Basic attacker; and
2. Tapu Lele-GX, which then searches Gladion?

The generic result in `results/shared_connector_contention/` proves that one-shot connectors cannot safely be counted independently across two missing channels.

This result specializes that phenomenon by adding:

- Quick Ball's discard gate;
- one Tapu Lele-GX;
- Wonder Tag setup-trigger loss;
- a setup-eligible Basic attacker;
- valid-opening conditioning;
- Prize risk;
- a Gladion rescue requirement.

Implementation: `tools/quick_ball_connector_contention.py`

Reproducer: `results/quick_ball_connector_contention/reproduce.py`

## Modeled deck

The 60-card baseline contains:

- 12 setup-eligible starters total;
- 1 Tapu Lele-GX;
- 1 required Basic attacker;
- 10 other starters;
- 4 Quick Ball;
- 2 Gladion-like rescue Supporters;
- 4 critical non-starter singletons;
- a variable number of dedicated disposable non-starters;
- filler.

The result is conditioned on a valid opening and at least one modeled critical card being Prized.

The joint first-window goal is:

- establish at least one copy of the required attacker; and
- make Gladion playable from hand.

## Physical connector model

If the attacker is already in the opening hand, it needs no Quick Ball.

If Gladion is already in hand, the Tapu Lele-GX channel needs no Quick Ball.

If Tapu Lele-GX is preserved in the opening hand because another setup starter is available, Wonder Tag can be used without searching Tapu Lele-GX.

Otherwise, each missing Basic target requires its own Quick Ball search.

Two missing Basic targets therefore require:

- two Quick Ball copies in hand; and
- two acceptable discard cards.

This is the real one-use connector capacity.

## Reusable-edge counterfactual

The comparison deliberately introduces a wrong graph abstraction.

When either or both Basic targets are missing, the counterfactual requires only:

- one Quick Ball; and
- one discard.

It effectively lets one physical Quick Ball realize both graph edges.

This isolates the overstatement caused by connector reuse.

## Result

| Dedicated disposable cards | Actual one-use Quick Ball | Reusable-edge graph | Overstatement |
| ---: | ---: | ---: | ---: |
| 4 | 7.788644% | 14.477518% | 6.688874 pp |
| 8 | 10.737693% | 21.765629% | 11.027936 pp |
| 12 | 13.057113% | 26.715925% | 13.658811 pp |
| 16 | 14.841821% | 29.943835% | 15.102014 pp |
| 20 | 16.176902% | 31.945482% | 15.768579 pp |
| 24 | 17.138910% | 33.110599% | 15.971688 pp |

All probabilities are joint first-window success given a valid start and at least one critical Prized.

## Finding 1: connector contention remains large after realistic setup semantics

At 12 dedicated disposable cards, the reusable-edge graph gives **26.715925%** joint success.

The physical one-use model gives **13.057113%**.

The graph overstates the joint line by **13.658811 percentage points**, more than doubling the physical success rate.

The gap is created by hands where the attacker and Tapu Lele-GX are both missing, both remain searchable, and the graph assigns the same Quick Ball capacity to both needs.

## Finding 2: the contention gap grows as discard gating weakens

With only four designated discardable cards, the overstatement is **6.69 points**.

At 24 designated discardable cards, it reaches **15.97 points**.

This interaction is strategically informative.

When cheap discards are scarce, the discard gate already prevents many Quick Ball lines. The one-use connector bottleneck is partly hidden behind that earlier failure mode.

As discardability improves, more hands can pay Quick Ball's cost. Shared connector capacity then becomes the dominant reason the two goals cannot both be completed.

AMR failure modes therefore need layered modeling. Removing one bottleneck can expose another.

## Finding 3: marginal reachability is a poor guide to simultaneous completion

Quick Ball has valid edges to both Basic targets.

Those edges are individually real.

The error appears when a model composes them without carrying the physical Quick Ball copy count forward.

This is a concrete deck-line version of the generic shared-connector result:

> reachability is target-local, while feasibility is resource-global.

A search algorithm needs to track connector consumption across the whole line.

## Setup interaction

The required attacker is itself a setup-eligible Basic.

When both the attacker and Tapu Lele-GX are in the opening hand, the attacker can satisfy the Active requirement and Tapu Lele-GX can remain in hand for Wonder Tag.

When Tapu Lele-GX is the only starter, it is consumed by setup and loses its hand-to-Bench trigger.

This creates a small synergy between the two target channels that a category-only generic contention model does not represent.

The specialized result therefore extends the generic shared-connector theorem rather than replacing it.

## Prize interaction

The required attacker can be Prized.

Tapu Lele-GX can be Prized.

Gladion can be Prized.

A Quick Ball edge only exists when its intended Basic target remains in the deck.

Wonder Tag only solves the rescue channel when an unprized Gladion remains searchable.

The shared connector is therefore embedded inside a larger Prize topology rather than treated as an abstract always-present target graph.

## Validation

The reproducer independently enumerates a small labeled deck over every accepted opening subset and every disjoint Prize subset.

It compares both policies:

- physical one-use Quick Ball capacity;
- reusable-edge counterfactual.

The exact category model and labeled enumeration match to floating-point precision.

## Relation to other repository results

`results/shared_connector_contention/` gives the clean general theorem for two costless non-starter targets.

`results/discard_cost_amr/` quantifies discard-cost playability.

`results/quick_ball_lele_access/` adds Tapu Lele-GX setup-trigger behavior and the Quick Ball discard gate for a single rescue objective.

This result composes those ideas into a joint objective with a shared connector.

## Limitations

The required attacker is represented as a Basic target whose mere establishment completes its channel.

The model does not include Energy, evolution, attack timing, Bench saturation, Ability lock, Item lock, alternative Pokémon search cards, later random draws, ordinary Prize-taking, or the strategic value of choosing one target over the other.

Dedicated disposable cards use a binary discard policy.

A real deck may rationally sacrifice a normally protected card when the alternative is losing the game, so the effective discard pool remains state-dependent.

## Next useful work

The next extension should assign unequal downstream values to the two channels.

When only one Quick Ball is available, an optimizer should decide whether to establish the attacker or spend the connector on Tapu Lele-GX according to the resulting line quality.

That turns connector contention from a binary feasibility problem into a resource-allocation policy problem.
