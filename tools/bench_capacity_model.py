from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_BENCH_CAPACITY = 5


@dataclass(frozen=True)
class Occupant:
    name: str
    continuation_value: float


def effective_capacity(
    extension_caps: tuple[int, ...] = (), restriction_caps: tuple[int, ...] = ()
) -> int:
    capacity = max((DEFAULT_BENCH_CAPACITY, *extension_caps))
    if restriction_caps:
        capacity = min(capacity, *restriction_caps)
    return capacity


def route_trace(start_occupancy: int, capacity: int, deltas: tuple[int, ...]) -> dict[str, Any]:
    occupancy = start_occupancy
    peak = occupancy
    trace = [occupancy]
    first_overflow_step = None
    for step, delta in enumerate(deltas, start=1):
        occupancy += delta
        trace.append(occupancy)
        peak = max(peak, occupancy)
        if first_overflow_step is None and occupancy > capacity:
            first_overflow_step = step
    return {
        "capacity": capacity,
        "start_occupancy": start_occupancy,
        "deltas": list(deltas),
        "trace": trace,
        "peak_occupancy": peak,
        "peak_increment": peak - start_occupancy,
        "final_occupancy": occupancy,
        "feasible": first_overflow_step is None,
        "first_overflow_step": first_overflow_step,
    }


def entry_then_capacity_drop(
    start_occupancy: int, capacity_before: int, capacity_after: int
) -> dict[str, Any]:
    if start_occupancy >= capacity_before:
        return {
            "start_occupancy": start_occupancy,
            "capacity_before": capacity_before,
            "capacity_after": capacity_after,
            "entry_legal": False,
            "reason": "no Bench slack for the entry action",
        }

    occupancy_after_entry = start_occupancy + 1
    forced_discards = max(0, occupancy_after_entry - capacity_after)
    transient_entry_can_be_discarded = forced_discards > 0
    preexisting_discards_if_entry_is_chosen = max(
        0, forced_discards - int(transient_entry_can_be_discarded)
    )
    return {
        "start_occupancy": start_occupancy,
        "capacity_before": capacity_before,
        "capacity_after": capacity_after,
        "entry_legal": True,
        "occupancy_after_entry": occupancy_after_entry,
        "peak_occupancy": occupancy_after_entry,
        "forced_discards": forced_discards,
        "transient_entry_can_be_discarded": transient_entry_can_be_discarded,
        "preexisting_discards_if_entry_is_chosen": preexisting_discards_if_entry_is_chosen,
        "final_occupancy": min(occupancy_after_entry, capacity_after),
    }


def contraction_impact(occupancy: int, new_capacity: int, stale_occupants: int) -> dict[str, int]:
    forced_discards = max(0, occupancy - new_capacity)
    stale_available = min(max(0, stale_occupants), occupancy)
    stale_removed = min(forced_discards, stale_available)
    live_removed = forced_discards - stale_removed
    return {
        "occupancy_before": occupancy,
        "capacity_after": new_capacity,
        "forced_discards": forced_discards,
        "stale_occupants_before": stale_available,
        "stale_removed": stale_removed,
        "live_removed_after_stale_buffer": live_removed,
    }


def contraction_path(occupancy: int, capacities: tuple[int, ...]) -> dict[str, Any]:
    current = occupancy
    total_discards = 0
    steps = []
    for capacity in capacities:
        discarded = max(0, current - capacity)
        current -= discarded
        total_discards += discarded
        steps.append(
            {
                "capacity": capacity,
                "discarded": discarded,
                "occupancy_after": current,
            }
        )
    return {
        "occupancy_before": occupancy,
        "capacity_path": list(capacities),
        "steps": steps,
        "total_discards": total_discards,
        "occupancy_after": current,
    }


def optimal_forced_discard(occupants: tuple[Occupant, ...], new_capacity: int) -> dict[str, Any]:
    discard_count = max(0, len(occupants) - new_capacity)
    ordered = sorted(occupants, key=lambda occupant: (occupant.continuation_value, occupant.name))
    discarded = ordered[:discard_count]
    retained = ordered[discard_count:]
    loss = sum(occupant.continuation_value for occupant in discarded)
    return {
        "old_occupancy": len(occupants),
        "new_capacity": new_capacity,
        "discard_count": discard_count,
        "affected_player_continuation_loss": loss,
        "discarded": [
            {"name": occupant.name, "continuation_value": occupant.continuation_value}
            for occupant in discarded
        ],
        "retained": [
            {"name": occupant.name, "continuation_value": occupant.continuation_value}
            for occupant in retained
        ],
    }


