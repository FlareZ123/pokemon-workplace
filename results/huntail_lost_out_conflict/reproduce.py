"""Reproduce a card-text-grounded Huntail / Tyranitar-GX KO routing conflict.

Card prints:
- Tyranitar-GX (sm8-121): Lost Out; Dusty Ruckus 130
- Lapras (bw4-25): Basic Water, HP 100, Lightning Weakness
- Huntail (sv10-55): Stage 1 Water; Diver's Catch

This computes conditional endpoint states given two effect orders. It does
not decide which player has authority to choose or whether either specific
order is legal under a particular tournament's official ruling.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import (
    AttachmentKind, BoardPokemon, PokemonCard, make_state
)
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance
)
from ko_order_outcome_space import ko_order_outcomes
from ko_order_signature_projection import project_with_zone_signatures
from ko_order_terminal_projection import project_terminal_outcomes
from knockout_redirection_ordering import resolve_ordered_programs, resolved_route_map
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ALL_TO_LOST, ATTACHED_ENERGY_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def build_pending():
    initial = IdentityLedger(
        ZoneCountState.from_mapping({
            ("lapras", "hand"): 1,
            ("clamperl", "hand"): 1,
            ("huntail", "hand"): 1,
            ("basic-water", "hand"): 2,
            ("double-colorless", "hand"): 1,
        })
    )
    ledger = initial
    for card_class, card_name, instance_id, holder_id in (
        ("lapras", "Lapras", "lapras-a", "a"),
        ("clamperl", "Clamperl", "clamperl-b", "b"),
        ("huntail", "Huntail", "huntail-b", "b"),
    ):
        ledger = materialize(
            ledger, card_class=card_class, card_name=card_name,
            source_zone="hand", instance_id=instance_id,
        )
        ledger = put_in_play_instance(ledger, instance_id, holder_id)

    board = make_state(
        (
            BoardPokemon(
                "a", (PokemonCard("lapras-a", "Lapras"),), retreat_cost=2
            ),
            BoardPokemon(
                "b",
                (
                    PokemonCard("clamperl-b", "Clamperl"),
                    PokemonCard(
                        "huntail-b", "Huntail", evolves_from="Clamperl"
                    ),
                ),
                retreat_cost=1,
            ),
        ),
        active_id="a",
    )
    state = StackBoardMaterialState(ledger, board)
    for instance_id in ("water-1", "water-2"):
        state = attach_from_hand(
            state, pokemon_id="a", card_class="basic-water",
            instance_id=instance_id, card_name="Basic Water Energy",
            kind=AttachmentKind.ENERGY, retreat_units=1,
        )
        assert state is not None
    state = attach_from_hand(
        state, pokemon_id="a", card_class="double-colorless",
        instance_id="dce-a", card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY, retreat_units=2,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    pending = prepare_knock_out_batch(state, ("a",))
    assert pending is not None
    return initial, pending


def main():
    # Printed attack damage exceeds defender HP without applying Weakness
    # (Tyranitar is Darkness; Lapras's Weakness is Lightning).
    tyranitar_dusty_ruckus_damage = 130
    lapras_hp = 100
    assert tyranitar_dusty_ruckus_damage >= lapras_hp

    initial, pending = build_pending()
    # Source conditions: the attacking Tyranitar's attack KO'd the opposing
    # Water Lapras and the defending player has Huntail on the Bench with
    # its relevant Ability functioning. All Basic Water targets remain
    # attached at the KO trigger boundary.
    lost = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=ALL_TO_LOST
    )
    recovered = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=ATTACHED_ENERGY_TO_HAND,
        selected_energy_ids=("water-1", "water-2"),
    )
    assert lost is not None and recovered is not None
    programs = {"tyranitar-lost-out": lost, "huntail-divers-catch": recovered}

    # Both sequences are hypothetical *conditional* implementations of the
    # competing destination programs; authority is deliberately upstream.
    outcomes = ko_order_outcomes(programs)
    assert len(outcomes) == 2
    assert sum(row.order_count for row in outcomes) == 2
    full = project_terminal_outcomes(pending, programs, promote_id="b")
    compressed = project_with_zone_signatures(
        pending, programs, promote_id="b"
    )
    assert compressed.outcomes == full
    assert compressed.physical_disposals == 2

    for route in outcomes:
        order = route.witness_order
        resolved = resolve_ordered_programs(programs, order)
        assert resolved is not None
        terminal = discard_pending_with_zone_routes(
            pending, promote_id="b",
            destinations=resolved_route_map(resolved),
        )
        assert terminal is not None
        assert terminal.board is not None
        assert terminal.board.active_id == "b"
        assert [row.pokemon_id for row in terminal.board.pokemon] == ["b"]
        assert_conserved(initial, terminal.ledger)
        assert terminal.ledger.exchangeable.count("lapras", "lost_zone") == 1
        assert terminal.ledger.exchangeable.count(
            "double-colorless", "lost_zone"
        ) == 1
        if order[0] == "huntail-divers-catch":
            assert terminal.ledger.exchangeable.count(
                "basic-water", "hand"
            ) == 2
            assert terminal.ledger.exchangeable.count(
                "basic-water", "lost_zone"
            ) == 0
        else:
            assert terminal.ledger.exchangeable.count(
                "basic-water", "hand"
            ) == 0
            assert terminal.ledger.exchangeable.count(
                "basic-water", "lost_zone"
            ) == 2

    print(
        "Huntail / Tyranitar-GX conditional KO conflict verified: "
        "Water goes to hand or Lost Zone according to supplied effect order; "
        "both conserve cards and leave Huntail Active"
    )


if __name__ == "__main__":
    main()
