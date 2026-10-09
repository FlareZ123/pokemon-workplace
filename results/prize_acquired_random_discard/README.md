# Random hand discard retains uncertainty about a Prize card's origin

## Concrete card witness and research question

**Mars** (`sm5-128`, Ultra Prism) is Expanded legal in the bundled English card database and instructs its player to draw two cards and, if successful, discard one random card from their opponent's hand. The opponent's hand may contain a card previously taken as a face-down Prize.

A public random discard reveals the discarded card. When the affected hand contains multiple identical copies, its opponent cannot generally tell whether the discarded physical copy was the previously Prized one. The affected player, who handles their own physical hand, does know.

This investigation asks whether a joint hidden-zone representation can preserve **card class, physical origin, current zone, and observer-specific knowledge** through that event.

Implementation: `tools/prize_acquired_random_discard.py`  
Regression: `results/prize_acquired_random_discard/reproduce.py`

## Exact model

Begin with a pending Prize from a public decline of Chansey's optional Lucky Bonus, as in [Prize-origin hand beliefs](../prize_acquired_hand_reveal/). Keep the Prize-origin card tagged as a physical instance and a latent class correlated with the deck top. The other two hand cards are publicly assumed known by group: one Chansey (C) and one other (O).

A uniformly random discard from the three-card hand has two possible hidden origins: the tagged Prize card or one of the two already-present cards. The model conditions on the publicly discarded **group**. The affected hand owner additionally conditions on whether the **tagged physical copy** was selected. Every observer's posterior continues to record whether the Prize-origin instance survives in hand, together with the residual count of other-hand card groups.

| Public discard observation | P(tagged card was Chansey) | P(deck top S) | P(tagged card remains in hand) |
| --- | --- | --- | --- |
| Before the random discard, after Lucky Bonus decline | 2/7 = 28.57% | 13/35 = 37.14% | 100% |
| A Chansey was discarded | 4/9 = 44.44% | 7/15 = 46.67% | 7/9 = 77.78% |
| An other card was discarded | 1/6 = 16.67% | 3/10 = 30.00% | 7/12 = 58.33% |

These are exact posterior probabilities for the declared four-world prior and activation probabilities.

The same *public* Chansey discard observation is tested in two different exact worlds: first, a Chansey already in hand is discarded; second, the tagged Prize-derived Chansey itself is discarded. The observer who only sees the discard group has the **same posterior** in both cases. The hand owner can distinguish the events.

## Reproduction and scope

The regression uses an independent rational probability oracle to verify the posterior. It tests three materialized physical discard outcomes, including both Chansey-copy choices, and checks exact per-class conservation from the initial ledger. A false claimed hand composition is rejected.

The random-discard transition models the opponent-hand random selection body of a card such as Mars after any antecedent conditions have been met. It does not simulate Mars's prior two-card draw, its Supporter budget, or opponent lock states. The observation model requires fully materialized hand cards and fixed known other-hand group counts. A full game policy must verify source action legality and incorporate unknown or newly drawn hand cards.

The contribution illustrates a general principle: hidden-zone posterior state must retain **origin as a latent variable**, since public visibility of an identical card later does not identify which physical copy crossed a previous private information boundary.
