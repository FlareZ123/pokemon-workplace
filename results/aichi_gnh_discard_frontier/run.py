"""Fixed-seed first-turn Aichi G&H payment-frontier experiment."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_gnh_discard_frontier import output, simulate

if __name__ == "__main__":
    print(output(simulate(raw_trials=200_000, seed=20261008)))
