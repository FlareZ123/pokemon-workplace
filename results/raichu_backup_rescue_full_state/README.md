# Harto Miki Raichu/Electrode: full-state backup Gladion rescue

## Question

The prior one-draw connector-race result isolated a clean post-Quick-Ball state and supplied Computer Search payment and Forest Seal readiness as external booleans.

This continuation reconnects that boundary to Harto Miki's full hand and Prize distribution. It carries the real five-card post-Quick-Ball hand, remaining conservative discard stock, already exposed connectors, the second Gladion's physical zone, and the shuffled post-search deck together.

Implementation: tools/raichu_backup_rescue_full_state.py

Independent regression: results/raichu_backup_rescue_full_state/reproduce.py

## Policy and information boundary

The deck partition preserves the preceding Harto models:

- 1 Alolan Raichu
- 2 Gladion
- 1 Computer Search
- 1 Forest Seal Stone
- 2 Crobat V
- 2 Quick Ball
- 11 conservative disposable non-starters
- Giratina as one disposable setup starter
- 13 other setup-eligible Basic Pokemon

The branch begins after a valid seven-card opening and one ordinary random draw.

It fixes one K0 action policy and then conditions on the hidden physical world:

1. Alolan Raichu is actually Prized, although that is not known yet.
2. Quick Ball and at least one Gladion are visible in the action hand.
3. At least one Crobat V remains in the deck.
4. The player pays Quick Ball by discarding one visible Gladion.
5. Quick Ball searches Crobat V, exposing the deck and establishing K1.
6. The player now knows Alolan Raichu is Prized and tries to recover the remaining Gladion in the same turn.

The Gladion discard therefore occurs before the information that makes the backup necessary. This is a consequence analysis of that fixed pre-search choice, not a claim that discarding Gladion is generally optimal.

After setup and the ordinary draw, the action hand has seven cards. Playing Quick Ball, discarding Gladion, searching Crobat V, and immediately benching Crobat leaves five cards, so Dark Asset exposes one card.

## Rescue routes

After K1 is established, same-turn rescue can succeed because:

- the second Gladion was already in the residual hand;
- Forest Seal Stone was already in hand and Star Alchemy can search the backup;
- Computer Search was already in hand and two conservative disposable cards remain;
- Dark Asset draws the backup Gladion;
- Dark Asset draws Forest Seal Stone;
- Dark Asset draws payable Computer Search;
- Computer Search was already in hand with one disposable and Dark Asset draws another disposable, activating the two-card payment.

The Forest Seal branch assumes the already validated physical gates are live: open Tool slot, no relevant suppression, and unused VSTAR Power. The Computer Search branch preserves its two-card payment. The Supporter window remains open for Gladion.

## Exact result

The targeted branch occurs in 0.526446% of valid-opening states. Before conditioning on a valid opening, the probability is 0.474210%.

Within that branch:

| Measurement | Conditional probability |
| --- | ---: |
| Backup Gladion already in hand | 5.248337% |
| Backup Gladion in deck | 85.401035% |
| Backup Gladion Prized | 9.350628% |
| Forest Seal Stone already in residual hand | 10.066892% |
| Computer Search already in residual hand | 10.066892% |
| At least 1 conservative disposable remains | 76.337299% |
| At least 2 conservative disposables remain | 34.725130% |
| Backup topologically available in hand or deck | 90.649372% |
| Rescue before Dark Asset | 16.054113% |
| Rescue after one-card Dark Asset | 20.482909% |
| Increment supplied by Dark Asset | 4.428796 pp |
| Topological availability still stranded | 70.166462 pp |

The topology ceiling is slightly above the preceding clean 90% figure because branch conditioning changes the remaining-card distribution and sometimes places the second Gladion in the residual hand already.

## Connector sensitivity

Recomputing the same branch with connector families disabled gives:

