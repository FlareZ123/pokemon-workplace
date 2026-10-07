"""Reproduce target-Prized Quick -> Dark Asset -> Computer Search -> Gladion."""

from __future__ import annotations

import json
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_dark_asset_computer_followup_execution import (
    GLADION_GROUP,
    RAICHU_GROUP,
    execute_quick_dark_asset_computer_gladion,
)
from trainer_search_transaction import TrainerSearchExecutionState


def state_with_disposables(count: int) -> TrainerSearchExecutionState:
    mapping = {
        ("quick_ball", "hand"): 1,
        ("protected_a", "hand"): 1,
        ("protected_b", "hand"): 1,
        ("protected_c", "hand"): 1,
        ("crobat_v", "deck"): 1,
        ("computer_search", "deck"): 1,
        ("gladion", "deck"): 1,
        ("filler", "deck"): 1,
        ("alolan_raichu", "prize"): 1,
    }
    for index in range(count):
        mapping[(f"disposable_{index}", "hand")] = 1
    hand_size = 4 + count
    for index in range(7 - hand_size):
        mapping[(f"neutral_{index}", "hand")] = 1
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(mapping)
    )


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    state = state_with_disposables(3)
    quick_candidates = (
        DiscardCandidate("disposable_0"),
        DiscardCandidate("disposable_1"),
        DiscardCandidate("disposable_2"),
    )
    computer_candidates = quick_candidates + (
        DiscardCandidate("protected_a", max_copies=0),
        DiscardCandidate("protected_b", max_copies=0),
        DiscardCandidate("protected_c", max_copies=0),
    )

    result = execute_quick_dark_asset_computer_gladion(
        state,
        BenchState(),
        quick_discard_candidates=quick_candidates,
        quick_discard_selection=DiscardSelection((1, 0, 0)),
        computer_discard_candidates=computer_candidates,
        computer_discard_selection=DiscardSelection((0, 1, 1, 0, 0, 0)),
    )

    assert result.first.hand_size_after_bench == 5
    assert result.first.dark_asset_draw_count == 1
    assert result.after_dark_asset_draw.zones.count("computer_search", "hand") == 1

    tx = result.computer
    assert tx.after.zones.count("computer_search", "discard") == 1
    assert tx.after.zones.count("disposable_1", "discard") == 1
    assert tx.after.zones.count("disposable_2", "discard") == 1
    assert tx.physical_after.ledger.instance("private-gladion").zone == "hand"
    assert tx.physical_after.ledger.instance("prize-raichu").zone == "prize"
    assert tx.physical_after.ledger.instance("top-filler").zone == "deck_top"

    actor = tx.beliefs_after.belief_for("actor")
    observer = tx.beliefs_after.belief_for("observer")
    assert isclose(actor.prize_probability_at(0, RAICHU_GROUP), 1.0, abs_tol=1e-12)
    assert isclose(actor.prize_probability_at(0, GLADION_GROUP), 0.0, abs_tol=1e-12)

    # The observer knows the policy but not which target was privately taken.
    assert 0.0 < observer.prize_probability_at(0, RAICHU_GROUP) < 1.0

    for protected in ("protected_a", "protected_b", "protected_c"):
        assert tx.after.zones.count(protected, "hand") == 1

    assert tx.physical_before.ledger.totals() == tx.physical_after.ledger.totals()

    two_disposable = state_with_disposables(2)
    two_candidates = (
        DiscardCandidate("disposable_0"),
        DiscardCandidate("disposable_1"),
    )
    residual_gate_rejected = expect_value_error(
        lambda: execute_quick_dark_asset_computer_gladion(
            two_disposable,
            BenchState(),
            quick_discard_candidates=two_candidates,
            quick_discard_selection=DiscardSelection((1, 0)),
            computer_discard_candidates=two_candidates + (
                DiscardCandidate("protected_a", max_copies=0),
                DiscardCandidate("protected_b", max_copies=0),
                DiscardCandidate("protected_c", max_copies=0),
            ),
            computer_discard_selection=DiscardSelection((0, 1, 0, 0, 0)),
        )
    )
    assert residual_gate_rejected

    print(
        json.dumps(
            {
                "raichu_physically_prized": True,
                "quick_post_bench_hand": result.first.hand_size_after_bench,
                "dark_asset_exact_draw": "Computer Search",
                "computer_search_exact_cost": 2,
                "computer_search_private_target": "Gladion",
                "actor_k1_raichu_prized_probability": actor.prize_probability_at(
                    0, RAICHU_GROUP
                ),
                "observer_remains_uncertain": (
                    0.0 < observer.prize_probability_at(0, RAICHU_GROUP) < 1.0
                ),
                "gladion_reached_hand": (
                    tx.physical_after.ledger.instance("private-gladion").zone == "hand"
                ),
                "two_initial_disposables_fail_residual_gate": residual_gate_rejected,
                "physical_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
