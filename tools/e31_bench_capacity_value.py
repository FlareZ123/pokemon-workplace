"""Exact E-31 action-order advantage across three Bench-capacity regimes.

Reuses physical Greedy Dice, Dream Ball, and Jirachi kernels. Each branch
contains four Prizes, one Jirachi among the two supplemental Prize slots,
and an original Greedy/Dream two-Prize award. The number of currently
unoccupied ordinary five-slot Bench spaces is varied as 0, 1, or 2.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from board_position_state import BoardPokemon, PokemonCard
from e31_greedy_order_physical import (
    make_state,
    play_dream,
    play_greedy,
    profiles_and_target,
)
from identity_materialization import (
    CardInstance, IdentityLedger, assert_conserved, move_instance,
)
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import PrizePendingTakeState
from promotion_pending_conservation import PromotionPendingState
from top_prize_physical_bridge import TopPrizePhysicalState


GREEDY = "Greedy Dice"
DREAM = "Dream Ball"


@dataclass(frozen=True)
class SlotMetrics:
    expected_prizes: Fraction
    fourth_prize_probability: Fraction
    dream_benched_probability: Fraction
    jirachi_benched_probability: Fraction


def tune_open_slots(initial, pending, board, *, open_slots: int):
    """Change real in-play materialized Basic count, retaining the 5-slot rule.

    With zero free slots one extra Basic is in play. With two free slots
    an existing former Bench Basic is moved into hand before the Prize
    award. Both constructions conserve the physical cards.
    """
    if open_slots not in (0, 1, 2):
        raise ValueError("supported open slot counts are 0, 1 and 2")
    if open_slots == 1:
        return initial, pending, board

    if open_slots == 0:
        extra = CardInstance(
            "bench-extra-card", "BASE-EXTRA", "Extra Basic", "in_play",
            board_object_id="bench-extra",
        )

        def adapt(ledger):
            return IdentityLedger(
                ledger.exchangeable,
                tuple(sorted(ledger.instances + (extra,),
                             key=lambda current: current.instance_id)),
            )

        pokemon = board.pokemon + (
            BoardPokemon(
                "bench-extra",
                (PokemonCard("bench-extra-card", "Extra Basic"),),
                retreat_cost=1,
            ),
        )
    else:
        def adapt(ledger):
            return move_instance(ledger, "base-4", "hand")

        pokemon = tuple(
            item for item in board.pokemon
            if item.pokemon_id != "bench-4"
        )

    before = adapt(initial)
    after = adapt(pending.physical.ledger)
    physical = TopPrizePhysicalState(
        after,
        pending.physical.top_instance_id,
        pending.physical.prize_instance_ids,
        pending.physical.face_up,
    )
    pending = PrizePendingTakeState(physical, pending.pending)
    board = PromotionPendingState(
        after, pokemon, active_id="active",
    )
    assert board.open_bench_slots == open_slots
    assert_conserved(before, after)
    return before, pending, board


def physical_branch(*, open_slots, order, known_positions,
                    jirachi_position, heads, use_jirachi=True):
    initial, pending, board = make_state(
        jirachi_first=(jirachi_position == 0),
    )
    initial, pending, board = tune_open_slots(
        initial, pending, board, open_slots=open_slots,
    )
    selection = jirachi_position if known_positions else 0
    greedy, dream, target, action = profiles_and_target()
    unresolved = PendingPrizeBatchOrder.from_staged(pending)

    for card in order:
        instance_id = "greedy" if card == GREEDY else "dream"
        pending = unresolved.choose_next(instance_id)
        if card == GREEDY:
            pending, board = play_greedy(
                pending, board, greedy,
                heads=heads,
                extra_position=selection,
                use_jirachi=use_jirachi,
            )
        else:
            pending, board = play_dream(
                pending, board, dream, target, action,
            )
        unresolved = unresolved.advance_after_resolution(
            pending,
            resolved_instance_id=instance_id,
        )

    assert unresolved is None
    assert not pending.pending
    assert_conserved(initial, board.ledger)
    assert board.ledger == pending.physical.ledger
    assert board.bench_capacity == 5
    newcomers = {item.pokemon_id for item in board.pokemon}
    return (
        4 - len(pending.physical.prize_instance_ids),
        "dream-target" in newcomers,
        "bonus-jirachi" in newcomers,
    )


def enumerate_slots(*, open_slots, order, known_positions,
                    use_jirachi=True):
    rows = [
        physical_branch(
            open_slots=open_slots,
            order=order,
            known_positions=known_positions,
            jirachi_position=pos,
            heads=heads,
            use_jirachi=use_jirachi,
        )
        for pos, heads in product((0, 1), (False, True))
    ]
    total = len(rows)
    return SlotMetrics(
        sum((Fraction(row[0], total) for row in rows), Fraction()),
        sum((Fraction(row[0] == 4, total) for row in rows), Fraction()),
        sum((Fraction(row[1], total) for row in rows), Fraction()),
        sum((Fraction(row[2], total) for row in rows), Fraction()),
    )


def main() -> None:
    for known in (False, True):
        extra = Fraction(1, 2) if known else Fraction(1, 4)
        for free in (0, 1, 2):
            early = enumerate_slots(
                open_slots=free,
                order=(GREEDY, DREAM),
                known_positions=known,
            )
            late = enumerate_slots(
                open_slots=free,
                order=(DREAM, GREEDY),
                known_positions=known,
            )
            if free == 0:
                expected = SlotMetrics(Fraction(5, 2), Fraction(), Fraction(), Fraction())
                assert early == late == expected
            elif free == 1:
                assert early == SlotMetrics(
                    Fraction(5, 2) + extra,
                    extra,
                    1 - extra,
                    extra,
                )
                assert late == SlotMetrics(
                    Fraction(5, 2),
                    Fraction(),
                    Fraction(1),
                    Fraction(),
                )
                decline = enumerate_slots(
                    open_slots=free,
                    order=(GREEDY, DREAM),
                    known_positions=known,
                    use_jirachi=False,
                )
                assert decline == late
            else:
                expected = SlotMetrics(
                    Fraction(5, 2) + extra,
                    extra,
                    Fraction(1),
                    extra,
                )
                assert early == late == expected
            print(
                f"position_known={known}; slots={free}; "
                f"Greedy-first={early}; Dream-first={late}"
            )

    print("Bench-capacity E-31 nonmonotonic order value: 48 physical coin/layout branches passed")


if __name__ == "__main__":
    main()
