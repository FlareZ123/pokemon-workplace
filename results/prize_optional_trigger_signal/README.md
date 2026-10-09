# Optional Prize-trigger decisions reveal hidden information

## Question

When a player takes a face-down Prize and has an optional E-31 effect that could put the card directly into play, does publicly **declining** that effect change the opponent's knowledge of the unseen card and correlated hidden zones?

Yes, **conditional on an assumed player choice policy**. A decision made with private information is an observation. The posterior is policy-dependent and is not a universal optimal-play claim.

Implementation: `tools/prize_optional_trigger_signal.py`
Regression: `results/prize_optional_trigger_signal/reproduce.py`

## Rule and implementation basis

The supplied Advanced Player's Rulebook E-31 locates relevant effects between seeing the previously face-down Prize and moving it to hand. Chansey (`sv3pt5-113`, Lucky Bonus) can go directly onto the Bench when it is not full, and may gain an extra Prize after a heads flip. An activated Chansey is publicly visible in play, while a declined Chansey goes to the private hand.

Existing modules `prize_pending_take`, `pending_prize_identity_belief`, and `before_hand_prize_executor` already represent the pending timing window, observer-specific latent identity, and physical self-to-Bench routing. This result adds the **decision-likelihood update before marginalizing pending identity**.

## Exact four-world witness

| Deck top | Pending Prize | Prior |
| --- | --- | ---: |
| S | Chansey C | 2/5 |
| F | Chansey C | 1/10 |
| S | Other O | 1/10 |
| F | Other O | 2/5 |

The actor privately sees C in the physical-world witness, while the opponent starts at `P(C)=1/2` and `P(top=S)=1/2`. Assume Bench space is available, `P(use | C)=3/5`, and `P(use | O)=0` because O lacks this trigger.

- Public use has probability `3/10` and reveals C, so `P(top=S | use)=4/5=80%`.
- Public decline has probability `7/10`, leaving `P(top=S | decline)=13/35=37.142857%` and `P(C | decline)=2/7=28.571429%`.

The exact fraction oracle in the reproducer enumerates all four states independently of the update implementation.

## Validation

The integration composes a Bayesian update on the joint top/remaining-Prize/pending belief, the existing direct E-31 physical transaction, and the destination-visibility update. It checks positive posterior probability for the exact material world and exact physical-card conservation.

Regression covers public activation, hidden-hand decline, policy-impossible use, invalid/missing policy probabilities, Bench-full illegality, pending-queue exhaustion, and the exact destination instance.

The result is conditional on an explicit action policy. When the Bench is full or the effect is otherwise unavailable, the relevant action probability is zero. Private strategic incentives or unknown board conditions require further latent variables in that policy. Declining alone is not proof that no Chansey was taken.

## Scope

One pending face-down Prize, direct Bench/attachment families, and an externally provided behavioral policy. The card physically moving into play is represented by its exact ledger instance; full board geometry, multiple simultaneous Prize awards, nested extra-Prize settlement, Item-play resolution, and inference from the order chosen between multiple pending cards remain separate.

A useful next extension is signaling from the owner's selected order among two simultaneously taken privately identified Prize cards, particularly when one choice triggers nested Prize awards.
