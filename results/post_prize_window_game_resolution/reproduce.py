"""Reproduce official Jirachi Prism Star terminal-timing ruling."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from post_knockout_game_resolution import (
    Outcome,
    resolve_prize_and_board_loss_conditions,
)
from post_prize_window_game_resolution import resolve_after_prize_window
from prize_before_hand_bench_entry import use_wish_upon_a_star
from prize_pending_take import resolve_next_pending_prize, stage_prize_takes
from promotion_pending_conservation import (
    PostKnockOutPromotionContext,
    PostKnockOutStage,
    dispose_pending_before_promotion,
    replace_player_state,
)
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import TopPrizePhysicalState


def build_player(
    prefix: str,
    *,
    prize_class: str,
    prize_name: str,
) -> tuple[IdentityLedger, StackBoardMaterialState, TopPrizePhysicalState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                (f"{prefix}-active-class", "hand"): 1,
                (f"{prefix}-top-class", "deck_top"): 1,
                (prize_class, "prize"): 1,
            }
        )
    )
    ledger = materialize(
        initial,
        card_class=f"{prefix}-active-class",
        card_name=f"{prefix} Active",
        source_zone="hand",
        instance_id=f"{prefix}-active-card",
    )
    ledger = put_in_play_instance(
        ledger,
        f"{prefix}-active-card",
        f"{prefix}-active",
    )
    ledger = materialize(
        ledger,
        card_class=f"{prefix}-top-class",
        card_name=f"{prefix} Top",
        source_zone="deck_top",
        instance_id=f"{prefix}-top-card",
    )
    ledger = materialize(
        ledger,
        card_class=prize_class,
        card_name=prize_name,
        source_zone="prize",
        instance_id=f"{prefix}-prize-card",
    )

    state = StackBoardMaterialState(
        ledger,
        make_state(
            (
                BoardPokemon(
                    f"{prefix}-active",
                    (PokemonCard(f"{prefix}-active-card", f"{prefix} Active"),),
                    retreat_cost=1,
                ),
            ),
            active_id=f"{prefix}-active",
        ),
    )
    physical = TopPrizePhysicalState(
        ledger,
        f"{prefix}-top-card",
        (f"{prefix}-prize-card",),
        (False,),
    )
    assert_conserved(initial, ledger)
    return initial, state, physical


def dispose_active(state: StackBoardMaterialState):
    assert state.board is not None
    pending = prepare_knock_out_batch(state, (state.board.active_id,))
    assert pending is not None
    return dispose_pending_before_promotion(pending)


def sync_physical(
    physical: TopPrizePhysicalState,
    ledger: IdentityLedger,
) -> TopPrizePhysicalState:
    return TopPrizePhysicalState(
        ledger,
        physical.top_instance_id,
        physical.prize_instance_ids,
        physical.face_up,
    )


def main() -> None:
    initial_a, state_a, physical_a = build_player(
        "a",
        prize_class="sm7-97",
        prize_name="Jirachi ◇",
    )
    initial_b, state_b, physical_b = build_player(
        "b",
        prize_class="b-filler-prize",
        prize_name="Filler Prize",
    )

    pending_a = dispose_active(state_a)
    pending_b = dispose_active(state_b)
    assert pending_a.pokemon == ()
    assert pending_b.pokemon == ()

    context = PostKnockOutPromotionContext(
        (("A", pending_a), ("B", pending_b)),
        next_player_id="B",
    )

    # Counterfactual early terminal check: both final Prizes taken and neither
    # player has a Pokemon would be a tie.
    early = resolve_prize_and_board_loss_conditions(
        player_ids=("A", "B"),
        prizes_remaining={"A": 0, "B": 0},
        pokemon_in_play={"A": 0, "B": 0},
    )
    assert early.outcome("A") == Outcome.TIE
    assert early.outcome("B") == Outcome.TIE

    physical_a = sync_physical(physical_a, pending_a.ledger)
    physical_b = sync_physical(physical_b, pending_b.ledger)
    prizes_a = stage_prize_takes(physical_a, positions=(0,))
    prizes_b = stage_prize_takes(physical_b, positions=(0,))
    context = replace_player_state(
        context,
        player_id="A",
        state=pending_a.with_ledger(prizes_a.physical.ledger),
    )
    context = replace_player_state(
        context,
        player_id="B",
        state=pending_b.with_ledger(prizes_b.physical.ledger),
    )

    # Game resolution is not yet allowed because both final Prize cards are
    # inside the E-31 pending window.
    assert resolve_after_prize_window(
        context,
        prizes_remaining={"A": 0, "B": 0},
    ) is None

    jirachi = use_wish_upon_a_star(
        prizes_a,
        context.state_for("A"),
        pokemon_id="a-jirachi",
        during_your_turn=True,
    )
    assert jirachi is not None
    assert jirachi.after_board.promotion_candidates == ("a-jirachi",)
    assert jirachi.after_prizes.pending == ()
    context = replace_player_state(
        context,
        player_id="A",
        state=jirachi.after_board,
    )

    filler = resolve_next_pending_prize(prizes_b)
    context = replace_player_state(
        context,
        player_id="B",
        state=context.state_for("B").with_ledger(
            filler.after.physical.ledger
        ),
    )

    resolved = resolve_after_prize_window(
        context,
        prizes_remaining={"A": 0, "B": 0},
    )
    assert resolved is not None
    assert resolved.context.stage == PostKnockOutStage.TERMINAL
    assert resolved.resolution.outcome("A") == Outcome.WIN
    assert resolved.resolution.outcome("B") == Outcome.LOSS

    # Jirachi survives as a real physical Pokemon. B still has no Pokemon.
    assert len(resolved.context.state_for("A").pokemon) == 1
    assert len(resolved.context.state_for("B").pokemon) == 0
    assert resolved.context.state_for("A").ledger.instance(
        "a-prize-card"
    ).zone == "in_play"

    assert_conserved(initial_a, resolved.context.state_for("A").ledger)
    assert_conserved(initial_b, resolved.context.state_for("B").ledger)

    print("post-Prize-window terminal timing regression passed")
    print("early counterfactual: tie")
    print("official E-31 sequence: A wins")


if __name__ == "__main__":
    main()
