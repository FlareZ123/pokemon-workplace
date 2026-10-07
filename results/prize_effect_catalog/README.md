# Prize effect transition catalog

## Question

Can recurring Prize-zone card text in paper Expanded be mapped into a small set of reusable state-transition atoms without treating every card as a one-off implementation?

For a conservative, validated subset, yes.

Implementation: `tools/prize_effect_catalog.py`  
Regression: `results/prize_effect_catalog/reproduce.py`

## Scope

The catalog scans the bundled card database through the same broad legality policy used by the Expanded baseline:

- sets marked Expanded-legal;
- card-level Expanded bans excluded;
- the seven maintained 2025–2026 official ban-overlay prints excluded;
- cards whose own text says they cannot be used at official tournaments excluded.

It extracts rules, attacks, and Abilities containing Prize wording and emits atoms only when a wording pattern is explicitly recognized.

The validated catalog currently contains:

- **139 compiled effect rows**;
- **19 transition atoms**.

These figures are compiler coverage counts, not counts of all Prize-referencing cards. Ordinary Rule Box Prize text and many Prize-count conditions are outside this zone-operation subset unless they match one of the compiled actions.

## Transition atoms

The current vocabulary is:

- `inspect_own_prize`
- `inspect_opponent_prize`
- `face_up_own_prize`
- `face_up_opponent_prize`
- `prize_to_hand`
- `hand_to_prize`
- `deck_to_prize`
- `prize_to_deck`
- `discard_to_prize`
- `prize_to_discard`
- `prize_to_attached`
- `swap_prize_topdeck`
- `swap_prize_hand`
- `shuffle_prizes`
- `take_prize`
- `take_extra_prize`
- `taken_prize_to_lost_zone`
- `taken_prize_to_discard`
- `before_hand_prize_trigger`

An effect may emit several atoms.

## Multi-axis witnesses

### Gladion

Gladion compiles to the combination containing:

- inspect own Prizes;
- Prize to hand;
- hand to Prize;
- shuffle Prizes.

The card is therefore better represented as an ordered multi-zone program than a generic "Prize recovery" label.

### Hisuian Heavy Ball

Hisuian Heavy Ball uses the same broad axes while adding a typed selection condition in the card text:

- inspect own Prizes;
- selected Prize card to hand;
- the Item into the Prize zone;
- shuffle the face-down Prizes.

The current atom compiler records the zone operations. Typed Basic-Pokémon eligibility remains a semantic layer for a later compiler.

### Arc Phone

Arc Phone compiles to:

- Prize/top-deck swap;
- Prize to deck;
- deck to Prize.

The first CI run exposed a useful grammar issue because Arc Phone names the top-deck referent before the switch verb. The parser was tightened to recognize that exact reversed wording family and then passed.

### Team Rocket's Bother-Bot

The referential wording "switch those cards" is compiled conservatively for this explicit Prize-and-hand construction:

- face up an opponent's Prize;
- Prize to hand;
- hand to Prize;
- Prize/hand swap.

This illustrates why a future text compiler needs local referent resolution rather than isolated keyword matching.

## Destination overrides and timing

Two especially important atoms connect directly to the recent state research:

- Barbaracle's Lost Block emits `taken_prize_to_lost_zone`;
- Billowing Smoke emits `taken_prize_to_discard`.

Both show that ordinary Prize-to-hand handling needs a destination override.

Treasure Energy, Dream Ball, Greedy Dice, Jirachi Prism Star, and Chansey's Lucky Bonus supply the `before_hand_prize_trigger` wording family. This independently supports the separate `prize_pending` timing layer being developed around the Prize-taking transition.

## Information-state operations

The catalog also identifies effects that require stronger Prize knowledge than a single composition belief can always represent:

- Town Map and related effects make Prize cards face up;
- one-Prize reveal effects distinguish a specific position;
- Arc Phone and other effects target a **face-down** Prize position;
- Prize swaps can therefore depend on which known cards are face up versus which positions remain face down.

This motivates a partitioned face-up/face-down Prize representation as a next state-kernel extension.

## Validation

The regression asserts named witnesses across the major operation families, including Gladion, Hisuian Heavy Ball, Peonia, Redeemable Ticket, Rotom Dex, Burst-GX, Treasure Energy, Lucky Bonus, Wish Upon a Star, Arc Phone, Team Rocket's Bother-Bot, Injection-GX, Lost Block, Billowing Smoke, Town Map, Poipole, Porygon, Discovery-GX, Lt. Surge's Bargain, and Missing Clover.

It also checks that a maintained banned-overlay print and an explicit tournament-excluded print do not enter the legal catalog.

GitHub Actions validation passed after the Arc Phone wording correction.

## Limits

This is intentionally a conservative semantic island.

The compiler does not yet encode:

- typed selection restrictions such as Basic Pokémon or Ultra Beast;
- exact ordering among all emitted atoms;
- optionality;
- counts or multiplicity parameters;
- target ownership beyond the atom name;
- coin flips and other stochastic gates;
- all Prize-count conditions;
- Rule Box award values;
- full pronoun and referent resolution;
- errata normalization beyond the maintained legality scope.

An atom records a directly supported transition axis. It is not a complete executable interpretation of the card.

## Next work

The most valuable next transition is the visibility partition implied by the catalog: split a player's remaining Prize cards into known face-up positions and uncertain face-down positions, then make face-down-only effects operate on the eligible partition.

That would connect card text such as Town Map, Blazer, Crescent Purge, Arc Phone, and Bother-Bot to the belief kernels without pretending all Prize positions remain exchangeable after public reveals.
