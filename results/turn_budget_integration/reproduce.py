"""Reproduce legacy split-state projection into TurnActionBudget."""

from __future__ import annotations

from dataclasses import replace
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchState
from board_object_kernel import make_board, make_pokemon
from legacy_turn_budget_bridge import (
    apply_budget_to_board,
    apply_budget_to_unified,
    project_composite_turn_budget,
    project_unified_turn_budget,
)
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def main() -> None:
    unified = make_state({})
    active = make_pokemon("active-1", "Test Active")
    board = make_board(active)

    fresh = project_composite_turn_budget(unified, board)
    assert fresh == TurnActionBudget()

    split = replace(
        unified,
        bench=BenchState(supporter_used=True),
        stadium_used=True,
        manual_attachment_used=True,
    )
    board_after_retreat = replace(board, retreat_used=True)
    projected = project_composite_turn_budget(split, board_after_retreat)

    assert projected.supporter_used
    assert projected.stadium_play_used
    assert projected.manual_energy_attachment_used
    assert projected.retreat_used
    assert not projected.turn_ended
    assert projected.can(TurnAction.ATTACK)
    assert not projected.can(TurnAction.SUPPORTER)
    assert not projected.can(TurnAction.STADIUM_PLAY)
    assert not projected.can(TurnAction.MANUAL_ENERGY_ATTACHMENT)
    assert not projected.can(TurnAction.RETREAT)

    ended_unified = replace(
        split,
        bench=replace(split.bench, turn_ended=True),
    )
    ended = project_composite_turn_budget(ended_unified, board_after_retreat)
    for action in TurnAction:
        assert not ended.can(action)

    target = TurnActionBudget(
        supporter_used=True,
        stadium_play_used=False,
        manual_energy_attachment_used=True,
        retreat_used=True,
        turn_ended=False,
    )
    synced_unified = apply_budget_to_unified(unified, target)
    synced_board = apply_budget_to_board(board, target)
    assert project_composite_turn_budget(synced_unified, synced_board) == target

    unified_only = project_unified_turn_budget(
        synced_unified,
        retreat_used=True,
    )
    assert unified_only == target

    reset = target.next_turn()
    reset_unified = apply_budget_to_unified(synced_unified, reset)
    reset_board = apply_budget_to_board(synced_board, reset)
    assert project_composite_turn_budget(reset_unified, reset_board) == reset

    print("legacy_turn_budget_bridge regression: PASS")


if __name__ == "__main__":
    main()
