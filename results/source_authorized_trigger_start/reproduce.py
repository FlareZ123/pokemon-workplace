"""Reproduce source-authorized selection over the trigger-deferral kernel."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from authorized_trigger_start import (
    AuthorizedStartStatus,
    start_authorized_ready_effect,
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
from source_order_chooser import OrderingPlayers
from trigger_deferral_kernel import (
    make_trigger_state,
    record_trigger,
    resolve_next_step,
)


def context() -> OrderingContext:
    return OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=1,
        interaction_id=LOST_CITY_REUNICLUS,
    )


def main() -> None:
    selected_sources = (
        TPCI_FEB_2026,
        ASIA_LOST_CITY_REUNICLUS_QA,
        JAPAN_LOST_CITY_QA,
    )

    # Two simultaneously ready effects create a genuine ordering branch.
    ready = make_trigger_state("persistent-cells", "lost-city")
    conflict = start_authorized_ready_effect(
        ready,
        effect_id="lost-city",
        steps=("route-to-lost-zone",),
        context=context(),
        source_ids=selected_sources,
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-a",
    )
    assert conflict.status == AuthorizedStartStatus.AUTHORITY_CONFLICT
    assert conflict.state == ready

    # Abstract source disagreement collapses when both roles identify one player.
    collapsed = start_authorized_ready_effect(
        ready,
        effect_id="lost-city",
        steps=("route-to-lost-zone",),
        context=context(),
        source_ids=selected_sources,
        players=OrderingPlayers(
            current_player="player-b",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-b",
    )
    assert collapsed.status == AuthorizedStartStatus.STARTED
    assert collapsed.authority_required
    assert collapsed.chooser == "player-b"
    assert collapsed.state.active is not None
    assert collapsed.state.active.effect_id == "lost-city"
    assert collapsed.state.ready_effects == {"persistent-cells"}

    # A selected TPCi profile gives the current player the branch choice.
    tpci = start_authorized_ready_effect(
        ready,
        effect_id="persistent-cells",
        steps=("return-to-hand",),
        context=context(),
        source_ids=(TPCI_FEB_2026,),
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-a",
    )
    assert tpci.status == AuthorizedStartStatus.STARTED
    assert tpci.chooser == "player-a"

    unauthorized = start_authorized_ready_effect(
        ready,
        effect_id="persistent-cells",
        steps=("return-to-hand",),
        context=context(),
        source_ids=(TPCI_FEB_2026,),
        players=OrderingPlayers(current_player="player-a"),
        submitted_by="player-b",
    )
    assert unauthorized.status == AuthorizedStartStatus.UNAUTHORIZED_CHOOSER
    assert unauthorized.state == ready

    missing = start_authorized_ready_effect(
        ready,
        effect_id="persistent-cells",
        steps=("return-to-hand",),
        context=context(),
        source_ids=(ASIA_LOST_CITY_REUNICLUS_QA,),
        players=OrderingPlayers(current_player="player-a"),
        submitted_by="player-a",
    )
    assert missing.status == AuthorizedStartStatus.MISSING_PLAYER_CONTEXT

    no_claim = start_authorized_ready_effect(
        ready,
        effect_id="persistent-cells",
        steps=("return-to-hand",),
        context=context(),
        source_ids=(ADVANCED_RULEBOOK_3_4,),
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
        submitted_by="player-a",
    )
    assert no_claim.status == AuthorizedStartStatus.NO_AUTHORITY_CLAIMS

    # A sole ready effect creates no ordering choice. It may progress even when
    # the selected sources would disagree about who controls a multi-effect
    # branch.
    sole = make_trigger_state("fainting-spell")
    started = start_authorized_ready_effect(
        sole,
        effect_id="fainting-spell",
        steps=("flip-heads", "knock-out-attacker"),
        context=context(),
        source_ids=selected_sources,
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
    )
    assert started.status == AuthorizedStartStatus.STARTED
    assert not started.authority_required
    assert started.chooser is None

    scheduler = started.state
    first = resolve_next_step(scheduler)
    assert first is not None
    _step, scheduler = first
    scheduler = record_trigger(scheduler, effect_id="swelling-spite")
    assert scheduler is not None
    assert scheduler.deferred_effects == {"swelling-spite"}

    # Deferral remains stronger than ready-set authority: no effect may start
    # while another is active.
    blocked = start_authorized_ready_effect(
        scheduler,
        effect_id="swelling-spite",
        steps=("search-haunter", "shuffle"),
        context=context(),
        source_ids=selected_sources,
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
    )
    assert blocked.status == AuthorizedStartStatus.INVALID_START

    second = resolve_next_step(scheduler)
    assert second is not None
    _step, scheduler = second
    assert scheduler.active is None
    assert scheduler.ready_effects == {"swelling-spite"}

    followup = start_authorized_ready_effect(
        scheduler,
        effect_id="swelling-spite",
        steps=("search-haunter", "shuffle"),
        context=context(),
        source_ids=selected_sources,
        players=OrderingPlayers(
            current_player="player-a",
            knocked_out_pokemon_owner="player-b",
        ),
    )
    assert followup.status == AuthorizedStartStatus.STARTED
    assert not followup.authority_required

    invalid = start_authorized_ready_effect(
        ready,
        effect_id="unknown",
        steps=("noop",),
        context=context(),
        source_ids=(TPCI_FEB_2026,),
        players=OrderingPlayers(current_player="player-a"),
        submitted_by="player-a",
    )
    assert invalid.status == AuthorizedStartStatus.INVALID_START

    print("source-authorized trigger-start regressions passed")


if __name__ == "__main__":
    main()
