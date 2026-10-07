from __future__ import annotations

from typing import Any


def full_board_refresh(
    capacity_before: int,
    restriction_cap: int,
    release_cap: int,
    core_occupancy: int,
) -> dict[str, Any]:
    """Model a full board constricted to restriction_cap, then released.

    Every non-core occupant is treated as stale and freely discardable.
    The result reports whether the core can survive intact.
    """
    if min(capacity_before, restriction_cap, release_cap, core_occupancy) < 0:
        raise ValueError("capacities and occupancy must be non-negative")
    if core_occupancy > capacity_before:
        raise ValueError("core occupancy cannot exceed the starting capacity")

    start_occupancy = capacity_before
    forced_discards = max(0, start_occupancy - restriction_cap)
    stale_occupants = start_occupancy - core_occupancy
    stale_removed = min(stale_occupants, forced_discards)
    core_removed = forced_discards - stale_removed
    restricted_occupancy = start_occupancy - forced_discards
    final_slack = max(0, release_cap - restricted_occupancy)

    return {
        "capacity_before": capacity_before,
        "restriction_cap": restriction_cap,
        "release_cap": release_cap,
        "core_occupancy": core_occupancy,
        "start_occupancy": start_occupancy,
        "stale_occupants": stale_occupants,
        "forced_discards": forced_discards,
        "stale_removed": stale_removed,
        "core_removed": core_removed,
        "core_preserved": core_removed == 0,
        "restricted_occupancy": restricted_occupancy,
        "final_slack": final_slack,
    }


def one_refresh_transaction_capacity(
    capacity_before: int,
    restriction_cap: int,
    release_cap: int,
    core_occupancy: int,
) -> dict[str, Any]:
    """Maximum one-turn transactional entries under one lossless bulk refresh.

    The board starts with only the persistent core. Transactional supports are
    played until the Bench is full, then the restriction is applied and later
    removed. If the restriction can preserve the core, the reopened slots are
    filled with more transactional supports.
    """
    if core_occupancy > capacity_before:
        raise ValueError("core occupancy cannot exceed starting capacity")

    initial_entries = capacity_before - core_occupancy
    refresh = full_board_refresh(
        capacity_before,
        restriction_cap,
        release_cap,
        core_occupancy,
    )
    additional_entries = refresh["final_slack"] if refresh["core_preserved"] else 0
    return {
        **refresh,
        "initial_transactional_entries": initial_entries,
        "additional_entries_after_refresh": additional_entries,
        "total_transactional_entries": initial_entries + additional_entries,
    }


def threshold_table() -> list[dict[str, Any]]:
    rows = []
    for capacity_before, label in ((5, "normal"), (8, "eight_slot")):
        for restriction_cap, restriction in ((4, "Collapsed Stadium"), (3, "Parallel City")):
            for core in range(capacity_before + 1):
                row = one_refresh_transaction_capacity(
                    capacity_before,
                    restriction_cap,
                    5,
                    core,
                )
                rows.append(
                    {
                        "starting_mode": label,
                        "restriction": restriction,
                        **row,
                    }
                )
    return rows


if __name__ == "__main__":
    for row in threshold_table():
        if row["core_preserved"]:
            print(row)
