"""Reproduce the position-aware Prize belief counterexample."""

from __future__ import annotations

import json
from math import isclose, log2
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief  # noqa: E402


def _card_by_id(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    path = ROOT / "resources" / "cards" / "en" / f"{set_id}.json"
    cards = json.loads(path.read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def _rules(card: dict) -> list[str]:
    return list(card.get("rules") or [])


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _assert_same_composition(
    left: PrizePositionBelief,
    right: PrizePositionBelief,
) -> None:
    left_distribution = left.composition_distribution()
    right_distribution = right.composition_distribution()
    assert set(left_distribution) == set(right_distribution)
    for state in left_distribution:
        _assert_close(
            left_distribution[state],
            right_distribution[state],
        )


def main() -> None:
    peonia = _card_by_id("swsh6-149")
    peonia_text = " ".join(_rules(peonia))
    assert "put a card from your hand face down as a Prize card" in peonia_text
    assert "shuffle" not in peonia_text.lower()

    arc_phone = _card_by_id("swsh11-152")
    arc_phone_text = " ".join(_rules(arc_phone))
    assert (
        "switch that card with 1 of your face-down Prize cards"
        in arc_phone_text
    )

    gladion = _card_by_id("sm4-95")
    gladion_text = " ".join(_rules(gladion))
    assert "shuffle this Gladion into your remaining Prize cards" in gladion_text

    manual_path = (
        ROOT
        / "resources"
        / "manual"
        / "EN_advanced_manual-2025-transcription-structured.md"
    )
    manual = manual_path.read_text(encoding="utf-8")
    assert "E-35   Shuffle them face down (implied)" in manual
    assert (
        "neither player has any information on the order of those cards"
        in manual
    )

    composition_only = PrizePositionBelief.from_exact_composition(
        {"TARGET": 1},
        prize_count=6,
    )
    known_position = PrizePositionBelief.from_known_positions(
        ("TARGET", None, None, None, None, None),
        groups=("TARGET",),
    )
    shuffled = known_position.shuffle_positions()

    _assert_same_composition(composition_only, known_position)
    _assert_same_composition(composition_only, shuffled)

    _assert_close(composition_only.composition_entropy_bits(), 0.0)
    _assert_close(known_position.composition_entropy_bits(), 0.0)
    _assert_close(shuffled.composition_entropy_bits(), 0.0)

    _assert_close(
        composition_only.single_group_position_entropy_bits("TARGET"),
        log2(6),
    )
    _assert_close(
        known_position.single_group_position_entropy_bits("TARGET"),
        0.0,
    )
    _assert_close(
        shuffled.single_group_position_entropy_bits("TARGET"),
        log2(6),
    )

    _assert_close(
        composition_only.best_position_probability("TARGET"),
        1 / 6,
    )
    _assert_close(
        known_position.best_position_probability("TARGET"),
        1.0,
    )
    _assert_close(
        shuffled.best_position_probability("TARGET"),
        1 / 6,
    )

    first_slot_known_filler = composition_only.condition_position(0, None)
    _assert_close(
        first_slot_known_filler.best_position_probability("TARGET"),
        1 / 5,
    )

    print("Exact one-target six-Prize composition")
    print(
        "  composition entropy:",
        f"{composition_only.composition_entropy_bits():.9f} bits",
    )
    print(
        "  unknown target-position entropy:",
        f"{composition_only.single_group_position_entropy_bits('TARGET'):.9f} bits",
    )
    print(
        "  best physical-slot hit with unknown order:",
        f"{composition_only.best_position_probability('TARGET'):.9%}",
    )
    print(
        "  best physical-slot hit with known target position:",
        f"{known_position.best_position_probability('TARGET'):.9%}",
    )
    print(
        "  after face-down shuffle:",
        f"{shuffled.best_position_probability('TARGET'):.9%}",
    )
    print(
        "  after ruling out one filler slot:",
        f"{first_slot_known_filler.best_position_probability('TARGET'):.9%}",
    )
    print()
    print("All Prize-position belief checks passed.")


if __name__ == "__main__":
    main()
