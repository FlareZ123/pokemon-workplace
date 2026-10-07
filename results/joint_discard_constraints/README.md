# Joint discard constraints: scalar/cardwise DCI is insufficient

## Question

Can a per-card discardability score or independent per-card limit determine whether a multi-card discard cost is strategically acceptable?

No.

This result formalizes one failure mode anticipated by the DCI discussion in `resources/human_concepts.md`.

Implementation: `tools/joint_discard_constraints.py`  
Regression: `results/joint_discard_constraints/reproduce.py`

## Deterministic counterexample

A hand contains one copy each of three card classes:

`A, B, C`

Every card is individually acceptable to discard.

The strategic continuation also requires that at least one of A or B survive.

Equivalently, the discard set must satisfy:

`discard(A) + discard(B) <= 1`

With only independent cardwise limits, all three two-card witnesses appear legal:

- A + B;
- A + C;
- B + C.

The joint constraint removes A + B and leaves two witnesses.

For a three-card cost:

- the independent model has one witness: A + B + C;
- the joint model has zero witnesses.

Every card remains individually discardable. The missing information is relational.

## Exact group-constraint layer

`DiscardGroupConstraint` adds an upper bound across a named set of candidate card classes.

For the example:

`{A, B}: max_total = 1`

`enumerate_group_constrained_discard_selections()` first obtains the exact card-class witnesses from the existing discard enumerator, then filters them by all group constraints.

This leaves the original exact execution layer unchanged while allowing a policy layer to express cross-card retention requirements.

## Probabilistic counterexample

The reproducer also shows that equal marginal discardability does not determine cost payability.

Two latent-state models both give:

- P(A discardable) = 1/2;
- P(B discardable) = 1/2.

Model 1 is anti-correlated:

- probability 1/2: only A is discardable;
- probability 1/2: only B is discardable.

Then a two-card discard is payable with probability 0.

Model 2 is positively correlated:

- probability 1/2: neither is discardable;
- probability 1/2: both are discardable.

Then a two-card discard is payable with probability 1/2.

The two models have identical per-card marginals and different joint feasibility.

This specifically rules out treating scalar DCI values as independent discard probabilities when multi-card costs matter.

## Representation consequence

A stronger discardability representation can separate:

1. per-card or per-class scores used for ranking;
2. exact legal discard witnesses;
3. joint retention constraints over sets of cards;
4. uncertainty over which joint constraints apply in the current hidden or future state.

A scalar DCI can remain useful as a heuristic feature.

It cannot be a sufficient statistic for all discard-cost decisions.

## Relation to existing work

`discard_cost_amr/` shows that the size of the disposable pool strongly changes immediate playability.

`discard_cost_witness/` shows that exact payment identity matters after a cost is paid.

This result adds the layer between them: even before choosing the exact witness, the set of strategically acceptable witnesses may have cross-card structure that independent candidate limits cannot express.

`temporal_discard_replenishment/` adds another dimension: the acceptable witness family can change after earlier actions generate new cards.

## Practical examples of joint constraints

The generic constraint can represent policies such as:

- preserve at least one of two redundant recovery routes;
- never discard both copies of the only remaining attacker family;
- keep at least one of several cards that all satisfy the same later requirement;
- preserve one member of a pair whose exact identity does not matter until later.

These are policy constraints rather than universal card properties.

## Limits

The group layer uses upper-bound linear constraints over selected card counts.

More complex policies may depend on nonlinear conditions, matchup state, Prize information, sequence position, or future stochastic outcomes.

The result does not claim that DCI should be abandoned. It proves that cardwise scalar values alone cannot encode every joint discard decision.

## Next useful work

The natural extension is a discard-policy object that can compile state-dependent strategic requirements into:

- per-class limits;
- cross-class group constraints;
- exact witness ranking.

That policy can then be evaluated at each temporal payment point after the hand changes.
