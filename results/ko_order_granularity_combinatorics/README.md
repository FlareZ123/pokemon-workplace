# Exact counting under grouped versus per-target KO effect granularity

## Question

Can two mathematically equivalent representations of the same Knock Out replacement choices have the same physical endpoints while assigning different numbers of possible effect orderings to each endpoint?

**Yes.** The [Tyranitar-GX double-KO fixture](../tyranitar_double_ko_ordering/) provides a concrete example with two victims. The general result is a combinatorial theorem for any positive integer number of independent targets.

## Abstract setup

Let there be `n` mutually independent physical KO targets. For target `i`, a recover effect `R_i` moves its card to hand if it resolves before a Lost Out-like assignment. Otherwise that target enters the Lost Zone. Earlier explicit destination assignments determine the final zone.

Two representations are compared:

**Grouped loss:** a single global loss effect `L` assigns all `n` targets to Lost Zone. It competes with the `n` individual recovery effects `R_1,...,R_n`. There are `n + 1` labeled effects.

**Per-target loss:** each target has its own loss effect `L_i` competing with `R_i`. There are `2n` labeled effects, with disjoint target sets across pairs.

All effects are treated as ready at one shared decision window. Neither representation is asserted to be uniquely mandated by actual Lost Out card text for simultaneous Knock Outs. They are distinct abstract input semantics.

## Derivation

There are exactly **`2^n` distinct physical destination vectors** in either representation: each target chooses one of two zones.

In the grouped representation, fix a subset `S` of `k` targets which recover to hand. For each target in `S`, its recovery effect must precede `L`; for each other target, its recovery effect must follow `L`. The `k` predecessors can be ordered in `k!` ways, and the `n-k` successors in `(n-k)!` ways. Thus the number of effect orders yielding exactly that subset is

\[
m_{\mathrm{grouped}}(S)=k!(n-k)!
\]

Summing over all subsets yields

\[
\sum_{k=0}^{n}\binom{n}{k}k!(n-k)!=(n+1)!
\]

In the per-target representation, the relative order of `R_i` and `L_i` determines target `i`'s result. Swapping their labels is a bijection between the two outcomes for that target and leaves other pairs unchanged. The `(2n)!` permutations therefore split equally among `2^n` subsets:

\[
m_{\mathrm{per-target}}(S)=\frac{(2n)!}{2^n}
\]

These are exact counts over abstract labeled effect permutations.

## Reproduction

`results/ko_order_granularity_combinatorics/reproduce.py` builds both effect-program variants for each `n = 1,...,5`, enumerates distinct destination vectors using the independent `ko_order_outcome_space.py` dynamic programming solver, then compares **every** per-subset multiplicity with its corresponding closed-form expression. It also verifies the totals `(n+1)!` and `(2n)!`, plus the `n=2` Tyranitar double-KO fixture's observed multiplicities.

| Targets (`n`) | Physical endpoints | Grouped abstract orders | Per-target abstract orders |
| ---: | ---: | ---: | ---: |
| 2 | 4 | 6 | 24 |
| 3 | 8 | 24 | 720 |
| 4 | 16 | 120 | 40,320 |
| 5 | 32 | 720 | 3,628,800 |

## How naive random-order sampling goes wrong

Consider the **all-Lost-Zone** endpoint under a synthetic harness that samples uniformly among labeled effect orders:

- Grouped loss: `n!` of `(n+1)!` orders yield all loss, with artificial weight `1/(n+1)`.
- Per-target loss: `(2n)!/2^n` of `(2n)!` orders yield all loss, with artificial weight `1/2^n`.

At `n=5`, the identical physical endpoint receives weight **1/6** under the grouped model and **1/32** under the per-target model, a factor of **16/3**. The difference is a modeling artifact of effect-instance granularity.

These weights are **neither gameplay probabilities nor estimates of actual players' decisions**. Pokémon players can choose the order when authorized, and additional card-specific rules may constrain how a source effect is resolved. A simulator that samples abstract permutations uniformly without an explicit behavioral model can make its outcome distribution depend on a representation choice.

## Implication

Deck simulations, payoff solvers and KO branching models should separate the *set of reachable physical states* from the *number of syntactic effect-order paths*. The right search-space reduction preserves legal options and source authority, then gives game states values through an explicit player policy or adversarial objective. Representation-dependent permutation counts should not be substituted for strategic probabilities.
