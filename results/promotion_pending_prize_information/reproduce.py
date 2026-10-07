"""Reproduce post-KO Prize-before-promotion timing and conservation."""

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
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_pending_take import (
    resolve_next_pending_prize,
    stage_prize_takes_with_observers,
)
from prize_top_swap_belief import TopPrizeJointBelief
from promotion_pending_conservation import (
    PostKnockOutPromotionContext,
    PostKnockOutStage,
    advance_after_prizes,
    choose_promotion,
    dispose_pending_before_promotion,
    finalize_promotions,
    next_promotion_player,
    replace_player_state,
    unresolved_prize_count,
)
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import TopPrizePhysicalState


def build_player(
    prefix: str,
    bench_roles: tuple[str, ...],
    *,
    with_hidden_prize: bool,
) -> tuple[IdentityLedger, StackBoardMaterialState, str | None, str | None]:
    counts = {
        (f"{prefix}-active-class", "hand"): 1,
        **{
            (f"{prefix}-{role}-class", "hand"): 1
            for role in bench_roles
        },
    }
    if with_hidden_prize:
        counts[(f"{prefix}-other-class", "deck_top")] = 1
        counts[(f"{prefix}-switch-class", "prize")] = 1

    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = materialize(
        initial,
        card_class=f"{prefix}-active-class",
        card_name=f"{prefix} Active Pokemon",
        source_zone="hand",
        instance_id=f"{prefix}-active-card",
    )
    ledger = put_in_play_instance(
        ledger,
        f"{prefix}-active-card",
        f"{prefix}-active",
    )

    board_rows = [
        BoardPokemon(
            f"{prefix}-active",
            (PokemonCard(f"{prefix}-active-card", f"{prefix} Active Pokemon"),),
            retreat_cost=1,
        )
    ]

    for role in bench_roles:
        instance_id = f"{prefix}-{role}-card"
        object_id = f"{prefix}-{role}"
        ledger = materialize(
            ledger,
            card_class=f"{prefix}-{role}-class",
            card_name=f"{prefix} {role}",
            source_zone="hand",
            instance_id=instance_id,
        )
        ledger = put_in_play_instance(ledger, instance_id, object_id)
        board_rows.append(
            BoardPokemon(
                object_id,
                (PokemonCard(instance_id, f"{prefix} {role}"),),
                retreat_cost=1,
            )
        )

    top_id = None
    prize_id = None
    if with_hidden_prize:
        top_id = f"{prefix}-top-card"
        prize_id = f"{prefix}-prize-card"
        ledger = materialize(
            ledger,
            card_class=f"{prefix}-other-class",
            card_name="Other Card",
            source_zone="deck_top",
            instance_id=top_id,
        )
        ledger = materialize(
            ledger,
            card_class=f"{prefix}-switch-class",
            card_name="Switch",
            source_zone="prize",
            instance_id=prize_id,
        )

    state = StackBoardMaterialState(
        ledger,
        make_state(tuple(board_rows), active_id=f"{prefix}-active"),
    )
    assert_conserved(initial, state.ledger)
    return initial, state, top_id, prize_id


def main() -> None:
    initial_a, state_a, _top_a, _prize_a = build_player(
        "a",
        ("bench",),
        with_hidden_prize=False,
    )
    initial_b, state_b, top_b, prize_b = build_player(
        "b",
        ("pivot", "attacker"),
        with_hidden_prize=True,
    )
    assert top_b is not None
    assert prize_b is not None

    pending_a = prepare_knock_out_batch(state_a, ("a-active",))
    pending_b = prepare_knock_out_batch(state_b, ("b-active",))
    assert pending_a is not None
    assert pending_b is not None

    after_ko_a = dispose_pending_before_promotion(pending_a)
    after_ko_b = dispose_pending_before_promotion(pending_b)

    assert after_ko_a.active_id is None
    assert after_ko_b.active_id is None
    assert after_ko_a.promotion_candidates == ("a-bench",)
    assert after_ko_b.promotion_candidates == ("b-pivot", "b-attacker")
    assert after_ko_b.ledger.exchangeable.count(
        "b-active-class", "discard"
    ) == 1

    context = PostKnockOutPromotionContext(
        (("A", after_ko_a), ("B", after_ko_b)),
        next_player_id="B",
    )
    assert context.stage == PostKnockOutStage.PRIZES

    assert choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-pivot",
    ) is None

    physical_b = TopPrizePhysicalState(
        after_ko_b.ledger,
        top_b,
        (prize_b,),
        (False,),
    )
    prior = TopPrizeJointBelief(
        ("Switch", "Other"),
        (False,),
        (
            (("Other", ("Switch",)), 0.5),
            (("Switch", ("Other",)), 0.5),
        ),
    )
    observers = ObserverTopPrizeBeliefs(
        (("B", prior), ("A", prior))
    )

    staged = stage_prize_takes_with_observers(
        physical_b,
        observers,
        actor_id="B",
        positions=(0,),
        group_by_card_class={
            "b-switch-class": "Switch",
            "b-other-class": "Other",
        },
    )
    b_with_pending_prize = after_ko_b.with_ledger(
        staged.after_pending.physical.ledger
    )
    context = replace_player_state(
        context,
        player_id="B",
        state=b_with_pending_prize,
    )

    assert unresolved_prize_count(context) == 1
    assert advance_after_prizes(context, game_continues=True) is None
    assert choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-pivot",
    ) is None

    actor_belief = staged.beliefs_after.belief_for("B")
    opponent_belief = staged.beliefs_after.belief_for("A")
    assert actor_belief.top_probability("Other") == 1.0
    assert opponent_belief.top_probability("Other") == 0.5

    resolved_prize = resolve_next_pending_prize(staged.after_pending)
    b_after_prize = b_with_pending_prize.with_ledger(
        resolved_prize.after.physical.ledger
    )
    context = replace_player_state(
        context,
        player_id="B",
        state=b_after_prize,
    )
    assert unresolved_prize_count(context) == 0
    assert b_after_prize.ledger.instance(prize_b).zone == "hand"

    context = advance_after_prizes(context, game_continues=True)
    assert context is not None
    assert context.stage == PostKnockOutStage.PROMOTION
    assert next_promotion_player(context) == "B"

    observed_prize_group = "Switch"
    b_choice = "b-pivot" if observed_prize_group == "Switch" else "b-attacker"
    after_b = choose_promotion(
        context,
        player_id="B",
        pokemon_id=b_choice,
    )
    assert after_b is not None
    assert after_b.state_for("B").active_id == "b-pivot"
    assert next_promotion_player(after_b) == "A"

    after_a = choose_promotion(
        after_b,
        player_id="A",
        pokemon_id="a-bench",
    )
    assert after_a is not None

    final = finalize_promotions(after_a)
    assert final is not None
    final_by_player = dict(final)
    assert final_by_player["B"].board is not None
    assert final_by_player["B"].board.active_id == "b-pivot"
    assert final_by_player["A"].board is not None
    assert final_by_player["A"].board.active_id == "a-bench"

    assert_conserved(initial_a, final_by_player["A"].ledger)
    assert_conserved(initial_b, final_by_player["B"].ledger)

    prior_switch = 0.5
    fixed_policy_success = max(prior_switch, 1.0 - prior_switch)
    informed_policy_success = 1.0
    assert fixed_policy_success == 0.5
    assert informed_policy_success == 1.0

    print("promotion-pending Prize-information regressions passed")
    print(f"fixed pre-Prize promotion utility: {fixed_policy_success:.1%}")
    print(f"post-Prize informed promotion utility: {informed_policy_success:.1%}")


if __name__ == "__main__":
    main()
