"""Exact-board regressions for global and positional Retreat Cost sources."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_cost_semantics import effective_retreat_cost
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_environment_modifiers import derive_environment_retreat_modifiers
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def board(active, *bench):
    return make_board(active, bench)


def actor(active, *bench):
    energy = active.energy
    classes = tuple(
        (card.instance_id, "class-" + card.instance_id) for card in energy
    )
    zones = ZoneCountState.from_mapping({
        (card_class, "attached"): 1 for _, card_class in classes
    })
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=zones,
            board=board(active, *bench),
            instance_classes=classes,
        ),
    )


def main() -> None:
    evolution = make_pokemon("evo", "Zoroark", tags=("Stage1",))
    basic = make_pokemon("basic", "Zorua", tags=("Basic",))
    pivot = make_pokemon("pivot", "Pivot")
    sn1 = make_pokemon(
        "sn1", "Hisuian Sneasler", print_id="swsh10-93", tags=("Stage1",)
    )
    sn2 = make_pokemon(
        "sn2", "Hisuian Sneasler", print_id="swsh10-93", tags=("Stage1",)
    )
    a1 = make_pokemon("a1", "Ariados", print_id="sv6-5", tags=("Stage1",))
    a2 = make_pokemon("a2", "Ariados", print_id="sv6-5", tags=("Stage1",))
    opponent = board(a1, a2)

    combined = derive_environment_retreat_modifiers(
        board(evolution, sn1, sn2), opponent,
        stadium_print_id="swsh2-160",
    )
    assert sorted(m.delta for m in combined) == [-2, -2, 1, 1, 2]
    assert effective_retreat_cost(2, combined) == 2
    assert len({m.effect_id for m in combined}) == 5

    no_evolution = derive_environment_retreat_modifiers(
        board(basic, sn1), opponent,
    )
    assert [m.delta for m in no_evolution] == [-2]

    disabled_sneasler = make_pokemon(
        "sn1", "Hisuian Sneasler", print_id="swsh10-93",
        abilities_enabled=False,
    )
    disabled_ariados = make_pokemon(
        "a1", "Ariados", print_id="sv6-5",
        abilities_enabled=False,
    )
    assert derive_environment_retreat_modifiers(
        board(evolution, disabled_sneasler),
        board(disabled_ariados),
        stadium_print_id="swsh2-160",
        stadium_effect_enabled=False,
    ) == ()

    # Both effects have explicit ownership constraints.
    assert derive_environment_retreat_modifiers(
        board(evolution, a1), board(sn1)
    ) == ()

    # Carry and Climb is Bench-only, so an Active Sneasler gives no reduction.
    assert derive_environment_retreat_modifiers(
        board(sn1, pivot), board(basic)
    ) == ()

    assert [m.delta for m in derive_environment_retreat_modifiers(
        board(evolution, pivot), board(basic), stadium_print_id="swsh2-160",
    )] == [2]
    assert [m.delta for m in derive_environment_retreat_modifiers(
        board(evolution, pivot), board(basic), stadium_print_id="swsh2-161",
    )] == []

    # Integration: a single DCE pays the dynamically computed cost 2.
    dce = EnergyAttachment(
        "dce", "Double Colorless Energy", ("C", "C"), print_id="base1-96"
    )
    funded = make_pokemon(
        "evo", "Zoroark", tags=("Stage1",), energy=(dce,)
    )
    attempt = attempt_board_derived_retreat(
        actor(funded, pivot, sn1), "pivot",
        base_retreat_cost=1,
        discard_energy_ids=("dce",),
        opponent_board=board(a1),
        stadium_print_id="swsh2-160",
    )
    assert attempt.effective_retreat_cost == 2
    assert attempt.transaction is not None and attempt.transaction.committed
    assert attempt.transaction.state.energy.zones.count("class-dce", "discard") == 1

    # Move the same Sneasler source into the Active Spot, losing the -2.
    # There is now insufficient Energy for cost 4.
    attempt2 = attempt_board_derived_retreat(
        actor(sn1, funded, pivot), "pivot",
        base_retreat_cost=1,
        discard_energy_ids=("dce",),
        opponent_board=board(a1),
        stadium_print_id="swsh2-160",
    )
    assert attempt2.effective_retreat_cost == 3
    assert attempt2.transaction is None

    # Float Stone has D-13 priority over all additive modifiers.
    float_stone = ToolAttachment(
        "float", "Float Stone", print_id="xy8-137"
    )
    free = make_pokemon(
        "evo", "Zoroark", tags=("Stage1",), tool=float_stone
    )
    attempt3 = attempt_board_derived_retreat(
        actor(free, pivot), "pivot",
        base_retreat_cost=2,
        discard_energy_ids=(),
        opponent_board=opponent,
        stadium_print_id="swsh2-160",
    )
    assert attempt3.effective_retreat_cost == 0
    assert attempt3.transaction is not None and attempt3.transaction.committed
    assert len(attempt3.applied_modifiers) == 4

    print("retreat environment modifiers: PASS")
    print("stacking witness:", sorted(m.delta for m in combined))
    print("funded combined cost:", attempt.effective_retreat_cost)


if __name__ == "__main__":
    main()
