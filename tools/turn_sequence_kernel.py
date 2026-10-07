"""Minimal turn-sequence kernel for ordinary and extra-turn boundaries."""

from __future__ import annotations

from dataclasses import dataclass, replace

from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class TurnSequenceState:
    current_player: str
    other_player: str
    budget: TurnActionBudget = TurnActionBudget()
    extra_turn_queued: bool = False
    skip_checkup_before_next_turn: bool = False

    def __post_init__(self) -> None:
        if not self.current_player or not self.other_player:
            raise ValueError("player identifiers must be non-empty")
        if self.current_player == self.other_player:
            raise ValueError("players must be distinct")
        if self.skip_checkup_before_next_turn and not self.extra_turn_queued:
            raise ValueError("checkup skip requires a queued extra turn")


@dataclass(frozen=True)
class TurnAdvance:
    state: TurnSequenceState
    pokemon_checkup_occurs: bool
    same_player_continues: bool


def close_turn_with_attack(
    state: TurnSequenceState,
    *,
    take_another_turn: bool = False,
    skip_pokemon_checkup: bool = False,
) -> TurnSequenceState | None:
    """Use the current turn's attack boundary and optionally queue an extra turn."""

    if skip_pokemon_checkup and not take_another_turn:
        raise ValueError("checkup skip requires an extra-turn effect")

    budget = state.budget.consume(TurnAction.ATTACK)
    if budget is None:
        return None

    return replace(
        state,
        budget=budget,
        extra_turn_queued=take_another_turn,
        skip_checkup_before_next_turn=(
            take_another_turn and skip_pokemon_checkup
        ),
    )


def close_turn_voluntarily(state: TurnSequenceState) -> TurnSequenceState | None:
    """End the current turn without attacking."""

    budget = state.budget.consume(TurnAction.END_TURN)
    if budget is None:
        return None
    return replace(
        state,
        budget=budget,
        extra_turn_queued=False,
        skip_checkup_before_next_turn=False,
    )


def advance_turn(state: TurnSequenceState) -> TurnAdvance | None:
    """Resolve the boundary and start the next turn with reset usage."""

    if not state.budget.turn_ended:
        return None

    next_budget = state.budget.next_turn()
    if state.extra_turn_queued:
        next_state = TurnSequenceState(
            current_player=state.current_player,
            other_player=state.other_player,
            budget=next_budget,
        )
        return TurnAdvance(
            state=next_state,
            pokemon_checkup_occurs=not state.skip_checkup_before_next_turn,
            same_player_continues=True,
        )

    next_state = TurnSequenceState(
        current_player=state.other_player,
        other_player=state.current_player,
        budget=next_budget,
    )
    return TurnAdvance(
        state=next_state,
        pokemon_checkup_occurs=True,
        same_player_continues=False,
    )
