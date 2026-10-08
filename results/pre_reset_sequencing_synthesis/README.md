# Pre-reset sequencing synthesis: material, information, order, and commitment

## Scope

Several recent Harto Raichu results now describe one coherent phenomenon:

- `raichu_draw_engine_fallback/` shows that different reset engines reached by the same search edge have very different continuation value;
- `pre_reset_search_dominance/` identifies when a search payment is incrementally free because an imminent full-hand reset would discard the same cards;
- `pre_reset_shuffle_value/` proves that the search's mandatory shuffle can still have positive or negative positional value;
- `raichu_reset_cancel_option/` measures information value from retaining the right to skip the reset after K1;
- `full_hand_reset_catalog/` shows that 15 canonical legal Expanded effect families can create related full-hand reset states.

This document synthesizes those results into a representation for future planners.

## Central claim

A pre-reset action cannot be evaluated from its literal card text in isolation.

Its strategic value depends on at least four state layers:

1. **material state**: which physical cards move between hand, deck, discard and board;
2. **composition information**: what the player knows about deck and Prize contents, including K0 versus K1;
3. **position information**: what the player knows about where cards occur inside an ordered hidden zone;
4. **commitment state**: whether the later reset is mandatory, still optional, or can be redirected after new information arrives.

The Harto results produce examples where each layer independently changes the preferred sequence.

## 1. Material layer: doomed-resource sequencing

Suppose a player intends to resolve a full-hand discard reset.

A pre-reset action has hand-material cost lower than its literal payment when the cards it consumes would certainly be discarded by that reset anyway.

Quick Ball is the concrete witness.

Under the conditions proved in `pre_reset_search_dominance/`:

- Quick Ball is in hand;
- another legal payment card is in hand;
- the reset source survives the payment;
- Quick Ball takes zero Basic Pokémon;
- the reset resolves immediately afterward;
- no intermediate trigger or restriction distinguishes the sequences;
- deck order is projected away.

Then:

`Quick Ball -> pay -> search 0 -> reset`

and:

`reset immediately`

can end with the same unordered hand, deck, discard and Bench multisets for the same fresh-draw witness.

The search-first line has additionally inspected the deck.

This is a form of **doomed-resource sequencing**. The payment is real as a rules action, while its incremental material cost relative to the committed reset is zero.

## 2. Composition-information layer: K1 can change the continuation

The material theorem by itself only says search-first is no worse inside the stated projection.

The Harto reset-cancellation result shows how information can turn that weak dominance into positive option value.

After Quick Ball establishes K1, the player may discover that the residual hand already reaches Alolan Raichu and decline Dedechange or Squawk and Seize.

In the 5,000,000-state paired Harto sample:

| Window | Reset-capable mass of branch | Cancel option value across branch | Option value conditional on reset capability |
| --- | ---: | ---: | ---: |
| Later turn, Dedenne | 11.581746% | **+1.118200 pp** | **+9.654847 pp** |
| First turn, Dedenne + Squawk | 18.410106% | **+1.788257 pp** | **+9.713452 pp** |

This is **information value through action cancellation**.

The player does not merely choose a better search output after K1. The information changes whether the destructive reset should happen at all.

## 3. Position-information layer: shuffle value has its own sign

The material theorem treats the deck as an unordered random composition.

A search shuffle breaks that equivalence when deck order carries information.

For a singleton target known to be in an N-card deck, let:

- `d` = size of the imminent reset draw;
- `p` = current probability that the target lies in those next d positions.

Without a shuffle:

`P(hit) = p`.

After a full-deck shuffle:

`P(hit) = d/N`.

So direct shuffle value is:

`d/N - p`.

For the Harto-sized 46-card / six-draw window:

- neutral threshold: 13.043478%;
- target certainly in next six: -86.956522 pp;
- target certainly outside next six: +13.043478 pp;
- known top card is a non-target, other 45 positions uniform: +1.932367 pp.

The material payment can therefore be incrementally free while the shuffle is strategically costly.

Composition belief and position belief are separate state variables.

## 4. Reset-transition type matters

The current paper-Expanded card snapshot contains 80 legal prints across 15 canonical literal `discard your hand and draw N` families.

They span several timing classes.

### Supporter resets

Professor Juniper, Professor Sycamore, Professor's Research, Carmine, and Ingo & Emmet.

These consume the Supporter window.

Ingo & Emmet is explicitly position-sensitive because it looks at the top card and can draw from the top or bottom of the deck.

### Ability resets

Dedechange, Phantom Star, Azure Pulse, Squawk and Seize, Regal Stance, and Sprint.

Their gates differ:

