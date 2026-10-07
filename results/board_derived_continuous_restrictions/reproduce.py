"""Reproduce board-derived continuous source-scoped restriction contexts."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import (
    initialize_setup_lock_state,
    initialize_snapshot_lock_state,
)
from active_source_scoped_restrictions import active_restrictions_for_player
from board_derived_continuous_restrictions import (
    active_restrictions_from_boards,
    derive_continuous_restriction_sources,
)
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from continuous_source_scoped_restrictions import continuous_restriction_active
from source_scoped_restriction_activation import build_restriction_activation_profiles


def _source_for_card(sources, card_id: str):
    matches = [
        row
        for row in sources
        if row.profile.restriction.card_id == card_id
    ]
    assert len(matches) == 1, (card_id, len(matches))
    return matches[0]


def _snapshot(player_board, opponent_board, *, stadium_name=None):
    state = initialize_snapshot_lock_state(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    assert state.resolved
    return state


def main() -> None:
    profiles = build_restriction_activation_profiles(ROOT / "resources")

    filler_a = make_pokemon("a-filler", "Filler A")
    filler_b = make_pokemon("b-filler", "Filler B")

    vileplume = make_pokemon(
        "vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Stage2",),
    )
    garbodor = make_pokemon(
        "garbodor",
        "Garbodor",
        print_id="xy9-57",
        tags=("Stage1",),
        tool=ToolAttachment("garbodor-tool", "Float Stone"),
    )
    vileplume_board = make_board(vileplume)
    garbodor_board = make_board(garbodor)

    garbotoxin_lock = _snapshot(vileplume_board, garbodor_board)
    suppressed_sources = derive_continuous_restriction_sources(
        vileplume_board,
        garbodor_board,
        profiles=profiles,
        lock_state=garbotoxin_lock,
        player_id="A",
        opponent_id="B",
    )
    suppressed_vileplume = _source_for_card(suppressed_sources, "xy7-3")
    assert not suppressed_vileplume.context.ability_enabled
    assert not active_restrictions_for_player(
        "A",
        continuous_sources=suppressed_sources,
    )

    hood_vileplume = make_pokemon(
        "vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Stage2",),
        tool=ToolAttachment("hood", "Stealthy Hood"),
    )
    hood_board = make_board(hood_vileplume)
    hood_lock = _snapshot(hood_board, garbodor_board)
    hood_sources = derive_continuous_restriction_sources(
        hood_board,
        garbodor_board,
        profiles=profiles,
        lock_state=hood_lock,
        player_id="A",
        opponent_id="B",
    )
    hood_source = _source_for_card(hood_sources, "xy7-3")
    assert hood_source.context.ability_enabled
    assert {row.card_id for row in active_restrictions_for_player(
        "A",
        continuous_sources=hood_sources,
    )} == {"xy7-3"}

    try:
        derive_continuous_restriction_sources(
            hood_board,
            garbodor_board,
            profiles=profiles,
            lock_state=hood_lock,
            stadium_name="Jamming Tower",
            player_id="A",
            opponent_id="B",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("stale pre-Stadium suppression overlay was accepted")

    jammed_lock = _snapshot(
        hood_board,
        garbodor_board,
        stadium_name="Jamming Tower",
    )
    jammed_sources = derive_continuous_restriction_sources(
        hood_board,
        garbodor_board,
        profiles=profiles,
        lock_state=jammed_lock,
        stadium_name="Jamming Tower",
        player_id="A",
        opponent_id="B",
    )
    jammed_vileplume = _source_for_card(jammed_sources, "xy7-3")
    assert not jammed_vileplume.context.ability_enabled
    assert not active_restrictions_for_player(
        "A",
        continuous_sources=jammed_sources,
    )

    disabled_vileplume = make_pokemon(
        "vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Stage2",),
        abilities_enabled=False,
    )
    disabled_board = make_board(disabled_vileplume)
    disabled_opponent = make_board(filler_b)
    disabled_lock = _snapshot(disabled_board, disabled_opponent)
    disabled_sources = derive_continuous_restriction_sources(
        disabled_board,
        disabled_opponent,
        profiles=profiles,
        lock_state=disabled_lock,
        player_id="A",
        opponent_id="B",
    )
    assert not _source_for_card(disabled_sources, "xy7-3").context.ability_enabled

    arbok = make_pokemon(
        "arbok",
        "Team Rocket's Arbok",
        print_id="sv10-113",
        tags=("Stage1",),
    )
    player_filler_board = make_board(filler_a)
    arbok_active_board = make_board(arbok, (filler_b,))
    arbok_active_lock = _snapshot(player_filler_board, arbok_active_board)
    arbok_active = active_restrictions_from_boards(
        "A",
        player_filler_board,
        arbok_active_board,
        profiles=profiles,
        lock_state=arbok_active_lock,
        player_id="A",
        opponent_id="B",
    )
    assert {row.card_id for row in arbok_active} == {"sv10-113"}

    arbok_bench_board = make_board(filler_b, (arbok,))
    arbok_bench_lock = _snapshot(player_filler_board, arbok_bench_board)
    arbok_bench = active_restrictions_from_boards(
        "A",
        player_filler_board,
        arbok_bench_board,
        profiles=profiles,
        lock_state=arbok_bench_lock,
        player_id="A",
        opponent_id="B",
    )
    assert not arbok_bench

    genesect = make_pokemon(
        "genesect",
        "Genesect",
        print_id="sv6pt5-40",
        tags=("Basic",),
        tool=ToolAttachment("genesect-tool", "Float Stone"),
    )
    genesect_board = make_board(genesect)
    genesect_lock = _snapshot(player_filler_board, genesect_board)
    genesect_sources = derive_continuous_restriction_sources(
        player_filler_board,
        genesect_board,
        profiles=profiles,
        lock_state=genesect_lock,
        player_id="A",
        opponent_id="B",
    )
    genesect_source = _source_for_card(genesect_sources, "sv6pt5-40")
    assert genesect_source.context.tool_attached
    assert continuous_restriction_active(
        genesect_source.profile,
        genesect_source.context,
    )

    barbaracle = make_pokemon(
        "barbaracle",
        "Barbaracle",
        print_id="xy10-23",
        tags=("Stage1",),
    )
    barbaracle_board = make_board(barbaracle)
    no_stadium_lock = _snapshot(player_filler_board, barbaracle_board)
    no_stadium_sources = derive_continuous_restriction_sources(
        player_filler_board,
        barbaracle_board,
        profiles=profiles,
        lock_state=no_stadium_lock,
        player_id="A",
        opponent_id="B",
    )
    no_stadium = _source_for_card(no_stadium_sources, "xy10-23")
    assert not no_stadium.context.stadium_in_play
    assert not continuous_restriction_active(no_stadium.profile, no_stadium.context)

    stadium_lock = _snapshot(
        player_filler_board,
        barbaracle_board,
        stadium_name="Parallel City",
    )
    stadium_sources = derive_continuous_restriction_sources(
        player_filler_board,
        barbaracle_board,
        profiles=profiles,
        lock_state=stadium_lock,
        stadium_name="Parallel City",
        player_id="A",
        opponent_id="B",
    )
    with_stadium = _source_for_card(stadium_sources, "xy10-23")
    assert with_stadium.context.stadium_in_play
    assert continuous_restriction_active(with_stadium.profile, with_stadium.context)

    omastar = make_pokemon(
        "omastar",
        "Omastar",
        print_id="sm9-76",
        tags=("Stage2",),
    )
    opponent_many = make_board(
        filler_a,
        (
            make_pokemon("a-bench-1", "Bench A1"),
            make_pokemon("a-bench-2", "Bench A2"),
        ),
    )
    omastar_board = make_board(omastar)
    omastar_lock = _snapshot(opponent_many, omastar_board)
    omastar_sources = derive_continuous_restriction_sources(
        opponent_many,
        omastar_board,
        profiles=profiles,
        lock_state=omastar_lock,
        player_id="A",
        opponent_id="B",
    )
    omastar_source = _source_for_card(omastar_sources, "sm9-76")
    assert omastar_source.context.player_pokemon_in_play == 1
    assert omastar_source.context.opponent_pokemon_in_play == 3
    assert continuous_restriction_active(omastar_source.profile, omastar_source.context)

    empoleon = make_pokemon(
        "empoleon",
        "Empoleon V",
        print_id="swsh5-40",
        tags=("Basic", "RuleBox"),
    )
    wobbuffet = make_pokemon(
        "wobbuffet",
        "Wobbuffet",
        print_id="xy4-36",
        tags=("Basic", "Psychic"),
    )
    empoleon_board = make_board(empoleon)
    wobbuffet_board = make_board(wobbuffet)
    unresolved = initialize_snapshot_lock_state(empoleon_board, wobbuffet_board)
    assert not unresolved.resolved
    try:
        derive_continuous_restriction_sources(
            empoleon_board,
            wobbuffet_board,
            profiles=profiles,
            lock_state=unresolved,
            player_id="A",
            opponent_id="B",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("unresolved Ability-lock state was accepted")

    setup_resolved = initialize_setup_lock_state(
        empoleon_board,
        wobbuffet_board,
        first_player_owner="player",
    )
    assert setup_resolved.resolved
    derive_continuous_restriction_sources(
        empoleon_board,
        wobbuffet_board,
        profiles=profiles,
        lock_state=setup_resolved,
        player_id="A",
        opponent_id="B",
    )

    print(
        json.dumps(
            {
                "garbotoxin_disables_vileplume_restriction": True,
                "stealthy_hood_preserves_vileplume_without_jamming_tower": True,
                "jamming_tower_invalidates_old_overlay_and_restores_suppression": True,
                "base_ability_disable_is_preserved": True,
                "active_spot_geometry_derived_from_board": True,
                "tool_attachment_geometry_derived_from_board": True,
                "stadium_geometry_derived_from_board": True,
                "relative_pokemon_count_derived_from_board": True,
                "unresolved_lock_state_rejected": True,
                "verified_setup_precedence_accepted": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
