"""Verify source-conflicted Lost City / Lost Out can have invariant KO outcome."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import (
    AttachmentKind, BoardPokemon, PokemonCard, make_state,
)
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from ko_authority_invariant_projection import (
    PhysicalCertainty, project_authority_neutral_ko,
)
from ko_redirection_authorized_order import (
    AuthorizedOrderStatus, authorize_and_resolve_order,
)
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    JAPAN_LOST_CITY_QA,
    LOST_CITY_LOST_OUT,
    TPCI_FEB_2026,
    OrderingContext, TimingWindow, TriggerKind,
)
from knockout_redirection_ordering import (
    resolve_ordered_programs, resolved_route_map,
)
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ALL_TO_LOST, POKEMON_TO_LOST
from knockout_zone_routing import discard_pending_with_zone_routes
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from source_order_chooser import ConcreteChooserStatus, OrderingPlayers
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def setup(attached_water_count):
    counts = {
        ("lapras", "hand"): 1,
        ("bidoof", "hand"): 1,
    }
    if attached_water_count:
        counts[("basic-water", "hand")] = attached_water_count
    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = initial
    for cls, name, instance, holder in (
        ("lapras", "Lapras", "lapras-a", "a"),
        ("bidoof", "Bidoof", "bidoof-b", "b"),
    ):
        ledger = materialize(
            ledger, card_class=cls, card_name=name,
            source_zone="hand", instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, holder)
    state = StackBoardMaterialState(
        ledger, make_state(
            (
                BoardPokemon(
                    "a", (PokemonCard("lapras-a", "Lapras"),), retreat_cost=2
                ),
                BoardPokemon(
                    "b", (PokemonCard("bidoof-b", "Bidoof"),), retreat_cost=1
                ),
            ),
            active_id="a",
        )
    )
    for i in range(attached_water_count):
        state = attach_from_hand(
            state, pokemon_id="a", card_class="basic-water",
            instance_id=f"water-{i}", card_name="Basic Water Energy",
            kind=AttachmentKind.ENERGY, retreat_units=1,
        )
        assert state is not None
    assert_conserved(initial, state.ledger)
    pending = prepare_knock_out_batch(state, ("a",))
    assert pending is not None
    lost_city = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=POKEMON_TO_LOST,
    )
    lost_out = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=ALL_TO_LOST,
    )
    assert lost_city is not None and lost_out is not None
    return initial, pending, {"lost-city": lost_city, "lost-out": lost_out}


def main():
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=1,
        interaction_id=LOST_CITY_LOST_OUT,
    )
    selected_sources = (JAPAN_LOST_CITY_QA, TPCI_FEB_2026)
    players = OrderingPlayers(
        current_player="attacker", knocked_out_pokemon_owner="defender"
    )

    for count in range(5):
        initial, pending, programs = setup(count)
        verified = project_authority_neutral_ko(
            pending, programs, context=context,
            source_ids=selected_sources, players=players, promote_id="b"
        )
        assert verified.authority.status == ConcreteChooserStatus.AUTHORITY_CONFLICT
        assert verified.authority.chooser is None
        assert verified.candidate_total_orders == 2

        # Existing authorization must not accept either submitted order
        # because the selected source interpretations name different players.
        for order in (("lost-city", "lost-out"), ("lost-out", "lost-city")):
            rejected = authorize_and_resolve_order(
                programs, order, context=context, source_ids=selected_sources,
                players=players, submitted_by="attacker",
            )
            assert rejected.status == AuthorizedOrderStatus.AUTHORITY_CONFLICT
            raw = resolve_ordered_programs(programs, order)
            assert raw is not None
            branch = discard_pending_with_zone_routes(
                pending, promote_id="b",
                destinations=resolved_route_map(raw),
            )
            assert branch is not None
            assert_conserved(initial, branch.ledger)
            assert branch.ledger.exchangeable.count("lapras", "lost_zone") == 1
            assert branch.board is not None and branch.board.active_id == "b"
            zone = "discard" if order[0] == "lost-city" else "lost_zone"
            assert branch.ledger.exchangeable.count("basic-water", zone) == count

        if count == 0:
            assert verified.certainty == PhysicalCertainty.INVARIANT
            assert verified.terminal_state is not None
            assert verified.possible_terminal_states == 1
            assert verified.possible_instance_routes == 1
            assert verified.terminal_state.board is not None
            assert verified.terminal_state.board.active_id == "b"
            assert_conserved(initial, verified.terminal_state.ledger)
        else:
            assert verified.certainty == PhysicalCertainty.ORDER_SENSITIVE
            assert verified.terminal_state is None
            assert verified.possible_terminal_states == 2
            assert verified.possible_instance_routes == 2

    # A concrete chooser can be identified under one source, but absent an
    # actual chosen order an attached-Energy state remains order-sensitive.
    _, pending, programs = setup(1)
    japan = project_authority_neutral_ko(
        pending, programs, context=context,
        source_ids=(JAPAN_LOST_CITY_QA,), players=players, promote_id="b",
    )
    assert japan.authority.status == ConcreteChooserStatus.RESOLVED
    assert japan.authority.chooser == "defender"
    assert japan.certainty == PhysicalCertainty.ORDER_SENSITIVE
    assert japan.terminal_state is None

    # A source providing no chooser can still coexist with an invariant
    # physical projection, without asserting order authorization.
    _, empty_pending, empty_programs = setup(0)
    unsupported = project_authority_neutral_ko(
        empty_pending, empty_programs, context=context,
        source_ids=(ADVANCED_RULEBOOK_3_4,),
        players=players, promote_id="b",
    )
    assert unsupported.authority.status == ConcreteChooserStatus.NO_AUTHORITY_CLAIMS
    assert unsupported.certainty == PhysicalCertainty.INVARIANT
    assert unsupported.terminal_state is not None

    # An externally imposed precedence can also collapse an otherwise
    # order-sensitive pair. The precedence below is a synthetic constraint,
    # and is not presented as an official Lost City / Lost Out policy.
    restricted = project_authority_neutral_ko(
        pending, programs, context=context,
        source_ids=selected_sources, players=players, promote_id="b",
        precedences=(("lost-city", "lost-out"),),
    )
    assert restricted.authority.status == ConcreteChooserStatus.AUTHORITY_CONFLICT
    assert restricted.certainty == PhysicalCertainty.INVARIANT
    assert restricted.terminal_state is not None
    assert restricted.terminal_state.ledger.exchangeable.count(
        "basic-water", "discard"
    ) == 1
    assert restricted.candidate_total_orders == 1

    print(
        "Authority-neutral KO projection passed: official Lost City / Lost Out "
        "source conflict yields a provably invariant state without attachments "
        "and two distinct states with any Basic Water attachments"
    )


if __name__ == "__main__":
    main()
