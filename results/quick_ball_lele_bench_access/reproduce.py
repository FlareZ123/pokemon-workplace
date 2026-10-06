from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from quick_ball_lele_bench_access import opening_gladion_access_with_bench_policy


def main() -> None:
    kwargs = dict(
        deck_size=60,
        prize_count=6,
        other_starters=11,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        quick_ball_copies=4,
        disposable_nonstarter=12,
    )
    bench_all = opening_gladion_access_with_bench_policy(
        **kwargs, setup_reserve_slots=0
    )
    reserve_one = opening_gladion_access_with_bench_policy(
        **kwargs, setup_reserve_slots=1
    )
    assert abs(bench_all - 0.48569162518069064) < 1e-15
    assert abs(reserve_one - 0.4856932449660702) < 1e-15
    assert abs(reserve_one - bench_all - 0.0000016197853795474337) < 1e-15

    high_basic = dict(kwargs, other_starters=27)
    high_bench_all = opening_gladion_access_with_bench_policy(
        **high_basic, setup_reserve_slots=0
    )
    high_reserve = opening_gladion_access_with_bench_policy(
        **high_basic, setup_reserve_slots=1
    )
    assert abs(high_reserve - high_bench_all - 0.0008523055010876135) < 1e-15

    print("quick_ball_lele_bench_access: all checks passed")
    print("12 starters recovery from reserving one slot:", reserve_one - bench_all)
    print("28 starters recovery from reserving one slot:", high_reserve - high_bench_all)


if __name__ == "__main__":
    main()
