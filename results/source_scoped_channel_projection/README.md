# Safe projection from source-scoped locks to PlayerChannels

## Question

The repository already uses `PlayerChannels` as a compact representation of ordinary card-play permissions. The source-scoped restriction audit shows that some legal effects carry semantics that a scalar channel cannot represent exactly.

This result measures that boundary and adds a compatibility bridge.

Implementation: `tools/source_scoped_channel_projection.py`

Regression: `results/source_scoped_channel_projection/reproduce.py`

## Result

Among the 106 print-level direct restrictions in the source-scoped audit, **94 restrictions project exactly into the existing hand-action channels**. This is 88.679245% of the audited family.

The remaining **12 restrictions** retain typed predicates. Their richer requirements overlap:

| Reason richer state is required | Print-level rows |
| --- | ---: |
| Evolution-only selector | 6 |
| Defending-Pokémon target relation | 4 |
| ACE SPEC selector | 2 |
| Pokémon-with-Ability selector | 2 |
| Energy attachment to a specific target | 2 |
| Printed card exception | 1 |

Rows can appear under more than one reason.

## Exact projection

The bridge maps ordinary hand restrictions onto `PlayerChannels` only when the mapping preserves the action set exactly.

Examples include Item, Tool, Supporter, Stadium, Trainer-wide, all-card, and Special-Energy restrictions. A Tool-attachment prohibition maps to the Tool hand channel because playing a Tool from hand is its attachment action. A Special-Energy attachment prohibition maps to the Special Energy hand channel.

The regression checks every one of the 94 projectable restrictions against a representative family of hand attempts. The direct typed predicate and the channel projection agree for every tested attempt.

## Residual predicates

Restrictions that select a narrower semantic subset remain explicit.

Spiritomb `bw11-87` / Sealing Scream is an ACE SPEC restriction. Collapsing it into the Item channel would also block ordinary Items and would miss ACE SPECs belonging to another Trainer or Energy class.

Evolution Jammer style effects select Pokémon played specifically to evolve. Mapping them to `pokemon_play=False` would also prevent unrelated Basic Pokémon from being played to the Bench.

Cross Slicer and Submission Hold select Energy attachment to the Defending Pokémon. A global Energy channel cannot preserve legal attachment to another Pokémon.

Team Rocket's Arbok `sv10-113` / Potent Glare combines a Pokémon-with-Ability selector with an explicit Team Rocket's Pokémon exception.

## Source-zone boundary

The bridge applies `PlayerChannels` only to hand-sourced attempts. Other source zones continue through the exact restriction predicate.

This preserves the earlier Vileplume / Dream Ball result. Irritating Pollen projects cleanly to `item_play=False` for hand actions, while a Dream Ball whose current source is `prize_pending` remains legal.

## Finding

A scalar channel model is useful when treated as a **verified projection** of richer legality state. The projection should expose residual predicates whenever card identity, action mode, target relation, or an exception matters.

For the current audited family, this hybrid representation preserves the compact fast path for 94 restrictions and keeps exact transaction semantics for the remaining 12.

## Limits

The 88.679245% figure describes the current conservative direct restriction family in the bundled snapshot. It is not a percentage of every lock effect in Expanded.

Source activation, duration, ownership, attack timing, Stadium prerequisites, coin outcomes, and causal Ability suppression remain outside this projection layer. Those facts determine which restrictions are active before this bridge is applied.

Future card text can introduce a new semantic dimension. The projection code treats unknown dimensions as residual instead of silently forcing them into an existing channel.
