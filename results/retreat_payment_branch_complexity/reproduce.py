"""Independent labeled-card check of the Retreat payment count formula."""
from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from board_object_kernel import EnergyAttachment, make_pokemon, legal_retreat_energy_choices
from retreat_payment_branch_complexity import count_retreat_payments


def main() -> None:
    checked = 0
    for ones, twos, cost in product(range(7), range(7), range(7)):
        energy = tuple(
            EnergyAttachment(f"one-{i}", "Basic Energy", ("C",))
            for i in range(ones)
        ) + tuple(
            EnergyAttachment(f"two-{i}", "Double Colorless Energy", ("C", "C"))
            for i in range(twos)
        )
        pokemon = make_pokemon("p", "Holder", energy=energy)
        choices = legal_retreat_energy_choices(pokemon, cost)
        units = {e.instance_id: len(e.units) for e in energy}
        minimal = sum(
            all(
                sum(units[j] for j in payment if j != i) < cost
                for i in payment
            ) for payment in choices
        )
        expected = count_retreat_payments(ones, twos, cost)
        assert (len(choices), minimal) == (expected.full, expected.inclusion_minimal), (
            ones, twos, cost
        )
        checked += 1

    assert checked == 343
    assert count_retreat_payments(1, 1, 2).full == 2
    assert count_retreat_payments(1, 1, 2).inclusion_minimal == 1
    assert count_retreat_payments(3, 2, 2).full == 12
    assert count_retreat_payments(3, 2, 2).inclusion_minimal == 5
    assert count_retreat_payments(4, 4, 3).full == 78
    assert count_retreat_payments(4, 4, 3).inclusion_minimal == 26
    assert count_retreat_payments(8, 8, 4).full == 2352
    assert count_retreat_payments(8, 8, 4).inclusion_minimal == 322
    assert count_retreat_payments(8, 8, 6).full == 13678
    assert count_retreat_payments(8, 8, 6).inclusion_minimal == 1428
    print("Physical Retreat payment counts: PASS", checked)


if __name__ == "__main__":
    main()
