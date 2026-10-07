"""Inter-turn exposure of reserved Bench slack to opponent capacity contraction."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from bench_capacity_model import Occupant, optimal_forced_discard


@dataclass(frozen=True)
class ExposureResult:
    label: str
    capacity_before: int
    occupancy_before: int
    slack_before: int
    capacity_after: int
    forced_discards: int
    discarded: tuple[str, ...]
    retained: tuple[str, ...]
    continuation_loss: float
    slack_after: int
    required_entrant_present_after: bool
    next_turn_entry_possible: bool
    objective_survives: bool


def contract(
    label: str,
    occupants: tuple[Occupant, ...],
    *,
    capacity_before: int,
    capacity_after: int,
    required_entrant_name: str = "required entrant",
    entrant_already_present: bool,
) -> ExposureResult:
    if len(occupants) > capacity_before:
        raise ValueError("starting occupancy exceeds capacity")
    outcome = optimal_forced_discard(occupants, capacity_after)
    discarded = tuple(row["name"] for row in outcome["discarded"])
    retained = tuple(row["name"] for row in outcome["retained"])
    entrant_present = entrant_already_present and required_entrant_name in retained
    slack_after = capacity_after - len(retained)
    next_turn_entry_possible = entrant_present or slack_after >= 1
    objective_survives = entrant_present if entrant_already_present else next_turn_entry_possible
    return ExposureResult(
        label=label,
        capacity_before=capacity_before,
        occupancy_before=len(occupants),
        slack_before=capacity_before - len(occupants),
        capacity_after=capacity_after,
        forced_discards=outcome["discard_count"],
        discarded=discarded,
        retained=retained,
        continuation_loss=outcome["affected_player_continuation_loss"],
        slack_after=slack_after,
        required_entrant_present_after=entrant_present,
        next_turn_entry_possible=next_turn_entry_possible,
        objective_survives=objective_survives,
    )


def _row(result: ExposureResult):
    return {
        "label": result.label,
        "capacity_before": result.capacity_before,
        "occupancy_before": result.occupancy_before,
        "slack_before": result.slack_before,
        "capacity_after": result.capacity_after,
        "forced_discards": result.forced_discards,
        "discarded": list(result.discarded),
        "retained": list(result.retained),
        "continuation_loss": result.continuation_loss,
        "slack_after": result.slack_after,
        "required_entrant_present_after": result.required_entrant_present_after,
        "next_turn_entry_possible": result.next_turn_entry_possible,
        "objective_survives": result.objective_survives,
    }


def build_result():
    core = (
        Occupant("core A", 10.0),
        Occupant("core B", 8.0),
        Occupant("core C", 7.0),
        Occupant("core D", 6.0),
    )
    high_entrant = Occupant("required entrant", 9.0)
    low_entrant = Occupant("required entrant", 2.0)

    scenarios = {
        "preload_then_collapsed": contract(
            "attack release preloads one slot; opponent Collapsed Stadium sets cap 4",
            core,
            capacity_before=5,
            capacity_after=4,
            entrant_already_present=False,
        ),
        "immediate_entry_then_collapsed": contract(
            "Item release and immediate high-value entry; opponent Collapsed Stadium sets cap 4",
            core + (high_entrant,),
            capacity_before=5,
            capacity_after=4,
            entrant_already_present=True,
        ),
        "preload_then_parallel": contract(
            "attack release preloads one slot; opponent Parallel City side sets cap 3",
            core,
            capacity_before=5,
            capacity_after=3,
            entrant_already_present=False,
        ),
        "immediate_entry_then_parallel": contract(
            "Item release and immediate high-value entry; opponent Parallel City side sets cap 3",
            core + (high_entrant,),
            capacity_before=5,
            capacity_after=3,
            entrant_already_present=True,
        ),
        "low_value_entry_then_collapsed": contract(
            "immediate low-value entry; opponent Collapsed Stadium sets cap 4",
            core + (low_entrant,),
            capacity_before=5,
            capacity_after=4,
            entrant_already_present=True,
        ),
    }

    assert scenarios["preload_then_collapsed"].forced_discards == 0
    assert scenarios["preload_then_collapsed"].slack_before == 1
    assert scenarios["preload_then_collapsed"].slack_after == 0
    assert not scenarios["preload_then_collapsed"].objective_survives
    assert scenarios["immediate_entry_then_collapsed"].discarded == ("core D",)
    assert scenarios["immediate_entry_then_collapsed"].required_entrant_present_after
    assert scenarios["preload_then_parallel"].discarded == ("core D",)
    assert not scenarios["preload_then_parallel"].objective_survives
    assert scenarios["immediate_entry_then_parallel"].discarded == ("core D", "core C")
    assert scenarios["immediate_entry_then_parallel"].required_entrant_present_after
    assert scenarios["low_value_entry_then_collapsed"].discarded == ("required entrant",)
    assert not scenarios["low_value_entry_then_collapsed"].objective_survives

    return {
        "card_text_anchors": {
            "collapsed_stadium": "Collapsed Stadium swsh9-137/swsh11-215: each player cannot have more than 4 Benched Pokémon and discards down to 4 when necessary.",
            "parallel_city": "Parallel City xy8-145: the chosen side cannot have more than 3 Benched Pokémon and discards down to 3 when it comes into play.",
        },
        "scenarios": {name: _row(result) for name, result in scenarios.items()},
        "findings": {
            "silent_slack_destruction": "capacity can fall to current occupancy, erase reserved slack, and force zero discards while still blocking a planned future Bench entry",
            "early_materialization_tradeoff": "placing the required entrant before the opponent window can preserve the objective under contraction if the affected player's discard policy prefers sacrificing another occupant",
            "entrant_value_dependency": "early materialization is not absolute protection; a low-value entrant can itself be the optimal forced discard",
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
    parser.add_argument("--output", type=Path, default=Path("results/interturn_bench_slack_exposure/model.json"))
    args = parser.parse_args()
    result = build_result()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
