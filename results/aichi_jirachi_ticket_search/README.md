# Aichi Vileplume: preserve Jirachi's Stellar Wish for Ticket access

## Question

Can a real, once-per-turn Pokémon Ability make extra Redeemable Ticket and Town Map copies more executable in the Aichi first-turn Vileplume Control line? Specifically, should Jirachi's **Stellar Wish** be used early to obtain a redundant Guzma & Hala or Tag Call, or preserved for an Item search after Guzma & Hala has already established the setup resources?

This is an extension of the [400,000-opening Ticket package experiment](../aichi_repeated_ticket_access/) and uses its published-list base. The goal is to investigate **sequencing and connector domination**, with a first-turn setup endpoint as the measured outcome.

**Reusable simulation:** [\`tools/aichi_jirachi_ticket_search.py\`](../../tools/aichi_jirachi_ticket_search.py)  
**Basic Jirachi regression:** [\`reproduce.py\`](reproduce.py)  
**Deferred connector regression:** [\`deferred_reproduce.py\`](deferred_reproduce.py)  
**Fixed-seed 300k baseline and deferred runs:** [\`run.py\`](run.py), [\`run_deferred.py\`](run_deferred.py)

## Card and timing basis

Jirachi's **Stellar Wish**, from \`sm9-99\` in the bundled card database, is a once-per-turn Active-Spot Ability that looks at the top five deck cards, may reveal one Trainer and put it into hand, shuffles the other cards into the deck, and makes Jirachi Asleep.

The Aichi planner has a Guzma & Hala route with access to TM: Evolution, Jet Energy and sometimes Artazon. When Guzma & Hala is used to search the deck, the deck is shuffled. A Jirachi Ability that has **not** been used earlier in the turn can therefore inspect a fresh five-card sample **after** this G&H search.

If that post-G&H Stellar Wish takes a Ticket or Town Map, it changes both the available Item counts and the composition of the deck before the first Ticket. After the selected card is removed, Stellar Wish shuffles the remaining deck; our simulator independently randomizes this new order. Subsequent consecutive Tickets do not shuffle the deck, so their new Prize sets correspond to sequential non-overlapping six-card blocks.

The simulated policy only selects a Ticket or Map if this increases the number of executable informed Ticket resets, given naturally held Items. Otherwise it declines Stellar Wish. The objective ends after the specified first-turn setup line.

### Two Ability-timing policies

**A. Strict unused-only follow-up.** Retain the original Aichi preparer: Jirachi uses Stellar Wish early whenever it finds Guzma & Hala or Tag Call in the original top five. Only when it found neither and remained unused may it perform a late post-G&H Stellar Wish for Ticket or Map.

**B. Defer redundant early connector.** If the original opening or first turn's natural draw already provides a viable Guzma & Hala or Tag Call route, the player can decline a redundant early Jirachi Stellar Wish Trainer hit, use the naturally held connector, then save Jirachi's Ability for the new top five **after** the G&H search.

The second policy requires careful physical card accounting. When early Stellar Wish would have found an unneeded G&H or Tag Call, that card remains in the deck. If a naturally held Tag Call replaces an early G&H hit, the Tag Call is instead consumed and the very same G&H can be fetched and played. The one-Supporter-per-turn rule remains respected. The four alternative cases are checked directly in the regression against the original preparer's hand/deck zones.

## Paired simulation

Each option was tested on the same **300,000 randomly ordered 60-card games**, seeded \`20261008\`, with **258,534 accepted Basic-containing openers** and **182,067 accepted openers whose modeled G&H core route was ready**. Policy comparisons within each option share the same start and random physical-card orders.

| Metric | Strict unused-only policy | Defer redundant early connector |
| --- | ---: | ---: |
| Eligible Jirachi after G&H | 11,292 | **22,732** |
| Stellar Wish Item acquisitions, 2 Tickets + 1 Map package | 1,745 | **3,502** |
| New first-reset access, same package | 1,719 | **3,448** |
| New second-reset access, same package | 26 | **54** |
| Dual Stage-2 lift from late Stellar Wish, same package | **+0.130350 pp** | **+0.251804 pp** |

The strict unused-only policy's two-Ticket/one-Map package moves its represented dual Pidgeot ex and Stoutland endpoint lift from **+2.982586 pp** without the late Ability to **+3.112937 pp** with it.

With redundant connector deferral, the corresponding modeled lift moves from **+2.980266 pp** without late Stellar Wish to **+3.232070 pp** with it. The incremental net value of late Stellar Wish inside that revised policy is **+0.251804405 percentage points**, from **652 helped states and one harmed state** among 258,534 accepted openers. Its approximate paired 95% normal confidence half-width is **0.019349 percentage points**. That one harmed state comes from a changed post-Stellar deck shuffle; these are physical-card stochastic policies rather than a guarantee of monotone outcome on every paired deal.

Other package effects with the deferred policy:

| Package | Additional first/second-reset access from late Wish | Dual Stage-2 gain from late Wish |
| --- | ---: | ---: |
| 1 Ticket | 2,066 / 0 | +0.146596 pp |
| 2 Tickets | 3,448 / 0 | +0.251418 pp |
| 2 Tickets + 1 Map | 3,448 / 54 | +0.251804 pp |
| 2 Tickets + 2 Maps | 3,448 / 113 | +0.252191 pp |
| 3 Tickets + 1 Map | 4,496 / 179 | +0.331871 pp |

A larger fraction of the gain again comes from securing **the first Ticket**. The few additional second-reset opportunities are much less frequent.

## Interpretation

Jirachi's early selection can be a real opportunity-cost decision. Selecting a redundant G&H/Tag Call from the first five cards may consume the only available Stellar Wish, eliminating the option to look for Ticket or Map after G&H search has shuffled the deck. Even though the early selection is locally strong, it can be dominated for the measured line when a suitable connector is already held naturally.

The experiment demonstrates a practical, quantified gain from preserving a once-per-turn search Ability. It **does not** establish that Ticket techs are optimal additions to the published Vileplume list or that the deferred sequencing is optimal across every matchup.

## Validation and unresolved limitations

- \`reproduce.py\` checks physical top-five selection eligibility, Item-role availability and paired win/loss count conservation.
- \`deferred_reproduce.py\` constructs explicit 60-card openings for four redundant-connector configurations and verifies the exact hand/deck changes, including consumed Tag Call, before exercising the stochastic policy.
- Both simulation runs are fixed-seed and repeatable in GitHub Actions, with physical cards separately labeled so selecting one duplicate changes only the corresponding physical copy.

As in the underlying Aichi planner, the G&H materialization step assumes successful access to the searched Tool and Special Energy and does **not** fully enforce its optional two-card discard cost, so these setup results remain optimistic abstractions. The model also omits competitive consequences of spending an early Tag Call, opponent Item lock, possible counters to the Active Jirachi, actual post-attack evolution resolution, and the future utility of displaced Supporters. It permits only one late Stellar Wish after the original G&H search and does not optimize every Trainer found in a five-card observation.

**Next question:** compare the value of deferred Jirachi against the cost of using Tag Call or delaying other Trainers in a longer first-two-turn model, including discardable hand resources and opponent lock timing. The decision could reverse in specific hands or matchups.
