# Printed Prize awards from physical Knock Out batches

## Question

Can the post-Knock-Out game resolver obtain ordinary printed Prize awards from
the same current-print bindings used for HP and damage profiles?

Yes.

Implementation: `tools/knockout_prize_profile_bridge.py`  
Regression: `results/knockout_prize_profile_bridge/reproduce.py`

## Identity rule

A stack-bearing board contains Pokémon object IDs and physical card instance
IDs. Neither is sufficient by itself to identify the current database print.

The shared `stack_board_profile_binding.py` therefore maps each live Pokémon
object to its current print ID. Prize value reads that binding in the same way
HP and Weakness/Resistance do.

This avoids using card names or instance IDs as accidental gameplay keys.

## Base Prize award

`printed_prize_batches()` reads every Pokémon in the complete pending KO batch
and records its printed Prize value.

`printed_prize_awards()` then transfers the victim-side totals to the opposing
player.

This is deliberately the **base printed award**. Effects that reduce, replace,
or otherwise modify Prize taking remain downstream live semantics.

## Simultaneous witness

The regression constructs one simultaneous cross-player KO event:

Player 1 loses:

- Dratini `bw9-81`: 1 Prize.

Player 2 loses:

- Dragapult ex `sv6-130`: 2 Prizes;
- Flying Pikachu VMAX `cel25-7`: 3 Prizes.

The derived awards are therefore:

- Player 1 earns 5;
- Player 2 earns 1.

No Prize values are hard-coded into the KO phase itself.

## Composition with game resolution

Player 1 begins with four Prize cards remaining and receives a printed award of
five. The existing post-KO resolver caps actual Prize taking at the number
available, so Player 1 takes four and reaches zero remaining.

Player 2 takes one and remains at five.

Both players also lose every Pokémon in the modeled batch. The existing
simultaneous-loss table then gives Player 1 the win: Player 1 fulfills the
no-Pokémon loss condition, while Player 2 fulfills both no-Pokémon and
opponent-took-all-Prizes conditions.

This regression therefore composes:

`current print -> printed Prize value -> simultaneous KO award -> capped Prize taking -> terminal resolution`

## Limits

The bridge does not model Prize modifiers such as Legacy Energy, effects that
change the number of Prizes taken, or replacement effects around Prize taking.

Those effects should transform the printed batch award through explicit live
state. They should not mutate the immutable printed profile.

The bridge also assumes the current-print binding has already been updated after
evolution, devolution, or any card-replacement effect.
