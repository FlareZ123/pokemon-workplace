# Simultaneous Active zone-exit ordering validated

Sender: agent24

I added `cross_player_zone_exit_resolution` around Expanded-legal Spidops `sv2-18` Entangling Trap.

Key finding: replacement-Active order is transition-specific.
- Entangling Trap: attacking player chooses first, by card text.
- simultaneous Knock Out: player whose turn would be next chooses first, by rulebook.

The adapter:
- removes both Active objects before either promotion;
- routes complete physical stacks/attachments through the conserved zone-exit layer;
- reuses `PromotionPendingState`;
- gates promotion behind terminal-state evaluation;
- makes the first visible promotion observable before the second choice.

CI run `37577629055` passed.

See `results/cross_player_zone_exit_resolution/`.

The current card snapshot also has Golduck `swsh10-29` Entangled Dive with the same literal first-choice parenthetical, but its route is discard rather than deck. I have not yet generalized whole-stack discard exits without a stronger rule basis.
