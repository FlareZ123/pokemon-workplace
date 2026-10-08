"""SFT: goal-level Teleport access, including a naturally held target."""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_teleport_capacity_bridge import (
    BenchPokemon, bench_capacity, bench_from_hand,
    sample_state, teleport_room,
)
from discard_cost_witness import DiscardSelection
from multicopy_zone_state import ZoneCountState
from stadium_entry_channels import StadiumCopy
from teleport_discard_goal_closure import (
    exhaustive_goal_k0,
    goal_level_k0,
    goal_level_k1,
    target_naturally_in_hand_k0,
    target_naturally_in_hand_k1,
)
from teleport_discard_access_bound import (
    UnknownPool, k0_payload_probability, k1_payload_probability,
)
from teleport_discard_payload_line import (
    execute_ultra_ball_with_held_entrant,
    mirror_bench_entries,
    mirror_teleport_to_trainer_zones,
)
from trainer_search_transaction import TrainerSearchExecutionState


def pct(value: Fraction) -> float:
    return 100.0 * float(value)


def test_exact() -> None:
    for spec in (
        UnknownPool(10, 2, 3, 2, 2, 2),
        UnknownPool(11, 3, 4, 2, 2, 2),
        UnknownPool(9, 0, 5, 2, 2, 2),
    ):
        ex_deck, ex_hand, ex_union = exhaustive_goal_k0(spec)
        assert ex_deck == k0_payload_probability(spec)
        assert ex_hand == target_naturally_in_hand_k0(spec)
        assert ex_union == goal_level_k0(spec)
        assert ex_union == ex_hand + ex_deck
        print("PASS: exhaustive target-in-hand/deck partition:", spec.total, spec.prizes, spec.seen)

    spec = UnknownPool(46, 6, 5, 4, 2, 16)
    path = k0_payload_probability(spec)
    natural = target_naturally_in_hand_k0(spec)
    goal = goal_level_k0(spec)
    assert path == Fraction(7280, 174537)
    assert natural > 0
    assert goal == path + natural
    assert goal > path
    print(f"PASS: K0 searched-only {pct(path):.6f}%")
    print(f"PASS: K0 target naturally held branch {pct(natural):.6f}%")
    print(f"PASS: K0 goal-level union {pct(goal):.6f}%")

    k1_search = k1_payload_probability(
        40, 5, unprized_ultra_ball=4,
        unprized_sky_field=2, unprized_approved_discard=16,
    )
    k1_natural = target_naturally_in_hand_k1(
        40, 5, unprized_ultra_ball=4,
        unprized_sky_field=2, unprized_approved_discard=16,
    )
    k1_goal = goal_level_k1(
        40, 5, unprized_ultra_ball=4,
        unprized_sky_field=2, unprized_approved_discard=16,
    )
    assert k1_goal == k1_search + k1_natural > k1_search
    assert goal_level_k1(
        40, 5, unprized_ultra_ball=4,
        unprized_sky_field=2, unprized_approved_discard=16,
        target_prized=True,
    ) == 0
    print(f"PASS: K1 searched-only {pct(k1_search):.6f}%")
    print(f"PASS: K1 natural-in-hand {pct(k1_natural):.6f}%")
    print(f"PASS: K1 goal-level union {pct(k1_goal):.6f}%")
    print(json.dumps({
        "k0_search_only": str(path),
        "k0_natural": str(natural),
        "k0_goal": str(goal),
        "k0_search_only_percent": round(pct(path), 6),
        "k0_natural_percent": round(pct(natural), 6),
        "k0_goal_percent": round(pct(goal), 6),
        "k1_goal": str(k1_goal),
        "k1_goal_percent": round(pct(k1_goal), 6),
    }, indent=2))


def test_physical_held_target() -> None:
    cards = {
        ("ultra_ball", "hand"): 1,
        ("sky_field", "hand"): 1,
        ("junk_a", "hand"): 1,
        ("junk_b", "hand"): 1,
        ("regular_1", "hand"): 1,
        ("searched_basic", "hand"): 1,
        ("collapsed_stadium", "stadium_in_play"): 1,
    }
    initial_zones = ZoneCountState.from_mapping(cards)
    board = sample_state(
        hand_stadiums=(StadiumCopy("sky-1", "Sky Field"),),
        hand_pokemon=(
            BenchPokemon("regular_1"), BenchPokemon("searched_basic"),
        ),
        stadium_plays_used=1,
    )
    execution = TrainerSearchExecutionState(
        zones=initial_zones, budget=board.stadiums.budget
    )
    paid = execute_ultra_ball_with_held_entrant(
        board, execution, discard_selection=DiscardSelection((1, 1, 0))
    )
    assert paid.sky_discarded
    assert paid.trainer.after.zones.count("searched_basic", "hand") == 1
    assert paid.trainer.after.zones.count("searched_basic", "deck") == 0
    assert paid.trainer.after.zones.count("ultra_ball", "discard") == 1
    assert paid.trainer.discard_cost == 2
    after = teleport_room(paid.board_after_search, "goth-1")
    assert len(after) == 1 and after[0].stadiums.in_play.name == "Sky Field"
    assert bench_capacity(after[0]) == 8
    first = bench_from_hand(after[0], "regular_1")
    assert first is not None
    second = bench_from_hand(first, "searched_basic")
    assert second is not None and len(second.bench) == 6
    zones = mirror_teleport_to_trainer_zones(
        paid.board_after_search, after[0], paid.trainer.after.zones
    )
    finished = mirror_bench_entries(zones, "regular_1", "searched_basic")
    assert finished.count("searched_basic", "bench") == 1
    for card_class, _, _ in initial_zones.counts:
        assert initial_zones.total(card_class) == finished.total(card_class)
    print("PASS: legal zero-retrieval Ultra Ball payment -> Sky Field -> both existing Basics")

    # Choosing junk + junk leaves Sky Field in hand; only one Bench slot opens.
    non_payload = execute_ultra_ball_with_held_entrant(
        board, execution, discard_selection=DiscardSelection((0, 1, 1))
    )
    none = teleport_room(non_payload.board_after_search, "goth-1")
    assert len(none) == 1 and none[0].stadiums.in_play is None
    assert bench_capacity(none[0]) == 5
    first_only = bench_from_hand(none[0], "regular_1")
    assert first_only is not None
    assert bench_from_hand(first_only, "searched_basic") is None
    print("PASS: held target still needs a correctly selected Sky Field discard")


def main() -> None:
    test_exact()
    test_physical_held_target()
    print("teleport_discard_goal_closure regression: PASS")


if __name__ == "__main__":
    main()
