"""Reproduce the full physical singleton Alolan Raichu Prize-rescue line."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_full_prized_rescue_execution import (
    execute_full_prized_raichu_rescue,
)
from trainer_search_transaction import TrainerSearchExecutionState


def base_state() -> TrainerSearchExecutionState:
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("quick_ball", "hand"): 1,
                ("disposable_0", "hand"): 1,
                ("disposable_1", "hand"): 1,
                ("disposable_2", "hand"): 1,
                ("protected_a", "hand"): 1,
                ("protected_b", "hand"): 1,
                ("protected_c", "hand"): 1,
                ("crobat_v", "deck"): 1,
                ("computer_search", "deck"): 1,
                ("gladion", "deck"): 1,
                ("filler", "deck"): 1,
                ("alolan_raichu", "prize"): 1,
            }
        )
    )


def main() -> None:
    state = base_state()
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

    result = execute_full_prized_raichu_rescue(
        state,
        BenchState(),
        quick_discard_candidates=quick_candidates,
        quick_discard_selection=DiscardSelection((1, 0, 0)),
        computer_discard_candidates=computer_candidates,
        computer_discard_selection=DiscardSelection((0, 1, 1, 0, 0, 0)),
    )

    assert len(result.gladion_outcomes) == 1
    outcome = result.gladion_outcomes[0]
    final = outcome.physical.physical_after

    assert final.ledger.instance("prize-raichu").zone == "hand"
    assert final.ledger.instance("private-gladion").zone == "prize"
    assert final.ledger.instance("top-filler").zone == "deck_top"
    assert final.ledger.exchangeable.count("crobat_v", "bench") == 1
    assert final.ledger.exchangeable.count("quick_ball", "discard") == 1
    assert final.ledger.exchangeable.count("computer_search", "discard") == 1
    assert outcome.budget_after.supporter_used

    for protected in ("protected_a", "protected_b", "protected_c"):
        assert final.ledger.exchangeable.count(protected, "hand") == 1

    initial_totals = state.zones
    for card_class in (
        "quick_ball",
        "computer_search",
        "gladion",
        "alolan_raichu",
        "crobat_v",
        "filler",
        "disposable_0",
        "disposable_1",
        "disposable_2",
        "protected_a",
        "protected_b",
        "protected_c",
    ):
        assert initial_totals.total(card_class) == final.ledger.total(card_class)

    print(
        json.dumps(
            {
                "line": [
                    "Quick Ball",
                    "Crobat V",
                    "Dark Asset -> Computer Search",
                    "Computer Search -> Gladion",
                    "Gladion -> Alolan Raichu",
                ],
                "alolan_raichu_final_zone": final.ledger.instance(
                    "prize-raichu"
                ).zone,
                "gladion_final_zone": final.ledger.instance(
                    "private-gladion"
                ).zone,
                "supporter_budget_consumed": outcome.budget_after.supporter_used,
                "crobat_final_zone": "bench",
                "protected_cards_preserved": True,
                "physical_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
