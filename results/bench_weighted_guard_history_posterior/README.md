# Exact policy-aware posterior of an intermediate Bench guard

## Question

The exact uniform-random Bench-contraction posterior assigns a fixed probability to a prerequisite Pokémon having been present before a second forced discard. How much can that inferred probability change when players prefer to retain some Pokémon over others?

**Substantially.** A simple fixed positive-weight survivor policy, representing a stylized retention preference, can shift the same conditional Lunatone/Solrock intermediate-guard probability from `1/2` to `9/10` or `1/10`. A weighted *second* discard stage can instead change it to `1/8` or `7/8` under an otherwise uniform first stage.

Implementation: `tools/bench_weighted_guard_history_posterior.py`.  
[Windows CI run 38134000279](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134000279).

## Explicit policy assumptions

Let `B` be `n` distinguishable initial Bench objects. Choose the intermediate survivor subset `A` of cardinality `a` using positive per-Pokémon *retention weights* `w_i`:

`P(A) = (product_{i in A} w_i) / e_a(w_B)`,

where `e_k(w_X) = sum_{T subseteq X, |T|=k} product_{i in T} w_i` is the elementary symmetric polynomial.

This is a probability distribution over fixed-size subsets: all weights are strictly positive, so every legal subset has nonzero probability. It is a controlled **product-weight selection model** rather than a calibrated model of real Pokémon player choice.

The second contraction to a final `b`-element set `S subseteq A` may be chosen:

1. uniformly, `P(S|A)=1/C(a,b)`; or
2. with a second positive-weight vector `v_i`, `P(S|A)=(product_{i in S}v_i)/e_b(v_A)`.

Condition on the precise observed final survivors `S`, and let `G` be a set of required original Pokémon objects for one intermediate Ability. We seek `P(G subseteq A | S)`.

These weights describe preferences for retaining Pokémon. They do not encode all game-theoretic payoffs, future draws, locks, Energy costs, damage, or the actual evolving board.

## Exact fast formula for weighted first stage and uniform second

Write `D=B\\S`, `g=G\\S`, `k=a-b`. Conditional on final `S`, an intermediate `A` is `S union T` where `T subseteq D` has `|T|=k`.

Because the second discard selection is uniform, its `1/C(a,b)` factor cancels during Bayesian conditioning. The first-stage factors from `S` also cancel. Therefore

`P(G subseteq A | S) = [ (product_{i in g} w_i) e_{k-|g|}(w_{D\\g}) ] / e_k(w_D).`

Here `e_j=0` for infeasible `j` and the empty product equals one.

This takes `O(nk)` arithmetic using a simple exact elementary-symmetric dynamic program, independent of how many `a`-object intermediate subsets exist. When every `w_i=1`, the formula simplifies to the earlier uniform result

`C(n-b-|g|,a-b-|g|) / C(n-b,a-b).`

The probability of the exact final set is also explicit:

`P(S) = [(product_{i in S}w_i) e_k(w_D)] / [e_a(w_B) C(a,b)].`

Multiplying by the posterior gives `P(S, guard enabled)`. Summing across every final set yields probability one and the correct first-stage guard marginal.

## Weighted second stage: exact finite-sum formula

If both stages have positive product weights, the probability of observing a particular final `S` given intermediate set `A` depends on *which other objects* were retained alongside `S`. Its normalization `e_b(v_A)` varies by the hidden intermediate state.

Bayesian conditioning gives, with `D=B\\S` and `k=a-b`,

`P(G subseteq A | S) =
 [sum_{T subseteq D, |T|=k, g subseteq T} (product_{i in T}w_i)/e_b(v_{S union T})]
 /
 [sum_{T subseteq D, |T|=k} (product_{i in T}w_i)/e_b(v_{S union T})].`

The implementation evaluates this finite sum exactly with rational arithmetic and calculates the matching joint/final probabilities. For small Expanded Bench capacities (at most eight in the current catalog), exhaustive subsets are manageable. The formula does not assume that the final choice is independent of intermediate Bench composition.

## Controlled source-grounded witness

Consider a five-to-four-to-three contraction. Let `G={0,1}` represent Lunatone `me1-74` and Solrock `pgo-39`. Observe final `S={0,2,3}`: Lunatone survives, Solrock was discarded, and the final Bench contains two other Pokémon.

There are two possible intermediate four-object survivor sets:

- `A_guard={0,1,2,3}`, in which both Lunar Cycle prerequisites were present;
- `A_other={0,2,3,4}`, in which one prerequisite was already gone.

With both stages uniform, each history has equal probability after conditioning on final `S`, so the posterior is `1/2`.

### Change the first-stage preference

Keep the second contraction uniform. If the first-stage retention weight of object 1 (Solrock) is nine times that of object 4, the posterior becomes `9/10`. If object 4 is favored nine-to-one over object 1, it becomes `1/10`. All other objects have weight one.

### Change the second-stage preference

Keep the first contraction uniform, but use second-stage retention weights of nine for one missing object and one for all other objects.

- Favoring **Solrock** (object 1) for final retention makes the *observed* final Bench that discarded it much less likely under `A_guard`. The posterior that Solrock had been present at the intermediate stage falls to `1/8`.
- Favoring **object 4** instead makes the observed final Bench that discarded object 4 rare under `A_other`, so the posterior that the guard had been present rises to `7/8`.

The second-stage reversal is a selection/conditioning effect: a surviving high-priority object would usually be retained, so seeing it absent after a weighted second contraction is evidence about which hidden intermediate set existed.

The 9:1 weights are illustrative preference ratios. They are not measured card values, a fitted human policy, or evidence that one particular Pokémon should have nine times another's strategic value.

## Independent exact validation

The implementation compares its elementary-symmetric formula against a separate **full forward enumeration** of both stages:

- choose each intermediate `A` with its exact product-weight probability;
- from each `A`, choose every final `b`-object set `S` with the specified second-stage probability;
- accumulate the joint event that the guard was present and final `S` is observed;
- divide the joint probability by the final-state marginal.

It performs the comparison across `n=0,...,7`, every guard cardinality, all `0<=b<=a<=n`, all final subsets, and three positive weight profiles, totaling **22,269** independent oracle comparisons.

Further tests verify:

- full equality with the uniform hypergeometric posterior when all weights equal one;
- exact 9/10 versus 1/10 first-stage preference reversals;
- exact 1/8 versus 7/8 second-stage preference reversals, compared to independent full enumeration;
- final-set probability normalization across representative five-, six-, and eight-object models;
- rejection of zero, missing and otherwise invalid weights.

All calculations use exact `fractions.Fraction` arithmetic. [Windows CI run 38134000279](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134000279).

## Strategy and simulator implications

Even when the same final board is observed, a history-compressing simulator's posterior for whether a support engine was available earlier can vary dramatically with the discard policy. A uniform random model gives a useful baseline; strategic decisions introduce a selection effect.

The weighted model supplies a composable, parameterized bridge between the earlier combinatorial occupancy proofs and future policy-aware state evaluation. An empirically fitted or game-theoretic policy could supply the weights, but the assumption that subset preferences factor as products must itself be tested.

There is no inference about real gameplay incidence or win rate.

Related results: [uniform guard posterior](../bench_guard_history_posterior/), [joint guard posterior](../bench_guard_joint_posterior/), [action-sensitive contraction synthesis](../bench_contraction_equivalence_synthesis/).
