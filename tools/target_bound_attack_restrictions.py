"""Bind Defending-Pokemon attack restrictions to physical board objects."""

from __future__ import annotations

from dataclasses import dataclass, replace

from attack_restriction_turn_windows import (
    AttackRestrictionWindow,
    begin_turn,
    end_turn,
    restriction_affects_player,
)
from board_object_kernel import BoardState
from source_scoped_action_restrictions import (
    CardActionAttempt,
    restriction_blocks_attempt,
)


@dataclass(frozen=True)
class TargetBoundAttackRestrictionWindow:
    window: AttackRestrictionWindow
    target_object_id: str
    target_card_name: str
    target_effect_live: bool = True

    def __post_init__(self) -> None:
        if not self.target_object_id or not self.target_card_name:
            raise ValueError("target identity must be non-empty")
        if self.window.restriction.required_target_relation != "defending_pokemon":
            raise ValueError("restriction is not Defending-Pokemon scoped")


def bind_defending_pokemon_window(
    window: AttackRestrictionWindow,
    target_board: BoardState,
) -> TargetBoundAttackRestrictionWindow:
    """Bind a newly materialized restriction to the current Active Pokemon."""

    target = target_board.get(target_board.active_id)
    return TargetBoundAttackRestrictionWindow(
        window=window,
        target_object_id=target.object_id,
        target_card_name=target.card_name,
    )


def begin_target_bound_turn(
    bound: TargetBoundAttackRestrictionWindow,
    player: str,
) -> TargetBoundAttackRestrictionWindow:
    return replace(bound, window=begin_turn(bound.window, player))


def end_target_bound_turn(
    bound: TargetBoundAttackRestrictionWindow,
    player: str,
) -> TargetBoundAttackRestrictionWindow:
    return replace(bound, window=end_turn(bound.window, player))


def advance_target_binding(
    bound: TargetBoundAttackRestrictionWindow,
    previous_board: BoardState,
    current_board: BoardState,
) -> TargetBoundAttackRestrictionWindow:
    """Advance target-effect identity across one physical board transition.

    Call this at every board mutation. Once the affected Pokemon leaves the
    Active Spot, leaves play, evolves, or devolves, the attack effect stays
    cleared even if that object later returns Active.
    """

    if not bound.target_effect_live:
        return bound

    try:
        previous = previous_board.get(bound.target_object_id)
    except KeyError as exc:
        raise ValueError("live target effect is missing from previous board") from exc

    if previous.card_name != bound.target_card_name:
        raise ValueError("live target binding is stale before transition")

    try:
        current = current_board.get(bound.target_object_id)
    except KeyError:
        return replace(bound, target_effect_live=False)

    moved_to_bench = (
        previous_board.active_id == bound.target_object_id
        and current_board.active_id != bound.target_object_id
    )
    identity_changed = current.card_name != bound.target_card_name
    if moved_to_bench or identity_changed:
        return replace(bound, target_effect_live=False)
    return bound


def target_bound_restriction_blocks_attempt(
    bound: TargetBoundAttackRestrictionWindow,
    *,
    player: str,
    attempt: CardActionAttempt,
    target_object_id: str,
) -> bool:
    """Evaluate one targeted action without caller-authored relation labels."""

    if not bound.target_effect_live:
        return False
    if not restriction_affects_player(bound.window, player):
        return False
    if target_object_id != bound.target_object_id:
        return False

    targeted_attempt = replace(
        attempt,
        target_relation="defending_pokemon",
    )
    return restriction_blocks_attempt(bound.window.restriction, targeted_attempt)
