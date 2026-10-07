"""Regression checks for the generic turn-action budget."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from turn_action_budget import TurnAction, TurnActionBudget, budget_from_flags


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    fresh = TurnActionBudget()
    for action in TurnAction:
        require(fresh.can(action), f"fresh turn should allow {action.value}")

    supporter = fresh.consume(TurnAction.SUPPORTER)
    require(supporter is not None, "first Supporter should consume")
    require(
        not supporter.can(TurnAction.SUPPORTER),
        "second Supporter in the same turn must be unavailable",
    )
    require(
        supporter.can(TurnAction.STADIUM_PLAY),
        "Supporter use must not consume Stadium play",
    )
    require(
        supporter.can(TurnAction.MANUAL_ENERGY_ATTACHMENT),
        "Supporter use must not consume normal Energy attachment",
    )
    require(
        supporter.can(TurnAction.RETREAT),
        "Supporter use must not consume Retreat",
    )

    state = fresh
    for action in (
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
    ):
        state = state.consume(action)
        require(state is not None, f"{action.value} should be independently usable")

    for action in (
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
    ):
        require(not state.can(action), f"{action.value} should now be exhausted")

    attacked = fresh.consume(TurnAction.ATTACK)
    require(attacked is not None and attacked.turn_ended, "attack must end the turn")
    for action in TurnAction:
        require(
            not attacked.can(action),
            f"no generic action should be available after attack: {action.value}",
        )

    ended = supporter.consume(TurnAction.END_TURN)
    require(ended is not None and ended.turn_ended, "voluntary end must close turn")
    require(
        ended.consume(TurnAction.STADIUM_PLAY) is None,
        "actions after voluntary end must be unavailable",
    )

    reset = state.next_turn()
    require(reset == fresh, "next_turn must reset every generic action channel")

    adapted = budget_from_flags(
        supporter_used=True,
        stadium_play_used=True,
        manual_energy_attachment_used=True,
        retreat_used=True,
        turn_ended=False,
    )
    require(
        adapted == state,
        "adapter must reproduce kernels that store usage flags separately",
    )

    print("turn_action_budget regression: PASS")


if __name__ == "__main__":
    main()
