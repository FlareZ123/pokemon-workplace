"""Belief-weighted Quick Ball discard safety for Harto Miki Raichu/Electrode.

This regression composes the generic belief-weighted discard policy with
physical Quick Ball -> Crobat V execution and literal Gladion Prize rescue.
The two physical worlds differ only in whether Alolan Raichu is in deck or
Prizes. World weights use the six-Prize posterior after the singleton has not
appeared among eight observed opening/draw cards: P(Prized)=6/52.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from belief_weighted_discard_policy import discard_safety_under_belief
from bench_state_kernel import BenchState
from continuation_discard_policy import (
    continuation_feasible_discards,
    feasible_selections,
)
from discard_cost_witness import DiscardCandidate, DiscardSelection
from gladion_supporter_physical_transaction import execute_gladion_supporter_physical
from identity_materialization import (
    IdentityLedger,
    dematerialize,
    materialize,
    move_instance,
)
from multicopy_zone_state import ZoneCountState
from prize_belief_kernel import PrizeBelief
from raichu_search_to_crobat_execution import execute_search_to_crobat
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_transaction import TrainerSearchExecutionState


QUICK_CANDIDATES = (
    DiscardCandidate("discard_a"),
    DiscardCandidate("discard_b"),
    DiscardCandidate("discard_c"),
    DiscardCandidate("gladion"),
)

DCI = {
    "discard_a": 0.6,
    "discard_b": 0.9,
    "discard_c": 0.7,
    "gladion": 1.0,
}


def selected_class(selection: DiscardSelection) -> str:
    index = next(
        index
        for index, count in enumerate(selection.counts)
        if count == 1
    )
    return QUICK_CANDIDATES[index].card_class


def binary_target_zone_belief() -> PrizeBelief:
    """Binary target-zone posterior carried by one representative Prize slot."""

    target_prized = 6.0 / 52.0
    return PrizeBelief(
        ("raichu",),
        1,
        (
            ((0,), 1.0 - target_prized),
            ((1,), target_prized),
        ),
    )


def state_for_world(prize_counts) -> ZoneCountState:
    """Instantiate one conserved representative for the target's zone."""

    target_prized = prize_counts["raichu"] == 1
    mapping = {
        ("quick_ball", "hand"): 1,
        ("discard_a", "hand"): 1,
        ("discard_b", "hand"): 1,
        ("discard_c", "hand"): 1,
        ("gladion", "hand"): 1,
        ("neutral_a", "hand"): 1,
        ("neutral_b", "hand"): 1,
        ("crobat_v", "deck"): 1,
        ("top_filler", "deck"): 1,
    }
    if target_prized:
        mapping[("alolan_raichu", "prize")] = 1
        mapping[("zone_filler", "deck")] = 1
    else:
        mapping[("alolan_raichu", "deck")] = 1
        mapping[("zone_filler", "prize")] = 1
    return ZoneCountState.from_mapping(mapping)


