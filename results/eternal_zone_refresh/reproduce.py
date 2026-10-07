from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from bench_bulk_refresh import full_board_refresh, one_refresh_transaction_capacity


def main() -> None:
    core5 = full_board_refresh(8, 5, 8, 5)
    assert core5["forced_discards"] == 3
    assert core5["stale_occupants"] == 3
    assert core5["core_preserved"] is True
    assert core5["final_slack"] == 3

    core6 = full_board_refresh(8, 5, 8, 6)
    assert core6["forced_discards"] == 3
    assert core6["stale_occupants"] == 2
    assert core6["core_preserved"] is False
    assert core6["core_removed"] == 1
    assert core6["final_slack"] == 3

    throughput = one_refresh_transaction_capacity(8, 5, 8, 5)
    assert throughput["initial_transactional_entries"] == 3
    assert throughput["additional_entries_after_refresh"] == 3
    assert throughput["total_transactional_entries"] == 6

    print("eternal_zone_refresh: all checks passed")


if __name__ == "__main__":
    main()
