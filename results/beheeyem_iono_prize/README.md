# Opposing Iono reverses the short-term packet-access benefit of earning Prizes

## Question

Taking Prize cards after an initial Beheeyem Mysterious Noise attack can add Beheeyem, Triple Acceleration Energy, a tutor or discard-payment filler directly to the player's hand. The [Prize-awarded packet model](../beheeyem_prize_packet/) demonstrated that this improves next-turn packet availability when the hand is retained.

What if the opponent plays **Iono** during their reply, shuffling the newly acquired cards and the rest of the hand to the **bottom of the player's deck** and requiring a fresh draw according to **remaining** Prize cards?

This is a direct example of how opponent hand disruption, Prize progress and resource renewal interact. It is especially relevant because Beheeyem's Mysterious Noise prevents the opponent playing **Item** cards during their next turn, while Iono is a **Supporter** and is therefore outside that particular restriction.

## Card text and scenario

The local English database gives Iono (sv2-185) this effect:

> Each player shuffles their hand and puts it on the bottom of their deck. If either player put any cards on the bottom of their deck in this way, each player draws a card for each of their remaining Prize cards.

This study assumes that an opponent Iono play is otherwise legally possible and that the draw condition is satisfied. It does not model how the opponent obtained Iono, its Supporter quota, or the effects of the opponent's own hand reset.

The Beheeyem setup is the same conditioned 60-card physical model as the previous studies. Two mature Elgyem and an anchor Basic are already on board. Six cards form the T2 residual hand, six are random Prizes, and 45 remain in deck. The first Beheeyem+TAE attack can be direct from hand, or rescued by a held physically accessible one-copy tutor at its actual target and filler discard cost.

After first attack, Beheeyem, TAE and its underlying Elgyem return to the shuffled deck, making **48** cards on direct attack or **47** on tutor-rescued attack. An exogenous successful KO awards **r in 0,1,2 random original Prize cards** to hand.

The opponent's subsequent Iono puts every surviving hand card, **including the newly taken Prizes**, at the bottom of the deck. Since the player has **6-r remaining Prizes**, Iono draws exactly **6-r** fresh top-deck cards. The player then draws d more cards naturally or by a stipulated extra blind draw. In these short horizons, the total **6-r+d** drawn cards come from the original shuffled 48-/47-card top deck and never reach the newly bottomed hand cards.

The returned hand identities are still in the deck and may be searched with a newly drawn tutor, but both packet categories are independently represented in the original shuffled deck by the recycled attack packet. Consequently, testing the B/TAE/tutor/filler composition of those top-deck draws is sufficient.

## Main reversal: more Prize rewards, fewer immediate packet outs after Iono

Four Beheeyem, four TAE, one Computer Search and d=1 T3 natural draw. All figures are unconditional **within the fixed three-Basic established-board model**, and assume a first attack earning the given r Prizes if it occurs.

| Prizes awarded by first attack | Two-packet access if hand survives | Two-packet access after opposing Iono |
| ---: | ---: | ---: |
| 0 | 0.662553% | **3.675774%** |
| 1 | 1.125764% | **2.820953%** |
| 2 | 1.679597% | **2.019569%** |

Without a hand reset, first-attack Prize rewards **increase** packet access because the newly awarded cards remain in hand. After Iono, an extra earned Prize **decreases** packet access in this model because the newly received card is immediately sent to the bottom and the player draws one fewer new card under Iono's remaining-Prize rule.

For the same B4/TAE4/Computer Search setup with no extra T3 draw (d=0), the opposing-Iono rates are 2.820953%, 2.019569% and 1.284008% for r=0,1,2 respectively.

This inversion is **about future hand-resource supply**, not the value of earning Prizes overall. Progress toward taking the sixth Prize remains a vital winning axis. Nor does the model conclude that an opposing Iono is globally beneficial. It isolates one narrow reacquisition event and ignores the opponent's other strategic options.

## Why Iono sometimes helps the player whose hand was disrupted

In this deliberately draw-starved model, opponent Iono raises aggregate two-packet access relative to the no-Iono baseline in every tested copy-count/tutor/draw/reward configuration. It replaces a small and often incomplete residual T2 hand with a large fresh draw from the shuffled deck containing the returned Beheeyem and TAE.

The effect is particularly pronounced with a singleton B and TAE, where a one-card T3 natural draw cannot supply both types unless the held tutor or other resource survives. With opponent Iono, a fresh four-to-six-card sample from the deck can itself supply both categories.

This finite model observes **1,152** configurations: 16 B/TAE copy pairs, four one-copy tutors, d=0–5, and r=0–2. Iono's packet-access rate is never below the no-Iono rate in that grid. That is an empirical exact-census observation under the isolated model, **not** a general claim about actual opponent hand disruption, other game objectives or full deck consistency.

## Exact identity and probability accounting

The important physical distinction is **bottom-of-deck placement**. Iono does not remove the newly acquired cards from the game. In this study, they become unreachable through the short sequence of top draws, although they remain eligible targets for a search through the deck if a tutor is subsequently drawn.

For each T2 hand and six-Prize composition, the solver:

1. Checks a legal first packet through direct access or a one-copy tutor rescue.
2. Constructs the correct 48- or 47-card post-attack top deck, with returned packet card identities.
3. Applies Iono's 6-r top-card draw and the next d draws to this deck.
4. Evaluates whether the resulting new hand contains both B and TAE or one category plus a newly drawn tutor and sufficient disposable filler.
5. Weights all physical hand and Prize configurations using exact rational multivariate hypergeometric probabilities.

For fixed initial deck configuration, the Iono result depends on r only through the **effective blind draw budget 6-r+d**. The identity of the r random Prize cards does not change that draw's top-deck contents because those awarded cards are bottomed before drawing.

Hence a mechanically useful invariant is that the rate at (d,r) equals the rate at (d-1,r-1) whenever both pairs are within scope and d,r are positive. Both have the same effective top-deck draw count.

## Reproducibility and limitations

- [Exact Iono engine](../../tools/beheeyem_iono_prize.py) enumerates the physical T2/Prize configurations and calls the exact reusable packet completion kernel for the **6-r+d** top draws.
- [Regression](reproduce.py) checks all 1,152 configurations, monotonicity in r, the exact draw-offset equality, symmetry of Ultra Ball versus Guzma & Hala under swapped B/T counts, and the no-Iono comparison.
- [Independent simulation](monte_carlo.py) physically builds the 60-card conditioned game, searches when applicable, returns the attack packet, randomly awards Prize identities, **shuffles and moves the whole hand to the bottom**, then performs the Iono draw and T3 draw. Four configurations each use 200,000 independently seeded shuffles.
- [GitHub Actions workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-iono-prize.yml) runs both checks.

The model conditions on successful initial board staging, enough evolution/attachment/pivot actions, freely available d extra draws, neutral filler discardability and an exogenously chosen opponent Iono reply. It does not account for whether the Iono player is strategically incentivized to play that Supporter, for actual KO rates or for the distribution of subsequent attack targets. It also ignores any other player deck-search, shuffling or bottom-card retrieval between Iono and the next attack.

A full two-player model should compare Iono against other opponent responses, include visible Prize-taking information, and make the opponent's action choice contingent on the first player's board and resources. This result supplies an exact reference for that extension.
