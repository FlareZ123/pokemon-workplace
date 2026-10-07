"""Bootstrap thresholds and sequencing for restoring Bench capacity."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from bounded_state_planner import shortest_bounded_plan
from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class RestoreState:
    occupancy: int
    capacity: int
    stadium: str
    tera_in_play: bool
    remover_benched: bool
    tera_entry_done: bool
    ordinary_entry_done: bool
    budget: TurnActionBudget


def _with(state: RestoreState, **changes) -> RestoreState:
    return RestoreState(**(state.__dict__ | changes))


def play_sky_field(state: RestoreState):
    if state.stadium == "sky_field" or state.budget.turn_ended:
        return ()
    budget = state.budget.consume(TurnAction.STADIUM_PLAY)
    if budget is None:
        return ()
    return (("play Sky Field", _with(state, stadium="sky_field", capacity=8, budget=budget)),)


def play_area_zero(state: RestoreState):
    if state.stadium == "area_zero" or state.budget.turn_ended:
        return ()
    budget = state.budget.consume(TurnAction.STADIUM_PLAY)
    if budget is None:
        return ()
    capacity = 8 if state.tera_in_play else 5
    return (("play Area Zero Underdepths", _with(state, stadium="area_zero", capacity=capacity, budget=budget)),)


def bench_pumpkaboo_remover(state: RestoreState):
    if state.remover_benched or state.budget.turn_ended or state.occupancy >= state.capacity:
        return ()
    occupancy = state.occupancy + 1
    return ((
        "Bench Pumpkin Pit remover and discard Stadium",
        _with(state, occupancy=occupancy, capacity=5, stadium="none", remover_benched=True),
    ),)


def bench_tera(state: RestoreState):
    if state.tera_entry_done or state.budget.turn_ended or state.occupancy >= state.capacity:
        return ()
    capacity = 8 if state.stadium == "area_zero" else state.capacity
    return ((
        "Bench Tera entrant",
        _with(state, occupancy=state.occupancy + 1, capacity=capacity, tera_in_play=True, tera_entry_done=True),
    ),)


def bench_ordinary(state: RestoreState):
    if state.ordinary_entry_done or state.budget.turn_ended or state.occupancy >= state.capacity:
        return ()
    return ((
        "Bench ordinary entrant",
        _with(state, occupancy=state.occupancy + 1, ordinary_entry_done=True),
    ),)


def plan(initial_occupancy: int, actions, goal, *, max_depth: int = 5):
    initial = RestoreState(
        occupancy=initial_occupancy,
        capacity=4,
        stadium="collapsed",
        tera_in_play=False,
        remover_benched=False,
        tera_entry_done=False,
        ordinary_entry_done=False,
        budget=TurnActionBudget(),
    )
    witness = shortest_bounded_plan(initial, actions, goal, max_depth=max_depth)
    return None if witness is None else witness.labels


def forced_area_zero_order(first: str):
    state = RestoreState(4, 4, "collapsed", False, False, False, False, TurnActionBudget())
    after_stadium = tuple(play_area_zero(state))[0][1]
    first_action = bench_tera if first == "tera" else bench_ordinary
    second_action = bench_ordinary if first == "tera" else bench_tera
    first_rows = tuple(first_action(after_stadium))
    if not first_rows:
        return {"first": first, "first_legal": False, "second_legal": False}
    after_first = first_rows[0][1]
    second_rows = tuple(second_action(after_first))
    return {
        "first": first,
        "first_legal": True,
        "capacity_after_first": after_first.capacity,
        "occupancy_after_first": after_first.occupancy,
        "second_legal": bool(second_rows),
        "final_capacity": second_rows[0][1].capacity if second_rows else after_first.capacity,
        "final_occupancy": second_rows[0][1].occupancy if second_rows else after_first.occupancy,
    }


def build_result():
    pump_full = plan(
        4,
        (bench_pumpkaboo_remover, bench_ordinary),
        lambda s: s.remover_benched and s.ordinary_entry_done,
    )
    pump_one_slack = plan(
        3,
        (bench_pumpkaboo_remover, bench_ordinary),
        lambda s: s.remover_benched and s.ordinary_entry_done,
    )
    sky_full = plan(
        4,
        (play_sky_field, bench_ordinary),
        lambda s: s.ordinary_entry_done,
    )
    area_two = plan(
        4,
        (play_area_zero, bench_tera, bench_ordinary),
        lambda s: s.tera_entry_done and s.ordinary_entry_done,
    )
    tera_first = forced_area_zero_order("tera")
    ordinary_first = forced_area_zero_order("ordinary")

    assert pump_full is None
    assert pump_one_slack == (
        "Bench Pumpkin Pit remover and discard Stadium",
        "Bench ordinary entrant",
    )
    assert sky_full == ("play Sky Field", "Bench ordinary entrant")
    assert area_two == (
        "play Area Zero Underdepths",
        "Bench Tera entrant",
        "Bench ordinary entrant",
    )
    assert tera_first["second_legal"]
    assert tera_first["capacity_after_first"] == 8
    assert not ordinary_first["second_legal"]
    assert ordinary_first["capacity_after_first"] == 5

    return {
        "card_text_anchors": {
            "pumpkaboo": "Pumpkaboo swsh7-76 / Pumpkin Pit: when played from hand onto the Bench, it may discard a Stadium in play.",
            "chien_pao": "Chien-Pao sv8-56 / Snow Sink has the same relevant hand-to-Bench Stadium-discard geometry.",
            "sky_field": "Sky Field xy6-89 lets each player have 8 Benched Pokémon while it is in play.",
            "area_zero": "Area Zero Underdepths sv7-131: a player with a Tera Pokémon in play can have up to 8 Benched Pokémon; otherwise the expansion does not apply.",
            "collapsed": "Collapsed Stadium swsh9-137/swsh11-215 restricts each player to 4 Benched Pokémon.",
        },
        "plans": {
            "pumpkaboo_from_full_four": pump_full,
            "pumpkaboo_with_one_slack": pump_one_slack,
            "sky_field_from_full_four": sky_full,
            "area_zero_two_entry_plan": area_two,
        },
        "area_zero_forced_order": {
            "tera_first": tera_first,
            "ordinary_first": ordinary_first,
        },
        "findings": {
            "bootstrap_threshold": "a Bench-triggered Stadium remover cannot unlock a full restricted Bench because it must enter the Bench before its removal Ability can resolve",
            "cross_channel_tradeoff": "direct Stadium replacement can restore capacity from zero slack because it spends Stadium bandwidth rather than Bench slack",
            "conditional_expansion_order": "after Area Zero replaces a restriction with no Tera in play, the first reopened default slot must be used by a Tera before additional entrants can exploit capacity 8",
        },
    }


def atomic_write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        temp = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
                temp = Path(handle.name)
            os.replace(temp, path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/bench_capacity_restoration_bootstrap/model.json"))
    args = parser.parse_args()
    result = build_result()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
