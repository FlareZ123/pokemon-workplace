"""Reproduce source-authorized KO redirection end to end."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_redirection_authorized_order import (
    AuthorizedOrderStatus,
    OrderingPlayers,
    authorize_and_resolve_order,
)
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    ASIA_LOST_CITY_REUNICLUS_QA,
    JAPAN_LOST_CITY_QA,
    LOST_CITY_REUNICLUS,
    TPCI_FEB_2026,
    OrderingContext,
    TimingWindow,
    TriggerKind,
)
from knockout_redirection_ordering import resolved_route_map
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import POKEMON_TO_LOST, SELF_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending


def program(pending, signature):
    routes = destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=signature,
    )
    assert routes is not None
    return routes


def dispose(pending, result):
    assert result.resolutions is not None
    state = discard_pending_with_zone_routes(
        pending,
        promote_id="b",
        destinations=resolved_route_map(result.resolutions),
    )
    assert state is not None
    assert state.board is not None
    assert state.board.active_id == "b"
    return state


def main() -> None:
    initial, pending = build_pending()
    programs = {
        "return-ability": program(pending, SELF_TO_HAND),
        "lost-city": program(pending, POKEMON_TO_LOST),
    }
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=1,
        interaction_id=LOST_CITY_REUNICLUS,
    )

    # TPCi and Asia/Japan identify different abstract roles here, and those
    # roles belong to different players in this state. Physical execution must
    # remain blocked.
    conflict = authorize_and_resolve_order(
        programs,
        ("lost-city", "return-ability"),
        context=context,
        source_ids=(
            TPCI_FEB_2026,
            ASIA_LOST_CITY_REUNICLUS_QA,
            JAPAN_LOST_CITY_QA,
        ),
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-a",
    )
    assert conflict.status == AuthorizedOrderStatus.AUTHORITY_CONFLICT
    assert conflict.chooser is None
    assert conflict.resolutions is None

    # If the current player also owns the Knocked Out Pokemon, every selected
    # source names the same concrete chooser. The source-level disagreement is
    # then immaterial to this concrete state.
    collapsed = authorize_and_resolve_order(
        programs,
        ("lost-city", "return-ability"),
        context=context,
        source_ids=(
            TPCI_FEB_2026,
            ASIA_LOST_CITY_REUNICLUS_QA,
            JAPAN_LOST_CITY_QA,
        ),
        players=OrderingPlayers(
            current_player="player-b",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-b",
    )
    assert collapsed.status == AuthorizedOrderStatus.RESOLVED
    assert collapsed.chooser == "player-b"
    collapsed_state = dispose(pending, collapsed)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert collapsed_state.ledger.exchangeable.count(
            card_class, "lost_zone"
        ) == 1
    assert collapsed_state.ledger.totals() == initial.totals()

    # Under the TPCi source alone, the current player can legally choose the
    # opposite order even when the Knocked Out Pokemon belongs to the opponent.
    tpci = authorize_and_resolve_order(
        programs,
        ("return-ability", "lost-city"),
        context=context,
        source_ids=(TPCI_FEB_2026,),
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-a",
    )
    assert tpci.status == AuthorizedOrderStatus.RESOLVED
    tpci_state = dispose(pending, tpci)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert tpci_state.ledger.exchangeable.count(card_class, "hand") == 1
    assert tpci_state.ledger.totals() == initial.totals()

    # The Japan card-specific source instead assigns the choice to the owner.
    japan = authorize_and_resolve_order(
        programs,
        ("lost-city", "return-ability"),
        context=context,
        source_ids=(JAPAN_LOST_CITY_QA,),
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-b",
    )
    assert japan.status == AuthorizedOrderStatus.RESOLVED
    assert japan.chooser == "player-b"

    unauthorized = authorize_and_resolve_order(
        programs,
        ("lost-city", "return-ability"),
        context=context,
        source_ids=(TPCI_FEB_2026,),
        players=OrderingPlayers(current_player="player-a"),
        submitted_by="player-b",
    )
    assert unauthorized.status == AuthorizedOrderStatus.UNAUTHORIZED_CHOOSER
    assert unauthorized.chooser == "player-a"
    assert unauthorized.resolutions is None

    missing = authorize_and_resolve_order(
        programs,
        ("lost-city", "return-ability"),
        context=context,
        source_ids=(ASIA_LOST_CITY_REUNICLUS_QA,),
        players=OrderingPlayers(current_player="player-a"),
        submitted_by="player-b",
    )
    assert missing.status == AuthorizedOrderStatus.MISSING_PLAYER_CONTEXT

    no_claim = authorize_and_resolve_order(
        programs,
        ("lost-city", "return-ability"),
        context=context,
        source_ids=(ADVANCED_RULEBOOK_3_4,),
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-a",
    )
    assert no_claim.status == AuthorizedOrderStatus.NO_AUTHORITY_CLAIMS

    invalid = authorize_and_resolve_order(
        programs,
        ("lost-city",),
        context=context,
        source_ids=(TPCI_FEB_2026,),
        players=OrderingPlayers(current_player="player-a"),
        submitted_by="player-a",
    )
    assert invalid.status == AuthorizedOrderStatus.INVALID_EFFECT_ORDER
    assert invalid.resolutions is None

    print("Authorized KO redirection regressions passed")


if __name__ == "__main__":
    main()
