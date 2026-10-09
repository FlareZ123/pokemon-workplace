"""Observer-relative Prize beliefs through a Peonia-seeded E-31 item chain.

A private random ordering of Peonia's three seeded cards leaves the opponent
uncertain about their positions even if their *composition* is known.
This regression uses the actual known physical layout as one supported world.
"""

from __future__ import annotations

from collections import Counter

from before_hand_prize_executor import (
    begin_before_hand_item_play,
    finish_before_hand_item_play,
    resolve_before_hand_item_effect,
)
from dream_ball_typed_bench_execution import execute_dream_ball_item_transaction
from e31_greedy_order_physical import profiles_and_target
from e31_peonia_seed_execution import initial_physical, play_peonia
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    independent_top_prize_belief,
)
from pending_prize_batch_identity_belief import (
    prepend_additional_pending_for_observers,
    project_completed_batch,
    resolve_pending_instance_visibility,
)
from prize_before_hand_bench_entry import use_wish_upon_a_star
from prize_pending_batch_observer import (
    PrizeBatchObserverState,
    resolve_batch_instance_destination,
    stage_prize_batch_with_latent_observers,
)
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import (
    resolve_next_pending_prize,
    stage_additional_prize_front,
)
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


GROUPS = {
    "TOP": "TOP",
    "xy11-102": "G",
    "swsh7-146": "D",
    "sm7-97": "J",
    "FILLER": None,
}
MODELED_GROUPS = ("TOP", "G", "D", "J")


def build_beliefs() -> ObserverTopPrizeBeliefs:
    """Actor knows private Peonia placement; opponent knows set, not order."""
    actor_positions = PrizePositionBelief.from_known_positions(
        ("G", "D", "J", None),
        groups=MODELED_GROUPS,
    )
    unknown_three = PrizePositionBelief.from_exact_composition(
        {"G": 1, "D": 1, "J": 1},
        prize_count=3,
    )
    opponent_positions = PrizePositionBelief(
        MODELED_GROUPS,
        4,
        tuple(
            (physical_three + (None,), probability)
            for physical_three, probability in unknown_three.masses
        ),
    )
    assert len(opponent_positions.masses) == 6
    assert opponent_positions.group_probability_at(2, "J") == 1 / 3

    def belief(positions: PrizePositionBelief):
        return independent_top_prize_belief(
            PrizeSlotVisibilityBelief.all_face_down(positions),
            {"TOP": 1.0},
        )

    return ObserverTopPrizeBeliefs((
        ("actor", belief(actor_positions)),
        ("opponent", belief(opponent_positions)),
    ))


def start_seeded_batch():
    initial, board, physical = initial_physical()
    board, physical = play_peonia(board, physical)
    beliefs = build_beliefs()
    assert beliefs.belief_for("actor").prize_probability_at(2, "J") == 1.0
    assert beliefs.belief_for("opponent").prize_probability_at(2, "J") == 1 / 3
    staged = stage_prize_batch_with_latent_observers(
        physical,
        beliefs,
        actor_id="actor",
        positions=(0, 1),
        group_by_card_class=GROUPS,
    )
    batch = staged.after
    assert (
        abs(batch.beliefs.belief_for("opponent").pending_probability(0, "G")
            - 1 / 3) < 1e-12
    )
    assert (
        abs(batch.beliefs.belief_for("opponent").pending_probability(1, "D")
            - 1 / 3) < 1e-12
    )
    return initial, board.with_ledger(batch.order.state.physical.ledger), batch


