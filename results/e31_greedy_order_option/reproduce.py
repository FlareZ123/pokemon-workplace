"""Re-run the exact Prize-chain ordering and positional-information tests."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from e31_greedy_order_option import exact_regressions


if __name__ == "__main__":
    exact_regressions()
