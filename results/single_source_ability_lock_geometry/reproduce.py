"""Reproduce single-source continuous Ability-lock geometry."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_action_quota_derivation import derive_board_action_quotas
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from build_expanded_legality_baseline import classify_effective_legality
from garbotoxin_suppression import garbotoxin_suppressed_object_ids
from single_source_ability_lock_geometry import (
    BIDE_BARRICADE,
    GARBOTOXIN,
    LAZY,
    NEUTRALIZING_GAS,
    PROFILES,
    STICKY_BIND,
    single_source_suppressed_object_ids,
)
from turn_action_budget import TurnAction, TurnActionBudget


def _card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def _verify_profiles() -> None:
    expected_names = {
        "Bide Barricade": "Bide Barricade",
        "Emperor's Eyes": "Emperor's Eyes",
        "Neutralizing Gas": "Neutralizing Gas",
        "Lazy": "Lazy",
        "Cursed Land": "Cursed Land",
        "Sticky Bind": "Sticky Bind",
        "Garbotoxin": "Garbotoxin",
    }
    for profile in PROFILES:
        for print_id in profile.print_ids:
            card = _card(print_id)
            status, _ = classify_effective_legality(card)
            assert status == "Legal"
            assert any(
                row["name"] == expected_names[profile.name]
                for row in card.get("abilities") or []
            )


def _quota(board, suppressed, budget):
    return derive_board_action_quotas(
        board,
        budget,
        suppressed_ability_object_ids=suppressed,
    )


def main() -> None:
    _verify_profiles()

    active = make_pokemon("active", "Test Active", print_id="test-active")
    zone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal"},
    )
    player = make_board(active, (zone,))
    opponent_dummy = make_pokemon("opp", "Opponent", print_id="opp")
    empty_opponent = make_board(opponent_dummy)

    base = TurnActionBudget()
    enabled = _quota(player, frozenset(), base)
    assert enabled.supporter_play_limit == 2
    used_one = enabled.consume(TurnAction.SUPPORTER)
    assert used_one is not None

    # Active Wobbuffet affects both players, excludes Psychic targets.
    wob = make_pokemon("wob", "Wobbuffet", print_id="xy4-36")
    wob_opponent = make_board(wob)
    bide_ids = single_source_suppressed_object_ids(
        player,
        wob_opponent,
        source_owner="opponent",
        source_object_id="wob",
    )
    assert "zone" in bide_ids
    assert _quota(player, bide_ids, used_one).supporter_play_limit == 1

    psychic_zone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal", "Psychic"},
    )
    psychic_player = make_board(active, (psychic_zone,))
    assert "zone" not in single_source_suppressed_object_ids(
        psychic_player,
        wob_opponent,
        source_owner="opponent",
        source_object_id="wob",
    )

    # Same-side Bide Barricade also suppresses non-Psychic Dual Brains.
    own_wob_player = make_board(wob, (zone,))
    own_bide = single_source_suppressed_object_ids(
        own_wob_player,
        empty_opponent,
        source_owner="player",
        source_object_id="wob",
    )
    assert "zone" in own_bide

    # Neutralizing Gas and Lazy require the opponent source to be Active.
    weezing = make_pokemon(
        "weezing",
        "Galarian Weezing",
        print_id="swsh2-113",
    )
    weezing_active = make_board(weezing)
    gas_ids = single_source_suppressed_object_ids(
        player,
        weezing_active,
        source_owner="opponent",
        source_object_id="weezing",
    )
    assert "zone" in gas_ids

    weezing_bench = make_board(opponent_dummy, (weezing,))
    assert single_source_suppressed_object_ids(
        player,
        weezing_bench,
        source_owner="opponent",
        source_object_id="weezing",
    ) == frozenset()

    slaking = make_pokemon("slaking", "Slaking", print_id="sm7-115")
    slaking_active = make_board(slaking)
    assert "zone" in single_source_suppressed_object_ids(
        player,
        slaking_active,
        source_owner="opponent",
        source_object_id="slaking",
    )
    # Lazy is opponent-scoped; the owner's own Magnezone is unaffected.
    own_slaking_player = make_board(slaking, (zone,))
    assert single_source_suppressed_object_ids(
        own_slaking_player,
        empty_opponent,
        source_owner="player",
        source_object_id="slaking",
    ) == frozenset()

    # Sticky Bind is Bench-dependent and targets Benched Stage 2 Pokemon.
    gastrodon = make_pokemon("gastro", "Gastrodon", print_id="sv8-107")
    gastro_opponent = make_board(opponent_dummy, (gastrodon,))
    sticky_ids = single_source_suppressed_object_ids(
        player,
        gastro_opponent,
        source_owner="opponent",
        source_object_id="gastro",
    )
    assert "zone" in sticky_ids

    zone_active_player = make_board(zone, (active,))
    assert "zone" not in single_source_suppressed_object_ids(
        zone_active_player,
        gastro_opponent,
        source_owner="opponent",
        source_object_id="gastro",
    )

    basic_zone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Basic", "Metal"},
    )
    basic_player = make_board(active, (basic_zone,))
    assert "zone" not in single_source_suppressed_object_ids(
        basic_player,
        gastro_opponent,
        source_owner="opponent",
        source_object_id="gastro",
    )

    # The general single-source Garbotoxin profile agrees with the specialized
    # overlay for the ordinary unprotected case.
    garb = make_pokemon(
        "garb",
        "Garbodor",
        print_id="xy9-57",
        tool=ToolAttachment("garb-tool", "Float Stone"),
    )
    garb_opponent = make_board(opponent_dummy, (garb,))
    general_garb = single_source_suppressed_object_ids(
        player,
        garb_opponent,
        source_owner="opponent",
        source_object_id="garb",
    )
    specialized_garb = garbotoxin_suppressed_object_ids(
        player,
        garb_opponent,
    )
    assert general_garb == specialized_garb
    assert "zone" in general_garb

    # Opponent Ability locks are blocked by live Stealthy Hood but return when
    # Jamming Tower blanks the Tool effect.
    hooded_zone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal"},
        tool=ToolAttachment("hood", "Stealthy Hood"),
    )
    hooded_player = make_board(active, (hooded_zone,))
    assert "zone" not in single_source_suppressed_object_ids(
        hooded_player,
        weezing_active,
        source_owner="opponent",
        source_object_id="weezing",
    )
    assert "zone" in single_source_suppressed_object_ids(
        hooded_player,
        weezing_active,
        source_owner="opponent",
        source_object_id="weezing",
        stadium_name="Jamming Tower",
    )

    # Profile constants retain the intended distinct geometry.
    assert BIDE_BARRICADE.activation == "active"
    assert NEUTRALIZING_GAS.scope == "opponent"
    assert LAZY.scope == "opponent"
    assert STICKY_BIND.target_position == "bench"
    assert GARBOTOXIN.activation == "tool_attached"

    print("single_source_ability_lock_geometry regression: PASS")


if __name__ == "__main__":
    main()
