# Exact KO terminal state distribution without global route expansion

## Question and contribution

A destination-only Knock Out model may have exponentially many physical-instance routing outcomes yet very few conserved states after equivalent copies are dematerialized. Earlier work reduced full physical disposals by grouping signatures, but still enumerated every global instance-level destination vector.

The new `tools/ko_order_histogram_convolution.py` solves that representation problem. It combines exact component-local destination distributions **directly at the exchangeable terminal histogram level**. It never constructs the global Cartesian product of instance routes.

Under one fixed pending-KO batch and promotion, an outcome includes its complete conserved terminal `StackBoardMaterialState`, exact integer number of labeled candidate effect orders, and one verifiable order witness. Counts are combinatorial order multiplicities, without any assumption that a real player randomizes their choices.

## Method

1. Build the established conflict-and-precedence graph between effect instances. Independent connected components can be ordered separately.
2. Classify each affected card instance. An instance mentioned in two components can only receive one constant destination from all of them; otherwise their effects would have been connected by a conflict edge. Count such fixed instances once. Count untouched KO cards as default discard.
3. For each component, use the previously validated exact subset DP to enumerate **local** physical-instance route outcomes.
4. Group local outcomes by sparse `(card_class, destination_zone, count)` histograms for instances written exclusively by that component. Add their exact within-component order counts, retaining an order witness.
5. Convolve these local histogram distributions. Merge equivalent aggregate histograms *after each component*, summing products of route-order counts.
6. Multiply by the exact multinomial factor `N! / product(n_i!)` for interleavings between independent components.
7. Resolve one witness order and run the existing physical conservation kernel once per distinct final histogram. Independently check the predicted histogram against the actual route execution.

All externally imposed precedence edges stay inside components by graph construction. There are no cross-component constraints.

### Correctness rationale

For every globally valid order, restriction to each component produces a unique local order and local histogram. Its total terminal histogram equals the sum of the fixed terms and component-local terms. The number of global interleavings is the same for every fixed combination of local orders, yielding the multinomial factor. Ordinary histogram convolution therefore counts **every** candidate total order exactly once and groups precisely by final conserved state.

This remains true if different local combinations have the same global histogram: their counts add at the merge step, and a legitimate witness can be retained.

## Independent verification

`results/ko_order_histogram_convolution/reproduce.py` compares all conserved terminal states and exact multiplicities against the preceding full signature-projection implementation over **175 deterministic random one-to-seven-effect programs**, including random acyclic precedence constraints. It additionally covers empty effects, identical-zone writers, instance-identity swaps, externally constrained outcomes, and both representations of the real printed-card Tyranitar-GX double Knock Out fixture.

A larger synthetic stress test has an Active Lapras with **40 physically distinct, gameplay-equivalent Basic Water Energy cards** attached and a Benched Bidoof. For each Water card, two abstract competing effects send it to hand or Lost Zone, generating **80 effect instances in 40 independent conflict pairs**.

Under these synthetic assumptions:

- There are `2^40 = 1,099,511,627,776` distinct physical-instance zone assignments.
- There are `80!` labeled effect orders.
- There are exactly **41 distinct conserved terminal states**, characterized by `k = 0,...,40` Water cards in hand.
- State `k` represents `C(40,k)` physically different assignments and `C(40,k) * 80! / 2^40` labeled effect orders.
- The algorithm examines **80 local route outcomes** and performs exactly **41 full physical disposals**.

The test verifies every state, its exact count, survivor promotion, and conservation of all initial card classes. A naive global enumerator would need to expand more than a trillion instance-level outcomes merely to obtain these 41 exchangeable states.

The stress-effect programs are synthetic and are not asserted to originate from 80 simultaneously triggered real card effects. The Energy-heavy board itself is a valid state for the existing fixed-batch attachment model; the purpose is exact algorithmic scalability.

## Limits and downstream use

The route histogram quotient is sound only when copy-specific histories are irrelevant after the KO, with fixed pending KO membership, unchanged survivors, a fixed promotion and destination-only movement. It cannot merge states when attack triggers, Prize events, reveal effects, identity-sensitive callbacks, or changed board resources create further distinctions. Current official card-text eligibility and ordering authority are external to this library.

The new convolution API offers an alternative to both global physical-instance outcome enumeration and the local yes/no invariance certificate. It returns the **complete weighted set of conserved terminal states** when downstream strategy genuinely needs those states, without representation-dependent probability assumptions.

### Reproduction

Run `python results/ko_order_histogram_convolution/reproduce.py`, or invoke the GitHub Actions workflow `validate-ko-order-histogram-convolution.yml`.
