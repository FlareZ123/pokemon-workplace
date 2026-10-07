from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_capacity_restoration_bootstrap import build_result


def main() -> None:
    r = build_result()
    p = r["plans"]
    assert p["pumpkaboo_from_full_four"] is None
    assert p["pumpkaboo_with_one_slack"] == (
        "Bench Pumpkin Pit remover and discard Stadium",
        "Bench ordinary entrant",
    )
    assert p["sky_field_from_full_four"] is not None
    assert p["area_zero_two_entry_plan"] is not None
    order = r["area_zero_forced_order"]
    assert order["tera_first"]["second_legal"]
    assert order["tera_first"]["capacity_after_first"] == 8
    assert not order["ordinary_first"]["second_legal"]
    assert order["ordinary_first"]["capacity_after_first"] == 5
    print("bench_capacity_restoration_bootstrap regression passed")


if __name__ == "__main__":
    main()
