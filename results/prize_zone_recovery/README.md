# Prize recovery and deck-search payloads

## Question

If a required card is Prized, does any Prize-recovery effect restore a line that later searches the deck for that card?

No. The recovery destination matters.

This result extends the search-target zone-depletion work with exact Prize-reset transitions. The motivating case is Technical Machine: Evolution in the Aichi Vileplume Control line, where evolution payloads must be in the deck when the attack resolves.

Implementation: `tools/prize_zone_recovery.py`

Validation: `results/prize_zone_recovery/reproduce.py`

## Mechanics represented

Gladion moves one face-down Prize card into the hand.

Rotom Dex returns the current Prize cards to the deck, shuffles, then selects the same number of new Prize cards.

Redeemable Ticket puts the current Prize cards on the bottom of the deck, then selects the same number of replacement Prize cards from the top of the pre-existing deck.

Technical Machine: Evolution searches the deck for Evolution cards. A target moved from Prize to hand by Gladion is therefore still absent from the deck for that search.

## Exact model

The model:

1. conditions a seven-card opening on containing a setup-eligible starter;
2. sets six Prize cards;
3. takes ordinary pre-search draws;
4. records the number of copies from each required non-Basic target group still in the deck;
5. optionally applies a Prize reset;
6. tests whether every target group still has the required number of searchable copies.

The Aichi timing baseline uses 60 cards, 14 ordinary Basic starters, six Prize cards, and one ordinary first-turn draw.

For each reset, the model records blind post-reset searchability, rescue mass, break mass, and an informed policy that resets only baseline-failing states.

## Finding 1: recovery destination is part of access

Gladion moves a chosen Prize card to the hand. For a downstream effect that specifically searches the deck, this does not increase searchable deck copies.

The useful state transition is therefore `Prize -> hand`. Collapsing that transition into a generic `unavailable -> available` flag loses information required by the next action.

## Finding 2: blind Prize resets preserve marginal searchability

For the Aichi timing window, both modeled resets leave overall searchability unchanged when used blindly.

| Target profile | Baseline | Blind Rotom Dex | Blind Redeemable Ticket |
| --- | ---: | ---: | ---: |
| singleton | 77.162486% | 77.162486% | 77.162486% |
| two copies | 95.094061% | 95.094061% | 95.094061% |
| two-copy + two-copy chain | 90.371427% | 90.371427% | 90.371427% |
| two-copy + singleton chain | 73.241397% | 73.241397% | 73.241397% |
| `(2,2,2,1)` package | 65.850959% | 65.850959% | 65.850959% |

The calculation exposes the cancellation directly. Rescue mass equals break mass under blind use.

For the `(2,2,2,1)` package, Rotom Dex rescues 13.511610% of accepted states and breaks 13.511610%. Redeemable Ticket rescues 14.966051% and breaks 14.966051%.

## Finding 3: Prize information creates option value

When the player knows the current state and resets only a baseline failure, the same transitions become useful.

| Target profile | Baseline | Informed Rotom Dex | Informed Redeemable Ticket |
| --- | ---: | ---: | ---: |
| singleton | 77.162486% | 86.065850% | 87.227158% |
| two copies | 95.094061% | 98.258336% | 98.570077% |
| two-copy + two-copy chain | 90.371427% | 96.334712% | 96.911798% |
| two-copy + singleton chain | 73.241397% | 83.924000% | 85.209326% |
| `(2,2,2,1)` package | 65.850959% | 79.362569% | 80.817010% |

For the Aichi-style four-channel package, state-conditioned Redeemable Ticket raises the isolated target-searchability ceiling by 14.966051 percentage points.

The improvement is policy value from information. Blind use has zero marginal improvement in this isolated objective because good and bad state changes cancel.

## Finding 4: Redeemable Ticket has stronger repair geometry

Redeemable Ticket moves the old Prize cards below the existing deck before selecting replacement Prizes from the top.

A target that was already Prized therefore leaves the Prize zone during that resolution.

Rotom Dex mixes the old Prize cards into the full replacement pool, so a returned target can immediately become a Prize again.

For a singleton known to be Prized at the Aichi timing window, Rotom Dex restores it to the searchable deck with probability `46 / 52 = 88.461538%`. Redeemable Ticket restores that old Prize target to the deck with certainty during the reset itself.

Redeemable Ticket can still create a failure by Prizing another required target that was already in the deck.

## Finding 5: Prize resets cannot repair every zone-depletion failure

A target can leave the deck through the opening hand, Prize cards, or an ordinary pre-search draw.

For the `(2,2,2,1)` profile, baseline searchability fails in 34.149041% of accepted states.

Of all accepted states, 25.537202% fail with at least one target copy in the current Prize cards. Another 8.611839% fail without any target copy in the current Prize cards.

The second component cannot be repaired by rotating the current Prize set alone.

## Strategic implication

Prize recovery should be typed by destination.

Relevant transitions can include Prize to hand, Prize to deck, Prize to discard, Prize to play, Prize swapping, and full Prize replacement. A downstream action then determines whether that destination actually restores its line.

This also links Prize information to material access. A reset with zero blind marginal value can gain substantial value when information identifies the states worth disturbing.

## Validation

The reproducer contains an independent labeled-card exhaustive check on a ten-card toy deck with two starter cards, a two-copy target group, a singleton target group, a three-card accepted opening, two Prize cards, and one ordinary draw.

For every accepted opening, disjoint Prize set, and draw, it enumerates every possible replacement Prize set for Rotom Dex and Redeemable Ticket. The labeled calculation matches the grouped exact model for baseline searchability, blind post-reset searchability, rescue mass, break mass, Prize-involved failures, and failures caused entirely by other zones.

The Aichi profile regressions also reproduce the earlier `conditioned_searchability.py` values and assert the blind-reset invariance.

## Limitations

This result isolates target-zone availability. It does not assign deck-slot cost to either reset Item, model access to the Item, model Item lock, or value other resources that can become newly Prized.

The informed policy assumes the relevant Prize information arrives before the reset decision.

The model also assumes random deck order at replacement time. Known top-deck manipulation would change the Redeemable Ticket transition.

The designated target groups do not include every strategically important card in the deck, so these probabilities are state-transition evidence rather than a deck-building recommendation.

## Next work

A practical continuation is to insert a Prize-reset action into the Aichi first-turn planner while preserving timing, information access, Item lock, and other ALS resources.

A broader continuation is a recovery-destination catalog so later state-transition compilers can distinguish hand recovery, deck recovery, Prize replacement, and direct-to-play effects.
