"""Dashing Pouch Retreat overpayment can fund a same-turn Ultra Ball.

Uses exact physical Retreat and canonical Item-search transactions against
the same zone ledger.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    EnergyAttachment, ToolAttachment, make_board, make_pokemon,
)
from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from energy_board_conservation import EnergyBoardState
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_energy_transaction import RetreatEnergyTransactionState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import CompiledTrainerSearchProfile, SearchOutput
from trainer_search_transaction import (
    TrainerSearchExecutionState, execute_trainer_retrieval_transaction,
)
from turn_action_budget import TurnActionBudget
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import BASIC_POKEMON, TargetGroup
from unified_state_kernel import make_state


ENERGY_CLASSES = ("energy_basic", "energy_dce")
SEARCH_PROFILE = CompiledTrainerSearchProfile(
    card_id="swsh9-150", name="Ultra Ball", action_class="Item",
    base_outputs=(SearchOutput("Pokémon", 1),),
    required_discard_other_cards=2,
)
TARGETS = (
    SearchZoneTarget(
        "target_pokemon",
        TargetGroup("Basic search target", 1, frozenset({BASIC_POKEMON})),
    ),
)
RETRIEVAL = next(
    action for action in enumerate_typed_retrieval_actions(
        SEARCH_PROFILE.base_outputs, tuple(t.group for t in TARGETS)
    )
    if action.target_cost == (1,)
)
DISCARD_CANDIDATES = tuple(DiscardCandidate(name) for name in ENERGY_CLASSES)


def build_actor(*, spare_hand: int = 0):
    energies = (
        EnergyAttachment("dce", "Double Colorless Energy", ("C", "C"), "bw4-92"),
        EnergyAttachment("basic", "Basic Psychic Energy", ("P",)),
    )
    holder = make_pokemon(
        "active", "Stage 1 holder", tags=("Stage1",), energy=energies,
        damage_counters=1, tool=ToolAttachment("pouch", "Dashing Pouch", "sm4-92"),
    )
    zones = {
        ("energy_dce", "attached"): 1,
        ("energy_basic", "attached"): 1,
        ("ultra_ball", "hand"): 1,
        ("target_pokemon", "deck"): 1,
    }
    if spare_hand:
        zones[("spare_fodder", "hand")] = spare_hand
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping(zones),
            board=make_board(holder, (make_pokemon("pivot", "Pivot"),)),
            instance_classes=(("basic", "energy_basic"), ("dce", "energy_dce")),
        ),
    )


def run_scenario(
    *, spare_hand: int = 0, blocker: bool = False,
    jamming_tower: bool = False, item_locked: bool = False,
):
    actor = build_actor(spare_hand=spare_hand)
    opponent = make_board(
        make_pokemon("opponent", "Opponent"),
        (make_pokemon("mime", "Mr. Mime", print_id="sm9-66"),)
        if blocker else (),
    )
    enumeration = enumerate_board_derived_retreat_actions(
        actor, opponent,
        base_retreat_cost=2,
        stadium_print_id="sv6-153" if jamming_tower else None,
    )
    assert len(enumeration.actions) == 2
    results = {}
    for action in enumeration.actions:
        payment = tuple(sorted(action.discard_energy_ids))
        transaction = action.attempt.transaction
        assert transaction is not None and transaction.committed
        after = transaction.state
        initial_zones = actor.energy.zones
        zones = after.energy.zones
        for card_class in ("ultra_ball", "target_pokemon", *ENERGY_CLASSES):
            assert zones.total(card_class) == initial_zones.total(card_class)
        assert after.unified.turn_budget is not None
        assert after.unified.turn_budget.retreat_used
        assert not after.unified.turn_budget.supporter_used

        candidates = DISCARD_CANDIDATES + (
            (DiscardCandidate("spare_fodder"),) if spare_hand else ()
        )
        choices = enumerate_discard_selections(zones, candidates, 2)
        viable = []
        for choice in choices:
            if item_locked:
                try:
                    execute_trainer_retrieval_transaction(
                        TrainerSearchExecutionState(
                            zones=zones,
                            budget=after.unified.turn_budget,
                            channels=PlayerChannels(item_play=False),
                        ),
                        profile=SEARCH_PROFILE,
                        action_card_class="ultra_ball",
                        targets=TARGETS,
                        retrieval_action=RETRIEVAL,
                        discard_candidates=candidates,
                        discard_selection=choice,
                    )
                except ValueError as error:
                    assert "Item play is locked" in str(error)
                else:
                    raise AssertionError("locked Item unexpectedly played")
                continue

            played = execute_trainer_retrieval_transaction(
                TrainerSearchExecutionState(
                    zones=zones,
                    budget=after.unified.turn_budget,
                ),
                profile=SEARCH_PROFILE,
                action_card_class="ultra_ball",
                targets=TARGETS,
                retrieval_action=RETRIEVAL,
                discard_candidates=candidates,
                discard_selection=choice,
            )
            assert played.after.zones.count("target_pokemon", "hand") == 1
            assert played.after.zones.count("ultra_ball", "discard") == 1
            assert played.after.budget.retreat_used
            assert not played.after.budget.supporter_used
            for card_class in ("ultra_ball", "target_pokemon", *ENERGY_CLASSES):
                assert played.after.zones.total(card_class) == initial_zones.total(card_class)
            viable.append(played)
        results[payment] = {
            "hand_energy": sum(zones.count(card, "hand") for card in ENERGY_CLASSES),
            "search_feasible": bool(viable),
            "payment_options": len(choices),
            "energy_destinations": {
                d.instance_id: d.destination_zone for d in transaction.destinations
            },
        }
    return results


def main():
    plain = run_scenario()
    assert plain == {
        ("dce",): {
            "hand_energy": 1, "search_feasible": False, "payment_options": 0,
            "energy_destinations": {"dce": "hand"},
        },
        ("basic", "dce"): {
            "hand_energy": 2, "search_feasible": True, "payment_options": 1,
            "energy_destinations": {"dce": "hand", "basic": "hand"},
        },
    }

    for blocked in (run_scenario(blocker=True), run_scenario(jamming_tower=True)):
        assert not any(r["search_feasible"] for r in blocked.values())
        assert all(r["hand_energy"] == 0 for r in blocked.values())
        assert all(
            set(r["energy_destinations"].values()) == {"discard"}
            for r in blocked.values()
        )

    locked = run_scenario(item_locked=True)
    assert not any(r["search_feasible"] for r in locked.values())
    assert locked[("basic", "dce")]["payment_options"] == 1

    with_spare = run_scenario(spare_hand=1)
    assert all(r["search_feasible"] for r in with_spare.values())
    print("Dashing Pouch -> Ultra Ball physical payment bridge: PASS")
    print(plain)
    print("Scoop-Up Block, Jamming Tower, Item lock suppress the search")
    print("One spare hand discard target restores the minimal-payment search")


if __name__ == "__main__":
    main()
