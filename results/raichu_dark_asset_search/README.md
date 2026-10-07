# Harto Miki Raichu/Electrode: first-order Dark Asset after search-to-Crobat

## Question

Once Quick Ball or Ultra Ball is used to put Crobat V into hand, how much additional Alolan Raichu access comes from immediately benching Crobat V and resolving Dark Asset?

This extends `results/raichu_search_to_seal_access/`. The preceding result stopped after using searched Crobat V as the Pokemon V prerequisite for Forest Seal Stone. This layer also credits the cards drawn by Crobat V itself.

Implementation: `tools/raichu_dark_asset_search.py`  
Independent labeled regression: `results/raichu_dark_asset_search/reproduce.py`

## Scope

The deck partition and setup policy are unchanged from the preceding Harto Miki models. The new transition is intentionally first-order. After a search-to-Crobat action, Dark Asset can directly expose:

- Alolan Raichu when it remains in deck;
- Forest Seal Stone, which can then be attached to the searched Crobat V and use Star Alchemy;
- Gladion when Alolan Raichu is Prized.

Secondary search connectors drawn by Dark Asset are excluded. This keeps the result attributable and avoids silently turning the component into a full-turn planner.

## Why the search cost changes Dark Asset

At the modeled action snapshot there are seven cards in hand after setup and one ordinary draw. Searching Crobat V changes that hand size before Dark Asset resolves.

For Quick Ball:

`7 -> play Quick Ball -> 6 -> discard 1 -> 5 -> search Crobat V -> 6 -> Bench Crobat V -> 5`

Dark Asset therefore draws one card.

For Ultra Ball:

`7 -> play Ultra Ball -> 6 -> discard 2 -> 4 -> search Crobat V -> 5 -> Bench Crobat V -> 4`

Dark Asset therefore draws two cards.

This produces a concrete cost-to-draw coupling: a discard/search cost lowers immediate hand resources while simultaneously increasing the number of cards Crobat V can draw back. The extra draw does not refund the discarded identities, so the two effects remain strategically distinct.

## Main result

Baseline assumptions remain 60 cards, valid seven-card opening, six Prize cards, one later ordinary draw, the conservative 12-card discard pool, open Bench space, no relevant Ability/Item/Tool lock, and one unused VSTAR Power.

| Measurement | Exact probability |
| --- | ---: |
| Search-completed Forest Seal access | 34.466609% |
| Add first-order Dark Asset | **35.092509%** |
| Incremental Dark Asset gain | **+0.625900 pp** |
| Quick Ball -> Crobat -> Dark Asset contribution | +0.512479 pp |
| Ultra Ball -> Crobat -> Dark Asset contribution | +0.113421 pp |
| Increment occurring while Raichu remains in deck | +0.447265 pp |
| Increment occurring while Raichu is Prized | +0.178635 pp |
| Target-Prized conditional access before Dark Asset | 33.825012% |
| Target-Prized conditional access with Dark Asset | **35.601961%** |

Quick Ball accounts for 81.8788% of the new first-order gain. Ultra Ball accounts for 18.1212%. The overall increment is split 71.4595% into target-in-deck states and 28.5405% into target-Prized states.

## Finding 1: discard cost can create draw bandwidth

The earlier DCI work treats discard cost as a gate on whether a connector can be played. Dark Asset adds a second role for that same payment: paying the connector reduces hand size before the draw-to-six Ability resolves.

This does not make higher discard costs intrinsically desirable. Ultra Ball requires more acceptable discard material in the first place, and the identities lost can matter later. Within states where the cost is already payable and Crobat V is the chosen output, however, Ultra Ball creates a two-card Dark Asset window while Quick Ball creates a one-card window.

The result therefore strengthens the temporal-resource view of DCI. A payment can alter a downstream resource-generation effect as well as consume cards immediately.

## Finding 2: Quick Ball still supplies most of the incremental value

Quick Ball's candidate search-to-Crobat action is available in 18.607122% of modeled states, while the target-Prized Ultra Ball Dark Asset branch is available in 1.456561%. After removing states already successful through the preceding policy, their contributions are 0.512479 and 0.113421 percentage points.

Quick Ball still wins on average because its one-card payment is available much more often. Ultra Ball's deeper Dark Asset draw partly compensates for its higher payment threshold in the narrower target-Prized branch.

## Finding 3: the Prized-target gain is strategically concentrated

Conditional on Alolan Raichu being Prized, access rises from 33.825012% to 35.601961%, a 1.776949-point gain.

In those states, Ultra Ball can inspect the deck, confirm the target is absent, search Crobat V, and draw two with Dark Asset. A drawn Gladion immediately supplies Prize access. A drawn Forest Seal Stone can use the searched Crobat V to search a remaining Gladion. Quick Ball has the same output family with one Dark Asset draw when its cheaper cost is the available route.

## Evidence and validation

The 60-card values are exact combinatorial expectations under the stated policy. The calculation keeps Prize counts for Alolan Raichu, Gladion, Forest Seal Stone, and Crobat V, marginalizes irrelevant Prize identities, and evaluates the one-card or two-card Dark Asset draw without replacement after a physical Crobat V copy leaves the deck.

A separate labeled 14-card regression enumerates every valid three-card opening, every two-card Prize set, every ordinary next draw, and every possible one-card or two-card Dark Asset sample after a concrete Crobat search. It uses two labeled Crobat V copies and two labeled Gladion copies, so it also checks cases where another Crobat is already Active or in hand. Every reported field matches the category model.

## Limitations

This is a first-order draw layer. It does not credit Quick Ball, Ultra Ball, Computer Search, or another connector if that connector itself is drawn by Dark Asset. It also omits Dedenne-GX, Squawkabilly ex, repeated draw engines, Battle Compressor, Rescue Stretcher, evolution readiness, attack setup, Bench competition, Ability lock, VSTAR opportunity cost, or matchup-specific preservation.

The binary disposable pool remains a deliberate simplification. Paying a cost can increase Dark Asset draw count while still destroying strategically important future resources, so the measured gain should not be read as a recommendation to discard aggressively.

## Next useful work

The next deck-specific step is a bounded turn planner that allows the cards drawn by Dark Asset to become new executable actions while preserving one-use Dark Asset, Item costs, Supporter bandwidth, the VSTAR budget, Bench capacity, and K0/K1 information timing. A smaller orthogonal validation is to push the Quick Ball and Ultra Ball witnesses through the repository's conserved Trainer transaction layer.
