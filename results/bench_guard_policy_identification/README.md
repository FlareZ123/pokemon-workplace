# A missing intermediate Bench guard has no nontrivial policy-free probability bound

## Research question

After observing the final Bench following two forced contractions, one may know that a named-Ability guard could have been present earlier. Without a model of the player's discard choices, can the earlier guard's probability be bounded more tightly than zero to one?

For the simplest positive-weight survivor-selection family, the answer is **no whenever both enabled and disabled histories are structurally possible**. The posterior can approach either zero or one, even though the final survivors are fixed.

Implementation: `tools/bench_guard_policy_identification.py`.  
[Windows CI 38134213217 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134213217).

## Setup and exact polynomial

Consider a starting Bench with `n` distinguishable Pokémon objects undergoing contractions `n -> a -> b`, with the exact final `b`-survivor set `S` observed.

Let:

- `N=n-b`: original Pokémon absent from the final Bench;
- `k=a-b`: original objects outside the final Bench that temporarily survived the first contraction;
- `g=|G\\S|`: named Ability-prerequisite objects absent from the final Bench.

Assume the second contraction chooses final survivors uniformly within the intermediate Bench, while the first stage uses a positive **product-weight** policy. Set the retention weight of every `g` missing guard object to `t>0`, and all other `N-g` objects outside the final Bench to weight one. (Weights on the known surviving objects cancel under conditioning.)

Among the `k` temporarily retained objects, let `j` be missing guard objects. The unnormalized probability of selecting `j` of them is

`C(g,j) C(N-g,k-j) t^j`.

The total normalizer is the positive polynomial

`Z(t) = sum_{j=max(0,k-(N-g))}^{min(k,g)} C(g,j) C(N-g,k-j) t^j`.

The complete intermediate guard survives iff all `g` missing guard objects were temporarily retained, giving the exact posterior

`q(t) = [C(N-g,k-g)t^g]/Z(t)`.

This is the specialization of the elementary-symmetric weighted posterior in [bench_weighted_guard_history_posterior](../bench_weighted_guard_history_posterior/).

## Exact feasibility classes

The structurally determined cases follow from the two-stage occupancy geometry:

| Condition | Classification | Posterior for every positive `t` |
| --- | --- | --- |
| `g=0` | Prerequisites all present finally | `1` |
| `k=N` | No first-stage object was actually lost | `1` |
| `g>k` | Too few temporary Bench slots to hold all missing prerequisites | `0` |
| `0<g<=k<N` | Both enabled and disabled histories possible | `0<q(t)<1` and policy-sensitive |

In the **policy-sensitive** case, the highest term of `Z(t)` is exactly the numerator, with exponent `g`. Since `k<N`, at least one lower-degree term exists and has a positive coefficient. Therefore

`q(t) = 1 / [1 + sum_{j<g} c_j t^{j-g}]`

with nonnegative coefficients `c_j` and at least one positive coefficient.

Every exponent `j-g` in the denominator correction is negative, so `q(t)` is strictly increasing in `t`. Its limits are

`lim_{t->0+} q(t)=0` and `lim_{t->infinity} q(t)=1`.

By continuity, every probability strictly between zero and one occurs for some positive finite preference ratio `t` under this simple policy family. The closure of the *policy-unidentified posterior set* is therefore `[0,1]`.

That conclusion is stronger than simply saying uniform random discards are unrealistic. Even restricting to one positive product-weight policy family, the exact final survivor set and legal rules alone cannot bound the earlier enabling event more sharply when both types of history are physically feasible.

The qualification is important: in actual games, knowledge of the player's policy, observed intermediate discard choices, known resource costs, or other evidence can narrow the posterior.

## Printed-card-motivated witness

Use the abstract Lunatone `me1-74` and Solrock `pgo-39` prerequisite pair and the five-to-four-to-three capacity schedule. Suppose the final three-Bench survivors include exactly one of the pair, giving

`N=2, k=1, g=1`.

Then `Z(t)=1+t` and

`q(t)=t/(1+t)`.

| Relative retention weight `t` for the absent guard | Posterior `q(t)` |
| ---: | ---: |
| `1/1000` | `1/1001` |
| `1` | `1/2` |
| `9` | `9/10` |
| `1000` | `1000/1001` |

All four posteriors are compatible with the **same** final Bench survivor identities and the same legally possible intermediate geometry. The weights describe hypothetical player choice tendencies, not actual human preferences.

## Independent exact validation

The regression enumerates all `N=0,...,8`, `0<=k,g<=N`, and four distinct positive weight ratios `1/5,1,5,25`, totaling **1,140** exact comparisons.

The independent oracle physically enumerates every `k`-object subset of the `N` absent-from-final objects. Each subset receives probability weight `t^(number of guard objects selected)`. It separately totals the weight of subsets containing **all** missing guard objects and the full normalizer.

Every oracle probability equals the rational binomial-polynomial value. Additional checks verify the classification and strict monotonicity for every small parameter triple, the Lunatone `t/(1+t)` special case and input rejection. [Windows CI 38134213217 succeeded](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134213217).

## Implications

A simulator or tactical evaluator should distinguish:

1. **Structural possibility**, decided by legal state geometry and card prerequisites.
2. **Conditional probability**, which requires a specified or learned discard policy.
3. **Strategic value**, which additionally requires payoff/continuation assessment and realistic action costs.

Only structural impossibility or certainty is policy-robust in this bare geometry model. Reporting a uniform-discard posterior as an objective probability of strategic player behavior would overstate the evidence.

A future implementation could constrain plausible retention odds from observed player tendencies or a continuation-aware optimization policy, then compute *conditional* probability intervals. Those extra premises must remain explicit.

Related research: [weighted posterior](../bench_weighted_guard_history_posterior/), [uniform posterior](../bench_guard_history_posterior/), [joint-guard correlation](../bench_guard_joint_posterior/).
