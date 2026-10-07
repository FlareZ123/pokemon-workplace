"""Regression checks for the generic turn-action budget."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality
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

    # Expanded-legal Magnezone bw8-46 has Dual Brains:
    # "During your turn, you may play 2 Supporter cards."
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / "bw8.json").read_text(
            encoding="utf-8"
        )
    )
    magnezone = next(card for card in cards if card["id"] == "bw8-46")
    status, source = classify_effective_legality(magnezone)
    require(status == "Legal", f"bw8-46 legality should be Legal, got {status}")
    require(source == "database", f"unexpected bw8-46 legality source: {source}")
    require(
        magnezone["abilities"][0]["name"] == "Dual Brains"
        and magnezone["abilities"][0]["text"]
        == "During your turn, you may play 2 Supporter cards.",
        "bw8-46 must preserve the Dual Brains counterexample text",
    )

    dual_brains = fresh.with_limit(TurnAction.SUPPORTER, 2)
    first_supporter = dual_brains.consume(TurnAction.SUPPORTER)
    require(first_supporter is not None, "Dual Brains must allow first Supporter")
    require(first_supporter.supporter_used, "legacy used alias should be true")
    require(
        first_supporter.can(TurnAction.SUPPORTER),
        "Dual Brains must still allow a second Supporter after the first",
    )
    second_supporter = first_supporter.consume(TurnAction.SUPPORTER)
    require(second_supporter is not None, "Dual Brains must allow second Supporter")
    require(
        second_supporter.supporter_plays_used == 2,
        "Dual Brains budget must record two Supporter plays",
    )
    require(
        not second_supporter.can(TurnAction.SUPPORTER),
        "Dual Brains must not allow a third Supporter",
    )
    next_dual_turn = second_supporter.next_turn()
    require(
        next_dual_turn.supporter_play_limit == 2
        and next_dual_turn.supporter_plays_used == 0,
        "next_turn must reset usage while preserving a derived Supporter limit",
    )

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
