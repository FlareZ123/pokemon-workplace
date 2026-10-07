"""Reproduce Omega Barrage attack-window semantics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from turn_action_budget import TurnAction  # noqa: E402
from turn_attack_window import (  # noqa: E402
    can_take_action,
    consume_action,
    fresh_turn,
)


def bunnelby_trait_text() -> str:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / "xy5.json").read_text(
            encoding="utf-8"
        )
    )
    bunnelby = next(card for card in rows if card["id"] == "xy5-121")
    assert (bunnelby.get("legalities") or {}).get("expanded") == "Legal"
    trait = bunnelby.get("ancientTrait") or {}
    assert trait.get("name") == "Ω Barrage"
    return trait.get("text") or ""


def main() -> None:
    assert "may attack twice a turn" in bunnelby_trait_text().lower()

    ordinary = fresh_turn(attack_limit=1)
    ordinary = consume_action(
        ordinary,
        TurnAction.ATTACK,
        attacker_object_id="ordinary-active",
    )
    assert ordinary is not None
    assert ordinary.attack_phase.turn_ended
    assert ordinary.action_budget.turn_ended

    omega = fresh_turn(attack_limit=2)
    omega = consume_action(omega, TurnAction.SUPPORTER)
    assert omega is not None

    first = consume_action(
        omega,
        TurnAction.ATTACK,
        attacker_object_id="omega-bunnelby",
    )
    assert first is not None
    assert first.attack_phase.attacks_used == 1
    assert not first.attack_phase.turn_ended
    assert not first.action_budget.turn_ended

    for action in (
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
    ):
        assert not can_take_action(first, action)

    assert can_take_action(
        first,
        TurnAction.ATTACK,
        attacker_object_id="omega-bunnelby",
    )
    assert not can_take_action(
        first,
        TurnAction.ATTACK,
        attacker_object_id="different-active",
    )
    assert can_take_action(first, TurnAction.END_TURN)

    second = consume_action(
        first,
        TurnAction.ATTACK,
        attacker_object_id="omega-bunnelby",
    )
    assert second is not None
    assert second.attack_phase.attacks_used == 2
    assert second.attack_phase.turn_ended
    assert second.action_budget.turn_ended

    optional = fresh_turn(attack_limit=2)
    optional = consume_action(
        optional,
        TurnAction.ATTACK,
        attacker_object_id="omega-bunnelby",
    )
    assert optional is not None
    optional = consume_action(optional, TurnAction.END_TURN)
    assert optional is not None
    assert optional.attack_phase.attacks_used == 1
    assert optional.attack_phase.turn_ended
    assert optional.action_budget.turn_ended

    print("Omega Barrage attack-window regression: PASS")


if __name__ == "__main__":
    main()
