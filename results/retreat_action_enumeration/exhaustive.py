"""Independent brute-force oracle for the bounded Retreat action enumerator."""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def make_actor(units: tuple[int, ...], bench_count: int, *, float_stone: bool):
    energy = tuple(
        EnergyAttachment(
            f"energy-{i}", "Basic Psychic Energy", ("P",) * count,
        )
        for i, count in enumerate(units)
    )
    tool = (
        ToolAttachment("float", "Float Stone", "xy8-137")
        if float_stone else None
    )
    active = make_pokemon("active", "Our Active", energy=energy, tool=tool)
    bench = tuple(
        make_pokemon(f"bench-{i}", "Bench Target")
        for i in range(bench_count)
    )
    classes = tuple(sorted(
        (item.instance_id, "class-" + item.instance_id) for item in energy
    ))
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                (name, "attached"): 1 for _, name in classes
            }),
            board=make_board(active, bench),
            instance_classes=classes,
        ),
    )


def all_subsets(energy_ids: tuple[str, ...]):
    return tuple(
        picked
        for size in range(len(energy_ids) + 1)
        for picked in combinations(energy_ids, size)
    )


def main() -> None:
    blank = make_board(make_pokemon("opp", "Opponent"))
    snorlax = make_board(make_pokemon(
        "snorlax", "Snorlax", print_id="pgo-55", tags=("Basic",),
    ))
    total_scenarios = total_branches = legal_branches = 0

    unit_sequences = [
        units for size in range(4)
        for units in product((1, 2), repeat=size)
    ]
    assert len(unit_sequences) == 15

    for units, base_cost, bench_count, uses_float, stadium, opp in product(
        unit_sequences,
        range(5),
        (1, 2),
        (False, True),
        (None, "swsh2-160", "sv6-153"),
        (blank, snorlax),
    ):
        scenario = make_actor(
            units, bench_count, float_stone=uses_float,
        )
        options = dict(
            base_retreat_cost=base_cost,
            opponent_board=opp,
            stadium_print_id=stadium,
        )
        generated = enumerate_board_derived_retreat_actions(
            scenario, opp,
            base_retreat_cost=base_cost,
            stadium_print_id=stadium,
        )
        assert generated.information_complete

        expected = set()
        energy_ids = tuple(
            item.instance_id
            for item in scenario.energy.board.get("active").energy
        )
        for target in scenario.energy.board.bench_ids:
            for selected in all_subsets(energy_ids):
                attempted = attempt_board_derived_retreat(
                    scenario,
                    target,
                    discard_energy_ids=selected,
                    **options,
                )
                if attempted.transaction is not None and attempted.transaction.committed:
                    expected.add((target, tuple(sorted(selected))))

        actual = {
            (action.bench_object_id, tuple(sorted(action.discard_energy_ids)))
            for action in generated.actions
        }
        assert actual == expected, (
            units, base_cost, bench_count, uses_float, stadium,
            opp.active_id, len(actual), len(expected),
            sorted(actual ^ expected),
        )
        legal_branches += len(actual)
        total_branches += bench_count * 2 ** len(units)
        total_scenarios += 1

    assert total_scenarios == 1800
    print("Retreat enumerator independent finite oracle: PASS")
    print({
        "scenarios": total_scenarios,
        "physical_subsets_checked": total_branches,
        "committed_branches": legal_branches,
    })


if __name__ == "__main__":
    main()