def build_examples() -> dict[str, Any]:
    capacity_examples = {
        "default": effective_capacity(),
        "sky_field": effective_capacity(extension_caps=(8,)),
        "sky_field_plus_sudowoodo": effective_capacity(
            extension_caps=(8,), restriction_caps=(4,)
        ),
        "area_zero_plus_collapsed_stadium": effective_capacity(
            extension_caps=(8,), restriction_caps=(4,)
        ),
        "sky_field_plus_parallel_city": effective_capacity(
            extension_caps=(8,), restriction_caps=(3,)
        ),
    }

    route_examples = {
        "two_entries_then_one_cleanup_default": route_trace(4, 5, (1, 1, -1)),
        "two_entries_then_one_cleanup_sky_field": route_trace(4, 8, (1, 1, -1)),
        "single_entry_under_collapsed": route_trace(4, 4, (1,)),
        "entry_then_same_turn_cleanup_with_one_slack": route_trace(4, 5, (1, -1)),
    }

    board = (
        Occupant("spent two-Prize search support", -2.0),
        Occupant("spent one-shot utility", 0.0),
        Occupant("pivot", 3.0),
        Occupant("secondary attacker", 6.0),
        Occupant("primary setup piece", 10.0),
    )
    contraction_examples = {
        "collapsed_to_four": optimal_forced_discard(board, 4),
        "parallel_or_dust_field_to_three": optimal_forced_discard(board, 3),
    }

    stale_absorption = []
    for occupancy, new_capacity in ((5, 4), (5, 3), (8, 5), (8, 4), (8, 3)):
        forced_discards = max(0, occupancy - new_capacity)
        stale_absorption.append(
            {
                "occupancy_before": occupancy,
                "capacity_after": new_capacity,
                "forced_discards": forced_discards,
                "minimum_stale_occupants_for_zero_live_loss": forced_discards,
            }
        )

    stale_buffer_examples = {
        "roadblock_from_five_with_one_stale": contraction_impact(5, 4, 1),
        "dust_field_from_five_with_two_stale": contraction_impact(5, 3, 2),
        "parallel_from_eight_with_three_stale": contraction_impact(8, 3, 3),
    }

    expansion_replacement_examples = {
        "sky_field_leaves_then_parallel": contraction_path(8, (5, 3)),
        "sky_field_leaves_then_collapsed": contraction_path(8, (5, 4)),
        "area_zero_leaves_then_parallel": contraction_path(8, (5, 3)),
    }

    entry_removal_examples = {
        "remover_from_four_under_sky_field": entry_then_capacity_drop(4, 8, 5),
        "remover_from_five_under_sky_field": entry_then_capacity_drop(5, 8, 5),
        "remover_from_seven_under_sky_field": entry_then_capacity_drop(7, 8, 5),
        "remover_from_full_eight_slot_bench": entry_then_capacity_drop(8, 8, 5),
    }

    return {
        "definitions": {
            "default_bench_capacity": DEFAULT_BENCH_CAPACITY,
            "bench_slack": "capacity minus current Bench occupancy",
            "route_peak_requirement": "maximum temporary Bench occupancy reached by a line, not its final occupancy",
            "continuation_value": "state-relative value to the affected player of keeping a Bench occupant in play; negative values represent liabilities whose removal is beneficial",
        },
        "capacity_examples": capacity_examples,
        "route_examples": route_examples,
        "contraction_examples": contraction_examples,
        "stale_absorption": stale_absorption,
        "stale_buffer_examples": stale_buffer_examples,
        "expansion_replacement_examples": expansion_replacement_examples,
        "entry_removal_examples": entry_removal_examples,
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as tmp_file:
                json.dump(payload, tmp_file, indent=2, ensure_ascii=False)
                tmp_file.write("\n")
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Model Bench capacity, route peak occupancy, and forced contraction.")
    parser.add_argument(
        "--output", type=Path, default=Path("results/bench_capacity_geometry/model_examples.json")
    )
    args = parser.parse_args()
    result = build_examples()
    atomic_write_json(args.output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
