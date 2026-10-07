"""Execute compiled Active/Bench movement clauses on conserved board objects."""

from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardState, switch_active
from position_effect_profile_compiler import (
    ChoiceAuthority,
    EffectTargetGeometry,
    PositionEffectKind,
    PositionEffectProfile,
)


@dataclass(frozen=True)
class PositionEffectExecution:
    actor_board: BoardState
    opponent_board: BoardState
    chooser: ChoiceAuthority
    chosen_object_id: str
    targeted_object_id: str


def effect_target_object_id(
    profile: PositionEffectProfile,
    actor_board: BoardState,
    opponent_board: BoardState,
    chosen_object_id: str,
) -> str | None:
    if profile.effect_target == EffectTargetGeometry.ACTOR_ACTIVE:
        return actor_board.active_id
    if profile.effect_target == EffectTargetGeometry.OPPONENT_ACTIVE:
        return opponent_board.active_id
    if profile.effect_target == EffectTargetGeometry.SELECTED_OPPONENT_BENCH:
        if chosen_object_id not in opponent_board.bench_ids:
            return None
        return chosen_object_id
    raise ValueError(profile.effect_target)


def execute_position_effect(
    profile: PositionEffectProfile,
    actor_board: BoardState,
    opponent_board: BoardState,
    *,
    chosen_object_id: str,
    blocked_effect_target_ids: frozenset[str] = frozenset(),
    coin_result: str | None = None,
) -> PositionEffectExecution | None:
    """Apply one compiled movement clause.

    blocked_effect_target_ids is an upstream effect-immunity overlay. The
    executor checks it against the rulebook-defined target object before moving
    either board. This is especially important for attack effects: forced
    switch-out targets the current opposing Active, while targeted gust targets
    the selected opposing Benched Pokemon.

    Attack damage, source-action legality, and play conditions remain upstream.
    Coin-gated movement is executed only after an explicit heads result.
    """

    if profile.coin_heads_required and coin_result != "heads":
        return None

    targeted_object_id = effect_target_object_id(
        profile,
        actor_board,
        opponent_board,
        chosen_object_id,
    )
    if targeted_object_id is None or targeted_object_id in blocked_effect_target_ids:
        return None

    if profile.kind == PositionEffectKind.SELF_SWITCH:
        moved = switch_active(actor_board, chosen_object_id)
        if moved is None:
            return None
        return PositionEffectExecution(
            actor_board=moved,
            opponent_board=opponent_board,
            chooser=profile.chooser,
            chosen_object_id=chosen_object_id,
            targeted_object_id=targeted_object_id,
        )

    if profile.kind in {
        PositionEffectKind.OPPONENT_FORCED_SWITCH,
        PositionEffectKind.TARGETED_GUST,
    }:
        moved = switch_active(opponent_board, chosen_object_id)
        if moved is None:
            return None
        return PositionEffectExecution(
            actor_board=actor_board,
            opponent_board=moved,
            chooser=profile.chooser,
            chosen_object_id=chosen_object_id,
            targeted_object_id=targeted_object_id,
        )

    raise ValueError(profile.kind)
