"""Reproduce Knock Out zone routing with Huntail-like Energy recovery."""

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
from knockout_zone_routing import discard_pending_with_zone_routes
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


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


def main() -> None:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("squirtle", "hand"): 1,
                ("bidoof", "hand"): 1,
                ("basic-water", "hand"): 2,
                ("dce", "hand"): 1,
            }
        )
    )

    ledger = put_pokemon(
        initial,
        card_class="squirtle",
        card_name="Squirtle",
        instance_id="squirtle-a",
        pokemon_id="a",
    )
    ledger = put_pokemon(
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
                (PokemonCard("squirtle-a", "Squirtle"),),
                retreat_cost=1,
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
    assert_conserved(initial, state.ledger)

    pending = prepare_knock_out_batch(state, ("a",))
    assert pending is not None

    # The trigger layer can still inspect all attached cards before disposal.
    assert pending.state.board is not None
    assert {
        card.card_id
        for card in pending.state.board.get("a").attachments
    } == {"water-1", "water-2", "dce-a"}

    routed = discard_pending_with_zone_routes(
        pending,
        promote_id="b",
        destinations={
            "water-1": "hand",
            "water-2": "hand",
        },
    )
    assert routed is not None
    assert routed.board is not None
    assert routed.board.active_id == "b"
    assert routed.ledger.exchangeable.count("basic-water", "hand") == 2
    assert routed.ledger.exchangeable.count("dce", "discard") == 1
    assert routed.ledger.exchangeable.count("squirtle", "discard") == 1
    assert [row.instance_id for row in routed.ledger.instances] == ["bidoof-b"]
    assert_conserved(initial, routed.ledger)

    # Board-bound destinations are rejected because disposed instances are
    # dematerialized by this adapter.
    assert discard_pending_with_zone_routes(
        pending,
        promote_id="b",
        destinations={"water-1": "attached"},
    ) is None

    print("Knock Out zone-routing regressions passed")


if __name__ == "__main__":
    main()
