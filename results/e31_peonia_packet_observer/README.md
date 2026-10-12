# Peonia packet choices leak position knowledge before card revelation

## Question

A player can use Peonia to replace face-down Prize cards with a known Greedy Dice, Dream Ball and Jirachi ◇ packet. How does the **public selection of Prize positions** constrain the opponent's identity beliefs, even while the identities remain face down? Can the resulting posterior be handed to the existing exact-physical pending-Prize executor without contradicting card-instance truth?

This test composes [the conserved Peonia exchange](../e31_peonia_seed_execution/), [the position/top posterior kernel](../prize_position_choice_signaling/), and [the physical pending-batch observer adapter](../prize_pending_batch_observer/). Code: [`tools/e31_peonia_packet_observer.py`](../../tools/e31_peonia_packet_observer.py). Reproducer: [`reproduce.py`](reproduce.py).

## Source and information assumptions

The Aichi 2026 runner-up list includes Peonia, although this particular three-card packet is **not** a claim about that tournament deck or its viability.

Peonia `swsh6-149` exchanges up to three selected face-down Prize cards for hand cards placed face down as Prizes. The official [Japanese Peonia Q&A](https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B7%E3%83%A3%E3%82%AF%E3%83%A4&regulation_faq_main_item1=all) establishes that returned cards need no shuffle and may be arranged at chosen positions. Greedy Dice `xy11-102`, Dream Ball `swsh7-146`, and Jirachi ◇ `sm7-97` use effects tied to being taken as face-down Prizes. Their existing physical two-branch witness is in [Peonia seeded execution](../e31_peonia_seed_execution/).

For this experiment **the actor randomly permutes the three known packet cards among positions 0, 1, 2**, with each of the six permutations equally likely. Position 3 contains unchanged filler. The opponent is assumed to know this packet *composition* and randomization policy, but cannot see the selected order. This is deliberately a **strong side-information assumption**; an ordinary opponent need not know that packet inventory. The actor privately knows the exact placement after choosing it.

The test uses the one realized physical placement `(Greedy, Dream, Jirachi, filler)`, which has nonzero probability under the randomized policy. It does not pretend that a player who deterministically always places the cards in that order would retain privacy from an opponent who knew that deterministic policy.

## Exact Bayesian result

The actor later takes two Prizes and, knowing their positions, always **chooses precisely the slots holding Greedy Dice and Dream Ball**. The observer sees the selected pair of physical positions `{0,1}`, before knowing the two card identities. Selection `{0,1}` occurs in two of six equiprobable packet permutations, so its prior probability is `1/3`.

| Belief or transition | Opponent probability |
| --- | ---: |
| Before observing selection, Jirachi ◇ at Prize position 2 | 1/3 |
| After observing `{0,1}`, Jirachi ◇ at position 2 | **1** |
| After observing `{0,1}`, Greedy Dice at position 0 | 1/2 |
| After observing `{0,1}`, Dream Ball at position 1 | 1/2 |
| If instead the actor chose a pair independently and uniformly, Jirachi at position 2 after observing `{0,1}` | 1/3 |

The selection partitions the six equiprobable worlds into three two-world classes. For the observed pair, the posterior keeps exactly `(Greedy, Dream, Jirachi)` and `(Dream, Greedy, Jirachi)`, each at `1/2`. Thus the action reveals `log2(3) ≈ 1.584963` bits of position information about the three-card permutation while one bit of Greedy/Dream ordering uncertainty remains. This is a **policy-conditioned inference**; it depends on the selection policy being common knowledge.

## Executable physical/observer bridge

The test executes the source-conserved Peonia state, creates actor and opponent `PrizePositionTopBelief` objects, applies the public choice likelihood, converts them to `ObserverTopPrizeBeliefs`, and calls `stage_prize_batch_with_latent_observers()` on **the real card-instance positions**.

Verified post-stage invariants:

- Original pending IDs remain `("greedy", "dream")`; the actor knows both identities while the opponent gives each ordering probability `1/2`.
- The physical remaining Prize at position 0 is `jirachi`, and the opponent posterior puts probability `1` on Jirachi being there.
- Adding the Greedy-heads extra Prize with `prepend_additional_prize_with_latent_observers(position=0)` produces queue `("jirachi", "greedy", "dream")`; the nested Jirachi blocks resolving the old Dream Ball sibling first.
- The pre-existing source-faithful physical executor independently checks the tails (two Prizes, Tapu Lele-GX entry) and heads (four Prizes, Jirachi ◇ entry) branches, giving conditional expectation **3** Prizes.

The shared pending-state adapter validates positive posterior probability on exact physical truth. It would reject an observer prior that excluded the physically realized Peonia order.

## Scope and limitations

This integrates observation, public choice signaling, physical staging, and **nested queue creation**. It does not yet integrate all later Jirachi/Greeedy/Dream card-effect destinations with dynamic observer beliefs in one atomic continuation. The independent complete physical executor verifies the two end outcomes, while the observer bridge verifies only the staged information and queue barrier.

The chosen two-Prize knockout, special three-card Peonia hand, one open Bench slot, and fair Greedy coin are supplied preconditions. They are not random-access probabilities measured in a real match. The rule allowing owner-chosen Greedy/Dream sibling resolution order remains an extrapolation from a directly confirmed Chansey/Dream ruling, as explained in the preceding results.

The result is an exact conditional information-state regression, **not evidence of competitive win rate or a recommended deck substitution**. The general modeling lesson is that a legal action selected using privately known Prize positions can expose those positions to an observer with an informative policy model. When measuring K1 or Peonia positional advantage, one must account for what the opponent infers from later public decisions.
