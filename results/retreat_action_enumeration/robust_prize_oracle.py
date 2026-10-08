"""Robust action oracle: unknown Prizes equal intersection of known worlds."""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_dynamic_energy_units import RetreatEnergyProviderContext
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


BEHIND = RetreatEnergyProviderContext(
    own_prizes_remaining=4, opponent_prizes_remaining=2,
)
TIED = RetreatEnergyProviderContext(
    own_prizes_remaining=2, opponent_prizes_remaining=2,
)


def make_case(
    which_cards: tuple[str, ...],
    counter_cache: int,
    reversal_cache: int,
    holder_tags: tuple[str, ...],
):
    candidates = {
        "counter": EnergyAttachment(
            "counter", "Counter Energy", ("C",) * counter_cache, "sm4-100",
        ),
        "reversal": EnergyAttachment(
            "reversal", "Reversal Energy", ("C",) * reversal_cache, "sv2-192",
        ),
        "dce": EnergyAttachment(
            "dce", "Double Colorless Energy", ("C", "C"), "bw4-92",
        ),
        "basic": EnergyAttachment("basic", "Basic Psychic Energy", ("P",)),
    }
    attached = tuple(candidates[name] for name in which_cards)
    holder = make_pokemon(
        "active", "Holder", tags=holder_tags, energy=attached,
    )
    pivot = make_pokemon("pivot", "Pivot")
    classes = tuple(sorted(
        (energy.instance_id, "class-" + energy.instance_id)
        for energy in attached
    ))
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                (card_class, "attached"): 1 for _, card_class in classes
            }),
            board=make_board(holder, (pivot,)),
            instance_classes=classes,
        ),
    )


def action_set(case, opponent, cost, context=None):
    result = enumerate_board_derived_retreat_actions(
        case, opponent, base_retreat_cost=cost,
        provider_context=context,
    )
    return (
        {tuple(sorted(action.discard_energy_ids)) for action in result.actions},
        result,
    )


def main() -> None:
    opponent = make_board(make_pokemon("opp", "Opponent"))
    card_pool = ("counter", "reversal", "dce", "basic")
    subsets = [
        subset
        for n in range(len(card_pool) + 1)
        for subset in combinations(card_pool, n)
    ]
    tags = (
        ("Stage1",),
        ("Basic",),
        ("Stage1", "RuleBox"),
        ("Stage1", "Pokemon-GX", "RuleBox"),
    )
    cases = 0
    robust_actions = conditional_action_choices = 0

    for subset, c_units, r_units, holder, cost in product(
        subsets,
        (1, 2),
        (1, 3),
        tags,
        range(7),
    ):
        case = make_case(subset, c_units, r_units, holder)
        unknown, observed = action_set(case, opponent, cost)
        low, low_info = action_set(case, opponent, cost, TIED)
        high, high_info = action_set(case, opponent, cost, BEHIND)
        assert low_info.information_complete and high_info.information_complete

        guaranteed = low & high
        assert unknown == guaranteed, (
            subset, c_units, r_units, holder, cost,
            sorted(unknown), sorted(guaranteed),
        )
        assert low <= high, (subset, c_units, r_units, holder, cost)
        robust_actions += len(guaranteed)
        conditional_action_choices += len(high - low)
        cases += 1

    assert cases == 1792

    # An explicit counterexample to treating theoretical provider maximum
    # as automatically executable under unknown Prize context.
    example = make_case(("counter", "dce"), 2, 3, ("Stage1",))
    unknown_three, _ = action_set(example, opponent, 3)
    unknown_four, _ = action_set(example, opponent, 4)
    assert unknown_three == {("counter", "dce")}
    assert unknown_four == set()
    assert action_set(example, opponent, 4, BEHIND)[0] == {
        ("counter", "dce"),
    }
    assert action_set(example, opponent, 4, TIED)[0] == set()

    print("Robust Prize-information Retreat action oracle: PASS")
    print({
        "boards": cases,
        "guaranteed_action_count": robust_actions,
        "contingent_behind_only_action_count": conditional_action_choices,
    })


if __name__ == "__main__":
    main()
