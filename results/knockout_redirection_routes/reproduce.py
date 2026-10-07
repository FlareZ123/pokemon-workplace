"""Reproduce executable Knock Out redirection routing for all classified signatures."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import AttachmentKind, BoardPokemon, PokemonCard, make_state
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import (
    ALL_TO_LOST,
    ATTACHED_ENERGY_TO_HAND,
    POKEMON_TO_LOST,
    SELF_TO_HAND,
)
from knockout_zone_routing import discard_pending_with_zone_routes
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def put_pokemon_card(
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


def build_pending():
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("honedge", "hand"): 1,
                ("doublade", "hand"): 1,
                ("aegislash", "hand"): 1,
                ("bidoof", "hand"): 1,
                ("basic-water", "hand"): 2,
                ("dce", "hand"): 1,
                ("muscle-band", "hand"): 1,
            }
        )
    )

    ledger = initial
    for card_class, card_name, instance_id in (
        ("honedge", "Honedge", "honedge-a"),
        ("doublade", "Doublade", "doublade-a"),
        ("aegislash", "Aegislash", "aegislash-a"),
    ):
        ledger = put_pokemon_card(
            ledger,
            card_class=card_class,
            card_name=card_name,
            instance_id=instance_id,
            pokemon_id="a",
        )

    ledger = put_pokemon_card(
        ledger,
        card_class="bidoof",
        card_name="Bidoof",
        instance_id="bidoof-b",
        pokemon_id="b",
    )

    board = make_state(
        (
            BoardPokemon(
                "a",
                (
                    PokemonCard("honedge-a", "Honedge"),
                    PokemonCard("doublade-a", "Doublade", evolves_from="Honedge"),
                    PokemonCard("aegislash-a", "Aegislash", evolves_from="Doublade"),
                ),
                retreat_cost=2,
            ),
            BoardPokemon(
                "b",
                (PokemonCard("bidoof-b", "Bidoof"),),
                retreat_cost=1,
            ),
        ),
        active_id="a",
    )
    state = StackBoardMaterialState(ledger, board)

    for instance_id in ("water-1", "water-2"):
        state = attach_from_hand(
            state,
            pokemon_id="a",
            card_class="basic-water",
            instance_id=instance_id,
            card_name="Basic Water Energy",
            kind=AttachmentKind.ENERGY,
            retreat_units=1,
        )
        assert state is not None

    state = attach_from_hand(
        state,
        pokemon_id="a",
        card_class="dce",
        instance_id="dce-a",
        card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=2,
    )
    assert state is not None

    state = attach_from_hand(
        state,
        pokemon_id="a",
        card_class="muscle-band",
        instance_id="band-a",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)

    pending = prepare_knock_out_batch(state, ("a",))
    assert pending is not None
    return initial, pending


def dispose(initial, pending, signature, selected=()):
    routes = destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=signature,
        selected_energy_ids=selected,
    )
    assert routes is not None
    result = discard_pending_with_zone_routes(
        pending,
        promote_id="b",
        destinations=routes,
    )
    assert result is not None
    assert result.board is not None
    assert result.board.active_id == "b"
    assert [row.instance_id for row in result.ledger.instances] == ["bidoof-b"]
    assert_conserved(initial, result.ledger)
    return result


def main() -> None:
    initial, pending = build_pending()

    # sm11-95 Aegislash / Durable Blade:
    # the evolved Pokemon stack returns to hand, attachments discard.
    hand = dispose(initial, pending, SELF_TO_HAND)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert hand.ledger.exchangeable.count(card_class, "hand") == 1
    assert hand.ledger.exchangeable.count("basic-water", "discard") == 2
    assert hand.ledger.exchangeable.count("dce", "discard") == 1
    assert hand.ledger.exchangeable.count("muscle-band", "discard") == 1

    # sm8-121 Tyranitar-GX / Lost Out:
    # the Pokemon stack and every attachment go to the Lost Zone.
    all_lost = dispose(initial, pending, ALL_TO_LOST)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert all_lost.ledger.exchangeable.count(card_class, "lost_zone") == 1
    assert all_lost.ledger.exchangeable.count("basic-water", "lost_zone") == 2
    assert all_lost.ledger.exchangeable.count("dce", "lost_zone") == 1
    assert all_lost.ledger.exchangeable.count("muscle-band", "lost_zone") == 1

    # swsh11-161 Lost City:
    # the Pokemon stack goes to the Lost Zone and attachments discard.
    pokemon_lost = dispose(initial, pending, POKEMON_TO_LOST)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert pokemon_lost.ledger.exchangeable.count(card_class, "lost_zone") == 1
    assert pokemon_lost.ledger.exchangeable.count("basic-water", "discard") == 2
    assert pokemon_lost.ledger.exchangeable.count("dce", "discard") == 1
    assert pokemon_lost.ledger.exchangeable.count("muscle-band", "discard") == 1

    # sv10-55 Huntail / Diver's Catch:
    # card semantics select the two Basic Water Energy instances.
    energy_hand = dispose(
        initial,
        pending,
        ATTACHED_ENERGY_TO_HAND,
        ("water-1", "water-2"),
    )
    for card_class in ("honedge", "doublade", "aegislash"):
        assert energy_hand.ledger.exchangeable.count(card_class, "discard") == 1
    assert energy_hand.ledger.exchangeable.count("basic-water", "hand") == 2
    assert energy_hand.ledger.exchangeable.count("dce", "discard") == 1
    assert energy_hand.ledger.exchangeable.count("muscle-band", "discard") == 1

    # Signature routing rejects malformed semantic inputs.
    assert destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=ATTACHED_ENERGY_TO_HAND,
        selected_energy_ids=("band-a",),
    ) is None
    assert destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=SELF_TO_HAND,
        selected_energy_ids=("water-1",),
    ) is None
    assert destinations_for_redirection(
        pending,
        pokemon_id="b",
        routing_signature=SELF_TO_HAND,
    ) is None
    assert destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature="unknown",
    ) is None

    print("Knock Out redirection routing regressions passed")


if __name__ == "__main__":
    main()