| Available rescue family | Conditional same-turn rescue |
| --- | ---: |
| Backup in hand plus direct Dark Asset Gladion draw | 7.146137% |
| Computer Search routes, Forest Seal disabled | 10.723378% |
| Forest Seal routes, Computer Search disabled | 17.172615% |
| Both connector families | 20.482909% |
| Both connector families, Dark Asset disabled | 16.054113% |

These are joint recomputations and should not be added as independent marginals.

Forest Seal is stronger in this narrow recovery role because the searched Crobat V supplies its host automatically and Star Alchemy has no discard payment. Computer Search still depends on the residual DCI gate.

## Disjoint route attribution

Using the fixed priority order backup already in hand, Forest Seal already in hand, Computer Search already in hand, then Dark Asset top card, the final 20.482909% decomposes as:

| Disjoint route | Conditional contribution |
| --- | ---: |
| Backup Gladion already in hand | 5.248337 pp |
| Forest Seal Stone already in hand | 8.686375 pp |
| Computer Search already in hand and payable | 2.119402 pp |
| Dark Asset draws backup Gladion | 1.657672 pp |
| Dark Asset draws Forest Seal Stone | 1.490773 pp |
| Dark Asset draws payable Computer Search | 0.515041 pp |
| Dark Asset draws a disposable that activates held Computer Search | 0.765310 pp |

The last route is a state-distribution effect absent from the clean positional race. A random draw can improve access without drawing the target or a connector by changing the connector's payment state.

## Relation to the clean connector race

The preceding raichu_backup_connector_race result reported 5.591837% access under sharper conditioning: backup Gladion, Computer Search, and Forest Seal Stone were all unresolved, neither connector was already in hand, and both external connector gates were live.

The current 20.482909% result uses a broader branch distribution, so the two percentages are not directly subtractable.

The clean result isolates hidden-placement correlation. This result integrates pre-existing hand exposure and residual payment state.

## Interpretation

The visible second Gladion is useful redundancy only when it survives the Prizes and is reachable before the deadline.

In this full branch, 90.649372% of worlds have the backup in hand or deck, yet only 20.482909% recover it in the same turn through the modeled routes. Most redundancy is therefore latent.

This sharpens the earlier belief-weighted DCI work. After K1, the value of Computer Search, Forest Seal Stone, and Dark Asset depends on different state variables. Computer Search requires acceptable payment. Forest Seal Stone requires its physical host and global permissions. Dark Asset can reveal material, reveal a connector, or change the payment state of a held connector.

## Validation

The 60-card values are exact combinatorial expectations under the stated policy.

The calculator conditions on a valid opening, integrates one ordinary draw, groups the six Prize cards with a multivariate hypergeometric distribution, materializes the setup Active, executes one Quick Ball payment and one Crobat search, then averages the one-card Dark Asset exposure without replacement.

The reproducer independently enumerates a labeled 12-card toy deck over every valid three-card opening, every ordinary draw, every disjoint two-card Prize set, the physical Quick Ball discard and Crobat search, and every possible Dark Asset top card after the search. Joint state mass, branch mass, topology, immediate rescue, and final rescue all match the grouped model to floating-point tolerance.

## Limits

This is a conditional recovery study, not a full Raichu consistency estimate.

It omits alternative K0 discard policies, other Pokemon and Supporter connectors, repeated draw effects, later turns, ordinary Prize-taking, competing uses of the VSTAR Power or Bench space, matchup-specific locks, and richer state-dependent discardability.

The branch is rare and strategically selected. Its conditional probabilities should not be read as additive percentage-point gains to overall deck performance.

## Next useful work

The strongest continuation is a paired K0 policy comparison.

The current branch hard-codes discarding the visible Gladion. A paired model should compare that action with discarding a conservative disposable card when one is available, preserving Gladion while allowing the same Quick Ball -> Crobat -> K1 transition. The comparison should measure endpoint access, residual discard stock, and downstream Dark Asset / Computer Search value under one common hidden-state distribution.
