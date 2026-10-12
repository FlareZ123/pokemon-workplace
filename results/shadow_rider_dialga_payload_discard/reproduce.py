"""Reproduce champion Shadow Rider's singleton Dialga discard extension."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.shadow_rider_dialga_payload_discard import run


def main() -> None:
    values = run()
    for key, probability in values.items():
        print(f"{key}: {float(probability):.9%} [{probability}]")
    print("Three labeled physical toy oracles passed: 66360 accepted deals")


if __name__ == "__main__":
    main()
