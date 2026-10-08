"""Reproducible paired-Aichi option to defer redundant early Jirachi."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_jirachi_ticket_search import output, simulate

if __name__ == "__main__":
    print(output(simulate(raw_trials=300_000, seed=20261008,
                          defer_redundant_stellar=True)))
