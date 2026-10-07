"""Reproduce top-draw conditioning after a Prize/top-deck swap."""

from __future__ import annotations

import json
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief  # noqa: E402
from prize_slot_visibility import PrizeSlotVisibilityBelief  # noqa: E402
from prize_top_draw_belief import (  # noqa: E402
    draw_observed_top,
    top_draw_outcomes,
)
from prize_top_swap_belief import (  # noqa: E402
    swap_known_top_with_face_down_prize,
)


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _card_by_id(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    path = ROOT / "resources" / "cards" / "en" / f"{set_id}.json"
    cards = json.loads(path.read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def main() -> None:
    trekking_shoes = _card_by_id("swsh10-156")
    trainer_text = " ".join(trekking_shoes.get("rules") or [])
    assert (
        "Look at the top card of your deck. You may put that card into your hand."
        in trainer_text
    )

    positions = PrizePositionBelief.from_exact_composition(
        {"A": 1, "B": 1, "X": 0},
        prize_count=2,
    )
    prizes = PrizeSlotVisibilityBelief.all_face_down(positions)
    joint = swap_known_top_with_face_down_prize(
        prizes,
        position=0,
        incoming_group="X",
    )

    _assert_close(joint.top_probability("A"), 0.5)
    _assert_close(joint.top_probability("B"), 0.5)

    drawn_a = draw_observed_top(joint, "A")
    _assert_close(drawn_a.observation_probability, 0.5)
    _assert_close(
        drawn_a.prizes_after_draw.positions.group_probability_at(0, "X"),
        1.0,
    )
    _assert_close(
        drawn_a.prizes_after_draw.positions.group_probability_at(1, "B"),
        1.0,
    )
    _assert_close(
        drawn_a.prizes_after_draw.positions.group_probability_at(1, "A"),
        0.0,
    )

    drawn_b = draw_observed_top(joint, "B")
    _assert_close(drawn_b.observation_probability, 0.5)
    _assert_close(
        drawn_b.prizes_after_draw.positions.group_probability_at(0, "X"),
        1.0,
    )
    _assert_close(
        drawn_b.prizes_after_draw.positions.group_probability_at(1, "A"),
        1.0,
    )
    _assert_close(
        drawn_b.prizes_after_draw.positions.group_probability_at(1, "B"),
        0.0,
    )

    outcomes = top_draw_outcomes(joint)
    assert {row.drawn_group for row in outcomes} == {"A", "B"}
    _assert_close(
        sum(row.observation_probability for row in outcomes),
        1.0,
    )

    print("Arc Phone-style joint support:")
    for (top_group, prize_state), probability in joint.masses:
        print(
            f"  p={probability:.3f}: top={top_group}, prizes={prize_state}"
        )

    print()
    print("After drawing/observing top A:")
    print(
        "  remaining slot 1 B probability:",
        f"{drawn_a.prizes_after_draw.positions.group_probability_at(1, 'B'):.3f}",
    )
    print("After drawing/observing top B:")
    print(
        "  remaining slot 1 A probability:",
        f"{drawn_b.prizes_after_draw.positions.group_probability_at(1, 'A'):.3f}",
    )
    print()
    print("All correlated top-draw belief checks passed.")


if __name__ == "__main__":
    main()
