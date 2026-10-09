# Prize-origin hand identity remains useful after acquisition

## Question

If an opponent takes a face-down Prize and declines an optional before-hand effect, can later public hand-card observations reveal information about the prior Prize identity and correlated deck top?

Yes. The original pending Prize must be retained as a **latent, labeled hand card** in the observer model. The existing immediate projection to top/Prize beliefs loses its correlation with that acquired card.

Implementation: `tools/prize_acquired_hand_reveal.py`  
Regression: `results/prize_acquired_hand_reveal/reproduce.py`

## Rule and information basis

The supplied Advanced Player's Rulebook E-31 identifies a before-hand timing window. A declined Chansey Lucky Bonus option sends the previously face-down Prize to private hand. Later effects could reveal a randomly chosen card from hand. A revealed card of the same name is not necessarily the original Prize copy, so inference must account for which physical hand copy was sampled without assuming its origin became visible.

The module composes a public-decline Bayesian update from `prize_optional_trigger_signal.py` with the physical Prize-to-hand transition in `before_hand_prize_executor.py`. It reuses `LatentPrivateTargetJointBelief` to retain the joint distribution of deck top, remaining Prize slots, and the specific Prize-derived hand card. The card keeps its physical `CardInstance` ID.

## Exact three-card-hand witness

Reuse the four-world prior and use-propensity assumptions from [optional Prize-trigger signaling](../prize_optional_trigger_signal/): P(use Lucky Bonus | Chansey)=3/5, P(use | other)=0. The observer initially has P(Chansey)=1/2, P(top S)=1/2. After watching the player decline, these become P(tagged Prize card is Chansey)=2/7, P(top S)=13/35.

Now assume the other two cards in hand are **one known Chansey and one known other card**, and a card is selected uniformly at random and publicly revealed without being removed. The exact physical test world has the Prize-derived card actually Chansey, but the opponent is uncertain.

| Randomly revealed card | P(tagged Prize card is Chansey) | P(deck top is S) |
| --- | --- | --- |
| No reveal, only decline | 2/7 = 28.57% | 13/35 = 37.14% |
| Chansey | 4/9 = 44.44% | 7/15 = 46.67% |
| Other | 1/6 = 16.67% | 3/10 = 30.00% |

The observation probability depends on the latent Prize origin: if the tagged Prize is Chansey, there are two Chansey among three hand cards; if it is other, there is only one. The correct observer update is a mixture across both cases.

A copy of Chansey that was already in hand can be the card actually revealed. That public observation changes the opponent's posterior about the **other**, originally Prized Chansey without revealing its physical ID. An implementation that forgets the Prize origin upon entering hand cannot make this update.

## Regression and scope

An independent rational Bayes oracle enumerates all four original worlds, applies the decline and random-reveal likelihood, and checks the exact fractions above. Physical invariants include the Prize-derived card's stable identity, its hand destination, no physical movement for a non-removing reveal, and per-card-class conservation. The test rejects inconsistent known hand contents.

This is a controlled information model, not a claim that every card-reveal effect randomly selects a hand card. A specific card must supply such a public random-hand reveal in a fully fledged game simulator, and its source-specific conditions must be checked. The witness assumes other-hand composition is known and the whole hand is materialized. Unknown other hand cards, public hand changes, effect timing, and repeated reveals require an extended joint hand composition model.
