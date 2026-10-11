"""Reproduce Arc Phone / Peonia shoes-free exact results."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from arc_peonia_shoes_free import check
if __name__ == "__main__":
    check()
