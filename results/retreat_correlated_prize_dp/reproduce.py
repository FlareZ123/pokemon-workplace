"""Independent physical oracle for correlated Prize-based Retreat DP."""
from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_pokemon, legal_retreat_energy_choices
from retreat_correlated_prize_dp import (
    CorrelatedPrizeEnergyGroup, count_correlated_prize_payments,
)


PROVIDERS = (
    ("counter", 1, 2),
    ("reversal", 1, 3),
    ("dce", 2, 2),
    ("basic", 1, 1),
)


def physical_sets(groups, cost: int, *, behind: bool) -> set[frozenset[str]]:
    energy = tuple(
        EnergyAttachment(
            f"{group.key}-{i}", group.key,
            ("C",) * (group.units_behind if behind else group.units_tied),
        )
        for group in groups for i in range(group.copies)
    )
    pokemon = make_pokemon("holder", "Holder", energy=energy)
    return {
        frozenset(payment)
        for payment in legal_retreat_energy_choices(pokemon, cost)
    }


def minimal(actions: set[frozenset[str]]) -> set[frozenset[str]]:
    return {
        payment for payment in actions
        if not any(other < payment for other in actions)
    }


def main() -> None:
    comparisons = paradox = 0
    lost = 0
    for sizes in product(range(3), repeat=4):
        groups = tuple(
            CorrelatedPrizeEnergyGroup(name, copies, lo, hi)
            for (name, lo, hi), copies in zip(PROVIDERS, sizes)
        )
        for cost in range(7):
            lower = physical_sets(groups, cost, behind=False)
            upper = physical_sets(groups, cost, behind=True)
            assert lower <= upper
            robust = lower & upper
            robust_min = minimal(robust)
            incorrect = minimal(lower) & minimal(upper)

            report = count_correlated_prize_payments(groups, cost)
            assert (
                report.robust_legal, report.possible_legal,
                report.robust_minimal, report.worldwise_minimal_intersection,
            ) == (len(robust), len(upper), len(robust_min), len(incorrect)), (
                sizes, cost, report
            )
            assert report.minimal_actions_lost_if_intersected_early >= 0
            if robust_min - incorrect:
                paradox += 1
                lost += len(robust_min - incorrect)
            comparisons += 1

    assert comparisons == 567 and paradox > 0
    witness = (
        CorrelatedPrizeEnergyGroup("counter", 1, 1, 2),
        CorrelatedPrizeEnergyGroup("basic", 1, 1, 1),
    )
    w = count_correlated_prize_payments(witness, 2)
    assert (w.robust_legal, w.possible_legal, w.robust_minimal,
            w.worldwise_minimal_intersection) == (1, 2, 1, 0)
    print("Correlated Prize-regime Retreat payment DP: PASS")
    print({"mixed_provider_cases": comparisons, "paradox_cases": paradox,
           "robust_minimal_payments_lost": lost,
           "witness_robust_vs_possible": (w.robust_legal, w.possible_legal)})


if __name__ == "__main__":
    main()
