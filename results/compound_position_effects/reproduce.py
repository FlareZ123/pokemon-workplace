from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from compound_position_effects import (
    compile_compound_position_profiles,
    execute_compound_position_effect,
)


def one(rows, card_id: str):
    matches = tuple(row for row in rows if row.card_id == card_id)
    assert len(matches) == 1
    return matches[0]


def main() -> None:
    rows = compile_compound_position_profiles(ROOT / "resources")
    assert len(rows) == 19
    assert len({row.name for row in rows}) == 10
    assert Counter(row.connector for row in rows) == Counter(
        {"if_you_do": 12, "then": 7}
    )

    baltoy = one(rows, "sv3-94")
    blastoise = one(rows, "xy12-21")
    assert baltoy.connector == "if_you_do"
    assert blastoise.connector == "then"

    # Literal compilation deliberately refuses two obvious database-typo bodies.
    assert not any(row.card_id == "xyp-XY122" for row in rows)
    assert not any(row.card_id == "me55-20" for row in rows)

    actor = make_board(
        make_pokemon("actor-active", "Spinner"),
        (
            make_pokemon("actor-bench-a", "Pivot A"),
            make_pokemon("actor-bench-b", "Pivot B"),
        ),
    )
    opponent = make_board(
        make_pokemon("opp-active", "Wall"),
        (
            make_pokemon("opp-bench-a", "Replacement A"),
            make_pokemon("opp-bench-b", "Replacement B"),
        ),
    )

    both = execute_compound_position_effect(
        baltoy,
        actor,
        opponent,
        actor_bench_choice="actor-bench-a",
        opponent_bench_choice="opp-bench-b",
    )
    assert both.actor_switched and both.opponent_switched
    assert both.actor_board.active_id == "actor-bench-a"
    assert both.opponent_board.active_id == "opp-bench-b"

    # If the first switch cannot happen, the dependent second clause is skipped.
    actor_without_bench = make_board(make_pokemon("solo-actor", "Spinner"))
    first_fails = execute_compound_position_effect(
        baltoy,
        actor_without_bench,
        opponent,
        actor_bench_choice=None,
        opponent_bench_choice="opp-bench-a",
    )
    assert not first_fails.actor_switched
    assert not first_fails.opponent_switched
    assert first_fails.opponent_board == opponent

    actor_blocked = execute_compound_position_effect(
        baltoy,
        actor,
        opponent,
        actor_bench_choice="actor-bench-a",
        opponent_bench_choice="opp-bench-a",
        blocked_actor_effect_targets=frozenset({"actor-active"}),
    )
    assert not actor_blocked.actor_switched
    assert not actor_blocked.opponent_switched

    # If the first succeeds and the second cannot, the first movement persists.
    opponent_without_bench = make_board(make_pokemon("solo-opp", "Wall"))
    second_fails = execute_compound_position_effect(
        baltoy,
        actor,
        opponent_without_bench,
        actor_bench_choice="actor-bench-b",
        opponent_bench_choice=None,
    )
    assert second_fails.actor_switched
    assert not second_fails.opponent_switched
    assert second_fails.actor_board.active_id == "actor-bench-b"
    assert second_fails.opponent_board == opponent_without_bench

    second_blocked = execute_compound_position_effect(
        baltoy,
        actor,
        opponent,
        actor_bench_choice="actor-bench-a",
        opponent_bench_choice="opp-bench-a",
        blocked_opponent_effect_targets=frozenset({"opp-active"}),
    )
    assert second_blocked.actor_switched
    assert not second_blocked.opponent_switched
    assert second_blocked.actor_board.active_id == "actor-bench-a"
    assert second_blocked.opponent_board == opponent

    print("compound position regression passed")
    print(f"profiles={len(rows)} names={len({row.name for row in rows})}")
    print(dict(sorted(Counter(row.connector for row in rows).items())))


if __name__ == "__main__":
    main()
