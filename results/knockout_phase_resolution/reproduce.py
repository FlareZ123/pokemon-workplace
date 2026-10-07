"""Reproduce Knock Out routing and cross-player ordering regressions."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from knockout_phase_resolution import (
    AttachmentRoute,
    KnockOutTrigger,
    PlayerKnockOutBatch,
    TwoPlayerKnockOutPhase,
    choose_knock_out_trigger_order,
    players_requiring_promotion,
    promotion_choice_order,
    route_pending_attachments,
)
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import (
    discard_pending_knock_out_batch,
    prepare_knock_out_batch,
)
from stack_knockout_conservation import (
    StackBoardMaterialState,
    attach_from_hand,
)


def put_pokemon(
    ledger: IdentityLedger,
    *,
    card_class: str,
    card_name: str,
    instance_id: str,
    pokemon_id: str,
) -> IdentityLedger:
    ledger = materialize(
        ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone="hand",
        instance_id=instance_id,
    )
    return put_in_play_instance(ledger, instance_id, pokemon_id)


def build_player_a() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("a-active", "hand"): 1,
                ("a-bench", "hand"): 1,
                ("water", "hand"): 1,
                ("dce", "hand"): 1,
            }
        )
    )
    ledger = put_pokemon(
        initial,
        card_class="a-active",
        card_name="Water Active",
        instance_id="a-active-copy",
        pokemon_id="a-active",
    )
    ledger = put_pokemon(
        ledger,
        card_class="a-bench",
        card_name="A Bench",
        instance_id="a-bench-copy",
        pokemon_id="a-bench",
    )
    board = make_state(
        (
            BoardPokemon(
                "a-active",
                (PokemonCard("a-active-copy", "Water Active"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "a-bench",
                (PokemonCard("a-bench-copy", "A Bench"),),
                retreat_cost=1,
            ),
        ),
        active_id="a-active",
    )
    state = StackBoardMaterialState(ledger, board)
    state = attach_from_hand(
        state,
        pokemon_id="a-active",
        card_class="water",
        instance_id="water-copy",
        card_name="Basic Water Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=1,
    )
    assert state is not None
    state = attach_from_hand(
        state,
        pokemon_id="a-active",
        card_class="dce",
        instance_id="dce-copy",
        card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=2,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def build_player_b() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("b-active", "hand"): 1,
                ("b-bench", "hand"): 1,
                ("band", "hand"): 1,
            }
        )
    )
    ledger = put_pokemon(
        initial,
        card_class="b-active",
        card_name="B Active",
        instance_id="b-active-copy",
        pokemon_id="b-active",
    )
    ledger = put_pokemon(
        ledger,
        card_class="b-bench",
        card_name="B Bench",
        instance_id="b-bench-copy",
        pokemon_id="b-bench",
    )
    board = make_state(
        (
            BoardPokemon(
                "b-active",
                (PokemonCard("b-active-copy", "B Active"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "b-bench",
                (PokemonCard("b-bench-copy", "B Bench"),),
                retreat_cost=1,
            ),
        ),
        active_id="b-active",
    )
    state = StackBoardMaterialState(ledger, board)
    state = attach_from_hand(
        state,
        pokemon_id="b-active",
        card_class="band",
        instance_id="band-copy",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def main() -> None:
    initial_a, state_a = build_player_a()
    initial_b, state_b = build_player_b()

    pending_a = prepare_knock_out_batch(state_a, ("a-active",))
    pending_b = prepare_knock_out_batch(state_b, ("b-active",))
    assert pending_a is not None
    assert pending_b is not None

    phase = TwoPlayerKnockOutPhase(
        (
            PlayerKnockOutBatch("A", pending_a),
            PlayerKnockOutBatch("B", pending_b),
        ),
        current_turn_player="A",
        next_turn_player="B",
    )

    triggers = (
        KnockOutTrigger(
            "divers-catch",
            "A",
            "route Basic Water Energy to hand instead of discard",
        ),
        KnockOutTrigger(
            "retaliation",
            "B",
            "a second simultaneous Knock Out trigger",
        ),
    )
    assert choose_knock_out_trigger_order(
        phase,
        triggers,
        ("retaliation", "divers-catch"),
        choosing_player="B",
    ) is None
    ordered = choose_knock_out_trigger_order(
        phase,
        triggers,
        ("retaliation", "divers-catch"),
        choosing_player="A",
    )
    assert ordered is not None
    assert tuple(row.trigger_id for row in ordered) == (
        "retaliation",
        "divers-catch",
    )

    routed_a = route_pending_attachments(
        pending_a,
        (AttachmentRoute("water-copy", "hand"),),
    )
    assert routed_a is not None
    assert routed_a.state.board is not None
    assert {
        attachment.card_id
        for attachment in routed_a.state.board.get("a-active").attachments
    } == {"dce-copy"}
    assert routed_a.state.ledger.exchangeable.count("water", "hand") == 1
    assert routed_a.state.ledger.exchangeable.count("water", "discard") == 0
    assert route_pending_attachments(
        pending_a,
        (
            AttachmentRoute("water-copy", "hand"),
            AttachmentRoute("water-copy", "discard"),
        ),
    ) is None
    assert route_pending_attachments(
        pending_a,
        (AttachmentRoute("missing-copy", "hand"),),
    ) is None
    assert_conserved(initial_a, routed_a.state.ledger)

    routed_phase = TwoPlayerKnockOutPhase(
        (
            PlayerKnockOutBatch("A", routed_a),
            PlayerKnockOutBatch("B", pending_b),
        ),
        current_turn_player="A",
        next_turn_player="B",
    )
    assert players_requiring_promotion(routed_phase) == ("A", "B")
    assert promotion_choice_order(routed_phase) == ("B", "A")

    resolved_a = discard_pending_knock_out_batch(
        routed_a,
        promote_id="a-bench",
    )
    resolved_b = discard_pending_knock_out_batch(
        pending_b,
        promote_id="b-bench",
    )
    assert resolved_a is not None
    assert resolved_b is not None
    assert resolved_a.board is not None
    assert resolved_b.board is not None
    assert resolved_a.board.active_id == "a-bench"
    assert resolved_b.board.active_id == "b-bench"
    assert resolved_a.ledger.exchangeable.count("water", "hand") == 1
    assert resolved_a.ledger.exchangeable.count("dce", "discard") == 1
    assert resolved_b.ledger.exchangeable.count("band", "discard") == 1
    assert_conserved(initial_a, resolved_a.ledger)
    assert_conserved(initial_b, resolved_b.ledger)

    terminal_b = prepare_knock_out_batch(
        state_b,
        ("b-active", "b-bench"),
    )
    assert terminal_b is not None
    one_sided_phase = TwoPlayerKnockOutPhase(
        (
            PlayerKnockOutBatch("A", pending_a),
            PlayerKnockOutBatch("B", terminal_b),
        ),
        current_turn_player="A",
        next_turn_player="B",
    )
    assert players_requiring_promotion(one_sided_phase) == ("A",)
    assert promotion_choice_order(one_sided_phase) == ("A",)

    print("Knock Out phase routing and ordering regressions passed")


if __name__ == "__main__":
    main()
