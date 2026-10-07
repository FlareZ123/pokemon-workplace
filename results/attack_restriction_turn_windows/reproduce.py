"""Reproduce attack-restriction turn windows, including extra turns."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_restriction_turn_windows import (
    begin_turn,
    create_attack_restriction_window,
    end_turn,
    restriction_affects_player,
)
from attack_source_scoped_restrictions import materialize_attack_restriction
from source_scoped_restriction_activation import build_restriction_activation_profiles
from turn_sequence_kernel import (
    TurnSequenceState,
    advance_turn,
    close_turn_voluntarily,
    close_turn_with_attack,
)


def _one(profiles, card_id: str, needle: str):
    matches = [
        row
        for row in profiles
        if row.restriction.card_id == card_id
        and (
            needle in row.restriction.source
            or needle in row.restriction.text
        )
    ]
    assert len(matches) == 1, (card_id, needle, len(matches))
    return matches[0]


def main() -> None:
    profiles = build_restriction_activation_profiles(ROOT / "resources")

    psyduck = _one(profiles, "sm9-26", "Headache")
    psyduck_restriction = materialize_attack_restriction(
        psyduck,
        coin_heads=True,
    )
    assert psyduck_restriction is not None
    psyduck_window = create_attack_restriction_window(
        psyduck,
        psyduck_restriction,
        source_player="A",
        other_player="B",
    )

    schedule = TurnSequenceState(current_player="A", other_player="B")
    closed = close_turn_with_attack(
        schedule,
        take_another_turn=True,
    )
    assert closed is not None
    extra = advance_turn(closed)
    assert extra is not None
    assert extra.same_player_continues
    assert extra.state.current_player == "A"

    psyduck_window = begin_turn(psyduck_window, "A")
    assert not restriction_affects_player(psyduck_window, "A")
    assert not restriction_affects_player(psyduck_window, "B")
    psyduck_window = end_turn(psyduck_window, "A")

    extra_closed = close_turn_voluntarily(extra.state)
    assert extra_closed is not None
    opponent_turn = advance_turn(extra_closed)
    assert opponent_turn is not None
    assert opponent_turn.state.current_player == "B"

    psyduck_window = begin_turn(psyduck_window, "B")
    assert restriction_affects_player(psyduck_window, "B")
    assert not restriction_affects_player(psyduck_window, "A")
    psyduck_window = end_turn(psyduck_window, "B")
    assert not restriction_affects_player(psyduck_window, "B")

    vanilluxe = _one(profiles, "xy8-45", "Frigid Breath")
    vanilluxe_restriction = materialize_attack_restriction(vanilluxe)
    assert vanilluxe_restriction is not None
    vanilluxe_window = create_attack_restriction_window(
        vanilluxe,
        vanilluxe_restriction,
        source_player="A",
        other_player="B",
    )

    ordinary = TurnSequenceState(current_player="A", other_player="B")
    ordinary_closed = close_turn_with_attack(ordinary)
    assert ordinary_closed is not None
    first_b = advance_turn(ordinary_closed)
    assert first_b is not None
    assert first_b.state.current_player == "B"

    vanilluxe_window = begin_turn(vanilluxe_window, "B")
    assert restriction_affects_player(vanilluxe_window, "B")
    assert restriction_affects_player(vanilluxe_window, "A")
    vanilluxe_window = end_turn(vanilluxe_window, "B")
    assert restriction_affects_player(vanilluxe_window, "B")

    b_closed = close_turn_voluntarily(first_b.state)
    assert b_closed is not None
    next_a = advance_turn(b_closed)
    assert next_a is not None
    assert next_a.state.current_player == "A"

    vanilluxe_window = begin_turn(vanilluxe_window, "A")
    assert restriction_affects_player(vanilluxe_window, "A")
    assert restriction_affects_player(vanilluxe_window, "B")
    vanilluxe_window = end_turn(vanilluxe_window, "A")
    assert not restriction_affects_player(vanilluxe_window, "A")
    assert not restriction_affects_player(vanilluxe_window, "B")

    vanilluxe_extra = create_attack_restriction_window(
        vanilluxe,
        vanilluxe_restriction,
        source_player="A",
        other_player="B",
    )
    vanilluxe_extra = begin_turn(vanilluxe_extra, "A")
    assert restriction_affects_player(vanilluxe_extra, "A")
    vanilluxe_extra = end_turn(vanilluxe_extra, "A")
    assert not restriction_affects_player(vanilluxe_extra, "B")

    print(
        json.dumps(
            {
                "opponent_next_turn_waits_through_source_extra_turn": True,
                "opponent_next_turn_expires_after_first_opponent_turn": True,
                "frigid_breath_affects_intervening_opponent_turn": True,
                "frigid_breath_affects_source_next_turn": True,
                "frigid_breath_expires_at_source_next_turn_end": True,
                "source_extra_turn_counts_as_source_next_turn": True,
                "scheduler_integration_verified": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
