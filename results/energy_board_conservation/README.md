# Energy board conservation bridge

## Question

How can aggregate Energy-copy counts and board attachments share one conservation law?

Implementation: `tools/energy_board_conservation.py`  
Regression: `results/energy_board_conservation/reproduce.py`

## State contract

The bridge combines:

- `ZoneCountState`, which owns card-class multiplicity by zone;
- `BoardState`, which owns attachment topology and physical instance IDs;
- an instance-to-class index linking each materialized Energy copy to its exchangeable class.

Validation requires each card class's aggregate `attached` count to equal the number of matching Energy instances present on the board.

## Regression

The test begins with two exchangeable Double Colorless Energy copies in hand. Both are attached to one Active Pokémon with separate physical instance IDs and the same print ID.

After both transitions:

- hand count is zero;
- attached count is two;
- the board has two physical attachments.

The Active then retreats for a cost of two by discarding one Double Colorless Energy. The board model treats that one physical card as two Energy units. The bridge also moves one aggregate copy from `attached` to `discard` and removes that physical instance from its index.

The second Double Colorless Energy remains attached to the Pokémon after it moves to the Bench.

A deliberately inconsistent aggregate count is rejected by validation.

## Implication

The repository now has a usable identity hierarchy:

1. card classes for legality and gameplay semantics;
2. per-zone counts while copies are exchangeable;
3. physical instance IDs when board topology or history distinguishes a copy.

Materialization and dematerialization should be explicit state transitions so one card cannot exist simultaneously in an aggregate off-board count and as a board attachment.

## Scope

This first bridge covers Energy attachment and Energy discarded for normal retreat. Attachment legality and once-per-turn action bandwidth remain upstream concerns.

Tool attachment, Knock Out discard, Bench-contraction discard, Energy movement, recovery, and Pokémon evolution-stack identity remain to be integrated.
