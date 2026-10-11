# Substituting one Trekking Shoes for one Arc Phone in known-Prized rescue

## Exact result

Under the same controlled K1 state as [shoes-free Arc reconnaissance](../arc_peonia_shoes_free/), one usable **Trekking Shoes** can take the place of the *last observing Arc Phone*. This preserves the chance of rescuing a singleton known to be among n face-down Prize positions.

Let a denote usable Arc Phones (up to four), s usable Trekking Shoes (up to four). The deck contains only inert filler F, the player holds one Peonia and an expendable F for its replacement payment, and only one valuable target T is uniformly located among the n Prizes. Exactly one Peonia can be played.

The optimal recovery probability is

\`P(n,a,s) = min[n, 3 + e(a,s)] / n\`,

where

- \`e(a,0) = max(0,a-1)\`;
- \`e(0,s) = 0\`;
- \`e(a,s) = a\` when \`a>=1\` and \`s>=1\`.

Consequently, the first Shoes contributes one additional effective Prize inspection whenever at least one Arc is available, while a second or later Shoes contributes **zero marginal target-recovery probability** in this deliberately filler-only deck state.

## Six-Prize exact table

| Arc Phone copies a | No Shoes | At least one Shoes |
|---:|---:|---:|
| 0 | 1/2 | 1/2 |
| 1 | 1/2 | 2/3 |
| 2 | 2/3 | 5/6 |
| 3 | 5/6 | 1 |
| 4 | 1 | 1 |

At a four-Item budget, **three Arc Phone and one Trekking Shoes** guarantee retrieval just as four Arc Phone do. With two Arc Phone and two Shoes, the optimum is only 5/6. Item count alone therefore does not determine Prize coverage.

## Why Shoes changes the frontier

Arc Phone (\`swsh11-152\`) inspects the deck top before optionally exchanging that card with a face-down Prize. The next Arc Phone can observe the displaced Prize. Trekking Shoes (\`swsh10-156\`) also inspects the top but can **take it into hand**, so a final Arc exchange can be followed by Shoes to retrieve its formerly unknown Prize. This allows a consecutive Arc chain to expose a distinct Prize with *every* Arc played, with Shoes consuming the last one at the endpoint.

If Shoes' observed top is filler F, its alternative discard-then-draw action only reaches more F in this model. It yields no additional chance of locating a T that is known to reside in the Prizes. Hence only the top-taking branch matters for this exact result.

Peonia (\`swsh6-149\`) covers up to three other positions. Every extra rescued Prize position beyond those three requires an Arc exchange. Without Shoes, identifying the last exchange requires another Arc; with Shoes, the last exchange's top card can instead be taken directly. This bounds coverage at \`3+max(0,a-1)\` without Shoes or \`3+a\` with Shoes, capped by n.

## Independent exhaustive policy test

\`tools/arc_peonia_shoes_comparison.py\` explores each physically labeled target position with an exact \`Fraction\` recursion, allowing Peonia at any stage and both Arc top-observation and optional swap decisions. It also allows playing Shoes at any stage. Every action is conditioned only on what the player can observe. It verifies the formula for n=1..6, a=0..4, s=0..4: **150 exact configurations**.

Run \`python tools/arc_peonia_shoes_comparison.py\`. The corresponding Windows CI workflow checks both this result and the parent shoes-free result.

## Limitations

The proof and policy depend on a target certainly Prized, a deck known to be entirely filler, freely available resources, and a pre-existing legal hand-payment option. Additional valuable deck cards make Shoes' discard/draw mode matter, changing the results. The setup omits realistic search/draw access, one-Supporter contention with other Supporters, opposing disruption, and genuine match utility. Equivalence here is **target-recovery probability**, not total card value or deck-slot equivalence.

A next step is an item-cost optimization comparing the combinations under a realistic distribution of natural opening and Prize access, and including the opportunity cost of using Shoes as a draw card.
