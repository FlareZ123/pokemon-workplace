# E-31 owner-selected ordering can allocate the final Bench slot

## Question

If one simultaneous Prize award contains Chansey with Lucky Bonus and Dream Ball, and the player has exactly one open Bench slot, can the official owner-selected E-31 order determine which effect reaches play?

Yes.

Regression: `results/e31_bench_slot_ordering/reproduce.py`

## Evidence inherited from the ordering result

The official mixed Chansey plus Dream Ball Q&A says the Prize owner chooses which before-hand effect to process first after the cards are taken.

The repository encodes that in `PendingPrizeBatchOrder`: siblings from one simultaneous Prize award can be reordered after staging, while nested additional Prize work remains a barrier.

This result composes that authority with the physical Chansey and Dream Ball executors.

## Initial state

The regression begins with:

- one Active Pokémon;
- four Benched Pokémon;
- exactly one open Bench slot;
- Chansey `sv3pt5-113` and Dream Ball `swsh7-146` staged from one simultaneous Prize award;
- Vileplume `xy7-3` available in deck as Dream Ball's exact target.

Both E-31 effects therefore compete for the same final Bench resource.

Lucky Bonus uses a tails branch in this regression so the test isolates Bench contention rather than nested additional-Prize work.

## Branch A: Chansey first

The owner chooses Chansey first.

Lucky Bonus puts the same physical Chansey Prize into the final Bench slot. The board now has zero open Bench slots.

Dream Ball becomes the next unresolved sibling. Its special Item play cannot complete its deck-to-Bench effect because the Bench is full, so the regression rejects the effect-use branch. Dream Ball is then allowed to finish its E-31 handling by entering hand instead.

Final material state:

- Chansey is in play;
- Dream Ball is in hand;
- Vileplume remains in deck.

## Branch B: Dream Ball first

The owner chooses Dream Ball first.

Dream Ball searches the exact Vileplume target and materializes that Stage 2 Pokémon directly into the final Bench slot. Dream Ball then enters discard.

Chansey becomes the next sibling. Lucky Bonus is now mechanically unavailable because the Bench is full, so Chansey resolves to hand.

Final material state:

- Vileplume is in play;
- Dream Ball is in discard;
- Chansey is in hand.

Per-card-class totals are conserved in both branches.

## Finding

Simultaneous E-31 effect ordering can be a resource-allocation policy decision.

The order is strategically observable only after the Prize identities are known, and a constrained shared resource such as the final Bench slot can make the branches mutually exclusive.

A simulator that resolves simultaneous Prize effects in physical Prize-position order, decklist order, or an arbitrary queue order can therefore choose the wrong legal state even when every individual card transition is implemented correctly.

This also gives a concrete discrete-value example:

- Chansey-first preserves the Pokémon target in deck and places Chansey in play;
- Dream-Ball-first converts the same slot into a chosen deck Pokémon, here Vileplume and its lock effect.

The difference is much larger than a simple ordering detail.

## Limits

The regression fixes Lucky Bonus to tails. A heads branch creates nested additional Prize work and should be modeled with the existing nested barrier before returning to Dream Ball.

The Dream Ball target is fixed to Vileplume to make the branch difference strategically visible. Other targets would produce different values.

The result proves mechanical branch divergence, not which ordering is optimal in a real game. The answer depends on matchup, board, remaining Prize topology, target availability, and the value of the selected Dream Ball Pokémon.
