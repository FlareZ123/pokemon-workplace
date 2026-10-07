# Retrieval projection preserves strategic feasibility

## Question

Does moving physical retrieval before strategic demand evaluation change the demand profiles the earlier typed allocator considered reachable?

For the regression cases, no. It is a refinement that preserves strategic feasibility while retaining additional physical actions.

Implementation: `tools/typed_search_retrieval.py`  
Regression: `results/retrieval_projection_equivalence/reproduce.py`

## Method

For each case, the test computes:

1. demand-first profiles with `enumerate_typed_target_profiles()`;
2. all raw physical retrieval actions;
3. every demand profile obtainable by projecting each raw retrieval after the fact.

After removing the all-zero demand profile, the projected raw profile set must equal the demand-first profile set. Full-demand feasibility must also match.

## Cases

The first regressions cover:

- Guzma & Hala with Stadium, Tool, and Special Energy targets while the only strategic demand is Special Energy;
- Secret Box with four physical output axes while only Item and Supporter are strategic demands.

The retrieval-first representation contains more exact actions because it keeps cards that do not satisfy an immediate demand. Its projection still reproduces the older strategic reachability result.

## Consequence

The older demand-first allocator remains useful as a compressed evaluator. Retrieval-first state is a richer execution representation rather than a different definition of strategic demand satisfaction.

This gives a safe migration direction:

`physical retrieval -> strategic projection`

instead of requiring search generation itself to discard side-payload information.

## Limits

The current regression set is small. Multi-unit outputs, distinct-type constraints, and overlapping broad/narrow selectors should also be included before treating equivalence as a general invariant.
