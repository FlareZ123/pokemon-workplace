"""Penny Supporter pickup under going-first Supporter restriction.

One targeted Basic support requires one hand-to-Bench activation. Penny
returns one Basic and all attached cards to hand. The first player may
not play ordinary Supporters on their first turn; Penny can still
serve as Quick Ball's discarded other card on that turn.

For this restricted single-target model, a playable Penny is equivalent
to one certain pickup, because no successful line needs to play more
than one pickup Supporter. Unplayable Penny is discard stock.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_trigger_paid_replay import analyze_paid_replay


def analyze_penny_package(penny: int) -> tuple[Fraction, Fraction]:
    """One support A, O3, Quick Ball4, Nest Ball4, four pickup slots."""
    if not 0 <= penny <= 4:
        raise ValueError("Penny copies must be 0..4")
    super_scoop = 4 - penny
    # First player on their first turn cannot play Penny, but can
    # discard a Penny to pay for a Quick Ball search.
    first = analyze_paid_replay(
        other_basics=3, quick_balls=4, nest_balls=4,
        coin_pickups=super_scoop,
        sure_pickups=0, expendable=penny,
    )
    # Second player may use one Penny as guaranteed pickup if the
    # Supporter action remains unused and no locking effect applies.
    second = analyze_paid_replay(
        other_basics=3, quick_balls=4, nest_balls=4,
        coin_pickups=super_scoop,
        sure_pickups=penny, expendable=0,
    )
    return first, second


def main() -> None:
    previous_first: Fraction | None = None
    previous_second: Fraction | None = None
    for penny in range(5):
        first, second = analyze_penny_package(penny)
        assert first <= second
        if previous_first is not None:
            assert first < previous_first
            assert second > previous_second
        print("Penny", penny, "Super Scoop Up", 4-penny,
              "going first", f"{100*float(first):.6f}%",
              "going second", f"{100*float(second):.6f}%",
              "Supporter availability gap", f"{100*float(second-first):.6f}pp")
        previous_first = first
        previous_second = second

    same_first, same_second = analyze_penny_package(0)
    assert same_first == same_second
    all_first, all_second = analyze_penny_package(4)
    assert all_second > same_second > all_first
    print("PASS: exact Penny package turn-order access differential")


if __name__ == "__main__":
    main()
