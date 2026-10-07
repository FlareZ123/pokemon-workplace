"""Compose setup Ability-lock precedence with canonical Supporter quota derivation."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_setup_precedence import resolve_setup_ability_lock_precedence
from board_action_quota_derivation import derive_board_action_quotas
from board_object_kernel import make_board, make_pokemon
from turn_action_budget import TurnActionBudget


def main() -> None:
    empoleon = make_pokemon(
        "empoleon",
        "Empoleon V",
        print_id="swsh5-40",
        tags={"Basic", "Water", "RuleBox"},
    )
    magnezone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal"},
    )
    player = make_board(empoleon, (magnezone,))

    wobbuffet = make_pokemon(
        "wobbuffet",
        "Wobbuffet",
        print_id="xy4-36",
        tags={"Basic", "Psychic"},
    )
    opponent = make_board(wobbuffet)

    base_budget = TurnActionBudget()
    assert base_budget.supporter_play_limit == 1

    player_first = resolve_setup_ability_lock_precedence(
        player,
        opponent,
        first_player_owner="player",
    )
    assert player_first.resolved
    assert player_first.player_suppressed_object_ids == frozenset()
    player_first_budget = derive_board_action_quotas(
        player,
        base_budget,
        suppressed_ability_object_ids=player_first.player_suppressed_object_ids,
    )
    assert player_first_budget.supporter_play_limit == 2

    opponent_first = resolve_setup_ability_lock_precedence(
        player,
        opponent,
        first_player_owner="opponent",
    )
    assert opponent_first.resolved
    assert opponent_first.player_suppressed_object_ids is not None
    assert {"empoleon", "zone"}.issubset(
        opponent_first.player_suppressed_object_ids
    )
    opponent_first_budget = derive_board_action_quotas(
        player,
        base_budget,
        suppressed_ability_object_ids=opponent_first.player_suppressed_object_ids,
    )
    assert opponent_first_budget.supporter_play_limit == 1

    print(
        "ability_lock_precedence_quota_bridge regression: PASS "
        f"(player-first={player_first_budget.supporter_play_limit}, "
        f"opponent-first={opponent_first_budget.supporter_play_limit})"
    )


if __name__ == "__main__":
    main()
