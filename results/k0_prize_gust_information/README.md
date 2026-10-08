# Knowing what is Prized can change whether to spend Boss's Orders

## Question

A player who has searched their deck can infer exactly how many Boss's Orders copies are in their face-down Prize cards. Before searching, they know the number in their hand and how many copies their decklist contains, but the unseen copies remain distributed between deck and Prizes. Does that extra K1 information improve tactical gust decisions, especially when taking Prizes might recover another Boss?

## Representation

This research builds on `results/prize_refill_gust/`, which draws an opening seven-card hand and six face-down Prizes from an abstract 60-card deck containing 0..4 Boss-like cards. The remaining cards are inert fillers. Each attacker turn draws one card. An attack KOs any selected target in one hit, yielding 1/2/3 Prize cards, possibly recovering further Boss cards into hand. The defender chooses worst-case promotions after KOs. The opposing board is established and does not replenish.

The K1 model `tools/prize_refill_gust.py` chooses actions with the number of Boss cards in Prizes and deck known to the attacker. It knows Prize **composition**, while exact Prize positions stay random.

The new K0 model `tools/k0_prize_gust_information.py` keeps instead this posterior statistic:

`(Boss in hand, total Boss unseen, deck size, Prize zone size)`.

At K0, the unseen Boss cards are exchangeable across all `deck size + Prize zone size` positions. A normal draw obtains a Boss with probability `total unseen Boss / (deck size + Prize zone size)`. After taking r Prizes, the number of Boss copies drawn follows the matching hypergeometric law across the unseen pool. The player observes cards moved to hand, updates unseen counts, and chooses later actions adaptively. At the moment of choosing their promotion, the defending player sees the public Prize count but not the identities of these privately obtained cards.

This is a deliberately simplified information experiment. Full real-game information asymmetry is more complex: the opponent generally does not know the player's exact starting hand, and strategically chosen cards can signal hidden information. The K1 comparator remains a perfect-zone-composition benchmark rather than a complete two-observer Bayesian game.

## Exact full-deck results

All **146** structural one-hit six-Prize opposing boards are tested with 0 through 4 Boss copies in the abstract deck, both with actual Prize recovery and a counterfactual that suppresses Prize-recovered Boss usage.

With normal Prize recovery:

| Total Boss copies | Boards where K1 improves expected attacks | Improvement on each affected board |
| ---: | ---: | ---: |
| 0 | 0 / 146 | 0 |
| 1 | 0 / 146 | 0 |
| 2 | 4 / 146 | 4/885 = 0.004520 attacks |
| 3 | 4 / 146 | 128/8555 = 0.014962 attacks |
| 4 | 4 / 146 | 5008/162545 = 0.030810 attacks |

The same four Active/Bench prize-value geometries are affected at K=2,3,4:

- Active 2, Bench 1/1/3/3;
- Active 2, Bench 1/1/1/3/3;
- Active 2, Bench 1/1/2/3/3;
- Active 2, Bench 1/1/3/3/3.

The numbers are exact rational expectations over uniformly random abstract opening hands, Prize positions, and natural draws. They are **not live-game population frequencies**, and should not be extrapolated directly to Boss deck counts.

When Prize-recovered gusts are disabled as a controlled counterfactual, K1 provides **zero** expected attack-count advantage over K0 on every one of the 146 board geometries and all K from zero through four. That is a striking model-specific interaction between gaining exact Prize composition information and the ability to later acquire Prized Boss cards.

## A concrete strategy switch

Consider Active **2 Prizes**, Bench **1,1,3,3 Prizes**, after the initial turn's natural draw, with one Boss already in hand and one additional Boss still unseen. The draw pile contains 46 cards and the Prize zone six.

At K0, the player's exact expected attack-turn values for the immediate options are:

| Immediate action | K0 optimal continuation |
| --- | ---: |
| Attack the current two-Prize Active without spending Boss | 3 attacks |
| Gust a three-Prize Benched target | 99/26 = 3.807692 attacks |
| Gust a one-Prize Benched target | 4 attacks |

The K0 policy therefore attacks the current Active for two Prizes and keeps Boss.

At K1, suppose the unseen Boss is **known to be Prized**, with no other Boss in the draw pile. Gusting a three-Prize target immediately changes the distribution of which future turns can recover the second Boss; the optimal expected attack count becomes **17/6 = 2.833333**, better than attacking the Active for 3.

Conversely, when K1 instead shows that the unseen Boss remains in the deck and none is Prized, the current-Active attack gives an optimum of 3. The informed player's correct opening attack is therefore *conditional on Prize composition*.

The gain in the full-deal expectation is small because this exact decision-sensitive state is reached relatively rarely.

## Validation

`results/k0_prize_gust_information/reproduce.py` performs **1,460 exact K0/K1 comparisons**: 146 board classes × 5 Boss-copy counts × two Prize-refill policies. It checks the precise four affected boards and three fractions above, plus the absence of information benefit when Prize-refilled Boss cards cannot be used.

For independent verification, a second oracle explicitly enumerates unknown Prize-zone Boss composition, then performs the conditional deck draw or Prize taking within each composition. The main K0 kernel instead marginalizes directly over the combined unseen pool. Both algorithms agree on **54** small-state scenarios with independent hand, unseen-copy, board, and refill configurations.

The local decision values are separately asserted, including both K1 continuations. All calculations use Python's `Fraction`, with exact combinatorial arithmetic.

Run from repository root: `python results/k0_prize_gust_information/reproduce.py`.

## Implication and further research

A deck search can have strategic information value even when it does not acquire a card: it changes the policy for spending an already-held tactical Supporter. The benefit can depend on the existence of a *different action*, Prize taking, that moves previously hidden cards into hand.

This toy experiment finds rare but measurable cases where exact Prize composition changes the optimal first attack. A realistic extension should integrate actual K0 search actions and their costs (for example Quick Ball versus delaying an attack), distinguish what each player knows, and include search-target access, supporter contention, and future opponent turns before recommending deck changes.
