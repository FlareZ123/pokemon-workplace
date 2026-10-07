"""Reproduce the physical bounded Quick -> Dark Asset -> Ultra witness."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_dark_asset_followup_execution import (
    execute_quick_dark_asset_ultra_raichu,
)
from trainer_search_transaction import TrainerSearchExecutionState


def base_state(disposable_copies: int) -> TrainerSearchExecutionState:
    mapping = {
        ("quick_ball", "hand"): 1,
        ("protected_a", "hand"): 1,
        ("protected_b", "hand"): 1,
        ("protected_c", "hand"): 1,
        ("crobat_v", "deck"): 2,
        ("ultra_ball", "deck"): 1,
        ("alolan_raichu", "deck"): 1,
    }
    for index in range(disposable_copies):
        mapping[(f"disposable_{index}", "hand")] = 1

    hand_size = 1 + 3 + disposable_copies
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
    state = base_state(3)
    quick_candidates = (
        DiscardCandidate("disposable_0"),
        DiscardCandidate("disposable_1"),
        DiscardCandidate("disposable_2"),
    )
    ultra_candidates = quick_candidates + (
        DiscardCandidate("protected_a", max_copies=0),
        DiscardCandidate("protected_b", max_copies=0),
        DiscardCandidate("protected_c", max_copies=0),
    )

    result = execute_quick_dark_asset_ultra_raichu(
        state,
        BenchState(),
        quick_discard_candidates=quick_candidates,
        quick_discard_selection=DiscardSelection((1, 0, 0)),
        ultra_discard_candidates=ultra_candidates,
        ultra_discard_selection=DiscardSelection((0, 1, 1, 0, 0, 0)),
    )

    assert result.first.hand_size_after_bench == 5
    assert result.first.dark_asset_draw_count == 1
    assert result.after_dark_asset_draw.zones.count("ultra_ball", "hand") == 1
    assert result.second.discard_cost == 2
    assert result.final.zones.count("alolan_raichu", "hand") == 1

    assert result.final.zones.count("quick_ball", "discard") == 1
    assert result.final.zones.count("ultra_ball", "discard") == 1
    assert result.final.zones.count("disposable_0", "discard") == 1
    assert result.final.zones.count("disposable_1", "discard") == 1
    assert result.final.zones.count("disposable_2", "discard") == 1
    assert result.final.zones.count("crobat_v", "bench") == 1
    for protected in ("protected_a", "protected_b", "protected_c"):
        assert result.final.zones.count(protected, "hand") == 1

    for card_class in (
        "quick_ball",
        "ultra_ball",
        "alolan_raichu",
        "crobat_v",
        "disposable_0",
        "disposable_1",
        "disposable_2",
        "protected_a",
        "protected_b",
        "protected_c",
    ):
        assert state.zones.total(card_class) == result.final.zones.total(card_class)

    two_disposable = base_state(2)
    two_quick_candidates = (
        DiscardCandidate("disposable_0"),
        DiscardCandidate("disposable_1"),
    )
    residual_gate_rejected = expect_value_error(
        lambda: execute_quick_dark_asset_ultra_raichu(
            two_disposable,
            BenchState(),
            quick_discard_candidates=two_quick_candidates,
            quick_discard_selection=DiscardSelection((1, 0)),
            ultra_discard_candidates=two_quick_candidates + (
                DiscardCandidate("protected_a", max_copies=0),
                DiscardCandidate("protected_b", max_copies=0),
                DiscardCandidate("protected_c", max_copies=0),
            ),
        )
    )
    assert residual_gate_rejected

    print(
        json.dumps(
            {
                "quick_post_bench_hand": result.first.hand_size_after_bench,
                "dark_asset_exact_draw": "Ultra Ball",
                "residual_disposables_after_quick": 2,
                "followup_ultra_discard_cost": result.second.discard_cost,
                "alolan_raichu_reached": (
                    result.final.zones.count("alolan_raichu", "hand") == 1
                ),
                "two_initial_disposables_fail_residual_gate": residual_gate_rejected,
                "protected_cards_preserved": True,
                "card_class_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
