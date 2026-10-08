"""Regression: Jamming Tower and Stealthy Hood change Retreat action outcomes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_stadium_tool_overlay import JAMMING_TOWER_PRINT_IDS
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor(active, *bench):
    cards = [item for mon in (active, *bench) for item in mon.energy]
    classes = tuple(sorted(
        (energy.instance_id, "class-" + energy.instance_id)
        for energy in cards
    ))
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                (card_class, "attached"): 1 for _, card_class in classes
            }),
            board=make_board(active, bench),
            instance_classes=classes,
        ),
    )


def attempt(our, opponent, *, cost, payment=(), stadium=None, enabled=True):
    return attempt_board_derived_retreat(
        our, "pivot",
        base_retreat_cost=cost,
        discard_energy_ids=payment,
        opponent_board=opponent,
        stadium_print_id=stadium,
        stadium_effect_enabled=enabled,
    )


def main():
    pivot = make_pokemon("pivot", "Pivot")
    empty_opponent = make_board(make_pokemon("opp", "Opp"))

    float_stone = ToolAttachment("float", "Float Stone", "xy8-137")
    free = actor(make_pokemon("active", "Active", tool=float_stone), pivot)
    baseline = attempt(free, empty_opponent, cost=2)
    assert baseline.effective_retreat_cost == 0
    assert baseline.transaction is not None and baseline.transaction.committed

    for tower_print in sorted(JAMMING_TOWER_PRINT_IDS):
        cancelled = attempt(
            free, empty_opponent, cost=2, stadium=tower_print,
        )
        assert cancelled.suppressed_own_tool_ids == ("float",)
        assert cancelled.effective_retreat_cost == 2
        assert cancelled.transaction is None
        assert cancelled.normalization.state.energy.board.get(
            "active"
        ).pokemon_state.tool_effect_enabled
        restored = attempt(
            cancelled.normalization.state,
            empty_opponent,
            cost=2,
        )
        assert restored.effective_retreat_cost == 0
        assert restored.transaction is not None and restored.transaction.committed

        ineffective = attempt(
            free, empty_opponent, cost=2,
            stadium=tower_print, enabled=False,
        )
        assert ineffective.effective_retreat_cost == 0
        assert ineffective.transaction is not None

    dce = EnergyAttachment(
        "dce", "Double Colorless Energy", ("C", "C"), "base1-96",
    )
    pouch = ToolAttachment("pouch", "Dashing Pouch", "sm4-92")
    pouch_state = actor(make_pokemon(
        "active", "Active", energy=(dce,), tool=pouch,
    ), pivot)
    hand = attempt(pouch_state, empty_opponent, cost=2, payment=("dce",))
    assert hand.transaction is not None and hand.transaction.committed
    assert hand.transaction.destinations[0].destination_zone == "hand"
    discarded = attempt(
        pouch_state, empty_opponent, cost=2, payment=("dce",),
        stadium="sv6-153",
    )
    assert discarded.transaction is not None and discarded.transaction.committed
    assert discarded.transaction.destinations[0].destination_zone == "discard"
    assert discarded.suppressed_own_tool_ids == ("pouch",)
    assert discarded.transaction.state.energy.board.get(
        "active"
    ).pokemon_state.tool_effect_enabled
    assert discarded.normalization.state.energy.board.get(
        "active"
    ).pokemon_state.tool_effect_enabled

    # An opposing Tool's increase can also be blanked.
    gravity = ToolAttachment("gravity", "Gravity Gemstone", "sv7-137")
    opponent_tool = make_board(make_pokemon("opp", "Opp", tool=gravity))
    zero = actor(make_pokemon("active", "Active"), pivot)
    increased = attempt(zero, opponent_tool, cost=0)
    assert increased.effective_retreat_cost == 1
    assert increased.transaction is None
    negated = attempt(zero, opponent_tool, cost=0, stadium="sv6-153")
    assert negated.effective_retreat_cost == 0
    assert negated.suppressed_opponent_tool_ids == ("gravity",)
    assert negated.transaction is not None and negated.transaction.committed

    # Opponent Snorlax: Hood protects its holder from the opponent's Ability.
    snorlax = make_board(make_pokemon(
        "snorlax", "Snorlax", print_id="pgo-55", tags=("Basic",),
    ))
    hood = ToolAttachment("hood", "Stealthy Hood", "sm10-186")
    hood_state = actor(make_pokemon(
        "active", "Active", energy=(dce,), tool=hood,
    ), pivot)
    protected = attempt(
        hood_state, snorlax, cost=2, payment=("dce",),
    )
    assert protected.retreat_denial_source_ids == ()
    assert protected.transaction is not None and protected.transaction.committed
    tower_blocks = attempt(
        hood_state, snorlax, cost=2, payment=("dce",),
        stadium="sv6-153",
    )
    assert tower_blocks.suppressed_own_tool_ids == ("hood",)
    assert tower_blocks.retreat_denial_source_ids == ("snorlax",)
    assert tower_blocks.transaction is None

    # Suppressing the Tool explicitly is equivalent to active Jamming Tower.
    pre_suppressed = actor(make_pokemon(
        "active", "Active", energy=(dce,), tool=hood,
        tool_effect_enabled=False,
    ), pivot)
    assert attempt(
        pre_suppressed, snorlax, cost=2, payment=("dce",),
    ).retreat_denial_source_ids == ("snorlax",)

    print("Retreat Jamming Tower / Stealthy Hood: PASS")
    print("Jamming Tower prints tested:", len(JAMMING_TOWER_PRINT_IDS))
    print("Dashing Pouch route changes hand -> discard")


if __name__ == "__main__":
    main()
