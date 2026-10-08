"""Regression: live Ability-based Retreat denial versus normal switching."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import ToolAttachment, make_board, make_pokemon, switch_active
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_ability_denial import opposing_retreat_denial_source_ids
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def state(*, conditions=(), tool=None, temporary_retreat_lock=False):
    holder = make_pokemon(
        "own", "Own Evolution", tags=("Stage1",),
        special_conditions=conditions,
        tool=tool,
        temporary_retreat_lock=temporary_retreat_lock,
    )
    pivot = make_pokemon("pivot", "Pivot")
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({}),
            board=make_board(holder, (pivot,)),
            instance_classes=(),
        ),
    )


def source(name, print_id, *, enabled=True, object_id="source"):
    return make_pokemon(
        object_id, name, print_id=print_id, abilities_enabled=enabled,
    )


def attempt(our_state, opp):
    return attempt_board_derived_retreat(
        our_state, "pivot",
        base_retreat_cost=2,
        discard_energy_ids=(),
        opponent_board=opp,
    )


def main() -> None:
    float_stone = ToolAttachment(
        "float", "Float Stone", print_id="xy8-137",
    )
    our = state(tool=float_stone)
    blank = make_board(make_pokemon("opp", "Opponent"))
    allowed = attempt(our, blank)
    assert allowed.effective_retreat_cost == 0
    assert allowed.retreat_denial_source_ids == ()
    assert allowed.transaction is not None and allowed.transaction.committed

    # Active-only Ability sources block even a zero-cost Retreat.
    active_sources = (
        ("bw8-101", "Snorlax"),
        ("pgo-55", "Snorlax"),
        ("sm35-47", "Spiritomb"),
        ("sv3pt5-139", "Omastar"),
        ("swsh3-91", "Flygon"),
    )
    for print_id, name in active_sources:
        opposing = make_board(source(name, print_id))
        result = attempt(our, opposing)
        assert result.effective_retreat_cost == 0
        assert result.retreat_denial_source_ids == ("source",)
        assert result.transaction is None
        suppressed = make_board(source(name, print_id, enabled=False))
        assert attempt(our, suppressed).transaction is not None

        # The same source on the Bench is inactive for these five prints.
        bench_source = make_board(
            make_pokemon("opp", "Opponent"),
            (source(name, print_id),),
        )
        assert attempt(our, bench_source).retreat_denial_source_ids == ()
        assert attempt(our, bench_source).transaction is not None

    # Cradily blocks any relevant Special Condition from either position.
    cradily = source("Cradily", "sm12-11")
    cradily_bench = make_board(
        make_pokemon("opp", "Opponent"), (cradily,),
    )
    for condition in ("Poisoned", "Burned", "Asleep", "Paralyzed", "Confused"):
        result = attempt(state(conditions=(condition,), tool=float_stone), cradily_bench)
        assert result.retreat_denial_source_ids == ("source",)
        assert result.transaction is None
    assert attempt(our, cradily_bench).transaction is not None
    assert attempt(
        state(conditions=("Poisoned",), tool=float_stone),
        make_board(make_pokemon("opp", "Opponent"),
                   (source("Cradily", "sm12-11", enabled=False),)),
    ).transaction is not None

    # Dragalge is specifically Poisoned-gated and can work from the Bench.
    for print_id in ("xy2-71", "xyp-XY10"):
        dragalge = make_board(
            make_pokemon("opp", "Opponent"),
            (source("Dragalge", print_id),),
        )
        poisoned = state(conditions=("Poisoned",), tool=float_stone)
        assert attempt(poisoned, dragalge).retreat_denial_source_ids == ("source",)
        assert attempt(poisoned, dragalge).transaction is None
        assert attempt(
            state(conditions=("Burned",), tool=float_stone), dragalge,
        ).transaction is not None

    # Multiple independent sources retain separate provenance.
    poisoned = state(conditions=("Poisoned",), tool=float_stone)
    double = make_board(
        make_pokemon("opp", "Opponent"),
        (
            source("Cradily", "sm12-11", object_id="cradily"),
            source("Dragalge", "xy2-71", object_id="dragalge"),
        ),
    )
    assert opposing_retreat_denial_source_ids(
        poisoned.energy.board, double
    ) == ("cradily", "dragalge")

    # The opponent's passive denial does not forbid an effect-based switch.
    switched = switch_active(poisoned.energy.board, "pivot")
    assert switched is not None and switched.active_id == "pivot"

    # A separate attack-applied Retreat lock remains a distinct gate.
    temporarily_locked = state(
        tool=float_stone, temporary_retreat_lock=True,
    )
    assert attempt(temporarily_locked, blank).transaction is None

    print("Ability Retreat-denial geometry: PASS")
    print("tested active-only prints:", len(active_sources))
    print("tested passive conditional prints: 3")


if __name__ == "__main__":
    main()
