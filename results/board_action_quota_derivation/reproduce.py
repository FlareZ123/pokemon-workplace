"""Reproduce physical-board derivation of live action quotas."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_action_quota_derivation import (
    derive_board_action_quotas,
    quota_grants_from_board,
    refresh_canonical_action_quotas,
    set_board_pokemon_abilities_enabled,
)
from board_object_kernel import knock_out, make_board, make_pokemon
from build_expanded_legality_baseline import classify_effective_legality
from canonical_turn_budget_owner import promote_composite_turn_budget
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def _card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def main() -> None:
    magnezone_card = _card("bw8-46")
    status, _ = classify_effective_legality(magnezone_card)
    assert status == "Legal"
    ability = next(
        row for row in magnezone_card["abilities"]
        if row["name"] == "Dual Brains"
    )
    assert ability["text"] == "During your turn, you may play 2 Supporter cards."

    active = make_pokemon("active", "Test Active", print_id="test-active")
    magnezone = make_pokemon(
        "magnezone",
        "Magnezone",
        print_id="bw8-46",
        abilities_enabled=True,
    )
    board = make_board(active, (magnezone,))

    grants = quota_grants_from_board(board)
    assert len(grants) == 1
    assert grants[0].limit == 2

    enabled = derive_board_action_quotas(board, TurnActionBudget())
    assert enabled.supporter_play_limit == 2
    first = enabled.consume(TurnAction.SUPPORTER)
    assert first is not None
    assert first.supporter_plays_used == 1
    assert first.can(TurnAction.SUPPORTER)

    # Effective Ability suppression removes the live grant without erasing
    # the already-played Supporter.
    suppressed_board = set_board_pokemon_abilities_enabled(
        board,
        "magnezone",
        False,
    )
    suppressed = derive_board_action_quotas(suppressed_board, first)
    assert suppressed.supporter_plays_used == 1
    assert suppressed.supporter_play_limit == 1
    assert not suppressed.can(TurnAction.SUPPORTER)

    restored_board = set_board_pokemon_abilities_enabled(
        suppressed_board,
        "magnezone",
        True,
    )
    restored = derive_board_action_quotas(restored_board, suppressed)
    assert restored.supporter_plays_used == 1
    assert restored.supporter_play_limit == 2
    assert restored.can(TurnAction.SUPPORTER)

    # Exact print identity matters. Another Magnezone name does not invent
    # the Dual Brains grant.
    other_print = make_pokemon(
        "other-zone",
        "Magnezone",
        print_id="sm5-36",
    )
    wrong_board = make_board(active, (other_print,))
    assert quota_grants_from_board(wrong_board) == ()
    assert derive_board_action_quotas(
        wrong_board,
        TurnActionBudget(),
    ).supporter_play_limit == 1

    # Duplicate active sources retain a total ceiling of two.
    magnezone2 = make_pokemon(
        "magnezone-2",
        "Magnezone",
        print_id="bw8-46",
    )
    doubled = make_board(active, (magnezone, magnezone2))
    assert len(quota_grants_from_board(doubled)) == 2
    assert derive_board_action_quotas(
        doubled,
        TurnActionBudget(),
    ).supporter_play_limit == 2

    # Leaving play removes the grant on the next derivation.
    ko = knock_out(board, "magnezone")
    assert ko is not None
    board_without_zone, removed = ko
    assert board_without_zone is not None
    assert removed.object_id == "magnezone"
    after_leave = derive_board_action_quotas(board_without_zone, first)
    assert after_leave.supporter_plays_used == 1
    assert after_leave.supporter_play_limit == 1
    assert not after_leave.can(TurnAction.SUPPORTER)

    # Canonical composite state can refresh its owned budget directly from
    # physical board truth.
    composite = promote_composite_turn_budget(make_state({}), board)
    composite = refresh_canonical_action_quotas(composite)
    assert composite.budget.supporter_play_limit == 2
    one = composite.budget.consume(TurnAction.SUPPORTER)
    assert one is not None
    from canonical_turn_budget_owner import with_canonical_budget
    composite = with_canonical_budget(composite, one)
    composite = type(composite)(
        unified=composite.unified,
        board=suppressed_board,
    )
    composite = refresh_canonical_action_quotas(composite)
    assert composite.budget.supporter_plays_used == 1
    assert composite.budget.supporter_play_limit == 1

    print("board_action_quota_derivation regression: PASS")


if __name__ == "__main__":
    main()
