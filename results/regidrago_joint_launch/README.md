# Exact joint Regidrago V access and Dragapult discard in one opening action window

## Research question

The published 2026 Aichi 10th-place [Regidrago VSTAR deck](../competitive_deck_baselines/) must place appropriate Dragon Pokémon in the discard pile for Apex Dragon and separately obtain its Basic Regidrago V. [The validated proposed one-card swap](../regidrago_basic_search_frontier/) adds Dragapult ex (`sv6-130`) while removing one Battle VIP Pass (`swsh8-225`), retaining Battle Compressor, Quick Ball and Mysterious Treasure. The first-turn Regidrago-access probability declines, whereas early Dragapult loading becomes easier. This result evaluates **the joint occurrence of both objectives in one physically executable Item sequence**, avoiding an invalid assumption that individually reachable objectives can use the same one-shot connector twice.

## Exact restricted action semantics

Uniform 60-card shuffle; a seven-card opening containing a legal Basic; six initial Prize cards; one natural draw; and one first-turn action window. Available named actions:

- **Battle VIP Pass** may find and Bench a Regidrago V still in deck. Assume an unused Bench slot.
- **Battle Compressor** may discard Dragapult ex directly from deck.
- **Quick Ball** may discard a held Dragapult ex or explicitly designated safe-filler card, then search a Basic Regidrago V if still in deck.
- **Mysterious Treasure** may likewise discard a held Dragapult/safe card to obtain Regidrago V, or may use safe filler to obtain a Dragapult from deck for a subsequent discard Item.

The model treats each physical Item as **one use**, accounts for its discard cost and card destination, and permits a restricted deck search to find zero. Items are not freely burned as payment for other Items, nor are valuable non-Dragon hand resources assumed disposable. The optional `D` designated safe cards are exogenous non-Basic fillers among the other card slots; `D=0` models only the deliberately discardable Dragon. This is a **full-information line-existence envelope within the stated action language**, since the solver can know which Dragon/Regidrago cards are Prized when selecting its line. First-search K0 information, turns of evolution, Energy, Supporters, Bench conflict, Abilities, opponents, attacks and Prize-taking remain out of scope.

## Exact results

All percentages are conditional on Basic-valid opening hands. Every build retains four Regidrago V and eleven other Basics. Swaps maintain 60 cards by replacing precisely one named Item with the second Dragapult ex.

| Build | Joint endpoint, D=0 | Joint endpoint, D=10 | Joint endpoint, D=20 |
| --- | ---: | ---: | ---: |
| Published, 1 Dragapult / 3 VIP / 1 Compressor | **13.257301%** | **21.702578%** | **24.431455%** |
| **+1 Dragapult, −1 VIP** (exact-print legal candidate) | **19.536020%** | **28.257859%** | **31.002058%** |
| +1 Dragapult, −1 Battle Compressor | 12.893229% | 20.569062% | 23.119384% |
| +1 Dragapult, −1 Quick Ball | 18.584922% | 25.455878% | 27.634480% |
| +1 Dragapult, −1 Mysterious Treasure | 18.584922% | 24.311416% | 26.123156% |

The candidate improves joint limited-Item access by **+6.278719 percentage points at D=0**, **+6.555281 points at D=10**, and **+6.570603 points at D=20**. At D=0 its marginal Regidrago V access still declines from 70.297724% to 68.000861%, so the improvement arises from physical *joint resource availability*, particularly discarding a held Dragapult to find Regidrago or preserving Compressor to discard a deck source.

Compressor is causally necessary for **6.470624%** of the published deck's accepted openings attaining the joint endpoint at D=0; the candidate's analogous figure is **6.642790%**. Removing Compressor eliminates this contribution, making the +Dragapult/-Compressor configuration weaker on the joint metric than the actual published deck in all tested D scenarios. Removing Quick Ball versus Treasure behaves differently at positive D because only Treasure can fetch Dragon Dragapult from deck.

A naive product of independent marginal endpoints would also be wrong: at D=0, published Regidrago access × Dragapult discard marginal gives **11.849522%**, whereas the exact joint policy yields 13.257301%. For the VIP-cut variant that product is **16.361879%**, whereas joint feasible probability is 19.536020%. These differences quantify positive action-level interdependence, including productive discard payment.

## Verification

`tools/regidrago_joint_launch.py` enumerates valid-opening eight-card category hands and exact Regidrago/Dragapult Prize configurations with integer combinatorics and rational arithmetic. For each hidden state, a finite memoized action planner enforces named Item consumption, discards, searches, and Bench access. `reproduce.py` independently deals each labeled physical card in four small decks and uses a separate breadth-first search over **actual physical hand/deck card identities**. Eight output statistics agree exactly. All five full-deck candidate variants and safe-filler levels `D=0,5,10,20,30` satisfy subset and resource-capacity invariants. Windows CI runs these checks.

## Interpretation

This supports further testing of the **complete legal +Dragapult/-VIP candidate** as a promising early-resource tradeoff. An accessible Basic and a loaded attack source still do not establish Regidrago VSTAR, attach the required Energy, guarantee Phantom Dive's availability before it matters, or beat an opponent. Tournament win-rate superiority is unmeasured. The highest-value next step is a stateful K0-first-search policy and turn-two/turn-three Regidrago VSTAR/energy action model against explicit opponents.
