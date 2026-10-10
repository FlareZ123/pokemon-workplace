# Opposing Iono, N and Marnie: draw-zone mechanics change the best disruption

## Question

Three legal paper Expanded Supporter effects can replace both players' hands, but they interact differently with a Beheeyem loop and newly taken Prize cards.

- **Iono (sv2-185):** each player shuffles their hand and puts it **at the bottom of their deck**. If either player bottomed a card, each player draws according to **their remaining Prize count**.
- **N (bw3-92):** each player shuffles their hand **into their deck**, then draws according to **their remaining Prize count**.
- **Marnie (swsh1-169):** each player shuffles their hand and puts it **at the bottom of their deck**. If the draw gate applies, the player of Marnie draws five, while the **opponent draws four**, regardless of remaining Prizes.

The distinction is particularly important after Beheeyem's Mysterious Noise: the attack has Item-locking text but does not prohibit an opposing Supporter play. This experiment asks which of these three replies makes acquiring a second Beheeyem+Triple Acceleration Energy packet hardest under an otherwise fixed conditional setup.

## Physically conserved game state

As in the prior [Iono model](../beheeyem_iono_prize/), the board starts with two evolution-ready Elgyem and an anchor Basic already present. The six-card residual T2 hand and six-Prize set are sampled from 57 residual physical cards. The first Beheeyem+TAE packet can be directly held, or a one-copy tutor can search one missing category with actual target restriction and neutral filler discard payment.

The first attack returns Beheeyem, attached TAE and underlying Elgyem to the randomized deck. A direct first packet leaves **48 cards** in deck. A T2 tutor rescue leaves **47** because searching removed one packet card before the attack.

The first attack is assumed to award **r=0,1,2 Prizes** as a conditional, exogenous KO outcome; the player picks r uniformly random original face-down Prize positions, adding those cards to hand. On the opponent's turn, one of the three Supporters replaces the entire surviving hand. The player then has d stipulated T3 additional blind draws, and the solver checks the next Beheeyem+TAE packet.

The actual distinction among the three sources is the physical location of the hand and the draw count:

| Opposing Supporter | Fate of the surviving hand (including earned Prizes) | Fresh cards accessible by Iono/N/Marnie + d T3 draws |
| --- | --- | --- |
| Iono | Shuffled separately, placed on **bottom** of deck | **6-r+d** from the original randomized 47/48 top deck |
| N | Shuffled **throughout** the whole deck | **6-r+d** from a larger deck containing returned hand cards |
| Marnie | Shuffled separately, placed on **bottom** of deck | **4+d** from the original randomized 47/48 top deck |

The player is the **opponent** of the Marnie player, so four cards is the correct Marnie draw quota. Returned-hand cards are still searchable on T3 if the player newly draws a tutor, even when bottomed, but they cannot appear in the short top-card draws themselves.

## Results: four Beheeyem, four TAE, one Computer Search

One additional T3 natural draw (d=1). Entries are joint T2-and-T3 packet access conditional on the three-Basic starting board and the given first-attack Prize reward.

| Prizes awarded by first attack | Opposing Iono | Opposing N | Opposing Marnie |
| ---: | ---: | ---: | ---: |
| 0 | 3.675774% | 3.475483% | **2.019569%** |
| 1 | 2.820953% | 2.647861% | **2.019569%** |
| 2 | 2.019569% | **1.881457%** | 2.019569% |

For **0 or 1 awarded Prize**, Marnie produces the lowest next-packet incidence among the three. With **2 awarded Prizes**, N produces the lowest incidence. The ranking therefore changes as the visible Prize race progresses, purely through the Supporters' card-destination and draw-count rules.

Marnie's modeled packet-access rate is **independent of r**. It bottom-decks the hand and then draws four regardless of remaining Prizes; the identities awarded from Prizes cannot appear in the original top 48/47 cards before the new short draw. This exact invariance is model-specific and will fail if some other card effect later reshuffles or accesses the bottomed resources.

By contrast, N and Iono draw one fewer card per Prize taken. N's whole-deck shuffle also dilutes the recycled Beheeyem+TAE packet with the previous hand. In the overall distribution this makes N slightly less helpful to the Beheeyem player than Iono when they draw the same number of cards.

## Exhaustive finite-scope ordering

The exact engine enumerates **1,152 configurations** of B=1–4 Beheeyem, TAE=1–4, four one-copy tutor modes, d=0–5 extra T3 cards and r=0–2 Prizes awarded.

Within this finite family:

- **Iono is always at least as favorable to the Beheeyem player's next-packet access as N.**
- For r=0 or r=1, **N has a higher next-packet rate than Marnie** in all 384 relevant configurations for each r.
- For r=2, **N has a lower next-packet rate than Marnie** in all 384 configurations.
- Marnie exactly matches Iono's r=2 packet rate for all r under the shared B/TAE/d/tutor parameters, because both draw four cards from the same randomized top-deck population.

Thus, if an opponent can choose among the three and only seeks to minimize this narrowly defined next-packet incidence using public knowledge of our r earned Prizes, the finite-model choice is **Marnie at r=0 or1** and **N at r=2**. This is a constrained opponent-response decision rule, **not** a recommendation about full-game match win probability. The opponent might prefer a different card to gain their own resources, take Prizes, gust or establish a stronger lock.

## Why N and Iono diverge despite equal hand-size draws

Although N and Iono both draw by remaining Prizes, N reintroduces every surviving hand card into the randomized deck **before** sampling new cards. This can include spare B/TAE copies and the physical tutor, improving some specific configurations. It also reintroduces numerous neutral filler cards, diluting the known recycled attacker packet. Iono keeps those prior hand cards away from the top draw, so its fresh top sample is more concentrated on the recycled attacker and TAE in the current controlled state.

The 1,152-case exact census finds Iono at least as favorable to the Beheeyem player as N in the aggregate. An additional K1 state-by-state analysis could investigate configurations where N locally yields greater next-packet access, just as Prize pickups sometimes outperform deck draws within known-Prize states.

## Evidence and reproduction

- The local card pool provides current-effect English text for **N bw3-92**, **Iono sv2-185**, and **Marnie swsh1-169**. The Advanced Player's Rulebook governs playable Supporter timing and partial effect resolution.
- [Exact engine](../../tools/beheeyem_supporter_reset.py) physically composes 47/48-card post-attack decks with the surviving hand and all possible six-Prize arrangements. It computes the three replacement-hand distributions using exact rational hypergeometric probabilities.
- [Deterministic regression](reproduce.py) verifies the 1,152 scenario grid (3,456 Supporter rates), matches the earlier Iono engine, checks Marnie's Prize-invariance, full-card conservation and Ultra Ball/Guzma & Hala target-category symmetry.
- [Independent physical simulation](monte_carlo.py) replays the actual shuffled card arrays, puts cards on the bottom for Iono or Marnie, or fully reshuffles for N, and samples the correct replacement-hand counts. Five representative cases use 200,000 Monte Carlo trials each.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-supporter-reset.yml) runs the exact and simulation checks.

## Scope

The research conditions on a previously staged board, a first attack that meets its prerequisites, a specific exogenous number of T2 Prizes, an opposing hand-reset Supporter being playable, and d additional T3 draws being available. Every neutral filler is assumed discardable. Opponent strategy, attacker positioning, future attack legality, realistic damage/KO conditions and full-board resource contention are outside the model.

The comparison is useful as an **exact adversarial test case** for future tactical search or deck optimization. It shows that grouping all hand-shuffling Supporters under a generic disruption edge would erase an observable, sometimes decision-changing difference in deck-top distribution and draw quotas.
