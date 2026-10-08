"""Reproduce officially described Aegislash / Tyranitar-GX order branches.

The Japan Q&A says the knocked-out Aegislash owner chooses whether Durable
Blade returns the Pokemon to hand or Lost Out sends it to the Lost Zone first.
Other regional interpretations are modeled as separate source policies.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_redirection_authorized_order import (
    AuthorizedOrderStatus, OrderingPlayers, authorize_and_resolve_order
)
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    JAPAN_LOST_OUT_AEGISLASH_QA,
    LOST_OUT_AEGISLASH,
    TPCI_FEB_2026,
    OrderingContext,
    TimingWindow,
    TriggerKind,
)
from knockout_redirection_ordering import resolved_route_map
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ALL_TO_LOST, SELF_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending


def main():
    initial, pending = build_pending()
    returned = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=SELF_TO_HAND
    )
    lost = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=ALL_TO_LOST
    )
    assert returned is not None and lost is not None
    programs = {"durable-blade": returned, "lost-out": lost}
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=1,
        interaction_id=LOST_OUT_AEGISLASH,
    )

    for ordering in (
        ("durable-blade", "lost-out"),
        ("lost-out", "durable-blade"),
    ):
        result = authorize_and_resolve_order(
            programs,
            ordering,
            context=context,
            source_ids=(JAPAN_LOST_OUT_AEGISLASH_QA,),
            players=OrderingPlayers(
                current_player="attacker", knocked_out_pokemon_owner="defender"
            ),
            submitted_by="defender",
        )
        assert result.status == AuthorizedOrderStatus.RESOLVED
        assert result.chooser == "defender"
        assert result.resolutions is not None
        state = discard_pending_with_zone_routes(
            pending, promote_id="b", destinations=resolved_route_map(result.resolutions)
        )
        assert state is not None and state.board is not None
        assert state.board.active_id == "b"
        assert state.ledger.totals() == initial.totals()

        pokemon_zone = "hand" if ordering[0] == "durable-blade" else "lost_zone"
        attachment_zone = "discard" if pokemon_zone == "hand" else "lost_zone"
        for card_class in ("honedge", "doublade", "aegislash"):
            assert state.ledger.exchangeable.count(card_class, pokemon_zone) == 1
        for card_class, count in (
            ("basic-water", 2),
            ("dce", 1),
            ("muscle-band", 1),
        ):
            assert state.ledger.exchangeable.count(card_class, attachment_zone) == count

    # Japan Q&A's owner selection and the broader TPCi 2026 current-player
    # claim disagree if the attacker and defender are different players.
    conflict = authorize_and_resolve_order(
        programs,
        ("lost-out", "durable-blade"),
        context=context,
        source_ids=(JAPAN_LOST_OUT_AEGISLASH_QA, TPCI_FEB_2026),
        players=OrderingPlayers(
            current_player="attacker", knocked_out_pokemon_owner="defender"
        ),
        submitted_by="attacker",
    )
    assert conflict.status == AuthorizedOrderStatus.AUTHORITY_CONFLICT
    assert conflict.resolutions is None

    # No contradiction exists when both role descriptions identify one
    # concrete player, despite the unresolved abstract rules precedence.
    aligned = authorize_and_resolve_order(
        programs,
        ("lost-out", "durable-blade"),
        context=context,
        source_ids=(JAPAN_LOST_OUT_AEGISLASH_QA, TPCI_FEB_2026),
        players=OrderingPlayers(
            current_player="defender", knocked_out_pokemon_owner="defender"
        ),
        submitted_by="defender",
    )
    assert aligned.status == AuthorizedOrderStatus.RESOLVED

    # The v3.4 multi-KO wording alone does not prescribe an order for this
    # single-KO event.
    narrow = authorize_and_resolve_order(
        programs,
        ("durable-blade", "lost-out"),
        context=context,
        source_ids=(ADVANCED_RULEBOOK_3_4,),
        players=OrderingPlayers(
            current_player="attacker", knocked_out_pokemon_owner="defender"
        ),
        submitted_by="attacker",
    )
    assert narrow.status == AuthorizedOrderStatus.NO_AUTHORITY_CLAIMS

    # The card-specific Japan claim must not leak into unrelated KOs.
    unrelated_context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        interaction_id="unrelated",
    )
    unrelated = authorize_and_resolve_order(
        programs,
        ("lost-out", "durable-blade"),
        context=unrelated_context,
        source_ids=(JAPAN_LOST_OUT_AEGISLASH_QA,),
        players=OrderingPlayers(
            current_player="attacker", knocked_out_pokemon_owner="defender"
        ),
        submitted_by="defender",
    )
    assert unrelated.status == AuthorizedOrderStatus.NO_AUTHORITY_CLAIMS
    print(
        "Official Japan Tyranitar-GX / Aegislash conditional KO destinations "
        "and sourced ordering authority passed"
    )


if __name__ == "__main__":
    main()
