"""Compare idealized clean outs with Quick Ball -> Tapu Lele-GX access."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from direct_rescue_outs import first_rescue_access_probability  # noqa: E402
from quick_ball_lele_access import opening_gladion_access_probability  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def main() -> None:
    clean = first_rescue_access_probability(
        60,
        6,
        starter_cards=12,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        direct_out_nonstarter=4,
        cards_seen=7,
        opening_hand_size=7,
    )

    base = dict(
        deck_size=60,
        prize_count=6,
        other_starters=11,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        quick_ball_copies=4,
        opening_hand_size=7,
    )

    print(f"Four idealized clean non-starter outs: {pct(clean)}")
    print("disposable | Quick Ball/Lele access | difference versus 4 clean outs")
    crossing = None
    for disposable in range(0, 25):
        actual = opening_gladion_access_probability(
            **base,
            disposable_nonstarter=disposable,
        )
        if crossing is None and actual >= clean:
            crossing = disposable
        if disposable in {0, 2, 4, 8, 12, 16, 20, 24}:
            print(
                f"{disposable:10d} | {pct(actual):>22} | "
                f"{100 * (actual - clean):+.6f} pp"
            )

    if crossing != 20:
        raise AssertionError(crossing)
    print(f"\nFirst integer disposable-pool size meeting clean-out baseline: {crossing}")


if __name__ == "__main__":
    main()
