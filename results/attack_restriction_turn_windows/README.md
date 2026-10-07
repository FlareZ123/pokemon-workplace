# Attack restriction turn windows

## Question

A concrete attack restriction still needs a lifetime. Extra turns mean simple alternation is insufficient.

Implementation: `tools/attack_restriction_turn_windows.py`

Regression: `results/attack_restriction_turn_windows/reproduce.py`

## Opponent-next-turn window

The common attack duration begins waiting after the attack applies the restriction. A source-player extra turn leaves it waiting. The restriction activates when the opponent next begins a turn and expires when that turn ends.

The regression uses Psyduck `sm9-26` / Headache with a successful heads result and the shared turn scheduler.

## Source-next-turn window

Vanilluxe `xy8-45` / Frigid Breath remains live through intervening turns and expires at the end of the source player's next turn. If the source player receives an extra turn immediately, that extra turn is the source player's next turn and the restriction expires at its end.

## Finding

Turn-relative restriction lifetime should follow player identity and turn boundaries. The timing owner receives only concrete restrictions whose attack gates have already resolved.

## Limits

The window does not execute card actions. It exposes temporal activity, after which the source-scoped permission layer evaluates the attempted action.

The current kernel covers the two duration families found in the audited attack restrictions. New duration wording requires an explicit family and regression.
