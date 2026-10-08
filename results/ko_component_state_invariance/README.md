# Certifying Knock Out terminal-state invariance by local components

## Question

When a source-order dispute is unresolved, can the simulator prove that every candidate effect order produces one identical complete conserved state **without enumerating all global destination combinations**?

Yes, under the repository's fixed pending-Knock-Out, fixed-promotion, explicit-destination-only semantics. The solution uses the conflict-and-precedence components established in [ko_order_component_factorization](../ko_order_component_factorization/) and the exact exchangeable terminal histogram from [ko_order_zone_signature](../ko_order_zone_signature/).

The implementation is `tools/ko_component_state_invariance.py`. It is a pure destination-invariance certificate and does not determine who may order effects. It accepts only already-compiled effect programs and externally established precedence restrictions.

## Exact criterion

Construct an effect graph: effects are adjacent when they assign conflicting destinations to the same physical instance or are coupled by a specified precedence relation. Its connected components can be independently ordered.

If the same instance appears in two distinct components, every writer must assign it **the same zone**, or there would be a conflict edge. That instance has a fixed zone and can be removed from every component's variable histogram.

Every remaining written physical instance belongs exclusively to one component. For each component, enumerate local destination outcomes with the existing exact subset dynamic program, then reduce them to a local histogram of `(card_class, destination, count)`.

For fixed KO batch, fixed promotion and static route-only cleanup, **all global terminal states are identical if and only if every component has just one distinct local histogram**.

### Proof

All component orders can be freely interleaved, because dependencies occur only inside a component. The final terminal histogram equals the sum of the fixed shared-instance contributions, the unchanged default-discard contributions and one independently chosen local histogram from each component.

If every local histogram is constant, their sum is constant. If one component has two different local histograms, hold every other component's order fixed; selecting those two alternatives yields two different terminal histograms. This establishes both directions. The existing physical conservation layer proves that terminal histogram equality identifies the same full `StackBoardMaterialState` for this narrow fixed-batch cleanup.

## Computational behavior

The certificate checks every input physical route for compatibility with the pending batch. It does not expand the Cartesian product of component outcomes. It independently collects local outcomes and counts all possible global labeled effect orders through the multinomial interleaving factor.

If at least one local histogram varies, it returns `invariant=False`, identifies each varying component, reports exact total-order multiplicity, and withholds any definitive terminal state.

If all are constant, it obtains one globally valid witness order by lexicographically merging local witnesses, then executes the complete conserved physical disposal **once**. An exact resulting terminal state accompanies the certificate. Source authority still remains separate.

## Reproduction

`python results/ko_component_state_invariance/reproduce.py` compares the local certificate with the independently implemented full signature-compressed terminal projector across **175 deterministic randomized programs** with 1–7 effect instances and randomly supplied acyclic precedence constraints. It additionally verifies:

- Two physical Basic Water routing alternatives that differ by instance identity but produce one exchangeable terminal state.
- Two disconnected same-zone writers targeting the same physical instance, which remain invariant without a conflict edge.
- Two independent conflicting destination pairs, which require four local endpoint inspections rather than full global expansion.
- Empty effect sets and externally constrained single outcomes.
- A 20-effect, ten-pair stress fixture with 1,024 possible physical destination combinations. **Only 20 local endpoint examinations** establish that the overall terminal state varies, while the exact total-order count remains `20!`.

The implementation intentionally makes no claim about which candidate effect orders a current regional Pokémon TCG tournament authorizes. Establishing real trigger applicability, source-version authority, and dynamic changes to the active board remain upstream responsibilities.

## Implication

This gives future source-aware simulations a cheap, exact answer to a narrow but valuable question: does an unresolved effect-order choice matter to the next conserved material state? When it does, uncertainty can be retained without expensive exhaustive enumeration. When it does not, physical execution can proceed through the unique state while documenting unresolved authority.
