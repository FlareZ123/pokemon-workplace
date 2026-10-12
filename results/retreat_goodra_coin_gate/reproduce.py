"""Deterministic exhaustive branch checks for Goodra's Slimy Sliding."""
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    EnergyAttachment, ToolAttachment, make_board, make_pokemon, switch_active,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_goodra_coin_gate import (
    GOODRA_SLIMY_SLIDING_PRINT_IDS, normal_retreat_goodra_outcomes,
    opponent_slimy_sliding_sources,
)
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def board_with_goodra(*, count=1, enabled=True, wrong_print=False):
    sources = tuple(
        make_pokemon(
            f"goodra{i}", "Goodra",
            print_id="unknown" if wrong_print else "me4-68",
            abilities_enabled=enabled, tags=("Stage2",),
        )
        for i in range(count)
    )
    return make_board(
        make_pokemon("opponent", "Opponent"),
        sources,
    )


def initial_state(*, with_energy=True, pouch=True):
    energy = (
        (EnergyAttachment("e1", "Basic Psychic Energy", ("P",)),)
        if with_energy else ()
    )
    tool = ToolAttachment("pouch", "Dashing Pouch") if pouch else None
    active = make_pokemon(
        "active", "Active Pokemon", energy=energy, tool=tool,
    )
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping(
                {("basic", "attached"): 1} if with_energy else {}
            ),
            board=make_board(
                active, (make_pokemon("pivot", "Pivot"),),
            ),
            instance_classes=(("e1", "basic"),) if with_energy else (),
        ),
    )


def first_retreat(state, opponent, base_retreat_cost):
    options = enumerate_board_derived_retreat_actions(
        state, opponent, base_retreat_cost=base_retreat_cost,
    )
    assert len(options.actions) == 1
    return options.actions[0]


def assert_same_zones(left, right):
    assert left.energy.zones == right.energy.zones
    assert left.energy.instance_classes == right.energy.instance_classes


def validate_sources() -> None:
    records = json.loads(
        (ROOT / "resources" / "cards" / "en" / "me4.json")
        .read_text(encoding="utf-8")
    )
    if isinstance(records, dict):
        records = records.get("data", [])
    source = next(card for card in records if card["id"] == "me4-68")
    assert source["name"] == "Goodra"
    abilities = source.get("abilities") or ()
    assert any(
        ability["name"] == "Slimy Sliding"
        and "doesn't stack" in ability["text"]
        and "Energy for its Retreat Cost is not discarded" in ability["text"]
        for ability in abilities
    )
    assert GOODRA_SLIMY_SLIDING_PRINT_IDS == {"me4-68"}
    assert len(opponent_slimy_sliding_sources(board_with_goodra(count=2))) == 2
    assert opponent_slimy_sliding_sources(
        board_with_goodra(enabled=False)
    ) == ()
    assert opponent_slimy_sliding_sources(
        board_with_goodra(wrong_print=True)
    ) == ()


def dashing_pouch_retreat_branches() -> None:
    state = initial_state()
    enemy = board_with_goodra(count=2)
    action = first_retreat(state, enemy, 1)
    branches = normal_retreat_goodra_outcomes(state, enemy, action)
    assert len(branches) == 2
    heads, tails = branches
    assert (heads.label, tails.label) == ("heads", "tails")
    assert heads.probability == tails.probability == Fraction(1, 2)
    assert heads.retreated and not tails.retreated
    assert heads.source_ids == tails.source_ids == ("goodra0", "goodra1")

    # Heads: ordinary physical Retreat; Dashing Pouch returns the paid Energy.
    assert heads.state.energy.board.active_id == "pivot"
    assert heads.state.energy.zones.count("basic", "hand") == 1
    assert heads.state.energy.zones.count("basic", "attached") == 0

    # Tails: no retreat, no discard, no Dashing Pouch return; quota is spent.
    assert tails.state.energy.board.active_id == "active"
    assert tails.state.energy.board.get("active").tool is not None
    assert tails.state.energy.board.get("active").energy == (
        state.energy.board.get("active").energy
    )
    assert_same_zones(state, tails.state)
    assert tails.state.unified.turn_budget is not None
    assert tails.state.unified.turn_budget.retreat_used
    assert not tails.state.unified.turn_budget.can(TurnAction.RETREAT)
    assert tails.state.energy.board.retreat_used
    assert enumerate_board_derived_retreat_actions(
        tails.state, enemy, base_retreat_cost=1,
    ).actions == ()

    # Tool-based switching uses no ordinary Retreat quota and avoids Goodra.
    switched = switch_active(state.energy.board, "pivot")
    assert switched is not None and switched.active_id == "pivot"
    assert switched.get("active").energy == state.energy.board.get("active").energy


def free_retreat_is_still_coin_gated() -> None:
    state = initial_state(with_energy=False, pouch=False)
    enemy = board_with_goodra()
    action = first_retreat(state, enemy, 0)
    branches = normal_retreat_goodra_outcomes(state, enemy, action)
    assert tuple(x.probability for x in branches) == (
        Fraction(1, 2), Fraction(1, 2),
    )
    assert branches[1].state.energy.board.active_id == "active"
    assert branches[1].state.unified.turn_budget.retreat_used

    disabled = board_with_goodra(enabled=False)
    action = first_retreat(state, disabled, 0)
    unopposed = normal_retreat_goodra_outcomes(state, disabled, action)
    assert len(unopposed) == 1
    assert unopposed[0].probability == Fraction(1)
    assert unopposed[0].retreated


def main() -> None:
    validate_sources()
    dashing_pouch_retreat_branches()
    free_retreat_is_still_coin_gated()
    print("Goodra exact Retreat coin-gate branches: PASS")
    print({"verified_prints": 1, "goodra_copies_tested": 2,
           "heads_fraction": "1/2", "tails_fraction": "1/2",
           "tails_discards_energy": False, "tails_uses_retreat_quota": True})


if __name__ == "__main__":
    main()
