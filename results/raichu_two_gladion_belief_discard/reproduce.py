"""Two-Gladion belief-weighted discard safety for Harto Miki Raichu/Electrode.

The current hand contains one visible Gladion. Alolan Raichu and the second
Gladion are both among 52 unseen cards, with six Prize cards. The model asks
whether discarding the visible Gladion for Quick Ball preserves at least one
physical continuation to Alolan Raichu in hand in each grouped Prize world.
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
    DiscardCandidate("visible_gladion"),
)

DCI = {
    "discard_a": 0.6,
    "discard_b": 0.9,
    "discard_c": 0.7,
    "visible_gladion": 1.0,
}


def selected_class(selection: DiscardSelection) -> str:
    index = next(
        index
        for index, count in enumerate(selection.counts)
        if count == 1
    )
    return QUICK_CANDIDATES[index].card_class


def belief() -> PrizeBelief:
    return PrizeBelief.from_hypergeometric(
        {
            "raichu": 1,
            "backup_gladion": 1,
        },
        pool_size=52,
        prize_count=6,
    )


def state_for_world(prize_counts) -> ZoneCountState:
    mapping = {
        ("quick_ball", "hand"): 1,
        ("discard_a", "hand"): 1,
        ("discard_b", "hand"): 1,
        ("discard_c", "hand"): 1,
        ("visible_gladion", "hand"): 1,
        ("neutral_a", "hand"): 1,
        ("neutral_b", "hand"): 1,
        ("crobat_v", "deck"): 1,
        ("top_filler", "deck"): 1,
    }
    mapping[
        ("alolan_raichu", "prize" if prize_counts["raichu"] else "deck")
    ] = 1
    mapping[
        (
            "backup_gladion",
            "prize" if prize_counts["backup_gladion"] else "deck",
        )
    ] = 1
    return ZoneCountState.from_mapping(mapping)


def _gladion_rescue(
    zones: ZoneCountState,
    first,
    *,
    gladion_card_class: str,
    gladion_instance_id: str,
):
    ledger = IdentityLedger(zones)
    ledger = materialize(
        ledger,
        card_class=gladion_card_class,
        card_name="Gladion",
        source_zone="hand",
        instance_id=gladion_instance_id,
    )
    ledger = materialize(
        ledger,
        card_class="alolan_raichu",
        card_name="Alolan Raichu",
        source_zone="prize",
        instance_id="prize-raichu",
    )
    prize_ids = ["prize-raichu"]

    if zones.count("backup_gladion", "prize") == 1:
        ledger = materialize(
            ledger,
            card_class="backup_gladion",
            card_name="Gladion",
            source_zone="prize",
            instance_id="prize-backup-gladion",
        )
        prize_ids.append("prize-backup-gladion")

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
        tuple(prize_ids),
        (False,) * len(prize_ids),
    )
    outcomes = execute_gladion_supporter_physical(
        physical,
        first.transaction.after.budget,
        first.transaction.after.channels,
        gladion_instance_id=gladion_instance_id,
        selected_position=0,
    )
    for index, outcome in enumerate(outcomes):
        final_ledger = dematerialize(
            outcome.physical.physical_after.ledger,
            "prize-raichu",
        )
        yield (
            f"gladion_rescue_{index}",
            final_ledger.exchangeable,
        )


def continuation(
    state: ZoneCountState,
    quick_selection: DiscardSelection,
):
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

    if zones.count("visible_gladion", "hand") == 1:
        yield from _gladion_rescue(
            zones,
            first,
            gladion_card_class="visible_gladion",
            gladion_instance_id="visible-gladion-1",
        )
        return

    if zones.count("backup_gladion", "deck") == 1:
        if first.dark_asset_draw_count < 1:
            return
        after_draw = zones.move("backup_gladion", "deck", "hand")
        yield from _gladion_rescue(
            after_draw,
            first,
            gladion_card_class="backup_gladion",
            gladion_instance_id="backup-gladion-1",
        )
        return

    # Both Alolan Raichu and the only remaining Gladion are Prized.
    return


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
    current_belief = belief()
    safety = discard_safety_under_belief(
        current_belief,
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

    both_prized_probability = 0.0
    world_rows = []
    expected_k1_dci = 0.0
    for counts, probability in current_belief.state_dicts():
        classes = safe_classes_for_world(state_for_world(counts))
        both_prized = bool(counts["raichu"] and counts["backup_gladion"])
        if both_prized:
            both_prized_probability += probability
        choice = max(classes, key=lambda card_class: DCI[card_class])
        expected_k1_dci += probability * DCI[choice]
        world_rows.append(
            {
                "raichu_prized": bool(counts["raichu"]),
                "backup_gladion_prized": bool(counts["backup_gladion"]),
                "probability": probability,
                "safe_discards": sorted(classes),
                "best_safe_discard": choice,
            }
        )

    assert abs(both_prized_probability - 0.011312217194570135) < 1e-12
    assert abs(
        safety_by_class["visible_gladion"]
        - (1.0 - both_prized_probability)
    ) < 1e-12
    for card_class in ("discard_a", "discard_b", "discard_c"):
        assert abs(safety_by_class[card_class] - 1.0) < 1e-12

    robust = [
        card_class
        for card_class, probability in safety_by_class.items()
        if abs(probability - 1.0) < 1e-12
    ]
    best_k0 = max(robust, key=lambda card_class: DCI[card_class])
    assert best_k0 == "discard_b"
    assert abs(expected_k1_dci - 0.9988687782805429) < 1e-12

    print(
        json.dumps(
            {
                "both_raichu_and_backup_gladion_prized": both_prized_probability,
                "visible_gladion_discard_safety": safety_by_class[
                    "visible_gladion"
                ],
                "ordinary_discard_safety": {
                    card_class: safety_by_class[card_class]
                    for card_class in ("discard_a", "discard_b", "discard_c")
                },
                "k0_robust_discard": best_k0,
                "k0_robust_dci": DCI[best_k0],
                "k1_expected_safe_dci": expected_k1_dci,
                "information_dci_gain": expected_k1_dci - DCI[best_k0],
                "worlds": world_rows,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
