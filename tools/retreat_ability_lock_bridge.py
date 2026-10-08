"""Project a verified causal Ability-lock overlay onto Retreat source boards."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ability_lock_causal_state import AbilityLockCausalState
from board_object_kernel import BoardState


@dataclass(frozen=True)
class RetreatAbilityProjection:
    own_board: BoardState
    opponent_board: BoardState
    resolved: bool
    suppressed_own_ids: tuple[str, ...] = ()
    suppressed_opponent_ids: tuple[str, ...] = ()


def project_retreat_ability_state(
    own_board: BoardState,
    opponent_board: BoardState,
    lock_state: AbilityLockCausalState | None = None,
) -> RetreatAbilityProjection:
    """Use immutable source flags derived by the existing lock-state owner.

    When a causal source cycle has not been resolved, the projection returns
    original boards but marks its result unresolved. The Retreat executor must
    withhold a physical transaction in that case.
    """
    if lock_state is None:
        return RetreatAbilityProjection(own_board, opponent_board, True)

    if not lock_state.resolved:
        return RetreatAbilityProjection(own_board, opponent_board, False)

    resolution = lock_state.resolution
    own_ids = resolution.player_suppressed_object_ids
    opponent_ids = resolution.opponent_suppressed_object_ids
    assert own_ids is not None and opponent_ids is not None

    def mask(board: BoardState, ids: frozenset[str]) -> BoardState:
        modified = replace(
            board,
            objects=tuple(
                replace(
                    pokemon,
                    abilities_enabled=(
                        pokemon.abilities_enabled
                        and pokemon.object_id not in ids
                    ),
                )
                for pokemon in board.objects
            ),
        )
        modified.validate()
        return modified

    return RetreatAbilityProjection(
        own_board=mask(own_board, own_ids),
        opponent_board=mask(opponent_board, opponent_ids),
        resolved=True,
        suppressed_own_ids=tuple(sorted(own_ids)),
        suppressed_opponent_ids=tuple(sorted(opponent_ids)),
    )
