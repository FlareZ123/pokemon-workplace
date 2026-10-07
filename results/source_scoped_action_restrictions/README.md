# Source-scoped card-action restrictions

## Question

Several Expanded effects say that a player cannot play or attach specified cards **from hand**. A global permission bit loses that source condition. This result asks whether the direct restriction family can be represented with one typed predicate that preserves source zone, card class, action mode, target relation, and explicit card exceptions.

Implementation: `tools/source_scoped_action_restrictions.py`

Regression: `results/source_scoped_action_restrictions/reproduce.py`

## Corpus audit

The compiler scans the effectively legal paper Expanded card pool and accepts a conservative wording family whose restriction explicitly names the hand as the prohibited source.

The current bundled snapshot contains **106 print-level restrictions across 63 card names**. The sources are 77 attacks and 29 Abilities. Of those restrictions, 101 affect the opponent and 5 affect both players.

Every accepted restriction names `hand` as its prohibited source zone. The represented semantic dimensions are:

| Dimension | Print-level rows |
| --- | ---: |
| Item | 42 |
| Stadium | 22 |
| Special Energy play | 20 |
| Tool | 13 |
| Supporter | 10 |
| All cards from hand | 7 |
| Evolution | 6 |
| Trainer | 5 |
| Special Energy attachment | 2 |
| ACE SPEC | 2 |
| Pokémon with an Ability | 2 |
| Energy attachment to the affected target | 2 |
| Tool attachment | 1 |

A single effect may contribute to more than one dimension.

## State representation

A compiled restriction keeps:

- the exact source card and effect text;
- the prohibited source zone;
- semantic card-action dimensions;
- player scope;
- an optional required target relation;
- explicit excluded card tags.

A concrete action attempt records card kind, source zone, action mode, card tags, and target relation. The predicate first checks source zone, then explicit exclusions and target relation, and finally semantic overlap.

This keeps the existing broad `PlayerChannels` model useful as a coarse compatibility layer while giving newer transaction code a more precise legality predicate.


## Exclusive branch resolution

Two audited attack profiles contain mutually exclusive lock branches.

Crobat `sv4-112` / Echoing Madness lets its user choose Item cards or Supporter cards. Vileplume `swsh11-3` / Allergy Storm uses a coin result to select Supporter lock on heads or Item lock on tails.

The compiled profile records the printed alternatives and refuses legality evaluation until one branch is resolved. `resolve_exclusive_restriction` binds the chosen dimension and returns an ordinary concrete restriction for downstream permission checks.

This prevents an unresolved union from blocking both categories simultaneously.

## Regression witnesses

### Vileplume and Prize-origin Dream Ball

Vileplume `xy7-3` / Irritating Pollen blocks an Item played from hand. The same predicate leaves a Dream Ball in `prize_pending` outside that prohibited source.

This generalizes the earlier `dream_ball_vileplume_lock_line` result instead of adding another Dream Ball-specific exception.

### Trainer-wide and all-card restrictions

Darkrai & Umbreon-GX `sm11-125` / Dark Moon-GX blocks a Tool action because Tools are Trainer cards.

Gengar & Mimikyu-GX `sm9-53` / Horror House-GX blocks a Basic Energy attachment from hand. An attachment from discard remains outside the represented hand restriction.

### ACE SPEC selector

Spiritomb `bw11-87` / Sealing Scream blocks an Item tagged as an ACE SPEC and leaves an ordinary Item outside that selector.

### Card exception

Team Rocket's Arbok `sv10-113` / Potent Glare blocks Pokémon with an Ability from hand while preserving its printed Team Rocket's Pokémon exception.

### Target-scoped restrictions

Dialga `xyp-XY77` / Time Freeze prevents evolution of the Defending Pokémon. The predicate does not spread that restriction to another evolution target.

Palkia `xyp-XY75` / Cross Slicer prevents Energy attachment from hand to the Defending Pokémon. The same Energy can remain legal for another target, and a non-hand attachment remains outside this source restriction.

## Rules relationship

The Advanced Player's Rulebook classifies effects such as "can't play any ... from their hand" as effects on a player. The printed source phrase therefore remains mechanically meaningful.

The existing lock research also shows why card class must remain typed. Pokémon Tools are their own Trainer type under the current rules, so an Item-only restriction and a Trainer-wide restriction reach different action sets.

## Finding

Direct play and attachment denial in this audited family is **source-sensitive**. A mechanically faithful transition predicate needs the attempted action's source zone alongside its card and target semantics.

A global `item_play=False`, `supporter_play=False`, or similar bit can still summarize the common hand-action case. It should not be treated as a complete description of legality for actions originating elsewhere.

## Limits

This compiler covers literal direct prohibitions that explicitly name cards played or attached from hand. It does not yet model every condition that controls whether the source effect itself is active. Position, Stadium prerequisites, coin outcomes, attack-duration windows, source ownership, and causal Ability-suppression state remain inputs from other kernels.

The target model currently formalizes the Defending-Pokémon relation needed by the audited evolution and Energy-attachment cases. More target geometries should be added when a verified card family requires them.

The compiler deliberately raises on a direct hand-scoped restriction matching the broad audit pattern when its semantic wording is outside the represented grammar. This makes corpus drift visible instead of silently accepting an unknown effect.
