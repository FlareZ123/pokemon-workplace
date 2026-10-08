# Exact factorization across independent KO destination-conflict groups

## Motivation

The baseline [KO order outcome-space solver](../ko_order_outcome_space/) avoids factorial enumeration by storing partial destination assignments in a dynamic program. Nonetheless, its subset state still grows with the total number of effects, including those that cannot affect one another.

In the concrete [Tyranitar-GX double-KO study](../tyranitar_double_ko_ordering/), one pair of effects conflicts only over the Active Aegislash evolution stack, while a second pair conflicts only over the Benched Lapras's attached Basic Water Energy. The two conflicts can be analyzed independently as long as no external precedence requires an order between their members.

The new `tools/ko_order_component_factorization.py` detects this structure and combines exact local results, preserving every physical endpoint, exact total-order multiplicity, and lexicographically smallest witnessing effect order.

## Independence criterion

Build a graph whose vertices are effect-instance identifiers.

Add an undirected edge between two effects when:

- they explicitly assign **different destination zones** to the **same physical card instance**; or
- an external precedence constraint references the two effects.

Overlapping assignments to the same zone are harmless for destination-only outcomes and do not create a conflict edge. Precedence edges are treated as undirected only for the purpose of forming independent groups; their direction is retained within the exact local solver.

Every connected component can be evaluated using the established `ko_order_outcomes` subset DP. If there is only one component, this reproduces the baseline.

## Exact count formula

Suppose the graph has `m` independent components, containing `n_1,...,n_m` labeled effects, with total `N = n_1 + ... + n_m`. Let `c_i(o_i)` be the exact number of legal-within-input orders in component `i` producing local endpoint `o_i`.

Because there is no cross-component precedence and the first-explicit-destination operation is commutative between independent components, the global endpoint `(o_1,...,o_m)` is produced by

\[
C(o_1,\ldots,o_m)
=\frac{N!}{n_1!n_2!\cdots n_m!}
\prod_{i=1}^{m}c_i(o_i).
\]

The multinomial factor counts all possible interleavings of each component's internal effect order. It is independent of the component endpoint selections.

The global per-instance zone vector is the merge of local vectors. Even when components explicitly mention the same instance, their assignments must agree in zone or an edge would have connected them. Such merging is therefore safe under the destination-only semantics.

For a witness, the lexicographically smallest global interleaving is built greedily from the head of each component's own lexicographically smallest endpoint-producing order. No precedence edge crosses a component boundary.

## Validation

`results/ko_order_component_factorization/reproduce.py` compares the factorized result with the **original monolithic exact solver** for 280 deterministic random programs with one through seven effects, including randomly generated acyclic precedence constraints. Equality covers every endpoint, count and full witnessing order. The test includes explicit overlap-without-conflict, a precedence edge joining previously independent groups, and malformed/cyclic constraint rejection.

It also imports the real Tyranitar-GX double-KO witness:

- grouped Lost Out produces one connected component;
- target-specific Lost Out produces two independent conflict-pair components.

The exact outcomes agree with the original solver in both representations.

A larger synthetic workload contains **20 effects** organized into ten disjoint conflicting pairs. The factorized algorithm handles **1,024 physical endpoints** with exact identical multiplicities of `20! / 2^10` orders each, summing to `20!` labeled permutations. Evaluating ten local two-effect DPs avoids materializing the large monolithic 20-effect subset frontier.

## Scope and limits

The independence graph certifies route commutativity for **already compiled, destination-only effects** and explicit precedence edges. It does not certify that real triggered effects are ready simultaneously, that their activation conditions remain valid after other state changes, or that separate rules sources agree on ordering authority.

Effects that mutate a surviving Pokémon, alter triggers, change card identity, or require live board-state inspection can create dependencies absent from destination assignments. Such effects must be handled by a stronger semantic dependency graph or a stateful effect scheduler. The current factorization is exact within its deliberately narrow scope.

The total number of distinct final states can still grow exponentially when independent effects offer real binary alternatives. Factorization removes redundant global-order bookkeeping; it cannot eliminate genuinely distinct endpoints without a further justified utility or exchangeability quotient.
