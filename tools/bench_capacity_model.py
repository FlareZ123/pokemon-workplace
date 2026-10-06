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
        stale_absorption.append(
            {
                "occupancy_before": occupancy,
                "capacity_after": new_capacity,
                "forced_discards": max(0, occupancy - new_capacity),
                "minimum_stale_occupants_for_zero_live_loss": max(0, occupancy - new_capacity),
            }
        )

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
