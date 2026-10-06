from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from setup_entry_payload_capacity import full_payload_probability, payload_outcome_distribution


def main() -> None:
    twelve = payload_outcome_distribution(60, 11)
    assert abs(sum(twelve.values()) - 1.0) < 1e-12
    assert abs(twelve["payload_2"] - 0.987955881849677) < 1e-15
    assert abs(twelve["payload_1"] - 0.011353639707140513) < 1e-15
    assert abs(twelve["payload_0"] - 0.0006763870463828391) < 1e-15
    assert abs(twelve["cannot_play_trigger"] - 0.000014091396799642481) < 1e-15
    assert full_payload_probability(60, 11, reserve_slots=3) == 1.0

    thirty_two = payload_outcome_distribution(60, 31)
    assert thirty_two["payload_2"] < 0.62
    assert full_payload_probability(60, 31, reserve_slots=3) == 1.0

    print("setup_entry_payload_capacity: all checks passed")
    print("12 total Basics:", twelve)
    print("32 total Basics:", thirty_two)


if __name__ == "__main__":
    main()
