"""Reproduce physical Quick/Ultra Ball -> Crobat V execution witnesses."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchState, add_core
from discard_cost_witness import DiscardCandidate
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from raichu_search_to_crobat_execution import execute_search_to_crobat
from trainer_search_transaction import TrainerSearchExecutionState


def seven_card_state(action: str) -> TrainerSearchExecutionState:
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                (action, "hand"): 1,
                ("disposable_a", "hand"): 1,
                ("disposable_b", "hand"): 1,
                ("disposable_c", "hand"): 1,
                ("protected_a", "hand"): 1,
                ("protected_b", "hand"): 1,
                ("protected_c", "hand"): 1,
                ("crobat_v", "deck"): 2,
            }
        )
    )


def full_bench() -> BenchState:
    state = BenchState()
    for index in range(5):
        next_state = add_core(
            state,
            name=f"core_{index}",
            retention_value=10.0 - index,
        )
        assert next_state is not None
        state = next_state
    return state


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def assert_class_total(before: ZoneCountState, after: ZoneCountState, card_class: str) -> None:
    assert before.total(card_class) == after.total(card_class), (
        card_class,
        before.total(card_class),
        after.total(card_class),
    )


def main() -> None:
    candidates = (
        DiscardCandidate("disposable_a"),
        DiscardCandidate("disposable_b"),
        DiscardCandidate("disposable_c"),
        DiscardCandidate("protected_a", max_copies=0),
        DiscardCandidate("protected_b", max_copies=0),
        DiscardCandidate("protected_c", max_copies=0),
    )

    quick_state = seven_card_state("quick_ball")
    quick = execute_search_to_crobat(
        quick_state,
        BenchState(),
        action_card_class="quick_ball",
        discard_candidates=candidates,
    )
    assert quick.crobat_benched
    assert quick.hand_size_after_search == 6
    assert quick.hand_size_after_bench == 5
    assert quick.dark_asset_draw_count == 1
    assert quick.transaction.discard_cost == 1
    assert quick.transaction.after.zones.count("quick_ball", "discard") == 1
    assert quick.transaction.after.zones.count("crobat_v", "hand") == 1
    assert quick.zones_after_bench.count("crobat_v", "bench") == 1
    assert quick.bench_after is not None
    assert quick.bench_after.trigger_count("Dark Asset") == 1
    assert quick.transaction.after.zones.count("protected_a", "hand") == 1

    ultra_state = seven_card_state("ultra_ball")
    ultra = execute_search_to_crobat(
        ultra_state,
        BenchState(),
        action_card_class="ultra_ball",
        discard_candidates=candidates,
    )
    assert ultra.crobat_benched
    assert ultra.hand_size_after_search == 5
    assert ultra.hand_size_after_bench == 4
    assert ultra.dark_asset_draw_count == 2
    assert ultra.transaction.discard_cost == 2
    assert ultra.transaction.after.zones.count("ultra_ball", "discard") == 1
    assert ultra.zones_after_bench.count("crobat_v", "bench") == 1
    assert ultra.bench_after is not None
    assert ultra.bench_after.trigger_count("Dark Asset") == 1
    assert ultra.transaction.after.zones.count("protected_a", "hand") == 1

    for card_class in (
        "quick_ball",
        "disposable_a",
        "disposable_b",
        "disposable_c",
        "protected_a",
        "protected_b",
        "protected_c",
        "crobat_v",
    ):
        assert_class_total(
            quick_state.zones,
            quick.zones_after_bench,
            card_class,
        )

    for card_class in (
        "ultra_ball",
        "disposable_a",
        "disposable_b",
        "disposable_c",
        "protected_a",
        "protected_b",
        "protected_c",
        "crobat_v",
    ):
        assert_class_total(
            ultra_state.zones,
            ultra.zones_after_bench,
            card_class,
        )

    saturated = execute_search_to_crobat(
        quick_state,
        full_bench(),
        action_card_class="quick_ball",
        discard_candidates=candidates,
    )
    assert not saturated.crobat_benched
    assert saturated.hand_size_after_search == 6
    assert saturated.hand_size_after_bench == 6
    assert saturated.dark_asset_draw_count == 0
    assert saturated.zones_after_bench.count("crobat_v", "hand") == 1
    assert saturated.zones_after_bench.count("crobat_v", "bench") == 0

    item_locked = expect_value_error(
        lambda: execute_search_to_crobat(
            TrainerSearchExecutionState(
                zones=quick_state.zones,
                channels=PlayerChannels(item_play=False),
            ),
            BenchState(),
            action_card_class="quick_ball",
            discard_candidates=candidates,
        )
    )
    assert item_locked

    insufficient_ultra_payment = expect_value_error(
        lambda: execute_search_to_crobat(
            TrainerSearchExecutionState(
                zones=ZoneCountState.from_mapping(
                    {
                        ("ultra_ball", "hand"): 1,
                        ("disposable_a", "hand"): 1,
                        ("protected_a", "hand"): 5,
                        ("crobat_v", "deck"): 1,
                    }
                )
            ),
            BenchState(),
            action_card_class="ultra_ball",
            discard_candidates=(
                DiscardCandidate("disposable_a"),
                DiscardCandidate("protected_a", max_copies=0),
            ),
        )
    )
    assert insufficient_ultra_payment

    print(
        json.dumps(
            {
                "quick_hand_after_search": quick.hand_size_after_search,
                "quick_hand_after_bench": quick.hand_size_after_bench,
                "quick_dark_asset_draw": quick.dark_asset_draw_count,
                "ultra_hand_after_search": ultra.hand_size_after_search,
                "ultra_hand_after_bench": ultra.hand_size_after_bench,
                "ultra_dark_asset_draw": ultra.dark_asset_draw_count,
                "full_bench_blocks_crobat_entry": not saturated.crobat_benched,
                "full_bench_leaves_searched_crobat_in_hand": (
                    saturated.zones_after_bench.count("crobat_v", "hand") == 1
                ),
                "item_lock_rejected": item_locked,
                "ultra_unpayable_rejected": insufficient_ultra_payment,
                "physical_card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
