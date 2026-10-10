# Stadium voluntary effect use must refresh every player's turn

## Finding

Some Stadium effects explicitly say "once during each player's turn."
The in-play instance's use allowance is local to the *current turn*, even
when the same Stadium card remains in play through subsequent turns.

Rulebook B-04 describes both players' ability to use effects on Stadiums
in play and separates those activations from the ordinary Stadium-play
quota. Grand Tree (`sv7-136`) is the concrete Expanded card witness.

A state representation keyed only by a persistent in-play instance ID
would incorrectly treat an effect used on turn T as spent for the rest
of the game's life of that Stadium. The per-instance history needs a
well-defined turn boundary reset. Turn sequencing and Stadium placement
are separate transitions.

## Implementation

`tools/stadium_effect_instance_usage.py` now exports
`begin_stadium_turn(state, action_budget=...)`.
The caller explicitly invokes this at the start of a **new actor turn**.
It preserves physical Stadium placement and any off-board card
identities, resets voluntary Stadium instance-use history, and installs
the next actor's open turn budget (or obtains a fresh budget through
`next_turn()` if none is supplied).

The generic effect source gate already composes this per-instance model.
No Stadium card needs to be played again for the other player to
activate a once-per-player-turn effect.

## Executable witness

`python results/stadium_effect_turn_scope/reproduce.py`

The test uses a physically unchanged in-play Grand Tree and separate
Bulbasaur -> Ivysaur evolution opportunities for different actor turns.

1. Player A activates Grand Tree. A cannot activate it again this turn.
2. The turn ends. The turn-schedule owner creates player B's new turn.
3. Player B activates that same in-play Grand Tree once, without playing
   another Stadium.
4. On player A's next turn, the Stadium can activate again.
5. If the turn schedule grants player A another turn, that new turn also
   refreshes its effect-use opportunity.

The tests require the source gate to recognize the refreshed instance
and prohibit same-turn reuse, while keeping Stadium play quota
independent. Attempts to open a turn with an already-ended budget
raise an error.

## Scope

The helper does not itself advance the game's turn scheduler, identify
the current player, or grant extra turns. Those operations belong to
the repository's turn-sequence kernels. The caller must invoke
`begin_stadium_turn` exactly once per real actor turn, with the
appropriate actor-owned action budget. It is intentionally invalid to
use the helper as a free same-turn refresh action.

This regression uses Grand Tree only as a concrete voluntary-effect
witness. It does not implement every text-specific once-per-game or
otherwise constrained Stadium effect. Continuous Stadium effects do
not use voluntary activation history.

## Confidence

High for the explicit rulebook and card-text meaning, and for the
deterministic turn-boundary state invariant tested here.
