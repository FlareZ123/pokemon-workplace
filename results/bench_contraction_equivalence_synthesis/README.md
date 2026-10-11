# When successive Bench contractions can be safely merged

## Scope and result map

A suite of exact small-state analyses investigates equivalence between staged forced Bench discards, direct discard transitions, and intervening optional Ability use in **paper Expanded**.

| Component | Result | Source / test |
| --- | --- | --- |
| Pure monotone contraction | Full physical state determined by final survivors | [physical confluence](../bench_contraction_physical_confluence/) · [CI 38132208735](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132208735) |
| Concrete counterexample | Lunatone can draw before being removed | [intermediate action](../bench_contraction_intermediate_action/) · [CI 38132398998](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132398998) |
| Action-optional exact physical count | 20 discard histories become 32 annotated histories and 19 distinct full states | [physical action census](../bench_contraction_action_equivalence/) · [CI 38132538881](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132538881) |
| General exact formula | Closed-form quotient for one optional `d`-source intermediate action | [guard equivalence](../bench_intermediate_guard_equivalence/) · [CI 38132630456](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132630456) |

All four CI runs passed.

## Strategic insight

Bench contraction discards entire Pokémon objects with their evolution cards and attachments. When the only actions are two certain monotone contractions `n -> a -> b`, removed physical-card sets are disjoint and their destinations are fixed. The order in which disjoint objects leave the board therefore does not affect the final canonical physical state. The number of staged histories per unique final set is `C(n-b,a-b)`.

Any intervening action can create a strategically distinct resource history. A five-Pokémon fixture with Lunatone `me1-74` and Solrock `pgo-39` gives a printed-card witness. After a first contraction the Lunar Cycle Ability can discard a Basic Fighting Energy and draw three. A second contraction can then remove Lunatone. Directly removing the same ultimate Pokémon before the action leaves the same board with different off-board resources.

This distinction is especially important when an optimizer collapses nodes based only on retained Pokémon names. The contraction may be part of a tactical schedule: the player uses a temporary support Pokémon and then releases its Bench slot without forfeiting the resolved effect.

## A formal single-action diagnostic

Suppose an intervening optional action requires `d` named original Bench objects, has a fixed nontrivial effect, and may be used once. For `0 <= b <= a <= n`:

- Pure histories: `H0 = C(n,a)C(a,b)`.
- Histories where the action is enabled at the intermediate stage: `H1 = C(n-d,a-d)C(a,b)`.
- Original final survivor sets: `F = C(n,b)`.

A particular final survivor `S` of size `b`, containing `r` of the `d` required objects, can be reached through an action-enabled intermediate stage precisely when `b+d-r <= a`. The number of such final sets is

`R = sum_{r=max(0,b+d-a)}^{min(d,b)} C(d,r)C(n-d,b-r)`

when `a >= d`, and zero otherwise.

If the action's used and unused effects remain distinguishable in the final resource state, the exact quotient size is `Q=F+R`. This result was checked against 1,155 independent object-subset enumerations for `n<=8`.

### Two concrete capacity geometries

| Source prerequisites | Contraction | Histories incl. optional action | Full terminal states |
| --- | --- | ---: | ---: |
| Two, e.g. Lunatone/Solrock | 5 → 4 → 3 | 32 | 19 |
| Two | 8 → 5 → 3 | 760 | 112 |

These are state-space cardinalities under the specified abstract model. They do not encode player policy, match frequency, win rate, card-draw probability, or costs of establishing the original board.

## Operational recommendation for larger search engines

A state-merging implementation can use the following progression:

1. Apply only authorized capacity changes and preserve the actual choice of discarded Pokémon IDs.
2. Model action windows before collapsing histories. In particular, retain enabling Pokémon, attachment/payment resources, once-per-turn Ability quotas and any other state dimension relevant to possible intermediate actions.
3. Apply the exact physical zone transitions for each executed action and mandatory discard.
4. Merge nodes only when their complete continuation-relevant state signatures agree. The full `StackBoardMaterialState` equality checks in the tests are a local reference for physical identity and zone counts.
5. When a payoff depends on the final state alone and the hypotheses of the pure-contraction theorem hold, replace redundant paths by their exact multiplicity. Multiplicity itself is a historical count; probability weights require a separate stochastic/player-policy model.

In a more general engine, event history, public and private observations, lock states, phase boundaries, and opponent reactions may matter even when the materialized board and zone counts coincide.


## Multiple guarded actions and simultaneous feasibility

The [multi-guard extension](../bench_multi_guard_action_equivalence/) generalizes the one-Ability result to multiple optional actions. A subset of actions `U` can be performed at the intermediate stage only if the union of their prerequisite Pokémon `G_U` fits inside the **same** intermediate survivor set. If `R(n,a,b,d)` is the earlier single-guard reachable-final-set function, then for distinguishable independent action effects:

`Q = sum_{U subseteq actions} R(n,a,b,|G_U|)`.

This formula properly accounts for shared prerequisites and prevents false action combinations when the union exceeds intermediate capacity. In a source-grounded, abstract eight-Bench witness with disjoint Lunatone/Solrock and Regigigas-plus-five-Regis guards, 8→7→5 gives 336 action-annotated histories and **148** full terminal states. In particular, 36 purported combined-action states would be impossible if one naively combined independently reachable effects. An independent exhaustive oracle checked **27,172** configurations with zero, one or two guard actions for all Bench sizes up to five. [Windows CI 38133033085 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133033085).

This result assumes fixed and distinguishable resource effects for each selected action, with no other action costs or contention. For actual play, named guard geometry must be composed with source positions, Ability and Supporter quotas, resource-payment constraints, applicable locks and the action window.

## Open questions

- Can the existing action/Ability execution compiler automatically produce a minimal set of state dimensions needed for safe contraction quotients?
- Which printed departure-trigger or Bench-capacity interaction supplies the simplest *board-affecting* counterexample, beyond the demonstrated off-board draw effect?
- How should a policy evaluate temporary use of a support Ability against the opportunity cost of losing it in the second contraction, including Prize exposure and locks?
- Can action-commutation certificates be reused across concrete card prints that share the same source and resource dependency grammar?

The next substantial step is a compositional equivalence checker that compares complete *continuation* semantics, not only terminal zone snapshots.
