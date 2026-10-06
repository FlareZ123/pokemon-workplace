from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from setup_bench_policy import (
    accepted_basic_count_distribution,
    connector_block_probability,
    setup_bench_occupancy,
)


def main() -> None:
    distribution = accepted_basic_count_distribution(60, 12)
    assert abs(sum(distribution.values()) - 1.0) < 1e-12
    assert setup_bench_occupancy(7) == 5
    assert setup_bench_occupancy(7, reserve_slots=1) == 4

    one_slot = connector_block_probability(60, 12, 1)
    two_slots = connector_block_probability(60, 12, 2)
    assert abs(one_slot - 0.00014442482181270888) < 1e-15
    assert abs(two_slots - 0.0030025160324221056) < 1e-15
    assert connector_block_probability(60, 12, 1, reserve_slots=1) == 0.0
    assert connector_block_probability(60, 32, 2, reserve_slots=2) == 0.0

    print("setup_bench_policy: all checks passed")
    print("12 Basics, one-slot block if bench-all:", one_slot)
    print("12 Basics, two-slot block if bench-all:", two_slots)


if __name__ == "__main__":
    main()
