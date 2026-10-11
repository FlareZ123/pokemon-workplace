# Multi-target Prize rescue: why knowing every slot can still be insufficient

## Finding

The one-singleton Arc Phone to Peonia guarantee does not extend directly to recovering *multiple* critical Prized cards simultaneously. The limiting factor becomes **Peonia's capacity to select three physical Prize positions**, even when Arc Phone has revealed much of the hidden Prize arrangement.

In a controlled state with n=6 facedown Prizes, q distinct critical singleton cards (q=1,2,3), a usable Arc Phone copies, one Peonia, a known filler deck top, and enough expendable hand filler to satisfy Peonia's Prize replacement payment, the exact probability of acquiring **all q cards** in the same turn is:

| Arc Phone copies | One target | Two targets | Three targets |
|---:|---:|---:|---:|
| 0 | 1/2 | 1/5 | 1/20 |
| 1 | 1/2 | 1/5 | 1/20 |
| 2 | 2/3 | 1/3 | 1/10 |
| 3 | 5/6 | 8/15 | 1/5 |
| 4 | 1 | 4/5 | 2/5 |

**Four Arcs guarantee a single-Prize singleton rescue, but only 80% joint success for two Prized singletons and 40% for three.** All results condition on those exact numbers of targets known to be Prized; they are not probabilities of those initial Prize configurations occurring in a normal game.

## Why access to positions is insufficient

Arc Phone (\`swsh11-152\`) can observe the deck top and optionally swap it with a facedown Prize. One Arc moves a hidden Prize to deck top and the next Arc can recognize its identity. Peonia (\`swsh6-149\`) can retrieve at most three chosen Prize cards, so a previously discovered important card consumes one of those selections.

With four Arcs, the player can identify up to three initially unknown Prize positions through the serial exchange chain. Suppose exactly one of two target singletons lies among those three identified slots. The player knows which slot holds that target and can select it with Peonia, but only two Peonia selections remain for the other target, which is uniformly among three uninspected positions. Conditional rescue is therefore 2/3. The remaining scenarios are either both targets in the identified group or both in the other three slots; in those cases Peonia can acquire both with certainty. The weighted total is 4/5.

This illustrates a concrete **observation versus acquisition-capacity collision**. Revealing a critical card may increase the certainty of acquiring it, while using one of the finite Peonia slots to acquire it reduces the number of unknown positions the same Supporter can cover.

## Exact hypergeometric formula

Let k=max(0,a-1) be the number of newly identified Prize positions from a Arcs when the initial deck top is known filler. Let j of the q target cards occur among those k positions. The exact chance of a joint rescue by Peonia (selection capacity m=3) is

\[
P = \sum_{j=\max(0,k-n+q)}^{\min(k,q)}
\frac{\binom{q}{j}\binom{n-q}{k-j}}{\binom{n}{k}}
\frac{\binom{\min(m-j,n-k)}{q-j}}{\binom{n-k}{q-j}},
\]

where any impossible combination contributes zero.

The first fraction is the probability of observing j targets among the k physically inspected positions. The second is the probability that the remaining q-j target positions lie among up to min(m-j,n-k) still-available Peonia selections in the uninspected pool.

This formula depends on the joint goal. Counting the union of observed and Peonia-selected positions and then applying a one-target argument overstates the probability of acquiring multiple targets because identified targets consume the same finite retrieval slots.

## Independent policy verification

\`tools/arc_peonia_multi_target.py\` implements both the exact hypergeometric policy and a separately structured \`Fraction\` Bellman optimizer that enumerates the physical subsets of target Prize positions, Arc Phone top observations and legal optional swaps, and the best final Peonia selection.

The regression compares both models for n=3..7, q=1..3 and a=0..4 (**75 exact configurations**). The goal is joint acquisition of every target, so the labels of the distinct targets can be symmetrically exchanged inside the physical oracle.

## Limitations

Every target is assumed certainly Prized, and the deck contains only inert filler. Sufficient expendable hand cards are available for all Peonia replacement payments. No Trekking Shoes, additional draw, recovery or second Supporter is allowed. Opponent locks, Prize taking, changing turn horizons and targets with different game-state values are not modeled.

The main lesson is that a positional search can fail a *conjunctive* recovery objective because the downstream acquisition effect has its own cardinality budget. This is closely related to multi-Prized collapse and connector contention, but quantified for actual Arc Phone and Peonia text.
