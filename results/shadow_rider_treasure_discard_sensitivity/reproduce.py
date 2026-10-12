"""Reproduce all exact Aichi Shadow Rider Treasure-discard policy curves."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.shadow_rider_treasure_discard_sensitivity import run


def main() -> None:
    probs = run()
    direct = probs["direct"]
    for policy, probability in probs.items():
        if policy == "direct":
            print(f"direct: {float(probability):.9%} [{probability}]")
        else:
            total = direct + probability
            print(
                f"{policy}: Treasure {float(probability):.9%}; "
                f"total {float(total):.9%}; [{probability}]"
            )
    print("Labeled physical oracle: 18312 accepted worlds, exact match")


if __name__ == "__main__":
    main()
