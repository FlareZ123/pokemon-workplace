"""Reproduce same-turn execution of a Supporter recovered from Prize cards."""

from __future__ import annotations

from fractions import Fraction
import json
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_action_quota_derivation import derive_board_action_quotas  # noqa: E402
from board_object_kernel import make_board, make_pokemon  # noqa: E402
from turn_action_budget import TurnActionBudget  # noqa: E402
from prize_supporter_execution import (  # noqa: E402
    analyze_prized_supporter_execution,
    analyze_with_dual_brains,
)


def _card_by_id(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    path = ROOT / "resources" / "cards" / "en" / f"{set_id}.json"
    cards = json.loads(path.read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def _trainer_text(card: dict) -> str:
    return " ".join(card.get("rules") or [])


def _assert_close(actual: float, expected: Fraction) -> None:
    if not isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    peonia = _card_by_id("swsh6-149")
    arc_phone = _card_by_id("swsh11-152")
    trekking_shoes = _card_by_id("swsh10-156")
    magnezone = _card_by_id("bw8-46")
    gladion = _card_by_id("sm4-95")

    assert "Supporter" in peonia.get("subtypes", [])
    assert "Put up to 3 Prize cards into your hand" in _trainer_text(peonia)
    assert (
        "switch that card with 1 of your face-down Prize cards"
        in _trainer_text(arc_phone)
    )
    assert (
        "Look at the top card of your deck. You may put that card into your hand."
        in _trainer_text(trekking_shoes)
    )

    assert "Supporter" in gladion.get("subtypes", [])
    assert "Look at your face-down Prize cards and put 1 of them into your hand." in _trainer_text(gladion)

    dual_brains = next(
        ability
        for ability in magnezone.get("abilities", [])
        if ability["name"] == "Dual Brains"
    )
    assert dual_brains["text"] == "During your turn, you may play 2 Supporter cards."

    manual_path = (
        ROOT
        / "resources"
        / "manual"
        / "EN_advanced_manual-2025-transcription-structured.md"
    )
    manual = manual_path.read_text(encoding="utf-8")
    assert "players can use any number of Item cards during their turn" in manual
    assert "players may only use one Supporter during their turn" in manual

    ordinary = analyze_prized_supporter_execution()
    _assert_close(
        ordinary.direct_hand_access_probability,
        Fraction(1, 6),
    )
    _assert_close(
        ordinary.direct_execution_probability,
        Fraction(1, 6),
    )
    _assert_close(
        ordinary.direct_next_turn_execution_probability,
        Fraction(1, 6),
    )
    _assert_close(
        ordinary.peonia_hand_access_probability,
        Fraction(2, 3),
    )
    _assert_close(
        ordinary.peonia_execution_probability,
        Fraction(0, 1),
    )
    _assert_close(
        ordinary.peonia_next_turn_execution_probability,
        Fraction(2, 3),
    )
    _assert_close(
        ordinary.gladion_hand_access_probability,
        Fraction(1, 1),
    )
    _assert_close(
        ordinary.gladion_execution_probability,
        Fraction(0, 1),
    )
    _assert_close(
        ordinary.gladion_next_turn_execution_probability,
        Fraction(1, 1),
    )

    dual = analyze_with_dual_brains()
    assert dual.supporter_limit == 2
    _assert_close(
        dual.direct_hand_access_probability,
        Fraction(1, 6),
    )
    _assert_close(
        dual.direct_execution_probability,
        Fraction(1, 6),
    )
    _assert_close(
        dual.peonia_hand_access_probability,
        Fraction(2, 3),
    )
    _assert_close(
        dual.peonia_execution_probability,
        Fraction(2, 3),
    )
    _assert_close(
        dual.peonia_next_turn_execution_probability,
        Fraction(2, 3),
    )
    _assert_close(
        dual.gladion_hand_access_probability,
        Fraction(1, 1),
    )
    _assert_close(
        dual.gladion_execution_probability,
        Fraction(1, 1),
    )
    _assert_close(
        dual.gladion_next_turn_execution_probability,
        Fraction(1, 1),
    )

    active = make_pokemon("active", "Test Active", print_id="test-active")
    zone = make_pokemon(
        "dual-brains",
        "Magnezone",
        print_id="bw8-46",
        abilities_enabled=True,
    )
    board = make_board(active, (zone,))
    live_budget = derive_board_action_quotas(board, TurnActionBudget())
    live_board_line = analyze_prized_supporter_execution(
        supporter_limit=live_budget.supporter_play_limit,
    )
    _assert_close(
        live_board_line.gladion_execution_probability,
        Fraction(1, 1),
    )

    suppressed_budget = derive_board_action_quotas(
        board,
        TurnActionBudget(),
        suppressed_ability_object_ids=frozenset({"dual-brains"}),
    )
    suppressed_board_line = analyze_prized_supporter_execution(
        supporter_limit=suppressed_budget.supporter_play_limit,
    )
    _assert_close(
        suppressed_board_line.gladion_execution_probability,
        Fraction(0, 1),
    )
    _assert_close(
        suppressed_board_line.peonia_execution_probability,
        Fraction(0, 1),
    )

    locked_channel = analyze_prized_supporter_execution(
        supporter_limit=0,
    )
    _assert_close(
        locked_channel.direct_hand_access_probability,
        Fraction(1, 6),
    )
    _assert_close(
        locked_channel.direct_execution_probability,
        Fraction(0, 1),
    )
    _assert_close(
        locked_channel.peonia_hand_access_probability,
        Fraction(0, 1),
    )
    _assert_close(
        locked_channel.gladion_hand_access_probability,
        Fraction(0, 1),
    )

    print("Ordinary one-Supporter turn:")
    print(
        "  Arc Phone -> Trekking Shoes: "
        f"hand={ordinary.direct_hand_access_probability:.9f}, "
        f"execute-now={ordinary.direct_execution_probability:.9f}, "
        f"execute-next={ordinary.direct_next_turn_execution_probability:.9f}"
    )
    print(
        "  Peonia -> Arc Phone -> Trekking Shoes: "
        f"hand={ordinary.peonia_hand_access_probability:.9f}, "
        f"execute-now={ordinary.peonia_execution_probability:.9f}, "
        f"execute-next={ordinary.peonia_next_turn_execution_probability:.9f}"
    )

    print(
        "  Gladion: "
        f"hand={ordinary.gladion_hand_access_probability:.9f}, "
        f"execute-now={ordinary.gladion_execution_probability:.9f}, "
        f"execute-next={ordinary.gladion_next_turn_execution_probability:.9f}"
    )

    print()
    print("Dual Brains turn:")
    print(
        "  Peonia -> Arc Phone -> Trekking Shoes: "
        f"hand={dual.peonia_hand_access_probability:.9f}, "
        f"execute={dual.peonia_execution_probability:.9f}"
    )
    print(
        "  Gladion: "
        f"hand={dual.gladion_hand_access_probability:.9f}, "
        f"execute={dual.gladion_execution_probability:.9f}"
    )

    print()
    print("Board-derived Dual Brains:")
    print(
        "  live Gladion execution="
        f"{live_board_line.gladion_execution_probability:.9f}"
    )
    print(
        "  suppressed Gladion execution="
        f"{suppressed_board_line.gladion_execution_probability:.9f}"
    )

    print()
    print("Hand-access probability and executable-line probability can diverge.")
    print("All Prized Supporter execution checks passed.")


if __name__ == "__main__":
    main()
