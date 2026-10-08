"""Reproduce payment-substitution slack identities."""

from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from payment_substitution_slack import (
    PaymentSubstitutionSlack,
    harto_quick_ball_ultra_ball_table,
)


def main() -> None:
    expected = (
        (0, 3, 1),
        (1, 2, 0),
        (2, 1, 0),
        (3, 0, 0),
        (4, 0, 0),
    )
    assert harto_quick_ball_ultra_ball_table() == expected

    for weaker_cost in range(4):
        for stronger_cost in range(1, 5):
            for safe_external in range(8):
                model = PaymentSubstitutionSlack(
                    weaker_cost=weaker_cost,
                    stronger_cost=stronger_cost,
                    safe_external=safe_external,
                )
                assert (
                    model.safe_external_threshold_sequential
                    == weaker_cost + stronger_cost
                )
                assert (
                    model.safe_external_threshold_stronger_first
                    == stronger_cost - 1
                )
                assert (
                    model.threshold_reduction == weaker_cost + 1
                )
                assert model.critical_pressure_reduction >= 0

    print("Harto (safe, QB-first q, stronger-first q):")
    for row in expected:
        print(row)
    print("generic threshold identities passed")


if __name__ == "__main__":
    main()
