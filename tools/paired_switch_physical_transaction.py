"""Physical two-sided targeted-switch Trainer action with ordered dependencies.

The source program is audited by paired_switch_order_catalog. Board-object
movement is delegated to the canonical board_object_kernel. The transaction
spends ordinary Supporter quota when applicable and reports consumed Item
copies; a higher-layer zone ledger must commit source hand->discard movement.

This is a bounded mechanic: the caller supplies explicit playable-card
availability, Item lock permission, and target/own promotion selections.
"""
from dataclasses import dataclass

from tools.board_object_kernel import BoardState, switch_active
from tools.paired_switch_order_catalog import PairedSwitchProgram
from tools.turn_action_budget import TurnAction, TurnActionBudget


SUPPORTERS = frozenset({"Guzma", "Team Rocket's Giovanni"})
ITEMS = frozenset({"Prime Catcher", "Cross Switcher"})


@dataclass(frozen=True)
class SwitchTransaction:
    player_board: BoardState
    opponent_board: BoardState
    turn_budget: TurnActionBudget
    source_copies_spent: int
    effect_sequence: tuple[str, ...]


def execute_paired_switch(
    player_board: BoardState,
    opponent_board: BoardState,
    turn_budget: TurnActionBudget,
    program: PairedSwitchProgram,
    *,
    opponent_promote_id: str | None,
    own_promote_id: str | None,
    copies_available: int = 1,
    item_play_allowed: bool = True,
) -> SwitchTransaction | None:
    """Apply a player's card with explicit source/target choices.

    Return None if the requested source or required target is not playable.
    A successful first switch remains when the second switch is impossible.
    """
    if program.name not in SUPPORTERS | ITEMS:
        raise ValueError("Unsupported paired-switch card")
    if copies_available < program.copies_together:
        return None
    if turn_budget.turn_ended:
        return None

    if program.name in SUPPORTERS:
        next_budget = turn_budget.consume(TurnAction.SUPPORTER)
        if next_budget is None:
            return None
    else:
        if not item_play_allowed:
            return None
        next_budget = turn_budget

    first_is_opponent = program.first == "opponent"
    if first_is_opponent:
        if opponent_promote_id not in opponent_board.bench_ids:
            return None
        moved_opponent = switch_active(opponent_board, opponent_promote_id)
        assert moved_opponent is not None

        if player_board.bench_ids:
            if own_promote_id not in player_board.bench_ids:
                return None
            moved_player = switch_active(player_board, own_promote_id)
            assert moved_player is not None
            effects = ("opponent", "own")
        else:
            moved_player = player_board
            effects = ("opponent",)
    else:
        # Giovanni's first step requires two own Team Rocket's Pokemon.
        active = player_board.get(player_board.active_id)
        if "team_rocket" not in active.tags:
            return None
        if own_promote_id not in player_board.bench_ids:
            return None
        chosen = player_board.get(own_promote_id)
        if "team_rocket" not in chosen.tags:
            return None
        moved_player = switch_active(player_board, own_promote_id)
        assert moved_player is not None

        if opponent_board.bench_ids:
            if opponent_promote_id not in opponent_board.bench_ids:
                return None
            moved_opponent = switch_active(opponent_board, opponent_promote_id)
            assert moved_opponent is not None
            effects = ("own", "opponent")
        else:
            moved_opponent = opponent_board
            effects = ("own",)

    return SwitchTransaction(
        player_board=moved_player,
        opponent_board=moved_opponent,
        turn_budget=next_budget,
        source_copies_spent=program.copies_together,
        effect_sequence=effects,
    )
