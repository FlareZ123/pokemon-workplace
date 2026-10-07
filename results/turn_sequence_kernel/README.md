# Extra-turn boundaries and action-budget reset

## Question

How should a turn-resource model represent attacks that end the current turn while scheduling another turn for the same player?

The Expanded card pool contains direct examples:

- Dialga-GX `sm5-100`, Timeless-GX;
- Origin Forme Dialga VSTAR `swsh10-114`, Star Chronos;
- other prints and Supreme Puff-GX with the same extra-turn instruction.

The checked Dialga prints are effectively legal under the repository's Expanded legality classifier.

Implementation: `tools/turn_sequence_kernel.py`  
Regression: `results/turn_sequence_kernel/reproduce.py`

## Finding

An extra turn is a fresh action-budget window for the same player.

Using the attack still closes the current turn. The attack's effect changes who owns the next turn and, for the checked wording, skips the intervening Pokémon Checkup / between-turn step.

The sequence is therefore:

`current actions -> attack -> current budget closes -> skip checkup -> same player starts a new turn -> turn budget resets`

This matters because a player can spend their ordinary Supporter, Stadium play, manual Energy attachment, and Retreat before Timeless-GX or Star Chronos, then receive those ordinary turn resources again on the scheduled turn.

The model keeps this separate from once-per-game GX/VSTAR restrictions. Those are different resources and remain upstream.

## State

`TurnSequenceState` stores:

- current player;
- other player;
- the current player's `TurnActionBudget`;
- the other player's retained budget/derived limits for their next turn;
- whether an extra turn is queued;
- whether Pokémon Checkup is skipped before that queued turn.

`close_turn_with_attack(...)` consumes the attack boundary and can queue the extra turn. For an ordinary boundary, `advance_turn(...)` swaps players and resets the incoming player's retained budget. For an extra turn, it keeps the same player and resets that player's own budget. This prevents player-specific quota effects such as Dual Brains from leaking across the turn handoff.

The returned `TurnAdvance` records whether Pokémon Checkup occurs and whether the same player continues.

## Validation

The reproducer:

- verifies Timeless-GX and Star Chronos text in the bundled resources;
- checks effective Expanded legality for their representative prints;
- verifies an ordinary turn end swaps players and performs Pokémon Checkup;
- verifies a two-Supporter limit owned by Player A does not leak into Player B's turn and returns when A becomes current again;
- spends Supporter, Stadium, manual attachment, and Retreat before an extra-turn attack;
- verifies the attack closes the current budget;
- verifies the scheduled turn stays with the same player and skips Pokémon Checkup;
- verifies every ordinary turn channel is available again on that new turn;
- verifies a subsequent ordinary attack passes control to the opponent.

## Strategic implication

Extra-turn effects multiply action bandwidth, not only attack count. Any planner that models Timeless-GX as “another attack” while retaining spent Supporter, attachment, Stadium, or Retreat flags across the boundary undervalues the line and can reject legal sequences.

This connects directly to multi-action ALS reasoning: a Timeless-GX line may use setup or gust resources before the first attack and then have a fresh Supporter/attachment window before the next attack.

## Limits

The kernel is intentionally small. It does not model damage, Prize taking, Knock Outs, promotion, once-per-game GX/VSTAR resources, draw-for-turn, or effects that happen at start/end of turn.

The checked extra-turn texts explicitly skip the intervening checkup step. Other future wording should be compiled into the boundary flags from its own card text rather than assumed to share this exact timing.
