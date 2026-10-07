"""Reproduce dynamic Special Energy provider state for Retreat."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_dynamic_energy_units import (
    DYNAMIC_UNIT_PRINT_IDS,
    RetreatEnergyProviderContext,
    refresh_active_retreat_energy_units,
    retreat_with_dynamic_energy_units,
)
from retreat_energy_transaction import RetreatEnergyTransactionState
from special_energy_unit_count_catalog import build as build_unit_catalog
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor_state(
    card_name: str,
    print_id: str,
    snapshot_units: int,
    *,
    holder_tags=(),
    extra_bench_tags=(),
) -> RetreatEnergyTransactionState:
    energy = EnergyAttachment(
        "energy",
        card_name,
        ("C",) * snapshot_units,
        print_id=print_id,
    )
    holder = make_pokemon(
        "holder",
        "Holder",
        tags=holder_tags,
        energy=(energy,),
    )
    pivot = make_pokemon("pivot", "Pivot")
    extras = tuple(
        make_pokemon(
            f"extra-{index}",
            f"Extra {index}",
            tags=tags,
        )
        for index, tags in enumerate(extra_bench_tags)
    )
    board = make_board(holder, (pivot,) + extras)
    energy_state = EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("energy-class", "attached"): 1,
        }),
        board=board,
        instance_classes=(("energy", "energy-class"),),
    )
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=energy_state,
    )


def unit_count(
    state: RetreatEnergyTransactionState,
    *,
    context: RetreatEnergyProviderContext | None = None,
) -> int:
    refreshed = refresh_active_retreat_energy_units(
        state,
        context=context,
    )
    return len(refreshed.energy.board.get("holder").energy[0].units)


def can_pay(
    state: RetreatEnergyTransactionState,
    cost: int,
    *,
    context: RetreatEnergyProviderContext | None = None,
    prism_star: bool = False,
):
    result = retreat_with_dynamic_energy_units(
        state,
        "pivot",
        retreat_cost=cost,
        discard_energy_ids=("energy",),
        provider_context=context,
        prism_star_energy_ids=("energy",) if prism_star else (),
    )
    return result


def main() -> None:
    catalog = build_unit_catalog(ROOT / "resources")
    assert {
        row["card_id"]
        for row in catalog["rows"]
    } == DYNAMIC_UNIT_PRINT_IDS

    ignition = actor_state(
        "Ignition Energy",
        "me2-124",
        1,
        holder_tags=("Stage1",),
    )
    assert unit_count(ignition) == 3
    assert can_pay(ignition, 3) is not None

    twin_basic = actor_state(
        "Twin Energy",
        "swsh2-174",
        1,
        holder_tags=("Basic",),
    )
    assert unit_count(twin_basic) == 2
    assert can_pay(twin_basic, 2) is not None

    twin_v = actor_state(
        "Twin Energy",
        "swsh2-174",
        2,
        holder_tags=("Basic", "Pokemon V"),
    )
    assert unit_count(twin_v) == 1
    assert can_pay(twin_v, 2) is None

    neo_stage2 = actor_state(
        "Neo Upper Energy",
        "sv5-162",
        1,
        holder_tags=("Stage2", "RuleBox"),
    )
    assert unit_count(neo_stage2) == 2
    assert can_pay(neo_stage2, 2) is not None

    neo_basic = actor_state(
        "Neo Upper Energy",
        "sv5-162",
        2,
        holder_tags=("Basic",),
    )
    assert unit_count(neo_basic) == 1
    assert can_pay(neo_basic, 2) is None

    behind = RetreatEnergyProviderContext(
        own_prizes_remaining=4,
        opponent_prizes_remaining=2,
    )
    tied = RetreatEnergyProviderContext(
        own_prizes_remaining=2,
        opponent_prizes_remaining=2,
    )

    counter_basic = actor_state(
        "Counter Energy",
        "sm4-100",
        1,
        holder_tags=("Basic",),
    )
    assert unit_count(counter_basic, context=behind) == 2
    assert can_pay(counter_basic, 2, context=behind) is not None
    assert unit_count(counter_basic, context=tied) == 1
    assert can_pay(counter_basic, 2, context=tied) is None
    # Unknown Prize state preserves the represented snapshot.
    assert unit_count(counter_basic) == 1

    counter_gx = actor_state(
        "Counter Energy",
        "sm4-100",
        2,
        holder_tags=("Stage1", "Pokemon-GX", "RuleBox"),
    )
    assert unit_count(counter_gx, context=behind) == 1
    assert can_pay(counter_gx, 2, context=behind) is None

    reversal = actor_state(
        "Reversal Energy",
        "sv4-266",
        1,
        holder_tags=("Stage1",),
    )
    assert unit_count(reversal, context=behind) == 3
    assert can_pay(reversal, 3, context=behind) is not None
    assert unit_count(reversal, context=tied) == 1
    assert can_pay(reversal, 3, context=tied) is None

    reversal_rule_box = actor_state(
        "Reversal Energy",
        "sv4-266",
        3,
        holder_tags=("Stage1", "RuleBox"),
    )
    assert unit_count(reversal_rule_box, context=behind) == 1
    assert can_pay(reversal_rule_box, 3, context=behind) is None

    super_boost_three_stage2 = actor_state(
        "Super Boost Energy ◇",
        "sm5-136",
        1,
        holder_tags=("Basic",),
        extra_bench_tags=(
            ("Stage2",),
            ("Stage2",),
            ("Stage2",),
        ),
    )
    assert unit_count(super_boost_three_stage2) == 4
    super_result = can_pay(
        super_boost_three_stage2,
        4,
        prism_star=True,
    )
    assert super_result is not None and super_result.committed
    assert super_result.state.energy.zones.count(
        "energy-class", "lost_zone"
    ) == 1

    super_boost_two_stage2 = actor_state(
        "Super Boost Energy ◇",
        "sm5-136",
        4,
        holder_tags=("Basic",),
        extra_bench_tags=(
            ("Stage2",),
            ("Stage2",),
        ),
    )
    assert unit_count(super_boost_two_stage2) == 1
    assert can_pay(
        super_boost_two_stage2,
        4,
        prism_star=True,
    ) is None

    print(json.dumps({
        "implemented_dynamic_prints": len(DYNAMIC_UNIT_PRINT_IDS),
        "implemented_dynamic_names": catalog["distinct_names"],
        "ignition_evolution_units": 3,
        "twin_basic_units": 2,
        "twin_v_units": 1,
        "neo_upper_stage2_units": 2,
        "counter_behind_eligible_units": 2,
        "reversal_behind_eligible_units": 3,
        "super_boost_three_stage2_units": 4,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
