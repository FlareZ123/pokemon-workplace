"""Verify exact Retreat payment DP against physical and orbit oracles."""
from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_pokemon, legal_retreat_energy_choices
from retreat_payment_branch_complexity import count_retreat_payments
from retreat_payment_polynomial_dp import count_retreat_payments_dp
from retreat_payment_symmetry import InterchangeableEnergy, retreat_payment_orbits


def main() -> None:
    tested = 0
    for sizes in product(range(3), repeat=4):
        groups = tuple(
            InterchangeableEnergy(str(i), count, i + 1)
            for i, count in enumerate(sizes)
        )
        attachments = tuple(
            EnergyAttachment(f"class-{g.key}-card-{i}", "Special Energy", ("C",) * g.provided_units)
            for g in groups
            for i in range(g.copies)
        )
        pokemon = make_pokemon("holder", "Holder", energy=attachments)
        amounts = {e.instance_id: len(e.units) for e in attachments}
        for cost in range(9):
            actions = legal_retreat_energy_choices(pokemon, cost)
            brute_minimal = sum(
                all(
                    sum(amounts[other] for other in subset if other != selected) < cost
                    for selected in subset
                )
                for subset in actions
            )
            report = count_retreat_payments_dp(groups, cost)
            orbits = retreat_payment_orbits(groups, cost)
            assert (report.counts.full, report.counts.inclusion_minimal) == (
                len(actions), brute_minimal,
            ), (sizes, cost)
            assert report.counts.full == sum(
                orbit.physical_multiplicity for orbit in orbits
            )
            assert report.counts.inclusion_minimal == sum(
                orbit.physical_multiplicity for orbit in orbits if orbit.inclusion_minimal
            )
            tested += 1
    assert tested == 729

    # Cross-validate two-unit specialization against earlier closed form.
    for ones, twos, cost in product(range(7), range(7), range(7)):
        groups = (
            InterchangeableEnergy("single", ones, 1),
            InterchangeableEnergy("double", twos, 2),
        )
        assert count_retreat_payments_dp(groups, cost).counts == count_retreat_payments(
            ones, twos, cost
        )

    extended = (
        InterchangeableEnergy("basic", 8, 1),
        InterchangeableEnergy("double", 4, 2),
        InterchangeableEnergy("triple", 4, 3),
        InterchangeableEnergy("quadruple", 1, 4),
    )
    report = count_retreat_payments_dp(extended, 4)
    assert (report.counts.full, report.counts.inclusion_minimal) == (3081, 243)
    print("Arbitrary-unit Retreat payment DP: PASS")
    print({"physical_oracle_cases": tested, "specialization_cases": 343,
           "example_full": report.counts.full,
           "example_minimal": report.counts.inclusion_minimal,
           "peak_dp_states": report.state_count,
           "dp_transitions": report.transitions})


if __name__ == "__main__":
    main()
