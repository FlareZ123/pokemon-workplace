"""Regression: unknown Prize counts cannot authorize ambiguous Retreat payment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_dynamic_energy_units import (
    RetreatEnergyProviderContext,
    retreat_with_dynamic_energy_units,
)
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor(name, print_id, snapshot, *, tags=("Basic",), dce=False):
    attached = [
        EnergyAttachment(
            "conditional", name, ("C",) * snapshot, print_id=print_id,
        )
    ]
    if dce:
        attached.append(EnergyAttachment(
            "dce", "Double Colorless Energy", ("C", "C"), print_id="base1-96",
        ))
    holder = make_pokemon(
        "holder", "Holder", tags=tags, energy=tuple(attached),
    )
    pivot = make_pokemon("pivot", "Pivot")
    classes = tuple(
        (energy.instance_id, "class-" + energy.instance_id)
        for energy in attached
    )
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


def attempt(state, cost, selected, *, context=None):
    opponent = make_board(make_pokemon("opp", "Opponent"))
    return attempt_board_derived_retreat(
        state, "pivot",
        base_retreat_cost=cost,
        discard_energy_ids=selected,
        opponent_board=opponent,
        provider_context=context,
    )


def main() -> None:
    behind = RetreatEnergyProviderContext(
        own_prizes_remaining=4, opponent_prizes_remaining=2,
    )
    tied = RetreatEnergyProviderContext(
        own_prizes_remaining=2, opponent_prizes_remaining=2,
    )

    # An eligible Counter Energy providing 2 in its cache cannot justify
    # cost 2 until Prize state is known.
    counter = actor("Counter Energy", "sm4-100", 2)
    undecidable = attempt(counter, 2, ("conditional",))
    assert undecidable.unresolved_selected_provider_ids == ("conditional",)
    assert undecidable.transaction is None
    assert attempt(counter, 2, ("conditional",), context=behind).transaction is not None
    assert attempt(counter, 2, ("conditional",), context=tied).transaction is None

    # Even with unknown Prizes, one Counter Energy always pays cost 1.
    safe = attempt(counter, 1, ("conditional",))
    assert safe.unresolved_selected_provider_ids == ()
    assert safe.transaction is not None and safe.transaction.committed
    assert retreat_with_dynamic_energy_units(
        counter, "pivot", retreat_cost=2,
        discard_energy_ids=("conditional",),
    ) is None

    # Counter Energy attached to GX is always 1; normalize this even when
    # relative Prize counts are unavailable.
    counter_gx = actor(
        "Counter Energy", "sm4-100", 2,
        tags=("Stage1", "Pokemon-GX", "RuleBox"),
    )
    gx = attempt(counter_gx, 2, ("conditional",))
    assert gx.unresolved_selected_provider_ids == ()
    assert gx.normalization.state.energy.board.get("holder").energy[0].units == ("C",)
    assert gx.transaction is None
    assert attempt(counter_gx, 1, ("conditional",)).transaction is not None

    reversal = actor(
        "Reversal Energy", "sv2-192", 3, tags=("Stage1",),
    )
    uncertain_reversal = attempt(reversal, 3, ("conditional",))
    assert uncertain_reversal.unresolved_selected_provider_ids == ("conditional",)
    assert uncertain_reversal.transaction is None
    assert attempt(reversal, 3, ("conditional",), context=behind).transaction is not None
    assert attempt(reversal, 3, ("conditional",), context=tied).transaction is None
    assert attempt(reversal, 1, ("conditional",)).transaction is not None

    reversal_rulebox = actor(
        "Reversal Energy", "sv2-192", 3, tags=("Stage1", "RuleBox"),
    )
    restricted = attempt(reversal_rulebox, 3, ("conditional",))
    assert restricted.unresolved_selected_provider_ids == ()
    assert restricted.normalization.state.energy.board.get("holder").energy[0].units == ("C",)
    assert restricted.transaction is None

    # Unselected uncertain Energy does not affect a physical DCE payment.
    mixed = actor("Counter Energy", "sm4-100", 2, dce=True)
    dce_only = attempt(mixed, 2, ("dce",))
    assert dce_only.unresolved_selected_provider_ids == ()
    assert dce_only.transaction is not None and dce_only.transaction.committed

    # Both cards together always supply >= 3, but only conditionally supply 4.
    guaranteed = attempt(mixed, 3, ("conditional", "dce"))
    assert guaranteed.unresolved_selected_provider_ids == ()
    assert guaranteed.transaction is not None and guaranteed.transaction.committed
    contingent = attempt(mixed, 4, ("conditional", "dce"))
    assert contingent.unresolved_selected_provider_ids == ("conditional",)
    assert contingent.transaction is None
    assert attempt(mixed, 4, ("conditional", "dce"), context=behind).transaction is not None
    assert attempt(mixed, 4, ("conditional", "dce"), context=tied).transaction is None

    print("Prize-dependent Retreat payment bounds: PASS")
    print("Counter/DCE cost 3 guaranteed; cost 4 contingent on Prize state")


if __name__ == "__main__":
    main()
