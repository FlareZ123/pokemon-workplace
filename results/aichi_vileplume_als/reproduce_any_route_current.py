"""Re-run the current broader Aichi Vileplume first-turn core planner."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_vileplume_als import simulate_any_route


def main() -> None:
    result = simulate_any_route(100_000, seed=20261007)
    core = result.probability("core")
    print(f"core={core:.9%}")
    print(f"mean_mulligans={result.mean_mulligans:.9f}")


if __name__ == "__main__":
    main()
