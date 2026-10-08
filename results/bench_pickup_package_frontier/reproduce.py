"""Exact fixed-eight-slot pickup/search package frontier for one support."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_trigger_paid_replay import analyze_paid_replay


def main() -> None:
    # Eight flexible slots hold 0..4 Nest Ball, 0..4 Super Scoop Up,
    # 0..1 ACE SPEC Scoop Up Cyclone and remaining disposable filler.
    # Four Quick Balls, three other ordinary Basics and singleton A fixed.
    evaluated: list[tuple[Fraction, int, int, int, int]] = []
    for ace in range(2):
        for nests in range(5):
            for coin in range(5):
                filler = 8 - nests - coin - ace
                if filler < 0:
                    continue
                score = analyze_paid_replay(
                    other_basics=3, quick_balls=4,
                    nest_balls=nests, coin_pickups=coin,
                    sure_pickups=ace, expendable=filler,
                )
                evaluated.append((score, nests, coin, ace, filler))

    assert len(evaluated) == 49
    ranked = sorted(evaluated, reverse=True)
    no_ace = max(record for record in evaluated if record[3] == 0)
    with_ace = max(record for record in evaluated if record[3] == 1)
    assert no_ace[1:] == (4, 4, 0, 0)
    assert with_ace[1:] == (4, 3, 1, 0)
    assert with_ace > no_ace
    print("Total fixed-slot packages checked:", len(evaluated))
    for score, nests, coin, ace, filler in ranked[:12]:
        print(f"{100*float(score):.6f}%",
              f"Nest={nests}", f"SuperScoop={coin}",
              f"Cyclone={ace}", f"discardable={filler}")

    # Cyclone replaces one of four Super Scoop Up copies in same slot budget.
    improvement = with_ace[0] - no_ace[0]
    assert improvement > 0
    print("Best non-ACE package:", f"{100*float(no_ace[0]):.6f}%")
    print("Best package including Cyclone:", f"{100*float(with_ace[0]):.6f}%")
    print("Cyclone-slot uplift:", f"{100*float(improvement):.6f}pp")
    print("PASS: exact 49-configuration restricted access frontier")


if __name__ == "__main__":
    main()
