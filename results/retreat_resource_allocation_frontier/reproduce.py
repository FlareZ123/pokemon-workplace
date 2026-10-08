"""Physical Retreat overpayment is strategically non-dominated by minimality."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    EnergyAttachment, ToolAttachment, make_board, make_pokemon,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def build_actor():
    energies = (
        EnergyAttachment("dce", "Double Colorless Energy", ("C", "C"), "bw4-92"),
        EnergyAttachment("basic", "Basic Psychic Energy", ("P",)),
    )
    active = make_pokemon(
        "active", "Holder", tags=("Stage1",),
        energy=energies, damage_counters=1,
        tool=ToolAttachment("pouch", "Dashing Pouch", "sm4-92"),
    )
    pivot = make_pokemon("pivot", "Pivot")
    classes = tuple(sorted(
        (card.instance_id, "class-" + card.instance_id)
        for card in energies
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


def enumerate_scenario(opponent_board, *, stadium=None):
    return enumerate_board_derived_retreat_actions(
        build_actor(), opponent_board,
        base_retreat_cost=2, stadium_print_id=stadium,
    )


def snapshots(actions):
    """Map physical payment to (destination map, residual holder Energy)."""
    results = {}
    for action in actions:
        transaction = action.attempt.transaction
        assert transaction is not None and transaction.committed
        payment = tuple(sorted(action.discard_energy_ids))
        destinations = {
            dest.instance_id: dest.destination_zone
            for dest in transaction.destinations
        }
        residual = {
            item.instance_id
            for item in transaction.state.energy.board.get("active").energy
        }
        assert residual == {"basic", "dce"} - set(payment)
        assert transaction.state.unified.turn_budget is not None
        assert transaction.state.unified.turn_budget.retreat_used
        results[payment] = destinations, residual
    return results


def main():
    blank = make_board(make_pokemon("opp", "Opponent"))
    normal = enumerate_scenario(blank)
    assert normal.information_complete
    # DCE alone, DCE+Basic, or two? Basic alone cannot cover cost 2.
    assert normal.checked_candidate_count == 2
    assert len(normal.actions) == 2
    result = snapshots(normal.actions)
    assert result == {
        ("dce",): ({"dce": "hand"}, {"basic"}),
        ("basic", "dce"): (
            {"dce": "hand", "basic": "hand"}, set()
        ),
    }

    # Both outcomes conserve the same physical cards but trade off Energy
    # returned to hand versus still attached to the retreated attacker.
    one = normal.actions[0].attempt.transaction
    assert one is not None
    for action in normal.actions:
        after = action.attempt.transaction
        assert after is not None
        for energy in ("basic", "dce"):
            card_class = "class-" + energy
            assert sum(
                after.state.energy.zones.count(card_class, zone)
                for zone in ("attached", "hand", "discard", "lost_zone")
            ) == 1

    mime = make_board(
        make_pokemon("opp", "Opponent"),
        (make_pokemon("mime", "Mr. Mime", print_id="sm9-66"),),
    )
    with_mime = enumerate_scenario(mime)
    assert with_mime.information_complete
    assert len(with_mime.actions) == 2
    blocked_hand = snapshots(with_mime.actions)
    assert blocked_hand == {
        ("dce",): ({"dce": "discard"}, {"basic"}),
        ("basic", "dce"): (
            {"dce": "discard", "basic": "discard"}, set()
        ),
    }
    assert all(
        action.attempt.scoop_up_block_source_ids == ("mime",)
        for action in with_mime.actions
    )

    # Jamming Tower removes Dashing Pouch's return-to-hand effect,
    # while leaving the Tool physically attached for later states.
    tower = enumerate_scenario(blank, stadium="sv6-153")
    assert len(tower.actions) == 2
    assert snapshots(tower.actions) == blocked_hand
    for action in tower.actions:
        transaction = action.attempt.transaction
        assert transaction is not None
        outgoing = transaction.state.energy.board.get("active")
        assert outgoing.tool is not None
        assert outgoing.tool.card_name == "Dashing Pouch"
        assert outgoing.pokemon_state.tool_effect_enabled

    # The four physically distinct post-Retreat states under two opponent
    # regimes cannot be collapsed to the lowest card-discard count.
    print("Retreat resource-allocation frontier: PASS")
    print("unblocked payment choices:", sorted(result))
    print("one paid DCE: 1 Energy card in hand, 1 still attached")
    print("two paid cards: 2 Energy cards in hand, none still attached")
    print("Scoop-Up Block / Jamming Tower remove the hand route")


if __name__ == "__main__":
    main()
