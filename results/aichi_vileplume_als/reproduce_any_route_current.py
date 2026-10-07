"""Re-run the current Aichi Vileplume named and broader first-turn planners."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_vileplume_als import simulate, simulate_any_route


ENDPOINT_PAIRS = (
    ("double_tm", "core"),
    ("pidgeot_stage2", "pidgeot"),
    ("stoutland_stage2", "stoutland"),
    ("dual_stage2", "dual"),
    ("item_lock", "item"),
    ("item_plus_pidgeot", "item_pidgeot"),
    ("item_plus_stoutland", "item_stoutland"),
)


def main() -> None:
    named = simulate(100_000, seed=20261007)
    broader = simulate_any_route(100_000, seed=20261007)

    core = broader.probability("core")
    if not isclose(core, 0.70709, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"current core={core!r}, expected 0.70709")

    for named_key, broader_key in ENDPOINT_PAIRS:
        left = named.probability(named_key)
        right = broader.probability(broader_key)
        print(
            f"{broader_key}: named={left:.9%} "
            f"broader={right:.9%} delta={right-left:.9%}"
        )
    print(f"mean_mulligans={broader.mean_mulligans:.9f}")


if __name__ == "__main__":
    main()
