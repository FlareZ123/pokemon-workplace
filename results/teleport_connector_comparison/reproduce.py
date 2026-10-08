"""SFT: exact and physical Quick Ball vs Ultra Ball Sky Field access."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_teleport_capacity_bridge import (
    BenchPokemon, bench_capacity, bench_from_hand,
    sample_state, teleport_room,
)
from build_expanded_legality_baseline import classify_effective_legality
from discard_cost_witness import DiscardSelection
from multicopy_zone_state import ZoneCountState
from stadium_entry_channels import StadiumCopy
from teleport_connector_comparison import Case, calculate, compare, exhaustive
from teleport_discard_payload_line import (
    execute_quick_ball_for_entrant,
    execute_ultra_ball_for_entrant,
    mirror_bench_entries,
    mirror_teleport_to_trainer_zones,
)
from trainer_search_transaction import TrainerSearchExecutionState


def pct(value) -> float:
    return 100.0 * float(value)


def card_checks() -> None:
    observed = {}
    for set_id, card_id in (("swsh1", "swsh1-179"), ("swsh9", "swsh9-150")):
        cards = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        c = next(row for row in cards if row["id"] == card_id)
        assert classify_effective_legality(c)[0] == "Legal"
        observed[c["name"]] = " ".join(c["rules"])
    assert "discard another card from your hand" in observed["Quick Ball"]
    assert "Search your deck for a Basic Pokémon" in observed["Quick Ball"]
    assert "discard 2 other cards from your hand" in observed["Ultra Ball"]
    assert "Search your deck for a Pokémon" in observed["Ultra Ball"]
    print("PASS: both items legal with verified cost and target domain")


def check_probabilities() -> None:
    for needs_payment in (False, True):
        for can_search in (False, True):
            case = Case(
                n=10, prizes=2, seen=4, connectors=2, sky=2,
                discard=2, needs_second_discard=needs_payment,
                target_searchable=can_search,
            )
            assert calculate(case) == exhaustive(case)
            print("PASS: exhaustive =", needs_payment, can_search)

    rows = compare()
    qb = rows["quick_basic"]
    ub = rows["ultra_basic"]
    qe = rows["quick_evolution_access"]
    ue = rows["ultra_evolution_access"]
    assert qb.goal > ub.goal
    assert ue.goal > qe.goal
    assert qb.naturally_held == qe.naturally_held
    assert qb.found_in_deck > 0 and qe.found_in_deck == 0
    assert ub == ue
    print(f"PASS: Quick Ball Basic endpoint {pct(qb.goal):.6f}%")
    print(f"PASS: Ultra Ball Basic endpoint {pct(ub.goal):.6f}%")
    print(f"PASS: Quick Ball Evolution-in-hand endpoint {pct(qe.goal):.6f}%")
    print(f"PASS: Ultra Ball Evolution-in-hand endpoint {pct(ue.goal):.6f}%")
    print(json.dumps({
        name: {
            "searched": str(row.found_in_deck),
            "held": str(row.naturally_held),
            "total_fraction": str(row.goal),
            "total_percent": round(pct(row.goal), 6),
        } for name, row in rows.items()
    }, indent=2))


def check_physical(*, target_held: bool) -> None:
    board = sample_state(
        hand_stadiums=(StadiumCopy("sky-1", "Sky Field"),),
        hand_pokemon=(
            (BenchPokemon("regular_1"), BenchPokemon("searched_basic"))
            if target_held else (BenchPokemon("regular_1"),)
        ),
        stadium_plays_used=1,
    )
    zones = ZoneCountState.from_mapping({
        ("quick_ball", "hand"): 1,
        ("sky_field", "hand"): 1,
        ("collapsed_stadium", "stadium_in_play"): 1,
        ("regular_1", "hand"): 1,
        ("searched_basic", "hand" if target_held else "deck"): 1,
    })
    execution = TrainerSearchExecutionState(zones=zones, budget=board.stadiums.budget)
    obtained = execute_quick_ball_for_entrant(board, execution, target_held=target_held)
    assert obtained.sky_discarded
    assert obtained.trainer.discard_cost == 1
    assert obtained.trainer.after.zones.count("quick_ball", "discard") == 1
    after = teleport_room(obtained.board_after_search, "goth-1")
    assert len(after) == 1
    assert after[0].stadiums.in_play.name == "Sky Field"
    assert after[0].stadiums.budget.stadium_plays_used == 1
    assert bench_capacity(after[0]) == 8
    first = bench_from_hand(after[0], "regular_1")
    assert first is not None
    second = bench_from_hand(first, "searched_basic")
    assert second is not None and len(second.bench) == 6
    moved = mirror_teleport_to_trainer_zones(
        obtained.board_after_search, after[0], obtained.trainer.after.zones
    )
    finished = mirror_bench_entries(moved, "regular_1", "searched_basic")
    assert finished.count("sky_field", "stadium_in_play") == 1
    assert finished.count("collapsed_stadium", "discard") == 1
    assert finished.count("searched_basic", "bench") == 1
    assert all(
        zones.total(name) == finished.total(name)
        for name in ("quick_ball", "sky_field", "regular_1",
                     "searched_basic", "collapsed_stadium")
    )
    print("PASS: one-discard Quick Ball -> Teleport Sky -> two entrants, target held =", target_held)


def check_ultra_extra_payment() -> None:
    board = sample_state(
        hand_stadiums=(StadiumCopy("sky-1", "Sky Field"),),
        hand_pokemon=(BenchPokemon("regular_1"),),
        stadium_plays_used=1,
    )
    zones = ZoneCountState.from_mapping({
        ("ultra_ball", "hand"): 1,
        ("sky_field", "hand"): 1,
        ("collapsed_stadium", "stadium_in_play"): 1,
        ("regular_1", "hand"): 1,
        ("searched_basic", "deck"): 1,
    })
    execution = TrainerSearchExecutionState(zones=zones, budget=board.stadiums.budget)
    try:
        execute_ultra_ball_for_entrant(
            board, execution, discard_selection=DiscardSelection((1, 0, 0))
        )
    except ValueError as exc:
        assert "costs 1, expected 2" in str(exc)
    else:
        raise AssertionError("Ultra Ball illegally used one-card payment")
    print("PASS: Ultra Ball cannot use Quick Ball's one-discard witness")


def main() -> None:
    card_checks()
    check_probabilities()
    check_physical(target_held=False)
    check_physical(target_held=True)
    check_ultra_extra_payment()
    print("teleport_connector_comparison regression: PASS")


if __name__ == "__main__":
    main()
