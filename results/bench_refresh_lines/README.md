# Temporary self-constriction as a Bench refresh primitive

## Question

Can Expanded capacity-restriction cards be used deliberately to remove spent Benched Pokémon and then reopen the slots in the same turn?

## Core line

Yes, when the player can remove the restricting Stadium after it has forced the discard.

A full normal five-Pokémon Bench can execute:

`play Parallel City facing yourself -> discard to 3 -> remove Parallel City with Field Blower -> normal capacity returns to 5`

The result is a three-Pokémon Bench with two open slots. The player has intentionally exchanged two chosen Benched Pokémon for two fresh slots without using a Supporter or the ACE SPEC slot.

A parallel one-slot version exists with Collapsed Stadium:

`play Collapsed Stadium -> discard to 4 -> remove it -> normal capacity returns to 5`

That line cleans one chosen occupant and reopens one slot. Collapsed Stadium also constricts the opponent, while Parallel City can orient the three-slot side toward only one player, which makes their strategic side effects different.

## Why Field Blower works as the release action

Field Blower is a legal Expanded Item whose text can choose Stadium cards in play, including the player's own, and discard them. Playing a Stadium and later discarding that Stadium with an Item are different actions. The one-Stadium-per-turn rule restricts playing Stadiums, while Items can normally be played repeatedly during the turn.

Other legal live-Stadium removal cards can sometimes fill the release role, with different costs and action windows. Examples include Lost Vacuum, Paint Roller, Dangerous Drill, Blowtorch, Worker, Pumpkaboo, Chien-Pao, Marshadow, and many attack-based effects. Attack-based removal happens at the end of the turn and therefore does not create same-turn post-removal action space.

## Quantitative refresh geometry

`tools/bench_refresh_lines.py` models a sequence of forced contractions followed by a capacity release.

From a full normal Bench:

| Line | Forced discards | Final occupancy after release | Fresh slots |
| --- | ---: | ---: | ---: |
| Parallel City to 3, then remove it | 2 | 3 | 2 |
| Collapsed Stadium to 4, then remove it | 1 | 4 | 1 |

From a full eight-slot Sky Field board, playing a restricting Stadium also removes Sky Field. The old expansion first collapses toward five, then the new restriction applies:

| Line from occupancy 8 | Total forced discards | Final occupancy after removing new restriction | Fresh slots at normal capacity 5 |
| --- | ---: | ---: | ---: |
| Sky Field replaced by Parallel City, then Parallel removed | 5 | 3 | 2 |
| Sky Field replaced by Collapsed Stadium, then Collapsed removed | 4 | 4 | 1 |

The first line can therefore purge five occupants from an eight-Pokémon Bench before reopening two normal slots. Whether that is desirable depends on how many of the five discarded occupants are stale or strategically expendable.

## Stale-buffer requirement

If `D` occupants must be discarded and only `S` of them are stale, then at least `max(0, D-S)` live occupants must also be lost in the simplified continuation-value model.

For example, replacing an eight-slot Sky Field board with Parallel City forces five total discards before the restriction is removed. Three stale support Pokémon absorb only three of those discards, so two additional live occupants would still have to be sacrificed. The same line is attractive only when the chosen losses and the newly opened slots justify that cost.

## Connector implications

This creates a useful distinction among cleanup resources:

- Supporter cleanup such as AZ or Professor Turo's Scenario competes for the Supporter window;
- Scoop Up Cyclone consumes the ACE SPEC slot;
- Super Scoop Up is stochastic;
- temporary Stadium constriction plus Item removal consumes the Stadium play and an Item but can clean several occupants deterministically;
- Bench-entry Stadium removers such as Pumpkaboo and Chien-Pao can remove a Stadium through an Ability but themselves require a transient Bench slot.

These channels should be represented as competing resource paths rather than collapsed into a generic "can clean Bench" edge.

## Timing consequence

A removal effect used in an attack cannot support a same-turn refresh because attacking ends the turn. An Item or Ability removal can occur before the attack and leaves the rest of the turn available. The action window is therefore part of the cleanup edge's semantics.

## Validation

`results/bench_refresh_lines/reproduce.py` checks the one-slot and two-slot normal refresh lines and an eight-slot Sky Field stress case, including stale-buffer loss.

## Limitations

The model tracks occupancy and stale count rather than Pokémon identities, attached resources, Prize liabilities, or future tactical value. It also treats each stated capacity transition as already legal and active. A full game engine must separately validate Stadium-play availability, Item lock, Ability lock, source conditions, and connector access.
