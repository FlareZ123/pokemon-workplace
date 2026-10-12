"""Reproduce executable E-31 Prize-to-Bench transitions."""

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
from prize_before_hand_bench_entry import (
    use_lucky_bonus,
    use_wish_upon_a_star,
)
from prize_pending_take import resolve_next_pending_prize, stage_prize_takes
from promotion_pending_conservation import dispose_pending_before_promotion
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import TopPrizePhysicalState


def build_state(
    *,
    prefix: str,
    bench_count: int,
    prize_classes: tuple[tuple[str, str], ...],
) -> tuple[IdentityLedger, StackBoardMaterialState, TopPrizePhysicalState]:
    counts = {(f"{prefix}-active-class", "hand"): 1}
    for index in range(bench_count):
        counts[(f"{prefix}-bench-{index}-class", "hand")] = 1
    counts[(f"{prefix}-top-class", "deck_top")] = 1
    for card_class, _card_name in prize_classes:
        counts[(card_class, "prize")] = counts.get((card_class, "prize"), 0) + 1

    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
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
    rows = [
        BoardPokemon(
            f"{prefix}-active",
            (PokemonCard(f"{prefix}-active-card", f"{prefix} Active"),),
            retreat_cost=1,
        )
    ]

    for index in range(bench_count):
        instance_id = f"{prefix}-bench-{index}-card"
        pokemon_id = f"{prefix}-bench-{index}"
        ledger = materialize(
            ledger,
            card_class=f"{prefix}-bench-{index}-class",
            card_name=f"{prefix} Bench {index}",
            source_zone="hand",
            instance_id=instance_id,
        )
        ledger = put_in_play_instance(ledger, instance_id, pokemon_id)
        rows.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, f"{prefix} Bench {index}"),),
                retreat_cost=1,
            )
        )

    top_id = f"{prefix}-top-card"
    ledger = materialize(
        ledger,
        card_class=f"{prefix}-top-class",
        card_name=f"{prefix} Top",
        source_zone="deck_top",
        instance_id=top_id,
    )

    prize_ids = []
    for index, (card_class, card_name) in enumerate(prize_classes):
        instance_id = f"{prefix}-prize-{index}"
        ledger = materialize(
            ledger,
            card_class=card_class,
            card_name=card_name,
            source_zone="prize",
            instance_id=instance_id,
        )
        prize_ids.append(instance_id)

    board = StackBoardMaterialState(
        ledger,
        make_state(tuple(rows), active_id=f"{prefix}-active"),
    )
    physical = TopPrizePhysicalState(
        ledger,
        top_id,
        tuple(prize_ids),
        tuple(False for _ in prize_ids),
    )
    assert_conserved(initial, ledger)
    return initial, board, physical


def sync_physical(
    physical: TopPrizePhysicalState,
    board,
) -> TopPrizePhysicalState:
    return TopPrizePhysicalState(
        board.ledger,
        physical.top_instance_id,
        physical.prize_instance_ids,
        physical.face_up,
    )


def after_active_ko(
    board: StackBoardMaterialState,
):
    assert board.board is not None
    pending = prepare_knock_out_batch(
        board,
        (board.board.active_id,),
    )
    assert pending is not None
    return dispose_pending_before_promotion(pending)



def validate_jirachi_knockout_slot_geometry() -> None:
    """Official Jirachi full-Bench Q&A and a derived sequential Prize chain.

    The opposing Active Knock Out that awards the initial Prize is assumed
    upstream. These four cases differ only in which of our own Pokemon are
    removed by the same resolution batch.
    """
    cases = (
        ("active_only", ("active",), False, False, 5),
        ("bench_only", ("bench-0",), True, False, 5),
        ("active_one_bench", ("active", "bench-0"), True, False, 5),
        ("active_two_benches", ("active", "bench-0", "bench-1"), True, True, 4),
    )
    for case, removed_roles, can_wish, can_lucky, wish_bench_size in cases:
        prefix = f"geometry-{case}"
        initial, board, physical = build_state(
            prefix=prefix,
            bench_count=5,
            prize_classes=(
                ("sm7-97", "Jirachi ◇"),
                ("sv3pt5-113", "Chansey"),
                (f"{prefix}-other-class", "Other"),
            ),
        )
        knocked_out = tuple(f"{prefix}-{role}" for role in removed_roles)
        batch = prepare_knock_out_batch(board, knocked_out)
        assert batch is not None
        post_ko = dispose_pending_before_promotion(batch)
        assert post_ko.active_id is None if "active" in removed_roles else post_ko.active_id == f"{prefix}-active"

        stage = stage_prize_takes(
            sync_physical(physical, post_ko),
            positions=(0,),
        )
        post_ko = post_ko.with_ledger(stage.physical.ledger)
        wish = use_wish_upon_a_star(
            stage,
            post_ko,
            pokemon_id=f"{prefix}-jirachi",
            during_your_turn=True,
        )
        assert (wish is not None) == can_wish, case

        if wish is None:
            assert post_ko.bench_occupancy == 5
            assert_conserved(initial, post_ko.ledger)
            continue

        assert wish.extra_prize_staged
        assert wish.after_board.bench_occupancy == wish_bench_size
        assert wish.after_prizes.pending[0].instance_id == f"{prefix}-prize-1"

        lucky = use_lucky_bonus(
            wish.after_prizes,
            wish.after_board,
            pokemon_id=f"{prefix}-chansey",
            coin_heads=True,
            during_your_turn=True,
        )
        assert (lucky is not None) == can_lucky, case

        if lucky is None:
            # Jirachi took the final Bench slot. The extra Prize still
            # reaches hand, but Chansey cannot enter after that decision.
            hand = resolve_next_pending_prize(wish.after_prizes)
            final_board = wish.after_board.with_ledger(hand.after.physical.ledger)
            assert hand.after.pending == ()
            assert final_board.ledger.instance(f"{prefix}-prize-1").zone == "hand"
            assert final_board.bench_occupancy == 5
        else:
            # Two prior Bench Knock Outs leave room for both Prize effects.
            # Heads on Lucky Bonus now stages a third face-down Prize.
            assert lucky.extra_prize_staged
            assert lucky.after_board.bench_occupancy == 5
            assert lucky.after_prizes.pending[0].instance_id == f"{prefix}-prize-2"
            third = resolve_next_pending_prize(lucky.after_prizes)
            assert third.after.pending == ()
            final_board = lucky.after_board.with_ledger(third.after.physical.ledger)
            assert final_board.ledger.instance(f"{prefix}-prize-2").zone == "hand"

        assert_conserved(initial, final_board.ledger)


