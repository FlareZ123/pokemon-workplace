# Pokémon zone-exit target geometry

## Question

Can the direct-effect portion of the legality-aware zone-exit catalog be
assigned conservative board-target geometry without collapsing card-specific
conditions into generic reachability?

Implementation: `tools/pokemon_zone_exit_target_geometry.py`  
Regression: `results/pokemon_zone_exit_target_geometry/reproduce.py`

## Input boundary

The compiler consumes only rows whose `timing_class` is `direct_effect` from
`pokemon_zone_exit_catalog`.

That excludes Rescue Scarf, Splash Energy, and Celebi, whose matching routing
text belongs to a Knock Out-triggered phase.

The input currently contains 143 print effects across 70 unique card names.

## Geometry vocabulary

The compiler recognizes 12 literal board-target families.

| Geometry | Print effects | Unique names |
| --- | ---: | ---: |
| self | 76 | 39 |
| one of your Pokémon, any position | 26 | 8 |
| opponent Active | 11 | 7 |
| one of opponent's Benched Pokémon | 7 | 5 |
| one of your Benched Pokémon | 6 | 4 |
| one opponent Pokémon, any position | 4 | 2 |
| any number of your Pokémon in play | 3 | 1 |
| one opponent Bench plus self | 3 | 2 |
| all opponent Benched Pokémon | 2 | 1 |
| all opponent Benched except selected survivors | 2 | 1 |
| one unqualified Pokémon to your hand | 2 | 1 |
| both Active Pokémon | 1 | 1 |

All 143 direct rows are assigned one of these literal families. The compiler
raises if a future matching row cannot be classified, making vocabulary drift
visible in CI.

## Representative witnesses

### Self

Accelgor `bw5-11` Deck and Cover shuffles this Pokémon and all attached cards
into the deck.

### One own Pokémon

Scoop Up Cyclone `bw10-95` selects one of your Pokémon.

This geometry also contains narrower filters such as Basic Pokémon, damaged
Pokémon, Colorless damaged Pokémon, or explicit exclusions. The geometry layer
does not erase those filters from the source text. It only records that the
position can be Active or Bench.

### One own Benched Pokémon

Swoobat `rsv10pt5-37` Happy Return selects one Benched Pokémon.

### Opponent Active

Tapu Fini-GX `sm3-39` Tapu Storm-GX moves the opponent's Active Pokémon.

### One opponent Pokémon

Shiftry-GX `sm7-14` Extrasensory selects one opponent Pokémon without an
Active/Bench restriction in the target clause.

### One opponent Benched Pokémon

Mimikyu-GX `sm8-149` Dream Fear-GX selects one opponent Benched Pokémon.

### Any number of your Pokémon in play

Virizion-GX `sm8-34` Breeze Away-GX can return any number of the player's
Pokémon in play.

This is a variable-cardinality board transition and cannot be represented as a
single fixed target edge.

### Multiple opponent Bench targets

Togepi & Cleffa & Igglybuff-GX `sm12-143` can shuffle all opposing Benched
Pokémon under its extra-Energy branch.

Shiftry `sv5-5` instead chooses three opponent Benched Pokémon and shuffles
the Benched Pokémon that were not chosen. Its transition therefore depends on a
survivor-selection complement rather than a direct target list.

### Mixed opponent target plus self

Butterfree `sv3pt5-12` and Noctowl `swsh1-144` remove one opposing Benched
Pokémon and then remove the attacker itself.

A one-target representation loses one half of the physical transition.

### Both Active

Spidops `sv2-18` Entangling Trap removes each player's Active Pokémon in the
same effect, which is the concrete witness used by
`cross_player_zone_exit_resolution`.

### Unqualified one-Pokémon wording

AZ `xy4-91` literally says to put one Pokémon into your hand without the
`of your Pokémon` phrase used by later cards.

The compiler preserves this as
`unqualified_one_to_your_hand` rather than silently rewriting the target
scope. A later semantic normalization layer can resolve that wording with
authoritative rulings or errata.

## Why geometry is separate from filters

A board target has several independent semantic dimensions.

- ownership;
- position;
- cardinality;
- selection rule;
- card-specific eligibility;
- state predicates;
- destination;
- timing.

Acerola and Scoop Up Cyclone share the same coarse `own_one` geometry while
Acerola requires damage counters. Penny restricts the target to Basic Pokémon.
Corviknight excludes Corviknight.

Those restrictions still matter for executable access, so the compiler keeps
the original normalized text alongside the geometry label.

## Strategic implication

Zone-exit effects are not one generic bounce mechanic.

The card pool includes:

- self-reset attacks;
- Bench release;
- opposing Active denial;
- targeted opposing Bench removal;
- wide Bench contraction;
- simultaneous cross-player Active removal;
- variable-cardinality own-board evacuation;
- mixed transitions that remove Pokémon from both sides.

These geometries interact differently with Bench capacity, replacement-Active
choice, evolution-stack identity, lock placement, Prize exposure, and future
board reconstruction.

## Validation

The regression asserts all current geometry counts, one witness for every
geometry family, and exclusion of the three Knock Out-triggered routing rows.

Run:

`python results/pokemon_zone_exit_target_geometry/reproduce.py`
