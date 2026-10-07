"""Reproduce the causal lock -> canonical turn-budget ownership chain."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_canonical_budget import refresh_canonical_budget_from_lock_state
from ability_lock_causal_state import initialize_setup_lock_state
from board_object_kernel import make_board, make_pokemon
from canonical_turn_budget_owner import CanonicalCompositeTurnState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import UnifiedState


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

    unified = UnifiedState(
        locations=(),
        turn_budget=TurnActionBudget(),
    )
    canonical = CanonicalCompositeTurnState(unified=unified, board=player)
    assert canonical.budget.supporter_play_limit == 1

    player_first_lock = initialize_setup_lock_state(
        player,
        opponent,
        first_player_owner="player",
    )
    player_first = refresh_canonical_budget_from_lock_state(
        canonical,
        player_first_lock,
    )
    assert player_first is not None
    assert player_first.budget.supporter_play_limit == 2
    assert player_first.unified.turn_budget == player_first.budget

    opponent_first_lock = initialize_setup_lock_state(
        player,
        opponent,
        first_player_owner="opponent",
    )
    opponent_first = refresh_canonical_budget_from_lock_state(
        canonical,
        opponent_first_lock,
    )
    assert opponent_first is not None
    assert opponent_first.budget.supporter_play_limit == 1
    assert opponent_first.unified.turn_budget == opponent_first.budget

    # An unresolved lock state cannot safely publish a downstream quota overlay.
    unresolved = initialize_setup_lock_state(
        player,
        opponent,
        first_player_owner="player",
    )
    assert unresolved.resolved
    unresolved_like = type(unresolved)(
        resolution=type(unresolved.resolution)(
            potential_sources=unresolved.resolution.potential_sources,
            suppression_edges=unresolved.resolution.suppression_edges,
            unresolved_cycles=(unresolved.resolution.potential_sources,),
            active_sources=None,
            player_suppressed_object_ids=None,
            opponent_suppressed_object_ids=None,
        ),
        basis="unresolved",
    )
    assert refresh_canonical_budget_from_lock_state(
        canonical,
        unresolved_like,
    ) is None

    print(
        "ability_lock_canonical_budget regression: PASS "
        f"(player-first={player_first.budget.supporter_play_limit}, "
        f"opponent-first={opponent_first.budget.supporter_play_limit})"
    )


if __name__ == "__main__":
    main()
