"""Reproduce Supporter-budget-coupled physical Gladion resolution."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from gladion_supporter_physical_transaction import (
    execute_gladion_supporter_physical,
)
from identity_materialization import IdentityLedger, materialize
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from top_prize_physical_bridge import TopPrizePhysicalState
from turn_action_budget import TurnActionBudget


def make_state() -> TopPrizePhysicalState:
    ledger = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("gladion", "hand"): 1,
                ("target", "prize"): 1,
                ("other_prize", "prize"): 1,
                ("top", "deck_top"): 1,
            }
        )
    )
    ledger = materialize(
        ledger,
        card_class="gladion",
        card_name="Gladion",
        source_zone="hand",
        instance_id="gladion-1",
    )
    ledger = materialize(
        ledger,
        card_class="target",
        card_name="Target",
        source_zone="prize",
        instance_id="prize-target",
    )
    ledger = materialize(
        ledger,
        card_class="other_prize",
        card_name="Other Prize",
        source_zone="prize",
        instance_id="prize-other",
    )
    ledger = materialize(
        ledger,
        card_class="top",
        card_name="Top",
        source_zone="deck_top",
        instance_id="top-1",
    )
    return TopPrizePhysicalState(
        ledger,
        "top-1",
        ("prize-target", "prize-other"),
        (False, False),
    )


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    state = make_state()
    budget = TurnActionBudget()
    outcomes = execute_gladion_supporter_physical(
        state,
        budget,
        PlayerChannels(),
        gladion_instance_id="gladion-1",
        selected_position=0,
    )
    assert len(outcomes) == 2
    assert abs(sum(row.physical.probability for row in outcomes) - 1.0) < 1e-12

    for row in outcomes:
        after = row.physical.physical_after
        assert row.budget_after.supporter_used
        assert after.ledger.instance("prize-target").zone == "hand"
        assert after.ledger.instance("gladion-1").zone == "prize"
        assert after.top_instance_id == "top-1"
        assert after.ledger.totals() == state.ledger.totals()
        assert set(after.prize_instance_ids) == {"gladion-1", "prize-other"}

    locked = expect_value_error(
        lambda: execute_gladion_supporter_physical(
            state,
            budget,
            PlayerChannels(supporter_play=False),
            gladion_instance_id="gladion-1",
            selected_position=0,
        )
    )
    assert locked

    exhausted = expect_value_error(
        lambda: execute_gladion_supporter_physical(
            state,
            TurnActionBudget(supporter_plays_used=1),
            PlayerChannels(),
            gladion_instance_id="gladion-1",
            selected_position=0,
        )
    )
    assert exhausted

    print(
        json.dumps(
            {
                "physical_shuffle_outcomes": len(outcomes),
                "probability_mass": sum(
                    row.physical.probability for row in outcomes
                ),
                "target_moves_prize_to_hand": True,
                "played_gladion_moves_hand_to_prize": True,
                "supporter_budget_consumed": True,
                "supporter_lock_rejected": locked,
                "spent_supporter_budget_rejected": exhausted,
                "deck_top_preserved": True,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
