"""Reproduce turn scheduling with UnifiedState-owned action budgets."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from canonical_turn_sequence_owner import (
    TurnScheduleState,
    advance_turn,
    close_turn_voluntarily,
    close_turn_with_attack,
)
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def _spend(budget: TurnActionBudget, *actions: TurnAction) -> TurnActionBudget:
    for action in actions:
        next_budget = budget.consume(action)
        assert next_budget is not None
        budget = next_budget
    return budget


def main() -> None:
    assert "budget" not in TurnScheduleState.__dataclass_fields__
    assert "other_budget" not in TurnScheduleState.__dataclass_fields__

    a_budget = TurnActionBudget().with_limit(TurnAction.SUPPORTER, 2)
    a_budget = _spend(
        a_budget,
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
    )
    b_budget = _spend(TurnActionBudget(), TurnAction.SUPPORTER)

    a = make_state({}, turn_budget=a_budget)
    b = make_state({}, turn_budget=b_budget)
    schedule = TurnScheduleState("A", "B")

    # Stale compatibility bits do not own the scheduling state.
    a = replace(
        a,
        bench=replace(a.bench, supporter_used=False, turn_ended=False),
        stadium_used=False,
        manual_attachment_used=False,
    )

    extra_end = close_turn_with_attack(
        schedule,
        a,
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    assert extra_end is not None
    extra_schedule, a_closed = extra_end
    assert a_closed.turn_budget is not None
    assert a_closed.turn_budget.turn_ended

    extra = advance_turn(extra_schedule, a_closed, b)
    assert extra is not None
    assert extra.schedule.current_player == "A"
    assert extra.schedule.other_player == "B"
    assert extra.same_player_continues
    assert not extra.pokemon_checkup_occurs
    assert extra.current_state.turn_budget is not None
    assert extra.current_state.turn_budget.supporter_play_limit == 2
    assert extra.current_state.turn_budget.supporter_plays_used == 0
    assert extra.current_state.turn_budget.stadium_plays_used == 0
    assert extra.current_state.turn_budget.manual_energy_attachments_used == 0
    assert extra.current_state.turn_budget.retreats_used == 0
    assert not extra.current_state.turn_budget.turn_ended

    # The non-current player's retained history has not been reset yet.
    assert extra.other_state.turn_budget == b_budget

    ordinary_end = close_turn_with_attack(
        extra.schedule,
        extra.current_state,
    )
    assert ordinary_end is not None
    ordinary_schedule, a_second_closed = ordinary_end

    to_b = advance_turn(
        ordinary_schedule,
        a_second_closed,
        extra.other_state,
    )
    assert to_b is not None
    assert to_b.schedule.current_player == "B"
    assert to_b.pokemon_checkup_occurs
    assert not to_b.same_player_continues
    assert to_b.current_state.turn_budget is not None
    assert to_b.current_state.turn_budget.supporter_play_limit == 1
    assert to_b.current_state.turn_budget.supporter_plays_used == 0
    assert to_b.other_state.turn_budget is not None
    assert to_b.other_state.turn_budget.supporter_play_limit == 2
    assert to_b.other_state.turn_budget.turn_ended

    # When A becomes current again, A's own two-Supporter limit returns and
    # usage resets. B's limit never leaks across the handoff.
    b_end = close_turn_with_attack(to_b.schedule, to_b.current_state)
    assert b_end is not None
    b_schedule, b_closed = b_end
    back_to_a = advance_turn(b_schedule, b_closed, to_b.other_state)
    assert back_to_a is not None
    assert back_to_a.schedule.current_player == "A"
    assert back_to_a.current_state.turn_budget is not None
    assert back_to_a.current_state.turn_budget.supporter_play_limit == 2
    assert back_to_a.current_state.turn_budget.supporter_plays_used == 0

    # Voluntary end uses the same owner and ordinary handoff semantics.
    voluntary = close_turn_voluntarily(
        back_to_a.schedule,
        back_to_a.current_state,
    )
    assert voluntary is not None
    voluntary_schedule, a_voluntary_closed = voluntary
    after_voluntary = advance_turn(
        voluntary_schedule,
        a_voluntary_closed,
        back_to_a.other_state,
    )
    assert after_voluntary is not None
    assert after_voluntary.schedule.current_player == "B"
    assert after_voluntary.pokemon_checkup_occurs

    print("canonical_turn_sequence_owner regression: PASS")


if __name__ == "__main__":
    main()