def main() -> None:
    initial_c, board_c, physical_c = build_state(
        prefix="c",
        bench_count=0,
        prize_classes=(("sv3pt5-113", "Chansey"),),
    )
    pending_board_c = after_active_ko(board_c)
    assert pending_board_c.pokemon == ()
    assert pending_board_c.active_id is None
    assert pending_board_c.open_bench_slots == 5

    physical_c = sync_physical(physical_c, pending_board_c)
    staged_c = stage_prize_takes(physical_c, positions=(0,))
    pending_board_c = pending_board_c.with_ledger(staged_c.physical.ledger)
    assert use_lucky_bonus(
        staged_c,
        pending_board_c,
        pokemon_id="c-chansey",
        coin_heads=False,
        during_your_turn=False,
    ) is None
    lucky = use_lucky_bonus(
        staged_c,
        pending_board_c,
        pokemon_id="c-chansey",
        coin_heads=False,
        during_your_turn=True,
    )
    assert lucky is not None
    assert lucky.after_board.active_id is None
    assert lucky.after_board.promotion_candidates == ("c-chansey",)
    assert lucky.after_prizes.pending == ()
    assert lucky.after_board.ledger.instance("c-prize-0").zone == "in_play"
    assert_conserved(initial_c, lucky.after_board.ledger)

    initial_f, board_f, physical_f = build_state(
        prefix="f",
        bench_count=5,
        prize_classes=(("sv3pt5-113", "Chansey"),),
    )
    pending_board_f = after_active_ko(board_f)
    assert pending_board_f.bench_occupancy == 5
    assert pending_board_f.open_bench_slots == 0

    physical_f = sync_physical(physical_f, pending_board_f)
    staged_f = stage_prize_takes(physical_f, positions=(0,))
    pending_board_f = pending_board_f.with_ledger(staged_f.physical.ledger)
    assert use_lucky_bonus(
        staged_f,
        pending_board_f,
        pokemon_id="f-chansey",
        coin_heads=False,
        during_your_turn=True,
    ) is None
    assert_conserved(initial_f, pending_board_f.ledger)

    initial_j, board_j, physical_j = build_state(
        prefix="j",
        bench_count=1,
        prize_classes=(
            ("sm7-97", "Jirachi ◇"),
            ("sv3pt5-113", "Chansey"),
        ),
    )
    pending_board_j = after_active_ko(board_j)
    physical_j = sync_physical(physical_j, pending_board_j)
    staged_j = stage_prize_takes(physical_j, positions=(0,))
    pending_board_j = pending_board_j.with_ledger(staged_j.physical.ledger)

    assert use_wish_upon_a_star(
        staged_j,
        pending_board_j,
        pokemon_id="j-jirachi",
        during_your_turn=False,
        extra_prize_position=0,
    ) is None
    wish = use_wish_upon_a_star(
        staged_j,
        pending_board_j,
        pokemon_id="j-jirachi",
        during_your_turn=True,
        extra_prize_position=0,
    )
    assert wish is not None
    assert wish.extra_prize_staged
    assert wish.after_board.ledger.instance("j-prize-0").zone == "in_play"
    assert wish.after_prizes.pending[0].instance_id == "j-prize-1"
    assert wish.after_board.open_bench_slots == 3

    chained_lucky = use_lucky_bonus(
        wish.after_prizes,
        wish.after_board,
        pokemon_id="j-chansey",
        coin_heads=False,
        during_your_turn=True,
    )
    assert chained_lucky is not None
    assert chained_lucky.after_prizes.pending == ()
    assert chained_lucky.after_board.ledger.instance("j-prize-1").zone == "in_play"
    assert {row.pokemon_id for row in chained_lucky.after_board.pokemon} == {
        "j-bench-0",
        "j-jirachi",
        "j-chansey",
    }
    assert_conserved(initial_j, chained_lucky.after_board.ledger)

    validate_jirachi_knockout_slot_geometry()
    print("before-hand Prize Bench-entry regressions passed")


if __name__ == "__main__":
    main()