def play_greedy_with_observers(board, batch: PrizeBatchObserverState,
                              *, heads: bool):
    greedy, dream, target, action = profiles_and_target()
    ordered = batch.order.choose_next("greedy")
    resolving = begin_before_hand_item_play(
        ordered,
        greedy,
        during_own_turn=True,
    )
    board = board.with_ledger(resolving.physical.ledger)

    # Playing the Prize-origin Item is public, unlike merely staging its
    # face-down Prize into the private pending window.
    belief = resolve_pending_instance_visibility(
        batch.beliefs,
        instance_id="greedy",
        visible_groups={"actor": "G", "opponent": "G"},
    )
    assert belief.pending_instance_ids == ("dream",)
    assert abs(
        sum(
            p for (_top, prize, _pending), p
            in belief.belief_for("opponent").masses
            if prize[0] == "J"
        ) - 0.5
    ) < 1e-12

    effect = resolve_before_hand_item_effect(resolving, coin_heads=heads)
    physical = resolving.pending_state()

    if heads:
        physical = stage_additional_prize_front(physical, position=0)
        belief = prepend_additional_pending_for_observers(
            belief,
            position=0,
            instance_id="jirachi",
            visible_groups={"actor": "J"},
        )
        board = board.with_ledger(physical.physical.ledger)
        wish = use_wish_upon_a_star(
            physical, board,
            pokemon_id="bonus-jirachi",
            during_your_turn=True,
            extra_prize_position=0,
        )
        assert wish is not None
        assert wish.extra_prize_staged
        physical = wish.after_prizes
        board = wish.after_board

        # Jirachi enters play and is now publicly identifiable. Wish Upon
        # a Star immediately stages the last extra Prize before Dream Ball.
        belief = resolve_pending_instance_visibility(
            belief,
            instance_id="jirachi",
            visible_groups={"actor": "J", "opponent": "J"},
        )
        belief = prepend_additional_pending_for_observers(
            belief,
            position=0,
            instance_id="filler",
            visible_groups={"actor": None},
        )
        assert belief.pending_instance_ids == ("filler", "dream")
        assert tuple(p.instance_id for p in physical.pending) == (
            "filler", "dream",
        )
        physical = resolve_next_pending_prize(physical).after
        belief = resolve_pending_instance_visibility(
            belief,
            instance_id="filler",
            visible_groups={"actor": None},
        )
        board = board.with_ledger(physical.physical.ledger)

    physical = finish_before_hand_item_play(
        effect,
        continuation_state=physical,
        additional_prizes_resolved=heads,
    )
    board = board.with_ledger(physical.physical.ledger)
    assert belief.pending_instance_ids == ("dream",)
    batch = PrizeBatchObserverState(
        PendingPrizeBatchOrder(physical, ("dream",)),
        belief,
        actor_id="actor",
        group_by_card_class=GROUPS,
    )
    return board, batch, (dream, target, action)


def complete_dream_with_observers(board, batch, deps, *, heads):
    dream, target, action = deps
    physical = batch.order.state
    if heads:
        assert board.open_bench_slots == 0
        final = resolve_batch_instance_destination(
            batch,
            instance_id="dream",
            destination_zone="hand",
        )
        assert final.after_batch is None
        physical = final.physical_resolution.after
        projected = final.after_beliefs
        board = board.with_ledger(physical.physical.ledger)
    else:
        assert board.open_bench_slots == 1
        tx = execute_dream_ball_item_transaction(
            physical,
            board,
            profile=dream,
            during_own_turn=True,
            targets=(target,),
            search_action=action,
            pokemon_id="dream-target",
            instance_id="dream-card",
        )
        physical, board = tx.after_prizes, tx.after_board
        pending = resolve_pending_instance_visibility(
            batch.beliefs,
            instance_id="dream",
            visible_groups={"actor": "D", "opponent": "D"},
        )
        projected = project_completed_batch(pending)

    assert not physical.pending
    assert physical.physical.ledger == board.ledger
    return physical, board, projected


def run_branch(*, heads: bool):
    initial, board, batch = start_seeded_batch()
    board, batch, deps = play_greedy_with_observers(board, batch, heads=heads)
    physical, board, beliefs = complete_dream_with_observers(
        board, batch, deps, heads=heads,
    )
    assert_conserved(initial, board.ledger)
    assert all(not t for t in physical.physical.face_up)
    assert board.ledger.instance("peonia").zone == "discard"
    assert board.ledger.instance("chansey").zone == "hand"
    assert (
        beliefs.belief_for("actor").prize_count
        == beliefs.belief_for("opponent").prize_count
        == len(physical.physical.prize_instance_ids)
    )
    if heads:
        assert not physical.physical.prize_instance_ids
        assert "bonus-jirachi" in {row.pokemon_id for row in board.pokemon}
        assert all(belief.prize_count == 0 for _, belief in beliefs.beliefs)
        return 4

    assert len(physical.physical.prize_instance_ids) == 2
    assert board.ledger.instance("jirachi").zone == "prize"
    assert "dream-target" in {row.pokemon_id for row in board.pokemon}
    for observer in ("actor", "opponent"):
        belief = beliefs.belief_for(observer)
        assert belief.prize_probability_at(0, "J") == 1.0
        assert belief.prize_probability_at(1, None) == 1.0
    return 2


def main() -> None:
    assert Counter((run_branch(heads=False), run_branch(heads=True))) == {
        2: 1, 4: 1,
    }
    print("Peonia-seeded E-31 observer-physical bridge passed: both coin branches")


if __name__ == "__main__":
    main()
