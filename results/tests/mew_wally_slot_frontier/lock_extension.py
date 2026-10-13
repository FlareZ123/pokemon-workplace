"""Conditional source-aware lock frontier for Wally/Tapu slot alternatives.

These are opposing board-state counterfactuals, not a metagame prevalence model.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.tests.mew_wally_slot_frontier.reproduce import FRONTIER
from results.tests.mew_wally_lock_matrix.reproduce import (
    exact as lock_exact, labeled_oracle as lock_physical_oracle,
)


def pool(wally: int, lele: int) -> tuple[int, ...]:
    # Mew, Genesect, VMAX, Wally, DCE, VIP, Quick, Ultra, Lele, Sky,
    # Field Blower, Lost Vacuum, all other (including remaining Red Cards).
    values = (4, 4, 3, wally, 4, 3, 4, 4, lele, 2, 1, 1, 29 - (wally - 1) - lele)
    assert sum(values) == 60
    return values


def main() -> None:
    for small in (
        (1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 0, 0, 2),
        (1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 0, 0, 2),
    ):
        assert sum(small) == 12
        for path in (False, True):
            for item in (False, True):
                for ability in (False, True):
                    for supporter in (False, True):
                        lhs = lock_exact(small, 3, 2, path, item, ability, supporter)
                        rhs = lock_physical_oracle(
                            small, 3, 2, path, item, ability, supporter
                        )
                        assert lhs == rhs, (small, path, item, ability, supporter, lhs, rhs)
        print("LOCKED PHYSICAL ORACLE PASS N=12, repeated Wally/Lele, 16 states")

    rows = {}
    for name, (wally, lele) in FRONTIER.items():
        inputs = pool(wally, lele)
        for path in (False, True):
            for item in (False, True):
                for ability in (False, True):
                    result = sum(lock_exact(inputs, 7, 6, path, item, ability).values(), Fraction(0))
                    rows[name, path, item, ability] = result
                    print(
                        f"{name:27s} Path={int(path)} Item={int(item)} "
                        f"Ability={int(ability)} chance={float(result):.12%}; exact={result}"
                    )
    expected = {
        (False, False, False): Fraction(207472683238253, 2367715165697700),
        (True, False, False): Fraction(6843086873823, 148403799559400),
        (False, True, False): Fraction(741946199453, 46178841884175),
        (True, True, False): Fraction(2205367535897, 184715367536700),
        (False, False, True): Fraction(3611784934223, 130550710890600),
        (False, True, True): Fraction(10535680679, 942425344575),
    }
    for flags, fraction in expected.items():
        assert rows[("two_Wally_one_Lele", *flags)] == fraction, flags

    assert rows["two_Wally_one_Lele", False, False, False] > rows[
        "one_Wally_two_Lele", False, False, False
    ]
    for path in (False, True):
        for item in (False, True):
            for ability in (False, True):
                assert rows["two_Wally_one_Lele", path, item, ability] > rows[
                    "one_Wally_two_Lele", path, item, ability
                ], (path, item, ability)
    print("MODEL COMPARISON PASS: W2L1 > W1L2 under all eight conditional scenarios")


if __name__ == "__main__":
    main()
