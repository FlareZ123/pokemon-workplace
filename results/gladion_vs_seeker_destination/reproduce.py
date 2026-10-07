"""Reproduce Gladion destination error under VS Seeker recovery."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from gladion_vs_seeker_destination import (  # noqa: E402
    _literal_success,
    _naive_discard_success,
    compare_gladion_destination,
)


def pct(x: float) -> str:
    return f"{100*x:.6f}%"


def main() -> None:
    _literal_success.cache_clear()
    _naive_discard_success.cache_clear()
    assert _literal_success(2, 2, 1, 0, 1, 0, 0, 2) == 0.0
    assert _naive_discard_success(2, 2, 1, 0, 1, 0, 0, 2) == 1.0

    table = {}
    for seekers in range(5):
        table[seekers] = []
        for turns in range(1, 5):
            r = compare_gladion_destination(
                60,
                6,
                starter_cards=12,
                critical_starter=0,
                critical_nonstarter=4,
                gladion_copies=1,
                vs_seeker_copies=seekers,
                rescue_turns=turns,
            )
            assert isclose(r.state_mass, 1.0, rel_tol=0.0, abs_tol=1e-12)
            assert r.naive_discard_conditional_success + 1e-15 >= r.literal_conditional_success
            table[seekers].append(
                (r.literal_conditional_success, r.naive_discard_conditional_success)
            )

    for literal, naive in table[0]:
        assert isclose(literal, naive, rel_tol=0.0, abs_tol=1e-12)

    literal_reference = table[0]
    for seekers in range(1, 5):
        for (base_literal, _), (literal, _) in zip(literal_reference, table[seekers]):
            assert isclose(base_literal, literal, rel_tol=0.0, abs_tol=1e-12)

    print("gladion_vs_seeker_destination: all assertions passed")
    for seekers, row in table.items():
        print("VS", seekers)
        for turn, (literal, naive) in enumerate(row, 1):
            print(turn, pct(literal), pct(naive), f"gap={100*(naive-literal):.6f}pp")


if __name__ == "__main__":
    main()
