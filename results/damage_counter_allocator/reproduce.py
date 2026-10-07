from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from damage_counter_allocator import (  # noqa: E402
    best_by_knockouts,
    best_by_prizes,
    enumerate_counter_allocations,
)


def main() -> None:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sv6.json").read_text(
            encoding="utf-8"
        )
    )
    dragapult = next(card for card in cards if card["id"] == "sv6-130")
    phantom = next(
        attack
        for attack in dragapult["attacks"]
        if attack["name"] == "Phantom Dive"
    )
    assert phantom["text"] == (
        "Put 6 damage counters on your opponent's Benched Pokémon "
        "in any way you like."
    )

    board = make_board(
        make_pokemon("active", "Active"),
        (
            make_pokemon("a", "One-Prize A", damage_counters=7),
            make_pokemon("b", "One-Prize B", damage_counters=5),
            make_pokemon("c", "Three-Prize C", damage_counters=17),
        ),
    )
    hp = {"a": 100, "b": 80, "c": 230}
    prizes = {"a": 1, "b": 1, "c": 3}

    outcomes = enumerate_counter_allocations(
        board,
        target_ids=("a", "b", "c"),
        total_counters=6,
        hp_by_object_id=hp,
        prize_value_by_object_id=prizes,
    )
    assert len(outcomes) == 28
    assert all(
        sum(count for _, count in row.requests) == 6
        for row in outcomes
    )

    ko_best = best_by_knockouts(outcomes)
    assert max(row.knockout_count for row in ko_best) == 2
    assert any(
        row.requests == (("a", 3), ("b", 3), ("c", 0))
        and row.newly_knocked_out_ids == ("a", "b")
        and row.prize_value == 2
        for row in ko_best
    )

    prize_best = best_by_prizes(outcomes)
    assert max(row.prize_value for row in prize_best) == 3
    assert any(
        row.requests == (("a", 0), ("b", 0), ("c", 6))
        and row.newly_knocked_out_ids == ("c",)
        and row.knockout_count == 1
        for row in prize_best
    )

    immune_c = enumerate_counter_allocations(
        board,
        target_ids=("a", "b", "c"),
        total_counters=6,
        hp_by_object_id=hp,
        prize_value_by_object_id=prizes,
        effect_immune_ids=frozenset({"c"}),
    )
    assert max(row.prize_value for row in immune_c) == 2
    wasted = next(
        row
        for row in immune_c
        if row.requests == (("a", 0), ("b", 0), ("c", 6))
    )
    assert wasted.placed == (("a", 0), ("b", 0), ("c", 0))
    assert wasted.newly_knocked_out_ids == ()

    assert enumerate_counter_allocations(
        board,
        target_ids=(),
        total_counters=6,
        hp_by_object_id={},
    ) == ()

    print(
        {
            "allocation_count": len(outcomes),
            "max_kos": max(row.knockout_count for row in outcomes),
            "max_prizes": max(row.prize_value for row in outcomes),
            "immune_c_max_prizes": max(
                row.prize_value for row in immune_c
            ),
        }
    )


if __name__ == "__main__":
    main()
