from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    TurnBoundaryEffect,
    choose_exact,
    resolve_attack,
)
from attack_copy_terminal_bridge import close_copy_attack_after_game_resolution
from board_position_state import BoardPokemon, PokemonCard, make_state
from canonical_turn_sequence_owner import TurnScheduleState, advance_turn
from identity_materialization import (
    IdentityLedger,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from post_knockout_game_resolution import Outcome
from post_prize_window_game_resolution import (
    PrizeWindowResolution,
    resolve_after_prize_window,
)
from promotion_pending_conservation import (
    PostKnockOutPromotionContext,
    PromotionPendingState,
    choose_promotion,
    dispose_pending_before_promotion,
)
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state as make_unified_state

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"

ATTACKS = {
    HAUGHTY: AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    ),
    TIMELESS: AttackDef(
        TIMELESS,
        "Timeless-GX",
        is_gx=True,
        effect_label="body:timeless-gx",
        turn_boundary_effect=TurnBoundaryEffect(
            take_another_turn=True,
            skip_pokemon_checkup=True,
        ),
    ),
}


def copied_timeless():
    return resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-dialga-revealed",
                    "Dialga-GX",
                    "P2",
                    "revealed",
                    attacks=(TIMELESS,),
                ),
            )
        ),
        choose=choose_exact((TIMELESS,)),
    )


def build_side(prefix: str, *, bench_count: int) -> StackBoardMaterialState:
    counts = {(f"{prefix}-active-class", "hand"): 1}
    for index in range(bench_count):
        counts[(f"{prefix}-bench-{index}-class", "hand")] = 1
    ledger = IdentityLedger(ZoneCountState.from_mapping(counts))

    def put(
        current: IdentityLedger,
        *,
        card_class: str,
        card_name: str,
        instance_id: str,
        pokemon_id: str,
    ) -> IdentityLedger:
        current = materialize(
            current,
            card_class=card_class,
            card_name=card_name,
            source_zone="hand",
            instance_id=instance_id,
        )
        return put_in_play_instance(current, instance_id, pokemon_id)

    ledger = put(
        ledger,
        card_class=f"{prefix}-active-class",
        card_name=f"{prefix} Active",
        instance_id=f"{prefix}-active-copy",
        pokemon_id=f"{prefix}-active",
    )
    pokemon = [
        BoardPokemon(
            f"{prefix}-active",
            (PokemonCard(f"{prefix}-active-copy", f"{prefix} Active"),),
            retreat_cost=1,
        )
    ]

    for index in range(bench_count):
        pokemon_id = f"{prefix}-bench-{index}"
        instance_id = f"{prefix}-bench-{index}-copy"
        ledger = put(
            ledger,
            card_class=f"{prefix}-bench-{index}-class",
            card_name=f"{prefix} Bench {index}",
            instance_id=instance_id,
            pokemon_id=pokemon_id,
        )
        pokemon.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, f"{prefix} Bench {index}"),),
                retreat_cost=1,
            )
        )

    return StackBoardMaterialState(
        ledger,
        make_state(pokemon, active_id=f"{prefix}-active"),
    )


def unchanged_pending(state: StackBoardMaterialState) -> PromotionPendingState:
    board = state.board
    assert board is not None
    return PromotionPendingState(
        state.ledger,
        board.pokemon,
        board.active_id,
        board.retreat_used,
        board.evolution_allowed,
        board.bench_capacity,
    )


def after_active_knockout(state: StackBoardMaterialState) -> PromotionPendingState:
    board = state.board
    assert board is not None
    pending = prepare_knock_out_batch(state, (board.active_id,))
    assert pending is not None
    return dispose_pending_before_promotion(pending)


def turn_state():
    return make_unified_state({}, turn_budget=TurnActionBudget())


def test_terminal_ko_cancels_pending_extra_turn() -> None:
    copy = copied_timeless()
    p1 = build_side("p1", bench_count=0)
    p2 = build_side("p2", bench_count=0)

    context = PostKnockOutPromotionContext(
        (
            ("P1", unchanged_pending(p1)),
            ("P2", after_active_knockout(p2)),
        ),
        next_player_id="P2",
    )
    terminal = resolve_after_prize_window(
        context,
        prizes_remaining={"P1": 5, "P2": 6},
    )
    assert terminal is not None
    assert terminal.resolution.outcome("P1") == Outcome.WIN
    assert terminal.resolution.outcome("P2") == Outcome.LOSS

    boundary = close_copy_attack_after_game_resolution(
        schedule=TurnScheduleState("P1", "P2"),
        current_state=turn_state(),
        copy_resolution=copy,
        prize_window_resolution=terminal,
    )
    assert boundary is not None
    assert boundary.terminal
    assert boundary.boards is None
    assert boundary.turn_closure is None


def test_promotion_must_finish_before_extra_turn() -> None:
    copy = copied_timeless()
    p1 = build_side("p1c", bench_count=0)
    p2 = build_side("p2c", bench_count=1)

    context = PostKnockOutPromotionContext(
        (
            ("P1", unchanged_pending(p1)),
            ("P2", after_active_knockout(p2)),
        ),
        next_player_id="P2",
    )
    continuing = resolve_after_prize_window(
        context,
        prizes_remaining={"P1": 5, "P2": 6},
    )
    assert continuing is not None
    assert not continuing.resolution.terminal

    blocked = close_copy_attack_after_game_resolution(
        schedule=TurnScheduleState("P1", "P2"),
        current_state=turn_state(),
        copy_resolution=copy,
        prize_window_resolution=continuing,
    )
    assert blocked is None

    promoted = choose_promotion(
        continuing.context,
        player_id="P2",
        pokemon_id="p2c-bench-0",
    )
    assert promoted is not None
    ready = PrizeWindowResolution(promoted, continuing.resolution)

    boundary = close_copy_attack_after_game_resolution(
        schedule=TurnScheduleState("P1", "P2"),
        current_state=turn_state(),
        copy_resolution=copy,
        prize_window_resolution=ready,
    )
    assert boundary is not None
    assert not boundary.terminal
    assert boundary.boards is not None
    assert dict(boundary.boards)["P2"].board is not None
    assert dict(boundary.boards)["P2"].board.active_id == "p2c-bench-0"
    assert boundary.turn_closure is not None

    schedule, p1_closed = boundary.turn_closure
    advanced = advance_turn(schedule, p1_closed, turn_state())
    assert advanced is not None
    assert advanced.same_player_continues
    assert advanced.schedule.current_player == "P1"
    assert not advanced.pokemon_checkup_occurs


def main() -> None:
    test_terminal_ko_cancels_pending_extra_turn()
    test_promotion_must_finish_before_extra_turn()
    print("attack-copy terminal boundary regression: PASS")


if __name__ == "__main__":
    main()
