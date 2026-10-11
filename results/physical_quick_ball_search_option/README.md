# Physically paid Quick Ball searches reveal when information is worth zero

## Question and main finding

The preceding [physical Supporter menu](../physical_supporter_menu/) examined a free K1 deck inspection even though it did not include a physical search Item. This experiment gives the player a real, payable source of K1: a held **Quick Ball** (swsh1-179) and one disposable filler card. Under the provided rulebook's deck-search rule, Quick Ball may search for zero Basic Pokémon and still inspect the remaining deck and shuffle it.

**A paid search may improve the target-redraw outcome even when the additional Prize information has exactly zero option value.** This happens because the Item and its payment leave the hand before a shuffle-back Supporter redraw, making useful cards in the deck relatively easier to draw. The material difference must be measured separately from K0/K1 observation value.

## Constructed first-turn deck and legal sequence

The seven mutually exclusive classes of the hypothetical 60-card deck are: 12 Basic starters (B), 4 Iono, 4 N, 4 Professor's Research, 4 non-Pokémon useful targets (T), 28 disposable non-Basic filler (F), and 4 Quick Ball (Q).

The player goes second: seven-card opening conditional on one Basic, select one Active Basic, deal six Prizes, draw one card, and observe the resulting seven-card hand and 46-card deck. The player can choose any held Iono/N/Research or Pass, as earlier. Optionally, if **both Q and F are held**, the player may play one Q, discard one F, search and inspect their deck, choose zero Basic output, and shuffle before selecting a subsequent available Supporter or Pass. Because both cards are non-targets, the K Prize prior remains the same, while the redraw hand size changes from seven to five (or from six to four after playing a Supporter).

The no-search policy chooses an action based on the observed hand without knowing which of the four target cards are Prized. The search-first policy **commits to paying based on that hand before learning K** and then chooses the best subsequent action after seeing the deck. The player may instead decline to search if doing so has greater modeled payoff. No target is requested from Quick Ball. The one-Step payoff is own immediate target-in-hand probability minus hypothetical λ times the independently marginalized opponent's next-draw target readiness. The opponent target-access penalties match the prior experiment.

Quick Ball appears as Expanded-legal in the supplied card database and has the additional-card discard prerequisite. Item lock, alternate searches, other card uses, opponent responses and future card value are excluded. The interpretation of F as fully disposable is an explicit model assumption.

## Exact 60-card results

The physically payable Quick Ball-plus-filler event occurs in **42.391235%** of hands conditional on a valid Basic start. Selecting the source remains optional, and the optimal incidence varies with the hypothetical objective.

| Opponent weight | Source selected | Total improvement over best no-search policy | Material-thinning part | Post-payment K1 choice part |
| ---: | ---: | ---: | ---: | ---: |
| 0 | **4.015584%** | **+0.049289939 pp** | +0.049289939 pp | **0** |
| 0.1 | **10.781919%** | **+0.051818963 pp** | +0.049289939 pp | +0.002529024 pp |
| 0.2 | **6.746318%** | **+0.082808768 pp** | +0.082808768 pp | **0** |

At λ=0 the best *free* deck-inspection policy also has zero extra action-choice value, while the **paid** source still creates a +0.049289939-percentage-point access improvement. At λ=0.1, the free observation premium without payment is +0.006666182 pp, while the optimal physically paid search produces +0.051818963 pp overall, mostly from removing inert cards before the next draw. The seemingly paradoxical difference arises because paid search changes the physical decision problem. A zero-price observation with unchanged deck/hand composition is an inappropriate numerical upper bound on a paid action's *combined material and informational* consequences.

We decompose each hand where search is chosen into post-payment fixed-action reward minus pre-payment fixed-action reward (**material term**) and post-payment informed-action reward minus post-payment fixed-action reward (**K1 choice term**). The exact expected terms add to the chosen-source gain over the no-search baseline. The search decision is conditional on the observed hand and is made before knowing K.

## Validation

- [Exact physical Quick Ball policy](../../tools/physical_quick_ball_search_option.py) computes the valid-opening multivariate hypergeometric distribution, payable Q+F gate, hand-specific pre/post-payment action menus, exact K posterior and optional search.
- [Independent labeled-card enumeration](reproduce.py) models physical opening cards, Prize placement, turn draw, an actual Q/F discard and distinct followup redraw subsets. **24 small configurations** exactly match no-search and optional-search payoffs, free observation, source payment/selection frequencies and both decomposition terms. Exact rational large-deck witnesses are pinned.
- [Windows regression](../../.github/workflows/validate-agent2-physical-quick-ball.yml) uses Python 3.13.

This is a narrow one-step source-access and target-readiness experiment, rather than a recommendation to waste Quick Ball in competitive play. Future card value, alternative Quick Ball Basic Pokémon output, the strength of Basic search, Supporter opportunity cost and attack readiness are omitted. The generalizable methodological point is that information and the material effect of acquiring it are inseparable until a physical transition is modeled explicitly.
