from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from bench_refresh_lines import refresh_line


def main() -> None:
    parallel = refresh_line(5, (3,), 5, stale_occupants=2)
    assert parallel["total_forced_discards"] == 2
    assert parallel["stale_removed"] == 2
    assert parallel["live_removed_after_stale_buffer"] == 0
    assert parallel["final_occupancy"] == 3
    assert parallel["final_slack"] == 2

    collapsed = refresh_line(5, (4,), 5, stale_occupants=1)
    assert collapsed["total_forced_discards"] == 1
    assert collapsed["final_slack"] == 1

    sky_parallel = refresh_line(8, (5, 3), 5, stale_occupants=3)
    assert sky_parallel["total_forced_discards"] == 5
    assert sky_parallel["stale_removed"] == 3
    assert sky_parallel["live_removed_after_stale_buffer"] == 2
    assert sky_parallel["final_slack"] == 2

    print("bench_refresh_lines: all checks passed")


if __name__ == "__main__":
    main()
