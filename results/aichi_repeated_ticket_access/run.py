"""Reproducible larger paired Aichi repeated-Ticket simulation (fixed seed)."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_repeated_ticket_access import output, simulate

if __name__ == "__main__":
    print(output(simulate(raw_trials=400_000, seed=20261008)))
