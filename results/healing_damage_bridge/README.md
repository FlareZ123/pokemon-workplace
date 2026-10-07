# Compiled healing changes future Knock Out thresholds on the damage board

## Question

Can a literal compiled healing effect feed the same board representation used by
the damage-calculation and Knock Out candidate kernels?

Yes.

Implementation: tools/healing_damage_bridge.py
Regression: results/healing_damage_bridge/reproduce.py

## Bridge

The healing compiler initially executes against board_position_state, the richer
stack-bearing board used by several conservation paths.

The damage and copied-attack kernels currently use board_object_kernel. The new
bridge applies the same HealingProfile semantics to that representation without
introducing a second parser or card-specific rule.

Trainer-only healing still rejects an undamaged target when the compiled heal is
the only effect. Healing removes one damage counter per 10 damage and floors at
zero.

## Threshold witness

A 200 HP target begins with 160 damage.

A later fixed 50-damage attack produces 210 total damage and the shared
damage-board kernel marks the target Knocked Out.

If a 30-damage Potion-style profile resolves first, the target falls to 130
damage. The same later 50-damage attack leaves 180 damage and the Knock Out set
is empty.

The witness therefore connects literal healing text to a strategically discrete
future outcome: whether the same attack creates a Prize-producing Knock Out.

## Finding

Healing should enter policy evaluation through future state, not through a
smooth generic value bonus.

Thirty points of healing can be irrelevant in many states and decisive at one
damage threshold. This is the same discrete-state phenomenon identified for
gust, lock, and other tactical effects in the repository's strategic concepts.

The compiler and bridge provide an executable path:

card text -> HealingProfile -> conserved board damage -> later damage -> KO set

## Limits

This bridge does not pay the Trainer action or Item permission cost. Those
budgets remain upstream.

The repository still has overlapping board representations. This adapter keeps
healing semantics shared across them while board-kernel convergence remains a
separate architectural task.
