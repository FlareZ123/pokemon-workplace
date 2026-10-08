"""SFT: a deliberate Ultra Ball discard makes Sky Field a Teleport payload."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_teleport_capacity_bridge import (
    BenchPokemon,
    bench_capacity,
    bench_from_hand,
    play_stadium,
    sample_state,
    teleport_room,
)
from discard_cost_witness import DiscardSelection
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from stadium_entry_channels import StadiumCopy
from teleport_discard_payload_line import (
    execute_ultra_ball_for_entrant,
    mirror_bench_entries,
    mirror_teleport_to_trainer_zones,
)
from trainer_search_transaction import TrainerSearchExecutionState


def starting_state(*, item_locked=False, roadblock=False):
    sky = StadiumCopy("sky-1", "Sky Field")
    board = sample_state(
        hand_stadiums=(sky,),
        hand_pokemon=(BenchPokemon("regular_1"),),
        stadium_plays_used=1,
        opponent_roadblock_live=roadblock,
    )
    zones = ZoneCountState.from_mapping(
        {
            ("sky_field", "hand"): 1,
            ("ultra_ball", "hand"): 1,
            ("junk_a", "hand"): 1,
            ("junk_b", "hand"): 1,
            ("regular_1", "hand"): 1,
            ("searched_basic", "deck"): 1,
            ("collapsed_stadium", "stadium_in_play"): 1,
        }
    )
    execution = TrainerSearchExecutionState(
        zones=zones,
        budget=board.stadiums.budget,
        channels=PlayerChannels(item_play=not item_locked),
    )
    return board, execution


def assert_conserved(original: ZoneCountState, after: ZoneCountState):
    classes = {c for c, _, _ in original.counts} | {c for c, _, _ in after.counts}
    for card_class in classes:
        assert original.total(card_class) == after.total(card_class), card_class
    print("PASS: each represented card-class total is conserved")


def attempt_entries(board):
    first = bench_from_hand(board, "regular_1")
    if first is None:
        return 0
    second = bench_from_hand(first, "searched_basic")
    return 1 if second is None else 2


def main():
    ultra = json.loads(
        (ROOT / "resources" / "cards" / "en" / "swsh9.json")
        .read_text(encoding="utf-8")
    )
    card = next(row for row in ultra if row["id"] == "swsh9-150")
    assert "discard 2 other cards" in " ".join(card["rules"])
    assert "Search your deck for a Pokémon" in " ".join(card["rules"])
    print("PASS: exact Ultra Ball physical discard and search grounded in swsh9-150")

    # Spent quota blocks the Sky Field that is still physically in hand.
    base, physical = starting_state()
    assert play_stadium(base, "sky-1") == ()
    assert bench_capacity(base) == 4

    # Correct order: Ultra Ball pays Sky + junk_a, searches second Basic.
    # Sky is now a legal discard-zone Teleport Room payload.
    good = execute_ultra_ball_for_entrant(
        base, physical, discard_selection=DiscardSelection((1, 1, 0))
    )
    assert good.sky_discarded
    assert good.trainer.after.zones.count("sky_field", "discard") == 1
    assert good.trainer.after.zones.count("searched_basic", "hand") == 1
    assert good.trainer.after.zones.count("ultra_ball", "discard") == 1
    assert good.trainer.after.budget.stadium_plays_used == 1
    after_teleport = teleport_room(good.board_after_search, "goth-1")
    assert len(after_teleport) == 1
    restored = after_teleport[0]
    assert restored.stadiums.in_play == StadiumCopy("sky-1", "Sky Field")
    assert bench_capacity(restored) == 8
    assert attempt_entries(restored) == 2
    mirror = mirror_teleport_to_trainer_zones(
        good.board_after_search, restored, good.trainer.after.zones
    )
    finished = mirror_bench_entries(mirror, "regular_1", "searched_basic")
    assert finished.count("sky_field", "stadium_in_play") == 1
    assert finished.count("collapsed_stadium", "discard") == 1
    assert finished.count("searched_basic", "bench") == 1
    assert finished.count("regular_1", "bench") == 1
    assert_conserved(physical.zones, finished)
    print("PASS: discard Sky -> Ultra Ball finds entrant -> Teleport Sky -> Bench both")

    # Same Ultra Ball and same number of payment cards, but choose both junk
    # cards. Sky stays in hand and is unusable with Stadium quota spent.
    bad = execute_ultra_ball_for_entrant(
        base, physical, discard_selection=DiscardSelection((0, 1, 1))
    )
    assert not bad.sky_discarded
    assert bad.trainer.after.zones.count("sky_field", "hand") == 1
    after_bad_teleport = teleport_room(bad.board_after_search, "goth-1")
    assert len(after_bad_teleport) == 1
    assert after_bad_teleport[0].stadiums.in_play is None
    assert bench_capacity(after_bad_teleport[0]) == 5
    assert attempt_entries(after_bad_teleport[0]) == 1
    print("PASS: discarding both junk cards strands Sky Field in inaccessible hand")

    # Using Teleport Room too early spends its source-specific Ability window.
    early = teleport_room(base, "goth-1")[0]
    assert early.stadiums.in_play is None
    early_counted = mirror_teleport_to_trainer_zones(base, early, physical.zones)
    early_execution = replace(physical, zones=early_counted)
    delayed_payload = execute_ultra_ball_for_entrant(
        early, early_execution, discard_selection=DiscardSelection((1, 1, 0))
    )
    assert delayed_payload.sky_discarded
    assert teleport_room(delayed_payload.board_after_search, "goth-1") == ()
    assert attempt_entries(delayed_payload.board_after_search) == 1
    print("PASS: Teleport-before-discard order loses the second entrant")

    # Roadblock is a separate restriction despite a successful Stadium change.
    restricted, restricted_zones = starting_state(roadblock=True)
    paid = execute_ultra_ball_for_entrant(
        restricted, restricted_zones, discard_selection=DiscardSelection((1, 1, 0))
    )
    raised = teleport_room(paid.board_after_search, "goth-1")[0]
    assert raised.stadiums.in_play.name == "Sky Field"
    assert bench_capacity(raised) == 4
    assert attempt_entries(raised) == 0
    print("PASS: opponent Roadblock overrides the constructed Sky Field channel")

    # Item lock closes Ultra Ball's payment/search path.
    locked, locked_zones = starting_state(item_locked=True)
    try:
        execute_ultra_ball_for_entrant(
            locked, locked_zones, discard_selection=DiscardSelection((1, 1, 0))
        )
    except ValueError as exc:
        assert "Item play is locked" in str(exc)
    else:
        raise AssertionError("Item lock did not stop Ultra Ball")
    print("PASS: Item lock rejects the physical Ultra Ball transaction")
    print("teleport_discard_payload_line regression: PASS")


if __name__ == "__main__":
    main()
