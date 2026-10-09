"""Fixed-seed 80k accepted-opening baseline for extra Tag Call preview."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_tagcall_information_preview import output, simulate

if __name__ == "__main__":
    print(output(simulate(raw_trials=80_000, seed=20261009)))
