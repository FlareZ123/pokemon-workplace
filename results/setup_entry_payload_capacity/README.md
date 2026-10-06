# Setup Bench slack for entry-plus-payload Abilities

## Question

How does setup Bench policy affect a hand-to-Bench Ability whose entry card then places additional Pokémon onto the Bench?

## Representative case

Radiant Eternatus has Climactic Gate: when it is played from the hand onto the Bench during the turn, it may search the deck for up to two Pokémon VMAX and put them onto the Bench, after which the turn ends if the Ability is used.

For the full two-VMAX line, three open Bench slots are required before Radiant Eternatus is played: one for Radiant Eternatus itself and two for the payload. The trigger also requires Radiant Eternatus to remain in hand through setup, so this analysis conditions on an opening containing Radiant Eternatus plus at least one other ordinary starter.

`tools/setup_entry_payload_capacity.py` gives an exact slot-capacity distribution under a setup policy that Benches as many other opening Basics as allowed after reserving a chosen number of slots.

## Exact outcomes under bench-all

Conditional on Radiant Eternatus being in the opening hand and at least one other starter being present, the setup policy chooses another starter as Active and Benches every remaining other starter it can.

The number of other starters in the opening then determines the slot outcome:

- 1 to 3 other starters: Radiant Eternatus enters and both VMAX targets can fit;
- 4 other starters: only one VMAX target can fit;
- 5 other starters: Radiant Eternatus can enter, while no VMAX target can fit;
- 6 or more other starters: the setup Bench is full and Radiant Eternatus cannot be played from hand at all.

This is a mechanical capacity result. It assumes the desired VMAX targets are actually available in the deck and ignores every other reason a player might decline Climactic Gate.

## Sensitivity

| Total ordinary Basic starters including Radiant Eternatus | Full 2-VMAX capacity | Only 1 VMAX fits | 0 VMAX fits after entry | Trigger cannot enter |
| ---: | ---: | ---: | ---: | ---: |
| 8 | 99.807648% | 0.187903% | 0.004421% | 0.000028% |
| 12 | 98.795588% | 1.135364% | 0.067639% | 0.001409% |
| 16 | 96.240825% | 3.398273% | 0.347730% | 0.013172% |
| 20 | 91.471108% | 7.334659% | 1.128409% | 0.065824% |
| 24 | 84.015282% | 12.940596% | 2.809958% | 0.234163% |
| 28 | 73.762551% | 19.715849% | 5.851155% | 0.670445% |
| 32 | 61.084885% | 26.619460% | 10.647784% | 1.647871% |

The table is conditional on the preserved-trigger opening described above. It isolates slot pressure from target Prize risk and access.

## Reserving enough slack

Reserving three setup Bench slots guarantees full slot capacity for the two-VMAX payload whenever the conditioned trigger-preservation event occurs. That guarantee has a strategic cost because it may leave useful opening Basics in hand.

This is a concrete example of why a route should carry a peak Bench requirement rather than only its final or immediate occupancy. Climactic Gate is an entry-plus-payload line with peak demand of three slots before the first action begins.

## Partial effects matter

The rulebook permits effects that put Basic Pokémon onto the Bench to use the available number when fewer slots are open, and Climactic Gate itself says "up to 2". A simulator should therefore distinguish at least four outcomes: full two-target payload, one-target payload, zero-target payload after entry, and inability to play the trigger card.

Collapsing these states into a single yes/no "Radiant Eternatus available" flag loses strategically important information.

## Validation

`results/setup_entry_payload_capacity/reproduce.py` checks the complete conditional outcome distribution for 12 total Basics, verifies normalization, and confirms that reserving three slots yields full slot capacity. It also checks a high-Basic stress case.

## Limitations

This model only studies Bench slots. It does not model whether the VMAX targets are Prized, whether they are strategically desirable, whether Ability lock is active, whether ending the turn is acceptable, or whether other setup choices produce a better board.

It also assumes ordinary Basic setup eligibility for the other starters. Optional setup cards and identity-dependent placement policies need a richer setup state model.
