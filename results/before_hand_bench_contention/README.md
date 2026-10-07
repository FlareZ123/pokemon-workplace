# One-open-Bench contention between Prize-origin E-31 effects

## Question

Can owner-selected E-31 resolution order matter strategically even when the same Prize cards were taken from the same physical state?

Yes. With exactly one open Bench slot, Chansey's Lucky Bonus and Dream Ball compete for a resource that only one of them can consume.

Regression: `results/before_hand_bench_contention/reproduce.py`

## Setup

The regression begins with:

- one Active Pokémon;
- four Benched Pokémon;
- exactly one open Bench slot;
- Chansey and Dream Ball taken together as face-down Prizes;
- one additional face-down Prize still available;
- one Tapu Lele-GX target remaining in the deck for Dream Ball.

The two taken cards are staged together, so the owner may choose which E-31 effect to process first under the official Chansey plus Dream Ball ordering ruling.

## Dream Ball first

Dream Ball uses the only open Bench slot to put Tapu Lele-GX directly from the deck into play.

The Bench is now full. Lucky Bonus cannot put Chansey onto the Bench, so the pending Chansey follows the ordinary route into hand.

The final distinguishing board card is Tapu Lele-GX. The extra Prize remains untouched.

## Chansey first

Lucky Bonus uses the only open Bench slot to put Chansey itself into play.

The regression takes the heads branch. That stages one additional Prize at the front of the pending queue. The nested Prize resolves before control returns to Dream Ball.

Afterward the Bench is still full. Dream Ball's typed search-to-Bench transaction is mechanically unavailable, so Dream Ball follows the ordinary route into hand. Tapu Lele-GX remains in the deck.

The final distinguishing board card is Chansey, and the additional Prize has entered hand.

## Finding

E-31 ordering is a resource-allocation decision.

The same simultaneous Prize award can produce different material boards, different deck depletion, and a different Prize-taking branch because the effects compete for one Bench slot. A simulator that fixes E-31 order before revealing the cards can erase a real policy choice.

The example also connects three previously separate abstractions:

- owner-selected same-award E-31 ordering;
- Bench capacity as a hard state resource;
- recursive additional Prize work as a barrier before returning to older siblings.

## Scope

The regression evaluates concrete legal execution paths. It does not assign a universal strategic preference between Chansey and Dream Ball. The stronger line depends on matchup, desired Bench occupant, Prize state, deck contents, and the value of the additional Prize branch.

The Lucky Bonus branch is conditioned on heads. Coin probability belongs to a higher-level policy evaluator if expected value is required.
