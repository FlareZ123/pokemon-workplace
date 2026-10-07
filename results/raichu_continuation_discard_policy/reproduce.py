"""Continuation-aware Quick Ball discard policy on the full Raichu rescue line."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchState
from continuation_discard_policy import (
    continuation_feasible_discards,
    feasible_selections,
    rank_continuation_discards,
)
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_full_prized_rescue_execution import execute_full_prized_raichu_rescue
from trainer_search_transaction import TrainerSearchExecutionState


QUICK_CANDIDATES = (
    DiscardCandidate("discard_a"),
    DiscardCandidate("discard_b"),
    DiscardCandidate("discard_c"),
    DiscardCandidate("future_piece"),
)

COMPUTER_CANDIDATES = (
    DiscardCandidate("discard_a"),
    DiscardCandidate("discard_b"),
    DiscardCandidate("discard_c"),
    DiscardCandidate("future_piece", max_copies=0),
)


def initial_state() -> ZoneCountState:
    return ZoneCountState.from_mapping(
        {
            ("quick_ball", "hand"): 1,
            ("discard_a", "hand"): 1,
            ("discard_b", "hand"): 1,
            ("discard_c", "hand"): 1,
            ("future_piece", "hand"): 1,
            ("neutral_a", "hand"): 1,
            ("neutral_b", "hand"): 1,
            ("crobat_v", "deck"): 1,
            ("computer_search", "deck"): 1,
            ("gladion", "deck"): 1,
            ("filler", "deck"): 1,
            ("alolan_raichu", "prize"): 1,
        }
    )


def computer_payment_after_quick(selection: DiscardSelection) -> DiscardSelection:
    discarded_index = next(
        index for index, count in enumerate(selection.counts) if count == 1
    )
    available = [
        index
        for index in range(3)
        if index != discarded_index
    ]
    if len(available) < 2:
        # If future_piece was discarded, all three dedicated cards remain.
        available = [0, 1, 2]
    chosen = set(available[:2])
    return DiscardSelection(
        tuple(
            1 if index in chosen else 0
            for index in range(len(COMPUTER_CANDIDATES))
        )
    )


def continuation(
    state: ZoneCountState,
    quick_selection: DiscardSelection,
):
    computer_selection = computer_payment_after_quick(quick_selection)
    result = execute_full_prized_raichu_rescue(
        TrainerSearchExecutionState(zones=state),
        BenchState(),
        quick_discard_candidates=QUICK_CANDIDATES,
        quick_discard_selection=quick_selection,
        computer_discard_candidates=COMPUTER_CANDIDATES,
        computer_discard_selection=computer_selection,
    )
    for index, outcome in enumerate(result.gladion_outcomes):
        yield (
            f"full_rescue_{index}",
            outcome.physical.physical_after.ledger.exchangeable,
        )


def selected_class(selection: DiscardSelection) -> str:
    index = next(
        index for index, count in enumerate(selection.counts) if count == 1
    )
    return QUICK_CANDIDATES[index].card_class


def main() -> None:
    state = initial_state()
    witnesses = continuation_feasible_discards(
        state,
        QUICK_CANDIDATES,
        1,
        continuation,
        {"future_piece": 1},
        endpoint_zone="hand",
    )
    selections = feasible_selections(witnesses)
    classes = tuple(selected_class(selection) for selection in selections)

    assert classes == ("discard_c", "discard_b", "discard_a") or set(classes) == {
        "discard_a",
        "discard_b",
        "discard_c",
    }
    assert "future_piece" not in classes
    assert len(selections) == 3

    ranked = rank_continuation_discards(
        witnesses,
        QUICK_CANDIDATES,
        {
            "discard_a": 0.6,
            "discard_b": 0.9,
            "discard_c": 0.7,
            "future_piece": 1.0,
        },
    )
    assert selected_class(ranked[0].witness.selection) == "discard_b"

    mechanical_future = DiscardSelection((0, 0, 0, 1))
    all_mechanical = {
        selection
        for selection in (
            DiscardSelection((1, 0, 0, 0)),
            DiscardSelection((0, 1, 0, 0)),
            DiscardSelection((0, 0, 1, 0)),
            mechanical_future,
        )
    }
    assert mechanical_future in all_mechanical
    assert mechanical_future not in set(selections)

    print(
        json.dumps(
            {
                "mechanical_quick_ball_discards": 4,
                "continuation_safe_discards": sorted(classes),
                "filtered_future_piece_discard": True,
                "future_piece_raw_dci_score": 1.0,
                "best_safe_discard": selected_class(
                    ranked[0].witness.selection
                ),
                "best_safe_dci_score": ranked[0].desirability,
                "full_rescue_and_future_piece_endpoint_preserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
