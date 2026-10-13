# Shadow Rider Mysterious Treasure payment sensitivity

## Question and source

This is a rules-grounded extension of the [Path + Iron Thorns counter frontier](../../shadow_rider_path_counter_frontier/). The published 2026 Aichi champion contains four **Mysterious Treasure**, eleven **Basic Psychic Energy**, and one **Radiant Eternatus**. Treasure print sm6-113 requires discarding a card from hand before searching for the Dragon-type Radiant.

The earlier model treated that discard as freely payable. This sensitivity test instead limits **Mysterious Treasure payment to a held Basic Psychic Energy**, discarding that Energy to unlock the Treasure route. Other Radiant routes remain available. This constrained policy supplies a specific sufficient class of payments: players may legally discard other cards and might rationally preserve Energy. Accordingly, the resulting success probability is a conservative restricted-access endpoint within the stated action model.

## Exact conditional results

The event is a Basic-valid opening seven, six hidden Prizes, and the first natural draw when going second, with opponent Active Iron Thorns ex and Path to the Peak already in play. Success requires an appropriate starting Active, an accessible Radiant, both Path and Thorns answers, and two Shadow Rider VMAX still in the deck. Forest Seal Stone searches at most one missing role. Other search, draw, locks, sequencing costs, future turns and opponent choices are excluded.

Every mix adds up to four total Canceling Cologne / Flutter Mane cards through the same sequential cuts as the parent: two Sky Field, one Dimension Valley, then Night Stretcher. The parent study conservatively validates all fifteen complete English-print 60-card decklists.

| Cologne / Flutter | Unrestricted Treasure discard | Held-Energy-only Treasure discard | Lost success |
| --- | ---: | ---: | ---: |
| 1 / 0 | 1.974084% | 1.498350% | 0.475734 pp |
| 0 / 1 | 1.841655% | 1.456201% | 0.385454 pp |
| 2 / 0 | 2.490177% | 1.895259% | 0.594918 pp |
| **1 / 1** | **2.622360%** | **2.027751%** | **0.594609 pp** |
| 0 / 2 | 2.507258% | 1.976244% | 0.531015 pp |
| 1 / 2 | 2.089297% | 1.617348% | 0.471949 pp |
| 1 / 3 | 2.626431% | 2.046265% | 0.580166 pp |

At two slots the mixed one-Cologne/one-Flutter package remains best, but its strict endpoint loses 22.674569% of prior success mass. Across all fifteen cases, the highest strict endpoint at each exact swap count is respectively C/F = 0/0, 1/0, 1/1, 1/2, 1/3. Three slots still underperform two. Four slots improve over two by 0.018514 percentage points in the restricted endpoint while sacrificing two further tournament-list cards.

## Verification

Run the module results.tests.shadow_rider_treasure_payment.reproduce from the repository root using Python. The reproducible script verifies the named source card text and baseline 11 Energy, recomputes all 15 exact rational rates, compares the unrestricted rates to the independently existing frontier, and checks conservation of total probability mass. A second algorithm enumerates **72,720 physical labeled-card toy deals** chronologically (opening, Prizes, draw), matching the hypergeometric calculation. The faster grouped-Prize solver takes roughly 12 seconds locally for all mixtures.

This is a conditional first-turn access sensitivity, **not a match win rate**, a verified opponent field, or a strategically recommended cut. A next step is a multi-card discard menu with state-dependent protected resources, plus continuation costs for losing a Psychic Energy otherwise needed for attack acceleration.
