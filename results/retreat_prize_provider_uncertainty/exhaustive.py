"""Exhaustive finite witness: conditional Retreat payment is snapshot-invariant."""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_dynamic_energy_units import (
    RetreatEnergyProviderContext,
    retreat_with_dynamic_energy_units,
    unresolved_selected_prize_provider_ids,
)
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def make_case(counter_cache: int, reversal_cache: int):
    cards = (
        EnergyAttachment(
            "counter", "Counter Energy", ("C",) * counter_cache,
            print_id="sm4-100",
        ),
        EnergyAttachment(
            "reversal", "Reversal Energy", ("C",) * reversal_cache,
            print_id="sv2-192",
        ),
        EnergyAttachment(
            "dce", "Double Colorless Energy", ("C", "C"),
            print_id="base1-96",
        ),
        EnergyAttachment("basic", "Basic Psychic Energy", ("P",)),
    )
    active = make_pokemon(
        "active", "Evolution", tags=("Stage1",), energy=cards,
    )
    pivot = make_pokemon("pivot", "Pivot")
    classes = tuple(sorted(
        (card.instance_id, "class-" + card.instance_id) for card in cards
    ))
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                (name, "attached"): 1 for _, name in classes
            }),
            board=make_board(active, (pivot,)),
            instance_classes=classes,
        ),
    )


def execute(state, selected, cost, context):
    result = retreat_with_dynamic_energy_units(
        state, "pivot", retreat_cost=cost, discard_energy_ids=selected,
        provider_context=context,
    )
    return result is not None and result.committed


def main() -> None:
    behind = RetreatEnergyProviderContext(
        own_prizes_remaining=4, opponent_prizes_remaining=2,
    )
    tied = RetreatEnergyProviderContext(
        own_prizes_remaining=2, opponent_prizes_remaining=2,
    )
    witness_count = 0
    always_legal = always_illegal = conditional = 0
    ids = ("counter", "reversal", "dce", "basic")

    for counter_cache, reversal_cache in product((1, 2), (1, 3)):
        state = make_case(counter_cache, reversal_cache)
        for count in range(5):
            for selected in combinations(ids, count):
                selected_set = set(selected)
                for cost in range(9):
                    physically_eligible = (
                        count <= cost if cost > 0 else count == 0
                    )
                    fixed = (2 if "dce" in selected_set else 0)
                    fixed += (1 if "basic" in selected_set else 0)
                    low = fixed + int("counter" in selected_set)
                    low += int("reversal" in selected_set)
                    high = fixed + 2 * int("counter" in selected_set)
                    high += 3 * int("reversal" in selected_set)
                    low_ok = physically_eligible and low >= cost
                    high_ok = physically_eligible and high >= cost
                    if cost == 0:
                        low_ok = high_ok = count == 0

                    actual_low = execute(state, selected, cost, tied)
                    actual_high = execute(state, selected, cost, behind)
                    assert (actual_low, actual_high) == (low_ok, high_ok), (
                        counter_cache, reversal_cache, selected, cost,
                        "known-context mismatch",
                    )

                    unknown = execute(state, selected, cost, None)
                    unresolved = unresolved_selected_prize_provider_ids(
                        state, selected, retreat_cost=cost,
                    )
                    if low_ok and high_ok:
                        assert unknown and unresolved == ()
                        always_legal += 1
                    elif not low_ok and not high_ok:
                        assert not unknown and unresolved == ()
                        always_illegal += 1
                    else:
                        assert not unknown and unresolved
                        conditional += 1
                    witness_count += 1

    assert witness_count == 576
    print("exact Prize-bound Retreat exhaustive test: PASS")
    print({
        "witnesses": witness_count,
        "guaranteed": always_legal,
        "impossible": always_illegal,
        "Prize_contingent": conditional,
    })


if __name__ == "__main__":
    main()
