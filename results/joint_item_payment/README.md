# Shared-hand discard-budget contention among Quick Ball, Ultra Ball, Secret Box

## Research question

The earlier [Basic-valid single-Item quota study](../basic_valid_discard_quota/) estimates payment feasibility for one Item at a time in separate constructed decks. Can several Items that share the same expendable hand cards all be used in a *single* deck and action window? An Item's individual payability does not imply a group is sequentially playable.

## Exact-print anchors and modeled deck

The supplied card corpus identifies **Quick Ball swsh1-179** (discard another card, Basic Pokémon search), **Ultra Ball swsh9-150** (discard two other cards, Pokémon search), and **Secret Box sv6-163** (discard three other cards, searches Item, Tool, Supporter, Stadium). All three prints are marked Expanded-legal by the supplied corpus. Secret Box has the ACE SPEC one-copy deck restriction.

One artificial **60-card legal-count composition** is used for the initial benchmark: B12 starter Basics, Q4 Quick Ball, U4 Ultra Ball, S1 Secret Box, F8 hypothetical discard-safe filler and P31 strategically protected cards. These category counts **do not constitute a playable decklist or a legality certification for unspecified filler cards**. All non-F hand cards are protected as payment, including all excess Item copies and extra Basics.

The player draws an initial seven-card hand conditioned on at least one Basic, places exactly one Basic into the Active Spot, places six uniformly random Prizes, and draws one natural card going second. At the action snapshot the hand has seven cards (seven initially, minus one Active, plus one draw).

The model distinguishes:

* **Held:** at least one physical copy of the named Item is in the post-setup hand.
* **Individually payable:** enough F cards to pay that one Item's cost, viewing the hand unchanged.
* **Sequentially payable pair:** both named Item copies exist, and the original hand holds enough F to pay the **sum** of their discard quotas. The first Item is played, but cards fetched from the deck are deliberately excluded from funding the second.
* **All sequential:** Q, U and S are all in hand with at least six F cards available, a demanding no-new-material restriction.

The study isolates discard-resource contention. It does not simulate successful searches, useful deck targets, searches yielding additional discardable cards, post-search shuffles, draw engines, lock effects, matchup-specific DCI, or future action opportunity costs. Actual action sequencing may allow new payment resources, so the sequential event is an exact **restricted line**, not an upper bound on all legal multi-Item play.

## Quantitative findings (conditional on Basic-valid setup)

| F | Any held | Any individually payable | At least two individually payable | At least two sequentially payable |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 73.335891% | 18.559013% | 0.764183% | 0.033176% |
| 8 | 73.335891% | **34.398664%** | **3.108094%** | **0.409984%** |
| 12 | 73.335891% | 47.158528% | 6.344490% | 1.411627% |
| 20 | 73.335891% | 63.751517% | 13.419482% | 5.485250% |
| 28 | 73.335891% | 71.027410% | 19.069774% | 11.398333% |

At F8, exactly computed individual source payments are Quick **27.619222%**, Ultra **9.453070%**, and Secret Box **0.453336%**. Those marginal values agree with the prior one-source engine when all other sources are placed in the protected class.

The **Quick + Ultra** pair illustrates the difference between inspecting a static hand and executing a line: **2.929273%** of Basic-valid states simultaneously hold Q, U and at least two safe filler cards, making each individually playable; only **0.404250%** have at least three such filler cards and can pay both sequentially without reusing searched output. Across all three distinct source pairs, **3.108094%** have at least two individually payable actions but **0.409984%** can pay some pair sequentially. Conditional on the former event, the restricted continuation succeeds in **13.190845%** of those states.

All three Items can individually be payable in **0.018870%** at F8. None can all be paid sequentially in this first-draw hand model, **for any F**, because the three physical Items plus six distinct discarded payment cards require at least nine hand cards; the post-setup hand contains only seven. This zero is a strict conservation consequence under the defined exclusion of newly searched cards.

One more caution: substituting marginal payability into an independence assumption gives 34.758538% for any playable Item at F8, whereas exact shared-hand enumeration yields **34.398664%**. At F20, the same independence calculation instead *underestimates* joint access, giving 61.571265% versus the exact 63.751517%. Source competition and common availability of discardable filler produce opposing correlations. A fixed-sign independence correction is therefore unjustified.

## Calculation and verification

The [joint exact solver](../../tools/joint_item_payment.py) enumerates initial **category counts** with multivariate-hypergeometric weight, conditions on holding a Basic, moves a Basic to Active, and enumerates the identity of the next natural draw. Uniformly chosen Prizes are marginalized out, since a natural draw from the shuffled unprized remainder is exchangeable with a draw from all remaining unseen cards when no intervening effects provide information.

For initial category histogram \(h\) and draw category \(j\), the conditional state weight is

\[
\frac{\prod_i \binom{N_i}{h_i}}{\binom{N}{7}-\binom{N-B}{7}}\,
\frac{N_j-h_j}{N-7}.
\]

Every probability uses exact Python `Fraction` arithmetic. The independent [physical-card oracle and reproducer](reproduce.py) exhaustively deal labeled small decks, select a starting Basic, separately place each possible Prize combination, then try every permitted natural draw. Four toy configurations agree with all **18** modeled event fractions. Further regression checks all 18 events are nondecreasing as protected cards are reclassified into F over 32 baseline filler-pool sizes. Existing [single-Item exact quota calculations](../../tools/basic_valid_discard_quota.py) provide independent marginal crosschecks.

A manually dispatched [Windows Python CI](../../.github/workflows/validate-agent2-joint-item-payment.yml) runs the full reproducer. Nothing is scheduled on repository push.

## Next investigations

A natural next step is to allow the first successfully executed Item to produce a *typed* and possibly discardable search target, then evaluate whether that output can pay a second Item. This demands target existence, search-output eligibility, source-preservation choices, and alternative-use opportunity costs. A stronger deck-specific model should substitute real exact-print card classes for hypothetical F and include the opportunity value of spending each resource.
