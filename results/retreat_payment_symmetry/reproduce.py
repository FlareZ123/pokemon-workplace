"""Verify symmetry-orbit counts against physical Retreat action generation."""
from __future__ import annotations

from collections import Counter
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon, legal_retreat_energy_choices
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_payment_symmetry import InterchangeableEnergy, retreat_payment_orbits
from retreat_payment_branch_complexity import count_retreat_payments
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def group_fixture(ones: int, twos: int):
    energy = tuple(
        EnergyAttachment(f"one-{i}", "Basic Psychic Energy", ("P",))
        for i in range(ones)
    ) + tuple(
        EnergyAttachment(f"two-{i}", "Double Colorless Energy", ("C", "C"), "bw4-92")
        for i in range(twos)
    )
    groups = tuple(
        InterchangeableEnergy(k, num, units)
        for k, num, units in (("one", ones, 1), ("two", twos, 2))
    )
    return energy, groups


def verify_counts() -> None:
    comparisons = 0
    for ones, twos, cost in product(range(6), range(6), range(7)):
        energy, groups = group_fixture(ones, twos)
        legal = legal_retreat_energy_choices(make_pokemon("holder", "Holder", energy=energy), cost)
        classes = {e.instance_id: e.instance_id.split("-")[0] for e in energy}
        brute = Counter(
            tuple(sum(classes[instance] == label for instance in payment)
                  for label in ("one", "two"))
            for payment in legal
        )
        orbits = retreat_payment_orbits(groups, cost)
        actual = {row.paid_per_group: row.physical_multiplicity for row in orbits}
        assert brute == actual, (ones, twos, cost, brute, actual)
        counts = count_retreat_payments(ones, twos, cost)
        assert sum(row.physical_multiplicity for row in orbits) == counts.full
        assert sum(row.physical_multiplicity for row in orbits if row.inclusion_minimal) == counts.inclusion_minimal
        comparisons += 1
    assert comparisons == 252


def verify_physical_successors() -> None:
    energy, groups = group_fixture(2, 2)
    classes = tuple(
        sorted((e.instance_id, e.instance_id.split("-")[0]) for e in energy)
    )
    actor = make_pokemon(
        "holder", "Holder", energy=energy,
        tool=ToolAttachment("pouch", "Dashing Pouch", "sm4-92"),
        damage_counters=1,
    )
    state = RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                ("one", "attached"): 2, ("two", "attached"): 2,
            }),
            board=make_board(actor, (make_pokemon("pivot", "Pivot"),)),
            instance_classes=classes,
        ),
    )
    opponent = make_board(make_pokemon("opponent", "Opponent"))
    actual = enumerate_board_derived_retreat_actions(
        state, opponent, base_retreat_cost=2,
    )
    assert len(actual.actions) == 8
    orbits = retreat_payment_orbits(groups, 2)
    assert len(orbits) == 4
    assert sorted(row.physical_multiplicity for row in orbits) == [1, 1, 2, 4]

    copies = dict(classes)
    successors: dict[tuple[int, int], set[tuple]] = {}
    for action in actual.actions:
        tx = action.attempt.transaction
        assert tx is not None and tx.committed
        signature = (
            tuple(sum(copies[i] == label for i in action.discard_energy_ids)
                  for label in ("one", "two"))
        )
        successor = (
            tx.state.energy.zones.count("one", "hand"),
            tx.state.energy.zones.count("two", "hand"),
            tx.state.energy.zones.count("one", "attached"),
            tx.state.energy.zones.count("two", "attached"),
            tx.state.energy.board.active_id,
            tx.state.unified.turn_budget.retreat_used,
        )
        successors.setdefault(signature, set()).add(successor)

    assert len(successors) == 4
    assert all(len(projected) == 1 for projected in successors.values())
    assert Counter({
        key: len([action for action in actual.actions
                  if tuple(sum(copies[i] == label for i in action.discard_energy_ids)
                           for label in ("one", "two")) == key])
        for key in successors
    }) == Counter({row.paid_per_group: row.physical_multiplicity for row in orbits})


def main() -> None:
    verify_counts()
    verify_physical_successors()
    assert len(retreat_payment_orbits(
        (InterchangeableEnergy("one", 8, 1), InterchangeableEnergy("two", 8, 2)),
        4,
    )) == 9
    print("Retreat payment exchangeability orbits: PASS")
    print({"brute_force_cases": 252, "distinct_payments_in_fixture": 8,
           "distinct_class_count_orbits": 4,
           "large_16_attachment_orbits": 9, "large_physical_payments": 2352})


if __name__ == "__main__":
    main()
