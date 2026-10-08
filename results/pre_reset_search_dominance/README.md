# Search before a full-hand reset: a material-state dominance result

## Question

The Harto Raichu draw-engine result leaves an apparent next choice when Dedenne-GX or Squawkabilly ex is already available:

- reset the hand immediately; or
- play Quick Ball first, then reset.

For the local model, this does not require another large simulation.

Under a specific and useful state projection, **Quick Ball before the reset weakly dominates resetting first**.

Implementation: `tools/pre_reset_search_dominance.py`  
Regression: `results/pre_reset_search_dominance/reproduce.py`

## Rules and card-text basis

Current Quick Ball text requires discarding another card from hand, then searches the deck for a Basic Pokémon and shuffles.

The current deck-search rule says that when a search is restricted to a specified card type, the player may choose fewer than the specified number and may choose none. Quick Ball can therefore legally inspect the deck, take zero Basic Pokémon, and shuffle.

Dedenne-GX's Dedechange says that when Dedenne-GX is played from hand to the Bench, the player may discard their hand and draw six cards.

Squawkabilly ex's Squawk and Seize says that once during the player's first turn, the player may discard their hand and draw six cards.

Items are discarded after they resolve.

## Exact local equivalence

Assume:

1. Quick Ball is legal and in hand.
2. A legal payment card is in hand and the payment is not the held reset source.
3. Dedenne-GX can be benched and use Dedechange, or Squawk and Seize is otherwise usable.
4. The reset will be used immediately after the Quick Ball line.
5. Quick Ball deliberately selects zero Basic Pokémon.
6. The model tracks deck composition and future randomized draw distribution, not a known physical top-deck order.
7. No intervening trigger, lock change, Bench-capacity change, or discard-timing effect distinguishes the two sequences.

Compare two sequences from the same state.

### Reset first

For held Dedenne-GX:

`bench Dedenne -> discard the remaining hand -> draw 6`

Quick Ball, its would-be payment, and every other residual hand card all enter the discard pile.

For an already-playable Squawkabilly ex, the same whole-hand discard occurs when Squawk and Seize resolves.

### Quick Ball first

`Quick Ball -> discard payment -> search deck, take 0 -> shuffle -> reset -> draw 6`

Quick Ball and the payment reach the discard pile first. The reset then discards every other residual hand card.

If the same six physical cards are used as the fresh draw witness, both sequences finish with exactly the same:

- hand multiset;
- deck multiset;
- discard multiset;
- reset Pokémon on the Bench.

The only modeled difference is epistemic:

- reset first may remain K0;
- Quick Ball first has inspected the deck and reaches K1 before the reset.

The regression checks this identity for both held Dedenne-GX and an already-in-play Squawkabilly ex.

## Why this matters

In this state projection, Quick Ball's discard cost is **materially free relative to the imminent reset**.

That phrase is narrow. The payment is not intrinsically free. The reset-first line would discard both Quick Ball and the payment anyway.

The action therefore converts cards that are already doomed to the reset into information without worsening the projected material state.

This is a stronger representation of the local sequencing question than assigning Quick Ball a fixed DCI or AMR value. Its effective cost depends on the downstream zone transition that is already planned.

## Connection to Harto Raichu

The exact Harto observable branch already guarantees Quick Ball plus a legal conservative payment candidate. When a usable reset engine is available, the local "reset first to preserve Quick Ball/payment" intuition fails under this projection because Dedechange or Squawk and Seize would discard those cards before they can be used.

Quick Ball first can instead:

- inspect the full deck;
- infer whether singleton Alolan Raichu is Prized;
- intentionally take no Basic Pokémon if deck thinning is undesirable;
- arrive at the same projected post-reset material state.

This explains why the next broad planner should not treat reset-first as automatically more resource-preserving.

## Important boundaries

This is a conditional dominance theorem, not a universal sequencing rule.

The material equivalence can fail when:

- a known or engineered top-deck order makes Quick Ball's mandatory shuffle costly;
- Item lock or another restriction prevents Quick Ball;
- the required payment must preserve a card for an effect before the reset;
- discard timing activates or disables another effect;
- hand-size, discard-pile, or card-play triggers care about the intermediate state;
- the reset source cannot legally be used after Quick Ball;
- Bench capacity changes;
- the player wants to search and keep or bench a Basic Pokémon, which changes deck composition or board state;
- using Quick Ball has opportunity cost beyond the imminent reset window.

Those cases should be modeled as additional state variables rather than silently absorbed into the dominance claim.

## Generalization

The argument is not specific to Quick Ball or Dedenne-GX.

A pre-reset action can be weakly dominant when all of these hold:

- its consumed hand cards would certainly be discarded by the planned reset;
- its material output can be declined;
- it provides useful information or another nonnegative option;
- its other side effects do not worsen the future state.

This is a form of **doomed-resource sequencing**: an action can have effectively zero incremental material cost because a later committed transition would destroy the same resources anyway.

## Next work

Two extensions are valuable:

1. Search the Expanded card pool for other full-hand reset effects and constrained searches that satisfy the same sufficient conditions.
2. Reintroduce the listed boundary conditions into Harto's whole-action planner, especially known top-deck information, Bench capacity, and discard-trigger interactions.
