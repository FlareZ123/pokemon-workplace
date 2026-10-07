from __future__ import annotations

from typing import Any


def refresh_line(
    start_occupancy: int,
    contraction_caps: tuple[int, ...],
    release_cap: int,
    *,
    stale_occupants: int = 0,
) -> dict[str, Any]:
    """Apply forced capacity contractions, then release to a larger capacity."""
    current = start_occupancy
    total_discards = 0
    steps = []
    for cap in contraction_caps:
        discarded = max(0, current - cap)
        current -= discarded
        total_discards += discarded
        steps.append(
            {
                "kind": "contract",
                "capacity": cap,
                "discarded": discarded,
                "occupancy_after": current,
            }
        )

    stale_removed = min(max(0, stale_occupants), total_discards)
    live_removed = total_discards - stale_removed
    final_slack = max(0, release_cap - current)
    steps.append(
        {
            "kind": "release",
            "capacity": release_cap,
            "occupancy_after": current,
            "slack_after": final_slack,
        }
    )
    return {
        "start_occupancy": start_occupancy,
        "contraction_caps": list(contraction_caps),
        "release_cap": release_cap,
        "total_forced_discards": total_discards,
        "stale_removed": stale_removed,
        "live_removed_after_stale_buffer": live_removed,
        "final_occupancy": current,
        "final_slack": final_slack,
        "steps": steps,
    }


def standard_refresh_examples() -> dict[str, dict[str, Any]]:
    return {
        "normal_parallel_then_remove": refresh_line(5, (3,), 5, stale_occupants=2),
        "normal_collapsed_then_remove": refresh_line(5, (4,), 5, stale_occupants=1),
        "sky_field_parallel_then_remove": refresh_line(8, (5, 3), 5, stale_occupants=5),
        "sky_field_collapsed_then_remove": refresh_line(8, (5, 4), 5, stale_occupants=4),
    }


if __name__ == "__main__":
    for name, row in standard_refresh_examples().items():
        print(name, row)
