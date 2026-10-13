"""Restricted 230-damage Mew VMAX line versus active Iron Thorns ex.

Exact first-seven/first natural draw/six Prize access with an already-active
Initialization Ability lock. A naturally held Muscle Band is compulsory.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.tests.mew_wally_iron_thorns_230.reproduce import (
    exact, oracle, verify_source_cards,
)

EXPECTED = {
    1: Fraction(412371942273, 175386308570200),
    2: Fraction(39482777184791, 8681622274224900),
    3: Fraction(114543736325093, 17363244548449800),
}


def pool(wally: int) -> tuple[int, ...]:
    # Mew, Genesect, Mew VMAX, Wally, DCE, VIP, Quick, Ultra, Muscle Band, other.
    # Tapu Lele belongs to "other" because active Iron Thorns suppresses Wonder Tag.
    result = (4, 4, 3, wally, 4, 3, 4, 4, 2, 32 - wally)
    assert sum(result) == 60
    return result


def main() -> None:
    verify_source_cards()
    # Independent labeled physical deal oracle exercises multiple Wally counts.
    for fixture, hand, prizes in (
        ((1, 1, 1, 2, 1, 0, 1, 1, 1, 3), 3, 2),
        ((2, 1, 1, 3, 1, 0, 1, 1, 1, 2), 4, 2),
    ):
        assert exact(fixture, hand, prizes) == oracle(fixture, hand, prizes)
        print(f"Repeated-Wally physical-deal oracle PASS N={sum(fixture)}")
    for wally, fraction in EXPECTED.items():
        observed = sum(exact(pool(wally), 7, 6), Fraction(0))
        assert observed == fraction, (wally, observed, fraction)
        print(
            f"Wally={wally}: first-turn 230-damage access "
            f"{float(observed):.12%}; exact={fraction}"
        )
    assert EXPECTED[2] > EXPECTED[1]
    assert EXPECTED[3] > EXPECTED[2]
    print("Increasing Wally count improves this restricted ability-locked 230-damage endpoint")


if __name__ == "__main__":
    main()
