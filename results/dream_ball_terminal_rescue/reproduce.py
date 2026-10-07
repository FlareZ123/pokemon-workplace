"""Reproduce Dream Ball changing a final Prize/no-Pokemon terminal result."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_profiles import build_before_hand_prize_profiles
from dream_ball_typed_bench_execution import (
    dream_ball_target_from_metadata,
    execute_dream_ball_item_transaction,
)
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from post_knockout_game_resolution import Outcome
from post_prize_window_game_resolution import resolve_after_prize_window
from prize_pending_take import (
    PendingPrize,
    PrizePendingTakeState,
    resolve_next_pending_prize,
)
from promotion_pending_conservation import (
    PostKnockOutPromotionContext,
    PostKnockOutStage,
    PromotionPendingState,
    replace_player_state,
    unresolved_prize_window_count,
)
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import (
    enumerate_typed_target_profiles,
    make_demand,
)


def make_state():
    initial_a = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("sv3-164", "deck"): 1,
            }
        ),
        (
            CardInstance("dream", "swsh7-146", "Dream Ball", "prize_pending"),
            CardInstance("top", "top-class", "Top Card", "deck_top"),
        ),
    )
    state_a = PromotionPendingState(
        initial_a,
        (),
        active_id=None,
    )
    prizes_a = PrizePendingTakeState(
        TopPrizePhysicalState(initial_a, "top", (), ()),
        (PendingPrize("dream", True),),
    )

    initial_b = IdentityLedger(ZoneCountState())
    state_b = PromotionPendingState(
        initial_b,
        (),
        active_id=None,
    )
    context = PostKnockOutPromotionContext(
        (("A", state_a), ("B", state_b)),
        next_player_id="B",
    )
    return initial_a, prizes_a, context


def main() -> None:
    profile_by_id = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(ROOT / "resources")
    }
    dream_ball = profile_by_id["swsh7-146"]
    metadata = pokemon_board_metadata_by_id(ROOT / "resources")
    target = dream_ball_target_from_metadata(
        metadata["sv3-164"],
        copies=1,
    )
    allocation = enumerate_typed_target_profiles(
        (SearchOutput("Pokemon"),),
        (target.search_target.group,),
        (make_demand("pokemon", "Pokemon"),),
    )
    action = next(
        row
        for row in allocation.actions
        if row.target_cost == (1,)
    )

    prizes_remaining = {"A": 0, "B": 0}

    initial_a, prizes_a, context = make_state()
    assert context.state_for("A").pokemon == ()
    assert context.state_for("B").pokemon == ()
    assert unresolved_prize_window_count(context) == 1
    assert resolve_after_prize_window(
        context,
        prizes_remaining=prizes_remaining,
    ) is None

    # Counterfactual policy: decline Dream Ball and put it into hand. With both
    # final Prizes gone and neither player controlling a Pokemon, the table ties.
    declined_prize = resolve_next_pending_prize(prizes_a).after
    declined_a = context.state_for("A").with_ledger(
        declined_prize.physical.ledger
    )
    declined_context = replace_player_state(
        context,
        player_id="A",
        state=declined_a,
    )
    declined = resolve_after_prize_window(
        declined_context,
        prizes_remaining=prizes_remaining,
    )
    assert declined is not None
    assert declined.context.stage == PostKnockOutStage.TERMINAL
    assert declined.resolution.outcome("A") == Outcome.TIE
    assert declined.resolution.outcome("B") == Outcome.TIE

    # Executed policy: Dream Ball remains inside E-31 timing, creates a Pidgeot
    # ex board object, and only then allows the terminal snapshot.
    used = execute_dream_ball_item_transaction(
        prizes_a,
        context.state_for("A"),
        profile=dream_ball,
        during_own_turn=True,
        targets=(target,),
        search_action=action,
        pokemon_id="pidgeot-object",
        instance_id="pidgeot-card",
    )
    assert used.after_board.active_id is None
    assert used.after_board.requires_promotion
    assert len(used.after_board.pokemon) == 1
    assert used.after_board.pokemon[0].name == "Pidgeot ex"

    used_context = replace_player_state(
        context,
        player_id="A",
        state=used.after_board,
    )
    assert unresolved_prize_window_count(used_context) == 0
    resolved = resolve_after_prize_window(
        used_context,
        prizes_remaining=prizes_remaining,
    )
    assert resolved is not None
    assert resolved.context.stage == PostKnockOutStage.TERMINAL
    assert resolved.resolution.outcome("A") == Outcome.WIN
    assert resolved.resolution.outcome("B") == Outcome.LOSS
    assert_conserved(initial_a, used.after_board.ledger)

    print(
        json.dumps(
            {
                "terminal_check_blocked_while_dream_ball_pending": True,
                "decline_dream_ball_outcome_A": declined.resolution.outcome("A").value,
                "use_dream_ball_outcome_A": resolved.resolution.outcome("A").value,
                "dream_ball_target": "Pidgeot ex sv3-164",
                "target_enters_before_terminal_snapshot": True,
                "promotion_never_needed_after_terminal_win": True,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
