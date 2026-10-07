"""Reproduce the state-level option value of holding a shared connector."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_competing_policy import competing_action_values


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def _symmetric_wait_state() -> None:
    expected = {
        2: (0.1, 0.05128205128205128),
        3: (0.19230769230769232, 0.10121457489878541),
        4: (0.2773279352226721, 0.14979757085020243),
        5: (0.3554546449283291, 0.19703103913630227),
        6: (0.4270707954918481, 0.24291497975708498),
    }

    print("Turns | wait | search either channel")
    for turns, (wait_expected, search_expected) in expected.items():
        values = competing_action_values(
            turns_remaining=turns,
            critical_remaining=1,
            setup_secured=False,
            rescue_in_hand=0,
            connector_in_hand=1,
            disposable_in_hand=2,
            setup_in_deck=2,
            rescue_in_deck=2,
            connector_in_deck=0,
            disposable_in_deck=20,
            other_in_deck=16,
            discard_cost=2,
        )

        _assert_close(values["wait"], wait_expected)
        _assert_close(values["search_setup"], search_expected)
        _assert_close(values["search_rescue_hold"], search_expected)
        _assert_close(values["search_rescue_play"], search_expected)

        print(
            f"{turns:5d} | "
            f"{values['wait']:.6%} | "
            f"{values['search_setup']:.6%}"
        )

    two_turn = competing_action_values(
        turns_remaining=2,
        critical_remaining=1,
        setup_secured=False,
        rescue_in_hand=0,
        connector_in_hand=1,
        disposable_in_hand=2,
        setup_in_deck=2,
        rescue_in_deck=2,
        connector_in_deck=0,
        disposable_in_deck=20,
        other_in_deck=16,
        discard_cost=2,
    )
    _assert_close(two_turn["wait"], 4 / 40)
    _assert_close(two_turn["search_setup"], 2 / 39)


def _deadline_states() -> None:
    setup_needed = competing_action_values(
        turns_remaining=1,
        critical_remaining=1,
        setup_secured=False,
        rescue_in_hand=1,
        connector_in_hand=1,
        disposable_in_hand=2,
        setup_in_deck=2,
        rescue_in_deck=2,
        connector_in_deck=0,
        disposable_in_deck=20,
        other_in_deck=16,
        discard_cost=2,
    )
    _assert_close(setup_needed["search_setup_play_rescue"], 1.0)
    _assert_close(setup_needed["wait"], 0.0)
    _assert_close(setup_needed["play_rescue"], 0.0)

    rescue_needed = competing_action_values(
        turns_remaining=1,
        critical_remaining=1,
        setup_secured=True,
        rescue_in_hand=0,
        connector_in_hand=1,
        disposable_in_hand=2,
        setup_in_deck=2,
        rescue_in_deck=2,
        connector_in_deck=0,
        disposable_in_deck=20,
        other_in_deck=16,
        discard_cost=2,
    )
    _assert_close(rescue_needed["search_rescue_play"], 1.0)
    _assert_close(rescue_needed["wait"], 0.0)

    print()
    print("Deadline checks")
    print(
        "Rescue already in hand, setup missing: "
        f"search setup + play rescue = "
        f"{setup_needed['search_setup_play_rescue']:.6%}"
    )
    print(
        "Setup already secured, rescue missing: "
        f"search rescue + play = "
        f"{rescue_needed['search_rescue_play']:.6%}"
    )


if __name__ == "__main__":
    _symmetric_wait_state()
    _deadline_states()
    print()
    print("All connector option-value checks passed.")
