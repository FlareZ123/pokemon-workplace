"""Re-run the current broader Aichi Vileplume first-turn core planner."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS, simulate_any_route


def main() -> None:
    result = simulate_any_route(100_000, seed=20261007)
    core = result.probability("core")
    if not isclose(core, 0.70709, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"current core={core!r}, expected 0.70709")

    for endpoint in ANY_ROUTE_ENDPOINTS:
        print(f"{endpoint}={result.probability(endpoint):.9%}")
    print(f"mean_mulligans={result.mean_mulligans:.9f}")


if __name__ == "__main__":
    main()
