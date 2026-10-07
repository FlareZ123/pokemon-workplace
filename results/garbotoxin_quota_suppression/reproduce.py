"""Reproduce Garbotoxin suppression as an overlay on board-derived quota."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_action_quota_derivation import derive_board_action_quotas
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from build_expanded_legality_baseline import classify_effective_legality
from garbotoxin_suppression import (
    GARBOTOXIN_PRINT_IDS,
    garbotoxin_source_active,
    garbotoxin_suppressed_object_ids,
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


def _supporter_limit(
    player_board,
    opponent_board,
    budget,
    *,
    stadium_name=None,
):
    suppressed = garbotoxin_suppressed_object_ids(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    return derive_board_action_quotas(
        player_board,
        budget,
        suppressed_ability_object_ids=suppressed,
    )


def main() -> None:
    # Verify every hard-coded Garbotoxin print against the bundled primary card
    # data rather than trusting name-level equivalence.
    for card_id in sorted(GARBOTOXIN_PRINT_IDS):
        card = _card(card_id)
        status, _ = classify_effective_legality(card)
        assert status == "Legal"
        ability = next(
            row for row in card["abilities"] if row["name"] == "Garbotoxin"
        )
        assert "has a Pokémon Tool card attached" in ability["text"]
        assert "has no Abilities (except for Garbotoxin)" in ability["text"]

    hood = _card("sm10-186")
    status, _ = classify_effective_legality(hood)
    assert status == "Legal"
    assert any(
        "Prevent all effects of your opponent's Abilities" in rule
        for rule in hood["rules"]
    )

    tower = _card("sv6-153")
    status, _ = classify_effective_legality(tower)
    assert status == "Legal"
    assert any(
        "Pokémon Tools attached to each Pokémon" in rule
        and "have no effect" in rule
        for rule in tower["rules"]
    )

    active = make_pokemon("active", "Test Active", print_id="test-active")
    magnezone = make_pokemon("zone", "Magnezone", print_id="bw8-46")
    player = make_board(active, (magnezone,))

    opp_active = make_pokemon("opp-active", "Test Opponent", print_id="opp-test")
    garbodor_no_tool = make_pokemon(
        "garbodor",
        "Garbodor",
        print_id="xy9-57",
    )
    opponent_no_lock = make_board(opp_active, (garbodor_no_tool,))
    assert not garbotoxin_source_active(garbodor_no_tool)

    base = TurnActionBudget()
    enabled = _supporter_limit(player, opponent_no_lock, base)
    assert enabled.supporter_play_limit == 2
    first = enabled.consume(TurnAction.SUPPORTER)
    assert first is not None

    garbodor = make_pokemon(
        "garbodor",
        "Garbodor",
        print_id="xy9-57",
        tool=ToolAttachment("garb-tool", "Float Stone"),
    )
    opponent_lock = make_board(opp_active, (garbodor,))
    assert garbotoxin_source_active(garbodor)

    suppressed_ids = garbotoxin_suppressed_object_ids(player, opponent_lock)
    assert "zone" in suppressed_ids
    locked = _supporter_limit(player, opponent_lock, first)
    assert locked.supporter_plays_used == 1
    assert locked.supporter_play_limit == 1
    assert not locked.can(TurnAction.SUPPORTER)

    # Stealthy Hood protects only from the opponent's Ability effect.
    hooded_zone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tool=ToolAttachment("hood", "Stealthy Hood", print_id="sm10-186"),
    )
    hooded_player = make_board(active, (hooded_zone,))
    hooded_ids = garbotoxin_suppressed_object_ids(
        hooded_player,
        opponent_lock,
    )
    assert "zone" not in hooded_ids
    hooded_budget = _supporter_limit(hooded_player, opponent_lock, first)
    assert hooded_budget.supporter_play_limit == 2
    assert hooded_budget.can(TurnAction.SUPPORTER)

    # Jamming Tower blanks Hood's protection, but the Tool remains physically
    # attached. Opposing Garbotoxin therefore suppresses Dual Brains again.
    tower_ids = garbotoxin_suppressed_object_ids(
        hooded_player,
        opponent_lock,
        stadium_name="Jamming Tower",
    )
    assert "zone" in tower_ids
    tower_budget = _supporter_limit(
        hooded_player,
        opponent_lock,
        first,
        stadium_name="Jamming Tower",
    )
    assert tower_budget.supporter_play_limit == 1
    assert not tower_budget.can(TurnAction.SUPPORTER)

    # Garbotoxin's own attached-Tool condition does not require that Tool's
    # effect function. Jamming Tower therefore does not deactivate the source.
    assert garbotoxin_source_active(garbodor)

    # A player's own Garbotoxin also suppresses their other Pokemon. Stealthy
    # Hood does not protect here because its wording is opponent-specific.
    own_garb = make_pokemon(
        "own-garb",
        "Garbodor",
        print_id="bw6-54",
        tool=ToolAttachment("own-tool", "Float Stone"),
    )
    own_lock_player = make_board(active, (hooded_zone, own_garb))
    empty_opponent = make_board(opp_active)
    own_ids = garbotoxin_suppressed_object_ids(
        own_lock_player,
        empty_opponent,
    )
    assert "zone" in own_ids
    assert "own-garb" not in own_ids
    own_budget = _supporter_limit(
        own_lock_player,
        empty_opponent,
        first,
    )
    assert own_budget.supporter_play_limit == 1

    print("garbotoxin_quota_suppression regression: PASS")


if __name__ == "__main__":
    main()
