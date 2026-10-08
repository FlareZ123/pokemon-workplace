"""Fixed-seed Tag Call G&H payment-resource sensitivity experiment."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_tagcall_payment_reachability import output, simulate

if __name__ == "__main__":
    print(output(simulate(raw_trials=100_000, seed=20261008)))
