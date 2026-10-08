"""Finite branch oracle for exact physical Retreat action enumeration."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_dynamic_energy_units import RetreatEnergyProviderContext
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor(energies=(), *, tool=None, pivots=2, conditions=()):
    active = make_pokemon(
        "active", "Active", tags=("Stage1",),
        energy=tuple(energies), tool=tool, special_conditions=conditions,
    )
    bench = tuple(make_pokemon(f"pivot-{i}", "Pivot") for i in range(pivots))
    classes = tuple(sorted(
        (energy.instance_id, "class-" + energy.instance_id)
        for energy in energies
    ))
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                (card_class, "attached"): 1
                for _, card_class in classes
            }),
            board=make_board(active, bench),
            instance_classes=classes,
        ),
    )


def options(state, opponent, cost, **kwargs):
    return enumerate_board_derived_retreat_actions(
        state, opponent, base_retreat_cost=cost, **kwargs,
    )


def main() -> None:
    blank = make_board(make_pokemon("opp", "Opponent"))
    dce = EnergyAttachment(
        "dce", "Double Colorless Energy", ("C", "C"), "base1-96",
    )
    a = EnergyAttachment("a", "Basic Psychic Energy", ("P",))
    b = EnergyAttachment("b", "Basic Fighting Energy", ("F",))
    full = actor((dce, a, b))

    basic = options(full, blank, 2)
    assert basic.information_complete
    assert basic.checked_candidate_count == 8
    assert len(basic.actions) == 8
    assert {
        tuple(sorted(action.discard_energy_ids)) for action in basic.actions
    } == {
        ("dce",), ("a", "b"), ("a", "dce"), ("b", "dce")
    }
    assert {action.bench_object_id for action in basic.actions} == {
        "pivot-0", "pivot-1"
    }
    for action in basic.actions:
        transaction = action.attempt.transaction
        assert transaction is not None and transaction.committed
        next_board = transaction.state.energy.board
        assert next_board.active_id == action.bench_object_id
        assert transaction.state.unified.turn_budget is not None
        assert transaction.state.unified.turn_budget.retreat_used
        paid = set(action.discard_energy_ids)
        for energy in (dce, a, b):
            card_class = "class-" + energy.instance_id
            assert transaction.state.energy.zones.count(
                card_class, "discard"
            ) == (1 if energy.instance_id in paid else 0)

    # Exact additive Stadium cost contracts the physical payment frontier.
    mined = options(full, blank, 2, stadium_print_id="swsh2-160")
    assert mined.preflight is not None
    assert mined.preflight.effective_retreat_cost == 4
    assert mined.checked_candidate_count == 2
    assert len(mined.actions) == 2
    assert all(
        set(choice.discard_energy_ids) == {"dce", "a", "b"}
        for choice in mined.actions
    )

    # A no-Retreat-Cost Tool removes every Energy payment, not Bench choices.
    float_stone = ToolAttachment("float", "Float Stone", "xy8-137")
    free = actor((dce, a, b), tool=float_stone)
    zero = options(free, blank, 2)
    assert zero.preflight is not None
    assert zero.preflight.effective_retreat_cost == 0
    assert {c.discard_energy_ids for c in zero.actions} == {()}
    assert len(zero.actions) == 2

    tower = options(
        free, blank, 2, stadium_print_id="sv6-153",
    )
    assert tower.preflight is not None
    assert tower.preflight.effective_retreat_cost == 2
    assert len(tower.actions) == 8

    # Snorlax blocks all normal Retreat payments, even when zero-cost.
    snorlax = make_board(make_pokemon(
        "snorlax", "Snorlax", print_id="pgo-55", tags=("Basic",),
    ))
    blocked = options(free, snorlax, 2)
    assert blocked.information_complete
    assert blocked.actions == ()
    assert blocked.checked_candidate_count == 2
    assert blocked.preflight is not None
    assert blocked.preflight.retreat_denial_source_ids == ("snorlax",)

    # Unknown Prize state: contingent payments are withheld, while
    # guaranteed physical payment combinations remain available.
    counter = EnergyAttachment(
        "counter", "Counter Energy", ("C", "C"), "sm4-100",
    )
    conditional = actor((counter,), pivots=1)
    unknown = options(conditional, blank, 2)
    assert not unknown.information_complete
    assert unknown.checked_candidate_count == 1
    assert unknown.actions == ()
    behind = RetreatEnergyProviderContext(
        own_prizes_remaining=4, opponent_prizes_remaining=2,
    )
    tied = RetreatEnergyProviderContext(
        own_prizes_remaining=2, opponent_prizes_remaining=2,
    )
    assert len(options(conditional, blank, 2, provider_context=behind).actions) == 1
    assert options(conditional, blank, 2, provider_context=tied).actions == ()

    mixed = actor((counter, dce), pivots=1)
    guaranteed = options(mixed, blank, 3)
    assert not guaranteed.information_complete
    assert len(guaranteed.actions) == 1
    assert set(guaranteed.actions[0].discard_energy_ids) == {"counter", "dce"}

    # Rescue Board threshold is unknown, but base cost 1 already becomes
    # zero from its unconditional -1: the no-cost mode changes nothing.
    rescue = actor(
        (), pivots=1,
        tool=ToolAttachment("rescue", "Rescue Board", "sv5-159"),
    )
    safe_rescue = options(rescue, blank, 1)
    assert not safe_rescue.information_complete
    assert safe_rescue.preflight is not None
    assert safe_rescue.preflight.tool_action_sufficient
    assert safe_rescue.checked_candidate_count == 1
    assert len(safe_rescue.actions) == 1
    assert safe_rescue.actions[0].discard_energy_ids == ()

    # At base cost 2, the unknown threshold changes cost 1 versus 0.
    unknown_rescue = options(rescue, blank, 2)
    assert not unknown_rescue.information_complete
    assert unknown_rescue.preflight is not None
    assert not unknown_rescue.preflight.tool_action_sufficient
    assert unknown_rescue.actions == ()
    assert unknown_rescue.checked_candidate_count == 0
    resolved = options(rescue, blank, 2, active_remaining_hp=30)
    assert len(resolved.actions) == 1
    assert resolved.actions[0].discard_energy_ids == ()
    assert options(
        rescue, blank, 2, active_remaining_hp=100,
    ).actions == ()

    # Outgoing with no Bench has no legal Retreat destination.
    alone = actor((dce,), pivots=0)
    no_pivots = options(alone, blank, 2)
    assert no_pivots.actions == ()
    assert no_pivots.checked_candidate_count == 0

    print("Board-derived Retreat action enumeration: PASS")
    print("cost 2: 8 branches; Galar Mine cost 4: 2; Float Stone: 2")
    print("unknown Counter Energy: only universally valid payment branches")


if __name__ == "__main__":
    main()
