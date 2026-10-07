# Generic per-turn action budget

## Question

Can the rule-level action limits that recur across the repository be represented as one reusable immutable state instead of being duplicated across board, access, and archetype-specific kernels?

This result adds `tools/turn_action_budget.py` and a deterministic regression at `results/turn_action_budget/reproduce.py`.

## Rule basis

The Advanced Player's Rulebook gives the generic limits modeled here:

- a player may use one Supporter during their turn (`I-B-03 Supporters`);
- a player may play one Stadium during their turn (`I-B-04 Stadiums`);
- once during their turn, a player may attach one Energy card from hand (`I-C Energy Cards`);
- Retreating can only be done once per turn (`I-A-03 Retreat`);
- once a player uses an attack, that player's turn ends (`I-A-01 Attacks`);
- a player may also announce the end of the turn without attacking (`I-A-01 Attacks`).

These are global turn channels. Card text can create additional effect-based actions, and those remain separate. For example, attaching Energy through an attack or Supporter effect does not consume the normal Energy attachment unless the card text says otherwise.

## Representation

`TurnActionBudget` is an immutable five-bit state:

- `supporter_used`;
- `stadium_play_used`;
- `manual_energy_attachment_used`;
- `retreat_used`;
- `turn_ended`.

The first four resources are independent. Consuming one does not consume any of the others.

`turn_ended` is an absorbing state for ordinary turn actions. Both attacking and voluntarily ending the turn set it. Once it is set, the generic turn budget rejects every further action.

`next_turn()` returns a fresh budget with every channel reset.

The module also exposes `budget_from_flags(...)` as a migration adapter for existing kernels that currently store these usage flags separately.

## Why this matters

Several repository components already carry overlapping pieces of this state:

- `unified_state_kernel.py` stores manual Energy attachment and Stadium usage, while Supporter usage currently lives inside its Bench substate;
- `board_object_kernel.py` stores Retreat usage;
- archetype-specific planners maintain additional local flags.

Those representations are individually workable, but composition can create impossible states if two subsystems disagree about whether a once-per-turn action has already been spent.

The generic budget supplies one common contract for future composition. A larger canonical state can own one `TurnActionBudget`, while specialized subsystems query or consume the shared channel rather than maintaining competing copies.

## Regression

The reproducer checks:

1. all generic channels are available in a fresh turn;
2. a second Supporter play is rejected after the first;
3. Supporter use leaves Stadium play, normal Energy attachment, and Retreat available;
4. Supporter, Stadium play, normal Energy attachment, and Retreat can each be consumed once in the same turn;
5. each of those four channels is exhausted independently after use;
6. attacking closes the turn and rejects every later generic action;
7. voluntarily ending the turn has the same absorbing effect;
8. `next_turn()` resets every channel;
9. the flag adapter reproduces an equivalent exhausted-but-open budget.

The regression is deterministic and uses no card-database assumptions.

## Scope and limits

This is a mechanical action-budget kernel rather than a complete turn engine.

It deliberately does not decide:

- whether a particular Supporter, Stadium, Energy, retreat, or attack is otherwise legal;
- first-turn restrictions;
- lock effects;
- target legality;
- card-specific extra actions;
- effect-based Energy attachments;
- Stadium effect-use limits;
- attack costs or attack-prevention effects;
- player identity or turn ownership.

Those belong in higher layers. The budget answers only whether the ordinary shared turn channel is still unspent.

## Architectural consequence

The repository's typed-state direction benefits from separating two questions:

1. **Can this action be paid for from the generic turn budget?**
2. **Does the current card/board state make the action legal and strategically useful?**

Keeping those questions separate prevents an access planner from counting a Supporter line after another subsystem has already spent the Supporter action, or a board planner from retreating twice because Retreat usage was tracked in only one representation.

A useful next integration step is to replace the duplicated action flags in `UnifiedState`, `BenchState`, and `BoardState` with one canonical `TurnActionBudget` owned by the composite state.
