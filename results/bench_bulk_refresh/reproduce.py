from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from bench_bulk_refresh import full_board_refresh, one_refresh_transaction_capacity


def main() -> None:
    parallel_core3 = full_board_refresh(5, 3, 5, 3)
    assert parallel_core3["core_preserved"] is True
    assert parallel_core3["forced_discards"] == 2
    assert parallel_core3["final_slack"] == 2

    parallel_core4 = full_board_refresh(5, 3, 5, 4)
    assert parallel_core4["core_preserved"] is False
    assert parallel_core4["core_removed"] == 1

    collapsed_core4 = full_board_refresh(5, 4, 5, 4)
    assert collapsed_core4["core_preserved"] is True
    assert collapsed_core4["forced_discards"] == 1
    assert collapsed_core4["final_slack"] == 1

    normal_parallel = one_refresh_transaction_capacity(5, 3, 5, 3)
    assert normal_parallel["initial_transactional_entries"] == 2
    assert normal_parallel["additional_entries_after_refresh"] == 2
    assert normal_parallel["total_transactional_entries"] == 4

    sky_parallel = one_refresh_transaction_capacity(8, 3, 5, 3)
    assert sky_parallel["initial_transactional_entries"] == 5
    assert sky_parallel["forced_discards"] == 5
    assert sky_parallel["total_transactional_entries"] == 7

    sky_collapsed = one_refresh_transaction_capacity(8, 4, 5, 4)
    assert sky_collapsed["core_preserved"] is True
    assert sky_collapsed["initial_transactional_entries"] == 4
    assert sky_collapsed["total_transactional_entries"] == 5

    print("bench_bulk_refresh: all checks passed")


if __name__ == "__main__":
    main()