- hand-to-Bench trigger;
- VSTAR Power;
- first-turn restriction;
- turn termination;
- ordinary once-during-turn use.

### Attack resets

Burst Roar, Tempest-GX, and two Fast Flight families.

The attack itself ends the turn.

The fresh hand therefore has no ordinary same-turn Trainer/Ability action window afterward.

Tempest-GX also consumes the once-per-game GX attack.

A generic planner should compile these differences instead of representing every reset as `draw N`.

## 5. Typed pre-action / reset representation

A useful reset transition should record at least:

```
ResetTransition
  hand_disposition
  draw_count
  source_kind
  source_location_gate
  supporter_cost
  once_per_game_resource
  first_turn_gate
  ends_turn
  position_sensitive
  fresh_hand_actionable_same_turn
```

A pre-reset connector should record:

```
PreAction
  hand_cost
  output_domain
  output_optional
  searches_full_deck
  shuffles_deck
  information_revealed
  board_side_effects
  action_budget_cost
```

The decision state then needs:

```
State
  material_zones
  board
  action_budgets
  deck_composition_belief
  prize_belief
  deck_position_belief
  reset_commitment
  endpoint_or_future_utility
```

This separates mechanisms that scalar DCI, AMR, or graph connectivity can collapse together.

## 6. Sufficient conditions for local material dominance

For a pre-action A followed by a planned full-hand reset R, A can preserve the same projected material state when all of the following hold:

1. A is legal before R.
2. Every hand card consumed by A would certainly be discarded by R.
3. A's material output can be declined or chosen so it does not worsen the state.
4. R remains legal after A.
5. Intermediate triggers, locks, board capacity and action budgets do not create a distinguishing side effect.
6. Any shuffle performed by A is value-neutral under the current deck-order belief, or deck order is outside the chosen projection.
7. The fresh draw is evaluated from the same resulting deck distribution.

When those conditions hold and A reveals additional information, an observation-consistent policy can always retain the original continuation and may gain better ones.

This is the precise sense in which search-first is weakly dominant in the local theorem.

## 7. Known failure modes

The repository now has explicit reasons for the sufficient conditions to fail.

### Deck-order information

A forced shuffle can erase a favorable top deck or repair an unfavorable one.

### Intermediate discard effects

Cards or Abilities may care about what was discarded, when it was discarded, or which zone a card occupied at a specific timing point.

### Lock and action-budget changes

Item lock can prevent the pre-action. A reset may consume a Supporter, VSTAR Power, GX attack, attack action, or the remainder of the turn.

### Board geometry

A hand-to-Bench reset source may need an open Bench slot. Pre-actions can also change the available Bench.

### Non-optional output

The theorem uses Quick Ball's ability to choose zero cards under constrained deck-search rules. A connector forced to materialize an output can change the deck or board even when its hand payment is doomed.

### Future utility

A one-turn target-access endpoint can value resources differently from the full game. Discarding a card "for free" relative to a reset does not make its earlier use free if another future line wanted that card preserved through a different sequence.

## 8. Harto-specific evidence hierarchy

The current Harto chain should be read in layers.

**Exact results**

- direct Prize-aware access;
- typed Forest Seal gate;
- search-to-Crobat and Dark Asset;
- K0 Quick Ball payment policy;
- visible direct-connector / Forest Seal sequencing;
- search-before-reset material identity;
- shuffle threshold formula.

**Simulation results**

- 5,000,000-state draw-engine fallback;
- 5,000,000-state reset-cancellation option value.

The simulation layers preserve the exact earlier baseline as a control-variate anchor and integrate post-engine draws exactly, but they remain estimates for the sampled initial state distribution.

## 9. Practical planner rule

When a destructive reset is under consideration, evaluate pre-reset actions in this order:

1. identify which current hand resources will disappear if the reset happens;
2. enumerate legal actions that can spend those doomed resources before the reset;
3. separate material output from information output;
4. check whether any action shuffles or otherwise changes deck-position belief;
5. reacquire the decision after new information instead of precommitting to the reset;
6. preserve timing resources and board gates explicitly;
7. compare final utility rather than raw cards drawn.

The important object is the **conditional transition policy**, not a static ranking of the search card or reset card.

## 10. Next research

The strongest next extension is to compile a generic reset-transition type system from the catalog and make it executable.

That system should ingest legal card text and emit:

- hand disposition;
- draw size;
- same-turn actionability;
- turn-resource consumption;
- once-per-game costs;
- timing gates;
- deck-order sensitivity;
- board-entry requirements.

The Harto planner could then use the same infrastructure as Professor's Research, Phantom Star, Azure Pulse, Regal Stance, Burst Roar, and other Expanded reset effects.
