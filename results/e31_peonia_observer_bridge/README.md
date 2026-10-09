# Observer-relative belief through Peonia-seeded E-31 Prize chains

## Question

Can a physically known Peonia placement remain unknown to the opponent through a subsequent simultaneous Prize award, while public E-31 Item play and nested Jirachi resolution update the observers correctly?

Yes, in an exact controlled four-Prize witness whose card truth and two observer beliefs are advanced together.

Implementation: [tools/e31_peonia_observer_bridge.py](../../tools/e31_peonia_observer_bridge.py)  
CI: [GitHub Actions run 37976525956](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37976525956), passed.

## Source and existing implementations

The official Japanese Q&A for Peonia says the replacement Prize cards may be placed in a selected order and do not need shuffling:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B7%E3%83%A3%E3%82%AF%E3%83%A4&regulation_faq_main_item1=all

Related physical source: [Peonia-seeded Prize pipeline](../e31_peonia_seed_execution/).

The observer transition reuses:

- `ObserverTopPrizeBeliefs` and `PrizePositionBelief` for private position posteriors;
- `stage_prize_batch_with_latent_observers` for preserving pending sibling identities as latent variables;
- `resolve_pending_instance_visibility` for public and private observations of a particular pending card;
- `prepend_additional_pending_for_observers` for the nested Greedy/Jirachi bonus Prize chain;
- `project_completed_batch` for the post-resolution observer state;
- physical `PrizePendingTakeState`, `PendingPrizeBatchOrder`, `before_hand_prize_executor`, Jirachi's exact Bench transition and Dream Ball's exact typed target transition.

## Controlled hidden-information state

Peonia physically places three named cards face down into Prize positions 0,1,2:

`(Greedy Dice, Dream Ball, Jirachi ◇, filler)`.

The **actor** knows all three positions. The opponent in this controlled information state knows that Greedy Dice, Dream Ball, and Jirachi occupy the first three positions but does not know their permutation. The opponent's belief over the six possible orders is uniform, corresponding to the actor using a privately randomized ordering policy before physically placing them. No face-down shuffle is required by Peonia.

This is a conservative observer information model in one sense: the opponent usually has less information about the specific cards in the hand selected by Peonia. It is also conditional on the actor using an unpredictable placement policy, because publicly known deterministic placement would reveal the positions through policy inference.

The actor and opponent have equal *Prized composition*. Their positional beliefs differ.

| Information checkpoint | Actor P(Jirachi at selected future extra-Prize position) | Opponent P(Jirachi at that position) |
| --- | ---: | ---: |
| Immediately after Peonia's placement | 100% | 33.333333% at original slot 2 |
| After the two-Prize award stages positions 0 and 1, before effects are played | 100% | 33.333333% at remaining slot 0 |
| Greedy Dice is played publicly from its Prize-origin pending Item slot | 100% | 50% |
| Greedy heads, Jirachi is subsequently revealed entering play | 100% | 100% after the revelation |
| Greedy tails, Dream Ball is subsequently revealed and played | 100% | 100% after the revelation |

At the second checkpoint the actor has seen the two awarded cards, while the opponent has not yet seen their faces. The table concerns **Jirachi's remaining physical position**, and the card slots are relabeled after the first two have left the Prize zone.

## Why the opponent's probability changes

Initially, under the controlled six-permutation policy, Jirachi has equal probability of occupying any of the three planted positions.

The opponent sees a two-Prize award remove the first two slots but learns none of their identities yet. Their posterior that the remaining planted position is Jirachi is still one third.

When the player reveals Greedy Dice to play its Prize-origin Item effect, the opponent can eliminate all placements where the first selected slot was not Greedy Dice. Among the remaining two possible arrangements, Jirachi occupies either the second selected slot or the remaining Prize slot, each with probability one half.

On heads, a Jirachi revealed by the additional Prize effect identifies the remaining planted Prize and closes that uncertainty. On tails, a publicly played Dream Ball identifies the second original Prize slot and reveals by elimination that the remaining planted Prize is Jirachi.

The actor did not need to infer any of this; their placement information had already fixed the exact position.

## Physical branches and validation

The regression runs both Greedy Dice coin outcomes from the same physical seeded packet. The physical card state and latent pending-belief state advance together, including the temporary `resolving_trainer` state for Greedy Dice and nested extra-Prize work on heads.

- Heads: Jirachi is taken as an additional Prize, enters the last Bench slot, stages and takes the remaining filler Prize, then Dream Ball moves to hand after the Item finishes. Final Prize count taken: four. Both observers have zero remaining Prize positions.
- Tails: Greedy Dice finishes without a bonus Prize and Dream Ball searches Tapu Lele-GX from the deck onto the Bench. Final Prize count taken: two. After Dream Ball is shown, both observers know the exact two remaining Prize identities and positions, Jirachi then filler.

The conservation assertion compares every card-class total against the pre-Peonia physical state. The physical Prize count, pending order, and observer positional dimensions are checked in both branches.

## Representation consequence

A simulator may need to distinguish the **actor's privileged action information** from the **opponent's belief about what the actor knows**, especially when physical slots are chosen while face down. Conditional on card placement policy, visible actions can also reveal information about other Prize cards that were not directly turned face up.

An E-31 search policy that conditions both players on the true selected Prize identities before they are publicly exposed will leak information too early.

## Limits

- The six-permutation opponent prior is a specified behavioral assumption, not an empirical opponent model. Different Peonia placement policies produce different posterior probabilities.
- The effect-order extrapolation from the official Chansey + Dream Ball mixed-E-31 ruling to Greedy Dice + Dream Ball remains an unresolved source question.
- The observer wrapper handles this exact two-sibling prize fragment. General source-aware Item/trainer transactions and arbitrary nested simultaneous awards need a larger unified state adapter.
- The play state, hand access, opponent's attack response, and probability of acquiring the Peonia packet are supplied rather than simulated.

## Reproduction

`python tools/e31_peonia_observer_bridge.py`

The same command is part of `.github/workflows/validate-e31-greedy-order-option.yml`.
