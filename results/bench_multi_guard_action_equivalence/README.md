# Exact Bench-contraction equivalence with multiple independent guarded actions

## Question

How many distinct complete terminal states can survive the quotient of two forced Bench contractions when several optional, resource-distinguishable actions may be taken at the intermediate stage, each with its own set of prerequisite Pokémon?

The exact model demonstrates a crucial constraint: **individually reachable guarded actions need not be jointly reachable**. A search that separately certifies each action's availability can invent a combined path when their union of required Pokémon does not fit into the same intermediate Bench.

Implementation: `tools/bench_multi_guard_action_equivalence.py`.  
[Passing Windows CI run 38133033085](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133033085).

## Model contract

The model starts with `n` distinct initial Benched Pokémon objects and two externally authorized forced capacity reductions `n -> a -> b`, where `0 <= b <= a <= n`.

There are `m` optional intermediate actions indexed by `j`. Action `j` requires a fixed set of original Bench-object identities `G_j` to remain in play at the intermediate stage. Within this **controlled model**:

- any subset of simultaneously enabled actions may be executed, in any order, with once-per-action uses and no resource contention;
- every selected action has one fixed nontrivial distinguishable off-board resource effect, independent of other selected actions;
- action outcomes do not change the board or the availability of other actions;
- the only Bench changes are the two chosen contractions, and discard transitions preserve whole stacks and attachments;
- other player turns, locks, probabilities, action usage limits, cost payments and phase legality are supplied by a future whole-turn engine.

The action-subset identity is part of the final-state signature: two distinct action subsets produce different resource outcomes. This assumption is needed for the exact quotient formula and should be relaxed explicitly when two actions have observationally equivalent or interacting effects.

## Exact combinatorial quotient

Let `U` be a chosen subset of optional action indices. Write `G_U = union_{j in U} G_j` and `d_U = |G_U|`. For an action subset to be enabled, the intermediate survivor set must retain the **entire union**.

The number of action-annotated paths using exactly subset `U` is

`H_U = C(n-d_U, a-d_U) C(a,b)`.

Here `C(x,y)=0` if `y<0` or `y>x`.

For a final survivor set of size `b`, an intermediate survivor set of size `a` exists that supports the chosen actions when the union of its final members and `G_U` fits at capacity `a`. The number of terminal survivor sets reachable through that action subset is

`R(n,a,b,d_U) = sum_{r=max(0,b+d_U-a)}^{min(d_U,b)} C(d_U,r)C(n-d_U,b-r)`

when `a >= d_U`, and zero otherwise.

Therefore, if each action subset's off-board effect is distinguishable, the full terminal-state quotient is

`Q(n,a,b,G_1,...,G_m) = sum_{U subseteq {1,...,m}} R(n,a,b,|G_U|)`.

The action-annotated history count is `H = sum_U H_U`.

This uses **union cardinalities**, so shared prerequisites are counted only once. It also correctly rejects a joint-use branch when `|G_1 union G_2|>a`, even when each `|G_j|<=a`.

## Source-grounded disjoint-guard geometry

The bundled Expanded card records supply a concrete pair of named-Ability prerequisite families:

- **Lunatone `me1-74`, Lunar Cycle**, requires **Solrock** in play and permits discarding a Basic Fighting Energy to draw three cards. Treat the two objects as one guard set of size two, including the source.
- **Regigigas `swsh10-130`, Ancient Wisdom**, requires **Regirock, Regice, Registeel, Regieleki and Regidrago** in play, together with the Regigigas source. Treat these six objects as a disjoint guard set of size six.

A hypothetical eight-Pokémon Bench contains all eight distinct named objects, and a separate Active Pokémon remains on the board. This is a **geometric abstraction**, not a claim about a tournament-legal initial board or achievable deck setup. An eight-Bench capacity must be provided externally; actual card effects, legality, energy access and activation windows are outside the proof.

At the intermediate capacity of seven, either the two-object guard or the six-object guard can fit alongside other survivors, but the union of all eight cannot fit. For `n=8, a=7, b=5`:

| Selected action subset | Guard union size | Action histories | Distinct reachable final survivor sets |
| --- | ---: | ---: | ---: |
| Skip both | 0 | 168 | 56 |
| Lunar Cycle only | 2 | 126 | 56 |
| Ancient Wisdom only | 6 | 42 | 36 |
| Both | 8 | 0 | 0 |
| **Total** | | **336** | **148 full states** |

If the model assumes that the two actions' separate availability can be combined into one action history, it invents **36** joint terminal states that no intermediate seven-slot Bench can support. This is an *infeasible-path* problem independently of Energy payments, action quotas or resource acquisition.

## Exhaustive verification

The regression generates all possible guard subsets of `n=0,...,5` objects, for `m=0,1,2` ordered optional actions, every `0<=b<=a<=n`, and all overlap structures. It compares the closed-form history count and full-state quotient to an **independent enumeration**:

1. choose every first-stage survivor set;
2. determine the actions enabled by that actual set;
3. enumerate every second-stage survivor set;
4. enumerate all subsets of enabled optional actions;
5. count exact `(final survivors, chosen action subset)` signatures.

All **27,172** parameter configurations match. Additional exact checks cover the eight-name disjoint guard witness and a pair of overlapping two-name guards.

The tests passed [GitHub Actions run 38132969638](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132969638) and a [Windows hosted repeat, run 38133033085](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133033085).

## Strategic interpretation

A state-space optimizer can eliminate duplicate histories by checking the **joint feasibility of the entire action prerequisite union** in the same intermediate board. Merely annotating independent access paths does not establish their combinability.

An exact resource-aware successor must additionally track action contention, costs, timing, source positions (Active or Bench), effects that modify available actions, information, and resulting resource states. Regigigas's actual Energy-attachment destination and Lunar Cycle's discard/draw requirements make these considerations significant in real games.

This result counts structural possibilities only. It does not estimate probability of the eight-object board, match win rate, benefit of either Ability, or practical deck-construction feasibility.

## Related research

- [Single guarded action quotient](../bench_intermediate_guard_equivalence/) derives `R` and verifies it in 1,155 cases.
- [Physical Lunar Cycle example](../bench_contraction_action_equivalence/) demonstrates that actions can change the full zone ledger between Bench contractions.
- [Joint named-guard capacity](../bench_joint_named_guard_capacity/) examines simultaneous positioning of named-Ability prerequisites.
- [Sequential named-guard release](../bench_temporal_guard_release_bounds/) studies performing guarded effects at different stages of a Bench-release schedule.
