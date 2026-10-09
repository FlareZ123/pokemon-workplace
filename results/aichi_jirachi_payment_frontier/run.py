"""Fixed-seed 80,000-opening Aichi payment and Jirachi Item access study."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_jirachi_payment_frontier import output, simulate

if __name__ == "__main__":
    print(output(simulate(raw_trials=80_000, seed=20261009)))
