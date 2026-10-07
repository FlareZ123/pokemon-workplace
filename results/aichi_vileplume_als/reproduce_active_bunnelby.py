from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_vileplume_als import TrialState, evaluate_state  # noqa: E402


def main() -> None:
    state = TrialState(
        hand=Counter(
            {
                "Technical Machine: Evolution": 1,
                "Jet Energy": 1,
            }
        ),
        deck=Counter(
            {
                "Artazon": 1,
                "Oddish": 1,
                "Gloom": 1,
                "Vileplume": 1,
            }
        ),
        active="Bunnelby",
        mulligans=0,
        stellar_hit=False,
        gnh_access=True,
    )

    result = evaluate_state(
        state,
        use_fan=False,
        use_artazon=True,
        greedy_fan=False,
    )

    if not result["double_tm"]:
        raise AssertionError(
            "An Active Bunnelby with Jet Energy must satisfy the Bunnelby core "
            "without requiring a second Bunnelby."
        )
    if not result["item_lock"]:
        raise AssertionError(
            "Artazon must remain available to fetch Oddish when the Active "
            "Bunnelby already satisfies the Bunnelby requirement."
        )

    print("Active Bunnelby regression passed.")
    print("double_tm:", result["double_tm"])
    print("item_lock:", result["item_lock"])


if __name__ == "__main__":
    main()
