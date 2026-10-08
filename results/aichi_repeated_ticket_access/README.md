# Repeated Redeemable Ticket and Town Map in Aichi Vileplume Control

## Question

If an Expanded deck can repeatedly replace its Prize cards with Redeemable Ticket, how much of the conditional Prize-repair ceiling survives after requiring naturally accessible copies of the Ticket and a reinspection Item? In a real, published first-turn setup line, does the second *use* of Ticket add much beyond the second *copy*?

We extend [the Aichi post-Guzma & Hala reset study](../aichi_post_gnh_prize_reset/) using the published 2026 Aichi runner-up Vileplume Control list. This is a scoped first-turn endpoint study, **not a deck recommendation**.

**Implementation:** [\`tools/aichi_repeated_ticket_access.py\`](../../tools/aichi_repeated_ticket_access.py)  
**Physical transition and policy regression:** [\`reproduce.py\`](reproduce.py)  
**Fixed-seed 400,000-order simulation:** [\`run.py\`](run.py)

## Methods and assumptions

We preserve the original Aichi list's 60-card composition, starter selection, ordinary first-turn draw, Jirachi's narrow Stellar Wish policy, Tag Call access to Guzma & Hala, and materialization of the searched TM: Evolution, Jet Energy, and possible Artazon.

The established [first-turn Aichi line](../aichi_vileplume_als/) is approximately:

\`Tag Call -> Guzma & Hala -> Jet Energy + TM: Evolution -> Bunnelby Barrage\`.

When that setup route is available, the completed deck search provides exact initial Prize **composition** information. We shuffle the physical current deck after the search and protect the already-retrieved G&H outputs before any Prize reset.

Four originally represented first-turn-neutral Supporter slots are available: Team Yell's Cheer, Karen, Plumeria, and Cassius. Candidate packages reinterpret the first one, two, three, or four *tagged slots* as Ticket or Town Map. The model does not score the future strategic functions of the displaced Supporters. That is a substantial opportunity-cost omission.

Tickets and Town Maps must be naturally present in the accepted opening hand or initial first-turn draw. A revealed newly Prized card does not automatically grant Item access. Town Map supplies perfect Prize reinspection after a failed first Ticket, without shuffling the deck. The second Ticket is used only if the first failed and the player has two Tickets and at least one Town Map available.

The two Ticket Prize blocks are disjoint consecutive groups of six physical cards from the single randomized deck order. There is no intervening deck shuffle or other modeled card movement between them. This matters: see [the exact shuffle-intervention comparison](../prize_ticket_reinspection/).

All package policies use the same underlying randomized trial for a paired comparison. We count a successful **first-turn setup endpoint** only. Neither playing a reset Item nor observing Prizes is assigned any additional cost beyond drawing the required Item copies.

## Primary simulation results

- Raw shuffled deck orders: **400,000**
- Accepted legal Basic-containing openers: **344,794**
- Accepted openers with the named G&H materialization route ready: **242,887**
- Random seed: **20261008**
- Baseline dual Pidgeot ex plus Stoutland Stage-2 endpoint: **41.78176%** of accepted openers
- Baseline Vileplume Item-lock endpoint: **36.27789%** of accepted openers

The following effects are improvements over the same no-Ticket list under the represented first-turn endpoints.

| Substituted tech slots | First Ticket available | Second Ticket + inspection available | Dual Stage-2 lift (pp) | Item-lock lift (pp) |
| --- | ---: | ---: | ---: | ---: |
| 1 Ticket | 8.34759% | 0% | +1.56209 | +0.31584 |
| 2 Tickets | 15.84453% | 0% | +2.96351 | +0.59514 |
| 2 Tickets + 1 Town Map | 15.84453% | 0.07135% | +2.96699 | +0.59514 |
| 2 Tickets + 2 Town Maps | 15.84453% | 0.13370% | +2.96960 | +0.59514 |
| 3 Tickets + 1 Town Map | 22.59871% | 0.19664% | +4.24543 | +0.83992 |

Item accessibility is measured on the accepted-opening denominator and requires the named G&H core route to be available as well.

The approximate 95% binomial half-width for the **total** dual Stage-2 improvement is ±0.04139 pp with one Ticket and ±0.05664 pp with two Tickets and a Town Map. All percentages are sampled estimates, not exact format-wide probabilities.

## Finding 1: a second Ticket copy provides access; a second Ticket use is rare

Two Ticket copies without a reinspection Map give a **+2.96351 pp** dual Stage-2 lift, compared with **+1.56209 pp** for one Ticket. Nearly all that additional gain comes from increasing the probability of naturally finding at least one Ticket for the first reset.

With the same two Ticket slots, adding a Town Map in a third slot enables a second informed reset. The *additional* dual Stage-2 improvement relative to two Tickets alone is **+0.003480339 pp** (12 additional successful accepted starts out of 344,794). The exact binomial 95% interval for this paired nonnegative improvement is **0.001798354–0.006079373 pp** under the independent-random-start model.

Adding a second Map while keeping two Tickets improves the same endpoint by an additional **+0.006090593 pp** (21 additional successful starts), versus two Tickets alone.

The three-Ticket/one-Map package improves the dual endpoint by **+4.24543 pp** overall, but its explicitly **second-reset-only** component is just **+0.00928 pp**. Most gain again comes from improved access to the first Ticket.

## Finding 2: endpoint sensitivity differs

In the 400,000-order sample, the second Ticket+Map produces **no observed additional Vileplume Item-lock setups** beyond two Tickets alone. The sample supports a very small marginal effect in this model, not an assertion of exact zero.

The alternate dual Stage-2 target improves somewhat more often because it has separate evolutions and search constraints that a Prize reset can repair. This is a concrete example of why conditional Ticket reset success must be attached to a specific archetype line and target requirements.

## Practical interpretation

The exact three-reset singleton witness in [Prize Ticket reinspection](../prize_ticket_reinspection/) gives 100% restoration if three Tickets and two non-shuffling reinspection opportunities are available. That is an optimistic, conditional result.

In this published Aichi first-turn model, the key denominator is **accepted openers with both a viable G&H route and naturally held Items**. Repeated resets are much harder to execute than their theoretical transition geometry suggests. Even allowing an extra Map slot, a second informed reset contributes only a few thousandths of a percentage point to the tested dual Stage-2 endpoint.

This distinction is particularly important for deck optimization: the deck slot devoted to an additional reinspection Item may produce more value as a search connector, consistency card, or matchup-specific response. That tradeoff cannot be resolved by a Prize-only repair model.

## Validation and limitations

[\`reproduce.py\`](reproduce.py) verifies the exact physical-card destination after one and two consecutive Tickets, the disjoint-block ordering, package assignment, and paired monotonicity relationships for natural Item access. The reproducible larger run executes through GitHub Actions on a fixed seed.

The model does not yet include targeted Item search; Iono or other hand resets; opposing Item lock; post-Ticket deck searches or shuffles; Town Map access through other connectors; card-playing order conflicts outside the protected G&H outputs; opponent matchups; the strategic value of removed TechSlot Supporters; or mid-/late-game Prize recovery. The corresponding probabilities are first-turn ceilings conditional on these omissions.

## Next steps

A strong extension should introduce an actual Item-search source into the post-G&H window and model its opportunity cost. That will require representing whether the search shuffles the deck and changes the consecutive Ticket Prize-block geometry. Another valuable direction is to test the second Ticket under a mid-game lock-pressure deadline, where restoring specific resources may have higher tactical utility than these first-turn evolution endpoints.