def continuation(
    state: ZoneCountState,
    quick_selection: DiscardSelection,
):
    """Execute the zone-dependent continuation after one exact Quick Ball discard."""

    first = execute_search_to_crobat(
        TrainerSearchExecutionState(zones=state),
        BenchState(),
        action_card_class="quick_ball",
        discard_candidates=QUICK_CANDIDATES,
        discard_selection=quick_selection,
    )
    if not first.crobat_benched:
        return

    zones = first.zones_after_bench

    if zones.count("alolan_raichu", "deck") == 1:
        if first.dark_asset_draw_count < 1:
            return
        yield (
            "target_in_deck_dark_asset_hit",
            zones.move("alolan_raichu", "deck", "hand"),
        )
        return

    if zones.count("alolan_raichu", "prize") != 1:
        raise AssertionError("representative world lost Alolan Raichu")

    # If Quick Ball discarded Gladion, the target-Prized continuation is gone.
    if zones.count("gladion", "hand") != 1:
        return

    ledger = IdentityLedger(zones)
    ledger = materialize(
        ledger,
        card_class="gladion",
        card_name="Gladion",
        source_zone="hand",
        instance_id="gladion-1",
    )
    ledger = materialize(
        ledger,
        card_class="alolan_raichu",
        card_name="Alolan Raichu",
        source_zone="prize",
        instance_id="prize-raichu",
    )
    ledger = materialize(
        ledger,
        card_class="top_filler",
        card_name="Top filler",
        source_zone="deck",
        instance_id="top-1",
    )
    ledger = move_instance(ledger, "top-1", "deck_top")
    physical = TopPrizePhysicalState(
        ledger,
        "top-1",
        ("prize-raichu",),
        (False,),
    )

    outcomes = execute_gladion_supporter_physical(
        physical,
        first.transaction.after.budget,
        first.transaction.after.channels,
        gladion_instance_id="gladion-1",
        selected_position=0,
    )
    for index, outcome in enumerate(outcomes):
        final_ledger = dematerialize(
            outcome.physical.physical_after.ledger,
            "prize-raichu",
        )
        yield (
            f"target_prized_gladion_rescue_{index}",
            final_ledger.exchangeable,
        )


def safe_classes_for_world(state: ZoneCountState) -> set[str]:
    witnesses = continuation_feasible_discards(
        state,
        QUICK_CANDIDATES,
        1,
        continuation,
        {"alolan_raichu": 1},
        endpoint_zone="hand",
    )
    return {
        selected_class(selection)
        for selection in feasible_selections(witnesses)
    }


def main() -> None:
    belief = binary_target_zone_belief()
    safety = discard_safety_under_belief(
        belief,
        state_for_world,
        QUICK_CANDIDATES,
        1,
        continuation,
        {"alolan_raichu": 1},
        endpoint_zone="hand",
    )
    safety_by_class = {
        selected_class(row.selection): row.safety_probability
        for row in safety
    }

    target_in_deck = 46.0 / 52.0
    target_prized = 6.0 / 52.0
    assert abs(safety_by_class["gladion"] - target_in_deck) < 1e-12
    for card_class in ("discard_a", "discard_b", "discard_c"):
        assert abs(safety_by_class[card_class] - 1.0) < 1e-12

    safe_by_world = {}
    for counts, probability in belief.state_dicts():
        label = "target_prized" if counts["raichu"] else "target_in_deck"
        classes = safe_classes_for_world(state_for_world(counts))
        safe_by_world[label] = (classes, probability)

    assert safe_by_world["target_in_deck"][0] == {
        "discard_a",
        "discard_b",
        "discard_c",
        "gladion",
    }
    assert safe_by_world["target_prized"][0] == {
        "discard_a",
        "discard_b",
        "discard_c",
    }

    robust = [
        card_class
        for card_class, probability in safety_by_class.items()
        if abs(probability - 1.0) < 1e-12
    ]
    best_k0 = max(robust, key=lambda card_class: DCI[card_class])
    assert best_k0 == "discard_b"

    k1_choice = {}
    expected_k1_dci = 0.0
    for label, (classes, probability) in safe_by_world.items():
        choice = max(classes, key=lambda card_class: DCI[card_class])
        k1_choice[label] = choice
        expected_k1_dci += probability * DCI[choice]

    assert k1_choice == {
        "target_in_deck": "gladion",
        "target_prized": "discard_b",
    }
    assert abs(expected_k1_dci - (46.0 + 6.0 * 0.9) / 52.0) < 1e-12

    print(
        json.dumps(
            {
                "posterior_target_in_deck": target_in_deck,
                "posterior_target_prized": target_prized,
                "discard_safety": safety_by_class,
                "k0_robust_discard": best_k0,
                "k0_robust_dci": DCI[best_k0],
                "k1_discard_by_world": k1_choice,
                "k1_expected_safe_dci": expected_k1_dci,
                "information_dci_gain": expected_k1_dci - DCI[best_k0],
                "gladion_discard_endpoint_failure_risk_k0": target_prized,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
